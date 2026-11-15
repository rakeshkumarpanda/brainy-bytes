# 2.3 Governance, risk, compliance and cyber law
# Example "vendor_tier" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Third party risk: score suppliers from a questionnaire and decide how closely to watch each one
WEIGHTS = {"data_access": 0.4, "security_controls": 0.3, "past_incidents": 0.3}

vendors = {
    "Payroll SaaS": {"data_access": 90, "security_controls": 60, "past_incidents": 70},
    "Office plant supplier": {"data_access": 5, "security_controls": 40, "past_incidents": 10},
    "Cloud backup provider": {"data_access": 80, "security_controls": 85, "past_incidents": 20},
}
# each score is 0 (no risk) to 100 (high risk)

def risk_score(answers):
    total = 0
    for item, weight in WEIGHTS.items():
        total += weight * answers[item]
    return total

def tier(score):
    if score >= 60:
        return "Tier 1: yearly assessment, contract security clauses, SOC 2 Type II report"
    if score >= 30:
        return "Tier 2: questionnaire every two years"
    return "Tier 3: basic checks only"

for name, answers in sorted(vendors.items(), key=lambda v: -risk_score(v[1])):
    s = risk_score(answers)
    print(f"{name:22} risk {s:5.1f}  {tier(s)}")
