# Chapter 1.3: reading history and differences. git log options, git show, git diff and its three comparisons, unified
# diff hunks, git blame, naming commits (~, ^, @{n}) and ranges (.., ...). Sources: Pro Git 2.3 and 7.1, gitrevisions(7),
# git-log, git-diff and git-blame manuals.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from gitkit import sh, flow

K = Kit()

K.lesson('log', 'Reading history with git log', f'''
<p><code>git log</code> lists commits newest first. Each entry has the commit id, the author, the date and the message. Its options turn it into a search tool.</p>
{fxs(
    fx('Compact history', '<code>git log --oneline --graph --decorate --all</code>', 'One line per commit, a text drawing of branches and merges, branch and tag names, every branch not just the current one.', key=True),
    fx('Filter', '<code>git log -n 5</code>, <code>--author=Asha</code>, <code>--since="2 weeks ago"</code>, <code>--grep=login</code>', 'Last 5 commits, by one person, in a time window, or with a word in the message.'),
    fx('What a change touched', '<code>git log -p</code>, <code>git log --stat</code>, <code>git log -- path/file</code>', '-p adds the full diff, --stat lists changed files with counts, and -- path limits history to one file.'),
    fx('Find code', '<code>git log -S "price_limit"</code>', 'The pickaxe: commits that added or removed that text. Great for "when did this function appear?".', key=True),
    fx('One commit in full', '<code>git show &lt;commit&gt;</code>', 'Message plus diff. git show HEAD:app.py prints the file as it was in that commit.'))}
{sh('Typical log output', """git log --oneline --graph -6""", """*   a41f0c2 (HEAD -> main) Merge branch 'feature/search'
|\\
| * 7c9e1d0 (feature/search) Add search by price
| * 33b2a91 Add search box
* | 51de0f4 Fix typo on checkout page
|/
* 0b8e3a7 Add product list""")}
{scene('who broke the price filter?', '<p>A tester finds that the price filter ignores decimals. Instead of reading every file, the developer runs git log -S "round(" -- src/filter.py and gets two commits. git show on the newer one shows a round() call added last Tuesday. Bug found in five minutes.</p>')}
''', kw=['git log', '--oneline', '--graph', '--all', 'git show', 'pickaxe', 'log -S', '--author', '--since', '--stat'])

K.lesson('diff', 'git diff: three comparisons and how to read a hunk', f'''
{table(['Command', 'Compares', 'Answers'], [
    ['<code>git diff</code>', 'working tree with the index', 'What have I changed but not staged?'],
    ['<code>git diff --staged</code>', 'index with HEAD', 'What will my next commit contain?'],
    ['<code>git diff HEAD</code>', 'working tree with HEAD', 'Everything since the last commit'],
    ['<code>git diff main feature</code>', 'two commits', 'How do these branches differ?'],
    ['<code>git diff main...feature</code>', 'merge base of the two with feature', 'What did feature add since it split off?']])}
{viz('diffviz')}
{fxs(fx('Hunk header', '<code>@@ -a,b +c,d @@</code>', 'The old file from line a for b lines became the new file from line c for d lines. Lines start with space (context), - (removed) or + (added).', key=True),
     fx('Word level and stats', '<code>git diff --word-diff</code>, <code>git diff --stat</code>', 'Shows changed words inside a line, or only counts per file.'))}
{note('git diff with no arguments shows nothing after git add. The changes did not vanish: they moved to the index. Use git diff --staged.', 'warn')}
{deep('How Git finds the differences', '<p>Git compares lines. It finds a longest common subsequence of lines (the default Myers algorithm finds a shortest edit script), keeps those lines as context and marks the rest as removed or added. Options --patience and --histogram give diffs that are easier to read when code blocks move. A changed line is always one deletion plus one addition.</p>')}
''', kw=['git diff', 'diff --staged', 'diff HEAD', 'hunk', '@@', 'word-diff', 'Myers', 'patience', 'histogram'])

