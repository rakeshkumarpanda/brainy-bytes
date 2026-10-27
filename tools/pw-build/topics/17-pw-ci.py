import importlib.util
import os

from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, table, tip

# the framework chapter reads the four real projects, this chapter reuses them
_spec = importlib.util.spec_from_file_location('fw16', os.path.join(os.path.dirname(os.path.abspath(__file__)), '16-pw-framework.py'))
fw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fw)

MODULE = fw.MODULE
TREE, run_files, js_show, JM, JT = fw.TREE, fw.run_files, fw.js_show, fw.JM, fw.JT
JAVA_NOISE = fw.JAVA_NOISE

IMG_NODE = 'mcr.microsoft.com/playwright:v1.63.0-noble'
IMG_PY = 'mcr.microsoft.com/playwright/python:v1.63.0-noble'
IMG_JAVA = 'mcr.microsoft.com/playwright/java:v1.63.0-noble'
DOCKER = 'docker run --rm --init --ipc=host --network host -v "$PWD":/work -w /work'
# the build machine reaches the internet through a proxy, so containers get its settings too (not shown on the page)
PROXY = ('-e HTTPS_PROXY -e https_proxy -e NO_PROXY -e no_proxy -e npm_config_https_proxy '
         '-e NODE_EXTRA_CA_CERTS=/ca.crt -e PIP_CERT=/ca.crt -v /root/.ccr/ca-bundle.crt:/ca.crt:ro')
M2 = os.path.expanduser('~/.m2')
DOCKER_NOISE = [(r'(?m)^WARNING: IPv4 forwarding is disabled.*\n', ''), (r'(?m)^WARNING: Running pip as the .root. user.*\n', ''),
                (r'(?m)^\n?\[notice\].*\n', ''), (r'(?m)^npm notice.*\n', '')]


def with_files(lang, extra):
    return {**run_files(lang), **extra}


# ---------- the workflow files ----------
def wf(lang):
    name = '.github/workflows/playwright.yml' if lang in ('ts', 'js') else '.github/workflows/tests.yml'
    return {name: TREE[lang][name]}


SHARD_NODE = '''name: Playwright tests (sharded)
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false                # let every shard finish, even if one fails
      matrix:
        shardIndex: [1, 2]
        shardTotal: [2]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: 22
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }} --reporter=blob
        env:
          BASE_URL: ${{ vars.BASE_URL }}
          ASHA_PASSWORD: ${{ secrets.ASHA_PASSWORD }}
          RAVI_PASSWORD: ${{ secrets.RAVI_PASSWORD }}
      - uses: actions/upload-artifact@v5
        if: ${{ !cancelled() }}
        with:
          name: blob-report-${{ matrix.shardIndex }}
          path: blob-report
          retention-days: 1

  merge-reports:
    if: ${{ !cancelled() }}           # merge even when a shard failed
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: 22
      - run: npm ci
      - uses: actions/download-artifact@v5
        with:
          path: all-blob-reports
          pattern: blob-report-*
          merge-multiple: true
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
      - uses: actions/upload-artifact@v5
        with:
          name: html-report--attempt-${{ github.run_attempt }}
          path: playwright-report
          retention-days: 14'''

SHARD_PY = '''name: Playwright tests (split)
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        group: [1, 2]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.13"
      - run: pip install -r requirements.txt
      - run: python -m playwright install --with-deps chromium
      - run: pytest --splits 2 --group ${{ matrix.group }} --junitxml=results/junit-${{ matrix.group }}.xml
        env:
          BASE_URL: ${{ vars.BASE_URL }}
          ASHA_PASSWORD: ${{ secrets.ASHA_PASSWORD }}
          RAVI_PASSWORD: ${{ secrets.RAVI_PASSWORD }}
      - uses: actions/upload-artifact@v5
        if: ${{ !cancelled() }}
        with:
          name: results-${{ matrix.group }}
          path: results/'''

SHARD_JAVA = '''name: Playwright tests (by feature)
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        feature: [smoke, products, cart]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-java@v5
        with:
          distribution: temurin
          java-version: "21"
          cache: maven
      - run: mvn -B test-compile
      - run: mvn -B exec:java -e -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.classpathScope=test -Dexec.args="install --with-deps chromium"
      - run: mvn -B test -Dtest="com.brainy.shop.tests.${{ matrix.feature }}.*Test"
        env:
          BASE_URL: ${{ vars.BASE_URL }}
          ASHA_PASSWORD: ${{ secrets.ASHA_PASSWORD }}
          RAVI_PASSWORD: ${{ secrets.RAVI_PASSWORD }}
      - uses: actions/upload-artifact@v5
        if: ${{ !cancelled() }}
        with:
          name: surefire-${{ matrix.feature }}
          path: target/surefire-reports/'''

JENKINS_NODE = '''pipeline {
  agent { docker { image 'mcr.microsoft.com/playwright:v1.63.0-noble' } }
  environment {
    CI = 'true'                                   // Jenkins does not set CI by itself
    BASE_URL = 'https://staging.shop.example'
    ASHA_PASSWORD = credentials('asha-password')  // a Secret text credential in Jenkins
  }
  stages {
    stage('Install') {
      steps { sh 'npm ci' }
    }
    stage('Test') {
      steps { sh 'npx playwright test' }
    }
  }
  post {
    always {
      junit 'results/junit.xml'
      archiveArtifacts artifacts: 'playwright-report/**', allowEmptyArchive: true
    }
  }
}'''

JENKINS_PY = '''pipeline {
  agent {
    docker {
      image 'mcr.microsoft.com/playwright/python:v1.63.0-noble'
      args '-u root'                              // so pip may install into the image
    }
  }
  environment {
    BASE_URL = 'https://staging.shop.example'
    ASHA_PASSWORD = credentials('asha-password')
  }
  stages {
    stage('Install') {
      steps { sh 'pip install -r requirements.txt' }
    }
    stage('Test') {
      steps { sh 'pytest -n 2 --junitxml=results/junit.xml' }
    }
  }
  post {
    always {
      junit 'results/junit.xml'
      archiveArtifacts artifacts: 'test-results/**', allowEmptyArchive: true
    }
  }
}'''

JENKINS_JAVA = '''pipeline {
  agent { docker { image 'mcr.microsoft.com/playwright/java:v1.63.0-noble' } }
  environment {
    BASE_URL = 'https://staging.shop.example'
    ASHA_PASSWORD = credentials('asha-password')
  }
  stages {
    stage('Test') {
      steps { sh 'mvn -B test' }
    }
  }
  post {
    always {
      junit 'target/surefire-reports/*.xml'
      archiveArtifacts artifacts: 'traces/**', allowEmptyArchive: true
    }
  }
}'''

GITLAB = '''stages:
  - test

e2e:
  stage: test
  image: mcr.microsoft.com/playwright:v1.63.0-noble
  parallel: 2                    # two jobs, CI_NODE_INDEX is 1 and 2
  script:
    - npm ci
    - npx playwright test --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL
  artifacts:
    when: always
    paths:
      - playwright-report/
    reports:
      junit: results/junit.xml'''

