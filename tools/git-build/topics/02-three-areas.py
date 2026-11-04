# Chapter 1.2: the working tree, the staging area (index) and the repository, file states, add, commit, status,
# good commit messages. Sources: Pro Git 1.3 and 2.2, git-status (short format XY codes), git-add, git-commit manuals.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from gitkit import sh, flow

K = Kit()

K.lesson('areas', 'The three areas of a Git project', f'''
<p>Picture a photo studio. The <b>stage</b> is where you place the people who should be in the next photo. The <b>camera</b> takes the photo and puts it in the <b>album</b>. People can walk around the studio without being in the photo.</p>
{table(['Area', 'Also called', 'What it holds', 'Studio picture'], [
    ['Working tree', 'working directory', 'The files you see and edit in your folder', 'the studio floor'],
    ['Staging area', 'the index', 'The exact snapshot your next commit will save', 'the stage'],
    ['Repository', '.git directory, HEAD', 'Every commit ever made', 'the album']])}
{flow(('edit', 'change files in the working tree'), ('git add', 'copy the change to the staging area'), ('git commit', 'save the staging area as a new commit'), ('git push', 'send commits to a remote, covered in step 4'))}
{viz('areas')}
<p>Why have a staging area at all? Because you often change several things at once. Staging lets you commit the bug fix now and the half done feature later, as two clean commits instead of one messy one.</p>
{note('git commit saves what is staged, not what is in your file. If you edit a file after git add, the newer edit is not in the commit until you add it again.', 'warn')}
''', kw=['working tree', 'staging area', 'index', 'repository', 'HEAD', 'three areas', 'git add', 'git commit'])

K.lesson('states', 'File states and git status', f'''
<p>Every file in your folder is either <b>tracked</b> (Git knows it from the last snapshot or the index) or <b>untracked</b> (new, Git has never seen it). Tracked files are unmodified, modified or staged.</p>
{table(['State', 'Meaning', 'How it gets there', 'Short code'], [
    ['Untracked', 'New file Git is not watching', 'You create it', '<code>??</code>'],
    ['Unmodified', 'Same as the last commit', 'After a commit or checkout', '(not listed)'],
    ['Modified', 'Changed, not staged', 'You edit a tracked file', '<code> M</code>'],
    ['Staged', 'Change is in the index', 'git add', '<code>M </code> or <code>A </code>'],
    ['Staged and modified again', 'Index has one version, the folder a newer one', 'edit after git add', '<code>MM</code>']])}
{fxs(
    fx('Short status', '<code>git status -s</code>  →  <code>XY path</code>', 'X compares the index with HEAD (what is staged). Y compares the working tree with the index (what is not staged yet). ?? means untracked.', key=True),
    fx('Long status', '<code>git status</code>', 'Lists staged changes, unstaged changes and untracked files, with the command to undo each.'))}
{sh('Read the short status', """git status -s""", """ M README.md
MM app.py
 D old.txt
A  new.py
?? notes.txt""")}
{steps('Read each line', ['README.md has a space then M: changed in the folder, nothing staged.', 'app.py has MM: one change staged, and another change made after that.', 'old.txt has D in the second column: deleted from the folder but not staged.', 'new.py has A: a new file added to the index.', eq('notes.txt has ??: untracked, git add notes.txt to start tracking it')])}
''', kw=['git status', 'status -s', 'untracked', 'modified', 'staged', 'XY codes', 'porcelain'])

