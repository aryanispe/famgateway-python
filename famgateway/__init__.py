"""
FamGateway Python SDK
Official client library for FamGateway P2P UPI Payment Gateway.
Developed by ARYANISPE (Govt. MSME Reg: UDYAM-BR-28-0050000)
"""

from .client import FamGateway
from .exceptions import (
    FamGatewayError,
    AuthenticationError,
    APIError,
    OrderNotFoundError,
    NetworkError,
)
from .models import OrderResponse, OrderStatus

__version__ = "1.0.3"
__author__ = "ARYANISPE"
__all__ = [
    "FamGateway",
    "FamGatewayError",
    "AuthenticationError",
    "APIError",
    "OrderNotFoundError",
    "NetworkError",
    "OrderResponse",
    "OrderStatus",
]
