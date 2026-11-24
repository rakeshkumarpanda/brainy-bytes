# Power tools 2.3: awk. Records and fields, -F, $0 $1 $NF NR NF, patterns and actions, BEGIN and END, comparisons and
# regex matches, ranges, sums, averages, maximum, associative arrays, printf, if, loops, functions, -v, -f, OFS.
# Sources: POSIX awk (Shell and Utilities volume), mawk(1) and the GNU Awk User's Guide (gawk 5.3), A. V. Aho,
# B. W. Kernighan, P. J. Weinberger, "The AWK Programming Language" (1988, second edition 2023). Ubuntu and Debian
# install mawk as awk by default (update-alternatives), macOS ships the One True AWK.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('model', 'Lines, fields and the pattern { action } idea', f'''
<p><code>awk</code> is a small programming language made for text in columns. It reads its input one <b>record</b> (normally one line) at a time and splits it into <b>fields</b>. Then it runs your program, which is a list of <code>pattern {{ action }}</code> rules.</p>
{fxs(fx('$0', 'the whole line', '$1 is the first field, $2 the second, $NF the last one.', key=True),
     fx('NR and NF', 'counters', 'NR is the number of the current line (record), NF the number of fields in it.'),
     fx('-F,', 'field separator', 'Default: runs of spaces and tabs. -F, splits at commas, -F: at colons.', key=True),
     fx('pattern { action }', 'a rule', 'If the pattern is true for a line, the action runs. No pattern: every line. No action: print the line.'))}
{play('lx-awk')}
{run('Picking columns', """awk '{print $1}' logs/app.log | head -n 3
awk '{print $3, $4}' logs/app.log | head -n 3
awk -F, '{print $1, $3}' marks.csv
awk -F: '{print $1, $7}' /etc/passwd | head -n 3
awk '{print NR, NF, $NF}' poem.txt""", note='The comma in print puts a space (the output separator) between values. Without the comma, values are glued together.')}
{note('Unlike cut, awk treats several spaces in a row as one separator, so it handles the columns of ps, df or ls -l output without trouble.', 'tip')}
{talk('awk is named after its three authors, Alfred Aho, Peter Weinberger and Brian Kernighan, who wrote it at Bell Labs in 1977. It is a complete little programming language, but you can start using it in seconds. awk reads text one line at a time, splits each line into fields, and calls them dollar one, dollar two and so on, with dollar zero for the whole line. So awk with print dollar one prints the first column of anything. A program is a list of rules. Each rule is a pattern followed by an action in curly braces. If the pattern is true for a line, the action runs. Leave out the pattern and the action runs on every line. Leave out the action and awk simply prints the matching lines. Unlike cut, awk treats several spaces in a row as a single separator, which is exactly what the output of commands like ps and df needs.')}
''', kw=['awk', 'fields', 'records', '$0', '$1', '$NF', 'NR', 'NF', '-F', 'pattern action', 'Aho Weinberger Kernighan'])

K.lesson('patterns', 'Choosing lines: patterns, BEGIN and END', f'''
{table(['Pattern', 'Selects', 'Example'], [
    ['<code>$3 &gt;= 80</code>', 'lines where field 3 is 80 or more', "<code>awk -F, '$3 &gt;= 80' marks.csv</code>"],
    ['<code>/ERROR/</code>', 'lines matching a regular expression', "<code>awk '/ERROR/' app.log</code>"],
    ['<code>$2 ~ /^ma/</code>', 'field 2 matches a regex (!~ for does not)', "<code>awk -F, '$2 ~ /^ma/'</code>"],
    ['<code>NR &gt; 1</code>', 'every line except the first', 'skip a header line'],
    ['<code>NR==2, NR==4</code>', 'a range from line 2 to line 4', "<code>awk 'NR==2, NR==4'</code>"],
    ['<code>a &amp;&amp; b</code>, <code>a || b</code>, <code>!a</code>', 'combine patterns', "<code>awk '$3 &gt; 70 &amp;&amp; $2 == \"maths\"'</code>"],
    ['<code>BEGIN</code>', 'runs once before the first line', 'print a heading, set FS'],
    ['<code>END</code>', 'runs once after the last line', 'print totals']])}
{run('Patterns at work', """awk -F, '$3 >= 85' marks.csv
awk '/ERROR/ {print $2, $4, $5}' logs/app.log
awk -F, '$2 == "maths" {print $1}' marks.csv
awk -F: '$3 == 0 {print $1, "has user ID 0"}' /etc/passwd
awk 'NR==2, NR==3' poem.txt
awk 'BEGIN {print "Report"} {n++} END {print n, "lines"}' notes.txt""", note='$3 == 0 compares the user ID field with 0, the superuser.')}
{note('awk compares two values as numbers when both look like numbers (fields count as "looks like a number" when their text is numeric), and as text otherwise. So $3 >= 80 compares scores numerically, while $1 == "Asha" compares text.', 'tip')}
{talk('Patterns decide which lines an action runs on. The most useful ones are comparisons, such as dollar three greater or equal to eighty, which keeps only the rows with high scores. A regular expression between slashes keeps lines that match, just like grep, and the tilde operator tests a single field against a regex. NR greater than one is the classic way to skip a header line. Two special patterns run outside the normal loop. BEGIN runs once before any input is read, which is the place to print a heading or set options. END runs once after the last line, which is where totals and averages are printed. With these few pieces you can already answer most questions about a log file or a spreadsheet export.')}
''', kw=['awk pattern', 'comparison', 'regex match', '~', '!~', 'NR > 1', 'range pattern', 'BEGIN', 'END', '&&', '||'])

K.lesson('calc', 'Calculating: sums, averages, counts and printf', f'''
{cmdtable([
    ("{ s += $3 } END { print s }", 'Total of a column', "awk -F, 'NR>1 {s+=$3} END {print s}' marks.csv"),
    ("END { print s / n }", 'Average: total divided by count', "awk -F, 'NR>1 {s+=$3; n++} END {print s/n}'"),
    ("$3 > max { max = $3 }", 'Largest value', "awk -F, 'NR>1 && $3>max {max=$3} END {print max}'"),
    ("{ c[$2]++ }", 'Count per group with an array', "awk -F, 'NR>1 {c[$2]++} END {for (k in c) print k, c[k]}'"),
    ("{ s[$1] += $3 }", 'Total per group', "awk -F, 'NR>1 {s[$1]+=$3} END {for (k in s) print k, s[k]}'"),
    ('printf "%-8s %5.1f\\n", a, b', 'Formatted output: width, decimals, alignment', "awk '{printf \"%-10s %3d\\n\", $1, NR}'")])}
{run('Numbers from marks.csv', """awk -F, 'NR > 1 {sum += $3} END {print "total", sum}' marks.csv
awk -F, 'NR > 1 {sum += $3; n++} END {print "average", sum / n}' marks.csv
awk -F, 'NR > 1 && $3 > max {max = $3; who = $1} END {print "best", who, max}' marks.csv
awk -F, 'NR > 1 {count[$2]++} END {for (s in count) print s, count[s]}' marks.csv | sort
awk -F, 'NR > 1 {total[$1] += $3} END {for (p in total) printf "%-6s %4d\\n", p, total[p]}' marks.csv | sort""", note='Variables start as 0 (or empty text), so sum += $3 needs no setup. An array such as count[$2] uses text as the index. The order of for (k in array) is not fixed, which is why the output goes through sort.')}
{deep('printf formats in one table', '<p><code>%s</code> text, <code>%d</code> whole number, <code>%f</code> decimal (<code>%.2f</code> two decimals), <code>%e</code> scientific, <code>%x</code> hexadecimal, <code>%c</code> one character, <code>%%</code> a percent sign. A number after % sets the width, <code>-</code> aligns left, <code>0</code> pads with zeros: <code>%-10s</code>, <code>%05d</code>, <code>%8.2f</code>. printf never adds a newline by itself, so end the format with <code>\\n</code>.</p>')}
{talk('awk really shines when you need numbers from text. Variables start at zero automatically, so adding up a column is one short rule: for every line, add dollar three to sum, and in the END block print it. Divide by the number of lines and you have an average. Keep the largest value seen so far and you have a maximum. The most powerful feature is the associative array. An array in awk can use any text as its index, so count of dollar two plus plus counts how many rows each subject has, in a single pass over the file. This is the same idea as a group by in SQL or a pivot table in a spreadsheet. For neat reports, printf lets you set widths and decimal places, for example percent minus ten s for a left aligned name and percent five point one f for a number with one decimal.')}
''', kw=['awk sum', 'average', 'maximum', 'associative array', 'count per group', 'printf', '%d', '%s', '%.2f', 'group by'])

K.lesson('programs', 'Real programs: if, loops, functions and options', f'''
{cmdtable([
    ('if (c) a; else b', 'Choose between two actions', "awk -F, 'NR>1 {if ($3>=80) print $1, \"A\"; else print $1, \"B\"}'"),
    ('for (i = 1; i <= NF; i++)', 'Loop over the fields of a line', "awk '{for (i=NF; i>0; i--) printf \"%s \", $i; print \"\"}'"),
    ('while (c) { ... }', 'Loop while a condition holds', "awk 'BEGIN {x=1; while (x<100) x*=2; print x}'"),
    ('next', 'Stop working on this line, go to the next one', "awk 'NR==1 {next} {print}'"),
    ('-v name=value', 'Pass a shell value into awk', "awk -v min=80 -F, '$3>=min' marks.csv"),
    ('-f prog.awk', 'Read the program from a file', 'awk -F, -f report.awk marks.csv'),
    ('$1 = $1; OFS', 'Rebuild the line with a new output separator', "awk -F, -v OFS='\\t' '{$1=$1; print}'"),
    ('function f(x) { ... }', 'Your own functions', "awk 'function sq(x) {return x*x} {print sq($1)}'"),
    ('length, substr, index, split, sub, gsub, toupper, tolower, sprintf', 'Built in functions for text', "awk '{print toupper(substr($1,1,1)) substr($1,2)}'")])}
{run('A small report program', """cat > report.awk << 'END'
BEGIN { FS = ","; print "Name    Subject  Score Grade" }
NR == 1 { next }
{
    grade = ($3 >= 85) ? "A" : ($3 >= 70) ? "B" : "C"
    printf "%-7s %-8s %5d %s\\n", $1, $2, $3, grade
    total += $3
}
END { printf "Average score: %.1f\\n", total / (NR - 1) }
END
awk -f report.awk marks.csv
awk -v min=80 -F, 'NR > 1 && $3 >= min {print $1, $3}' marks.csv
awk -F, -v OFS=' | ' '{$1 = $1; print}' marks.csv | head -n 3
awk '{gsub(/a/, "4"); print}' notes.txt""", note='cond ? x : y picks x when cond is true. Assigning a field ($1 = $1) makes awk rebuild the line with OFS. gsub replaces every match in the line, like sed s///g.')}
{note('Ubuntu and Debian install mawk as awk, many other distributions use GNU awk (gawk), and macOS uses the original "one true awk". Everything in this chapter works in all of them. gawk adds extras such as asort(), strftime() and --csv for quoted CSV fields.', 'tip')}
{lab('Reports with awk', [
    ('Print only the first field (the date) of every line of <code>logs/app.log</code>.', "awk '{print $1}' logs/app.log", [{'cmd': r'awk'}, {'out': '^2026-11-23\\n2026-11-23'}]),
    ('Print the name and score (fields 1 and 3) of <code>marks.csv</code>, comma separated input.', "awk -F, '{print $1, $3}' marks.csv", [{'cmd': r'awk\s+-F'}, {'out': '^name score\\nAsha 91'}]),
    ('Show the rows of <code>marks.csv</code> with a score below 75.', "awk -F, '$3 < 75' marks.csv", [{'cmd': r'awk'}, {'out': '^John,english,67\\nRavi,maths,72$'}]),
    ('Print the total of all scores (skip the header).', "awk -F, 'NR > 1 {s += $3} END {print s}' marks.csv", [{'cmd': r'awk'}, {'out': '^481$'}]),
    ('Print how many marks each student has, one line per student, sorted.', "awk -F, 'NR > 1 {c[$1]++} END {for (n in c) print n, c[n]}' marks.csv | sort", [{'cmd': r'awk.*\['}, {'out': '^Asha 2\\nJohn 1\\nMeera 1\\nRavi 2$'}]),
    ('Print the number of words in each line of <code>poem.txt</code>.', "awk '{print NF}' poem.txt", [{'cmd': r'NF'}, {'out': '^4\\n6\\n6\\n6$'}]),
    ('Print the user names of /etc/passwd whose user ID (field 3) is 1000 or more.', "awk -F: '$3 >= 1000 {print $1}' /etc/passwd", [{'cmd': r'awk\s+-F\s*:'}, {'out': '^asha\\nlearner$'}])])}
{talk('As your tasks grow, awk grows with you. It has if and else, while and for loops, its own functions, and built in functions for text such as length, substr, split and gsub. Longer programs are best kept in a file and run with dash f, so they can be read, tested and stored in version control. Use dash v to pass a value from the shell into awk, rather than gluing shell variables into the program text, because that is safer and easier to read. One detail can surprise you: assigning to a field, even dollar one equals dollar one, makes awk rebuild the whole line using the output separator OFS, which is a neat way to turn commas into tabs. Different systems ship different awk programs, mawk on Ubuntu, GNU awk on many others, and the original version on macOS, but everything in this chapter works in all of them.')}
''', kw=['awk if', 'awk for loop', 'awk while', 'next', 'awk -v', 'awk -f', 'OFS', 'awk function', 'gsub', 'substr', 'split', 'mawk', 'gawk'])

K.lesson('levels', 'awk from school to research', f'''
{ladder(
    '<p>awk splits each line into numbered columns. print $1 shows the first column, a pattern such as $3 &gt; 50 chooses lines, END prints totals at the end, and arrays count things per group.</p>',
    '<p>An awk program is a sequence of pattern action pairs applied to each record. Fields split by FS, variables are untyped (string or number by context), arrays are associative, and BEGIN and END run outside the input loop. Comparisons are numeric when both sides are numeric strings.</p>',
    '<p>Implementations compile the program to an internal tree or byte code. mawk (Mike Brennan) is known for speed, gawk adds network sockets, profiling, namespaces and arbitrary precision with -M. Splitting records is the hot path, so fast implementations avoid creating fields that the program never reads. For very large files awk is often limited by disk speed, not by the CPU.</p>',
    '<p>awk inspired Perl (Larry Wall, 1987) and the idea of "little languages" described by Jon Bentley in 1986. The second edition of The AWK Programming Language (2023) added UTF-8 and CSV support to the one true awk. Data tools such as Miller, xsv and DuckDB command line queries continue the idea of querying text tables directly, now with typed columns and SQL.</p>')}
{scene('the disk alert', '<p>A monitoring alert says a disk is almost full. The engineer runs <code>df -P | awk \'NR&gt;1 &amp;&amp; $5+0 &gt; 80 {print $6, $5}\'</code> to list every file system above 80 percent use, then <code>du -sk /var/log/* | sort -n | tail -n 5</code> to find the biggest logs. $5+0 turns "85%" into the number 85.</p>')}
{talk('awk turned out to be far more influential than its authors expected. Larry Wall created Perl in 1987 partly to go beyond what awk and sed could do, and Jon Bentley used awk as the main example when he wrote about little languages, small special purpose languages that solve one kind of problem very well. Inside, every awk reads the program, turns it into an internal form and then runs it once per line. The mawk version used on Ubuntu is known for its speed, while GNU awk adds features such as network connections and arbitrary precision numbers. Remarkably, the original authors were still improving it decades later. The second edition of their book, published in 2023, added proper support for UTF-8 text and CSV files. Modern tools such as Miller and DuckDB continue the same idea of asking questions directly of text tables.')}
''', kw=['awk implementation', 'mawk', 'gawk', 'one true awk', 'Perl', 'little languages', 'CSV', 'UTF-8', 'Miller', 'DuckDB'])

K.quiz('e', "What does awk '{print $1}' file print?", ['The first line', 'The first field of every line', 'The whole file', 'The number of lines'], 1, 'Fields.', '$1 is the first field of each line.')
K.quiz('e', 'Which variable holds the number of the current line?', ['NF', 'NR', 'FS', '$0'], 1, 'Number of Record.', 'NR counts records read so far.')
K.quiz('e', 'Which option tells awk that fields are separated by commas?', ['-d,', '-F,', '-t,', '-s,'], 1, 'Field separator.', '-F sets FS.')
K.quiz('e', 'What is $NF?', ['The number of fields', 'The last field of the line', 'The first field', 'The file name'], 1, 'Field number NF.', 'NF is the field count, so $NF is the last field.')
K.quiz('m', "What does awk -F, '$3 >= 80' marks.csv print?", ['Only field 3', 'Whole lines where field 3 is 80 or more', 'The number 80', 'Nothing, an action is missing'], 1, 'No action means print.', 'A pattern without an action prints the matching line.')
K.quiz('m', 'Where do you print a total after all lines are read?', ['In BEGIN', 'In END', 'In the first rule', 'With NR==1'], 1, 'After the last line.', 'END runs once after all input.')
K.quiz('m', 'How do you skip the header line of a CSV in awk?', ['NR > 1', 'NF > 1', '$1 != 1', 'BEGIN'], 0, 'Line numbers.', 'NR > 1 is true for every line except the first.')
K.quiz('m', "What does awk -F, 'NR>1 {c[$2]++} END {for (k in c) print k, c[k]}' do?", ['Sums field 2', 'Counts how many lines have each value of field 2', 'Prints field 2', 'Sorts the file'], 1, 'Arrays with text keys.', 'c[$2]++ increases a counter per distinct value.')
K.quiz('m', "Why is cut -d' ' poor for ps output, while awk works?", ['cut is slower', 'cut treats each space as a separator, awk treats runs of spaces as one', 'awk knows ps', 'cut cannot read pipes'], 1, 'Several spaces.', 'awk splits on runs of blanks by default.')
K.quiz('h', 'What does printf print with the format %-6s|%4.1f followed by a newline, for the values ab and 3.14159?', ['ab    | 3.1', 'ab|3.14', '    ab|3.1', 'ab | 3.14159'], 0, 'Left align 6, width 4, one decimal.', '%-6s pads "ab" to 6 on the right, %4.1f gives " 3.1".')
K.quiz('h', 'Why should you pass shell values with awk -v rather than inside the program text?', ['It is faster', 'It avoids quoting problems and code injection when the value contains special characters', 'awk cannot read the shell', 'It is required'], 1, 'Clean separation.', '-v passes data as data, not as program text.')
K.quiz('h', 'In what order does for (k in arr) visit the keys?', ['Sorted', 'Insertion order', 'Unspecified, it depends on the awk version', 'Reverse'], 2, 'Not defined by POSIX.', 'Pipe the output through sort when order matters.')
K.quiz('x', "In awk, '10' < '9' with both from fields compares how?", ['As text, so true', 'As numbers, so false, because both look numeric', 'It is an error', 'Randomly'], 1, 'Strnum values.', 'Field values that look like numbers compare numerically.')

K.calc('e', 'The scores after the header in marks.csv are 91, 78, 85, 67, 72, 88. What does a sum of $3 print?', '481', 'Add them.', ['91 + 78 = 169.', '169 + 85 + 67 = 321.', eq('321 + 72 + 88 = 481')], check=481)
K.calc('e', 'A line "Like a diamond in the sky" has how many fields with the default separator?', '6', 'Count the words.', ['Words: Like, a, diamond, in, the, sky.', 'Each word is one field.', eq('NF = 6')], check=6)
K.calc('m', 'Average of the six scores 91, 78, 85, 67, 72, 88, rounded to one decimal, times 10 (so 80.2 becomes 802).', '802', 'Total over count.', ['Total: 481.', 'Count: 6.', 'Average: 481 ÷ 6 = 80.17, rounded 80.2.', eq('80.2 × 10 = 802')], check=802)
K.calc('m', "/etc/passwd lines have 7 fields. awk -F: '{n += NF} END {print n}' on a file of 30 lines prints?", '210', 'Fields per line times lines.', ['Fields per line: 7.', 'Lines: 30.', eq('7 × 30 = 210')], check=210)
K.calc('m', 'Ravi has scores 78 and 72. What does total[$1] += $3 hold for Ravi at the end?', '150', 'Add his rows.', ['First row: 78.', 'Second row: 72.', eq('78 + 72 = 150')], check=150)
K.calc('h', 'df shows Use% values 85%, 40%, 92% and 81%. How many lines does awk \'$5+0 > 80\' keep (ignore the header)?', '3', '$5+0 turns 85% into 85.', ['Values: 85, 40, 92, 81.', 'Above 80: 85, 92 and 81.', eq('3 lines')], check=3)

K.must('Fields', '$0 whole line, $1 first field, $NF last, NF field count, NR line number. -F, or -F: change the separator.')
K.must('Rules', 'pattern { action }. No pattern: every line. No action: print. BEGIN before input, END after it.')
K.must('Patterns', 'Comparisons ($3 >= 80), regex (/ERROR/, $2 ~ /x/), NR > 1 to skip a header, ranges NR==2,NR==4, && || !.')
K.must('Numbers', 'Variables start at 0. Sum in a rule, print in END. Arrays with text keys count or total per group.')
K.must('Programs', 'printf for neat columns, if and loops, -v to pass values, -f for program files, $1=$1 with OFS to rebuild lines.')

T = K.topic(
    slug='awk', topic='awk',
    step=(2, 'Searching and editing text', 'lx-power-2', 'Find lines with grep and regular expressions, change text with sed, and turn columns into reports with awk.', 'Intermediate'),
    title='awk: columns, patterns and reports', short='awk', badge='2.3', minutes=50, added='2026-11-23',
    lead='Use awk to pick columns, filter rows with conditions, add up numbers, count per group and print neat reports, from one line commands to small programs in a file.',
    desc='Records and fields, $0 $1 $NF, NR and NF, -F, pattern action rules, BEGIN and END, comparisons and regex patterns, ranges, sums, averages and maximums, associative arrays, printf formats, if and loops, next, -v and -f, OFS, built in text functions, mawk, gawk and the one true awk.',
    summary='Fields and -F, patterns, BEGIN and END, sums, arrays, printf and small awk programs.',
    keywords=['awk', 'columns', 'fields', 'NR', 'NF', 'BEGIN', 'END', 'printf', 'associative array', 'sum column', 'report', 'gawk', 'mawk'],
    recap='<p>awk splits lines into fields and runs pattern { action } rules. Use -F for separators, NR &gt; 1 to skip headers, END for totals, arrays to group, printf for reports.</p>')
