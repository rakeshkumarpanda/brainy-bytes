# Cryptography 2.3: Diffie-Hellman, ElGamal and the discrete logarithm. Checked against Diffie and Hellman, New
# Directions in Cryptography (1976), ElGamal (IEEE Trans. Inf. Theory, 1985), Pohlig and Hellman (1978), Shoup (1997),
# Lim and Lee (CRYPTO 1997), RFC 3526 (the group 14 prime was checked against its pi formula and as a safe prime),
# RFC 7919, RFC 5869 (HKDF), RFC 8446 (TLS 1.3), and Adrian and others, Imperfect Forward Secrecy (Logjam, CCS 2015).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-dh')
K = Kit()

K.code('dh_toy', r'''
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
''')

K.code('dlog_bsgs', r'''
# The discrete log: brute force against baby step giant step
from math import isqrt

def brute_force(g, h, p):
    value, x = 1, 0
    while value != h:
        value = value * g % p
        x = x + 1
    return x

def baby_giant(g, h, p, n):              # n = order of g
    m = isqrt(n) + 1
    table = {}
    value = 1
    for j in range(m):                   # baby steps: g^j
        table[value] = j
        value = value * g % p
    step = pow(g, -m, p)                 # g^(-m)
    y = h
    for i in range(m):                   # giant steps: h * g^(-m i)
        if y in table:
            return i * m + table[y]
        y = y * step % p
    return None

p, g = 101, 2
print("2^x = 48 mod 101: brute force", brute_force(g, 48, p), " BSGS", baby_giant(g, 48, p, 100))

# A 41 bit safe prime p = 2q + 1. g = 4 has prime order q.
p = 1099511628443
q = (p - 1) // 2
g = 4
secret = 123456789012
h = pow(g, secret, p)
x = baby_giant(g, h, p, q)
print("41 bit group: found x =", x, "correct:", x == secret)
print("about", 2 * (isqrt(q) + 1), "steps instead of up to", q)
print("for a 2048 bit group the same method needs about 2^1024 steps")
''', long=True)

K.code('pohlig_hellman', r'''
# Pohlig-Hellman: a discrete log is easy when p - 1 has only small prime factors
import random

p = 8608456956238879741                  # a 63 bit prime, and p - 1 is "smooth"
factors = [4, 3, 5, 49, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]   # prime powers whose product is p - 1
n = p - 1
check = 1
for f in factors:
    check = check * f
print("p - 1 is the product of the list:", check == n)

def is_generator(g):
    for r in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
        if pow(g, n // r, p) == 1:
            return False
    return True

g = 2
while not is_generator(g):
    g = g + 1
rng = random.Random(1)
secret = rng.randrange(2, n)
h = pow(g, secret, p)

# Solve x mod f in the small subgroup of size f, for each prime power f
remainders = []
for f in factors:
    g_small = pow(g, n // f, p)          # has order f
    h_small = pow(h, n // f, p)          # equals g_small ^ (x mod f)
    x_small = 0
    while pow(g_small, x_small, p) != h_small:
        x_small = x_small + 1            # at most f tries, f is tiny
    remainders.append(x_small)

# Join the small answers with the Chinese remainder theorem
x = 0
for r, f in zip(remainders, factors):
    Mi = n // f
    x = x + r * Mi * pow(Mi, -1, f)
x = x % n
print("generator g =", g, "| recovered the 63 bit secret:", x == secret)
print("work: about", sum(factors), "small steps. A safe prime of this size would need about 2^31.")
''', long=True)

K.code('dh_validate', r'''
# Always check the other side's public value. Bad values force a guessable key.
p = 1099511628443                        # toy safe prime p = 2q + 1
q = (p - 1) // 2
g = 4
b = 314159265358                         # Bob's secret

def bob_key(A):
    return pow(A, b, p)

def valid(A):
    # 1 < A < p - 1, and A must lie in the subgroup of order q
    return 1 < A < p - 1 and pow(A, q, p) == 1

for A in (1, p - 1, 0, pow(g, 271828, p)):
    print("A =", A, "| Bob's key would be", bob_key(A), "| valid:", valid(A))
''')

K.code('dh_mitm', r'''
# Man in the middle on plain Diffie-Hellman, and a fingerprint check that exposes it
import hashlib
import secrets

p = 1099511628443                        # a toy safe prime (41 bits). Real systems use 2048 bits or more.
q = (p - 1) // 2
g = 4

def new_secret():
    return secrets.randbelow(q - 2) + 2

def fingerprint(key):                    # a short code people can compare by phone or in person
    return hashlib.sha256(str(key).encode()).hexdigest()[:8]

a, b, m = new_secret(), new_secret(), new_secret()
A, B, M = pow(g, a, p), pow(g, b, p), pow(g, m, p)

# Mallory replaces A and B with her own M
alice_key = pow(M, a, p)                 # Alice thinks this is shared with Bob
bob_key = pow(M, b, p)                   # Bob thinks this is shared with Alice
mallory_with_alice = pow(A, m, p)
mallory_with_bob = pow(B, m, p)

print("Mallory knows Alice's key:", mallory_with_alice == alice_key)
print("Mallory knows Bob's key:  ", mallory_with_bob == bob_key)
print("Alice and Bob share a key:", alice_key == bob_key)
print("fingerprints:", fingerprint(alice_key), "vs", fingerprint(bob_key), "-> attack exposed")

# Without Mallory the fingerprints match
honest_alice, honest_bob = pow(B, a, p), pow(A, b, p)
print("honest run fingerprints match:", fingerprint(honest_alice) == fingerprint(honest_bob))
''')

K.code('elgamal', r'''
# ElGamal encryption: Diffie-Hellman with a fresh random k for every message
import secrets

# Toy example from the worked problem
p, g = 23, 5
x = 6                                    # private key
h = pow(g, x, p)                         # public key h = g^x = 8
m, k = 10, 3                             # message and one time random k
c1 = pow(g, k, p)                        # 5^3 mod 23 = 10
c2 = m * pow(h, k, p) % p                # 10 * 8^3 mod 23 = 14
s = pow(c1, x, p)                        # shared value h^k = c1^x
print("ciphertext (c1, c2) =", (c1, c2), " decrypts to", c2 * pow(s, -1, p) % p)

# Larger toy group: safe prime p = 2q + 1, messages encoded as squares mod p
p = 1099511628443
q = (p - 1) // 2
g = 4
x = secrets.randbelow(q - 2) + 2
h = pow(g, x, p)

def encrypt(m):
    k = secrets.randbelow(q - 2) + 2     # NEW k for every message
    return pow(g, k, p), m * pow(h, k, p) % p

def decrypt(c1, c2):
    return c2 * pow(pow(c1, x, p), -1, p) % p

m = pow(4242, 2, p)                      # a square, so it lies in the subgroup
e1, e2 = encrypt(m), encrypt(m)
print("same message, different ciphertexts:", e1 != e2, "| both decrypt:", decrypt(*e1) == m == decrypt(*e2))

# Multiplying ciphertexts multiplies the messages (homomorphic, and also malleable)
m2 = pow(1000, 2, p)
f1, f2 = encrypt(m), encrypt(m2)
product = (f1[0] * f2[0] % p, f1[1] * f2[1] % p)
print("Dec(E(m) * E(m2)) = m * m2:", decrypt(*product) == m * m2 % p)

# Reusing k is fatal: one known message reveals every other one
k = secrets.randbelow(q - 2) + 2
known, secret_msg = pow(11, 2, p), pow(777, 2, p)
c_known = (pow(g, k, p), known * pow(h, k, p) % p)
c_secret = (pow(g, k, p), secret_msg * pow(h, k, p) % p)
mask = c_known[1] * pow(known, -1, p) % p          # h^k, worked out from the known pair
print("k reused, secret recovered:", c_secret[1] * pow(mask, -1, p) % p == secret_msg)
''')

