# Foundations 3.2: editing text in the terminal. nano and vim, choosing the default editor, small edits without an
# editor. Sources: GNU nano manual and nano(1) (version 7.2 key list, ^O ^X ^K ^U ^W M-U M-E ^_), vim(1),
# Vim :help (modes, motions, operators, :w :q :q! :wq ZZ, vimtutor), Debian select-editor(1) and
# update-alternatives(1), sudoedit in sudo(8), git-var(1) for GIT_EDITOR, VISUAL and EDITOR order.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('nano', 'nano: the friendly editor', f'''
<p>Servers usually have no mouse and no windows, so you edit configuration files right inside the terminal. <code>nano</code> is the easiest editor to start with: you type and the text appears, and the main commands are listed at the bottom of the screen. In that list <b>^</b> means the Ctrl key and <b>M-</b> means the Alt key.</p>
{sample('What nano looks like', 'nano notes.txt', """  GNU nano 7.2                       notes.txt
Buy milk
Call grandma
Finish the Linux lesson


                             [ Read 3 lines ]
^G Help      ^O Write Out ^W Where Is  ^K Cut       ^T Execute   ^C Location
^X Exit      ^R Read File ^\\ Replace   ^U Paste     ^J Justify   ^/ Go To Line""", note='The two bottom rows are the shortcut list. The exact list changes a little between nano versions.')}
{cmdtable([
    ('Ctrl+O, Enter', 'Write out (save) the file, Enter accepts the file name', '^O'),
    ('Ctrl+X', 'Exit. If there are unsaved changes nano asks Y or N first', '^X'),
    ('Ctrl+K', 'Cut the current line', '^K'),
    ('Ctrl+U', 'Paste the lines you cut', '^U'),
    ('Ctrl+W', 'Search for text (Where Is)', '^W'),
    ('Alt+U and Alt+E', 'Undo and redo', 'M-U'),
    ('Ctrl+G', 'Help with every shortcut', '^G'),
    ('nano +12 FILE', 'Open the file with the cursor on line 12', 'nano +12 app.conf')], head=('Keys', 'What it does', 'Shown as'))}
{steps('Edit a file with nano', [
    'Open it: <code>nano notes.txt</code>.',
    'Move with the arrow keys and type your change.',
    'Press Ctrl+O, check the file name at the bottom, press Enter.',
    'Press Ctrl+X to leave.'])}
{talk('If you have never edited a file in a terminal, start with nano. It works like a basic notepad. You open a file, move with the arrow keys, type, and the text appears. The only new thing is that commands use the Control key, and nano lists them at the bottom of the screen, where a small hat symbol means Control. Control O writes the file to disk, which nano calls write out. Control X exits, and if you forgot to save, nano asks you first. Control K cuts a whole line and Control U pastes it back, which is the quickest way to move lines around. nano began in 1999 as a free copy of an older editor called Pico, and today it is installed by default on Ubuntu and many other distributions, so it is a safe choice on almost any server you log into.')}
''', kw=['nano', 'Ctrl+O', 'Ctrl+X', 'write out', 'cut paste line', 'terminal editor', 'Pico'])

K.lesson('vim', 'vim: the editor with modes', f'''
<p><code>vim</code> (Vi IMproved) is on nearly every Unix system, often also as <code>vi</code>. It looks strange at first because it has <b>modes</b>. In <b>Normal</b> mode every key is a command: j moves down, dd deletes a line. In <b>Insert</b> mode keys type text. You switch between them all the time, and once your fingers know the keys, editing becomes very fast.</p>
{fxs(fx('Normal', 'the starting mode', 'Keys move the cursor and change text. Esc always brings you back here.', key=True),
     fx('Insert', 'typing text', 'Enter with i, a, A, o or O. The bottom line shows -- INSERT --.'),
     fx('Command line', 'starts with :', ':w saves, :q quits, :wq saves and quits, :q! quits without saving.', key=True),
     fx('Visual', 'selecting', 'v selects characters, V whole lines. Then d deletes or y copies the selection.'))}
{play('lx-vim')}
{cmdtable([
    ('h j k l', 'Left, down, up, right (the arrow keys work too)', 'jjj'),
    ('w and b', 'Next word, back one word', 'w'),
    ('0 and $', 'Start and end of the line', '$'),
    ('gg and G', 'First line and last line. 12G goes to line 12', 'G'),
    ('i a A o O', 'Insert before, append after, append at line end, open line below, open line above', 'o'),
    ('x', 'Delete the character under the cursor', 'x'),
    ('dd and yy', 'Delete (cut) a line, yank (copy) a line', 'dd'),
    ('p and P', 'Paste after or before the cursor', 'p'),
    ('u and Ctrl+R', 'Undo and redo', 'u'),
    ('/word, n, N', 'Search forwards, next match, previous match', '/ERROR'),
    (':%s/old/new/g', 'Replace every old with new in the whole file', ':%s/http/https/g'),
    (':w :q :wq :q!', 'Save, quit, save and quit, quit and discard changes', ':wq')], head=('In Normal mode', 'What it does', 'Example'))}
{note('Stuck in vim with keys doing strange things? Press Esc two times, then type <code>:q!</code> and Enter to leave without saving. Run <code>vimtutor</code> for a free 30 minute lesson inside vim itself.', 'tip')}
{deep('Why vim keys combine like words', '<p>Most Normal mode commands are an <b>operator</b> followed by a <b>motion</b>. d is delete, c is change, y is yank. w is a word, $ is the end of the line, G is the end of the file. So dw deletes a word, d$ deletes to the end of the line, yG copies everything to the end of the file and cw changes a word. A number repeats: 3dd deletes three lines. Once you know 5 operators and 10 motions you have 50 commands without learning each one.</p>')}
{talk('vim is famous for being hard to quit. A question on Stack Overflow called how do I exit the vim editor has been viewed millions of times. The reason is modes. When vim opens, it is in Normal mode, where letters are commands, not text. Press i to enter Insert mode and type normally. Press Escape to go back. To save and quit, type colon w q and press Enter. To quit and throw away changes, type colon q exclamation mark. The original vi was written by Bill Joy at Berkeley in 1976, for slow terminals where every keystroke mattered. Bram Moolenaar released vim in 1991 and looked after it for over thirty years. Why learn it? Because vi or vim is present on almost every Unix machine, even tiny rescue systems, and because its keys work like a small language. d means delete and w means word, so d w deletes a word.')}
''', kw=['vim', 'vi', 'Normal mode', 'Insert mode', ':wq', ':q!', 'dd', 'yy', 'how to exit vim', 'vimtutor', 'operator motion'])

K.lesson('choose', 'Choosing an editor and editing without one', f'''
<p>Programs such as <code>crontab -e</code>, <code>git commit</code> and <code>visudo</code> open an editor for you. They look at the <b>VISUAL</b> and <b>EDITOR</b> variables to decide which one. On Debian and Ubuntu, <code>select-editor</code> asks you once and remembers the answer.</p>
{cmdtable([
    ('export EDITOR=nano', 'Use nano from now on in this shell (add it to ~/.bashrc to keep it)', 'export EDITOR=vim'),
    ('select-editor', 'Debian and Ubuntu: pick your editor from a numbered list', 'select-editor'),
    ('sudoedit FILE', 'Edit a root owned file safely: your editor works on a copy, sudo writes it back', 'sudoedit /etc/hosts'),
    ('vim -R FILE or view FILE', 'Open read only, so you cannot change it by accident', 'view /etc/fstab')])}
{run('Small edits without opening an editor', """echo "Water the plants" >> notes.txt
cat notes.txt
cat > shopping.txt << 'END'
milk
eggs
bread
END
cat shopping.txt
vim -Es -u NONE -c '%s/milk/oat milk/' -c 'wq' shopping.txt
cat shopping.txt""", note='&gt;&gt; adds a line at the end of a file, and cat with a here document writes several lines at once. Both are explained fully in Shell Power Tools. The vim line runs vim with no screen: it replaces milk with oat milk and saves, which is handy in scripts.')}
{note('Never edit /etc/sudoers with a normal editor. Use <code>visudo</code>, which checks the file before saving. A typing mistake in that file can stop sudo working for everyone.', 'warn')}
{lab('Edit files the shell way', [
    ('Add the line <code>Water the plants</code> to the end of <code>notes.txt</code>.', 'echo "Water the plants" >> notes.txt', [{'has': ['notes.txt', 'Water the plants']}, {'has': ['notes.txt', 'Buy milk']}]),
    ('Create <code>todo.txt</code> containing the single line <code>learn vim</code>.', 'echo "learn vim" > todo.txt', [{'has': ['todo.txt', 'learn vim']}, {'lines': ['todo.txt', 1]}]),
    ('Write a three line file <code>list.txt</code> (milk, eggs, bread) with cat and a here document.', "cat > list.txt << 'END'\nmilk\neggs\nbread\nEND", [{'lines': ['list.txt', 3]}, {'has': ['list.txt', 'eggs']}]),
    ('Make vim your default editor for this shell.', 'export EDITOR=vim', [{'env': ['EDITOR', 'vim']}]),
    ('Check the result by printing the variable.', 'echo $EDITOR', [{'out': '^vim$'}])])}
{talk('Some commands open an editor on their own. When you run crontab dash e to schedule a job, or git commit without a message, the program needs to know which editor you like. It checks a variable called VISUAL, then one called EDITOR, and falls back to a default, often nano or vi. Set EDITOR in your bashrc file and every program follows your choice. Also remember that many small edits need no editor at all. Two arrows add a line to the end of a file. cat with a here document writes several lines at once. Even vim can be told to make a change and save without showing a screen, which is useful in scripts. And for the system file that controls sudo, always use visudo, because it refuses to save a broken file that could lock everyone out.')}
''', kw=['EDITOR', 'VISUAL', 'select-editor', 'sudoedit', 'visudo', 'here document', 'append line', 'vim -Es', 'view'])

K.lesson('levels', 'Editors from school to research', f'''
{ladder(
    '<p>nano is the easy editor: type, Ctrl+O to save, Ctrl+X to exit. vim has modes: i to type, Esc to stop typing, :wq to save and quit, :q! to quit without saving.</p>',
    '<p>Terminal editors read the file into a buffer, let you change it, and write the buffer back on save. vim is modal and composes operators (d, c, y) with motions (w, $, G, text objects such as iw). Programs pick an editor from VISUAL, then EDITOR, and Debian also offers the sensible-editor command.</p>',
    '<p>Editors draw the screen through terminal escape codes described by the terminfo database (TERM). Safe saving writes a new file and renames it over the old one, or writes in place with a backup, which vim controls with the backupcopy option. vim keeps a swap file (.notes.txt.swp) so a crash or a lost SSH connection does not lose work, and warns when another vim already edits the same file.</p>',
    '<p>Text editors are a research subject in human computer interaction, from studies of modal versus modeless editing (Larry Tesler argued against modes at Xerox PARC in the 1970s) to the data structures that hold the text, such as gap buffers, piece tables and ropes, and to CRDTs that let several people edit the same file at once without a central server.</p>')}
{scene('the lost SSH session', '<p>An admin edits /etc/nginx/nginx.conf in vim over a slow connection and the session drops. On logging back in, vim says a swap file .nginx.conf.swp exists. Pressing R recovers the unsaved changes, and after checking them the admin deletes the swap file. nano saves a similar emergency copy named nginx.conf.save.</p>')}
{talk('Under the surface, an editor is a program that loads a file into memory, lets you change that copy, and writes it back when you save. The screen is drawn with special character codes that the terminal understands, and the TERM variable tells the editor which codes to use. vim protects you with a swap file. If your connection drops in the middle of editing, the swap file still holds your changes, and vim offers to recover them the next time you open the file. Researchers have studied editors for decades. Larry Tesler at Xerox famously argued that modes confuse people, while vim users argue that modes make editing faster once learned. Inside, editors use clever structures such as piece tables and ropes to change large files quickly, and modern collaborative editors use special data types called CRDTs so many people can type in the same document at once.')}
''', kw=['buffer', 'terminfo', 'swap file', 'recovery', 'modal editing', 'piece table', 'rope', 'CRDT'])

K.quiz('e', 'In nano, which keys save the file?', ['Ctrl+S', 'Ctrl+O then Enter', 'Ctrl+X', 'Esc :w'], 1, 'Write Out.', 'Ctrl+O writes out the file, Enter accepts the name.')
K.quiz('e', 'In vim, which key starts typing text before the cursor?', ['i', 'x', 'q', 'd'], 0, 'Insert.', 'i enters Insert mode.')
K.quiz('e', 'How do you quit vim without saving?', [':wq', ':q!', 'Ctrl+X', 'exit'], 1, 'Force quit.', ':q! quits and discards changes.')
K.quiz('e', 'What does ^X mean in the nano shortcut list?', ['The X key twice', 'Ctrl+X', 'Shift+X', 'Alt+X'], 1, 'The hat is Ctrl.', '^ stands for the Ctrl key, M- for Alt.')
K.quiz('m', 'In vim Normal mode, what does dd do?', ['Duplicates a line', 'Deletes (cuts) the current line', 'Moves down', 'Saves'], 1, 'Delete line.', 'dd deletes the line into the register, p pastes it.')
K.quiz('m', 'You typed :wq but the text ":wq" appeared in your file. What happened?', ['vim is broken', 'You were still in Insert mode, press Esc first', 'The file is read only', 'You need sudo'], 1, 'Modes.', 'Commands work only after Esc returns you to Normal mode.')
K.quiz('m', 'Which variable do programs such as crontab -e check to choose your editor?', ['SHELL', 'EDITOR (after VISUAL)', 'TERM', 'PATH'], 1, 'Editor variable.', 'Programs check VISUAL, then EDITOR.')
K.quiz('m', 'Which vim command replaces every "http" with "https" in the whole file?', ['/http/https', ':%s/http/https/g', ':r http https', 'cw https'], 1, 'Substitute on every line.', '% means all lines, s substitute, g every match in a line.')
K.quiz('m', 'What is the safe way to edit /etc/sudoers?', ['nano /etc/sudoers', 'visudo', 'echo >> /etc/sudoers', 'chmod 777 /etc/sudoers'], 1, 'It checks before saving.', 'visudo checks the syntax so a mistake cannot lock you out.')
K.quiz('h', 'What does d$ do in vim?', ['Deletes the whole file', 'Deletes from the cursor to the end of the line', 'Deletes the last line', 'Saves and quits'], 1, 'Operator plus motion.', 'd is delete, $ is the end of the line.')
K.quiz('h', 'vim says a swap file .app.conf.swp exists. What is the most likely cause?', ['The file is a virus', 'An earlier vim session on this file crashed or is still open', 'The disk is full', 'The file is binary'], 1, 'Crash protection.', 'vim keeps a swap file while editing and leaves it behind after a crash.')
K.quiz('h', 'Why do sysadmins learn vi even if they prefer nano?', ['vi is faster to install', 'vi or vim is present on almost every Unix system, even minimal ones', 'nano cannot save', 'vi has a mouse'], 1, 'Always there.', 'vi is part of the POSIX standard, so it is installed on nearly every Unix-like system.')
K.quiz('x', 'In vim, what does 3dw do?', ['Deletes 3 lines', 'Deletes 3 words', 'Moves 3 words', 'Copies 3 words'], 1, 'Count, operator, motion.', 'A count repeats the operator and motion: three words are deleted.')

K.calc('e', 'In vim you press dd on line 4 of a 10 line file. How many lines are left?', '9', 'One line removed.', ['Start: 10 lines.', 'dd removes 1.', eq('10 − 1 = 9')], check=9)
K.calc('e', 'You yank one line with yy and press p three times. How many new lines appear?', '3', 'Each p pastes once.', ['The register holds 1 line.', 'p is pressed 3 times.', eq('1 × 3 = 3 new lines')], check=3)
K.calc('m', 'A file has 120 lines. You are on line 1. What count do you type before G to land on line 87?', '87', 'nG goes to line n.', ['G alone goes to the last line.', 'A number before G names the line.', eq('87G')], check=87)
K.calc('m', 'You run 5dd on line 3 of a 20 line file. How many lines does the file have afterwards?', '15', 'A count repeats dd.', ['5dd deletes lines 3 to 7.', 'Lines removed: 5.', eq('20 − 5 = 15')], check=15)
K.calc('m', 'With 5 operators (d c y > <) and 8 motions (w b e $ 0 G gg }), how many operator plus motion pairs are there?', '40', 'Every operator with every motion.', ['Operators: 5.', 'Motions: 8.', eq('5 × 8 = 40 commands')], check=40)
K.calc('h', 'You save a 2 MB file over SSH at 250 KB per second upload speed for a remote editor that sends the whole file. About how many seconds does each save take?', '8', 'Size over speed, 1 MB = 1000 KB here.', ['Size: 2 MB = 2000 KB.', 'Speed: 250 KB per second.', eq('2000 ÷ 250 = 8 seconds')], check=8)

K.must('nano', 'Type to edit. Ctrl+O and Enter saves, Ctrl+X exits, Ctrl+K cuts a line, Ctrl+U pastes, Ctrl+W searches.')
K.must('vim modes', 'Normal for commands, Insert (i a o) for typing, Esc to go back, : for the command line.')
K.must('vim survival', ':w save, :q quit, :wq save and quit, :q! quit without saving. When lost, Esc Esc then :q!.')
K.must('vim editing', 'x, dd, yy, p, u, /word, :%s/old/new/g. Operators plus motions: dw, d$, cw. Learn with vimtutor.')
K.must('Editor choice', 'Programs use VISUAL then EDITOR. Use visudo for sudoers and sudoedit for root files. &gt;&gt; and here documents edit without an editor.')

T = K.topic(
    slug='editors', topic='editors',
    step=(3, 'Permissions and editing', 'lx-basics-3', 'Who may read, change or run each file, and how to edit text in the terminal with nano and vim.', 'Beginner'),
    title='Editing text: nano and vim', short='nano and vim', badge='3.2', minutes=35, added='2026-11-23',
    lead='Edit files inside the terminal: nano for quick friendly changes, vim for speed once you know its modes, and how to choose your default editor and make small edits without opening one.',
    desc='nano keys (write out, exit, cut, paste, search, undo), vim modes, motions, operators, search and replace, saving and quitting, vimtutor, VISUAL and EDITOR, select-editor, sudoedit, visudo, swap files and recovery.',
    summary='nano, vim modes and keys, :wq and :q!, EDITOR, visudo and sudoedit.',
    keywords=['nano', 'vim', 'vi', 'exit vim', ':wq', 'editor', 'EDITOR variable', 'visudo', 'sudoedit', 'vimtutor'],
    recap='<p>nano for easy edits, vim with Normal and Insert modes, :wq to save and quit, :q! to escape, EDITOR to choose, and visudo for sudoers.</p>')
