# 2.1 Federated learning in full
# Example "vertical_fl" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Vertical federated learning: a bank and a shop hold different columns about the same customers.
# Step 1 finds the shared customers, step 2 trains one logistic regression split across the two parties.
import hashlib
import math

bank = {"c01": [0.9, 0.2], "c02": [0.1, 0.8], "c03": [0.7, 0.4], "c05": [0.2, 0.9], "c06": [0.8, 0.1]}   # income, debt
labels = {"c01": 1, "c02": 0, "c03": 1, "c05": 0, "c06": 1}                                         # repaid the loan?
shop = {"c01": [0.8], "c03": [0.6], "c04": [0.5], "c05": [0.1], "c06": [0.9]}                         # spending score

# 1. find shared customers without listing them in the clear. A salted hash is only a teaching sketch:
#    real systems use a private set intersection (PSI) protocol, because short IDs can be guessed.
SALT = b"agreed-secret-salt"
def h(cid):
    return hashlib.sha256(SALT + cid.encode()).hexdigest()[:12]
shared_hashes = {h(c) for c in bank} & {h(c) for c in shop}
ids = sorted(c for c in bank if h(c) in shared_hashes)
print("shared customers:", ids)

# 2. each party keeps its own weights and computes a partial score on its own columns
wa, wb, b = [0.0, 0.0], [0.0], 0.0
for epoch in range(300):
    for cid in ids:
        za = wa[0] * bank[cid][0] + wa[1] * bank[cid][1] + b      # bank side
        zb = wb[0] * shop[cid][0]                                  # shop side, sent to the bank
        p = 1 / (1 + math.exp(-(za + zb)))
        err = p - labels[cid]                                      # only the bank knows the label
        # the bank sends err back to the shop. Real systems encrypt it (for example with Paillier).
        wa = [wa[0] - 0.5 * err * bank[cid][0], wa[1] - 0.5 * err * bank[cid][1]]
        b -= 0.5 * err
        wb = [wb[0] - 0.5 * err * shop[cid][0]]
print("bank weights (income, debt):", [round(v, 2) for v in wa], " shop weight (spending):", [round(v, 2) for v in wb])
for cid in ids:
    z = wa[0] * bank[cid][0] + wa[1] * bank[cid][1] + b + wb[0] * shop[cid][0]
    print(f"  {cid}: P(repay) = {1 / (1 + math.exp(-z)):.3f}  actual {labels[cid]}")
