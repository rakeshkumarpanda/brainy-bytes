# Chapter 5.2: refs, HEAD, the index, plumbing commands, packfiles and deltas, git gc, fsck, dangling objects and the
# reftable format. Sources: Pro Git 10.1, 10.3, 10.4, 10.7, gitrepository-layout, git-update-index, git-write-tree,
# git-commit-tree, git-update-ref, git-pack-refs, git-gc, git-fsck, git-maintenance manuals, Git 3.0 breaking changes.
# Every output below comes from real runs with Git 2.43.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow, file

K = Kit()

K.code('delta', r'''
# A packfile stores a similar object as a delta: copy ranges from a base object, plus new bytes
base = "def add(a, b):\n    return a + b\n"
new = "def add(a, b):\n    return a + b\n\ndef sub(a, b):\n    return a - b\n"

same = 0
while same < min(len(base), len(new)) and base[same] == new[same]:
    same += 1
delta = [("copy", 0, same), ("insert", new[same:])]
print("instructions:", delta)
print("full object :", len(new), "bytes")
print("delta       : about", 2 + len(new) - same, "bytes (a copy instruction plus the new text)")

rebuilt = base[delta[0][1]:delta[0][2]] + delta[1][1]
print("rebuilt ok  :", rebuilt == new)
''')

K.lesson('refs', 'Refs and HEAD are small text files', f'''
<p>Objects have ugly ids, so Git keeps <b>refs</b>: names that hold an id. A branch is a ref under <code>refs/heads/</code>, a tag under <code>refs/tags/</code>, and what you last fetched under <code>refs/remotes/</code>. HEAD usually does not hold an id. It holds the name of a branch, which makes it a <b>symbolic ref</b>.</p>
{table(['File in .git', 'Holds', 'Changed by'], [
    ['<code>HEAD</code>', '<code>ref: refs/heads/main</code> (or an id when detached)', 'git switch, git checkout'],
    ['<code>refs/heads/main</code>', 'the id of the newest commit on main', 'commit, merge, reset, pull'],
    ['<code>refs/tags/v1.0</code>', 'a commit id or a tag object id', 'git tag'],
    ['<code>refs/remotes/origin/main</code>', 'the last fetched id of main on origin', 'fetch, pull, push'],
    ['<code>packed-refs</code>', 'many refs in one file, after git pack-refs or git gc', 'gc, pack-refs'],
    ['<code>logs/HEAD</code>, <code>logs/refs/...</code>', 'the reflog: every old value of each ref', 'every ref update']])}
{sh('Look at the files', """cat .git/HEAD
git symbolic-ref HEAD
cat .git/packed-refs""", """ref: refs/heads/main
refs/heads/main
# pack-refs with: peeled fully-peeled sorted
6132f575896694519968125e6f41dce6232775ac refs/heads/main
3a2a89b76035cd6b23b6d47ca2ded45631cc8ff3 refs/tags/v1.0
^aa1cc961b5f90c399a85465ec3ca67ad215a0b47""", 'Real output after git gc. The ^ line is the commit the annotated tag points to.')}
{note('Never edit ref files with a text editor. Use git update-ref, which writes safely, checks the old value if you ask and records the change in the reflog.', 'warn')}
{deep('reftable', '<p>Thousands of loose ref files are slow on some file systems and cannot be updated atomically as a group. The reftable format, added in Git 2.45 with git init --ref-format=reftable, stores all refs in a few sorted binary files. The plans for Git 3.0 make it the default. Commands do not change, which is one more reason to use git update-ref rather than touching files.</p>')}
''', kw=['refs', 'refs/heads', 'refs/tags', 'refs/remotes', 'HEAD', 'symbolic ref', 'packed-refs', 'update-ref', 'reflog files', 'reftable'])

