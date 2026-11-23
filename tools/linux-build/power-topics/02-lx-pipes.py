# Power tools 1.2: pipes and filters. The | operator, the Unix philosophy, sort, uniq, cut, tr, wc, head and tail in
# pipelines, exit status of a pipeline, PIPESTATUS and pipefail, SIGPIPE. Sources: bash(1) Pipelines, GNU coreutils
# manual (sort, uniq, cut, tr, wc), pipe(7) (65536 byte capacity since Linux 2.6.11), signal(7) SIGPIPE,
# M. D. McIlroy et al., "UNIX Time-Sharing System: Foreword", Bell System Technical Journal 57(6), 1978,
# J. Bentley, "Programming Pearls: A Literate Program", CACM 29(6), June 1986 (McIlroy's word count pipeline).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('pipe', 'The pipe: one command feeds the next', f'''
<p>The <b>pipe</b> <code>|</code> connects the stdout of one command to the stdin of the next. No temporary file is needed: data flows straight from one program into the other while both run.</p>
{fxs(fx('A | B', 'pipe', 'The output of A becomes the input of B. Errors (stream 2) still go to the terminal.', key=True),
     fx('A | B | C | D', 'pipeline', 'Any number of commands. Each one does a small job.'),
     fx('A 2>&1 | B', 'errors too', 'Send stderr into the pipe as well. Bash also accepts A |& B.'))}
{run('Your first pipelines', """ls /etc | head -n 5
cat fruits.txt | sort
sort fruits.txt | uniq
ls /usr/bin | wc -l""", note='ls /usr/bin | wc -l counts the programs in /usr/bin of the machine that built this page, so your number will differ.')}
{play('lx-pipe')}
{note('A command that reads a file name never needs cat in front of it: sort fruits.txt does the same as cat fruits.txt | sort with one process less. cat is still handy to start a long pipeline in a readable way.', 'tip')}
{talk('The pipe is the single most famous idea in Unix. The vertical bar takes the output of one command and feeds it directly into the next one, with no file in between. Doug McIlroy at Bell Labs pushed for this for years, and Ken Thompson added pipes to Unix in 1973, reportedly in a single night. Overnight, the small tools that already existed could be combined into new ones. McIlroy later summed up the Unix way of thinking: write programs that do one thing and do it well, and write programs that work together. A pipeline is exactly that. ls lists, head keeps the first lines, sort sorts, wc counts. None of them knows about the others, yet together they answer questions nobody planned for. Notice that error messages are not sent down the pipe. They still go to your screen, so you see problems while the data keeps flowing.')}
''', kw=['pipe', '|', 'pipeline', 'stdout to stdin', 'Unix philosophy', 'McIlroy', '|&'])

K.lesson('sort', 'Sorting and counting: sort, uniq, wc', f'''
{cmdtable([
    ('sort', 'Sort lines by text', 'sort names.txt'),
    ('sort -n', 'Sort by number, so 9 comes before 10', 'sort -n sizes.txt'),
    ('sort -r', 'Reverse the order', 'sort -rn scores.txt'),
    ('sort -t, -k3', 'Split fields at commas and sort by field 3', 'sort -t, -k3 -n marks.csv'),
    ('sort -u', 'Sort and keep one copy of each line', 'sort -u emails.txt'),
    ('sort -h', 'Sort human sizes like 2K, 15M, 1G (GNU)', 'du -sh * | sort -h'),
    ('uniq', 'Remove repeated lines that are next to each other', 'sort list | uniq'),
    ('uniq -c', 'Count each run of repeated lines', 'sort list | uniq -c'),
    ('uniq -d', 'Show only lines that appear more than once', 'sort list | uniq -d'),
    ('wc -l', 'Count lines', 'ls | wc -l')])}
{run('Text order and number order', """printf '10\\n9\\n100\\n25\\n' > nums.txt
sort nums.txt
sort -n nums.txt
sort -rn nums.txt""", note='Plain sort compares characters from the left, so "100" comes before "25" and "9" comes last. sort -n compares numbers.')}
{run('Counting things', """uniq fruits.txt
sort fruits.txt | uniq -c
sort fruits.txt | uniq -c | sort -rn | head -n 2
sort -t, -k3 -rn marks.csv | head -n 3""", note='uniq only removes repeats that sit next to each other, so on the unsorted file it removes nothing. Sort first. The last line sorts the CSV by its third field, the score.')}
{note('sort uses the rules of your language setting (locale), which can put capitals and small letters together. Scripts that need the same order everywhere run LC_ALL=C sort, which compares plain byte values.', 'tip')}
{talk('sort and uniq are a famous pair. sort puts lines in order. By default it compares text from the left, letter by letter, which surprises people with numbers: one hundred comes before twenty five, because the character one comes before two. Add dash n to sort by numeric value, dash r to reverse, and dash k to pick a column. uniq removes repeated lines, but only when the repeats are next to each other. That is why you almost always see sort followed by uniq. With dash c, uniq counts how many times each line appeared. Then a final sort dash r n puts the most common at the top. This short recipe, sort, uniq dash c, sort dash r n, head, is used every day to find the most frequent visitors in a web log, the commonest errors, or the most popular products.')}
''', kw=['sort', 'sort -n', 'sort -r', 'sort -k', 'sort -t', 'sort -u', 'sort -h', 'uniq', 'uniq -c', 'uniq -d', 'top N', 'locale'])

K.lesson('cut', 'Slicing and changing text: cut and tr', f'''
{cmdtable([
    ('cut -d, -f1', 'Field 1 of comma separated lines', 'cut -d, -f1 marks.csv'),
    ('cut -d: -f1,7', 'Fields 1 and 7, separated by colons', 'cut -d: -f1,7 /etc/passwd'),
    ('cut -c1-8', 'Characters 1 to 8 of each line', 'cut -c1-10 app.log'),
    ('tr a-z A-Z', 'Translate characters: small letters to capitals', 'tr a-z A-Z < poem.txt'),
    ("tr -d '0-9'", 'Delete every digit', "tr -d '0-9' < file"),
    ("tr -s ' '", 'Squeeze runs of spaces into one', "tr -s ' ' < file"),
    ("tr ' ' '\\n'", 'Turn spaces into newlines, one word per line', "tr ' ' '\\n' < poem.txt")])}
{run('Columns and characters', """cut -d, -f1 marks.csv
cut -d, -f1 marks.csv | tail -n +2 | sort -u
cut -d: -f1,7 /etc/passwd | head -n 3
cut -c12-19 logs/app.log | head -n 3
tr a-z A-Z < notes.txt
tr -d aeiou < notes.txt""", note='tail -n +2 drops the header line before counting names. In /etc/passwd field 1 is the user name and field 7 the login shell.')}
{run('Word frequency in one line', """tr ' ' '\\n' < poem.txt | tr A-Z a-z | sort | uniq -c | sort -rn | head -n 3""", note='Split into words, make them lower case, sort, count, sort by count, keep the top three.')}
{note('cut uses exactly one character as the separator. Columns separated by several spaces, as in ps or ls -l output, need squeezing with tr -s first, or awk, which is covered two chapters later.', 'warn')}
{talk('cut and tr are small tools that do one job each. cut picks columns. Tell it the separator with dash d and the field numbers with dash f, and it pulls out, for example, just the names from a spreadsheet file, or the user names from the system password file. tr translates characters one for one. tr with a to z and capital A to Z shouts everything in capitals. With dash d it deletes characters, and with dash s it squeezes repeated characters into one. Put them together with sort and uniq and you can count word frequencies in a whole book with one line. In 1986 the computer scientist Donald Knuth wrote a long, carefully crafted program for exactly that task, for a magazine column. Doug McIlroy reviewed it and showed that a six command Unix pipeline gave the same answer. Both approaches have their place, but the story shows how much power small tools have when combined.')}
''', kw=['cut', 'cut -d', 'cut -f', 'cut -c', 'tr', 'tr -d', 'tr -s', 'columns', 'word frequency', 'Knuth McIlroy'])

K.lesson('status', 'Did the pipeline work: exit status and pipefail', f'''
<p>Every command ends with an <b>exit status</b>, a number from 0 to 255. 0 means success, anything else means a problem. The shell keeps the last one in <code>$?</code>. A pipeline reports the status of its <b>last</b> command only, which can hide an early failure.</p>
{cmdtable([
    ('echo $?', 'Status of the last command or pipeline', 'ls nothere; echo $?'),
    ('echo ${PIPESTATUS[@]}', 'Bash: the status of every command in the last pipeline', 'false | true; echo ${PIPESTATUS[@]}'),
    ('set -o pipefail', 'The pipeline fails if any command in it fails', 'set -o pipefail'),
    ('A && B', 'Run B only if A succeeded', 'mkdir out && cd out'),
    ('A || B', 'Run B only if A failed', 'cd out || echo "no folder"')])}
{run('Hidden failures', """cat nothere | sort
echo "status: $?"
cat nothere | sort
echo "every part: ${PIPESTATUS[@]}"
set -o pipefail
cat nothere | sort
echo "with pipefail: $?"
mkdir -p out && echo "made out"
cd nothere || echo "could not enter"
yes | head -n 3""", note='Without pipefail the pipeline reports 0 because sort succeeded, even though cat failed with status 1. yes prints y for ever, but stops quietly once head has its three lines, because writing to a closed pipe ends it with the signal SIGPIPE.')}
{lab('Build data pipelines', [
    ('Show the fruits in sorted order.', 'sort fruits.txt', [{'cmd': r'sort'}, {'out': '^apple\\napple\\napple\\nbanana'}]),
    ('Count how many times each fruit appears (sort, then uniq -c).', 'sort fruits.txt | uniq -c', [{'cmd': r'sort.*\|\s*uniq\s+-c'}, {'out': '3 apple'}]),
    ('Show only the single most common fruit with its count.', 'sort fruits.txt | uniq -c | sort -rn | head -n 1', [{'cmd': r'uniq\s+-c.*\|\s*sort\s+-(rn|nr).*\|\s*head'}, {'out': '^\\s*3 apple\\s*$'}]),
    ('List each student name in <code>marks.csv</code> once, without the header.', 'cut -d, -f1 marks.csv | tail -n +2 | sort -u', [{'cmd': r'cut'}, {'out': '^Asha\\nJohn\\nMeera\\nRavi$'}]),
    ('Count the number of different subjects in <code>marks.csv</code>.', 'cut -d, -f2 marks.csv | tail -n +2 | sort -u | wc -l', [{'cmd': r'cut.*-f\s*2.*wc\s+-l'}, {'out': '^3$'}]),
    ('Show the poem in capital letters.', 'tr a-z A-Z < poem.txt', [{'cmd': r'tr\s+'}, {'out': 'TWINKLE TWINKLE'}]),
    ('Count how many files are in <code>/etc</code>.', 'ls /etc | wc -l', [{'cmd': r'ls\s+/etc\s*\|\s*wc\s+-l'}, {'out': '^\\d+$'}])])}
{talk('How do you know whether a command worked. Every command finishes with a number called its exit status. Zero means success, and any other number means something went wrong. The shell stores it in dollar question mark. Pipelines have a trap. Their status is the status of the last command only. If cat fails because a file is missing, but sort after it runs happily on empty input, the whole pipeline reports success. In a backup script that can mean a failure nobody notices for months. Bash offers two fixes. The PIPESTATUS array holds the status of every command in the last pipeline, and set dash o pipefail makes the pipeline fail when any part fails. Careful scripts turn pipefail on at the top, as you will see in the scripting section.')}
''', kw=['exit status', '$?', 'PIPESTATUS', 'pipefail', '&&', '||', 'SIGPIPE', 'yes | head'])

K.lesson('levels', 'Pipes from school to research', f'''
{ladder(
    '<p>The | symbol sends the output of one command into the next. sort orders lines, uniq -c counts repeats, cut picks columns, tr changes letters and wc -l counts lines. Joined together they answer questions in one line.</p>',
    '<p>A pipeline connects stdout of each command to stdin of the next and runs all of them at the same time. Filters read stdin and write stdout. The pipeline status is that of the last command unless pipefail is set, and PIPESTATUS holds every status.</p>',
    '<p>The shell calls pipe() to get a pair of descriptors, forks one child per command and uses dup2() to wire them. The kernel buffers data in the pipe, 65,536 bytes by default on Linux, and blocks a fast writer until the reader catches up, which gives natural flow control. When the reader exits, the next write sends SIGPIPE to the writer. Bash runs each part of a multi command pipeline in a subshell, so echo hi | read x sets x only in a child, unless shopt -s lastpipe is used.</p>',
    '<p>The pipe and filter style influenced software architecture (Shaw and Garlan), stream processing systems such as Apache Kafka and Apache Flink, and dataflow languages. Research on shell performance, such as the PaSh project (EuroSys 2021), automatically turns ordinary pipelines into parallel ones that use many CPU cores while giving the same output.</p>')}
{scene('the slow website', '<p>A site slows down and the engineer suspects a single visitor. One line answers it: <code>cut -d" " -f1 access.log | sort | uniq -c | sort -rn | head -n 5</code>. It prints the five IP addresses with the most requests. One address with 400,000 requests in an hour stands out, and a firewall rule blocks it.</p>')}
{talk('Inside the computer, a pipe is a small buffer in the kernel with two ends, one for writing and one for reading. The shell creates the pipe, starts both programs at the same time, and connects the writer to one end and the reader to the other. On Linux the buffer holds sixty four kilobytes. If the writer is faster, the kernel pauses it until the reader catches up, so memory never fills up. When the reader stops early, as head does, the writer receives a signal called SIGPIPE and ends quietly. The pipe and filter idea spread far beyond the shell. Large data systems such as Apache Kafka are built on the same thinking: small steps connected by streams. Researchers have even built tools, such as the PaSh project presented in 2021, that take an ordinary shell pipeline and run it in parallel on many processor cores automatically.')}
''', kw=['pipe()', 'pipe buffer', '65536', 'flow control', 'SIGPIPE', 'subshell', 'lastpipe', 'PaSh', 'stream processing'])

K.quiz('e', 'What does the | symbol do?', ['Ends a command', 'Sends the output of one command into the next', 'Runs a command as root', 'Saves output to a file'], 1, 'Pipe.', 'The pipe connects stdout of the left command to stdin of the right one.')
K.quiz('e', 'Which command counts the lines coming out of a pipe?', ['sort', 'wc -l', 'uniq', 'cut'], 1, 'Word count.', 'wc -l counts lines.')
K.quiz('e', 'Which option makes sort compare numbers?', ['-r', '-n', '-u', '-k'], 1, 'Numeric.', 'sort -n sorts by numeric value.')
K.quiz('e', 'What does tr a-z A-Z do?', ['Deletes letters', 'Turns small letters into capitals', 'Sorts letters', 'Counts letters'], 1, 'Translate.', 'tr translates each character of the first set into the second.')
K.quiz('m', 'uniq fruits.txt removes nothing, but the file has repeats. Why?', ['uniq is broken', 'uniq only removes repeats that are next to each other, sort first', 'The file is binary', 'You need -c'], 1, 'Adjacent lines.', 'Run sort before uniq.')
K.quiz('m', 'Which pipeline shows the 3 most common lines with their counts?', ['sort | uniq -c | sort -rn | head -n 3', 'uniq | sort | head', 'sort -u | head -n 3', 'wc -l | sort'], 0, 'Count, then rank.', 'Sort, count, sort by count descending, keep three.')
K.quiz('m', 'How do you get the user names (field 1) from /etc/passwd?', ['cut -f1 /etc/passwd', 'cut -d: -f1 /etc/passwd', 'tr : 1 /etc/passwd', 'sort -k1 /etc/passwd'], 1, 'Colon separated.', 'Fields in /etc/passwd are separated by colons.')
K.quiz('m', 'Plain sort puts 100 before 25. Why?', ['It is random', 'It compares characters from the left, and 1 comes before 2', 'It sorts by length', 'It is a bug'], 1, 'Text order.', 'Without -n, sort compares strings.')
K.quiz('m', 'cat nothere | sort, then echo $?. What is printed?', ['1', '0', '2', '127'], 1, 'Last command decides.', 'The status of a pipeline is that of sort, which succeeded.')
K.quiz('h', 'What does set -o pipefail change?', ['Pipes become faster', 'A pipeline fails if any command in it fails', 'Errors go into the pipe', 'Pipes are disabled'], 1, 'Any part.', 'With pipefail the status is the last non zero status in the pipeline.')
K.quiz('h', 'Why does yes | head -n 3 finish, even though yes never stops by itself?', ['yes has a limit', 'When head exits, the next write by yes gets SIGPIPE and ends it', 'The shell kills yes after 3 lines', 'head reads everything first'], 1, 'Writing to a closed pipe.', 'SIGPIPE ends a writer whose reader is gone.')
K.quiz('h', 'Which sends both stdout and stderr of cmd into grep?', ['cmd | grep x 2>&1', 'cmd 2>&1 | grep x', 'cmd > grep x', 'cmd 2| grep x'], 1, 'Redirect before the pipe.', '2>&1 must be on cmd, before the |.')
K.quiz('x', 'How big is a Linux pipe buffer by default?', ['512 bytes', '4 KB', '64 KB (65,536 bytes)', '1 MB'], 2, 'Sixteen pages.', 'pipe(7): since Linux 2.6.11 the capacity is 65,536 bytes.')

K.calc('e', 'fruits.txt has 8 lines with 5 different fruits. How many lines does sort fruits.txt | uniq print?', '5', 'One line per different fruit.', ['Repeats are removed after sorting.', 'Different fruits: 5.', eq('5 lines')], check=5)
K.calc('e', 'A pipeline has 4 commands joined by |. How many | symbols does it contain?', '3', 'One between each pair.', ['Commands: 4.', 'Gaps between them: 4 − 1.', eq('3 pipes')], check=3)
K.calc('m', 'A log has 1200 lines. 300 come from one IP address and the rest are spread evenly over 60 other addresses. How many requests does each of the other addresses make?', '15', 'Remaining lines over addresses.', ['Remaining: 1200 − 300 = 900.', 'Addresses: 60.', eq('900 ÷ 60 = 15')], check=15)
K.calc('m', 'sort -n on the numbers 10, 9, 100, 25. What is the second number in the output?', '10', 'Numeric order.', ['sort -n compares the values, not the characters.', 'Order: 9, 10, 25, 100.', eq('Second: 10')], check=10)
K.calc('m', 'A writer produces 1 MB per second and the reader takes 2 MB per second. With a 64 KB pipe, does the writer ever wait? Answer 1 for yes, 0 for no.', '0', 'Compare speeds.', ['The reader is faster than the writer.', 'The buffer never fills.', eq('0, the writer never waits')], check=0)
K.calc('h', 'false | true | false | true. With set -o pipefail, what is $? (false exits with 1)?', '1', 'The rightmost failure.', ['Statuses: 1 0 1 0.', 'pipefail returns the last non zero status.', eq('$? = 1')], check=1)

K.must('Pipe', 'A | B feeds stdout of A into stdin of B. Errors still go to the terminal unless you add 2>&1 before the |.')
K.must('sort and uniq', 'sort (-n numbers, -r reverse, -t, -k3 by field, -u unique, -h sizes). uniq needs sorted input, -c counts.')
K.must('Top N recipe', 'sort | uniq -c | sort -rn | head -n N finds the most common lines.')
K.must('cut and tr', 'cut -d, -f2 picks fields, cut -c1-8 characters. tr a-z A-Z translates, -d deletes, -s squeezes.')
K.must('Status', '$? is 0 for success. A pipeline reports its last command. PIPESTATUS shows all, set -o pipefail catches any failure.')

T = K.topic(
    slug='pipes-filters', topic='pipes-filters',
    step=(1, 'Streams and pipes', 'lx-power-1', 'Standard input, output and error, redirecting them to files, and joining commands with pipes into small data factories.', 'Intermediate'),
    title='Pipes and filters', short='Pipes and filters', badge='1.2', minutes=40, added='2026-11-23',
    lead='Join small commands with | to answer real questions in one line: sort, count, pick columns, change characters, and check that every step of a pipeline really worked.',
    desc='The pipe operator, the Unix philosophy, sort with -n -r -t -k -u -h, uniq and uniq -c, the top N recipe, cut with fields and characters, tr translate, delete and squeeze, exit status, PIPESTATUS, pipefail, && and ||, SIGPIPE, and how the kernel buffers a pipe.',
    summary='|, sort, uniq -c, cut, tr, wc, exit status, PIPESTATUS and pipefail.',
    keywords=['pipe', 'pipeline', 'sort', 'uniq', 'cut', 'tr', 'wc', 'pipefail', 'PIPESTATUS', 'exit status', 'filters'],
    recap='<p>A | B joins commands. sort, uniq -c, sort -rn, head finds the top lines. cut picks fields, tr changes characters. Check $? and use pipefail so failures are not hidden.</p>')
