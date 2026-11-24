# Internals and advanced 3.3: full revision of the Unix and Linux course. The whole course on one page, the numbers
# that come up again and again (permission bits, umask, cron fields, exit codes, CIDR), pipelines read step by step,
# incidents solved with commands from every section, one mixed practice lab, and how Linux is examined at school,
# university and in the hands-on certifications.
# Sources: the earlier chapters of this course and their man pages: chmod(1), umask in the bash manual, crontab(5),
# bash(1) on exit status 128 + n, ip(8), sort(1), uniq(1), awk (gawk manual). Exam facts from the public pages of the
# Linux Professional Institute (LPIC-1, exams 101 and 102), CompTIA Linux+, Red Hat (RHCSA, exam EX200, hands-on)
# and the Linux Foundation (LFCS, hands-on). No question is copied from any real exam.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('map', 'The whole course on one page', f'''
<p>This chapter teaches nothing new. It puts the five parts of the course side by side, drills the numbers and patterns that come up most, and ends with a lab that mixes all of them. Each line names the chapter to go back to.</p>
{table(['Part', 'Chapters', 'Commands to know by heart'], [
    ['Foundations', '1.1 to 3.2: what Linux is, the shell, help, the file tree, files, reading files, permissions, editors', '<code>pwd ls cd man mkdir cp mv rm cat less head tail chmod chown nano vim</code>'],
    ['Power tools', '1.1 to 4.2: redirection, pipes, grep, sed, awk, find, archives, processes, variables', '<code>&gt; &gt;&gt; 2&gt;&amp;1 | sort uniq wc cut grep -E sed -i awk find xargs tar ps kill jobs export</code>'],
    ['Scripting', '1.1 to 4.2: first scripts, expansions, decisions, loops, functions, arrays, robust scripts, scheduling', '<code>#!/bin/bash $1 "$@" [[ ]] if case for while read local set -euo pipefail trap crontab</code>'],
    ['Administration', '1.1 to 4.3: users, packages, systemd, logs, disks, LVM and backups, networking, SSH, firewall', '<code>sudo useradd apt systemctl journalctl df du lsblk mount lvcreate rsync ip ss ssh ufw</code>'],
    ['Internals and advanced', '1.1 to 3.3: kernel, processes, files inside, memory, containers, performance', '<code>strace /proc stat ln lsof free vmstat unshare setcap iostat pidstat perf</code>']])}
{table(['Exam or path', 'Format', 'Where this course covers it'], [
    ['School and university Unix exams', 'Short answers, command output to predict, small scripts on paper', 'Foundations, Power tools, Scripting'],
    ['LPIC-1 (Linux Professional Institute, exams 101 and 102)', 'Multiple choice and fill in the blank', 'all parts, with Administration for packages, boot, disks and networking'],
    ['CompTIA Linux+', 'Multiple choice and performance based questions', 'Administration, Scripting, Firewall and Performance'],
    ['RHCSA (Red Hat, exam EX200) and LFCS (Linux Foundation)', 'Hands-on tasks on live systems, no multiple choice', 'every lab, and the practice shell, but on RHEL use dnf and firewalld instead of apt and ufw'],
    ['Job interviews for DevOps, SRE and support', 'Troubleshooting stories and “what happens when”', 'Advanced chapters and the incident lesson here']])}
{note('Hands-on exams reward speed with man pages, <code>--help</code> and tab completion more than memory. Practise every lab here without looking at the hints.', 'tip')}
{talk('This last chapter teaches nothing new. It brings the whole course together. The five parts are foundations, power tools, scripting, administration, and internals. The table lists the commands to know by heart from each part, and the chapter to go back to when one feels shaky. School and university exams ask you to predict output and write small scripts. L P I C one and Comp T I A Linux plus are mostly multiple choice. R H C S A and L F C S are hands on, on a live system, so practise the labs here without hints and get fast with man pages and tab completion.')}
''', kw=['revision', 'course summary', 'Linux exam', 'LPIC-1', 'CompTIA Linux+', 'RHCSA', 'EX200', 'LFCS', 'hands-on exam', 'interview preparation', 'commands to know'])

K.lesson('numbers', 'The numbers that come up again and again', f'''
{table(['Topic', 'Rule', 'Example', 'Chapter'], [
    ['Permission bits', 'r = 4, w = 2, x = 1, one digit each for user, group, others', '<code>chmod 640</code> is rw-r-----', 'Foundations 3.1'],
    ['umask', 'new files start at 666, folders at 777, umask bits are taken away', 'umask 027: files 640, folders 750', 'Foundations 3.1'],
    ['Special bits', 'SUID 4, SGID 2, sticky 1, as a fourth digit in front', '<code>chmod 1777 /tmp</code>, <code>chmod 2775 shared</code>', 'Foundations 3.1'],
    ['Exit status', '0 is success, 1 to 125 errors, 126 not executable, 127 not found, 128 + n killed by signal n', 'SIGKILL (9) gives 137, Ctrl+C (SIGINT, 2) gives 130', 'Scripting 2.1, Power 4.1'],
    ['cron fields', 'minute, hour, day of month, month, day of week', '<code>30 2 * * 1-5</code> is 02:30 Monday to Friday', 'Scripting 4.2'],
    ['File descriptors', '0 stdin, 1 stdout, 2 stderr', '<code>cmd &gt; out.log 2&gt;&amp;1</code>', 'Power 1.1'],
    ['CIDR', 'a /n network has 2 to the power (32 − n) addresses, minus 2 for hosts', '/24: 256 addresses, 254 hosts', 'Admin 4.1'],
    ['Ports', '22 SSH, 53 DNS, 80 HTTP, 443 HTTPS, below 1024 need root or CAP_NET_BIND_SERVICE', '<code>ss -tln</code>', 'Admin 4.1, Advanced 3.1']])}
{run('Check three of the rules on a real shell', """umask 027
touch report.txt
mkdir private
stat -c '%a %A %n' report.txt private
printf '%o\\n' $(( 0666 & ~0027 ))
sleep 30 &
kill -9 $!
wait $!
echo "exit status: $?"
bash -c 'nosuchcommand' 2>/dev/null
echo "exit status: $?\"""", note='With umask 027 a new file gets 640 and a new folder 750, and the shell arithmetic shows the same: 666 with the bits of 027 taken away is 640. A sleep killed with signal 9 reports 128 + 9 = 137, and a command that is not found reports 127.')}
{steps('Read a permission string in five seconds', [
    'Take <code>-rwxr-x---</code>. The first character is the type: - file, d folder, l link.',
    'Split the rest into three groups: rwx, r-x, ---.',
    'Add r 4, w 2, x 1 in each group: 7, 5, 0.',
    'So it is 750: the owner may do everything, the group may read and run, others nothing.',
    'An s in the user group means SUID, in the group group SGID, and a t in the last group the sticky bit.'])}
{talk('Some numbers come back in every exam and on every server. Permission digits add read four, write two and execute one, for user, group and others, so six four zero is read and write for the owner and read for the group. The umask takes bits away from six six six for files and seven seven seven for folders. Exit status zero is success, one hundred twenty seven means command not found, and one hundred twenty eight plus n means killed by signal n, so a kill minus nine gives one hundred thirty seven. The box checks three of these rules on a real shell.')}
''', kw=['chmod octal', 'permission digits', 'umask 027', 'SUID SGID sticky', 'exit status 137', 'exit status 127', '128 + n', 'cron fields', 'file descriptors', 'CIDR hosts', 'well known ports', 'read permission string'])

K.lesson('pipes', 'Read and build pipelines', f'''
<p>Exams love a pipeline with a question “what does it print?”. Read it from left to right and write down what each stage hands to the next.</p>
{run('Three classic pipelines on the practice files', """sort fruits.txt | uniq -c | sort -rn | head -n 3
awk -F, 'NR > 1 { sum[$2] += $3; n[$2]++ } END { for (s in sum) printf "%s %.1f\\n", s, sum[s] / n[s] }' marks.csv | sort
grep ERROR logs/app.log | cut -d' ' -f2,4-
ls -l | awk 'NR > 1 { total += $5 } END { print total, "bytes in", NR - 1, "entries" }'""", note='First: sort puts equal lines next to each other, uniq -c counts each run, sort -rn puts the biggest count first, head keeps three. Second: awk splits marks.csv at commas, skips the header, adds up the scores and counts per subject, and prints the average. Third: grep keeps the error lines and cut keeps the time and the message. Fourth: awk adds up the size column of ls -l.')}
{table(['Need', 'Pattern', 'Chapter'], [
    ['how often does each value occur', '<code>sort | uniq -c | sort -rn</code>', 'Power 1.2'],
    ['sum or average a column', "<code>awk '{ s += $3 } END { print s }'</code>", 'Power 2.3'],
    ['change text in many files', "<code>grep -rl old . | xargs sed -i 's/old/new/g'</code>", 'Power 2.2 and 3.1'],
    ['find big old files', '<code>find /var/log -type f -size +100M -mtime +30</code>', 'Power 3.1'],
    ['save output and errors', '<code>./job.sh &gt; job.log 2&gt;&amp;1</code>', 'Power 1.1'],
    ['run a command for each line', '<code>while read -r host; do ssh "$host" uptime; done &lt; hosts.txt</code>', 'Scripting 2.2']])}
{note('Filenames with spaces break <code>xargs</code> and unquoted loops. Use <code>find -print0 | xargs -0</code>, and always quote "$var" in scripts.', 'warn')}
{talk('Pipelines are the heart of the shell and a favourite exam question. Read one from left to right and note what each stage passes on. In the first, sort groups equal lines, uniq minus c counts them, sort minus r n puts the biggest count first and head keeps three. The second uses awk to average the scores per subject. The third keeps error lines and cuts out the fields you need, and the fourth adds up a column. The table lists the patterns that solve most daily tasks, and the chapter that teaches each one.')}
''', kw=['pipeline', 'sort uniq -c', 'awk average', 'awk sum', 'grep cut', 'xargs sed', 'find size mtime', 'while read', 'print0', 'quote variables', 'predict output'])

K.lesson('incidents', 'Incidents: the whole course at work', f'''
<p>Real problems do not stay inside one chapter. An admin looks, narrows down, finds the cause, fixes it, and stops it from coming back, using whatever tool fits.</p>
{play('lx-triage')}
{table(['Symptom', 'First commands', 'Usual causes', 'Chapters'], [
    ['No space left on device', '<code>df -h</code>, <code>df -i</code>, <code>du -xh --max-depth=1 /</code>, <code>lsof +L1</code>', 'logs, old kernels or images, deleted files still open, out of inodes', 'Admin 2.2 and 3.1, Advanced 2.1'],
    ['Service will not start', '<code>systemctl status</code>, <code>journalctl -u NAME -n 50</code>, the service’s config test', 'port in use, config error, wrong permissions, missing file', 'Admin 2.1 and 2.2'],
    ['Cannot connect over the network', '<code>ip -br addr</code>, <code>ip route</code>, <code>ping</code>, <code>ss -tln</code>, <code>nc -vz</code>, <code>ufw status</code>', 'nothing listening, firewall, wrong route or DNS', 'Admin 4.1 to 4.3'],
    ['Permission denied', '<code>ls -l</code>, <code>id</code>, <code>namei -l PATH</code>, <code>sudo -l</code>', 'missing x on a parent folder, wrong owner, not in the group yet (log in again)', 'Foundations 3.1, Admin 1.1'],
    ['Server is slow', '<code>uptime</code>, <code>vmstat 1</code>, <code>top</code>, <code>iostat -xz 1</code>, <code>free -m</code>', 'CPU hog, swapping, a saturated disk', 'Advanced 2.2 and 3.2'],
    ['Script works by hand, fails in cron', '<code>grep CRON /var/log/syslog</code>, the job’s log, <code>env -i</code> test', 'PATH, missing variables, relative paths', 'Scripting 4.2']])}
{scene('the full disk at midnight', '<p>A monitoring alert said the root file system was at 100 %. <code>df -h</code> confirmed it, but <code>du</code> found only 20 GB of the 40 GB. <code>sudo lsof +L1</code> showed a 19 GB debug log that someone had deleted while the app still wrote to it. Restarting the app gave the space back. The team then added a logrotate rule with copytruncate, a disk alert at 80 %, and a note in the runbook. Three chapters (disks, files inside, logs) solved one incident.</p>')}
{talk('Real problems cross chapters. In the animation, pick a problem and see the commands an admin would use, with the chapter each comes from. For a full disk, look with d f, find the big folder with d u, and remember that a deleted file still open keeps its space. For a service that will not start, read systemctl status and the journal. For network trouble, go from the bottom up: address, route, port, firewall. For permission denied, check every folder on the path. Fix the cause, then make sure it cannot happen again.')}
''', kw=['troubleshooting', 'incident', 'no space left on device', 'df -i', 'lsof +L1', 'service will not start', 'address already in use', 'connection refused', 'connection timed out', 'permission denied', 'namei', 'cron PATH', 'runbook'])

K.lesson('practice', 'Final practice: one lab across the course', f'''
<p>Twelve tasks, one from each corner of the course. Try each without the hint first.</p>
{lab('The whole course', [
    ('Show the folder you are in.', 'pwd', [{'out': r'^/home/learner$'}]),
    ('Count the lines of fruits.txt that contain apple.', 'grep -c apple fruits.txt', [{'out': r'^3$'}]),
    ('Print each fruit with its count, most common first.', 'sort fruits.txt | uniq -c | sort -rn', [{'out': r'^\s+3 apple'}]),
    ('Add up the scores (column 3) of marks.csv, skipping the header, with awk.', "awk -F, 'NR > 1 { s += $3 } END { print s }' marks.csv", [{'out': r'^481$'}]),
    ('Show only the ERROR lines of logs/app.log.', 'grep ERROR logs/app.log', [{'out': 'payment failed'}]),
    ('Create the folder projects/site.', 'mkdir projects/site', [{'exists': '/home/learner/projects/site'}]),
    ('Give projects/site the mode 750.', 'chmod 750 projects/site', [{'mode': ['projects/site', '750']}]),
    ('Pack the logs folder into logs.tar.gz.', 'tar czf logs.tar.gz logs', [{'exists': '/home/learner/logs.tar.gz'}]),
    ('Check whether nginx is running.', 'systemctl is-active nginx', [{'out': r'^active$'}]),
    ('List the TCP ports that are listening, as numbers.', 'ss -tln', [{'out': r':80\s'}]),
    ('Show how full the root file system is, in human units.', 'df -h /', [{'out': r'/dev/sda1\s+40G'}]),
    ('Show the run queue and CPU split with vmstat, every second, 2 times.', 'vmstat 1 2', [{'out': r'r\s+b\s+swpd'}])])}
{talk('This last lab mixes the whole course. Find where you are, count and rank lines with grep, sort and uniq, add up a column with awk, and pick out error lines. Make a folder and give it mode seven five zero, then pack the logs into a tar archive. As an admin, check nginx, the listening ports and the free space on the root file system, and finish with vmstat. If any task feels slow, go back to the chapter named in the revision tables.')}
''', kw=['final lab', 'mixed practice', 'revision lab', 'grep -c', 'uniq -c', 'awk sum', 'chmod 750', 'tar czf', 'systemctl is-active', 'ss -tln', 'df -h', 'vmstat'])

K.lesson('levels', 'Where to go from here', f'''
{ladder(
    '<p>You can move around the file tree, make, copy and delete files, read them, set permissions, and string commands together with pipes. That is enough to use any Linux computer, a Raspberry Pi or a phone’s terminal app with confidence.</p>',
    '<p>You can write robust Bash scripts, schedule them, run a server with users, packages, services, logs, disks, backups, SSH and a firewall, and find out why something fails or is slow. That covers LPIC-1, Linux+ and most of RHCSA and LFCS.</p>',
    '<p>Next steps for a job: configuration management with Ansible, containers with Docker and Kubernetes, CI/CD pipelines (the Git and CI/CD subject on this site), monitoring with Prometheus and Grafana, and cloud servers. Practise on a spare VM and break it on purpose.</p>',
    '<p>For depth: read the kernel source and its documentation, write a small kernel module or an eBPF program, study the C standard library and system calls (Advanced 1.1), and follow LWN.net for kernel development. Research topics include schedulers, file systems, memory tiering, and secure isolation.</p>')}
{scene('the intern who learned by breaking things', '<p>An intern got a spare cloud VM and one rule: break it, then fix it, and write down how. Week one, a <code>chmod -R 700 /</code> on a test copy taught how much depends on permissions. Week two, a full disk and a deleted open file. Week three, a wrong firewall rule that locked out SSH, fixed through the cloud console. After two months the notes were the team’s best runbook, and the intern passed RHCSA.</p>')}
{talk('You have reached the end of the course. At school level you can use any Linux computer with confidence. As a professional you can script, run and repair a server, which covers the common certifications. For a job in operations, learn Ansible, containers, Kubernetes, pipelines, monitoring and the cloud, and practise on a spare virtual machine that you break on purpose. For depth, read the kernel source, write an e B P F program, and follow kernel news on L W N. Keep using the practice shell and the labs to stay fast.')}
''', kw=['next steps', 'Ansible', 'Docker', 'Kubernetes', 'CI/CD', 'Prometheus', 'Grafana', 'cloud', 'kernel module', 'eBPF program', 'LWN', 'homelab', 'break and fix'])

K.quiz('e', 'Which command shows the folder you are in?', ['ls', 'pwd', 'cd', 'where'], 1, 'Print working directory.', 'Foundations 1.2.')
K.quiz('e', 'What does chmod 640 file give?', ['rw-r-----', 'rwxr-----', 'rw-rw-r--', 'r--r-----'], 0, '6 = 4 + 2, 4 = r.', 'Foundations 3.1.')
K.quiz('e', 'Which operator sends output to a file and replaces what was there?', ['>>', '>', '|', '<'], 1, 'One arrow.', '>> appends.')
K.quiz('e', 'What does the exit status 127 mean in bash?', ['Success', 'Command not found', 'Killed', 'Permission denied'], 1, 'Not found.', '126 is not executable.')
K.quiz('m', 'umask is 027. What mode does a new folder get?', ['755', '750', '640', '770'], 1, '777 minus the bits.', 'Files get 640.')
K.quiz('m', 'What does <code>sort | uniq -c | sort -rn</code> produce?', ['Lines in random order', 'Each distinct line with its count, most common first', 'Only duplicate lines', 'Line numbers'], 1, 'Count runs.', 'Power 1.2.')
K.quiz('m', 'What does the cron line <code>0 */6 * * *</code> mean?', ['Every 6 minutes', 'At minute 0 of every 6th hour', 'At 06:00 only', 'Every 6 days'], 1, 'Minute first.', 'Scripting 4.2.')
K.quiz('m', 'A script runs fine by hand but fails from cron with “command not found”. The most likely reason?', ['cron is broken', 'cron runs with a short PATH', 'The disk is full', 'The script is too long'], 1, 'Environment.', 'Use full paths or set PATH.')
K.quiz('m', 'nginx will not start and its log says “Address already in use”. Which command finds the culprit?', ['df -h', 'ss -tlnp', 'free -m', 'lsblk'], 1, 'Ports.', 'Admin 4.1.')
K.quiz('h', 'df shows 100 % but du finds only half. What is a likely cause?', ['A broken disk', 'A deleted file still held open by a process', 'Too many folders', 'A wrong umask'], 1, 'lsof +L1.', 'Advanced 2.1.')
K.quiz('h', 'ssh says “Connection timed out” instead of “Connection refused”. What does that suggest?', ['sshd is not running', 'Packets are dropped, often by a firewall', 'Wrong password', 'Wrong key'], 1, 'Refused means a reply came.', 'Admin 4.3.')
K.quiz('h', 'A container sees PID 1 as its own shell. Which kernel feature does that?', ['cgroups', 'the PID namespace', 'chroot', 'seccomp'], 1, 'Namespaces.', 'Advanced 3.1.')
K.quiz('h', 'Load average is 9 on a 4 CPU server with id 70 % and wa 25 %. What do you check next?', ['CPU frequency', 'The disks, with iostat -xz 1', 'The firewall', 'The users'], 1, 'D state tasks.', 'Advanced 3.2.')
K.quiz('x', 'Which exams test Linux skills with hands-on tasks on a live system?', ['LPIC-1 only', 'RHCSA and LFCS', 'None', 'Every exam'], 1, 'Performance based.', 'Practise the labs without hints.')

K.calc('e', 'What octal mode is <code>rwxr-x---</code>?', '750', 'Add r 4, w 2, x 1 per group.', ['rwx = 7.', 'r-x = 5, --- = 0.', eq('750')], check=750)
K.calc('e', 'A process killed by SIGKILL (signal 9). What exit status does bash report?', '137', '128 + n.', ['128 + 9.', 'Signals add to 128.', eq('137')], check=137)
K.calc('m', 'umask 077. What mode does a new file get? (start from 666)', '600', 'Take bits away.', ['666 with the bits of 077 removed.', '6 stays, 6 and 6 become 0.', eq('600')], check=600)
K.calc('m', 'How many usable host addresses does a /26 network have?', '62', '2 to the power (32 − n), minus 2.', ['32 − 26 = 6.', '2 to the power 6 = 64.', eq('64 − 2 = 62 hosts')], check=62)
K.calc('m', 'A cron job runs at <code>*/15</code> minutes. How many times does it run in one day?', '96', 'Per hour times 24.', ['60 ÷ 15 = 4 per hour.', '4 × 24.', eq('96 runs')], check=96)
K.calc('h', 'A log grows 300 MB a day on a disk with 12 GB free. In how many days is the disk full?', '40', 'Divide.', ['12 GB = 12000 MB.', '12000 ÷ 300.', eq('40 days')], check=40)
K.calc('x', 'logrotate keeps 7 old logs of 300 MB each, compressed to 10 % of their size, plus the live log of 300 MB. How many MB is that in total?', '510', 'Old logs compressed.', ['7 × 300 × 0.1 = 210 MB.', 'Plus 300 MB live.', eq('510 MB')], check=510)

K.must('Foundations and power tools', 'Paths, ls, cd, cp, mv, rm, less, permissions in octal and umask, redirection with 2>&1, pipes with sort, uniq, cut, grep, sed, awk, find, xargs and tar.')
K.must('Scripting', 'A shebang, quoted "$@", [[ ]] tests, case, for and while read loops, functions with local, set -euo pipefail, trap, exit codes, cron with full paths and flock.')
K.must('Administration', 'sudo and groups, apt, systemctl and journalctl, df, du, lsblk, mount and fstab, LVM and rsync backups, ip, ss, ssh with keys, ufw default deny.')
K.must('Internals', 'System calls and strace, fork and exec, inodes and links, virtual memory and the OOM killer, namespaces, cgroups and capabilities, the USE method with vmstat and iostat.')
K.must('Troubleshooting', 'Look, narrow down, find the cause, fix it, prevent it. Read the log first, go bottom up for networks, check every folder for permissions, and change one thing at a time.')

T = K.topic(
    slug='course-revision', topic='course-revision',
    step=(3, 'Containers and performance', 'lx-adv-3', 'Build a container from kernel features by hand, then find out why a system is slow with the right tools and method, and finish with a full revision of the course.', 'Expert'),
    title='Course revision: the whole of Unix and Linux in one chapter', short='Course revision', badge='3.3', minutes=45, added='2026-11-24',
    lead='Bring the five parts together: the commands to know by heart, the numbers that come up in every exam, pipelines read step by step, incidents solved with tools from every chapter, and one last lab across the whole course.',
    desc='A one page map of the course, how Linux is examined (school, LPIC-1, Linux+, RHCSA, LFCS), permission digits, umask, exit codes, cron, CIDR and ports, classic pipelines, troubleshooting full disks, failed services, network and permission problems, a mixed final lab, and where to go next.',
    summary='Course map, key numbers, pipelines, incidents, final lab, next steps.',
    keywords=['revision', 'exam', 'LPIC-1', 'RHCSA', 'LFCS', 'Linux+', 'permissions', 'umask', 'exit status', 'pipelines', 'troubleshooting', 'final lab'],
    recap='<p>The course runs from the file tree and the shell, through pipes, text tools and scripts, to running a server and seeing inside the kernel. The same few numbers (permission digits, umask, exit codes, cron fields, CIDR) and pipeline patterns come back again and again. Incidents are solved by looking, narrowing down, finding the cause, fixing it and preventing it, with tools from every part.</p>')
