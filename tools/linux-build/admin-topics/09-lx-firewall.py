# System administration 4.3: firewall and hardening. What a packet filter does (netfilter hooks, default deny,
# connection tracking, first match), ufw (defaults, allow, deny, limit, insert, delete, app profiles, status),
# nftables (tables, chains, hooks, policy, sets, counters, nft -c and -f, /etc/nftables.conf), and hardening a
# server: updates with unattended-upgrades, fewer listening services, SUID files, kernel settings with sysctl,
# fail2ban, auditd and AppArmor.
# Sources: ufw(8), ufw-framework(8), nft(8), the nftables wiki (Simple ruleset for a server), nf_conntrack,
# sysctl(8) and the kernel ip-sysctl documentation, unattended-upgrades(8) and its Ubuntu configuration files,
# fail2ban-client(1), fail2ban-regex(1), jail.conf(5), auditctl(8), audit.rules(7), ausearch(8), aa-status(8),
# the Ubuntu Server guide (Security). Real boxes run ufw 0.36.2, nftables 1.0.9 and Fail2Ban 1.0.2 in the build
# container, each inside its own network namespace so the build host’s own rules are never touched.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

NETNS = """for n in web pc; do ip netns add $n; ip -n $n link set lo up; done
ip link add eth0 netns pc type veth peer name eth0 netns web
ip -n web addr add 10.0.0.80/24 dev eth0
ip -n pc addr add 10.0.0.50/24 dev eth0
ip -n web link set eth0 up
ip -n pc link set eth0 up
for p in 22 80 5432; do ip netns exec web nc -lk -p $p > /dev/null 2>&1 & done
sleep 1
probe() { for p in 22 80 5432; do ip netns exec pc nc -z -w 1 10.0.0.80 $p 2>/dev/null && echo "port $p open" || echo "port $p blocked"; done; }
"""

K.lesson('what', 'What a firewall does', f'''
<p>A <b>firewall</b> decides, packet by packet, which network traffic may reach a machine, leave it or pass through it. On Linux the filtering itself happens inside the kernel, in a framework called <b>netfilter</b>. Tools such as <code>nft</code>, <code>iptables</code>, <code>ufw</code> and <code>firewalld</code> only write the rules.</p>
{steps('How a new incoming connection is judged', [
    'The packet arrives on a network card. The kernel sees that it is for this machine and passes it to the <b>input</b> hook. Packets the machine sends go through <b>output</b>, and packets it routes for others through <b>forward</b>.',
    '<b>Connection tracking</b> (conntrack) checks whether the packet belongs to a connection that is already allowed. Replies and the rest of an allowed connection are accepted at once. This is what makes the firewall <b>stateful</b>.',
    'A new connection is compared with the rules from the top. The first rule that matches decides: accept, drop (silently) or reject (with an error back).',
    'If no rule matches, the chain’s <b>policy</b> decides. A safe server uses <b>default deny</b> for incoming traffic and opens only the ports it needs.'])}
{play('lx-firewall')}
{table(['Tool', 'What it is', 'Where you meet it'], [
    ['<code>nft</code> (nftables)', 'the current rule language and tool for netfilter', 'Debian, Ubuntu and RHEL use nftables underneath'],
    ['<code>iptables</code>', 'the older tool. Today it is usually iptables-nft, which writes nftables rules', 'old guides and scripts, Docker'],
    ['<code>ufw</code>', 'uncomplicated firewall, a simple front end', 'Ubuntu, installed by default but inactive'],
    ['<code>firewalld</code>', 'a front end with zones (public, internal and so on)', 'Fedora, RHEL, Rocky, AlmaLinux'],
    ['cloud security groups', 'filters in front of the virtual machine', 'AWS, Azure, Google Cloud, used together with the host firewall']])}
{note('Drop or reject. A dropped packet gets no answer, so the client waits until it gives up. A rejected one gets an error back at once (“Connection refused”). Drop is the usual choice for traffic from the internet, reject is friendlier inside your own network.', 'tip')}
{talk('A firewall decides which network traffic may reach your machine. On Linux the real work happens in the kernel, in a part called net filter, and tools such as n f t, i p tables and u f w just write the rules for it. When a packet arrives for your machine, connection tracking first checks whether it belongs to a connection that is already allowed, such as the reply to a web page you asked for. Those packets pass at once. A brand new connection is compared with your rules from the top, and the first rule that matches decides. If no rule matches, the default policy decides, and on a server that should be deny. Try the animation. Notice how a block rule placed below an allow rule never gets a chance, because the allow rule matches first.')}
''', kw=['firewall', 'packet filter', 'netfilter', 'input chain', 'output chain', 'forward chain', 'connection tracking', 'conntrack', 'stateful firewall', 'default deny', 'policy drop', 'first match', 'drop vs reject', 'nftables', 'iptables-nft', 'ufw', 'firewalld', 'security group'])

