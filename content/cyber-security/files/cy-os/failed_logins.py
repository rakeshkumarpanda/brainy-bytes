# 2.1 Operating systems: users, permissions, processes and logs
# Example "failed_logins" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Windows writes event 4625 for every failed logon. Many failures for one account in a short time look like guessing.
events = [
    ("09:00:01", 4625, "admin"), ("09:00:02", 4625, "admin"), ("09:00:03", 4625, "admin"),
    ("09:00:04", 4625, "admin"), ("09:00:05", 4625, "admin"), ("09:00:09", 4624, "admin"),
    ("09:10:00", 4625, "riya"), ("09:12:30", 4624, "riya"),
]

failures = {}
for time, event_id, account in events:
    if event_id == 4625:
        failures[account] = failures.get(account, 0) + 1

limit = 5
for account, count in failures.items():
    if count >= limit:
        print(account, "had", count, "failed logons: possible password guessing")
    else:
        print(account, "had", count, "failed logon(s): normal")

# A failure burst followed by a success (4624) is the worst sign: the guess may have worked
for i in range(1, len(events)):
    if events[i][1] == 4624 and events[i - 1][1] == 4625 and failures.get(events[i][2], 0) >= limit:
        print("ALERT: success after many failures for", events[i][2], "at", events[i][0])
