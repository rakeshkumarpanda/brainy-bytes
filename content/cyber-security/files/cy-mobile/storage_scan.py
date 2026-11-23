# 4.2 Mobile security: sandboxes, permissions, signing and the OWASP Mobile Top 10
# Example "storage_scan" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Insecure data storage: scan an app's files for secrets that should never sit in plain text
import re

app_files = {
    "shared_prefs/settings.xml": '<string name="theme">dark</string><string name="auth_token">eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYXNoYSJ9.x1</string>',
    "files/log.txt": "2026-11-22 10:01 login ok user=asha password=Summer@2026",
    "databases/cache.db": "card=4111111111111111 exp=12/29",
    "res/config.json": '{"api_key": "AKIAEXAMPLEKEY123456", "region": "ap-south-1"}',
}

RULES = [
    ("JSON web token", r"eyJ[\w-]+\.[\w-]+\.[\w-]+"),
    ("password in a log", r"password=\S+"),
    ("card number", r"\b(?:\d[ -]?){13,16}\b"),
    ("cloud access key", r"AKIA[0-9A-Z]{16}"),
]

for path, text in app_files.items():
    hits = [name for name, rx in RULES if re.search(rx, text)]
    print(f"{path:28s} {'; '.join(hits) if hits else 'clean'}")

print("\nFix: keep tokens in the Android Keystore or iOS Keychain, never log passwords,")
print("never store card numbers, and keep cloud keys on the server, not inside the app.")
