# 3.1 Data cleaning: missing values, types, outliers and joins
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


# ================================================================== 2882. Drop Duplicate Rows (Easy)
# https://leetcode.com/problems/drop-duplicate-rows/
# Pattern: pandas: drop_duplicates on one column
# Idea: Keep the first row for each email. drop_duplicates with subset set to the email column does
# exactly that.

import pandas as pd


def dropDuplicateEmails(customers):
    return customers.drop_duplicates(subset=["email"], keep="first")


# ================================================================== 2883. Drop Missing Data (Easy)
# https://leetcode.com/problems/drop-missing-data/
# Pattern: pandas: dropna on one column
# Idea: Remove rows where the name is missing. dropna with subset set to the name column keeps rows
# with holes elsewhere.

def dropMissingData(students):
    return students.dropna(subset=["name"])


# ================================================================== 2885. Rename Columns (Easy)
# https://leetcode.com/problems/rename-columns/
# Pattern: pandas: rename
# Idea: Give rename a dictionary from old names to new names.

def renameColumns(students):
    return students.rename(columns={"id": "student_id", "first": "first_name", "last": "last_name", "age": "age_in_years"})


# ================================================================== 2886. Change Data Type (Easy)
# https://leetcode.com/problems/change-data-type/
# Pattern: pandas: astype
# Idea: The grade column holds floats like 73.0. astype(int) turns them into whole numbers.

def changeDatatype(students):
    students["grade"] = students["grade"].astype(int)
    return students


# ================================================================== 2887. Fill Missing Data (Easy)
# https://leetcode.com/problems/fill-missing-data/
# Pattern: pandas: fillna with a constant
# Idea: A missing quantity here means none in stock, so fill it with 0.

def fillMissingValues(products):
    products["quantity"] = products["quantity"].fillna(0)
    return products


# ================================================================== 2890. Reshape Data: Melt (Easy)
# https://leetcode.com/problems/reshape-data-melt/
# Pattern: pandas: melt wide to long
# Idea: Keep product as the id column. Every quarter column becomes rows with a quarter name and a
# sales value.

def meltTable(report):
    return report.melt(id_vars=["product"], var_name="quarter", value_name="sales")


# ================================================================== 1667. Fix Names in a Table (Easy)
# https://leetcode.com/problems/fix-names-in-a-table/
# Pattern: pandas: string cleaning
# Idea: str.capitalize makes the first letter upper case and the rest lower case. Then sort by
# user_id.

def fix_names(users):
    users["name"] = users["name"].str.capitalize()
    return users.sort_values("user_id")


# ================================================================== 1517. Find Users With Valid E-Mails (Easy)
# https://leetcode.com/problems/find-users-with-valid-e-mails/
# Pattern: pandas: str.match with a pattern
# Idea: The name must start with a letter and use only letters, digits, underscore, dot or dash,
# followed by exactly @leetcode.com.

def valid_emails(users):
    pattern = "^[A-Za-z][A-Za-z0-9_.-]*@leetcode[.]com$"
    return users[users["mail"].str.match(pattern)]


# ================================================================== 196. Delete Duplicate Emails (Easy)
# https://leetcode.com/problems/delete-duplicate-emails/
# Pattern: pandas: sort, then drop duplicates in place
# Idea: Sort by id so the smallest id comes first, then drop later copies of each email. LeetCode
# checks the same table, so change it in place.

def delete_duplicate_emails(person):
    person.sort_values(by="id", inplace=True)
    person.drop_duplicates(subset="email", keep="first", inplace=True)


def after_delete(person):
    delete_duplicate_emails(person)
    return person["id"].tolist()


# ================================================================== 183. Customers Who Never Order (Easy)
# https://leetcode.com/problems/customers-who-never-order/
# Pattern: pandas: anti join with isin
# Idea: Keep customers whose id is not in the customerId column of orders. The tilde sign means
# "not".

def find_customers(customers, orders):
    never = customers[~customers["id"].isin(orders["customerId"])]
    return never[["name"]].rename(columns={"name": "Customers"})


if __name__ == "__main__":
    results = []
    results.append(check("2882. Drop Duplicate Rows", [('dropDuplicateEmails(pd.DataFrame({"customer_id": [1, 2, 3], "email": ["a@x.com", "b@x.com", "a@x.com"]}))["customer_id"].tolist()', [1, 2])]))
    results.append(check("2883. Drop Missing Data", [('dropMissingData(pd.DataFrame({"student_id": [32, 217, 779], "name": ["Piper", None, "Georgia"], "age": [5, 19, 20]}))["student_id"].tolist()', [32, 779])]))
    results.append(check("2885. Rename Columns", [('list(renameColumns(pd.DataFrame({"id": [1], "first": ["Mason"], "last": ["King"], "age": [6]})).columns)', ['student_id', 'first_name', 'last_name', 'age_in_years'])]))
    results.append(check("2886. Change Data Type", [('changeDatatype(pd.DataFrame({"student_id": [1, 2], "grade": [73.0, 87.0]}))["grade"].tolist()', [73, 87])]))
    results.append(check("2887. Fill Missing Data", [('fillMissingValues(pd.DataFrame({"name": ["Wristwatch", "WirelessEarbuds"], "quantity": [None, 32]}))["quantity"].tolist()', [0.0, 32.0])]))
    results.append(check("2890. Reshape Data: Melt", [('meltTable(pd.DataFrame({"product": ["Umbrella"], "quarter_1": [417], "quarter_2": [224]})).values.tolist()', [['Umbrella', 'quarter_1', 417], ['Umbrella', 'quarter_2', 224]])]))
    results.append(check("1667. Fix Names in a Table", [('fix_names(pd.DataFrame({"user_id": [2, 1], "name": ["bOB", "aLice"]}))["name"].tolist()', ['Alice', 'Bob'])]))
    results.append(check("1517. Find Users With Valid E-Mails", [('valid_emails(pd.DataFrame({"user_id": [1, 2, 3, 4], "mail": ["winston@leetcode.com", "jonathanisgreat", "_annabelle@leetcode.com", "sally.come@leetcode.com"]}))["user_id"].tolist()', [1, 4])]))
    results.append(check("196. Delete Duplicate Emails", [('after_delete(pd.DataFrame({"id": [3, 1, 2], "email": ["john@x.com", "john@x.com", "bob@x.com"]}))', [1, 2])]))
    results.append(check("183. Customers Who Never Order", [('find_customers(pd.DataFrame({"id": [1, 2, 3, 4], "name": ["Joe", "Henry", "Sam", "Max"]}), pd.DataFrame({"id": [1, 2], "customerId": [3, 1]}))["Customers"].tolist()', ['Henry', 'Max'])]))
    if all(results):
        print("Every solution passes its tests.")
