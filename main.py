import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile, CallbackQuery # <-- NEW IMPORT
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from aiohttp import web

from keyboards import get_main_menu 
from database import add_user, toggle_reminder, save_wish, get_all_users

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 123456789 # <--- REPLACE WITH YOUR REAL ID

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

class WeddingStates(StatesGroup):
    waiting_for_wish = State()
    waiting_for_broadcast = State()

# ==========================================
#              CORE COMMANDS
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    
    welcome_text = (
        "📖 <b>ምሳሌ 18:22</b>\n<i>«ሚስት የሚያገኝ መልካም ነገርን ያገኛል፤...»</i>\n\n"
        "እንኳን ወደ <b>[ሙሽራ] እና [ሙሽሪት]</b> የሰርግ መረጃ መስጫ ቦት በሰላም መጡ! 😊 💍\n\n"
        "እባክዎ ከታች ያሉትን ቁልፎች በመጫን ዝርዝር መረጃዎችን ያግኙ። 👇"
    )
    
    photo_path = "assets/welcome.jpg"
    if os.path.exists(photo_path):
        await message.answer_photo(photo=FSInputFile(photo_path), caption=welcome_text, reply_markup=get_main_menu())
    else:
        await message.answer(text=welcome_text, reply_markup=get_main_menu())

# ==========================================
#           INLINE BUTTON HANDLERS
# ==========================================

@dp.callback_query(F.data == "btn_program")
async def handle_prog(callback: CallbackQuery):
    await callback.message.answer("📅 <b>የፕሮግራም ዝርዝር</b>\n\n📍 ስርዓተ ተክሊል፡ [ቦታ]\n⏰ ሰዓት: 4:00\n\n📍 የምሳ ግብዣ፡ [ቦታ]\n⏰ ሰዓት: 7:00")
    await callback.answer() # Stops the loading spinner on the button

@dp.callback_query(F.data == "btn_location")
async def handle_loc(callback: CallbackQuery):
    await callback.message.answer("📍 <b>የአዳራሹ መገኛ (ካርታ)</b>\n\n🔗 https://maps.google.com/...")
    await callback.answer()

@dp.callback_query(F.data == "btn_countdown")
async def handle_countdown(callback: CallbackQuery):
    wedding_date = datetime(2025, 9, 29)
    days_left = (wedding_date - datetime.now()).days
    await callback.message.answer(f"⏳ <b>ስንት ቀን ቀረው?</b>\n\nለታላቁ የሰርጋችን ቀን <b>{max(0, days_left)} ቀናት</b> ቀርተዋል! 🎉")
    await callback.answer()

@dp.callback_query(F.data == "btn_bible")
async def handle_bible(callback: CallbackQuery):
    await callback.message.answer("📖 <i>«ፍቅር ይታገሣል፥ ቸርነትንም ያደርጋል...»</i> (1ቆሮ 13፡4)")
    await callback.answer()


@dp.callback_query(F.data == "btn_remind")
async def handle_remind(callback: CallbackQuery):
    # 1. IMMEDIATELY stop the loading spinner (Makes it feel instant)
    await callback.answer("ጥያቄዎ እየተሰራ ነው...") 
    
    # 2. DO the database work in the background
    await toggle_reminder(callback.from_user.id, True)
    
    # 3. SEND the reply
    await callback.message.answer("✅ <b>የማስታወሻ ደወል በርቷል!</b>")

# --- PHOTO GALLERY (INLINE TRIGGER) ---
@dp.callback_query(F.data == "btn_photos")
async def handle_photos(callback: CallbackQuery):
    gallery_path = "assets/gallery/"
    if not os.path.exists(gallery_path) or not os.listdir(gallery_path):
        await callback.message.answer("📸 ፎቶዎች በቅርቡ ይጫናሉ!")
        return await callback.answer()

    anim_msg = await callback.message.answer("⏳ ፎቶዎችን በማዘጋጀት ላይ...")
    for i in ["3...", "2...", "1...", "🚀 እነሆ!"]:
        await asyncio.sleep(0.7)
        await anim_msg.edit_text(f"📸 <b>ፎቶዎችን በማዘጋጀት ላይ...</b>\n\n{i}")
    
    await anim_msg.delete()
    photos = sorted([f for f in os.listdir(gallery_path) if f.endswith(('.jpg', '.png', '.jpeg'))])
    for photo_name in photos:
        await callback.message.answer_photo(photo=FSInputFile(os.path.join(gallery_path, photo_name)))
        await asyncio.sleep(1.2)
    
    await callback.answer()

# --- GUESTBOOK (INLINE TRIGGER) ---
@dp.callback_query(F.data == "btn_wish")
async def ask_for_wish(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✨ <b>የመልካም ምኞት መግለጫ</b>\n\nለሙሽሮቹ ማስተላለፍ የሚፈልጉትን መልዕክት እዚህ ይፃፉልን።")
    await state.set_state(WeddingStates.waiting_for_wish)
    await callback.answer()

@dp.message(WeddingStates.waiting_for_wish)
async def process_wish(message: types.Message, state: FSMContext):
    await save_wish(message.from_user.id, message.from_user.full_name, message.text)
    
    # Forward original message to Admin (so you can click user name)
    await bot.forward_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
    
    # Detailed info with direct profile link
    user_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>"
    admin_info = (f"✅ <b>አዲስ መልዕክት ደርሷል!</b>\n👤 <b>ከ፡</b> {user_link}\n🆔 <b>ID:</b> <code>{message.from_user.id}</code>")
    await bot.send_message(ADMIN_ID, admin_info)
    
    await message.answer("🙏 <b>እናመሰግናለን!</b> መልዕክትዎ ለሙሽሮቹ ደርሷል።")
    await state.clear()

# ==========================================
#              ADMIN BROADCAST
# ==========================================

@dp.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("📣 <b>ለመላክ የሚፈልጉትን መልዕክት ይፃፉ፡</b>\n\nለመሰረዝ 'cancel' ይበሉ።")
    await state.set_state(WeddingStates.waiting_for_broadcast)

@dp.message(WeddingStates.waiting_for_broadcast)
async def perform_broadcast(message: types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await state.clear()
        return await message.answer("❌ ተሰርዟ።")
    
    users = await get_all_users()
    status_msg = await message.answer(f"⏳ ለ {len(users)} ተጠቃሚዎች በመላክ ላይ...")
    
    count = 0
    for user_id in users:
        try:
            await bot.send_message(user_id, f"📢 <b>መልዕክት ከሙሽሮቹ፡</b>\n\n{message.text}")
            count += 1
            await asyncio.sleep(0.05)
        except: continue
    
    await status_msg.delete()
    await message.answer(f"✅ መልዕክቱ ለ {count} ተጠቃሚዎች በተሳካ ሁኔታ ተልኳል!")
    await state.clear()

# ==========================================
#              SERVER & STARTUP
# ==========================================

async def handle_ping(r): return web.Response(text="Alive")
async def start_web_server():
    app = web.Application(); app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080))).start()

async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server(); await bot.delete_webhook(drop_pending_updates=True); await dp.start_polling(bot)

if __name__ == "__main__":
    try: asyncio.run(main())
    except: pass