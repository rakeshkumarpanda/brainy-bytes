# Foundations 2.2: networks for security. Checked against RFC 791 (IPv4 and its header checksum), RFC 1918 (private
# addresses), RFC 4632 (CIDR), RFC 3021 (/31 links), RFC 8200 (IPv6), RFC 9293 (TCP, 2022), RFC 6528 (random initial
# sequence numbers), RFC 826 (ARP), RFC 2131 (DHCP), RFC 1034 and 1035 (DNS), RFC 9110 (HTTP semantics), the IANA
# service name and port number registry, and Kurose and Ross, Computer Networking: A Top-Down Approach (8th edition).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-networks')
K = Kit()

K.code('subnet_calc', r'''
import ipaddress

# Work out a subnet by hand with bit operations, then check with Python's ipaddress module
def to_number(ip):
    parts = ip.split(".")
    n = 0
    for p in parts:
        n = n * 256 + int(p)
    return n

def to_ip(n):
    return ".".join(str((n >> shift) & 255) for shift in [24, 16, 8, 0])

address = "192.168.10.77"
prefix = 26

ip = to_number(address)
host_bits = 32 - prefix
mask = (0xFFFFFFFF << host_bits) & 0xFFFFFFFF      # prefix ones, then zeros
network = ip & mask
broadcast = network | (~mask & 0xFFFFFFFF)
hosts = 2 ** host_bits - 2

print("mask:     ", to_ip(mask))
print("network:  ", to_ip(network))
print("broadcast:", to_ip(broadcast))
print("hosts:    ", hosts, "from", to_ip(network + 1), "to", to_ip(broadcast - 1))

check = ipaddress.ip_network(address + "/" + str(prefix), strict=False)
print("ipaddress agrees:", check.network_address, check.broadcast_address, check.num_addresses - 2)
''')

K.code('private_or_public', r'''
import ipaddress

# Private ranges (RFC 1918) never travel on the public internet. Loopback is the machine itself.
for text in ["10.4.2.1", "172.20.0.9", "192.168.1.1", "8.8.8.8", "127.0.0.1", "172.32.0.1"]:
    ip = ipaddress.ip_address(text)
    if ip.is_loopback:
        kind = "loopback (this computer)"
    elif ip.is_private:
        kind = "private (inside a home or company network)"
    else:
        kind = "public"
    print(text, "->", kind)

# Is an address inside a firewall rule's network?
rule = ipaddress.ip_network("10.0.0.0/8")
print("10.200.3.4 in 10.0.0.0/8?", ipaddress.ip_address("10.200.3.4") in rule)
''')

K.code('ip_header', r'''
# Read a real IPv4 header from its 20 bytes (written in hex) and check its checksum
header_hex = "45000073000040004011b861c0a80001c0a800c7"
data = bytes.fromhex(header_hex)

version = data[0] >> 4                 # top 4 bits
header_words = data[0] & 0x0F          # bottom 4 bits: length in 32 bit words
total_length = data[2] * 256 + data[3]
ttl = data[8]
protocol = data[9]
names = {1: "ICMP", 6: "TCP", 17: "UDP"}
source = ".".join(str(b) for b in data[12:16])
destination = ".".join(str(b) for b in data[16:20])

print("version", version, "| header", header_words * 4, "bytes | total", total_length, "bytes")
print("time to live", ttl, "| protocol", protocol, names.get(protocol, "?"))
print("from", source, "to", destination)

# The checksum: add the header as 16 bit numbers, fold the carries back in.
# A correct header (checksum field included) adds up to 0xFFFF.
total = 0
for i in range(0, 20, 2):
    total = total + data[i] * 256 + data[i + 1]
while total > 0xFFFF:
    total = (total & 0xFFFF) + (total >> 16)
print("sum with carries folded:", hex(total), "->", "header is intact" if total == 0xFFFF else "header is damaged")
''')

K.code('ports', r'''
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
''')

K.code('handshake', r'''
# Sequence and acknowledgement numbers in a TCP connection
client_isn = 1000      # initial sequence numbers, random in real systems
server_isn = 5000
data_len = 120

print("1. client -> server  SYN      seq =", client_isn)
print("2. server -> client  SYN-ACK  seq =", server_isn, " ack =", client_isn + 1)
print("3. client -> server  ACK      seq =", client_isn + 1, " ack =", server_isn + 1)
print("4. client -> server  data     seq =", client_isn + 1, " length =", data_len)
print("5. server -> client  ACK      ack =", client_isn + 1 + data_len)

# A SYN flood: many SYNs, no final ACK. Each half open connection waits in a queue.
queue_size = 128
syn_per_second = 500
print("queue full after", round(queue_size / syn_per_second, 3), "seconds without SYN cookies")
''')

K.code('dns_lookup_model', r'''
# A model of how a resolver finds www.example.com, asking from the top of the tree down
root = {"com": "TLD server for .com"}
tld = {"example.com": "authoritative server for example.com"}
authoritative = {"www.example.com": ("A", "93.184.215.14"), "example.com": ("MX", "mail.example.com")}
cache = {}

def resolve(name):
    if name in cache:
        print("  answer from cache")
        return cache[name]
    label = name.split(".")[-1]
    print("  ask a root server -> go to the", root[label])
    zone = ".".join(name.split(".")[-2:])
    print("  ask the .com server -> go to the", tld[zone])
    answer = authoritative[name]
    print("  ask the authoritative server ->", answer)
    cache[name] = answer
    return answer

print("first lookup:")
resolve("www.example.com")
print("second lookup:")
resolve("www.example.com")
''')

