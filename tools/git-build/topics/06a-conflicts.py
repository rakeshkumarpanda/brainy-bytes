# Chapter 2.4: merge conflicts end to end. How a conflict arises, what Git writes into the file and the index, and six
# ways out: edit by hand, checkout --ours or --theirs, -X ours or -X theirs, git mergetool, rebase (with the swapped
# labels), and abort. Also conflict styles, rerere, conflicts from cherry-pick and stash pop, modify/delete conflicts
# and the GitHub and GitLab web resolvers. Every terminal output below was produced by Git 2.43.0 on the same three line
# shop.yml, with author Asha and a fixed date so the ids match the animation. Sources: git-merge, git-checkout, git-mergetool, git-rebase, git-rerere and git-ls-files manuals, GitHub
# docs "Resolving a merge conflict on GitHub", GitLab docs "Merge request conflicts".
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from gitkit import sh, flow

K = Kit()

K.lesson('arise', 'How a conflict arises', f'''
<p>A conflict needs three things: a common starting point, and two branches that each change the <b>same lines</b> of that starting point in <b>different</b> ways. Here is the exact setup used in every example on this page.</p>
{flow(('Base commit B', 'shop.yml has title: Shop, colour: blue, price: 10'),
      ('feature branch', 'Commit F changes colour: blue to colour: red'),
      ('main branch', 'Commit M changes colour: blue to colour: green'),
      ('git merge feature', 'Both sides changed line 2 differently. Git stops and asks you.'))}
{sh('Recreate it yourself in an empty folder', """git init -b main shop && cd shop
printf 'title: Shop\\ncolour: blue\\nprice: 10\\n' > shop.yml
git add shop.yml && git commit -m "Start shop"
git switch -c feature
sed -i 's/blue/red/' shop.yml && git commit -am "Make it red"
git switch main
sed -i 's/blue/green/' shop.yml && git commit -am "Make it green"
git merge feature""", """Auto-merging shop.yml
CONFLICT (content): Merge conflict in shop.yml
Automatic merge failed; fix conflicts and then commit the result.""")}
<p>Press Play below and step through it. Then change the two lines, pick another way out, and play it again. Make both lines identical to see that the same change on both sides is not a conflict at all.</p>
{viz('conflictlab')}
{table(['Change on main', 'Change on feature', 'Result'], [
    ['line 2 to green', 'line 3 to L', 'No conflict, both changes kept (different lines, not touching)'],
    ['line 2 to green', 'line 2 to green', 'No conflict, the same change'],
    ['line 2 to green', 'line 2 to red', '<b>Content conflict</b>'],
    ['line 2 to green', 'line 3 to L, with line 2 changed by main right next to it', 'Usually one conflict hunk, because touching changed lines are treated as one block'],
    ['delete the file', 'edit the file', '<b>modify/delete conflict</b>']])}
''', kw=['merge conflict', 'how conflicts arise', 'same lines', 'merge base', 'CONFLICT (content)', 'shop.yml'])

K.lesson('inside', 'What Git writes during a conflict', f'''
<p>While the merge is stopped, Git keeps the conflict in two places: markers in your working file, and three versions of the file in the index.</p>
{sh('The working file', """cat shop.yml""", """title: Shop
<<<<<<< HEAD
colour: green
=======
colour: red
>>>>>>> feature
price: 10""")}
{table(['Marker', 'Meaning'], [
    ['<code>&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD</code>', 'Start of ours: the branch you are on (main)'],
    ['<code>=======</code>', 'End of ours, start of theirs'],
    ['<code>&gt;&gt;&gt;&gt;&gt;&gt;&gt; feature</code>', 'End of theirs: the branch you are merging in'],
    ['<code>||||||| 9df4fec</code>', 'Only with diff3 or zdiff3: the base version follows, up to ======='],
    ['Lines outside the markers', 'Already merged by Git. title and price were not in dispute.']])}
{sh('The index holds three stages of the same path', """git ls-files -s""", """100644 43918cc4350c12c7f3c22c9b100a72aa87392b72 1	shop.yml
100644 ca20d2f7390cdacead2744d74c0495ed4c2734d0 2	shop.yml
100644 a948cd2871dc89abc707644334e43bde560ed543 3	shop.yml""")}
<p>Stage 1 is the base, stage 2 is ours, stage 3 is theirs. A normal file sits at stage 0. <b>git add</b> on the file replaces the three stages with one stage 0 entry, and that is exactly what "mark as resolved" means.</p>
{sh('See the base as well, in the markers', """git merge --abort
git config merge.conflictStyle zdiff3
git merge feature
cat shop.yml""", """title: Shop
<<<<<<< HEAD
colour: green
||||||| 9df4fec
colour: blue
=======
colour: red
>>>>>>> feature
price: 10""")}
<p>Now you can see that both sides started from blue. Knowing the starting point often tells you which change was intended, so many teams turn zdiff3 on globally.</p>
{fxs(
    fx('Which files are in conflict', '<code>git status</code> or <code>git diff --name-only --diff-filter=U</code>', 'Conflicted files show as both modified, or UU in the short format.', key=True),
    fx('Look at one stage', '<code>git show :1:shop.yml</code>, <code>:2:</code>, <code>:3:</code>', 'Prints the base, ours or theirs version straight from the index.'),
    fx('Combined diff', '<code>git diff</code>', 'During a conflict it shows a combined diff with two columns of + and minus signs, one per side.'))}
''', kw=['conflict markers', 'HEAD', 'ours', 'theirs', 'index stages', 'git ls-files -s', 'stage 1 2 3', 'zdiff3', 'diff3', 'git show :2:'])

