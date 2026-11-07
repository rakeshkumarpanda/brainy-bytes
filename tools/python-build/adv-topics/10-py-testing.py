# Advanced Python 3.2: testing. Goes beyond PCPP-32-101 (which names unittest in its testing block) to the tools
# used in real projects, checked against the Python 3.14 documentation of unittest and unittest.mock, and the
# documentation of pytest 9.2 (fixtures, parametrize, raises, approx, tmp_path, monkeypatch), coverage.py 7 and
# Hypothesis. Every terminal output on the page is a real run made while writing this chapter.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show, term

chapter('py-testing')
K = Kit()

K.code('unit', r'''
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
''')

K.code('fixtures', r'''
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
''')

K.code('failures', r'''
import unittest


def average(numbers):
    return sum(numbers) / len(numbers)


class TestAverage(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(average([2, 4]), 3)

    def test_wrong_expectation(self):
        self.assertEqual(average([1, 2]), 2)   # the TEST is wrong here: 1.5 != 2

    def test_empty(self):
        average([])                            # crashes: this is an ERROR, not a FAIL


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAverage)
result = unittest.TestResult()
suite.run(result)
print("ran:", result.testsRun)
for test, trace in result.failures:
    print("FAIL :", test.id().split(".")[-1], "|", trace.strip().splitlines()[-1])
for test, trace in result.errors:
    print("ERROR:", test.id().split(".")[-1], "|", trace.strip().splitlines()[-1])
print("all passed:", result.wasSuccessful())
''')

K.code('mocking', r'''
from unittest.mock import Mock, patch


class WeatherClient:
    def temperature(self, city):
        raise RuntimeError("this would call the internet")


def advice(client, city):
    t = client.temperature(city)
    return "take a jacket" if t < 15 else "t-shirt weather"


fake = Mock()
fake.temperature.return_value = 9              # pretend the service said 9 degrees
print(advice(fake, "Pune"))
fake.temperature.assert_called_once_with("Pune")
print(fake.temperature.call_count, fake.temperature.call_args)

fake.temperature.side_effect = [20, 3]         # a different answer on each call
print(advice(fake, "Goa"), "|", advice(fake, "Leh"))

with patch.object(WeatherClient, "temperature", return_value=30):
    print(advice(WeatherClient(), "Delhi"))    # the real class with one method replaced

flaky = Mock(side_effect=TimeoutError("no answer"))
try:
    flaky()
except TimeoutError as err:
    print("TimeoutError:", err)
''')

SHOP = '''import json
import os


def discount(price, percent):
    if percent < 0 or percent > 100:
        raise ValueError("percent must be 0 to 100")
    return price - price * percent / 100


def price_with_tax(price):
    rate = float(os.environ.get("TAX_RATE", "0.18"))
    return round(price * (1 + rate), 2)


class Cart:
    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        self.items[name] = self.items.get(name, 0) + price * qty

    def total(self):
        return sum(self.items.values())

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.items, f)'''

TESTS = '''import json

import pytest

from shop import Cart, discount, price_with_tax


@pytest.fixture
def cart():
    c = Cart()
    c.add("pen", 10, qty=3)
    c.add("book", 250)
    return c


def test_total(cart):
    assert cart.total() == 280


@pytest.mark.parametrize("price, percent, expected", [
    (100, 0, 100),
    (80, 50, 40),
    (99, 10, 89.1),
    (0.3, 0, 0.1 + 0.2),
])
def test_discount(price, percent, expected):
    assert discount(price, percent) == pytest.approx(expected)


def test_bad_percent():
    with pytest.raises(ValueError, match="0 to 100"):
        discount(10, 150)


def test_save(cart, tmp_path):
    path = tmp_path / "cart.json"
    cart.save(path)
    assert json.loads(path.read_text()) == {"pen": 30, "book": 250}


def test_tax_rate_from_environment(monkeypatch):
    monkeypatch.setenv("TAX_RATE", "0.05")
    assert price_with_tax(200) == 210.0'''

PROPS = '''from hypothesis import given, strategies as st

from shop import discount


@given(st.floats(min_value=0, max_value=1e6))
def test_full_discount_is_free(price):
    assert discount(price, 100) == 0'''

K.lesson('idea', 'Why we test, and a first test suite', f'''
{src('Python 3.14 documentation of unittest and unittest.mock, and the documentation of pytest 9.2, coverage.py and Hypothesis. Terminal outputs are real runs.')}
{wwh('A <b>test</b> is a small piece of code that calls your code with known inputs and checks the result. A <b>test suite</b> is all of them together, and a <b>test runner</b> (unittest or pytest) finds them, runs them and reports what passed and what failed.',
     'Without tests you check by hand, once, and every later change can silently break something that used to work. Tests check the same things in a second, every time, so you can change and improve code without fear. They also show how the code is meant to be used, and a failing test points straight at the bug.',
     'Each test follows <b>Arrange, Act, Assert</b>: set up the inputs, call the code, and assert what must be true. The runner records PASSED, FAILED (an assert was false) or ERROR (the test crashed). In <b>test driven development</b> you write the failing test first (red), make it pass (green), then clean up the code (refactor) with the tests watching.')}
{viz('pyunit')}
{run('unit')}
{note('unittest is built into Python. A test is a method whose name starts with test_ inside a class that inherits from unittest.TestCase. assertEqual, assertTrue, assertIn, assertRaises and assertAlmostEqual (for floats) check results and give a clear message when they fail.', 'exam')}
''', kw=['testing', 'unit test', 'unittest', 'TestCase', 'assertEqual', 'assertRaises', 'Arrange Act Assert', 'TDD', 'red green refactor'])

