# Cryptography 1.3: hash functions, MACs and password storage. Checked against FIPS 180-4 (SHA-2 and its padding),
# FIPS 202 (SHA-3), RFC 2104 and RFC 4231 (HMAC and its test vectors), RFC 6962 (Merkle trees in Certificate
# Transparency), RFC 9106 (Argon2), RFC 8018 (PBKDF2), the OWASP Password Storage Cheat Sheet, Wang et al. (2005) on
# MD5, Stevens et al. (2017, SHAttered) and Leurent and Peyrin (2020) on SHA-1, and Duong and Rizzo (2009) on the
# Flickr length extension.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-hashing')
K = Kit()

K.code('hash_props', r'''
# Collisions and preimages on SHORT hashes, to see the 2^(n/2) and 2^n rules in action
import hashlib

def short_hash(text, bits):              # keep only the first bits of SHA-256
    full = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    return full >> (256 - bits)

# Collision: any two different messages with the same 24 bit hash
seen = {}
i = 0
while True:
    msg = "text " + str(i)
    h = short_hash(msg, 24)
    if h in seen:
        print("24 bit collision after", i + 1, "tries:", repr(seen[h]), "and", repr(msg))
        break
    seen[h] = msg
    i = i + 1
print("birthday rule predicts about", round(1.1774 * 2 ** 12), "tries")

# Preimage: a message whose 16 bit hash equals a GIVEN target
target = short_hash("hello", 16)
j = 0
while short_hash("guess " + str(j), 16) != target:
    j = j + 1
print("16 bit preimage after", j + 1, "tries, the rule predicts about", 2 ** 16)
print("single runs vary a lot: the rules give the average over many runs")
''', long=True)

K.code('length_extension', r'''
# The length extension attack on SHA-256(secret + message), with SHA-256 written out in full
import hashlib
import struct

K = []
H0 = []

def is_prime(n):
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True

def frac_bits(x):                        # first 32 bits of the fractional part
    return int((x - int(x)) * 2 ** 32)

n = 2
while len(K) < 64:                       # constants from square and cube roots of primes (FIPS 180-4)
    if is_prime(n):
        if len(H0) < 8:
            H0.append(frac_bits(n ** 0.5))
        K.append(frac_bits(n ** (1 / 3)))
    n = n + 1

def rotr(x, r):
    return ((x >> r) | (x << (32 - r))) & 0xFFFFFFFF

def compress(state, block):              # one 64 byte block updates the 8 word state
    w = list(struct.unpack(">16I", block))
    for i in range(16, 64):
        s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w.append((w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF)
    a, b, c, d, e, f, g, h = state
    for i in range(64):
        t1 = (h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i]) & 0xFFFFFFFF
        t2 = ((rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & 0xFFFFFFFF
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xFFFFFFFF, c, b, a, (t1 + t2) & 0xFFFFFFFF
    return [(x + y) & 0xFFFFFFFF for x, y in zip(state, [a, b, c, d, e, f, g, h])]

def padding(length):                     # 0x80, zeros, then the length in bits as 8 bytes
    zeros = (55 - length) % 64
    return b"\x80" + b"\x00" * zeros + struct.pack(">Q", length * 8)

def sha256(data, state=None, done=0):
    if state is None:
        state = H0
    data = data + padding(done + len(data))
    for i in range(0, len(data), 64):
        state = compress(state, data[i:i + 64])
    return b"".join(struct.pack(">I", x) for x in state)

print("our SHA-256 matches hashlib:", sha256(b"abc").hex() == hashlib.sha256(b"abc").hexdigest())

# The server signs with SHA-256(secret + message). The attacker sees message and tag, never the secret.
secret = b"k3y-only-server-knows"
message = b"user=riya&role=reader"
tag = hashlib.sha256(secret + message).digest()

guess = 21                               # the attacker tries secret lengths until one works
glue = padding(guess + len(message))
extra = b"&role=admin"
state = list(struct.unpack(">8I", tag))  # the tag IS the internal state after the last block
forged_tag = sha256(extra, state, guess + len(message) + len(glue))
forged_message = message + glue + extra

print("forged message:", forged_message)
print("server accepts the forged tag:", hashlib.sha256(secret + forged_message).digest() == forged_tag)
''', long=True)

K.code('hmac_demo', r'''
# HMAC built by hand, compared with Python's hmac module
import hashlib
import hmac

def my_hmac(key, message):
    if len(key) > 64:
        key = hashlib.sha256(key).digest()       # long keys are hashed first
    key = key + bytes(64 - len(key))             # pad to the 64 byte block size
    inner_key = bytes(b ^ 0x36 for b in key)     # ipad
    outer_key = bytes(b ^ 0x5C for b in key)     # opad
    inner = hashlib.sha256(inner_key + message).digest()
    return hashlib.sha256(outer_key + inner).hexdigest()

key = b"shared secret"
msg = b"PAY RIYA 100"
print("by hand :", my_hmac(key, msg))
print("library :", hmac.new(key, msg, hashlib.sha256).hexdigest())

# RFC 4231 test case 2
print("RFC 4231:", my_hmac(b"Jefe", b"what do ya want for nothing?"))

# The receiver checks a tag in constant time
received = hmac.new(key, msg, hashlib.sha256).hexdigest()
print("genuine :", hmac.compare_digest(received, my_hmac(key, msg)))
print("changed :", hmac.compare_digest(received, my_hmac(key, b"PAY RIYA 900")))
''', long=True)

