# 2.2 Networks for security: layers, addresses, subnets, TCP and DNS
# Example "ip_header" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Read a real IPv4 header from its 20 bytes (written in hex) and check its checksum
header_hex = "45000073000040004011b861c0a80001c0a800c7"
data = bytes.fromhex(header_hex)

version = data[0] >> 4                 # top 4 bits
header_words = data[0] & 0x0F          # bottom 4 bits: length in 32 bit words
total_length = data[2] * 256 + data[3]
ttl = data[8]
protocol = data[9]
names = {1: "ICMP", 6: "TCP", 17: "UDP"}
source = ".".join(str(b) for b in data[12:16])
destination = ".".join(str(b) for b in data[16:20])

print("version", version, "| header", header_words * 4, "bytes | total", total_length, "bytes")
print("time to live", ttl, "| protocol", protocol, names.get(protocol, "?"))
print("from", source, "to", destination)

# The checksum: add the header as 16 bit numbers, fold the carries back in.
# A correct header (checksum field included) adds up to 0xFFFF.
total = 0
for i in range(0, 20, 2):
    total = total + data[i] * 256 + data[i + 1]
while total > 0xFFFF:
    total = (total & 0xFFFF) + (total >> 16)
print("sum with carries folded:", hex(total), "->", "header is intact" if total == 0xFFFF else "header is damaged")
