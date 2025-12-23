from aiogram import types
from utils.users import get_user

async def profile_handler(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.answer(
        f"💎 Ваши звёзды: {user['stars']}\n"
        f"👥 Приглашено: {user['referrals']}\n"
        f"💰 Заработано на реферальных ссылках: {user['ref_earnings']}\n"
        f"Ваша реферальная ссылка: {user['ref_link']}"
    )
