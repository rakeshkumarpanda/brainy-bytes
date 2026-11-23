# Shell scripting 4.1: robust scripts. set -e, set -u and set -o pipefail with the exact errexit exceptions, trap on
# EXIT, ERR, INT and TERM, mktemp and cleanup, LINENO and BASH_COMMAND, bash -n and bash -x with PS4, ShellCheck,
# command -v, readonly, umask, --, flock locks, dry runs and idempotent steps. Sources: bash(1) sections SHELL BUILTIN
# COMMANDS (set, trap, command, readonly, umask), Shell Variables (LINENO, BASH_COMMAND, PS4, PIPESTATUS), SIGNALS,
# mktemp(1), flock(1), the ShellCheck wiki for the SC codes quoted, the GNU Bash Reference Manual 4.3.1.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('strict', 'Stop on the first error: set -e, -u and pipefail', f'''
<p>By default bash runs every line of a script, even after a command fails. Three options make a script stop instead of carrying on with bad data. Many scripts start with all three on one line.</p>
{table(['Option', 'Effect', 'Watch out for'], [
    ['<code>set -e</code> (errexit)', 'exit as soon as a simple command fails', 'ignored inside if, while and until tests, in && and || lists except the last command, and after !'],
    ['<code>set -u</code> (nounset)', 'using a variable that was never set is an error, and the script exits', 'use ${VAR:-} for variables that may be missing, such as optional settings'],
    ['<code>set -o pipefail</code>', 'a pipeline fails when any part fails, not only the last', 'grep finding nothing in the middle of a pipe now counts as a failure'],
    ['<code>set -euo pipefail</code>', 'all three at once, usually the second line of a script', 'it is a safety net, not a replacement for checking errors yourself']])}
{play('lx-errexit')}
{run('What set -e and friends really do', """cat > strict.sh <<'EOF'
#!/bin/bash
set -euo pipefail
echo "start"
if grep -q pizza fruits.txt; then echo "pizza"; else echo "no pizza, still running"; fi
grep -q pizza fruits.txt || echo "handled with ||"
count=$(grep -c apple fruits.txt)
echo "apples: $count"
grep pizza fruits.txt | sort
echo "never printed"
EOF
bash strict.sh; echo "exit status $?"
printf 'set -u\\necho "name is ${NAME:-unknown}"\\necho "home is $HOEM"\\necho "never"\\n' > typo.sh
bash typo.sh; echo "exit status $?"
printf 'set -e\\nn=0\\n(( n++ ))\\necho "n=$n"\\n' > gotcha.sh
bash gotcha.sh; echo "exit status $?"
printf 'set -e\\nn=0\\n(( ++n ))\\necho "n=$n"\\n' > fixed.sh
bash fixed.sh""", note='The failing test inside if and the failure before || did not stop the script. With pipefail the grep that found nothing made the pipeline fail, so set -e stopped it. set -u caught the typo HOEM, while ${NAME:-unknown} supplied a default. (( n++ )) returns the old value 0, which counts as a failure, but (( ++n )) returns 1 and passes.')}
{note('set -e is ignored in a function called from a condition such as if myfunc or myfunc || ..., for the whole function body. Check important steps explicitly with || die "...".', 'warn')}
{talk('A plain bash script keeps going after a failure, which can be dangerous. Imagine a cleanup script whose cd command fails, followed by a delete that now runs in the wrong folder. Three options give you a safety net. Set dash e stops the script when a command fails. Set dash u stops it when you use a variable that was never set, which catches typos in variable names. And set dash o pipefail makes a pipeline fail if any part of it fails, not only the last command. Most careful scripts start with set dash e u o pipefail. But set dash e has exceptions, and they matter. A failure inside an if test, a while test, or before a double ampersand or double bar is treated as a decision, not an error. And arithmetic that evaluates to zero, such as n plus plus when n starts at zero, counts as a failure and stops the script. Try the animation to see every rule in action.')}
''', kw=['set -e', 'errexit', 'set -u', 'nounset', 'pipefail', 'set -euo pipefail', 'strict mode', 'unbound variable', 'errexit exceptions', '(( n++ )) gotcha'])

K.lesson('trap', 'Cleaning up with trap and temporary files', f'''
<p><code>trap 'commands' SIGNALS</code> runs commands when the script receives a signal or reaches a special moment. The most useful is <b>EXIT</b>, which runs whenever the script ends, normally, after an error, or after Ctrl+C or a kill.</p>
{cmdtable([
    ("trap 'cmds' EXIT", 'Run cmds when the script ends, however it ends', "trap 'rm -rf \"$tmpdir\"' EXIT"),
    ("trap 'cmds' ERR", 'Run cmds after any failing command (same rules as set -e)', "trap 'echo \"failed at line $LINENO\"' ERR"),
    ("trap 'cmds' INT TERM", 'Catch Ctrl+C (INT) and kill (TERM)', "trap 'echo stopping; exit 130' INT"),
    ("trap '' INT", 'Ignore a signal', "trap '' HUP"),
    ('trap - INT', 'Back to the default action', 'trap - INT'),
    ('mktemp, mktemp -d', 'Create a unique temporary file or folder that only you can read', 'tmp=$(mktemp) && trap \'rm -f "$tmp"\' EXIT')])}
{run('A script that always cleans up', """cat > tidy.sh <<'EOF'
#!/bin/bash
set -euo pipefail
workdir=$(mktemp -d)
cleanup() { rm -rf -- "$workdir"; echo "cleanup: removed the temp folder" >&2; }
trap cleanup EXIT
trap 'echo "error on line $LINENO: $BASH_COMMAND" >&2' ERR
echo "working in a private folder: $(stat -c %A "$workdir")"
sort fruits.txt > "$workdir/sorted"
uniq -c "$workdir/sorted" | sort -rn | head -2
cp "$workdir/sorted" /root/sorted.txt
echo "not reached"
EOF
bash tidy.sh; echo "exit status $?"
cat > stop.sh <<'EOF'
#!/bin/bash
trap 'echo "caught Ctrl+C (INT), saving state"; exit 130' INT
trap 'echo "goodbye from EXIT"' EXIT
echo "working"
kill -INT $$
echo "never printed"
EOF
bash stop.sh; echo "exit status $?\"""", note='mktemp -d made a folder only the owner can open (drwx------). The cp to /root failed, so the ERR trap printed the line number and the failing command, set -e stopped the script, and the EXIT trap still removed the temporary folder. The second script sent itself SIGINT, as Ctrl+C would, and the INT trap ran before EXIT. 130 is 128 plus 2, the number of SIGINT.')}
{note('Never use a fixed name such as /tmp/myscript.tmp. Another user can create it first, as a symbolic link to one of your files, and your script would overwrite that file. mktemp picks a new random name every time.', 'warn')}
{talk('Scripts often create temporary files, take locks, or start helper processes, and these must be cleaned up even when something goes wrong. The trap command is the tool for this. Trap followed by a command and the word EXIT runs that command whenever the script ends, whether it finished normally, failed under set dash e, or was stopped with Control C. The usual pattern is to create a private temporary folder with mktemp dash d, write a small cleanup function, and register it with trap cleanup EXIT straight away. A trap on ERR runs after any failing command, and the variables LINENO and BASH COMMAND tell you exactly where it happened, which makes error messages much more helpful. Traps on INT and TERM let a script react to Control C and to kill, for example to save its state. Always let mktemp choose the name, because fixed names in slash tmp can be abused by other users.')}
''', kw=['trap', 'EXIT trap', 'ERR trap', 'cleanup', 'mktemp', 'mktemp -d', 'temporary files', 'SIGINT', 'SIGTERM', 'LINENO', 'BASH_COMMAND', 'Ctrl+C in scripts'])

K.lesson('debug', 'Finding bugs: bash -n, set -x and ShellCheck', f'''
{cmdtable([
    ('bash -n script.sh', 'Check the syntax without running anything', 'bash -n deploy.sh && echo "syntax ok"'),
    ('bash -x script.sh', 'Run and print every command after expansion', 'bash -x backup.sh 2> trace.log'),
    ('set -x ... set +x', 'Trace only part of a script', 'set -x; risky_step; set +x'),
    ("PS4='+ line $LINENO: '", 'Change the prefix of trace lines, for example to show line numbers', "export PS4='+ ${BASH_SOURCE}:${LINENO}: '"),
    ('shellcheck script.sh', 'A separate program that finds common mistakes without running the script', 'shellcheck -x deploy.sh'),
    ('echo "..." >&2', 'Debug messages to stderr, so they do not mix with real output', 'echo "debug: n=$n" >&2')])}
{run('Syntax checks and traces', """printf 'for f in *.txt; do\\n  echo "$f"\\n' > broken.sh
bash -n broken.sh; echo "status $?"
cat > trace.sh <<'EOF'
total=0
for n in 3 4; do
  total=$(( total + n * n ))
done
[ "$total" -gt 20 ] && echo "big: $total"
EOF
bash -x trace.sh
PS4='+ line $LINENO: ' bash -x trace.sh 2>&1 | head -4""", note='bash -n found the missing done without running a single command. The trace shows each command after expansion, so you see the real numbers that were added. Setting PS4 for one run added the line number to every trace line.')}
{sample('ShellCheck on a risky script (ShellCheck is a separate program, install it with apt install shellcheck)', """cat -n clean.sh
shellcheck clean.sh""", out="""     1	#!/bin/bash
     2	dir=$1
     3	cd $dir
     4	rm -rf $dir/cache

In clean.sh line 3:
cd $dir
^-----^ SC2164 (warning): Use 'cd ... || exit' or 'cd ... || return' in case cd fails.
   ^--^ SC2086 (info): Double quote to prevent globbing and word splitting.

In clean.sh line 4:
rm -rf $dir/cache
       ^--^ SC2086 (info): Double quote to prevent globbing and word splitting.

For more information:
  https://www.shellcheck.net/wiki/SC2164 -- Use 'cd ... || exit' or 'cd ... ...
  https://www.shellcheck.net/wiki/SC2086 -- Double quote to prevent globbing ...""", note='Each finding has a code you can look up on the ShellCheck wiki. Fixing both gives cd -- "$dir" || exit 1 and rm -rf -- "$dir/cache". With an empty $1, the original would have run rm -rf /cache.')}
{talk('Three tools find most bugs in shell scripts. Bash dash n reads the whole script and checks the syntax without running anything, which is a quick safety step before you deploy a script. Bash dash x runs the script and prints every command after all expansions, with a plus sign in front, so you see the real values of variables at each step. You can switch tracing on and off inside a script with set dash x and set plus x, and the variable PS4 changes the prefix, for example to show line numbers. The third tool is ShellCheck, a free program that reads a script and warns about common mistakes, such as missing quotes around variables or a cd whose failure is ignored. Each warning has a code like S C two zero eight six, which you can look up on the ShellCheck wiki for an explanation and a fix. Many teams run ShellCheck automatically on every change.')}
''', kw=['bash -n', 'syntax check', 'bash -x', 'set -x', 'xtrace', 'PS4', 'debugging scripts', 'ShellCheck', 'SC2086', 'SC2164', 'trace with line numbers'])

K.lesson('defend', 'Defensive habits for scripts that run unattended', f'''
{table(['Habit', 'Example', 'Why'], [
    ['Quote every expansion', '<code>rm -- "$file"</code>', 'spaces and wildcards in data cannot change the command'],
    ['End options with --', '<code>cp -- "$src" "$dst"</code>', 'a file called -rf is not read as an option'],
    ['Check tools exist', '<code>command -v jq >/dev/null || die "jq is needed"</code>', 'fail early with a clear message'],
    ['Constants are readonly', '<code>readonly BACKUP_DIR=/srv/backup</code>', 'a later line cannot change them by mistake'],
    ['Private files', '<code>umask 077</code>', 'new files are readable only by you'],
    ['One run at a time', '<code>flock -n /tmp/job.lock ./job.sh</code>', 'a second copy started by cron exits instead of clashing'],
    ['Dry run first', '<code>run() { if (( DRY )); then echo "would run: $*"; else "$@"; fi; }</code>', 'see what would happen before it happens'],
    ['Idempotent steps', '<code>mkdir -p</code>, <code>ln -sfn</code>, <code>grep -q ... || echo ... >> file</code>', 'running the script twice gives the same result']])}
{run('Defensive building blocks', """need() { command -v "$1" >/dev/null || { echo "missing tool: $1" >&2; return 1; }; }
need sort && echo "sort is at $(command -v sort)"
need jq-does-not-exist; echo "status $?"
readonly LIMIT=3
LIMIT=10
echo "LIMIT is still $LIMIT"
touch -- -rf
ls -- -rf && rm -- -rf && echo "removed the file called -rf"
bash -c 'umask 077; touch private.txt; stat -c "%A %n" private.txt'
DRY=1
run() { if (( DRY )); then echo "would run: $*"; else "$@"; fi; }
run rm -rf /srv/old-releases
grep -q '^export EDITOR=' .bashrc || echo 'export EDITOR=nano' >> .bashrc
grep -q '^export EDITOR=' .bashrc || echo 'export EDITOR=nano' >> .bashrc
grep -c '^export EDITOR=' .bashrc
flock -n /tmp/demo.lock echo "got the lock and ran the job\"""", note='command -v answered without running anything. The readonly variable refused the change. With -- the file named -rf was treated as a name, not as options. umask 077 in a child bash made a file only the owner can read, without changing the umask of this shell. The dry run printed the dangerous command instead of running it. The grep or echo line added the setting once, even though it ran twice.')}
{lab('Make a script safe', [
    ('Turn on the three strict options in one set command.', 'set -euo pipefail', [{'cmd': r'set\s+-euo\s+pipefail|set\s+-eu\s+-o\s+pipefail'}]),
    ('Turn the strict options off again, so the practice shell stays usable.', 'set +euo pipefail', [{'cmd': r'set\s+\+'}]),
    ('Create a temporary folder with mktemp and keep its path in the variable tmp.', 'tmp=$(mktemp -d)', [{'cmd': r'mktemp\s+-d'}, {'envre': ['tmp', '^/tmp/tmp\\.']}]),
    ('Register a trap that removes "$tmp" when the shell exits.', 'trap \'rm -rf "$tmp"\' EXIT', [{'cmd': r'^\s*trap\b.*EXIT'}]),
    ('Check the syntax of the file notes.txt as a script with bash -n.', 'bash -n notes.txt', [{'cmd': r'bash\s+-n'}]),
    ('Print where the sort command lives, using command -v.', 'command -v sort', [{'out': '^/usr/bin/sort$'}]),
    ('Make LIMIT a readonly variable with the value 5.', 'readonly LIMIT=5', [{'env': ['LIMIT', '5']}])])}
{talk('Scripts that run unattended, from cron or a deployment pipeline, need extra care, because nobody is watching when something odd happens. A few habits prevent most disasters. Quote every variable, and put a double dash before file names, so a file called dash r f can never be read as options. Check at the start that every tool the script needs is installed, using command dash v, and stop with a clear message if not. Make constants readonly, and set umask zero seven seven when the script writes private data. Use flock so that two copies of the same job cannot run at once. Offer a dry run mode that prints what would happen. And write steps that are idempotent, which means running them twice gives the same result as running them once, such as mkdir dash p, or adding a line to a file only when it is not already there.')}
''', kw=['defensive scripting', 'command -v', 'readonly', 'umask 077', 'flock', 'lock file', 'dry run', 'idempotent', 'end of options --', 'unattended scripts'])

K.lesson('levels', 'Robust scripts from school to research', f'''
{ladder(
    '<p>A good script stops when something goes wrong, tells you where, and tidies up after itself. set -euo pipefail stops it, trap cleans up, and bash -x and ShellCheck help you find mistakes.</p>',
    '<p>errexit is skipped in conditions, in && and || lists except the last command, after !, and in all commands of a function called from a condition. A command substitution inside a local declaration hides its status, since local itself succeeds, so write local x and then x=$(cmd). The EXIT trap runs once when the shell ends, and ERR follows the same rules as errexit.</p>',
    '<p>Subshells and command substitutions do not inherit the ERR trap unless set -E (errtrace) is on, and set -T does the same for DEBUG and RETURN. inherit_errexit (shopt, bash 4.4) makes $( ) inherit set -e. Signals interrupt a foreground external command only after it exits, so long-running tools should be started in the background and waited for if a script must react quickly. PIPESTATUS gives the status of every part of the last pipeline.</p>',
    '<p>Many experts argue that set -e is unreliable because of its many exceptions (see the BashFAQ entry 105 on Greg’s Wiki), and prefer explicit checks with || die. Static analysis research on shell scripts, including work behind ShellCheck and the NL2Bash and Smoosh projects, shows that error handling and quoting dominate real bugs. Configuration management tools such as Ansible encode the idea of idempotent steps directly, so that running a task twice is always safe.</p>')}
{scene('the backup that deleted itself', '<p>A nightly job ran <code>cd $BACKUP_DIR; rm -rf *</code> to empty a staging folder. One night BACKUP_DIR was empty after a config change, cd went to the home folder, and the job deleted it. The rewrite starts with <code>set -euo pipefail</code>, reads <code>: "${BACKUP_DIR:?is not set}"</code>, runs <code>cd -- "$BACKUP_DIR" || exit 1</code>, uses <code>flock</code> so two runs never overlap, and logs every step through an ERR trap. ShellCheck now runs in CI and flagged three other scripts with the same pattern.</p>')}
{talk('Here is the expert view on robust scripts. Set dash e has many exceptions: it is ignored inside conditions, in all but the last command of double ampersand and double bar lists, after an exclamation mark, and in every command of a function that was called from a condition. A command substitution inside a local declaration also hides its failure, because local itself succeeds, so declare the variable first and assign it on the next line. Subshells do not inherit the ERR trap unless you set dash capital E. Because of these traps, many experienced writers prefer explicit checks with double bar die after each important step, and treat set dash e only as a backup. Researchers who study real shell scripts find that error handling and quoting cause most bugs, which is exactly what ShellCheck focuses on. And tools such as Ansible build the idea of idempotent steps into their design.')}
''', kw=['errexit exceptions', 'local hides status', 'set -E', 'errtrace', 'inherit_errexit', 'PIPESTATUS', 'BashFAQ 105', 'explicit error checks', 'Ansible idempotence'])

K.quiz('e', 'Which option stops a script when a command fails?', ['set -x', 'set -e', 'set -n', 'set -v'], 1, 'e for error.', 'set -e is errexit.')
K.quiz('e', 'Which option makes an unset variable an error?', ['set -u', 'set -e', 'set -f', 'set -o noclobber'], 0, 'u for unset.', 'set -u is nounset.')
K.quiz('e', 'Which command checks a script for syntax errors without running it?', ['bash -x', 'bash -n', 'bash -e', 'bash -c'], 1, 'n for no execution.', 'bash -n only parses.')
K.quiz('e', 'Which command makes a unique temporary file?', ['touch /tmp/tmp', 'mktemp', 'tmpfile', 'mkdir /tmp'], 1, 'Make temp.', 'mktemp creates a new file with a random name.')
K.quiz('m', 'With set -e, does <code>if grep -q x file; then ...</code> stop the script when grep finds nothing?', ['Yes', 'No, a failing test of if is allowed', 'Only with pipefail', 'Only with set -u'], 1, 'Conditions are decisions.', 'set -e ignores failures in if tests.')
K.quiz('m', 'What does set -o pipefail change?', ['Pipes run faster', 'A pipeline fails when any part fails', 'Pipes are disabled', 'Only the first command counts'], 1, 'Any part.', 'Without it, only the last command counts.')
K.quiz('m', 'Which trap runs however the script ends?', ['trap ... ERR', 'trap ... EXIT', 'trap ... INT', 'trap ... DEBUG'], 1, 'The end.', 'EXIT runs on every exit.')
K.quiz('m', 'set -e and n=0. Why does (( n++ )) stop the script?', ['n++ is a syntax error', 'It evaluates to the old value 0, which means status 1', 'n is read only', 'It does not stop it'], 1, 'Zero is false.', 'An arithmetic result of 0 gives status 1.')
K.quiz('m', 'Which variable holds the line number inside an ERR trap?', ['$LINE', '$LINENO', '$BASH_LINE', '$NR'], 1, 'Line number.', 'LINENO is the current line.')
K.quiz('h', 'Why can local x=$(failing_cmd) hide an error?', ['local cannot hold output', 'The status is that of local, which succeeds', 'x is global', 'It does not hide it'], 1, 'local succeeds.', 'Split it: local x, then x=$(cmd).')
K.quiz('h', 'ShellCheck reports SC2086 on rm -rf $dir/cache. What is the fix?', ['Use rm -r', 'Quote it: rm -rf -- "$dir/cache"', 'Use sudo', 'Add set -x'], 1, 'Quotes.', 'SC2086 asks for double quotes.')
K.quiz('h', 'A script ends by SIGINT after its INT trap calls exit 130. What does $? show in the caller?', ['0', '2', '130', '1'], 2, 'The trap’s exit.', 'The trap exited with 130.')
K.quiz('x', 'Which option makes subshells and $( ) inherit the ERR trap?', ['set -T', 'set -E', 'set -u', 'shopt -s lastpipe'], 1, 'errtrace.', 'set -E is errtrace.')

K.calc('e', 'A script is stopped by SIGTERM (signal 15) with no trap. What exit status does the caller see?', '143', '128 plus the signal.', ['Deaths by signal add 128.', '128 + 15.', eq('143')], check=143)
K.calc('e', 'mktemp -d makes a folder with mode 700. Who may enter it, apart from root?', '1', 'Only the owner.', ['7 for the owner, 0 for group and others.', 'Only the owner.', eq('1 user')], check=1)
K.calc('m', 'With umask 077, what mode does a new file get (files start from 666)?', '600', 'Remove the umask bits.', ['666 with 077 removed.', 'Owner keeps 6, group and others get 0.', eq('600')], check=600)
K.calc('m', 'false | true | false. Without pipefail, what is $?', '1', 'The last command.', ['Only the last part counts.', 'The last part is false.', eq('status 1')], check=1)
K.calc('m', 'true | false | true. With pipefail, what is $?', '1', 'Any failure counts.', ['pipefail gives the last non-zero status.', 'false gave 1.', eq('status 1')], check=1)
K.calc('h', 'A loop with set -e runs (( i++ )) for i from 0. On which pass does the script stop (count from 1)?', '1', 'The first value is 0.', ['On pass 1, i is 0.', 'i++ gives 0, status 1.', eq('pass 1')], check=1)

K.must('Strict mode', 'set -euo pipefail near the top. -e stops on failures, -u on unset variables, pipefail on any failing pipe part.')
K.must('Exceptions', 'set -e ignores if, while and until tests, && and || lists except the last command, and ! commands. (( n++ )) from 0 fails.')
K.must('trap', "trap cleanup EXIT for tidying up, trap '...' ERR with $LINENO and $BASH_COMMAND, INT and TERM for Ctrl+C and kill.")
K.must('Temporary files', 'tmp=$(mktemp) or $(mktemp -d), then trap \'rm -rf -- "$tmp"\' EXIT. Never fixed names in /tmp.')
K.must('Debugging', 'bash -n checks syntax, bash -x or set -x traces, PS4 sets the trace prefix, ShellCheck finds common mistakes.')

T = K.topic(
    slug='robust-scripts', topic='robust-scripts',
    step=(4, 'Robust and scheduled scripts', 'lx-script-4', 'Write scripts that fail safely, clean up after themselves, are easy to debug, and run on a schedule with cron, at and systemd timers.', 'Advanced'),
    title='Robust scripts: errors, traps and debugging', short='Robust scripts', badge='4.1', minutes=55, added='2026-11-23',
    lead='Make scripts stop on errors with set -euo pipefail and know its exceptions, clean up with trap and mktemp, find bugs with bash -n, set -x and ShellCheck, and add defensive habits for unattended runs.',
    desc='set -e, set -u and pipefail with the exact errexit exceptions, the (( n++ )) gotcha, trap on EXIT, ERR, INT and TERM, mktemp and cleanup functions, LINENO and BASH_COMMAND, signals sent to the script itself, bash -n, bash -x and PS4, ShellCheck codes SC2086 and SC2164, command -v, readonly, umask 077, the -- marker, flock locks, dry runs and idempotent steps.',
    summary='set -euo pipefail, trap and mktemp, bash -n, set -x and ShellCheck, defensive habits.',
    keywords=['set -e', 'set -u', 'pipefail', 'trap', 'EXIT', 'ERR', 'mktemp', 'bash -x', 'bash -n', 'ShellCheck', 'flock', 'idempotent'],
    recap='<p>set -euo pipefail stops a script on failures, unset variables and failing pipes, with exceptions for conditions and lists. trap cleanup EXIT and mktemp keep things tidy, bash -n, set -x and ShellCheck find bugs, and quoting, --, readonly, umask and flock protect unattended runs.</p>')
