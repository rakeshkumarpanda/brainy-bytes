# Chapter 9.1: exam revision. One place to revise Git and CI/CD by the shape of the question rather than by topic:
# command recall, scenario questions (what do you run), history puzzles, YAML debugging, pipeline design for Dev and QA,
# and the certification style multiple choice of the GitHub Actions and GitLab CI/CD certifications. Every question is
# an original practice question, not a copy of an exam. Every command and every number was checked in earlier chapters.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow, file

K = Kit()

K.code('undo', r'''
# Exam drill: pick the right undo command for the situation
situation = input("Where is the mistake? (working, staged, last-local, pushed, lost): ").strip()
answers = {
    "working":    "git restore <file>              discard edits in the working tree",
    "staged":     "git restore --staged <file>     unstage, keep the edits",
    "last-local": "git reset --soft HEAD~1         undo the commit, keep the changes staged",
    "pushed":     "git revert <commit>             new commit that undoes it, safe for shared history",
    "lost":       "git reflog, then git branch rescue <id>",
}
print(answers.get(situation, "Unknown. Choose one of the five words."))
''', stdin='pushed\n')

K.lesson('map', 'How Git and CI/CD are examined', f'''
<p>This chapter is for the week before an exam, an interview or a certification. It teaches nothing new. It shows the shapes questions take, with worked answers, and points back to the chapter where each idea is taught. The questions are original practice questions.</p>
{table(['Setting', 'Typical format', 'What earns the marks', 'Practise in'], [
    ['College lab and semester exams', 'write the command, draw the commit graph, explain a term', 'the exact command and a correct graph', 'Lessons 2 and 3'],
    ['Job interviews (Dev, QA, DevOps)', 'scenarios: what do you run, how do you design the pipeline', 'safe choices for shared history, clear reasons', 'Lessons 3 and 4'],
    ['GitHub Actions and GitLab CI/CD certifications', 'multiple choice on syntax, triggers, artifacts, security', 'knowing defaults and limits exactly', 'Lesson 4 and the quiz'],
    ['Code review at work', 'spot the bug in a workflow file', 'reading YAML carefully', 'Lesson 4']])}
<h3>The twelve ideas asked most often</h3>
<ol>
<li>Working tree, staging area, repository, and git status codes (chapter 1.2).</li>
<li>Commits as snapshots, ids as hashes, HEAD~ and HEAD^ (chapters 1.3 and 5.1).</li>
<li>Branches as pointers, fast forward versus three way merge (chapters 2.1 and 2.2).</li>
<li>Resolving conflicts and reading conflict markers (chapter 2.2).</li>
<li>Rebase versus merge and the golden rule (chapter 2.3).</li>
<li>restore, reset (soft, mixed, hard), revert and reflog (chapter 3.1).</li>
<li>fetch versus pull, rejected pushes and force-with-lease (chapter 4.1).</li>
<li>Workflows, pull requests, branch protection (chapter 4.2).</li>
<li>CI versus CD, jobs, stages, needs, runners, artifacts versus cache (chapter 6.1).</li>
<li>GitHub Actions triggers, matrix, permissions, artifacts (chapters 7.1 to 7.3).</li>
<li>GitLab rules, workflow rules, needs, artifacts, job token (chapters 8.1 to 8.3).</li>
<li>Dev versus QA responsibilities, build once and promote (chapters 6.1, 7.2, 8.2).</li>
</ol>
{note('When asked "how do you undo", first say where the mistake is (working tree, staging area, local commit, pushed commit) and whether others have it. The right command follows from those two facts.', 'exam')}
''', kw=['exam', 'revision', 'interview', 'certification', 'most asked'])

