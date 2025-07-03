import os
import logging
from typing import List

from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

import openai
from dotenv import load_dotenv

# ---------------------------------------------------------------------------- #
# Configuration                                                                 #
# ---------------------------------------------------------------------------- #

load_dotenv()  # Load variables from .env if present

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "0"))  # Your Telegram ID
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

if not BOT_TOKEN:
    raise RuntimeError("Please set the TELEGRAM_BOT_TOKEN environment variable.")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")
if not ALLOWED_USER_ID:
    raise RuntimeError(
        "Please set the ALLOWED_USER_ID environment variable to your Telegram user id."
    )

openai.api_key = OPENAI_API_KEY

# ---------------------------------------------------------------------------- #
# Logging                                                                       #
# ---------------------------------------------------------------------------- #

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
# Helpers                                                                       #
# ---------------------------------------------------------------------------- #

def _authorized(update: Update) -> bool:
    """Check whether the incoming update is from the allowed user."""
    return (
        update.effective_user is not None
        and update.effective_user.id == ALLOWED_USER_ID
    )

async def _reject(update: Update) -> None:
    """Inform unauthorized users politely."""
    if update.message:
        await update.message.reply_text(
            "Sorry, this bot is private. You are not authorized to use it.",
            parse_mode=constants.ParseMode.MARKDOWN,
        )

# ---------------------------------------------------------------------------- #
# Command handlers                                                              #
# ---------------------------------------------------------------------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start command handler."""
    if not _authorized(update):
        await _reject(update)
        return

    await update.message.reply_text(
        "👋 Hello! I am your personal AI assistant, ready to help you with anything."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help command handler."""
    if not _authorized(update):
        await _reject(update)
        return

    help_text = (
        "I can answer your questions, write code, brainstorm ideas, and more. "
        "Just send me a message!"
    )
    await update.message.reply_text(help_text)

# ---------------------------------------------------------------------------- #
# ChatGPT-powered message handler                                               #
# ---------------------------------------------------------------------------- #

SYSTEM_PROMPT = (
    "You are a helpful, ever-advancing AI assistant integrated into a private Telegram bot. "
    "Answer concisely and helpfully. If code is requested, provide it in Markdown blocks."
)

HISTORY_KEY = "history"  # key used to store conversation history in chat_data
MAX_HISTORY_MESSAGES = 10  # keep last N messages for context

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages by forwarding them to OpenAI's ChatCompletion."""
    if not _authorized(update):
        await _reject(update)
        return

    user_message = update.message.text.strip()
    if not user_message:
        return

    # Retrieve history from context.chat_data
    history: List[dict] = context.chat_data.get(HISTORY_KEY, [])

    # Build the messages list for OpenAI
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": user_message},
    ]

    # Call OpenAI ChatCompletion
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
        )
        assistant_reply = response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("OpenAI API call failed: %s", e)
        assistant_reply = "⚠️ Sorry, something went wrong while contacting the AI service."

    # Update history and keep it trimmed
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": assistant_reply})
    context.chat_data[HISTORY_KEY] = history[-MAX_HISTORY_MESSAGES:]

    await update.message.reply_text(assistant_reply, parse_mode=constants.ParseMode.MARKDOWN)

# ---------------------------------------------------------------------------- #
# Main entry point                                                              #
# ---------------------------------------------------------------------------- #

async def main() -> None:
    """Start the bot."""
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Catch-all handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    # Run the bot until interrupted
    await application.initialize()
    logger.info("🤖 Bot started successfully.")
    await application.start()
    await application.updater.start_polling()
    await application.idle()

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())