# 2.1 Federated learning in full
# Example "comm_rounds" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Communication: how many rounds until the model is good enough? FedSGD (1 local step) against FedAvg (E local steps)
import random

random.seed(0)
def hospital(n, lo, hi):
    return [(x, 2.0 * x + 1.0 + random.gauss(0, 0.1)) for x in (random.uniform(lo, hi) for _ in range(n))]

clients = [hospital(40, 0.0, 0.4), hospital(100, 0.3, 0.7), hospital(60, 0.6, 1.0)]
n_total = sum(len(c) for c in clients)
allrows = [r for c in clients for r in c]

def mse(w, b):
    return sum((w * x + b - y) ** 2 for x, y in allrows) / len(allrows)

def local_train(w, b, rows, epochs, lr=0.8):
    for _ in range(epochs):
        gw = sum((w * x + b - y) * x for x, y in rows) / len(rows)
        gb = sum((w * x + b - y) for x, y in rows) / len(rows)
        w, b = w - lr * gw, b - lr * gb
    return w, b

def rounds_needed(epochs, target=0.015, max_rounds=1000):
    w = b = 0.0
    for rnd in range(1, max_rounds + 1):
        results = [local_train(w, b, c, epochs) for c in clients]
        w = sum(len(c) / n_total * r[0] for c, r in zip(clients, results))
        b = sum(len(c) / n_total * r[1] for c, r in zip(clients, results))
        if mse(w, b) < target:
            return rnd
    return None

# a phone keyboard model has about 1.4 million parameters of 4 bytes, sent down and up every round
for e in (1, 5, 20):
    r = rounds_needed(e)
    mb = r * 2 * len(clients) * 1_400_000 * 4 / 1e6
    print(f"E = {e:2} local steps: {r:4} rounds  -> at keyboard model size that is {mb:8.1f} MB sent in total")
print("\nMore local work per round means far fewer rounds, which is the whole point of FedAvg.")
