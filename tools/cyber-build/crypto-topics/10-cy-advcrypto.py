# Cryptography 3.3: secret sharing, commitments, zero knowledge proofs, homomorphic encryption and secure multiparty
# computation. Checked against Shamir (1979), Blakley (1979), Pedersen (1991), Goldwasser, Micali and Rackoff (1985),
# Quisquater et al. (1989), Schnorr (1989), Fiat and Shamir (1986), Parno et al. (Pinocchio, 2013), Groth (2016),
# Ben-Sasson et al. (STARKs, 2018), Paillier (1999), Gentry (2009), Yao (1982, 1986), Goldreich, Micali and Wigderson
# (1987), Bogetoft et al. (sugar beet auction, 2009), RFC 9591 (FROST) and Bonawitz et al. (secure aggregation, 2017).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-advcrypto')
K = Kit()

K.code('shamir', r'''
# Shamir secret sharing (1979): any 3 of 5 shares rebuild the secret, 2 shares reveal nothing
import secrets

P = 2 ** 127 - 1                         # a prime. All arithmetic is mod P.

def split(secret, k, n):
    coeffs = [secret] + [secrets.randbelow(P) for i in range(k - 1)]   # f(0) = secret, degree k - 1
    shares = []
    for x in range(1, n + 1):
        y = 0
        for c in reversed(coeffs):       # Horner's rule for f(x)
            y = (y * x + c) % P
        shares.append((x, y))
    return shares

def rebuild(shares):                     # Lagrange interpolation at x = 0
    total = 0
    for i, (xi, yi) in enumerate(shares):
        num, den = 1, 1
        for j, (xj, yj) in enumerate(shares):
            if i != j:
                num = num * (-xj) % P
                den = den * (xi - xj) % P
        total = (total + yi * num * pow(den, -1, P)) % P
    return total

secret = int.from_bytes(b"vault code 7391", "big")
shares = split(secret, k=3, n=5)
print("5 shares made, any 3 rebuild the secret")
for pick in ([0, 1, 2], [1, 3, 4], [0, 2, 4]):
    got = rebuild([shares[i] for i in pick])
    print("shares", [shares[i][0] for i in pick], "->", got.to_bytes(15, "big"))
wrong = rebuild(shares[:2])
print("only 2 shares give a random looking number:", wrong == secret, "| value starts", str(wrong)[:12])
''', long=True)

K.code('commit', r'''
# Commitments: lock in a value now, reveal it later, and prove you did not change it
import hashlib
import secrets

def commit(value):
    salt = secrets.token_bytes(16)       # the salt hides small value sets (yes or no, 1 to 100)
    return hashlib.sha256(salt + value).hexdigest(), salt

def check(commitment, salt, value):
    return hashlib.sha256(salt + value).hexdigest() == commitment

c, salt = commit(b"my bid: 4200")
print("published commitment:", c[:24], "...")
print("honest reveal accepted:", check(c, salt, b"my bid: 4200"))
print("changed bid accepted:  ", check(c, salt, b"my bid: 3900"))

# Pedersen commitment: C = g^m * h^r mod p. Hiding for everyone, binding unless log_g(h) is known.
p = 1099511628443                        # toy safe prime from the Diffie-Hellman chapter
q = (p - 1) // 2
g, h = 4, 9                              # two generators of the order q subgroup, log_g(h) unknown to the committer
m1, r1 = 20, secrets.randbelow(q)
m2, r2 = 22, secrets.randbelow(q)
C1 = pow(g, m1, p) * pow(h, r1, p) % p
C2 = pow(g, m2, p) * pow(h, r2, p) % p
C_sum = C1 * C2 % p                      # commitments can be added without opening them
print("product of commitments opens to 42:", C_sum == pow(g, 42, p) * pow(h, (r1 + r2) % q, p) % p)
''', long=True)

K.code('schnorr_zkp', r'''
# Schnorr's zero knowledge proof: prove you know x with y = g^x, without revealing x
import hashlib
import secrets

p = 1099511628443                        # toy safe prime p = 2q + 1 (41 bits). Real systems use 256 bit curves.
q = (p - 1) // 2
g = 4                                    # generator of the subgroup of prime order q

x = secrets.randbelow(q)                 # the prover's secret, for example a password derived key
y = pow(g, x, p)                         # public

def one_round(knows_x):
    if knows_x:
        r = secrets.randbelow(q)
        t = pow(g, r, p)                 # 1. commitment
        c = secrets.randbelow(q)         # 2. verifier's random challenge
        s = (r + c * x) % q              # 3. response
    else:                                # a cheater guesses the challenge in advance
        guess = secrets.randbelow(q)
        s = secrets.randbelow(q)
        t = pow(g, s, p) * pow(y, -guess, p) % p
        c = secrets.randbelow(q)         # the real challenge is almost never the guess
    return pow(g, s, p) == t * pow(y, c, p) % p          # check g^s = t * y^c

print("honest prover, 20 rounds accepted:", all(one_round(True) for i in range(20)))
print("cheater, 20 rounds accepted:      ", all(one_round(False) for i in range(20)))

# Fiat-Shamir: replace the verifier's challenge by a hash, giving a non interactive proof (a signature)
def prove(message):
    r = secrets.randbelow(q)
    t = pow(g, r, p)
    c = int.from_bytes(hashlib.sha256(f"{t},{y},{message}".encode()).digest(), "big") % q
    return t, (r + c * x) % q

def verify(message, t, s):
    c = int.from_bytes(hashlib.sha256(f"{t},{y},{message}".encode()).digest(), "big") % q
    return pow(g, s, p) == t * pow(y, c, p) % p

t, s = prove("login at 10:42")
print("non interactive proof valid:", verify("login at 10:42", t, s), "| reused for another message:", verify("login at 23:59", t, s))
''', long=True)

K.code('paillier', r'''
# Paillier encryption (1999): add numbers while they stay encrypted
import random
from math import gcd, lcm

rng = random.Random(5)                   # repeatable demo. Real keys use the secrets module and 2048 bit n.

def is_prime(n):
    if n < 2 or n % 2 == 0:
        return n == 2
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

def prime(bits):
    while True:
        c = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(c):
            return c

p, q = prime(256), prime(256)
n = p * q
n2 = n * n
g = n + 1                                # the standard simple choice
lam = lcm(p - 1, q - 1)
mu = pow(lam, -1, n)                     # works because g = n + 1

def encrypt(m):
    r = rng.randrange(1, n)
    while gcd(r, n) != 1:
        r = rng.randrange(1, n)
    return pow(g, m, n2) * pow(r, n, n2) % n2

def decrypt(c):
    L = (pow(c, lam, n2) - 1) // n
    return L * mu % n

salaries = [52000, 61000, 48500, 70500]
encrypted = [encrypt(s) for s in salaries]
total = 1
for c in encrypted:
    total = total * c % n2               # multiplying ciphertexts ADDS the hidden numbers
print("sum computed on encrypted data:", decrypt(total), "| real sum:", sum(salaries))
print("times 3 without decrypting:", decrypt(pow(encrypted[0], 3, n2)), "=", 3 * salaries[0])
print("same salary encrypts differently:", encrypt(52000) != encrypt(52000))
''', long=True)

