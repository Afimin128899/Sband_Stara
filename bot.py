# bot.py
# Telegram referral bot: 1 реф = +1 ⭐ (внутренний баланс)
# + Flyer (flyerapi): обязательная подписка при /start + задания (tasks) и награда за выполнение

import os
import re
import asyncio
from datetime import datetime

import aiosqlite
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from flyerapi import Flyer

# ----------------- ENV -----------------
load_dotenv()

BOT_TOKEN = os.getenv("8500994183:AAFuJAtatem_2olCueCceAPi9QxMOL08_EE", "").strip()
FLYER_KEY = os.getenv("FL-eliuMo-kzwWnO-uvimwU-UOfqjW", "").strip()
APP_URL = (os.getenv("https://t.me/Sband_Stars_Check_Bot", "").strip()).rstrip("/")  # например: https://t.me/YourBotUsername

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is empty. Put it into .env")
if not FLYER_KEY:
    raise RuntimeError("FLYER_KEY is empty. Put it into .env")
if not APP_URL:
    raise RuntimeError("APP_URL is empty. Put it into .env (e.g. https://t.me/YourBotUsername)")

# ----------------- SETTINGS -----------------
DB_PATH = "db.sqlite3"
REF_RE = re.compile(r"^ref_(\d+)$")
TASKS_LIMIT = 10
TASK_REWARD_STARS = 1  # сколько ⭐ даём за выполненное задание Flyer

# ----------------- DB -----------------
CREATE_SQL = """
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  referrer_id INTEGER,
  referrals_count INTEGER NOT NULL DEFAULT 0,
  stars_balance INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_referrer ON users(referrer_id);

-- чтобы не награждать пользователя за одно и то же задание дважды
CREATE TABLE IF NOT EXISTS rewarded_tasks (
  user_id INTEGER NOT NULL,
  signature TEXT NOT NULL,
  rewarded_at TEXT NOT NULL,
  PRIMARY KEY (user_id, signature)
);
"""

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_SQL)
        await db.commit()

async def get_user(db: aiosqlite.Connection, user_id: int):
    cur = await db.execute(
        "SELECT user_id, referrer_id, referrals_count, stars_balance FROM users WHERE user_id=?",
        (user_id,),
    )
    return await cur.fetchone()

async def create_user(db: aiosqlite.Connection, user_id: int, referrer_id: int | None):
    await db.execute(
        "INSERT INTO users(user_id, referrer_id, referrals_count, stars_balance, created_at) VALUES(?,?,?,?,?)",
        (user_id, referrer_id, 0, 0, datetime.utcnow().isoformat()),
    )

async def add_ref_reward(db: aiosqlite.Connection, referrer_id: int, reward: int = 1):
    await db.execute(
        "UPDATE users SET referrals_count = referrals_count + 1, stars_balance = stars_balance + ? WHERE user_id=?",
        (reward, referrer_id),
    )

async def add_stars(db: aiosqlite.Connection, user_id: int, amount: int):
    await db.execute(
        "UPDATE users SET stars_balance = stars_balance + ? WHERE user_id=?",
        (amount, user_id),
    )

async def spend_star(db: aiosqlite.Connection, user_id: int, amount: int = 1) -> bool:
    cur = await db.execute("SELECT stars_balance FROM users WHERE user_id=?", (user_id,))
    row = await cur.fetchone()
    if not row:
        return False
    bal = int(row[0])
    if bal < amount:
        return False
    await db.execute("UPDATE users SET stars_balance = stars_balance - ? WHERE user_id=?", (amount, user_id))
    return True

async def was_task_rewarded(db: aiosqlite.Connection, user_id: int, signature: str) -> bool:
    cur = await db.execute(
        "SELECT 1 FROM rewarded_tasks WHERE user_id=? AND signature=?",
        (user_id, signature),
    )
    return (await cur.fetchone()) is not None

async def mark_task_rewarded(db: aiosqlite.Connection, user_id: int, signature: str):
    await db.execute(
        "INSERT OR IGNORE INTO rewarded_tasks(user_id, signature, rewarded_at) VALUES(?,?,?)",
        (user_id, signature, datetime.utcnow().isoformat()),
    )

# ----------------- BOT -----------------
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

flyer = Flyer(FLYER_KEY)

def make_ref_link(user_id: int) -> str:
    # deep-linking Telegram: https://t.me/YourBot?start=ref_123
    return f"{APP_URL}?start=ref_{user_id}"

def task_kb(tasks: list[dict]):
    kb = InlineKeyboardBuilder()
    for t in tasks:
        title = (t.get("title") or "Задание").strip()
        signature = t.get("signature")
        if not signature:
            continue
        kb.button(text=f"✅ Проверить: {title}", callback_data=f"taskcheck:{signature}")
    kb.adjust(1)
    return kb.as_markup()

async def ensure_registered_and_ref(message: Message, start_args: str) -> None:
    """Регистрирует пользователя и начисляет 1⭐ рефереру (только 1 раз, только для новых)."""
    user_id = message.from_user.id
    referrer_id = None

    m = REF_RE.match((start_args or "").strip()) if start_args else None
    if m:
        referrer_id = int(m.group(1))

    async with aiosqlite.connect(DB_PATH) as db:
        user = await get_user(db, user_id)
        if user is not None:
            return  # уже зарегистрирован

        valid_ref = (
            referrer_id is not None
            and referrer_id != user_id
        )

        if valid_ref:
            ref_exists = await get_user(db, referrer_id)
            if ref_exists is None:
                valid_ref = False

        await create_user(db, user_id, referrer_id if valid_ref else None)

        if valid_ref:
            await add_ref_reward(db, referrer_id, reward=1)

        await db.commit()

    # уведомим реферера (если был валидный)
    if valid_ref:
        try:
            await bot.send_message(
                referrer_id,
                f"✅ У тебя новый реферал!\n+1 ⭐ (внутренние звёзды)."
            )
        except Exception:
            pass

