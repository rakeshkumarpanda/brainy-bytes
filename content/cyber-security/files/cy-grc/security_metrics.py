# 2.3 Governance, risk, compliance and cyber law
# Example "security_metrics" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Metrics for the board: key performance indicators (KPIs) and key risk indicators (KRIs) against thresholds
metrics = [
    # name, value, target, higher is better?
    ("MFA coverage (% of accounts)", 1840 / 2000 * 100, 99, True),
    ("Critical patches applied within 15 days (%)", 270 / 300 * 100, 95, True),
    ("Phishing test click rate (%)", 6.0, 5, False),
    ("Mean time to contain incidents (hours)", 1.4, 4, False),
    ("Backups restored successfully in tests (%)", 100.0, 100, True),
]
for name, value, target, higher in metrics:
    ok = value >= target if higher else value <= target
    print(f"{name:44} {value:6.1f}  target {'>=' if higher else '<='} {target:<4}  {'OK' if ok else 'ACTION NEEDED'}")

before, after = 18.0, 6.0
print(f"\nPhishing click rate fell from {before}% to {after}%: a {(before - after) / before * 100:.1f}% drop after training.")
