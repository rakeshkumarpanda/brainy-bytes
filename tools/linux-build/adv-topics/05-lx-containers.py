# Internals and advanced 3.1: containers under the hood. What a container is (a process with namespaces, cgroups,
# capabilities, seccomp and its own root file system), the eight namespace types, /proc/PID/ns, unshare and nsenter,
# a hand made container from busybox, chroot and pivot_root, overlayfs layers and whiteouts, cgroups v1 and v2 (pids,
# memory, cpu), systemd slices, capabilities (file capabilities, getcap, setcap, capsh), seccomp, rootless
# containers with user namespaces, and how Docker, Podman, containerd and runc fit together.
# Sources: namespaces(7), pid_namespaces(7), network_namespaces(7), user_namespaces(7), unshare(1), nsenter(1),
# lsns(8), chroot(8), pivot_root(2), cgroups(7), the kernel documentation (admin-guide/cgroup-v2.rst,
# filesystems/overlayfs.rst), capabilities(7), getcap(8), setcap(8), capsh(1), seccomp(2), systemd.resource-control(5),
# the OCI runtime specification, docker-run(1) and podman-run(1) for the options named.
# Real boxes run in the build container as root: unshare with a busybox root file system, overlayfs with a whiteout,
# a pids cgroup with a limit of 5, and a file capability that lets the user learner bind port 80. The container uses
# cgroup v1, so that box names the v1 files, and the lesson explains the v2 layout that Ubuntu 24.04 uses.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('what', 'A container is a process with its own view', f'''
{table(['Building block', 'What it gives the container', 'Chapter'], [
    ['namespaces', 'its own view: PIDs, network, host name, mounts, users, IPC', 'this one'],
    ['a root file system', 'the image: its own /bin, /etc and libraries, often as overlayfs layers', 'this one'],
    ['cgroups', 'limits and accounting for CPU, memory, PIDs and I/O', 'this one and 2.2'],
    ['capabilities', 'only some of root’s powers, even for root inside', 'this one'],
    ['seccomp', 'a filter of allowed system calls', '1.1'],
    ['LSM (AppArmor, SELinux)', 'rules for which files and actions are allowed', 'admin 4.3']])}
{table(['Namespace', 'Flag', 'Isolates'], [
    ['mnt', '<code>--mount</code>', 'the list of mounts'],
    ['uts', '<code>--uts</code>', 'host name and domain name'],
    ['ipc', '<code>--ipc</code>', 'System V IPC and POSIX message queues'],
    ['pid', '<code>--pid</code>', 'process ids, the inside starts at 1'],
    ['net', '<code>--net</code>', 'interfaces, addresses, routes, firewall, ports'],
    ['user', '<code>--user</code>', 'user and group ids: root inside can be an unprivileged user outside'],
    ['cgroup', '<code>--cgroup</code>', 'the view of the cgroup tree'],
    ['time', '<code>--time</code>', 'the boot and monotonic clocks (Linux 5.6)']])}
{play('lx-ns')}
{note('Containers share the host’s kernel. A container cannot run a different kernel, a kernel bug can be a way out of every container, and a container built for x86-64 does not run on ARM. Virtual machines each run their own kernel, which is stronger isolation at a higher cost.', 'warn')}
{talk('A container is not a small virtual machine. It is an ordinary Linux process that the kernel shows a different view of the system. Namespaces give it its own process ids, its own network, its own host name and its own list of mounts. A root file system from an image gives it its own programs and libraries. Cgroups limit how much C P U and memory it may use, capabilities take away most of root’s powers, and seccomp blocks dangerous system calls. Choose namespaces in the animation and see what the process inside sees. Remember that all containers on a machine share one kernel.')}
''', kw=['container', 'namespace', 'mount namespace', 'UTS namespace', 'IPC namespace', 'PID namespace', 'network namespace', 'user namespace', 'cgroup namespace', 'time namespace', 'container vs virtual machine', 'shared kernel', 'isolation'])

K.lesson('handmade', 'A container by hand: unshare, chroot and /proc/PID/ns', f'''
{cmdtable([
    ('ls -l /proc/PID/ns', 'The namespaces of a process, as links with an inode number', 'ls -l /proc/$$/ns'),
    ('lsns', 'All namespaces on the system and their first process', 'sudo lsns -t net'),
    ('unshare FLAGS CMD', 'Run a command in new namespaces', 'sudo unshare --uts --pid --fork --mount-proc bash'),
    ('nsenter -t PID FLAGS CMD', 'Run a command inside the namespaces of a running process', 'sudo nsenter -t 4242 --net ip addr'),
    ('chroot DIR CMD', 'Run a command with DIR as its root folder', 'sudo chroot rootfs /bin/sh'),
    ('docker inspect -f "{{.State.Pid}}" NAME', 'The host PID of a container, to use with nsenter', 'sudo nsenter -t $(docker inspect -f "{{.State.Pid}}" web) --net ss -tln')])}
{run('Build a tiny container from busybox', """cd "$(mktemp -d)"
mkdir -p rootfs/bin rootfs/proc
cp /bin/busybox rootfs/bin/
chroot rootfs /bin/busybox --install -s /bin
ls rootfs/bin | wc -l
readlink /proc/self/ns/uts
readlink /proc/self/ns/pid
printf '%s\\n' 'mount -t proc proc /proc' 'hostname box' 'echo "hostname: $(hostname)"' 'readlink /proc/self/ns/uts' 'readlink /proc/self/ns/pid' 'ps' 'ip link' 'ls /' > rootfs/init.sh
cat rootfs/init.sh
unshare --mount --uts --ipc --net --pid --fork chroot rootfs /bin/sh /init.sh
hostname | grep -c box""", note='busybox is one static program that acts as sh, ps, ls, ip and hundreds more, so one file makes a working root file system. Inside, the namespace links show different inode numbers than outside, which proves they are new namespaces. The shell is PID 1, ps lists only the two processes of the container, ip link shows only lo, switched off, and ls / shows only bin, proc and the script. The host name box exists only inside: the last line counts 0 matches outside. Real runtimes do the same steps, use pivot_root instead of chroot so the old root cannot be reached, and add cgroups, capabilities and seccomp.', root=True)}
{talk('You can build a container with two commands. Unshare starts a program in new namespaces, and chroot gives it a new root folder. In the demo, busybox, a single program that acts as hundreds of commands, fills a tiny root file system. Inside the container the shell is process one, ps sees only two processes, the network has only an unused loopback, and the root folder has only bin and proc. The host name box exists only inside. The links in slash proc slash P I D slash n s identify each namespace by an inode number, so you can compare them inside and outside. Nsenter does the opposite of unshare: it joins the namespaces of a running process, which is how you debug a container with the host’s tools.')}
''', kw=['unshare', 'nsenter', 'lsns', '/proc/PID/ns', 'chroot', 'pivot_root', 'busybox', 'root file system', 'rootfs', 'mount-proc', 'container by hand', 'docker inspect State.Pid'])

K.lesson('layers', 'Images and overlayfs', f'''
<p>A container image is a stack of read-only <b>layers</b>, each a set of file changes, for example the base system, then the installed packages, then your app. When a container starts, <b>overlayfs</b> joins the layers into one tree and puts a thin writable layer on top.</p>
{run('Join two folders with overlayfs, change, delete and add files', """cd "$(mktemp -d)"
mkdir lower upper work merged
echo base > lower/a.txt
echo keep > lower/b.txt
mount -t overlay overlay -o lowerdir=lower,upperdir=upper,workdir=work merged
echo changed > merged/a.txt
rm merged/b.txt
echo new > merged/c.txt
ls merged
cat lower/a.txt
ls -l upper
umount merged""", note='merged shows the joined view. Changing a.txt copies it up into upper first (copy up), so the lower layer still says base. Deleting b.txt cannot touch the read-only lower layer, so overlayfs puts a <b>whiteout</b> in upper: a character device with the numbers 0, 0, which hides the lower file. The new c.txt exists only in upper. Docker’s overlay2 driver keeps image layers as lower folders and each container’s changes as its upper folder, which is why docker diff can list them.', root=True)}
{table(['Image practice', 'Why'], [
    ['put rarely changing steps first in the Dockerfile', 'layers are cached and shared, so a change rebuilds only the layers after it'],
    ['delete temporary files in the same RUN step', 'a file deleted in a later layer still takes space in the earlier one, hidden by a whiteout'],
    ['use small base images (alpine, distroless, ubuntu minimal)', 'fewer files to download and fewer packages with security holes'],
    ['keep data in volumes, not in the writable layer', 'the writable layer disappears with the container']])}
{talk('A container image is a stack of read only layers, each holding the files that one build step added or changed. Overlay f s joins them into one tree and adds a writable layer on top for the running container. In the demo, changing a file copies it up into the upper layer first, so the lower layer stays untouched. Deleting a file that lives in a lower layer leaves a whiteout, a special device file that hides it. That is why a file deleted in a later build step still makes the image bigger. Put steps that rarely change first, and clean up in the same step that made the mess.')}
''', kw=['container image', 'image layers', 'overlayfs', 'overlay2', 'lowerdir', 'upperdir', 'workdir', 'copy up', 'whiteout', 'writable layer', 'Dockerfile layers', 'layer cache', 'docker diff', 'volume'])

K.lesson('cgroups', 'cgroups: limits for CPU, memory and processes', f'''
{shape('cgroup v2 on Ubuntu 24.04', """/sys/fs/cgroup/                    one tree, all controllers
├── system.slice/                  services
│   ├── ssh.service/
│   └── docker-4f2c….scope/        a container
│       ├── cgroup.procs           PIDs in this group
│       ├── memory.max             hard memory limit
│       ├── memory.current         memory in use now
│       ├── cpu.max                "50000 100000" = half a CPU
│       ├── pids.max               the most processes
│       └── memory.events          oom_kill counter
└── user.slice/                    login sessions""", note='Every process belongs to exactly one cgroup, shown in /proc/PID/cgroup as 0::/path. systemd makes a cgroup per service, per login session and per container scope. cgroup v1, still found on older systems and in some containers, has one tree per controller (/sys/fs/cgroup/memory, /sys/fs/cgroup/pids) with other file names.')}
{run('Stop a runaway with a pids limit of 5', """mkdir /sys/fs/cgroup/pids/demo
echo 5 > /sys/fs/cgroup/pids/demo/pids.max
bash -c 'echo $$ > /sys/fs/cgroup/pids/demo/cgroup.procs
for i in 1 2 3 4 5 6; do sleep 2 & done
wait' 2>&1 | sort | uniq -c
cat /sys/fs/cgroup/pids/demo/pids.max
sleep 2
rmdir /sys/fs/cgroup/pids/demo""", note='The bash and its first four sleeps fill the limit of 5. Every further fork fails with “Resource temporarily unavailable” (EAGAIN), bash retries, and the last sleeps start only when earlier ones end. A fork bomb inside such a group cannot take the machine down. This build container has the older v1 layout, so the folder is /sys/fs/cgroup/pids. On Ubuntu 24.04 the same file pids.max sits in the group’s folder in the one v2 tree.', root=True)}
{cmdtable([
    ('systemd-cgls', 'The cgroup tree with the processes in it', 'systemd-cgls -u ssh.service'),
    ('systemd-cgtop', 'CPU, memory and I/O per cgroup, like top', 'systemd-cgtop -m'),
    ('systemd-run --scope -p MemoryMax=500M -p CPUQuota=50% CMD', 'Run one command in its own limited cgroup', 'sudo systemd-run --scope -p MemoryMax=500M ./import.sh'),
    ('systemctl set-property UNIT KEY=VAL', 'Change limits of a running service (and keep them)', 'sudo systemctl set-property nginx.service CPUQuota=200%'),
    ('docker run --memory 512m --cpus 1.5 --pids-limit 100', 'The same limits for one container', 'docker run --memory 512m --cpus 1.5 nginx')])}
{talk('Cgroups, short for control groups, put processes into groups and limit what each group may use: C P U time, memory, the number of processes and disk I O. On Ubuntu twenty four point zero four there is one tree under slash sys slash f s slash cgroup, and systemd makes a group for every service, every login and every container. Files such as memory dot max, c p u dot max and p i d s dot max hold the limits. In the demo, a group with a limit of five processes stops a burst of forks with resource temporarily unavailable. That is how one container cannot eat all the memory or start a fork bomb that freezes the host.')}
''', kw=['cgroups', 'cgroup v2', 'cgroup v1', 'control groups', '/sys/fs/cgroup', 'cgroup.procs', 'memory.max', 'memory.current', 'cpu.max', 'pids.max', 'memory.events', '/proc/PID/cgroup', 'systemd slice', 'systemd-cgls', 'systemd-cgtop', 'systemd-run --scope', 'CPUQuota', 'set-property', 'fork bomb', 'Resource temporarily unavailable', 'docker --memory', 'docker --cpus', '--pids-limit'])

K.lesson('caps', 'Capabilities, seccomp and rootless containers', f'''
<p>Linux splits root’s power into about 40 <b>capabilities</b>, such as CAP_NET_BIND_SERVICE (use ports below 1024), CAP_NET_RAW (raw sockets, ping), CAP_CHOWN or CAP_SYS_ADMIN (mounts and many other things). A process has sets of them, shown in /proc/PID/status as hex masks, and a program file can carry some (file capabilities).</p>
{run('Give one program one capability instead of root', """getcap /usr/bin/ping
capsh --decode=0000000000000400
ip netns add lab
ip -n lab link set lo up
cp /usr/bin/python3.12 /usr/local/bin/pyweb
ip netns exec lab sudo -u learner python3 -c 'import socket; socket.socket().bind(("127.0.0.1", 80))' 2>&1 | tail -n 1
setcap cap_net_bind_service=+ep /usr/local/bin/pyweb
getcap /usr/local/bin/pyweb
ip netns exec lab sudo -u learner /usr/local/bin/pyweb -c 'import socket; socket.socket().bind(("127.0.0.1", 80)); print("bound to port 80")'
sudo -u learner grep CapEff /proc/self/status
rm /usr/local/bin/pyweb
ip netns delete lab""", note='ping on Ubuntu 24.04 carries cap_net_raw instead of being SUID root. capsh --decode turns a hex mask into names. As learner, Python may not bind port 80 (PermissionError), but a copy of the Python program with the file capability cap_net_bind_service may, with no other root power. (The test runs in a network namespace so it touches no real port 80.) A normal user’s effective set is all zeros. A root shell on a normal host shows 000001ffffffffff, all 41 bits set, while a container usually gets a much smaller set because the runtime drops the dangerous ones.', root=True)}
{table(['Option', 'Effect'], [
    ['<code>--cap-drop ALL --cap-add NET_BIND_SERVICE</code>', 'start from no capabilities and add only what is needed'],
    ['<code>--security-opt no-new-privileges</code>', 'SUID programs and file capabilities cannot raise privileges inside'],
    ['<code>--read-only</code>', 'the container’s root file system cannot be changed'],
    ['<code>--user 1000:1000</code>', 'run the process as a normal user, not root'],
    ['the default seccomp profile', 'Docker and Podman block about 40 to 50 risky system calls, such as kexec_load and add_key'],
    ['<code>--privileged</code>', 'turns all of this off: avoid it'],
    ['rootless Podman or Docker', 'a user namespace maps root inside to your own user outside, using /etc/subuid and /etc/subgid']])}
{steps('Who does what when you type docker run nginx', [
    'The <b>docker</b> client sends the request to the <b>dockerd</b> daemon over /run/docker.sock (anyone who can write that socket is effectively root).',
    'dockerd asks <b>containerd</b> to pull the image layers and prepare an overlayfs snapshot.',
    'containerd starts a shim, which calls <b>runc</b> with an OCI bundle: a config.json with namespaces, cgroups, capabilities, seccomp, mounts, plus the root file system.',
    'runc makes the namespaces and cgroup, switches root with pivot_root, drops capabilities, loads seccomp and finally runs execve on nginx, which becomes PID 1 of the container. runc then exits.',
    'Podman does the same without a daemon, and Kubernetes talks to containerd or CRI-O through the CRI interface.'])}
{talk('Root on Linux is really a bundle of about forty capabilities, such as binding to ports below one thousand twenty four, or using raw sockets. A program can get just one of them instead of full root. On Ubuntu, ping carries the raw socket capability instead of running as root. In the demo, a copy of Python gets the capability to bind low ports, and then the normal user learner can listen on port eighty, with no other powers. Containers use this to drop most of root’s powers even for root inside, add a seccomp filter on system calls, and with user namespaces, root inside a rootless container is just your own user outside. Avoid the privileged flag, which switches all of this off.')}
''', kw=['capabilities', 'CAP_NET_BIND_SERVICE', 'CAP_NET_RAW', 'CAP_SYS_ADMIN', 'file capabilities', 'getcap', 'setcap', 'capsh', 'CapEff', 'cap-drop', 'cap-add', 'no-new-privileges', 'read-only container', 'seccomp profile', 'privileged container', 'rootless', 'Podman', 'subuid', 'subgid', 'dockerd', 'containerd', 'runc', 'OCI', 'CRI-O', 'docker.sock'])

K.lesson('practice', 'Practice: namespaces, cgroups and capabilities', f'''
<p>Read the namespaces, cgroups and capabilities of processes on the practice server.</p>
{lab('Container building blocks', [
    ('List the namespace links of your shell.', 'ls -l /proc/$$/ns', [{'out': r'uts -> uts:\['}]),
    ('Show the network namespace of your shell with readlink.', 'readlink /proc/$$/ns/net', [{'out': r'^net:\[\d+\]$'}]),
    ('Show which cgroup your shell is in.', 'cat /proc/$$/cgroup', [{'out': r'^0::/user\.slice/'}]),
    ('Show the cgroup of sshd, PID 412.', 'cat /proc/412/cgroup', [{'out': 'system.slice/ssh.service'}]),
    ('Show the effective capabilities of a normal process.', 'grep CapEff /proc/self/status', [{'out': r'CapEff:\s+0000000000000000'}]),
    ('Show them for a root process.', 'sudo grep CapEff /proc/self/status', [{'out': r'CapEff:\s+000001ffffffffff'}]),
    ('Decode the mask 0000000000000400.', 'capsh --decode=0000000000000400', [{'out': 'cap_net_bind_service'}]),
    ('Show the file capabilities of ping.', 'getcap /usr/bin/ping', [{'out': 'cap_net_raw=ep'}]),
    ('Copy cat to /usr/local/bin/webcat with sudo.', 'sudo cp /usr/bin/cat /usr/local/bin/webcat', [{'exists': '/usr/local/bin/webcat'}]),
    ('Give webcat the capability cap_net_bind_service=+ep.', 'sudo setcap cap_net_bind_service=+ep /usr/local/bin/webcat', [{'cmd': r'setcap\s+cap_net_bind_service'}]),
    ('Check it with getcap.', 'getcap /usr/local/bin/webcat', [{'out': 'cap_net_bind_service=ep'}])])}
{talk('Now read the building blocks of containers on the practice server. List the namespace links of your shell and read one with readlink. Show the cgroup of your shell, which sits in the user slice, and of the s s h daemon, which has its own service group. Compare the effective capabilities of a normal process and a root process, and decode one mask with capsh. Look at the capability of ping, then give a copy of cat the capability to bind low ports, and check it with getcap.')}
''', kw=['namespace lab', 'cgroup lab', 'capability lab', 'getcap practice', 'setcap practice'])

K.lesson('levels', 'Containers from school to research', f'''
{ladder(
    '<p>A container is a program packed with everything it needs, which runs in its own little room on the computer: it sees only its own files, its own network and its own processes, while sharing the computer’s kernel.</p>',
    '<p>Explain namespaces, cgroups, capabilities, seccomp and overlayfs, read /proc/PID/ns and cgroup, use unshare and nsenter to debug, set limits for containers and services, drop capabilities, run as a normal user, and avoid --privileged and a writable docker.sock.</p>',
    '<p>Platform teams run Kubernetes with resource requests and limits, Pod Security Standards, network policies, rootless and read-only containers, image scanning and signing (Trivy, cosign, SBOMs), and stronger isolation where needed with gVisor (a user space kernel), Kata Containers or Firecracker micro VMs.</p>',
    '<p>Research studies container escapes and kernel attack surface, eBPF based security and observability (Cilium, Falco, Tetragon), WebAssembly as a lighter sandbox, confidential containers in encrypted VMs (AMD SEV, Intel TDX), and the cost of isolation for serverless platforms that start thousands of sandboxes per second.</p>')}
{scene('the container that could read the host', '<p>A team ran a monitoring container with --privileged and the host’s / mounted inside, because “it needed access”. A bug in the tool let an attacker run commands, and with all capabilities and the host files they read SSH keys from the host. In the clean-up, the team listed what the tool really needed: read access to /proc and one capability (CAP_SYS_PTRACE). They ran it with --cap-drop ALL --cap-add SYS_PTRACE, a read-only root file system and no host mounts, and added a policy that rejects privileged containers.</p>')}
{talk('Here is how understanding containers grows. At school you learn that a container is a packed program in its own little room, sharing the computer’s kernel. Professionals know the building blocks, namespaces, cgroups, capabilities, seccomp and overlay layers, and use them to debug and to lock containers down. Platform teams run Kubernetes with limits, security policies, signed images and, where needed, stronger sandboxes such as g Visor or micro virtual machines. Researchers look for container escapes, build security tools with e B P F, and explore WebAssembly and confidential computing as new kinds of sandboxes.')}
''', kw=['Kubernetes', 'resource limits', 'Pod Security Standards', 'NetworkPolicy', 'image scanning', 'Trivy', 'cosign', 'SBOM', 'gVisor', 'Kata Containers', 'Firecracker', 'container escape', 'Falco', 'Tetragon', 'WebAssembly sandbox', 'confidential containers'])

K.quiz('e', 'What does a container share with its host?', ['Nothing', 'The kernel', 'Its root file system', 'Its process ids'], 1, 'One kernel.', 'Virtual machines have their own.')
K.quiz('e', 'Which kernel feature gives a container its own process ids?', ['cgroups', 'the PID namespace', 'seccomp', 'overlayfs'], 1, 'Namespaces isolate views.', 'The first process inside is PID 1.')
K.quiz('e', 'Which feature limits how much memory a container may use?', ['namespaces', 'cgroups', 'chroot', 'capabilities'], 1, 'Control groups.', 'memory.max.')
K.quiz('e', 'Which command runs a program in new namespaces?', ['nsenter', 'unshare', 'chroot', 'lsns'], 1, 'Un-share.', 'nsenter joins existing ones.')
K.quiz('m', 'Where can you see the namespaces of a process?', ['/etc/namespaces', '/proc/PID/ns', '/sys/ns', 'lsblk'], 1, 'Links in /proc.', 'Equal inode numbers mean the same namespace.')
K.quiz('m', 'What does overlayfs put in the upper layer when you delete a file of a lower layer?', ['Nothing', 'A whiteout (a 0, 0 character device)', 'A copy of the file', 'A symbolic link'], 1, 'Hide, not delete.', 'The lower layer is read only.')
K.quiz('m', 'Why does a file deleted in a later Dockerfile step still make the image bigger?', ['A Docker bug', 'The earlier layer still contains it, the later one only hides it', 'Compression', 'The cache'], 1, 'Layers.', 'Clean up in the same RUN step.')
K.quiz('m', 'What does CAP_NET_BIND_SERVICE allow?', ['Raw sockets', 'Binding to ports below 1024', 'Changing the firewall', 'Mounting'], 1, 'Low ports.', 'Without full root.')
K.quiz('m', 'A container with pids.max 100 tries to start process 101. What happens?', ['The host crashes', 'fork fails with Resource temporarily unavailable', 'The oldest process is killed', 'Nothing'], 1, 'EAGAIN.', 'Fork bombs stay contained.')
K.quiz('h', 'Which program finally creates the namespaces and starts the container process for Docker?', ['dockerd', 'runc', 'the docker client', 'systemd'], 1, 'The OCI runtime.', 'Called through containerd and a shim.')
K.quiz('h', 'Why is write access to /run/docker.sock as good as root?', ['It is not', 'You can start a privileged container with the host’s / mounted', 'It holds passwords', 'It runs as root by itself'], 1, 'The daemon obeys.', 'Treat the docker group like sudo.')
K.quiz('h', 'What does a user namespace give rootless containers?', ['More speed', 'Root inside maps to an unprivileged user outside', 'A new kernel', 'No network'], 1, 'Mapped ids.', '/etc/subuid and subgid.')
K.quiz('h', 'How do you run the host’s ss inside a container’s network namespace?', ['docker exec ss', 'nsenter -t PID --net ss -tln', 'chroot', 'unshare --net'], 1, 'Join, do not create.', 'PID from docker inspect.')
K.quiz('x', 'Why do some platforms use gVisor or Firecracker instead of plain containers?', ['Speed only', 'They do not share the host kernel directly, which reduces the kernel attack surface', 'They need no images', 'They are older'], 1, 'Stronger isolation.', 'For untrusted code.')

K.calc('e', 'cpu.max is "50000 100000". What share of one CPU may the group use, in percent?', '50', 'Quota over period.', ['50000 ÷ 100000 = 0.5.', '× 100.', eq('50 %')], check=50)
K.calc('e', 'A host runs 12 containers with a 512 MiB memory limit each. How many MiB could they use together at most?', '6144', 'Multiply.', ['12 × 512.', 'Limits, not current use.', eq('6144 MiB')], check=6144)
K.calc('m', 'cpu.max "150000 100000" allows how many CPUs worth of time?', '1.5', 'Quota over period.', ['150000 ÷ 100000.', 'More than 1 means several CPUs.', eq('1.5 CPUs')], check=1.5)
K.calc('m', 'The capability mask 0x400 has which bit set? (count from 0)', '10', 'Powers of 2.', ['0x400 = 1024.', '1024 = 2 to the power 10.', eq('bit 10, CAP_NET_BIND_SERVICE')], check=10)
K.calc('h', 'An image has layers of 80, 120 and 15 MB. Five containers run from it and each writes 4 MB. How many MB of disk do they use together?', '235', 'Layers are shared.', ['Image layers once: 80 + 120 + 15 = 215.', 'Writable layers: 5 × 4 = 20.', eq('215 + 20 = 235 MB')], check=235)
K.calc('h', 'A fork bomb doubles its processes every second, starting at 1. pids.max is 512. After how many seconds does it hit the limit?', '9', 'Powers of 2.', ['2 to the power 9 = 512.', 'After 9 doublings.', eq('9 s')], check=9)
K.calc('x', 'A full capability mask covers capabilities 0 to 40. How many capabilities is that?', '41', 'Count both ends.', ['0 to 40 inclusive.', '40 − 0 + 1.', eq('41 capabilities')], check=41)

K.must('What a container is', 'A process with namespaces, a root file system, cgroup limits, fewer capabilities and a seccomp filter, sharing the host kernel.')
K.must('Namespaces', 'mnt, uts, ipc, pid, net, user, cgroup, time. /proc/PID/ns links, unshare to create, nsenter to join, lsns to list.')
K.must('Images', 'Read-only layers joined by overlayfs with a writable upper layer. Copy up on change, whiteouts for deletes.')
K.must('cgroups', 'One v2 tree in /sys/fs/cgroup on Ubuntu 24.04, memory.max, cpu.max, pids.max, /proc/PID/cgroup, systemd-cgls, systemd-cgtop, systemd-run -p.')
K.must('Least privilege', 'Capabilities (getcap, setcap, capsh --decode), --cap-drop ALL, no-new-privileges, non-root user, rootless with user namespaces, never --privileged. Docker: dockerd, containerd, runc.')

T = K.topic(
    slug='containers-inside', topic='containers-inside',
    step=(3, 'Containers and performance', 'lx-adv-3', 'Build a container from kernel features by hand, then find out why a system is slow with the right tools and method, and finish with a full revision of the course.', 'Expert'),
    title='Containers under the hood: namespaces, cgroups, layers and capabilities', short='Containers inside', badge='3.1', minutes=60, added='2026-11-24',
    lead='See that a container is just a process: build one by hand with unshare and chroot, join image layers with overlayfs, limit it with cgroups, and take away root’s powers with capabilities, seccomp and user namespaces.',
    desc='Containers as processes, the eight namespaces, /proc/PID/ns, unshare and nsenter, a busybox container by hand, overlayfs layers and whiteouts, cgroups v2 and a real pids limit, systemd slices and limits, capabilities with getcap, setcap and capsh, seccomp, rootless containers, and how docker, containerd and runc work together.',
    summary='Namespaces, a container by hand, overlayfs, cgroups, capabilities, seccomp, runc.',
    keywords=['container', 'namespaces', 'unshare', 'nsenter', 'chroot', 'overlayfs', 'cgroups', 'cgroup v2', 'capabilities', 'setcap', 'seccomp', 'rootless', 'Docker', 'Podman', 'runc', 'containerd'],
    recap='<p>A container is a normal process that namespaces give its own view, an image gives its own files through overlayfs layers, cgroups limit, and dropped capabilities and seccomp restrict. unshare and chroot build one by hand, nsenter joins one, and runc does the same steps for Docker, Podman and Kubernetes. All containers share the host kernel.</p>')
