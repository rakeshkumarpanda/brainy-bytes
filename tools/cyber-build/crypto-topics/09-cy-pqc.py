# Cryptography 3.2: post quantum cryptography. Checked against Shor (1997), Grover (1996), Regev (2005), FIPS 203, 204
# and 205 (August 2024, sizes checked with the cryptography package), NIST IR 8413 and IR 8547 (draft), NSA CNSA 2.0,
# Beullens (Rainbow, 2022), Castryck and Decru (SIKE, 2022), Gidney (2025) and Lamport (1979).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-pqc')
K = Kit()

K.code('shor_classical', r'''
# The number theory inside Shor's algorithm. A quantum computer finds the period r quickly.
# Here we find it slowly by trying powers, which is fine for tiny numbers like 15 and 21.
from math import gcd

def period(a, N):                       # smallest r > 0 with a^r = 1 mod N
    r, value = 1, a % N
    while value != 1:
        value = value * a % N
        r = r + 1
    return r

def shor_factor(N, a):
    g = gcd(a, N)
    if g != 1:
        return g, N // g, "lucky: a shares a factor with N"
    r = period(a, N)
    if r % 2 == 1:
        return None, None, f"period r = {r} is odd, pick another a"
    x = pow(a, r // 2, N)
    if x == N - 1:
        return None, None, f"a^(r/2) = -1 mod N, pick another a"
    return gcd(x - 1, N), gcd(x + 1, N), f"period r = {r}, a^(r/2) mod N = {x}"

print("powers of 7 mod 15:", [pow(7, k, 15) for k in range(1, 9)])
for N, a in [(15, 7), (21, 2), (35, 3), (15, 14)]:
    p, q, note = shor_factor(N, a)
    print(f"N = {N}, a = {a}: {note} -> factors {p} and {q}")
''', long=True)

K.code('lwe_toy', r'''
# Learning With Errors: Regev's encryption of one bit at a time (toy sizes, not secure)
import random

rng = random.Random(42)
q, n, m = 97, 8, 20                      # modulus, secret length, number of public samples

s = [rng.randrange(q) for i in range(n)]                       # the secret vector
A = [[rng.randrange(q) for j in range(n)] for i in range(m)]  # public random matrix
e = [rng.choice([-1, 0, 1]) for i in range(m)]                 # small errors
b = [(sum(A[i][j] * s[j] for j in range(n)) + e[i]) % q for i in range(m)]
# public key: (A, b). Without the errors, Gaussian elimination would find s at once.

def encrypt(bit):
    rows = [i for i in range(m) if rng.random() < 0.5]        # a random subset of samples
    u = [sum(A[i][j] for i in rows) % q for j in range(n)]
    v = (sum(b[i] for i in rows) + bit * (q // 2)) % q
    return u, v

def decrypt(u, v):
    d = (v - sum(u[j] * s[j] for j in range(n))) % q           # = bit * q/2 + small noise
    return 0 if min(d, q - d) < q // 4 else 1, d

bits = [1, 0, 1, 1, 0, 0, 1, 0]
results = [decrypt(*encrypt(x)) for x in bits]
print("sent:     ", bits)
print("received: ", [r[0] for r in results])
print("noisy values (near 0 means 0, near 48 means 1):", [r[1] for r in results])

# Why the errors matter: without them, s falls out of plain linear algebra
print("with errors the public key looks random. With e = 0 it would be b = A s, solvable in milliseconds.")
''', long=True)

K.code('baby_kyber', r'''
# A baby version of ML-KEM's core: Module-LWE with polynomials (toy sizes, NOT the real standard)
import random

rng = random.Random(7)
q, n, k = 3329, 8, 2                     # real ML-KEM: q = 3329, n = 256, k = 2, 3 or 4

def poly_mul(a, b):                      # multiply in Z_q[x] / (x^n + 1): x^n wraps round to -1
    out = [0] * n
    for i in range(n):
        for j in range(n):
            if i + j < n:
                out[i + j] = (out[i + j] + a[i] * b[j]) % q
            else:
                out[i + j - n] = (out[i + j - n] - a[i] * b[j]) % q
    return out

def poly_add(a, b):
    return [(x + y) % q for x, y in zip(a, b)]

def small():                             # coefficients from -2 to 2, like the CBD noise in ML-KEM
    return [rng.choice([-2, -1, 0, 1, 2]) % q for i in range(n)]

def mat_vec(M, v):                       # k by k matrix of polynomials times a vector of k polynomials
    out = []
    for row in M:
        acc = [0] * n
        for a, b in zip(row, v):
            acc = poly_add(acc, poly_mul(a, b))
        out.append(acc)
    return out

def transpose(M):
    return [[M[j][i] for j in range(k)] for i in range(k)]

# Key generation
A = [[[rng.randrange(q) for c in range(n)] for j in range(k)] for i in range(k)]
s = [small() for i in range(k)]
e = [small() for i in range(k)]
t = [poly_add(x, y) for x, y in zip(mat_vec(A, s), e)]        # public key (A, t), secret s

# Encrypt 8 message bits, each scaled to 0 or about q/2
message = [1, 0, 1, 1, 0, 1, 0, 0]
r = [small() for i in range(k)]
e1 = [small() for i in range(k)]
e2 = small()
u = [poly_add(x, y) for x, y in zip(mat_vec(transpose(A), r), e1)]
v = e2
for ti, ri in zip(t, r):
    v = poly_add(v, poly_mul(ti, ri))
v = poly_add(v, [bit * ((q + 1) // 2) for bit in message])

# Decrypt: v - s.u = m * q/2 + (small noise)
w = v
for si, ui in zip(s, u):
    w = [(x - y) % q for x, y in zip(w, poly_mul(si, ui))]
decoded = [1 if q // 4 < c < 3 * q // 4 else 0 for c in w]
print("message:", message)
print("decoded:", decoded, "| correct:", decoded == message)
print("noisy coefficients:", w)
print("public t here:", k * n, "numbers plus a seed for A. Real ML-KEM-768: k = 3, n = 256, 1184 bytes.")
''', long=True)

