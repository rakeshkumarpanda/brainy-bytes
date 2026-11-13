# 3.1 Data cleaning: missing values, types, outliers and joins
# Model solutions. Try practice.py first.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Count missing values per column
# A table is a dictionary of column name to list of values, where None means missing. Write
# count_missing(table) that returns a dictionary of column name to the number of None values.
# Why it works: This is what df.isna().sum() does, written by hand.

def count_missing(table):
    result = {}
    for name in table:
        count = 0
        for value in table[name]:
            if value is None:
                count = count + 1
        result[name] = count
    return result


# ================================================================== task 2: Fill holes with the median
# Write fill_median(values) that replaces every None in a list of numbers with the median of the
# known numbers. Return the new list. Do not use statistics or numpy.
# Why it works: In a real project you would compute the median on the training rows and reuse it for
# the test rows.

def fill_median(values):
    known = sorted([v for v in values if v is not None])
    n = len(known)
    if n % 2 == 1:
        median = known[n // 2]
    else:
        median = (known[n // 2 - 1] + known[n // 2]) / 2
    result = []
    for v in values:
        if v is None:
            result.append(median)
        else:
            result.append(v)
    return result


# ================================================================== task 3: Find outliers with the IQR rule
# Write iqr_outliers(values) that returns the sorted list of outliers using the 1.5 IQR rule.
# Compute Q1 and Q3 with the pandas linear method: position = (n − 1) × q, then move between the two
# nearest sorted values.
# Why it works: Check your helper against pandas: pd.Series(values).quantile(0.25) uses the same
# linear method.

def quantile(sorted_values, q):
    position = (len(sorted_values) - 1) * q
    low = int(position)
    high = min(low + 1, len(sorted_values) - 1)
    part = position - low
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * part


def iqr_outliers(values):
    s = sorted(values)
    q1 = quantile(s, 0.25)
    q3 = quantile(s, 0.75)
    iqr = q3 - q1
    low_fence = q1 - 1.5 * iqr
    high_fence = q3 + 1.5 * iqr
    result = []
    for v in s:
        if v < low_fence or v > high_fence:
            result.append(v)
    return result


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Count missing values per column", [('count_missing({"age": [25, None, 30], "city": ["Delhi", None, None]})', {'age': 1, 'city': 2}), ('count_missing({"x": [1, 2]})', {'x': 0})]))
    results.append(check("Task 2: Fill holes with the median", [('fill_median([4, None, 8, 6])', [4, 6, 8, 6]), ('fill_median([3, 9, None, 5, 100])', [3, 9, 7.0, 5, 100]), ('fill_median([None, 2])', [2, 2])]))
    results.append(check("Task 3: Find outliers with the IQR rule", [('iqr_outliers([32, 35, 36, 38, 40, 41, 43, 45, 47, 150])', [150]), ('iqr_outliers([1, 2, 3, 4, 5])', []), ('iqr_outliers([2, 5, 30, 32, 33, 35, 36, 38, 40, 90])', [2, 5, 90])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
