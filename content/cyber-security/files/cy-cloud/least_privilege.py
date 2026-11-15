# 2.2 Cloud security: shared responsibility, identity, settings and keys
# Example "least_privilege" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Least privilege from evidence: compare what a role is granted with what the audit log shows it used
granted = {"s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListAllMyBuckets", "ec2:RunInstances",
           "ec2:TerminateInstances", "iam:CreateUser", "iam:AttachUserPolicy", "kms:Decrypt", "sqs:SendMessage"}

# 90 days of audit log events for this role (action names only)
used_log = ["s3:GetObject"] * 4200 + ["s3:PutObject"] * 830 + ["kms:Decrypt"] * 4200 + ["sqs:SendMessage"] * 90

used = set(used_log)
unused = sorted(granted - used)
print(f"granted {len(granted)} actions, used {len(used)} in 90 days")
print("never used:", ", ".join(unused))
print(f"{len(unused) / len(granted) * 100:.0f}% of the permissions could be removed")

risky = [a for a in unused if a.startswith("iam:") or a.endswith("Terminate" + "Instances")]
print("most dangerous unused ones:", ", ".join(risky))
print("\nSuggested policy actions:", sorted(used))
