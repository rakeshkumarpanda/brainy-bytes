# Shell scripting 1.1: your first scripts. What a script is, the shebang line, chmod +x, four ways to run a script
# (./script, bash script, source, PATH), comments, positional parameters $0 $1..$9 ${10} $# "$@" "$*", exit status,
# exit, $?, true and false, echo and printf, read, here documents, messages to stderr. Sources: bash(1) sections
# INVOCATION, Positional Parameters, Special Parameters, EXIT STATUS, SHELL BUILTIN COMMANDS (read, printf, exit,
# source), execve(2) for the #! line, the GNU Bash Reference Manual chapter 3.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('first', 'A script is a file of commands', f'''
<p>A <b>shell script</b> is a text file that holds commands you could type yourself. bash reads it from top to bottom and runs each line. Anything you repeat more than twice, such as a backup, a report or a setup, is a good first script.</p>
{steps('Write and run a script', [
    'Create the file with an editor, for example nano greet.sh.',
    'Make the first line the shebang: #!/bin/bash. It tells the kernel which program should read the file.',
    'Write the commands, one per line. Lines that start with # are comments and are ignored.',
    'Make it executable once: chmod +x greet.sh.',
    'Run it with its path: ./greet.sh. The ./ is needed because the current folder is not in PATH.'])}
{run('Your first script', """cat > greet.sh <<'EOF'
#!/bin/bash
# greet.sh: say hello to everyone named on the command line
echo "Script: $0, number of names: $#"
for name in "$@"; do
  echo "Hello, $name!"
done
EOF
chmod +x greet.sh
ls -l greet.sh
./greet.sh Asha "Ravi Kumar"
bash greet.sh Meera
greet.sh""", note='The here document (cat with EOF) writes the script in one go. chmod +x added the x bits. Typing greet.sh alone fails with status 127, because bash looks for commands only in the PATH folders.')}
{table(['How you run it', 'Needs x bit?', 'Runs in', 'Typical use'], [
    ['<code>./greet.sh</code>', 'yes', 'a new bash process (from the shebang)', 'the normal way'],
    ['<code>bash greet.sh</code>', 'no', 'a new bash process', 'testing, or when you cannot chmod'],
    ['<code>source greet.sh</code> or <code>. greet.sh</code>', 'no', 'the current shell', 'loading variables and functions, such as ~/.bashrc'],
    ['<code>greet.sh</code>', 'yes', 'a new bash process', 'after copying it into a folder on PATH, such as ~/bin']])}
{note('Use #!/bin/bash when the script uses bash features such as [[ ]] or arrays. #!/bin/sh asks for a plain POSIX shell, which on Debian and Ubuntu is dash, and many bash features fail there.', 'warn')}
{talk('A shell script is simply a text file full of commands. Instead of typing the same ten lines every morning, you write them once and run the file. The first line, called the shebang, starts with a hash and an exclamation mark followed by the path of the interpreter, for example slash bin slash bash. When you run the file, the kernel reads those two characters and starts that program to read the rest. Lines starting with a hash are comments for humans. Before you can run the script by name, give it permission to execute with chmod plus x, and then start it with dot slash and its name. The dot slash matters: for safety, the current folder is not in PATH, so bash would not find the script otherwise. You can also run any script with bash followed by the file name, or load it into your current shell with source.')}
''', kw=['shell script', 'shebang', '#!/bin/bash', 'chmod +x', './script', 'bash script.sh', 'source', 'comment', 'sh vs bash', 'dash'])

K.lesson('args', 'Arguments: $1, $2, $# and "$@"', f'''
<p>Words typed after the script name are its <b>arguments</b>. Inside the script they are the <b>positional parameters</b> $1, $2 and so on. From the tenth on you need braces: ${{10}}.</p>
{table(['Parameter', 'Holds'], [
    ['<code>$0</code>', 'the name the script was started with'],
    ['<code>$1</code> ... <code>$9</code>, <code>${10}</code>', 'the arguments, one each'],
    ['<code>$#</code>', 'how many arguments there are'],
    ['<code>"$@"</code>', 'all arguments, each kept as its own word (almost always what you want)'],
    ['<code>"$*"</code>', 'all arguments joined into one word with spaces'],
    ['<code>shift</code>', 'drops $1 and moves the others down by one'],
    ['<code>${1:-default}</code>', '$1, or the default when it is empty or missing']])}
{play('lx-args')}
{run('Arguments in action', """cat > args.sh <<'EOF'
#!/bin/bash
echo "name: $0  count: $#"
echo "first: $1  second: $2"
echo "all, one per line:"
printf '  [%s]\\n' "$@"
shift
echo "after shift: $# left, first is now $1"
EOF
bash args.sh Asha "New Delhi" 42
bash args.sh
cat > hello.sh <<'EOF'
#!/bin/bash
name=${1:-friend}
echo "Hello, $name!"
EOF
bash hello.sh
bash hello.sh Ravi""", note='printf repeats its format for every argument, so it prints each one in brackets. The quotes kept "New Delhi" as one argument. With no arguments, $1 is empty and ${1:-friend} falls back to friend.')}
{note('Always quote "$1" and "$@". Without quotes a file name like My Report.pdf becomes two words, and an empty argument disappears completely.', 'warn')}
{talk('Scripts become useful when they take input from the command line. Every word after the script name is an argument, and inside the script you read them as dollar one, dollar two and so on, while dollar zero holds the name of the script itself. Dollar hash tells you how many arguments were given, which is how a script checks that it was used correctly. To pass all the arguments on, write dollar at sign inside double quotes. That keeps every argument as its own word, even if it contains spaces. The shift command throws away the first argument and moves the rest down, which is handy when you process them one by one in a loop. And a default value such as dollar brace one colon dash friend gives a friendly fallback when the user types nothing.')}
''', kw=['arguments', 'positional parameters', '$1', '$0', '$#', '"$@"', '"$*"', 'shift', '${1:-default}', 'quoting arguments'])

K.lesson('status', 'Exit status: how scripts say yes or no', f'''
<p>Every command ends with an <b>exit status</b>, a number from 0 to 255. <b>0 means success</b> and anything else means some kind of failure. The status of the last command is in <code>$?</code>. A script sets its own status with <code>exit N</code>, and without it the script returns the status of its last command.</p>
{table(['Status', 'Usual meaning'], [
    ['0', 'success'],
    ['1', 'general failure (grep: no line matched)'],
    ['2', 'wrong usage, for example a bad option'],
    ['126', 'found but not executable (no x bit)'],
    ['127', 'command not found'],
    ['128 + N', 'killed by signal N, for example 130 after Ctrl+C']])}
{run('Reading and setting exit statuses', """ls notes.txt; echo "status $?"
ls nothere; echo "status $?"
grep -q milk notes.txt; echo "grep found it: status $?"
grep -q pizza notes.txt; echo "grep found nothing: status $?"
nosuchcmd; echo "status $?"
cat > check.sh <<'EOF'
#!/bin/bash
if [ $# -eq 0 ]; then
  echo "usage: $0 FILE" >&2
  exit 2
fi
echo "checking $1"
EOF
bash check.sh; echo "status $?"
bash check.sh notes.txt; echo "status $?"
mkdir -p backup && cp notes.txt backup/ && echo "copied"
cd nowhere || echo "could not enter nowhere\"""", note='ls notes.txt prints the file name and succeeds. grep -q prints nothing and only sets the status. check.sh writes its usage message to stderr with >&2 and exits with 2. && runs the next command only after a success, || only after a failure.')}
{note('Test a status right after the command. Even echo changes $?, so save it first if you need it twice: rc=$?.', 'tip')}
{talk('In the shell, success and failure are numbers. Every command finishes with an exit status, and zero means everything went well, while any other number means something went wrong. That is the opposite of many programming languages, where zero means false, so it is worth remembering. The special variable dollar question mark holds the status of the last command, so you can print it or test it. Some numbers have fixed meanings: one hundred and twenty seven means the command was not found, and one hundred and twenty six means it could not be executed. Your own scripts should follow the same rule: exit zero when they succeed, and exit with a small non zero number, often one or two, when they fail. That lets other scripts and tools such as cron, make and CI pipelines know whether your script worked. The operators double ampersand and double bar build on exit statuses: run the next command only if the last one succeeded, or only if it failed.')}
''', kw=['exit status', 'exit code', '$?', 'exit', 'return code', '0 means success', '127', '126', '&&', '||', 'usage message'])

K.lesson('io', 'Talking to the user: echo, printf, read and here documents', f'''
{cmdtable([
    ('echo "text"', 'Print a line (-n no newline, -e turns escape codes into characters)', 'echo "Done in $SECONDS s"'),
    ('printf FORMAT ARGS', 'Formatted output, the portable choice', "printf '%-8s %5.1f\\n' Asha 91.5"),
    ('echo "msg" >&2', 'Write an error or progress message to stderr', 'echo "error: no such file" >&2'),
    ('read -r VAR', 'Read one line from the keyboard (or stdin) into VAR', 'read -r answer'),
    ('read -r -p "Name: " VAR', 'Show a prompt first', 'read -r -p "Continue? [y/N] " ok'),
    ('read -r A B REST', 'Split the line into words, the last variable gets the rest', 'read -r first last <<< "Asha Rao"'),
    ('cat <<EOF ... EOF', 'A here document: many lines of text, $variables expanded', 'cat <<EOF > report.txt'),
    ("cat <<'EOF' ... EOF", 'Quoted end word: text is taken literally', "cat <<'EOF' > script.sh")])}
{run('Output and input in scripts', """printf '%-8s|%6s|%s\\n' name score grade
printf '%-8s|%6.1f|%s\\n' Asha 91.5 A Ravi 78 B
read -r first last <<< "Asha Rao"
echo "first=$first last=$last"
read -r -p "Your city: " city <<< "Pune"
echo "city=$city"
user=$USER
cat <<EOF
Report for $user
Files here: $(ls | wc -l)
EOF
cat <<'EOF'
Nothing is expanded here: $user $(date)
EOF""", note='printf reused its format for the second pair of values. read takes its input from a here string here, and with no terminal attached the -p prompt is not shown. The first here document expanded the variable and the command, the quoted EOF kept the text exactly.')}
{lab('Write your first scripts', [
    ('Create <code>hi.sh</code> whose first line is <code>#!/bin/bash</code> and second line is <code>echo "Hi, $1"</code>.', "printf '#!/bin/bash\\necho \"Hi, $1\"\\n' > hi.sh", [{'has': ['hi.sh', '#!/bin/bash']}, {'has': ['hi.sh', 'echo "Hi, $1"']}]),
    ('Make <code>hi.sh</code> executable for everyone.', 'chmod +x hi.sh', [{'mode': ['hi.sh', '755']}]),
    ('Run it with its path and the argument Asha.', './hi.sh Asha', [{'cmd': r'^\./hi\.sh'}, {'out': '^Hi, Asha$'}]),
    ('Run it through bash with the argument Ravi.', 'bash hi.sh Ravi', [{'cmd': r'^bash\s+hi\.sh'}, {'out': '^Hi, Ravi$'}]),
    ('Run a command that does not exist, then print the exit status.', 'nosuchcmd; echo $?', [{'out': '^127$'}]),
    ('Create <code>count.sh</code> that prints <code>$# args: $@</code>, then run it with bash and the arguments a, "b c" and d.', "printf '#!/bin/bash\\necho \"$# args: $@\"\\n' > count.sh && bash count.sh a \"b c\" d", [{'out': '^3 args: a b c d$'}]),
    ('Read the words <code>Asha Rao</code> from a here string into the variables first and last.', 'read -r first last <<< "Asha Rao"', [{'env': ['first', 'Asha']}, {'env': ['last', 'Rao']}])])}
{talk('Scripts talk to people through standard output and standard error. echo is quick for simple lines, while printf gives exact control with a format string, much like in C: percent s for text, percent d for whole numbers and percent point one f for one decimal place. Send error messages and progress notes to standard error with greater than ampersand two, so they still reach the screen when the normal output goes into a file or a pipe. To ask a question, use read dash r with a variable name, and dash p to show a prompt. Here documents let you write many lines of text at once, such as a report or a config file. Without quotes around the end word, variables and commands inside are expanded. With quotes, the text is written exactly as it is, which is perfect for creating another script.')}
''', kw=['echo', 'printf', 'read', 'read -p', 'read -r', 'stderr', '>&2', 'here document', '<<EOF', "<<'EOF'", 'here string', 'prompt'])

K.lesson('levels', 'First scripts from school to research', f'''
{ladder(
    '<p>A script is a list of commands saved in a file. The first line says which program runs it. Arguments come in as $1, $2, and the script answers with an exit status, where 0 means it worked.</p>',
    '<p>When you run ./greet.sh, the kernel’s execve() sees the two bytes #! at the start, reads the interpreter path and runs it with the script path as an argument, as if you typed /bin/bash ./greet.sh. The shell then parses the file line by line, so a syntax error late in the file appears only when that line is reached. Exit statuses are 8 bits, so exit 256 becomes 0.</p>',
    '<p>The #! line allows one optional argument and is limited in length (256 bytes on current Linux). #!/usr/bin/env bash finds bash through PATH, which helps on systems where bash lives elsewhere, at the cost of trusting PATH. POSIX sh scripts run on any Unix (dash, busybox ash, ksh), while bash scripts may use arrays, [[ ]] and other extensions. Tools such as ShellCheck read scripts statically and warn about unquoted variables, missing exit checks and portability problems.</p>',
    '<p>Studies of real shell scripts (for example the Smoosh formal semantics of POSIX shell, POPL 2020, and work on static analysis of Dockerfiles and CI scripts) show how hard the shell language is to analyse: word splitting and expansion depend on runtime values. Projects such as Oil and NGS design new shells that keep compatibility while removing these traps.</p>')}
{scene('the morning report', '<p>An analyst runs the same five commands every morning to count yesterday’s orders from a log. She writes them into <code>orders.sh</code>, takes the date as <code>$1</code> with today as the default, prints a usage line to stderr and exits with 2 when the log is missing. Now <code>./orders.sh 2026-11-22</code> gives the answer in a second, and the team’s dashboard calls the same script.</p>')}
{talk('Here is what really happens when you run a script by name. The kernel opens the file, sees the two characters hash and exclamation mark at the very start, reads the interpreter path that follows, and runs that interpreter with your script as its argument. bash then reads the file and executes it line by line, which is why a typo near the end only shows up when that line is reached. Exit statuses are stored in eight bits, so the largest is two hundred and fifty five. Experienced writers often start scripts with hash bang slash usr slash bin slash env bash, which finds bash wherever it is installed. They also run ShellCheck, a free tool that reads a script and warns about common mistakes, especially missing quotes. Researchers have even written exact mathematical descriptions of how the shell expands words, because the rules are so easy to get wrong, and some new shells try to keep the convenience while removing the traps.')}
''', kw=['execve', 'shebang internals', '#!/usr/bin/env bash', 'POSIX sh', 'dash', 'ShellCheck', 'exit status range', 'portability', 'Smoosh', 'Oil shell'])

K.quiz('e', 'What must the first line of a bash script be?', ['# bash', '#!/bin/bash', '//bash', 'run bash'], 1, 'Hash bang.', 'The shebang names the interpreter.')
K.quiz('e', 'You wrote backup.sh. Which command makes it executable?', ['chmod +x backup.sh', 'exec backup.sh', 'chown +x backup.sh', 'run backup.sh'], 0, 'Change mode.', 'chmod +x adds execute permission.')
K.quiz('e', 'Why do you type ./backup.sh and not just backup.sh?', ['./ makes it faster', 'The current folder is not in PATH', './ means run as root', 'It is a typing habit only'], 1, 'Command search.', 'bash only searches PATH for names without a slash.')
K.quiz('e', 'What does exit status 0 mean?', ['Failure', 'Success', 'Not found', 'Killed'], 1, 'Zero is good.', 'In the shell, 0 means success.')
K.quiz('m', 'A script is run as ./s.sh a "b c" d. What is $#?', ['3', '4', '5', '2'], 0, 'Quotes keep words together.', 'a, b c and d are three arguments.')
K.quiz('m', 'Which passes all arguments on unchanged, even ones with spaces?', ['$*', '$@', '"$@"', '"$*"'], 2, 'Quoted at sign.', '"$@" keeps each argument as its own word.')
K.quiz('m', 'What does name=${1:-guest} do?', ['Always sets guest', 'Uses $1, or guest when $1 is empty or unset', 'Deletes $1', 'Fails without $1'], 1, 'Default value.', ':- supplies a default.')
K.quiz('m', 'How should a script print an error message?', ['echo "error" > error', 'echo "error" >&2', 'print error', 'echo -e error'], 1, 'Stream 2.', '>&2 sends the message to stderr.')
K.quiz('m', 'Which runs a script inside the current shell, so its variables stay?', ['bash s.sh', './s.sh', 'source s.sh', 'exec s.sh'], 2, 'Load it here.', 'source (or .) runs the file in the current shell.')
K.quiz('h', 'What is the difference between <<EOF and <<\'EOF\'?', ['None', 'Quoted EOF stops $variables and $(commands) from expanding', 'Quoted EOF adds a newline', 'Unquoted EOF is not allowed'], 1, 'Literal text.', 'Quoting the end word makes the here document literal.')
K.quiz('h', 'A script ends with exit 300. What status does the caller see?', ['300', '44', '255', '0'], 1, '8 bits.', '300 mod 256 = 44.')
K.quiz('h', 'Your script uses [[ ]] and arrays but starts with #!/bin/sh. What happens on Ubuntu?', ['Works the same', 'dash runs it and the bash features fail', 'It runs as root', 'It is converted to bash'], 1, 'sh is dash there.', 'Use #!/bin/bash for bash features.')
K.quiz('x', 'What does the kernel do with the line #!/usr/bin/env bash?', ['Ignores it', 'Runs /usr/bin/env with bash and the script path, and env finds bash in PATH', 'Runs bash from /usr/bin/env/bash', 'Compiles the script'], 1, 'execve and the interpreter line.', 'env searches PATH for bash, then runs it on the script.')

K.calc('e', 'A script is run as ./s.sh one two three four. What is $#?', '4', 'Count words after the name.', ['Words after ./s.sh: one, two, three, four.', '$0 is not counted.', eq('4')], check=4)
K.calc('e', 'After one shift in that script, how many arguments are left?', '3', 'shift drops one.', ['Before: 4.', 'shift removes $1.', eq('4 − 1 = 3')], check=3)
K.calc('m', 'A command was killed by Ctrl+C (SIGINT, signal 2). What does $? show?', '130', '128 plus the signal.', ['Signal deaths add 128.', '128 + 2.', eq('130')], check=130)
K.calc('m', 'printf repeats its format. With the format "%s-%s" plus a newline code and the values a b c d, how many lines are printed?', '2', 'Two values per line.', ['The format uses 2 arguments.', '4 arguments ÷ 2 per line.', eq('2 lines: a-b and c-d')], check=2)
K.calc('m', 'A script takes ${12}. How many arguments must be given at least for it to be non-empty?', '12', 'Position 12.', ['${12} is the twelfth argument.', 'Fewer arguments leave it empty.', eq('12')], check=12)
K.calc('h', 'exit 513 is used in a script. What status does the parent see?', '1', 'Only 8 bits survive.', ['Statuses are taken mod 256.', '513 = 2 × 256 + 1.', eq('1')], check=1)

K.must('Script basics', 'First line #!/bin/bash, then chmod +x and run with ./name.sh. bash name.sh needs no x bit, source runs it in the current shell.')
K.must('Arguments', '$0 name, $1..$9 and ${10}, $# count, "$@" all as separate words, shift moves them down, ${1:-default} for a fallback.')
K.must('Exit status', '0 is success. $? holds the last status. exit N ends the script. 127 not found, 126 not executable, 128+N killed by signal N.')
K.must('Output', 'printf for exact formats, echo for simple lines, errors to stderr with >&2.')
K.must('Input', 'read -r VAR (add -p "prompt"), read -r a b rest splits words. Here documents: <<EOF expands, <<\'EOF\' keeps text literal.')

T = K.topic(
    slug='first-scripts', topic='first-scripts',
    step=(1, 'Writing scripts', 'lx-script-1', 'Turn commands into reusable scripts: the shebang, arguments, exit statuses, input and output, and how the shell expands every word.', 'Intermediate'),
    title='Your first shell scripts', short='First scripts', badge='1.1', minutes=45, added='2026-11-23',
    lead='Write a script, make it executable and run it four different ways, read arguments with $1 and "$@", report success or failure with exit statuses, and talk to the user with printf, read and here documents.',
    desc='What a script is, the shebang line and chmod +x, ./script versus bash script versus source versus PATH, comments, positional parameters $0 $1 ${10} $# "$@" "$*" and shift, default values, exit statuses, $?, exit, && and ||, echo and printf, stderr with >&2, read with -r and -p, here documents and here strings, and how the kernel runs a #! file.',
    summary='Shebang and chmod +x, arguments and "$@", exit statuses, printf, read and here documents.',
    keywords=['shell script', 'bash script', 'shebang', 'chmod +x', 'arguments', '$1', '"$@"', 'exit status', '$?', 'printf', 'read', 'here document'],
    recap='<p>A script is a file of commands with #!/bin/bash on top. Arguments arrive as $1, $2 and "$@", the script answers with an exit status (0 is success), and printf, read and here documents handle output and input.</p>')
