import asyncio
from aiogram import Bot, Dispatcher, F
from keyboards.main_menu import main_menu
from keyboards.profile_menu import profile_menu
from handlers import tasks, withdraw, admin, profile
from utils.users import add_referral, get_user

from config import BOT_TOKEN

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text.startswith("/start"))
async def start(message):
    args = message.get_args()
    user = get_user(message.from_user.id)

    if args:
        try:
            ref_id = int(args)
            if ref_id != message.from_user.id:
                add_referral(ref_id)
        except:
            pass

    await message.answer("👋 Добро пожаловать в Sband Stars", reply_markup=profile_menu())

# Профиль и рефералы
@dp.callback_query(F.data == "show_profile")
async def profile_cb(call):
    await profile.show_profile(call)

@dp.callback_query(F.data == "referrals")
async def referrals_cb(call):
    await profile.referral_system(call)

# Задания
@dp.callback_query(F.data == "tasks")
async def tasks_cb(call):
    await tasks.tasks_handler(call)

# Вывод
@dp.callback_query(F.data == "withdraw_menu")
async def withdraw_menu_cb(call):
    await withdraw.withdraw_menu_handler(call)

@dp.callback_query(F.data.startswith("withdraw_"))
async def withdraw_cb(call):
    amount = int(call.data.split("_")[1])
    await withdraw.withdraw_request(call, amount, bot)

# Админ
@dp.message(F.text.startswith("/give"))
async def give(message):
    await admin.admin_give_stars(message)

@dp.callback_query(F.data.startswith("withdraw_ok"))
async def withdraw_ok_cb(call):
    await admin.withdraw_ok(call)

@dp.callback_query(F.data.startswith("withdraw_decline"))
async def withdraw_decline_cb(call):
    await admin.withdraw_decline(call)

# Назад
@dp.callback_query(F.data == "back_main")
async def back_main_cb(call):
    await call.message.answer("🏠 Главное меню", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
