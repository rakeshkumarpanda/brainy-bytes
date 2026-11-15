# 2.1 Threat intelligence: knowing the attacker
# Example "stix_share" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Sharing an indicator in a STIX 2.1 style object, marked with a Traffic Light Protocol level
import json

TLP = {
    "TLP:RED": "only the people in the meeting or the named recipients",
    "TLP:AMBER+STRICT": "only inside the recipient's own organisation",
    "TLP:AMBER": "the recipient's organisation and its clients who need it",
    "TLP:GREEN": "the wider community, but not public websites",
    "TLP:CLEAR": "anyone, it can be published",
}

indicator = {
    "type": "indicator",
    "spec_version": "2.1",
    "id": "indicator--6d3f6a6c-0e3c-4d3b-9f1e-7a2b5c9d1e01",
    "name": "Payroll themed phishing C2 domain",
    "pattern": "[domain-name:value = 'update-checker.example']",
    "pattern_type": "stix",
    "valid_from": "2026-11-15T00:00:00Z",
    "valid_until": "2027-02-13T00:00:00Z",
    "labels": ["malicious-activity"],
    "kill_chain_phases": [{"kill_chain_name": "mitre-attack", "phase_name": "command-and-control"}],
    "x_tlp": "TLP:AMBER",
}

text = json.dumps(indicator, indent=2)
print("\n".join(text.splitlines()[:9]) + "\n  ...")
received = json.loads(text)
print(f"\nreceived: {received['name']}")
print(f"look for: {received['pattern']}")
print(f"share with: {TLP[received['x_tlp']]}")