K.lesson('fixtures', 'setUp, subTest and skip', f'''
{run('fixtures')}
{table(['Tool', 'What it does'], [
    ['setUp(self) and tearDown(self)', 'Run before and after EVERY test, so each test starts fresh'],
    ['setUpClass(cls) and tearDownClass(cls)', 'Run once for the whole class (for slow set up like a database)'],
    ['self.subTest(...)', 'Inside a loop, report each case separately and keep going after a failure'],
    ['@unittest.skip(reason), skipIf(cond, reason)', 'Do not run this test, and say why'],
    ['@unittest.expectedFailure', 'A known bug: the test is expected to fail for now'],
    ['python -m unittest discover', 'Find every test_*.py file in the folder and run it']])}
{note('Tests must not depend on each other or on their order. test_add_more added a book, but test_total still saw only the pen, because setUp made a new cart for each test.', 'warn')}
''', kw=['setUp', 'tearDown', 'setUpClass', 'subTest', 'skip', 'expectedFailure', 'discover', 'test isolation'])

K.lesson('failures', 'Reading failures and errors', f'''
{run('failures')}
{versus('Three outcomes of a test', ['', 'PASSED', 'FAILED', 'ERROR'], [
    ['Means', 'Every assert was true', 'An assert was false', 'The test crashed with another exception'],
    ['Usually points to', 'Nothing to do', 'Wrong result: a bug in the code or in the test', 'A crash: bad input handling, a typo, a missing file'],
    ['First thing to read', '', 'The two values in the message', 'The last line of the traceback']],
    'read the last line first. When a test fails, check whether the code or the test is wrong: here test_wrong_expectation expected 2, but the average of 1 and 2 really is 1.5.')}
''', kw=['FAIL', 'ERROR', 'AssertionError', 'traceback', 'TestResult', 'wasSuccessful'])

K.lesson('mocking', 'Mocks: replacing what you cannot test', f'''
{run('mocking')}
{table(['Mock feature', 'Use'], [
    ['Mock().method.return_value = x', 'The fake method returns x'],
    ['side_effect = [a, b] or an exception', 'A different answer on each call, or raise an error to test failure handling'],
    ['assert_called_once_with(...), call_count, call_args', 'Check HOW your code used the dependency'],
    ['patch("module.name") and patch.object(Class, "attr")', 'Replace a real object for the length of a with block or a test, then put it back'],
    ['MagicMock', 'A Mock that also supports special methods like len() and with']])}
{note('advice() receives the client as an argument (dependency injection), so a test can hand it a fake. Code that creates its own network client deep inside is much harder to test. Designing for testability means passing dependencies in.', 'tip')}
{versus('Testing code that calls a web service', ['', 'call the real service', 'a Mock', 'a fake local server'], [
    ['Speed', 'Slow', 'Instant', 'Fast'],
    ['Works offline and in CI', 'No', 'Yes', 'Yes'],
    ['Can test timeouts and errors', 'Hard', 'Easy with side_effect', 'Yes'],
    ['Catches changes in the real service', 'Yes', 'No', 'No']],
    'use mocks for unit tests, and keep a few slow integration tests that call the real thing.')}
''', kw=['mock', 'Mock', 'MagicMock', 'patch', 'patch.object', 'side_effect', 'return_value', 'dependency injection', 'test double'])

