# Chapter 6.1: CI/CD foundations. Continuous integration, continuous delivery and deployment, pipelines, stages,
# jobs and steps, runners, YAML basics, artifacts versus cache, variables and secrets, environments, build once and
# promote, Dev and QA responsibilities, and three real incidents. Sources: GitHub Actions docs (understanding GitHub
# Actions, store and share data, dependency caching, secure use reference), GitLab CI/CD docs (quick start, jobs,
# job artifacts, caching, runners), the US SEC order on Knight Capital (2013), Codecov security update (April 2021),
# GitHub advisory and CVE-2025-30066 for tj-actions/changed-files (March 2025), YAML 1.1 and 1.2 type rules.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow, file, devqa

K = Kit()

K.code('order', r'''
# How a CI server decides when each job may start: a job waits only for the jobs in its needs list
jobs = {
    "lint":        {"needs": [],             "minutes": 1},
    "unit-tests":  {"needs": ["lint"],       "minutes": 2},
    "build":       {"needs": ["unit-tests"], "minutes": 1},
    "smoke-tests": {"needs": ["build"],      "minutes": 2},
}

finish = {}
while len(finish) < len(jobs):
    for name, job in jobs.items():
        if name not in finish and all(n in finish for n in job["needs"]):
            start = max([finish[n] for n in job["needs"]] + [0])
            finish[name] = start + job["minutes"]
            print(f"{name:12} starts at minute {start}, ends at minute {finish[name]}")
print("pipeline time:", max(finish.values()), "minutes")
''')

K.lesson('why', 'What CI and CD mean, and why teams need them', f'''
<p><b>Continuous integration (CI)</b> means every developer merges small changes into the shared branch often, and a server automatically builds and tests every push. Problems show up within minutes, while the change is still fresh in the author's head.</p>
<p><b>Continuous delivery (CD)</b> means every change that passes the pipeline is packaged and ready to release, and a person presses the button. <b>Continuous deployment</b> goes one step further: a green pipeline releases to production with no human step.</p>
{flow(('Commit and push', 'a developer pushes a branch or opens a pull request'),
      ('Pipeline starts', 'the CI server reads the YAML file in the repository'),
      ('Build and test', 'lint, unit tests, build a package (the artifact)'),
      ('Deploy to test', 'QA and automated tests check the same artifact'),
      ('Release', 'a person approves (delivery) or it goes out by itself (deployment)'))}
{scene('Knight Capital, 1 August 2012', '<p>Knight Capital deployed new trading code by hand to eight servers. According to the US Securities and Exchange Commission, a technician did not copy the new code to one of the eight. That server still had old, unused code, and a reused flag in the new orders switched the old code on. In about 45 minutes it sent millions of unintended orders, and the firm lost about 460 million US dollars. The SEC order points to the lack of written deployment procedures and of a second person checking. An automated pipeline that deploys the same package to every server, and verifies the result, is the standard defence.</p>')}
{table(['Term', 'GitHub Actions', 'GitLab CI/CD'], [
    ['the config file', '<code>.github/workflows/*.yml</code> (many files allowed)', '<code>.gitlab-ci.yml</code> at the root (one file, can include others)'],
    ['one run', 'workflow run', 'pipeline'],
    ['a unit of work on one machine', 'job', 'job'],
    ['the commands inside a job', 'steps (run or uses)', 'script lines'],
    ['the machine', 'runner (GitHub hosted or self hosted)', 'runner (instance runners on GitLab.com or your own)'],
    ['grouping', 'needs between jobs', 'stages, plus needs to skip waiting']])}
''', kw=['continuous integration', 'continuous delivery', 'continuous deployment', 'CI/CD', 'pipeline', 'Knight Capital', 'automation', 'workflow run'])

