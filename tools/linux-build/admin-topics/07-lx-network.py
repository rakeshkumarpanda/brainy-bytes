# System administration 4.1: networking. IPv4 addresses, CIDR prefixes and subnet masks, private ranges, MAC addresses
# and ARP, the default gateway, DNS and /etc/hosts, ports and sockets, TCP and UDP. The ip command (addr, link, route,
# neigh, route get), ping, traceroute and tracepath, ss, curl, nc, dig, host, getent hosts, resolvectl, tcpdump,
# netplan and NetworkManager (nmcli), hostnamectl. Sources: ip(8), ip-address(8), ip-route(8), ip-neighbour(8),
# ip-netns(8), ping(8), traceroute(8), ss(8), curl(1), nc(1) (OpenBSD netcat), dig(1), resolv.conf(5), hosts(5),
# nsswitch.conf(5), systemd-resolved(8), resolvectl(1), tcpdump(8), netplan(5) and the netplan documentation,
# nmcli(1), RFC 1918 (private addresses), RFC 4632 (CIDR), RFC 5737 (documentation addresses), RFC 9293 (TCP).
# Every real run box builds its own small network out of Linux network namespaces and veth cables in the build
# container, so the output is real and shows nothing of the build host. dnsmasq plays the DNS server.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('basics', 'Addresses, subnets, gateways, names and ports', f'''
<p>Every machine on a network needs a few facts to talk to others. <code>ip -br addr</code> and <code>ip route</code> show most of them.</p>
{table(['Idea', 'Example', 'What it does'], [
    ['IPv4 address with prefix', '<code>192.168.1.50/24</code>', 'the machine’s number on the network. /24 says the first 24 bits name the network, so 192.168.1.0 to 192.168.1.255 are neighbours'],
    ['Subnet mask', '<code>255.255.255.0</code>', 'the old way to write /24'],
    ['MAC address', '<code>52:54:00:12:34:56</code>', 'the hardware address of the network card, used on the local network only'],
    ['Default gateway', '<code>192.168.1.1</code>', 'the router that gets every packet for addresses outside the subnet'],
    ['DNS server', '<code>127.0.0.53</code> (systemd-resolved), which asks <code>192.168.1.1</code>', 'turns names such as www.shop.lab into addresses'],
    ['Port', '<code>22</code> ssh, <code>80</code> http, <code>443</code> https, <code>53</code> dns', 'picks the program on the target machine'],
    ['TCP and UDP', 'TCP for web and ssh, UDP for DNS and video calls', 'TCP sets up a connection and resends lost data. UDP sends single messages']])}
{table(['Private range (RFC 1918)', 'Prefix', 'Typical use'], [
    ['10.0.0.0 to 10.255.255.255', '10.0.0.0/8', 'company and cloud networks'],
    ['172.16.0.0 to 172.31.255.255', '172.16.0.0/12', 'Docker’s default bridge uses 172.17.0.0/16'],
    ['192.168.0.0 to 192.168.255.255', '192.168.0.0/16', 'home routers'],
    ['127.0.0.0/8', 'loopback', 'the machine itself, <code>localhost</code>']])}
{play('lx-packet')}
{sample('The network settings of the practice server', """ip -br addr
ip route
cat /etc/resolv.conf""", out=["""lo               UNKNOWN        127.0.0.1/8 ::1/128
enp0s3           UP             192.168.1.50/24 fe80::5054:ff:fe12:3456/64""", """default via 192.168.1.1 dev enp0s3 proto static
192.168.1.0/24 dev enp0s3 proto kernel scope link src 192.168.1.50""", """# This is /run/systemd/resolve/stub-resolv.conf managed by man:systemd-resolved(8).
# Do not edit.

nameserver 127.0.0.53
options edns0 trust-ad
search ."""], note='enp0s3 is the network card. Modern names describe where the card sits (en for Ethernet, p0s3 for PCI bus 0, slot 3), so they stay the same across reboots. The route for 192.168.1.0/24 is added by the kernel when the address is set. The default route sends everything else to the router. The addresses 198.51.100.0/24 and 203.0.113.0/24 used for shop.lab in this course are reserved for documentation (RFC 5737), so they never clash with real servers.')}
{talk('To talk on a network, a machine needs an address, a subnet, a gateway and a name server. The address, such as one nine two dot one six eight dot one dot fifty, is its number. The slash twenty four after it says that the first three numbers name the network, so every address that starts with one nine two dot one six eight dot one is a neighbour that can be reached directly. Everything else goes to the default gateway, the router. A D N S server turns names into addresses, and on Ubuntu a local helper called systemd resolved answers at one two seven dot zero dot zero dot five three. Finally, a port number picks the program on the other machine: twenty two for s s h, eighty for web pages, four four three for secure web pages. Try the animation to follow one request from a name to an answer, and see where it fails when something is wrong.')}
''', kw=['IP address', 'IPv4', 'CIDR', 'prefix length', 'subnet', 'subnet mask', 'MAC address', 'default gateway', 'router', 'DNS', 'port', 'TCP', 'UDP', 'RFC 1918', 'private addresses', 'loopback', 'localhost', 'interface name', 'enp0s3'])

K.lesson('ip', 'The ip command: interfaces, addresses and routes', f'''
{cmdtable([
    ('ip -br addr, ip addr show DEV', 'Addresses of all interfaces, short or long', 'ip -br addr'),
    ('ip -br link', 'Interfaces with state and MAC address', 'ip -br link'),
    ('ip route, ip route get ADDR', 'The routing table, and the route one address would take', 'ip route get 1.1.1.1'),
    ('ip neigh', 'The neighbour (ARP) table: IP to MAC on the local network', 'ip neigh'),
    ('ip addr add ADDR/PREFIX dev DEV', 'Add an address until the next reboot', 'sudo ip addr add 192.168.1.60/24 dev enp0s3'),
    ('ip link set DEV up, down', 'Switch an interface on or off', 'sudo ip link set enp0s3 down'),
    ('ip route add NET via GW', 'Add a route, for example a default route', 'sudo ip route add default via 192.168.1.1'),
    ('ping -c N HOST', 'Send N echo requests and measure the round trip', 'ping -c 3 192.168.1.1')])}
{run('Two machines and a cable, built from network namespaces', """ip netns add pc
ip netns add web
ip link add eth0 netns pc type veth peer name eth0 netns web
pc() { ip netns exec pc "$@"; }
pc ip -br link
pc ip addr add 192.168.50.10/24 dev eth0
pc ip link set eth0 up
ip -n web addr add 192.168.50.20/24 dev eth0
ip -n web link set eth0 up
pc ip -br addr
pc ip route
pc ping -c 2 192.168.50.20
pc ip neigh
pc ping -c 1 -W 1 10.9.9.9
ip -all netns delete""", note='A network namespace is a separate network stack inside one Linux kernel, the same feature that gives every container its own network. A veth pair is a virtual cable. ip netns exec runs a command inside a namespace, and the little function pc saves typing. Before ip link set up the interface is DOWN and has no address, and eth0@if2 means the other end of the cable is interface number 2 in the other namespace. Setting the address also adds the route for 192.168.50.0/24, so the other side can be reached directly, and ARP fills the neighbour table with its MAC address. There is no default route, so 10.9.9.9 is unreachable.', root=True)}
{note('Changes made with ip addr, ip link and ip route are lost at the next reboot. That is useful for tests, and the permanent settings go into netplan or NetworkManager (lesson 7). On a remote server, never take down the interface you are connected through.', 'warn')}
{talk('The ip command shows and changes the network settings of a Linux machine. Ip dash b r addr gives a short list of interfaces and their addresses, and ip route shows the routing table, which decides where each packet goes. Ip route get and an address tells you exactly which route that address would use. Ip neigh shows the neighbour table, the M A C addresses that A R P has found on the local network. With sudo you can add addresses and routes and switch interfaces on and off, but these changes only last until the next reboot. Ping sends small echo requests and shows how long each answer takes, the first test for any connection. In the demo, two network namespaces act as two machines joined by a virtual cable, which is exactly how containers get their own networks.')}
''', kw=['ip command', 'ip addr', 'ip -br addr', 'ip link', 'ip route', 'ip route get', 'ip neigh', 'ARP', 'neighbour table', 'ip addr add', 'ip link set up', 'ping', 'network namespace', 'ip netns', 'veth'])

K.lesson('routing', 'Routing between networks', f'''
<p>A machine sends a packet straight to a neighbour in its own subnet. For any other address it uses the most specific matching route, and the <b>default route</b> (0.0.0.0/0) matches everything. A <b>router</b> is a machine with interfaces in two networks that forwards packets between them.</p>
{run('A router between a home network and a server network', """for n in pc router srv; do ip netns add $n; done
ip link add eth0 netns pc type veth peer name lan netns router
ip link add eth0 netns srv type veth peer name dmz netns router
ip -n pc addr add 192.168.1.50/24 dev eth0
ip -n router addr add 192.168.1.1/24 dev lan
ip -n router addr add 10.0.0.1/24 dev dmz
ip -n srv addr add 10.0.0.80/24 dev eth0
for x in "pc eth0" "router lan" "router dmz" "srv eth0"; do set -- $x; ip -n $1 link set $2 up; done
ip netns exec pc ping -c 1 -W 1 10.0.0.80
ip -n pc route add default via 192.168.1.1
ip -n srv route add default via 10.0.0.1
ip netns exec router sysctl -w net.ipv4.ip_forward=1
ip netns exec pc ping -c 2 10.0.0.80
ip netns exec pc ip route get 10.0.0.80
ip netns exec pc traceroute -n -q 1 -w 1 10.0.0.80
ip -all netns delete""", note='Without a default route the first ping fails at once with Network is unreachable, because pc has no route for 10.0.0.0/24. After the default routes, the router must also be allowed to forward: net.ipv4.ip_forward is 0 by default, so a normal Linux machine never passes packets on. The ttl of 63 shows that one router took one off the starting value of 64. traceroute lists every hop on the way.', root=True)}
{table(['ping says', 'Meaning', 'Look at'], [
    ['<code>Network is unreachable</code>', 'no route at all, often no default route', '<code>ip route</code>'],
    ['<code>Destination Host Unreachable</code>', 'the target is in the local subnet but nobody answers ARP', 'is it on, cable, address, <code>ip neigh</code>'],
    ['no replies, 100% packet loss', 'packets leave but nothing comes back', 'the gateway, a firewall dropping ICMP, the route back'],
    ['<code>Name or service not known</code>', 'the name does not exist in DNS or /etc/hosts', 'spelling, <code>dig NAME</code>'],
    ['<code>Temporary failure in name resolution</code>', 'no DNS server could be asked', '<code>resolvectl status</code>, network up']])}
{talk('When a packet is not for a neighbour in the same subnet, Linux looks for the most specific route that matches the address, and if nothing else matches, it uses the default route to the router. A router is simply a machine with legs in two networks that forwards packets from one to the other. Linux can do this too, but only after you switch on ip forward, which is off by default. In the demo, a pc, a router and a server are three network namespaces. The first ping fails because the pc has no route to the server network. After adding default routes on both sides and enabling forwarding on the router, the ping works, the time to live drops by one for the hop, and traceroute shows the router on the way. The table shows what the different ping errors mean, which points you to the right fix.')}
''', kw=['routing', 'default route', 'routing table', 'longest prefix match', 'router', 'ip_forward', 'sysctl net.ipv4.ip_forward', 'traceroute', 'tracepath', 'TTL', 'Network is unreachable', 'Destination Host Unreachable'])

K.lesson('dns', 'Names: /etc/hosts, DNS and systemd-resolved', f'''
<p>Programs ask the C library to resolve a name. The order is set by the <code>hosts:</code> line of <code>/etc/nsswitch.conf</code>, on Ubuntu Server <code>hosts: files dns</code>: first <code>/etc/hosts</code>, then DNS. Desktops add mdns4_minimal for .local names. On Ubuntu, DNS questions go to systemd-resolved at 127.0.0.53, which asks the real DNS servers given by DHCP or netplan and caches the answers.</p>
{cmdtable([
    ('getent hosts NAME', 'Resolve the way programs do (hosts file and DNS)', 'getent hosts www.shop.lab'),
    ('dig NAME, dig +short NAME', 'Ask DNS directly, with full details or only the answer', 'dig +short MX shop.lab'),
    ('dig @SERVER NAME', 'Ask one particular DNS server', 'dig @1.1.1.1 example.org'),
    ('host NAME', 'A short summary of A and MX records', 'host shop.lab'),
    ('resolvectl status, resolvectl query NAME', 'DNS servers per interface, and a query through resolved', 'resolvectl status enp0s3'),
    ('/etc/hosts', 'Fixed names for this machine only', '192.168.1.20  files')])}
{table(['Record', 'Holds', 'Example'], [
    ['A, AAAA', 'IPv4 and IPv6 address', 'www.shop.lab. A 198.51.100.80'],
    ['CNAME', 'another name to look up instead', 'shop.lab. CNAME www.shop.lab.'],
    ['MX', 'mail server with a priority', 'shop.lab. MX 10 mail.shop.lab.'],
    ['NS', 'the servers responsible for a zone', 'shop.lab. NS ns1.shop.lab.'],
    ['TXT', 'free text, used by SPF, DKIM and domain checks', 'shop.lab. TXT "v=spf1 mx -all"'],
    ['PTR', 'reverse lookup: address to name', '80.100.51.198.in-addr.arpa. PTR www.shop.lab.']])}
{run('A small DNS server, and a client that uses it', """ip netns add router
ip netns add pc
ip link add eth0 netns pc type veth peer name lan netns router
ip -n router addr add 192.168.1.1/24 dev lan
ip -n pc addr add 192.168.1.50/24 dev eth0
ip -n router link set lan up
ip -n pc link set eth0 up
ip -n router link set lo up
ip netns exec router dnsmasq --no-resolv --no-hosts --listen-address=192.168.1.1 --bind-interfaces --local=/shop.lab/ --address=/www.shop.lab/198.51.100.80 --mx-host=shop.lab,mail.shop.lab,10 --host-record=mail.shop.lab,198.51.100.25 --pid-file=/run/dnsmasq-lab.pid
mkdir -p /etc/netns/pc
echo 'nameserver 192.168.1.1' > /etc/netns/pc/resolv.conf
ip netns exec pc dig +short www.shop.lab
ip netns exec pc dig +short MX shop.lab
ip netns exec pc dig wwww.shop.lab | grep -E 'status|SERVER'
ip netns exec pc getent hosts mail.shop.lab
echo '192.168.1.20 files.shop.lab files' >> /etc/netns/pc/hosts
ip netns exec pc getent hosts files
ip netns exec pc dig +short files.shop.lab
kill "$(cat /run/dnsmasq-lab.pid)"
rm -r /etc/netns/pc
ip -all netns delete""", note='dnsmasq is a small DNS server, here answering for the made-up zone shop.lab only. ip netns exec mounts /etc/netns/pc/resolv.conf and /etc/netns/pc/hosts over the real files for the commands it runs, which lets the pc have its own name settings. A misspelt name gets NXDOMAIN, which means the name does not exist. getent finds files through /etc/hosts, while dig asks DNS only and gets no answer for it. That difference explains many puzzles of the kind “ping works but dig says nothing”.', root=True)}
{talk('People use names, computers use numbers, and name resolution joins the two. When a program needs an address, Linux first checks slash etc slash hosts, a simple list of addresses and names for this machine only, and then asks D N S. On Ubuntu, D N S questions go to systemd resolved, a local helper at one two seven dot zero dot zero dot five three, which forwards them to the real D N S servers and remembers the answers. D N S stores records: A records hold addresses, M X records name mail servers, C NAME records point to another name. Dig asks D N S directly and shows the full answer, and getent hosts resolves a name exactly as programs do, including the hosts file. In the demo, a tiny D N S server answers for the made up zone shop dot lab, and you can see that a name in the hosts file works for getent but not for dig.')}
''', kw=['DNS', 'name resolution', '/etc/hosts', 'nsswitch.conf', 'systemd-resolved', '127.0.0.53', 'resolvectl', 'resolv.conf', 'dig', 'dig +short', 'host', 'getent hosts', 'A record', 'AAAA', 'CNAME', 'MX record', 'TXT record', 'PTR reverse lookup', 'NXDOMAIN', 'dnsmasq'])

K.lesson('ports', 'Ports and sockets: ss, curl and nc', f'''
<p>A server program <b>listens</b> on a port. A client connects from a random high port to that port, and the pair of addresses and ports is a <b>socket</b> connection. <code>ss</code> lists sockets, <code>curl</code> speaks HTTP, and <code>nc -z</code> tests whether a port is open.</p>
{cmdtable([
    ('ss -tlnp', 'TCP sockets that listen, numeric, with the program (needs sudo for other users’ programs)', 'sudo ss -tlnp'),
    ('ss -tulpn', 'TCP and UDP', 'sudo ss -tulpn'),
    ('ss -tn state established', 'Open connections', 'ss -tn state established'),
    ('curl -I URL', 'Only the HTTP status and headers', 'curl -I http://localhost'),
    ('curl -v URL', 'Show the connection and the full request and answer', 'curl -v https://example.org'),
    ('curl -o FILE URL', 'Save the body to a file', 'curl -o page.html http://localhost'),
    ('nc -zv HOST PORT', 'Is the port open', 'nc -zv files.shop.lab 22')])}
{run('A web server in one namespace, a client in another', """ip netns add srv
ip netns add pc
ip link add eth0 netns pc type veth peer name eth0 netns srv
ip -n srv addr add 10.0.0.80/24 dev eth0
ip -n pc addr add 10.0.0.50/24 dev eth0
ip -n srv link set eth0 up
ip -n pc link set eth0 up
mkdir -p /srv/lab-www
echo '<h1>It works</h1>' > /srv/lab-www/index.html
ip netns exec srv python3 -m http.server 80 --bind 10.0.0.80 --directory /srv/lab-www > /dev/null 2>&1 &
sleep 1
ip netns exec srv ss -tlnp | sed -E 's/pid=[0-9]+/pid=N/'
ip netns exec pc curl -sI http://10.0.0.80/ | head -1
ip netns exec pc curl -s http://10.0.0.80/
ip netns exec pc nc -zv -w 1 10.0.0.80 80
ip netns exec pc nc -zv -w 1 10.0.0.80 22
kill %1
rm -r /srv/lab-www
ip -all netns delete""", note='Python’s http.server is enough to play the web server. ss shows it listening on 10.0.0.80 port 80 (the process ID is replaced by N here, because it changes on every run). The Send-Q of a listening socket is its backlog, the queue of connections waiting to be accepted. Port 22 is closed, so the connection is refused at once.', root=True)}
{sample('Sockets of the practice server', """sudo ss -tlnp""", out="""State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
LISTEN 0      4096      127.0.0.54:53        0.0.0.0:*    users:(("systemd-resolve",pid=388,fd=17))
LISTEN 0      4096   127.0.0.53%lo:53        0.0.0.0:*    users:(("systemd-resolve",pid=388,fd=15))
LISTEN 0      4096         0.0.0.0:22        0.0.0.0:*    users:(("sshd",pid=412,fd=3))
LISTEN 0      4096            [::]:22           [::]:*    users:(("sshd",pid=412,fd=4))
LISTEN 0      511          0.0.0.0:80        0.0.0.0:*    users:(("nginx",pid=905,fd=6))
LISTEN 0      511             [::]:80           [::]:*    users:(("nginx",pid=905,fd=7))""", note='0.0.0.0 means every IPv4 address of the machine, and [::] every IPv6 address, so ssh and nginx can be reached from outside. systemd-resolved listens only on loopback addresses, so only this machine can use it. A service that should be private, such as a database, should listen on 127.0.0.1.')}
{talk('A server program listens on a port and waits. Ss shows these listening sockets: ss dash t l n p lists T C P sockets that listen, with numeric ports and the program that owns each one. Use sudo to see programs of other users. The address column matters. Zero dot zero dot zero dot zero means every address, so the service can be reached from the network, while one two seven dot zero dot zero dot one means this machine only, which is right for a database that only local programs use. Curl talks to web servers, and curl dash capital I shows just the status line and headers. Nc dash z v tests whether a port is open: succeeded, refused, or a timeout when a firewall drops the packets. In the demo, a tiny web server runs in one namespace and a client in another.')}
''', kw=['port', 'socket', 'listening socket', 'ss', 'ss -tlnp', 'ss -tulpn', 'netstat', '0.0.0.0', 'bind address', 'curl', 'curl -I', 'curl -v', 'nc -zv', 'netcat', 'Connection refused', 'backlog'])

K.lesson('trouble', 'Troubleshooting step by step, and tcpdump', f'''
{steps('When “the network does not work”, test from the bottom up', [
    'Is the interface up with an address? <code>ip -br addr</code>',
    'Can you reach the gateway? <code>ip route</code>, then <code>ping -c 3 192.168.1.1</code>',
    'Can you reach an outside address without DNS? <code>ping -c 3 1.1.1.1</code>',
    'Does DNS work? <code>dig +short example.org</code> and <code>resolvectl status</code>',
    'Is the port open on the server? <code>nc -zv HOST PORT</code>, and on the server <code>sudo ss -tlnp</code>',
    'Does the application answer? <code>curl -v http://HOST/</code>, then the service’s logs with <code>journalctl -u NAME</code>',
    'Still unclear: watch the packets with <code>sudo tcpdump -n -i DEV port PORT</code>'])}
{run('Watching a TCP handshake with tcpdump', """cd "$(mktemp -d)"
ip netns add srv
ip netns add pc
ip link add eth0 netns pc type veth peer name eth0 netns srv
ip -n srv addr add 10.0.0.80/24 dev eth0
ip -n pc addr add 10.0.0.50/24 dev eth0
ip -n srv link set eth0 up
ip -n pc link set eth0 up
ip netns exec srv python3 -m http.server 80 --bind 10.0.0.80 > /dev/null 2>&1 &
sleep 1
ip netns exec srv timeout 3 tcpdump -n -i eth0 -c 4 'tcp port 80' 2>/dev/null | awk '{print $3, $4, $5, $6, $7}' > dump.txt &
sleep 1
ip netns exec pc curl -s -o /dev/null -w '%{http_code}\\n' http://10.0.0.80/
wait %2
cat dump.txt | sed -E 's/\\.[0-9]{4,5} /.CLIENT /; s/\\.[0-9]{4,5}:/.CLIENT:/'
kill %1
ip -all netns delete""", note='The first three packets are the handshake: Flags [S] is SYN, [S.] is SYN-ACK and [.] is ACK. The fourth, [P.], pushes the HTTP request. The client port is random, so it is replaced by CLIENT here. tcpdump needs root, and -n keeps it from looking up names. Save a capture with -w file.pcap to open it later in Wireshark.', root=True)}
{talk('When someone says the network does not work, test from the bottom up, one layer at a time. First check that the interface is up and has an address. Then ping the gateway, then an outside address without using names, then test D N S with dig. If all that works, check whether the port is open with n c, and on the server whether the program listens, with ss. Then ask the application itself with curl dash v and read its logs. Each step that works rules out a whole group of causes. When nothing explains the problem, tcpdump shows the actual packets. In the demo it catches the three way handshake of a web request: S Y N, S Y N A C K and A C K, followed by the request itself.')}
''', kw=['network troubleshooting', 'bottom-up troubleshooting', 'tcpdump', 'packet capture', 'pcap', 'Wireshark', 'three-way handshake', 'SYN', 'SYN-ACK', 'ACK', 'TCP flags', 'curl -v'])

K.lesson('config', 'Permanent settings: netplan and NetworkManager', f'''
<p>Settings made with <code>ip</code> vanish at reboot. Ubuntu Server keeps them in YAML files under <code>/etc/netplan/</code>, which <code>netplan</code> turns into configuration for systemd-networkd (servers) or NetworkManager (desktops). Fedora, RHEL and most desktops use NetworkManager directly, with <code>nmcli</code>.</p>
{sample('The netplan file of the practice server', """sudo cat /etc/netplan/01-netcfg.yaml""", out="""network:
  version: 2
  ethernets:
    enp0s3:
      addresses:
        - 192.168.1.50/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses: [192.168.1.1]""", note='A static address, a default route and a DNS server. For DHCP, replace the three settings with dhcp4: true. YAML needs spaces, never tabs, and the indentation is part of the meaning. The file should be readable by root only, mode 600, because it can hold Wi-Fi passwords.')}
{cmdtable([
    ('sudo netplan try', 'Apply, and roll back after 120 seconds unless you press Enter', 'sudo netplan try'),
    ('sudo netplan apply', 'Apply the files now', 'sudo netplan apply'),
    ('netplan get, netplan status', 'Show the merged settings and the live state', 'sudo netplan status'),
    ('nmcli device status', 'NetworkManager: devices and their connections', 'nmcli device status'),
    ('nmcli connection modify NAME ipv4.addresses ...', 'Change a stored connection', 'sudo nmcli con mod "Wired connection 1" ipv4.method manual ipv4.addresses 192.168.1.50/24 ipv4.gateway 192.168.1.1'),
    ('nmcli connection up NAME', 'Activate it', 'sudo nmcli con up "Wired connection 1"'),
    ('hostnamectl set-hostname NAME', 'Set the machine’s name', 'sudo hostnamectl set-hostname web1')])}
{note('On a server you reach over ssh, always use netplan try instead of apply. If the new settings cut you off, you cannot press Enter, and netplan puts the old settings back after two minutes.', 'tip')}
{talk('Settings made with the ip command are gone after a reboot, so the permanent settings live in configuration files. On Ubuntu servers these are Y A M L files in slash etc slash netplan. Each file describes interfaces, with addresses, routes and name servers, or simply says D H C P four true. Indentation matters in Y A M L, and tabs are not allowed. Netplan try applies the change and rolls it back after two minutes unless you confirm, which protects you from locking yourself out of a remote server. Netplan apply makes it permanent. Desktops and Red Hat style systems use NetworkManager instead, controlled with n m c l i, where you modify a stored connection and bring it up. Hostnamectl sets the name of the machine.')}
''', kw=['netplan', '/etc/netplan', 'netplan try', 'netplan apply', 'YAML', 'dhcp4', 'static IP', 'systemd-networkd', 'NetworkManager', 'nmcli', 'nmcli connection', 'hostnamectl', 'set-hostname'])

K.lesson('practice', 'Practice: diagnose the network of the practice server', f'''
<p>Users say the web site on the practice server is down, and some names do not resolve. Work through the layers.</p>
{lab('Network checks from the bottom up', [
    ('Show all interfaces and their addresses in the short form.', 'ip -br addr', [{'out': r'enp0s3\s+UP\s+192\.168\.1\.50/24'}]),
    ('Show the routing table.', 'ip route', [{'out': 'default via 192.168.1.1'}]),
    ('Ping the gateway 192.168.1.1 three times.', 'ping -c 3 192.168.1.1', [{'out': '3 received'}]),
    ('Find the address of www.shop.lab with dig, showing only the answer.', 'dig +short www.shop.lab', [{'out': r'^198\.51\.100\.80$'}]),
    ('Ask which route the kernel would use for 198.51.100.80.', 'ip route get 198.51.100.80', [{'out': 'via 192.168.1.1 dev enp0s3'}]),
    ('List the listening TCP sockets with their programs.', 'sudo ss -tlnp', [{'out': 'nginx'}]),
    ('Stop nginx, then check http://localhost with curl -I to see the failure.', 'sudo systemctl stop nginx; curl -I http://localhost', [{'out': 'Failed to connect to localhost port 80'}]),
    ('Start nginx again and check that curl -I shows status 200.', 'sudo systemctl start nginx && curl -I http://localhost', [{'out': 'HTTP/1.1 200 OK'}]),
    ('Add the name files for 192.168.1.20 to /etc/hosts.', 'echo "192.168.1.20 files" | sudo tee -a /etc/hosts', [{'has': ['/etc/hosts', '192.168.1.20 files']}]),
    ('Ping files once by its new name.', 'ping -c 1 files', [{'out': '1 received'}]),
    ('Test whether port 22 is open on files.', 'nc -zv files 22', [{'out': 'succeeded'}])])}
{talk('Now be the admin who gets the call. Start at the bottom: show the interfaces and addresses, and the routing table, and ping the gateway. Look up the web shop’s address with dig, and ask the kernel which route it would take. Then list the listening sockets and see nginx on port eighty. Stop nginx on purpose, and watch curl fail to connect, which is exactly what users would see. Start it again and get the status two hundred, O K. Finally give the file server a short name in the hosts file, ping it by that name, and check that its s s h port is open.')}
''', kw=['network lab', 'ip practice', 'ping practice', 'dig practice', 'ss practice', 'curl practice', 'hosts file practice'])

K.lesson('levels', 'Networking from school to research', f'''
{ladder(
    '<p>Every device has an address, a router connects your home to the internet, and DNS turns names into addresses. ping tells you whether another machine answers.</p>',
    '<p>Read and set addresses, routes and DNS with ip, netplan and resolvectl, find listening services with ss, test ports with nc and curl, and troubleshoot from the bottom up. Bind private services to 127.0.0.1, and know the common ports.</p>',
    '<p>Network namespaces, veth pairs and bridges are how Docker and Kubernetes give each container its own network, with NAT through nftables. VLANs, bonding, WireGuard tunnels, IPv6 with SLAAC, load balancers and reverse proxies such as nginx or HAProxy build real data centre and cloud networks (VPCs, subnets, security groups, route tables).</p>',
    '<p>Research and large operators work on software-defined networking (OpenFlow, P4), fast packet processing with eBPF and XDP inside the kernel, new congestion control (BBR), QUIC and HTTP/3 over UDP, and measuring the internet at scale. Studies of big outages often trace them to BGP route leaks or DNS failures, which is why both are watched so closely.</p>')}
{scene('the site that worked by address but not by name', '<p>After a move to a new office network, a team could reach their test server with <code>curl http://10.20.0.15</code> but not with its name. <code>getent hosts test.internal</code> returned nothing while ping by address worked, so routing and the server were fine. <code>resolvectl status</code> showed the laptops still used the old office DNS server, which the new network blocked. Updating the DNS server in netplan, and running <code>netplan try</code>, fixed it in a minute because the layers were checked in order.</p>')}
{talk('Here is how networking knowledge grows. At school you learn that every device has an address, that the router connects your home to the internet, and that D N S turns names into addresses. Professionals read and change addresses, routes and D N S with ip and netplan, find services with ss, test ports with n c and curl, and always troubleshoot from the bottom up. Containers and clouds build on the same ideas: network namespaces and virtual cables give each container its own network, and cloud networks use subnets, route tables and security groups. Researchers and large operators push packets faster with e B P F, design new protocols like QUIC, and study how routing and D N S failures take down large parts of the internet.')}
''', kw=['container networking', 'bridge', 'NAT', 'VLAN', 'bonding', 'WireGuard', 'IPv6', 'SLAAC', 'reverse proxy', 'load balancer', 'VPC', 'security group', 'SDN', 'eBPF', 'XDP', 'BBR', 'QUIC', 'HTTP/3', 'BGP'])

K.quiz('e', 'Which command shows the IP addresses of a Linux machine?', ['ifconfig only', 'ip addr', 'route', 'ping'], 1, 'The ip tool.', 'ip addr, or ip -br addr for short.')
K.quiz('e', 'What does a default gateway do?', ['Stores names', 'Receives every packet for addresses outside the subnet', 'Gives out passwords', 'Blocks attacks'], 1, 'The router.', 'It forwards traffic to other networks.')
K.quiz('e', 'What does DNS do?', ['Encrypts traffic', 'Turns names into IP addresses', 'Assigns MAC addresses', 'Speeds up disks'], 1, 'Names.', 'Domain Name System.')
K.quiz('e', 'Which port does ssh use by default?', ['21', '22', '80', '443'], 1, 'Two twos.', '22.')
K.quiz('m', 'How many addresses does a /24 network hold?', ['24', '254', '256', '1024'], 2, '32 − 24 = 8 bits.', '2⁸ = 256, of which 254 are usable for hosts.')
K.quiz('m', 'ping says Network is unreachable. What is missing first of all?', ['DNS', 'A route, often the default route', 'The web server', 'A MAC address'], 1, 'No path.', 'Check ip route.')
K.quiz('m', 'Which file is checked before DNS on most Linux systems?', ['/etc/resolv.conf', '/etc/hosts', '/etc/hostname', '/etc/networks'], 1, 'Fixed names.', 'The order is set in /etc/nsswitch.conf.')
K.quiz('m', 'Which command lists listening TCP ports with their programs?', ['ss -tlnp', 'ip route', 'dig', 'ping -l'], 0, 'Socket statistics.', 'Use sudo to see all programs.')
K.quiz('m', 'A database listens on 0.0.0.0:5432 but should be local only. What should it listen on?', ['0.0.0.0', '127.0.0.1', '192.168.1.255', '::'], 1, 'Loopback.', 'Then only this machine can connect.')
K.quiz('h', 'dig finds no answer for a name, but getent hosts and ping work. Why?', ['DNS is down', 'The name is in /etc/hosts, which dig does not read', 'ping uses a cache', 'getent is broken'], 1, 'Different paths.', 'dig asks DNS only.')
K.quiz('h', 'A Linux router has both interfaces up, yet nothing passes between the networks. Which setting is likely off?', ['net.ipv4.ip_forward', 'vm.swappiness', 'kernel.hostname', 'net.ipv4.tcp_syncookies'], 0, 'Forwarding.', 'It is 0 by default.')
K.quiz('h', 'nc to a port answers Connection refused at once. What does that tell you?', ['A firewall dropped the packet', 'The host answered, but no program listens on that port', 'DNS failed', 'The cable is broken'], 1, 'A reset came back.', 'A silent drop would time out instead.')
K.quiz('h', 'Why use netplan try instead of netplan apply over ssh?', ['It is faster', 'It rolls back by itself if you lose the connection and cannot confirm', 'apply needs a reboot', 'try checks spelling only'], 1, 'Safety net.', 'The old settings return after 120 seconds.')
K.quiz('x', 'Which route wins for 10.1.2.3 when the table has 10.0.0.0/8, 10.1.0.0/16 and default?', ['default', '10.0.0.0/8', '10.1.0.0/16', 'the first one listed'], 2, 'Most specific.', 'The longest matching prefix wins.')

K.calc('e', 'A /24 network: how many host addresses are usable, leaving out the network and broadcast addresses?', '254', 'Two to the eight, minus two.', ['32 − 24 = 8 host bits.', '2⁸ = 256.', eq('256 − 2 = 254')], check=254)
K.calc('e', 'ping replies took 11.3, 11.6 and 11.9 ms. What is the average in ms?', '11.6', 'Add and divide.', ['11.3 + 11.6 + 11.9 = 34.8.', 'Divide by 3.', eq('11.6 ms')], check=11.6)
K.calc('m', 'How many usable host addresses does a /26 network have?', '62', 'Six host bits.', ['32 − 26 = 6.', '2⁶ = 64.', eq('64 − 2 = 62')], check=62)
K.calc('m', 'Write the subnet mask of a /20 as the value of its third byte.', '240', 'Bits 17 to 20 are on.', ['A /20 has 16 bits in the first two bytes.', 'The third byte has 4 bits on: 11110000.', eq('128 + 64 + 32 + 16 = 240')], check=240)
K.calc('h', 'A packet starts with TTL 64 and arrives with TTL 61. How many routers did it pass?', '3', 'Each router subtracts one.', ['64 − 61.', 'Every hop lowers the TTL by 1.', eq('3 routers')], check=3)
K.calc('h', 'A 10 MB file goes over a 100 Mbit/s link. About how many seconds does it take at full speed (1 byte = 8 bits)?', '0.8', 'Bytes to bits.', ['10 MB = 80 Mbit.', '80 ÷ 100.', eq('0.8 s')], check=0.8)
K.calc('x', 'How many /24 networks fit into 10.0.0.0/16?', '256', 'Difference of prefixes.', ['24 − 16 = 8 extra bits.', 'Each bit doubles the count.', eq('2⁸ = 256')], check=256)

K.must('Basics', 'Address with prefix (192.168.1.50/24), default gateway, DNS server, ports (22, 53, 80, 443), TCP and UDP. Private ranges 10/8, 172.16/12, 192.168/16.')
K.must('ip', 'ip -br addr, ip -br link, ip route, ip route get, ip neigh. ip addr add, ip link set up, ip route add default via GW last only until reboot.')
K.must('Names', '/etc/hosts first, then DNS through systemd-resolved at 127.0.0.53. getent hosts resolves like programs, dig asks DNS only. A, AAAA, CNAME, MX, NS, TXT, PTR.')
K.must('Sockets', 'sudo ss -tlnp shows listeners and programs. 0.0.0.0 is every address, 127.0.0.1 is local only. curl -I and -v, nc -zv HOST PORT.')
K.must('Method', 'Bottom up: interface, gateway, outside address, DNS, port, application, then tcpdump. Permanent settings in netplan (netplan try) or nmcli.')

T = K.topic(
    slug='networking', topic='networking',
    step=(4, 'Networking and security', 'lx-admin-4', 'Configure and troubleshoot networks, log in and copy files securely with SSH, and protect a server with a firewall and sensible hardening.', 'Advanced'),
    title='Networking: addresses, routes, DNS and sockets', short='Networking', badge='4.1', minutes=65, added='2026-11-23',
    lead='Read and change addresses and routes with ip, understand how a router and DNS move a request from a name to a server, find listening services with ss, test them with curl and nc, troubleshoot from the bottom up, and keep settings with netplan.',
    desc='IPv4 addresses, prefixes and masks, private ranges, MAC addresses and ARP, default gateways, DNS and /etc/hosts, ports, TCP and UDP. ip addr, link, route and neigh, ping and traceroute, routing and ip_forward, systemd-resolved, dig and getent, ss, curl and nc, tcpdump, netplan and nmcli, all run for real in network namespaces.',
    summary='Addresses and subnets, the ip command, routing, DNS, sockets, troubleshooting, netplan.',
    keywords=['ip', 'ip addr', 'ip route', 'ping', 'traceroute', 'DNS', 'dig', '/etc/hosts', 'ss', 'curl', 'nc', 'tcpdump', 'netplan', 'nmcli'],
    recap='<p>Each machine needs an address with a prefix, a default gateway, a DNS server and services listening on ports. ip shows and changes them until reboot, netplan or nmcli keep them. Names go through /etc/hosts and then DNS. ss shows listeners, curl and nc test them, and problems are found layer by layer from the interface up to the application, with tcpdump as the last resort.</p>')
