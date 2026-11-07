# Advanced Python 6.3: databases with sqlite3. Checked against the Python 3.14 documentation of sqlite3 (connect,
# Cursor, execute, executemany, executescript, placeholders, lastrowid, rowcount, the connection as a context manager,
# row_factory and sqlite3.Row, IntegrityError and OperationalError, the autocommit attribute from 3.12, the deprecated
# default date adapters) and the SQLite documentation (CHECK, FOREIGN KEY with PRAGMA foreign_keys, EXPLAIN QUERY
# PLAN, window functions, B-tree pages).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-sqlite')
K = Kit()

K.code('first_db', r'''
import os
import sqlite3
import tempfile

path = os.path.join(tempfile.mkdtemp(), "shop.db")
conn = sqlite3.connect(path)                   # makes the file if it does not exist
cur = conn.cursor()
cur.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL)")
cur.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("tea", 2.5))
cur.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("cake", 4.0))
print("new id:", cur.lastrowid)
conn.commit()                                  # save the changes in the file
conn.close()

conn = sqlite3.connect(path)                   # open it again: the data is still there
cur = conn.execute("SELECT id, name, price FROM products ORDER BY price")
print(cur.fetchone())                          # one row as a tuple
print(cur.fetchall())                          # the rows that are left
for name, price in conn.execute("SELECT name, price FROM products"):
    print(f"{name}: {price:.2f}")
print(conn.execute("SELECT COUNT(*) FROM products").fetchone()[0])
conn.close()
''')

K.code('queries', r'''
import sqlite3

conn = sqlite3.connect(":memory:")             # a database that lives only in memory
conn.executescript("""
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL);
INSERT INTO customers VALUES (1, 'Ann', 'Paris'), (2, 'Bo', 'Rome'), (3, 'Cy', 'Paris'), (4, 'Di', 'Oslo');
INSERT INTO orders VALUES (1, 1, 30), (2, 1, 20), (3, 2, 70), (4, 3, 15);
""")


def print_rows(sql):
    for row in conn.execute(sql):
        print(row)
    print("-")


print_rows("SELECT name FROM customers WHERE city = 'Paris' ORDER BY name")
print_rows("SELECT city, COUNT(*) FROM customers GROUP BY city ORDER BY city")
print_rows("""SELECT c.name, o.amount FROM customers c
              JOIN orders o ON o.customer_id = c.id
              ORDER BY o.amount DESC LIMIT 2""")
print_rows("""SELECT c.name, COALESCE(SUM(o.amount), 0) AS total FROM customers c
              LEFT JOIN orders o ON o.customer_id = c.id
              GROUP BY c.id HAVING total < 60 ORDER BY total""")
''')

K.code('params', r'''
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (name TEXT, password TEXT)")
people = [("ann", "s3cret"), ("bo", "hunter2"), ("o'neil", "pa55")]
cur = conn.executemany("INSERT INTO users VALUES (?, ?)", people)    # one statement, many rows
print("inserted:", cur.rowcount)

row = conn.execute("SELECT name FROM users WHERE name = :who", {"who": "o'neil"}).fetchone()
print(row)                                     # a named placeholder: the quote is no problem

typed = "nobody' OR '1'='1"                    # what an attacker types into a login box
bad_sql = f"SELECT name FROM users WHERE name = '{typed}'"
print(bad_sql)
print(conn.execute(bad_sql).fetchall())        # every user comes back: SQL injection
print(conn.execute("SELECT name FROM users WHERE name = ?", (typed,)).fetchall())

try:
    conn.execute(f"SELECT * FROM users WHERE name = '{people[2][0]}'")
except sqlite3.OperationalError as err:
    print("OperationalError:", err)            # an honest name with a quote breaks the f-string
''')

K.code('transactions', r'''
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0))")
conn.executemany("INSERT INTO accounts VALUES (?, ?)", [("ann", 100), ("bo", 20)])
conn.commit()


def transfer(sender, receiver, amount):
    with conn:                                 # commit at the end, or rollback on an exception
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, receiver))
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, sender))


transfer("ann", "bo", 30)
print(conn.execute("SELECT * FROM accounts ORDER BY name").fetchall())
try:
    transfer("bo", "ann", 500)                 # bo would go below 0, so CHECK fails
except sqlite3.IntegrityError as err:
    print("IntegrityError:", err)
print(conn.execute("SELECT * FROM accounts ORDER BY name").fetchall())    # unchanged: rolled back

try:
    with conn:
        conn.execute("INSERT INTO accounts VALUES ('ann', 5)")             # the name is the primary key
except sqlite3.IntegrityError as err:
    print("IntegrityError:", err)

conn.execute("PRAGMA foreign_keys = ON")       # SQLite does not check foreign keys unless you ask
conn.execute("CREATE TABLE payments (id INTEGER PRIMARY KEY, account TEXT REFERENCES accounts(name))")
try:
    with conn:
        conn.execute("INSERT INTO payments (account) VALUES ('zed')")
except sqlite3.IntegrityError as err:
    print("IntegrityError:", err)
''')

