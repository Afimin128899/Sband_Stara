from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Профиль",
                    callback_data="profile"
                ),
                InlineKeyboardButton(
                    text="📋 Задания",
                    callback_data="tasks"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🛠 Тех. поддержка",
                    url="https://t.me/ShardenFoot"
                )
            ],
            [
                InlineKeyboardButton(
                    text="15 ⭐",
                    callback_data="exchange_15"
                ),
                InlineKeyboardButton(
                    text="25 ⭐",
                    callback_data="exchange_25"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="50 ⭐",
                    callback_data="exchange_50"
                ),
                InlineKeyboardButton(
                    text="100 ⭐",
                    callback_data="exchange_100"
                ),
            ],
        ]
    )
    
