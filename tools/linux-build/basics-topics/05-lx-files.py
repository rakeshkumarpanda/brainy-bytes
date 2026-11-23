# Foundations 2.2: making, copying, moving, renaming and deleting files and folders, globbing and brace expansion,
# safe habits. Sources: GNU coreutils manual (mkdir, touch, cp, mv, rm, rmdir), bash(1) Pathname Expansion and
# Brace Expansion, glob(7), POSIX file name rules (any byte except / and NUL).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('make', 'Making folders and files: mkdir and touch', f'''
{cmdtable([
    ('mkdir NAME', 'Make a folder', 'mkdir projects/site'),
    ('mkdir -p A/B/C', 'Make the whole chain, and do not complain if it exists', 'mkdir -p work/2026/nov'),
    ('mkdir -v NAME', 'Say what was made', 'mkdir -v music'),
    ('touch FILE', 'Make an empty file, or update the time of one that exists', 'touch todo.txt'),
    ('echo text &gt; FILE', 'Make a file with one line in it (the &gt; arrow is explained in Shell Power Tools)', 'echo hi &gt; hello.txt')])}
{run('Make a small project', '''mkdir site
mkdir site/css site/js
mkdir -p site/images/2026/nov
touch site/index.html site/css/style.css
ls -R site''')}
<p>Linux file names may contain any character except <code>/</code> and the invisible null byte, and they are case sensitive. Good habits: use lower case, letters, digits, dots, dashes and underscores. Avoid spaces and characters like <code>*</code>, <code>?</code>, <code>$</code>, <code>&amp;</code> and the semicolon, which the shell treats specially. A file extension such as .txt is only part of the name. Linux does not need it, programs look at the content.</p>
{note('mkdir a/b fails with "No such file or directory" when a does not exist yet. Add -p to create every missing parent.', 'warn')}
{talk('mkdir is short for make directory and touch is a funny name with a real meaning. Its first job was to touch a file, updating its time stamp without changing the content. Programmers used it with a build tool called make, which decides what to rebuild by comparing file times. Making an empty file was a side effect that turned out to be handy. Here is a rule many people learn the hard way. Linux treats Report.txt and report.txt as two different files, while Windows and macOS usually treat them as the same. In 2014 Git had a serious security bug on Windows and macOS caused by exactly this difference in how case is handled. Pick a simple naming style early: lower case letters, digits and dashes, no spaces. Your future self, and every script you write, will thank you.')}
''', kw=['mkdir', 'mkdir -p', 'touch', 'file names', 'case sensitive', 'extensions'])

K.lesson('copymove', 'Copying, moving and renaming: cp and mv', f'''
{fxs(fx('Copy', '<code>cp SOURCE DEST</code>', 'Copies a file. If DEST is a folder, the copy goes inside it with the same name. Several sources need a folder as DEST.', key=True),
     fx('Copy a folder', '<code>cp -r FOLDER DEST</code>', '-r (recursive) copies the folder and everything inside. -a also keeps times, owners and links, best for backups.', key=True),
     fx('Move or rename', '<code>mv OLD NEW</code>', 'Inside one disk, mv only changes the name, so even a huge folder moves instantly. mv to another disk copies, then deletes.', key=True))}
{cmdtable([
    ('cp -i', 'Ask before overwriting an existing file', 'cp -i a.txt b.txt'),
    ('cp -v', 'Print each copy', 'cp -v *.txt backup/'),
    ('cp -p', 'Keep mode, owner and times', 'cp -p notes.txt old/'),
    ('mv -i', 'Ask before overwriting', 'mv -i draft.txt final.txt'),
    ('mv -n', 'Never overwrite', 'mv -n new.txt old.txt')])}
{run('Copy, rename and move', '''mkdir backup
cp notes.txt backup/
cp notes.txt notes-copy.txt
mv notes-copy.txt todo.txt
cp -r logs backup/
mv todo.txt backup/
ls backup backup/logs''')}
{note('cp and mv overwrite an existing destination file without asking. Use -i while you learn, or -n when you never want to overwrite.', 'warn')}
{note('There is no rename command needed: renaming is moving a file to a new name in the same folder.', 'tip')}
{talk('Copying a huge folder can take minutes, but moving it to another place on the same disk takes a fraction of a second. Why? Because a move does not touch the data at all. A folder is really just a list of names, each pointing to the place where the file lives. mv only takes the name out of one list and writes it into another. The bytes stay exactly where they were. Only when you move to a different disk does mv have to copy every byte and then delete the original. Another thing that surprises beginners is that cp and mv will silently replace a file that already has the destination name. There is no undo. That is why many Linux distributions set up cp and mv with the dash i option for the root user, so they ask first, and why careful people check with ls before pressing Enter.')}
''', kw=['cp', 'cp -r', 'cp -a', 'mv', 'rename', 'overwrite', 'cp -i', 'mv -n'])

K.lesson('remove', 'Deleting safely: rm and rmdir', f'''
<p><b>rm deletes for good.</b> There is no recycle bin on the command line, and no undo. Read every rm command twice before pressing Enter.</p>
{cmdtable([
    ('rm FILE', 'Delete files', 'rm old.txt'),
    ('rm -i FILE', 'Ask about each file first', 'rm -i *.log'),
    ('rm -r FOLDER', 'Delete a folder and everything inside it', 'rm -r build'),
    ('rm -f FILE', 'Force: never ask, no error if missing. Dangerous with -r', 'rm -f tmp.txt'),
    ('rmdir FOLDER', 'Delete a folder only if it is empty, a safe choice', 'rmdir empty-folder'),
    ('rm -- -name', 'Delete a file whose name starts with a dash', 'rm -- -weird.txt')])}
{run('Delete, and see the safety nets', '''mkdir -p trash/inner
touch trash/a.txt
rmdir trash
rm trash
rm -r trash
ls trash''', note='rmdir refuses because the folder is not empty, rm refuses a folder without -r, and after rm -r it is gone.')}
{steps('A safe deleting routine', [
    'Run <code>ls</code> with exactly the same pattern first, for example <code>ls *.log</code>, and read the list.',
    'Press Up, change ls to rm, and check that nothing else changed.',
    'Prefer a specific path to a wildcard, and never type a lonely * or / with -r.',
    'Use <code>rm -i</code> or move things to a trash folder while you learn.',
    'Keep backups. They are the only real undo.'])}
{note('GNU rm refuses rm -r / and needs --no-preserve-root to do it (protection added in coreutils 6.4, 2006). But it will happily delete everything with rm -rf ~/* or with a typo such as a space in rm -rf ./ folder. There is no protection for those.', 'warn')}
{talk('Here is a true kind of story that happens every year. In 2017 an engineer at the code hosting company GitLab was fixing a database problem late at night, tired, logged into two servers. He meant to delete a folder on the broken server, but ran the command on the healthy one. About three hundred gigabytes of live data disappeared in seconds. GitLab recovered most of it from a copy that happened to be six hours old, and they wrote openly about it so others could learn. The lesson is simple. rm does not ask, does not use a recycle bin, and does not forgive. Check the prompt to see which machine you are on, list the files before deleting them, and keep backups that you have actually tested. Professionals are not people who never make mistakes. They are people who build habits that make mistakes rare and recoverable.')}
''', kw=['rm', 'rm -r', 'rm -f', 'rm -i', 'rmdir', 'no recycle bin', 'preserve-root', 'safe delete'])

K.lesson('glob', 'Wildcards and braces: many files at once', f'''
<p>Instead of typing every name, you can give the shell a <b>pattern</b>. The shell turns the pattern into the list of matching names before the command starts. This is called <b>globbing</b>.</p>
{fxs(fx('*', 'any text, even none', '*.txt matches notes.txt and a.txt. * alone matches every name that does not start with a dot.', key=True),
     fx('?', 'exactly one character', 'photo?.jpg matches photo1.jpg but not photo10.jpg.'),
     fx('[abc] [a-z] [!a]', 'one character from a set', '[nf]* matches names starting with n or f. [!0-9]* names not starting with a digit.'),
     fx('{a,b} {1..5}', 'brace expansion, not a match', 'Makes words even if no file exists: mkdir day{1..3} makes day1 day2 day3.', key=True))}
{play('lx-glob')}
{run('Patterns, run for real', '''touch photo1.jpg photo2.jpg photo10.jpg
echo *.txt
echo photo?.jpg
echo photo*.jpg
echo [mn]*
mkdir -p week/{mon,tue,wed}
echo report-{2025..2026}.pdf
ls week''')}
{note('If nothing matches, bash passes the pattern itself unchanged. rm *.bak in a folder with no .bak files gives "rm: cannot remove ’*.bak’: No such file or directory".', 'tip')}
{lab('Organise a messy folder', [
    ('Make a folder called <code>archive</code>.', 'mkdir archive', [{'exists': 'archive', 'type': 'd'}]),
    ('Make nested folders <code>work/2026/nov</code> in one command.', 'mkdir -p work/2026/nov', [{'exists': 'work/2026/nov', 'type': 'd'}]),
    ('Create an empty file <code>todo.txt</code>.', 'touch todo.txt', [{'exists': 'todo.txt', 'type': 'f'}]),
    ('Copy every .txt file into archive with one wildcard.', 'cp *.txt archive/', [{'exists': 'archive/notes.txt'}, {'exists': 'archive/fruits.txt'}, {'exists': 'archive/poem.txt'}]),
    ('Rename <code>todo.txt</code> to <code>tasks.txt</code>.', 'mv todo.txt tasks.txt', [{'exists': 'tasks.txt'}, {'gone': 'todo.txt'}]),
    ('Copy the whole logs folder into archive.', 'cp -r logs archive/', [{'exists': 'archive/logs/app.log'}]),
    ('Make three folders day1 day2 day3 with brace expansion.', 'mkdir day{1..3}', [{'exists': 'day1', 'type': 'd'}, {'exists': 'day3', 'type': 'd'}]),
    ('Remove the empty folder day2 with the safe command.', 'rmdir day2', [{'cmd': r'^\s*rmdir'}, {'gone': 'day2'}]),
    ('Delete the archive folder and everything in it.', 'rm -r archive', [{'gone': 'archive'}])])}
{talk('Wildcards save enormous amounts of typing. A photographer with three thousand pictures can copy every JPEG file with one short pattern. The important detail is who does the matching. It is the shell, not the command. Before cp even starts, the shell looks in the folder, finds every name that fits the pattern, and hands that list to cp. That is why patterns work the same way with every command. The idea goes back to the first Unix, where a separate tiny program called glob did the expanding, short for global, and the name stuck. Braces are different. They do not look at files at all. They simply make words, so mkdir with day one to three in braces creates three folders that did not exist before. One warning: a star does not match hidden names that start with a dot, which is usually what you want.')}
''', kw=['wildcards', 'globbing', '*', '?', '[abc]', 'brace expansion', '{1..5}', 'pattern', 'nullglob'])

K.lesson('levels', 'File operations from school to research', f'''
{ladder(
    '<p>mkdir makes a folder, touch makes an empty file, cp copies, mv moves or renames, and rm deletes for ever. A star in a name means "anything here", so *.jpg means every picture ending in .jpg.</p>',
    '<p>File management commands operate on paths. Globbing (*, ?, [...]) is performed by the shell, brace expansion generates words before globbing, and the command receives the resulting argument list. cp -a preserves metadata, mv within a filesystem is a rename, and rm unlinks names.</p>',
    '<p>rm calls unlink() or unlinkat(), which removes a directory entry. The data blocks are freed only when the inode link count reaches zero and no process holds the file open, which is why deleting a log that a program still writes does not free disk space. mv on one filesystem calls rename(), which is atomic: other processes see the old name or the new one, never a half state. Across filesystems mv falls back to copy plus unlink.</p>',
    '<p>Topics include atomic file replacement patterns (write a temp file, fsync, rename) used by databases and editors, crash consistency studies that showed many applications lose data on power failure (Pillai and others, OSDI 2014), copy on write filesystems (Btrfs, ZFS) with instant reflink copies via cp --reflink, and secure deletion, which is hard on SSDs because of wear levelling.</p>')}
{scene('a disk that stays full', '<p>An engineer deletes a 20 GB log file to free space, but df still shows the disk full. The web server still has the file open, so the kernel keeps the data until the server closes it. Restarting the service, or emptying the file with <code>: &gt; file</code> instead of deleting it, frees the space. You will meet this again in the inodes chapter.</p>')}
{talk('Inside the computer, deleting a file is not what most people imagine. rm does not wipe the data. It removes the name from the folder list, and the space is only marked as free when no name points to it and no program has the file open. This explains a famous puzzle on servers. An engineer deletes a huge log file, but the disk stays full, because the web server is still writing to it. Researchers have also studied what happens to files when the power fails. A well known study presented at the OSDI conference in 2014 found that many popular programs could lose or corrupt data in a crash, because they replaced files in an unsafe order. The safe pattern is to write a new file, flush it to disk, and then rename it over the old one, because rename on one disk is atomic. Databases and good editors all use this trick.')}
''', kw=['unlink', 'rename atomic', 'open file deleted', 'reflink', 'crash consistency', 'secure delete'])

K.quiz('e', 'Which command makes a new folder?', ['touch', 'mkdir', 'mkfile', 'cd'], 1, 'Make directory.', 'mkdir makes directories.')
K.quiz('e', 'How do you rename notes.txt to list.txt?', ['rename notes.txt list.txt', 'mv notes.txt list.txt', 'cp -r notes.txt list.txt', 'rn notes.txt list.txt'], 1, 'Renaming is moving.', 'mv OLD NEW renames a file in the same folder.')
K.quiz('e', 'What happens to a file deleted with rm?', ['It goes to the trash', 'It is gone, there is no undo', 'It is hidden', 'It moves to /tmp'], 1, 'No recycle bin.', 'rm removes the file for good.')
K.quiz('e', 'Which pattern matches every file ending in .log?', ['?.log', '*.log', '[log]', 'log*'], 1, 'Star means any text.', '*.log matches any name that ends with .log.')
K.quiz('m', 'mkdir a/b/c fails because a does not exist. What fixes it?', ['mkdir -r a/b/c', 'mkdir -p a/b/c', 'mkdir -f a/b/c', 'touch a/b/c'], 1, 'Parents.', '-p creates all missing parent folders.')
K.quiz('m', 'cp photos backup refuses and says -r was not specified, so it is omitting the directory. Why?', ['photos is a folder, so cp needs -r', 'backup is full', 'photos is empty', 'You need sudo'], 0, 'Folders need recursion.', 'Copying a folder needs cp -r (or -a).')
K.quiz('m', 'Which matches photo1.jpg but not photo10.jpg?', ['photo*.jpg', 'photo?.jpg', 'photo[10].jpg', 'photo.jpg'], 1, 'One character exactly.', '? stands for exactly one character.')
K.quiz('m', 'rmdir old says "Directory not empty". What is the safe next step?', ['rm -rf / ', 'Look inside with ls old, then decide', 'Reboot', 'chmod 777 old'], 1, 'Look before you delete.', 'Check the contents before using rm -r.')
K.quiz('m', 'What does mkdir {jan,feb,mar} create?', ['One folder named {jan,feb,mar}', 'Three folders jan, feb and mar', 'Nothing', 'Files'], 1, 'Brace expansion makes words.', 'The shell expands it to mkdir jan feb mar.')
K.quiz('h', 'Who expands *.txt into file names?', ['The cp command', 'The shell, before the command starts', 'The kernel', 'The terminal'], 1, 'Same for every command.', 'Globbing is done by the shell, the command only sees the list.')
K.quiz('h', 'Why does moving a 50 GB folder within one disk finish instantly?', ['It is compressed', 'mv only changes directory entries (a rename), no data is copied', 'It runs in the background', 'It deletes the data'], 1, 'Names, not bytes.', 'On the same filesystem mv uses rename().')
K.quiz('h', 'How do you delete a file named -f?', ['rm -f', 'rm -- -f or rm ./-f', 'rm "-f"', 'You cannot'], 1, 'Stop option parsing.', '-- ends options, and ./-f is a path that does not start with a dash.')
K.quiz('x', 'You delete a big log file but df shows no free space gained. Most likely cause?', ['df is slow', 'A running process still has the file open, so its blocks are not freed', 'The file was a link', 'rm failed silently'], 1, 'Open files keep data alive.', 'Space is freed when the last name is gone and no process holds it open.')

K.calc('e', 'mkdir day{1..7} makes how many folders?', '7', 'Count from 1 to 7.', ['Brace range 1..7.', 'Words: day1 to day7.', eq('7 folders')], check=7)
K.calc('e', 'A folder has photo1.jpg to photo12.jpg. How many does photo?.jpg match?', '9', 'One character after photo.', ['photo?.jpg needs exactly one character.', 'photo1 to photo9 have one digit.', eq('9 matches (photo10 to photo12 have two digits)')], check=9)
K.calc('m', 'mkdir -p y{2025,2026}/m{01..12} makes how many month folders?', '24', 'Two years times twelve months.', ['Years: 2.', 'Months per year: 12.', eq('2 × 12 = 24 month folders (plus the 2 year folders)')], check=24)
K.calc('m', 'touch {a,b,c}{1,2,3}.txt creates how many files?', '9', 'Braces multiply.', ['First braces: 3 choices.', 'Second braces: 3 choices.', eq('3 × 3 = 9 files, a1.txt to c3.txt')], check=9)
K.calc('m', 'You copy a 700 MB folder to another disk that reads and writes at 140 MB/s. About how many seconds does it take?', '5', 'Size over speed.', ['Size: 700 MB.', 'Speed: 140 MB per second.', eq('700 ÷ 140 = 5 seconds')], check=5)
K.calc('h', 'A folder holds 40 files. 25 end in .jpg and 6 of those start with a dot. How many does ls *.jpg list?', '19', 'A star skips hidden names.', ['.jpg names: 25.', 'Hidden ones are skipped by *: 6.', eq('25 − 6 = 19')], check=19)

K.must('Make', 'mkdir (with -p for parents) makes folders. touch makes empty files or updates times.')
K.must('Copy and move', 'cp copies, cp -r or -a for folders. mv moves and renames. Both overwrite silently, use -i or -n.')
K.must('Delete', 'rm deletes for good, rm -r for folders, rmdir only empty folders. List first, then delete.')
K.must('Globs', '* any text, ? one character, [abc] one from a set. The shell expands them. * skips hidden names.')
K.must('Braces', '{a,b} and {1..5} make words even without files: mkdir day{1..3}.')

T = K.topic(
    slug='manage-files', topic='manage-files',
    step=(2, 'Files and folders', 'lx-basics-2', 'The single file tree, paths, making, copying, moving and deleting files and folders, wildcards, and reading files.', 'Beginner'),
    title='Working with files and folders', short='Files and folders', badge='2.2', minutes=35, added='2026-11-23',
    lead='Make, copy, move, rename and delete files and folders, handle many files at once with wildcards and braces, and build the habits that stop you deleting the wrong thing.',
    desc='mkdir and mkdir -p, touch, file naming rules, cp, cp -r and cp -a, mv for moving and renaming, rm, rm -r, rm -i and rmdir, why there is no undo, globbing with * ? and [ ], brace expansion, and what happens inside the kernel.',
    summary='mkdir, touch, cp, mv, rm and rmdir, safe deleting, wildcards and brace expansion.',
    keywords=['mkdir', 'touch', 'cp', 'mv', 'rm', 'rmdir', 'rename', 'wildcards', 'glob', 'brace expansion', 'delete files'],
    recap='<p>mkdir -p, touch, cp -r, mv and rm -r cover daily file work. Wildcards and braces handle many names at once. rm has no undo, so list first.</p>')