K.code('rows_index', r'''
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row                 # rows work like tuples AND like dicts
conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, year INTEGER)")
conn.executemany("INSERT INTO books (title, year) VALUES (?, ?)",
                 [("Dune", 1965), ("Neuromancer", 1984), ("Hyperion", 1989)])
row = conn.execute("SELECT * FROM books WHERE year > ?", (1980,)).fetchone()
print(row["title"], row[2], row.keys())
print([dict(r) for r in conn.execute("SELECT title, year FROM books ORDER BY year DESC")])


def plan(sql):
    return [r["detail"] for r in conn.execute("EXPLAIN QUERY PLAN " + sql)]


print(plan("SELECT * FROM books WHERE year = 1984"))       # SCAN: reads every row
conn.execute("CREATE INDEX idx_books_year ON books(year)")
print(plan("SELECT * FROM books WHERE year = 1984"))       # SEARCH: jumps to the row with the index
print(plan("SELECT * FROM books WHERE id = 2"))            # the primary key is an index already
''')

K.lesson('idea', 'Databases and SQL from Python', f'''
{src('Python 3.14 documentation of sqlite3 and the SQLite documentation.')}
{wwh('A <b>database</b> stores data in <b>tables</b>: rows of records with named columns, like a strict spreadsheet. You ask it questions in <b>SQL</b> (Structured Query Language). <b>SQLite</b> is a complete SQL database in one file, and Python ships with the <b>sqlite3</b> module to use it, so there is nothing to install.',
     'A JSON or CSV file must be read completely, changed in memory and written back completely. Two programs writing at once can destroy it, a crash halfway leaves half a file, and finding one record among millions means reading them all.',
     'The database reads and writes only the pages it needs, finds rows fast with <b>indexes</b>, checks rules such as "balance may not be negative", and groups changes into <b>transactions</b> that are saved completely or not at all. SQL says WHAT you want and the database works out HOW to get it.')}
{viz('pysql')}
{versus('Where to keep data', ['', 'JSON or CSV file', 'SQLite (sqlite3)', 'PostgreSQL or MySQL', 'pandas DataFrame'], [
    ['Setup', 'None', 'None, one file', 'A server to install and run', 'pip install pandas'],
    ['Find one record in a million', 'Read everything', 'Milliseconds with an index', 'Milliseconds with an index', 'Fast, but all data in memory'],
    ['Safe when a program crashes', 'No', 'Yes, transactions', 'Yes, transactions', 'No, memory only'],
    ['Many writers at once', 'No', 'One writer at a time', 'Yes, many', 'No'],
    ['Rules on the data', 'None', 'Types, NOT NULL, UNIQUE, CHECK, foreign keys', 'The same and more', 'Only in your code'],
    ['Typical use', 'Small settings and exports', 'Apps, phones, browsers, tests, prototypes', 'Web sites with many users', 'Analysis and reports']],
    'SQLite for one program or a small site, PostgreSQL for a web app with many users at once, pandas for analysis. The SQL you learn here works in all of them with small changes.')}
''', kw=['database', 'table', 'row', 'column', 'SQL', 'SQLite', 'sqlite3', 'index', 'transaction', 'PostgreSQL'])

K.lesson('first', 'Connect, execute, commit, fetch', f'''
{run('first_db')}
{table(['Step', 'Code', 'Meaning'], [
    ['Open', 'conn = sqlite3.connect("shop.db")', 'Opens the file, or makes it. ":memory:" gives a database in memory only.'],
    ['Cursor', 'cur = conn.cursor()', 'An object that runs SQL and walks through results. conn.execute() makes one for you.'],
    ['Run SQL', 'cur.execute(sql, values)', 'Runs one statement. Values go in a tuple, matching the ? marks.'],
    ['Save', 'conn.commit()', 'Makes INSERT, UPDATE and DELETE permanent. Without it they are lost on close.'],
    ['Read', 'fetchone(), fetchall(), fetchmany(n), for row in cur', 'Rows come back as tuples.'],
    ['Close', 'conn.close()', 'Frees the file. Uncommitted changes are thrown away.']])}
{note('The most common beginner bug: INSERT works, the program ends, and the data is gone. You forgot conn.commit(). Using "with conn:" commits for you.', 'exam')}
{note('SQL types in SQLite are flexible: INTEGER, REAL, TEXT, BLOB and NULL. Python int, float, str, bytes and None map to them. Store dates as ISO text such as "2026-11-07", because the automatic date converters are deprecated since Python 3.12.', 'tip')}
''', kw=['connect', 'cursor', 'execute', 'commit', 'fetchone', 'fetchall', 'fetchmany', 'close', ':memory:', 'lastrowid', 'types'])