AZURE = '''trigger:
  - main

pool:
  vmImage: ubuntu-latest

steps:
  - task: UseNode@1
    inputs:
      version: '22'
    displayName: Install Node.js
  - script: npm ci
    displayName: npm ci
  - script: npx playwright install --with-deps chromium
    displayName: Install Chromium
  - script: npx playwright test
    displayName: Run Playwright tests
    env:
      CI: 'true'
      ASHA_PASSWORD: $(ASHA_PASSWORD)
  - task: PublishTestResults@2
    condition: succeededOrFailed()
    inputs:
      testResultsFormat: JUnit
      testResultsFiles: results/junit.xml
  - task: PublishPipelineArtifact@1
    condition: succeededOrFailed()
    inputs:
      targetPath: playwright-report
      artifact: playwright-report'''

FOCUS_TS = '''import { test, expect } from '../../src/fixtures/index';

test.describe('product sort', () => {
  test.only('the cheapest product comes first', async ({ productsPage }) => {   // left behind after debugging
    await productsPage.open();
    await expect(productsPage.cards.first()).toContainText('Gel pen');
  });
});'''

TS_FAIL = [(r'(?ms)^\s+\d+ \|.*?(?=^\s+at |\Z)', ''), (r'(?m)^\s+Error Context: .*\n', '')]

CODES = {
    'cimode': four('Run the suite the way the pipeline runs it',
                   java=jv(run_files('java'), kind='testng', cmd='mvn test && ls target/surefire-reports | grep xml', show=['pom.xml'], replace=JAVA_NOISE),
                   py=py(run_files('python'), ini=None, cmd='pytest -n 2 --junitxml=results/junit.xml && ls results', show=['pytest.ini'],
                         replace=[(r'(?m)^(=+ test session starts =+|platform .*|rootdir: .*|configfile: .*|plugins: .*)\n', '')]),
                   js=js(run_files('js'), config=None, cmd='CI=true npx playwright test && ls results', show=['playwright.config.js']),
                   ts=ts(run_files('ts'), cmd='CI=true npx playwright test && ls results', show=['playwright.config.ts']),
                   result='The same seven tests passed, this time with the settings a pipeline uses. <code>CI=true</code> is what GitHub Actions and GitLab set on every job, and the config reads it: two workers, two retries, forbidOnly, and a JUnit XML file next to the HTML report. pytest wrote its JUnit file with <code>--junitxml</code> and spread the tests over two processes with <code>-n 2</code> from pytest-xdist. Surefire writes its XML files for every run. Every CI server can read JUnit XML, which is why all four runs leave one behind.'),
    'forbid': one('A forgotten test.only fails the pipeline',
                  ts(with_files('ts', {'tests/products/sort.spec.ts': FOCUS_TS}), cmd='CI=true npx playwright test', expect='fail',
                     show=['tests/products/sort.spec.ts'], replace=TS_FAIL),
                  result='On a laptop, test.only would quietly run one test and report success. With <code>CI=true</code> the config turns on forbidOnly, and the whole run stops before any test starts. Without it, a pull request could pass CI having run one test out of seven.'),
    'gha': four('The workflow file each project keeps in .github/workflows',
                java=shown(wf('java'), 'java', 'git push', note='Runs on GitHub, shown here'),
                py=shown(wf('python'), 'py', 'git push', note='Runs on GitHub, shown here'),
                js=shown(wf('js'), 'js', 'git push', note='Runs on GitHub, shown here'),
                ts=shown(wf('ts'), 'ts', 'git push', note='Runs on GitHub, shown here'),
                result='These are the real workflow files of the four framework projects. GitHub runs them on every push to main and on every pull request. The steps are always the same five: get the code, install the language, install the packages, install the browser with its system libraries, run the tests, and keep the results even when tests fail.'),
    'secret': four('What a run looks like when a secret is wrong',
                   java=jv(run_files('java'), kind='testng', cmd='ASHA_PASSWORD=wrong mvn test -Dtest="com.brainy.shop.tests.smoke.*Test"', expect='fail',
                           show=[JM + 'data/Users.java'], replace=JAVA_NOISE + [(r'(?m)^\tat .*\n', '')]),
                   py=py(run_files('python'), ini=None, cmd='ASHA_PASSWORD=wrong pytest tests/smoke -q --tb=line', expect='fail',
                         show=['framework/data/users.py']),
                   js=js(run_files('js'), config=None, cmd='ASHA_PASSWORD=wrong npx playwright test tests/smoke --reporter=line', expect='fail',
                         show=['src/data/users.js'], replace=TS_FAIL),
                   ts=ts(run_files('ts'), cmd='ASHA_PASSWORD=wrong npx playwright test tests/smoke --reporter=line', expect='fail',
                         show=['src/data/users.ts'], replace=TS_FAIL),
                   result='The password came from the environment variable, so the framework signed in with the wrong one and the greeting never appeared. The wrong password test still passed, because it sets its own password. This is exactly what a team sees when a secret is missing or out of date in the CI settings: the sign in tests fail and everything else is fine. The fix is in the CI settings, not in the code.'),
    'matrix': four('Each matrix job runs its own part of the suite',
                   java=jv({**run_files('java'), '.github/workflows/tests.yml': SHARD_JAVA}, kind='testng',
                           cmd='for f in smoke products cart; do echo "== job $f"; mvn -o -B -Dstyle.color=never test -Dtest="com.brainy.shop.tests.$f.*Test" | grep -E "Running|Tests run:" | grep -v " in " | sed "s/^\\[INFO\\] //"; done',
                           shown_cmd='for f in smoke products cart; do echo "== job $f"; mvn test -Dtest="com.brainy.shop.tests.$f.*Test"; done',
                           show=['.github/workflows/tests.yml'], replace=JAVA_NOISE),
                   py=py({**run_files('python'), '.github/workflows/tests.yml': SHARD_PY}, ini=None, replace=[(r'\n{3,}', '\n\n')],
                         cmd='for i in 1 2; do echo "== job group $i of 2"; pytest --splits 2 --group $i -q; done',
                         show=['.github/workflows/tests.yml']),
                   js=js({**run_files('js'), '.github/workflows/playwright.yml': SHARD_NODE}, config=None,
                         cmd='for i in 1 2; do echo "== job shard $i of 2"; npx playwright test --shard=$i/2 --reporter=blob; mkdir -p all-blob-reports; mv blob-report/*.zip all-blob-reports/; done; echo "== job merge-reports"; npx playwright merge-reports --reporter=list ./all-blob-reports',
                         show=['.github/workflows/playwright.yml']),
                   ts=ts({**run_files('ts'), '.github/workflows/playwright.yml': SHARD_NODE},
                         cmd='for i in 1 2; do echo "== job shard $i of 2"; npx playwright test --shard=$i/2 --reporter=blob; mkdir -p all-blob-reports; mv blob-report/*.zip all-blob-reports/; done; echo "== job merge-reports"; npx playwright merge-reports --reporter=list ./all-blob-reports',
                         show=['.github/workflows/playwright.yml']),
                   result='The loop does here, one after another, what the matrix does on GitHub at the same time on separate machines. Playwright Test split the seven tests into four and three, each shard saved a blob report, and merge-reports joined them into one result for the whole run. pytest-split split the tests into two groups. Maven has no shard option, so the Java matrix runs one test package per job with <code>-Dtest</code>, which also overrides the suite file.'),
    'docker': four('The framework inside the official Playwright image',
                   java=jv(run_files('java'), kind='testng',
                           cmd=f'{DOCKER} -v {M2}:/root/.m2 {IMG_JAVA} mvn -o -B -Dstyle.color=never test -Dsuite=testng-smoke.xml',
                           shown_cmd=f'{DOCKER} -v "$HOME/.m2":/root/.m2 {IMG_JAVA} mvn -B test -Dsuite=testng-smoke.xml',
                           show=['pom.xml'], replace=JAVA_NOISE + DOCKER_NOISE),
                   py=py({**run_files('python'), 'requirements.txt': TREE['python']['requirements.txt']}, ini=None,
                         cmd=f'{DOCKER} {PROXY} {IMG_PY} /bin/bash -c "pip install -q -r requirements.txt && pytest -m smoke"',
                         shown_cmd=f'{DOCKER} {IMG_PY} /bin/bash -c "pip install -q -r requirements.txt && pytest -m smoke"',
                         show=['requirements.txt'], replace=DOCKER_NOISE),
                   js=js({**run_files('js'), 'package-lock.json': TREE['js']['package-lock.json']}, config=None,
                         cmd=f'{DOCKER} {PROXY} {IMG_NODE} /bin/bash -c "npm ci --no-audit --no-fund && npx playwright test --grep @smoke"',
                         shown_cmd=f'{DOCKER} {IMG_NODE} /bin/bash -c "npm ci && npx playwright test --grep @smoke"',
                         show=['package.json'], replace=DOCKER_NOISE),
                   ts=ts({**run_files('ts'), 'package-lock.json': TREE['ts']['package-lock.json']},
                         cmd=f'{DOCKER} {PROXY} {IMG_NODE} /bin/bash -c "npm ci --no-audit --no-fund && npx playwright test --grep @smoke"',
                         shown_cmd=f'{DOCKER} {IMG_NODE} /bin/bash -c "npm ci && npx playwright test --grep @smoke"',
                         show=['package.json'], replace=DOCKER_NOISE),
                   result='The smoke tests passed inside the official images, which already hold Chromium, Firefox, WebKit and every system library they need. The image does not hold your packages, so npm ci, pip install or Maven still install them. The image tag v1.63.0 matches the Playwright version in the project. If the two differ, Playwright cannot find its browsers. <code>--network host</code> lets the container reach the shop running on this machine. Against a staging server it is not needed.'),
    'jenkins': four('A Jenkinsfile for each project',
                    java=shown({'Jenkinsfile': JENKINS_JAVA}, 'java', note='Runs on Jenkins, shown here'),
                    py=shown({'Jenkinsfile': JENKINS_PY}, 'py', note='Runs on Jenkins, shown here'),
                    js=shown({'Jenkinsfile': JENKINS_NODE}, 'js', note='Runs on Jenkins, shown here'),
                    ts=shown({'Jenkinsfile': JENKINS_NODE}, 'ts', note='Runs on Jenkins, shown here'),
                    result='Jenkins starts the job inside the same official image, so nothing has to be installed on the Jenkins machine except Docker. credentials() reads a secret stored in Jenkins. The junit step reads the JUnit XML and shows passed and failed tests on the build page, and archiveArtifacts keeps the report.'),
    'gitlab': one('GitLab CI with two parallel jobs', shown({'.gitlab-ci.yml': GITLAB}, 'ts', note='Runs on GitLab, shown here'),
                  result='GitLab starts two copies of the job because of <code>parallel: 2</code>, and gives each one CI_NODE_INDEX and CI_NODE_TOTAL, which fit straight into --shard. The JUnit report appears in the merge request.'),
    'azure': one('Azure Pipelines', shown({'azure-pipelines.yml': AZURE}, 'ts', note='Runs on Azure DevOps, shown here'),
                 result='Azure Pipelines does not set CI, so the step sets it, and the config switches to its CI settings. PublishTestResults shows the JUnit results in the Tests tab, and PublishPipelineArtifact keeps the HTML report.'),
}

