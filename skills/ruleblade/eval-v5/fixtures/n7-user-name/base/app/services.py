from .models import User


def display_name(user: User) -> str:
    return user.name.strip().title()
