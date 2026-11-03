# Chapter 8.2: GitLab CI/CD from scratch. Baby steps from an empty GitLab.com project to a green pipeline on every
# commit with the same calc-app project, the .gitlab-ci.yml line by line (it passed the official CI schema and every
# command was run for real), the pipeline editor and its Validate tab, unit test reports, what Dev and QA change and
# why, protected branches with Pipelines must succeed, and a scheduled nightly regression.
# Sources: GitLab docs: CI/CD quick start, pipeline editor, CI/CD YAML reference, job artifacts, unit test reports,
# pipeline schedules, protected branches, auto merge and Pipelines must succeed, workflow keyword.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow, file, devqa, changes, babystep, starter

K = Kit()

K.code('schedule', r'''
# Which jobs of the sample .gitlab-ci.yml appear in each pipeline (rules first match, no rules means always)
jobs = {
    "lint": None, "unit-tests": None, "build": None, "smoke-tests": None,
    "nightly-regression": [("schedule", True)],
}

def in_pipeline(job, source):
    rules = jobs[job]
    if rules is None:
        return True
    for src, add in rules:
        if source == src:
            return add
    return False

for source in ["push", "merge_request_event", "schedule"]:
    names = [j for j in jobs if in_pipeline(j, source)]
    print(f"{source:20} {len(names)} jobs: {', '.join(names)}")
''')

DL = '<a href="calc-app-starter.zip" download>calc-app-starter.zip</a>'

K.lesson('setup', 'Baby steps: an empty project to a green pipeline', f'''
<p>The same calc-app project runs on GitLab with one file, <code>.gitlab-ci.yml</code>. GitLab.com provides instance runners, so you do not install anything on a server. Tick each step as you finish it.</p>
{babystep(1, 'Prepare the project on your computer', f'<p>Download {DL} and unzip it, then run the unit tests once as in chapter 7.2: python -m venv .venv, pip install -r requirements.txt, python -m pytest -q tests/unit. You should see 5 passed.</p>')}
{babystep(2, 'Create a blank project on GitLab', '<p>On gitlab.com select New project, then Create blank project. Name it calc-app and clear the option to initialise the repository with a README, because you will push an existing repository. Select Create project and copy the HTTPS or SSH clone URL.</p>')}
{babystep(3, 'Push the project', sh('First push to GitLab', """git init -b main
git add .
git commit -m "Start calc-app with GitLab CI"
git remote add origin https://gitlab.com/YOUR-NAME/calc-app.git
git push -u origin main""") + '<p>If you already pushed the folder to GitHub in chapter 7.2, add GitLab as a second remote instead: git remote add gitlab URL, then git push -u gitlab main.</p>')}
{babystep(4, 'Watch the pipeline', '<p>In the project, go to Build, Pipelines. A pipeline started as soon as .gitlab-ci.yml arrived on main. Select it to see four stages, lint, test, build and qa, with one job each. Each job log starts by pulling the python:3.13-slim image, then runs the script lines. All four turn green.</p>')}
{babystep(5, 'See the test report and the artifact', '<p>On the pipeline page, the Tests tab lists the 5 unit tests and 3 smoke tests read from the JUnit reports. Open the build job: on the right side, Job artifacts offers Download and Browse, and the archive holds dist/calc-app.zip.</p>')}
{babystep(6, 'Edit the pipeline safely in the browser', '<p>Go to Build, Pipeline editor. It shows .gitlab-ci.yml with syntax checks as you type. The Validate tab simulates a pipeline for a branch and lists the jobs it would create, and the Visualize tab draws the stages and needs. Use them before every commit to the file.</p>')}
{babystep(7, 'Break it in a merge request', sh('A broken branch', """git switch -c broken-add
# in app/calc.py change: return a + b   to: return a - b
git commit -am "Break add on purpose"
git push -u origin broken-add""") + '<p>The push output prints a link to create a merge request. Open it. The workflow rules now run a merge request pipeline for this branch, unit-tests fails, build and smoke-tests do not start, and the merge request shows the failed test test_add from the JUnit report without opening the log.</p>')}
{babystep(8, 'Fix it and merge', '<p>Change the line back, commit and push. The merge request pipeline runs again and turns green. Merge it, and a branch pipeline runs on main.</p>')}
{babystep(9, 'Require a green pipeline', '<p>Go to Settings, Merge requests, Merge checks and select Pipelines must succeed. Then Settings, Repository, Protected branches: for main set Allowed to merge to Maintainers (or Developers and Maintainers) and Allowed to push and merge to No one. Now every change reaches main through a merge request with a green pipeline.</p>')}
{babystep(10, 'Schedule the nightly regression', '<p>Go to Build, Pipeline schedules, New schedule. Enter a description, the interval pattern 30 2 * * 1-5, a time zone, and main as the target branch, then save. Each night the pipeline source is schedule, so the nightly-regression job is added and runs the full suite on the build of that pipeline.</p>')}
''', kw=['gitlab setup', 'create blank project', 'first pipeline', 'Build Pipelines', 'Pipeline editor', 'Validate', 'Tests tab', 'merge request pipeline', 'Pipelines must succeed', 'pipeline schedule'])

