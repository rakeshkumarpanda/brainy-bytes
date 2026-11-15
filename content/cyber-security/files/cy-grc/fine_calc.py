# 2.3 Governance, risk, compliance and cyber law
# Example "fine_calc" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The size of the stick: maximum fines under GDPR and India's DPDP Act
def gdpr_max(turnover_eur, serious=True):
    """Article 83: the higher of a fixed amount or a share of worldwide yearly turnover."""
    if serious:
        return max(20_000_000, 0.04 * turnover_eur)
    return max(10_000_000, 0.02 * turnover_eur)

for turnover in (50_000_000, 500_000_000, 2_000_000_000, 100_000_000_000):
    print(f"turnover EUR {turnover:>15,}: max serious fine EUR {gdpr_max(turnover):>15,.0f}")

# DPDP Act 2023 schedule, highest amounts in rupees (crore = 10 million)
CRORE = 10_000_000
dpdp = {
    "no reasonable security safeguards to prevent a breach": 250 * CRORE,
    "not telling the Board or people about a breach": 200 * CRORE,
    "breaking extra duties about children's data": 200 * CRORE,
}
print()
for breach, amount in dpdp.items():
    print(f"up to Rs {amount:>13,}  for {breach}")
print("\nThe biggest GDPR fine so far: EUR 1.2 billion against Meta (Irish DPC, May 2023), for data transfers to the US.")
