# 6.3 Databases with sqlite3 and SQL
# Example "rows_index" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
