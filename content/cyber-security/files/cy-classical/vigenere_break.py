# 1.1 Classical ciphers: Caesar, substitution, Vigenère and the one time pad
# Example "vigenere_break" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

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
