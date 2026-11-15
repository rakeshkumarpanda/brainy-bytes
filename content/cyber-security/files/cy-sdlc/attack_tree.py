# 2.2 Secure development: threat models, scanners, fuzzing and the supply chain
# Example "attack_tree" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# An attack tree (Schneier, 1999): the goal at the root, ways to reach it below.
# OR node: the attacker picks the cheapest child. AND node: the attacker needs every child.
tree = ("OR", "Read customer database", [
    ("AND", "Use a stolen admin password", [
        ("LEAF", "Phish an admin", 2000, 0.3),
        ("LEAF", "Bypass MFA (push fatigue)", 1000, 0.2),
    ]),
    ("LEAF", "SQL injection in the search page", 500, 0.1),
    ("AND", "Steal a backup", [
        ("LEAF", "Find the backup bucket name", 100, 0.5),
        ("LEAF", "Bucket left public", 0, 0.05),
    ]),
])

def evaluate(node, depth=0, show=True, fixed=()):
    kind, name = node[0], node[1]
    if kind == "LEAF":
        cost, p = (float("inf"), 0.0) if name in fixed else (node[2], node[3])
    else:
        results = [evaluate(child, depth + 1, show, fixed) for child in node[2]]
        if kind == "OR":
            cost = min(c for c, _ in results)               # cheapest way
            q = 1.0
            for _, pc in results:
                q *= 1 - pc
            p = 1 - q                                       # at least one way works (independent)
        else:
            cost = sum(c for c, _ in results)               # must pay for every step
            p = 1.0
            for _, pc in results:
                p *= pc                                     # every step must work
    if show:                                                # children print before their parent
        print(f"{'    ' * depth}{kind:4} {name:36} cost {cost:5}  P(success) {p:.4f}")
    return cost, p

cost, p = evaluate(tree)
print("\nWhat if we fix leaves? (a fixed leaf costs infinity and never succeeds)")
for fix in [("SQL injection in the search page",), ("Bucket left public",),
            ("SQL injection in the search page", "Bucket left public")]:
    c, pr = evaluate(tree, show=False, fixed=fix)
    print(f"   fix {' + '.join(fix):55} cheapest attack {c:5}  P(success) {pr:.4f}")