K.lesson('plumbing', 'add and commit done by hand', f'''
<p>Commands like add and commit are <b>porcelain</b>: friendly commands for people. Each is built from <b>plumbing</b> commands that do one small step. Running the steps yourself shows exactly what a commit is.</p>
{viz('plumbing')}
{sh('Make a commit with plumbing only', """echo hello > hello.txt
git hash-object -w hello.txt
git update-index --add hello.txt
git ls-files --stage
git write-tree
echo "First commit" | git commit-tree aaa96ce
git update-ref refs/heads/main 0f2f6da
git log --oneline""", """ce013625030ba8dba906f756967f9e9ca394464a
100644 ce013625030ba8dba906f756967f9e9ca394464a 0	hello.txt
aaa96ced2d9a1c8e72c56b253a0e2fe78393feb7
0f2f6da1b1026e7464d4051044863d17b1aaf7e6
0f2f6da First commit""", 'Real output, with the same author and date as chapter 5.1, so the ids match')}
{table(['Porcelain', 'Plumbing steps'], [
    ['<code>git add f</code>', 'hash-object -w f, then update-index --add f'],
    ['<code>git commit -m m</code>', 'write-tree, commit-tree &lt;tree&gt; -p HEAD -m m, update-ref refs/heads/&lt;branch&gt; &lt;new id&gt;'],
    ['<code>git branch b</code>', 'update-ref refs/heads/b HEAD'],
    ['<code>git switch b</code>', 'read-tree and checkout-index for the files, symbolic-ref HEAD refs/heads/b']])}
<p>The <b>index</b> (.git/index) is a binary file that lists every tracked path with its mode, blob id and a <b>stage number</b>. Stage 0 is normal. During a merge conflict one path has stages 1 (base), 2 (ours) and 3 (theirs), which is how git status knows what is unmerged.</p>
{note('Plumbing output is stable and meant for scripts. Porcelain output such as git status can change between versions, so scripts should use plumbing or the --porcelain options.', 'exam')}
''', kw=['porcelain', 'plumbing', 'update-index', 'write-tree', 'commit-tree', 'update-ref', 'ls-files --stage', 'index file', 'stage number', 'read-tree'])

K.lesson('packs', 'Packfiles, deltas and garbage collection', f'''
<p>A new object is first written as a <b>loose object</b>: one zlib file per object. That is fast to write but wasteful when there are thousands. <code>git gc</code>, which Git also runs automatically now and then, bundles them into a <b>packfile</b>. Inside a pack, an object that is similar to another can be stored as a <b>delta</b>: instructions to copy parts of a base object plus the few new bytes.</p>
{code('delta')}
{sh('Before and after git gc', """git count-objects -v
git gc
git count-objects -v
ls .git/objects/pack""", """count: 16
size: 64
count: 0
size: 0
in-pack: 16
packs: 1
pack-e477b897487a7cae224bc4db7d3d282d6086dc65.idx
pack-e477b897487a7cae224bc4db7d3d282d6086dc65.pack
pack-e477b897487a7cae224bc4db7d3d282d6086dc65.rev""", 'Real output, shortened: 16 loose objects became one pack')}
{fxs(
    fx('Pack and clean', '<code>git gc</code>', 'Packs loose objects and refs, and removes unreachable objects older than the grace period (two weeks by default, gc.pruneExpire).', key=True),
    fx('Check the database', '<code>git fsck</code>', 'Verifies every object and reports dangling objects that nothing points to.', key=True),
    fx('Count', '<code>git count-objects -vH</code>', 'Loose and packed objects and their sizes.'),
    fx('Background upkeep', '<code>git maintenance start</code>', 'Schedules prefetch, commit-graph and repacking in the background for big repositories.'))}
{sh('A dangling object and its fate', """echo bye > b.txt
git hash-object -w b.txt
git fsck
git gc --prune=now
git fsck""", """b023018cabc396e7692c70bbf5784a93d3f738ab
dangling blob b023018cabc396e7692c70bbf5784a93d3f738ab""", 'Real output: after gc --prune=now the blob is gone and fsck is silent')}
{note('Commits you can still see in the reflog are reachable from it, so gc keeps them until the reflog entry expires (90 days by default, 30 for entries that are not reachable from the branch). That is the safety net from chapter 3.1. --prune=now on a repository you care about removes that net for loose objects nothing points to.', 'warn')}
''', kw=['loose object', 'packfile', 'delta', 'git gc', 'gc.pruneExpire', 'git fsck', 'dangling', 'count-objects', 'git maintenance', 'idx', 'repack'])