K.lesson('sql', 'SQL in one lesson: SELECT, WHERE, JOIN, GROUP BY', f'''
{run('queries')}
{table(['SQL', 'Does', 'Runs in step'], [
    ['FROM a JOIN b ON ...', 'Takes rows from tables and pairs them up', '1'],
    ['WHERE condition', 'Keeps rows where the condition is true', '2'],
    ['GROUP BY column', 'Puts rows with the same value in one group', '3'],
    ['HAVING condition', 'Keeps groups (it can use COUNT, SUM, AVG)', '4'],
    ['SELECT columns', 'Picks and names the output columns', '5'],
    ['ORDER BY column DESC', 'Sorts the result', '6'],
    ['LIMIT n OFFSET k', 'Keeps n rows after skipping k', '7']])}
{table(['Change data', 'Example'], [
    ['Make a table', 'CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)'],
    ['Add rows', 'INSERT INTO t (name) VALUES (?)'],
    ['Change rows', 'UPDATE t SET name = ? WHERE id = ?'],
    ['Remove rows', 'DELETE FROM t WHERE id = ?'],
    ['Remove the table', 'DROP TABLE IF EXISTS t']])}
{versus('Kinds of JOIN', ['', 'INNER JOIN (JOIN)', 'LEFT JOIN', 'CROSS JOIN'], [
    ['Keeps', 'Only pairs that match', 'Every left row, with NULL when nothing matches', 'Every left row with every right row'],
    ['Rows for 4 customers, 3 with orders', 'One per matching order', 'Matching orders plus 1 row for the customer without orders', '4 &times; number of orders'],
    ['Use it for', 'Orders with their customer', 'Customers and their orders, even with none', 'All combinations (rarely)']],
    'Use LEFT JOIN with COALESCE(SUM(...), 0) when rows without a partner must still appear with 0.')}
{note('An UPDATE or DELETE without WHERE changes EVERY row. Write the WHERE first, and try it as a SELECT before you run it.', 'warn')}
''', kw=['SELECT', 'WHERE', 'ORDER BY', 'GROUP BY', 'HAVING', 'JOIN', 'LEFT JOIN', 'COUNT', 'SUM', 'COALESCE', 'LIMIT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE'])

K.lesson('params', 'Placeholders and SQL injection', f'''
{run('params')}
{table(['Style', 'SQL', 'Values'], [
    ['qmark', 'WHERE name = ? AND age &gt; ?', 'a tuple: ("ann", 30)'],
    ['named', 'WHERE name = :name AND age &gt; :age', 'a dict: {"name": "ann", "age": 30}'],
    ['Many rows', 'executemany("INSERT INTO t VALUES (?, ?)", rows)', 'a list of tuples'],
    ['A script', '<code>executescript("CREATE ...; INSERT ...")</code>', 'no values: only for your own fixed SQL']])}
{note('Never put values into SQL with f-strings, +, % or .format(). Use ? or :name every time. Placeholders stop SQL injection, handle quotes in names like O\'Neil, and let the database reuse the prepared statement.', 'warn')}
{note('Placeholders are for VALUES only. A table or column name cannot be a ?. If a user picks the column to sort by, check it against a fixed list such as {"name", "price"} before you put it into the SQL.', 'exam')}
''', kw=['placeholder', 'qmark', 'named parameters', 'executemany', 'executescript', 'SQL injection', 'rowcount', 'OperationalError'])

K.lesson('txn', 'Transactions and rules on the data', f'''
{run('transactions')}
{versus('ACID: what a transaction promises', ['Letter', 'Means', 'In the example'], [
    ['A, atomic', 'All the changes happen, or none', 'The failed transfer did not give Ann 500'],
    ['C, consistent', 'Rules such as CHECK and UNIQUE always hold', 'No balance is ever below 0'],
    ['I, isolated', 'Others do not see half done changes', 'Another connection sees the old balances until commit'],
    ['D, durable', 'After commit the data survives a crash or power cut', 'SQLite writes a journal before it changes the file']],
    'Put every group of changes that must happen together inside one "with conn:" block.')}
{table(['Rule in CREATE TABLE', 'Stops', 'Error'], [
    ['PRIMARY KEY, UNIQUE', 'Two rows with the same value', 'IntegrityError: UNIQUE constraint failed'],
    ['NOT NULL', 'A missing value', 'IntegrityError: NOT NULL constraint failed'],
    ['CHECK (balance &gt;= 0)', 'Values that break your rule', 'IntegrityError: CHECK constraint failed'],
    ['REFERENCES other(col)', 'A link to a row that does not exist', 'IntegrityError: FOREIGN KEY constraint failed (after PRAGMA foreign_keys = ON)']])}
{note('"with conn:" commits or rolls back, but it does NOT close the connection. Since Python 3.12 you can also pass autocommit=False to sqlite3.connect for the transaction rules of the database standard (PEP 249).', 'tip')}
''', kw=['transaction', 'commit', 'rollback', 'with conn', 'ACID', 'atomic', 'IntegrityError', 'CHECK', 'UNIQUE', 'NOT NULL', 'foreign key', 'PRAGMA', 'autocommit'])

K.lesson('rows', 'Friendlier rows and fast lookups with indexes', f'''
{run('rows_index')}
{note('An index is a sorted copy of one column with a pointer to each row, kept in a B-tree. It turns a scan of every row into a few page reads. It costs disk space and makes INSERT and UPDATE a little slower, so index the columns you search, join or sort by often.', 'tip')}
{deep('ORMs: databases without writing SQL', '<p>An ORM (object relational mapper) turns tables into classes and rows into objects. SQLAlchemy is the most used one, and Django has its own ORM, which the web part of this course uses. ORMs still create SQL for you, so knowing SQL helps you find slow queries and the "N+1 queries" problem, where a loop runs one query per row instead of one JOIN.</p>')}
''', kw=['row_factory', 'sqlite3.Row', 'dict rows', 'index', 'CREATE INDEX', 'EXPLAIN QUERY PLAN', 'B-tree', 'ORM', 'SQLAlchemy', 'N+1'])

