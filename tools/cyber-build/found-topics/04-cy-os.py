# Foundations 2.1: operating systems for security. Checked against the Linux man pages chmod(1), umask(2), open(2),
# path_resolution(7), passwd(5) and shadow(5), Microsoft Learn (security identifiers, access control lists and the
# order of ACEs in a DACL, User Account Control, audit events 4624, 4625, 4672, 4688, 4720, 4740 and 1102), the Intel
# 64 and IA-32 Software Developer's Manual vol. 3 (privilege levels) and Silberschatz, Galvin and Gagne, Operating
# System Concepts (10th edition).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-os')
K = Kit()

K.code('octal_perms', r'''
# Turn an octal mode such as 754 into the rwx letters that ls -l shows
def letters(digit):
    out = ""
    out = out + ("r" if digit & 4 else "-")    # read is worth 4
    out = out + ("w" if digit & 2 else "-")    # write is worth 2
    out = out + ("x" if digit & 1 else "-")    # execute is worth 1
    return out

for mode in ["754", "644", "600", "777"]:
    text = ""
    for ch in mode:
        text = text + letters(int(ch))
    print(mode, "->", text)

# And back: rwxr-xr-- to octal
def to_octal(text):
    value = {"r": 4, "w": 2, "x": 1, "-": 0}
    result = ""
    for start in [0, 3, 6]:
        total = 0
        for ch in text[start:start + 3]:
            total = total + value[ch]
        result = result + str(total)
    return result

print("rwxr-xr-- ->", to_octal("rwxr-xr--"))
print("rw-r----- ->", to_octal("rw-r-----"))
''')

K.code('umask_calc', r'''
# New files start from 666 (rw for all) and new folders from 777, then the umask REMOVES bits
def apply_umask(start, umask):
    return start & ~umask          # keep only the bits that the umask does not block

for umask in [0o022, 0o027, 0o077]:
    file_mode = apply_umask(0o666, umask)
    dir_mode = apply_umask(0o777, umask)
    print("umask", format(umask, "03o"), "-> new file", format(file_mode, "03o"), " new folder", format(dir_mode, "03o"))
''')

K.code('access_check', r'''
# How the Linux kernel decides: owner first, then group, then other. Only the FIRST class that matches is used.
def can_access(user, user_groups, owner, group, mode, want):
    bit = {"read": 4, "write": 2, "execute": 1}[want]
    if user == "root":
        if want == "execute":
            return (mode & 0o111) != 0      # root still needs some execute bit to run a file
        return True                         # root skips read and write checks
    if user == owner:
        digit = (mode >> 6) & 7
    elif group in user_groups:
        digit = (mode >> 3) & 7
    else:
        digit = mode & 7
    return (digit & bit) != 0

print(can_access("riya", ["staff"], "riya", "staff", 0o754, "write"))   # owner digit 7: True
print(can_access("amit", ["staff"], "riya", "staff", 0o754, "write"))   # group digit 5: False
print(can_access("amit", ["staff"], "riya", "staff", 0o604, "read"))    # group digit 0: False, even though other may read
print(can_access("root", [], "riya", "staff", 0o600, "read"))           # root: True
''')

K.code('passwd_check', r'''
# Audit a copy of /etc/passwd: every account with user id 0 has full root power
passwd = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
riya:x:1000:1000:Riya:/home/riya:/bin/bash
backup:x:0:0:old backup job:/var/backups:/bin/bash
www-data:x:33:33:web server:/var/www:/usr/sbin/nologin"""

for line in passwd.split("\n"):
    name, password, uid, gid, comment, home, shell = line.split(":")
    if uid == "0":
        warning = "  <-- root power" if name != "root" else ""
        print("uid 0:", name + warning)
    if not shell.endswith("nologin") and int(uid) >= 1000:
        print("person who can log in:", name)
''')

K.code('failed_logins', r'''
# Windows writes event 4625 for every failed logon. Many failures for one account in a short time look like guessing.
events = [
    ("09:00:01", 4625, "admin"), ("09:00:02", 4625, "admin"), ("09:00:03", 4625, "admin"),
    ("09:00:04", 4625, "admin"), ("09:00:05", 4625, "admin"), ("09:00:09", 4624, "admin"),
    ("09:10:00", 4625, "riya"), ("09:12:30", 4624, "riya"),
]

failures = {}
for time, event_id, account in events:
    if event_id == 4625:
        failures[account] = failures.get(account, 0) + 1

limit = 5
for account, count in failures.items():
    if count >= limit:
        print(account, "had", count, "failed logons: possible password guessing")
    else:
        print(account, "had", count, "failed logon(s): normal")

# A failure burst followed by a success (4624) is the worst sign: the guess may have worked
for i in range(1, len(events)):
    if events[i][1] == 4624 and events[i - 1][1] == 4625 and failures.get(events[i][2], 0) >= limit:
        print("ALERT: success after many failures for", events[i][2], "at", events[i][0])
''')

