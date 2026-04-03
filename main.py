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
from database import init_db, add_user, toggle_reminder, save_wish, get_all_users, get_all_wishes, count_users

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Safely convert ADMIN_ID to integer
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

SECONDARY_ADMIN_ID = int(os.getenv("SECONDARY_ADMIN_ID", 0))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Fast cache for images
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
        msg = await bot.send_photo(
            chat_id, 
            FSInputFile(photo_path), 
            caption=caption, 
            reply_markup=reply_markup, 
            request_timeout=120
        )
        FILE_CACHE[photo_path] = msg.photo[-1].file_id
    else:
        await bot.send_message(chat_id, caption, reply_markup=reply_markup)

# ==========================================
#           COMMAND HANDLERS
# ==========================================
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Save User to DB
    await add_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
    
    # --- NOTIFICATION LOGIC ---
    # We notify both admins if the user is NOT one of the admins
    if message.from_user.id not in [ADMIN_ID, SECONDARY_ADMIN_ID]:
        user_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
        notify_text = f"🆕 <b>አዲስ ተጠቃሚ ቦቱን ጀምሯል!</b>\n👤 <b>ስም:</b> {user_link}"
        
        # 1. Notify Primary Admin (You)
        try:
            await bot.forward_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
            await bot.send_message(ADMIN_ID, notify_text)
        except: pass

        # 2. Notify Secondary Admin (Other person)
        try:
            # We don't necessarily need to forward the profile twice, 
            # just sending the text notification is enough and cleaner
            await bot.send_message(SECONDARY_ADMIN_ID, notify_text)
        except: pass
    # ---------------------------

    welcome_text = (
        'ዓለም ከመፈጠሩ አስቀድሞ ከጊዜ ቀመር ግምጃ ቤት አንደኛው ዶሴ ተገለጠ። በውስጡ የብራና ፅሁፍ ተገልጦ አንዲህ ተነበበ።\n\n'
        '"እነሆ ፍቅርሥላሴ ኃይሌ ከጎን አጥንቱ ማህሌት ፈለቀ ተገኝታለችና ሚስት ትሁነው፤ እርሱም ባል ይሁናት!" በቤተሰብ በወዳጅ ዘመዶቹ ዘንድም ታላቅ ደስታ ሆነ። አሁን ጊዜው ደረሰና ፈቃዱ ሊፈጸም ከደጅ ነው።\n\n'
        '"ይህች ከእግዚአብሔር ዘንድ ሆነች፣ ለአይናችንም ድንቅ ናት።" መዝ 118፣23\n\n'
        'ክቡራን ወዳጆቼ ፣ እናንተም የእግዚአብሔር ህዝቦች እና ሌሎችም ምስክሮች ባሉበት የቃል ኪዳን ስርዓት ስላለን እንዲገኙ ከሚነበብ ፊርማ ጋር በጌታ ፍቅር ጋብዞኖዎታል።\n\n'
        'ለተሻለ ማብራርያ ቀጣይ ምርጫ ይንኩ!'
    )
    
    await send_wedding_photo(message.chat.id, "assets/welcome.jpg", welcome_text, get_main_menu())


@dp.message(Command("developer", "development"))
async def cmd_developer(message: types.Message):
    dev_text = (
        "👨‍💻 <b>ስለ Bot ሰሪዉ (Developer)</b>\n\n"
        "ለራስዎ ወይም ለወዳጅዎ ሰርግ ተመሳሳይ ቦት ማሰራት ከፈለጉ:\n"
        "📞 <b>ስልክ:</b> +251996246990\n"
        "💬 <b>ቴሌግራም:</b> @jonas_wjohn\n"
    )
    await send_wedding_photo(message.chat.id, "assets/developer.jpg", dev_text, get_back_button())

@dp.message(Command("users"))
async def cmd_users_count(message: types.Message):
    """Shows the total number of users who have started the bot."""
    count = await count_users()
    # We use a professional looking message
    await message.answer(f"📊 <b>የቦቱ ተጠቃሚዎች ጠቅላላ ብዛት:</b> {count}")


