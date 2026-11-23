# 5.1 Certification revision: exams, recall, formulas and scenarios
# Example "revision_maths" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Every formula of the subject in one small program, so you can check your exam answers
import math

# 1. Risk (Foundations 1.2 and Operations 2.3)
asset_value, exposure, aro = 200000, 0.25, 0.4
sle = asset_value * exposure
ale = sle * aro
print(f"risk: SLE = {asset_value} x {exposure} = {sle:.0f}, ALE = SLE x ARO = {ale:.0f} per year")
control_cost, ale_after = 12000, 4000
print(f"      control value = ALE before - ALE after - cost = {ale - ale_after - control_cost:.0f}")

# 2. Passwords and brute force (Foundations 1.3, Systems 2.1)
length, alphabet = 12, 62
bits = length * math.log2(alphabet)
guesses_per_second = 1e10
years = 2 ** bits / 2 / guesses_per_second / (3600 * 24 * 365)
print(f"password: {length} characters from {alphabet}: {bits:.1f} bits, average crack time {years:.2e} years at 1e10 per second")

# 3. Hash collisions: the birthday bound (Crypto 1.3)
n = 128
print(f"birthday: a {n} bit hash needs about 2^{n // 2} = {2 ** (n // 2):.2e} tries for a 50% collision chance")

# 4. Toy RSA (Crypto 2.2), numbers far too small for real use
p, q, e = 61, 53, 17
N, phi = p * q, (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = 65
c = pow(m, e, N)
print(f"RSA: N = {N}, phi = {phi}, d = {d}, encrypt {m} -> {c}, decrypt -> {pow(c, d, N)}")

# 5. Diffie Hellman (Crypto 2.3)
P, g, a, b = 23, 5, 6, 15
A, B = pow(g, a, P), pow(g, b, P)
print(f"DH: A = {A}, B = {B}, shared secret {pow(B, a, P)} = {pow(A, b, P)}")

# 6. Alerts and the base rate (Operations 1.1, Advanced 1.1)
prior, tpr, fpr = 0.001, 0.99, 0.01
ppv = tpr * prior / (tpr * prior + fpr * (1 - prior))
print(f"base rate: detector with 99% TPR and 1% FPR, 1 in 1000 events bad: P(bad | alert) = {ppv:.3f}")

# 7. Availability (Foundations 1.2, Operations 1.2)
mtbf, mttr = 2000, 4
avail = mtbf / (mtbf + mttr)
print(f"availability: {mtbf} / ({mtbf} + {mttr}) = {avail:.5f}, downtime {(1 - avail) * 8760:.1f} hours a year")
for nines in (0.999, 0.9999, 0.99999):
    print(f"      {nines * 100:g}% up means {(1 - nines) * 525600:.1f} minutes down a year")

# 8. Differential privacy (Advanced 2.3)
eps = 0.5
print(f"DP: Laplace scale for a count at eps {eps} is b = 1 / eps = {1 / eps:.1f}, attack advantage at most e^eps - 1 = {math.exp(eps) - 1:.3f}")