K.lesson('maths', 'The maths: indexes, joins and estimates', f'''
{fxs(fx('Full scan', 'cost &asymp; N rows read', 'Finding one user among 1,000,000 without an index reads 1,000,000 rows.'),
     fx('B-tree height', 'h = &lceil;log<sub>f</sub> N&rceil;, f = keys per page (fan out)', 'N = 1,000,000 and f = 100: h = 3 page reads instead of a million rows.', key=True),
     fx('Binary search in a sorted index', 'comparisons &asymp; &lceil;log<sub>2</sub> N&rceil;', 'log<sub>2</sub> 1,000,000 &asymp; 20.'),
     fx('Selectivity of WHERE a = v', 'rows &asymp; N / V(a), V(a) = number of different values', '1,000,000 rows and 100 cities: about 10,000 rows per city.', key=True),
     fx('Equi join size estimate', '|R &#8904; S| &asymp; |R| &times; |S| / max(V(R, a), V(S, a))', '1000 customers, 5000 orders, joined on 1000 customer ids: 1000 &times; 5000 / 1000 = 5000 rows.'),
     fx('Cost of commits', 'time &asymp; commits &times; time per disk sync', '1000 inserts with 1000 commits at 5 ms each: 5 s. One commit: about 5 ms.'))}
{steps('Worked example: how many page reads does an index save?', [
    'A table has 2,000,000 rows. Each 4096 byte page holds 40 rows, so the table has 2,000,000 / 40 = 50,000 pages.',
    'A full scan reads all 50,000 pages.',
    'The index on the column holds about 200 keys per page, so its height is &lceil;log<sub>200</sub> 2,000,000&rceil; = 3, because 200<sup>2</sup> = 40,000 is too small and 200<sup>3</sup> = 8,000,000 is enough.',
    'Reading one row costs 3 index pages plus 1 table page.',
    eq('4 page reads instead of 50,000: about 12,500 times fewer')])}
''', kw=['full scan', 'B-tree height', 'fan out', 'binary search', 'selectivity', 'join size', 'cost of commits', 'page'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Connect, create a table, INSERT with ? placeholders, commit, and read rows with SELECT and fetchall.</p>',
    '<p>Write WHERE, ORDER BY, GROUP BY, HAVING and JOINs, use "with conn:" for transactions, and catch IntegrityError from UNIQUE, NOT NULL and CHECK rules.</p>',
    '<p>Design tables with primary and foreign keys (normal forms), add indexes after reading EXPLAIN QUERY PLAN, and use window functions such as ROW_NUMBER and DENSE_RANK.</p>',
    '<p>Understand B-trees, the write ahead log (WAL), isolation levels and locking, query planners and cost estimates, and move from SQLite to PostgreSQL with an ORM and migrations.</p>')}
{grow('Store and read rows safely.', 'Query, join and protect data with transactions.', 'Design schemas and tune queries with indexes.')}
''', kw=['beginner', 'expert', 'normal forms', 'window functions', 'WAL', 'isolation levels', 'query planner', 'migrations'])

lc(175, 'Combine Two Tables', 'combine-two-tables', 'e', 'LEFT JOIN keeps people without an address', 'Every person must appear, even without an address, so use LEFT JOIN. Missing columns come back as None.', r'''
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
''', [('combine_two_tables([(1, "Wang", "Allen"), (2, "Alice", "Bob")], [(1, 2, "New York City", "New York"), (2, 3, "Leetcode", "California")])', [['Allen', 'Wang', None, None], ['Bob', 'Alice', 'New York City', 'New York']])])
lc(182, 'Duplicate Emails', 'duplicate-emails', 'e', 'GROUP BY with HAVING COUNT', 'Group the rows by email and keep the groups that have more than one row.', r'''
import sqlite3


def duplicate_emails(person):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Person (id INTEGER, email TEXT)")
    db.executemany("INSERT INTO Person VALUES (?, ?)", person)
    rows = db.execute("SELECT email FROM Person GROUP BY email HAVING COUNT(*) > 1 ORDER BY email").fetchall()
    db.close()
    return [row[0] for row in rows]
