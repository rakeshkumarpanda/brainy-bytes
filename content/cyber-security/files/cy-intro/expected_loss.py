# 1.1 What cybersecurity is: goals, threats and layers
# Example "expected_loss" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Expected loss of a risk = chance it happens in a year x what it costs when it happens
risks = [
    ("laptop stolen", 0.20, 80000),
    ("ransomware", 0.05, 2500000),
    ("website down for a day", 0.30, 150000),
]

total = 0
for name, chance, cost in risks:
    loss = chance * cost
    total = total + loss
    print(name, "-> expected loss per year:", round(loss))
print("total expected loss per year:", round(total))

# Gordon and Loeb: it is rarely worth spending more than about 37% (1 / e) of the expected loss on protection
import math
print("rough upper limit for the security budget:", round(total / math.e))