K.code('mpc_sum', r'''
# Secure multiparty computation: three hospitals learn their total patient count, but no single count
import secrets

M = 2 ** 61 - 1                          # all shares live mod a large prime
counts = {"Asha Hospital": 1840, "Bose Clinic": 975, "City Care": 2310}

def share(value, parties):
    parts = [secrets.randbelow(M) for i in range(parties - 1)]
    parts.append((value - sum(parts)) % M)   # the parts add up to value mod M
    return parts

names = list(counts)
received = {name: [] for name in names}
for owner, value in counts.items():
    for name, part in zip(names, share(value, len(names))):
        received[name].append(part)       # each hospital gets one random looking part from everyone

print("what City Care receives (random looking):", [str(v)[:8] + "..." for v in received["City Care"]])
partial = {name: sum(parts) % M for name, parts in received.items()}
total = sum(partial.values()) % M
print("published partial sums reveal nothing alone. Total:", total, "| check:", sum(counts.values()))

# The same idea powers secure aggregation in federated learning: masks that cancel in the sum
mask = secrets.randbelow(M)
update_a, update_b = 7, 12               # two phones' model updates (as integers)
sent_a, sent_b = (update_a + mask) % M, (update_b - mask) % M
print("server sees", str(sent_a)[:8] + "...", "and", str(sent_b)[:8] + "...", "but the sum is", (sent_a + sent_b) % M)
''', long=True)

K.lesson('idea', 'Cryptography beyond encryption', f'''
{talk('So far cryptography has done two jobs: keeping messages secret and proving who sent them. Since the late 1970s researchers have built tools for harder jobs, where people who do not fully trust each other still need to work together. Adi Shamir showed in 1979 how to split a secret into pieces so that only a group can rebuild it. Shafi Goldwasser, Silvio Micali and Charles Rackoff showed in 1985 that you can convince someone a statement is true without telling them anything else, and Goldwasser and Micali later received the Turing Award partly for this work. Andrew Yao asked in 1982 how two millionaires could find out who is richer without revealing their wealth, which started secure multiparty computation. In 2009 Craig Gentry built the first fully homomorphic encryption, which lets a server compute on data it cannot read. For decades these ideas were too slow for real use. Today they protect cryptocurrency wallets, private contact discovery, census style statistics, password breach checks and federated learning on phones. This chapter explains each tool with small numbers you can check by hand and Python programs that run them.')}
{src('Shamir, How to Share a Secret (1979), Blakley (1979), Pedersen (CRYPTO 1991), Goldwasser, Micali and Rackoff (STOC 1985), Quisquater et al., How to Explain Zero Knowledge Protocols to Your Children (1989), Schnorr (1989), Fiat and Shamir (1986), Parno et al., Pinocchio (2013), Groth (2016), Ben-Sasson et al. (2018), Paillier (EUROCRYPT 1999), Gentry (STOC 2009), Yao (1982, 1986), GMW (1987), Bogetoft et al. (2009), RFC 9591, Bonawitz et al. (CCS 2017).')}
{wwh('<b>Advanced cryptographic tools</b> let several parties hold, check or compute on secrets without any one of them seeing everything: secret sharing, commitments, zero knowledge proofs, homomorphic encryption and secure multiparty computation (MPC).',
     'Real systems often need trust spread across people or machines: no single admin should hold the master key, a server should add votes without seeing them, a user should prove age without showing a birth date.',
     'Each tool rests on maths you already know: polynomials over a prime field, discrete logarithms and modular arithmetic from the RSA and Diffie-Hellman chapters.')}
{table(['Tool', 'The question it answers', 'A real use'], [
    ['Secret sharing', 'How can a group hold a key so that no small subset can use it?', 'Splitting a root key among 5 officers, any 3 can act'],
    ['Commitment', 'How do I lock in a choice now and reveal it later?', 'Sealed bid auctions, coin flipping over the phone'],
    ['Zero knowledge proof', 'How do I prove I know a secret without showing it?', 'Zcash private payments, proving an age range'],
    ['Homomorphic encryption', 'How can a server compute on data it cannot read?', 'Encrypted voting tallies, private lookups on Apple devices'],
    ['Secure multiparty computation', 'How can several parties compute a joint result without sharing inputs?', 'Sugar beet auction, wage gap study, threshold wallets']])}
''', kw=['advanced cryptography', 'secret sharing', 'commitment', 'zero knowledge', 'homomorphic encryption', 'multiparty computation', 'MPC', 'Yao millionaires'])

K.lesson('shamir', 'Shamir secret sharing', f'''
{talk('Shamir secret sharing uses one fact from school algebra: two points fix a line, three points fix a parabola, and in general k points fix a polynomial of degree k minus 1. To share a secret, put it as the constant term of a random polynomial of degree k minus 1, then hand out points on the curve, one per person. Any k people can join their points and rebuild the polynomial with Lagrange interpolation, then read off the value at x equals 0, which is the secret. Fewer than k people learn nothing at all, because for every possible secret there is exactly one polynomial that passes through their points and that secret. This is called information theoretic security: it holds even against an attacker with unlimited computing power, quantum or not. All the arithmetic is done modulo a prime, so the numbers never grow and no information leaks through sizes. George Blakley published a scheme with the same goal in the same year using intersecting planes. Shamir sharing protects the root keys of certificate authorities and DNSSEC, where several key holders must meet, and it is the base of threshold signatures such as FROST, published as RFC 9591 in 2024.')}
{viz('cyshamir')}
{run('shamir')}
{wwh('<b>A (k, n) threshold scheme</b> splits a secret s into n shares so that any k shares rebuild s and any k &minus; 1 shares reveal nothing about it.',
     'It removes the single point of failure of one key holder, and also the single point of theft. Losing up to n &minus; k shares is still safe.',
     'Pick f(x) = s + a<sub>1</sub>x + &hellip; + a<sub>k&minus;1</sub>x<sup>k&minus;1</sup> mod p with random a<sub>i</sub>. Share i is (i, f(i)). Rebuild with Lagrange interpolation at x = 0.')}
{fxs(fx('Sharing polynomial', 'f(x) = s + a<sub>1</sub>x + a<sub>2</sub>x<sup>2</sup> + &hellip; + a<sub>k&minus;1</sub>x<sup>k&minus;1</sup> (mod p)', 'Toy: s = 7, f(x) = 7 + 3x + 2x<sup>2</sup> mod 11 gives shares (1, 1), (2, 10), (3, 1), (4, 7), (5, 6).', key=True),
     fx('Lagrange at zero', 's = f(0) = &sum;<sub>i</sub> y<sub>i</sub> &prod;<sub>j&ne;i</sub> x<sub>j</sub> / (x<sub>j</sub> &minus; x<sub>i</sub>) (mod p)', 'Two shares (1, 5) and (2, 9) of a line mod 11: s = 5 &middot; 2/1 + 9 &middot; 1/(&minus;1) = 10 &minus; 9 = 1.', key=True),
     fx('Perfect secrecy', 'for k &minus; 1 shares, every s in Z<sub>p</sub> is equally likely', 'Each candidate s fixes one polynomial through the known points, so the shares give no hint.'))}
{deep('Why Lagrange interpolation works', '<p>For each share i build the basis polynomial &ell;<sub>i</sub>(x) = &prod;<sub>j&ne;i</sub> (x &minus; x<sub>j</sub>) / (x<sub>i</sub> &minus; x<sub>j</sub>). It equals 1 at x<sub>i</sub> and 0 at every other x<sub>j</sub>. Then f(x) = &sum; y<sub>i</sub> &ell;<sub>i</sub>(x) passes through all k points and has degree k &minus; 1, so by uniqueness it is the sharing polynomial. Putting x = 0 gives the formula above. Division means multiplying by a modular inverse, which exists because p is prime. Shamir sharing is also linear: adding two people&rsquo;s shares point by point gives shares of the sum of the secrets, which MPC protocols use heavily.</p>')}
{note('Plain Shamir sharing trusts the dealer and the share holders to be honest. A cheating holder can hand in a wrong share and change the rebuilt secret. Verifiable secret sharing (Feldman 1987, Pedersen 1991) publishes commitments to the coefficients so every share can be checked.', 'warn')}
''', kw=['Shamir secret sharing', 'threshold scheme', 'Lagrange interpolation', 'Blakley', 'information theoretic security', 'verifiable secret sharing', 'Feldman', 'FROST', 'RFC 9591', 'DNSSEC root key'])

