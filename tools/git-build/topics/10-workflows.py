# Chapter 4.2: team workflows. GitHub flow, Gitflow, trunk based development, forking workflow, pull requests and
# merge requests, code review, merge methods on GitHub and GitLab, branch protection, CODEOWNERS, conventional commits.
# Sources: GitHub docs (about protected branches, about merge methods, about code owners), GitLab docs (protected
# branches, merge methods, auto merge and Pipelines must succeed, Code Owners), nvie.com "A successful Git branching
# model" (2010, with the 2020 note), trunkbaseddevelopment.com, conventionalcommits.org 1.0.0.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow, file, devqa

K = Kit()

K.code('conv', r'''
# Conventional Commits decide the next semantic version from the commit messages since the last tag
messages = [
    "fix(calc): divide by zero raises ValueError",
    "docs: explain the pipeline in README",
    "feat(calc): add percent()",
    "fix: round results to 10 places",
]

def kind(msg):
    head = msg.split(":")[0]
    if head.endswith("!") or "BREAKING CHANGE" in msg:
        return "major"
    if head.startswith("feat"):
        return "minor"
    if head.startswith("fix"):
        return "patch"
    return "none"

order = ["none", "patch", "minor", "major"]
best = "none"
for m in messages:
    k = kind(m)
    print(f"{k:6} <- {m}")
    if order.index(k) > order.index(best):
        best = k
print("next release bumps:", best)
''')

K.lesson('models', 'Four branching workflows', f'''
<p>Git lets you branch any way you like, so teams agree on a <b>workflow</b>: which branches live long, where new work starts and how it gets back. Pick one in the animation and watch the commits move.</p>
{viz('flows')}
{table(['Workflow', 'Long lived branches', 'Best for', 'Main risk'], [
    ['GitHub flow', 'main only', 'web apps that deploy often', 'needs good CI, because main must always work'],
    ['Gitflow', 'main and develop', 'products with numbered, scheduled releases and several supported versions', 'many branches and slow, painful merges'],
    ['Trunk based', 'main (the trunk)', 'teams with strong automated tests who merge at least daily', 'unfinished work must hide behind feature flags'],
    ['Forking', 'your fork plus the original (upstream)', 'open source, where outsiders cannot push', 'keeping the fork in sync']])}
{note('Gitflow was published by Vincent Driessen in 2010. In 2020 he added a note to the article saying that for software delivered continuously, such as web apps, a simpler workflow like GitHub flow is usually a better fit. Gitflow still suits software with explicit versions.', 'exam')}
{sh('Forking workflow: keep your fork in sync', """git remote add upstream https://github.com/ORIGINAL/calc-app.git
git fetch upstream
git switch main
git merge --ff-only upstream/main
git push origin main""")}
''', kw=['workflow', 'GitHub flow', 'Gitflow', 'trunk based development', 'feature flags', 'forking workflow', 'upstream', 'develop branch', 'release branch', 'hotfix'])

K.lesson('pr', 'Pull requests and merge requests', f'''
<p>A <b>pull request</b> (GitHub) or <b>merge request</b> (GitLab) is a page that asks to merge one branch into another. It is not a Git feature: it lives on the server. It shows the diff, runs CI on every push, and collects review comments and approvals.</p>
{flow(('Push the branch', 'git push -u origin feature/percent'),
      ('Open the PR or MR', 'title, description, linked issue, reviewers'),
      ('CI runs', 'the pipeline result appears as a status check on the page'),
      ('Review', 'comments on lines, change requests, approvals'),
      ('Fix and push again', 'the PR updates itself and CI runs again'),
      ('Merge', 'with the method the project allows, then delete the branch'))}
{table(['GitHub merge button', 'GitLab merge method', 'Resulting history'], [
    ['Create a merge commit', 'Merge commit', 'all branch commits plus a merge commit, the same as git merge --no-ff'],
    ['Squash and merge', 'Squash commits option (with the merge commit methods a merge commit is added too)', 'one new commit holding the whole change'],
    ['Rebase and merge', 'Fast-forward merge', 'the branch commits replayed on top, straight line, no merge commit'],
    ['(no equivalent)', 'Merge commit with semi-linear history', 'merge commit, but only allowed when the branch is already rebased on the target']])}
{devqa('<p>Keep the PR small and focused, write what changed and why, link the issue, and make CI green before asking for review. Answer every comment, by changing code or explaining.</p>',
       '<p>Read the description for what to test, pull the branch or download the build artifact from its pipeline, test on a test environment, and add test cases for the edge cases you found. A green pipeline is necessary, not sufficient.</p>',
       'A pull request, seen by Dev and by QA')}
{note('Squash and merge makes main easy to read, but the branch commits do not appear on main. If someone keeps working on the old branch afterwards, Git does not know those commits were merged and conflicts follow. Start a fresh branch after a squash merge.', 'warn')}
''', kw=['pull request', 'merge request', 'code review', 'status check', 'squash and merge', 'rebase and merge', 'merge commit', 'fast-forward merge', 'semi-linear history'])

