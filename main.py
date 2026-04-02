import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from aiohttp import web

# Custom Imports
from keyboards import get_main_menu, get_back_button
from database import init_db, add_user, toggle_reminder, save_wish, get_all_users, get_all_wishes

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5873042615

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

FILE_CACHE = {}

class WeddingStates(StatesGroup):
    waiting_for_wish = State()
    waiting_for_broadcast = State()

# ==========================================
#           IMAGE SENDING HELPER
# ==========================================

async def send_wedding_photo(chat_id, photo_path, caption, reply_markup=None):
    if photo_path in FILE_CACHE:
        await bot.send_photo(chat_id, FILE_CACHE[photo_path], caption=caption, reply_markup=reply_markup)
    elif os.path.exists(photo_path):
        msg = await bot.send_photo(chat_id, FSInputFile(photo_path), caption=caption, reply_markup=reply_markup, request_timeout=120)
        FILE_CACHE[photo_path] = msg.photo[-1].file_id
    else:
        await bot.send_message(chat_id, caption, reply_markup=reply_markup)

# ==========================================
#           COMMAND HANDLERS
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await add_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
    welcome_text = (
        "📖 <b>ምሳሌ 18:22</b>\n<i>«ሚስት የሚያገኝ መልካም ነገርን ያገኛል፤...»</i>\n\n"
        "እንኳን ወደ <b>[ሙሽራ] እና [ሙሽሪት]</b> የሰርግ መረጃ መስጫ ቦት በሰላም መጡ! 😊 💍\n\n"
        "እባክዎ ከታች ያሉትን ቁልፎች በመጫን ዝርዝር መረጃዎችን ያግኙ። 👇"
    )
    await send_wedding_photo(message.chat.id, "assets/welcome.jpg", welcome_text, get_main_menu())

@dp.message(Command("developer", "development"))
@dp.message(Command("developer", "development"))
async def cmd_developer(message: types.Message):
    """Professional developer info command with a photo."""
    dev_text = (
        "👨‍💻 <b>ስለ ሲስተም አልሚው (Developer)</b>\n\n"
        "ይህ የሰርግ ቦት ሲስተም የተገነባው በጥራት እና በዘመናዊ ቴክኖሎጂ ነው።\n\n"
        "ለራስዎ ወይም ለወዳጅዎ ሰርግ ተመሳሳይ ቦት ማሰራት ከፈለጉ:\n"
        "📞 <b>ስልክ:</b> +2519........\n"
        "💬 <b>ቴሌግራም:</b> @YourUsername\n"
    )
    # This uses the same fast helper function as the other buttons
    await send_wedding_photo(message.chat.id, "assets/developer.jpg", dev_text, get_back_button())

@dp.message(Command("export"))
async def cmd_export(message: types.Message):
    """Generates a readable text report of all wishes."""
    if message.from_user.id != ADMIN_ID: return
    
    wishes = await get_all_wishes()
    if not wishes:
        return await message.answer("❌ እስካሁን ምንም የመልካም ምኞት መልዕክት አልተመዘገበም።")
    
    # Create the report content
    report_content = f"💍 የሰርግ የመልካም ምኞት መግለጫዎች ሪፖርት\nቀን: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report_content += "="*40 + "\n\n"
    
    for i, (name, wish, time) in enumerate(wishes, 1):
        report_content += f"{i}. ከ: {name} ({time})\n"
        report_content += f"   መልዕክት: {wish}\n"
        report_content += "-"*20 + "\n"

    # Send as a downloadable text file
    file_data = BufferedInputFile(report_content.encode('utf-8'), filename="wedding_wishes_report.txt")
    await message.answer_document(file_data, caption="✅ የመልካም ምኞት መግለጫዎች ሪፖርት (Text File)")

# ==========================================
#           INLINE BUTTON HANDLERS
# ==========================================

@dp.callback_query(F.data == "btn_start")
async def back_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    try: await callback.message.delete()
    except: pass
    await cmd_start(callback.message, state)