K.lesson('idea', 'How computers talk: packets and layers', f'''
{talk('In the 1960s the US Department of Defense funded a network called ARPANET. Its designers had a bold idea called packet switching. Instead of holding a phone line open for a whole call, a message is chopped into small pieces called packets, each with an address, and every piece finds its own way through the network. If one path breaks, packets take another. In 1974 Vint Cerf and Bob Kahn described TCP and IP, and on the first of January 1983 ARPANET switched over to them. That day is often called the birthday of the internet. The protocols were designed for a small group of trusted researchers, so they had almost no security built in. Addresses could be faked, and anyone on the path could read the traffic. Almost every network attack you will study comes from that early trust, and almost every network defence was added later on top.')}
{src('RFC 791, RFC 9293, RFC 1918, RFC 4632, RFC 1034 and 1035, RFC 9110, the IANA port registry and Kurose and Ross, Computer Networking.')}
{wwh('A <b>network</b> lets computers send data to each other in small pieces called <b>packets</b>. The work is split into <b>layers</b>: each layer does one job and uses the layer below it.',
     'An attacker who understands the layers knows where to listen, fake or flood. A defender who understands them knows where to filter, encrypt and watch. Every firewall rule and every packet capture is written in the language of layers.',
     'Going down the layers, each one wraps the data in its own <b>header</b> (encapsulation): the application data, then a TCP or UDP header with ports, then an IP header with addresses, then an Ethernet or Wi-Fi header for one link. The receiver removes them in reverse.')}
<p>Press <b>Step</b> to wrap one web request layer by layer and unwrap it at the server.</p>
{viz('cyencap')}
{table(['TCP/IP layer', 'OSI layers', 'Job', 'Address it uses', 'Examples', 'Typical attacks'], [
    ['Application', '7 Application, 6 Presentation, 5 Session', 'What the program says', 'Names, URLs', 'HTTP, DNS, SMTP, SSH, TLS', 'Phishing sites, SQL injection, DNS spoofing'],
    ['Transport', '4 Transport', 'Which program, in order, reliably', 'Ports', 'TCP, UDP', 'Port scans, SYN floods, session hijacking'],
    ['Internet', '3 Network', 'Across networks, hop by hop', 'IP addresses', 'IPv4, IPv6, ICMP', 'IP spoofing, ping floods, route hijacking'],
    ['Link', '2 Data link, 1 Physical', 'Across one cable or radio link', 'MAC addresses', 'Ethernet, Wi-Fi, ARP', 'ARP spoofing, MAC flooding, rogue Wi-Fi']])}
{note('A memory aid for the 7 OSI layers from 1 to 7: "Please Do Not Throw Sausage Pizza Away" (Physical, Data link, Network, Transport, Session, Presentation, Application).', 'tip')}
''', kw=['network', 'packet', 'packet switching', 'layers', 'OSI model', 'TCP/IP model', 'encapsulation', 'header', 'ARPANET'])

K.lesson('address', 'Addresses: MAC, IPv4, IPv6, private ranges and NAT', f'''
{talk('Every device on a network needs an address, just like every house needs one for the post. Networks actually use two kinds. The MAC address is burned into the network card by the maker. It is like a person’s name, and it is only used on the local network. The IP address is like a postal address: it tells routers across the whole internet where to deliver. The first internet addresses, IPv4, have 32 bits, which allows about 4.3 billion addresses. That sounded like plenty in 1981 but ran out as phones and laptops spread. Two fixes followed. One was private addresses with NAT, which lets a whole home share one public address. The other was IPv6, with 128 bits, enough to give every grain of sand on Earth many addresses. Security people must know these ranges by heart, because firewall rules and logs are full of them.')}
{table(['Address', 'Size', 'Looks like', 'Used for'], [
    ['MAC', '48 bits', '3C:22:FB:1A:09:7E', 'One device on one local link. Can be changed in software'],
    ['IPv4', '32 bits', '192.168.1.20', 'Routing across networks. About 4.3 billion addresses'],
    ['IPv6', '128 bits', '2001:db8::1', 'The newer internet address, 2<sup>128</sup> addresses'],
    ['Port', '16 bits', '443', 'Which program on the device: 0 to 65535']])}
{table(['Special IPv4 range', 'Meaning'], [
    ['10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16', 'Private (RFC 1918). Used inside homes and companies, never routed on the internet'],
    ['127.0.0.0/8', 'Loopback: the computer itself (127.0.0.1 is "localhost")'],
    ['169.254.0.0/16', 'Link local: a device gave itself an address because DHCP failed'],
    ['0.0.0.0', 'Any address on this machine (for a server listening everywhere)'],
    ['255.255.255.255', 'Broadcast to everyone on the local network'],
    ['192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24', 'Reserved for documentation and examples, like this page']])}
{run('private_or_public')}
{scene('your home router and NAT', '<p>Your phone, laptop and TV all have private addresses like 192.168.1.x. Your router has one public address from your internet provider. When your laptop opens a website, the router swaps the private address for its public one and remembers the swap in a table, so the reply finds its way back. This is <b>network address translation</b> (NAT). As a side effect, a computer on the internet cannot start a connection to your laptop, because the router has no table entry for it. NAT is not a firewall, but it blocks a lot of unwanted traffic by accident.</p>')}
{note('172.32.0.1 is public, not private. The private block is 172.16.0.0/12, which ends at 172.31.255.255. This is a favourite trick question.', 'exam')}
''', kw=['MAC address', 'IP address', 'IPv4', 'IPv6', 'private addresses', 'RFC 1918', 'loopback', 'localhost', 'NAT', 'link local', 'port'])

