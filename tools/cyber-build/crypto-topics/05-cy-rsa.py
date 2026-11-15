# Cryptography 2.2: RSA. Checked against Rivest, Shamir and Adleman (CACM, 1978), RFC 8017 (PKCS #1 v2.2), FIPS 186-5
# (2023), Boneh, Twenty Years of Attacks on the RSA Cryptosystem (Notices of the AMS, 1999), Wiener (IEEE Trans. Inf.
# Theory, 1990), Bleichenbacher (CRYPTO 1998), Böck, Somorovsky and Young, ROBOT (2017), Nemec and others, ROCA (CCS 2017),
# NIST SP 800-57 Part 1 Rev. 5 and the NIST IR 8547 initial public draft (November 2024).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-rsa')
K = Kit()

K.code('rsa_toy', r'''
# Textbook RSA with small numbers, then a real size key made the same way
import secrets
from math import gcd

p, q = 61, 53
n = p * q                                # public modulus
phi = (p - 1) * (q - 1)                  # Euler's phi, kept secret
e = 17                                   # public exponent
print("n =", n, " phi =", phi, " gcd(e, phi) =", gcd(e, phi))
d = pow(e, -1, phi)                      # private exponent
print("public key (n, e) =", (n, e), " private d =", d)

m = 65                                   # the message as a number below n
c = pow(m, e, n)                         # encrypt with the public key
print("encrypt 65 ->", c)
print("decrypt", c, "->", pow(c, d, n))

# The same steps at real size: two random 1024 bit primes
def is_prime(n, rounds=40):
    if n < 4:
        return n in (2, 3)
    for small in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % small == 0:
            return n == small
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for i in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for j in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def random_prime(bits):
    while True:
        candidate = secrets.randbits(bits) | (3 << (bits - 2)) | 1   # top two bits set, odd
        if candidate % 65537 != 1 and is_prime(candidate):
            return candidate

e = 65537
p = random_prime(1024)
q = random_prime(1024)
n = p * q
d = pow(e, -1, (p - 1) * (q - 1))
print("n has", n.bit_length(), "bits, d has", d.bit_length(), "bits")
m = int.from_bytes(b"meet at the library at 6", "big")
c = pow(m, e, n)
back = pow(c, d, n)
print("round trip ok:", back == m, "->", back.to_bytes(24, "big"))
''', long=True)

K.code('rsa_proof_check', r'''
# Check RSA correctness for EVERY message, including ones that share a factor with n
from math import gcd, lcm

p, q, e = 5, 11, 3
n = p * q
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
print("n =", n, " phi =", phi, " e =", e, " d =", d)

works = 0
shared = []
for m in range(n):
    if pow(pow(m, e, n), d, n) == m:
        works = works + 1
    if gcd(m, n) != 1:
        shared.append(m)
print("messages that come back:", works, "of", n)
print("messages sharing a factor with n:", shared)
print("they still come back, for example 15 ->", pow(15, e, n), "->", pow(pow(15, e, n), d, n))

# The smaller exponent from the Carmichael function works as well
lam = lcm(p - 1, q - 1)
d_small = pow(e, -1, lam)
ok = all(pow(pow(m, e, n), d_small, n) == m for m in range(n))
print("lambda(n) =", lam, " d mod lambda =", d_small, " works for all:", ok)

# Why gcd(e, phi) must be 1: with e = 5 two messages share a ciphertext
e_bad = 5
seen = {}
for m in range(n):
    c = pow(m, e_bad, n)
    if c in seen:
        print("e = 5 is useless here:", seen[c], "and", m, "both encrypt to", c)
        break
    seen[c] = m
''')

K.code('rsa_sign', r'''
# RSA signatures with the toy key: hash, then sign with d, verify with e
import hashlib

n, e, d = 3233, 17, 2753                 # p = 61, q = 53

def h(message):
    # a TOY hash: the first two bytes of SHA-256, reduced below n. Real RSA uses the full hash with PSS padding.
    return int.from_bytes(hashlib.sha256(message).digest()[:2], "big") % n

def sign(message):
    return pow(h(message), d, n)

def verify(message, signature):
    return pow(signature, e, n) == h(message)

msg = b"Pay Riya 100 rupees"
s = sign(msg)
print("H(msg) =", h(msg), " signature =", s)
print("valid:", verify(msg, s))
print("changed message valid:", verify(b"Pay Riya 900 rupees", s))

# Without a hash, textbook RSA signatures can be forged
s_fake = 1000                            # pick ANY signature first
m_fake = pow(s_fake, e, n)               # then compute the message it signs
print("forged pair: message", m_fake, "signature", s_fake, "checks:", pow(s_fake, e, n) == m_fake)

# And signatures multiply: sig(a) * sig(b) is a signature on a * b
a, b = 12, 20
sa, sb = pow(a, d, n), pow(b, d, n)
print("sig(12) * sig(20) mod n signs 240:", pow(sa * sb % n, e, n) == a * b % n)
''')

K.code('rsa_crt', r'''
# RSA-CRT decryption, and the Bellcore fault attack that breaks it
from math import gcd

p, q = 61, 53
n, e, d = p * q, 17, 2753
dp = d % (p - 1)                         # 53
dq = d % (q - 1)                         # 49
q_inv = pow(q, -1, p)                    # 38
print("dp =", dp, " dq =", dq, " q_inv =", q_inv)

def crt_power(c, fault=False):
    mp = pow(c, dp, p)                   # half size work mod p
    mq = pow(c, dq, q)                   # half size work mod q
    if fault:
        mq = (mq + 1) % q                # a glitch spoils the mod q half
    h = q_inv * (mp - mq) % p            # Garner's formula
    return mq + h * q

c = 2790
print("CRT decrypt:", crt_power(c), " direct:", pow(c, d, n))

# A signature is the same operation. A faulty one leaks a prime factor.
m = 1234
s_good = crt_power(m)
s_bad = crt_power(m, fault=True)
print("good signature verifies:", pow(s_good, e, n) == m)
print("faulty signature verifies:", pow(s_bad, e, n) == m)
leak = gcd(pow(s_bad, e, n) - m, n)
print("gcd(s'^e - m, n) =", leak, "->", leak, "x", n // leak, "= n")

# The defence: check before you release
def safe_sign(m):
    s = crt_power(m, fault=True)
    if pow(s, e, n) != m:
        return None                      # refuse to output a bad signature
    return s
print("safe_sign with a fault returns:", safe_sign(m))
''')

