# Power tools 2.1: grep and regular expressions. grep options, basic and extended regular expressions, character
# classes, anchors, repetition, groups and alternation, -r -l -o -c -n -A -B -C. Sources: GNU grep manual (3.11),
# grep(1), regex(7), POSIX Base Definitions chapter 9 Regular Expressions, K. Thompson, "Regular Expression Search
# Algorithm", CACM 11(6), 1968, S. C. Kleene, "Representation of Events in Nerve Nets and Finite Automata", 1956,
# Mike Haertel's 2010 mailing list note "why GNU grep is fast".
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('grep', 'Finding lines: grep', f'''
<p><code>grep PATTERN FILE</code> prints every line of FILE that contains PATTERN. With no file it reads stdin, so it fits at the end of any pipeline. The name comes from the old ed editor command <code>g/re/p</code>: globally search for a regular expression and print.</p>
{cmdtable([
    ('grep word FILE', 'Lines that contain word (case sensitive)', 'grep ERROR app.log'),
    ('grep -i word', 'Ignore upper and lower case', 'grep -i error app.log'),
    ('grep -v word', 'Lines that do NOT contain word', 'grep -v INFO app.log'),
    ('grep -n word', 'Show line numbers', 'grep -n milk notes.txt'),
    ('grep -c word', 'Only count the matching lines', 'grep -c ERROR app.log'),
    ('grep -w word', 'Match whole words only', 'grep -w in poem.txt'),
    ('grep -o pattern', 'Print only the matched part', "grep -o '[0-9]*%' app.log"),
    ('grep -r word DIR', 'Search every file below DIR', 'grep -r TODO src'),
    ('grep -l word FILES', 'Only list the names of files that match', 'grep -l ERROR logs/*'),
    ('grep -A2 -B1 word', 'Also show 2 lines After and 1 line Before each match (-C for both)', 'grep -A2 ERROR app.log'),
    ('grep -e a -e b', 'Several patterns, a line matching any of them is printed', 'grep -e apple -e kiwi fruits.txt'),
    ('grep -q word', 'Print nothing, only set the exit status (0 found, 1 not found)', 'grep -q root /etc/passwd')])}
{run('grep on the server log', """grep ERROR logs/app.log
grep -c INFO logs/app.log
grep -v INFO logs/app.log
grep -n -i 'logged in' logs/app.log
grep -A1 WARN logs/app.log
grep -r ERROR logs
ls -l | grep '^d'""", note='With -r, grep puts the file name in front of each line. ls -l | grep ^d keeps only folders, because their lines start with d.')}
{note('Put the pattern in single quotes. Then the shell leaves * ? $ and spaces alone and grep receives exactly what you typed.', 'tip')}
{talk('grep is the command engineers type more than almost any other. It reads lines and prints the ones that match a pattern. The name is a fossil from the earliest Unix editor, called ed, where the command g slash r e slash p meant search globally for a regular expression and print. Ken Thompson turned that editor command into a separate program in 1973, and it has been on every Unix system since. The basic use is simple: grep ERROR followed by a log file shows only the error lines. Options make it sharper. Dash i ignores case, dash v shows lines that do not match, dash c counts, dash n numbers the lines and dash r searches a whole folder tree. Dash A and dash B show a few lines after or before each match, which is perfect for seeing what happened just before an error.')}
''', kw=['grep', 'grep -i', 'grep -v', 'grep -c', 'grep -n', 'grep -r', 'grep -l', 'grep -o', 'grep -A', 'grep -q', 'g/re/p'])

