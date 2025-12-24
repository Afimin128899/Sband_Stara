from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def withdraw_menu_handler(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="15 ⭐", callback_data="withdraw_15")],
        [InlineKeyboardButton(text="25 ⭐", callback_data="withdraw_25")],
        [InlineKeyboardButton(text="50 ⭐", callback_data="withdraw_50")],
        [InlineKeyboardButton(text="100 ⭐", callback_data="withdraw_100")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])
    await call.message.answer("💸 Выберите сумму для вывода:", reply_markup=kb)

async def withdraw_request(call, amount, bot, admin_id):
    await call.message.answer(
        f"⏳ Заявка на вывод {amount} ⭐ отправлена администратору"
    )

    await bot.send_message(
        admin_id,
        f"📤 Запрос на вывод\n"
        f"👤 ID: {call.from_user.id}\n"
        f"💰 Сумма: {amount} ⭐"
    )
    
