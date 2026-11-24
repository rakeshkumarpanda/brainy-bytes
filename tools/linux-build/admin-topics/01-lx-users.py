# System administration 1.1: users, groups and sudo. /etc/passwd, /etc/shadow, /etc/group and their fields, UID
# ranges from /etc/login.defs, useradd, adduser, usermod -aG, groupadd, passwd, chpasswd, chage, userdel, getent,
# id, sudo, su, sudo -i, sudo -u, sudo -l, visudo, /etc/sudoers.d, secure_path and the auth log. Sources: passwd(5),
# shadow(5), group(5), login.defs(5), useradd(8), usermod(8), userdel(8), groupadd(8), passwd(1), chage(1),
# chpasswd(8), getent(1), sudo(8), sudoers(5), visudo(8), su(1), the Debian adduser(8) manual.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('accounts', 'Accounts: users, groups and the files behind them', f'''
<p>Linux knows people and services as numbers. A <b>UID</b> names a user and a <b>GID</b> names a group, and three plain text files map the numbers to names and settings.</p>
{table(['File', 'Holds', 'Who can read it'], [
    ['<code>/etc/passwd</code>', 'one line per account: name, UID, primary GID, comment, home folder, shell', 'everyone (mode 644)'],
    ['<code>/etc/shadow</code>', 'the password hashes and the password ageing dates', 'root and the shadow group only (mode 640)'],
    ['<code>/etc/group</code>', 'one line per group: name, GID, extra members', 'everyone (mode 644)'],
    ['<code>/etc/login.defs</code>', 'defaults for new accounts, such as UID_MIN and PASS_MAX_DAYS', 'everyone']])}
{table(['UID range on Debian and Ubuntu', 'Used for'], [
    ['0', 'root, the superuser. The kernel gives UID 0 every permission'],
    ['1 to 999', 'system accounts for services, such as www-data (33) for web servers'],
    ['1000 to 60000', 'people (UID_MIN and UID_MAX in /etc/login.defs)'],
    ['65534', 'nobody, an account that owns nothing']])}
{play('lx-account')}
{run('The account files on a real system', """getent passwd root learner
id learner
id -nG learner
ls -l /etc/passwd /etc/shadow /etc/group
cat /etc/shadow
grep -E '^(UID_MIN|UID_MAX|PASS_MAX_DAYS|ENCRYPT_METHOD)' /etc/login.defs""", note='getent reads the account databases, which are the files here but can also come from a network directory such as LDAP. id -nG lists the group names, and learner is in the sudo group, so learner may use sudo. /etc/shadow refused to open for a normal user, which protects the password hashes from guessing attacks.')}
{talk('Linux does not really think in names. Every user has a number called a U I D, and every group has a number called a G I D. Three text files connect the numbers to names. Slash etc slash passwd has one line per account with seven fields separated by colons: the name, an x, the U I D, the main group, a comment with the full name, the home folder and the login shell. Despite its name it holds no passwords any more. The password hashes moved to slash etc slash shadow, which only root can read. Slash etc slash group lists groups and their extra members. U I D zero is root. Numbers below one thousand belong to services, and people start at one thousand. Use the animation to read each field of real lines, and notice that the getent command reads these databases for you.')}
''', kw=['/etc/passwd', '/etc/shadow', '/etc/group', 'UID', 'GID', 'UID 0 root', 'system account', 'login.defs', 'getent passwd', 'id command', 'password hash', 'passwd fields'])

K.lesson('manage', 'Creating, changing and removing accounts', f'''
{cmdtable([
    ('useradd -m -s /bin/bash -c "Full Name" NAME', 'Create a user with a home folder (-m), a shell and a comment. Without -s, Debian and Ubuntu give /bin/sh', 'sudo useradd -m -s /bin/bash dev1'),
    ('adduser NAME', 'Debian and Ubuntu: a friendly script that asks questions, creates the home folder and sets a password', 'sudo adduser dev1'),
    ('passwd NAME', 'Set or change a password. Without a name it changes your own', 'sudo passwd dev1'),
    ('usermod -aG GROUP NAME', 'Add the user to an extra group. The change applies from the next login', 'sudo usermod -aG docker dev1'),
    ('usermod -L NAME, usermod -U NAME', 'Lock and unlock the password', 'sudo usermod -L dev1'),
    ('chage -M DAYS NAME, chage -l NAME', 'Set the maximum password age, list the ageing settings', 'sudo chage -M 90 dev1'),
    ('groupadd NAME, groupdel NAME', 'Create or delete a group', 'sudo groupadd web'),
    ('userdel -r NAME', 'Delete the user, with -r also the home folder and mail', 'sudo userdel -r dev1')])}
{note('<code>usermod -G web dev1</code> without -a replaces the whole list of extra groups, so dev1 silently leaves sudo, docker and every other group. Always write -aG.', 'warn')}
{run('The life of an account, run as root', """useradd -m -u 1002 -s /bin/bash -c "Dev One" dev1
getent passwd dev1
ls -la /home/dev1
groupadd -g 1003 web
usermod -aG web,sudo dev1
id dev1
passwd -S dev1
echo 'dev1:Garden.Tree.42' | chpasswd
passwd -S dev1
chage -M 90 dev1
chage -l dev1 | head -4
usermod -L dev1
passwd -S dev1
sudo -u dev1 bash -c 'whoami; cd; pwd'
userdel -r dev1
groupdel web
id dev1""", root=True, note='useradd -m copied the files of /etc/skel into the new home folder. passwd -S printed L (locked) until chpasswd set a password, then P, then L again after usermod -L. The fifth field of passwd -S is the maximum age, now 90 days. userdel -r removed the home folder and warned that dev1 had no mail spool.')}
{note('chpasswd reads name:password lines from standard input, which suits scripts. Never put a real password in a command line on a shared machine, because other users can see running commands with ps.')}
{talk('Creating an account is a job for root, so these commands run with sudo. Useradd dash m creates a user and a home folder, which is filled with starter files copied from slash etc slash skel. On Debian and Ubuntu, adduser is a friendlier helper that asks for the full name and a password. A new account from useradd starts with a locked password, shown as L by passwd dash capital S, until you set one with passwd or chpasswd. To add someone to an extra group, use usermod dash a capital G. Never forget the a, which means append. Without it the user is removed from every group that is not in your list. Chage controls password ageing, for example a maximum age of ninety days. And userdel dash r deletes the account together with its home folder, so copy any data you need first.')}
''', kw=['useradd', 'useradd -m', 'adduser', 'usermod -aG', 'add user to group', 'groupadd', 'passwd', 'chpasswd', 'chage', 'password ageing', 'userdel -r', 'lock account', '/etc/skel'])

K.lesson('sudo', 'sudo, su and the sudoers file', f'''
{table(['Command', 'What happens', 'Password asked'], [
    ['<code>sudo CMD</code>', 'run one command as root, and log it', 'your own password, then remembered for 15 minutes by default'],
    ['<code>sudo -u NAME CMD</code>', 'run one command as another user', 'your own'],
    ['<code>sudo -i</code>', 'a full root login shell, until you type exit', 'your own'],
    ['<code>sudo -l</code>', 'list what you are allowed to run', 'your own'],
    ['<code>su - NAME</code>', 'become another user with a login shell', 'the password of that user'],
    ['<code>sudo visudo</code>', 'edit /etc/sudoers safely, with a syntax check', 'your own']])}
{shape('A sudoers rule', """who      hosts = (run as users:groups)  tags       commands
%sudo    ALL   = (ALL:ALL)                         ALL
dev1     ALL   = (root)               NOPASSWD:    /usr/bin/systemctl restart nginx""", note='A % in front of the name means a group. Put your own rules in a small file in /etc/sudoers.d and create it with sudo visudo -f /etc/sudoers.d/NAME.')}
{run('Reading and checking sudo rules, run as root', """grep -E '^(Defaults|root|%sudo|@includedir)' /etc/sudoers
sudo -l -U learner
printf 'learner ALL=(root) NOPASSWD: /usr/bin/systemctl restart nginx\\n' > /tmp/web-restart
visudo -cf /tmp/web-restart
printf 'learner ALL=(root) NOPASSWD /usr/bin/systemctl\\n' > /tmp/broken
visudo -cf /tmp/broken
rm /tmp/web-restart /tmp/broken""", root=True, note='The %sudo rule is why members of the sudo group may run any command. secure_path is the PATH sudo uses, which includes the sbin folders where admin tools live. visudo -c checked one good file and found the missing colon after NOPASSWD in the other, pointing at the column.')}
{note('A sudoers file with a syntax error can stop sudo from working for everyone. Never edit it with a plain editor. visudo refuses to save a broken file.', 'warn')}
{cmdtable([
    ('/var/log/auth.log (Debian, Ubuntu), /var/log/secure (RHEL)', 'Every sudo use, login and failed password', 'sudo grep sudo /var/log/auth.log | tail'),
    ('journalctl _COMM=sudo', 'The same entries from the systemd journal', 'journalctl _COMM=sudo --since today'),
    ('who, w', 'Who is logged in now, and what they run', 'w'),
    ('last, lastb', 'Past logins, and failed ones (lastb needs root)', 'last -n 5')])}
{talk('Logging in as root for daily work is risky, because one typo can damage the whole system. Instead, normal users run single commands as root with sudo. Sudo asks for your own password, not root’s, remembers it for a few minutes, and writes every use to the log, so you always know who did what. Sudo dash i gives a root shell when you need several commands, and sudo dash u runs a command as another user, such as a database account. Who may do what is written in slash etc slash sudoers. A rule says who, on which hosts, as which user, and which commands. A percent sign means a group, which is why everyone in the sudo group may run anything. Never edit this file with a normal editor. Use visudo, which checks the syntax first, and keep your own rules in small files inside slash etc slash sudoers dot d. You can give a narrow right, such as restarting one service, without handing out full root power.')}
''', kw=['sudo', 'sudo -i', 'sudo -u', 'sudo -l', 'su', 'su -', 'sudoers', 'visudo', 'sudoers.d', 'NOPASSWD', '%sudo group', 'secure_path', 'auth.log', 'least privilege'])

K.lesson('practice', 'Practice: manage an account in the practice shell', f'''
<p>The practice shell keeps its own /etc/passwd, /etc/group and /etc/shadow, and its useradd, usermod and userdel change them the way the real tools do. Commands in /usr/sbin are found only through sudo, as on Debian.</p>
{lab('Create, change and remove an account', [
    ('Create the user dev1 with a home folder and bash as the login shell.', 'sudo useradd -m -s /bin/bash dev1', [{'exists': '/home/dev1', 'type': 'd'}, {'has': ['/etc/passwd', 'dev1:x:1002:1002::/home/dev1:/bin/bash']}]),
    ('Print the passwd line of dev1 with getent.', 'getent passwd dev1', [{'out': '^dev1:x:1002:'}]),
    ('Create a group called web.', 'sudo groupadd web', [{'has': ['/etc/group', 'web:x:']}]),
    ('Add dev1 to the group web, keeping its other groups.', 'sudo usermod -aG web dev1', [{'has': ['/etc/group', 'web:x:1003:dev1']}]),
    ('Give dev1 a password with chpasswd.', 'echo "dev1:Garden.Tree.42" | sudo chpasswd', [{'cmd': 'chpasswd'}, {'has': ['/etc/shadow', 'dev1:$y$']}]),
    ('Show the password status of dev1.', 'sudo passwd -S dev1', [{'out': '^dev1 P '}]),
    ('Lock the password of dev1.', 'sudo usermod -L dev1', [{'has': ['/etc/shadow', 'dev1:!$y$']}]),
    ('List the groups of dev1.', 'groups dev1', [{'out': '^dev1 : dev1 web$'}]),
    ('Delete dev1 together with its home folder.', 'sudo userdel -r dev1', [{'gone': '/home/dev1'}])])}
{talk('Time to practise. The practice shell has its own account files, and its useradd, usermod and userdel change them just like the real tools. Create a user called dev one with a home folder, look at its line with getent, make a group called web and add dev one to it with usermod dash a capital G. Then give it a password with chpasswd, check the status, lock it, and finally remove the account and its home folder with userdel dash r. Look at slash etc slash group between the steps to see the files change.')}
''', kw=['useradd practice', 'usermod practice', 'account lab', 'chpasswd practice', 'userdel practice'])

K.lesson('levels', 'Accounts and privilege from school to research', f'''
{ladder(
    '<p>Each person has their own account and password. Only administrators may use sudo, and they use it for one command at a time. Accounts for people who left are locked or deleted.</p>',
    '<p>Give rights through groups, not through individual sudo rules, and keep each sudoers.d rule as narrow as possible, with full paths. Avoid NOPASSWD for broad commands. A rule such as <code>(root) /usr/bin/vim</code> gives full root, because vim can start a shell. Service accounts use /usr/sbin/nologin and no password. Expire contractor accounts with <code>chage -E</code>.</p>',
    '<p>The Name Service Switch (/etc/nsswitch.conf) lets getent and every program read accounts from files, LDAP or SSSD, so large sites manage users centrally. PAM (Pluggable Authentication Modules, /etc/pam.d) decides how a login is checked, with password rules, lockouts after failed tries, and two-factor modules. sudo can log full session input and output, and its rules can live in LDAP.</p>',
    '<p>Password hashing has moved from MD5 crypt to SHA-512 crypt to yescrypt, a memory-hard function, because GPUs made fast hashes cheap to attack. Research on privilege separation, such as the OpenSSH design that splits a small privileged monitor from an unprivileged worker, and on Linux capabilities, which divide root’s power into pieces like CAP_NET_BIND_SERVICE, aims to make UID 0 matter less.</p>')}
{scene('the intern with root', '<p>A startup gave every developer <code>ALL=(ALL) NOPASSWD: ALL</code> for convenience. A leaked laptop key let an attacker log in as one developer and become root at once. The fix moved rights into groups, replaced the blanket rule with narrow files such as <code>%deploy ALL=(root) /usr/bin/systemctl restart app</code>, turned on passwords for sudo, and sent auth.log to a central log server, where a failed sudo now raises an alert.</p>')}
{talk('Here is the bigger picture. Good practice is to give rights to groups rather than to single people, and to keep every sudo rule as narrow as possible. Be careful, because some programs can escape to a shell, so allowing an editor or a pager through sudo can hand out full root power. Service accounts get the nologin shell and no password. In larger organisations accounts come from a central directory such as LDAP, which the name service switch makes look just like the local files, and PAM modules decide how logins are checked, including lockouts and two factor codes. Password hashes have moved to slow, memory hard functions such as yescrypt, because graphics cards can test billions of fast hashes per second. And the long term research goal is to make root less special, by splitting its power into smaller capabilities and by separating programs into privileged and unprivileged parts.')}
''', kw=['least privilege', 'sudo shell escape', 'nologin', 'chage -E', 'nsswitch.conf', 'LDAP', 'SSSD', 'PAM', 'yescrypt', 'Linux capabilities', 'privilege separation'])

K.quiz('e', 'Which file lists the accounts and is readable by everyone?', ['/etc/shadow', '/etc/passwd', '/etc/sudoers', '/etc/users'], 1, 'Despite the name.', '/etc/passwd has no hashes any more.')
K.quiz('e', 'Which UID does root have?', ['1', '0', '1000', '65534'], 1, 'The first number.', 'UID 0 is root.')
K.quiz('e', 'Which command runs one command as root?', ['su', 'sudo', 'root', 'admin'], 1, 'Superuser do.', 'sudo CMD.')
K.quiz('e', 'Where are the password hashes kept?', ['/etc/passwd', '/etc/shadow', '/etc/group', '/home'], 1, 'Hidden.', 'Only root can read /etc/shadow.')
K.quiz('m', 'Which command adds dev1 to docker without removing other groups?', ['usermod -G docker dev1', 'usermod -aG docker dev1', 'groupadd docker dev1', 'useradd -G docker dev1'], 1, 'Append.', '-a keeps the existing groups.')
K.quiz('m', 'What does an x in the second field of /etc/passwd mean?', ['No password', 'The hash is in /etc/shadow', 'The account is locked', 'Root only'], 1, 'Look elsewhere.', 'x points to /etc/shadow.')
K.quiz('m', 'Which password does sudo ask for by default?', ['The root password', 'Your own password', 'No password', 'The group password'], 1, 'Yours.', 'sudo checks your own password.')
K.quiz('m', 'How should you edit /etc/sudoers?', ['nano /etc/sudoers', 'sudo visudo', 'echo >> /etc/sudoers', 'chmod 777 first'], 1, 'Checked editing.', 'visudo checks the syntax before saving.')
K.quiz('m', 'passwd -S prints <code>dev1 L ...</code>. What does L mean?', ['Logged in', 'Locked password', 'Local account', 'Long password'], 1, 'Locked.', 'L is locked, P has a password, NP none.')
K.quiz('m', 'What does a % in front of a name in sudoers mean?', ['A comment', 'A group', 'A percentage', 'A host'], 1, 'Many users.', '%sudo means the group sudo.')
K.quiz('h', 'Why is <code>dev1 ALL=(root) /usr/bin/vim</code> dangerous?', ['vim is slow', 'vim can start a shell, which then runs as root', 'vim cannot read files', 'It is not dangerous'], 1, 'Escapes.', ':!bash inside vim gives a root shell.')
K.quiz('h', 'Which shell stops anyone logging in to a service account?', ['/bin/bash', '/usr/sbin/nologin', '/bin/sh', '/etc/shells'], 1, 'No login.', 'nologin prints a message and exits.')
K.quiz('h', 'A user was added to a group, but id in their open terminal does not show it. Why?', ['usermod failed', 'Group lists are read at login, so they must log in again', 'Groups need a reboot', 'id is cached for a day'], 1, 'Next login.', 'Log out and in, or run newgrp.')
K.quiz('x', 'Which file decides whether getent reads accounts from files or LDAP?', ['/etc/pam.d/common-auth', '/etc/nsswitch.conf', '/etc/login.defs', '/etc/sudoers'], 1, 'Name service.', 'nsswitch.conf lists the sources.')

K.calc('e', 'How many colon-separated fields does a line of /etc/passwd have?', '7', 'Count them.', ['name, password, UID, GID', 'comment, home, shell', eq('4 + 3 = 7')], check=7)
K.calc('e', 'Debian gives people UIDs from 1000. Accounts 1000, 1001 and 1002 exist. Which UID does useradd pick next?', '1003', 'One more than the highest.', ['The highest UID in the range is 1002.', 'useradd takes the next free number.', eq('1002 + 1 = 1003')], check=1003)
K.calc('m', 'A password was last changed on shadow day 20780, with a maximum age of 90. On which shadow day does it expire?', '20870', 'Add the days.', ['Expiry is last change plus maximum age.', '20780 + 90.', eq('20870')], check=20870)
K.calc('m', 'sudo remembers your password for 15 minutes by default. You ran sudo at 10:00 and again at 10:09. Until what minute past 10 is it remembered now?', '24', 'Each use restarts the timer.', ['The timer restarts at 10:09.', '9 + 15.', eq('10:24')], check=24)
K.calc('h', '/etc/shadow has mode 640, owner root, group shadow. How many of the classes owner, group and others may read it?', '2', '6 and 4 can read.', ['Owner 6 is rw, group 4 is r.', 'Others 0 is nothing.', eq('2 classes')], check=2)
K.calc('h', 'A shadow line has 9 fields and a passwd line 7. How many fields do the two lines of one account have together?', '16', 'Add them.', ['passwd has 7.', 'shadow has 9.', eq('7 + 9 = 16')], check=16)

K.must('Account files', '/etc/passwd (7 fields, readable), /etc/shadow (hashes and ageing, root only), /etc/group. getent reads them.')
K.must('UIDs', '0 is root, 1 to 999 system accounts, 1000 and up people. The kernel checks numbers, not names.')
K.must('Managing users', 'useradd -m -s /bin/bash, passwd or chpasswd, usermod -aG (never -G alone), chage, userdel -r.')
K.must('sudo', 'sudo CMD, sudo -i, sudo -u NAME, sudo -l. Edit rules only with visudo, keep them narrow in /etc/sudoers.d.')
K.must('Logs', 'sudo and logins go to /var/log/auth.log on Debian and Ubuntu, /var/log/secure on RHEL, and to the journal.')

T = K.topic(
    slug='users-sudo', topic='users-sudo',
    step=(1, 'Users and software', 'lx-admin-1', 'Manage accounts, groups and sudo rights, and install, update and remove software with package managers.', 'Intermediate'),
    title='Users, groups and sudo', short='Users and sudo', badge='1.1', minutes=50, added='2026-11-23',
    lead='Read the account files field by field, create, change and remove users and groups, set and lock passwords, and give exactly the right amount of root power with sudo and visudo.',
    desc='/etc/passwd, /etc/shadow and /etc/group with every field, UID ranges and /etc/login.defs, getent and id, useradd, adduser, usermod -aG, groupadd, passwd, chpasswd, chage and userdel, sudo, sudo -i, sudo -u, sudo -l and su, sudoers rules, visudo and /etc/sudoers.d, secure_path, and the auth log.',
    summary='Account files, managing users and groups, passwords and ageing, sudo and sudoers.',
    keywords=['useradd', 'usermod', 'userdel', 'groupadd', 'passwd', 'shadow', 'sudo', 'sudoers', 'visudo', 'getent', 'UID', 'GID'],
    recap='<p>Accounts live in /etc/passwd, /etc/shadow and /etc/group, and the kernel only sees UIDs and GIDs. useradd, usermod -aG, passwd, chage and userdel manage them as root. sudo runs single commands as root, with narrow rules written through visudo and every use logged.</p>')
