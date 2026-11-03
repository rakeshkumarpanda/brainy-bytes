# Chapter 1.1: what version control is, why Git exists, how Git thinks (snapshots, distributed), installing and
# configuring it. Sources: Pro Git chapter 1 (git-scm.com/book), git-config and git-init manual pages, the Git 3.0
# breaking changes document (Documentation/BreakingChanges.adoc in git/git).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow

K = Kit()

K.code('versions', r'''
# Saving a project without version control: copies pile up
copies = ["report.docx", "report_v2.docx", "report_final.docx",
          "report_final_REAL.docx", "report_final_REAL_fixed.docx"]
for name in copies:
    print("saved a full copy:", name)
print(len(copies), "copies and still no answer to: what changed, who changed it, and why?")

# With version control: one file, a list of saved snapshots with a message each
history = []
def commit(msg, who):
    history.append({"id": len(history) + 1, "msg": msg, "who": who})
commit("first draft", "Asha")
commit("add sales chart", "Ravi")
commit("fix typo in title", "Asha")
for c in history:
    print("commit", c["id"], "by", c["who"] + ":", c["msg"])
''')

K.code('config', r'''
# How git config picks a value: system, then global, then local. The last one found wins.
levels = [
    ("system", "/etc/gitconfig", {"core.editor": "vi"}),
    ("global", "~/.gitconfig", {"user.name": "Asha", "user.email": "asha@home.example", "core.editor": "code --wait"}),
    ("local", ".git/config", {"user.email": "asha@work.example"}),
]
effective, origin = {}, {}
for level, path, values in levels:
    for key, value in values.items():
        effective[key] = value          # a later level overwrites an earlier one
        origin[key] = path
for key in sorted(effective):
    print(f"{key:12} = {effective[key]:22} from {origin[key]}")
''')

K.lesson('why', 'Why version control exists', f'''
<p>Think of writing a school project on a computer. You save it as <b>project.docx</b>, then you are scared to break it, so you save <b>project_v2.docx</b>, then <b>project_final.docx</b>, then <b>project_final_REAL.docx</b>. After a week you have a folder full of copies and no idea which one has the good introduction.</p>
<p><b>Version control</b> is a tool that remembers every saved version of your files for you, together with who saved it, when, and a short note on why. You keep one folder. The tool keeps the history. You can look at any old version, compare two versions, or undo a mistake, at any time.</p>
{code('versions')}
<p>Now add a team. Five people edit the same website. Without a tool, they email files around and overwrite each other\'s work. Version control lets everyone work at the same time and then <b>merges</b> their changes, and it warns when two people changed the same line.</p>
{table(['Problem without version control', 'What version control gives you'], [
    ['Many copies with confusing names', 'One folder, a clean history of saved snapshots'],
    ['No idea what changed', 'An exact list of changed lines between any two versions'],
    ['A mistake ruins the only copy', 'Go back to any earlier version'],
    ['Two people overwrite each other', 'Separate branches that are merged with checks'],
    ['Nobody knows why a line exists', 'Every change carries an author, a date and a message']])}
{scene('Google Docs version history', '<p>If you have opened File, Version history in Google Docs, you have used a simple version control system. Git does the same for whole folders of code, with much more control: you decide when a version is saved, you write the note, and you can keep several lines of work going at once.</p>')}
''', kw=['version control', 'VCS', 'history', 'why git', 'final_v2'])

