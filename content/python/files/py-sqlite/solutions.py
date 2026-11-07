# 6.3 Databases with sqlite3 and SQL
# Model solutions. Try practice.py first.
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


# ================================================================== task 1: Save names that contain quotes
# Write save_and_list(names). It makes an in memory database with a table people (name TEXT),
# inserts every name, and returns all names sorted alphabetically with ORDER BY. Names can contain
# quotes, like O'Neil. Use a ? placeholder, never an f-string.
# Why it works: The third test is a classic injection attempt. With a placeholder it is stored as an
# ordinary, if strange, name.

import sqlite3


def save_and_list(names):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE people (name TEXT)")
    db.executemany("INSERT INTO people VALUES (?)", [(name,) for name in names])
    rows = db.execute("SELECT name FROM people ORDER BY name").fetchall()
    db.close()
    return [row[0] for row in rows]


# ================================================================== task 2: Make a bank transfer all or nothing
# Write transfer(db, sender, receiver, amount). The table accounts(name, balance) has a CHECK that
# balance is never below 0. Move the money with two UPDATE statements inside one transaction ("with
# db:"). If the sender does not have enough money, SQLite raises IntegrityError: catch it and raise
# ValueError("not enough money") instead, with nothing changed. The helper run(moves) starts ann
# with 100 and bo with 50, tries each move and returns the balances and the number of failed moves.
# Why it works: Catching the error OUTSIDE "with db:" matters: the exception must pass through the
# with block so it can roll back first.

import sqlite3


def transfer(db, sender, receiver, amount):
    try:
        with db:
            db.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, receiver))
            db.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, sender))
    except sqlite3.IntegrityError as err:
        raise ValueError("not enough money") from err


def run(moves):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER CHECK (balance >= 0))")
    db.executemany("INSERT INTO accounts VALUES (?, ?)", [("ann", 100), ("bo", 50)])
    db.commit()
    failed = 0
    for sender, receiver, amount in moves:
        try:
            transfer(db, sender, receiver, amount)
        except ValueError:
            failed += 1
    balances = db.execute("SELECT name, balance FROM accounts ORDER BY name").fetchall()
    db.close()
    return [balances, failed]


# ================================================================== task 3: Write a report with LEFT JOIN, GROUP BY and HAVING
# Write city_report(customers, orders, min_total). customers is a list of (id, name, city), orders a
# list of (id, customer_id, amount). Return one row [city, number of customers, total amount] for
# each city whose total is at least min_total. Customers without orders count as customers with 0.
# Sort by total from high to low, then by city. Use LEFT JOIN, COUNT(DISTINCT ...), COALESCE and
# HAVING.
# Why it works: COUNT(*) counts joined rows, not customers: Ann with two orders would be counted
# twice. Mistakes like this are why reports are tested with small known data.

import sqlite3


def city_report(customers, orders, min_total):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE customers (id INTEGER, name TEXT, city TEXT)")
    db.execute("CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount REAL)")
    db.executemany("INSERT INTO customers VALUES (?, ?, ?)", customers)
    db.executemany("INSERT INTO orders VALUES (?, ?, ?)", orders)
    rows = db.execute("""
        SELECT c.city, COUNT(DISTINCT c.id), COALESCE(SUM(o.amount), 0.0) AS total
        FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
        GROUP BY c.city
        HAVING total >= ?
        ORDER BY total DESC, c.city""", (min_total,)).fetchall()
    db.close()
    return [list(row) for row in rows]


CUSTOMERS = [(1, "Ann", "Paris"), (2, "Bo", "Rome"), (3, "Cy", "Paris"), (4, "Di", "Oslo"), (5, "Ed", "Lima")]
ORDERS = [(1, 1, 30), (2, 1, 20), (3, 2, 70), (4, 3, 25), (5, 4, 10)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Save names that contain quotes", [('save_and_list(["Cy", "Ann", "Bo"])', ['Ann', 'Bo', 'Cy']), ('save_and_list(["O\'Neil", "Ann"])', ['Ann', "O'Neil"]), ('save_and_list(["x\'); DROP TABLE people; --"])', ["x'); DROP TABLE people; --"]), ('save_and_list([])', [])]))
    results.append(check("Task 2: Make a bank transfer all or nothing", [('run([("ann", "bo", 30)])', [[['ann', 70], ['bo', 80]], 0]), ('run([("bo", "ann", 500)])', [[['ann', 100], ['bo', 50]], 1]), ('run([("bo", "ann", 500), ("ann", "bo", 100), ("bo", "ann", 150)])', [[['ann', 150], ['bo', 0]], 1])]))
    results.append(check("Task 3: Write a report with LEFT JOIN, GROUP BY and HAVING", [('city_report(CUSTOMERS, ORDERS, 0)', [['Paris', 2, 75.0], ['Rome', 1, 70.0], ['Oslo', 1, 10.0], ['Lima', 1, 0.0]]), ('city_report(CUSTOMERS, ORDERS, 50)', [['Paris', 2, 75.0], ['Rome', 1, 70.0]]), ('city_report(CUSTOMERS, [], 0)', [['Lima', 1, 0.0], ['Oslo', 1, 0.0], ['Paris', 2, 0.0], ['Rome', 1, 0.0]])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
