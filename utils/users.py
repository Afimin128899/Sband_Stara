from utils.storage import users

def get_user(user_id: int):
    if user_id not in users:
        users[user_id] = {
            "stars": 0,          # баланс
            "referrals": 0,      # количество приглашённых
            "withdrawn": 0       # сколько всего выведено
        }
    return users[user_id]

def add_referral(user_id: int):
    """Добавить 1 приглашённого и +2 звезды"""
    user = get_user(user_id)
    user["referrals"] += 1
    user["stars"] += 2
    
