import os
import re
import asyncio
from datetime import datetime

import asyncpg
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
APP_URL = (os.getenv("https://t.me/Sband_Stars_Check_Bot", "").strip()).rstrip("/")
DATABASE_URL = os.getenv("postgresql://SbandStarsdx_necessary:3e8a6346378acc5eb7ef1e7268f2c54f6a21c1a2@5ikxsp.h.filess.io:5434/SbandStarsdx_necessary", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is empty. Put it into .env")
if not FLYER_KEY:
    raise RuntimeError("FLYER_KEY is empty. Put it into .env")
if not APP_URL:
    raise RuntimeError("APP_URL is empty. Put it into .env (e.g. https://t.me/YourBotUsername)")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is empty. Put it into .env (postgresql://user:pass@host:5432/db)")

# ----------------- SETTINGS -----------------
REF_RE = re.compile(r"^ref_(\d+)$")
TASKS_LIMIT = 5
TASK_REWARD_STARS = 1

# ----------------- SQL -----------------
CREATE_SQL = """
CREATE TABLE IF NOT EXISTS users (
  user_id BIGINT PRIMARY KEY,
  referrer_id BIGINT NULL,
  referrals_count INTEGER NOT NULL DEFAULT 0,
  stars_balance INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_referrer ON users(referrer_id);

CREATE TABLE IF NOT EXISTS rewarded_tasks (
  user_id BIGINT NOT NULL,
  signature TEXT NOT NULL,
  rewarded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, signature)
);
"""

# ----------------- Bot / Dispatcher -----------------
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

flyer = Flyer(FLYER_KEY)

pool: asyncpg.Pool | None = None

def make_ref_link(user_id: int) -> str:
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

# ----------------- DB helpers -----------------
async def db_init():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    async with pool.acquire() as conn:
        await conn.execute(CREATE_SQL)

async def db_get_user(conn: asyncpg.Connection, user_id: int):
    return await conn.fetchrow(
        "SELECT user_id, referrer_id, referrals_count, stars_balance FROM users WHERE user_id=$1",
        user_id,
    )

async def db_create_user(conn: asyncpg.Connection, user_id: int, referrer_id: int | None):
    await conn.execute(
        """
        INSERT INTO users(user_id, referrer_id, referrals_count, stars_balance, created_at)
        VALUES ($1, $2, 0, 0, NOW())
        ON CONFLICT (user_id) DO NOTHING
        """,
        user_id, referrer_id
    )

async def db_add_ref_reward(conn: asyncpg.Connection, referrer_id: int, reward: int = 1):
    await conn.execute(
        """
        UPDATE users
        SET referrals_count = referrals_count + 1,
            stars_balance = stars_balance + $2
        WHERE user_id = $1
        """,
        referrer_id, reward
    )

async def db_add_stars(conn: asyncpg.Connection, user_id: int, amount: int):
    await conn.execute(
        "UPDATE users SET stars_balance = stars_balance + $2 WHERE user_id=$1",
        user_id, amount
    )

async def db_spend_star(conn: asyncpg.Connection, user_id: int, amount: int = 1) -> bool:
    # атомарно: списать только если хватает
    row = await conn.fetchrow(
        """
        UPDATE users
        SET stars_balance = stars_balance - $2
        WHERE user_id = $1 AND stars_balance >= $2
        RETURNING stars_balance
        """,
        user_id, amount
    )
    return row is not None

async def db_was_task_rewarded(conn: asyncpg.Connection, user_id: int, signature: str) -> bool:
    row = await conn.fetchrow(
        "SELECT 1 FROM rewarded_tasks WHERE user_id=$1 AND signature=$2",
        user_id, signature
    )
    return row is not None

async def db_mark_task_rewarded(conn: asyncpg.Connection, user_id: int, signature: str):
    await conn.execute(
        """
        INSERT INTO rewarded_tasks(user_id, signature, rewarded_at)
        VALUES ($1, $2, NOW())
        ON CONFLICT (user_id, signature) DO NOTHING
        """,
        user_id, signature
    )

async def ensure_registered_and_ref(message: Message, start_args: str) -> None:
    """Регистрирует пользователя (только 1 раз). Если старт по рефке — начисляет +1⭐ рефереру."""
    assert pool is not None
    user_id = message.from_user.id

    referrer_id = None
    m = REF_RE.match((start_args or "").strip()) if start_args else None
    if m:
        referrer_id = int(m.group(1))

    async with pool.acquire() as conn:
        async with conn.transaction():
            user = await db_get_user(conn, user_id)
            if user is not None:
                return  # уже есть

            valid_ref = (referrer_id is not None and referrer_id != user_id)
            if valid_ref:
                ref_exists = await db_get_user(conn, referrer_id)
                if ref_exists is None:
                    valid_ref = False

            await db_create_user(conn, user_id, referrer_id if valid_ref else None)

            if valid_ref:
                await db_add_ref_reward(conn, referrer_id, reward=1)

    if referrer_id and referrer_id != user_id:
        # уведомим реферера (если он был валидный и существовал)
        try:
            await bot.send_message(referrer_id, "✅ У тебя новый реферал!\n+1 ⭐ (внутренние звёзды).")
        except Exception:
            pass

# ----------------- Handlers -----------------
@router.message(CommandStart())
async def start(message: Message, command: CommandStart):
    # 1) обязательная подписка через Flyer
    ok = await flyer.check(message.from_user.id, language_code=message.from_user.language_code)
    if not ok:
        return

    # 2) регистрация + рефка
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
    assert pool is not None
    uid = message.from_user.id
    async with pool.acquire() as conn:
        user = await db_get_user(conn, uid)
        if user is None:
            await message.answer("Ты ещё не зарегистрирован. Нажми /start")
            return
        refs = int(user["referrals_count"])
        bal = int(user["stars_balance"])
    await message.answer(f"Рефералов: {refs}\nБаланс ⭐: {bal}")

@router.message(Command("redeem"))
async def redeem_cmd(message: Message):
    assert pool is not None
    uid = message.from_user.id

    async with pool.acquire() as conn:
        async with conn.transaction():
            user = await db_get_user(conn, uid)
            if user is None:
                await message.answer("Нажми /start")
                return

            ok = await db_spend_star(conn, uid, amount=1)
            if not ok:
                await message.answer("Недостаточно ⭐. Пригласи друзей через /link")
                return

    await message.answer("Готово! Списал 1⭐ 🎁")

@router.message(Command("tasks"))
async def tasks_cmd(message: Message):
    # тоже проверяем обязательные условия
    ok = await flyer.check(message.from_user.id, language_code=message.from_user.language_code)
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
    assert pool is not None
    user_id = call.from_user.id
    lang = call.from_user.language_code
    signature = call.data.split(":", 1)[1].strip()

    ok = await flyer.check(user_id, language_code=lang)
    if not ok:
        await call.answer("Сначала выполни условия подписки.", show_alert=True)
        return

    try:
        status = await flyer.check_task(user_id=user_id, signature=signature)
    except Exception:
        await call.answer("Ошибка проверки задания. Попробуй позже.", show_alert=True)
        return

    # универсальная попытка понять "выполнено"
    done = False
    if isinstance(status, bool):
        done = status
    elif isinstance(status, dict):
        for k in ("ok", "done", "completed", "success", "status"):
            if k in status:
                v = status[k]
                if isinstance(v, bool) and v:
                    done = True
                if isinstance(v, str) and v.lower() in ("ok", "done", "completed", "success", "true"):
                    done = True

    if not done:
        await call.answer("Пока не выполнено ❌", show_alert=True)
        return

    # награда 1 раз за signature
    async with pool.acquire() as conn:
        async with conn.transaction():
            # если пользователь вдруг без /start — создадим
            await db_create_user(conn, user_id, None)

            if await db_was_task_rewarded(conn, user_id, signature):
                await call.answer("Уже получено ✅", show_alert=True)
                return

            await db_add_stars(conn, user_id, TASK_REWARD_STARS)
            await db_mark_task_rewarded(conn, user_id, signature)

    await call.answer(f"+{TASK_REWARD_STARS}⭐ начислено!", show_alert=True)
    await call.message.answer(f"✅ Задание выполнено. Начислил +{TASK_REWARD_STARS}⭐")

# ----------------- MAIN -----------------
async def main():
    await db_init()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

