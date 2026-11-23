# System administration 2.1: boot and systemd. Firmware (UEFI, BIOS), GRUB and /etc/default/grub, the kernel and its
# command line, the initramfs, systemd as PID 1, targets and the old runlevels, unit types and unit files, unit file
# locations and drop-ins, systemd-analyze verify, systemctl start, stop, restart, reload, enable, disable, mask,
# status, is-active, --failed, daemon-reload, writing a service with Restart= and User=, sandboxing options, rescue
# and emergency targets. Sources: bootup(7), systemd(1), systemd.unit(5), systemd.service(5), systemd.special(7),
# systemd.exec(5), systemctl(1), systemd-analyze(1), the GRUB manual, initramfs-tools(7), dracut(8).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('boot', 'How Linux starts: firmware to login', f'''
<p>Starting a computer is a relay race. Each stage loads the next one and hands over control, and knowing the order tells you where to look when a machine does not come up.</p>
{table(['Stage', 'What it does', 'Where it is configured'], [
    ['Firmware (UEFI or BIOS)', 'tests the hardware and starts a boot loader from the disk', 'firmware setup screen, the EFI System Partition at /boot/efi'],
    ['Boot loader (GRUB)', 'shows the menu, loads the kernel and initramfs, passes the kernel command line', '<code>/etc/default/grub</code>, then <code>sudo update-grub</code> writes /boot/grub/grub.cfg'],
    ['Kernel', 'detects the hardware, starts memory management and drivers', '/boot/vmlinuz-VERSION, the command line in /proc/cmdline'],
    ['initramfs', 'a small file system in memory that loads the drivers for the real root disk and mounts it', 'built by update-initramfs (Debian) or dracut (Fedora, RHEL)'],
    ['systemd (PID 1)', 'mounts file systems from /etc/fstab and starts services until the default target is reached', 'unit files in /usr/lib/systemd/system and /etc/systemd/system'],
    ['Login', 'getty on text consoles, a display manager on desktops, sshd for remote logins', 'the units getty@.service, gdm.service, ssh.service']])}
{play('lx-boot')}
{table(['Target', 'Old runlevel', 'Meaning'], [
    ['<code>poweroff.target</code>', '0', 'switch off'],
    ['<code>rescue.target</code>', '1', 'single user, basic system, for repairs'],
    ['<code>multi-user.target</code>', '2, 3, 4', 'full system with networking, text logins, the usual target of servers'],
    ['<code>graphical.target</code>', '5', 'multi-user plus a graphical login'],
    ['<code>reboot.target</code>', '6', 'restart'],
    ['<code>emergency.target</code>', 'none', 'only a root shell, root file system read-only, used when even rescue fails']])}
{run('Targets and the old runlevel names on a real system', """ls -l /lib/systemd/system/runlevel*.target | awk '{print $9, $10, $11}'
systemctl --root=/ get-default""", note='The runlevel names still exist as links to targets, so old scripts keep working. This system boots into graphical.target by default. A server would usually use multi-user.target, set with sudo systemctl set-default multi-user.target.')}
{note('To reach a rescue shell on a machine that does not boot, press e in the GRUB menu, add <code>systemd.unit=rescue.target</code> (or emergency.target) to the line that starts with linux, and boot with Ctrl+X. The change lasts for one boot only.')}
{talk('When you press the power button, several programs take turns. First the firmware, called U E F I on modern computers or BIOS on old ones, checks the hardware and starts a boot loader from the disk. On Linux the boot loader is usually GRUB, which shows a menu and loads two files into memory: the kernel and the initramfs. The kernel detects the hardware, and the initramfs, a tiny temporary file system, loads the drivers needed to reach the real root disk, for example for encryption, where it asks for your passphrase. Then the kernel starts systemd as process number one. Systemd mounts the file systems listed in slash etc slash fstab and starts all services, many of them in parallel, until it reaches the default target, such as multi user for servers or graphical for desktops. Targets replaced the old numbered runlevels. In the animation, choose a fault to see exactly where a broken boot stops and how to fix it.')}
''', kw=['boot process', 'UEFI', 'BIOS', 'GRUB', 'update-grub', 'kernel command line', 'initramfs', 'dracut', 'systemd PID 1', 'targets', 'runlevels', 'multi-user.target', 'rescue mode', 'emergency mode'])

K.lesson('units', 'Units and unit files', f'''
<p>Everything systemd manages is a <b>unit</b>, described by a small text file in INI style. The file name ends with the unit type.</p>
{table(['Type', 'Manages', 'Example'], [
    ['<code>.service</code>', 'a program, often a background daemon', 'ssh.service, nginx.service'],
    ['<code>.timer</code>', 'starts a service on a schedule', 'apt-daily.timer'],
    ['<code>.socket</code>', 'a network or local socket, which starts its service on the first connection', 'ssh.socket'],
    ['<code>.target</code>', 'a group of units, a synchronisation point', 'multi-user.target'],
    ['<code>.mount</code>, <code>.automount</code>', 'a mounted file system (made from /etc/fstab lines too)', 'home.mount'],
    ['<code>.path</code>', 'starts a service when a file or folder changes', 'cups.path']])}
{table(['Folder', 'Holds', 'Priority'], [
    ['<code>/etc/systemd/system</code>', 'your own units and overrides', 'highest'],
    ['<code>/run/systemd/system</code>', 'units created at run time', 'middle'],
    ['<code>/usr/lib/systemd/system</code>', 'units installed by packages. Never edit these, upgrades overwrite them', 'lowest']])}
{run('Real unit files: a service and the timer that starts it', """cat /lib/systemd/system/apt-daily.service
cat /lib/systemd/system/apt-daily.timer
systemctl --root=/ list-unit-files --type=timer --no-pager | head -5""", note='The service is Type=oneshot, a job that runs and ends. Its timer fires at 06:00 and 18:00 with a random delay of up to 12 hours, and Persistent=true catches up after downtime. The [Install] section says which target pulls the unit in when it is enabled.')}
{run('Check a unit file before you use it', """printf '[Unit]\\nDescription=Hello web demo\\nAfter=network.target\\n\\n[Service]\\nExecStart=/usr/bin/python3 -m http.server 8080\\nRestart=on-failure\\n\\n[Install]\\nWantedBy=multi-user.target\\n' > hello.service
systemd-analyze verify ./hello.service && echo "hello.service looks fine"
printf '[Service]\\nExecStart=/usr/bin/python3 -m http.server 8080\\nRestrat=always\\n' > typo.service
systemd-analyze verify ./typo.service""", note='systemd-analyze verify found the misspelled key Restrat. systemd itself only logs such a line and ignores it, so the service would quietly run without the restart rule.')}
{cmdtable([
    ('sudo systemctl edit NAME', 'Create a drop-in override in /etc/systemd/system/NAME.service.d/override.conf, without touching the package file', 'sudo systemctl edit nginx'),
    ('systemctl cat NAME', 'Show the unit file and all its drop-ins', 'systemctl cat nginx'),
    ('sudo systemctl daemon-reload', 'Make systemd read changed unit files', 'sudo systemctl daemon-reload'),
    ('systemctl list-dependencies TARGET', 'Show what a target pulls in', 'systemctl list-dependencies multi-user.target')])}
{talk('Systemd manages things called units, and each unit is a short text file. The ending of the file name tells the type. A dot service unit runs a program, a dot timer starts a service on a schedule, a dot socket waits for connections, and a dot target groups other units, like a milestone during boot. Package units live in slash usr slash lib slash systemd slash system, and you should never edit them, because an upgrade overwrites them. Your own units and changes go in slash etc slash systemd slash system, which wins over the package folder. The safest way to change a package’s unit is systemctl edit, which writes a small override file. Every unit file has sections in square brackets. Unit holds the description and the order, Service says what to run, and Install says which target pulls it in when it is enabled. Before you trust a new file, run systemd analyze verify, which catches typos that systemd would otherwise silently ignore.')}
''', kw=['systemd unit', 'unit file', '.service', '.timer', '.socket', '.target', '/etc/systemd/system', '/usr/lib/systemd/system', 'drop-in', 'systemctl edit', 'systemd-analyze verify', 'daemon-reload', 'WantedBy'])

K.lesson('systemctl', 'Managing services with systemctl', f'''
{cmdtable([
    ('systemctl status NAME', 'State, main process, memory, and the last log lines', 'systemctl status ssh'),
    ('sudo systemctl start, stop, restart NAME', 'Start or stop now', 'sudo systemctl restart nginx'),
    ('sudo systemctl reload NAME', 'Re-read the configuration without stopping, if the service supports it', 'sudo systemctl reload nginx'),
    ('sudo systemctl enable, disable NAME', 'Start at boot, or not. Add --now to also start or stop it now', 'sudo systemctl enable --now nginx'),
    ('sudo systemctl mask, unmask NAME', 'Forbid any start, even by other units', 'sudo systemctl mask apache2'),
    ('systemctl is-active, is-enabled NAME', 'One word, for scripts', 'systemctl is-active --quiet nginx || echo down'),
    ('systemctl --failed', 'Units that failed', 'systemctl --failed'),
    ('systemctl list-units --type=service', 'Loaded services and their state', 'systemctl list-units --type=service --all')])}
{sample('Checking and controlling a service (the build container has no running systemd, so this output comes from the practice shell, which follows systemd 255)', """systemctl status nginx
systemctl stop nginx
sudo systemctl stop nginx
systemctl is-active nginx
sudo systemctl start nginx
systemctl is-active nginx
systemctl --failed""", out=["""● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-11-23 08:30:00 UTC; 1h 1min ago
       Docs: man:nginx(8)
   Main PID: 905 (nginx)
      Tasks: 2 (limit: 4558)
     Memory: 2.8M
        CPU: 21ms
     CGroup: /system.slice/nginx.service
             ├─905 "nginx: master process /usr/sbin/nginx"
             └─1200 "nginx: worker process"

Nov 23 08:30:00 brainy systemd[1]: Starting nginx.service - A high performance web server and a reverse proxy server...
Nov 23 08:30:00 brainy systemd[1]: Started nginx.service - A high performance web server and a reverse proxy server.""",
    "Failed to stop nginx.service: Interactive authentication required.", "", "inactive", "", "active",
    """  UNIT           LOAD   ACTIVE SUB     DESCRIPTION
● backup.service loaded failed failed  Nightly backup

Legend: LOAD   → Reflects whether the unit definition was properly loaded.
        ACTIVE → The high-level unit activation state, i.e. generalization of SUB.
        SUB    → The low-level unit activation state, values depend on unit type.

1 loaded units listed."""], note='The Loaded line says where the unit file is, whether it starts at boot (enabled) and what the vendor preset is. Active says the state and since when. Changing a service needs root, so the first stop was refused. systemctl --failed found a backup job that failed during the night.')}
{note('enable and start are different. enable only creates a link so the unit starts at the next boot. start runs it now. A new service usually needs both, which is what enable --now does.', 'warn')}
{talk('Systemctl is the remote control for services. Systemctl status shows whether a service runs, its main process, how much memory it uses, and its last log lines, which is often enough to see what went wrong. Start, stop and restart act right now, and reload asks the service to read its configuration again without dropping connections, if it supports that. Enable and disable are about the next boot: enable creates a link so the service starts automatically, and dash dash now also starts it at once. Mask is stronger than disable, because it forbids any start at all. For scripts, is active and is enabled print one word and set the exit status. And after every boot or change, systemctl dash dash failed quickly lists anything that broke.')}
''', kw=['systemctl status', 'systemctl start', 'systemctl stop', 'systemctl restart', 'systemctl reload', 'systemctl enable', 'enable --now', 'systemctl disable', 'systemctl mask', 'is-active', 'is-enabled', 'systemctl --failed', 'list-units'])

K.lesson('write', 'Writing your own service', f'''
{shape('/etc/systemd/system/myapp.service', """[Unit]
Description=My web app
After=network-online.target
Wants=network-online.target

[Service]
User=myapp                       # never run an app as root
WorkingDirectory=/srv/myapp
Environment=PORT=8080
ExecStart=/srv/myapp/venv/bin/python app.py
Restart=on-failure               # start it again if it crashes
RestartSec=5
NoNewPrivileges=yes              # sandboxing, see systemd.exec(5)
ProtectSystem=full
PrivateTmp=yes

[Install]
WantedBy=multi-user.target""", note='ExecStart needs a full path. The program must stay in the foreground, because systemd watches that process. Do not use & or nohup here.')}
{table(['Setting', 'Effect'], [
    ['<code>Type=simple</code> (default)', 'the program in ExecStart is the service itself'],
    ['<code>Type=oneshot</code>', 'a job that runs and ends, such as a backup started by a timer'],
    ['<code>Type=forking</code>', 'old style daemons that fork into the background, such as nginx'],
    ['<code>Restart=on-failure</code>, <code>always</code>', 'restart after a crash or a non-zero exit, or after any exit'],
    ['<code>EnvironmentFile=/etc/myapp.env</code>', 'read KEY=value lines, keeps secrets out of the unit file'],
    ['<code>ProtectHome=yes</code>, <code>ProtectSystem=strict</code>', 'hide /home, make the whole file system read-only for the service'],
    ['<code>DynamicUser=yes</code>', 'run as a temporary user that exists only while the service runs']])}
{steps('From unit file to running service', [
    '<b>Write the unit.</b> Create the file in /etc/systemd/system with sudo, for example with <code>sudo systemctl edit --force --full myapp.service</code>.',
    '<b>Reload.</b> <code>sudo systemctl daemon-reload</code> makes systemd read it.',
    '<b>Enable and start.</b> <code>sudo systemctl enable --now myapp</code>.',
    '<b>Check.</b> <code>systemctl status myapp</code> and <code>journalctl -u myapp -f</code> to watch the log.',
    '<b>Change later.</b> Edit, then daemon-reload and restart. systemctl status warns when the file changed on disk without a reload.'])}
{talk('Turning your own program into a service is easy and gives you a lot for free: start at boot, automatic restarts after crashes, logging, and security limits. Create a file in slash etc slash systemd slash system ending in dot service. In the Unit section give a description and say that it should start after the network is online. In the Service section, name the user it runs as, because an app should never run as root, and give the full path of the program in ExecStart. The program must stay in the foreground, since systemd watches that process. Restart equals on failure brings it back after a crash. Options such as ProtectSystem and PrivateTmp put the service in a small sandbox. In the Install section, WantedBy multi user target makes it start at boot. Then run daemon reload, enable dash dash now, and check it with systemctl status and journalctl dash u.')}
''', kw=['write systemd service', 'ExecStart', 'Type=simple', 'Type=oneshot', 'Type=forking', 'Restart=on-failure', 'User=', 'EnvironmentFile', 'ProtectSystem', 'PrivateTmp', 'DynamicUser', 'network-online.target', 'custom service'])

K.lesson('practice', 'Practice: fix and add services in the practice shell', f'''
<p>The practice computer runs cron, ssh and nginx as services, and a backup job failed last night. Its systemctl and journalctl follow systemd 255, and nothing here can harm a real machine.</p>
{lab('Find the failure, then run your own service', [
    ('List the units that failed.', 'systemctl --failed', [{'out': 'backup.service'}]),
    ('Read the error lines of the backup unit from the journal (it needs root).', 'sudo journalctl -u backup -p err', [{'out': 'No such file or directory'}]),
    ('Restart nginx.', 'sudo systemctl restart nginx', [{'cmd': r'systemctl\s+restart\s+nginx'}, {'code': 0}]),
    ('Write a script heartbeat.sh that runs date and sleep 60 in a loop, and make it executable.', """printf '#!/bin/bash\\nwhile true; do date; sleep 60; done\\n' > heartbeat.sh && chmod +x heartbeat.sh""", [{'mode': ['heartbeat.sh', '755']}]),
    ('Write /etc/systemd/system/heartbeat.service that runs /home/learner/heartbeat.sh as the user learner and is wanted by multi-user.target.', """printf '[Unit]\\nDescription=Heartbeat demo\\n\\n[Service]\\nExecStart=/home/learner/heartbeat.sh\\nUser=learner\\nRestart=on-failure\\n\\n[Install]\\nWantedBy=multi-user.target\\n' | sudo tee /etc/systemd/system/heartbeat.service""", [{'has': ['/etc/systemd/system/heartbeat.service', 'ExecStart=/home/learner/heartbeat.sh']}]),
    ('Tell systemd to read unit files again.', 'sudo systemctl daemon-reload', [{'cmd': r'systemctl\s+daemon-reload'}]),
    ('Enable the service and start it now, in one command.', 'sudo systemctl enable --now heartbeat', [{'exists': '/etc/systemd/system/multi-user.target.wants/heartbeat.service', 'type': 'l'}]),
    ('Check that it runs.', 'systemctl is-active heartbeat', [{'out': '^active$'}])])}
{talk('Now practise on the pretend server. First list the failed units, and read the error lines of the failed backup with journalctl, which needs sudo. Then restart nginx. After that, write a tiny script that prints the date every minute, write a service file for it in slash etc slash systemd slash system with sudo tee, reload systemd, enable and start it in one command, and check that it is active.')}
''', kw=['systemctl practice', 'service lab', 'journalctl practice', 'enable --now practice', 'failed unit practice'])

K.lesson('levels', 'Boot and services from school to research', f'''
{ladder(
    '<p>A computer starts in stages: firmware, boot loader, kernel, then systemd, which starts the services. systemctl status, start, stop and enable control services.</p>',
    '<p>Order and requirement are different things: After= only orders, Wants= and Requires= pull units in. Use network-online.target only when a service really needs a working network at start. <code>systemd-analyze blame</code> and <code>systemd-analyze critical-chain</code> show what slows the boot. Socket activation starts a service on its first connection.</p>',
    '<p>systemd puts each service in its own cgroup, so it can limit memory and CPU (MemoryMax=, CPUQuota=) and always kill every process of a service. <code>systemd-analyze security NAME</code> scores a unit’s sandbox. Secure Boot checks signatures from the firmware through the boot loader to the kernel, and measured boot records hashes in the TPM so disk keys unlock only on an untouched system.</p>',
    '<p>Init systems are a long-running debate: SysV init scripts ran one after another, Upstart reacted to events, and systemd uses dependencies and parallel start-up. Research and industry work on unified kernel images, which bundle kernel, initramfs and command line into one signed UEFI file, and on fast boot for containers and micro-VMs such as Firecracker, which start a kernel in about a hundred milliseconds.</p>')}
{scene('the server that waited 90 seconds', '<p>After a reboot a web server took two minutes to come up. <code>systemd-analyze critical-chain</code> showed a mount of a network share waiting 90 seconds for a server that had been retired. The fix added <code>nofail</code> and <code>x-systemd.mount-timeout=10</code> to the fstab line, and the boot went back to 14 seconds. The team now checks <code>systemctl --failed</code> and the boot time after every kernel update.</p>')}
{talk('Here is the bigger picture on boot and services. In unit files, After only sets the order, while Wants and Requires actually pull another unit in, and mixing these up is a common mistake. Systemd analyze blame and critical chain show which units slow down the boot. Each service lives in its own control group, so systemd can limit its memory and CPU, and when you stop a service every one of its processes is stopped. Systemd analyze security gives each service a score for how well it is sandboxed. Secure Boot checks digital signatures at each stage, and a T P M chip can keep disk keys locked unless the boot was untouched. Historically, Linux moved from simple numbered init scripts to systemd’s dependency based, parallel start, and today researchers work on single signed boot images and on virtual machines that boot in a fraction of a second.')}
''', kw=['After vs Wants', 'Requires', 'systemd-analyze blame', 'critical-chain', 'socket activation', 'cgroups', 'MemoryMax', 'systemd-analyze security', 'Secure Boot', 'measured boot', 'TPM', 'SysV init', 'unified kernel image', 'Firecracker'])

K.quiz('e', 'Which program runs as process 1 on most Linux systems today?', ['bash', 'systemd', 'grub', 'sshd'], 1, 'The service manager.', 'systemd is PID 1.')
K.quiz('e', 'Which command shows whether the nginx service runs?', ['systemctl status nginx', 'ps nginx', 'service list', 'nginx --status'], 0, 'status.', 'systemctl status NAME.')
K.quiz('e', 'Which boot loader do most Linux systems use?', ['NTLDR', 'GRUB', 'systemd', 'BIOS'], 1, 'Grand Unified.', 'GRUB loads the kernel.')
K.quiz('e', 'Which command makes a service start at every boot?', ['systemctl start', 'systemctl enable', 'systemctl reload', 'systemctl status'], 1, 'Enable.', 'enable creates the boot link.')
K.quiz('m', 'What is the initramfs for?', ['Storing user files', 'Loading the drivers needed to mount the real root disk', 'Showing the boot menu', 'Running cron'], 1, 'Early root.', 'It is a small root in memory.')
K.quiz('m', 'Which target is the usual default on a server?', ['graphical.target', 'multi-user.target', 'rescue.target', 'poweroff.target'], 1, 'No desktop.', 'multi-user is runlevel 3.')
K.quiz('m', 'Where should your own unit files go?', ['/usr/lib/systemd/system', '/etc/systemd/system', '/home/units', '/var/systemd'], 1, 'etc.', '/etc wins over /usr/lib.')
K.quiz('m', 'What must you run after editing a unit file?', ['sudo reboot', 'sudo systemctl daemon-reload', 'sudo update-grub', 'nothing'], 1, 'Reload.', 'daemon-reload re-reads unit files.')
K.quiz('m', 'What does systemctl mask do?', ['Hides the log', 'Forbids any start of the unit', 'Encrypts the unit', 'Disables logging'], 1, 'Stronger than disable.', 'It links the unit to /dev/null.')
K.quiz('h', 'Why should a program in ExecStart not end with &?', ['It is slower', 'systemd watches the foreground process, and & makes it exit at once', 'It is a syntax error in bash', 'It disables logging'], 1, 'Foreground.', 'The main process must keep running.')
K.quiz('h', 'A unit has After=db.service but no Wants=. If db.service is not started, what happens?', ['The unit waits forever', 'The unit starts without db, After only orders', 'Boot fails', 'db is started automatically'], 1, 'Order only.', 'Wants or Requires pull units in.')
K.quiz('h', 'Which file do you edit to change the kernel command line permanently on Debian?', ['/boot/grub/grub.cfg', '/etc/default/grub, then update-grub', '/proc/cmdline', '/etc/fstab'], 1, 'Generated file.', 'grub.cfg is generated from /etc/default/grub.')
K.quiz('h', 'A disk in /etc/fstab is missing at boot. What keeps the boot from dropping to emergency mode?', ['The option nofail', 'The option ro', 'Removing the UUID', 'mask local-fs.target'], 0, 'No fail.', 'nofail lets the boot go on.')
K.quiz('x', 'Which command scores how well a service is sandboxed?', ['systemd-analyze blame', 'systemd-analyze security', 'systemctl status', 'journalctl -p'], 1, 'Security.', 'systemd-analyze security NAME.')

K.calc('e', 'How many old runlevels map to multi-user.target on Ubuntu?', '3', 'Count them.', ['runlevel2, runlevel3 and runlevel4.', 'All three link to multi-user.target.', eq('3')], check=3)
K.calc('e', 'A service has Restart=on-failure and RestartSec=5. It crashes at 10:00:00. At how many seconds past 10:00 does it start again?', '5', 'Wait, then start.', ['systemd waits RestartSec.', '0 + 5.', eq('10:00:05')], check=5)
K.calc('m', 'apt-daily.timer fires at 06:00 with RandomizedDelaySec=12h. What is the latest hour it can start?', '18', 'Add up to 12 hours.', ['Planned at 06:00.', 'Plus at most 12 h.', eq('06 + 12 = 18')], check=18)
K.calc('m', 'A boot took 2 s in firmware, 1 s in GRUB, 3 s in the kernel and 8 s in user space. How many seconds in total?', '14', 'Add the stages.', ['2 + 1 + 3.', 'Plus 8 for systemd.', eq('14 s')], check=14)
K.calc('h', 'A service sets MemoryMax=512M and uses 384M. How many MB more may it use?', '128', 'Subtract.', ['The limit is 512.', '512 − 384.', eq('128 MB')], check=128)
K.calc('h', 'systemctl is-active prints inactive. Which exit status does it return?', '3', 'Not 0.', ['0 means active.', 'inactive gives 3, as LSB status codes say.', eq('3')], check=3)

K.must('Boot order', 'Firmware (UEFI or BIOS), GRUB, kernel, initramfs, systemd as PID 1, targets, login.')
K.must('Targets', 'multi-user.target for servers, graphical.target for desktops, rescue and emergency for repairs.')
K.must('Unit files', '/usr/lib/systemd/system from packages, /etc/systemd/system yours and stronger. systemctl edit for overrides, daemon-reload after changes.')
K.must('systemctl', 'status, start, stop, restart, reload, enable --now, disable, mask, is-active, --failed.')
K.must('Your service', 'Full path in ExecStart, stays in the foreground, User=, Restart=on-failure, WantedBy=multi-user.target, sandbox options.')

T = K.topic(
    slug='boot-systemd', topic='boot-systemd',
    step=(2, 'Boot, services and logs', 'lx-admin-2', 'Follow the boot from firmware to login, manage services with systemd, and read the logs to find out what went wrong.', 'Intermediate'),
    title='Boot and services: GRUB, systemd and systemctl', short='Boot and systemd', badge='2.1', minutes=55, added='2026-11-23',
    lead='Follow a Linux machine from the power button to the login prompt, read unit files, control services with systemctl, and write your own service with restarts and a sandbox.',
    desc='Firmware, GRUB and /etc/default/grub, the kernel and initramfs, systemd as PID 1, targets and runlevels, rescue and emergency mode, unit types, unit file folders and drop-ins, systemd-analyze verify, systemctl status, start, stop, restart, reload, enable, disable, mask, is-active and --failed, and writing a service with User=, Restart= and sandboxing.',
    summary='The boot stages, targets, unit files, systemctl, and writing your own service.',
    keywords=['boot', 'GRUB', 'initramfs', 'systemd', 'systemctl', 'unit file', 'target', 'service', 'enable', 'daemon-reload'],
    recap='<p>A machine boots through firmware, GRUB, the kernel and the initramfs to systemd, which starts units until the default target. Unit files live in /usr/lib/systemd/system and, stronger, /etc/systemd/system. systemctl starts, stops, enables and inspects services, and your own services need a foreground ExecStart, a user and a restart rule.</p>')
