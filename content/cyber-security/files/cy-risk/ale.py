# 1.2 Risk in numbers: matrices, ALE, attack trees and continuity
# Example "ale" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Quantitative risk: how much money a risk is expected to cost each year
asset_value = 2000000        # AV: value of the customer database in rupees
exposure_factor = 0.4        # EF: share of the value lost in one incident (40%)
aro = 0.5                    # ARO: incidents expected per year (once every 2 years)

sle = asset_value * exposure_factor      # single loss expectancy: cost of ONE incident
ale = sle * aro                          # annualised loss expectancy: cost per YEAR
print("SLE (one incident):", sle)
print("ALE (per year):    ", ale)

# A control cuts the ARO to 0.1 and costs 60,000 rupees a year. Is it worth it?
ale_after = sle * 0.1
control_cost = 60000
value = ale - ale_after - control_cost
print("ALE after the control:", ale_after)
print("value of the control per year:", value)
if value > 0:
    print("worth buying")
else:
    print("costs more than it saves")
