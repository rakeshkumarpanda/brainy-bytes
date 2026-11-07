# 6.3 Databases with sqlite3 and SQL
# Example "queries" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
