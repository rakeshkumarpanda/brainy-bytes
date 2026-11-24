# System administration 4.2: SSH. How an ssh connection works (key exchange, host keys and known_hosts, user
# authentication), ssh-keygen, key types and passphrases, ssh-copy-id and authorized_keys, file modes, ssh-agent,
# ~/.ssh/config, running remote commands, scp, sftp and rsync over ssh, local and remote port forwarding, jump hosts,
# and the server side: sshd_config, sshd -t and -T, PasswordAuthentication, PermitRootLogin, AllowUsers, reloads.
# Sources: ssh(1), ssh_config(5), ssh-keygen(1), ssh-agent(1), ssh-add(1), ssh-copy-id(1), scp(1), sftp(1), rsync(1),
# sshd(8), sshd_config(5), the OpenSSH release notes (9.0 default key exchange sntrup761x25519), RFC 4251 to 4254.
# Real boxes run OpenSSH 9.6 in the build container: sshd inside a network namespace (with its own host name
# through unshare --uts) and the client in another, as the unprivileged user learner. A temporary user deploy plays
# the account on the server, and the last box removes it again.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('how', 'How an ssh login works', f'''
<p><b>SSH</b> (secure shell) gives you a shell, a command or a file copy on another machine over an encrypted connection. The client <code>ssh</code> connects to the server <code>sshd</code> on TCP port 22.</p>
{steps('One login, in order', [
    'TCP connection to port 22, then both sides agree on algorithms and run a key exchange. On OpenSSH 9.x the default is a hybrid of sntrup761 and x25519, meant to resist future quantum computers. Everything after this is encrypted.',
    'The server proves its identity with its <b>host key</b>. The client compares it with <code>~/.ssh/known_hosts</code>. On the first visit it shows the fingerprint and asks.',
    'The user proves their identity, best with a <b>key pair</b>: the client signs a challenge with the private key, and the server checks it against the public keys in <code>~/.ssh/authorized_keys</code> of the account. A password is the fallback.',
    'sshd starts a shell or the command you gave, as that user, and pipes its input and output through the encrypted channel.'])}
{play('lx-ssh')}
{table(['File', 'Side', 'Holds', 'Mode'], [
    ['<code>~/.ssh/id_ed25519</code>', 'client', 'your private key, never share it', '600'],
    ['<code>~/.ssh/id_ed25519.pub</code>', 'client', 'your public key, safe to share', '644'],
    ['<code>~/.ssh/known_hosts</code>', 'client', 'host keys of servers you trust (names hashed on Ubuntu)', '600 or 644'],
    ['<code>~/.ssh/config</code>', 'client', 'aliases and settings per host', '600'],
    ['<code>~/.ssh/authorized_keys</code>', 'server', 'public keys allowed to log in as this user', '600, folder 700'],
    ['<code>/etc/ssh/sshd_config</code>', 'server', 'settings of sshd', '644'],
    ['<code>/etc/ssh/ssh_host_*_key</code>', 'server', 'the host keys', '600']])}
{talk('S S H gives you a secure shell on another machine. The client, called s s h, connects to the server program, s s h d, on port twenty two. First the two sides run a key exchange, so everything that follows is encrypted, even your password. Then the server proves who it is with its host key. Your client keeps the host keys of servers you have visited in known hosts, and on the very first visit it shows the fingerprint and asks whether to trust it. If a known server suddenly shows a different key, ssh stops with a loud warning, because someone could be pretending to be that server. Next you prove who you are, best with a key pair. Your private key signs a challenge, and the server checks the signature with your public key in authorized keys. The private key never leaves your computer. Try the animation to see each step, and what you see when a step fails.')}
''', kw=['ssh', 'sshd', 'port 22', 'secure shell', 'key exchange', 'host key', 'known_hosts', 'fingerprint', 'public key authentication', 'authorized_keys', 'private key', 'man-in-the-middle', 'sntrup761x25519', 'REMOTE HOST IDENTIFICATION HAS CHANGED'])

K.lesson('keys', 'Key pairs: ssh-keygen, passphrases and ssh-agent', f'''
{cmdtable([
    ('ssh-keygen -t ed25519 -C COMMENT', 'Make a new key pair (Ed25519 is short, fast and the modern default)', 'ssh-keygen -t ed25519 -C "asha@laptop"'),
    ('ssh-keygen -t rsa -b 4096', 'An RSA key, for old servers that lack Ed25519', 'ssh-keygen -t rsa -b 4096'),
    ('ssh-keygen -lf FILE', 'Show the fingerprint of a key', 'ssh-keygen -lf ~/.ssh/id_ed25519.pub'),
    ('ssh-keygen -p -f FILE', 'Add or change the passphrase', 'ssh-keygen -p -f ~/.ssh/id_ed25519'),
    ('eval "$(ssh-agent -s)"', 'Start an agent that holds unlocked keys for this session', 'eval "$(ssh-agent -s)"'),
    ('ssh-add, ssh-add -l', 'Unlock a key into the agent, list loaded keys', 'ssh-add ~/.ssh/id_ed25519')])}
{run('Make a key pair and look at it', """ssh-keygen -t ed25519 -N '' -C 'learner@laptop' -f ~/.ssh/id_ed25519
ls -l ~/.ssh
cut -c1-60 ~/.ssh/id_ed25519.pub
ssh-keygen -lf ~/.ssh/id_ed25519.pub
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add -l
eval "$(ssh-agent -k)\"""", note='-N "" sets an empty passphrase so this page can be built without a keyboard. For your own keys, leave -N out and type a passphrase: then a stolen key file is useless without it, and ssh-agent asks for it only once per session. ssh-keygen created ~/.ssh with mode 700 and the private key with mode 600 by itself. The randomart picture is a drawing of the fingerprint, easier for people to compare than a long string.')}
{note('Never copy your private key to a server or into a chat. Give out only the .pub file. Use one key per device, so you can remove a lost laptop’s key from authorized_keys without touching the others.', 'warn')}
{talk('A key pair has two halves. The private key stays on your computer, readable only by you. The public key, the file ending in dot pub, can be copied anywhere. Ssh keygen dash t ed25519 makes a modern key pair, short and fast. Add a comment with dash capital C so you can recognise it later. Protect the private key with a passphrase, so a stolen file is useless. To avoid typing the passphrase for every login, start ssh agent once per session and unlock the key with ssh add. The fingerprint, shown with ssh keygen dash l f, is a short summary of a key that is easy to compare. Use a separate key for each device, so you can remove one without affecting the others.')}
''', kw=['ssh-keygen', 'ed25519', 'RSA key', 'key pair', 'passphrase', 'ssh-keygen -lf', 'fingerprint', 'randomart', 'ssh-agent', 'ssh-add', 'id_ed25519.pub', 'key per device'])

K.lesson('login', 'Installing a key and logging in', f'''
{run('An ssh server in one namespace, a client in another', """for n in web pc; do ip netns add $n; ip -n $n link set lo up; done
ip link add eth0 netns pc type veth peer name eth0 netns web
ip -n web addr add 10.0.0.80/24 dev eth0
ip -n pc addr add 10.0.0.50/24 dev eth0
ip -n web link set eth0 up
ip -n pc link set eth0 up
useradd -m -s /bin/bash deploy
echo 'deploy:Lab-only-pass-26' | chpasswd
mkdir -p /srv/sshlab
ssh-keygen -q -t ed25519 -N '' -f /srv/sshlab/ssh_host_ed25519_key
printf '%s\\n' 'ListenAddress 10.0.0.80' 'HostKey /srv/sshlab/ssh_host_ed25519_key' 'UsePAM yes' 'KbdInteractiveAuthentication no' 'Subsystem sftp /usr/lib/openssh/sftp-server' 'PidFile /srv/sshlab/sshd.pid' > /srv/sshlab/sshd_config
mkdir -p /run/sshd
ip netns exec web unshare --uts sh -c 'hostname web1 && exec /usr/sbin/sshd -f /srv/sshlab/sshd_config'
ssh-keygen -lf /srv/sshlab/ssh_host_ed25519_key.pub | cut -d' ' -f2
pc() { ip netns exec pc sudo -u learner "$@"; }
pc ssh -o BatchMode=yes deploy@10.0.0.80 true
pc ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes deploy@10.0.0.80 true
pc sshpass -p 'Lab-only-pass-26' ssh-copy-id deploy@10.0.0.80
pc ssh deploy@10.0.0.80 'hostname; whoami; ls -la .ssh'
pc ssh deploy@10.0.0.80 'echo "$SSH_CONNECTION"'""", note='The first try fails with Host key verification failed, because BatchMode cannot ask the question and the host is unknown. accept-new stores an unknown host key without asking but still refuses a changed one. That login has no key on the server yet and BatchMode forbids passwords, so it ends with Permission denied. ssh-copy-id logs in once with the password and appends your public key to ~/.ssh/authorized_keys on the server. sshpass types the password here only because this page is built without a keyboard. Never put a real password on a command line. After that, login works with the key alone. SSH_CONNECTION shows the client address and port and the server address and port. This box leaves the server running for the next lessons.', root=True, keep=True)}
{note('If key login fails, check modes first: on the server, the home folder must not be writable by others, ~/.ssh must be 700 and authorized_keys 600, or sshd logs “Authentication refused: bad ownership or modes”. On the client, a private key readable by others is ignored with “UNPROTECTED PRIVATE KEY FILE”. Then try <code>ssh -v</code>, which prints every step.', 'tip')}
{talk('Before you can log in with a key, your public key must be on the server, in the file authorized keys inside the dot s s h folder of the account. Ssh copy id does this for you: it logs in once with the password and appends your key. From then on, s s h logs in with the key, and you can switch password logins off. In the demo, a real s s h server runs in its own network namespace with the host name web one. The very first connection fails because the host is unknown and batch mode cannot ask. Accept new stores the host key, then ssh copy id installs the key, and the next login runs commands as the user deploy without any password. If key login ever fails, check the file modes on both sides first, and use s s h dash v to watch every step.')}
''', kw=['ssh-copy-id', 'authorized_keys', 'first login', 'StrictHostKeyChecking', 'accept-new', 'BatchMode', 'Host key verification failed', 'Permission denied (publickey)', 'remote command', 'SSH_CONNECTION', 'ssh -v', 'bad ownership or modes'])

K.lesson('config', 'Aliases, file copies and rsync over ssh', f'''
{shape('A host entry in ~/.ssh/config', """Host web1
    HostName 10.0.0.80
    User deploy
    Port 22
    IdentityFile ~/.ssh/id_ed25519""", note='After this, ssh web1 is enough. For each setting, the first value found wins, so put specific Host blocks before a general Host * block at the end.')}
{cmdtable([
    ('scp FILE HOST:PATH', 'Copy a file to a server', 'scp report.pdf web1:/tmp/'),
    ('scp HOST:PATH .', 'Copy a file from a server', 'scp web1:/var/log/syslog .'),
    ('scp -r DIR HOST:', 'Copy a folder', 'scp -r site web1:'),
    ('rsync -av -e ssh SRC/ HOST:DEST/', 'Copy only changes, resume big copies', 'rsync -av --delete site/ web1:/srv/www/'),
    ('sftp HOST', 'Interactive file transfer (ls, get, put)', 'sftp web1'),
    ('ssh HOST CMD < FILE', 'Feed a local file to a remote command', 'ssh web1 "sudo tee /etc/motd" < motd.txt')])}
{run('Use an alias, copy files with scp, sync with rsync', """mkdir -p site
printf '%s\\n' 'Host web1' '    HostName 10.0.0.80' '    User deploy' > .ssh/config
echo '<h1>Shop</h1>' > site/index.html
echo 'body{}' > site/style.css
chown -R learner: .ssh/config site
pc() { ip netns exec pc sudo -u learner "$@"; }
pc ssh web1 hostname
pc scp -q site/index.html web1:
pc ssh web1 ls
pc rsync -a site/ web1:www/
pc ssh web1 'ls www'
echo 'body{color:navy}' > site/style.css
pc rsync -av site/ web1:www/ | grep -v bytes
pc scp -q web1:www/style.css copy.css
cat copy.css""", note='The alias saves typing the address and user every time. scp copies whole files (-q hides its progress bar). rsync compares both sides and sends only files that changed, here just style.css on the second run, which makes it the better tool for repeated copies and big folders. Both use the same ssh login, key and known_hosts. Since OpenSSH 9.0, scp uses the SFTP protocol underneath, so the server needs the Subsystem sftp line that Ubuntu’s sshd_config has. (This box runs in learner’s home folder as root, so chown hands the new files to learner.)', root=True, keep=True, cwd='/home/learner')}
{talk('Typing user names and addresses gets old quickly, so put them in the file dot s s h slash config. A Host block gives an alias, and below it HostName, User, Port and IdentityFile say how to reach it. Then s s h web one is all you type, and every tool that uses s s h understands the alias too. To copy files, s c p works like c p with a host name and a colon in front of the remote path. Rsync over s s h is smarter: it compares both sides and sends only what changed, so the second run in the demo sends just the one changed file. Sftp gives an interactive file transfer session. All of them use the same keys and known hosts as s s h itself.')}
''', kw=['~/.ssh/config', 'Host alias', 'HostName', 'IdentityFile', 'scp', 'scp -r', 'sftp', 'rsync over ssh', 'rsync -e ssh', 'remote copy', 'file transfer'])

K.lesson('tunnels', 'Port forwarding and jump hosts', f'''
{table(['Option', 'What it does', 'Typical use'], [
    ['<code>-L 9000:127.0.0.1:8080</code>', 'local port 9000 leads to port 8080 as seen from the server', 'reach a database or admin page that listens only on the server’s localhost'],
    ['<code>-R 8080:127.0.0.1:3000</code>', 'port 8080 on the server leads back to port 3000 on your machine', 'show a local development site to someone on the server side'],
    ['<code>-D 1080</code>', 'a SOCKS proxy through the server', 'browse as if you were in the server’s network'],
    ['<code>-J bastion</code>', 'connect through a jump host (ProxyJump)', 'reach private servers behind one public bastion'],
    ['<code>-N -f</code>', 'no remote command, go to the background', 'keep a tunnel open without a shell']])}
{run('Reach a service that listens only on the server’s localhost', """mkdir -p /srv/sshlab/admin
echo 'admin page, local only' > /srv/sshlab/admin/index.html
ip netns exec web python3 -m http.server 8080 --bind 127.0.0.1 --directory /srv/sshlab/admin > /dev/null 2>&1 &
sleep 1
pc() { ip netns exec pc sudo -u learner "$@"; }
pc curl -s --max-time 2 http://10.0.0.80:8080/ || echo "direct: no connection"
pc ssh -f -N -o ExitOnForwardFailure=yes -L 9000:127.0.0.1:8080 web1
pc curl -s http://127.0.0.1:9000/
pkill -u learner -f 'ssh -f -N'
kill %1""", note='The admin page listens on 127.0.0.1 of the server only, so a direct connection from outside fails. The tunnel carries connections to port 9000 on the client through ssh, and on the server they are made to 127.0.0.1:8080. ExitOnForwardFailure makes ssh give up if the tunnel cannot be set up, instead of running without it.', root=True, keep=True)}
{shape('A jump host in ~/.ssh/config', """Host bastion
    HostName bastion.example.com
    User asha

Host db1
    HostName 10.0.5.20
    User asha
    ProxyJump bastion""", note='ssh db1 first logs in to bastion and from there opens the connection to 10.0.5.20. Your private key stays on your laptop the whole time, which is safer than copying keys to the bastion or using agent forwarding (-A).')}
{talk('S S H can carry other connections inside its encrypted channel. With dash capital L, a port on your own machine leads to a port as seen from the server, which is how admins reach a database or an admin page that listens only on the server’s localhost. In the demo, the admin page cannot be reached directly, but through the tunnel on port nine thousand it answers. Dash capital R works the other way round, and dash capital D makes a S O C K S proxy. Big networks hide their servers behind one public jump host, also called a bastion. With ProxyJump in the config file, s s h hops through it automatically, and your private key never leaves your laptop.')}
''', kw=['port forwarding', 'ssh tunnel', 'ssh -L', 'local forwarding', 'ssh -R', 'remote forwarding', 'ssh -D', 'SOCKS proxy', 'ProxyJump', 'ssh -J', 'jump host', 'bastion', 'ExitOnForwardFailure', 'agent forwarding'])

K.lesson('server', 'Securing sshd', f'''
{table(['sshd_config setting', 'Recommended', 'Why'], [
    ['<code>PasswordAuthentication</code>', '<code>no</code>, once keys work', 'stops password guessing completely'],
    ['<code>PermitRootLogin</code>', '<code>no</code> (Ubuntu default is <code>prohibit-password</code>)', 'log in as yourself and use sudo, which leaves a trail'],
    ['<code>PubkeyAuthentication</code>', '<code>yes</code> (default)', 'key login'],
    ['<code>AllowUsers</code>, <code>AllowGroups</code>', 'only the accounts that need ssh', 'a forgotten account cannot be used'],
    ['<code>MaxAuthTries</code>', '<code>3</code> to <code>6</code>', 'fewer guesses per connection'],
    ['<code>KbdInteractiveAuthentication</code>', '<code>no</code> unless you use one-time codes', 'another password path'],
    ['<code>X11Forwarding</code>', '<code>no</code> on servers', 'not needed without a desktop']])}
{steps('Change sshd settings without locking yourself out', [
    'Make sure key login works and keep one ssh session open the whole time.',
    'Put your changes in a file in <code>/etc/ssh/sshd_config.d/</code>, for example <code>50-hardening.conf</code>. The main file includes that folder near the top, and the first value found for a setting wins.',
    'Test the syntax with <code>sudo sshd -t</code>, and the effective values with <code>sudo sshd -T | grep -i password</code>.',
    'Reload with <code>sudo systemctl reload ssh</code>. Existing sessions stay open.',
    'Open a new session from a second terminal before you close the old one.'])}
{run('Test a config, harden it, and watch password login fail', """printf '%s\\n' 'HostKey /srv/sshlab/ssh_host_ed25519_key' 'PasswordAuthenticaton no' > /srv/sshlab/typo.conf
/usr/sbin/sshd -t -f /srv/sshlab/typo.conf
printf '%s\\n' 'PasswordAuthentication no' 'PermitRootLogin no' 'AllowUsers deploy' 'MaxAuthTries 3' >> /srv/sshlab/sshd_config
/usr/sbin/sshd -t -f /srv/sshlab/sshd_config && echo syntax ok
/usr/sbin/sshd -T -f /srv/sshlab/sshd_config | grep -E '^(passwordauthentication|permitrootlogin|allowusers|maxauthtries|pubkeyauthentication) '
kill -HUP "$(cat /srv/sshlab/sshd.pid)"
sleep 1
pc() { ip netns exec pc sudo -u learner "$@"; }
pc ssh -o PubkeyAuthentication=no -o BatchMode=yes deploy@10.0.0.80 true
pc ssh web1 'echo key login still works'
kill "$(cat /srv/sshlab/sshd.pid)"
userdel -r deploy 2>/dev/null
rm -r /srv/sshlab
ip -all netns delete""", note='One letter missing in PasswordAuthentication makes sshd refuse the whole file, which is why you test before you reload. sshd -T prints the settings sshd would really use, in lower case. A HUP signal makes sshd reread its file, which is what systemctl reload ssh does. With passwords off, the server offers only publickey, so a client without a key is turned away at once.', root=True, keep=True)}
{note('Password guessing robots try every server on the internet within hours of it going online, as the auth.log in chapter 2.2 showed. Keys only, no root login, a short AllowUsers list and a firewall (chapter 4.3) stop nearly all of it. fail2ban can block addresses that keep failing.', 'tip')}
{talk('On the server side, a few settings in s s h d config make a big difference. Once your key works, set PasswordAuthentication to no, so password guessing robots have nothing to guess. Set PermitRootLogin to no, so people log in as themselves and use sudo. AllowUsers limits s s h to the accounts that really need it. Put your changes in a small file in the s s h d config dot d folder, test them with s s h d dash t, which catches typos, and look at the effective values with s s h d dash capital T. Then reload the service, which keeps existing sessions open. Always keep one session open and test a new login before you log out, so a mistake never locks you out of a remote server.')}
''', kw=['sshd_config', 'sshd_config.d', 'PasswordAuthentication no', 'PermitRootLogin', 'prohibit-password', 'AllowUsers', 'AllowGroups', 'MaxAuthTries', 'sshd -t', 'sshd -T', 'systemctl reload ssh', 'SIGHUP', 'fail2ban', 'ssh hardening'])

K.lesson('practice', 'Practice: key login to the file server', f'''
<p>Set up key login from the practice server to the file server files.shop.lab (192.168.1.20), copy a file there, and switch off password logins on the practice server itself.</p>
{lab('SSH keys, aliases and a safer sshd', [
    ('Make an Ed25519 key pair at ~/.ssh/id_ed25519 with the comment learner@brainy and an empty passphrase.', 'ssh-keygen -t ed25519 -C "learner@brainy" -N "" -f ~/.ssh/id_ed25519', [{'exists': '~/.ssh/id_ed25519.pub'}]),
    ('Show the fingerprint of your public key.', 'ssh-keygen -lf ~/.ssh/id_ed25519.pub', [{'out': r'^256 SHA256:\S+ learner@brainy \(ED25519\)'}]),
    ('Write ~/.ssh/config with a Host fs whose HostName is files.shop.lab.', 'printf "Host fs\\n    HostName files.shop.lab\\n" > ~/.ssh/config', [{'has': ['~/.ssh/config', 'HostName files.shop.lab']}]),
    ('Install your public key on fs.', 'ssh-copy-id fs', [{'out': r'Number of key\(s\) added: 1'}]),
    ('Run hostname on fs.', 'ssh fs hostname', [{'out': '^files$'}]),
    ('Copy notes.txt from your home folder to your home folder on fs.', 'scp notes.txt fs:', [{'out': '100%'}]),
    ('List your home folder on fs.', 'ssh fs ls', [{'out': 'notes.txt'}]),
    ('In /etc/ssh/sshd_config, turn the line #PasswordAuthentication yes into PasswordAuthentication no.', "sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config", [{'has': ['/etc/ssh/sshd_config', '\nPasswordAuthentication no']}]),
    ('Test the sshd configuration.', 'sudo sshd -t', [{'cmd': r'sshd\s+-t'}, {'code': 0}]),
    ('Reload the ssh service.', 'sudo systemctl reload ssh', [{'cmd': r'reload\s+ssh'}, {'code': 0}])])}
{talk('Now set up key login yourself. Make an ed25519 key pair with a comment, and look at its fingerprint. Write a small config file with the alias f s for the file server. Install your public key there with ssh copy id, and log in with the key to run hostname. Copy the notes file with s c p and list your home folder on the server to see it arrived. Finally, harden the practice server itself: switch password logins off in s s h d config, test the file with s s h d dash t, and reload the service.')}
''', kw=['ssh lab', 'ssh-keygen practice', 'ssh-copy-id practice', 'scp practice', 'sshd hardening practice'])

K.lesson('levels', 'Remote access from school to research', f'''
{ladder(
    '<p>ssh lets you use another computer’s command line safely over the network. A key pair is like a lock and a key: the public half goes on the server, the private half stays with you.</p>',
    '<p>Use Ed25519 keys with passphrases and ssh-agent, one key per device, aliases in ~/.ssh/config, rsync over ssh for copies, tunnels for private services, and sshd with keys only, no root login and an AllowUsers list. Check host key fingerprints on the first visit.</p>',
    '<p>Teams use SSH certificates (ssh-keygen -s with a certificate authority) so servers trust one CA instead of many authorized_keys files, short-lived certificates from tools such as HashiCorp Vault or step-ca, hardware keys (FIDO2, ed25519-sk), bastion hosts with session recording, and configuration management (Ansible works over ssh) to keep hundreds of servers in step.</p>',
    '<p>Research looks at post-quantum key exchange (OpenSSH made sntrup761x25519 the default in 9.0 and added ML-KEM later), formal analysis of the SSH protocol, and attacks such as Terrapin (2023), which tampered with the handshake sequence numbers and led to the strict key exchange extension. Internet-wide scans study weak and shared host keys.</p>')}
{scene('the laptop that was stolen', '<p>A developer’s laptop was stolen from a car. Because the team used one key per device with a passphrase, the admin removed just that public key from authorized_keys on all servers with a short Ansible run, and nobody else had to change anything. A team that had copied one shared private key to everyone would have had to replace it everywhere at once. The team later moved to short-lived SSH certificates, which expire by themselves after a day.</p>')}
{talk('Here is how remote access grows with experience. At school you learn that s s h opens a safe command line on another computer, and that a key pair works like a lock and key. Professionals use modern keys with passphrases, one per device, aliases, rsync and tunnels, and servers that accept keys only. Teams with many servers use S S H certificates signed by their own authority, short lived certificates, hardware security keys and bastion hosts. Researchers make the protocol ready for quantum computers and analyse it for flaws, such as the Terrapin attack, which led to a stricter handshake.')}
''', kw=['SSH certificates', 'certificate authority', 'ssh-keygen -s', 'short-lived certificates', 'FIDO2', 'ed25519-sk', 'bastion', 'session recording', 'Ansible', 'post-quantum ssh', 'ML-KEM', 'Terrapin attack', 'strict key exchange'])

K.quiz('e', 'Which port does sshd listen on by default?', ['21', '22', '23', '443'], 1, 'Two twos.', '22.')
K.quiz('e', 'Which half of a key pair may you give to a server?', ['The private key', 'The public key (.pub)', 'Both', 'Neither'], 1, 'Public.', 'The private key never leaves your machine.')
K.quiz('e', 'Which command makes a new key pair?', ['ssh-add', 'ssh-keygen', 'ssh-copy-id', 'sshd'], 1, 'Key generator.', 'ssh-keygen -t ed25519.')
K.quiz('e', 'Which command copies a file to a server over ssh?', ['cp', 'scp', 'mv', 'ftp'], 1, 'Secure copy.', 'scp file host:path.')
K.quiz('m', 'Where does the server look for public keys that may log in as deploy?', ['/etc/ssh/keys', '/home/deploy/.ssh/authorized_keys', '/home/deploy/.ssh/known_hosts', '/etc/passwd'], 1, 'Authorized.', 'One key per line.')
K.quiz('m', 'What does ~/.ssh/known_hosts protect you from?', ['Viruses', 'Connecting to a server that pretends to be the one you know', 'Lost passwords', 'Slow networks'], 1, 'Host keys.', 'A changed key stops the login.')
K.quiz('m', 'What mode should a private key file have?', ['644', '600', '755', '777'], 1, 'Owner only.', 'ssh ignores keys others can read.')
K.quiz('m', 'Which command checks sshd_config for errors?', ['sshd -t', 'ssh -t', 'systemctl check ssh', 'sshd --lint'], 0, 'Test.', 'sshd -T prints the effective settings.')
K.quiz('m', 'What does ssh-agent do?', ['Logs every login', 'Holds unlocked keys so you type the passphrase once per session', 'Scans for open ports', 'Copies keys to servers'], 1, 'Agent.', 'Load keys with ssh-add.')
K.quiz('h', 'A service listens only on 127.0.0.1:5432 of a server. How can you reach it from your laptop?', ['It is impossible', 'ssh -L 5432:127.0.0.1:5432 server', 'scp', 'ssh -D 5432'], 1, 'Local forward.', 'Then connect to 127.0.0.1:5432 on the laptop.')
K.quiz('h', 'ssh shows REMOTE HOST IDENTIFICATION HAS CHANGED. What should you do first?', ['Delete known_hosts', 'Check the new fingerprint with the server’s admin before removing the old line', 'Use -o StrictHostKeyChecking=no', 'Reinstall ssh'], 1, 'Verify.', 'Only then ssh-keygen -R host.')
K.quiz('h', 'Why put sshd changes in /etc/ssh/sshd_config.d/ instead of editing the main file?', ['It is faster', 'Package updates keep your file, and the include sits near the top so it wins', 'sshd reads only that folder', 'It disables the main file'], 1, 'First value wins.', 'Updates may replace the main file.')
K.quiz('h', 'Why is ProxyJump safer than copying your key to the bastion?', ['It is faster', 'The private key stays on your laptop', 'It disables passwords', 'It hides your IP'], 1, 'Key stays home.', 'The second connection is tunnelled through the first.')
K.quiz('x', 'Why do teams with many servers move to SSH certificates?', ['They are shorter', 'Servers trust one CA, and certificates can expire by themselves', 'They need no private key', 'They work without sshd'], 1, 'One trust anchor.', 'No authorized_keys sprawl.')

K.calc('e', 'An Ed25519 public key is 256 bits. How many bytes is that?', '32', 'Divide by 8.', ['8 bits are 1 byte.', '256 ÷ 8.', eq('32 bytes')], check=32)
K.calc('e', 'MaxAuthTries is 3. A robot opens 40 connections. How many password guesses can it make at most?', '120', 'Tries per connection.', ['3 guesses per connection.', '40 connections.', eq('3 × 40 = 120')], check=120)
K.calc('m', 'A team of 12 people with 2 devices each uses one key per device. How many public keys does each server need?', '24', 'Keys per person.', ['Each device has its own key.', '12 × 2.', eq('24 keys')], check=24)
K.calc('m', 'An SHA256 fingerprint has 256 bits. In base64, each character holds 6 bits. How many characters does it need, rounded up?', '43', 'Divide and round up.', ['256 ÷ 6 = 42.67.', 'Round up.', eq('43 characters')], check=43)
K.calc('h', 'rsync sends only changed files. A site has 2000 files of 50 KB, and 30 changed. How many KB does the second run send, ignoring overhead?', '1500', 'Only the changed ones.', ['30 files changed.', '30 × 50 KB.', eq('1500 KB')], check=1500)
K.calc('h', 'scp copies 2 GB at 40 MB/s. About how many seconds does it take (1 GB = 1000 MB)?', '50', 'Size over speed.', ['2000 MB.', '2000 ÷ 40.', eq('50 s')], check=50)
K.calc('x', 'A brute force robot tries 10 passwords per second, all day. How many guesses is that in one day?', '864000', 'Seconds in a day.', ['A day has 86400 seconds.', '× 10.', eq('864000 guesses')], check=864000)

K.must('The login', 'Key exchange, then the host key checked against known_hosts, then user authentication with a key from authorized_keys, then the session. A changed host key stops the login.')
K.must('Keys', 'ssh-keygen -t ed25519 -C, a passphrase, ssh-agent and ssh-add. Private key 600, ~/.ssh 700, authorized_keys 600. One key per device.')
K.must('Daily use', 'ssh-copy-id HOST, ssh HOST CMD, aliases in ~/.ssh/config, scp, sftp and rsync over ssh, ssh -v for debugging.')
K.must('Tunnels', '-L local:host:port, -R, -D, -N -f, ProxyJump (-J) through a bastion.')
K.must('sshd', 'PasswordAuthentication no, PermitRootLogin no, AllowUsers, a file in sshd_config.d, sshd -t and -T, systemctl reload ssh, keep a session open.')

T = K.topic(
    slug='ssh', topic='ssh',
    step=(4, 'Networking and security', 'lx-admin-4', 'Configure and troubleshoot networks, log in and copy files securely with SSH, and protect a server with a firewall and sensible hardening.', 'Advanced'),
    title='SSH: keys, remote work, tunnels and a safe sshd', short='SSH', badge='4.2', minutes=60, added='2026-11-23',
    lead='Log in to other machines with ssh and key pairs, understand host keys and known_hosts, copy files with scp and rsync, reach private services through tunnels and jump hosts, and set up sshd so that password guessing gets nowhere.',
    desc='How ssh works, host keys and known_hosts, ssh-keygen with Ed25519, passphrases and ssh-agent, ssh-copy-id and authorized_keys, file modes, ~/.ssh/config aliases, scp, sftp and rsync over ssh, local and remote port forwarding, ProxyJump, sshd_config hardening with sshd -t and -T, all run for real with OpenSSH 9.6 in network namespaces.',
    summary='Key pairs, known hosts, logging in, copying files, tunnels, hardening sshd.',
    keywords=['ssh', 'sshd', 'ssh-keygen', 'ssh-copy-id', 'authorized_keys', 'known_hosts', 'ssh-agent', 'scp', 'sftp', 'rsync', 'ssh tunnel', 'ProxyJump', 'sshd_config'],
    recap='<p>ssh encrypts the connection, checks the server’s host key against known_hosts and logs you in with a key whose public half sits in authorized_keys. ~/.ssh/config holds aliases, scp and rsync copy files, -L and ProxyJump reach private machines, and sshd with keys only, no root login and a tested config keeps robots out.</p>')
