# 2.2 Networks for security: layers, addresses, subnets, TCP and DNS
# Example "subnet_calc" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

import ipaddress

# Work out a subnet by hand with bit operations, then check with Python's ipaddress module
def to_number(ip):
    parts = ip.split(".")
    n = 0
    for p in parts:
        n = n * 256 + int(p)
    return n

def to_ip(n):
    return ".".join(str((n >> shift) & 255) for shift in [24, 16, 8, 0])

address = "192.168.10.77"
prefix = 26

ip = to_number(address)
host_bits = 32 - prefix
mask = (0xFFFFFFFF << host_bits) & 0xFFFFFFFF      # prefix ones, then zeros
network = ip & mask
broadcast = network | (~mask & 0xFFFFFFFF)
hosts = 2 ** host_bits - 2

print("mask:     ", to_ip(mask))
print("network:  ", to_ip(network))
print("broadcast:", to_ip(broadcast))
print("hosts:    ", hosts, "from", to_ip(network + 1), "to", to_ip(broadcast - 1))

check = ipaddress.ip_network(address + "/" + str(prefix), strict=False)
print("ipaddress agrees:", check.network_address, check.broadcast_address, check.num_addresses - 2)
