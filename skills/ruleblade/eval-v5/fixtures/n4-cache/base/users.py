import db


def get_user(user_id: int) -> dict:
    return db.load_user(user_id)