K.lesson('layout', 'The whole .git folder', f'''
{table(['Path', 'What it is'], [
    ['<code>HEAD</code>', 'the current branch'], ['<code>config</code>', 'local settings, remotes, branch upstreams'],
    ['<code>index</code>', 'the staging area'], ['<code>objects/</code>', 'loose objects in xx/ folders, packs in pack/'],
    ['<code>refs/</code>, <code>packed-refs</code>', 'branches, tags, remote-tracking branches, stash'],
    ['<code>logs/</code>', 'reflogs'], ['<code>hooks/</code>', 'sample and real hook scripts'],
    ['<code>info/exclude</code>', 'personal ignore rules'], ['<code>MERGE_HEAD</code>, <code>ORIG_HEAD</code>, <code>FETCH_HEAD</code>', 'temporary refs during a merge, after a reset or rebase, and after a fetch']])}
{scene('CI clones and the .git folder', '<p>CI runners clone the repository for every job. With actions/checkout the default is fetch-depth: 1, a shallow clone of one commit, which is fast but has no history. A job that runs git describe, counts commits for a version number, or diffs against main then fails with a confusing error. The fix is fetch-depth: 0 for the full history, or fetching just the refs you need. GitLab sets the clone depth with the GIT_DEPTH variable for the same reason.</p>')}
{ladder(
    '<p>Branches and HEAD are tiny files with ids or names in them. The index is the list for the next commit. Git packs many objects into one file to save space and throws away what nothing points to.</p>',
    '<p>Refs live in refs/ or packed-refs, HEAD is a symbolic ref. Porcelain is built on plumbing: hash-object, update-index, write-tree, commit-tree, update-ref. gc packs, fsck checks, unreachable objects are pruned after the grace period.</p>',
    '<p>Packs hold objects as zlib data or deltas against a base, with an .idx for lookup and a .rev for reverse lookup. Delta choice uses heuristics on type, name and size, not history order, so a delta can point backward in time.</p>',
    '<p>Large hosts add commit-graph files, multi-pack indexes, bitmaps and reftable to answer reachability questions quickly. Research on Git storage studies delta selection and how partial clone and protocol version 2 reduce what a client downloads.</p>')}
''', kw=['.git folder', 'config', 'MERGE_HEAD', 'ORIG_HEAD', 'FETCH_HEAD', 'fetch-depth', 'GIT_DEPTH', 'commit-graph', 'bitmap'])

