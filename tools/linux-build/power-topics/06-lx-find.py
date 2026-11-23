# Power tools 3.1: finding files. find with -name -iname -type -size -mtime -mmin -newer -perm -user -empty -maxdepth,
# operators ! -o ( ) and -prune, actions -print -print0 -exec ; and + -delete, xargs -n -I -0 -P -r, locate and
# updatedb, which, type, command -v. Sources: GNU findutils manual (find, xargs, locate), find(1), xargs(1),
# plocate(1) and updatedb(8), bash(1) type builtin, POSIX command -v.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('find', 'find: search the tree by name, type, size and age', f'''
<p><code>find WHERE TESTS</code> walks through a folder and everything below it, checks each entry against your tests and prints the ones that pass. Unlike ls, it looks inside every sub folder, and unlike grep it searches names and details, not content.</p>
{cmdtable([
    ("find . -name '*.txt'", 'Names matching a pattern (quote it!)', "find ~ -name '*.pdf'"),
    ("find . -iname 'readme*'", 'Same, ignoring case', "find . -iname '*.JPG'"),
    ('find . -type f', 'Only regular files (d folders, l symbolic links)', 'find /etc -type d'),
    ('find . -size +100M', 'Bigger than 100 MiB (- smaller, k M G units, c bytes)', 'find / -size +1G'),
    ('find . -mtime -7', 'Content changed less than 7 days ago (+7 more than 7)', 'find logs -mtime +30'),
    ('find . -mmin -10', 'Changed in the last 10 minutes', 'find /tmp -mmin -10'),
    ('find . -newer FILE', 'Changed more recently than FILE', 'find . -newer build.log'),
    ('find . -empty', 'Empty files and folders', 'find . -type d -empty'),
    ('find . -user NAME', 'Owned by a user (-group for a group)', 'find /home -user asha'),
    ('find . -perm -u+x', 'Mode includes these bits (-perm 644 exact)', 'find . -perm -o+w'),
    ('find . -maxdepth 1', 'Do not go deeper than one level', 'find . -maxdepth 2 -type d')])}
{play('lx-find')}
{run('Searching the home folder', """find . -name '*.txt' | sort
find . -type d | sort
find logs -type f | sort
find . -maxdepth 1 -type f -name '*.csv'
find . -empty
find . -iname 'NOTES*'
find /etc -maxdepth 1 -name 'host*' | sort""", note='find visits entries in the order the file system stores them, which is not alphabetical, so these lines pipe the result through sort. -empty finds the empty projects folder.')}
{note('Always quote the pattern: find . -name "*.txt". Without quotes the shell expands *.txt in the current folder first, and find then searches for those exact names only.', 'warn')}
{talk('find is the tool for questions like where did I save that file, which logs are older than a month, or what is eating my disk. You tell it where to start and what to look for, and it walks through every folder underneath, checking each entry. Tests can look at the name with dash name, at the kind of entry with dash type, at the size with dash size and at the age with dash m time. Units matter: dash size plus one hundred M means bigger than one hundred mebibytes, and dash m time plus thirty means changed more than thirty days ago. Always put the name pattern in quotes. Otherwise the shell expands the star before find even starts, and you get confusing results. find has been part of Unix since the nineteen seventies, and the GNU version on Linux adds many extra tests.')}
''', kw=['find', 'find -name', 'find -type', 'find -size', 'find -mtime', 'find -mmin', 'find -newer', 'find -empty', 'find -perm', 'find -user', 'maxdepth'])

K.lesson('combine', 'Combining tests: and, or, not, prune', f'''
<p>Tests written one after another must <b>all</b> be true (an implied -a, "and"). <code>-o</code> means "or", <code>!</code> means "not", and parentheses group tests. In the shell the parentheses must be escaped or quoted: <code>\\( ... \\)</code>.</p>
{table(['Expression', 'Meaning'], [
    ["<code>-type f -name '*.log'</code>", 'files AND named *.log'],
    ["<code>-name '*.jpg' -o -name '*.png'</code>", 'named *.jpg OR *.png'],
    ["<code>! -name '*.txt'</code> or <code>-not -name '*.txt'</code>", 'NOT named *.txt'],
    ["<code>-type f \\( -name '*.jpg' -o -name '*.png' \\)</code>", 'files that are jpg or png (the brackets group the or)'],
    ["<code>-path ./node_modules -prune -o -type f -print</code>", 'skip a whole folder, list the files everywhere else']])}
{run('Combined expressions', """find . -type f \\( -name '*.jpg' -o -name '*.png' \\) | sort
find . -type f ! -name '*.txt' | sort
find . -path ./logs -prune -o -type f -print | sort
find . -type f -size -1k -name '*.log' | sort""", note='-prune stops find from going into ./logs, and -print is then needed so that only the -o part prints. -size -1k means "rounded up to whole KiB, less than 1", which only empty files pass, so the last command prints nothing even though app.log is tiny.')}
{note('The and binds tighter than the or. find . -name "*.jpg" -o -name "*.png" -type f means jpg files of any type, or png files that are regular files. Use parentheses whenever you mix -o with other tests.', 'tip')}
{talk('Once you need more than one condition, find becomes a small logic language. Tests next to each other must all pass, so dash type f dash name star dot log means files and also named dot log. Dash o means or, and an exclamation mark means not. Because and is stronger than or, mixing them without brackets gives surprising results, so put round brackets around the or part. In the shell the brackets must be escaped with a backslash. One more useful word is dash prune, which tells find not to enter a folder. Developers use it all the time to skip huge folders such as node underscore modules or dot git, which can contain hundreds of thousands of files they never want to search.')}
''', kw=['find -o', 'find !', 'find -not', 'parentheses', 'find -prune', 'and or not', 'operator precedence'])

K.lesson('act', 'Doing something with the results: -exec, -delete and xargs', f'''
{cmdtable([
    ('find ... -exec CMD {} \\;', 'Run CMD once for each file, {} is the file name', "find . -name '*.sh' -exec chmod +x {} \\;"),
    ('find ... -exec CMD {} +', 'Run CMD once with many file names at the end (faster)', "find logs -name '*.log' -exec wc -l {} +"),
    ('find ... -delete', 'Delete every match (test without -delete first!)', "find /tmp -name '*.tmp' -mtime +7 -delete"),
    ('find ... -print0 | xargs -0 CMD', 'Pass names safely, even with spaces or newlines in them', "find . -name '*.log' -print0 | xargs -0 ls -l"),
    ('CMD | xargs CMD2', 'Turn input words into arguments of CMD2', 'echo a b c | xargs mkdir'),
    ('xargs -n 1', 'Use one argument per run', 'cat urls.txt | xargs -n 1 echo get'),
    ('xargs -I{} CMD {}', 'Put each input line where {} is', "ls *.jpg | xargs -I{} cp {} backup/{}"),
    ('xargs -P 4', 'Run up to 4 commands at the same time', "find . -name '*.png' | xargs -P 4 -n 1 optipng")])}
{run('Acting on matches', """find . -name '*.sh' -exec ls -l {} \\;
find logs -name '*.log' -exec wc -l {} + | sort -n
find . -name '*.txt' | sort | xargs wc -l
echo mon tue wed | xargs -n 1 echo day
ls logs | xargs -I{} echo "found {}"
mkdir -p tmp/a && touch tmp/a/x.tmp tmp/y.tmp
find tmp -name '*.tmp' | sort
find tmp -name '*.tmp' -delete
find tmp | sort""", note='With + find collects names and runs wc once, which also prints a total. -delete removed both .tmp files, and the folders stay.')}
{steps('A safe routine for -delete and -exec rm', [
    'Run the find command with no action and read the list.',
    'Add the action only when the list is exactly what you want to remove.',
    'Keep -delete at the end: placed first, find -delete -name x deletes everything it visits.',
    'For names that may contain spaces, use -print0 with xargs -0, or -exec ... + instead of a plain pipe.'])}
{lab('Find and act', [
    ('Find every file in your home folder whose name ends with <code>.log</code>.', "find . -name '*.log'", [{'cmd': r'find'}, {'out': './logs/app.log'}, {'out': './logs/old.log'}]),
    ('List only the folders under your home folder.', 'find . -type d', [{'cmd': r'-type\s+d'}, {'out': '^\\.\\n\\./logs'}]),
    ('Find empty files or folders.', 'find . -empty', [{'cmd': r'-empty'}, {'out': '^\\./projects$'}]),
    ('Find the pictures: files named *.jpg or *.png, using -o.', "find . -name '*.jpg' -o -name '*.png'", [{'cmd': r'-o'}, {'out': 'beach\\.jpg'}, {'out': 'cat\\.png'}]),
    ('Count the lines of every .log file in <code>logs</code> with one wc run (-exec ... +).', "find logs -name '*.log' -exec wc -l {} +", [{'cmd': r'-exec\s+wc\s+-l\s+\{\}\s*\+'}, {'out': '8 total'}]),
    ('Make <code>scripts/hello.sh</code> executable by running chmod through find -exec.', "find scripts -name '*.sh' -exec chmod u+x {} \\;", [{'mode': ['scripts/hello.sh', '744']}]),
    ('Pipe the names of the .txt files into xargs to count their lines.', "find . -name '*.txt' | xargs wc -l", [{'cmd': r'\|\s*xargs'}, {'out': 'total'}])])}
{talk('Finding files is often only the first step. With dash exec, find runs a command for each match, and the curly braces stand for the file name. End it with a backslash semicolon to run the command once per file, or with a plus sign to pass many files to one run, which is much faster when there are thousands. Dash delete removes every match, so always run the same find without it first and read the list. The xargs command does a similar job in a pipeline. It reads words from its input and adds them as arguments to another command. File names with spaces can confuse it, so the safe pair is find dash print zero with xargs dash zero, which separates names with an invisible null character that can never appear in a file name. xargs dash P even runs several commands in parallel to use all your processor cores.')}
''', kw=['find -exec', '{} \\;', '{} +', 'find -delete', 'xargs', 'xargs -n', 'xargs -I', 'xargs -0', 'print0', 'xargs -P', 'parallel'])

K.lesson('locate', 'Faster lookups: locate, which and type', f'''
<p>find reads the disk every time, which can take minutes on a big system. <code>locate</code> searches a database of file names instead, built by <code>updatedb</code>, usually once a day by a timer. It answers in a fraction of a second, but it does not know about files created since the last update. On current Debian and Ubuntu it is provided by the plocate package.</p>
{cmdtable([
    ('locate NAME', 'Every path containing NAME, from the database', 'locate sshd_config'),
    ('locate -i NAME', 'Ignore case', 'locate -i readme'),
    ('sudo updatedb', 'Rebuild the database now', 'sudo updatedb'),
    ('which CMD', 'Which program file runs for CMD, using PATH', 'which python3'),
    ('type CMD', 'Bash: is CMD an alias, a function, a builtin or a file', 'type cd ls'),
    ('command -v CMD', 'Portable test that CMD exists, good in scripts', 'command -v git || echo "no git"')])}
{sample('locate in action', 'locate sshd_config', """/etc/ssh/sshd_config
/etc/ssh/sshd_config.d
/usr/share/doc/openssh-server/examples/sshd_config""", note='Paths depend on what is installed. If locate is missing, install it with sudo apt install plocate.')}
{run('Which program runs', """which ls bash
type cd
type ls
command -v grep
command -v notarealcommand || echo "not installed\"""", note='cd is built into bash, so there is no file for it. type ls may show an alias on systems that set one in ~/.bashrc, this build shell has none.')}
{talk('Searching the whole disk with find can take a long time on a big server. locate takes a different approach. Once a day, a program called updatedb walks the file system and stores every path in a compact database. locate then searches only that database, so it answers almost instantly. The price is freshness: a file created five minutes ago is not in the database until the next update, unless you run sudo updatedb yourself. Two other small commands answer a related question: which program will run when I type this name. which follows the PATH variable and prints the file. type is built into bash and also knows about aliases, functions and built in commands such as cd. In scripts, command dash v is the portable way to check whether a tool is installed before using it.')}
''', kw=['locate', 'plocate', 'updatedb', 'which', 'type', 'command -v', 'PATH lookup', 'builtin'])

K.lesson('levels', 'Finding files from school to research', f'''
{ladder(
    '<p>find searches folders for files by name, type, size or age, and can run a command on each one. locate is faster because it searches a list made earlier. which shows where a command lives.</p>',
    '<p>find evaluates a boolean expression of tests, operators and actions for each directory entry in a depth first walk. -exec {{}} + batches arguments like xargs, -print0 and xargs -0 use NUL separators. locate trades freshness for speed with a periodically built index.</p>',
    '<p>GNU find walks the tree with the fts library, reading directory entries with getdents64() and calling stat (or using the d_type field to skip stat) only when a test needs metadata, which makes -name searches fast. xargs keeps each command line below the limit given by sysconf(_SC_ARG_MAX), minus the size of the environment, which is why it splits huge lists into several runs. plocate uses a posting list index with compression and io_uring to answer queries in milliseconds.</p>',
    '<p>File search at scale moves to indexes: desktop search engines (Spotlight, Tracker, Windows Search) watch the file system with inotify or similar events and update a full text index. Research on file system metadata search (for example Spyglass, FAST 2009, and GUFI from Los Alamos) builds indexes that answer find style questions over billions of files on supercomputer storage in seconds.</p>')}
{scene('the full disk at night', '<p>A database server runs out of space. The engineer runs <code>sudo find / -xdev -type f -size +1G -exec ls -lh {{}} + 2&gt;/dev/null</code> and spots a 40 GB core dump in /var/crash from a crashed program. After checking it is not needed, <code>sudo find /var/crash -name "*.crash" -mtime +7 -delete</code> frees the space, and a ticket is opened to fix the crash.</p>')}
{talk('Under the hood, find walks the directory tree depth first, reading the list of names in each folder. A clever detail is that it avoids asking for full file details unless a test needs them, because the folder listing already tells it whether an entry is a file or a folder. That is why searching by name is fast. xargs hides another detail: the kernel limits how long a command line can be, so when you pipe a million names into xargs, it quietly splits them into several runs that each fit the limit. At larger scale, searching the disk every time becomes too slow, so desktop search tools keep an index that is updated whenever a file changes. Supercomputer centres face file systems with billions of files, and research projects such as GUFI at Los Alamos National Laboratory build special indexes so that administrators can answer find style questions in seconds instead of days.')}
''', kw=['fts', 'getdents', 'd_type', 'ARG_MAX', 'plocate', 'io_uring', 'inotify', 'metadata index', 'GUFI'])

K.quiz('e', 'Which command finds all files named report.pdf under your home folder?', ['grep report.pdf ~', "find ~ -name 'report.pdf'", 'ls -R report.pdf', 'locate -r ~'], 1, 'Search names.', 'find searches the tree by name.')
K.quiz('e', 'Which test limits find to regular files?', ['-type d', '-type f', '-file', '-regular'], 1, 'f for file.', '-type f selects regular files.')
K.quiz('e', 'Why put the pattern in quotes: find . -name "*.txt"?', ['Quotes make find faster', 'So the shell does not expand *.txt before find runs', 'Quotes are required for every option', 'To ignore case'], 1, 'Who expands the star.', 'Unquoted, the shell would replace *.txt with names in the current folder.')
K.quiz('e', 'What does find . -mtime +30 select?', ['Files changed in the last 30 days', 'Files changed more than 30 days ago', 'Files bigger than 30 MB', 'Files with 30 lines'], 1, 'Plus means more.', '+30 means more than 30 days.')
K.quiz('m', 'Which runs wc -l once with all matching files?', ["find . -name '*.log' -exec wc -l {} (the per-file ending)", "find . -name '*.log' -exec wc -l {} +", "find . -name '*.log' | wc -l", "find . -wc"], 1, 'Plus batches.', '-exec ... + collects many names into one run.')
K.quiz('m', 'Which finds jpg or png files only, not folders?', ["find . -type f -name '*.jpg' -o -name '*.png'", "find . -type f '(' -name '*.jpg' -o -name '*.png' ')'", "find . -name '*.jpg,*.png'", "find . -type jpg,png"], 1, 'Group the or.', 'Without brackets, -type f only applies to the jpg part.')
K.quiz('m', 'What does find . -path ./node_modules -prune -o -type f -print do?', ['Deletes node_modules', 'Lists files everywhere except inside ./node_modules', 'Lists only node_modules', 'Fails'], 1, 'Prune skips.', '-prune stops find from descending into that folder.')
K.quiz('m', 'Why use find -print0 | xargs -0 instead of find | xargs?', ['It is shorter', 'File names with spaces or newlines are passed safely', 'It runs as root', 'It sorts the names'], 1, 'NUL separators.', 'A NUL byte cannot appear in a file name, so it is a safe separator.')
K.quiz('m', 'locate does not find a file you created a minute ago. Why?', ['locate is broken', 'Its database was built before the file existed, run sudo updatedb', 'The file is hidden', 'locate only searches /etc'], 1, 'Indexed search.', 'locate reads a database that is refreshed periodically.')
K.quiz('h', 'Which command tells you whether ls is an alias, a builtin or a program?', ['which ls', 'type ls', 'whereis ls', 'file ls'], 1, 'Bash knows its aliases.', 'type reports aliases, functions, builtins and files.')
K.quiz('h', 'find / -name "*.conf" prints many "Permission denied" lines. How do you hide them?', ['find / -name "*.conf" 2> /dev/null', 'find / -name "*.conf" > /dev/null', 'find -q /', 'sudo find -silent'], 0, 'Errors are stream 2.', 'Redirect stderr to /dev/null.')
K.quiz('h', 'What does find . -size -1k match?', ['Files under 1024 bytes', 'Only empty files, because sizes are rounded up to whole KiB', 'Files over 1 KiB', 'Nothing ever'], 1, 'Rounding up.', 'A 300 byte file counts as 1k, which is not less than 1.')
K.quiz('x', 'Why does xargs sometimes run the command several times for one input list?', ['A bug', 'To keep each command line below the kernel limit ARG_MAX', 'To use more CPUs by default', 'Because of -0'], 1, 'Argument length limit.', 'xargs splits arguments so execve does not fail with "Argument list too long".')

K.calc('e', 'find . -mtime -7 runs on Friday. Files changed on which earlier day still match: 5 days ago (1) or 9 days ago (0)?', '1', 'Less than 7 days.', ['-7 means less than 7 days ago.', '5 days is less than 7.', eq('1 (yes)')], check=1)
K.calc('e', 'find runs -exec rm {} with the per-file ending (backslash semicolon) on 250 files. How many times does rm start?', '250', 'The per-file ending runs once per file', ['The per-file ending runs the command for each match.', 'Matches: 250.', eq('250 runs')], check=250)
K.calc('m', 'xargs -n 50 receives 1230 file names. How many times does it run the command?', '25', 'Divide and round up.', ['1230 ÷ 50 = 24.6.', 'A partial group still needs a run.', eq('25 runs')], check=25)
K.calc('m', 'A file is 2,500,000 bytes. With -size in M units (1 MiB = 1,048,576 bytes, rounded up), what size does find use?', '3', 'Round up.', ['2,500,000 ÷ 1,048,576 ≈ 2.38.', 'find rounds up to whole units.', eq('3 (so -size -3M does not match it)')], check=3)
K.calc('m', 'A tree has 12 folders with 40 files each. find . -type f prints how many lines?', '480', 'Files per folder times folders.', ['Folders: 12.', 'Files each: 40.', eq('12 × 40 = 480')], check=480)
K.calc('h', 'xargs -P 4 runs jobs that take 3 seconds each. About how many seconds for 20 jobs?', '15', 'Four at a time.', ['20 jobs ÷ 4 at once = 5 rounds.', 'Each round takes 3 seconds.', eq('5 × 3 = 15 seconds')], check=15)

K.must('find', 'find WHERE TESTS. -name (quote it), -iname, -type f/d/l, -size +100M, -mtime -7, -mmin, -empty, -user, -perm, -maxdepth.')
K.must('Logic', 'Tests side by side mean and. -o is or, ! is not, quoted brackets group, and binds tighter than or. -prune skips a folder.')
K.must('Actions', '-exec cmd {} with the backslash semicolon ending runs per file, -exec cmd {} + in batches, -delete (preview first, keep it last).')
K.must('xargs', 'Turns input into arguments. -n count, -I{} placement, -0 with find -print0 for safe names, -P parallel.')
K.must('Lookups', 'locate uses a daily database (sudo updatedb to refresh). which, type and command -v tell what a command name runs.')

T = K.topic(
    slug='find-files', topic='find-files',
    step=(3, 'Finding and packing files', 'lx-power-3', 'Search the file tree with find and xargs, and bundle and compress files with tar, gzip, xz and zip.', 'Intermediate'),
    title='Finding files: find, xargs and locate', short='find and xargs', badge='3.1', minutes=45, added='2026-11-23',
    lead='Search the whole file tree by name, type, size, age and owner, combine tests with and, or and not, act on the results safely with -exec and xargs, and use locate, which and type for quick lookups.',
    desc='find tests (-name -iname -type -size -mtime -mmin -newer -empty -user -perm -maxdepth), operators and grouping, -prune, actions (-exec per file and with +, -delete, -print0), xargs with -n -I -0 -P, locate and updatedb, which, type and command -v, and how find and xargs work inside.',
    summary='find by name, type, size and age, -o and -prune, -exec and -delete, xargs, locate and which.',
    keywords=['find', 'xargs', 'locate', 'find -exec', 'find -name', 'find -size', 'find -mtime', 'print0', 'which', 'type', 'search files'],
    recap='<p>find walks a tree and tests every entry. Combine tests with ! -o and brackets, skip folders with -prune, act with -exec or -delete, pass names to xargs safely with -print0 and -0.</p>')