K.code('rsa_attacks', r'''
# Attacks on careless RSA, all on toy keys made right here
import random
from math import gcd, isqrt

rng = random.Random(2026)                # fixed seed so the demo is repeatable. NEVER use random for real keys.

def is_prime(n):
    if n < 4:
        return n in (2, 3)
    if n % 2 == 0:
        return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1) or a % n == 0:
            continue
        for j in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def prime_for_e3(bits):                  # p mod 3 = 2, so gcd(3, p - 1) = 1
    while True:
        p = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if p % 3 == 2 and is_prime(p):
            return p

def cube_root(x):                        # the whole number r with r^3 <= x < (r + 1)^3
    low, high = 0, 1 << (x.bit_length() // 3 + 1)
    while low < high:
        mid = (low + high + 1) // 2
        if mid ** 3 <= x:
            low = mid
        else:
            high = mid - 1
    return low

# 1. Malleability: anyone can turn an encryption of m into one of 2m
n, e, d = 3233, 17, 2753
c = pow(65, e, n)
c2 = c * pow(2, e, n) % n
print("1. c * 2^e decrypts to", pow(c2, d, n))

# 2. Small e with no padding: if m^3 < n, the ciphertext is just m^3
p, q = prime_for_e3(512), prime_for_e3(512)
n = p * q
m = int.from_bytes(b"PIN 4321", "big")
c = pow(m, 3, n)
print("2. m^3 < n:", m ** 3 < n, " cube root gives", cube_root(c).to_bytes(8, "big"))

# 3. Hastad: the same m sent with e = 3 to three people
keys = [prime_for_e3(256) * prime_for_e3(256) for i in range(3)]
m = int.from_bytes(b"the secret meeting is at noon", "big")
cs = [pow(m, 3, k) for k in keys]
N = keys[0] * keys[1] * keys[2]
x = 0
for ci, ki in zip(cs, keys):             # Chinese remainder theorem gives m^3 mod N = m^3
    Ni = N // ki
    x = x + ci * Ni * pow(Ni, -1, ki)
x = x % N
print("3. Hastad recovers:", cube_root(x).to_bytes(29, "big"))

# 4. Two keys that share a prime (bad randomness at boot)
shared = prime_for_e3(256)
n1 = shared * prime_for_e3(256)
n2 = shared * prime_for_e3(256)
g = gcd(n1, n2)
print("4. gcd(n1, n2) finds the shared prime:", g == shared)

# 5. Fermat factoring when p and q are too close
def fermat_factor(n):
    a = isqrt(n)
    if a * a < n:
        a = a + 1
    tries = 0
    while True:
        b2 = a * a - n
        b = isqrt(b2)
        tries = tries + 1
        if b * b == b2:
            return a - b, a + b, tries
        a = a + 1

print("5. 5959 =", fermat_factor(5959))
p = prime_for_e3(512)
q = p + 2
while not is_prime(q):
    q = q + 2
f1, f2, tries = fermat_factor(p * q)
print("   1024 bit n with close primes factored in", tries, "try:", {f1, f2} == {p, q})
''', long=True)

K.code('wiener', r'''
# Wiener's attack: a small private exponent d falls out of the continued fraction of e / n
import random
from math import gcd, isqrt

def continued_fraction(a, b):            # the terms of a / b
    terms = []
    while b != 0:
        terms.append(a // b)
        a, b = b, a % b
    return terms

def convergents(terms):                  # the fractions k / d that the terms build, one by one
    h0, h1 = 0, 1
    k0, k1 = 1, 0
    for t in terms:
        h0, h1 = h1, t * h1 + h0
        k0, k1 = k1, t * k1 + k0
        yield h1, k1

def wiener(n, e):
    for k, d in convergents(continued_fraction(e, n)):
        if k == 0 or (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k           # a guess for phi(n)
        s = n - phi + 1                  # would be p + q
        disc = s * s - 4 * n             # (p - q)^2
        if disc >= 0 and isqrt(disc) ** 2 == disc:
            r = isqrt(disc)
            return d, (s + r) // 2, (s - r) // 2
    return None

print("small example:", wiener(90581, 17993))

# A 1024 bit key with a 200 bit private exponent: far too small
rng = random.Random(7)                   # toy demo only. Real keys use the secrets module.

def is_prime(n):
    if n % 2 == 0:
        return n == 2
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for j in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def prime(bits):
    while True:
        p = rng.getrandbits(bits) | (3 << (bits - 2)) | 1
        if is_prime(p):
            return p

p, q = prime(512), prime(512)
n, phi = p * q, (p - 1) * (q - 1)
while True:
    d = rng.getrandbits(200) | (1 << 199) | 1
    if gcd(d, phi) == 1:
        break
e = pow(d, -1, phi)                      # e is now huge and looks harmless
found = wiener(n, e)
print("n has", n.bit_length(), "bits, e has", e.bit_length(), "bits")
print("d recovered:", found[0] == d, " factors correct:", found[1] * found[2] == n)
print("terms in the continued fraction of e/n:", len(continued_fraction(e, n)))
''', long=True)

K.code('rsa_oaep', r'''
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
''')

K.lesson('idea', 'What RSA is and where it came from', f'''
{talk('In April 1977, three young researchers at MIT, Ron Rivest, Adi Shamir and Leonard Adleman, were trying to turn the idea of Diffie and Hellman into a working system. Diffie and Hellman had shown how two people could agree on a key in public, but they had no way to encrypt a message to someone with a key anyone could look up. Rivest and Shamir proposed schemes, and Adleman, a number theorist, broke them one after another for months. Then, after a Passover dinner, Rivest could not sleep and wrote down a scheme that Adleman could not break. It used two large primes, multiplied together. In August 1977 Martin Gardner described it in his Scientific American column and printed a challenge: a 129 digit number to factor, with a prize of one hundred dollars. The authors guessed it would take forty quadrillion years. A team of 600 volunteers factored it in 1994. Later it came out that Clifford Cocks at the British agency GCHQ had found the same scheme in 1973, within weeks of joining, but it was kept secret until 1997. The RSA patent expired in September 2000, and RSA became the most widely used public key system in the world.')}
{src('Rivest, Shamir and Adleman, A Method for Obtaining Digital Signatures and Public Key Cryptosystems (CACM, 1978), RFC 8017 (PKCS #1 v2.2), FIPS 186-5 (2023), Boneh, Twenty Years of Attacks on the RSA Cryptosystem (1999), NIST IR 8547 (draft, 2024).')}
{wwh('<b>RSA</b> is a public key system. The public key is a pair (n, e) where n = p q is the product of two secret primes. The private key is d with e d &equiv; 1 (mod &phi;(n)). Encrypt with c = m<sup>e</sup> mod n, decrypt with m = c<sup>d</sup> mod n.',
     'Anyone can encrypt to you or check your signature using only the public key. Only you can decrypt or sign. It made secure email, software signing, HTTPS certificates and smart cards possible.',
     'Making the key needs primes, an inverse and Euler’s theorem from Cryptography 2.1. Breaking it seems to need factoring n, which is believed to be infeasible for n of 2048 bits or more.')}
{table(['Part', 'Symbol', 'Public or secret', 'Toy example'], [
    ['Two primes', 'p, q', 'Secret, deleted or kept with d', '61 and 53'],
    ['Modulus', 'n = p q', 'Public', '3233'],
    ['Euler’s phi', '&phi;(n) = (p &minus; 1)(q &minus; 1)', 'Secret', '3120'],
    ['Public exponent', 'e, with gcd(e, &phi;(n)) = 1', 'Public', '17 (65537 in practice)'],
    ['Private exponent', 'd = e<sup>&minus;1</sup> mod &phi;(n)', 'Secret', '2753']])}
''', kw=['RSA', 'Rivest', 'Shamir', 'Adleman', 'Clifford Cocks', 'GCHQ', 'public key', 'private key', 'RSA-129', 'Martin Gardner', 'patent'])

