# Chapter 7.2: GitHub Actions from scratch. Baby steps from an empty GitHub repository to a green CI run on every
# commit, using the sample calc-app project (tools/git-build/starter). Its workflows passed actionlint and every command
# in them was run for real. Covers the CI workflow line by line, what Dev and QA each change and why, branch
# protection with required checks, the QA regression workflow, and the errors beginners hit first.
# Sources: GitHub docs quickstart for Actions, workflow syntax, downloading workflow artifacts, about protected
# branches, actions/checkout, setup-python, upload-artifact and download-artifact READMEs, gh run download manual.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow, file, devqa, changes, babystep, starter

K = Kit()

K.code('junit', r'''
# QA reads the JUnit XML report that pytest wrote (--junitxml) and the pipeline kept as an artifact
import xml.etree.ElementTree as ET

report = """<testsuites><testsuite name="pytest" tests="5" failures="1" errors="0" skipped="0">
<testcase classname="tests.unit.test_calc" name="test_add"><failure message="assert -1 == 5"/></testcase>
<testcase classname="tests.unit.test_calc" name="test_subtract"/>
<testcase classname="tests.unit.test_calc" name="test_multiply"/>
<testcase classname="tests.unit.test_calc" name="test_divide"/>
<testcase classname="tests.unit.test_calc" name="test_divide_by_zero"/>
</testsuite></testsuites>"""

suite = ET.fromstring(report).find("testsuite")
total, failed = int(suite.get("tests")), int(suite.get("failures"))
print(f"{total - failed} passed, {failed} failed")
for case in suite.iter("testcase"):
    bad = case.find("failure")
    if bad is not None:
        print("FAILED", case.get("name"), "-", bad.get("message"))
''')

DL = '<a href="calc-app-starter.zip" download>calc-app-starter.zip</a>'

K.lesson('setup', 'Baby steps: from nothing to a green build', f'''
<p>Follow these steps once, in order, and you will have a real repository on GitHub where every commit starts a pipeline that lints, tests, builds a package, smoke tests that package and keeps it as a downloadable artifact. Tick each step as you finish it. Your ticks are saved in this browser.</p>
{babystep(1, 'Install the tools', '<p>You need Git (git --version should print 2.28 or newer, for init -b), Python 3.12 or newer and a free GitHub account. Optional: the GitHub CLI gh, for downloading artifacts from the terminal.</p>')}
{babystep(2, 'Get the sample project', f'<p>Download {DL} and unzip it. It holds a tiny calculator, its tests and both pipeline files. You can also type the files yourself from the next lessons.</p>' + sh('What you should have', """cd calc-app
find . -type f | sort""", """./.github/workflows/ci.yml
./.github/workflows/qa-regression.yml
./.gitignore
./.gitlab-ci.yml
./README.md
./app/__init__.py
./app/calc.py
./requirements.txt
./tests/smoke/test_smoke.py
./tests/unit/test_calc.py"""))}
{babystep(3, 'Prove it works on your computer first', '<p>A pipeline only repeats what works locally. If it fails here, it fails there.</p>' + sh('Run the unit tests locally', """python -m venv .venv
. .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m pytest -q tests/unit""", """.....                                                                    [100%]
5 passed in 0.02s""", 'Real output'))}
{babystep(4, 'Create an empty repository on GitHub', '<p>On github.com press New repository. Name it calc-app, choose Public or Private, and do not add a README, .gitignore or license, because the project already has them. Press Create repository and copy the URL it shows.</p>')}
{babystep(5, 'Make the first commit and push', sh('Turn the folder into a repository and push', """git init -b main
git add .
git commit -m "Start calc-app with CI"
git remote add origin https://github.com/YOUR-NAME/calc-app.git
git push -u origin main""", """branch 'main' set up to track 'origin/main'.""", 'The last line'))}
{babystep(6, 'Watch the pipeline run', '<p>Open the repository, then the Actions tab. A run of CI has started because you pushed to main. Click it. You see four jobs joined by lines: lint, then unit-tests, then build, then smoke-tests. Each turns green in about a minute. The commit on the Code tab now shows a green check mark.</p>')}
{babystep(7, 'Download the build artifact', '<p>On the run page scroll to the Artifacts section. You will see calc-app, unit-report and smoke-report. Click calc-app to download a zip that contains calc-app.zip, the exact file that the smoke tests used.</p>' + sh('Or with the GitHub CLI', """gh run list --workflow ci.yml --limit 3
gh run download RUN_ID -n calc-app -D downloaded"""))}
{babystep(8, 'Break it on purpose, on a branch', '<p>A pipeline you have never seen fail is a pipeline you do not trust.</p>' + sh('Change add() so it subtracts', """git switch -c broken-add
# in app/calc.py change: return a + b   to: return a - b
git commit -am "Break add on purpose"
git push -u origin broken-add""") + '<p>Open a pull request from broken-add to main. CI runs because of the pull_request trigger, unit-tests turns red and build and smoke-tests are skipped because they need it. Open the failed step to read the same message you would see locally:</p>' + sh('From the unit-tests log', 'python -m pytest -q tests/unit --junitxml=reports/unit.xml', """FAILED tests/unit/test_calc.py::test_add - assert -1 == 5
1 failed, 4 passed""", 'Real pytest output'))}
{babystep(9, 'Fix it and see green again', sh('Fix and push to the same branch', """# change it back to: return a + b
git commit -am "Fix add"
git push""") + '<p>The pull request updates and CI runs again. When it is green, merge it. The push to main runs CI once more on the merged code.</p>')}
{babystep(10, 'Make the green build a rule', '<p>In the repository open Settings, then Branches (or Rules, Rulesets), and add a rule for main: require a pull request before merging and require status checks to pass, choosing unit-tests and smoke-tests. From now on nobody can merge a red change into main.</p>')}
''', kw=['setup from scratch', 'first workflow', 'baby steps', 'Actions tab', 'green build', 'push trigger', 'artifacts section', 'gh run download', 'required status checks'])

