import os, random, time, threading, textwrap
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
MAX_SIGNALS_PER_DAY = 5

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
    today = str(now_bd().date())
    if uid not in users or users[uid]["date"] != today:
        users[uid] = {"date": today, "left": MAX_SIGNALS_PER_DAY, "auto": False}
    return users[uid]

def is_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ["left", "kicked"]
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
    signal_time = now_bd()
    entry_time = signal_time + timedelta(minutes=random.choice([2, 3]))
    expiry_time = entry_time + timedelta(minutes=1)

    return {
        "pair": random.choice(PAIRS),
        "direction": random.choice(["CALL", "PUT"]),
        "signal_time": signal_time.strftime("%H:%M"),
        "entry_time": entry_time.strftime("%H:%M"),
        "expiry_time": expiry_time.strftime("%H:%M"),
        "confidence": random.randint(90, 97),
        "trend": random.choice(["UPTREND", "DOWNTREND", "STRONG"]),
        "volume": random.choice(["STRONG", "MEDIUM", "HIGH"]),
        "result": random.choice(["WIN", "WIN", "WIN", "MTG WIN", "LOSS"])
    }

def make_signal_image(sig):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), "#061014")
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 54)
        font_med = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        font_small = ImageFont.truetype("DejaVuSans-Bold.ttf", 25)
        font_tiny = ImageFont.truetype("DejaVuSans.ttf", 20)
    except:
        font_big = font_med = font_small = font_tiny = ImageFont.load_default()

    green = "#39ff14"
    red = "#ff3131"
    cyan = "#00e5ff"
    yellow = "#ffe600"
    white = "#f5f5f5"
    gray = "#1b2a30"

    # Grid
    for x in range(0, W, 80):
        draw.line((x, 0, x, H), fill="#0e2228", width=1)
    for y in range(0, H, 60):
        draw.line((0, y, W, y), fill="#0e2228", width=1)

    # Header
    draw.text((35, 25), BOT_NAME, fill=white, font=font_big)
    draw.text((38, 88), "AI POWERED BINARY SIGNAL BOT", fill=green, font=font_small)
    draw.text((650, 35), "UTC+6 BANGLADESH TIME", fill=yellow, font=font_small)
    draw.text((650, 80), f"{now_bd().strftime('%d %b %Y')} | {now_bd().strftime('%I:%M:%S %p')}", fill=white, font=font_small)

    # Fake chart area
    chart_x, chart_y, chart_w, chart_h = 520, 140, 710, 410
    draw.rectangle((chart_x, chart_y, chart_x+chart_w, chart_y+chart_h), outline="#17414a", width=2)

    base = chart_y + 260
    cx = chart_x + 30
    price = base
    for i in range(25):
        up = random.choice([True, False])
        body = random.randint(25, 80)
        wick = random.randint(15, 55)
        color = green if up else red
        open_y = price
        close_y = price - body if up else price + body
        high = min(open_y, close_y) - wick
        low = max(open_y, close_y) + wick
        draw.line((cx+10, high, cx+10, low), fill=color, width=3)
        draw.rectangle((cx, min(open_y, close_y), cx+22, max(open_y, close_y)), fill=color)
        price = close_y + random.randint(-35, 35)
        price = max(chart_y+70, min(chart_y+chart_h-80, price))
        cx += 27

    # Lines
    draw.line((chart_x, chart_y+75, chart_x+chart_w, chart_y+75), fill=red, width=3)
    draw.line((chart_x, chart_y+260, chart_x+chart_w, chart_y+260), fill=green, width=3)
    draw.text((chart_x+15, chart_y+20), f"{sig['pair']} | M1 | {sig['direction']} | OTC", fill=white, font=font_tiny)

    # Signal arrow
    arrow_x, arrow_y = chart_x+560, chart_y+250
    sig_color = green if sig["direction"] == "CALL" else red
    draw.rounded_rectangle((arrow_x, arrow_y-40, arrow_x+120, arrow_y+10), radius=12, outline=sig_color, width=4)
    draw.text((arrow_x+20, arrow_y-32), sig["direction"], fill=sig_color, font=font_small)

    # Left signal panel
    px, py, pw, ph = 35, 160, 430, 430
    draw.rounded_rectangle((px, py, px+pw, py+ph), radius=22, outline=green, width=3, fill="#071b13")
    draw.text((px+45, py+25), ">> LIVE SIGNAL <<", fill=green, font=font_big)

    rows = [
        ("ASSET", sig["pair"], green),
        ("DIRECTION", sig["direction"], sig_color),
        ("SIGNAL TIME", sig["signal_time"], white),
        ("ENTRY TIME", f"{sig['entry_time']} CANDLE", yellow),
        ("EXPIRY", f"{sig['expiry_time']} (M1)", white),
        ("CONFIDENCE", f"{sig['confidence']}%", green),
        ("TREND", sig["trend"], green),
        ("VOLUME", sig["volume"], green),
    ]

    y = py + 105
    for label, value, col in rows:
        draw.rounded_rectangle((px+25, y, px+pw-25, y+45), radius=10, outline="#28545c", width=2)
        draw.text((px+45, y+9), label, fill=white, font=font_tiny)
        draw.text((px+210, y+7), value, fill=col, font=font_small)
        y += 50

    draw.rounded_rectangle((px+70, py+ph-48, px+pw-70, py+ph-12), radius=8, fill=green)
    draw.text((px+115, py+ph-45), "MTG 1 STEP IF LOSS", fill="#001000", font=font_small)

    # Bottom
    draw.rectangle((0, 620, W, H), fill="#03090b")
    draw.text((40, 650), "JOIN OUR PRIVATE CHANNEL", fill=white, font=font_small)
    draw.text((40, 685), "GET DAILY SIGNALS", fill=green, font=font_tiny)
    draw.text((470, 645), BOT_NAME, fill=white, font=font_big)
    draw.text((505, 692), "WE ANALYZE, YOU TRADE SAFELY", fill=green, font=font_tiny)
    draw.text((955, 650), "CONTACT ADMIN", fill=white, font=font_small)
    draw.text((955, 690), f"@{ADMIN_USERNAME}", fill=cyan, font=font_small)

    bio = BytesIO()
    img.save(bio, format="PNG")
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

