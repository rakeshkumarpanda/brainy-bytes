# 2.1 Authentication: passwords, MFA, passkeys and single sign on
# Example "passkey" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Why passkeys stop phishing: the signature covers the website's origin, so a look alike site gets nothing useful
# Toy Schnorr signatures in a small group (from the zero knowledge chapter). Real passkeys use ECDSA P-256 or Ed25519.
import hashlib
import secrets

p = 1099511628443                        # toy safe prime, q = (p - 1) / 2 is prime
q = (p - 1) // 2
g = 4

def H(*parts):
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big") % q

# Registration: the authenticator makes a new key pair just for this site. The server keeps only the public key.
private = secrets.randbelow(q)
public = pow(g, private, p)
registered_origin = "https://bank.example"

def authenticator_sign(challenge, origin):
    # the browser, not the user, fills in the origin it is really talking to
    r = secrets.randbelow(q)
    t = pow(g, r, p)
    c = H(t, challenge, origin)
    return origin, t, (r + c * private) % q

def server_verify(challenge, response):
    origin, t, s = response
    if origin != registered_origin:
        return "rejected: signed for " + origin
    c = H(t, challenge, origin)
    return "accepted" if pow(g, s, p) == t * pow(public, c, p) % p else "rejected: bad signature"

challenge = secrets.token_hex(16)        # fresh random challenge from the real bank
print("user on the real site:", server_verify(challenge, authenticator_sign(challenge, "https://bank.example")))

# A phishing site relays the bank's challenge, but the browser signs the phishing origin
relayed = authenticator_sign(challenge, "https://bank-example.login.test")
print("phisher relays it:    ", server_verify(challenge, relayed))

# Changing the origin field after signing breaks the signature
origin, t, s = relayed
print("phisher edits origin: ", server_verify(challenge, ("https://bank.example", t, s)))
print("replay of an old login:", server_verify(secrets.token_hex(16), authenticator_sign(challenge, "https://bank.example")))
