# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
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


# ================================================================== task 1: Column averages with NumPy
# Write column_means(table) that takes a list of rows (all the same length) and returns a list with
# the average of each column. Use NumPy with axis=0 and convert the answer back with .tolist().
# Hint: np.array(table) makes the 2D array. mean(axis=0) goes down the rows. .tolist() turns the
# result into a plain list.

import numpy as np


def column_means(table):
    # your code here
    pass


# ================================================================== task 2: Standard scaling of a list
# Write standardise(values) that returns each value as (x − mean) / std, rounded to 3 decimals,
# using the NumPy standard deviation (divide by n). If std is 0, return a list of zeros.
# Hint: Make an array, find mean() and std(). Guard against std = 0. Subtract and divide on the
# whole array at once.

import numpy as np


def standardise(values):
    # your code here
    pass


# ================================================================== task 3: Average per city with pandas
# Write city_average(rows). rows is a list of dictionaries such as {"city": "Pune", "temp": 31}.
# Return a dictionary from each city to its average temperature rounded to 1 decimal. Use pandas
# groupby.
# Hint: pd.DataFrame(rows) turns a list of dicts into a table. groupby("city")["temp"].mean() gives
# a Series. Loop over .items() to build the dict.

import pandas as pd


def city_average(rows):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Column averages with NumPy", [('column_means([[1, 2], [3, 4]])', [2.0, 3.0]), ('column_means([[10, 0, 5]])', [10.0, 0.0, 5.0]), ('column_means([[1], [2], [6]])', [3.0])]))
    results.append(check("Task 2: Standard scaling of a list", [('standardise([2, 4, 6])', [-1.225, 0.0, 1.225]), ('standardise([5, 5, 5])', [0.0, 0.0, 0.0]), ('standardise([0, 10])', [-1.0, 1.0])]))
    results.append(check("Task 3: Average per city with pandas", [('city_average([{"city": "Pune", "temp": 31}, {"city": "Pune", "temp": 29}, {"city": "Delhi", "temp": 40}])', {'Delhi': 40.0, 'Pune': 30.0}), ('city_average([{"city": "A", "temp": 1}, {"city": "A", "temp": 2}])', {'A': 1.5})]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
