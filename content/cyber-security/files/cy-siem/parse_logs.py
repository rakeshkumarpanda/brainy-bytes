# 1.1 Logging, monitoring and the SIEM
# Example "parse_logs" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Turn log lines from three different systems into one common shape (a dictionary with the same keys)
import json
import re

RAW_LINES = [
    "Nov 15 09:12:04 web1 sshd[811]: Failed password for root from 203.0.113.9 port 52144 ssh2",
    "EventID=4625 Time=2026-11-15T09:12:09Z Account=asha Source=203.0.113.9 Host=PC-22",
    '{"ts": "2026-11-15T09:12:30Z", "event": "login", "user": "asha", "ip": "203.0.113.9", "ok": true}',
    "Nov 15 09:14:40 web1 sshd[815]: Accepted password for deploy from 10.0.0.5 port 50001 ssh2",
]

SSH_PATTERN = re.compile(r"(\w+ +\d+ [\d:]+) (\S+) sshd\[\d+\]: (Failed|Accepted) password for (\S+) from (\S+)")


def parse(line):
    """Return one event as a dictionary, or None if we do not know this format."""
    match = SSH_PATTERN.search(line)
    if match:
        time, host, word, user, ip = match.groups()
        result = "failure" if word == "Failed" else "success"
        return {"time": time, "host": host, "user": user, "ip": ip, "action": "logon", "outcome": result, "source": "sshd"}
    if line.startswith("EventID="):
        fields = dict(part.split("=", 1) for part in line.split())
        result = "failure" if fields["EventID"] == "4625" else "success"   # 4625 failed logon, 4624 success
        return {"time": fields["Time"], "host": fields["Host"], "user": fields["Account"], "ip": fields["Source"],
                "action": "logon", "outcome": result, "source": "windows"}
    if line.startswith("{"):
        data = json.loads(line)
        result = "success" if data["ok"] else "failure"
        return {"time": data["ts"], "host": "shop-app", "user": data["user"], "ip": data["ip"],
                "action": "logon", "outcome": result, "source": "webapp"}
    return None


events = []
for line in RAW_LINES:
    event = parse(line)
    events.append(event)
    print(f"{event['source']:8} {event['user']:7} {event['ip']:12} {event['outcome']}")

# Now one simple search works across every source
bad_ip = "203.0.113.9"
hits = [e for e in events if e["ip"] == bad_ip]
print(f"\nEvents from {bad_ip}: {len(hits)}")
for e in hits:
    print("   ", e["source"], e["user"], e["outcome"])
