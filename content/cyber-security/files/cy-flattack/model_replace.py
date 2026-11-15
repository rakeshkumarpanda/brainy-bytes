# 2.2 Attacks and defences in federated learning
# Example "model_replace" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Model replacement (Bagdasaryan et al. 2020): one client scales its update so the average becomes its own model.
# The server uses G_new = G + (eta / n) * sum(L_i - G), where L_i are the clients' models.
import math

G = [1.0, 2.0]                     # current global model (two weights to keep it readable)
n, eta = 10, 1.0                   # 10 clients this round, server learning rate 1
honest = [[1.0 + 0.05 * i, 2.0 - 0.03 * i] for i in range(9)]   # small, sensible changes
X = [5.0, -3.0]                    # the attacker's backdoored model

gamma = n / eta                    # boost factor
attacker = [G[k] + gamma * (X[k] - G[k]) for k in range(2)]
print("attacker sends", [round(v, 2) for v in attacker], "after boosting by", gamma)

def aggregate(models, clip=None):
    upd = [0.0, 0.0]
    for L in models:
        d = [L[k] - G[k] for k in range(2)]
        size = math.hypot(*d)
        if clip and size > clip:
            d = [v * clip / size for v in d]          # norm clipping: no change may be longer than clip
        upd = [upd[k] + d[k] for k in range(2)]
    return [G[k] + eta / n * upd[k] for k in range(2)]

print("FedAvg result:          ", [round(v, 3) for v in aggregate(honest + [attacker])], "  close to X =", X)
print("with norm clip 1.0:     ", [round(v, 3) for v in aggregate(honest + [attacker], clip=1.0)])
print("if the attacker sent no change:", [round(v, 3) for v in aggregate(honest)])
