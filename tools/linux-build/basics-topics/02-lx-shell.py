# Foundations 1.2: terminal, console and shell, the prompt, the shape of a command, builtins and PATH, history,
# completion and keyboard shortcuts. Sources: bash(1) manual (GNU Bash 5.2), type and history builtins, readline(3)
# default key bindings, POSIX Shell Command Language, Apple support note on zsh as default shell (macOS 10.15).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('terminal', 'Terminal, console and shell are three different things', f'''
<p>People mix these words up, so let us fix them first.</p>
{table(['Word', 'What it really is', 'Examples'], [
    ['<b>Terminal</b> (terminal emulator)', 'The window that shows text and sends your key presses. It does not understand commands at all.', 'GNOME Terminal, Konsole, macOS Terminal, Windows Terminal, iTerm2'],
    ['<b>Shell</b>', 'The program inside the terminal that reads your command, understands it and starts other programs.', 'bash, zsh, sh (dash on Ubuntu), fish'],
    ['<b>Console</b>', 'The screen and keyboard plugged straight into the machine, or the text screens you reach with Ctrl Alt F3 on many Linux desktops.', 'A server room monitor, a virtual console tty3'],
    ['<b>Command line</b> (CLI)', 'The general idea of working by typing text commands, instead of clicking.', 'Everything in this subject']])}
<p>The name terminal comes from history. In the 1970s a terminal was a real machine with a keyboard and a printer or screen, wired to a big shared computer. The <b>tty</b> you still see in Linux comes from teletypewriter, the printing machines used as the first Unix terminals.</p>
{note('bash (the Bourne Again SHell) is the default shell on most Linux distributions. macOS switched its default to zsh with macOS Catalina in 2019. The commands in this subject work in both, and scripts are written for bash.', 'tip')}
{talk('In the 1970s, using Unix meant sitting at a teletype, a noisy machine like an electric typewriter joined to the computer by a cable. You typed a command, and the answer was printed on a roll of paper. Ken Thompson and Dennis Ritchie wrote early Unix on exactly such machines, which is why commands are so short. Typing ls instead of list saved time and paper. Later the paper became a glass screen, and today the screen is a window on your desktop, but Linux still calls these devices tty, short for teletypewriter. The shell is a separate program that runs inside that window. The first Unix shell was written by Ken Thompson, then Stephen Bourne wrote the Bourne shell in 1979, and in 1989 Brian Fox wrote bash for the GNU project. The name means Bourne Again Shell, a little joke about the older shell it replaced.')}
''', kw=['terminal', 'terminal emulator', 'shell', 'console', 'tty', 'bash', 'zsh', 'dash', 'CLI'])

K.lesson('prompt', 'Reading the prompt', f'''
<p>When the shell is ready for you, it prints a <b>prompt</b> and waits. A typical bash prompt on Ubuntu looks like this:</p>
{table(['Part', 'Example', 'Meaning'], [
    ['User name', '<code>learner</code>', 'Who you are logged in as'],
    ['@ and host name', '<code>@brainy</code>', 'The name of the computer, useful when you are logged in to several'],
    ['Colon and folder', '<code>:~/logs</code>', 'The folder you are in. ~ is short for your home folder'],
    ['Last sign', '<code>$</code> or <code>#</code>', '$ for an ordinary user, # for root, the all powerful administrator']])}
