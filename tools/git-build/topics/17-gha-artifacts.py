# Chapter 7.3: artifacts and caching on GitHub Actions. upload-artifact and download-artifact inputs and outputs,
# immutability and overwrite, retention, hidden files, permissions loss, archive false, pulling artifacts in the same
# run, from another run, from another repository, with the web page, gh run download and the REST API, actions/cache
# keys, restore-keys, scope and limits, setup-python cache, cache poisoning. Sources: actions/upload-artifact,
# actions/download-artifact and actions/cache READMEs, GitHub docs: store and share data, downloading workflow
# artifacts, dependency caching, REST API for artifacts, limits. Checked on 2026-11-02.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from gitkit import sh, flow, file, devqa, changes

K = Kit()

K.lesson('upload', 'Publishing artifacts: upload-artifact', f'''
<p>An <b>artifact</b> is a file or folder that a job saves at the end so that later jobs, people and other workflows can use it. On GitHub you publish it with <code>actions/upload-artifact</code>.</p>
{file('upload-examples.yml', """- name: Publish the build
  id: up
  uses: actions/upload-artifact@v7
  with:
    name: calc-app
    path: |
      dist/calc-app.zip
      !dist/**/*.tmp
    if-no-files-found: error
    retention-days: 30
- run: echo "Artifact ${{ steps.up.outputs.artifact-id }} at ${{ steps.up.outputs.artifact-url }}"
""", {5: 'The name later downloads use. It must be unique within the run.', 6: 'One or more paths, wildcards allowed. A line starting with ! excludes files.', 9: 'error, warn (the default) or ignore when nothing matches.', 10: 'Days to keep it, from 1 up to the repository or organisation limit (90 by default). Without it the repository setting applies, 90 days by default.', 11: 'Outputs: artifact-id for the REST API, artifact-url for people, artifact-digest (SHA-256) to check the content.'})}
{table(['Fact', 'Detail'], [
    ['Immutable', 'Since version 4 an artifact cannot be changed after upload. Uploading the same name twice in one run fails, unless you set overwrite: true, which deletes the old one and gives a new id.'],
    ['Zipped', 'By default the files are zipped. archive: false uploads one file as it is.'],
    ['Hidden files', 'Files and folders starting with a dot are skipped unless include-hidden-files: true, so .env files are not leaked by accident.'],
    ['Permissions', 'Zipped artifacts lose file permissions: files become 644, so an executable bit is lost. Put a tar file inside if you need it.'],
    ['Limits', 'At most 500 artifacts per job. Storage counts against the account quota.']])}
{viz('artlife', plat='gha')}
{note('A matrix job that uploads with a fixed name fails from the second combination on, because names must be unique. Add the matrix values: name: report-${{ matrix.os }}-${{ matrix.python }}.', 'warn')}
''', kw=['upload-artifact', 'artifact name', 'retention-days', 'if-no-files-found', 'immutable', 'overwrite', 'archive false', 'include-hidden-files', 'artifact-id', 'artifact-url', 'artifact-digest', '500 artifacts'])

