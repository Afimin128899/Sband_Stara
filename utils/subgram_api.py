import requests

SUBGRAM_API = "https://api.subgram.org/api/v1"
SUBGRAM_API_KEY = "ВАШ_SUBGRAM_API_KEY"

def get_sponsors(user_id):
    """Получение заданий (спонсоров) через SubGram API"""
    response = requests.post(
        f"{SUBGRAM_API}/pub/get-sponsors",
        headers={"Authorization": f"Bearer {SUBGRAM_API_KEY}"},
        json={"user_id": user_id}
    )
    data = response.json()
    sponsors = data.get("result", {}).get("sponsors", [])
    return sponsors