K.lesson('file', 'The .gitlab-ci.yml, line by line', f'''
{starter('.gitlab-ci.yml', {1: 'workflow:rules decide which pipelines exist at all.', 3: 'Merge request pipelines for every merge request.', 4: 'No branch pipeline when the branch has an open merge request, which prevents duplicate pipelines.', 6: 'Branch pipelines otherwise, including main. Tag pushes create no pipeline.', 8: 'The four stages, in order.', 15: 'Every job runs in this Docker image on the instance runner.', 18: 'pip keeps downloads here, inside the project folder, because GitLab can only cache paths inside the project directory.', 23: 'The cheapest check first.', 27: 'Cache pip downloads. The key changes when requirements.txt changes.', 35: 'python -m pytest so the project folder is on the import path. The JUnit file feeds the Tests tab.', 37: 'Keep the report even when tests fail.', 41: 'reports:junit makes GitLab parse the file and show results in the merge request and the Tests tab.', 42: 'Reports are short lived. Without expire_in the instance default applies.', 48: 'Build the package once.', 50: 'The downloaded archive gets this name, with the short commit id, so files from different pipelines do not get mixed up.', 53: 'Keep the build for 30 days.', 57: 'needs with artifacts: true: start right after build and download its artifacts, here dist/calc-app.zip.', 68: 'PYTHONPATH points at the zip so the smoke tests import the packaged build.', 79: 'This job is added only in scheduled pipelines.', 86: 'The full suite against the build of the same pipeline.'})}
{viz('pipeline', preset='starter', plat='gitlab', mode='stages')}
{code('schedule')}
{note('GitLab uploads artifacts of all jobs and passes them on to jobs in later stages automatically. needs and dependencies control which ones a job downloads. dependencies: [] downloads none, which saves time in jobs that do not need files.', 'exam')}
''', kw=['.gitlab-ci.yml line by line', 'workflow rules', 'stages', 'default image', 'PIP_CACHE_DIR', 'cache key files', 'junit report', 'artifacts name', 'expire_in', 'needs artifacts', 'dependencies'])