K.lesson('pull', 'Pulling artifacts: five ways', f'''
<p>"Pulling" an artifact means getting the file back. Who needs it and from where decides the method.</p>
{table(['Who', 'From where', 'How'], [
    ['A later job', 'the same run', '<code>actions/download-artifact</code> with <code>name</code>, plus <code>needs</code> on the uploading job'],
    ['A job in another workflow', 'another run, same repository', 'download-artifact with <code>github-token</code>, <code>run-id</code> (and <code>repository</code>), or <code>gh run download</code>'],
    ['A person', 'any run', 'the Artifacts section at the bottom of the run summary page'],
    ['A person or script with a terminal', 'any run', '<code>gh run download &lt;run-id&gt; -n calc-app -D dir</code>'],
    ['Any tool', 'any run', 'the REST API: list, then download the zip']])}
{file('download-examples.yml', """# 1. Same run: one artifact into a folder
- uses: actions/download-artifact@v8
  with:
    name: calc-app
    path: dist
# 2. Same run: every report of a matrix, into one folder
- uses: actions/download-artifact@v8
  with:
    pattern: report-*
    merge-multiple: true
    path: reports
# 3. Another run or repository: needs a token with actions read access there
- uses: actions/download-artifact@v8
  with:
    name: calc-app
    github-token: ${{ secrets.GH_PAT }}
    repository: OWNER/calc-app
    run-id: 1234567890
""", {4: 'Without path the files land in the working directory.', 9: 'pattern selects several artifacts by name.', 10: 'merge-multiple puts their files in one folder instead of one folder per artifact.', 16: 'By default download-artifact only sees the current run. A token opens other runs.', 18: 'The run id is the number in the run page URL: /actions/runs/1234567890.'})}
{sh('From a terminal with the GitHub CLI', """gh run list --workflow ci.yml --branch main --status success --limit 1
gh run download 1234567890 -n calc-app -D downloaded
ls downloaded""", """calc-app.zip""")}
{sh('With the REST API (any language, curl shown)', """# list artifacts named calc-app, newest first
curl -H "Authorization: Bearer $TOKEN" \\
  "https://api.github.com/repos/OWNER/calc-app/actions/artifacts?name=calc-app"
# download one by id: GitHub answers with a redirect to a short lived URL, -L follows it
curl -L -H "Authorization: Bearer $TOKEN" -o calc-app.zip \\
  "https://api.github.com/repos/OWNER/calc-app/actions/artifacts/ARTIFACT_ID/zip"
""")}
{devqa('<p>Developers mostly use way 1: build uploads, the next job downloads, all inside one run. They also grab an artifact from a failed pull request run to reproduce a bug locally.</p>',
       '<p>QA uses ways 2 to 5: a scheduled regression workflow pulls the last green build with gh run download, testers download builds from the run page, and test management tools use the REST API to attach reports to test cycles.</p>',
       'Who pulls artifacts and how')}
{note('Artifacts are for files of one run, kept for a limited time. For a release that users install, publish it to GitHub Releases or GitHub Packages, which keep it until you delete it.', 'exam')}
''', kw=['download-artifact', 'pull artifact', 'pattern', 'merge-multiple', 'run-id', 'github-token', 'gh run download', 'REST API', 'artifacts zip', 'GitHub Releases', 'GitHub Packages'])

K.lesson('cache', 'Caching dependencies: actions/cache', f'''
<p>A <b>cache</b> stores files that are slow to download or build, such as pip packages, so the next run can restore them. Unlike an artifact, losing a cache only makes a run slower.</p>
{file('cache-example.yml', """- uses: actions/setup-python@v7
  with:
    python-version: '3.13'
    cache: pip
# the same idea written out by hand with actions/cache
- uses: actions/cache@v6
  id: pipcache
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
- run: pip install -r requirements.txt
""", {4: 'The easy way: setup-python builds the key from your requirements file for you.', 9: 'The folder to save and restore.', 10: 'The key changes whenever requirements.txt changes, so a new set of packages gets a new cache.', 11: 'If there is no exact match, take the newest cache whose key starts with this prefix, then pip installs only what is new.', 13: 'Still run the install. With a cache it is fast, without one it is correct.'})}
{viz('cachekey')}
{table(['Rule', 'Detail'], [
    ['Scope', 'A run can restore caches from its own branch and from the default branch. A pull request can also use its base branch. Branches do not see each other\'s caches.'],
    ['Save', 'A cache is saved at the end of the job only when the key had no exact hit. An existing key is never overwritten.'],
    ['Limits', '10 GB per repository by default. Entries not used for 7 days are removed, and the oldest go first when the limit is reached.'],
    ['Output', 'cache-hit is true only for an exact key match.'],
    ['Security', 'Workflows from low trust triggers such as fork pull requests get read only access to the default branch cache, to prevent cache poisoning.']])}
{note('Never cache secrets or build outputs that must be correct. Caches can be restored from a partial match, so they may hold stale files. If a job must use exactly these files, it needs an artifact, not a cache.', 'warn')}
''', kw=['actions/cache', 'cache key', 'hashFiles', 'restore-keys', 'cache-hit', 'cache scope', 'default branch cache', '10 GB', '7 days', 'setup-python cache', 'cache poisoning'])

