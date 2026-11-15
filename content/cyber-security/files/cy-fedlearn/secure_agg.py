# 2.1 Federated learning in full
# Example "secure_agg" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Secure aggregation (Bonawitz et al. 2017), small version: the server learns only the SUM of the phones' updates.
# Every pair of phones agrees a random mask. The lower numbered phone adds it, the higher one subtracts it.
import random

M = 2 ** 16                                  # updates are scaled to integers and added mod M
updates = {1: [12, 5, 7], 2: [3, 9, 1], 3: [8, 2, 6], 4: [4, 4, 4]}
phones = sorted(updates)

def pair_mask(i, j):
    # in the real protocol i and j derive this from a Diffie-Hellman shared key, so the server never knows it
    rng = random.Random(f"{min(i, j)}-{max(i, j)}")
    return [rng.randrange(M) for _ in range(3)]

def masked(i):
    out = list(updates[i])
    for j in phones:
        if j == i:
            continue
        m = pair_mask(i, j)
        sign = 1 if i < j else -1
        out = [(o + sign * mk) % M for o, mk in zip(out, m)]
    return out

sent = {i: masked(i) for i in phones}
for i in phones:
    print(f"phone {i} sends {sent[i]}   (its real update {updates[i]} is hidden)")
total = [sum(v[k] for v in sent.values()) % M for k in range(3)]
print("server sum:", total, "  check:", [sum(u[k] for u in updates.values()) for k in range(3)])

# phone 4 drops out after the masks were set up: its masks no longer cancel
alive = [1, 2, 3]
partial = [sum(sent[i][k] for i in alive) % M for k in range(3)]
# the survivors reveal their pair masks with phone 4 (the real protocol rebuilds them from Shamir shares)
for i in alive:
    m = pair_mask(i, 4)
    partial = [(p - mk) % M for p, mk in zip(partial, m)]     # phone i had added +mask for pair (i, 4)
print("after phone 4 drops out and its masks are removed:", partial, "  check:", [sum(updates[i][k] for i in alive) for k in range(3)])
