from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def admin_give_stars(message: types.Message, admin_id: int):
    """
    Команда администратора:
    /give USER_ID AMOUNT ПРИЧИНА
    """
    if message.from_user.id != admin_id:
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        await message.answer("❌ Использование: /give USER_ID AMOUNT [причина]")
        return

    user_id = int(parts[1])
    amount = int(parts[2])
    reason = parts[3] if len(parts) > 3 else "Без причины"

    # Тут ты позже подключишь БД и начисление
    await message.answer(
        f"✅ Выдано {amount} ⭐ пользователю {user_id}\n"
        f"📄 Причина: {reason}"
    )


async def withdraw_ok(call: types.CallbackQuery):
    """
    Подтверждение вывода
    """
    await call.message.edit_text("✅ Вывод выполнен")


async def withdraw_decline(call: types.CallbackQuery):
    """
    Отклонение вывода
    """
    await call.message.edit_text("❌ Вывод отклонён")
    