K.lesson('pytest', 'pytest: the most used test runner', f'''
<p>pytest needs plain functions and plain assert, and gives much more detail when something fails. Install it with <code>pip install pytest</code>. Here is a small module and its tests:</p>
{show('shop.py', SHOP)}
{show('test_shop.py', TESTS, {8: 'A <b>fixture</b>: any test that names cart as a parameter gets a fresh one.', 20: '<b>parametrize</b> runs the same test once per row.', 27: '<b>pytest.approx</b> compares floats with a small tolerance, so 0.1 + 0.2 equals 0.3.', 31: '<b>pytest.raises</b> passes only if the error is raised, and match checks its message.', 35: '<b>tmp_path</b> is a built in fixture: a fresh temporary folder for this test.', 41: '<b>monkeypatch</b> changes an environment variable just for this test.'})}
{term(['$ pytest -v',
       'collecting ... collected 8 items',
       '',
       'test_shop.py::test_total PASSED                                          [ 12%]',
       'test_shop.py::test_discount[100-0-100] PASSED                            [ 25%]',
       'test_shop.py::test_discount[80-50-40] PASSED                             [ 37%]',
       'test_shop.py::test_discount[99-10-89.1] PASSED                           [ 50%]',
       'test_shop.py::test_discount[0.3-0-0.30000000000000004] PASSED            [ 62%]',
       'test_shop.py::test_bad_percent PASSED                                    [ 75%]',
       'test_shop.py::test_save PASSED                                           [ 87%]',
       'test_shop.py::test_tax_rate_from_environment PASSED                      [100%]',
       '',
       '============================== 8 passed in 0.11s ==============================='], 'Running the tests')}
<p>Change / to // in discount and run only the discount tests. pytest shows the values on both sides of the failing assert:</p>
{term(['$ pytest -q -k discount',
       '..F.                                                                     [100%]',
       '=================================== FAILURES ===================================',
       '__________________________ test_discount[99-10-89.1] ___________________________',
       '',
       'price = 99, percent = 10, expected = 89.1',
       '',
       '>       assert discount(price, percent) == pytest.approx(expected)',
       'E       assert 90 == 89.1 &plusmn; 8.9e-05',
       'E         comparison failed',
       'E         Obtained: 90',
       'E         Expected: 89.1 &plusmn; 8.9e-05',
       '',
       'test_shop.py:27: AssertionError',
       '=========================== short test summary info ============================',
       'FAILED test_shop.py::test_discount[99-10-89.1] - assert 90 == 89.1 &plusmn; 8.9e-05',
       '1 failed, 3 passed, 4 deselected in 0.11s'], 'A failing test')}
{term(['$ coverage run -m pytest -q',
       '$ coverage report -m',
       'Name      Stmts   Miss  Cover   Missing',
       '---------------------------------------',
       'shop.py      19      0   100%',
       '---------------------------------------',
       'TOTAL        19      0   100%'], 'Measuring coverage')}
{versus('Test runners', ['', 'unittest', 'pytest', 'doctest'], [
    ['Install', 'Built in', 'pip install pytest', 'Built in'],
    ['A test is', 'A method in a TestCase class', 'Any test_ function', 'A >>> example in a docstring'],
    ['Checks with', 'self.assertEqual and friends', 'Plain assert, with detailed messages', 'Printed output'],
    ['Set up', 'setUp and tearDown', 'Fixtures, shared and combined by name', 'None'],
    ['Many inputs', 'subTest', 'parametrize', 'More examples'],
    ['Runs the others', 'No', 'Yes, unittest and doctest tests too', 'No']],
    'use pytest for projects. It runs old unittest suites too. Keep doctest for examples in documentation.')}
{note('100 % coverage means every line ran during the tests, NOT that every case was checked. The next lesson shows a bug that survives full coverage.', 'warn')}
''', kw=['pytest', 'fixture', 'parametrize', 'approx', 'raises', 'tmp_path', 'monkeypatch', 'coverage', '-k', '-v'])

K.lesson('property', 'Property based testing', f'''
<p>Instead of picking examples yourself, you state a rule that must hold for EVERY input, and the Hypothesis library (<code>pip install hypothesis</code>) searches for an input that breaks it. Rule: a 100 % discount makes any price free.</p>
{show('test_props.py', PROPS)}
{term(['$ pytest -q test_props.py',
       'F                                                                        [100%]',
       '=================================== FAILURES ===================================',
       '__________________________ test_full_discount_is_free __________________________',
       'price = 41943.17912896944',
       '',
       '>       assert discount(price, 100) == 0',
       'E       assert -7.275957614183426e-12 == 0',
       'E        +  where -7.275957614183426e-12 = discount(41943.17912896944, 100)',
       'E       Failing test case: test_full_discount_is_free(',
       'E           price=41943.17912896944,',
       'E       )',
       '=========================== short test summary info ============================',
       'FAILED test_props.py::test_full_discount_is_free - assert -7.275957614183426e...',
       '1 failed in 0.26s'], 'Hypothesis finds a real bug')}
{note('All 8 example tests passed with 100 % coverage, yet price &minus; price &times; 100 / 100 can come out a tiny bit below zero because of float rounding. The fix is price &times; (100 &minus; percent) / 100, which gives exactly 0 at 100 %. The failing price changes from run to run, because Hypothesis tries random inputs.', 'exam')}
''', kw=['property based testing', 'Hypothesis', 'given', 'strategies', 'float rounding', 'invariant'])

K.lesson('strategy', 'What to test and how much', f'''
{table(['Kind of test', 'Checks', 'Speed', 'How many'], [
    ['Unit test', 'One function or class, dependencies mocked', 'Milliseconds', 'Most of them'],
    ['Integration test', 'Several parts together: code plus a real database or file', 'Seconds', 'Some'],
    ['End to end test', 'The whole program as a user uses it (for web apps: Selenium or Playwright)', 'Slow', 'A few for the main journeys']])}
{table(['Always test', 'Example for discount(price, percent)'], [
    ['A normal case', 'discount(80, 50) is 40'],
    ['The edges of every range', 'percent 0 and 100, price 0'],
    ['Just outside the range', 'percent &minus;1 and 101 raise ValueError'],
    ['Awkward values', 'floats like 0.3, very large prices'],
    ['Every bug you fixed', 'A regression test that would have caught it']])}
{note('This shape, many fast unit tests at the bottom and few slow end to end tests at the top, is called the test pyramid. Run the fast tests on every save and all tests in CI (see the Git and CI/CD subject).', 'tip')}
''', kw=['test pyramid', 'unit test', 'integration test', 'end to end', 'edge cases', 'boundary values', 'regression test', 'CI'])

