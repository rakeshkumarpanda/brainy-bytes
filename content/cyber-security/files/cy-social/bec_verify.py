# 4.1 Social engineering and phishing: tricks, email authentication and defences
# Example "bec_verify" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Business email compromise: a payment change rule that would have stopped most cases
from datetime import date

vendors = {"Shakti Steel": {"account": "HDFC 5011 2233", "phone": "+91 22 4000 1111"}}

requests = [
    {"vendor": "Shakti Steel", "new_account": "HDFC 5011 2233", "amount": 450000, "via": "email", "urgent": False},
    {"vendor": "Shakti Steel", "new_account": "YES 9988 7766", "amount": 1850000, "via": "email", "urgent": True},
]

def check_payment(r, called_back=False):
    v = vendors[r["vendor"]]
    flags = []
    if r["new_account"] != v["account"]:
        flags.append("bank details changed")
    if r["urgent"]:
        flags.append("urgent or secret")
    if r["amount"] >= 1_000_000:
        flags.append("large amount")
    if "bank details changed" in flags and not called_back:
        return "HOLD: call the vendor on " + v["phone"] + " (from your records, never from the email)", flags
    return "pay", flags

for r in requests:
    decision, flags = check_payment(r)
    print(f"Rs {r['amount']:>9,}  flags {flags}  -> {decision}")

# the 2024 Hong Kong case: about 25 million US dollars sent after a deepfake video call
print("\nRule of thumb: a request to move money or change bank details is confirmed on a second channel")
print("you already trust, such as a known phone number, before anything is paid.")
