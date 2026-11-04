# Chapter 3.1: undoing things. restore, restore --staged, commit --amend, reset --soft, --mixed and --hard, revert,
# the reflog and recovering lost commits, which undo to use when. Sources: Pro Git 2.4 and 7.7 (Reset Demystified),
# git-restore, git-reset, git-revert and git-reflog manuals (reflog entries for unreachable commits expire after
# 30 days and reachable ones after 90 days by default, gc.reflogExpireUnreachable and gc.reflogExpire).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from gitkit import sh, flow

K = Kit()

K.lesson('levels3', 'Undo at each of the three levels', f'''
<p>Every undo answers one question: <b>where is the thing I want to undo?</b> In your files, in the staging area, or already in a commit? And has that commit been shared?</p>
{table(['What you want to undo', 'Command', 'Safe?'], [
    ['Edits in a file you have not staged', '<code>git restore app.py</code>', 'The edits are gone for good'],
    ['A file you staged by mistake', '<code>git restore --staged app.py</code>', 'Yes, the edits stay in the file'],
    ['The message or content of your last commit (not pushed)', '<code>git commit --amend</code>', 'Yes, rewrites one local commit'],
    ['Your last commits (not pushed)', '<code>git reset &lt;commit&gt;</code>', 'Yes with --soft or --mixed, careful with --hard'],
    ['A commit already pushed and shared', '<code>git revert &lt;commit&gt;</code>', 'Yes, adds a new commit, rewrites nothing'],
    ['Something you reset or deleted by mistake', '<code>git reflog</code> then reset or branch', 'Usually rescues it']])}
{viz('areas', cmds='edit README.md\ngit add README.md\ngit restore --staged README.md\ngit restore README.md')}
{note('git restore app.py without --staged overwrites your file from the index. Uncommitted edits it removes are not in any commit, so the reflog cannot bring them back.', 'warn')}
''', kw=['undo', 'git restore', 'restore --staged', 'unstage', 'discard changes'])

K.lesson('reset', 'git reset: soft, mixed and hard', f'''
<p><code>git reset &lt;commit&gt;</code> moves the current branch (and HEAD with it) to another commit. The mode says how much else follows:</p>
{table(['Mode', 'Moves the branch', 'Resets the index', 'Resets your files', 'Use it to'], [
    ['--soft', 'yes', 'no', 'no', 'redo the last commits as one: changes stay staged'],
    ['--mixed (default)', 'yes', 'yes', 'no', 'unstage and recommit differently: changes stay in your files'],
    ['--hard', 'yes', 'yes', 'yes', 'throw everything away and match the commit exactly']])}
{viz('areas', cmds='edit app.py\ngit commit -am "one"\nedit app.py\ngit commit -am "two"\ngit reset --soft HEAD~1')}
{fxs(
    fx('Undo the last commit, keep the work staged', '<code>git reset --soft HEAD~1</code>', 'Then git commit again, for example to combine two commits.', key=True),
    fx('Undo the last commit, keep the work unstaged', '<code>git reset HEAD~1</code>', 'Same as --mixed.'),
    fx('Discard all local work', '<code>git reset --hard HEAD</code>', 'Tracked files go back to the last commit. Untracked files stay. Uncommitted edits are lost.', key=True),
    fx('Fix the last commit', '<code>git commit --amend</code>', 'Replaces the last commit with a new one: new message and anything newly staged.'))}
{note('git reset --hard with uncommitted changes is the most common way people lose work in Git. Run git status and git stash first if in doubt.', 'warn')}
''', kw=['git reset', 'reset --soft', 'reset --mixed', 'reset --hard', 'HEAD~1', 'commit --amend', 'undo last commit'])

K.lesson('revert', 'git revert: undo in public', f'''
<p>On a shared branch you cannot remove a commit without rewriting history. <code>git revert</code> instead makes a <b>new</b> commit that does the opposite of the old one. History stays true: it shows the mistake and its undo.</p>
{viz('gitsim', cmds='git commit -m "good"\ngit commit -m "bad"\ngit commit -m "more work"\ngit revert HEAD~1', show='log')}
{fxs(fx('Undo a pushed commit', '<code>git revert &lt;commit&gt;</code>', 'Creates "Revert ..." as a new commit. --no-edit keeps the default message.', key=True),
     fx('Undo a merge commit', '<code>git revert -m 1 &lt;merge&gt;</code>', '-m 1 says parent 1 (the main line) is the side to keep.'))}
{scene('Friday deploy rollback', '<p>A release goes out and checkout payments fail. The team does not reset main, because twenty people have pulled it and CI deployed from it. They run git revert on the bad merge commit, push, and the pipeline deploys the reverted code. On Monday they fix the bug properly and, because the revert is a normal commit, they can even revert the revert to bring the feature back.</p>')}
''', kw=['git revert', 'revert merge', 'revert -m 1', 'rollback', 'shared history'])