K.code('passwords', r'''
# Storing passwords: why fast hashes fail, and the right way with a salt and a slow function
import hashlib
import hmac
import os
import time

# 1. A leaked table of unsalted MD5 hashes, and a dictionary attack
leaked = {"riya": hashlib.md5(b"sunshine").hexdigest(), "amit": hashlib.md5(b"Tr0ub4dor&3").hexdigest()}
wordlist = ["123456", "password", "qwerty", "sunshine", "iloveyou"]
for user in leaked:
    for word in wordlist:
        if hashlib.md5(word.encode()).hexdigest() == leaked[user]:
            print(user, "cracked:", word)

# 2. The right way: a random salt per user and a slow, memory hard function
def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1)   # OWASP suggests n=2**17
    return salt, digest

def check_password(password, salt, digest):
    test = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1)
    return hmac.compare_digest(test, digest)

salt, digest = hash_password("sunshine")
print("right password:", check_password("sunshine", salt, digest))
print("wrong password:", check_password("Sunshine", salt, digest))

salt2, digest2 = hash_password("sunshine")
print("two users with the same password get the same hash:", digest == digest2)

# 3. The cost per guess: PBKDF2-HMAC-SHA256 with OWASP's 600,000 iterations
start = time.perf_counter()
hashlib.pbkdf2_hmac("sha256", b"sunshine", os.urandom(16), 600_000)
print("one PBKDF2 guess took about", round(time.perf_counter() - start, 2), "seconds")
''')

K.code('merkle', r'''
# A Merkle tree: one short root hash commits to a whole list, and a short proof shows one item is in it
import hashlib

def h(data):
    return hashlib.sha256(data).digest()

def build(items):                         # every level of the tree, leaves first (needs 2, 4, 8, ... items)
    level = [h(x.encode()) for x in items]
    levels = [level]
    while len(level) > 1:
        level = [h(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
        levels.append(level)
    return levels

def proof(levels, index):                 # the sibling hash at every level
    path = []
    for level in levels[:-1]:
        sibling = index ^ 1               # the other node of the pair
        path.append((level[sibling], sibling < index))
        index = index // 2
    return path

def verify(item, path, root):
    value = h(item.encode())
    for sibling, sibling_is_left in path:
        if sibling_is_left:
            value = h(sibling + value)
        else:
            value = h(value + sibling)
    return value == root

items = ["riya pays amit 10", "amit pays dev 5", "dev pays riya 7", "riya pays sam 2"]
levels = build(items)
root = levels[-1][0]
print("root:", root.hex()[:32], "...")

p = proof(levels, 2)
print("proof for item 2 has", len(p), "hashes for", len(items), "items")
print("item 2 is in the tree:", verify(items[2], p, root))
print("a changed item fails :", verify("dev pays riya 70", p, root))
''')

K.lesson('idea', 'Hash functions: a fingerprint for any data', f'''
{talk('A cryptographic hash function is one of the most used tools in all of computing, even though most people never see one. It takes any amount of data, a word or a whole film, and produces a short fixed size value, such as 256 bits for SHA-256. The same input always gives the same output, and the smallest change gives a completely different one. But the real power comes from three hardness properties. Given a hash, you cannot find any input that produces it. Given one input, you cannot find a second input with the same hash. And you cannot find any two inputs with the same hash at all. Ron Rivest’s MD5, from 1991, was the workhorse of the 1990s until Wang Xiaoyun’s team broke its collision resistance in 2004. In 2012 the Flame spy malware used an MD5 collision to forge a Microsoft code signing certificate, so infected computers trusted it as a Windows update. SHA-1 fell in 2017. Today we use SHA-256 and SHA-3. Hashes protect software downloads, Git commits, digital signatures, blockchains and passwords.')}
{src('FIPS 180-4, FIPS 202, RFC 2104, RFC 4231, RFC 6962, RFC 8018, RFC 9106, the OWASP Password Storage Cheat Sheet, Wang et al. (2005), Stevens et al. (2017), Leurent and Peyrin (2020).')}
{wwh('A <b>cryptographic hash function</b> H maps any input to a fixed length output (the digest) and is easy to compute but hard to reverse or to collide.',
     'Hashes let you check that data is unchanged, identify files, sign large documents by signing only their hash, and store passwords without storing the passwords.',
     'Compute <code>hashlib.sha256(data).hexdigest()</code>. Security rests on three properties, each with its own brute force cost for an n bit hash: preimage 2<sup>n</sup>, second preimage 2<sup>n</sup>, collision 2<sup>n/2</sup>.')}
{table(['Property', 'The attacker must find', 'Brute force cost', 'Needed by'], [
    ['Preimage resistance (one way)', 'Any m with H(m) = a given h', '2<sup>n</sup>', 'Password storage, commitments'],
    ['Second preimage resistance', 'm2 &ne; m1 with H(m2) = H(m1), m1 given', '2<sup>n</sup>', 'File integrity, download checks'],
    ['Collision resistance', 'Any pair m1 &ne; m2 with H(m1) = H(m2)', '2<sup>n/2</sup> (birthday)', 'Digital signatures, certificates']])}
{run('hash_props')}
{note('Collision resistance is the first property to fall, because it only costs 2<sup>n/2</sup>. MD5 and SHA-1 lost collision resistance, but nobody has found a practical preimage attack on either. They are still banned for security use, because signatures need collision resistance.', 'exam')}
''', kw=['hash function', 'digest', 'preimage resistance', 'second preimage', 'collision resistance', 'MD5', 'SHA-1', 'SHA-256', 'Flame', 'one way function'])