''', [('duplicate_emails([(1, "a@b.com"), (2, "c@d.com"), (3, "a@b.com")])', ['a@b.com']), ('duplicate_emails([(1, "x@y.com")])', [])])
lc(183, 'Customers Who Never Order', 'customers-who-never-order', 'e', 'NOT IN a subquery, or LEFT JOIN ... IS NULL', 'Find customers whose id is not in the list of customer ids of the orders.', r'''
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
''', [('never_ordered([(1, "Joe"), (2, "Henry"), (3, "Sam"), (4, "Max")], [(1, 3), (2, 1)])', ['Henry', 'Max'])])
lc(197, 'Rising Temperature', 'rising-temperature', 'e', 'Join the table with itself on yesterday', 'Pair each day with the day before using DATE(day, \'-1 day\'), then keep pairs where the temperature went up.', r'''
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
''', [('rising_temperature([(1, "2015-01-01", 10), (2, "2015-01-02", 25), (3, "2015-01-03", 20), (4, "2015-01-04", 30)])', [2, 4])])
lc(196, 'Delete Duplicate Emails', 'delete-duplicate-emails', 'e', 'DELETE rows that are not the smallest id', 'Keep MIN(id) of each email and delete every other row.', r'''
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
''', [('delete_duplicate_emails([(1, "john@example.com"), (2, "bob@example.com"), (3, "john@example.com")])', [[1, 'john@example.com'], [2, 'bob@example.com']])])
lc(176, 'Second Highest Salary', 'second-highest-salary', 'm', 'DISTINCT, ORDER BY, LIMIT 1 OFFSET 1 inside a subquery', 'The outer SELECT turns "no row" into NULL, which is None in Python.', r'''
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
''', [('second_highest_salary([(1, 100), (2, 200), (3, 300)])', 200), ('second_highest_salary([(1, 100)])', None), ('second_highest_salary([(1, 100), (2, 100)])', None)])
lc(178, 'Rank Scores', 'rank-scores', 'm', 'The DENSE_RANK window function', 'DENSE_RANK() OVER (ORDER BY score DESC) gives equal scores the same rank and leaves no gaps after ties.', r'''
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
''', [('rank_scores([(1, 3.5), (2, 3.65), (3, 4.0), (4, 3.85), (5, 4.0), (6, 3.65)])', [[4.0, 1], [4.0, 1], [3.85, 2], [3.65, 3], [3.65, 3], [3.5, 4]])])
lc(184, 'Department Highest Salary', 'department-highest-salary', 'm', 'Join with the maximum of each department', 'A subquery finds MAX(salary) per department. Join it back to keep every employee who earns that much, ties included.', r'''
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
''', [('department_highest_salary([(1, "Joe", 70000, 1), (2, "Jim", 90000, 1), (3, "Henry", 80000, 2), (4, "Sam", 60000, 2), (5, "Max", 90000, 1)], [(1, "IT"), (2, "Sales")])', [['IT', 'Jim', 90000], ['IT', 'Max', 90000], ['Sales', 'Henry', 80000]])])
lc(185, 'Department Top Three Salaries', 'department-top-three-salaries', 'h', 'DENSE_RANK per department with PARTITION BY', 'PARTITION BY departmentId restarts the ranking in each department. Keep rank 3 or better. Ties share a rank.', r'''
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
''', [('top_three_salaries([(1, "Joe", 85000, 1), (2, "Henry", 80000, 2), (3, "Sam", 60000, 2), (4, "Max", 90000, 1), (5, "Janet", 69000, 1), (6, "Randy", 85000, 1), (7, "Will", 70000, 1)], [(1, "IT"), (2, "Sales")])', [['IT', 'Max', 90000], ['IT', 'Joe', 85000], ['IT', 'Randy', 85000], ['IT', 'Will', 70000], ['Sales', 'Henry', 80000], ['Sales', 'Sam', 60000]])])
lc(262, 'Trips and Users', 'trips-and-users', 'h', 'Join twice to the users table, then average a condition', 'Join Users once for the client and once for the driver and keep trips where neither is banned. AVG(status != \'completed\') is the share of cancelled trips, because a true test counts as 1.', r'''
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
''', [('cancellation_rate([(1, 1, 10, 1, "completed", "2013-10-01"), (2, 2, 11, 1, "cancelled_by_driver", "2013-10-01"), (3, 3, 12, 6, "completed", "2013-10-01"), (4, 4, 13, 6, "cancelled_by_client", "2013-10-01"), (5, 1, 10, 1, "completed", "2013-10-02"), (6, 2, 11, 6, "completed", "2013-10-02"), (7, 3, 12, 6, "completed", "2013-10-02"), (8, 2, 12, 12, "completed", "2013-10-03"), (9, 3, 10, 12, "completed", "2013-10-03"), (10, 4, 13, 12, "cancelled_by_driver", "2013-10-03")], [(1, "No", "client"), (2, "Yes", "client"), (3, "No", "client"), (4, "No", "client"), (10, "No", "driver"), (11, "No", "driver"), (12, "No", "driver"), (13, "No", "driver")])', [['2013-10-01', 0.33], ['2013-10-02', 0.0], ['2013-10-03', 0.5]])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>LeetCode has a whole set of SQL problems. Here each one is solved with sqlite3 from Python: the function builds a small database in memory from the example rows, runs the SQL and returns the rows. You practise LEFT JOIN, GROUP BY with HAVING, self joins on dates, DELETE with a subquery, LIMIT with OFFSET, and the window functions DENSE_RANK and PARTITION BY.</p>'), kw=['LeetCode', 'SQL', 'LEFT JOIN', 'GROUP BY', 'HAVING', 'self join', 'subquery', 'DENSE_RANK', 'PARTITION BY', 'window function'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'sqlite3 is a full SQL database in one file. connect, execute, commit, fetchone or fetchall, close.',
    'SQL runs in the order FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT. LEFT JOIN keeps rows without a partner.',
    'Always use ? or :name placeholders. f-strings in SQL cause SQL injection and break on quotes.',
    '"with conn:" makes a transaction: commit at the end, rollback on an exception. PRIMARY KEY, UNIQUE, NOT NULL, CHECK and foreign keys raise IntegrityError.',
    'sqlite3.Row gives rows by column name. Indexes turn a full scan into a few B-tree page reads, and EXPLAIN QUERY PLAN shows which one is used.'],
    'Next: building desktop windows with tkinter.')}
{files('Three tasks: save names that contain quotes safely, make a bank transfer all or nothing, and write a report with LEFT JOIN, GROUP BY and HAVING.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which call saves INSERT and UPDATE changes permanently?', ['conn.save()', 'conn.commit()', 'cur.fetchall()', 'conn.close()'], 1, 'Commit.', 'close() without commit() throws the changes away.')
K.quiz('e', 'What does sqlite3.connect(":memory:") give you?', ['A file called :memory:', 'A database that lives only in RAM and is gone when closed', 'An error', 'A read only database'], 1, 'Memory.', 'Very useful for tests.')
K.quiz('e', 'Which SQL keyword keeps only the rows that match a condition?', ['ORDER BY', 'WHERE', 'GROUP BY', 'LIMIT'], 1, 'A filter on rows.', 'HAVING is the filter for groups.')
K.quiz('m', 'Why is f"SELECT * FROM users WHERE name = \'{name}\'" dangerous?', ['It is slow', 'A quote in name can change the SQL itself (SQL injection)', 'f-strings cannot hold SQL', 'It returns tuples'], 1, 'Text becomes code.', 'Use WHERE name = ? with (name,).')
K.quiz('m', 'In which order does the database run these parts?', ['SELECT, FROM, WHERE, GROUP BY', 'FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY', 'FROM, SELECT, WHERE, ORDER BY', 'WHERE, FROM, SELECT, HAVING'], 1, 'FROM first.', 'That is why WHERE cannot use a column name made in SELECT.')
K.quiz('m', 'What does "with conn:" do when an exception happens inside the block?', ['Closes the connection', 'Rolls back the transaction', 'Commits anyway', 'Ignores the exception'], 1, 'Undo.', 'It commits when the block ends normally. It never closes the connection.')
K.quiz('m', 'Customers Ann (2 orders), Bo (1 order) and Cy (no orders). How many rows does customers LEFT JOIN orders give?', ['3', '4', '2', '6'], 1, 'Cy keeps one row with NULLs.', '2 + 1 + 1 = 4.')
K.quiz('m', 'Which can NOT be a ? placeholder?', ['A name to compare', 'A number in WHERE', 'A table name', 'A value in INSERT'], 2, 'Values only.', 'Check table and column names against a fixed list instead.')
K.quiz('h', 'Why does INSERT INTO payments (account) VALUES (\'zed\') work without an error even though no account zed exists?', ['zed exists', 'SQLite does not check foreign keys until PRAGMA foreign_keys = ON', 'Foreign keys only work in PostgreSQL', 'INSERT never checks rules'], 1, 'A PRAGMA.', 'Turn it on for every new connection.')
K.quiz('h', 'What is the main cost of adding an index on a column?', ['Queries get slower', 'Extra disk space and slower INSERT, UPDATE and DELETE', 'The column becomes read only', 'Rows are reordered'], 1, 'The index must be kept up to date.', 'Index what you search, join or sort by.')
K.quiz('h', 'Inserting 100,000 rows takes minutes. What helps most?', ['A bigger cursor', 'Put all inserts in one transaction (or use executemany) and commit once', 'Use fetchall', 'Close and reopen the connection'], 1, 'Disk syncs.', 'Each commit waits for the disk. One commit for all rows is far faster.')
K.quiz('x', 'In the style of a CMU 15-445 exam: a B+ tree has fan out 200 and indexes 8,000,000 keys. How many levels does a lookup read?', ['2', '3', '4', '23'], 1, '200<sup>3</sup> = 8,000,000.', '&lceil;log<sub>200</sub> 8,000,000&rceil; = 3.')
K.quiz('x', 'In the style of a Stanford CS 145 exam: R has 10,000 rows and S 2,000 rows. They are joined on a, with 100 different values of a in R and 200 in S. About how many rows does the join give?', ['20,000,000', '100,000', '200,000', '2,000'], 1, '|R| &times; |S| / max(V).', '10,000 &times; 2,000 / 200 = 100,000.')

K.calc('e', 'A table has 5 rows. You insert 3 rows and delete 1. How many rows are left?', '7', '5 + 3 &minus; 1.', ['Insert: 8.', 'Delete: 7.', eq('7')], check=5 + 3 - 1)
K.calc('e', 'A CROSS JOIN of a table with 4 rows and one with 5 rows gives how many rows?', '20', 'Every pair.', ['4 &times; 5.', 'Every row with every row.', eq('20')], check=4 * 5)
K.calc('e', 'Customers Ann (3 orders), Bo (1 order), Cy and Di (no orders). How many rows does customers LEFT JOIN orders give?', '6', '3 + 1 + 1 + 1.', ['Ann: 3 rows, Bo: 1 row.', 'Cy and Di: 1 row each with NULLs.', eq('6')], check=3 + 1 + 1 + 1)
K.calc('m', 'How many comparisons does binary search need in a sorted index of 1,000,000 keys (rounded up)?', '20', '&lceil;log<sub>2</sub> 1,000,000&rceil;.', ['2<sup>19</sup> = 524,288 is too small.', '2<sup>20</sup> = 1,048,576 is enough.', eq('20')], check=(1_000_000 - 1).bit_length())
K.calc('m', 'A B-tree has fan out 100 and 1,000,000 keys. What is its height?', '3', '&lceil;log<sub>100</sub> 10<sup>6</sup>&rceil;.', ['100<sup>2</sup> = 10,000 is too small.', '100<sup>3</sup> = 1,000,000 is enough.', eq('3')], check=3)
K.calc('m', '1,000,000 rows, 250 different cities. About how many rows does WHERE city = ? return?', '4000', 'N / V(city).', ['1,000,000 / 250.', 'Each city is assumed equally common.', eq('4,000')], check=1_000_000 // 250)
K.calc('m', '2000 inserts, each with its own commit that waits 5 ms for the disk. How many seconds is that?', '10', '2000 &times; 5 ms.', ['10,000 ms.', '/ 1000.', eq('10 s')], check=2000 * 5 // 1000)
K.calc('h', 'Pages of 4096 bytes hold 40 rows each. How many pages does a table of 2,000,000 rows need?', '50000', '2,000,000 / 40.', ['Rows divided by rows per page.', '2,000,000 / 40.', eq('50,000 pages')], check=2_000_000 // 40)
K.calc('h', 'R has 1000 rows and S 5000 rows, joined on a key with 1000 different values in each. Estimate the join size.', '5000', '|R| &times; |S| / max(V).', ['1000 &times; 5000 = 5,000,000.', '/ 1000.', eq('5,000 rows')], check=1000 * 5000 // 1000)
K.calc('x', 'In the style of a Stanford CS 145 exam: 1,000,000 rows, WHERE a = ? AND b = ?, with 100 different values of a and 20 of b, assumed independent. How many rows are expected?', '500', 'N / (V(a) &times; V(b)).', ['Selectivity of a: 1/100, of b: 1/20.', '1,000,000 / 2000.', eq('500')], check=1_000_000 // (100 * 20))

K.assign('safenames', 'e', 'Save names that contain quotes',
         '<p>Write <code>save_and_list(names)</code>. It makes an in memory database with a table people (name TEXT), inserts every name, and returns all names sorted alphabetically with ORDER BY. Names can contain quotes, like O\'Neil. Use a ? placeholder, never an f-string.</p>',
         '''
