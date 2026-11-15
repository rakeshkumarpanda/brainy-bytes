# 1.2 Incident response: from the first alert to lessons learned
# Example "playbook" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A response playbook written as data, run step by step, the way a SOAR tool runs it.
# The case: a user reported a phishing email after typing their password into the fake page.
case = {"user": "meena", "entered_password": True, "mfa_enrolled": False, "forward_rule": True, "others_got_email": 14}

PLAYBOOK = [
    ("Reset password and end all sessions", lambda c: c["entered_password"]),
    ("Enrol user in phishing resistant MFA", lambda c: not c["mfa_enrolled"]),
    ("Delete the mail forwarding rule the attacker made", lambda c: c["forward_rule"]),
    ("Remove the same email from other mailboxes", lambda c: c["others_got_email"] > 0),
    ("Block the phishing domain at the proxy and DNS", lambda c: True),
    ("Ask a human to review sign ins of the last 7 days", lambda c: True),
]

done = 0
for step, (action, needed) in enumerate(PLAYBOOK, start=1):
    if needed(case):
        done += 1
        print(f"step {step}: DO   {action}")
    else:
        print(f"step {step}: skip {action} (not needed for this case)")
print(f"\n{done} actions for {case['user']}. {case['others_got_email']} other people got the email, so check whether any of them clicked too.")
