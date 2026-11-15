# Cryptography 1.1: classical ciphers and how they were broken. Checked against Katz and Lindell, Introduction to
# Modern Cryptography (3rd edition, chapters 1 and 2), Stinson and Paterson, Cryptography Theory and Practice (4th
# edition, chapter 2), Shannon, Communication Theory of Secrecy Systems (1949), Kahn, The Codebreakers, and NSA's
# public history of the Venona project.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-classical')
K = Kit()

K.code('caesar_brute', r'''
# The Caesar cipher, and breaking it by trying every key
ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def caesar(text, k):
    out = ""
    for ch in text:
        if ch in ABC:
            out = out + ABC[(ABC.index(ch) + k) % 26]
        else:
            out = out + ch            # spaces and punctuation stay as they are
    return out

secret = caesar("MEET AT THE OLD BRIDGE", 3)
print("ciphertext:", secret)
print("decrypted :", caesar(secret, -3))

print("Brute force, all 26 keys:")
for k in range(26):
    print(k, caesar(secret, -k))
''', long=True)

K.code('freq_break', r'''
# Let the computer pick the Caesar key: the shift whose letter counts look most like English
ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ENGLISH = [8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4,
           6.7, 7.5, 1.9, 0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074]

def shift(text, k):
    out = ""
    for ch in text:
        out = out + ABC[(ABC.index(ch) + k) % 26]
    return out

def chi_squared(text):
    score = 0
    for i in range(26):
        observed = text.count(ABC[i])
        expected = ENGLISH[i] / 100 * len(text)
        score = score + (observed - expected) ** 2 / expected
    return score

cipher = "AOLZLJBYPAFVMHZFZALTZOVBSKKLWLUKVUSFVUAOLZLJYLJFVMAOLRLF"
best_k, best_score = 0, None
for k in range(26):
    score = chi_squared(shift(cipher, -k))
    if best_score is None or score < best_score:
        best_k, best_score = k, score

print("best key:", best_k, " score:", round(best_score, 1))
print("message :", shift(cipher, -best_k))
''', long=True)

K.code('vigenere_break', r'''
# Break a Vigenere cipher: find the key length with the index of coincidence, then each letter with chi-squared
ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ENGLISH = [8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4,
           6.7, 7.5, 1.9, 0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074]

def vigenere(text, key, sign):           # sign +1 encrypts, -1 decrypts
    out = ""
    for i in range(len(text)):
        p = ABC.index(text[i])
        k = ABC.index(key[i % len(key)])
        out = out + ABC[(p + sign * k) % 26]
    return out

def coincidence(text):                   # chance that two letters picked at random are equal
    total = 0
    for letter in ABC:
        n = text.count(letter)
        total = total + n * (n - 1)
    return total / (len(text) * (len(text) - 1))

def chi_squared(text):
    score = 0
    for i in range(26):
        expected = ENGLISH[i] / 100 * len(text)
        score = score + (text.count(ABC[i]) - expected) ** 2 / expected
    return score

def best_shift(column):
    best, best_score = 0, None
    for k in range(26):
        score = chi_squared(vigenere(column, ABC[k], -1))
        if best_score is None or score < best_score:
            best, best_score = k, score
    return best

plain = ("THESECURITYOFASYSTEMSHOULDDEPENDONLYONTHESECRECYOFTHEKEYANDNOTONTHESECRECYOFTHEMETHOD"
         "THISIDEAWASWRITTENDOWNBYAUGUSTEKERCKHOFFSINEIGHTEENEIGHTYTHREEANDITISSTILLTHEFIRSTRULE"
         "OFMODERNCRYPTOGRAPHYATTACKERSWILLLEARNHOWYOURSYSTEMWORKSSOONERORLATERBECAUSEPROGRAMS"
         "AREOFTENSTOLENORREVERSEDANDPEOPLETALKTHEONLYTHINGTHATMUSTSTAYSECRETISTHESMALLKEYWHICH"
         "YOUCANCHANGEQUICKLYIFITISEVERLEAKEDTOANATTACKER")
cipher = vigenere(plain, "CIPHER", 1)    # the attacker sees only this

best_m, best_ic = 1, 0
for m in range(1, 9):
    total = 0
    for i in range(m):
        total = total + coincidence(cipher[i::m])
    average = total / m
    print("key length", m, "average IC", round(average, 4))
    if average > best_ic:
        best_m, best_ic = m, average

key = ""
for i in range(best_m):
    key = key + ABC[best_shift(cipher[i::best_m])]
print("key length:", best_m, " key:", key)
print("message starts:", vigenere(cipher, key, -1)[:40])
''', long=True)

K.code('otp_xor', r'''
# The one time pad with XOR, and why a pad must never be used twice
import secrets

def xor(a, b):
    out = []
    for i in range(len(a)):
        out.append(a[i] ^ b[i])
    return bytes(out)

p1 = b"ATTACK AT DAWN"
p2 = b"RETREAT AT TEN"
pad = secrets.token_bytes(len(p1))       # truly random, as long as the message

c1 = xor(p1, pad)
print("c1 (looks random):", c1.hex())
print("decrypt c1       :", xor(c1, pad))

# The mistake: the same pad for a second message
c2 = xor(p2, pad)
print("c1 XOR c2 == p1 XOR p2:", xor(c1, c2) == xor(p1, p2))   # the pad cancels out

# If the attacker can guess p1, they get p2 without ever seeing the pad
print("attacker recovers p2:", xor(xor(c1, c2), p1))
''', long=True)

