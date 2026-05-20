import os, random, time, threading
from datetime import datetime, timedelta, timezone
from io import BytesIO

import telebot
from telebot import types
from PIL import Image, ImageDraw, ImageFont
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BOT_NAME = "S_R X VENOM_AI"
ADMIN_USERNAME = "srtraderowner_098"

CHANNEL_ID = -1002734046747
CHANNEL_INVITE_LINK = "https://t.me/+jlIIxaT6OB0wNDk1"

BD_TZ = timezone(timedelta(hours=6))
MAX_SIGNALS = 5

users = {}
last_signals = {}

PAIRS = [
    "USDIDR-OTC", "USDBDT-OTC", "USDINR-OTC", "USDBRL-OTC",
    "USDMXN-OTC", "USDNGN-OTC", "EURUSD-OTC", "GBPUSD-OTC",
    "EURJPY-REAL", "AUDJPY-REAL", "EURUSD-REAL"
]

def now_bd():
    return datetime.now(BD_TZ)

def get_user(uid):
    today = now_bd().strftime("%Y-%m-%d")
    if uid not in users or users[uid]["date"] != today:
        users[uid] = {"date": today, "left": MAX_SIGNALS, "auto": False}
    return users[uid]

def is_joined(uid):
    try:
        m = bot.get_chat_member(CHANNEL_ID, uid)
        return m.status not in ["left", "kicked"]
    except:
        return False

def join_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📢 JOIN PRIVATE CHANNEL", url=CHANNEL_INVITE_LINK),
        types.InlineKeyboardButton("✅ I HAVE JOINED", callback_data="check_join"),
        types.InlineKeyboardButton("👨‍💻 CONTACT ADMIN", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    return kb

def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📊 LIVE SIGNAL", callback_data="live"),
        types.InlineKeyboardButton("🔥 AUTO SIGNAL", callback_data="auto"),
        types.InlineKeyboardButton("🌈 RESULT CHECKER", callback_data="result"),
        types.InlineKeyboardButton("👨‍💻 CONTACT", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    return kb

def back_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ BACK MENU", callback_data="back"))
    return kb

def create_signal():
    now = now_bd()
    entry = now + timedelta(minutes=random.choice([2, 3]))
    return {
        "pair": random.choice(PAIRS),
        "direction": random.choice(["CALL", "PUT"]),
        "signal_time": now.strftime("%H:%M"),
        "entry_time": entry.strftime("%H:%M"),
        "confidence": random.randint(90, 97),
        "result": random.choice(["WIN", "WIN", "WIN", "MTG WIN", "LOSS"])
    }

def make_image(sig):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), "#061014")
    d = ImageDraw.Draw(img)

    try:
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 56)
        med = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        small = ImageFont.truetype("DejaVuSans.ttf", 26)
    except:
        big = med = small = ImageFont.load_default()

    green = "#39ff14"
    red = "#ff3131"
    yellow = "#ffe600"
    white = "#f5f5f5"
    cyan = "#00e5ff"

    for x in range(0, W, 80):
        d.line((x, 0, x, H), fill="#10262c")
    for y in range(0, H, 60):
        d.line((0, y, W, y), fill="#10262c")

    d.text((40, 30), BOT_NAME, fill=white, font=big)
    d.text((45, 95), "AI POWERED BINARY SIGNAL BOT", fill=green, font=small)
    d.text((750, 45), "UTC+6 BANGLADESH TIME", fill=yellow, font=small)
    d.text((750, 85), now_bd().strftime("%d %b %Y | %I:%M:%S %p"), fill=white, font=small)

    d.rounded_rectangle((40, 170, 500, 590), radius=25, outline=green, width=4, fill="#071b13")
    d.text((105, 200), "LIVE SIGNAL", fill=green, font=big)

    sig_color = green if sig["direction"] == "CALL" else red
    rows = [
        ("PAIR", sig["pair"], green),
        ("DIRECTION", sig["direction"], sig_color),
        ("SIGNAL", sig["signal_time"] + " UTC+6", white),
        ("ENTRY", sig["entry_time"] + " CANDLE", yellow),
        ("EXPIRY", "M1", white),
        ("CONFIDENCE", str(sig["confidence"]) + "%", green),
        ("MTG", "1 STEP IF LOSS", yellow),
    ]

    y = 285
    for label, value, color in rows:
        d.rounded_rectangle((70, y, 470, y + 42), radius=10, outline="#28545c", width=2)
        d.text((90, y + 8), label, fill=white, font=small)
        d.text((245, y + 8), value, fill=color, font=small)
        y += 50

    # chart area
    d.rectangle((560, 170, 1220, 560), outline="#17414a", width=3)
    cx = 590
    price = 380
    for _ in range(22):
        up = random.choice([True, False])
        body = random.randint(25, 75)
        wick = random.randint(15, 45)
        color = green if up else red
        open_y = price
        close_y = price - body if up else price + body
        high = min(open_y, close_y) - wick
        low = max(open_y, close_y) + wick
        d.line((cx + 10, high, cx + 10, low), fill=color, width=3)
        d.rectangle((cx, min(open_y, close_y), cx + 24, max(open_y, close_y)), fill=color)
        price = max(230, min(500, close_y + random.randint(-35, 35)))
        cx += 28

    d.text((590, 190), f"{sig['pair']} | M1 | {sig['direction']}", fill=white, font=small)
    d.rounded_rectangle((930, 460, 1135, 520), radius=15, outline=sig_color, width=4)
    d.text((965, 472), sig["direction"], fill=sig_color, font=med)

    d.rectangle((0, 630, W, H), fill="#02090b")
    d.text((60, 660), "PRIVATE SIGNAL ACCESS", fill=white, font=small)
    d.text((500, 650), BOT_NAME, fill=green, font=big)
    d.text((960, 660), f"@{ADMIN_USERNAME}", fill=cyan, font=small)

    bio = BytesIO()
    img.save(bio, "PNG")
    bio.seek(0)
    return bio