K.lesson('keygen', 'Making a key, encrypting and decrypting', f'''
{talk('Here is the whole of RSA in five steps. First, pick two large random primes p and q of the same size, for example 1024 bits each. Second, multiply them to get n, the modulus. Third, compute phi of n, which is p minus 1 times q minus 1. Fourth, choose the public exponent e, which must share no factor with phi. Almost everyone uses 65537, a prime equal to 2 to the 16 plus 1, because its binary form has only two ones, so encryption needs just 17 multiplications. Fifth, compute d, the inverse of e modulo phi, with the extended Euclidean algorithm. Publish n and e. Keep d secret, and either keep p and q for fast decryption or delete them. To encrypt, turn the message into a number m smaller than n and compute m to the e modulo n. To decrypt, compute c to the d modulo n. Try the animation with the classic example from many textbooks, p equal to 61 and q equal to 53. Then try your own primes, and see what happens when e shares a factor with phi.')}
{viz('cyrsa')}
{run('rsa_toy')}
{steps('Worked example with p = 5, q = 11, e = 3', [
    'n = 5 &times; 11 = 55.',
    '&phi;(n) = 4 &times; 10 = 40. gcd(3, 40) = 1, so e = 3 is allowed.',
    'd = 3<sup>&minus;1</sup> mod 40 = 27, because 3 &times; 27 = 81 = 2 &times; 40 + 1.',
    'Encrypt m = 2: c = 2<sup>3</sup> mod 55 = 8.',
    'Decrypt: 8<sup>27</sup> mod 55 = 2. The message is back.'])}
{fxs(fx('Key generation', 'n = p q, &phi;(n) = (p &minus; 1)(q &minus; 1), gcd(e, &phi;(n)) = 1, d = e<sup>&minus;1</sup> mod &phi;(n)', 'p = 61, q = 53: n = 3233, &phi; = 3120, e = 17, d = 2753.', key=True),
     fx('Encryption', 'c = m<sup>e</sup> mod n, with 0 &le; m &lt; n', '65<sup>17</sup> mod 3233 = 2790.', key=True),
     fx('Decryption', 'm = c<sup>d</sup> mod n', '2790<sup>2753</sup> mod 3233 = 65.', key=True),
     fx('Using the Carmichael function', 'd = e<sup>&minus;1</sup> mod &lambda;(n), &lambda;(n) = lcm(p &minus; 1, q &minus; 1)', 'lcm(60, 52) = 780 and 17<sup>&minus;1</sup> mod 780 = 413, a smaller d that works just as well. FIPS 186-5 uses &lambda;.'))}
{note('FIPS 186-5 sets rules that block known attacks: e is odd with 2<sup>16</sup> &lt; e &lt; 2<sup>256</sup>, d &gt; 2<sup>nlen/2</sup> (stops Wiener’s attack), and |p &minus; q| &gt; 2<sup>nlen/2 &minus; 100</sup> (stops Fermat factoring). Primes must come from a strong random generator.', 'tip')}
''', kw=['RSA key generation', 'encrypt', 'decrypt', 'modulus', 'public exponent', '65537', 'private exponent', 'Carmichael lambda', 'FIPS 186-5'])

K.lesson('proof', 'Why decryption always works: the proof', f'''
{talk('A careful student will ask a fair question. Euler’s theorem only promises that m to the phi of n is 1 when m shares no factor with n. What if the message happens to be a multiple of p? Then Euler’s theorem says nothing, and yet RSA still works. The neat way to prove it uses the Chinese remainder theorem. Instead of working modulo n, we check the answer modulo p and modulo q separately. Modulo p, either p divides m, and then both sides are zero, or it does not, and then Fermat’s little theorem does the job. The same holds modulo q. Since the result is right modulo both primes, the Chinese remainder theorem says it is right modulo n. This proof is a favourite in university exams. The program checks it for every single message for the small key with n equal to 55, including the fifteen messages that share a factor with n. In practice, such a message would reveal a factor of n by a simple gcd, but with 1024 bit primes the chance of picking one at random is about one in two to the 1023, so it never happens by accident.')}
{fx('Correctness', '(m<sup>e</sup>)<sup>d</sup> &equiv; m (mod n) for every m from 0 to n &minus; 1', 'Holds whenever e d &equiv; 1 (mod &phi;(n)) or (mod &lambda;(n)), and n is a product of different primes.', key=True)}
{deep('The full proof, covering every message', '<p>Write e d = 1 + k(p &minus; 1)(q &minus; 1) for some whole number k &ge; 0. We show m<sup>ed</sup> &equiv; m (mod p).</p><p><b>Case 1:</b> p divides m. Then m &equiv; 0 (mod p) and m<sup>ed</sup> &equiv; 0 (mod p). Both sides agree.</p><p><b>Case 2:</b> p does not divide m. By Fermat, m<sup>p&minus;1</sup> &equiv; 1 (mod p). So m<sup>ed</sup> = m &middot; (m<sup>p&minus;1</sup>)<sup>k(q&minus;1)</sup> &equiv; m &middot; 1 = m (mod p).</p><p>The same argument with the roles swapped gives m<sup>ed</sup> &equiv; m (mod q). Now p and q are different primes, so both divide m<sup>ed</sup> &minus; m and so does their product. Therefore m<sup>ed</sup> &equiv; m (mod n). With &lambda;(n) in place of &phi;(n) the proof is the same, because &lambda;(n) is still a multiple of p &minus; 1 and of q &minus; 1.</p>')}
{run('rsa_proof_check')}
{note('Exam favourite: "Prove that RSA decryption is correct even when gcd(m, n) &ne; 1." Answers that only quote Euler’s theorem lose marks. Use Fermat modulo p and modulo q, then join with CRT as above.', 'exam')}
''', kw=['RSA correctness', 'proof', 'Euler theorem', 'Fermat little theorem', 'Chinese remainder theorem', 'gcd(m, n)', 'lambda'])

K.lesson('sign', 'RSA signatures', f'''
{talk('RSA can run backwards. If you raise a value to the private exponent d, anyone can raise the result to the public exponent e and get the value back. Only the owner of d could have made it, so it works as a signature. In practice we never sign the message itself. We first hash it with SHA-256, then pad the hash, then apply d. The hash keeps the signature short, whatever the length of the message, and blocks two simple forgeries. Without a hash, anyone can choose a random number s and compute s to the e. The pair is a valid message and signature, though the message is random gibberish. Signatures also multiply: the product of signatures on a and on b is a signature on a times b. These tricks are called existential forgery, and they show why textbook RSA is not a safe signature scheme on its own. The modern padding for signatures is PSS, proved secure by Mihir Bellare and Phillip Rogaway in 1996. RSA signatures still protect most software updates, code signing certificates and many HTTPS certificates today.')}
{wwh('An <b>RSA signature</b> on message M is s = pad(H(M))<sup>d</sup> mod n. Anyone checks it by computing s<sup>e</sup> mod n and comparing with pad(H(M)).',
     'It proves who signed and that the message was not changed, and the signer cannot later deny it. This is the basis of certificates, code signing and signed documents.',
     'Hash the message, pad the hash with PSS (or the older PKCS #1 v1.5 signature padding), raise to d. To verify, raise to e and check the padding and hash.')}
{viz('cyrsasign')}
{run('rsa_sign')}
{fxs(fx('Sign and verify', 's = H(M)<sup>d</sup> mod n, accept if s<sup>e</sup> mod n = H(M)', 'Signing uses the private key, verifying uses the public key, the opposite of encryption.', key=True),
     fx('Existential forgery of textbook RSA', 'pick s, set m = s<sup>e</sup> mod n', 'With the toy key, s = 1000 signs m = 175.'),
     fx('Multiplicative property', 's<sub>a</sub> &middot; s<sub>b</sub> mod n is a signature on a &middot; b mod n', 'Hashing breaks this, because H(a) &middot; H(b) is not H of anything useful.'))}
{note('Sign then encrypt with the same RSA key pair is a classic mistake. Use separate key pairs for signing and for encryption, as the standards require.', 'warn')}
''', kw=['RSA signature', 'hash then sign', 'PSS', 'existential forgery', 'multiplicative property', 'code signing', 'certificate'])

