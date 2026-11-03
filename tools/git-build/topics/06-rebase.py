# Chapter 2.3: rebase, interactive rebase, --onto, autosquash, the golden rule, cherry-pick, merge versus rebase.
# Sources: Pro Git 3.6 and 7.6, git-rebase and git-cherry-pick manuals (--update-refs since Git 2.38).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow

K = Kit()

K.code('replay', r'''
# Rebase = replay your commits, one by one, on top of a new base. Copies get new ids.
main = ["C0", "C1", "C4"]            # main moved on with C4
feature = ["C0", "C1", "C2", "C3"]   # feature started at C1
base = "C1"
mine = feature[feature.index(base) + 1:]
print("commits to replay:", mine)
new_feature = list(main)
for c in mine:
    copy = c + "'"                   # same change, new parent, so a new id
    new_feature.append(copy)
    print("replayed", c, "as", copy, "on top of", new_feature[-2])
print("feature is now:", new_feature)
print("old", mine, "are left behind (only the reflog knows them)")
''')

K.code('todo', r'''
# What an interactive rebase todo list does to a list of commits
commits = [("a1", "Add search box"), ("b2", "WIP"), ("c3", "fix typo in search"), ("d4", "Add search by price")]
todo = [("pick", "a1"), ("fixup", "c3"), ("drop", "b2"), ("reword", "d4")]
msgs = dict(commits)
result = []
for action, cid in todo:
    if action == "pick":
        result.append(msgs[cid])
    elif action in ("fixup", "squash"):
        result[-1] = result[-1] + (" + " + msgs[cid] if action == "squash" else "")
    elif action == "reword":
        result.append(msgs[cid] + " (message edited)")
    elif action == "drop":
        pass
for i, m in enumerate(result, 1):
    print(i, m)
''')

K.lesson('rebase', 'Rebase: move your work onto a new base', f'''
<p>You started a feature from main on Monday. By Wednesday main has new commits. Merging would add a merge commit. <b>Rebasing</b> instead takes your commits, sets them aside, moves your branch to the new tip of main, and replays your commits there one by one. History becomes one straight line, as if you had started today.</p>
{viz('gitsim', cmds='git switch -c feature\ngit commit -m "add button"\ngit commit -m "style button"\ngit switch main\ngit commit -m "fix typo"\ngit switch feature\ngit rebase main\ngit switch main\ngit merge feature')}
{code('replay')}
{fxs(
    fx('Rebase the current branch', '<code>git rebase &lt;upstream&gt;</code>', 'Replays the commits of HEAD that are not in upstream on top of upstream.', key=True),
    fx('Continue, skip or stop', '<code>git rebase --continue</code>, <code>--skip</code>, <code>--abort</code>', 'After fixing a conflict: git add, then --continue. --abort returns to before the rebase.', key=True),
    fx('Move a range somewhere else', '<code>git rebase --onto &lt;newbase&gt; &lt;oldbase&gt; [&lt;branch&gt;]</code>', 'Takes the commits after oldbase and replays them on newbase.'),
    fx('Update stacked branches too', '<code>git rebase --update-refs</code>', 'Also moves other branches that point at commits being rewritten (Git 2.38 and later).'))}
{note('Rebased commits are copies with new ids, because their parent changed. Anyone who had the old ones now has commits that no longer exist on the branch.', 'warn')}
''', kw=['git rebase', 'rebase main', 'replay commits', 'linear history', 'rebase --continue', 'rebase --abort', 'rebase --onto', 'update-refs'])

K.lesson('golden', 'The golden rule, and merge versus rebase', f'''
<p><b>Do not rebase commits that exist outside your repository and that people may have based work on.</b> Rebasing your own local branch before you share it is fine. Rebasing main after the team pulled it forces everyone to untangle duplicate commits.</p>
{table(['', 'Merge', 'Rebase'], [
    ['History', 'True record, with merge commits', 'Clean straight line, rewritten'],
    ['Commit ids', 'Unchanged', 'New ids for replayed commits'],
    ['Safe on shared branches', 'Yes', 'No, only on your own branch'],
    ['Conflicts', 'Solved once, in the merge commit', 'May be solved once per replayed commit'],
    ['Good for', 'Bringing a finished feature into main', 'Updating your feature branch with main before review']])}
{sh('A common, safe habit', """git switch feature/search
git fetch origin
git rebase origin/main
# fix conflicts if any, run the tests
git push --force-with-lease""")}
{note('After rebasing a branch you already pushed, a normal push is rejected. Use --force-with-lease, never plain --force, and only on a branch that is yours. Chapter 4.1 explains why.', 'warn')}
{scene('the pull request that went stale', '<p>A reviewer asks Ravi to update his pull request because main moved. He rebases onto origin/main, reruns the tests locally, and force pushes with lease. The pull request shows his three commits neatly on top of the latest main, and the CI checks run again on code that matches what will be merged.</p>')}
''', kw=['golden rule of rebasing', 'merge vs rebase', 'force-with-lease', 'shared branch', 'rewrite history'])

