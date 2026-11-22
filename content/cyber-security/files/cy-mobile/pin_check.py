# 4.2 Mobile security: sandboxes, permissions, signing and the OWASP Mobile Top 10
# Example "pin_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Certificate pinning: compare the hash of the server's public key with a value built into the app
import base64
import hashlib

def spki_pin(public_key_bytes):
    return base64.b64encode(hashlib.sha256(public_key_bytes).digest()).decode()

BANK_KEY = b"bank.example public key bytes (real apps hash the DER encoded SubjectPublicKeyInfo)"
BACKUP_KEY = b"bank.example backup key, kept offline for rotation"
PINS = {spki_pin(BANK_KEY), spki_pin(BACKUP_KEY)}      # always pin a backup key too

def connect(presented_key, chain_trusted):
    if not chain_trusted:
        return "refused: certificate chain not trusted"
    if spki_pin(presented_key) not in PINS:
        return "refused: public key does not match the pin"
    return "connected"

print("pin of the real key:", spki_pin(BANK_KEY)[:24], "...")
print("home Wi-Fi, real certificate        ->", connect(BANK_KEY, chain_trusted=True))
print("café Wi-Fi, fake cert, user CA      ->", connect(b"attacker key", chain_trusted=True))
print("after the bank rotates to backup key ->", connect(BACKUP_KEY, chain_trusted=True))
