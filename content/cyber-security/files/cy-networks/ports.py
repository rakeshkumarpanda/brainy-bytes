# 2.2 Networks for security: layers, addresses, subnets, TCP and DNS
# Example "ports" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Well known ports: which service usually listens where, and is the traffic protected?
services = {
    21: ("FTP", "plain text"), 22: ("SSH", "encrypted"), 23: ("Telnet", "plain text"),
    25: ("SMTP mail", "plain unless STARTTLS"), 53: ("DNS", "plain unless DoH or DoT"),
    80: ("HTTP", "plain text"), 443: ("HTTPS", "encrypted"), 445: ("SMB file sharing", "depends"),
    3389: ("RDP remote desktop", "encrypted, but a top target"),
}

open_ports = [22, 80, 443, 23, 3389]
for port in open_ports:
    name, note = services.get(port, ("unknown", "?"))
    if port < 1024:
        band = "well known"
    elif port < 49152:
        band = "registered"
    else:
        band = "dynamic"
    print(port, band, name, "-", note)

risky = [p for p in open_ports if services[p][1] == "plain text"]
print("close or replace these plain text services:", risky)
