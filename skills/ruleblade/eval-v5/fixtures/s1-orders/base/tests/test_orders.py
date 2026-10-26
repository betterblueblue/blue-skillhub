import unittest

from app.export import to_row
from app.models import Order
from app.payment import can_ship, refund


class OrderTest(unittest.TestCase):
    def test_can_ship_only_when_paid(self):
        self.assertFalse(can_ship(Order(id=1, amount=100)))
        self.assertTrue(can_ship(Order(id=2, amount=100, status="paid")))

    def test_refund(self):
        order = Order(id=3, amount=100, status="paid")
        refund(order)
        self.assertEqual(order.status, "refunded")

    def test_export_row(self):
        row = to_row(Order(id=4, amount=50, state="published"))
        self.assertEqual(row, {"id": 4, "amount": 50, "state": "published"})
