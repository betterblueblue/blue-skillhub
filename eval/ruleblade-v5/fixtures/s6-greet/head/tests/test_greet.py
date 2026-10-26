import unittest

from greet import farewell, hello


class GreetTest(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(hello("Ann"), "Hello, Ann!")
        self.assertEqual(hello(""), "Hello!")

    def test_farewell(self):
        self.assertEqual(farewell("Ann"), "Goodbye, Ann!")
        self.assertEqual(farewell(""), "Goodbye!")
        self.assertEqual(farewell(None), "Goodbye!")
