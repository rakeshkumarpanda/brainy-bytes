# Chapter 4.1: remotes. clone, remote, fetch, pull, push, upstream tracking, ahead and behind, divergent branches,
# force-with-lease and force-if-includes, prune, refspecs, shallow and partial clones, HTTPS and SSH authentication.
# Sources: Pro Git 2.5, 3.5, 10.5, git-clone, git-fetch, git-pull, git-push, git-remote manuals, GitHub docs on
# token authentication. Terminal output was captured from real runs with Git 2.43.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow, file

K = Kit()

K.code('aheadbehind', r'''
# How git status counts "ahead" and "behind": commits on one side that the other side cannot reach
parents = {
    "A": [], "B": ["A"], "C": ["B"],          # shared history
    "D": ["C"], "E": ["D"],                   # your two local commits
    "F": ["C"],                               # a teammate pushed one commit
}

def reach(tip):
    seen, todo = set(), [tip]
    while todo:
        c = todo.pop()
        if c not in seen:
            seen.add(c)
            todo.extend(parents[c])
    return seen

mine, theirs = reach("E"), reach("F")
print("ahead :", sorted(mine - theirs))
print("behind:", sorted(theirs - mine))
print(f"[origin/main: ahead {len(mine - theirs)}, behind {len(theirs - mine)}]")
''')

K.lesson('clone', 'Remotes and git clone', f'''
<p>Until now every commit lived only on your laptop. A <b>remote</b> is another copy of the same repository, usually on a server such as GitHub or GitLab, that the team shares. Because Git is distributed, your clone holds the full history, and the remote is simply the copy everyone agrees to meet at.</p>
{flow(('git clone URL', 'downloads every commit, creates a remote called origin and checks out the default branch'),
      ('git fetch', 'asks origin what is new and downloads it, without touching your files'),
      ('git pull', 'fetch, then merge or rebase the new commits into your branch'),
      ('git push', 'uploads your new commits and moves the branch on the server'))}
{sh('Clone, then look at what you got', """git clone https://github.com/OWNER/calc-app.git
cd calc-app
git remote -v
git branch -a""", """origin  https://github.com/OWNER/calc-app.git (fetch)
origin  https://github.com/OWNER/calc-app.git (push)
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/main""")}
{table(['Name', 'What it is', 'Who moves it'], [
    ['<code>main</code>', 'your local branch', 'you, when you commit, merge or reset'],
    ['<code>origin/main</code>', 'a <b>remote-tracking branch</b>: your last known position of main on origin', 'only git fetch, pull and push'],
    ['<code>origin</code>', 'a short name for the server URL, stored in .git/config', 'git remote add, rename, set-url, remove']])}
{fxs(
    fx('Clone', '<code>git clone &lt;url&gt; [folder]</code>', 'Creates origin, copies all branches as origin/*, checks out the default branch and sets it to track origin.', key=True),
    fx('Manage remotes', '<code>git remote -v</code>, <code>git remote add upstream &lt;url&gt;</code>, <code>git remote set-url origin &lt;url&gt;</code>', 'A repository can have many remotes. upstream is the usual name for the original project when you work on a fork.'),
    fx('Fast clones for CI', '<code>git clone --depth 1</code>, <code>git clone --filter=blob:none</code>', '--depth 1 is a shallow clone with only the newest commit. --filter=blob:none is a partial clone that fetches file contents only when needed.'))}
{note('origin/main does not update by itself. It is a snapshot from your last fetch. If git status says "up to date", it means up to date with that snapshot, not with the server right now.', 'warn')}
{deep('HTTPS or SSH', '<p>Both work. With HTTPS, GitHub stopped accepting account passwords for Git operations on 13 August 2021, so you use a personal access token or a credential manager that signs you in through the browser. With SSH you create a key pair with ssh-keygen -t ed25519, add the public key to your account, and use a URL like git@github.com:OWNER/calc-app.git. GitLab works the same way with personal access tokens or SSH keys.</p>')}
''', kw=['remote', 'git clone', 'origin', 'remote-tracking branch', 'origin/main', 'git remote', 'upstream', 'shallow clone', 'partial clone', 'ssh key', 'personal access token'])