K.lesson('birthday', 'The birthday paradox and collision maths', f'''
{talk('Here is a puzzle that surprises almost everyone. How many people do you need in a room for a better than even chance that two share a birthday? Most people guess around 180, half of 365. The real answer is 23. The trick is that we are not asking whether someone shares your birthday. We are asking whether any pair shares a birthday, and 23 people form 253 pairs. Each new person has to avoid every birthday already taken, and the chance of avoiding them all shrinks quickly. The same maths applies to hash values. If a hash has n bits, there are 2 to the n possible outputs, but an attacker who hashes many random messages will find two with the same output after only about 2 to the n over 2 tries. That is why a 128 bit hash like MD5 only ever offered 64 bits of collision security, and why we now use 256 bit hashes, which give 128 bits. The same bound limits block ciphers, random IDs and nonces: anything chosen at random from N values starts repeating after about the square root of N.')}
{wwh('The <b>birthday paradox</b>: among n random values from N possibilities, a repeat becomes likely once n is around &radic;N.',
     'It sets the real collision security of a hash (half its length in bits) and how many random nonces, IDs or blocks you can use before repeats appear.',
     'P(no repeat) = (1 &minus; 1/N)(1 &minus; 2/N)...(1 &minus; (n&minus;1)/N) &asymp; e<sup>&minus;n(n&minus;1)/2N</sup>. Set it to 1/2 and solve: n &asymp; &radic;(2 N ln 2) &asymp; 1.18 &radic;N.')}
{viz('cybirthday')}
{fxs(fx('Exact', 'P(collision) = 1 &minus; &prod;<sub>i=1</sub><sup>n&minus;1</sup> (1 &minus; i/N)', 'For N = 365 and n = 23 this is 0.507.', key=True),
     fx('Approximation', 'P(collision) &asymp; 1 &minus; e<sup>&minus;n<sup>2</sup>/2N</sup> &asymp; n<sup>2</sup>/2N when small', 'Uses 1 &minus; x &asymp; e<sup>&minus;x</sup> for small x.', key=True),
     fx('50% point', 'n<sub>1/2</sub> &asymp; &radic;(2 ln 2 &middot; N) &asymp; 1.1774 &radic;N', 'N = 365: 22.5, so 23 people. N = 2<sup>128</sup>: about 2.2 &times; 10<sup>19</sup> hashes.'),
     fx('Hash collision security', 'n bit hash &rarr; about 2<sup>n/2</sup> work', 'MD5: 2<sup>64</sup> at best (and broken far below). SHA-256: 2<sup>128</sup>.'))}
{deep('Deriving the approximation', '<p>Take logs: ln P(no repeat) = &Sigma;<sub>i&lt;n</sub> ln(1 &minus; i/N) &asymp; &minus;&Sigma; i/N = &minus;n(n &minus; 1)/2N, using ln(1 &minus; x) &asymp; &minus;x when x is small. So P(no repeat) &asymp; e<sup>&minus;n(n&minus;1)/2N</sup>. Setting this to 1/2 gives n(n &minus; 1) = 2N ln 2, so n &asymp; &radic;(2N ln 2). Pollard’s rho method finds hash collisions in about the same number of steps while using almost no memory, by walking x &rarr; H(x) until the path loops.</p>')}
''', kw=['birthday paradox', 'birthday attack', 'collision probability', 'square root of N', '23 people', 'Pollard rho', '2^(n/2)'])

K.lesson('md', 'Inside SHA-256: the Merkle-Damgård chain and length extension', f'''
{talk('How can a function take input of any length? In 1989, Ralph Merkle and Ivan Damgård independently showed a neat answer. Build a compression function that takes a fixed size state and one fixed size block of message and outputs a new state. Pad the message to a whole number of blocks, including its length at the end, then feed the blocks in one by one. The final state is the hash. They proved that if the compression function is collision resistant, so is the whole hash. MD5, SHA-1 and SHA-256 are all built this way. SHA-256 uses 64 byte blocks, a 32 byte state made of eight 32 bit words, and 64 rounds of additions, rotations and bit mixing, with constants taken from the cube roots of the first 64 prime numbers, so nobody can claim the designers hid a trapdoor in them. But the design has one surprising weakness. The hash output is the full internal state. So anyone who knows the hash of some unknown data can keep hashing more blocks, as if they had the data. If a website signs requests as SHA-256 of a secret key followed by the request, an attacker can add new parameters and compute a valid signature without the key. Exactly this broke the Flickr API in 2009.')}
{wwh('<b>Merkle-Damgård</b> builds a hash from a compression function f: H<sub>0</sub> = IV, H<sub>i</sub> = f(H<sub>i&minus;1</sub>, M<sub>i</sub>), and the hash is the last H. <b>Length extension</b>: from H(m) alone, anyone can compute H(m ‖ pad ‖ x).',
     'It explains why SHA(key ‖ message) is not a safe MAC and why HMAC exists. SHA-3 uses a different design, the sponge, which is not vulnerable.',
     'SHA-256 pads with the bit 1, then zeros, then the 64 bit message length, to a multiple of 512 bits. It then runs the compression function on each 512 bit block. The attacker uses the published hash as the state and continues.')}
{viz('cymd')}
{run('length_extension')}
{fxs(fx('Chain', 'H<sub>0</sub> = IV, H<sub>i</sub> = f(H<sub>i&minus;1</sub>, M<sub>i</sub>), hash = H<sub>t</sub>', 'If f is collision resistant, so is H (Merkle and Damgård, 1989).', key=True),
     fx('SHA-256 padding', 'm ‖ 1 ‖ 0<sup>k</sup> ‖ len<sub>64</sub>, with k the smallest number making the total a multiple of 512 bits', 'In bytes: 0x80, then (55 &minus; L) mod 64 zero bytes, then 8 length bytes.', key=True),
     fx('Length extension', 'H(m ‖ pad(m) ‖ x) = f*(H(m), x)', 'Needs only H(m) and the length of m, never m itself.'))}
{table(['Design', 'Examples', 'Length extension'], [
    ['Merkle-Damgård', 'MD5, SHA-1, SHA-256, SHA-512', 'Vulnerable'],
    ['Truncated Merkle-Damgård', 'SHA-512/256, SHA-384', 'Safe: part of the state is hidden'],
    ['Sponge', 'SHA-3, SHAKE', 'Safe: the capacity part of the state is never output'],
    ['HAIFA and tree modes', 'BLAKE2, BLAKE3', 'Safe by design']])}
''', kw=['Merkle-Damgard', 'compression function', 'SHA-256 internals', 'padding', 'length extension', 'Flickr', 'sponge', 'SHA-3', 'BLAKE2', 'SHA-512/256'])