K.code('keyspace_maths', r'''
# How big are the key spaces, and how many letters does an attacker need?
import math

caesar_keys = 26
affine_keys = 0
for a in range(26):
    if math.gcd(a, 26) == 1:
        affine_keys = affine_keys + 26          # every good a with every b
substitution_keys = math.factorial(26)

print("Caesar keys      :", caesar_keys)
print("affine keys      :", affine_keys)
print("substitution keys:", substitution_keys)
bits = math.log2(substitution_keys)
print("that is about 2 to the power", round(bits, 1))

# Unicity distance: letters needed before only one key gives sensible English
redundancy = 3.2                                  # bits per English letter (textbook estimate)
print("unicity distance:", round(bits / redundancy, 1), "letters")

# A computer trying a billion keys per second against the substitution cipher
seconds = substitution_keys / 2 / 1e9
print("brute force years:", "%.1e" % (seconds / (365.25 * 24 * 3600)))
''')

K.lesson('idea', 'Secret writing: the words and the one big rule', f'''
{talk('People have hidden messages for as long as they have written them. Spartan generals wound a strip of leather round a stick of a fixed thickness, called a scytale, and wrote along it. Julius Caesar shifted the letters of his letters. For two thousand years, most ciphers were invented by clever people and broken by cleverer ones. In the ninth century the Arab scholar al-Kindi wrote the first known description of frequency analysis, which broke almost every cipher of his time. In the sixteenth century Mary, Queen of Scots, was executed partly because her cipher letters were broken. In the twentieth century, Polish mathematicians led by Marian Rejewski, and then Alan Turing and the team at Bletchley Park, broke the German Enigma machine, and historians believe this shortened the Second World War. Every one of these stories teaches the same lesson, which the Dutch linguist Auguste Kerckhoffs wrote down in 1883: a cipher must stay secure even if the enemy knows exactly how it works. Only the key may be secret. This chapter shows you the classical ciphers, how each one was broken, and the maths that tells us when a cipher is truly safe.')}
{src('Katz and Lindell, Introduction to Modern Cryptography, Stinson and Paterson, Cryptography Theory and Practice, Shannon (1949), Kahn, The Codebreakers.')}
{wwh('<b>Cryptography</b> is the science of keeping messages secret and unchanged when an enemy can read the channel. A <b>cipher</b> turns <b>plaintext</b> into <b>ciphertext</b> using a <b>key</b>. Decryption turns it back. <b>Cryptanalysis</b> is the science of breaking ciphers.',
     'Every password, bank payment, phone call and message you send relies on encryption. The classical ciphers are broken, but the ways they broke are the same ways modern systems fail.',
     'Encryption E uses key k to turn a message m into c = E<sub>k</sub>(m). Decryption D gives back m = D<sub>k</sub>(c). The design is public. The key is secret, chosen at random from a set of keys called the <b>key space</b>.')}
{table(['Word', 'Meaning', 'Example'], [
    ['Plaintext', 'The readable message', 'ATTACK AT DAWN'],
    ['Ciphertext', 'The scrambled message that travels', 'DWWDFN DW GDZQ'],
    ['Key', 'The small secret that controls the cipher', 'shift 3'],
    ['Key space', 'Every possible key', '26 shifts'],
    ['Brute force', 'Trying every key', '26 tries for Caesar'],
    ['Kerckhoffs’ principle', 'Only the key is secret, never the method', 'AES is public, your key is not']])}
{table(['Attack model', 'What the attacker has', 'Classical example'], [
    ['Ciphertext only', 'Only intercepted ciphertext', 'Frequency analysis on a Caesar message'],
    ['Known plaintext', 'Some plaintext and ciphertext pairs', 'Guessed weather reports in Enigma traffic'],
    ['Chosen plaintext', 'Can encrypt messages of their choice', 'Planting a word to see how it is encrypted'],
    ['Chosen ciphertext', 'Can get chosen ciphertexts decrypted', 'Padding oracle attacks on web servers']])}
{note('Never invent your own cipher for real use. History is full of "unbreakable" home made ciphers broken in days. Use public, studied algorithms such as AES, which this section covers next.', 'warn')}
''', kw=['cryptography', 'cipher', 'plaintext', 'ciphertext', 'key', 'key space', 'brute force', 'Kerckhoffs principle', 'cryptanalysis', 'attack models', 'scytale', 'Enigma', 'al-Kindi'])

