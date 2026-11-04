# Chapter 4.3: power tools. git bisect (manual and run), git worktree, submodules, hooks (client and server,
# core.hooksPath, --no-verify, the pre-commit framework), git grep, sparse checkout, signing commits and tags with SSH or
# GPG, git archive. Sources: Pro Git 7.5, 7.10, 7.11, 8.3, git-bisect, git-worktree, git-submodule, githooks,
# git-sparse-checkout, git-commit -S manuals, actions/checkout README (submodules input). Terminal output was captured
# from real runs with Git 2.43. The xz utils facts come from the public reports on CVE-2024-3094.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from gitkit import sh, flow, file

K = Kit()

K.lesson('bisect', 'git bisect: find the commit that broke it', f'''
<p>The tests passed at release v1.0 and fail today, 15 commits later. Reading every diff is slow. <b>git bisect</b> checks out the commit in the middle and asks you whether it is good or bad. Each answer throws away half of the suspects, so even 1000 commits need only about 10 tests.</p>
{viz('bisect')}
{sh('Bisect by hand', """git bisect start
git bisect bad              # the current commit is broken
git bisect good v1.0        # this tag was fine
# Git checks out a commit in the middle. Test it, then say:
git bisect good             # or: git bisect bad, or: git bisect skip
# repeat until Git prints the first bad commit
git bisect reset            # go back to where you started""")}
{sh('Let a script do the testing', """git bisect start HEAD v1.0
git bisect run sh test.sh""", """Bisecting: 7 revisions left to test after this (roughly 3 steps)
[9826dda] change 8
running 'sh' 'test.sh'
Bisecting: 3 revisions left to test after this (roughly 2 steps)
...
f026a7d2dc1f0bcf5a9028611556ac4bb588dea5 is the first bad commit
    change 11
bisect found first bad commit""", 'Real output, shortened: 4 tests for 15 commits')}
{table(['Exit code of the script', 'Meaning for bisect run'], [
    ['0', 'good'], ['1 to 127, except 125', 'bad'], ['125', 'cannot test this commit, skip it'], ['above 127', 'stop bisecting']])}
{note('Bisect works best when every commit builds and passes tests on its own. Huge commits that mix many changes also make the answer less useful. This is one more reason for small, atomic commits.', 'tip')}
''', kw=['git bisect', 'bisect run', 'binary search', 'first bad commit', 'bisect skip', 'exit code 125', 'regression'])

K.lesson('worktree', 'worktree and submodules', f'''
<p><b>git worktree</b> gives one repository several working folders, each on its own branch. You can fix a bug on a hotfix branch in one folder while a long build or test run continues in another, without stashing or cloning again.</p>
{sh('A second folder for a hotfix', """git worktree add ../hotfix -b hotfix v1.0
git worktree list
# when done
git worktree remove ../hotfix""", """Preparing worktree (new branch 'hotfix')
HEAD is now at 45a81bb change 1
/work/calc-app  cac7ede [main]
/work/hotfix    45a81bb [hotfix]""", 'Real output, paths shortened')}
{note('A branch can be checked out in only one worktree at a time. All worktrees share the same .git objects, so a commit made in one is visible in the others at once.', 'tip')}
<p>A <b>submodule</b> puts another repository inside yours at a fixed commit, for example a shared library. The parent repository does not store the library files. It stores the library URL in <code>.gitmodules</code> and one commit id for the folder.</p>
{file('.gitmodules', """[submodule "libs/shared"]
	path = libs/shared
	url = https://github.com/OWNER/shared.git""", {2: 'Where the other repository appears in your working tree.', 3: 'Where to clone it from. The exact commit is stored in the parent commit, not here.'}, lang='text')}
{fxs(
    fx('Add and clone', '<code>git submodule add &lt;url&gt; &lt;path&gt;</code>, <code>git clone --recurse-submodules &lt;url&gt;</code>', 'A plain clone leaves submodule folders empty.', key=True),
    fx('After a pull', '<code>git submodule update --init --recursive</code>', 'Checks out the commit each submodule is pinned to.', key=True),
    fx('In CI', '<code>actions/checkout</code> with <code>submodules: recursive</code>, GitLab variable <code>GIT_SUBMODULE_STRATEGY: recursive</code>', 'Both platforms skip submodules unless asked.'))}
{deep('Submodule or something else', '<p>Submodules pin an exact version, which is safe, but every update needs a commit in the parent and every clone needs the extra flag. git subtree copies the other project into a folder as normal files with history, so clones need nothing special. For libraries that have releases, a package manager (pip, npm, Maven) is usually the simplest choice.</p>')}
''', kw=['git worktree', 'worktree add', 'worktree list', 'submodule', '.gitmodules', 'recurse-submodules', 'submodule update', 'GIT_SUBMODULE_STRATEGY', 'subtree'])

