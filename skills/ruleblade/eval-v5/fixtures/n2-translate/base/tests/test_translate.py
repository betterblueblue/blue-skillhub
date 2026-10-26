import unittest

from translate import translate


class TranslateTest(unittest.TestCase):
    def test_greetings(self):
        self.assertEqual(translate("你好"), "Hello")
        self.assertEqual(translate("谢谢"), "Thank you")
        self.assertEqual(translate("早上好"), "Good morning")
