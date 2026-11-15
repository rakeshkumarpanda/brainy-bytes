# 2.2 Access control models: from the access matrix to RBAC and ABAC
# Example "blp_biba" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Bell-LaPadula (secrecy) and Biba (integrity) on a lattice of levels and categories
LEVELS = {"UNCLASSIFIED": 0, "CONFIDENTIAL": 1, "SECRET": 2, "TOP SECRET": 3}

def dominates(a, b):
    # label a dominates b when its level is at least b's and it holds every category of b
    return LEVELS[a[0]] >= LEVELS[b[0]] and set(b[1]) <= set(a[1])

def blp(subject, obj, op):
    if op == "read":
        return dominates(subject, obj)   # simple security property: no read up
    return dominates(obj, subject)       # star property: no write down

officer = ("SECRET", {"NUCLEAR"})
files = {
    "lunch menu": ("UNCLASSIFIED", set()),
    "reactor plan": ("SECRET", {"NUCLEAR"}),
    "missile codes": ("TOP SECRET", {"NUCLEAR"}),
    "spy list": ("SECRET", {"CRYPTO"}),
}
for name, label in files.items():
    r = "yes" if blp(officer, label, "read") else "no"
    w = "yes" if blp(officer, label, "write") else "no"
    print(f"{name:14} {label[0]:13} {sorted(label[1])!s:12} read {r:3} write {w}")

# Biba flips the arrows to protect integrity: no read down, no write up
INTEGRITY = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
def biba(subject, obj, op):
    if op == "read":
        return INTEGRITY[obj] >= INTEGRITY[subject]     # never read less trusted data
    return INTEGRITY[subject] >= INTEGRITY[obj]          # never write to more trusted data
print("browser (LOW) writes system file (HIGH):", biba("LOW", "HIGH", "write"))
print("installer (HIGH) reads downloaded file (LOW):", biba("HIGH", "LOW", "read"))
