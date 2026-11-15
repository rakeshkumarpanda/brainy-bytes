# 2.2 Cloud security: shared responsibility, identity, settings and keys
# Example "cidr_exposure" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How many addresses can reach our admin ports? Overlapping rules must not be counted twice.
import ipaddress

rules = [
    ("10.0.0.0/24", 22),          # office network may use SSH
    ("10.0.0.128/25", 22),        # a second rule that overlaps the first
    ("203.0.113.0/28", 3389),     # a partner may use Remote Desktop
    ("0.0.0.0/0", 443),           # the website is public, which is fine
]
ADMIN_PORTS = {22, 3389}

admin_nets = [ipaddress.ip_network(cidr) for cidr, port in rules if port in ADMIN_PORTS]
for net in admin_nets:
    print(f"{str(net):16} {net.num_addresses:6} addresses")
merged = list(ipaddress.collapse_addresses(admin_nets))
total = sum(n.num_addresses for n in merged)
print(f"\nafter merging overlaps: {[str(n) for n in merged]} = {total} addresses can reach admin ports")
print(f"if someone writes 0.0.0.0/0 for SSH: {ipaddress.ip_network('0.0.0.0/0').num_addresses} addresses")
