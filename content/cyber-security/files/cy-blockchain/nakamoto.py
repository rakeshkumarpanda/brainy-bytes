# 3.1 Blockchain security: hash chains, mining, consensus and wallets
# Example "nakamoto" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The double spend race (Nakamoto 2008, section 11): chance an attacker with share q ever overtakes after z blocks
import math
import random

def attacker_success(q, z):
    p = 1 - q
    if q >= p:
        return 1.0
    lam = z * q / p
    total = 1.0
    for k in range(z + 1):
        poisson = math.exp(-lam) * lam ** k / math.factorial(k)
        total -= poisson * (1 - (q / p) ** (z - k))
    return total

print("q     z=1      z=3      z=6")
for q in (0.1, 0.2, 0.3, 0.45):
    print(f"{q:<5} " + "  ".join(f"{attacker_success(q, z):.5f}" for z in (1, 3, 6)))

def confirmations_needed(q, risk=0.001):
    z = 0
    while attacker_success(q, z) >= risk:
        z += 1
    return z

for q in (0.1, 0.15, 0.25, 0.3):
    print(f"attacker {q:.0%}: wait for {confirmations_needed(q)} blocks to push the risk below 0.1%")

# check one value by simulating many races
random.seed(5)
def race(q, z, give_up=40):
    honest = attacker = 0
    while honest < z:
        if random.random() < q: attacker += 1
        else: honest += 1
    while honest - attacker < give_up:
        if attacker >= honest: return True      # caught up: Nakamoto counts a tie as success
        if random.random() < q: attacker += 1
        else: honest += 1
    return False
wins = sum(race(0.3, 3) for _ in range(4000))
print(f"simulated q=0.3, z=3: {wins / 4000:.3f}   formula: {attacker_success(0.3, 3):.3f}")