K.lesson('devqa', 'What Dev and QA change on GitLab, and why', f'''
{devqa('<p>Goal: quick, cheap feedback on every push and merge request.</p><ul><li>Use needs so jobs start as soon as their inputs exist.</li><li>Set interruptible: true so a new push cancels the old pipeline.</li><li>Cache dependencies with a key on the lock file.</li><li>Move shared setup into a hidden job with extends.</li><li>Use protected variables so branches cannot read deploy keys.</li></ul>',
       '<p>Goal: repeatable evidence about the exact build.</p><ul><li>Download the build artifact with needs, never rebuild.</li><li>Split long suites with parallel and CI_NODE_INDEX.</li><li>Publish JUnit reports so failures show in the merge request.</li><li>Schedule regression with pipeline schedules and rules on CI_PIPELINE_SOURCE.</li><li>Keep release builds with longer expire_in or the Keep button.</li></ul>')}
{changes([
    ['image: python:3.13-slim', 'pin a digest, python:3.13-slim@sha256:...', 'the same image every run, even if the tag is updated', 'Both'],
    ['workflow: rules', 'add - if: $CI_COMMIT_TAG for release pipelines', 'tags currently create no pipeline', 'Dev'],
    ['lint job', 'add a real linter such as ruff, with allow_failure: true at first', 'catch style and bug patterns without blocking the team on day one', 'Dev'],
    ['(no interruptible)', 'default: interruptible: true', 'new pushes cancel outdated pipelines (with the project setting for auto cancel)', 'Dev'],
    ['expire_in: 30 days on build', '1 year for tagged release builds, or publish to the package registry', 'support and QA must reach the released file later', 'QA'],
    ['smoke-tests', 'add api-tests and e2e jobs with needs: [build] and parallel: 3', 'more coverage of the same artifact in less wall time', 'QA'],
    ['nightly-regression rules', 'also allow - if: $CI_PIPELINE_SOURCE == "web" with a SUITE variable', 'testers can start a regression on demand from Build, Pipelines, New pipeline', 'QA'],
    ['artifacts: when: always', 'keep it, and add screenshots or logs to paths', 'failures need evidence the most', 'QA']])}
{table(['You see', 'Cause', 'Fix'], [
    ['No pipeline after the push', 'the file name or location is wrong, YAML is invalid, or workflow rules matched nothing (for example a tag push)', 'open the Pipeline editor, read the error, check the workflow rules'],
    ['This job is stuck because you do not have any active runners', 'no runner matches, often because of tags: on the job', 'remove or fix tags, or enable instance runners under Settings, CI/CD, Runners'],
    ['Two pipelines for one push', 'a job has merge request rules but there is no workflow block', 'add the workflow rules from this chapter'],
    ['ModuleNotFoundError in smoke-tests', 'the artifact did not arrive, so dist/calc-app.zip is missing', 'check needs: build with artifacts: true and that build uploaded the path'],
    ['Cache never restores', 'the cache path is outside the project folder', 'set PIP_CACHE_DIR inside $CI_PROJECT_DIR, as in the sample']])}
''', kw=['Dev changes', 'QA changes', 'interruptible', 'allow_failure', 'image digest', 'expire_in', 'parallel', 'web pipeline', 'stuck job', 'no runners', 'troubleshooting'])

K.lesson('compare', 'The same pipeline on GitHub and GitLab', f'''
{table(['Idea', 'GitHub Actions (ci.yml)', 'GitLab CI/CD (.gitlab-ci.yml)'], [
    ['When to run', '<code>on: push / pull_request</code> with branch filters', '<code>workflow: rules</code> with pipeline source and branch variables'],
    ['Machine', '<code>runs-on: ubuntu-latest</code>, then setup-python', '<code>image: python:3.13-slim</code> on an instance runner'],
    ['Get the code', '<code>actions/checkout</code> in every job', 'automatic, the runner clones before the script'],
    ['Order', '<code>needs</code> only', '<code>stages</code>, plus <code>needs</code> to skip waiting'],
    ['Keep the build', '<code>actions/upload-artifact</code>', '<code>artifacts: paths</code>'],
    ['Use the build later', '<code>actions/download-artifact</code> + needs', 'automatic for later stages, or <code>needs: artifacts: true</code>'],
    ['Test report in the UI', 'upload the XML, or a reporting action', '<code>artifacts: reports: junit</code>, shown in the MR and Tests tab'],
    ['Cache', '<code>cache: pip</code> in setup-python', '<code>cache: key: files:</code> plus a cache folder inside the project'],
    ['Nightly', 'separate workflow with <code>schedule</code>', 'a pipeline schedule plus a job rule on <code>CI_PIPELINE_SOURCE</code>'],
    ['Merge only when green', 'branch rule: required status checks', 'Merge checks: Pipelines must succeed']])}
{ladder(
    '<p>Push a .gitlab-ci.yml and GitLab runs it on its own runners. Use the Pipeline editor to check it first, and make green pipelines a merge rule.</p>',
    '<p>workflow rules pick branch or merge request pipelines, four stages run in order, build keeps calc-app.zip, smoke-tests pulls it with needs, JUnit reports show in merge requests, and a schedule adds the regression job.</p>',
    '<p>Dev tunes speed with needs, interruptible and caches. QA tunes evidence with parallel suites, reports, schedules and retention. Pinning image digests makes runs repeatable.</p>',
    '<p>Large organisations move the shared parts into CI/CD components with versioned inputs, enforce required pipelines through compliance frameworks, and sign build provenance for the artifacts they release.</p>')}
''', kw=['GitHub vs GitLab', 'comparison', 'checkout automatic', 'stages vs needs', 'junit in merge request'])

