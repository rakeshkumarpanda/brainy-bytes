# 4.2 Mobile security: sandboxes, permissions, signing and the OWASP Mobile Top 10
# Example "apk_hash" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Why a repackaged app cannot pass as an update: the signature covers a hash of every byte
import hashlib
import hmac

def digest(app_bytes):
    return hashlib.sha256(app_bytes).hexdigest()

# a stand in for a real signature: only the holder of the key can produce the tag
DEV_KEY = b"developer signing key kept in a hardware module"
ATTACKER_KEY = b"some other key"

def sign(app_bytes, key):
    return hmac.new(key, app_bytes, hashlib.sha256).hexdigest()

def install_update(app_bytes, tag, installed_key):
    expected = sign(app_bytes, installed_key)
    return "installed" if hmac.compare_digest(expected, tag) else "REFUSED: not signed by the same key"

real = b"BrainyBank v2.1: login, balance, transfer"
evil = real + b", send_sms_to_attacker()"
print("real app hash :", digest(real)[:32])
print("evil app hash :", digest(evil)[:32])

print("genuine update           ->", install_update(real, sign(real, DEV_KEY), DEV_KEY))
print("evil app, old signature  ->", install_update(evil, sign(real, DEV_KEY), DEV_KEY))
print("evil app, attacker key   ->", install_update(evil, sign(evil, ATTACKER_KEY), DEV_KEY))
print("\nReal Android signing uses RSA, ECDSA or Ed25519 public key signatures (APK scheme v2 and later),")
print("so the phone needs only the public key. HMAC is used here to keep the example short.")
