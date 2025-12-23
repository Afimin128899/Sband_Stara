import requests

API_URL = "https://api.flyerservice.io/v1/tasks"

def get_tasks(user_id: int, api_key: str):
    """
    Получение доступных заданий FlyerService
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(API_URL, headers=headers, params={"user_id": user_id, "limit": 5}, timeout=10)
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
        
