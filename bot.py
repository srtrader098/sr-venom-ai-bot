import os, random, time, threading
from datetime import datetime, timedelta, timezone
from io import BytesIO
import telebot
from telebot import types
from PIL import Image, ImageDraw, ImageFont

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BOT_NAME = "S_R X VENOM_AI"
ADMIN_USERNAME = "srtraderowner_098"
CHANNEL_ID = -1002734046747
CHANNEL_INVITE_LINK = "https://t.me/+jlIIxaT6OB0wNDk1"

BD_TZ = timezone(timedelta(hours=6))
MAX_SIGNALS = 5

users = {}
last_signal = {}
stats = {"win": 25, "loss": 8}

PAIRS = [
    "USD/IDR (OTC)", "USD/BDT (OTC)", "USD/INR (OTC)",
    "USD/BRL (OTC)", "USD/MXN (OTC)", "EUR/USD (OTC)"
]

def now_bd():
    return datetime.now(BD_TZ)

def get_user(uid):
    today = now_bd().strftime("%Y-%m-%d")
    if uid not in users or users[uid]["date"] != today:
        users[uid] = {"date": today, "left": MAX_SIGNALS}
    return users[uid]

def is_joined(uid):
    try:
        m = bot.get_chat_member(CHANNEL_ID, uid)
        return m.status not in ["left", "kicked"]
    except:
        return False

def join_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 JOIN CHANNEL", url=CHANNEL_INVITE_LINK))
    kb.add(types.InlineKeyboardButton("✅ I HAVE JOINED", callback_data="check_join"))
    return kb

