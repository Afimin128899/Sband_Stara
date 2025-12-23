from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Профиль", callback_data="show_profile"),
                InlineKeyboardButton(text="📋 Задания", callback_data="tasks"),
            ],
            [
                InlineKeyboardButton(text="💸 Вывод", callback_data="withdraw_menu"),
            ],
            [
                InlineKeyboardButton(text="🛠 Поддержка", url="https://t.me/ShardenFoot")
            ]
        ]
    )
    