DG = {
    'pipe': {'t': 'What happens after git push', 'w': 900, 'h': 230,
             'n': [['push', 20, 85, 120, 56, 'git push', {'c': 0, 'sub': 'or a pull request', 'i': 'A push or a pull request starts the workflow.'}],
                   ['vm', 170, 85, 130, 56, 'fresh machine', {'c': 5, 'sub': 'runner', 'i': 'CI gives the job a clean machine or container every time.'}],
                   ['inst', 330, 20, 140, 56, 'install', {'c': 1, 'sub': 'packages, browser', 'i': 'npm ci, pip install or Maven, then the browser with its system libraries.'}],
                   ['test', 330, 150, 140, 56, 'run tests', {'c': 2, 'sub': 'CI settings', 'i': 'Retries, workers and reporters for CI, with secrets from the CI settings.'}],
                   ['rep', 510, 85, 140, 56, 'keep results', {'c': 3, 'sub': 'reports, traces', 'i': 'Reports and traces are uploaded even when tests fail.'}],
                   ['gate', 690, 85, 170, 56, 'merge allowed?', {'c': 4, 'sub': 'required check', 'i': 'A pull request can only be merged when the check is green.'}]],
             'e': [['push', 'vm'], ['vm', 'inst'], ['inst', 'test'], ['test', 'rep'], ['rep', 'gate']],
             'st': [[['push'], 'A developer pushes code or opens a pull request.'],
                    [['vm', 'push>vm'], 'The CI service starts a fresh machine for the job.'],
                    [['inst', 'vm>inst'], 'It installs the packages and the browser.'],
                    [['test', 'inst>test'], 'It runs the tests with the CI settings and secrets.'],
                    [['rep', 'test>rep'], 'It keeps the reports and traces, pass or fail.'],
                    [['gate', 'rep>gate'], 'The result decides whether the pull request can be merged.']]},
}

