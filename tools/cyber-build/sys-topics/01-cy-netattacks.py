# Network and Systems 1.1: network attacks and defences. Checked against RFC 826 (ARP), RFC 4987 (SYN flooding and
# SYN cookies), Bernstein (1996), US-CERT TA14-017A (amplification factors), RFC 2827 / BCP 38, Kaminsky (2008),
# RFC 5452 (DNS resilience), RFC 4033 (DNSSEC), RFC 8484 (DoH), CVE-2023-44487 (HTTP/2 Rapid Reset) and Nmap docs.
# Every attack here runs on toy data inside the program. Nothing touches a real network.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-netattacks')
K = Kit()

K.code('arp_watch', r'''
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
''', long=True)

K.code('syn_cookies', r'''
# SYN floods and SYN cookies (Bernstein, 1996), with toy numbers
import hashlib
import hmac

# 1. Why a SYN flood fills the queue: half open connections = attack rate x timeout
backlog = 1024                           # slots for half open connections
timeout = 30                             # seconds a server waits for the final ACK
for rate in (10, 30, 50, 100):           # forged SYN packets per second
    half_open = rate * timeout
    state = "FULL: new users refused" if half_open >= backlog else "ok"
    print(f"{rate:4} SYN/s -> {half_open:5} half open of {backlog}  {state}")

# 2. SYN cookies: keep no state, hide it in the server's sequence number instead
SECRET = b"server secret, rotated often"
MSS_TABLE = [536, 1300, 1440, 1460]      # the server can encode one of 4 MSS values in 2 bits

def cookie(src, dst, sport, dport, t, mss_index):
    msg = f"{src},{dst},{sport},{dport},{t}".encode()
    mac = int.from_bytes(hmac.new(SECRET, msg, hashlib.sha256).digest()[:3], "big")   # 24 bits
    return ((t % 32) << 27) | (mss_index << 24) | mac       # 5 + 3 + 24 = 32 bits (we use 2 of the 3)

def check(src, dst, sport, dport, now, ack):
    isn = (ack - 1) % 2 ** 32            # the client acknowledges our sequence number + 1
    t_low, mss_index = isn >> 27, (isn >> 24) & 7
    for t in (now, now - 1):             # accept cookies from this or the previous minute
        if t % 32 == t_low and mss_index < len(MSS_TABLE) and cookie(src, dst, sport, dport, t, mss_index) == isn:
            return MSS_TABLE[mss_index]
    return None

minute = 29_000_000                      # minutes since 1970, a toy clock
isn = cookie("198.51.100.4", "203.0.113.10", 51000, 443, minute, 3)
print("cookie sent as sequence number:", isn)
print("real client ACK accepted, MSS =", check("198.51.100.4", "203.0.113.10", 51000, 443, minute, isn + 1))
print("forged ACK from a guess:       ", check("198.51.100.4", "203.0.113.10", 51000, 443, minute, 123456789))
print("same ACK three minutes later:  ", check("198.51.100.4", "203.0.113.10", 51000, 443, minute + 3, isn + 1))
''', long=True)

K.code('scan_model', r'''
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
''', long=True)

K.code('dns_race', r'''
# DNS cache poisoning: why random source ports matter (Kaminsky, 2008)
import random

def chance(n_forged, space):
    # probability that at least one of n forged replies matches the one value the resolver expects
    return 1 - (1 - 1 / space) ** n_forged

for label, space in (("16 bit query ID only", 2 ** 16), ("ID plus about 16 bits of random port", 2 ** 32)):
    print(f"{label:38}: one race with 100 forged replies wins with p = {chance(100, space):.6f}")

# Kaminsky's trick: ask for random names (a1.bank.test, a2.bank.test, ...) so the attacker can race again and again
races = 0
rng = random.Random(1)
while True:
    races += 1
    if rng.random() < chance(100, 2 ** 16):
        break
print("with a 16 bit ID, the toy attacker won after", races, "races")
print("expected races with port randomisation:", round(1 / chance(100, 2 ** 32)))
''', long=True)

K.code('amplification', r'''
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
''', long=True)

