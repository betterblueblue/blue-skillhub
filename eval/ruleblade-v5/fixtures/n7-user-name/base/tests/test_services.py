import unittest

from app.export import export_user
from app.models import User
from app.services import display_name


class UserTest(unittest.TestCase):
    def test_display_name(self):
        self.assertEqual(display_name(User(id=1, name=" ann lee ", email="a@x.io")), "Ann Lee")

    def test_export(self):
        user = User(id=2, name="bo", email="b@x.io")
        self.assertEqual(export_user(user), {"id": 2, "name": "bo", "email": "b@x.io"})
