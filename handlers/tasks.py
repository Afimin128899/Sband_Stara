from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.flyer_api import get_tasks

async def tasks_handler(call, api_key):
    tasks = get_tasks(call.from_user.id, api_key)

    if not tasks:
        await call.message.answer("❌ Заданий нет")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    text = "📋 Задания:\n\n"

    for t in tasks:
        text += f"🔹 {t['title']}\n💰 0.25 ⭐\n\n"
        kb.inline_keyboard.append(
            [InlineKeyboardButton(text="▶️ Перейти", url=t["url"])]
        )

    await call.message.answer(text, reply_markup=kb)
    
