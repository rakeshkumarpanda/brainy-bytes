# 2.2 Secure development: threat models, scanners, fuzzing and the supply chain
# Example "secret_scan" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Secret scanning: find keys and passwords committed to code, using known patterns plus entropy
import math, re
from collections import Counter

FILES = {
    "config.py": 'DEBUG = True\nAWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"\nREGION = "ap-south-1"\n',
    "deploy.sh": 'export API_TOKEN="q8Zr3VbN1xTt6YwP0kLm9sDf2GhJ4cXe"\necho "deploying build 4417"\n',
    "README.md": "Set your token in the environment. Example: TOKEN=changeme\n",
    "id_rsa": "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAA...\n",
}
PATTERNS = {
    "AWS access key id": r"\bAKIA[0-9A-Z]{16}\b",
    "private key file": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}

def entropy(s):
    n = len(s)
    return -sum(c / n * math.log2(c / n) for c in Counter(s).values())

for name, text in FILES.items():
    for label, pat in PATTERNS.items():
        for m in re.finditer(pat, text):
            print(f"{name:10} pattern  {label}: {m.group(0)[:24]}")
    for m in re.finditer(r'"([A-Za-z0-9+/=_-]{20,})"', text):     # long quoted strings
        h = entropy(m.group(1))
        if h > 4.0:
            print(f"{name:10} entropy  {h:.2f} bits per character in {m.group(1)[:12]}... looks like a random secret")
print("AKIAIOSFODNN7EXAMPLE is the documented example key from AWS, never a real one.")
print("Found a real secret? Revoke and rotate it first: deleting the commit does not remove it from clones.")