K.lesson('subnet', 'Subnet maths with CIDR', f'''
{talk('Big networks are cut into smaller pieces called subnets, the same way a city is cut into neighbourhoods. Subnets keep traffic local, make addresses easier to manage, and, most importantly for security, let us put walls between parts of a company: the guest Wi-Fi in one subnet, the servers in another, the payment machines in a third. Since 1993, networks have been written with CIDR notation, a slash and a number, like slash twenty four. The number tells how many of the 32 address bits are the network part. Everything else is a little binary maths with AND and OR, exactly the bit operations from the maths chapter. Network engineers and penetration testers do this maths in their heads, and it is asked in every networking and security exam.')}
{wwh('<b>CIDR</b> notation a.b.c.d/n says the first n bits of the address are the <b>network</b> part and the remaining 32 &minus; n bits are the <b>host</b> part. The <b>subnet mask</b> is n ones followed by zeros.',
     'Firewall rules, routing tables, cloud security groups and access lists are all written as networks like 10.0.0.0/16. To read or write them, you must know which addresses a prefix covers.',
     'Network address = address AND mask (host bits set to 0). Broadcast = network with all host bits set to 1. Usable hosts = 2<sup>32 &minus; n</sup> &minus; 2.')}
{viz('cysubnet')}
{run('subnet_calc')}
{fxs(fx('Hosts in a subnet', 'hosts = 2<sup>32 &minus; n</sup> &minus; 2', 'Minus 2 for the network and broadcast addresses. /24 gives 254, /26 gives 62, /30 gives 2.', key=True),
     fx('Network and broadcast', 'network = IP AND mask &nbsp;&nbsp; broadcast = network OR (NOT mask)', 'Bit operations on the 32 bit numbers.', key=True),
     fx('Mask from prefix', 'mask = 2<sup>32</sup> &minus; 2<sup>32 &minus; n</sup>', '/24 = 255.255.255.0, /26 = 255.255.255.192, /16 = 255.255.0.0.'),
     fx('Block size', 'block = 2<sup>32 &minus; n</sup> = 256 &minus; (last non 255 mask byte)', '/26: 256 &minus; 192 = 64, so networks start at .0, .64, .128, .192.'))}
{steps('Worked example: which network is 10.1.5.200/22 in?', [
    '/22 leaves 10 host bits. The third byte has 6 network bits and 2 host bits, so the block size there is 2<sup>2</sup> = 4.',
    'Third byte 5 lies in the block 4 to 7 (multiples of 4: 0, 4, 8, ...).',
    eq('network = 10.1.4.0/22'),
    'Broadcast: the last address of the block, 10.1.7.255.',
    eq('hosts = 2<sup>10</sup> &minus; 2 = 1,022'),
    'So a firewall rule for 10.1.4.0/22 covers 10.1.4.0 to 10.1.7.255.'])}
''', kw=['subnet', 'subnetting', 'CIDR', 'subnet mask', 'prefix', 'network address', 'broadcast address', 'hosts formula', 'block size'])

K.lesson('ports', 'Ports, TCP and UDP', f'''
{talk('An IP address gets a packet to the right computer, but a computer runs many programs at once: a browser, a mail app, a game. Ports tell the computer which program the packet is for. Think of an apartment building: the IP address is the building, and the port is the flat number. Servers listen on well known ports, so the web is on port 443, secure shell on 22, and so on. Attackers scan ports to see which doors are open, because each open port is a program that could have a bug. There are two main transport protocols. TCP is like a phone call: it sets up a connection, numbers every byte and resends anything lost. UDP is like dropping postcards in a box: fast and simple, but with no promise that they arrive. Both have their place, and both have their own attacks.')}
{run('ports')}
{table(['Port', 'Protocol', 'Service', 'Security note'], [
    ['20, 21', 'TCP', 'FTP', 'Passwords in plain text. Use SFTP or FTPS'],
    ['22', 'TCP', 'SSH', 'Encrypted remote login. Brute force target, use keys'],
    ['23', 'TCP', 'Telnet', 'Plain text. Should never be open today'],
    ['25', 'TCP', 'SMTP', 'Mail between servers. Spoofing without SPF, DKIM, DMARC'],
    ['53', 'UDP and TCP', 'DNS', 'Spoofing, cache poisoning, amplification floods, tunnelling'],
    ['67, 68', 'UDP', 'DHCP', 'Rogue DHCP servers can redirect traffic'],
    ['80', 'TCP', 'HTTP', 'Plain text web'],
    ['123', 'UDP', 'NTP', 'Time sync. Wrong time breaks logs and certificates'],
    ['161', 'UDP', 'SNMP', 'Default "public" community strings leak device data'],
    ['389, 636', 'TCP', 'LDAP, LDAPS', 'Directory of users. 636 is the encrypted form'],
    ['443', 'TCP (and UDP for HTTP/3)', 'HTTPS', 'Encrypted web'],
    ['445', 'TCP', 'SMB', 'Windows file sharing. Used by WannaCry. Never expose to the internet'],
    ['3306, 5432', 'TCP', 'MySQL, PostgreSQL', 'Databases should not face the internet'],
    ['3389', 'TCP', 'RDP', 'Remote desktop. A top ransomware entry point when exposed']])}
{versus('TCP and UDP', ['', 'TCP', 'UDP'], [
    ['Connection', 'Yes, three way handshake first', 'No, just send'],
    ['Delivery', 'Reliable: numbered bytes, acknowledgements, resends', 'Best effort: may be lost, repeated or out of order'],
    ['Speed and overhead', 'Slower, 20 byte header at least', 'Faster, 8 byte header'],
    ['Used for', 'Web, email, file transfer, SSH', 'DNS queries, video calls, games, VPNs such as WireGuard'],
    ['Typical attacks', 'SYN flood, session hijacking, RST injection', 'Spoofed source addresses, reflection and amplification floods']],
    'TCP when every byte must arrive, UDP when speed matters more than perfection. Because UDP has no handshake, its source address is easy to fake, which makes it the favourite tool for reflection attacks.')}
{note('Port ranges: 0 to 1023 well known (need admin rights to listen on Linux), 1024 to 49151 registered, 49152 to 65535 dynamic or private (used for the client side of connections).', 'exam')}
''', kw=['ports', 'well known ports', 'TCP', 'UDP', 'SSH 22', 'HTTPS 443', 'SMB 445', 'RDP 3389', 'DNS 53', 'port ranges', 'TCP vs UDP'])

