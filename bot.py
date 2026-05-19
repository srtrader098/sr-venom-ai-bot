import telebot
from telebot import types
import random

BOT_TOKEN = "8853971922:AAFvmtAZqQurskA2kuLal_ntB-mUFmWkJgM"

bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_USERNAME = "srtraderowner_098"

pairs = [
    "EUR/USD OTC",
    "USD/JPY OTC",
    "GBP/USD OTC",
    "USD/BDT OTC",
    "EUR/JPY REAL",
    "AUD/JPY REAL"
]

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton("📊 LIVE SIGNAL", callback_data="live"),
        types.InlineKeyboardButton("🔥 AUTO SIGNAL", callback_data="auto"),
        types.InlineKeyboardButton("🌈 RESULT CHECKER", callback_data="result"),
        types.InlineKeyboardButton("⚙️ TOOLS", callback_data="tools"),
        types.InlineKeyboardButton(
            "👨‍💻 CONTACT ADMIN",
            url=f"https://t.me/{ADMIN_USERNAME}"
        )
    )

    return markup

@bot.message_handler(commands=["start"])
def start(message):

    name = message.from_user.first_name or "Trader"

    text = f"""
🌪 𝗦_𝗥 𝗫 𝗩𝗘𝗡𝗢𝗠_𝗔𝗜

✨ Welcome, {name}!

🤖 Premium AI Trading Signal Bot
📊 OTC + REAL Market
⚡ Fast Signal System

⬇️ Choose an option below:
"""

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "live":

        pair = random.choice(pairs)

        direction = random.choice([
            "BUY ⬆️",
            "SELL ⬇️"
        ])

        duration = random.choice([
            "1 MIN",
            "3 MIN",
            "5 MIN"
        ])

        confidence = random.randint(85, 97)

        text = f"""
📊 LIVE SIGNAL GENERATED

💹 Pair: {pair}

⏰ Time: {duration}

📈 Direction: {direction}

🎯 Confidence: {confidence}%

⚠️ Trade with proper risk management.
"""

        bot.send_message(call.message.chat.id, text)

    elif call.data == "auto":

        bot.send_message(
            call.message.chat.id,
            "🔥 AUTO SIGNAL SYSTEM COMING SOON!"
        )

    elif call.data == "result":

        bot.send_message(
            call.message.chat.id,
            "🌈 RESULT CHECKER\n\nSend your result screenshot to admin."
        )

    elif call.data == "tools":

        bot.send_message(
            call.message.chat.id,
            """
⚙️ TOOLS SECTION

🕐 Best Trading Time:
7PM - 11PM (BD Time)

📊 Market:
OTC + REAL

🚀 Strategy:
Trend + Momentum
"""
        )

print("Bot started successfully...")

bot.infinity_polling()
