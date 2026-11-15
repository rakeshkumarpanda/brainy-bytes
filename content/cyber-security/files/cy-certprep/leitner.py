# 3.1 Certification revision: exams, recall, formulas and scenarios
# Example "leitner" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Spaced repetition with Leitner boxes: review a card less often each time you get it right
import random

random.seed(4)
cards = ["port 22", "port 443", "AES block size", "SHA-256 length", "ALE formula", "RTO vs RPO",
         "order of volatility", "NIST IR phases", "Kerberos port", "RSA d", "Laplace scale", "Krum"]
skill = {c: random.uniform(0.3, 0.7) for c in cards}   # chance of recalling each card at the start
box = {c: 1 for c in cards}                              # every card starts in box 1
EVERY = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}                  # box k is reviewed every EVERY[k] days

reviews = 0
for day in range(1, 31):
    for c in cards:
        if day % EVERY[box[c]] != 0:
            continue
        reviews += 1
        if random.random() < skill[c]:
            box[c] = min(5, box[c] + 1)                  # right: move up, see it less often
            skill[c] = min(0.98, skill[c] + 0.05)        # each correct recall makes the memory stronger
        else:
            box[c] = 1                                   # wrong: back to box 1, see it daily
    if day in (1, 7, 14, 30):
        counts = [sum(1 for c in cards if box[c] == k) for k in range(1, 6)]
        print(f"day {day:2d}: cards in boxes 1 to 5 = {counts}")

print(f"\n{reviews} reviews in 30 days instead of {len(cards) * 30} for daily review of every card")
print("weak cards:", [c for c in cards if box[c] <= 2])
