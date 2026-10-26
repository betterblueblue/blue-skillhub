import unittest

from calc import average, totals


class CalcTest(unittest.TestCase):
    def test_average(self):
        self.assertEqual(average([1, 2, 3]), 2)

    def test_totals(self):
        self.assertEqual(totals([{"amount": 3}, {"amount": 4}]), 7)
