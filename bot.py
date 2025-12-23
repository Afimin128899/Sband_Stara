import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from keyboards.main_menu import main_menu
from handlers import profile, tasks, referrals
from utils.users import get_user

API_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# =========================
# /start
# =========================
@dp.message(CommandStart())
async def start(message: types.Message):
    get_user(message.from_user.id)

    if message.text and len(message.text.split()) > 1:
        try:
            ref_id = int(message.text.split()[1])
            referrals.handle_referral(message.from_user.id, ref_id)
        except:
            pass

    await message.answer(
        "Добро пожаловать в ⭐ Sband_Stars!",
        reply_markup=main_menu()
    )

# =========================
# Callback кнопки
# =========================
@dp.callback_query(F.data == "profile")
async def profile_cb(call: types.CallbackQuery):
    await profile.profile_handler(call)

@dp.callback_query(F.data == "tasks")
async def tasks_cb(call: types.CallbackQuery):
    await tasks.tasks_handler(call)

@dp.callback_query(F.data == "done_task")
async def done_task_cb(call: types.CallbackQuery):
    await tasks.done_task_handler(call)

@dp.callback_query(F.data.startswith("exchange_"))
async def exchange_cb(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    amount = int(call.data.split("_")[1])

    if user["stars"] >= amount:
        user["stars"] -= amount
        await call.message.answer(f"✅ Вы обменяли {amount} ⭐")
    else:
        await call.message.answer("❌ Недостаточно звёзд")

# =========================
# Запуск
# =========================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