K.lesson('hooks', 'Hooks: scripts Git runs for you', f'''
<p>A <b>hook</b> is a script that Git runs at a fixed moment, such as before a commit is made or before a push is sent. If a pre hook exits with a code other than 0, Git stops the action. Pick a hook in the animation and make it fail.</p>
{viz('hooks')}
{file('.git/hooks/pre-commit', """#!/bin/sh
# Block commits that still contain debug prints
if git diff --cached | grep -q 'print("DEBUG'; then
  echo "Remove DEBUG prints before committing"
  exit 1
fi""", {1: 'A hook is any executable file with the exact hook name. chmod +x is required on macOS and Linux.', 3: 'git diff --cached shows what is about to be committed.', 5: 'A non zero exit code stops the commit.'}, lang='text')}
{sh('The hook in action', """git commit -am "try"
echo $?
git commit -am "try" --no-verify""", """Remove DEBUG prints before committing
1""", 'Real output: --no-verify skips the hook')}
{table(['Hook', 'Runs', 'Typical use'], [
    ['pre-commit', 'before the commit message is asked for', 'format code, lint, find secrets'],
    ['commit-msg', 'after the message is written', 'check Conventional Commits format'],
    ['pre-push', 'before objects are sent', 'run fast unit tests'],
    ['pre-receive and update', 'on the server, when a push arrives', 'reject pushes that break rules (GitLab server hooks, GitHub uses rulesets instead)'],
    ['post-receive', 'on the server, after the push', 'notify, start deployments']])}
{note('Files in .git/hooks are not committed and not cloned, and anyone can skip them with --no-verify. Use hooks for fast feedback on your laptop, and run the same checks again in CI, which no one can skip.', 'warn')}
{deep('Sharing hooks with the team', '<p>Commit the scripts to a folder such as .githooks and ask everyone to run git config core.hooksPath .githooks once. Many teams use the pre-commit framework instead: a .pre-commit-config.yaml file lists checks by repository and version, pre-commit install writes the hook, and the same command runs in CI with pre-commit run --all-files.</p>')}
''', kw=['git hooks', 'pre-commit', 'commit-msg', 'pre-push', 'pre-receive', 'post-receive', 'no-verify', 'core.hooksPath', 'pre-commit framework'])

