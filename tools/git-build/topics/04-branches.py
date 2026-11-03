# Chapter 2.1: branches and HEAD. A branch is a movable pointer (a file holding a commit id), HEAD is a pointer to the
# current branch, git branch, switch and checkout, detached HEAD, naming, listing and deleting. Sources: Pro Git 3.1 and
# 3.2, git-branch, git-switch and git-checkout manuals (switch and restore were added in Git 2.23).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow

K = Kit()

K.code('pointers', r'''
# Branches are just names that point at commits. HEAD names the current branch.
refs = {"main": "C1"}
head = "main"
parents = {"C0": [], "C1": ["C0"]}
count = 2

def commit():
    global count
    new = "C" + str(count)
    count += 1
    parents[new] = [refs[head]]     # the new commit's parent is the old tip
    refs[head] = new                # only the current branch moves
    return new

refs["feature"] = refs["main"]      # git branch feature: a new pointer, no copy of files
head = "feature"                    # git switch feature
print("commit on feature:", commit(), refs)
head = "main"
print("commit on main:   ", commit(), refs)
print("feature parent chain:", refs["feature"], "->", parents[refs["feature"]][0])
''')

K.lesson('what', 'A branch is just a movable label', f'''
<p>In many old tools a branch meant copying the whole project into a new folder. In Git a branch is tiny: a file inside <code>.git/refs/heads/</code> that holds one commit id, 41 bytes. Creating a branch is instant because nothing is copied.</p>
<p>Think of a bookmark in a book you are writing. The book is the chain of commits. The bookmark called <b>main</b> sits on the last page you wrote. When you write a new page with the bookmark in your hand, the bookmark moves to the new page. <b>HEAD</b> is the answer to "which bookmark am I holding right now?".</p>
{fxs(
    fx('Create', '<code>git branch &lt;name&gt; [&lt;start&gt;]</code>', 'Makes a new pointer at HEAD, or at start. You stay where you are.'),
    fx('Switch', '<code>git switch &lt;name&gt;</code>', 'Moves HEAD to that branch and updates your files to its snapshot.', key=True),
    fx('Create and switch', '<code>git switch -c &lt;name&gt;</code>', 'The same as the older git checkout -b &lt;name&gt;.', key=True),
    fx('See branches', '<code>git branch -vv</code>, <code>git branch -a</code>', '-vv shows the tip commit and the upstream of each branch, -a adds remote tracking branches.'))}
{viz('gitsim')}
{code('pointers')}
{note('Only the branch HEAD points to moves when you commit. Other branches stay exactly where they are. That is the whole trick behind parallel work.', 'tip')}
''', kw=['branch', 'pointer', 'refs/heads', 'HEAD', 'git branch', 'git switch', 'switch -c', 'checkout -b', 'branch -vv'])

K.lesson('switch', 'switch, checkout and what happens to your files', f'''
<p>Git 2.23 split the old all in one <code>git checkout</code> into two clearer commands: <code>git switch</code> for branches and <code>git restore</code> for files. checkout still works and you will see it in older guides.</p>
{table(['Job', 'Newer command', 'Older command'], [
    ['Go to a branch', '<code>git switch feature</code>', '<code>git checkout feature</code>'],
    ['Create a branch and go to it', '<code>git switch -c feature</code>', '<code>git checkout -b feature</code>'],
    ['Go back to the previous branch', '<code>git switch -</code>', '<code>git checkout -</code>'],
    ['Look at an old commit', '<code>git switch --detach a1b2c3d</code>', '<code>git checkout a1b2c3d</code>'],
    ['Throw away edits in a file', '<code>git restore app.py</code>', '<code>git checkout -- app.py</code>']])}
<p>When you switch, Git rewrites the files in your folder to match the other branch. Uncommitted changes come along if they do not clash. If a change would be overwritten, Git refuses:</p>
{sh('Git protects uncommitted work', 'git switch main', """error: Your local changes to the following files would be overwritten by checkout:
        app.py
Please commit your changes or stash them before you switch branches.
Aborting""")}
{note('Commit or stash (chapter 3.2) before switching when Git complains. Never fix it with a hard reset unless you really want to lose the edits.', 'warn')}
''', kw=['git switch', 'git checkout', 'git restore', 'switch -', 'Git 2.23', 'would be overwritten'])

K.lesson('detached', 'Detached HEAD, without fear', f'''
<p>Normally HEAD points to a branch, and the branch points to a commit. If you check out a commit id or a tag directly, HEAD points straight at the commit. That is <b>detached HEAD</b>. You can look around, build and even commit. But new commits belong to no branch, so when you switch away they are only reachable through the reflog, and Git will eventually clean them up.</p>
{sh('Detached HEAD, then save the work', """git switch --detach v1.0
# try something, commit it
git commit -am "experiment"
# keep it: give it a branch name
git switch -c experiment""", """HEAD is now at 3f2a9c1 Release 1.0
[detached HEAD 8d1e004] experiment
Switched to a new branch 'experiment'""")}
{steps('Typical reasons to be detached', ['Testing an old release to see if a bug was already there.', 'git bisect checks out commits for you in this state.', 'CI systems often check out the exact commit, so jobs run with a detached HEAD.', eq('Fix: git switch -c name keeps the commits, git switch main leaves them behind')])}
{note('If you already left the detached commits, run git reflog, find the id, and run git branch rescue &lt;id&gt;.', 'tip')}
''', kw=['detached HEAD', 'checkout commit', 'switch --detach', 'rescue commit', 'reflog'])