K.lesson('ci', 'The CI workflow, line by line', f'''
<p>This is the full <code>.github/workflows/ci.yml</code> from the sample project. Click a marked line note to see why it is there.</p>
{starter('.github/workflows/ci.yml', {3: 'Three triggers: pushes to main, pull requests into main, and a manual Run workflow button.', 10: 'The GITHUB_TOKEN of this run may only read the code. Nothing here needs more.', 14: 'One run per branch or PR. A new push cancels the older, now useless, run.', 21: 'Every job starts on a fresh machine with no files, so every job checks out the code.', 24: 'Quoted so that YAML keeps it a string.', 26: 'compileall fails on any syntax error, the cheapest possible check, so it goes first.', 29: 'unit-tests starts only when lint is green.', 36: 'setup-python caches pip downloads, keyed on requirements.txt.', 39: 'python -m pytest puts the project folder on the import path. --junitxml writes a machine readable report.', 41: 'always() keeps the report even when tests fail, which is exactly when you need it.', 46: 'Reports are small and only useful for a while, so 14 days.', 59: 'Build the package once. Every later test uses this exact file.', 63: 'The artifact name other jobs and workflows use to find it.', 65: 'Fail the job if the zip was not made, instead of uploading nothing with a warning.', 69: 'smoke-tests waits for build, so the artifact exists.', 79: 'Pull the artifact made earlier in this run into dist/.', 84: 'PYTHONPATH points at the zip, so the tests import the packaged app, not the source folder.'})}
{viz('pipeline', preset='starter', plat='gha')}
{table(['Job', 'Needs', 'Makes', 'Fails when'], [
    ['lint', 'nothing', 'nothing', 'a .py file has a syntax error'],
    ['unit-tests', 'lint', 'unit-report (14 days)', 'a unit test fails'],
    ['build', 'unit-tests', 'calc-app (30 days)', 'the zip cannot be made'],
    ['smoke-tests', 'build', 'smoke-report (14 days)', 'the packaged app is broken or not the packaged one']])}
''', kw=['ci.yml', 'line by line', 'checkout', 'setup-python cache', 'junitxml', 'if always', 'upload-artifact', 'download-artifact', 'retention-days', 'if-no-files-found', 'PYTHONPATH'])