K.lesson('ufw', 'ufw: a simple firewall for Ubuntu', f'''
{cmdtable([
    ('ufw status verbose', 'Show whether it is on, the defaults and the rules', 'sudo ufw status verbose'),
    ('ufw default deny incoming', 'Block new incoming connections unless a rule allows them', 'sudo ufw default deny incoming'),
    ('ufw allow PROFILE|PORT/PROTO', 'Open a service by app profile or by port', 'sudo ufw allow OpenSSH'),
    ('ufw allow from NET to any port P proto tcp', 'Open a port for one address or network only', 'sudo ufw allow from 192.168.1.0/24 to any port 5432 proto tcp'),
    ('ufw limit PORT/PROTO', 'Allow, but deny an address that opens 6 or more connections in 30 seconds', 'sudo ufw limit 22/tcp'),
    ('ufw insert N RULE', 'Put a rule at position N instead of the end', 'sudo ufw insert 1 deny from 203.0.113.7'),
    ('ufw status numbered, ufw delete N', 'List rules with numbers, delete one', 'sudo ufw delete 3'),
    ('ufw enable, disable, reset', 'Turn on (and at boot), turn off, remove all rules', 'sudo ufw enable')])}
{run('Turn ufw on for a server and test it from another machine', NETNS + """probe
fw() { ip netns exec web ufw "$@"; }
fw default deny incoming
fw allow OpenSSH
fw allow 80/tcp
fw --force enable
fw status verbose
probe
fw insert 1 deny from 10.0.0.50 to any port 80 proto tcp
fw status numbered
probe
fw --force delete 1
probe
fw --force reset > /dev/null
rm -f /etc/ufw/*.rules.20*
kill $(jobs -p)""", note='The box runs ufw inside the namespace web, a small server with something listening on ports 22, 80 and 5432, and tests it from the namespace pc with nc. Before ufw is on, all three ports answer. After default deny with ssh and web allowed, 5432 is blocked. The deny rule for the client 10.0.0.50 is inserted at position 1, above the allow rules, so it wins for port 80. Deleting rule 1 opens port 80 again. --force skips the yes or no questions of enable and delete, which is needed here because the page is built without a keyboard. No (v6) rows appear in this lab namespace. On a normal Ubuntu server, where IPV6=yes in /etc/default/ufw, every rule without an address shows up twice, once for IPv4 and once as (v6).', root=True)}
{note('Always allow ssh before you run <code>ufw enable</code> on a remote server. ufw warns “Command may disrupt existing ssh connections” for this reason. Keep your session open and test a new login, as in chapter 4.2. Cloud consoles have a serial console for the day it still goes wrong.', 'warn')}
{talk('U f w, the uncomplicated firewall, comes with Ubuntu but starts switched off. A good start is ufw default deny incoming, then allow only what the server offers, for example OpenSSH and port eighty. Allow s s h before you enable the firewall, or you lock yourself out of a remote server. A rule can name an app profile, a port with its protocol, or a source address, such as allowing the database port only from the office network. Rules are checked from the top, so a block rule for one bad address must be inserted at position one with ufw insert. Ufw status numbered shows the order, and ufw delete with a number removes a rule. In the demo, nc from a second machine shows each port opening and closing for real.')}
''', kw=['ufw', 'ufw enable', 'ufw status', 'ufw status verbose', 'ufw status numbered', 'ufw default deny incoming', 'ufw allow', 'ufw deny', 'ufw limit', 'ufw insert', 'ufw delete', 'ufw reset', 'app profile', 'OpenSSH profile', 'allow from subnet', 'lock yourself out'])

