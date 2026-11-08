# 6.1 API security: passwords, JWT, OAuth 2.0, CORS and OWASP
# Example "passwords" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# Storing passwords: never the password, never a fast hash, always a slow salted hash.
import base64
import hashlib
import hmac
import secrets
import time

print("1. A plain fast hash is not enough")
for pw in ["sunshine", "sunshine", "Sunshine1"]:
    print(f"   sha256({pw!r:12}) = {hashlib.sha256(pw.encode()).hexdigest()[:24]}...")
print("   The same password always gives the same hash, so one stolen table of")
print("   precomputed hashes (a rainbow table) cracks every user who picked it.")


def hash_password(password, iterations=600_000, salt=None):
    """Return a Django style string: algorithm$iterations$salt$hash."""
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${base64.b64encode(digest).decode()}"


def check_password(password, stored):
    algorithm, iterations, salt, _ = stored.split("$")
    again = hash_password(password, int(iterations), salt)
    return hmac.compare_digest(again, stored)


print("\n2. A salted slow hash (PBKDF2, the default in Django)")
a = hash_password("sunshine", salt="Qx81LmZ0aa7Kc3d1")
b = hash_password("sunshine", salt="pW2nB7tRr4Ee9oYs")
print("   ann:", a[:60] + "...")
print("   ben:", b[:60] + "...")
print("   same password, different salt, different hash:", a != b)
print("   check 'sunshine' :", check_password("sunshine", a))
print("   check 'sunshine!':", check_password("sunshine!", a))

print("\n3. Slow on purpose")
for rounds in [1_000, 100_000, 600_000]:
    start = time.perf_counter()
    hash_password("sunshine", rounds, "fixedsalt")
    ms = (time.perf_counter() - start) * 1000
    print(f"   {rounds:>7,} rounds: {ms:7.1f} ms per guess")
print("   One login waits a fraction of a second. An attacker with a list of a")
print("   billion guesses must pay that cost a billion times for every user.")

print("\n4. scrypt also needs lots of memory, which slows down graphics cards")
digest = hashlib.scrypt(b"sunshine", salt=b"Qx81LmZ0aa7Kc3d1", n=2**14, r=8, p=1)
print("   scrypt:", digest.hex()[:32] + "...", f"({128 * 2**14 * 8 // 2**20} MB of memory per guess)")

print("\n5. Secrets for tokens come from the secrets module, never from random")
print("   API key      :", len(secrets.token_urlsafe(32)), "characters from 32 random bytes")
print("   reset code   :", len(f"{secrets.randbelow(10**6):06d}"), "digits")
print("   random.random() is predictable once an attacker sees a few outputs.")
