# 2.3 Governance, risk, compliance and cyber law
# Example "control_crosswalk" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# One control, many frameworks: a crosswalk shows which NIST CSF 2.0 function each of our controls supports
controls = [
    # our control, ISO 27001:2022 Annex A, CIS Controls v8, CSF 2.0 function
    ("Security policy approved by the board", "5.1", "-", "GV"),
    ("Supplier security reviews", "5.19", "15", "GV"),
    ("Asset inventory", "5.9", "1", "ID"),
    ("MFA for all users", "8.5", "6", "PR"),
    ("Security awareness training", "6.3", "14", "PR"),
    ("Patch management", "8.8", "7", "PR"),
    ("Central logging and alerts", "8.15, 8.16", "8", "DE"),
    ("Incident response plan", "5.24", "17", "RS"),
]
FUNCTIONS = {"GV": "Govern", "ID": "Identify", "PR": "Protect", "DE": "Detect", "RS": "Respond", "RC": "Recover"}

count = {code: 0 for code in FUNCTIONS}
for name, iso, cis, fn in controls:
    count[fn] += 1
    print(f"{name:38} ISO A.{iso:10} CIS {cis:3} -> {FUNCTIONS[fn]}")

print()
for code, name in FUNCTIONS.items():
    print(f"{name:9} {'#' * count[code]:5} {count[code]}")
print("\nRecover has nothing: add tested backups and a recovery plan (ISO A.8.13, CIS 11).")