K.code('lamport', r'''
# Lamport one time signatures (1979): security from a hash function only, so quantum computers do not break it
import hashlib
import secrets

def H(data):
    return hashlib.sha256(data).digest()

def keygen():
    private = [[secrets.token_bytes(32), secrets.token_bytes(32)] for i in range(256)]
    public = [[H(a), H(b)] for a, b in private]
    return private, public

def bits_of(message):
    digest = int.from_bytes(H(message), "big")
    return [(digest >> (255 - i)) & 1 for i in range(256)]

def sign(private, message):
    return [private[i][bit] for i, bit in enumerate(bits_of(message))]   # reveal one secret per bit

def verify(public, message, signature):
    return all(H(signature[i]) == public[i][bit] for i, bit in enumerate(bits_of(message)))

private, public = keygen()
sig = sign(private, b"release v1.0")
print("signature size:", 256 * 32, "bytes, public key:", 2 * 256 * 32, "bytes")
print("valid:", verify(public, b"release v1.0", sig))
print("changed message valid:", verify(public, b"release v6.6", sig))

# Signing a second message with the same key reveals more secrets
sig2 = sign(private, b"release v2.0")
known = set()
for i in range(256):
    known.add((i, bits_of(b"release v1.0")[i]))
    known.add((i, bits_of(b"release v2.0")[i]))
both = sum(1 for i in range(256) if (i, 0) in known and (i, 1) in known)
print("after two signatures the attacker knows both secrets for", both, "of 256 positions")
print("so each key must sign ONE message. Merkle trees (XMSS, LMS) and SLH-DSA build many-time schemes from this idea.")
''', long=True)

K.code('pq_real', r'''
# Real ML-KEM-768 and ML-DSA-65 (FIPS 203 and 204), plus a hybrid with X25519 (pip install cryptography)
from cryptography.hazmat.primitives.asymmetric import mlkem, mldsa
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

raw, pub_raw = serialization.Encoding.Raw, serialization.PublicFormat.Raw

# ML-KEM: a key encapsulation mechanism
receiver = mlkem.MLKEM768PrivateKey.generate()
public = receiver.public_key()
secret_sender, ciphertext = public.encapsulate()      # sender makes a random secret and wraps it
secret_receiver = receiver.decapsulate(ciphertext)     # receiver unwraps it
print("ML-KEM-768 public key:", len(public.public_bytes(raw, pub_raw)), "bytes, ciphertext:", len(ciphertext), "bytes")
print("shared secret:", len(secret_sender), "bytes, equal:", secret_sender == secret_receiver)

# Hybrid: secure if EITHER X25519 or ML-KEM holds (X25519MLKEM768 in TLS)
a, b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
classical = a.exchange(b.public_key())
hybrid_key = HKDF(hashes.SHA256(), 32, None, b"hybrid demo").derive(secret_sender + classical)
print("hybrid key:", len(hybrid_key), "bytes from ML-KEM secret + X25519 secret")

# ML-DSA: lattice signatures
signer = mldsa.MLDSA65PrivateKey.generate()
signature = signer.sign(b"firmware 7.2")
verifier = signer.public_key()
verifier.verify(signature, b"firmware 7.2")
print("ML-DSA-65 public key:", len(verifier.public_bytes(raw, pub_raw)), "bytes, signature:", len(signature), "bytes, verified")
try:
    verifier.verify(signature, b"firmware 7.3")
except InvalidSignature:
    print("changed firmware rejected")
''')

K.lesson('idea', 'The quantum threat and why we must move now', f'''
{talk('In 1994 Peter Shor, then at Bell Labs, showed that a quantum computer could factor large numbers and compute discrete logarithms in polynomial time. That one result threatens RSA, Diffie-Hellman and elliptic curves, which means almost all the public key cryptography on the internet. Two years later Lov Grover found a quantum search algorithm that speeds up brute force from n steps to about the square root of n, which halves the effective strength of symmetric keys. No quantum computer today comes close to breaking real keys. The largest machines have around a thousand noisy physical qubits, and an attack on RSA-2048 is estimated to need about a million. So why worry now? Because of harvest now, decrypt later: an adversary can record encrypted traffic today and decrypt it once a quantum computer exists. Michele Mosca put this as a simple inequality. If the years your data must stay secret plus the years your migration takes are more than the years until a quantum computer arrives, you are already late. In August 2024 NIST published the first three post quantum standards, and the move has begun across browsers, messaging apps and operating systems.')}
{src('Shor (1994, SIAM J. Computing 1997), Grover (1996), Regev, On Lattices, Learning with Errors (2005), FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), NIST IR 8413 and IR 8547, NSA CNSA 2.0 (2022), Gidney, How to Factor 2048 Bit RSA Integers with Less Than a Million Noisy Qubits (2025), Lamport (1979).')}
{wwh('<b>Post quantum cryptography</b> (PQC) means classical algorithms, run on ordinary computers, whose security rests on problems that quantum computers are not known to solve quickly, such as lattice problems and hash functions.',
     'Shor’s algorithm breaks RSA, DH and ECC. Data recorded today may be decrypted later, so long lived secrets need protection now.',
     'Replace key exchange with ML-KEM (often as a hybrid with X25519) and signatures with ML-DSA, SLH-DSA or FN-DSA. Use AES-256 and SHA-384 or larger for long term symmetric security.')}
{fxs(fx('Mosca’s inequality', 'if x + y &gt; z, act now', 'x = years data must stay secret, y = years to migrate, z = years until a cryptographically relevant quantum computer. x = 10, y = 5, z = 12: exposed for 3 years.', key=True),
     fx('Grover’s speed up', 'about (&pi;/4)&radic;N quantum steps to search N keys', 'AES-128 drops to about 64 bit strength in theory, AES-256 to 128. Grover does not parallelise well, so AES-128 is still considered acceptable, but AES-256 is advised for long term data.', key=True))}
{table(['Algorithm', 'Quantum attack', 'Status after a large quantum computer'], [
    ['RSA, DH, ECDH, ECDSA, Ed25519', 'Shor: polynomial time', 'Broken'],
    ['AES-128', 'Grover: about 2<sup>64</sup>', 'Weakened, still usable for most data'],
    ['AES-256, SHA-384, SHA-512', 'Grover: about 2<sup>128</sup> and more', 'Safe'],
    ['ML-KEM, ML-DSA, SLH-DSA', 'None known', 'Believed safe']])}
''', kw=['post quantum cryptography', 'PQC', 'Shor', 'Grover', 'harvest now decrypt later', 'Mosca inequality', 'quantum threat', 'qubits'])

