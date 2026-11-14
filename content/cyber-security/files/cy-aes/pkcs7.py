# 1.2 Symmetric encryption: AES, GF(2⁸) and modes of operation
# Example "pkcs7" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# PKCS 7 padding: fill the last block with N bytes of value N
def pad(data, size=16):
    n = size - len(data) % size            # always 1 to 16 bytes, never 0
    return data + bytes([n]) * n

def unpad(data, size=16):
    n = data[-1]
    if n < 1 or n > size or data[-n:] != bytes([n]) * n:
        raise ValueError("bad padding")
    return data[:-n]

for msg in [b"HELLO", b"EXACTLY16BYTES!!", b""]:
    padded = pad(msg)
    print(len(msg), "bytes ->", len(padded), "bytes, ends with", padded[-3:].hex())

print(unpad(pad(b"HELLO")))
try:
    unpad(b"HELLO" + bytes([3, 3, 2]))
except ValueError as error:
    print("rejected:", error)
