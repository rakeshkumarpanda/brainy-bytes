# 6.1 Regular expressions
# Example "parsing" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import re

LINE = re.compile(r"""
    (?P<date>\d{4}-\d{2}-\d{2})\s
    (?P<time>\d{2}:\d{2}:\d{2})\s
    (?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s
    (?P<logger>[\w.]+):\s
    (?P<message>.*)
""", re.VERBOSE)

logs = [
    "2026-11-07 10:00:01 ERROR shop.pay: card declined for order 1042",
    "this line is broken",
    "2026-11-07 10:00:05 INFO shop.cart: order 1043 saved",
]
for line in logs:
    m = LINE.fullmatch(line)
    if m is None:
        print("skipped:", line)
        continue
    order = re.search(r"order (\d+)", m["message"])
    print(m["level"], m["logger"], order.group(1) if order else None)
