# 3.2 Testing: unittest, pytest and mocks
# Example "fixtures" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import sys
import unittest


class Cart:
    def __init__(self):
        self.items = {}

    def add(self, name, price):
        self.items[name] = price

    def total(self):
        return sum(self.items.values())


class TestCart(unittest.TestCase):
    def setUp(self):                           # runs before EVERY test: a fresh cart each time
        self.cart = Cart()
        self.cart.add("pen", 10)

    def test_total(self):
        self.assertEqual(self.cart.total(), 10)

    def test_add_more(self):
        self.cart.add("book", 250)
        self.assertEqual(self.cart.total(), 260)

    def test_many_prices(self):
        for price in [0, 5, 99]:
            with self.subTest(price=price):    # each value is reported on its own
                self.cart.add("extra", price)
                self.assertEqual(self.cart.total(), 10 + price)

    @unittest.skip("not written yet")
    def test_discount(self):
        pass


runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
unittest.main(argv=["tests"], testRunner=runner, exit=False)
