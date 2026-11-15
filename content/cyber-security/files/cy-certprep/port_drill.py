# 3.1 Certification revision: exams, recall, formulas and scenarios
# Example "port_drill" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A port and protocol drill: the facts every security exam expects you to know
import random

PORTS = {
    20: "FTP data", 21: "FTP control", 22: "SSH, SFTP, SCP", 23: "Telnet (plain text, avoid)",
    25: "SMTP", 53: "DNS", 67: "DHCP server", 80: "HTTP", 88: "Kerberos", 110: "POP3",
    123: "NTP", 143: "IMAP", 161: "SNMP", 389: "LDAP", 443: "HTTPS", 445: "SMB",
    514: "Syslog", 636: "LDAPS", 993: "IMAPS", 995: "POP3S", 1812: "RADIUS authentication",
    3389: "RDP",
}
SECURE = {"Telnet (plain text, avoid)": "SSH 22", "HTTP": "HTTPS 443", "LDAP": "LDAPS 636",
          "IMAP": "IMAPS 993", "POP3": "POP3S 995", "FTP control": "SFTP 22 or FTPS 990"}

random.seed(7)
quiz = random.sample(sorted(PORTS), 8)
for port in quiz:
    print(f"port {port:5d}  ->  {PORTS[port]}")

print("\nplain text protocol and its secure replacement:")
for old, new in SECURE.items():
    print(f"  {old:28s} -> {new}")

well_known = sum(1 for p in PORTS if p < 1024)
print(f"\n{well_known} of {len(PORTS)} ports here are well known (below 1024), so only administrators can open them on Linux by default")
