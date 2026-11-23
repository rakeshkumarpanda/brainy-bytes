# Shell scripting 2.1: decisions. if, then, elif, else and fi with any command as the condition, test and [ ] with
# file, string and number operators and their argument-count rules, [[ ]] with patterns, =~ and BASH_REMATCH, (( ))
# for numbers, && and || chains, and case with patterns, |, ;;, ;& and ;;&. Sources: bash(1) sections Compound
# Commands (if, case, [[ ]], (( ))), CONDITIONAL EXPRESSIONS, ARITHMETIC EVALUATION and the test builtin, the GNU
# Bash Reference Manual 3.2.5.2 and 6.4, and POSIX test(1).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('if', 'if, elif and else: decisions by exit status', f'''
<p><code>if</code> runs a command and looks only at its <b>exit status</b>. Status 0 means true and runs the <code>then</code> part. Anything else tries the next <code>elif</code>, then <code>else</code>. The block ends with <code>fi</code>, which is if backwards.</p>
{shape('if, elif and else', """if COMMAND; then
  ...            # runs when COMMAND exits with 0
elif OTHER; then
  ...            # runs when COMMAND failed and OTHER succeeded
else
  ...            # runs when everything above failed
fi""")}
{run('Any command can be the condition', """if grep -q apple fruits.txt; then
  echo "we have apples"
fi
if ! grep -q pear fruits.txt; then
  echo "no pears today"
fi
if mkdir reports 2>/dev/null; then
  echo "made reports"
else
  echo "reports already exists"
fi
mkdir reports 2>/dev/null && echo "made it" || echo "could not make it"
count=$(grep -c apple fruits.txt)
if [ "$count" -ge 3 ]; then
  echo "plenty: $count"
elif [ "$count" -ge 1 ]; then
  echo "a few: $count"
else
  echo "none"
fi""", note='grep -q gives only a status, which is perfect for if. ! turns success into failure and back. The second mkdir failed because the folder now exists. The fruit list has the word apple on 3 lines, so the first branch ran.')}
{note('a && b || c is not a full if. If b itself fails, c runs too. Use a real if when the middle command can fail.', 'warn')}
{talk('The if statement in bash works differently from most languages. It does not test a true or false value. It runs a command and looks at the exit status. Zero means success, so the then part runs. Any other status moves on to the next elif, and finally to else. The block always ends with the word fi, which is if spelled backwards. Because any command can be the condition, you can write if grep dash q apple fruits dot t x t, and the block runs only when the word is found. An exclamation mark in front reverses the result. You will often see the short form with double ampersand and double bar. It reads well, but it has a trap: if the middle command fails, the last one runs as well. So use a proper if whenever the middle command might fail.')}
''', kw=['if', 'then', 'elif', 'else', 'fi', 'condition', 'exit status', 'grep -q', '! negation', '&& ||', 'if statement'])

K.lesson('test', 'test and [ ]: files, strings and numbers', f'''
<p>The command <code>test</code>, also written <code>[ ... ]</code>, checks one condition and exits with 0 for true or 1 for false. Because <code>[</code> is a command, it needs a space after it and a space before the final <code>]</code>.</p>
{table(['Group', 'Operator', 'True when'], [
    ['Files', '<code>-e f</code>, <code>-f f</code>, <code>-d f</code>, <code>-L f</code>', 'f exists, is a regular file, is a folder, is a symbolic link'],
    ['Files', '<code>-r f</code>, <code>-w f</code>, <code>-x f</code>, <code>-s f</code>', 'you may read, write or run f, f is not empty'],
    ['Files', '<code>a -nt b</code>, <code>a -ot b</code>', 'a is newer than b, older than b'],
    ['Strings', '<code>-z s</code>, <code>-n s</code>', 's is empty, s is not empty'],
    ['Strings', '<code>a = b</code>, <code>a != b</code>', 'the texts are equal, not equal'],
    ['Numbers', '<code>-eq -ne -lt -le -gt -ge</code>', 'equal, not equal, less, less or equal, greater, greater or equal'],
    ['Combine', '<code>! expr</code>, <code>[ a ] && [ b ]</code>, <code>[ a ] || [ b ]</code>', 'not, and, or (prefer && and || between two tests to -a and -o)']])}
{play('lx-test')}
{run('Tests, run for real', """[ -f notes.txt ] && echo "notes.txt is a file"
[ -d logs ] && echo "logs is a folder"
[ -x notes.txt ] || echo "notes.txt is not executable"
n=12
[ "$n" -gt 10 ]; echo "12 > 10: status $?"
[ "$n" -lt 10 ]; echo "12 < 10: status $?"
[ "10" = "10.0" ]; echo "string 10 = 10.0: status $?"
[ 10 -eq 10 ]; echo "number 10 -eq 10: status $?"
empty=""
[ -z "$empty" ] && echo "empty is empty"
[ $empty = yes ]
[ "$empty" = yes ]; echo "quoted: status $?"
[ "$n" -gt 10 ] && [ "$n" -lt 20 ] && echo "between 10 and 20"
[ abc -eq 1 ]""", note='= compares text, so 10 and 10.0 differ, while -eq compares numbers. The unquoted empty variable vanished, so test saw only = yes and complained. With quotes it worked and simply returned 1. Status 2 means test itself could not understand the question.')}
{note('Write [ "$x" = y ], always with quotes. Use = and != for text, -eq and -lt for whole numbers. [ 9 > 10 ] is not a comparison at all: it redirects output into a file called 10.', 'warn')}
{talk('The test command checks a single condition. You can write it as the word test, but almost everyone uses the square bracket form. The opening bracket is actually the name of a command, so the spaces around it are required, just like spaces between any command and its arguments. There are three families of checks. File checks such as dash f for a regular file, dash d for a folder and dash x for executable. String checks: dash z for empty, dash n for not empty, and equals and not equals. Number checks use letters: dash e q for equal, dash l t for less than and dash g t for greater than. Mixing them up is a classic bug, because equals compares text, so ten and ten point zero are different. Because the bracket is a normal command, its arguments go through word splitting first. An empty variable without quotes simply disappears, and test then sees the wrong number of arguments. The animation shows exactly how that happens. The cure is always the same: put double quotes around every variable inside single brackets.')}
''', kw=['test', '[ ]', '-f', '-d', '-e', '-z', '-n', '-eq', '-lt', '-gt', 'string comparison', 'number comparison', 'unary operator expected', 'file tests'])

K.lesson('dbl', 'The bash way: [[ ]] and (( ))', f'''
<p>bash adds two safer forms. <code>[[ ... ]]</code> is a <b>keyword</b>, not a command, so there is no word splitting and no globbing inside it. It also understands patterns, regular expressions and <code>&&</code> and <code>||</code>. <code>(( ... ))</code> evaluates whole number arithmetic with C-like operators and is true when the result is not 0.</p>
{table(['', '[ ] (test)', '[[ ]]', '(( ))'], [
    ['What it is', 'a command, POSIX', 'a bash keyword', 'a bash keyword'],
    ['Empty unquoted variable', 'breaks the test', 'safe', 'counts as 0'],
    ['Text', '<code>=</code> <code>!=</code>', '<code>==</code> <code>!=</code> with patterns, <code><</code> <code>></code> sort order', 'not for text'],
    ['Regular expressions', 'no', '<code>=~</code>, groups in BASH_REMATCH', 'no'],
    ['Numbers', '<code>-lt -gt ...</code>', '<code>-lt -gt ...</code>', '<code>< > <= >= == !=</code>, <code>+ - * / % **</code>'],
    ['And, or', 'two tests with && ||', '<code>&&</code> <code>||</code> inside', '<code>&&</code> <code>||</code> inside']])}
{run('Patterns, regular expressions and arithmetic', """empty=""
[[ $empty = yes ]]; echo "empty with [[ ]]: status $?"
file="holiday photo.JPG"
[[ $file == *.jpg ]] && echo "lower-case jpg" || echo "not *.jpg"
[[ ${file,,} == *.jpg ]] && echo "a jpg in any case"
[[ $file == "*.JPG" ]] || echo "a quoted pattern is plain text"
date="2026-11-23"
if [[ $date =~ ^([0-9]{4})-([0-9]{2})-([0-9]{2})$ ]]; then
  echo "year ${BASH_REMATCH[1]}, month ${BASH_REMATCH[2]}, day ${BASH_REMATCH[3]}"
fi
[[ apple < banana ]] && echo "apple sorts before banana"
n=17
(( n > 10 && n % 2 == 1 )) && echo "$n is big and odd"
(( n % 2 == 0 )); echo "is 17 even: status $?"
(( count = n * 2 )); echo "count=$count"
(( 0 )); echo "(( 0 )) gives status $?\"""", note='Inside [[ ]] the empty variable caused no error. Patterns after == are case sensitive, so the lower-cased copy ${file,,} matched. Quoting the right side turns the pattern into plain text. BASH_REMATCH holds the whole match at index 0 and each bracket group after it. (( )) can also assign, and a result of 0 means false.')}
{note('Use [[ ]] and (( )) in bash scripts. Use [ ] only when the script must run under plain sh (#!/bin/sh), because dash has no [[ ]].', 'tip')}
{talk('Bash gives you two better tools for conditions. Double square brackets are a keyword that the shell understands directly, so it does not split variables or expand stars inside. That makes empty and spaced values safe, even without quotes. Inside double brackets, double equals compares with a pattern, so star dot j p g matches any file ending in dot j p g. Equals tilde matches a regular expression, and every bracket group you capture lands in an array called BASH REMATCH. You can also join tests with double ampersand and double bar inside the brackets. For numbers, double parentheses let you write maths the way you learned it at school, with greater than, less than, and the percent sign for the remainder. The result counts as true when it is not zero. One caution: these are bash features, so a script that starts with hash bang slash bin slash s h cannot use them.')}
''', kw=['[[ ]]', '(( ))', 'pattern matching', '==', '=~', 'BASH_REMATCH', 'regular expression', 'arithmetic condition', 'string sort order', 'test vs [['])

K.lesson('case', 'case: choose by pattern', f'''
<p>When one value can take many forms, <code>case</code> is clearer than a long elif chain. bash tries the patterns from top to bottom and runs the first arm that matches.</p>
{shape('case', """case "$answer" in
  y|yes|Y)  echo "go on" ;;
  n*|N*)    echo "stop" ;;
  "")       echo "no answer" ;;
  *)        echo "please answer y or n" ;;
esac""")}
{table(['Arm ending', 'Effect'], [
    ['<code>;;</code>', 'stop after this arm (the normal case)'],
    ['<code>;&</code>', 'also run the next arm without testing its pattern (bash 4 and later)'],
    ['<code>;;&</code>', 'keep testing the following patterns and run any that match (bash 4 and later)']])}
{play('lx-case')}
{run('case in a small service script', """cat > svc.sh <<'EOF'
#!/bin/bash
case "$1" in
  start)        echo "starting the service" ;;
  stop)         echo "stopping the service" ;;
  restart)      echo "stopping"; echo "starting" ;;
  status|st)    echo "running" ;;
  *)            echo "usage: $0 {start|stop|restart|status}" >&2; exit 2 ;;
esac
EOF
bash svc.sh start
bash svc.sh st
bash svc.sh reload; echo "status $?"
for f in a.jpg b.TXT c.tar.gz notes; do
  case $f in
    *.jpg|*.png)   echo "$f: image" ;;
    *.[tT][xX][tT]) echo "$f: text" ;;
    *.tar.*)       echo "$f: archive" ;;
    *)             echo "$f: unknown" ;;
  esac
done
case abc in a*) echo "starts with a" ;;& *c) echo "ends with c" ;; esac""", note='The script picks one arm by its first argument, and the catch-all *) prints a usage message to stderr with status 2. With <code>;;&amp;</code> the second pattern was tested too, so both lines printed.')}
{lab('Make decisions', [
    ('Set the variable n to 15.', 'n=15', [{'env': ['n', '15']}]),
    ('With [ ] and -gt, print yes only when n is greater than 10.', '[ "$n" -gt 10 ] && echo yes', [{'cmd': r'\[\s.*-gt'}, {'out': '^yes$'}]),
    ('Print found only when notes.txt is a regular file.', '[ -f notes.txt ] && echo found', [{'cmd': r'-f\s+notes\.txt'}, {'out': '^found$'}]),
    ('In one line, set file to photo.jpg and use [[ ]] with the pattern *.jpg to print image.', 'file=photo.jpg; [[ $file == *.jpg ]] && echo image', [{'cmd': r'\[\['}, {'out': '^image$'}]),
    ('With (( )) and the remainder operator, print odd when n is odd.', '(( n % 2 )) && echo odd', [{'cmd': r'\(\(.*%'}, {'out': '^odd$'}]),
    ('Write an if with elif and else that prints big when n is over 20, medium when it is over 10, and small otherwise.', 'if (( n > 20 )); then echo big; elif (( n > 10 )); then echo medium; else echo small; fi', [{'cmd': r'^\s*if\b.*\belif\b.*\belse\b'}, {'out': '^medium$'}]),
    ('Use case on $n so that two-digit numbers starting with 1 print teen and everything else prints other.', 'case $n in 1?) echo teen ;; *) echo other ;; esac', [{'cmd': r'^\s*case\b'}, {'out': '^teen$'}])])}
{talk('The case statement chooses between many possibilities by pattern. You give it one value, then a list of arms. Each arm starts with a pattern and a closing parenthesis, followed by the commands, and ends with two semicolons. Bash tests the patterns from the top and runs only the first arm that matches, so put specific patterns first and the catch all star last. A vertical bar lets one arm accept several patterns, such as y or yes. The patterns are the same wildcards you use for file names, so star dot j p g matches every JPEG name. That makes case the natural choice for service scripts that accept start, stop and restart, and for sorting files by type. Two less common endings exist: semicolon ampersand runs the next arm as well, and two semicolons with an ampersand keeps testing the remaining patterns.')}
''', kw=['case', 'esac', 'pattern', ';;', ';&', ';;&', '*)', 'catch-all', 'service script', 'start stop restart', 'usage message'])

K.lesson('levels', 'Decisions from school to research', f'''
{ladder(
    '<p>if runs a command and checks whether it worked. [ ] asks a question about a file, some text or a number. case picks one action from a list of patterns. fi and esac close the blocks.</p>',
    '<p>The condition of if, while and until is a list of commands, and only the status of the last one counts. test decides by the number of arguments it receives, which is why unquoted empty variables break it. [[ ]] and (( )) are parsed by bash itself, so their contents are not split or globbed.</p>',
    '<p>Inside [[ ]], quoting the right side of == or =~ makes it literal text, so keep a regular expression in a variable, re="^[0-9]+$", and write [[ $x =~ $re ]]. The bash option nocasematch makes [[ ]] and case ignore letter case. A number in (( )) with a leading 0 is octal, so (( 08 )) is an error, while 10#08 forces base 10. errexit (set -e) ignores failures inside if conditions and in all but the last command of && and || lists.</p>',
    '<p>The POSIX test rules by argument count were written to make test predictable, but parsing operators and operands from the same words stays ambiguous, for example in [ "$a" = -n ]. Research on shell semantics such as Smoosh and studies of real-world scripts report condition errors and quoting mistakes among the most common bugs, and linters such as ShellCheck include dedicated checks (SC2070, SC2071, SC2086) for them.</p>')}
{scene('the deployment gate', '<p>A release script must stop when the disk is nearly full or when the branch is not main. It uses <code>[[ $(git branch --show-current) == main ]] || { echo "deploy only from main" >&2; exit 1; }</code> and <code>(( usage < 90 ))</code> on the percentage that df reports. A case statement maps the first argument to staging or production, with a usage message in the *) arm. Every rule is a single readable line, and a wrong value stops the deploy before anything changes.</p>')}
{talk('Here is the expert view of decisions. The condition of if is really a list of commands, and only the status of the last one matters. The test command decides what to do by counting its arguments, which explains every unary operator expected message you will ever see. Double brackets and double parentheses are read by bash itself, so their contents are never split or globbed. A few traps remain. If you quote the right side of a regular expression match, it becomes plain text, so store the expression in a variable instead. Numbers with a leading zero are octal inside double parentheses, so eight with a leading zero is an error unless you write ten hash before it. And the set dash e option ignores failures inside conditions, which surprises many people. Linters such as ShellCheck carry dedicated warnings for these mistakes, because studies of real scripts find them again and again.')}
''', kw=['condition list', 'test argument count', 'regex in a variable', 'nocasematch', 'octal in (( ))', '10#08', 'set -e and if', 'ShellCheck', 'deployment check'])

K.quiz('e', 'Which word closes an if block?', ['end', 'done', 'fi', 'esac'], 2, 'if backwards.', 'if ... fi.')
K.quiz('e', 'What does if look at to decide?', ['The output of the command', 'The exit status of the command', 'The length of the line', 'The current folder'], 1, 'Status 0 is true.', 'if checks the exit status.')
K.quiz('e', 'Which test is true when notes.txt is a folder?', ['[ -f notes.txt ]', '[ -d notes.txt ]', '[ -x notes.txt ]', '[ -z notes.txt ]'], 1, 'd for directory.', '-d tests for a folder.')
K.quiz('e', 'Why is [-f notes.txt] wrong?', ['-f does not exist', '[ needs spaces around it because it is a command name', 'notes.txt needs quotes', 'It is correct'], 1, 'Spaces.', '[ is a command and must be its own word.')
K.quiz('m', 'Which compares two whole numbers?', ['[ "$a" = "$b" ]', '[ "$a" -eq "$b" ]', '[ "$a" == "$b" ]', '[ "$a" -n "$b" ]'], 1, 'Letters for numbers.', '-eq compares numbers.')
K.quiz('m', 'x is empty. What does [ $x = yes ] print?', ['nothing, status 1', 'an error: unary operator expected', 'yes', 'status 0'], 1, 'The variable vanished.', 'test sees only = and yes.')
K.quiz('m', 'Which test matches every name ending in .log?', ['[ $f = *.log ]', '[[ $f == *.log ]]', '[[ $f == "*.log" ]]', '(( f == *.log ))'], 1, 'Unquoted pattern in [[ ]].', '== in [[ ]] matches a pattern.')
K.quiz('m', 'After [[ 2026-11 =~ ^([0-9]+)-([0-9]+)$ ]], what is ${BASH_REMATCH[2]}?', ['2026', '11', '2026-11', 'empty'], 1, 'Second group.', 'Index 2 is the second bracket group.')
K.quiz('m', 'In case, which pattern catches every other value?', ['else)', 'default)', '*)', '?)'], 2, 'A star matches anything.', '*) is the catch-all arm.')
K.quiz('h', 'a && b || c. When does c run?', ['Only when a fails', 'When a fails or when b fails', 'Never', 'Always'], 1, 'Not a real if.', 'c runs after any failure of the && part.')
K.quiz('h', 'What does [ 9 > 10 ] do?', ['Compares 9 and 10', 'Runs [ 9 ] and writes its output to a file called 10', 'Gives a syntax error', 'Compares text'], 1, 'Redirection.', '> is a redirection outside [[ ]].')
K.quiz('h', 'Which arm ending tests the next patterns too?', ['<code>;;</code>', '<code>;&amp;</code>', '<code>;;&amp;</code>', '<code>&amp;&amp;</code>'], 2, 'bash 4.', '<code>;;&amp;</code> keeps testing.')
K.quiz('x', 'Why does (( 08 + 1 )) fail?', ['08 is too big', 'A leading 0 means octal, and 8 is not an octal digit', '(( )) cannot add', 'Spaces are wrong'], 1, 'Base 8.', 'Use 10#08 to force base 10.')

K.calc('e', 'n=7. What status does [ "$n" -gt 5 ] give?', '0', 'True gives 0.', ['7 > 5 is true.', 'True means status 0.', eq('0')], check=0)
K.calc('e', 'n=7. What status does (( n % 2 == 0 )) give?', '1', 'Is 7 even?', ['7 % 2 = 1.', '1 == 0 is false.', eq('false gives status 1')], check=1)
K.calc('m', 'n=17. What does (( n * 2 - 4 )) compute, and is it true?', '30', 'Times first.', ['17 × 2 = 34.', '34 − 4 = 30.', eq('30, not zero, so true')], check=30)
K.calc('m', 'x is empty. How many arguments does [ $x = yes ] give the [ command, counting the final ]?', '3', 'The empty variable vanishes.', ['Words after [: $x, =, yes, ].', '$x is empty and unquoted, so it disappears.', eq('=, yes and ] are 3')], check=3)
K.calc('m', 'A case has 5 arms and the value matches arms 2 and 4. How many arms run when every arm ends with <code>;;</code>?', '1', 'First match only.', ['Arm 2 matches first.', '<code>;;</code> stops the case.', eq('1 arm')], check=1)
K.calc('h', 'What is 10#010 + 010 in (( ))?', '18', 'One is base 10, one is octal.', ['10#010 is ten.', '010 is octal, which is 8.', eq('10 + 8 = 18')], check=18)

K.must('if', '<code>if CMD; then ...; elif CMD; then ...; else ...; fi</code>. The condition is a command, status 0 is true, ! reverses it.')
K.must('test and [ ]', 'Spaces inside the brackets. Files -e -f -d -r -w -x -s, text = != -z -n, numbers -eq -ne -lt -le -gt -ge. Quote every variable.')
K.must('[[ ]]', 'No splitting or globbing inside. == with an unquoted pattern, =~ with a regular expression and BASH_REMATCH, && and || inside.')
K.must('(( ))', 'Whole number maths with < > == % and friends. True when the result is not 0. A leading 0 means octal.')
K.must('case', '<code>case "$v" in pat1|pat2) ... ;; *) ... ;; esac</code>. First match wins. <code>;&amp;</code> falls through, <code>;;&amp;</code> keeps testing.')

T = K.topic(
    slug='conditions', topic='conditions',
    step=(2, 'Decisions and loops', 'lx-script-2', 'Let scripts choose and repeat: if, test, [[ ]], (( )) and case, then for, while and until loops over files, lines and numbers.', 'Intermediate'),
    title='Decisions: if, test and case', short='Decisions', badge='2.1', minutes=50, added='2026-11-23',
    lead='Make scripts decide: if with any command as the condition, test and [ ] for files, text and numbers, the safer [[ ]] and (( )), and case for choosing by pattern.',
    desc='if, then, elif, else and fi, exit status as the condition, ! to negate, && and || chains and their trap, test and [ ] with file, string and number operators and the argument-count rules, quoting inside [ ], [[ ]] with patterns, =~ and BASH_REMATCH, (( )) arithmetic conditions, octal numbers, and case with patterns, choices and the three kinds of arm ending.',
    summary='if and exit statuses, test and [ ], [[ ]] and (( )), and case.',
    keywords=['if', 'elif', 'test', '[ ]', '[[ ]]', '(( ))', 'case', 'condition', 'BASH_REMATCH', 'file test', 'string comparison', 'number comparison'],
    recap='<p>if runs a command and checks its exit status. [ ] tests files, text and numbers but needs quoted variables, [[ ]] adds patterns and regular expressions safely, (( )) does maths, and case picks the first matching pattern.</p>')
