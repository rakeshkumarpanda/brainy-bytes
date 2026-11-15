# 2.1 Federated learning in full
# Example "client_drift" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Client drift on non-IID data, and two fixes: FedProx and SCAFFOLD.
# Each client k has its own loss f_k(w) = a_k / 2 * (w - c_k)^2 (equal data sizes).
# The best global model minimises the average loss: w* = sum(a_k * c_k) / sum(a_k).
clients = [(1.0, 0.0), (4.0, 10.0)]          # (curvature a_k, best point c_k): very different data
w_star = sum(a * c for a, c in clients) / sum(a for a, c in clients)
print(f"true global optimum w* = {w_star:.3f}")

def grad(w, a, c):
    return a * (w - c)

def fedavg_round(w, steps, lr, mu=0.0):
    new = []
    for a, c in clients:
        v = w
        for _ in range(steps):
            v -= lr * (grad(v, a, c) + mu * (v - w))   # FedProx adds mu * (v - w), FedAvg has mu = 0
        new.append(v)
    return sum(new) / len(new)

def scaffold_round(w, steps, lr):
    # control variates: each client's gradient at the global model, and their average
    ci = [grad(w, a, c) for a, c in clients]
    cg = sum(ci) / len(ci)
    new = []
    for (a, c), ck in zip(clients, ci):
        v = w
        for _ in range(steps):
            v -= lr * (grad(v, a, c) - ck + cg)          # correct the local direction towards the global one
        new.append(v)
    return sum(new) / len(new)

def run(step_fn, rounds=200):
    w = 0.0
    for _ in range(rounds):
        w = step_fn(w)
    return w

print(" E   FedAvg  FedProx mu=1  FedProx mu=4  SCAFFOLD")
for E in (1, 5, 50):
    a = run(lambda w: fedavg_round(w, E, 0.1))
    p1 = run(lambda w: fedavg_round(w, E, 0.1, 1.0))
    p4 = run(lambda w: fedavg_round(w, E, 0.1, 4.0))
    s = run(lambda w: scaffold_round(w, E, 0.1))
    print(f"{E:2}   {a:6.3f}  {p1:12.3f}  {p4:12.3f}  {s:8.3f}")
print("\nWith many local steps each client runs to its own optimum, so plain averaging drifts towards 5.0.")
print("FedProx pulls local models back towards the global one. SCAFFOLD corrects the direction and reaches 8.0.")
