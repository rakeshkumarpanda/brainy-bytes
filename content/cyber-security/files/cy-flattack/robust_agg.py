# 2.2 Attacks and defences in federated learning
# Example "robust_agg" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Byzantine robust aggregation: the mean, coordinate wise median, trimmed mean and Krum against 3 bad clients of 10
import statistics as st

honest = [[1.0, 0.5], [1.1, 0.4], [0.9, 0.6], [1.05, 0.55], [0.95, 0.45], [1.2, 0.5], [0.85, 0.5]]
bad = [[-8.0, 9.0], [-8.5, 9.5], [-7.5, 8.5]]          # attackers push the model the wrong way together
updates = honest + bad
f = len(bad)

def mean(us):
    return [sum(u[k] for u in us) / len(us) for k in range(2)]

def median(us):
    return [st.median(u[k] for u in us) for k in range(2)]

def trimmed_mean(us, beta):
    out = []
    for k in range(2):
        vals = sorted(u[k] for u in us)[beta:len(us) - beta]   # drop the beta smallest and largest
        out.append(sum(vals) / len(vals))
    return out

def krum(us, f):
    # score each update by its summed squared distance to its n - f - 2 nearest neighbours, pick the lowest
    scores = []
    for i, u in enumerate(us):
        d = sorted(sum((u[k] - v[k]) ** 2 for k in range(2)) for j, v in enumerate(us) if j != i)
        scores.append(sum(d[:len(us) - f - 2]))
    return us[scores.index(min(scores))]

print("true honest mean:  ", [round(v, 3) for v in mean(honest)])
print("plain mean:        ", [round(v, 3) for v in mean(updates)], "  dragged away by 3 attackers")
print("coordinate median: ", [round(v, 3) for v in median(updates)])
print("trimmed mean b=3:  ", [round(v, 3) for v in trimmed_mean(updates, 3)])
print("Krum (f=3):        ", krum(updates, f))
