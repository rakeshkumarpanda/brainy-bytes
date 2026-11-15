# Network and Systems 1.2: firewalls, intrusion detection, VPNs and zero trust. Checked against Cheswick and Bellovin
# (1994), Denning, An Intrusion-Detection Model (1987), Axelsson, The Base-Rate Fallacy (2000), Snort and Suricata rule
# docs, RFC 4301 and RFC 7296 (IPsec, IKEv2), Donenfeld, WireGuard (NDSS 2017), Ward and Beyer, BeyondCorp (2014) and
# NIST SP 800-207 (2020).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-firewall')
K = Kit()

K.code('firewall', r'''
# A tiny firewall: ordered rules, first match wins, default deny, plus a state table for replies
from ipaddress import ip_address, ip_network

RULES = [                                # (action, protocol, source network, destination port)
    ("allow", "tcp", "0.0.0.0/0", 443),     # anyone may reach the web server over HTTPS
    ("allow", "tcp", "10.0.0.0/8", 22),     # only the office network may use SSH
    ("deny",  "tcp", "0.0.0.0/0", 23),      # Telnet is never allowed (and logged)
]                                        # anything else falls to the default: deny

def stateless(proto, src, dport):
    for number, (action, p, net, port) in enumerate(RULES, start=1):
        if p == proto and ip_address(src) in ip_network(net) and port == dport:
            return action, f"rule {number}"
    return "deny", "default rule"

packets = [("tcp", "203.0.113.5", 443), ("tcp", "10.1.2.3", 22), ("tcp", "203.0.113.5", 22),
           ("tcp", "198.51.100.7", 23), ("udp", "203.0.113.5", 53)]
for proto, src, dport in packets:
    action, why = stateless(proto, src, dport)
    print(f"{proto} {src:14} -> port {dport:<4} {action.upper():5} ({why})")

# Stateful: remember connections we started, and let only their replies back in
state = set()
def outbound(src, sport, dst, dport):
    state.add((dst, dport, src, sport))  # the reply will come back with the addresses swapped

def inbound_allowed(src, sport, dst, dport):
    return (src, sport, dst, dport) in state

outbound("10.0.0.5", 51000, "192.0.2.80", 443)
print("reply from the web server allowed:", inbound_allowed("192.0.2.80", 443, "10.0.0.5", 51000))
print("unsolicited packet allowed:      ", inbound_allowed("203.0.113.9", 443, "10.0.0.5", 51000))
''', long=True)

K.code('ids', r'''
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
''', long=True)

K.code('tunnel', r'''
# What a VPN tunnel does: wrap the whole inner packet, encrypted, inside a new outer packet
# Toy cipher built from SHA-256 so it runs anywhere. Real VPNs use ChaCha20-Poly1305 or AES-GCM.
import hashlib
import hmac
import secrets

KEY = secrets.token_bytes(32)            # agreed by a handshake (WireGuard uses Noise with X25519)

def keystream(nonce, length):
    out = b""
    counter = 0
    while len(out) < length:
        out += hashlib.sha256(KEY + nonce + counter.to_bytes(4, "big")).digest()
        counter += 1
    return out[:length]

def seal(inner):
    nonce = secrets.token_bytes(12)
    body = bytes(a ^ b for a, b in zip(inner, keystream(nonce, len(inner))))
    tag = hmac.new(KEY, nonce + body, hashlib.sha256).digest()[:16]
    return nonce + body + tag

def open_(sealed):
    nonce, body, tag = sealed[:12], sealed[12:-16], sealed[-16:]
    if not hmac.compare_digest(tag, hmac.new(KEY, nonce + body, hashlib.sha256).digest()[:16]):
        return None                      # tampered or wrong key: drop the packet
    return bytes(a ^ b for a, b in zip(body, keystream(nonce, len(body))))

inner = b"src=10.8.0.2 dst=10.20.0.15 | GET /payroll HTTP/1.1"
outer = {"src": "198.51.100.20", "dst": "203.0.113.1 (VPN gateway)", "udp_port": 51820, "payload": seal(inner)}
print("on the wire, anyone sees:", outer["src"], "->", outer["dst"], "udp", outer["udp_port"])
print("payload bytes look random:", outer["payload"][:16].hex(), "...")
print("gateway opens it:", open_(outer["payload"]))
tampered = bytearray(outer["payload"])
tampered[20] ^= 1                        # flip one bit on the way
print("a changed bit is caught:", open_(bytes(tampered)))

# The cost: every packet carries extra headers, so the inner packet must be smaller
for name, overhead in (("WireGuard over IPv4", 20 + 8 + 32), ("WireGuard over IPv6", 40 + 8 + 32)):
    print(f"{name}: overhead {overhead} bytes, inner MTU = 1500 - {overhead} = {1500 - overhead}")
''', long=True)