K.lesson('history', 'Where Git came from and how it is different', f'''
<p>Version control systems came in three waves.</p>
{table(['Kind', 'Examples', 'Where the history lives', 'Weak spot'], [
    ['Local', 'RCS', 'One computer', 'No teamwork, one disk failure loses everything'],
    ['Centralised', 'CVS, Subversion (SVN), Perforce', 'One central server', 'Server down means nobody can commit or read history'],
    ['Distributed', 'Git, Mercurial', 'Every clone has the full history', 'More ideas to learn at the start']])}
{viz('vcs')}
<p>Git was written by Linus Torvalds in <b>2005</b> for the Linux kernel. The kernel team had used a closed tool called BitKeeper for free, and when that free licence ended they needed a replacement. The goals were speed, a simple design, strong support for thousands of parallel branches, being fully distributed, and handling a project as big as Linux. Today Git is the most widely used version control system, and GitHub, GitLab and Bitbucket are all built around it.</p>
<h3>Snapshots, not lists of differences</h3>
<p>Older tools store a file plus a list of changes to it. Git thinks differently. Every time you <b>commit</b>, Git takes a <b>snapshot</b> of what all your files look like at that moment and stores a reference to it. If a file did not change, Git does not store it again. It just points to the copy it already has.</p>
{deep('Three promises Git keeps', '<p><b>Almost everything is local.</b> Your clone has the whole history, so log, diff and commit read your own disk and are fast, even on a plane.</p><p><b>Git has integrity.</b> Everything is identified by a checksum (a SHA-1 hash today) of its content. You cannot change a file, a folder or an old commit without Git noticing, because the name would change.</p><p><b>Git generally only adds data.</b> Almost every action adds to the database. Once something is committed it is very hard to lose, especially if you push it somewhere else too.</p>')}
''', kw=['history of git', 'Linus Torvalds', 'BitKeeper', 'centralised', 'distributed', 'Subversion', 'snapshots', 'integrity', 'SHA-1'])

K.lesson('setup', 'Install Git and tell it who you are', f'''
<p>Git runs on Windows, macOS and Linux. Install it, then check the version.</p>
{table(['System', 'How to install'], [
    ['Windows', 'Download Git for Windows from git-scm.com. It includes Git Bash, a terminal where every command on these pages works.'],
    ['macOS', 'Run <code>git --version</code>. If Git is missing, macOS offers to install the Xcode command line tools. Homebrew users can run <code>brew install git</code>.'],
    ['Linux (Debian, Ubuntu)', '<code>sudo apt install git</code>'],
    ['Linux (Fedora)', '<code>sudo dnf install git</code>']])}
{sh('Check that Git works', 'git --version', 'git version 2.43.0')}
<p>Every commit records an author name and email, so set them once. <code>--global</code> means for every repository of your user account.</p>
{sh('First time setup', """git config --global user.name "Asha Rao"
git config --global user.email "asha@example.com"
git config --global init.defaultBranch main
git config --global core.editor "code --wait"
# check what Git will use, and from which file
git config --list --show-origin""")}
{fxs(
    fx('Set a value for your user', '<code>git config --global &lt;key&gt; "&lt;value&gt;"</code>', 'Stored in ~/.gitconfig. Use --local (the default inside a repository) to set it for one repository only.', key=True),
    fx('Which value wins', 'system &lt; global &lt; local', 'Git reads /etc/gitconfig, then ~/.gitconfig, then .git/config. A later file overrides an earlier one, so the most specific setting wins.', key=True),
    fx('Get help', '<code>git help &lt;command&gt;</code> or <code>git &lt;command&gt; -h</code>', 'The first opens the full manual page, the second prints a short list of options in the terminal.'))}
{viz('configlv')}
{code('config')}
{note('init.defaultBranch decides the name of the first branch in new repositories. Git 2.28 added this setting. If it is not set, current Git still uses master and prints a hint, and the Git project has said that new repositories will use main by default in Git 3.0.', 'tip')}
{note('Using a work laptop for personal projects? Set your personal email globally and your work email with git config user.email inside each work repository. The local value wins there.', 'tip')}
''', kw=['install git', 'git --version', 'git config', 'user.name', 'user.email', 'init.defaultBranch', 'core.editor', '--show-origin', 'system global local'])