K.lesson('crt', 'Fast decryption with CRT, and the fault attack', f'''
{talk('Decryption with a 2048 bit exponent is the slow part of RSA. The owner of the key knows p and q, so they can use the Chinese remainder theorem from the last chapter. They compute the answer modulo p using a reduced exponent, d modulo p minus 1, and modulo q using d modulo q minus 1, and then join the two halves with a short formula found by Harvey Garner in 1959. Each half uses numbers and exponents of half the size, so each costs about one eighth as much, and the whole decryption runs about four times faster. Almost every library does this. There is a catch, found at Bellcore in 1996 by Dan Boneh, Richard DeMillo and Richard Lipton, with a sharper version by Arjen Lenstra. If a fault spoils just one half of a signature, for example from a voltage glitch, heat or a laser aimed at a smart card, the faulty signature is still right modulo p but wrong modulo q. Then a single gcd with n gives away p. One bad signature breaks the key. The defence is simple: check every signature with the public key before releasing it.')}
{fxs(fx('CRT exponents', 'd<sub>p</sub> = d mod (p &minus; 1), d<sub>q</sub> = d mod (q &minus; 1), q<sub>inv</sub> = q<sup>&minus;1</sup> mod p', 'Toy key: d<sub>p</sub> = 53, d<sub>q</sub> = 49, q<sub>inv</sub> = 38.', key=True),
     fx('Garner’s recombination', 'm<sub>p</sub> = c<sup>d<sub>p</sub></sup> mod p, m<sub>q</sub> = c<sup>d<sub>q</sub></sup> mod q, h = q<sub>inv</sub>(m<sub>p</sub> &minus; m<sub>q</sub>) mod p, m = m<sub>q</sub> + h q', 'The private key file in PKCS #1 stores p, q, d<sub>p</sub>, d<sub>q</sub> and q<sub>inv</sub> for exactly this.', key=True),
     fx('Bellcore attack', 'faulty s&prime; with s&prime; &equiv; s (mod p) but not mod q gives p = gcd(s&prime;<sup>e</sup> &minus; m, n)', 'With the toy key the gcd is 61.', key=True))}
{run('rsa_crt')}
{attack([
    ['Glitches the chip during one CRT half and collects one faulty signature', 'Verify each signature with e before releasing it'],
    ['Measures decryption time to learn bits of d or p (Kocher, 1996, Brumley and Boneh, 2003 over a network)', 'Constant time code and blinding: decrypt c &middot; r<sup>e</sup>, then divide by r'],
    ['Watches power use or electromagnetic leaks on a smart card', 'Masking, blinding and certified hardware']])}
''', kw=['RSA-CRT', 'Garner', 'dp dq qinv', 'Bellcore attack', 'fault attack', 'Boneh DeMillo Lipton', 'Lenstra', 'blinding', 'timing attack', 'side channel'])

K.lesson('attacks', 'Attacks on textbook RSA', f'''
{talk('Plain RSA, exactly as in the textbook, is called textbook RSA, and it is not safe to use as it stands. It is deterministic, so the same message always gives the same ciphertext, and an attacker can test guesses. If the message is yes or no, they encrypt both with your public key and compare. It is malleable: multiplying a ciphertext by 2 to the e makes a valid encryption of twice the message, without knowing it. With a small exponent such as 3 and a short message, m cubed may be smaller than n, so no reduction ever happens and an ordinary cube root reveals the message. In 1985 Johan Håstad showed that if the same message goes to three people who all use e equal to 3, the Chinese remainder theorem plus a cube root recovers it, even when m cubed is bigger than each n. Bad key generation is just as dangerous. If two keys share a prime, a gcd breaks both. If p and q are too close together, Fermat’s old method from 1643 factors n almost instantly. In 2022 Hanno Böck found printers from Canon and Fujifilm whose key library made exactly this mistake. All of these demos run on toy keys made inside the program.')}
{safe('Every attack here runs only on keys the program makes itself. Testing keys or servers you do not own is illegal in most countries. Tools such as testssl.sh check your own servers for weak RSA settings.')}
{run('rsa_attacks')}
{fxs(fx('Malleability', 'c &middot; t<sup>e</sup> &equiv; (m t)<sup>e</sup> (mod n)', '2790 &middot; 2<sup>17</sup> mod 3233 decrypts to 130.', key=True),
     fx('Small e, short m', 'if m<sup>e</sup> &lt; n then c = m<sup>e</sup> exactly, so m = c<sup>1/e</sup>', 'c = 1,000,000 with e = 3 gives m = 100.', key=True),
     fx('Håstad broadcast', 'CRT on c<sub>1</sub>, c<sub>2</sub>, c<sub>3</sub> gives m<sup>3</sup> mod n<sub>1</sub>n<sub>2</sub>n<sub>3</sub> = m<sup>3</sup>', 'Needs e copies of the same message under e different keys.'),
     fx('Fermat factoring', 'n = a<sup>2</sup> &minus; b<sup>2</sup> = (a &minus; b)(a + b), try a = &lceil;&radic;n&rceil;, &lceil;&radic;n&rceil; + 1, ...', '5959: a = 80 gives 6400 &minus; 5959 = 441 = 21<sup>2</sup>, so 5959 = 59 &times; 101.', key=True))}
{scene('ROCA and the Estonian ID cards', '<p>In 2017 researchers from Masaryk University in Czechia found that an RSA library in Infineon chips made primes with a special hidden structure, to save time. Their attack, called ROCA (CVE-2017-15361), could factor a 2048 bit key from these chips for at most about 40,000 US dollars of cloud computing time. About 750,000 Estonian national ID cards, many security keys and TPM chips were affected. Estonia suspended the certificates and issued updates. The lesson: primes must be random, and key generation code needs careful review, not just the RSA formulas.</p>')}
{attack([
    ['Guesses a short message and encrypts the guess', 'Random padding (OAEP) makes each ciphertext different'],
    ['Multiplies the ciphertext to change the message', 'OAEP rejects any change on decryption'],
    ['Uses e = 3 on a short message, or Håstad’s broadcast', 'OAEP padding, and e = 65537'],
    ['Finds keys that share a prime by a gcd across many keys', 'Good randomness when keys are made, especially at first boot'],
    ['Factors n because p and q are close, or have a hidden structure', 'Follow FIPS 186-5 key generation, and use tested libraries']])}
''', kw=['textbook RSA', 'deterministic', 'malleability', 'small exponent attack', 'cube root', 'Hastad broadcast', 'shared prime', 'gcd attack', 'Fermat factoring', 'ROCA', 'Infineon'])