K.code('dh_hkdf', r'''
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
''')

K.lesson('idea', 'The key exchange problem and Diffie-Hellman', f'''
{talk('Until the 1970s, every secret message required a key delivered in advance, by courier, in a sealed bag, or in a meeting. Militaries and banks spent fortunes moving keys around. In 1974 Ralph Merkle, then an undergraduate at Berkeley, proposed a way to agree on a key in public using puzzles, and his professor rejected the idea. Two years later, at Stanford, Whitfield Diffie and Martin Hellman published New Directions in Cryptography. It showed how two people who have never met can agree on a secret key while an eavesdropper hears every word. Hellman later asked that the method be called Diffie-Hellman-Merkle, to credit Merkle’s part. At GCHQ, Malcolm Williamson had found the same method in secret around 1974. Diffie and Hellman received the Turing Award in 2015. Their exchange is still inside almost every secure connection today, in TLS, SSH, IPsec VPNs and the Signal messaging protocol, usually in its elliptic curve form, which comes in the next chapter.')}
{src('Diffie and Hellman, New Directions in Cryptography (1976), ElGamal (1985), Pohlig and Hellman (1978), RFC 3526, RFC 7919, RFC 5869 (HKDF), RFC 8446 (TLS 1.3), Adrian and others, Imperfect Forward Secrecy: How Diffie-Hellman Fails in Practice (Logjam, 2015).')}
{wwh('<b>Diffie-Hellman key exchange</b> lets two parties agree on a shared secret over a public channel. Each picks a secret exponent and sends g raised to it modulo a prime. Each raises what they receive to their own secret, and both get g<sup>ab</sup>.',
     'It solves key distribution: no courier and no earlier meeting. With fresh exponents for every session it also gives <b>forward secrecy</b>, so a key stolen later cannot unlock recorded traffic.',
     'Security rests on the <b>discrete logarithm problem</b>: from g<sup>a</sup> mod p it seems infeasible to find a when p is large and well chosen.')}
{table(['Name', 'Year', 'What it gives'], [
    ['Merkle puzzles', '1974 (published 1978)', 'First public key agreement, but only a quadratic gap between users and attacker'],
    ['Diffie-Hellman', '1976', 'Key agreement from discrete logs'],
    ['ElGamal encryption', '1985', 'Public key encryption from Diffie-Hellman'],
    ['DSA', '1991 (FIPS 186, 1994)', 'Signatures from discrete logs, based on ElGamal and Schnorr'],
    ['ECDH, X25519', '1985 idea, 2006 curve', 'The same exchange on elliptic curves, with much smaller keys']])}
''', kw=['Diffie-Hellman', 'key exchange', 'key distribution', 'Merkle puzzles', 'Williamson', 'GCHQ', 'New Directions in Cryptography', 'Turing Award', 'discrete logarithm'])

K.lesson('groups', 'Groups, generators and safe primes', f'''
{talk('To understand why Diffie-Hellman is built the way it is, we need a little group theory. Take a prime p and look at the numbers from 1 to p minus 1 under multiplication modulo p. Multiplying two of them gives another one, every number has an inverse, and 1 does nothing. That makes them a group, written Z p star, with p minus 1 elements. The order of an element g is the smallest k with g to the k equal to 1. If the order is p minus 1, then g is a generator, and its powers visit every element. Joseph-Louis Lagrange proved in the 1770s a fact that matters a lot here: the order of any element divides the size of the group. So if p minus 1 has small factors, there are small subgroups, and as you will see in the Pohlig-Hellman lesson, small subgroups leak secrets. That is why careful designs use a safe prime, p equal to 2q plus 1 with q also prime. Then the only subgroups have sizes 1, 2, q and 2q, and we work in the subgroup of size q, which is huge. The standard 2048 bit group 14 from RFC 3526 is built this way, with g equal to 2.')}
{wwh('A <b>cyclic group</b> is generated by one element g: every element is g<sup>k</sup>. The <b>order</b> of g is the smallest k &gt; 0 with g<sup>k</sup> = 1. A <b>safe prime</b> is p = 2q + 1 with q prime.',
     'The discrete log is only as hard as the subgroup it lives in. Small subgroups make it easy, so the group must have a large prime order subgroup.',
     'Pick a safe prime p. Squares mod p form the subgroup of prime order q. Use a generator g of that subgroup, for example g = 4, or g = 2 when 2 is a square, as in RFC 3526.')}
{fxs(fx('Order of an element', 'ord(g) = smallest k &gt; 0 with g<sup>k</sup> &equiv; 1 (mod p)', 'Mod 23: ord(5) = 22, so 5 is a generator. ord(2) = 11, because 2<sup>11</sup> = 2048 = 89 &times; 23 + 1.', key=True),
     fx('Lagrange’s theorem', 'ord(g) divides the group size, here p &minus; 1', 'Mod 23 the possible orders are 1, 2, 11 and 22.', key=True),
     fx('Generator test', 'g generates Z<sub>p</sub><sup>*</sup> &hArr; g<sup>(p&minus;1)/r</sup> &ne; 1 for every prime r dividing p &minus; 1', 'p = 23, p &minus; 1 = 2 &times; 11: 5<sup>11</sup> &equiv; 22 and 5<sup>2</sup> &equiv; 2, so 5 is a generator.'),
     fx('Safe prime', 'p = 2q + 1, with p and q prime', '23 = 2 &times; 11 + 1. 4 = 2<sup>2</sup> has order 11.'))}
{note('Exam favourite: "Is g a generator modulo p?" Factor p &minus; 1, then test g<sup>(p&minus;1)/r</sup> for each prime factor r. Do not list all the powers.', 'exam')}
''', kw=['group', 'cyclic group', 'generator', 'order', 'Lagrange theorem', 'safe prime', 'subgroup', 'RFC 3526', 'primitive root'])

