"""
FamGateway Telegram Bot Example (using pyTelegramBotAPI / telebot)

Installation:
    pip install famgateway pyTelegramBotAPI

Run:
    python telegram_telebot.py
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from famgateway import FamGateway, FamGatewayError

# Initialize Bot & FamGateway
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
FAMGATEWAY_API_KEY = "YOUR_FAMGATEWAY_API_KEY"

bot = telebot.TeleBot(BOT_TOKEN)
fg = FamGateway(api_key=FAMGATEWAY_API_KEY)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Welcome! Type /buy to purchase VIP access for INR 50."
    )


@bot.message_handler(commands=['buy'])
def create_payment(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "User"

    bot.send_message(message.chat.id, "Generating your dynamic UPI QR code...")

    try:
        # Create a dynamic INR 50 UPI payment order
        order = fg.create_order(
            amount=50.00,
            customer_name=f"{user_name} ({user_id})"
        )

        caption_text = (
            f"*Pay with any UPI App*\n\n"
            f"*Amount to Pay:* `INR {order.payable_amount}`\n"
            f"*Order ID:* `{order.order_id}`\n\n"
            f"Scan the QR code above with PhonePe, GPay, Paytm, or tap below to pay directly:"
        )

        # Create inline buttons for direct UPI and check status
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Pay via UPI App", url=order.upi_intent),
            InlineKeyboardButton("Web Checkout", url=order.checkout_url)
        )
        markup.row(
            InlineKeyboardButton("Check Payment Status", callback_data=f"check_{order.order_id}")
        )

        # Send QR image directly in Telegram chat!
        bot.send_photo(
            chat_id=message.chat.id,
            photo=order.qr_url,
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=markup
        )

    except FamGatewayError as e:
        bot.send_message(message.chat.id, f"Payment error: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_payment_callback(call):
    order_id = call.data.split("_")[1]

    try:
        status = fg.get_status(order_id)

        if status.is_paid:
            bot.answer_callback_query(call.id, "Payment Verified!", show_alert=True)
            bot.send_message(
                call.message.chat.id,
                f"*Payment Successful!*\n\n"
                f"Thank you! Your transaction (UTR: `{status.utr}`) has been verified.\n"
                f"Here is your VIP Link: https://t.me/+ExampleInviteLink",
                parse_mode="Markdown"
            )
        else:
            bot.answer_callback_query(
                call.id,
                "Payment not received yet. Please pay and click check again.",
                show_alert=True
            )

    except FamGatewayError as e:
        bot.answer_callback_query(call.id, f"Error checking: {e}", show_alert=True)


if __name__ == "__main__":
    print("Telegram bot is running...")
    bot.infinity_polling()