K.lesson('nft', 'nftables: the rules underneath', f'''
{shape('A small server ruleset, /etc/nftables.conf', """table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif "lo" accept
		ct state established,related accept
		ct state invalid drop
		icmp type echo-request accept
		tcp dport { 22, 80 } counter accept
		counter comment "dropped by policy"
	}
}""", note='A table holds chains, and the family inet covers IPv4 and IPv6 together. A base chain is attached to a hook (input) with a priority and a policy. Each rule is a list of matches and a verdict, read from left to right. { 22, 80 } is an anonymous set. counter counts packets and bytes, so you can see which rules are used.')}
{cmdtable([
    ('nft list ruleset', 'Show every table, chain and rule', 'sudo nft list ruleset'),
    ('nft -c -f FILE', 'Check a file without loading it', 'sudo nft -c -f /etc/nftables.conf'),
    ('nft -f FILE', 'Load a file in one atomic step', 'sudo nft -f /etc/nftables.conf'),
    ('nft -a list chain inet filter input', 'Show rules with their handle numbers', 'sudo nft -a list chain inet filter input'),
    ('nft insert rule ...', 'Add a rule at the top of a chain (add puts it at the end)', 'sudo nft insert rule inet filter input tcp dport 443 accept'),
    ('nft delete rule inet filter input handle N', 'Delete one rule by handle', 'sudo nft delete rule inet filter input handle 7'),
    ('systemctl enable --now nftables', 'Load /etc/nftables.conf at every boot', 'sudo systemctl enable --now nftables')])}
{run('Load a ruleset, test it and read the counters', NETNS + """cd "$(mktemp -d)"
cat > fw.nft <<'NFT'
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif "lo" accept
		ct state established,related accept
		ct state invalid drop
		icmp type echo-request accept
		tcp dport { 22, 80 } counter accept
		counter comment "dropped by policy"
	}
}
NFT
ip netns exec web nft -c -f fw.nft && echo "syntax ok"
ip netns exec web nft -f fw.nft
probe
ip netns exec pc ping -c 1 -W 1 10.0.0.80 | grep -o '1 received'
ip netns exec web nft list ruleset
ip netns exec web nft insert rule inet filter input ip saddr 10.0.0.0/24 tcp dport 5432 accept
probe
ip netns exec web nft -a list chain inet filter input | sed -n '2,5p'
kill $(jobs -p)""", note='nft -c only checks the file, which catches typos before anything changes. Loading with -f replaces the rules in one step, so there is never a moment with half a firewall. Ports 22 and 80 are accepted and counted, 5432 falls through to the last counter and then to policy drop, and ping passes because echo requests are allowed. The counters show 2 packets accepted (one SYN for each open port) and 1 packet dropped. insert puts the new database rule at the top of the chain, so it is checked before everything else, and -a shows the handle numbers you need to delete a rule later.', root=True)}
{note('Use one tool per machine. ufw, firewalld and Docker all write nftables or iptables rules, and mixing them by hand makes the order hard to follow. On Ubuntu with ufw, look with <code>sudo nft list ruleset</code> but change things with ufw.', 'tip')}
{talk('Underneath u f w and firewalld, modern Linux uses n f tables. A ruleset has tables, a table has chains, and a base chain hangs on a hook such as input with a default policy. On a server the policy is drop, and the rules then accept traffic on loopback, packets of connections that are already established, ping, and the ports the server offers. Curly braces make a set, so one rule can cover several ports. Counters show how many packets each rule matched, which is the fastest way to see whether a rule is used at all. Check a file with n f t dash c before you load it, load it with n f t dash f, and enable the n f tables service so the rules come back after a reboot.')}
''', kw=['nftables', 'nft', 'nft list ruleset', 'nft -f', 'nft -c', 'table inet filter', 'base chain', 'hook input', 'policy drop', 'ct state established,related', 'ct state invalid', 'anonymous set', 'counter', 'rule handle', 'nft insert rule', 'nft delete rule', '/etc/nftables.conf', 'nftables.service', 'iptables-nft'])

