import unittest
from accounts import business_logic


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.instance = None

    def test_something(self):
        self.assertEqual(1, 1.0, 'int is not float')


