# 1.2 Risk in numbers: matrices, ALE, attack trees and continuity
# Example "register" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A small risk register: each risk gets likelihood and impact from 1 to 5
risks = [
    ["phishing", 4, 3],
    ["laptop theft", 3, 2],
    ["ransomware", 2, 5],
    ["website down", 3, 3],
    ["flood in server room", 1, 4],
]

def zone(score):
    if score >= 16:
        return "critical"
    if score >= 10:
        return "high"
    if score >= 5:
        return "medium"
    return "low"

for r in risks:
    r.append(r[1] * r[2])          # score = likelihood x impact

risks.sort(key=lambda r: r[3], reverse=True)
appetite = 8
for name, likelihood, impact, score in risks:
    action = "treat" if score > appetite else "accept and watch"
    print(name, "| score", score, "|", zone(score), "|", action)