K.lesson('choose', 'Artifact, cache, release or package', f'''
{table(['Need', 'Use', 'Kept'], [
    ['Pass the build from build to test jobs', 'artifact', 'retention-days, up to 90 by default'],
    ['Keep test reports, screenshots, logs', 'artifact with if: always()', 'shorter retention is fine'],
    ['Speed up installs', 'cache', 'until unused for 7 days or evicted'],
    ['Ship a version to users', 'GitHub Release asset', 'until deleted'],
    ['Share a library with other projects', 'GitHub Packages or PyPI and similar registries', 'until deleted']])}
{scene('the expired build', '<p>A common support story: a customer reports a bug in last quarter\'s release, and the team wants the exact binary. The pipeline only uploaded it as an artifact with default retention, so after 90 days it is gone, and a rebuild from the tag pulls newer dependencies and behaves differently. The fix teams adopt is to attach release builds to a GitHub Release or a package registry at tag time, and to record the artifact digest so the file can be verified later.</p>')}
{ladder(
    '<p>An artifact is a file a job keeps for later, a cache is a shortcut that makes the next run faster. You can download artifacts from the web page, the terminal or the API.</p>',
    '<p>upload-artifact needs a unique name and sets retention. download-artifact pulls from the same run, or from other runs with a token and run-id. actions/cache restores by exact key, then by restore-keys prefixes, within branch scope.</p>',
    '<p>Artifacts are immutable and carry a SHA-256 digest. Caches are never overwritten and are evicted after 7 days unused or beyond 10 GB. Fork triggers get read only cache access to stop poisoning.</p>',
    '<p>Artifact attestations sign a statement that a given workflow run built a file with a given digest, which a consumer can verify before deploying. This is the SLSA provenance idea built into the platform.</p>')}
''', kw=['artifact vs cache', 'release', 'package registry', 'retention', 'digest', 'attestation', 'provenance'])

K.quiz('e', 'Which action publishes a build so later jobs can use it?', ['actions/cache', 'actions/upload-artifact', 'actions/checkout', 'actions/setup-python'], 1, 'Upload.', 'download-artifact gets it back.')
K.quiz('e', 'How long are artifacts kept by default?', ['1 day', '7 days', '90 days', 'Forever'], 2, 'About three months.', 'Repository settings or retention-days can shorten it.')
K.quiz('e', 'Where does a person download an artifact on github.com?', ['Settings', 'The Artifacts section of the run summary page', 'Insights', 'Wiki'], 1, 'Run page.', 'Logged in users with read access can download.')
K.quiz('m', 'Two matrix jobs upload with name: report. What happens?', ['Files merge', 'The second upload fails because names must be unique', 'The first is renamed', 'Nothing'], 1, 'Immutable.', 'Add matrix values to the name.')
K.quiz('m', 'What does restore-keys do in actions/cache?', ['Deletes old caches', 'Gives prefixes to try when there is no exact key match', 'Encrypts the cache', 'Sets retention'], 1, 'Fallback.', 'The newest matching entry is restored.')
K.quiz('m', 'A run on feature/x can restore caches saved on', ['Any branch', 'feature/x and the default branch', 'Only main', 'Only feature/x'], 1, 'Scope.', 'Sibling branches are isolated.')
K.quiz('m', 'Which command downloads the calc-app artifact of run 42 from a terminal?', ['git pull 42', 'gh run download 42 -n calc-app', 'gh artifact get calc-app', 'curl 42'], 1, 'gh run.', '-D chooses the folder.')
K.quiz('h', 'download-artifact cannot see an artifact from another workflow run. What is missing?', ['needs', 'github-token and run-id inputs', 'retention-days', 'a cache key'], 1, 'Scope.', 'By default it only sees the current run.')
K.quiz('h', 'You upload an executable script as an artifact and after download it is not executable. Why?', ['A bug', 'Zipped artifacts reset files to 644', 'Windows runner', 'Cache conflict'], 1, 'Permissions.', 'Put it in a tar inside the artifact.')
K.quiz('x', 'Why are fork pull request workflows given read only access to the default branch cache?', ['To save space', 'To stop untrusted code from poisoning a cache that trusted workflows restore', 'Forks are slow', 'Licensing'], 1, 'Poisoning.', 'A poisoned cache could run code in a trusted workflow.')

