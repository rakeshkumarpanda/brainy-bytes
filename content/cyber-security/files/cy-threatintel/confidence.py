# 2.1 Threat intelligence: knowing the attacker
# Example "confidence" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How sure are we? Update the chance that an IP is malicious as independent sources report it (Bayes with odds).
def to_odds(p):
    return p / (1 - p)

def to_prob(odds):
    return odds / (1 + odds)

prior = 0.20                   # before any report: 1 in 5 IPs on this list turn out to be bad
reports = [
    ("Feed A (reliable, B2 on the Admiralty scale)", 4.0),   # likelihood ratio: how much more likely if really bad
    ("Our own sandbox saw it as C2", 9.0),
    ("Feed C (unknown source, F6)", 1.0),                    # no information: ratio 1 changes nothing
]

odds = to_odds(prior)
print(f"start: P = {prior:.2f}, odds = {odds:.2f}")
for source, ratio in reports:
    odds = odds * ratio
    print(f"after {source}: odds x {ratio} = {odds:.2f}, P = {to_prob(odds):.3f}")
print("\nIndependent sources multiply. Two feeds that copy each other are really one source, so do not count them twice.")