K.lesson('reflog', 'The reflog: your safety net', f'''
<p>Every time HEAD moves (commit, reset, switch, rebase, merge, pull) Git writes a line in the <b>reflog</b>. It is local to your clone and is not pushed. It lets you find commits that no branch points to any more.</p>
{sh('Rescue after a bad hard reset', """git reset --hard HEAD~2
# oh no, those two commits were needed
git reflog
git reset --hard HEAD@{1}""", """HEAD is now at 51de0f4 Fix typo
51de0f4 HEAD@{0}: reset: moving to HEAD~2
a41f0c2 HEAD@{1}: commit: Add search by price
7c9e1d0 HEAD@{2}: commit: Add search box
51de0f4 HEAD@{3}: commit: Fix typo
HEAD is now at a41f0c2 Add search by price""")}
{viz('gitsim', cmds='git commit -m "good"\ngit commit -m "needed"\ngit reset --hard HEAD~1\ngit reset --hard HEAD@{1}', show='both')}
{deep('How long does the reflog keep things?', '<p>By default reflog entries for commits that are no longer reachable from any branch expire after 30 days (gc.reflogExpireUnreachable) and other entries after 90 days (gc.reflogExpire). git gc then may delete the unreachable commits. Uncommitted work was never in any commit, so it was never in the reflog either. git fsck --lost-found can sometimes find blobs you once staged with git add.</p>')}
{ladder(
    '<p>restore is an eraser for your page, reset is moving your bookmark back, revert is writing a new page that says "ignore what page 7 said", and the reflog is a diary of every place your bookmark has been.</p>',
    '<p>reset moves the branch ref and optionally the index and working tree. revert creates an inverse commit. restore copies a file from the index or a commit. The reflog records old values of HEAD and of each branch.</p>',
    '<p>reset with a path (git reset -- file) does not move HEAD: it copies that file\'s entry from a commit into the index, the opposite of git add. Pro Git calls the three trees HEAD, index and working directory, and every undo command is a copy between them.</p>',
    '<p>Version control research treats history as an append mostly log. Systems that forbid rewriting (for example some audit or regulated environments) rely on revert only, while Git allows rewriting locally and leaves policy to the server, where protected branches block force pushes.</p>')}
''', kw=['reflog', 'HEAD@{1}', 'recover lost commit', 'gc.reflogExpire', 'fsck lost-found', 'three trees'])

K.quiz('e', 'You staged a file by mistake. Which command unstages it but keeps your edits?', ['git restore --staged file', 'git restore file', 'git reset --hard', 'git rm file'], 0, 'Staged.', '--staged copies HEAD back into the index only.')
K.quiz('e', 'Which undo is safe on a branch others have pulled?', ['git reset --hard', 'git revert', 'git rebase -i', 'git commit --amend'], 1, 'Adds a commit.', 'revert does not rewrite history.')
K.quiz('e', 'What does git commit --amend do?', ['Adds a new commit', 'Replaces the last commit with a corrected one', 'Deletes the last commit', 'Pushes'], 1, 'Fix the last one.', 'It makes a new commit that replaces the previous tip.')
K.quiz('m', 'git reset --soft HEAD~1 leaves the changes of the undone commit', ['Deleted', 'Staged', 'Unstaged', 'Stashed'], 1, 'Soft touches only HEAD.', 'The index still has them.')
K.quiz('m', 'git reset HEAD~1 (no mode) is the same as', ['--soft', '--mixed', '--hard', '--keep'], 1, 'Default.', 'Mixed resets the index but not your files.')
K.quiz('m', 'After git reset --hard HEAD~2 you want the commits back. Use', ['git revert', 'git reflog then git reset --hard HEAD@{1}', 'git pull', 'They are gone'], 1, 'Diary of HEAD.', 'The reflog remembers where HEAD was.')
K.quiz('m', 'Which of these can the reflog NOT recover?', ['A commit removed by reset --hard', 'Uncommitted edits removed by reset --hard', 'A deleted branch', 'Commits replaced by rebase'], 1, 'Never committed.', 'The reflog only knows commits.')
K.quiz('h', 'You need to revert a merge commit and keep main\'s side. Which flag?', ['-m 1', '-m 2', '--hard', '--no-ff'], 0, 'Mainline parent.', '-m 1 names the first parent as the line to keep.')
K.quiz('h', 'Is the reflog shared when you push?', ['Yes', 'No, it is local to each clone', 'Only for main', 'Only with --mirror'], 1, 'Local diary.', 'Each repository keeps its own reflog.')
K.quiz('x', 'git reset -- app.py (a path, no commit) does what?', ['Moves HEAD back', 'Copies app.py from HEAD into the index, the opposite of git add', 'Deletes app.py', 'Reverts app.py'], 1, 'Path form.', 'With a path, reset only updates the index entry.')

