# 1.1 Network attacks and defences: spoofing, floods, scans and poisoning
# Example "arp_watch" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# ARP spoofing on a toy network, and a watcher that spots it (like the arpwatch tool)
# Nothing is sent on a real network. The "network" is a list of ARP replies.
replies = [
    ("10.0.0.1", "aa:aa:aa:00:00:01"),   # the real gateway
    ("10.0.0.5", "bb:bb:bb:00:00:05"),   # a laptop
    ("10.0.0.7", "cc:cc:cc:00:00:07"),   # the attacker's own address
    ("10.0.0.1", "cc:cc:cc:00:00:07"),   # forged: the attacker claims to be the gateway
    ("10.0.0.5", "cc:cc:cc:00:00:07"),   # forged: and claims to be the laptop
]

cache = {}                               # the victim's ARP cache: IP -> MAC. ARP has no authentication.
alerts = []
for ip, mac in replies:
    old = cache.get(ip)
    if old is not None and old != mac:
        alerts.append(f"{ip} changed from {old} to {mac}")
    cache[ip] = mac                      # a normal host simply believes the newest reply

print("victim's cache now:")
for ip, mac in cache.items():
    print(f"  {ip:10} -> {mac}")

owners = {}
for ip, mac in cache.items():
    owners.setdefault(mac, []).append(ip)
for mac, ips in owners.items():
    if len(ips) > 1:
        alerts.append(f"{mac} answers for {len(ips)} addresses: {', '.join(ips)}")

print("alerts:")
for a in alerts:
    print("  ", a)
