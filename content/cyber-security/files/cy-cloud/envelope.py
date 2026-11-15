# 2.2 Cloud security: shared responsibility, identity, settings and keys
# Example "envelope" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Envelope encryption, the way a cloud KMS does it. A toy cipher built from SHA-256 keeps it to the
# standard library. Real systems use AES-256-GCM. Never use this toy for real data.
import hashlib
import os

def keystream_xor(key, data):
    out = bytearray()
    counter = 0
    while len(out) < len(data):
        out += hashlib.sha256(key + counter.to_bytes(8, "big")).digest()
        counter += 1
    return bytes(a ^ b for a, b in zip(data, out))

MASTER_V1 = os.urandom(32)               # lives only inside the KMS hardware
file_data = b"Payroll November: 214 staff, total 1,93,40,000 rupees"

data_key = os.urandom(32)                         # 1. KMS makes a fresh data key
locked_key = keystream_xor(MASTER_V1, data_key)   #    and also returns it locked with the master key
cipher = keystream_xor(data_key, file_data)       # 2. encrypt the file with the plain data key
del data_key                                      # 3. forget the plain key, store cipher + locked_key
print("stored file  :", cipher[:24].hex(), "...")
print("stored key   :", locked_key[:12].hex(), "... (locked)")

# reading: ask KMS (which checks permission and logs the call) to unlock the data key
plain_key = keystream_xor(MASTER_V1, locked_key)
print("decrypted    :", keystream_xor(plain_key, cipher).decode())

# rotating the master key: only the 32 byte data key is re-locked, not the file
MASTER_V2 = os.urandom(32)
locked_key = keystream_xor(MASTER_V2, keystream_xor(MASTER_V1, locked_key))
print("after rotation the file bytes are unchanged, and it still opens:",
      keystream_xor(keystream_xor(MASTER_V2, locked_key), cipher) == file_data)
