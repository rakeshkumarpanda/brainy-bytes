# 2.2 Secure development: threat models, scanners, fuzzing and the supply chain
# Example "sast_scan" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A tiny static analyser (in the spirit of Bandit or Semgrep): walk the syntax tree of Python code
# and flag dangerous calls. The code being scanned is only parsed, never run.
import ast

SOURCE = """
import pickle, subprocess, sqlite3
DB_PASSWORD = "hunter2"

def search(db, term):
    return db.execute(f"SELECT * FROM items WHERE name = '{term}'")

def ping(host):
    subprocess.run("ping -c 1 " + host, shell=True)

def load(blob):
    return pickle.loads(blob)

def calc(expr):
    return eval(expr)

def safe_search(db, term):
    return db.execute("SELECT * FROM items WHERE name = ?", (term,))
"""

class Scanner(ast.NodeVisitor):
    def __init__(self):
        self.findings = []

    def add(self, node, rule, msg):
        self.findings.append((node.lineno, rule, msg))

    def visit_Call(self, node):
        name = ast.unparse(node.func)
        if name in ("eval", "exec"):
            self.add(node, "B307", f"{name}() runs any code it is given")
        if name in ("pickle.loads", "pickle.load"):
            self.add(node, "B301", "unpickling untrusted data can run code")
        if any(k.arg == "shell" and getattr(k.value, "value", False) is True for k in node.keywords):
            self.add(node, "B602", "subprocess with shell=True, injection risk")
        if name.endswith(".execute") and node.args and isinstance(node.args[0], (ast.JoinedStr, ast.BinOp)):
            self.add(node, "B608", "SQL built with an f-string or +, use ? placeholders")
        self.generic_visit(node)

    def visit_Assign(self, node):
        for t in node.targets:
            if isinstance(t, ast.Name) and "PASSWORD" in t.id.upper() and isinstance(node.value, ast.Constant):
                self.add(node, "B105", f"hard coded password in {t.id}")
        self.generic_visit(node)

s = Scanner()
s.visit(ast.parse(SOURCE))
for line, rule, msg in sorted(s.findings):
    print(f"line {line:2}  {rule}  {msg}")
print(f"{len(s.findings)} findings. safe_search on line 18 is not flagged, because it uses placeholders.")
