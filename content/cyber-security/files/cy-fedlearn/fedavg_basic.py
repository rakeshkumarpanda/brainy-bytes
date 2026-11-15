# 2.1 Federated learning in full
# Example "fedavg_basic" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Federated averaging (FedAvg, McMahan et al. 2017): three hospitals train one model without sharing patient rows.
# Model: predict a blood test value y from age x with y = w * x + b (x scaled to 0 to 1).
import random

random.seed(0)
def hospital(n, age_lo, age_hi):
    rows = []
    for _ in range(n):
        x = random.uniform(age_lo, age_hi)
        rows.append((x, 2.0 * x + 1.0 + random.gauss(0, 0.1)))     # the true rule is y = 2x + 1
    return rows

clients = {"Asha (young patients)": hospital(40, 0.0, 0.4),
           "Bose (middle aged)": hospital(100, 0.3, 0.7),
           "City (older patients)": hospital(60, 0.6, 1.0)}

def local_train(w, b, rows, epochs=5, lr=0.8):
    """Plain gradient descent on the client's own rows. Only w and b leave the hospital."""
    for _ in range(epochs):
        gw = sum((w * x + b - y) * x for x, y in rows) / len(rows)
        gb = sum((w * x + b - y) for x, y in rows) / len(rows)
        w, b = w - lr * gw, b - lr * gb
    return w, b

w, b = 0.0, 0.0                                   # the global model on the server
n_total = sum(len(r) for r in clients.values())
for rnd in range(1, 101):
    new_w = new_b = 0.0
    for name, rows in clients.items():
        lw, lb = local_train(w, b, rows)          # 1. send the global model, 2. train locally
        new_w += len(rows) / n_total * lw         # 3. weighted average by data size
        new_b += len(rows) / n_total * lb
    w, b = new_w, new_b
    if rnd in (1, 5, 20, 50, 100):
        print(f"round {rnd:3}: w = {w:.3f}, b = {b:.3f}")

# what a central server would learn if it could pool all rows (the privacy cost FL avoids)
allrows = [r for rows in clients.values() for r in rows]
cw, cb = local_train(0.0, 0.0, allrows, epochs=1000, lr=0.8)
print(f"\ncentral model on pooled data: w = {cw:.3f}, b = {cb:.3f}   (true rule: w = 2, b = 1)")