K.lesson('idea', 'Why networks are attacked and what defenders protect', f'''
{talk('The internet was designed in the 1970s and 1980s by researchers who mostly trusted each other. Protocols such as ARP, DNS, TCP and BGP believe what they are told, so an attacker who can send packets can often lie about who they are. In 1988 the Morris worm spread across about a tenth of the internet in a day. In 1994 Kevin Mitnick used TCP sequence number prediction to pose as a trusted computer. In 1996 the internet provider Panix was knocked offline for days by a SYN flood, and in 2016 the Mirai botnet of hacked cameras and routers took down the DNS provider Dyn, and with it sites such as Twitter and Netflix for many users. Network attacks fall into a few families. Eavesdropping and man in the middle attacks break confidentiality and integrity. Denial of service breaks availability. Reconnaissance, such as port scanning, is the first step of most intrusions. Spoofing and poisoning attacks, against ARP, DNS and BGP, redirect traffic to the attacker. This chapter shows how each works on toy data and, more importantly, how defenders detect and stop it. Remember that scanning or attacking systems without permission is a crime in most countries, under laws such as the US Computer Fraud and Abuse Act, the UK Computer Misuse Act and India’s IT Act 2000.')}
{src('RFC 826 (ARP, 1982), RFC 4987 (TCP SYN flooding attacks and common mitigations, 2007), Bernstein, SYN cookies (1996), US-CERT alert TA14-017A (UDP based amplification attacks), RFC 2827 (BCP 38), Kaminsky (Black Hat 2008), RFC 5452, RFC 4033 to 4035 (DNSSEC), RFC 8484 (DNS over HTTPS), CVE-2023-44487, Nmap reference guide.')}
{safe('Every program on this page works on a list or dictionary inside the program. To practise on real packets, use your own virtual lab (for example two virtual machines on a host only network) or a legal training range, and only scan systems you own or have written permission to test.')}
{wwh('<b>A network attack</b> abuses how computers talk to each other: it listens to, changes, blocks or redirects traffic, or maps a network to find a way in.',
     'Most protocols were built without authentication, and every service reachable on a network is a possible way in. Knowing the attacks tells defenders where to put controls.',
     'Attackers forge packets (spoofing), flood resources (denial of service), probe for open services (scanning) and poison the tables that map names and addresses (ARP, DNS, BGP). Defenders answer with switch features, filtering, rate limits, encryption and monitoring.')}
{attack([
    ['Sniff traffic on a shared network', 'Encrypt everything with TLS, SSH or a VPN, use switched networks and 802.1X'],
    ['ARP spoofing to become a man in the middle', 'DHCP snooping with Dynamic ARP Inspection, arpwatch alerts, TLS'],
    ['SYN flood and other floods', 'SYN cookies, rate limits, upstream scrubbing, anycast and a CDN'],
    ['Reflection with spoofed UDP (DNS, NTP, memcached)', 'BCP 38 ingress filtering, close open resolvers and reflectors'],
    ['Port scan to map services', 'Close unused ports, firewall the rest, alert on scan patterns'],
    ['DNS cache poisoning', 'Random source ports and IDs, DNSSEC validation, DoH or DoT to a trusted resolver'],
    ['BGP hijack of address space', 'RPKI route origin validation, route filtering, monitoring']])}
''', kw=['network attacks', 'spoofing', 'man in the middle', 'denial of service', 'reconnaissance', 'Morris worm', 'Mitnick', 'Mirai', 'Dyn', 'Computer Misuse Act', 'CFAA', 'IT Act 2000'])

K.lesson('arp', 'Sniffing and ARP spoofing', f'''
{talk('On a local network, computers find each other by MAC address, the hardware address of the network card. When a laptop wants to send a packet to its gateway at 10.0.0.1, it broadcasts an ARP request asking who has that address, and the gateway replies with its MAC. The laptop stores the answer in its ARP cache. The protocol, described in RFC 826 in 1982, has no authentication, and most systems accept a reply they never asked for. So an attacker on the same network can send the laptop a forged reply saying the gateway is at the attacker’s MAC, and send the gateway a forged reply saying the laptop is at the attacker’s MAC. From then on, traffic in both directions passes through the attacker, who forwards it so that nothing seems broken. This is a man in the middle position. The attacker can read anything not encrypted, and can try to change it. On old hubs and open Wi-Fi an attacker could simply listen, which is called sniffing. Switches send each frame only to its destination port, but ARP spoofing defeats that. The defences are at the switch, with DHCP snooping and Dynamic ARP Inspection, on hosts, with tools such as arpwatch, and above all with encryption, because TLS turns a man in the middle into someone holding unreadable bytes.')}
{viz('cyarp')}
{run('arp_watch')}
{wwh('<b>ARP spoofing</b> (ARP poisoning): sending forged ARP replies so that a victim maps an IP address, usually the gateway’s, to the attacker’s MAC address.',
     'It turns the attacker into a man in the middle on a LAN, the starting point for stealing sessions, downgrading connections and injecting content.',
     'Hosts update their cache from any ARP reply. The attacker repeats forged replies every few seconds to both sides and forwards the traffic. Detection watches for an IP that changes MAC or a MAC that claims many IPs.')}
{table(['Defence', 'Where', 'How it helps', 'Limits'], [
    ['Dynamic ARP Inspection (DAI)', 'Managed switch', 'Drops ARP replies that do not match the DHCP snooping table', 'Needs managed switches and DHCP snooping'],
    ['Static ARP entries', 'Each host', 'The cache entry for the gateway cannot change', 'Hard to manage, protects only that host'],
    ['arpwatch or an IDS', 'Monitoring host', 'Alerts when an IP changes MAC', 'Detects, does not prevent'],
    ['802.1X port authentication', 'Switch port', 'Only authenticated devices join the LAN', 'Insiders can still attack'],
    ['TLS, SSH, VPN', 'Applications', 'A man in the middle sees only ciphertext and cannot forge certificates', 'Users must not click through certificate warnings']])}
{note('IPv6 replaces ARP with Neighbor Discovery, which has the same weakness. RA Guard and ND inspection on switches play the role of DAI.', 'tip')}
''', kw=['ARP', 'ARP spoofing', 'ARP poisoning', 'sniffing', 'man in the middle', 'MAC address', 'DHCP snooping', 'Dynamic ARP Inspection', 'arpwatch', '802.1X', 'Neighbor Discovery', 'RA Guard'])