K.lesson('exchange', 'The exchange step by step', f'''
{talk('Here is the exchange itself. Alice and Bob first agree, in public, on a prime p and a generator g. Alice picks a secret number a and sends Bob A equal to g to the a, modulo p. Bob picks a secret b and sends Alice B equal to g to the b. Now Alice raises B to her secret a, and Bob raises A to his secret b. Both get g to the a times b. The eavesdropper, called Eve in cryptography papers, sees p, g, A and B, but not a or b. Getting the key from what she sees is called the computational Diffie-Hellman problem, and the only known way to solve it is to compute a discrete logarithm. The animation uses the classic example with p equal to 23 and g equal to 5. Then the program repeats the exchange with the real 2048 bit prime from RFC 3526, the one used by many VPN and SSH servers. One important detail: the shared number is not used as a key directly. It goes through a key derivation function, which turns it into an AES key, as the forward secrecy lesson shows.')}
{viz('cydh')}
{run('dh_toy')}
{steps('Worked example with p = 23, g = 5, a = 6, b = 15', [
    'Alice: A = 5<sup>6</sup> mod 23 = 15625 mod 23 = 8.',
    'Bob: B = 5<sup>15</sup> mod 23 = 19.',
    'They swap A = 8 and B = 19 in public.',
    'Alice: 19<sup>6</sup> mod 23 = 2. Bob: 8<sup>15</sup> mod 23 = 2.',
    'Shared key 2 = 5<sup>90</sup> mod 23 = 5<sup>90 mod 22</sup> = 5<sup>2</sup> mod 23. Eve would have to find 6 from 8 or 15 from 19.'])}
{fxs(fx('Public values', 'A = g<sup>a</sup> mod p, B = g<sup>b</sup> mod p', 'a and b are secret, random, and new for every session.', key=True),
     fx('Shared secret', 'K = B<sup>a</sup> = A<sup>b</sup> = g<sup>ab</sup> mod p', 'p = 23, g = 5, a = 6, b = 15: K = 2.', key=True),
     fx('Computational Diffie-Hellman (CDH)', 'given g, g<sup>a</sup>, g<sup>b</sup>, find g<sup>ab</sup>', 'Believed hard in good groups. Solving discrete log solves CDH.'),
     fx('Decisional Diffie-Hellman (DDH)', 'tell g<sup>ab</sup> apart from a random g<sup>c</sup>', 'Fails in the full group Z<sub>p</sub><sup>*</sup>, holds in the prime order subgroup of a safe prime.'))}
''', kw=['Diffie-Hellman exchange', 'shared secret', 'CDH', 'DDH', 'Eve', 'RFC 3526 group 14', 'worked example'])

K.lesson('dlp', 'The discrete logarithm problem and how it is attacked', f'''
{talk('The discrete logarithm problem asks: given g, p and h, find x with g to the x equal to h modulo p. With real numbers, logarithms are easy, because powers grow smoothly. Modulo p, the powers jump around with no visible pattern, so there is no shortcut from size. Brute force tries x equal to 1, 2, 3 and so on, up to p steps. In 1971 Daniel Shanks found baby step giant step, which needs only about the square root of p steps, at the cost of storing a table of the same size. John Pollard’s rho method from 1978 gets the same square root time with almost no memory, and it is the best known attack on elliptic curves. For groups modulo a prime there is something much better, index calculus and the number field sieve, which are sub exponential, just like factoring. That is why finite field Diffie-Hellman needs keys as long as RSA, 2048 or 3072 bits. In 2015 the Logjam team showed that one huge precomputation for a single prime lets an attacker then solve each new log in that group quickly. For 512 bit export grade groups, the precomputation took about a week and each log about a minute. They estimated that a nation state could do the same for one widely shared 1024 bit prime.')}
{wwh('The <b>discrete logarithm</b> of h to base g modulo p is the x with g<sup>x</sup> &equiv; h (mod p). The <b>DLP</b> is finding it.',
     'Diffie-Hellman, ElGamal, DSA and Schnorr signatures are only as strong as the DLP in their group. Key sizes follow from the best attacks.',
     'Baby step giant step: write x = i m + j with m &asymp; &radic;n. Store g<sup>j</sup>, then step h &middot; g<sup>&minus;mi</sup> until it hits the table. Pollard rho: a random walk that finds a collision in about &radic;n steps with tiny memory.')}
{viz('cybsgs')}
{run('dlog_bsgs')}
{table(['Method', 'Time', 'Memory', 'Works in'], [
    ['Brute force', 'n', 'Tiny', 'Any group'],
    ['Baby step giant step (Shanks, 1971)', 'about 2&radic;n', '&radic;n', 'Any group'],
    ['Pollard rho (1978)', 'about &radic;(&pi;n/2)', 'Tiny', 'Any group, best known for elliptic curves'],
    ['Pohlig-Hellman (1978)', '&radic;(largest prime factor of n)', 'Small', 'Groups whose order has small factors'],
    ['Index calculus, number field sieve', 'sub exponential, like factoring', 'Large', 'Z<sub>p</sub><sup>*</sup>, not elliptic curves'],
    ['Shor’s algorithm (1994)', 'polynomial', 'Quantum computer', 'Every group above']])}
{fx('Generic lower bound (Shoup, 1997)', 'any generic algorithm needs about &radic;q group operations for a group of prime order q', 'So a 256 bit prime order q gives about 128 bit security, the basis of elliptic curve key sizes.', key=True)}
{note('Logjam (2015): about 8 percent of the top million HTTPS sites still accepted 512 bit export Diffie-Hellman, and many servers shared the same few 1024 bit primes. Use groups of at least 2048 bits, such as the RFC 7919 ffdhe groups, or elliptic curves.', 'warn')}
''', kw=['discrete logarithm problem', 'DLP', 'baby step giant step', 'Shanks', 'Pollard rho', 'index calculus', 'number field sieve', 'Logjam', 'Shoup generic bound', 'export grade'])