K.lesson('anatomy', 'Inside a pipeline: jobs, stages, runners and YAML', f'''
<p>A pipeline is a set of <b>jobs</b>. Each job runs on a fresh machine called a <b>runner</b>, so jobs share nothing unless you pass files on as artifacts. Jobs either wait for a whole <b>stage</b> to finish (the GitLab default) or only for the jobs they <b>need</b>. Try both modes and make one job fail.</p>
{viz('pipeline')}
{code('order')}
<p>Both platforms describe pipelines in <b>YAML</b>: indentation with spaces shows what belongs to what, <code>key: value</code> makes a map and <code>- item</code> makes a list. Break the file in the animation and read the error.</p>
{viz('yamlview')}
{note('YAML guesses types. python-version: 3.10 is read as the number 3.1, and the job installs the wrong Python. Always quote versions: python-version: "3.10". Old YAML 1.1 parsers also read a bare no or off as false.', 'warn')}
{table(['YAML', 'Means'], [
    ['<code>image: python:3.13-slim</code>', 'a key with a string value'],
    ['<code>branches: [main, dev]</code>', 'a list written on one line'],
    ['<code>steps:</code> then lines starting with <code>- </code>', 'a list written as lines'],
    ['<code>run: |</code>', 'a block of text: every following indented line is kept, newlines included'],
    ['<code># note</code>', 'a comment']])}
''', kw=['job', 'stage', 'runner', 'needs', 'DAG', 'YAML', 'indentation', 'list', 'map', 'quote versions', 'block scalar'])

K.lesson('data', 'Artifacts, cache, variables and secrets', f'''
<p>Jobs start on clean machines, so you decide what moves between them and how.</p>
{table(['', 'Artifact', 'Cache'], [
    ['What for', 'results you need later: a build package, test reports, coverage', 'things you can rebuild but would rather not: downloaded dependencies'],
    ['Who uses it', 'later jobs in the same run, people, other pipelines', 'later runs of the same or another job'],
    ['If it is missing', 'the pipeline is wrong', 'the job is only slower'],
    ['GitHub Actions', 'actions/upload-artifact and download-artifact, kept 90 days by default', 'actions/cache or the cache option of setup actions, 10 GB per repository'],
    ['GitLab CI/CD', 'artifacts: paths and expire_in (30 days on GitLab.com by default)', 'cache: key and paths']])}
{fxs(
    fx('Variables', 'GitHub: <code>env:</code> and <code>vars.NAME</code>. GitLab: <code>variables:</code> and project CI/CD variables', 'Plain settings such as a test URL. Visible in logs if printed.'),
    fx('Secrets', 'GitHub: <code>${{ secrets.NAME }}</code>. GitLab: masked and protected CI/CD variables', 'Stored encrypted and hidden in logs. Never write a secret into the YAML file.', key=True),
    fx('Least privilege', 'GitHub: <code>permissions: contents: read</code>. GitLab: protected variables only on protected branches', 'Give each job only the access it needs.', key=True),
    fx('Pin third party actions', '<code>uses: owner/action@&lt;full commit SHA&gt;</code>', 'A tag such as @v4 can be moved to new code. A full commit id cannot.', key=True))}
{scene('Codecov, 2021', '<p>Codecov offered a Bash script that thousands of CI pipelines downloaded and ran on every build to upload coverage. In January 2021 an attacker changed that script on Codecov\'s server so that it also sent the environment variables of each CI job, which often held tokens and keys, to the attacker. It went unnoticed until April 2021, when a customer compared the script with its published checksum. Lessons: check downloaded scripts against a checksum, give CI jobs as few secrets as possible, and rotate credentials after such a leak.</p>')}
{scene('tj-actions/changed-files, March 2025', '<p>An attacker gained access to the popular GitHub Action tj-actions/changed-files and moved its version tags to a malicious commit that printed the CI runner\'s secrets into the job log (CVE-2025-30066). Public repositories with public logs exposed their secrets. Workflows that pinned the action to a full commit SHA kept running the old, safe code. GitHub\'s own security guidance recommends pinning third party actions to a full length commit SHA.</p>')}
''', kw=['artifact', 'cache', 'variables', 'secrets', 'masked variable', 'protected variable', 'permissions', 'least privilege', 'pin SHA', 'Codecov', 'tj-actions', 'supply chain'])

