# 2.3 Diffie-Hellman, ElGamal and the discrete logarithm
# Example "dh_toy" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Diffie-Hellman with small numbers, then with the real 2048 bit group from RFC 3526
import secrets

p, g = 23, 5                             # public, agreed in the open
a, b = 6, 15                             # Alice's and Bob's secrets
A = pow(g, a, p)                         # Alice sends this
B = pow(g, b, p)                         # Bob sends this
print("A =", A, " B =", B)
print("Alice gets", pow(B, a, p), " Bob gets", pow(A, b, p))

# RFC 3526 group 14: a 2048 bit safe prime p = 2q + 1, with g = 2
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
p = int(P_HEX, 16)
q = (p - 1) // 2
g = 2
print("p has", p.bit_length(), "bits. g generates the subgroup of prime order q:", pow(g, q, p) == 1)

a = secrets.randbelow(q - 2) + 2         # fresh secrets every session
b = secrets.randbelow(q - 2) + 2
A = pow(g, a, p)
B = pow(g, b, p)
key_alice = pow(B, a, p)
key_bob = pow(A, b, p)
print("same key:", key_alice == key_bob, "| key has", key_alice.bit_length(), "bits")