K.code('zero_trust', r'''
# Zero trust: decide every request on identity, device and context, never on network location alone
def decide(req):
    reasons = []
    if not req["user_verified"]:
        return "deny", ["user not signed in"]
    if not req["device_managed"] or not req["disk_encrypted"] or req["os_patch_days"] > 30:
        return "deny", ["device fails health check"]
    if req["resource"] == "payroll" and req["role"] != "finance":
        return "deny", ["role not allowed for payroll"]
    if req["new_location"] or req["resource"] == "payroll":
        reasons.append("step up: ask for a passkey or MFA again")
        return "challenge", reasons
    return "allow", ["identity, device and role all fine"]

base = {"user_verified": True, "device_managed": True, "disk_encrypted": True, "os_patch_days": 5,
        "role": "engineer", "resource": "wiki", "new_location": False}
cases = {
    "engineer on a healthy laptop opens the wiki": {},
    "same engineer from a new country": {"new_location": True},
    "engineer tries payroll": {"resource": "payroll"},
    "finance user opens payroll": {"role": "finance", "resource": "payroll"},
    "unpatched laptop, even inside the office": {"os_patch_days": 90},
}
for label, change in cases.items():
    verdict, why = decide({**base, **change})
    print(f"{label:45} -> {verdict.upper():9} ({', '.join(why)})")
''', long=True)

K.lesson('idea', 'Defence in depth: layers between attacker and data', f'''
{talk('No single control stops every attack, so defenders stack several, each catching what the others miss. This idea is called defence in depth, borrowed from military thinking. For networks the first layers are firewalls, which decide which traffic may pass, intrusion detection systems, which watch traffic for signs of attack, and virtual private networks, which carry traffic safely across networks you do not trust. Firewalls grew out of packet filtering routers in the late 1980s, and William Cheswick and Steven Bellovin’s 1994 book Firewalls and Internet Security made the idea mainstream. Dorothy Denning described intrusion detection in 1987. For years the model was a castle with a moat: a hard perimeter around a trusted inside. That model failed when attackers got inside through phishing or a supplier, then moved freely. In the 2013 Target breach, attackers entered with stolen credentials from a heating and ventilation contractor and reached the payment systems. Google, after the Operation Aurora attacks of 2009, rebuilt its access model so that no network is trusted, which became zero trust. This chapter covers each layer, how it works inside, and how to measure whether it works.')}
{src('Cheswick and Bellovin, Firewalls and Internet Security (1994), Denning (IEEE TSE 1987), Axelsson (ACM TISSEC 2000), Snort 3 and Suricata documentation, RFC 4301 (IPsec architecture), RFC 7296 (IKEv2), Donenfeld, WireGuard: Next Generation Kernel Network Tunnel (NDSS 2017), Ward and Beyer, BeyondCorp (login 2014), NIST SP 800-207 Zero Trust Architecture (2020), NIST SP 800-41 r1 (firewall policy).')}
{wwh('<b>Network defences</b>: a firewall enforces a traffic policy, an IDS or IPS detects (and an IPS also blocks) attacks in traffic, a VPN gives an encrypted tunnel, and zero trust checks every request on identity and device instead of location.',
     'Each layer lowers risk in a different way: firewalls shrink what is reachable, IDS shortens the time attackers stay unnoticed, VPNs protect data in transit, and zero trust limits how far a stolen account can go.',
     'Firewalls match packet fields against ordered rules and track connection state. IDS match signatures or score anomalies. VPNs encapsulate and encrypt packets. Zero trust puts a policy decision point in front of every resource.')}
{table(['Layer', 'Question it answers', 'Typical products and tools'], [
    ['Perimeter firewall', 'Which traffic may enter or leave?', 'nftables, pf, cloud security groups, next generation firewalls'],
    ['DMZ and segmentation', 'If one zone falls, what else is reachable?', 'VLANs, subnets, microsegmentation'],
    ['IDS / IPS', 'Does this traffic look like an attack?', 'Snort, Suricata, Zeek'],
    ['VPN', 'Can we cross an untrusted network safely?', 'WireGuard, IPsec, OpenVPN'],
    ['Zero trust access', 'Should this user, on this device, reach this app now?', 'Identity aware proxies, BeyondCorp style gateways']])}
''', kw=['defence in depth', 'perimeter', 'castle and moat', 'DMZ', 'Target breach', 'Operation Aurora', 'firewall', 'IDS', 'VPN', 'zero trust'])

