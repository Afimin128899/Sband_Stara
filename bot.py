from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from keyboards.main_menu import main_menu
from handlers import profile, tasks, referrals
from utils.users import get_user

API_TOKEN = "8389664932:AAHw-vE5o52ODbQgUPcHf5CsSlhAIls_vDE"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# =========================
# Старт бота
# =========================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user = get_user(message.from_user.id)
    
    # Обработка реферала
    if message.get_args():
        try:
            ref_id = int(message.get_args())
            referrals.handle_referral(message.from_user.id, ref_id)
        except ValueError:
            pass

    await message.answer(
        "Добро пожаловать! Ваше главное меню:",
        reply_markup=main_menu()
    )

# =========================
# Обработка кнопок
# =========================
@dp.callback_query_handler(lambda c: True)
async def callback_handler(call: types.CallbackQuery):
    if call.data == "profile":
        await profile.profile_handler(call)
    elif call.data == "tasks":
        await tasks.tasks_handler(call)
    elif call.data == "done_task":
        await tasks.done_task_handler(call)
    elif call.data.startswith("exchange_"):
        user = get_user(call.from_user.id)
        stars_needed = int(call.data.split("_")[1])
        if user["stars"] >= stars_needed:
            user["stars"] -= stars_needed
            await call.message.answer(f"Вы обменяли {stars_needed} звёзд!")
        else:
            await call.message.answer("У вас недостаточно звёзд.")

# =========================
# Запуск бота
# =========================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
