# 1.2 Incident response: from the first alert to lessons learned
# Example "ir_metrics" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Incident metrics from timelines: time to detect, time to contain, time to recover (in hours)
from datetime import datetime

def hours(a, b):
    fmt = "%Y-%m-%d %H:%M"
    return (datetime.strptime(b, fmt) - datetime.strptime(a, fmt)).total_seconds() / 3600

# start of attack, detected, contained, recovered
incidents = {
    "phishing account": ("2026-03-02 08:10", "2026-03-02 09:40", "2026-03-02 10:05", "2026-03-02 13:00"),
    "ransomware FS-02": ("2026-05-18 01:00", "2026-05-18 03:30", "2026-05-18 04:15", "2026-05-19 18:00"),
    "web shell": ("2026-07-01 12:00", "2026-07-09 12:00", "2026-07-09 15:00", "2026-07-10 09:00"),
}
detect, contain, recover = [], [], []
for name, (start, found, held, back) in incidents.items():
    d, c, r = hours(start, found), hours(found, held), hours(held, back)
    detect.append(d); contain.append(c); recover.append(r)
    print(f"{name:17} detect {d:6.1f} h   contain {c:4.2f} h   recover {r:5.1f} h")

n = len(incidents)
print(f"\nMTTD {sum(detect) / n:.1f} h, mean time to contain {sum(contain) / n:.2f} h, mean time to recover {sum(recover) / n:.1f} h")
print("The web shell went unseen for 8 days. That number, not the others, is where to invest first.")