K.lesson('harden', 'Hardening a server step by step', f'''
{steps('A short hardening checklist for a new server', [
    'Install security updates automatically. On Ubuntu, <code>unattended-upgrades</code> installs updates from the security pocket every day.',
    'Log in with ssh keys only, no root login (chapter 4.2), and give each admin their own account with sudo (chapter 1.1).',
    'List what listens on the network with <code>sudo ss -tulpn</code>. Stop and disable every service you do not need with <code>sudo systemctl disable --now NAME</code>, and bind internal ones to 127.0.0.1.',
    'Turn on the firewall with default deny incoming and only the needed ports open.',
    'Check files with the SUID bit, which run as their owner (often root). Only well known programs such as passwd and sudo should have it.',
    'Set safe kernel network settings with sysctl, and keep logs, an audit trail and backups so you notice and recover from a break-in.'])}
{shape('/etc/apt/apt.conf.d/20auto-upgrades', """APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";""", note='"1" means every day. Which updates are installed is set in /etc/apt/apt.conf.d/50unattended-upgrades, where Ubuntu allows the release’s security pocket by default. Run sudo dpkg-reconfigure -plow unattended-upgrades to write this file, and sudo unattended-upgrade --dry-run --debug to see what it would do. A reboot is still needed for a new kernel, and /var/run/reboot-required says so.')}
{run('Find listening services, SUID files and kernel settings', """ip netns add web
ip -n web link set lo up
ip netns exec web python3 -m http.server 8000 --bind 0.0.0.0 > /dev/null 2>&1 &
ip netns exec web python3 -m http.server 6379 --bind 127.0.0.1 > /dev/null 2>&1 &
sleep 1
ip netns exec web ss -tlnp | sed 's/,pid=[0-9]*//; s/,fd=[0-9]*//'
find /usr/bin /usr/sbin -perm -4000 -type f | sort
stat -c '%A %U %n' /usr/bin/passwd
ip netns exec web sysctl net.ipv4.ip_forward net.ipv4.tcp_syncookies net.ipv4.conf.all.accept_redirects
sysctl kernel.randomize_va_space
kill $(jobs -p)""", note='ss -tlnp lists TCP sockets in LISTEN state with the program that owns them (process ids are cut out here). 0.0.0.0:8000 is reachable from every network, 127.0.0.1:6379 only from the machine itself, which is how a cache or database should listen. -perm -4000 finds files with the SUID bit, shown as the s in -rwsr-xr-x. This list is the normal one for Ubuntu 24.04. A new or unknown SUID file is a classic sign of a break-in. In the sysctl output, ip_forward 0 means the machine does not route for others, syncookies 1 protects against SYN floods, randomize_va_space 2 is full address space randomisation, and accept_redirects 1 is worth turning off on a server.', root=True)}
{shape('/etc/sysctl.d/99-hardening.conf', """net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.tcp_syncookies = 1
kernel.kptr_restrict = 1""", note='Files in /etc/sysctl.d are read at boot. Apply them now with sudo sysctl --system. ICMP redirects let another machine change your routes, rp_filter drops packets whose source address could not come from that interface, and kptr_restrict hides kernel addresses from normal users.')}
{talk('Hardening means making a server a smaller target. First, let unattended upgrades install security updates every day, so known holes get fixed without you. Second, use ssh keys only and personal accounts with sudo. Third, look at what listens on the network with s s tulpn. Every listening program is a door, so stop the ones you do not need, and bind internal ones such as a cache or database to one twenty seven dot zero dot zero dot one. Fourth, switch on the firewall. Fifth, check for files with the S U I D bit, because they run as root, and an unknown one is a warning sign. Finally, set a few kernel network settings with sysctl, such as refusing I C M P redirects, and keep logs and backups so you can notice a problem and recover.')}
''', kw=['hardening', 'server hardening', 'unattended-upgrades', '20auto-upgrades', 'security updates', 'reboot-required', 'ss -tulpn', 'listening ports', 'attack surface', 'systemctl disable --now', 'bind to localhost', 'SUID', 'find -perm -4000', 'sysctl', 'sysctl.d', 'accept_redirects', 'rp_filter', 'tcp_syncookies', 'randomize_va_space', 'kptr_restrict'])