def result_message(sig):
    if sig["result"] == "WIN":
        status = "🟩🟩 PROFIT ✅ 🟩🟩"
    elif sig["result"] == "MTG WIN":
        status = "🟨🟨 MTG 1 STEP PROFIT ✅ 🟨🟨"
    else:
        status = "🟥🟥 LOSS ❌ 🟥🟥"

    return f"""
✥═════ R | E | S | U | L | T ═════✥

📊 {sig['pair']} | 🕘 {sig['entry_time']} CANDLE
{status}

💬 Contact: @{ADMIN_USERNAME}
"""

def send_join(chat_id):
    bot.send_message(
        chat_id,
        "🔐 Access Locked\n\nএই bot use করতে আগে private channel এ join করতে হবে।\n\nJoin করার পরে ✅ I HAVE JOINED চাপো।",
        reply_markup=join_menu()
    )

def send_home(chat_id, user_id, name="Trader"):
    data = get_user(user_id)
    text = f"""
━━━━━━━━━━━━━━━━━━━━
| 🌪 {BOT_NAME} |
━━━━━━━━━━━━━━━━━━━━

✨ Welcome, {name}!

🤖 AI-powered Binary Signal Bot
📊 OTC + REAL Market
🕐 Timezone: UTC+6 Bangladesh
⌛ Signal Type: M1
🛡 MTG: 1 Step

📌 Signals remaining today: {data["left"]}

⬇️ Select option below:
"""
    bot.send_message(chat_id, text, reply_markup=main_menu())

@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    if not is_joined(uid):
        send_join(message.chat.id)
        return
    send_home(message.chat.id, uid, message.from_user.first_name or "Trader")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id

    if call.data == "check_join":
        if is_joined(uid):
            bot.send_message(call.message.chat.id, "✅ Access Approved!")
            send_home(call.message.chat.id, uid, call.from_user.first_name or "Trader")
        else:
            bot.send_message(call.message.chat.id, "❌ Channel join detect হয়নি। Bot কে private channel admin করো, তারপর আবার try করো।", reply_markup=join_menu())
        return

    if not is_joined(uid):
        send_join(call.message.chat.id)
        return

    data = get_user(uid)

    if call.data == "live":
        if data["left"] <= 0:
            bot.send_message(call.message.chat.id, "❌ Daily signal limit finished. Try tomorrow.", reply_markup=back_menu())
            return

        data["left"] -= 1
        sig = create_signal()
        last_signals[uid] = sig

        img = make_signal_image(sig)
        bot.send_photo(call.message.chat.id, img, caption=signal_caption(sig))
        bot.send_message(call.message.chat.id, f"📌 Remaining signals today: {data['left']}")

        def delayed_result():
            time.sleep(75)
            bot.send_message(call.message.chat.id, result_message(sig), reply_markup=main_menu())

        threading.Thread(target=delayed_result, daemon=True).start()

    elif call.data == "auto":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("▶️ START AUTO", callback_data="start_auto"),
            types.InlineKeyboardButton("🛑 STOP AUTO", callback_data="stop_auto"),
            types.InlineKeyboardButton("⬅️ BACK MENU", callback_data="back")
        )
        bot.send_message(call.message.chat.id, "🔥 AUTO SIGNAL MODE\n\nM1 signal, UTC+6, auto result enabled.", reply_markup=kb)

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

                bot.send_photo(chat_id, make_signal_image(sig), caption=signal_caption(sig))
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
            bot.send_message(call.message.chat.id, "❌ No signal found yet. Generate LIVE SIGNAL first.", reply_markup=back_menu())
        else:
            bot.send_message(call.message.chat.id, result_message(sig), reply_markup=main_menu())

    elif call.data == "back":
        send_home(call.message.chat.id, uid, call.from_user.first_name or "Trader")

print("S_R X VENOM_AI dynamic image bot running...")
bot.infinity_polling()
