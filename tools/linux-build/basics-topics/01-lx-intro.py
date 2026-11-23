# Foundations 1.1: what an operating system is, the story of Unix and Linux, kernel and user space, distributions,
# where to practise. Sources: The Open Group (UNIX trademark, Single UNIX Specification), IEEE Std 1003.1 (POSIX),
# kernel.org, the TOP500 list (November 2017 onwards all systems run Linux), Linus Torvalds' comp.os.minix post of
# 25 August 1991, the GNU project announcement of 27 September 1983, Ubuntu release cycle pages, Microsoft WSL docs.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk

K = Kit()

K.lesson('os', 'What an operating system does', f'''
<p>A computer is a box of parts: a processor that does sums very fast, memory that remembers things for a short time, a disk that keeps files when the power is off, a screen, a keyboard and a network card. None of these parts knows how to share itself between the apps you run.</p>
<p>The <b>operating system</b> is the program that manages all of those parts for you. When your music app and your browser both want the processor, it gives each one a turn many times a second. When an app wants to save a file, it decides where on the disk the bytes go. When two people use the same computer, it keeps their files apart.</p>
{table(['Part of the computer', 'What the operating system does with it', 'An everyday example'], [
    ['Processor (CPU)', 'Gives every running program a short turn, thousands of times a second', 'Music keeps playing while you type a message'],
    ['Memory (RAM)', 'Gives each program its own space and stops programs reading each other', 'A crashed game does not break your browser'],
    ['Disk', 'Organises bytes into files and folders', 'Your photos are still there after a restart'],
    ['Devices', 'Talks to the keyboard, screen, printer and network card through drivers', 'A new mouse works as soon as you plug it in'],
    ['Users', 'Checks who you are and what you may touch', 'Your brother cannot read your files on a shared laptop']])}
<p>Windows, macOS, Android, iOS and Linux are all operating systems. This subject is about the Unix family, which includes Linux and macOS, and about Linux most of all, because it is the one you will meet on servers, in the cloud, in phones and in almost every company that writes software.</p>
{scene('your phone', '<p>If you have an Android phone, you already use Linux every day. Android is built on the Linux kernel. When you open a camera app, the Linux kernel is the part that talks to the camera chip and hands the picture to the app.</p>')}
{talk('Every time you switch on a computer, a phone or even a smart television, a hidden program wakes up first and takes charge of everything. That program is the operating system. In the 1950s there was no such thing. People booked a computer for an hour, loaded their own program on punched cards, and nobody else could use the machine until they were finished. Operating systems were invented so that many programs, and later many people, could share one expensive machine fairly. Today the same idea runs in your pocket. Your phone has music, maps and messages running at once, and the operating system shares out the processor, the memory and the battery between them, many times every second. In this subject we study the operating system family called Unix, and its most famous member, Linux, which runs most of the servers behind the websites you use.')}
''', kw=['operating system', 'OS', 'kernel', 'CPU', 'memory', 'drivers', 'Android'])

