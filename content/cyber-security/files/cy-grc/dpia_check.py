# 2.3 Governance, risk, compliance and cyber law
# Example "dpia_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Does this project need a data protection impact assessment (DPIA)? A simple screening like GDPR article 35.
projects = {
    "Staff canteen menu app": {"personal": False, "sensitive": False, "large_scale": False, "monitoring": False, "new_tech": False},
    "Face recognition at office gates": {"personal": True, "sensitive": True, "large_scale": False, "monitoring": True, "new_tech": True},
    "Loyalty card for 5 million shoppers": {"personal": True, "sensitive": False, "large_scale": True, "monitoring": True, "new_tech": False},
}

def needs_dpia(p):
    if not p["personal"]:
        return False, "no personal data"
    flags = [k for k in ("sensitive", "large_scale", "monitoring", "new_tech") if p[k]]
    # common rule of thumb from EU guidance: two or more high risk signs means do a DPIA
    return len(flags) >= 2, ", ".join(flags) if flags else "low risk processing"

for name, p in projects.items():
    need, why = needs_dpia(p)
    print(f"{name:36} {'DPIA needed' if need else 'no DPIA':12} ({why})")
print("\nPrivacy by design (GDPR article 25): build the safeguards in at the start, not after launch.")