K.lesson('interactive', 'Interactive rebase: tidy your commits before review', f'''
<p><code>git rebase -i HEAD~4</code> opens a list of your last four commits, oldest at the top. You change the word in front of each line and save.</p>
{sh('The todo list Git opens', """pick a1b2c3d Add search box
pick b2c3d4e WIP
pick c3d4e5f fix typo in search
pick d4e5f6a Add search by price""")}
{table(['Command', 'Effect'], [
    ['pick', 'keep the commit as it is'],
    ['reword', 'keep the change, edit the message'],
    ['edit', 'stop after this commit so you can amend it or split it'],
    ['squash', 'meld into the previous commit and combine the messages'],
    ['fixup', 'meld into the previous commit and throw this message away'],
    ['drop', 'remove the commit'],
    ['(change the order of lines)', 'reorder the commits']])}
{code('todo')}
{fxs(fx('Prepare a fixup now, squash later', '<code>git commit --fixup=&lt;commit&gt;</code> then <code>git rebase -i --autosquash &lt;base&gt;</code>', 'The fixup! commit is moved next to its target and marked fixup automatically.', key=True))}
{note('Interactive rebase rewrites history. Use it on commits that only you have, usually right before opening or updating a pull request.', 'tip')}
''', kw=['interactive rebase', 'rebase -i', 'pick', 'reword', 'edit', 'squash', 'fixup', 'drop', 'autosquash', 'commit --fixup'])

K.lesson('cherry', 'Cherry-pick: copy one commit', f'''
<p><code>git cherry-pick &lt;commit&gt;</code> applies the change of one commit on top of your current branch as a new commit. It is how a bug fix made on main reaches an older release branch without bringing everything else along.</p>
{viz('gitsim', cmds='git switch -c release/1.0\ngit switch main\ngit commit -m "new feature"\ngit commit -m "fix crash"\ngit switch release/1.0\ngit cherry-pick main\ngit tag v1.0.1')}
{fxs(fx('Copy commits', '<code>git cherry-pick &lt;commit&gt;...</code>, <code>git cherry-pick A..B</code>', 'Each picked commit becomes a new commit with a new id. -x adds "(cherry picked from commit ...)" to the message.', key=True),
     fx('Undo a commit by adding its opposite', '<code>git revert &lt;commit&gt;</code>', 'Covered in chapter 3.1. Safe on shared branches because nothing is rewritten.'))}
{ladder(
    '<p>Rebase is like copying your homework neatly onto a fresh page after the teacher changed the first page. Cherry-pick is copying one good paragraph into another notebook.</p>',
    '<p>Rebase and cherry-pick both apply the diff of a commit to a new parent, creating a new commit. Rebase does it for a range and then moves the branch. Rebase skips commits whose change is already upstream.</p>',
    '<p>Git detects already applied changes by patch id, a hash of the diff ignoring line numbers and whitespace. rebase --onto takes three points: new base, old base (exclusive) and branch. Rebase by default drops merge commits, and --rebase-merges recreates them.</p>',
    '<p>Rewriting public history breaks the assumption that a commit id names a stable history. Tools like git range-diff compare two versions of a patch series, which is how mailing list based projects such as Git itself review rebased series.</p>')}
''', kw=['cherry-pick', 'cherry-pick -x', 'backport', 'release branch', 'patch id', 'rebase-merges', 'range-diff'])

