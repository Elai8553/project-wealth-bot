# project-wealth-bot
Web version of ElijahBot for trading and betting insight. 

## Personal AI Telegram Bot

This repository contains a private Telegram bot powered by OpenAI's GPT models. The bot responds **only** to the Telegram user whose numeric ID is specified via the `ALLOWED_USER_ID` environment variable.

### Features

- End-to-end encrypted chat with OpenAI via Telegram
- Keeps short conversation history for context
- Rejects all unauthorized users automatically
- Easily extensible for new commands and capabilities

### Quick start

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your credentials:

   ```bash
   TELEGRAM_BOT_TOKEN=xxxxxxxxxx:YYYYYYYYYYYYYYYYYYYYY
   OPENAI_API_KEY=sk-...
   ALLOWED_USER_ID=123456789  # your own Telegram numeric id
   ```

   *Find your Telegram user ID by sending `/id` to [@userinfobot](https://t.me/userinfobot).*

3. Start the bot locally:

   ```bash
   python bot.py
   ```

4. Open Telegram, find your bot, and send `/start`.

### Deployment

The bot can run anywhere Python 3.9+ is available—Fly.io, Render, Railway, etc. Make sure to set the same environment variables in your hosting provider.

### Extending capabilities

The core logic lives in `bot.py`. Add new `CommandHandler` or custom `MessageHandler` instances to extend the bot. You may also hook into the `chat_handler` to intercept or transform messages before they are sent to OpenAI.

PRs welcome! 