K.lesson('commit', 'Adding and committing well', f'''
{fxs(
    fx('Stage', '<code>git add &lt;file&gt;</code>, <code>git add .</code>, <code>git add -p</code>', 'git add . stages everything under the current folder. -p asks about each changed piece (hunk) so you can stage part of a file.', key=True),
    fx('Commit', '<code>git commit -m "message"</code>', 'Saves the staging area. Without -m Git opens your editor for a longer message.', key=True),
    fx('Stage tracked files and commit', '<code>git commit -am "message"</code>', '-a stages every change to tracked files first. New untracked files are not included.'),
    fx('Remove and rename', '<code>git rm &lt;file&gt;</code>, <code>git mv &lt;old&gt; &lt;new&gt;</code>', 'Changes the folder and stages the change in one step. git rm --cached keeps the file on disk but stops tracking it.'))}
{sh('Two clean commits from one messy afternoon', """git status -s
git add src/login.py
git commit -m "Fix crash when the password is empty"
git add -p src/search.py
git commit -m "Add search by price"
git status -s""", """ M src/login.py
 M src/search.py
[main 4e1d2aa] Fix crash when the password is empty
 1 file changed, 2 insertions(+)
[main 9b07c31] Add search by price
 1 file changed, 14 insertions(+)
 M src/search.py""")}
<h3>A good commit message</h3>
{table(['Rule', 'Good', 'Bad'], [
    ['Short summary line, about 50 characters', 'Fix crash when the password is empty', 'fixed stuff'],
    ['Imperative mood, as if giving an order', 'Add search by price', 'Added search, adding search'],
    ['Blank line, then the why in the body', 'Users saw a 500 error on empty input...', '(nothing)'],
    ['One logical change per commit', 'One bug fix', 'Bug fix plus renaming plus new feature']])}
{note('Conventional Commits is a popular format: feat: add search by price, fix: handle empty password, docs: update README. Tools read it to make changelogs and choose the next version number.', 'tip')}
{scene('the 2 a.m. bug hunt', '<p>A shop site breaks at night. The on call developer runs git log and sees "Fix rounding of discount prices" from yesterday. One command, git show, displays the exact lines. Twenty minutes later the cause is found. With a message like "update" and a commit that touched forty files, the same search takes hours.</p>')}
''', kw=['git add -p', 'git commit -m', 'commit -am', 'git rm', 'git mv', 'commit message', 'conventional commits', 'atomic commit'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Your folder is your desk. The staging area is a tray where you put the pages you want to send. A commit is putting the tray in an envelope with a note and filing it forever.</p>',
    '<p>The index is a binary file, .git/index, that lists every tracked path with its blob id, mode and file metadata. git add writes blobs and updates the index. git commit turns the index into tree objects and makes a commit that points to the top tree and to its parent.</p>',
    '<p>Because the index caches file size and modification time, git status can skip hashing unchanged files, which keeps it fast on large repositories. During a merge the index can hold up to three versions of a path (stages 1, 2 and 3 for base, ours and theirs), which is how Git tracks a conflict.</p>',
    '<p>Studies of commit history show that tangled commits, which mix unrelated changes, hurt tools that find the commit that caused a bug and tools that predict defects. Research tools try to untangle such commits automatically, which is one reason the habit of small commits matters beyond style.</p>')}
{deep('git add -p in practice', '<p>Git shows one hunk at a time and asks Stage this hunk [y,n,q,a,d,s,e,?]. y stages it, n skips it, s splits it into smaller hunks, e lets you edit the hunk by hand, q quits. Afterwards git diff --staged shows what is staged and git diff what is left.</p>')}
''', kw=['index file', 'stages 1 2 3', 'tangled commits', 'git add -p'])

K.quiz('e', 'Which area holds the snapshot your next commit will save?', ['Working tree', 'Staging area (index)', 'Remote', 'The reflog'], 1, 'The stage.', 'git commit turns the staging area into a commit.')
K.quiz('e', 'git status -s shows ?? before a file. What does that mean?', ['Conflict', 'Untracked', 'Deleted', 'Staged'], 1, 'Never added.', '?? means Git has never tracked this file.')
K.quiz('e', 'Which command stages every change under the current folder?', ['git commit .', 'git add .', 'git stage --all-files', 'git push .'], 1, 'Dot means here.', 'git add . stages new, changed and deleted files under the current folder.')
K.quiz('m', 'You add app.py, then edit it again and commit without adding. What is in the commit?', ['The newest edit', 'The version you added', 'Nothing', 'Both versions'], 1, 'Commit saves the index.', 'The second edit stays in the working tree, shown as MM before the commit.')
K.quiz('m', 'What does MM mean in git status -s?', ['Merged twice', 'Staged change plus a newer unstaged change', 'Moved file', 'Merge conflict'], 1, 'Two columns.', 'X = M (index differs from HEAD) and Y = M (folder differs from index).')
K.quiz('m', 'git commit -am "msg" includes', ['All files including new ones', 'Changes to already tracked files only', 'Only staged files', 'Nothing'], 1, '-a and new files.', 'New untracked files still need git add.')
K.quiz('m', 'Which commit message follows the usual advice best?', ['changes', 'Fixed the bug.', 'Fix crash when the password is empty', 'FIX!!!'], 2, 'Imperative, specific.', 'Short, imperative, says what changed.')
K.quiz('h', 'You want to commit only half of the changes in one file. Use', ['git add -p', 'git commit --half', 'git split', 'git add -u'], 0, 'Patch mode.', 'git add -p asks hunk by hunk.')
K.quiz('h', 'git rm --cached secrets.env does what?', ['Deletes the file from disk', 'Stops tracking it but keeps it on disk', 'Encrypts it', 'Removes it from all old commits'], 1, 'Cached means the index.', 'It removes the path from the index only. Old commits still contain it.')
K.quiz('x', 'During a merge conflict, how many versions of one path can the index hold?', ['1', '2', '3', '4'], 2, 'Base, ours, theirs.', 'Stages 1, 2 and 3 hold base, ours and theirs until you resolve and git add.')

K.calc('e', 'git status -s prints 3 lines starting with ??, 2 with space M and 1 with M space. How many files have unstaged changes to tracked files?', '2', 'Second column M.',
       ['?? lines are untracked, not tracked changes.', '" M" means modified, not staged: 2 files.', eq('Answer 2')], check=2)
K.calc('e', 'You change 4 files and run git add on 3 of them, then commit. How many files are in that commit as changed?', '3', 'Only staged files.',
       ['The commit saves the index.', '3 files were staged.', eq('3 files changed in the commit')], check=3)
K.calc('m', 'HEAD has a.py v1, the index has a.py v2, the folder has a.py v2. What are the two status letters? Type them with no space for a blank, answer as the count of letters that are M.', '1', 'X compares index with HEAD, Y folder with index.',
       ['X: index v2 vs HEAD v1, different: M.', 'Y: folder v2 vs index v2, same: blank.', eq('Code "M " has 1 M')], check=1)
K.calc('m', 'A summary line should stay near 50 characters. "Fix rounding of discount prices on the checkout page" has how many characters?', '52', 'Count letters and spaces.',
       ['Count each word plus the spaces between words.', 'Fix(3) rounding(8) of(2) discount(8) prices(6) on(2) the(3) checkout(8) page(4) = 44 letters.', eq('44 letters + 8 spaces = 52 characters')], check=len('Fix rounding of discount prices on the checkout page'))
K.calc('h', 'You stage 2 hunks out of 5 in a file with git add -p and commit. How many hunks still show in git diff?', '3', 'The rest stay unstaged.',
       ['5 hunks changed.', '2 went into the commit.', eq('5 − 2 = 3 hunks left in git diff')], check=3)
K.calc('h', 'A day of work: 1 bug fix, 1 refactor, 1 feature, each touching different files. With one commit per logical change, how many commits?', '3', 'One per logical change.',
       ['Bug fix: 1.', 'Refactor: 1.', eq('Feature: 1, total 3')], check=3)

K.must('Three areas', 'Working tree (your files), staging area or index (next snapshot), repository (all commits). add moves changes to the index, commit saves the index.')
K.must('Status codes', 'git status -s prints XY: X staged (index vs HEAD), Y unstaged (folder vs index). ?? untracked, MM staged and changed again.')
K.must('Commit saves the index', 'Edits made after git add are not in the commit until you add again. commit -a stages tracked files only.')
K.must('Partial staging', 'git add -p stages hunk by hunk so one file can feed two clean commits.')
K.must('Good messages', 'Short imperative summary near 50 characters, blank line, then why. One logical change per commit.')

T = K.topic(
    slug='three-areas', topic='three-areas', step=(1, 'Getting started with Git', 'git-start', 'What version control is, how Git thinks, the three areas of a repository, and how to read history and differences.', 'Beginner'),
    title='The three areas: working tree, staging area and repository', short='Three areas', badge='1.2', minutes=40, added='2026-11-02',
    lead='See how a change travels from your folder to the staging area to a commit, read every git status code, and write commits a teammate can understand.',
    desc='The working tree, the index and the repository, file states, git status long and short format, git add and add -p, git commit and commit -a, git rm and mv, and good commit messages.',
    summary='Working tree, staging area and repository, file states and status codes, add, add -p, commit and good commit messages.',
    keywords=['staging area', 'index', 'working tree', 'git status', 'git add', 'git commit', 'commit message', 'untracked'],
    recap='<p>A change goes from your folder to the index with git add and into history with git commit. git status -s tells you exactly where every file stands.</p>')
