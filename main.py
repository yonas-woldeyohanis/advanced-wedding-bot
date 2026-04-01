import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F  # <-- Notice 'F' is imported here
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from aiohttp import web

# Import our keyboard menu
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
#              COMMAND HANDLERS
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Handles the /start command"""
    welcome_text = (
        "📖 <b>ምሳሌ 18:22</b>\n"
        "<i>«ሚስት የሚያገኝ መልካም ነገርን ያገኛል፤ ከእግዚአብሔርም ዘንድ ሞገስን ይቀበላል።»</i>\n\n"
        "እንኳን ወደ <b>[የሙሽራው ስም] እና [የሙሽሪት ስም]</b> የጋብቻ ሥነ-ሥርዓት መረጃ መስጫ ቦት በሰላም መጡ! 😊 💍\n\n"
        "ይህ ቦት ስለ ሰርጉ ሙሉ መረጃ (የሰርጉ ቀን፣ ቦታ፣ የፎቶ ማዕከለ-ስዕላት እና ሌሎችም) የያዘ ነው። "
        "እባክዎ ከታች ያሉትን ቁልፎች በመጠቀም መረጃዎችን ያግኙ። 👇"
    )

    photo_path = "assets/welcome.jpg"

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=welcome_text, reply_markup=get_main_menu())
    else:
        await message.answer(text=welcome_text, reply_markup=get_main_menu())

# Works for both /developer and /development
@dp.message(Command("developer", "development"))
async def cmd_developer(message: types.Message):
    """Handles the developer commands"""
    dev_text = (
        "👨‍💻 <b>ስለ ሲስተም አልሚው (Developer)</b>\n\n"
        "ይህ የሰርግ ቦት ሲስተም የተገነባው በጥራት እና በዘመናዊ ቴክኖሎጂ ነው።\n\n"
        "ለራስዎ፣ ለወዳጅዎ ሰርግ፣ ወይም ለሌላ ፕሮግራም ተመሳሳይ ቦት ማሰራት ከፈለጉ:\n"
        "📞 <b>ስልክ:</b> +2519........\n"
        "💬 <b>ቴሌግራም:</b> @YourUsername\n"
    )
    await message.answer(dev_text)


# ==========================================
#              BUTTON HANDLERS
# ==========================================

@dp.message(F.text == "📅 ፕሮግራም እና ቦታ")
async def handle_program(message: types.Message):
    text = (
        "📅 <b>የፕሮግራም ዝርዝር</b>\n\n"
        "<b>የስርዓተ ተክሊል ፕሮግራም፡</b>\n"
        "📍 ቦታ: [የቤተክርስቲያን/የቦታ ስም]\n"
        "⏰ ሰዓት: ከጠዋቱ 4:00 ጀምሮ\n\n"
        "<b>የምሳ ግብዣ፡</b>\n"
        "📍 ቦታ: [የሆቴል/አዳራሽ ስም]\n"
        "⏰ ሰዓት: ከቀኑ 7:00 ጀምሮ\n\n"
        "<i>(ትክክለኛው መረጃ እዚህ ይገባል)</i>"
    )
    await message.answer(text)

@dp.message(F.text == "📍 ካርታ (Location)")
async def handle_location(message: types.Message):
    text = (
        "📍 <b>የአዳራሹ መገኛ (Google Maps)</b>\n\n"
        "እባክዎ ከታች ያለውን ሊንክ በመጫን አዳራሹ የሚገኝበትን ትክክለኛ ቦታ በካርታ ያግኙ።\n\n"
        "🔗 [የጎግል ማፕ ሊንክ እዚህ ይገባል]\n\n"
        "<i>(በቀጣይ ሎኬሽኑን በቀጥታ በቴሌግራም ካርታ እንዲልክ እናደርገዋለን)</i>"
    )
    await message.answer(text)

@dp.message(F.text == "📸 የቅድመ-ጋብቻ ፎቶዎች")
async def handle_photos(message: types.Message):
    text = (
        "📸 <b>የቅድመ-ጋብቻ (Pre-wedding) ፎቶዎች</b>\n\n"
        "በቅርቡ የሙሽሮቹን ውብ ፎቶዎች እዚህ ማየት ይችላሉ!\n\n"
        "<i>(በቀጣይ ክፍል ብዙ ፎቶዎችን በአንድ ጊዜ Album አድርጎ እንዲልክ እናስተካክለዋለን)</i>"
    )
    await message.answer(text)

@dp.message(F.text == "👗 የአለባበስ ዘይቤ")
async def handle_dress_code(message: types.Message):
    text = (
        "👗 <b>የአለባበስ ዘይቤ (Dress Code)</b>\n\n"
        "በዕለቱ የክብር እንግዶቻችን በሚከተሉት ቀለማት ደምቀው ቢገኙ ደስታችን እጥፍ ይሆናል፡\n\n"
        "🟢 አረንጓዴ\n"
        "🟡 ቢጫ\n"
        "<i>(ወይም የፈለጉትን የከለር ኮድ እዚህ እናስገባለን)</i>"
    )
    await message.answer(text)

@dp.message(F.text == "⏳ ስንት ቀን ቀረው?")
async def handle_countdown(message: types.Message):
    # Set the actual wedding date here (Year, Month, Day)
    wedding_date = datetime(2025, 9, 29) 
    today = datetime.now()
    
    delta = wedding_date - today
    days_left = delta.days

    if days_left > 0:
        text = f"⏳ <b>ስንት ቀን ቀረው?</b>\n\nለታላቁ የሰርጋችን ቀን <b>{days_left} ቀናት</b> ብቻ ቀርተውታል! በጉጉት እንጠብቆታለን። 🎉"
    elif days_left == 0:
        text = "🎉 <b>ዛሬ የተጠባበቅነው ታላቁ የሰርጋችን ቀን ነው!</b> 🎉\n\nበደስታችን አብረውን ስለሆኑ እናመሰግናለን!"
    else:
        text = "💍 <b>ሰርጋችን በስኬት ተጠናቋል!</b> አብረውን ስለነበሩ ከልብ እናመሰግናለን። 🙏"

    await message.answer(text)

@dp.message(F.text == "📝 የመልካም ምኞት መግለጫ")
async def handle_wishes(message: types.Message):
    text = (
        "📝 <b>የመልካም ምኞት መግለጫ</b>\n\n"
        "ለሙሽሮቹ ማስተላለፍ የሚፈልጉትን የመልካም ምኞት መልዕክት እና ምክር መፃፍ ይችላሉ።\n\n"
        "<i>(በቀጣይ ይህን ስንሰራው፣ ሰዎች የሚፅፉት መልዕክት በቀጥታ ለሙሽሮቹ ብቻ በሚታይ ሚስጥራዊ ቻናል እንዲገባ እናደርገዋለን!)</i>"
    )
    await message.answer(text)

@dp.message(F.text == "📖 የመጽሐፍ ቅዱስ ጥቅስ")
async def handle_bible_verse(message: types.Message):
    text = (
        "📖 <b>የዕለቱ ጥቅስ</b>\n\n"
        "<i>«ፍቅር ይታገሣል፥ ቸርነትንም ያደርጋል፤ ፍቅር አይቀናም፤ ፍቅር አይመካም፥ አይታበይም፤ የማይገባውን አያደርግም፥ የራሱን አይፈልግም፥ አይበሳጭም፥ በደልን አይቆጥርም፤»</i>\n"
        "<b>(፩ኛ ወደ ቆሮንቶስ ሰዎች 13፡4-5)</b>"
    )
    await message.answer(text)

@dp.message(F.text == "🔔 ማስታወሻ (Remind me)")
async def handle_reminder(message: types.Message):
    text = (
        "🔔 <b>የማስታወሻ ደወል (Reminder)</b>\n\n"
        "ማስታወሻዎን አብርተዋል። ሰርጉ <b>ከ3 ቀን በፊት</b>፣ <b>ከ1 ቀን በፊት</b> እና <b>በዕለቱ ጠዋት</b> ይህ ቦት መልዕክት ልኮ ያስታውሰዎታል!\n\n"
        "<i>(ይህን ወደፊት ዳታቤዝ (MongoDB) ስናገናኝ ትክክለኛ እንዲሆን አድርገን እንሰራዋለን)</i>"
    )
    await message.answer(text)


# ==========================================
#        DUMMY WEB SERVER (FOR RENDER)
# ==========================================
async def handle_ping(request):
    return web.Response(text="Bot is awake and running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🌐 Dummy web server running on port {port}")


# ==========================================
#              MAIN STARTUP
# ==========================================
async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("🤖 Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")