PARTS = [
    part('what', '🚦', 'What CI does for your tests', f'''
<p><b>Continuous integration</b>, CI for short, means a server runs your tests every time someone pushes code or opens a pull request. Nobody has to remember to run them, and a change that breaks the shop is caught before it is merged. <b>Continuous delivery</b>, the CD, goes on to deploy the change when the checks are green.</p>
<div class="viz" data-viz="flow" data-k="pipe"></div>
{table(['', 'On your laptop', 'On CI'], [
    ['the machine', 'yours, with everything already installed', 'a fresh machine for every run'],
    ['the browser', 'installed once', 'installed in every run, or already in a Docker image'],
    ['the settings', 'a local .env file', 'variables and secrets in the CI settings'],
    ['a failure', 'you watch it happen', 'you read the report, the logs and the trace afterwards'],
    ['test.only', 'handy while debugging', 'must fail the run'],
])}
{tip('The Playwright documentation sums CI up in three steps: make sure the machine can run browsers, install the packages and browsers, then run the tests. Everything in this chapter is a version of those three steps.', 'tip')}
''', easy=True, kw=['CI', 'CD', 'continuous integration', 'pipeline', 'pull request', 'runner']),

    part('cimode', '🤖', 'Running the suite the way the pipeline does', f'''
<p>Most CI services set the environment variable <code>CI=true</code>. GitHub Actions and GitLab do it on every job. Jenkins and Azure Pipelines do not, so their pipeline files set it. The config reads it and changes a few settings:</p>
{table(['Setting on CI', 'Why'], [
    ['forbidOnly: true', 'a forgotten test.only stops the run instead of skipping the rest'],
    ['retries: 2', 'a test that fails once and then passes is reported as flaky, not hidden'],
    ['a fixed number of workers', 'CI machines are smaller than laptops. The Playwright docs suggest 1 for the most stable runs, or sharding for speed'],
    ['JUnit XML and HTML reporters', 'the CI server reads the XML, and people read the HTML'],
    ['trace: on-first-retry', 'every retried test leaves a trace to open later'],
])}
[[cimode]]
[[forbid]]
{tip('pytest and TestNG have no test.only, so there is nothing to forbid. In pytest the closest mistake is leaving <code>-k</code> or a single file in the CI command, so keep the command in the workflow file and review changes to it.', 'pro')}
''', kw=['CI=true', 'forbidOnly', 'retries', 'workers', 'junit', 'junitxml', 'surefire', 'xdist']),

    part('github', '🐙', 'GitHub Actions, line by line', f'''
<p>A GitHub Actions workflow is a YAML file in <code>.github/workflows/</code>. Each framework project from the last chapter already has one. Pick your language at the top of the page.</p>
[[gha]]
{table(['Line', 'What it does'], [
    ['on: push / pull_request', 'when the workflow runs'],
    ['runs-on: ubuntu-latest', 'a fresh Linux machine from GitHub'],
    ['timeout-minutes: 30', 'stops a job that hangs. Keep it above any global timeout in the test config'],
    ['actions/checkout', 'gets the code of the commit'],
    ['setup-node, setup-python, setup-java', 'installs the language version'],
    ['npm ci, pip install -r, mvn', 'installs the exact package versions from the lock or requirements file'],
    ['playwright install --with-deps chromium', 'downloads Chromium and installs the Linux libraries it needs'],
    ['env: with secrets. and vars.', 'hands settings and passwords to the tests'],
    ['if: ${{ !cancelled() }}', 'uploads the results even when tests failed, which is when you need them most'],
    ['upload-artifact', 'keeps the report as a download on the run page'],
])}
{table(['Trigger', 'Use it for'], [
    ['push to main', 'checking what was merged'],
    ['pull_request', 'checking a change before it is merged'],
    ['schedule with cron', 'a nightly run of the full suite, for example in every browser'],
    ['workflow_dispatch', 'a Run workflow button for runs by hand'],
    ['deployment_status', 'testing a preview or staging deployment once it is ready'],
])}
{tip('In the repository settings, a branch rule can make this workflow a required check. Then a pull request cannot be merged while its tests are red.', 'pro')}
''', kw=['GitHub Actions', 'workflow', 'yaml', 'upload-artifact', 'install --with-deps', 'triggers', 'cron', 'required check']),

    part('secrets', '🔐', 'Secrets and settings per environment', f'''
<p>A pipeline needs the same settings as your laptop: the address of the app and the test passwords. They come from the CI settings, never from the code.</p>
{table(['Kind', 'In GitHub', 'In the workflow', 'Seen in logs'], [
    ['a setting such as BASE_URL', 'Settings, Secrets and variables, Actions, Variables', '${{ vars.BASE_URL }}', 'yes'],
    ['a password', 'the same page, Secrets', '${{ secrets.ASHA_PASSWORD }}', 'no, GitHub masks it as ***'],
])}
<p>The framework reads both from the environment, with a local default. Here is what happens when the secret is wrong:</p>
[[secret]]
{tip('Secrets are not given to workflows that run for pull requests from forks, so a fork cannot read your passwords. Tests that need them are skipped or fail there, which is expected.', 'warn')}
''', kw=['secrets', 'variables', 'vars', 'environment', 'BASE_URL', 'masked', 'credentials']),

    part('shards', '🧩', 'Shards with a matrix, and one merged report', f'''
<p>A <b>matrix</b> starts the same job several times with different values. Give each copy a different shard and the suite runs on several machines at once. For Playwright Test, each shard saves a <b>blob report</b>, and a last job merges them into one HTML report.</p>
[[matrix]]
{table(['', 'Playwright Test', 'pytest', 'Maven with TestNG'], [
    ['split the suite', '--shard=1/2', '--splits 2 --group 1 (pytest-split)', 'one package or suite per job'],
    ['balance', 'by test count, with fullyParallel', 'by stored durations with --store-durations', 'by hand'],
    ['one report', 'blob reports, then merge-reports', 'one JUnit file per job', 'one Surefire folder per job'],
])}
{tip('fail-fast: false keeps the other shards running when one fails, so you see every failure in one run. The merge job uses if: !cancelled() for the same reason.', 'tip')}
''', kw=['matrix', 'shard', 'blob', 'merge-reports', 'pytest-split', 'fail-fast', 'parallel jobs']),

    part('docker', '🐳', 'The official Docker images', f'''
<p>Microsoft publishes Docker images with the browsers and all their system libraries already installed. A job that runs inside one skips the browser install step, and every run uses exactly the same machine.</p>
{table(['Language', 'Image'], [
    ['JavaScript and TypeScript', 'mcr.microsoft.com/playwright:v1.63.0-noble'],
    ['Python', 'mcr.microsoft.com/playwright/python:v1.63.0-noble'],
    ['Java', 'mcr.microsoft.com/playwright/java:v1.63.0-noble'],
    ['.NET', 'mcr.microsoft.com/playwright/dotnet:v1.63.0-noble'],
])}
[[docker]]
{table(['Flag', 'Why the Playwright docs recommend it'], [
    ['--ipc=host', 'without it Chromium can run out of memory and crash'],
    ['--init', 'avoids special treatment of the process with id 1, a common cause of leftover processes'],
    ['a fixed tag such as v1.63.0-noble', 'the image must match the Playwright version in the project. noble means Ubuntu 24.04'],
    ['--user pwuser with a seccomp profile', 'only when the tests visit sites you do not trust'],
])}
{tip('In GitHub Actions, the same image goes under <code>container: image:</code> in the job, with <code>options: --user 1001</code>, and the browser install step is left out.', 'pro')}
''', kw=['docker', 'image', 'container', 'ipc=host', 'init', 'noble', 'mcr.microsoft.com']),

    part('others', '🏭', 'Jenkins, GitLab and Azure DevOps', f'''
<p>Many companies use Jenkins, GitLab or Azure DevOps instead of GitHub Actions. The steps stay the same. Only the file and a few names change.</p>
[[jenkins]]
[[gitlab]]
[[azure]]
{table(['CI service', 'File', 'Sets CI=true', 'Secrets'], [
    ['GitHub Actions', '.github/workflows/*.yml', 'yes', 'secrets.NAME'],
    ['GitLab CI', '.gitlab-ci.yml', 'yes', 'CI/CD variables, marked masked'],
    ['Jenkins', 'Jenkinsfile', 'no, set it yourself', "credentials('id')"],
    ['Azure Pipelines', 'azure-pipelines.yml', 'no, set it yourself', 'secret pipeline variables, $(NAME)'],
])}
''', kw=['Jenkins', 'Jenkinsfile', 'GitLab', 'Azure DevOps', 'Azure Pipelines', 'CircleCI', 'Bitbucket']),

    part('red', '🧯', 'When the pipeline goes red', f'''
<p>A failed run is only useful if someone can find out why quickly. Work through it in this order.</p>
{table(['Step', 'Playwright Test', 'pytest', 'Java'], [
    ['1. read the failure in the job log', 'the list reporter output', 'the short summary at the end', 'the Surefire summary'],
    ['2. download the artifact', 'playwright-report', 'test-results', 'target/surefire-reports and traces'],
    ['3. open the trace', 'npx playwright show-report, then the trace', 'playwright show-trace trace.zip', 'mvn exec:java with show-trace'],
    ['4. run only the failures again', 'npx playwright test --last-failed', 'pytest --lf', 'mvn test -Dtest=CheckoutTest'],
])}
{tip('Never fix a red pipeline by adding a skip or a longer sleep. Find out whether the app or the test is wrong. The trace from the debugging chapter shows the page at every step of the failed run.', 'warn')}
{tip('A test marked flaky in the report passed on a retry. Treat it as a bug to fix this week, not as a pass.', 'pro')}
''', kw=['failure', 'artifact', 'trace', 'last-failed', 'flaky', 'rerun']),
]

