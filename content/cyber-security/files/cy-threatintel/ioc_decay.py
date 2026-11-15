# 2.1 Threat intelligence: knowing the attacker
# Example "ioc_decay" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Indicators go stale. Model usefulness as halving every h days, and retire an indicator below 10%.
import math

HALF_LIFE = {"file hash": 180, "domain": 30, "ip": 7}     # rough values, tune them on your own data
RETIRE_BELOW = 0.10

for kind, h in HALF_LIFE.items():
    retire_day = h * math.log2(1 / RETIRE_BELOW)
    values = [2 ** (-t / h) for t in (0, 7, 30, 90)]
    print(f"{kind:9} half life {h:3} days | day 0, 7, 30, 90: " + ", ".join(f"{v:.2f}" for v in values) + f" | retire after {retire_day:.1f} days")
print("\nIP addresses change hands fastest, so their indicators age fastest. Behaviour (TTPs) ages slowest of all.")
