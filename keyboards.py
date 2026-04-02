from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📅 ፕሮግራም", callback_data="btn_program"), 
                InlineKeyboardButton(text="📍 ካርታ (Location)", callback_data="btn_location"))
    builder.row(InlineKeyboardButton(text="📸 ፎቶዎች", callback_data="btn_photos"), 
                InlineKeyboardButton(text="⏳ ስንት ቀን ቀረው?", callback_data="btn_countdown"))
    builder.row(InlineKeyboardButton(text="📝 መልካም ምኞት", callback_data="btn_wish"), 
                InlineKeyboardButton(text="🔔 ማስታወሻ (Remind me)", callback_data="btn_remind"))
    return builder.as_markup()

def get_back_button():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 ወደ ዋናው ማውጫ", callback_data="btn_start"))
    return builder.as_markup()