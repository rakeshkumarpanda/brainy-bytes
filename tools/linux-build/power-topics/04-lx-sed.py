# Power tools 2.2: sed, the stream editor. The cycle and pattern space, s///flags, & and groups, other delimiters,
# addresses and ranges, d p q i a c y =, -n -E -i. Sources: GNU sed manual (4.9), sed(1), POSIX sed (2024 edition
# added -E), L. E. McMahon, "SED: A Non-interactive Text Editor", Bell Labs, 1978. BSD and macOS sed -i takes a
# required suffix argument (FreeBSD sed(1)).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('idea', 'A stream editor: how sed works', f'''
<p><code>sed</code> (stream editor) changes text as it flows past, without opening an editor. It reads its input one line at a time into a working area called the <b>pattern space</b>, runs your script on that line, prints the result and moves on. By default it prints to stdout and leaves the file untouched.</p>
{steps('One sed cycle, repeated for every line', [
    'Read the next line into the pattern space (without its newline).',
    'Run each command of the script in order, if its address selects this line.',
    'At the end of the script print the pattern space, unless -n was given.',
    'Empty the pattern space and start again with the next line.'])}
{play('lx-sed')}
{run('Three small scripts', """sed 's/apple/APPLE/' fruits.txt
sed '1d' marks.csv
sed -n '2,3p' poem.txt""", note='The first changes the first apple on each line. The second deletes line 1, the header. The third prints only lines 2 and 3, because -n switches off the automatic printing.')}
{talk('sed is short for stream editor. Lee McMahon wrote it at Bell Labs in the early nineteen seventies, so that the editing commands people typed by hand in the ed editor could be applied automatically to text flowing through a pipe. The idea is a loop. sed reads one line into a working area called the pattern space, runs your little script on it, prints the result, and moves on to the next line. It never needs the whole file in memory, so it handles huge files easily. By default it prints to the screen and leaves the original file alone, which makes it safe to experiment. Watch the animation in this lesson closely, because once you understand the cycle, every sed command becomes easy to predict.')}
''', kw=['sed', 'stream editor', 'pattern space', 'sed cycle', 'McMahon', 'non interactive'])

K.lesson('subst', 'Find and replace: the s command', f'''
<p>The command you will use most is <b>s</b> for substitute: <code>s/OLD/NEW/FLAGS</code>. OLD is a regular expression, NEW is the replacement text.</p>
{cmdtable([
    ("s/cat/dog/", 'Replace the first cat on each line', "sed 's/cat/dog/' pets.txt"),
    ("s/cat/dog/g", 'Replace every cat on each line (global)', "sed 's/a/A/g' notes.txt"),
    ("s/cat/dog/2", 'Replace only the second match on each line', "sed 's/a/X/2' fruits.txt"),
    ("s/cat/dog/I", 'Ignore case (GNU)', "sed 's/error/ERR/I' app.log"),
    ("s/milk/oat &/", '&amp; in NEW stands for the whole match', "sed 's/[0-9]*%/(&)/' app.log"),
    ("s|/usr|/opt|", 'Any character can be the delimiter, handy for paths', "sed 's|/home|/srv|' file"),
    ("s/^/# /", 'Insert text at the start of every line', "sed 's/^/# /' config"),
    ("s/ *$//", 'Remove spaces at the end of lines', "sed 's/ *$//' file"),
    ("-E 's/(a)(b)/\\2\\1/'", 'With -E, ( ) capture groups, <code>\\1</code> and <code>\\2</code> put them back', "sed -E 's/(.*),(.*)/\\2 \\1/' f")])}
{run('Substitutions for real', """sed 's/a/A/' notes.txt
sed 's/a/A/g' notes.txt
sed 's/milk/oat &/' notes.txt
sed 's/^/> /' poem.txt
sed 's|/home/|/srv/|' /etc/passwd | tail -n 1
sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\\3.\\2.\\1/' logs/app.log | head -n 2""", note='Without g only the first match on each line changes. The last command reorders the date into day.month.year using three capture groups.')}
{note('Put sed scripts in single quotes, so the shell does not touch $, * or backslashes. If the replacement itself contains the delimiter, choose another one: s|a/b|c/d| is easier to read than escaping every slash with a backslash.', 'tip')}
{talk('The s command, for substitute, is the heart of sed. You write s, slash, what to find, slash, what to put instead, slash. That replaces the first match on each line. Add g at the end, for global, and every match on the line is replaced. The part you search for is a regular expression, so everything from the grep chapter works here. Two tricks make s very powerful. An ampersand in the replacement means the whole text that matched, so you can wrap or extend it instead of retyping it. And with dash capital E, round brackets capture parts of the match, which you can put back in any order with backslash one, backslash two and so on. That is how people reformat dates or swap columns in thousands of lines in one go. If your text contains slashes, such as file paths, use a different delimiter, like a vertical bar.')}
''', kw=['s command', 'substitute', 's///g', 'global', '&', 'capture group', '\\1', 'delimiter', 'sed -E', 'find and replace'])

K.lesson('address', 'Choosing lines: addresses, d, p and friends', f'''
<p>Any command can have an <b>address</b> in front of it, which chooses the lines it works on. Without an address the command runs on every line.</p>
{table(['Address', 'Selects', 'Example'], [
    ['<code>3</code>', 'line 3', "<code>sed '3d'</code>"],
    ['<code>$</code>', 'the last line', "<code>sed -n '$p'</code>"],
    ['<code>/regex/</code>', 'lines matching the regex', "<code>sed '/^#/d'</code> drops comment lines"],
    ['<code>2,5</code>', 'lines 2 to 5', "<code>sed -n '2,5p'</code>"],
    ['<code>/start/,/end/</code>', 'from a line matching start to the next line matching end', "<code>sed '/BEGIN/,/END/d'</code>"],
    ['<code>addr!</code>', 'every line NOT selected', "<code>sed '/maths/!d'</code> keeps maths lines"]])}
{cmdtable([
    ('d', 'Delete the line (nothing printed, next cycle starts)', "sed '/^$/d' file"),
    ('p', 'Print the line now (use with -n)', "sed -n '/ERROR/p' app.log"),
    ('q', 'Quit after this line', "sed '10q' big.log"),
    ('i\\ text', 'Insert a line before', "sed '1i\\ name,score' data"),
    ('a\\ text', 'Append a line after', "sed '$a\\ END' file"),
    ('c\\ text', 'Change (replace) the whole line', "sed '3c\\ new line' file"),
    ('y/abc/xyz/', 'Translate characters, like tr', "sed 'y/abc/ABC/' file"),
    ('=', 'Print the line number', "sed -n '$=' file counts lines"),
    ('cmd1; cmd2', 'Several commands, or -e cmd1 -e cmd2', "sed '/INFO/d; s/ERROR/ALERT/'")])}
{run('Addresses at work', """sed -n '/ERROR/p' logs/app.log
sed '/INFO/d' logs/app.log
sed -n '$p' poem.txt
sed '/maths/!d' marks.csv
sed '/WARN/,/ravi/d' logs/app.log
sed '1i\\Shopping list:' notes.txt
sed -n '$=' fruits.txt
sed '2q' poem.txt""", note='/WARN/,/ravi/d deletes a block from the WARN line down to the line with ravi. sed -n \'$=\' prints the number of the last line, which is the line count.')}
{talk('Every sed command can be aimed at certain lines with an address. A number picks that line, and a dollar sign picks the last one. A regular expression between slashes picks every line that matches. Two addresses with a comma make a range, for example from the line containing BEGIN to the line containing END, which is perfect for removing a whole block from a configuration file. An exclamation mark after the address flips it, so the command runs on all the other lines. The commands themselves are short letters. d deletes the line, p prints it, q stops sed early, and i, a and c insert, append or change whole lines. A very common pair is dash n with p. Dash n turns off the automatic printing, and p prints only the lines you chose, which makes sed work like grep, but with ranges and line numbers as well.')}
''', kw=['address', 'range', '/regex/', '$', 'negation !', 'd delete', 'p print', 'sed -n', 'q quit', 'insert', 'append', 'change', 'y command'])

K.lesson('inplace', 'Editing files in place: sed -i', f'''
<p>sed normally writes to stdout. <code>sed -i</code> writes the result back into the file instead. GNU sed does this by writing a temporary file and renaming it over the original, so the old content is gone unless you ask for a backup.</p>
{cmdtable([
    ("sed -i 's/a/b/' FILE", 'Change FILE in place (GNU sed)', "sed -i 's/8080/9090/' app.conf"),
    ("sed -i.bak 's/a/b/' FILE", 'Change FILE and keep the original as FILE.bak', "sed -i.bak 's/old/new/' site.conf"),
    ("sed -i '' 's/a/b/' FILE", 'The same on macOS and BSD, where -i needs a suffix argument (empty here)', "sed -i '' 's/x/y/' f"),
    ("sed -i '/^#/d' FILE", 'Delete all comment lines from FILE', "sed -i '/^#/d' list.txt")])}
{run('Change a file and keep a backup', """cp notes.txt todo.txt
sed -i.bak 's/grandma/the doctor/' todo.txt
cat todo.txt
cat todo.txt.bak
sed -i -e 's/Buy/Get/' -e '$a\\Walk the dog' todo.txt
cat todo.txt""", note='The .bak file holds the version from before the change. Two -e scripts run one after the other on each line.')}
{steps('A safe routine for editing real configuration files', [
    'Run the sed command without -i first and read the output.',
    'Check that only the intended lines changed, for example with diff: <code>sed \'s/a/b/\' f | diff f -</code>.',
    'Run it again with -i.bak, so a copy of the original remains.',
    'Test the service, then delete the .bak file when you are happy.'])}
{lab('Edit text with sed', [
    ('Print <code>notes.txt</code> with every lower case a changed to A.', "sed 's/a/A/g' notes.txt", [{'cmd': r'sed'}, {'out': 'CAll grAndmA'}]),
    ('Print <code>marks.csv</code> without its first line, using sed.', "sed '1d' marks.csv", [{'cmd': r'sed'}, {'out': '^Asha,maths,91'}]),
    ('Print only line 3 of <code>poem.txt</code>.', "sed -n '3p' poem.txt", [{'cmd': r'sed\s+-n'}, {'out': '^Up above the world so high$'}]),
    ('Show <code>logs/app.log</code> without its INFO lines.', "sed '/INFO/d' logs/app.log", [{'cmd': r'sed'}, {'out': '^2026-11-23 09:01:12 WARN'}]),
    ('Print the log with every date rewritten from 2026-11-23 to 23.11.2026 (use -E and groups).', "sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\\3.\\2.\\1/' logs/app.log", [{'cmd': r'sed\s+-E'}, {'out': '^23\\.11\\.2026 09:00:01'}]),
    ('Change milk to bread inside <code>notes.txt</code> itself, keeping a backup <code>notes.txt.bak</code>.', "sed -i.bak 's/milk/bread/' notes.txt", [{'has': ['notes.txt', 'Buy bread']}, {'has': ['notes.txt.bak', 'Buy milk']}]),
    ('Put <code># </code> in front of every line of <code>poem.txt</code>, in place.', "sed -i 's/^/# /' poem.txt", [{'has': ['poem.txt', '# Twinkle']}, {'has': ['poem.txt', '# Like a diamond']}])])}
{talk('When you are sure the output is right, dash i makes sed write the change back into the file itself. GNU sed does this safely by writing a new file and renaming it over the old one, but the old content is then gone. So it is good practice to write dash i dot bak, which keeps a copy of the original next to it. Watch out for one difference between systems. On macOS and BSD, dash i must be followed by a suffix, so people write dash i and an empty pair of quotes there. A script written on Linux can therefore fail on a Mac. Professionals use a simple routine: run the command without dash i, compare the result, then run it again with a backup, and test the service before removing the backup. That habit has saved many production servers.')}
''', kw=['sed -i', 'in place', 'sed -i.bak', 'backup', 'macOS sed', 'BSD sed', 'multiple -e', 'config edit'])

K.lesson('levels', 'sed from school to research', f'''
{ladder(
    '<p>sed changes text line by line. s/old/new/ replaces the first match, s/old/new/g every match, d deletes lines, -n with p prints chosen lines, and -i saves the change into the file.</p>',
    '<p>sed applies a script to each input line in the pattern space. Commands take zero, one or two addresses (line numbers, $, regular expressions, ranges, negation). The s command supports flags g, p, N and I, &amp; and back references, and -E selects extended regular expressions.</p>',
    '<p>Besides the pattern space sed has a <b>hold space</b>, a second buffer. h and H copy or append the pattern space to it, g and G copy it back, x swaps them, and N appends the next input line. With branches (b, t, labels) sed is Turing complete: people have written a calculator and even games in it. GNU sed -i writes to a temporary file in the same folder and renames it, so the file gets a new inode and hard links to the old one keep the old content.</p>',
    '<p>sed belongs to the family of line based editors that started with QED and ed in the 1960s and 1970s. Structural regular expressions (Rob Pike, 1987, used in the sam editor) generalised the idea from lines to arbitrary text structure. Research on program synthesis, such as FlashFill in Excel (Gulwani, 2011), learns such text transformations from a few examples instead of a hand written script.</p>')}
{scene('the domain move', '<p>A company moves its website from http to https and from old.example.com to example.com. An engineer previews the change on 300 HTML files with <code>grep -rl old.example.com site/ | xargs sed -n \'s|http://old.example.com|https://example.com|gp\'</code>, checks the result, then runs the same with <code>sed -i.bak</code>. Five minutes of work instead of opening 300 files by hand.</p>')}
{talk('Most people only ever use the substitute and delete commands of sed, but there is more inside. Besides the pattern space, sed has a second buffer called the hold space, where it can keep text while it reads further lines. With commands that copy between the two buffers and simple jumps, sed can carry out any computation at all. Hobbyists have written a calculator and even small games in it, just to prove the point. A practical detail matters for system administrators: sed dash i writes a fresh file and renames it, so the edited file is technically a new file. sed comes from a long line of editors that started with QED and ed in the nineteen sixties and seventies. Today researchers go a step further with programs that learn a text transformation from just a few examples, like the Flash Fill feature in Excel, created by Sumit Gulwani at Microsoft Research.')}
''', kw=['hold space', 'N', 'h H g G x', 'branch', 'Turing complete', 'inode', 'structural regular expressions', 'FlashFill'])

K.quiz('e', 'What does sed \'s/cat/dog/\' do on each line?', ['Deletes cat', 'Replaces the first cat with dog', 'Replaces every cat', 'Counts cats'], 1, 'Substitute once.', 'Without g only the first match on each line is replaced.')
K.quiz('e', 'Which flag replaces every match on a line?', ['p', 'g', 'i', 'n'], 1, 'Global.', 'g makes the substitution global within the line.')
K.quiz('e', 'Does sed change the file by default?', ['Yes, always', 'No, it prints the result to stdout', 'Only for .txt files', 'Only as root'], 1, 'Stream editor.', 'Only -i writes back into the file.')
K.quiz('e', 'Which command deletes line 1?', ["sed '1d'", "sed 'd1'", "sed '1p'", "sed -n 1"], 0, 'Address then command.', 'The address 1 selects line 1, d deletes it.')
K.quiz('m', 'Which prints only lines that contain ERROR?', ["sed '/ERROR/p'", "sed -n '/ERROR/p'", "sed '/ERROR/d'", "sed 's/ERROR//'"], 1, 'Turn off auto print.', 'Without -n every line would print and the matches twice.')
K.quiz('m', 'In sed \'s/[0-9]*%/(&)/\', what does & stand for?', ['A literal ampersand', 'The whole text that matched', 'The line number', 'A newline'], 1, 'The match.', '& in the replacement is the matched text.')
K.quiz('m', 'You must replace /usr/local with /opt. Which is easiest to read?', ['Put a backslash before every slash of the paths', "sed 's|/usr/local|/opt|'", "sed 'y/usr/opt/'", "sed '/usr/d'"], 1, 'Change the delimiter.', 'Any character can follow s as the delimiter, so the slashes in the paths need no escaping.')
K.quiz('m', 'What does sed \'/maths/!d\' marks.csv print?', ['Lines without maths', 'Only the lines containing maths', 'Nothing', 'Line numbers'], 1, '! inverts the address.', 'd runs on every line that does not match, so only maths lines remain.')
K.quiz('m', 'What does sed -i.bak \'s/a/b/\' f do?', ['Prints the change', 'Changes f and saves the original as f.bak', 'Creates f.bak only', 'Fails'], 1, 'In place with backup.', '-i with a suffix keeps a backup copy.')
K.quiz('h', 'Which command prints the number of lines in a file?', ["sed -n '$='", "sed '$d'", "sed -n '1p'", "sed '='"], 0, 'Line number of the last line.', "= prints the line number, $ selects the last line.")
K.quiz('h', 'With sed -E, which brackets capture part of a match so the replacement can reuse it?', ['( )', '[ ]', '{ }', '< >'], 0, 'Groups.', 'Round brackets capture a group, and a backslash with its number puts it back.')
K.quiz('h', 'A script written for GNU sed uses sed -i \'s/a/b/\' f. What happens on macOS?', ['It works the same', 'macOS sed takes the script as the backup suffix and fails or misbehaves, it needs sed -i \'\'', 'It deletes f', 'It asks for a password'], 1, 'BSD sed -i needs an argument.', 'On BSD and macOS the suffix argument of -i is required.')
K.quiz('x', 'What is the sed hold space?', ['A swap file', 'A second buffer that keeps text between cycles, used with h, H, g, G and x', 'The output file', 'The regex cache'], 1, 'Second buffer.', 'The hold space lets sed work across lines.')

K.calc('e', "A file has 50 lines. How many lines does sed '1d' print?", '49', 'One line fewer.', ['Lines: 50.', 'Deleted: 1.', eq('50 − 1 = 49')], check=49)
K.calc('e', "How many lines does sed -n '10,24p' print from a 100 line file?", '15', 'Count both ends.', ['From line 10 to line 24.', 'Count = 24 − 10 + 1.', eq('15 lines')], check=15)
K.calc('m', "The line 'banana' goes through sed 's/a/X/g'. How many X characters are in the result?", '3', 'Count the a letters.', ['banana has the letters b a n a n a.', 'Every a becomes X with g.', eq('3 X characters: bXnXnX')], check=3)
K.calc('m', "Same line, but sed 's/a/X/2'. Which position (1 to 6) holds the X?", '4', 'Only the second a.', ['The a letters are at positions 2, 4 and 6.', 'Flag 2 replaces only the second one.', eq('Position 4: banXna')], check=4)
K.calc('m', "A config has 120 lines, 35 of them comments starting with #, and 10 empty lines. How many lines does sed -e '/^#/d' -e '/^$/d' print?", '75', 'Remove both kinds.', ['Comment lines: 35.', 'Empty lines: 10.', eq('120 − 35 − 10 = 75 lines')], check=75)
K.calc('h', 'sed -i.bak runs on 300 files of 40 KB each. How many megabytes of backups appear (1 MB = 1000 KB)?', '12', 'One backup per file.', ['Backups: 300 files.', 'Each 40 KB: 300 × 40 = 12,000 KB.', eq('12,000 KB = 12 MB')], check=12)

K.must('Cycle', 'sed reads a line into the pattern space, runs the script, prints it (unless -n), and repeats. The file is not changed without -i.')
K.must('Substitute', 's/old/new/ first match, /g all, /2 the second, /I ignore case. & is the match. With -E, ( ) capture groups that a backslash and a number put back.')
K.must('Addresses', '3, $, /regex/, 2,5 and /a/,/b/ ranges, ! to invert. sed -n \'/x/p\' works like grep.')
K.must('Commands', 'd delete, p print, q quit, i a c insert, append, change, y translate, = line number. Give several with -e or separate them with a semicolon.')
K.must('In place', 'sed -i edits the file, sed -i.bak keeps a backup. macOS needs sed -i \'\'. Preview without -i first.')

T = K.topic(
    slug='sed', topic='sed',
    step=(2, 'Searching and editing text', 'lx-power-2', 'Find lines with grep and regular expressions, change text with sed, and turn columns into reports with awk.', 'Intermediate'),
    title='sed: the stream editor', short='sed', badge='2.2', minutes=45, added='2026-11-23',
    lead='Change text without opening an editor: find and replace with regular expressions, delete or print chosen lines, and safely edit files in place, line by line, as the text streams past.',
    desc='The sed cycle and pattern space, the s command with g, N, I and p flags, & and capture groups with -E, other delimiters, addresses, ranges and negation, d p q i a c y and =, -n, -i and -i.bak, the macOS difference, the hold space, and where sed came from.',
    summary='The sed cycle, s/old/new/g, addresses and ranges, d and p, -n, -E and -i.',
    keywords=['sed', 'stream editor', 'find and replace', 's///g', 'sed -i', 'sed -n', 'addresses', 'regex replace', 'delete lines'],
    recap='<p>sed runs a script on each line. s/old/new/g replaces, addresses choose lines, d deletes, -n with p prints chosen lines, and -i.bak edits the file with a backup.</p>')
