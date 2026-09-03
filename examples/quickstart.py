"""
FamGateway Quickstart Example (5 Lines of Code)
"""

from famgateway import FamGateway

# 1. Initialize client
fg = FamGateway(api_key="YOUR_FAMGATEWAY_API_KEY")

# 2. Create an order (Only amount is required!)
order = fg.create_order(amount=100.0)

# Optional: pass customer details if needed:
# order = fg.create_order(amount=100.0, customer_name="Aryan", customer_phone="9876543210")

print(f"Order Created: {order.order_id}")
print(f"Payable Amount: ₹{order.payable_amount}")
print(f"Direct QR Image: {order.qr_url}")
print(f"UPI Intent Link: {order.upi_intent}")
print(f"Hosted Checkout URL: {order.checkout_url}")

# 3. Check status
status = fg.get_status(order.order_id)
print(f"Payment Status: {status.status} (Paid: {status.is_paid})")
