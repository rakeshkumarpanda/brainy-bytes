# 4.3 IoT and industrial control security: Mirai, Modbus, Purdue and Stuxnet
# Example "zone_rules" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Purdue levels and a firewall policy: which flows are allowed between zones?
LEVEL = {"internet": 5, "office_pc": 4, "erp": 4, "dmz_historian": 3.5, "dmz_jump": 3.5,
         "site_historian": 3, "hmi": 2, "scada": 2, "plc": 1}

ALLOW = {("office_pc", "dmz_historian"), ("erp", "dmz_historian"), ("site_historian", "dmz_historian"),
         ("office_pc", "dmz_jump"), ("dmz_jump", "hmi"), ("hmi", "plc"), ("scada", "plc")}

def allowed(src, dst):
    return (src, dst) in ALLOW

def check(path):
    for a, b in zip(path, path[1:]):
        if not allowed(a, b):
            return f"blocked at {a} -> {b}"
        if LEVEL[a] >= 4 and LEVEL[b] <= 3:
            return f"rule error: {a} (level {LEVEL[a]}) talks straight to {b} (level {LEVEL[b]})"
    return "path open"

for path in [["office_pc", "site_historian", "hmi", "plc"],
             ["office_pc", "dmz_historian", "plc"],
             ["office_pc", "dmz_jump", "hmi", "plc"],
             ["internet", "plc"]]:
    print(" -> ".join(path), ":", check(path))

print("\nThe jump host path is open by design, so it needs MFA, recording and approval for each session.")
