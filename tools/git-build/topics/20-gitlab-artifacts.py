# Chapter 8.3: GitLab artifacts and caching. artifacts paths, exclude, untracked, name, when, expire_in, access,
# reports (junit), the Keep button and kept latest artifacts, passing artifacts between jobs (stages, dependencies,
# needs artifacts), pulling artifacts from the UI, the job artifacts API by ref and by job id, report file types,
# merge request refs, glab job artifact, CI_JOB_TOKEN and the allowlist, needs:project, cache keys and policy,
# the package registry for releases. Sources: GitLab docs: job artifacts, CI/CD YAML reference (artifacts, cache,
# needs, dependencies), job artifacts API, CI/CD job token, caching, GitLab.com settings, glab job artifact help.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from gitkit import sh, flow, file, devqa, changes

K = Kit()

K.lesson('keep', 'Keeping files: the artifacts keyword', f'''
{file('artifacts-examples.yml', """build:
  stage: build
  script:
    - mkdir -p dist
    - python -m zipfile -c dist/calc-app.zip app
  artifacts:
    name: "calc-app-$CI_COMMIT_SHORT_SHA"
    paths:
      - dist/
    exclude:
      - dist/**/*.tmp
    expire_in: 30 days
    when: on_success
    access: developer

unit-tests:
  stage: test
  script:
    - python -m pytest -q tests/unit --junitxml=reports/unit.xml
  artifacts:
    when: always
    reports:
      junit: reports/unit.xml
""", {7: 'Name of the downloaded archive. Variables are allowed.', 8: 'Files and folders to keep, relative to the project folder. Paths outside it are not allowed.', 10: 'Leave out matching files.', 12: 'How long to keep. Without it the instance default applies, 30 days on GitLab.com. Examples: 1 week, 3 mos, never.', 13: 'on_success (default), on_failure or always.', 14: 'Who may download: all, developer, maintainer or none.', 21: 'always keeps the report when tests fail, which is when you need it.', 23: 'GitLab parses the file and shows results in the merge request and the Tests tab. Reports are stored separately from the archive.'})}
{viz('artlife', plat='gitlab')}
{table(['Rule', 'Detail'], [
    ['Latest kept', 'Artifacts from the most recently completed pipeline and the most recent successful pipeline on each branch or tag are kept regardless of expire_in, until a newer pipeline replaces them (a project setting can turn this off).'],
    ['Keep button', 'On a job page, Keep stops one job\'s artifacts from expiring.'],
    ['Size', 'GitLab.com limits a job\'s artifacts to 1 GB.'],
    ['untracked: true', 'adds every file Git does not track, handy for build folders, risky for secrets.']])}
{note('reports such as junit are not inside the downloadable archive. To keep the XML as a file too, also list it under paths, as the sample project does.', 'warn')}
''', kw=['artifacts', 'artifacts paths', 'exclude', 'artifacts name', 'expire_in', 'when always', 'access', 'reports junit', 'keep artifacts', 'latest artifacts kept', '1 GB'])

K.lesson('between', 'Passing artifacts between jobs', f'''
<p>By default a job downloads the artifacts of every job in <b>earlier stages</b>. Two keywords narrow that down.</p>
{table(['Setting on the job', 'Downloads'], [
    ['nothing', 'artifacts of all jobs in earlier stages'],
    ['<code>dependencies: [build]</code>', 'only build\'s artifacts (build must be in an earlier stage)'],
    ['<code>dependencies: []</code>', 'nothing, the job starts faster'],
    ['<code>needs: [build]</code>', 'only build\'s artifacts, and the job starts as soon as build is done'],
    ['<code>needs: [{job: build, artifacts: false}]</code>', 'waits for build but downloads nothing'],
    ['<code>needs: project: OWNER/other, job: build, ref: main, artifacts: true</code>', 'artifacts of the latest successful build job on main of another project, up to five such jobs (Premium and Ultimate)']])}
{devqa('<p>The build job uploads one archive, and later jobs in the same pipeline pick it up automatically or through needs. Developers rarely think about it until a job cannot find a file.</p>',
       '<p>QA jobs use needs: [build] so the tests always run against the build of the same pipeline. A separate QA project can pull the latest green build of the app project with needs:project or with the API and the job token.</p>',
       'Artifacts inside the pipeline')}
''', kw=['dependencies', 'dependencies empty', 'needs artifacts', 'needs project', 'cross project artifacts', 'earlier stages'])

