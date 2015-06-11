import unittest

class FlaskrTestCase(unittest.TestCase):

    def fakeTest(self):
        self.assertTrue(10 < 20)

if __name__ == '__main__':
    unittest.main()