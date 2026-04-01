from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu():
    """Returns a beautiful, compact Inline Keyboard (Attached to message)."""
    builder = InlineKeyboardBuilder()

    # Row 1: Essential Info
    builder.row(
        InlineKeyboardButton(text="📅 ፕሮግራም", callback_data="btn_program"),
        InlineKeyboardButton(text="📍 ካርታ (Location)", callback_data="btn_location")
    )
    
    # Row 2: Visuals & Countdown
    builder.row(
        InlineKeyboardButton(text="📸 ፎቶዎች", callback_data="btn_photos"),
        InlineKeyboardButton(text="⏳ ስንት ቀን ቀረው?", callback_data="btn_countdown")
    )
    
    # Row 3: Engagement
    builder.row(
        InlineKeyboardButton(text="📝 መልካም ምኞት", callback_data="btn_wish"),
        InlineKeyboardButton(text="📖 ጥቅስ", callback_data="btn_bible")
    )
    
    # Row 4: Reminder
    builder.row(
        InlineKeyboardButton(text="🔔 ማስታወሻ (Remind me)", callback_data="btn_remind")
    )

    return builder.as_markup()