K.lesson('commit', 'Commitments: lock now, reveal later', f'''
{talk('A commitment is the digital version of writing a choice on paper, sealing it in an envelope and putting it on the table. Later you open the envelope and everyone can see you did not change your mind. It needs two properties. Hiding means nobody can read the choice from the sealed envelope. Binding means you cannot open the envelope to a different choice. The easiest commitment is a hash of a random salt followed by the value. The salt matters: without it, a commitment to yes or no, or to a number from 1 to 100, is broken by hashing every possible value. Torben Pedersen proposed in 1991 a commitment built from discrete logarithms: C equals g to the m times h to the r, modulo a prime. It is perfectly hiding, because for any m there is an r that gives the same C, and it is binding as long as nobody knows the discrete log of h to the base g. Pedersen commitments have a useful extra property: multiplying two commitments gives a commitment to the sum of the values. This lets confidential transactions in some cryptocurrencies prove that inputs equal outputs without showing amounts. Commitments are also the first move in most zero knowledge proofs.')}
{run('commit')}
{wwh('<b>A commitment scheme</b> has Commit(m, r) = C and Open(C, m, r) = accept or reject. It must be hiding (C reveals nothing about m) and binding (no one can open C to a different m).',
     'It enforces fairness when moves happen in turn: sealed bids, coin flips over a network, voting, and the first message of a zero knowledge proof.',
     'Hash commitment: C = SHA-256(r &#8214; m) with a fresh random r. Pedersen commitment: C = g<sup>m</sup> h<sup>r</sup> mod p, where log<sub>g</sub> h is unknown.')}
{fxs(fx('Pedersen commitment', 'C = g<sup>m</sup> h<sup>r</sup> (mod p)', 'Toy group of order 11 inside Z<sub>23</sub>: g = 4, h = 9, m = 2, r = 3 gives C = 16 &middot; 16 = 256 &equiv; 3 (mod 23).', key=True),
     fx('Additive property', 'C(m<sub>1</sub>, r<sub>1</sub>) &middot; C(m<sub>2</sub>, r<sub>2</sub>) = C(m<sub>1</sub> + m<sub>2</sub>, r<sub>1</sub> + r<sub>2</sub>)', 'The program commits to 20 and 22 and checks that the product opens to 42.', key=True),
     fx('Why binding holds', 'g<sup>m</sup>h<sup>r</sup> = g<sup>m&prime;</sup>h<sup>r&prime;</sup> gives log<sub>g</sub> h = (m &minus; m&prime;)/(r&prime; &minus; r) mod q', 'Opening two ways would solve a discrete log, which is assumed hard.'))}
{table(['Commitment', 'Hiding', 'Binding', 'Extra'], [
    ['Hash with salt', 'Computational (salt must be random)', 'Computational (collision resistance)', 'Fast, any data'],
    ['Pedersen', 'Perfect, even with unlimited computing', 'Computational (discrete log)', 'Additive, used in ZK proofs'],
    ['Both perfect at once', 'Impossible', 'Impossible', 'One of the two must rest on a hard problem']])}
''', kw=['commitment', 'hiding', 'binding', 'hash commitment', 'salt', 'Pedersen commitment', 'sealed bid', 'coin flipping', 'confidential transactions'])

