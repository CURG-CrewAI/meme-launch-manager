import os, threading, logging
import asyncio, traceback
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from adapters.telegram import TelegramAdapter
from src.meme_launch_manager.main import MemeLaunchFlow, MemeLaunchFlowState

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

_current_thread: threading.Thread | None = None
_io: TelegramAdapter | None = None
_current_chat_id: int | None = None

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(process)d - %(name)s:%(lineno)d - %(levelname)s: %(message)s",
)
log = logging.getLogger("bot")


# Error
async def error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = "".join(
        traceback.format_exception(None, context.error, context.error.__traceback__)
    )
    log.error("Unhandled error:\n%s", err)
    if update and getattr(update, "effective_chat", None):
        await context.bot.send_message(
            update.effective_chat.id, "Unexpected error occurred"
        )


# Commands
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Welcome to meme launch manager\n/help: Show commands"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Meme Launch Manager Commands:\n\n"
        "/start - Start bot\n"
        "/launch - Start meme launch manager\n"
        "/cancel - End meme launch manager\n"
        "/help - Show help\n"
    )
    await update.message.reply_text(help_text)


async def launch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _current_thread, _io, _current_chat_id

    if _current_thread and _current_thread.is_alive():
        await update.message.reply_text(
            "Already Start... if you want to restart /cacel and /launch"
        )
        return

    _current_chat_id = update.effective_chat.id
    loop = asyncio.get_running_loop()
    _io = TelegramAdapter(context.application, _current_chat_id, loop)
    await update.message.reply_text("Start meme launch manager flow, Plz answer!")

    def run_flow():
        global _current_thread, _io, _current_chat_id
        try:
            MemeLaunchFlow(io=_io, state=MemeLaunchFlowState()).kickoff()
        except Exception as e:
            log.exception("Flow Error Occured")
        finally:
            _io = None
            _current_chat_id = None
            _current_thread = None
            print("Clean All")

    _current_thread = threading.Thread(target=run_flow, daemon=True)
    _current_thread.start()


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _current_thread, _io, _current_chat_id
    _current_thread = None
    _io = None
    _current_chat_id = None
    await update.message.reply_text("Meme Launch Manage is canceled")


async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _io

    if not update.message:
        return

    if not _io:
        await update.message.reply_text("Start with /launch")
        return

    if update.message.text:
        _io.put_answer(update.message.text.strip())
        return

    if update.message.photo:
        sizes = update.message.photo
        small_id = sizes[0].file_id
        _io.put_answer({"type": "photo", "file_id": small_id})
        return

    _io.put_answer({"type": "unknown", "raw": update.message.to_dict()})


def main():
    app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()

    # commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("launch", launch_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(
        MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, inbox)
    )

    # error
    app.add_error_handler(error)
    # polls the bot
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
