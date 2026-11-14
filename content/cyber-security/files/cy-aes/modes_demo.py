# 1.2 Symmetric encryption: AES, GF(2⁸) and modes of operation
# Example "modes_demo" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Block cipher modes: why ECB leaks patterns and CBC and CTR do not
import hashlib
import hmac

def round_function(half, key, r):           # any mixing function works inside a Feistel network
    return hmac.new(key, bytes([r]) + half, hashlib.sha256).digest()[:8]

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def encrypt_block(block, key):              # a 16 byte Feistel block cipher, the structure DES used
    left, right = block[:8], block[8:]
    for r in range(4):
        left, right = right, xor(left, round_function(right, key, r))
    return left + right

def decrypt_block(block, key):              # the same rounds backwards: round_function is never inverted
    left, right = block[:8], block[8:]
    for r in range(3, -1, -1):
        left, right = xor(right, round_function(left, key, r)), left
    return left + right

def blocks(data):
    return [data[i:i + 16] for i in range(0, len(data), 16)]

key = b"a demo key only"
message = b"PAY RIYA 100 RS." * 3 + b"PAY AMIT 500 RS."      # four 16 byte blocks, three the same

ecb = [encrypt_block(b, key) for b in blocks(message)]
print("ECB:")
for c in ecb:
    print("  ", c.hex())

iv = bytes(16)                               # use a random IV in real life: secrets.token_bytes(16)
prev, cbc = iv, []
for b in blocks(message):
    c = encrypt_block(xor(b, prev), key)
    cbc.append(c)
    prev = c
print("CBC:")
for c in cbc:
    print("  ", c.hex())

nonce = b"nonce123"
ctr = []
for i, b in enumerate(blocks(message)):
    pad = encrypt_block(nonce + i.to_bytes(8, "big"), key)
    ctr.append(xor(b, pad))
print("CTR:")
for c in ctr:
    print("  ", c.hex())

back = b"".join(decrypt_block(c, key) for c in ecb)
print("ECB decrypts back:", back == message)
