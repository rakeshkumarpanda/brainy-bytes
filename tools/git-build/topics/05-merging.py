# Chapter 2.2: merging. Fast-forward, three way merge and the merge base, --no-ff, --squash, --ff-only, conflicts and
# markers, resolving, abort, conflict styles, the ort strategy (default since Git 2.34), ours and theirs options,
# rerere. Sources: Pro Git 3.2 and 7.8, git-merge, git-merge-base and git-rerere manuals.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow

K = Kit()

K.code('mergebase', r'''
# Find the merge base: the newest commit both branches share
parents = {"C0": [], "C1": ["C0"], "C2": ["C1"], "C3": ["C2"], "C4": ["C1"], "C5": ["C4"]}

def ancestors(c):
    out, todo = [], [c]
    while todo:
        x = todo.pop(0)
        if x not in out:
            out.append(x)
            todo.extend(parents[x])
    return out

main, feature = "C3", "C5"
a = ancestors(main)
b = ancestors(feature)
common = [c for c in a if c in b]
print("ancestors of main:   ", a)
print("ancestors of feature:", b)
print("merge base:", common[0])
print("fast-forward possible?", main in b)
''')

K.lesson('ff', 'Fast-forward or a real merge', f'''
<p>To bring a feature into main you run <code>git merge feature</code> while on main. What Git does depends on the shape of the history.</p>
{table(['Situation', 'What Git does', 'New commit?'], [
    ['main has not moved since feature started', '<b>Fast-forward</b>: main just slides up to the tip of feature', 'No'],
    ['Both branches have new commits', '<b>Three way merge</b>: compares both tips with their merge base and makes a merge commit with two parents', 'Yes'],
    ['feature is already contained in main', 'Already up to date', 'No']])}
{viz('gitsim', cmds='git switch -c feature\ngit commit -m "step 1"\ngit commit -m "step 2"\ngit switch main\ngit merge feature')}
{fxs(
    fx('Merge a branch into the current one', '<code>git merge &lt;branch&gt;</code>', 'Fast-forwards when it can, otherwise makes a merge commit.', key=True),
    fx('Always make a merge commit', '<code>git merge --no-ff &lt;branch&gt;</code>', 'Keeps the feature visible as its own bubble in history, even when a fast-forward was possible.'),
    fx('Refuse anything but a fast-forward', '<code>git merge --ff-only &lt;branch&gt;</code>', 'Fails instead of making a merge commit. Safe default for updating a branch you do not work on.'),
    fx('Squash', '<code>git merge --squash &lt;branch&gt;</code> then <code>git commit</code>', 'Stages all changes of the branch as one new ordinary commit. The branch itself is not recorded as merged.'),
    fx('Merge base', '<code>git merge-base main feature</code>', 'Prints the best common ancestor that a three way merge uses as its base.', key=True))}
{code('mergebase')}
''', kw=['git merge', 'fast-forward', 'three way merge', 'merge commit', '--no-ff', '--ff-only', '--squash', 'merge base', 'merge-base'])

K.lesson('three', 'How a three way merge decides', f'''
<p>Git looks at three versions of every file: the <b>base</b> (the merge base), <b>ours</b> (the branch you are on) and <b>theirs</b> (the branch you merge in). For each part of the file:</p>
{table(['Base', 'Ours', 'Theirs', 'Result'], [
    ['x', 'x', 'x', 'x (nobody changed it)'],
    ['x', 'y', 'x', 'y (only we changed it)'],
    ['x', 'x', 'z', 'z (only they changed it)'],
    ['x', 'y', 'y', 'y (we both made the same change)'],
    ['x', 'y', 'z', '<b>CONFLICT</b>, you decide']])}
{viz('merge3')}
<p>That is why Git can merge most work by itself. It only stops when the same lines were changed in two different ways, or when one side deleted a file the other side edited.</p>
{deep('The ort strategy', '<p>Since Git 2.34 the default merge strategy is <b>ort</b> (Ostensibly Recursive\'s Twin), a rewrite of the older recursive strategy that is much faster and handles renames better. When there is more than one best common ancestor (a criss cross history), ort first merges those ancestors into a virtual base. Other strategies: <b>octopus</b> merges more than two branches at once if there are no conflicts, <b>ours</b> records a merge but keeps our tree completely. Do not confuse the ours strategy (-s ours) with the option -X ours, which only picks our side for conflicting hunks.</p>')}
''', kw=['three way merge', 'base ours theirs', 'ort', 'recursive', 'octopus', 'strategy ours', '-X ours', 'criss cross'])

