users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {"stars": 0, "refs": 0}
    return users[user_id]

def add_referral(ref_id):
    get_user(ref_id)
    users[ref_id]["refs"] += 1
    users[ref_id]["stars"] += 2
    
