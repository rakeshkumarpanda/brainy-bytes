# 1.3 Hash functions, MACs and password storage
# Example "merkle" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A Merkle tree: one short root hash commits to a whole list, and a short proof shows one item is in it
import hashlib

def h(data):
    return hashlib.sha256(data).digest()

def build(items):                         # every level of the tree, leaves first (needs 2, 4, 8, ... items)
    level = [h(x.encode()) for x in items]
    levels = [level]
    while len(level) > 1:
        level = [h(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
        levels.append(level)
    return levels

def proof(levels, index):                 # the sibling hash at every level
    path = []
    for level in levels[:-1]:
        sibling = index ^ 1               # the other node of the pair
        path.append((level[sibling], sibling < index))
        index = index // 2
    return path

def verify(item, path, root):
    value = h(item.encode())
    for sibling, sibling_is_left in path:
        if sibling_is_left:
            value = h(sibling + value)
        else:
            value = h(value + sibling)
    return value == root

items = ["riya pays amit 10", "amit pays dev 5", "dev pays riya 7", "riya pays sam 2"]
levels = build(items)
root = levels[-1][0]
print("root:", root.hex()[:32], "...")

p = proof(levels, 2)
print("proof for item 2 has", len(p), "hashes for", len(items), "items")
print("item 2 is in the tree:", verify(items[2], p, root))
print("a changed item fails :", verify("dev pays riya 70", p, root))
