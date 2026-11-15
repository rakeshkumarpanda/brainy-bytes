# 2.2 RSA: keys, proofs, signatures and attacks
# Example "rsa_sign" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# RSA signatures with the toy key: hash, then sign with d, verify with e
import hashlib

n, e, d = 3233, 17, 2753                 # p = 61, q = 53

def h(message):
    # a TOY hash: the first two bytes of SHA-256, reduced below n. Real RSA uses the full hash with PSS padding.
    return int.from_bytes(hashlib.sha256(message).digest()[:2], "big") % n

def sign(message):
    return pow(h(message), d, n)

def verify(message, signature):
    return pow(signature, e, n) == h(message)

msg = b"Pay Riya 100 rupees"
s = sign(msg)
print("H(msg) =", h(msg), " signature =", s)
print("valid:", verify(msg, s))
print("changed message valid:", verify(b"Pay Riya 900 rupees", s))

# Without a hash, textbook RSA signatures can be forged
s_fake = 1000                            # pick ANY signature first
m_fake = pow(s_fake, e, n)               # then compute the message it signs
print("forged pair: message", m_fake, "signature", s_fake, "checks:", pow(s_fake, e, n) == m_fake)

# And signatures multiply: sig(a) * sig(b) is a signature on a * b
a, b = 12, 20
sa, sb = pow(a, d, n), pow(b, d, n)
print("sig(12) * sig(20) mod n signs 240:", pow(sa * sb % n, e, n) == a * b % n)
