from flyerapi import Flyer

def get_flyer_tasks(user_id: int, api_key: str, language_code: str = "en"):
    """
    Получение списка заданий с помощью flyerapi.
    Возвращает список словарей с полями:
        title, description, signature (для проверки)
    """
    flyer = Flyer(api_key)
    try:
        tasks = flyer.get_tasks(user_id=user_id, language_code=language_code, limit=5)
        # Возвращаем сырой список заданий
        return tasks
    except Exception as e:
        print(f"[FlyerAPI error] {e}")
        return []
        
