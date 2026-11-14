# 1.1 What cybersecurity is: goals, threats and layers
# Example "at_least_one" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# If each person clicks a phishing link with chance p, what is the chance that AT LEAST ONE of n people clicks?
# P(nobody clicks) = (1 - p) ** n, so P(at least one) = 1 - (1 - p) ** n

p = 0.03     # 3 people in 100 click

for n in [1, 10, 50, 100, 200]:
    nobody = (1 - p) ** n
    print(n, "people -> chance at least one clicks:", round(1 - nobody, 3))