K.lesson('caesar', 'The Caesar cipher and modular arithmetic', f'''
{talk('The Roman historian Suetonius tells us that Julius Caesar wrote private letters by replacing each letter with the one three places further along the alphabet. A became D, B became E, and near the end of the alphabet, X wrapped round to A. That wrapping is the first piece of maths every cryptographer learns: arithmetic modulo 26, sometimes called clock arithmetic. On a clock, 3 hours after 11 is 2, not 14. With 26 letters, 3 places after X, which is letter 23, is 26, which wraps to 0, which is A. The Caesar cipher was probably good enough in Rome, because few enemies could read at all. Today it is a toy: there are only 26 possible shifts, so a computer, or a patient child, tries them all. A version called ROT13, a shift of 13, is still used online to hide spoilers, because applying it twice gives the original text.')}
{wwh('The <b>Caesar cipher</b> replaces each letter with the letter k places later, wrapping from Z back to A. The shift k is the key.',
     'It is the simplest example of a key, encryption, decryption and brute force, and it introduces modular arithmetic, which RSA and elliptic curves also use.',
     'Number the letters A = 0 to Z = 25. Encrypt with C = (P + k) mod 26 and decrypt with P = (C &minus; k) mod 26.')}
{viz('cycaesar')}
{fxs(fx('Encrypt', 'C = (P + k) mod 26', 'P and C are letter numbers, A = 0. X (23) with k = 3: 26 mod 26 = 0 = A.', key=True),
     fx('Decrypt', 'P = (C &minus; k) mod 26', 'Python’s % always gives a result from 0 to 25, even for negative numbers: (0 &minus; 3) % 26 = 23.', key=True),
     fx('Mod', 'a mod n = the remainder after dividing a by n', '29 mod 26 = 3, because 29 = 1 &times; 26 + 3.'))}
{run('caesar_brute')}
{note('Exam favourite: the number of Caesar keys is 26 if you count shift 0, and 25 useful ones. On average a brute force finds the key after trying about half of them.', 'exam')}
''', kw=['Caesar cipher', 'shift cipher', 'modular arithmetic', 'mod 26', 'ROT13', 'brute force', 'clock arithmetic'])

K.lesson('freq', 'Substitution ciphers and frequency analysis', f'''
{talk('A smarter idea than shifting is to scramble the whole alphabet. The key is any arrangement of the 26 letters, so A might become Q, B might become M, and so on. The number of possible keys is 26 factorial, about 4 times 10 to the power 26, more than the number of grains of sand on Earth. Nobody can try them all. For centuries people thought this made the cipher unbreakable. But al-Kindi noticed something in the ninth century. In any language, some letters are common and some are rare. In English, E is about 12.7 percent of letters, T about 9 percent, and Z less than a tenth of a percent. A substitution cipher changes the letters but not how often they appear. So the most common ciphertext letter probably stands for E. Then you look at common pairs like TH and common words like THE, and the whole message falls apart like a crossword puzzle. The lesson is deep: a huge key space is necessary, but it is not enough. A cipher must also hide the patterns in the message.')}
{wwh('A <b>monoalphabetic substitution cipher</b> maps each plain letter to one fixed cipher letter. <b>Frequency analysis</b> breaks it by matching letter counts with the known counts of the language.',
     'It proves that a big key space alone does not make a cipher safe. Modern ciphers are designed so that the ciphertext looks random, with no patterns left to count.',
     'Count each ciphertext letter, compare with English, guess the most common letters first, then use common pairs and words to fix the rest. For a Caesar cipher, the chi-squared score picks the shift automatically.')}
{viz('cyfreq')}
{run('freq_break')}
{fxs(fx('Chi-squared score', '&chi;<sup>2</sup> = &Sigma;<sub>i</sub> (O<sub>i</sub> &minus; E<sub>i</sub>)<sup>2</sup> / E<sub>i</sub>', 'O<sub>i</sub> is how often letter i appears, E<sub>i</sub> how often English would have it. The shift with the smallest score wins.', key=True),
     fx('Substitution key space', '26! = 403,291,461,126,605,635,584,000,000 &asymp; 2<sup>88.4</sup>', 'Too many to try, yet frequency analysis needs only a few hundred letters.'))}
{run('keyspace_maths')}
{table(['Cipher', 'Rule', 'Keys', 'Broken by'], [
    ['Caesar', 'C = P + k', '26', 'Try all 26'],
    ['Affine', 'C = aP + b, with a coprime to 26', '12 &times; 26 = 312', 'Try all, or solve from two known letters'],
    ['Substitution', 'Any scrambled alphabet', '26! &asymp; 4 &times; 10<sup>26</sup>', 'Frequency analysis'],
    ['Vigenère', 'A repeating key word of length m', '26<sup>m</sup>', 'Find m, then frequency analysis per column'],
    ['One time pad', 'A random key as long as the message, used once', '26<sup>n</sup>', 'Not breakable, if used correctly']])}
''', kw=['substitution cipher', 'monoalphabetic', 'frequency analysis', 'letter frequency', 'chi-squared', '26 factorial', 'affine cipher', 'al-Kindi'])