K.lesson('watch', 'fail2ban, auditd and AppArmor', f'''
{shape('/etc/fail2ban/jail.local', """[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true""", note='fail2ban reads logs, counts failures per address with a filter, and bans an address that fails maxretry times within findtime, for bantime. On Ubuntu 24.04 the file jail.d/defaults-debian.conf already enables the sshd jail, reads the systemd journal (backend = systemd) and bans with nftables. Put your own values in jail.local, because package updates replace jail.conf.')}
{run('Watch fail2ban ban a password guesser', """ip netns add web
ip -n web link set lo up
d=/srv/f2blab
mkdir -p $d
cp -r /etc/fail2ban $d/conf
rm -f $d/conf/jail.d/*
touch $d/auth.log
printf '%s\\n' '[DEFAULT]' 'banaction = nftables' 'backend = polling' '[sshd]' 'enabled = true' "logpath = $d/auth.log" 'maxretry = 5' 'findtime = 10m' 'bantime = 10m' > $d/conf/jail.local
f2b() { ip netns exec web fail2ban-client -c $d/conf -s $d/sock "$@"; }
ip netns exec web fail2ban-server -c $d/conf -s $d/sock -p $d/pid --logtarget $d/f2b.log -b 2>/dev/null
sleep 2
for i in 1 2 3 4 5 6; do echo "$(date -u +%Y-%m-%dT%H:%M:%S).000000+00:00 web1 sshd[210$i]: Failed password for invalid user admin from 203.0.113.7 port 5100$i ssh2" >> $d/auth.log; done
fail2ban-regex $d/auth.log $d/conf/filter.d/sshd.conf | grep '^Lines'
sleep 4
f2b status sshd
ip netns exec web nft list ruleset
f2b set sshd unbanip 203.0.113.7
f2b stop
rm -r $d""", note='The box writes six failed ssh logins from 203.0.113.7 into a log file. fail2ban-regex tests the stock sshd filter against that file and matches all six lines, a good check before you trust a jail. The server, running in its own network namespace with a polling backend, counts five failures within ten minutes and bans the address. The ban is a real nftables set with a rule that rejects port 22 for every address in it. unbanip lifts a ban by hand, for example when a colleague locked themselves out.', root=True)}
{cmdtable([
    ('fail2ban-client status sshd', 'Failures and banned addresses of a jail', 'sudo fail2ban-client status sshd'),
    ('fail2ban-client set JAIL unbanip IP', 'Lift a ban', 'sudo fail2ban-client set sshd unbanip 192.168.1.60'),
    ('auditctl -w FILE -p wa -k KEY', 'Record every write or attribute change of a file', 'sudo auditctl -w /etc/passwd -p wa -k identity'),
    ('ausearch -k KEY -i', 'Show the audit records with that key, readable', 'sudo ausearch -k identity -i'),
    ('aa-status', 'Which AppArmor profiles are loaded, in enforce or complain mode', 'sudo aa-status'),
    ('aa-complain, aa-enforce PROFILE', 'Switch a profile to logging only, or back to blocking', 'sudo aa-enforce /etc/apparmor.d/usr.bin.tcpdump')])}
{note('Rules added with auditctl are lost at reboot. Make them permanent in a file in /etc/audit/rules.d/ and load them with sudo augenrules --load. AppArmor is on by default in Ubuntu and limits what a program may open even when it runs as root. Its denials appear in the kernel log as apparmor="DENIED".', 'tip')}
{talk('Three more tools watch and limit a server. Fail2ban reads the logs, counts failed logins per address, and bans an address that fails too often, here five times in ten minutes. In the demo it really bans the address with an n f tables rule. Ubuntu enables its s s h jail as soon as you install it. Auditd records security events. A watch rule on slash etc slash passwd, made with auditctl dash w, logs every change to that file with a key you can search for with ausearch. App armor gives a program a profile that lists the files and abilities it may use, so even a broken program running as root cannot read everything. Aa status shows which profiles are loaded and whether they block or only log.')}
''', kw=['fail2ban', 'jail.local', 'jail.conf', 'defaults-debian.conf', 'bantime', 'findtime', 'maxretry', 'fail2ban-client status', 'unbanip', 'fail2ban-regex', 'sshd jail', 'auditd', 'auditctl -w', 'audit rules', 'ausearch', 'augenrules', 'AppArmor', 'aa-status', 'aa-enforce', 'aa-complain', 'apparmor DENIED'])

