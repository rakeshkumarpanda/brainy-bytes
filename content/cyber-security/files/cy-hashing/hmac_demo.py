# 1.3 Hash functions, MACs and password storage
# Example "hmac_demo" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# HMAC built by hand, compared with Python's hmac module
import hashlib
import hmac

def my_hmac(key, message):
    if len(key) > 64:
        key = hashlib.sha256(key).digest()       # long keys are hashed first
    key = key + bytes(64 - len(key))             # pad to the 64 byte block size
    inner_key = bytes(b ^ 0x36 for b in key)     # ipad
    outer_key = bytes(b ^ 0x5C for b in key)     # opad
    inner = hashlib.sha256(inner_key + message).digest()
    return hashlib.sha256(outer_key + inner).hexdigest()

key = b"shared secret"
msg = b"PAY RIYA 100"
print("by hand :", my_hmac(key, msg))
print("library :", hmac.new(key, msg, hashlib.sha256).hexdigest())

# RFC 4231 test case 2
print("RFC 4231:", my_hmac(b"Jefe", b"what do ya want for nothing?"))

# The receiver checks a tag in constant time
received = hmac.new(key, msg, hashlib.sha256).hexdigest()
print("genuine :", hmac.compare_digest(received, my_hmac(key, msg)))
print("changed :", hmac.compare_digest(received, my_hmac(key, b"PAY RIYA 900")))
