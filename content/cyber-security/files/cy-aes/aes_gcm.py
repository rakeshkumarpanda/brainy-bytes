# 1.2 Symmetric encryption: AES, GF(2⁸) and modes of operation
# Example "aes_gcm" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Real AES-256-GCM with the cryptography package (pip install cryptography)
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

key = AESGCM.generate_key(bit_length=256)
aes = AESGCM(key)
nonce = os.urandom(12)                     # 96 bits, NEW for every message with this key
header = b"order 1044"                     # sent in clear, but protected against changes

sealed = aes.encrypt(nonce, b"PAY RIYA 100 RS.", header)
print(len(sealed), "bytes = 16 bytes of message + 16 byte tag")
print("opened:", aes.decrypt(nonce, sealed, header))

changed = bytearray(sealed)
changed[0] = changed[0] ^ 1                # an attacker flips one bit
try:
    aes.decrypt(nonce, bytes(changed), header)
except InvalidTag:
    print("changed message rejected")

try:
    aes.decrypt(nonce, sealed, b"order 9999")
except InvalidTag:
    print("changed header rejected")