K.lesson('roles', 'Dev and QA in a pipeline, and build once, promote many', f'''
<p>The same pipeline serves two groups with different questions. Developers ask "did my change break anything, and how fast can I know?". QA asks "is this exact build good enough to release, and can I prove it?".</p>
{devqa('<ul><li>Fast feedback on every push: lint and unit tests in a few minutes.</li><li>Builds the artifact once and tags it with the commit id.</li><li>Uses cache to keep the pipeline fast.</li><li>Fixes a red pipeline before starting new work.</li><li>Deploys automatically to a dev environment.</li></ul>',
       '<ul><li>Tests the artifact the pipeline built, never a fresh build from a laptop.</li><li>Runs slower suites: API, end to end, regression, often on a schedule or before release.</li><li>Keeps test reports as artifacts so failures can be shown later.</li><li>Owns the quality gate: which checks must pass before production.</li><li>Tracks flaky tests instead of pressing retry until green.</li></ul>')}
{flow(('Build once', 'one job builds calc-app.zip from commit 7c9e1d0'),
      ('Dev environment', 'deployed automatically, developers check it'),
      ('QA environment', 'the same zip, QA runs regression and end to end tests'),
      ('Staging', 'the same zip with production like settings'),
      ('Production', 'the same zip after approval'))}
{note('If each environment rebuilds from source, QA tested a different file from the one users get. Build once, store it as an artifact or in a package registry, and promote that same file.', 'exam')}
{ladder(
    '<p>CI is a robot that builds and tests every change you push. CD makes sure every good change is ready to ship. Dev uses the pipeline for quick answers, QA uses it to prove a build is ready.</p>',
    '<p>A pipeline is a graph of jobs on fresh runners, written in YAML. Artifacts pass results on, caches speed up dependency downloads, secrets live outside the YAML. Build once and promote the same artifact.</p>',
    '<p>Pipeline time is the longest path through the job graph, so needs and parallel jobs shorten it. Every third party step runs with your secrets, so pin by SHA, restrict permissions and treat CI as production.</p>',
    '<p>DORA research measures delivery with lead time, deployment frequency, change failure rate and time to restore. SLSA defines levels of build integrity, from documented builds to hosted, isolated builds with signed provenance.</p>')}
''', kw=['Dev view', 'QA view', 'quality gate', 'flaky tests', 'environments', 'staging', 'build once', 'promote', 'regression', 'DORA', 'SLSA'])

