from utils.users import get_user

def handle_referral(user_id, ref_id):
    if ref_id != user_id:
        ref_user = get_user(ref_id)
        ref_user["referrals"] += 1
        ref_user["ref_earnings"] += 2  # 2 звезды за приглашение
