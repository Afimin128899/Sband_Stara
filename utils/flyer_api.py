import requests

API_URL = "https://api.flyerservice.io/v1/tasks"

def get_tasks(user_id: int, api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(
            API_URL,
            headers=headers,
            params={"user_id": user_id, "limit": 5},
            timeout=10
        )
        data = r.json()
        return data.get("data", [])
    except Exception as e:
        print("Flyer API error:", e)
        return []
        