def signal_caption(sig):
    return f"""
═════【 {BOT_NAME} 】═════

💎 ACTIVE PAIR »» {sig['pair']}
⏰ SIGNAL TIME »» {sig['signal_time']} UTC+6
🕯 ENTRY TIME »» {sig['entry_time']} CANDLE
⌛ EXPIRATION »» M1
🔴 DIRECTION »» {sig['direction']}
✨ CONFIDENCE »» {sig['confidence']}%

‼️ MTG 1 STEP IF LOSS ‼️
"""

def result_text(sig):
    if sig["result"] == "WIN":
        r = "🟩🟩 PROFIT ✅ 🟩🟩"
    elif sig["result"] == "MTG WIN":
        r = "🟨🟨 MTG 1 STEP PROFIT ✅ 🟨🟨"
    else:
        r = "🟥🟥 LOSS ❌ 🟥🟥"

    return f"""
✥═════ R | E | S | U | L | T ═════✥

📊 {sig['pair']}
🕯 Entry: {sig['entry_time']} CANDLE
{r}

💬 Contact: @{ADMIN_USERNAME}
"""

def send_join(chat_id):
    bot.send_message(
        chat_id,
        "🔐 Access Locked\n\nআগে private channel এ join করো।\nJoin করার পরে ✅ I HAVE JOINED চাপো।",
        reply_markup=join_menu()
    )

def home(chat_id, uid, name="Trader"):
    data = get_user(uid)
    bot.send_message(chat_id, f"""
━━━━━━━━━━━━━━━━━━━━
| 🌪 {BOT_NAME} |
━━━━━━━━━━━━━━━━━━━━

✨ Welcome, {name}!

📊 OTC + REAL Market
🕐 Timezone: UTC+6 Bangladesh
⌛ Signal Type: M1
🛡 MTG: 1 Step

📌 Signals remaining today: {data['left']}

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
def callback(call):
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

    data = get_user(uid)

    if call.data == "live":
        if data["left"] <= 0:
            bot.send_message(call.message.chat.id, "❌ Daily signal limit finished.", reply_markup=back_menu())
            return

        data["left"] -= 1
        sig = create_signal()
        last_signals[uid] = sig

        bot.send_photo(call.message.chat.id, make_image(sig), caption=signal_caption(sig))
        bot.send_message(call.message.chat.id, f"📌 Remaining signals today: {data['left']}")

        def delayed():
            time.sleep(75)
            bot.send_message(call.message.chat.id, result_text(sig), reply_markup=main_menu())

        threading.Thread(target=delayed, daemon=True).start()

    elif call.data == "auto":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("▶️ START AUTO", callback_data="start_auto"),
            types.InlineKeyboardButton("🛑 STOP AUTO", callback_data="stop_auto"),
            types.InlineKeyboardButton("⬅️ BACK MENU", callback_data="back")
        )
        bot.send_message(call.message.chat.id, "🔥 AUTO SIGNAL MODE\n\nM1 + UTC+6 + Auto result.", reply_markup=kb)

    elif call.data == "start_auto":
        if data["auto"]:
            bot.send_message(call.message.chat.id, "⚠️ Auto already running.")
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
                bot.send_photo(chat_id, make_image(sig), caption=signal_caption(sig))
                time.sleep(75)
                bot.send_message(chat_id, result_text(sig))
                time.sleep(45)

        threading.Thread(target=auto_run, args=(call.message.chat.id, uid), daemon=True).start()

    elif call.data == "stop_auto":
        data["auto"] = False
        bot.send_message(call.message.chat.id, "🛑 Auto stopped.", reply_markup=back_menu())

    elif call.data == "result":
        sig = last_signals.get(uid)
        if not sig:
            bot.send_message(call.message.chat.id, "❌ আগে LIVE SIGNAL generate করো।", reply_markup=back_menu())
        else:
            bot.send_message(call.message.chat.id, result_text(sig), reply_markup=main_menu())

    elif call.data == "back":
        home(call.message.chat.id, uid, call.from_user.first_name or "Trader")

# Render Web Service keep-alive
app = Flask(__name__)

@app.route("/")
def index():
    return "S_R X VENOM_AI bot is running."

def run_bot():
    print("Bot polling started...")
    bot.infinity_polling(skip_pending=True, timeout=60)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
