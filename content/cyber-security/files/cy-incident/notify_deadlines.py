# 1.2 Incident response: from the first alert to lessons learned
# Example "notify_deadlines" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Who must be told, and by when? Deadlines counted from when the team became aware of the incident.
from datetime import datetime, timedelta

aware = datetime(2026, 11, 12, 22, 30)      # a Thursday, 22:30

def add_business_days(start, days):
    day = start
    while days > 0:
        day += timedelta(days=1)
        if day.weekday() < 5:                 # Monday is 0, Friday is 4
            days -= 1
    return day

deadlines = [
    ("CERT-In, India (report within 6 hours)", aware + timedelta(hours=6)),
    ("EU NIS2 early warning (24 hours)", aware + timedelta(hours=24)),
    ("GDPR supervisory authority (72 hours)", aware + timedelta(hours=72)),
    ("US SEC Form 8-K (4 business days after deciding it is material)", add_business_days(aware, 4)),
]
print("aware:", aware.strftime("%a %d %b %H:%M"))
for who, when in deadlines:
    print(f"{when.strftime('%a %d %b %H:%M')}  {who}")
print("\nKeep a lawyer and the data protection officer in the loop. Rules depend on the country and the sector.")
