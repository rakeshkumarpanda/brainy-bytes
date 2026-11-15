# Cryptography 1.2: symmetric encryption, AES and modes of operation. Checked against FIPS 197 (AES, including the
# worked examples {57}+{83} = {d4}, {57}.{83} = {c1}, xtime of {57} and Appendix C.1), NIST SP 800-38A (ECB, CBC,
# CTR), SP 800-38D (GCM), SP 800-131A Rev. 2 (3DES retired after 2023), RFC 8439 (ChaCha20-Poly1305), RFC 5652
# section 6.3 (PKCS 7 padding), Vaudenay (2002) on padding oracles, Bhargavan and Leurent (2016) on Sweet32, and the
# cryptography package documentation for AESGCM.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-aes')
K = Kit()


def _gm(a, b):
    """GF(2^8) multiply, used only to check a problem answer below."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = ((a << 1) ^ (0x11B if a & 0x80 else 0)) & 0xFF
        b >>= 1
    return r


K.code('gf_maths', r'''
# Arithmetic in GF(2^8), the field of 256 bytes that AES works in
def xtime(a):                       # multiply by 2: shift left, and reduce if a 9th bit appears
    a = a << 1
    if a & 0x100:
        a = a ^ 0x11B               # x^8 + x^4 + x^3 + x + 1
    return a

def gmul(a, b):                     # multiply: add (XOR) shifted copies, like long multiplication
    result = 0
    while b:
        if b & 1:
            result = result ^ a
        a = xtime(a)
        b = b >> 1
    return result

print("addition is XOR: {57} + {83} =", hex(0x57 ^ 0x83))

a = 0x57
for power in [1, 2, 4, 8, 16]:
    print("{57} x", power, "=", hex(a))
    a = xtime(a)

print("{57} x {83} =", hex(gmul(0x57, 0x83)))
print("{57} x {13} =", hex(gmul(0x57, 0x13)))

for b in range(1, 256):             # every non zero byte has an inverse
    if gmul(0x53, b) == 1:
        print("inverse of {53} is", hex(b))
        break
''', long=True)

K.code('aes_core', r'''
# AES-128 from scratch, checked against the example in FIPS 197 (Appendix C.1). For learning only.
def xtime(a):                       # multiply by 2 in GF(2^8)
    a = a << 1
    if a & 0x100:
        a = a ^ 0x11B
    return a

def gmul(a, b):                     # multiply two bytes in GF(2^8)
    result = 0
    while b:
        if b & 1:
            result = result ^ a
        a = xtime(a)
        b = b >> 1
    return result

# 3 generates every non zero byte: 3^0, 3^1, ..., 3^254. Log tables then give inverses quickly.
EXP = [1] * 255
for i in range(1, 255):
    EXP[i] = gmul(EXP[i - 1], 3)
LOG = [0] * 256
for i in range(255):
    LOG[EXP[i]] = i

def inverse(a):
    if a == 0:
        return 0
    return EXP[(255 - LOG[a]) % 255]

SBOX = []                           # inverse, then a fixed bit mixing (affine) step, then XOR 0x63
for x in range(256):
    b = inverse(x)
    s = 0x63
    for i in range(8):
        bit = (b >> i) ^ (b >> ((i + 4) % 8)) ^ (b >> ((i + 5) % 8)) ^ (b >> ((i + 6) % 8)) ^ (b >> ((i + 7) % 8))
        s = s ^ ((bit & 1) << i)
    SBOX.append(s)

def sub_bytes(state):
    return [SBOX[v] for v in state]

def shift_rows(state):              # state is 16 bytes, column by column
    out = [0] * 16
    for i in range(16):
        row, col = i % 4, i // 4
        out[i] = state[row + 4 * ((col + row) % 4)]
    return out

def mix_columns(state):
    out = []
    for c in range(4):
        a0, a1, a2, a3 = state[4 * c:4 * c + 4]
        out.append(gmul(a0, 2) ^ gmul(a1, 3) ^ a2 ^ a3)
        out.append(a0 ^ gmul(a1, 2) ^ gmul(a2, 3) ^ a3)
        out.append(a0 ^ a1 ^ gmul(a2, 2) ^ gmul(a3, 3))
        out.append(gmul(a0, 3) ^ a1 ^ a2 ^ gmul(a3, 2))
    return out

def add_round_key(state, key):
    return [state[i] ^ key[i] for i in range(16)]

def expand_key(key):                # 11 round keys of 16 bytes from one 16 byte key
    keys = [list(key)]
    rcon = 1
    for r in range(1, 11):
        prev = keys[-1]
        t = [SBOX[prev[13]] ^ rcon, SBOX[prev[14]], SBOX[prev[15]], SBOX[prev[12]]]
        new = []
        for i in range(16):
            if i < 4:
                new.append(prev[i] ^ t[i])
            else:
                new.append(prev[i] ^ new[i - 4])
        keys.append(new)
        rcon = xtime(rcon)
    return keys

def encrypt_block(block, key):
    keys = expand_key(key)
    state = add_round_key(list(block), keys[0])
    for r in range(1, 11):
        state = sub_bytes(state)
        state = shift_rows(state)
        if r < 10:                  # the last round has no MixColumns
            state = mix_columns(state)
        state = add_round_key(state, keys[r])
    return bytes(state)

key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
plain = bytes.fromhex("00112233445566778899aabbccddeeff")
cipher = encrypt_block(plain, key)
print("S-box of {53}:", hex(SBOX[0x53]), "(FIPS 197 says 0xed)")
print("ciphertext   :", cipher.hex())
print("FIPS 197 says: 69c4e0d86a7b0430d8cdb78070b4c55a")
print("match:", cipher.hex() == "69c4e0d86a7b0430d8cdb78070b4c55a")
''', long=True)

K.code('modes_demo', r'''
# Block cipher modes: why ECB leaks patterns and CBC and CTR do not
import hashlib
import hmac

def round_function(half, key, r):           # any mixing function works inside a Feistel network
    return hmac.new(key, bytes([r]) + half, hashlib.sha256).digest()[:8]

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def encrypt_block(block, key):              # a 16 byte Feistel block cipher, the structure DES used
    left, right = block[:8], block[8:]
    for r in range(4):
        left, right = right, xor(left, round_function(right, key, r))
    return left + right

def decrypt_block(block, key):              # the same rounds backwards: round_function is never inverted
    left, right = block[:8], block[8:]
    for r in range(3, -1, -1):
        left, right = xor(right, round_function(left, key, r)), left
    return left + right

def blocks(data):
    return [data[i:i + 16] for i in range(0, len(data), 16)]

key = b"a demo key only"
message = b"PAY RIYA 100 RS." * 3 + b"PAY AMIT 500 RS."      # four 16 byte blocks, three the same

ecb = [encrypt_block(b, key) for b in blocks(message)]
print("ECB:")
for c in ecb:
    print("  ", c.hex())

iv = bytes(16)                               # use a random IV in real life: secrets.token_bytes(16)
prev, cbc = iv, []
for b in blocks(message):
    c = encrypt_block(xor(b, prev), key)
    cbc.append(c)
    prev = c
print("CBC:")
for c in cbc:
    print("  ", c.hex())

nonce = b"nonce123"
ctr = []
for i, b in enumerate(blocks(message)):
    pad = encrypt_block(nonce + i.to_bytes(8, "big"), key)
    ctr.append(xor(b, pad))
print("CTR:")
for c in ctr:
    print("  ", c.hex())

back = b"".join(decrypt_block(c, key) for c in ecb)
print("ECB decrypts back:", back == message)
''', long=True)

K.code('pkcs7', r'''
# PKCS 7 padding: fill the last block with N bytes of value N
def pad(data, size=16):
    n = size - len(data) % size            # always 1 to 16 bytes, never 0
    return data + bytes([n]) * n

def unpad(data, size=16):
    n = data[-1]
    if n < 1 or n > size or data[-n:] != bytes([n]) * n:
        raise ValueError("bad padding")
    return data[:-n]

for msg in [b"HELLO", b"EXACTLY16BYTES!!", b""]:
    padded = pad(msg)
    print(len(msg), "bytes ->", len(padded), "bytes, ends with", padded[-3:].hex())

print(unpad(pad(b"HELLO")))
try:
    unpad(b"HELLO" + bytes([3, 3, 2]))
except ValueError as error:
    print("rejected:", error)
''')

K.code('aes_gcm', r'''
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
''')

K.lesson('idea', 'Symmetric encryption and block ciphers', f'''
{talk('Modern encryption began in the 1970s. Banks and governments needed a public standard, so in 1977 the United States adopted the Data Encryption Standard, DES, based on an IBM design called Lucifer. DES used a 56 bit key. At the time that was a lot, but computers kept getting faster. In 1998 the Electronic Frontier Foundation built a machine called Deep Crack for about 250,000 dollars that found a DES key in 56 hours, and in 1999, working with thousands of volunteers over the internet, it took less than a day. The world needed a replacement, and this time NIST ran an open competition. Fifteen designs from around the world were attacked in public for three years. In October 2000 the winner was announced: Rijndael, by two Belgian researchers, Joan Daemen and Vincent Rijmen. It became the Advanced Encryption Standard, AES, in 2001. Today AES protects your Wi-Fi, your disk, your phone, your messages and almost every secure web page, and modern processors have special instructions that run it in a few cycles per byte. In more than twenty years, nobody has found a practical way to break it.')}
{src('FIPS 197, NIST SP 800-38A and 800-38D, SP 800-131A Rev. 2, RFC 8439, RFC 5652, Vaudenay (2002), Bhargavan and Leurent (2016).')}
{wwh('<b>Symmetric encryption</b> uses the same secret key to encrypt and decrypt. A <b>block cipher</b> such as AES encrypts one fixed size block (128 bits for AES) at a time. A <b>mode of operation</b> says how to use it for longer messages.',
     'Symmetric ciphers are fast, so they encrypt almost all real data. Public key cryptography, covered later, is mostly used to agree on a symmetric key.',
     'A block cipher is a keyed permutation: for each key it shuffles all 2<sup>128</sup> possible blocks in a way that looks random. It is built from many rounds of simple steps that create <b>confusion</b> (the key is mixed in non linearly) and <b>diffusion</b> (each input bit affects every output bit).')}
{table(['Cipher', 'Year', 'Block', 'Key', 'Status'], [
    ['DES', '1977', '64 bits', '56 bits', 'Broken by brute force (1998)'],
    ['3DES', '1998', '64 bits', '112 bits effective', 'Retired by NIST after 2023, small block (Sweet32)'],
    ['AES', '2001', '128 bits', '128, 192 or 256 bits', 'The standard. No practical attack'],
    ['ChaCha20', '2008', 'Stream cipher', '256 bits', 'Standard in TLS 1.3, fast without AES hardware']])}
{note('Shannon named the two goals in 1949: confusion hides how the key relates to the ciphertext, diffusion spreads each plaintext bit over the whole ciphertext. Every modern block cipher is built around them.', 'exam')}
''', kw=['symmetric encryption', 'block cipher', 'DES', '3DES', 'AES', 'Rijndael', 'Deep Crack', 'confusion', 'diffusion', 'permutation', 'ChaCha20'])

K.lesson('gf', 'The maths inside AES: the field GF(2<sup>8</sup>)', f'''
{talk('AES treats every byte as a small polynomial. The byte 0x57, which is 0101 0111 in binary, stands for x to the 6 plus x to the 4 plus x squared plus x plus 1, one term for each 1 bit. Adding two bytes means adding polynomials whose coefficients are only 0 or 1, where 1 plus 1 is 0. That is exactly the XOR operation. Multiplying is like school long multiplication of polynomials, but the result can grow past 8 bits, so we divide by a fixed polynomial of degree 8 and keep the remainder, much like taking a number modulo 26 in the Caesar cipher. AES uses x to the 8 plus x to the 4 plus x cubed plus x plus 1, which is 0x11B. This set of 256 bytes with these rules is a finite field, named GF of 2 to the 8, after Évariste Galois, the French mathematician who died at 20 in a duel in 1832 and left the theory behind. In a field, every non zero element has an inverse, so we can divide. AES uses that inverse to build its S-box, because inversion is very non linear, which is just what a cipher needs.')}
{wwh('<b>GF(2<sup>8</sup>)</b> is a set of 256 elements (the bytes) where addition is XOR and multiplication is polynomial multiplication modulo m(x) = x<sup>8</sup> + x<sup>4</sup> + x<sup>3</sup> + x + 1.',
     'AES needs byte operations that can be undone (a field has inverses) and that mix bits in a non linear way. GF(2<sup>8</sup>) gives both, and it fits exactly in one byte.',
     'Add with XOR. Multiply by 2 with <code>xtime</code>: shift left one bit and, if a 9th bit appears, XOR with 0x11B. Multiply by any byte by adding shifted copies. The inverse of a is the byte b with a &middot; b = 1.')}
{run('gf_maths')}
{fxs(fx('Addition', 'a + b = a &oplus; b', '{{57}} + {{83}} = {{d4}}. Subtraction is the same as addition.', key=True),
     fx('Multiply by 2 (xtime)', 'xtime(a) = (a &laquo; 1) &oplus; (0x11B if bit 7 of a was 1)', '{{57}} &middot; 2 = {{ae}}, &middot; 4 = {{47}}, &middot; 8 = {{8e}}, &middot; 16 = {{07}}.', key=True),
     fx('General multiply', '{{57}} &middot; {{13}} = {{57}} &middot; (16 + 2 + 1) = {{07}} &oplus; {{ae}} &oplus; {{57}} = {{fe}}', 'Write the second byte as a sum of powers of 2 and add the xtime results.'),
     fx('Inverse', 'a<sup>&minus;1</sup> = a<sup>254</sup>, because a<sup>255</sup> = 1 for a &ne; 0', 'The inverse of {{53}} is {{ca}}. The S-box applies an affine map to this inverse: S(53) = {{ed}}.'))}
{deep('Why the S-box resists attacks', '<p>Linear cryptanalysis (Matsui, 1993) looks for linear equations between input, output and key bits that hold more often than half the time. Differential cryptanalysis (Biham and Shamir, 1990) looks for input differences that cause one output difference with high probability. Inversion in GF(2<sup>8</sup>) has the best possible behaviour for an 8 bit map: no input difference leads to any output difference with probability above 4/256, and the best linear approximation holds with probability at most 1/2 + 16/256. AES then uses ShiftRows and MixColumns so that any 4 round path must pass through at least 25 S-boxes, which makes both attacks far more expensive than brute force.</p>')}
''', kw=['GF(2^8)', 'finite field', 'Galois field', 'polynomial', 'xtime', '0x11B', 'irreducible polynomial', 'inverse', 'S-box', 'linear cryptanalysis', 'differential cryptanalysis'])

K.lesson('aes', 'How AES works: rounds, state and key schedule', f'''
{talk('AES works on a block of 16 bytes arranged as a 4 by 4 grid called the state. Each round applies four simple steps. SubBytes swaps each byte through the S-box. ShiftRows slides the rows sideways by different amounts. MixColumns multiplies each column by a fixed matrix in the field you just met. AddRoundKey XORs in 16 bytes of key material. A 128 bit key gets 10 rounds, a 192 bit key 12, and a 256 bit key 14. The key schedule stretches the one main key into a different round key for each round. Why so many rounds? Each round mixes a little, and the designers proved that after a few rounds every output bit depends on every input bit and every key bit in a complicated way. The best known attack on full AES-128, the biclique attack from 2011, is only about four times faster than trying every key, which still means 2 to the 126 operations. That is far beyond any computer that exists or is planned.')}
{wwh('<b>AES</b> encrypts a 128 bit block with a 128, 192 or 256 bit key, using 10, 12 or 14 rounds of SubBytes, ShiftRows, MixColumns and AddRoundKey on a 4 &times; 4 byte state.',
     'It is the most used cipher in the world. Understanding its steps tells you why a key alone is not enough: the mode, the IV and the integrity check matter just as much.',
     'Start with AddRoundKey using the first round key. Then do the full round 9 times (for AES-128) and a last round without MixColumns. Decryption runs the inverse steps in reverse order.')}
{viz('cyaesround')}
{run('aes_core')}
{table(['Step', 'What it does', 'Purpose'], [
    ['SubBytes', 'Each byte through the S-box', 'Confusion: the only non linear step'],
    ['ShiftRows', 'Row r rotates left by r places', 'Diffusion across columns'],
    ['MixColumns', 'Each column times a fixed 4 &times; 4 matrix in GF(2<sup>8</sup>)', 'Diffusion within a column'],
    ['AddRoundKey', 'XOR with the round key', 'Mixes in the secret key'],
    ['Key schedule', 'RotWord, SubWord and a round constant', 'A different key for every round']])}
{fx('MixColumns', '[b<sub>0</sub>, b<sub>1</sub>, b<sub>2</sub>, b<sub>3</sub>] = [[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]] &middot; [a<sub>0</sub>, a<sub>1</sub>, a<sub>2</sub>, a<sub>3</sub>]', 'All products and sums in GF(2<sup>8</sup>). Change one input byte and all four outputs change.', key=True)}
{note('The program is for learning only. Real code must use a tested library, because simple implementations leak the key through timing and cache use (table lookups take different times for different bytes). Modern CPUs offer AES instructions (AES-NI) that run in constant time.', 'warn')}
''', kw=['AES', 'rounds', 'state', 'SubBytes', 'ShiftRows', 'MixColumns', 'AddRoundKey', 'key schedule', 'AES-128', 'AES-256', 'biclique', 'AES-NI', 'FIPS 197'])

K.lesson('modes', 'Modes of operation: ECB, CBC and CTR', f'''
{talk('A block cipher only encrypts 16 bytes. Real messages are longer, so we need a mode of operation, a recipe for using the cipher many times. The obvious recipe, called electronic codebook or ECB, encrypts each block separately. It has a famous flaw. When someone encrypted a picture of Tux, the Linux penguin, with ECB, the encrypted picture still clearly showed the penguin, because every identical block of the picture became the same encrypted block. Cipher block chaining, CBC, invented at IBM in 1976, fixes this by mixing each block with the previous encrypted block, starting from a random value called the initialisation vector, or IV. Counter mode, CTR, turns the block cipher into a stream cipher: it encrypts a counter to make a long key stream, which is XORed with the message, just like a one time pad made from a short key. CTR can encrypt many blocks at once in parallel, which is why it is the basis of the fastest modern modes. But each mode has its own rule that must never be broken. For CBC the IV must be unpredictable. For CTR, a nonce and counter pair must never repeat with the same key, or you are back to the two time pad.')}
{wwh('A <b>mode of operation</b> turns a block cipher into a way to encrypt messages of any length. <b>ECB</b> encrypts blocks separately, <b>CBC</b> chains each block to the previous ciphertext, <b>CTR</b> XORs the message with an encrypted counter.',
     'The mode decides what an attacker can see. ECB shows repeated blocks. A repeated CTR nonce reveals the XOR of two messages. A predictable CBC IV allowed the BEAST attack on TLS 1.0 in 2011.',
     'ECB: C<sub>i</sub> = E(P<sub>i</sub>). CBC: C<sub>i</sub> = E(P<sub>i</sub> &oplus; C<sub>i&minus;1</sub>), C<sub>0</sub> = IV. CTR: C<sub>i</sub> = P<sub>i</sub> &oplus; E(nonce &#8214; i).')}
{viz('cyecb')}
{viz('cycbc')}
{run('modes_demo')}
{table(['Mode', 'Encrypt', 'Decrypt', 'Parallel', 'Rule'], [
    ['ECB', 'C<sub>i</sub> = E(P<sub>i</sub>)', 'P<sub>i</sub> = D(C<sub>i</sub>)', 'Yes', 'Never use for real data'],
    ['CBC', 'C<sub>i</sub> = E(P<sub>i</sub> &oplus; C<sub>i&minus;1</sub>)', 'P<sub>i</sub> = D(C<sub>i</sub>) &oplus; C<sub>i&minus;1</sub>', 'Decrypt only', 'Random, unpredictable IV. Add a MAC'],
    ['CTR', 'C<sub>i</sub> = P<sub>i</sub> &oplus; E(N &#8214; i)', 'Same as encrypt', 'Yes', 'Never repeat nonce and counter. Add a MAC'],
    ['GCM', 'CTR plus a GHASH tag', 'Check tag, then CTR', 'Yes', 'Unique 96 bit nonce. The default choice'],
    ['XTS', 'Tweaked per disk sector', 'Same idea', 'Yes', 'Disk encryption (BitLocker, FileVault, LUKS)']])}
{note('The program uses a small Feistel network as its block cipher, the structure of DES: split the block in halves, and in each round XOR one half with a function of the other half. A Feistel cipher decrypts by running the rounds backwards, even if the round function cannot be inverted.', 'tip')}
''', kw=['mode of operation', 'ECB', 'CBC', 'CTR', 'GCM', 'XTS', 'IV', 'nonce', 'ECB penguin', 'BEAST', 'Feistel network', 'parallel encryption'])

K.lesson('padding', 'Padding and the padding oracle attack', f'''
{talk('ECB and CBC can only encrypt whole blocks, so a message that is 13 bytes long needs 3 extra bytes. The usual rule, called PKCS 7 padding, fills the gap with bytes that all have the value of the gap: three bytes of value 3. If the message already fills the last block exactly, a whole extra block of sixteen 16s is added, so the receiver can always remove the padding without guessing. That sounds harmless, but in 2002 the Swiss cryptographer Serge Vaudenay showed a frightening attack. If a server tells you, even indirectly, whether the padding of a ciphertext you sent was correct, then you can decrypt any CBC message byte by byte, with about 128 tries per byte on average, without ever learning the key. The leak can be an error message, a different status code, or even a few microseconds of difference in response time. Padding oracle attacks hit ASP.NET in 2010, and TLS suffered related attacks such as Lucky Thirteen in 2013 and POODLE in 2014. The deep lesson: encryption without an integrity check lets attackers play with your ciphertexts and learn from your reactions.')}
{wwh('<b>PKCS 7 padding</b> adds N bytes of value N (1 &le; N &le; 16) so the message fills whole blocks. A <b>padding oracle</b> is any behaviour that tells an attacker whether a ciphertext decrypted to valid padding.',
     'It shows why "encrypt only" designs fail. The fix is authenticated encryption, which rejects any changed ciphertext before looking at its padding.',
     'The attacker changes the previous ciphertext block byte by byte. When the server says the padding is valid, the attacker knows that the last decrypted byte equals 01 (then 02 02, and so on) and can solve for the real plaintext byte with XOR.')}
{run('pkcs7')}
{fxs(fx('Padding length', 'N = 16 &minus; (L mod 16)', 'L = 13 gives N = 3. L = 16 gives N = 16, a full extra block.', key=True),
     fx('Padding oracle cost', 'about 128 tries per byte on average, at most 256', 'A 16 byte block needs at most 16 &times; 256 = 4,096 requests.'))}
{attack([
    ['Sends changed CBC ciphertexts and watches for "bad padding" errors', 'Use authenticated encryption (AES-GCM). Check the MAC before decrypting'],
    ['Measures tiny timing differences between padding and MAC errors', 'Constant time checks and one generic error for every failure'],
    ['Flips bits in a CBC block to change the next plaintext block', 'Encrypt then MAC, or an AEAD mode']])}
''', kw=['padding', 'PKCS 7', 'padding oracle', 'Vaudenay', 'POODLE', 'Lucky Thirteen', 'CBC bit flipping', 'encrypt then MAC'])

K.lesson('aead', 'Authenticated encryption: AES-GCM and ChaCha20-Poly1305', f'''
{talk('Encryption hides a message, but it does not stop someone from changing it. In CTR mode, flipping one bit of the ciphertext flips the same bit of the plaintext, so an attacker who knows the message format could turn a payment of 100 into 900 without knowing the key. The answer is authenticated encryption with associated data, AEAD, which encrypts and adds a tag that proves the ciphertext and some extra unencrypted data, like a header, were not changed. Galois Counter Mode, GCM, standardised by NIST in 2007, combines counter mode with a fast checksum computed in the field GF of 2 to the 128. ChaCha20-Poly1305, built by Daniel Bernstein, is the other main choice and is fast on phones without AES hardware. TLS 1.3, the protocol behind secure web pages, allows only AEAD ciphers. There is one strict rule for GCM: never use the same nonce twice with the same key. If you do, the attacker gets the XOR of the two messages, and worse, can recover the secret value used for the tag and then forge messages. This is called the forbidden attack, and researchers found real web servers making exactly this mistake in 2016.')}
{wwh('<b>AEAD</b> (authenticated encryption with associated data) gives confidentiality and integrity together. <b>AES-GCM</b> and <b>ChaCha20-Poly1305</b> encrypt the message and produce a 16 byte tag over the ciphertext and the associated data.',
     'An attacker who changes even one bit is caught before the data is used. This removes padding oracles and bit flipping attacks at once.',
     'Encrypt with a key, a unique nonce, the plaintext and optional associated data. Decrypt with the same key, nonce and associated data. If the tag does not match, the library raises an error and returns nothing.')}
{local('aes_gcm', 'It needs the cryptography package: python3 -m pip install cryptography.')}
{table(['Choice', 'Use it for', 'Nonce rule'], [
    ['AES-256-GCM', 'Most data on servers and laptops with AES hardware', '96 bit, unique per key. Random nonces are fine up to about 2<sup>32</sup> messages per key'],
    ['ChaCha20-Poly1305', 'Phones and devices without AES hardware, and TLS 1.3', '96 bit, unique per key'],
    ['XChaCha20-Poly1305', 'Many messages with random nonces', '192 bit nonce, so random nonces are always safe'],
    ['AES-GCM-SIV', 'When a nonce might accidentally repeat', 'A repeat only reveals that two messages were equal']])}
{note('Order matters if you build it yourself: encrypt, then compute a MAC over the ciphertext (encrypt then MAC). MAC then encrypt led to the padding oracle attacks on TLS. Better still, use an AEAD from a library and do not build it yourself.', 'exam')}
''', kw=['AEAD', 'authenticated encryption', 'AES-GCM', 'ChaCha20-Poly1305', 'tag', 'associated data', 'nonce reuse', 'forbidden attack', 'GCM-SIV', 'TLS 1.3', 'encrypt then MAC'])

K.lesson('keysize', 'Key sizes, brute force and the birthday bound', f'''
{talk('How long does a key need to be? Each extra bit doubles the work of trying every key. A 56 bit DES key has about 72 thousand million million keys, and special hardware tried them in days in 1998. A 128 bit AES key has 2 to the 128 keys, a number with 39 digits. If every one of the eight billion people on Earth had a computer trying a billion billion keys per second, searching half the space would still take more than six hundred years. Quantum computers change the picture a little. Grover’s algorithm, from 1996, can search an unordered space of N items in about the square root of N steps, so it would cut AES-128 to around 2 to the 64 quantum steps, and AES-256 to 2 to the 128. That is why governments now ask for AES-256 for long term secrets. A second limit matters for the block size. With 64 bit blocks, as in 3DES, two ciphertext blocks become equal by chance after about 2 to the 32 blocks, around 32 gigabytes, because of the birthday paradox. In 2016 the Sweet32 attack used that to recover secret cookies from long running 3DES connections.')}
{wwh('The <b>key size</b> sets brute force cost: 2<sup>n</sup> keys for an n bit key. The <b>block size</b> sets how much data one key can safely encrypt before random collisions leak information.',
     'Choosing sizes is a real engineering decision: AES-128 is enough today against classical computers, AES-256 adds a margin against quantum search, and 64 bit blocks are no longer acceptable.',
     'Average brute force time = 2<sup>n&minus;1</sup> / speed. Grover reduces this to about 2<sup>n/2</sup>. Collisions among b bit blocks appear after about 2<sup>b/2</sup> blocks.')}
{fxs(fx('Brute force', 'average tries = 2<sup>n</sup> / 2 = 2<sup>n&minus;1</sup>', 'DES at 9 &times; 10<sup>10</sup> keys per second: 2<sup>55</sup> / (9 &times; 10<sup>10</sup>) s &asymp; 4.6 days.', key=True),
     fx('Grover’s quantum search', 'about 2<sup>n/2</sup> steps', 'AES-128 drops to about 64 bit security, AES-256 to 128 bits. Grover cannot be run in parallel efficiently, so the real cost is even higher.', key=True),
     fx('Birthday bound for blocks', 'collisions after about 2<sup>b/2</sup> blocks', '64 bit blocks: 2<sup>32</sup> blocks &times; 8 bytes = 32 GiB. 128 bit blocks: 2<sup>64</sup> blocks, about 256 billion GiB.'))}
{table(['Key', 'Classical security', 'Against Grover', 'Verdict'], [
    ['56 bit (DES)', '2<sup>56</sup>', '2<sup>28</sup>', 'Broken'],
    ['112 bit (3DES)', '2<sup>112</sup>', '2<sup>56</sup>', 'Retired: small block'],
    ['128 bit (AES-128)', '2<sup>128</sup>', '2<sup>64</sup>', 'Safe today'],
    ['256 bit (AES-256)', '2<sup>256</sup>', '2<sup>128</sup>', 'Safe long term']])}
''', kw=['key size', 'brute force', 'Grover', 'quantum', 'AES-256', 'birthday bound', 'block size', 'Sweet32', '3DES', '2^128'])

K.lesson('versus', 'Symmetric choices compared', f'''
{talk('When you pick a symmetric cipher today, the real decision is rarely the algorithm, because AES and ChaCha20 are both excellent. The decision is the mode and how you handle nonces and keys. Encrypting a disk needs a mode that keeps each sector the same size, so XTS is used there, but it cannot detect tampering, which is acceptable for a stolen laptop but not for a network. Encrypting network messages needs an AEAD such as GCM. Encrypting many messages with random nonces suggests XChaCha20. And when you build a whole protocol, use a vetted library such as libsodium or the Python cryptography package, rather than putting the pieces together yourself, because most real failures happen in that putting together.')}
{versus('Picking a symmetric scheme', ['', 'AES-GCM', 'ChaCha20-Poly1305', 'AES-CBC + HMAC', 'AES-XTS', 'AES-ECB'], [
    ['Integrity', 'Yes (tag)', 'Yes (tag)', 'Yes, if MAC is checked first', 'No', 'No'],
    ['Speed', 'Very fast with AES-NI', 'Very fast in software', 'Slower, two passes', 'Fast', 'Fast'],
    ['Main risk', 'Nonce reuse is fatal', 'Nonce reuse is fatal', 'Padding oracles if done in the wrong order', 'Tampering not detected', 'Leaks patterns'],
    ['Where used', 'TLS, SSH, cloud storage', 'TLS on phones, WireGuard', 'Older systems', 'Disk encryption', 'Nowhere, for real data'],
    ['Verdict', 'Default choice', 'Default without AES hardware', 'Legacy, acceptable', 'Disks only', 'Avoid']],
    'Use an AEAD (AES-GCM or ChaCha20-Poly1305) for data in motion and in files, XTS for whole disks, and never ECB. The weakest part is usually nonce and key handling, not the cipher.')}
''', kw=['comparison', 'AES-GCM vs ChaCha20', 'CBC HMAC', 'XTS', 'ECB', 'WireGuard', 'libsodium'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Symmetric cryptography has layers. A beginner knows that one shared key locks and unlocks, and that AES is the standard. A college student can describe the AES round, explain modes and why ECB is unsafe, and use AES-GCM correctly from a library. A masters student studies security definitions: a block cipher should be a pseudorandom permutation, CBC and CTR are secure against chosen plaintext attacks with random IVs, and GCM is secure against chosen ciphertext attacks as long as nonces are unique. They also study side channels, where the key leaks through time, power use or electromagnetic signals. At the research frontier, cryptographers design lightweight ciphers for tiny devices, like Ascon, which NIST selected in 2023 and published as a standard in 2025. They also study how to keep implementations constant time, and how quantum computers might change the security of symmetric schemes beyond Grover’s search.')}
{ladder(
    '<p>One secret key locks and unlocks. AES is the cipher everyone uses. Never encrypt a picture or file block by block with ECB.</p>',
    '<p>Explain the AES round and the four steps, multiply in GF(2<sup>8</sup>), compare ECB, CBC, CTR and GCM, apply PKCS 7 padding, and use AES-GCM from a library with unique nonces.</p>',
    '<p>Pseudorandom permutations and the PRP/PRF switching lemma, IND-CPA security of CBC and CTR, IND-CCA and authenticated encryption (GCM, encrypt then MAC), padding oracles as chosen ciphertext attacks, and side channels: cache timing attacks on table based AES (Bernstein in 2005, and Osvik, Shamir and Tromer in 2006) and power analysis.</p>',
    '<p>Lightweight cryptography (Ascon, NIST SP 800-232, 2025), nonce misuse resistant AEAD (GCM-SIV, RFC 8452), wide block and tweakable ciphers, formal verification of constant time code, and the effect of quantum algorithms beyond Grover, such as Simon’s algorithm breaking some modes in the quantum query model.</p>')}
{grow('Explain symmetric keys, AES and why ECB fails.',
      'Describe the AES round, compute in GF(2<sup>8</sup>), choose modes and use AES-GCM correctly.',
      'Define PRP and IND-CCA security, analyse padding oracles and side channels, and follow lightweight and misuse resistant designs.')}
''', kw=['beginner', 'expert', 'PRP', 'IND-CCA', 'side channel', 'cache timing', 'power analysis', 'Ascon', 'GCM-SIV', 'lightweight cryptography'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Symmetric encryption uses one shared key. A <b>block cipher</b> encrypts fixed blocks. DES (56 bit) fell in 1998. <b>AES</b> (128 bit block, 128, 192 or 256 bit key) has been the standard since 2001.',
    'AES works in <b>GF(2<sup>8</sup>)</b>: add = XOR, multiply mod x<sup>8</sup> + x<sup>4</sup> + x<sup>3</sup> + x + 1 (0x11B). {{57}} + {{83}} = {{d4}}, {{57}} &middot; {{83}} = {{c1}}.',
    'Each AES round: <b>SubBytes</b> (S-box, non linear), <b>ShiftRows</b>, <b>MixColumns</b>, <b>AddRoundKey</b>. 10, 12 or 14 rounds. The last round has no MixColumns.',
    '<b>ECB</b> leaks repeated blocks. <b>CBC</b>: C<sub>i</sub> = E(P<sub>i</sub> &oplus; C<sub>i&minus;1</sub>) with a random IV. <b>CTR</b>: C<sub>i</sub> = P<sub>i</sub> &oplus; E(nonce &#8214; i), never repeat a nonce.',
    '<b>PKCS 7</b> adds N bytes of value N. A padding oracle decrypts CBC in about 128 tries per byte.',
    'Use <b>AEAD</b>: AES-GCM or ChaCha20-Poly1305, 96 bit unique nonce, 16 byte tag. Nonce reuse in GCM is catastrophic.',
    'Brute force: 2<sup>n&minus;1</sup> tries on average. Grover gives about 2<sup>n/2</sup>, so AES-256 for long term secrets. 64 bit blocks collide after about 2<sup>32</sup> blocks (Sweet32).'],
    'Cryptography 1.3 covers hash functions in depth, message authentication codes, and how to store passwords safely.')}
{files('Three tasks: PKCS 7 padding, checking and removing padding, and multiplying by 2 in GF(2<sup>8</sup>).')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In symmetric encryption, the sender and receiver use', ['Different keys', 'The same secret key', 'No key', 'A public key'], 1, 'Symmetric means the same.', 'Both sides share one secret key.')
K.quiz('e', 'What is the AES block size?', ['64 bits', '128 bits', '256 bits', 'Any size'], 1, 'Always the same for AES.', 'AES always uses 128 bit blocks. Only the key size varies.')
K.quiz('e', 'How many rounds does AES-128 use?', ['8', '10', '12', '14'], 1, '128 bits: 10, 192: 12, 256: 14.', 'AES-128 has 10 rounds.')
K.quiz('e', 'Why is ECB mode unsafe?', ['It is slow', 'Identical plaintext blocks give identical ciphertext blocks', 'It needs a long key', 'It cannot decrypt'], 1, 'Think of the penguin.', 'Patterns in the data stay visible.')
K.quiz('m', 'In GF(2<sup>8</sup>), what is {57} + {83}?', ['{da}', '{d4}', '{c1}', '{140}'], 1, 'Addition is XOR.', '0x57 XOR 0x83 = 0xd4.')
K.quiz('m', 'Which AES step is the only non linear one?', ['ShiftRows', 'MixColumns', 'SubBytes', 'AddRoundKey'], 2, 'The S-box.', 'SubBytes uses inversion in GF(2<sup>8</sup>), which is non linear.')
K.quiz('m', 'CBC decryption of block i is', ['D(C<sub>i</sub>)', 'D(C<sub>i</sub>) XOR C<sub>i&minus;1</sub>', 'C<sub>i</sub> XOR IV', 'E(C<sub>i</sub>)'], 1, 'Undo the chain.', 'Encryption XORed with C<sub>i&minus;1</sub> before E, so XOR it after D.')
K.quiz('m', 'A 13 byte message with PKCS 7 and 16 byte blocks ends with', ['13 zero bytes', '03 03 03', '0D 0D 0D', '10 repeated 16 times'], 1, '16 &minus; 13.', 'Three bytes of value 3.')
K.quiz('m', 'What does the GCM tag protect?', ['Only the key', 'The ciphertext and the associated data', 'Only the nonce', 'Nothing'], 1, 'Integrity of what was sent.', 'The tag covers ciphertext and associated data, so any change is detected.')
K.quiz('h', 'Two messages are encrypted with AES-CTR, the same key and the same nonce. What leaks?', ['Nothing', 'The XOR of the two plaintexts', 'The key', 'Only the length'], 1, 'Same key stream.', 'C1 XOR C2 = P1 XOR P2, a two time pad.')
K.quiz('h', 'Why was 3DES retired even though 112 bit keys are hard to brute force?', ['It is too fast', 'Its 64 bit blocks collide after about 2<sup>32</sup> blocks (Sweet32)', 'It has no key schedule', 'It is not a block cipher'], 1, 'Block size, not key size.', 'The birthday bound on 64 bit blocks lets long connections leak.')
K.quiz('h', 'A server returns "bad padding" for some CBC ciphertexts and "bad data" for others. This enables', ['A brute force attack', 'A padding oracle attack that decrypts messages', 'Nothing harmful', 'A replay only'], 1, 'Vaudenay 2002.', 'Different errors tell the attacker when padding is valid, which leaks plaintext byte by byte.')
K.quiz('x', 'In the style of a Stanford CS 255 exam: what effective security does AES-128 keep against Grover’s algorithm?', ['128 bits', 'About 64 bits', '32 bits', 'None'], 1, 'Square root of 2<sup>128</sup>.', 'Grover searches N keys in about &radic;N steps, 2<sup>64</sup>.')
K.quiz('x', 'In the style of an MIT 6.857 problem: why does a Feistel network decrypt even when its round function F cannot be inverted?', ['F is always invertible', 'Each round computes L XOR F(R), and XOR with the same F(R) undoes it, so F is only ever evaluated', 'Decryption uses a different key', 'It does not decrypt'], 1, 'Look at what each round changes.', 'A round maps (L, R) to (R, L XOR F(R)). Knowing R you recompute F(R) and XOR again.')

K.calc('e', 'What is the AES block size in bits?', '128', 'Same for every key size.', ['AES fixes the block.', 'It is 16 bytes.', eq('16 &times; 8 = 128 bits')], check=16 * 8)
K.calc('e', 'How many rounds does AES-256 use?', '14', '10, 12, 14.', ['AES-128: 10.', 'AES-192: 12.', eq('AES-256: 14')], check=14)
K.calc('e', 'In GF(2<sup>8</sup>), what is {57} + {83}? Answer in hex, two digits.', 'd4', 'XOR.', ['0x57 = 0101 0111.', '0x83 = 1000 0011.', eq('XOR = 1101 0100 = d4')], check=format(0x57 ^ 0x83, '02x'))
K.calc('m', 'xtime({57}): multiply 0x57 by 2 in GF(2<sup>8</sup>). Answer in hex.', 'ae', 'Bit 7 of 0x57 is 0.', ['0x57 &laquo; 1 = 0xae.', 'No 9th bit, no reduction.', eq('= ae')], check=format(_gm(0x57, 2), '02x'))
K.calc('m', 'PKCS 7 padding for a 13 byte message with 16 byte blocks: how many padding bytes?', '3', 'N = 16 &minus; (L mod 16).', ['13 mod 16 = 13.', '16 &minus; 13 = 3.', eq('3 bytes, each 0x03')], check=16 - 13 % 16)
K.calc('m', 'PKCS 7 padding for a 32 byte message: how many padding bytes?', '16', 'Padding is never zero.', ['32 mod 16 = 0.', '16 &minus; 0 = 16.', eq('a whole extra block of 16 bytes')], check=16 - 32 % 16)
K.calc('m', 'DES with 9 &times; 10<sup>10</sup> keys per second. Average days to find the key (half of 2<sup>56</sup>), rounded?', '5', '2<sup>55</sup> / speed.', ['2<sup>55</sup> &asymp; 3.6 &times; 10<sup>16</sup>.', 'Divide by 9 &times; 10<sup>10</sup>: about 400,000 seconds.', eq('400,000 / 86,400 &asymp; 4.6, about 5 days')], check=round(2 ** 55 / 9e10 / 86400))
K.calc('h', 'What is {57} &middot; {83} in GF(2<sup>8</sup>)? Answer in hex.', 'c1', '{83} = 128 + 2 + 1.', ['{57}&middot;2 = ae, &middot;4 = 47, &middot;8 = 8e, &middot;16 = 07, &middot;32 = 0e, &middot;64 = 1c, &middot;128 = 38.', '{57}&middot;{83} = 38 &oplus; ae &oplus; 57.', eq('= c1')], check=format(_gm(0x57, 0x83), '02x'))
K.calc('h', 'How many 16 byte blocks does CTR need for a 1 MiB (2<sup>20</sup> byte) message?', '65536', 'Divide by 16.', ['2<sup>20</sup> bytes.', '16 = 2<sup>4</sup> bytes per block.', eq('2<sup>16</sup> = 65,536 blocks')], check=2 ** 20 // 16)
K.calc('h', 'Sweet32: 64 bit blocks collide after about 2<sup>32</sup> blocks. How many GiB is that?', '32', '8 bytes per block.', ['2<sup>32</sup> &times; 8 bytes = 2<sup>35</sup> bytes.', '1 GiB = 2<sup>30</sup> bytes.', eq('2<sup>35</sup> / 2<sup>30</sup> = 32 GiB')], check=2 ** 32 * 8 // 2 ** 30)
K.calc('x', 'In the style of an IIT Madras cryptography problem: MixColumns on the column d4 bf 5d 30. Top output byte = 2&middot;d4 &oplus; 3&middot;bf &oplus; 5d &oplus; 30. Answer in hex.', '04', '2&middot;d4: bit 7 set, so reduce.', ['2&middot;d4 = 1a8 &oplus; 11b = b3.', '3&middot;bf = 2&middot;bf &oplus; bf = 65 &oplus; bf = da.', eq('b3 &oplus; da &oplus; 5d &oplus; 30 = 04')], check=format(_gm(0xd4, 2) ^ _gm(0xbf, 3) ^ 0x5d ^ 0x30, '02x'))

K.assign('pad', 'e', 'PKCS 7 padding',
         '<p>Write <code>pad(data, size)</code> that adds N bytes of value N, where N = size &minus; (len(data) mod size). N is never 0.</p>',
         '''
def pad(data, size):
    # your code here
    pass
''', [('pad(b"HELLO", 8).hex()', '48454c4c4f030303'), ('len(pad(b"12345678", 8))', 16), ('pad(b"", 4).hex()', '04040404')],
         '''
def pad(data, size):
    n = size - len(data) % size
    return data + bytes([n]) * n
''', 'Compute n with %, then add bytes([n]) * n.', '<p>A message that already fills its last block still gets a full block of padding, so unpad never has to guess.</p>')
K.assign('unpad', 'm', 'Check and remove padding',
         '<p>Write <code>unpad(data, size)</code>. Read N from the last byte. Return the data without padding if 1 &le; N &le; size and the last N bytes all equal N. Otherwise return None.</p>',
         '''
def unpad(data, size):
    # your code here
    pass
''', [('unpad(bytes.fromhex("48454c4c4f030303"), 8)', 'HELLO'), ('unpad(bytes.fromhex("48454c4c4f030302"), 8)', None), ('unpad(bytes.fromhex("4142434400000000"), 8)', None)],
         '''
def unpad(data, size):
    n = data[-1]
    if n < 1 or n > size:
        return None
    if data[-n:] != bytes([n]) * n:
        return None
    return data[:-n].decode()
''', 'Check the range of N first, then compare the tail with bytes([n]) * n.', '<p>In a real system, never tell the sender which check failed. Different answers for bad padding and bad data are exactly the padding oracle.</p>')
K.assign('xtime', 'm', 'Multiply by 2 in GF(2<sup>8</sup>)',
         '<p>Write <code>xtime(a)</code> for a byte a: shift left by one bit, and if the result has bit 8 set (it is 256 or more), XOR it with 0x11B.</p>',
         '''
def xtime(a):
    # your code here
    pass
''', [('xtime(0x57)', 0xae), ('xtime(0xae)', 0x47), ('xtime(0x80)', 0x1b), ('xtime(0)', 0)],
         '''
def xtime(a):
    a = a << 1
    if a & 0x100:
        a = a ^ 0x11B
    return a
''', 'Shift with a << 1, test bit 8 with a & 0x100, and reduce with ^ 0x11B.', '<p>These are the FIPS 197 values: {57}&middot;2 = {ae} and {57}&middot;4 = {47}. Every AES multiplication is built from this one step.</p>')

K.must('AES', '128 bit block. Keys 128, 192, 256 bits with 10, 12, 14 rounds. SubBytes, ShiftRows, MixColumns, AddRoundKey. Last round no MixColumns.')
K.must('GF(2<sup>8</sup>)', 'Add = XOR. xtime: shift left, XOR 0x11B on overflow. {57}+{83} = {d4}, {57}&middot;{83} = {c1}. Inverse = a<sup>254</sup>.')
K.must('Modes', 'ECB leaks patterns. CBC: C<sub>i</sub> = E(P<sub>i</sub> &oplus; C<sub>i&minus;1</sub>), random IV. CTR: P<sub>i</sub> &oplus; E(N &#8214; i), unique nonce.')
K.must('Padding', 'PKCS 7: N bytes of value N, N = 16 &minus; L mod 16, never 0. Padding oracles decrypt CBC.')
K.must('AEAD', 'AES-GCM or ChaCha20-Poly1305. 96 bit nonce, 16 byte tag. Never reuse a nonce. TLS 1.3 allows only AEAD.')
K.must('Sizes', 'Brute force 2<sup>n&minus;1</sup>. Grover 2<sup>n/2</sup>. Block collisions after 2<sup>b/2</sup> blocks (Sweet32 on 64 bit blocks).')

T = K.topic(
    slug='cy-aes', topic='cy-aes', step=(1, 'Classical and symmetric cryptography', 'cy-c1', 'From Caesar to AES: how ciphers were broken, how modern block ciphers work, and how hashes and MACs protect data.', 'Intermediate'),
    title='Symmetric encryption: AES, GF(2⁸) and modes of operation', short='AES and modes', badge='1.2', minutes=75,
    lead='How modern symmetric encryption works: block ciphers from DES to AES, the field GF(2⁸) behind the S-box, the AES round step by step on real FIPS 197 numbers, ECB, CBC and CTR modes, PKCS 7 padding and the padding oracle, authenticated encryption with AES-GCM and ChaCha20-Poly1305, and key and block sizes against brute force, Grover and the birthday bound.',
    desc='symmetric encryption, block cipher, DES, 3DES, AES, Rijndael, GF(2^8), finite field, xtime, S-box, SubBytes, ShiftRows, MixColumns, AddRoundKey, key schedule, FIPS 197, modes of operation, ECB penguin, CBC, CTR, GCM, XTS, IV, nonce, Feistel network, PKCS 7 padding, padding oracle, POODLE, AEAD, AES-GCM, ChaCha20-Poly1305, nonce reuse, brute force, Grover, birthday bound, Sweet32',
    summary='GF(2⁸), the AES round, ECB, CBC and CTR, padding oracles, AES-GCM and key sizes.',
    keywords=['AES', 'GF(2^8)', 'S-box', 'ECB', 'CBC', 'CTR', 'GCM', 'padding oracle', 'ChaCha20', 'Grover'],
    recap='<p>AES itself is safe. Real failures come from the mode, the nonce and missing integrity: use an AEAD with unique nonces.</p>',
    added='2026-11-14')