K.lesson('ways', 'Six ways to resolve the same conflict', f'''
{table(['Way', 'Commands', 'Result in shop.yml', 'Use it when'], [
    ['1. Edit by hand', 'edit, delete markers, <code>git add</code>, <code>git commit</code>', 'Whatever you write, for example colour: purple', 'Both changes matter, or a mix is right. The usual case.'],
    ['2. Keep ours for a file', '<code>git checkout --ours shop.yml</code>, add, commit', 'colour: green', 'Their version of this file is simply wrong or stale'],
    ['3. Keep theirs for a file', '<code>git checkout --theirs shop.yml</code>, add, commit', 'colour: red', 'Generated files such as package-lock.json, which you then regenerate'],
    ['4. Pick a side for every hunk up front', '<code>git merge -X ours feature</code> or <code>-X theirs</code>', 'green or red, no stop at all', 'You already know one side wins every clash. Non clashing changes are still merged.'],
    ['5. A merge tool', '<code>git mergetool</code>', 'What you save in the MERGED pane', 'Many hunks, or you prefer a side by side view'],
    ['6. Back out', '<code>git merge --abort</code>', 'Back to colour: green, as before the merge', 'You need to ask someone first, or you merged the wrong branch']])}
{sh('Way 1, by hand', """# open shop.yml, write colour: purple, delete the three marker lines
git add shop.yml
git commit --no-edit""", """[main c279a4c] Merge branch 'feature'""")}
{sh('Way 2 and 3, one whole side', """git checkout --theirs shop.yml
git add shop.yml
git commit --no-edit""", """Updated 1 path from the index
[main 119b0b1] Merge branch 'feature'""")}
<p>Commit ids include the author and the time, so the ids on your machine will differ from the ones shown here. File ids such as 43918cc depend only on the content, so they will match.</p>
{sh('Way 4, decide before merging', """git merge -X ours feature""", """Auto-merging shop.yml
Merge made by the 'ort' strategy.""")}
{sh('Way 5, a merge tool', """git mergetool --tool-help
git mergetool --tool=vimdiff""", """'git mergetool --tool=<tool>' may be set to one of the following:
		vimdiff          Use Vim with a custom layout (see `git help mergetool`'s `BACKEND SPECIFIC HINTS` section)
		vimdiff1         Use Vim with a 2 panes layout (LOCAL and REMOTE)
		vimdiff2         Use Vim with a 3 panes layout (LOCAL, MERGED and REMOTE)""", cap='What you will see (shortened)')}
<p>A merge tool opens four views: <b>LOCAL</b> (ours), <b>BASE</b>, <b>REMOTE</b> (theirs) and <b>MERGED</b>, which is the real file you edit. Save and quit, and git mergetool runs git add for you. VS Code, IntelliJ and Meld do the same job with buttons such as Accept Current, Accept Incoming and Accept Both. Accept Current means ours and Accept Incoming means theirs.</p>
{note('git checkout --ours and git merge -X ours are different. The first acts on a whole file after the stop. The second acts on each clashing hunk during the merge, and still keeps their changes in every other place. git merge -s ours (a strategy, with a small s) is different again: it throws away all of their changes.', 'warn')}
{sh('Changed your mind about a file you resolved', """git checkout -m shop.yml""", """Recreated 1 merge conflict""")}
''', kw=['resolve conflict', 'git checkout --ours', 'git checkout --theirs', '-X ours', '-X theirs', 'git mergetool', 'LOCAL BASE REMOTE MERGED', 'git merge --abort', 'checkout -m', 'Accept Current', 'Accept Incoming'])

