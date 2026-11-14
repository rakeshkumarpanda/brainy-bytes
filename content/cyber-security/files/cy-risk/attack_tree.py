# 1.2 Risk in numbers: matrices, ALE, attack trees and continuity
# Example "attack_tree" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# An attack tree: a leaf is a cost. A node is ("AND", children) or ("OR", children).
tree = ("OR", [
    ("AND", [1, 5]),        # take over an admin: phishing email AND beat MFA
    3,                      # SQL injection
    20,                     # bribe an insider
    ("AND", [4, 50]),       # steal a backup AND crack its encryption
])

def cheapest(node):
    if not isinstance(node, tuple):    # a leaf: its cost
        return node
    kind, children = node
    costs = []
    for child in children:
        costs.append(cheapest(child))
    if kind == "AND":
        return sum(costs)              # every step must be paid for
    return min(costs)                  # OR: the attacker picks the cheapest route

print("cheapest attack costs:", cheapest(tree), "thousand")

# The same tree with chances of success instead of costs
chance_tree = ("OR", [("AND", [0.3, 0.2]), 0.1, 0.5, ("AND", [0.2, 0.01])])

def success(node):
    if not isinstance(node, tuple):
        return node
    kind, children = node
    if kind == "AND":
        p = 1
        for child in children:
            p = p * success(child)
        return p
    fail = 1
    for child in children:
        fail = fail * (1 - success(child))
    return 1 - fail

print("chance the goal is reached:", round(success(chance_tree), 4))
