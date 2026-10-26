import unittest

from greet import hello


class GreetTest(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(hello("Ann"), "Hello, Ann!")
        self.assertEqual(hello(""), "Hello!")
