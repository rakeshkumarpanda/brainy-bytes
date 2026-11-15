# 2.3 Python for security: bytes, hashes, logs, packets and safe code
# Example "log_regex" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Find failed SSH logins in a log and count them per address
import re

log = """Nov 14 09:00:01 web1 sshd[811]: Failed password for root from 203.0.113.7 port 51022 ssh2
Nov 14 09:00:03 web1 sshd[811]: Failed password for root from 203.0.113.7 port 51023 ssh2
Nov 14 09:00:04 web1 sshd[812]: Accepted password for riya from 198.51.100.4 port 50110 ssh2
Nov 14 09:00:06 web1 sshd[813]: Failed password for invalid user admin from 203.0.113.7 port 51030 ssh2
Nov 14 09:00:09 web1 sshd[814]: Failed password for amit from 198.51.100.23 port 40001 ssh2
Nov 14 09:00:11 web1 sshd[815]: Failed password for root from 203.0.113.7 port 51041 ssh2
Nov 14 09:00:15 web1 CRON[900]: pam_unix(cron:session): session opened for user root
Nov 14 09:00:20 web1 sshd[816]: Failed password for amit from 198.51.100.23 port 40007 ssh2"""

pattern = re.compile(r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>[\d.]+)")

counts = {}
for line in log.splitlines():
    m = pattern.search(line)
    if m:
        ip = m.group("ip")
        counts[ip] = counts.get(ip, 0) + 1
        print("failed:", m.group("user"), "from", ip)

LIMIT = 3
for ip in counts:
    if counts[ip] >= LIMIT:
        print("BLOCK", ip, "after", counts[ip], "failures")