K.lesson('sync', 'fetch, pull and push, ahead and behind', f'''
<p>Two people clone the same repository. Asha makes a commit, Ben makes a different commit and pushes first. Now the histories have <b>diverged</b>. Play with the animation: pick how many commits each side has and what you run.</p>
{viz('remotes')}
{sh('Asha tries to push after Ben', 'git push', """To github.com:OWNER/calc-app.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'github.com:OWNER/calc-app.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.""", 'Real output (Git 2.43)')}
<p>A push is only accepted when it is a <b>fast forward</b>: the server branch must be an ancestor of what you push, so no one's commit is thrown away. Asha first fetches and looks.</p>
{sh('Fetch, then compare', """git fetch
git status
git branch -vv""", """On branch main
Your branch and 'origin/main' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

* main 0d66c75 [origin/main: ahead 1, behind 1] asha work""")}
{code('aheadbehind')}
{sh('git pull with diverged branches and no setting', 'git pull', """hint: You have divergent branches and need to specify how to reconcile them.
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
fatal: Need to specify how to reconcile divergent branches.""", 'Real output, shortened')}
{table(['Command', 'What happens to your branch', 'Good when'], [
    ['<code>git pull --no-rebase</code>', 'fetch, then a merge commit joins the two lines', 'you want history to show exactly what happened'],
    ['<code>git pull --rebase</code>', 'fetch, then your local commits are replayed on top of origin/main', 'you want a straight line and your commits are not pushed yet'],
    ['<code>git pull --ff-only</code>', 'fetch, then move only if no one diverged, otherwise stop', 'a branch you never commit to directly, such as main on a deploy server']])}
{note('Pick one default once: git config --global pull.rebase true is a popular choice for feature work. Then git pull followed by git push is the everyday rhythm.', 'tip')}
''', kw=['git fetch', 'git pull', 'git push', 'fast forward', 'rejected', 'fetch first', 'diverged', 'ahead', 'behind', 'branch -vv', 'pull.rebase', 'ff-only'])

K.lesson('tracking', 'Upstream branches, force pushes and pruning', f'''
<p>Each local branch can have an <b>upstream</b>: the remote-tracking branch it compares with and pulls from. Clone sets it for the default branch. For a new branch you set it on the first push.</p>
{sh('Publish a new branch', """git switch -c feature/login
git commit -am "Add login form"
git push -u origin feature/login""", """branch 'feature/login' set up to track 'origin/feature/login'.""", 'The last line of the output')}
{fxs(
    fx('Set upstream', '<code>git push -u origin &lt;branch&gt;</code>', 'After this, plain git push and git pull know where to go. -u is short for --set-upstream.', key=True),
    fx('Safer force push', '<code>git push --force-with-lease</code>', 'Overwrites the server branch only if it still points where your origin/branch says. Otherwise it is rejected with stale info.', key=True),
    fx('Delete a remote branch', '<code>git push origin --delete feature/login</code>', 'Removes the branch on the server, for example after the pull request merged.'),
    fx('Clean up old remote-tracking branches', '<code>git fetch --prune</code>', 'Removes origin/* names whose branch was deleted on the server. git config --global fetch.prune true does it on every fetch.'))}
<p>After a rebase or amend of a branch you already pushed, a normal push is rejected because it is not a fast forward. <code>--force</code> would overwrite whatever is on the server, including a teammate's new commit. <code>--force-with-lease</code> checks first.</p>
{sh('Ben pushed while Asha was rebasing', 'git push --force-with-lease', """To github.com:OWNER/calc-app.git
 ! [rejected]        main -> main (stale info)
error: failed to push some refs to 'github.com:OWNER/calc-app.git'""", 'Real output: the lease protected Ben\'s commit')}
{note('The lease compares with origin/branch. If an editor or a script runs git fetch in the background, origin/branch is already updated and the lease passes without you ever seeing Ben\'s work. Git 2.30 added --force-if-includes, used together with --force-with-lease, to also check that you had integrated what you fetched.', 'warn')}
{scene('one force push, many repositories', '<p>In November 2013 a contributor to the Jenkins project ran git push --force while push.default was set to matching, so Git force pushed every local branch, many of them weeks old, to more than a hundred of the project\'s GitHub repositories at once. Git 2.0 later changed the default of push.default to simple, which pushes only the current branch. The project recovered the lost commits from the reflogs of developers who had fresh clones and from GitHub support. This is why most teams now forbid force pushes to main with branch protection, and allow them only on personal feature branches with --force-with-lease.</p>')}
{deep('Refspecs: the rule behind fetch and push', '<p>.git/config holds the line <code>fetch = +refs/heads/*:refs/remotes/origin/*</code>. Read it as source:destination. Every branch on the server (refs/heads/anything) is copied to refs/remotes/origin/anything on your side. The leading + allows the copy to move even when it is not a fast forward. git push origin feature/login is short for the refspec refs/heads/feature/login:refs/heads/feature/login. You can push one branch to another name, as in git push origin HEAD:refs/heads/test-run, which CI scripts sometimes use.</p>')}
''', kw=['upstream', 'set-upstream', 'push -u', 'force-with-lease', 'force-if-includes', 'stale info', 'push --delete', 'fetch --prune', 'fetch.prune', 'refspec', 'refs/remotes'])