K.quiz('e', 'What does git rebase main do on a feature branch?', ['Deletes main', 'Replays feature\'s own commits on top of main', 'Merges feature into main', 'Pushes'], 1, 'Replay.', 'It moves the base of your work to the tip of main.')
K.quiz('e', 'After a rebase, the replayed commits have', ['The same ids', 'New ids', 'No ids', 'The ids of main'], 1, 'Parent changed.', 'A different parent means a different commit object.')
K.quiz('e', 'Which command stops a rebase with conflicts and goes back?', ['git rebase --abort', 'git rebase --stop', 'git reset', 'git merge --abort'], 0, 'Abort.', 'git rebase --abort restores the branch as it was.')
K.quiz('m', 'The golden rule of rebasing says', ['Always rebase main', 'Do not rebase commits others may have based work on', 'Never rebase', 'Rebase only on Fridays'], 1, 'Shared history.', 'Rebase your own unshared commits only.')
K.quiz('m', 'In git rebase -i, fixup does what?', ['Edits a message', 'Melds the commit into the previous one and drops its message', 'Deletes the commit', 'Splits it'], 1, 'Like squash, quieter.', 'squash keeps both messages for editing, fixup discards this one.')
K.quiz('m', 'You fixed a bug on main and need it on release/1.0 without other new features. Use', ['git merge main', 'git cherry-pick <fix commit>', 'git rebase main', 'git push'], 1, 'One commit.', 'Cherry-pick copies only that change.')
K.quiz('m', 'You rebased a branch you had already pushed. Plain git push says rejected. Best next step?', ['git push --force', 'git push --force-with-lease', 'Delete the remote', 'git pull and push'], 1, 'Safer force.', 'The lease fails if someone else pushed in the meantime.')
K.quiz('h', 'Your feature commits B and C sit on top of an old topic branch you no longer want. Which command moves only B and C onto main?', ['git rebase main', 'git rebase --onto main topic feature', 'git cherry-pick main', 'git merge --onto'], 1, 'Three points.', 'Replay commits after topic, up to feature, onto main.')
K.quiz('h', 'How does rebase notice that one of your commits is already in upstream?', ['By message', 'By patch id, a hash of the change', 'By author', 'It does not'], 1, 'Same change.', 'Commits whose patch id already exists upstream are skipped.')
K.quiz('x', 'Which option makes a rebase also move other branch refs that point into the rewritten range?', ['--keep-base', '--update-refs', '--autostash', '--root'], 1, 'Stacked branches.', '--update-refs (Git 2.38) updates them.')

K.calc('e', 'A feature branch has 4 commits. You rebase it onto main with no skipped commits. How many new commit objects are created?', '4', 'One copy per commit.',
       ['Each commit is replayed once.', 'Each replay makes a new object.', eq('4 new commits')], check=4)
K.calc('e', 'git rebase -i HEAD~5 opens how many lines (commits)?', '5', 'HEAD~5 is the base.',
       ['The base is not included.', 'The 5 commits above it are listed.', eq('5')], check=5)
K.calc('m', 'Todo list: pick, fixup, pick, squash, drop, pick. How many commits remain?', '3', 'Count picks.',
       ['pick 1 stays, fixup melds into it.', 'pick 2 stays, squash melds into it.', 'drop removes one.', eq('pick 3 stays: 3 commits')], check=3)
K.calc('m', 'You rebase 6 commits and every replay hits one conflict. How many times do you run git rebase --continue?', '6', 'Once per stop.',
       ['Rebase stops at each conflicting commit.', 'After fixing and git add, you continue.', eq('6 times')], check=6)
K.calc('h', 'Feature has commits X, Y, Z. Y is already in main as a cherry-pick (same patch). After git rebase main, how many commits are replayed?', '2', 'Same patch is skipped.',
       ['X is new, replayed.', 'Y has the same patch id as a main commit, skipped.', eq('Z replayed. Total 2')], check=2)
K.calc('h', 'You cherry-pick a range A..B where B is 4 commits after A. How many commits are copied?', '4', 'A..B excludes A.',
       ['A..B means after A up to B.', 'That is 4 commits.', eq('4')], check=4)