K.lesson('rebase', 'Conflicts during a rebase: the labels swap', f'''
<p>If you rebase feature onto main instead of merging, the same clash appears, but your own commit is now replayed on top of main. That changes who is ours.</p>
{sh('Rebase the feature branch', """git switch feature
git rebase main""", """Auto-merging shop.yml
CONFLICT (content): Merge conflict in shop.yml
error: could not apply ed28287... Make it red
hint: Resolve all conflicts manually, mark them as resolved with
hint: "git add/rm <conflicted_files>", then run "git rebase --continue".
hint: You can instead skip this commit: run "git rebase --skip".
hint: To abort and get back to the state before "git rebase", run "git rebase --abort".
Could not apply ed28287... Make it red""")}
{sh('The file during the rebase', """cat shop.yml""", """title: Shop
<<<<<<< HEAD
colour: green
=======
colour: red
>>>>>>> ed28287 (Make it red)
price: 10""")}
{table(['', 'During git merge feature (on main)', 'During git rebase main (on feature)'], [
    ['HEAD and ours', 'main, colour: green', 'main, colour: green (the commit you are replaying onto)'],
    ['theirs', 'feature, colour: red', 'your own commit ed28287, colour: red'],
    ['To keep your feature change', 'git checkout --theirs', '<b>also</b> git checkout --theirs'],
    ['Finish with', 'git add, git commit', 'git add, git rebase --continue'],
    ['Back out with', 'git merge --abort', 'git rebase --abort'],
    ['Drop just this commit', 'not available', 'git rebase --skip']])}
{sh('Finish the rebase', """git checkout --theirs shop.yml
git add shop.yml
git rebase --continue""", """Updated 1 path from the index
[detached HEAD d696c84] Make it red
 1 file changed, 1 insertion(+), 1 deletion(-)
Successfully rebased and updated refs/heads/feature.""")}
{note('A rebase replays commits one by one, so a branch with five commits can stop up to five times, once for each commit that clashes. A merge stops at most once. That is a fair reason to merge long lived branches, or to squash before rebasing.', 'tip')}
''', kw=['rebase conflict', 'git rebase --continue', 'git rebase --skip', 'git rebase --abort', 'ours theirs swapped', 'HEAD during rebase'])

K.lesson('other', 'Other places conflicts appear', f'''
{sh('cherry-pick', """git cherry-pick feature""", """Auto-merging shop.yml
CONFLICT (content): Merge conflict in shop.yml
error: could not apply ed28287... Make it red
hint: After resolving the conflicts, mark them with
hint: "git add/rm <pathspec>", then run
hint: "git cherry-pick --continue".
hint: You can instead skip this commit with "git cherry-pick --skip".
hint: To abort and get back to the state before "git cherry-pick",
hint: run "git cherry-pick --abort".""")}
{sh('stash pop', """git stash pop""", """Auto-merging shop.yml
CONFLICT (content): Merge conflict in shop.yml
On branch main
Unmerged paths:
  (use "git restore --staged <file>..." to unstage)
  (use "git add <file>..." to mark resolution)
	both modified:   shop.yml

no changes added to commit (use "git add" and/or "git commit -a")
The stash entry is kept in case you need it again.""")}
<p>After a conflicting stash pop, resolve the file, then <b>git stash drop</b> yourself, because Git kept the entry. There is nothing to commit or continue.</p>
{sh('modify/delete', """git merge feature""", """CONFLICT (modify/delete): old.txt deleted in HEAD and modified in feature.  Version feature of old.txt left in tree.
Automatic merge failed; fix conflicts and then commit the result.""")}
<p>No markers here, because there is no line to compare against a deleted file. Decide: <b>git add old.txt</b> keeps the edited file, <b>git rm old.txt</b> confirms the delete. Then commit.</p>
{table(['Situation', 'Finish', 'Back out'], [
    ['git merge', 'git add, git commit', 'git merge --abort'],
    ['git rebase', 'git add, git rebase --continue', 'git rebase --abort'],
    ['git cherry-pick', 'git add, git cherry-pick --continue', 'git cherry-pick --abort'],
    ['git revert', 'git add, git revert --continue', 'git revert --abort'],
    ['git stash pop', 'git add (or restore), then git stash drop', 'git checkout -- . then the stash is still there'],
    ['git pull', 'same as merge, or as rebase with pull.rebase true', 'git merge --abort or git rebase --abort']])}
''', kw=['cherry-pick conflict', 'stash pop conflict', 'modify/delete', 'revert conflict', 'pull conflict', 'git stash drop'])

