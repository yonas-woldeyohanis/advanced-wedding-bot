import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties # <-- NEW IMPORT
from dotenv import load_dotenv
from aiohttp import web

# 1. Load environment variables (Bot Token)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file!")

# 2. Initialize Bot and Dispatcher
# Use DefaultBotProperties for aiogram 3.7.0+
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML")) # <-- CHANGED LINE
dp = Dispatcher()

# ==========================================
#              BOT LOGIC
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """This handles the /start command"""
    welcome_text = (
        f"Hello, <b>{message.from_user.first_name}</b>! 👋\n\n"
        f"I am the advanced Wedding Bot engine. 💍✨\n"
        f"I am currently alive and ready to be programmed!"
    )
    await message.answer(welcome_text)


# ==========================================
#        DUMMY WEB SERVER (FOR RENDER)
# ==========================================

async def handle_ping(request):
    """UptimeRobot will ping this URL to keep the bot awake."""
    return web.Response(text="Bot is awake and running!")

async def start_web_server():
    """Starts a tiny web server in the background."""
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render assigns a port dynamically. We use it if it exists, otherwise default to 8080.
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🌐 Dummy web server running on port {port}")


# ==========================================
#              MAIN STARTUP
# ==========================================

async def main():
    # Setup logging so we can see errors in the terminal
    logging.basicConfig(level=logging.INFO)
    
    # Start the web server concurrently
    await start_web_server()
    
    # Drop any old messages the bot received while it was offline
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling for Telegram messages
    logging.info("🤖 Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        # aiogram 3 requires asyncio.run()
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")