K.lesson('practice', 'Practice: lock down the practice server', f'''
<p>The practice server runs ssh on port 22 and nginx on port 80. A database on port 5432 should be reachable from the office network 192.168.1.0/24 only, and the address 203.0.113.7 keeps guessing passwords.</p>
{lab('Firewall and hardening', [
    ('Show whether the firewall is on.', 'sudo ufw status', [{'out': 'Status: inactive'}]),
    ('Set the default for incoming traffic to deny.', 'sudo ufw default deny incoming', [{'out': "Default incoming policy changed to 'deny'"}]),
    ('List the app profiles ufw knows.', 'sudo ufw app list', [{'out': 'OpenSSH'}]),
    ('Allow ssh by its app profile, before you switch anything on.', 'sudo ufw allow OpenSSH', [{'cmd': r'allow\s+OpenSSH'}, {'out': 'Rules updated'}]),
    ('Allow the web server on 80/tcp.', 'sudo ufw allow 80/tcp', [{'cmd': r'allow\s+80/tcp'}, {'out': 'Rules updated'}]),
    ('Allow port 5432 over tcp from 192.168.1.0/24 only.', 'sudo ufw allow from 192.168.1.0/24 to any port 5432 proto tcp', [{'cmd': r'from\s+192\.168\.1\.0/24.*5432'}, {'out': 'Rules updated'}]),
    ('Switch the firewall on.', 'sudo ufw enable', [{'out': 'Firewall is active and enabled on system startup'}]),
    ('Block 203.0.113.7 with a rule at position 1.', 'sudo ufw insert 1 deny from 203.0.113.7', [{'out': 'Rule inserted'}]),
    ('Show the rules with their numbers.', 'sudo ufw status numbered', [{'out': r'\[ 1\] Anywhere\s+DENY IN\s+203\.0\.113\.7'}]),
    ('Show the defaults and the ports behind each profile.', 'sudo ufw status verbose', [{'out': r'Default: deny \(incoming\)'}]),
    ('List the TCP ports that programs listen on, with the programs.', 'sudo ss -tlnp', [{'cmd': r'ss\s+-\w*t\w*l'}, {'out': 'sshd'}]),
    ('Find files with the SUID bit in /usr/bin.', 'find /usr/bin -perm -4000', [{'cmd': r'-perm\s+-4000'}, {'out': '/usr/bin/passwd'}])])}
{talk('Now lock down the practice server yourself. Check that the firewall is off, set the default for incoming traffic to deny, and look at the app profiles. Allow OpenSSH first, so you never lock yourself out, then the web port, and the database port only for the office network. Switch the firewall on, then block the password guesser with a rule at position one, above the allow rules. Look at the numbered and the verbose status to check the order and the defaults. Finally, list the listening ports with s s, and search for files with the S U I D bit.')}
''', kw=['ufw lab', 'firewall practice', 'hardening practice', 'ufw insert practice', 'ss practice', 'SUID practice'])

K.lesson('levels', 'Firewalls from school to research', f'''
{ladder(
    '<p>A firewall is a set of rules that decides which network traffic may come in or go out. A server should allow only the few services it offers, such as ssh and a web site, and block everything else.</p>',
    '<p>Use default deny, allow ssh first, open ports per service and per network, insert block rules above allow rules, test from another machine with nc, and read counters in nft. Keep the server updated with unattended-upgrades, remove services you do not need, check SUID files, use fail2ban against guessing, auditd for a trail and AppArmor to contain programs.</p>',
    '<p>Teams keep firewall rules in configuration management (Ansible, Terraform for cloud security groups), use network segmentation with separate zones for web, application and database servers, filter outgoing traffic too (egress filtering), and follow benchmarks such as the CIS Benchmarks and DISA STIGs, checked with tools like Lynis or OpenSCAP. Kubernetes uses NetworkPolicies, often enforced with eBPF tools such as Cilium.</p>',
    '<p>Research covers fast packet filtering with eBPF and XDP, which drops unwanted packets in the network driver before the normal kernel path, verification of firewall rule sets for conflicts and shadowed rules, zero trust networks where every connection is authenticated instead of trusting the local network, and intrusion detection with machine learning.</p>')}
{scene('the database that was open to the world', '<p>A start-up moved its database to a cloud server and left it listening on 0.0.0.0:5432 with no firewall, “just for the move”. Within days, automated scanners found it and tried thousands of logins. An engineer noticed the noise in the logs, bound the database to the private network, added a ufw rule that allowed 5432 only from the application servers, and set up fail2ban for ssh. The team then added a check that runs ss -tlnp on every server each night and reports any new listening port.</p>')}
{talk('Here is how firewall skills grow. At school you learn that a firewall is a set of rules that lets only wanted traffic in. Professionals use default deny, open each port only for the networks that need it, test from another machine, and harden the server with updates, fewer services, fail2ban, audit rules and app armor. Teams manage rules as code, split networks into zones, filter outgoing traffic too, and check servers against security benchmarks. Researchers build very fast filters with e B P F and X D P, check large rule sets for mistakes automatically, and work on zero trust networks, where no connection is trusted just because it comes from inside.')}
''', kw=['egress filtering', 'network segmentation', 'CIS Benchmark', 'DISA STIG', 'Lynis', 'OpenSCAP', 'NetworkPolicy', 'Cilium', 'eBPF', 'XDP', 'zero trust', 'shadowed rules', 'intrusion detection'])

