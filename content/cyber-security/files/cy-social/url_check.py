# 4.1 Social engineering and phishing: tricks, email authentication and defences
# Example "url_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A simple phishing link checker: the clues security teams teach, written as code
from urllib.parse import urlparse

BAIT = ("login", "verify", "secure", "update", "kyc", "account", "support")

def clues(url):
    u = urlparse(url)
    host = (u.hostname or "").lower()
    labels = host.split(".")
    found = []
    if u.scheme != "https":
        found.append("not https")
    if host.replace(".", "").isdigit():
        found.append("raw IP address instead of a name")
    if "@" in u.netloc:
        found.append("@ in the address hides the real host")
    if any(l.startswith("xn--") for l in labels):
        found.append("punycode: letters from another alphabet")
    if len(labels) > 3:
        found.append(f"{len(labels)} levels of subdomain")
    if any(b in host for b in BAIT):
        found.append("bait word in the host name")
    if "-" in labels[-2] if len(labels) > 1 else False:
        found.append("hyphen in the registered name")
    return host, found

for url in ["https://www.onlinesbi.sbi/",
            "http://sbi-kyc-update.co/login",
            "https://indiapost.gov.in.track-parcel.top/pay",
            "http://192.168.10.5/paytm",
            "https://www.google.com@evil.example/",
            "https://xn--pple-43d.com/"]:
    host, found = clues(url)
    print(f"{host:36s} {len(found)} clue(s): {', '.join(found) if found else 'none'}")
