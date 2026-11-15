# 1.2 Firewalls, intrusion detection, VPNs and zero trust
# Example "firewall" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A tiny firewall: ordered rules, first match wins, default deny, plus a state table for replies
from ipaddress import ip_address, ip_network

RULES = [                                # (action, protocol, source network, destination port)
    ("allow", "tcp", "0.0.0.0/0", 443),     # anyone may reach the web server over HTTPS
    ("allow", "tcp", "10.0.0.0/8", 22),     # only the office network may use SSH
    ("deny",  "tcp", "0.0.0.0/0", 23),      # Telnet is never allowed (and logged)
]                                        # anything else falls to the default: deny

def stateless(proto, src, dport):
    for number, (action, p, net, port) in enumerate(RULES, start=1):
        if p == proto and ip_address(src) in ip_network(net) and port == dport:
            return action, f"rule {number}"
    return "deny", "default rule"

packets = [("tcp", "203.0.113.5", 443), ("tcp", "10.1.2.3", 22), ("tcp", "203.0.113.5", 22),
           ("tcp", "198.51.100.7", 23), ("udp", "203.0.113.5", 53)]
for proto, src, dport in packets:
    action, why = stateless(proto, src, dport)
    print(f"{proto} {src:14} -> port {dport:<4} {action.upper():5} ({why})")

# Stateful: remember connections we started, and let only their replies back in
state = set()
def outbound(src, sport, dst, dport):
    state.add((dst, dport, src, sport))  # the reply will come back with the addresses swapped

def inbound_allowed(src, sport, dst, dport):
    return (src, sport, dst, dport) in state

outbound("10.0.0.5", 51000, "192.0.2.80", 443)
print("reply from the web server allowed:", inbound_allowed("192.0.2.80", 443, "10.0.0.5", 51000))
print("unsolicited packet allowed:      ", inbound_allowed("203.0.113.9", 443, "10.0.0.5", 51000))
