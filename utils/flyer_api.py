import requests
from config import FLYER_API_KEY

API_URL = "https://api.flyerservice.io/v1/tasks"

HEADERS = {
    "Authorization": f"Bearer {FLYER_API_KEY}",
    "Content-Type": "application/json"
}

def get_tasks(user_id: int):
    try:
        r = requests.get(API_URL, headers=HEADERS, params={"user_id": user_id, "limit": 5}, timeout=10)
        data = r.json()
        tasks = data.get("data", [])
        result = []
        for t in tasks:
            result.append({
                "title": t.get("title", "Задание"),
                "url": t.get("url", "#")
            })
        return result
    except Exception as e:
        print(f"[ERROR] Flyer API: {e}")
        return []
        