K.lesson('mac', 'Message authentication codes and HMAC', f'''
{talk('Encryption keeps a message secret, but it does not prove who sent it or that it was not changed. For that we need a message authentication code, a MAC. Both sides share a secret key. The sender computes a short tag from the key and the message, and the receiver recomputes it. If an attacker changes the message, they cannot compute the matching tag without the key. The obvious design, hashing the key followed by the message, falls to the length extension attack you just saw. In 1996 Mihir Bellare, Ran Canetti and Hugo Krawczyk designed HMAC, which hashes twice with two different versions of the key, and they proved it secure under mild assumptions about the hash. HMAC became RFC 2104 in 1997 and is now everywhere: in TLS, in JSON Web Tokens, in AWS request signatures, in TOTP codes on your phone, and in the password function PBKDF2. A MAC is not a signature, though. Because both sides share the key, either side could have made the tag, so a MAC cannot prove to a third person who wrote the message. That needs public key signatures, coming later in this section.')}
{wwh('A <b>MAC</b> is a short tag computed from a secret key and a message. <b>HMAC</b> is the standard way to build a MAC from a hash: HMAC(K, m) = H((K0 &oplus; opad) ‖ H((K0 &oplus; ipad) ‖ m)).',
     'Without a MAC, an attacker can change encrypted or plain messages unnoticed. HMAC is simple, fast, proven, and available in every language.',
     'Pad the key to the block size (64 bytes for SHA-256). XOR with ipad (0x36 bytes), hash with the message. XOR the key with opad (0x5c bytes), hash with the inner result. Compare tags with a constant time function.')}
{viz('cyhmac')}
{run('hmac_demo')}
{fxs(fx('HMAC', 'HMAC(K, m) = H( (K0 &oplus; opad) ‖ H( (K0 &oplus; ipad) ‖ m ) )', 'ipad = 0x36 repeated, opad = 0x5c repeated, K0 = key padded to the block size.', key=True),
     fx('Forgery chance', 'P(guessing a valid t bit tag) = 2<sup>&minus;t</sup>', 'A full 256 bit HMAC-SHA256 tag: 2<sup>&minus;256</sup>. Even truncated to 128 bits it is safe.'))}
{table(['Tool', 'Proves unchanged', 'Proves who', 'Key'], [
    ['Hash (SHA-256)', 'Only if the hash travels safely', 'No', 'None'],
    ['MAC (HMAC)', 'Yes', 'Only to someone who shares the key', 'Shared secret'],
    ['Digital signature', 'Yes', 'Yes, to anyone', 'Private key signs, public key checks'],
    ['AEAD tag (GCM)', 'Yes, plus encryption', 'Only to key holders', 'Shared secret']])}
''', kw=['MAC', 'message authentication code', 'HMAC', 'ipad', 'opad', 'RFC 2104', 'RFC 4231', 'JWT', 'tag', 'compare_digest', 'integrity'])

K.lesson('passwords', 'Storing passwords: salts and slow hashes', f'''
{talk('Websites must check your password without storing it, because databases get stolen. The first idea was to store a hash of each password. But a fast hash is a gift to attackers. A single modern graphics card can compute many billions of MD5 hashes per second, so after a breach attackers simply hash every word in a huge list of real leaked passwords and look for matches. In 2012, LinkedIn lost millions of unsalted SHA-1 password hashes, and most were cracked within days. Two defences fix this. A salt is a random value stored next to each hash and mixed into it. Two users with the same password then get different hashes, and attackers cannot reuse precomputed tables, called rainbow tables, across users. A slow hash is deliberately expensive. bcrypt, from 1999, has a cost setting. scrypt, from 2009, also needs lots of memory, which graphics cards have little of per core. Argon2 won the Password Hashing Competition in 2015 and is now the first choice. If checking a guess takes a server a tenth of a second, that is nothing for one login but a disaster for an attacker trying billions of guesses.')}
{wwh('Store passwords with a <b>password hashing function</b>: a random <b>salt</b> per user and a deliberately <b>slow</b>, ideally <b>memory hard</b> function such as Argon2id, scrypt, bcrypt or PBKDF2.',
     'Password databases leak. Salting stops one table cracking everyone, and slowness makes each guess cost the attacker real time and money.',
     'On sign up: make a random 16 byte salt, compute the slow hash, store salt and hash. On login: recompute with the stored salt and compare in constant time. Raise the cost settings as computers get faster.')}
{run('passwords')}
{table(['Function', 'Year', 'Strength', 'OWASP setting (2023)'], [
    ['Argon2id', '2015 (RFC 9106)', 'Memory hard, tunable time and memory', 'm = 19 MiB, t = 2, p = 1'],
    ['scrypt', '2009', 'Memory hard', 'N = 2<sup>17</sup>, r = 8, p = 1'],
    ['bcrypt', '1999', 'Slow, uses only 4 KB, input limited to 72 bytes', 'cost 10 or more'],
    ['PBKDF2-HMAC-SHA256', '2000 (RFC 8018)', 'Slow but not memory hard, FIPS approved', '600,000 iterations'],
    ['MD5, SHA-1, SHA-256 alone', 'n/a', 'Far too fast', 'Never for passwords']])}
{fxs(fx('Attack time', 'time = (number of candidates) / (guesses per second)', 'All 8 letter lower case passwords: 26<sup>8</sup> &asymp; 2.1 &times; 10<sup>11</sup>. At 10<sup>10</sup> MD5 per second: 21 seconds.', key=True),
     fx('Effect of slowness', 'guesses per second &divide; iterations', 'PBKDF2 with 600,000 iterations turns those 21 seconds into about 145 days on the same hardware.', key=True))}
{attack([
    ['Uses rainbow tables of precomputed hashes', 'A unique random salt for every password'],
    ['Runs billions of guesses per second on GPUs', 'Argon2id or scrypt with high cost settings'],
    ['Uses lists of passwords leaked from other sites', 'Check new passwords against known breached lists and add MFA'],
    ['Steals the database and the salts together', 'Add a pepper: a secret key kept outside the database, for example in an HSM']])}
''', kw=['password storage', 'salt', 'pepper', 'rainbow table', 'Argon2', 'scrypt', 'bcrypt', 'PBKDF2', 'OWASP', 'LinkedIn breach', 'GPU cracking', 'memory hard'])

