# 2.2 Access control models: from the access matrix to RBAC and ABAC
# Example "access_matrix" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Lampson's access matrix (1971), and the two ways systems store it: ACLs and capability lists
matrix = {                               # matrix[subject][object] = set of rights
    "asha":  {"payroll.xlsx": {"read", "write"}, "wiki": {"read", "write"}},
    "ravi":  {"payroll.xlsx": {"read"},          "wiki": {"read"}},
    "build": {"repo": {"read"},                  "wiki": {"read"}},
}

# ACL: store each COLUMN with its object (what Linux, Windows and S3 buckets do)
acl = {}
for subject, row in matrix.items():
    for obj, rights in row.items():
        acl.setdefault(obj, {})[subject] = rights
# Capability list: store each ROW with its subject (like file descriptors or signed tokens)
caps = {subject: dict(row) for subject, row in matrix.items()}

print("ACL of payroll.xlsx:", {s: sorted(r) for s, r in acl["payroll.xlsx"].items()})
print("capabilities of ravi:", {o: sorted(r) for o, r in caps["ravi"].items()})

def check(subject, obj, right):
    return right in matrix.get(subject, {}).get(obj, set())

for s, o, r in [("ravi", "payroll.xlsx", "read"), ("ravi", "payroll.xlsx", "write"), ("build", "payroll.xlsx", "read")]:
    print(f"{s} {r} {o}: {'allowed' if check(s, o, r) else 'denied'}")

# Questions each layout answers quickly
print("who can touch payroll? (easy with ACLs):", sorted(acl["payroll.xlsx"]))
print("what can ravi touch?  (easy with capabilities):", sorted(caps["ravi"]))
