# Shell scripting 1.2: quoting and expansions. Backslash, single, double and $'...' quoting, the order of expansions
# (brace, tilde, parameter, arithmetic, command and process substitution, word splitting, pathname expansion, quote
# removal), parameter expansion operators, command substitution, arithmetic expansion, process substitution and IFS.
# Sources: bash(1) sections QUOTING and EXPANSION (Brace Expansion, Tilde Expansion, Parameter Expansion, Command
# Substitution, Arithmetic Expansion, Process Substitution, Word Splitting, Pathname Expansion, Quote Removal),
# the GNU Bash Reference Manual 3.1.2 and 3.5.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('quotes', 'Four ways to quote', f'''
<p>Many characters mean something special to bash: a space separates words, <code>$</code> starts a variable, <code>*</code> matches file names, <code>|</code> starts a pipe. <b>Quoting</b> switches that meaning off, so the character is just text.</p>
{table(['Quoting', 'What it protects', 'Example', 'Gives'], [
    ['<code>\\x</code> backslash', 'the one next character', '<code>echo \\$5</code>', '$5'],
    ["<code>'...'</code> single quotes", 'everything inside, no exceptions', "<code>echo '$HOME *'</code>", '$HOME *'],
    ['<code>"..."</code> double quotes', 'spaces and wildcards, but $, backquote and backslash still work', '<code>echo "$HOME *"</code>', '/home/learner *'],
    ["<code>$'...'</code> ANSI-C quotes", 'like single quotes, but backslash codes become characters', "<code>echo $'a\\tb'</code>", 'a, a tab, b']])}
{run('Quoting, run for real', """name=Asha
echo Hello    $name    "and    $name"    'and $name'
echo "Price: \\$5, home: $HOME"
echo 'It'"'"'s here'
echo $'tab:\\there' $'two\\nlines'
file="My Report.txt"
touch "$file"
ls -l "$file"
ls $file""", note='Unquoted, the runs of spaces collapse because each space just separates words. Double quotes kept the spaces and expanded $name, single quotes kept $name as text. A single quote cannot appear inside single quotes, so the fourth line closes them, adds a double quoted one and opens them again. Without quotes, the file name became two arguments, My and Report.txt.')}
{note('Rule of thumb: put double quotes around every $variable and $(command), unless you really want the result split into words. Use single quotes for text that must stay exactly as typed, such as awk and sed programs.', 'tip')}
{talk('Bash gives many characters a special job. A space separates words, a dollar sign starts a variable, and a star matches file names. Quoting turns those jobs off. A backslash protects just the next character. Single quotes protect everything between them, so nothing inside changes at all. Double quotes are the everyday choice: they keep spaces and stars as plain text, but they still let dollar signs work, so variables and command substitutions are filled in. The fourth kind, dollar followed by single quotes, works like single quotes but understands codes such as backslash n for a new line and backslash t for a tab. The most common bug in shell scripts is a missing pair of double quotes around a variable. A file name with a space then becomes two separate arguments, as the last line of the example shows. So the safe habit is simple: always write double quotes around dollar variables.')}
''', kw=['quoting', 'single quotes', 'double quotes', 'backslash', "$'...'", 'ANSI-C quoting', 'escape', 'spaces in file names', 'quote a variable'])

K.lesson('order', 'The order of expansions', f'''
<p>After splitting a line into words, bash <b>expands</b> them before running the command. The manual fixes the order. Knowing it explains many surprises.</p>
{steps('What bash does to every command line', [
    '<b>Brace expansion</b>: {a,b} and {1..3} make several words. Pure text, nothing is looked up yet.',
    '<b>Tilde expansion</b>: ~ at the start of a word becomes a home folder.',
    '<b>Parameter, arithmetic and command substitution</b> (and process substitution), from left to right: $name, ${...}, $((...)), $(...), <(...).',
    '<b>Word splitting</b>: unquoted results of the previous step are split at the characters in $IFS (space, tab and newline by default).',
    '<b>Pathname expansion</b>: unquoted words with * ? or [ ] become the matching file names.',
    '<b>Quote removal</b>: the quote characters that are left are removed. The command starts with what remains.'])}
{play('lx-expand')}
{run('The order explains these results', """n=3
echo {1..$n}
seq -s ' ' 1 $n
echo ~ "~" ~root
pattern='*.txt'
echo $pattern
echo "$pattern"
empty=''
printf '[%s]' $empty x "$empty"; echo""", note='Braces run before variables, so {1..$n} saw the text $n and was left alone. seq does the counting instead. Quoted, ~ stays a plain tilde. The pattern stored in a variable is globbed only when unquoted. The unquoted empty variable vanished completely, the quoted one stayed as an empty argument.')}
{note('Globbing happens after variables are expanded, so a file name inside a variable can turn into a list of other files. That is why rm $f is dangerous and rm -- "$f" is safe.', 'warn')}
{talk('Every command line goes through a fixed series of expansions before the command starts, and the bash manual gives the exact order. First comes brace expansion, which is pure text work: a comma list or a range inside braces becomes several words. Second is tilde expansion, where a tilde at the start of a word becomes your home folder. Third, from left to right, bash fills in variables, arithmetic, and the output of commands. Fourth, the results of step three that were not inside double quotes are split into separate words at spaces, tabs and new lines. Fifth, any unquoted word that still has a star, a question mark or square brackets is replaced by matching file names. Last of all, the quote characters themselves are removed. The order explains real puzzles. For example, brace ranges cannot use a variable, because the braces are handled before the variable has a value. Try the animation with your own lines and watch each stage change the words.')}
''', kw=['expansion order', 'brace expansion', 'tilde expansion', 'parameter expansion', 'command substitution', 'arithmetic expansion', 'word splitting', 'pathname expansion', 'globbing', 'quote removal', '{1..$n}'])

K.lesson('params', 'Parameter expansion: editing a value without sed', f'''
<p>Inside <code>${{...}}</code> bash can do much more than read a variable. It can give a default, cut a prefix or suffix, replace text, take a slice or change case. It is fast because no extra program starts.</p>
{cmdtable([
    ('${#v}', 'Length of the value in characters', 'echo ${#name}'),
    ('${v:-word}', 'v, or word when v is unset or empty', 'port=${PORT:-8080}'),
    ('${v:=word}', 'Like :- and also assigns word to v', ': ${LOG:=/tmp/app.log}'),
    ('${v:?message}', 'Stop with an error when v is unset or empty', 'cd "${DIR:?DIR is not set}"'),
    ('${v:+word}', 'word only when v is set and not empty', 'echo ${debug:+-v}'),
    ('${v#pat} ${v##pat}', 'Remove the shortest or longest match from the start', 'echo ${path##*/}'),
    ('${v%pat} ${v%%pat}', 'Remove the shortest or longest match from the end', 'echo ${file%.*}'),
    ('${v/old/new} ${v//old/new}', 'Replace the first match, or every match', 'echo ${s// /_}'),
    ('${v:start:len}', 'A slice, counting from 0. A negative start counts from the end', 'echo ${d:0:4}'),
    ('${v^^} ${v,,} ${v^}', 'Upper case, lower case, capital first letter', 'echo ${name^^}')])}
{run('Taking a path apart', """path=/home/learner/photos/trip.2026.jpg
echo "${#path} characters"
echo "file name: ${path##*/}"
echo "folder:    ${path%/*}"
echo "no ext:    ${path%.*}"
echo "short cut: ${path%%.*}"
echo "extension: ${path##*.}"
name=asha
echo "${name^} ${name^^} ${name:0:3}"
title="report for the year"
echo "${title// /_}"
echo "port ${PORT:-8080}, debug flag [${DEBUG:+-v}]"
for f in notes.txt poem.txt; do echo mv "$f" "${f%.txt}.md"; done""", note='One # or % removes the shortest match, two remove the longest. ${path%%.*} stopped at the first dot. PORT and DEBUG are not set, so :- gave the default and :+ gave nothing. The loop only prints the mv commands, a safe way to preview a bulk rename.')}
{lab('Cut and change values', [
    ('Set the variable <code>file</code> to <code>report.final.txt</code>.', 'file=report.final.txt', [{'env': ['file', 'report.final.txt']}]),
    ('Print the value of file without its last extension.', 'echo ${file%.*}', [{'cmd': r'%'}, {'out': '^report.final$'}]),
    ('Print only the extension of file.', 'echo ${file##*.}', [{'cmd': r'##'}, {'out': '^txt$'}]),
    ('Print the length of the value of file.', 'echo ${#file}', [{'cmd': r'\$\{#file\}'}, {'out': '^16$'}]),
    ('Print the value of file in capital letters.', 'echo ${file^^}', [{'cmd': r'\^\^'}, {'out': '^REPORT.FINAL.TXT$'}]),
    ('The variable town is not set. Print its value with Pune as the default.', 'echo ${town:-Pune}', [{'cmd': r':-'}, {'out': '^Pune$'}]),
    ('Print the value of file with every dot replaced by an underscore.', 'echo ${file//./_}', [{'cmd': r'//'}, {'out': '^report_final_txt$'}])])}
{talk('Parameter expansion lets you edit the value of a variable right inside the dollar and braces, without starting sed or cut. Dollar brace hash name gives the length. A colon and a dash gives a default when the variable is empty, which is the standard way to read optional settings such as a port number. A colon and a question mark stops the script with a clear message when a required variable is missing. The hash and percent forms cut a pattern from the start or the end of the value. One hash or one percent removes the shortest possible match, and two remove the longest. That gives you the file name, the folder or the extension of a path in a single step. A slash replaces text, and two slashes replace every match. Finally, two carets make the value upper case and two commas make it lower case. Because no new program starts, these are much faster than sed inside a loop that runs thousands of times.')}
''', kw=['parameter expansion', '${#var}', '${var:-default}', '${var:=}', '${var:?}', '${var:+}', '${var#}', '${var##}', '${var%}', '${var%%}', '${var/old/new}', 'substring', '${var^^}', 'basename', 'dirname', 'file extension'])

K.lesson('subst', 'Command, arithmetic and process substitution, and IFS', f'''
{cmdtable([
    ('$(command)', 'The output of the command, with trailing newlines removed', 'today=$(date +%F)'),
    ('`command`', 'The old form of $( ). It is hard to nest, so prefer $( )', 'echo `whoami`'),
    ('$((expression))', 'Whole number arithmetic: + - * / % **', 'echo $((7 / 2))'),
    ('<(command)', 'Process substitution: the output as a file name to read', 'diff <(sort a) <(sort b)'),
    ('IFS=: read -r a b', 'Split one line at colons into variables', 'IFS=: read -r user pw uid <<< "$line"')])}
{run('Substitutions, run for real', """echo "I am $(whoami) in $(pwd)"
count=$(ls | wc -l)
echo "$count entries here"
echo "outer $(echo "inner $(echo deepest)")"
echo $((7 / 2)) $((7 % 2)) $((2 ** 10)) $(( (3 + 4) * 2 ))
diff <(head -3 fruits.txt) <(sort fruits.txt | head -3)
echo <(true)
line="root:x:0:0:root:/root:/bin/bash"
IFS=: read -r user pw uid gid rest <<< "$line"
echo "$user has uid $uid and shell ${rest##*:}"
list="a,b,,c"
IFS=,
for x in $list; do echo "[$x]"; done
unset IFS
lines="$(printf 'x\\n\\n\\n')"
echo "[$lines]\"""", note='$( ) nests without escaping. Arithmetic is whole numbers only, so 7 / 2 is 3. diff read two command outputs as if they were files, and echo shows the name bash gave such a file. With IFS set to a comma, splitting kept the empty field between the two commas. Command substitution removed all three trailing newlines.')}
{note('$((...)) has no fractions. For decimals use awk, for example awk "BEGIN { print 7 / 2 }", or bc.', 'tip')}
{talk('Command substitution, written as a dollar and parentheses around a command, runs that command and puts its output into the line. It is how a script stores the date, the number of files, or any result, in a variable. The old form with backquotes does the same thing, but it is awkward to nest, so modern scripts use the dollar and parentheses form. Trailing new lines are removed from the output. Arithmetic expansion, with a dollar and double parentheses, does whole number maths: plus, minus, times, divide, the remainder with percent, and powers with two stars. There are no fractions, so seven divided by two gives three. Process substitution, a less than sign and parentheses, runs a command and hands its output to another command as if it were a file. That is perfect for comparing two command outputs with diff. Finally, IFS, the internal field separator, decides where word splitting and read cut a line. Set it to a colon to read a line of the password file, and unset it again afterwards to return to the normal spaces, tabs and new lines.')}
''', kw=['command substitution', '$(...)', 'backticks', 'arithmetic expansion', '$((...))', 'integer arithmetic', 'process substitution', '<(...)', 'IFS', 'field separator', 'read with IFS', 'word splitting'])

K.lesson('levels', 'Expansions from school to research', f'''
{ladder(
    '<p>Before a command runs, bash replaces parts of the line: braces, ~, $variables, $(commands) and wildcards. Quotes decide what may be replaced. Double quotes around variables keep values with spaces in one piece.</p>',
    '<p>The order is fixed: brace, tilde, then parameter, arithmetic and command substitution from left to right, then word splitting with IFS, pathname expansion and quote removal. Only results that were not in double quotes are split and globbed, which is why "$var" is safe and $var is not.</p>',
    '<p>Word splitting treats IFS white space and other IFS characters differently: runs of white space count as one separator and are trimmed at the ends, while each other character such as a colon ends a field, so a::b gives an empty field. Command substitution runs in a subshell, so variables set inside it are lost. set -f turns pathname expansion off, and shopt -s nullglob makes a pattern with no match disappear instead of staying as text.</p>',
    '<p>The POSIX standard defines these steps in its Shell Command Language chapter, and the Smoosh project (Greenberg and Blatt, POPL 2020) turned them into an executable formal model that was tested against real shells. It found places where shells disagree with the standard and with each other. Static analysers such as ShellCheck flag unquoted expansions (warning SC2086) because word splitting and globbing of data is a frequent source of bugs and security holes.</p>')}
{scene('the file with a space', '<p>A nightly cleanup script ran <code>rm $old</code> on a file called <code>backup 2026.tar</code>. Word splitting turned it into two arguments, backup and 2026.tar, and the script deleted an unrelated file called backup. The fix was one pair of quotes: <code>rm -- "$old"</code>. The team added ShellCheck to their CI so the same mistake is caught before a merge.</p>')}
{talk('Here is the deeper picture. The bash manual and the POSIX standard both describe the same pipeline of expansions, and the only words that are split and globbed are the ones produced by unquoted expansions. Splitting follows IFS. Spaces, tabs and new lines in IFS are grouped and trimmed, while any other character, such as a colon, ends a field each time it appears, so two colons in a row give an empty field. Command substitution runs in a subshell, so it cannot change variables in your script. Two options change globbing: set dash f turns it off, and the nullglob option makes a pattern with no match vanish. Researchers built a formal model of all these rules, called Smoosh, and tested it against real shells, finding cases where the shells disagree. In practice, the lesson from all this work is the same as on day one: quote your variables, and let ShellCheck remind you when you forget.')}
''', kw=['POSIX shell expansion', 'IFS white space', 'empty field', 'subshell', 'set -f', 'nullglob', 'Smoosh', 'ShellCheck SC2086', 'rm with spaces'])

K.quiz('e', 'What does echo \'$HOME\' print?', ['/home/learner', '$HOME', 'HOME', 'nothing'], 1, 'Single quotes.', 'Nothing is expanded inside single quotes.')
K.quiz('e', 'What does echo "$HOME" print?', ['/home/learner', '$HOME', '"$HOME"', 'HOME'], 0, 'Double quotes.', 'Variables are expanded inside double quotes.')
K.quiz('e', 'Which quoting keeps a file name with a space as one argument and still expands the variable?', ['None', '"$file"', "'$file'", '$file'], 1, 'Quote variables.', 'Double quotes keep spaces and expand $file.')
K.quiz('e', 'What does $(whoami) do inside a command?', ['Prints the word whoami', 'Puts the output of whoami into the line', 'Runs whoami in the background', 'Nothing'], 1, 'Command substitution.', 'The output replaces the $( ).')
K.quiz('m', 'n=3. What does echo {1..$n} print?', ['1 2 3', '{1..3}', '1..3', 'an error'], 1, 'Braces come first.', 'Brace expansion runs before $n is expanded, so the braces are left alone.')
K.quiz('m', 'path=/a/b/c.tar.gz. What is ${path##*/}?', ['/a/b', 'c.tar.gz', 'c', 'gz'], 1, 'Longest from the start.', '##*/ removes everything up to the last slash.')
K.quiz('m', 'file=c.tar.gz. What is ${file%.*}?', ['c', 'c.tar', 'gz', 'tar.gz'], 1, 'Shortest from the end.', '% removes the shortest match, .gz.')
K.quiz('m', 'What does echo $((7 / 2)) print?', ['3.5', '3', '4', 'an error'], 1, 'Whole numbers.', 'Shell arithmetic drops the fraction.')
K.quiz('m', 'Which operator stops a script with a message when a variable is empty?', ['${v:-msg}', '${v:+msg}', '${v:?msg}', '${v:=msg}'], 2, 'Question mark.', ':? prints the message and stops.')
K.quiz('h', 'Which step happens last of these?', ['Word splitting', 'Pathname expansion', 'Brace expansion', 'Parameter expansion'], 1, 'Wildcards late.', 'Pathname expansion comes after word splitting.')
K.quiz('h', 'IFS=: and line="a::b". How many words does $line give when unquoted?', ['2', '3', '1', '4'], 1, 'Each colon ends a field.', 'a, an empty field and b.')
K.quiz('h', 'What does diff <(sort a) <(sort b) give diff as arguments?', ['The sorted text', 'Two file names such as /dev/fd/63 and /dev/fd/62', 'The words sort a and sort b', 'Nothing'], 1, 'Process substitution.', 'Each <( ) becomes a file name to read from.')
K.quiz('x', 'Why is count set inside $(count=5) lost afterwards?', ['It is a syntax error', 'Command substitution runs in a subshell', 'count is read only', 'It is not lost'], 1, 'Child process.', 'Changes inside a subshell do not reach the parent.')

K.calc('e', 'name=Asha. What is ${#name}?', '4', 'Count the characters.', ['A, s, h, a.', 'Four characters.', eq('4')], check=4)
K.calc('e', 'What does $((2 ** 10)) give?', '1024', 'Power.', ['** is a power.', '2 to the power 10.', eq('2^10 = 1024')], check=1024)
K.calc('m', 'What does $(( (3 + 4) * 2 - 5 % 3 )) give?', '12', 'Brackets, then *, then %, then −.', ['3 + 4 = 7.', '7 × 2 = 14 and 5 % 3 = 2.', eq('14 − 2 = 12')], check=12)
K.calc('m', 'd=2026-11-23. Using ${d:5:2}, which number is the month?', '11', 'Start at 5, take 2.', ['Characters 0 to 3 are 2026, 4 is a dash.', 'Characters 5 and 6 are 11.', eq('11')], check=11)
K.calc('m', 'echo {a,b}{1,2,3} prints how many words?', '6', 'Every pair.', ['2 choices in the first braces.', '3 choices in the second.', eq('2 × 3 = 6')], check=6)
K.calc('h', 'IFS=, and list="x,,y,". How many fields does unquoted $list give?', '3', 'A final comma adds no empty field.', ['x, then an empty field between the two commas.', 'Then y. The last comma only ends y.', eq('3 fields')], check=3)

K.must('Quoting', 'Single quotes keep everything literal, double quotes keep spaces and wildcards but expand $ and $( ), a backslash protects one character, $\'...\' understands codes like a tab.')
K.must('Order', 'Brace, tilde, then parameter, arithmetic and command substitution, then word splitting, pathname expansion and quote removal.')
K.must('Quote variables', 'Write "$var" and "$(cmd)". Unquoted results are split at IFS and globbed, so spaces and * in data break the command.')
K.must('Parameter expansion', '${#v} length, ${v:-d} default, ${v:?msg} required, ${v#p} ${v##p} cut from the start, ${v%p} ${v%%p} cut from the end, ${v//a/b} replace, ${v:s:n} slice, ${v^^} ${v,,} case.')
K.must('Substitution', '$(cmd) output (trailing newlines removed), $((expr)) whole number maths, <(cmd) output as a file name, IFS sets where splitting and read cut.')

T = K.topic(
    slug='expansions', topic='expansions',
    step=(1, 'Writing scripts', 'lx-script-1', 'Turn commands into reusable scripts: the shebang, arguments, exit statuses, input and output, and how the shell expands every word.', 'Intermediate'),
    title='Quoting and expansions', short='Expansions', badge='1.2', minutes=50, added='2026-11-23',
    lead='See exactly what bash does to a command line before it runs: four kinds of quoting, the fixed order of expansions, parameter expansion to cut and change values, command, arithmetic and process substitution, and IFS.',
    desc='Backslash, single, double and ANSI-C quoting, the order of expansions from the bash manual, brace and tilde expansion, word splitting with IFS, pathname expansion, quote removal, parameter expansion operators for defaults, prefixes, suffixes, replacement, slices and case, command substitution, arithmetic expansion and process substitution.',
    summary='Quoting, the order of expansions, ${...} operators, $( ), $(( )), <( ) and IFS.',
    keywords=['quoting', 'expansion', 'parameter expansion', 'word splitting', 'IFS', 'command substitution', 'arithmetic expansion', 'process substitution', 'brace expansion', 'globbing'],
    recap='<p>Bash expands a line in a fixed order: braces, tilde, variables and substitutions, word splitting, wildcards and quote removal. Double quotes stop splitting and globbing, and ${...} edits values without extra programs.</p>')