K.lesson('tcp', 'The TCP handshake and reading a packet', f'''
{talk('TCP has to solve a hard problem: deliver every byte in order across a network that loses, delays and repeats packets. Its answer is to number every byte. At the start, each side picks a starting number and tells the other in a short three step greeting, called the three way handshake: SYN, SYN ACK, ACK. After that, each side acknowledges the next byte it expects. If an acknowledgement does not come back, the sender resends. This handshake matters for security in two ways. First, a SYN flood sends thousands of first steps and never finishes them, filling the server’s memory. Second, in the 1980s many systems picked predictable starting numbers, and in 1994 Kevin Mitnick famously used guessed sequence numbers to inject fake packets into a trusted connection. Today starting numbers are random. Let us watch the numbers move.')}
{viz('cytcp')}
{run('handshake')}
{fxs(fx('Acknowledgement number', 'ack = seq of the received segment + its data length (+ 1 for a SYN or FIN)', 'It always names the next byte the receiver expects.', key=True),
     fx('IPv4 header checksum', 'sum of 16 bit words with carries folded back = 0xFFFF for a correct header', 'One’s complement addition (RFC 791). It catches accidents, not attackers, because anyone can recompute it.'))}
<p>Every packet is just bytes. The program below reads a real 20 byte IPv4 header, the same way tools like Wireshark and intrusion detection systems do, and checks its checksum.</p>
{run('ip_header')}
{show('A TCP handshake in tcpdump (lines shortened)', '''10:01:02.100 IP 192.168.1.20.51514 > 203.0.113.10.443: Flags [S], seq 1000
10:01:02.130 IP 203.0.113.10.443 > 192.168.1.20.51514: Flags [S.], seq 5000, ack 1001
10:01:02.131 IP 192.168.1.20.51514 > 203.0.113.10.443: Flags [.], ack 5001''', {1: 'Flags [S] is a SYN from the client’s port 51514 to the server’s port 443.', 2: 'Flags [S.] is SYN plus ACK (the dot means ACK). ack 1001 = 1000 + 1.', 3: 'Flags [.] is the final ACK. The connection is established.'}, lang='text')}
{note('A checksum is not security. It detects random damage, but an attacker who changes a packet simply recomputes it. Protection against tampering needs a keyed MAC or a signature, which the Cryptography section teaches.', 'warn')}
''', kw=['TCP handshake', 'SYN', 'SYN-ACK', 'ACK', 'sequence number', 'acknowledgement', 'SYN flood', 'IPv4 header', 'checksum', 'tcpdump', 'Wireshark', 'Mitnick'])

K.lesson('dns', 'DNS, ARP and DHCP: the helpers that trust too much', f'''
{talk('Three small helper protocols make networks easy to use, and all three were designed to trust whoever answers first. DNS turns names like example dot com into IP addresses, so you never have to remember numbers. It was designed by Paul Mockapetris in 1983. ARP, from 1982, lets a computer on a local network find the MAC address that owns an IP address by simply shouting a question and believing the reply. DHCP, from 1993, hands a new device its IP address, its router and its DNS server automatically. Because none of them checks who is answering, an attacker on the same network can lie. A fake ARP reply puts the attacker in the middle of your traffic. A fake DNS answer sends you to a copy of your bank. A fake DHCP server can make every device use the attacker’s DNS. Knowing how they work tells you exactly what the attacker fakes.')}
{run('dns_lookup_model')}
{table(['DNS record', 'Holds', 'Security use'], [
    ['A and AAAA', 'IPv4 and IPv6 address of a name', 'Changing them redirects all visitors'],
    ['CNAME', 'An alias to another name', 'Dangling CNAMEs to deleted cloud services allow subdomain takeover'],
    ['MX', 'The mail servers for a domain', 'Where email for the domain is delivered'],
    ['TXT', 'Free text', 'Holds SPF and DMARC email policies, and domain ownership proofs'],
    ['NS', 'The authoritative name servers', 'Whoever controls these controls the whole domain'],
    ['PTR', 'Name for an address (reverse lookup)', 'Seen in logs and mail checks']])}
{attack([
    ['ARP spoofing: tells the LAN "the router’s IP is at my MAC"', 'Dynamic ARP inspection on switches, static ARP for key hosts, and encryption (TLS) so stolen traffic is unreadable'],
    ['DNS spoofing or cache poisoning: a fake answer for a bank’s name', 'DNSSEC signs DNS answers, random source ports and IDs in resolvers, HTTPS certificates catch the fake site'],
    ['Rogue DHCP server hands out the attacker’s DNS', 'DHCP snooping on switches only trusts the real server port'],
    ['DNS tunnelling: hides stolen data inside DNS queries', 'Watch for long random looking names and huge query volumes'],
    ['DNS amplification: small spoofed queries cause big answers to a victim', 'Close open resolvers, rate limit responses, filter spoofed sources (BCP 38)']])}
{steps('DHCP in four messages (DORA)', [
    '<b>Discover</b>: a new laptop broadcasts "is there a DHCP server?"',
    '<b>Offer</b>: the server offers an address, say 192.168.1.20, with the router and DNS server.',
    '<b>Request</b>: the laptop asks to take that offer.',
    '<b>Acknowledge</b>: the server confirms. The laptop now uses those settings, which is why a fake server that answers first can control them.'])}
''', kw=['DNS', 'DNS records', 'A record', 'MX', 'TXT', 'CNAME', 'DNSSEC', 'cache poisoning', 'ARP', 'ARP spoofing', 'DHCP', 'DORA', 'rogue DHCP', 'DNS tunnelling', 'amplification'])