K.lesson('maths', 'The maths: coverage, boundaries and binary search', f'''
{fxs(fx('Line coverage', 'coverage = lines run / total lines &times; 100 %', '17 of 19 lines run: 17 / 19 &asymp; 89.5 %.', key=True),
     fx('Boundary value tests for a range a to b', 'test a &minus; 1, a, b, b + 1 (and one value inside)', 'percent from 0 to 100: test &minus;1, 0, 100, 101 and 50, five tests.', key=True),
     fx('Combinations of k options with v values each', 'all combinations = v<sup>k</sup>', '3 settings with 4 values each: 64 tests. Pairwise testing covers every pair of values with far fewer, about v<sup>2</sup> = 16.'),
     fx('Binary search steps (the LeetCode set)', 'steps &le; &lceil;log<sub>2</sub>(n + 1)&rceil;', 'n = 1000 sorted items: at most 10 steps. This is also how git bisect finds the commit that broke a test.', key=True),
     fx('Chance a random test hits a bug that needs one value out of N', '1 &minus; (1 &minus; 1/N)<sup>t</sup> after t tests', 'N = 1000 and t = 100: about 9.5 %. Picking edge cases on purpose beats random luck.'))}
{steps('Worked example: how many commits does git bisect test?', [
    'A test passed 1000 commits ago and fails now.',
    'Each check halves the commits that could contain the bug.',
    '2<sup>10</sup> = 1024 is the first power of 2 that is at least 1000.',
    eq('at most 10 test runs to find the commit that broke it')])}
''', kw=['coverage formula', 'boundary value analysis', 'pairwise testing', 'binary search', 'git bisect', 'probability'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write unittest test cases with assertEqual and assertRaises and run them.</p>',
    '<p>Use setUp, subTest and skip, read failures and errors, and write pytest tests with fixtures, parametrize, approx and raises.</p>',
    '<p>Mock dependencies with Mock, side_effect and patch, measure coverage, test edge cases on purpose, and work test first.</p>',
    '<p>Design for testability (dependency injection, pure functions), write property based tests with Hypothesis, use mutation testing to check that the tests themselves catch bugs, and build a pyramid of unit, integration and end to end tests that runs in CI.</p>')}
{grow('Write and run tests.', 'Use fixtures, parametrize and mocks.', 'Design testable code and test the tests.')}
''', kw=['beginner', 'expert', 'mutation testing', 'testability'])

lc(704, 'Binary Search', 'binary-search', 'e', 'Halve the range each step', 'Keep low and high. Look at the middle. The famous bug is an off by one in the loop condition, so test arrays of length 0, 1 and 2.', r'''
def search(nums, target):
    low, high = 0, len(nums) - 1
    while low <= high:
        middle = (low + high) // 2
        if nums[middle] == target:
            return middle
        if nums[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1
''', [('search([-1, 0, 3, 5, 9, 12], 9)', 4), ('search([-1, 0, 3, 5, 9, 12], 2)', -1), ('search([], 1)', -1), ('[search([7], 7), search([7], 1)]', [0, -1])])
lc(35, 'Search Insert Position', 'search-insert-position', 'e', 'Binary search for the first place not smaller', 'When the loop ends, low is where target belongs. Test before the first item and after the last.', r'''
def search_insert(nums, target):
    low, high = 0, len(nums)
    while low < high:
        middle = (low + high) // 2
        if nums[middle] < target:
            low = middle + 1
        else:
            high = middle
    return low
''', [('[search_insert([1, 3, 5, 6], t) for t in [5, 2, 7, 0]]', [2, 1, 4, 0])])
lc(278, 'First Bad Version', 'first-bad-version', 'e', 'Binary search on a yes or no question', 'Exactly what git bisect does with a failing test. The is_bad check is passed in, so a test can give a fake one.', r'''
def first_bad_version(n, is_bad):
    low, high = 1, n
    while low < high:
        middle = (low + high) // 2
        if is_bad(middle):
            high = middle
        else:
            low = middle + 1
    return low


def make_is_bad(first_bad):
    """A fake version checker for the tests (LeetCode gives you isBadVersion)."""
    return lambda version: version >= first_bad
''', [('first_bad_version(5, make_is_bad(4))', 4), ('first_bad_version(1, make_is_bad(1))', 1), ('first_bad_version(2126753390, make_is_bad(1702766719))', 1702766719)])
lc(374, 'Guess Number Higher or Lower', 'guess-number-higher-or-lower', 'e', 'Binary search against an API', 'The guess API answers -1, 1 or 0. In tests we inject a fake API, like a Mock with a side effect.', r'''
def guess_number(n, guess):
    low, high = 1, n
    while True:
        middle = (low + high) // 2
        answer = guess(middle)
        if answer == 0:
            return middle
        if answer == -1:
            high = middle - 1
        else:
            low = middle + 1


def make_guess(pick):
    """A fake guess API for the tests: -1 means too high, 1 means too low."""
    def guess(number):
        if number > pick:
            return -1
        if number < pick:
            return 1
        return 0
    return guess
''', [('guess_number(10, make_guess(6))', 6), ('guess_number(1, make_guess(1))', 1), ('guess_number(2, make_guess(2))', 2)])
lc(34, 'Find First and Last Position of Element in Sorted Array', 'find-first-and-last-position-of-element-in-sorted-array', 'm', 'Two binary searches', 'Find the first index not smaller than target and the first index bigger than target. bisect_left and bisect_right do exactly this.', r'''
import bisect


def search_range(nums, target):
    left = bisect.bisect_left(nums, target)
    if left == len(nums) or nums[left] != target:
        return [-1, -1]
    return [left, bisect.bisect_right(nums, target) - 1]
''', [('search_range([5, 7, 7, 8, 8, 10], 8)', [3, 4]), ('search_range([5, 7, 7, 8, 8, 10], 6)', [-1, -1]), ('search_range([], 0)', [-1, -1])])
lc(162, 'Find Peak Element', 'find-peak-element', 'm', 'Walk uphill with binary search', 'If the middle is lower than its right neighbour, a peak lies to the right. Otherwise it lies at the middle or to the left.', r'''
def find_peak_element(nums):
    low, high = 0, len(nums) - 1
    while low < high:
        middle = (low + high) // 2
        if nums[middle] < nums[middle + 1]:
            low = middle + 1
        else:
            high = middle
    return low
''', [('find_peak_element([1, 2, 3, 1])', 2), ('find_peak_element([1, 2, 1, 3, 5, 6, 4]) in (1, 5)', True)])
lc(153, 'Find Minimum in Rotated Sorted Array', 'find-minimum-in-rotated-sorted-array', 'm', 'Compare the middle with the right end', 'If the middle is bigger than the last item, the drop (and the minimum) is to the right.', r'''
def find_min(nums):
    low, high = 0, len(nums) - 1
    while low < high:
        middle = (low + high) // 2
        if nums[middle] > nums[high]:
            low = middle + 1
        else:
            high = middle
    return nums[low]
''', [('find_min([3, 4, 5, 1, 2])', 1), ('find_min([4, 5, 6, 7, 0, 1, 2])', 0), ('find_min([11, 13, 15, 17])', 11)])
lc(33, 'Search in Rotated Sorted Array', 'search-in-rotated-sorted-array', 'm', 'One half is always sorted', 'Check which half is in order, then whether target lies inside it. Many edge cases: test a rotation at every position.', r'''
def search_rotated(nums, target):
    low, high = 0, len(nums) - 1
    while low <= high:
        middle = (low + high) // 2
        if nums[middle] == target:
            return middle
        if nums[low] <= nums[middle]:
            if nums[low] <= target < nums[middle]:
                high = middle - 1
            else:
                low = middle + 1
        else:
            if nums[middle] < target <= nums[high]:
                low = middle + 1
            else:
                high = middle - 1
    return -1
''', [('search_rotated([4, 5, 6, 7, 0, 1, 2], 0)', 4), ('search_rotated([4, 5, 6, 7, 0, 1, 2], 3)', -1), ('search_rotated([1], 0)', -1)])
lc(875, 'Koko Eating Bananas', 'koko-eating-bananas', 'm', 'Binary search on the answer', 'Try a speed in the middle and count the hours needed. Too slow: go faster. Fast enough: try slower.', r'''
def min_eating_speed(piles, h):
    low, high = 1, max(piles)
    while low < high:
        speed = (low + high) // 2
        hours = sum((pile + speed - 1) // speed for pile in piles)
        if hours <= h:
            high = speed
        else:
            low = speed + 1
    return low
''', [('min_eating_speed([3, 6, 7, 11], 8)', 4), ('min_eating_speed([30, 11, 23, 4, 20], 5)', 30), ('min_eating_speed([30, 11, 23, 4, 20], 6)', 23)])
lc(4, 'Median of Two Sorted Arrays', 'median-of-two-sorted-arrays', 'h', 'Binary search the cut in the shorter array', 'Cut both arrays so the left parts hold half of all items and every left item is at most every right item. Then the median comes from the four items around the cuts.', r'''
def find_median_sorted_arrays(nums1, nums2):
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    half = (m + n + 1) // 2
    low, high = 0, m
    while True:
        i = (low + high) // 2
        j = half - i
        left1 = nums1[i - 1] if i > 0 else float("-inf")
        right1 = nums1[i] if i < m else float("inf")
        left2 = nums2[j - 1] if j > 0 else float("-inf")
        right2 = nums2[j] if j < n else float("inf")
        if left1 <= right2 and left2 <= right1:
            if (m + n) % 2:
                return float(max(left1, left2))
            return (max(left1, left2) + min(right1, right2)) / 2
        if left1 > right2:
            high = i - 1
        else:
            low = i + 1
''', [('find_median_sorted_arrays([1, 3], [2])', 2.0), ('find_median_sorted_arrays([1, 2], [3, 4])', 2.5), ('find_median_sorted_arrays([], [1])', 1.0)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Binary search is the classic place for off by one bugs, so it is the perfect place to practise testing edge cases: empty lists, one item, the first and the last position. Two problems call an outside API (isBadVersion and guess), and the downloadable solutions inject a fake one, the same idea as a Mock.</p>'), kw=['LeetCode', 'binary search', 'edge cases', 'off by one', 'git bisect', 'fake API'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A test arranges inputs, acts by calling the code and asserts the result. A runner reports PASSED, FAILED or ERROR.',
    'unittest: TestCase classes, assertEqual, assertRaises, assertAlmostEqual, setUp for a fresh start, subTest for loops, skip.',
    'Mocks replace slow or outside dependencies: return_value, side_effect, assert_called_once_with, patch and patch.object.',
    'pytest: plain assert, fixtures, parametrize, approx, raises, tmp_path, monkeypatch, and detailed failure messages.',
    'Coverage shows which lines ran, not whether the checks are good. Hypothesis searches for inputs that break a rule.',
    'Test normal cases, edges, just outside the edges and every fixed bug. Many unit tests, fewer integration and end to end tests.'],
    '3.3 shows logging and debugging: finding out what a running program is doing.')}
{files('Three tasks: a tiny test runner, a currency converter tested with Mock, and a TestCase that must catch three buggy versions of a Stack.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In unittest, how must a test method be named?', ['check_anything', 'It must start with test', 'It must end with Test', 'Any name'], 1, 'Discovery by name.', 'The runner only runs methods whose names start with test.')
K.quiz('e', 'Which assertion checks that a block raises ValueError?', ['assertEqual(ValueError)', 'with self.assertRaises(ValueError):', 'assertTrue(ValueError)', 'assertIs(ValueError)'], 1, 'A context manager.', 'The with block passes only if ValueError is raised inside it.')
K.quiz('e', 'When does setUp run?', ['Once for the whole class', 'Before every single test method', 'After all tests', 'Only when a test fails'], 1, 'A fresh start.', 'Each test gets its own fresh set up.')
K.quiz('m', 'What is the difference between FAIL and ERROR in unittest?', ['None', 'FAIL: an assertion was false. ERROR: the test raised some other exception', 'ERROR is for skipped tests', 'FAIL means a syntax error'], 1, 'Wrong result or crash.', 'average([]) raised ZeroDivisionError, which counts as an ERROR.')
K.quiz('m', 'Why use assertAlmostEqual or pytest.approx for floats?', ['They are faster', 'Floats have tiny rounding errors, so 0.1 + 0.2 is not exactly 0.3', 'assertEqual does not work on floats', 'To round to integers'], 1, 'Rounding.', 'They allow a small tolerance.')
K.quiz('m', 'fake = Mock() and then fake.get.return_value = 5. What does fake.get("x") return?', ['None', '5', 'A Mock', '"x"'], 1, 'return_value.', 'The configured return value is returned for any arguments.')
K.quiz('m', 'What does @pytest.mark.parametrize do?', ['Runs a test in parallel', 'Runs the same test once for each set of arguments', 'Makes a fixture', 'Skips a test'], 1, 'Many inputs.', 'Each row becomes its own test in the report.')
K.quiz('m', 'A pytest test has a parameter named tmp_path. What does it get?', ['A string', 'A fresh temporary folder as a Path, made just for that test', 'The current folder', 'Nothing, it is an error'], 1, 'A built in fixture.', 'pytest sees the name and passes the fixture value.')
K.quiz('h', 'What does side_effect = [20, 3] on a Mock method do?', ['Returns [20, 3]', 'Returns 20 on the first call and 3 on the second', 'Raises an error', 'Calls 20 and 3'], 1, 'One answer per call.', 'An iterable side_effect gives the next value on each call.')
K.quiz('h', 'Your tests reach 100 % line coverage. Does that mean the code has no bugs?', ['Yes', 'No, every line ran, but some inputs may still give wrong results', 'Only for pure functions', 'Yes, if all tests pass'], 1, 'Coverage is not correctness.', 'Hypothesis found a float bug in fully covered code.')
K.quiz('h', 'Why is advice(client, city) easier to test than a function that creates its own WeatherClient inside?', ['It is shorter', 'The test can pass in a fake client (dependency injection)', 'It runs faster', 'It has no return value'], 1, 'Pass dependencies in.', 'A fake can be given without patching anything.')
K.quiz('x', 'In the style of an MIT 6.031 exam: valid percent is 0 to 100. Which set of inputs is best for boundary testing?', ['50 only', '0, 50, 100', '-1, 0, 50, 100, 101', '1, 2, 3, 4, 5'], 2, 'Edges and just outside.', 'Bugs live at the edges: test both sides of each boundary plus one normal value.')
K.quiz('x', 'In the style of a Stanford CS 108 exam: mutation testing changes / to // in your code and all tests still pass. What does that tell you?', ['The code is correct', 'The tests are too weak: no test notices that change', 'Mutation testing is broken', 'The change is harmless'], 1, 'Testing the tests.', 'A good suite kills mutants. A surviving mutant shows a missing test, such as discount(99, 10).')

K.calc('e', '17 of 19 lines run during the tests. What is the line coverage in percent (1 decimal place)?', '89.5', 'Lines run over total.', ['17 / 19 = 0.8947...', 'Times 100.', eq('89.5 %')], check=round(17 / 19 * 100, 1))
K.calc('e', 'A test suite has 8 tests and 1 fails. What percent pass?', '87.5', 'Passed over total.', ['8 &minus; 1 = 7 passed.', '7 / 8 = 0.875.', eq('87.5 %')], check=7 / 8 * 100)
K.calc('e', 'How many boundary value tests do you write for the range 0 to 100, including one normal value?', '5', 'a &minus; 1, a, b, b + 1, inside.', ['&minus;1 and 0.', '100 and 101.', eq('Plus 50: 5 tests')], check=5)
K.calc('m', 'What does discount(99, 10) return with the buggy // version?', '90', '99 &times; 10 // 100 first.', ['99 &times; 10 = 990.', '990 // 100 = 9.', eq('99 &minus; 9 = 90')], check=99 - 99 * 10 // 100)
K.calc('m', '3 settings each have 4 possible values. How many tests cover every combination?', '64', 'v<sup>k</sup>.', ['v = 4, k = 3.', '4 &times; 4 &times; 4.', eq('64')], check=4 ** 3)
K.calc('m', 'At most how many steps does binary search need for 1000 sorted items?', '10', '&lceil;log<sub>2</sub>(n + 1)&rceil;.', ['2<sup>9</sup> = 512 is too few.', '2<sup>10</sup> = 1024 &ge; 1001.', eq('10 steps')], check=10)
K.calc('m', 'min_eating_speed([3, 6, 7, 11], 8): how many hours does speed 4 take?', '8', 'Round each pile up.', ['3 / 4 and 6 / 4 round up to 1 and 2.', '7 / 4 and 11 / 4 round up to 2 and 3.', eq('1 + 2 + 2 + 3 = 8')], check=1 + 2 + 2 + 3)
K.calc('h', 'A bug needs one special value out of N = 1000. Chance in percent that 100 random tests hit it (1 decimal place)?', '9.5', '1 &minus; (1 &minus; 1/N)<sup>t</sup>.', ['(0.999)<sup>100</sup> &asymp; 0.905.', '1 &minus; 0.905 = 0.095.', eq('9.5 %')], check=round((1 - 0.999 ** 100) * 100, 1))
K.calc('h', 'git bisect over 5000 commits: at most how many test runs?', '13', 'Smallest power of 2 at or above 5000.', ['2<sup>12</sup> = 4096 is too small.', '2<sup>13</sup> = 8192.', eq('13 runs')], check=13)
K.calc('x', 'In the style of a CMU 17-214 exam: a suite of 400 unit tests takes 2 ms each, 40 integration tests take 0.5 s each and 5 end to end tests take 20 s each. What is the total time in seconds?', '120.8', 'Add the three layers.', ['400 &times; 0.002 = 0.8 s.', '40 &times; 0.5 = 20 s and 5 &times; 20 = 100 s.', eq('0.8 + 20 + 100 = 120.8 s')], check=round(400 * 0.002 + 40 * 0.5 + 5 * 20, 1))

K.assign('runner', 'e', 'A tiny test runner',
         '<p>Write <code>run_cases(func, cases)</code>. cases is a list of (args, expected) pairs, where args is a tuple. Call func(*args) for each case and return the list of indexes of the cases that fail. A case also fails if func raises an exception.</p>',
         '''
def run_cases(func, cases):
    failing = []
    for i in range(len(cases)):
        args, expected = cases[i]
        if func(*args) != expected:
            failing.append(i)
    return failing
''', [('run_cases(abs, [((-2,), 2), ((3,), 3), ((0,), 1)])', [2]), ('run_cases(int, [(("7",), 7), (("x",), 0)])', [1]), ('run_cases(max, [])', [])],
         '''
def run_cases(func, cases):
    failing = []
    for i in range(len(cases)):
        args, expected = cases[i]
        try:
            ok = func(*args) == expected
        except Exception:
            ok = False
        if not ok:
            failing.append(i)
    return failing
''', 'Wrap the call in try and except Exception, and treat an exception as a failure.', '<p>This is the heart of every test runner: call, compare, and never let one crashing test stop the others.</p>')
K.assign('converter', 'm', 'A converter tested with Mock',
         '<p>Write <code>convert(amount, currency, client)</code> that returns amount in rupees, rounded to 2 places, using <code>client.get_rate(currency)</code>. For "INR" return amount without calling the client at all. For a negative amount raise ValueError, also without calling the client. The tests use unittest.mock.Mock as the client.</p>',
         '''
from unittest.mock import Mock


def convert(amount, currency, client):
    return amount * client.get_rate(currency)


def try_negative():
    client = Mock()
    try:
        convert(-5, "USD", client)
    except ValueError:
        return "ValueError", client.get_rate.call_count
    return "no error", client.get_rate.call_count
''', [('(lambda m: (convert(10, "USD", m), m.get_rate.call_count))(Mock(**{"get_rate.return_value": 83.456}))', [834.56, 1]), ('(lambda m: (convert(50, "INR", m), m.get_rate.call_count))(Mock())', [50, 0]), ('(lambda m: (convert(2, "EUR", m), list(m.get_rate.call_args.args)))(Mock(**{"get_rate.return_value": 90}))', [180, ['EUR']]), ('try_negative()', ['ValueError', 0])],
         '''
from unittest.mock import Mock


def convert(amount, currency, client):
    if amount < 0:
        raise ValueError("amount cannot be negative")
    if currency == "INR":
        return amount
    rate = client.get_rate(currency)
    return round(amount * rate, 2)


def try_negative():
    client = Mock()
    try:
        convert(-5, "USD", client)
    except ValueError:
        return "ValueError", client.get_rate.call_count
    return "no error", client.get_rate.call_count
''', 'Check the amount first, then the INR case, and only then call client.get_rate once.', '<p>The mock records every call, so the tests can prove that INR never touches the network: call_count is 0.</p>')
K.assign('mutants', 'h', 'Write tests that catch buggy Stacks',
         '<p>Write a unittest TestCase <code>TestStack</code> with at least 3 tests. Each test makes its stack with <code>self.stack_class()</code>. Your tests must all pass for the correct <code>Stack</code>, and must FAIL for each buggy version: <code>QueueStack</code> (pop takes the oldest item), <code>SilentStack</code> (pop on an empty stack returns None instead of raising IndexError) and <code>EatingPeekStack</code> (peek removes the item). run_tests is the helper the checker uses.</p>',
         '''
import unittest


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def size(self):
        return len(self.items)


class QueueStack(Stack):
    def pop(self):
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop(0)


class SilentStack(Stack):
    def pop(self):
        if not self.items:
            return None
        return self.items.pop()


class EatingPeekStack(Stack):
    def peek(self):
        return self.items.pop()


class TestStack(unittest.TestCase):
    stack_class = Stack

    def test_push(self):
        s = self.stack_class()
        s.push(1)
        self.assertEqual(s.size(), 1)


def run_tests(case, stack_class):
    test_case = type("Run", (case,), {"stack_class": stack_class})
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_case)
    result = unittest.TestResult()
    suite.run(result)
    return result.testsRun, len(result.failures) + len(result.errors)
''', [('(lambda r: [r[0] >= 3, r[1]])(run_tests(TestStack, Stack))', [True, 0]), ('run_tests(TestStack, QueueStack)[1] > 0', True), ('run_tests(TestStack, SilentStack)[1] > 0', True), ('run_tests(TestStack, EatingPeekStack)[1] > 0', True)],
         '''
import unittest


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def size(self):
        return len(self.items)


class QueueStack(Stack):
    def pop(self):
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop(0)


class SilentStack(Stack):
    def pop(self):
        if not self.items:
            return None
        return self.items.pop()


class EatingPeekStack(Stack):
    def peek(self):
        return self.items.pop()


class TestStack(unittest.TestCase):
    stack_class = Stack

    def test_last_in_first_out(self):
        s = self.stack_class()
        s.push(1)
        s.push(2)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 1)

    def test_pop_empty_raises(self):
        s = self.stack_class()
        with self.assertRaises(IndexError):
            s.pop()

    def test_peek_keeps_item(self):
        s = self.stack_class()
        s.push("a")
        self.assertEqual(s.peek(), "a")
        self.assertEqual(s.size(), 1)


