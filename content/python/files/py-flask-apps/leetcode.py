# 3.2 Real Flask apps: structure, database, login and tests
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


# ================================================================== 595. Big Countries (Easy)
# https://leetcode.com/problems/big-countries/
# Pattern: WHERE with OR
# Idea: A country is big when its area is at least 3,000,000 or its population at least 25,000,000.
# One WHERE with OR does it.

import sqlite3


def big_countries(world):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE World (name TEXT, continent TEXT, area INTEGER, population INTEGER, gdp INTEGER)")
    db.executemany("INSERT INTO World VALUES (?, ?, ?, ?, ?)", world)
    rows = db.execute("""
        SELECT name, population, area FROM World
        WHERE area >= 3000000 OR population >= 25000000 ORDER BY name""").fetchall()
    db.close()
    return rows


# ================================================================== 1757. Recyclable and Low Fat Products (Easy)
# https://leetcode.com/problems/recyclable-and-low-fat-products/
# Pattern: WHERE with AND
# Idea: Both columns must be "Y". The kind of filter a shop page runs for every search.

import sqlite3


def find_products(products):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Products (product_id INTEGER, low_fats TEXT, recyclable TEXT)")
    db.executemany("INSERT INTO Products VALUES (?, ?, ?)", products)
    rows = db.execute("""
        SELECT product_id FROM Products
        WHERE low_fats = 'Y' AND recyclable = 'Y' ORDER BY product_id""").fetchall()
    db.close()
    return [row[0] for row in rows]


# ================================================================== 584. Find Customer Referee (Easy)
# https://leetcode.com/problems/find-customer-referee/
# Pattern: NULL needs IS NULL
# Idea: referee_id != 2 is not true for NULL, because NULL compared with anything is unknown. Add OR
# referee_id IS NULL.

import sqlite3


def find_customer_referee(customers):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Customer (id INTEGER, name TEXT, referee_id INTEGER)")
    db.executemany("INSERT INTO Customer VALUES (?, ?, ?)", customers)
    rows = db.execute("""
        SELECT name FROM Customer
        WHERE referee_id != 2 OR referee_id IS NULL ORDER BY id""").fetchall()
    db.close()
    return [row[0] for row in rows]


# ================================================================== 1148. Article Views I (Easy)
# https://leetcode.com/problems/article-views-i/
# Pattern: DISTINCT with a column compared to another
# Idea: Authors who viewed their own article: author_id = viewer_id. DISTINCT removes repeats.

import sqlite3


def own_article_views(views):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Views (article_id INTEGER, author_id INTEGER, viewer_id INTEGER, view_date TEXT)")
    db.executemany("INSERT INTO Views VALUES (?, ?, ?, ?)", views)
    rows = db.execute("SELECT DISTINCT author_id FROM Views WHERE author_id = viewer_id ORDER BY author_id").fetchall()
    db.close()
    return [row[0] for row in rows]


# ================================================================== 570. Managers with at Least 5 Direct Reports (Medium)
# https://leetcode.com/problems/managers-with-at-least-5-direct-reports/
# Pattern: GROUP BY with HAVING, then join back
# Idea: Count the people per managerId, keep the ones with 5 or more, and join with the table again
# to get the names.

import sqlite3


def managers_with_five(employees):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Employee (id INTEGER, name TEXT, department TEXT, managerId INTEGER)")
    db.executemany("INSERT INTO Employee VALUES (?, ?, ?, ?)", employees)
    rows = db.execute("""
        SELECT boss.name FROM Employee boss
        JOIN (SELECT managerId FROM Employee GROUP BY managerId HAVING COUNT(*) >= 5) big
          ON boss.id = big.managerId
        ORDER BY boss.name""").fetchall()
    db.close()
    return [row[0] for row in rows]


# ================================================================== 1934. Confirmation Rate (Medium)
# https://leetcode.com/problems/confirmation-rate/
# Pattern: LEFT JOIN, AVG of a CASE, IFNULL
# Idea: Every user who signed up must appear, even with no confirmations, so use a LEFT JOIN. The
# rate is the average of 1 for confirmed and 0 otherwise.

import sqlite3


