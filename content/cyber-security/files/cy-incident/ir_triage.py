# 1.2 Incident response: from the first alert to lessons learned
# Example "ir_triage" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Triage: give every incident a priority from its impact and its urgency (each 1 low, 2 medium, 3 high)
def priority(impact, urgency):
    score = impact * urgency
    if score >= 9:
        return "P1 critical: call the response team now, day or night"
    if score >= 6:
        return "P2 high: start within 1 hour"
    if score >= 3:
        return "P3 medium: start today"
    return "P4 low: handle in normal work"

incidents = [
    ("Ransomware renaming files on the main file server", 3, 3),
    ("One laptop with adware pop ups", 1, 2),
    ("Admin account logged in from an unknown country", 3, 2),
    ("Phishing email reported, nobody clicked", 1, 3),
    ("Public website defaced", 2, 3),
]
for name, impact, urgency in sorted(incidents, key=lambda x: -x[1] * x[2]):
    print(f"impact {impact} x urgency {urgency} = {impact * urgency}  {priority(impact, urgency)}")
    print("        " + name)
