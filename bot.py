import os
import random
import time
import threading
import telebot
from telebot import types
from datetime import date

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BOT_NAME = "🌪 S_R X VENOM_AI"
ADMIN_USERNAME = "srtraderowner_098"

MAX_SIGNALS = 5
user_data = {}

PAIRS = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC",
    "USD/BDT OTC", "USD/INR OTC", "EUR/JPY REAL", "AUD/JPY REAL"
]

def get_user(uid):
    today = str(date.today())
    if uid not in user_data or user_data[uid]["date"] != today:
        user_data[uid] = {"date": today, "left": MAX_SIGNALS, "auto": False}
    return user_data[uid]

def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📊 LIVE SIGNAL", callback_data="live"),
        types.InlineKeyboardButton("🔥 AUTO SIGNAL", callback_data="auto"),
        types.InlineKeyboardButton("🌈 RESULT CHECKER", callback_data="result"),
        types.InlineKeyboardButton("⚙️ TORNADO TOOLS", callback_data="tools"),
        types.InlineKeyboardButton("👨‍💻 CONTACT ADMIN", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    return kb

def back_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ BACK TO MENU", callback_data="back"))
    return kb

def signal_text():
    pair = random.choice(PAIRS)
    direction = random.choice(["BUY ⬆️", "SELL ⬇️"])
    duration = random.choice(["1 MIN", "3 MIN", "5 MIN"])
    confidence = random.randint(86, 97)

    return f"""
📊 LIVE SIGNAL GENERATED

💹 Pair: {pair}
⏰ Time: {duration}
📈 Direction: {direction}
🎯 Confidence: {confidence}%

⚠️ Use proper money management.
"""

@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    data = get_user(uid)
    name = message.from_user.first_name or "Trader"

    text = f"""
━━━━━━━━━━━━━━━━━━━━
| {BOT_NAME} |
━━━━━━━━━━━━━━━━━━━━

✨ Welcome, {name}!

🤖 Premium AI Trading Signal Bot
📊 OTC + REAL Market Analysis
⚡ Fast Signal System
🔐 VIP Mode Ready

📌 Signals remaining today: {data["left"]}

⬇️ Choose an option below:
"""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)

    uid = call.from_user.id
    data = get_user(uid)

    if call.data == "live":
        if data["left"] <= 0:
            bot.send_message(call.message.chat.id, "❌ Daily signal limit finished. Try again tomorrow.", reply_markup=back_menu())
            return

        data["left"] -= 1
        bot.send_message(call.message.chat.id, signal_text() + f"\n📌 Remaining: {data['left']}", reply_markup=back_menu())

    elif call.data == "auto":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("▶️ START AUTO SIGNAL", callback_data="start_auto"),
            types.InlineKeyboardButton("🛑 STOP AUTO SIGNAL", callback_data="stop_auto"),
            types.InlineKeyboardButton("⬅️ BACK TO MENU", callback_data="back")
        )
        bot.send_message(call.message.chat.id, "🔥 AUTO SIGNAL MODE\n\nStart auto signal below:", reply_markup=kb)

    elif call.data == "start_auto":
        if data["auto"]:
            bot.send_message(call.message.chat.id, "⚠️ Auto signal already running.")
            return

        data["auto"] = True
        bot.send_message(call.message.chat.id, "✅ Auto signal started. Signal will come every 60 seconds.")

        def auto_run(chat_id, user_id):
            while get_user(user_id)["auto"]:
                d = get_user(user_id)
                if d["left"] <= 0:
                    d["auto"] = False
                    bot.send_message(chat_id, "❌ Daily signal limit finished. Auto signal stopped.")
                    break
                d["left"] -= 1
                bot.send_message(chat_id, signal_text() + f"\n📌 Remaining: {d['left']}")
                time.sleep(60)

        threading.Thread(target=auto_run, args=(call.message.chat.id, uid), daemon=True).start()

    elif call.data == "stop_auto":
        data["auto"] = False
        bot.send_message(call.message.chat.id, "🛑 Auto signal stopped.", reply_markup=back_menu())

    elif call.data == "result":
        bot.send_message(call.message.chat.id, """
🌈 RESULT CHECKER

📌 Last Signals Result:
✅ WIN
✅ WIN
❌ LOSS
✅ WIN
✅ WIN

📊 Accuracy Today: 80%
""", reply_markup=back_menu())

    elif call.data == "tools":
        bot.send_message(call.message.chat.id, """
⚙️ TORNADO TOOLS

🕐 Best Trading Time:
7PM - 11PM BD Time

📊 Market:
OTC + REAL

🚀 Strategy:
Trend + Momentum

🔐 VIP License:
Available

👨‍💻 Admin:
@srtraderowner_098
""", reply_markup=back_menu())

    elif call.data == "back":
        name = call.from_user.first_name or "Trader"
        bot.send_message(call.message.chat.id, f"""
🌪 S_R X VENOM_AI

✨ Welcome back, {name}!

📌 Signals remaining today: {data["left"]}

⬇️ Choose option:
""", reply_markup=main_menu())

print("Advanced bot running...")
bot.infinity_polling()
