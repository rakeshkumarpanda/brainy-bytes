# 2.2 Access control models: from the access matrix to RBAC and ABAC
# Example "abac" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Attribute based access control (ABAC): decide from attributes of user, resource, action and context
POLICY = [                               # checked in order, deny rules win (deny overrides)
    ("deny",  lambda u, r, a, c: not c["device_managed"], "unmanaged device"),
    ("deny",  lambda u, r, a, c: r["classification"] == "restricted" and u["clearance"] < 2, "clearance too low"),
    ("allow", lambda u, r, a, c: u["dept"] == r["dept"] and a in ("read", "edit"), "same department"),
    ("allow", lambda u, r, a, c: u["role"] == "auditor" and a == "read", "auditors may read"),
]

def decide(u, r, a, c):
    allow_reason = None
    for effect, test, why in POLICY:
        if test(u, r, a, c):
            if effect == "deny":
                return "DENY", why
            allow_reason = allow_reason or why
    return ("ALLOW", allow_reason) if allow_reason else ("DENY", "no rule allows it (default deny)")

doc = {"dept": "finance", "classification": "restricted"}
people = {
    "asha (finance, clearance 2)": {"dept": "finance", "clearance": 2, "role": "staff"},
    "ravi (finance, clearance 1)": {"dept": "finance", "clearance": 1, "role": "staff"},
    "meera (audit, clearance 2)":  {"dept": "audit", "clearance": 2, "role": "auditor"},
    "dev (sales, clearance 2)":    {"dept": "sales", "clearance": 2, "role": "staff"},
}
for name, user in people.items():
    print(f"{name:28} edit: {decide(user, doc, 'edit', {'device_managed': True})}")
print("asha on a personal laptop:", decide(people["asha (finance, clearance 2)"], doc, "read", {"device_managed": False}))