K.lesson('conflicts', 'Resolving a conflict step by step', f'''
{sh('A conflict and its fix', """git merge feature
git status
# open shop.yml, edit the marked part, delete the markers
git add shop.yml
git commit""", """Auto-merging shop.yml
CONFLICT (content): Merge conflict in shop.yml
Automatic merge failed; fix conflicts and then commit the result.
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)
Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   shop.yml""")}
<p>Inside the file Git writes conflict markers:</p>
{sh('What the file looks like', """<<<<<<< HEAD
colour: green
=======
colour: red
>>>>>>> feature""")}
{steps('Resolve it', ['Read both sides. Above ======= is ours (HEAD), below is theirs (feature).', 'Edit the text to what it should be. It may be one side, the other, or a mix.', 'Delete every marker line. A left over &lt;&lt;&lt;&lt;&lt;&lt;&lt; will break your code.', 'git add the file to mark it resolved, then git commit to finish the merge.', eq('Changed your mind? git merge --abort returns to the state before the merge')])}
{fxs(
    fx('Abort', '<code>git merge --abort</code>', 'Puts everything back as it was before git merge started.', key=True),
    fx('Take one whole side for a file', '<code>git checkout --ours file</code> or <code>--theirs file</code>', 'Then git add file. Useful for generated files such as lock files.'),
    fx('See the base too', '<code>git config merge.conflictStyle diff3</code>', 'Markers then also show the base version between ||||||| and =======. zdiff3 is a tidier variant.'),
    fx('Remember resolutions', '<code>git config rerere.enabled true</code>', 'Reuse recorded resolution: when the same conflict comes back, Git applies your earlier fix.'))}
{note('A file with conflict markers still compiles in some languages, for example inside a YAML string or a Markdown file. Search for &lt;&lt;&lt;&lt;&lt;&lt;&lt; before committing, or let a pre-commit check do it.', 'warn')}
{scene('two testers, one config file', '<p>Asha raises a timeout to 30 seconds for slow test machines. Ravi lowers it to 10 to make failures show faster. Both edit the same line, so the merge stops. Git cannot know which is right. The team talks, picks 20, writes it, and commits the merge. Conflicts are a conversation, not an error.</p>')}
''', kw=['merge conflict', 'conflict markers', 'git merge --abort', 'checkout --ours', 'checkout --theirs', 'conflictStyle', 'diff3', 'zdiff3', 'rerere', 'unmerged paths'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Two friends edit copies of the same story. Git compares both copies with the original. If they changed different sentences, Git combines them. If they changed the same sentence differently, Git asks you which to keep.</p>',
    '<p>A merge commit has two parents. A fast-forward only moves the pointer. A three way merge combines base, ours and theirs, and conflicts happen when both sides change overlapping lines differently.</p>',
    '<p>The merge base is a lowest common ancestor in the commit DAG. With several best common ancestors, ort merges them recursively into a virtual base. Rename detection pairs deleted and added files by similarity so changes follow moved files.</p>',
    '<p>Line based three way merge knows nothing about code structure. Research on structured and semistructured merge parses the code into syntax trees to merge more safely, and studies show many textual merges that succeed still introduce semantic conflicts that only tests catch, which is a strong argument for running CI on the merge result.</p>')}
{note('A clean merge is not a correct merge. Two changes can merge without any conflict and still break the program together. That is why CI on pull requests tests the merged code, not only the branch.', 'exam')}
''', kw=['semantic conflict', 'structured merge', 'merge result testing'])

K.quiz('e', 'When can Git fast-forward?', ['When both branches have new commits', 'When the current branch has not moved since the other branch started', 'Always', 'Never on main'], 1, 'Nothing to combine.', 'main just slides forward to the tip.')
K.quiz('e', 'A merge commit has how many parents?', ['0', '1', '2 or more', 'Exactly 3'], 2, 'Two lines join.', 'Usually 2. An octopus merge has more.')
K.quiz('e', 'Which command cancels a merge with conflicts and restores the earlier state?', ['git merge --stop', 'git merge --abort', 'git reset --soft', 'git revert'], 1, 'Abort.', 'It returns to the state before git merge.')
K.quiz('m', 'In conflict markers, the part above ======= comes from', ['theirs', 'ours (HEAD)', 'the base', 'the remote'], 1, 'HEAD is first.', '<<<<<<< HEAD starts ours.')
K.quiz('m', 'Base x, ours x, theirs z. The merge result is', ['x', 'z', 'conflict', 'both'], 1, 'Only one side changed.', 'Git takes the side that changed.')
K.quiz('m', 'How do you tell Git a conflict is resolved?', ['git resolve', 'git add the file', 'git push', 'git merge --done'], 1, 'Stage it.', 'git add marks it resolved, then git commit.')
K.quiz('m', 'What does --no-ff do?', ['Refuses to merge', 'Makes a merge commit even when a fast-forward was possible', 'Squashes', 'Skips conflicts'], 1, 'No fast-forward.', 'It keeps a visible merge commit.')
K.quiz('h', 'What is the default merge strategy in current Git?', ['recursive', 'ort', 'octopus', 'resolve'], 1, 'Since 2.34.', 'ort replaced recursive as the default in Git 2.34.')
K.quiz('h', 'git merge -s ours other versus git merge -X ours other', ['Same thing', '-s ours ignores all of their changes, -X ours only picks ours for conflicting parts', '-X ours ignores everything', 'Neither exists'], 1, 'Strategy versus option.', 'The strategy keeps our whole tree, the option only settles conflicts.')
K.quiz('x', 'A merge finished with no conflicts but the tests now fail. What is the likely cause?', ['Git bug', 'A semantic conflict: two compatible text changes that break together', 'Line endings', 'The merge base was wrong'], 1, 'Clean text, broken logic.', 'Text merge does not understand code, so CI must test the merge result.')

K.calc('e', 'main has 3 new commits and feature has 4 since they split. How many parents does the merge commit have?', '2', 'Two branches.',
       ['git merge feature on main joins two tips.', 'Commit counts do not matter.', eq('2 parents')], check=2)
K.calc('e', 'main has 0 new commits and feature has 5. git merge feature (default options) creates how many new commits?', '0', 'Fast-forward.',
       ['main has not moved, so a fast-forward is possible.', 'The pointer moves to feature\'s tip.', eq('0 new commits')], check=0)
K.calc('m', 'Same as before but with --no-ff. How many new commits?', '1', 'A merge commit is forced.',
       ['--no-ff refuses to fast-forward.', 'One merge commit is made.', eq('1')], check=1)
K.calc('m', 'A file has 6 parts. Ours changed parts 2 and 5, theirs changed parts 5 and 6, both changed part 5 differently. How many conflicts?', '1', 'Only part 5 overlaps.',
       ['Part 2: ours only, taken.', 'Part 6: theirs only, taken.', eq('Part 5: changed differently on both, 1 conflict')], check=1)
K.calc('h', 'With --squash, feature had 7 commits. After git merge --squash feature and git commit, how many new commits are on main?', '1', 'One ordinary commit.',
       ['Squash stages all changes as one change.', 'git commit records it once.', eq('1 commit, with one parent')], check=1)
K.calc('h', 'C0 to C1 to C2 to C3 is main. feature starts at C1 with C4, C5. What is the merge base? Give the number after C.', '1', 'Newest shared commit.',
       ['Ancestors of C3: C3, C2, C1, C0.', 'Ancestors of C5: C5, C4, C1, C0.', eq('Newest shared: C1')], check=1)

K.assign('mb', 'm', 'Find the merge base',
         '<p>Write <code>merge_base(parents, a, b)</code>. Return the common ancestor of a and b that is not an ancestor of any other common ancestor. You may assume there is exactly one.</p>',
         '''