@dp.callback_query(F.data == "btn_program")
async def handle_prog(callback: CallbackQuery):
    await callback.answer("ፕሮግራሙን በማዘጋጀት ላይ...")
    text = ("📅 <b>የፕሮግራም ዝርዝር</b>\n\n📍 ስርዓተ ተክሊል፡ [ቦታ]\n⏰ 4:30\n\n📍 የምሳ ግብዣ፡ [ቦታ]\n⏰ 7:00")
    await send_wedding_photo(callback.message.chat.id, "assets/program.jpg", text, get_back_button())

@dp.callback_query(F.data == "btn_location")
async def handle_loc(callback: CallbackQuery):
    await callback.answer("ካርታውን በማዘጋጀት ላይ...")
    text = ("📍 <b>የአዳራሹ መገኛ</b>\n\n🔗 https://maps.google.com/...")
    await send_wedding_photo(callback.message.chat.id, "assets/map.jpg", text, get_back_button())

@dp.callback_query(F.data == "btn_countdown")
async def handle_countdown(callback: CallbackQuery):
    await callback.answer()
    days = (datetime(2025, 9, 29) - datetime.now()).days
    text = f"⏳ <b>ስንት ቀን ቀረው?</b>\n\nለታላቁ የሰርጋችን ቀን <b>{max(0, days)} ቀናት</b> ቀርተዋል! 🎉"
    await send_wedding_photo(callback.message.chat.id, "assets/countdown.jpg", text, get_back_button())

@dp.callback_query(F.data == "btn_remind")
async def handle_remind(callback: CallbackQuery):
    await callback.answer()
    await toggle_reminder(callback.from_user.id, 1)
    await callback.message.answer("✅ <b>የማስታወሻ ደወል በርቷል!</b>", reply_markup=get_back_button())

@dp.callback_query(F.data == "btn_photos")
async def handle_photos(callback: CallbackQuery):
    await callback.answer()
    gallery_path = "assets/gallery/"
    if not os.path.exists(gallery_path): 
        return await callback.message.answer("📸 በቅርቡ ይጫናሉ!", reply_markup=get_back_button())
    
    anim_msg = await callback.message.answer("⏳ ፎቶዎችን በማዘጋጀት ላይ...")
    for i in ["3...", "2...", "1...", "🚀"]:
        await asyncio.sleep(0.4)
        try: await anim_msg.edit_text(f"📸 <b>ፎቶዎችን በማዘጋጀት ላይ...</b>\n\n{i}")
        except: pass
    
    await anim_msg.delete()
    photos = sorted([f for f in os.listdir(gallery_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    for p in photos:
        await callback.message.answer_photo(FSInputFile(os.path.join(gallery_path, p)), request_timeout=60)
        await asyncio.sleep(0.5)
    
    await callback.message.answer("👆 ማዕከለ-ስዕላቱ ተጠናቋል።", reply_markup=get_back_button())

@dp.callback_query(F.data == "btn_wish")
async def ask_for_wish(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("✨ <b>የመልካም ምኞት መግለጫ</b>\n\nለሙሽሮቹ መልዕክት ይፃፉልን።")
    await state.set_state(WeddingStates.waiting_for_wish)

@dp.message(WeddingStates.waiting_for_wish)
async def process_wish(message: types.Message, state: FSMContext):
    await save_wish(message.from_user.id, message.from_user.first_name, message.text)
    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await bot.send_message(ADMIN_ID, f"✅ <b>አዲስ መልዕክት!</b>\n👤 ከ: <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>")
    await message.answer("🙏 መልዕክትዎ ደርሷል! እናመሰግናለን።", reply_markup=get_back_button())
    await state.clear()

@dp.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📣 ለመላክ የሚፈልጉትን መልዕክት ይፃፉ (ወይም 'cancel')")
        await state.set_state(WeddingStates.waiting_for_broadcast)

@dp.message(WeddingStates.waiting_for_broadcast)
async def perform_broadcast(message: types.Message, state: FSMContext):
    if message.text.lower() == 'cancel': await state.clear(); return await message.answer("❌ ተሰርዟል", reply_markup=get_back_button())
    users = await get_all_users()
    for uid in users:
        try: await bot.send_message(uid, f"📢 <b>መልዕክት፡</b>\n\n{message.text}"); await asyncio.sleep(0.05)
        except: continue
    await message.answer("✅ ተልኳል!", reply_markup=get_back_button())
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
    await init_db()
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try: asyncio.run(main())
    except: pass