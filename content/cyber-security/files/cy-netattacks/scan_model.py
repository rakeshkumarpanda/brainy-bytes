# 1.1 Network attacks and defences: spoofing, floods, scans and poisoning
# Example "scan_model" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How a port scanner reads a host, on a pretend host defined in this file
toy_host = {22: "open", 80: "open", 443: "open", 23: "closed", 3389: "filtered", 445: "filtered"}

def probe_syn(port):
    """What a SYN probe gets back. Nothing here touches a real network."""
    state = toy_host.get(port, "closed")
    return {"open": "SYN-ACK", "closed": "RST", "filtered": None}[state]

def classify(reply):
    if reply == "SYN-ACK":
        return "open (a service is listening)"
    if reply == "RST":
        return "closed (host is up, nothing listening)"
    return "filtered (no reply: a firewall dropped it)"

for port in (22, 23, 80, 443, 445, 3389, 8080):
    print(f"port {port:5}: reply {str(probe_syn(port)):8} -> {classify(probe_syn(port))}")

# The defender's side: flag a source that touches many ports in a short time
log = [("203.0.113.9", p, t) for t, p in enumerate(range(20, 40))]      # one source, 20 ports in 20 seconds
log += [("198.51.100.4", 443, 3), ("198.51.100.4", 443, 9)]             # a normal visitor
window, limit = 60, 10
by_source = {}
for src, port, t in log:
    if t >= window:                      # only count the last 60 seconds
        continue
    by_source.setdefault(src, set()).add(port)
for src, ports in by_source.items():
    verdict = "PORT SCAN ALERT" if len(ports) > limit else "normal"
    print(f"{src:14} touched {len(ports):2} ports in {window} s -> {verdict}")