K.lesson('shor', 'How Shor’s algorithm breaks RSA', f'''
{talk('Shor’s algorithm turns factoring into a different question: finding the period of a sequence. Pick a random number a and look at a, a squared, a cubed and so on, all modulo N. Because there are only N possible values, the sequence must repeat, and the length of the cycle is called the period r. Once r is known, and if it is even, a to the r minus 1 is divisible by N, and it splits as a to the r over 2 minus 1, times a to the r over 2 plus 1. Each factor usually shares exactly one prime with N, and Euclid’s algorithm pulls it out. Finding r is the hard part. A classical computer has to walk through the sequence, which takes about as long as factoring. A quantum computer prepares all exponents at once in superposition, computes a to the x modulo N for all of them together, and then applies the quantum Fourier transform, which turns the hidden repetition into a measurable frequency. The same idea computes discrete logarithms, which breaks Diffie-Hellman and elliptic curves. In 2001 IBM used a seven qubit machine to factor 15 this way. Factoring a 2048 bit number needs error corrected logical qubits, built from many physical ones, which is the engineering challenge still ahead.')}
{viz('cyshor')}
{run('shor_classical')}
{fxs(fx('Period', 'r = smallest r &gt; 0 with a<sup>r</sup> &equiv; 1 (mod N)', 'a = 7, N = 15: 7, 4, 13, 1, so r = 4.', key=True),
     fx('Factors from the period', 'if r is even and a<sup>r/2</sup> &#8802; &minus;1: p = gcd(a<sup>r/2</sup> &minus; 1, N), q = gcd(a<sup>r/2</sup> + 1, N)', '7<sup>2</sup> = 49 &equiv; 4 (mod 15): gcd(3, 15) = 3, gcd(5, 15) = 5.', key=True),
     fx('Cost', 'about O((log N)<sup>3</sup>) quantum gates with schoolbook arithmetic', 'Polynomial, against the sub exponential number field sieve. Gidney (2025): RSA-2048 with under a million noisy qubits in under a week.'))}
''', kw=['Shor algorithm', 'period finding', 'quantum Fourier transform', 'superposition', 'factoring', 'discrete log', 'logical qubits', 'Gidney 2025'])

K.lesson('lwe', 'Lattices and Learning With Errors', f'''
{talk('Most of the new standards rest on lattices. A lattice is a regular grid of points in many dimensions, all whole number combinations of a few basis vectors. Two problems on lattices seem hard even for quantum computers: finding the shortest non zero vector, and finding the lattice point closest to a given point, once there are hundreds of dimensions. In 2005 Oded Regev introduced a problem called Learning With Errors that is easy to state and is linked to those lattice problems. You are given many random linear equations in a secret vector s, modulo a small number q, but each answer has a small random error added. Without the errors, ordinary Gaussian elimination from school would find s in moments. With the errors, all known algorithms, classical and quantum, take exponential time. Regev proved that solving LWE on average would solve worst case lattice problems with a quantum computer, and he received the Gödel Prize in 2018. Encryption works because the owner of s can remove almost everything except the small noise and the message, which sits either near zero or near q over 2.')}
{wwh('<b>Learning With Errors</b> (LWE): given A and b = A s + e mod q, with random A and small error e, find s. Its decision version: tell b apart from random.',
     'It gives encryption and signatures believed secure against quantum computers, with worst case to average case reductions to lattice problems, and it is fast.',
     'To encrypt a bit, combine a random subset of the public samples and add the bit times q/2. To decrypt, subtract &lang;u, s&rang;. What is left is the bit times q/2 plus a small sum of errors. Round to the nearest of 0 or q/2.')}
{viz('cylwe')}
{run('lwe_toy')}
{fxs(fx('LWE sample', 'b = &lang;a, s&rang; + e (mod q), with e small', 'Toy: q = 97, n = 8, errors in {{&minus;1, 0, 1}}.', key=True),
     fx('Correct decryption', '|sum of errors| &lt; q/4', 'Toy: at most 20 errors of size 1, so |noise| &le; 20 &lt; 24.25, decryption never fails.', key=True),
     fx('Ring and module LWE', 'replace numbers by polynomials in Z<sub>q</sub>[x]/(x<sup>n</sup> + 1)', 'One polynomial product does the work of an n by n matrix, so keys shrink from megabytes to about a kilobyte.'))}
{deep('Why the noise is essential', '<p>If e = 0, then b = A s mod q is a linear system. With m &ge; n equations, Gaussian elimination mod q recovers s in O(n<sup>3</sup>) steps. Adding small noise makes each equation slightly wrong, and errors compound when equations are combined, so elimination fails. The best known attacks instead look for short vectors in a related lattice using BKZ lattice reduction, whose cost grows exponentially with the dimension. Parameters are chosen so this cost exceeds 2<sup>128</sup> or more, also against quantum versions of these attacks.</p>')}
''', kw=['lattice', 'shortest vector problem', 'Learning With Errors', 'LWE', 'Regev', 'Godel Prize', 'ring LWE', 'module LWE', 'BKZ', 'noise'])

