"""
Data models for FamGateway API responses
"""
from typing import Optional, Dict, Any

class BaseResponse:
    """Wrapper that allows both attribute access (obj.foo) and dict access (obj['foo'])."""
    def __init__(self, raw: Dict[str, Any]):
        self._raw = raw

    def __getitem__(self, item):
        return self._raw[item]

    def __contains__(self, item):
        return item in self._raw

    def get(self, key, default=None):
        return self._raw.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return self._raw

    def __repr__(self):
        return f"{self.__class__.__name__}({self._raw})"


class OrderResponse(BaseResponse):
    """
    Response returned when an order is created.
    """
    @property
    def order_id(self) -> str:
        return self._raw.get("order_id", "")

    @property
    def qr_url(self) -> str:
        """Direct URL of the generated QR code image (ideal for Telegram bots)."""
        return self._raw.get("qr_url", "")

    @property
    def checkout_url(self) -> str:
        """Hosted web checkout URL (ideal for web redirects)."""
        return self._raw.get("checkout_url", "")

    @property
    def upi_id(self) -> str:
        """The receiver FamPay / UPI ID."""
        return self._raw.get("upi_id", "")

    @property
    def amount(self) -> float:
        """Original requested amount."""
        return float(self._raw.get("amount", 0.0))

    @property
    def payable_amount(self) -> float:
        """Exact payable amount in INR."""
        return float(self._raw.get("payable_amount", 0.0))

    @property
    def upi_intent(self) -> str:
        """Deep link (upi://pay?...) for opening UPI apps directly on mobile."""
        return self._raw.get("upi_intent", "")

    @property
    def created_at_ist(self) -> str:
        return self._raw.get("created_at_ist", "")

    @property
    def expires_at_ist(self) -> str:
        return self._raw.get("expires_at_ist", "")


class OrderStatus(BaseResponse):
    """
    Response returned when checking or verifying the status of an order.
    """
    def __init__(self, raw: Dict[str, Any]):
        flattened = dict(raw)
        if isinstance(raw.get("data"), dict):
            flattened.update(raw["data"])
        super().__init__(flattened)

    @property
    def order_id(self) -> str:
        return self._raw.get("order_id", "")

    @property
    def status(self) -> str:
        """Current status: 'success', 'pending', 'expired', or 'failed'."""
        return str(self._raw.get("status", "pending")).lower()

    @property
    def is_paid(self) -> bool:
        """Returns True if the payment has been successfully captured."""
        return self.status in ("success", "paid", "captured")

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def is_expired(self) -> bool:
        return self.status == "expired"

    @property
    def amount(self) -> float:
        return float(self._raw.get("amount", 0.0))

    @property
    def payable_amount(self) -> float:
        return float(self._raw.get("payable_amount", self._raw.get("amount", 0.0)))

    @property
    def utr(self) -> Optional[str]:
        """Bank RRN / UTR number if payment is captured."""
        return self._raw.get("utr")

    @property
    def transaction_id(self) -> Optional[str]:
        """FamPay Transaction Reference ID."""
        return self._raw.get("transaction_id")

    @property
    def sender_name(self) -> Optional[str]:
        """Name of the customer extracted from the UPI payment notification."""
        return self._raw.get("sender_name") or self._raw.get("customer_name")

    @property
    def payment_time(self) -> Optional[str]:
        """Timestamp when payment was completed."""
        return self._raw.get("payment_time_ist") or self._raw.get("payment_time")

    @property
    def payment_time_ist(self) -> Optional[str]:
        """Timestamp in IST when payment was completed."""
        return self._raw.get("payment_time_ist") or self._raw.get("payment_time")