K.lesson('vigenere', 'The Vigenère cipher, Kasiski and the index of coincidence', f'''
{talk('To beat frequency analysis, sixteenth century cryptographers used several alphabets in turn. Giovan Battista Bellaso described the method in 1553, but it is named after Blaise de Vigenère, who wrote about a stronger version later. A key word such as LEMON sets the shift for each letter: L shifts the first letter by 11, E the second by 4, and so on, and then the key repeats. Now the letter A in the message turns into different ciphertext letters depending on where it falls, so the counts are smeared out. For three hundred years it was called le chiffre indéchiffrable, the unbreakable cipher. Then Charles Babbage broke it in the 1850s and kept quiet, and Friedrich Kasiski published a method in 1863. The key idea: because the key repeats, letters that are a key length apart are encrypted with the same shift. If you can find the key length, the cipher splits into a few simple Caesar ciphers. In 1922, the American cryptologist William Friedman gave a statistical tool for finding that length, the index of coincidence, which is the chance that two letters picked from a text are the same.')}
{wwh('The <b>Vigenère cipher</b> adds a repeating key word to the message, letter by letter, modulo 26. It is a <b>polyalphabetic</b> cipher because it uses several Caesar alphabets in turn.',
     'It hides single letter frequencies, so plain frequency analysis fails. Breaking it shows a general rule: any repetition in the key is a weakness.',
     'Encrypt with C<sub>i</sub> = (P<sub>i</sub> + K<sub>i mod m</sub>) mod 26. To break it, find the key length m (repeated pieces in the ciphertext appear at distances that are multiples of m, or the index of coincidence jumps at the right m), then break each of the m columns as a Caesar cipher.')}
{viz('cyvigenere')}
{fxs(fx('Vigenère', 'C<sub>i</sub> = (P<sub>i</sub> + K<sub>i mod m</sub>) mod 26', 'm is the key length. Letters m apart use the same key letter.', key=True),
     fx('Index of coincidence', 'IC = &Sigma;<sub>i</sub> n<sub>i</sub>(n<sub>i</sub> &minus; 1) / ( N(N &minus; 1) )', 'n<sub>i</sub> is the count of letter i, N the text length. English text gives about 0.066. Random letters give 1/26 &asymp; 0.038.', key=True),
     fx('Why IC finds m', 'columns at the right m are Caesar ciphers of English, so their IC &asymp; 0.066', 'At a wrong m the columns mix shifts and look random, so IC stays near 0.038.'))}
{run('vigenere_break')}
{note('The program prints an average IC of about 0.063 at key length 6 and about 0.04 for the wrong lengths. Multiples of the real length, such as 12, would also score high, so pick the smallest length that scores high.', 'exam')}
''', kw=['Vigenere', 'polyalphabetic', 'key length', 'Kasiski', 'index of coincidence', 'Friedman', 'Babbage', 'Bellaso', 'repeating key'])

K.lesson('otp', 'The one time pad and perfect secrecy', f'''
{talk('Is any cipher truly unbreakable? Yes, and it is surprisingly simple. In 1917, Gilbert Vernam at AT&T built a teleprinter that combined each character of a message with a character from a paper tape of key. Joseph Mauborgne of the US Army added the crucial rule: the key must be truly random, as long as the message, and never used again. That is the one time pad. In 1949, Claude Shannon, the father of information theory, proved that it gives perfect secrecy: the ciphertext tells an attacker absolutely nothing about the message, no matter how much computing power they have. Every message of the same length is equally possible. But the price is heavy. You need as much secret key as you have messages, and you must deliver it safely in advance. And the rule of never reusing it is absolute. During the Second World War, Soviet pad factories under pressure printed some pages twice. American and British analysts in the Venona project spotted the reuse and, over many years, read thousands of Soviet intelligence messages. A perfect cipher was broken by one human shortcut.')}
{wwh('The <b>one time pad</b> combines the message with a truly random key of the same length, usually with XOR: c = m &oplus; k. The key is used only once and then destroyed.',
     'It is the only cipher proven to be unbreakable, and it explains why modern stream ciphers try to imitate a random pad with a short key.',
     'XOR each message bit with a key bit. Decrypt with the same operation, since (m &oplus; k) &oplus; k = m. If a pad is used twice, c<sub>1</sub> &oplus; c<sub>2</sub> = m<sub>1</sub> &oplus; m<sub>2</sub>, the key disappears, and guessing parts of one message reveals the other.')}
{run('otp_xor')}
{fxs(fx('Perfect secrecy (Shannon)', 'P(M = m | C = c) = P(M = m)', 'Seeing the ciphertext does not change the attacker’s belief about any message.', key=True),
     fx('Shannon’s key size bound', '|K| &ge; |M|', 'Perfect secrecy needs at least as many keys as messages. So the key must be as long as the message.', key=True),
     fx('Two time pad', 'c<sub>1</sub> &oplus; c<sub>2</sub> = (m<sub>1</sub> &oplus; k) &oplus; (m<sub>2</sub> &oplus; k) = m<sub>1</sub> &oplus; m<sub>2</sub>', 'The pad cancels. A guessed word in one message gives the matching letters of the other (crib dragging).'))}
{deep('Why the one time pad is perfect: a short proof', '<p>Take any message m and ciphertext c of n bits. Exactly one key gives c from m, namely k = m &oplus; c. Every key has probability 2<sup>&minus;n</sup>. So P(C = c | M = m) = 2<sup>&minus;n</sup> for every m, which does not depend on m. By Bayes’ rule, P(M = m | C = c) = P(C = c | M = m) P(M = m) / P(C = c) = P(M = m), because P(C = c) is also 2<sup>&minus;n</sup>. The ciphertext changes nothing.</p>')}
{scene('the Venona decrypts', '<p>In 1943 the US Army’s Signal Intelligence Service began studying thousands of coded Soviet telegrams. Analyst Richard Hallock noticed that some messages had been encrypted with pad pages already used for other messages. Using that reuse, a small team including Meredith Gardner slowly recovered parts of about 3,000 messages over almost 40 years, revealing Soviet spies inside the atomic bomb project. NSA released the Venona translations to the public in 1995.</p>')}
''', kw=['one time pad', 'Vernam', 'XOR', 'perfect secrecy', 'Shannon', 'two time pad', 'key reuse', 'Venona', 'crib dragging'])

