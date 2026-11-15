# 1.1 Network attacks and defences: spoofing, floods, scans and poisoning
# Example "dns_race" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# DNS cache poisoning: why random source ports matter (Kaminsky, 2008)
import random

def chance(n_forged, space):
    # probability that at least one of n forged replies matches the one value the resolver expects
    return 1 - (1 - 1 / space) ** n_forged

for label, space in (("16 bit query ID only", 2 ** 16), ("ID plus about 16 bits of random port", 2 ** 32)):
    print(f"{label:38}: one race with 100 forged replies wins with p = {chance(100, space):.6f}")

# Kaminsky's trick: ask for random names (a1.bank.test, a2.bank.test, ...) so the attacker can race again and again
races = 0
rng = random.Random(1)
while True:
    races += 1
    if rng.random() < chance(100, 2 ** 16):
        break
print("with a 16 bit ID, the toy attacker won after", races, "races")
print("expected races with port randomisation:", round(1 / chance(100, 2 ** 32)))
