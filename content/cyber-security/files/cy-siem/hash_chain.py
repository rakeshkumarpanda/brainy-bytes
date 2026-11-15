# 1.1 Logging, monitoring and the SIEM
# Example "hash_chain" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A tamper evident log: each record stores HMAC(key, previous tag + text). Change or delete one line and
# the check fails at that point. The key lives on a separate server, so the intruder cannot rebuild the tags.
import hashlib
import hmac

KEY = b"kept-on-the-log-server"     # in real life: a secret from a vault, never in code

def tag(prev, text):
    return hmac.new(KEY, (prev + "|" + text).encode(), hashlib.sha256).hexdigest()[:12]

def write_log(lines):
    records, prev = [], "start"
    for text in lines:
        prev = tag(prev, text)
        records.append([text, prev])
    return records

def first_broken(records):
    prev = "start"
    for i, (text, stored) in enumerate(records):
        if tag(prev, text) != stored:
            return i + 1                    # line number, counting from 1
        prev = stored
    return None

log = write_log(["09:00 asha logged in", "09:05 asha opened payroll.xlsx",
                 "09:07 asha exported 900 rows", "09:09 asha deleted export.csv", "09:10 asha logged out"])
print("untouched log, first broken line:", first_broken(log))

edited = [r[:] for r in log]
edited[2][0] = "09:07 asha exported 9 rows"
print("after editing line 3, first broken line:", first_broken(edited))

deleted = log[:3] + log[4:]
print("after deleting line 4, first broken line:", first_broken(deleted))