K.lesson('recall', 'Command recall in one table', f'''
{table(['Task', 'Command'], [
    ['Start a repository with main', '<code>git init -b main</code>'],
    ['Stage parts of a file', '<code>git add -p</code>'],
    ['See staged changes', '<code>git diff --staged</code>'],
    ['History as a graph', '<code>git log --oneline --graph --all</code>'],
    ['Who changed this line', '<code>git blame -L 10,20 file</code>'],
    ['Create and switch branch', '<code>git switch -c name</code>'],
    ['Merge keeping a merge commit', '<code>git merge --no-ff name</code>'],
    ['Abort a conflicted merge', '<code>git merge --abort</code>'],
    ['Replay branch on main', '<code>git rebase main</code>'],
    ['Clean up last 3 commits', '<code>git rebase -i HEAD~3</code>'],
    ['Copy one commit here', '<code>git cherry-pick -x id</code>'],
    ['Unstage', '<code>git restore --staged file</code>'],
    ['Undo last local commit, keep changes', '<code>git reset --soft HEAD~1</code>'],
    ['Undo a pushed commit', '<code>git revert id</code>'],
    ['Find lost commits', '<code>git reflog</code>'],
    ['Park work', '<code>git stash push -u -m note</code>'],
    ['Release tag', '<code>git tag -a v1.0.0 -m msg</code> and <code>git push origin v1.0.0</code>'],
    ['Publish a branch', '<code>git push -u origin name</code>'],
    ['Safe force push', '<code>git push --force-with-lease</code>'],
    ['Find the bad commit', '<code>git bisect start, bad, good v1.0</code> or <code>bisect run</code>'],
    ['Why is a file ignored', '<code>git check-ignore -v path</code>'],
    ['Object type and content', '<code>git cat-file -t id</code>, <code>-p id</code>'],
    ['Pull an Actions artifact', '<code>gh run download RUN_ID -n name</code>'],
    ['Pull a GitLab artifact', '<code>glab job artifact main build</code> or the jobs/artifacts API']])}
{code('undo')}
''', kw=['command recall', 'cheat table', 'undo chooser'])

K.lesson('scenarios', 'Scenario questions with worked answers', f'''
{steps('1. You committed to main instead of a feature branch, and have not pushed', [
    'The commit exists only locally, so rewriting is safe.',
    '<code>git branch feature/x</code> keeps a pointer to the commit.',
    '<code>git reset --hard HEAD~1</code> moves main back (no uncommitted work to lose, check git status first).',
    '<code>git switch feature/x</code> and continue. Main is clean, the commit lives on the branch.'])}
{steps('2. A bad commit was pushed to main and teammates have pulled it', [
    'Shared history must not be rewritten.',
    '<code>git revert &lt;id&gt;</code> creates a new commit that undoes it.',
    'Push it through a pull request so CI checks the revert too.',
    'For a merge commit, revert with <code>-m 1</code> to keep the main line.'])}
{steps('3. git push is rejected with fetch first', [
    'Someone pushed commits you do not have, so your push is not a fast forward.',
    '<code>git pull --rebase</code> (or fetch then rebase) puts your commits on top.',
    'Fix conflicts if any, run the tests, then <code>git push</code>.',
    'Never use --force here, it would delete their commits.'])}
{steps('4. The pipeline is green on the branch but red after merge', [
    'Two changes that each passed can break together (a semantic conflict).',
    'Run CI on the merge result: pull_request runs test the merge commit on GitHub, merged results pipelines do it on GitLab.',
    'Merge queues (GitHub) or merge trains (GitLab) test each change on top of the ones queued before it.',
    'Meanwhile revert the merge on main to get green again.'])}
{steps('5. QA reports the build they tested differs from production', [
    'Each environment rebuilt from source, so the bytes differ.',
    'Build once, upload the artifact, and promote that file through every environment.',
    'Name artifacts with the commit id and record the digest.',
    'Keep release builds in a release or package registry, not only in expiring artifacts.'])}
{steps('6. A secret was committed and pushed an hour ago', [
    'Rotate the secret immediately: assume it is leaked.',
    'Remove it from the code and add the file to .gitignore.',
    'If required, rewrite history with a tool such as git filter-repo and coordinate a force push, knowing clones may keep it.',
    'Add secret scanning in a pre-commit hook and in CI.'])}
''', kw=['scenario', 'wrong branch', 'pushed bad commit', 'rejected push', 'semantic conflict', 'merge queue', 'build once', 'leaked secret'])