K.lesson('firewall', 'Firewalls: rules, state and order', f'''
{talk('A firewall compares each packet with an ordered list of rules. A rule names fields such as protocol, source address, destination address and port, and an action, allow or deny. The first rule that matches decides, so order matters. If a broad allow rule sits above a narrow deny rule, the deny is never reached, a mistake called shadowing. Good policy ends with a default deny, so anything not clearly allowed is blocked. The earliest firewalls were stateless packet filters: they judged each packet alone, which made return traffic awkward, because replies had to be allowed by separate rules. Stateful firewalls, popularised by Check Point FireWall-1 in 1994, keep a table of connections that were started from inside, and let only matching replies back in. Application layer firewalls and proxies understand protocols such as HTTP, and next generation firewalls add user identity, application recognition and intrusion prevention. A web application firewall sits in front of a website and blocks attacks like SQL injection. On Linux, nftables replaced iptables from 2014, and every cloud offers security groups that are stateful firewalls attached to each server. A common design puts public servers in a demilitarised zone, a separate network between the internet and the internal network, so a hacked web server cannot reach internal systems directly.')}
{viz('cyfirewall')}
{run('firewall')}
{wwh('<b>A firewall</b> enforces a policy on traffic between networks or hosts, using ordered rules over packet fields and, when stateful, a connection table.',
     'It reduces the attack surface: services that are not reachable cannot be attacked from outside, and outbound rules make it harder for malware to call home.',
     'Check rules top down, first match wins, default deny. A stateful firewall adds each outbound connection to a table and allows inbound packets only if they match an entry with addresses and ports swapped.')}
{table(['Type', 'Looks at', 'Strength', 'Weakness'], [
    ['Stateless packet filter', 'Header fields of each packet', 'Very fast, simple', 'No idea of connections, easy to get wrong'],
    ['Stateful firewall', 'Headers plus a connection table', 'Replies handled safely, default for hosts and clouds', 'State table can be flooded'],
    ['Application proxy / WAF', 'Application data such as HTTP', 'Blocks SQL injection and similar', 'Slower, must understand each protocol'],
    ['Next generation firewall', 'Applications, users, threats', 'One box with IPS, TLS inspection, identity', 'Cost, complexity, TLS inspection privacy issues'],
    ['Host firewall', 'Traffic of one machine', 'Protects inside the network too', 'Must be managed on every host']])}
{fxs(fx('First match', 'action = action of the smallest i with match(rule<sub>i</sub>, packet), else default', 'TCP 22 from 203.0.113.5 fails rules 1 and 2, so the default deny applies.', key=True),
     fx('State table size', 'entries &asymp; new connections per second &times; idle timeout', '2000 per second &times; 120 s = 240000 entries (Little’s law again).'))}
{note('Write rules from the most specific to the most general, log denies, and review the rule set regularly. Old allow rules for projects that ended are a common way in.', 'tip')}
''', kw=['firewall', 'packet filter', 'stateless', 'stateful', 'connection tracking', 'first match', 'default deny', 'shadowing', 'Check Point', 'next generation firewall', 'web application firewall', 'WAF', 'nftables', 'iptables', 'security groups', 'DMZ'])

K.lesson('ids', 'Intrusion detection and prevention', f'''
{talk('An intrusion detection system watches network traffic or host activity and raises alerts when something looks like an attack. An intrusion prevention system sits in the path of traffic and can also drop it. There are two main ways to decide. Signature based detection matches known patterns, such as a path traversal string in a web request or the bytes of a known exploit. Snort, written by Martin Roesch in 1998, and Suricata, released in 2010, are the best known open source engines, and their rules combine ports, protocol details and content patterns. Signatures are precise but blind to new attacks. Anomaly based detection, proposed by Dorothy Denning in 1987, learns what normal looks like and flags large deviations, for example a sudden burst of failed logins. It can catch new attacks but raises more false alarms. Zeek, started by Vern Paxson as Bro in the mid 1990s, takes a third approach: it turns traffic into rich logs of connections, DNS queries and certificates that analysts and scripts can search. The hardest problem is the base rate. Attacks are rare among billions of events, so even a detector with a tiny false alarm rate produces mostly false alarms, a point Stefan Axelsson made in 2000. That is why tuning, context and good metrics such as precision and recall matter as much as detection itself.')}
{viz('cyids')}
{run('ids')}
{wwh('<b>IDS</b> (detect and alert) and <b>IPS</b> (detect and block) inspect network traffic (NIDS) or host activity (HIDS) for attacks, using signatures, anomaly scores or both.',
     'Firewalls allow some traffic by design, and attacks hide inside allowed traffic. Detection shortens the time an attacker stays unnoticed, which reports put at days to months.',
     'Signatures: match fields and content patterns. Anomalies: model normal (mean and standard deviation, or machine learning) and alert beyond a threshold. Measure with a labelled test set: precision, recall, F1.')}
{fxs(fx('z score', 'z = (x &minus; &mu;) / &sigma;, alert if z &gt; k', 'Normal failures: &mu; = 4.17, &sigma; = 1.21. 41 failures gives z &asymp; 30.4, an alert. With k = 3, about 0.27% of normal minutes still cross the line (two sided, for a normal distribution).', key=True),
     fx('Precision and recall', 'P = TP / (TP + FP), R = TP / (TP + FN), F1 = 2PR / (P + R)', 'TP = 90, FP = 10, FN = 30: P = 0.90, R = 0.75, F1 = 0.82.', key=True),
     fx('Base rate (Bayes)', 'P(attack | alert) = P(alert | attack) P(attack) / P(alert)', 'Detection 99.9%, false alarms 0.1%, attacks 1 in 100000 events: only about 1% of alerts are real.', key=True),
     fx('EWMA baseline', 'S<sub>t</sub> = &alpha;x<sub>t</sub> + (1 &minus; &alpha;)S<sub>t&minus;1</sub>', '&alpha; = 0.2, S = 100, x = 150: S = 110. The baseline follows slow change but not sudden bursts.'))}
{table(['Approach', 'Finds', 'False alarms', 'Example'], [
    ['Signature', 'Known attacks precisely', 'Few, if rules are good', 'Snort and Suricata rules, YARA for files'],
    ['Anomaly', 'New and unusual behaviour', 'More, needs tuning', 'Login burst, data leaving at night'],
    ['Network security monitoring', 'Evidence for investigation', 'Not an alarm by itself', 'Zeek logs, full packet capture'],
    ['Host IDS', 'File changes, suspicious processes', 'Moderate', 'OSSEC, Wazuh, EDR agents']])}
''', kw=['intrusion detection', 'IDS', 'IPS', 'NIDS', 'HIDS', 'signature', 'anomaly detection', 'Snort', 'Suricata', 'Zeek', 'Bro', 'Denning', 'z score', 'EWMA', 'precision', 'recall', 'F1', 'base rate fallacy', 'Axelsson'])

