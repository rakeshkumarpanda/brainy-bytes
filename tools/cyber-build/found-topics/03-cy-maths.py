# Foundations 1.3: the maths for security. Checked against Katz and Lindell, Introduction to Modern Cryptography
# (3rd edition, 2020) appendix A (birthday bound), Shannon, "A Mathematical Theory of Communication" (1948),
# RFC 4648 (Base16, Base32, Base64), RFC 3629 (UTF-8), NIST SP 800-63B (memorised secrets) and Axelsson, "The
# Base-Rate Fallacy and the Difficulty of Intrusion Detection", ACM TISSEC 3(3) 2000.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq, frac, sqrt
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk

chapter('cy-maths')
K = Kit()

K.code('to_binary', r'''
# Turn a number into binary by dividing by 2 and keeping the remainders
number = 202
n = number
remainders = []
while n > 0:
    remainders.append(n % 2)     # the remainder is the next bit (from the right)
    n = n // 2

bits = ""
for r in reversed(remainders):   # read the remainders from the bottom up
    bits = bits + str(r)
print(number, "in binary is", bits)
print("Python agrees:", bin(number), hex(number))

# A character is stored as a number too
for ch in "Hi!":
    code = ord(ch)
    print(ch, "->", code, "->", format(code, "08b"), "-> hex", format(code, "02X"))
''')

K.code('xor_cipher', r'''
# XOR every byte of a message with a key byte. Doing it twice gives the message back.
message = "HELLO"
key = "K"

secret = []
for i in range(len(message)):
    m = ord(message[i])
    k = ord(key[i % len(key)])   # repeat the key if it is shorter
    secret.append(m ^ k)         # ^ is XOR in Python
print("encrypted bytes:", secret)
print("as hex:", " ".join(format(b, "02X") for b in secret))

back = ""
for i in range(len(secret)):
    k = ord(key[i % len(key)])
    back = back + chr(secret[i] ^ k)
print("decrypted:", back)

# The three rules that make this work
a = 0b1011
print(a ^ a, "(a xor a is 0)")
print(a ^ 0, "(a xor 0 is a)")
''')

K.code('mod_clock', r'''
# Modular arithmetic: count on a clock with n positions
print("15 mod 12 =", 15 % 12)        # 15:00 is 3 o'clock
print("-3 mod 26 =", -3 % 26)        # Python gives a positive answer
print("(7 + 9) mod 10 =", (7 + 9) % 10)
print("(7 x 9) mod 10 =", (7 * 9) % 10)

# The rules: you may take mod at every step and the answer is the same
a, b, n = 1234, 5678, 97
print((a * b) % n, "==", ((a % n) * (b % n)) % n)

# Caesar shift: each letter moves 3 places on a clock of 26 letters
word = "ATTACK"
shift = 3
out = ""
for ch in word:
    position = ord(ch) - ord("A")             # A=0, B=1, ... Z=25
    out = out + chr((position + shift) % 26 + ord("A"))
print(word, "->", out)
''')

K.code('key_space', r'''
# How many passwords exist, and how long does trying them all take?
guesses_per_second = 1_000_000_000      # an assumed attacker speed: one billion guesses each second
seconds_per_year = 365 * 24 * 3600

choices = [
    ("4 digit PIN", 10, 4),
    ("8 lowercase letters", 26, 8),
    ("8 characters from 95 keyboard symbols", 95, 8),
    ("12 characters from 95 keyboard symbols", 95, 12),
]
for name, symbols, length in choices:
    space = symbols ** length
    worst = space / guesses_per_second               # seconds to try every one
    print(name, "| space", space, "| worst case", round(worst / seconds_per_year, 6), "years")

# Each extra bit of key doubles the work
print("2 ** 128 keys =", 2 ** 128)
''')

K.code('birthday', r'''
import math

# Chance that at least two of k people share a birthday (365 days)
def shared(k, days=365):
    all_different = 1.0
    for i in range(k):
        all_different = all_different * (days - i) / days
    return 1 - all_different

for k in [10, 23, 50, 70]:
    print(k, "people ->", round(shared(k), 4))

# The quick formula: about 1.1774 x sqrt(N) tries give a 50% chance of a repeat
N = 365
print("50% point estimate:", round(1.1774 * math.sqrt(N), 1))

# For a hash with b bits there are N = 2 ** b values. About 2 ** (b / 2) tries find a collision.
for b in [32, 64, 128, 256]:
    print(b, "bit hash -> about 2 **", b // 2, "tries for a collision")
''')

K.code('bayes_alert', r'''
# An intrusion detector catches 99% of attacks and wrongly flags 1% of normal events.
# Only 10 in 10,000 events are attacks. If it raises an alarm, how likely is a real attack?
events = 10000
attacks = 10
normal = events - attacks

detection_rate = 0.99
false_alarm_rate = 0.01

true_alarms = attacks * detection_rate
false_alarms = normal * false_alarm_rate
print("true alarms:", true_alarms)
print("false alarms:", false_alarms)
print("P(attack | alarm) =", round(true_alarms / (true_alarms + false_alarms), 4))

# The same with Bayes rule written with probabilities
p_attack = attacks / events
p_alarm = detection_rate * p_attack + false_alarm_rate * (1 - p_attack)
print("Bayes rule gives  ", round(detection_rate * p_attack / p_alarm, 4))
''')