K.assign('todo', 'm', 'Apply an interactive rebase todo list',
         '<p><code>commits</code> maps ids to messages and <code>todo</code> is a list of (action, id) pairs with actions pick, reword, squash, fixup or drop. Write <code>apply_todo(commits, todo)</code> that returns the list of resulting messages. squash joins with " + ", fixup keeps only the earlier message, reword appends " (edited)".</p>',
         '''
def apply_todo(commits, todo):
    # your code here
    pass
''', [("apply_todo({'a': 'A', 'b': 'B', 'c': 'C'}, [('pick', 'a'), ('squash', 'b'), ('pick', 'c')])", ['A + B', 'C']),
      ("apply_todo({'a': 'A', 'b': 'B', 'c': 'C'}, [('pick', 'a'), ('fixup', 'b'), ('drop', 'c')])", ['A']),
      ("apply_todo({'a': 'A', 'b': 'B'}, [('pick', 'b'), ('reword', 'a')])", ['B', 'A (edited)'])],
         '''
def apply_todo(commits, todo):
    out = []
    for action, cid in todo:
        if action == 'pick':
            out.append(commits[cid])
        elif action == 'reword':
            out.append(commits[cid] + ' (edited)')
        elif action == 'squash':
            out[-1] = out[-1] + ' + ' + commits[cid]
        elif action == 'fixup':
            pass
    return out
''', 'Walk the list in order. squash and fixup change the last result.', '<p>Note that reordering lines reorders commits, as the third test shows.</p>')
K.assign('replay', 'h', 'Which commits does rebase replay?',
         '<p>Write <code>to_replay(parents, order, head, upstream, patch)</code>. Return, oldest first (use <code>order</code>, the creation order), the non merge commits reachable from head but not from upstream, leaving out any whose <code>patch[c]</code> equals the patch of a commit reachable from upstream.</p>',
         '''
def to_replay(parents, order, head, upstream, patch):
    # your code here
    pass
''', [("to_replay({'A': [], 'B': ['A'], 'X': ['A'], 'Y': ['X']}, ['A', 'B', 'X', 'Y'], 'Y', 'B', {'A': 'a', 'B': 'b', 'X': 'x', 'Y': 'y'})", ['X', 'Y']),
      ("to_replay({'A': [], 'B': ['A'], 'X': ['A'], 'Y': ['X']}, ['A', 'B', 'X', 'Y'], 'Y', 'B', {'A': 'a', 'B': 'x', 'X': 'x', 'Y': 'y'})", ['Y'])],
         '''
def anc(parents, c):
    seen, todo = set(), [c]
    while todo:
        x = todo.pop()
        if x not in seen:
            seen.add(x)
            todo.extend(parents[x])
    return seen

def to_replay(parents, order, head, upstream, patch):
    up = anc(parents, upstream)
    up_patches = {patch[c] for c in up}
    mine = anc(parents, head) - up
    return [c for c in order if c in mine and len(parents[c]) < 2 and patch[c] not in up_patches]
''', 'Take the set difference of ancestors, then filter out merges and already applied patches.', '<p>This is close to what git rebase computes before it starts replaying.</p>')

K.must('Rebase', 'Replays your commits on a new base. Copies get new ids. --continue after fixing, --abort to give up.')
K.must('Golden rule', 'Never rebase commits others may have built on. Rebase your own branch, then push --force-with-lease.')
K.must('Merge or rebase', 'Merge keeps true history and is safe on shared branches. Rebase gives a straight line for your own work.')
K.must('Interactive rebase', 'rebase -i: pick, reword, edit, squash, fixup, drop, reorder. commit --fixup plus --autosquash automates it.')
K.must('Cherry-pick', 'Copies one commit as a new commit, for example a fix to a release branch. -x records the source.')

T = K.topic(
    slug='rebase-cherry-pick', topic='rebase', step=(2, 'Branching and merging', 'git-branch', 'Branches as pointers, fast-forward and three way merges, conflicts, rebase, interactive rebase and cherry-pick.', 'Intermediate'),
    title='Rebase, interactive rebase and cherry-pick', short='Rebase and cherry-pick', badge='2.3', minutes=50, added='2026-11-02',
    lead='Move your work onto the latest main, tidy commits before review, copy one fix to a release branch, and know when rewriting history is safe.',
    desc='git rebase and how replay creates new commits, conflicts during rebase, --onto and --update-refs, the golden rule, merge versus rebase, interactive rebase commands, fixup and autosquash, cherry-pick and patch ids.',
    summary='Rebase, the golden rule, merge versus rebase, interactive rebase (pick, squash, fixup, drop) and cherry-pick.',
    keywords=['git rebase', 'interactive rebase', 'squash', 'fixup', 'cherry-pick', 'golden rule', 'merge vs rebase', 'rebase --onto'],
    recap='<p>Rebase replays commits on a new base, giving new ids. Use it on your own branch, never on shared history. Cherry-pick copies single commits.</p>')
