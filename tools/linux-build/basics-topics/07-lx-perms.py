# Foundations 3.1: users, groups and permissions. rwx on files and folders, ls -l mode string, octal and symbolic
# chmod, chown and chgrp, umask, setuid, setgid and the sticky bit, how the kernel decides. Sources: GNU coreutils
# manual (chmod, chown, chgrp, stat, File permissions chapter), chmod(1), umask(2), path_resolution(7),
# capabilities(7) (CAP_DAC_OVERRIDE), inode(7) (S_ISUID, S_ISGID, S_ISVTX), acl(5), US patent 4,135,240 (setuid).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('who', 'Users, groups and the ls -l mode string', f'''
<p>Linux was built for many people sharing one computer, so every file has an <b>owner</b> (a user) and a <b>group</b>. Every person who is not the owner and not in the group counts as <b>others</b>. For each of these three classes the file stores three switches: <b>r</b> read, <b>w</b> write, <b>x</b> execute.</p>
{fxs(fx('-rw-r--r--', 'the mode string', 'First character is the type (- file, d folder, l link). Then three groups of three: owner, group, others.', key=True),
     fx('r = 4, w = 2, x = 1', 'the numbers', 'Add the switches of one class to get one digit. rw- is 4 + 2 = 6.'),
     fx('644', 'the same mode in numbers', 'Owner rw (6), group r (4), others r (4). The usual mode of a text file.', key=True))}
{run('Who am I, and who owns what', """id
ls -l notes.txt scripts/hello.sh
ls -ld logs
ls -l /etc/passwd /etc/shadow /usr/bin/passwd""", note='learner owns its files, and /etc/shadow, which holds the password hashes, can be read only by root and the shadow group. The s in /usr/bin/passwd is the setuid bit, explained later in this chapter.')}
{table(['Letter', 'On a file', 'On a folder'], [
    ['r', 'Read the content (cat, less, cp from it)', 'List the names inside (ls)'],
    ['w', 'Change the content', 'Create, delete and rename entries inside (needs x too)'],
    ['x', 'Run it as a program', 'Enter it (cd) and reach anything inside by name']])}
{note('Deleting a file is a change to the folder, not to the file. So whether you may delete notes.txt depends on the w and x of its folder, not on the mode of notes.txt.', 'tip')}
{talk('Linux comes from Unix, and Unix was designed in the nineteen seventies for many people sharing one big computer at a university or company. So from day one, every file needed an answer to the question who may do what with this. The answer is small and clever. Each file has one owner and one group, and everybody else is called others. For each of those three, there are three switches: read, write and execute. When you run ls dash l, you see them as letters, for example r w dash, r dash dash, r dash dash. People also write the same thing as numbers, where read counts four, write counts two and execute counts one. Add them up and you get one digit per class, so the common text file mode is six four four. Once you can read these nine letters, a large part of Linux administration stops being mysterious.')}
''', kw=['owner', 'group', 'others', 'rwx', 'mode string', 'ls -l', 'id', 'octal permissions', '644', '755'])

K.lesson('decide', 'How the kernel decides', f'''
<p>When a program tries to open a file, the kernel checks only <b>one</b> class, chosen in this order:</p>
{steps('The permission check', [
    'If you are root, reading and writing are allowed. Executing a file still needs at least one x bit somewhere in its mode.',
    'If you are the owner of the file, only the owner bits count, even if the group or others bits would give you more.',
    'Otherwise, if you are a member of the file’s group, only the group bits count.',
    'Otherwise the others bits count.',
    'To reach the file at all, you also need x on every folder in its path, from / down.'])}
{play('lx-access')}
{note('Because only one class is checked, a file with mode 604 (rw- --- r--) can be read by strangers but not by members of its group. Unusual, but legal.', 'tip')}
{run('Folders need x to enter', """mkdir vault
echo secret > vault/key.txt
chmod 600 vault
ls vault
cat vault/key.txt
cd vault
chmod 700 vault
cat vault/key.txt""", note='With r but no x, ls can read the names in the folder, but nothing inside can be opened and cd is refused. Putting x back fixes both.')}
{talk('Here is the rule the kernel follows every time a program opens a file. First, is this the root user. Root may read and write anything. Second, is this person the owner of the file. If yes, the kernel looks at the owner switches and stops there. Third, is this person a member of the file group. If yes, it looks at the group switches and stops. Otherwise it uses the switches for others. Only one class is ever checked, so the owner cannot borrow rights from the group. There is one more condition that surprises people. To open a file, you need the execute switch on every folder on the way to it. On a folder, execute really means may pass through. That is how a home folder with mode seven five zero keeps other people out, even if a file inside is readable by everyone.')}
''', kw=['permission check', 'root', 'CAP_DAC_OVERRIDE', 'search permission', 'folder x bit', 'path resolution', 'Permission denied'])

K.lesson('chmod', 'Changing permissions: chmod, chown, chgrp', f'''
{cmdtable([
    ('chmod 755 FILE', 'Set the whole mode with numbers', 'chmod 755 deploy.sh'),
    ('chmod u+x FILE', 'Add execute for the owner (u user, g group, o others, a all)', 'chmod u+x hello.sh'),
    ('chmod go-w FILE', 'Remove write from group and others', 'chmod go-w report.txt'),
    ('chmod u=rw,go= FILE', 'Set exactly, = with nothing after it removes everything', 'chmod u=rw,go= key.pem'),
    ('chmod -R g+rX DIR', 'Recursive. Capital X adds x only to folders and files that already have some x', 'chmod -R g+rX shared'),
    ('chown USER FILE', 'Change the owner (root only)', 'sudo chown asha report.txt'),
    ('chown USER:GROUP FILE', 'Change owner and group together', 'sudo chown www-data:www-data site'),
    ('chgrp GROUP FILE', 'Change the group, to one you belong to', 'chgrp sudo notes.txt')])}
{play('lx-chmod')}
{run('Making a script runnable', """ls -l scripts/hello.sh
./scripts/hello.sh
chmod u+x scripts/hello.sh
ls -l scripts/hello.sh
./scripts/hello.sh Asha
chmod 600 notes.txt
chmod go-rx logs
ls -l notes.txt
ls -ld logs""", note='Permission denied until the owner gets x. After chmod the file shows rwx and runs.')}
{run('Owners change only with root', """touch report.txt
chown root report.txt
chgrp sudo report.txt
ls -l report.txt""", note='A normal user may not give a file away, so chown fails. chgrp works because learner is a member of the group sudo and owns the file.')}
{run('As root', """touch /home/learner/report.txt
chown root:root /home/learner/report.txt
ls -l /home/learner/report.txt
stat -c '%a %A %U:%G %n' /home/learner/report.txt""", root=True, keep=True, note='The prompt ends in # because this box runs as root. stat -c prints chosen fields: %a the mode in numbers, %A as letters, %U and %G the owner and group names.')}
{table(['Mode', 'Letters', 'Typical use'], [
    ['644', 'rw-r--r--', 'Ordinary files, web pages, configuration that is not secret'],
    ['600', 'rw-------', 'Secrets: SSH private keys, files with passwords'],
    ['755', 'rwxr-xr-x', 'Programs and scripts, ordinary folders'],
    ['700', 'rwx------', 'Private folders such as ~/.ssh'],
    ['750', 'rwxr-x---', 'Folders shared with one team'],
    ['777', 'rwxrwxrwx', 'Almost never right: anyone may change or replace it']])}
{note('chmod 777 to make an error go away is a classic mistake. It lets every user and every hacked service on the machine change the file. Find which user needs access and give only that.', 'warn')}
{talk('The command that changes permissions is chmod, short for change mode. You can use it in two ways. With numbers, you give the whole mode at once, such as seven five five for a script. With letters, you describe a change. u plus x means give the owner execute. g o minus w means take write away from group and others. The letter form is safer when you only want to change one thing, because it leaves the other bits alone. Ownership is changed with chown, and only root may give a file to someone else. Otherwise anybody could hand a huge file to a colleague and fill up their disk quota. A useful habit for secrets: SSH refuses to use a private key that other people can read, so key files should be six hundred. When something says permission denied, resist the temptation to type chmod seven seven seven. Work out which user needs which right, and give exactly that.')}
''', kw=['chmod', 'chmod numeric', 'chmod symbolic', 'u+x', 'go-w', 'chmod -R', 'capital X', 'chown', 'chgrp', '777', '600'])

K.lesson('special', 'umask and the special bits', f'''
<p>New files do not start with random permissions. The program asks for 666 for a file (rw for everyone) or 777 for a folder, and the kernel switches off every bit that is set in your <b>umask</b>. The common umask 022 switches off w for group and others, so files come out as 644 and folders as 755. Some distributions use 002 for normal users, which keeps group write.</p>
{fxs(fx('mode = request AND NOT umask', 'umask removes bits', '666 with umask 022 gives 644. 777 with umask 077 gives 700.', key=True),
     fx('4000 setuid', 'run as the file owner', '/usr/bin/passwd is rwsr-xr-x and owned by root, so it can write /etc/shadow for you.'),
     fx('2000 setgid', 'group of the file or folder', 'On a folder, new files inherit the folder’s group. Perfect for team folders.'),
     fx('1000 sticky', 'only owners delete', '/tmp is drwxrwxrwt: everyone may create files, but only the owner of a file may delete or rename it.'))}
{run('umask in action', """umask
touch a.txt
mkdir d1
umask 077
touch b.txt
mkdir d2
ls -ld a.txt d1 b.txt d2""", note='The umask change lasts only for this shell. Put umask 077 in ~/.bashrc to keep it.')}
{run('The special bits you meet every day', """ls -ld /tmp /usr/bin/passwd
mkdir team
chmod 2775 team
chmod +t team
ls -ld team
stat -c '%a %n' team /tmp""", note='In ls -l the special bits replace the x position: s for setuid or setgid, t for sticky. A capital S or T means the special bit is set but the x under it is not.')}
{note('Linux ignores setuid and setgid on scripts that start with #!. Only compiled programs can use them, because a script could be swapped or tricked between the moment the kernel reads it and the moment the interpreter does.', 'tip')}
{lab('Lock down and open up', [
    ('Make <code>scripts/hello.sh</code> executable for its owner.', 'chmod u+x scripts/hello.sh', [{'mode': ['scripts/hello.sh', '744']}]),
    ('Run it with the name Asha.', './scripts/hello.sh Asha', [{'out': 'Hello, Asha!'}]),
    ('Make <code>notes.txt</code> readable and writable only by you, with numbers.', 'chmod 600 notes.txt', [{'mode': ['notes.txt', '600']}]),
    ('Give <code>poem.txt</code> the mode rw-r----- using letters.', 'chmod u=rw,g=r,o= poem.txt', [{'cmd': r'^\s*chmod\s+[ugoa=+,rwx-]+\s+poem\.txt'}, {'mode': ['poem.txt', '640']}]),
    ('Set your umask to 077.', 'umask 077', [{'cmd': r'^\s*umask\s+0?077\s*$'}]),
    ('Make a folder <code>private</code> and check it is rwx------.', 'mkdir private', [{'mode': ['private', '700']}]),
    ('Make a folder <code>team</code> and give it mode 2770 (setgid plus rwx for owner and group).', 'mkdir team; chmod 2770 team', [{'mode': ['team', '2770']}]),
    ('Try to read <code>/home/asha/diary.txt</code> and see the kernel refuse.', 'cat /home/asha/diary.txt', [{'cmd': r'diary\.txt'}, {'out': 'Permission denied'}])])}
{talk('Two last pieces complete the picture. The first is umask. When a program creates a file, it usually asks for read and write for everyone, and the umask removes some of those bits. With the common umask of zero two two, write is removed for group and others, so new files come out as six four four. The second piece is three special bits. Setuid makes a program run with the rights of its owner. That is how the passwd program, owned by root, can update the protected password file for an ordinary user. Dennis Ritchie invented this idea, and Bell Labs received a patent for it in 1979, then placed it in the public domain. Setgid on a folder makes new files inherit the folder group, which keeps team folders tidy. The sticky bit on a shared folder like slash tmp lets everyone create files, but only the owner may delete them.')}
''', kw=['umask', '022', '077', 'setuid', 'setgid', 'sticky bit', '/tmp', 'passwd', 'S_ISUID', 'team folder', 'chmod 2775'])

K.lesson('levels', 'Permissions from school to research', f'''
{ladder(
    '<p>Every file has an owner, a group and others, and for each of them read, write and execute switches. chmod changes the switches, chown changes the owner, and root can do almost anything. Keep secrets at 600 and never use 777.</p>',
    '<p>Unix discretionary access control stores 12 mode bits in the inode: 9 rwx bits plus setuid, setgid and sticky. Access is checked against the effective user and group IDs of the process, using exactly one class. umask filters the mode requested in open() and mkdir(). Directory x is search permission.</p>',
    '<p>Modern Linux splits root into about 40 capabilities (capabilities(7)), so a web server can get only CAP_NET_BIND_SERVICE to use port 80. POSIX ACLs (getfacl, setfacl, shown as a + after the mode) give rights to extra users and groups. Mandatory access control in SELinux and AppArmor adds rules that even the owner cannot override, and setuid binaries are a classic source of privilege escalation bugs, so distributions keep their number small.</p>',
    '<p>Research compares discretionary, mandatory and role based models (Bell and LaPadula 1973 for secrecy, Biba 1977 for integrity), studies capability systems such as Capsicum in FreeBSD, and measures how often real systems are misconfigured. Container isolation builds on these ideas with user namespaces, where uid 0 inside a container maps to an unprivileged user outside, a topic in the advanced section.</p>')}
{scene('the leaked key', '<p>A developer copies a cloud SSH key to a shared server and gets <code>WARNING: UNPROTECTED PRIVATE KEY FILE!</code> followed by a refusal to use the key. ssh is right: the file was 644, readable by every user on the machine. <code>chmod 600 ~/.ssh/id_ed25519</code> fixes it, and <code>chmod 700 ~/.ssh</code> protects the folder.</p>')}
{talk('The nine switches you learned are the base of a much bigger security story. The full mode has twelve bits, including the three special ones, and they live inside the file inode. On modern Linux, the all powerful root user is actually split into about forty separate capabilities, so a web server can be given only the right to open port eighty and nothing else. When nine switches are not enough, access control lists let you give rights to extra people, and you can spot them by a plus sign after the mode in ls dash l. On top of that, security modules like SELinux on Red Hat systems and AppArmor on Ubuntu add rules that even a file owner cannot break. Researchers have studied these models since the nineteen seventies, and the same ideas now protect every container running in the cloud.')}
''', kw=['capabilities', 'ACL', 'getfacl', 'setfacl', 'SELinux', 'AppArmor', 'MAC', 'DAC', 'privilege escalation', 'Bell LaPadula'])

K.quiz('e', 'In -rwxr-xr--, what may "others" do?', ['Read, write and execute', 'Read and execute', 'Read only', 'Nothing'], 2, 'Last three letters.', 'The last group r-- belongs to others: read only.')
K.quiz('e', 'What number stands for rw-?', ['4', '5', '6', '7'], 2, 'r 4 plus w 2.', '4 + 2 = 6.')
K.quiz('e', 'Which command makes deploy.sh runnable by its owner?', ['chmod u+x deploy.sh', 'chown x deploy.sh', 'run deploy.sh', 'chmod 444 deploy.sh'], 0, 'u plus x.', 'chmod u+x adds execute for the owner.')
K.quiz('e', 'What is the mode 755 in letters?', ['rwxr-xr-x', 'rwxrwxrwx', 'rw-r--r--', 'rwx------'], 0, '7 5 5.', '7 rwx, 5 r-x, 5 r-x.')
K.quiz('m', 'Which mode should an SSH private key have?', ['644', '600', '755', '777'], 1, 'Only you.', '600 lets only the owner read and write it, and ssh refuses keys others can read.')
K.quiz('m', 'A folder has r but not x for you. What happens?', ['You can cd into it', 'You can list names, but cannot enter it or open files inside', 'You can delete it', 'Nothing changes'], 1, 'x is search.', 'r lists names, x is needed to pass through.')
K.quiz('m', 'You may delete a file you do not own if ...', ['The file is 666', 'You have w and x on its folder and the folder is not sticky', 'You are in its group', 'Never'], 1, 'Deleting changes the folder.', 'Removing a name needs write and search permission on the folder.')
K.quiz('m', 'With umask 027, what mode does a new file get?', ['640', '750', '644', '600'], 0, '666 minus bits 027.', '666 with 027 removed is 640.')
K.quiz('m', 'Why does /usr/bin/passwd have an s in its mode?', ['It is a script', 'setuid: it runs as its owner root, so it can update /etc/shadow', 'It is sticky', 'It is a link'], 1, 'Set user ID.', 'setuid makes the program run with the owner’s rights.')
K.quiz('h', 'A file is ---rwx--- owned by you and in your group. Can you read it?', ['Yes, through the group bits', 'No, as owner only the owner bits count', 'Yes, always', 'Only with sudo'], 1, 'Only one class is checked.', 'The owner class is chosen first and its bits are all off.')
K.quiz('h', 'What does chmod -R g+rX shared do?', ['Adds read and execute to everything', 'Adds read to everything and execute only to folders and files that already have some x', 'Removes execute', 'Changes the owner'], 1, 'Capital X.', 'X adds search to folders without making every file executable.')
K.quiz('h', 'ls -ld team shows drwxrws---. What does the s mean?', ['setuid', 'setgid: new files inside get the folder’s group', 'sticky', 'socket'], 1, 's in the group position.', 's in the group x position is the setgid bit.')
K.quiz('x', 'Which kernel feature lets a program bind port 80 without being fully root?', ['setgid', 'The capability CAP_NET_BIND_SERVICE', 'umask', 'The sticky bit'], 1, 'Root split into pieces.', 'capabilities(7) divides root privileges into units.')

K.calc('e', 'What is the octal digit for r-x?', '5', 'Add the values.', ['r = 4.', 'x = 1.', eq('4 + 1 = 5')], check=5)
K.calc('e', 'Write rwxr-x--- as a three digit number.', '750', 'One digit per class.', ['rwx = 4 + 2 + 1 = 7.', 'r-x = 4 + 1 = 5.', '--- = 0.', eq('750')], check=750)
K.calc('m', 'A new folder is made with umask 027. What mode does it get?', '750', 'Folders start from 777.', ['Start: 777 (rwxrwxrwx).', 'Remove 027: group loses w, others lose rwx.', eq('777 with 027 removed = 750')], check=750)
K.calc('m', 'A file has mode 640. You run chmod g+w,o+r. What is the new mode as a number?', '664', 'Add the bits.', ['Group: 4 + 2 = 6.', 'Others: 0 + 4 = 4.', eq('6 6 4, so 664')], check=664)
K.calc('m', 'How many different nine bit permission patterns (rwx for three classes) are possible?', '512', 'Each bit is on or off.', ['9 bits.', 'Each has 2 states.', eq('2⁹ = 512')], check=512)
K.calc('h', 'Write the full four digit mode of /tmp, which ls shows as drwxrwxrwt.', '1777', 'The t is the sticky bit.', ['rwx rwx rwx = 777.', 't in the last place means sticky, value 1000, with x set.', eq('1000 + 777 = 1777')], check=1777)

K.must('Mode string', 'Type, then owner, group and others, each rwx. r 4, w 2, x 1. 644 files, 755 programs and folders, 600 secrets.')
K.must('One class', 'The kernel uses only the first class that matches: root, owner, group, others. You also need x on every folder in the path.')
K.must('chmod', 'Numbers set everything (chmod 750). Letters change parts (u+x, go-w, u=rw). -R for trees, X for folders only.')
K.must('Ownership', 'chown needs root. chgrp works for groups you belong to. Deleting needs w and x on the folder.')
K.must('umask and special bits', 'umask removes bits from new files (022 gives 644 and 755). setuid 4000, setgid 2000, sticky 1000 as on /tmp.')

T = K.topic(
    slug='permissions', topic='permissions',
    step=(3, 'Permissions and editing', 'lx-basics-3', 'Who may read, change or run each file, and how to edit text in the terminal with nano and vim.', 'Beginner'),
    title='Users, groups and permissions', short='Permissions', badge='3.1', minutes=40, added='2026-11-23',
    lead='Read the nine letters of ls -l, understand exactly how the kernel decides who may open a file, change permissions and owners safely, and meet umask, setuid, setgid and the sticky bit.',
    desc='Owner, group and others, rwx on files and folders, octal and symbolic modes, the kernel permission check, chmod, chown and chgrp, umask, setuid on passwd, setgid team folders, the sticky bit on /tmp, capabilities, ACLs and mandatory access control.',
    summary='rwx, 644 and 755, chmod, chown, umask, setuid, setgid and the sticky bit.',
    keywords=['permissions', 'chmod', 'chown', 'chgrp', 'umask', 'rwx', 'octal', 'setuid', 'setgid', 'sticky bit', 'Permission denied'],
    recap='<p>Owner, group, others, each rwx. The kernel checks one class. chmod with numbers or letters, chown as root, umask for new files, and the special bits s and t.</p>')