def run_tests(case, stack_class):
    test_case = type("Run", (case,), {"stack_class": stack_class})
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_case)
    result = unittest.TestResult()
    suite.run(result)
    return result.testsRun, len(result.failures) + len(result.errors)
''', 'One test per promise of a stack: last in first out, popping an empty stack raises IndexError, and peek does not remove the item.', '<p>This is mutation testing by hand: each buggy class is a "mutant", and a good suite fails on every one of them while passing on the real Stack.</p>')

K.must('unittest', 'class T(unittest.TestCase), methods test_..., assertEqual, assertTrue, assertIn, assertRaises (with), assertAlmostEqual, setUp, subTest, skip.')
K.must('Outcomes', 'PASSED, FAILED (assert false), ERROR (other exception). Read the last line. Tests must not depend on each other.')
K.must('Mocks', 'Mock().m.return_value, side_effect (list or exception), assert_called_once_with, call_count, patch and patch.object. Inject dependencies.')
K.must('pytest', 'test_ functions with plain assert, fixtures by parameter name, parametrize, approx, raises(match=), tmp_path, monkeypatch, -v, -k.')
K.must('Strategy', 'Edges and just outside, every fixed bug, coverage is not correctness, property tests with Hypothesis, the test pyramid, TDD.')

T = K.topic(
    slug='py-testing', topic='py-testing', step=(3, 'Professional code: style, testing and logging', 'py-a3', 'Write code others can read, prove it works with tests, and find problems fast with logging and debugging.', 'Advanced'),
    title='Testing: unittest, pytest and mocks', short='Testing', badge='3.2', minutes=80,
    lead='Prove that your code works, and keep it working. Learn unittest test cases, fixtures and subTest, reading failures, mocks and patch, pytest with fixtures, parametrize and approx, coverage, property based testing with Hypothesis, and what to test.',
    desc='why test, Arrange Act Assert, unittest TestCase and assertions, setUp and tearDown, subTest, skip, PASSED, FAILED and ERROR, unittest.mock Mock, return_value, side_effect, assert_called_once_with, patch and patch.object, dependency injection, pytest fixtures, parametrize, approx, raises, tmp_path, monkeypatch, coverage, Hypothesis, the test pyramid, boundary values, TDD, mutation testing.',
    summary='unittest, fixtures, failures and errors, mocks, pytest, coverage, property based testing, test strategy.',
    keywords=['testing', 'unittest', 'pytest', 'mock', 'patch', 'fixture', 'parametrize', 'coverage', 'Hypothesis', 'TDD', 'PCPP'],
    recap='<p>Write small, independent tests for normal cases and edges, mock what you cannot control, and let pytest run them every time you change code.</p>',
    added='2026-11-07', leet=leet_items())
