import asyncio
from aiogram import Bot, Dispatcher, F, types
from config import BOT_TOKEN
from keyboards.main_menu import main_menu
from handlers import tasks, withdraw, admin

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в Sband Stars",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "tasks")
async def t(call):
    await tasks.tasks_handler(call)


@dp.callback_query(F.data == "withdraw_menu")
async def wm(call):
    await withdraw.withdraw_menu_handler(call)


@dp.callback_query(F.data.startswith("withdraw_"))
async def w(call):
    amount = int(call.data.split("_")[1])
    await withdraw.withdraw_request(call, amount, bot)


@dp.callback_query(F.data.startswith("withdraw_ok"))
async def wok(call):
    await admin.withdraw_ok(call)


@dp.callback_query(F.data.startswith("withdraw_decline"))
async def wd(call):
    await admin.withdraw_decline(call)


@dp.message(F.text.startswith("/give"))
async def give(message):
    await admin.admin_give_stars(message)


@dp.callback_query(F.data == "back_main")
async def back(call):
    await call.message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    