K.lesson('names', 'Naming commits: HEAD, ~, ^ and ranges', f'''
<p>You can name a commit by its id (full or a unique prefix like <code>a41f0c2</code>), by a branch or tag name, or by <b>HEAD</b>, which means "the commit I am on now". From any of those you can walk backwards.</p>
{fxs(
    fx('Ancestors', '<code>X~n</code> = n first parents back. <code>X^n</code> = the n-th parent of X', 'HEAD~1 is the parent, HEAD~2 the grandparent. For a merge commit, X^1 is the branch you were on and X^2 is the branch you merged in.', key=True),
    fx('Two dots', '<code>A..B</code> = reachable from B but not from A', 'git log main..feature lists what feature has that main does not.', key=True),
    fx('Three dots', '<code>A...B</code> = reachable from either but not both', 'With git log --left-right each commit is marked &lt; or &gt; for its side.'),
    fx('Where HEAD was', '<code>HEAD@{n}</code>', 'The n-th previous position of HEAD, from the reflog. HEAD@{1} is where you were before the last move.'))}
{viz('revsel')}
{steps('Work it out: G is a merge with parents E (first) and D (second)', ['G~1 follows the first parent: E.', 'G^2 is the second parent: D.', 'G~3 is G, E, C, B going back three first parents: B.', eq('D..G = commits reachable from G minus those from D = E, G')])}
{note('HEAD~2 and HEAD^^ name the same commit. HEAD^2 is different: it is the second parent of HEAD and only exists if HEAD is a merge commit.', 'exam')}
''', kw=['HEAD', 'HEAD~1', 'HEAD^2', 'tilde', 'caret', 'double dot', 'triple dot', 'revision', 'gitrevisions', 'HEAD@{1}'])

K.lesson('blame', 'Who wrote this line and why', f'''
{fxs(fx('Line by line authors', '<code>git blame -L 10,20 app.py</code>', 'For each line: the commit, author and date that last changed it. -w ignores whitespace changes, -C finds lines moved from other files.'),
     fx('Ignore big reformat commits', '<code>git blame --ignore-revs-file .git-blame-ignore-revs</code>', 'Skip commits listed in the file, such as a project wide formatting run, so blame shows the real author. GitHub reads this file too.'))}
{sh('Blame a few lines', 'git blame -L 3,5 src/cart.py', """5d2c11e3 (Asha 2026-10-02 10:14:21 +0530 3) def total(items):
9f0aa71c (Ravi 2026-10-20 16:40:02 +0530 4)     s = sum(i.price for i in items)
9f0aa71c (Ravi 2026-10-20 16:40:02 +0530 5)     return round(s, 2)""")}
<p>Blame is not about blaming people. It finds the commit, and the commit message tells you why the line exists. Read it before you delete something that looks useless.</p>
{ladder(
    '<p>git log is the diary of the project, git diff shows what changed between two pages of the diary, and git blame tells you who wrote each sentence.</p>',
    '<p>Revisions name commits, ranges name sets of commits. A..B is the set difference of the ancestor sets, A...B the symmetric difference. Most history commands accept both.</p>',
    '<p>Range arithmetic is defined on the commit graph: ^A B, A..B and B --not A are the same set. Merge commits make first parent history special: git log --first-parent shows only the commits made on the branch itself, a clean view of a main branch that receives merges.</p>',
    '<p>Line tracking across renames and moves (blame -C -C) is a hard problem studied as code provenance. Tools like SZZ use blame to find the commits that introduced a bug from the commits that fixed it, a core method in empirical software engineering research.</p>')}
''', kw=['git blame', 'blame -L', 'ignore-revs', 'first-parent', 'SZZ'])

K.quiz('e', 'Which command shows one line per commit with branch names and a drawing of merges?', ['git log --oneline --graph --decorate', 'git status -s', 'git show --all', 'git diff --graph'], 0, 'Graph.', 'These options make the compact graph view.')
K.quiz('e', 'You staged all changes. git diff shows nothing. Why?', ['Changes are lost', 'git diff compares the folder with the index, and they are equal now', 'Git is broken', 'You need to push'], 1, 'Where did they go?', 'Use git diff --staged to see staged changes.')
K.quiz('e', 'HEAD means', ['The first commit', 'The commit you are on now', 'The remote', 'The newest tag'], 1, 'Where you are.', 'HEAD usually points to the current branch, which points to a commit.')
K.quiz('m', 'HEAD~2 is', ['The second parent of HEAD', 'The grandparent of HEAD along first parents', 'Two commits ahead', 'The commit two days ago'], 1, 'Tilde walks back.', '~ follows first parents.')
K.quiz('m', 'For a merge commit M, M^2 is', ['The grandparent', 'The tip of the branch that was merged in', 'The merge base', 'M itself'], 1, 'Second parent.', 'The first parent is the branch you were on, the second the one merged in.')
K.quiz('m', 'git log main..feature lists', ['Commits on main not on feature', 'Commits on feature not on main', 'All commits', 'Commits on both'], 1, 'Reachable from the right, not the left.', 'A..B = in B, not in A.')
K.quiz('m', 'In a hunk header @@ -12,4 +12,5 @@, how many lines does the new side have?', ['4', '5', '12', '9'], 1, 'Plus side.', '+12,5: starting at line 12, 5 lines.')
K.quiz('h', 'Which command finds commits that added or removed the text "apply_discount"?', ['git grep apply_discount', 'git log -S apply_discount', 'git blame apply_discount', 'git diff apply_discount'], 1, 'Pickaxe.', 'git grep searches the files now, log -S searches changes over history.')
K.quiz('h', 'git diff main...feature compares feature with', ['main', 'the merge base of main and feature', 'HEAD', 'origin'], 1, 'Three dots in diff.', 'For diff, A...B means merge base of A and B against B.')
K.quiz('x', 'How do you stop blame from pointing every line at a big formatting commit?', ['git blame --quiet', 'List that commit in .git-blame-ignore-revs and use --ignore-revs-file', 'Delete the commit', 'git blame -w only'], 1, 'Ignore revisions.', 'blame skips listed commits and looks past them.')

