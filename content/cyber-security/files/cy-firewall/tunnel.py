# 1.2 Firewalls, intrusion detection, VPNs and zero trust
# Example "tunnel" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# What a VPN tunnel does: wrap the whole inner packet, encrypted, inside a new outer packet
# Toy cipher built from SHA-256 so it runs anywhere. Real VPNs use ChaCha20-Poly1305 or AES-GCM.
import hashlib
import hmac
import secrets

KEY = secrets.token_bytes(32)            # agreed by a handshake (WireGuard uses Noise with X25519)

def keystream(nonce, length):
    out = b""
    counter = 0
    while len(out) < length:
        out += hashlib.sha256(KEY + nonce + counter.to_bytes(4, "big")).digest()
        counter += 1
    return out[:length]

def seal(inner):
    nonce = secrets.token_bytes(12)
    body = bytes(a ^ b for a, b in zip(inner, keystream(nonce, len(inner))))
    tag = hmac.new(KEY, nonce + body, hashlib.sha256).digest()[:16]
    return nonce + body + tag

def open_(sealed):
    nonce, body, tag = sealed[:12], sealed[12:-16], sealed[-16:]
    if not hmac.compare_digest(tag, hmac.new(KEY, nonce + body, hashlib.sha256).digest()[:16]):
        return None                      # tampered or wrong key: drop the packet
    return bytes(a ^ b for a, b in zip(body, keystream(nonce, len(body))))

inner = b"src=10.8.0.2 dst=10.20.0.15 | GET /payroll HTTP/1.1"
outer = {"src": "198.51.100.20", "dst": "203.0.113.1 (VPN gateway)", "udp_port": 51820, "payload": seal(inner)}
print("on the wire, anyone sees:", outer["src"], "->", outer["dst"], "udp", outer["udp_port"])
print("payload bytes look random:", outer["payload"][:16].hex(), "...")
print("gateway opens it:", open_(outer["payload"]))
tampered = bytearray(outer["payload"])
tampered[20] ^= 1                        # flip one bit on the way
print("a changed bit is caught:", open_(bytes(tampered)))

# The cost: every packet carries extra headers, so the inner packet must be smaller
for name, overhead in (("WireGuard over IPv4", 20 + 8 + 32), ("WireGuard over IPv6", 40 + 8 + 32)):
    print(f"{name}: overhead {overhead} bytes, inner MTU = 1500 - {overhead} = {1500 - overhead}")