K.lesson('dos', 'Denial of service: SYN floods and amplification', f'''
{talk('A denial of service attack tries to make a service unavailable, usually by exhausting some resource: bandwidth, memory, connection slots or CPU. When it comes from many machines at once, often a botnet of hacked devices, it is a distributed denial of service, or DDoS. The SYN flood is a classic. When a client sends SYN, the server reserves a slot in its backlog queue, replies SYN-ACK and waits for the final ACK. An attacker sends SYNs from forged addresses and never answers, so slots fill. If the backlog has 1024 slots and the server waits 30 seconds, 35 forged SYNs a second are enough to keep it full. In 1996 Daniel Bernstein proposed SYN cookies: when the queue is full, the server stores nothing and instead encodes the connection details and a secret keyed hash in the sequence number it sends back. A real client echoes that number plus one, and the server rebuilds the connection from it. Reflection attacks use a different trick. The attacker sends small UDP requests to public servers with the victim’s address as the source, and the servers send large replies to the victim. DNS can amplify about 50 times, NTP’s old monlist command about 557 times, and memcached up to 51000 times. In 2018 GitHub survived a 1.35 terabit per second memcached attack. The root fix is BCP 38: networks should drop outgoing packets whose source address is not their own, which stops spoofing at the edge.')}
{viz('cysynflood')}
{run('syn_cookies')}
{run('amplification')}
{fxs(fx('Half open connections', 'H = r &times; T (until H reaches the backlog B)', 'r = 50 forged SYNs per second, T = 30 s: H = 1500 &gt; B = 1024, so the queue is full. This is Little’s law L = &lambda;W.', key=True),
     fx('Amplification factor', 'k = response bytes / request bytes', 'A 60 byte DNS query that returns a 3000 byte answer: k = 50.', key=True),
     fx('Reflected bandwidth', 'victim load &asymp; bots &times; upload &times; k', '1000 bots at 1 Mbit/s through DNS (k = 54) gives about 54 Gbit/s.'),
     fx('SYN cookie layout', '32 bits = 5 bits (t mod 32) + 3 bits (MSS) + 24 bits (keyed hash)', 'The client returns ISN + 1, and the server checks the hash for this minute or the last one.'))}
{table(['Attack', 'Layer', 'Resource exhausted', 'Main defences'], [
    ['SYN flood', 'Transport (TCP)', 'Backlog slots', 'SYN cookies, larger backlog, shorter timeout'],
    ['UDP reflection and amplification', 'Network and transport', 'Victim’s bandwidth', 'BCP 38, close reflectors, upstream scrubbing'],
    ['Slowloris (2009)', 'Application (HTTP)', 'Web server connection slots', 'Timeouts, reverse proxies, connection limits'],
    ['HTTP/2 Rapid Reset (2023)', 'Application', 'Server CPU, 398 million requests per second seen by Google', 'Patches limiting stream resets, CDN'],
    ['Botnet floods (Mirai, 2016)', 'All', 'Everything', 'Anycast CDNs, scrubbing centres, securing IoT devices']])}
{note('Testing a DDoS defence means a planned exercise with your provider’s written agreement. Running a flood against anyone else, even as a test, is illegal and harms other users of the network.', 'warn')}
''', kw=['denial of service', 'DoS', 'DDoS', 'SYN flood', 'backlog', 'SYN cookies', 'Bernstein', 'reflection', 'amplification', 'memcached', 'NTP monlist', 'BCP 38', 'ingress filtering', 'Slowloris', 'HTTP/2 Rapid Reset', 'botnet', 'Little law'])

