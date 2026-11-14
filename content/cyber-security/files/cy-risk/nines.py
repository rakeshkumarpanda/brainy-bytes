# 1.2 Risk in numbers: matrices, ALE, attack trees and continuity
# Example "nines" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Availability and downtime: how many minutes per year can a service be down?
minutes_per_year = 365 * 24 * 60

for availability in [0.99, 0.999, 0.9999, 0.99999]:
    down = (1 - availability) * minutes_per_year
    print(str(availability * 100) + "% up ->", round(down, 1), "minutes down per year")

# Availability from failures: MTBF = mean time between failures, MTTR = mean time to repair
mtbf = 1000   # hours
mttr = 2      # hours
print("availability =", round(mtbf / (mtbf + mttr), 5))
