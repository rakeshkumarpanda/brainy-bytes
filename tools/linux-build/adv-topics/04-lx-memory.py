# Internals and advanced 2.2: memory. Virtual address spaces, pages and page tables, the layout of a process
# (/proc/PID/maps), VSZ and RSS, demand paging and page faults, copy on write after fork, PSS, reading free and
# /proc/meminfo, reclaim of page cache, swap and swappiness, overcommit, the OOM killer and oom_score_adj, memory
# limits with cgroups and systemd, and pressure stall information.
# Sources: proc(5) (maps, smaps_rollup, status, meminfo, oom_score_adj, pressure), mmap(2), brk(2), fork(2), free(1),
# vmstat(8), getrusage(2), the kernel documentation (admin-guide/mm/concepts.rst, admin-guide/sysctl/vm.rst
# swappiness and overcommit_memory, mm/overcommit-accounting.rst, accounting/psi.rst, admin-guide/cgroup-v2.rst
# memory.max and memory.events), systemd.resource-control(5) MemoryMax=, the Ubuntu Server guide.
# Real boxes run Python in the build container: a 1 GiB mapping that is only partly touched, copy on write after
# fork, the memory map of grep, and a real OOM kill inside a memory cgroup with a 100 MiB limit. The build container
# still uses cgroup v1, so that box names the v1 files and the lesson explains the v2 files of Ubuntu 24.04.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('virtual', 'Virtual memory, pages and page faults', f'''
<p>Every process sees its own <b>virtual address space</b>, as if it had the whole memory to itself. The kernel and the CPU’s memory management unit (MMU) translate each virtual address to a real place in RAM, one <b>page</b> (4 KiB on x86-64) at a time, using the process’s <b>page table</b>.</p>
{table(['Term', 'Meaning'], [
    ['page and frame', 'a 4 KiB piece of virtual memory, and the 4 KiB piece of RAM that holds it'],
    ['VSZ (VmSize)', 'all virtual memory the process has mapped, used or not'],
    ['RSS (VmRSS)', 'the part that is in RAM right now, shared pages included'],
    ['minor page fault', 'the page gets a frame without disk I/O (a fresh zero page, or a page already in the cache)'],
    ['major page fault', 'the page must be read from disk (swap or a file), which takes milliseconds'],
    ['ASLR', 'address space layout randomisation: the kernel puts stack, heap and libraries at random addresses each run (kernel.randomize_va_space = 2)']])}
{play('lx-vm')}
{run('Map 1 GiB, use 200 MiB, and count the page faults', """cat > lazy.py <<'EOF'
import mmap, resource

def show(label):
    with open("/proc/self/status") as f:
        v = {k: x.split()[0] for k, x in (l.split(":", 1) for l in f) if k in ("VmSize", "VmRSS")}
    faults = resource.getrusage(resource.RUSAGE_SELF).ru_minflt
    print(f"{label:<17} VmSize {int(v['VmSize']) // 1024:>5} MiB  VmRSS {int(v['VmRSS']) // 1024:>4} MiB  faults {faults}")

show("start")
m = mmap.mmap(-1, 1024 * 2**20)
show("1 GiB mapped")
for i in range(0, 200 * 2**20, 4096):
    m[i] = 1
show("200 MiB touched")
m.close()
show("unmapped")
EOF
python3 lazy.py""", note='Mapping 1 GiB raises VmSize by 1024 MiB at once, but RSS stays the same, because no page has a frame yet. Writing one byte in every 4 KiB page of the first 200 MiB causes one minor page fault per page: 200 × 256 = 51200 more faults, and RSS grows by 200 MiB. Unmapping gives everything back. This demand paging is why VSZ alone says little about how much RAM a program really needs.')}
{run('The memory map of a process', """grep -E 'grep|heap|stack|vdso|libc' /proc/self/maps | awk '{print $1, $2, $6}'""", note='Each line of /proc/PID/maps is one mapping: an address range, the permissions (r read, w write, x execute, p private copy on write), and what is behind it. The program file appears several times, once per part: code is r-xp, data rw-p. [heap] grows with brk and [stack] with function calls, and [vdso] is a small piece of kernel code mapped into every process so that calls such as clock_gettime need no system call. The addresses change on every run because of ASLR.')}
{talk('Every process lives in its own virtual address space, as if it owned all the memory. The kernel and the C P U translate virtual addresses into real memory, one four kilobyte page at a time. Memory is handed out lazily: when a program asks for a gigabyte, the kernel only notes the range. Real memory is attached the first time each page is touched, through a page fault. That is why the virtual size of a program, V S Z, is often much bigger than its resident size, R S S. The demo maps one gigabyte, touches two hundred megabytes, and you can count exactly one fault per page. The memory map in slash proc shows each mapping: the program, its libraries, the heap and the stack.')}
''', kw=['virtual memory', 'virtual address space', 'page', 'page frame', 'page table', 'MMU', 'VSZ', 'RSS', 'VmSize', 'VmRSS', 'page fault', 'minor fault', 'major fault', 'demand paging', 'mmap', 'brk', 'heap', 'stack', '/proc/PID/maps', 'vdso', 'ASLR', 'randomize_va_space'])

K.lesson('cow', 'Copy on write and shared memory', f'''
{run('fork shares pages until someone writes', """cat > cow.py <<'EOF'
import os, resource

def faults():
    return resource.getrusage(resource.RUSAGE_SELF).ru_minflt

data = bytearray(100 * 2**20)
pid = os.fork()
if pid == 0:
    before = faults()
    total = sum(data[::4096])
    after_read = faults()
    for i in range(0, 40 * 2**20, 4096):
        data[i] = 1
    print(f"child: reading 100 MiB caused {after_read - before} faults")
    print(f"child: writing 40 MiB caused {faults() - after_read} faults", flush=True)
    os._exit(0)
os.waitpid(pid, 0)
EOF
python3 cow.py""", note='After fork the child shares all 100 MiB with its parent. Reading every page costs almost nothing (the few faults come from Python’s own work). Writing 40 MiB causes about 40 × 256 = 10240 faults, one per page, because each written page must first be copied into a frame of the child’s own. The other 60 MiB stay shared. (flush=True matters here: os._exit skips the normal clean-up that would empty Python’s output buffer.)')}
{table(['Memory that is shared', 'Example'], [
    ['code of programs and libraries', 'every bash process uses the same frames for /usr/bin/bash and libc'],
    ['copy on write pages after fork', 'web server workers forked from one master'],
    ['shared memory', 'shm_open, /dev/shm, PostgreSQL shared_buffers'],
    ['the page cache', 'a file read by ten programs is in RAM only once']])}
{cmdtable([
    ('grep -E "^(Rss|Pss)" /proc/PID/smaps_rollup', 'RSS, and PSS, where each shared page is divided among the processes that share it', 'grep -E "^(Rss|Pss)" /proc/$$/smaps_rollup'),
    ('ps -o pid,vsz,rss,comm', 'VSZ and RSS in KiB per process', 'ps -o pid,vsz,rss,comm -C nginx'),
    ('ps aux --sort=-rss | head', 'The biggest users of RAM first', 'ps aux --sort=-rss | head -n 5'),
    ('pmap -x PID', 'The mappings with their RSS, a friendlier view of maps', 'pmap -x $$ | tail -n 3')])}
{note('Adding up the RSS of every process counts shared pages many times, so the sum can be bigger than the RAM in the machine. Use PSS when you need a fair total per program, or look at the cgroup’s memory.current for a whole service.', 'tip')}
{talk('When a process forks, the kernel does not copy its memory. Parent and child share the same pages, marked read only. Only when one of them writes to a page does the kernel copy that page, which is called copy on write. That keeps fork fast, even for big programs. In the demo, the child reads one hundred megabytes for free, and writing forty megabytes causes one fault per copied page. Programs also share their code and libraries, and files in the page cache are in memory only once. That is why adding up the R S S of all processes gives too much. P S S divides each shared page fairly between the processes that use it.')}
''', kw=['copy on write', 'COW', 'fork memory', 'shared pages', 'shared memory', 'shm', '/dev/shm', 'PSS', 'smaps_rollup', 'pmap', 'ps --sort=-rss', 'vsz rss', 'shared libraries'])

K.lesson('free', 'Reading free, meminfo and swap', f'''
{shape('free -h on the practice server', """               total        used        free      shared  buff/cache   available
Mem:           7.7Gi       2.1Gi       3.0Gi       120Mi       2.6Gi       5.3Gi
Swap:          2.0Gi          0B       2.0Gi""", note='This is what free -h prints in the practice shell. used is memory programs hold, buff/cache is the page cache and kernel buffers, and available estimates how much new programs can get without swapping, cache that can be dropped included. A server with little free but plenty available is healthy.')}
{table(['/proc/meminfo line', 'Meaning'], [
    ['MemTotal, MemFree', 'all usable RAM, and RAM that holds nothing at all'],
    ['MemAvailable', 'the kernel’s estimate of memory available for new work (what free calls available)'],
    ['Buffers, Cached', 'block device buffers and the page cache'],
    ['Dirty, Writeback', 'cache pages waiting to be written, and pages being written now'],
    ['AnonPages', 'memory with no file behind it: heaps and stacks'],
    ['SwapTotal, SwapFree', 'swap space and how much of it is unused'],
    ['Committed_AS, CommitLimit', 'memory promised to programs, and the limit used when overcommit is strict (mode 2)']])}
{table(['Setting', 'Default on Ubuntu 24.04', 'What it does'], [
    ['<code>vm.swappiness</code>', '60', '0 to 200: how much the kernel prefers swapping anonymous pages over dropping cache. Lower it on databases, raise it with zram'],
    ['<code>vm.overcommit_memory</code>', '0', '0 heuristic overcommit, 1 always allow, 2 never promise more than CommitLimit'],
    ['<code>vm.vfs_cache_pressure</code>', '100', 'how eagerly the kernel frees cached inodes and folder entries'],
    ['<code>vm.min_free_kbytes</code>', 'set at boot from RAM size', 'memory the kernel keeps free for emergencies']])}
{steps('Is the machine short of memory', [
    'Look at <code>available</code> in free -h, not at free. Under about 10 % of total means pressure.',
    'Run <code>vmstat 1 5</code>. Non-zero <b>si</b> and <b>so</b> (swap in and out) in every line means the machine swaps all the time.',
    'Read <code>/proc/pressure/memory</code>. The some avg10 value is the share of the last 10 seconds in which at least one task waited for memory.',
    'Search the kernel log: <code>journalctl -k | grep -i "out of memory"</code>.',
    'Find the biggest users with <code>ps aux --sort=-rss | head</code> or <code>systemd-cgtop -m</code> per service.'])}
{talk('Free shows the memory of the whole machine. Do not worry when free is small: Linux uses spare memory as page cache, shown as buff slash cache, and gives it back the moment programs need it. The column to watch is available. Slash proc slash meminfo has the details, such as how much memory is dirty and waiting to be written, and how much swap is used. Swappiness, sixty by default, sets how much the kernel prefers swapping out idle program memory over dropping file cache. To check for a real memory shortage, look at available, at the s i and s o columns of vmstat, which show swapping, at the memory pressure file, and at the kernel log for out of memory kills.')}
''', kw=['free', 'free -h', 'available memory', 'buff/cache', '/proc/meminfo', 'MemAvailable', 'MemFree', 'Dirty', 'AnonPages', 'Committed_AS', 'swap', 'swappiness', 'vm.swappiness', 'overcommit_memory', 'vfs_cache_pressure', 'min_free_kbytes', 'vmstat si so', 'PSI', '/proc/pressure/memory', 'memory pressure'])

K.lesson('oom', 'The OOM killer and memory limits', f'''
{steps('What happens when memory runs out', [
    'The kernel first reclaims: it drops clean page cache, writes dirty pages back, and swaps anonymous pages out if there is swap.',
    'If that is not enough, the <b>OOM killer</b> (out of memory) gives every process a badness score, mainly from how much memory it uses, adjusted by <code>/proc/PID/oom_score_adj</code> from −1000 (never kill) to 1000 (kill first). <code>/proc/PID/oom_score</code> shows the result.',
    'It sends SIGKILL to the process with the highest score. The shell shows “Killed” and status 137, and the kernel log has a line “Out of memory: Killed process PID (name)”.',
    'With a cgroup memory limit, the same happens inside the group only: the service that hit its own limit is killed, and the rest of the machine is fine.'])}
{run('A real OOM kill inside a 100 MiB memory cgroup', """mkdir /sys/fs/cgroup/memory/demo
echo 100M > /sys/fs/cgroup/memory/demo/memory.limit_in_bytes
cat /sys/fs/cgroup/memory/demo/memory.limit_in_bytes
bash -c 'echo $$ > /sys/fs/cgroup/memory/demo/cgroup.procs
exec python3 -c "
a = bytearray(50 * 2**20); print(\\"50 MiB ok\\", flush=True)
b = bytearray(200 * 2**20); print(\\"250 MiB ok\\")"'
echo "status $?"
grep oom_kill /sys/fs/cgroup/memory/demo/memory.oom_control
rmdir /sys/fs/cgroup/memory/demo""", note='The bash moves itself into the cgroup and then becomes Python (exec). The first 50 MiB fit inside the 100 MiB limit. The next 200 MiB do not, so the kernel kills Python with SIGKILL, and the shell reports status 137. The cgroup counts the kill (oom_kill 1), while the rest of the machine never noticed. The build container uses the older cgroup v1 files. On Ubuntu 24.04, which uses cgroup v2, the limit is the file memory.max and the kill count is in memory.events.', root=True)}
{shape('Limits for a service on Ubuntu 24.04 (systemctl edit shop.service)', """[Service]
MemoryHigh=800M
MemoryMax=1G
MemorySwapMax=0
OOMScoreAdjust=500""", note='MemoryHigh slows the service down and reclaims its memory hard when it goes above 800M. MemoryMax is the hard limit where the OOM killer acts inside the service. OOMScoreAdjust makes it the preferred victim if the whole machine runs out. systemctl status shows the memory in use and the peak, and systemd-cgtop shows all services.')}
{note('Java, Node.js and databases manage their own heaps. Set their limits (for example -Xmx for Java, --max-old-space-size for Node.js, shared_buffers for PostgreSQL) below the cgroup limit, or the kernel will kill them before they get a chance to clean up.', 'warn')}
{talk('When memory really runs out, the kernel first drops cache and swaps. If that is not enough, the out of memory killer picks a victim, usually the process that uses the most memory, and kills it with SIGKILL. The program just dies with status one hundred thirty seven, and the kernel log names it. Oom score adj lets you protect important processes or offer others as victims. The best protection is a memory limit per service, using cgroups. In the demo, a real cgroup with a one hundred megabyte limit kills a Python program that asks for two hundred fifty megabytes, and nothing else on the machine is touched. On Ubuntu you set such limits with MemoryMax in a systemd unit.')}
''', kw=['OOM killer', 'out of memory', 'oom_score', 'oom_score_adj', 'OOMScoreAdjust', 'Killed', 'exit 137', 'cgroup memory limit', 'memory.max', 'memory.events', 'memory.limit_in_bytes', 'MemoryMax', 'MemoryHigh', 'MemorySwapMax', 'systemd-cgtop', 'reclaim', 'Xmx'])

K.lesson('practice', 'Practice: check memory on the practice server', f'''
<p>Find out how the practice server uses its memory and change one memory setting.</p>
{lab('Memory facts', [
    ('Show memory and swap in human units.', 'free -h', [{'out': r'^Mem:\s+\S+Gi'}]),
    ('Show the MemAvailable line of /proc/meminfo.', 'grep MemAvailable /proc/meminfo', [{'out': r'^MemAvailable:\s+\d+ kB'}]),
    ('Show the VmSize and VmRSS lines of your shell (PID in $$).', "grep -E '^(VmSize|VmRSS)' /proc/$$/status", [{'out': r'VmRSS:\s+\d+ kB'}]),
    ('Show pid, vsz, rss and comm of your processes.', 'ps -o pid,vsz,rss,comm', [{'cmd': r'ps\s+-o\s+\S*rss'}]),
    ('Show the current swappiness with sysctl.', 'sysctl vm.swappiness', [{'out': r'^vm\.swappiness = 60$'}]),
    ('Show the overcommit mode.', 'sysctl vm.overcommit_memory', [{'out': r'^vm\.overcommit_memory = 0$'}]),
    ('Try to set swappiness to 10 as yourself.', 'sysctl -w vm.swappiness=10', [{'out': 'permission denied'}]),
    ('Set it to 10 with sudo.', 'sudo sysctl -w vm.swappiness=10', [{'out': r'^vm\.swappiness = 10$'}]),
    ('Read the value straight from /proc/sys.', 'cat /proc/sys/vm/swappiness', [{'out': '^10$'}]),
    ('Show the oom_score_adj of your shell.', 'cat /proc/$$/oom_score_adj', [{'out': '^0$'}]),
    ('Find the OOM kill in the kernel log (reading it needs sudo).', 'sudo journalctl -k | grep -i "out of memory"', [{'out': 'Killed process 2261'}])])}
{talk('Now look at memory on the practice server. Show free in human units, and find MemAvailable in meminfo. Read the virtual size and the resident size of your shell in its status file, and list the V S Z and R S S of your processes with p s. Then look at swappiness and the overcommit mode with sysctl. Try to change swappiness as yourself, which is refused, then with sudo, and read the new value straight from slash proc slash sys. Finally check the O O M score adjustment of your shell and find the out of memory kill in the kernel log.')}
''', kw=['memory lab', 'free practice', 'sysctl practice', 'swappiness practice', 'oom practice'])

K.lesson('levels', 'Memory from school to research', f'''
{ladder(
    '<p>RAM is the computer’s fast working memory. Each program thinks it has its own memory, and the operating system quietly hands out real memory only for the parts it uses. When memory is full, the system can park unused parts on the disk (swap).</p>',
    '<p>Read free (watch available), meminfo, VSZ and RSS, maps and smaps_rollup, understand page faults and copy on write, set swappiness and overcommit with sysctl, recognise OOM kills (status 137, kernel log) and set MemoryMax for services.</p>',
    '<p>Performance engineers use huge pages (2 MiB and 1 GiB, transparent huge pages) for databases and virtual machines, NUMA placement with numactl on servers with several CPU sockets, zram and zswap for compressed swap, systemd-oomd with PSI to act before the kernel OOM killer does, and tools such as perf, bpftrace and valgrind to find leaks and faults.</p>',
    '<p>Research looks at memory tiering with CXL attached memory and persistent memory, multi-generational LRU (MGLRU, in Linux 6.1) for better reclaim decisions, memory safety (Rust, hardware tagging such as ARM MTE), and attacks on memory hardware such as Rowhammer, which flips bits in neighbouring rows of DRAM.</p>')}
{scene('the nightly report that killed the database', '<p>Every night at 02:00 the PostgreSQL server of a shop restarted. The kernel log showed “Out of memory: Killed process (postgres)”. A new reporting job ran on the same machine and loaded a whole table into memory, but the OOM killer chose postgres because it used the most RAM. The team put the job in its own systemd service with MemoryMax=2G, set OOMScoreAdjust=-900 on PostgreSQL, and the next night only the report hit its limit, while the database stayed up.</p>')}
{talk('Here is how understanding memory grows. At school you learn that each program believes it has its own memory, and that the system hands out real memory only for the parts in use. Professionals read free, meminfo and the memory map, know what page faults and copy on write mean, and set limits for services so one program cannot take the whole machine down. Performance engineers use huge pages, place memory close to the right C P U, compress swap with zram, and react to memory pressure before the kernel has to kill. Researchers build new kinds of memory tiers, better reclaim algorithms, and defences against attacks on the memory chips themselves.')}
''', kw=['huge pages', 'transparent huge pages', 'THP', 'NUMA', 'numactl', 'zram', 'zswap', 'systemd-oomd', 'MGLRU', 'CXL', 'memory tiering', 'valgrind', 'memory leak', 'Rowhammer', 'ARM MTE'])

K.quiz('e', 'How big is a normal memory page on x86-64 Linux?', ['512 bytes', '4 KiB', '1 MiB', '64 KiB'], 1, 'Four kilobytes.', 'Huge pages are 2 MiB or 1 GiB.')
K.quiz('e', 'Which column of free shows memory new programs can really get?', ['free', 'available', 'shared', 'total'], 1, 'Available.', 'It counts cache that can be dropped.')
K.quiz('e', 'What is swap?', ['Extra CPU', 'Disk space that holds memory pages the kernel moved out of RAM', 'A backup', 'A file system'], 1, 'Pages on disk.', 'Slow, but better than a crash.')
K.quiz('e', 'Which signal does the OOM killer send?', ['SIGTERM', 'SIGKILL', 'SIGHUP', 'SIGSTOP'], 1, 'No mercy.', 'Status 137.')
K.quiz('m', 'A program maps 1 GiB but uses 10 MiB. What does RSS show?', ['1 GiB', 'About 10 MiB plus its code', '0', '2 GiB'], 1, 'Resident pages only.', 'VSZ shows the 1 GiB.')
K.quiz('m', 'What is a page fault?', ['A bug', 'A trap when a page has no frame yet or is read only, handled by the kernel', 'A disk error', 'A full page table'], 1, 'Normal and frequent.', 'Minor or major.')
K.quiz('m', 'Why is free memory low on a healthy Linux server?', ['A leak', 'Spare RAM is used as page cache and given back when needed', 'Swap is off', 'The kernel reserves it'], 1, 'Cache.', 'Watch available.')
K.quiz('m', 'What does oom_score_adj -1000 do?', ['Kills it first', 'The OOM killer never chooses this process', 'Limits it to 1000 KiB', 'Nothing'], 1, 'Protection.', 'Range -1000 to 1000.')
K.quiz('m', 'Which sysctl sets how eagerly the kernel swaps?', ['vm.dirty_ratio', 'vm.swappiness', 'kernel.pid_max', 'vm.overcommit_memory'], 1, 'Swap.', 'Default 60.')
K.quiz('h', 'After fork, when are pages copied?', ['At once', 'Only when parent or child writes to them (copy on write)', 'Never', 'At exec'], 1, 'On write.', 'Reads share the frame.')
K.quiz('h', 'Why can the RSS of all processes add up to more than the RAM?', ['A kernel bug', 'Shared pages are counted in every process that uses them', 'Swap is included', 'RSS is in bits'], 1, 'Double counting.', 'Use PSS for fair totals.')
K.quiz('h', 'vmstat shows non-zero si and so in every line. What does that mean?', ['The disk is fast', 'The machine swaps in and out all the time and needs more RAM or less load', 'Swap is off', 'CPU is idle'], 1, 'Swap in, swap out.', 'Thrashing.')
K.quiz('h', 'Which systemd setting sets a hard memory limit for a service?', ['LimitNOFILE=', 'MemoryMax=', 'CPUQuota=', 'Nice='], 1, 'Max.', 'Uses the cgroup memory.max.')
K.quiz('x', 'What does vm.overcommit_memory = 2 change?', ['Disables swap', 'The kernel refuses allocations beyond CommitLimit instead of promising more than it has', 'Doubles RAM', 'Turns off the OOM killer for root'], 1, 'Strict accounting.', 'malloc can fail early.')

K.calc('e', 'How many 4 KiB pages are in 1 MiB?', '256', 'Divide.', ['1 MiB = 1024 KiB.', '1024 ÷ 4.', eq('256 pages')], check=256)
K.calc('e', 'A program touches 200 MiB, one page fault per 4 KiB page. How many faults?', '51200', 'Pages in 200 MiB.', ['256 pages per MiB.', '200 × 256.', eq('51200 faults')], check=51200)
K.calc('m', 'MemTotal is 8 GiB and MemAvailable is 0.6 GiB. What percent is available?', '7.5', 'Divide and times 100.', ['0.6 ÷ 8 = 0.075.', '× 100.', eq('7.5 %')], check=7.5)
K.calc('m', 'A page table entry is 8 bytes and maps 4 KiB. How many KiB of entries are needed to map 1 GiB?', '2048', 'Pages times 8 bytes.', ['1 GiB has 262144 pages.', '262144 × 8 = 2097152 bytes.', eq('2048 KiB')], check=2048)
K.calc('h', 'A minor fault takes 0.5 µs and a major fault 5 ms. How many times slower is a major fault?', '10000', 'Same units first.', ['5 ms = 5000 µs.', '5000 ÷ 0.5.', eq('10000 times')], check=10000)
K.calc('h', 'Ten forked workers share 300 MiB of code. RSS counts it in each. How many MiB does the RSS total overstate?', '2700', 'Counted 10 times, exists once.', ['10 × 300 = 3000 MiB counted.', 'Really 300 MiB.', eq('3000 − 300 = 2700 MiB')], check=2700)
K.calc('x', 'With 2 MiB huge pages instead of 4 KiB pages, how many times fewer pages map the same memory?', '512', 'Divide the page sizes.', ['2 MiB = 2048 KiB.', '2048 ÷ 4.', eq('512 times fewer')], check=512)

K.must('Virtual memory', 'Own address space per process, 4 KiB pages, page tables and the MMU. VSZ is mapped, RSS is in RAM. Minor and major page faults. /proc/PID/maps, ASLR.')
K.must('Sharing', 'fork shares pages copy on write, code and libraries are shared, the page cache holds a file once. PSS in smaps_rollup divides shared pages.')
K.must('Reading memory', 'free -h: watch available. /proc/meminfo, vmstat si and so, /proc/pressure/memory, ps aux --sort=-rss.')
K.must('Settings', 'sysctl vm.swappiness (60), vm.overcommit_memory (0), sysctl -w as root, files in /etc/sysctl.d.')
K.must('OOM', 'Reclaim, then the OOM killer sends SIGKILL (status 137, kernel log). oom_score_adj -1000 to 1000. Per service limits with MemoryMax= and MemoryHigh= (cgroup memory.max).')

T = K.topic(
    slug='memory', topic='memory',
    step=(2, 'Files and memory inside', 'lx-adv-2', 'See what files and memory really are to the kernel: inodes, links and open descriptors, the page cache, virtual memory, swapping and the OOM killer.', 'Expert'),
    title='Memory: virtual memory, page faults, swap and the OOM killer', short='Memory', badge='2.2', minutes=55, added='2026-11-24',
    lead='Understand how Linux hands out memory: virtual address spaces and pages, page faults and copy on write, what free and meminfo really say, swap and swappiness, and how the OOM killer and cgroup limits decide who dies when memory runs out.',
    desc='Virtual address spaces, pages and page tables, VSZ and RSS, demand paging with a real 1 GiB mapping, copy on write after fork, /proc/PID/maps and smaps_rollup, free and /proc/meminfo, swappiness and overcommit with sysctl, pressure stall information, the OOM killer, oom_score_adj, and a real OOM kill in a memory cgroup.',
    summary='Pages, page faults, VSZ and RSS, copy on write, free, swap, OOM killer, MemoryMax.',
    keywords=['virtual memory', 'page fault', 'VSZ', 'RSS', 'PSS', 'copy on write', 'free', 'meminfo', 'swap', 'swappiness', 'overcommit', 'OOM killer', 'oom_score_adj', 'cgroup', 'MemoryMax'],
    recap='<p>Each process has its own virtual address space, and pages get real frames only when they are touched, through page faults. fork shares pages until they are written. free’s available column, meminfo and vmstat tell whether memory is short. When reclaim and swap are not enough, the OOM killer sends SIGKILL, so give services their own limits with MemoryMax.</p>')