K.lesson('first', 'Your first repository in two minutes', f'''
<p>A <b>repository</b> (repo) is a project folder that Git watches. The history lives in a hidden folder called <code>.git</code> inside it. Delete that folder and the files stay, but the history is gone.</p>
{sh('Make a repository and the first commit', """mkdir shop && cd shop
git init
echo "# Shop" > README.md
git status
git add README.md
git commit -m "Add README"
git log --oneline""", """Initialized empty Git repository in /home/asha/shop/.git/
On branch main
No commits yet
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md
[main (root-commit) 1a2b3c4] Add README
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
1a2b3c4 (HEAD -> main) Add README""")}
{flow(('git init', 'creates the .git folder, an empty history'), ('edit files', 'your normal work in any editor'), ('git add', 'choose which changes go in the next snapshot'), ('git commit', 'save the snapshot with a message'), ('git log', 'read the history'))}
<p>The short id <code>1a2b3c4</code> will be different on your computer, because it is a hash of the content, the author and the time. That is normal.</p>
{note('Running git init in the wrong folder, for example your whole home folder, makes Git track everything. If that happens, delete the new .git folder in that place. Your files are not touched.', 'warn')}
{steps('What you can do with these five commands', [
    'Save versions of any text project: code, notes, a book, configuration files.',
    'See exactly what changed with git diff before you commit.',
    'Go back to an older version when you break something.',
    eq('Together with git push, keep a backup of the whole history on GitHub or GitLab')])}
''', kw=['git init', 'repository', '.git folder', 'first commit', 'git add', 'git commit', 'git log'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Git is a time machine for a folder. Every time you press save in Git, called a commit, it takes a photo of all your files and writes a note on the back. You can flip back through the photos whenever you like, and friends can work on their own copies and later put the work together.</p>',
    '<p>Git is a distributed version control system. A repository holds a directed acyclic graph of commits, each one a full snapshot of the project tree identified by a cryptographic hash. Clones are complete, so most work is offline, and collaboration means exchanging commits between repositories.</p>',
    '<p>Git is a content addressable object store (blobs, trees, commits, annotated tags) plus a set of references. Storage is deduplicated by hash and packed with delta compression. Merges are three way, based on the merge base of the commit graph. Integrity follows from hashing: a commit id fixes its whole history, a Merkle tree structure.</p>',
    '<p>Open questions and current work include the move from SHA-1 to SHA-256 object names with interoperability between the two, the reftable format for references in very large repositories, partial clone and sparse checkout for monorepos, and merge algorithms. Research on mining software repositories uses Git histories to study how developers work and where bugs come from.</p>')}
{scene('the Linux kernel', '<p>The kernel has well over a million commits from thousands of people. No central server decides anything. Maintainers pull from each other\'s repositories, and Linus pulls from his lieutenants. That is the distributed model working at the largest scale.</p>')}
{note('Git and GitHub are not the same thing. Git is the tool on your computer. GitHub, GitLab and Bitbucket are websites that host Git repositories and add pull requests, issues and CI/CD pipelines.', 'exam')}
''', kw=['git vs github', 'DAG', 'content addressable', 'Merkle tree', 'SHA-256', 'reftable'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does a version control system mainly do?', ['Compiles code', 'Remembers every saved version of your files with who, when and why', 'Hosts websites', 'Finds bugs automatically'], 1, 'Think of a time machine for a folder.', 'It records history and lets you compare and restore versions.')
K.quiz('e', 'Who wrote the first version of Git, and when?', ['Bill Gates, 1995', 'Linus Torvalds, 2005', 'GitHub, 2008', 'Junio Hamano, 1999'], 1, 'The Linux kernel needed it.', 'Linus Torvalds wrote Git in 2005 after the kernel lost its free BitKeeper licence. Junio Hamano has maintained it since.')
K.quiz('e', 'Git and GitHub are', ['The same thing', 'A tool on your computer, and a website that hosts Git repositories', 'Two names for one website', 'A language and a library'], 1, 'One runs locally.', 'Git works without any website. GitHub hosts repositories and adds pull requests and Actions.')
K.quiz('e', 'Where does Git keep the history of a repository?', ['In the cloud only', 'In the hidden .git folder inside the project', 'In the Windows registry', 'In every file'], 1, 'Hidden folder.', 'Deleting .git deletes the history but leaves your files.')
K.quiz('m', 'In a centralised system the server goes down. What can a developer still do?', ['Commit and see history', 'Only edit files, no commits or history', 'Everything as usual', 'Push to a backup'], 1, 'History lives on the server.', 'With a central server, commits and log need the server. In Git they work offline.')
K.quiz('m', 'How does Git store a new version when only one of ten files changed?', ['It stores all ten files again', 'It stores the changed file and points to the nine it already has', 'It stores only a diff of every file', 'It stores nothing until push'], 1, 'Snapshots with reuse.', 'Each commit is a snapshot, but unchanged files are references to existing objects.')
K.quiz('m', 'Which config level wins when the same key is set in all three?', ['system', 'global', 'local', 'The first one read'], 2, 'Most specific wins.', 'Git reads system, global, local in order and the last value read wins.')
K.quiz('m', 'Which command shows every setting and the file it came from?', ['git config --list --show-origin', 'git status --all', 'git show config', 'git log --config'], 0, 'Show origin.', 'It prints file:path followed by key=value for each setting.')
K.quiz('h', 'Why can you not quietly change an old commit\'s content in Git?', ['Old commits are read only files', 'Everything is named by a hash of its content, so any change gives a new id', 'GitHub blocks it', 'Commits are encrypted'], 1, 'Integrity.', 'Changing content changes the hash, and every later commit refers to the old hash.')
K.quiz('h', 'What does init.defaultBranch control?', ['The branch you push to', 'The name of the first branch in newly created repositories', 'The branch CI builds', 'The branch git pull uses'], 1, 'Only for git init.', 'It sets the initial branch name. Existing repositories are not changed.')
K.quiz('x', 'Which change does the Git project list for Git 3.0 about new repositories?', ['Branches are removed', 'SHA-256 object names and main as the default branch name', 'No more merges', 'History is stored in the cloud'], 1, 'Read BreakingChanges.', 'The breaking changes document plans SHA-256 as the default hash and main as the default branch name for new repositories.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A team saves a full copy of a 2 MB folder for each of 15 versions instead of using Git. How many MB do the copies use?', '30', 'Copies times size.',
       ['Each copy is the full folder: 2 MB.', 'There are 15 copies.', eq('15 × 2 = 30 MB')], check=30)
K.calc('e', 'Git checks system, global and local config. A key is set only in system and global. Which level wins? Answer 1 for system, 2 for global, 3 for local.', '2', 'Last one read wins.',
       ['Order: system (1), global (2), local (3).', 'Local is not set, so it is skipped.', eq('global wins, answer 2')], check=2)
K.calc('m', 'A project has 10 files. Each commit changes exactly one file. After 5 commits (including the first, which adds all 10), how many file versions (blobs) does Git store, if every change creates new content?', '14', 'First commit stores 10, each later commit adds one.',
       ['Commit 1 stores all 10 files: 10 blobs.', 'Commits 2 to 5 each add one changed file: 4 blobs.', eq('10 + 4 = 14 blobs, not 50')], check=14)
K.calc('m', 'A SHA-1 id is 40 hex digits. How many bits is that?', '160', 'Each hex digit is 4 bits.',
       ['One hex digit holds 4 bits.', '40 digits.', eq('40 × 4 = 160 bits')], check=160)
K.calc('m', 'A SHA-256 id has 256 bits. How many hex digits does it take to write it?', '64', 'Divide by 4.',
       ['Each hex digit is 4 bits.', '256 bits in total.', eq('256 ÷ 4 = 64 digits')], check=64)
K.calc('h', 'Git shows a 7 digit short id by default. How many different values can 7 hex digits take? Give the exact number.', '268435456', '16 to the power 7.',
       ['Each hex digit has 16 values.', 'Seven digits.', eq('16⁷ = 2²⁸ = 268,435,456')], check=16 ** 7)
K.calc('h', 'With a centralised system, a team of 6 cannot commit while the server is down for 3 hours. How many developer hours of committing are blocked? (With Git the answer would be 0.)', '18', 'People times hours.',
       ['6 developers.', '3 hours each.', eq('6 × 3 = 18 developer hours')], check=18)

# ---------------------------------------------------------------- assignments
K.assign('cfg', 'e', 'Work out the effective git config',
         '<p>Write <code>effective(levels)</code>. <code>levels</code> is a list of dictionaries in the order Git reads them (system, global, local). Return one dictionary where a later level overrides an earlier one.</p>',
         '''