K.lesson('pull', 'Pulling artifacts: UI, API, glab and job token', f'''
<p>GitLab gives you several ways to get a build back, from a click to a script in another pipeline.</p>
{table(['From', 'Where to click'], [
    ['A pipelines list', 'Download artifacts, then pick the job'],
    ['A jobs list', 'Download artifacts next to the job'],
    ['A job page', 'Download or Browse in the Job artifacts panel'],
    ['A merge request', 'Artifacts on the Overview page, for the latest pipeline'],
    ['Build, Artifacts', 'every artifact in the project, with Download and Browse']])}
{sh('REST API: latest successful build on main, by job name', """curl --location --header "PRIVATE-TOKEN: $TOKEN" \\
  --output calc-app.zip \\
  "https://gitlab.com/api/v4/projects/PROJECT_ID/jobs/artifacts/main/download?job=build"
# one file out of the archive
curl --location --header "PRIVATE-TOKEN: $TOKEN" --output calc-app-only.zip \\
  "https://gitlab.com/api/v4/projects/PROJECT_ID/jobs/artifacts/main/raw/dist/calc-app.zip?job=build"
""")}
{sh('REST API: a report file from a specific job', """curl --location --header "PRIVATE-TOKEN: $TOKEN" --output unit.xml.gz \\
  "https://gitlab.com/api/v4/projects/PROJECT_ID/jobs/JOB_ID/artifacts?file_type=junit"
""")}
{sh('The GitLab CLI', """glab auth login
glab job artifact main build
glab job artifact main build --path downloaded/""")}
{file('qa-project/.gitlab-ci.yml', """pull-latest-build:
  stage: test
  script:
    - apt-get update && apt-get install -y curl unzip
    - >
      curl --location --fail --header "JOB-TOKEN: $CI_JOB_TOKEN"
      --output build.zip
      "$CI_API_V4_URL/projects/$APP_PROJECT_ID/jobs/artifacts/main/download?job=build"
    - unzip build.zip
    - ls dist/
""", {4: 'The slim Python image has no curl or unzip, so install them.', 6: 'CI_JOB_TOKEN is created for each job and expires when the job ends. It can call the artifact download endpoints.', 8: 'CI_API_V4_URL is the API root of this GitLab instance. APP_PROJECT_ID is a variable you set to the app project\'s id.'})}
{table(['Rule', 'Detail'], [
    ['ref_name', 'a branch or tag name. For merge request pipelines use refs/merge-requests/IID/head, the variable CI_MERGE_REQUEST_REF_PATH holds it.'],
    ['Reports', 'not in the archive. Use the job id endpoint with file_type=junit, or list the file under paths.'],
    ['Job token', 'the other project must add the calling project to its CI/CD job token allowlist (Settings, CI/CD, Job token permissions).'],
    ['--location', 'GitLab.com may redirect through a CDN, so curl must follow redirects.']])}
{note('The finished release belongs in the package registry or a release asset, not in a job artifact that may expire. For example, publish a Python wheel to the project\'s PyPI registry in a tag pipeline with the CI_JOB_TOKEN.', 'exam')}
''', kw=['download artifacts', 'browse artifacts', 'job artifacts API', 'jobs/artifacts/main/download', 'file_type junit', 'glab job artifact', 'CI_JOB_TOKEN', 'JOB-TOKEN header', 'allowlist', 'CI_API_V4_URL', 'merge request ref', 'package registry'])