K.lesson('devqa', 'What Dev and QA change, and why', f'''
<p>The sample file is a safe start. Real teams change it, and developers and testers change different things for different reasons.</p>
{devqa('<p>Goal: the fastest trustworthy answer to "did I break something?".</p><ul><li>Keep lint and unit tests under a few minutes.</li><li>Run on every push to every branch so feedback comes before the pull request.</li><li>Use caches for dependencies.</li><li>Cancel outdated runs.</li><li>Build once and publish the artifact for others.</li></ul>',
       '<p>Goal: evidence that this exact build works, kept long enough to show later.</p><ul><li>Test the artifact, never a rebuild.</li><li>Run long suites on a schedule or on demand, not on every push.</li><li>Use fail-fast: false so one failure does not hide others.</li><li>Keep reports with if: always() and longer retention.</li><li>Make suites selectable with workflow_dispatch inputs.</li></ul>')}
{changes([
    ['branches: [main] under push', 'remove the filter, or add \'feature/**\'', 'feedback on every branch push, before a PR exists', 'Dev'],
    ['python-version: \'3.13\'', 'a matrix of \'3.12\', \'3.13\'', 'prove the code works on every version you support', 'Dev'],
    ['cache: pip', 'keep it, and pin versions in requirements.txt', 'stable cache key, faster installs, same packages every run', 'Dev'],
    ['retention-days: 30 on calc-app', 'longer for release builds, up to 90 (or the repository limit)', 'QA and support must reach the build that was released', 'QA'],
    ['retention-days: 14 on reports', '30 or more for regression reports', 'auditors and later bug reports need the evidence', 'QA'],
    ['smoke-tests job', 'add api-tests and e2e jobs that also need build, with strategy.fail-fast: false', 'more coverage of the same artifact, all failures visible at once', 'QA'],
    ['on: (no schedule)', 'a separate qa-regression.yml with schedule and workflow_dispatch', 'slow suites should not block every developer push', 'QA'],
    ['permissions: contents: read', 'add only what a new job needs, for example actions: read to download from other runs', 'least privilege limits damage from a compromised step', 'Both'],
    ['uses: actions/checkout@v7', 'pin to a full commit SHA in security sensitive repositories', 'a moved tag cannot change what runs (tj-actions, 2025)', 'Both']])}
{note('Change one thing at a time and push it on a branch with a pull request. The pull request runs the workflow file from the branch, so you see the result before main is affected.', 'tip')}
''', kw=['Dev changes', 'QA changes', 'retention', 'matrix', 'fail-fast false', 'schedule', 'workflow_dispatch inputs', 'least privilege', 'pin SHA'])

K.lesson('qa', 'The QA regression workflow and common errors', f'''
<p>QA runs the full suite every weekday night and whenever someone presses Run workflow, always against a build that CI already made. It finds the newest green CI run on main, or takes a run id you type in, and pulls the calc-app artifact from it.</p>
{starter('.github/workflows/qa-regression.yml', {5: '02:30 UTC, Monday to Friday.', 6: 'The Run workflow button, with an optional input.', 15: 'actions: read lets gh read runs and artifacts of other workflow runs in this repository.', 21: 'The gh CLI is installed on GitHub hosted runners and reads its token from GH_TOKEN.', 32: 'The input arrives through an environment variable, never pasted into the script, so a strange value cannot become a command.', 35: 'The newest successful CI run on main, as a run id.', 38: 'Save the id as a step output for the next step.', 40: 'Download one named artifact from that other run into dist/.', 42: 'The whole suite, unit and smoke, against the packaged build.'})}
{code('junit')}
{table(['You see', 'Cause', 'Fix'], [
    ['No run starts after a push', 'the file is not in .github/workflows/, the YAML is invalid, or the branch filter does not match', 'check the path, open the file on GitHub (it shows YAML errors), check on: push: branches'],
    ['No such file or directory: requirements.txt', 'no actions/checkout step in that job', 'add uses: actions/checkout as the first step of every job'],
    ['ModuleNotFoundError: No module named \'app\'', 'pytest started without the project on the import path', 'run python -m pytest, or set PYTHONPATH'],
    ['download-artifact cannot find calc-app', 'the name differs from the upload, or the job lacks needs: build', 'use the same name and add needs'],
    ['gh run download fails with HTTP 403 or 404', 'the workflow token lacks actions: read, or the artifact expired', 'add the permission, check the retention period'],
    ['A required check stays at Expected and never reports', 'the rule names a job that no longer exists', 'rename the check in the rule or keep the job id']])}
{ladder(
    '<p>Put the YAML file in .github/workflows/, push, and GitHub runs your tests on every commit. Break it once on purpose so you know what red looks like.</p>',
    '<p>The CI workflow chains lint, unit-tests, build and smoke-tests with needs, builds one artifact and tests it. Branch protection turns the green checks into a merge rule. QA pulls the same artifact into a scheduled workflow.</p>',
    '<p>Each choice trades speed against evidence: triggers, caches and cancel-in-progress make Dev feedback fast, while retention, fail-fast: false and separate scheduled suites give QA durable results.</p>',
    '<p>Mature setups add reusable workflows shared across repositories, artifact attestations that sign which workflow built which file, and test impact analysis that runs only the tests a change can affect.</p>')}
''', kw=['qa-regression.yml', 'schedule', 'workflow_dispatch', 'actions read', 'GH_TOKEN', 'gh run list', 'GITHUB_OUTPUT', 'junit report', 'troubleshooting', 'ModuleNotFoundError'])

