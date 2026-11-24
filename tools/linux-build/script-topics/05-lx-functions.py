# Shell scripting 3.1: functions. Defining with name() { } and the function keyword, arguments inside a function,
# return statuses versus output, capturing output with $( ), local and dynamic scope, FUNCNAME, recursion, functions
# with redirections, subshell bodies, sourcing a library, die and log helpers, the main "$@" layout. Sources: bash(1)
# sections FUNCTIONS, SHELL BUILTIN COMMANDS (return, local, declare -f -F, source, unset -f, export -f), Shell
# Variables (FUNCNAME), the GNU Bash Reference Manual 3.3.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('define', 'Defining and calling a function', f'''
<p>A <b>function</b> gives a name to a group of commands. You call it like any other command, with arguments. Inside the function, <code>$1</code>, <code>$2</code>, <code>$#</code> and <code>"$@"</code> are the function’s own arguments, not the script’s.</p>
{shape('Two ways to write a function', """name() {
  commands           # $1 $2 ... "$@" are the function's arguments
}

function name {      # the bash keyword form, same result
  commands
}""")}
{run('Functions, run for real', """greet() {
  echo "Hello, $1! You gave $# argument(s)."
}
greet Asha
greet "Ravi Kumar" extra
type greet
backup() {
  local src=$1 dest=${2:-backup}
  mkdir -p "$dest" && cp -- "$src" "$dest/" && echo "copied $src to $dest/"
}
backup notes.txt
backup poem.txt archive
declare -F
unset -f greet
greet Meera""", note='Each call gets its own $1 and $#. type shows the stored body. backup used ${2:-backup} as a default folder. declare -F lists the names of all functions. After unset -f, greet is gone and bash reports command not found.')}
{note('A function must be defined before the line that calls it runs. In a script, put all functions at the top and the main commands at the bottom.', 'tip')}
{talk('A function is a small named piece of a script. You write the name, a pair of round brackets, and then the commands between curly braces. After that, the name works like a new command. When you call it, any words after the name become its arguments, and inside the function dollar one, dollar two and dollar at sign refer to those arguments, not to the arguments of the whole script. Bash also accepts the keyword function in front of the name, which does the same thing. Functions must be defined before they are used, because bash reads and runs the script from top to bottom. The type command shows the body of a function, declare dash capital F lists all function names, and unset dash f removes one. Functions keep scripts short and readable: write a task once, give it a clear name, and call it wherever you need it.')}
''', kw=['function', 'define a function', 'call a function', 'name() { }', 'function keyword', 'function arguments', 'type', 'declare -F', 'unset -f'])

K.lesson('return', 'Getting results out: status, output and variables', f'''
<p>A bash function has three ways to hand back a result. Pick the one that fits.</p>
{table(['Way', 'How', 'Use it for'], [
    ['Exit status', '<code>return N</code> (0 to 255). Without return, the status of the last command', 'yes or no answers, used with if, && and ||'],
    ['Output', '<code>echo</code> or <code>printf</code> the result, catch it with <code>v=$(fn ...)</code>', 'text and numbers'],
    ['A variable', 'set a global, or write into a name given by the caller with <code>printf -v "$1"</code>', 'avoiding the subshell of $( ), several results']])}
{run('Three ways to return', """is_even() { (( $1 % 2 == 0 )); }
for n in 3 8; do
  if is_even "$n"; then echo "$n is even"; else echo "$n is odd"; fi
done
check_file() {
  [ -f "$1" ] || { echo "missing: $1" >&2; return 2; }
  return 0
}
check_file nothere.txt; echo "status $?"
square() { echo $(( $1 * $1 )); }
area=$(square 12)
echo "area is $area"
to_upper() { printf -v "$1" '%s' "${2^^}"; }
to_upper shout "quiet please"
echo "$shout"
fact() {
  (( $1 <= 1 )) && { echo 1; return; }
  echo $(( $1 * $(fact $(( $1 - 1 ))) ))
}
echo "5! = $(fact 5)"
r() { return 300; }; r; echo "return 300 gives $?\"""", note='is_even returns the status of (( )), so it works directly in if. check_file sends its message to stderr and returns 2. square prints its answer and $( ) catches it. printf -v wrote into the variable named by the first argument. fact calls itself, a recursive function. Statuses are 8 bits, so 300 became 44.')}
{note('return is for statuses, not data. return 1000 or return "text" cannot carry a result. Print the value and capture it with $( ) instead.', 'warn')}
{talk('Functions return results in three ways. The first is the exit status, set with the word return and a number from zero to two hundred and fifty five. Zero means yes or success, anything else means no or failure. That makes a function perfect as an if condition, as in if is even. If you leave out return, the function gives the status of its last command. The second way is output. Print the answer with echo or printf, and the caller catches it with dollar and round brackets, like area equals dollar square twelve. This is the usual way to return text or numbers. The third way is a variable. A function can set a global variable, or use printf dash v to write into a variable whose name the caller passes in. That avoids starting a subshell and can hand back more than one value. A common mistake is to return a big number or a word with return, which cannot work, because a status is only eight bits.')}
''', kw=['return', 'exit status of a function', 'return value', 'command substitution', 'printf -v', 'recursion', 'factorial', 'function in if', 'status is 8 bits'])

K.lesson('scope', 'local variables and dynamic scope', f'''
<p>Variables in bash are <b>global</b> unless you declare them with <code>local</code> inside a function. A local variable exists only while that function runs. bash uses <b>dynamic scope</b>: a function that reads a variable sees the value of the nearest caller that has one.</p>
{play('lx-scope')}
{run('local and global, run for real', """total=0
add_bad()  { total=$(( total + $1 )); tmp=$1; }
add_good() { local tmp=$1; total=$(( total + tmp )); }
add_bad 5; add_good 7
echo "total=$total tmp=$tmp"
x=main
show() { echo "show sees x=$x"; }
caller_fn() { local x=caller; show; }
caller_fn
show
where() { echo "I am ${FUNCNAME[0]}, called by ${FUNCNAME[1]:-the script}"; }
outer() { where; }
outer
counter=0
bump() { (( counter++ )); }
bump; bump; echo "counter=$counter"
v=$(bump; echo "$counter"); echo "inside \\$( ): $v, outside: $counter"
in_sub() ( cd /tmp; pwd )
in_sub; pwd""", note='add_bad leaked tmp into the script, add_good kept it local. show saw the caller’s local x, which is dynamic scope. FUNCNAME lists the function names on the call stack. A function called inside $( ) runs in a subshell, so its change to counter was lost. A body in round brackets always runs in a subshell, so its cd did not move the script.')}
{note('Start every function by copying its arguments into local variables with clear names: local file=$1 count=${2:-10}. It documents the function and protects the rest of the script.', 'tip')}
{talk('By default, every variable in bash is global, even one you set inside a function. That is a common source of bugs, because a helper function can quietly overwrite a variable the main script needs. The fix is the local keyword. A local variable lives only while its function runs, and it hides any global with the same name. Bash also has dynamic scope, which surprises people who know other languages. When a function reads a variable it does not own, bash looks at the function that called it, then that function’s caller, and so on up to the script. So a helper can see the local variables of whoever called it. The animation shows the call stack and which value each line reads. The array FUNCNAME holds the names on the stack, which is handy for log messages. Finally, remember that a function run inside dollar and round brackets runs in a subshell, so changes to variables there never come back.')}
''', kw=['local', 'global variable', 'dynamic scope', 'call stack', 'FUNCNAME', 'subshell', 'function in $( )', 'function body in ( )', 'variable leak'])

K.lesson('library', 'Function libraries and the main layout', f'''
<p>Useful functions can live in their own file, a <b>library</b>, that several scripts load with <code>source</code>. A well-organised script then has three parts: settings, functions, and a short <code>main</code> function that is called with <code>"$@"</code>.</p>
{run('A small library and a script that uses it', """mkdir -p lib
cat > lib/log.sh <<'EOF'
# lib/log.sh: logging helpers, load with source
[[ -n ${LOG_SH_LOADED:-} ]] && return 0
LOG_SH_LOADED=1
_say() { printf '%s [%s] %s\\n' "$(date +%H:%M)" "${FUNCNAME[2]:-main}" "$*" >&2; }
log()  { _say "$*"; }
die()  { _say "ERROR: $*"; exit 1; }
EOF
cat > report.sh <<'EOF'
#!/bin/bash
source "$(dirname "$0")/lib/log.sh"
source "$(dirname "$0")/lib/log.sh"
count_lines() { wc -l < "$1"; }
main() {
  [ $# -ge 1 ] || die "usage: report.sh FILE..."
  local f
  for f in "$@"; do
    [ -r "$f" ] || die "cannot read $f"
    echo "$f: $(count_lines "$f") lines"
  done
  log "done with $# file(s)"
}
main "$@"
EOF
bash report.sh fruits.txt poem.txt 2>&1 | sed 's/^[0-9][0-9]:[0-9][0-9]/HH:MM/'
bash report.sh 2>&1 | sed 's/^[0-9][0-9]:[0-9][0-9]/HH:MM/'; echo "status ${PIPESTATUS[0]}"
bash report.sh nothere.txt 2>&1 | sed 's/^[0-9][0-9]:[0-9][0-9]/HH:MM/'""", note='The library guards itself with LOG_SH_LOADED, so loading it twice is harmless. log and die write to stderr through _say, which prints the time and the name of the function that called log or die, FUNCNAME[2]. die then exits with status 1, which PIPESTATUS[0] shows even through the pipe. main "$@" passes every script argument to main unchanged. The sed only replaces the clock time so this page does not change on every build.')}
{lab('Write and use functions', [
    ('Define a function <code>hi</code> that prints <code>Hi, NAME</code> with its first argument, then call it with Asha.', 'hi() { echo "Hi, $1"; }; hi Asha', [{'cmd': r'hi\s*\(\)\s*\{'}, {'out': '^Hi, Asha$'}]),
    ('Define <code>double</code> that prints twice its argument with $(( )), and store double 21 in the variable d.', 'double() { echo $(( $1 * 2 )); }; d=$(double 21)', [{'env': ['d', '42']}]),
    ('Define <code>is_big</code> that succeeds when its argument is over 100, then run is_big 500 && echo big.', 'is_big() { (( $1 > 100 )); }; is_big 500 && echo big', [{'cmd': r'is_big'}, {'out': '^big$'}]),
    ('Set x=outside. Define <code>f</code> that sets a local x=inside and prints it. Call f, then print $x.', 'x=outside; f() { local x=inside; echo $x; }; f; echo $x', [{'cmd': r'\blocal\b'}, {'out': '^inside$'}, {'env': ['x', 'outside']}]),
    ('Write <code>lib.sh</code> containing a function <code>shout</code> that prints its arguments in capitals, then load it with source and run shout hello.', "printf 'shout() { echo \"${*^^}\"; }\\n' > lib.sh; source lib.sh; shout hello", [{'has': ['lib.sh', 'shout']}, {'out': '^HELLO$'}]),
    ('List the names of all defined functions.', 'declare -F', [{'out': 'declare -f hi'}])])}
{talk('As scripts grow, organise them the way professionals do. Put reusable functions, such as logging and error handling, into a library file, and load it with source at the top of each script. A small guard variable at the top of the library makes it safe to load twice. A helper called die prints an error message to standard error and exits with a failure status, so every check in the script becomes one short line. Then write the main logic inside a function called main, and make the very last line main followed by dollar at sign in double quotes. That passes all the script arguments to main unchanged, keeps the top level of the file clean, and makes sure every function is defined before any of them runs. The example shows a report script built this way, with clear usage and error messages.')}
''', kw=['function library', 'source', 'include guard', 'log function', 'die function', 'main "$@"', 'script layout', 'stderr logging', 'FUNCNAME[1]'])

K.lesson('levels', 'Functions from school to research', f'''
{ladder(
    '<p>A function is a named list of commands. You define it once and call it by name with arguments. It answers with a status, or prints a result that you can catch with $( ).</p>',
    '<p>Functions run in the current shell, so they can change variables and the current folder, unless they run inside $( ), a pipeline or a ( ) body. Variables are global unless declared local, and scope is dynamic. return sets an 8-bit status, and the positional parameters are saved and restored around each call.</p>',
    '<p>local -n declares a nameref, a variable that refers to another variable by name, so a function can fill an array the caller chose. export -f makes a function visible to child bash processes through the environment, a feature that was involved in the Shellshock bug (CVE-2014-6271) when old bash versions ran code found after a function definition in an environment variable. Redirections written after a function body apply to every call, and declare -f prints the body.</p>',
    '<p>Dynamic scoping, used by bash and early Lisp, contrasts with the lexical scoping of most modern languages. Programming language research treats it as harder to reason about, because a function’s meaning depends on its callers. Tools such as bats-core (Bash Automated Testing System) and shUnit2 test shell functions one by one, and sourcing a script whose last line is guarded with [[ ${BASH_SOURCE[0]} == "$0" ]] && main "$@" lets tests load its functions without running it.</p>')}
{scene('the shared deploy helpers', '<p>A team had the same twenty lines of logging, retry and lock code copied into nine deploy scripts. They moved it into <code>lib/common.sh</code> with <code>log</code>, <code>die</code>, <code>retry</code> and <code>with_lock</code> functions, all using local variables. Each script became a short <code>main</code> function. When the retry logic needed a fix, one change in the library fixed all nine scripts, and bats tests now check every helper.</p>')}
{talk('Let us look at functions from an expert point of view. Functions run inside the current shell, so they can change variables and even the current folder, unless they run in a subshell such as a pipeline or command substitution. Bash saves and restores the positional parameters around every call. A nameref, made with local dash n, lets a function write into a variable or array the caller names. Export dash f passes a function to child bash processes through the environment. That exact feature was the doorway for the famous Shellshock security bug in 2014, when old versions of bash ran extra commands hidden after a function definition. In language research, bash uses dynamic scope like early Lisp, while most modern languages use lexical scope, which is easier to reason about. For quality, teams test shell functions with tools such as bats, and guard the last line of a script so that tests can load its functions without running main.')}
''', kw=['nameref', 'local -n', 'export -f', 'Shellshock', 'CVE-2014-6271', 'dynamic vs lexical scope', 'bats', 'shUnit2', 'BASH_SOURCE', 'testing shell functions'])

K.quiz('e', 'Which line defines a function called hello?', ['<code>hello: { echo hi }</code>', '<code>hello() { echo hi; }</code>', '<code>def hello: echo hi</code>', '<code>func hello echo hi</code>'], 1, 'Name, brackets, braces.', '<code>name() { commands; }</code> defines a function.')
K.quiz('e', 'Inside a function, what is $1?', ['The first argument of the script', 'The first argument of the function call', 'The function name', 'Always empty'], 1, 'Its own arguments.', 'Each call has its own positional parameters.')
K.quiz('e', 'Which keyword keeps a variable inside its function?', ['my', 'var', 'local', 'private'], 2, 'local.', 'local limits the variable to the function.')
K.quiz('e', 'How do you load functions from lib.sh into the current shell?', ['run lib.sh', 'source lib.sh', 'import lib.sh', 'bash lib.sh'], 1, 'Run it here.', 'source runs the file in the current shell.')
K.quiz('m', 'What is the usual way to get text back from a function?', ['return "text"', 'Print it and use v=$(fn)', 'exit "text"', 'export it'], 1, 'Output.', 'Capture the output with $( ).')
K.quiz('m', 'A function has no return line. What status does it give?', ['Always 0', 'The status of its last command', 'Always 1', '255'], 1, 'Last command.', 'Without return, the last status is used.')
K.quiz('m', 'Without local, what happens when a function sets tmp=5?', ['tmp exists only in the function', 'tmp becomes a global variable', 'It is an error', 'tmp is exported'], 1, 'Global by default.', 'Variables are global unless declared local.')
K.quiz('m', 'Why does main "$@" sit on the last line of a script?', ['It is required by bash', 'It passes all script arguments to main after every function is defined', 'It exports main', 'It makes main local'], 1, 'Defined first, called last.', 'All functions exist by then and the arguments stay intact.')
K.quiz('m', '<code>f() { local x=in; g; }</code>, <code>g() { echo $x; }</code> and x=out. What does f print?', ['out', 'in', 'nothing', 'an error'], 1, 'Dynamic scope.', 'g sees the local x of its caller f.')
K.quiz('h', 'count=0 and <code>bump() { (( count++ )); }</code>. What is count after v=$(bump)?', ['1', '0', '2', 'empty'], 1, 'Subshell.', 'bump ran inside $( ), so the change was lost.')
K.quiz('h', 'What status does a function give after return 256?', ['256', '0', '255', '1'], 1, '8 bits.', '256 mod 256 = 0.')
K.quiz('h', 'Which writes a result into a variable named by the caller?', ['echo > $1', 'printf -v "$1" "%s" "$value"', 'return $1', 'export $1'], 1, 'printf -v.', 'printf -v assigns to the named variable.')
K.quiz('x', 'Which 2014 bug involved bash functions passed through the environment?', ['Heartbleed', 'Shellshock', 'Spectre', 'Log4Shell'], 1, 'CVE-2014-6271.', 'Shellshock ran code after an exported function definition.')

K.calc('e', '<code>f() { echo $#; }</code>. What does f a "b c" d print?', '3', 'Quotes keep one argument.', ['a is one.', '"b c" is one.', eq('a, b c, d = 3')], check=3)
K.calc('e', '<code>square() { echo $(( $1 * $1 )); }</code>. What is $(square 15)?', '225', 'Times itself.', ['15 × 15.', '= 225.', eq('225')], check=225)
K.calc('m', 'fact 6 with the recursive fact function. What is printed?', '720', '6 × 5 × 4 × 3 × 2 × 1.', ['6 × 5 = 30.', '30 × 4 × 3 = 360.', eq('360 × 2 × 1 = 720')], check=720)
K.calc('m', 'fact 6 calls itself until the argument is 1. How many calls of fact happen in total?', '6', 'One per number.', ['fact 6, 5, 4, 3, 2 each call the next.', 'fact 1 stops.', eq('6 calls')], check=6)
K.calc('m', 'A function ends with return 257. What is $? afterwards?', '1', 'Mod 256.', ['Statuses keep 8 bits.', '257 − 256.', eq('1')], check=1)
K.calc('h', 'fib() returns fib(n−1) + fib(n−2), with fib 0 = 0 and fib 1 = 1. What is fib 10?', '55', 'Build up the sequence.', ['0, 1, 1, 2, 3, 5, 8.', '13, 21, 34.', eq('fib 10 = 55')], check=55)

K.must('Define and call', '<code>name() { ...; }</code> or <code>function name { ...; }</code>. Call it like a command. Inside, $1, $# and "$@" are the call’s own arguments.')
K.must('Results', 'Status with return N (0 to 255) for yes or no. Text and numbers by printing and catching with v=$(fn). printf -v NAME to set a variable.')
K.must('Scope', 'Variables are global unless declared local. Scope is dynamic, so a function sees its caller’s locals. $( ) and pipelines run functions in a subshell.')
K.must('Libraries', 'Keep helpers in a file and load it with source. Guard it against double loading. log to stderr, die to log and exit 1.')
K.must('Layout', 'Settings, then functions, then main() and a last line main "$@".')

T = K.topic(
    slug='functions', topic='functions',
    step=(3, 'Functions and data', 'lx-script-3', 'Build scripts from named, tested pieces: functions with local variables, libraries, arrays and option parsing with getopts.', 'Intermediate'),
    title='Functions, scope and libraries', short='Functions', badge='3.1', minutes=50, added='2026-11-23',
    lead='Split scripts into named functions: define and call them, return statuses and values, keep variables local, understand dynamic scope, and share helpers through a sourced library.',
    desc='Defining functions with name() and the function keyword, arguments inside functions, return statuses, returning text with $( ), printf -v, recursion, local variables and dynamic scope, FUNCNAME, functions in subshells, unset -f and declare -F, libraries loaded with source and guarded against double loading, log and die helpers, the main "$@" layout, namerefs, export -f and Shellshock.',
    summary='Functions, return statuses and values, local and dynamic scope, libraries and main "$@".',
    keywords=['function', 'return', 'local', 'scope', 'dynamic scope', 'source', 'library', 'main', 'FUNCNAME', 'recursion', 'printf -v'],
    recap='<p>A function is a named list of commands with its own $1 and "$@". It answers with a status from return or prints a value for $( ). local keeps helper variables private, scope is dynamic, and libraries loaded with source share helpers between scripts.</p>')
