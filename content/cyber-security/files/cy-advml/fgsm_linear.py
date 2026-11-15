# 1.2 Attacks on machine learning and their defences
# Example "fgsm_linear" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Evasion on a toy linear malware scorer: the fast gradient sign method (FGSM), then the certified safe distance
import math

# a trained model: features scaled 0 to 1 (entropy, crypto APIs, packed, network calls, signed)
w = [2.0, 1.5, 1.8, 1.2, -2.5]
b = -2.0

def score(x):
    z = sum(wi * xi for wi, xi in zip(w, x)) + b
    return 1 / (1 + math.exp(-z)), z

def sign(v):
    return (v > 0) - (v < 0)

x = [0.8, 0.7, 0.9, 0.6, 0.0]        # a malicious file
p, z = score(x)
print(f"original: P(malware) = {p:.3f}  (z = {z:.2f})")

# for a linear model the gradient of z with respect to x is just w, so the attacker
# moves every feature by eps against the sign of its weight
for eps in (0.1, 0.2, 0.3, 0.4):
    adv = [min(1, max(0, xi - eps * sign(wi))) for xi, wi in zip(x, w)]
    pa, za = score(adv)
    print(f"eps {eps}: P(malware) = {pa:.3f}  z dropped by {z - za:.2f}  {'EVADES' if pa < 0.5 else 'still caught'}")

# the defender's view: no change smaller than |z| / sum|w| in every feature can flip this decision
l1 = sum(abs(wi) for wi in w)
l2 = math.sqrt(sum(wi * wi for wi in w))
print(f"\ncertified radius: L-inf {abs(z) / l1:.3f}, L2 {abs(z) / l2:.3f}")
print("Real malware features cannot all change freely: removing 'packed' or adding a signature costs the attacker.")
