from utils.storage import users


def get_user(user_id: int):
    if user_id not in users:
        users[user_id] = {
            "stars": 0,
            "referrals": 0
        }
    return users[user_id]
    