K.code('entropy', r'''
import math
import random

# Shannon entropy: the average number of bits of surprise per symbol
def entropy(data):
    counts = {}
    for symbol in data:
        counts[symbol] = counts.get(symbol, 0) + 1
    total = len(data)
    h = 0.0
    for c in counts.values():
        p = c / total
        h = h - p * math.log2(p)
    return h

print("aaaaaaaa      ->", round(entropy("aaaaaaaa"), 3), "bits per symbol")
print("abababab      ->", round(entropy("abababab"), 3))
print("english text  ->", round(entropy("the quick brown fox jumps over the lazy dog"), 3))

random.seed(3)
noise = [random.randrange(256) for i in range(4096)]
print("random bytes  ->", round(entropy(noise), 3), "(the most is 8 bits per byte)")

# Strength of a random password: length x log2(number of symbols)
print("random 12 char password from 95 symbols:", round(12 * math.log2(95), 1), "bits")
''', long=True)

K.code('base64_demo', r'''
import base64
import math

# Base64 turns any bytes into 64 safe text characters. Every 3 bytes become 4 characters.
data = "Hi!".encode()
text = base64.b64encode(data).decode()
print(data, "->", text)
print("back:", base64.b64decode(text))

for n in [1, 2, 3, 10, 100]:
    print(n, "bytes ->", 4 * math.ceil(n / 3), "Base64 characters")

# Base64 is an ENCODING, not encryption: anyone can decode it
print(base64.b64decode("cGFzc3dvcmQxMjM=").decode())
''')

K.lesson('bits', 'Bits, bytes, binary and hex', f'''
{talk('Every photo, password and message on a computer is stored as a long row of tiny switches that are either off or on. We write off as zero and on as one, and each switch is called a bit, short for binary digit. Eight bits make a byte, which can hold 256 different values, enough for one letter of the English alphabet. Security people read bytes all day long: in network packets, in malware files, in encryption keys. Writing eight zeros and ones for every byte is slow and easy to misread, so we use hexadecimal, base sixteen, where one byte is always exactly two symbols. When you see something like zero x C A, that is just the number 202 written in hex. In this lesson you will learn to switch between decimal, binary and hex by hand, so these strings never scare you again.')}
{src('RFC 4648 for Base64, RFC 3629 for UTF-8, and Katz and Lindell, Introduction to Modern Cryptography.')}
{wwh('A <b>bit</b> is a single 0 or 1. A <b>byte</b> is 8 bits and holds a value from 0 to 255. <b>Binary</b> writes numbers in base 2, <b>hexadecimal</b> (hex) in base 16 with the digits 0 to 9 and A to F.',
     'Keys, hashes, packets and files are all bytes. To read a hash, spot a malware signature or understand a key length, you must be at home with bits and hex.',
     'Each binary place is worth double the one to its right: 1, 2, 4, 8, 16 and so on. To convert to binary, divide by 2 again and again and read the remainders from the bottom up. To convert binary to hex, cut the bits into groups of four, because 2<sup>4</sup> = 16.')}
{viz('cybinary')}
{run('to_binary')}
{table(['Decimal', 'Binary', 'Hex', 'Where you meet it'], [
    ['0', '0000 0000', '00', 'An empty byte'],
    ['65', '0100 0001', '41', 'The letter A in ASCII'],
    ['127', '0111 1111', '7F', 'The largest value of a signed byte'],
    ['202', '1100 1010', 'CA', 'Any byte in a key or hash'],
    ['255', '1111 1111', 'FF', 'The largest byte. Also 255.255.255.0 in network masks']])}
{fxs(fx('Value of a binary number', 'b<sub>n&minus;1</sub>&middot;2<sup>n&minus;1</sup> + ... + b<sub>1</sub>&middot;2 + b<sub>0</sub>', 'Each bit b times its place value. 1100 1010 = 128 + 64 + 8 + 2 = 202.', key=True),
     fx('How many values n bits can hold', '2<sup>n</sup> values, from 0 to 2<sup>n</sup> &minus; 1', '8 bits: 256 values. 32 bits: about 4.3 billion. 128 bits: about 3.4 &times; 10<sup>38</sup>.', key=True),
     fx('Digits needed', 'one hex digit = 4 bits, one byte = 2 hex digits', 'A 256 bit hash is written as 64 hex characters.'))}
<p>Text is bytes too. <b>ASCII</b> (1963) gives each English character a number from 0 to 127. <b>Unicode</b> gives every character in every language a number, and <b>UTF-8</b> stores it in 1 to 4 bytes: English letters take 1 byte, most Indian scripts 3 bytes. Many security bugs come from programs that confuse characters with bytes.</p>
{run('base64_demo')}
{fxs(fx('Base64 length', 'characters = 4 &times; &lceil;n / 3&rceil;', 'n is the number of bytes. Every 3 bytes (24 bits) become 4 characters of 6 bits each. Padding with = fills the last group.'))}
{note('Base64 and hex are encodings, not encryption. Anyone can decode them in one line. Attackers often hide data in Base64 hoping a human reviewer will not look closely.', 'warn')}
''', kw=['bit', 'byte', 'binary', 'hexadecimal', 'hex', 'ASCII', 'Unicode', 'UTF-8', 'Base64', 'encoding', 'place value'])