K.quiz('e', 'What does the file .git/HEAD usually contain?', ['A commit id', 'ref: refs/heads/main', 'The whole history', 'The remote URL'], 1, 'A pointer to a branch.', 'It holds an id only when HEAD is detached.')
K.quiz('e', 'Where do branches live as refs?', ['refs/tags', 'refs/heads', 'objects/', 'hooks/'], 1, 'Heads.', 'Tags in refs/tags, fetched branches in refs/remotes.')
K.quiz('e', 'What does git gc mainly do?', ['Deletes branches', 'Packs loose objects and removes unreachable old ones', 'Pushes to the server', 'Fixes conflicts'], 1, 'Garbage collect.', 'It also packs refs.')
K.quiz('m', 'Which plumbing command turns the index into a tree object?', ['git commit-tree', 'git write-tree', 'git update-index', 'git read-tree'], 1, 'Write the tree.', 'commit-tree then wraps the tree in a commit.')
K.quiz('m', 'In git ls-files --stage, what does stage 2 mean during a conflict?', ['The base version', 'Our version', 'Their version', 'Resolved'], 1, '1 base, 2 ours, 3 theirs.', 'Stage 0 is a normal entry.')
K.quiz('m', 'What is a dangling object?', ['A corrupt object', 'An object that no ref, reflog or other object points to', 'A big file', 'A submodule'], 1, 'Unreachable.', 'git fsck lists them, gc removes them after the grace period.')
K.quiz('m', 'Why should scripts use plumbing instead of parsing git status?', ['Plumbing is faster', 'Plumbing output is stable, porcelain output may change', 'Porcelain needs admin rights', 'No reason'], 1, 'Contracts.', 'Or use --porcelain options made for scripts.')
K.quiz('h', 'A CI job runs git describe and fails with no names found. The checkout used fetch-depth 1. Why?', ['Tags are broken', 'The shallow clone has no tags and no history to describe from', 'gc removed them', 'The runner is offline'], 1, 'Shallow.', 'Use fetch-depth: 0 or fetch tags.')
K.quiz('h', 'In a packfile, what is a delta?', ['A compressed tar', 'Instructions to rebuild an object from a base object plus new bytes', 'A signature', 'A ref'], 1, 'Copy and insert.', 'Similar objects store only differences.')
K.quiz('x', 'What do the plans for Git 3.0 say about refs?', ['Refs are removed', 'reftable becomes the default ref storage', 'HEAD is renamed', 'Tags become branches'], 1, 'New format.', 'Added in Git 2.45 as an option.')

K.calc('e', 'git count-objects shows count: 16 before gc and in-pack: 16 after. How many loose objects remain after gc?', '0', 'All packed.',
       ['gc moved every reachable object into the pack.', 'Loose count drops to zero.', eq('count: 0')], check=0)
K.calc('e', 'Plumbing for one commit: hash-object, update-index, write-tree, commit-tree, update-ref. How many commands?', '5', 'Count them.',
       ['hash-object and update-index do the add.', 'write-tree and commit-tree make the objects.', eq('update-ref moves the branch: 5 commands')], check=5)
K.calc('m', 'A merge conflict on one file. How many index entries does that path have?', '3', 'Stages 1 to 3.',
       ['Stage 1: base.', 'Stage 2: ours.', eq('Stage 3: theirs, so 3 entries')], check=3)
K.calc('m', 'A file of 30 bytes gets 40 bytes appended. Roughly how many bytes does the delta store, counting 2 bytes for the copy instruction?', '42', 'Copy plus new text.',
       ['Copy the first 30 bytes from the base: 2 bytes of instruction.', 'Insert the 40 new bytes.', eq('2 + 40 = 42 bytes, instead of 70')], check=42)
K.calc('h', 'A file of 70 bytes stored as a 42 byte delta. What percent of the full size is saved? Round to a whole number.', '40', '(70 minus 42) over 70.',
       ['Saved bytes: 70 - 42 = 28.', '28 / 70 = 0.4.', eq('40 percent')], check=40)
K.calc('h', 'An unreachable commit was made today. gc.pruneExpire is the default two weeks and the reflog still lists it. With no option, on which day from now does gc first delete it? Use reflog expiry of 30 days for unreachable entries.', '30', 'Both nets must expire.',
       ['The reflog keeps unreachable entries 30 days.', 'After that the object is unreachable and must also be older than 2 weeks, which it is.', eq('first removable on day 30')], check=30)