K.lesson('story', 'The story of Unix and Linux', f'''
<p>Unix was born in <b>1969</b> at Bell Labs, the research lab of the American phone company AT&amp;T. Ken Thompson and Dennis Ritchie wanted a simple, friendly system for programmers, and they built it on a spare PDP-7 computer. In <b>1973</b> they rewrote Unix in a new language Ritchie had made, called <b>C</b>. That was a big idea: an operating system written in a high level language could be moved to a new kind of computer by recompiling it, instead of writing it again.</p>
<p>Universities got copies, and the University of California, Berkeley, built its own version called <b>BSD</b>. Companies made their own Unix too, so in <b>1988</b> the IEEE published the first <b>POSIX</b> standard, a list of what every Unix-like system must offer, so that programs work on all of them.</p>
<p>In <b>1983</b> Richard Stallman announced the <b>GNU</b> project to build a completely free Unix-like system. By 1991 GNU had a compiler, a shell and most tools, but no finished kernel. On <b>25 August 1991</b> a 21 year old student in Helsinki, <b>Linus Torvalds</b>, posted that he was making a free operating system kernel "just a hobby, won't be big and professional like gnu". He released Linux 0.01 in September 1991, and in 1992 he put it under the GNU General Public License. GNU tools plus the Linux kernel made a complete free system.</p>
{play('lx-timeline')}
{table(['Name', 'What it is'], [
    ['UNIX (in capitals)', 'A trademark of The Open Group. Only systems that pass its tests (the Single UNIX Specification) may use the name. macOS is one of them.'],
    ['Unix-like', 'Any system that behaves like Unix, certified or not. Linux and FreeBSD are Unix-like.'],
    ['POSIX', 'The IEEE standard (IEEE 1003.1) for the commands, shell and C functions a Unix-like system offers. A POSIX shell script runs on Linux, macOS and BSD.'],
    ['Linux', 'Strictly, only the kernel that Linus Torvalds started. In daily speech, the whole system built on it.'],
    ['GNU/Linux', 'The name the Free Software Foundation prefers for the whole system, because most of the tools come from GNU.']])}
{note('Linux is not Unix code. Linus wrote the kernel from scratch. It is called Unix-like because it follows the same ideas and the POSIX standard.', 'exam')}
{talk('Here is a story about a spare computer. In 1969, at Bell Labs in New Jersey, Ken Thompson found an old PDP-7 machine that nobody was using and wrote a small operating system on it, partly so he could play a space travel game he had written. That system became Unix. A few years later he and Dennis Ritchie rewrote it in the C language, which meant Unix could be copied to new computers easily, and it spread to universities all over the world. Twenty two years after that, in August 1991, a student called Linus Torvalds in Finland wrote a short message to an online group saying he was building a free kernel as a hobby. He expected a few friends to try it. Today Linux runs every one of the five hundred fastest supercomputers on Earth, most cloud servers, and billions of Android phones. A hobby project grew into one of the largest team efforts in history, with thousands of people adding code every year.')}
''', kw=['history', 'Bell Labs', 'Ken Thompson', 'Dennis Ritchie', 'C language', 'BSD', 'POSIX', 'GNU', 'Richard Stallman', 'Linus Torvalds', 'GPL', 'Single UNIX Specification'])

K.lesson('layers', 'Kernel, shell and tools: the layers of Linux', f'''
<p>Linux is built in layers, and each layer only talks to the one below it.</p>
{table(['Layer', 'What it is', 'Examples'], [
    ['Hardware', 'The real parts', 'CPU, memory, disk, network card'],
    ['<b>Kernel</b>', 'The core program that controls the hardware. It starts first, never stops, and is the only part allowed to touch devices directly', 'The Linux kernel, with its drivers'],
    ['System libraries', 'Ready made functions programs call to ask the kernel for help', 'glibc, the GNU C library, or musl on Alpine'],
    ['<b>Shell</b> and tools', 'The programs you type commands into, and the small commands themselves', 'bash, zsh, ls, cp, grep from GNU coreutils and friends'],
    ['Applications', 'Everything else', 'Browsers, databases, web servers, games']])}
<p>The kernel runs in a protected mode of the processor called <b>kernel space</b>. Your programs run in <b>user space</b>. A user program that wants to read a file cannot read the disk itself. It asks the kernel with a <b>system call</b>, and the kernel checks that you are allowed, does the work and hands back the result. This is why one broken program cannot crash the whole computer.</p>
{play('lx-layers')}
{run('Ask the machine that built this page about itself', '''uname -s
uname -r
head -3 /etc/os-release''', note='uname -s prints the kernel name and uname -r its version. /etc/os-release names the distribution, the layer of tools around the kernel. The page was built inside an Ubuntu container, and the kernel belongs to the computer hosting it.')}
{deep('Why a kernel version looks like 6.8.0', '<p>Linux versions are written major.minor.patch, for example 6.8.0. Since Linux 3.0 in 2011 the first number has no special meaning: Linus moves it up when the second number grows large. A new minor version comes out about every nine or ten weeks. Distributions add their own suffix, so Ubuntu shows something like 6.8.0-45-generic.</p>')}
{talk('Think about ordering food in a restaurant. You do not walk into the kitchen and use the stove yourself. You tell the waiter, the waiter tells the kitchen, and the food comes back to your table. Linux works in the same safe way. A program never touches the disk or the network card directly. It asks the kernel through a system call, and the kernel checks the request first. This idea, called protected mode, arrived in ordinary personal computers with the Intel 80386 processor in 1985, and Linus Torvalds wrote the first Linux kernel for exactly that processor. Because of these layers, a program that crashes only hurts itself, and the rest of the system keeps working. When you learn the commands in this subject, remember that every one of them is just a small program in user space, asking the kernel for help.')}
''', kw=['kernel', 'user space', 'kernel space', 'system call', 'glibc', 'shell', 'coreutils', 'uname', 'os-release', 'kernel version'])

