import unittest

from shipping import shipping_fee


class ShippingTest(unittest.TestCase):
    def test_first_kg(self):
        self.assertEqual(shipping_fee(1), 10)
        self.assertEqual(shipping_fee(0.3), 10)

    def test_whole_kg(self):
        self.assertEqual(shipping_fee(3), 20)

    def test_partial_kg(self):
        self.assertEqual(shipping_fee(2.5), 17.5)
