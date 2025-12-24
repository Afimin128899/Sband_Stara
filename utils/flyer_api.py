import requests

API_URL = "https://api.flyerservice.io/v1/tasks"

def get_tasks(user_id, api_key):
    try:
        r = requests.get(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            params={"user_id": user_id}
        )
        return r.json().get("data", [])
    except:
        return []
        