K.lesson('pohlig', 'Small subgroups: Pohlig-Hellman and bad public values', f'''
{talk('In 1978 Stephen Pohlig and Martin Hellman showed that the size of the prime is not the whole story. What matters is the largest prime factor of the group order. If p minus 1 splits into small primes, an attacker solves the discrete log separately inside each small subgroup, where it takes only a few steps, and then joins the pieces with the Chinese remainder theorem. The program in this lesson breaks a 63 bit discrete log in a few hundred steps because p minus 1 is a product of tiny primes. A related danger comes from the values the other side sends. If Bob blindly accepts A equal to 1, his key is 1. If he accepts p minus 1, his key is 1 or p minus 1. And if he reuses his secret with a group that has small subgroups, an attacker can send elements of small order and learn his secret a few bits at a time, an attack described by Chae Hoon Lim and Pil Joong Lee in 1997. In 2016 OpenSSL fixed a high severity bug of exactly this kind. The defences are simple: use a safe prime group, check every received value, and use fresh secrets each time.')}
{wwh('<b>Pohlig-Hellman</b> solves a discrete log in a group of order n = &prod; r<sub>i</sub><sup>e<sub>i</sub></sup> by solving it in each subgroup of order r<sub>i</sub><sup>e<sub>i</sub></sup> and joining the results with CRT.',
     'It shows that the group order must have a large prime factor, ideally be prime, and it powers small subgroup attacks on careless implementations.',
     'For each prime power f dividing n: g<sub>f</sub> = g<sup>n/f</sup>, h<sub>f</sub> = h<sup>n/f</sup>, find x mod f with g<sub>f</sub><sup>x</sup> = h<sub>f</sub>. Then CRT gives x mod n.')}
{run('pohlig_hellman')}
{run('dh_validate')}
{fxs(fx('Pohlig-Hellman cost', 'about &Sigma; e<sub>i</sub>(log n + &radic;r<sub>i</sub>) operations', 'Depends on the largest prime factor r of the order, not on the size of p.', key=True),
     fx('Public value check', '1 &lt; A &lt; p &minus; 1 and A<sup>q</sup> &equiv; 1 (mod p)', 'For a safe prime p = 2q + 1 this confirms A is in the subgroup of order q.', key=True))}
{attack([
    ['Uses a group whose order has only small prime factors', 'Use a safe prime or a standard group (RFC 3526, RFC 7919)'],
    ['Sends A = 0, 1 or p &minus; 1 to force a known key', 'Reject values outside 1 &lt; A &lt; p &minus; 1 and outside the subgroup'],
    ['Sends elements of small order to learn a reused secret bit by bit (Lim and Lee, 1997)', 'Fresh secrets every session, and the A<sup>q</sup> = 1 check'],
    ['Measures timing that depends on leading zero bytes of the secret (Raccoon, 2020)', 'Constant time code, and ephemeral secrets']])}
''', kw=['Pohlig-Hellman', 'smooth order', 'small subgroup attack', 'Lim Lee', 'public key validation', 'safe prime', 'Raccoon attack', 'CVE-2016-0701'])

K.lesson('mitm', 'Man in the middle and authenticated key exchange', f'''
{talk('Diffie-Hellman protects against someone who only listens. It does nothing against someone who can change messages. Mallory, sitting on the network, catches Alice’s value and sends Bob her own instead, and does the same in the other direction. Alice ends up sharing a key with Mallory, and so does Bob. Mallory decrypts every message, reads or changes it, and encrypts it again for the other side. Nobody sees an error. The cure is authentication: each side must prove who sent the public values. In TLS, the server signs the whole handshake with the private key of its certificate, and the browser checks the certificate chain up to a trusted authority. In the Station to Station protocol from 1992, by Diffie, Paul van Oorschot and Michael Wiener, both sides sign. Messaging apps such as Signal and WhatsApp let users compare a safety number, which is a fingerprint of their keys, in person or by a call. If Mallory is in the middle, the numbers differ.')}
{viz('cymitm')}
{run('dh_mitm')}
{wwh('A <b>man in the middle</b> (MITM) relays and changes messages between two parties. Against unauthenticated Diffie-Hellman she sets up two separate keys and reads everything.',
     'Without authentication, key exchange only stops passive eavesdroppers. Active attackers on Wi-Fi, ISPs or compromised routers can intercept.',
     'Bind the exchange to identities: signatures with certificates (TLS, SSH host keys), a pre shared key, or a human fingerprint check (safety numbers).')}
{table(['Protocol', 'How the exchange is authenticated'], [
    ['TLS 1.3', 'Server signs the handshake transcript with its certificate key (CertificateVerify)'],
    ['SSH', 'Server host key signs the exchange, the client checks it against known_hosts'],
    ['IPsec IKEv2', 'Signatures or a pre shared key'],
    ['Signal', 'Long term identity keys in X3DH, plus safety numbers users can compare'],
    ['Station to Station (1992)', 'Both sides sign both public values']])}
{note('The very first SSH connection to a new server shows a fingerprint and asks you to accept it. That is the only moment a man in the middle can slip in, so check the fingerprint with the server owner.', 'tip')}
''', kw=['man in the middle', 'MITM', 'authenticated key exchange', 'Station to Station', 'certificate', 'safety number', 'fingerprint', 'SSH known_hosts', 'TLS CertificateVerify'])

K.lesson('elgamal', 'ElGamal encryption', f'''
{talk('In 1985 Taher Elgamal, who later led the team that created SSL at Netscape, turned Diffie-Hellman into public key encryption. The receiver’s long term key is h equal to g to the x. To send a message, the sender makes a one time Diffie-Hellman exchange with that key: pick a random k, send c1 equal to g to the k, and multiply the message by h to the k, which only the receiver can recompute as c1 to the x. Because k is random, the same message gives a different ciphertext each time, unlike textbook RSA. ElGamal is also homomorphic for multiplication: multiplying two ciphertexts gives an encryption of the product of the messages. That property is useful in electronic voting and mix networks, and dangerous anywhere an attacker could change ciphertexts. The randomness must never repeat. If k is used twice, one known message reveals the other. ElGamal’s signature scheme, also from 1985, led to DSA, whose own nonce rule, broken by Sony in the PlayStation 3, is covered in the elliptic curve chapter.')}
{wwh('<b>ElGamal encryption</b>: public key h = g<sup>x</sup>. Encrypt m with random k as (c<sub>1</sub>, c<sub>2</sub>) = (g<sup>k</sup>, m &middot; h<sup>k</sup>). Decrypt m = c<sub>2</sub> &middot; (c<sub>1</sub><sup>x</sup>)<sup>&minus;1</sup>.',
     'It gives randomized public key encryption from the discrete log, and its multiplicative homomorphism is used in voting systems and threshold cryptography.',
     'c<sub>1</sub><sup>x</sup> = g<sup>kx</sup> = h<sup>k</sup>, so dividing c<sub>2</sub> by it leaves m. In the prime order subgroup it is IND-CPA secure under DDH, but it is malleable, so it is not CCA secure without extra steps.')}
{run('elgamal')}
{steps('Worked example with p = 23, g = 5, x = 6, m = 10, k = 3', [
    'Public key h = 5<sup>6</sup> mod 23 = 8.',
    'c<sub>1</sub> = 5<sup>3</sup> mod 23 = 125 mod 23 = 10.',
    'c<sub>2</sub> = 10 &times; 8<sup>3</sup> mod 23 = 10 &times; 6 mod 23 = 14.',
    'Decrypt: s = c<sub>1</sub><sup>x</sup> = 10<sup>6</sup> mod 23 = 6. Its inverse is 4, because 6 &times; 4 = 24 &equiv; 1.',
    'm = 14 &times; 4 mod 23 = 56 mod 23 = 10. The message is back.'])}
{fxs(fx('ElGamal', '(c<sub>1</sub>, c<sub>2</sub>) = (g<sup>k</sup>, m h<sup>k</sup>), m = c<sub>2</sub> (c<sub>1</sub><sup>x</sup>)<sup>&minus;1</sup>', 'Ciphertext is twice the size of the message.', key=True),
     fx('Homomorphism', 'E(m<sub>1</sub>) &middot; E(m<sub>2</sub>) = (g<sup>k<sub>1</sub>+k<sub>2</sub></sup>, m<sub>1</sub>m<sub>2</sub> h<sup>k<sub>1</sub>+k<sub>2</sub></sup>) = E(m<sub>1</sub>m<sub>2</sub>)', 'Exponential ElGamal (encrypt g<sup>m</sup>) makes it additive, used for vote tallies.'),
     fx('Reused k', 'c<sub>2</sub> / m = h<sup>k</sup>, then m&prime; = c<sub>2</sub>&prime; / h<sup>k</sup>', 'One known plaintext reveals every message sent with the same k.', key=True))}
''', kw=['ElGamal', 'Taher Elgamal', 'randomized encryption', 'homomorphic', 'malleable', 'nonce reuse', 'IND-CPA', 'DDH', 'electronic voting'])