K.lesson('http', 'HTTP and HTTPS in one page', f'''
{talk('The web runs on HTTP, the HyperText Transfer Protocol, which Tim Berners Lee created at CERN between 1989 and 1991. HTTP is a simple conversation: your browser sends a request, such as get this page, and the server sends a response with a status code and the content. Plain HTTP travels as readable text, so anyone on the path, such as the owner of a cafe Wi-Fi, can read your passwords and change the pages. HTTPS is the same HTTP conversation wrapped inside TLS encryption, which keeps it secret and proves you are talking to the real site. Today almost all web traffic is HTTPS. The Application Security section goes deep into web attacks. Here you only need to read a request and a response.')}
{show('An HTTP request and response', '''GET /account HTTP/1.1
Host: shop.example
Cookie: session=7f3a9c
User-Agent: Mozilla/5.0

HTTP/1.1 200 OK
Content-Type: text/html
Set-Cookie: session=7f3a9c; Secure; HttpOnly; SameSite=Lax

<html>...</html>''', {1: 'Method GET, path /account, protocol version.', 2: 'Host says which website, because one IP can host many sites.', 3: 'The session cookie proves who you are. Stealing it is as good as stealing the password.', 6: 'Status 200 means success. 301 and 302 redirect, 401 needs login, 403 is forbidden, 404 not found, 500 is a server error.', 8: 'Secure sends the cookie only over HTTPS, HttpOnly hides it from JavaScript, SameSite limits cross site sending.'}, lang='http')}
{table(['Status class', 'Meaning', 'Examples'], [
    ['1xx', 'Information', '101 Switching Protocols'],
    ['2xx', 'Success', '200 OK, 201 Created, 204 No Content'],
    ['3xx', 'Redirection', '301 Moved Permanently, 302 Found, 304 Not Modified'],
    ['4xx', 'Client error', '400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests'],
    ['5xx', 'Server error', '500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable']])}
{note('401 means "who are you? log in". 403 means "I know who you are, and you may not". Many apps mix them up, and testers check both.', 'exam')}
''', kw=['HTTP', 'HTTPS', 'request', 'response', 'methods', 'status codes', 'headers', 'cookies', 'Secure HttpOnly SameSite', '401 vs 403'])

