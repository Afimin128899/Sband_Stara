from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def profile_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Профиль", callback_data="show_profile"),
                InlineKeyboardButton(text="👥 Реферальная система", callback_data="referrals"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
            ]
        ]
    )
  