def merge_base(parents, a, b):
    # your code here
    pass
''', [("merge_base({'C0': [], 'C1': ['C0'], 'C2': ['C1'], 'C3': ['C2'], 'C4': ['C1'], 'C5': ['C4']}, 'C3', 'C5')", 'C1'),
      ("merge_base({'A': [], 'B': ['A'], 'C': ['B']}, 'C', 'B')", 'B')],
         '''
def anc(parents, c):
    seen, todo = set(), [c]
    while todo:
        x = todo.pop()
        if x not in seen:
            seen.add(x)
            todo.extend(parents[x])
    return seen

def merge_base(parents, a, b):
    common = anc(parents, a) & anc(parents, b)
    for c in common:
        if not any(c != o and c in anc(parents, o) for o in common):
            return c
''', 'Find all common ancestors, then keep the one that is not below another one.', '<p>When b is an ancestor of a, the merge base is b itself, and a merge is already up to date.</p>')
K.assign('m3', 'h', 'Three way merge of one line',
         '<p>Write <code>merge_line(base, ours, theirs)</code>. Return the merged line, or the string <code>"CONFLICT"</code> when both sides changed it differently.</p>',
         '''
def merge_line(base, ours, theirs):
    # your code here
    pass
''', [("merge_line('x', 'x', 'z')", 'z'), ("merge_line('x', 'y', 'x')", 'y'), ("merge_line('x', 'y', 'y')", 'y'), ("merge_line('x', 'y', 'z')", 'CONFLICT')],
         '''
