# Хранилище пользователей (для простоты, в реальной версии - база)
users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "stars": 0,
            "referrals": 0,
            "ref_earnings": 0,
            "ref_link": f"https://t.me/YourBot?start={user_id}"
        }
    return users[user_id]
