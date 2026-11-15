# 1.2 Injection: SQL, blind SQL, commands, SSRF and paths
# Example "sqli_demo" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# SQL injection on an in-memory SQLite database, and the fix: parameterised queries
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE users (id INTEGER, name TEXT, password_hash TEXT, role TEXT);
INSERT INTO users VALUES (1, 'alice', 'h_7f3a', 'admin'), (2, 'bob', 'h_91cc', 'user');
CREATE TABLE cards (owner TEXT, number TEXT);
INSERT INTO cards VALUES ('alice', '4111-1111-1111-1111'), ('bob', '5500-0000-0000-0004');
""")

def login_buggy(name, pw_hash):
    sql = f"SELECT name, role FROM users WHERE name = '{name}' AND password_hash = '{pw_hash}'"
    print("   SQL:", sql)
    return db.execute(sql).fetchall()

def login_safe(name, pw_hash):
    sql = "SELECT name, role FROM users WHERE name = ? AND password_hash = ?"
    return db.execute(sql, (name, pw_hash)).fetchall()      # data is sent apart from the query

print("1. normal login:")
print("  ", login_buggy("bob", "h_91cc"))
print("2. attacker types  alice' --  as the user name and anything as the password:")
print("  ", login_buggy("alice' --", "x"), " <- logged in as admin without a password")
print("3. attacker types  ' OR '1'='1  in both boxes:")
print("  ", login_buggy("' OR '1'='1", "' OR '1'='1"), " <- every row")

def search_buggy(term):
    sql = f"SELECT name FROM users WHERE name LIKE '%{term}%'"
    return db.execute(sql).fetchall()

print("4. UNION attack on a search box reads another table:")
print("  ", search_buggy("zzz' UNION SELECT owner || ': ' || number FROM cards --"))
print("5. the same inputs against the parameterised version:")
print("  ", login_safe("alice' --", "x"), login_safe("' OR '1'='1", "' OR '1'='1"), "<- treated as plain text, no match")