K.lesson('merkle', 'Merkle trees: hashing many things at once', f'''
{talk('Ralph Merkle had another lasting idea, from 1979: the hash tree. Hash every item in a list, then hash the hashes in pairs, then hash those in pairs, until one hash is left at the top, called the root. The root commits to the whole list: change any item and the root changes. The clever part is the proof. To show that one item is in a list of a million, you only need about twenty hashes, the siblings on the path from the item up to the root, because two to the twenty is about a million. Merkle trees are everywhere. Git stores your project as a tree of hashes, so a commit hash pins every file. Bitcoin puts a Merkle root of all transactions in each block header, so a phone can check that a payment is in a block without downloading the block. Certificate Transparency, which keeps public logs of every web certificate, uses Merkle trees so that browsers can check that a certificate was logged and that logs never quietly rewrite history. And file sharing systems like BitTorrent and IPFS use them to check each downloaded piece.')}
{wwh('A <b>Merkle tree</b> hashes items in pairs, level by level, to a single <b>root</b>. An <b>inclusion proof</b> for one item is the list of sibling hashes on its path to the root.',
     'One short root commits to millions of items, and anyone can check one item with about log<sub>2</sub>(n) hashes instead of all n.',
     'Leaves are H(item). Each parent is H(left ‖ right). To verify, start from H(item) and combine with each sibling in the right order. If you reach the root, the item is in the tree.')}
{run('merkle')}
{fxs(fx('Proof size', 'hashes in a proof = log<sub>2</sub> n', 'n = 4: 2 hashes. n = 1,048,576: 20 hashes, 640 bytes with SHA-256.', key=True),
     fx('Domain separation', 'leaf = H(0x00 ‖ item), node = H(0x01 ‖ left ‖ right)', 'RFC 6962 uses different prefixes so that an inner node can never be passed off as a leaf.'))}
{note('The program uses plain H(item) and H(left ‖ right) to stay short. Real systems add the 0x00 and 0x01 prefixes. Bitcoin’s simpler rule of copying the last hash when a level is odd allowed a real bug in 2012 (CVE-2012-2459), where two different transaction lists had the same root.', 'warn')}
''', kw=['Merkle tree', 'hash tree', 'root', 'inclusion proof', 'Git', 'Bitcoin', 'Certificate Transparency', 'RFC 6962', 'log n proof'])