K.assign('idx', 'm', 'Read conflict stages',
         '<p>Write <code>unmerged(entries)</code>. entries is a list of <code>[mode, id, stage, path]</code> lines as printed by git ls-files --stage. Return the sorted list of paths that have any entry with a stage above 0.</p>',
         '''
def unmerged(entries):
    # your code here
    pass
''', [("unmerged([['100644', 'a1', 0, 'README.md'], ['100644', 'b1', 1, 'app.py'], ['100644', 'b2', 2, 'app.py'], ['100644', 'b3', 3, 'app.py']])", ['app.py']),
      ("unmerged([['100644', 'a1', 0, 'x']])", []),
      ("unmerged([['100644', 'c', 2, 'z.py'], ['100644', 'd', 3, 'a.py']])", ['a.py', 'z.py'])],
         '''
def unmerged(entries):
    return sorted({path for mode, oid, stage, path in entries if stage > 0})
''', 'Collect paths with stage 1, 2 or 3 in a set, then sort.', '<p>git status uses the same rule to print both modified and the other unmerged states.</p>')
K.assign('delta', 'h', 'Apply a delta',
         '<p>Write <code>apply_delta(base, ops)</code>. ops is a list of instructions: <code>["copy", start, length]</code> copies that slice of base, <code>["insert", text]</code> adds new text. Return the rebuilt string.</p>',
         '''
def apply_delta(base, ops):
    # your code here
    pass
''', [("apply_delta('hello world', [['copy', 0, 6], ['insert', 'there']])", 'hello there'),
      ("apply_delta('abcdef', [['copy', 3, 3], ['copy', 0, 3]])", 'defabc'),
      ("apply_delta('', [['insert', 'new file']])", 'new file')],
         '''
def apply_delta(base, ops):
    out = []
    for op in ops:
        if op[0] == 'copy':
            out.append(base[op[1]:op[1] + op[2]])
        else:
            out.append(op[1])
    return ''.join(out)
''', 'Walk the instructions in order and build a list of pieces.', '<p>Real pack deltas encode the same two instructions in binary, with offsets and sizes packed into a few bytes.</p>')

K.must('Refs', 'Names for ids: refs/heads (branches), refs/tags, refs/remotes, packed-refs. HEAD is a symbolic ref to a branch. Change refs with update-ref, never by hand. reftable comes in Git 2.45 and is planned as default in 3.0.')
K.must('Plumbing behind add and commit', 'hash-object -w, update-index --add, write-tree, commit-tree, update-ref. Porcelain is for people, plumbing is stable for scripts.')
K.must('Index stages', '0 normal, 1 base, 2 ours, 3 theirs during a conflict. git ls-files --stage shows them.')
K.must('Packs and gc', 'Loose objects are packed by gc, similar objects stored as deltas. gc prunes unreachable objects after two weeks, reflog entries keep commits alive for 30 or 90 days. fsck checks and lists dangling objects.')
K.must('CI clones', 'actions/checkout fetches one commit by default (fetch-depth: 1). Use fetch-depth: 0 when a job needs tags or history. GitLab uses GIT_DEPTH.')

T = K.topic(
    slug='refs-packs', topic='refs-packs', step=(5, 'Git internals', 'git-internals', 'Open the .git folder: the four object types, how ids are computed, refs, the index, packfiles and garbage collection, and the plumbing commands that porcelain is built on.', 'Advanced'),
    title='Refs, the index, plumbing and packfiles', short='Refs and packs', badge='5.2', minutes=50, added='2026-11-02',
    lead='Branches and HEAD are tiny text files, the index is a list for the next commit, and packfiles keep the database small. Make a commit with plumbing commands only and watch git gc clean up.',
    desc='refs/heads, refs/tags, refs/remotes, HEAD as a symbolic ref, packed-refs and reftable, porcelain and plumbing, hash-object, update-index, write-tree, commit-tree and update-ref, index stages, loose objects, packfiles and deltas, git gc and prune expiry, fsck and dangling objects, the .git folder layout and shallow clones in CI.',
    summary='Refs and HEAD, plumbing behind add and commit, index stages, packfiles, deltas, gc and fsck.',
    keywords=['refs', 'symbolic ref', 'packed-refs', 'plumbing', 'write-tree', 'commit-tree', 'packfile', 'git gc'],
    recap='<p>Refs name commits, the index lists the next tree, plumbing builds every commit, and gc packs and prunes the object database.</p>')
