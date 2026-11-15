# 1.1 Logging, monitoring and the SIEM
# Example "sigma_rule" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A rule written as data, in the spirit of Sigma: the same rule can be turned into a search for any SIEM.
# This one looks for the Windows security log being cleared (event 1102), a common step to hide an attack.
RULE = {
    "title": "Security event log cleared",
    "attack_technique": "T1070.001 Indicator Removal: Clear Windows Event Logs",
    "level": "high",
    "selection": {"source": "windows", "EventID": "1102"},
    "filter_admin_tool": {"user": "backup-svc"},          # a known, approved job that rotates logs
    "condition": "selection and not filter_admin_tool",
}

events = [
    {"source": "windows", "EventID": "4624", "user": "asha", "host": "PC-22"},
    {"source": "windows", "EventID": "1102", "user": "backup-svc", "host": "DC-1"},
    {"source": "windows", "EventID": "1102", "user": "asha", "host": "PC-22"},
    {"source": "linux", "EventID": "1102", "user": "root", "host": "web1"},
]


def matches(event, block):
    """True if every field in the block has the same value in the event."""
    for field, value in block.items():
        if event.get(field) != value:
            return False
    return True


def rule_fires(event, rule):
    selected = matches(event, rule["selection"])
    filtered = matches(event, rule["filter_admin_tool"])
    return selected and not filtered        # the condition written in the rule


for event in events:
    if rule_fires(event, RULE):
        print(f"[{RULE['level']}] {RULE['title']} on {event['host']} by {event['user']}")
        print(f"        maps to MITRE ATT&CK {RULE['attack_technique']}")
print("The approved backup job and the Linux event did not fire, so the rule stays quiet when it should.")
