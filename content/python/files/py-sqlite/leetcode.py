# 6.3 Databases with sqlite3 and SQL
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


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


# ================================================================== 175. Combine Two Tables (Easy)
# https://leetcode.com/problems/combine-two-tables/
# Pattern: LEFT JOIN keeps people without an address
# Idea: Every person must appear, even without an address, so use LEFT JOIN. Missing columns come
# back as None.

import sqlite3


def combine_two_tables(person, address):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Person (personId INTEGER, lastName TEXT, firstName TEXT)")
    db.execute("CREATE TABLE Address (addressId INTEGER, personId INTEGER, city TEXT, state TEXT)")
    db.executemany("INSERT INTO Person VALUES (?, ?, ?)", person)
    db.executemany("INSERT INTO Address VALUES (?, ?, ?, ?)", address)
    rows = db.execute("""
        SELECT p.firstName, p.lastName, a.city, a.state
        FROM Person p LEFT JOIN Address a ON p.personId = a.personId
        ORDER BY p.personId""").fetchall()
    db.close()
    return rows


# ================================================================== 182. Duplicate Emails (Easy)
# https://leetcode.com/problems/duplicate-emails/
# Pattern: GROUP BY with HAVING COUNT
# Idea: Group the rows by email and keep the groups that have more than one row.

import sqlite3


def duplicate_emails(person):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Person (id INTEGER, email TEXT)")
    db.executemany("INSERT INTO Person VALUES (?, ?)", person)
    rows = db.execute("SELECT email FROM Person GROUP BY email HAVING COUNT(*) > 1 ORDER BY email").fetchall()
    db.close()
    return [row[0] for row in rows]


# ================================================================== 183. Customers Who Never Order (Easy)
# https://leetcode.com/problems/customers-who-never-order/
# Pattern: NOT IN a subquery, or LEFT JOIN ... IS NULL
# Idea: Find customers whose id is not in the list of customer ids of the orders.

import sqlite3


def never_ordered(customers, orders):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Customers (id INTEGER, name TEXT)")
    db.execute("CREATE TABLE Orders (id INTEGER, customerId INTEGER)")
    db.executemany("INSERT INTO Customers VALUES (?, ?)", customers)
    db.executemany("INSERT INTO Orders VALUES (?, ?)", orders)
    rows = db.execute("""
        SELECT c.name FROM Customers c
        LEFT JOIN Orders o ON o.customerId = c.id
        WHERE o.id IS NULL ORDER BY c.id""").fetchall()
    db.close()
    return [row[0] for row in rows]


# ================================================================== 197. Rising Temperature (Easy)
# https://leetcode.com/problems/rising-temperature/
# Pattern: Join the table with itself on yesterday
# Idea: Pair each day with the day before using DATE(day, '-1 day'), then keep pairs where the
# temperature went up.

import sqlite3


def rising_temperature(weather):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Weather (id INTEGER, recordDate TEXT, temperature INTEGER)")
    db.executemany("INSERT INTO Weather VALUES (?, ?, ?)", weather)
    rows = db.execute("""
        SELECT today.id FROM Weather today
        JOIN Weather yesterday ON yesterday.recordDate = DATE(today.recordDate, '-1 day')
        WHERE today.temperature > yesterday.temperature ORDER BY today.id""").fetchall()
    db.close()
    return [row[0] for row in rows]


# ================================================================== 196. Delete Duplicate Emails (Easy)
# https://leetcode.com/problems/delete-duplicate-emails/
# Pattern: DELETE rows that are not the smallest id
# Idea: Keep MIN(id) of each email and delete every other row.

import sqlite3


def delete_duplicate_emails(person):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Person (id INTEGER, email TEXT)")
    db.executemany("INSERT INTO Person VALUES (?, ?)", person)
    with db:
        db.execute("DELETE FROM Person WHERE id NOT IN (SELECT MIN(id) FROM Person GROUP BY email)")
    rows = db.execute("SELECT id, email FROM Person ORDER BY id").fetchall()
    db.close()
    return rows


# ================================================================== 176. Second Highest Salary (Medium)
# https://leetcode.com/problems/second-highest-salary/
# Pattern: DISTINCT, ORDER BY, LIMIT 1 OFFSET 1 inside a subquery
# Idea: The outer SELECT turns "no row" into NULL, which is None in Python.

