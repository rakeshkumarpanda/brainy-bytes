# System administration 2.2: logs and health checks. The systemd journal and journalctl (-u, -p, -b, -k, --since,
# --until, -g, -f, -o, _COMM=, --disk-usage, --vacuum-size), syslog priorities, rsyslog text files in /var/log,
# auth.log, dpkg.log and apt history, logger, reading logs with grep, awk, sort and uniq, logrotate, dmesg and the OOM
# killer, uptime and load average, free, df and df -i, vmstat. Sources: journalctl(1), journald.conf(5),
# systemd.journal-fields(7), logger(1), rsyslog.conf(5), logrotate(8), dmesg(1), uptime(1), free(1), df(1),
# vmstat(8), proc(5) for /proc/loadavg and /proc/meminfo, RFC 5424 for the severity levels.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('where', 'Where Linux keeps its logs', f'''
<p>Programs report what they do in <b>logs</b>. Modern systems keep two kinds side by side: the <b>systemd journal</b>, a structured store read with journalctl, and plain <b>text files in /var/log</b>, written by rsyslog and by programs themselves.</p>
{table(['Log', 'Holds', 'Read with'], [
    ['the journal (/var/log/journal, or /run/log/journal until the next boot)', 'everything systemd units, the kernel and programs report', '<code>journalctl</code>'],
    ['<code>/var/log/syslog</code> (Debian, Ubuntu), <code>/var/log/messages</code> (RHEL)', 'general system messages, copied from the journal by rsyslog', '<code>less</code>, <code>tail -f</code>, <code>grep</code>'],
    ['<code>/var/log/auth.log</code>, <code>/var/log/secure</code> (RHEL)', 'logins, ssh, sudo, failed passwords', 'root or the adm group'],
    ['<code>/var/log/kern.log</code>, <code>dmesg</code>', 'kernel messages: hardware, drivers, out of memory', '<code>sudo dmesg -T</code>'],
    ['<code>/var/log/dpkg.log</code>, <code>/var/log/apt/history.log</code>', 'every package installed, upgraded or removed', '<code>grep</code>'],
    ['<code>/var/log/nginx/</code>, <code>/var/log/postgresql/</code>', 'logs of single applications', 'the application’s own format']])}
{table(['Priority', 'Number', 'Meaning'], [
    ['emerg', '0', 'the system is unusable'], ['alert', '1', 'act at once'], ['crit', '2', 'critical failure'], ['err', '3', 'error'],
    ['warning', '4', 'something may go wrong'], ['notice', '5', 'normal but worth noting'], ['info', '6', 'information'], ['debug', '7', 'details for developers']])}
{play('lx-journal')}
{run('Text logs on a real Ubuntu system', """ls /var/log | head -12
ls -l /var/log/apt/
grep ' install ' /var/log/dpkg.log | tail -3
grep -A3 '^Start-Date' /var/log/apt/history.log | tail -4""", note='Not every program writes here: this container has no rsyslog, so there is no syslog or auth.log file, and the journal holds those messages instead. term.log belongs to the group adm, the usual group for reading logs. dpkg.log and history.log show exactly what changed and when, which is the first place to look after an update breaks something.')}
{talk('When something goes wrong on a Linux machine, the logs tell you what happened. Today most systems keep two kinds. The systemd journal collects messages from every service, the kernel and many programs, and stores them with extra facts such as the unit name and the priority. You read it with journalctl. Many systems also run rsyslog, which copies messages into plain text files in slash var slash log, such as syslog for general messages and auth dot log for logins, ssh and sudo. Package tools keep their own history in dpkg dot log and apt slash history dot log. Every message has a priority from zero, emergency, to seven, debug, and errors are priority three. Many log files can only be read by root or by members of the group adm. Try the animation to see how a few filters turn a wall of log lines into the handful that explain a problem.')}
''', kw=['logs', '/var/log', 'systemd journal', 'journald', 'rsyslog', 'syslog', 'auth.log', '/var/log/secure', 'kern.log', 'dpkg.log', 'apt history.log', 'log priority', 'adm group'])

K.lesson('journalctl', 'Searching the journal with journalctl', f'''
{cmdtable([
    ('journalctl -u NAME', 'Messages of one unit', 'journalctl -u nginx'),
    ('journalctl -p err', 'Priority err and worse', 'journalctl -p err -b'),
    ('journalctl -b, -b -1', 'This boot, the previous boot (needs a persistent journal)', 'journalctl -b -1 -p warning'),
    ('journalctl --since, --until', 'A time window: today, yesterday, "2026-11-23 09:00", "2 hours ago"', 'journalctl --since "1 hour ago"'),
    ('journalctl -f', 'Follow new messages as they come, like tail -f', 'journalctl -fu nginx'),
    ('journalctl -k', 'Kernel messages only', 'journalctl -k -b'),
    ('journalctl -g PATTERN', 'Messages that match a regular expression', 'journalctl -u ssh -g "Failed password"'),
    ('journalctl _COMM=NAME, -t TAG', 'By program name, by syslog tag', 'journalctl _COMM=sudo'),
    ('journalctl -o json-pretty', 'Show every stored field of each entry', 'journalctl -u ssh -n 1 -o json-pretty'),
    ('journalctl --disk-usage, --vacuum-size=500M', 'Space used, and shrink it', 'sudo journalctl --vacuum-time=30d')])}
{sample('Narrowing the journal down (the build container has no running journald, so this output comes from the practice shell)', """journalctl -u backup
sudo journalctl -p err --since today
sudo journalctl -u ssh -g accepted
sudo journalctl _COMM=sudo""", out=["""Hint: You are currently not seeing messages from other users and the system.
      Users in groups 'adm', 'systemd-journal' can see all messages.
      Pass -q to turn off this notice.
-- No entries --""", """Nov 23 02:30:04 brainy backup.sh[4711]: rsync: [Receiver] mkdir "/mnt/backup/home" failed: No such file or directory (2)
Nov 23 02:30:04 brainy backup.sh[4711]: rsync error: error in file IO (code 11) at main.c(791) [Receiver=3.2.7]
Nov 23 02:30:05 brainy systemd[1]: Failed to start backup.service - Nightly backup.
Nov 23 08:50:00 brainy sudo:     asha : 3 incorrect password attempts ; TTY=pts/1 ; PWD=/home/asha ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow
Nov 23 09:26:00 brainy kernel: Out of memory: Killed process 2261 (java) total-vm:4194304kB, anon-rss:3145728kB, file-rss:0kB, shmem-rss:0kB, UID:1001 pgtables:6400kB oom_score_adj:0""",
    "Nov 23 07:20:00 brainy sshd[3402]: Accepted publickey for learner from 192.0.2.10 port 51515 ssh2: ED25519 SHA256:q2Y7v8dHkP0e3m1t5JZpLr4a9GxT6cUoWbNfK1sQe8A",
    """Nov 23 08:05:00 brainy sudo:  learner : TTY=pts/0 ; PWD=/home/learner ; USER=root ; COMMAND=/usr/bin/apt update
Nov 23 08:06:00 brainy sudo:  learner : TTY=pts/0 ; PWD=/home/learner ; USER=root ; COMMAND=/usr/bin/systemctl restart nginx
Nov 23 08:50:00 brainy sudo:     asha : 3 incorrect password attempts ; TTY=pts/1 ; PWD=/home/asha ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow"""], note='A normal user sees only their own messages. One filter on priority found a failed backup, a user who typed the sudo password wrong three times, and a program killed because memory ran out. Every line of the journal has a time, the host, the program with its process ID, and the message.')}
{note('On some systems the journal lives only in memory (/run/log/journal) and is lost at reboot. Create /var/log/journal, or set Storage=persistent in /etc/systemd/journald.conf, to keep it, so that journalctl -b -1 can show why the last boot crashed.')}
{talk('Journalctl is a search tool for the journal. Without options it prints everything, which is far too much, so you add filters. Dash u picks one unit, such as nginx. Dash p err keeps errors and anything worse. Dash b limits it to the current boot, and dash b minus one to the boot before, which helps after a crash. Since and until set a time window, and they understand words like today and phrases like two hours ago. Dash g searches the text with a regular expression, and dash k shows only kernel messages. Dash f keeps the output open and prints new lines as they arrive, which is perfect while you restart a service in another window. Remember that normal users only see their own messages, so use sudo or join the adm group. And if the journal is kept only in memory, make it persistent, so you can read what happened before the last reboot.')}
''', kw=['journalctl', 'journalctl -u', 'journalctl -p err', 'journalctl -b', 'journalctl --since', 'journalctl -f', 'journalctl -k', 'journalctl -g', '_COMM', 'persistent journal', 'journald.conf', 'vacuum'])

K.lesson('text', 'Reading text logs with grep, awk and friends', f'''
<p>Text logs are lines, so the tools from the power tools section answer most questions. A typical task: who is trying to guess passwords over ssh, and how often.</p>
{run('Count failed ssh logins by address', """cat > auth-sample.log <<'EOF'
Nov 23 06:30:00 web1 sshd[3100]: Invalid user admin from 203.0.113.7 port 40000
Nov 23 06:30:02 web1 sshd[3100]: Failed password for invalid user admin from 203.0.113.7 port 40000 ssh2
Nov 23 06:36:28 web1 sshd[3107]: Failed password for root from 198.51.100.23 port 40211 ssh2
Nov 23 06:42:54 web1 sshd[3114]: Failed password for root from 203.0.113.7 port 40422 ssh2
Nov 23 06:49:03 web1 sshd[3121]: Invalid user test from 192.0.2.200 port 40633
Nov 23 06:49:05 web1 sshd[3121]: Failed password for invalid user test from 192.0.2.200 port 40633 ssh2
Nov 23 06:55:29 web1 sshd[3128]: Failed password for root from 203.0.113.7 port 40844 ssh2
Nov 23 07:20:00 web1 sshd[3402]: Accepted publickey for learner from 192.0.2.10 port 51515 ssh2
EOF
grep -c 'Failed password' auth-sample.log
grep 'Failed password' auth-sample.log | grep -oE 'from [0-9.]+' | sort | uniq -c | sort -rn
grep 'Failed password' auth-sample.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -1
grep -oE 'for (invalid user )?[a-z]+' auth-sample.log | awk '{print $NF}' | sort | uniq -c
awk '$3 >= "06:40:00" && $3 < "07:00:00"' auth-sample.log | wc -l
grep 'Accepted' auth-sample.log | awk '{print $3, $9, "from", $11}'""", note='The address is always the fourth field from the end of a Failed password line, so awk can pick it with $(NF-3) however long the line is. Comparing the time field as text works because the format has a fixed width. One address made most of the attempts, a typical sign of a password guessing robot.')}
{cmdtable([
    ('tail -f FILE, less +F FILE', 'Watch a log grow', 'sudo tail -f /var/log/nginx/access.log'),
    ('zgrep, zcat', 'Search rotated logs that were compressed', 'zgrep "Failed password" /var/log/auth.log.2.gz'),
    ('logger -t TAG MESSAGE', 'Write your own line into the system log, for example from a script', 'logger -t backup -p user.err "disk full"'),
    ('lnav, goaccess', 'Extra tools: a log viewer and a web log report', 'lnav /var/log/syslog')])}
{talk('Text logs are just lines of text, so everything you learned about grep, awk, sort and uniq works on them. A classic job is to find who is trying to guess passwords over ssh. Grep finds the failed password lines, grep dash o pulls out the addresses, and sort, uniq dash c and sort dash r n count them and put the busiest first. Awk can pick fields by number, and dollar N F minus three counts from the end of the line, which works even when lines have different lengths. Tail dash f keeps a log open while it grows. Rotated logs are often compressed, and zgrep searches inside them without unpacking. And when you write your own scripts, the logger command puts your messages into the same system log, with a tag and a priority, so they appear next to everything else.')}
''', kw=['grep logs', 'awk logs', 'count failed logins', 'uniq -c', 'tail -f', 'zgrep', 'logger', 'log analysis', 'ssh brute force', 'NF-3'])

K.lesson('rotate', 'Keeping logs small with logrotate', f'''
<p>Logs grow forever unless something trims them. <b>logrotate</b>, run once a day by a systemd timer or cron, renames the current file, starts a fresh one, compresses old ones and deletes the oldest.</p>
{shape('A logrotate rule in /etc/logrotate.d/myapp', """/var/log/myapp/*.log {
    daily               # or weekly, monthly, or size 100M
    rotate 7            # keep 7 old files
    compress            # gzip old files
    delaycompress       # but leave the newest old file uncompressed
    missingok           # no error if the log is missing
    notifempty          # skip empty logs
    create 0640 myapp adm
    postrotate          # tell the program to reopen its log
        systemctl reload myapp
    endscript
}""", note='Many programs keep writing to the old file after a rename. postrotate makes them reopen the log, and copytruncate is the fallback for programs that cannot.')}
{run('logrotate at work, run as root', """apt-get install -y -qq logrotate >/dev/null 2>&1; logrotate --version | head -1
cd "$(mktemp -d)"
printf 'line 1\\nline 2\\n' > app.log
printf '%s/app.log {\\n    daily\\n    rotate 3\\n    compress\\n    delaycompress\\n    missingok\\n    notifempty\\n    create 0640 root adm\\n}\\n' "$PWD" > app.conf
logrotate -d -f -s state app.conf 2>&1 | grep -E '^(rotating log|  log needs)'
logrotate -s state -f app.conf && ls -l app.log*
echo "line 3" >> app.log
logrotate -s state -f app.conf && ls app.log*""", root=True, note='-d is a dry run that only explains what would happen, and -f forces a rotation now. The create line made a fresh, empty app.log with mode 640 for root and adm. After two rotations there is the fresh app.log, the newest old file app.log.1 kept plain because of delaycompress, and app.log.2.gz. The state file remembers when each log was last rotated.')}
{talk('Log files grow every day, and a full disk can stop a whole server. Logrotate prevents this. Once a day it checks each log against its rules in slash etc slash logrotate dot d. When a log is due, it renames app dot log to app dot log dot one, shifts older files up by one number, compresses them, deletes the oldest beyond the count you chose, and creates a fresh empty file. A rule says how often to rotate, by time or by size, how many old files to keep, and whether to compress them. Because many programs keep writing into the old renamed file, a postrotate script usually tells the program to reopen its log. Test a new rule with logrotate dash d, which only describes what it would do, and dash f to force a rotation now.')}
''', kw=['logrotate', 'log rotation', '/etc/logrotate.d', 'rotate 7', 'compress', 'delaycompress', 'postrotate', 'copytruncate', 'logrotate -d', 'logrotate -f', 'disk full logs'])

K.lesson('health', 'Quick health checks: load, memory, disk and the kernel', f'''
{cmdtable([
    ('uptime', 'Time since boot and the load average over 1, 5 and 15 minutes', 'uptime'),
    ('nproc', 'Number of CPUs. Compare it with the load', 'nproc'),
    ('free -h', 'Memory and swap. Read the available column, not free', 'free -h'),
    ('df -h, df -i', 'Free space and free inodes per file system', 'df -h /var'),
    ('du -sh PATH, du -h --max-depth=1', 'What uses the space', 'sudo du -h --max-depth=1 /var | sort -h'),
    ('vmstat 1 5', 'Every second: running and blocked processes, swap, I/O, CPU', 'vmstat 1 5'),
    ('sudo dmesg -T', 'Kernel ring buffer with readable times: disk errors, USB, out of memory', 'sudo dmesg -T | tail')])}
{run('A one minute health check', """uptime
nproc
cat /proc/loadavg
free -h
df -h / | tail -1
df -i / | tail -1
vmstat 1 3""", note='A load average below the number of CPUs means the CPUs keep up. In free, buff/cache is memory the kernel lends to the file cache and gives back when programs need it, so available is the number that matters. df -i counts inodes, since a disk can be full of tiny files while it still has free bytes. In vmstat the first line is an average since boot, the next ones are live, and wa is time spent waiting for disks.')}
{note('When memory runs out, the kernel’s OOM killer stops a process to save the system. The journal then has a line like “Out of memory: Killed process 2261 (java)”. Find it with <code>sudo journalctl -k -g "out of memory"</code> or <code>sudo dmesg -T | grep -i oom</code>.', 'warn')}
{talk('Before you dig into logs, a quick health check often points to the problem. Uptime shows the load average, the number of processes that want a CPU, averaged over one, five and fifteen minutes. Compare it with nproc, the number of CPUs. A load of four on a four CPU machine means fully busy. Free dash h shows memory, and the available column is what counts, because Linux uses spare memory as a file cache and gives it back when needed. Df dash h shows free disk space, and df dash i shows free inodes, which can run out when there are millions of tiny files. Vmstat prints a line every second with processes, memory, input and output, and CPU use. And dmesg shows kernel messages, such as disk errors or the out of memory killer, which stops a program when memory runs out.')}
''', kw=['uptime', 'load average', 'nproc', 'free -h', 'available memory', 'df -h', 'df -i', 'inodes', 'du -sh', 'vmstat', 'dmesg', 'OOM killer', 'health check'])

K.lesson('practice', 'Practice: investigate an incident in the practice shell', f'''
<p>The practice server had a busy night: password guessing over ssh, a failed backup and a program killed for using too much memory. Use the logs to find out what happened.</p>
{lab('Read the logs like an admin', [
    ('Try to read /var/log/auth.log as yourself.', 'cat /var/log/auth.log', [{'cmd': r'auth\.log'}, {'code': 1}]),
    ('Count the lines with Failed password in auth.log, using sudo.', 'sudo grep -c "Failed password" /var/log/auth.log', [{'out': '^12$'}]),
    ('List the addresses of the failed logins with a count for each, busiest first.', """sudo grep "Failed password" /var/log/auth.log | grep -oE "from [0-9.]+" | sort | uniq -c | sort -rn""", [{'out': '7 from 203\\.0\\.113\\.7'}]),
    ('Show all journal entries of priority err or worse from today.', 'sudo journalctl -p err --since today', [{'out': 'Out of memory'}]),
    ('Show only the kernel messages that mention memory, ignoring case.', 'sudo journalctl -k -g memory', [{'out': 'Killed process 2261'}]),
    ('Find who ran sudo, using the journal field _COMM.', 'sudo journalctl _COMM=sudo', [{'out': 'incorrect password attempts'}]),
    ('Write the message "incident reviewed" into the system log with the tag ops.', 'logger -t ops "incident reviewed"', [{'cmd': r'logger\s+-t\s+ops'}]),
    ('Show the journal entries with the tag ops.', 'sudo journalctl -t ops', [{'out': 'ops: incident reviewed'}])])}
{talk('Now you are the admin on call. The practice server had a busy night. Start by trying to read the auth log without sudo, to see that it is protected. Then count the failed password lines, and list the attacking addresses with a count for each, busiest first. Next ask the journal for every error since today, and narrow the kernel messages down to the one about memory. Find out who used sudo and whether anyone typed the password wrong. Finally, write a note into the system log with logger and a tag, and find it again with journalctl dash t.')}
''', kw=['log lab', 'incident investigation', 'auth.log practice', 'journalctl practice', 'logger practice'])

K.lesson('levels', 'Logs and monitoring from school to research', f'''
{ladder(
    '<p>Logs are the diary of a computer. When something breaks, look at the newest errors first: <code>sudo journalctl -p err -b</code> and the log of the program that failed.</p>',
    '<p>Make the journal persistent, set size limits in journald.conf, and rotate text logs. Ship logs off the machine (rsyslog forwarding, systemd-journal-upload), so an attacker who becomes root cannot erase the trail. Watch disk, memory, load and failed units, and alert before users notice.</p>',
    '<p>Central stacks collect logs and metrics from many machines: the ELK stack (Elasticsearch, Logstash, Kibana) or Grafana Loki for logs, Prometheus with node_exporter and Grafana for metrics, and alerting rules on top. Structured logs (key=value or JSON) are much easier to search than free text. auditd records security events such as file access and commands for compliance.</p>',
    '<p>Observability research and practice join logs, metrics and traces (OpenTelemetry) to follow one request across many services. Studies of large outages, such as the published post-mortems of cloud providers, show that missing or misleading monitoring often delays recovery more than the fault itself. Log parsing research (for example the Drain algorithm and the LogHub data sets) turns free-text lines into templates so machine learning can spot unusual patterns.</p>')}
{scene('the disk that filled up at 3 a.m.', '<p>A web server stopped answering at night. <code>df -h</code> showed / at 100 percent, and <code>du -h --max-depth=1 /var | sort -h</code> pointed at /var/log/myapp, where a debug log had grown to 40 GB because it had no rotation rule. The fix added a logrotate rule with <code>size 500M</code> and <code>rotate 5</code>, set <code>SystemMaxUse=1G</code> for the journal, and added a disk alert at 80 percent so the next problem pages someone hours earlier.</p>')}
{talk('Here is how log work grows with experience. Beginners learn to look at the newest errors first. Professionals make sure logs survive reboots, rotate them so disks never fill up, and send copies to another machine, because an attacker with root could delete local logs. They also watch a few key numbers, such as disk space, memory, load and failed services, and get an alert before users notice a problem. Larger teams collect logs and metrics from all machines in central systems such as the E L K stack, Grafana Loki and Prometheus, and prefer structured logs that are easy to search. At the research level, observability joins logs, metrics and traces to follow a single request through many services, and log parsing algorithms turn millions of free text lines into patterns that machine learning can check for anything unusual.')}
''', kw=['persistent journal', 'log forwarding', 'central logging', 'ELK', 'Loki', 'Prometheus', 'node_exporter', 'Grafana', 'structured logging', 'auditd', 'OpenTelemetry', 'log parsing', 'monitoring alerts'])

K.quiz('e', 'Which command reads the systemd journal?', ['syslog', 'journalctl', 'logread', 'cat /var/journal'], 1, 'Journal control.', 'journalctl.')
K.quiz('e', 'Where are most text log files kept?', ['/etc/log', '/var/log', '/tmp/log', '/usr/log'], 1, 'Variable data.', '/var/log.')
K.quiz('e', 'Which log file holds ssh logins and sudo use on Ubuntu?', ['/var/log/dpkg.log', '/var/log/auth.log', '/var/log/kern.log', '/var/log/boot.log'], 1, 'Authentication.', 'auth.log, or secure on RHEL.')
K.quiz('e', 'Which command shows free memory in readable units?', ['df -h', 'free -h', 'du -h', 'mem -h'], 1, 'Free.', 'free -h.')
K.quiz('m', 'Which option shows only the messages of one service?', ['journalctl -p', 'journalctl -u NAME', 'journalctl -k', 'journalctl -b'], 1, 'Unit.', '-u selects a unit.')
K.quiz('m', 'journalctl -p err shows which priorities?', ['Only err', 'err and everything more serious', 'Everything except err', 'Only warnings'], 1, 'And worse.', 'err, crit, alert, emerg.')
K.quiz('m', 'Which command follows new journal lines as they arrive?', ['journalctl -f', 'journalctl -r', 'journalctl -n', 'journalctl -o'], 0, 'Follow.', '-f follows.')
K.quiz('m', 'What does logrotate do with a log that is due?', ['Deletes it', 'Renames it, starts a new one, compresses and removes old copies', 'Emails it', 'Encrypts it'], 1, 'Rotate.', 'The old copies are numbered and limited.')
K.quiz('m', 'In free -h, which column tells how much memory programs can still get?', ['free', 'available', 'shared', 'total'], 1, 'Available.', 'The cache is given back on demand.')
K.quiz('h', 'The load average is 8.0 on a machine with 4 CPUs. What does it mean?', ['The machine is idle', 'Twice as much work wants CPU time as the CPUs can do', '8 users are logged in', 'Memory is full'], 1, 'Compare with nproc.', 'Load above the CPU count means waiting.')
K.quiz('h', 'df -h shows free space, but writing a file fails with No space left on device. What should you check?', ['free -h', 'df -i for inodes', 'uptime', 'nproc'], 1, 'Many tiny files.', 'Inodes can run out first.')
K.quiz('h', 'Why add postrotate with a reload to a logrotate rule?', ['To compress faster', 'So the program reopens its log instead of writing to the renamed file', 'To send mail', 'It is required syntax'], 1, 'Open file.', 'The program keeps the old file open otherwise.')
K.quiz('h', 'journalctl -b -1 says there is no such boot. What is the likely reason?', ['The disk is broken', 'The journal is kept only in memory', 'You need -u', 'The kernel is old'], 1, 'Persistent storage.', 'Create /var/log/journal or set Storage=persistent.')
K.quiz('x', 'Why ship logs to another machine?', ['To save disk space only', 'So an attacker who gains root cannot erase the evidence', 'journalctl needs it', 'It makes logs faster'], 1, 'Tamper.', 'Remote copies survive a compromise.')

K.calc('e', 'Priorities go from 0 (emerg) to 7 (debug). How many levels does journalctl -p err show?', '4', 'err and more serious.', ['err is 3.', 'Levels 0, 1, 2 and 3.', eq('4 levels')], check=4)
K.calc('e', 'logrotate keeps rotate 7 old files plus the current one. How many files exist at most?', '8', 'Add the current one.', ['7 old files.', 'Plus app.log itself.', eq('7 + 1 = 8')], check=8)
K.calc('m', 'Failed logins: 7 from one address, 3 from another, 2 from a third. What percent came from the busiest address, rounded?', '58', 'Part of the total.', ['The total is 12.', '7 ÷ 12 = 0.583.', eq('58 %')], check=58)
K.calc('m', 'A load average of 3.0 on 4 CPUs. What percent of CPU capacity is wanted?', '75', 'Load divided by CPUs.', ['3 ÷ 4.', 'Times 100.', eq('75 %')], check=75)
K.calc('h', 'A log grows 2 GB a day, rotated daily with rotate 7 and compression that shrinks old files to 10 percent. About how many GB does it use in total?', '3.4', 'One plain, seven compressed.', ['The current file is up to 2 GB.', 'Seven old files at 0.2 GB are 1.4 GB.', eq('2 + 1.4 = 3.4 GB')], check=3.4)
K.calc('h', 'A disk has 16777216 inodes and 16557104 are free. How many are used?', '220112', 'Subtract.', ['Total minus free.', '16777216 − 16557104.', eq('220112')], check=220112)

K.must('Two log systems', 'The journal (journalctl) and text files in /var/log (syslog, auth.log, kern.log, dpkg.log). Many need sudo or the adm group.')
K.must('journalctl filters', '-u unit, -p err, -b boot, --since and --until, -g pattern, -k kernel, -f follow, _COMM=name.')
K.must('Text logs', 'grep, awk, sort, uniq -c and sort -rn answer most questions. zgrep for rotated files, logger to write your own lines.')
K.must('logrotate', 'Rules in /etc/logrotate.d: daily or size, rotate N, compress, postrotate reload. Test with -d, force with -f.')
K.must('Health', 'uptime and nproc for load, free -h available, df -h and df -i, du for big folders, vmstat, dmesg for the kernel and OOM kills.')

T = K.topic(
    slug='logs-health', topic='logs-health',
    step=(2, 'Boot, services and logs', 'lx-admin-2', 'Follow the boot from firmware to login, manage services with systemd, and read the logs to find out what went wrong.', 'Intermediate'),
    title='Logs and health checks: journalctl, /var/log and logrotate', short='Logs and health', badge='2.2', minutes=55, added='2026-11-23',
    lead='Find the lines that explain a problem in the systemd journal and the text logs of /var/log, keep logs from filling the disk with logrotate, and check load, memory, disk and the kernel in a minute.',
    desc='The systemd journal and journalctl filters (-u, -p, -b, --since, -g, -k, -f, _COMM=), syslog priorities, persistent journals, rsyslog files such as syslog and auth.log, dpkg and apt logs, grep and awk on logs, logger, logrotate rules and testing, uptime and load average, free, df and inodes, du, vmstat, dmesg and the OOM killer.',
    summary='The journal and journalctl, text logs in /var/log, log analysis, logrotate, quick health checks.',
    keywords=['journalctl', 'journal', '/var/log', 'syslog', 'auth.log', 'logrotate', 'logger', 'dmesg', 'uptime', 'free', 'df', 'vmstat'],
    recap='<p>The journal, read with journalctl and its filters, and the text files in /var/log record what the system does. grep, awk and uniq turn text logs into answers, logrotate keeps them small, and uptime, free, df, vmstat and dmesg give a quick picture of load, memory, disk and kernel trouble.</p>')