def confirmation_rate(signups, confirmations):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Signups (user_id INTEGER, time_stamp TEXT)")
    db.execute("CREATE TABLE Confirmations (user_id INTEGER, time_stamp TEXT, action TEXT)")
    db.executemany("INSERT INTO Signups VALUES (?, ?)", signups)
    db.executemany("INSERT INTO Confirmations VALUES (?, ?, ?)", confirmations)
    rows = db.execute("""
        SELECT s.user_id,
               ROUND(IFNULL(AVG(CASE WHEN c.action = 'confirmed' THEN 1.0 ELSE 0.0 END), 0), 2)
        FROM Signups s LEFT JOIN Confirmations c ON s.user_id = c.user_id
        GROUP BY s.user_id ORDER BY s.user_id""").fetchall()
    db.close()
    return rows


# ================================================================== 180. Consecutive Numbers (Medium)
# https://leetcode.com/problems/consecutive-numbers/
# Pattern: Join the table with itself twice
# Idea: Pair each row with the next two ids. If all three have the same number, that number appears
# at least three times in a row.

import sqlite3


def consecutive_numbers(logs):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Logs (id INTEGER, num INTEGER)")
    db.executemany("INSERT INTO Logs VALUES (?, ?)", logs)
    rows = db.execute("""
        SELECT DISTINCT a.num FROM Logs a
        JOIN Logs b ON b.id = a.id + 1 AND b.num = a.num
        JOIN Logs c ON c.id = a.id + 2 AND c.num = a.num
        ORDER BY a.num""").fetchall()
    db.close()
    return [row[0] for row in rows]


# ================================================================== 550. Game Play Analysis IV (Medium)
# https://leetcode.com/problems/game-play-analysis-iv/
# Pattern: First day per player, then look for the next day
# Idea: Find each player's first login with MIN, check whether they came back the day after, and
# divide by the number of players.

import sqlite3


def came_back_next_day(activity):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Activity (player_id INTEGER, device_id INTEGER, event_date TEXT, games_played INTEGER)")
    db.executemany("INSERT INTO Activity VALUES (?, ?, ?, ?)", activity)
    row = db.execute("""
        WITH first AS (SELECT player_id, MIN(event_date) AS day FROM Activity GROUP BY player_id)
        SELECT ROUND(1.0 * COUNT(a.player_id) / (SELECT COUNT(*) FROM first), 2)
        FROM first f
        LEFT JOIN Activity a ON a.player_id = f.player_id AND a.event_date = DATE(f.day, '+1 day')""").fetchone()
    db.close()
    return row[0]


# ================================================================== 601. Human Traffic of Stadium (Hard)
# https://leetcode.com/problems/human-traffic-of-stadium/
# Pattern: Window function: id minus row number groups a run
# Idea: Keep the days with 100 or more people. Within a run of consecutive ids, id minus
# ROW_NUMBER() stays the same, so it names the run. Keep runs of 3 or more.

import sqlite3


def busy_days(stadium):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Stadium (id INTEGER, visit_date TEXT, people INTEGER)")
    db.executemany("INSERT INTO Stadium VALUES (?, ?, ?)", stadium)
    rows = db.execute("""
        WITH busy AS (
            SELECT id, visit_date, people, id - ROW_NUMBER() OVER (ORDER BY id) AS run
            FROM Stadium WHERE people >= 100),
        runs AS (SELECT run FROM busy GROUP BY run HAVING COUNT(*) >= 3)
        SELECT id, visit_date, people FROM busy WHERE run IN (SELECT run FROM runs)
        ORDER BY visit_date""").fetchall()
    db.close()
    return rows


# ================================================================== 432. All O`one Data Structure (Hard)
# https://leetcode.com/problems/all-oone-data-structure/
# Pattern: A dict of counts (simple version)
# Idea: Count page views per key and ask for the most and least viewed key. This simple version
# keeps a dict and uses max and min. The O(1) version keeps a linked list of buckets, one bucket for
# each count.