K.lesson('web', 'Resolving in GitHub and GitLab', f'''
<p>When a pull request or merge request cannot merge, both sites can resolve simple conflicts in the browser.</p>
{table(['', 'GitHub pull request', 'GitLab merge request'], [
    ['Where', 'This branch has conflicts that must be resolved, then the Resolve conflicts button', 'Merge blocked: merge conflicts must be resolved, then Resolve conflicts'],
    ['How', 'An editor shows the file with markers. Edit, then Mark as resolved, then Commit merge.', 'Interactive mode with Use ours or Use theirs per hunk, or an inline editor for the whole file'],
    ['What it commits', 'A merge commit that merges the base branch into your head branch', 'A merge commit of the target branch into the source branch'],
    ['When the button is missing', 'Conflicts it cannot show in the browser, for example a deleted or renamed file', 'Conflicts it cannot parse, for example binary files or files that are too large'],
    ['Fallback', 'Resolve locally with the commands on this page, then push', 'Resolve locally, then push']])}
{note('The web resolver merges main into your branch. If your team requires a linear history or rebased branches, do not use it. Rebase locally instead and push with git push --force-with-lease.', 'warn')}
{scene('Dev and QA on the same config file', '<p>A developer raises the retry count in config.yml from 3 to 5 on a feature branch. A QA engineer lowers it to 2 on main so flaky tests fail faster. The pull request shows This branch has conflicts. The developer opens the file locally with zdiff3, sees the base was 3, talks to QA, and they agree on 3 for CI and 5 for production through an environment variable. One hand edited merge commit later, CI runs on the merged result and the pull request goes green.</p>')}
''', kw=['GitHub resolve conflicts', 'GitLab resolve conflicts', 'pull request conflicts', 'merge request conflicts', 'Mark as resolved', 'Use ours', 'Use theirs'])

K.lesson('fewer', 'Fewer and easier conflicts', f'''
{fxs(
    fx('Reuse recorded resolutions', '<code>git config --global rerere.enabled true</code>', 'Git records how you solved a conflict and applies the same fix if exactly that conflict returns.', key=True),
    fx('Keep branches short', '<code>git fetch</code> then <code>git rebase origin/main</code> often', 'Small and frequent integration means small conflicts.'),
    fx('Show the base', '<code>git config --global merge.conflictStyle zdiff3</code>', 'You see what both sides started from.'),
    fx('Find leftovers', '<code>git diff --check</code>', 'Reports left over conflict markers before you commit.', key=True))}
{sh('rerere at work: the second time the same conflict happens', """git config rerere.enabled true
git merge feature
# resolve by hand to colour: purple, git add, git commit
# later the same merge is redone, for example after a reset
git merge feature""", """Auto-merging shop.yml
CONFLICT (content): Merge conflict in shop.yml
Recorded preimage for 'shop.yml'
Automatic merge failed; fix conflicts and then commit the result.
Recorded resolution for 'shop.yml'.
Auto-merging shop.yml
CONFLICT (content): Merge conflict in shop.yml
Resolved 'shop.yml' using previous resolution.
Automatic merge failed; fix conflicts and then commit the result.""")}
<p>Note that rerere fixes the file but still leaves it unstaged, so you look at it, then git add and commit as usual.</p>
{steps('A calm routine for any conflict', [
    'Run git status. Read which operation is in progress and which files are unmerged.',
    'For each file, read ours, theirs and, with zdiff3, the base. Ask who made each change and why.',
    'Pick a way: edit by hand, take one side, or use a tool. Delete every marker line.',
    'Run git diff --check, then build and run the tests locally.',
    eq('git add the files, then git commit, or git rebase --continue, or git cherry-pick --continue')])}
{ladder(
    '<p>Two people changed the same sentence of a shared story in two different ways. Git will not guess which one is right, so it shows both and asks you to choose or write a new sentence.</p>',
    '<p>A conflict happens when both sides of a three way merge change overlapping lines differently. Git writes markers into the file and keeps base, ours and theirs as index stages 1, 2 and 3. git add collapses them to stage 0.</p>',
    '<p>The merge is line based. Adjacent edits form one hunk, so changes that touch each other clash even if they are logically separate. During a rebase the replayed commit is theirs. rerere stores a preimage and postimage keyed by the conflict text and replays the fix later.</p>',
    '<p>Research on structured merge parses files into syntax trees to avoid false conflicts, for example two methods added at the same place, and empirical studies of open source projects find that a noticeable share of merges are textual conflicts, while some clean merges still contain semantic conflicts that only tests reveal.</p>')}
''', kw=['rerere', 'git diff --check', 'conflict routine', 'fewer conflicts', 'zdiff3', 'structured merge'])