INFO = {'title': 'A pipeline in four ideas', 'panels': [
    panel([['e', '🚀'], ['t', 'git push', {'b': 1}]], 'Every push', 'Tests run by themselves.', 'Nobody has to remember.'),
    panel([['e', '🖥️'], ['t', 'fresh', {'b': 1}]], 'Fresh machine', 'Install everything each time.', 'Or use the Docker image.'),
    panel([['e', '🔐'], ['t', 'secrets', {'b': 1}]], 'Secrets', 'From the CI settings.', 'Masked in the logs.'),
    panel([['e', '📦'], ['t', 'artifacts', {'b': 1}]], 'Evidence', 'Reports kept, pass or fail.', 'Traces explain failures.')],
    'remember': 'CI runs the same three steps everywhere: a machine that can run browsers, the packages and browsers installed, then the tests with CI settings and secrets.'}

REAL = [
    ['🛒', 'A sale day saved', 'A developer changes the cart total for a festival discount. The checkout test fails on the pull request with ₹698 expected and ₹0 shown. The bug never reaches customers.'],
    ['⏱️', 'Forty minutes to twelve', 'A suite of 600 tests takes forty minutes on one CI machine. A matrix of four shards brings each pull request check down to about twelve minutes, and one merged report still shows the whole run.'],
    ['🔑', 'The password that expired', 'Every sign in test fails on Monday morning. The trace shows the error message for a wrong password. The staging password had been changed, and updating one CI secret fixes the whole suite.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter runs the framework the way a CI pipeline does: CI settings, GitHub Actions files, secrets, shards with a merged report, the official Docker images, and Jenkins, GitLab and Azure DevOps.',
        'यह अध्याय framework को वैसे चलाता है जैसे CI pipeline चलाती है: CI settings, GitHub Actions files, secrets, merged report के साथ shards, official Docker images, और Jenkins, GitLab और Azure DevOps।',
        'ಈ ಅಧ್ಯಾಯ framework ಅನ್ನು CI pipeline ನಡೆಸುವಂತೆ ನಡೆಸುತ್ತದೆ: CI settings, GitHub Actions files, secrets, merged report ಜೊತೆ shards, official Docker images, ಮತ್ತು Jenkins, GitLab, Azure DevOps.',
        'ଏହି ଅଧ୍ୟାୟ framework କୁ CI pipeline ପରି ଚଳାଏ: CI settings, GitHub Actions files, secrets, merged report ସହ shards, official Docker images, ଏବଂ Jenkins, GitLab ଓ Azure DevOps।',
        'يشغّل هذا الفصل الإطار كما يشغّله خط CI: إعدادات CI، وملفات GitHub Actions، والأسرار، والتقسيم مع تقرير مدمج، وصور Docker الرسمية، وJenkins وGitLab وAzure DevOps.',
        'Dieses Kapitel führt das Framework so aus wie eine CI-Pipeline: CI-Einstellungen, GitHub-Actions-Dateien, Secrets, Shards mit einem zusammengeführten Bericht, die offiziellen Docker-Images sowie Jenkins, GitLab und Azure DevOps.'),
    say('what', 'What CI does', 'CI runs your tests on a fresh machine every time someone pushes code or opens a pull request. A broken change is caught before it is merged.',
        'CI हर बार किसी के code push करने या pull request खोलने पर एक नई machine पर आपके tests चलाता है। टूटा हुआ बदलाव merge से पहले पकड़ा जाता है।',
        'ಯಾರಾದರೂ code push ಮಾಡಿದಾಗ ಅಥವಾ pull request ತೆರೆದಾಗ CI ಹೊಸ machine ನಲ್ಲಿ ನಿಮ್ಮ tests ನಡೆಸುತ್ತದೆ. ಮುರಿದ ಬದಲಾವಣೆ merge ಮೊದಲು ಸಿಗುತ್ತದೆ.',
        'କେହି code push କଲେ ବା pull request ଖୋଲିଲେ CI ନୂଆ machine ରେ ଆପଣଙ୍କ tests ଚଳାଏ। ଭଙ୍ଗା ପରିବର୍ତ୍ତନ merge ପୂର୍ବରୁ ଧରାପଡେ।',
        'يشغّل CI اختباراتك على جهاز جديد في كل مرة يدفع فيها أحد كودًا أو يفتح طلب دمج. فيُكتشف التغيير المعطوب قبل دمجه.',
        'CI führt deine Tests auf einer frischen Maschine aus, sobald jemand Code pusht oder einen Pull Request öffnet. Eine fehlerhafte Änderung wird vor dem Mergen entdeckt.'),
    say('cimode', 'CI settings', 'Most CI services set CI to true. The config reads it and turns on forbidOnly, retries, a fixed number of workers and JUnit XML reports.',
        'ज़्यादातर CI services CI को true करती हैं। Config इसे पढ़कर forbidOnly, retries, तय workers और JUnit XML reports चालू करता है।',
        'ಹೆಚ್ಚಿನ CI services CI ಅನ್ನು true ಮಾಡುತ್ತವೆ. Config ಅದನ್ನು ಓದಿ forbidOnly, retries, ನಿಗದಿತ workers ಮತ್ತು JUnit XML reports ಆನ್ ಮಾಡುತ್ತದೆ.',
        'ଅଧିକାଂଶ CI services CI କୁ true କରନ୍ତି। Config ଏହାକୁ ପଢି forbidOnly, retries, ନିର୍ଦ୍ଦିଷ୍ଟ workers ଓ JUnit XML reports ଚାଲୁ କରେ।',
        'تضبط معظم خدمات CI المتغير CI على true. ويقرؤه الإعداد فيفعّل forbidOnly وإعادة المحاولة وعددًا ثابتًا من العمال وتقارير JUnit XML.',
        'Die meisten CI-Dienste setzen CI auf true. Die Konfiguration liest das und schaltet forbidOnly, Wiederholungen, eine feste Zahl von Workern und JUnit-XML-Berichte ein.'),
    say('github', 'GitHub Actions', 'A workflow file in .github/workflows gets the code, installs the language, the packages and the browser, runs the tests, and uploads the report even when tests fail.',
        '.github/workflows की workflow file code लेती है, language, packages और browser install करती है, tests चलाती है, और tests fail होने पर भी report upload करती है।',
        '.github/workflows ನ workflow file code ಪಡೆಯುತ್ತದೆ, language, packages, browser install ಮಾಡುತ್ತದೆ, tests ನಡೆಸುತ್ತದೆ, tests fail ಆದರೂ report upload ಮಾಡುತ್ತದೆ.',
        '.github/workflows ର workflow file code ଆଣେ, language, packages ଓ browser install କରେ, tests ଚଳାଏ, ଏବଂ tests fail ହେଲେ ମଧ୍ୟ report upload କରେ।',
        'ملف سير العمل في ‎.github/workflows يجلب الكود، ويثبّت اللغة والحزم والمتصفح، ويشغّل الاختبارات، ويرفع التقرير حتى عند فشلها.',
        'Eine Workflow-Datei in .github/workflows holt den Code, installiert Sprache, Pakete und Browser, führt die Tests aus und lädt den Bericht auch bei Fehlern hoch.'),
    say('secrets', 'Secrets', 'Settings and passwords live in the CI settings and reach the tests as environment variables. A wrong or missing secret makes the sign in tests fail, and the fix is in the settings.',
        'Settings और passwords CI settings में रहते हैं और environment variables के रूप में tests तक पहुँचते हैं। गलत या गायब secret से sign in tests fail होते हैं, और सुधार settings में होता है।',
        'Settings ಮತ್ತು passwords CI settings ನಲ್ಲಿ ಇರುತ್ತವೆ, environment variables ಆಗಿ tests ಗೆ ತಲುಪುತ್ತವೆ. ತಪ್ಪು ಅಥವಾ ಇಲ್ಲದ secret ನಿಂದ sign in tests fail ಆಗುತ್ತವೆ, ಸರಿಪಡಿಸುವುದು settings ನಲ್ಲಿ.',
        'Settings ଓ passwords CI settings ରେ ରହେ ଏବଂ environment variables ଭାବେ tests ପାଖରେ ପହଞ୍ଚେ। ଭୁଲ ବା ନଥିବା secret ରେ sign in tests fail ହୁଏ, ଏବଂ ସମାଧାନ settings ରେ।',
        'تعيش الإعدادات وكلمات المرور في إعدادات CI وتصل إلى الاختبارات كمتغيرات بيئة. والسر الخاطئ أو المفقود يُفشل اختبارات تسجيل الدخول، وإصلاحه في الإعدادات.',
        'Einstellungen und Passwörter liegen in den CI-Einstellungen und erreichen die Tests als Umgebungsvariablen. Ein falsches oder fehlendes Secret lässt die Anmeldetests scheitern, und die Lösung liegt in den Einstellungen.'),
    say('shards', 'Shards', 'A matrix starts the same job several times, each with its own shard. Playwright Test saves a blob report per shard and merges them into one report at the end.',
        'Matrix एक ही job को कई बार चलाता है, हर बार अपने shard के साथ। Playwright Test हर shard का blob report बचाता है और आख़िर में उन्हें एक report में जोड़ता है।',
        'Matrix ಒಂದೇ job ಅನ್ನು ಹಲವು ಬಾರಿ ಆರಂಭಿಸುತ್ತದೆ, ಪ್ರತಿಯೊಂದಕ್ಕೂ ತನ್ನ shard. Playwright Test ಪ್ರತಿ shard ಗೆ blob report ಉಳಿಸಿ ಕೊನೆಯಲ್ಲಿ ಒಂದು report ಆಗಿ ಸೇರಿಸುತ್ತದೆ.',
        'Matrix ସେହି job କୁ ଅନେକ ଥର ଆରମ୍ଭ କରେ, ପ୍ରତ୍ୟେକର ନିଜ shard ସହ। Playwright Test ପ୍ରତି shard ର blob report ସଞ୍ଚୟ କରି ଶେଷରେ ଗୋଟିଏ report ରେ ଯୋଡେ।',
        'تبدأ المصفوفة المهمة نفسها عدة مرات، لكل نسخة جزؤها. ويحفظ Playwright Test تقرير blob لكل جزء ثم يدمجها في تقرير واحد في النهاية.',
        'Eine Matrix startet denselben Job mehrmals, jeden mit seinem eigenen Shard. Playwright Test speichert pro Shard einen Blob-Bericht und führt sie am Ende zu einem Bericht zusammen.'),
    say('docker', 'Docker', 'The official Playwright images already hold the browsers and their system libraries. Use the tag that matches your Playwright version, and run with ipc host and init.',
        'Official Playwright images में browsers और उनकी system libraries पहले से होती हैं। अपने Playwright version वाला tag इस्तेमाल करें, और ipc host और init के साथ चलाएँ।',
        'Official Playwright images ನಲ್ಲಿ browsers ಮತ್ತು system libraries ಮೊದಲೇ ಇವೆ. ನಿಮ್ಮ Playwright version ಗೆ ಹೊಂದುವ tag ಬಳಸಿ, ipc host ಮತ್ತು init ಜೊತೆ ನಡೆಸಿ.',
        'Official Playwright images ରେ browsers ଓ system libraries ଆଗରୁ ଅଛି। ଆପଣଙ୍କ Playwright version ସହ ମେଳ ଖାଉଥିବା tag ବ୍ୟବହାର କରନ୍ତୁ, ଏବଂ ipc host ଓ init ସହ ଚଳାନ୍ତୁ।',
        'تحتوي صور Playwright الرسمية على المتصفحات ومكتباتها مسبقًا. استخدم الوسم المطابق لإصدار Playwright لديك، وشغّلها مع ipc host وinit.',
        'Die offiziellen Playwright-Images enthalten die Browser und ihre Systembibliotheken bereits. Nimm das Tag, das zu deiner Playwright-Version passt, und starte mit ipc host und init.'),
    say('others', 'Other CI services', 'Jenkins, GitLab and Azure DevOps run the same steps from their own files. Jenkins and Azure do not set CI, so their files set it.',
        'Jenkins, GitLab और Azure DevOps अपनी files से वही steps चलाते हैं। Jenkins और Azure CI set नहीं करते, इसलिए उनकी files इसे set करती हैं।',
        'Jenkins, GitLab ಮತ್ತು Azure DevOps ತಮ್ಮ files ನಿಂದ ಅದೇ steps ನಡೆಸುತ್ತವೆ. Jenkins ಮತ್ತು Azure CI set ಮಾಡುವುದಿಲ್ಲ, ಆದ್ದರಿಂದ ಅವರ files ಅದನ್ನು set ಮಾಡುತ್ತವೆ.',
        'Jenkins, GitLab ଓ Azure DevOps ନିଜ files ରୁ ସେହି steps ଚଳାନ୍ତି। Jenkins ଓ Azure CI set କରନ୍ତି ନାହିଁ, ତେଣୁ ସେମାନଙ୍କ files ଏହାକୁ set କରେ।',
        'تشغّل Jenkins وGitLab وAzure DevOps الخطوات نفسها من ملفاتها. ولا تضبط Jenkins وAzure المتغير CI، لذا تضبطه ملفاتها.',
        'Jenkins, GitLab und Azure DevOps führen dieselben Schritte aus eigenen Dateien aus. Jenkins und Azure setzen CI nicht, also setzen ihre Dateien es.'),
    say('red', 'A red pipeline', 'Read the failure in the log, download the report, open the trace, then run only the failed tests again. Never hide a failure with a skip or a longer sleep.',
        'Log में failure पढ़ें, report download करें, trace खोलें, फिर सिर्फ fail हुए tests दोबारा चलाएँ। Failure को skip या लंबे sleep से कभी न छिपाएँ।',
        'Log ನಲ್ಲಿ failure ಓದಿ, report download ಮಾಡಿ, trace ತೆರೆಯಿರಿ, ನಂತರ fail ಆದ tests ಮಾತ್ರ ಮತ್ತೆ ನಡೆಸಿ. Failure ಅನ್ನು skip ಅಥವಾ ಉದ್ದ sleep ನಿಂದ ಮರೆಮಾಡಬೇಡಿ.',
        'Log ରେ failure ପଢନ୍ତୁ, report download କରନ୍ତୁ, trace ଖୋଲନ୍ତୁ, ତାପରେ କେବଳ fail ହୋଇଥିବା tests ପୁଣି ଚଳାନ୍ତୁ। Failure କୁ skip ବା ଲମ୍ବା sleep ରେ କେବେ ଲୁଚାନ୍ତୁ ନାହିଁ।',
        'اقرأ الفشل في السجل، ونزّل التقرير، وافتح الأثر، ثم أعد تشغيل الاختبارات الفاشلة فقط. ولا تُخفِ الفشل أبدًا بتخطٍّ أو انتظار أطول.',
        'Lies den Fehler im Log, lade den Bericht herunter, öffne den Trace und führe dann nur die fehlgeschlagenen Tests erneut aus. Verstecke einen Fehler nie mit einem Skip oder einem längeren Sleep.'),
    say('practice', 'Playground labs', 'In the labs you make two tests safe for CI: one without a fixed wait, and one that takes the shop address from the config instead of the code.',
        'Labs में आप दो tests को CI के लिए सुरक्षित बनाते हैं: एक बिना fixed wait के, और एक जो shop address code की जगह config से लेता है।',
        'Labs ನಲ್ಲಿ ಎರಡು tests ಅನ್ನು CI ಗೆ ಸುರಕ್ಷಿತ ಮಾಡುತ್ತೀರಿ: ಒಂದು fixed wait ಇಲ್ಲದೆ, ಇನ್ನೊಂದು shop address ಅನ್ನು code ಬದಲು config ನಿಂದ ಪಡೆಯುತ್ತದೆ.',
        'Labs ରେ ଆପଣ ଦୁଇଟି tests କୁ CI ପାଇଁ ସୁରକ୍ଷିତ କରନ୍ତି: ଗୋଟିଏ fixed wait ବିନା, ଏବଂ ଗୋଟିଏ ଯାହା shop address code ବଦଳରେ config ରୁ ନିଏ।',
        'في المختبرات تجعل اختبارين آمنين لـ CI: أحدهما بلا انتظار ثابت، والآخر يأخذ عنوان المتجر من الإعداد بدل الكود.',
        'In den Labs machst du zwei Tests CI-sicher: einen ohne feste Wartezeit und einen, der die Shop-Adresse aus der Konfiguration statt aus dem Code nimmt.'),
]

