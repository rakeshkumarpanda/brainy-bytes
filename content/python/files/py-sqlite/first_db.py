# 6.3 Databases with sqlite3 and SQL
# Example "first_db" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
