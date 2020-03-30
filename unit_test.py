import unittest

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.instance = None

    def test_something(self):
        self.assertEqual(1, 1.0, 'int is not float')


if __name__ == '__main__':
        unittest.main()