K.lesson('mlkem', 'ML-KEM (Kyber): the new key exchange', f'''
{talk('ML-KEM, published as FIPS 203 in August 2024, is the standardised form of CRYSTALS-Kyber, designed by an international team and chosen by NIST in 2022 after a six year public competition that started with 82 submissions. It is a key encapsulation mechanism, or KEM, which is slightly different from Diffie-Hellman. The receiver publishes a public key. The sender runs Encaps, which makes a fresh random 32 byte secret and a ciphertext that wraps it. The receiver runs Decaps on the ciphertext and gets the same secret. Inside, ML-KEM uses module LWE over polynomials with 256 coefficients modulo the prime 3329, and a transform by Fujisaki and Okamoto that makes it secure even against attackers who can feed it chosen ciphertexts. It is fast, often faster than X25519, but its keys and ciphertexts are about a kilobyte each instead of 32 bytes. Because the new schemes have had less time under attack than elliptic curves, the first deployments are hybrids: X25519MLKEM768 combines both shared secrets, so the connection is safe if either one holds. Chrome turned it on by default in 2024, and OpenSSH 10 made a similar hybrid its default in 2025.')}
{run('baby_kyber')}
{wwh('<b>ML-KEM</b> (FIPS 203) is a lattice based key encapsulation mechanism: KeyGen gives (ek, dk), Encaps(ek) gives (K, c), Decaps(dk, c) gives K.',
     'It replaces Diffie-Hellman and RSA key transport for establishing session keys, safe against quantum computers as far as anyone knows.',
     'Public key t = A s + e with A from a seed. Encrypt with u = A<sup>T</sup> r + e<sub>1</sub>, v = t<sup>T</sup> r + e<sub>2</sub> + &lceil;q/2&rfloor; m. Decrypt with v &minus; s<sup>T</sup> u. The FO transform re-encrypts during Decaps to reject tampered ciphertexts.')}
{table(['Parameter set', 'Security category', 'Public key', 'Ciphertext', 'Shared secret'], [
    ['ML-KEM-512', '1 (like AES-128)', '800 bytes', '768 bytes', '32 bytes'],
    ['ML-KEM-768', '3 (like AES-192)', '1184 bytes', '1088 bytes', '32 bytes'],
    ['ML-KEM-1024', '5 (like AES-256)', '1568 bytes', '1568 bytes', '32 bytes'],
    ['X25519 for comparison', 'about 128 bit, not quantum safe', '32 bytes', '32 bytes', '32 bytes']])}
{fxs(fx('ML-KEM ring', 'R<sub>q</sub> = Z<sub>q</sub>[x]/(x<sup>256</sup> + 1), q = 3329, module rank k = 2, 3, 4', 'x<sup>256</sup> = &minus;1 in this ring, which the program’s poly_mul uses with n = 8.', key=True),
     fx('Hybrid secret (X25519MLKEM768)', 'K = KDF(K<sub>ML-KEM</sub> &#8214; K<sub>X25519</sub>)', 'An attacker must break both to learn K.'))}
{note('Implementations must be constant time. In 2024 the KyberSlash bugs showed that a division whose time depended on secret data leaked keys from several Kyber libraries. Use well reviewed libraries.', 'warn')}
''', kw=['ML-KEM', 'Kyber', 'FIPS 203', 'key encapsulation', 'KEM', 'module LWE', 'Fujisaki-Okamoto', 'X25519MLKEM768', 'hybrid', 'KyberSlash', 'OpenSSH'])

K.lesson('sigs', 'Post quantum signatures: ML-DSA, SLH-DSA and FN-DSA', f'''
{talk('For signatures, NIST standardised two schemes in 2024 and has a third on the way. ML-DSA, FIPS 204, is the standard form of CRYSTALS-Dilithium. It is a lattice signature built with a technique called Fiat-Shamir with aborts, introduced by Vadim Lyubashevsky: the signer computes a candidate signature, and if it would leak information about the secret key, throws it away and tries again. ML-DSA is fast and is the general purpose choice, but its signatures are about 2.4 to 4.6 kilobytes, compared with 64 bytes for Ed25519. SLH-DSA, FIPS 205, is the standard form of SPHINCS+. It relies only on hash functions, the most conservative assumption in cryptography, with public keys of just 32 bytes, but signatures of 8 to 50 kilobytes and slow signing. It grew from Leslie Lamport’s one time signatures of 1979 and Ralph Merkle’s tree of 1979. FN-DSA, based on Falcon, gives much smaller lattice signatures but needs delicate floating point code. Not every candidate survived: in 2022 Ward Beullens broke the multivariate scheme Rainbow over a weekend on a laptop, and Castryck and Decru broke the isogeny scheme SIKE in about an hour.')}
{viz('cylamport')}
{run('lamport')}
{table(['Scheme', 'Based on', 'Public key', 'Signature', 'Notes'], [
    ['ML-DSA-44 / 65 / 87 (FIPS 204)', 'Module lattices', '1312 / 1952 / 2592 bytes', '2420 / 3309 / 4627 bytes', 'General purpose default'],
    ['SLH-DSA-128s / 128f (FIPS 205)', 'Hash functions only', '32 bytes', '7856 / 17088 bytes', 'Most conservative, slow to sign'],
    ['FN-DSA-512 (Falcon, FIPS 206 in progress)', 'NTRU lattices', '897 bytes', 'about 666 bytes', 'Small, tricky to implement'],
    ['XMSS, LMS (SP 800-208)', 'Hash based, stateful', 'about 32 to 64 bytes', '2 to 3 KB', 'Must never reuse a state, firmware signing'],
    ['Ed25519 for comparison', 'Elliptic curve', '32 bytes', '64 bytes', 'Not quantum safe']])}
{local('pq_real', 'It needs a recent cryptography package with ML-KEM and ML-DSA (this page ran version 50): python3 -m pip install --upgrade cryptography.')}
''', kw=['ML-DSA', 'Dilithium', 'FIPS 204', 'SLH-DSA', 'SPHINCS+', 'FIPS 205', 'FN-DSA', 'Falcon', 'Lamport signature', 'XMSS', 'LMS', 'Rainbow', 'SIKE', 'Fiat-Shamir with aborts'])