import sqlite3


def save_and_list(names):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE people (name TEXT)")
    for name in names:
        db.execute(f"INSERT INTO people VALUES ('{name}')")
    rows = db.execute("SELECT name FROM people ORDER BY name").fetchall()
    db.close()
    return [row[0] for row in rows]
''', [('save_and_list(["Cy", "Ann", "Bo"])', ['Ann', 'Bo', 'Cy']), ('save_and_list(["O\'Neil", "Ann"])', ['Ann', "O'Neil"]), ('save_and_list(["x\'); DROP TABLE people; --"])', ["x'); DROP TABLE people; --"]), ('save_and_list([])', [])],
         '''
import sqlite3


def save_and_list(names):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE people (name TEXT)")
    db.executemany("INSERT INTO people VALUES (?)", [(name,) for name in names])
    rows = db.execute("SELECT name FROM people ORDER BY name").fetchall()
    db.close()
    return [row[0] for row in rows]
''', 'Pass each name as a value: execute("INSERT INTO people VALUES (?)", (name,)). The comma makes (name,) a tuple. executemany does all of them at once.', '<p>The third test is a classic injection attempt. With a placeholder it is stored as an ordinary, if strange, name.</p>')
K.assign('transfer', 'm', 'Make a bank transfer all or nothing',
         '<p>Write <code>transfer(db, sender, receiver, amount)</code>. The table accounts(name, balance) has a CHECK that balance is never below 0. Move the money with two UPDATE statements inside one transaction ("with db:"). If the sender does not have enough money, SQLite raises IntegrityError: catch it and raise ValueError("not enough money") instead, with nothing changed. The helper <code>run(moves)</code> starts ann with 100 and bo with 50, tries each move and returns the balances and the number of failed moves.</p>',
         '''
