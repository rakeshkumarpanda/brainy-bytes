# Foundations 1.3: getting help. Sources: man(1) and man-pages(7) (section numbers and page layout), the bash help
# builtin, GNU coding standards (--help and --version), info(1), whatis(1) and apropos(1) from man-db, the tldr-pages
# project. The build container is a minimal image without manual pages, so man output is shown as a typical example.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('man', 'The manual: man pages', f'''
<p>Every Linux system carries its own manual. Type <code>man</code> followed by a command name and you get its <b>manual page</b>: what it does, every option, examples and related commands. It works without internet, and it describes the exact version installed on that machine.</p>
{sample('Open the manual page of ls', 'man ls', """LS(1)                         User Commands                         LS(1)

NAME
       ls - list directory contents

SYNOPSIS
       ls [OPTION]... [FILE]...

DESCRIPTION
       List  information  about  the FILEs (the current directory by default).
       Sort entries alphabetically if none of -cftuvSUX nor --sort is specified.

       -a, --all
              do not ignore entries starting with .""", note='This build machine has no manual pages installed, so this is how the top of the page looks on Ubuntu 24.04. The (1) means section 1, user commands.')}
{table(['Key inside man', 'What it does'], [
    ['Space or Page Down', 'Next screen'], ['b or Page Up', 'Previous screen'], ['/word then Enter', 'Search forward for word'],
    ['n and N', 'Next and previous match'], ['g and G', 'Top and bottom of the page'], ['h', 'Help on all keys'], ['q', 'Quit, back to the prompt']])}