K.lesson('protect', 'Protect main: branch rules and code owners', f'''
<p>A workflow is only a promise until the server enforces it. Both platforms let you protect a branch so that changes arrive only through reviewed, tested pull requests.</p>
{table(['Rule', 'GitHub (Settings, Branches or Rules)', 'GitLab (Settings, Repository, Protected branches)'], [
    ['No direct pushes', 'Require a pull request before merging', 'Allowed to push and merge: No one'],
    ['Reviews', 'Required approvals, require review from Code Owners', 'Approval rules, Require approval from code owners (Premium)'],
    ['Tests must pass', 'Require status checks to pass, pick the CI jobs', 'Settings, Merge requests, Merge checks: Pipelines must succeed'],
    ['No history rewrites', 'Force pushes are blocked by default in a rule', 'Allowed to force push: off'],
    ['No deleting the branch', 'Deletions are blocked by default in a rule', 'A protected branch cannot be deleted with git push, only by a Maintainer in the UI or API'],
    ['Straight history', 'Require linear history', 'Merge method: Fast-forward merge']])}
{file('.github/CODEOWNERS', """# Default owners for everything
*                 @OWNER/maintainers
# Python code
*.py              @OWNER/backend
# The pipelines need a CI owner to approve
/.github/workflows/ @OWNER/ci-team
/.gitlab-ci.yml     @OWNER/ci-team
# Protect this file itself
/.github/CODEOWNERS @OWNER""", {2: 'The first rule matches every file.', 4: 'The last matching pattern wins, so a .py file goes to backend, not maintainers.', 6: 'Changes to pipelines can leak secrets or skip tests, so they get their own reviewers.', 9: 'GitHub recommends owning the CODEOWNERS file itself, otherwise anyone could remove themselves from review.'}, lang='text')}
<p>GitHub looks for CODEOWNERS in <code>.github/</code>, the repository root, then <code>docs/</code>, and uses the first one it finds. Owners are requested for review automatically when a pull request touches their files. GitLab reads the same file name, and Code Owners there is a Premium and Ultimate feature.</p>
{note('If your branch rule requires a status check called unit-tests, the job name in the workflow must stay unit-tests. Renaming the job makes the required check wait forever. GitHub also advises keeping job names unique across workflows for this reason.', 'warn')}
''', kw=['branch protection', 'protected branch', 'required status checks', 'pipelines must succeed', 'required approvals', 'CODEOWNERS', 'code owners', 'linear history', 'force push', 'rulesets'])

K.lesson('commits', 'Good commit messages and Conventional Commits', f'''
<p>A commit message is a letter to the person who reads it in two years. The common convention: a short summary line of about 50 characters in the imperative ("Add percent function", not "added"), a blank line, then a body that explains why.</p>
<p><b>Conventional Commits</b> (version 1.0.0 of the specification) adds a type in front so that tools can read the history: <code>type(scope): description</code>.</p>
{table(['Message', 'Meaning', 'Semver effect'], [
    ['<code>fix(calc): handle divide by zero</code>', 'a bug fix', 'PATCH'],
    ['<code>feat(calc): add percent()</code>', 'a new feature', 'MINOR'],
    ['<code>feat!: drop Python 3.9</code> or a footer <code>BREAKING CHANGE: ...</code>', 'a breaking change', 'MAJOR'],
    ['<code>docs:</code>, <code>test:</code>, <code>ci:</code>, <code>refactor:</code>, <code>chore:</code>', 'allowed extra types', 'none by default']])}
{code('conv')}
{scene('release notes from history', '<p>Projects such as Angular adopted structured commit messages so that changelogs could be generated from Git history, and that convention grew into the Conventional Commits specification. Release tools read the messages since the last tag, pick the next version and write the release notes, which is why a CI job often checks message format on every pull request.</p>')}
{ladder(
    '<p>A workflow is the team agreement on how branches are used. Pull requests are where code is checked by people and by CI before it reaches main.</p>',
    '<p>GitHub flow keeps one long lived branch, Gitflow two, trunk based development merges small changes daily. Branch protection turns the rules into server checks: reviews, required status checks, no force pushes.</p>',
    '<p>Merge methods change the shape of main: merge commits keep context, squash gives one commit per PR, rebase or fast forward gives a straight line. Merge queues (GitHub) and merge trains (GitLab) test each change against the result of the ones queued before it.</p>',
    '<p>The DORA research programme links short lived branches, trunk based development and fast feedback from CI to better delivery performance. Supply chain frameworks such as SLSA go further: they ask that releases are built by a hosted CI platform, not on a laptop, and that the build produces signed provenance saying which commit it came from.</p>')}
''', kw=['commit message', 'imperative', 'Conventional Commits', 'feat', 'fix', 'BREAKING CHANGE', 'changelog', 'merge queue', 'merge train'])

