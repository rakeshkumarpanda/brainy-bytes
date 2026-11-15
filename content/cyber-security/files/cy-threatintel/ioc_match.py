# 2.1 Threat intelligence: knowing the attacker
# Example "ioc_match" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Match our own logs against a feed of indicators of compromise (IOCs), and ignore indicators that have expired
from datetime import date

today = date(2026, 11, 15)
feed = [
    # value, type, date added, days it stays useful
    ("203.0.113.80", "ip", date(2026, 11, 10), 14),
    ("update-checker.example", "domain", date(2026, 10, 1), 90),
    ("198.51.100.66", "ip", date(2026, 9, 1), 14),          # old: probably reused by someone else now
    ("e3b0c44298fc1c149afbf4c8996fb924", "md5", date(2026, 11, 1), 365),
]
logs = [
    "10:01 fw ALLOW 10.0.0.22 -> 203.0.113.80:443",
    "10:02 dns QUERY update-checker.example from 10.0.0.31",
    "10:05 fw ALLOW 10.0.0.40 -> 198.51.100.66:80",
    "10:09 edr FILE written md5=e3b0c44298fc1c149afbf4c8996fb924 host PC-9",
    "10:12 dns QUERY flipkart.com from 10.0.0.22",
]

active = []
for value, kind, added, life in feed:
    age = (today - added).days
    if age <= life:
        active.append(value)
    else:
        print(f"expired, skipped: {value} ({kind}, {age} days old, useful for {life})")

print()
for line in logs:
    hits = [v for v in active if v in line]
    if hits:
        print("MATCH", hits[0], "|", line)
print("\nOld IP indicators cause false alarms, because cloud addresses are reused by new, innocent owners.")
