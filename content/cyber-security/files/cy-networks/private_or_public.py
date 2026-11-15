# 2.2 Networks for security: layers, addresses, subnets, TCP and DNS
# Example "private_or_public" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

import ipaddress

# Private ranges (RFC 1918) never travel on the public internet. Loopback is the machine itself.
for text in ["10.4.2.1", "172.20.0.9", "192.168.1.1", "8.8.8.8", "127.0.0.1", "172.32.0.1"]:
    ip = ipaddress.ip_address(text)
    if ip.is_loopback:
        kind = "loopback (this computer)"
    elif ip.is_private:
        kind = "private (inside a home or company network)"
    else:
        kind = "public"
    print(text, "->", kind)

# Is an address inside a firewall rule's network?
rule = ipaddress.ip_network("10.0.0.0/8")
print("10.200.3.4 in 10.0.0.0/8?", ipaddress.ip_address("10.200.3.4") in rule)