K.calc('e', 'retention-days is not set and the repository uses the default. How many days is the artifact kept?', '90', 'Default.',
       ['No retention-days: the repository setting applies.', 'The default setting is 90 days.', eq('90 days')], check=90)
K.calc('e', 'A matrix of 3 operating systems uploads one report each. How many artifacts?', '3', 'One per job.',
       ['Each matrix job uploads once.', 'Names include the OS.', eq('3 artifacts')], check=3)
K.calc('m', 'A cache entry was last used on day 10. With the 7 day rule, on which day is it first eligible for removal?', '17', 'Add 7.',
       ['Unused entries go after 7 days.', '10 + 7.', eq('day 17')], check=17)
K.calc('m', 'Each run saves a 400 MB cache with a new key. How many runs until the 10 GB limit forces eviction? Use 1 GB = 1000 MB.', '25', 'Divide.',
       ['10 GB = 10000 MB.', '10000 / 400 = 25.', eq('the 26th save evicts the oldest, 25 fit')], check=25)
K.calc('h', 'pip install takes 90 s without cache and 15 s with an exact hit. 60 runs a week, 80 percent exact hits. Seconds saved per week?', '3600', 'Only hits save time.',
       ['Hits: 0.8 × 60 = 48 runs.', 'Saving per hit: 90 - 15 = 75 s.', eq('48 × 75 = 3600 s, one hour')], check=3600)
K.calc('h', 'Artifacts: build 20 MB kept 30 days, reports 1 MB each from 3 jobs kept 14 days. Daily runs. Roughly how many MB are stored once both have reached steady state?', '642', 'Size times days kept.',
       ['Builds: 20 MB × 30 days = 600 MB.', 'Reports: 3 MB a day × 14 days = 42 MB.', eq('600 + 42 = 642 MB')], check=642)

K.must('upload-artifact', 'name (unique per run), path with ! excludes, if-no-files-found, retention-days (default 90), outputs artifact-id, artifact-url, artifact-digest. Immutable since v4, overwrite: true replaces. Hidden files skipped, permissions reset.')
K.must('Pull artifacts', 'Same run: download-artifact name or pattern plus needs. Other run: github-token, repository, run-id. People: run page. Terminal: gh run download <id> -n name -D dir. API: /repos/{owner}/{repo}/actions/artifacts/{id}/zip.')
K.must('actions/cache', 'key from runner.os and hashFiles, restore-keys prefixes, cache-hit only on exact match, saved only on a miss. Branch scope plus default branch. 10 GB per repo, 7 days unused.')
K.must('Choose', 'Artifact for results of a run, cache for speed, Release or Packages for versions users install.')
K.must('Safety', 'No secrets in caches or artifacts, read only cache for fork triggers, record digests, use attestations for release builds.')

T = K.topic(
    slug='gha-artifacts', topic='gha-artifacts', step=(7, 'GitHub Actions', 'gh-actions', 'Write GitHub Actions workflows from the first line: events, jobs, matrix and contexts, then a complete Dev and QA pipeline built from scratch, then artifacts and caches including how to pull a build from any run.', 'Intermediate'),
    title='GitHub Actions artifacts and caching: publish, pull and speed up', short='Actions artifacts', badge='7.3', minutes=55, added='2026-11-02',
    lead='Publish build outputs as artifacts, pull them back in the same run, from another run, from the web page, the gh CLI or the REST API, and make pipelines faster with caches that are safe to lose.',
    desc='upload-artifact inputs and outputs, immutability, overwrite, retention and hidden files, download-artifact with name, pattern, merge-multiple, github-token and run-id, gh run download, the REST API download, actions/cache keys, hashFiles, restore-keys, scope, limits and cache poisoning, and when to use releases and packages instead.',
    summary='Publishing and pulling artifacts five ways, retention and immutability, caching with keys and restore-keys, and the limits.',
    keywords=['upload-artifact', 'download-artifact', 'gh run download', 'artifact api', 'actions/cache', 'restore-keys', 'retention', 'cache scope'],
    recap='<p>Upload once with a unique name, pull it with download-artifact, gh run download or the API, cache only what is safe to lose, and put releases somewhere permanent.</p>')
