import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from config import BOT_TOKEN
from queue import Queue
from .downloader import download_video
import storage


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send a video link (YouTube / TikTok / Instagram)"
    )


# ---------------- HANDLE LINK ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    job_id = str(len(storage.CACHE) + 1)

    storage.CACHE[job_id] = {"url": url}

    keyboard = [
        [InlineKeyboardButton("MP4", callback_data=f"mp4|{job_id}")],
        [InlineKeyboardButton("MP3", callback_data=f"mp3|{job_id}")]
    ]

    await update.message.reply_text(
        "Choose format:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- FORMAT SELECT ----------------
async def format_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    fmt, job_id = query.data.split("|")

    storage.CACHE[job_id]["format"] = fmt

    keyboard = [
        [InlineKeyboardButton("360p", callback_data=f"q|360|{job_id}")],
        [InlineKeyboardButton("720p", callback_data=f"q|720|{job_id}")],
        [InlineKeyboardButton("1080p", callback_data=f"q|1080|{job_id}")]
    ]

    await query.edit_message_text(
        "Choose quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- QUALITY SELECT ----------------
async def quality_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, quality, job_id = query.data.split("|")

    job = storage.CACHE[job_id]
    job["quality"] = quality

    await query.edit_message_text("Downloading...")

    file_path = await download_video(job)

    if job["format"] == "mp4":
        await context.bot.send_video(query.message.chat.id, video=open(file_path + ".mp4", "rb"))
    else:
        await context.bot.send_audio(query.message.chat.id, audio=open(file_path + ".mp3", "rb"))

    await query.message.reply_text("Done ✔")


# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.add_handler(CallbackQueryHandler(format_callback, pattern="^(mp4|mp3)"))
    app.add_handler(CallbackQueryHandler(quality_callback, pattern="^q\\|"))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()