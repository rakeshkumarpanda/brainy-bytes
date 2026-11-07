# 1.2 Sockets, TCP and UDP: under HTTP
# Example "ip_ports" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import ipaddress

net = ipaddress.ip_network("192.168.1.0/24")
print(net.num_addresses, "addresses,", net.num_addresses - 2, "for computers")
print("netmask", net.netmask, "and broadcast", net.broadcast_address)
print(ipaddress.ip_address("192.168.1.77") in net)
print(ipaddress.ip_address("192.168.2.5") in net)
print([str(part) for part in net.subnets(new_prefix=26)])
print(ipaddress.ip_address("10.0.0.1").is_private, ipaddress.ip_address("8.8.8.8").is_private)
print(ipaddress.ip_address("::1"), "is IPv6 version", ipaddress.ip_address("::1").version)
print(int(ipaddress.ip_address("192.168.1.1")))     # an IPv4 address is just a 32 bit number

WELL_KNOWN = {22: "SSH", 53: "DNS", 80: "HTTP", 443: "HTTPS", 5432: "PostgreSQL", 6379: "Redis"}
for port, name in WELL_KNOWN.items():
    print(port, name)
