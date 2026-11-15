# 2.1 Authentication: passwords, MFA, passkeys and single sign on
# Example "totp" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# One time passwords: HOTP (RFC 4226) and TOTP (RFC 6238), checked against the RFC test vectors
import hashlib
import hmac
import struct

def hotp(secret, counter, digits=6, algo=hashlib.sha1):
    mac = hmac.new(secret, struct.pack(">Q", counter), algo).digest()   # HMAC of the 8 byte counter
    offset = mac[-1] & 0x0F                                             # dynamic truncation
    code = int.from_bytes(mac[offset:offset + 4], "big") & 0x7FFFFFFF   # 31 bits
    return str(code % 10 ** digits).zfill(digits)

def totp(secret, unix_time, step=30, digits=6, algo=hashlib.sha1):
    return hotp(secret, unix_time // step, digits, algo)                # the counter is the time slot

key = b"12345678901234567890"
print("RFC 4226 HOTP, counter 0:", hotp(key, 0), "(expected 755224)")
print("RFC 4226 HOTP, counter 1:", hotp(key, 1), "(expected 287082)")
print("RFC 6238 TOTP SHA-1, t = 59:", totp(key, 59, digits=8), "(expected 94287082)")
key256 = b"12345678901234567890123456789012"
print("RFC 6238 TOTP SHA-256, t = 59:", totp(key256, 59, digits=8, algo=hashlib.sha256), "(expected 46119246)")

# The server accepts the current slot and one either side, to allow for clock drift
def verify(secret, code, now, window=1):
    return any(totp(secret, now + d * 30) == code for d in range(-window, window + 1))

now = 1_700_000_000
code = totp(key, now)
print("code", code, "accepted now:", verify(key, code, now), "| 25 s later:", verify(key, code, now + 25), "| 2 min later:", verify(key, code, now + 120))
print("chance a random guess hits one of 3 slots:", 3 / 10 ** 6)
