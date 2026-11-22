# 4.3 IoT and industrial control security: Mirai, Modbus, Purdue and Stuxnet
# Example "default_creds" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Audit your own device inventory for factory passwords (a defender's check, on a made up list)
DEFAULTS = {("admin", "admin"), ("root", "root"), ("admin", "1234"), ("root", "xc3511"),
            ("admin", "password"), ("user", "user"), ("root", "vizxv"), ("support", "support")}

inventory = [
    {"name": "lobby camera", "user": "admin", "password": "admin", "firmware": "2019.04", "telnet": True},
    {"name": "warehouse DVR", "user": "root", "password": "xc3511", "firmware": "2016.11", "telnet": True},
    {"name": "office router", "user": "admin", "password": "T7#qL9!vRm2", "firmware": "2026.09", "telnet": False},
    {"name": "smart TV", "user": "user", "password": "b4Kp!xw8", "firmware": "2025.12", "telnet": False},
]

for d in inventory:
    problems = []
    if (d["user"], d["password"]) in DEFAULTS:
        problems.append("factory password")
    if d["telnet"]:
        problems.append("telnet open (port 23)")
    if int(d["firmware"][:4]) < 2024:
        problems.append(f"old firmware {d['firmware']}")
    print(f"{d['name']:15s} {'; '.join(problems) if problems else 'ok'}")

print("\nThe real Mirai tried about 60 such pairs, including root / xc3511 used by many DVRs and cameras.")