K.lesson('xor', 'XOR: the most important operation in cryptography', f'''
{talk('If cryptography had a favourite operation, it would be XOR, which means exclusive or. It takes two bits and answers one simple question: are they different? If yes, the answer is one. If they are the same, the answer is zero. That sounds too simple to be useful, but XOR has a magic property: doing it twice with the same key brings back exactly what you started with. In 1917 an engineer at AT and T named Gilbert Vernam used this idea to encrypt teleprinter messages with a paper tape of random key. Later, Claude Shannon proved that if the key is truly random, as long as the message, and never used again, nobody can ever break it. That is the one time pad. Today XOR is inside AES, inside stream ciphers, inside hashes and inside checksums.')}
{wwh('<b>XOR</b> (exclusive or, written ⊕ or ^) outputs 1 when its two input bits differ and 0 when they match. On bytes, it works on each of the 8 bit pairs separately.',
     'XOR is fast, it undoes itself, and if one input is random the output is random too. This makes it the basic mixing step of almost every cipher.',
     'To encrypt, XOR the message with a key: c = m ⊕ k. To decrypt, XOR again with the same key: c ⊕ k = m ⊕ k ⊕ k = m. The key bits decide which message bits get flipped.')}
{viz('cyxor')}
{run('xor_cipher')}
{table(['a', 'b', 'a AND b', 'a OR b', 'a XOR b'], [['0', '0', '0', '0', '0'], ['0', '1', '0', '1', '1'], ['1', '0', '0', '1', '1'], ['1', '1', '1', '1', '0']])}
{fxs(fx('XOR rules', 'a ⊕ 0 = a &nbsp;&nbsp; a ⊕ a = 0 &nbsp;&nbsp; a ⊕ b = b ⊕ a &nbsp;&nbsp; (a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)', 'Together these give (m ⊕ k) ⊕ k = m, so XOR with the same key decrypts.', key=True),
     fx('XOR is addition without carry', 'a ⊕ b = (a + b) mod 2', 'For single bits. This is why XOR is "addition" in the field of two elements used inside AES.'))}
{steps('Worked example: why reusing an XOR key is fatal', [
    'Two messages m<sub>1</sub> and m<sub>2</sub> are encrypted with the same key k: c<sub>1</sub> = m<sub>1</sub> ⊕ k and c<sub>2</sub> = m<sub>2</sub> ⊕ k.',
    'An eavesdropper XORs the two ciphertexts: c<sub>1</sub> ⊕ c<sub>2</sub> = m<sub>1</sub> ⊕ k ⊕ m<sub>2</sub> ⊕ k.',
    eq('c<sub>1</sub> ⊕ c<sub>2</sub> = m<sub>1</sub> ⊕ m<sub>2</sub>'),
    'The key has vanished. The attacker now has the XOR of two real messages, and guessing a common word in one reveals the same spot in the other.',
    'This is why a one time pad key must be used only once. Soviet messages that reused pad pages were partly read by the US Venona project.'])}
''', kw=['XOR', 'exclusive or', 'truth table', 'one time pad', 'Vernam', 'key reuse', 'stream cipher'])

K.lesson('mod', 'Modular arithmetic: maths on a clock', f'''
{talk('You already know modular arithmetic, because you read clocks. If it is ten o’clock and you wait five hours, it is three o’clock, not fifteen o’clock. The numbers wrap around after twelve. Mathematicians write this as fifteen mod twelve equals three. The great German mathematician Carl Friedrich Gauss wrote the rules down in 1801, and almost two hundred years later these same rules became the base of RSA, Diffie Hellman and elliptic curve cryptography. The reason is beautiful. Some sums are easy one way on a clock, but very hard to undo, like mixing paint. Here we learn the basic rules. The Cryptography section builds the full number theory on top of them.')}
{wwh('<b>a mod n</b> is the remainder when a is divided by n. Working "mod n" means every result wraps around into the range 0 to n &minus; 1, like the hours on a clock.',
     'Computers have fixed size numbers, so arithmetic wraps naturally. More importantly, public key cryptography is built on operations that are easy mod n but hard to reverse, such as powers mod n.',
     'Add, subtract and multiply as normal, then take the remainder. You can take mod after every step and get the same final answer, which keeps the numbers small.')}
{run('mod_clock')}
{fxs(fx('Definition', 'a mod n = r, where a = q &middot; n + r and 0 &le; r &lt; n', 'q is the whole number quotient, r the remainder.', key=True),
     fx('Rules', '(a + b) mod n = ((a mod n) + (b mod n)) mod n <br>(a &times; b) mod n = ((a mod n) &times; (b mod n)) mod n', 'So big products never need to be computed in full.', key=True),
     fx('Congruence', 'a ≡ b (mod n) means n divides a &minus; b', '17 ≡ 5 (mod 12), because 12 divides 12.'),
     fx('Caesar cipher', 'c = (m + k) mod 26 &nbsp;&nbsp; m = (c &minus; k) mod 26', 'Letters A to Z as 0 to 25, shifted by the key k.'))}
{steps('Worked example: a big power mod a small number, without big numbers', [
    'Find 7<sup>4</sup> mod 10.',
    '7<sup>2</sup> = 49, and 49 mod 10 = 9.',
    '7<sup>4</sup> = (7<sup>2</sup>)<sup>2</sup>, so take 9<sup>2</sup> = 81.',
    eq('81 mod 10 = 1, so 7<sup>4</sup> mod 10 = 1'),
    'Check: 7<sup>4</sup> = 2401, which ends in 1. Squaring and reducing at each step is the "square and multiply" method RSA uses on numbers with hundreds of digits.'])}
{note('In maths and Python, &minus;3 mod 26 = 23. In C and Java, &minus;3 % 26 gives &minus;3. Many cipher bugs come from negative remainders.', 'warn')}
''', kw=['modular arithmetic', 'mod', 'remainder', 'congruence', 'clock arithmetic', 'Caesar', 'square and multiply', 'Gauss'])

