# 6.3 Databases with sqlite3 and SQL
# Example "params" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
