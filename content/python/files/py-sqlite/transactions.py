# 6.3 Databases with sqlite3 and SQL
# Example "transactions" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