K.lesson('entropy', 'The maths of breaking: key space, redundancy and unicity distance', f'''
{talk('Shannon’s 1949 paper did more than prove the one time pad perfect. It gave a way to measure how much ciphertext an attacker needs to break a cipher. The idea starts with redundancy. English is very predictable: after Q almost always comes U, and after TH comes E very often. Shannon estimated that English carries only about one to one and a half bits of real information per letter, even though a random letter could carry log two of 26, about 4.7 bits. The rest, around 3.2 bits per letter, is redundancy, and redundancy is what an attacker uses to tell a right key from a wrong one. If the key has H bits of uncertainty, then after about H divided by 3.2 letters of ciphertext, only one key will give sensible English. This number is called the unicity distance. For the simple substitution cipher, with about 88 bits of key, that is only about 28 letters. Below that, many keys give sensible text, and even a perfect attacker cannot be sure. Above it, the message is determined, and the only question is how much work finding it takes.')}
{wwh('The <b>key space</b> size sets the brute force cost. <b>Redundancy</b> is how predictable a language is. The <b>unicity distance</b> is roughly how much ciphertext is needed before only one key makes sense.',
     'These numbers tell you whether an attack is possible in principle (enough ciphertext) and practical (small enough key space or a shortcut).',
     'Key entropy H(K) = log<sub>2</sub>(number of keys) for a random key. English redundancy D &asymp; 3.2 bits per letter. Unicity distance U &asymp; H(K) / D.')}
{fxs(fx('Key entropy', 'H(K) = log<sub>2</sub> |K|', 'Caesar: log<sub>2</sub> 26 &asymp; 4.7 bits. Substitution: log<sub>2</sub> 26! &asymp; 88.4 bits. AES-128: 128 bits.', key=True),
     fx('Redundancy of English', 'D = log<sub>2</sub> 26 &minus; H<sub>English</sub> &asymp; 4.7 &minus; 1.5 = 3.2 bits per letter', 'A common textbook estimate. Shannon measured 0.6 to 1.3 bits for H<sub>English</sub> with long context.'),
     fx('Unicity distance', 'U &asymp; H(K) / D', 'Substitution: 88.4 / 3.2 &asymp; 28 letters. Caesar: 4.7 / 3.2 &asymp; 1.5 letters, so two letters already pin down the key.', key=True),
     fx('Brute force time', 'average time = |K| / (2 &times; speed)', 'Half the key space on average. 2<sup>128</sup> keys at 10<sup>12</sup> per second still needs about 5 &times; 10<sup>18</sup> years.'))}
{steps('How to judge a cipher', [
    'Count the keys: if a computer can try them all, it is broken.',
    'Look for patterns that survive encryption: letter counts, repeated blocks, repeated keys.',
    'Ask how much ciphertext the attacker gets compared with the unicity distance.',
    'Check the attack models: can the attacker choose plaintexts or get ciphertexts decrypted.',
    'Prefer ciphers whose security has been studied publicly for years.'])}
''', kw=['key space', 'entropy', 'redundancy', 'unicity distance', 'Shannon', 'brute force time', 'information theory', 'bits'])

