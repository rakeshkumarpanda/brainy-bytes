# Internals and advanced 3.2: performance analysis. Latency, throughput and utilization, the USE method, the
# 60 second checklist, load average and run queue, vmstat, mpstat, pidstat, top, iostat -x and what %util means on
# SSDs, sar and the sysstat history, time, strace -c and the cost of system calls, perf (stat, top, record,
# report), flame graphs and the eBPF tools of bcc and bpftrace.
# Sources: proc(5) (/proc/loadavg), vmstat(8), mpstat(1), pidstat(1), iostat(1), sar(1), sadc(8), the sysstat
# package files of Ubuntu 24.04 (/etc/default/sysstat, sysstat-collect.timer), top(1), time(1) and the bash manual
# (the time keyword), strace(1), perf-stat(1), perf-top(1), perf-record(1), stress-ng(1), and Brendan Gregg's
# USE method and "Linux Performance Analysis in 60,000 Milliseconds" (Netflix Technology Blog).
# Real boxes run in the build container: stress-ng CPU and disk workers watched with vmstat and pidstat, and dd with
# strace -c to count system calls. The container has 4 CPUs, which the CPU box states. perf is not installed in the
# build container (it needs linux-tools for the running kernel), so perf appears as a command table only.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('method', 'Measure first: the USE method and the 60 second checklist', f'''
<p>“The server is slow” is a feeling, not a measurement. Performance work starts by turning it into numbers: <b>latency</b> (how long one request takes, best as percentiles such as p99), <b>throughput</b> (requests or bytes per second), <b>utilization</b> (how busy a resource is) and <b>saturation</b> (how much work waits in a queue).</p>
{table(['Resource', 'Utilization', 'Saturation', 'Errors'], [
    ['CPU', '<code>mpstat -P ALL 1</code>, us + sy per CPU', '<code>vmstat 1</code> r above the number of CPUs, load average', '<code>dmesg</code> machine check messages'],
    ['Memory', '<code>free -m</code>, available', '<code>vmstat 1</code> si and so (swapping), PSI in /proc/pressure/memory', 'OOM killer lines in <code>journalctl -k</code>'],
    ['Disk', '<code>iostat -xz 1</code> %util', 'aqu-sz, r_await and w_await', '<code>dmesg</code> I/O errors, <code>smartctl -H</code>'],
    ['Network', '<code>sar -n DEV 1</code> rxkB/s and txkB/s against link speed', '<code>nstat</code> or <code>ss -ti</code> retransmits', '<code>ip -s link</code> errors and drops']])}
{play('lx-use')}
{cmdtable([
    ('uptime', 'Load averages over 1, 5 and 15 minutes: rising or falling', 'uptime'),
    ('dmesg | tail', 'Recent kernel messages: OOM kills, I/O errors, dropped packets', 'sudo dmesg -T | tail'),
    ('vmstat 1', 'Run queue, memory, swap, I/O and CPU split every second', 'vmstat 1 5'),
    ('mpstat -P ALL 1', 'CPU use per CPU: one hot CPU means a single threaded hot spot', 'mpstat -P ALL 1 3'),
    ('pidstat 1', 'CPU use per process, like a top that scrolls', 'pidstat 1 5'),
    ('iostat -xz 1', 'Per disk: requests, throughput, wait times, queue and %util', 'iostat -xz 1 3'),
    ('free -m', 'Memory in MiB, look at available', 'free -m'),
    ('sar -n DEV 1', 'Network throughput per interface', 'sar -n DEV 1 3'),
    ('sar -n TCP,ETCP 1', 'New TCP connections and retransmits per second', 'sar -n TCP,ETCP 1 3'),
    ('top', 'A summary to check that nothing was missed', 'top')])}
{note('This list of ten commands is Brendan Gregg’s 60 second checklist from Netflix. All of them come with Ubuntu or with the sysstat package (<code>sudo apt install sysstat</code>), so they are ready before an incident starts.', 'tip')}
{talk('When someone says the server is slow, first turn the feeling into numbers. Latency is how long one request takes, throughput is how many requests per second get done, utilization is how busy a part is, and saturation is how much work is waiting for it. The USE method checks every resource, C P U, memory, disk and network, for utilization, saturation and errors, in a fixed order, so you do not guess. In the animation, pick a symptom and follow the check. The ten commands of the sixty second checklist give a first picture of any Linux server in about a minute.')}
''', kw=['performance', 'latency', 'throughput', 'utilization', 'saturation', 'errors', 'USE method', 'Brendan Gregg', '60 second checklist', 'percentile', 'p99', 'bottleneck', 'sysstat', 'PSI', '/proc/pressure'])

K.lesson('cpu', 'CPU: load average, vmstat, mpstat and pidstat', f'''
<p>The <b>load average</b> in <code>uptime</code> and /proc/loadavg is the average number of tasks that are running, waiting for a CPU, or in uninterruptible sleep (state D, usually waiting for disk), over 1, 5 and 15 minutes. Compare it with the number of CPUs: a load of 4 is full use on 4 CPUs but a long queue on 1.</p>
{run('Two CPU hogs seen by vmstat and pidstat', """nproc
stress-ng --cpu 2 --timeout 6s --quiet &
sleep 1
vmstat 1 3 | awk '{print $1, $2, $13, $14, $15, $16}'
pidstat -u -C stress-ng 1 1 | grep Average
wait""", note='stress-ng starts two workers that only compute. The build machine has 4 CPUs, so two busy workers make us (user time) about 50 %. The first vmstat line is the average since boot, as vmstat(8) says, so it looks quiet. r counts the tasks that run or wait to run. pidstat names the two workers, each near 100 % of one CPU. awk keeps only the columns r, b, us, sy, id and wa.', root=True)}
{table(['vmstat column', 'Meaning', 'Look out for'], [
    ['r', 'tasks running or waiting for a CPU', 'r above the number of CPUs for a long time: CPU saturation'],
    ['b', 'tasks blocked, waiting for I/O', 'often above 0: a disk problem'],
    ['si, so', 'memory swapped in and out per second', 'both above 0 all the time: not enough RAM'],
    ['bi, bo', 'blocks read from and written to disks per second', 'compare with what the disk can do'],
    ['in, cs', 'interrupts and context switches per second', 'a sudden jump: lock contention or too many threads'],
    ['us, sy', 'CPU time in programs and in the kernel', 'high sy: many system calls, see the next lessons'],
    ['id, wa', 'idle, and idle while waiting for I/O', 'high wa: CPUs are free but tasks wait for the disk'],
    ['st', 'time stolen by the hypervisor for other VMs', 'above a few percent on a cloud VM: noisy neighbours or a too small instance']])}
{cmdtable([
    ('uptime', 'Load averages for 1, 5 and 15 minutes', 'uptime'),
    ('cat /proc/loadavg', 'The same numbers, plus running/total tasks and the last PID', 'cat /proc/loadavg'),
    ('vmstat DELAY COUNT', 'A line every DELAY seconds, COUNT times, the first is since boot', 'vmstat 1 5'),
    ('vmstat -S M', 'Memory columns in MiB', 'vmstat -S M 1 3'),
    ('mpstat -P ALL 1', 'Per CPU use, find one CPU at 100 %', 'mpstat -P ALL 1 3'),
    ('pidstat 1', 'Per process CPU use (-r memory, -d disk, -w context switches)', 'pidstat -d 1 3'),
    ('ps -eo pid,comm,%cpu --sort=-%cpu', 'Processes sorted by CPU use', 'ps -eo pid,comm,%cpu --sort=-%cpu | head')])}
{note('A load of 8 on a 2 CPU machine with id near 0 means CPU saturation. A load of 8 with id high and wa high means tasks in state D, waiting for disk or a hung NFS server, so adding CPUs would not help.', 'warn')}
{talk('The load average is the number of tasks that run, wait for a C P U, or wait in uninterruptible sleep, usually for the disk, averaged over one, five and fifteen minutes. Always compare it with the number of C P Us. In the demo, two workers of stress n g keep two of four C P Us busy, so vmstat shows about fifty percent user time and pidstat shows each worker near one hundred percent. Read vmstat from left to right: r for the run queue, b for tasks blocked on I O, s i and s o for swapping, then the C P U split into user, system, idle, wait and steal. Remember that the first line of vmstat is the average since boot.')}
''', kw=['load average', '/proc/loadavg', 'uptime', 'run queue', 'uninterruptible sleep', 'D state', 'vmstat', 'r column', 'b column', 'si so', 'context switches', 'user time', 'system time', 'iowait', 'steal time', 'mpstat', 'pidstat', 'stress-ng', 'ps --sort', 'nproc'])

K.lesson('disk', 'Disks: iostat, await, queue size and %util', f'''
<p>Disk trouble shows as slow saves, high <b>wa</b> in vmstat, and tasks in state D. <code>iostat -x</code> shows each device: requests per second, kilobytes per second, the average time a request takes including the wait in the queue (r_await and w_await, in milliseconds), the average queue length (aqu-sz) and %util, the share of time the device had at least one request.</p>
{run('A disk writer seen by vmstat and pidstat', """mkdir -p /srv/iolab
stress-ng --hdd 1 --hdd-bytes 64M --timeout 5s --quiet --temp-path /srv/iolab &
sleep 1
vmstat 1 3 | awk '{print $1, $2, $9, $10, $15, $16}'
pidstat -d -C stress-ng 1 1 | grep Average
wait
rm -rf /srv/iolab""", note='The hdd worker writes and rereads a 64 MiB file as fast as it can. vmstat shows bo (blocks written per second) jump, and wa rises while id falls. On a slower disk b also shows the tasks blocked waiting for I/O. pidstat -d names the process and its write rate in kB/s. The exact numbers differ on every run and every disk.', root=True)}
{table(['iostat -x column', 'Meaning'], [
    ['r/s, w/s', 'read and write requests completed per second (IOPS)'],
    ['rkB/s, wkB/s', 'kilobytes read and written per second (throughput)'],
    ['r_await, w_await', 'average milliseconds per request, including the queue time'],
    ['rareq-sz, wareq-sz', 'average request size in kB: small means random I/O'],
    ['aqu-sz', 'average number of requests in the queue and in service'],
    ['%util', 'share of time the device was busy with at least one request']])}
{note('On devices that serve many requests in parallel, such as RAID arrays and NVMe or SATA SSDs, %util at 100 does not mean the device is at its limit, as iostat(1) itself warns. Watch await and aqu-sz instead: if the wait times grow while throughput stays flat, the device is saturated.', 'warn')}
{sample('iostat on the practice server', """iostat -xz 1 2""", out="""Linux 6.8.0-practice (brainy) \t11/24/26 \t_x86_64_\t(2 CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           2.10    0.00    0.80    0.30    0.00   96.80

Device            r/s     rkB/s   rrqm/s  %rrqm r_await rareq-sz     w/s     wkB/s   wrqm/s  %wrqm w_await wareq-sz     d/s     dkB/s   drqm/s  %drqm d_await dareq-sz     f/s f_await  aqu-sz  %util
sda              3.10     24.50     0.04   1.27    0.61     7.90    5.42     68.20     2.31  29.88    1.92    12.58    0.00      0.00     0.00   0.00    0.00     0.00    0.21    0.85    0.01   0.62

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.84    0.00    0.32    0.12    0.00   98.72

Device            r/s     rkB/s   rrqm/s  %rrqm r_await rareq-sz     w/s     wkB/s   wrqm/s  %wrqm w_await wareq-sz     d/s     dkB/s   drqm/s  %drqm d_await dareq-sz     f/s f_await  aqu-sz  %util
sda              1.24      9.80     0.04   1.27    0.61     7.90    2.17     27.28     2.31  29.88    1.92    12.58    0.00      0.00     0.00   0.00    0.00     0.00    0.21    0.85    0.01   0.25""", note='On the practice server the disk sda is quiet: a few requests per second, 1 to 2 ms per request and under 1 % util. The first report is the average since boot, the second covers the last second. -z hides devices with no activity, which keeps the output short on machines with many loop devices.')}
{talk('Disk problems show as slow saves, a high wait value in vmstat and tasks in state D. In the demo, a worker writes a sixty four megabyte file again and again: vmstat shows the written blocks jump and the wait time rise, and pidstat names the writer. iostat with minus x gives each disk: requests per second, kilobytes per second, the average time per request in milliseconds, the queue size, and percent util. On S S Ds and RAID arrays, percent util can be one hundred while the device still has room, so watch the wait times and the queue size.')}
''', kw=['iostat', 'iostat -x', 'IOPS', 'r_await', 'w_await', 'aqu-sz', '%util', 'rareq-sz', 'disk saturation', 'iowait', 'pidstat -d', 'iotop', 'SSD util', 'NVMe', 'random I/O', 'sequential I/O'])

K.lesson('calls', 'Where the time goes: time, strace -c, perf and eBPF', f'''
<p>Once you know which process is slow, ask where its time goes: in its own code (user time), in the kernel (system time, for example many small system calls), or waiting (real time much longer than user plus sys).</p>
{run('About 200 kB copied with 1 byte and with 64 KiB per call', """dd if=/dev/zero of=/dev/null bs=1 count=200000 2>&1 | tail -n 1
dd if=/dev/zero of=/dev/null bs=64k count=4 2>&1 | tail -n 1
strace -c -o /tmp/one.txt dd if=/dev/zero of=/dev/null bs=1 count=200000 status=none
head -n 4 /tmp/one.txt
strace -c -o /tmp/big.txt dd if=/dev/zero of=/dev/null bs=64k count=4 status=none
head -n 4 /tmp/big.txt""", note='The first copies 200 kB and the second 256 KiB, nearly the same amount. With bs=1 dd makes 200 000 read and 200 000 write calls, and each call crosses into the kernel and back. The rate line shows how much slower that is. strace -c counts the calls: about 200 000 reads and writes against a handful with 64 KiB blocks. strace itself makes every call much slower, so its times are only good for comparing, and it is not for busy production servers.')}
{cmdtable([
    ('time CMD', 'real (wall clock), user and sys time of one command', 'time gzip -k big.log'),
    ('strace -c CMD', 'Count and time the system calls of a command', 'strace -c -f ./build.sh'),
    ('strace -p PID -T', 'Watch a running process, with the time each call took', 'sudo strace -p 2261 -T -e trace=read,write'),
    ('perf stat CMD', 'CPU counters: cycles, instructions, cache misses, context switches', 'sudo perf stat gzip -k big.log'),
    ('perf top', 'The functions using the most CPU right now, system wide', 'sudo perf top'),
    ('perf record -F 99 -g -p PID', 'Sample stacks 99 times a second for later analysis', 'sudo perf record -F 99 -g -p 2261 -- sleep 30'),
    ('perf report', 'Browse the samples saved in perf.data', 'sudo perf report'),
    ('execsnoop-bpfcc', 'eBPF: print every new process as it starts', 'sudo execsnoop-bpfcc'),
    ('biolatency-bpfcc', 'eBPF: a histogram of disk I/O latency', 'sudo biolatency-bpfcc 10 1'),
    ('runqlat-bpfcc', 'eBPF: how long tasks wait in the CPU run queue', 'sudo runqlat-bpfcc 10 1')])}
{steps('Profile a slow program with perf', [
    'Install perf on Ubuntu with <code>sudo apt install linux-tools-common linux-tools-$(uname -r)</code>, because perf must match the running kernel.',
    'Record the slow program under real load: <code>sudo perf record -F 99 -g -p PID -- sleep 30</code>.',
    'Look at the hottest functions with <code>sudo perf report</code>, or draw a <b>flame graph</b>: <code>perf script</code> piped into stackcollapse-perf.pl and flamegraph.pl from Brendan Gregg’s FlameGraph project. The widest boxes are where the CPU time goes.',
    'For questions perf cannot answer cheaply, such as the latency of each disk request or how long tasks wait for a CPU, use the eBPF tools of bcc (package bpfcc-tools, commands ending in -bpfcc) or a one line bpftrace program.'])}
{note('Unlike strace, perf and eBPF tools sample or count inside the kernel with little overhead, which is why they are the tools for production. Normal users may be limited by kernel.perf_event_paranoid, so run them with sudo.', 'tip')}
{talk('After you know which process is slow, find out where its time goes. The time command splits it into real time, user time in the program and system time in the kernel. In the demo, dd copies the same two hundred kilobytes once with one byte per call and once with sixty four kilobytes per call. strace minus c counts two hundred thousand reads and writes against a handful, and the rate shows the cost of so many trips into the kernel. strace slows a program down a lot, so on production servers use perf, which samples the C P U with little cost, flame graphs to see the hottest code, and e B P F tools such as biolatency and runqlat.')}
''', kw=['time command', 'real user sys', 'strace -c', 'system call overhead', 'dd block size', 'perf', 'perf stat', 'perf top', 'perf record', 'perf report', 'flame graph', 'FlameGraph', 'eBPF', 'bcc', 'bpfcc-tools', 'bpftrace', 'execsnoop', 'biolatency', 'runqlat', 'linux-tools', 'perf_event_paranoid'])

K.lesson('history', 'History with sar, and fixing what you found', f'''
<p>The tools so far show <b>now</b>. To answer “what happened at 3 a.m.?” you need history. The sysstat package collects it: on Ubuntu 24.04 the timer sysstat-collect.timer runs every 10 minutes and saves a file per day in /var/log/sysstat, which sar reads.</p>
{steps('Keep a performance history with sysstat', [
    'Install and switch it on: <code>sudo apt install sysstat</code>, set <code>ENABLED="true"</code> in /etc/default/sysstat (it is "false" after install), then <code>sudo systemctl enable --now sysstat</code>.',
    'Read today: <code>sar -u</code> (CPU), <code>sar -r</code> (memory), <code>sar -q</code> (run queue and load), <code>sar -d</code> (disks), <code>sar -n DEV</code> (network).',
    'Read an earlier day with <code>sar -u -f /var/log/sysstat/sa23</code> for the 23rd, and a time window with <code>-s 02:50:00 -e 03:20:00</code>.',
    'For many servers, ship the same numbers to a monitoring system such as Prometheus with node_exporter, and graph them in Grafana.'])}
{table(['What you found', 'Typical fixes'], [
    ['one process uses all of one CPU', 'profile it with perf, fix the hot loop, or run more workers on the other CPUs'],
    ['every CPU busy, run queue long', 'fewer jobs at once, nice or CPUQuota= for batch jobs, more CPUs'],
    ['swapping (si, so) and OOM kills', 'find the leak, MemoryMax= per service, more RAM'],
    ['disk await high, small requests', 'bigger writes, fewer fsync calls, the page cache, a faster disk'],
    ['many system calls, high sy', 'bigger buffers, batching, fewer small reads and writes'],
    ['high st on a cloud VM', 'a bigger or dedicated instance type']])}
{note('Change one thing at a time and measure again with the same tool. A fix that is not measured is a guess, and a tuning value copied from the internet without a measurement often makes things worse.', 'warn')}
{talk('The tools so far show what is happening now, but often the question is what happened last night. The sysstat package saves numbers every ten minutes on Ubuntu, after you set enabled to true in slash etc slash default slash sysstat and enable the service. sar reads them back: minus u for C P U, minus r for memory, minus q for the run queue, minus d for disks and minus n DEV for the network, with minus f for an earlier day. Then fix what the numbers show, one change at a time, and measure again with the same tool.')}
''', kw=['sar', 'sysstat', 'sadc', '/var/log/sysstat', 'sysstat-collect.timer', 'ENABLED true', 'sar -u', 'sar -r', 'sar -q', 'sar -d', 'sar -n DEV', 'sar -f', 'Prometheus', 'node_exporter', 'Grafana', 'tuning', 'CPUQuota', 'MemoryMax', 'measure again'])

K.lesson('practice', 'Practice: find the busy process', f'''
<p>Start a CPU hog on the practice server, then find it with the performance tools, and stop it.</p>
{lab('Performance tools', [
    ('Count the CPUs of the server.', 'nproc', [{'out': r'^2$'}]),
    ('Show the load averages with uptime.', 'uptime', [{'out': 'load average'}]),
    ('Read the same numbers from /proc/loadavg.', 'cat /proc/loadavg', [{'out': r'^\d+\.\d\d \d+\.\d\d \d+\.\d\d \d+/\d+ \d+$'}]),
    ('Start a CPU hog in the background: yes with its output sent to /dev/null.', 'yes > /dev/null &', [{'cmd': r'^yes\s*>\s*/dev/null\s*&$'}]),
    ('Run vmstat every second, 3 times.', 'vmstat 1 3', [{'out': r'r\s+b\s+swpd'}]),
    ('Show the use of each CPU with mpstat, once a second, once.', 'mpstat -P ALL 1 1', [{'out': r'Average:\s+0\s+99\.70'}]),
    ('Show CPU use per process with pidstat for one second.', 'pidstat 1 1', [{'out': r'99\.70\s+\d\s+yes'}]),
    ('List processes sorted by CPU use, with pid, comm and %cpu.', 'ps -eo pid,comm,%cpu --sort=-%cpu', [{'out': r'PID COMMAND\s+%CPU\n\s+\d+ yes'}]),
    ('Stop the hog with pkill.', 'pkill yes', [{'cmd': r'^pkill\s+(-x\s+)?yes$'}]),
    ('Show the disks with iostat -xz.', 'iostat -xz', [{'out': r'sda\s+\d'}]),
    ('Show memory in MiB with vmstat -S M.', 'vmstat -S M', [{'out': r'swpd\s+free'}])])}
{talk('Now practise on the server. Count the C P Us with n proc and read the load averages with uptime and from slash proc slash load avg. Start a C P U hog with yes sent to slash dev slash null in the background. Run vmstat, then mpstat for each C P U, and see one C P U at almost one hundred percent. pidstat and ps sorted by C P U both name yes as the culprit. Stop it with pkill, and finish with a look at the disks with iostat and at memory in megabytes with vmstat.')}
''', kw=['performance lab', 'find busy process', 'vmstat practice', 'mpstat practice', 'pidstat practice', 'iostat practice'])

K.lesson('levels', 'Performance from school to research', f'''
{ladder(
    '<p>A computer has parts that can get too busy: the processor, the memory, the disk and the network. When one of them has more work than it can do, things wait in a line and the computer feels slow. Good tools show which part is busy.</p>',
    '<p>Use the USE method and the 60 second checklist, read load average, vmstat, mpstat, pidstat, iostat -x and sar, know what %util means on SSDs, compare real, user and sys time, count system calls with strace -c on a test system, and change one thing at a time.</p>',
    '<p>Site reliability engineers set latency objectives in percentiles, profile production with perf and continuous profilers (Parca, Pyroscope), draw flame graphs and off-CPU graphs, trace with eBPF (bcc, bpftrace), size systems with queueing theory and load tests, and tune CPU frequency, NUMA placement, interrupts and I/O schedulers with measurements.</p>',
    '<p>Research works on tail latency at scale, scheduler designs (the EEVDF scheduler since Linux 6.6, sched_ext with BPF schedulers), low overhead always on tracing, performance models of cloud machines with noisy neighbours, and automatic tuning with machine learning.</p>')}
{scene('the slow website at 9 a.m.', '<p>Every morning at 9 the shop’s pages took 6 seconds. The CPUs were at 40 %, so the team first blamed the database. Following the USE method, vmstat showed wa at 35 % and b at 6, and iostat showed w_await of 200 ms on the data disk with small 4 kB writes. pidstat -d named a log shipper that started at 9, read every log file again and called fsync after each line. Batching the writes and moving the logs to their own disk brought the pages back under 300 ms, and sar the next morning showed the disk queue gone.</p>')}
{talk('Here is how performance skills grow. At school you learn that a computer has parts that can be too busy, and then work waits in a line. Professionals use the U S E method and the sixty second checklist, read vmstat, mpstat, pidstat, iostat and sar, and change one thing at a time. Reliability engineers set targets for slow requests, profile production with perf and flame graphs, and trace with e B P F. Researchers work on tail latency, new schedulers such as E E V D F and s c h e d e x t, and tracing that is cheap enough to leave on all the time.')}
''', kw=['SRE', 'latency objective', 'continuous profiling', 'Parca', 'Pyroscope', 'off-CPU analysis', 'queueing theory', 'load testing', 'NUMA', 'CPU frequency', 'I/O scheduler', 'tail latency', 'EEVDF', 'sched_ext', 'noisy neighbour'])

K.quiz('e', 'Which command shows the load averages?', ['free', 'uptime', 'df', 'lsblk'], 1, 'Also in /proc/loadavg.', '1, 5 and 15 minutes.')
K.quiz('e', 'What does the USE method check for every resource?', ['Users, Services, Events', 'Utilization, Saturation, Errors', 'Uptime, Swap, Energy', 'Updates, Security, Encryption'], 1, 'Three questions.', 'Brendan Gregg’s method.')
K.quiz('e', 'Which package gives iostat, mpstat, pidstat and sar on Ubuntu?', ['procps', 'sysstat', 'coreutils', 'util-linux'], 1, 'System statistics.', 'sudo apt install sysstat.')
K.quiz('e', 'What does the r column of vmstat count?', ['Reads per second', 'Tasks running or waiting for a CPU', 'RAM in use', 'Retransmits'], 1, 'The run queue.', 'Compare with the number of CPUs.')
K.quiz('m', 'Why does the first line of vmstat 1 look different from the rest?', ['It is a header', 'It is the average since boot', 'It is always zero', 'It is the maximum'], 1, 'vmstat(8).', 'Read the later lines.')
K.quiz('m', 'Load average is 8, the machine has 2 CPUs, id is 60 % and wa is 35 %. What is the likely cause?', ['CPU saturation', 'Tasks waiting for I/O in state D', 'Too little swap', 'A network loop'], 1, 'Linux counts D state in the load.', 'CPUs are idle, the disk is not.')
K.quiz('m', 'Which iostat column is the average time per request, including the queue?', ['%util', 'r_await and w_await', 'rkB/s', 'rrqm/s'], 1, 'Await.', 'In milliseconds.')
K.quiz('m', 'An NVMe SSD shows %util 100. What should you check before calling it saturated?', ['Nothing, it is full', 'await and aqu-sz, because the device serves many requests in parallel', 'The CPU temperature', 'The swap size'], 1, 'iostat(1) warns about this.', 'Parallel devices.')
K.quiz('m', 'mpstat shows CPU 0 at 100 % and CPU 1 to 7 idle. What does that suggest?', ['A disk problem', 'A single threaded hot spot', 'Memory leak', 'Nothing'], 1, 'One CPU.', 'More CPUs would not help.')
K.quiz('h', 'A program shows real 10 s, user 0.5 s, sys 0.3 s. Where did most of the time go?', ['In its own code', 'In the kernel', 'Waiting, for example for disk, network or a lock', 'In perf'], 2, 'real minus user minus sys.', 'Off-CPU time.')
K.quiz('h', 'Why is strace a poor choice on a busy production server?', ['It needs a reboot', 'It slows every system call of the traced program a lot', 'It only works on files', 'It cannot attach'], 1, 'ptrace stops at each call.', 'Use perf or eBPF.')
K.quiz('h', 'What does the width of a box in a flame graph show?', ['The time of day', 'How often that function was on the CPU in the samples', 'The memory use', 'The number of threads'], 1, 'Width, not colour.', 'Widest boxes are the hot spots.')
K.quiz('h', 'Which vmstat column shows time taken by the hypervisor for other VMs?', ['wa', 'st', 'sy', 'gu'], 1, 'Steal.', 'Cloud VMs.')
K.quiz('x', 'Where does sar read history from on Ubuntu 24.04?', ['/var/log/syslog', '/var/log/sysstat, filled by sysstat-collect.timer every 10 minutes', '/proc/history', 'journalctl'], 1, 'One file per day.', 'Set ENABLED="true" first.')

K.calc('e', 'A machine has 4 CPUs and a load average of 6. What is the load per CPU?', '1.5', 'Divide.', ['6 ÷ 4.', 'Above 1 means tasks wait.', eq('1.5 per CPU')], check=1.5)
K.calc('e', 'Two CPU bound workers run on 4 CPUs. About what percent does vmstat show as us?', '50', 'Share of all CPUs.', ['2 of 4 CPUs busy.', '2 ÷ 4 = 0.5.', eq('50 %')], check=50)
K.calc('m', 'dd copies 200000 bytes with bs=1. How many read and write calls does it make together, roughly?', '400000', 'One read and one write per block.', ['200000 blocks.', '× 2 calls each.', eq('400000 system calls')], check=400000)
K.calc('m', 'A disk does 400 requests per second, each with an average await of 50 ms. How many requests are in the queue and in service on average? (Little’s law)', '20', 'L = λ × W.', ['λ = 400 per second.', 'W = 0.05 s.', eq('400 × 0.05 = 20')], check=20)
K.calc('m', 'mpstat on an 8 CPU machine shows one CPU at 100 % and the rest idle. What is the overall %usr for all, roughly?', '12.5', 'Average over all CPUs.', ['100 ÷ 8.', 'The average hides the hot CPU.', eq('12.5 %')], check=12.5)
K.calc('h', 'A command shows real 12 s, user 3 s, sys 1 s on one thread. How many seconds did it spend off the CPU, waiting?', '8', 'real − user − sys.', ['12 − 3 − 1.', 'Waiting for I/O, network or locks.', eq('8 s')], check=8)
K.calc('x', 'sysstat collects every 10 minutes. How many samples does one day’s file hold?', '144', 'Minutes in a day.', ['24 × 60 = 1440 minutes.', '1440 ÷ 10.', eq('144 samples')], check=144)

K.must('Method', 'Turn “slow” into latency, throughput, utilization and saturation. USE: Utilization, Saturation, Errors for CPU, memory, disk and network. The 60 second checklist.')
K.must('CPU', 'Load average counts running, runnable and D state tasks: compare with nproc. vmstat r, us, sy, wa, st. mpstat -P ALL for one hot CPU, pidstat and top for the process.')
K.must('Disks', 'iostat -xz: r/s, w/s, kB/s, r_await and w_await, aqu-sz, %util. On SSDs %util 100 is not saturation, watch await and the queue.')
K.must('Where time goes', 'time: real, user, sys. strace -c counts system calls but slows the program. perf stat, top, record and report, flame graphs, eBPF tools from bpfcc-tools.')
K.must('History and fixes', 'sysstat with ENABLED="true", sar -u -r -q -d -n DEV and -f for an earlier day. Change one thing, measure again with the same tool.')

T = K.topic(
    slug='performance', topic='performance',
    step=(3, 'Containers and performance', 'lx-adv-3', 'Build a container from kernel features by hand, then find out why a system is slow with the right tools and method, and finish with a full revision of the course.', 'Expert'),
    title='Performance: find the bottleneck with USE, vmstat, iostat, perf and sar', short='Performance', badge='3.2', minutes=55, added='2026-11-24',
    lead='Turn “the server is slow” into numbers. Check CPU, memory, disk and network with the USE method, read vmstat, mpstat, pidstat and iostat, find where a program spends its time with strace and perf, and look back in time with sar.',
    desc='Latency, throughput, utilization and saturation, the USE method and the 60 second checklist, load average and the run queue, vmstat columns, mpstat and pidstat, iostat -x with await, aqu-sz and %util, time, strace -c and the cost of system calls, perf and flame graphs, eBPF tools, and sar history from sysstat.',
    summary='USE method, load average, vmstat, mpstat, pidstat, iostat, strace -c, perf, sar.',
    keywords=['performance', 'USE method', 'load average', 'vmstat', 'mpstat', 'pidstat', 'iostat', 'sar', 'sysstat', 'strace -c', 'perf', 'flame graph', 'eBPF', 'stress-ng', 'bottleneck'],
    recap='<p>Performance work measures before it changes anything. The USE method checks utilization, saturation and errors of CPU, memory, disk and network. Load average is compared with the number of CPUs, vmstat shows the run queue, swapping and the CPU split, mpstat and pidstat find the hot CPU and process, and iostat -x shows await and queue size per disk. time, strace -c and perf show where a program spends its time, and sar keeps the history.</p>')
