# 8.1 Exam practice: PCPP1 style papers
# Example "paper_c" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import csv
import heapq
import io
import json
import re
import sqlite3
from collections import Counter, defaultdict, deque, namedtuple

print("Q1", re.findall(r"\d+", "a1b22c333"), re.sub(r"(\w+)@(\w+)", r"\2 at \1", "ann@home"))
print("Q2", re.match(r"b", "abc"), bool(re.search(r"b", "abc")), re.fullmatch(r"a.c", "abc") is not None)
print("Q3", re.findall(r"<.+>", "<a><b>"), re.findall(r"<.+?>", "<a><b>"))
print("Q4", json.dumps({"b": (1, 2), "a": None}, sort_keys=True), json.loads("[1, 2.0, true]"))
rows = list(csv.reader(io.StringIO('x,"y, z",3\n')))
print("Q5", rows, type(rows[0][2]).__name__)
print("Q6", Counter("banana").most_common(2), dict(defaultdict(int, a=1)))
d = deque([1, 2, 3], maxlen=3)
d.append(4)
d.appendleft(0)
print("Q7", list(d))
nums = [5, 1, 4, 2]
heapq.heapify(nums)
print("Q8", nums[0], heapq.nsmallest(2, [5, 1, 4, 2]), heapq.heappop(nums), nums)
Point = namedtuple("Point", "x y")
p = Point(1, 2)
print("Q9", p.x + p[1], p._replace(x=9), p._asdict())
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE t (n INTEGER)")
db.executemany("INSERT INTO t VALUES (?)", [(3,), (1,), (2,)])
print("Q10", db.execute("SELECT COUNT(*), MAX(n), SUM(n) FROM t").fetchone())
