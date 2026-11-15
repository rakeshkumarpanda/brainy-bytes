# 2.3 Python for security: bytes, hashes, logs, packets and safe code
# Example "packet_parse" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Reading binary data with struct: a DNS header and the internet checksum
import struct

# A DNS query header is six 16 bit numbers in network byte order ("!" means big endian)
header = struct.pack("!HHHHHH", 0x1A2B, 0x0100, 1, 0, 0, 0)
print("header bytes:", header.hex(), "=", len(header), "bytes")

ident, flags, questions, answers, authority, extra = struct.unpack("!HHHHHH", header)
print("id", hex(ident), " flags", hex(flags), " questions", questions)
print("recursion desired bit:", (flags >> 8) & 1)

# The internet checksum (RFC 1071), used in IPv4, TCP and UDP headers
def checksum(data):
    total = 0
    for i in range(0, len(data), 2):
        total = total + (data[i] << 8) + data[i + 1]
    while total > 0xFFFF:                       # fold the carries back in
        total = (total & 0xFFFF) + (total >> 16)
    return 0xFFFF - total                        # ones complement

ip = bytes.fromhex("450000730000400040110000c0a80001c0a800c7")   # checksum field is 0000 for now
value = checksum(ip)
print("IPv4 header checksum:", hex(value))

fixed = ip[:10] + struct.pack("!H", value) + ip[12:]
print("check the fixed header:", checksum(fixed), "(0 means it is correct)")