K.lesson('forward', 'Forward secrecy, key derivation and TLS 1.3', f'''
{talk('Suppose an agency records all your encrypted traffic for years, and one day steals your server’s private key. With RSA key transport, where the client encrypts the session key to the server’s RSA key, every recorded session can now be decrypted. With ephemeral Diffie-Hellman, each session used fresh secrets that were deleted afterwards, so the stolen long term key, which was only used to sign, unlocks nothing from the past. This property is called forward secrecy. After the Snowden revelations in 2013, major sites switched to ephemeral key exchange, and TLS 1.3, published in 2018, made it mandatory by removing RSA key transport altogether. Two more details matter. First, the raw shared value is not uniformly random, so it is passed through a key derivation function. HKDF, designed by Hugo Krawczyk in 2010, extracts the randomness and expands it into as many keys as needed, separate ones for each direction. Second, Signal goes further with its double ratchet, which mixes in a new Diffie-Hellman exchange as messages flow, so even a stolen phone state heals itself after a few messages.')}
{wwh('<b>Forward secrecy</b>: compromise of long term keys does not reveal past session keys. It comes from <b>ephemeral</b> Diffie-Hellman, where session secrets are generated fresh and deleted.',
     'Encrypted traffic is often recorded and kept. Forward secrecy limits the damage of a later break in or legal seizure of keys.',
     'Each handshake: new secrets a and b, exchange, sign the transcript with the long term key, derive keys with HKDF, then erase a and b. HKDF-Extract(salt, shared) gives a pseudorandom key, HKDF-Expand(key, info, length) gives the working keys.')}
{local('dh_hkdf', 'It needs the cryptography package for HKDF and AES-GCM: python3 -m pip install cryptography.')}
{fxs(fx('HKDF (RFC 5869)', 'PRK = HMAC(salt, IKM), OKM = T(1) &#8214; T(2) &#8214; ..., T(i) = HMAC(PRK, T(i&minus;1) &#8214; info &#8214; i)', 'IKM is the shared Diffie-Hellman value. info labels the purpose, so each key is different.', key=True),
     fx('TLS 1.3 key schedule', 'early secret &rarr; handshake secret (from (EC)DHE) &rarr; master secret, all with HKDF', 'Every traffic key depends on the ephemeral exchange.'))}
{note('Recent releases of the Python cryptography package mark finite field Diffie-Hellman as deprecated and point users to X25519. New designs should use elliptic curve Diffie-Hellman, and hybrids with ML-KEM for quantum safety.', 'tip')}
''', kw=['forward secrecy', 'ephemeral Diffie-Hellman', 'DHE', 'HKDF', 'key derivation', 'TLS 1.3', 'Snowden', 'double ratchet', 'Signal'])

