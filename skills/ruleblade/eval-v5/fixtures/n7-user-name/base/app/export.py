import json
from pathlib import Path

from .models import User

FIELDS = json.loads((Path(__file__).parent / "export_fields.json").read_text(encoding="utf-8"))


def export_user(user: User) -> dict:
    return {field: getattr(user, field) for field in FIELDS}