K.code('suid_audit', r'''
# Find files with the setuid bit (octal 4000). A setuid program runs with its OWNER's rights.
files_found = [
    ("/usr/bin/passwd", "root", 0o4755),
    ("/usr/bin/sudo", "root", 0o4755),
    ("/home/riya/tool", "riya", 0o0755),
    ("/opt/backup/run.sh", "root", 0o4777),
    ("/usr/bin/ls", "root", 0o0755),
]

expected = ["/usr/bin/passwd", "/usr/bin/sudo"]
for path, owner, mode in files_found:
    if mode & 0o4000:
        risky = ""
        if mode & 0o002:
            risky = " and ANYONE can change it: a user could put their own code here and run it as root"
        elif path not in expected:
            risky = " (unexpected, check why)"
        print("setuid", format(mode, "04o"), owner, path + risky)
''')

K.lesson('idea', 'What an operating system does for security', f'''
{talk('An operating system is the big program that runs all the other programs, like Windows, macOS, Linux, Android or iOS. In the early 1960s, computers ran one job at a time, and security barely existed. Then time sharing arrived: many people used one expensive computer at the same time. Suddenly one user’s program could read another user’s files or crash the whole machine. The Multics project in the late 1960s, built by MIT, Bell Labs and General Electric, introduced many ideas we still use, such as protection rings and access control lists. Its younger cousin, Unix, gave us users, groups and the read, write, execute permissions you will learn today. Linux and macOS come straight from that Unix family. The key idea is simple: programs are not trusted to police themselves. A small, trusted core called the kernel checks every request.')}
{src('Linux man pages chmod(1), umask(2), open(2), passwd(5) and shadow(5), Microsoft Learn on SIDs, ACLs, UAC and audit events, and Silberschatz, Operating System Concepts.')}
{wwh('An <b>operating system</b> (OS) shares the computer’s CPU, memory, disk and network between many programs and users. Its trusted core, the <b>kernel</b>, enforces who may do what.',
     'Without the OS, any program could read any file, watch any keystroke and crash the machine. The OS keeps users apart, keeps programs apart, and keeps them away from the hardware.',
     'The CPU has at least two modes. Normal programs run in <b>user mode</b> and must ask the kernel, through a <b>system call</b>, to open files, use the network or start programs. The kernel, in <b>kernel mode</b>, checks the request against the user’s identity and the object’s permissions, then does the work or refuses.')}
<p>Press <b>Step</b> to follow a request from a program into the kernel and back. Change the request and play again.</p>
{viz('cyrings')}
{table(['OS job', 'Security meaning'], [
    ['Process isolation', 'Each program gets its own virtual memory. One program cannot read another’s memory'],
    ['User accounts', 'Every action is done as some user, so permissions and logs have a name attached'],
    ['File permissions', 'The kernel checks read, write and execute rights on every open'],
    ['Privilege levels', 'Only the kernel (ring 0) touches hardware. Programs run in ring 3'],
    ['Logging', 'Logons, failures, new processes and permission changes are recorded'],
    ['Updates', 'The OS vendor ships fixes for its own bugs, which attackers race to use']])}
{note('The kernel is the most trusted code on the machine. A bug in the kernel gives an attacker everything, which is why kernel updates matter so much and why the kernel is kept as small as practical.', 'tip')}
''', kw=['operating system', 'kernel', 'user mode', 'kernel mode', 'system call', 'protection rings', 'process isolation', 'Multics', 'Unix'])

K.lesson('users', 'Users, groups and the all powerful administrator', f'''
{talk('Every action on a computer happens on behalf of some user. When you log in, the operating system gives your session an identity, and every program you start carries it. On Linux, that identity is a number called the user ID. The user with ID zero, named root, can do almost anything: read every file, kill any program, change any setting. Windows has a similar idea with the Administrator account and security identifiers. Because root is so powerful, attackers always try to become root, and good administrators avoid logging in as root at all. Instead, they use a normal account and borrow root power for one command at a time with sudo on Linux or the User Account Control prompt on Windows. In this lesson we look at where accounts live and how to spot a dangerous one.')}
{table(['Idea', 'Linux and macOS', 'Windows'], [
    ['Identity of a user', 'User ID (UID), a number. root is UID 0', 'Security identifier (SID), for example S-1-5-21-...-1001'],
    ['Super user', 'root (UID 0)', 'Administrator (the built in account has RID 500), SYSTEM for services'],
    ['Account list', '/etc/passwd (readable by everyone, no passwords inside)', 'The SAM database, or Active Directory in a company'],
    ['Password hashes', '/etc/shadow (readable only by root, and the shadow group on Ubuntu)', 'SAM and NTDS.dit on domain controllers'],
    ['Borrow admin power', 'sudo, controlled by /etc/sudoers', 'User Account Control (UAC) consent or credential prompt'],
    ['Groups', '/etc/group, for example sudo, staff, docker', 'Local groups and domain groups, for example Administrators']])}
{run('passwd_check')}
{show('A line of /etc/passwd', 'riya:x:1000:1000:Riya Sharma:/home/riya:/bin/bash', {1: 'Seven fields split by colons: user name, x (the hash lives in /etc/shadow), UID, primary group ID, comment, home folder and login shell.'}, lang='text')}
{scene('the second root account', '<p>During an audit, a security analyst runs a simple check for accounts with UID 0 and finds two: root and a forgotten account named backup. Someone had copied the root line years ago to make a quick backup job. Anyone who guessed its weak password would have full control of the server without ever touching the root password. Checking for UID 0 accounts is one of the first steps after a suspected break in, because attackers like to hide a second root account.</p>')}
{note('Being in the docker group on Linux is close to being root, because a user who can start containers can mount the whole disk into one. Treat such groups like admin rights.', 'warn')}
''', kw=['users', 'groups', 'root', 'UID 0', 'Administrator', 'SID', 'etc passwd', 'etc shadow', 'SAM', 'sudo', 'UAC', 'docker group'])

