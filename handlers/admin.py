async def admin_give_stars(message, admin_id):
    if message.from_user.id != admin_id:
        return
        
