from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu():
    """Main Menu with 2-column layout and Coordinators at the bottom."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📅 ፕሮግራም", callback_data="btn_program"))
    builder.add(InlineKeyboardButton(text="📍 ካርታ (Location)", callback_data="btn_location"))
    builder.add(InlineKeyboardButton(text="📸 ፎቶዎች", callback_data="btn_photos"))
    builder.add(InlineKeyboardButton(text="⏳ ስንት ቀን ቀረው?", callback_data="btn_countdown"))
    builder.add(InlineKeyboardButton(text="📝 መልካም ምኞት", callback_data="btn_wish"))
    builder.add(InlineKeyboardButton(text="🔔 ማስታወሻ (Remind me)", callback_data="btn_remind"))
    
    # NEW BUTTON: Row 4 (Full Width)
    builder.row(InlineKeyboardButton(text="📞 አስተባባሪዎች", callback_data="btn_coordinators"))

    builder.adjust(2, 2, 2, 1) # This makes 3 rows of 2, and 1 row of 1
    return builder.as_markup()

def get_back_button():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 ወደ ዋናው ማውጫ", callback_data="btn_start"))
    return builder.as_markup()