K.lesson('count', 'Counting keys and passwords: how big is big enough?', f'''
{talk('How long would it take to guess your password by trying every possibility? This question is called brute force, and the answer is just counting. If a lock has four dials with ten digits each, there are ten times ten times ten times ten, ten thousand combinations. A thief trying one per second needs under three hours. Every extra dial multiplies the work by ten. Computer keys work the same way, except that each extra bit doubles the work. Cryptographers today want at least 128 bits of security. Two to the power 128 is so large that if every computer on Earth tried keys for the age of the universe, they would still not finish. Counting tells us when a secret is long enough, and why short passwords fall in minutes.')}
{wwh('The <b>key space</b> is the number of possible keys or passwords. With an alphabet of N symbols and length L, it is N<sup>L</sup>. Its size in bits is L &times; log<sub>2</sub> N.',
     'A cipher is only as strong as its key space allows. If the key space is small, an attacker simply tries every key. Counting tells us how long that takes.',
     'Count the possibilities, divide by the attacker’s guessing speed. On average the right key is found halfway through, so the expected time is half the worst case.')}
{run('key_space')}
{fxs(fx('Key space', 'N<sup>L</sup>', 'N symbols, length L. A 4 digit PIN: 10<sup>4</sup> = 10,000.', key=True),
     fx('Bits of strength', 'bits = log<sub>2</sub>(N<sup>L</sup>) = L &times; log<sub>2</sub> N', '12 random keyboard symbols: 12 &times; log<sub>2</sub> 95 &asymp; 78.8 bits.', key=True),
     fx('Brute force time', 'worst = space / rate &nbsp;&nbsp; average = space / (2 &times; rate)', 'Rate is guesses per second.'),
     fx('Doubling rule', '2<sup>n+1</sup> = 2 &times; 2<sup>n</sup>', 'One more bit doubles the work. Ten more bits multiply it by 1024.'))}
{scene('the 4 digit phone PIN', '<p>A phone PIN has 10,000 possibilities. A computer could try them all in a blink. Phones stay safe because of a different control: after a few wrong tries they make you wait, and some can wipe themselves. This limits the attacker to maybe a few guesses an hour. Security often combines a small key space with a rate limit. Without the rate limit, the PIN would be useless.</p>')}
{note('These counts assume random choices. Human passwords are not random: "Password@123" is in every attacker’s list. Real strength depends on how the password was chosen, not just its length.', 'warn')}
''', kw=['key space', 'brute force', 'password strength', 'bits of security', 'combinatorics', 'rate limit', '128 bit'])

K.lesson('prob', 'Probability traps: the birthday paradox and the base rate', f'''
{talk('Two puzzles from probability shape security more than almost any others. The first is the birthday paradox. In a class of only 23 students, there is a better than even chance that two share a birthday. It feels wrong because we compare ourselves with others, but the question is about any pair, and 23 students make 253 pairs. In cryptography, this means a hash with 128 bits of output can be broken for collisions with only about two to the power 64 tries, not two to the power 128. The second puzzle is the base rate fallacy. In 2000 the Swedish researcher Stefan Axelsson showed that an intrusion detector that is right 99 percent of the time can still raise mostly false alarms, simply because real attacks are so rare. Both puzzles are about thinking carefully before trusting your gut.')}
{fxs(fx('Birthday bound (exact)', 'P(repeat) = 1 &minus; (N/N)((N&minus;1)/N)...((N&minus;k+1)/N)', 'k tries, N possible values.'),
     fx('Birthday bound (quick)', 'P(repeat) &asymp; 1 &minus; e<sup>&minus;k<sup>2</sup>/(2N)</sup> &nbsp;&nbsp; 50% at k &asymp; 1.1774 ' + sqrt('N'), 'For a b bit hash, N = 2<sup>b</sup>, so about 2<sup>b/2</sup> tries find a collision.', key=True),
     fx('Bayes rule', 'P(attack | alarm) = ' + frac('P(alarm | attack) P(attack)', 'P(alarm)'), 'P(alarm) = P(alarm | attack) P(attack) + P(alarm | normal) P(normal).', key=True))}
{run('birthday')}
<p>Now the base rate trap. Press <b>Step</b> to send 10,000 events through a detector, then move the sliders.</p>
{viz('cybayes')}
{run('bayes_alert')}
{steps('Worked example: an alarm from a 99% accurate detector', [
    'Base rate: 1 attack per 1,000 events, P(attack) = 0.001. Detection rate 0.99, false alarm rate 0.01.',
    'P(alarm) = 0.99 &times; 0.001 + 0.01 &times; 0.999 = 0.00099 + 0.00999 = 0.01098.',
    eq('P(attack | alarm) = 0.00099 / 0.01098 &asymp; 0.090'),
    'Only about 9% of alarms are real attacks. Analysts would chase 10 false alarms for every real one.',
    'Cutting the false alarm rate to 0.001 gives 0.00099 / (0.00099 + 0.000999) &asymp; 0.50. Reducing false alarms helped far more than raising detection could.'])}
{note('When someone says a detector is "99% accurate", always ask: how rare is the thing it detects, and what is its false alarm rate? Without the base rate, accuracy means little.', 'exam')}
''', kw=['birthday paradox', 'birthday bound', 'collision', 'base rate fallacy', 'Bayes rule', 'false positive', 'intrusion detection', 'Axelsson'])

