# 1.2 Firewalls, intrusion detection, VPNs and zero trust
# Example "zero_trust" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Zero trust: decide every request on identity, device and context, never on network location alone
def decide(req):
    reasons = []
    if not req["user_verified"]:
        return "deny", ["user not signed in"]
    if not req["device_managed"] or not req["disk_encrypted"] or req["os_patch_days"] > 30:
        return "deny", ["device fails health check"]
    if req["resource"] == "payroll" and req["role"] != "finance":
        return "deny", ["role not allowed for payroll"]
    if req["new_location"] or req["resource"] == "payroll":
        reasons.append("step up: ask for a passkey or MFA again")
        return "challenge", reasons
    return "allow", ["identity, device and role all fine"]

base = {"user_verified": True, "device_managed": True, "disk_encrypted": True, "os_patch_days": 5,
        "role": "engineer", "resource": "wiki", "new_location": False}
cases = {
    "engineer on a healthy laptop opens the wiki": {},
    "same engineer from a new country": {"new_location": True},
    "engineer tries payroll": {"resource": "payroll"},
    "finance user opens payroll": {"role": "finance", "resource": "payroll"},
    "unpatched laptop, even inside the office": {"os_patch_days": 90},
}
for label, change in cases.items():
    verdict, why = decide({**base, **change})
    print(f"{label:45} -> {verdict.upper():9} ({', '.join(why)})")