<p>The page is shown by a <b>pager</b>, usually <code>less</code>, which is why the keys are the same as in less.</p>
{table(['Heading', 'What you find there'], [
    ['NAME', 'The command and a one line description'],
    ['SYNOPSIS', 'How to call it. [ ] means optional, ... means can repeat, so ls [OPTION]... [FILE]... means zero or more options then zero or more files'],
    ['DESCRIPTION', 'What it does and every option'],
    ['EXIT STATUS', 'The numbers it returns, 0 for success'],
    ['EXAMPLES', 'Ready to copy uses (not every page has them)'],
    ['SEE ALSO', 'Related pages, for example cp(1) and dir_colors(5)']])}
{talk('The Unix manual is older than most of the commands in it. The first edition of the Unix Programmer’s Manual was written by Ken Thompson and Dennis Ritchie in November 1971, and it already had a page for every command, with a name, a synopsis and a description, exactly the layout you still see today. When Unix spread to universities, the manual came on the same tape, so every machine carried its own documentation. That habit is very useful. A web page might describe a newer or older version of a command, but the man page on the machine describes exactly the version installed there. Engineers who work on servers without internet access depend on it. Learn four keys and you can read any page: Space to go down, slash to search, n for the next match, and q to quit.')}
''', kw=['man', 'manual page', 'man pages', 'SYNOPSIS', 'less', 'pager', 'q to quit'])

K.lesson('sections', 'Manual sections and searching the manual', f'''
<p>The manual is split into numbered <b>sections</b>, because the same name can mean different things. passwd is a command you run, and it is also a file format.</p>
{table(['Section', 'Contains', 'Example'], [
    ['1', 'User commands', 'ls(1), passwd(1)'], ['2', 'System calls, the kernel’s services', 'open(2), fork(2)'],
    ['3', 'Library functions, mostly C', 'printf(3)'], ['4', 'Special files, usually in /dev', 'null(4)'],
    ['5', 'File formats and configuration files', 'passwd(5), crontab(5)'], ['6', 'Games', 'fortune(6)'],
    ['7', 'Overviews and conventions', 'man-pages(7), signal(7), regex(7)'], ['8', 'System administration commands, usually for root', 'mount(8), useradd(8)']])}
{fxs(fx('A page from one section', '<code>man 5 passwd</code>', 'Without the number, man shows the first section that has the page, here passwd(1), the command.', key=True),
     fx('Search page descriptions', '<code>man -k word</code> = <code>apropos word</code>', 'Lists every page whose NAME line contains the word, with its section.', key=True),
     fx('One line summary', '<code>whatis ls</code> = <code>man -f ls</code>', 'Prints only the NAME line.'))}
{sample('Find commands when you do not know their name', 'apropos "copy files"', """cp (1)               - copy files and directories
cpio (1)             - copy files to and from archives
install (1)          - copy files and set attributes
rsync (1)            - a fast, versatile, remote (and local) file-copying tool""", note='apropos searches a small database that is rebuilt by mandb, usually every day. On a fresh system run sudo mandb once if apropos finds nothing.')}
{note('When people write ls(1) or crontab(5) in a book or chat, the number is the manual section. Read crontab(5) as: run man 5 crontab.', 'exam')}
{talk('The idea of numbered sections comes straight from the printed Unix manuals of the 1970s, which were real books with chapters. Chapter one held the commands, chapter two the system calls, chapter three the library functions, and so on. When the manual moved onto the computer, the numbers stayed. They are still useful, because one word can name different things. For example, passwd is a command that changes your password, and it is also the file slash etc slash passwd, which lists the users. man passwd shows the command, man 5 passwd shows the file format. The other great trick is searching. If you remember what you want to do but not the name of the command, apropos looks through the one line descriptions of every page. Typing apropos copy shows cp, rsync and other tools you may never have heard of.')}
''', kw=['man sections', 'man 5', 'apropos', 'man -k', 'whatis', 'mandb', 'section 1', 'section 8'])

K.lesson('quick', 'Quick help: --help, help, info and tldr', f'''
<p>A full manual page is long. Often you only need a reminder.</p>
{cmdtable([
    ('COMMAND --help', 'Prints a short summary of the options straight into the terminal. Almost every GNU program has it.', 'ls --help | head'),
    ('help BUILTIN', 'Help for commands built into bash, which have no man page of their own', 'help cd'),
    ('COMMAND --version', 'Shows which version you have, useful before you read a web page about it', 'ls --version'),
    ('info COMMAND', 'The GNU manual, longer and with chapters and links. Move with Tab and Enter, q quits', 'info coreutils'),
    ('tldr COMMAND', 'Community written short examples (install the tldr client first)', 'tldr tar')])}
{run('Quick help, run for real', '''ls --help | head -n 4
help cd | head -n 3
ls --version | head -n 1''', note='The GNU coding standards ask every GNU program to support --help and --version, which is why they work almost everywhere on Linux.')}
{note('help only knows shell builtins (cd, echo, export, type, history). For a builtin, man cd usually opens the long bash manual instead, so try help first.', 'tip')}
{note('Options that work on Linux may not work on macOS, because macOS uses BSD versions of many tools. When an example from the web fails, check --version and the local man page.', 'warn')}
{talk('Here is a habit used by experienced engineers. Before typing a command they have not used for a while, they run it with dash dash help and pipe it into head, to see the first few lines of options. It takes two seconds and avoids guesses. The dash dash help and dash dash version options are a promise from the GNU coding standards, written in the 1990s by the Free Software Foundation, so nearly every Linux tool supports them. The help command is different. It explains commands that live inside bash itself, like cd and history. In 2013 a group of volunteers started the tldr pages project, short for too long, did not read, which gives a few practical examples for each command instead of the full manual. It is popular with beginners. A good order to remember is help or dash dash help first, then man, then the web.')}
''', kw=['--help', 'help builtin', '--version', 'info', 'tldr', 'GNU coding standards', 'BSD vs GNU'])

K.lesson('practice', 'Getting unstuck, step by step', f'''
<p>Here is a routine that solves most "how do I" moments, in order.</p>
{steps('From stuck to solved', [
    'Do you know the command name? If not, run <code>apropos word</code> with a word that describes the job.',
    'Need a reminder of one option? Run <code>COMMAND --help | less</code> or <code>help COMMAND</code> for a builtin.',
    'Need the full story? Run <code>man COMMAND</code>, press / and type the option or word you need.',
    'Got an error message? Read it slowly. Linux errors usually name the file and the reason, for example "No such file or directory" or "Permission denied".',
    'Still stuck? Search the web with the exact error text in quotes and the name of your distribution, and check that the answer matches your version.'])}
{table(['Common error', 'What it means', 'First thing to try'], [
    ['command not found', 'The program is not installed, misspelled, or not in PATH', 'Check spelling, then type, then install the package'],
    ['No such file or directory', 'The path is wrong', 'pwd and ls to see where you are, Tab to complete the name'],
    ['Permission denied', 'You lack the right to read, write or run it', 'ls -l to see the permissions, sudo only if it is a system file you mean to change'],
    ['Is a directory', 'You gave a folder to a command that wants a file', 'Use ls for folders, or the -r option where it exists'],
    ['Usage: ...', 'The options or arguments are wrong', 'Read the usage line, it is a short SYNOPSIS']])}
{lab('Find help without leaving the terminal', [
    ('Read the short manual of <code>ls</code> with man.', 'man ls', [{'cmd': r'^\s*man\s+ls'}]),
    ('Read the manual of <code>man</code> itself to see the section numbers.', 'man man', [{'cmd': r'^\s*man\s+man'}, {'out': 'Sections'}]),
    ('Ask the shell what kind of command <code>history</code> is.', 'type history', [{'cmd': r'type\s+history'}, {'out': 'builtin'}]),
    ('Make an error on purpose: list a folder that does not exist, <code>nofolder</code>.', 'ls nofolder', [{'out': 'No such file or directory'}]),
    ('Run a command that is not installed in the practice shell, <code>banana</code>, and read the error.', 'banana', [{'out': 'command not found'}])])}
{talk('Every expert gets stuck. The difference is that they have a routine for getting unstuck. The most important step is the cheapest one: read the error message. Linux error messages are short but precise. No such file or directory almost always means a typo or the wrong folder, and permission denied means the file exists but you are not allowed to touch it. Many beginners skip the message and paste the whole problem into a search engine. Try the manual first. The answers there match your exact version, and you will learn options you did not know about. When you do search the web, put the exact error text in quotation marks and add the name of your distribution, for example Ubuntu 24.04. And check the date of the answer, because a command explained in 2012 may have changed since then.')}
''', kw=['error messages', 'No such file or directory', 'Permission denied', 'command not found', 'troubleshooting', 'apropos'])

K.lesson('levels', 'Documentation from school to research', f'''
{ladder(
    '<p>Linux has a book of instructions built in. Type man and the name of a command, and it tells you how to use it. Press q to close the book.</p>',
    '<p>Manual pages are grouped into sections (1 commands, 2 system calls, 3 library calls, 5 file formats, 8 admin commands). man -k searches descriptions. Builtins are explained by help, GNU programs answer --help and --version, and info holds longer GNU manuals.</p>',
    '<p>Man pages are written in the roff typesetting language with the man or mdoc macros and rendered by groff or mandoc. mandb indexes them for whatis and apropos. The Linux man-pages project documents the kernel and glibc interfaces in sections 2, 3, 4, 5 and 7, and is the reference for system programmers alongside POSIX.</p>',
    '<p>Research on documentation includes studies of how developers search for help, automatic generation of examples from manuals, checking that documentation matches code behaviour, and using language models to explain commands. Projects such as explainshell map each word of a command line to the matching part of its man page.</p>')}
{scene('a job interview', '<p>An interviewer asks how you would find the option that makes cp keep file times. A strong answer is not a guess: "I would run man cp and search for time with /time, which shows --preserve, or check cp --help." Showing how you find answers is valued as much as remembering them.</p>')}
{talk('Man pages are written in a very old typesetting language called roff, which dates back to the early 1970s and was one of the first programs used at Bell Labs. In fact, the Unix team got money for a new computer partly by promising to build a system for preparing patent documents, and roff was part of that work. Today the Linux man pages project, led for many years by Michael Kerrisk, documents the system calls and library functions of Linux, and programmers around the world rely on it. At the research end, people study how developers search for help, and tools like explainshell take a whole command line and show which part of the manual explains each word. Whatever level you reach, the skill stays the same. Good engineers know how to find a reliable answer quickly, and the manual on the machine is the most reliable place to start.')}
''', kw=['roff', 'groff', 'mandoc', 'man-pages project', 'explainshell', 'documentation'])

K.quiz('e', 'Which command shows the manual page of cp?', ['help cp', 'man cp', 'cp man', 'info --cp'], 1, 'Three letters for manual.', 'man cp opens the manual page.')
K.quiz('e', 'Which key leaves a man page?', ['Esc', 'q', 'Ctrl X', 'Enter'], 1, 'Quit.', 'The pager less quits with q.')
K.quiz('e', 'How do you search for the word size inside a man page?', ['Type /size and press Enter', 'Type search size', 'Press F3', 'Type ?size?'], 0, 'Slash searches forward.', 'In less, /word searches forward and n goes to the next match.')
K.quiz('e', 'Which gives help for the bash builtin cd?', ['man cd only', 'help cd', 'cd --manual', 'whatis cd only'], 1, 'Builtins have their own help.', 'help explains shell builtins.')
K.quiz('m', 'Which manual section holds file formats such as /etc/passwd?', ['1', '2', '5', '8'], 2, 'Configuration files.', 'Section 5 is file formats. man 5 passwd explains the file.')
K.quiz('m', 'You forgot the name of a command that compresses files. What do you run?', ['man compress-files', 'apropos compress', 'help compress', 'which compress'], 1, 'Search descriptions.', 'apropos (man -k) searches the NAME lines of all pages.')
K.quiz('m', 'In the synopsis ls [OPTION]... [FILE]..., what do the brackets mean?', ['Required', 'Optional', 'Type the brackets', 'Comments'], 1, 'You can run plain ls.', '[ ] means optional and ... means it can repeat.')
K.quiz('m', 'mount(8) in a document tells you that mount is', ['a library call', 'an administration command, usually for root', 'a game', 'a file format'], 1, 'Section 8.', 'Section 8 holds system administration commands.')
K.quiz('m', 'An example from a web page fails with "illegal option" on your Mac. Most likely reason?', ['Your Mac is broken', 'macOS uses BSD versions of the tool with different options', 'You need root', 'The file is missing'], 1, 'GNU versus BSD.', 'Check the local man page, the BSD tool may spell the option differently.')
K.quiz('h', 'apropos finds nothing on a brand new server. What helps?', ['Reinstall Linux', 'Run sudo mandb to build the index', 'Use help instead', 'Reboot twice'], 1, 'apropos reads a database.', 'mandb builds the index that whatis and apropos read.')
K.quiz('x', 'Which manual section documents fork and open as the kernel provides them?', ['1', '2', '3', '7'], 1, 'System calls.', 'Section 2 is system calls. Section 3 has the C library wrappers like fopen.')

K.calc('e', 'A man page is 480 lines long and your terminal shows 24 lines per screen. How many presses of Space take you from the first screen to the last? (The first screen is already shown.)', '19', 'Count screens, then subtract the one already shown.',
       ['Screens: 480 ÷ 24 = 20.', 'You already see screen 1.', eq('20 − 1 = 19 presses')], check=480 // 24 - 1)
K.calc('e', 'There are 8 standard manual sections. passwd has pages in sections 1 and 5. How many sections have no passwd page?', '6', 'Total minus the ones that have it.',
       ['Sections in all: 8.', 'With passwd: 2.', eq('8 − 2 = 6')], check=6)
K.calc('m', 'Reading the full manual takes 6 minutes, --help takes 1 minute. You look up 25 options this week, and 20 of them are answered by --help alone. If you try --help first and open man only when needed, how many minutes do you spend?', '55', 'Every lookup pays for --help, five also pay for man.',
       ['--help for all 25: 25 × 1 = 25 minutes.', 'man for the 5 that needed it: 5 × 6 = 30 minutes.', eq('25 + 30 = 55 minutes (instead of 150 with man every time)')], check=25 + 5 * 6)
K.calc('m', 'apropos copy returns 12 pages. 7 are in section 1, 2 in section 3, the rest in section 8. How many are admin commands?', '3', 'The rest.',
       ['Section 1 and 3 together: 7 + 2 = 9.', 'Total: 12.', eq('12 − 9 = 3 in section 8')], check=3)
K.calc('m', 'A man page search /size finds 9 matches. You are on match 1. How many presses of n reach the last match?', '8', 'Each n moves one match.',
       ['Matches: 9.', 'Start at 1.', eq('9 − 1 = 8 presses')], check=8)
K.calc('h', 'The first Unix manual was dated November 1971. How many years before the Linux announcement in August 1991 is that, in whole years?', '19', 'Count from November 1971 to August 1991.',
       ['November 1971 to November 1990 is 19 years.', 'November 1990 to August 1991 is 9 more months, less than a year.', eq('19 whole years')], check=19)

K.must('man', 'man COMMAND opens the manual. Space next, b back, /word search, n next match, q quit.')
K.must('Sections', '1 commands, 2 system calls, 3 library, 5 file formats, 7 overviews, 8 admin. man 5 passwd picks a section.')
K.must('Searching', 'apropos word (man -k) finds pages by description, whatis gives one line. mandb builds the index.')
K.must('Quick help', 'COMMAND --help for options, help BUILTIN for bash builtins, --version before trusting a web answer.')
K.must('Read errors', 'command not found, No such file or directory, Permission denied and Is a directory each point to a clear first step.')

T = K.topic(
    slug='getting-help', topic='getting-help',
    step=(1, 'Meet Unix and Linux', 'lx-basics-1', 'What an operating system is, where Unix and Linux came from, the terminal and the shell, and how to ask the system for help.', 'Beginner'),
    title='Getting help: man, --help and friends', short='Getting help', badge='1.3', minutes=25, added='2026-11-23',
    lead='Learn to answer your own questions: read manual pages, use their sections, search the manual, get quick help from --help and help, and turn error messages into fixes.',
    desc='man pages and the less pager, SYNOPSIS notation, manual sections 1 to 8, man -k and apropos, whatis, --help and --version, the help builtin, info and tldr, reading common error messages and a routine for getting unstuck.',
    summary='man pages, manual sections, apropos and whatis, --help, help for builtins, info and tldr, and reading error messages.',
    keywords=['man', 'man page', 'apropos', 'whatis', 'help', '--help', 'info', 'tldr', 'manual sections', 'error messages'],
    recap='<p>man COMMAND for the full manual, COMMAND --help or help BUILTIN for a reminder, apropos to find a command by what it does, and always read the error message first.</p>')
