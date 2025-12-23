from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("📋 Задания", callback_data="tasks"),
                InlineKeyboardButton("💸 Вывод", callback_data="withdraw_menu"),
            ],
            [
                InlineKeyboardButton(
                    "🛠 Поддержка",
                    url="https://t.me/ShardenFoot"
                )
            ]
        ]
    )
    
