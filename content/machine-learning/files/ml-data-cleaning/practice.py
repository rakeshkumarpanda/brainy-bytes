# 3.1 Data cleaning: missing values, types, outliers and joins
# Practice tasks. Fill in each function, then run this file.
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
# Hint: Loop over the columns. Inside, loop over the values and count the ones that are None.

def count_missing(table):
    # your code here
    pass


# ================================================================== task 2: Fill holes with the median
# Write fill_median(values) that replaces every None in a list of numbers with the median of the
# known numbers. Return the new list. Do not use statistics or numpy.
# Hint: Sort the known values. Odd count: take the middle one. Even count: average the two middle
# ones. Then rebuild the list.

def fill_median(values):
    # your code here
    pass


# ================================================================== task 3: Find outliers with the IQR rule
# Write iqr_outliers(values) that returns the sorted list of outliers using the 1.5 IQR rule.
# Compute Q1 and Q3 with the pandas linear method: position = (n − 1) × q, then move between the two
# nearest sorted values.
# Hint: Write a small quantile helper first. Then compute the fences and keep the values outside
# them.

def iqr_outliers(values):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Count missing values per column", [('count_missing({"age": [25, None, 30], "city": ["Delhi", None, None]})', {'age': 1, 'city': 2}), ('count_missing({"x": [1, 2]})', {'x': 0})]))
    results.append(check("Task 2: Fill holes with the median", [('fill_median([4, None, 8, 6])', [4, 6, 8, 6]), ('fill_median([3, 9, None, 5, 100])', [3, 9, 7.0, 5, 100]), ('fill_median([None, 2])', [2, 2])]))
    results.append(check("Task 3: Find outliers with the IQR rule", [('iqr_outliers([32, 35, 36, 38, 40, 41, 43, 45, 47, 150])', [150]), ('iqr_outliers([1, 2, 3, 4, 5])', []), ('iqr_outliers([2, 5, 30, 32, 33, 35, 36, 38, 40, 90])', [2, 5, 90])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
