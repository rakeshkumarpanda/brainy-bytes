# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
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


# ================================================================== 2877. Create a DataFrame from List (Easy)
# https://leetcode.com/problems/create-a-dataframe-from-list/
# Pattern: pandas: build a DataFrame
# Idea: Pass the list of rows and the column names student_id and age to pd.DataFrame.

import pandas as pd


def createDataframe(student_data):
    return pd.DataFrame(student_data, columns=["student_id", "age"])


# ================================================================== 2878. Get the Size of a DataFrame (Easy)
# https://leetcode.com/problems/get-the-size-of-a-dataframe/
# Pattern: pandas: shape
# Idea: df.shape is (rows, columns). Return it as a list.

def getDataframeSize(players):
    return [players.shape[0], players.shape[1]]


# ================================================================== 2879. Display the First Three Rows (Easy)
# https://leetcode.com/problems/display-the-first-three-rows/
# Pattern: pandas: head
# Idea: head(3) returns the first three rows.

def selectFirstRows(employees):
    return employees.head(3)


# ================================================================== 2880. Select Data (Easy)
# https://leetcode.com/problems/select-data/
# Pattern: pandas: filter rows, pick columns
# Idea: Keep rows where student_id is 101, then keep only the name and age columns.

def selectData(students):
    return students[students["student_id"] == 101][["name", "age"]]


# ================================================================== 2881. Create a New Column (Easy)
# https://leetcode.com/problems/create-a-new-column/
# Pattern: pandas: a computed column
# Idea: A new column is made by assigning to df["bonus"]. The maths runs on the whole column at
# once.

def createBonusColumn(employees):
    employees["bonus"] = employees["salary"] * 2
    return employees


# ================================================================== 2884. Modify Columns (Easy)
# https://leetcode.com/problems/modify-columns/
# Pattern: pandas: change a column in place
# Idea: Multiply the salary column by 2 and store it back.

def modifySalaryColumn(employees):
    employees["salary"] = employees["salary"] * 2
    return employees


# ================================================================== 2888. Reshape Data: Concatenate (Easy)
# https://leetcode.com/problems/reshape-data-concatenate/
# Pattern: pandas: stack tables
# Idea: pd.concat puts the second table under the first.

def concatenateTables(df1, df2):
    return pd.concat([df1, df2])


# ================================================================== 2889. Reshape Data: Pivot (Easy)
# https://leetcode.com/problems/reshape-data-pivot/
# Pattern: pandas: pivot long data into a wide table
# Idea: pivot(index="month", columns="city", values="temperature") makes one row per month and one
# column per city.

def pivotTable(weather):
    return weather.pivot(index="month", columns="city", values="temperature")


# ================================================================== 2891. Method Chaining (Easy)
# https://leetcode.com/problems/method-chaining/
# Pattern: pandas: chain filter, sort and select
# Idea: Filter weight > 100, sort by weight from heavy to light, keep the name column. Writing it as
# one chain reads like a sentence.

def findHeavyAnimals(animals):
    return animals[animals["weight"] > 100].sort_values("weight", ascending=False)[["name"]]


# ================================================================== 1572. Matrix Diagonal Sum (Easy)
# https://leetcode.com/problems/matrix-diagonal-sum/
# Pattern: 2D indexing (NumPy style rows and columns)
# Idea: Add mat[i][i] and mat[i][n − 1 − i] for every row. When n is odd, the centre was added
# twice, so take it away once.

def diagonal_sum(mat):
    n = len(mat)
    total = 0
    for i in range(n):
        total = total + mat[i][i] + mat[i][n - 1 - i]
    if n % 2 == 1:
        total = total - mat[n // 2][n // 2]
    return total


if __name__ == "__main__":
    results = []
    results.append(check("2877. Create a DataFrame from List", [('createDataframe([[1, 15], [2, 11]]).values.tolist()', [[1, 15], [2, 11]]), ('list(createDataframe([[1, 15]]).columns)', ['student_id', 'age'])]))
    results.append(check("2878. Get the Size of a DataFrame", [('getDataframeSize(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))', [3, 2])]))
    results.append(check("2879. Display the First Three Rows", [('selectFirstRows(pd.DataFrame({"x": [1, 2, 3, 4, 5]}))["x"].tolist()', [1, 2, 3])]))
    results.append(check("2880. Select Data", [('selectData(pd.DataFrame({"student_id": [101, 53], "name": ["Ulysses", "William"], "age": [13, 10]})).values.tolist()', [['Ulysses', 13]])]))
    results.append(check("2881. Create a New Column", [('createBonusColumn(pd.DataFrame({"name": ["Piper"], "salary": [4548]}))["bonus"].tolist()', [9096])]))
    results.append(check("2884. Modify Columns", [('modifySalaryColumn(pd.DataFrame({"name": ["Jack", "Piper"], "salary": [19666, 74754]}))["salary"].tolist()', [39332, 149508])]))
    results.append(check("2888. Reshape Data: Concatenate", [('concatenateTables(pd.DataFrame({"id": [1, 2]}), pd.DataFrame({"id": [3]}))["id"].tolist()', [1, 2, 3])]))
    results.append(check("2889. Reshape Data: Pivot", [('pivotTable(pd.DataFrame({"city": ["A", "B", "A", "B"], "month": ["Jan", "Jan", "Feb", "Feb"], "temperature": [1, 2, 3, 4]})).loc["Feb"].tolist()', [3, 4])]))
    results.append(check("2891. Method Chaining", [('findHeavyAnimals(pd.DataFrame({"name": ["Tatiana", "Khaled", "Alex", "Jonathan"], "weight": [464, 41, 328, 463]}))["name"].tolist()', ['Tatiana', 'Jonathan', 'Alex'])]))
    results.append(check("1572. Matrix Diagonal Sum", [('diagonal_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', 25), ('diagonal_sum([[5]])', 5)]))
    if all(results):
        print("Every solution passes its tests.")
