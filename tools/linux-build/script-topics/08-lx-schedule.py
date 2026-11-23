# Shell scripting 4.2: scheduled jobs. The five crontab fields, lists, ranges, steps, names and the @ shortcuts, the
# day-of-month or day-of-week rule, crontab -e, -l, -r and FILE, the environment cron gives a job (SHELL, PATH, HOME,
# MAILTO), the % rule, logging, /etc/crontab and /etc/cron.d with the user field, run-parts and the cron.daily folders,
# anacron, at, atq, atrm and batch, and systemd timers with OnCalendar, Persistent, RandomizedDelaySec and
# systemd-analyze calendar. Sources: crontab(1) and crontab(5) of Debian cron and of cronie, cron(8), run-parts(8),
# anacron(8) and anacrontab(5), at(1) and atd(8), systemd.timer(5), systemd.time(7), systemd-analyze(1).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('fields', 'cron: a schedule in five fields', f'''
<p>cron is a background service (a daemon) that starts commands at fixed times. Each user has a list of jobs called a <b>crontab</b>. Every line of it holds five time fields and then the command to run.</p>
{shape('One crontab line', """minute  hour  day-of-month  month  day-of-week  command
  30     2         *          *         *      /home/learner/backup.sh""", note='The job starts whenever the clock matches all five fields. A star means any value.')}
{table(['Field', 'Allowed values', 'Example', 'Meaning of the example'], [
    ['minute', '0 to 59', '<code>30</code>', 'at minute 30'],
    ['hour', '0 to 23', '<code>9-17</code>', 'every hour from 9 to 17'],
    ['day of month', '1 to 31', '<code>1,15</code>', 'on the 1st and the 15th'],
    ['month', '1 to 12, or jan to dec', '<code>*/3</code>', 'every third month: 1, 4, 7, 10'],
    ['day of week', '0 to 7 (0 and 7 are both Sunday), or sun to sat', '<code>1-5</code>', 'Monday to Friday']])}
{table(['Symbol', 'Meaning', 'Example'], [
    ['<code>*</code>', 'every value', '<code>* * * * *</code> runs every minute'],
    ['<code>,</code>', 'a list', '<code>0 8,20 * * *</code> runs at 08:00 and 20:00'],
    ['<code>-</code>', 'a range', '<code>0 9-17 * * *</code> runs on the hour from 09:00 to 17:00'],
    ['<code>/</code>', 'a step inside a range or *', '<code>*/15 * * * *</code> runs at minutes 0, 15, 30 and 45'],
    ['<code>@daily</code> and friends', 'shortcuts: @yearly, @monthly, @weekly, @daily, @hourly', '<code>@daily</code> is <code>0 0 * * *</code>'],
    ['<code>@reboot</code>', 'once, when the cron daemon starts', 'start a helper after every boot']])}
{play('lx-cron')}
{note('When both day of month and day of week are restricted, cron runs the job when either one matches. <code>0 0 13 * 5</code> runs on every 13th and on every Friday, not only on Friday the 13th.', 'warn')}
{note('Names work for months and days, such as mon or jan, in any case. Debian cron says in crontab(5) that ranges and lists of names are not allowed, while cronie on Fedora and RHEL accepts them. Numbers such as 1-5 work everywhere.')}
{talk('Many jobs on a server must happen on their own at fixed times, such as a nightly backup, a weekly report, or cleaning old log files every hour. The cron service handles this. It wakes up every minute and checks a list of jobs called a crontab. Each line has five time fields and then a command. The fields are the minute, the hour, the day of the month, the month, and the day of the week. A star means any value. So thirty, two, star, star, star means at two thirty every night. You can list values with commas, give ranges with a dash, and use a slash for steps, so star slash fifteen in the minute field means every fifteen minutes. There are shortcuts too, such as at daily and at hourly. One rule surprises many people. When you set both the day of the month and the day of the week, cron runs the job when either one matches. Type your own schedules into the animation and Pip will list the next times the job would run.')}
''', kw=['cron', 'crontab', 'cron syntax', 'five fields', 'minute hour day month weekday', 'cron step */15', 'cron range', '@daily', '@reboot', '@hourly', 'day of month or day of week', 'cron expression'])

K.lesson('crontab', 'Managing your crontab and the cron environment', f'''
{cmdtable([
    ('crontab -e', 'Edit your crontab in your editor ($VISUAL or $EDITOR). cron checks the lines when you save', 'EDITOR=nano crontab -e'),
    ('crontab -l', 'List your crontab', 'crontab -l > crontab.backup'),
    ('crontab FILE', 'Replace your crontab with the lines in FILE', 'crontab jobs.cron'),
    ('crontab -', 'Replace it with lines read from standard input', '(crontab -l; echo "@daily ~/tidy.sh") | crontab -'),
    ('crontab -r', 'Remove your whole crontab, without asking', 'crontab -l > old.cron && crontab -r'),
    ('sudo crontab -u NAME -l', 'Root can list or edit the crontab of another user', 'sudo crontab -u www-data -l')])}
{sample('Installing and listing a crontab (cron is not installed in the build container, so this output comes from the practice shell, which follows Debian cron)', """cat jobs.cron
crontab jobs.cron
crontab -l
echo "61 * * * * /home/learner/report.sh" | crontab -
crontab -r
crontab -l""", out=["""# m h dom mon dow command
MAILTO=""
30 2 * * * /home/learner/backup.sh >> /home/learner/backup.log 2>&1
*/10 * * * * /usr/bin/flock -n /tmp/sync.lock /home/learner/sync.sh""", "", """# m h dom mon dow command
MAILTO=""
30 2 * * * /home/learner/backup.sh >> /home/learner/backup.log 2>&1
*/10 * * * * /usr/bin/flock -n /tmp/sync.lock /home/learner/sync.sh""", """"-":1: bad minute
errors in crontab file, can't install.""", "", "no crontab for learner"]
       , note='crontab printed nothing when the install worked. Minute 61 is out of range, so cron refused the whole new file and kept the old crontab. crontab -r removed everything at once, so save a copy with crontab -l first.')}