K.lesson('perms', 'Linux permissions and the octal maths of chmod', f'''
{talk('Unix gave every file three kinds of permission, read, write and execute, for three kinds of people: the file’s owner, the members of the file’s group, and everyone else. That is nine switches in total, and Ken Thompson and Dennis Ritchie at Bell Labs found a clever way to write them as just three digits. Each digit is a small sum: read is worth four, write two and execute one. So seven means all three, five means read and execute, and zero means nothing. This is called octal, base eight, because one digit goes from zero to seven. When a security person sees mode 777 on a file, they wince, because it means anyone on the machine can change it. When they see 600 on a private key, they relax. Let us learn to read these numbers at a glance, and learn one surprising rule the kernel follows.')}
{wwh('A Linux <b>mode</b> has three octal digits for the <b>owner</b>, the <b>group</b> and <b>others</b>. Each digit adds read (4), write (2) and execute (1). An optional fourth digit in front holds setuid (4), setgid (2) and sticky (1).',
     'Permissions are the main way a multi user system keeps people out of each other’s files. Wrong permissions, such as a world writable script run by root, are a classic way attackers gain more power.',
     'On every open the kernel finds the <b>first</b> class that matches you (owner, else group, else other) and uses only that digit. Then it checks the bit you asked for.')}
{viz('cychmod')}
{run('octal_perms')}
{run('access_check')}
{table(['Mode', 'Letters', 'Typical use'], [
    ['600', 'rw-------', 'Private keys (~/.ssh/id_ed25519), password files'],
    ['644', 'rw-r--r--', 'Normal documents and web pages'],
    ['700', 'rwx------', 'A private folder or script'],
    ['755', 'rwxr-xr-x', 'Programs and public folders'],
    ['777', 'rwxrwxrwx', 'Almost always a mistake: anyone can change it'],
    ['1777', 'rwxrwxrwt', '/tmp: everyone may write, but only owners may delete their files (sticky bit)'],
    ['4755', 'rwsr-xr-x', '/usr/bin/passwd: runs as root so users can change their own password (setuid)']])}
{fxs(fx('One octal digit', 'digit = 4r + 2w + 1x', 'r, w and x are 1 when allowed, 0 when not. 6 = 4 + 2 = rw-.', key=True),
     fx('umask', 'new mode = default AND (NOT umask)', 'Default 666 for files and 777 for folders. umask 022 gives files 644 and folders 755. umask 077 gives 600 and 700.', key=True))}
{run('umask_calc')}
{term(['$ ls -l report.txt', '-rw-r----- 1 riya staff 2048 Nov 14 10:02 report.txt', '$ chmod 600 report.txt', '$ ls -l report.txt', '-rw------- 1 riya staff 2048 Nov 14 10:02 report.txt', '$ chmod g+r,o-rwx report.txt   # symbolic form: add read for group, remove all for others'], 'chmod on Linux')}
{note('Because only the first matching class counts, mode 604 lets "other" read a file but blocks its own group. Owner and group are not "at least other". This trips up many students.', 'exam')}
''', kw=['permissions', 'chmod', 'octal', 'rwx', 'owner group other', 'umask', 'setuid', 'setgid', 'sticky bit', '777', '644', '600', 'ls -l'])