K.lesson('more', 'grep, sparse checkout, signing and archive', f'''
{fxs(
    fx('Search tracked files', '<code>git grep -n "def add"</code>', 'Faster than grep on big repositories and ignores untracked junk. Add a commit or tag to search an old version: git grep -n TODO v1.0.', key=True),
    fx('Work on part of a monorepo', '<code>git sparse-checkout set app tests</code>', 'Only these folders appear in the working tree. git sparse-checkout disable brings everything back.'),
    fx('Sign a commit or tag', '<code>git commit -S</code>, <code>git tag -s v1.0.0</code>', 'Proves who made it. Set commit.gpgsign true to sign every commit.', key=True),
    fx('Export a release', '<code>git archive --format=zip -o calc-app.zip v1.0.0</code>', 'Writes the files of a tag or commit to a zip or tar, without the .git folder.'))}
{sh('Sign with your SSH key (Git 2.34 or newer)', """git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git commit -m "Signed change"
git log --show-signature -1""")}
<p>Add the same public key to GitHub or GitLab as a signing key, and the platform shows the commit as Verified. Anyone can type any name in user.name, so a signature is the only proof that a commit came from the key holder.</p>
{scene('the xz utils backdoor, 2024', '<p>In March 2024 Andres Freund noticed that SSH logins on a test system used more CPU than expected, and traced it to a backdoor in xz utils versions 5.6.0 and 5.6.1 (CVE-2024-3094). A maintainer account that had earned trust over about two years had added obfuscated binary test files to the repository, and the release tarballs contained a modified build script that was not in the Git repository at all. Lessons that teams took: build releases from the tagged Git commit inside CI, compare tarballs with the repository, review changes to build and test files carefully and sign tags.</p>')}
{ladder(
    '<p>bisect finds the bad commit by halving, worktree gives you extra folders, submodules pin another project, and hooks run checks at the right moment.</p>',
    '<p>bisect run uses exit codes (0 good, 125 skip, other 1 to 127 bad). Submodules are stored as a gitlink entry with mode 160000. Client hooks live in .git/hooks or core.hooksPath and can be skipped, server hooks cannot.</p>',
    '<p>Bisect needs about log2(n) tests. Sparse checkout in cone mode matches whole folders, which keeps it fast. Commit signatures are stored inside the commit object in a gpgsig header and cover the tree, parents, author and message.</p>',
    '<p>Software supply chain work (SLSA, Sigstore gitsign, reproducible builds) builds on these tools: signed commits and tags say who wrote the code, CI provenance says how the artifact was built from that exact commit.</p>')}
''', kw=['git grep', 'sparse-checkout', 'monorepo', 'signed commits', 'commit -S', 'gpg.format ssh', 'Verified', 'git archive', 'xz backdoor', 'supply chain'])

K.quiz('e', 'What does git bisect help you find?', ['A lost branch', 'The first commit that introduced a bug', 'The biggest file', 'Merge conflicts'], 1, 'Binary search.', 'Mark good and bad, Git halves the range each time.')
K.quiz('e', 'Which hook runs before Git creates a commit?', ['post-commit', 'pre-commit', 'pre-push', 'post-receive'], 1, 'Before.', 'It can stop the commit by exiting non zero.')
K.quiz('e', 'Which flag skips the pre-commit and commit-msg hooks?', ['--force', '--no-verify', '--quiet', '--skip'], 1, 'Verify.', 'That is why CI must repeat the checks.')
K.quiz('m', 'About how many tests does bisect need for 1000 commits?', ['1000', '100', 'about 10', '2'], 2, 'Halving.', '2 to the power 10 is 1024.')
K.quiz('m', 'In git bisect run, which exit code means skip this commit?', ['0', '1', '125', '128'], 2, 'Special value.', '125 marks a commit that cannot be tested.')
K.quiz('m', 'You cloned a repository with submodules and their folders are empty. Fix?', ['git pull', 'git submodule update --init --recursive', 'git fetch --all', 'git reset --hard'], 1, 'Init them.', 'Or clone with --recurse-submodules next time.')
K.quiz('m', 'Why are client hooks not enough to enforce rules?', ['They are slow', 'They are not cloned and can be skipped with --no-verify', 'They only run on Windows', 'They need admin rights'], 1, 'Local only.', 'Enforce in CI and branch protection.')
K.quiz('h', 'Can the same branch be checked out in two worktrees at once?', ['Yes', 'No, Git refuses', 'Only with --force on add', 'Only for main'], 1, 'One place each.', 'Git refuses by default because the two folders would fight over the branch.')
K.quiz('h', 'What does the parent repository store for a submodule folder?', ['All its files', 'A commit id (a gitlink), plus the URL in .gitmodules', 'A zip file', 'Nothing'], 1, 'Pointer.', 'The entry has mode 160000 in the tree.')
K.quiz('x', 'Why is a signed commit stronger evidence than the author name?', ['Names are encrypted', 'Anyone can set user.name, but only the key holder can make a valid signature', 'GitHub checks names', 'Signatures hide the code'], 1, 'Proof.', 'Platforms show Verified when the key is registered to the account.')