def effective(levels):
    # your code here
    pass
''', [("effective([{'core.editor': 'vi'}, {'user.email': 'a@home'}, {'user.email': 'a@work'}])", {'core.editor': 'vi', 'user.email': 'a@work'}),
      ("effective([{}, {'user.name': 'Asha'}, {}])", {'user.name': 'Asha'}),
      ("effective([{'x': '1'}, {'x': '2'}, {'x': '3'}])", {'x': '3'})],
         '''
def effective(levels):
    out = {}
    for level in levels:
        out.update(level)
    return out
''', 'Start with an empty dictionary and update it with each level in order.', '<p>This is exactly what git config does when it reads /etc/gitconfig, ~/.gitconfig and .git/config.</p>')
K.assign('snap', 'm', 'Count stored file versions',
         '<p>Each commit is a dictionary from file name to content. Write <code>stored(commits)</code> that returns how many different (file name, content) pairs Git would need to store as blobs. Unchanged files are not stored again.</p>',
         '''
def stored(commits):
    # your code here
    pass
''', [("stored([{'a': '1', 'b': '1'}, {'a': '2', 'b': '1'}])", 3), ("stored([{'a': 'x'}, {'a': 'x'}, {'a': 'x'}])", 1),
      ("stored([{'a': '1', 'b': '2'}, {'a': '2', 'b': '1'}])", 4)],
         '''