K.lesson('basic', 'Regular expressions: the basic building blocks', f'''
<p>A <b>regular expression</b> (regex) is a pattern that describes text. Most characters match themselves, and a few have special meanings.</p>
{fxs(fx('.', 'any one character', 'h.t matches hat, hot and h9t.', key=True),
     fx('*', 'the item before, 0 or more times', 'lo*l matches ll, lol and loooool.'),
     fx('^ and $', 'start and end of the line', '^ERROR matches lines that begin with ERROR. ^$ matches empty lines.', key=True),
     fx('[abc] [a-z] [^0-9]', 'one character from a set', '[aeiou] any vowel. [^0-9] any character that is not a digit.'),
     fx('[[:digit:]] [[:alpha:]] [[:space:]]', 'named classes', 'Work the same in every language setting.'),
     fx('backslash', 'make a special character plain', 'A backslash before a dot makes it a real dot, so the pattern 1 backslash dot 5 matches 1.5 but not 125.'))}
{play('lx-regex')}
{run('Anchors, dots and sets', """grep '^Asha' marks.csv
grep 'a$' fruits.txt
grep 'gr.nd' notes.txt
grep '^[A-Z]' marks.csv | head -n 2
grep '[0-9][0-9]%' logs/app.log
grep -c '^$' poem.txt
grep -o '[[:digit:]]*s$' logs/app.log""", note='^$ counts empty lines (there are none in poem.txt). The last command prints only the "30s" at the end of the timeout line.')}
{note('A regex star is not the shell star. In a file pattern *.txt means "anything". In a regex * means "repeat the item before it", so .* is the regex for "anything".', 'warn')}
{talk('Regular expressions are a tiny language for describing text, and they are worth learning once, because grep, sed, awk, vim, Python, JavaScript and almost every editor understand them. The idea comes from mathematics. In the nineteen fifties Stephen Kleene described patterns with a star meaning repeat, and in 1968 Ken Thompson published a way to search text with them on a computer. The basics are few. A dot means any one character. A star means repeat the thing before me zero or more times. A hat at the start ties the match to the beginning of the line, and a dollar at the end ties it to the end. Square brackets list a set of allowed characters, such as zero to nine for any digit. One warning: the regex star is not the same as the shell star you met with file names. In a regex, dot star is how you say anything at all.')}
''', kw=['regular expression', 'regex', '.', '*', '^', '$', '[a-z]', '[^0-9]', 'character class', '[[:digit:]]', 'escape', 'Kleene'])

