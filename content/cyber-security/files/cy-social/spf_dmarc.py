# 4.1 Social engineering and phishing: tricks, email authentication and defences
# Example "spf_dmarc" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A small SPF and DMARC evaluator on made up DNS records (real ones live in DNS TXT records)
import ipaddress

DNS = {
    "bank.example": {"spf": "v=spf1 ip4:203.0.113.0/24 -all", "dmarc": "v=DMARC1; p=reject; rua=mailto:dmarc@bank.example"},
    "bank-example.com": {"spf": "v=spf1 ip4:192.0.2.0/24 -all", "dmarc": None},
}

def spf(domain, ip):
    rec = DNS.get(domain, {}).get("spf")
    if not rec:
        return "none"
    for part in rec.split()[1:]:
        if part.startswith("ip4:") and ipaddress.ip_address(ip) in ipaddress.ip_network(part[4:]):
            return "pass"
    return "fail"

def dmarc_policy(domain):
    rec = DNS.get(domain, {}).get("dmarc")
    if not rec:
        return None
    tags = dict(t.strip().split("=", 1) for t in rec.split(";") if "=" in t)
    return tags.get("p")

def deliver(header_from, envelope_domain, ip, dkim_domain):
    from_dom = header_from.split("@")[1]
    spf_ok = spf(envelope_domain, ip) == "pass" and envelope_domain == from_dom
    dkim_ok = dkim_domain == from_dom
    policy = dmarc_policy(from_dom)
    if spf_ok or dkim_ok:
        return "inbox (DMARC pass)"
    return {"reject": "rejected", "quarantine": "spam folder", "none": "inbox, report sent"}.get(policy, "inbox, no DMARC record")

cases = [("real bank mail", "alerts@bank.example", "bank.example", "203.0.113.25", "bank.example"),
         ("spoofed From", "alerts@bank.example", "evil.example", "198.51.100.66", None),
         ("lookalike domain", "alerts@bank-example.com", "bank-example.com", "192.0.2.10", "bank-example.com"),
         ("forwarded by a list", "alerts@bank.example", "bank.example", "233.252.0.5", "bank.example")]
for name, hf, env, ip, dk in cases:
    print(f"{name:20s} -> {deliver(hf, env, ip, dk)}")
