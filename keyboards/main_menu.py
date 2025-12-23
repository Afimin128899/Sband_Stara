from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Профиль", callback_data="profile"),
        InlineKeyboardButton("Задания", callback_data="tasks"),
        InlineKeyboardButton("Тех. поддержка", url="https://t.me/ShardenFoot")
    )
    markup.add(
        InlineKeyboardButton("15 звёзд", callback_data="exchange_15"),
        InlineKeyboardButton("25 звёзд", callback_data="exchange_25"),
        InlineKeyboardButton("50 звёзд", callback_data="exchange_50"),
        InlineKeyboardButton("100 звёзд", callback_data="exchange_100")
    )
    return markup