K.lesson('zkp', 'Zero knowledge proofs', f'''
{talk('A zero knowledge proof lets a prover convince a verifier that a statement is true while revealing nothing beyond that fact. The classic story, told by Jean-Jacques Quisquater and colleagues in 1989, is a cave shaped like a ring with a magic door at the back. Peggy says she knows the password that opens the door. Victor waits outside while she walks down the left or right path. Then he shouts which side she must come out of. If she knows the password she can always obey. If she is bluffing she gets it right only half the time, so after 20 rounds a bluffer survives with chance about one in a million. Victor ends up convinced, yet he learns nothing about the password, and a video of the rounds would not convince anyone else, because Peggy and Victor could have agreed the sides in advance. A proof must have three properties: completeness, where an honest prover always passes, soundness, where a cheater almost always fails, and zero knowledge, where the verifier could have produced the same transcript alone. Claus Schnorr gave in 1989 a short proof that you know x with y equal to g to the x. Fiat and Shamir showed in 1986 how to replace the verifier by a hash, which turns the proof into a digital signature. Modern succinct proofs, called SNARKs and STARKs, prove that a whole program ran correctly with a proof of a few hundred bytes to a few hundred kilobytes.')}
{viz('cyzkp')}
{run('schnorr_zkp')}
{steps('Schnorr identification, one round', [
    'Commit: the prover picks a random r, sends t = g<sup>r</sup> mod p.',
    'Challenge: the verifier sends a random c.',
    'Respond: the prover sends s = r + c x mod q.',
    'Check: the verifier accepts if g<sup>s</sup> = t &middot; y<sup>c</sup> mod p, which holds because g<sup>r + cx</sup> = g<sup>r</sup>(g<sup>x</sup>)<sup>c</sup>.'])}
{fxs(fx('Schnorr check', 'g<sup>s</sup> &equiv; t &middot; y<sup>c</sup> (mod p), with s = r + cx mod q', 'Toy p = 23, q = 11, g = 4, x = 7, y = 8. r = 3, c = 5: t = 18, s = 38 mod 11 = 5, g<sup>5</sup> = 12 and 18 &middot; 8<sup>5</sup> = 18 &middot; 16 = 288 &equiv; 12.', key=True),
     fx('Soundness error', 'Pr[cheater passes n rounds] = (1/|C|)<sup>n</sup>', 'Binary challenges: 2<sup>&minus;20</sup> &asymp; one in a million after 20 rounds. With c from a group of size 2<sup>256</sup>, one round is enough.', key=True),
     fx('Fiat-Shamir', 'c = H(t, y, message)', 'The hash plays the verifier. The result is a Schnorr signature, the ancestor of EdDSA.'))}
{deep('Why Schnorr is zero knowledge and sound', '<p><b>Zero knowledge (honest verifier)</b>: a simulator who does not know x picks c and s at random and sets t = g<sup>s</sup> y<sup>&minus;c</sup>. The triple (t, c, s) has exactly the same distribution as a real one, so a transcript teaches nothing. This is exactly the cheater&rsquo;s trick in the program, which only works when the challenge is known before t is sent. <b>Soundness (special soundness)</b>: if a prover can answer two different challenges c and c&prime; for the same t, then s &minus; s&prime; = (c &minus; c&prime;)x, so x = (s &minus; s&prime;)/(c &minus; c&prime;) mod q. A prover who passes often must know x. The same algebra explains why reusing r in ECDSA or Schnorr signatures leaks the private key, the flaw behind the 2010 PlayStation 3 break.</p>')}
{table(['Proof system', 'Year', 'Proof size', 'Setup', 'Used in'], [
    ['Schnorr / Sigma protocols', '1989', 'A few group elements', 'None', 'Signatures, password protocols'],
    ['Groth16 SNARK', '2016', '3 group elements, about 128 to 192 bytes', 'Trusted setup per circuit', 'Zcash (from 2018), many blockchains'],
    ['PLONK', '2019', 'About 0.5 to 1 KB', 'One universal trusted setup', 'Rollups'],
    ['STARK', '2018', 'Tens to hundreds of KB', 'None, hash based, believed quantum safe', 'StarkNet, provable computation'],
    ['Bulletproofs', '2018', 'About 0.7 KB for a 64 bit range', 'None', 'Monero amounts']])}
''', kw=['zero knowledge proof', 'ZKP', 'Ali Baba cave', 'completeness', 'soundness', 'simulator', 'Schnorr identification', 'Sigma protocol', 'Fiat-Shamir', 'SNARK', 'Groth16', 'PLONK', 'STARK', 'Bulletproofs', 'Zcash', 'trusted setup'])

K.lesson('he', 'Homomorphic encryption', f'''
{talk('Homomorphic encryption lets someone compute on encrypted numbers and get an encrypted answer, without ever seeing the numbers. You have met a small version already: textbook RSA is multiplicatively homomorphic, because the product of two ciphertexts decrypts to the product of the messages. Pascal Paillier published in 1999 a scheme that is additively homomorphic, where multiplying ciphertexts adds the hidden numbers. It also has semantic security, because each encryption uses fresh randomness, so the same salary never encrypts to the same ciphertext twice. That makes Paillier a good fit for encrypted voting tallies and for summing values from many parties. For thirty years nobody knew how to support both addition and multiplication without limit, which would let a server run any program on encrypted data. Craig Gentry solved this in 2009 in his Stanford PhD thesis, using lattices. His key idea, bootstrapping, refreshes the noise that grows in a ciphertext after each operation by running the decryption circuit homomorphically. Later schemes, BGV, BFV, CKKS for approximate real numbers and TFHE for fast bit operations, made it practical for some tasks. It is still slow, often thousands to a million times slower than computing on plain data, but Apple used BFV in 2024 for private lookups such as caller ID, and libraries such as Microsoft SEAL and OpenFHE are open source.')}
{viz('cypaillier')}
{run('paillier')}
{wwh('<b>Homomorphic encryption</b>: there are operations &#8853; on ciphertexts and + on plaintexts with Dec(Enc(a) &#8853; Enc(b)) = a + b. Partially homomorphic schemes support one operation, fully homomorphic (FHE) schemes support addition and multiplication any number of times.',
     'It lets you hand data to an untrusted cloud or a counting server and still get useful results, while the data stays encrypted the whole time.',
     'Paillier: c = g<sup>m</sup> r<sup>n</sup> mod n<sup>2</sup>. Multiplying ciphertexts multiplies g powers, which adds exponents. FHE schemes hide messages in lattice noise and add and multiply polynomials.')}
{fxs(fx('Paillier encryption', 'c = g<sup>m</sup> r<sup>n</sup> (mod n<sup>2</sup>), with g = n + 1', 'Toy n = 35 (p = 5, q = 7), n<sup>2</sup> = 1225, g = 36, random r coprime to n.', key=True),
     fx('Paillier decryption', 'm = L(c<sup>&lambda;</sup> mod n<sup>2</sup>) &middot; &mu; (mod n), with L(u) = (u &minus; 1)/n', '&lambda; = lcm(4, 6) = 12, &mu; = &lambda;<sup>&minus;1</sup> mod 35 = 3, because 12 &middot; 3 = 36 &equiv; 1.', key=True),
     fx('Additive homomorphism', 'Enc(a) &middot; Enc(b) = Enc(a + b mod n), and Enc(a)<sup>k</sup> = Enc(k a mod n)', 'Toy: a = 20, b = 22 decrypt to 42 mod 35 = 7. Sums wrap round n, so real keys use a 2048 bit n.', key=True),
     fx('Why g = n + 1 works', '(1 + n)<sup>m</sup> &equiv; 1 + m n (mod n<sup>2</sup>)', 'By the binomial theorem every term with n<sup>2</sup> vanishes, so the message sits in a linear term that L reads off.'))}
{table(['Scheme', 'Type', 'Operations', 'Typical use'], [
    ['Textbook RSA', 'Partial', 'Multiply', 'A teaching example only, unpadded RSA is insecure'],
    ['ElGamal', 'Partial', 'Multiply (or add in the exponent)', 'Helios and other e-voting tallies'],
    ['Paillier (1999)', 'Partial', 'Add, multiply by a known constant', 'Sums, votes, threshold protocols'],
    ['BGV, BFV (2011, 2012)', 'Fully (levelled plus bootstrapping)', 'Exact integer add and multiply', 'Private lookups, Apple Live Caller ID'],
    ['CKKS (2017)', 'Fully, approximate', 'Real number arithmetic', 'Encrypted machine learning inference'],
    ['TFHE (2016)', 'Fully', 'Fast bootstrapped gates and lookups', 'General programs on encrypted bits']])}
''', kw=['homomorphic encryption', 'Paillier', 'additive homomorphism', 'semantic security', 'fully homomorphic encryption', 'FHE', 'Gentry', 'bootstrapping', 'BGV', 'BFV', 'CKKS', 'TFHE', 'Microsoft SEAL', 'OpenFHE', 'ElGamal', 'e-voting'])

