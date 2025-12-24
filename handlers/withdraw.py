from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def withdraw_menu_handler(call):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="15 ⭐", callback_data="withdraw_15")],
        [InlineKeyboardButton(text="25 ⭐", callback_data="withdraw_25")],
        [InlineKeyboardButton(text="50 ⭐", callback_data="withdraw_50")],
        [InlineKeyboardButton(text="100 ⭐", callback_data="withdraw_100")]
    ])
    await call.message.answer("💸 Выберите сумму:", reply_markup=kb)

async def withdraw_request(call, amount, bot, admin_id):
    await call.message.answer("⏳ Заявка отправлена")

    await bot.send_message(
        admin_id,
        f"📤 Запрос вывода\n👤 {call.from_user.id}\n💰 {amount} ⭐"
    )
    