def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📊 LIVE SIGNAL", callback_data="live"),
        types.InlineKeyboardButton("🌈 RESULT CHECKER", callback_data="result"),
        types.InlineKeyboardButton("👨‍💻 CONTACT", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    return kb

def make_chart_image(sig, result=None):
    img = Image.new("RGB", (900, 430), "#05090b")
    d = ImageDraw.Draw(img)

    try:
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        med = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        small = ImageFont.truetype("DejaVuSans.ttf", 18)
    except:
        big = med = small = ImageFont.load_default()

    green = "#21ff38"
    red = "#ff2b3d"
    white = "#f1f1f1"
    gray = "#24313a"

    for x in range(0, 900, 70):
        d.line((x, 0, x, 430), fill="#101820")
    for y in range(0, 430, 55):
        d.line((0, y, 900, y), fill="#101820")

    d.text((20, 15), f"{sig['pair']} | M1 | {sig['direction']} | OTC", fill=white, font=small)

    x = 40
    price = 260
    for i in range(26):
        up = random.choice([True, False])
        body = random.randint(18, 65)
        wick = random.randint(10, 35)
        color = green if up else red

        o = price
        c = price - body if up else price + body
        hi = min(o, c) - wick
        lo = max(o, c) + wick

        d.line((x+10, hi, x+10, lo), fill=color, width=2)
        d.rectangle((x, min(o,c), x+20, max(o,c)), fill=color)
        price = max(90, min(350, c + random.randint(-25, 25)))
        x += 31

    d.line((20, 80, 880, 80), fill=red, width=3)
    d.line((20, 355, 880, 355), fill="#0088ff", width=3)

    sig_color = green if sig["direction"] == "CALL" else red
    d.rounded_rectangle((660, 210, 820, 270), radius=15, outline=sig_color, width=4)
    d.text((700, 225), sig["direction"], fill=sig_color, font=big)

    if result:
        r_color = green if "WIN" in result else red
        d.rounded_rectangle((650, 285, 835, 340), radius=15, outline=r_color, width=4)
        d.text((690, 300), result, fill=r_color, font=big)

    bio = BytesIO()
    img.save(bio, "PNG")
    bio.seek(0)
    return bio

def create_signal():
    current = now_bd()
    entry = current + timedelta(minutes=random.choice([2, 3]))
    result_time = entry + timedelta(seconds=75)

    return {
        "pair": random.choice(PAIRS),
        "direction": random.choice(["CALL", "PUT"]),
        "signal_time": current.strftime("%H:%M:%S"),
        "entry_time": entry.strftime("%H:%M"),
        "result_time": result_time,
        "price": f"{random.uniform(1.10000, 1.99999):.5f}",
        "result": random.choice(["WIN", "WIN", "WIN", "MTG WIN", "LOSS"])
    }

def signal_caption(sig):
    return f"""
==== {BOT_NAME} PREMIUM ====

╭━━━━━━━・◆・━━━━━━━╮
📊 PAIR     → {sig['pair']}
🕘 TIME     → {sig['signal_time']}
⌛ EXPIRY   → M1
🟢 DIRECTION → {sig['direction']}
🎯 PRICE    → {sig['price']}
🕯 ENTRY    → {sig['entry_time']} CANDLE
╰━━━━━━━・◆・━━━━━━━╯

🔁 MTG 1 STEP IF LOSS

📳 Signal Sent Successfully
🎯 Send Signal Screenshot

👨‍💻 Contact: @{ADMIN_USERNAME}
"""

def result_caption(sig):
    if sig["result"] == "WIN":
        result_line = "🟩🟩🟩 SURESHOT WIN 🟩🟩🟩"
        stats["win"] += 1
    elif sig["result"] == "MTG WIN":
        result_line = "🟨🟨🟨 SURESHOT MTG 🟨🟨🟨"
        stats["win"] += 1
    else:
        result_line = "🟥🟥🟥 LOSS ❌ 🟥🟥🟥"
        stats["loss"] += 1

    total = stats["win"] + stats["loss"]
    rate = round((stats["win"] / total) * 100, 1)

    return f"""
========== RESULT ==========

💹 {sig['pair']} | 🕘 {sig['entry_time']}

{result_line}

╭━━━━━━━・◆・━━━━━━━╮
🚀 Win: {stats['win']} | Loss: {stats['loss']} ({rate}%)
🔥 Current Pair: 3x2 (60.0%)
╰━━━━━━━・◆・━━━━━━━╯

📳 Result Sent Successfully

👨‍💻 Contact: @{ADMIN_USERNAME}
"""

def send_join(chat_id):
    bot.send_message(
        chat_id,
        "🔐 Access Locked\n\nআগে private channel এ join করো। তারপর ✅ I HAVE JOINED চাপো।",
        reply_markup=join_menu()
    )

def home(chat_id, uid, name):
    u = get_user(uid)
    bot.send_message(chat_id, f"""
━━━━━━━━━━━━━━━━━━━━
| {BOT_NAME} |
━━━━━━━━━━━━━━━━━━━━

✨ Welcome, {name}!

📊 Premium Binary Signal Bot
🕐 Timezone: UTC+6 Bangladesh
⌛ Signal: M1
🔁 MTG: 1 Step

📌 Signals remaining today: {u['left']}

⬇️ Select option below:
""", reply_markup=main_menu())

@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.from_user.id
    if not is_joined(uid):
        send_join(msg.chat.id)
        return
    home(msg.chat.id, uid, msg.from_user.first_name or "Trader")

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id

    if call.data == "check_join":
        if is_joined(uid):
            bot.send_message(call.message.chat.id, "✅ Access Approved!")
            home(call.message.chat.id, uid, call.from_user.first_name or "Trader")
        else:
            bot.send_message(call.message.chat.id, "❌ Join detect হয়নি। Bot কে channel admin করো।", reply_markup=join_menu())
        return

    if not is_joined(uid):
        send_join(call.message.chat.id)
        return

    u = get_user(uid)

    if call.data == "live":
        if u["left"] <= 0:
            bot.send_message(call.message.chat.id, "❌ Daily signal limit finished.")
            return

        u["left"] -= 1
        sig = create_signal()
        last_signal[uid] = sig

        bot.send_photo(call.message.chat.id, make_chart_image(sig), caption=signal_caption(sig))
        bot.send_message(call.message.chat.id, f"📌 Remaining Signals: {u['left']}")

        def send_result_later():
            wait = max(5, int((sig["result_time"] - now_bd()).total_seconds()))
            time.sleep(wait)
            bot.send_photo(
                call.message.chat.id,
                make_chart_image(sig, sig["result"].replace("MTG WIN", "WIN")),
                caption=result_caption(sig),
                reply_markup=main_menu()
            )

        threading.Thread(target=send_result_later, daemon=True).start()

    elif call.data == "result":
        sig = last_signal.get(uid)
        if not sig:
            bot.send_message(call.message.chat.id, "❌ আগে LIVE SIGNAL নাও।")
        else:
            bot.send_photo(call.message.chat.id, make_chart_image(sig, "WIN"), caption=result_caption(sig), reply_markup=main_menu())

print("V2 premium bot running...")
bot.infinity_polling(skip_pending=True)
