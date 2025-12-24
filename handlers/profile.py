from utils.users import users

async def show_profile(call):
    u = users.get(call.from_user.id, {})
    await call.message.answer(
        f"👤 Профиль\n"
        f"⭐ Баланс: {u.get('stars',0)}\n"
        f"👥 Рефералы: {u.get('refs',0)}"
    )
    
