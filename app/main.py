import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from app.config import BOT_TOKEN
from downloader import download_video
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
async def format_callback(update, context):
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
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from downloader import download_video
import storage


async def quality_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, quality, job_id = query.data.split("|")

    job = storage.CACHE[job_id]
    job["quality"] = quality

    await query.edit_message_text("Downloading...")

    # Run blocking yt-dlp in thread
    file_path = await asyncio.to_thread(download_video, job)

    chat_id = query.message.chat.id

    try:
        if job["format"] == "mp4":
            video_path = file_path + ".mp4"

            with open(video_path, "rb") as f:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=f
                )

        else:
            audio_path = file_path + ".mp3"

            with open(audio_path, "rb") as f:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=f
                )

        await query.message.reply_text("Done ✔")

    except Exception as e:
        await query.message.reply_text(f"Error: {e}")

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