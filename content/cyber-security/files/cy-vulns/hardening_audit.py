# 3.2 Vulnerabilities: CVE, CVSS, patching and hardening
# Example "hardening_audit" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A tiny configuration audit in the style of CIS Benchmarks and Lynis: compare settings with a baseline
SSHD_CONFIG = """
Port 22
PermitRootLogin yes
PasswordAuthentication yes
PubkeyAuthentication yes
X11Forwarding yes
MaxAuthTries 6
Protocol 2
"""

BASELINE = [
    # (setting, safe value, why)
    ("PermitRootLogin", "no", "log in as a normal user and use sudo, so actions are traceable"),
    ("PasswordAuthentication", "no", "keys cannot be guessed or sprayed like passwords"),
    ("PubkeyAuthentication", "yes", "needed when passwords are off"),
    ("X11Forwarding", "no", "an extra channel most servers never need"),
    ("MaxAuthTries", "4", "fewer guesses per connection"),
]

def parse(text):
    conf = {}
    for line in text.strip().splitlines():
        if line.strip() and not line.startswith("#"):
            key, value = line.split(None, 1)
            conf[key] = value.strip()
    return conf

def audit(conf):
    passed, failed = [], []
    for key, safe, why in BASELINE:
        have = conf.get(key, "(not set)")
        ok = int(have) <= int(safe) if key == "MaxAuthTries" and have.isdigit() else have.lower() == safe
        (passed if ok else failed).append((key, have, safe, why))
    return passed, failed

passed, failed = audit(parse(SSHD_CONFIG))
for key, have, safe, why in failed:
    print(f"FAIL {key:23} is {have:4} should be {safe:4} because {why}")
for key, have, safe, why in passed:
    print(f"PASS {key:23} is {have}")
print(f"score {len(passed)}/{len(BASELINE)} = {len(passed) / len(BASELINE):.0%}")

# Attack surface: every listening service is a door. Close what is not needed.
listening = {22: "ssh", 80: "http", 443: "https", 3306: "mysql", 6379: "redis", 8080: "admin panel"}
needed = {22, 443}
print("close or firewall:", ", ".join(f"{p}/{listening[p]}" for p in sorted(set(listening) - needed)))
