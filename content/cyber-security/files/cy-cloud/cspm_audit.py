# 2.2 Cloud security: shared responsibility, identity, settings and keys
# Example "cspm_audit" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A tiny cloud security posture check (CSPM): read the settings and flag the classic mistakes
config = {
    "buckets": [
        {"name": "web-assets", "public_read": True, "encrypted": True, "purpose": "public website images"},
        {"name": "customer-exports", "public_read": True, "encrypted": False, "purpose": "CSV exports"},
        {"name": "backups", "public_read": False, "encrypted": True, "purpose": "nightly backups"},
    ],
    "firewall_rules": [
        {"name": "web", "port": 443, "source": "0.0.0.0/0"},
        {"name": "ssh-anywhere", "port": 22, "source": "0.0.0.0/0"},
        {"name": "db", "port": 5432, "source": "10.0.0.0/16"},
    ],
    "root_account_mfa": False,
    "audit_logging": True,
}

findings = []
for b in config["buckets"]:
    if b["public_read"] and "public" not in b["purpose"]:
        findings.append(("HIGH", f"bucket {b['name']} is public but holds {b['purpose']}"))
    if not b["encrypted"]:
        findings.append(("MEDIUM", f"bucket {b['name']} is not encrypted at rest"))
for r in config["firewall_rules"]:
    if r["source"] == "0.0.0.0/0" and r["port"] in (22, 3389, 5432, 3306):
        findings.append(("HIGH", f"rule {r['name']} opens admin or database port {r['port']} to the whole internet"))
if not config["root_account_mfa"]:
    findings.append(("CRITICAL", "root account has no MFA"))
if not config["audit_logging"]:
    findings.append(("HIGH", "audit logging is off"))

order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
for level, text in sorted(findings, key=lambda f: order[f[0]]):
    print(f"{level:8} {text}")
checks = len(config["buckets"]) * 2 + len(config["firewall_rules"]) + 2
print(f"\n{checks - len(findings)} of {checks} checks pass")
