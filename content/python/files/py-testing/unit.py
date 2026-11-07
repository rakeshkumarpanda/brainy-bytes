# 3.2 Testing: unittest, pytest and mocks
# Example "unit" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import sys
import unittest


def discount(price, percent):
    if percent < 0 or percent > 100:
        raise ValueError("percent must be 0 to 100")
    return price * (100 - percent) / 100


class TestDiscount(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(discount(100, 0), 100)

    def test_half_price(self):
        self.assertEqual(discount(80, 50), 40)

    def test_float_rounding(self):
        self.assertAlmostEqual(discount(0.3, 0), 0.1 + 0.2)

    def test_bad_percent(self):
        with self.assertRaises(ValueError):
            discount(10, 150)


runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
unittest.main(argv=["tests"], testRunner=runner, exit=False)