K.lesson('windows', 'Windows access control lists', f'''
{talk('Windows took a different path from Unix. Instead of nine fixed switches, every file, folder, registry key and service in Windows can carry a full list of rules, called an access control list. Each rule, called an access control entry, says that a particular user or group is allowed or denied some right, such as read or modify. This design came from the VMS operating system, because the lead designer of Windows NT, Dave Cutler, had built VMS before joining Microsoft in 1988. Lists are far more flexible than nine bits, but flexibility has a cost: long lists, inherited rules from parent folders, and deny rules can make it hard to see who really has access. Attackers love that confusion. In this lesson you will learn the order in which Windows reads the rules, which decides the answer.')}
{wwh('An <b>access control list</b> (DACL) on a Windows object is an ordered list of <b>access control entries</b> (ACEs). Each ACE allows or denies specific rights to one SID (a user or a group).',
     'Real organisations need fine grained rules: the finance group may edit, auditors may read, contractors may not even list the folder. Nine Unix bits cannot say all that.',
     'Windows walks the ACEs in order until every requested right is granted or one is denied. In the normal (canonical) order, explicit deny comes first, then explicit allow, then inherited deny, then inherited allow. If no ACE grants a right, it is denied.')}
{show('icacls output for a folder (Windows)', '''C:\\Finance BUILTIN\\Administrators:(OI)(CI)(F)
          CORP\\Finance:(OI)(CI)(M)
          CORP\\Auditors:(OI)(CI)(RX)
          CORP\\Contractors:(OI)(CI)(DENY)(RX)''', {1: 'Administrators have Full control (F). (OI)(CI) means the rule is inherited by files (object inherit) and subfolders (container inherit).', 2: 'The Finance group may Modify (M): read, write, delete.', 3: 'Auditors may Read and eXecute (RX) only.', 4: 'Contractors are explicitly denied. Explicit deny is checked before any allow, so a contractor who is also in Finance is still blocked.'}, lang='text')}
{table(['ACE order (canonical)', 'Effect'], [
    ['1. Explicit deny', 'Set on this object. Wins over every allow'],
    ['2. Explicit allow', 'Set on this object. Wins over inherited deny'],
    ['3. Inherited deny', 'Comes from a parent folder'],
    ['4. Inherited allow', 'Comes from a parent folder'],
    ['No matching ACE', 'Access denied (implicit deny)']])}
{note('An explicit allow on a file beats an inherited deny from its parent folder, because explicit ACEs come first. "Deny always wins" is only true when the deny is at the same level or closer.', 'exam')}
{note('Leave the built in Administrator and SYSTEM accounts out of daily work. Use a normal account and let UAC ask for admin rights only when needed, so malware you open by mistake does not start with full power.', 'tip')}
''', kw=['Windows', 'ACL', 'DACL', 'ACE', 'icacls', 'NTFS permissions', 'explicit deny', 'inheritance', 'implicit deny', 'canonical order'])

K.lesson('privesc', 'Processes and privilege escalation', f'''
{talk('A process is a program that is running. When you open a browser, the operating system creates a process, gives it memory and an identity, and lets it run. Attackers who break into a machine usually land as a weak user, perhaps the web server account. Their next goal is privilege escalation: turning that weak foothold into root or SYSTEM. They look for mistakes. A setuid program that anyone can edit. A service that runs as SYSTEM but reads its settings from a folder normal users can write to. A scheduled task running an old script. A kernel that has not been patched. Penetration testers check exactly these things, and defenders remove them. In this lesson you will audit a list of files for one of the most famous mistakes, the dangerous setuid file.')}
{wwh('<b>Privilege escalation</b> is gaining more rights than you were given. <b>Vertical</b>: a normal user becomes admin. <b>Horizontal</b>: one user reaches another user’s data at the same level.',
     'Most attacks start with low rights (a phished user, a web app account). Escalation turns a small breach into full control, so stopping it limits the damage.',
     'Attackers look for misconfigured permissions, setuid files, services and scheduled tasks that run as admin but can be changed by users, stored passwords, and unpatched kernel bugs. Defenders follow least privilege, patch quickly and audit these places.')}
{run('suid_audit')}
{attack([
    ['Finds a world writable script run by root from cron', 'Scripts run by root must be owned by root and not writable by others (mode 700 or 755)'],
    ['Uses a setuid program that can run a shell', 'Keep setuid files to a short known list, audit with find / -perm -4000'],
    ['Changes the program path of a Windows service', 'Service folders and registry keys writable only by admins'],
    ['Reads a password from a config file or shell history', 'Store secrets in a vault, set files to 600'],
    ['Uses a public kernel exploit', 'Patch the kernel quickly, enable automatic security updates'],
    ['Abuses membership of docker or Administrators', 'Least privilege: remove people from powerful groups they do not need']])}
{safe('Practise privilege escalation only on machines you own, such as a virtual machine you set up yourself, or on legal training labs made for this purpose. The program above only reads a made up list.')}
''', kw=['process', 'privilege escalation', 'vertical', 'horizontal', 'setuid audit', 'cron', 'services', 'kernel exploit', 'least privilege'])