K.lesson('manage', 'Naming, renaming and deleting branches', f'''
{fxs(
    fx('Rename', '<code>git branch -m &lt;old&gt; &lt;new&gt;</code>', 'With one name it renames the current branch.'),
    fx('Delete safely', '<code>git branch -d &lt;name&gt;</code>', 'Refuses if the branch has commits not merged into the current branch or its upstream.', key=True),
    fx('Force delete', '<code>git branch -D &lt;name&gt;</code>', 'Deletes even unmerged work. The commits survive in the reflog for a while.'),
    fx('Merged or not', '<code>git branch --merged</code>, <code>--no-merged</code>', 'Lists branches whose tips are (or are not) contained in HEAD. Good for clean up.'))}
{table(['Naming habit', 'Example'], [['type and short description', 'feature/search-by-price, fix/login-crash'], ['ticket number', 'feature/SHOP-142-search'], ['no spaces, lowercase, dashes', 'release/2.4']])}
{ladder(
    '<p>A branch is a sticky note with a name on one page of the history. Making one is free. You can have as many as you like and throw them away when the work is merged.</p>',
    '<p>A branch is a ref under refs/heads. HEAD is a symbolic ref, usually "ref: refs/heads/main". Committing creates a commit whose parent is the old tip and updates the ref HEAD points to.</p>',
    '<p>Refs may be loose files or lines in .git/packed-refs. Updates are atomic: Git writes a lock file and renames it. Branch names are restricted by git check-ref-format (no spaces, no .., no ~ ^ : ? * [).</p>',
    '<p>The reftable backend stores refs in a binary sorted table, which scales to millions of refs and fixes problems such as two names that differ only in case on case insensitive file systems. The Git project plans to make it the default for new repositories in Git 3.0.</p>')}
{scene('the long lived branch', '<p>A team keeps a branch called new-design open for four months. When they finally merge, hundreds of files conflict. Short branches that merge within days avoid this, which is why most teams aim for small pull requests.</p>')}
''', kw=['branch -d', 'branch -D', 'branch -m', 'merged', 'no-merged', 'branch naming', 'symbolic ref', 'packed-refs', 'reftable'])

K.quiz('e', 'What is a Git branch?', ['A copy of all files', 'A movable pointer to a commit', 'A remote server', 'A folder'], 1, 'Tiny file.', 'It is a ref holding one commit id.')
K.quiz('e', 'Which command creates a branch and switches to it?', ['git branch -s x', 'git switch -c x', 'git commit -b x', 'git new x'], 1, '-c for create.', 'git checkout -b x does the same.')
K.quiz('e', 'When you commit, which branch moves?', ['All branches', 'The branch HEAD points to', 'main always', 'None'], 1, 'Current branch.', 'Other branches stay where they are.')
K.quiz('m', 'You check out a tag directly. What state are you in?', ['Merging', 'Detached HEAD', 'Rebasing', 'Bare'], 1, 'HEAD points at a commit.', 'HEAD points to a commit, not a branch.')
K.quiz('m', 'git branch -d feature fails with "not fully merged". Why?', ['The name is wrong', 'feature has commits not contained in the current branch', 'feature is checked out elsewhere', 'You need -m'], 1, 'Safety check.', '-d protects unmerged work. Merge it or use -D if you are sure.')
K.quiz('m', 'Which command returns to the previous branch?', ['git switch -', 'git switch ..', 'git back', 'git branch -p'], 0, 'Like cd -.', 'git switch - and git checkout - both work.')
K.quiz('m', 'Git refuses to switch because local changes would be overwritten. The safest fix is', ['git reset --hard', 'Commit or stash the changes first', 'Delete .git', 'git switch -f'], 1, 'Keep the work.', 'Committing or stashing keeps your edits.')
K.quiz('h', 'What does .git/HEAD usually contain?', ['A commit id', 'ref: refs/heads/main', 'The remote URL', 'The last message'], 1, 'Symbolic ref.', 'In detached HEAD it contains a commit id instead.')
K.quiz('h', 'You made commits in detached HEAD and switched away. How do you get them back?', ['They are gone', 'Find the id in git reflog and create a branch at it', 'git pull', 'git revert'], 1, 'Reflog.', 'git branch rescue <id> brings them back while the reflog still has them.')
K.quiz('x', 'Which branch name is invalid?', ['feature/login', 'fix-12', 'release..2', 'hotfix_3'], 2, 'check-ref-format.', 'Two dots in a row are not allowed in ref names.')

K.calc('e', 'A branch ref file holds a 40 character SHA-1 id and a newline. How many bytes is it?', '41', '40 plus 1.',
       ['40 hex characters, one byte each.', 'One newline byte.', eq('40 + 1 = 41 bytes')], check=41)
