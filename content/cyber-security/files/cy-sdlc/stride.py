# 2.2 Secure development: threat models, scanners, fuzzing and the supply chain
# Example "stride" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# STRIDE per element: list the threats that apply to each part of a data flow diagram
STRIDE = {
    "S": "Spoofing (pretending to be someone else)       -> authentication",
    "T": "Tampering (changing data or code)              -> integrity",
    "R": "Repudiation (denying an action)                -> logging, non repudiation",
    "I": "Information disclosure (leaking data)          -> confidentiality",
    "D": "Denial of service (making it unavailable)      -> availability",
    "E": "Elevation of privilege (gaining more rights)   -> authorisation",
}
APPLIES = {                      # Microsoft's STRIDE per element table
    "external entity": "SR",
    "process": "STRIDE",
    "data store": "TRID",        # R applies when the store holds logs
    "data flow": "TID",
}
diagram = [
    ("Customer (browser)", "external entity"),
    ("Web app", "process"),
    ("Orders database", "data store"),
    ("Browser -> web app (HTTPS)", "data flow"),
    ("Web app -> payment provider", "data flow"),
]
total = 0
for name, kind in diagram:
    letters = APPLIES[kind]
    total += len(letters)
    print(f"{name} [{kind}]: {letters}")
    for letter in letters:
        print("    " + STRIDE[letter])
print(f"\n{total} threats to think through for {len(diagram)} elements")
