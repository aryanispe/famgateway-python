"""
FamGateway Client implementation
"""
import hmac
import hashlib
import json
import requests
from typing import Optional, Union, Dict, Any

from .exceptions import (
    FamGatewayError,
    AuthenticationError,
    APIError,
    OrderNotFoundError,
    NetworkError,
)
from .models import OrderResponse, OrderStatus

DEFAULT_BASE_URL = "https://famgateway.in"
DEFAULT_TIMEOUT = 15  # seconds


class FamGateway:
    """
    FamGateway Python Client

    Usage:
        >>> from famgateway import FamGateway
        >>> fg = FamGateway(api_key="your_api_key")
        >>> order = fg.create_order(amount=100.0)
        >>> print(order.qr_url)
        >>> status = fg.get_status(order.order_id)
        >>> print(status.is_paid)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        if not api_key or not isinstance(api_key, str):
            raise AuthenticationError("A valid FamGateway api_key string is required.")

        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FamGateway-Python-SDK/1.0.4",
            "Accept": "application/json",
        })

    def _request(self, method: str, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            resp = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error connecting to FamGateway: {str(e)}") from e

        try:
            result = resp.json()
        except json.JSONDecodeError:
            raise APIError(
                f"Invalid JSON response from FamGateway API (HTTP {resp.status_code})",
                status_code=resp.status_code,
            )

        # 401 Unauthorized
        if resp.status_code == 401 or result.get("status") == "unauthorized":
            raise AuthenticationError(
                result.get("message", "Invalid or missing FamGateway API Key"),
                status_code=resp.status_code,
                response_body=result,
            )

        # 404 Not Found
        if resp.status_code == 404 or result.get("status") == "not_found":
            raise OrderNotFoundError(
                result.get("message", "Order ID or payment link not found"),
                status_code=resp.status_code,
                response_body=result,
            )

        # 408 Expired is a normal business status for timed-out orders
        if resp.status_code == 408 or result.get("status") == "expired":
            return result

        # Other HTTP 4xx/5xx or API failure status
        if resp.status_code >= 400 or result.get("status") in ("error", "failed"):
            raise APIError(
                result.get("message", result.get("error", "FamGateway API Request Failed")),
                status_code=resp.status_code,
                response_body=result,
            )

        return result

    def create_order(
        self,
        amount: Union[int, float, str],
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        redirect_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
    ) -> OrderResponse:
        """
        Create a new dynamic UPI Payment Order.

        :param amount: Payment amount in INR (e.g. 100 or 50.50)
        :param customer_name: (Optional) Customer's name or bot username
        :param customer_email: (Optional) Customer's email
        :param customer_phone: (Optional) Customer's phone number
        :param redirect_url: (Optional) Where to redirect after payment on hosted checkout
        :param webhook_url: (Optional) Specific webhook URL override for this order
        :return: OrderResponse with qr_url, upi_intent, order_id, payable_amount
        """
        try:
            amt_float = float(amount)
            if amt_float <= 0:
                raise ValueError("Amount must be greater than 0")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid amount provided: {amount}")

        params = {
            "api_key": self.api_key,
            "amount": amt_float,
        }

        if customer_name:
            params["customer_name"] = str(customer_name)
        if customer_email:
            params["customer_email"] = str(customer_email)
        if customer_phone:
            params["customer_phone"] = str(customer_phone)
        if redirect_url:
            params["redirect_url"] = str(redirect_url)
        if webhook_url:
            params["webhook_url"] = str(webhook_url)

        res = self._request("GET", "/api/qr.php", params=params)
        data = res.get("data", {})
        return OrderResponse(data)

    def get_status(self, order_id: str) -> OrderStatus:
        """
        Check the fast status of an order via public polling endpoint.

        :param order_id: The order identifier (e.g. "fg_XXXXXXXX")
        :return: OrderStatus object with .is_paid, .status, .utr, .sender_name
        """
        if not order_id:
            raise ValueError("order_id is required")

        params = {
            "order_id": order_id.strip(),
        }

        res = self._request("GET", "/api/checkout-status.php", params=params)
        return OrderStatus(res)

    def verify_order(self, order_id: str) -> OrderStatus:
        """
        Verify payment status with authenticated merchant credentials.
        Triggers instant backend IMAP synchronization for active transactions.

        :param order_id: The order identifier (e.g. "fg_XXXXXXXX" or "LINK_slug")
        :return: OrderStatus object with .is_paid, .status, .utr, .transaction_id, .sender_name
        """
        if not order_id:
            raise ValueError("order_id is required")

        params = {
            "api_key": self.api_key,
            "order_id": order_id.strip(),
        }

        res = self._request("GET", "/api/verify-order.php", params=params)
        return OrderStatus(res)

    def simulate_payment(self, order_id: str) -> dict:
        """
        Simulate a successful payment for testing / sandbox development.

        :param order_id: The order identifier to mark as paid
        :return: Response dict
        """
        if not order_id:
            raise ValueError("order_id is required")

        params = {
            "api_key": self.api_key,
            "order_id": order_id.strip(),
        }

        return self._request("GET", "/api/simulate-payment.php", params=params)

    @staticmethod
    def verify_webhook_signature(payload: Union[str, bytes], signature: str, api_key: str) -> bool:
        """
        Cryptographically verify the HMAC-SHA256 signature of an incoming FamGateway webhook.

        :param payload: Raw request body (str or bytes)
        :param signature: Value of the 'X-FamGateway-Signature' header
        :param api_key: Merchant private API key (HMAC secret)
        :return: True if the signature matches, False otherwise
        """
        if not payload or not signature or not api_key:
            return False

        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
        else:
            payload_bytes = payload

        computed = hmac.new(api_key.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, signature.strip())

    def verify_webhook(self, payload: Union[str, bytes], signature: str) -> bool:
        """
        Verify an incoming webhook payload using the initialized client's API Key.

        :param payload: Raw request body (str or bytes)
        :param signature: Value of the 'X-FamGateway-Signature' header
        :return: True if valid, False otherwise
        """
        return FamGateway.verify_webhook_signature(payload, signature, self.api_key)