K.lesson('versus', 'Diffie-Hellman compared', f'''
{talk('Key exchange can be done in several ways, and each has a place. Finite field Diffie-Hellman, the version in this chapter, is well understood and has standard groups, but needs large keys because of the number field sieve. Elliptic curve Diffie-Hellman, especially X25519, does the same job with 32 byte keys and is now the default almost everywhere. RSA key transport is simpler but has no forward secrecy and is gone from TLS 1.3. Pre shared keys avoid public key maths entirely but need the keys delivered in advance, the very problem Diffie and Hellman solved. And ML-KEM, the new post quantum standard, is a key encapsulation mechanism rather than an exchange, but it plays the same role, and is already deployed in hybrid mode with X25519 in major browsers.')}
{versus('Ways to agree on a session key', ['', 'Finite field DHE', 'X25519 (ECDHE)', 'RSA key transport', 'Pre shared key', 'ML-KEM-768'], [
    ['Hard problem', 'Discrete log mod p', 'Elliptic curve discrete log', 'Factoring', 'None (shared secret)', 'Module lattices'],
    ['Key size, 128 bit security', '3072 bit p', '32 bytes', '3072 bit n', '16 or 32 bytes', '1184 byte public key'],
    ['Forward secrecy', 'Yes', 'Yes', 'No', 'Only with an added DH', 'Yes, with fresh keys'],
    ['Needs authentication added', 'Yes', 'Yes', 'Built into the certificate', 'Built in', 'Yes'],
    ['Quantum safe', 'No', 'No', 'No', 'Yes, if the key is long', 'Believed yes'],
    ['In TLS 1.3', 'Allowed (ffdhe groups)', 'Default', 'Removed', 'Allowed', 'Hybrid with X25519']],
    'Use X25519, or a hybrid of X25519 and ML-KEM-768, for new systems. Use finite field DH only with 2048 bit or larger standard groups. Never use RSA key transport.')}
''', kw=['comparison', 'DHE vs ECDHE', 'X25519', 'RSA key transport', 'pre shared key', 'ML-KEM', 'hybrid key exchange', 'ffdhe'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Diffie-Hellman connects school arithmetic to some of the deepest questions in cryptography. A beginner learns that two people can agree on a secret in public, and that this is what the padlock in a browser relies on. A college student can run the exchange by hand, test generators, explain the discrete log problem, use baby step giant step and spot a man in the middle. A masters student studies the CDH and DDH assumptions and the reductions between them, the generic group model and Shoup’s square root lower bound, Pohlig-Hellman and index calculus, and authenticated key exchange models such as Canetti and Krawczyk’s. At the research level, people prove the security of real protocols such as TLS 1.3 and Signal with formal tools like Tamarin and ProVerif, study the number field sieve for discrete logs, and design key exchange that survives quantum computers, from lattices and from isogenies. One isogeny scheme, SIKE, was a strong post quantum candidate until Wouter Castryck and Thomas Decru broke it in 2022 with a single laptop in about an hour.')}
{ladder(
    '<p>Two people can agree on a secret key in public. Each keeps one secret number and sends one public number. The padlock in your browser uses this, and it only stops attackers if the other side is also proved genuine.</p>',
    '<p>Run the exchange by hand, test a generator with g<sup>(p&minus;1)/r</sup>, explain CDH and the DLP, solve small logs with baby step giant step, break a smooth group with Pohlig-Hellman, and show how a man in the middle and a fingerprint check work.</p>',
    '<p>CDH, DDH and their relations, why DDH fails in Z<sub>p</sub><sup>*</sup>, the generic group model and the &radic;q bound, index calculus, ElGamal IND-CPA from DDH, authenticated key exchange (SIGMA, the Canetti and Krawczyk model), HKDF and the TLS 1.3 key schedule.</p>',
    '<p>Formal verification of TLS 1.3 and Signal (Tamarin, ProVerif), discrete log records with the number field sieve (795 bits in 2019), precomputation attacks (Logjam), isogeny based key exchange and the 2022 break of SIKE, and post quantum KEMs as replacements.</p>')}
{grow('Explain how two people agree on a key in public and why authentication is still needed.',
      'Compute exchanges, test generators, run BSGS and Pohlig-Hellman, and design a safe handshake.',
      'Reason about CDH and DDH, generic bounds, authenticated key exchange proofs and quantum safe replacements.')}
''', kw=['beginner', 'expert', 'generic group model', 'SIGMA', 'Canetti Krawczyk', 'Tamarin', 'ProVerif', 'SIKE', 'isogeny', 'Castryck Decru'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Diffie-Hellman</b> (1976): public p, g. A = g<sup>a</sup>, B = g<sup>b</sup>, key K = B<sup>a</sup> = A<sup>b</sup> = g<sup>ab</sup>. With p = 23, g = 5, a = 6, b = 15: A = 8, B = 19, K = 2.',
    '<b>Groups</b>: ord(g) divides p &minus; 1 (Lagrange). Test a generator with g<sup>(p&minus;1)/r</sup> &ne; 1. Use a <b>safe prime</b> p = 2q + 1 and the subgroup of order q.',
    '<b>DLP</b>: find x from g<sup>x</sup>. Generic attacks (BSGS, Pollard rho) take about &radic;q. Index calculus and the NFS are sub exponential mod p, so use 2048 to 3072 bit groups.',
    '<b>Pohlig-Hellman</b>: the largest prime factor of the order sets the cost. Validate received values: 1 &lt; A &lt; p &minus; 1 and A<sup>q</sup> = 1.',
    '<b>Man in the middle</b>: plain DH has no authentication. Sign the handshake (TLS, SSH) or compare fingerprints (safety numbers).',
    '<b>ElGamal</b>: (g<sup>k</sup>, m h<sup>k</sup>). Randomized and multiplicatively homomorphic. Never reuse k.',
    '<b>Forward secrecy</b> from ephemeral keys. Derive keys with <b>HKDF</b>. TLS 1.3 requires (EC)DHE and removed RSA key transport.',
    '<b>Logjam</b> (2015): 512 bit export groups broken, shared 1024 bit primes at risk. Prefer X25519 or hybrids with ML-KEM.'],
    'Cryptography 2.4 moves the same ideas to elliptic curves: point addition, ECDH and X25519, ECDSA and Ed25519, and the nonce mistakes that leaked real keys.')}
{files('Three tasks: compute a Diffie-Hellman key, write baby step giant step, and decrypt ElGamal.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does Diffie-Hellman let two people do?', ['Sign documents', 'Agree on a shared secret key over a public channel', 'Hash passwords', 'Factor numbers'], 1, 'Key exchange.', 'Each sends one public value, and both compute the same key.')
K.quiz('e', 'In Diffie-Hellman, which values does Eve see?', ['a and b', 'p, g, A and B', 'Only the key', 'Nothing'], 1, 'Everything sent.', 'The secrets a and b never leave Alice and Bob.')
K.quiz('e', 'With p = 23, g = 5 and Alice’s secret a = 6, what does Alice send?', ['6', '8', '19', '2'], 1, '5<sup>6</sup> mod 23.', '15625 mod 23 = 8.')
K.quiz('e', 'What hard problem protects Diffie-Hellman?', ['Factoring', 'Discrete logarithm', 'Sorting', 'Collision finding'], 1, 'Find x from g<sup>x</sup>.', 'Recovering a from g<sup>a</sup> mod p is the discrete log problem.')
K.quiz('m', 'What is a safe prime?', ['Any prime above 2048 bits', 'p = 2q + 1 with q also prime', 'A prime that ends in 7', 'A Mersenne prime'], 1, 'Large prime order subgroup.', 'Then the only subgroups have sizes 1, 2, q and 2q.')
K.quiz('m', 'Plain Diffie-Hellman with no signatures is open to', ['Brute force', 'A man in the middle', 'Birthday attacks', 'Nothing'], 1, 'Active attacker.', 'Mallory swaps both public values and shares one key with each side.')
K.quiz('m', 'Baby step giant step solves a discrete log in a group of size n in about', ['n steps', '&radic;n steps', 'log n steps', 'n<sup>2</sup> steps'], 1, 'Square root.', 'It stores about &radic;n baby steps and takes up to &radic;n giant steps.')
K.quiz('m', 'Why does TLS 1.3 use only ephemeral (EC)DHE key exchange?', ['It is faster', 'It gives forward secrecy', 'It avoids certificates', 'It needs no randomness'], 1, 'Stolen keys later.', 'Fresh secrets deleted after each session cannot be recovered from a later stolen long term key.')
K.quiz('m', 'Why is the raw shared value passed through HKDF?', ['To make it longer only', 'It is not uniformly random, and separate keys are needed for each purpose', 'To encrypt it', 'For compression'], 1, 'Extract then expand.', 'HKDF extracts a uniform key and expands it into labelled working keys.')
K.quiz('h', 'p &minus; 1 = 2<sup>2</sup> &middot; 3 &middot; 5 &middot; 7 &middot; ... with only small primes. What breaks the discrete log quickly?', ['Pollard rho', 'Pohlig-Hellman', 'Wiener', 'Fermat factoring'], 1, 'Small subgroups.', 'It solves the log in each small subgroup and joins the answers with CRT.')
K.quiz('h', 'Bob receives A = p &minus; 1 and computes A<sup>b</sup>. His key is', ['Random', '1 or p &minus; 1', 'Always 0', 'g'], 1, '(&minus;1)<sup>b</sup>.', 'p &minus; 1 &equiv; &minus;1, so the key is 1 for even b and p &minus; 1 for odd b. Validate received values.')
K.quiz('h', 'ElGamal reuses the same k for two messages, and the attacker knows the first message. Then', ['Nothing leaks', 'The second message is revealed', 'Only the length leaks', 'The private key x is revealed directly'], 1, 'h<sup>k</sup> is the same.', 'c<sub>2</sub> / m gives h<sup>k</sup>, which then unlocks the second c<sub>2</sub>.')
K.quiz('h', 'Logjam (2015) showed that', ['AES is broken', 'One precomputation for a common 512 bit prime let attackers solve each later log in about a minute', 'SHA-256 collides', 'RSA-2048 was factored'], 1, 'Precomputation.', 'The number field sieve’s heavy part depends only on p, so shared primes are a single point of failure.')
K.quiz('x', 'In the style of a Stanford CS 255 exam: why does DDH fail in the full group Z<sub>p</sub><sup>*</sup> with a generator g?', ['It does not fail', 'The Legendre symbol reveals whether exponents are even, so g<sup>ab</sup> can be told apart from random', 'Because p is prime', 'Because g is small'], 1, 'Quadratic residues.', 'g<sup>ab</sup> is a square exactly when a or b is even, which can be checked from g<sup>a</sup> and g<sup>b</sup>. Working in the prime order subgroup fixes this.')
K.quiz('x', 'In the style of an MIT 6.857 question: a server reuses one static DH secret in a group whose order has small factors and does not validate inputs. The attacker can', ['Do nothing', 'Send small order elements and learn the secret modulo each small factor (Lim and Lee)', 'Only cause a crash', 'Read the certificate'], 1, 'Small subgroup confinement.', 'Each response reveals the secret mod a small r, and CRT joins the pieces.')

K.calc('e', 'p = 23, g = 5, a = 6. Compute A = g<sup>a</sup> mod p.', '8', 'Square and multiply or direct.', ['5<sup>2</sup> = 25 &equiv; 2.', '5<sup>6</sup> = (5<sup>2</sup>)<sup>3</sup> &equiv; 2<sup>3</sup> = 8.', eq('A = 8')], check=pow(5, 6, 23))
K.calc('e', 'p = 23, g = 5, b = 15. Compute B = g<sup>b</sup> mod p.', '19', '5<sup>15</sup> = 5<sup>12</sup> &middot; 5<sup>3</sup>.', ['5<sup>6</sup> &equiv; 8, so 5<sup>12</sup> &equiv; 64 &equiv; 18.', '5<sup>3</sup> = 125 &equiv; 10. 18 &times; 10 = 180 &equiv; 19.', eq('B = 19')], check=pow(5, 15, 23))
K.calc('e', 'Alice has a = 6 and receives B = 19, with p = 23. What is the shared key?', '2', 'B<sup>a</sup> mod p.', ['19 &equiv; &minus;4, so 19<sup>6</sup> &equiv; 4<sup>6</sup> = 4096.', '4096 = 178 &times; 23 + 2.', eq('K = 2')], check=pow(19, 6, 23))
K.calc('m', 'What is the order of 2 modulo 23?', '11', 'Orders divide 22.', ['2<sup>2</sup> = 4 &ne; 1.', '2<sup>11</sup> = 2048 = 89 &times; 23 + 1.', eq('ord(2) = 11')], check=next(k for k in range(1, 23) if pow(2, k, 23) == 1))
K.calc('m', 'For baby step giant step with p = 101 (group size 100), what is m = &lceil;&radic;100&rceil;?', '10', 'Square root.', ['&radic;100 = 10.', 'So 10 baby steps and at most 10 giant steps.', eq('m = 10')], check=10)
K.calc('m', 'ElGamal with p = 23, g = 5, k = 3: what is c<sub>1</sub>?', '10', 'g<sup>k</sup> mod p.', ['5<sup>3</sup> = 125.', '125 = 5 &times; 23 + 10.', eq('c<sub>1</sub> = 10')], check=pow(5, 3, 23))
K.calc('m', 'ElGamal with p = 23, public key h = 8, k = 3, m = 10: what is c<sub>2</sub>?', '14', 'm &middot; h<sup>k</sup> mod p.', ['8<sup>3</sup> = 512 = 22 &times; 23 + 6.', '10 &times; 6 = 60 = 2 &times; 23 + 14.', eq('c<sub>2</sub> = 14')], check=10 * pow(8, 3, 23) % 23)
K.calc('m', 'Decrypt ElGamal (c<sub>1</sub>, c<sub>2</sub>) = (10, 14) with p = 23 and x = 6.', '10', 's = c<sub>1</sub><sup>x</sup>, then multiply c<sub>2</sub> by s<sup>&minus;1</sup>.', ['10<sup>6</sup> mod 23 = 6, and 6<sup>&minus;1</sup> = 4.', '14 &times; 4 = 56 = 2 &times; 23 + 10.', eq('m = 10')], check=14 * pow(pow(10, 6, 23), -1, 23) % 23)
K.calc('h', 'For the safe prime p = 23 = 2q + 1, what is the order q of the subgroup generated by 4?', '11', '4 = 2<sup>2</sup> is a square.', ['q = (23 &minus; 1) / 2 = 11.', '4<sup>11</sup> = 2<sup>22</sup> &equiv; 1 by Fermat.', eq('ord(4) = 11')], check=next(k for k in range(1, 23) if pow(4, k, 23) == 1))
K.calc('h', 'An attacker sends Bob A = 22 = p &minus; 1 with p = 23. Bob’s secret is b = 15. What key does Bob compute?', '22', '22 &equiv; &minus;1.', ['(&minus;1)<sup>15</sup> = &minus;1.', '&minus;1 mod 23 = 22.', eq('K = 22')], check=pow(22, 15, 23))
K.calc('h', 'p = 101, p &minus; 1 = 2<sup>2</sup> &middot; 5<sup>2</sup>. Pohlig-Hellman with brute force inside the subgroups of size 4 and 25 needs at most how many tries in total?', '29', 'Add the subgroup sizes.', ['Subgroup of size 4: up to 4 tries.', 'Subgroup of size 25: up to 25 tries.', eq('4 + 25 = 29, instead of up to 100')], check=4 + 25)
K.calc('h', 'How many baby steps does BSGS store for a group of order 2<sup>64</sup>?', '4294967296', '&radic;(2<sup>64</sup>).', ['&radic;(2<sup>64</sup>) = 2<sup>32</sup>.', '2<sup>32</sup> = 4,294,967,296.', eq('about 4.3 billion table entries')], check=2 ** 32)
K.calc('x', 'In the style of an IIT Madras exam: g = 5 generates Z<sub>23</sub><sup>*</sup>, and Eve sees h = 5<sup>x</sup> mod 23 = 2. Compute h<sup>11</sup> mod 23 (Euler’s criterion). A result of 1 means x is even.', '1', '2<sup>11</sup> mod 23.', ['2<sup>11</sup> = 2048 = 89 &times; 23 + 1.', 'So 2 is a square mod 23, and x is even (indeed x = 2).', eq('2<sup>11</sup> &equiv; 1 (mod 23)')], check=pow(2, 11, 23))

K.assign('dh_key', 'e', 'A Diffie-Hellman key',
         '<p>Write <code>dh_key(p, other_public, my_secret)</code> that returns the shared key. Reject bad public values: return None unless 1 &lt; other_public &lt; p &minus; 1.</p>',
         '''
def dh_key(p, other_public, my_secret):
    # your code here
    pass
''', [('dh_key(23, 19, 6)', 2), ('dh_key(23, 8, 15)', 2), ('dh_key(23, 1, 6)', None), ('dh_key(23, 22, 15)', None), ('dh_key(1000003, 777, 271828)', pow(777, 271828, 1000003))],
         '''
def dh_key(p, other_public, my_secret):
    if not 1 < other_public < p - 1:
        return None
    return pow(other_public, my_secret, p)
''', 'Check the range first, then return pow(other_public, my_secret, p).', '<p>Real code also checks that the value lies in the right subgroup, A<sup>q</sup> mod p = 1 for a safe prime p = 2q + 1.</p>')
K.assign('bsgs', 'm', 'Baby step, giant step',
         '<p>Write <code>bsgs(g, h, p)</code> that returns the smallest x &ge; 0 with g<sup>x</sup> mod p = h, using baby step giant step with m = isqrt(p &minus; 1) + 1. Return None if there is no answer.</p>',
         '''
from math import isqrt

def bsgs(g, h, p):
    # your code here
    pass
''', [('bsgs(2, 48, 101)', 73), ('bsgs(5, 100, 383)', 270), ('bsgs(2, 1, 101)', 0), ('bsgs(4, pow(4, 123456, 1000003), 1000003)', 123456)],
         '''
from math import isqrt

def bsgs(g, h, p):
    m = isqrt(p - 1) + 1
    table = {}
    value = 1
    for j in range(m):
        if value not in table:
            table[value] = j
        value = value * g % p
    step = pow(g, -m, p)
    y = h % p
    for i in range(m):
        if y in table:
            return i * m + table[y]
        y = y * step % p
    return None
''', 'Store g^j for j below m in a dictionary, keeping the first j. Then multiply h by g^(-m) each round and look it up.', '<p>Keeping only the first j for each value makes the answer the smallest x, which matters when g is not a generator and values repeat.</p>')
K.assign('elgamal_decrypt', 'm', 'Decrypt ElGamal',
         '<p>Write <code>elgamal_decrypt(p, x, c1, c2)</code> that returns m = c<sub>2</sub> &middot; (c<sub>1</sub><sup>x</sup>)<sup>&minus;1</sup> mod p.</p>',
         '''
def elgamal_decrypt(p, x, c1, c2):
    # your code here
    pass
''', [('elgamal_decrypt(23, 6, 10, 14)', 10), ('elgamal_decrypt(467, 127, pow(2, 213, 467), 100 * pow(pow(2, 127, 467), 213, 467) % 467)', 100), ('elgamal_decrypt(23, 6, 1, 5)', 5)],
         '''
def elgamal_decrypt(p, x, c1, c2):
    s = pow(c1, x, p)
    return c2 * pow(s, -1, p) % p
''', 'Compute s = pow(c1, x, p), then multiply c2 by pow(s, -1, p) and reduce mod p.', '<p>The second test is a small example with p = 467, g = 2, private key x = 127 and random k = 213, built the same way as the worked problem.</p>')

K.must('Exchange', 'A = g<sup>a</sup>, B = g<sup>b</sup>, K = B<sup>a</sup> = A<sup>b</sup> = g<sup>ab</sup>. p = 23, g = 5, a = 6, b = 15: 8, 19, key 2.')
K.must('Groups', 'ord(g) | p &minus; 1. Generator: g<sup>(p&minus;1)/r</sup> &ne; 1 for each prime r | p &minus; 1. Safe prime p = 2q + 1.')
K.must('DLP attacks', 'BSGS 2&radic;n with &radic;n memory, Pollard rho &radic;n, Pohlig-Hellman uses small factors, NFS sub exponential mod p.')
K.must('Validate and authenticate', 'Check 1 &lt; A &lt; p &minus; 1 and A<sup>q</sup> = 1. Sign the handshake or compare fingerprints against MITM.')
K.must('ElGamal', '(g<sup>k</sup>, m h<sup>k</sup>), m = c<sub>2</sub>/c<sub>1</sub><sup>x</sup>. Randomized, multiplicatively homomorphic, never reuse k.')
K.must('Forward secrecy', 'Ephemeral DH, delete secrets, HKDF for keys. TLS 1.3 removed RSA key transport. Logjam: avoid 512 and shared 1024 bit groups.')

T = K.topic(
    slug='cy-dh', topic='cy-dh', step=(2, 'Public key cryptography and its maths', 'cy-c2', 'The number theory behind public keys, then RSA, Diffie-Hellman and elliptic curves, each with its proofs and its attacks.', 'Advanced'),
    title='Diffie-Hellman, ElGamal and the discrete logarithm', short='Diffie-Hellman', badge='2.3', minutes=85,
    lead='Key exchange in public: the history, cyclic groups, generators and safe primes, the exchange step by step, CDH and DDH, the discrete log problem and its attacks (baby step giant step, Pollard rho, Pohlig-Hellman, index calculus, Logjam), public value checks, the man in the middle and authenticated exchange, ElGamal encryption, and forward secrecy with HKDF as in TLS 1.3.',
    desc='Diffie-Hellman, key exchange, Merkle puzzles, cyclic group, generator, order, Lagrange theorem, safe prime, RFC 3526, CDH, DDH, discrete logarithm problem, baby step giant step, Shanks, Pollard rho, Pohlig-Hellman, index calculus, number field sieve, Logjam, small subgroup attack, public key validation, Raccoon, man in the middle, Station to Station, safety number, ElGamal, homomorphic encryption, nonce reuse, forward secrecy, ephemeral, HKDF, TLS 1.3, X25519, ML-KEM',
    summary='groups and safe primes, the exchange, CDH and DDH, DLP attacks, Pohlig-Hellman and validation, MITM, ElGamal, forward secrecy and HKDF.',
    keywords=['Diffie-Hellman', 'discrete log', 'safe prime', 'baby step giant step', 'Pohlig-Hellman', 'man in the middle', 'ElGamal', 'forward secrecy', 'HKDF', 'Logjam'],
    recap='<p>Two public numbers make one private key. The group must be large and prime order, the values must be checked, the exchange must be signed, and the secrets must be thrown away after use.</p>',
    added='2026-11-14')