import sqlite3


def transfer(db, sender, receiver, amount):
    db.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, receiver))
    try:
        db.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, sender))
    except sqlite3.IntegrityError:
        raise ValueError("not enough money")
    db.commit()


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
''', [('run([("ann", "bo", 30)])', [[['ann', 70], ['bo', 80]], 0]), ('run([("bo", "ann", 500)])', [[['ann', 100], ['bo', 50]], 1]), ('run([("bo", "ann", 500), ("ann", "bo", 100), ("bo", "ann", 150)])', [[['ann', 150], ['bo', 0]], 1])],
         '''
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
''', 'In the starter the first UPDATE already gave the receiver the money and nothing undoes it. Put both UPDATEs in "with db:" so the IntegrityError rolls both back, and catch the error outside the with block.', '<p>Catching the error OUTSIDE "with db:" matters: the exception must pass through the with block so it can roll back first.</p>')
K.assign('cityreport', 'h', 'Write a report with LEFT JOIN, GROUP BY and HAVING',
         '<p>Write <code>city_report(customers, orders, min_total)</code>. customers is a list of (id, name, city), orders a list of (id, customer_id, amount). Return one row [city, number of customers, total amount] for each city whose total is at least min_total. Customers without orders count as customers with 0. Sort by total from high to low, then by city. Use LEFT JOIN, COUNT(DISTINCT ...), COALESCE and HAVING.</p>',
         '''