def stored(commits):
    seen = set()
    for snap in commits:
        for name, content in snap.items():
            seen.add((name, content))
    return len(seen)
''', 'Use a set of (name, content) pairs.', '<p>Real Git stores blobs by content alone, so two files with identical content share one blob. Here the name is kept in the pair to keep the idea simple.</p>')

K.must('Version control', 'Records every version of your files with author, time and message, so you can compare, restore and work in parallel.')
K.must('Distributed', 'Every Git clone has the full history. Commit, log and diff work offline. Centralised tools need the server.')
K.must('Snapshots', 'A commit is a snapshot of the whole project. Unchanged files are reused, not stored again.')
K.must('Config levels', 'system, global (~/.gitconfig), local (.git/config). Later wins. Set user.name, user.email and init.defaultBranch first.')
K.must('Git is not GitHub', 'Git is the tool. GitHub, GitLab and Bitbucket host repositories and add pull requests, reviews and CI/CD.')

T = K.topic(
    slug='what-is-git', topic='what-is-git', step=(1, 'Getting started with Git', 'git-start', 'What version control is, how Git thinks, the three areas of a repository, and how to read history and differences.', 'Beginner'),
    title='What Git is and how to set it up', short='What Git is', badge='1.1', minutes=35, added='2026-11-02',
    lead='Understand why version control exists, how Git differs from older tools, and set Git up on your computer with your name, email and default branch.',
    desc='Version control explained simply, local, centralised and distributed systems, the story of Git, snapshots instead of differences, installing Git, git config levels and your first repository.',
    summary='Why version control exists, centralised versus distributed, snapshots, installing Git, git config levels and a first repository.',
    keywords=['what is git', 'version control', 'distributed', 'centralised', 'snapshots', 'git config', 'install git', 'git init'],
    recap='<p>Git keeps the full history of a folder as snapshots on your own computer. Set your name, email and default branch once with git config, then git init, add and commit.</p>')