K.lesson('vpn', 'VPNs: IPsec, TLS VPNs and WireGuard', f'''
{talk('A virtual private network builds an encrypted tunnel across a network you do not trust, such as the internet or café Wi-Fi. Each original packet is encrypted and wrapped inside a new packet addressed to the other end of the tunnel, which unwraps it and forwards it. Site to site VPNs join office networks. Remote access VPNs connect a laptop to the company network. Consumer VPNs send all of a user’s traffic through a provider, which hides it from the local network but makes the provider the party you must trust. The oldest standard is IPsec, designed in the 1990s, whose Encapsulating Security Payload protects packets and whose IKE protocol, now IKEv2, agrees keys. It is powerful but complex. TLS based VPNs such as OpenVPN, from 2001, run over ordinary TLS and pass easily through firewalls. WireGuard, designed by Jason Donenfeld and published in 2017, uses a small fixed set of modern algorithms, Curve25519, ChaCha20-Poly1305 and BLAKE2s, in about 4000 lines of code, and became part of the Linux kernel in 2020. VPN appliances themselves are prime targets: several serious vulnerabilities in commercial VPN gateways have been exploited at scale, so patching them quickly is essential.')}
{viz('cyvpn')}
{run('tunnel')}
{wwh('<b>A VPN</b> encapsulates packets inside encrypted, authenticated packets between two tunnel endpoints, giving confidentiality and integrity across an untrusted network.',
     'It protects traffic from local eavesdroppers, joins networks securely and gives remote staff access to internal services.',
     'A handshake authenticates both ends and agrees keys (IKEv2, TLS, or the Noise framework in WireGuard). Each packet is then sealed with an AEAD cipher and a counter that stops replay.')}
{table(['VPN', 'Year', 'Crypto', 'Notes'], [
    ['IPsec (ESP with IKEv2)', '1998, IKEv2 2005', 'AES-GCM, SHA-2, DH or ECDH, configurable', 'Standard in routers and site to site links, complex'],
    ['OpenVPN', '2001', 'TLS with configurable ciphers', 'Runs over UDP or TCP 443, flexible'],
    ['WireGuard', '2017, Linux 5.6 in 2020', 'Curve25519, ChaCha20-Poly1305, BLAKE2s (fixed)', 'Small and fast, about 4000 lines'],
    ['SSL VPN appliances', '2000s', 'TLS', 'Common, and a frequent target when unpatched']])}
{fxs(fx('Tunnel MTU', 'inner MTU = link MTU &minus; outer IP &minus; UDP &minus; tunnel header and tag', 'WireGuard over IPv6: 1500 &minus; 40 &minus; 8 &minus; 32 = 1420, the default. Over IPv4: 1440.', key=True))}
''', kw=['VPN', 'tunnel', 'encapsulation', 'IPsec', 'ESP', 'IKEv2', 'OpenVPN', 'WireGuard', 'Noise protocol', 'ChaCha20-Poly1305', 'site to site', 'remote access', 'MTU'])

K.lesson('zerotrust', 'Zero trust and segmentation', f'''
{talk('Zero trust is the idea that no request should be trusted just because it comes from inside the network. The term was popularised by John Kindervag at Forrester in 2010. Google’s BeyondCorp, described in 2014, was the first large implementation: employees reach internal applications through an access proxy from any network, and each request is checked against who the user is, whether their device is managed and healthy, and what they are allowed to do. NIST published Special Publication 800-207 on zero trust architecture in 2020. The core parts are a policy engine that decides, a policy enforcement point in front of each resource, strong identity with multi factor authentication or passkeys, device health checks, least privilege, and continuous monitoring. Segmentation is the network side of the same idea. Instead of one flat network, systems are divided into zones, and with microsegmentation each workload talks only to what it needs. This limits lateral movement, where an attacker who takes one machine hops to the next. Zero trust is not a product you buy but a direction, usually reached step by step, starting with identity and the most valuable data.')}
{run('zero_trust')}
{wwh('<b>Zero trust</b>: never trust, always verify. Every access is decided on identity, device health and context, with least privilege, no matter where the request comes from.',
     'Perimeters fail through phishing, stolen VPN credentials and suppliers. Zero trust limits what a stolen account or a hacked laptop can reach.',
     'A policy decision point evaluates each request using identity, device posture, resource sensitivity and signals such as location. A policy enforcement point allows, denies or asks for step up authentication.')}
{steps('Moving towards zero trust', [
    'List your users, devices, applications and data, and mark the most valuable.',
    'Make identity strong: single sign on, MFA or passkeys for everyone.',
    'Check device health: managed, patched, disk encrypted, endpoint protection running.',
    'Put applications behind an identity aware proxy instead of a flat VPN.',
    'Segment the network so each workload reaches only what it needs.',
    'Log every decision and watch for unusual access.'])}
{fxs(fx('Microsegmentation pairs', 'possible directed flows = n(n &minus; 1)', '50 workloads: 2450 possible flows. Allowing only the few dozen that are needed removes most paths for lateral movement.', key=True))}
''', kw=['zero trust', 'BeyondCorp', 'NIST SP 800-207', 'Kindervag', 'policy decision point', 'policy enforcement point', 'device posture', 'least privilege', 'segmentation', 'microsegmentation', 'lateral movement', 'identity aware proxy'])

