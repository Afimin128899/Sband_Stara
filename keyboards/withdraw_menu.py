from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def withdraw_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("15 ⭐", callback_data="withdraw_15"),
                InlineKeyboardButton("25 ⭐", callback_data="withdraw_25"),
            ],
            [
                InlineKeyboardButton("50 ⭐", callback_data="withdraw_50"),
                InlineKeyboardButton("100 ⭐", callback_data="withdraw_100"),
            ],
            [
                InlineKeyboardButton("🔙 Назад", callback_data="back_main"),
            ],
        ]
    )
  