K.lesson('scan', 'Reconnaissance and port scanning', f'''
{talk('Before attacking, an intruder maps the target: which hosts are alive, which ports are open, and which software and versions are listening. The best known tool is Nmap, released by Gordon Lyon in 1997 and used daily by defenders to check their own networks. A port is open if a service listens on it, closed if the host answers with a reset, and filtered if a firewall drops the probe so nothing comes back. A connect scan uses the ordinary connect call and finishes the handshake, so services usually log it. A SYN scan, also called half open, sends only the SYN and resets as soon as a SYN-ACK arrives, which is faster and leaves fewer application logs, but needs raw packet rights. Further probes guess the service version and the operating system from tiny differences in replies. Defenders run the same scans against themselves to find forgotten services, and they detect hostile scans by noticing one source touching many ports or hosts in a short time. Services such as Shodan and Censys scan the whole IPv4 internet continuously, so anything exposed is found within hours.')}
{viz('cyscan')}
{run('scan_model')}
{wwh('<b>Port scanning</b> sends probes to many ports to learn which are open, closed or filtered, and often which software runs on them.',
     'It is step one of almost every intrusion and of every defensive audit. You cannot protect a service you did not know was exposed.',
     'Send SYN: SYN-ACK means open, RST means closed, silence or an ICMP unreachable message means filtered. Version detection sends protocol specific probes and matches the answers against a database.')}
{table(['Scan', 'What is sent', 'Pros', 'Cons'], [
    ['Connect scan', 'Full TCP handshake', 'No special rights needed', 'Logged by the services'],
    ['SYN (half open) scan', 'SYN, then RST after SYN-ACK', 'Fast, fewer application logs', 'Needs raw packets, still seen by an IDS'],
    ['UDP scan', 'Empty or protocol specific UDP datagrams', 'Finds DNS, SNMP, NTP', 'Slow, many ports look open or filtered'],
    ['Ping sweep', 'ICMP echo or TCP probes to many hosts', 'Finds live hosts quickly', 'Often blocked'],
    ['Version and OS detection', 'Protocol probes, TCP/IP quirks', 'Names the software and version', 'Noisy, more likely to be noticed']])}
{note('Scan your own lab or a host you have written permission to test. Scanning other people’s systems can break the law and your provider’s terms, even if you do nothing else.', 'warn')}
''', kw=['reconnaissance', 'port scanning', 'Nmap', 'open closed filtered', 'SYN scan', 'half open scan', 'connect scan', 'UDP scan', 'ping sweep', 'version detection', 'OS fingerprinting', 'Shodan', 'Censys'])

K.lesson('dns', 'Poisoning names and routes: DNS and BGP', f'''
{talk('DNS turns names into addresses, and a resolver caches each answer for its time to live. If an attacker can get a false answer into the cache, every user of that resolver is sent to the attacker’s server. Early resolvers accepted any reply whose 16 bit query ID matched, so an attacker who raced the real server with many forged replies had a fair chance. In 2008 Dan Kaminsky showed how to make the race repeatable: ask the resolver for random names under the target domain, such as a1.bank.example, a2.bank.example and so on, each causing a fresh query and a fresh race, and in the forged replies include extra data that claims the whole domain. The industry shipped a coordinated fix within weeks: randomise the source port as well as the query ID, which adds about 16 bits of guessing. The full fix is DNSSEC, which signs DNS records so a resolver can check them. The root zone was signed in 2010. DNS over TLS and DNS over HTTPS encrypt the path from the user to the resolver. Routing has a similar weakness. BGP, which joins the networks of the internet, believes the routes it is told. In 2008 Pakistan Telecom accidentally took YouTube offline worldwide by announcing a more specific route, and in 2018 attackers hijacked Amazon DNS address space to steal cryptocurrency. RPKI lets networks sign which addresses they may announce.')}
{run('dns_race')}
{fxs(fx('Chance per race', 'p = 1 &minus; (1 &minus; 1/N)<sup>n</sup> &asymp; n/N for n &#8810; N', 'n = 100 forged replies, N = 2<sup>16</sup>: p &asymp; 0.0015, so about 655 races on average.', key=True),
     fx('With source port randomisation', 'N &asymp; 2<sup>16</sup> &times; 2<sup>16</sup> = 2<sup>32</sup>', 'Expected races &asymp; 2<sup>32</sup>/100 &asymp; 43 million, which turns minutes into months.', key=True),
     fx('DNSSEC', 'RRSIG = Sign(zone key, record set), chained up to the root key', 'A forged answer fails signature checks, however many races the attacker runs.'))}
{table(['Protection', 'What it protects', 'Standard'], [
    ['Random source port and ID', 'Makes off path forgery a 32 bit guess', 'RFC 5452 (2009)'],
    ['DNSSEC validation', 'Integrity and origin of records', 'RFC 4033 to 4035, root signed 2010'],
    ['DNS over TLS / HTTPS', 'Privacy and integrity from user to resolver', 'RFC 7858 (2016), RFC 8484 (2018)'],
    ['RPKI route origin validation', 'Which network may announce which prefix', 'RFC 6480, RFC 6811'],
    ['TLS certificates', 'Even if DNS lies, the fake server cannot prove it is the bank', 'RFC 8446 with the Web PKI']])}
''', kw=['DNS cache poisoning', 'Kaminsky', 'query ID', 'source port randomisation', 'DNSSEC', 'DNS over HTTPS', 'DNS over TLS', 'BGP hijack', 'RPKI', 'Pakistan Telecom YouTube', 'Route 53 hijack'])