K.quiz('e', 'What makes the pipeline start after git push to main?', ['You press a button', 'on: push: branches: [main] in a file under .github/workflows/', 'The README', 'A webhook you must write'], 1, 'The trigger.', 'GitHub reads the workflow files in the pushed commit.')
K.quiz('e', 'Why run the tests on your own computer before pushing the workflow?', ['It is required by GitHub', 'If it fails locally, it fails in CI too, and local is faster to debug', 'To create the artifact', 'To get a token'], 1, 'Local first.', 'A pipeline only repeats commands that work.')
K.quiz('e', 'Where do you download an artifact in the GitHub web page?', ['Settings', 'The Artifacts section of the workflow run page', 'The Code tab', 'Releases only'], 1, 'Run page.', 'Or use gh run download.')
K.quiz('m', 'Why does every job in ci.yml start with actions/checkout?', ['Style', 'Each job runs on a fresh machine with no files', 'To save cache', 'To log in'], 1, 'Fresh runner.', 'Jobs share nothing unless you pass artifacts.')
K.quiz('m', 'Why does the report upload use if: always()?', ['To run faster', 'So the report is kept even when tests fail', 'To skip it on main', 'It is required'], 1, 'Failures need evidence.', 'Without it the step is skipped after a failure.')
K.quiz('m', 'unit-tests fails. What happens to build and smoke-tests?', ['They run anyway', 'They are skipped because they need unit-tests', 'They fail too', 'They retry'], 1, 'needs chain.', 'A job runs only when the jobs it needs succeeded, unless its if says otherwise.')
K.quiz('m', 'Which change is mainly a QA change?', ['Adding cache: pip', 'Cancel in progress', 'Longer retention for regression reports', 'Running lint first'], 2, 'Evidence.', 'QA needs results to stay available.')
K.quiz('h', 'Why does the smoke test set PYTHONPATH=dist/calc-app.zip?', ['Speed', 'So it imports the packaged build, proving the artifact itself works', 'Because the source folder is missing', 'To skip unit tests'], 1, 'Test the artifact.', 'test_smoke checks that app.__file__ comes from the zip.')
K.quiz('h', 'Why does qa-regression.yml pass inputs.ci_run_id through env as RUN_ID?', ['Shorter', 'So a crafted input cannot be injected into the shell script', 'gh needs it', 'Inputs cannot be used in run'], 1, 'Data, not code.', 'Same rule as PR titles.')
K.quiz('x', 'QA wants to test the build of CI run 123 from yesterday. Which permission must the QA workflow have?', ['contents: write', 'actions: read', 'packages: write', 'pull-requests: write'], 1, 'Read runs and artifacts.', 'Artifacts belong to Actions.')

K.calc('e', 'The CI chain runs lint 1, unit-tests 2, build 1, smoke-tests 2 minutes. How many minutes until the artifact exists?', '4', 'Up to build.',
       ['lint ends at 1.', 'unit-tests ends at 3.', eq('build ends at 4')], check=4)
K.calc('e', 'unit-tests fails at minute 3. How many of the four jobs ran?', '2', 'Skipped jobs do not run.',
       ['lint ran and passed.', 'unit-tests ran and failed.', eq('build and smoke-tests were skipped: 2 ran')], check=2)
K.calc('m', 'calc-app has retention-days: 30. The run finished on 3 November. On which day of December does the artifact expire?', '3', 'November has 30 days.',
       ['3 November plus 27 days is 30 November.', 'Three more days reach 30 days in total.', eq('3 December')], check=3)
K.calc('m', 'You add a matrix of 2 Python versions to unit-tests only. How many unit-tests jobs run per push?', '2', 'One per value.',
       ['matrix python: [3.12, 3.13].', 'One job per value.', eq('2 jobs')], check=2)
K.calc('h', 'Without cancel-in-progress, a developer pushes 5 times in 10 minutes and each 6 minute run finishes. With it, only the last run finishes and each cancelled run had used 2 minutes. Runner minutes saved?', '16', 'Compare totals.',
       ['Without: 5 × 6 = 30 minutes.', 'With: 4 × 2 + 6 = 14 minutes.', eq('30 - 14 = 16 minutes saved')], check=16)
K.calc('h', 'The regression workflow runs Monday to Friday. How many scheduled runs in 4 weeks?', '20', 'Five a week.',
       ['Cron day of week 1-5.', '5 runs per week.', eq('5 × 4 = 20 runs')], check=20)