K.lesson('versus', 'Classical ciphers compared', f'''
{talk('Lined up side by side, the classical ciphers show how cryptography grew up. Each new cipher fixed the weakness that broke the one before. Caesar had too few keys, so substitution added more keys. Substitution kept letter counts, so Vigenère used several alphabets. Vigenère repeated its key, so the one time pad used a key that never repeats. But the pad was too heavy to use widely. Machines like Enigma tried to get the best of both: a short key setting that produced a very long, non repeating stream of alphabets. The army Enigma, with three rotors and ten plugboard cables, had about 1.6 times 10 to the power 20 daily settings, yet it fell to a mix of mathematics, captured material, operator mistakes and the electromechanical bombes. Modern ciphers like AES take the final step. They are built so that, without the key, the output cannot be told apart from random, even when the attacker chooses the inputs.')}
{versus('From Caesar to the one time pad', ['', 'Caesar', 'Substitution', 'Vigenère', 'One time pad', 'Modern (AES)'], [
    ['Key', 'One shift', 'A scrambled alphabet', 'A short word, repeated', 'Random, as long as the message', '128 or 256 random bits'],
    ['Key space', '26', '2<sup>88</sup>', '26<sup>m</sup>', '26<sup>n</sup> (or 2<sup>n</sup> bits)', '2<sup>128</sup> or 2<sup>256</sup>'],
    ['Hides letter counts', 'No', 'No', 'Partly', 'Yes', 'Yes'],
    ['Broken by', 'Trying 26 keys', 'Frequency analysis', 'Key length, then frequencies', 'Nothing, unless the pad is reused', 'No practical attack known'],
    ['Practical', 'Very', 'Very', 'Yes', 'No: huge keys to share', 'Yes']],
    'Each step fixed the last weakness. The one time pad is perfect but impractical. Modern ciphers trade perfect secrecy for computational security: breaking them is possible in theory, but would take longer than the age of the universe.')}
''', kw=['comparison', 'Caesar vs Vigenere', 'one time pad vs AES', 'Enigma', 'computational security'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Classical cryptography is the gateway to the whole subject. A beginner learns the words and why short keys fail. A college student can break Caesar and Vigenère with code and explain frequency analysis and the index of coincidence. A masters student understands Shannon’s perfect secrecy proof, entropy and unicity distance, and the jump to modern security definitions, where we prove that no efficient attacker can tell the ciphertexts of two chosen messages apart. Researchers go further. Modern cryptography rests on reductions: a proof that breaking the cipher would solve a problem believed to be hard. And historians of cryptography still find new things. In 2023 a team of codebreakers decrypted more than fifty letters written in cipher by Mary, Queen of Scots, that had sat unread in the French national library for centuries.')}
{ladder(
    '<p>A cipher scrambles a message with a key. Caesar shifts letters and has only 26 keys, so anyone can try them all. Counting letters breaks more complex letter swaps.</p>',
    '<p>Use C = (P + k) mod 26, break Caesar by brute force or chi-squared, break substitution by frequency analysis, break Vigenère with the index of coincidence and per column analysis, and explain why one time pads must never be reused.</p>',
    '<p>Prove the one time pad perfectly secret and the bound |K| &ge; |M|. Use entropy, redundancy and unicity distance. Move to computational security: indistinguishability under chosen plaintext attack (IND-CPA), where an efficient attacker must not tell apart encryptions of two messages they choose, with advantage only negligibly above 1/2.</p>',
    '<p>Reduction proofs link a scheme’s security to hard problems. Pseudorandom generators stretch a short key into a long pad, and stream cipher security is defined by indistinguishability from a truly random string. Historical cryptanalysis continues with computer search: in 2023 Lasry, Biermann and Tomokiyo decrypted 57 letters of Mary, Queen of Scots, found in the Bibliothèque nationale de France.</p>')}
{grow('Explain keys, ciphertext and why Caesar is weak.',
      'Break Caesar, substitution and Vigenère with code, and explain the one time pad and its reuse failure.',
      'Prove perfect secrecy, compute unicity distance and state IND-CPA security.')}
''', kw=['beginner', 'expert', 'IND-CPA', 'computational security', 'reduction', 'pseudorandom generator', 'Mary Queen of Scots'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A cipher turns plaintext into ciphertext with a key. <b>Kerckhoffs</b>: the method is public, only the key is secret.',
    '<b>Caesar</b>: C = (P + k) mod 26. Only 26 keys, so brute force breaks it at once.',
    '<b>Substitution</b> has 26! &asymp; 2<sup>88</sup> keys but keeps letter counts, so <b>frequency analysis</b> breaks it. &chi;<sup>2</sup> = &Sigma; (O &minus; E)<sup>2</sup> / E scores how English a text looks.',
    '<b>Vigenère</b>: C<sub>i</sub> = (P<sub>i</sub> + K<sub>i mod m</sub>) mod 26. Find m with Kasiski or the <b>index of coincidence</b> (English &asymp; 0.066, random &asymp; 0.038), then break each column.',
    'The <b>one time pad</b> (c = m &oplus; k, random key as long as the message, used once) has <b>perfect secrecy</b>: P(M | C) = P(M). It needs |K| &ge; |M|.',
    'Reusing a pad gives c<sub>1</sub> &oplus; c<sub>2</sub> = m<sub>1</sub> &oplus; m<sub>2</sub>. Venona read Soviet messages this way.',
    'Unicity distance U &asymp; H(K) / D with D &asymp; 3.2 bits per English letter. Substitution: about 28 letters.',
    'A big key space is necessary but not enough. A good cipher must also leave no patterns.'],
    'Cryptography 1.2 moves to modern symmetric ciphers: block ciphers, AES and its rounds, and the modes that make a block cipher safe for long messages.')}
{files('Three tasks: a Caesar cipher that keeps spaces, Vigenère decryption, and XOR of two byte strings.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is the key in a Caesar cipher?', ['The alphabet', 'The shift', 'The message length', 'The first letter'], 1, 'What changes between users?', 'The shift (for example 3) is the secret key.')
K.quiz('e', 'Kerckhoffs’ principle says that', ['The method must be secret', 'Only the key needs to be secret', 'Keys should be short', 'Ciphers should change daily'], 1, 'What may the enemy know?', 'A good cipher stays safe even if the enemy knows the method.')
K.quiz('e', 'Which letter is most common in English text?', ['A', 'E', 'T', 'S'], 1, 'About 12.7%.', 'E is about 12.7% of English letters.')
K.quiz('e', 'With Caesar shift 3, what does X become?', ['A', 'Z', 'B', 'Y'], 0, '23 + 3 = 26.', '26 mod 26 = 0 = A.')
K.quiz('m', 'Why does a substitution cipher with 26! keys still fall quickly?', ['Computers try all keys', 'It keeps the letter frequencies of the language', 'The key is printed on the message', 'It only works on short texts'], 1, 'What survives encryption?', 'Letter counts survive, so frequency analysis matches them to English.')
K.quiz('m', 'What weakness of Vigenère do Kasiski and the index of coincidence use?', ['The alphabet is public', 'The key repeats every m letters', 'It uses XOR', 'It needs long keys'], 1, 'Repetition.', 'Letters m apart share a key letter, so the cipher splits into m Caesar ciphers.')
K.quiz('m', 'What index of coincidence does English text have, roughly?', ['0.038', '0.066', '0.5', '1.0'], 1, 'Higher than random.', 'English is about 0.066, random letters about 1/26 = 0.038.')
K.quiz('m', 'One time pad: c = m XOR k. How do you decrypt?', ['c XOR k', 'c minus k', 'c AND k', 'You cannot'], 0, 'XOR undoes itself.', '(m XOR k) XOR k = m.')
K.quiz('m', 'How many keys does the affine cipher C = aP + b mod 26 have?', ['26', '312', '676', '26!'], 1, 'a must be coprime to 26.', '12 good values of a times 26 values of b = 312.')
K.quiz('h', 'Two messages were encrypted with the same one time pad. What does c1 XOR c2 give?', ['The key', 'm1 XOR m2', 'Nothing useful', 'm1 + m2'], 1, 'The pad cancels.', '(m1 XOR k) XOR (m2 XOR k) = m1 XOR m2.')
K.quiz('h', 'Perfect secrecy means', ['The cipher is fast', 'P(M = m | C = c) = P(M = m) for every m and c', 'The key is 128 bits', 'Nobody knows the method'], 1, 'The ciphertext changes nothing.', 'Seeing c does not change the probability of any message.')
K.quiz('h', 'Average IC per column is 0.041 at m = 5, 0.063 at m = 6 and 0.062 at m = 12. The key length is most likely', ['5', '6', '12', '18'], 1, 'Multiples score high too.', 'Pick the smallest length with an English like IC. 12 is a multiple of 6.')
K.quiz('x', 'In the style of a Stanford CS 255 exam: Shannon proved perfect secrecy requires', ['|K| &ge; |M|', '|K| = 2', 'A public key', 'A 128 bit key'], 0, 'Count keys and messages.', 'Every message must be reachable from each ciphertext, so there are at least as many keys as messages.')
K.quiz('x', 'In the style of an MIT 6.857 problem: the unicity distance of simple substitution on English is about', ['2 letters', '28 letters', '1,000 letters', 'Infinite'], 1, 'H(K) / D = 88.4 / 3.2.', '88.4 bits divided by about 3.2 bits of redundancy per letter is about 28 letters.')

K.calc('e', 'Caesar shift 3: which letter does X become? Answer the letter.', 'A', 'X is 23.', ['X = 23.', '23 + 3 = 26.', eq('26 mod 26 = 0 = A')], check='ABCDEFGHIJKLMNOPQRSTUVWXYZ'[(23 + 3) % 26])
K.calc('e', 'How many Caesar keys are there, counting shift 0?', '26', 'One per letter.', ['Shifts 0 to 25.', 'Count them.', eq('26 keys')], check=26)
K.calc('e', 'ROT13 applied twice shifts each letter by how much, mod 26?', '0', '13 + 13.', ['13 + 13 = 26.', '26 mod 26.', eq('= 0, so the text comes back')], check=(13 + 13) % 26)
K.calc('m', 'Vigenère: plain letter T with key letter E. Which cipher letter? Answer the letter.', 'X', 'T = 19, E = 4.', ['T = 19, E = 4.', '19 + 4 = 23.', eq('23 = X')], check='ABCDEFGHIJKLMNOPQRSTUVWXYZ'[(19 + 4) % 26])
K.calc('m', 'log<sub>2</sub>(26!) to the nearest whole number?', '88', 'Use the program, or Stirling.', ['26! &asymp; 4.03 &times; 10<sup>26</sup>.', 'log<sub>2</sub> 10 &asymp; 3.32, so 26.6 &times; 3.32.', eq('&asymp; 88.4, so 88')], check=round(__import__('math').log2(__import__('math').factorial(26))))
K.calc('m', 'Brute forcing Caesar with keys 1 to 25 equally likely, trying them in order. Average number of tries?', '13', 'Average of 1 to 25.', ['Sum 1 + ... + 25 = 325.', 'Divide by 25.', eq('325 / 25 = 13')], check=sum(range(1, 26)) // 25)
K.calc('m', 'A one time pad for a 1,000 byte message needs how many bits of key?', '8000', 'Key as long as the message.', ['1,000 bytes of key.', '8 bits per byte.', eq('1000 &times; 8 = 8000 bits')], check=1000 * 8)
K.calc('h', 'Unicity distance of substitution with H(K) = 88.4 bits and D = 3.2 bits per letter, to the nearest letter?', '28', 'U = H(K) / D.', ['88.4 / 3.2.', '= 27.6.', eq('&asymp; 28 letters')], check=round(88.4 / 3.2))
K.calc('h', 'How many Vigenère keys of length exactly 5 are there?', '11881376', '26 choices per letter.', ['26 per position.', '5 positions.', eq('26<sup>5</sup> = 11,881,376')], check=26 ** 5)
K.calc('h', 'Two time pad: c1 byte 0x3A, c2 byte 0x5C, and the attacker knows m1 byte is 0x41. What is m2 in decimal?', '39', 'm2 = c1 XOR c2 XOR m1.', ['0x3A XOR 0x5C = 0x66.', '0x66 XOR 0x41 = 0x27.', eq('0x27 = 39 (an apostrophe)')], check=0x3A ^ 0x5C ^ 0x41)
K.calc('x', 'In the style of an IIT Kharagpur cryptography problem: how many keys (a, b) does the affine cipher mod 26 have, with a coprime to 26?', '312', 'Count a with gcd(a, 26) = 1.', ['26 = 2 &times; 13, so a must be odd and not 13.', 'That gives &phi;(26) = 12 values of a, and 26 values of b.', eq('12 &times; 26 = 312')], check=sum(1 for a in range(26) if __import__('math').gcd(a, 26) == 1) * 26)

K.assign('caesar', 'e', 'A Caesar cipher that keeps spaces',
         '<p>Write <code>caesar(text, k)</code> for upper case text. Shift every letter A to Z by k places with wrap round. Keep every other character as it is. A negative k decrypts.</p>',
         '''
def caesar(text, k):
    # your code here
    pass
''', [('caesar("ATTACK AT DAWN", 3)', 'DWWDFN DW GDZQ'), ('caesar("XYZ", 3)', 'ABC'), ('caesar("DWWDFN", -3)', 'ATTACK'), ('caesar("HI, YOU!", 13)', 'UV, LBH!')],
         '''
def caesar(text, k):
    abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    out = ""
    for ch in text:
        if ch in abc:
            out = out + abc[(abc.index(ch) + k) % 26]
        else:
            out = out + ch
    return out
''', 'Find the letter number with abc.index, add k, take % 26, and look the result up again.', '<p>Python’s % gives a result from 0 to 25 even when k is negative, so the same function decrypts.</p>')
K.assign('vigdec', 'm', 'Vigenère decryption',
         '<p>Write <code>vig_decrypt(cipher, key)</code>. Both are upper case letters only. Subtract the key letter numbers (repeating the key) modulo 26.</p>',
         '''
def vig_decrypt(cipher, key):
    # your code here
    pass
''', [('vig_decrypt("LXFOPVEFRNHR", "LEMON")', 'ATTACKATDAWN'), ('vig_decrypt("ABC", "A")', 'ABC'), ('vig_decrypt("B", "B")', 'A')],
         '''
def vig_decrypt(cipher, key):
    abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    out = ""
    for i in range(len(cipher)):
        c = abc.index(cipher[i])
        k = abc.index(key[i % len(key)])
        out = out + abc[(c - k) % 26]
    return out
''', 'Use key[i % len(key)] to repeat the key, and (c - k) % 26 to subtract.', '<p>LXFOPVEFRNHR with LEMON is the classic textbook example. The key position i % len(key) is exactly the repetition that Kasiski exploits.</p>')
K.assign('xor', 'm', 'XOR two byte strings',
         '<p>Write <code>xor_bytes(a, b)</code> that returns a bytes object where each byte is a[i] XOR b[i]. Both inputs have the same length.</p>',
         '''
def xor_bytes(a, b):
    # your code here
    pass
''', [('xor_bytes(b"AB", b"  ").decode()', 'ab'), ('len(xor_bytes(b"", b""))', 0), ('list(xor_bytes(bytes([255, 0]), bytes([15, 15])))', [240, 15])],
         '''
def xor_bytes(a, b):
    out = []
    for i in range(len(a)):
        out.append(a[i] ^ b[i])
    return bytes(out)
''', 'Loop over the positions, use ^ on the two numbers, collect them in a list and call bytes() at the end.', '<p>XOR with a space (32) flips upper case letters to lower case, which is why the first test gives b"ab". This same function is the one time pad, and later the heart of stream ciphers and AES rounds.</p>')

K.must('Words', 'Plaintext, ciphertext, key, key space, brute force. Kerckhoffs: only the key is secret.')
K.must('Caesar', 'C = (P + k) mod 26, P = (C &minus; k) mod 26, A = 0. 26 keys. ROT13 is its own inverse.')
K.must('Frequency analysis', 'Substitution keeps letter counts. &chi;<sup>2</sup> = &Sigma; (O &minus; E)<sup>2</sup> / E. E 12.7%, T 9.1%, A 8.2%.')
K.must('Vigenère', 'C<sub>i</sub> = (P<sub>i</sub> + K<sub>i mod m</sub>) mod 26. IC = &Sigma; n(n &minus; 1) / N(N &minus; 1): English 0.066, random 0.038.')
K.must('One time pad', 'c = m &oplus; k, random key as long as the message, once. P(M | C) = P(M). |K| &ge; |M|. Reuse gives m<sub>1</sub> &oplus; m<sub>2</sub>.')
K.must('Unicity distance', 'U &asymp; H(K) / D, D &asymp; 3.2 bits per letter. 26! &asymp; 2<sup>88.4</sup>, so about 28 letters.')

T = K.topic(
    slug='cy-classical', topic='cy-classical', step=(1, 'Classical and symmetric cryptography', 'cy-c1', 'From Caesar to AES: how ciphers were broken, how modern block ciphers work, and how hashes and MACs protect data.', 'Intermediate'),
    title='Classical ciphers: Caesar, substitution, Vigenère and the one time pad', short='Classical ciphers', badge='1.1', minutes=60,
    lead='How secret writing started and how each cipher was broken: Caesar and modular arithmetic, substitution and frequency analysis with chi-squared, Vigenère with Kasiski and the index of coincidence, the one time pad and Shannon’s perfect secrecy, and the maths of key space and unicity distance.',
    desc='classical cryptography, Kerckhoffs principle, attack models, Caesar cipher, mod 26, ROT13, brute force, substitution cipher, frequency analysis, chi-squared, affine cipher, 26 factorial, Vigenere, Kasiski, index of coincidence, Friedman, one time pad, XOR, perfect secrecy, Shannon, two time pad, Venona, entropy, redundancy, unicity distance, Enigma',
    summary='Caesar and mod 26, frequency analysis, Vigenère and the index of coincidence, the one time pad and perfect secrecy, unicity distance.',
    keywords=['Caesar', 'frequency analysis', 'Vigenere', 'index of coincidence', 'one time pad', 'perfect secrecy', 'Kerckhoffs', 'unicity distance'],
    recap='<p>A big key space is not enough: a cipher must hide every pattern. The one time pad is perfect but only if the key is random, as long as the message, and never reused.</p>',
    added='2026-11-14')
