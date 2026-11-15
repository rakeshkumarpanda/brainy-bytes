# 1.3 Hash functions, MACs and password storage
# Example "passwords" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Storing passwords: why fast hashes fail, and the right way with a salt and a slow function
import hashlib
import hmac
import os
import time

# 1. A leaked table of unsalted MD5 hashes, and a dictionary attack
leaked = {"riya": hashlib.md5(b"sunshine").hexdigest(), "amit": hashlib.md5(b"Tr0ub4dor&3").hexdigest()}
wordlist = ["123456", "password", "qwerty", "sunshine", "iloveyou"]
for user in leaked:
    for word in wordlist:
        if hashlib.md5(word.encode()).hexdigest() == leaked[user]:
            print(user, "cracked:", word)

# 2. The right way: a random salt per user and a slow, memory hard function
def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1)   # OWASP suggests n=2**17
    return salt, digest

def check_password(password, salt, digest):
    test = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1)
    return hmac.compare_digest(test, digest)

salt, digest = hash_password("sunshine")
print("right password:", check_password("sunshine", salt, digest))
print("wrong password:", check_password("Sunshine", salt, digest))

salt2, digest2 = hash_password("sunshine")
print("two users with the same password get the same hash:", digest == digest2)

# 3. The cost per guess: PBKDF2-HMAC-SHA256 with OWASP's 600,000 iterations
start = time.perf_counter()
hashlib.pbkdf2_hmac("sha256", b"sunshine", os.urandom(16), 600_000)
print("one PBKDF2 guess took about", round(time.perf_counter() - start, 2), "seconds")
