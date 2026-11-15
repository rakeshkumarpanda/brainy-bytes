# 2.1 Authentication: passwords, MFA, passkeys and single sign on
# Example "password_policy" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Modern password rules (NIST SP 800-63B): length, a breached list, and rate limiting
import hashlib
import math

breached = {"password", "123456", "qwerty123", "iloveyou", "Summer2024!", "qwerty123qwerty"}     # tiny stand in for real lists
breached_sha1 = {hashlib.sha1(w.encode()).hexdigest().upper() for w in breached}

def k_anonymity_check(pw):
    # like the Have I Been Pwned range API: send only the first 5 hex chars, compare the rest locally
    h = hashlib.sha1(pw.encode()).hexdigest().upper()
    prefix, suffix = h[:5], h[5:]
    bucket = [x[5:] for x in breached_sha1 if x.startswith(prefix)]          # what the server would return
    return suffix in bucket, prefix

def check(pw, only_factor=True):
    need = 15 if only_factor else 8
    if len(pw) < need:
        return f"too short: {len(pw)} < {need}"
    hit, prefix = k_anonymity_check(pw)
    if hit:
        return f"found in a breach (sent only {prefix} to the checker)"
    return "ok"

for pw in ["Summer2024!", "Tr0ub4dor&3", "correct horse battery staple", "qwerty123qwerty"]:
    print(f"{pw!r:32} -> {check(pw)}")

# Online guessing: rate limits make even short PINs survive
for label, tries in (("10 tries then lock", 10), ("100 tries per day for a year", 36500)):
    print(f"6 digit PIN, {label}: chance of success {tries / 10 ** 6:.4%}")
print("bits in a 4 word passphrase from a 7776 word list:", round(4 * math.log2(7776), 1))
