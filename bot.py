from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3, time, random, os

TOKEN = os.getenv("8869935767:AAG83Y-ietypiy_vFo5xH00l8xjd4RtufFw")  # Railway variable use করবা
ADMIN_ID = -1003738331357  # তোমার Telegram ID

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, coins INT, last_egg INT)")
conn.commit()

# START MENU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    cursor.execute("SELECT * FROM users WHERE id=?", (uid,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?,0,0)", (uid,))
        conn.commit()

    keyboard = [
        [InlineKeyboardButton("🥚 Collect Egg", callback_data="egg")],
        [InlineKeyboardButton("🎰 Spin", callback_data="spin")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎮 *Welcome to Egg Master Pro*\n\nEarn coins & enjoy!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# BUTTON HANDLER
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    # BALANCE
    if query.data == "balance":
        cursor.execute("SELECT coins FROM users WHERE id=?", (uid,))
        coins = cursor.fetchone()[0]

        await query.edit_message_text(f"💰 Balance: {coins}")

    # EGG SYSTEM
    elif query.data == "egg":
        cursor.execute("SELECT last_egg FROM users WHERE id=?", (uid,))
        last = cursor.fetchone()[0]
        now = int(time.time())

        if now - last < 10:
            await query.edit_message_text("⏱️ Wait 10 seconds!")
            return

        cursor.execute("UPDATE users SET coins=coins+10, last_egg=? WHERE id=?", (now, uid))
        conn.commit()

        await query.edit_message_text("🥚 You got 10 coins!")

    # SPIN SYSTEM
    elif query.data == "spin":
        num = random.randint(0,9)

        if num >= 5:
            win = 20
            msg = f"🎰 {num}\n🔥 Big Win +20"
        else:
            win = 5
            msg = f"🎰 {num}\n🙂 Small Win +5"

        cursor.execute("UPDATE users SET coins=coins+? WHERE id=?", (win, uid))
        conn.commit()

        await query.edit_message_text(msg)

# COMMANDS
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cursor.execute("SELECT coins FROM users WHERE id=?", (uid,))
    coins = cursor.fetchone()[0]

    await update.message.reply_text(f"💰 Balance: {coins}")

# RUN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("balance", balance))

print("Bot Running...")
app.run_polling()
