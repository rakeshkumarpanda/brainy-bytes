# 1.1 Classical ciphers: Caesar, substitution, Vigenère and the one time pad
# Example "freq_break" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

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