K.lesson('versus', 'Network defences compared', f'''
{talk('Students often mix up firewalls, intrusion detection and VPNs, because all three sit on the network. A firewall decides what is allowed, an IDS notices what is bad among the allowed traffic, an IPS does both in line, a VPN protects traffic while it crosses an untrusted network, and zero trust moves the decision from the network to each application request. They work together. A firewall without monitoring leaves you blind to attacks through open ports, and a VPN without zero trust can give a stolen account access to everything inside.')}
{versus('Network defences side by side', ['', 'Firewall', 'IDS', 'IPS', 'VPN', 'Zero trust'], [
    ['Main job', 'Allow or block by policy', 'Detect and alert', 'Detect and block in line', 'Encrypt traffic across untrusted networks', 'Decide each request on identity and device'],
    ['Placement', 'Network edges, hosts, cloud', 'Copy of traffic (tap or span port)', 'In the traffic path', 'Endpoints and gateways', 'In front of every application'],
    ['Risk if wrong', 'Open holes, or blocked business', 'Missed attacks, alert fatigue', 'Blocking real users', 'Gateway flaws expose the network', 'Complex rollout, user friction'],
    ['Stops', 'Unwanted connections', 'Nothing by itself', 'Known attacks in traffic', 'Eavesdropping and tampering', 'Stolen account moving laterally'],
    ['Examples', 'nftables, security groups', 'Zeek, Suricata in IDS mode', 'Suricata inline, NGFW', 'WireGuard, IPsec', 'BeyondCorp, identity aware proxies']],
    'Use all of them: default deny firewalls, monitoring with tuned alerts, modern VPNs kept patched, and a steady move to zero trust access.')}
''', kw=['comparison', 'firewall versus IDS', 'IDS versus IPS', 'VPN', 'zero trust'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that a firewall blocks unwanted traffic, that a VPN encrypts traffic on public Wi-Fi, and that companies watch for attacks. A college student writes firewall rules with default deny, explains stateful inspection, reads a Snort or Suricata rule, computes precision, recall and the base rate effect, and configures WireGuard between two virtual machines. A masters student designs segmented networks and zero trust access, tunes detection with statistics and machine learning, studies IPsec and IKEv2 in detail, and understands evasion, where attackers split or encode traffic so the IDS sees something different from the target. Researchers work on encrypted traffic analysis, provable properties of firewall rule sets, high speed pattern matching in hardware, adversarial attacks on machine learning detectors and formal verification of VPN protocols.')}
{ladder(
    '<p>Firewalls block, IDS watch, VPNs encrypt, and zero trust checks every request. No single tool is enough.</p>',
    '<p>First match rules with default deny, stateful tables, DMZ design, signature and anomaly detection, precision, recall and the base rate, and VPN encapsulation with MTU maths.</p>',
    '<p>Rule set analysis (shadowing and redundancy), IDS evasion (fragmentation, Ptacek and Newsham 1998), Zeek scripting, IKEv2 and the Noise framework, zero trust architecture per SP 800-207, microsegmentation.</p>',
    '<p>Encrypted traffic classification, adversarial ML against detectors, hardware pattern matching (Aho-Corasick at line rate), verified implementations of WireGuard and TLS, and formal models of policy.</p>')}
{grow('Say what each defence does and where it sits.',
      'Write rules, read alerts with precision and recall, and set up a tunnel in a lab.',
      'Design layered architectures and measure their effect.')}
''', kw=['beginner', 'expert', 'IDS evasion', 'Ptacek and Newsham', 'Aho-Corasick', 'encrypted traffic analysis'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Defence in depth</b>: firewalls, IDS and IPS, VPNs and zero trust, each covering others’ gaps. Perimeters alone failed (Target 2013).',
    '<b>Firewall</b>: ordered rules, first match wins, default deny. Stateful tables let replies in. Watch for shadowed rules.',
    '<b>Types</b>: stateless filter, stateful, application proxy and WAF, NGFW, host firewall. DMZ for public servers.',
    '<b>IDS and IPS</b>: signatures (Snort 1998, Suricata 2010) versus anomalies (Denning 1987). Zeek logs everything for analysis.',
    '<b>Maths</b>: z = (x &minus; &mu;)/&sigma;, P = TP/(TP + FP), R = TP/(TP + FN), F1 = 2PR/(P + R). Base rate: most alerts can be false.',
    '<b>VPN</b>: encrypted encapsulation. IPsec with IKEv2, OpenVPN, WireGuard (Curve25519, ChaCha20-Poly1305, 1420 byte MTU).',
    '<b>Zero trust</b>: BeyondCorp 2014, NIST SP 800-207. Identity, device health, least privilege, per request decisions, microsegmentation.'],
    'Next, Network and Systems 1.3: wireless security, from WEP’s failure to WPA3.')}
{files('Three tasks: a first match port filter, a CIDR aware packet filter, and z score anomaly alerts.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does "default deny" mean in a firewall?', ['Deny the first packet', 'Anything not clearly allowed by a rule is blocked', 'Deny only Telnet', 'Turn the firewall off by default'], 1, 'Last rule.', 'It is the safe default: forgotten services stay unreachable.')
K.quiz('e', 'What is the main difference between an IDS and an IPS?', ['An IDS is faster', 'An IPS sits in the traffic path and can block, an IDS only alerts', 'An IDS encrypts traffic', 'There is none'], 1, 'Prevention.', 'IPS is inline, IDS usually watches a copy of the traffic.')
K.quiz('e', 'On café Wi-Fi with HTTPS but no VPN, what can the watcher still see?', ['Your password', 'Which server you connect to, and usually its name', 'Nothing at all', 'The page contents'], 1, 'Headers.', 'IP headers stay readable, and the server name often appears in DNS or the TLS handshake.')
K.quiz('e', 'Zero trust means', ['Trust no one, so block everything', 'Do not trust a request because of network location, verify identity and device every time', 'Use zero passwords', 'Remove all firewalls'], 1, 'Verify.', 'Location inside the office is no longer proof of trust.')
K.quiz('m', 'Rule 1: allow TCP from any to any port. Rule 2: deny TCP to port 23. What happens to Telnet?', ['Denied', 'Allowed, because rule 1 matches first and rule 2 is shadowed', 'Logged and denied', 'Dropped by default'], 1, 'Order.', 'First match wins, so put specific rules above general ones.')
K.quiz('m', 'Why does a stateful firewall not need a rule allowing every inbound reply?', ['Replies are never sent', 'It records outbound connections and allows only packets that match them', 'It trusts port 443', 'It decrypts replies'], 1, 'State table.', 'The reply matches an entry with the addresses and ports swapped.')
K.quiz('m', 'Signature based detection is weak against', ['Known attacks', 'New attacks with no signature yet', 'Port scans', 'Any attack'], 1, 'Zero day.', 'Anomaly detection or behaviour analysis helps there.')
K.quiz('m', 'Which algorithms does WireGuard use?', ['RSA and 3DES', 'Curve25519, ChaCha20-Poly1305 and BLAKE2s', 'MD5 and RC4', 'Any the user picks'], 1, 'Fixed set.', 'No negotiation means less code and no downgrade attacks. A flaw would mean a new version.')
K.quiz('m', 'What does a DMZ protect against?', ['Viruses on laptops', 'A hacked public server reaching the internal network directly', 'Power cuts', 'Phishing'], 1, 'Separate zone.', 'Public servers sit between two firewalls with tight rules into the inside.')
K.quiz('h', 'An IDS has 99.9% detection and 0.1% false alarms, and 1 in 100000 events is an attack. Roughly what fraction of alerts are real?', ['99.9%', 'About 1%', '50%', '0.1%'], 1, 'Axelsson 2000.', '0.999 &times; 10<sup>&minus;5</sup> against 0.001 &times; 0.99999: about 1 real alert in 101.')
K.quiz('h', 'Precision 0.9 and recall 0.75 give an F1 score of about', ['0.83', '0.82', '0.675', '0.9'], 1, 'Harmonic mean.', '2 &times; 0.9 &times; 0.75 / 1.65 = 0.818.')
K.quiz('h', 'Why is the inner MTU of a tunnel smaller than 1500?', ['Encryption compresses data', 'Outer headers and the authentication tag take room in each 1500 byte packet', 'VPNs are slow', 'IPv6 needs it'], 1, 'Overhead.', 'WireGuard over IPv6 adds 80 bytes, so 1420 bytes are left.')
K.quiz('h', 'What is lateral movement?', ['Moving a server rack', 'An attacker using one compromised machine to reach others inside the network', 'Load balancing', 'DNS failover'], 1, 'Hopping.', 'Segmentation and zero trust limit it.')
K.quiz('x', 'In the style of a CMU 18-731 question: Ptacek and Newsham (1998) showed IDS evasion by insertion and evasion. What is the root cause?', ['Weak encryption', 'The IDS reassembles traffic differently from the target host, so they see different data', 'Slow hardware', 'Too many rules'], 1, 'Ambiguity.', 'Overlapping fragments and TTL tricks exploit differences. Normalisation and target based reassembly are the fixes.')
K.quiz('x', 'In the style of an IISc security exam: a firewall rule set has rules r<sub>1</sub> to r<sub>n</sub>. When is r<sub>j</sub> redundant?', ['When it is longer', 'When removing it does not change the decision for any packet', 'When it is a deny rule', 'When it is the last rule'], 1, 'Same function.', 'Shadowed rules are one kind: an earlier rule matches all its packets with a different action, so r<sub>j</sub> never fires.')

K.calc('e', 'Rule 1 allows TCP 443 from anyone, rule 2 allows TCP 22 from 10.0.0.0/8, rule 3 denies TCP 23, rule 4 is default deny. Which rule decides a TCP 22 packet from 203.0.113.5?', '4', 'Check in order.', ['Rule 1: port 443 only.', 'Rule 2: source not in 10.0.0.0/8. Rule 3: port 23 only.', eq('rule 4, default deny')], check=4)
K.calc('e', 'How many addresses does 10.0.0.0/8 contain?', '16777216', '2<sup>32 &minus; 8</sup>.', ['32 &minus; 8 = 24 host bits.', '2<sup>24</sup> = 16777216.', eq('16777216')], check=2 ** 24)
K.calc('e', 'An IDS raised 100 alerts: 90 real attacks, 10 false alarms. What is its precision in percent?', '90', 'TP / (TP + FP).', ['90 / 100.', '= 0.90.', eq('90%')], check=round(100 * 90 / 100))
K.calc('m', 'Same IDS missed 30 attacks. What is its recall in percent?', '75', 'TP / (TP + FN).', ['90 / (90 + 30) = 90 / 120.', '= 0.75.', eq('75%')], check=round(100 * 90 / 120))
K.calc('m', 'With P = 0.9 and R = 0.75, what is F1 in percent? Round to a whole number.', '82', '2PR / (P + R).', ['2 &times; 0.675 = 1.35.', '1.35 / 1.65 = 0.818.', eq('82%')], check=round(100 * 2 * 0.9 * 0.75 / 1.65))
K.calc('m', 'Normal traffic: mean 100 requests per minute, standard deviation 15. A minute has 160. What is the z score?', '4', '(x &minus; &mu;) / &sigma;.', ['160 &minus; 100 = 60.', '60 / 15 = 4.', eq('z = 4')], check=(160 - 100) // 15)
K.calc('m', 'WireGuard over IPv6 adds 40 + 8 + 32 bytes. What inner MTU is left on a 1500 byte link?', '1420', 'Subtract.', ['40 + 8 + 32 = 80.', '1500 &minus; 80.', eq('1420')], check=1500 - 80)
K.calc('m', 'A firewall sees 2000 new connections per second and keeps idle entries for 120 seconds. About how many state table entries does it hold?', '240000', 'Little’s law.', ['L = &lambda;W.', '2000 &times; 120.', eq('240000')], check=2000 * 120)
K.calc('h', 'A SIEM gets 10<sup>9</sup> events a day, and a rule fires falsely on 0.01% of them. How many false alerts a day?', '100000', '10<sup>9</sup> &times; 10<sup>&minus;4</sup>.', ['0.01% = 0.0001.', '10<sup>9</sup> &times; 0.0001 = 10<sup>5</sup>.', eq('100000 false alerts')], check=10 ** 9 // 10 ** 4)
K.calc('h', 'EWMA baseline with &alpha; = 0.2: previous S = 100, new value x = 150. What is the new S?', '110', '&alpha;x + (1 &minus; &alpha;)S.', ['0.2 &times; 150 = 30.', '0.8 &times; 100 = 80.', eq('S = 110')], check=round(0.2 * 150 + 0.8 * 100))
K.calc('h', 'For normal data, about 0.27% of values lie more than 3 standard deviations from the mean. In 10000 normal minutes, about how many false alarms does a 3 sigma rule give?', '27', '10000 &times; 0.0027.', ['0.27% = 0.0027.', '10000 &times; 0.0027 = 27.', eq('about 27')], check=round(10000 * 0.0027))
K.calc('h', 'Detection 99.9%, false alarms 0.1%, attacks 1 in 100000 events. What percent of alerts are real? Round to a whole number.', '1', 'Bayes.', ['True: 0.999 &times; 0.00001 = 0.00000999.', 'False: 0.001 &times; 0.99999 = 0.00099999.', eq('0.00000999 / 0.00100998 &asymp; 1%')], check=round(100 * 0.999e-5 / (0.999e-5 + 0.001 * 0.99999)))
K.calc('x', 'Microsegmentation: how many possible directed flows exist between 50 workloads?', '2450', 'n(n &minus; 1).', ['Each of 50 can talk to 49 others.', '50 &times; 49.', eq('2450')], check=50 * 49)
K.calc('x', 'WireGuard over IPv4 adds 20 + 8 + 32 bytes. What inner MTU is left on a 1500 byte link?', '1440', 'Subtract.', ['20 + 8 + 32 = 60.', '1500 &minus; 60.', eq('1440')], check=1500 - 60)

K.assign('first_match', 'e', 'A first match port filter',
         '<p>Write <code>first_match(rules, port)</code>. Each rule is [port, action], where port is a number or the text "any". Return the action of the first rule that matches the port, or "deny" if none matches.</p>',
         '''
def first_match(rules, port):
    # your code here
    pass
''', [('first_match([[443, "allow"], [23, "deny"]], 443)', 'allow'), ('first_match([[443, "allow"], [23, "deny"]], 22)', 'deny'), ('first_match([["any", "allow"], [23, "deny"]], 23)', 'allow')],
         '''
def first_match(rules, port):
    for rule_port, action in rules:
        if rule_port == "any" or rule_port == port:
            return action
    return "deny"
''', 'Loop over the rules in order and return as soon as one matches. After the loop, return "deny".', '<p>The third test shows shadowing: the deny for port 23 is never reached because "any" matches first.</p>')
K.assign('cidr_filter', 'm', 'A packet filter with networks',
         '<p>Write <code>cidr_filter(rules, src, port)</code>. Each rule is [action, network, port] such as ["allow", "10.0.0.0/8", 22]. A rule matches if <code>src</code> is inside the network and the port is equal. Return the first matching action, or "deny". Use <code>ipaddress.ip_address</code> and <code>ipaddress.ip_network</code>.</p>',
         '''
from ipaddress import ip_address, ip_network

def cidr_filter(rules, src, port):
    # your code here
    pass
''', [('cidr_filter([["allow", "10.0.0.0/8", 22]], "10.1.2.3", 22)', 'allow'), ('cidr_filter([["allow", "10.0.0.0/8", 22]], "203.0.113.5", 22)', 'deny'), ('cidr_filter([["deny", "192.168.1.0/24", 80], ["allow", "0.0.0.0/0", 80]], "192.168.1.9", 80)', 'deny'), ('cidr_filter([["deny", "192.168.1.0/24", 80], ["allow", "0.0.0.0/0", 80]], "192.168.2.9", 80)', 'allow')],
         '''
from ipaddress import ip_address, ip_network

def cidr_filter(rules, src, port):
    for action, net, rule_port in rules:
        if ip_address(src) in ip_network(net) and port == rule_port:
            return action
    return "deny"
''', 'ip_address(src) in ip_network(net) tests whether an address is inside a network.', '<p>0.0.0.0/0 contains every IPv4 address, so it is the usual way to write "from anyone".</p>')
K.assign('z_alerts', 'h', 'Z score anomaly alerts',
         '<p>Write <code>z_alerts(counts, k)</code> that returns the list of positions i where |counts[i] &minus; mean| / sd is greater than k. Use the population standard deviation (<code>statistics.pstdev</code>). If the standard deviation is 0, return an empty list.</p>',
         '''
import statistics

def z_alerts(counts, k):
    # your code here
    pass
''', [('z_alerts([4, 5, 3, 6, 4, 5, 4, 3, 6, 4, 40], 3)', [10]), ('z_alerts([1, 2, 3, 4, 5], 1)', [0, 4]), ('z_alerts([5, 5, 5, 5], 2)', [])],
         '''
import statistics

def z_alerts(counts, k):
    mean = statistics.mean(counts)
    sd = statistics.pstdev(counts)
    if sd == 0:
        return []
    return [i for i, x in enumerate(counts) if abs(x - mean) / sd > k]
''', 'Compute mean and pstdev once, guard against sd = 0, then use a list comprehension with enumerate.', '<p>Including the attack in the data raises the mean and sd, which can hide it. Real detectors learn the baseline from clean training data, as the animation does.</p>')

K.must('Layers', 'Defence in depth: firewall, IDS/IPS, VPN, zero trust. Perimeter alone fails (Target 2013, Aurora 2009 led to BeyondCorp).')
K.must('Firewall', 'Ordered rules, first match, default deny, shadowing. Stateless versus stateful (Check Point 1994). WAF, NGFW, DMZ, security groups, nftables.')
K.must('IDS and IPS', 'Signature (Snort 1998, Suricata 2010) versus anomaly (Denning 1987). Zeek logs. IPS inline. Evasion by ambiguous reassembly.')
K.must('Metrics', 'z = (x &minus; &mu;)/&sigma;. P = TP/(TP+FP), R = TP/(TP+FN), F1 = 2PR/(P+R). Base rate: 99.9% detector, 1 in 10<sup>5</sup> attacks, 1% real.')
K.must('VPN', 'Encapsulate and encrypt. IPsec ESP with IKEv2, OpenVPN, WireGuard (Curve25519, ChaCha20-Poly1305, BLAKE2s). MTU 1500 &minus; 80 = 1420.')
K.must('Zero trust', 'Never trust location. Identity, device health, least privilege, per request. NIST SP 800-207 (2020). Microsegmentation limits lateral movement.')

T = K.topic(
    slug='cy-firewall', topic='cy-firewall', step=(1, 'Defending the network', 'cy-s1', 'Network attacks and how to stop them, firewalls, intrusion detection and VPNs, and the security of wireless networks.', 'Intermediate'),
    title='Firewalls, intrusion detection, VPNs and zero trust', short='Firewalls and IDS', badge='1.2', minutes=80,
    lead='The layers that defend a network: firewall rules with first match and default deny, stateful inspection, DMZs and WAFs, signature and anomaly intrusion detection with z scores, precision, recall and the base rate fallacy, VPN tunnels from IPsec to WireGuard with MTU maths, and zero trust access with segmentation.',
    desc='firewall, packet filter, stateful firewall, connection tracking, first match, default deny, rule shadowing, DMZ, web application firewall, WAF, next generation firewall, nftables, iptables, security groups, intrusion detection system, IDS, IPS, Snort, Suricata, Zeek, signature detection, anomaly detection, z score, EWMA, precision, recall, F1, base rate fallacy, VPN, IPsec, IKEv2, ESP, OpenVPN, WireGuard, tunnel MTU, zero trust, BeyondCorp, NIST SP 800-207, microsegmentation, lateral movement, defence in depth',
    summary='firewall rules and state, IDS and IPS with detection maths, VPNs from IPsec to WireGuard, and zero trust.',
    keywords=['firewall', 'stateful', 'default deny', 'IDS', 'IPS', 'Snort', 'Zeek', 'VPN', 'WireGuard', 'zero trust'],
    recap='<p>Firewalls decide, detectors notice, tunnels protect, and zero trust checks every request. Each covers gaps in the others.</p>',
    added='2026-11-15')
