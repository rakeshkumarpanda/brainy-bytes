# 2.1 Threat intelligence: knowing the attacker
# Example "dga_detect" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Spot domains made up by malware (domain generation algorithms) from how random their letters look
import math
from collections import Counter

def entropy(s):
    n = len(s)
    return -sum(c / n * math.log2(c / n) for c in Counter(s).values())

def vowel_share(s):
    return sum(1 for ch in s if ch in "aeiou") / len(s)

def score(name):
    total = entropy(name)
    if vowel_share(name) < 0.2:
        total += 1          # real words need vowels
    if any(ch.isdigit() for ch in name):
        total += 1          # digits inside a word are unusual
    return total

THRESHOLD = 3.5
domains = ["google", "wikipedia", "xkqzvbtrwplm", "flipkart", "q7j2nd9vx0ra",
           "icicibank", "bwuzhfaiyeqo", "irctc", "zzqjxkwv", "timesofindia"]
for d in domains:
    s = score(d)
    print(f"{d + '.com':18} entropy {entropy(d):4.2f}  vowels {vowel_share(d):4.2f}  score {s:4.2f}  {'FLAG' if s > THRESHOLD else ''}")