K.quiz('e', 'What should a server’s default policy for incoming traffic be?', ['allow', 'deny', 'reject everything including replies', 'none'], 1, 'Default deny.', 'Then open only what you need.')
K.quiz('e', 'Which command shows whether ufw is on and lists its rules?', ['ufw show', 'ufw status', 'ufw list', 'ufw rules'], 1, 'Status.', 'Add verbose or numbered for more.')
K.quiz('e', 'What must you allow before ufw enable on a remote server?', ['Port 80', 'ssh (port 22)', 'ping', 'DNS'], 1, 'Your own way in.', 'Otherwise you lock yourself out.')
K.quiz('e', 'Which command lists the ports that programs listen on?', ['ls -ports', 'ss -tulpn', 'ps aux', 'ip route'], 1, 'Socket statistics.', 'With the owning program.')
K.quiz('m', 'A deny rule for one address sits below an allow rule for port 22. What happens to that address on port 22?', ['It is denied', 'It is allowed, because the first match wins', 'ufw refuses the rule', 'It is rate limited'], 1, 'Top to bottom.', 'Use ufw insert 1.')
K.quiz('m', 'What does connection tracking add to a firewall?', ['Speed only', 'Replies of allowed connections pass without their own rules', 'Logging', 'Encryption'], 1, 'Stateful.', 'ct state established,related accept.')
K.quiz('m', 'What is the difference between drop and reject?', ['None', 'drop sends no answer, reject sends an error back', 'reject is slower', 'drop logs the packet'], 1, 'Silent or not.', 'Drop causes a timeout.')
K.quiz('m', 'What does ufw limit 22/tcp do?', ['Opens port 22 for one hour', 'Allows, but denies an address that connects 6 or more times in 30 seconds', 'Limits bandwidth', 'Allows only IPv4'], 1, 'Rate limit.', 'A simple brake on guessing.')
K.quiz('m', 'Why is a new SUID root file a warning sign?', ['It uses disk space', 'It runs as root for any user who starts it', 'It slows the boot', 'It disables sudo'], 1, 'Set user ID.', 'Attackers leave them as back doors.')
K.quiz('h', 'Which nft command checks a ruleset file without loading it?', ['nft -f', 'nft -c -f', 'nft list ruleset', 'nft --test'], 1, 'Check.', 'Then load with nft -f.')
K.quiz('h', 'fail2ban has maxretry 5 and findtime 10m. When is an address banned?', ['After 5 failures in a day', 'After 5 failures within 10 minutes', 'After 10 failures', 'At once'], 1, 'Within findtime.', 'For bantime.')
K.quiz('h', 'A cache must be used only by programs on the same machine. How should it listen?', ['0.0.0.0', '127.0.0.1', 'The public address', 'Any port above 1024'], 1, 'Loopback.', 'Then no firewall rule is even needed.')
K.quiz('h', 'Where should auditd rules go so they survive a reboot?', ['In ~/.bashrc', 'A file in /etc/audit/rules.d/, loaded with augenrules', 'Only auditctl', '/etc/sysctl.conf'], 1, 'rules.d.', 'auditctl rules are temporary.')
K.quiz('x', 'Why does nft -f load a whole file in one step matter?', ['It is shorter', 'There is never a moment with only half the rules loaded', 'It saves memory', 'It skips conntrack'], 1, 'Atomic.', 'Either all rules or none.')

