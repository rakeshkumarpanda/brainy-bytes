# 2.2 RSA: keys, proofs, signatures and attacks
# Example "rsa_oaep" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Real RSA with padding: OAEP for encryption, PSS for signatures (pip install cryptography)
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
public_key = private_key.public_key()
print("key size:", public_key.key_size, "bits, e =", public_key.public_numbers().e)

oaep = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
c1 = public_key.encrypt(b"session key 1234", oaep)
c2 = public_key.encrypt(b"session key 1234", oaep)
print("ciphertext length:", len(c1), "bytes")
print("same message, different ciphertexts:", c1 != c2)
print("decrypted:", private_key.decrypt(c1, oaep))

pss = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
message = b"release v2.4.1, sha256 9f2c..."
signature = private_key.sign(message, pss, hashes.SHA256())
public_key.verify(signature, message, pss, hashes.SHA256())       # raises if wrong
print("PSS signature verified,", len(signature), "bytes")
try:
    public_key.verify(signature, message + b"!", pss, hashes.SHA256())
except InvalidSignature:
    print("changed message rejected")

# Largest message OAEP with SHA-256 can carry in one 3072 bit block
print("OAEP limit:", 3072 // 8 - 2 * 32 - 2, "bytes, so RSA wraps a symmetric key, not the file")
