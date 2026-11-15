# 1.1 Machine learning for security
# Example "drift_psi" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Is the world changing under the model? Population stability index (PSI) between training and today
import math

bins = ["< 1 KB", "1 to 10 KB", "10 to 100 KB", "100 KB to 1 MB", "> 1 MB"]
train = [0.10, 0.30, 0.35, 0.20, 0.05]      # share of email attachments in each size bin when the model was trained
week1 = [0.11, 0.29, 0.34, 0.21, 0.05]
week9 = [0.05, 0.15, 0.30, 0.30, 0.20]      # attackers moved to big ISO and ZIP files

def psi(expected, actual):
    total = 0
    for e, a in zip(expected, actual):
        total += (a - e) * math.log(a / e)
    return total

def verdict(v):
    return "stable" if v < 0.1 else "watch it" if v < 0.25 else "retrain now"

for name, now in [("week 1", week1), ("week 9", week9)]:
    v = psi(train, now)
    print(f"{name}: PSI = {v:.4f}  {verdict(v)}")
print("\nper bin for week 9:")
for b, e, a in zip(bins, train, week9):
    print(f"  {b:15} {e:.2f} -> {a:.2f}  adds {(a - e) * math.log(a / e):.4f}")
