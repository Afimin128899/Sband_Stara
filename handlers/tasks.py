from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.users import get_user
from utils.subgram_api import get_sponsors

async def tasks_handler(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    sponsors = get_sponsors(call.from_user.id)
    if not sponsors:
        await call.message.answer("Нет доступных заданий сейчас.")
        return

    keyboard = InlineKeyboardMarkup()
    msg_text = ""
    for s in sponsors:
        msg_text += f"Название: {s.get('name', 'Задание')}\nОписание: {s.get('description', '')}\n💎 0.25 звезды\n\n"
        keyboard.add(InlineKeyboardButton(s.get("button_text", "Перейти"), url=s.get("link")))
    
    keyboard.add(InlineKeyboardButton("✅ Я выполнил", callback_data="done_task"))
    await call.message.answer(msg_text, reply_markup=keyboard)

async def done_task_handler(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["stars"] += 0.25
    await call.answer("🎉 Ты получил 0.25 звезды!")