K.quiz('e', 'What causes a content conflict?', ['Two branches changing different files', 'Two branches changing the same lines differently', 'Any merge with two parents', 'A push without pull'], 1, 'Same place, different text.', 'Only overlapping, different changes conflict.')
K.quiz('e', 'Both branches change line 2 to exactly colour: green. What happens on merge?', ['Conflict', 'No conflict, the line is colour: green', 'Git keeps both lines', 'The merge is refused'], 1, 'Same change.', 'Identical changes on both sides merge cleanly.')
K.quiz('e', 'During git merge feature on main, what is between <<<<<<< HEAD and =======?', ['theirs', 'ours, the main version', 'the base', 'the stash'], 1, 'HEAD is the current branch.', 'HEAD is main, so it is ours.')
K.quiz('e', 'Which command tells Git a conflicted file is resolved?', ['git resolve', 'git add', 'git fix', 'git merge --done'], 1, 'Stage it.', 'git add replaces the three stages with stage 0.')
K.quiz('m', 'In git ls-files -s during a conflict, stage 3 holds', ['the base', 'ours', 'theirs', 'the resolved file'], 2, '1, 2, 3.', '1 base, 2 ours, 3 theirs.')
K.quiz('m', 'You are rebasing feature onto main and want to keep your feature change for a file. Which command?', ['git checkout --ours', 'git checkout --theirs', 'git merge -X ours', 'git rebase --skip'], 1, 'Labels swap in a rebase.', 'During a rebase your replayed commit is theirs.')
K.quiz('m', 'What does git merge -X theirs feature do?', ['Takes the whole feature tree', 'Resolves each clashing hunk with feature\'s side and still merges everything else', 'Aborts on conflict', 'Rebases'], 1, 'An option, not a strategy.', 'Only clashing hunks follow theirs.')
K.quiz('m', 'After a conflicting git stash pop and resolving the file, what else should you do?', ['git stash pop again', 'git stash drop, because the entry was kept', 'git commit --continue', 'Nothing'], 1, 'Git kept the entry.', 'The stash entry is kept in case you need it again.')
K.quiz('m', 'Which command finishes a rebase after resolving?', ['git commit', 'git rebase --continue', 'git rebase --done', 'git merge --continue'], 1, 'Continue.', 'add, then git rebase --continue.')
K.quiz('h', 'A modify/delete conflict on old.txt. You want to keep the edited file. What do you run before committing?', ['git rm old.txt', 'git add old.txt', 'git checkout --ours old.txt', 'Nothing'], 1, 'Keep means add.', 'git add keeps it, git rm confirms the delete.')
K.quiz('h', 'You resolved shop.yml wrongly but have not committed. How do you get the markers back?', ['git reset --hard', 'git checkout -m shop.yml', 'git stash', 'git rebase --skip'], 1, 'Recreate.', 'It prints Recreated 1 merge conflict.')
K.quiz('h', 'What does merge.conflictStyle zdiff3 add to the markers?', ['Line numbers', 'The base version between ||||||| and =======', 'Author names', 'Nothing'], 1, 'Base.', 'You see what both sides started from.')
K.quiz('x', 'A feature branch with 6 commits is rebased onto main and 3 of them touch the clashing line. Up to how many times can the rebase stop?', ['1', '3', '6', '0'], 1, 'One replay per commit.', 'Each commit that clashes stops the rebase once.')

