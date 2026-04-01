from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    """Returns the main Reply Keyboard Menu in a professional 2-column grid."""
    
    keyboard = [
        # Row 1: Essential Info
        [KeyboardButton(text="📅 ፕሮግራም እና ቦታ"), KeyboardButton(text="📍 ካርታ (Location)")],
        
        # Row 2: Visuals & Aesthetics
        [KeyboardButton(text="📸 የቅድመ-ጋብቻ ፎቶዎች"), KeyboardButton(text="👗 የአለባበስ ዘይቤ")],
        
        # Row 3: Engagement
        [KeyboardButton(text="⏳ ስንት ቀን ቀረው?"), KeyboardButton(text="📝 የመልካም ምኞት መግለጫ")],
        
        # Row 4: Extras
        [KeyboardButton(text="📖 የመጽሐፍ ቅዱስ ጥቅስ"), KeyboardButton(text="🔔 ማስታወሻ (Remind me)")]
    ]
    
    # resize_keyboard=True makes it fit nicely at the bottom of the screen
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)