K.lesson('versus', 'Network attacks compared', f'''
{talk('It helps to compare these attacks by what the attacker needs and what they break. ARP spoofing needs a foothold on the same local network but gives full man in the middle power there. DNS poisoning and BGP hijacks work from far away and redirect many users at once. Floods need a lot of traffic, which is why botnets and amplification exist, and they break availability without stealing anything. Scanning breaks nothing by itself but tells the attacker where to aim. A useful habit for exams is to name the protocol weakness behind each attack, usually missing authentication or a resource that is reserved before the other side proves anything, and then the matching defence.')}
{versus('Network attacks side by side', ['', 'ARP spoofing', 'SYN flood', 'Amplification DDoS', 'Port scan', 'DNS poisoning'], [
    ['Attacker needs', 'Same LAN', 'Many packets, spoofed sources', 'Botnet plus open reflectors', 'Reachability', 'Ability to race a resolver'],
    ['Breaks', 'Confidentiality, integrity', 'Availability', 'Availability', 'Nothing directly, finds targets', 'Integrity, redirects users'],
    ['Weakness used', 'ARP has no authentication', 'State kept before the client proves itself', 'UDP has no handshake, sources can be forged', 'Services answer anyone', 'Answers not authenticated'],
    ['Key defence', 'DAI, TLS', 'SYN cookies', 'BCP 38, scrubbing', 'Close and filter ports, IDS', 'Port randomisation, DNSSEC'],
    ['Famous case', 'Wi-Fi café attacks', 'Panix 1996', 'GitHub 2018, 1.35 Tbps', 'Shodan finds exposed devices', 'Kaminsky 2008']],
    'Encrypt and authenticate traffic, keep no state for unproven clients, filter spoofed sources, expose only what you must, and watch for patterns.')}
''', kw=['comparison', 'ARP spoofing', 'SYN flood', 'amplification', 'port scan', 'DNS poisoning'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Network security spans everyday habits and deep protocol research. A beginner learns that public Wi-Fi can be watched, that HTTPS matters, and that floods can knock sites offline. A college student can explain the TCP handshake and why a SYN flood works, read a packet capture in Wireshark, run Nmap against a lab machine and describe ARP and DNS poisoning with their defences. A masters student models attacks with queueing theory, studies SYN cookie and TCP option trade offs, measures amplification across protocols, designs DDoS mitigation with anycast and scrubbing, and configures DNSSEC and RPKI. Researchers find new amplification vectors and protocol flaws, such as HTTP/2 Rapid Reset in 2023, measure the whole internet with tools like ZMap that can scan all of IPv4 in under an hour, and study off path attacks that infer TCP sequence numbers through side channels.')}
{ladder(
    '<p>Public networks can be watched, so use HTTPS and a VPN. Floods can knock services offline. Attackers scan the internet constantly looking for open doors.</p>',
    '<p>The TCP handshake and SYN floods, ARP and DNS poisoning, amplification factors, Nmap port states, BCP 38, SYN cookies and Dynamic ARP Inspection.</p>',
    '<p>Queueing models of floods (Little’s law), SYN cookie encoding, DDoS architecture with anycast and scrubbing, DNSSEC chains of trust, RPKI, and reading pcap files with Wireshark and Zeek.</p>',
    '<p>New amplification vectors, internet wide measurement (ZMap, 2013), off path TCP attacks through side channels, BGP security beyond origin validation (BGPsec, ASPA), and formal analysis of protocols.</p>')}
{grow('Explain each attack in one sentence and its main defence.',
      'Run the toy programs, do the flood and DNS maths, and read a scan result.',
      'Design defences in layers and estimate attack costs with models.')}
''', kw=['beginner', 'expert', 'Wireshark', 'Zeek', 'ZMap', 'BGPsec', 'ASPA', 'off path attacks'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Why</b>: ARP, DNS, TCP and BGP trust what they hear. Attacks spoof, flood, scan and poison.',
    '<b>ARP spoofing</b>: forged replies make the attacker a man in the middle. Defend with DHCP snooping plus DAI, arpwatch and TLS.',
    '<b>SYN flood</b>: half open H = r &times; T fills backlog B. SYN cookies keep no state: 5 bits time, 3 bits MSS, 24 bits keyed hash.',
    '<b>Amplification</b>: k = response / request. DNS about 54, NTP monlist 557, memcached up to 51000. BCP 38 stops spoofed sources.',
    '<b>Scanning</b>: SYN-ACK open, RST closed, silence filtered. SYN scan is half open, connect scan completes. Scan only with permission.',
    '<b>DNS poisoning</b>: p &asymp; n/N per race. Kaminsky made races repeatable. Fix: random ports (2<sup>32</sup>), DNSSEC, DoT and DoH.',
    '<b>BGP</b>: hijacks redirect address space (YouTube 2008, Route 53 2018). RPKI signs route origins.',
    '<b>Layers</b>: encrypt, authenticate, keep no state for unproven clients, filter, monitor.'],
    'Next, Network and Systems 1.2: firewalls, intrusion detection and VPNs, the tools that put these defences in place.')}
{files('Three tasks: half open connections in a SYN flood, an ARP change detector, and a sliding window port scan detector.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which property does a denial of service attack break?', ['Confidentiality', 'Integrity', 'Availability', 'Non repudiation'], 2, 'CIA.', 'It stops real users from reaching the service.')
K.quiz('e', 'Why can ARP spoofing work at all?', ['ARP is encrypted', 'ARP replies are not authenticated, and hosts accept replies they never asked for', 'Switches forward everything', 'MAC addresses are secret'], 1, 'Trust.', 'RFC 826 has no way to prove who sent a reply.')
K.quiz('e', 'In a port scan, a reply of RST to a SYN means the port is', ['Open', 'Closed', 'Filtered', 'Encrypted'], 1, 'Reset.', 'The host is up but nothing listens there.')
K.quiz('e', 'Which simple step protects against a man in the middle on public Wi-Fi?', ['Turning off the screen', 'Using HTTPS or a VPN and never clicking through certificate warnings', 'Using a long Wi-Fi name', 'Clearing the browser history'], 1, 'Encryption.', 'The attacker then sees only ciphertext and cannot fake the server’s certificate.')
K.quiz('m', 'How do SYN cookies stop a SYN flood from filling the queue?', ['They block all SYNs', 'The server keeps no state and hides it, with a keyed hash, in the sequence number it sends', 'They make the timeout longer', 'They encrypt the SYN'], 1, 'Stateless.', 'Only a client that really received the SYN-ACK can return the right number.')
K.quiz('m', 'What makes UDP services useful for reflection attacks?', ['They are fast', 'No handshake, so a request with a forged source gets its reply sent to the victim', 'They use port 80', 'They are encrypted'], 1, 'No handshake.', 'TCP would need the victim to complete the handshake first.')
K.quiz('m', 'What does BCP 38 ask networks to do?', ['Block port 53', 'Drop outgoing packets whose source address is not from their own range', 'Use IPv6 only', 'Sign BGP routes'], 1, 'Ingress filtering.', 'It stops spoofed packets at the edge, which removes reflection and many floods.')
K.quiz('m', 'What did Kaminsky’s 2008 attack add to DNS cache poisoning?', ['A faster computer', 'Queries for random subdomains so the attacker can race again immediately, with forged data for the whole domain', 'Breaking DNSSEC', 'Guessing passwords'], 1, 'Repeatable races.', 'TTL caching no longer slowed the attacker down.')
K.quiz('m', 'Dynamic ARP Inspection checks ARP replies against', ['The DNS cache', 'The DHCP snooping binding table', 'The routing table', 'Certificates'], 1, 'Bindings.', 'The switch learned which MAC got which IP when DHCP handed it out.')
K.quiz('h', 'Why is a SYN scan called half open?', ['It scans half the ports', 'It sends RST after the SYN-ACK, so the handshake never completes', 'It uses half a packet', 'It only scans UDP'], 1, 'Handshake.', 'The connection never reaches the application, so fewer logs are written.')
K.quiz('h', 'Which DNS change added about 16 bits to what an off path attacker must guess?', ['Longer TTLs', 'Randomising the UDP source port of each query', 'Using TCP only', 'Shorter names'], 1, 'Port.', 'Guessing ID and port together is about 2<sup>32</sup> instead of 2<sup>16</sup>.')
K.quiz('h', 'What does RPKI route origin validation check?', ['Website certificates', 'Whether the network announcing a prefix is authorised to originate it', 'Packet checksums', 'DNS names'], 1, 'Origins.', 'Signed ROAs say which AS may announce which prefix. Path checks need BGPsec or ASPA.')
K.quiz('h', 'An IDS flags 99% of scans with 1% false alarms, but only 0.1% of sources scan. Most alerts are', ['Real scans', 'False alarms', 'Half and half', 'Impossible to say'], 1, 'Base rate.', 'P(scan | alert) = 0.00099 / (0.00099 + 0.00999) &asymp; 9%. This is why alert tuning matters.')
K.quiz('x', 'In the style of a Stanford CS 155 question: why does a SYN cookie reduce the TCP options a connection can use?', ['It does not', 'Only 32 bits fit in the sequence number, so options such as window scaling and SACK must be dropped or squeezed into timestamp bits', 'Cookies disable TCP', 'Options are illegal'], 1, 'Bit budget.', 'Linux stores some option bits in the TCP timestamp when timestamps are on.')
K.quiz('x', 'In the style of an IIT Kanpur networks exam: a server keeps half open entries for W seconds and forged SYNs arrive at rate &lambda;. By Little’s law, how many entries are occupied on average?', ['&lambda; / W', '&lambda; W', 'W / &lambda;', '&lambda; + W'], 1, 'L = &lambda;W.', 'This is the H = r &times; T formula of the chapter. The backlog must exceed it, or cookies must take over.')

K.calc('e', 'Forged SYNs arrive at 50 per second and each half open connection waits 30 seconds. How many half open connections build up?', '1500', 'r &times; T.', ['50 &times; 30.', 'More than a 1024 slot backlog.', eq('H = 1500')], check=50 * 30)
K.calc('e', 'A 60 byte request returns a 3000 byte response. What is the amplification factor?', '50', 'Response over request.', ['3000 / 60.', 'Each byte sent becomes 50 at the victim.', eq('k = 50')], check=3000 // 60)
K.calc('e', 'How many TCP port numbers exist (0 to 65535)?', '65536', '16 bit field.', ['Port numbers are 16 bits.', '2<sup>16</sup> = 65536.', eq('65536')], check=2 ** 16)
K.calc('m', 'A scanner sends 1000 probes per second. About how many seconds does it take to probe ports 1 to 65535 once? Round to a whole number.', '66', '65535 / 1000.', ['65535 / 1000 = 65.5.', 'Round.', eq('about 66 s')], check=round(65535 / 1000))
K.calc('m', '2000 bots each send 2 Mbit/s of spoofed requests through a reflector with k = 50. How many Gbit/s reach the victim?', '200', 'bots &times; upload &times; k.', ['2000 &times; 2 = 4000 Mbit/s.', '&times; 50 = 200000 Mbit/s = 200 Gbit/s.', eq('200 Gbit/s')], check=2000 * 2 * 50 // 1000)
K.calc('m', 'How many bits does a SYN cookie carry in total (5 bits time, 3 bits MSS, 24 bits hash)?', '32', 'Add.', ['5 + 3 + 24.', 'Exactly the size of a TCP sequence number.', eq('32 bits')], check=5 + 3 + 24)
K.calc('m', 'With a 16 bit query ID and 100 forged replies per race, about how many races does an attacker need on average? Round to a whole number.', '655', '2<sup>16</sup> / 100.', ['p &asymp; 100 / 65536 per race.', 'Expected races &asymp; 65536 / 100.', eq('about 655')], check=round(2 ** 16 / 100))
K.calc('m', 'A server waits 20 seconds per half open connection and must survive 40 forged SYNs per second. What backlog size is needed at least?', '800', 'r &times; T.', ['40 &times; 20.', 'Any smaller queue fills.', eq('B &ge; 800')], check=40 * 20)
K.calc('h', 'A backlog of 4096 and a 60 second timeout. What is the smallest whole number of forged SYNs per second that fills it?', '69', 'B / T, rounded up.', ['4096 / 60 = 68.3.', 'Round up.', eq('69 SYN/s')], check=-(-4096 // 60))
K.calc('h', 'The SYN cookie time field is t mod 32 with t in minutes. After how many minutes does it repeat?', '32', '5 bits.', ['2<sup>5</sup> = 32 values.', 'The server only accepts the current and previous minute anyway.', eq('32 minutes')], check=2 ** 5)
K.calc('h', 'An IDS detects 99% of scanning sources with a 1% false alarm rate, and 0.1% of sources scan. What percent of alerts are real scans? Round to a whole number.', '9', 'Bayes.', ['True alerts: 0.99 &times; 0.001 = 0.00099.', 'False alerts: 0.01 &times; 0.999 = 0.00999.', eq('0.00099 / 0.01098 &asymp; 9%')], check=round(100 * 0.99 * 0.001 / (0.99 * 0.001 + 0.01 * 0.999)))
K.calc('x', 'With ID and source port randomised (about 2<sup>32</sup> combinations) and 100 forged replies per race, about how many million races are expected? Round to a whole number.', '43', '2<sup>32</sup> / 100.', ['2<sup>32</sup> = 4294967296.', '/ 100 &asymp; 42.9 million.', eq('about 43 million')], check=round(2 ** 32 / 100 / 1e6))
K.calc('x', 'A botnet of 100000 cameras each uploads 10 Mbit/s. How many Gbit/s can it send without any amplification?', '1000', 'Multiply, then divide by 1000.', ['100000 &times; 10 = 1000000 Mbit/s.', '= 1000 Gbit/s = 1 Tbit/s.', eq('1000 Gbit/s')], check=100000 * 10 // 1000)
K.calc('x', 'Little’s law for legitimate traffic: 200 new connections per second, each half open for one round trip of 0.1 s. How many half open entries on average?', '20', 'L = &lambda;W.', ['200 &times; 0.1.', 'Tiny next to a flood.', eq('L = 20')], check=round(200 * 0.1))

K.assign('half_open', 'e', 'Half open connections in a SYN flood',
         '<p>Write <code>half_open(rate, timeout, backlog)</code> that returns how many half open connections a server holds in the steady state: rate &times; timeout, but never more than the backlog.</p>',
         '''
def half_open(rate, timeout, backlog):
    # your code here
    pass
''', [('half_open(50, 30, 1024)', 1024), ('half_open(30, 30, 1024)', 900), ('half_open(0, 30, 1024)', 0)],
         '''
def half_open(rate, timeout, backlog):
    return min(rate * timeout, backlog)
''', 'Multiply, then use min with the backlog.', '<p>When the result equals the backlog, new SYNs are dropped unless SYN cookies are on.</p>')
K.assign('arp_changes', 'm', 'Detect ARP spoofing',
         '<p>Write <code>arp_changes(replies)</code>. <code>replies</code> is a list of [ip, mac] pairs in the order they arrived. Keep a cache, and return the list of IP addresses whose MAC changed, each IP once, in the order the first change happened.</p>',
         '''
def arp_changes(replies):
    # your code here
    pass
''', [('arp_changes([["10.0.0.1", "aa"], ["10.0.0.5", "bb"], ["10.0.0.1", "cc"], ["10.0.0.5", "cc"], ["10.0.0.1", "dd"]])', ['10.0.0.1', '10.0.0.5']), ('arp_changes([["10.0.0.1", "aa"], ["10.0.0.1", "aa"]])', []), ('arp_changes([])', [])],
         '''
def arp_changes(replies):
    cache, changed = {}, []
    for ip, mac in replies:
        if ip in cache and cache[ip] != mac and ip not in changed:
            changed.append(ip)
        cache[ip] = mac
    return changed
''', 'Use a dict for the cache and a list for the answer. Check before you overwrite.', '<p>A repeated identical reply is normal. Only a change of MAC for the same IP is suspicious, and a real network card swap also triggers it, so alerts need a human look.</p>')
K.assign('scan_alert', 'h', 'A sliding window port scan detector',
         '<p>Write <code>scan_alert(log, window, limit)</code>. <code>log</code> is a list of [source, port, time] entries sorted by time. Return a sorted list of the sources that touch more than <code>limit</code> distinct ports within any period of <code>window</code> seconds (times t with start &le; t &lt; start + window, where start is the time of one of that source’s entries).</p>',
         '''
def scan_alert(log, window, limit):
    # your code here
    pass
''', [('scan_alert([["a", p, p] for p in range(20)], 10, 5)', ['a']), ('scan_alert([["a", p, 100 * p] for p in range(20)], 10, 5)', []), ('scan_alert([["b", 80, 1], ["b", 80, 2], ["c", 22, 1], ["c", 23, 2], ["c", 25, 3]], 60, 2)', ['c'])],
         '''
def scan_alert(log, window, limit):
    by_source = {}
    for src, port, t in log:
        by_source.setdefault(src, []).append((t, port))
    found = []
    for src, events in by_source.items():
        for start, port in events:
            ports = {p for t, p in events if start <= t < start + window}
            if len(ports) > limit:
                found.append(src)
                break
    return sorted(found)
''', 'Group entries by source. For each entry of a source, count distinct ports with times from that entry’s time up to time plus window.', '<p>Slow scans spread probes over hours to slip under such windows, which is why detectors also keep longer term counts per source.</p>')

K.must('Families', 'Sniff and MITM (C, I), DoS (A), scan (recon), spoof and poison (ARP, DNS, BGP). Protocols trust what they hear. Scan only with permission.')
K.must('ARP spoofing', 'Forged replies: gateway at attacker’s MAC. Defences: DHCP snooping + DAI, static entries, arpwatch, 802.1X, TLS. IPv6: RA Guard.')
K.must('SYN flood', 'H = r &times; T fills backlog B. SYN cookies: 5 bit t mod 32, 3 bit MSS, 24 bit keyed hash, ACK = ISN + 1. Bernstein 1996.')
K.must('Amplification', 'k = response / request: DNS 28 to 54, NTP 556.9, memcached 10000 to 51000. GitHub 1.35 Tbps 2018. BCP 38 (RFC 2827).')
K.must('Scanning', 'SYN-ACK open, RST closed, silence filtered. SYN scan half open needs raw packets, connect scan logged. Detect many ports per source per window.')
K.must('DNS and BGP', 'p &asymp; n/N. Kaminsky 2008: random subdomains. Fix: random ports (2<sup>32</sup>), DNSSEC, DoT/DoH. BGP hijacks: RPKI ROAs.')

T = K.topic(
    slug='cy-netattacks', topic='cy-netattacks', step=(1, 'Defending the network', 'cy-s1', 'Network attacks and how to stop them, firewalls, intrusion detection and VPNs, and the security of wireless networks.', 'Intermediate'),
    title='Network attacks and defences: spoofing, floods, scans and poisoning', short='Network attacks', badge='1.1', minutes=80,
    lead='How attackers abuse protocols that trust what they hear, and how defenders stop them: ARP spoofing and the man in the middle, SYN floods and SYN cookies, reflection and amplification with real factors, port scanning and its detection, DNS cache poisoning after Kaminsky, BGP hijacks and RPKI, all run on toy data with the maths worked out.',
    desc='network attacks, network security, sniffing, man in the middle, ARP spoofing, ARP poisoning, Dynamic ARP Inspection, DHCP snooping, arpwatch, 802.1X, denial of service, DDoS, SYN flood, SYN cookies, backlog, Little law, reflection, amplification, DNS amplification, NTP monlist, memcached, BCP 38, ingress filtering, Slowloris, HTTP/2 Rapid Reset, botnet, Mirai, port scanning, Nmap, SYN scan, connect scan, UDP scan, open closed filtered, reconnaissance, Shodan, DNS cache poisoning, Kaminsky, source port randomisation, DNSSEC, DNS over HTTPS, BGP hijack, RPKI',
    summary='ARP spoofing, SYN floods and cookies, amplification DDoS, port scanning, DNS poisoning and BGP hijacks with their defences.',
    keywords=['network attacks', 'ARP spoofing', 'SYN flood', 'SYN cookies', 'DDoS', 'amplification', 'port scan', 'Nmap', 'DNS poisoning', 'BGP'],
    recap='<p>Most network attacks exploit protocols that believe whatever they hear. Encrypt, authenticate, keep no state for strangers, filter forged sources and watch for patterns.</p>',
    added='2026-11-15')