K.lesson('teamday', 'A day with a remote, step by step', f'''
{steps('Asha and Ben share calc-app', [
    'Morning: <code>git switch main</code> then <code>git pull</code>. Asha starts from the newest main.',
    '<code>git switch -c feature/percent</code>, edit, <code>git commit -am "Add percent()"</code>.',
    '<code>git push -u origin feature/percent</code>. The branch now exists on the server, and CI starts testing it.',
    'She opens a pull request. Ben reviews it and asks for a change. She commits again and runs plain <code>git push</code>.',
    'Meanwhile main moved. She runs <code>git fetch</code> then <code>git rebase origin/main</code>, fixes one conflict, and pushes with <code>git push --force-with-lease</code>.',
    'The pull request is merged on the server. She runs <code>git switch main</code>, <code>git pull</code>, <code>git branch -d feature/percent</code> and <code>git fetch --prune</code>.'])}
{ladder(
    '<p>The remote is the shared copy. fetch looks, pull brings the changes in, push sends yours out. The server only accepts a push that does not throw away anyone\'s commits.</p>',
    '<p>origin/main is a remote-tracking ref updated only by network commands. Ahead and behind are counts of commits reachable from one tip and not the other. pull is fetch plus merge or rebase, chosen by pull.rebase or pull.ff.</p>',
    '<p>The fetch protocol negotiates which objects each side already has and sends one packfile with the rest. Refspecs map server refs to local refs. --force-with-lease is a compare and swap on the remote ref, the same idea used in lock free programming.</p>',
    '<p>Large monorepos use partial clone (--filter=blob:none), sparse checkout and protocol version 2, which lets the client ask only for the refs it needs. Git 3.0 plans to make SHA-256 and reftable defaults, which affects how servers and clients interoperate.</p>')}
''', kw=['daily workflow', 'pull request', 'rebase origin/main', 'branch -d', 'protocol v2', 'packfile'])

