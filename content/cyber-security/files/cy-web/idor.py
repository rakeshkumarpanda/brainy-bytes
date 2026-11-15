# 1.1 The web: sessions, origins, tokens and the OWASP Top 10
# Example "idor" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Broken access control, number 1 in the OWASP Top 10 2021: an insecure direct object reference (IDOR)
INVOICES = {
    1001: {"owner": "alice", "amount": 499},
    1002: {"owner": "bob", "amount": 12000},
    1003: {"owner": "alice", "amount": 75},
}

def get_invoice_buggy(user, invoice_id):
    # The login check passed, so the code trusts the id in the URL: /invoices/1002
    return INVOICES.get(invoice_id, "not found")

def get_invoice_fixed(user, invoice_id):
    inv = INVOICES.get(invoice_id)
    if inv is None or inv["owner"] != user:   # check ownership on the server, every time
        return "not found"                    # same answer for "missing" and "not yours", so ids leak nothing
    return inv

print("alice asks for 1001 (hers):  ", get_invoice_buggy("alice", 1001))
print("alice asks for 1002 (bob's): ", get_invoice_buggy("alice", 1002), " <- data leak")
print("fixed, alice asks for 1002:  ", get_invoice_fixed("alice", 1002))
print("fixed, alice asks for 1003:  ", get_invoice_fixed("alice", 1003))

# Walking the ids is trivial when they are sequential, so attackers loop over them
leaked = [i for i in range(1000, 1005) if isinstance(get_invoice_buggy("alice", i), dict) and INVOICES[i]["owner"] != "alice"]
print("ids alice can read that are not hers (buggy):", leaked)
leaked = [i for i in range(1000, 1005) if isinstance(get_invoice_fixed("alice", i), dict) and INVOICES[i]["owner"] != "alice"]
print("ids alice can read that are not hers (fixed):", leaked)