K.calc('e', 'A file has 10 lines. main changes lines 2 and 8. feature changes lines 5 and 8, and its line 8 differs from main. How many conflict hunks?', '1', 'Only line 8 is changed by both.',
       ['Line 2: only main changed it, taken.', 'Line 5: only feature changed it, taken.', eq('Line 8: changed differently on both sides, so 1 hunk')], check=1)
K.calc('e', 'How many marker lines does Git write for one conflict hunk with the default merge style?', '3', 'Start, middle, end.',
       ['<<<<<<< HEAD starts ours.', '======= separates the sides.', eq('>>>>>>> feature ends it, so 3 marker lines')], check=3)
K.calc('m', 'With zdiff3, how many marker lines does one conflict hunk have?', '4', 'One more for the base.',
       ['The three default markers stay.', '||||||| starts the base section.', eq('3 + 1 = 4')], check=4)
K.calc('m', 'During a conflict on one file, git ls-files -s shows 3 entries for it. How many entries does it show after git add?', '1', 'Stages 1, 2, 3 become 0.',
       ['Base, ours, theirs: 3 entries at stages 1, 2 and 3.', 'git add writes the resolved file at stage 0 and removes the others.', eq('1 entry')], check=1)
K.calc('m', 'A merge stops with 4 conflicted files. You run git checkout --theirs on 2 of them and edit the other 2 by hand. How many files must you git add before git commit works?', '4', 'Every unmerged path.',
       ['checkout --theirs writes the file but does not stage it.', 'Hand edits also need staging.', eq('2 + 2 = 4')], check=4)
K.calc('h', 'A branch with 8 commits is rebased. Commits 2, 5 and 7 clash with main. You resolve commit 2, skip commit 5, and resolve commit 7. How many commits does the rebased branch have?', '7', 'skip drops one.',
       ['8 commits are replayed.', 'git rebase --skip drops commit 5.', eq('8 minus 1 = 7')], check=7)
K.calc('h', 'With rerere on, the same conflict appears 5 times over a week of rebases. How many times do you resolve it by hand?', '1', 'Recorded once.',
       ['The first time Git records preimage and resolution.', 'The next 4 times it reports Resolved using previous resolution.', eq('1 by hand, 4 reused')], check=1)

K.must('Why it happens', 'Both sides of a three way merge changed the same or touching lines differently. The same change on both sides is not a conflict.')
K.must('What Git writes', 'Markers <<<<<<< ours ======= theirs >>>>>>> in the file, and stages 1 base, 2 ours, 3 theirs in the index. git add collapses them to stage 0.')
K.must('Six ways out', 'Edit by hand, checkout --ours or --theirs, merge -X ours or -X theirs, git mergetool, or abort. Then git add and finish.')
K.must('Rebase swaps labels', 'During a rebase HEAD is the branch you rebase onto, and theirs is your own commit. Finish with git rebase --continue.')
K.must('Finish or back out', 'merge, rebase, cherry-pick and revert each have --continue and --abort. After stash pop, drop the entry yourself.')
K.must('Check before committing', 'git diff --check finds leftover markers. Run the tests, because a clean text merge can still be wrong.')

T = K.topic(
    slug='merge-conflicts', topic='conflicts', step=(2, 'Branching and merging', 'git-branch', 'Branches as pointers, fast-forward and three way merges, conflicts, rebase, interactive rebase and cherry-pick.', 'Intermediate'),
    title='Merge conflicts from start to finish', short='Merge conflicts', badge='2.4', minutes=50, added='2026-11-04',
    lead='Watch one conflict appear step by step, see exactly what Git writes, and resolve it six different ways, including during a rebase.',
    desc='How conflicts arise, conflict markers and index stages, zdiff3, resolving by hand, checkout --ours and --theirs, -X ours and -X theirs, mergetool, abort, rebase conflicts with swapped labels, cherry-pick, stash pop and modify/delete conflicts, the GitHub and GitLab web resolvers, and rerere.',
    summary='One end to end conflict animation and six ways to resolve it, with real Git output for every step.',
    keywords=['merge conflict', 'resolve conflict', 'conflict markers', 'checkout --ours', 'checkout --theirs', 'mergetool', 'rebase conflict', 'rerere', 'zdiff3'],
    recap='<p>A conflict is Git asking you to decide where both sides changed the same lines. Read ours, theirs and the base, pick a way out, delete the markers, git add, and finish the operation.</p>')