K.quiz('e', 'Do you need to install a runner to use GitLab CI/CD on GitLab.com?', ['Yes, always', 'No, GitLab.com provides instance runners', 'Only for Python', 'Only for private projects'], 1, 'Hosted.', 'You can still add your own runners.')
K.quiz('e', 'Where do you see pipelines in a GitLab project?', ['Settings, General', 'Build, Pipelines', 'Plan, Issues', 'Deploy, Releases'], 1, 'Build menu.', 'Pipeline editor and schedules are there too.')
K.quiz('e', 'Which GitLab tool checks .gitlab-ci.yml before you commit?', ['Pipeline editor, Validate tab', 'Wiki', 'Snippets', 'Issue board'], 0, 'Editor.', 'It also visualises stages and needs.')
K.quiz('m', 'In the sample, why is PIP_CACHE_DIR inside $CI_PROJECT_DIR?', ['Speed', 'GitLab can only cache paths inside the project folder', 'pip requires it', 'To hide it'], 1, 'Cache paths.', 'Paths outside are not saved.')
K.quiz('m', 'What does reports: junit add?', ['Faster tests', 'Test results shown in the merge request and the Tests tab', 'A new stage', 'Retries'], 1, 'Visibility.', 'It does not change the job status.')
K.quiz('m', 'Which setting stops merging when the pipeline failed?', ['Protected tags', 'Merge checks: Pipelines must succeed', 'Runner tags', 'Auto DevOps'], 1, 'Merge checks.', 'Under Settings, Merge requests.')
K.quiz('m', 'When is nightly-regression added to a pipeline?', ['Every push', 'Only when the pipeline source is schedule', 'Only for tags', 'Never'], 1, 'Its rule.', 'Pipeline schedules create such pipelines.')
K.quiz('h', 'A job log says it is stuck because there are no active runners. Most likely cause on GitLab.com?', ['Bad Python code', 'The job has tags that no available runner has', 'The cache is full', 'The branch is protected'], 1, 'Tags select runners.', 'Remove or fix the tags.')
K.quiz('h', 'Your .gitlab-ci.yml has the sample workflow rules. You push tag v1.0. What runs?', ['A tag pipeline', 'Nothing, no workflow rule matches a tag push', 'Only build', 'The schedule'], 1, 'First match, or none.', 'Add a rule for $CI_COMMIT_TAG.')
K.quiz('x', 'Why does the artifacts name include $CI_COMMIT_SHORT_SHA?', ['It is required', 'Downloaded archives carry the commit, so builds from different pipelines are not confused', 'For caching', 'For rules'], 1, 'Traceability.', 'The file name tells you exactly which commit it came from.')

K.calc('e', 'The sample pipeline on a push to main. How many jobs run?', '4', 'nightly-regression only on schedules.',
       ['lint, unit-tests, build, smoke-tests.', 'nightly-regression has a schedule rule.', eq('4 jobs')], check=4)
K.calc('e', 'The same file in a scheduled pipeline. How many jobs?', '5', 'Add the nightly job.',
       ['The four normal jobs have no rules, so they run.', 'nightly-regression matches schedule.', eq('5 jobs')], check=5)
K.calc('m', 'Stage times: lint 1, test 2, build 1, qa 2 minutes (in stage mode). Total?', '6', 'Add the stages.',
       ['Each stage waits for the previous one.', '1 + 2 + 1 + 2.', eq('6 minutes')], check=6)
K.calc('m', 'A push to a branch with an open MR, using the sample workflow rules. How many pipelines?', '1', 'workflow rules.',
       ['The branch rule is skipped because CI_OPEN_MERGE_REQUESTS is set.', 'The MR pipeline runs.', eq('1 pipeline')], check=1)
K.calc('h', 'An e2e suite takes 24 minutes. With parallel: 4 and an even split, how long does the e2e stage take?', '6', 'Divide.',
       ['4 jobs run at the same time.', '24 / 4.', eq('6 minutes')], check=6)
K.calc('h', 'Cron 30 2 * * 1-5 in time zone UTC. How many scheduled pipelines in a 31 day month that starts on a Monday?', '23', 'Count weekdays.',
       ['4 full weeks: 20 weekdays.', 'Days 29, 30, 31 are Monday, Tuesday, Wednesday.', eq('20 + 3 = 23')], check=23)

