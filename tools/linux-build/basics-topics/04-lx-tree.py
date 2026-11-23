# Foundations 2.1: the single file tree, the Filesystem Hierarchy Standard, absolute and relative paths, . .. ~ and -,
# pwd, cd and ls in depth, hidden files. Sources: Filesystem Hierarchy Standard 3.0 (Linux Foundation, 2015),
# file-hierarchy(7) from systemd, GNU coreutils ls documentation, bash(1) on cd and tilde expansion, the Debian
# usrmerge notes (/bin, /sbin and /lib as links into /usr).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('onetree', 'One tree for everything', f'''
<p>Windows gives every disk its own letter: C:, D:, E:. Linux does it differently. There is <b>one single tree</b> of folders, and it starts at the top folder called the <b>root</b>, written as a single slash <code>/</code>. Every file on every disk, USB stick and network share appears somewhere inside that tree. A USB stick does not get a letter, it gets a folder, for example /media/learner/USB.</p>
<p>Linux people say <b>directory</b> where Windows says folder. They are the same thing. Paths use a forward slash <code>/</code> between names, never a backslash.</p>
{sample('The top of the tree on a typical Ubuntu machine', 'ls /', 'bin   dev  home  lib64  mnt  proc  run   srv  tmp  var\nboot  etc  lib   media  opt  root  sbin  sys  usr', note='Your list may have a few more names, such as snap or lost+found. The build machine of this page is a container with extra folders, so this is a typical desktop listing.')}
{play('lx-path')}
{note('The word root means two different things. / is the root directory, the top of the tree. root is also the name of the administrator user, whose home folder is /root. Context tells you which one is meant.', 'warn')}
{talk('Unix chose a single tree in the early 1970s, and the idea turned out to be powerful. Every disk, every USB stick and even special things like running programs appear as folders somewhere in one tree that starts at slash. When you plug in a USB stick, Linux attaches its files at a folder such as slash media, and this is called mounting. A program never needs to know which physical disk a file is on. It only needs the path. That is why a big company can move its data to a bigger disk, or to a network storage box, without changing a single program, only the place where the disk is attached. Windows took a different path from MS-DOS, giving each disk its own letter. Neither is wrong, but on Linux you will always think in one tree, and every path you write starts from slash or from where you stand.')}
''', kw=['root directory', 'slash', 'single tree', 'directory', 'folder', 'mount', 'drive letters'])

K.lesson('fhs', 'What lives where: the standard folders', f'''
<p>Linux distributions agree on what each top folder is for. The rules are written in the <b>Filesystem Hierarchy Standard</b> (FHS), version 3.0 from 2015. Once you know them, you can find your way around any Linux machine.</p>
{table(['Folder', 'What it holds', 'Example'], [
    ['/', 'The root, the top of everything', ''],
    ['/home', 'One folder per person for their own files', '/home/learner/notes.txt'],
    ['/root', 'Home folder of the root user', ''],
    ['/etc', 'System wide settings, as plain text files', '/etc/hostname, /etc/passwd'],
    ['/usr/bin', 'Programs for everyone. /bin is now a link to it on most distributions', '/usr/bin/ls'],
    ['/usr/sbin', 'Programs for system administration', '/usr/sbin/useradd'],
    ['/usr/lib, /lib', 'Libraries the programs share', 'libc.so.6'],
    ['/usr/local', 'Software you install yourself, outside the package manager', '/usr/local/bin/mytool'],
    ['/opt', 'Big add-on packages from outside companies', '/opt/google/chrome'],
    ['/var', 'Data that changes while the system runs', '/var/log/syslog, /var/www'],
    ['/var/log', 'Log files', '/var/log/auth.log'],
    ['/tmp', 'Temporary files, often wiped at reboot, writable by everyone', ''],
    ['/boot', 'The kernel and the files needed to start the computer', '/boot/vmlinuz'],
    ['/dev', 'Device files: disks, terminals, /dev/null', '/dev/sda'],
    ['/proc and /sys', 'Pretend files made by the kernel that show live information', '/proc/cpuinfo'],
    ['/mnt and /media', 'Places to attach other disks, by hand or automatically', '/media/learner/USB'],
    ['/run', 'Runtime data since the last boot, such as process id files', '/run/sshd.pid'],
    ['/srv', 'Data served by this machine, for example a website', '/srv/www']])}
{run('Look at some of them for real', '''ls -ld /bin /sbin /lib
ls /etc | head -n 5
cat /etc/hostname
head -n 2 /proc/cpuinfo''', note='On Ubuntu 24.04, /bin, /sbin and /lib are symbolic links into /usr (the "merged /usr" layout). /proc/cpuinfo is not on any disk: the kernel writes it when you read it.')}
{note('A quick memory aid: /etc for settings, /var for things that vary, /usr for installed programs, /home for people, /tmp for throw away files, /dev for devices.', 'tip')}
{deep('Why /bin and /usr/bin both exist', '<p>In early Unix the first disk was small, so the programs needed to start the system lived in /bin and everything else went on a second disk mounted at /usr. That reason disappeared long ago. Fedora (2012), Debian 12 (2023) and Ubuntu now keep everything in /usr and make /bin, /sbin and /lib links to it, so old scripts that call /bin/sh still work.</p>')}
{talk('The folder names of Linux look strange at first, but each one has a story. The name etc comes from the early Unix manuals, where it held miscellaneous files, and today it holds almost every setting of the system as readable text. var means variable, for data that changes while the system runs, like log files and databases. The split between slash bin and slash usr slash bin is a famous accident of history. In 1971 the first disk of the Unix computer at Bell Labs filled up, so Ken Thompson and Dennis Ritchie moved part of the system onto a second disk mounted at slash usr. Fifty years later the reason is gone, and modern distributions such as Fedora, Debian and Ubuntu have merged them back together, keeping links so old scripts still work. The Filesystem Hierarchy Standard writes all of this down so every distribution looks familiar.')}
''', kw=['FHS', 'Filesystem Hierarchy Standard', '/etc', '/home', '/var', '/usr', '/bin', '/tmp', '/dev', '/proc', '/opt', 'usrmerge'])

K.lesson('paths', 'Absolute and relative paths, . .. and ~', f'''
<p>A <b>path</b> tells the system how to reach a file. There are two kinds.</p>
{fxs(fx('Absolute path', 'starts with <code>/</code>', 'The full route from the root. It means the same thing wherever you are: /home/learner/logs/app.log.', key=True),
     fx('Relative path', 'does not start with <code>/</code>', 'A route from the folder you are in now. From /home/learner, logs/app.log means /home/learner/logs/app.log.', key=True),
     fx('Special names', '<code>.</code> this folder, <code>..</code> the parent, <code>~</code> your home, <code>-</code> the previous folder (only for cd)', 'They can be mixed into any path: ../asha, ~/logs, ./script.sh.'))}
{steps('Work out where logs/../scripts/./hello.sh points, starting in /home/learner', [
    'Start: /home/learner (the path does not start with /, so it is relative).',
    'logs: go into /home/learner/logs.',
    '..: go up to the parent, back to /home/learner.',
    'scripts: go into /home/learner/scripts.',
    '.: stay where you are.',
    eq('hello.sh: the file /home/learner/scripts/hello.sh')])}
{run('Paths in action', '''pwd
cd logs
pwd
cd ..
pwd
cd /etc
pwd
cd ~
pwd
cd -
cd
pwd''', note='cd - goes back to the previous folder and prints it. cd with nothing goes home.')}
{note('Every folder contains . and .., even the root. In / the parent .. points back to / itself, so cd .. at the top stays at the top.', 'tip')}
{talk('Paths are like directions to a house. An absolute path is like a full postal address: country, city, street and house number. It works from anywhere in the world. A relative path is like telling a neighbour, two doors down on the left. It is shorter, but only makes sense from where you are standing. On Linux, an absolute path always starts with a slash, and a relative path never does. There are a few handy shortcuts. A single dot means here, two dots mean one folder up, and the tilde means your home folder. The tilde shortcut comes from an old terminal called the Lear Siegler ADM-3A from 1976, whose Home key also had a tilde printed on it. Bill Joy used that terminal while writing software at Berkeley, so the tilde came to mean home. Many programmers still type cd tilde every day without knowing that story.')}
''', kw=['absolute path', 'relative path', 'dot', 'dot dot', 'tilde', 'cd -', 'pwd', 'cd', 'parent directory'])

K.lesson('ls', 'Seeing what is there: ls in depth', f'''
{cmdtable([
    ('ls', 'Names in the current folder', 'ls'),
    ('ls -l', 'Long listing: type and permissions, links, owner, group, size, time, name', 'ls -l logs'),
    ('ls -a', 'Also show hidden names, the ones starting with a dot, plus . and ..', 'ls -a'),
    ('ls -A', 'Hidden names too, but without . and ..', 'ls -A'),
    ('ls -h', 'With -l, sizes like 4.0K instead of 4096', 'ls -lh'),
    ('ls -t', 'Newest first. Add -r to reverse any order', 'ls -ltr'),
    ('ls -S', 'Biggest first', 'ls -lS'),
    ('ls -R', 'Go into every subfolder too', 'ls -R projects'),
    ('ls -d', 'Show the folder itself, not its contents', 'ls -ld /tmp'),
    ('ls -F', 'Add a mark: / for folders, * for programs, @ for links', 'ls -F')])}
{run('Read a long listing', '''ls -l
ls -A
ls -F''')}
{table(['Column in ls -l', 'Example', 'Meaning'], [
    ['1. Type and permissions', '<code>drwxr-xr-x</code>', 'First letter: - file, d directory, l symbolic link, c and b devices. Then nine permission letters (chapter 3.1).'],
    ['2. Links', '<code>2</code>', 'How many names point to this item (chapter on inodes)'],
    ['3. Owner', '<code>learner</code>', 'The user who owns it'],
    ['4. Group', '<code>learner</code>', 'The group that owns it'],
    ['5. Size', '<code>332</code>', 'Bytes. A directory shows the space for its list of names, often 4096'],
    ['6. Time', '<code>Nov 23 09:30</code>', 'Last time the content was changed. Older than six months shows the year instead of the time'],
    ['7. Name', '<code>latest.log -&gt; logs/app.log</code>', 'For a link, also where it points']])}
{note('Files whose names start with a dot are <b>hidden</b>. It is only a naming habit, not a security feature: ls -a shows them. Settings files like .bashrc are hidden so they do not clutter your home folder.', 'tip')}
{lab('Walk the tree', [
    ('Show the full path of where you are.', 'pwd', [{'out': '^/home/learner$'}]),
    ('Go into the <code>logs</code> folder.', 'cd logs', [{'cwd': '/home/learner/logs'}]),
    ('Go back up to the parent folder with <code>..</code>', 'cd ..', [{'cmd': r'cd\s+\.\.'}, {'cwd': '/home/learner'}]),
    ('Jump to <code>/etc</code> with an absolute path.', 'cd /etc', [{'cwd': '/etc'}]),
    ('List /etc in long form.', 'ls -l', [{'cmd': r'ls\s+-\w*l'}, {'out': 'passwd'}]),
    ('Go home with the tilde.', 'cd ~', [{'cwd': '/home/learner'}]),
    ('Show hidden files in your home folder.', 'ls -a', [{'cmd': r'ls\s+-\w*[aA]'}, {'out': r'\.bashrc'}]),
    ('List the scripts folder without going into it, using a relative path.', 'ls -l scripts', [{'cmd': r'ls\b.*scripts'}, {'out': 'hello.sh'}])])}
{talk('The ls command is probably the most typed command in the history of Unix. Its name is short for list, and it was in the very first edition of Unix in 1971. The long listing with dash l packs a lot into one line: what kind of thing it is, who may use it, who owns it, how big it is and when it last changed. Learn to read that line slowly once, and you will read it in a glance forever. Hidden files have a funny origin. In early Unix, ls was written to skip the dot and dot dot entries, and the quick way to do that was to skip every name starting with a dot. People then noticed they could hide their settings files by starting their names with a dot, and the habit stuck. It was a small bug that became a feature, and it is why your home folder has files like dot bashrc that you never see unless you ask.')}
''', kw=['ls', 'ls -l', 'ls -a', 'hidden files', 'dotfiles', 'ls -lh', 'ls -ltr', 'ls -R', 'ls -d', 'long listing columns'])

K.lesson('levels', 'The file tree from school to research', f'''
{ladder(
    '<p>All the files in Linux live in one big upside down tree. The top is called root and written /. Folders hold files and other folders. A path is the list of folder names you walk through to reach a file.</p>',
    '<p>Linux presents a single hierarchical namespace rooted at /. Other filesystems are mounted onto directories. The FHS assigns roles to top level directories. Paths are absolute or relative to the process working directory, and the kernel resolves them component by component.</p>',
    '<p>Path resolution (namei) walks each component through the dentry cache, checks execute permission on every directory crossed, follows symbolic links (up to 40 in a path), and crosses mount points. Each process has its own current directory and root directory, which chroot and mount namespaces change, so two processes can see different trees.</p>',
    '<p>Current work includes per process views of the tree in containers (mount namespaces, overlay filesystems), safer path lookup with openat2() and its RESOLVE_ flags (Linux 5.6, 2020) against symlink race attacks, and union and network filesystems. Older research systems such as Plan 9 from Bell Labs pushed the one tree idea further, with every resource as a file in a per process namespace.</p>')}
{scene('a web server', '<p>On a Linux web server, the website files usually live in /var/www, the settings of the web server in /etc/nginx, its logs in /var/log/nginx, and the program itself in /usr/sbin/nginx. An engineer who has never seen that server can still find everything in a minute, because every machine follows the same layout.</p>')}
{talk('The one tree idea has been pushed very far. In the late 1980s the same Bell Labs team that created Unix built a research system called Plan 9, where every resource, even the network and the windows on the screen, was a file in a tree, and every program could have its own private view of that tree. Linux borrowed some of those ideas. Today, when you start a container with Docker, the container gets its own private file tree through a kernel feature called mount namespaces, so it sees a slash that is really just a folder on the host. Security researchers also study path tricks, where an attacker swaps a folder for a link at just the right moment, and in 2020 Linux added a safer way to open paths called openat2. All of this still rests on the simple idea you learned here: one tree, starting at slash.')}
''', kw=['namespace', 'mount', 'path resolution', 'dentry', 'chroot', 'mount namespace', 'openat2', 'Plan 9'])

K.quiz('e', 'What is the top folder of the Linux file tree called?', ['C:', 'The root, written /', 'home', 'top'], 1, 'One slash.', 'Everything starts at /, the root directory.')
K.quiz('e', 'Which folder holds your own files?', ['/etc', '/home/your-name', '/usr', '/bin'], 1, 'One folder per person.', 'Each user has a home folder under /home. ~ is a short way to write it.')
K.quiz('e', 'Which command prints the folder you are in?', ['cd', 'pwd', 'ls', 'where'], 1, 'Print working directory.', 'pwd prints the absolute path of the current folder.')
K.quiz('e', 'Which ls option shows hidden files?', ['-l', '-a', '-h', '-t'], 1, 'All.', '-a shows names that start with a dot.')
K.quiz('m', 'You are in /home/learner/logs. Where does cd .. take you?', ['/', '/home', '/home/learner', '/home/learner/logs/..'], 2, 'Up one level.', '.. is the parent of the current folder.')
K.quiz('m', 'Which path is absolute?', ['logs/app.log', './notes.txt', '/etc/hostname', '../asha'], 2, 'It starts with something special.', 'Only paths that start with / are absolute.')
K.quiz('m', 'Where should system wide settings files live?', ['/var', '/etc', '/tmp', '/opt'], 1, 'Text settings.', '/etc holds configuration such as /etc/hosts and /etc/passwd.')
K.quiz('m', 'Where do log files usually go?', ['/etc/log', '/var/log', '/usr/log', '/home/log'], 1, 'Data that varies.', '/var/log holds logs written while the system runs.')
K.quiz('m', 'What does cd - do?', ['Goes to /', 'Goes back to the previous folder', 'Goes home', 'Deletes the folder'], 1, 'Like a back button.', 'cd - switches to $OLDPWD and prints it.')
K.quiz('m', 'In ls -l, the first character is d. What is the item?', ['A device', 'A directory', 'A deleted file', 'A document'], 1, '- is a file, l is a link.', 'd marks a directory.')
K.quiz('h', 'You are in /etc. What is the absolute path of ../home/./learner/../asha?', ['/home/asha', '/etc/home/asha', '/home/learner/asha', '/asha'], 0, 'Resolve one name at a time.', '/etc then .. gives /, home gives /home, . stays, learner then .. return to /home, asha gives /home/asha.')
K.quiz('h', 'Why is /proc/cpuinfo not stored on any disk?', ['It is in memory cache', 'The kernel creates its contents at the moment you read it', 'It is a link to the disk', 'It is deleted at boot'], 1, 'proc is a pretend filesystem.', '/proc is a virtual filesystem filled by the kernel on demand.')
K.quiz('x', 'Two processes print different contents for ls /. What kernel feature most likely explains it?', ['Different shells', 'Mount namespaces or chroot give them different root trees', 'A broken disk', 'Different terminals'], 1, 'Containers.', 'Each process can have its own root directory and mount namespace.')

K.calc('e', 'How many folders do you go through to reach /home/learner/logs/app.log from the root, not counting / itself and not counting the file?', '3', 'Count the names between slashes, except the last.',
       ['Names: home, learner, logs, app.log.', 'app.log is the file.', eq('folders: home, learner, logs = 3')], check=3)
K.calc('e', 'You are in /home/learner/logs. How many times must you run cd .. to reach /?', '3', 'One level per cd ..', ['/home/learner/logs to /home/learner.', '/home/learner to /home.', eq('/home to /: 3 times')], check=3)
K.calc('m', 'ls -l shows a size of 4096 for a directory. How many kilobytes (KiB) is that?', '4', '1 KiB = 1,024 bytes.', ['Size in bytes: 4,096.', 'One KiB is 1,024 bytes.', eq('4,096 ÷ 1,024 = 4 KiB, which ls -lh shows as 4.0K')], check=4)
K.calc('m', 'From /home/learner/logs, a relative path to /home/asha needs how many .. steps before the name asha?', '2', 'Climb to the common parent.', ['Common parent of the two paths: /home.', 'From logs: up to learner (1), up to home (2).', eq('../../asha uses 2 .. steps')], check=2)
K.calc('m', 'The absolute path /home/learner/projects is 23 characters long. The relative path from /home/learner is projects. How many characters do you save?', '15', 'Count both.', ['Absolute: 23 characters.', 'Relative: projects has 8 characters.', eq('23 − 8 = 15')], check=23 - 8)
K.calc('h', 'The kernel follows at most 40 symbolic links while resolving one path. A chain of links each pointing to the next is 41 long. How many links too many is that?', '1', 'Compare with the limit.', ['Limit: 40.', 'Chain: 41.', eq('41 − 40 = 1 too many, so the kernel gives "Too many levels of symbolic links" (ELOOP)')], check=1)

K.must('One tree', 'Everything hangs from / (the root). Disks are mounted onto folders, there are no drive letters.')
K.must('FHS', '/etc settings, /home people, /var changing data and /var/log logs, /usr programs, /tmp temporary, /dev devices, /proc live kernel info.')
K.must('Paths', 'Absolute starts with /. Relative starts from pwd. . here, .. parent, ~ home, cd - previous folder.')
K.must('ls', '-l long, -a hidden, -h human sizes, -t newest first, -r reverse, -R recursive, -d the folder itself.')
K.must('Hidden files', 'A name starting with a dot is hidden from plain ls. It is a convention, not security.')

T = K.topic(
    slug='file-tree', topic='file-tree',
    step=(2, 'Files and folders', 'lx-basics-2', 'The single file tree, paths, making, copying, moving and deleting files and folders, wildcards, and reading files.', 'Beginner'),
    title='The file tree and paths', short='The file tree', badge='2.1', minutes=35, added='2026-11-23',
    lead='See how Linux puts every file in one tree that starts at /, what each standard folder is for, how absolute and relative paths work, and how to move around and look with pwd, cd and ls.',
    desc='The single directory tree and mounting, the Filesystem Hierarchy Standard (/etc, /home, /var, /usr, /tmp, /dev, /proc), merged /usr, absolute and relative paths, . .. ~ and cd -, pwd, cd, ls options, reading ls -l and hidden dotfiles.',
    summary='The single tree, standard folders (FHS), absolute and relative paths, pwd, cd and ls in depth, hidden files.',
    keywords=['file tree', 'root directory', 'fhs', 'path', 'absolute path', 'relative path', 'pwd', 'cd', 'ls', 'hidden files', '/etc', '/var', '/home'],
    recap='<p>One tree from /. Know the standard folders. Absolute paths start with /, relative ones start where you are. pwd tells you where, cd moves you, ls shows what is there.</p>')
