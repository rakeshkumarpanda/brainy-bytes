# 2.1 Federated learning in full
# Example "compress_update" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Making updates small: top-k sparsification and 8 bit quantisation of a model update
import random

random.seed(2)
update = [random.gauss(0, 1) * (3 if i % 10 == 0 else 0.3) for i in range(40)]   # a few big values, many small

def top_k(u, k):
    keep = sorted(range(len(u)), key=lambda i: -abs(u[i]))[:k]
    return {i: u[i] for i in keep}                   # send (index, value) pairs only

def quantise(values, bits=8):
    lo, hi = min(values), max(values)
    levels = 2 ** bits - 1
    step = (hi - lo) / levels
    codes = [round((v - lo) / step) for v in values]  # small integers 0 to 255
    return [lo + c * step for c in codes], step

def error(u, approx):
    return sum((a - b) ** 2 for a, b in zip(u, approx)) ** 0.5 / sum(a * a for a in u) ** 0.5

full_bytes = len(update) * 4                          # 32 bit floats
sparse = top_k(update, 8)
dense_back = [sparse.get(i, 0.0) for i in range(len(update))]
q_vals, step = quantise(list(sparse.values()))
q_back = [0.0] * len(update)
for i, v in zip(sparse, q_vals):
    q_back[i] = v

print(f"full update:        {full_bytes:4} bytes, relative error 0")
print(f"top 8 of 40:        {8 * (4 + 4):4} bytes (index + value), relative error {error(update, dense_back):.3f}")
print(f"top 8 and 8 bit:    {8 * (1 + 1) + 8:4} bytes (index + code, plus lo and step), relative error {error(update, q_back):.3f}")
print("\nError feedback: each phone keeps what it did not send and adds it to its next update, so nothing is lost for good.")
