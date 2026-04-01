import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from aiohttp import web

# Import our updated keyboard menu
from keyboards import get_main_menu 

# 1. Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file!")

# 2. Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ==========================================
#              BOT LOGIC
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Handles the /start command"""
    
    # Clean, professional, pure Amharic welcome message
    welcome_text = (
        "📖 <b>ምሳሌ 18:22</b>\n"
        "<i>«ሚስት የሚያገኝ መልካም ነገርን ያገኛል፤ ከእግዚአብሔርም ዘንድ ሞገስን ይቀበላል።»</i>\n\n"
        "እንኳን ወደ <b>[የሙሽራው ስም] እና [የሙሽሪት ስም]</b> የጋብቻ ሥነ-ሥርዓት መረጃ መስጫ ቦት በሰላም መጡ! 😊 💍\n\n"
        "ይህ ቦት ስለ ሰርጉ ሙሉ መረጃ (የሰርጉ ቀን፣ ቦታ፣ የፎቶ ማዕከለ-ስዕላት እና ሌሎችም) የያዘ ነው። "
        "እባክዎ ከታች ያሉትን ቁልፎች በመጠቀም መረጃዎችን ያግኙ። 👇"
    )

    photo_path = "assets/welcome.jpg"

    # Send with photo if it exists in the assets folder
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(
            photo=photo, 
            caption=welcome_text, 
            reply_markup=get_main_menu()
        )
    else:
        # Fallback if photo is missing
        await message.answer(
            text=welcome_text,
            reply_markup=get_main_menu()
        )

@dp.message(Command("developer"))
async def cmd_developer(message: types.Message):
    """Handles the /developer command (Hidden from main menu)"""
    
    dev_text = (
        "👨‍💻 <b>ስለ ዴቨሎፐሩ</b>\n\n"
        "ይህ የሰርግ ቦት ሲስተም የተገነባው በጥራት እና በዘመናዊ ቴክኖሎጂ ነው።\n\n"
        "ለራስዎ፣ ለወዳጅዎ ሰርግ፣ ወይም ለሌላ ፕሮግራም ተመሳሳይ ቦት ማሰራት ከፈለጉ:\n"
        "📞 <b>ስልክ:</b> +251912345678\n"
        "💬 <b>ቴሌግራም:</b> @YourUsername\n"
    )
    
    await message.answer(dev_text)


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
    
    # Render assigns a port dynamically. Default to 8080 locally.
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🌐 Dummy web server running on port {port}")


# ==========================================
#              MAIN STARTUP
# ==========================================

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Start the web server concurrently
    await start_web_server()
    
    # Drop any old messages
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling
    logging.info("🤖 Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")