K.lesson('distros', 'Distributions: many flavours, one kernel', f'''
<p>Nobody installs only a kernel. A <b>distribution</b> (distro) is a complete package: the Linux kernel, the GNU tools, a package manager to install software, a desktop if you want one, and a team that tests and updates it all. They all run the same commands you learn here, with small differences in how software is installed.</p>
{table(['Distribution', 'Family and package tool', 'Release style', 'Good for'], [
    ['Ubuntu', 'Debian family, apt and .deb files', 'A new version every six months, a Long Term Support (LTS) version every two years with five years of standard support', 'Beginners, cloud servers, desktops'],
    ['Debian', 'apt and .deb', 'Stable releases about every two years', 'Servers that must never surprise you'],
    ['Fedora', 'Red Hat family, dnf and .rpm files', 'About every six months, new software early', 'Developers who want the latest tools'],
    ['Red Hat Enterprise Linux (RHEL), Rocky, AlmaLinux', 'dnf and .rpm', 'Major versions supported for ten years', 'Companies, banks, government'],
    ['Arch Linux', 'pacman', 'Rolling: always updating, no big versions', 'People who want to build and understand every piece'],
    ['Alpine Linux', 'apk, musl C library', 'Small fixed releases', 'Containers, because a base image is only a few megabytes']])}
{play('lx-distro')}
{note('An Ubuntu version number is the year and month of its release. 24.04 means April 2024. LTS versions come out in April of even years: 20.04, 22.04, 24.04.', 'tip')}
{note('Learn the commands, not the distribution. ls, grep and chmod work the same everywhere. Only the package tool (apt, dnf, pacman, apk) changes between families.', 'tip')}
{talk('When Linux was young, installing it meant downloading the kernel and dozens of tools separately and putting them together by hand, which only experts could do. In 1993 two of the oldest distributions still alive today appeared. Slackware came first in July, and Debian followed in August, started by a student called Ian Murdock. A distribution does all the putting together for you. In 2004 a company called Canonical released Ubuntu, based on Debian, with the goal of making Linux easy for everyone, and it became very popular. Today there are hundreds of distributions, but most belong to a few families. If you use Ubuntu at home and your company uses Red Hat Enterprise Linux, nearly everything you type is the same. Only the way you install software changes, apt on one and dnf on the other.')}
''', kw=['distribution', 'distro', 'Ubuntu', 'Debian', 'Fedora', 'RHEL', 'Arch', 'Alpine', 'LTS', 'rolling release', 'apt', 'dnf', 'pacman', 'apk'])

K.lesson('practice', 'Where you can practise, and your first commands', f'''
<p>You do not need a new computer to learn Linux. Pick any of these.</p>
{table(['You have', 'How to get a Linux shell'], [
    ['Windows 10 or 11', 'Open PowerShell as administrator and run <code>wsl --install</code>. It installs the Windows Subsystem for Linux with Ubuntu. After a restart, open Ubuntu from the Start menu.'],
    ['macOS', 'Open the Terminal app. macOS is a certified UNIX and its default shell has been zsh since macOS Catalina (10.15). Most commands here work, but macOS uses BSD versions of tools, so a few options differ from GNU Linux.'],
    ['Any computer', 'Install VirtualBox or another virtual machine app and run Ubuntu inside it. Nothing on your real system changes.'],
    ['A browser only', 'The practice shell on every page of this subject. It is a pretend Linux inside the page, made for learning, so it is safe to try anything.'],
    ['A Raspberry Pi or an old laptop', 'Install Raspberry Pi OS or Ubuntu on it and learn on real hardware.']])}
{run('Your first five commands, run for real', '''whoami
pwd
ls
date -u -d '2026-11-23 09:30'
echo "Hello, Linux"''', note='whoami prints your user name, pwd the folder you are in, ls the files in it. date prints a date (here a fixed one, so the page always shows the same text). echo prints whatever you give it.')}
{lab('Your first visit', [
    ('Find out who you are logged in as.', 'whoami', [{'cmd': r'^\s*whoami'}, {'out': 'learner'}]),
    ('Print the folder you are standing in.', 'pwd', [{'cmd': r'^\s*pwd'}, {'out': '^/home/learner$'}]),
    ('List the files in this folder.', 'ls', [{'cmd': r'^\s*ls\b'}, {'out': 'notes.txt'}]),
    ('Ask the kernel its name and version with all details.', 'uname -a', [{'cmd': r'uname\s+-a'}]),
    ('Read the file that names the distribution: <code>/etc/os-release</code>.', 'cat /etc/os-release', [{'cmd': r'cat\s+/etc/os-release'}, {'out': 'Practice Linux'}]),
    ('Make the computer greet you with echo.', 'echo "Hello, Linux"', [{'cmd': r'^\s*echo\s+\S'}])])}
{note('Commands are case sensitive. <code>ls</code> works, <code>LS</code> gives "command not found". File names are case sensitive too: notes.txt and Notes.txt are two different files.', 'warn')}
{talk('There is a famous saying among people who learn Linux. You do not learn it by reading, you learn it by typing. When the Windows Subsystem for Linux arrived in 2016, millions of Windows users suddenly had a real Linux shell one command away, and it became one of the most common ways students start. Many cloud companies also give a free small Linux server for learning. On this page you have the practice shell, a pretend Linux computer that lives inside the page. It has a user called learner, a home folder with a few files, and a list of missions. Try the missions now. Nothing you type there can harm your real computer, so be curious. Type a command, read what comes back, and if something looks strange, that is exactly the moment you learn the most.')}
''', kw=['WSL', 'wsl --install', 'macOS Terminal', 'zsh', 'virtual machine', 'whoami', 'pwd', 'ls', 'date', 'echo', 'case sensitive'])

