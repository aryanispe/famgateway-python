"""
FamGateway Webhook Handler Example (Flask)

Installation:
    pip install famgateway flask

Run:
    python flask_webhook.py
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook/famgateway", methods=["POST"])
def handle_webhook():
    data = request.json or {}
    
    event = data.get("event")
    order_id = data.get("order_id")
    amount = data.get("amount")
    utr = data.get("utr")
    sender_name = data.get("sender_name")
    
    print(f"🔔 Received Webhook: Event={event}, OrderID={order_id}, Amount=₹{amount}, UTR={utr}")

    if event == "payment.success":
        # 1. Update order in your database
        # 2. Deliver digital goods / grant access / send email
        print(f"✅ Payment captured from {sender_name} for order {order_id}!")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
