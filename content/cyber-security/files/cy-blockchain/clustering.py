# 3.1 Blockchain security: hash chains, mining, consensus and wallets
# Example "clustering" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Following the money: the common input heuristic (Meiklejohn et al. 2013) on a made up ledger
# Coins spent together as inputs of one transaction almost always belong to one owner.
txs = [
    {"id": "t1", "inputs": ["A1", "A2"], "outputs": ["S1"]},        # ransom paid to S1
    {"id": "t2", "inputs": ["S1", "S2"], "outputs": ["S3", "X9"]},
    {"id": "t3", "inputs": ["S3"], "outputs": ["EX1"]},             # EX1 is a known exchange deposit address
    {"id": "t4", "inputs": ["B1", "B2", "B3"], "outputs": ["C1"]},
]

parent = {}
def find(a):
    parent.setdefault(a, a)
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a
def union(a, b):
    parent[find(a)] = find(b)

for t in txs:
    first = t["inputs"][0]
    for other in t["inputs"][1:]:
        union(first, other)

clusters = {}
for addr in list(parent):
    clusters.setdefault(find(addr), []).append(addr)
for c in clusters.values():
    print("one owner probably controls:", sorted(c))

flows = {o: t["id"] for t in txs for o in t["outputs"]}
print("the ransom wallet S1 shares an owner with S2, and money moved on to exchange address EX1 in", flows["EX1"])
print("exchanges must know their customers, so investigators can ask who owns EX1")