K.calc('e', 'Bisect over 16 commits (1 good, 16 bad). How many tests does the halving need?', '4', 'log2 of 16.',
       ['Each test halves the range of suspects.', '16, 8, 4, 2, 1.', eq('log2(16) = 4 tests')], check=4)
K.calc('e', 'With 1024 suspect commits, how many tests in the worst case?', '10', '2 to the 10.',
       ['2¹⁰ = 1024.', 'Each test halves the suspects.', eq('10 tests')], check=10)
K.calc('m', 'Good is commit 1, bad is commit 16. The first test picks (1 + 16) // 2. Which commit is that?', '8', 'Integer halving.',
       ['1 + 16 = 17.', '17 // 2 = 8.', eq('test commit 8')], check=8)
K.calc('m', 'Doubling the number of suspect commits adds how many bisect tests?', '1', 'One more halving.',
       ['log2(2n) = log2(n) + 1.', 'So one extra test.', eq('+1 test')], check=1)
K.calc('h', 'bisect run: the script exits 0, 0, 1, 125, 1. How many commits were marked bad?', '2', 'Code 125 is skip.',
       ['0 means good: 2 commits.', '125 means skip: 1 commit.', eq('1 means bad: 2 commits')], check=2)
K.calc('h', 'A repository has 3 submodules and one of them has 2 submodules of its own. With --recurse-submodules, how many repositories are cloned in total, counting the parent?', '6', 'Count every level.',
       ['Parent: 1.', 'First level submodules: 3.', eq('Nested: 2, total 1 + 3 + 2 = 6')], check=6)

K.must('git bisect', 'start, bad, good <tag>, then good or bad or skip until the first bad commit, then reset. bisect run script: 0 good, 125 skip, 1 to 127 bad. About log2(n) tests.')
K.must('worktree', 'git worktree add <path> <branch> gives another folder on another branch, sharing one .git. One branch per worktree.')
K.must('Submodules', 'Pinned commit of another repository. .gitmodules holds the URL. Clone with --recurse-submodules or run submodule update --init --recursive. CI needs submodules: recursive or GIT_SUBMODULE_STRATEGY.')
K.must('Hooks', 'pre-commit, commit-msg, pre-push on the client (skippable with --no-verify, not cloned), pre-receive and post-receive on the server. Share with core.hooksPath or the pre-commit framework, and repeat checks in CI.')
K.must('More tools', 'git grep searches tracked files, sparse-checkout limits folders, commit -S and tag -s sign (SSH or GPG), git archive exports a tag without .git.')

T = K.topic(
    slug='power-tools', topic='power-tools', step=(4, 'Remotes and teamwork', 'git-team', 'Share work through GitHub and GitLab: clone, fetch, pull and push, pick a branching workflow, review through pull requests, and use the power tools teams rely on.', 'Intermediate'),
    title='Power tools: bisect, worktree, submodules, hooks and signing', short='Power tools', badge='4.3', minutes=50, added='2026-11-02',
    lead='Find the commit that broke the build in minutes, work on two branches at once, include other repositories, run checks automatically at commit time and prove who wrote a commit.',
    desc='git bisect by hand and with bisect run and its exit codes, git worktree, submodules and .gitmodules, submodules in GitHub Actions and GitLab CI, client and server hooks, core.hooksPath and the pre-commit framework, git grep, sparse checkout, signing commits and tags with SSH keys, git archive, and the xz utils backdoor.',
    summary='bisect, worktree, submodules, hooks, grep, sparse checkout, signed commits and archive.',
    keywords=['git bisect', 'bisect run', 'git worktree', 'submodule', 'git hooks', 'pre-commit', 'signed commits', 'sparse checkout'],
    recap='<p>bisect halves the suspects, worktree adds folders, submodules pin other repositories, hooks give early feedback that CI must repeat, and signatures prove authorship.</p>')