import sqlite3


def city_report(customers, orders, min_total):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE customers (id INTEGER, name TEXT, city TEXT)")
    db.execute("CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount REAL)")
    db.executemany("INSERT INTO customers VALUES (?, ?, ?)", customers)
    db.executemany("INSERT INTO orders VALUES (?, ?, ?)", orders)
    rows = db.execute("""
        SELECT c.city, COUNT(*), SUM(o.amount) AS total
        FROM customers c JOIN orders o ON o.customer_id = c.id
        GROUP BY c.city
        ORDER BY total DESC, c.city""").fetchall()
    db.close()
    return [list(row) for row in rows]


CUSTOMERS = [(1, "Ann", "Paris"), (2, "Bo", "Rome"), (3, "Cy", "Paris"), (4, "Di", "Oslo"), (5, "Ed", "Lima")]
ORDERS = [(1, 1, 30), (2, 1, 20), (3, 2, 70), (4, 3, 25), (5, 4, 10)]
''', [('city_report(CUSTOMERS, ORDERS, 0)', [['Paris', 2, 75.0], ['Rome', 1, 70.0], ['Oslo', 1, 10.0], ['Lima', 1, 0.0]]), ('city_report(CUSTOMERS, ORDERS, 50)', [['Paris', 2, 75.0], ['Rome', 1, 70.0]]), ('city_report(CUSTOMERS, [], 0)', [['Lima', 1, 0.0], ['Oslo', 1, 0.0], ['Paris', 2, 0.0], ['Rome', 1, 0.0]])],
         '''
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
''', 'Three fixes: LEFT JOIN so Lima stays, COUNT(DISTINCT c.id) because Ann has two order rows, COALESCE(SUM(...), 0.0) for cities with no orders, and HAVING total &gt;= ? for the limit.', '<p>COUNT(*) counts joined rows, not customers: Ann with two orders would be counted twice. Mistakes like this are why reports are tested with small known data.</p>')

K.must('Basics', 'sqlite3.connect(path or ":memory:"), execute, executemany, executescript, commit, close, fetchone, fetchall, lastrowid, rowcount.')
K.must('SQL', 'CREATE TABLE, INSERT, SELECT, UPDATE and DELETE with WHERE, ORDER BY, GROUP BY, HAVING, JOIN, LEFT JOIN, COUNT, SUM, COALESCE, LIMIT.')
K.must('Safety', 'Values only through ? or :name. Never f-strings in SQL. Check table and column names against a fixed list.')
K.must('Transactions', '"with conn:" commits or rolls back (does not close). IntegrityError from PRIMARY KEY, UNIQUE, NOT NULL, CHECK, foreign keys (PRAGMA foreign_keys = ON).')
K.must('Speed', 'sqlite3.Row, CREATE INDEX, EXPLAIN QUERY PLAN (SCAN vs SEARCH), one commit for many inserts, B-tree height log base f of N.')

T = K.topic(
    slug='py-sqlite', topic='py-sqlite', step=(6, 'The standard library toolbox: text, data, databases and GUIs', 'py-a6', 'Find patterns in text, read and write data formats, store data in SQLite, and build desktop windows with tkinter.', 'Advanced'),
    title='Databases with sqlite3 and SQL', short='sqlite3 and SQL', badge='6.3', minutes=90,
    lead='Store data in a real database that ships with Python. Learn SQL step by step, keep it safe from SQL injection with placeholders, make changes all or nothing with transactions, and find rows fast with indexes.',
    desc='sqlite3 connect, cursor, execute, executemany, executescript, commit, fetchone, fetchall, lastrowid, rowcount, SQL CREATE TABLE, INSERT, SELECT, WHERE, ORDER BY, GROUP BY, HAVING, JOIN, LEFT JOIN, aggregates, the logical order of a query, placeholders and SQL injection, transactions with the connection as a context manager, ACID, PRIMARY KEY, UNIQUE, NOT NULL, CHECK, foreign keys, IntegrityError, sqlite3.Row, indexes, EXPLAIN QUERY PLAN, B-tree maths and join estimates.',
    summary='sqlite3, SQL queries and joins, placeholders against injection, transactions, constraints and indexes.',
    keywords=['sqlite3', 'SQLite', 'SQL', 'database', 'JOIN', 'GROUP BY', 'SQL injection', 'transaction', 'index', 'IntegrityError'],
    recap='<p>Connect, run SQL with placeholders, group changes in "with conn:", let constraints guard the data, and add an index where EXPLAIN QUERY PLAN shows a SCAN.</p>',
    added='2026-11-07', leet=leet_items())
