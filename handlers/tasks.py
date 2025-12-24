from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.flyer_api import get_flyer_tasks

async def tasks_handler(call, api_key: str):
    user_id = call.from_user.id
    # language_code можно брать из call.from_user.language_code или жестко задавать
    tasks = await get_flyer_tasks(user_id, api_key, language_code="ru")

    if not tasks:
        await call.message.answer("❌ Нет доступных заданий")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    text = "📋 Доступные задания:\n\n"

    for t in tasks:
        sig = t.get("signature") or t.get("id") or t.get("task_id")
        title = t.get("title", "Задание")
        # текст задания
        text += f"🔹 {title}\n💰 Награда: 0.25 ⭐\n\n"

        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text="▶️ Открыть",
                callback_data=f"task_open:{sig}"
            )
        ])

    kb.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    ])

    await call.message.answer(text, reply_markup=kb)
    