K.lesson('versus', 'Hash functions compared', f'''
{talk('With so many hash functions around, the choice can look confusing, but the rules are short. For general integrity and signatures, use SHA-256, or SHA-512 on 64 bit machines where it can be faster. If length extension could matter, use HMAC, SHA-512/256 or SHA-3. BLAKE2 and BLAKE3 are very fast modern designs, popular in tools and file systems. For passwords, never use any of these directly. Use Argon2id, scrypt or bcrypt. For non security jobs such as hash tables, checksums for accidental errors, or deduplication where nobody is attacking, fast non cryptographic hashes like xxHash or CRC32 are fine, but never let them near a security decision.')}
{versus('Which hash for which job', ['', 'SHA-256', 'SHA-3-256', 'BLAKE3', 'Argon2id', 'MD5 and SHA-1', 'CRC32'], [
    ['Type', 'Merkle-Damgård', 'Sponge', 'Tree based', 'Password hash', 'Merkle-Damgård', 'Checksum'],
    ['Speed', 'Fast, hardware support', 'Medium', 'Very fast, parallel', 'Slow on purpose', 'Fast', 'Very fast'],
    ['Length extension', 'Vulnerable', 'Safe', 'Safe', 'Not relevant', 'Vulnerable', 'Not relevant'],
    ['Security status', 'Safe', 'Safe', 'Safe', 'Safe', 'Broken collisions', 'Not cryptographic'],
    ['Use for', 'Signatures, integrity, HMAC', 'Backup standard, XOF', 'Files, tools', 'Passwords', 'Nothing secure', 'Accidental errors only']],
    'SHA-256 is the default. HMAC for keyed integrity. Argon2id for passwords. MD5, SHA-1 and CRC32 only where no attacker exists.')}
''', kw=['comparison', 'SHA-256 vs SHA-3', 'BLAKE3', 'Argon2id', 'MD5', 'CRC32', 'xxHash'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Hash functions reach from everyday use to the deepest theory. A beginner learns that a hash is a fingerprint and that passwords must be stored as slow, salted hashes. A college student can explain the three security properties, the birthday bound, HMAC and Merkle trees, and write code for each. A masters student studies the random oracle model, where a hash is treated as a perfectly random function in proofs, and its known limits. They study how differential attacks broke MD5 and SHA-1, and how the sponge construction gets its security from the hidden capacity. At the research level, cryptographers build chosen prefix collisions, where two different chosen starting documents are completed so they hash the same. That attack on SHA-1 in 2020 cost about 45 thousand dollars of rented graphics cards and showed that PGP keys signed with SHA-1 could be impersonated. Others design hashes that are cheap inside zero knowledge proofs, such as Poseidon, which matter for the advanced crypto chapter later.')}
{ladder(
    '<p>A hash is a short fingerprint of data. The same data always gives the same hash, and a tiny change gives a different one. Websites should store passwords as salted, slow hashes, never as plain text.</p>',
    '<p>State preimage, second preimage and collision resistance with costs 2<sup>n</sup>, 2<sup>n</sup>, 2<sup>n/2</sup>. Derive the birthday bound. Explain Merkle-Damgård, padding and length extension. Build HMAC and Merkle proofs, and choose Argon2id with a salt for passwords.</p>',
    '<p>The random oracle model and its limits (Canetti, Goldreich and Halevi, 1998). Differential cryptanalysis of MD5 and SHA-1, multicollisions (Joux, 2004) showing that joining two Merkle-Damgård hashes adds little security, indifferentiability and the sponge’s 2<sup>c/2</sup> security from capacity c.</p>',
    '<p>Chosen prefix collisions (MD5 in 2007, used by Flame in 2012, SHA-1 in 2020 by Leurent and Peyrin), quantum collision search (Brassard, Høyer and Tapp: about 2<sup>n/3</sup> in theory), and arithmetization oriented hashes such as Poseidon for zero knowledge proof systems.</p>')}
{grow('Explain hashes as fingerprints and why passwords need salted slow hashes.',
      'Use the three properties, the birthday bound, HMAC, Merkle trees and password hashing correctly.',
      'Reason in the random oracle model, analyse MD and sponge designs, and follow chosen prefix collision research.')}
''', kw=['beginner', 'expert', 'random oracle', 'multicollision', 'Joux', 'indifferentiability', 'chosen prefix collision', 'Poseidon', 'BHT'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A hash maps any input to a fixed size digest. Security: <b>preimage</b> (2<sup>n</sup>), <b>second preimage</b> (2<sup>n</sup>), <b>collision</b> (2<sup>n/2</sup>).',
    '<b>Birthday paradox</b>: P &asymp; 1 &minus; e<sup>&minus;n<sup>2</sup>/2N</sup>, 50% at n &asymp; 1.18 &radic;N. 23 people for 365 days. SHA-256 gives 128 bit collision security.',
    'MD5 (2004) and SHA-1 (2017) have broken collision resistance. Use SHA-256, SHA-512 or SHA-3.',
    '<b>Merkle-Damgård</b>: H<sub>i</sub> = f(H<sub>i&minus;1</sub>, M<sub>i</sub>). Padding: 0x80, zeros, 64 bit length. The output is the full state, so <b>length extension</b> breaks SHA(key ‖ msg).',
    '<b>HMAC</b>(K, m) = H((K0 &oplus; opad) ‖ H((K0 &oplus; ipad) ‖ m)), ipad 0x36, opad 0x5c. Check tags with compare_digest. A MAC does not prove who sent it to a third party.',
    'Passwords: random <b>salt</b> per user plus a slow, memory hard function. Argon2id first, then scrypt, bcrypt, PBKDF2 (600,000 iterations). Never plain fast hashes.',
    '<b>Merkle trees</b>: one root commits to n items, inclusion proofs need log<sub>2</sub> n hashes. Used in Git, Bitcoin and Certificate Transparency.'],
    'The next step of this section moves to public key cryptography, starting with the number theory behind RSA: modular arithmetic, gcd, inverses, Fermat and Euler.')}
{files('Three tasks: a short hash for birthday experiments, HMAC by hand checked against RFC 4231, and a Merkle root.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does a hash function output?', ['A value as long as the input', 'A fixed size digest', 'The key', 'Encrypted text that can be decrypted'], 1, 'SHA-256 always gives the same size.', 'A hash gives a fixed size digest, 256 bits for SHA-256.')
K.quiz('e', 'Which is safe for new security uses?', ['MD5', 'SHA-1', 'SHA-256', 'CRC32'], 2, 'Two of these are broken, one is not cryptographic.', 'SHA-256 is safe. MD5 and SHA-1 have collisions, CRC32 is only a checksum.')
K.quiz('e', 'What is a salt in password storage?', ['A secret key for all users', 'A random value stored with each password hash', 'A type of hash', 'An encryption algorithm'], 1, 'Different for each user.', 'A random per user value that makes equal passwords hash differently.')
K.quiz('e', 'How many people make a shared birthday more likely than not?', ['183', '23', '50', '365'], 1, 'Count pairs, not people.', '23 people give a 50.7% chance.')
K.quiz('m', 'Collision search on an n bit hash costs about', ['2<sup>n</sup>', '2<sup>n/2</sup>', 'n<sup>2</sup>', '2n'], 1, 'Birthday bound.', 'About 2<sup>n/2</sup> random tries.')
K.quiz('m', 'Why is SHA-256(key ‖ message) a bad MAC?', ['SHA-256 is broken', 'Length extension lets attackers add data and compute a valid tag', 'It is too slow', 'Keys cannot be hashed'], 1, 'The output is the full state.', 'Anyone can continue the hash from the tag without knowing the key.')
K.quiz('m', 'What are the HMAC ipad and opad bytes?', ['0x00 and 0xFF', '0x36 and 0x5c', '0x80 and 0x00', '0x5c and 0x36'], 1, 'Inner first.', 'ipad is 0x36, opad is 0x5c (RFC 2104).')
K.quiz('m', 'Why use Argon2id instead of SHA-256 for passwords?', ['SHA-256 has collisions', 'Argon2id is slow and memory hard, so each guess is expensive', 'Argon2id is shorter', 'SHA-256 cannot take passwords'], 1, 'Think of GPUs guessing billions per second.', 'Password hashes must be slow and memory hungry to resist brute force.')
K.quiz('m', 'A Merkle proof for one item among 1,024 needs how many hashes?', ['1,024', '512', '10', '32'], 2, 'log<sub>2</sub> 1024.', 'One sibling per level: log<sub>2</sub> 1024 = 10.')
K.quiz('h', 'Which hash is NOT vulnerable to length extension?', ['MD5', 'SHA-1', 'SHA-256', 'SHA-3-256'], 3, 'Different construction.', 'SHA-3 is a sponge and never outputs its capacity part.')
K.quiz('h', 'Digital signatures on certificates mainly need which property of the hash?', ['Speed', 'Collision resistance', 'Short output', 'Preimage resistance only'], 1, 'Flame and the forged certificate.', 'With a collision, a signature on one document is valid for another.')
K.quiz('h', 'Two users have the same password. With proper salting their stored hashes are', ['Equal', 'Different', 'Empty', 'Reversible'], 1, 'Salts differ.', 'Different random salts give different hashes.')
K.quiz('x', 'In the style of a Stanford CS 255 exam: Joux’s multicollision result shows that H1(m) ‖ H2(m) for two Merkle-Damgård hashes of n bits each gives collision security of about', ['2<sup>n</sup>', 'n &middot; 2<sup>n/2</sup>, far below the 2<sup>n</sup> one might expect', '2<sup>2n</sup>', '2<sup>n/4</sup>'], 1, 'Multicollisions in an iterated hash are cheap.', '2<sup>n/2</sup> collisions chained n/2 times give 2<sup>n/2</sup> messages with one H1 value, and among them a collision in H2 is likely.')
K.quiz('x', 'In the style of an MIT 6.875 question: in the random oracle model the hash is modelled as', ['A secret key', 'A truly random function that everyone can query', 'An encryption scheme', 'A fixed public table of 256 entries'], 1, 'Idealised.', 'Proofs treat H as a random function. Canetti, Goldreich and Halevi showed schemes secure in this model that are insecure with any real hash.')

K.calc('e', 'How many bytes does a SHA-512 digest have?', '64', '512 bits.', ['512 bits.', '8 bits per byte.', eq('512 / 8 = 64 bytes')], check=512 // 8)
K.calc('e', 'What is the HMAC ipad byte in hex?', '36', 'RFC 2104.', ['ipad is repeated 64 times.', 'Its value is 0x36.', eq('36')], check='36')
K.calc('e', 'Smallest number of people with more than a 50% chance of a shared birthday (365 days)?', '23', 'n &asymp; 1.18 &radic;365.', ['&radic;365 &asymp; 19.1.', '1.1774 &times; 19.1 &asymp; 22.5.', eq('so 23 people')], check=next(n for n in range(1, 100) if 1 - __import__('math').prod((365 - i) / 365 for i in range(n)) > 0.5))
K.calc('m', 'How many bits of collision security does SHA-256 give?', '128', 'Half the output.', ['Output 256 bits.', 'Birthday bound 2<sup>n/2</sup>.', eq('256 / 2 = 128')], check=256 // 2)
K.calc('m', 'Using 1.1774 &radic;N, about how many tries find a 24 bit collision? Round to a whole number.', '4823', 'N = 2<sup>24</sup>, &radic;N = 2<sup>12</sup>.', ['&radic;N = 4,096.', '1.1774 &times; 4,096 = 4,822.6.', eq('&asymp; 4,823 tries')], check=round(1.1774 * 2 ** 12))
K.calc('m', 'About how many tries does a 16 bit preimage take?', '65536', '2<sup>n</sup>.', ['A preimage needs about 2<sup>n</sup> tries.', 'n = 16.', eq('2<sup>16</sup> = 65,536')], check=2 ** 16)
K.calc('m', 'SHA-256 padding for a 3 byte message: how many zero bytes come after 0x80?', '52', '(55 &minus; L) mod 64.', ['L = 3.', '55 &minus; 3 = 52.', eq('52 zero bytes, then 8 length bytes: 3 + 1 + 52 + 8 = 64')], check=(55 - 3) % 64)
K.calc('h', 'Length extension: secret 21 bytes plus message 21 bytes. How long is the SHA-256 padding (the "glue") in bytes?', '22', '1 + (55 &minus; 42) mod 64 + 8.', ['L = 42.', '(55 &minus; 42) mod 64 = 13 zero bytes.', eq('1 + 13 + 8 = 22 bytes')], check=1 + (55 - 42) % 64 + 8)
K.calc('h', 'For a 64 bit hash, about how many billion values give a 50% collision chance? Round to a whole number.', '5', '1.1774 &times; 2<sup>32</sup>.', ['2<sup>32</sup> &asymp; 4.295 &times; 10<sup>9</sup>.', '&times; 1.1774 &asymp; 5.06 &times; 10<sup>9</sup>.', eq('&asymp; 5 billion')], check=round(1.1774 * 2 ** 32 / 1e9))
K.calc('h', 'All 8 letter lower case passwords at 10<sup>10</sup> MD5 guesses per second. How many seconds, rounded?', '21', '26<sup>8</sup> candidates.', ['26<sup>8</sup> = 208,827,064,576.', 'Divide by 10<sup>10</sup>.', eq('&asymp; 20.9, about 21 seconds')], check=round(26 ** 8 / 1e10))
K.calc('x', 'In the style of a CMU 18-733 problem: the same attack against PBKDF2 with 600,000 iterations (each guess costs 600,000 hashes). How many days, rounded?', '145', 'Guesses per second fall by 600,000.', ['10<sup>10</sup> / 600,000 &asymp; 16,667 guesses per second.', '2.088 &times; 10<sup>11</sup> / 16,667 &asymp; 1.253 &times; 10<sup>7</sup> seconds.', eq('/ 86,400 &asymp; 145 days')], check=round(26 ** 8 / (1e10 / 600000) / 86400))

K.assign('shorthash', 'e', 'A short hash for experiments',
         '<p>Write <code>short_hash(text, bits)</code> that returns the first <code>bits</code> bits of SHA-256 of the UTF-8 text, as a whole number.</p>',
         '''
import hashlib

def short_hash(text, bits):
    # your code here
    pass
''', [('short_hash("abc", 8)', 186), ('short_hash("abc", 16)', 47736), ('short_hash("abc", 4)', 11)],
         '''
import hashlib

def short_hash(text, bits):
    full = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    return full >> (256 - bits)
''', 'Turn the hex digest into a number with int(..., 16) and shift right by 256 &minus; bits.', '<p>SHA-256("abc") starts with ba78, so 8 bits give 0xba = 186. Short hashes make birthday and preimage attacks small enough to run on a laptop.</p>')
K.assign('hmac', 'm', 'HMAC-SHA256 by hand',
         '<p>Write <code>hmac_tag(key, msg)</code> for byte strings. Hash keys longer than 64 bytes first, pad with zero bytes to 64, then return the hex HMAC using ipad 0x36 and opad 0x5c. Do not use the hmac module.</p>',
         '''
import hashlib

def hmac_tag(key, msg):
    # your code here
    pass
''', [('hmac_tag(b"Jefe", b"what do ya want for nothing?")', '5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843'),
      ('hmac_tag(b"shared secret", b"PAY RIYA 100")', 'e8d3387d800cb5a07006ec9d27f3d03351363b7c56384ce321fa1a838ebecb3b')],
         '''
import hashlib

def hmac_tag(key, msg):
    if len(key) > 64:
        key = hashlib.sha256(key).digest()
    key = key + bytes(64 - len(key))
    inner_key = bytes([b ^ 0x36 for b in key])
    outer_key = bytes([b ^ 0x5C for b in key])
    inner = hashlib.sha256(inner_key + msg).digest()
    return hashlib.sha256(outer_key + inner).hexdigest()
''', 'Follow RFC 2104: K0, then the inner hash of (K0 XOR ipad) + msg, then the outer hash of (K0 XOR opad) + inner.', '<p>The first test is RFC 4231 test case 2, the official check value for HMAC-SHA256.</p>')
K.assign('merkle', 'm', 'A Merkle root',
         '<p>Write <code>merkle_root(items)</code> for a list of strings whose length is a power of 2. Leaves are SHA-256 of each UTF-8 string. Each parent is SHA-256 of left + right (raw 32 byte digests). Return the root as hex.</p>',
         '''
import hashlib

def merkle_root(items):
    # your code here
    pass
''', [('merkle_root(["a", "b", "c", "d"])', '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'),
      ('merkle_root(["tx1", "tx2"])', 'bbea820f07f7f89aeea1ab4a354ecea39f2f72accd05c64371522ee371cd0c48'),
      ('merkle_root(["only"])', 'f905b19542ed08c9a9c26543cca32e5711d207dcffb81b4cdb44ce0b989431c9')],
         '''
import hashlib

def merkle_root(items):
    level = []
    for item in items:
        level.append(hashlib.sha256(item.encode()).digest())
    while len(level) > 1:
        parents = []
        for i in range(0, len(level), 2):
            parents.append(hashlib.sha256(level[i] + level[i + 1]).digest())
        level = parents
    return level[0].hex()
''', 'Keep a list for the current level and replace it by the list of parent hashes until one is left.', '<p>Hash the raw digests, not their hex text. A list with one item has its leaf hash as the root.</p>')

K.must('Properties', 'Preimage 2<sup>n</sup>, second preimage 2<sup>n</sup>, collision 2<sup>n/2</sup>. MD5 and SHA-1 broken for collisions.')
K.must('Birthday', 'P &asymp; 1 &minus; e<sup>&minus;n<sup>2</sup>/2N</sup>. 50% at 1.18 &radic;N. 23 people. SHA-256 = 128 bit collision security.')
K.must('Merkle-Damgård', 'H<sub>i</sub> = f(H<sub>i&minus;1</sub>, M<sub>i</sub>). Pad 0x80, zeros, 64 bit length. Length extension breaks H(key ‖ m). SHA-3 sponge is safe.')
K.must('HMAC', 'H((K0 &oplus; opad) ‖ H((K0 &oplus; ipad) ‖ m)), ipad 0x36, opad 0x5c, 64 byte block. compare_digest.')
K.must('Passwords', 'Salt per user, Argon2id (19 MiB, t = 2), scrypt N = 2<sup>17</sup>, bcrypt 10+, PBKDF2 600,000. Never fast hashes.')
K.must('Merkle trees', 'Root commits to all items. Proof = log<sub>2</sub> n sibling hashes. Git, Bitcoin, Certificate Transparency.')

T = K.topic(
    slug='cy-hashing', topic='cy-hashing', step=(1, 'Classical and symmetric cryptography', 'cy-c1', 'From Caesar to AES: how ciphers were broken, how modern block ciphers work, and how hashes and MACs protect data.', 'Intermediate'),
    title='Hash functions, MACs and password storage', short='Hashes and MACs', badge='1.3', minutes=70,
    lead='Hash functions from the inside out: the three security properties, the birthday paradox and its maths, the Merkle-Damgård chain in SHA-256 and a working length extension attack, HMAC step by step, salted slow password hashing with Argon2id, scrypt and PBKDF2, and Merkle trees with inclusion proofs.',
    desc='hash function, preimage resistance, second preimage, collision resistance, MD5, SHA-1, SHA-256, SHA-3, birthday paradox, birthday attack, Merkle-Damgard, compression function, SHA-256 padding, length extension attack, Flickr, HMAC, ipad, opad, RFC 2104, RFC 4231, MAC, password hashing, salt, pepper, rainbow table, Argon2id, scrypt, bcrypt, PBKDF2, OWASP, Merkle tree, inclusion proof, Certificate Transparency, Git',
    summary='hash properties, the birthday bound, SHA-256 and length extension, HMAC, password hashing and Merkle trees.',
    keywords=['hash', 'birthday paradox', 'SHA-256', 'length extension', 'HMAC', 'salt', 'Argon2', 'Merkle tree', 'collision', 'MAC'],
    recap='<p>Hashes give integrity, HMAC adds a key, slow salted hashes protect passwords, and Merkle trees scale integrity to millions of items.</p>',
    added='2026-11-14')