K.quiz('e', 'What name does git clone give the server it cloned from?', ['main', 'origin', 'upstream', 'remote'], 1, 'Default name.', 'You can rename it, but origin is the default.')
K.quiz('e', 'Which command downloads new commits but never changes your working files?', ['git pull', 'git fetch', 'git merge', 'git checkout'], 1, 'Look, do not touch.', 'fetch only updates remote-tracking branches such as origin/main.')
K.quiz('e', 'git pull is', ['git push in reverse', 'git fetch followed by a merge or rebase', 'git clone again', 'git reset'], 1, 'Two steps.', 'pull = fetch + integrate.')
K.quiz('m', 'git push says "rejected (fetch first)". What does it mean?', ['Your password is wrong', 'The server has commits you do not have, so your push is not a fast forward', 'The branch is protected', 'The network failed'], 1, 'Someone was faster.', 'Fetch, integrate, then push again.')
K.quiz('m', 'What does git push -u origin feature/x add compared with a plain push?', ['It uploads tags', 'It sets origin/feature/x as the upstream of your branch', 'It forces the push', 'It deletes the remote branch'], 1, 'u for upstream.', 'Later git push and git pull need no arguments.')
K.quiz('m', 'git branch -vv shows [origin/main: ahead 2, behind 3]. What is true?', ['You have 2 commits the server lacks and the server has 3 you lack', 'You are 2 commits behind', 'You must clone again', 'Nothing to do'], 0, 'Read it literally.', 'The branches have diverged.')
K.quiz('m', 'Which pull mode refuses to create a merge commit and stops if branches diverged?', ['--rebase', '--no-rebase', '--ff-only', '--squash'], 2, 'Fast forward or nothing.', 'Good for branches you never commit to directly.')
K.quiz('h', 'Why is --force-with-lease safer than --force?', ['It is faster', 'It only overwrites the server branch if it still points where your origin/branch says', 'It makes a backup', 'It asks the team'], 1, 'Compare first.', 'Otherwise it is rejected with stale info.')
K.quiz('h', 'A teammate deleted feature/old on the server, but you still see origin/feature/old. Fix?', ['git branch -D origin/feature/old', 'git fetch --prune', 'git pull --rebase', 'git push --delete'], 1, 'Prune.', 'fetch --prune removes stale remote-tracking branches.')
K.quiz('x', 'In fetch = +refs/heads/*:refs/remotes/origin/*, what does the leading + allow?', ['Pushing tags', 'Updating the destination even when it is not a fast forward', 'Fetching only new branches', 'Using SSH'], 1, 'Plus means force.', 'Needed because branches on the server can be rewritten.')

K.calc('e', 'Your branch has commits D and E that origin/main lacks. origin/main has F that you lack. How many commits ahead are you?', '2', 'Count your side only.',
       ['Commits reachable from main and not from origin/main: D, E.', 'Commits reachable from origin/main and not from main: F.', eq('ahead = 2, behind = 1')], check=2)
K.calc('e', 'You are ahead 0, behind 4. You run git pull --ff-only. How many commits move into your branch?', '4', 'No divergence.',
       ['Ahead 0 means you have nothing the server lacks.', 'So a fast forward is possible.', eq('main moves forward by 4 commits')], check=4)
K.calc('m', 'Ahead 3, behind 2. You run git pull --rebase. How many of your commits are replayed with new ids?', '3', 'Only your commits move.',
       ['The 2 server commits come in unchanged.', 'Your 3 local commits are copied on top of them.', eq('3 new commit ids')], check=3)
K.calc('m', 'Ahead 3, behind 2. You run git pull --no-rebase. How many commits does main gain, including the merge commit?', '3', 'Server commits plus one.',
       ['The 2 server commits become part of your history.', 'A merge commit joins the two lines.', eq('2 + 1 = 3 new commits on main')], check=3)
K.calc('h', 'A shallow clone with --depth 1 of a repository with 5000 commits. How many commits does git log show?', '1', 'Only the tip.',
       ['--depth 1 fetches only the newest commit of each fetched branch.', 'Its parents are recorded as missing (grafted).', eq('git log shows 1 commit')], check=1)
K.calc('h', 'origin/main is at 7c1. Your lease expects 7c1. The server is at 9ab because Ben pushed. Is the push accepted? Answer 1 for yes, 0 for no.', '0', 'Compare and swap.',
       ['--force-with-lease compares the server value with the expected value.', '9ab is not 7c1.', eq('rejected (stale info), answer 0')], check=0)

