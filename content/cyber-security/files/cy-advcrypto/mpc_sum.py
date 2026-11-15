# 1.3 Advanced cryptography: secret sharing, zero knowledge, homomorphic encryption and MPC
# Example "mpc_sum" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Secure multiparty computation: three hospitals learn their total patient count, but no single count
import secrets

M = 2 ** 61 - 1                          # all shares live mod a large prime
counts = {"Asha Hospital": 1840, "Bose Clinic": 975, "City Care": 2310}

def share(value, parties):
    parts = [secrets.randbelow(M) for i in range(parties - 1)]
    parts.append((value - sum(parts)) % M)   # the parts add up to value mod M
    return parts

names = list(counts)
received = {name: [] for name in names}
for owner, value in counts.items():
    for name, part in zip(names, share(value, len(names))):
        received[name].append(part)       # each hospital gets one random looking part from everyone

print("what City Care receives (random looking):", [str(v)[:8] + "..." for v in received["City Care"]])
partial = {name: sum(parts) % M for name, parts in received.items()}
total = sum(partial.values()) % M
print("published partial sums reveal nothing alone. Total:", total, "| check:", sum(counts.values()))

# The same idea powers secure aggregation in federated learning: masks that cancel in the sum
mask = secrets.randbelow(M)
update_a, update_b = 7, 12               # two phones' model updates (as integers)
sent_a, sent_b = (update_a + mask) % M, (update_b - mask) % M
print("server sees", str(sent_a)[:8] + "...", "and", str(sent_b)[:8] + "...", "but the sum is", (sent_a + sent_b) % M)
