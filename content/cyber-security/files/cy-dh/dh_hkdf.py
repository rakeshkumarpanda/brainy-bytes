# 2.3 Diffie-Hellman, ElGamal and the discrete logarithm
# Example "dh_hkdf" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Ephemeral Diffie-Hellman, then HKDF and AES-GCM, the pattern TLS 1.3 uses (pip install cryptography)
import os
import secrets
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

P_HEX = (
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74"
    "020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F1437"
    "4FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF05"
    "98DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB"
    "9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF695581718"
    "3995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF"
)
p, g = int(P_HEX, 16), 2                 # RFC 3526 group 14
q = (p - 1) // 2

alice = secrets.randbelow(q - 2) + 2     # ephemeral: new secrets for this session only
bob = secrets.randbelow(q - 2) + 2
A, B = pow(g, alice, p), pow(g, bob, p)  # the values sent over the network
shared_alice = pow(B, alice, p).to_bytes(256, "big")
shared_bob = pow(A, bob, p).to_bytes(256, "big")
print("shared secret:", len(shared_alice), "bytes, equal:", shared_alice == shared_bob)

def derive(shared):                      # never use the raw shared value as a key
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"demo chat v1").derive(shared)

key = derive(shared_alice)
nonce = os.urandom(12)
sealed = AESGCM(key).encrypt(nonce, b"hello Bob", None)
print("Bob reads:", AESGCM(derive(shared_bob)).decrypt(nonce, sealed, None))
del alice, bob                           # forget the secrets: old sessions stay safe later
print("ephemeral keys deleted, so a later break in cannot decrypt this session")