K.quiz('e', 'What does continuous integration mean?', ['Deploying every hour', 'Merging small changes often, with every push built and tested automatically', 'Writing integration tests only', 'Using one branch'], 1, 'Merge often, test always.', 'Problems show up within minutes.')
K.quiz('e', 'Where does GitHub Actions look for workflow files?', ['.gitlab-ci.yml', '.github/workflows/', 'ci/', '.git/hooks'], 1, 'A folder.', 'Any .yml or .yaml file in that folder.')
K.quiz('e', 'What is a runner?', ['A test framework', 'The machine that runs the jobs', 'A Git command', 'A YAML key'], 1, 'Does the work.', 'Hosted by the platform or by you.')
K.quiz('m', 'Continuous delivery versus continuous deployment: the difference is', ['None', 'Deployment releases to production automatically, delivery waits for a person', 'Delivery has no tests', 'Deployment is only for mobile apps'], 1, 'Human button.', 'Both keep every change releasable.')
K.quiz('m', 'You want downloaded pip packages reused between runs. Artifact or cache?', ['Artifact', 'Cache', 'Secret', 'Variable'], 1, 'Rebuildable.', 'A missing cache only costs time.')
K.quiz('m', 'You want QA to test the exact zip that the build job made. Artifact or cache?', ['Artifact', 'Cache', 'Both', 'Neither'], 0, 'Results.', 'Artifacts are the outputs of a run.')
K.quiz('m', 'python-version: 3.10 in YAML installs Python 3.1. Why?', ['A bug in Python', 'YAML reads 3.10 as the number 3.1, so quote it', 'Version 3.10 does not exist', 'The runner is old'], 1, 'Numbers.', 'Write "3.10".')
K.quiz('h', 'Why pin a third party action to a full commit SHA?', ['It is faster', 'Tags can be moved to malicious code, a commit id cannot', 'GitHub requires it', 'It saves cache space'], 1, 'tj-actions.', 'March 2025 showed moved tags leaking secrets.')
K.quiz('h', 'What caused the Knight Capital loss in 2012, according to the SEC?', ['A hacker', 'New code was not deployed to one of eight servers by a manual process, and old code was triggered', 'A database crash', 'A slow network'], 1, 'Manual deploy.', 'Automated, verified deployment is the fix.')
K.quiz('x', 'Why build once and promote the same artifact?', ['To save disk', 'So that the file tested by QA is exactly the file released', 'Because rebuilds are forbidden', 'To skip tests'], 1, 'Same bytes.', 'Rebuilds can pick up different dependencies or code.')

K.calc('e', 'Jobs in a chain: lint 1 min, tests 2 min, build 1 min, smoke 2 min. Total pipeline time?', '6', 'A chain adds up.',
       ['Each job waits for the one before.', '1 + 2 + 1 + 2.', eq('6 minutes')], check=6)
K.calc('e', 'Two independent jobs of 3 and 5 minutes run in parallel. How long does the pipeline take?', '5', 'The longest one.',
       ['They start together.', 'The pipeline ends when the slower one ends.', eq('max(3, 5) = 5 minutes')], check=5)
K.calc('m', 'Stage mode: stage 1 has jobs of 1 and 6 minutes, stage 2 has a 2 minute job that only needs the 1 minute job. Total?', '8', 'Stages wait for everything.',
       ['Stage 1 ends when its slowest job ends: 6.', 'Stage 2 starts at 6.', eq('6 + 2 = 8 minutes')], check=8)
K.calc('m', 'Same jobs but with needs: the 2 minute job needs only the 1 minute job. Total?', '6', 'Longest path.',
       ['The 2 minute job starts at minute 1 and ends at 3.', 'The 6 minute job ends at 6.', eq('max(3, 6) = 6 minutes')], check=6)
K.calc('h', 'A team pushes 40 times a day. Each pipeline takes 12 minutes on 1 runner, and pipelines queue. How many runner hours a day?', '8', 'Minutes to hours.',
       ['40 × 12 = 480 minutes.', '480 / 60.', eq('8 runner hours')], check=8)
K.calc('h', 'Caching cuts dependency install from 3 minutes to 0.5 in a 12 minute pipeline. With 40 runs a day, how many minutes are saved per day?', '100', 'Saving per run times runs.',
       ['Saving per run: 3 - 0.5 = 2.5 minutes.', '40 runs a day.', eq('2.5 × 40 = 100 minutes')], check=100)

