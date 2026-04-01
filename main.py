import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from aiohttp import web

# Import our database & keyboard functions
from keyboards import get_main_menu 
from database import add_user, toggle_reminder, save_wish, get_all_users

# 1. Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8339063491  
# 2. Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# --- FSM States ---
class WeddingStates(StatesGroup):
    waiting_for_wish = State()
    waiting_for_broadcast = State()

# ==========================================
#              COMMAND HANDLERS
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear() # Clear any active states
    await add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    
    welcome_text = (
        "📖 <b>ምሳሌ 18:22</b>\n"
        "<i>«ሚስት የሚያገኝ መልካም ነገርን ያገኛል፤ ከእግዚአብሔርም ዘንድ ሞገስን ይቀበላል።»</i>\n\n"
        "እንኳን ወደ <b>[Groom & Bride]</b> የሰርግ መረጃ መስጫ ቦት በሰላም መጡ! 😊 💍\n\n"
        "እባክዎ ከታች ያሉትን ቁልፎች በመጠቀም መረጃዎችን ያግኙ። 👇"
    )
    photo_path = "assets/welcome.jpg"
    if os.path.exists(photo_path):
        await message.answer_photo(photo=FSInputFile(photo_path), caption=welcome_text, reply_markup=get_main_menu())
    else:
        await message.answer(text=welcome_text, reply_markup=get_main_menu())

# --- ADMIN BROADCAST FEATURE ---
@dp.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return # Only you can use this
    await message.answer("📣 <b>ለሁሉም ተጠቃሚዎች የሚላከውን መልዕክት ይፃፉ፡</b>\n\n(ለመሰረዝ 'cancel' ብለው ይፃፉ)")
    await state.set_state(WeddingStates.waiting_for_broadcast)

@dp.message(WeddingStates.waiting_for_broadcast)
async def perform_broadcast(message: types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await state.clear()
        return await message.answer("❌ ብሮድካስት ተሰርዟል።")
    
    users = await get_all_users()
    count = 0
    await message.answer(f"⏳ ለ {len(users)} ተጠቃሚዎች በመላክ ላይ...")
    
    for user_id in users:
        try:
            await bot.send_message(user_id, f"📢 <b>አዲስ መልዕክት ከሙሽሮቹ፡</b>\n\n{message.text}")
            count += 1
            await asyncio.sleep(0.05) # Prevent Telegram flood limit
        except Exception:
            continue
    
    await message.answer(f"✅ መልዕክቱ ለ {count} ተጠቃሚዎች በተሳካ ሁኔታ ተልኳል!")
    await state.clear()

# ==========================================
#              BUTTON HANDLERS
# ==========================================

@dp.message(F.text == "📝 የመልካም ምኞት መግለጫ")
async def ask_for_wish(message: types.Message, state: FSMContext):
    await message.answer("✨ <b>የመልካም ምኞት መግለጫ</b>\n\nለሙሽሮቹ ማስተላለፍ የሚፈልጉትን መልዕክት እዚህ ይፃፉልን። (አንድ መልዕክት ብቻ መፃፍ ይችላሉ)")
    await state.set_state(WeddingStates.waiting_for_wish)

@dp.message(WeddingStates.waiting_for_wish)
async def process_wish(message: types.Message, state: FSMContext):
    if not message.text or len(message.text) < 3:
        return await message.answer("⚠️ እባክዎ ትርጉም ያለው መልዕክት ይፃፉ።")
    
    # Save to MongoDB
    await save_wish(message.from_user.id, message.from_user.full_name, message.text)
    
    # Notify the Admin (The Couple) immediately!
    notify_text = (
        "🔔 <b>አዲስ የመልካም ምኞት መልዕክት ደርሷል!</b>\n\n"
        f"👤 <b>ከ፡</b> {message.from_user.full_name}\n"
        f"📝 <b>መልዕክት፡</b> {message.text}"
    )
    await bot.send_message(ADMIN_ID, notify_text)
    
    await message.answer("🙏 <b>እናመሰግናለን!</b> መልዕክትዎ ለሙሽሮቹ ደርሷል።")
    await state.clear()

@dp.message(F.text == "⏳ ስንት ቀን ቀረው?")
async def handle_countdown(message: types.Message):
    wedding_date = datetime(2025, 9, 29) 
    days_left = (wedding_date - datetime.now()).days
    text = f"⏳ <b>ስንት ቀን ቀረው?</b>\n\nለታላቁ የሰርጋችን ቀን <b>{days_left} ቀናት</b> ቀርተዋል! 🎉" if days_left > 0 else "🎉 ዛሬ ቀኑ ነው!"
    await message.answer(text)

@dp.message(F.text == "📅 ፕሮግራም እና ቦታ")
async def handle_prog(message: types.Message):
    await message.answer("📅 <b>የፕሮግራም ዝርዝር</b>\n\n📍 ስርዓተ ተክሊል፡ [ቦታ]\n📍 የምሳ ግብዣ፡ [ቦታ]")

@dp.message(F.text == "📍 ካርታ (Location)")
async def handle_loc(message: types.Message):
    # Pro Tip: Send an actual location object instead of just text
    # await message.answer_location(latitude=9.006, longitude=38.767)
    await message.answer("📍 <b>ካርታ፡</b> https://maps.google.com/...")

@dp.message(F.text == "📸 የቅድመ-ጋብቻ ፎቶዎች")
async def handle_pics(message: types.Message):
    await message.answer("📸 <b>ፎቶዎች፡</b> በቅርቡ ውብ ፎቶዎችን እዚህ እናጋራለን!")

@dp.message(F.text == "👗 የአለባበስ ዘይቤ")
async def handle_dress(message: types.Message):
    await message.answer("👗 <b>አለባበስ፡</b> አረንጓዴ እና ቢጫ።")

@dp.message(F.text == "📖 የመጽሐፍ ቅዱስ ጥቅስ")
async def handle_bible(message: types.Message):
    await message.answer("📖 <i>«ፍቅር ይታገሣል፥ ቸርነትንም ያደርጋል...»</i> (1ቆሮ 13፡4)")

@dp.message(F.text == "🔔 ማስታወሻ (Remind me)")
async def handle_remind(message: types.Message):
    await toggle_reminder(message.from_user.id, True)
    await message.answer("✅ <b>የማስታወሻ ደወል በርቷል!</b>")

# ==========================================
#        DUMMY WEB SERVER & STARTUP
# ==========================================
async def handle_ping(r): return web.Response(text="Alive")
async def start_web_server():
    app = web.Application(); app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app); await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try: asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass