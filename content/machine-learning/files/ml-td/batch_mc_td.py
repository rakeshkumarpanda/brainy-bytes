# 2.2 Monte Carlo and temporal difference learning
# Example "batch_mc_td" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Sutton and Barto example 6.4. Eight episodes were observed:
# A,0,B,0 once, then B,1 six times, then B,0 once. What are V(A) and V(B)?
episodes = [[("A", 0), ("B", 0)]] + [[("B", 1)]] * 6 + [[("B", 0)]]

# Monte Carlo: average the returns that followed each state
returns = {"A": [], "B": []}
for ep in episodes:
    for i, (s, _) in enumerate(ep):
        returns[s].append(sum(r for _, r in ep[i:]))
print("Monte Carlo:", {s: round(sum(g) / len(g), 3) for s, g in returns.items()})

# Batch TD(0): sweep the same data again and again with small steps until the values settle
V = {"A": 0.0, "B": 0.0, "end": 0.0}
for _ in range(3000):
    for ep in episodes:
        for i, (s, r) in enumerate(ep):
            nxt = ep[i + 1][0] if i + 1 < len(ep) else "end"
            V[s] += 0.01 * (r + V[nxt] - V[s])
print("Batch TD:   ", {s: round(V[s], 3) for s in ("A", "B")})