K.lesson('levels', 'The Unix way of thinking, from school to research', f'''
<p>Unix came with a way of building software that people still follow. Doug McIlroy, who invented Unix pipes, summed it up like this (as quoted by Peter Salus in 1994): <b>write programs that do one thing and do it well, write programs to work together, and write programs to handle text streams, because that is a universal interface.</b></p>
{table(['Unix idea', 'What it means', 'Where you will see it'], [
    ['Small tools', 'Each command does one job, for example sort only sorts', 'ls, sort, wc, grep'],
    ['Pipes join tools', 'The output of one command becomes the input of the next', '<code>sort fruits.txt | uniq -c</code>'],
    ['Text everywhere', 'Settings, logs and data are plain text you can read and edit', '/etc/passwd, /var/log, CSV files'],
    ['Everything is a file', 'Devices, processes and even kernel settings appear as files', '/dev/null, /proc/cpuinfo'],
    ['Silence is golden', 'A command that works prints nothing extra', 'cp and mkdir print nothing when they succeed']])}
{ladder(
    '<p>Linux is the boss program inside a computer. It shares the computer between all the apps, keeps everyone’s files safe, and lets you give orders by typing short words like ls (show my files) into a black window called a terminal.</p>',
    '<p>Linux is a free, open source, Unix-like operating system kernel. Together with GNU tools and a package manager it forms a distribution. Users work through a shell, which runs small single purpose programs that can be combined with pipes, following the Unix philosophy and the POSIX standard.</p>',
    '<p>Linux is a monolithic kernel with loadable modules. Processes in user space reach kernel services through system calls, with memory protection by virtual memory and privilege rings. Its interfaces follow POSIX and the Single UNIX Specification closely, so software is portable across Unix-like systems. Distributions differ in libc (glibc, musl), init system, packaging and release model.</p>',
    '<p>Open problems include safer kernel code (the Rust for Linux effort, merged as experimental in Linux 6.1 in December 2022), real time behaviour (PREEMPT_RT was merged into the main kernel in Linux 6.12 in 2024), eBPF programs that run safely inside the kernel, scaling to thousands of cores, and studies of the kernel development process itself, one of the largest collaborations in software.</p>')}
{scene('a website you used today', '<p>When you watched a video or searched the web today, your request almost certainly landed on Linux servers. Most of them have no screen at all. Engineers manage them only through a shell over the network, using exactly the commands this subject teaches.</p>')}
{talk('In 1978 the Bell System Technical Journal printed a special issue about Unix, and in it Doug McIlroy wrote down rules for building programs the Unix way. The best known summary is very short: do one thing well, work together, and use text. These rules explain why Linux feels the way it does. Instead of one giant program that does everything, you get hundreds of small commands, and you join them like building blocks. For example, one command lists files, a second one counts lines, and together they count your files. This idea has lasted more than fifty years and still shapes modern software, from small command line tools to the way big cloud systems are split into small services. As you go through this subject, notice how often a hard job becomes easy when you join two or three small tools.')}
''', kw=['Unix philosophy', 'Doug McIlroy', 'do one thing well', 'pipes', 'everything is a file', 'text streams', 'Rust for Linux', 'eBPF', 'PREEMPT_RT'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is the main job of an operating system?', ['Drawing pictures', 'Managing the hardware and sharing it between programs and users', 'Browsing the web', 'Writing programs for you'], 1, 'It is the manager of the computer.', 'It shares the CPU, memory, disk and devices, and keeps users and programs apart.')
K.quiz('e', 'Who started writing Linux, and in which year?', ['Ken Thompson in 1969', 'Linus Torvalds in 1991', 'Richard Stallman in 1983', 'Dennis Ritchie in 1973'], 1, 'A student in Helsinki.', 'Linus Torvalds announced his hobby kernel on 25 August 1991.')
K.quiz('e', 'Where was Unix created?', ['Microsoft', 'Bell Labs at AT&T', 'Apple', 'The University of Helsinki'], 1, 'A phone company research lab.', 'Ken Thompson and Dennis Ritchie created Unix at Bell Labs in 1969.')
K.quiz('e', 'Which of these uses the Linux kernel?', ['Android', 'iOS', 'Windows 11', 'MS-DOS'], 0, 'Phones.', 'Android is built on the Linux kernel. iOS is built on Apple\'s own Darwin system.')
K.quiz('m', 'Why was rewriting Unix in C in 1973 so important?', ['C is faster than machine code', 'The system could be moved to other computers by recompiling it', 'C was the only language', 'It made Unix free'], 1, 'Portability.', 'Written in a high level language, Unix could be ported instead of rewritten for every machine.')
K.quiz('m', 'What is a Linux distribution?', ['Another name for the kernel', 'The kernel plus tools, a package manager and updates, tested together', 'A paid version of Linux', 'A kind of virus'], 1, 'A complete package.', 'Ubuntu, Fedora and Debian all ship the Linux kernel with GNU tools, package managers and their own choices.')
K.quiz('m', 'A program wants to read a file. How does it get the data?', ['It reads the disk directly', 'It makes a system call and the kernel reads the disk', 'It asks the shell', 'It asks the BIOS'], 1, 'Only one layer may touch the hardware.', 'Programs in user space ask the kernel through system calls such as read.')
K.quiz('m', 'Which standard describes the shell and commands common to Unix-like systems?', ['ISO 9001', 'POSIX (IEEE 1003.1)', 'HTML5', 'TCP/IP'], 1, 'IEEE published it in 1988.', 'POSIX lets the same scripts and C programs work across Linux, BSD and macOS.')
K.quiz('m', 'You typed LS and got "command not found". Why?', ['ls is not installed', 'Linux commands are case sensitive', 'You need sudo', 'The terminal is broken'], 1, 'Capital letters matter.', 'The command is ls in lower case. LS is a different name that does not exist.')
K.quiz('h', 'What does Ubuntu 22.04 tell you?', ['Version 22, patch 4', 'Released in April 2022, and it is an LTS because it came in April of an even year', 'Released on 22 April', 'The 22nd build of version 4'], 1, 'Year and month.', 'Ubuntu numbers are YY.MM. LTS releases come every April of an even year.')
K.quiz('h', 'Which name may only be used by systems certified by The Open Group?', ['Linux', 'UNIX', 'POSIX', 'GNU'], 1, 'A trademark.', 'UNIX is a trademark. Certified systems such as macOS may use it. Linux is Unix-like.')
K.quiz('h', 'A shell script uses only POSIX features. Where will it most likely run unchanged?', ['Only on Ubuntu', 'On Linux, macOS and the BSDs', 'Only on Windows', 'Only on the computer that wrote it'], 1, 'That is the point of a standard.', 'POSIX scripts are portable across Unix-like systems.')
K.quiz('x', 'Which statement about Linux and GNU is accurate?', ['Linux contains Bell Labs Unix code', 'The Linux kernel plus GNU tools make a complete free system, which is why some call it GNU/Linux', 'GNU is a Linux distribution', 'GNU was started after Linux'], 1, 'Dates: GNU 1983, Linux 1991.', 'GNU provided the compiler, shell and tools, and Linux provided the missing kernel.')
K.quiz('x', 'Since Linux 3.0, what does a jump in the first version number (for example 5.19 to 6.0) mean?', ['A complete rewrite', 'Nothing special, the minor number had grown large', 'A new license', 'That old programs stop working'], 1, 'Linus said the numbers are just numbers.', 'Linux does not break user space between versions. The major number moves when the minor number gets big.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Unix was started in 1969 and Linux in 1991. How many years apart is that?', '22', 'Subtract the years.',
       ['Linux year: 1991.', 'Unix year: 1969.', eq('1991 − 1969 = 22 years')], check=1991 - 1969)
K.calc('e', 'Ubuntu ships an LTS every two years. 24.04 is an LTS. Which year does the next LTS come out? Give the year, for example 2030.', '2026', 'Add two years.',
       ['The LTS of 24.04 came out in 2024.', 'The next one is two years later.', eq('2024 + 2 = 2026, called 26.04')], check=2026)
K.calc('e', 'Ubuntu 24.04 LTS has five years of standard support from April 2024. In which year does it end? ', '2029', 'Add five years.',
       ['Release: April 2024.', 'Support: five years.', eq('2024 + 5 = 2029')], check=2029)
K.calc('m', 'Unix time counts seconds from 1 January 1970 00:00 UTC. How many seconds are in one day?', '86400', 'Hours times minutes times seconds.',
       ['One day has 24 hours.', 'One hour has 60 minutes of 60 seconds each: 3,600 seconds.', eq('24 × 3,600 = 86,400 seconds')], check=24 * 3600)
K.calc('m', 'Old systems stored Unix time in a signed 32 bit number. The biggest value is 2³¹ − 1. What is that number?', '2147483647', '2 to the power 31 is 2,147,483,648.',
       ['A signed 32 bit number keeps one bit for the sign, so 31 bits hold the value.', '2³¹ = 2,147,483,648.', eq('2³¹ − 1 = 2,147,483,647 seconds')], check=2 ** 31 - 1)
K.calc('h', 'How many whole days after 1 January 1970 does a signed 32 bit time run out? Divide 2,147,483,647 seconds by 86,400 and drop the fraction.', '24855', 'Whole days only.',
       ['Seconds available: 2,147,483,647.', 'Seconds per day: 86,400.', eq('2,147,483,647 ÷ 86,400 = 24,855.13'), 'So the counter runs out 24,855 days later, on 19 January 2038 at 03:14:07 UTC. This is the Year 2038 problem. Modern Linux uses 64 bit time.'], check=2147483647 // 86400)
K.calc('h', 'A new Linux minor version comes out about every 9 weeks. About how many releases is that per year? Round down.', '5', '52 weeks in a year.',
       ['A year has 52 weeks.', 'One release every 9 weeks.', eq('52 ÷ 9 = 5.8, so about 5 full release cycles a year')], check=52 // 9)

# ---------------------------------------------------------------- summary
K.must('Operating system', 'The manager of the computer: it shares the CPU, memory, disk and devices between programs and users.')
K.must('Unix and Linux', 'Unix: Bell Labs, 1969, rewritten in C in 1973. Linux: a free Unix-like kernel by Linus Torvalds, 1991, licensed under the GPL.')
K.must('Layers', 'Hardware, kernel (kernel space), libraries, shell and tools, apps (user space). Programs ask the kernel for help with system calls.')
K.must('Distributions', 'Kernel plus GNU tools plus a package manager. Debian family uses apt, Red Hat family uses dnf. Commands are the same everywhere.')
K.must('Standards and names', 'POSIX (IEEE 1003.1) keeps Unix-like systems compatible. UNIX is a trademark for certified systems such as macOS.')
K.must('Case matters', 'Commands and file names are case sensitive: ls is not LS, notes.txt is not Notes.txt.')

T = K.topic(
    slug='what-is-linux', topic='what-is-linux',
    step=(1, 'Meet Unix and Linux', 'lx-basics-1', 'What an operating system is, where Unix and Linux came from, the terminal and the shell, and how to ask the system for help.', 'Beginner'),
    title='Meet Unix and Linux', short='Meet Unix and Linux', badge='1.1', minutes=35, added='2026-11-23',
    lead='Find out what an operating system does, how Unix was born at Bell Labs and Linux in a student\'s bedroom, how the kernel, shell and tools fit together, and where you can start typing commands today.',
    desc='What an operating system is, the history of Unix, GNU and Linux, POSIX and the UNIX trademark, kernel space and user space, system calls, distributions and package families, WSL and other ways to practise, and the Unix philosophy.',
    summary='Operating systems, the story of Unix and Linux, kernel and user space, distributions, where to practise, first commands and the Unix philosophy.',
    keywords=['what is linux', 'unix', 'operating system', 'kernel', 'distribution', 'ubuntu', 'posix', 'gnu', 'linus torvalds', 'wsl', 'unix philosophy'],
    recap='<p>Linux is a free Unix-like kernel. With GNU tools and a package manager it becomes a distribution. Programs live in user space and ask the kernel for help with system calls. The same commands work on every distribution.</p>')
