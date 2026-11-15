# 3.2 Vulnerabilities: CVE, CVSS, patching and hardening
# Example "heartbleed_model" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Heartbleed (CVE-2014-0160) in miniature: a reply that trusts the length the client claims.
# The "memory" here is a Python bytearray with pretend secrets next to the request buffer.
memory = bytearray(b"HELLO" + b"|user=alice|session=9f2c|privkey=MIIEv...|" + b"." * 16)
BUF = 0                                   # the client's payload was copied to the start of memory

def heartbeat_buggy(payload_len_claimed, payload_len_real):
    # OpenSSL 1.0.1 to 1.0.1f echoed back payload_len_claimed bytes without checking the real length
    return bytes(memory[BUF:BUF + payload_len_claimed])

def heartbeat_fixed(payload_len_claimed, payload_len_real):
    # The fix in 1.0.1g: silently discard a request whose claimed length is longer than what arrived
    if payload_len_claimed > payload_len_real:
        return None
    return bytes(memory[BUF:BUF + payload_len_claimed])

print("honest request, 5 bytes:    ", heartbeat_buggy(5, 5))
print("lying request, claims 50:   ", heartbeat_buggy(50, 5))
print("same lie against the fix:   ", heartbeat_fixed(50, 5))
print("honest request against fix: ", heartbeat_fixed(5, 5))
print()
print("The length field is 16 bits, so one request could leak up to", 2 ** 16 - 1, "bytes, and attackers could repeat it.")
