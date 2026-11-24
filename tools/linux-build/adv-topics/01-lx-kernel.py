# Internals and advanced 1.1: the kernel and system calls. What the kernel does, user space and kernel space, how a
# system call crosses the border, libc wrappers, errno, strace (-e, -f, -c, -o), ltrace, the virtual file systems
# /proc and /sys, kernel versions, modules (lsmod, modinfo, modprobe, modprobe.d), the kernel log and the command line.
# Sources: syscalls(2), syscall(2), intro(2), errno(3), strace(1), ltrace(1), proc(5), sysfs(5), uname(1), lsmod(8),
# modinfo(8), modprobe(8), modprobe.d(5), modules-load.d(5), dmesg(1), kernel.org documentation (admin-guide,
# filesystems/proc), The Linux Programming Interface (Kerrisk) chapters 2 and 3.
# Real boxes run strace 6.8 and Python 3 in the build container (Ubuntu 24.04) as the user learner, and a network
# namespace for /sys/class/net so that the build host’s own devices are not shown. The kernel release of the build
# host is never printed.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('layers', 'User space, kernel space and the system call', f'''
<p>The <b>kernel</b> is the one program that runs with full control of the hardware. Everything else, from bash to a web browser, runs in <b>user space</b> with limited rights. When a program needs anything the kernel controls, it makes a <b>system call</b>.</p>
{table(['The kernel manages', 'What that means', 'System calls you meet'], [
    ['processes', 'starts and stops programs and shares the CPUs between them', '<code>fork</code>, <code>execve</code>, <code>wait4</code>, <code>exit_group</code>, <code>kill</code>'],
    ['memory', 'gives each process its own address space', '<code>mmap</code>, <code>brk</code>, <code>munmap</code>'],
    ['files', 'one tree of names over many file systems (the VFS)', '<code>openat</code>, <code>read</code>, <code>write</code>, <code>close</code>, <code>stat</code>'],
    ['devices', 'drivers for disks, network cards, keyboards', '<code>ioctl</code>, plus read and write on device files'],
    ['networking', 'TCP/IP, sockets, the firewall', '<code>socket</code>, <code>connect</code>, <code>accept</code>, <code>sendto</code>'],
    ['security', 'users, permissions, capabilities, namespaces', '<code>setuid</code>, <code>capset</code>, <code>unshare</code>']])}
{steps('What happens in one call such as read()', [
    'The program calls <code>read(fd, buf, n)</code>, a normal C function in the C library (glibc on Ubuntu).',
    'glibc puts the system call number and the arguments in CPU registers and runs the <code>syscall</code> instruction. The CPU switches to kernel mode.',
    'The kernel checks the arguments (is fd open, may this process write to buf), does the work, and puts the result in a register.',
    'The CPU returns to user mode. On error the kernel returns a negative number, and glibc turns it into -1 plus a code in the variable <code>errno</code>.'])}
{play('lx-syscall')}
{talk('The kernel is the heart of the operating system, and the only program with full control of the hardware. All other programs run in user space with limited rights, so they cannot touch the disk, the network or the screen directly. Instead they ask the kernel with a system call, such as open, read, write or fork. The C library wraps each system call in a normal function, and a special C P U instruction switches into the kernel and back. If something goes wrong, the call returns minus one and sets an error code called errno, for example E N O E N T for a missing file. Pick a command in the animation and follow its system calls one by one. Every line is real strace output.')}
''', kw=['kernel', 'user space', 'kernel space', 'kernel mode', 'system call', 'syscall', 'glibc', 'libc wrapper', 'errno', 'ENOENT', 'EACCES', 'VFS', 'monolithic kernel', 'execve', 'openat', 'read', 'write', 'mmap', 'fork'])

K.lesson('strace', 'Watching system calls with strace', f'''
{cmdtable([
    ('strace CMD', 'Print every system call of a command, with arguments and results', 'strace ls'),
    ('strace -e trace=SET CMD', 'Only some calls: a list, or groups such as file, network, process, memory', 'strace -e trace=openat,read cat notes.txt'),
    ('strace -f CMD', 'Follow child processes too', 'strace -f bash script.sh'),
    ('strace -c CMD', 'Count calls and time instead of printing them', 'strace -c ls'),
    ('strace -o FILE CMD', 'Write the trace to a file, so it does not mix with the output', 'strace -o trace.txt make'),
    ('strace -p PID', 'Attach to a running process (needs root or the same user)', 'sudo strace -p 905'),
    ('ltrace CMD', 'Library calls instead of system calls', 'ltrace -e strlen echo hi')])}
{run('Read a file, fail on a missing one, and count the calls', """echo hello > hello.txt
strace -e trace=openat,read,write,close -o t1.txt cat hello.txt
sed -n '/hello.txt/,$p' t1.txt
strace -o t2.txt cat missing.txt
grep -e missing -e 'write(2' -e exit_group t2.txt
strace -c -o t3.txt ls > /dev/null
sort -k4 -n -r t3.txt | head -n 6""", note='The first trace shows the lines that matter: openat returns file descriptor 3, read copies the 6 bytes, write sends them to descriptor 1, and a read that returns 0 means end of file. (sed starts the listing at hello.txt and hides the loader opening libc and the locale files before it.) For a missing file, openat returns -1 with ENOENT, and cat writes the familiar message to descriptor 2 before exit_group(1). strace -c counts every call. Most of them happen before ls does any real work: the loader maps libc into memory (mmap), and the C library opens the locale files, which is where the failed openat calls come from.')}
{run('Find the config file a script is looking for', """printf '%s\\n' 'cfg=$HOME/.config/shop/app.conf' '[ -r "$cfg" ] && . "$cfg"' 'cat /etc/shop.conf 2>/dev/null || echo "no config found"' > app.sh
bash app.sh
strace -f -e trace=file -o t.txt bash app.sh
grep shop t.txt | sed 's/^[0-9]* *//'""", note='The script only says “no config found”. trace=file shows every call that takes a file name, and -f follows the cat child. The two ENOENT lines name the exact paths it tried, ~/.config/shop/app.conf and /etc/shop.conf. This trick works for any program that does not say where it looks: a missing library, a plugin folder or a certificate file. (sed removes the process id that -f puts in front of each line.)')}
{run('errno numbers and their messages', """python3 -c 'import errno, os
for n in (1, 2, 13, 17, 28): print(n, errno.errorcode[n], os.strerror(n))'""", note='These are the codes behind messages you see every day. EPERM and EACCES both mean “not allowed”: EPERM for actions only privileged processes may do, EACCES for missing file permissions. The full list is in man 3 errno, and the numbers are the same in every language.')}
{note('strace slows a program down a lot, because the kernel stops it at every call. Use it to find out what a program does, not to measure how fast it is. On production servers, <code>perf trace</code> or eBPF tools such as <code>opensnoop</code> from bpfcc-tools watch the same calls with much less cost.', 'tip')}
{talk('Strace shows every system call a program makes, with its arguments and its result. That makes it one of the best debugging tools on Linux, because programs cannot hide what they ask the kernel. With dash e trace, you pick which calls to see, for example only file calls. Dash f follows child processes, dash c counts the calls, and dash o writes the trace to a file. In the demo, a script only says no config found. Strace shows the two exact paths it looked for, both ending in E N O E N T, no such file. That is how admins find missing config files, libraries and certificates in minutes instead of hours.')}
''', kw=['strace', 'strace -e trace', 'strace -f', 'strace -c', 'strace -o', 'strace -p', 'trace=file', 'ltrace', 'errno', 'strerror', 'EPERM', 'EACCES', 'ENOENT', 'missing config file', 'perf trace', 'opensnoop', 'eBPF'])

K.lesson('proc', '/proc and /sys: the kernel as files', f'''
<p>The kernel shows its own state as files. <code>/proc</code> (procfs) has a folder for every process and many system-wide files. <code>/sys</code> (sysfs) has the devices, drivers and kernel objects. The files take no disk space: the kernel writes their content at the moment you read them.</p>
{table(['Path', 'What it shows'], [
    ['<code>/proc/PID/status</code>', 'name, state, parent, user ids, memory, capabilities of a process'],
    ['<code>/proc/PID/cmdline</code>, <code>environ</code>', 'the command line and the environment, separated by NUL bytes'],
    ['<code>/proc/PID/fd/</code>', 'one link per open file descriptor'],
    ['<code>/proc/PID/cwd</code>, <code>exe</code>', 'links to the current folder and the program file'],
    ['<code>/proc/self</code>', 'a link to the folder of whoever reads it'],
    ['<code>/proc/meminfo</code>, <code>loadavg</code>, <code>uptime</code>', 'memory, load average, seconds since boot (free, uptime and top read these)'],
    ['<code>/proc/cmdline</code>', 'the kernel command line from the boot loader'],
    ['<code>/proc/sys/</code>', 'kernel settings, the same as sysctl names with dots instead of slashes'],
    ['<code>/sys/class/net/</code>, <code>/sys/block/</code>', 'network interfaces and block devices with their properties']])}
{run('Look at a process from the inside', """grep -E '^(Name|State|Pid|PPid|Uid)' /proc/self/status
ls -l /proc/self/fd 9>&- | awk 'NR > 1 {print $1, $9, $10, $11}'
readlink /proc/self/exe
sleep 30 &
xargs -0 echo < /proc/$!/cmdline
ls /proc/$! | head -n 8
kill $!
cat /proc/sys/kernel/pid_max
cat /proc/sys/kernel/ostype""", note='/proc/self is a different folder for every reader. When grep reads it, the status is grep’s own: its name, state R (running), its process id and its parent, the shell. ls shows its own open descriptors: 0, 1 and 2, plus 3 for the folder it is reading. Here 0, 1 and 2 are a socket and pipes, because this page is built by a program, not in a terminal. In a terminal all three point to /dev/pts/N. cmdline separates the words with NUL bytes, which xargs -0 reads. pid_max is the highest process id before numbers start again from the bottom. The build container uses the kernel default 32768, while Ubuntu 24.04 raises it to 4194304 at boot with /usr/lib/sysctl.d/50-pid-max.conf.')}
{run('/sys inside a small network namespace', """ip netns add lab
ip -n lab link add veth0 type veth peer name veth1
ip netns exec lab ls /sys/class/net
ip netns exec lab cat /sys/class/net/veth0/mtu
ip netns exec lab cat /sys/class/net/veth0/operstate
ip -n lab link set veth0 up
ip -n lab link set veth1 up
ip netns exec lab cat /sys/class/net/veth0/operstate
ip netns delete lab""", note='Every interface has a folder in /sys/class/net with one small file per property, which is where ip and other tools read them. The box uses a network namespace so you see only its own interfaces, lo and a veth pair (ip netns exec mounts a matching /sys). operstate changes from down to up when both ends of the pair are up.', root=True)}
{talk('The kernel publishes its state as files, so you can read it with cat. Slash proc has a folder for every running process, named after its process id. Inside are the status, the command line, the open file descriptors and links to the program and its current folder. Slash proc slash self always points to the process that reads it. Slash proc also holds system wide files such as meminfo and loadavg, which is where free, uptime and top get their numbers, and slash proc slash sys holds the kernel settings that sysctl changes. Slash sys describes devices and drivers, for example one folder per network interface with its M T U and its state. None of these files exist on a disk: the kernel writes their content at the moment you read them.')}
''', kw=['/proc', 'procfs', '/proc/PID', '/proc/self', '/proc/PID/status', '/proc/PID/cmdline', '/proc/PID/fd', '/proc/PID/environ', '/proc/meminfo', '/proc/loadavg', '/proc/cmdline', '/proc/sys', 'sysfs', '/sys', '/sys/class/net', 'pid_max', 'operstate', 'virtual file system'])

K.lesson('modules', 'Kernel versions, modules and the kernel log', f'''
{cmdtable([
    ('uname -r, uname -a', 'Kernel release, and everything uname knows', 'uname -r'),
    ('lsmod', 'Loaded modules, their size and who uses them (reads /proc/modules)', 'lsmod | head'),
    ('modinfo NAME', 'File, description, license, parameters of a module', 'modinfo ext4'),
    ('modprobe NAME, modprobe -r NAME', 'Load a module with the modules it needs, or remove it', 'sudo modprobe wireguard'),
    ('/etc/modules-load.d/*.conf', 'Modules to load at every boot, one name per line', 'echo wireguard | sudo tee /etc/modules-load.d/wg.conf'),
    ('/etc/modprobe.d/*.conf', 'Options and blacklists for modules', 'blacklist pcspkr'),
    ('dmesg, journalctl -k', 'The kernel ring buffer: drivers, disks, out of memory kills', 'sudo dmesg -T | tail'),
    ('cat /proc/cmdline', 'Boot options the kernel got from GRUB', 'cat /proc/cmdline')])}
{steps('How Linux grows without a reboot', [
    'Linux is a <b>monolithic</b> kernel: drivers and file systems run inside the kernel, in kernel space. To keep the kernel small, most of them are built as <b>loadable modules</b>, files ending in <code>.ko</code> (or .ko.zst, compressed) under <code>/lib/modules/$(uname -r)/</code>.',
    'When the system finds new hardware, udev asks the kernel to load the matching module. modprobe looks the name up in <code>modules.dep</code> and loads the modules it depends on first.',
    'Settings for a module go in a file in /etc/modprobe.d/, such as <code>options kvm_intel nested=1</code>. A <code>blacklist NAME</code> line stops automatic loading.',
    'The kernel package (linux-image on Ubuntu) brings the kernel and its modules for one release. Old releases stay installed until apt autoremove, so you can boot an older one from the GRUB menu if a new one fails.'])}
{shape('Ubuntu kernel release names', """6.8.0-48-generic
│ │ │  │   └── flavour: generic, lowlatency, aws, azure, ...
│ │ │  └────── Ubuntu’s build number of this release
│ │ └───────── patch level from kernel.org (0 here)
│ └─────────── minor version
└───────────── major version""", note='Ubuntu 24.04 LTS started with the 6.8 kernel and later offers newer ones through the HWE (hardware enablement) packages. A reboot is needed to run a new kernel, and /var/run/reboot-required says so after an update.')}
{note('Kernel messages are key in a crisis: “Out of memory: Killed process”, I/O errors from a failing disk, a driver that crashed. dmesg shows them since boot. On Ubuntu reading it needs sudo (kernel.dmesg_restrict = 1). journalctl -k -b -1 shows the kernel messages of the boot before, which helps after a crash.', 'tip')}
{talk('Linux is a monolithic kernel, which means drivers and file systems run inside the kernel itself. To stay small, most of them are loadable modules, files ending in dot k o that the kernel loads when it needs them. Lsmod lists the loaded modules, modinfo describes one, and modprobe loads a module together with the modules it depends on. Files in slash etc slash modprobe dot d give options or blacklist a module, and files in modules load dot d load modules at every boot. Uname dash r shows the kernel release you are running, and the kernel log, read with dmesg or journalctl dash k, shows what drivers and disks have been doing, including out of memory kills.')}
''', kw=['uname -r', 'kernel release', 'kernel module', 'loadable module', '.ko', 'lsmod', 'modinfo', 'modprobe', 'modprobe -r', 'modules.dep', 'modprobe.d', 'blacklist', 'modules-load.d', 'udev', 'dmesg', 'journalctl -k', 'dmesg_restrict', '/proc/cmdline', 'linux-image', 'HWE kernel', 'monolithic kernel'])

K.lesson('practice', 'Practice: explore the kernel through /proc', f'''
<p>Use /proc to answer questions about the practice server and about your own shell.</p>
{lab('Kernel facts from /proc', [
    ('Print the kernel release.', 'uname -r', [{'out': r'^6\.8\.0'}]),
    ('Show the kernel version line from /proc.', 'cat /proc/version', [{'out': '^Linux version'}]),
    ('Show the boot options the kernel got.', 'cat /proc/cmdline', [{'out': 'root=UUID='}]),
    ('Count the CPUs.', 'nproc', [{'out': r'^\d+$'}]),
    ('Show the line MemTotal of /proc/meminfo.', 'grep MemTotal /proc/meminfo', [{'out': r'^MemTotal:\s+\d+ kB'}]),
    ('Show the load averages.', 'cat /proc/loadavg', [{'out': r'^\d+\.\d\d \d+\.\d\d \d+\.\d\d'}]),
    ('Print the process id of your shell.', 'echo $$', [{'out': r'^\d+$'}]),
    ('Show the lines Name, State and PPid of /proc/self/status.', "grep -E '^(Name|State|PPid)' /proc/self/status", [{'out': r'PPid:\s+\d+'}]),
    ('List the open file descriptors of your shell with ls -l.', 'ls -l /proc/$$/fd', [{'out': r'255 -> /dev/pts/0'}]),
    ('Print the program file behind /proc/self/exe.', 'readlink /proc/self/exe', [{'out': 'readlink$'}]),
    ('Show the highest possible process id.', 'cat /proc/sys/kernel/pid_max', [{'out': r'^\d+$'}])])}
{talk('Time to explore the kernel yourself. Print the kernel release and the version line, and the boot options the kernel received. Count the C P Us, find the total memory in meminfo and read the load averages. Then look at processes: print the process id of your shell, read the status of slash proc slash self, and list the open file descriptors of your shell, including two five five, which bash keeps for itself. Finally, see which program reads slash proc slash self slash exe, and how high process ids can go.')}
''', kw=['/proc lab', 'kernel lab', 'meminfo practice', 'proc self practice'])

K.lesson('levels', 'The kernel from school to research', f'''
{ladder(
    '<p>The kernel is the boss of the computer: it decides which program runs, keeps programs from touching each other’s memory, and talks to the hardware. Programs ask it for help with system calls.</p>',
    '<p>Use strace to see what programs ask for, read process and system state in /proc, devices in /sys, settings with sysctl, and manage modules with modprobe. Read the kernel log after crashes and keep at least one older kernel installed.</p>',
    '<p>Kernel and platform teams build their own kernels with extra patches, tune scheduler and memory settings, use live patching (Canonical Livepatch, kpatch) to fix security holes without a reboot, and observe production with perf and eBPF tools such as bpftrace. Container platforms rely on namespaces, cgroups and seccomp filters that limit which system calls a program may make.</p>',
    '<p>Research looks at new kernel designs (microkernels such as seL4, which is formally verified, unikernels and library operating systems), Rust in the Linux kernel (merged in 6.1), io_uring, which queues system calls in shared memory to avoid the cost of crossing into the kernel, and the security of the user and kernel border after attacks such as Meltdown and Spectre.</p>')}
{scene('the program that hung at start-up', '<p>After a move to new servers, an in-house reporting tool hung for exactly 30 seconds every time it started, and then worked. Its logs showed nothing. An admin ran it under <code>strace -f -tt -e trace=network</code> and saw a connect() to an old licence server address that no longer existed, which waited until the timeout. The address came from a forgotten line in /etc/hosts. Fixing that line made the tool start in under a second.</p>')}
{talk('Here is how understanding the kernel grows. At school you learn that the kernel is the boss of the computer, and that programs ask it for help. Professionals use strace, slash proc, slash sys, sysctl and the kernel log every week to find out why something fails. Platform teams patch kernels while they run, observe production servers with e B P F, and limit which system calls containers may make. Researchers design verified microkernels, bring the Rust language into Linux, and invent faster ways to cross the border between programs and the kernel, such as io uring.')}
''', kw=['microkernel', 'seL4', 'unikernel', 'Rust for Linux', 'io_uring', 'live patching', 'Livepatch', 'kpatch', 'eBPF', 'bpftrace', 'seccomp', 'Meltdown', 'Spectre'])

K.quiz('e', 'Which program has full control of the hardware?', ['bash', 'The kernel', 'systemd', 'The BIOS'], 1, 'The core.', 'Everything else runs in user space.')
K.quiz('e', 'How does a program ask the kernel to open a file?', ['It writes to the disk itself', 'With a system call such as openat', 'Through /etc/fstab', 'With sudo'], 1, 'Ask the kernel.', 'libc wraps it in open().')
K.quiz('e', 'Which tool prints the system calls of a command?', ['top', 'strace', 'grep', 'lsmod'], 1, 'System call trace.', 'strace CMD.')
K.quiz('e', 'Where does Linux show a folder for every running process?', ['/var/run', '/proc', '/sys', '/tmp'], 1, 'Processes.', 'Named after the process id.')
K.quiz('m', 'A system call fails. What does the C library function usually return?', ['0', '-1, with the reason in errno', 'NULL always', 'It exits the program'], 1, 'Minus one.', 'errno holds a code such as ENOENT.')
K.quiz('m', 'What does ENOENT mean?', ['Permission denied', 'No such file or directory', 'Disk full', 'File exists'], 1, 'No entry.', 'errno 2.')
K.quiz('m', 'Which strace option also follows child processes?', ['-c', '-f', '-o', '-p'], 1, 'Fork.', 'Needed for scripts.')
K.quiz('m', 'What is /proc/self?', ['The root folder', 'A link to the /proc folder of the process that reads it', 'The kernel itself', 'The first process'], 1, 'Whoever reads it.', 'So cat /proc/self/status shows cat.')
K.quiz('m', 'Which command loads a module with the modules it depends on?', ['insmod', 'modprobe', 'lsmod', 'modinfo'], 1, 'Probe.', 'It reads modules.dep.')
K.quiz('h', 'Why do the files in /proc show size 0 in ls -l?', ['They are empty', 'The kernel makes their content at the moment you read them', 'They are broken links', 'Only root can see the size'], 1, 'Virtual.', 'No disk space is used.')
K.quiz('h', 'What is the difference between EPERM and EACCES?', ['None', 'EPERM: only a privileged process may do it, EACCES: file permissions forbid it', 'EPERM is for networks', 'EACCES means the file is missing'], 1, 'Privilege or permission.', 'errno 1 and 13.')
K.quiz('h', 'How do you stop a module from loading automatically?', ['Delete it', 'A blacklist line in a file in /etc/modprobe.d/', 'chmod 000 on it', 'Remove it from /proc/modules'], 1, 'Blacklist.', 'modprobe -r removes it now.')
K.quiz('h', 'Why does strace -c ls show many mmap calls?', ['ls is slow', 'The loader maps libc and other libraries into memory before main() runs', 'ls reads every file', 'mmap is how ls prints'], 1, 'Before main.', 'mprotect follows.')
K.quiz('x', 'What does io_uring change about system calls?', ['Nothing', 'Requests go through rings in shared memory, so many I/O operations need few or no border crossings', 'It removes the kernel', 'It only works for networking'], 1, 'Shared rings.', 'Less cost per operation.')

K.calc('e', 'strace -c counted 17 mmap, 8 close and 7 fstat calls. How many is that together?', '32', 'Add them.', ['17 + 8 = 25.', '25 + 7.', eq('32 calls')], check=32)
K.calc('e', 'A program has file descriptors 0, 1 and 2 open and opens two files. Which number does the second file get?', '4', 'Lowest free number.', ['The first file gets 3.', 'The second gets the next free one.', eq('fd 4')], check=4)
K.calc('m', 'A system call costs about 100 ns. A program makes 2 million of them. How many milliseconds is that?', '200', 'Multiply, then convert.', ['2 000 000 × 100 ns = 200 000 000 ns.', '1 ms = 1 000 000 ns.', eq('200 ms')], check=200)
K.calc('m', 'read() asks for 131072 bytes at a time. How many reads does cat need for a 1 MiB file, not counting the last empty read?', '8', 'Divide.', ['1 MiB = 1048576 bytes.', '1048576 ÷ 131072.', eq('8 reads')], check=8)
K.calc('h', '/proc/uptime shows 268860 seconds. How many whole days is that?', '3', 'Seconds per day.', ['A day has 86400 seconds.', '268860 ÷ 86400 = 3.1.', eq('3 days')], check=3)
K.calc('h', 'MemTotal is 8048304 kB and MemAvailable is 5563880 kB. What percent is available, rounded?', '69', 'Divide and times 100.', ['5563880 ÷ 8048304 = 0.691.', '× 100.', eq('69 %')], check=69)
K.calc('x', 'strace makes a program 40 times slower. Normally it runs in 0.5 s. How long under strace?', '20', 'Multiply.', ['0.5 s × 40.', 'That is why strace is not for timing.', eq('20 s')], check=20)

K.must('Two worlds', 'The kernel runs in kernel mode with full control. Programs run in user space and ask with system calls, wrapped by libc. Errors return -1 with errno (ENOENT, EACCES, EPERM).')
K.must('strace', 'strace -e trace=file|network|process, -f for children, -c to count, -o FILE, -p PID. Look for -1 ENOENT to find missing files.')
K.must('/proc', '/proc/PID/status, cmdline, environ, fd/, cwd, exe. /proc/self. meminfo, loadavg, uptime, cmdline. /proc/sys equals sysctl.')
K.must('/sys', 'Devices and drivers as small files, for example /sys/class/net/IFACE/mtu and operstate.')
K.must('Modules', 'uname -r, lsmod, modinfo, modprobe and modprobe -r, /etc/modprobe.d (options, blacklist), /etc/modules-load.d, dmesg and journalctl -k.')

T = K.topic(
    slug='kernel-syscalls', topic='kernel-syscalls',
    step=(1, 'Kernel and processes', 'lx-adv-1', 'Look under the shell: how programs ask the kernel for everything with system calls, how the kernel shows its state in /proc and /sys, and how processes are born, run and die.', 'Expert'),
    title='The kernel and system calls: strace, /proc, /sys and modules', short='Kernel and system calls', badge='1.1', minutes=55, added='2026-11-24',
    lead='See how every program depends on the kernel: what crosses the border between user space and kernel space, how to watch it with strace, how the kernel shows its state in /proc and /sys, and how modules add drivers while it runs.',
    desc='What the kernel manages, user space and kernel space, system calls and libc wrappers, errno, strace with -e, -f, -c and -o, ltrace, /proc per process and system wide, /proc/sys, /sys, kernel releases, lsmod, modinfo, modprobe, modprobe.d and the kernel log, with real strace runs on Ubuntu 24.04.',
    summary='User and kernel space, system calls, strace, /proc, /sys, modules.',
    keywords=['kernel', 'system call', 'syscall', 'strace', 'ltrace', 'errno', '/proc', '/sys', 'procfs', 'sysfs', 'kernel module', 'modprobe', 'lsmod', 'dmesg', 'uname'],
    recap='<p>Programs run in user space and get everything from the kernel through system calls, which libc wraps and which return -1 and an errno on failure. strace shows those calls and quickly reveals missing files. The kernel shows processes and settings in /proc, devices in /sys, and loads drivers as modules with modprobe.</p>')