import sqlite3


def second_highest_salary(employee):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Employee (id INTEGER, salary INTEGER)")
    db.executemany("INSERT INTO Employee VALUES (?, ?)", employee)
    row = db.execute("""
        SELECT (SELECT DISTINCT salary FROM Employee
                ORDER BY salary DESC LIMIT 1 OFFSET 1)""").fetchone()
    db.close()
    return row[0]


# ================================================================== 178. Rank Scores (Medium)
# https://leetcode.com/problems/rank-scores/
# Pattern: The DENSE_RANK window function
# Idea: DENSE_RANK() OVER (ORDER BY score DESC) gives equal scores the same rank and leaves no gaps
# after ties.

import sqlite3


def rank_scores(scores):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Scores (id INTEGER, score REAL)")
    db.executemany("INSERT INTO Scores VALUES (?, ?)", scores)
    rows = db.execute("""
        SELECT score, DENSE_RANK() OVER (ORDER BY score DESC) AS rank
        FROM Scores ORDER BY score DESC""").fetchall()
    db.close()
    return rows


# ================================================================== 184. Department Highest Salary (Medium)
# https://leetcode.com/problems/department-highest-salary/
# Pattern: Join with the maximum of each department
# Idea: A subquery finds MAX(salary) per department. Join it back to keep every employee who earns
# that much, ties included.

import sqlite3


def department_highest_salary(employee, department):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Employee (id INTEGER, name TEXT, salary INTEGER, departmentId INTEGER)")
    db.execute("CREATE TABLE Department (id INTEGER, name TEXT)")
    db.executemany("INSERT INTO Employee VALUES (?, ?, ?, ?)", employee)
    db.executemany("INSERT INTO Department VALUES (?, ?)", department)
    rows = db.execute("""
        SELECT d.name, e.name, e.salary
        FROM Employee e
        JOIN Department d ON d.id = e.departmentId
        JOIN (SELECT departmentId, MAX(salary) AS top FROM Employee GROUP BY departmentId) m
          ON m.departmentId = e.departmentId AND m.top = e.salary
        ORDER BY d.name, e.name""").fetchall()
    db.close()
    return rows


# ================================================================== 185. Department Top Three Salaries (Hard)
# https://leetcode.com/problems/department-top-three-salaries/
# Pattern: DENSE_RANK per department with PARTITION BY
# Idea: PARTITION BY departmentId restarts the ranking in each department. Keep rank 3 or better.
# Ties share a rank.

import sqlite3


def top_three_salaries(employee, department):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Employee (id INTEGER, name TEXT, salary INTEGER, departmentId INTEGER)")
    db.execute("CREATE TABLE Department (id INTEGER, name TEXT)")
    db.executemany("INSERT INTO Employee VALUES (?, ?, ?, ?)", employee)
    db.executemany("INSERT INTO Department VALUES (?, ?)", department)
    rows = db.execute("""
        SELECT d.name, r.name, r.salary FROM (
            SELECT name, salary, departmentId,
                   DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) AS place
            FROM Employee) r
        JOIN Department d ON d.id = r.departmentId
        WHERE r.place <= 3
        ORDER BY d.name, r.salary DESC, r.name""").fetchall()
    db.close()
    return rows


# ================================================================== 262. Trips and Users (Hard)
# https://leetcode.com/problems/trips-and-users/
# Pattern: Join twice to the users table, then average a condition
# Idea: Join Users once for the client and once for the driver and keep trips where neither is
# banned. AVG(status != 'completed') is the share of cancelled trips, because a true test counts as
# 1.

import sqlite3


def cancellation_rate(trips, users):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Trips (id INTEGER, client_id INTEGER, driver_id INTEGER, city_id INTEGER, status TEXT, request_at TEXT)")
    db.execute("CREATE TABLE Users (users_id INTEGER, banned TEXT, role TEXT)")
    db.executemany("INSERT INTO Trips VALUES (?, ?, ?, ?, ?, ?)", trips)
    db.executemany("INSERT INTO Users VALUES (?, ?, ?)", users)
    rows = db.execute("""
        SELECT t.request_at, ROUND(AVG(t.status != 'completed'), 2)
        FROM Trips t
        JOIN Users c ON c.users_id = t.client_id AND c.banned = 'No'
        JOIN Users d ON d.users_id = t.driver_id AND d.banned = 'No'
        WHERE t.request_at BETWEEN '2013-10-01' AND '2013-10-03'
        GROUP BY t.request_at ORDER BY t.request_at""").fetchall()
    db.close()
    return rows


