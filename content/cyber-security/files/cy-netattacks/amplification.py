# 1.1 Network attacks and defences: spoofing, floods, scans and poisoning
# Example "amplification" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Reflection and amplification: why spoofed UDP requests can flood a victim
factors = {                              # bandwidth amplification factors from US-CERT alert TA14-017A
    "DNS": 54,                           # up to 54 (28 to 54)
    "NTP monlist": 556.9,
    "SSDP": 30.8,
    "CharGEN": 358.8,
    "Memcached": 51000,                  # 10,000 to 51,000, added in 2018
}
bots, upload_mbps = 1000, 1              # each bot sends 1 Mbit/s of spoofed requests
for proto, k in factors.items():
    gbps = bots * upload_mbps * k / 1000
    print(f"{proto:12} x{k:>8}: {bots} bots at {upload_mbps} Mbit/s reflect about {gbps:,.0f} Gbit/s at the victim")
print("(an upper bound: real floods are capped by how many open reflectors exist and their own bandwidth)")

# BCP 38 (ingress filtering): a network drops packets whose source address is not one of its own
my_prefix = "198.51.100."
for src in ("198.51.100.20", "203.0.113.10"):
    print(src, "-> forwarded" if src.startswith(my_prefix) else "-> dropped (spoofed source)")
