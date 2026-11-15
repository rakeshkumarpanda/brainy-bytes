# 1.2 Firewalls, intrusion detection, VPNs and zero trust
# Example "ids" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Two ways an intrusion detection system decides: signatures (known bad) and anomalies (unusual)
import re
import statistics

# 1. Signature rules, in the spirit of Snort and Suricata: a port plus a pattern in the payload
SIGNATURES = [
    (80, re.compile(r"\.\./\.\./"), "path traversal attempt"),
    (80, re.compile(r"(?i)union\s+select"), "SQL injection attempt"),
    (22, re.compile(r"^SSH-1\."), "old SSH version 1"),
]
traffic = [
    (80, "GET /index.html HTTP/1.1"),
    (80, "GET /../../etc/passwd HTTP/1.1"),
    (80, "GET /item?id=1 UNION SELECT password FROM users"),
    (22, "SSH-2.0-OpenSSH_9.6"),
]
for port, payload in traffic:
    hits = [name for p, rx, name in SIGNATURES if p == port and rx.search(payload)]
    print(f"port {port}: {payload[:40]:40} -> {', '.join(hits) or 'no alert'}")

# 2. Anomaly detection: learn normal login failures per minute, alert when far from normal
normal = [3, 5, 4, 6, 2, 5, 4, 3, 6, 4, 5, 3]
mean, sd = statistics.mean(normal), statistics.pstdev(normal)
print(f"normal: mean {mean:.2f}, standard deviation {sd:.2f}")
for minute, failures in enumerate([4, 7, 41, 5], start=1):
    z = (failures - mean) / sd
    print(f"minute {minute}: {failures:3} failures, z = {z:5.1f} -> {'ALERT' if abs(z) > 3 else 'normal'}")

# 3. How good is the detector? Precision and recall from a labelled test
tp, fp, fn = 90, 10, 30
precision, recall = tp / (tp + fp), tp / (tp + fn)
print(f"precision {precision:.2f}, recall {recall:.2f}, F1 {2 * precision * recall / (precision + recall):.2f}")