K.lesson('wiener', 'Wiener’s attack on a small private exponent', f'''
{talk('Decryption speed depends on the size of d, so an engineer might be tempted to choose a small d first and compute e from it. In 1990 Michael Wiener showed that this is fatal. Because e times d is one more than k times phi, and phi is very close to n, the fraction e over n is extremely close to k over d. A tool from the 1700s, continued fractions, finds the best approximations to any fraction, and one of them is exactly k over d when d is smaller than about a quarter root of n, divided by 3. Each guess is easy to test: it gives a guess for phi, which gives a guess for p plus q, and then p and q are the roots of a quadratic. In 1999 Dan Boneh and Glenn Durfee used lattice methods to push the limit up to n to the power 0.292. Standards now insist that d is larger than the square root of n, which a normal key made from e equal to 65537 always is. The animation runs the attack on a small key step by step.')}
{wwh('<b>Wiener’s attack</b> recovers d from (n, e) alone when d &lt; n<sup>1/4</sup> / 3 and q &lt; p &lt; 2q.',
     'It shows that speeding up RSA by choosing a small d breaks the key completely, and it introduces lattice style thinking used in many later attacks.',
     'Expand e / n as a continued fraction. For each convergent k / d, compute &phi; = (e d &minus; 1) / k, then s = n &minus; &phi; + 1 = p + q, and check whether x<sup>2</sup> &minus; s x + n = 0 has whole number roots.')}
{viz('cywiener')}
{run('wiener')}
{fxs(fx('Why it works', '|e / n &minus; k / d| &lt; 1 / (2 d<sup>2</sup>) when d &lt; n<sup>1/4</sup> / 3', 'Legendre’s theorem: any fraction that close is a convergent of the continued fraction.', key=True),
     fx('Recover p and q', 's = n &minus; &phi; + 1, p, q = (s &plusmn; &radic;(s<sup>2</sup> &minus; 4n)) / 2', 'n = 90581, e = 17993: d = 5, &phi; = 89964, s = 618, p = 379, q = 239.', key=True),
     fx('Wiener bound for a 1024 bit n', 'log<sub>2</sub>(n<sup>1/4</sup> / 3) &asymp; 256 &minus; 1.58 &asymp; 254 bits', 'Boneh and Durfee: d &lt; n<sup>0.292</sup>, about 299 bits for a 1024 bit n.'))}
''', kw=['Wiener attack', 'small private exponent', 'continued fraction', 'convergent', 'Boneh Durfee', 'lattice', 'Legendre'])

K.lesson('padding', 'Padding: OAEP, PKCS #1 v1.5, Bleichenbacher and PSS', f'''
{talk('Every attack on textbook RSA in the earlier lesson is stopped by padding: before encrypting, the message is mixed with fresh random bytes in a structured way. The first standard, PKCS number 1 version 1.5 from 1993, simply put a fixed header, some random non zero bytes, a zero byte and then the message. In 1998 Daniel Bleichenbacher found that if a server tells you whether a ciphertext decrypts to correct padding, even through a different error message or a slightly different response time, you can decrypt any ciphertext with about a million carefully chosen queries. It became known as the million message attack. Servers added patches, but the attack kept coming back. In 2017 the ROBOT study found that servers at major sites, including Facebook and PayPal, were still vulnerable, nineteen years later. The better padding, OAEP, was designed by Bellare and Rogaway in 1994 and uses two rounds of hashing to scramble the message with randomness, so any change is detected on decryption. TLS 1.3, from 2018, removed RSA encryption of keys completely and uses RSA only for signatures, with PSS padding.')}
{wwh('<b>OAEP</b> (Optimal Asymmetric Encryption Padding) mixes the message with a random seed using a hash based mask, so RSA encryption becomes randomized and non malleable. <b>PSS</b> does the same job for signatures.',
     'Padding turns RSA from a broken textbook formula into a secure scheme with a security proof (IND-CCA2 for OAEP in the random oracle model).',
     'OAEP: DB = lHash &#8214; zeros &#8214; 0x01 &#8214; M. Pick a random seed. maskedDB = DB &oplus; MGF(seed), maskedSeed = seed &oplus; MGF(maskedDB). Encrypt 0x00 &#8214; maskedSeed &#8214; maskedDB with RSA.')}
{local('rsa_oaep', 'It needs the cryptography package: python3 -m pip install cryptography.')}
{fxs(fx('OAEP message limit', 'max length = k &minus; 2 h &minus; 2 bytes', 'k = key bytes, h = hash bytes. 2048 bit key with SHA-256: 256 &minus; 64 &minus; 2 = 190 bytes.', key=True),
     fx('PKCS #1 v1.5 encryption block', '0x00 &#8214; 0x02 &#8214; at least 8 random non zero bytes &#8214; 0x00 &#8214; M', 'A server that reveals "padding OK or not" is a padding oracle.'))}
{table(['Scheme', 'Use', 'Status'], [
    ['Textbook RSA', 'Teaching only', 'Never use: deterministic and malleable'],
    ['PKCS #1 v1.5 encryption', 'Old TLS key transport', 'Avoid: Bleichenbacher (1998), ROBOT (2017). Removed in TLS 1.3'],
    ['RSA-OAEP', 'Encrypting keys', 'Recommended for RSA encryption'],
    ['PKCS #1 v1.5 signatures', 'Many certificates', 'No practical break, still widely used'],
    ['RSA-PSS', 'Signatures, TLS 1.3', 'Recommended, has a tight security proof']])}
{note('RSA never encrypts a whole file. It wraps a random symmetric key (for example an AES-256 key), and the file is encrypted with AES-GCM. This is called hybrid encryption.', 'tip')}
''', kw=['OAEP', 'PKCS1 v1.5', 'Bleichenbacher', 'million message attack', 'ROBOT', 'padding oracle', 'PSS', 'TLS 1.3', 'hybrid encryption', 'IND-CCA2'])

K.lesson('sizes', 'Key sizes, speed and the quantum deadline', f'''
{talk('How long should an RSA key be? The answer comes from the best factoring method, the number field sieve, together with a safety margin. NIST says a 2048 bit key gives about 112 bits of security, and 3072 bits gives about 128 bits, the same as AES-128. Going higher costs a lot: doubling the key length makes private key operations roughly eight times slower, which is one reason elliptic curves, with 256 bit keys for 128 bit security, took over for new designs. The bigger threat is quantum computing. Shor’s algorithm would factor any RSA modulus in polynomial time on a large fault tolerant quantum computer. No such machine exists yet, but data recorded today could be decrypted later, which is called harvest now, decrypt later. So in November 2024 NIST proposed, in its draft report IR 8547, that RSA keys giving 112 bits of security be deprecated after 2030, and that all RSA, along with the other quantum vulnerable schemes, be disallowed after 2035. The replacement standards, ML-KEM and ML-DSA, are covered in the post quantum chapter of this section.')}
{table(['Modulus', 'Security (NIST SP 800-57)', 'Status'], [
    ['512 bits', 'Broken', 'Factored in 1999 (RSA-155). Now hours on rented servers'],
    ['1024 bits', 'About 80 bits', 'Disallowed. Believed within reach of a well funded attacker'],
    ['2048 bits', 'About 112 bits', 'Minimum today. Deprecated after 2030 in NIST IR 8547 draft'],
    ['3072 bits', 'About 128 bits', 'Recommended until 2035'],
    ['4096 bits', 'About 140 bits (estimate)', 'Common for long lived keys, slower'],
    ['Any size', 'Broken by a large quantum computer', 'Disallowed after 2035 in NIST IR 8547 draft']])}
{fxs(fx('Cost of RSA operations', 'private key: about k<sup>3</sup>, public key with e = 65537: about k<sup>2</sup>', 'k = bits of n. Doubling k makes signing about 8 times slower but verifying only about 4 times slower.', key=True),
     fx('Why verifying is fast', 'e = 65537 needs 17 multiplications, d needs about 1.5 k', 'So RSA is good when there are many verifiers, such as certificates and software updates.'))}
''', kw=['RSA key size', '2048', '3072', 'NIST SP 800-57', 'NIST IR 8547', 'Shor algorithm', 'harvest now decrypt later', 'post quantum', 'quantum computer'])

