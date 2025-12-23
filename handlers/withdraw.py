from aiogram import types
from utils.users import get_user
from utils.storage import withdraws
from keyboards.withdraw_menu import withdraw_menu
from keyboards.main_menu import main_menu
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
import uuid


async def withdraw_menu_handler(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.answer(
        f"💸 Вывод\n⭐ Баланс: {user['stars']}",
        reply_markup=withdraw_menu()
    )


async def withdraw_request(call: types.CallbackQuery, amount: int, bot):
    user = get_user(call.from_user.id)

    if user["stars"] < amount:
        await call.answer("❌ Недостаточно ⭐", show_alert=True)
        return

    wid = str(uuid.uuid4())[:8]
    user["stars"] -= amount

    withdraws[wid] = {
        "user_id": call.from_user.id,
        "amount": amount,
        "status": "pending"
    }

    admin_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    "✅ Выполнено",
                    callback_data=f"withdraw_ok:{wid}"
                ),
                InlineKeyboardButton(
                    "❌ Отклонить",
                    callback_data=f"withdraw_decline:{wid}"
                ),
            ]
        ]
    )

    await bot.send_message(
        ADMIN_ID,
        f"📥 Новый вывод\nID: {wid}\nUser: {call.from_user.id}\n⭐ {amount}",
        reply_markup=admin_kb
    )

    await call.message.answer(
        "⏳ Запрос отправлен",
        reply_markup=main_menu()
    )
  
