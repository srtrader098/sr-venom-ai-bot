import os
import random
import threading
import time
from datetime import datetime, timedelta, timezone, date

import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BOT_NAME = "🌪 S_R X VENOM_AI"
ADMIN_USERNAME = "srtraderowner_098"

MAX_SIGNALS_PER_DAY = 5
BD_TZ = timezone(timedelta(hours=6))

PAIRS = [
    "USDIDR-OTC", "USDBDT-OTC", "USDINR-OTC", "USDBRL-OTC",
    "USDMXN-OTC", "USDNGN-OTC", "EURUSD-OTC", "GBPUSD-OTC",
    "EURJPY-REAL", "AUDJPY-REAL", "EURUSD-REAL"
]

users = {}
last_signals = {}

def bd_now():
    return datetime.now(BD_TZ)

def get_user(uid):
    today = str(date.today())
    if uid not in users or users[uid]["date"] != today:
        users[uid] = {"date": today, "left": MAX_SIGNALS_PER_DAY, "auto": False}
    return users[uid]

def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📊 LIVE SIGNAL", callback_data="live"),
        types.InlineKeyboardButton("🔥 AUTO SIGNAL", callback_data="auto"),
        types.InlineKeyboardButton("🌈 RESULT CHECKER", callback_data="result"),
        types.InlineKeyboardButton("👥 CONTACT", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    return kb

def back_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ BACK MENU", callback_data="back"))
    return kb

def create_signal():
    pair = random.choice(PAIRS)
    direction = random.choice(["CALL", "PUT"])
    confidence = random.randint(90, 97)
    entry_candle = random.choice(["1st candle", "2nd candle", "3rd candle"])
    signal_time = (bd_now() + timedelta(minutes=1)).strftime("%H:%M")

    return {
        "pair": pair,
        "direction": direction,
        "confidence": confidence,
        "entry": entry_candle,
        "time": signal_time,
        "expiry": "M1",
        "result": random.choice(["WIN", "WIN", "WIN", "MTG WIN", "LOSS"])
    }

def signal_message(sig):
    return f"""
═════【 {BOT_NAME} 】═════

╭─────【 🛡 】─────╮
💎 ACTIVE PAIR »» {sig['pair']}
⏰ TIMETABLE »» {sig['time']} UTC+6
⌛ EXPIRATION »» {sig['expiry']}
🔴 DIRECTION »» {sig['direction']}
🕯 ENTRY »» {sig['entry']}
✨ CONFIDENCE »» {sig['confidence']}%
╰─────【 🛡 】─────╯

‼️ MTG 1 STEP IF LOSS ‼️

💬 Contact: @{ADMIN_USERNAME}
"""

def result_message(sig):
    if sig["result"] == "WIN":
        status = "🟩🟩 SURESHOT WIN 🟩🟩"
    elif sig["result"] == "MTG WIN":
        status = "🟨🟨 MTG 1 STEP WIN 🟨🟨"
    else:
        status = "🟥🟥 LOSS / AVOID NEXT 🟥🟥"

    return f"""
✥═════ R | E | S | U | L | T ═════✥

📊 {sig['pair']}  |  🕘 {sig['time']}
{status}

💬 Contact: @{ADMIN_USERNAME}
"""

@bot.message_handler(commands=["start"])
def start(message):
    data = get_user(message.from_user.id)
    name = message.from_user.first_name or "Trader"

    text = f"""
━━━━━━━━━━━━━━━━━━━━
| {BOT_NAME} |
━━━━━━━━━━━━━━━━━━━━

✨ Welcome, {name}!

🤖 AI-powered Binary Signal Bot
📊 OTC + REAL Market
🕐 Timezone: UTC+6 Bangladesh
⌛ Signal Type: M1

📌 Signals remaining today: {data["left"]}

⬇️ Select option below:
"""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id
    data = get_user(uid)

    if call.data == "live":
        if data["left"] <= 0:
            bot.send_message(call.message.chat.id, "❌ Daily signal limit finished. Try tomorrow.", reply_markup=back_menu())
            return

        data["left"] -= 1
        sig = create_signal()
        last_signals[uid] = sig

        bot.send_message(call.message.chat.id, signal_message(sig))
        bot.send_message(call.message.chat.id, f"📌 Remaining signals today: {data['left']}")

        def send_result():
            time.sleep(75)
            bot.send_message(call.message.chat.id, result_message(sig), reply_markup=main_menu())

        threading.Thread(target=send_result, daemon=True).start()

    elif call.data == "auto":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("▶️ START AUTO", callback_data="start_auto"),
            types.InlineKeyboardButton("🛑 STOP AUTO", callback_data="stop_auto"),
            types.InlineKeyboardButton("⬅️ BACK MENU", callback_data="back")
        )
        bot.send_message(call.message.chat.id, "🔥 AUTO SIGNAL MODE\n\nEvery signal is M1 UTC+6.", reply_markup=kb)

    elif call.data == "start_auto":
        if data["auto"]:
            bot.send_message(call.message.chat.id, "⚠️ Auto signal already running.")
            return

        data["auto"] = True
        bot.send_message(call.message.chat.id, "✅ Auto signal started.")

        def auto_run(chat_id, user_id):
            while get_user(user_id)["auto"]:
                d = get_user(user_id)

                if d["left"] <= 0:
                    d["auto"] = False
                    bot.send_message(chat_id, "❌ Daily limit finished. Auto stopped.")
                    break

                d["left"] -= 1
                sig = create_signal()
                last_signals[user_id] = sig

                bot.send_message(chat_id, signal_message(sig))
                time.sleep(75)
                bot.send_message(chat_id, result_message(sig))
                time.sleep(45)

        threading.Thread(target=auto_run, args=(call.message.chat.id, uid), daemon=True).start()

    elif call.data == "stop_auto":
        data["auto"] = False
        bot.send_message(call.message.chat.id, "🛑 Auto signal stopped.", reply_markup=back_menu())

    elif call.data == "result":
        sig = last_signals.get(uid)
        if not sig:
            bot.send_message(call.message.chat.id, "❌ No signal found yet. Generate a LIVE SIGNAL first.", reply_markup=back_menu())
        else:
            bot.send_message(call.message.chat.id, result_message(sig), reply_markup=main_menu())

    elif call.data == "back":
        start(call.message)

print("S_R X VENOM_AI running...")
bot.infinity_polling()