K.lesson('extended', 'Extended regular expressions: grep -E', f'''
<p>With <code>grep -E</code> (extended syntax) a few more symbols become special, which makes patterns shorter and easier to read. In plain grep the same features exist, but need a backslash in front: <code>\\+ \\? \\| \\( \\) \\{{ \\}}</code>.</p>
{table(['Extended (grep -E)', 'Basic (grep)', 'Meaning', 'Example'], [
    ['<code>+</code>', '<code>\\+</code>', 'the item before, 1 or more times', '<code>[0-9]+</code> one or more digits'],
    ['<code>?</code>', '<code>\\?</code>', 'the item before is optional', '<code>colou?r</code> matches color and colour'],
    ['<code>{3}</code> <code>{2,4}</code>', '<code>\\{3\\}</code>', 'exact number or range of repeats', '<code>[0-9]{4}</code> four digits, a year'],
    ['<code>a|b</code>', '<code>a\\|b</code>', 'a or b', '<code>ERROR|WARN</code>'],
    ['<code>( )</code>', '<code>\\( \\)</code>', 'group items together', '<code>(ab)+</code> matches ab, abab'],
    ['<code>\\b</code>, <code>\\&lt;</code>, <code>\\&gt;</code>', 'same', 'word boundary, start or end of a word', '<code>\\bcat\\b</code>']])}
{run('Extended patterns at work', """grep -E 'ERROR|WARN' logs/app.log
grep -E '^(Asha|Ravi),' marks.csv
grep -E ',[89][0-9]$' marks.csv
grep -Eo '[0-9]{2}:[0-9]{2}:[0-9]{2}' logs/app.log | head -n 3
grep -Eo 'order [0-9]+' logs/app.log
grep 'ERROR\\|WARN' logs/app.log | wc -l""", note='The last line uses basic syntax, where the | needs a backslash. ,[89][0-9]$ finds marks from 80 to 99 at the end of each line.')}
{deep('Greedy matching and grep -P', '<p>Repetition is <b>greedy</b>: <code>a.*b</code> on "a1b2b" matches the whole "a1b2b", not just "a1b". GNU grep also offers <code>grep -P</code> for Perl compatible expressions with extras such as <code>\\d</code> for a digit, lazy repeats like <code>.*?</code> and look ahead. It is very common in scripts written by Python and JavaScript programmers, but it is not part of POSIX and may be missing on other systems.</p>')}
{lab('Hunt through the log', [
    ('Show every ERROR line of <code>logs/app.log</code>.', 'grep ERROR logs/app.log', [{'cmd': r'grep'}, {'out': '^2026-11-23 09:02:40 ERROR payment failed for order 1042\\n2026-11-23 09:04:18 ERROR database timeout after 30s$'}]),
    ('Count the INFO lines with one option.', 'grep -c INFO logs/app.log', [{'cmd': r'grep\s+-c'}, {'out': '^4$'}]),
    ('Show all lines that are NOT INFO.', 'grep -v INFO logs/app.log', [{'cmd': r'grep\s+-v'}, {'out': 'WARN'}]),
    ('Find lines with ERROR or WARN in one extended pattern.', "grep -E 'ERROR|WARN' logs/app.log", [{'cmd': r'grep\s+(-E|-iE|-Ei)'}, {'out': 'WARN'}, {'out': 'database timeout'}]),
    ('Show the WARN line plus the one line after it.', 'grep -A1 WARN logs/app.log', [{'cmd': r'-A\s*1|-C\s*1'}, {'out': 'payment failed'}]),
    ('Print only the order number part (like <code>order 1042</code>) with grep -o.', "grep -Eo 'order [0-9]+' logs/app.log", [{'cmd': r'-[A-Za-z]*o'}, {'out': '^order 1042$'}]),
    ('List the names of students whose mark is 80 or more, from <code>marks.csv</code>.', "grep -E ',[89][0-9]$' marks.csv | cut -d, -f1", [{'cmd': r'grep'}, {'out': '^Asha\\nMeera\\nAsha$'}]),
    ('Search the whole <code>logs</code> folder for the word timeout.', 'grep -r timeout logs', [{'cmd': r'grep\s+-[a-zA-Z]*r'}, {'out': 'logs/app.log:'}])])}
{talk('Extended regular expressions add a handful of symbols that make patterns much shorter. Plus means one or more, question mark means optional, curly braces give an exact number of repeats, a vertical bar means or, and round brackets group things together. With grep dash E these symbols work directly. In plain grep they exist too, but you must put a backslash in front of each one, which quickly becomes hard to read. So most people simply use grep dash E. With these tools you can describe a date, a time, an order number or an email address in one pattern. For example, four digits, a dash, two digits, a dash, two digits matches a date like the ones in our log file. When you see a long pattern, do not panic. Read it piece by piece from left to right, exactly as the animation in this lesson does.')}
''', kw=['grep -E', 'extended regex', '+', '?', '{n,m}', 'alternation', '|', 'group', 'word boundary', 'greedy', 'grep -P'])