K.lesson('logs', 'Where the OS records security events', f'''
{talk('When something goes wrong on a computer, the first question an investigator asks is: what do the logs say? Operating systems keep diaries of important events: who logged in, who failed to log in, which programs started, who changed a permission. On Linux, these go to files in the var log folder or to the systemd journal. On Windows, they go to the Event Log, and each kind of event has a number. You will meet event 4624, a successful logon, and 4625, a failed logon, again and again in security work. A long run of 4625 events followed by a 4624 is the classic picture of a password guessing attack that finally worked. Logs are only useful if they are switched on, kept long enough, and protected, because a clever attacker’s first job is to delete them.')}
{table(['Event', 'Windows Security log ID', 'Linux place'], [
    ['Successful logon', '4624', '/var/log/auth.log (Ubuntu, Debian) or /var/log/secure (RHEL), and journalctl'],
    ['Failed logon', '4625', 'Same files: "Failed password for ..." lines from sshd'],
    ['Special (admin) rights given at logon', '4672', 'sudo lines in auth.log'],
    ['New process created', '4688', 'auditd EXECVE records, if auditd is set up'],
    ['User account created', '4720', 'useradd lines in auth.log'],
    ['Account locked out', '4740', 'pam_faillock messages'],
    ['Audit log cleared', '1102', 'Missing or truncated log files']])}
{run('failed_logins')}
{note('Event 1102 (the security log was cleared) almost never happens in normal work. When it shows up, treat it as a sign that someone is hiding their tracks.', 'exam')}
{note('Logs on the same machine an attacker controls can be deleted. Send copies to a separate log server or SIEM as they are written. Security Operations covers this in depth.', 'tip')}
''', kw=['logs', 'event log', '4624', '4625', '4672', '4688', '4720', '4740', '1102', 'auth.log', 'journalctl', 'brute force detection'])

