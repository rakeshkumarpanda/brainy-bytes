# 4.4 API security: BOLA, rate limits, mass assignment and the OWASP API Top 10
# Example "ssrf_guard" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A webhook API fetches a URL that the customer supplies. Refuse internal addresses (no network is used here).
import ipaddress
from urllib.parse import urlsplit

def parse_host(host):
    # also catch numeric forms such as 2852039166, which is 169.254.169.254 written as one number
    try:
        return ipaddress.ip_address(int(host)) if host.isdigit() else ipaddress.ip_address(host)
    except ValueError:
        return None

def check_webhook(url):
    parts = urlsplit(url)
    if parts.scheme != "https":
        return "refuse: https only"
    ip = parse_host(parts.hostname or "")
    if ip is None:
        return "resolve the name, then run this same check on every address it returns"
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
        return f"refuse: {ip} is an internal address"
    return "allow"

for url in ["https://hooks.example.com/in", "https://169.254.169.254/latest/meta-data/",
            "https://2852039166/", "https://127.0.0.1:8080/admin", "https://10.0.3.7/",
            "http://hooks.example.com/in", "https://93.184.215.14/hook"]:
    print(f"{url:45s} {check_webhook(url)}")
