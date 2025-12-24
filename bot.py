import asyncio
from aiogram import Bot, Dispatcher, F
from handlers import tasks, withdraw, admin, profile
from keyboards.main_menu import main_menu
from utils.users import get_user, add_referral

BOT_TOKEN = "8389664932:AAHw-vE5o52ODbQgUPcHf5CsSlhAIls_vDE"
ADMIN_ID = 548858090
FLYER_API_KEY = "FL-JCQcno-ZEliXE-fQqxRr-rfbkQS"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text.startswith("/start"))
async def start(message):
    parts = message.text.split(maxsplit=1)
    ref_id = parts[1] if len(parts) > 1 else None

    get_user(message.from_user.id)

    if ref_id:
        try:
            ref_id = int(ref_id)
            if ref_id != message.from_user.id:
                add_referral(ref_id)
        except:
            pass

    await message.answer(
        "👋 Добро пожаловать в Sband Stars",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "tasks")
async def tasks_cb(call):
    await tasks.tasks_handler(call, FLYER_API_KEY)

@dp.callback_query(F.data == "profile")
async def profile_cb(call):
    await profile.show_profile(call)

@dp.callback_query(F.data == "withdraw")
async def withdraw_menu(call):
    await withdraw.withdraw_menu_handler(call)

@dp.callback_query(F.data.startswith("withdraw_"))
async def withdraw_request(call):
    amount = int(call.data.split("_")[1])
    await withdraw.withdraw_request(call, amount, bot, ADMIN_ID)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
