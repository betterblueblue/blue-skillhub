CALLS = {"load_user": 0}


def load_user(user_id: int) -> dict:
    CALLS["load_user"] += 1
    return {"id": user_id, "name": f"user{user_id}"}