if __name__ == "__main__":
    results = []
    results.append(check("175. Combine Two Tables", [('combine_two_tables([(1, "Wang", "Allen"), (2, "Alice", "Bob")], [(1, 2, "New York City", "New York"), (2, 3, "Leetcode", "California")])', [['Allen', 'Wang', None, None], ['Bob', 'Alice', 'New York City', 'New York']])]))
    results.append(check("182. Duplicate Emails", [('duplicate_emails([(1, "a@b.com"), (2, "c@d.com"), (3, "a@b.com")])', ['a@b.com']), ('duplicate_emails([(1, "x@y.com")])', [])]))
    results.append(check("183. Customers Who Never Order", [('never_ordered([(1, "Joe"), (2, "Henry"), (3, "Sam"), (4, "Max")], [(1, 3), (2, 1)])', ['Henry', 'Max'])]))
    results.append(check("197. Rising Temperature", [('rising_temperature([(1, "2015-01-01", 10), (2, "2015-01-02", 25), (3, "2015-01-03", 20), (4, "2015-01-04", 30)])', [2, 4])]))
    results.append(check("196. Delete Duplicate Emails", [('delete_duplicate_emails([(1, "john@example.com"), (2, "bob@example.com"), (3, "john@example.com")])', [[1, 'john@example.com'], [2, 'bob@example.com']])]))
    results.append(check("176. Second Highest Salary", [('second_highest_salary([(1, 100), (2, 200), (3, 300)])', 200), ('second_highest_salary([(1, 100)])', None), ('second_highest_salary([(1, 100), (2, 100)])', None)]))
    results.append(check("178. Rank Scores", [('rank_scores([(1, 3.5), (2, 3.65), (3, 4.0), (4, 3.85), (5, 4.0), (6, 3.65)])', [[4.0, 1], [4.0, 1], [3.85, 2], [3.65, 3], [3.65, 3], [3.5, 4]])]))
    results.append(check("184. Department Highest Salary", [('department_highest_salary([(1, "Joe", 70000, 1), (2, "Jim", 90000, 1), (3, "Henry", 80000, 2), (4, "Sam", 60000, 2), (5, "Max", 90000, 1)], [(1, "IT"), (2, "Sales")])', [['IT', 'Jim', 90000], ['IT', 'Max', 90000], ['Sales', 'Henry', 80000]])]))
    results.append(check("185. Department Top Three Salaries", [('top_three_salaries([(1, "Joe", 85000, 1), (2, "Henry", 80000, 2), (3, "Sam", 60000, 2), (4, "Max", 90000, 1), (5, "Janet", 69000, 1), (6, "Randy", 85000, 1), (7, "Will", 70000, 1)], [(1, "IT"), (2, "Sales")])', [['IT', 'Max', 90000], ['IT', 'Joe', 85000], ['IT', 'Randy', 85000], ['IT', 'Will', 70000], ['Sales', 'Henry', 80000], ['Sales', 'Sam', 60000]])]))
    results.append(check("262. Trips and Users", [('cancellation_rate([(1, 1, 10, 1, "completed", "2013-10-01"), (2, 2, 11, 1, "cancelled_by_driver", "2013-10-01"), (3, 3, 12, 6, "completed", "2013-10-01"), (4, 4, 13, 6, "cancelled_by_client", "2013-10-01"), (5, 1, 10, 1, "completed", "2013-10-02"), (6, 2, 11, 6, "completed", "2013-10-02"), (7, 3, 12, 6, "completed", "2013-10-02"), (8, 2, 12, 12, "completed", "2013-10-03"), (9, 3, 10, 12, "completed", "2013-10-03"), (10, 4, 13, 12, "cancelled_by_driver", "2013-10-03")], [(1, "No", "client"), (2, "Yes", "client"), (3, "No", "client"), (4, "No", "client"), (10, "No", "driver"), (11, "No", "driver"), (12, "No", "driver"), (13, "No", "driver")])', [['2013-10-01', 0.33], ['2013-10-02', 0.0], ['2013-10-03', 0.5]])]))
    if all(results):
        print("Every solution passes its tests.")
