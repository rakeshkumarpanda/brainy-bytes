# 1.1 Certificates, PKI and TLS 1.3
# Example "tls_keyschedule" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The TLS 1.3 key schedule (RFC 8446, section 7.1), checked against the RFC 8448 example handshake
import hashlib
import hmac

def hkdf_extract(salt, ikm):
    return hmac.new(salt, ikm, hashlib.sha256).digest()

def hkdf_expand_label(secret, label, context, length):
    full = b"tls13 " + label
    info = length.to_bytes(2, "big") + bytes([len(full)]) + full + bytes([len(context)]) + context
    out, block, i = b"", b"", 1
    while len(out) < length:
        block = hmac.new(secret, block + info + bytes([i]), hashlib.sha256).digest()
        out, i = out + block, i + 1
    return out[:length]

def derive_secret(secret, label, messages):
    return hkdf_expand_label(secret, label, hashlib.sha256(messages).digest(), 32)

zeros = bytes(32)
early = hkdf_extract(zeros, zeros)                        # no pre shared key
print("early secret:    ", early.hex()[:16], "...")
print("matches RFC 8448:", early.hex() == "33ad0a1c607ec03b09e6cd9893680ce210adf300aa1f2660e1b22e10f170f92a")

derived = derive_secret(early, b"derived", b"")
print("derived:         ", derived.hex()[:16], "...")
print("matches RFC 8448:", derived.hex() == "6f2615a108c702c5678f54fc9dbab69716c076189c48250cebeac3576c3611ba")

ecdhe = bytes.fromhex("8bd4054fb55b9d63fdfbacf9f04b9f0d35e6d63f537563efd46272900f89492d")   # X25519 result in RFC 8448
handshake = hkdf_extract(derived, ecdhe)
print("handshake secret:", handshake.hex()[:16], "...")
print("matches RFC 8448:", handshake.hex() == "1dc826e93606aa6fdc0aadc12f741b01046aa6b99f691ed221a9f0ca043fbeac")

master = hkdf_extract(derive_secret(handshake, b"derived", b""), zeros)
print("master secret:   ", master.hex()[:16], "...")
print("every traffic key comes from these three steps, so it depends on the fresh ECDHE value")
