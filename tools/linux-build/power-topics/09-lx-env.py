# Power tools 4.2: the shell environment. Shell variables and environment variables, export, env, printenv,
# NAME=value cmd, readonly and declare, common variables, PATH and command lookup (alias, function, builtin, PATH,
# hash), aliases and small functions, startup files (/etc/profile, ~/.profile, ~/.bash_profile, ~/.bashrc,
# login and non-login shells, source), history and its expansions, PS1. Sources: bash(1) sections PARAMETERS,
# Shell Variables, COMMAND EXECUTION, INVOCATION, HISTORY, HISTORY EXPANSION, PROMPTING and ALIASES, the GNU Bash
# Reference Manual, environ(7), env(1) and printenv(1) from GNU coreutils, Ubuntu /etc/skel/.profile and .bashrc.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('vars', 'Shell variables and environment variables', f'''
<p>A <b>shell variable</b> is a name with a text value, kept inside one running bash. Write it with no spaces around the equals sign and read it with a dollar sign. An <b>environment variable</b> is a variable that is <b>exported</b>: bash copies it into every program it starts. Children get a copy, so they can never change the parent's value.</p>
{cmdtable([
    ('NAME=value', 'Set a shell variable (no spaces around =)', 'city=Pune'),
    ('echo "$NAME"', 'Read it (quote it to keep spaces)', 'echo "I live in $city"'),
    ('export NAME', 'Make it an environment variable', 'export city'),
    ('export NAME=value', 'Set and export in one step', 'export EDITOR=vim'),
    ('NAME=value CMD', 'Set a variable only for one command', 'LANG=C sort names.txt'),
    ('unset NAME', 'Remove a variable', 'unset city'),
    ('env, printenv NAME', 'Show the environment, or one variable', 'printenv HOME'),
    ('declare -p NAME', 'Show how a variable is defined (-x exported, -r read only)', 'declare -p PATH'),
    ('readonly NAME=value', 'A variable that cannot be changed', 'readonly MAX=10')])}
{run('Who can see a variable', """city=Pune
echo "parent: $city"
bash -c 'echo "child before export: [$city]"'
export city
bash -c 'echo "child after export: [$city]"'
bash -c 'city=Delhi'; echo "parent still: $city"
GREETING=hello bash -c 'echo "one command sees: $GREETING"'
echo "afterwards: [$GREETING]"
env | sort""", note='bash -c starts a child shell. It sees city only after export, and its own change to city is lost when it exits. The last command lists the whole environment this page was built with, which was kept small on purpose.')}
{table(['Variable', 'Holds'], [
    ['<code>HOME</code>', 'your home folder, where cd alone takes you'],
    ['<code>USER</code>, <code>LOGNAME</code>', 'your user name'],
    ['<code>PATH</code>', 'folders searched for commands, separated by colons'],
    ['<code>PWD</code>, <code>OLDPWD</code>', 'the current folder and the previous one (cd - uses it)'],
    ['<code>SHELL</code>', 'your login shell'],
    ['<code>LANG</code>', 'language and character set, for example en_IN.UTF-8'],
    ['<code>EDITOR</code>', 'the editor programs such as git and crontab open'],
    ['<code>PS1</code>', 'the look of the prompt'],
    ['<code>HISTSIZE</code>', 'how many commands history keeps in memory']])}
{note('city = Pune with spaces is not an assignment. bash runs a command called city with the arguments = and Pune, and prints city: command not found.', 'warn')}
{talk('Variables let the shell remember a value by name. You set one with a name, an equals sign and a value, with no spaces, and you read it back with a dollar sign in front of the name. Such a variable lives only inside the current shell. To pass it on to programs you start, you export it, which turns it into an environment variable. Every process has its own environment, and a child receives a copy of its parent’s exported variables when it starts. Because it is a copy, a child can never change a variable in its parent, which surprises many beginners who run a script to set something and find it gone afterwards. You can also put a variable in front of a single command, like LANG equals C sort, to change it just for that one run. Some variables are set for you at login: HOME, USER, PATH, SHELL and LANG are the most important.')}
''', kw=['variable', 'shell variable', 'environment variable', 'export', 'env', 'printenv', 'unset', 'declare', 'readonly', 'HOME', 'USER', 'LANG', 'EDITOR', 'environ'])

K.lesson('path', 'PATH: how bash finds commands', f'''
<p>When you type a command name with no slash in it, bash looks for it in this order: an <b>alias</b>, a <b>function</b>, a <b>builtin</b> command, and then each folder listed in <code>PATH</code>, from left to right. The first executable file with that name wins. A name with a slash, such as <code>./run.sh</code>, is used as a path and PATH is not searched.</p>
{play('lx-cmdpath')}
{run('Adding your own folder of tools', """echo "$PATH"
mkdir -p ~/bin
printf '#!/bin/bash\\necho "hello from my tool"\\n' > ~/bin/tool
chmod +x ~/bin/tool
tool
PATH="$HOME/bin:$PATH"
tool
type tool cd ls
command -v tool""", note='The first tool fails with status 127 because ~/bin is not in PATH yet. Putting the new folder first means your tools win over system ones with the same name. Write PATH="$PATH:$HOME/bin" to put it last instead.')}
{steps('Make a PATH change permanent', [
    'Open ~/.bashrc in an editor (or ~/.profile for every login).',
    'Add the line export PATH="$HOME/bin:$PATH" at the end.',
    'Run source ~/.bashrc, or open a new terminal, to load it.',
    'Check with echo "$PATH" and type yourcommand.'])}
{note('Never put . (the current folder) in PATH, and never write PATH=~/bin without $PATH. The first lets a file called ls in a shared folder run instead of the real ls. The second leaves you with no commands at all until you open a new terminal.', 'warn')}
{talk('PATH is a list of folders separated by colons. When you type a name like ls, bash first checks whether it is an alias, a function or a builtin, such as cd or echo. If not, it looks in the first folder of PATH, then the second, and so on, and runs the first executable file it finds. If none has it, you get command not found and exit status one hundred and twenty seven. That is why your own scripts need either a path, like dot slash run dot s h, or a folder that is listed in PATH. A common habit is a bin folder in your home, added to the front of PATH in your startup file. bash also remembers where it found each command, in a table you can see with the hash command, so it does not search every time.')}
''', kw=['PATH', 'command lookup', 'command not found', 'exit 127', '~/bin', 'which', 'type', 'command -v', 'hash', 'builtin', 'precedence'])

K.lesson('startup', 'Startup files, aliases and functions', f'''
<p>bash reads a few files when it starts, so your settings come back in every new terminal. Which files depend on the kind of shell. A <b>login shell</b> is the first shell after you log in, for example over ssh. An <b>interactive non-login shell</b> is a new terminal window or tab on a desktop.</p>
{table(['File', 'Read by', 'Put here'], [
    ['<code>/etc/profile</code>', 'login shells, for every user', 'system wide settings (the administrator edits it)'],
    ['<code>~/.bash_profile</code>, <code>~/.bash_login</code>, <code>~/.profile</code>', 'login shells, only the first of them that exists', 'environment variables such as PATH and EDITOR'],
    ['<code>~/.bashrc</code>', 'interactive non-login shells', 'aliases, functions, prompt, history settings'],
    ['<code>~/.bash_logout</code>', 'login shells when they exit', 'cleanup']])}
{note('On Ubuntu and Debian, ~/.profile itself runs ~/.bashrc, so putting your settings in ~/.bashrc covers both kinds of shell. Scripts run non-interactively and read none of these files.', 'tip')}
{cmdtable([
    ('alias NAME=\'TEXT\'', 'A short name for a longer command', "alias ll='ls -alF'"),
    ('alias', 'List all aliases', 'alias'),
    ('unalias NAME', 'Remove one', 'unalias ll'),
    ('\\ls or command ls', 'Run the real command, skipping an alias', 'command ls'),
    ('NAME() { ... }', 'A function: like an alias but takes arguments', 'mkcd() { mkdir -p "$1" && cd "$1"; }'),
    ('source FILE', 'Run a file in the current shell (same as . FILE)', 'source ~/.bashrc')])}
{run('Aliases and functions', """shopt -s expand_aliases
alias ll='ls -alF'
alias gs='git status'
alias
type ll
mkcd() { mkdir -p "$1" && cd "$1"; }
mkcd projects/demo
pwd
type mkcd | head -1""", note='Scripts do not expand aliases unless they run shopt -s expand_aliases, interactive shells have it on already. A function runs inside the current shell, so its cd changes this shell\u2019s folder. A script could not do that, because it runs as a child.')}
{talk('Every time bash starts, it reads startup files, so your aliases and settings come back. A login shell, the first one after you log in, reads slash etc slash profile and then the first of dot bash profile, dot bash login and dot profile that exists in your home. A new terminal window is usually an interactive non login shell, which reads dot bash r c. On Ubuntu, dot profile runs dot bash r c too, so dot bash r c is the place for most personal settings. After editing it, run source dot bash r c to load the changes into the shell you are using. An alias gives a short name to a longer command, such as l l for ls dash a l capital F. When you need arguments in the middle, write a small function instead. Functions run inside your current shell, so a function can even change folder, something a separate script can never do for you.')}
''', kw=['.bashrc', '.profile', '.bash_profile', '/etc/profile', 'login shell', 'non-login shell', 'source', 'alias', 'unalias', 'function', 'startup files'])

K.lesson('history', 'History and the prompt', f'''
<p>bash keeps a list of the commands you typed, saves it to <code>~/.bash_history</code> when the shell exits, and lets you search and reuse it. The prompt is drawn from the variable <code>PS1</code>.</p>
{cmdtable([
    ('history', 'List past commands with numbers', 'history | tail -20'),
    ('!!', 'Run the last command again', 'sudo !!'),
    ('!N', 'Run command number N', '!42'),
    ('!string', 'Run the last command that started with string', '!ssh'),
    ('!$', 'The last word of the previous command', 'mkdir reports && cd !$'),
    ('Ctrl+R', 'Search history as you type, press again for older matches', 'Ctrl+R then type ssh'),
    ('history -c', 'Clear the list in memory', 'history -c')])}
{table(['PS1 code', 'Shows'], [
    ['<code>\\u</code>', 'user name'], ['<code>\\h</code>', 'host name up to the first dot'],
    ['<code>\\w</code>', 'current folder, with ~ for home'], ['<code>\\W</code>', 'only the last part of the folder'],
    ['<code>\\$</code>', '# for root, $ for everyone else'], ['<code>\\t</code>', 'time as HH:MM:SS'],
    ['<code>\\n</code>', 'a new line']])}
{sample('Reusing history', """history | tail -3
!!
sudo !!
PS1='[\\t] \\u:\\W\\$ '""", ['  501  cd /var/log\n  502  ls -l syslog\n  503  tail -n 2 syslog', 'tail -n 2 syslog\ntail: cannot open \'syslog\' for reading: Permission denied', 'sudo tail -n 2 syslog\nNov 23 09:00:00 brainy systemd[1]: Started Daily apt download activities.\nNov 23 09:00:02 brainy CRON[812]: (root) CMD (run-parts /etc/cron.hourly)', '[09:45:12] learner:log$'], note='bash prints the expanded command before running it, so you always see what !! turned into. The new prompt shows the time, the user and the last part of the folder.')}
{lab('Shape your shell', [
    ('Create a shell variable <code>city</code> with the value <code>Pune</code>.', 'city=Pune', [{'env': ['city', 'Pune']}]),
    ('Export <code>city</code> so child programs can see it.', 'export city', [{'exported': 'city'}]),
    ('Prove it: start a child shell that prints <code>$city</code>.', "bash -c 'echo $city'", [{'cmd': r'bash\s+-c'}, {'out': '^Pune$'}]),
    ('Make a folder <code>~/bin</code> and add it to the front of PATH.', 'mkdir -p ~/bin && export PATH="$HOME/bin:$PATH"', [{'exists': 'bin', 'type': 'd'}, {'envre': ['PATH', '^/home/learner/bin:']}]),
    ('Create the alias <code>ll</code> for <code>ls -alF</code>.', "alias ll='ls -alF'", [{'alias': ['ll', 'ls -alF']}]),
    ('Ask bash what <code>cd</code> is.', 'type cd', [{'cmd': r'^type\s+cd'}, {'out': 'builtin'}]),
    ('Show your last three commands from history.', 'history | tail -n 3', [{'cmd': r'history'}, {'out': 'type cd'}])])}
{talk('bash remembers what you type. The history command lists it with numbers, and a few short forms save a lot of typing. Two exclamation marks repeat the last command, which is handy as sudo bang bang when you forgot sudo. Bang and a number repeats that line from history, and bang dollar is the last word of the previous command. The most useful trick of all is control R: start typing any part of an old command and bash finds it, and pressing control R again goes further back. The history is saved to dot bash history when the shell exits, and HISTSIZE sets how many lines are kept. Finally, the prompt itself is just a variable, PS1. Special codes such as backslash u for the user, backslash w for the folder and backslash t for the time let you design it, and many people add the git branch or colours.')}
''', kw=['history', '!!', '!$', '!N', 'Ctrl+R', 'reverse search', '.bash_history', 'HISTSIZE', 'PS1', 'prompt', 'sudo !!'])

K.lesson('levels', 'The environment from school to research', f'''
{ladder(
    '<p>Variables store values by name. export passes them to programs you start. PATH lists the folders where commands live, and ~/.bashrc keeps your settings for every new terminal.</p>',
    '<p>The environment is an array of NAME=value strings handed to a program by execve() and read with getenv(). Child processes get a copy, which is why scripts cannot change the caller and why source exists. Command lookup order is alias, function, builtin, then PATH, and the result is cached in a hash table that hash -r clears.</p>',
    '<p>Environment variables are a security boundary: sudo resets most of them (env_reset in sudoers) and setuid programs ignore LD_PRELOAD and LD_LIBRARY_PATH, which would otherwise let a user inject code. Services under systemd do not read shell startup files at all and get their environment from Environment= lines. The twelve factor app method stores configuration in environment variables so the same container image runs in testing and production.</p>',
    '<p>Shells keep evolving: zsh and fish add richer completion and history search, and tools such as direnv load project specific variables when you enter a folder. Shellshock (CVE-2014-6271) showed the danger of parsing environment values: bash ran code hidden after function definitions in variables, which web servers passed in from HTTP headers. Research on secret management (Vault, SOPS) moves passwords out of plain environment variables, which leak through /proc/PID/environ, crash reports and child processes.</p>')}
{scene('the missing tool after reboot', '<p>A developer installs a tool into ~/.local/bin and it works, but after logging in again the shell says command not found. <code>echo "$PATH"</code> shows the folder is missing. The developer had typed <code>export PATH=...</code> only in the terminal. Adding the same line to ~/.bashrc and running <code>source ~/.bashrc</code> makes it permanent, and <code>type tool</code> now prints the full path.</p>')}
{talk('Under the hood, the environment is a plain list of name equals value strings. When bash starts a program, it passes that list to the kernel along with the program and its arguments, and the program reads it with the getenv function. That is the whole mechanism, and it explains the rules: children get a copy, and nothing flows back. Because variables can change how programs behave, they also matter for security. sudo throws most of them away, and programs that run with extra privileges ignore variables that would let a user load their own code. In twenty fourteen a bug called Shellshock let attackers run commands on web servers simply by sending a crafted header that became an environment variable for bash. Today, cloud apps store their configuration in environment variables, while real secrets move into dedicated tools, because the environment of a process can leak in more places than people expect.')}
''', kw=['execve', 'getenv', 'environ', 'hash -r', 'LD_PRELOAD', 'env_reset', 'sudo environment', 'systemd Environment', 'twelve factor', 'Shellshock', 'CVE-2014-6271', 'direnv', 'secrets'])

K.quiz('e', 'Which line correctly sets a variable?', ['city = Pune', 'city=Pune', '$city=Pune', 'set city Pune'], 1, 'No spaces.', 'Spaces would make bash run a command called city.')
K.quiz('e', 'What does export do to a variable?', ['Deletes it', 'Copies it into the environment of programs started later', 'Saves it to disk', 'Makes it read only'], 1, 'Children see it.', 'Exported variables are passed to child processes.')
K.quiz('e', 'Which variable lists the folders searched for commands?', ['HOME', 'PATH', 'SHELL', 'PWD'], 1, 'Search path.', 'PATH holds colon separated folders.')
K.quiz('e', 'Which key combination searches your command history as you type?', ['Ctrl+H', 'Ctrl+R', 'Ctrl+S', 'Ctrl+F'], 1, 'R for reverse.', 'Ctrl+R starts reverse incremental search.')
K.quiz('m', 'A script runs cd /tmp. Why is your terminal still in the old folder afterwards?', ['cd is broken in scripts', 'The script ran in a child process with its own current folder', 'Scripts cannot use cd', '/tmp is read only'], 1, 'Child copy.', 'Use source script.sh to run it in the current shell.')
K.quiz('m', 'After PATH=~/bin (without $PATH) ls fails. Why?', ['ls was deleted', 'PATH now holds only ~/bin, so /usr/bin is not searched', 'ls needs sudo', 'The alias is wrong'], 1, 'Replaced, not added.', 'Always keep the old value: PATH="$HOME/bin:$PATH".')
K.quiz('m', 'You edited ~/.bashrc. How do you load the change into the current shell?', ['restart the computer', 'source ~/.bashrc', 'bash ~/.bashrc', 'export ~/.bashrc'], 1, 'Run it here.', 'source reads the file in the current shell.')
K.quiz('m', 'What does sudo !! do?', ['Deletes history', 'Runs the previous command again with sudo', 'Runs sudo twice', 'Shows sudo help'], 1, 'Bang bang.', '!! expands to the last command.')
K.quiz('m', 'What does LANG=C sort names.txt do?', ['Sets LANG for the rest of the session', 'Runs sort with LANG=C for this one command only', 'Fails', 'Sorts in reverse'], 1, 'Prefix assignment.', 'A NAME=value before a command applies only to it.')
K.quiz('h', 'Which file does an interactive non-login bash read?', ['~/.profile', '~/.bashrc', '/etc/profile', '~/.bash_logout'], 1, 'New terminal window.', 'bash(1) INVOCATION: interactive non-login shells read ~/.bashrc.')
K.quiz('h', 'In what order does bash look for a command name?', ['PATH, builtin, alias', 'alias, function, builtin, PATH', 'function, PATH, alias', 'builtin, PATH, function'], 1, 'Aliases expand first.', 'Aliases, then functions, builtins, then PATH.')
K.quiz('h', 'Why must cd be a builtin command?', ['It is faster', 'A separate program could only change its own folder, not the shell’s', 'For security', 'Because it has no options'], 1, 'Process boundaries.', 'Each process has its own current folder.')
K.quiz('x', 'Why does sudo reset most environment variables by default?', ['To save memory', 'So a user cannot change how root programs behave, for example with LD_PRELOAD', 'Because root has no environment', 'To speed up logins'], 1, 'Privilege boundary.', 'env_reset in sudoers removes variables that could inject code.')

K.calc('e', 'PATH=/home/learner/bin:/usr/local/bin:/usr/bin:/bin. How many folders are searched for a missing command?', '4', 'Count the parts between colons.', ['Split at each colon.', 'Four folder names.', eq('4')], check=4)
K.calc('e', 'tool exists in /usr/bin and in /home/learner/bin. With the PATH above, which position (1 to 4) wins?', '1', 'Left to right.', ['bash stops at the first match.', '/home/learner/bin is position 1.', eq('1')], check=1)
K.calc('m', 'HISTSIZE=1000 and you have typed 1250 commands in this shell. How many are listed by history?', '1000', 'Keeps the newest.', ['Only HISTSIZE lines stay in memory.', 'The oldest 250 are dropped.', eq('1000')], check=1000)
K.calc('m', 'A parent exports 3 variables and keeps 5 unexported. How many of those 8 does a child shell see?', '3', 'Only exported.', ['Exported: 3.', 'Unexported stay in the parent.', eq('3')], check=3)
K.calc('m', 'history shows command 40 to 49. You run !45 then history again. What number does the new entry get?', '50', 'Next number.', ['The last entry was 49.', 'The expanded !45 is saved as a new line.', eq('50')], check=50)
K.calc('h', 'A command is not found and PATH has 6 folders, each check taking 0.2 ms. How many ms does bash spend searching?', '1.2', 'Every folder is tried.', ['A miss checks all 6 folders.', '6 × 0.2 ms.', eq('1.2 ms')], check=1.2)

K.must('Variables', 'NAME=value with no spaces, read with "$NAME". export passes it to children, as a copy. NAME=value CMD sets it for one command.')
K.must('PATH', 'Colon separated folders, searched left to right after aliases, functions and builtins. Add with PATH="$HOME/bin:$PATH", never without $PATH.')
K.must('Startup', '~/.bashrc for aliases, functions and prompt. Login shells read ~/.profile. source ~/.bashrc applies edits now.')
K.must('Alias and function', "alias ll='ls -alF' for short names. A function takes arguments and runs in the current shell.")
K.must('History', 'history, !! and sudo !!, !N, !$, Ctrl+R to search. PS1 sets the prompt with codes for user, host, folder and time.')

T = K.topic(
    slug='environment', topic='environment',
    step=(4, 'Processes and the shell environment', 'lx-power-4', 'See and control running programs with ps, top, signals and job control, then shape your shell with variables, PATH, aliases and startup files.', 'Intermediate'),
    title='The shell environment: variables, PATH and startup files', short='Variables and PATH', badge='4.2', minutes=45, added='2026-11-23',
    lead='Set and export variables, understand what child processes can see, control where commands come from with PATH, keep your aliases and functions in ~/.bashrc, and reuse history like a professional.',
    desc='Shell variables and environment variables, export, env, printenv, NAME=value before a command, declare and readonly, common variables, PATH and the lookup order of alias, function, builtin and PATH, hash, aliases and functions, login and non-login startup files, source, history expansion with !! !N !$ and Ctrl+R, PS1, and how the environment works inside and why it matters for security.',
    summary='Variables and export, PATH lookup, .bashrc and .profile, aliases, functions, history and the prompt.',
    keywords=['environment variable', 'export', 'PATH', '.bashrc', '.profile', 'alias', 'source', 'history', 'PS1', 'env', 'printenv', 'login shell', 'Ctrl+R'],
    recap='<p>Variables live in one shell until exported, and children only ever get copies. PATH decides which program a name runs. ~/.bashrc brings your aliases, functions and prompt back in every terminal.</p>')