K.lesson('migrate', 'Migrating to post quantum cryptography', f'''
{talk('Replacing the public key cryptography of the whole world is one of the largest engineering projects in computing, and it is happening now. The steps are well understood. First, make an inventory: find every place that uses RSA, Diffie-Hellman or elliptic curves, in protocols, libraries, certificates, hardware and contracts. Second, build crypto agility, the ability to swap algorithms by configuration instead of rewriting code. Third, protect key exchange first, because recorded traffic is at risk today, while signatures only need to be replaced before a quantum computer exists. Hybrids are the bridge. Signal added the PQXDH protocol in 2023, Apple’s iMessage moved to PQ3 in 2024, and Chrome, Firefox, Cloudflare and OpenSSH all negotiate hybrid key exchange by default. Governments have set deadlines: the NSA’s CNSA 2.0 expects national security systems to use quantum resistant algorithms by about 2033, and NIST’s draft IR 8547 would disallow RSA and elliptic curves after 2035. One alternative often mentioned, quantum key distribution, uses physics instead of maths, but it needs special hardware and trusted relay points, and agencies such as the NSA and the UK’s NCSC do not recommend it for general use.')}
{steps('A migration plan', [
    'Inventory every use of RSA, DH, ECDH, ECDSA and EdDSA, including in vendors’ products and hardware.',
    'Rank by data lifetime: anything secret for 10 or more years goes first (harvest now, decrypt later).',
    'Turn on hybrid key exchange (X25519MLKEM768) in TLS, SSH and VPNs wherever supported.',
    'Design for crypto agility: algorithm choice in configuration, larger buffers for kilobyte keys and signatures.',
    'Plan the signature move: ML-DSA for general use, SLH-DSA or LMS for firmware and roots of trust.',
    'Raise symmetric strength: AES-256, SHA-384 or larger, for long term secrets.'])}
{note('Post quantum keys and signatures are larger. A TLS handshake with ML-KEM-768 adds about 2 KB, which can push the first flight over one network packet and expose old middleboxes that drop large ClientHellos. Test before rollout.', 'tip')}
''', kw=['migration', 'crypto inventory', 'crypto agility', 'hybrid', 'PQXDH', 'iMessage PQ3', 'CNSA 2.0', 'NIST IR 8547', 'QKD', 'BB84'])

