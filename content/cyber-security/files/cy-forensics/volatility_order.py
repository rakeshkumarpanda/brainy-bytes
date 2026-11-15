# 1.3 Digital forensics: collecting and reading evidence
# Example "volatility_order" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Plan a collection in the order of volatility from RFC 3227: most fragile first
ORDER = {
    "registers and cache": 1,
    "routing table, ARP cache, process table, kernel statistics, memory": 2,
    "temporary file systems": 3,
    "disk": 4,
    "remote logging and monitoring data": 5,
    "physical configuration and network topology": 6,
    "archival media (backups)": 7,
}
found_on_scene = ["disk", "archival media (backups)", "routing table, ARP cache, process table, kernel statistics, memory",
                  "remote logging and monitoring data", "temporary file systems"]

plan = sorted(found_on_scene, key=lambda item: ORDER[item])
for step, item in enumerate(plan, start=1):
    print(f"{step}. collect {item}")
print("\nWrite down the time, the tool and its version, and the hash of everything you collect.")