@dp.message(Command("export"))
async def cmd_export(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    wishes = await get_all_wishes()
    if not wishes: return await message.answer("❌ ምንም መልዕክት የለም።")
    
    report = f"💍 የሰርግ መልዕክቶች ሪፖርት\n" + "="*25 + "\n\n"
    for i, (name, wish, time) in enumerate(wishes, 1):
        report += f"{i}. ከ: {name}\n   መልዕክት: {wish}\n" + "-"*15 + "\n"

    file_data = BufferedInputFile(report.encode('utf-8'), filename="wishes.txt")
    await message.answer_document(file_data, caption="✅ የመልካም ምኞት ሪፖርት")

# ==========================================
#           INLINE BUTTON HANDLERS
# ==========================================

@dp.callback_query(F.data == "btn_start")
async def back_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    """Refined 'Back' logic: Deletes clutter and sends a SIMPLE menu."""
    await callback.answer()
    await state.clear()
    
    # 1. Delete the previous response message to keep the chat clean
    try:
        await callback.message.delete()
    except: pass
    
    # 2. Send a simple, clean main menu without re-sending the long poem/photo
    await callback.message.answer(
        "<b>ዋናው ማውጫ</b>\nእባክዎ የሚፈልጉትን መረጃ ይምረጡ፡ 👇", 
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "btn_program")
async def handle_prog(callback: CallbackQuery):
    await callback.answer("በማዘጋጀት ላይ...")
    text = (
        "📅 <b>የፕሮግራም ዝርዝር</b>\n\n"
        "📍 <b>የቃልኪዳን ስነ-ስርዓት፡</b>\nበሐዋሳ ፌዝ አርሜ ቤተክርስቲያን\n⏰ 4:30\n\n"
        "📍 <b>የምሳ እና የኬክ ፕሮግራም፡</b>\nበጆሹዋ ኮምፔይን ኢትዮጲያ ሐዋሳ ሚኒስትሪ\n⏰ 7:00"
    )
    await send_wedding_photo(callback.message.chat.id, "assets/program.jpg", text, get_back_button())

@dp.callback_query(F.data == "btn_location")
async def handle_loc(callback: CallbackQuery):
    await callback.answer("ካርታዎችን በማዘጋጀት ላይ...")
    
    # Church Location
    text1 = (
        "📍 <b>Joshua Campaign Ethiopia Hawasa Office</b>\n\n"
        "🔗 https://maps.app.goo.gl/uxk5y3mUR8mpkoFK7?g_st=atm"
    )
    await send_wedding_photo(callback.message.chat.id, "assets/map_church.jpg", text1)
    
    await asyncio.sleep(0.5)
    
    # Hotel Location
    text2 = (
        "📍 <b>Faith Army Church Hawassa</b>\n\n"
        "🔗 https://maps.app.goo.gl/MxCg4Q5V5LndDAnD9?g_st=atm"
    )
    await send_wedding_photo(callback.message.chat.id, "assets/map_hotel.jpg", text2, get_back_button())

@dp.callback_query(F.data == "btn_countdown")
async def handle_countdown(callback: CallbackQuery):
    await callback.answer()
    days = (datetime(2026, 5, 29) - datetime.now()).days
    text = f"⏳ <b>ስንት ቀን ቀረው?</b>\n\nየሰርጋችን ቀን <b>{max(0, days)} ቀናት</b> ቀርተዋል! 🎉"
    await send_wedding_photo(callback.message.chat.id, "assets/countdown.jpg", text, get_back_button())

@dp.callback_query(F.data == "btn_remind")
async def handle_remind(callback: CallbackQuery):
    await callback.answer()
    await toggle_reminder(callback.from_user.id, 1)
    await callback.message.answer("✅ <b>የማስታወሻ ደወል በርቷል!🙏</b>", reply_markup=get_back_button())

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
        await asyncio.sleep(0.6)
    
    await callback.message.answer("👆👆👆", reply_markup=get_back_button())

@dp.callback_query(F.data == "btn_wish")
async def ask_for_wish(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("✨ <b>የመልካም ምኞት መግለጫ</b>\n\nለሙሽሮቹ መልዕክት ይፃፉልን።")
    await state.set_state(WeddingStates.waiting_for_wish)

@dp.message(WeddingStates.waiting_for_wish)
async def process_wish(message: types.Message, state: FSMContext):
    await save_wish(message.from_user.id, message.from_user.first_name, message.text)
    
    # Notify admin
    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await bot.send_message(ADMIN_ID, f"✅ <b>አዲስ መልዕክት ደርሷል!</b>\n👤 ከ: {message.from_user.first_name}")
    
    await message.answer("🙏 መልዕክትዎ ደርሷል! እናመሰግናለን።", reply_markup=get_back_button())
    await state.clear()

@dp.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📣 መልዕክቱን ይፃፉ (ወይም 'cancel')")
        await state.set_state(WeddingStates.waiting_for_broadcast)

@dp.message(WeddingStates.waiting_for_broadcast)
async def perform_broadcast(message: types.Message, state: FSMContext):
    if message.text.lower() == 'cancel': 
        await state.clear()
        return await message.answer("❌ ተሰርዟል", reply_markup=get_back_button())
    
    users = await get_all_users()
    for uid in users:
        try: 
            await bot.send_message(uid, f"📢 <b>መልዕክት፡</b>\n\n{message.text}")
            await asyncio.sleep(0.05)
        except: continue
    await message.answer("✅ ተልኳል!", reply_markup=get_back_button())
    await state.clear()

# ==========================================
#              SERVER & STARTUP
# ==========================================

async def handle_ping(r): return web.Response(text="Alive")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass