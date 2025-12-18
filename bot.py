from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8541074478:AAGDuywv4_aKJ0ezvDSMH9WSCfGu8ZOv3Nk"
ADMIN_IDS = [8427136625]
LOG_CHANNEL_ID = -1003480204668

CHANNELS = [
    {"id": -1003480204668, "link": "https://t.me/+szU80GzwByEyOGE9"},
    {"id": -1003619502150, "link": "https://t.me/+5NLFRp1MIa85YTM1"},
    {"id": -1003567727910, "link": "https://t.me/+UPsmYolGEZI5OTA1"},
    {"id": -1003689409913, "link": "https://t.me/+3RFTEr00KzI2YWNl"},
    {"id": -1003689409913, "link": "https://t.me/+3RFTEr00KzI2YWNl"},
]

# ---------------- UTILS ---------------- #

async def check_membership(bot, user_id):
    not_joined = []
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch["id"], user_id)
            if member.status not in ("member", "administrator", "creator"):
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    return not_joined


def join_keyboard(channels):
    buttons = [[InlineKeyboardButton("🔗 Join Channel", url=ch["link"])]
               for ch in channels]
    buttons.append([InlineKeyboardButton("✅ Verify", callback_data="verify")])
    return InlineKeyboardMarkup(buttons)

# ---------------- START ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    not_joined = await check_membership(context.bot, user.id)

    if not_joined:
        await update.message.reply_text(
            "🚫 **Join all channels to continue**",
            reply_markup=join_keyboard(not_joined),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("✅ **You are verified!**")

# ---------------- VERIFY CALLBACK ---------------- #

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    not_joined = await check_membership(context.bot, user.id)

    if not_joined:
        await query.edit_message_text(
            "❌ **Still missing channels**",
            reply_markup=join_keyboard(not_joined),
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text("✅ **Verification successful!**")

        if LOG_CHANNEL_ID:
            await context.bot.send_message(
                LOG_CHANNEL_ID,
                f"✅ VERIFIED\n👤 {user.mention_html()}\n🆔 `{user.id}`",
                parse_mode="HTML"
            )

# ---------------- FORCE JOIN GROUP ---------------- #

async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if chat.type not in ("group", "supergroup"):
        return

    not_joined = await check_membership(context.bot, user.id)
    if not_joined:
        try:
            await update.message.delete()
        except:
            pass

        await context.bot.send_message(
            chat.id,
            f"🚫 {user.mention_html()} join required channels!",
            reply_markup=join_keyboard(not_joined),
            parse_mode="HTML"
        )

# ---------------- ADMIN PANEL ---------------- #

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    await update.message.reply_text("📊 Bot is running.\n✅ Verification active")

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    await update.message.reply_text("📜 Logs are sent to log channel.")

# ---------------- MAIN ---------------- #

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(verify_callback, pattern="verify"))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("logs", logs))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, force_join))

from telegram.ext import Application

app = Application.builder().token(BOT_TOKEN).build()

if __name__ == "__main__":
    app.run_polling()
    
