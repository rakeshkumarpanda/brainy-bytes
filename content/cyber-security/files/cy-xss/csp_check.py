# 1.3 Cross site attacks: XSS, CSP, CSRF and clickjacking
# Example "csp_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How a browser applies a Content Security Policy to the scripts on a page (a simplified model of CSP Level 3)
import base64, hashlib

def parse(policy):
    out = {}
    for part in policy.split(";"):
        words = part.split()
        if words:
            out[words[0]] = words[1:]
    return out

def allowed(policy, script):
    sources = policy.get("script-src", policy.get("default-src", ["*"]))
    kind, value, nonce = script
    if kind == "inline":
        if nonce and f"'nonce-{nonce}'" in sources:
            return True, "nonce matches"
        digest = base64.b64encode(hashlib.sha256(value.encode()).digest()).decode()
        if f"'sha256-{digest}'" in sources:
            return True, "hash matches"
        if "'unsafe-inline'" in sources:
            return True, "'unsafe-inline' allows every inline script"
        return False, "inline script without a valid nonce or hash"
    host = value.split("/")[2]
    if "'strict-dynamic'" in sources:
        return False, "'strict-dynamic': needs the nonce, or a trusted script must load it"
    if host in sources or "*" in sources:
        return True, "host is listed"
    return False, f"{host} is not in script-src"

page_scripts = [
    ("inline", "initMenu()", "r4nd0mN0nc3"),                       # the site's own script, given the nonce
    ("inline", "steal(document.cookie)", None),                    # injected by an attacker through XSS
    ("external", "https://cdn.example.com/lib.js", None),
    ("external", "https://evil.io/x.js", None),
]
policies = {
    "weak": "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.example.com",
    "allow list": "default-src 'self'; script-src 'self' cdn.example.com",
    "strict (nonce)": "default-src 'self'; script-src 'nonce-r4nd0mN0nc3' 'strict-dynamic'; object-src 'none'; base-uri 'none'",
}
for name, text in policies.items():
    p = parse(text)
    print(f"policy {name}: {text}")
    for s in page_scripts:
        ok, why = allowed(p, s)
        label = s[1] if s[0] == "external" else "inline " + s[1]
        print(f"   {'RUN  ' if ok else 'BLOCK'} {label:34} {why}")
    print()
