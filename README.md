# FamGateway Python SDK

[![PyPI version](https://img.shields.io/pypi/v/famgateway.svg?color=blue)](https://pypi.org/project/famgateway/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/famgateway?color=blue)](https://pypi.org/project/famgateway/)
[![Python versions](https://img.shields.io/pypi/pyversions/famgateway.svg)](https://pypi.org/project/famgateway/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Govt MSME Registered](https://img.shields.io/badge/MSME-UDYAM--BR--28--0050000-blue)](https://famgateway.in)
[![GitHub Stars](https://img.shields.io/github/stars/aryanispe/famgateway-python?style=social)](https://github.com/aryanispe/famgateway-python)

The official Python client library for **[FamGateway](https://famgateway.in)** — 100% Free, Zero-Fee Peer-to-Peer UPI Payment Gateway for Indian Developers and Businesses.

- 📦 **PyPI Official Package:** [https://pypi.org/project/famgateway/](https://pypi.org/project/famgateway/)
- 🌐 **Official Website:** [https://famgateway.in](https://famgateway.in)
- 📖 **API Documentation:** [https://famgateway.in/docs.php](https://famgateway.in/docs.php)
- 🏛️ **Govt. MSME Registration:** `UDYAM-BR-28-0050000` (ARYANISPE)

---

## Features

- **Instant Dynamic UPI QR Codes** — Get direct QR image URLs (`qr_url`) to send directly in Telegram Bots or apps.
- **Deep UPI Intent Links** — `upi://pay?...` URLs for 1-tap payments in PhonePe, Google Pay, and Paytm.
- **Telegram Bot Friendly** — Send QR codes directly to users inside Telegram chats without external browser redirects.
- **Zero Transaction Fees** — 100% peer-to-peer settlement directly into your FamPay / UPI ID.
- **Instant Webhooks & Polling** — Automated payment reconciliation via webhooks and status API.

---

## Installation

Install the official package from [PyPI](https://pypi.org/project/famgateway/):

```bash
pip install famgateway
```

Or upgrade to the latest release:

```bash
pip install --upgrade famgateway
```

---

## Quickstart (3 Lines of Code)

```python
from famgateway import FamGateway

# 1. Initialize client with your API Key
fg = FamGateway(api_key="your_famgateway_api_key")

# 2. Create a dynamic UPI payment order (Only amount is required!)
order = fg.create_order(amount=100.0)

# Optional: You can also pass customer metadata for your own records:
# order = fg.create_order(amount=100.0, customer_name="Aryan Gupta", customer_phone="9876543210")

print("Order ID:", order.order_id)
print("Payable Amount: Rs.", order.payable_amount)
print("QR Code Image URL:", order.qr_url)
print("Deep UPI Intent:", order.upi_intent)
print("Hosted Checkout URL:", order.checkout_url)

# 3. Check order payment status
status = fg.get_status(order.order_id)
if status.is_paid:
    print(f"Payment Captured! UTR: {status.utr}")
```

---

## Telegram Bot Integration Example

Use `famgateway` to collect payments directly inside Telegram without any website redirect:

```python
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from famgateway import FamGateway

bot = telebot.TeleBot("YOUR_TELEGRAM_BOT_TOKEN")
fg = FamGateway(api_key="YOUR_FAMGATEWAY_API_KEY")

@bot.message_handler(commands=['buy'])
def handle_buy(message):
    # 1. Create UPI payment order for Rs 50
    order = fg.create_order(
        amount=50.0,
        customer_name=f"{message.from_user.first_name} ({message.from_user.id})"
    )

    # 2. Create inline pay button
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Pay via UPI App", url=order.upi_intent),
        InlineKeyboardButton("Web Checkout", url=order.checkout_url)
    )
    markup.row(
        InlineKeyboardButton("Check Status", callback_data=f"check_{order.order_id}")
    )

    # 3. Send QR image directly in chat
    bot.send_photo(
        chat_id=message.chat.id,
        photo=order.qr_url,
        caption=f"Scan to Pay Rs {order.payable_amount}\n\nOrder ID: `{order.order_id}`",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def handle_status(call):
    order_id = call.data.split("_")[1]
    status = fg.get_status(order_id)

    if status.is_paid:
        bot.answer_callback_query(call.id, "Payment Verified!", show_alert=True)
        bot.send_message(call.message.chat.id, f"Payment received! Payer: {status.sender_name}, UTR: `{status.utr}`")
    else:
        bot.answer_callback_query(call.id, "Payment pending. Please complete the UPI payment.", show_alert=True)

bot.infinity_polling()
```

---

## API Reference

### `FamGateway(api_key, base_url="https://famgateway.in", timeout=15)`
Initializes the FamGateway client.

### `fg.create_order(amount, customer_name=None, customer_email=None, customer_phone=None, redirect_url=None, webhook_url=None)`
Creates a new payment order and generates dynamic UPI QR details.

**Returns `OrderResponse` object:**
- `order.order_id` *(str)*: Unique order reference (e.g. `fg_J2KVI0O8`)
- `order.amount` *(float)*: Base order amount
- `order.payable_amount` *(float)*: Reconciled payable amount
- `order.qr_url` *(str)*: Direct URL of the QR code image
- `order.upi_intent` *(str)*: Deep link (`upi://pay?...`) for opening UPI apps
- `order.checkout_url` *(str)*: Hosted web checkout URL
- `order.upi_id` *(str)*: Receiver UPI ID
- `order.created_at_ist` *(str)*: Order generation timestamp (IST)
- `order.expires_at_ist` *(str)*: Order expiry timestamp (IST)

### `fg.get_status(order_id)`
Fast public polling check for an order.

### `fg.verify_order(order_id)`
Full server-side payment verification with authenticated merchant credentials and instant IMAP sync.

**Returns `OrderStatus` object:**
- `status.status` *(str)*: `'success'`, `'pending'`, or `'expired'`
- `status.is_paid` *(bool)*: `True` if payment captured successfully
- `status.is_pending` *(bool)*: `True` if awaiting customer payment
- `status.is_expired` *(bool)*: `True` if order timed out after 5 minutes
- `status.utr` *(str|None)*: Bank 12-digit UTR / RRN reference
- `status.transaction_id` *(str|None)*: FamPay transaction reference ID
- `status.sender_name` *(str|None)*: Name of payer extracted from UPI
- `status.payment_time` *(str|None)*: Payment confirmation timestamp

### `fg.verify_webhook(payload, signature)`
Verifies the cryptographic HMAC-SHA256 signature (`X-FamGateway-Signature`) of incoming webhooks.

### `fg.simulate_payment(order_id)`
Simulates a successful payment for sandbox / local development without real funds.

---

## About & Legal

FamGateway is a developer-focused payment orchestration platform operated by **ARYANISPE**.
- **Govt. MSME Registration:** `UDYAM-BR-28-0050000` (Ministry of MSME, Govt. of India)
- **Website:** [https://famgateway.in](https://famgateway.in)
- **Support:** [support@famgateway.in](mailto:support@famgateway.in)

## License
MIT License. Free for commercial and private use.