<p>So <code>learner@brainy:~/logs$</code> means: user learner, on computer brainy, in the folder logs inside the home folder, as an ordinary user. The prompt text comes from a shell variable called <code>PS1</code>, so it can be changed. In PS1, <code>\\u</code> is the user, <code>\\h</code> the host, <code>\\w</code> the folder and <code>\\$</code> prints # for root and $ for everyone else.</p>
{run('Find the facts the prompt shows', '''whoami
hostname
pwd
echo "$HOME"''', note='The host name here is the name of the machine that built this page.')}
{note('Seeing # instead of $ means you are root. Every command you type can change or delete anything on the system. Slow down, and leave root as soon as you have finished.', 'warn')}
{note('When you copy commands from a web page, do not copy the $ or # at the start. They are the prompt, not part of the command.', 'tip')}
{talk('The prompt is the shell saying I am ready, your turn. Engineers who manage many servers rely on it every day. Imagine a person logged in to a test server and a live shop server in two windows at the same time. The only visible difference is the host name in the prompt, and a command meant for the test machine typed into the wrong window can take a real shop offline. Many companies colour the prompt red on production machines for exactly this reason. The last character matters too. A dollar sign means an ordinary user, and a hash sign means root, the administrator who can do anything. Get into the habit of glancing at the prompt before you press Enter, especially before commands that delete or change things. It takes half a second and has saved many careers.')}
''', kw=['prompt', 'PS1', 'root', '$ and #', 'hostname', 'whoami', 'home folder', 'tilde'])

K.lesson('anatomy', 'The shape of every command', f'''
<p>Almost every command line has the same shape:</p>
{fxs(fx('Command line', '<code>command  -options  arguments</code>', 'The command is the program to run. Options (flags) change its behaviour and start with - or --. Arguments say what to work on, often file names. Words are separated by spaces.', key=True),
     fx('Short and long options', '<code>ls -l -a</code> = <code>ls -la</code> = <code>ls -l --all</code>', 'Short options are one letter after one dash and can be joined. Long options are whole words after two dashes and cannot be joined.'),
     fx('An option with a value', '<code>head -n 3 notes.txt</code> = <code>head -n3</code> = <code>head --lines=3</code>', 'Some options need a value right after them.'))}
{play('lx-cmdparts')}
{run('One command, three spellings of the same options', '''ls -l -a logs
ls -la logs
ls --all -l logs''')}
<p>Spaces matter. <code>ls -la</code> is one option word, but <code>ls - la</code> passes the strange arguments - and la. If a file name contains a space, put it in quotes: <code>cat "my notes.txt"</code>, otherwise the shell sees two files called my and notes.txt.</p>
{run('Quotes keep a name with a space together', '''echo "shopping list" > "my notes.txt"
cat "my notes.txt"
cat my notes.txt''')}
{talk('Every command you will ever type follows one simple pattern. First the name of the program, then options that change how it behaves, then the things it should work on. In 1971, the first Unix manual already described commands this way. Options with one dash and one letter come from those early days, when every keystroke was precious. Long options with two dashes, such as dash dash all, were added later by the GNU project because they are easier to read and remember. You can usually use either. One mistake trips up nearly every beginner: file names with spaces. The shell splits a line at spaces, so a file called my notes becomes two separate words. Put such a name in quotes, or better, avoid spaces in file names altogether and use a dash or an underscore instead.')}
''', kw=['command syntax', 'options', 'flags', 'arguments', 'short options', 'long options', 'quotes', 'spaces in names'])

K.lesson('findcmd', 'Where commands come from: builtins, PATH and type', f'''
<p>When you type a command, the shell looks for it in this order: an <b>alias</b> you defined, a shell <b>function</b>, a <b>builtin</b> (a command built into the shell itself, such as cd and echo), and finally a program file in one of the folders listed in the <code>PATH</code> variable, searched from left to right.</p>
{run('Ask the shell what a name means', '''type cd
type ls
type -a echo
echo "$PATH"
which ls''', note='cd has to be a builtin: a separate program could only change its own folder, not the shell\'s. echo exists both as a builtin and as a program, and the builtin wins.')}
{cmdtable([
    ('type NAME', 'Says whether NAME is an alias, function, builtin or a file, and where', 'type ls'),
    ('type -a NAME', 'Lists every match, in the order the shell would try them', 'type -a echo'),
    ('which NAME', 'Prints the path of the program file found in PATH', 'which python3'),
    ('echo $PATH', 'Shows the folders searched for programs, separated by colons', 'echo $PATH'),
    ('command -v NAME', 'POSIX way to test if a command exists, useful in scripts', 'command -v git')])}
{note('If you get "command not found", either the program is not installed, the name is misspelled, or its folder is not in PATH. To run a program in the current folder you must write ./name, because the current folder is not in PATH on purpose.', 'warn')}
{deep('Why the current folder is not in PATH', '<p>If . were in PATH, someone could leave a file called ls in a shared folder like /tmp. The next person to type ls there would run that file instead of the real ls, with their own rights. Leaving . out of PATH and typing ./script makes it explicit that you are running something from here.</p>')}
{talk('Here is a question that surprises people. Where does the command ls actually live? It is not magic inside the terminal. It is an ordinary program file, usually stored in the folder slash usr slash bin, and the shell finds it by searching a list of folders kept in a variable called PATH. A few commands are different. cd, which changes your folder, must be built into the shell itself, because a separate program can only change its own folder, and the change would vanish the moment it finished. The type command tells you which kind each name is. Security people care about PATH too. In the 1980s, a classic trick on shared Unix machines was to leave a fake program in a public folder, hoping someone with more rights would run it by accident. That is why the current folder is deliberately left out of PATH today.')}
''', kw=['builtin', 'PATH', 'type', 'which', 'command -v', 'command not found', 'alias', 'function', './'])

K.lesson('keys', 'History, Tab completion and shortcuts that save hours', f'''
<p>Experienced users rarely type a whole command. They let the shell do the work.</p>
{table(['Keys', 'What they do'], [
    ['<b>Tab</b>', 'Completes a command or file name. Press it twice to list every choice when there is more than one.'],
    ['<b>Up</b> and <b>Down</b>', 'Walk back and forward through commands you typed before'],
    ['<b>Ctrl R</b>', 'Search your history: type a few letters of an old command, press Ctrl R again for older matches, Enter to run it'],
    ['<b>Ctrl C</b>', 'Stop the program that is running now (sends the interrupt signal)'],
    ['<b>Ctrl D</b>', 'End of input. At an empty prompt it closes the shell'],
    ['<b>Ctrl L</b>', 'Clear the screen, the same as the clear command'],
    ['<b>Ctrl A</b> and <b>Ctrl E</b>', 'Jump to the start or the end of the line'],
    ['<b>Ctrl U</b> and <b>Ctrl K</b>', 'Cut from the cursor to the start, or to the end, of the line'],
    ['<b>Ctrl W</b>', 'Delete the word before the cursor'],
    ['<b>!!</b>', 'The whole previous command, for example <code>sudo !!</code> to repeat it as root'],
    ['<b>!$</b>', 'The last word of the previous command, often a file name']])}
{run('The history list', '''# history is on by itself in an interactive shell. This box runs as a script, so it switches it on first
set -o history
echo first
echo second
history | tail -n 3''', note='history numbers every command. !N runs number N again. In an interactive bash the list is saved to ~/.bash_history when the shell exits.')}
{lab('Drive the shell like a pro', [
    ('Print the list of commands this shell knows with <code>help</code>.', 'help', [{'cmd': r'^\s*help\b'}]),
    ('Ask what kind of command <code>cd</code> is.', 'type cd', [{'cmd': r'^\s*type\s+cd'}, {'out': 'builtin'}]),
    ('Ask where the program <code>ls</code> lives.', 'which ls', [{'cmd': r'^\s*(which|type)\s+ls'}, {'out': '/usr/bin/ls'}]),
    ('Show the folders the shell searches for programs.', 'echo $PATH', [{'out': '/usr/bin'}]),
    ('List folder contents in long form using the joined options <code>-la</code>.', 'ls -la', [{'cmd': r'ls\s+-(la|al)\b'}]),
    ('Show the commands you typed so far.', 'history', [{'cmd': r'^\s*history'}, {'out': r'^\s+1\s'}]),
    ('Run the previous command again with <code>!!</code>.', '!!', [{'cmd': r'^\s*!!'}])])}
{note('Tab completion is not only for speed. If Tab does not complete a file name, the file is not where you think it is, so you catch the mistake before pressing Enter.', 'tip')}
{talk('Bash gets its comfortable editing keys from a library called GNU Readline, written by Brian Fox around 1989, the same person who wrote bash. Many of the shortcuts, like Control A to jump to the start of a line and Control E for the end, come from the Emacs text editor, which was popular with the GNU developers. Control C is even older. It sends an interrupt signal that tells the running program to stop, and it has worked that way on Unix since the 1970s. The history list is a real time saver. Engineers who fix servers at night often press Control R, type three letters, and find the long command they used last month. Learn Tab, the arrow keys, Control R and Control C today. Those four alone will make you twice as fast, and Tab will quietly stop you from typing the wrong file name.')}
''', kw=['tab completion', 'history', 'Ctrl R', 'Ctrl C', 'Ctrl D', 'Ctrl L', 'readline', '!!', '!$', 'keyboard shortcuts'])

K.lesson('levels', 'The shell from school to research', f'''
{ladder(
    '<p>The terminal is a window where you talk to the computer by typing. The shell is the listener inside it. You type a short order, press Enter, and the shell finds the right program, runs it, and shows you the answer.</p>',
    '<p>A shell is a command interpreter and a programming language. It reads a line, splits it into words, performs expansions, looks up the command (alias, function, builtin, PATH), creates a process to run external programs and waits for it, then reports the exit status in $?. bash follows POSIX sh and adds arrays, [[ ]], history and Readline editing.</p>',
    '<p>Under the hood an external command runs through fork() and execve(): the shell clones itself, and the child replaces its program with the one found in PATH, inheriting open file descriptors 0, 1 and 2 connected to the terminal device (a pseudo terminal, /dev/pts/N, managed by the terminal emulator). The kernel tty layer handles line editing in canonical mode and turns Ctrl C into SIGINT for the foreground process group.</p>',
    '<p>Research and engineering topics include shell language semantics and formal specifications of POSIX sh (the Smoosh project, 2020), static analysis of scripts (ShellCheck), safe parallel shell pipelines (PaSh, 2021), new structured shells such as Nushell and PowerShell that pass objects instead of text, and terminal protocols beyond the 1970s VT100 escape codes.</p>')}
{scene('a night shift fix', '<p>A website is slow at 2 am. The on call engineer logs in to a Linux server with SSH, presses Ctrl R to find the command that shows the busiest processes, sees one stuck program, stops it, and the site recovers. No mouse, no desktop, about one minute of typing. This is why the shell is still the main tool for servers.</p>')}
{talk('Why do professionals still type commands when we have beautiful graphical apps? The answer is control and speed. A graphical app shows only the buttons its designers chose. The shell lets you combine any program with any other, repeat a task for ten thousand files, and save your steps as a script that runs again tomorrow. It also works over a slow network connection to a server on another continent, where a graphical desktop would crawl. In 2019 Microsoft built the new Windows Terminal and added a real Linux kernel to Windows through WSL 2, because so many developers wanted a proper Unix shell. At the research end, people now study the shell language formally, build tools that check scripts for bugs before they run, and design new shells that pass structured data instead of plain text.')}
''', kw=['shell language', 'fork exec', 'pseudo terminal', 'pts', 'SIGINT', 'ShellCheck', 'Nushell', 'PowerShell'])

K.quiz('e', 'Which program actually understands the commands you type?', ['The terminal', 'The shell', 'The monitor', 'The keyboard driver'], 1, 'The terminal is only a window.', 'The shell (bash, zsh) reads and runs commands. The terminal just shows text.')
K.quiz('e', 'The prompt ends with #. What does that tell you?', ['You are in a comment', 'You are root', 'The command failed', 'You are offline'], 1, '$ is for ordinary users.', 'A # prompt means the root user, who can change anything.')
K.quiz('e', 'In ls -l notes.txt, what is -l?', ['The command', 'An option', 'An argument', 'A file'], 1, 'It starts with a dash.', 'Options change how a command works. notes.txt is the argument.')
K.quiz('e', 'Which key completes a file name for you?', ['Enter', 'Tab', 'Esc', 'Space'], 1, 'Try it twice for a list.', 'Tab completes names, and pressing it twice lists the choices.')
K.quiz('m', 'Why is cd built into the shell instead of being a separate program?', ['To make it faster', 'A separate program can only change its own folder, not the shell\'s', 'Because it is old', 'Because it needs root'], 1, 'Each process has its own current folder.', 'A child process cannot change its parent\'s working directory, so cd must run inside the shell.')
K.quiz('m', 'You type myscript in the folder that holds it and get "command not found". Why?', ['The file is empty', 'The current folder is not in PATH, so you must type ./myscript', 'Scripts cannot run on Linux', 'You need to reboot'], 1, 'Where does the shell look?', 'Only folders in PATH are searched. ./myscript names the file directly.')
K.quiz('m', 'What does cat my notes.txt try to do?', ['Open "my notes.txt"', 'Open two files: my and notes.txt', 'Create a file', 'Nothing'], 1, 'The shell splits at spaces.', 'Without quotes, the space separates two arguments.')
K.quiz('m', 'Which shortcut searches your command history?', ['Ctrl S', 'Ctrl R', 'Ctrl H', 'Ctrl F'], 1, 'R for reverse search.', 'Ctrl R starts reverse incremental search through history.')
K.quiz('m', 'Which of these are equal to ls -la?', ['ls -l -a', 'ls -l a', 'ls la', 'ls --la'], 0, 'Short options can be joined.', '-la is -l plus -a. ls -l a would list a file called a.')
K.quiz('h', 'type -a echo prints a builtin first and then /usr/bin/echo. Which one runs when you type echo?', ['/usr/bin/echo', 'The builtin', 'Both', 'A random one'], 1, 'The search order.', 'Aliases, functions and builtins come before PATH, so the builtin wins.')
K.quiz('h', 'You just ran cat /var/log/syslog and got Permission denied. Which line repeats it as root most quickly?', ['sudo !!', 'sudo $?', 'root !!', 'su !$'], 0, '!! is the previous command.', 'sudo !! expands to sudo cat /var/log/syslog.')
K.quiz('x', 'What happens inside the shell when you run an external command like ls?', ['The shell reads ls into itself', 'The shell forks a child, the child calls execve() to become ls, and the shell waits for it', 'The kernel types the command', 'The terminal runs ls'], 1, 'Two system calls.', 'fork() makes a copy of the shell, execve() replaces it with the ls program, wait() collects the exit status.')

K.calc('e', 'You need to type a 24 character command 15 times today. Using the Up arrow, each repeat costs 2 key presses (Up and Enter) instead of typing it again plus Enter. How many key presses do you save?', '322', 'Count presses both ways.',
       ['Typing it every time: 15 × (24 + 1) = 375 presses.', 'Type it once (25 presses), then 14 repeats at 2 presses each: 25 + 28 = 53.', eq('375 − 53 = 322 presses saved')], check=15 * 25 - (25 + 14 * 2))
K.calc('e', 'PATH is /usr/local/bin:/usr/bin:/bin. How many folders does the shell search?', '3', 'Count the parts between colons.',
       ['The colon separates folders.', 'Parts: /usr/local/bin, /usr/bin, /bin.', eq('3 folders')], check=3)
K.calc('m', 'PATH is /home/learner/bin:/usr/local/bin:/usr/bin:/bin. A program called tool exists in /usr/bin and in /home/learner/bin. Which position in PATH wins? Give the number, counting from 1.', '1', 'Left to right.',
       ['The shell stops at the first folder that has the program.', '/home/learner/bin is first in the list.', eq('position 1 wins')], check=1)
K.calc('m', 'ls -l -a -h -t uses four separate short options. Joined as one word, how many characters does the option word have, counting the dash?', '5', 'One dash plus four letters.',
       ['Joined form: -laht.', 'One dash and four letters.', eq('1 + 4 = 5 characters')], check=5)
K.calc('m', 'Your history holds 500 commands. HISTSIZE is changed to 1000 and you type 650 more. How many commands are in the list now?', '1000', 'The list keeps at most HISTSIZE entries.',
       ['500 + 650 = 1,150 commands typed.', 'HISTSIZE limits the list to 1,000.', eq('min(1,150, 1,000) = 1,000')], check=min(1150, 1000))
K.calc('h', 'A terminal shows 80 columns and 24 rows, the size of the classic VT100. How many characters fit on one screen?', '1920', 'Columns times rows.',
       ['80 characters per row.', '24 rows.', eq('80 × 24 = 1,920 characters')], check=80 * 24)

K.must('Terminal and shell', 'The terminal is the window. The shell (bash, zsh) reads commands and starts programs.')
K.must('Prompt', 'user@host:folder$. ~ is your home folder. # means root, so be careful.')
K.must('Command shape', 'command -options arguments. Short options join (-la), long options use -- (--all). Quote names with spaces.')
K.must('Finding commands', 'Order: alias, function, builtin, then PATH left to right. type and which tell you. Run local files with ./name.')
K.must('Keys', 'Tab completes, Up and Down walk history, Ctrl R searches it, Ctrl C stops a program, Ctrl L clears, !! repeats.')

T = K.topic(
    slug='terminal-and-shell', topic='terminal-and-shell',
    step=(1, 'Meet Unix and Linux', 'lx-basics-1', 'What an operating system is, where Unix and Linux came from, the terminal and the shell, and how to ask the system for help.', 'Beginner'),
    title='The terminal and the shell', short='Terminal and shell', badge='1.2', minutes=35, added='2026-11-23',
    lead='Tell the terminal, the shell and the console apart, read the prompt, learn the shape of every command, see how the shell finds programs, and use history, Tab and shortcuts like a professional.',
    desc='Terminal emulators, consoles and tty, bash and zsh, the prompt and PS1, root and the # prompt, command syntax with short and long options, quoting names with spaces, builtins, PATH, type and which, history, Tab completion and Readline shortcuts.',
    summary='Terminal versus shell, the prompt, command syntax, options and arguments, builtins and PATH, history and keyboard shortcuts.',
    keywords=['terminal', 'shell', 'bash', 'zsh', 'prompt', 'PS1', 'options', 'arguments', 'PATH', 'type', 'which', 'history', 'tab completion', 'ctrl r', 'ctrl c'],
    recap='<p>The terminal shows text, the shell runs commands. Every command is command, options, arguments. The shell finds programs in PATH. Tab, history and Ctrl R save typing.</p>')
