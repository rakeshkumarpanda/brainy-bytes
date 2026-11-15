# 1.1 Logging, monitoring and the SIEM
# Example "brute_rule" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A detection rule: alert when one source IP has N or more failed logins inside W minutes.
# A second rule: a success from the same IP soon after that alert means the guessing may have worked.
from collections import defaultdict, deque

N = 5      # how many failures
W = 5      # inside how many minutes

# (minute, source ip, user, outcome) in time order
events = [
    (1, "198.51.100.4", "ravi", "failure"),
    (4, "198.51.100.4", "ravi", "success"),           # one typo, then fine: normal
    (10, "203.0.113.9", "admin", "failure"),
    (11, "203.0.113.9", "admin", "failure"),
    (11, "203.0.113.9", "root", "failure"),
    (12, "203.0.113.9", "admin", "failure"),
    (12, "203.0.113.9", "test", "failure"),
    (13, "203.0.113.9", "admin", "failure"),
    (15, "203.0.113.9", "admin", "success"),          # guessed it
]

recent = defaultdict(deque)     # ip -> minutes of recent failures
alerted = {}                    # ip -> minute of the alert

for minute, ip, user, outcome in events:
    window = recent[ip]
    while window and window[0] <= minute - W:      # forget failures older than W minutes
        window.popleft()
    if outcome == "failure":
        window.append(minute)
        if len(window) >= N and ip not in alerted:
            alerted[ip] = minute
            print(f"minute {minute:2}: ALERT brute force from {ip}, {len(window)} failures in {W} minutes")
    elif ip in alerted:
        print(f"minute {minute:2}: CRITICAL {ip} logged in as {user} after a brute force alert. Lock the account now.")

print("\nIPs alerted:", list(alerted))
print("The single typo from 198.51.100.4 raised nothing, which is what we want.")
