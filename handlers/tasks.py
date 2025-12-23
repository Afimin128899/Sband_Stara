from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.flyer_api import get_tasks
from keyboards.main_menu import main_menu


async def tasks_handler(call: types.CallbackQuery):
    tasks = get_tasks(call.from_user.id)

    if not tasks:
        await call.message.answer(
            "❌ Заданий нет",
            reply_markup=main_menu()
        )
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[])

    text = "📋 Задания:\n\n"
    for task in tasks:
        text += f"🔹 {task.get('title', 'Задание')}\n💰 0.25 ⭐\n\n"
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                "▶️ Перейти",
                url=task.get("url")
            )
        ])

    kb.inline_keyboard.append([
        InlineKeyboardButton("🔙 Назад", callback_data="back_main")
    ])

    await call.message.answer(text, reply_markup=kb)
    