K.calc('e', 'main is at C2. You run git switch -c feature and commit twice, then switch to main and commit once. How many commits are on feature but not on main?', '2', 'Count feature only commits.',
       ['feature: C3, C4 after C2.', 'main: C5 after C2.', eq('feature only: C3, C4 = 2')], check=2)
K.calc('m', 'Same story. How many commits are reachable from main if the history started with C0?', '4', 'C0, C1, C2, C5.',
       ['C0, C1, C2 are shared.', 'C5 is on main.', eq('4 commits')], check=4)
K.calc('m', 'A team of 8 each keeps 3 feature branches plus main and develop. How many branch refs are in the shared repository if everyone pushes theirs?', '26', 'Per person times count, plus 2.',
       ['8 × 3 = 24 feature branches.', 'Plus main and develop.', eq('24 + 2 = 26')], check=26)
K.calc('h', 'In detached HEAD you make 3 commits, then switch to main. How many of those commits does git branch --contains on any branch list? Answer the number of the 3 that still belong to a branch.', '0', 'No branch was created.',
       ['The commits were made with HEAD pointing to a commit, not a branch.', 'Switching away left them with no ref.', eq('0, only the reflog knows them')], check=0)
K.calc('h', 'git branch --merged lists 7 branches including main (the current one). How many can you delete with git branch -d without force?', '6', 'All except the current branch.',
       ['Every merged branch passes the -d check.', 'You cannot delete the branch you are on.', eq('7 − 1 = 6')], check=6)

K.assign('br', 'e', 'Commit on the current branch',
         '<p><code>refs</code> maps branch names to commit ids and <code>head</code> is the current branch. Write <code>commit(refs, head, new_id)</code> that returns a new dictionary where only the current branch moves to <code>new_id</code>.</p>',
         '''
def commit(refs, head, new_id):
    # your code here
    pass
''', [("commit({'main': 'C1', 'feature': 'C1'}, 'feature', 'C2')", {'main': 'C1', 'feature': 'C2'}), ("commit({'main': 'C5'}, 'main', 'C6')", {'main': 'C6'})],
         '''
def commit(refs, head, new_id):
    out = dict(refs)
    out[head] = new_id
    return out
''', 'Copy the dictionary, then change one key.', '<p>This is all git commit does to refs: one pointer moves.</p>')
K.assign('del', 'm', 'Is it safe to delete?',
         '<p>Write <code>safe_delete(parents, refs, current, name)</code>. Return True when the tip of <code>name</code> is an ancestor of (or equal to) the tip of <code>current</code>, as git branch -d checks.</p>',
         '''
def safe_delete(parents, refs, current, name):
    # your code here
    pass
''', [("safe_delete({'A': [], 'B': ['A'], 'C': ['B']}, {'main': 'C', 'old': 'B'}, 'main', 'old')", True),
      ("safe_delete({'A': [], 'B': ['A'], 'X': ['A']}, {'main': 'B', 'old': 'X'}, 'main', 'old')", False)],
         '''
def safe_delete(parents, refs, current, name):
    seen, todo = set(), [refs[current]]
    while todo:
        c = todo.pop()
        if c not in seen:
            seen.add(c)
            todo.extend(parents[c])
    return refs[name] in seen
''', 'Collect every ancestor of the current tip and look for the other tip.', '<p>Git also accepts the branch if it is merged into its upstream branch.</p>')

K.must('Branch', 'A branch is a ref, a 41 byte file with a commit id. Creating one copies nothing. Commits move only the branch HEAD points to.')
K.must('switch', 'git switch name, git switch -c name, git switch - (previous). checkout does the same in older guides.')
K.must('Detached HEAD', 'HEAD points at a commit. Commits made there need git switch -c name, or they are left for the reflog only.')
K.must('Delete', 'git branch -d refuses unmerged work. -D forces. --merged and --no-merged help clean up.')
K.must('Protect work', 'Git refuses to switch if uncommitted edits would be overwritten. Commit or stash first.')

T = K.topic(
    slug='branches', topic='branches', step=(2, 'Branching and merging', 'git-branch', 'Branches as pointers, fast-forward and three way merges, conflicts, rebase, interactive rebase and cherry-pick.', 'Intermediate'),
    title='Branches and HEAD', short='Branches', badge='2.1', minutes=40, added='2026-11-02',
    lead='Learn that a branch is only a label on a commit, move between branches safely, and stop fearing detached HEAD.',
    desc='What a branch is, HEAD, git branch, switch and checkout, what happens to your files, detached HEAD and how to rescue commits, renaming and deleting branches, naming habits and ref internals.',
    summary='Branches as pointers, HEAD, switch and checkout, detached HEAD and rescue, renaming and deleting branches.',
    keywords=['branch', 'HEAD', 'git switch', 'git checkout', 'detached HEAD', 'git branch -d', 'branch naming'],
    recap='<p>A branch is a movable label. HEAD says which label you hold. Commits move that label only.</p>')
