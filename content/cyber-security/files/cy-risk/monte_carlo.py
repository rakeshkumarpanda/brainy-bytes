# 1.2 Risk in numbers: matrices, ALE, attack trees and continuity
# Example "monte_carlo" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

import random

# FAIR style: simulate many years. Each month a breach happens with a small chance,
# and each breach costs a random amount between a low and a high estimate.
random.seed(1)
chance_per_month = 0.04
low, high = 200000, 1500000

years = []
for y in range(5000):
    loss = 0
    for month in range(12):
        if random.random() < chance_per_month:
            loss = loss + random.uniform(low, high)
    years.append(loss)

years.sort()
average = sum(years) / len(years)
print("average loss per year:", round(average))
print("years with no breach:", sum(1 for v in years if v == 0), "of", len(years))
print("1 year in 10 is worse than:", round(years[int(0.9 * len(years))]))
print("1 year in 100 is worse than:", round(years[int(0.99 * len(years))]))
