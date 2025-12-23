from aiogram import types
from utils.users import get_user
from keyboards.main_menu import main_menu

async def show_profile(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    text = (
        f"👤 Ваш профиль\n\n"
        f"⭐ Баланс: {user['stars']}\n"
        f"📤 Выведено: {user['withdrawn']}\n"
        f"👥 Приглашено людей: {user['referrals']}"
    )
    await call.message.answer(text, reply_markup=main_menu())

async def referral_system(call: types.CallbackQuery):
    text = (
        f"👥 Ваша реферальная система\n\n"
        f"Отправьте ссылку друзьям:\n"
        f"https://t.me/ВАШ_БОТ?start={call.from_user.id}\n\n"
        f"Каждый приглашённый даёт +2 ⭐"
    )
    await call.message.answer(text, reply_markup=main_menu())
  
