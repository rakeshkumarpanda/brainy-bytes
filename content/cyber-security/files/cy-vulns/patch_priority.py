# 3.2 Vulnerabilities: CVE, CVSS, patching and hardening
# Example "patch_priority" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Which patch first? Combine CVSS (how bad), EPSS (how likely to be exploited soon), CISA KEV (already exploited)
# and exposure (can the internet reach it). The findings are made up, the method is how real teams triage.
findings = [
    # (asset, CVE, CVSS base, EPSS probability, in KEV?, internet facing?)
    ("vpn-gateway", "CVE-A", 9.8, 0.94, True, True),
    ("hr-laptop-17", "CVE-B", 9.8, 0.02, False, False),
    ("web-shop", "CVE-C", 7.5, 0.61, True, True),
    ("build-server", "CVE-D", 8.8, 0.05, False, False),
    ("print-server", "CVE-E", 6.5, 0.001, False, False),
    ("mail-relay", "CVE-F", 5.3, 0.40, False, True),
]

def priority(cvss, epss, kev, exposed):
    risk = cvss / 10 * max(epss, 0.01)           # impact times likelihood, with a small floor
    if kev:
        risk += 1.0                              # exploited in the wild: always first
    if exposed:
        risk *= 2                                # reachable from the internet
    return round(risk, 3)

def deadline(cvss, kev):
    if kev:
        return "fix within 14 days (BOD 22-01 style)"
    if cvss >= 9:
        return "fix within 15 days"
    if cvss >= 7:
        return "fix within 30 days"
    return "fix within 90 days"

ranked = sorted(findings, key=lambda f: priority(f[2], f[3], f[4], f[5]), reverse=True)
print(f"{'rank':4} {'asset':13} {'cve':6} {'cvss':>4} {'epss':>6} {'kev':5} {'net':5} {'score':>6}  deadline")
for i, (asset, cve, cvss, epss, kev, net) in enumerate(ranked, 1):
    print(f"{i:<4} {asset:13} {cve:6} {cvss:4} {epss:6.3f} {str(kev):5} {str(net):5} {priority(cvss, epss, kev, net):6}  {deadline(cvss, kev)}")

by_cvss = sorted(findings, key=lambda f: f[2], reverse=True)
print(f"\nSorting by CVSS alone puts {by_cvss[1][0]} (EPSS {by_cvss[1][3]}) above web-shop, which attackers are already using.")
