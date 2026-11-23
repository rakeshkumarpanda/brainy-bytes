# Power tools 4.1: processes, jobs and signals. PID and PPID, fork and exec, process states, /proc, ps, top, pgrep,
# signals (HUP INT QUIT KILL TERM STOP TSTP CONT), kill, pkill, killall, exit status 128+N, job control with &,
# Ctrl+Z, jobs, fg, bg, wait, nohup and disown, nice and renice. Sources: bash(1) JOB CONTROL and SIGNALS sections,
# signal(7), ps(1) and top(1) from procps-ng, kill(1), pgrep(1), nohup(1) and nice(1) from GNU coreutils,
# proc(5), fork(2), execve(2), sched(7).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('what', 'What a process is', f'''
<p>A <b>program</b> is a file on disk, such as <code>/usr/bin/sleep</code>. A <b>process</b> is a program while it runs: it has memory, open files, an owner and a number called the <b>process ID</b> (PID). Every process except the first one was started by another process, its parent, whose number is the <b>PPID</b>.</p>
{steps('How the shell starts a command', [
    'You type sleep 5 and press Enter.',
    'bash calls fork(), which makes a copy of itself. The copy is the child, with a new PID.',
    'The child calls execve() to replace itself with the program /usr/bin/sleep. The PID stays the same.',
    'The parent bash waits. When the child exits, bash collects its exit status into $? and shows the prompt.'])}
{table(['State letter', 'Meaning'], [
    ['<code>R</code>', 'running, or ready to run on a CPU'],
    ['<code>S</code>', 'sleeping, waiting for something (input, a timer, the network)'],
    ['<code>D</code>', 'uninterruptible sleep, usually waiting for a disk'],
    ['<code>T</code>', 'stopped, for example by Ctrl+Z'],
    ['<code>Z</code>', 'zombie: finished, but the parent has not collected its exit status yet']])}
{run('Looking at your own process', """echo "this shell is PID $$"
grep -E '^(Name|State|PPid|Threads)' /proc/$$/status
sleep 30 &
ps -o pid,ppid,stat,comm -p $$,$!
kill $!""", note='$$ is the PID of the current shell and $! the PID of the last background job. Every running process has a folder /proc/PID full of live information from the kernel. The numbers change on every run.')}
{note('The first process, PID 1, is started by the kernel at boot. On most current distributions it is systemd. It adopts orphans: when a parent dies first, its children get PID 1 as their new parent.', 'tip')}
{talk('A program is just a file sitting on the disk. When you run it, the kernel creates a process: a running copy with its own memory, its own open files and a unique number called the process ID. Processes form a family tree. The shell you type in is a process, and every command you start from it becomes its child. Under the hood, bash first makes a copy of itself with the fork system call, and the copy then replaces itself with the new program using exec. At any moment a process is in a state: running, sleeping while it waits for something, stopped, or a zombie, which has finished but whose parent has not yet read its exit status. Linux shows all of this live in the folder slash proc, where every process has a sub folder named after its number.')}
''', kw=['process', 'program', 'PID', 'PPID', 'fork', 'exec', 'process state', 'zombie', '/proc', '$$', 'init', 'systemd'])

K.lesson('watch', 'Watching processes: ps, top and pgrep', f'''
{cmdtable([
    ('ps', 'Processes of this terminal', 'ps'),
    ('ps aux', 'Every process with owner, CPU, memory and state (BSD style options, no dash)', 'ps aux | grep nginx'),
    ('ps -ef', 'Every process with its parent PID (POSIX style)', 'ps -ef | less'),
    ('ps -o COLS', 'Choose the columns', 'ps -o pid,ppid,ni,stat,cmd'),
    ('ps -p PID', 'One process by number', 'ps -p 1 -o comm'),
    ('ps -u USER', 'Processes of one user', 'ps -u www-data'),
    ('top', 'Live view sorted by CPU (q quits, k kills, M sorts by memory)', 'top'),
    ('pgrep NAME', 'PIDs of processes whose name matches', 'pgrep -l nginx'),
    ('pstree', 'The family tree of processes', 'pstree -p')])}
{sample('ps aux on a small web server', 'ps aux', """USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.1 167700 13020 ?        Ss   Nov20   0:09 /sbin/init
root         412  0.0  0.1  15428  8960 ?        Ss   Nov20   0:00 sshd: /usr/sbin/sshd -D
root         905  0.0  0.0  55224  1580 ?        Ss   Nov20   0:00 nginx: master process /usr/sbin/nginx
www-data    1200  0.1  0.1  55888  5652 ?        S    Nov20   2:41 nginx: worker process
learner     2001  0.0  0.0  10012  5300 pts/0    Ss   09:30   0:00 -bash
learner     2405  0.0  0.0   9236  3612 pts/0    R+   09:42   0:00 ps aux""", note='VSZ is virtual memory and RSS the memory really in RAM, both in KiB. A question mark under TTY means a background service with no terminal. In STAT, s marks a session leader and + a process in the foreground.')}
{sample('top, the first lines', 'top', """top - 09:42:10 up 3 days,  2:41,  1 user,  load average: 0.42, 0.35, 0.30
Tasks: 112 total,   1 running, 111 sleeping,   0 stopped,   0 zombie
%Cpu(s):  1.3 us,  0.3 sy,  0.0 ni, 98.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :   7859.4 total,   5120.6 free,   1210.3 used,   1528.5 buff/cache""", note='Load average is the average number of processes running or waiting to run over 1, 5 and 15 minutes. On a 4 core machine a load of 4 means fully busy. us is time in programs, sy in the kernel, id idle and wa waiting for disks.')}
{note('ps aux | grep nginx also finds the grep command itself. pgrep nginx avoids that, and pgrep -a shows the full command lines.', 'tip')}
{talk('ps takes a snapshot of the processes. On its own it shows only the processes of your terminal. ps aux, written without a dash, is the classic way to see everything, with the owner, the share of CPU and memory, the state letter and the full command. ps dash e f shows the same processes with the number of each parent, which helps you follow the family tree. For a live view, top refreshes every few seconds and sorts the busiest processes to the top. Its first lines are worth learning. The load average shows how many processes wanted the CPU over the last one, five and fifteen minutes, and the CPU line shows how much time goes to programs, to the kernel, and to waiting for disks. When you only need a process number, pgrep finds it by name.')}
''', kw=['ps', 'ps aux', 'ps -ef', 'ps -o', 'top', 'htop', 'pgrep', 'pstree', 'load average', 'RSS', 'VSZ', 'STAT'])

K.lesson('signals', 'Signals: asking and forcing processes to stop', f'''
<p>A <b>signal</b> is a small numbered message the kernel delivers to a process. Most signals can be caught by the program, which then runs its own handler, for example to save work before exiting. Two cannot be caught, blocked or ignored: SIGKILL and SIGSTOP.</p>
{table(['Number', 'Name', 'Sent by', 'Default action'], [
    ['1', 'SIGHUP', 'the terminal closing, or kill -HUP', 'end. Many services reload their config on it'],
    ['2', 'SIGINT', 'Ctrl+C', 'end'],
    ['3', 'SIGQUIT', 'Ctrl and the backslash key', 'end and write a core dump'],
    ['9', 'SIGKILL', 'kill -9', 'end at once, cannot be caught'],
    ['15', 'SIGTERM', 'kill (the default)', 'end, the polite request'],
    ['18', 'SIGCONT', 'fg, bg, kill -CONT', 'continue a stopped process'],
    ['19', 'SIGSTOP', 'kill -STOP', 'stop, cannot be caught'],
    ['20', 'SIGTSTP', 'Ctrl+Z', 'stop, can be caught']])}
{cmdtable([
    ('kill PID', 'Send SIGTERM', 'kill 4211'),
    ('kill -9 PID', 'Send SIGKILL, the last resort', 'kill -9 4211'),
    ('kill -HUP PID', 'Send a named signal (also -s HUP or -1)', 'sudo kill -HUP $(pgrep -o nginx)'),
    ('kill -l', 'List signal names and numbers', 'kill -l 9'),
    ('pkill NAME', 'Signal every process whose name matches', 'pkill -u asha firefox'),
    ('killall NAME', 'Signal processes with exactly this name', 'killall -TERM node')])}
{run('Signals and exit statuses', """kill -l | head -3
kill -l 9
sleep 30 & echo "started $!"
kill $!
wait $!; echo "exit status $?"
sleep 30 &
kill -9 $!
wait $!; echo "exit status $?"
kill -l 137""", note='A process killed by signal N ends with exit status 128 + N: 143 for SIGTERM (15) and 137 for SIGKILL (9). kill -l turns such a status back into a name.')}
{steps('Stopping a stuck program the right way', [
    'Try Ctrl+C in its terminal first (SIGINT).',
    'From another terminal, find the PID with pgrep -a NAME, then send kill PID (SIGTERM) and give it a few seconds.',
    'Only if it is still there, use kill -9 PID. It cannot save files or remove lock files, so expect some cleanup.',
    'A process in state D (waiting for a disk) ignores even SIGKILL until the disk answers. Look at the storage, not the process.'])}
{talk('Signals are how processes are told to stop, pause or reload. Pressing control C sends SIGINT to the program in the foreground. The kill command, despite its name, simply sends a signal, and by default it sends SIGTERM, number fifteen, which politely asks the program to finish. A good program catches it, saves its work and exits. Number nine, SIGKILL, is different: the program never sees it, and the kernel removes the process at once. That makes it the last resort, because files may be left half written. SIGHUP, number one, was sent when a modem line hung up, and today many services such as nginx treat it as a request to reload their configuration. When a process is killed by a signal, its exit status is one hundred and twenty eight plus the signal number, so one hundred and forty three means it got SIGTERM.')}
''', kw=['signal', 'kill', 'kill -9', 'SIGTERM', 'SIGKILL', 'SIGINT', 'SIGHUP', 'SIGSTOP', 'SIGCONT', 'Ctrl+C', 'pkill', 'killall', 'exit status 143', '128+N'])

K.lesson('jobs', 'Job control: &, Ctrl+Z, fg, bg and nohup', f'''
<p>bash can run several commands from one terminal. A <b>job</b> is a command started from this shell. Only one job is in the <b>foreground</b>, reading your keyboard. The others run, or wait stopped, in the <b>background</b>.</p>
{cmdtable([
    ('CMD &', 'Start in the background, the prompt returns at once', 'sleep 300 &'),
    ('Ctrl+Z', 'Stop the foreground job (SIGTSTP)', 'press it while vim or a long copy runs'),
    ('jobs', 'List this shell’s jobs (+ current, - previous)', 'jobs -l'),
    ('fg %N', 'Bring job N to the foreground', 'fg %1'),
    ('bg %N', 'Continue a stopped job in the background', 'bg %1'),
    ('kill %N', 'Signal a job by number instead of PID', 'kill %2'),
    ('wait', 'Wait for background jobs to finish', 'wait'),
    ('nohup CMD &', 'Keep running after you log out, output goes to nohup.out', 'nohup ./backup.sh &'),
    ('disown %N', 'Remove a running job from the shell, so logging out does not send it SIGHUP', 'disown %1')])}
{play('lx-jobs')}
{sample('An interactive session', """sleep 300 &
sleep 600
jobs
bg %2
fg %1""", ['[1] 2400', """^Z
[2]+  Stopped                 sleep 600""", """[1]-  Running                 sleep 300 &
[2]+  Stopped                 sleep 600""", '[2]+ sleep 600 &', 'sleep 300'], note='The second sleep ran in the foreground until Ctrl+Z (shown as ^Z) stopped it. bg let it continue in the background, and fg %1 brought the first job forward, so the shell waits for it.')}
{lab('Drive some jobs', [
    ('Start <code>sleep 300</code> in the background.', 'sleep 300 &', [{'cmd': r'sleep\s+300\s*&\s*$'}, {'out': '^\\[1\\] \\d+'}]),
    ('List the jobs of this shell.', 'jobs', [{'cmd': r'^jobs'}, {'out': 'Running\\s+sleep 300'}]),
    ('Stop job 1 with the STOP signal, as Ctrl+Z would.', 'kill -STOP %1', [{'cmd': r'kill\s+-(STOP|19|SIGSTOP|TSTP|20)'}, {'out': 'Stopped'}]),
    ('Let job 1 continue in the background.', 'bg %1', [{'cmd': r'^bg'}, {'out': 'sleep 300 &'}]),
    ('Find the process IDs of nginx without using ps.', 'pgrep nginx', [{'cmd': r'^pgrep'}, {'out': '905'}]),
    ('End job 1 politely with SIGTERM.', 'kill %1', [{'cmd': r'^kill\s+(-TERM\s+|-15\s+)?%1'}, {'out': 'Terminated'}]),
    ('Show the processes of your terminal.', 'ps', [{'cmd': r'^ps'}, {'out': 'bash'}])])}
{note('Closing a terminal sends SIGHUP to its shell, which passes it on to its jobs. Use nohup, disown, or better a terminal multiplexer such as tmux or screen for long work over ssh, so a dropped connection does not kill it.', 'warn')}
{talk('Job control lets one terminal juggle several tasks. Put an ampersand at the end of a command and it starts in the background, so the prompt comes back at once. If a command is already running in the foreground, control Z stops it, and then you choose: bg lets it continue in the background, fg brings it back to the foreground. The jobs command lists everything this shell started, with a plus sign on the current job and a minus on the previous one, and you can refer to jobs as percent one, percent two and so on, even with kill. One danger remains. When you close the terminal or your ssh connection drops, the shell sends the hang up signal to its jobs and they die. nohup makes a command ignore that signal and saves its output in nohup dot out. For long work on a server, most people use tmux or screen, which keep whole sessions alive and let you reconnect later.')}
''', kw=['job control', 'background', 'foreground', '&', 'Ctrl+Z', 'jobs', 'fg', 'bg', 'wait', 'nohup', 'disown', 'tmux', 'screen', 'SIGHUP'])

K.lesson('levels', 'Processes from school to research', f'''
{ladder(
    '<p>Every running program is a process with a number. ps and top show them, kill asks one to stop, and & runs a command in the background so you can keep typing.</p>',
    f'<p>Processes are created by fork() and execve(), reaped by the parent with wait(), and controlled with signals. nice values from -20 (most favoured) to 19 (least) change the share of CPU time: <code>nice -n 10 CMD</code> starts a command politely, <code>renice -n 5 -p PID</code> changes a running one, and only root may lower the value.</p>',
    '<p>Linux schedules threads, not processes: each is a task_struct, and threads are tasks that share memory, made with clone(). Since kernel 6.6 the default scheduler is EEVDF (Earliest Eligible Virtual Deadline First), which replaced CFS and still turns nice values into weights. Process groups and sessions let the terminal driver send Ctrl+C and Ctrl+Z to the whole foreground pipeline. Control groups (cgroups v2) limit CPU, memory and I/O for groups of processes, which is the base of containers and systemd services.</p>',
    '<p>Research on scheduling now targets huge core counts and mixed workloads: sched_ext (merged in Linux 6.12) lets schedulers be written as eBPF programs and loaded at runtime, so new policies can be tested without rebuilding the kernel. Work on memory pressure (PSI, pressure stall information) and on user space OOM killers such as systemd-oomd aims to keep phones and servers responsive under load instead of freezing.</p>')}
{scene('the runaway report', '<p>Users say the server is slow. The engineer runs <code>top</code>, presses P and sees a reporting script at 100% CPU for two hours. <code>pgrep -a report</code> gives PID 7310. <code>kill 7310</code> sends SIGTERM, the script logs "shutting down" and exits after closing its database connection. The fix for tomorrow: run it with <code>nice -n 15</code> so it never slows down the web shop again.</p>')}
{talk('Underneath, Linux schedules tasks. A process is a task with its own memory, and threads are tasks that share memory with each other. The scheduler decides which task runs on which core and for how long. Nice values from minus twenty to plus nineteen act as weights: a nicer process gets a smaller share when the CPU is busy, but still runs when the CPU is free. Since version six point six, Linux uses a scheduler called EEVDF, and since version six point twelve, sched ext even lets engineers write scheduling policies as eBPF programs and load them while the system runs. Control groups put limits on whole groups of processes, and they are the foundation of containers such as Docker. So the simple ps and kill commands you learned sit on top of some of the most studied code in the kernel.')}
''', kw=['nice', 'renice', 'niceness', 'scheduler', 'EEVDF', 'CFS', 'task_struct', 'clone', 'threads', 'process group', 'session', 'cgroups', 'sched_ext', 'PSI'])

K.quiz('e', 'What is a PID?', ['A password ID', 'The number that identifies a running process', 'A program file', 'A disk partition'], 1, 'Process ID.', 'Every process gets a unique process ID.')
K.quiz('e', 'Which key combination sends SIGINT to the program in the foreground?', ['Ctrl+Z', 'Ctrl+C', 'Ctrl+D', 'Ctrl+L'], 1, 'C for cancel.', 'Ctrl+C sends SIGINT.')
K.quiz('e', 'Which command runs sleep 100 in the background?', ['sleep 100 bg', 'bg sleep 100', 'sleep 100 &', 'sleep &100'], 2, 'Trailing symbol.', 'A trailing & starts a background job.')
K.quiz('e', 'Which signal does plain kill PID send?', ['SIGKILL (9)', 'SIGTERM (15)', 'SIGHUP (1)', 'SIGSTOP (19)'], 1, 'The polite one.', 'kill defaults to SIGTERM.')
K.quiz('m', 'A job was stopped with Ctrl+Z. Which command lets it continue without taking over the terminal?', ['fg', 'bg', 'jobs', 'nohup'], 1, 'Background.', 'bg continues a stopped job in the background.')
K.quiz('m', 'Why should kill -9 be the last resort?', ['It is slower', 'The program cannot catch it, so it cannot save work or clean up', 'It needs root', 'It restarts the computer'], 1, 'No handler.', 'SIGKILL cannot be caught.')
K.quiz('m', 'A script reports exit status 137. What happened?', ['It ran out of disk', 'It was killed by SIGKILL (128 + 9)', 'It finished normally', 'It got SIGTERM'], 1, '128 plus the signal.', '137 − 128 = 9, SIGKILL.')
K.quiz('m', 'What does ps -ef show that plain ps does not?', ['Only your terminal', 'Every process, with the parent PID', 'Only root processes', 'Disk usage'], 1, 'e for every, f for full.', 'ps -ef lists all processes with PPID.')
K.quiz('m', 'Which command keeps a job running after you log out, writing to nohup.out?', ['nohup ./job.sh &', 'nice ./job.sh', 'jobs ./job.sh', 'fg ./job.sh'], 0, 'No hang up.', 'nohup ignores SIGHUP.')
K.quiz('h', 'What is a zombie process?', ['A process using 100% CPU', 'A finished process whose parent has not read its exit status', 'A virus', 'A stopped process'], 1, 'State Z.', 'It stays in the table until the parent calls wait().')
K.quiz('h', 'Which nice value gives a process the smallest share of a busy CPU?', ['-20', '0', '10', '19'], 3, 'Nicer means more generous.', '19 is the least favoured.')
K.quiz('h', 'Which two signals can never be caught or ignored?', ['SIGINT and SIGTERM', 'SIGKILL and SIGSTOP', 'SIGHUP and SIGCONT', 'SIGQUIT and SIGTSTP'], 1, 'The kernel enforces them.', 'signal(7): SIGKILL and SIGSTOP cannot be caught, blocked or ignored.')
K.quiz('x', 'On a 4 core server, the load average is 8.0. What does it suggest?', ['The server is idle', 'About twice as many tasks want CPU (or disk) as cores can serve', '8 users are logged in', 'Memory is full'], 1, 'Compare with cores.', 'Load counts runnable and uninterruptible tasks.')

K.calc('e', 'A process was killed by SIGTERM (15). What exit status does the shell report?', '143', '128 plus the signal.', ['128 + 15.', 'The shell adds 128 for a signal death.', eq('143')], check=143)
K.calc('e', 'Exit status 130. Which signal number ended the process?', '2', 'Subtract 128.', ['130 − 128 = 2.', 'Signal 2 is SIGINT.', eq('2 (Ctrl+C)')], check=2)
K.calc('m', 'Load average 6.0 on 4 cores. How many tasks, on average, are waiting beyond what the cores can run?', '2', 'Load minus cores.', ['Cores can run 4 at once.', '6 − 4 = 2.', eq('2 waiting')], check=2)
K.calc('m', 'top shows 12.5 us, 2.5 sy, 0.0 ni, 85.0 id. What percent of CPU time is busy?', '15', 'Everything except idle.', ['Busy = us + sy + ni.', '12.5 + 2.5 + 0.0 = 15.', eq('15%')], check=15)
K.calc('m', 'A machine has 8 GiB of RAM. A process shows %MEM 25.0. About how many MiB is that?', '2048', 'A quarter of 8192 MiB.', ['8 GiB = 8192 MiB.', '25% of 8192.', eq('2048 MiB')], check=2048)
K.calc('h', 'Three background jobs: sleep 20, sleep 50, sleep 35, all started together. After how many seconds does wait return?', '50', 'The longest one.', ['wait with no arguments waits for all jobs.', 'They run at the same time.', eq('max(20, 50, 35) = 50 seconds')], check=50)

K.must('Process', 'A running program. PID and parent PPID, created by fork then exec. States R S D T Z. $$ is this shell, $! the last background job.')
K.must('Watch', 'ps for your terminal, ps aux or ps -ef for all, ps -o to pick columns, top live, pgrep -a NAME for PIDs.')
K.must('Signals', 'kill sends SIGTERM (15). kill -9 SIGKILL cannot be caught. Ctrl+C is SIGINT, Ctrl+Z SIGTSTP. Death by signal N gives status 128 + N.')
K.must('Jobs', 'CMD & background, Ctrl+Z stop, jobs list, fg and bg with %N, wait for all. nohup or tmux for work that must survive logout.')
K.must('Priority', 'nice -n 10 CMD starts politely, renice changes a running process. -20 most favoured, 19 least, only root lowers it.')

T = K.topic(
    slug='processes', topic='processes',
    step=(4, 'Processes and the shell environment', 'lx-power-4', 'See and control running programs with ps, top, signals and job control, then shape your shell with variables, PATH, aliases and startup files.', 'Intermediate'),
    title='Processes, jobs and signals', short='Processes and signals', badge='4.1', minutes=50, added='2026-11-23',
    lead='Find out what is running with ps, top and pgrep, stop programs politely or by force with signals, juggle background jobs with &, Ctrl+Z, fg and bg, and keep work alive after logout.',
    desc='What a process is (PID, PPID, fork and exec, states, /proc), ps aux, ps -ef, ps -o, top and load average, pgrep, signals with kill, pkill and killall, exit status 128+N, job control with &, Ctrl+Z, jobs, fg, bg, wait, nohup and disown, nice and renice, and how the Linux scheduler and cgroups work.',
    summary='PIDs and states, ps and top, kill and signals, background jobs, nohup and nice.',
    keywords=['process', 'ps', 'top', 'kill', 'signal', 'SIGTERM', 'SIGKILL', 'jobs', 'fg', 'bg', 'nohup', 'nice', 'pgrep', 'background job'],
    recap='<p>Every running program is a process with a PID. ps and top show them, signals stop or pause them (kill is TERM, -9 is KILL), and job control moves work between foreground and background.</p>')