K.calc('e', 'A server offers ssh, http and https. With default deny, how many ports must be opened?', '3', 'One per service.', ['22, 80 and 443.', 'Count them.', eq('3 ports')], check=3)
K.calc('e', 'A ufw rule without an address shows twice in ufw status, for IPv4 and IPv6. How many rows do 4 such rules give?', '8', 'Two each.', ['Each rule has a v6 twin.', '4 × 2.', eq('8 rows')], check=8)
K.calc('m', 'A robot makes one failed guess every 30 seconds, starting at minute 0. With maxretry 5 and findtime 10m, after how many minutes is it banned?', '2', 'Time of the 5th failure.', ['Failures at 0, 0.5, 1, 1.5 and 2 minutes.', 'The 5th one triggers the ban.', eq('4 × 0.5 = 2 minutes')], check=2)
K.calc('m', 'ufw limit denies an address after 6 connections in 30 seconds. At most how many connections per minute can one address make?', '10', 'Up to 5 per 30 seconds.', ['The 6th is denied.', '5 per 30 s, two windows.', eq('5 × 2 = 10')], check=10)
K.calc('h', 'A port scan tries all 65535 TCP ports. Default deny with 3 open ports. How many ports are dropped?', '65532', 'Subtract the open ones.', ['65535 ports in total.', '3 are allowed.', eq('65535 − 3 = 65532')], check=65532)
K.calc('h', 'An nft counter shows 1800 packets dropped by policy in 1 hour. How many per minute on average?', '30', 'Divide by 60.', ['1 hour is 60 minutes.', '1800 ÷ 60.', eq('30 packets per minute')], check=30)
K.calc('x', 'With maxretry 5 per address, how many addresses must a botnet use to make 1000 guesses without any ban?', '250', 'Under the limit per address.', ['4 failures per address stay below 5.', '1000 ÷ 4.', eq('250 addresses')], check=250)

K.must('How it decides', 'netfilter in the kernel, input, output and forward hooks, conntrack lets established traffic pass, first matching rule wins, then the policy. Default deny on servers.')
K.must('ufw', 'default deny incoming, allow OpenSSH first, allow PORT/PROTO, allow from NET to any port P, limit, insert 1, status numbered and verbose, delete N, enable.')
K.must('nftables', 'table inet filter, a base chain on hook input with policy drop, ct state established,related accept, sets in braces, counters, nft -c -f, nft -f, nftables.service.')
K.must('Hardening', 'unattended-upgrades, ssh keys only, ss -tulpn and disable unused services, bind internal services to 127.0.0.1, find -perm -4000, sysctl.d settings.')
K.must('Watching', 'fail2ban jails with maxretry, findtime and bantime, auditctl -w with ausearch -k, AppArmor profiles with aa-status.')

T = K.topic(
    slug='firewall-hardening', topic='firewall',
    step=(4, 'Networking and security', 'lx-admin-4', 'Configure and troubleshoot networks, log in and copy files securely with SSH, and protect a server with a firewall and sensible hardening.', 'Advanced'),
    title='Firewall and hardening: ufw, nftables and a safer server', short='Firewall', badge='4.3', minutes=60, added='2026-11-24',
    lead='Understand how the kernel decides which packets to let in, set up ufw and nftables with default deny, and harden a server with automatic updates, fewer services, fail2ban, audit rules and AppArmor.',
    desc='netfilter hooks, connection tracking, first match and default deny, ufw defaults, allow, deny, limit, insert, delete and app profiles, nftables tables, chains, sets and counters, unattended-upgrades, ss -tulpn, SUID files, sysctl hardening, fail2ban, auditd and AppArmor, run for real with ufw, nft and fail2ban in network namespaces.',
    summary='Default deny, ufw, nftables, hardening checklist, fail2ban, auditd, AppArmor.',
    keywords=['firewall', 'ufw', 'nftables', 'nft', 'iptables', 'netfilter', 'conntrack', 'default deny', 'hardening', 'unattended-upgrades', 'SUID', 'sysctl', 'fail2ban', 'auditd', 'AppArmor'],
    recap='<p>The kernel’s netfilter lets replies of allowed connections pass, checks new ones against the rules from the top and falls back to the policy, which should be deny. ufw and nft write those rules. A hardened server also installs updates by itself, runs only the services it needs, has no unexpected SUID files, and uses fail2ban, auditd and AppArmor to slow down, record and contain attacks.</p>')
