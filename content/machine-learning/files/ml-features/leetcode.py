# 3.2 Features: encoding, scaling, engineering and selection
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


# ================================================================== 1873. Calculate Special Bonus (Easy)
# https://leetcode.com/problems/calculate-special-bonus/
# Pattern: pandas: a feature from a rule
# Idea: The bonus is the full salary when the id is odd and the name does not start with M,
# otherwise 0. Build the column with a boolean mask, then sort by id.

import pandas as pd


def calculate_special_bonus(employees):
    rule = (employees["employee_id"] % 2 == 1) & (~employees["name"].str.startswith("M"))
    employees["bonus"] = employees["salary"].where(rule, 0)
    return employees[["employee_id", "bonus"]].sort_values("employee_id")


# ================================================================== 1757. Recyclable and Low Fat Products (Easy)
# https://leetcode.com/problems/recyclable-and-low-fat-products/
# Pattern: pandas: combine two masks
# Idea: Keep rows where both flags are "Y". Use & between the two conditions and wrap each in
# brackets.

def find_products(products):
    keep = (products["low_fats"] == "Y") & (products["recyclable"] == "Y")
    return products[keep][["product_id"]]


# ================================================================== 595. Big Countries (Easy)
# https://leetcode.com/problems/big-countries/
# Pattern: pandas: an "or" mask
# Idea: A country is big if its area is at least 3,000,000 or its population is at least 25,000,000.
# Use | for "or".

def big_countries(world):
    big = (world["area"] >= 3000000) | (world["population"] >= 25000000)
    return world[big][["name", "population", "area"]]


# ================================================================== 178. Rank Scores (Medium)
# https://leetcode.com/problems/rank-scores/
# Pattern: pandas: dense rank as a feature
# Idea: rank(method="dense", ascending=False) gives equal scores the same rank with no gaps. Sort by
# score from high to low.

def order_scores(scores):
    scores["rank"] = scores["score"].rank(method="dense", ascending=False).astype(int)
    return scores[["score", "rank"]].sort_values("score", ascending=False)


# ================================================================== 2356. Number of Unique Subjects Taught by Each Teacher (Easy)
# https://leetcode.com/problems/number-of-unique-subjects-taught-by-each-teacher/
# Pattern: pandas: groupby with nunique
# Idea: Group by teacher and count the different subject ids. reset_index turns the result back into
# a table.

def count_unique_subjects(teacher):
    result = teacher.groupby("teacher_id")["subject_id"].nunique().reset_index()
    return result.rename(columns={"subject_id": "cnt"})


# ================================================================== 1741. Find Total Time Spent by Each Employee (Easy)
# https://leetcode.com/problems/find-total-time-spent-by-each-employee/
# Pattern: pandas: a computed column, then groupby sum
# Idea: Make a column out_time minus in_time, then add it up for each day and employee.

def total_time(employees):
    employees["total_time"] = employees["out_time"] - employees["in_time"]
    result = employees.groupby(["event_day", "emp_id"])["total_time"].sum().reset_index()
    return result.rename(columns={"event_day": "day"})


# ================================================================== 1484. Group Sold Products By The Date (Easy)
# https://leetcode.com/problems/group-sold-products-by-the-date/
# Pattern: pandas: groupby with two aggregates
# Idea: For each date, count the different products and join their sorted names with commas.

def categorize_products(activities):
    rows = []
    for day, group in activities.groupby("sell_date"):
        names = sorted(group["product"].unique())
        rows.append([day, len(names), ",".join(names)])
    return pd.DataFrame(rows, columns=["sell_date", "num_sold", "products"])


if __name__ == "__main__":
    results = []
    results.append(check("1873. Calculate Special Bonus", [('calculate_special_bonus(pd.DataFrame({"employee_id": [2, 3, 7, 8, 9], "name": ["Meir", "Michael", "Addilyn", "Juan", "Kannon"], "salary": [3000, 3800, 7400, 6100, 7700]}))["bonus"].tolist()', [0, 0, 7400, 0, 7700])]))
    results.append(check("1757. Recyclable and Low Fat Products", [('find_products(pd.DataFrame({"product_id": [0, 1, 2, 3, 4], "low_fats": ["Y", "Y", "N", "Y", "N"], "recyclable": ["N", "Y", "Y", "Y", "N"]}))["product_id"].tolist()', [1, 3])]))
    results.append(check("595. Big Countries", [('big_countries(pd.DataFrame({"name": ["Afghanistan", "Albania", "Algeria"], "population": [25500100, 2831741, 37100000], "area": [652230, 28748, 2381741]}))["name"].tolist()', ['Afghanistan', 'Algeria'])]))
    results.append(check("178. Rank Scores", [('order_scores(pd.DataFrame({"id": [1, 2, 3, 4, 5, 6], "score": [3.5, 3.65, 4.0, 3.85, 4.0, 3.65]}))["rank"].tolist()', [1, 1, 2, 3, 3, 4])]))
    results.append(check("2356. Number of Unique Subjects Taught by Each Teacher", [('count_unique_subjects(pd.DataFrame({"teacher_id": [1, 1, 1, 2, 2, 2, 2], "subject_id": [2, 2, 3, 1, 2, 3, 4], "dept_id": [3, 4, 3, 1, 1, 1, 1]}))["cnt"].tolist()', [2, 4])]))
    results.append(check("1741. Find Total Time Spent by Each Employee", [('total_time(pd.DataFrame({"emp_id": [1, 1, 1, 2, 2], "event_day": ["2020-11-28", "2020-11-28", "2020-12-03", "2020-11-28", "2020-12-09"], "in_time": [4, 55, 1, 3, 47], "out_time": [32, 200, 42, 33, 74]}))["total_time"].tolist()', [173, 30, 41, 27])]))
    results.append(check("1484. Group Sold Products By The Date", [('categorize_products(pd.DataFrame({"sell_date": ["2020-05-30", "2020-06-01", "2020-06-02", "2020-05-30", "2020-06-01", "2020-06-02", "2020-05-30"], "product": ["Headphone", "Pencil", "Mask", "Basketball", "Bible", "Mask", "T-Shirt"]})).values.tolist()', [['2020-05-30', 3, 'Basketball,Headphone,T-Shirt'], ['2020-06-01', 2, 'Bible,Pencil'], ['2020-06-02', 1, 'Mask']])]))
    if all(results):
        print("Every solution passes its tests.")
