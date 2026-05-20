import os
import random
import time
import threading
from datetime import datetime, timedelta, timezone

import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BOT_NAME = "S_R X VENOM_AI"
ADMIN_USERNAME = "srtraderowner_098"

CHANNEL_ID = -1002734046747
CHANNEL_LINK = "https://t.me/+jlIIxaT6OB0wNDk1"

BD_TZ = timezone(timedelta(hours=6))
MAX_SIGNAL = 5

users = {}
last_signal = {}

PAIRS = [
    "USD/BDT (OTC)",
    "USD/INR (OTC)",
    "USD/IDR (OTC)",
    "USD/BRL (OTC)",
    "EUR/USD (OTC)",
    "GBP/USD (OTC)",
    "USD/DZD (OTC)",
]  "USD/MXN (OTC)",

def now_bd():
    return datetime.now(BD_TZ)

def user_data(uid):
    today = now_bd().strftime("%Y-%m-%d")
    if uid not in users or users[uid]["date"] != today:
        users[uid] = {"date": today, "left": MAX_SIGNAL}
    return users[uid]

def is_joined(uid):
    try:
        m = bot.get_chat_member(CHANNEL_ID, uid)
        return m.status not in ["left", "kicked"]
    except:
        return False

def join_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📢 JOIN CHANNEL", url=CHANNEL_LINK),
        types.InlineKeyboardButton("✅ I HAVE JOINED", callback_data="check_join"),
    )
    return kb

def menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📊 LIVE SIGNAL", callback_data="live"),
        types.InlineKeyboardButton("🌈 RESULT CHECKER", callback_data="result"),
        types.InlineKeyboardButton("👨‍💻 CONTACT ADMIN", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    return kb

def send_home(chat_id, uid, name="Trader"):
    data = user_data(uid)
    bot.send_message(chat_id, f"""
━━━━━━━━━━━━━━━━━━━━
🔥 {BOT_NAME}
━━━━━━━━━━━━━━━━━━━━

✨ Welcome, {name}

📊 Market: OTC
🕐 Timezone: UTC+6 Bangladesh
⌛ Expiry: M1
🔁 MTG: 1 Step

📌 Signals left today: {data["left"]}

Choose option below 👇
""", reply_markup=menu())

def create_signal():
    now = now_bd()
    entry = now + timedelta(minutes=random.choice([2, 3]))
    result_time = entry + timedelta(seconds=75)

    return {
        "pair": random.choice(PAIRS),
        "direction": random.choice(["CALL 🟢", "PUT 🔴"]),
        "signal_time": now.strftime("%H:%M:%S"),
        "entry_time": entry.strftime("%H:%M"),
        "result_time": result_time,
        "result": random.choice(["WIN", "WIN", "WIN", "MTG WIN", "LOSS"])
    }

def signal_text(sig):
    direction = sig["direction"].replace(" 🟢", "").replace(" 🔴", "")

    return f"""
☲☲☲☲ 【𝚂_𝚁 𝚇 𝚅𝙴𝙽𝙾𝙼_𝙰𝙸】☲☲☲☲
╭━━━━━━【⛨】━━━━━━╮
💎 𝙰𝙲𝚃𝙸𝚅𝙴 𝙿𝙰𝙸𝚁 »» {sig["pair"]}
⏰ 𝚃𝙸𝙼𝙴𝚃𝙰𝙱𝙻𝙴 »» {sig["entry_time"]}
⏳ 𝙴𝚇𝙿𝙸𝚁𝙰𝚃𝙸𝙾𝙽 »» M1
🟢 𝙳𝙸𝚁𝙴𝙲𝚃𝙸𝙾𝙽 »» {direction}
✨ 𝙲𝙾𝙽𝙵𝙸𝙳𝙴𝙽𝙲𝙴 »» {random.randint(92, 97)}%
╰━━━━━━【⛨】━━━━━━╯
‼️ 𝙼𝚃𝙶 1 𝚂𝚃𝙴𝙿 𝙸𝙵 𝙻𝙾𝚂𝚂 ‼️
💬𝙲𝚘𝚗𝚝𝚊𝚌𝚝: @{ADMIN_USERNAME}
"""

def result_text(sig):
    if sig["result"] == "WIN":
        r = "🟩🟩 SURESHOT WIN ✅ 🟩🟩"
    elif sig["result"] == "MTG WIN":
        r = "🟨🟨 MTG 1 STEP WIN ✅ 🟨🟨"
    else:
        r = "🟥🟥 LOSS ❌ 🟥🟥"

    return f"""
========== RESULT ==========

📊 {sig["pair"]}
🕯 Entry: {sig["entry_time"]} CANDLE

{r}

👨‍💻 Contact: @{ADMIN_USERNAME}
"""

@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.from_user.id

    if not is_joined(uid):
        bot.send_message(
            msg.chat.id,
            "🔐 Access Locked\n\nআগে private channel এ join করো। তারপর ✅ I HAVE JOINED চাপো।",
            reply_markup=join_keyboard()
        )
        return

    send_home(msg.chat.id, uid, msg.from_user.first_name or "Trader")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id

    if call.data == "check_join":
        if is_joined(uid):
            bot.send_message(call.message.chat.id, "✅ Access Approved!")
            send_home(call.message.chat.id, uid, call.from_user.first_name or "Trader")
        else:
            bot.send_message(
                call.message.chat.id,
                "❌ Join detect হয়নি। Bot কে channel admin করা আছে কিনা check করো।",
                reply_markup=join_keyboard()
            )
        return

    if not is_joined(uid):
        bot.send_message(
            call.message.chat.id,
            "🔐 আগে channel join করো।",
            reply_markup=join_keyboard()
        )
        return

    data = user_data(uid)

    if call.data == "live":
        if data["left"] <= 0:
            bot.send_message(call.message.chat.id, "❌ Daily signal limit finished.")
            return

        data["left"] -= 1
        sig = create_signal()
        last_signal[uid] = sig

        bot.send_message(call.message.chat.id, signal_text(sig))
        bot.send_message(call.message.chat.id, f"📌 Remaining Signals: {data['left']}")

        def wait_and_result():
            wait = int((sig["result_time"] - now_bd()).total_seconds())
            if wait < 5:
                wait = 5
            time.sleep(wait)
            bot.send_message(call.message.chat.id, result_text(sig), reply_markup=menu())

        threading.Thread(target=wait_and_result, daemon=True).start()

    elif call.data == "result":
        sig = last_signal.get(uid)
        if not sig:
            bot.send_message(call.message.chat.id, "❌ আগে LIVE SIGNAL নাও।")
        else:
            bot.send_message(call.message.chat.id, result_text(sig), reply_markup=menu())

print("V1 stable bot running...")
bot.infinity_polling(skip_pending=True)