K.assign('junitsum', 'm', 'Summarise a test report',
         '<p>Write <code>summary(xml_text)</code> that reads a JUnit XML report like the one in this chapter and returns <code>[passed, failed, failed_names]</code>, where failed_names is a sorted list of test names that have a failure or error element.</p>',
         '''
import xml.etree.ElementTree as ET

def summary(xml_text):
    # your code here
    pass
''', [("summary('<testsuite><testcase name=\"a\"/><testcase name=\"b\"><failure/></testcase></testsuite>')", [1, 1, ['b']]),
      ("summary('<testsuites><testsuite><testcase name=\"z\"><error/></testcase><testcase name=\"y\"><failure/></testcase></testsuite></testsuites>')", [0, 2, ['y', 'z']]),
      ("summary('<testsuite><testcase name=\"ok\"/></testsuite>')", [1, 0, []])],
         '''
import xml.etree.ElementTree as ET

def summary(xml_text):
    root = ET.fromstring(xml_text)
    passed, bad = 0, []
    for case in root.iter('testcase'):
        if case.find('failure') is not None or case.find('error') is not None:
            bad.append(case.get('name'))
        else:
            passed += 1
    return [passed, len(bad), sorted(bad)]
''', 'iter(\'testcase\') finds test cases at any depth, so it works with and without the testsuites wrapper.', '<p>Skipped tests have a skipped element. A fuller version would count them separately.</p>')
K.assign('willrun', 'e', 'Will ci.yml run',
         '<p>Write <code>ci_runs(event, branch)</code> for the triggers of the sample ci.yml: push to main, pull_request into main, and workflow_dispatch on any branch. For a pull_request, branch is the target branch. Return True or False.</p>',
         '''
def ci_runs(event, branch):
    # your code here
    pass
''', [("ci_runs('push', 'main')", True), ("ci_runs('push', 'broken-add')", False), ("ci_runs('pull_request', 'main')", True),
      ("ci_runs('pull_request', 'release')", False), ("ci_runs('workflow_dispatch', 'broken-add')", True), ("ci_runs('schedule', 'main')", False)],
         '''
def ci_runs(event, branch):
    if event == 'workflow_dispatch':
        return True
    if event in ('push', 'pull_request'):
        return branch == 'main'
    return False
''', 'Handle each event in the on section, and return False for events that are not listed.', '<p>This is why the broken-add branch only got a CI run once the pull request was opened.</p>')

K.must('From scratch', 'Test locally, create an empty repo, commit the project with .github/workflows/ci.yml, push to main, watch the Actions tab, download the artifact, break it on a branch, fix it, then require the checks on main.')
K.must('ci.yml', 'push and pull_request on main plus workflow_dispatch, permissions contents: read, concurrency per ref. lint, unit-tests, build, smoke-tests chained by needs. Checkout in every job.')
K.must('Artifacts in the flow', 'build uploads calc-app once (if-no-files-found: error), smoke-tests downloads it with download-artifact in the same run, reports kept with if: always().')
K.must('Dev versus QA changes', 'Dev: triggers, matrix, cache, cancel-in-progress. QA: test the artifact, separate scheduled suites, fail-fast false, longer retention, inputs.')
K.must('QA regression', 'schedule plus workflow_dispatch input, actions: read, GH_TOKEN, gh run list for the last green run, gh run download -n calc-app, inputs passed through env.')

T = K.topic(
    slug='gha-scratch', topic='gha-scratch', step=(7, 'GitHub Actions', 'gh-actions', 'Write GitHub Actions workflows from the first line: events, jobs, matrix and contexts, then a complete Dev and QA pipeline built from scratch, then artifacts and caches including how to pull a build from any run.', 'Intermediate'),
    title='GitHub Actions from scratch: a green build on every commit', short='Actions from scratch', badge='7.2', minutes=70, added='2026-11-02',
    lead='Baby steps from an empty repository to a pipeline that lints, tests, builds, smoke tests and keeps the package on every commit, then what developers and testers each change, and a QA regression workflow that pulls the build from CI.',
    desc='step by step setup with the downloadable calc-app project, the CI workflow line by line, needs, cache, JUnit reports, upload and download of the build artifact, breaking and fixing a build through a pull request, required status checks, Dev and QA change tables, the scheduled QA regression workflow with gh run download, and the most common errors.',
    summary='A complete GitHub Actions setup from an empty repository, explained line by line, with Dev and QA changes and a QA regression workflow.',
    keywords=['github actions setup', 'ci.yml', 'green build', 'upload-artifact', 'download-artifact', 'qa regression', 'gh run download', 'branch protection'],
    recap='<p>One YAML file and one push give a pipeline. Test locally first, build once, test the artifact, require the checks on main, and let QA pull the same build on its own schedule.</p>')
