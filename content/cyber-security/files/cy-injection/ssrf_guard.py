# 1.2 Injection: SQL, blind SQL, commands, SSRF and paths
# Example "ssrf_guard" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Server side request forgery (SSRF): a "fetch this URL for me" feature can be aimed at internal addresses,
# such as the cloud metadata service at 169.254.169.254. DNS is a dictionary here, nothing is fetched.
import ipaddress
from urllib.parse import urlsplit

FAKE_DNS = {"images.example.org": "93.184.216.34", "internal.corp": "10.0.0.12", "sneaky.example.net": "127.0.0.1"}

def resolve(host):
    try:
        return ipaddress.ip_address(host)              # already an address (also handles IPv6)
    except ValueError:
        pass
    if host.isdigit():                                 # browsers and libraries accept 2130706433 for 127.0.0.1
        return ipaddress.ip_address(int(host))
    return ipaddress.ip_address(FAKE_DNS.get(host, "0.0.0.0"))

def allowed(url):
    u = urlsplit(url)
    if u.scheme not in ("http", "https"):
        return False, "scheme " + u.scheme
    ip = resolve(u.hostname)
    if ip.version == 6 and ip.ipv4_mapped:             # ::ffff:127.0.0.1 is really 127.0.0.1
        ip = ip.ipv4_mapped
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified or ip.is_reserved:
        return False, f"{ip} is internal"
    return True, str(ip)

urls = [
    "https://images.example.org/cat.png",
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "http://internal.corp/admin",
    "http://sneaky.example.net/",                       # public name, private address
    "http://2130706433/",                               # 127.0.0.1 written as one number
    "http://[::ffff:127.0.0.1]/",
    "file:///etc/passwd",
]
for url in urls:
    ok, why = allowed(url)
    print(f"{'ALLOW' if ok else 'BLOCK'}  {url:66} {why}")
print("Also: connect to the address you checked (not a fresh lookup), and do not follow redirects blindly.")