def merge_line(base, ours, theirs):
    if ours == theirs:
        return ours
    if ours == base:
        return theirs
    if theirs == base:
        return ours
    return 'CONFLICT'
''', 'Same on both sides, or changed on one side only, can be decided.', '<p>Git applies this rule to whole hunks, not single lines, which is why neighbouring edits also conflict.</p>')

K.must('Fast-forward', 'If the current branch has not moved, merge just moves the pointer. --no-ff forces a merge commit, --ff-only forbids one.')
K.must('Three way merge', 'Base, ours, theirs. One side changed: take it. Same change: take it. Different changes: conflict.')
K.must('Resolve', 'Edit, delete <<<<<<< ======= >>>>>>> markers, git add, git commit. git merge --abort to give up.')
K.must('Strategies', 'ort is the default since Git 2.34. -s ours keeps our tree, -X ours only settles conflicts our way.')
K.must('Clean is not correct', 'A merge without conflicts can still break the program. Test the merged result in CI.')

T = K.topic(
    slug='merging', topic='merging', step=(2, 'Branching and merging', 'git-branch', 'Branches as pointers, fast-forward and three way merges, conflicts, rebase, interactive rebase and cherry-pick.', 'Intermediate'),
    title='Merging and resolving conflicts', short='Merging', badge='2.2', minutes=45, added='2026-11-02',
    lead='Know when Git fast-forwards and when it makes a merge commit, see how a three way merge decides, and resolve conflicts calmly.',
    desc='Fast-forward, three way merge, the merge base, --no-ff, --ff-only and --squash, conflict markers, resolving and aborting, conflict styles, rerere, the ort strategy, ours and theirs, and semantic conflicts.',
    summary='Fast-forward versus three way merge, merge base, squash, conflicts and markers, abort, diff3, rerere and the ort strategy.',
    keywords=['git merge', 'fast-forward', 'merge conflict', 'merge base', 'no-ff', 'squash merge', 'ort', 'rerere'],
    recap='<p>Git fast-forwards when it can, otherwise it merges base, ours and theirs. It only asks you where both sides changed the same lines differently.</p>')
