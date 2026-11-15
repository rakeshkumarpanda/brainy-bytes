# 2.3 Governance, risk, compliance and cyber law
# Example "audit_sample" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Audit sampling: how big a sample gives a good chance of catching a control failure?
import math
import random

def chance_to_catch(error_rate, n):
    """Probability that a sample of n contains at least one exception (independent draws)."""
    return 1 - (1 - error_rate) ** n

def sample_size(error_rate, confidence):
    """Smallest n so that the chance to catch at least one exception reaches the confidence."""
    return math.ceil(math.log(1 - confidence) / math.log(1 - error_rate))

for n in (5, 25, 45, 60):
    print(f"n = {n:2}: chance to catch a 5% failure rate = {chance_to_catch(0.05, n):.4f}")
print("\nsample needed for 95% confidence at a 5% failure rate:", sample_size(0.05, 0.95))
print("sample needed for 99% confidence at a 2% failure rate:", sample_size(0.02, 0.99))

# try it: 200 changes, 10 of them not approved, draw 25 at random 1000 times
random.seed(7)
population = [True] * 10 + [False] * 190          # True means "not approved"
hits = sum(any(random.sample(population, 25)) for _ in range(1000))
print(f"\nsimulation: a sample of 25 caught a problem in {hits} of 1000 audits")