K.lesson('mpc', 'Secure multiparty computation', f'''
{talk('Secure multiparty computation, or MPC, lets several parties compute a function of their private inputs and learn only the result. Andrew Yao posed the millionaires problem in 1982 and in 1986 gave garbled circuits, a way for two parties to evaluate any circuit where one party encrypts the gates and the other evaluates them blind, using oblivious transfer to get its input keys. In 1987 Goldreich, Micali and Wigderson showed that any function can be computed securely by any number of parties. The easiest version to understand uses additive secret sharing: each party splits its number into random parts that add up to it, sends one part to each other party, and everyone publishes the sum of what they received. The total comes out right, but each part alone looks random. The first large real use was in Denmark in January 2008, when about 1200 farmers sold sugar beet contracts in an auction run with MPC, so no one, not even the organisers, saw individual bids. In 2015 and later, Boston employers used MPC from Boston University to measure the gender wage gap without revealing any company’s payroll. Today MPC protects keys in cryptocurrency wallets, where threshold signatures such as FROST let several devices sign without the full key ever existing in one place. And Bonawitz and colleagues at Google showed in 2017 how phones can send masked model updates so that the server only learns their sum, which is secure aggregation for federated learning.')}
{run('mpc_sum')}
{wwh('<b>MPC</b>: n parties with inputs x<sub>1</sub>, &hellip;, x<sub>n</sub> compute y = f(x<sub>1</sub>, &hellip;, x<sub>n</sub>) so that each learns y and nothing more than y implies. Security is defined by comparison with an ideal trusted third party.',
     'It replaces the trusted middleman when competitors, hospitals or governments must combine data that law or business keeps private.',
     'Secret share each input, compute on shares (addition is free, multiplication needs interaction such as Beaver triples), and reveal only the output. Two party protocols often use garbled circuits and oblivious transfer instead.')}
{fxs(fx('Additive sharing', 'x = x<sub>1</sub> + x<sub>2</sub> + &hellip; + x<sub>n</sub> (mod M), with x<sub>1</sub> to x<sub>n&minus;1</sub> random', 'Toy M = 101: x = 40 with parts 77 and 15 needs a last part (40 &minus; 77 &minus; 15) mod 101 = 49.', key=True),
     fx('Secure aggregation mask', 'client a sends u<sub>a</sub> + m<sub>ab</sub>, client b sends u<sub>b</sub> &minus; m<sub>ab</sub>', 'The masks cancel in the sum. With n clients there are n(n &minus; 1)/2 pairwise masks, 4950 for 100 clients.', key=True),
     fx('Threat models', 'semi honest (follow the protocol, try to learn more) versus malicious (deviate at will)', 'Malicious security costs more: MACs on shares (SPDZ, 2012) or cut and choose for garbled circuits.'))}
{table(['Deployment', 'Year', 'Technique', 'What stayed private'], [
    ['Danish sugar beet auction', '2008', 'Three party secret sharing', 'About 1200 farmers&rsquo; bids'],
    ['Boston wage gap study', '2015 onwards', 'Secret sharing in a web app', 'Each employer&rsquo;s salaries by gender'],
    ['Private set intersection (Google Password Checkup)', '2019 onwards', 'PSI, oblivious PRFs', 'Contact lists, leaked password checks'],
    ['Threshold wallets (FROST, RFC 9591)', '2024', 'Shamir shares plus Schnorr', 'The full private key never exists'],
    ['Federated learning secure aggregation', '2017', 'Pairwise masks plus Shamir for dropouts', 'Each phone&rsquo;s model update']])}
{note('The Federated Learning chapter in the Advanced section builds on this: FedAvg, secure aggregation with dropouts, differential privacy noise and attacks such as gradient inversion and poisoning.', 'tip')}
''', kw=['secure multiparty computation', 'MPC', 'Yao', 'garbled circuits', 'oblivious transfer', 'GMW', 'additive secret sharing', 'Beaver triples', 'SPDZ', 'semi honest', 'malicious', 'sugar beet auction', 'wage gap', 'private set intersection', 'PSI', 'threshold signatures', 'FROST', 'secure aggregation', 'federated learning'])