K.calc('e', 'Your branch is at C5. You run git reset --hard HEAD~2. Which commit number is HEAD at?', '3', 'Two back.',
       ['HEAD~1 = C4.', 'HEAD~2 = C3.', eq('HEAD at C3')], check=3)
K.calc('e', 'You revert 3 bad commits one by one. How many new commits appear?', '3', 'One per revert.',
       ['Each git revert makes one inverse commit.', '3 reverts.', eq('3 new commits')], check=3)
K.calc('m', 'Reflog (newest first): HEAD@{0} reset, HEAD@{1} commit C7, HEAD@{2} commit C6. To get back C7, which n do you use in HEAD@{n}?', '1', 'Where HEAD was before the reset.',
       ['HEAD@{0} is now.', 'HEAD@{1} is one move ago, C7.', eq('n = 1')], check=1)
K.calc('m', 'Default expiry: unreachable reflog entries after 30 days, others after 90. You reset away a commit 45 days ago. Is it still in the reflog? Answer 1 for yes, 0 for no.', '0', 'Unreachable since the reset.',
       ['After the reset no branch reaches the commit.', 'Unreachable entries expire after 30 days.', eq('45 > 30, so 0 (likely gone after git gc)')], check=0)
K.calc('h', 'You amend the last commit 3 times. How many commit objects exist for that one change, counting the original?', '4', 'Each amend makes a new one.',
       ['Original: 1.', 'Each amend creates a new commit: 3.', eq('1 + 3 = 4 objects, 3 of them unreachable')], check=4)
K.calc('h', 'Out of soft, mixed and hard, how many reset modes change your working tree files?', '1', 'Only one touches files.',
       ['soft: only HEAD.', 'mixed: HEAD and index.', eq('hard: also files, so 1')], check=1)

K.must('Where is it', 'Unstaged edit: git restore file. Staged: git restore --staged file. Local commit: reset or amend. Shared commit: revert.')
K.must('Reset modes', '--soft moves the branch only. --mixed (default) also resets the index. --hard also resets your files.')
K.must('Revert', 'Makes a new inverse commit. Safe on shared branches. Merge commits need -m 1.')
K.must('Reflog', 'Local diary of HEAD. git reflog, then git reset --hard HEAD@{n} or git branch rescue <id>. Unreachable entries expire after 30 days by default.')
K.must('Danger', 'reset --hard and restore throw away uncommitted edits, which no command can bring back.')

T = K.topic(
    slug='undo', topic='undo', step=(3, 'Undo, stash, tags and ignore rules', 'git-undo', 'Undo safely at every level, rescue lost commits, park work in the stash, mark releases with tags and keep junk out with .gitignore.', 'Intermediate'),
    title='Undoing things: restore, reset, revert and the reflog', short='Undo', badge='3.1', minutes=45, added='2026-11-02',
    lead='Pick the right undo for every situation, understand the three kinds of reset, revert in public, and rescue commits with the reflog.',
    desc='git restore and restore --staged, commit --amend, reset soft, mixed and hard, revert including merge commits, the reflog and its expiry, and the three trees model.',
    summary='restore, amend, the three reset modes, revert, reflog rescue and when each undo is safe.',
    keywords=['git reset', 'git revert', 'git restore', 'reflog', 'amend', 'undo commit', 'reset hard', 'recover'],
    recap='<p>Ask where the change is and whether it is shared. restore for files, reset for local commits, revert for shared ones, and the reflog when something seems lost.</p>')
