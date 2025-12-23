from aiogram import types
from config import ADMIN_ID
from utils.users import get_user
from utils.storage import withdraws


async def admin_give_stars(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, uid, amount, *reason = message.text.split()
        uid = int(uid)
        amount = float(amount)
        reason = " ".join(reason)
    except:
        await message.answer("❌ /give user_id amount причина")
        return

    user = get_user(uid)
    user["stars"] += amount

    await message.answer(
        f"✅ Выдано {amount} ⭐\n👤 {uid}\n📝 {reason}"
    )


async def withdraw_ok(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    wid = call.data.split(":")[1]
    withdraws[wid]["status"] = "done"
    await call.message.answer("✅ Вывод выполнен")


async def withdraw_decline(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    wid = call.data.split(":")[1]
    withdraws[wid]["status"] = "declined"
    await call.message.answer("❌ Вывод отклонён. Причина?")
  