K.lesson('versus', 'Comparing the models and protocols', f'''
{talk('Two models describe networks. The OSI model, published by the International Organization for Standardization in 1984, has seven neat layers and is used to teach and to talk about where a problem sits. The TCP IP model has four layers and describes what the internet actually runs. Security people use both: you will hear that a web application firewall works at layer seven, while a simple packet filter works at layers three and four. Next to these models, we compare IPv4 with IPv6. IPv6 is not just bigger. It removed broadcasts, made a neighbour discovery protocol that replaces ARP, and is often switched on by default even when nobody manages it, which can open a door that the IPv4 firewall does not cover.')}
{versus('OSI and TCP/IP', ['', 'OSI model', 'TCP/IP model'], [
    ['Layers', '7: physical, data link, network, transport, session, presentation, application', '4: link, internet, transport, application'],
    ['Origin', 'ISO standard, 1984', 'The protocols of ARPANET and the internet, 1970s and 1980s'],
    ['Used for', 'Teaching, naming where a device or attack works ("a layer 7 firewall")', 'Describing the real internet stack'],
    ['Session and presentation', 'Separate layers', 'Part of the application layer (TLS sits here in practice)']],
    'Learn both. Use the OSI numbers to say where something works, and the TCP/IP model to understand real packets.')}
{versus('IPv4 and IPv6', ['', 'IPv4', 'IPv6'], [
    ['Address size', '32 bits, about 4.3 billion', '128 bits, about 3.4 &times; 10<sup>38</sup>'],
    ['Written as', '192.168.1.20', '2001:db8::1 (hex groups, :: shortens zeros)'],
    ['Finding neighbours', 'ARP (no authentication)', 'Neighbour Discovery (also spoofable, SEND adds signatures)'],
    ['NAT', 'Common, hides many devices behind one address', 'Usually not needed, every device can have a public address'],
    ['Security trap', 'Spoofing and ARP attacks', 'Enabled by default but forgotten in firewall rules and monitoring']],
    'IPv6 does not make networks secure by itself. Make sure firewall rules, logging and monitoring cover IPv6 as well as IPv4.')}
''', kw=['OSI vs TCP/IP', 'IPv4 vs IPv6', 'layer 7', 'neighbour discovery', 'comparison'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Networking for security goes from simple to very deep. A beginner knows that data travels in packets with addresses. A college student reads headers, calculates subnets and knows the common ports and their risks. A masters student studies routing protocols such as BGP, the system that ties the internet’s networks together, and how a single false route announcement can pull a country’s traffic into the wrong place. Researchers measure the whole internet, build programmable networks and design protocols with formal proofs. In 2008, for example, the security researcher Dan Kaminsky found a way to poison DNS caches at scale, and the whole industry patched DNS servers together in secret before announcing it. Pick your level and keep climbing.')}
{ladder(
    '<p>Computers send data in small packets. Each packet has an address so it reaches the right computer, and a port so it reaches the right app. Some traffic is locked (HTTPS) and some is not (HTTP).</p>',
    '<p>Use the four TCP/IP layers, compute subnets with CIDR, read IP and TCP headers, know the handshake and the common ports, and explain ARP, DNS and DHCP spoofing.</p>',
    '<p>The internet is a network of autonomous systems that exchange routes with BGP, which by default trusts announcements. Prefix hijacks (for example the 2008 Pakistan Telecom YouTube incident) send traffic the wrong way. RPKI signs which network may announce which prefix. TCP congestion control, QUIC (HTTP/3 over UDP with built in TLS 1.3) and DNS over HTTPS change what defenders can see.</p>',
    '<p>Research measures attacks across the whole internet (network telescopes that watch unused address space see scans and backscatter from spoofed floods), builds verified protocol implementations, and studies traffic analysis: even encrypted packets leak which site you visit through sizes and timing, which motivates padding and anonymity networks such as Tor.</p>')}
{grow('Explain packets, addresses and ports, and why HTTPS is safer than HTTP.',
      'Calculate subnets, read packet headers, trace a TCP handshake and explain ARP, DNS and DHCP attacks.',
      'Explain BGP hijacks and RPKI, QUIC and encrypted DNS, and traffic analysis on encrypted traffic.')}
''', kw=['beginner', 'expert', 'BGP', 'prefix hijack', 'RPKI', 'QUIC', 'HTTP/3', 'DNS over HTTPS', 'traffic analysis', 'Tor', 'Kaminsky'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Data travels in <b>packets</b>. Each layer adds a header (encapsulation): application data, TCP or UDP (ports), IP (addresses), Ethernet or Wi-Fi (MAC addresses).',
    'TCP/IP has 4 layers, OSI has 7. Memory aid: Please Do Not Throw Sausage Pizza Away.',
    'MAC 48 bits, IPv4 32 bits, IPv6 128 bits, port 16 bits. Private ranges: 10/8, 172.16/12, 192.168/16. Loopback 127/8.',
    '<b>CIDR /n</b>: network = IP AND mask, broadcast = all host bits 1, hosts = 2<sup>32&minus;n</sup> &minus; 2.',
    'TCP is reliable with a <b>SYN, SYN-ACK, ACK</b> handshake and numbered bytes. ack = next expected byte. UDP is fast with no handshake, easy to spoof.',
    'Know the ports: 22 SSH, 23 Telnet, 25 SMTP, 53 DNS, 80 HTTP, 443 HTTPS, 445 SMB, 3389 RDP.',
    '<b>ARP, DNS and DHCP</b> trust the first answer, so attackers spoof them. Defences: dynamic ARP inspection, DNSSEC, DHCP snooping and TLS everywhere.',
    'HTTP status classes 1xx to 5xx. 401 means log in, 403 means not allowed. Secure, HttpOnly and SameSite protect cookies.'],
    'Foundations 2.3 teaches the Python a security person uses every day: bytes, hashing, regular expressions for logs, parsing packets and simple safe tools.')}
{files('Three tasks: the network address of an IP and prefix, the number of hosts in a subnet, and whether an address is private.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'How many bits are in an IPv4 address?', ['16', '32', '48', '128'], 1, 'Four bytes.', 'IPv4 has 32 bits, written as four numbers from 0 to 255.')
K.quiz('e', 'Which port does HTTPS normally use?', ['80', '22', '443', '25'], 2, 'Secure web.', 'HTTPS listens on TCP port 443.')
K.quiz('e', 'Which address is private?', ['8.8.8.8', '192.168.1.10', '203.0.113.5', '1.1.1.1'], 1, 'RFC 1918.', '192.168.0.0/16 is a private range.')
K.quiz('e', 'What does DNS do?', ['Encrypts web pages', 'Turns names into IP addresses', 'Gives devices MAC addresses', 'Blocks viruses'], 1, 'Like a phone book.', 'DNS maps names such as example.com to IP addresses.')
K.quiz('m', 'The three way handshake is', ['SYN, ACK, FIN', 'SYN, SYN-ACK, ACK', 'ACK, SYN, RST', 'GET, POST, PUT'], 1, 'Start, agree, confirm.', 'SYN, SYN-ACK, ACK sets up a TCP connection.')
K.quiz('m', 'How many usable hosts does a /24 network have?', ['256', '254', '255', '24'], 1, '2<sup>8</sup> &minus; 2.', '256 addresses minus network and broadcast = 254.')
K.quiz('m', 'ARP spoofing works because', ['ARP is encrypted', 'ARP replies are believed without any check', 'ARP uses port 443', 'Routers block ARP'], 1, 'Trust.', 'Hosts accept any ARP reply, so an attacker can claim the router’s IP.')
K.quiz('m', 'Which protocol has no handshake and is easy to spoof?', ['TCP', 'UDP', 'TLS', 'SSH'], 1, 'Postcards.', 'UDP sends without a handshake, so the source address is easy to fake.')
K.quiz('m', 'Is 172.32.5.1 a private address?', ['Yes, everything 172.x is private', 'No, the private block 172.16.0.0/12 ends at 172.31.255.255', 'Only on weekends', 'Yes, it is loopback'], 1, 'Check the /12 range.', '172.16.0.0/12 covers 172.16 to 172.31 only.')
K.quiz('h', 'A client SYN has seq 4000. The server’s SYN-ACK must carry ack =', ['4000', '4001', '4002', 'any value'], 1, 'A SYN uses one sequence number.', 'The SYN counts as one byte, so the next expected is 4001.')
K.quiz('h', 'Why does the IPv4 checksum not stop an attacker from changing a packet?', ['It is too long', 'Anyone can recompute it after changing the packet, it has no secret key', 'Routers ignore it', 'It is encrypted'], 1, 'No key.', 'Checksums catch accidents. Tamper protection needs a keyed MAC or signature.')
K.quiz('h', 'Which network contains 10.1.5.200/22?', ['10.1.5.0/22', '10.1.4.0/22', '10.1.0.0/22', '10.1.8.0/22'], 1, 'Block size 4 in the third byte.', '5 is in the block 4 to 7, so the network is 10.1.4.0/22.')
K.quiz('x', 'In the style of a Stanford CS144 exam: a resolver uses a fixed source port and only a 16 bit query ID. Roughly how many forged answers must an off path attacker send to guess the ID with 50% chance for one query?', ['About 2<sup>8</sup>', 'About 2<sup>15</sup> (half of 65,536)', 'About 2<sup>32</sup>', 'One'], 1, 'Guessing one value out of 2<sup>16</sup>.', 'With 2<sup>16</sup> IDs, sending half of them gives 50%. Random source ports add about 16 more bits, which is why Kaminsky’s fix used them.')
K.quiz('x', 'In the style of an MIT 6.829 question: a DNS amplification attack sends 60 byte queries that cause 3,000 byte answers to the victim. What is the amplification factor?', ['5', '50', '500', '3000'], 1, 'Answer size / query size.', '3000 / 60 = 50. A 1 Gbit/s attacker can aim 50 Gbit/s at the victim.')

K.calc('e', 'How many addresses (including network and broadcast) are in a /28?', '16', '2<sup>32 &minus; 28</sup>.', ['32 &minus; 28 = 4 host bits.', '2<sup>4</sup>.', eq('= 16')], check=2 ** 4)
K.calc('e', 'How many usable hosts are in a /27?', '30', '2<sup>5</sup> &minus; 2.', ['32 &minus; 27 = 5.', '2<sup>5</sup> = 32.', eq('32 &minus; 2 = 30')], check=2 ** 5 - 2)
K.calc('e', 'A SYN has seq 100. What ack does the SYN-ACK carry?', '101', 'Plus one.', ['The SYN uses one sequence number.', '100 + 1.', eq('ack = 101')], check=101)
K.calc('m', 'What is the last byte of the subnet mask for /26 (as a decimal number)?', '192', 'Two network bits in the last byte.', ['Last byte bits: 11000000.', '128 + 64.', eq('= 192')], check=128 + 64)
K.calc('m', 'What is the network address of 192.168.10.77/26? Give the last byte.', '64', 'Block size 64.', ['/26 block size = 64.', '77 lies in 64 to 127.', eq('network ends in .64')], check=77 - 77 % 64)
K.calc('m', 'What is the broadcast address of 192.168.10.77/26? Give the last byte.', '127', 'Last address of the block.', ['Block is 64 to 127.', 'Broadcast = last one.', eq('.127')], check=64 + 64 - 1)
K.calc('m', 'Client seq 1001 sends 250 bytes. What ack does the server send back?', '1251', 'seq + length.', ['Bytes 1001 to 1250.', 'Next expected byte.', eq('1001 + 250 = 1251')], check=1001 + 250)
K.calc('h', 'How many /24 subnets fit in a /16 network?', '256', '2<sup>24 &minus; 16</sup>.', ['8 extra network bits.', '2<sup>8</sup>.', eq('= 256')], check=2 ** 8)
K.calc('h', 'What prefix gives at least 500 usable hosts with the fewest addresses? Answer the prefix number.', '23', 'Smallest h with 2<sup>h</sup> &minus; 2 &ge; 500.', ['2<sup>8</sup> &minus; 2 = 254, too small.', '2<sup>9</sup> &minus; 2 = 510, enough, so 9 host bits.', eq('prefix = 32 &minus; 9 = 23')], check=32 - next(h for h in range(1, 33) if 2 ** h - 2 >= 500))
K.calc('h', 'A DNS amplification query is 64 bytes and the answer 4,096 bytes. What is the amplification factor?', '64', 'Divide.', ['Answer 4,096 bytes.', 'Query 64 bytes.', eq('4096 / 64 = 64')], check=4096 // 64)
K.calc('x', 'In the style of a Cornell CS 4450 problem: folding a 16 bit ones complement sum, what is 0xB861 + 0x4500 + 0xC0A8 with carries folded? Answer in decimal.', '48650', 'Add, then add the carry back.', ['0xB861 + 0x4500 = 0xFD61. Plus 0xC0A8 = 0x1BE09.', 'Fold: 0xBE09 + 0x1 = 0xBE0A.', eq('0xBE0A = 48,650')], check=(lambda t: (t & 0xFFFF) + (t >> 16))(0xB861 + 0x4500 + 0xC0A8))

K.assign('netaddr', 'm', 'Network address of an IP and prefix',
         '<p>Write <code>network(ip, prefix)</code>. ip is text such as "192.168.10.77" and prefix a number from 1 to 32. Return the network address as text, by setting every host bit to 0. Do not use the ipaddress module.</p>',
         '''
def network(ip, prefix):
    # your code here
    pass
''', [('network("192.168.10.77", 26)', '192.168.10.64'), ('network("10.1.5.200", 22)', '10.1.4.0'), ('network("8.8.8.8", 32)', '8.8.8.8'), ('network("172.31.9.9", 12)', '172.16.0.0')],
         '''
def network(ip, prefix):
    n = 0
    for part in ip.split("."):
        n = n * 256 + int(part)
    host_bits = 32 - prefix
    n = (n >> host_bits) << host_bits
    out = []
    for shift in [24, 16, 8, 0]:
        out.append(str((n >> shift) & 255))
    return ".".join(out)
''', 'Turn the four numbers into one 32 bit number, shift right by the host bits and back left (this clears them), then split into four bytes again.', '<p>Shifting right then left is the same as AND with the mask. Firewalls and routers do exactly this comparison for every packet.</p>')
K.assign('hosts', 'e', 'Usable hosts in a subnet',
         '<p>Write <code>usable_hosts(prefix)</code> that returns 2 to the power (32 minus prefix) minus 2. For /31 return 2 and for /32 return 1, the two special cases.</p>',
         '''
def usable_hosts(prefix):
    # your code here
    pass
''', [('usable_hosts(24)', 254), ('usable_hosts(26)', 62), ('usable_hosts(31)', 2), ('usable_hosts(32)', 1), ('usable_hosts(8)', 16777214)],
         '''
def usable_hosts(prefix):
    if prefix == 32:
        return 1
    if prefix == 31:
        return 2
    return 2 ** (32 - prefix) - 2
''', 'Handle 32 and 31 first, then use the formula.', '<p>/31 links between two routers use both addresses (RFC 3021), and /32 names one host. Every other subnet loses two addresses to the network and broadcast.</p>')
K.assign('private', 'e', 'Is this address private?',
         '<p>Write <code>is_private(ip)</code> that returns True when the IPv4 address is in 10.0.0.0/8, 172.16.0.0/12 or 192.168.0.0/16, else False. Use the numbers only, no modules.</p>',
         '''
def is_private(ip):
    # your code here
    pass
''', [('is_private("10.4.2.1")', True), ('is_private("172.20.0.9")', True), ('is_private("172.32.0.1")', False), ('is_private("192.168.1.1")', True), ('is_private("8.8.8.8")', False)],
         '''
def is_private(ip):
    a, b, c, d = [int(x) for x in ip.split(".")]
    if a == 10:
        return True
    if a == 172 and 16 <= b <= 31:
        return True
    if a == 192 and b == 168:
        return True
    return False
''', 'Split into four numbers. Check the first byte, and for 172 also check that the second byte is from 16 to 31.', '<p>Log analysts flag traffic where a private address appears on an internet facing interface, because private sources should never arrive from outside. That is a classic sign of spoofing.</p>')

K.must('Layers', 'TCP/IP: link (MAC), internet (IP), transport (ports, TCP/UDP), application. OSI has 7. Encapsulation adds a header per layer.')
K.must('Addresses', 'IPv4 32 bits, IPv6 128, MAC 48, port 16. Private 10/8, 172.16/12, 192.168/16. Loopback 127/8.')
K.must('Subnets', 'network = IP AND mask, broadcast = host bits all 1, hosts = 2<sup>32&minus;n</sup> &minus; 2.')
K.must('TCP and UDP', 'SYN, SYN-ACK, ACK. ack = next expected byte. UDP has no handshake, so it is easy to spoof and amplify.')
K.must('Ports', '22 SSH, 23 Telnet, 25 SMTP, 53 DNS, 80 HTTP, 443 HTTPS, 445 SMB, 3389 RDP. 0 to 1023 well known.')
K.must('Trusting helpers', 'ARP, DNS and DHCP believe the first answer. Defend with dynamic ARP inspection, DNSSEC, DHCP snooping and TLS.')

T = K.topic(
    slug='cy-networks', topic='cy-networks', step=(2, 'How computers and networks work', 'cy-f2', 'How operating systems keep users apart, how data moves across networks, and the Python every security person needs.', 'Beginner'),
    title='Networks for security: layers, addresses, subnets, TCP and DNS', short='Networks', badge='2.2', minutes=65,
    lead='Learn how computers talk: packets and encapsulation, the OSI and TCP/IP layers, MAC, IPv4 and IPv6 addresses, private ranges and NAT, subnet maths with CIDR, ports, TCP and UDP, the handshake with sequence numbers, reading a real IP header, DNS, ARP, DHCP and HTTP.',
    desc='networking for security, packets, packet switching, encapsulation, OSI model, TCP/IP model, MAC address, IPv4, IPv6, private addresses RFC 1918, NAT, loopback, CIDR, subnet mask, network and broadcast address, hosts formula, ports, well known ports, TCP vs UDP, three way handshake, sequence and acknowledgement numbers, SYN flood, IPv4 header, checksum, tcpdump, DNS records, DNSSEC, cache poisoning, ARP spoofing, DHCP DORA, rogue DHCP, DNS amplification, HTTP methods, status codes, cookies, HTTPS, BGP, RPKI, QUIC, traffic analysis.',
    summary='layers and encapsulation, addresses and private ranges, subnet maths, ports, TCP and UDP, the handshake, DNS, ARP, DHCP and HTTP.',
    keywords=['network', 'OSI', 'TCP/IP', 'IP address', 'subnet', 'CIDR', 'ports', 'TCP handshake', 'DNS', 'ARP spoofing'],
    recap='<p>Packets carry layered headers. Do subnet maths with AND, know the ports and the handshake, and remember that ARP, DNS and DHCP trust whoever answers.</p>',
    added='2026-11-14')