K.calc('e', 'A hunk header reads @@ -20,6 +20,8 @@ and has 5 context lines. How many lines were added if 1 line was removed?', '3', 'New side = context + added.',
       ['Old side 6 = context 5 + removed 1.', 'New side 8 = context 5 + added.', eq('added = 8 − 5 = 3')], check=3)
K.calc('e', 'A straight history A, B, C, D, E with HEAD at E. Which letter is HEAD~3? Give its position counting A as 1.', '2', 'Walk back three.',
       ['HEAD~1 = D.', 'HEAD~2 = C.', eq('HEAD~3 = B, position 2')], check=2)
K.calc('m', 'History A, B, C on main. feature branches from B and adds X, Y. How many commits does git log main..feature show?', '2', 'In feature, not in main.',
       ['feature reaches A, B, X, Y.', 'main reaches A, B, C.', eq('{A, B, X, Y} − {A, B, C} = {X, Y}: 2 commits')], check=2)
K.calc('m', 'Same history. How many commits does git log main...feature show?', '3', 'Symmetric difference.',
       ['Only in main: C.', 'Only in feature: X, Y.', eq('1 + 2 = 3 commits')], check=3)
K.calc('h', 'G is a merge with parents E and D. E has parent C, D has parent C, C has parent B, B has parent A. How many commits are reachable from G, including G?', '6', 'Count A to G without F.',
       ['Start at G, add E and D.', 'Both lead to C, then B, then A.', eq('G, E, D, C, B, A = 6')], check=6)
K.calc('h', 'git diff --stat says "3 files changed, 27 insertions(+), 9 deletions(-)". What is the net change in line count?', '18', 'Insertions minus deletions.',
       ['27 lines added.', '9 lines removed.', eq('27 − 9 = 18 more lines')], check=18)

K.must('git log', '--oneline --graph --all for the picture. -S text to find when code appeared. -p and --stat for what changed. -- path for one file.')
K.must('Three diffs', 'git diff: folder vs index. git diff --staged: index vs HEAD. git diff HEAD: folder vs HEAD.')
K.must('Hunks', '@@ -a,b +c,d @@: old lines a to a+b-1 became new lines c to c+d-1. A changed line is one - and one +.')
K.must('Naming commits', 'X~n: n first parents back. X^n: n-th parent of a merge. HEAD@{n}: where HEAD was n moves ago.')
K.must('Ranges', 'A..B: in B not in A. A...B: in one but not both (log), or merge base to B (diff).')

T = K.topic(
    slug='history-diffs', topic='history-diffs', step=(1, 'Getting started with Git', 'git-start', 'What version control is, how Git thinks, the three areas of a repository, and how to read history and differences.', 'Beginner'),
    title='Reading history: log, diff, blame and naming commits', short='History and diffs', badge='1.3', minutes=45, added='2026-11-02',
    lead='Search history like a detective, read every part of a diff, and name any commit with ~, ^, .. and ...',
    desc='git log and its filters, git show, the pickaxe, git diff against the index, HEAD and other commits, hunk headers, the diff algorithm, ~ and ^, HEAD@{n}, two dot and three dot ranges, and git blame.',
    summary='git log filters and the pickaxe, the three diffs and hunk headers, ~, ^, reflog names, .. and ... ranges, and git blame.',
    keywords=['git log', 'git diff', 'git show', 'git blame', 'HEAD~1', 'HEAD^2', 'double dot', 'triple dot', 'hunk'],
    recap='<p>git log tells the story, git diff shows exact line changes, and ~, ^, .. and ... let you point at any commit or set of commits.</p>')
