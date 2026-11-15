# 2.2 Access control models: from the access matrix to RBAC and ABAC
# Example "rbac" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Role based access control (RBAC) with a role hierarchy and separation of duties
role_perms = {
    "employee":   {"read:wiki", "submit:expense"},
    "manager":    {"approve:expense"},
    "accountant": {"pay:expense", "read:ledger"},
    "auditor":    {"read:ledger", "read:logs"},
}
juniors = {"manager": ["employee"], "accountant": ["employee"], "auditor": ["employee"]}   # seniors inherit
user_roles = {"asha": {"manager"}, "ravi": {"accountant"}, "meera": {"auditor"}, "dev": {"employee"}}
conflicts = [("manager", "accountant")]  # the same person must not approve AND pay (separation of duties)

def all_roles(role):
    found = {role}
    for j in juniors.get(role, []):
        found |= all_roles(j)
    return found

def perms(user):
    out = set()
    for r in user_roles.get(user, set()):
        for rr in all_roles(r):
            out |= role_perms[rr]
    return out

for user in user_roles:
    print(f"{user:6} roles {sorted(user_roles[user])} -> {sorted(perms(user))}")

def assign(user, role):
    new = user_roles[user] | {role}
    for a, b in conflicts:
        if a in new and b in new:
            return f"refused: {a} and {b} conflict (separation of duties)"
    user_roles[user] = new
    return "assigned"

print("give asha the accountant role:", assign("asha", "accountant"))
print("give dev the manager role:   ", assign("dev", "manager"))
print("asha may pay expenses:", "pay:expense" in perms("asha"))