K.quiz('e', 'In GitHub flow, how many long lived branches are there?', ['One, main', 'Two, main and develop', 'One per developer', 'None'], 0, 'Simple.', 'Short feature branches merge into main through pull requests.')
K.quiz('e', 'What does GitLab call a pull request?', ['Push request', 'Merge request', 'Change list', 'Patch set'], 1, 'Same idea.', 'MR on GitLab, PR on GitHub.')
K.quiz('e', 'Is a pull request a feature of Git itself?', ['Yes, git pull-request', 'No, it is a feature of the hosting server', 'Only in Git 3', 'Only for forks'], 1, 'Server side.', 'git request-pull exists but only prints a summary for email.')
K.quiz('m', 'Which workflow keeps a develop branch next to main?', ['GitHub flow', 'Gitflow', 'Trunk based', 'Forking'], 1, 'Two long lived.', 'develop collects the next release.')
K.quiz('m', 'Trunk based teams merge unfinished features into main. How do users not see them?', ['They do not merge them', 'Feature flags switch the code off', 'They use tags', 'They revert every night'], 1, 'Switches.', 'The code ships dark and is turned on later.')
K.quiz('m', 'Which GitHub merge button turns the whole branch into one commit on main?', ['Create a merge commit', 'Squash and merge', 'Rebase and merge', 'Fast forward'], 1, 'Squash.', 'One commit per pull request.')
K.quiz('m', 'In a CODEOWNERS file, two patterns match a file. Which owners are used?', ['The first match', 'The last match', 'Both', 'None'], 1, 'Like .gitignore.', 'Later patterns take precedence.')
K.quiz('h', 'Where do you require a green pipeline before merging on GitLab?', ['.gitlab-ci.yml', 'Settings, Merge requests, Merge checks, Pipelines must succeed', 'Protected tags', 'Runners page'], 1, 'Merge checks.', 'Combined with protected branches, nothing untested reaches main.')
K.quiz('h', 'Which commit message produces a MAJOR bump under Conventional Commits?', ['fix: typo', 'feat: add export', 'feat!: remove the v1 API', 'docs: update'], 2, 'The bang.', '! after the type, or a BREAKING CHANGE footer.')
K.quiz('x', 'A required status check named unit-tests never reports after you renamed the job to tests. Why?', ['GitHub is down', 'The rule waits for a check called unit-tests, which no job reports any more', 'Branch protection was deleted', 'The cache expired'], 1, 'Names must match.', 'Update the rule or keep the old job name.')

K.calc('e', 'Commits since v1.4.0: fix, docs, fix. What is the next version, written without dots (1.4.1 is 141)?', '141', 'Only fixes.',
       ['fix gives PATCH, docs gives nothing.', 'The highest bump is PATCH.', eq('1.4.0 to 1.4.1, written 141')], check=141)
K.calc('e', 'Commits since v1.4.0: fix, feat, docs. Next version without dots?', '150', 'feat beats fix.',
       ['The highest bump is MINOR from feat.', 'MINOR up, PATCH to 0.', eq('1.5.0, written 150')], check=150)
K.calc('m', 'Commits since v2.3.1: feat, fix, feat!. Next version without dots?', '300', 'The bang wins.',
       ['feat! is a breaking change.', 'MAJOR up, the rest to 0.', eq('3.0.0, written 300')], check=300)
K.calc('m', 'A PR has 7 commits. How many new commits land on main with Squash and merge?', '1', 'Squash.',
       ['Squash combines all changes.', 'It creates one new commit on main.', eq('1 commit')], check=1)
K.calc('m', 'A PR has 7 commits and main has moved. How many new commits land on main with Create a merge commit?', '8', 'Branch plus merge.',
       ['All 7 branch commits become reachable from main.', 'One merge commit joins the lines.', eq('7 + 1 = 8')], check=8)
K.calc('h', 'CODEOWNERS: "* @a", "*.py @b", "/tests/ @c". Who owns tests/test_calc.py? Answer 1 for a, 2 for b, 3 for c.', '3', 'Last match wins.',
       ['* matches: owner a.', '*.py matches: owner b.', eq('/tests/ matches last: owner c, answer 3')], check=3)

