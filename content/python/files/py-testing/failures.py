# 3.2 Testing: unittest, pytest and mocks
# Example "failures" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