K.lesson('entropy', 'Entropy: measuring surprise and randomness', f'''
{talk('In 1948 Claude Shannon, working at Bell Labs, published a paper that started information theory. He asked how to measure information, and his answer was surprise. If I tell you the sun rose this morning, you learn almost nothing. If I tell you it snowed in Chennai, you learn a lot. Shannon turned this into a formula called entropy, measured in bits. For security, entropy answers two practical questions. How unpredictable is a password or a key? And does a file look random? Encrypted and compressed data look almost perfectly random, with close to eight bits of entropy per byte. Malware analysts use this to spot packed or encrypted parts of a suspicious program, and network defenders use it to spot data being smuggled out.')}
{wwh('<b>Shannon entropy</b> is the average surprise of a symbol, in bits. If one symbol is certain, entropy is 0. If all N symbols are equally likely, entropy is the largest possible, log<sub>2</sub> N.',
     'It measures how hard a secret is to guess and whether data looks random. A key with low entropy can be guessed, however long it looks.',
     'Count how often each symbol appears, turn the counts into probabilities p, and add up &minus;p log<sub>2</sub> p over every symbol.')}
{run('entropy')}
{fxs(fx('Shannon entropy', 'H = &minus; &Sigma; p<sub>i</sub> log<sub>2</sub> p<sub>i</sub>', 'Sum over every symbol i with probability p<sub>i</sub>. Units: bits per symbol.', key=True),
     fx('Maximum entropy', 'H<sub>max</sub> = log<sub>2</sub> N', 'All N symbols equally likely. For bytes N = 256, so at most 8 bits per byte.'),
     fx('Entropy of a random secret', 'H = L &times; log<sub>2</sub> N', 'L symbols chosen uniformly at random from N. A random 4 word passphrase from a 7,776 word list: 4 &times; 12.9 &asymp; 51.7 bits.'))}
{deep('Min entropy, the measure cryptographers really use', '<p>Shannon entropy is an average. An attacker cares about the <b>most likely</b> guess. Min entropy is H<sub>&infin;</sub> = &minus;log<sub>2</sub>(max p<sub>i</sub>). If a password scheme gives "123456" with probability 1/100, its min entropy is only log<sub>2</sub> 100 &asymp; 6.6 bits, however many other passwords are possible. Random number generators for keys (NIST SP 800-90B) are assessed with min entropy for exactly this reason.</p>')}
''', kw=['entropy', 'Shannon', 'information theory', 'randomness', 'min entropy', 'password entropy', 'passphrase', 'packed malware'])