K.assign('ptime', 'm', 'Pipeline time with needs',
         '<p>Write <code>pipeline_time(jobs)</code>. jobs maps a job name to <code>[minutes, needs]</code>, where needs is a list of job names. A job starts when all its needs have finished. Return the total minutes until the last job ends.</p>',
         '''
def pipeline_time(jobs):
    # your code here
    pass
''', [("pipeline_time({'lint': [1, []], 'test': [2, ['lint']], 'build': [1, ['test']]})", 4),
      ("pipeline_time({'a': [3, []], 'b': [5, []]})", 5),
      ("pipeline_time({'web': [1, []], 'docs': [6, []], 'test-web': [2, ['web']], 'deploy': [1, ['test-web']]})", 6),
      ("pipeline_time({'a': [1, []], 'b': [2, ['a']], 'c': [4, ['a']], 'd': [1, ['b', 'c']]})", 6)],
         '''
def pipeline_time(jobs):
    end = {}
    def finish(name):
        if name not in end:
            minutes, needs = jobs[name]
            end[name] = max([finish(n) for n in needs] + [0]) + minutes
        return end[name]
    return max(finish(n) for n in jobs)
''', 'A job ends at the latest end time of its needs plus its own minutes. Compute it recursively and remember results.', '<p>This is the longest path through a directed acyclic graph, also called the critical path.</p>')
K.assign('stagetime', 'h', 'Pipeline time with stages',
         '<p>Write <code>stage_time(stages)</code>. stages is a list of stages in order, each a list of job minutes. Every job in a stage starts when the whole previous stage has finished. Return the total minutes. An empty stage takes 0 minutes.</p>',
         '''
def stage_time(stages):
    # your code here
    pass
''', [("stage_time([[1], [2], [1], [2]])", 6), ("stage_time([[1, 6], [2], [1]])", 9), ("stage_time([[3, 3, 3]])", 3), ("stage_time([[], [4]])", 4)],
         '''
def stage_time(stages):
    return sum(max(s) if s else 0 for s in stages)
''', 'Each stage costs as long as its slowest job.', '<p>Compare with the needs version: stages are simpler to read, needs are faster when jobs of very different lengths share a stage.</p>')

K.must('CI and CD', 'CI: merge small changes often, every push built and tested. Continuous delivery: always releasable, a person releases. Continuous deployment: a green pipeline releases by itself.')
K.must('Pipeline parts', 'Pipeline or workflow run, jobs on fresh runners, steps or script lines. Stages wait for the whole previous stage, needs wait only for named jobs. Time = longest path.')
K.must('YAML', 'Spaces not tabs, key: value, - list items, run: | for blocks. Quote versions ("3.10").')
K.must('Artifacts versus cache', 'Artifacts are results to keep and pass on (build packages, reports). Cache is a speed up for dependencies, safe to lose.')
K.must('Secure and promote', 'Secrets outside YAML, least permissions, pin third party actions by SHA (tj-actions 2025, Codecov 2021). Build once, promote the same artifact through dev, QA, staging and production (Knight Capital 2012).')

T = K.topic(
    slug='cicd-basics', topic='cicd-basics', step=(6, 'CI/CD foundations', 'cicd-basics', 'What continuous integration and delivery mean, how pipelines, jobs, runners and YAML fit together, artifacts versus cache, secrets, and how Dev and QA use the same pipeline differently.', 'Intermediate'),
    title='CI/CD foundations: pipelines, runners, artifacts and roles', short='CI/CD basics', badge='6.1', minutes=55, added='2026-11-02',
    lead='Before writing a single workflow file, understand what a pipeline is, why jobs need artifacts to share files, how YAML trips people up, how secrets leak, and what developers and testers each want from CI.',
    desc='continuous integration, delivery and deployment, workflow runs and pipelines, jobs, steps, stages, needs and runners, YAML syntax and type traps, artifacts versus cache, variables and secrets, permissions and SHA pinning, environments, build once and promote, Dev and QA views, and the Knight Capital, Codecov and tj-actions incidents.',
    summary='CI, CD and pipelines, jobs, stages, needs and runners, YAML, artifacts versus cache, secrets, Dev and QA roles.',
    keywords=['continuous integration', 'continuous delivery', 'pipeline', 'runner', 'yaml', 'artifact', 'cache', 'secrets'],
    recap='<p>A pipeline is a graph of jobs on fresh runners described in YAML. Artifacts carry results, caches carry speed, secrets stay out of the file, and the same build moves from Dev to QA to production.</p>')