K.lesson('versus', 'The privacy tools compared', f'''
{talk('These tools overlap, so choosing between them is a common exam and interview question. Secret sharing is the cheapest and protects data at rest across holders, but someone must rebuild the secret to use it, unless it is combined with MPC. Homomorphic encryption needs only one server and no interaction, but it is the slowest, and the key holder can decrypt everything. MPC is faster than FHE for many tasks but needs several parties online who are trusted not to all collude. Zero knowledge proofs do not compute on hidden data for someone else. They prove that a computation on your own hidden data was correct. Trusted execution environments such as Intel SGX and AMD SEV take a hardware route instead of maths, which is fast but depends on the chip vendor and has suffered side channel attacks such as Foreshadow in 2018. Many real systems combine tools: federated learning uses MPC style masks plus differential privacy, and private payment systems combine commitments with zero knowledge proofs.')}
{versus('Cryptographic privacy tools', ['', 'Secret sharing', 'Commitment', 'Zero knowledge proof', 'Homomorphic encryption', 'MPC'], [
    ['Goal', 'Split a secret among holders', 'Lock a value, reveal later', 'Prove a fact about a secret', 'Compute on encrypted data', 'Compute jointly on private inputs'],
    ['Parties', 'Dealer and n holders', 'Committer and verifier', 'Prover and verifier', 'Client and one server', 'Two or more'],
    ['Assumption', 'None (information theoretic)', 'Hash or discrete log', 'Discrete log, pairings or hashes', 'Factoring (Paillier) or lattices (FHE)', 'Honest majority or OT and encryption'],
    ['Speed', 'Very fast', 'Very fast', 'Fast to verify, slow to prove for big programs', 'Slowest, 10<sup>3</sup> to 10<sup>6</sup> times', 'Moderate, network bound'],
    ['Example', 'Root key ceremonies', 'Sealed bids', 'Zcash, age proofs', 'Apple Live Caller ID', 'Sugar beet auction, wallets']],
    'Use secret sharing for keys, commitments and ZK proofs for verifiable claims, HE when one untrusted server must compute alone, and MPC when several parties hold the data.')}
''', kw=['comparison', 'trusted execution environment', 'SGX', 'SEV', 'Foreshadow', 'differential privacy'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('These topics run from puzzles a child can follow to some of the most active research in computer science. A beginner can explain the cave story, splitting a password among friends and the idea of adding numbers while they stay locked. A college student can share and rebuild a secret by Lagrange interpolation, run a Schnorr proof and its Fiat-Shamir version, check Paillier’s algebra and sum numbers with additive shares. A masters student studies formal definitions with simulators, special soundness and rewinding, verifiable secret sharing, oblivious transfer and garbled circuits, Beaver triples, SNARK arithmetisation with R1CS and polynomial commitments, and FHE noise growth and bootstrapping. Research covers faster provers, post quantum zero knowledge, FHE hardware accelerators, maliciously secure MPC at scale and the composition of these tools with differential privacy.')}
{ladder(
    '<p>A group can share a secret so that only enough members together can open it. You can prove you know something without showing it. Some encryption lets a computer add numbers it cannot read.</p>',
    '<p>Shamir sharing and Lagrange interpolation mod p, hash and Pedersen commitments, Schnorr rounds and Fiat-Shamir, Paillier encryption and its additive property, additive shares and masked sums.</p>',
    '<p>Simulation based definitions, special soundness and rewinding, Feldman and Pedersen VSS, OT and garbled circuits, Beaver triples and SPDZ, R1CS, QAP and KZG commitments, FHE noise budgets and bootstrapping.</p>',
    '<p>Prover efficiency (folding schemes, lookup arguments), lattice and hash based post quantum ZK, FHE accelerators, MPC with dishonest majorities at scale, and combining MPC, HE and differential privacy in federated learning.</p>')}
{grow('Explain what each tool is for with one everyday example.',
      'Run and check the toy programs and do the maths by hand.',
      'Reason about security definitions, costs and how to combine the tools.')}
''', kw=['beginner', 'expert', 'simulation', 'rewinding', 'R1CS', 'QAP', 'KZG', 'folding schemes', 'noise budget'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Shamir</b> (1979): secret s = f(0) of a random degree k &minus; 1 polynomial mod p. Any k shares rebuild by Lagrange, k &minus; 1 reveal nothing.',
    '<b>Commitments</b>: hiding and binding. Hash with salt, or Pedersen C = g<sup>m</sup>h<sup>r</sup>, which is perfectly hiding and additive.',
    '<b>Zero knowledge</b> (GMR 1985): completeness, soundness, zero knowledge. Cave story, cheater passes n binary rounds with 2<sup>&minus;n</sup>.',
    '<b>Schnorr</b>: t = g<sup>r</sup>, challenge c, s = r + cx, check g<sup>s</sup> = t y<sup>c</sup>. Fiat-Shamir hashes the challenge and gives a signature.',
    '<b>SNARKs and STARKs</b>: Groth16 about 128 to 192 bytes with trusted setup, STARKs larger but hash based and transparent.',
    '<b>Paillier</b> (1999): c = g<sup>m</sup>r<sup>n</sup> mod n<sup>2</sup>. Multiplying ciphertexts adds plaintexts. Gentry (2009) gave FHE with bootstrapping.',
    '<b>MPC</b>: Yao garbled circuits, GMW, additive shares. Sugar beet auction 2008, wage gap study, FROST wallets.',
    '<b>Secure aggregation</b> (Bonawitz et al. 2017): masks that cancel in the sum, the bridge to federated learning.'],
    'This completes the cryptography section. The next section, Network and Systems Security, applies it to networks, operating systems and the cloud.')}
{files('Three tasks: additive shares that sum to a value, Shamir rebuild by Lagrange interpolation, and summing Paillier ciphertexts without decrypting each one.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In a 3 of 5 Shamir scheme, what can 2 share holders learn about the secret?', ['Two thirds of it', 'Nothing at all', 'Its first digit', 'Its length only'], 1, 'Perfect secrecy.', 'Every possible secret fits a degree 2 polynomial through any 2 points, so all secrets stay equally likely.')
K.quiz('e', 'Which two properties must a commitment have?', ['Fast and small', 'Hiding and binding', 'Public and private', 'Signed and dated'], 1, 'Envelope.', 'Hiding keeps the value secret until opening, binding stops you opening it to something else.')
K.quiz('e', 'A zero knowledge proof convinces the verifier that a statement is true and reveals', ['The secret', 'Nothing beyond the truth of the statement', 'Half the secret', 'The prover’s identity'], 1, 'Zero.', 'The verifier could have produced the same transcript alone, so it learns nothing new.')
K.quiz('e', 'Additively homomorphic encryption lets a server', ['Read the data', 'Add encrypted numbers and return an encrypted sum', 'Break the key', 'Compress the data'], 1, 'Paillier.', 'Multiplying Paillier ciphertexts adds the hidden numbers.')
K.quiz('m', 'Why must a hash commitment to "yes" or "no" include a random salt?', ['To make it shorter', 'Without it anyone can hash both options and compare', 'Hashes need salt to run', 'For binding'], 1, 'Small value sets.', 'Hiding fails when the value space can be searched.')
K.quiz('m', 'In the cave story, a bluffer survives 10 rounds with probability', ['1/10', '1/1024', '1/2', '0'], 1, '(1/2)<sup>10</sup>.', 'Each round is a fair guess, so 2<sup>&minus;10</sup> = 1/1024.')
K.quiz('m', 'The Fiat-Shamir transform replaces the verifier’s challenge with', ['A fixed number', 'A hash of the commitment, public key and message', 'The secret key', 'A timestamp'], 1, 'Random oracle.', 'This turns an interactive proof into a non interactive one, a signature when a message is included.')
K.quiz('m', 'Why is Paillier encryption randomised with r<sup>n</sup>?', ['To speed it up', 'So the same message gives different ciphertexts and cannot be matched', 'To add a signature', 'To shrink ciphertexts'], 1, 'Semantic security.', 'Without randomness, equal salaries would be visible as equal ciphertexts.')
K.quiz('m', 'In additive secret sharing over three parties, what does each party receive from the others?', ['Their full inputs', 'One random looking part of each input', 'Their keys', 'Nothing'], 1, 'Parts.', 'Each part alone is uniform. Only the sum of all parts reveals the input.')
K.quiz('h', 'If a Schnorr prover answers two different challenges for the same commitment t, an extractor gets x =', ['s + s&prime;', '(s &minus; s&prime;)/(c &minus; c&prime;) mod q', 'c &middot; c&prime;', 't / y'], 1, 'Special soundness.', 's &minus; s&prime; = (c &minus; c&prime;)x. The same fact leaks keys when a signer reuses a nonce.')
K.quiz('h', 'What did Gentry’s 2009 bootstrapping solve?', ['Key distribution', 'Noise growth that limited how many operations FHE could do', 'Slow RSA', 'Quantum attacks on AES'], 1, 'Refresh.', 'Evaluating decryption homomorphically resets the noise so computation can continue without limit.')
K.quiz('h', 'Why is a Pedersen commitment perfectly hiding?', ['It uses AES', 'For every m there is an r that gives the same C, so C carries no information about m', 'It is very large', 'h is secret'], 1, 'All openings exist.', 'h generates the group, so g<sup>m</sup>h<sup>r</sup> is uniform when r is uniform.')
K.quiz('h', 'What does secure aggregation in federated learning hide from the server?', ['The final model', 'Each client’s individual update, revealing only the sum', 'The number of clients', 'The learning rate'], 1, 'Masks cancel.', 'Bonawitz et al. (2017) use pairwise masks plus Shamir shares to handle clients that drop out.')
K.quiz('x', 'In the style of an MIT 6.875 question: what goes wrong if someone keeps the secret trapdoor from a Groth16 trusted setup?', ['Nothing', 'They can forge proofs of false statements, so soundness fails while zero knowledge still holds', 'All witnesses leak', 'Proofs become larger'], 1, 'Toxic waste.', 'Zero knowledge still holds, but the trapdoor from the setup breaks soundness. Ceremonies use many participants so one honest one suffices.')
K.quiz('x', 'In the style of an IIT Madras cryptography exam: can a commitment scheme be both perfectly hiding and perfectly binding?', ['Yes, Pedersen is', 'No: perfect hiding means other openings exist, and an unbounded committer could find one', 'Yes, with hashes', 'Only with quantum computers'], 1, 'Counting.', 'If C is consistent with every m, binding can only be computational. Pedersen picks perfect hiding, hash commitments are both computational.')

K.calc('e', 'A 3 of 5 Shamir scheme uses a polynomial of what degree?', '2', 'k &minus; 1.', ['k = 3 points fix the polynomial.', 'Degree = 3 &minus; 1.', eq('degree 2')], check=3 - 1)
K.calc('e', 'How many different groups of 3 people from 5 share holders can rebuild the secret?', '10', '5 choose 3.', ['C(5, 3) = 5! / (3! 2!).', '120 / 12 = 10.', eq('10 groups')], check=__import__('math').comb(5, 3))
K.calc('e', 'Binary challenges: a cheater passes n rounds with probability 2<sup>&minus;n</sup>. For n = 10, that is 1 in how many?', '1024', '2<sup>10</sup>.', ['Each round is a coin flip.', '2<sup>10</sup> = 1024.', eq('1 in 1024')], check=2 ** 10)
K.calc('m', 'Shamir toy: f(x) = 7 + 3x + 2x<sup>2</sup> mod 11. What is share f(2)?', '10', 'Evaluate then reduce.', ['7 + 6 + 8 = 21.', '21 mod 11 = 10.', eq('share (2, 10)')], check=(7 + 3 * 2 + 2 * 4) % 11)
K.calc('m', 'A line mod 11 has shares (1, 5) and (2, 9). What is the secret f(0)?', '1', 'Lagrange: y<sub>1</sub> &middot; 2/(2 &minus; 1) + y<sub>2</sub> &middot; 1/(1 &minus; 2).', ['5 &middot; 2 = 10.', '9 &middot; (&minus;1) = &minus;9.', eq('10 &minus; 9 = 1')], check=(5 * 2 - 9) % 11)
K.calc('m', 'Schnorr toy: p = 23, g = 4, secret x = 7. What is the public key y = g<sup>x</sup> mod p?', '8', 'Square and multiply.', ['4<sup>2</sup> = 16, 4<sup>4</sup> = 256 &equiv; 3.', '4<sup>7</sup> = 3 &middot; 16 &middot; 4 = 192 &equiv; 8.', eq('y = 8')], check=pow(4, 7, 23))
K.calc('m', 'Same toy, q = 11. With r = 3 and challenge c = 5, what is the response s = r + c x mod q?', '5', '3 + 35.', ['3 + 5 &middot; 7 = 38.', '38 mod 11 = 5.', eq('s = 5')], check=(3 + 5 * 7) % 11)
K.calc('m', 'Pedersen toy: C = 4<sup>2</sup> &middot; 9<sup>3</sup> mod 23. What is C?', '3', '9<sup>3</sup> = 729.', ['4<sup>2</sup> = 16, 729 mod 23 = 16.', '16 &middot; 16 = 256, 256 mod 23 = 3.', eq('C = 3')], check=pow(4, 2, 23) * pow(9, 3, 23) % 23)
K.calc('h', 'Paillier toy with p = 5, q = 7. What is &lambda; = lcm(p &minus; 1, q &minus; 1)?', '12', 'lcm(4, 6).', ['4 = 2<sup>2</sup>, 6 = 2 &middot; 3.', 'lcm = 2<sup>2</sup> &middot; 3.', eq('&lambda; = 12')], check=__import__('math').lcm(4, 6))
K.calc('h', 'Same toy: n = 35. What is &mu; = &lambda;<sup>&minus;1</sup> mod n?', '3', '12 &middot; &mu; &equiv; 1 (mod 35).', ['12 &middot; 3 = 36.', '36 mod 35 = 1.', eq('&mu; = 3')], check=pow(12, -1, 35))
K.calc('h', 'Same toy: Enc(20) &middot; Enc(22) is decrypted. What number comes out?', '7', 'Sums wrap round n = 35.', ['20 + 22 = 42.', '42 mod 35 = 7.', eq('7, so real n must exceed any possible sum')], check=(20 + 22) % 35)
K.calc('h', 'Additive shares mod 101: secret 40, first two parts 77 and 15. What is the third part?', '49', '(40 &minus; 77 &minus; 15) mod 101.', ['40 &minus; 92 = &minus;52.', '&minus;52 + 101 = 49.', eq('49')], check=(40 - 77 - 15) % 101)
K.calc('x', 'Secure aggregation with pairwise masks: how many masks are needed for 100 clients?', '4950', 'One per pair.', ['n(n &minus; 1)/2.', '100 &middot; 99 / 2 = 4950.', eq('4950 pairs')], check=100 * 99 // 2)
K.calc('x', 'With binary challenges, what is the smallest number of rounds n so a cheater’s chance 2<sup>&minus;n</sup> is below one in a million?', '20', '2<sup>20</sup> = 1048576.', ['2<sup>19</sup> = 524288, still below 10<sup>6</sup>.', '2<sup>20</sup> = 1048576 &gt; 10<sup>6</sup>.', eq('n = 20')], check=next(n for n in range(1, 64) if 2 ** n > 10 ** 6))

K.assign('additive_shares', 'e', 'Finish a set of additive shares',
         '<p>Write <code>finish_shares(value, parts, M)</code>. You are given the random parts for all parties but the last. Return the full list of parts, with the last part chosen so that all parts add up to <code>value</code> modulo <code>M</code>. Every part must be between 0 and M &minus; 1.</p>',
         '''
def finish_shares(value, parts, M):
    # your code here
    pass
''', [('finish_shares(40, [77, 15], 101)', [77, 15, 49]), ('finish_shares(5, [1, 2, 3], 11)', [1, 2, 3, 10]), ('sum(finish_shares(1840, [123456, 98765], 2 ** 61 - 1)) % (2 ** 61 - 1)', 1840)],
         '''
def finish_shares(value, parts, M):
    last = (value - sum(parts)) % M
    return list(parts) + [last]
''', 'The last part is value minus the sum of the others, reduced mod M.', '<p>Python&rsquo;s % always returns a value from 0 to M &minus; 1 for positive M, even when the left side is negative, so &minus;52 % 101 gives 49 directly.</p>')
K.assign('shamir_rebuild', 'm', 'Rebuild a Shamir secret',
         '<p>Write <code>rebuild(shares, P)</code>, where <code>shares</code> is a list of [x, y] pairs on a polynomial mod the prime P. Use Lagrange interpolation at x = 0 and return the secret f(0) from 0 to P &minus; 1. Use <code>pow(d, -1, P)</code> for a modular inverse.</p>',
         '''
def rebuild(shares, P):
    # your code here
    pass
''', [('rebuild([[1, 1], [2, 10], [3, 1]], 11)', 7), ('rebuild([[2, 10], [4, 7], [5, 6]], 11)', 7), ('rebuild([[1, 5], [2, 9]], 11)', 1)],
         '''
def rebuild(shares, P):
    total = 0
    for i, (xi, yi) in enumerate(shares):
        num, den = 1, 1
        for j, (xj, yj) in enumerate(shares):
            if i != j:
                num = num * (-xj) % P
                den = den * (xi - xj) % P
        total = (total + yi * num * pow(den, -1, P)) % P
    return total
''', 'For each share multiply (0 &minus; x<sub>j</sub>) on top and (x<sub>i</sub> &minus; x<sub>j</sub>) below over all other shares, then add y<sub>i</sub> times top times the inverse of below.', '<p>Different groups of 3 shares from f(x) = 7 + 3x + 2x<sup>2</sup> all give 7, which is the threshold property. Two shares of that parabola would give a wrong but valid looking number.</p>')
K.assign('paillier_sum', 'h', 'Sum Paillier ciphertexts',
         '<p>Toy Paillier key: n = 35, g = 36, &lambda; = 12, &mu; = 3. Write <code>paillier_sum(ciphertexts, n, lam, mu)</code> that multiplies all ciphertexts mod n<sup>2</sup> and then decrypts the product with m = L(c<sup>&lambda;</sup> mod n<sup>2</sup>) &middot; &mu; mod n, where L(u) = (u &minus; 1) // n. The ciphertexts 88, 512 and 257 hide 4, 9 and 5.</p>',
         '''
def paillier_sum(ciphertexts, n, lam, mu):
    # your code here
    pass
''', [('paillier_sum([88], 35, 12, 3)', 4), ('paillier_sum([88, 512], 35, 12, 3)', 13), ('paillier_sum([88, 512, 257], 35, 12, 3)', 18)],
         '''
def paillier_sum(ciphertexts, n, lam, mu):
    n2 = n * n
    c = 1
    for x in ciphertexts:
        c = c * x % n2
    L = (pow(c, lam, n2) - 1) // n
    return L * mu % n
''', 'Start with c = 1, multiply in each ciphertext mod n * n, then apply L and multiply by mu mod n.', '<p>The server that multiplies never needs &lambda; or &mu;. Only the key holder decrypts the total, which is how encrypted tallies work. 88 = 36<sup>4</sup> &middot; 2<sup>35</sup> mod 1225, so it encrypts 4 with r = 2.</p>')

K.must('Shamir', 's = f(0), degree k &minus; 1 mod p, share (i, f(i)). Lagrange at 0: &sum; y<sub>i</sub> &prod; x<sub>j</sub>/(x<sub>j</sub> &minus; x<sub>i</sub>). k &minus; 1 shares: nothing. VSS checks shares.')
K.must('Commitments', 'Hiding plus binding. SHA-256(salt &#8214; m). Pedersen g<sup>m</sup>h<sup>r</sup>: perfectly hiding, binding by DL, additive. Never both perfect.')
K.must('Zero knowledge', 'Complete, sound, ZK (simulator). Cave: 2<sup>&minus;n</sup>. Schnorr: t = g<sup>r</sup>, s = r + cx, g<sup>s</sup> = t y<sup>c</sup>. Two answers extract x.')
K.must('Succinct proofs', 'Fiat-Shamir c = H(t, y, m). Groth16 about 128 to 192 bytes, trusted setup. PLONK universal. STARK transparent, hash based. Bulletproofs ranges.')
K.must('Homomorphic', 'Paillier c = g<sup>m</sup>r<sup>n</sup> mod n<sup>2</sup>, g = n + 1, m = L(c<sup>&lambda;</sup>)&mu;. Product adds. Gentry 2009 bootstrapping. BGV, BFV, CKKS, TFHE.')
K.must('MPC', 'Yao 1982 and garbled circuits 1986, GMW 1987, additive shares, Beaver triples, SPDZ. Sugar beet 2008. FROST RFC 9591. Secure aggregation 2017.')

T = K.topic(
    slug='cy-advcrypto', topic='cy-advcrypto', step=(3, 'Applied and modern cryptography', 'cy-c3', 'Certificates and TLS 1.3, the move to post quantum cryptography, and advanced tools: secret sharing, zero knowledge proofs and homomorphic encryption.', 'Advanced'),
    title='Advanced cryptography: secret sharing, zero knowledge, homomorphic encryption and MPC', short='Advanced tools', badge='1.3', minutes=90,
    lead='Cryptography for parties who do not fully trust each other: Shamir secret sharing with Lagrange interpolation, hash and Pedersen commitments, zero knowledge proofs from the cave story to Schnorr, Fiat-Shamir and SNARKs, Paillier homomorphic encryption with worked numbers and the path to FHE, and secure multiparty computation from Yao to secure aggregation for federated learning.',
    desc='advanced cryptography, Shamir secret sharing, threshold scheme, Lagrange interpolation, verifiable secret sharing, commitment scheme, hiding, binding, Pedersen commitment, zero knowledge proof, ZKP, Ali Baba cave, Schnorr identification, Sigma protocol, special soundness, Fiat-Shamir, SNARK, Groth16, PLONK, STARK, Bulletproofs, Zcash, trusted setup, homomorphic encryption, Paillier, fully homomorphic encryption, FHE, Gentry, bootstrapping, BGV, BFV, CKKS, TFHE, secure multiparty computation, MPC, Yao millionaires, garbled circuits, oblivious transfer, GMW, additive secret sharing, Beaver triples, SPDZ, private set intersection, FROST, threshold signatures, secure aggregation, federated learning',
    summary='Shamir secret sharing, commitments, zero knowledge proofs, Paillier and FHE, MPC and secure aggregation.',
    keywords=['secret sharing', 'Shamir', 'commitment', 'Pedersen', 'zero knowledge', 'Schnorr', 'SNARK', 'Paillier', 'FHE', 'MPC'],
    recap='<p>Split, lock, prove and compute without revealing: these tools let parties who do not trust each other still work on secrets together.</p>',
    added='2026-11-15')
