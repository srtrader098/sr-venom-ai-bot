import os
import random
import time
from datetime import datetime, timedelta, timezone

import telebot
from telebot import types

# =========================
# BASIC SETTINGS
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")

bot = telebot.TeleBot(BOT_TOKEN)

BOT_NAME = "S_R X VENOM_AI"
ADMIN_USERNAME = "srtraderowner_098"  # @ ছাড়া username
CHANNEL_ID = -1002734046747
CHANNEL_LINK = "https://t.me/+jlIIxaT6OB0wNDk1"

BD_TZ = timezone(timedelta(hours=6))

PAIRS = [
    "USDMXN-OTC",
    "USDIDR-OTC",
    "USDBDT-OTC",
    "USDINR-OTC",
    "EURUSD-OTC",
    "GBPUSD-OTC",
]

pending_signals = {}


# =========================
# HELPERS
# =========================
def now_bd():
    return datetime.now(BD_TZ)


def clean_username(username):
    return (username or "").replace("@", "").lower()


def is_admin(user):
    return clean_username(user.username) == clean_username(ADMIN_USERNAME)


def is_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ["left", "kicked"]
    except Exception:
        # Bot channel admin না হলে এখানে fail করতে পারে
        return False


# =========================
# BUTTONS
# =========================
def join_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📢 JOIN CHANNEL", url=CHANNEL_LINK))
    kb.add(types.InlineKeyboardButton("✅ I JOINED", callback_data="check_join"))
    return kb


def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📊 LIVE SIGNAL", callback_data="live_signal"),
        types.InlineKeyboardButton("🌈 RESULT CHECKER", callback_data="result_checker"),
    )
    kb.add(types.InlineKeyboardButton("👨‍💻 CONTACT ADMIN", url=f"https://t.me/{ADMIN_USERNAME}"))
    return kb


def admin_result_markup(signal_id):
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("✅ WIN", callback_data=f"result:win:{signal_id}"),
        types.InlineKeyboardButton("🟨 MTG", callback_data=f"result:mtg:{signal_id}"),
        types.InlineKeyboardButton("❌ LOSS", callback_data=f"result:loss:{signal_id}"),
    )
    return kb


# =========================
# TEXT UI
# =========================
def start_text(message):
    name = message.from_user.first_name or "MD"
    return f"""
━━━━━━━━━━━━━━━━━━━━
| 🌪 {BOT_NAME} |
━━━━━━━━━━━━━━━━━━━━

✨ Welcome, {name}!

📊 OTC + REAL Market
🕐 Timezone: UTC+6 Bangladesh
⌛ Signal Type: M1
🛡 MTG: 1 Step

⬇️ Select option below:
"""


def make_signal():
    entry = now_bd() + timedelta(minutes=2)
    signal_id = str(int(time.time()))

    return {
        "id": signal_id,
        "pair": random.choice(PAIRS),
        "direction": random.choice(["CALL", "PUT"]),
        "entry_time": entry,
        "entry_text": entry.strftime("%H:%M"),
        "confidence": random.randint(92, 98),
    }


def signal_text(sig):
    direction_emoji = "🟢" if sig["direction"] == "CALL" else "🔴"
    return f"""
══════ 【{BOT_NAME}】 ══════

╭━━━━━━【⛨】━━━━━━╮
💎 ACTIVE PAIR »» {sig['pair']}
⏰ TIMETABLE »» {sig['entry_text']}
⏳ EXPIRATION »» M1
{direction_emoji} DIRECTION »» {sig['direction']}
✨ CONFIDENCE »» {sig['confidence']}%
╰━━━━━━【⛨】━━━━━━╯

‼️ MTG 1 STEP IF LOSS ‼️

💬 Contact: @{ADMIN_USERNAME}
"""


def result_text(sig, result):
    if result == "win":
        status = "🟩🟩🟩 SURESHOT WIN 🟩🟩🟩"
    elif result == "mtg":
        status = "🟨🟨🟨 SURESHOT MTG 🟨🟨🟨"
    else:
        status = "🟥🟥🟥 SIGNAL LOSS 🟥🟥🟥"

    return f"""
══════════ RESULT ══════════

╭━━━━━━【⛨】━━━━━━╮
📊 {sig['pair']} | 🕘 {sig['entry_text']}

{status}

╰━━━━━━【⛨】━━━━━━╯

📳 Result Sent Successfully
💬 Contact: @{ADMIN_USERNAME}
"""


# =========================
# HANDLERS
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    if not is_joined(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🔐 First join our channel, then tap ✅ I JOINED.",
            reply_markup=join_markup(),
        )
        return

    bot.send_message(message.chat.id, start_text(message), reply_markup=main_menu())


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id

    if call.data == "check_join":
        if is_joined(uid):
            bot.send_message(call.message.chat.id, "✅ Access Approved!", reply_markup=main_menu())
        else:
            bot.send_message(
                call.message.chat.id,
                "❌ Join not detected.\n\nBot কে private channel এর admin করে দাও, তারপর আবার try করো।",
                reply_markup=join_markup(),
            )
        return

    if not is_joined(uid):
        bot.send_message(call.message.chat.id, "🔐 First join channel.", reply_markup=join_markup())
        return

    if call.data == "live_signal":
        sig = make_signal()
        pending_signals[sig["id"]] = {
            "signal": sig,
            "chat_id": call.message.chat.id,
        }

        bot.send_message(call.message.chat.id, signal_text(sig))

        # Admin হলে result control button দেখাবে
        if is_admin(call.from_user):
            bot.send_message(
                call.message.chat.id,
                "🛡 Select Result After Candle Close:",
                reply_markup=admin_result_markup(sig["id"]),
            )
        return

    if call.data == "result_checker":
        if not pending_signals:
            bot.send_message(call.message.chat.id, "📊 No pending signal result right now.", reply_markup=main_menu())
        else:
            bot.send_message(call.message.chat.id, "📊 Pending signal result available. Admin will publish soon.")
        return

    if call.data.startswith("result:"):
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Only admin can publish result.", show_alert=True)
            return

        _, result, signal_id = call.data.split(":")
        item = pending_signals.get(signal_id)

        if not item:
            bot.send_message(call.message.chat.id, "❌ Signal expired/not found.")
            return

        sig = item["signal"]

        # Entry candle শেষ হওয়ার আগে result publish করবে না
        publish_time = sig["entry_time"] + timedelta(minutes=1, seconds=5)
        wait = int((publish_time - now_bd()).total_seconds())

        if wait > 0:
            bot.send_message(call.message.chat.id, f"⏳ Result will publish after {wait} seconds...")
            time.sleep(wait)

        bot.send_message(item["chat_id"], result_text(sig, result), reply_markup=main_menu())
        pending_signals.pop(signal_id, None)
        return


print("✅ S_R X VENOM_AI Bot Running...")
bot.infinity_polling(skip_pending=True, timeout=60)