K.lesson('versus', 'Security models compared', f'''
{talk('Not every operating system protects things the same way. The Unix model that Linux and macOS use is called discretionary access control: the owner of a file decides who may use it. That is simple, but it means a careless owner, or malware running as that owner, can give everything away. Military systems in the 1970s and 1980s wanted something stricter, called mandatory access control, where a central policy decides and even the owner cannot override it. Linux later gained mandatory controls too, with SELinux, first released by the American National Security Agency in 2000, and AppArmor. Phones went further still: Android and iOS put each app in its own sandbox and ask you before an app may use the camera or your contacts. Let us compare these models.')}
{versus('How operating systems decide access', ['', 'Unix permissions (DAC)', 'Windows ACLs (DAC)', 'SELinux and AppArmor (MAC)', 'Mobile sandboxes (Android, iOS)'], [
    ['Who decides', 'The file owner', 'The object owner, with inheritance', 'A central policy written by admins', 'The OS and the user, per app permission'],
    ['Detail', 'Nine bits plus special bits', 'Long lists per user or group, allow and deny', 'Labels on every process and file', 'Each app is its own user in its own sandbox'],
    ['Strength', 'Simple, fast, easy to audit', 'Very flexible', 'Even root processes are limited by policy', 'One bad app cannot read other apps’ data'],
    ['Weakness', 'Owner or malware as the owner can give away access', 'Hard to see who really has access', 'Policies are hard to write, often switched off', 'Users click "Allow" without reading']],
    'Discretionary control trusts owners, mandatory control trusts a central policy. Modern systems layer both: Unix bits or ACLs for daily sharing, and SELinux, AppArmor or app sandboxes to contain programs that get taken over.')}
''', kw=['DAC', 'MAC', 'SELinux', 'AppArmor', 'sandbox', 'Android permissions', 'iOS', 'discretionary', 'mandatory', 'comparison'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Operating system security goes very deep. A beginner learns that accounts and permissions keep people apart. A college student reads modes like 754, writes umasks and knows the Windows event IDs. A masters student studies how the kernel enforces isolation with virtual memory, page tables and system call filtering, and how containers and virtual machines differ in what they really separate. Researchers formally prove kernels correct, like the seL4 microkernel, whose functional correctness was proved by machine in 2009, or attack the hardware below the kernel, as the Spectre and Meltdown research did in 2018 by showing that the CPU itself can leak memory across the boundaries the OS believes are solid.')}
{ladder(
    '<p>Each person has their own account. Files have rules about who may read or change them. The administrator can do everything, so we use that account only when we must.</p>',
    '<p>Read and set modes in octal, use umask, know that the first matching class decides, audit UID 0 accounts and setuid files, read Windows ACLs in canonical order, and watch events 4624, 4625 and 1102.</p>',
    '<p>The kernel enforces isolation with virtual memory (each process has its own page tables), privilege rings and system call checks. Containers share one kernel and are separated by namespaces, cgroups, capabilities and seccomp filters, so a kernel bug can break out. Virtual machines are separated by a hypervisor and are stronger. Mandatory access control (SELinux type enforcement) limits even root processes.</p>',
    '<p>The seL4 microkernel has a machine checked proof (Klein et al., 2009) that its C code matches its specification, and later proofs of integrity and confidentiality. Spectre and Meltdown (2018) showed that speculative execution in CPUs leaks data across process and kernel boundaries through cache timing, breaking assumptions of the OS model and leading to fixes such as kernel page table isolation.</p>')}
{grow('Explain users, the administrator and why we avoid using it daily.',
      'Decode chmod modes, apply umask, audit accounts and setuid files, and read Windows ACLs and logon events.',
      'Explain containers versus virtual machines, seccomp and SELinux, formally verified kernels and CPU side channels.')}
''', kw=['beginner', 'expert', 'virtual memory', 'containers', 'namespaces', 'seccomp', 'seL4', 'Spectre', 'Meltdown'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'The <b>kernel</b> runs in kernel mode (ring 0). Programs run in user mode (ring 3) and must use <b>system calls</b>, so the kernel checks every request.',
    'Linux identities are UIDs. <b>UID 0 (root)</b> can do almost anything. Windows uses SIDs, Administrator and SYSTEM. Use sudo or UAC instead of logging in as admin.',
    '/etc/passwd lists accounts, /etc/shadow holds the hashes and is readable only by root (and group shadow on Ubuntu).',
    'Mode digits add <b>r = 4, w = 2, x = 1</b> for owner, group and other. 600 private, 644 public read, 755 programs, 777 a mistake.',
    'The kernel uses <b>only the first matching class</b> (owner, else group, else other). Root skips read and write checks.',
    'umask removes bits: new mode = default AND NOT umask. umask 022 gives 644 files and 755 folders. setuid 4000, setgid 2000, sticky 1000.',
    'Windows ACL order: explicit deny, explicit allow, inherited deny, inherited allow, then implicit deny.',
    'Watch 4624 (logon), 4625 (failed logon), 4672, 4688, 4720, 4740 and <b>1102 (log cleared)</b>. Privilege escalation hunts writable root scripts, setuid files, weak services and old kernels.'],
    'Foundations 2.2 explains how computers talk: the OSI and TCP/IP layers, IP addresses and subnet maths, ports, the TCP handshake, DNS and HTTP.')}
{files('Three tasks: an octal digit to rwx letters, the Linux access decision, and counting failed logons per account.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which Linux user ID belongs to root?', ['1', '0', '1000', '65534'], 1, 'The first number.', 'root has UID 0, and any account with UID 0 has root power.')
K.quiz('e', 'In a mode digit, what is write worth?', ['1', '2', '4', '7'], 1, 'r = 4, w = ?, x = 1.', 'Read 4, write 2, execute 1.')
K.quiz('e', 'Which mode should a private SSH key have?', ['777', '755', '600', '644'], 2, 'Only the owner reads and writes.', '600 = rw------- for the owner only.')
K.quiz('e', 'Which Windows event ID records a failed logon?', ['4624', '4625', '4720', '1102'], 1, 'One more than success.', '4625 is a failed logon, 4624 a successful one.')
K.quiz('m', 'What does mode 754 give the group?', ['rwx', 'r-x', 'r--', 'rw-'], 1, 'Middle digit 5 = 4 + 1.', '5 = read + execute = r-x.')
K.quiz('m', 'A program in user mode wants to read a file. It must', ['Read the disk directly', 'Ask the kernel through a system call', 'Switch itself to ring 0', 'Ask another program'], 1, 'The only door.', 'Only the kernel touches hardware, so the program makes a system call.')
K.quiz('m', 'With umask 027, what mode does a new file get (default 666)?', ['640', '750', '644', '600'], 0, '666 AND NOT 027.', 'Owner keeps rw (6), group loses w (4), other loses all (0): 640.')
K.quiz('m', 'What does the sticky bit on /tmp do?', ['Makes files run as root', 'Only a file’s owner can delete it, even though everyone can write in /tmp', 'Hides files', 'Encrypts files'], 1, 'Shared folder rule.', 'Sticky stops users deleting each other’s files in a shared folder.')
K.quiz('m', 'Which Windows event most strongly suggests an attacker hiding tracks?', ['4624', '4688', '1102', '4720'], 2, 'The log itself.', '1102 means the security log was cleared.')
K.quiz('h', 'Mode 604, a group member asks to read. The answer is', ['Allowed, because other may read', 'Denied, because the group digit 0 is used, not the other digit', 'Allowed, because group is above other', 'Depends on the owner'], 1, 'First matching class.', 'The kernel uses the first class that matches (group), and its digit is 0.')
K.quiz('h', 'In a Windows DACL, an inherited deny for Everyone and an explicit allow for Riya on the same file. Can Riya read?', ['No, deny always wins', 'Yes, explicit allow comes before inherited deny', 'Only if she is admin', 'Windows refuses to store that'], 1, 'Canonical order.', 'Explicit ACEs are checked before inherited ones.')
K.quiz('h', 'Why is a root owned setuid file with mode 4777 critical?', ['It is hidden', 'Anyone can replace its code, and it then runs as root', 'It cannot be executed', 'It slows the system'], 1, 'Writable by others and runs as owner.', 'World writable plus setuid root lets any user run their own code as root.')
K.quiz('x', 'In the style of an MIT 6.858 exam: containers share one kernel, while VMs each run their own kernel on a hypervisor. Which statement is right?', ['Containers isolate better than VMs', 'A kernel bug can let a process escape a container, while a VM escape needs a hypervisor bug', 'VMs share memory with the host kernel directly', 'There is no difference'], 1, 'What do they share?', 'A shared kernel is a shared attack surface, so container isolation depends on that kernel being bug free.')
K.quiz('x', 'In the style of a CMU 15-410 question: why does Meltdown break process isolation even with correct page tables?', ['The kernel had a typo', 'Speculative execution reads kernel memory before the permission check finishes and leaks it through cache timing', 'Users had root', 'Page tables were disabled'], 1, 'Hardware side channel.', 'The CPU speculatively loaded protected data, and its trace in the cache could be measured.')

K.calc('e', 'What octal digit means rw- ?', '6', 'r = 4, w = 2.', ['r is on: 4.', 'w is on: 2.', eq('4 + 2 + 0 = 6')], check=4 + 2)
K.calc('e', 'What octal digit means r-x ?', '5', 'r = 4, x = 1.', ['r on: 4.', 'w off: 0, x on: 1.', eq('4 + 0 + 1 = 5')], check=5)
K.calc('e', 'Write rwxr-x--- as a three digit octal mode.', '750', 'Each group of three.', ['rwx = 7.', 'r-x = 5.', eq('--- = 0, so 750')], check='750')
K.calc('m', 'Default file mode 666 with umask 022. What mode does a new file get?', '644', '666 AND NOT 022.', ['Owner 6 minus nothing = 6.', 'Group 6, remove w (2) = 4. Other the same = 4.', eq('644')], check=format(0o666 & ~0o022, 'o'))
K.calc('m', 'Default folder mode 777 with umask 077. What mode does a new folder get?', '700', 'Remove everything for group and other.', ['Owner keeps 7.', 'Group and other lose all bits.', eq('700')], check=format(0o777 & ~0o077, 'o'))
K.calc('m', 'How many different three digit permission modes (without special bits) are there?', '512', 'Each digit has 8 values.', ['Each digit: 0 to 7, so 8 values.', 'Three digits.', eq('8 &times; 8 &times; 8 = 512')], check=8 ** 3)
K.calc('m', 'Mode 4755 as a decimal number (the kernel stores it in binary)?', '2541', 'Octal place values 512, 64, 8, 1.', ['4 &times; 512 = 2048, 7 &times; 64 = 448.', '5 &times; 8 = 40, 5 &times; 1 = 5.', eq('2048 + 448 + 40 + 5 = 2541')], check=0o4755)
K.calc('h', 'A file has mode 640. How many of the nine permission bits are on?', '3', 'Count the 1s.', ['6 = rw- has 2 bits.', '4 = r-- has 1, 0 has 0.', eq('2 + 1 + 0 = 3')], check=bin(0o640).count('1'))
K.calc('h', 'An account had 5 failed logons (4625) at 09:00:01 to 09:00:05, then a success (4624) at 09:00:09. How many seconds from the first failure to the success?', '8', 'Subtract the times.', ['First failure at 09:00:01.', 'Success at 09:00:09.', eq('9 &minus; 1 = 8 seconds')], check=8)
K.calc('h', 'A setuid flag is checked with mode AND 0o4000. What is 0o4755 AND 0o4000 in octal?', '4000', 'Keep only the setuid bit.', ['0o4755 has the 4 in the special digit.', 'AND with 0o4000 keeps only that bit.', eq('result 4000 (not zero, so setuid is set)')], check=format(0o4755 & 0o4000, 'o'))
K.calc('x', 'In the style of an IIT OS course problem: umask u gives new files 640 and new folders 750. Defaults are 666 and 777. What is the umask (3 octal digits)?', '027', 'Find the bits removed from 777.', ['777 &rarr; 750 removes 0 from owner, 2 from group, 7 from other.', 'Check files: 666 AND NOT 027 = 640.', eq('umask = 027')], check='027')

K.assign('rwx', 'e', 'An octal digit to letters',
         '<p>Write <code>rwx(digit)</code> that turns one octal digit (0 to 7) into its three letters, using "-" for a missing right. For example 5 gives "r-x".</p>',
         '''
def rwx(digit):
    # your code here
    pass
''', [('rwx(7)', 'rwx'), ('rwx(5)', 'r-x'), ('rwx(0)', '---'), ('rwx(6)', 'rw-')],
         '''
def rwx(digit):
    out = ""
    if digit & 4:
        out = out + "r"
    else:
        out = out + "-"
    if digit & 2:
        out = out + "w"
    else:
        out = out + "-"
    if digit & 1:
        out = out + "x"
    else:
        out = out + "-"
    return out
''', 'Test each bit with &amp; 4, &amp; 2 and &amp; 1 and add a letter or a dash.', '<p>digit &amp; 4 is not zero exactly when the read bit is on. Testing bits with AND is how the kernel, and every permission tool, reads a mode.</p>')
K.assign('access', 'm', 'The Linux access decision',
         '<p>Write <code>allowed(is_owner, in_group, mode, bit)</code>. mode is a whole number such as 0o754, bit is 4 (read), 2 (write) or 1 (execute). Use the owner digit if is_owner is True, else the group digit if in_group is True, else the other digit. Return True when that digit has the bit.</p>',
         '''
def allowed(is_owner, in_group, mode, bit):
    # your code here
    pass
''', [('allowed(True, True, 0o754, 2)', True), ('allowed(False, True, 0o754, 2)', False), ('allowed(False, True, 0o604, 4)', False), ('allowed(False, False, 0o604, 4)', True)],
         '''
def allowed(is_owner, in_group, mode, bit):
    if is_owner:
        digit = (mode // 64) % 8
    elif in_group:
        digit = (mode // 8) % 8
    else:
        digit = mode % 8
    return (digit & bit) != 0
''', 'The owner digit is (mode // 64) % 8, the group digit (mode // 8) % 8 and the other digit mode % 8. Pick only the first that matches.', '<p>The third test is the trap from the lesson: the group is denied even though others may read, because only the first matching class counts.</p>')
K.assign('fails', 'm', 'Count failed logons per account',
         '<p>Write <code>suspects(events, limit)</code>. events is a list of [event_id, account] pairs. Count the 4625 (failed logon) events per account and return a sorted list of the accounts with at least limit failures.</p>',
         '''
def suspects(events, limit):
    # your code here
    pass
''', [('suspects([[4625, "admin"], [4625, "admin"], [4624, "riya"], [4625, "riya"]], 2)', ['admin']), ('suspects([], 1)', []), ('suspects([[4625, "b"], [4625, "a"], [4625, "b"], [4625, "a"]], 2)', ['a', 'b'])],
         '''
def suspects(events, limit):
    counts = {}
    for event_id, account in events:
        if event_id == 4625:
            counts[account] = counts.get(account, 0) + 1
    found = []
    for account in counts:
        if counts[account] >= limit:
            found.append(account)
    return sorted(found)
''', 'Count only event 4625 in a dict, then keep the accounts whose count reaches the limit, and sort them.', '<p>This is the simplest brute force detection rule, the kind a SIEM runs every minute. Real rules also add a time window, for example 5 failures within 2 minutes.</p>')

K.must('Kernel', 'Programs run in user mode (ring 3), the kernel in kernel mode (ring 0). System calls are the only door, so every request is checked.')
K.must('Accounts', 'Linux UID 0 = root. /etc/passwd lists accounts, /etc/shadow holds hashes. Windows SIDs, Administrator, SYSTEM. Use sudo or UAC.')
K.must('Modes', 'r = 4, w = 2, x = 1 for owner, group, other. 600, 644, 755, never 777. setuid 4000, setgid 2000, sticky 1000.')
K.must('Rules', 'First matching class decides (owner, else group, else other). Root skips r and w checks. new mode = default AND NOT umask.')
K.must('Windows ACLs', 'Order: explicit deny, explicit allow, inherited deny, inherited allow, else implicit deny.')
K.must('Logs', '4624 logon, 4625 failed, 4672 admin rights, 4688 new process, 4720 user created, 4740 lockout, 1102 log cleared.')

T = K.topic(
    slug='cy-os', topic='cy-os', step=(2, 'How computers and networks work', 'cy-f2', 'How operating systems keep users apart, how data moves across networks, and the Python every security person needs.', 'Beginner'),
    title='Operating systems: users, permissions, processes and logs', short='Operating systems', badge='2.1', minutes=60,
    lead='Learn how an operating system protects you: user and kernel mode, system calls, root and Administrator, /etc/passwd and /etc/shadow, Linux permissions with the octal maths of chmod and umask, Windows ACLs, privilege escalation, security logs and the DAC and MAC models.',
    desc='operating system security, kernel, user mode, kernel mode, rings, system calls, users and groups, root UID 0, Administrator, SID, etc passwd, etc shadow, sudo, UAC, Linux permissions, rwx, octal chmod, umask, setuid, setgid, sticky bit, Windows ACL, DACL, ACE order, icacls, privilege escalation, setuid audit, event IDs 4624 4625 4672 4688 4720 4740 1102, auth.log, DAC vs MAC, SELinux, AppArmor, sandboxes, containers vs VMs, seL4, Spectre, Meltdown.',
    summary='user and kernel mode, accounts and root, chmod octal maths and umask, Windows ACLs, privilege escalation and security logs.',
    keywords=['operating system', 'kernel', 'root', 'chmod', 'umask', 'setuid', 'ACL', 'privilege escalation', 'event 4625', 'SELinux'],
    recap='<p>The kernel checks every request. Read modes as 4, 2 and 1, use the first matching class, keep admin rights rare and watch the logs.</p>',
    added='2026-11-14')
