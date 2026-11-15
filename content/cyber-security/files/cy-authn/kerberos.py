# 2.1 Authentication: passwords, MFA, passkeys and single sign on
# Example "kerberos" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Kerberos in miniature: a trusted KDC hands out tickets so passwords never cross the network
# Toy authenticated encryption from SHA-256 and HMAC. Real Kerberos uses AES (RFC 3962, RFC 8009).
import hashlib
import hmac
import json
import secrets

def stream(key, nonce, n):               # keystream: SHA-256 of key, nonce and a counter
    return b"".join(hashlib.sha256(key + nonce + i.to_bytes(4, "big")).digest() for i in range(n // 32 + 1))

def seal(key, obj):
    data = json.dumps(obj).encode()
    nonce = secrets.token_bytes(12)
    body = bytes(a ^ b for a, b in zip(data, stream(key, nonce, len(data))))
    return nonce + body + hmac.new(key, nonce + body, hashlib.sha256).digest()

def unseal(key, blob):
    nonce, body, tag = blob[:12], blob[12:-32], blob[-32:]
    if not hmac.compare_digest(tag, hmac.new(key, nonce + body, hashlib.sha256).digest()):
        raise ValueError("wrong key or tampered ticket")
    return json.loads(bytes(a ^ b for a, b in zip(body, stream(key, nonce, len(body)))))

def key_from_password(pw, salt):         # real Kerberos: PBKDF2 string to key
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 10000)

# Long term keys, known to the KDC only
asha_key = key_from_password("Correct-Horse-41", "EXAMPLE.ORGasha")
krbtgt_key = secrets.token_bytes(32)     # the KDC's own key. Stealing it allows "golden tickets".
files_key = secrets.token_bytes(32)      # the file server's key

# 1. AS exchange: Asha asks for a ticket granting ticket (TGT). No password is sent.
s1 = secrets.token_bytes(16).hex()
tgt = seal(krbtgt_key, {"user": "asha", "session": s1, "expires": 36000})
as_reply = seal(asha_key, {"session": s1})           # only someone with Asha's password can open this
s1_client = unseal(key_from_password("Correct-Horse-41", "EXAMPLE.ORGasha"), as_reply)["session"]
print("1. Asha opened the AS reply with her password: session key", s1_client[:8], "...")

# 2. TGS exchange: show the TGT and ask for a ticket to the file server
inside = unseal(krbtgt_key, tgt)                    # the KDC reads its own TGT
s2 = secrets.token_bytes(16).hex()
service_ticket = seal(files_key, {"user": inside["user"], "session": s2})
tgs_reply = seal(bytes.fromhex(inside["session"]), {"session": s2})
s2_client = unseal(bytes.fromhex(s1_client), tgs_reply)["session"]
print("2. Got a service ticket for the file server")

# 3. AP exchange: the file server opens the ticket with its own key, no call to the KDC needed
print("3. File server sees user:", unseal(files_key, service_ticket)["user"], "| shared session key matches:", unseal(files_key, service_ticket)["session"] == s2_client)

# A wrong password cannot open the AS reply
try:
    unseal(key_from_password("guess123", "EXAMPLE.ORGasha"), as_reply)
except ValueError as e:
    print("wrong password:", e)