K.lesson('cache', 'Caching on GitLab', f'''
{file('cache-examples.yml', """variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

unit-tests:
  cache:
    key:
      files:
        - requirements.txt
      prefix: $CI_JOB_NAME
    paths:
      - .cache/pip
    policy: pull-push
""", {2: 'Make pip write its downloads inside the project folder, because only paths there can be cached.', 7: 'The key is computed from the content of these files, by default up to two files.', 9: 'An optional prefix keeps separate caches per job.', 11: 'What to save and restore.', 12: 'pull-push (default) restores and saves. pull only restores, push only saves. Many jobs use pull to save upload time.'})}
{viz('cachekey')}
{table(['', 'Artifacts', 'Cache'], [
    ['Meant for', 'results to pass on and keep', 'dependencies to reuse'],
    ['Shared between', 'jobs of the pipeline, people, API, other projects', 'runs of jobs on the same runner or shared cache storage'],
    ['Guaranteed', 'yes, until expiry', 'no, it is a best effort speed up'],
    ['Keyword', '<code>artifacts:</code>', '<code>cache:</code>']])}
{ladder(
    '<p>Artifacts keep the results of a job so others can use them, caches make the next run faster. You can download artifacts from many places in GitLab or with a script.</p>',
    '<p>artifacts: paths, name, when, expire_in, reports. Later stages fetch earlier artifacts, needs and dependencies narrow it. Pull with the UI, the API by ref and job name, glab job artifact, or CI_JOB_TOKEN from another project on the allowlist.</p>',
    '<p>The latest successful artifacts per ref are kept beyond expire_in. Reports live outside the archive and need file_type. Cache keys from files and per job prefixes keep caches correct, policies limit uploads.</p>',
    '<p>Fine grained job token permissions and signed build provenance make cross project artifact flows auditable, which matters when a QA or release project consumes builds from many application projects.</p>')}
''', kw=['cache', 'cache key files', 'prefix', 'cache policy', 'pull-push', 'pull', 'PIP_CACHE_DIR', 'artifacts vs cache'])

K.quiz('e', 'Which keyword keeps files from a GitLab job?', ['cache', 'artifacts', 'keep', 'store'], 1, 'Results.', 'artifacts: paths lists them.')
K.quiz('e', 'How long are artifacts kept on GitLab.com when expire_in is not set?', ['1 day', '30 days', '90 days', 'Forever'], 1, 'Instance default.', 'Self managed instances can choose another default.')
K.quiz('e', 'Where in the project UI do you see every artifact?', ['Settings, General', 'Build, Artifacts', 'Plan, Wiki', 'Code, Tags'], 1, 'Build menu.', 'Download and Browse are there.')
K.quiz('m', 'Without needs or dependencies, which artifacts does a job download?', ['None', 'All artifacts from jobs in earlier stages', 'Only from the same stage', 'Only from main'], 1, 'Default.', 'Use dependencies: [] to download nothing.')
K.quiz('m', 'Which API call downloads the latest successful build job artifacts on main?', ['GET /projects/:id/pipelines', 'GET /projects/:id/jobs/artifacts/main/download?job=build', 'GET /projects/:id/repository/archive', 'POST /projects/:id/artifacts'], 1, 'jobs/artifacts.', 'Add --location to curl on GitLab.com.')
K.quiz('m', 'Why does downloading the junit report with the ref and job name endpoint give 404?', ['Wrong token', 'Reports are not in the archive, use the job id endpoint with file_type=junit', 'Reports expire at once', 'JUnit is not supported'], 1, 'Separate storage.', 'Or add the file to paths.')
K.quiz('m', 'Which glab command downloads the artifacts of job build on main?', ['glab ci get build', 'glab job artifact main build', 'glab pull build', 'glab artifact main'], 1, 'job artifact.', '--path chooses the folder.')
K.quiz('h', 'A QA project uses CI_JOB_TOKEN to download from the app project and gets 403 or 404. What is missing?', ['A runner', 'The QA project must be on the app project\'s job token allowlist', 'expire_in', 'A tag'], 1, 'Allowlist.', 'Settings, CI/CD, Job token permissions on the app project.')
K.quiz('h', 'What does cache policy: pull do?', ['Saves only', 'Restores the cache but does not upload it at the end', 'Disables cache', 'Pulls artifacts'], 1, 'Read only.', 'Saves time in jobs that do not change dependencies.')
K.quiz('x', 'Your build artifact has expire_in: 1 week, but the build from the last green pipeline on main from a month ago can still be downloaded. Why?', ['A bug', 'GitLab keeps artifacts of the latest successful pipeline on each ref regardless of expire_in', 'Someone pressed Keep', 'Caching'], 1, 'Latest kept.', 'They go once a newer pipeline succeeds on that ref.')