<p>A job does not run in your login shell. cron starts it with a very small environment, and this is the most common reason a script works in the terminal but fails from cron.</p>
{table(['Setting', 'Value cron gives a job', 'What to do'], [
    ['SHELL', '<code>/bin/sh</code>, not bash', 'put <code>#!/bin/bash</code> in scripts, or set <code>SHELL=/bin/bash</code> at the top of the crontab'],
    ['PATH', '<code>/usr/bin:/bin</code>', 'use full paths such as <code>/usr/local/bin/node</code>, or set PATH at the top of the crontab'],
    ['HOME, LOGNAME', 'taken from /etc/passwd', 'no .bashrc or .profile is read, so aliases and exported variables are missing'],
    ['Working folder', 'your home folder', 'use full paths, or <code>cd /srv/app || exit 1</code> first'],
    ['MAILTO', 'output is mailed to the owner of the crontab', '<code>MAILTO=""</code> turns mail off, so redirect output to a log file instead'],
    ['The % sign', 'turned into a new line, and the text after the first % becomes standard input', 'write <code>date +\\%F</code> in a crontab line, or move the command into a script']])}
{run('The same command with and without your login environment', """mkdir -p bin
printf '#!/bin/sh\\necho "hello from my own tool"\\n' > bin/hello
chmod +x bin/hello
PATH="$HOME/bin:$PATH" hello
env -i HOME="$HOME" PATH=/usr/bin:/bin SHELL=/bin/sh sh -c 'echo "PATH is $PATH"; hello; echo "status $?"'
env -i HOME="$HOME" PATH=/usr/bin:/bin sh -c '"$HOME/bin/hello"'
date +%F
printf '%s\\n' 'date +%F >> /home/learner/dates.log' 'date +\\%F >> /home/learner/dates.log'""", note='env -i started a shell with nothing but the variables given, the way cron does. The tool in your own bin folder was not found until the full path was used. The last two lines show the wrong and the right way to write a percent sign in a crontab line.')}
{note('Always redirect output in a cron line, for example <code>>> /var/log/myjob.log 2>&1</code>. Without it the output is mailed, and on a server without mail it is lost, so you never see the error.', 'warn')}
{talk('You manage your own crontab with the crontab command. Crontab dash e opens it in your editor, and cron checks every line when you save. Crontab dash l lists it, and crontab followed by a file name replaces it with the lines in that file. Be careful with crontab dash r, which deletes the whole crontab at once without asking, so keep a copy with crontab dash l first. The biggest surprise for beginners is the environment. A cron job does not run in your login shell. It runs with slash bin slash sh, a short PATH of only slash usr slash bin and slash bin, and none of your aliases or settings from dot bash r c. So use full paths, start scripts with a bash shebang, and always send the output to a log file with two greater than signs and two greater than ampersand one. One more trap: a percent sign in a crontab line means a new line, so write it with a backslash in front, or move the command into a script.')}
''', kw=['crontab -e', 'crontab -l', 'crontab -r', 'install crontab', 'cron environment', 'cron PATH', 'MAILTO', 'cron percent sign', 'cron job not running', 'cron log output', 'bad minute', 'flock in cron'])

K.lesson('system', 'System crontabs, cron.daily and anacron', f'''
<p>Besides the personal crontabs, the system has its own. These files have an extra <b>user</b> field after the five time fields, which says which account runs the command.</p>
{table(['Place', 'Who edits it', 'Format'], [
    ['<code>crontab -e</code> (stored in /var/spool/cron)', 'each user, with the crontab command only', 'five fields, then the command'],
    ['<code>/etc/crontab</code>', 'root, with a normal editor', 'five fields, a user name, then the command'],
    ['<code>/etc/cron.d/NAME</code>', 'packages and root', 'like /etc/crontab, one file per package'],
    ['<code>/etc/cron.hourly</code>, <code>cron.daily</code>, <code>cron.weekly</code>, <code>cron.monthly</code>', 'root, by dropping in executable scripts', 'whole scripts, run by run-parts'],
    ['<code>/etc/cron.allow</code>, <code>/etc/cron.deny</code>', 'root', 'user names allowed or denied to use crontab']])}
{run('Real system crontab files and run-parts', """cat /etc/cron.d/e2scrub_all
mkdir -p daily
printf '#!/bin/sh\\necho "rotating logs"\\n' > daily/10-logs
printf '#!/bin/sh\\necho "cleaning caches"\\n' > daily/20-cache
cp daily/10-logs daily/backup.sh
cp daily/10-logs daily/30-old~
chmod +x daily/*
ls daily
run-parts --test daily
run-parts --report daily""", note='The package file in /etc/cron.d names root as the user before the command. run-parts runs the scripts of a folder in name order. Debian run-parts only accepts names made of letters, digits, dashes and underscores, so backup.sh and 30-old~ were skipped. A dot in the name is the classic reason a script in /etc/cron.daily never runs.')}
<p>On Debian and Ubuntu, /etc/crontab starts the cron.hourly folder at minute 17 of every hour and the daily, weekly and monthly folders at 06:25, 06:47 and 06:52, unless anacron is installed, which then takes over the last three.</p>
{shape('An anacron line in /etc/anacrontab', """period-in-days  delay-in-minutes  job-name      command
      1               5           cron.daily    run-parts --report /etc/cron.daily
      7              10           cron.weekly   run-parts --report /etc/cron.weekly""", note='anacron remembers the last run of each job in /var/spool/anacron. If the computer was off at the planned time, the job runs soon after the next start, after the delay.')}
{talk('Besides each user’s own crontab, Linux has system wide schedules. The file slash etc slash crontab and the files in slash etc slash cron dot d look like normal crontab lines with one extra field after the five time fields, the name of the user who runs the command. Packages drop their jobs into cron dot d, as you saw with a real file from this computer. Simpler still are the folders cron dot hourly, cron dot daily, cron dot weekly and cron dot monthly. You put an executable script there and a tool called run parts runs every script in the folder in name order. Watch out for file names, because on Debian run parts skips names with a dot, so a script called backup dot s h is silently ignored. Cron assumes the computer is always on. Anacron is for laptops and desktops that are often switched off. It remembers when each daily, weekly or monthly job last ran, and runs it soon after the next start if a run was missed.')}
''', kw=['/etc/crontab', '/etc/cron.d', 'cron.daily', 'cron.hourly', 'run-parts', 'run-parts skips dot', 'anacron', 'anacrontab', 'cron.allow', 'cron.deny', 'system crontab user field'])

K.lesson('at', 'Run once later: at, atq, atrm and batch', f'''
{cmdtable([
    ('at TIME', 'Read commands from standard input and run them once at TIME', 'echo "./report.sh" | at 23:00'),
    ('at -f FILE TIME', 'Take the commands from a file', 'at -f deploy.sh now + 2 hours'),
    ('atq (or at -l)', 'List your waiting jobs', 'atq'),
    ('atrm N (or at -r N)', 'Remove job number N', 'atrm 4'),
    ('at -c N', 'Show the full script of job N, including the saved environment', 'at -c 4 | tail -3'),
    ('batch', 'Run the commands when the system load is low (below 1.5 by default)', 'echo "make all" | batch')])}
{table(['Time format', 'Means'], [
    ['<code>now + 10 minutes</code>', 'in 10 minutes. Units: minutes, hours, days, weeks'],
    ['<code>16:30</code> or <code>4:30pm</code>', 'the next 16:30, today or tomorrow'],
    ['<code>noon</code>, <code>midnight</code>, <code>teatime</code>', '12:00, 00:00 and 16:00'],
    ['<code>9am tomorrow</code>', 'tomorrow at 09:00'],
    ['<code>10:00 2026-12-24</code>', 'a full date. at(1) lists more forms']])}
{sample('Queueing, listing and removing jobs (at is not installed in the build container, so this output comes from the practice shell, which follows the at package)', """echo "uptime >> /home/learner/load.log" | at now + 5 minutes
at -f nightly.sh teatime tomorrow
atq
atrm 1
atq""", out=["""warning: commands will be executed using /bin/sh
job 1 at Mon Nov 23 09:35:00 2026""", """warning: commands will be executed using /bin/sh
job 2 at Tue Nov 24 16:00:00 2026""", """1	Mon Nov 23 09:35:00 2026 a learner
2	Tue Nov 24 16:00:00 2026 a learner""", "", """2	Tue Nov 24 16:00:00 2026 a learner"""], note='at always runs the job with /bin/sh. Each job gets a number, and the letter a in atq is the queue. batch jobs go to queue b.')}
{note('Unlike cron, at keeps the working folder, the umask and almost all environment variables from the moment you queued the job. Output is mailed to you, so redirect it to a file when the system has no mail.')}
{talk('Cron is for jobs that repeat. For a job that should run only once, later, use at. You type at and a time, such as at now plus ten minutes, at four thirty p m, or at nine a m tomorrow, and give it the commands on standard input, for example with echo and a pipe, or from a file with dash f. At answers with a job number. A t q lists the waiting jobs and a t r m with a number removes one. The command batch is similar, but instead of a time it waits until the system is not busy, which suits heavy work such as a big compile. A nice detail is that at remembers your current folder and your environment variables from the moment you queued the job, so it behaves much more like your terminal than cron does.')}
''', kw=['at command', 'run once later', 'atq', 'atrm', 'at -f', 'batch', 'at now + minutes', 'teatime', 'at -c', 'atd'])

K.lesson('timers', 'systemd timers: the modern scheduler', f'''
<p>On systems that use systemd, a <b>timer</b> unit can start a <b>service</b> unit on a schedule. It takes two small files instead of one line, but gives you logs, missed-run catch up, random delays and dependencies.</p>
{shape('backup.service and backup.timer in /etc/systemd/system', """# backup.service: what to run
[Unit]
Description=Nightly backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh

# backup.timer: when to run it
[Unit]
Description=Run the nightly backup

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true
RandomizedDelaySec=10min

[Install]
WantedBy=timers.target""", note='The timer starts the service with the same name. Persistent=true runs a missed job at the next boot, as anacron does. RandomizedDelaySec spreads the start over up to 10 minutes, so many servers do not all start at once.')}
{table(['Timer setting', 'Meaning'], [
    ['<code>OnCalendar=Mon..Fri 09:00</code>', 'calendar times, written as weekday year-month-day hour:minute:second'],
    ['<code>OnCalendar=daily</code>', 'shortcuts: minutely, hourly, daily, weekly, monthly, yearly, quarterly'],
    ['<code>OnBootSec=5min</code>', '5 minutes after the computer starts'],
    ['<code>OnUnitActiveSec=1h</code>', '1 hour after the service last started, so it repeats'],
    ['<code>Persistent=true</code>', 'catch up a run that was missed while the computer was off'],
    ['<code>AccuracySec=1s</code>', 'how exact the start time must be. The default is 1 minute']])}
{run('Check calendar expressions before you use them (real systemd-analyze, counting from Monday 23 November 2026, 09:30 UTC)', """systemd-analyze calendar --base-time='2026-11-23 09:30:00 UTC' --iterations=3 'Mon..Fri 09:00' | grep -v 'From now'
systemd-analyze calendar --base-time='2026-11-23 09:30:00 UTC' --iterations=3 '*:0/15' weekly | grep -v 'From now'
systemd-analyze calendar --base-time='2026-11-23 09:30:00 UTC' --iterations=3 'Sat *-*-1..7 03:00' | grep -v 'From now'""", note='systemd-analyze shows the normalized form and the next start times, so you can test a schedule safely. The last one means the first Saturday of every month, which is hard to write in cron because of the either rule for day fields.')}
{cmdtable([
    ('sudo systemctl daemon-reload', 'Read new or changed unit files', 'sudo systemctl daemon-reload'),
    ('sudo systemctl enable --now NAME.timer', 'Start the timer now and at every boot', 'sudo systemctl enable --now backup.timer'),
    ('systemctl list-timers', 'All timers with their next and last run', 'systemctl list-timers --all'),
    ('journalctl -u NAME.service', 'The output and logs of every run', 'journalctl -u backup.service --since today'),
    ('sudo systemctl start NAME.service', 'Run the job once by hand, to test it', 'sudo systemctl start backup.service'),
    ('systemctl --user ...', 'Timers for your own account, in ~/.config/systemd/user', 'systemctl --user enable --now notes.timer')])}
{talk('Most modern Linux systems use systemd, and systemd has its own scheduler called timers. Instead of one crontab line you write two small files. A service file says what to run, and a timer file with the same name says when. The when is written with OnCalendar, for example Monday to Friday at nine o’clock, or simply daily. Timers have useful extras. Persistent equals true runs a job that was missed while the computer was off. RandomizedDelaySec adds a small random wait so a thousand servers do not all hit the backup server at the same second. Every run is logged, so journalctl dash u with the service name shows exactly what happened. Before you trust a schedule, test it with systemd analyze calendar, which prints the next times it would fire. Then reload systemd, enable the timer, and check it with systemctl list timers.')}
''', kw=['systemd timer', 'OnCalendar', 'Persistent=true', 'RandomizedDelaySec', 'OnBootSec', 'OnUnitActiveSec', 'systemd-analyze calendar', 'systemctl list-timers', 'timers.target', 'journalctl -u', 'cron vs systemd timer'])

K.lesson('levels', 'Scheduled jobs from school to research', f'''
{ladder(
    '<p>cron runs jobs again and again at fixed times, written as five fields: minute, hour, day of month, month and day of week. at runs a job once, later. Always use full paths and send the output to a log file.</p>',
    '<p>Prefer one script per job, with set -euo pipefail, a lock with flock -n so runs never overlap, and output redirected with <code>>> log 2>&1</code>. Remember the small environment, the % rule, the either rule for day fields, and that crontab -r removes everything. anacron or Persistent=true catches runs missed while the machine was off.</p>',
    '<p>cron uses the local time zone of the system, so a job set inside the hour that summer time skips or repeats needs care. cron(8) explains how your cron handles such clock changes, and many teams keep servers on UTC to avoid the question. systemd timers add RandomizedDelaySec against the thundering herd, where many machines start the same job at the same moment, and AccuracySec lets systemd group wake ups to save power. Monitoring a job means checking that it ran, not only that it did not fail, for example with a heartbeat that the last step sends.</p>',
    '<p>Distributed schedulers such as Kubernetes CronJobs keep the cron syntax but add a concurrency policy (Allow, Forbid or Replace) and a deadline for late starts. Workflow engines such as Apache Airflow describe jobs as graphs with dependencies, retries and backfills of missed intervals. Research on large clusters, such as Google’s Borg papers, studies how batch jobs with flexible start times fill the gaps left by services that must answer at once.</p>')}
{scene('the report that ran at the wrong time', '<p>A team scheduled <code>0 0 1-7 * 1</code>, hoping for a report on the first Monday of each month. It ran on the 1st to the 7th of every month and on every Monday, because cron runs the job when either day field matches. The fix keeps <code>0 0 * * 1</code> and adds <code>[ "$(date +\\%d)" -le 07 ] || exit 0</code> at the start, or moves the job to a timer with <code>OnCalendar=Mon *-*-1..7 00:00</code>, which systemd-analyze confirms before it goes live.</p>')}
{talk('Here is the bigger picture on scheduled jobs. A good scheduled job is a small script that stops on errors, takes a lock with flock so two copies never overlap, and writes everything to a log. Cron works in the local time zone, so a job planned inside the hour that changes for summer time needs care, which is one reason many teams run servers on U T C. When thousands of machines run the same job, a random delay spreads the load, and systemd timers have this built in. Checking that a job succeeded is not enough. You also need an alert when it did not run at all, which is often done with a heartbeat message from the last step. At large scale, Kubernetes CronJobs keep the familiar cron syntax and add rules for overlapping runs, and workflow tools such as Apache Airflow handle dependencies between jobs, retries and catching up on missed runs.')}
''', kw=['cron best practices', 'flock -n cron', 'daylight saving cron', 'UTC servers', 'thundering herd', 'heartbeat monitoring', 'Kubernetes CronJob', 'Apache Airflow', 'first Monday of month cron'])

K.lesson('practice', 'Practice: schedule jobs in the practice shell', f'''
<p>The practice shell below has its own crontab and at commands. They check your lines the way Debian cron does and keep the jobs, but nothing really runs at the chosen time.</p>
{lab('Schedule a backup and a one-off reminder', [
    ('Write a crontab line into the file jobs.cron that runs $HOME/backup.sh every day at 02:30.', 'echo "30 2 * * * $HOME/backup.sh" > jobs.cron', [{'has': ['jobs.cron', '30 2 * * * ']}]),
    ('Install jobs.cron as your crontab.', 'crontab jobs.cron', [{'exists': '/var/spool/cron/crontabs/learner'}]),
    ('List your crontab to check it.', 'crontab -l', [{'cmd': r'crontab\s+-l'}, {'out': '30 2'}]),
    ('Try to install a line with minute 75 from standard input, and read the error.', 'echo "75 * * * * date" | crontab -', [{'out': 'bad minute'}]),
    ('Queue the command date to run once in 10 minutes with at.', 'echo date | at now + 10 minutes', [{'cmd': r'\bat\s+now\s*\+\s*10\s*min'}]),
    ('List the waiting at jobs.', 'atq', [{'cmd': r'^\s*(atq|at\s+-l)\b'}, {'out': 'learner'}]),
    ('Remove job 1 from the queue.', 'atrm 1', [{'cmd': r'^\s*(atrm|at\s+-[rd])\s+1\b'}]),
    ('Remove your whole crontab.', 'crontab -r', [{'gone': '/var/spool/cron/crontabs/learner'}, {'cmd': r'crontab\s+-r'}])])}
{talk('Now it is your turn. The practice shell has its own crontab and at commands that check your lines exactly like Debian cron, although nothing really runs later. First write a crontab line into a file with echo, install it with crontab and the file name, and list it with crontab dash l. Then try a broken line on purpose and read the error, so you know what it looks like. After that, queue a one off job with at, list the queue with a t q, and remove the job with a t r m. Finally, remove the whole crontab with crontab dash r.')}
''', kw=['practice cron', 'crontab exercise', 'at exercise', 'install crontab', 'atq atrm practice'])

K.quiz('e', 'Which field comes first in a crontab line?', ['hour', 'minute', 'day of week', 'month'], 1, 'Smallest unit first.', 'minute hour day-of-month month day-of-week.')
K.quiz('e', 'What does <code>30 2 * * *</code> mean?', ['Every 30 minutes', 'At 02:30 every day', 'On 30 February', 'At 30:02'], 1, 'Minute 30, hour 2.', 'Every day at 02:30.')
K.quiz('e', 'Which command lists your crontab?', ['crontab -e', 'crontab -l', 'crontab -r', 'cron -list'], 1, 'l for list.', 'crontab -l prints it.')
K.quiz('e', 'Which command runs a job only once, later?', ['cron', 'at', 'watch', 'sleep'], 1, 'At a time.', 'at queues a one-off job.')
K.quiz('m', 'What does <code>*/15</code> in the minute field mean?', ['Minute 15 only', 'Minutes 0, 15, 30 and 45', 'Every 15 hours', '15 times a minute'], 1, 'A step.', 'Steps through 0 to 59 by 15.')
K.quiz('m', 'Which day-of-week values mean Sunday?', ['1 only', '0 and 7', '6 and 7', '7 only'], 1, 'Two values.', 'Both 0 and 7 are Sunday.')
K.quiz('m', 'A script works in the terminal but not from cron, with "command not found". The likely cause?', ['cron is broken', 'cron uses a short PATH of /usr/bin:/bin', 'The script is too long', 'cron needs sudo'], 1, 'The environment.', 'Use full paths or set PATH.')
K.quiz('m', 'Why can <code>date +%F</code> break inside a crontab line?', ['date is not allowed', 'cron turns % into a new line', 'cron has no date', 'F is a bad option'], 1, 'Percent is special.', 'Write a backslash before %, or use a script.')
K.quiz('m', 'What extra field do /etc/crontab and /etc/cron.d files have?', ['A password', 'The user that runs the command', 'The year', 'A priority'], 1, 'Whose job.', 'A user name after the five time fields.')
K.quiz('m', 'Why might /etc/cron.daily/backup.sh never run on Debian?', ['Daily is too often', 'run-parts skips names that contain a dot', 'It must be in cron.d', 'It needs a .cron ending'], 1, 'The name.', 'Only letters, digits, - and _ are accepted.')
K.quiz('h', 'What does <code>0 0 13 * 5</code> do?', ['Runs only on Friday the 13th', 'Runs on every 13th and on every Friday', 'Never runs', 'Runs on 5 March'], 1, 'Two day fields.', 'cron uses either one when both are set.')
K.quiz('h', 'Which tool catches up jobs missed while a laptop was switched off?', ['atq', 'anacron', 'crontab -r', 'run-parts'], 1, 'Not always on.', 'anacron remembers the last runs.')
K.quiz('h', 'In a systemd timer, what does Persistent=true do?', ['Keeps the service running', 'Runs a missed start at the next boot', 'Makes the timer survive deletion', 'Turns off logging'], 1, 'Missed runs.', 'It catches up after downtime.')
K.quiz('h', 'Which command shows the next times an OnCalendar expression fires?', ['systemctl cat', 'systemd-analyze calendar', 'journalctl -u', 'crontab -l'], 1, 'Analyze.', 'systemd-analyze calendar EXPR.')
K.quiz('x', 'Which line stops two runs of a cron job from overlapping?', ['<code>*/5 * * * * nice ./sync.sh</code>', '<code>*/5 * * * * flock -n /tmp/sync.lock ./sync.sh</code>', '<code>*/5 * * * * ./sync.sh &amp;</code>', '<code>*/5 * * * * at now ./sync.sh</code>'], 1, 'A lock.', 'flock -n exits if the lock is taken.')

K.calc('e', 'How many times a day does <code>0 * * * *</code> run?', '24', 'Minute 0 of every hour.', ['It runs once an hour.', 'There are 24 hours.', eq('24')], check=24)
K.calc('e', 'How many times an hour does <code>*/10 * * * *</code> run?', '6', 'Minutes 0, 10, 20, 30, 40, 50.', ['Count the steps from 0 to 59.', '0, 10, 20, 30, 40, 50.', eq('6')], check=6)
K.calc('m', 'How many times a day does <code>*/15 9-17 * * *</code> run?', '36', '9 hours, 4 times each.', ['Hours 9 to 17 are 9 hours.', 'Each hour has minutes 0, 15, 30, 45.', eq('9 × 4 = 36')], check=36)
K.calc('m', 'How many times a week does <code>0 8,20 * * 1-5</code> run?', '10', 'Twice a day, five days.', ['8:00 and 20:00 is 2 a day.', 'Monday to Friday is 5 days.', eq('2 × 5 = 10')], check=10)
K.calc('h', 'In a 30-day month starting on a Monday, how many days does <code>0 0 1-7 * 1</code> run?', '11', 'Either rule.', ['Days 1 to 7 give 7 days.', 'Mondays are 1, 8, 15, 22 and 29, and day 1 is counted already, so 4 more.', eq('7 + 4 = 11')], check=11)
K.calc('h', 'A timer has RandomizedDelaySec=10min and OnCalendar=02:30. What is the latest start, in minutes after 02:00?', '40', 'Up to 10 minutes late.', ['The planned start is 02:30.', 'The delay adds up to 10 minutes.', eq('30 + 10 = 40')], check=40)

K.must('Five fields', 'minute hour day-of-month month day-of-week, then the command. * any, , list, - range, / step, @daily and @reboot shortcuts.')
K.must('Either rule', 'When both day of month and day of week are set, cron runs the job when either matches.')
K.must('crontab', 'crontab -e edits, -l lists, FILE installs, -r removes everything without asking. A bad line refuses the whole file.')
K.must('Environment', 'SHELL=/bin/sh, PATH=/usr/bin:/bin, no .bashrc. Use full paths, redirect output to a log, escape % in crontab lines.')
K.must('Other schedulers', 'at, atq and atrm for one-off jobs, anacron for machines that are switched off, systemd timers with OnCalendar and Persistent=true.')

T = K.topic(
    slug='scheduling', topic='scheduling',
    step=(4, 'Robust and scheduled scripts', 'lx-script-4', 'Write scripts that fail safely, clean up after themselves, are easy to debug, and run on a schedule with cron, at and systemd timers.', 'Advanced'),
    title='Scheduled jobs: cron, at and systemd timers', short='Scheduled jobs', badge='4.2', minutes=55, added='2026-11-23',
    lead='Run scripts on a schedule with cron and read every crontab field, avoid the traps of the cron environment, use the system cron folders and anacron, queue one-off jobs with at, and write systemd timers checked with systemd-analyze.',
    desc='The five crontab fields with lists, ranges, steps, names and @ shortcuts, the either rule for day fields, crontab -e, -l, -r and FILE, the cron environment with SHELL, PATH and MAILTO, the % rule and logging, /etc/crontab and /etc/cron.d with the user field, run-parts and its name rules, anacron, at, atq, atrm and batch, and systemd timers with OnCalendar, Persistent, RandomizedDelaySec, list-timers and systemd-analyze calendar.',
    summary='crontab fields and rules, the cron environment, system cron folders and anacron, at and batch, systemd timers.',
    keywords=['cron', 'crontab', 'at', 'atq', 'batch', 'anacron', 'run-parts', 'systemd timer', 'OnCalendar', 'systemd-analyze'],
    recap='<p>A crontab line has five time fields and a command, and day fields use the either rule. cron gives jobs a small environment, so use full paths and log the output. System cron folders run through run-parts, anacron catches missed runs, at runs a job once, and systemd timers add logs and catch up, tested with systemd-analyze calendar.</p>')
