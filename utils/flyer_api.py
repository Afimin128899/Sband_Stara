import requests

API_KEY = "FL-JCQcno-ZEliXE-fQqxRr-rfbkQS"
API_URL = "https://api.flyerservice.io"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def get_tasks(user_id: int):
    try:
        r = requests.get(
            f"{API_URL}/v1/tasks",
            headers=HEADERS,
            params={"user_id": user_id},
            timeout=10
        )
        return r.json().get("tasks", [])
    except:
        return []
      