QUIZ = [
    quiz(1, 'What does continuous integration do with your tests?', ['deletes them', 'runs them on every push and pull request', 'writes them', 'runs them once a year'], 1,
         'Every change.', 'A CI server runs the suite for every push and pull request, so problems are caught before merging.'),
    quiz(1, 'Which command installs Chromium together with the Linux libraries it needs?', ['npm install chromium', 'npx playwright install --with-deps chromium', 'apt install chrome', 'npx playwright test --deps'], 1,
         'with deps.', '--with-deps also installs the system packages the browser needs on Linux.'),
    quiz(1, 'Where should the staging password for CI live?', ['in the workflow file', 'in the CI secrets', 'in users.ts', 'in the README'], 1,
         'Not in Git.', 'Secrets live in the CI settings and reach the job as environment variables.'),
    quiz(1, 'Why does the upload step use if: !cancelled()?', ['to save space', 'so results are kept even when tests failed', 'to skip uploads', 'it is required syntax'], 1,
         'Failures need evidence.', 'Without it, a failed test step would skip the upload, and the report you need would be lost.'),
    quiz(2, 'What happens to a test.only when CI is true in the framework config?', ['it runs alone', 'the run fails because forbidOnly is on', 'it is ignored', 'it is retried'], 1,
         'forbidOnly.', 'forbidOnly makes Playwright stop the run when any test.only is found.'),
    quiz(2, 'Which CI services set CI=true by themselves?', ['Jenkins and Azure Pipelines', 'GitHub Actions and GitLab', 'none', 'only Jenkins'], 1,
         'Two of them do.', 'GitHub Actions and GitLab set it. In Jenkins and Azure Pipelines the pipeline file sets it.'),
    quiz(2, 'What does --ipc=host prevent in the Playwright Docker image?', ['slow downloads', 'Chromium running out of memory and crashing', 'wrong time zones', 'missing fonts'], 1,
         'Shared memory.', 'The Playwright docs recommend it because Chromium can run out of memory without it.'),
    quiz(2, 'What happens when the Docker image tag does not match the Playwright version in the project?', ['nothing', 'Playwright cannot find its browsers', 'tests run twice', 'the image updates itself'], 1,
         'Versions must match.', 'Each Playwright version expects its own browser builds, which the matching image holds.'),
    quiz(2, 'How does pytest split a suite across two CI jobs in this chapter?', ['--shard=1/2', 'pytest-split with --splits 2 --group 1', '-n 2', '-m smoke'], 1,
         'A plugin.', 'pytest-split adds --splits and --group. -n 2 only uses two processes on one machine.'),
    quiz(3, 'Why does the merge-reports job need blob reports instead of HTML reports?', ['blob is smaller to type', 'blob reports hold the raw results that can be merged into one report', 'HTML cannot be uploaded', 'GitHub needs blob'], 1,
         'Merging needs raw data.', 'Each shard writes a blob report, and merge-reports builds one HTML report from all of them.'),
    quiz(3, 'Which Surefire option overrides the TestNG suite file to run one package?', ['-Dsuite', '-Dtest', '-Dgroups', '-Dparallel'], 1,
         'test wins.', '-Dtest picks the test classes, and Surefire then ignores the suite file.'),
    quiz(3, 'Why do the Playwright docs not recommend caching browsers in CI?', ['it is not allowed', 'restoring the cache takes about as long as downloading, and system libraries cannot be cached', 'browsers change every day', 'caches are unsafe'], 1,
         'No time saved.', 'Restoring takes about as long as the download, and the Linux libraries still need installing.'),
]