class AllOne:
    def __init__(self):
        self.counts = {}

    def inc(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1

    def dec(self, key):
        self.counts[key] -= 1
        if self.counts[key] == 0:
            del self.counts[key]

    def getMaxKey(self):
        if not self.counts:
            return ""
        return max(self.counts, key=self.counts.get)

    def getMinKey(self):
        if not self.counts:
            return ""
        return min(self.counts, key=self.counts.get)


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


if __name__ == "__main__":
    results = []
    results.append(check("595. Big Countries", [('big_countries([("Afghanistan", "Asia", 652230, 25500100, 20343000000), ("Albania", "Europe", 28748, 2831741, 12960000000), ("Algeria", "Africa", 2381741, 37100000, 188681000000), ("Andorra", "Europe", 468, 78115, 3712000000), ("Angola", "Africa", 1246700, 20609294, 100990000000)])', [['Afghanistan', 25500100, 652230], ['Algeria', 37100000, 2381741]])]))
    results.append(check("1757. Recyclable and Low Fat Products", [('find_products([(0, "Y", "N"), (1, "Y", "Y"), (2, "N", "Y"), (3, "Y", "Y"), (4, "N", "N")])', [1, 3])]))
    results.append(check("584. Find Customer Referee", [('find_customer_referee([(1, "Will", None), (2, "Jane", None), (3, "Alex", 2), (4, "Bill", None), (5, "Zack", 1), (6, "Mark", 2)])', ['Will', 'Jane', 'Bill', 'Zack'])]))
    results.append(check("1148. Article Views I", [('own_article_views([(1, 3, 5, "2019-08-01"), (1, 3, 6, "2019-08-02"), (2, 7, 7, "2019-08-01"), (2, 7, 6, "2019-08-02"), (4, 7, 1, "2019-07-22"), (3, 4, 4, "2019-07-21"), (3, 4, 4, "2019-07-21")])', [4, 7])]))
    results.append(check("570. Managers with at Least 5 Direct Reports", [('managers_with_five([(101, "John", "A", None), (102, "Dan", "A", 101), (103, "James", "A", 101), (104, "Amy", "A", 101), (105, "Anne", "A", 101), (106, "Ron", "B", 101)])', ['John'])]))
    results.append(check("1934. Confirmation Rate", [('confirmation_rate([(3, "2020-03-21 10:16:13"), (7, "2022-01-04 13:57:59"), (2, "2020-07-29 23:09:44"), (6, "2020-12-09 10:39:37")], [(3, "2021-01-06 03:30:46", "timeout"), (3, "2021-07-14 14:00:00", "timeout"), (7, "2021-06-12 11:57:29", "confirmed"), (7, "2021-06-13 12:58:28", "confirmed"), (7, "2021-06-14 13:59:27", "confirmed"), (2, "2021-01-22 00:00:00", "confirmed"), (2, "2021-02-28 23:59:59", "timeout")])', [[2, 0.5], [3, 0.0], [6, 0.0], [7, 1.0]])]))
    results.append(check("180. Consecutive Numbers", [('consecutive_numbers([(1, 1), (2, 1), (3, 1), (4, 2), (5, 1), (6, 2), (7, 2)])', [1]), ('consecutive_numbers([(1, 3), (2, 3), (3, 4), (4, 4), (5, 4), (6, 3), (7, 3), (8, 3)])', [3, 4])]))
    results.append(check("550. Game Play Analysis IV", [('came_back_next_day([(1, 2, "2016-03-01", 5), (1, 2, "2016-03-02", 6), (2, 3, "2017-06-25", 1), (3, 1, "2016-03-02", 0), (3, 4, "2018-07-03", 5)])', 0.33)]))
    results.append(check("601. Human Traffic of Stadium", [('busy_days([(1, "2017-01-01", 10), (2, "2017-01-02", 109), (3, "2017-01-03", 150), (4, "2017-01-04", 99), (5, "2017-01-05", 145), (6, "2017-01-06", 1455), (7, "2017-01-07", 199), (8, "2017-01-09", 188)])', [[5, '2017-01-05', 145], [6, '2017-01-06', 1455], [7, '2017-01-07', 199], [8, '2017-01-09', 188]])]))
    results.append(check("432. All O`one Data Structure", [('play(AllOne, ["AllOne", "inc", "inc", "getMaxKey", "getMinKey", "inc", "getMaxKey", "getMinKey"], [[], ["hello"], ["hello"], [], [], ["leet"], [], []])', [None, None, None, 'hello', 'hello', None, 'hello', 'leet'])]))
    if all(results):
        print("Every solution passes its tests.")