# ----------------- HANDLERS -----------------
@router.message(CommandStart())
async def start(message: Message, command: CommandStart):
    # 1) обязательная подписка через Flyer
    ok = await flyer.check(
        message.from_user.id,
        language_code=message.from_user.language_code
    )
    if not ok:
        return  # не пускаем дальше, пока не выполнит условия в Flyer

    # 2) рефералка + регистрация
    await ensure_registered_and_ref(message, command.args or "")

    # 3) приветствие
    await message.answer(
        "Привет! 👋\n"
        "Это реферальный бот.\n\n"
        "Команды:\n"
        "• /link — твоя реф-ссылка\n"
        "• /balance — рефералы и ⭐ баланс\n"
        "• /tasks — задания (Flyer)\n"
        "• /redeem — списать 1⭐ (пример обмена)\n\n"
        f"Твоя ссылка:\n{make_ref_link(message.from_user.id)}"
    )

@router.message(Command("link"))
async def link_cmd(message: Message):
    await message.answer(f"Твоя реф-ссылка:\n{make_ref_link(message.from_user.id)}")

@router.message(Command("balance"))
async def balance_cmd(message: Message):
    uid = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        user = await get_user(db, uid)
        if user is None:
            await message.answer("Ты ещё не зарегистрирован. Нажми /start")
            return
        _, _, refs, bal = user
    await message.answer(f"Рефералов: {refs}\nБаланс ⭐: {bal}")

@router.message(Command("redeem"))
async def redeem_cmd(message: Message):
    uid = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        user = await get_user(db, uid)
        if user is None:
            await message.answer("Нажми /start")
            return

        ok = await spend_star(db, uid, amount=1)
        if not ok:
            await message.answer("Недостаточно ⭐. Пригласи друзей через /link")
            return

        await db.commit()

    # Здесь вместо примера можно выдавать доступ/контент/промокод
    await message.answer("Готово! Списал 1⭐ 🎁")

@router.message(Command("tasks"))
async def tasks_cmd(message: Message):
    # на всякий случай — пусть /tasks тоже проверяет обязательные условия
    ok = await flyer.check(
        message.from_user.id,
        language_code=message.from_user.language_code
    )
    if not ok:
        return

    tasks = await flyer.get_tasks(
        user_id=message.from_user.id,
        language_code=message.from_user.language_code,
        limit=TASKS_LIMIT
    )

    if not tasks:
        await message.answer("Сейчас заданий нет.")
        return

    text_lines = ["Задания:", ""]
    for t in tasks:
        title = (t.get("title") or "Задание").strip()
        text_lines.append(f"• {title}")
    text_lines.append("")
    text_lines.append("Нажми «Проверить», чтобы получить награду.")

    await message.answer("\n".join(text_lines), reply_markup=task_kb(tasks))

@router.callback_query(F.data.startswith("taskcheck:"))
async def cb_taskcheck(call: CallbackQuery):
    user_id = call.from_user.id
    lang = call.from_user.language_code
    signature = call.data.split(":", 1)[1].strip()

    # проверим обязательные условия Flyer перед наградой
    ok = await flyer.check(user_id, language_code=lang)
    if not ok:
        await call.answer("Сначала выполни условия подписки.", show_alert=True)
        return

    # проверить задание в Flyer
    try:
        status = await flyer.check_task(user_id=user_id, signature=signature)
    except Exception:
        await call.answer("Ошибка проверки задания. Попробуй позже.", show_alert=True)
        return

    # В flyerapi статус может быть dict/булево — аккуратно определяем "выполнено"
    done = False
    if isinstance(status, bool):
        done = status
    elif isinstance(status, dict):
        # пробуем распространённые ключи
        for k in ("ok", "done", "completed", "success", "status"):
            if k in status:
                v = status[k]
                if isinstance(v, bool) and v:
                    done = True
                if isinstance(v, str) and v.lower() in ("ok", "done", "completed", "success", "true"):
                    done = True
    else:
        done = False

    if not done:
        await call.answer("Пока не выполнено ❌", show_alert=True)
        return

    # награда только 1 раз за signature
    async with aiosqlite.connect(DB_PATH) as db:
        user = await get_user(db, user_id)
        if user is None:
            # если человек нажал кнопку без /start — зарегистрируем
            await create_user(db, user_id, None)
            await db.commit()

        if await was_task_rewarded(db, user_id, signature):
            await call.answer("Уже получено ✅", show_alert=True)
            return

        await add_stars(db, user_id, TASK_REWARD_STARS)
        await mark_task_rewarded(db, user_id, signature)
        await db.commit()

    await call.answer(f"+{TASK_REWARD_STARS}⭐ начислено!", show_alert=True)
    await call.message.answer(f"✅ Задание выполнено. Начислил +{TASK_REWARD_STARS}⭐")

# ----------------- MAIN -----------------
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