CALC = [
    calc(1, 'A suite takes 40 minutes on one CI machine. With 4 equal shards, about how many minutes does each shard take?', 10, '40 / 4', ['40 / 4 = 10 minutes']),
    calc(1, 'The matrix has shardIndex [1, 2, 3] and shardTotal [3]. How many test jobs start?', 3, '3 × 1', ['3 values × 1 value = 3 jobs']),
    calc(2, 'The framework has 7 tests and the run used 2 shards. Shard 1 ran 4 tests. How many did shard 2 run?', 3, '7 - 4', ['7 - 4 = 3']),
    calc(2, 'A test fails twice, then passes on the last retry with retries: 2. How many times did it run?', 3, '1 + 2', ['first run + 2 retries = 3']),
    calc(2, 'A team has 30 pull requests a week and each check takes 12 minutes. How many CI minutes a week is that?', 360, '30 × 12', ['30 × 12 = 360']),
    calc(3, 'The Java matrix has the features smoke, products and cart, in 2 browsers. How many jobs start?', 6, '3 × 2', ['3 features × 2 browsers = 6 jobs']),
    calc(3, 'Shards take 9, 11, 10 and 14 minutes, then the merge job takes 2. How many minutes until the merged report is ready?', 16, 'slowest shard + merge', ['the shards run at the same time, so the slowest one decides: 14', '14 + 2 = 16']),
    calc(3, 'An artifact is kept 14 days and one run makes 25 MB. With 20 runs a day, how many MB are stored at most?', 7000, '25 × 20 × 14', ['25 × 20 = 500 MB a day', '500 × 14 = 7000 MB']),
]