K.assign('whichjobs', 'm', 'Which jobs run',
         '<p>Write <code>jobs_for(source)</code> for the sample .gitlab-ci.yml. Return the list of job names in file order that appear in a pipeline with this CI_PIPELINE_SOURCE: lint, unit-tests, build and smoke-tests always, nightly-regression only for "schedule".</p>',
         '''
def jobs_for(source):
    # your code here
    pass
''', [("jobs_for('push')", ['lint', 'unit-tests', 'build', 'smoke-tests']),
      ("jobs_for('schedule')", ['lint', 'unit-tests', 'build', 'smoke-tests', 'nightly-regression']),
      ("jobs_for('merge_request_event')", ['lint', 'unit-tests', 'build', 'smoke-tests'])],
         '''
def jobs_for(source):
    names = ['lint', 'unit-tests', 'build', 'smoke-tests']
    if source == 'schedule':
        names.append('nightly-regression')
    return names
''', 'Start with the always jobs and add the scheduled one.', '<p>The workflow rules decide whether there is a pipeline at all, this decides what is in it.</p>')
K.assign('split', 'h', 'Split tests for parallel jobs',
         '<p>Write <code>my_tests(tests, index, total)</code> the way a parallel job uses CI_NODE_INDEX (1 based) and CI_NODE_TOTAL: sort the test names, then take every total-th test starting at position index - 1. Return the list.</p>',
         '''
def my_tests(tests, index, total):
    # your code here
    pass
''', [("my_tests(['d', 'a', 'c', 'b'], 1, 2)", ['a', 'c']), ("my_tests(['d', 'a', 'c', 'b'], 2, 2)", ['b', 'd']),
      ("my_tests(['x', 'y', 'z'], 3, 3)", ['z']), ("my_tests(['x'], 2, 2)", [])],
         '''
def my_tests(tests, index, total):
    return sorted(tests)[index - 1::total]
''', 'Sorting makes every job see the same order, then a slice with a step picks this job\'s share.', '<p>Every test runs exactly once across all jobs. Smarter splitters balance by past run time.</p>')

K.must('From scratch', 'Blank project without README, push the repo with .gitlab-ci.yml, watch Build, Pipelines, check the Tests tab and job artifacts, break and fix in a merge request, then Pipelines must succeed and protected main.')
K.must('The sample file', 'workflow rules (MR, skip branch with open MR, branches), stages lint, test, build, qa, image python:3.13-slim, cache key files on requirements.txt, junit reports, build artifact with name and expire_in, smoke-tests with needs artifacts, nightly job on schedule.')
K.must('Tools', 'Pipeline editor (Validate, Visualize), Tests tab, job artifacts Download and Browse, Build, Pipeline schedules.')
K.must('Dev versus QA changes', 'Dev: needs, interruptible, cache, extends, protected variables. QA: test the artifact, parallel suites, JUnit reports, schedules and web runs, longer expiry for releases.')
K.must('Common errors', 'No pipeline (YAML or workflow rules), stuck job (runner tags), duplicate pipelines (no workflow rules), missing artifact (needs), cache path outside the project.')

T = K.topic(
    slug='gitlab-scratch', topic='gitlab-scratch', step=(8, 'GitLab CI/CD', 'gitlab-ci', 'Write GitLab pipelines from the first line: stages, rules, needs and runners, then the same Dev and QA pipeline built from scratch on GitLab, then artifacts, reports and how to pull a build with the API and glab.', 'Intermediate'),
    title='GitLab CI/CD from scratch: a green pipeline on every commit', short='GitLab from scratch', badge='8.2', minutes=65, added='2026-11-02',
    lead='Baby steps from an empty GitLab project to a pipeline that lints, tests, builds, smoke tests and keeps the package on every commit, the file explained line by line, what developers and testers change, and how it compares with GitHub Actions.',
    desc='step by step setup on GitLab.com with the calc-app project, the .gitlab-ci.yml line by line, the pipeline editor, Tests tab and job artifacts, merge request pipelines that fail and recover, Pipelines must succeed and protected branches, pipeline schedules for nightly regression, Dev and QA change tables, common errors and a GitHub to GitLab comparison.',
    summary='A complete GitLab CI/CD setup from an empty project, line by line, with Dev and QA changes and a GitHub comparison.',
    keywords=['gitlab ci setup', '.gitlab-ci.yml', 'pipeline editor', 'merge request pipeline', 'pipelines must succeed', 'pipeline schedule', 'junit report', 'github vs gitlab'],
    recap='<p>Push one .gitlab-ci.yml, validate it in the editor, build once and test the artifact, show JUnit results in merge requests, require green pipelines, and schedule the long suites.</p>')
