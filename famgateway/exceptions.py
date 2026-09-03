"""
Custom Exceptions for FamGateway SDK
"""

class FamGatewayError(Exception):
    """Base exception for all FamGateway SDK errors."""
    def __init__(self, message: str, status_code: int = None, response_body: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body or {}

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(FamGatewayError):
    """Raised when the API Key is missing or invalid."""
    pass


class APIError(FamGatewayError):
    """Raised when the FamGateway API returns a failure status."""
    pass


class OrderNotFoundError(FamGatewayError):
    """Raised when the requested Order ID does not exist."""
    pass


class NetworkError(FamGatewayError):
    """Raised when connection to FamGateway fails (timeout, DNS, SSL)."""
    pass