LABS = [
    {'id': 'nowait', 'title': 'Take out the fixed wait', 'name': 'search finds the lamp',
     'task': 'This test waits three seconds before it checks, which slows CI and still fails on a busy machine. On <code>/products</code>, search for <code>lamp</code> and check that exactly <b>one</b> card is in the list named <b>Products</b>, with no fixed wait at all.',
     'goal': 'One card is shown and the test has no fixed wait.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('search finds the lamp', async ({ page }) => {
  await page.goto('/products');
  await page.getByPlaceholder('Search products').fill('lamp');
  await page.waitForTimeout(3000);
  // replace the wait with a check that waits by itself
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('search finds the lamp', async ({ page }) => {
  await page.goto('/products');
  await page.getByPlaceholder('Search products').fill('lamp');
  await expect(page.getByRole('list', { name: 'Products' }).getByRole('listitem')).toHaveCount(1);
});'''},
     'hint': "A web first check waits by itself: <code>await expect(page.getByRole('list', { name: 'Products' }).getByRole('listitem')).toHaveCount(1)</code>.",
     'why': 'The check retries until the list has one card or the timeout runs out. It is as fast as the page allows on a laptop and still patient on a slow CI machine.',
     'check': [[r"!/wait_?for_?timeout/i.test(ctx.code)", 'No fixed wait is left'], [r"/count(Async)?\(1\)/i.test(ctx.code)", 'The test checks for one card'],
               ["/'lamp'|\"lamp\"/.test(ctx.code)", 'The test searches for lamp']]},
    {'id': 'relative', 'title': 'Let the config choose the address', 'name': 'the water bottle is listed',
     'task': 'This test has the shop address written into it, so it can never run against staging. Open <code>/products</code> with a <b>relative</b> address and check that the card with the test id <code>product-5</code> contains <b>Water bottle</b>.',
     'goal': 'The products page is open through the base URL and the bottle is listed.', 'start': '',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the water bottle is listed', async ({ page }) => {
  await page.goto('http://localhost:4173/products');
  // use a relative address, then check the card product-5
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the water bottle is listed', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByTestId('product-5')).toContainText('Water bottle');
});'''},
     'hint': "Start the address with a slash: <code>page.goto('/products')</code>. The base URL from the config, or BASE_URL on CI, is put in front.",
     'why': 'With a relative address, the same test runs against a laptop, a Docker container or staging. Only BASE_URL changes, in the CI settings.',
     'check': [[r"!/https?:\/\//.test(ctx.code)", 'No full address in the test'], ["ctx.url.includes('/products')", 'The products page is open'],
               ["/Water bottle/.test(ctx.text)", 'The bottle is on the page']]},
]

T = {
    'slug': 'pw-ci', 'title': 'CI/CD pipelines', 'short': 'CI/CD', 'emoji': '🚦', 'module': MODULE, 'minutes': 30,
    'lead': 'Run the framework on every push. CI settings, GitHub Actions files for each language, secrets, shards with one merged report, the official Docker images, and Jenkins, GitLab and Azure DevOps.',
    'desc': 'Playwright in continuous integration for TypeScript, JavaScript, Python and Java: CI=true settings, forbidOnly, GitHub Actions workflows, secrets and variables, matrix sharding with blob reports and merge-reports, pytest-split, Maven per package jobs, the official Docker images with ipc host and init, Jenkinsfiles, GitLab CI, Azure Pipelines and what to do when a pipeline fails.',
    'summary': 'The framework ran with CI settings, a forgotten test.only failed the run, a wrong secret failed the sign in tests, shards merged into one report, and the smoke tests passed inside the official Docker images in all four languages.',
    'keywords': ['CI', 'CD', 'pipeline', 'GitHub Actions', 'workflow', 'Jenkins', 'GitLab', 'Azure', 'Docker', 'shard', 'matrix', 'secrets', 'artifact', 'forbidOnly'],
    'plain': 'CI is a server that runs your tests every time code changes. It starts a fresh machine, installs everything, runs the tests with settings and passwords from its own settings, and keeps the reports so you can see why something failed.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