K.lesson('levels', 'grep and regex from school to research', f'''
{ladder(
    '<p>grep finds lines that contain a pattern. A dot means any character, a star means repeat, ^ is the start of the line and $ the end. grep -E adds + ? | and braces for counts.</p>',
    '<p>POSIX defines basic (BRE) and extended (ERE) regular expressions. grep selects lines matching any of its patterns, with options for inversion, counting, context and recursion. Matching uses leftmost longest semantics for ERE in POSIX, while Perl style engines use leftmost first with backtracking.</p>',
    '<p>Regular expressions without back references describe regular languages and can be matched by finite automata in time linear in the input. Thompson built an NFA in 1968. GNU grep compiles patterns to a DFA, skips quickly to candidate lines with a Boyer and Moore style search for fixed strings, and avoids splitting input into lines until a match is found. Back references (<code>\\1</code>) are not regular and force a slower backtracking matcher.</p>',
    '<p>Backtracking engines can take exponential time on patterns like (a+)+$, which caused real outages, for example the Stack Overflow outage of July 2016 and a Cloudflare outage in July 2019 (ReDoS, regular expression denial of service). Research and modern engines such as RE2 and Rust regex guarantee linear time, and tools such as ripgrep combine them with SIMD string search and parallel directory walking.</p>')}
{scene('the 2019 regex outage', '<p>On 2 July 2019 a single new firewall rule containing the regex fragment <code>.*(?:.*=.*)</code> made CPUs on Cloudflare servers worldwide hit 100 percent, and sites behind it returned errors for about 27 minutes. The pattern caused heavy backtracking. Cloudflare later moved its rules to engines that guarantee linear time. Simple patterns and engines like GNU grep or RE2 avoid this class of bug.</p>')}
{talk('Inside, a regular expression is turned into a small machine called a finite automaton, which reads the text one character at a time and never has to go back. Ken Thompson described how to build such a machine in 1968, and GNU grep still uses this approach, together with clever tricks to jump quickly over text that cannot match. That is why grep can search gigabytes in seconds. Some regex engines in programming languages work differently. They try one possibility, and if it fails, go back and try another. For most patterns that is fine, but certain patterns make them try an enormous number of possibilities. In July 2019, one such pattern in a firewall rule pushed Cloudflare servers around the world to full processor load for about twenty seven minutes. Modern engines such as RE2 and the Rust regex library are designed so this cannot happen.')}
''', kw=['BRE', 'ERE', 'finite automaton', 'DFA', 'NFA', 'Boyer Moore', 'backtracking', 'ReDoS', 'RE2', 'ripgrep', 'back reference'])

K.quiz('e', 'What does grep ERROR app.log print?', ['The number of errors', 'Every line of app.log containing ERROR', 'The first error only', 'The file name'], 1, 'Lines that match.', 'grep prints each matching line.')
K.quiz('e', 'Which option makes grep ignore upper and lower case?', ['-v', '-i', '-c', '-n'], 1, 'Ignore case.', '-i ignores case.')
K.quiz('e', 'Which option shows the lines that do NOT match?', ['-v', '-x', '-o', '-l'], 0, 'Invert.', '-v inverts the match.')
K.quiz('e', 'In a regex, what does ^ at the start mean?', ['Any character', 'The start of the line', 'Repeat', 'Not'], 1, 'Anchor.', '^ anchors the match to the start of the line.')
K.quiz('m', 'Which regex matches any single character?', ['*', '.', '?', '$'], 1, 'Dot.', 'A dot matches exactly one character.')
K.quiz('m', 'Which pattern finds empty lines?', ['^$', '$^', '.*', '[ ]'], 0, 'Start right next to end.', '^$ means nothing between the start and the end.')
K.quiz('m', 'What does [^0-9] match?', ['A digit', 'Any one character that is not a digit', 'The start of a number', 'Nothing'], 1, 'A caret inside brackets.', 'Inside [ ], a leading ^ negates the set.')
K.quiz('m', 'Which command finds lines containing ERROR or WARN?', ["grep 'ERROR|WARN'", "grep -E 'ERROR|WARN'", "grep -v ERROR WARN", "grep ERROR,WARN"], 1, 'Extended syntax.', 'In ERE the bar means or. Basic grep needs a backslash before the bar.')
K.quiz('m', 'How do you count how many lines contain "timeout"?', ['grep -n timeout', 'grep -c timeout', 'grep -l timeout', 'grep -o timeout'], 1, 'Count.', '-c prints the number of matching lines.')
K.quiz('h', 'Which regex matches colour and color?', ['colou*r', 'colou?r', 'colo.r', 'col(ou)r'], 1, 'Optional u.', '? makes the u optional (ERE).')
K.quiz('h', 'grep -E \'[0-9]{4}-[0-9]{2}\' matches which?', ['2026-11', '26-11', '2026/11', '202-611'], 0, 'Four digits, dash, two digits.', '{4} repeats the digit class exactly four times.')
K.quiz('h', 'What is the regex for "anything at all" (any text)?', ['*', '.*', '?', '[*]'], 1, 'Any character, repeated.', '. any character, * repeated zero or more times.')
K.quiz('x', 'Why can some regex engines hang on patterns like (a+)+$, while GNU grep does not?', ['GNU grep is newer', 'Backtracking engines may try exponentially many paths, automaton based matchers are linear', 'Because of -E', 'Because of UTF-8'], 1, 'Automata versus backtracking.', 'DFA style matching reads each character once.')

