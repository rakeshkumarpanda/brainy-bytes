# 2.2 Cloud security: shared responsibility, identity, settings and keys
# Example "iam_eval" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How a cloud IAM policy decides, in the AWS order: an explicit Deny wins, then any Allow, otherwise Deny.
from fnmatch import fnmatch          # lets "*" match anything, like policy wildcards

policy = [
    {"effect": "Allow", "action": "s3:GetObject", "resource": "reports-bucket/*"},
    {"effect": "Allow", "action": "s3:PutObject", "resource": "reports-bucket/uploads/*"},
    {"effect": "Deny", "action": "s3:*", "resource": "reports-bucket/payroll/*"},
]

def decide(action, resource):
    matching = [s for s in policy if fnmatch(action, s["action"]) and fnmatch(resource, s["resource"])]
    if any(s["effect"] == "Deny" for s in matching):
        return "DENY (explicit)"
    if any(s["effect"] == "Allow" for s in matching):
        return "ALLOW"
    return "DENY (default, nothing allows it)"

requests = [
    ("s3:GetObject", "reports-bucket/q3.pdf"),
    ("s3:PutObject", "reports-bucket/uploads/a.csv"),
    ("s3:GetObject", "reports-bucket/payroll/nov.xlsx"),
    ("s3:DeleteObject", "reports-bucket/q3.pdf"),
]
for action, resource in requests:
    print(f"{action:16} {resource:34} {decide(action, resource)}")