K.calc('e', 'expire_in: 2 weeks. How many days is that?', '14', 'Weeks to days.',
       ['1 week = 7 days.', '2 × 7.', eq('14 days')], check=14)
K.calc('e', 'A job sets dependencies: []. How many artifact archives does it download?', '0', 'Empty list.',
       ['dependencies lists the jobs to fetch from.', 'The list is empty.', eq('0 archives')], check=0)
K.calc('m', 'Stages: build (2 jobs with artifacts), test (3 jobs with artifacts), report. The report job sets nothing. How many archives does it download?', '5', 'All earlier stages.',
       ['Earlier stages: build and test.', '2 + 3 jobs with artifacts.', eq('5 archives')], check=5)
K.calc('m', 'Same pipeline, the report job sets needs to the 3 test jobs. How many archives?', '3', 'Only what needs names.',
       ['needs limits downloads to the listed jobs.', '3 test jobs.', eq('3 archives')], check=3)
K.calc('h', 'Each pipeline keeps a 200 MB build for 30 days, 10 pipelines a day. Steady state storage in GB (1 GB = 1000 MB)?', '60', 'Size × count × days.',
       ['Per day: 10 × 200 = 2000 MB.', 'Kept 30 days: 2000 × 30 = 60000 MB.', eq('60 GB')], check=60)
K.calc('h', 'Same, but you shorten expire_in to 7 days. How many GB are saved?', '46', 'Difference in days.',
       ['New storage: 2000 MB × 7 = 14000 MB = 14 GB.', 'Old storage: 60 GB.', eq('60 - 14 = 46 GB saved')], check=46)

K.must('artifacts keyword', 'paths, exclude, name, when (on_success, on_failure, always), expire_in (GitLab.com default 30 days), access, reports: junit. Latest successful artifacts per ref are kept beyond expire_in. Keep button. 1 GB on GitLab.com.')
K.must('Between jobs', 'Earlier stages by default, dependencies: [list] or [] to narrow, needs: [job] to start early and fetch, needs:project for other projects (Premium).')
K.must('Pull artifacts', 'UI: pipelines, jobs, job page, MR, Build Artifacts. API: /projects/:id/jobs/artifacts/:ref/download?job=name, /jobs/:job_id/artifacts?file_type=junit. CLI: glab job artifact <ref> <job>. CI_JOB_TOKEN with JOB-TOKEN header plus allowlist.')
K.must('Cache', 'cache key files (up to two), prefix, paths inside the project, policy pull-push, pull or push. Best effort only.')
K.must('Releases', 'Artifacts expire. Releases go to the package registry or release assets.')

T = K.topic(
    slug='gitlab-artifacts', topic='gitlab-artifacts', step=(8, 'GitLab CI/CD', 'gitlab-ci', 'Write GitLab pipelines from the first line: stages, rules, needs and runners, then the same Dev and QA pipeline built from scratch on GitLab, then artifacts, reports and how to pull a build with the API and glab.', 'Intermediate'),
    title='GitLab artifacts and caching: keep, pass on and pull builds', short='GitLab artifacts', badge='8.3', minutes=55, added='2026-11-02',
    lead='Keep build outputs and test reports, pass them between jobs, and pull them back from the UI, the REST API, the glab CLI or another project\'s pipeline with the job token, then speed things up with caches.',
    desc='artifacts paths, exclude, name, when, expire_in, access and reports, kept latest artifacts and the Keep button, default artifact passing, dependencies and needs, needs:project, downloading from the UI, the job artifacts API by ref and by job id, report file types, merge request refs, glab job artifact, CI_JOB_TOKEN and the allowlist, cache keys, prefixes and policies, and the package registry.',
    summary='GitLab artifacts and reports, passing them between jobs, pulling with UI, API, glab and job token, and caching.',
    keywords=['gitlab artifacts', 'expire_in', 'reports junit', 'dependencies', 'job artifacts api', 'glab', 'ci_job_token', 'gitlab cache'],
    recap='<p>Keep results with artifacts, narrow what jobs fetch with needs and dependencies, pull builds with the UI, API, glab or the job token, and cache only what is safe to lose.</p>')
