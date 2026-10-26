import unittest

from pricing import discount


class PricingTest(unittest.TestCase):
    def test_no_discount_for_small_order(self):
        self.assertEqual(discount(50), 50)