K.assign('owners', 'm', 'Who owns this file',
         '<p>Write <code>owners(rules, path)</code>. rules is a list of <code>[pattern, owner]</code> pairs. Patterns are <code>*</code> (everything), <code>*.ext</code> (files ending in .ext) or <code>/dir/</code> (everything under that top level folder). The last matching rule wins. Return the owner, or None.</p>',
         '''
def owners(rules, path):
    # your code here
    pass
''', [("owners([['*', '@a'], ['*.py', '@b']], 'app/calc.py')", '@b'),
      ("owners([['*', '@a'], ['*.py', '@b'], ['/tests/', '@c']], 'tests/test_calc.py')", '@c'),
      ("owners([['*.py', '@b']], 'README.md')", None),
      ("owners([['/tests/', '@c'], ['*', '@a']], 'tests/x.py')", '@a')],
         '''
def match(pattern, path):
    if pattern == '*':
        return True
    if pattern.startswith('*.'):
        return path.endswith(pattern[1:])
    if pattern.startswith('/') and pattern.endswith('/'):
        return path.startswith(pattern[1:])
    return path == pattern

def owners(rules, path):
    found = None
    for pattern, who in rules:
        if match(pattern, path):
            found = who
    return found
''', 'Loop over every rule and keep the owner of the latest match.', '<p>Order matters: put the general rule first and specific rules after it.</p>')
K.assign('nextver', 'h', 'Next version from commit messages',
         '<p>Write <code>next_version(tag, messages)</code>. tag looks like <code>v1.4.0</code>. Use Conventional Commits: <code>type!:</code> or a message containing <code>BREAKING CHANGE</code> is major, <code>feat</code> is minor, <code>fix</code> is patch, anything else changes nothing. Return the new tag, or the same tag if nothing changes.</p>',
         '''
def next_version(tag, messages):
    # your code here
    pass
''', [("next_version('v1.4.0', ['fix: a', 'docs: b'])", 'v1.4.1'), ("next_version('v1.4.0', ['fix: a', 'feat: b'])", 'v1.5.0'),
      ("next_version('v1.4.0', ['feat!: c'])", 'v2.0.0'), ("next_version('v1.4.0', ['chore: x'])", 'v1.4.0'),
      ("next_version('v0.9.3', ['fix: a', 'refactor: b\\n\\nBREAKING CHANGE: new API'])", 'v1.0.0')],
         '''
def level(msg):
    head = msg.split(':')[0]
    if head.endswith('!') or 'BREAKING CHANGE' in msg:
        return 3
    if head.startswith('feat'):
        return 2
    if head.startswith('fix'):
        return 1
    return 0

def next_version(tag, messages):
    major, minor, patch = (int(x) for x in tag[1:].split('.'))
    top = max([level(m) for m in messages] + [0])
    if top == 3:
        return f'v{major + 1}.0.0'
    if top == 2:
        return f'v{major}.{minor + 1}.0'
    if top == 1:
        return f'v{major}.{minor}.{patch + 1}'
    return tag
''', 'Find the strongest change among all messages, then bump once.', '<p>Real release tools do exactly this before they create the tag and release notes.</p>')

K.must('Workflows', 'GitHub flow: main plus short branches. Gitflow: main plus develop, release and hotfix branches. Trunk based: merge small changes daily behind feature flags. Forking: push to your fork, PR upstream.')
K.must('PR and MR', 'Server pages that show the diff, run CI and collect reviews before a merge. Keep them small.')
K.must('Merge methods', 'Merge commit keeps the branch, squash gives one commit, rebase or fast forward gives a straight line.')
K.must('Protect main', 'Require PRs, approvals and passing status checks (GitHub) or Pipelines must succeed (GitLab). Block force pushes and deletes.')
K.must('CODEOWNERS and messages', 'CODEOWNERS: last match wins, owners auto requested. Conventional Commits: fix PATCH, feat MINOR, ! or BREAKING CHANGE MAJOR.')

T = K.topic(
    slug='workflows', topic='workflows', step=(4, 'Remotes and teamwork', 'git-team', 'Share work through GitHub and GitLab: clone, fetch, pull and push, pick a branching workflow, review through pull requests, and use the power tools teams rely on.', 'Intermediate'),
    title='Team workflows, pull requests and branch protection', short='Team workflows', badge='4.2', minutes=50, added='2026-11-02',
    lead='How real teams use branches: GitHub flow, Gitflow, trunk based and forking, how pull requests and merge requests work, which merge button to press, and how to make the server enforce the rules.',
    desc='GitHub flow, Gitflow, trunk based development and feature flags, forking workflow and upstream sync, pull requests and merge requests, code review from the Dev and QA sides, GitHub and GitLab merge methods, branch protection and Pipelines must succeed, CODEOWNERS, commit message style and Conventional Commits.',
    summary='Branching workflows, PRs and MRs, merge methods, branch protection, CODEOWNERS and Conventional Commits.',
    keywords=['github flow', 'gitflow', 'trunk based', 'pull request', 'merge request', 'branch protection', 'codeowners', 'conventional commits'],
    recap='<p>Agree a workflow, send every change through a reviewed pull request, let the server enforce reviews and green pipelines, and write messages that tools can read.</p>')
