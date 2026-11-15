# 2.1 Threat intelligence: knowing the attacker
# Example "attack_coverage" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Map detection rules to MITRE ATT&CK tactics and find the gaps
TACTICS = ["Reconnaissance", "Resource Development", "Initial Access", "Execution", "Persistence",
           "Privilege Escalation", "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
           "Collection", "Command and Control", "Exfiltration", "Impact"]

rules = {
    "Phishing attachment opened": ("T1566", "Initial Access"),
    "PowerShell encoded command": ("T1059.001", "Execution"),
    "New Run key": ("T1547.001", "Persistence"),
    "Event log cleared": ("T1070.001", "Defense Evasion"),
    "Brute force": ("T1110", "Credential Access"),
    "LSASS memory read": ("T1003.001", "Credential Access"),
    "Admin share login": ("T1021.002", "Lateral Movement"),
    "Beaconing to rare domain": ("T1071", "Command and Control"),
    "Mass file rename": ("T1486", "Impact"),
}

count = {t: 0 for t in TACTICS}
for name, (technique, tactic) in rules.items():
    count[tactic] += 1

for tactic in TACTICS:
    bar = "#" * count[tactic]
    print(f"{tactic:21} {count[tactic]}  {bar}")
covered = sum(1 for t in TACTICS if count[t] > 0)
print(f"\ncovered {covered} of {len(TACTICS)} tactics = {covered / len(TACTICS) * 100:.1f}%")
print("gaps:", ", ".join(t for t in TACTICS if count[t] == 0))