K.lesson('yaml', 'Spot the bug: pipeline files', f'''
{file('bug-1.yml', """on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v7
        with:
          python-version: 3.10
      - run: python -m pytest""", {8: 'Bug: no actions/checkout before this, so the runner has no code to test.', 10: 'Bug: unquoted 3.10 is read as the number 3.1. Write \'3.10\'.', 11: 'Bug: nothing installed pytest. A fresh Python has no pytest, so add pip install -r requirements.txt first.'})}
{file('bug-2.yml', """jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v7
      - run: pytest --junitxml=report.xml
      - uses: actions/upload-artifact@v7
        with:
          name: report
          path: report.xml""", {10: 'Bug: no if: always(), so the report is lost exactly when tests fail.', 12: 'Bug: both matrix jobs upload the name report. The second upload fails. Use report-${{ matrix.os }}.'})}
{file('bug-3.gitlab-ci.yml', """stages: [build, test]
build:
  stage: build
  script:
    - make dist
test:
  stage: test
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH
  script:
    - ./run-tests dist/app""", {5: 'Bug: no artifacts: paths, so dist/ is lost when the build job ends and the test job cannot find it.', 8: 'Bug: rules for merge requests and branches with no workflow:rules, so a push to a branch with an open MR creates two pipelines.'})}
{note('In exams and reviews, read a pipeline file in this order: triggers, checkout or clone, versions, what each job needs from another job, what is kept, and what runs with which permissions.', 'tip')}
''', kw=['spot the bug', 'yaml debugging', 'missing checkout', 'unquoted version', 'artifact name clash', 'missing artifacts', 'duplicate pipelines'])

K.quiz('e', 'Which command shows staged changes?', ['git diff', 'git diff --staged', 'git log -p', 'git status -s'], 1, 'Staged.', 'Plain git diff shows unstaged changes.')
K.quiz('e', 'A branch in Git is', ['a copy of all files', 'a movable pointer to a commit', 'a folder', 'a server'], 1, 'Pointer.', 'Creating one is instant.')
K.quiz('e', 'Which file defines a GitLab pipeline?', ['.gitlab-ci.yml', 'pipeline.json', '.github/workflows/ci.yml', 'Jenkinsfile'], 0, 'Dot file.', 'At the repository root.')
K.quiz('m', 'You want to undo a pushed commit without rewriting history. Command?', ['git reset --hard', 'git revert', 'git commit --amend', 'git rebase -i'], 1, 'New commit.', 'revert adds an inverse commit.')
K.quiz('m', 'git merge feature when main has no new commits since the branch started produces', ['a merge commit', 'a fast forward', 'a conflict', 'a rebase'], 1, 'Straight line.', 'Unless --no-ff is used.')
K.quiz('m', 'Which is NOT a valid reason to use a cache instead of an artifact?', ['Speeding up pip installs', 'Passing the build to the test job', 'Reusing downloaded packages', 'Saving dependency download time'], 1, 'Results need artifacts.', 'Caches may be missing.')
K.quiz('m', 'In GitHub Actions, how do jobs run by default?', ['One after another', 'In parallel unless needs says otherwise', 'Only manually', 'In alphabetical order'], 1, 'Parallel.', 'needs creates order.')
K.quiz('m', 'In GitLab, which variable tells you the pipeline came from a schedule?', ['CI_COMMIT_BRANCH', 'CI_PIPELINE_SOURCE', 'CI_JOB_TOKEN', 'CI_DEFAULT_BRANCH'], 1, 'Source.', 'Its value is schedule.')
K.quiz('h', 'Which pair is correct?', ['reset --soft keeps changes staged, reset --hard discards them', 'reset --soft discards, --hard keeps', 'both keep changes', 'both discard'], 0, 'Soft is gentle.', '--mixed keeps them unstaged.')
K.quiz('h', 'A workflow uses third party actions by tag. What is the documented hardening?', ['Use @main', 'Pin each to a full commit SHA', 'Use @latest', 'Fork every action'], 1, 'Immutable reference.', 'Tags can be moved.')
K.quiz('h', 'QA wants yesterday\'s CI build in a nightly GitHub workflow. Which combination works?', ['actions/cache with the same key', 'permissions actions: read and gh run download with the run id', 'git pull the artifact', 'upload-artifact with overwrite'], 1, 'Other run.', 'Or download-artifact with github-token and run-id.')
K.quiz('x', 'Why is git pull --rebase preferred over git pull for a local feature branch that is not shared?', ['It is faster', 'It keeps your local commits on top of the remote ones with no merge commit noise', 'It cannot conflict', 'It pushes too'], 1, 'Linear history.', 'Safe because those commits are not shared yet.')