K.lesson('versus', 'RSA compared with other public key systems', f'''
{talk('RSA is not the only public key system, and for new designs it is often not the first choice. Diffie-Hellman key exchange, the subject of the next chapter, agrees a fresh key for each session, which gives forward secrecy: stealing the server’s long term key later does not unlock old sessions. RSA key transport, where the client encrypts a key to the server’s RSA key, does not have this property, which is one reason TLS 1.3 dropped it. Elliptic curve schemes give the same security with much smaller keys and faster signing. RSA still wins in one place: verifying a signature is very fast, so it remains popular for certificates and firmware. And all three, RSA, Diffie-Hellman and elliptic curves, fall to a large quantum computer, while the new lattice based standards do not, as far as anyone knows.')}
{versus('Choosing a public key system', ['', 'RSA', 'Finite field DH', 'Elliptic curves', 'ML-KEM and ML-DSA'], [
    ['Hard problem', 'Factoring', 'Discrete log mod p', 'Elliptic curve discrete log', 'Module lattices (MLWE)'],
    ['Public key for 128 bit security', '3072 bits (384 bytes)', '3072 bits', '256 bits (32 bytes for X25519)', '1184 bytes (ML-KEM-768)'],
    ['Does', 'Encryption and signatures', 'Key exchange', 'Key exchange (ECDH) and signatures (ECDSA, Ed25519)', 'Key exchange (ML-KEM), signatures (ML-DSA)'],
    ['Speed', 'Fast verify, slow sign', 'Medium', 'Fast', 'Very fast, larger messages'],
    ['Forward secrecy', 'No, as key transport', 'Yes, with fresh keys', 'Yes, with fresh keys', 'Yes, with fresh keys'],
    ['Quantum safe', 'No', 'No', 'No', 'Believed yes']],
    'Use RSA-PSS or RSA-OAEP when a system requires RSA. Prefer elliptic curves for new designs today, and plan the move to ML-KEM and ML-DSA, often as hybrids such as X25519 with ML-KEM-768.')}
''', kw=['RSA vs ECC', 'RSA vs Diffie-Hellman', 'forward secrecy', 'ML-KEM', 'ML-DSA', 'X25519', 'Ed25519', 'hybrid key exchange'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('RSA rewards study at every level. A beginner learns that RSA has a public key for locking and a private key for unlocking, and that its safety rests on how hard it is to split a big number into its two primes. A college student can make a toy key by hand, encrypt and decrypt, prove correctness with Fermat and the Chinese remainder theorem, explain signatures and the CRT speed up, and run the textbook attacks. A masters student studies security definitions such as IND-CCA2 and the proofs for OAEP and PSS in the random oracle model, the Bleichenbacher attack in detail, and side channels on real implementations. At the research level, people use Coppersmith’s method and lattice reduction to attack RSA with partial information, such as knowing a quarter of the bits of p, and study whether breaking RSA is really as hard as factoring. Dan Boneh and Ramarathnam Venkatesan showed in 1998 that for small e this might not be so. Others estimate the quantum resources needed to factor RSA-2048.')}
{ladder(
    '<p>RSA has a public key (n, e) that anyone can use to lock a message or check a signature, and a private key d that only the owner has. Breaking it seems to need factoring n into its two primes, which is very hard for big numbers.</p>',
    '<p>Make a key from p and q, compute &phi; and d with extended Euclid, encrypt and decrypt, prove correctness with Fermat plus CRT, sign with hash then d, speed up with CRT, and demonstrate malleability, small e, Håstad, shared primes, Fermat factoring and Wiener.</p>',
    '<p>IND-CPA and IND-CCA2, why textbook RSA fails both, OAEP and PSS proofs in the random oracle model, Bleichenbacher and Manger padding oracles, fault and timing attacks with blinding as the defence, and the RSA assumption compared with factoring.</p>',
    '<p>Coppersmith’s small root method and LLL: stereotyped messages, partial key exposure, Boneh and Durfee’s d &lt; n<sup>0.292</sup>, factoring with known high bits of p, the open question of whether breaking RSA is equivalent to factoring, and quantum resource estimates for RSA-2048.</p>')}
{grow('Explain public and private keys and why factoring protects RSA.',
      'Build, prove, sign, speed up and attack toy RSA keys with confidence.',
      'Analyse padding proofs, oracle and fault attacks, and lattice attacks such as Coppersmith and Boneh and Durfee.')}
''', kw=['beginner', 'expert', 'IND-CCA2', 'random oracle model', 'Coppersmith', 'LLL', 'partial key exposure', 'RSA assumption', 'Manger attack'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Keys</b>: n = p q, &phi;(n) = (p &minus; 1)(q &minus; 1), e with gcd(e, &phi;) = 1 (usually 65537), d = e<sup>&minus;1</sup> mod &phi;(n) or mod &lambda;(n).',
    '<b>Encrypt</b> c = m<sup>e</sup> mod n. <b>Decrypt</b> m = c<sup>d</sup> mod n. Toy example: 65 to 2790 and back with n = 3233, d = 2753.',
    '<b>Proof</b>: Fermat modulo p and modulo q, joined by CRT, covers every m, even those sharing a factor with n.',
    '<b>Signatures</b>: s = pad(H(M))<sup>d</sup>, verify s<sup>e</sup>. Hash and pad, or forgery is trivial. Use PSS.',
    '<b>RSA-CRT</b> is about 4 times faster. A single faulty half signature leaks p = gcd(s&prime;<sup>e</sup> &minus; m, n). Verify before release.',
    '<b>Textbook RSA</b> is deterministic and malleable. Small e cube roots, Håstad broadcast, shared primes, close primes (Fermat) and small d (Wiener) all break careless keys.',
    '<b>Padding</b>: OAEP for encryption, PSS for signatures. PKCS #1 v1.5 encryption falls to Bleichenbacher padding oracles (ROBOT, 2017).',
    '<b>Sizes</b>: 2048 bits gives about 112 bit security, 3072 about 128. NIST IR 8547 draft: deprecate 112 bit RSA after 2030, disallow all RSA after 2035 because of quantum computers.'],
    'Cryptography 2.3 turns to the other hard problem: Diffie-Hellman key exchange, ElGamal and the discrete logarithm, with forward secrecy and the attacks on small groups.')}
{files('Three tasks: compute a private exponent, decrypt with CRT, and the integer cube root behind the small e attack.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In RSA, which key encrypts a message to Asha?', ['Asha’s private key', 'Asha’s public key', 'The sender’s private key', 'A shared AES key'], 1, 'Anyone must be able to do it.', 'Anyone encrypts with Asha’s public key (n, e). Only Asha’s private d decrypts.')
K.quiz('e', 'RSA’s security rests on the difficulty of', ['Sorting', 'Factoring n = p q', 'Hashing', 'Finding gcd'], 1, 'Two primes.', 'Knowing p and q gives &phi;(n) and so d. Finding them from n is factoring.')
K.quiz('e', 'Which public exponent is used almost everywhere?', ['3', '17', '65537', '2048'], 2, '2<sup>16</sup> + 1.', '65537 is prime and has only two 1 bits, so encryption and verification are fast.')
K.quiz('e', 'With p = 5 and q = 11, what is n?', ['16', '55', '40', '50'], 1, 'Multiply.', 'n = 5 &times; 11 = 55.')
K.quiz('m', 'Why must gcd(e, &phi;(n)) = 1?', ['To make n prime', 'So that e has an inverse d modulo &phi;(n)', 'To make encryption faster', 'It is not needed'], 1, 'Inverses need coprime.', 'Without it d does not exist, and different messages collide, as e = 5 with n = 55 shows.')
K.quiz('m', 'A signature is made with', ['The public key e', 'The private key d', 'Both keys', 'No key'], 1, 'Only the owner can sign.', 's = H(M)<sup>d</sup> mod n. Anyone verifies with e.')
K.quiz('m', 'Why is textbook RSA encryption not safe?', ['It is too slow', 'It is deterministic and malleable', 'It uses small primes', 'It cannot decrypt'], 1, 'Same input, same output.', 'An attacker can test guesses and multiply ciphertexts. OAEP fixes both.')
K.quiz('m', 'RSA-CRT decryption is about how much faster than direct decryption?', ['2 times', '4 times', '8 times', '100 times'], 1, 'Two half size exponentiations.', 'Each half costs about 1/8, two of them about 1/4 of the full cost.')
K.quiz('m', 'Which padding should be used for RSA encryption today?', ['None', 'PKCS #1 v1.5', 'OAEP', 'Zero padding'], 2, 'Optimal.', 'OAEP is randomized and non malleable. PKCS #1 v1.5 encryption falls to padding oracles.')
K.quiz('h', 'One faulty RSA-CRT signature s&prime; on m is wrong mod q but right mod p. What reveals p?', ['s&prime; mod n', 'gcd(s&prime;<sup>e</sup> &minus; m, n)', 's&prime; &minus; m', 'n / s&prime;'], 1, 's&prime;<sup>e</sup> &equiv; m mod p only.', 'p divides s&prime;<sup>e</sup> &minus; m but q does not, so the gcd with n is p (Bellcore attack).')
K.quiz('h', 'The same message goes to three people, each with e = 3 and no padding. The attacker', ['Learns nothing', 'Uses CRT to get m<sup>3</sup> mod n<sub>1</sub>n<sub>2</sub>n<sub>3</sub>, which equals m<sup>3</sup>, then takes a cube root', 'Must factor all three moduli', 'Needs one private key'], 1, 'Håstad.', 'm<sup>3</sup> &lt; n<sub>1</sub>n<sub>2</sub>n<sub>3</sub>, so the CRT result is m<sup>3</sup> exactly.')
K.quiz('h', 'Wiener’s attack works when', ['e is small', 'd is smaller than about n<sup>1/4</sup> / 3', 'p and q are far apart', 'OAEP is used'], 1, 'Small private exponent.', 'Then k / d is a convergent of e / n. FIPS 186-5 requires d &gt; 2<sup>nlen/2</sup>.')
K.quiz('h', 'Which property of RSA key transport led TLS 1.3 to drop it?', ['It is too slow', 'It gives no forward secrecy', 'It needs large e', 'It cannot use AES'], 1, 'Stolen key later.', 'Anyone who later steals the server’s RSA key can decrypt recorded sessions. Ephemeral Diffie-Hellman avoids this.')
K.quiz('x', 'In the style of an MIT 6.875 question: why does RSA decryption work for m with gcd(m, n) = p?', ['It does not work', 'Mod p both sides are 0, mod q Fermat applies, and CRT joins them', 'Euler’s theorem covers it directly', 'Because e is odd'], 1, 'Split by prime.', 'Euler’s theorem needs gcd(m, n) = 1, so the proof works mod p and mod q separately.')
K.quiz('x', 'In the style of a Stanford CS 255 exam: the Bleichenbacher attack needs', ['The private key', 'A server that leaks whether a ciphertext has valid PKCS #1 v1.5 padding', 'A quantum computer', 'Two keys that share a prime'], 1, 'Oracle.', 'Each yes or no answer narrows the range of m. About a million queries recover it. ROBOT (2017) found it still working.')

K.calc('e', 'For RSA with p = 5 and q = 11, what is n?', '55', 'n = p q.', ['5 &times; 11.', 'n is public.', eq('n = 55')], check=5 * 11)
K.calc('e', 'For p = 5 and q = 11, what is &phi;(n)?', '40', '(p &minus; 1)(q &minus; 1).', ['4 &times; 10.', '&phi;(n) is secret.', eq('&phi;(55) = 40')], check=4 * 10)
K.calc('e', 'Encrypt m = 2 with n = 55 and e = 3.', '8', 'c = m<sup>e</sup> mod n.', ['2<sup>3</sup> = 8.', '8 &lt; 55, no reduction.', eq('c = 8')], check=pow(2, 3, 55))
K.calc('m', 'With &phi;(n) = 40 and e = 3, find d.', '27', 'Inverse of 3 mod 40.', ['3 &times; 27 = 81.', '81 = 2 &times; 40 + 1.', eq('d = 27')], check=pow(3, -1, 40))
K.calc('m', 'Decrypt c = 8 with n = 55 and d = 27.', '2', 'Use Euler or compute 8<sup>27</sup> mod 55.', ['8 = 2<sup>3</sup>, so 8<sup>27</sup> = 2<sup>81</sup>.', '&lambda;(55) = lcm(4, 10) = 20 and 81 mod 20 = 1.', eq('2<sup>81</sup> &equiv; 2<sup>1</sup> = 2 (mod 55)')], check=pow(8, 27, 55))
K.calc('m', 'For the toy key p = 61, d = 2753, what is d<sub>p</sub> = d mod (p &minus; 1)?', '53', 'Divide by 60.', ['60 &times; 45 = 2700.', '2753 &minus; 2700 = 53.', eq('d<sub>p</sub> = 53')], check=2753 % 60)
K.calc('m', 'c = 2790 encrypts 65 under n = 3233, e = 17. An attacker sends c &middot; 2<sup>17</sup> mod n. What does it decrypt to?', '130', 'Malleability.', ['(2 m)<sup>e</sup> = 2<sup>e</sup> m<sup>e</sup>.', 'So it decrypts to 2 &times; 65.', eq('130')], check=pow(2790 * pow(2, 17, 3233) % 3233, 2753, 3233))
K.calc('m', 'What is &lambda;(3233) = lcm(60, 52)?', '780', 'lcm = product / gcd.', ['gcd(60, 52) = 4.', '60 &times; 52 / 4 = 780.', eq('&lambda;(3233) = 780')], check=__import__('math').lcm(60, 52))
K.calc('h', 'With e = 3, no padding and a 2048 bit n, the ciphertext is c = 1,000,000. What is m?', '100', 'm<sup>3</sup> &lt; n, so no reduction happened.', ['c = m<sup>3</sup> exactly.', 'Take the ordinary cube root.', eq('m = 1,000,000<sup>1/3</sup> = 100')], check=round(1000000 ** (1 / 3)))
K.calc('h', 'For the toy key p = 61, q = 53, what is q<sub>inv</sub> = q<sup>&minus;1</sup> mod p?', '38', 'Find x with 53x &equiv; 1 (mod 61).', ['53 &times; 38 = 2014.', '2014 = 33 &times; 61 + 1.', eq('q<sub>inv</sub> = 38')], check=pow(53, -1, 61))
K.calc('h', 'Wiener’s attack works for d &lt; n<sup>1/4</sup> / 3. For a 1024 bit n, about how many bits may d have at most? Round down.', '254', 'log<sub>2</sub> n<sup>1/4</sup> = 256.', ['log<sub>2</sub> 3 &asymp; 1.58.', '256 &minus; 1.58 = 254.4.', eq('about 254 bits')], check=int(256 - __import__('math').log2(3)))
K.calc('x', 'In the style of an IIT Bombay exam: factor n = 5959 by Fermat’s method. Give the smaller prime.', '59', 'Start at a = &lceil;&radic;5959&rceil; = 78.', ['78<sup>2</sup> &minus; 5959 = 125, 79<sup>2</sup> &minus; 5959 = 282, not squares.', '80<sup>2</sup> &minus; 5959 = 441 = 21<sup>2</sup>.', eq('5959 = (80 &minus; 21)(80 + 21) = 59 &times; 101')], check=min(k for k in range(2, 78) if 5959 % k == 0))
K.calc('x', 'How many bytes can one RSA-OAEP block carry with a 2048 bit key and SHA-256?', '190', 'k &minus; 2h &minus; 2.', ['k = 256 bytes, h = 32 bytes.', '256 &minus; 64 &minus; 2.', eq('190 bytes')], check=256 - 2 * 32 - 2)

K.assign('rsa_private', 'e', 'Compute the private exponent',
         '<p>Write <code>rsa_private(p, q, e)</code> that returns d = e<sup>&minus;1</sup> mod (p &minus; 1)(q &minus; 1), or None when gcd(e, &phi;) is not 1. You may use pow(e, -1, phi) after checking the gcd.</p>',
         '''
from math import gcd

def rsa_private(p, q, e):
    # your code here
    pass
''', [('rsa_private(61, 53, 17)', 2753), ('rsa_private(5, 11, 3)', 27), ('rsa_private(5, 11, 5)', None), ('rsa_private(11, 13, 7)', 103)],
         '''
from math import gcd

def rsa_private(p, q, e):
    phi = (p - 1) * (q - 1)
    if gcd(e, phi) != 1:
        return None
    return pow(e, -1, phi)
''', 'Compute phi first, check gcd(e, phi), then invert.', '<p>With p = 5, q = 11 and e = 5, gcd(5, 40) = 5, so no d exists and the "encryption" is not even one to one.</p>')
K.assign('crt_decrypt', 'm', 'RSA decryption with CRT',
         '<p>Write <code>crt_decrypt(c, p, q, d)</code> that decrypts with d<sub>p</sub>, d<sub>q</sub>, q<sub>inv</sub> and Garner’s formula. Do not compute pow(c, d, p * q).</p>',
         '''
def crt_decrypt(c, p, q, d):
    # your code here
    pass
''', [('crt_decrypt(2790, 61, 53, 2753)', 65), ('crt_decrypt(8, 5, 11, 27)', 2),
      ('crt_decrypt(598195729194, 1000003, 1000033, 983264276609)', 424242)],
         '''
def crt_decrypt(c, p, q, d):
    dp = d % (p - 1)
    dq = d % (q - 1)
    q_inv = pow(q, -1, p)
    mp = pow(c, dp, p)
    mq = pow(c, dq, q)
    h = q_inv * (mp - mq) % p
    return mq + h * q
''', 'Compute mp and mq with the reduced exponents, then h = q_inv * (mp - mq) mod p and m = mq + h q.', '<p>Python’s % keeps h between 0 and p &minus; 1 even when mp &lt; mq, so m always lands between 0 and n &minus; 1. In C or Java you would add p first.</p>')
K.assign('cube_root', 'm', 'The integer cube root behind the small e attack',
         '<p>Write <code>cube_root(x)</code> that returns the largest whole number r with r<sup>3</sup> &le; x, for any x &ge; 0. Use binary search on whole numbers, not floats, because floats lose precision for big numbers.</p>',
         '''
def cube_root(x):
    # your code here
    pass
''', [('cube_root(1000000)', 100), ('cube_root(27)', 3), ('cube_root(26)', 2), ('cube_root(0)', 0), ('cube_root(12345 ** 3)', 12345),
      ('cube_root(2 ** 300) == 2 ** 100', True)],
         '''
def cube_root(x):
    low, high = 0, 1
    while high ** 3 <= x:
        high = high * 2
    while low < high:
        mid = (low + high + 1) // 2
        if mid ** 3 <= x:
            low = mid
        else:
            high = mid - 1
    return low
''', 'Double high until high cubed passes x, then binary search keeping low cubed at most x.', '<p>round(x ** (1 / 3)) fails for big ciphertexts because a float only holds about 16 digits. The small e attack on a real ciphertext needs exact whole number arithmetic.</p>')

K.must('Keys', 'n = pq, &phi; = (p &minus; 1)(q &minus; 1), e = 65537 with gcd(e, &phi;) = 1, d = e<sup>&minus;1</sup> mod &phi; (or &lambda;).')
K.must('Use', 'c = m<sup>e</sup> mod n, m = c<sup>d</sup> mod n. Sign s = pad(H(M))<sup>d</sup>, verify s<sup>e</sup>. 61, 53, 17, 2753: 65 to 2790.')
K.must('Proof', 'Fermat mod p and mod q, CRT joins. Works for every m, even gcd(m, n) &ne; 1.')
K.must('CRT', 'd<sub>p</sub>, d<sub>q</sub>, q<sub>inv</sub>, m = m<sub>q</sub> + q &middot; (q<sub>inv</sub>(m<sub>p</sub> &minus; m<sub>q</sub>) mod p). 4 times faster. Fault: gcd(s&prime;<sup>e</sup> &minus; m, n) = p.')
K.must('Attacks', 'Textbook: deterministic, malleable. Small e cube root, Håstad, shared prime gcd, Fermat for close p, q, Wiener for d &lt; n<sup>1/4</sup>/3.')
K.must('Padding and size', 'OAEP to encrypt, PSS to sign. v1.5 encryption: Bleichenbacher, ROBOT. 2048 = 112 bits, 3072 = 128. Quantum: gone after 2035.')

T = K.topic(
    slug='cy-rsa', topic='cy-rsa', step=(2, 'Public key cryptography and its maths', 'cy-c2', 'The number theory behind public keys, then RSA, Diffie-Hellman and elliptic curves, each with its proofs and its attacks.', 'Advanced'),
    title='RSA: keys, proofs, signatures and attacks', short='RSA', badge='2.2', minutes=90,
    lead='RSA from first principles: its history, key generation, encryption and decryption, the full correctness proof, signatures, fast CRT decryption and the Bellcore fault attack, the classic attacks on textbook RSA (malleability, small e, Håstad, shared primes, Fermat factoring, Wiener), OAEP and PSS padding with Bleichenbacher’s attack, key sizes and the quantum deadline.',
    desc='RSA, Rivest Shamir Adleman, Clifford Cocks, key generation, public exponent 65537, private exponent, Carmichael lambda, FIPS 186-5, RSA correctness proof, RSA signature, PSS, existential forgery, RSA-CRT, Garner, Bellcore fault attack, blinding, timing attack, textbook RSA, malleability, small exponent attack, Hastad broadcast attack, shared prime gcd, Fermat factoring, ROCA, Wiener attack, continued fraction, Boneh Durfee, OAEP, PKCS1 v1.5, Bleichenbacher, ROBOT, padding oracle, hybrid encryption, key size, NIST IR 8547, Shor, post quantum',
    summary='key generation, encryption, correctness proof, signatures, CRT and faults, textbook attacks, Wiener, OAEP and PSS, key sizes.',
    keywords=['RSA', 'key generation', 'correctness proof', 'signature', 'RSA-CRT', 'Bellcore', 'Hastad', 'Wiener', 'OAEP', 'Bleichenbacher'],
    recap='<p>The formulas take five lines. Safe RSA takes much more: random primes, the right exponents, padding with OAEP or PSS, constant time code and checked signatures.</p>',
    added='2026-11-14')
