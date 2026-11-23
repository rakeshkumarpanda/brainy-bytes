# Shell scripting 2.2: loops. for over words, globs, braces and "$@", the C-style for (( )), while and until,
# reading a file line by line with while IFS= read -r, IFS for fields, reading command output with < <( ), the pipe
# subshell trap, break and continue with levels, redirecting a whole loop, nullglob, find -print0 with read -d '',
# select menus. Sources: bash(1) sections Compound Commands (for, while, until, select), SHELL BUILTIN COMMANDS
# (read, break, continue, shopt), Pipelines (each command in a pipeline runs in a subshell), the GNU Bash Reference
# Manual 3.2.5.1 and 4.3.2.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('for', 'for loops: one pass per item', f'''
<p>A <code>for</code> loop runs its body once for every word in a list. bash builds the whole list first, using all the usual expansions, and then sets the loop variable to each word in turn.</p>
{shape('Two kinds of for loop', """for NAME in WORD1 WORD2 ...; do
  ...                  # $NAME is each word in turn
done

for (( INIT; TEST; STEP )); do
  ...                  # runs while TEST is not 0
done""")}
{table(['List', 'Gives', 'Example'], [
    ['plain words', 'exactly those words', '<code>for c in red green blue</code>'],
    ['a glob', 'the matching file names, sorted', '<code>for f in *.csv</code>'],
    ['braces', 'a range or a set', '<code>for n in {1..10}</code>'],
    ['<code>"$@"</code>', 'every argument of the script', '<code>for arg in "$@"</code> (or just <code>for arg</code>)'],
    ['<code>$(command)</code>', 'the output, split into words', '<code>for u in $(cut -d: -f1 /etc/passwd)</code>']])}
{play('lx-loop')}
{run('for loops, run for real', """for city in Pune "New Delhi" Chennai; do
  echo "visiting $city"
done
for f in *.txt; do
  echo "$f has $(wc -l < "$f") lines"
done
for n in {1..5}; do printf '%d ' $((n * n)); done; echo
for (( i = 10; i > 0; i -= 4 )); do echo "countdown $i"; done
for f in *.xyz; do echo "found [$f]"; done
shopt -s nullglob
for f in *.xyz; do echo "found [$f]"; done
echo "after the loop f is still [$f]\"""", note='The quotes kept New Delhi as one item. *.txt was sorted alphabetically. With no matching file, *.xyz stayed as literal text and the loop ran once with it. After shopt -s nullglob the pattern vanished and the loop did not run at all. The loop variable keeps the last value it had.')}
{note('Do not loop over $(ls) or $(cat file). File names with spaces are split into pieces. Use a glob for files and while read for lines.', 'warn')}
{talk('A for loop repeats its body once for every item in a list. Bash builds the list first with all the usual expansions, so you can give plain words, a wildcard pattern that becomes file names, a brace range such as one dot dot ten, or dollar at sign in quotes for every argument of the script. Then the loop variable takes each item in turn, and the body between do and done runs once per item. There is also a second form borrowed from the C language, with double parentheses and three parts: a start, a test and a step, which is handy for counting. One surprise: if a pattern such as star dot x y z matches no file, bash keeps the pattern as plain text and the loop runs once with it. The nullglob option fixes that by removing patterns that match nothing. Try the animation with your own list and body to watch every pass.')}
''', kw=['for loop', 'for in', 'do done', 'C-style for', 'for (( ))', 'loop over files', 'glob in for', 'brace range', 'nullglob', 'for arg in "$@"'])

K.lesson('while', 'while and until, and reading files line by line', f'''
<p><code>while</code> repeats as long as its condition command succeeds. <code>until</code> repeats as long as it fails. The most common use of while is reading input one line at a time.</p>
{cmdtable([
    ('while CMD; do ...; done', 'Repeat while CMD exits with 0', 'while (( n < 5 )); do ...; done'),
    ('until CMD; do ...; done', 'Repeat until CMD exits with 0', 'until ping -c1 host; do sleep 5; done'),
    ('while true; do ...; done', 'Repeat for ever, leave with break', 'while true; do read -r cmd || break; done'),
    ('while IFS= read -r line; do ...; done < file', 'One pass per line, the line kept exactly', 'while IFS= read -r line; do echo "$line"; done < notes.txt'),
    ('while IFS=, read -r a b c; do ...; done < file.csv', 'Split each line into fields', 'while IFS=, read -r name subj score; do ...; done < marks.csv'),
    ('while read -r x; do ...; done < <(cmd)', 'Read the output of a command, in the current shell', 'while read -r pid; do ...; done < <(pgrep bash)')])}
{run('while, until and reading lines', """n=1
while (( n <= 3 )); do echo "round $n"; (( n++ )); done
until [ -e ready.flag ]; do echo "not ready, creating the flag"; touch ready.flag; done
while IFS= read -r line; do
  echo "line: [$line]"
done < poem.txt
total=0
while IFS=, read -r name subject score; do
  [ "$name" = name ] && continue
  total=$(( total + score ))
done < marks.csv
echo "total of all scores: $total"
count=0
grep a fruits.txt | while read -r f; do (( count++ )); done
echo "after the pipe: count=$count"
count=0
while read -r f; do (( count++ )); done < <(grep a fruits.txt)
echo "with < <( ): count=$count\"""", note='IFS= keeps leading spaces and -r keeps backslashes, so each line arrives exactly as written. The header line of marks.csv was skipped with continue. After the pipe the count was still 0, because every part of a pipeline runs in its own subshell and its variables are lost. Process substitution kept the loop in the current shell.')}
{note('The last line of a file without a final newline is still read into the variable, but read returns 1, so the loop skips it. Write while IFS= read -r line || [ -n "$line" ] to keep it.', 'tip')}
{talk('A while loop keeps going as long as its condition command succeeds. Until is the mirror image: it keeps going as long as the command fails, which reads nicely for waiting, such as until the server answers. The most important pattern of all is reading a file line by line. Write while I F S equals nothing, read dash r line, and put the file after done with a less than sign. The empty IFS keeps spaces at the start of the line, and dash r keeps backslashes as they are. To split each line into fields, set IFS to a comma and give read several variable names, which turns a CSV file into variables in one step. One famous trap: if you pipe into a while loop, the loop runs in a subshell, so counters you change inside are lost when it ends. Feed the loop with a less than sign and process substitution instead, and the variables survive.')}
''', kw=['while loop', 'until loop', 'while true', 'while read', 'read line by line', 'IFS= read -r', 'CSV fields', 'process substitution', 'pipe subshell', 'last line without newline'])

K.lesson('control', 'break, continue and whole-loop redirection', f'''
{table(['Command', 'Effect'], [
    ['<code>break</code>', 'leave the loop now, continue after done'],
    ['<code>continue</code>', 'skip the rest of this pass, start the next one'],
    ['<code>break 2</code>, <code>continue 2</code>', 'act on the loop 2 levels out (for nested loops)'],
    ['<code>done > file</code>', 'send the output of every pass into one file, opened once'],
    ['<code>done | sort</code>', 'pipe the whole loop output into another command'],
    ['<code>select x in a b c</code>', 'print a numbered menu and read a choice into x, until break']])}
{run('Controlling loops', """for n in {1..10}; do
  (( n % 2 )) && continue
  (( n > 8 )) && break
  echo "even $n"
done
for row in A B C; do
  for col in 1 2 3; do
    [ "$col" = 3 ] && continue 2
    [ "$row" = C ] && break 2
    printf '%s%s ' "$row" "$col"
  done
done; echo
for f in *.txt; do echo "$(wc -l < "$f") $f"; done | sort -n
for i in 1 2 3; do echo "entry $i"; done > entries.log
cat entries.log
find . -maxdepth 1 -name '*.txt' -print0 | sort -z | while IFS= read -r -d '' f; do echo "safe: [$f]"; done""", note='continue skipped odd numbers and break stopped at 10. continue 2 jumped to the next row before column 3, and break 2 left both loops when row C began. The whole loop output was sorted or written to a file at once. With -print0 and read -d an empty delimiter, every name arrives whole, even one with spaces or a newline.')}
{sample('A select menu (interactive)', """PS3="Pick a size: "
select size in small medium large quit; do
  [ "$size" = quit ] && break
  echo "you chose $size"
done""", out="""1) small
2) medium
3) large
4) quit
Pick a size: 2
you chose medium
Pick a size: 4""", note='select prints the menu to stderr, shows PS3 as the prompt and reads a number. An invalid number leaves the variable empty.')}
{lab('Loop like a pro', [
    ('Print the numbers 1 to 5, each on its own line, with a for loop and a brace range.', 'for n in {1..5}; do echo $n; done', [{'cmd': r'^\s*for\b.*\{1\.\.5\}'}, {'out': '^1$'}, {'out': '^5$'}]),
    ('With a C-style for loop, print 0 2 4 6 8 on separate lines.', 'for ((i=0; i<10; i+=2)); do echo $i; done', [{'cmd': r'for\s*\(\('}, {'out': '^8$'}]),
    ('Loop over every .txt file and print its name followed by the word file, like notes.txt file.', 'for f in *.txt; do echo "$f file"; done', [{'cmd': r'for\s+\w+\s+in\s+\*\.txt'}, {'out': r'^notes\.txt file$'}]),
    ('Read poem.txt line by line with while read and print each line in capital letters using ${line^^}.', 'while IFS= read -r line; do echo "${line^^}"; done < poem.txt', [{'cmd': r'while.*read'}, {'out': '^TWINKLE TWINKLE LITTLE STAR$'}]),
    ('Use while read with IFS=, on marks.csv to print the first field of every line.', 'while IFS=, read -r name rest; do echo "$name"; done < marks.csv', [{'cmd': r'IFS=,'}, {'out': '^Meera$'}]),
    ('Set n to 1, then use until to double n until it is at least 100, and print the final n.', 'n=1; until (( n >= 100 )); do (( n *= 2 )); done; echo $n', [{'cmd': r'\buntil\b'}, {'out': '^128$'}]),
    ('Print the numbers 1 to 10 but stop the loop with break when the number reaches 4, so only 1, 2 and 3 appear.', 'for n in {1..10}; do (( n == 4 )) && break; echo $n; done', [{'cmd': r'\bbreak\b'}, {'out': '^3$'}])])}
{talk('Two small commands give you full control inside a loop. Break leaves the loop at once and carries on after done. Continue skips the rest of the current pass and jumps to the next one. In nested loops, add a number: break two leaves both loops, and continue two moves straight to the next pass of the outer loop. You can also treat the whole loop as one command. Put a greater than sign and a file name after done, and the output of every pass goes into that file, which is opened only once. Or pipe the whole loop into sort. For file names that may contain spaces or even new lines, the safe pattern is find with dash print zero, read with dash d and an empty delimiter, and an empty IFS. Finally, select builds a numbered menu for interactive scripts and keeps asking until you break out.')}
''', kw=['break', 'continue', 'break 2', 'nested loops', 'done > file', 'loop output', 'select menu', 'PS3', 'find -print0', 'read -d', 'safe file names'])

K.lesson('levels', 'Loops from school to research', f'''
{ladder(
    '<p>A loop repeats work. for goes through a list of items, while keeps going while something is true, and until keeps going until it becomes true. break stops a loop and continue skips to the next round.</p>',
    '<p>The for list is expanded once, before the first pass, so changing a variable inside the loop does not change the list. while runs its condition before every pass. Each part of a pipeline runs in a subshell, so variables set in cmd | while read are lost, while done < file and done < <(cmd) keep the loop in the current shell.</p>',
    '<p>Shell loops start a new process for every external command inside them, so a loop over a million lines that calls sed or cut each time is slow. Move the whole job into awk, or use parameter expansion and builtins inside the loop. read is slow too, since it reads one byte at a time from a pipe to avoid reading past the newline. mapfile -t arr < file reads all lines into an array in one step. shopt -s lastpipe (with job control off, as in scripts) runs the last part of a pipeline in the current shell.</p>',
    '<p>Studies of shell scripts in package repositories and CI pipelines find that loops over unquoted command output and word-split file names are common sources of bugs, which tools such as ShellCheck flag (SC2045 for looping over ls, SC2013 for reading lines with for). Research systems such as PaSh (EuroSys 2021) parallelise data-parallel shell pipelines automatically, and GNU parallel and xargs -P run loop bodies on many cores.</p>')}
{scene('the nightly image resize', '<p>A photo site resizes every new upload at night. The first script was <code>for f in $(ls uploads)</code> and failed on names with spaces. The fixed script uses <code>for f in uploads/*.jpg</code> with nullglob, skips files that already have a thumbnail with <code>[ -e "thumbs/${f##*/}" ] && continue</code>, and logs each pass with <code>done >> resize.log</code>. Later the team replaced the loop body with <code>find uploads -name "*.jpg" -print0 | xargs -0 -P 4</code> to use four cores.</p>')}
{talk('Here is what experienced script writers know about loops. The list of a for loop is built only once, before the first pass. While checks its condition before every pass. A pipe into while puts the loop in a subshell, which is why counters vanish, and redirecting a file or process substitution into done avoids it. Speed matters too. Every external command inside a loop starts a new process, so calling sed or cut a million times is slow. It is far faster to hand the whole file to awk, or to use parameter expansion and other builtins inside the loop. To load every line of a file into an array at once, use mapfile. Researchers have built systems such as PaSh that split shell pipelines across many processor cores automatically, and everyday tools such as xargs with dash capital P and GNU parallel let you run the body of a loop on many cores at once.')}
''', kw=['loop performance', 'subshell in pipeline', 'lastpipe', 'mapfile', 'awk instead of loop', 'xargs -P', 'GNU parallel', 'PaSh', 'ShellCheck SC2045'])

K.quiz('e', 'Which word ends the body of a for loop?', ['end', 'fi', 'done', 'esac'], 2, 'do ... done.', 'Loops end with done.')
K.quiz('e', 'How many times does for x in a b c runs its body?', ['1', '2', '3', '4'], 2, 'One per word.', 'Three words, three passes.')
K.quiz('e', 'Which loop keeps going while its command fails?', ['while', 'until', 'for', 'select'], 1, 'The opposite of while.', 'until repeats while the condition fails.')
K.quiz('e', 'Which command skips the rest of the current pass?', ['break', 'continue', 'exit', 'return'], 1, 'Go to the next round.', 'continue starts the next pass.')
K.quiz('m', 'Which is the safe way to read a file line by line?', ['for line in $(cat f)', '<code>while IFS= read -r line; do ...; done &lt; f</code>', 'cat f | for line', 'read f'], 1, 'while read with IFS= and -r.', 'It keeps every line exactly.')
K.quiz('m', 'for f in *.pdf runs in a folder with no PDF files. What is $f in the single pass?', ['empty', '*.pdf', 'an error', 'the folder name'], 1, 'No match, no change.', 'An unmatched pattern stays as text unless nullglob is on.')
K.quiz('m', 'What does <code>for (( i = 0; i &lt; 3; i++ ))</code> print with echo $i in the body?', ['1 2 3', '0 1 2', '0 1 2 3', '3'], 1, 'Starts at 0, stops before 3.', '0, 1 and 2.')
K.quiz('m', 'Where do you put the input file for a while read loop?', ['After while', 'After read', 'After done, with <', 'Before for'], 2, 'Redirect the whole loop.', 'done < file feeds every read.')
K.quiz('m', 'Which ends both an inner and an outer loop at once?', ['break', 'break 2', 'continue 2', 'exit 2'], 1, 'Two levels.', 'break 2 leaves two loops.')
K.quiz('h', '<code>count=0; cmd | while read -r x; do (( count++ )); done; echo $count</code> prints 0. Why?', ['read failed', 'The loop ran in a subshell, so count changed only there', 'count is read only', '(( )) does not add'], 1, 'Pipelines.', 'Each part of a pipeline is a subshell.')
K.quiz('h', 'Why is for f in $(ls) a bad idea?', ['ls is slow', 'Names with spaces are split into separate words', 'It skips hidden files only', 'It is a syntax error'], 1, 'Word splitting.', 'Use for f in * instead.')
K.quiz('h', 'Which pair handles file names that contain newlines?', ['ls and for', 'find -print0 and read -d \'\'', 'cat and while', 'echo and cut'], 1, 'The NUL byte.', 'NUL cannot appear in a file name.')
K.quiz('x', 'Why can a loop calling sed on each of a million lines be slow?', ['sed is single threaded', 'Each sed call starts a new process', 'Loops have a limit', 'bash caches the output'], 1, 'Processes.', 'Starting a process each time costs far more than the work.')

K.calc('e', 'How many passes does for n in {1..12} make?', '12', 'Count the range.', ['The range is 1 to 12.', 'Both ends are included.', eq('12 passes')], check=12)
K.calc('e', '<code>for (( i = 10; i &gt; 0; i -= 4 ))</code>. How many passes?', '3', 'List the values.', ['i = 10, then 6, then 2.', 'Next would be −2, which fails i > 0.', eq('3 passes')], check=3)
K.calc('m', 'Two nested loops: the outer runs over 4 items, the inner over 5. How many times does the inner body run?', '20', 'Every pair.', ['Each outer pass runs the inner loop fully.', '5 inner passes per outer pass.', eq('4 × 5 = 20')], check=20)
K.calc('m', '<code>n=1; until (( n &gt;= 100 )); do (( n *= 3 )); done</code>. What is n afterwards?', '243', 'Powers of 3.', ['1, 3, 9, 27, 81.', '81 is below 100, so one more time.', eq('81 × 3 = 243')], check=243)
K.calc('m', 'for n in {1..10}, with continue when n is odd. How many times does the line after continue run?', '5', 'Even numbers only.', ['Odd numbers 1, 3, 5, 7, 9 are skipped.', 'Even numbers 2, 4, 6, 8, 10 reach the line.', eq('5')], check=5)
K.calc('h', 'A file has 6 lines and the last one has no final newline. How many passes does a plain while read -r line make?', '5', 'read returns 1 on the last line.', ['Lines 1 to 5 end with a newline.', 'Line 6 is read, but read returns 1, so the body is skipped.', eq('5 passes')], check=5)

K.must('for', '<code>for x in LIST; do ...; done</code>. LIST may be words, a glob, a brace range or "$@". <code>for (( i=0; i&lt;n; i++ ))</code> counts. shopt -s nullglob removes unmatched patterns.')
K.must('while and until', 'while CMD repeats while CMD succeeds, until while it fails, while true with break for a loop you leave from the inside.')
K.must('Reading lines', '<code>while IFS= read -r line; do ...; done &lt; file</code>. Set IFS=, and give several names to split fields. Use < <(cmd) rather than cmd | while to keep variables.')
K.must('Control', 'break leaves the loop, continue skips to the next pass, add a number for nested loops. done > file and done | cmd redirect the whole loop.')
K.must('Safe names', 'Loop over globs, never over $(ls). For any name use find -print0 | while IFS= read -r -d \'\' f.')

T = K.topic(
    slug='loops', topic='loops',
    step=(2, 'Decisions and loops', 'lx-script-2', 'Let scripts choose and repeat: if, test, [[ ]], (( )) and case, then for, while and until loops over files, lines and numbers.', 'Intermediate'),
    title='Loops: for, while and until', short='Loops', badge='2.2', minutes=50, added='2026-11-23',
    lead='Repeat work safely: for over words, files and ranges, the C-style for, while and until, reading files line by line, break and continue, and redirecting a whole loop.',
    desc='for over words, globs, brace ranges and "$@", the C-style for (( )), nullglob, while and until, while true with break, reading files with while IFS= read -r, splitting fields with IFS, the pipe subshell trap and < <( ), the missing last newline, break and continue with levels, done > file and done | sort, find -print0 with read -d, select menus and loop speed.',
    summary='for, C-style for, while and until, while read, break and continue.',
    keywords=['for loop', 'while loop', 'until', 'while read', 'read line by line', 'break', 'continue', 'nullglob', 'subshell', 'select', 'find -print0', 'IFS'],
    recap='<p>for walks a list built once before the loop, while and until repeat on a condition, while IFS= read -r reads lines exactly, break and continue steer the loop, and a whole loop can be redirected after done.</p>')
