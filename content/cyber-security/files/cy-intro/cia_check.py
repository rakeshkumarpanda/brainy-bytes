# 1.1 What cybersecurity is: goals, threats and layers
# Example "cia_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Sort some incidents by the security goal they break.
# C = confidentiality (secret seen), I = integrity (data changed), A = availability (service down)
incidents = [
    ("Customer list copied and sold online", True, False, False),
    ("Student raises own marks in the school system", False, True, False),
    ("Ransomware locks and steals hospital files", True, True, True),
    ("Fake traffic takes a ticket site down", False, False, True),
    ("Account number changed on an emailed bill", False, True, False),
]

for name, conf, integ, avail in incidents:
    broken = []
    if conf:
        broken.append("confidentiality")
    if integ:
        broken.append("integrity")
    if avail:
        broken.append("availability")
    print(name)
    print("   breaks:", ", ".join(broken))
