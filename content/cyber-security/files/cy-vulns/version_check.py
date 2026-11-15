# 3.2 Vulnerabilities: CVE, CVSS, patching and hardening
# Example "version_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Is this version vulnerable? Compare dotted versions as numbers, not as text, against known affected ranges.
def parse(v):
    return tuple(int(part) for part in v.split("."))

# Affected ranges for Log4Shell family bugs in Apache Log4j 2, from the Apache Log4j security page.
# Simplified: the real advisories also list fixed backports on older branches (2.12.x for Java 7, 2.3.x for Java 6).
ADVISORIES = [
    ("CVE-2021-44228 (Log4Shell)", "2.0.0", "2.15.0"),   # affected from 2.0.0 up to, not including, 2.15.0
    ("CVE-2021-45046", "2.0.0", "2.16.0"),
    ("CVE-2021-45105", "2.0.0", "2.17.0"),
    ("CVE-2021-44832", "2.0.0", "2.17.1"),
]

def check(version):
    v = parse(version)
    return [cve for cve, low, fixed in ADVISORIES if parse(low) <= v < parse(fixed)]

print("text comparison says '2.9.1' > '2.15.0':", "2.9.1" > "2.15.0", "(wrong)")
print("number comparison says (2,9,1) > (2,15,0):", parse("2.9.1") > parse("2.15.0"), "(right)")
print()
inventory = {"payments-api": "2.14.1", "search": "2.9.1", "intranet": "2.16.0", "reports": "2.17.0", "new-app": "2.20.0"}
for app, ver in inventory.items():
    hits = check(ver)
    status = "VULNERABLE to " + ", ".join(hits) if hits else "no known Log4j 2 issue in this list"
    print(f"{app:13} log4j {ver:7} {status}")