K.lesson('versus', 'Post quantum options compared', f'''
{talk('The families of post quantum schemes trade size, speed and confidence. Lattice schemes, ML-KEM and ML-DSA, are fast with keys of around one or two kilobytes, and they are the default choices. Hash based signatures are the most trusted, because they only need a good hash function, but they are large or need careful state handling. Code based encryption such as Classic McEliece, from 1978, has never been broken, but its public keys are hundreds of kilobytes to over a megabyte. HQC, another code based KEM, was chosen by NIST in March 2025 as a backup to ML-KEM built on different maths. Multivariate and isogeny schemes have suffered recent breaks, so they are mainly research topics today. The guiding idea is diversity: if a new attack hits lattices, a hash based or code based fallback must be ready.')}
{versus('Families of post quantum cryptography', ['', 'Lattices (ML-KEM, ML-DSA)', 'Hash based (SLH-DSA, LMS)', 'Codes (HQC, McEliece)', 'Isogenies (CSIDH)', 'Classical ECC today'], [
    ['Confidence', 'High, much studied', 'Highest, hash only', 'High for McEliece', 'Low after the SIKE break', 'Broken by Shor'],
    ['Key sizes', 'About 1 to 2.5 KB', '32 byte keys, 8 to 50 KB signatures', 'Up to about 1 MB public keys', 'Very small', '32 bytes'],
    ['Speed', 'Very fast', 'Slow signing', 'Fast', 'Slow', 'Fast'],
    ['Does', 'KEM and signatures', 'Signatures only', 'KEM', 'Key exchange', 'All'],
    ['Standard', 'FIPS 203, 204', 'FIPS 205, SP 800-208', 'HQC chosen 2025', 'None', 'Being retired by 2035']],
    'Use ML-KEM in a hybrid with X25519 now, ML-DSA for general signatures, and SLH-DSA or LMS where the longest term trust matters.')}
''', kw=['comparison', 'lattice', 'hash based', 'code based', 'Classic McEliece', 'HQC', 'isogeny', 'CSIDH', 'diversity'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Post quantum cryptography is where the newest standards meet active research. A beginner learns that a future quantum computer could break today’s public key cryptography, that data recorded now could be decrypted later, and that new standards already exist and are switched on in browsers. A college student can explain Shor’s period finding and Grover’s square root speed up, run toy LWE and Lamport signatures, and describe what a KEM is and why hybrids are used. A masters student studies lattice problems and reductions, ring and module LWE, the number theoretic transform that makes polynomial multiplication fast, the Fujisaki-Okamoto transform, Fiat-Shamir with aborts, and the BKZ algorithm that sets the parameters. At the research level, people estimate the real cost of lattice attacks, prove security in the quantum random oracle model, design side channel resistant implementations, verify them formally, and estimate how many qubits and how much time Shor’s algorithm really needs.')}
{ladder(
    '<p>Quantum computers could one day break RSA and elliptic curves. New post quantum standards (ML-KEM, ML-DSA, SLH-DSA) are already used by browsers and messaging apps, often together with the old ones.</p>',
    '<p>Explain Shor and Grover, Mosca’s inequality, LWE encryption, the KEM interface, Lamport and Merkle signatures, the parameter tables, and how hybrid key exchange works.</p>',
    '<p>SVP, CVP and Regev’s reduction, ring and module LWE, the NTT, FO and its implicit rejection, Fiat-Shamir with aborts, BKZ and the core SVP cost model, and constant time implementation (KyberSlash).</p>',
    '<p>Concrete lattice attack estimates, QROM proofs, masking against side channels, formally verified PQC (libcrux, the Jasmin and EasyCrypt projects), isogeny research after SIKE, and quantum resource estimates for Shor.</p>')}
{grow('Explain the quantum threat and that new standards exist.',
      'Run toy LWE, Lamport and Shor examples and choose the right standard.',
      'Analyse lattice reductions, FO transforms, attack costs and implementations.')}
''', kw=['beginner', 'expert', 'NTT', 'QROM', 'BKZ', 'core SVP', 'masking', 'formal verification', 'libcrux'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Shor</b> (1994) breaks RSA, DH and ECC by period finding. <b>Grover</b> (1996) halves symmetric strength: use AES-256 for long term secrets.',
    '<b>Harvest now, decrypt later</b>. Mosca: if x + y &gt; z, act now.',
    '<b>Shor’s maths</b>: period r of a<sup>x</sup> mod N, then gcd(a<sup>r/2</sup> &plusmn; 1, N). 15 with a = 7: r = 4, factors 3 and 5.',
    '<b>LWE</b>: b = A s + e mod q. Noise makes it hard. Decrypt by rounding to 0 or q/2 while |noise| &lt; q/4.',
    '<b>ML-KEM</b> (FIPS 203): module LWE, q = 3329, n = 256. ML-KEM-768: 1184 byte key, 1088 byte ciphertext. Deploy as hybrid X25519MLKEM768.',
    '<b>Signatures</b>: ML-DSA (FIPS 204, 2.4 to 4.6 KB), SLH-DSA (FIPS 205, hash based, 8 to 50 KB), FN-DSA (Falcon). Lamport keys sign once.',
    '<b>Broken candidates</b>: Rainbow and SIKE (2022). HQC chosen as a backup KEM (2025).',
    '<b>Migrate</b>: inventory, crypto agility, key exchange first, then signatures. CNSA 2.0 by about 2033, NIST IR 8547 draft disallows RSA and ECC after 2035.'],
    'Cryptography 3.3 closes the section with tools beyond encryption: secret sharing, commitments, zero knowledge proofs, homomorphic encryption and secure multiparty computation.')}
{files('Three tasks: quantum strength of a key, Shor’s factoring step from a period, and polynomial multiplication in the ML-KEM style ring.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which algorithm lets a quantum computer break RSA?', ['Grover', 'Shor', 'Dijkstra', 'AES'], 1, '1994.', 'Shor’s algorithm factors and computes discrete logs in polynomial time.')
K.quiz('e', 'What does "harvest now, decrypt later" mean?', ['Steal passwords today', 'Record encrypted traffic now and decrypt it once a quantum computer exists', 'Delay updates', 'Mine cryptocurrency'], 1, 'Recording.', 'Long lived secrets sent today are at risk, so key exchange must move first.')
K.quiz('e', 'How does Grover’s algorithm affect AES-256?', ['Breaks it', 'Reduces it to about 128 bit strength, still safe', 'No effect', 'Makes it faster'], 1, 'Square root.', 'Grover searches N keys in about &radic;N steps.')
K.quiz('e', 'ML-KEM is used for', ['Signatures', 'Establishing a shared secret key', 'Hashing', 'Compression'], 1, 'KEM.', 'It is a key encapsulation mechanism, replacing Diffie-Hellman style key exchange.')
K.quiz('m', 'What makes LWE hard where plain linear equations are easy?', ['A bigger modulus', 'Small random errors added to each equation', 'Using floats', 'Secret matrices'], 1, 'Noise.', 'Without errors, Gaussian elimination solves for s. Errors defeat it.')
K.quiz('m', 'Why deploy X25519MLKEM768 instead of ML-KEM alone?', ['It is smaller', 'The key stays safe if either X25519 or ML-KEM holds', 'ML-KEM needs X25519 to work', 'For speed'], 1, 'Belt and braces.', 'Hybrids protect against an unexpected break in the newer scheme.')
K.quiz('m', 'SLH-DSA (SPHINCS+) relies on', ['Lattices', 'Only hash functions', 'Elliptic curves', 'Factoring'], 1, 'Most conservative.', 'Its security reduces to properties of the hash function.')
K.quiz('m', 'Why can a Lamport key sign only one message?', ['It expires', 'Each signature reveals half the secrets, and a second one reveals enough to forge', 'The hash changes', 'It is too slow'], 1, 'Reveal.', 'Two different messages expose both secrets in many positions.')
K.quiz('m', 'In Shor’s method, once the period r of a<sup>x</sup> mod N is known and even, the factors come from', ['r itself', 'gcd(a<sup>r/2</sup> &plusmn; 1, N)', 'a &times; r', 'N / r'], 1, 'Difference of squares.', 'a<sup>r</sup> &minus; 1 = (a<sup>r/2</sup> &minus; 1)(a<sup>r/2</sup> + 1) is a multiple of N.')
K.quiz('h', 'Which 2022 event showed the value of algorithm diversity?', ['AES was broken', 'Rainbow and SIKE, both NIST candidates, were broken with ordinary computers', 'RSA-2048 was factored', 'SHA-256 collided'], 1, 'Candidates fell.', 'Beullens broke Rainbow on a laptop, and Castryck and Decru broke SIKE in about an hour.')
K.quiz('h', 'What does the Fujisaki-Okamoto transform add to ML-KEM?', ['Smaller keys', 'Security against chosen ciphertext attacks, by re-encrypting during decapsulation and rejecting mismatches', 'Faster key generation', 'Quantum resistance'], 1, 'CCA.', 'The base LWE scheme is only CPA secure. FO makes tampering detectable.')
K.quiz('h', 'An ML-DSA-65 signature is about how large?', ['64 bytes', '3.3 KB', '50 KB', '1 MB'], 1, 'Kilobytes.', '3309 bytes, about 52 times an Ed25519 signature.')
K.quiz('h', 'Why are stateful hash signatures (XMSS, LMS) risky in practice?', ['They are slow', 'Reusing a one time key state, for example after restoring a backup, breaks security', 'They need quantum hardware', 'They use RSA'], 1, 'State.', 'Each leaf key may sign once, so the signer must never roll back its counter.')
K.quiz('x', 'In the style of an MIT 6.875 question: why does replacing Z<sub>q</sub><sup>n&times;n</sup> matrices with Z<sub>q</sub>[x]/(x<sup>n</sup> + 1) shrink keys?', ['It does not', 'One ring element (n numbers) represents a structured n by n matrix, so keys go from n<sup>2</sup> to n numbers per block', 'Polynomials are compressed', 'q becomes smaller'], 1, 'Negacyclic matrices.', 'Multiplication by a fixed polynomial is a negacyclic matrix fully described by its first column.')
K.quiz('x', 'In the style of an IIT Bombay quantum computing exam: which step of Shor’s algorithm needs the quantum computer?', ['Choosing a', 'Finding the period r with the quantum Fourier transform', 'Computing gcd', 'Checking r is even'], 1, 'Only one part.', 'Everything else is classical number theory that a laptop does instantly.')

K.calc('e', 'Grover’s algorithm against AES-128 gives about 2<sup>k</sup> work. What is k?', '64', 'Square root of 2<sup>128</sup>.', ['&radic;(2<sup>128</sup>) = 2<sup>64</sup>.', 'Hard to parallelise in practice.', eq('k = 64')], check=128 // 2)
K.calc('e', 'And against AES-256?', '128', 'Half the bits.', ['&radic;(2<sup>256</sup>) = 2<sup>128</sup>.', 'Still far out of reach.', eq('k = 128')], check=256 // 2)
K.calc('e', 'How many bytes is an ML-KEM-768 public key?', '1184', 'FIPS 203 table.', ['k = 3 polynomials of 256 coefficients, 12 bits each: 1152 bytes.', 'Plus a 32 byte seed for A.', eq('1152 + 32 = 1184')], check=3 * 256 * 12 // 8 + 32)
K.calc('m', 'Mosca: data must stay secret x = 10 years, migration takes y = 5 years, a quantum computer arrives in z = 12 years. How many years is the data exposed?', '3', 'x + y &minus; z.', ['10 + 5 = 15.', '15 &minus; 12 = 3.', eq('3 years at risk')], check=10 + 5 - 12)
K.calc('m', 'What is the period r of 7<sup>x</sup> mod 15?', '4', 'List the powers.', ['7, 49 &equiv; 4, 28 &equiv; 13, 91 &equiv; 1.', 'Back to 1 after 4 steps.', eq('r = 4')], check=next(r for r in range(1, 15) if pow(7, r, 15) == 1))
K.calc('m', 'With r = 4, compute gcd(7<sup>2</sup> &minus; 1, 15).', '3', '7<sup>2</sup> mod 15 = 4.', ['4 &minus; 1 = 3.', 'gcd(3, 15) = 3.', eq('factor 3')], check=__import__('math').gcd(pow(7, 2, 15) - 1, 15))
K.calc('m', 'In the toy LWE with q = 97, decryption is correct while |noise| is below q/4. What is q/4, rounded down?', '24', '97 / 4.', ['97 / 4 = 24.25.', 'Round down.', eq('24')], check=97 // 4)
K.calc('m', 'An ML-DSA-65 signature is 3309 bytes and an Ed25519 signature 64 bytes. About how many times larger is ML-DSA? Round to a whole number.', '52', 'Divide.', ['3309 / 64 = 51.7.', 'Round.', eq('about 52 times')], check=round(3309 / 64))
K.calc('h', 'A Lamport signature for a 256 bit hash reveals one 32 byte secret per bit. How many bytes is the signature?', '8192', '256 &times; 32.', ['One secret per bit.', '256 &times; 32 = 8192.', eq('8 KB')], check=256 * 32)
K.calc('h', 'In Z<sub>3329</sub>[x]/(x<sup>4</sup> + 1), x<sup>4</sup> &middot; x<sup>3</sup> = &minus;x<sup>3</sup>. Written with coefficients from 0 to 3328, what is the coefficient of x<sup>3</sup>?', '3328', 'x<sup>4</sup> = &minus;1.', ['x<sup>7</sup> = x<sup>4</sup> &middot; x<sup>3</sup> = &minus;x<sup>3</sup>.', '&minus;1 mod 3329 = 3328.', eq('3328 x<sup>3</sup>')], check=-1 % 3329)
K.calc('h', 'Toy LWE: 20 samples, each error in {&minus;1, 0, 1}. What is the largest possible |noise|?', '20', 'All errors the same sign.', ['20 &times; 1.', 'Below q/4 = 24.25, so never a decryption error.', eq('20')], check=20)
K.calc('x', 'X25519MLKEM768 feeds the concatenation of both shared secrets into the KDF. How many bytes is that input?', '64', '32 + 32.', ['ML-KEM shared secret: 32 bytes.', 'X25519 shared secret: 32 bytes.', eq('64 bytes')], check=32 + 32)
K.calc('x', 'In the style of a Waterloo CO 789 question: an ML-KEM-768 ciphertext is 1088 bytes. Its u part is 3 polynomials with 256 coefficients compressed to 10 bits. How many bytes is the v part?', '128', '1088 minus the u part.', ['u: 3 &times; 256 &times; 10 / 8 = 960 bytes.', '1088 &minus; 960 = 128 bytes, that is 256 coefficients of 4 bits.', eq('128 bytes')], check=1088 - 3 * 256 * 10 // 8)

K.assign('quantum_bits', 'e', 'Quantum strength of a symmetric key',
         '<p>Write <code>quantum_bits(key_bits)</code> that returns the approximate security in bits against Grover’s algorithm, which is half the key length (rounded down).</p>',
         '''
def quantum_bits(key_bits):
    # your code here
    pass
''', [('quantum_bits(128)', 64), ('quantum_bits(256)', 128), ('quantum_bits(192)', 96)],
         '''
def quantum_bits(key_bits):
    return key_bits // 2
''', 'Grover gives a square root speed up, which halves the exponent.', '<p>This is why CNSA 2.0 requires AES-256 for national security systems: it keeps 128 bits of strength even against Grover.</p>')
K.assign('shor_step', 'm', 'The classical part of Shor’s algorithm',
         '<p>Write <code>shor_step(N, a)</code>. Find the period r of a<sup>x</sup> mod N by trying powers (fine for small N). If gcd(a, N) &gt; 1 return that gcd. If r is odd or a<sup>r/2</sup> &equiv; &minus;1 (mod N), return None. Otherwise return the smaller of gcd(a<sup>r/2</sup> &minus; 1, N) and gcd(a<sup>r/2</sup> + 1, N).</p>',
         '''
from math import gcd

def shor_step(N, a):
    # your code here
    pass
''', [('shor_step(15, 7)', 3), ('shor_step(21, 2)', 3), ('shor_step(35, 3)', 5), ('shor_step(15, 14)', None), ('shor_step(15, 5)', 5)],
         '''
from math import gcd

def shor_step(N, a):
    g = gcd(a, N)
    if g > 1:
        return g
    r, value = 1, a % N
    while value != 1:
        value = value * a % N
        r = r + 1
    if r % 2 == 1:
        return None
    x = pow(a, r // 2, N)
    if x == N - 1:
        return None
    return min(gcd(x - 1, N), gcd(x + 1, N))
''', 'Loop multiplying by a until you get back to 1 to find r, then use pow(a, r // 2, N) and two gcds.', '<p>For a random a, the chance of success is at least one half, so Shor repeats with a new a a few times at most.</p>')
K.assign('ring_mul', 'h', 'Multiplication in the ML-KEM ring',
         '<p>Write <code>ring_mul(a, b, q)</code> for two coefficient lists of the same length n, in Z<sub>q</sub>[x]/(x<sup>n</sup> + 1). Coefficient i is the constant term for x<sup>i</sup>. Remember x<sup>n</sup> = &minus;1, so a product term that reaches degree n or more wraps round with a minus sign. Return a list with values from 0 to q &minus; 1.</p>',
         '''
def ring_mul(a, b, q):
    # your code here
    pass
''', [('ring_mul([0, 1, 0, 0], [0, 0, 0, 1], 3329)', [3328, 0, 0, 0]), ('ring_mul([1, 2], [3, 4], 17)', [12, 10]), ('ring_mul([1, 0, 0, 0], [5, 6, 7, 8], 97)', [5, 6, 7, 8])],
         '''
def ring_mul(a, b, q):
    n = len(a)
    out = [0] * n
    for i in range(n):
        for j in range(n):
            if i + j < n:
                out[i + j] = (out[i + j] + a[i] * b[j]) % q
            else:
                out[i + j - n] = (out[i + j - n] - a[i] * b[j]) % q
    return out
''', 'Use a double loop over i and j. If i + j is below n add the product, otherwise subtract it at position i + j &minus; n.', '<p>(1 + 2x)(3 + 4x) = 3 + 10x + 8x<sup>2</sup>, and x<sup>2</sup> = &minus;1 here, so the result is (3 &minus; 8) + 10x = &minus;5 + 10x &equiv; 12 + 10x (mod 17). Real ML-KEM does this with the number theoretic transform in O(n log n).</p>')

K.must('Threat', 'Shor breaks RSA, DH, ECC. Grover halves symmetric bits: AES-256. Harvest now, decrypt later. Mosca: x + y &gt; z.')
K.must('Shor', 'Period r of a<sup>x</sup> mod N, then gcd(a<sup>r/2</sup> &plusmn; 1, N). 15, a = 7: r = 4, 3 and 5.')
K.must('LWE', 'b = As + e mod q. Noise is the security. Decode near 0 or q/2 while |noise| &lt; q/4. Module LWE in Z<sub>q</sub>[x]/(x<sup>n</sup> + 1).')
K.must('ML-KEM', 'FIPS 203, q = 3329, n = 256, k = 2/3/4. 768: pk 1184, ct 1088, K 32 bytes. FO transform. Hybrid X25519MLKEM768.')
K.must('Signatures', 'ML-DSA (FIPS 204, 2.4 to 4.6 KB), SLH-DSA (FIPS 205, hash only), FN-DSA (Falcon), LMS/XMSS stateful. Lamport signs once.')
K.must('Migration', 'Inventory, crypto agility, key exchange first. Rainbow and SIKE broke in 2022. CNSA 2.0 about 2033, IR 8547 draft 2035.')

T = K.topic(
    slug='cy-pqc', topic='cy-pqc', step=(3, 'Applied and modern cryptography', 'cy-c3', 'Certificates and TLS 1.3, the move to post quantum cryptography, and advanced tools: secret sharing, zero knowledge proofs and homomorphic encryption.', 'Advanced'),
    title='Post quantum cryptography: Shor, lattices, ML-KEM and ML-DSA', short='Post quantum', badge='1.2', minutes=85,
    lead='Why quantum computers threaten today’s public keys and what replaces them: Shor’s period finding with worked numbers, Grover and key sizes, Mosca’s inequality, lattices and Learning With Errors, a baby ML-KEM in Python, the FIPS 203, 204 and 205 standards with their sizes, Lamport and hash based signatures, broken candidates, hybrids and a migration plan.',
    desc='post quantum cryptography, PQC, quantum computer, Shor algorithm, period finding, quantum Fourier transform, Grover algorithm, harvest now decrypt later, Mosca inequality, lattice, Learning With Errors, LWE, Regev, ring LWE, module LWE, ML-KEM, Kyber, FIPS 203, key encapsulation, Fujisaki-Okamoto, X25519MLKEM768, ML-DSA, Dilithium, FIPS 204, SLH-DSA, SPHINCS+, FIPS 205, FN-DSA, Falcon, Lamport signature, XMSS, LMS, Rainbow, SIKE, HQC, Classic McEliece, CNSA 2.0, crypto agility, QKD',
    summary='the quantum threat, Shor and Grover, LWE, ML-KEM, ML-DSA and SLH-DSA, hash based signatures, hybrids and migration.',
    keywords=['post quantum', 'Shor', 'Grover', 'LWE', 'ML-KEM', 'ML-DSA', 'SLH-DSA', 'Lamport', 'hybrid', 'migration'],
    recap='<p>Quantum computers would break the maths, not the idea. New hard problems, lattices and hashes, take over, starting with hybrid key exchange today.</p>',
    added='2026-11-14')