K.assign('ab', 'm', 'Ahead and behind',
         '<p>Write <code>ahead_behind(parents, mine, theirs)</code>. parents maps a commit to the list of its parents. Return <code>[ahead, behind]</code>: the number of commits reachable from mine and not from theirs, and the other way round.</p>',
         '''
def ahead_behind(parents, mine, theirs):
    # your code here
    pass
''', [("ahead_behind({'A': [], 'B': ['A'], 'C': ['B'], 'D': ['B']}, 'C', 'D')", [1, 1]),
      ("ahead_behind({'A': [], 'B': ['A'], 'C': ['B']}, 'C', 'A')", [2, 0]),
      ("ahead_behind({'A': [], 'B': ['A'], 'C': ['A'], 'M': ['B', 'C']}, 'M', 'C')", [2, 0]),
      ("ahead_behind({'A': []}, 'A', 'A')", [0, 0])],
         '''
def reach(parents, tip):
    seen, todo = set(), [tip]
    while todo:
        c = todo.pop()
        if c not in seen:
            seen.add(c)
            todo.extend(parents[c])
    return seen

def ahead_behind(parents, mine, theirs):
    a, b = reach(parents, mine), reach(parents, theirs)
    return [len(a - b), len(b - a)]
''', 'Collect every commit reachable from each tip, then subtract the sets.', '<p>This is what git rev-list --left-right --count main...origin/main prints.</p>')
K.assign('refspec', 'h', 'Apply a fetch refspec',
         '<p>Write <code>map_ref(refspec, ref)</code> for refspecs like <code>+refs/heads/*:refs/remotes/origin/*</code>. Ignore a leading +. If the source pattern (with one *) matches ref, return the destination with the * replaced. Otherwise return None.</p>',
         '''
def map_ref(refspec, ref):
    # your code here
    pass
''', [("map_ref('+refs/heads/*:refs/remotes/origin/*', 'refs/heads/main')", 'refs/remotes/origin/main'),
      ("map_ref('+refs/heads/*:refs/remotes/origin/*', 'refs/heads/feature/x')", 'refs/remotes/origin/feature/x'),
      ("map_ref('refs/heads/*:refs/remotes/up/*', 'refs/tags/v1')", None),
      ("map_ref('refs/heads/main:refs/remotes/origin/main', 'refs/heads/main')", 'refs/remotes/origin/main')],
         '''
def map_ref(refspec, ref):
    src, dst = refspec.lstrip('+').split(':')
    if '*' not in src:
        return dst if ref == src else None
    pre, post = src.split('*')
    if ref.startswith(pre) and ref.endswith(post) and len(ref) >= len(pre) + len(post):
        mid = ref[len(pre):len(ref) - len(post)]
        return dst.replace('*', mid)
    return None
''', 'Split at the colon, then at the star. The part the star matched goes into the destination.', '<p>A refspec without a star maps one exact ref.</p>')

K.must('Remote basics', 'clone creates origin and origin/* remote-tracking branches. origin/main is your last known copy of the server branch, updated only by fetch, pull and push.')
K.must('Fetch, pull, push', 'fetch downloads and changes nothing else. pull = fetch + merge or rebase (pull.rebase, --ff-only). push is accepted only as a fast forward.')
K.must('Ahead and behind', 'ahead = commits only you have, behind = commits only the server has. Both above 0 means diverged.')
K.must('Upstream', 'git push -u origin <branch> sets tracking. git branch -vv shows it with ahead and behind counts.')
K.must('Force safely', 'Never force push shared branches. On your own branch use --force-with-lease (and --force-if-includes). fetch --prune removes stale origin/* names.')

T = K.topic(
    slug='remotes', topic='remotes', step=(4, 'Remotes and teamwork', 'git-team', 'Share work through GitHub and GitLab: clone, fetch, pull and push, pick a branching workflow, review through pull requests, and use the power tools teams rely on.', 'Intermediate'),
    title='Remotes: clone, fetch, pull and push', short='Remotes', badge='4.1', minutes=50, added='2026-11-02',
    lead='Share commits with a team: what origin and origin/main really are, why a push gets rejected, how to pull without surprises and how to force push without destroying a teammate\'s work.',
    desc='git clone, origin, remote-tracking branches, git remote, fetch versus pull, push and fast forwards, ahead and behind, divergent branches, pull.rebase and --ff-only, upstream tracking with push -u, force-with-lease and force-if-includes, prune, refspecs, shallow and partial clones, HTTPS tokens and SSH keys.',
    summary='Remotes and origin/main, fetch, pull and push, ahead and behind, upstreams, safe force pushes, prune and refspecs.',
    keywords=['git clone', 'origin', 'git fetch', 'git pull', 'git push', 'ahead behind', 'force-with-lease', 'refspec'],
    recap='<p>origin/main is your last known copy of the server. fetch looks, pull integrates, push sends a fast forward, and --force-with-lease is the only force push for shared work.</p>')
