# Foundations 2.3: reading and inspecting files. cat, tac, less, head, tail (-n, -n +N, -f, -F), wc, nl, file, stat,
# diff, cmp, od. Sources: GNU coreutils manual (cat, tac, head, tail, wc, nl, stat, od), less(1) by Mark Nudelman,
# file(1) and magic(5), GNU diffutils manual (diff normal format, cmp).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('cat', 'Printing a whole file: cat and friends', f'''
<p><code>cat</code> prints files to the screen. Its name comes from con<b>cat</b>enate, which means joining things end to end. Give it two files and it prints the first one followed by the second one, with nothing in between.</p>
{cmdtable([
    ('cat FILE', 'Print the whole file', 'cat notes.txt'),
    ('cat A B', 'Print A, then B, joined', 'cat notes.txt poem.txt'),
    ('cat -n FILE', 'Number every line', 'cat -n poem.txt'),
    ('cat -A FILE', 'Show hidden characters: $ marks a line end, ^I marks a tab', 'cat -A notes.txt'),
    ('tac FILE', 'Print the lines in reverse order, last line first', 'tac poem.txt'),
    ('nl FILE', 'Number the lines that are not empty', 'nl poem.txt')])}
{run('Reading the starting files', """cat notes.txt
cat -n poem.txt
tac poem.txt
cat notes.txt poem.txt""")}
{run('Seeing the invisible', """printf 'one\\ttwo\\nthree  \\n' > odd.txt
cat odd.txt
cat -A odd.txt""", note='The file holds a tab and two spaces at the end of a line. On screen they look the same as ordinary spaces, but cat -A shows the tab as ^I and puts a $ where each line ends, so the two trailing spaces become visible.')}
{note('cat is fine for short files. For a file with thousands of lines the text flies past and only the end stays on screen. Use less for that, as the next lesson shows.', 'tip')}
{talk('The first command most people learn for reading a file is cat. It sounds like the animal, but it is short for concatenate, which simply means joining things together. Ken Thompson wrote it for the very first version of Unix in 1971, and it has barely changed since. If you give cat one file, it prints that file. If you give it two, it prints them one after the other, which is handy for joining parts of a document. Two small options are worth remembering. Dash n puts a number in front of every line, which helps when someone says the problem is on line forty. Dash capital A shows characters you normally cannot see, such as tabs and spaces at the end of a line. Those invisible characters cause real bugs, for example in configuration files where a tab and a space mean different things.')}
''', kw=['cat', 'concatenate', 'cat -n', 'cat -A', 'tac', 'nl', 'print file', 'hidden characters'])

K.lesson('less', 'Reading long files page by page: less', f'''
<p><code>less</code> opens a file one screen at a time and lets you move around and search. It reads only what it needs, so it opens a huge log instantly. It never changes the file. The name is a joke on the older pager <code>more</code>, which could only move forwards: less can do more than more.</p>
{cmdtable([
    ('Space or f', 'Next page', 'Space'),
    ('b', 'Back one page', 'b'),
    ('Down or j, Up or k', 'One line down or up', 'j'),
    ('g and G', 'Jump to the first line, or to the last line', 'G'),
    ('/word', 'Search forwards for word', '/ERROR'),
    ('?word', 'Search backwards', '?login'),
    ('n and N', 'Next match, previous match', 'n'),
    ('F', 'Follow the end of a growing file, like tail -f (Ctrl+C stops following)', 'F'),
    ('h', 'Help screen with every key', 'h'),
    ('q', 'Quit and go back to the prompt', 'q')], head=('Key inside less', 'What it does', 'Example'))}
{cmdtable([
    ('less FILE', 'Open a file', 'less logs/app.log'),
    ('less -N FILE', 'Show line numbers', 'less -N poem.txt'),
    ('less -S FILE', 'Chop long lines instead of wrapping them, scroll sideways with the arrow keys', 'less -S marks.csv'),
    ('less +G FILE', 'Open the file at its end', 'less +G logs/app.log'),
    ('less -i FILE', 'Searches ignore upper and lower case, unless the search has capitals', 'less -i logs/app.log')])}
{sample('A screen of less', 'less /var/log/syslog', """Nov 23 09:00:00 brainy systemd[1]: Started Daily apt download activities.
Nov 23 09:00:02 brainy CRON[812]: (root) CMD (run-parts /etc/cron.hourly)
Nov 23 09:00:05 brainy kernel: [  412.118230] usb 1-1: new high-speed USB device
...
/var/log/syslog lines 1-40/1832 2%""", note='The last line shows the file name, which lines are on screen and how far through the file you are. Press q to leave.')}
{note('When the output of less goes to a pipe or a file instead of a screen, less behaves like cat and copies everything. The man command uses less to show manual pages, so the same keys work there.', 'tip')}
{talk('Imagine a log file with two million lines. cat would pour all of it across your screen in a few seconds, and you would only see the very end. less solves this. It shows one screen, then waits for you. Space goes forward, b goes back, and slash followed by a word searches, which is what you will use most. Press n to jump to the next match and q to quit. The program was written by Mark Nudelman, starting in 1983, because the older pager called more could only move forwards. So less can do more than more, and the joke name stuck. You have already used less without knowing it, because the man command shows manual pages inside it. One more useful key is capital F. It keeps the end of the file on screen and shows new lines as they arrive, which is perfect for watching a server log while you test a web page.')}
''', kw=['less', 'pager', 'more', 'search in file', '/pattern', 'less -N', 'less -S', 'less F follow'])

K.lesson('headtail', 'The start and the end: head and tail', f'''
<p>Often you only need a few lines. <code>head</code> prints the start of a file and <code>tail</code> prints the end. Both show 10 lines unless you say otherwise.</p>
{fxs(fx('head -n N', 'first N lines', 'head -n 3 logs/app.log shows the oldest three log lines.', key=True),
     fx('tail -n N', 'last N lines', 'tail -n 2 logs/app.log shows the two newest entries.', key=True),
     fx('tail -n +N', 'from line N to the end', 'tail -n +2 marks.csv skips the header line of a CSV file.'),
     fx('tail -f', 'keep watching', 'Prints new lines as they are added, until you press Ctrl+C.'))}
{play('lx-headtail')}
{run('head and tail, run for real', """head -n 3 logs/app.log
tail -n 2 logs/app.log
tail -n +2 marks.csv
head -c 8 notes.txt; echo
head -n 2 notes.txt poem.txt""", note='With more than one file, head prints a ==> name <== line before each one. head -c counts bytes instead of lines, and the echo only adds the missing line end.')}
{sample('Watching a live log', 'tail -f /var/log/nginx/access.log', """203.0.113.7 - - [23/Nov/2026:09:31:02 +0000] "GET / HTTP/1.1" 200 612 "-" "Mozilla/5.0"
203.0.113.7 - - [23/Nov/2026:09:31:02 +0000] "GET /style.css HTTP/1.1" 200 1048 "-" "Mozilla/5.0"
198.51.100.23 - - [23/Nov/2026:09:31:09 +0000] "GET /login HTTP/1.1" 200 2210 "-" "curl/8.5.0"
^C""", note='Each time someone opens a page, a new line appears. Ctrl+C stops watching. The addresses come from the ranges reserved for examples.')}
{note('Logs are often rotated: app.log is renamed to app.log.1 and a new app.log starts. tail -f keeps reading the old renamed file and goes quiet. tail -F follows the name, notices the new file and continues with it.', 'warn')}
{lab('Read the server log', [
    ('Print the whole of <code>notes.txt</code>.', 'cat notes.txt', [{'cmd': r'^\s*cat\s+notes\.txt\s*$'}]),
    ('Show the first 3 lines of <code>logs/app.log</code>.', 'head -n 3 logs/app.log', [{'cmd': r'^\s*head\s+(-n\s*3|-3)\s+logs/app\.log'}, {'out': 'server started'}]),
    ('Show only the last line of <code>logs/app.log</code>.', 'tail -n 1 logs/app.log', [{'cmd': r'^\s*tail\s+(-n\s*1|-1)\s+logs/app\.log'}, {'out': 'backup finished'}]),
    ('Print <code>marks.csv</code> without its header line.', 'tail -n +2 marks.csv', [{'cmd': r'^\s*tail\s+-n\s*\+2\s+marks\.csv'}, {'out': 'Asha,maths,91'}]),
    ('Count the lines of <code>fruits.txt</code>.', 'wc -l fruits.txt', [{'cmd': r'^\s*wc\s+-l\s+fruits\.txt'}, {'out': '8 fruits.txt'}]),
    ('Print <code>poem.txt</code> with line numbers.', 'cat -n poem.txt', [{'cmd': r'^\s*(cat\s+-n|nl)\s+poem\.txt'}, {'out': '4\tLike a diamond'}]),
    ('Print <code>poem.txt</code> upside down, last line first.', 'tac poem.txt', [{'cmd': r'^\s*tac\s+poem\.txt'}])])}
{talk('head and tail are two of the most used commands on any server. head shows the beginning of a file, tail shows the end, and both default to ten lines. The dash n option chooses another number. A trick worth remembering is tail with a plus sign. tail dash n plus two means start at line two and print everything after it, which is the standard way to drop the header row of a spreadsheet file. The most loved option is dash f, for follow. An engineer who is testing a website runs tail dash f on the web server log and watches each visit appear the moment it happens. If something breaks, the error appears right there in the terminal. Use capital F on servers whose logs are rotated each night, because it notices when a fresh log file replaces the old one.')}
''', kw=['head', 'tail', 'head -n', 'tail -n', 'tail -n +2', 'tail -f', 'tail -F', 'log rotation', 'first lines', 'last lines'])

K.lesson('inspect', 'Measuring and comparing files: wc, file, stat, diff', f'''
{cmdtable([
    ('wc FILE', 'Count lines, words and bytes', 'wc logs/app.log'),
    ('wc -l FILE', 'Count lines only', 'wc -l fruits.txt'),
    ('file FILE', 'Guess what kind of data a file holds by reading its first bytes', 'file scripts/hello.sh'),
    ('stat FILE', 'Show size, owner, permissions, inode and times', 'stat notes.txt'),
    ('diff A B', 'Show the lines that differ between two text files', 'diff old.txt new.txt'),
    ('cmp A B', 'Report the first byte where two files differ, works for any file', 'cmp a.bin b.bin'),
    ('od -c FILE', 'Dump every byte, with special characters spelled out', 'od -c notes.txt')])}
{run('Counting', """wc logs/app.log
wc -l fruits.txt poem.txt
wc -w poem.txt""", note='wc prints lines, then words, then bytes. A word is anything between spaces, tabs or line ends. With several files you also get a total line.')}
{run('What is inside, and its details', """file notes.txt logs scripts/hello.sh latest.log
stat notes.txt""", note='file never trusts the name. It reads the first bytes and compares them with a list of known signatures called magic numbers, for example every PNG image starts with the bytes 89 50 4E 47. stat shows the inode number and three times: Access (last read), Modify (content changed) and Change (details such as permissions changed). The Birth line appears only on file systems that record creation time.')}
{run('Spotting the difference', """printf 'milk\\neggs\\nbread\\n' > monday.txt
printf 'milk\\nbutter\\nbread\\njam\\n' > tuesday.txt
diff monday.txt tuesday.txt
diff -u monday.txt tuesday.txt
cmp monday.txt tuesday.txt""", note='In the normal format, 2c2 means line 2 changed into line 2, and 3a4 means a line was added after line 3. Lines starting with &lt; come from the first file and lines with &gt; from the second. The -u unified format with - and + is what Git and code review tools show.')}
{run('Every single byte', """od -c notes.txt | head -n 3""", note='od shows that a line end is one byte, written <code>\\n</code>. Files from Windows often end lines with two bytes, carriage return then newline (<code>\\r\\n</code>), which is why some scripts break after a file is copied from Windows.')}
{talk('Sometimes you need facts about a file rather than its words. wc counts lines, words and bytes. Engineers use wc dash l all the time, for example to count how many errors happened today or how many users are in a list. The file command answers the question what is this thing. It ignores the name and reads the first few bytes, because most formats begin with a fixed signature, called a magic number. A picture renamed to report dot txt is still reported as a picture. stat prints the details the system keeps about a file, such as owner, size, permissions and times. Finally, diff compares two text files and prints only the lines that changed. The original diff was written for Unix in the early nineteen seventies, and its descendants power every code review today. When you see minus and plus lines in Git, you are looking at diff output.')}
''', kw=['wc', 'wc -l', 'file', 'magic number', 'stat', 'inode', 'mtime', 'ctime', 'diff', 'diff -u', 'cmp', 'od', 'line endings'])

K.lesson('levels', 'Reading files from school to research', f'''
{ladder(
    '<p>cat prints a file, less lets you scroll and search, head shows the start, tail shows the end, wc counts lines and words, and diff shows what changed between two versions.</p>',
    '<p>These tools read files as streams of bytes divided into lines by the newline character. head and tail select by line or byte count, tail -f polls or watches the file for growth, file identifies formats by magic numbers in magic(5), and diff computes a shortest edit script between two line sequences.</p>',
    '<p>cat loops over read() and write() system calls. GNU tail on a seekable file seeks near the end and reads backwards in blocks, so tail -n 5 on a 50 GB log is instant. On Linux tail -f uses inotify to sleep until the file changes. less keeps an index of line positions and reads only the regions it displays. GNU diff uses the O(ND) algorithm published by Eugene Myers in 1986, where D is the number of differences, so similar files are compared quickly.</p>',
    '<p>Research topics include diff algorithms that produce more readable results (patience and histogram diff in Git), structural diffs that compare syntax trees instead of lines, file type identification with machine learning when magic numbers are missing (Google Magika, 2024), and log analysis at scale, where systems such as the ELK stack index billions of lines that tail could never handle alone.</p>')}
{scene('the 3 a.m. incident', '<p>A shopping site starts failing at night. The on-call engineer logs in and runs <code>tail -n 50 /var/log/app/error.log</code> to see the latest errors, then <code>grep -c timeout</code> on the same file to count them, and finally <code>tail -F</code> to watch whether new errors keep coming after a restart. Every command here is in this chapter or the next one.</p>')}
{talk('How does tail show the last five lines of a fifty gigabyte file without reading all fifty gigabytes. GNU tail jumps straight to the end of the file and reads backwards in blocks until it has found enough line endings. That is why it answers instantly. When you follow a file, modern Linux lets tail sleep until the kernel says the file has changed, using a feature called inotify, instead of checking again and again. diff hides clever mathematics too. In 1986 Eugene Myers published an algorithm whose cost depends mostly on how many differences there are, so two nearly identical files are compared very fast. That algorithm still sits inside GNU diff and inside Git. Researchers keep improving the ideas, for example with diffs that understand program structure, and with machine learning models that recognise file types when the usual signatures are missing.')}
''', kw=['read system call', 'seek', 'inotify', 'Myers diff', 'patience diff', 'Magika', 'log analysis'])

K.quiz('e', 'Which command prints a whole short file to the screen?', ['cat', 'head', 'cd', 'mkdir'], 0, 'Concatenate.', 'cat prints whole files.')
K.quiz('e', 'How many lines does tail print when you give no number?', ['1', '5', '10', 'All of them'], 2, 'Same default as head.', 'head and tail both default to 10 lines.')
K.quiz('e', 'Which key quits less?', ['x', 'q', 'Esc', 'Ctrl+Q'], 1, 'Q for quit.', 'q leaves less and returns to the prompt.')
K.quiz('e', 'Which command counts the lines of a file?', ['wc -l', 'cat -l', 'count', 'nl -c'], 0, 'Word count with -l.', 'wc -l prints the number of lines.')
K.quiz('m', 'You want everything in data.csv except the first header line. Which command?', ['head -n 1 data.csv', 'tail -n +2 data.csv', 'tail -n 2 data.csv', 'cat -n data.csv'], 1, 'Start from line 2.', 'tail -n +2 starts at line 2 and prints to the end.')
K.quiz('m', 'Inside less, how do you search forwards for the word ERROR?', ['Type /ERROR and press Enter', 'Press s then ERROR', 'Ctrl+F ERROR', 'grep ERROR'], 0, 'Slash searches.', '/ starts a forward search, n jumps to the next match.')
K.quiz('m', 'file says holiday.txt is "JPEG image data". What does that tell you?', ['file is broken', 'The content is a JPEG picture, whatever the name says', 'The file is empty', 'It is a text file'], 1, 'file reads bytes, not names.', 'file checks magic numbers at the start of the content.')
K.quiz('m', 'diff prints 3a4 > jam. What happened?', ['Line 3 was deleted', 'A line "jam" was added after line 3, becoming line 4 of the second file', 'Line 4 changed', 'The files are equal'], 1, 'a means add.', 'In normal diff format, a is add, d is delete and c is change.')
K.quiz('m', 'Which command shows tabs as ^I and line ends as $?', ['cat -n', 'cat -A', 'less -S', 'tac'], 1, 'Show All.', 'cat -A makes invisible characters visible.')
K.quiz('h', 'A log is renamed every night and a new one is started. Which keeps following the new file?', ['tail -f', 'tail -F', 'less', 'head -f'], 1, 'Follow the name.', 'tail -F follows the file name and retries when the file is replaced.')
K.quiz('h', 'wc -l reports 0 for a file that clearly shows one line of text. Most likely reason?', ['The file is binary', 'The only line has no newline character at its end', 'wc is broken', 'The file is hidden'], 1, 'wc counts newlines.', 'wc -l counts newline characters, so a final line without one is not counted.')
K.quiz('h', 'Which stat time changes when you run chmod on a file, but not when you only read it?', ['Access', 'Modify', 'Change', 'Birth'], 2, 'Details, not content.', 'ctime (Change) records changes to the inode, such as permissions.')
K.quiz('x', 'Why is tail -n 5 on a 50 GB log almost instant?', ['It is cached', 'It seeks to the end and reads backwards in blocks until it finds 5 newlines', 'It reads in parallel', 'It only reads the first 5 lines'], 1, 'No need to read the beginning.', 'GNU tail seeks near the end of a regular file.')

K.calc('e', 'head -n 3 on a file of 20 lines, followed by tail -n 3 on the same file. How many lines are printed in total?', '6', 'Three from each end.', ['head gives 3 lines.', 'tail gives 3 lines.', eq('3 + 3 = 6 lines')], check=6)
K.calc('e', 'marks.csv has 7 lines including one header. How many lines does tail -n +2 marks.csv print?', '6', 'Every line except the first.', ['Total lines: 7.', 'Skip line 1.', eq('7 − 1 = 6 lines')], check=6)
K.calc('m', 'less shows 40 lines per screen. How many presses of Space take you from the first screen to the screen that shows line 200?', '4', 'Each press moves 40 lines.', ['Screen 1 shows lines 1 to 40.', 'After k presses you see lines 40k+1 to 40k+40.', 'Need 40k+40 ≥ 200, so k ≥ 4.', eq('4 presses (lines 161 to 200)')], check=4)
K.calc('m', 'A log grows by 12 lines per minute. tail -f has run for 15 minutes. How many new lines has it printed?', '180', 'Rate times time.', ['Rate: 12 lines per minute.', 'Time: 15 minutes.', eq('12 × 15 = 180 lines')], check=180)
K.calc('m', 'A text file has 4 lines of 9 characters each, plus a newline after every line. How many bytes does wc -c report?', '40', 'Count the newlines too.', ['Characters: 4 × 9 = 36.', 'Newlines: 4.', eq('36 + 4 = 40 bytes')], check=40)
K.calc('h', 'The same file is converted to Windows line ends, where each line ends with a carriage return byte plus the newline byte. How many bytes now?', '44', 'One extra byte per line.', ['Before: 40 bytes.', 'Each of the 4 lines gains one carriage return byte.', eq('40 + 4 = 44 bytes')], check=44)

K.must('cat and less', 'cat prints whole files (cat -n numbers lines, cat -A shows hidden characters). less pages through big files: Space, b, /word, n, q.')
K.must('head and tail', 'Both default to 10 lines. -n N chooses another number, tail -n +N starts at line N.')
K.must('Follow', 'tail -f watches a growing file. tail -F also survives log rotation. Ctrl+C stops.')
K.must('Measure', 'wc counts lines, words and bytes. wc -l counts newline characters. file reads magic numbers, not names. stat shows metadata.')
K.must('Compare', 'diff shows changed lines (c change, a add, d delete, or - and + with -u). cmp finds the first differing byte.')

T = K.topic(
    slug='read-files', topic='read-files',
    step=(2, 'Files and folders', 'lx-basics-2', 'The single file tree, paths, making, copying, moving and deleting files and folders, wildcards, and reading files.', 'Beginner'),
    title='Reading and inspecting files', short='Reading files', badge='2.3', minutes=30, added='2026-11-23',
    lead='Print short files, page through huge ones, grab the first or last lines, watch a live log, and measure and compare files like an engineer on call.',
    desc='cat, tac, nl and cat -A, less and its keys, head and tail with -n, -n +N, -f and -F, wc, file and magic numbers, stat and the three file times, diff and diff -u, cmp and od, and how tail and diff work inside.',
    summary='cat, less, head, tail -f, wc, file, stat and diff.',
    keywords=['cat', 'less', 'head', 'tail', 'tail -f', 'wc', 'file', 'stat', 'diff', 'read file', 'log file'],
    recap='<p>cat for short files, less for long ones, head and tail for the ends, tail -F for live logs, wc to count, file and stat for facts, and diff to compare.</p>')