K.lesson('versus', 'Encoding, encryption and hashing compared', f'''
{talk('Three words are mixed up so often that they cause real security failures: encoding, encryption and hashing. All three turn data into something that looks different, so beginners treat them as the same thing. They are not. Encoding, like Base64 or hex, just changes the format so data travels safely, and anyone can reverse it. Encryption hides data with a key, and only someone with the key can reverse it. Hashing makes a fixed size fingerprint that cannot be reversed at all, and is used to check that data has not changed or to store passwords. Companies have leaked millions of passwords because a developer thought Base64 was encryption. After this lesson you will never make that mistake.')}
{versus('Encoding, encryption and hashing', ['', 'Encoding', 'Encryption', 'Hashing'], [
    ['Purpose', 'Change format so data can travel or be shown', 'Keep data secret', 'Make a fingerprint to check integrity or store passwords'],
    ['Needs a key?', 'No', 'Yes', 'No (a keyed hash, HMAC, uses one)'],
    ['Reversible?', 'Yes, by anyone', 'Yes, only with the key', 'No, one way'],
    ['Output size', 'Grows with input (Base64 adds about a third)', 'About the same as the input', 'Always the same size (SHA-256: 256 bits)'],
    ['Examples', 'Base64, hex, URL encoding, UTF-8', 'AES, ChaCha20, RSA', 'SHA-256, SHA-3, bcrypt for passwords'],
    ['Protects', 'Nothing', 'Confidentiality', 'Integrity']],
    'Encoding is for transport, encryption is for secrecy, hashing is for fingerprints. Never use encoding to protect anything.')}
{table(['Maths tool', 'Where it is used later in this subject'], [
    ['Binary and hex', 'Reading packets, hashes, keys and malware'],
    ['XOR', 'One time pad, stream ciphers, AES, CBC and CTR modes'],
    ['Modular arithmetic', 'Caesar and Vigenère ciphers, RSA, Diffie-Hellman, elliptic curves, TOTP codes'],
    ['Counting and powers of 2', 'Key lengths, password policy, brute force estimates'],
    ['Birthday bound', 'Hash collisions, nonce reuse, why 64 bit blocks are too small'],
    ['Bayes rule', 'Intrusion detection, SIEM alert tuning, spam filters'],
    ['Entropy', 'Password strength, random number generators, packed malware detection']])}
''', kw=['encoding vs encryption vs hashing', 'Base64 is not encryption', 'comparison', 'where maths is used'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('The maths in this chapter grows with you. At school you count combinations and convert numbers to binary. At college you use modular arithmetic, XOR and Bayes rule to reason about ciphers and detectors. At masters level you meet groups and fields, the algebra that makes AES and elliptic curves work, and you use probability bounds to prove that an attack needs a certain number of tries. At research level, security proofs measure an attacker’s advantage as a function of the number of queries, and these bounds decide exact key and block sizes in modern standards. Do not worry if the top levels feel far away. Each later chapter climbs one more step.')}
{ladder(
    '<p>Computers store everything as 0s and 1s. Hex is a short way to write them. XOR flips bits where the key has a 1, and doing it twice undoes it. Longer passwords have many more possibilities.</p>',
    '<p>Convert between bases, use mod n rules, compute key spaces as N<sup>L</sup> and bits as L log<sub>2</sub> N, apply the birthday bound 2<sup>b/2</sup> for collisions, and Bayes rule for alert accuracy.</p>',
    '<p>The integers mod n form a ring, and mod a prime p they form a field where every non zero number has an inverse. XOR on bytes is addition in GF(2<sup>8</sup>), the field inside AES. The birthday bound comes from 1 &minus; e<sup>&minus;k(k&minus;1)/(2N)</sup>, and min entropy measures guessing resistance.</p>',
    '<p>Provable security bounds an adversary’s advantage, for example q<sup>2</sup>/2<sup>n</sup> for a block cipher modelled as a random permutation after q queries (the PRP to PRF switching lemma). Such birthday type bounds are why 64 bit block ciphers fell to the Sweet32 attack (2016) and why modes limit how much data one key may encrypt.</p>')}
{grow('Convert numbers to binary and hex, use XOR, and count possible passwords.',
      'Do mod n arithmetic, compute bits of strength, apply the birthday bound and Bayes rule, and compute entropy.',
      'Work in finite fields, use min entropy, and read birthday type advantage bounds in security proofs.')}
''', kw=['beginner', 'expert', 'finite field', 'GF(2^8)', 'advantage', 'Sweet32', 'switching lemma'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A byte is 8 bits (0 to 255). Convert to binary by repeated division by 2, to hex by groups of 4 bits. One byte = 2 hex digits.',
    '<b>Encoding</b> (Base64, hex, UTF-8) is not encryption. Base64 makes 4 characters from every 3 bytes.',
    '<b>XOR</b>: 1 when bits differ. a ⊕ a = 0 and a ⊕ 0 = a, so (m ⊕ k) ⊕ k = m. Reusing an XOR key leaks m<sub>1</sub> ⊕ m<sub>2</sub>.',
    '<b>a mod n</b> is the remainder. You may reduce mod n after every step. Caesar: c = (m + k) mod 26.',
    'Key space N<sup>L</sup>, strength L log<sub>2</sub> N bits, average brute force time = space / (2 &times; rate). Each bit doubles the work.',
    '<b>Birthday bound</b>: about 2<sup>b/2</sup> tries find a collision in a b bit hash. 23 people give a 50% chance of a shared birthday.',
    '<b>Base rate</b>: P(attack | alarm) = TP / (TP + FP). Rare attacks make most alarms false, so false alarm rate matters most.',
    '<b>Entropy</b> H = &minus;&Sigma; p log<sub>2</sub> p. Random bytes are near 8 bits per byte, a sign of encryption or packing.'],
    'Foundations 2.1 shows how operating systems keep users apart: accounts, permissions, processes and the octal maths of chmod.')}
{files('Three tasks: a number to binary by hand, XOR of two byte lists, and the Shannon entropy of a string.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'How many different values can one byte hold?', ['8', '128', '256', '1024'], 2, '2 to the power 8.', '2<sup>8</sup> = 256 values, from 0 to 255.')
K.quiz('e', 'What is 1 XOR 1?', ['0', '1', '2', '11'], 0, 'Same bits.', 'XOR gives 0 when the bits match.')
K.quiz('e', 'What is 17 mod 5?', ['2', '3', '5', '12'],0, 'Remainder.', '17 = 3 &times; 5 + 2.')
K.quiz('e', 'Base64 is', ['A strong encryption method', 'An encoding anyone can reverse', 'A hash function', 'A password manager'], 1, 'No key.', 'Base64 only changes the format. Anyone can decode it.')
K.quiz('m', 'The hex number FF equals', ['15', '16', '255', '256'], 2, '15 &times; 16 + 15.', 'F = 15, so 15 &times; 16 + 15 = 255.')
K.quiz('m', 'Why does XOR with the same key decrypt?', ['XOR is slow', 'Because k ⊕ k = 0 and m ⊕ 0 = m', 'Because XOR is a hash', 'It does not'], 1, 'Two rules together.', '(m ⊕ k) ⊕ k = m ⊕ (k ⊕ k) = m ⊕ 0 = m.')
K.quiz('m', 'How many possible 6 digit PINs are there?', ['60', '10<sup>6</sup>', '6<sup>10</sup>', '2<sup>6</sup>'], 1, 'N<sup>L</sup>.', '10 choices for each of 6 places: 10<sup>6</sup>.')
K.quiz('m', 'Adding 10 random bits to a key multiplies brute force work by about', ['10', '20', '100', '1024'], 3, '2<sup>10</sup>.', 'Each bit doubles the work: 2<sup>10</sup> = 1024.')
K.quiz('m', 'About how many tries find a collision in a 64 bit hash?', ['2<sup>64</sup>', '2<sup>32</sup>', '64', '2<sup>8</sup>'], 1, 'Birthday bound.', 'About 2<sup>b/2</sup> = 2<sup>32</sup>.')
K.quiz('h', 'A detector catches 99% of attacks with a 1% false alarm rate. Attacks are 1 in 10,000 events. An alarm is most likely', ['A real attack', 'A false alarm', 'Exactly 99% likely to be real', 'Impossible to judge'], 1, 'Compare TP and FP.', 'TP &asymp; 0.99, FP &asymp; 100 per 10,000 events, so about 1% of alarms are real.')
K.quiz('h', 'A file section has entropy 7.98 bits per byte. It is most likely', ['Plain English text', 'Encrypted or compressed data', 'All zeros', 'A list of names'], 1, 'Maximum is 8.', 'Near 8 bits per byte means the bytes look random, as encrypted or compressed data does.')
K.quiz('h', 'Two ciphertexts were made with the same XOR key. XORing them gives', ['The key', 'm<sub>1</sub> ⊕ m<sub>2</sub>', 'Zero', 'Random noise with no information'], 1, 'The key cancels.', 'c<sub>1</sub> ⊕ c<sub>2</sub> = m<sub>1</sub> ⊕ m<sub>2</sub>, which leaks both messages.')
K.quiz('x', 'In the style of an MIT 6.875 problem: what is the min entropy of a password scheme where the most common password has probability 1/1024?', ['1024 bits', '10 bits', '32 bits', '0 bits'], 1, '&minus;log<sub>2</sub> of the max probability.', '&minus;log<sub>2</sub>(1/1024) = 10 bits.')
K.quiz('x', 'In the style of a Stanford CS255 problem: a 64 bit block cipher in CBC mode starts to leak when two cipher blocks collide. After roughly how much data with one key does this become likely?', ['About 2<sup>64</sup> blocks', 'About 2<sup>32</sup> blocks (about 32 GB)', 'About 64 blocks', 'Never'], 1, 'Birthday bound on 64 bit blocks.', '2<sup>32</sup> blocks of 8 bytes is 32 GiB. This is the Sweet32 attack on 3DES and Blowfish.')

K.calc('e', 'Convert the binary number 1010 to decimal.', '10', 'Place values 8, 4, 2, 1.', ['1 &times; 8 = 8.', '0 &times; 4 + 1 &times; 2 + 0 &times; 1 = 2.', eq('8 + 2 = 10')], check=0b1010)
K.calc('e', 'What is 23 mod 7?', '2', 'Remainder after dividing.', ['7 &times; 3 = 21.', '23 &minus; 21 = 2.', eq('23 mod 7 = 2')], check=23 % 7)
K.calc('e', 'How many possible 3 letter codes use only A to Z?', '17576', '26<sup>3</sup>.', ['26 choices for each place.', '26 &times; 26 = 676.', eq('676 &times; 26 = 17,576')], check=26 ** 3)
K.calc('m', 'What is 202 XOR 75 (as a decimal number)?', '129', 'Write both in binary first.', ['202 = 1100 1010, 75 = 0100 1011.', 'XOR bit by bit: 1000 0001.', eq('1000 0001 = 128 + 1 = 129')], check=202 ^ 75)
K.calc('m', 'Convert hex 0x3C to decimal.', '60', '3 &times; 16 + 12.', ['3 &times; 16 = 48.', 'C = 12.', eq('48 + 12 = 60')], check=0x3C)
K.calc('m', 'How many Base64 characters encode 10 bytes?', '16', '4 &times; ceil(10 / 3).', ['10 / 3 = 3.33, round up to 4 groups.', 'Each group is 4 characters.', eq('4 &times; 4 = 16')], check=4 * -(-10 // 3))
K.calc('m', 'How many bits of strength has a random 8 character password from 64 symbols?', '48', 'L &times; log<sub>2</sub> N.', ['log<sub>2</sub> 64 = 6.', 'L = 8.', eq('8 &times; 6 = 48 bits')], check=8 * 6)
K.calc('h', 'What is the Shannon entropy of the string "aabb" in bits per symbol?', '1', 'Two symbols, each with p = 0.5.', ['p(a) = p(b) = 0.5.', 'H = &minus;2 &times; 0.5 &times; log<sub>2</sub> 0.5.', eq('H = 1 bit')], check=1.0)
K.calc('h', 'A detector has detection rate 0.9 and false alarm rate 0.05. Attacks are 100 of 10,000 events. What share of alarms are real? Round to 4 decimal places.', '0.1538', 'TP / (TP + FP).', ['TP = 100 &times; 0.9 = 90.', 'FP = 9,900 &times; 0.05 = 495.', eq('90 / 585 &asymp; 0.1538')], check=round(90 / (90 + 9900 * 0.05), 4))
K.calc('h', 'Use the quick birthday formula: roughly how many random 32 bit IDs give a 50% chance of a repeat? Round to the nearest whole number.', '77163', '1.1774 &times; &radic;(2<sup>32</sup>).', ['&radic;(2<sup>32</sup>) = 2<sup>16</sup> = 65,536.', '1.1774 &times; 65,536 = 77,162.1.', eq('&asymp; 77,162 to 77,163')], check=77163, tol=2)
K.calc('x', 'In the style of an IIT CS6xx problem: compute 3<sup>13</sup> mod 7 with square and multiply.', '3', '13 = 8 + 4 + 1.', ['3<sup>1</sup> = 3, 3<sup>2</sup> = 9 ≡ 2, 3<sup>4</sup> ≡ 4, 3<sup>8</sup> ≡ 16 ≡ 2 (mod 7).', '3<sup>13</sup> = 3<sup>8</sup> &times; 3<sup>4</sup> &times; 3<sup>1</sup> ≡ 2 &times; 4 &times; 3 = 24.', eq('24 mod 7 = 3')], check=pow(3, 13, 7))

K.assign('binary', 'e', 'A number to binary by hand',
         '<p>Write <code>to_binary(n)</code> that returns the binary digits of a whole number n as a string, using repeated division by 2 (do not use <code>bin()</code>). <code>to_binary(0)</code> returns "0".</p>',
         '''
def to_binary(n):
    # your code here
    pass
''', [('to_binary(202)', '11001010'), ('to_binary(0)', '0'), ('to_binary(1)', '1'), ('to_binary(255)', '11111111')],
         '''
def to_binary(n):
    if n == 0:
        return "0"
    bits = ""
    while n > 0:
        bits = str(n % 2) + bits
        n = n // 2
    return bits
''', 'Take n % 2 for the next bit and put it in FRONT of the string, then n // 2. Stop when n is 0.', '<p>This is the same repeated division the animation shows. Reading the remainders from the bottom up is the same as putting each new bit at the front.</p>')
K.assign('xor', 'e', 'XOR two byte lists',
         '<p>Write <code>xor_bytes(data, key)</code>. data and key are lists of numbers from 0 to 255. Return a new list where each data byte is XORed with a key byte, repeating the key when it is shorter.</p>',
         '''
def xor_bytes(data, key):
    # your code here
    pass
''', [('xor_bytes([72, 73], [75])', [3, 2]), ('xor_bytes([1, 2, 3], [1, 2, 3])', [0, 0, 0]), ('xor_bytes(xor_bytes([10, 20, 30], [7, 9]), [7, 9])', [10, 20, 30])],
         '''
def xor_bytes(data, key):
    out = []
    for i in range(len(data)):
        out.append(data[i] ^ key[i % len(key)])
    return out
''', 'Loop over the positions. Use i % len(key) to pick the key byte, and ^ for XOR.', '<p>The third test shows that XOR twice with the same key returns the data. A repeating key like this is weak, as you will see in the Cryptography section, but every stream cipher uses this XOR step.</p>')
K.assign('entropy', 'm', 'Shannon entropy of a string',
         '<p>Write <code>entropy(text)</code> that returns the Shannon entropy of the characters in text, in bits per character, rounded to 3 decimal places. Use <code>math.log2</code>.</p>',
         '''
import math

def entropy(text):
    # your code here
    pass
''', [('entropy("aaaa")', 0.0), ('entropy("aabb")', 1.0), ('entropy("abcd")', 2.0), ('entropy("aab")', 0.918)],
         '''
import math

def entropy(text):
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    h = 0.0
    for c in counts.values():
        p = c / len(text)
        h = h - p * math.log2(p)
    return round(abs(h), 3)
''', 'Count each character in a dict, turn counts into probabilities, add up &minus;p log<sub>2</sub> p.', '<p>Analysts run exactly this over chunks of a file. Chunks near 8 bits per byte are probably encrypted or compressed, which in a program often means hidden malware code.</p>')

K.must('Bits and hex', 'Byte = 8 bits = 0 to 255 = 2 hex digits. n bits hold 2<sup>n</sup> values. Encoding (Base64, hex) is not encryption.')
K.must('XOR', '1 when bits differ. (m ⊕ k) ⊕ k = m. Same key twice leaks m<sub>1</sub> ⊕ m<sub>2</sub>.')
K.must('Mod', 'a mod n = remainder. Reduce after every step. Caesar c = (m + k) mod 26.')
K.must('Counting', 'Key space N<sup>L</sup>, strength L log<sub>2</sub> N bits. Each bit doubles brute force work.')
K.must('Birthday and Bayes', 'Collisions after about 2<sup>b/2</sup> tries. P(attack | alarm) = TP / (TP + FP): rare attacks make most alarms false.')
K.must('Entropy', 'H = &minus;&Sigma; p log<sub>2</sub> p. Max log<sub>2</sub> N. Random or encrypted bytes are near 8 bits per byte.')

T = K.topic(
    slug='cy-maths', topic='cy-maths', step=(1, 'Start here', 'cy-f1', 'What security protects and from whom, how risk is measured, and the maths every security decision uses.', 'Beginner'),
    title='The maths for security: bits, XOR, mod, counting, probability and entropy', short='Maths for security', badge='1.3', minutes=65,
    lead='Learn the maths every later chapter uses: binary, hex and Base64, XOR and why it undoes itself, modular arithmetic on a clock, key spaces and brute force, the birthday paradox, the base rate trap with Bayes rule, and Shannon entropy.',
    desc='bits, bytes, binary, hexadecimal, ASCII, Unicode, UTF-8, Base64, XOR truth table and rules, one time pad, key reuse, modular arithmetic, congruence, Caesar cipher, square and multiply, key space, brute force time, bits of strength, birthday paradox and bound, hash collisions, base rate fallacy, Bayes rule, intrusion detection alerts, Shannon entropy, min entropy, encoding vs encryption vs hashing, finite fields, Sweet32.',
    summary='binary and hex, XOR, modular arithmetic, key spaces, the birthday bound, the base rate trap and entropy.',
    keywords=['binary', 'hex', 'XOR', 'modular arithmetic', 'key space', 'brute force', 'birthday paradox', 'Bayes rule', 'base rate', 'entropy'],
    recap='<p>Bits and hex to read data, XOR and mod to build ciphers, counting to size keys, and probability to judge collisions and alarms.</p>',
    added='2026-11-14')