K.calc('e', 'logs/app.log has 7 lines and 4 contain INFO. How many lines does grep -v INFO print?', '3', 'The rest.', ['Total: 7.', 'Matching INFO: 4.', eq('7 − 4 = 3')], check=3)
K.calc('e', 'How many lines of fruits.txt (mango, apple, banana, apple, cherry, mango, apple, kiwi) does grep apple print?', '3', 'Count the apples.', ['apple appears on lines 2, 4 and 7.', 'Each match is one line.', eq('3 lines')], check=3)
K.calc('m', 'How many different strings does [0-9]{3} match?', '1000', 'Ten choices, three times.', ['Each position: 10 digits.', 'Three positions.', eq('10³ = 1000 strings')], check=1000)
K.calc('m', 'How many different strings does [ab][cd]? match?', '6', 'The second part is optional.', ['Without the optional part: 2 (a, b).', 'With it: 2 × 2 = 4.', eq('2 + 4 = 6 strings')], check=6)
K.calc('m', 'grep -A2 ERROR on a log where 2 errors are 10 lines apart. How many lines are printed in total (no separator lines counted)?', '6', 'Each match plus two after.', ['Per match: 1 + 2 = 3 lines.', 'The groups do not overlap.', eq('2 × 3 = 6 lines')], check=6)
K.calc('h', 'A backtracking engine tries 2ⁿ paths for a bad pattern on n characters. With 1 million paths per second, about how many seconds for n = 30 (2³⁰ ≈ 1.07 billion)?', '1074', 'Paths divided by speed.', ['Paths: 2³⁰ ≈ 1,073,741,824.', 'Speed: 1,000,000 per second.', eq('≈ 1074 seconds, almost 18 minutes')], check=1074)

K.must('grep', 'grep PATTERN FILE prints matching lines. -i case, -v invert, -c count, -n numbers, -w words, -o only the match.')
K.must('Searching wider', '-r searches folders, -l lists file names, -A -B -C add context, -q only sets the exit status.')
K.must('Basic regex', '. any char, * repeat, ^ start, $ end, [abc] set, [^abc] not in set, a backslash makes a special character plain. Quote patterns.')
K.must('Extended regex', 'grep -E: + one or more, ? optional, {n,m} counts, | or, ( ) groups. Basic grep needs backslashes.')
K.must('Regex is not glob', 'The shell * means anything, the regex * means repeat. .* is "anything" in a regex.')

T = K.topic(
    slug='grep-regex', topic='grep-regex',
    step=(2, 'Searching and editing text', 'lx-power-2', 'Find lines with grep and regular expressions, change text with sed, and turn columns into reports with awk.', 'Intermediate'),
    title='grep and regular expressions', short='grep and regex', badge='2.1', minutes=45, added='2026-11-23',
    lead='Find exactly the lines you need in files and pipelines with grep, and learn to read and write regular expressions, from a single dot to extended patterns with groups and counts.',
    desc='grep and its main options (-i -v -c -n -w -o -r -l -A -B -C -e -q), basic regular expressions (. * ^ $ sets and classes), extended syntax with grep -E (+ ? {} | ()), greedy matching, grep -P, regex versus shell globs, and how grep matches with automata.',
    summary='grep options, basic and extended regular expressions, anchors, sets, repeats and groups.',
    keywords=['grep', 'regex', 'regular expression', 'grep -E', 'grep -r', 'grep -v', 'anchors', 'character class', 'search text', 'log search'],
    recap='<p>grep prints matching lines, with -i -v -c -n -r -o and context options. Regex: . * ^ $ [ ], and with -E also + ? {} | ( ). Quote patterns and read them piece by piece.</p>')
