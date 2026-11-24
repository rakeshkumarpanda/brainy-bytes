# Power tools 1.1: standard streams and redirection. stdin, stdout, stderr, file descriptors 0 1 2, > >> >| 2> 2>&1
# &> < here documents, here strings, /dev/null, tee, noclobber. Sources: bash(1) REDIRECTION section and the GNU Bash
# Reference Manual 3.6 Redirections, stdin(3), null(4), GNU coreutils manual (tee), POSIX Shell Command Language 2.7.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('streams', 'Three streams for every command', f'''
<p>Every program on Linux starts with three open channels, called <b>standard streams</b>. Each has a number, its <b>file descriptor</b>.</p>
{table(['Number', 'Name', 'Normally connected to', 'Used for'], [
    ['0', 'stdin (standard input)', 'the keyboard', 'Data the program reads'],
    ['1', 'stdout (standard output)', 'the terminal', 'Normal results'],
    ['2', 'stderr (standard error)', 'the terminal', 'Error messages and warnings']])}
<p>Results and errors both appear on your screen, so they look the same. But they travel on separate streams, and the shell can send each one somewhere else. This is called <b>redirection</b>, and the shell sets it up before the command starts. The command itself does not know where its output goes.</p>
{run('One command, two streams', """ls notes.txt nothere
ls notes.txt nothere > /dev/null
ls notes.txt nothere 2> /dev/null""", note='The first line shows both streams. In the second, stdout goes to /dev/null, a special file that swallows everything, so only the error is left. In the third, the error is thrown away and only the result is left.')}
{note('/dev/null is a real file in the tree, a character device. Writing to it always succeeds and the data disappears. Reading from it gives end of file at once.', 'tip')}
{talk('Every program on Linux is born with three open channels. Channel zero is standard input, where it reads data, normally from your keyboard. Channel one is standard output, for normal results, and channel two is standard error, for complaints and warnings. Both of those go to your terminal, which is why they look the same on screen. Keeping errors on a separate channel was a clever early Unix decision. It means you can save the useful results of a command in a file while the error messages still appear in front of you, or the other way round. The numbers zero, one and two are called file descriptors. You will see them again and again in shell commands, in programming and in system internals, so it is worth remembering them now.')}
''', kw=['stdin', 'stdout', 'stderr', 'file descriptor', '0 1 2', 'standard streams', '/dev/null'])

K.lesson('output', 'Sending output to files: > and >>', f'''
{cmdtable([
    ('cmd > FILE', 'stdout to FILE. FILE is created, or emptied first if it exists', 'ls > list.txt'),
    ('cmd >> FILE', 'stdout added to the end of FILE', 'date >> log.txt'),
    ('cmd 2> FILE', 'stderr to FILE', 'find / -name x 2> errors.txt'),
    ('cmd 2>> FILE', 'stderr added to the end of FILE', 'backup.sh 2>> errors.log'),
    ('cmd > FILE 2>&1', 'stdout to FILE, then stderr to the same place', 'backup.sh > all.log 2>&1'),
    ('cmd &> FILE', 'Bash shortcut for both streams to FILE', 'make &> build.log'),
    ('set -o noclobber', 'Make > refuse to overwrite an existing file (>| forces it)', 'set -o noclobber')])}
{run('Saving and adding', """ls > list.txt
cat list.txt
echo "first" > diary.txt
echo "second" >> diary.txt
cat diary.txt
echo "oops" > diary.txt
cat diary.txt""", note='list.txt appears in its own listing, because the shell creates the file before ls starts. The last &gt; replaced the whole diary with one line.')}
{play('lx-redirect')}
{run('The order of 2>&1 matters', """ls notes.txt nothere > out1.txt 2>&1
cat out1.txt
ls notes.txt nothere 2>&1 > out2.txt
cat out2.txt""", note='Redirections are read from left to right. 2&gt;&amp;1 means: make stream 2 go where stream 1 goes right now. In the first command, stream 1 already points at out1.txt, so both end up there. In the second, stream 1 still points at the terminal when 2&gt;&amp;1 is read, so the error stays on screen.')}
{run('A safety catch', """set -o noclobber
echo "new" > notes.txt
echo "forced" >| diary.txt
cat diary.txt""", note='With noclobber on, &gt; refuses to replace an existing file. &gt;| overrides the catch on purpose.')}
{note('A classic accident: sort data.txt &gt; data.txt leaves an empty file. The shell empties data.txt before sort starts reading it. Write to a new name and rename it afterwards.', 'warn')}
{talk('The arrow is one of the most useful symbols in the shell. A single arrow pointing right sends the output of a command into a file. Two arrows add the output to the end of a file instead, which is how log files grow line by line. Be careful with the single arrow. The shell empties the file before the command even starts, so a command that reads and writes the same file destroys it. To catch error messages, put the number two in front of the arrow. The trickiest pattern is two arrow ampersand one, which means send errors to the same place as normal output. Order matters here. The shell reads redirections from left to right, and two arrow ampersand one copies wherever output points at that moment. So write the file redirection first, and two arrow ampersand one after it. Engineers write this in cron jobs every day.')}
''', kw=['>', '>>', '2>', '2>&1', '&>', 'append', 'overwrite', 'noclobber', '>|', 'order of redirections', 'log file'])

K.lesson('input', 'Feeding input: <, here documents and here strings', f'''
{cmdtable([
    ('cmd < FILE', 'stdin reads from FILE instead of the keyboard', 'wc -l < fruits.txt'),
    ("cmd << 'END' ... END", 'Here document: the lines up to END become stdin', "cat << 'END'"),
    ('cmd << END ... END', 'Same, but $variables and $(commands) inside are expanded', 'cat << END'),
    ('cmd <<< "text"', 'Here string (bash): one piece of text plus a newline becomes stdin', 'tr a-z A-Z <<< "hi"')])}
{run('Reading from a file and from text', """wc -l fruits.txt
wc -l < fruits.txt
sort < fruits.txt > sorted.txt
head -n 3 sorted.txt
tr a-z A-Z <<< "shout this"
cat << END
Hello $USER, today is a good day.
Your home is $HOME.
END
cat << 'END'
Quoted: $USER stays as it is.
END""", note='wc prints the file name only when it opened the file itself. With &lt; the shell opens the file, and wc only sees a stream. With a quoted end word the here document is taken literally.')}
{note('A here document is the usual way for a script to write a whole configuration file in one go. Use &lt;&lt;- (with a dash) to let the closing word and the lines be indented with tab characters.', 'tip')}
{talk('Input can be redirected too. An arrow pointing left makes a command read from a file instead of the keyboard. Many commands can open files themselves, so the difference seems small, but it teaches an important idea: with the arrow, the shell opens the file and the command only sees a stream of data. A here document goes one step further. You write two left arrows and an end word, then several lines of text, then the end word again on its own line. Everything in between becomes the input. Scripts use this constantly to write configuration files or long messages. If you put the end word in quotes, the text is taken exactly as written. Without quotes, the shell fills in variables such as dollar USER. Bash also has a short form with three arrows, called a here string, for a single line of input.')}
''', kw=['<', 'input redirection', 'here document', 'heredoc', '<<', '<<-', 'here string', '<<<'])

K.lesson('tee', 'Seeing and saving at the same time: tee', f'''
<p><code>tee</code> reads stdin and writes it both to the screen and to one or more files, like a T shaped pipe fitting that splits water two ways. It is the tool to use when you want to watch output and keep a copy.</p>
{cmdtable([
    ('cmd | tee FILE', 'Show the output and save it to FILE', 'ls -l | tee listing.txt'),
    ('cmd | tee -a FILE', 'Show it and add it to the end of FILE', 'date | tee -a runs.log'),
    ('cmd | sudo tee FILE', 'Write a root owned file, because sudo echo x > file does not work', 'echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward')])}
{run('tee in action', """ls logs | tee folder.txt
cat folder.txt
date -u -d '2026-11-23 10:00' | tee -a runs.log
date -u -d '2026-11-23 11:00' | tee -a runs.log
wc -l runs.log""", note='The | symbol connects commands, the subject of the next chapter. tee prints what it receives and also writes it to the file.')}
{note('sudo echo hi &gt; /etc/motd fails with Permission denied, because the redirection is done by your own shell before sudo runs. echo hi | sudo tee /etc/motd works, because tee runs as root and opens the file itself.', 'warn')}
{lab('Steer the streams', [
    ('Save the listing of your home folder (<code>ls</code>) into <code>list.txt</code>.', 'ls > list.txt', [{'has': ['list.txt', 'notes.txt']}]),
    ('Add the line <code>done</code> to the end of <code>list.txt</code>.', 'echo done >> list.txt', [{'has': ['list.txt', 'done']}, {'has': ['list.txt', 'notes.txt']}]),
    ('Run <code>ls notes.txt nothere</code> and send only the error message into <code>err.txt</code>.', 'ls notes.txt nothere 2> err.txt', [{'has': ['err.txt', 'nothere']}, {'out': '^notes\\.txt$'}]),
    ('Run the same ls but throw the error away into /dev/null.', 'ls notes.txt nothere 2> /dev/null', [{'cmd': r'2>\s*/dev/null'}, {'out': '^notes\\.txt$'}]),
    ('Run it again and send both streams into <code>all.txt</code>, writing 2&gt;&amp;1 after the file.', 'ls notes.txt nothere > all.txt 2>&1', [{'cmd': r'>\s*all\.txt\s+2>&1'}, {'has': ['all.txt', 'nothere']}, {'has': ['all.txt', 'notes.txt']}]),
    ('Count the lines of <code>fruits.txt</code> by feeding the file to <code>wc -l</code> with &lt;.', 'wc -l < fruits.txt', [{'cmd': r'wc\s+-l\s*<\s*fruits\.txt'}, {'out': '^8$'}]),
    ('Show the words of <code>poem.txt</code> in capitals and keep a copy in <code>loud.txt</code> using tee.', "tr a-z A-Z < poem.txt | tee loud.txt", [{'has': ['loud.txt', 'TWINKLE']}, {'out': 'TWINKLE'}])])}
{talk('Sometimes you want to see output and save it at the same time. That is the job of tee, named after the T shaped fitting plumbers use to split a pipe in two directions. Whatever flows into tee comes out on the screen and also lands in a file. With dash a, it adds to the file instead of replacing it. tee also solves a puzzle that confuses many beginners. Typing sudo echo something into a protected file fails with permission denied, even though sudo is there. The reason is that the arrow is handled by your own shell, before sudo starts, and your shell is not root. Piping into sudo tee works, because then tee runs as root and opens the file itself. You will see this pattern in many official installation guides.')}
''', kw=['tee', 'tee -a', 'sudo tee', 'pipe', 'save and show', 'Permission denied sudo echo'])

K.lesson('levels', 'Redirection from school to research', f'''
{ladder(
    '<p>Commands read from stdin and write results to stdout and errors to stderr. &gt; saves output in a file, &gt;&gt; adds to it, 2&gt; catches errors, &lt; reads from a file and tee shows and saves at the same time.</p>',
    '<p>The shell performs redirections before executing the command, processing them left to right. n&gt;&amp;m duplicates descriptor m onto n. Here documents and here strings supply stdin from the script itself. /dev/null discards writes.</p>',
    '<p>Inside, the shell forks, then in the child calls open() for each file and dup2() to place it on descriptor 0, 1 or 2, and finally execve() the program, which inherits the descriptor table. That is why programs need no code for redirection. 2&gt;&amp;1 is literally dup2(1, 2). Bash creates here documents as temporary files or pipes. stdout to a terminal is line buffered by the C library, but block buffered to a file or pipe, which explains why output order can change when redirected.</p>',
    '<p>The idea that every resource looks like a file descriptor ("everything is a file") was pushed further by Plan 9 from Bell Labs, and today appears in Linux as /proc and /sys, eventfd, timerfd and signalfd. Research on capability systems such as Capsicum treats file descriptors as unforgeable access tokens, so a sandboxed program can use only the descriptors it was given.</p>')}
{scene('the nightly backup', '<p>A cron job runs <code>/usr/local/bin/backup.sh &gt;&gt; /var/log/backup.log 2&gt;&amp;1</code> at 02:00. Normal progress and errors both land in one growing log. With <code>2&gt;&amp;1 &gt;&gt; file</code> in the wrong order, errors would go to the cron daemon instead, which mails them to root, and nobody reads that mail box.</p>')}
{talk('Inside the computer, redirection is beautifully simple. When you run a command, the shell first makes a copy of itself. In that copy it opens the file you named and moves it into slot one, or slot two, of the file descriptor table, using a system call named dup two. Then it replaces itself with the program you asked for. The program inherits the table and simply writes to slot one, never knowing that slot one is now a file. That is why every program supports redirection for free. The same thinking, that everything should look like a file, was taken further by the Plan 9 system at Bell Labs, and Linux borrowed parts of it in slash proc and slash sys. Researchers working on sandboxes even treat file descriptors as keys: a program can only touch what it has been handed.')}
''', kw=['fork', 'dup2', 'execve', 'file descriptor table', 'buffering', 'Plan 9', 'everything is a file', 'Capsicum'])

K.quiz('e', 'Which file descriptor number is standard error?', ['0', '1', '2', '3'], 2, '0 in, 1 out, 2 errors.', 'stderr is descriptor 2.')
K.quiz('e', 'What does ls > list.txt do if list.txt already exists?', ['Adds to the end', 'Replaces its content', 'Refuses', 'Asks first'], 1, 'Single arrow.', '> empties the file and writes the new output.')
K.quiz('e', 'Which operator adds output to the end of a file?', ['>', '>>', '<', '|'], 1, 'Two arrows.', '>> appends.')
K.quiz('e', 'Where does data written to /dev/null go?', ['To the screen', 'Nowhere, it is thrown away', 'To a log file', 'To the trash folder'], 1, 'The bit bucket.', '/dev/null discards everything written to it.')
K.quiz('m', 'You want only the error messages of a command in errors.txt. Which form?', ['cmd > errors.txt', 'cmd 2> errors.txt', 'cmd < errors.txt', 'cmd | errors.txt'], 1, 'Number 2.', '2> redirects stderr only.')
K.quiz('m', 'Which sends both stdout and stderr to all.log?', ['cmd 2>&1 > all.log', 'cmd > all.log 2>&1', 'cmd 2> all.log', 'cmd >> 2 all.log'], 1, 'File first, then copy.', 'Left to right: stdout to the file, then stderr to where stdout points.')
K.quiz('m', 'Why does sort data.txt > data.txt leave data.txt empty?', ['sort has a bug', 'The shell empties data.txt before sort reads it', 'The disk is full', 'Because of noclobber'], 1, 'Redirection happens first.', 'The file is truncated when the shell sets up the redirection.')
K.quiz('m', 'In cat << \'END\' ... END, what happens to $USER in the text?', ['It becomes your user name', 'It stays as the literal text $USER', 'It causes an error', 'It is removed'], 1, 'Quoted end word.', 'Quoting the end word disables expansion inside the here document.')
K.quiz('m', 'echo hi | sudo tee /etc/motd works but sudo echo hi > /etc/motd fails. Why?', ['tee is faster', 'The redirection is done by your own shell, not by sudo', 'echo cannot run as root', '/etc/motd is special'], 1, 'Who opens the file.', 'Your unprivileged shell opens the file for >, while tee runs as root.')
K.quiz('h', 'ls notes.txt nothere 2>&1 > out.txt. Where does the error message go?', ['out.txt', 'The terminal', '/dev/null', 'Nowhere'], 1, 'Copy at that moment.', 'When 2>&1 is read, stdout still points at the terminal.')
K.quiz('h', 'wc -l < fruits.txt prints only 8, without the file name. Why?', ['wc is broken', 'The shell opened the file, so wc only sees a stream with no name', 'Because of -l', 'The file is empty'], 1, 'Who opened it.', 'With < the command reads stdin and never learns the file name.')
K.quiz('h', 'What does set -o noclobber change?', ['> refuses to overwrite existing files', '>> stops working', 'Errors are hidden', 'Pipes are disabled'], 0, 'No clobbering.', 'With noclobber, > fails on an existing file and >| forces it.')
K.quiz('x', 'Which system call does the shell use to make 2>&1 happen?', ['open', 'dup2(1, 2)', 'pipe', 'kill'], 1, 'Duplicate a descriptor.', 'dup2 copies descriptor 1 onto descriptor 2.')

K.calc('e', 'You run echo a > f, then echo b >> f, then echo c >> f. How many lines does f have?', '3', 'One write, then two appends.', ['> writes 1 line.', 'Each >> adds 1 line.', eq('1 + 2 = 3 lines')], check=3)
K.calc('e', 'You run echo a >> f, echo b >> f, then echo c > f. How many lines are left?', '1', 'The last > replaces everything.', ['After two appends: 2 lines.', '> empties the file and writes 1 line.', eq('1 line')], check=1)
K.calc('m', 'A cron job appends 6 lines to a log every hour. How many lines after one full day?', '144', 'Lines per hour times hours.', ['Lines per run: 6.', 'Runs per day: 24.', eq('6 × 24 = 144 lines')], check=144)
K.calc('m', 'A command prints 40 lines, 7 of them on stderr. You run it with 2> /dev/null. How many lines appear on screen?', '33', 'Only stdout is left.', ['Total: 40.', 'Errors thrown away: 7.', eq('40 − 7 = 33 lines')], check=33)
K.calc('m', 'A log line is about 120 bytes and 5000 lines are appended every day. About how many megabytes does the log grow per 30 day month (1 MB = 1,000,000 bytes)?', '18', 'Bytes per day, times days.', ['Per day: 120 × 5000 = 600,000 bytes.', 'Per month: 600,000 × 30 = 18,000,000 bytes.', eq('18 MB')], check=18)
K.calc('h', 'A program writes 3 lines to stdout and 2 to stderr. You run prog > a.txt 2>&1 | wc -l. What number does wc print?', '0', 'Nothing is left for the pipe.', ['Both streams go to a.txt.', 'The pipe receives nothing.', eq('wc -l prints 0')], check=0)

K.must('Streams', '0 stdin (keyboard), 1 stdout (results), 2 stderr (errors). Both outputs show on the terminal until redirected.')
K.must('Output', '> replaces, >> appends, 2> catches errors, &> or > f 2>&1 catches both. The file is emptied before the command runs.')
K.must('Order', 'Redirections run left to right. 2>&1 copies where stdout points at that moment, so write it after > file.')
K.must('Input', '< file feeds a file, << END is a here document (quote END to stop expansion), <<< is a here string.')
K.must('tee and /dev/null', 'tee shows and saves (tee -a appends, sudo tee writes root files). /dev/null throws output away.')

T = K.topic(
    slug='redirection', topic='redirection',
    step=(1, 'Streams and pipes', 'lx-power-1', 'Standard input, output and error, redirecting them to files, and joining commands with pipes into small data factories.', 'Intermediate'),
    title='Streams and redirection', short='Redirection', badge='1.1', minutes=40, added='2026-11-23',
    lead='Learn the three streams every program has, send output and errors to files, feed files and text into commands, and use tee to watch and save at the same time.',
    desc='stdin, stdout and stderr, file descriptors 0, 1 and 2, > and >>, 2> and 2>&1 and why their order matters, &>, noclobber, < input, here documents and here strings, /dev/null, tee and sudo tee, and how the shell uses dup2 inside.',
    summary='stdin, stdout, stderr, >, >>, 2>&1, <, here documents, /dev/null and tee.',
    keywords=['redirection', 'stdout', 'stderr', 'stdin', '2>&1', '>>', 'here document', '/dev/null', 'tee', 'file descriptor'],
    recap='<p>Three streams: 0 in, 1 out, 2 errors. &gt; replaces, &gt;&gt; appends, 2&gt;&amp;1 after the file joins errors, &lt; and here documents feed input, tee shows and saves.</p>')