K.calc('e', 'Ahead 2, behind 0. After git push, how many commits does origin/main gain?', '2', 'Fast forward.',
       ['Ahead 2 means two commits only you have.', 'Behind 0 means the push is a fast forward.', eq('origin/main gains 2 commits')], check=2)
K.calc('e', 'How many hex digits in a full SHA-1 object id?', '40', '160 bits.',
       ['SHA-1 gives 160 bits.', '4 bits per hex digit.', eq('160 / 4 = 40')], check=40)
K.calc('m', 'git bisect over 64 commits. Worst case number of tests?', '6', 'Powers of two.',
       ['2⁶ = 64.', 'Each test halves the range.', eq('6 tests')], check=6)
K.calc('m', 'Matrix 4 operating systems × 3 versions with 2 excludes. Jobs?', '10', 'Product minus excludes.',
       ['4 × 3 = 12.', 'Minus 2 excluded.', eq('10 jobs')], check=10)
K.calc('m', 'GitLab stage mode: build stage jobs 3 and 8 minutes, test stage one job of 4 minutes. Total?', '12', 'Slowest per stage.',
       ['build stage: 8.', 'test stage: 4.', eq('8 + 4 = 12 minutes')], check=12)
K.calc('h', 'Same, but the test job needs only the 3 minute job. Total?', '8', 'Longest path.',
       ['test runs from 3 to 7.', 'The 8 minute job ends at 8.', eq('max(7, 8) = 8 minutes')], check=8)
K.calc('h', 'Artifact uploaded on day 0 with retention 14 on GitHub. Last whole day it is available?', '13', 'Strictly less than 14.',
       ['Available while day < 0 + 14.', 'Day 14 is excluded.', eq('day 13')], check=13)

T = K.topic(
    slug='exam-revision', topic='exam-revision', kind='revision',
    step=(9, 'Exam revision', 'git-revision', 'Revise Git and CI/CD by question type: command recall, scenarios, YAML bug hunts and certification style multiple choice.', 'All levels'),
    title='Exam revision: commands, scenarios and pipeline bug hunts', short='Exam revision', badge='9.1', minutes=50, added='2026-11-02',
    lead='Practise every question shape you will meet in exams, interviews and certifications: exact commands, what to run in a scenario, how to read a pipeline file for bugs, and quick multiple choice.',
    desc='How Git and CI/CD are examined, the twelve most asked ideas, a command recall table, an undo chooser, six scenario questions with worked answers, three buggy pipeline files explained, a mock quiz and quick numericals.',
    summary='Exam and interview style questions on Git and CI/CD with worked answers, a command table and pipeline bug hunts.',
    keywords=['exam', 'revision', 'interview', 'certification', 'scenarios', 'command table', 'spot the bug', 'mock quiz'],
    recap='')
