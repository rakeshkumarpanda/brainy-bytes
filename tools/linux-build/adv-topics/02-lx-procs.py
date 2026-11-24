# Internals and advanced 1.2: processes inside. fork, execve, exit and wait, copy on write, why builtins exist, the
# process tree and PID 1, exit status and wait status, process states (R, S, D, T, Z, I), zombies and orphans,
# subreapers, threads (clone, LWP, /proc/PID/task), and the scheduler: nice, priorities, scheduling policies (chrt)
# and CPU affinity (taskset).
# Sources: fork(2), clone(2), execve(2), wait(2), waitpid(2), _exit(2), exit(3), credentials(7), proc(5) (stat and
# status), ps(1) (PROCESS STATE CODES), pstree(1), prctl(2) (PR_SET_CHILD_SUBREAPER), sched(7), nice(1), chrt(1),
# taskset(1), pthreads(7), the kernel documentation of the EEVDF scheduler (Linux 6.6), bash(1) (EXIT STATUS).
# Real boxes compile a small C program with gcc and run Python, ps and unshare in the build container. Zombies and
# orphans are shown inside a private PID namespace (unshare --pid --fork --mount-proc), so ps shows only the demo.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('born', 'fork, exec, exit and wait', f'''
<p>Every process except the very first is made by another process. Unix splits this into two steps that you can combine freely: <b>fork</b> copies the running process, and <b>execve</b> replaces the program inside a process with a new one.</p>
{steps('The life of one command', [
    '<b>fork()</b>: the kernel makes a child that is a copy of the parent, with a new PID. fork returns twice: 0 in the child and the child’s PID in the parent. On Linux the system call behind it is clone.',
    '<b>execve(path, argv, envp)</b>: the child loads a new program. The PID, the parent, the open file descriptors and the current folder stay. Memory, code and signal handlers are replaced.',
    '<b>exit(status)</b>: the program ends. The kernel frees almost everything but keeps the exit status for the parent.',
    '<b>wait()</b> or waitpid(): the parent collects the status, and only then does the process disappear completely. In bash the status ends up in <code>$?</code>.'])}
{play('lx-fork')}
{run('fork, exec and wait in a small C program', """cat > forkdemo.c <<'EOF'
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    printf("parent %d starts\\n", getpid());
    fflush(stdout);
    pid_t pid = fork();
    if (pid == 0) {
        printf("child %d, my parent is %d\\n", getpid(), getppid());
        fflush(stdout);
        execlp("ls", "ls", "/nope", (char *)NULL);
        _exit(127);
    }
    int status;
    waitpid(pid, &status, 0);
    printf("child %d exited with status %d\\n", pid, WEXITSTATUS(status));
    return 0;
}
EOF
gcc -Wall -o forkdemo forkdemo.c
./forkdemo""", note='fork returns 0 in the child, which prints its own PID and its parent and then runs execlp, a libc helper for execve that searches PATH. ls fails because /nope does not exist and exits with 2. The line after execlp only runs if exec itself fails (127 is what shells use for “command not found”). The parent waits for exactly this child and reads its status with WEXITSTATUS. fflush matters: without it, text still sitting in the output buffer would be copied by fork and could be printed twice.')}
{note('This split is why redirections and pipes are easy in Unix. Between fork and exec, the child can close and reopen file descriptors (dup2, as in chapter 1.1), change folder, drop privileges or set limits, and the new program simply starts with that setup.', 'tip')}
{talk('Every process on Linux is made by another one, in two steps. Fork makes a copy of the running process with a new process id. Fork returns twice: zero in the child, and the child’s process id in the parent. Then the child calls exec, which loads a new program into the same process. The process id, the parent and the open files stay. When the program ends, it calls exit with a status, and the parent collects that status with wait. Bash does exactly this for every external command you type, and puts the status in dollar question mark. In the C demo you can see all four steps, and ls failing with status two.')}
''', kw=['fork', 'clone', 'execve', 'exec', 'exit', 'wait', 'waitpid', 'WEXITSTATUS', 'exit status', 'process creation', 'child process', 'parent process', 'copy on write', 'execlp', 'fflush', 'shell builtin'])

K.lesson('tree', 'The process tree, PID 1 and exit statuses', f'''
{cmdtable([
    ('pstree, pstree -p', 'The process tree, with PIDs', 'pstree -p $$'),
    ('ps -o pid,ppid,stat,cmd', 'Choose the columns, here the parent and the state', 'ps -o pid,ppid,stat,cmd'),
    ('ps -ef --forest', 'All processes, children indented under their parents', 'ps -ef --forest'),
    ('echo $?', 'Exit status of the last command', 'false; echo $?'),
    ('echo ${{PIPESTATUS[@]}}', 'Exit statuses of every command in the last pipeline', 'false | true; echo ${{PIPESTATUS[@]}}')])}
{table(['Status', 'Meaning'], [
    ['0', 'success'],
    ['1 to 125', 'the program’s own error codes (grep: 1 no match, 2 error)'],
    ['126', 'found but could not be run (no x permission)'],
    ['127', 'command not found'],
    ['128 + N', 'killed by signal N: 130 is Ctrl+C (SIGINT, 2), 137 is SIGKILL (9), 143 is SIGTERM (15)']])}
{run('A tree, and statuses from signals', """bash -c 'sleep 30 & sleep 30 & pstree -p $$ | sed -E "s/[0-9]+/N/g"; kill %1 %2'
sleep 30 &
kill -TERM $!
wait $!
echo "status $?"
sleep 30 &
kill -KILL $!
wait $!
echo "status $?"
bash -c 'exit 300'
echo "status $?\"""", note='pstree draws the inner bash with its children: the two sleeps and the two sides of the pipe, pstree and sed (which hides the process ids, as they change every run). When its output is not a terminal, pstree draws with plain ASCII characters instead of lines. A process killed by a signal has no exit code of its own, so the shell reports 128 plus the signal number: 143 for SIGTERM and 137 for SIGKILL. A status is only 8 bits, so exit 300 becomes 300 − 256 = 44.')}
{note('PID 1 is special. On Ubuntu it is systemd, which starts every service. The kernel never lets PID 1 die (if it exits, the kernel panics), it does not get signals it has no handler for, and it becomes the parent of every orphaned process. In a container, your own program may be PID 1, which is why containers use a small init such as tini or docker run --init.', 'warn')}
{talk('All processes form one tree. At the top is process one, systemd on Ubuntu, which the kernel starts at boot. Every other process has a parent, shown as P P I D, and pstree draws the whole family. When a process ends, it leaves an exit status for its parent. Zero means success and anything else is an error. Some numbers have fixed meanings: one hundred twenty seven means command not found, and one hundred twenty eight plus a signal number means the process was killed by that signal. So one hundred thirty seven means it got SIGKILL, number nine, which is what you see when the kernel kills a program that uses too much memory.')}
''', kw=['process tree', 'pstree', 'PPID', 'PID 1', 'systemd PID 1', 'init', 'ps -ef --forest', 'exit status', '$?', 'PIPESTATUS', '126', '127', '128+N', 'exit code 137', 'exit code 143', 'tini', 'docker run --init'])

K.lesson('states', 'Process states, zombies and orphans', f'''
{table(['STAT', 'State', 'What it means'], [
    ['R', 'running or runnable', 'on a CPU now, or waiting in the run queue for one'],
    ['S', 'interruptible sleep', 'waiting for something: input, a timer, a network packet. Most processes, most of the time'],
    ['D', 'uninterruptible sleep', 'waiting for I/O inside the kernel, usually a disk or a network file system. Cannot be killed until the I/O ends'],
    ['T', 'stopped', 'paused by SIGSTOP or Ctrl+Z, or held by a debugger'],
    ['Z', 'zombie', 'has exited, but the parent has not called wait yet'],
    ['I', 'idle', 'an idle kernel thread'],
    ['extra letters', '<code>s</code> session leader, <code>l</code> has threads, <code>+</code> in the foreground, <code>&lt;</code> high priority, <code>N</code> low priority', '']])}
{run('Make a zombie and an orphan, in a private PID namespace', """unshare --pid --fork --mount-proc bash -c '
bash -c "sleep 1 & exec sleep 4" &
sleep 2
ps -o pid,ppid,stat,args | cut -c1-44
wait
bash -c "sleep 3 &"
ps -o pid,ppid,stat,args | cut -c1-44
true'""", note='unshare gives the demo its own PID namespace, so the outer bash is PID 1 here and ps sees only the demo. The inner bash starts sleep 1 in the background and then replaces itself with sleep 4 (exec), a program that never calls wait. When sleep 1 exits, it stays behind as a zombie, Z and &lt;defunct&gt;, with its parent still alive. In the second part, bash -c starts sleep 3 and exits at once. The orphaned sleep gets PID 1 as its new parent (PPID 1), and PID 1 will reap it.', root=True)}
{note('Many processes in state D at once, a high load average with idle CPUs, and commands that hang on <code>ls</code> often mean a disk or an NFS server that does not answer. kill -9 cannot help with D, because the signal is only handled when the I/O returns. Look at <code>dmesg</code> for I/O errors and at the storage itself.', 'tip')}
{talk('Every process is in a state, shown in the stat column of p s. R means running or ready to run, and S means sleeping while it waits for something, which is the normal state of most processes. D is a deep sleep inside the kernel while it waits for a disk, and such a process cannot be killed until the disk answers. T means stopped, for example by control Z. Z means zombie: the process has exited, but its parent has not collected the exit status yet. A zombie uses no memory, but a parent that never waits can leak thousands of them. If a parent dies first, the child becomes an orphan and gets process one as its new parent, which cleans up after it. The demo makes both, for real, in a private process namespace.')}
''', kw=['process state', 'STAT column', 'R running', 'S sleeping', 'D uninterruptible sleep', 'T stopped', 'Z zombie', 'defunct', 'I idle', 'orphan process', 'reparenting', 'subreaper', 'unshare --pid', 'PID namespace', 'reap', 'SIGCHLD', 'NFS hang'])

K.lesson('threads', 'Threads and the scheduler', f'''
{table(['', 'Process', 'Thread'], [
    ['Memory', 'its own address space', 'shares the address space of its process'],
    ['Made with', 'fork (clone without sharing flags)', 'pthread_create (clone with CLONE_VM, CLONE_FILES and others)'],
    ['Seen as', 'a PID in ps', 'a TID, shown as LWP in ps -L, and a folder in /proc/PID/task/'],
    ['A crash', 'affects only that process', 'takes down the whole process'],
    ['Talking', 'pipes, sockets, shared memory', 'any variable, with locks to stay safe']])}
{run('Threads of a Python program, nice and the scheduling policy', """cat > threads.py <<'EOF'
import os, subprocess, threading, time
for i in range(3):
    threading.Thread(target=time.sleep, args=(3,)).start()
subprocess.run(["ps", "-L", "-o", "pid,lwp,nlwp,stat,comm", "-p", str(os.getpid())])
print("tasks:", len(os.listdir(f"/proc/{os.getpid()}/task")))
EOF
python3 threads.py
nice -n 10 sleep 30 &
ps -o pid,ni,pri,comm -p $!
chrt -p $!
kill $!""", note='The Python program has one PID and four threads: the main thread, whose TID equals the PID, and three more. NLWP counts them, l in Sl says the process has threads, and every thread has a folder under /proc/PID/task. nice -n 10 starts sleep with a lower priority: NI 10, and ps shows PRI 9 on its own scale where a higher number means more important. chrt shows the normal policy SCHED_OTHER, the one nearly every program uses.')}
{table(['Tool', 'What it changes'], [
    ['<code>nice -n N CMD</code>, <code>renice -n N -p PID</code>', 'niceness from -20 (most CPU) to 19 (least). Only root may lower it below 0'],
    ['<code>chrt -f -p 50 PID</code>', 'real-time policy SCHED_FIFO with priority 1 to 99, which always runs before normal tasks (careful: it can freeze a machine)'],
    ['<code>chrt -b CMD</code>, <code>chrt -i CMD</code>', 'SCHED_BATCH for long batch jobs, SCHED_IDLE for work that should only use idle CPU'],
    ['<code>taskset -c 0,1 CMD</code>', 'CPU affinity: which CPUs a process may run on'],
    ['<code>ionice -c 3 CMD</code>', 'disk I/O priority, class 3 is idle'],
    ['<code>systemd-run --scope -p CPUQuota=50% CMD</code>', 'a hard CPU limit through cgroups (chapter 3.1)']])}
{note('Since Linux 6.6 the normal scheduler is EEVDF (earliest eligible virtual deadline first), which replaced CFS. Both give each runnable task a fair share of CPU time weighted by its nice value: each nice step changes the weight by about 25 percent, so a nice 0 task gets about 1.25 times the CPU of a nice 1 task when they compete.', 'tip')}
{talk('A process can contain several threads. Threads share the memory and the open files of their process, so they can work on the same data, but a crash in one thread ends the whole process. On Linux every thread is a task of its own with a thread id, shown as L W P in p s dash capital L, and a folder in slash proc slash P I D slash task. The scheduler decides which task runs on which C P U and for how long. Nice values from minus twenty to nineteen change a task’s share: nicer tasks get less. Chrt sets special policies such as real time, and taskset pins a process to certain C P Us. Since kernel six point six, the scheduler is called E E V D F.')}
''', kw=['thread', 'pthread', 'clone', 'CLONE_VM', 'TID', 'LWP', 'NLWP', 'ps -L', '/proc/PID/task', 'scheduler', 'EEVDF', 'CFS', 'nice', 'renice', 'niceness', 'PRI', 'chrt', 'SCHED_OTHER', 'SCHED_FIFO', 'SCHED_BATCH', 'SCHED_IDLE', 'real-time priority', 'taskset', 'CPU affinity', 'ionice'])

K.lesson('practice', 'Practice: follow processes through their life', f'''
<p>Start, inspect, pause and end processes on the practice server, and read their state in /proc.</p>
{lab('Process life cycle', [
    ('Show the process tree.', 'pstree', [{'out': r'systemd─┬─bash'}]),
    ('Show the tree with process ids.', 'pstree -p', [{'out': r'bash\(\d+\)'}]),
    ('Start sleep 300 in the background.', 'sleep 300 &', [{'out': r'^\[1\] \d+'}]),
    ('Show the columns pid, ppid, stat and cmd of your processes.', 'ps -o pid,ppid,stat,cmd', [{'out': r'sleep 300'}]),
    ('Show the State line of the background job in /proc (its PID is in $!).', 'grep State /proc/$!/status', [{'out': r'S \(sleeping\)'}]),
    ('Stop the job with SIGSTOP.', 'kill -STOP %1', [{'cmd': r'kill\s+-(STOP|19|SIGSTOP)'}]),
    ('Read its State again.', 'grep State /proc/$!/status', [{'out': r'T \(stopped\)'}]),
    ('Let it continue.', 'kill -CONT %1', [{'cmd': r'kill\s+-(CONT|18|SIGCONT)'}]),
    ('Run a shell that exits with status 3.', "bash -c 'exit 3'", [{'code': 3}]),
    ('Print the status of the last command.', 'echo $?', [{'out': '^3$'}]),
    ('Start sleep 100 with niceness 10 in the background.', 'nice -n 10 sleep 100 &', [{'cmd': r'nice\s+-n\s*10'}]),
    ('Show pid, ni and cmd of your processes.', 'ps -o pid,ni,cmd', [{'out': r'\s10 sleep 100'}])])}
{talk('Now follow processes yourself. Draw the process tree with pstree, once with process ids. Start sleep in the background and look at its parent and state with p s dash o. Read its state in slash proc, stop it with SIGSTOP and read the state again, which turns into T for stopped. Let it continue. Then run a shell that exits with status three and print the status. Finally start a nicer sleep with niceness ten and check the N I column.')}
''', kw=['process lab', 'pstree practice', 'ps -o practice', 'proc status practice', 'nice practice'])

K.lesson('levels', 'Processes from school to research', f'''
{ladder(
    '<p>A process is a program that is running. Each one has a number, a parent that started it, and a state such as running or sleeping. When it ends, it leaves a result code: 0 means everything went well.</p>',
    '<p>Read the tree with pstree and ps, understand fork, exec, exit and wait, exit statuses including 128+N, process states (D, Z, T), zombies and orphans, threads in ps -L, and priorities with nice, chrt and taskset.</p>',
    '<p>Engineers write services that handle SIGTERM and SIGCHLD correctly, use process supervisors (systemd units with Restart=, or a small init in containers), choose between processes and threads (or event loops) for concurrency, pin latency critical work to CPUs, isolate CPUs with isolcpus or cgroup cpusets, and debug with /proc/PID/stack, gdb and perf.</p>',
    '<p>Research studies schedulers (EEVDF, sched_ext in Linux 6.12, which lets schedulers be written as BPF programs), the cost of fork for large processes and alternatives such as posix_spawn and vfork, process creation in microservices and serverless systems that start thousands of short tasks per second, and lightweight virtual machines such as Firecracker.</p>')}
{scene('the server that ran out of process ids', '<p>A monitoring agent on a build server started a small check script every second, but never called wait for it. After two days, ps showed over 30000 &lt;defunct&gt; entries, and new logins failed with “fork: retry: Resource temporarily unavailable”. Killing the agent made systemd the parent of all zombies, which reaped them in a second. The vendor fixed the agent, and the team added a check that alerts when the number of Z processes grows.</p>')}
{talk('Here is how understanding processes grows. At school you learn that a process is a running program with a number, a parent and a result code. Professionals read the process tree, understand fork, exec and wait, know what states like D and Z mean, and use nice and chrt to share the C P U. Engineers build services that handle signals and child processes correctly, pick between processes and threads, and pin critical work to C P Us. Researchers design new schedulers, including ones written as B P F programs, and find faster ways to start thousands of tiny tasks per second.')}
''', kw=['process supervisor', 'Restart=', 'posix_spawn', 'vfork', 'sched_ext', 'isolcpus', 'cpuset', '/proc/PID/stack', 'gdb', 'Firecracker', 'Resource temporarily unavailable', 'fork bomb'])

K.quiz('e', 'Which system call makes a copy of the running process?', ['exec', 'fork', 'wait', 'kill'], 1, 'Copy.', 'On Linux it is clone underneath.')
K.quiz('e', 'What does exec do?', ['Makes a new process', 'Replaces the program inside the current process', 'Ends the process', 'Waits for a child'], 1, 'Same PID, new program.', 'Open files stay.')
K.quiz('e', 'What does exit status 0 mean?', ['Error', 'Success', 'Killed', 'Not found'], 1, 'Zero is good.', 'Anything else is an error.')
K.quiz('e', 'Which command draws the process tree?', ['ls -R', 'pstree', 'tree', 'top'], 1, 'Process tree.', 'pstree -p adds PIDs.')
K.quiz('m', 'Why is cd a shell builtin?', ['It is faster', 'A child process could not change the shell’s own folder', 'It needs root', 'It is older'], 1, 'Own state.', 'The same for export and exit.')
K.quiz('m', 'What is a zombie process?', ['A virus', 'A process that exited but whose parent has not called wait yet', 'A process using 100 % CPU', 'A stopped process'], 1, 'Dead but not collected.', 'State Z, defunct.')
K.quiz('m', 'A program exits with status 137. What happened?', ['Not found', 'It was killed by SIGKILL (128 + 9)', 'It succeeded', 'Permission denied'], 1, '128 plus a signal.', 'Often the OOM killer.')
K.quiz('m', 'Who becomes the parent of an orphan?', ['Nobody', 'PID 1, or the nearest subreaper', 'The shell', 'The kernel thread kthreadd'], 1, 'Reparenting.', 'It reaps the orphan when it exits.')
K.quiz('m', 'What does state D mean?', ['Dead', 'Uninterruptible sleep, usually waiting for disk I/O', 'Daemon', 'Debugging'], 1, 'Deep sleep.', 'kill -9 waits until the I/O ends.')
K.quiz('h', 'How do you get rid of zombies?', ['kill -9 the zombie', 'Make the parent call wait, or end the parent so PID 1 reaps them', 'Reboot only', 'rm /proc/PID'], 1, 'They are already dead.', 'Fix or kill the parent.')
K.quiz('h', 'What do threads of one process share?', ['Nothing', 'The address space and open files', 'Only the PID', 'Only the stack'], 1, 'Shared memory.', 'Each has its own stack and TID.')
K.quiz('h', 'What does nice -n 19 do?', ['Gives the most CPU', 'Gives the process the lowest normal priority', 'Makes it real time', 'Pins it to CPU 19'], 1, 'Nicest to others.', 'Range -20 to 19.')
K.quiz('h', 'Why can text be printed twice after fork in a C program?', ['A kernel bug', 'Unflushed text in the stdio buffer is copied into the child', 'printf runs twice', 'The terminal echoes it'], 1, 'Buffers are copied.', 'Call fflush before fork.')
K.quiz('x', 'Why does a container often need a small init such as tini as PID 1?', ['For networking', 'PID 1 must reap orphans and forward signals, which most programs do not do', 'To save memory', 'For logging'], 1, 'PID 1 duties.', 'docker run --init adds one.')

K.calc('e', 'A process is killed with SIGTERM (15). Which status does the shell report?', '143', '128 plus the signal.', ['128 + 15.', 'Shells add 128.', eq('143')], check=143)
K.calc('e', 'bash -c "exit 260". Which status do you see?', '4', 'Statuses are 8 bits.', ['The status is taken modulo 256.', '260 − 256.', eq('4')], check=4)
K.calc('m', 'Ctrl+C sends SIGINT (2). Which status does the shell show?', '130', '128 plus 2.', ['128 + 2.', 'SIGINT is 2.', eq('130')], check=130)
K.calc('m', 'A parent forks 3 children, and each child forks 2 more. How many processes are there in total, the parent included?', '10', 'Count each level.', ['1 parent.', '3 children, 3 × 2 = 6 grandchildren.', eq('1 + 3 + 6 = 10')], check=10)
K.calc('h', 'A loop calls fork() 4 times, and every process (parent and children) keeps looping. How many processes exist at the end?', '16', 'Doubles each time.', ['Each fork doubles the number.', '2 to the power 4.', eq('2 × 2 × 2 × 2 = 16')], check=16)
K.calc('h', 'pid_max is 32768. A buggy agent leaks 1 zombie per second. After how many whole hours are all process ids used, ignoring the ones already in use?', '9', 'Seconds to hours.', ['32768 seconds.', '÷ 3600 = 9.1.', eq('9 hours')], check=9)
K.calc('x', 'Each nice step changes the CPU weight by about 1.25 times. Roughly how many times more CPU does a nice 0 task get than a nice 3 task?', '2', 'Multiply three times.', ['1.25 × 1.25 × 1.25 = 1.95.', 'Round.', eq('about 2 times')], check=2)

K.must('Birth and death', 'fork copies (returns 0 in the child), execve replaces the program (PID and open files stay), exit leaves a status, wait collects it. Builtins such as cd run without fork.')
K.must('Tree and status', 'pstree -p, ps -o pid,ppid,stat,cmd. PID 1 is systemd. Status 0 ok, 126 not executable, 127 not found, 128+N killed by signal N (130, 137, 143).')
K.must('States', 'R running, S sleeping, D waiting for I/O (cannot be killed), T stopped, Z zombie. Orphans get PID 1 as parent.')
K.must('Threads', 'Share memory and files. TID shown as LWP in ps -L, folders in /proc/PID/task, l in STAT.')
K.must('Scheduler', 'EEVDF since 6.6. nice and renice -20 to 19, chrt for policies (SCHED_OTHER, FIFO, BATCH, IDLE), taskset for CPUs, ionice for disks.')

T = K.topic(
    slug='process-lifecycle', topic='process-lifecycle',
    step=(1, 'Kernel and processes', 'lx-adv-1', 'Look under the shell: how programs ask the kernel for everything with system calls, how the kernel shows its state in /proc and /sys, and how processes are born, run and die.', 'Expert'),
    title='How processes live: fork, exec, wait, states and threads', short='Process life cycle', badge='1.2', minutes=55, added='2026-11-24',
    lead='Follow a process from fork and exec to exit and wait, read exit statuses and process states, understand zombies and orphans, and see how threads and the scheduler share the CPUs.',
    desc='fork, execve, exit and wait in C and in bash, builtins, the process tree and PID 1, exit statuses and 128+N, process states R, S, D, T, Z, zombies and orphans in a PID namespace, threads with ps -L and /proc/PID/task, and the scheduler with nice, chrt, taskset and EEVDF.',
    summary='fork and exec, wait and exit statuses, states, zombies, orphans, threads, nice.',
    keywords=['fork', 'exec', 'execve', 'wait', 'exit status', 'process tree', 'pstree', 'PID 1', 'process state', 'zombie', 'orphan', 'thread', 'LWP', 'scheduler', 'nice', 'chrt', 'taskset'],
    recap='<p>A process is born when its parent forks and usually runs a new program with execve. It ends with exit, and stays a zombie until the parent collects the status with wait. Orphans move to PID 1. Statuses follow fixed rules (127 not found, 128+N for signals). Threads share their process’s memory, and the EEVDF scheduler shares the CPUs by nice value and policy.</p>')
