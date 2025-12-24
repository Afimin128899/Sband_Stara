from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.flyer_api import get_tasks
from keyboards.main_menu import main_menu

async def tasks_handler(call: types.CallbackQuery, api_key: str):
    tasks = get_tasks(call.from_user.id, api_key)

    if not tasks:
        await call.message.answer("❌ Заданий нет", reply_markup=main_menu())
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    text = "📋 Доступные задания:\n\n"

    for t in tasks:
        text += f"🔹 {t.get('title','Задание')}\n💰 0.25 ⭐\n\n"
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="▶️ Перейти", url=t.get("url", "#"))
        ])

    kb.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    ])

    await call.message.answer(text, reply_markup=kb)
    
