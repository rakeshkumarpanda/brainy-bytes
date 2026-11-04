# Chapter 8.1: GitLab CI/CD concepts. .gitlab-ci.yml, stages (default .pre, build, test, deploy, .post), jobs and
# script, image and services, default, variables and predefined variables, rules and when, workflow:rules and
# duplicate pipelines, merge request pipelines, needs (up to 50) and DAG pipelines, parallel:matrix (up to 200),
# extends, include, runners (instance, group, project) and executors, pipeline sources. Sources: GitLab docs: CI/CD
# YAML syntax reference, job rules, workflow keyword, merge request pipelines, predefined variables, runners,
# quick start, pipeline architectures. Checked on 2026-11-02 against gitlab-org/gitlab master.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from gitkit import sh, flow, file, devqa

K = Kit()

K.lesson('basics', 'One file, stages and jobs', f'''
<p>GitLab reads one file, <code>.gitlab-ci.yml</code>, at the root of the repository. Every top level key that is not a reserved keyword is a <b>job</b>. A job needs a <code>script</code> and belongs to a <b>stage</b>. Jobs in the same stage run in parallel, and by default a stage starts only after every job of the previous stage succeeded.</p>
{file('.gitlab-ci.yml', """stages:
  - build
  - test

default:
  image: python:3.13-slim

variables:
  APP_NAME: calc-app

build-job:
  stage: build
  script:
    - echo "Building $APP_NAME at $CI_COMMIT_SHORT_SHA"

test-job:
  stage: test
  script:
    - python --version
""", {1: 'The order of stages. Without this key GitLab uses .pre, build, test, deploy, .post.', 5: 'default applies settings to every job, here the Docker image each job runs in.', 8: 'Variables for all jobs. Read them as $NAME in scripts.', 11: 'A job. The name is yours, it appears in the pipeline graph.', 14: 'CI_COMMIT_SHORT_SHA is one of many predefined variables GitLab sets in every job.'})}
{viz('pipeline', preset='starter', plat='gitlab', mode='stages')}
{table(['Keyword', 'Where', 'Does'], [
    ['<code>stages</code>', 'top', 'order of stages'],
    ['<code>default</code>', 'top', 'image, before_script, after_script, cache, retry and more for every job'],
    ['<code>variables</code>', 'top or job', 'CI/CD variables'],
    ['<code>workflow</code>', 'top', 'whether the whole pipeline is created'],
    ['<code>include</code>', 'top', 'pull in YAML from other files, projects, templates or components'],
    ['<code>stage</code>, <code>script</code>', 'job', 'where it runs and the shell commands (script is required)'],
    ['<code>image</code>, <code>services</code>', 'job', 'Docker image for the job, and side containers such as a database'],
    ['<code>rules</code>, <code>needs</code>', 'job', 'when the job is added, and which jobs it waits for'],
    ['<code>artifacts</code>, <code>cache</code>', 'job', 'files to keep and pass on, files to reuse between pipelines']])}
{note('script lines run in order, and the job fails at the first command that exits with a non zero code. after_script still runs, but its result does not change the job status.', 'exam')}
''', kw=['.gitlab-ci.yml', 'stages', 'job', 'script', 'default', 'image', 'services', 'variables', '.pre', '.post', 'before_script', 'after_script'])

K.lesson('rules', 'rules, workflow and pipeline types', f'''
<p><code>rules</code> decide if a job is added to a pipeline. GitLab reads them top to bottom and the <b>first rule that matches</b> decides. If none matches, the job is left out. Change the pipeline source and branch in the animation and see which rule wins.</p>
{viz('glrules')}
{table(['Pipeline type', 'Started by', 'Useful variables'], [
    ['Branch pipeline', 'a push to a branch', 'CI_COMMIT_BRANCH (not set in merge request or tag pipelines)'],
    ['Tag pipeline', 'pushing a tag', 'CI_COMMIT_TAG'],
    ['Merge request pipeline', 'creating or updating a merge request, when a job has rules for it', 'CI_PIPELINE_SOURCE == "merge_request_event", CI_MERGE_REQUEST_TARGET_BRANCH_NAME'],
    ['Scheduled pipeline', 'Build, Pipeline schedules', 'CI_PIPELINE_SOURCE == "schedule"'],
    ['Manual run', 'Build, Pipelines, New pipeline', 'CI_PIPELINE_SOURCE == "web"']])}
{file('workflow-rules.yml', """workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
""", {1: 'workflow:rules decide whether a pipeline is created at all, before any job rules.', 3: 'Always run for merge requests.', 4: 'A push to a branch that already has an open merge request: skip the branch pipeline, because the merge request pipeline covers it.', 6: 'Every other branch push gets a branch pipeline. Tags match no rule, so tag pushes create no pipeline with this block.'})}
{note('Add a rule for merge requests to one job without workflow:rules and a single push to a branch with an open merge request can start two pipelines, a branch pipeline and a merge request pipeline. The workflow block above is the documented fix.', 'warn')}
''', kw=['rules', 'if', 'when', 'never', 'on_success', 'manual', 'workflow rules', 'duplicate pipelines', 'merge request pipeline', 'CI_PIPELINE_SOURCE', 'CI_COMMIT_BRANCH', 'CI_OPEN_MERGE_REQUESTS', 'CI_COMMIT_TAG'])

K.lesson('needs', 'needs, parallel, extends and include', f'''
{fxs(
    fx('Skip waiting for the stage', '<code>needs: [build]</code>', 'The job starts as soon as build is done, even if other jobs of the build stage still run. needs: [] starts at once. Up to 50 jobs in one needs list.', key=True),
    fx('Run a job many times', '<code>parallel: 3</code> or <code>parallel: matrix:</code>', 'parallel: 3 gives jobs 1/3, 2/3, 3/3 with CI_NODE_INDEX and CI_NODE_TOTAL for test splitting. parallel:matrix sets variables, at most 200 combinations.', key=True),
    fx('Reuse a job template', '<code>.python-job:</code> then <code>extends: .python-job</code>', 'Jobs whose name starts with a dot are hidden and never run, so they work as templates.'),
    fx('Split the file', '<code>include: local:</code>, <code>project:</code>, <code>remote:</code>, <code>template:</code>, <code>component:</code>', 'Share one pipeline definition between many projects.'))}
{file('reuse-example.yml', """.python-job:
  image: python:3.13-slim
  before_script:
    - pip install -r requirements.txt

unit-tests:
  extends: .python-job
  stage: test
  script:
    - python -m pytest -q tests/unit

e2e:
  extends: .python-job
  stage: test
  needs: [build]
  parallel: 3
  script:
    - python -m pytest -q tests/e2e --shard $CI_NODE_INDEX/$CI_NODE_TOTAL
""", {1: 'A hidden job: the leading dot means GitLab never runs it on its own.', 7: 'Copies image and before_script from the template, then adds its own keys.', 15: 'Starts right after build, without waiting for the rest of the stage.', 16: 'Three copies of the job run in parallel.', 18: 'Each copy picks its share of tests. The --shard option here belongs to a pytest plugin you would add, it is not built into pytest.'})}
{viz('pipeline', preset='slow', plat='gitlab', mode='stages')}
<p>Switch the animation above between stage mode and needs mode: the long docs build no longer holds back the web deployment.</p>
''', kw=['needs', 'DAG', 'needs empty', 'parallel', 'parallel matrix', 'CI_NODE_INDEX', 'extends', 'hidden job', 'include', 'component', 'template'])

K.lesson('runners', 'Runners, executors and variables', f'''
<p>A <b>runner</b> is the agent that picks up jobs and runs them. On GitLab.com, GitLab hosted instance runners are ready for every project, so you can skip setting up your own. You can still register your own runner for a project or group, for example to reach machines inside your network.</p>
{table(['Runner scope', 'Available to'], [['Instance', 'every project on the GitLab instance (GitLab hosted runners on GitLab.com are instance runners)'], ['Group', 'every project in a group'], ['Project', 'one project']])}
{table(['Executor', 'Runs each job', 'Note'], [
    ['Docker', 'in a fresh container from the job image', 'the most common, clean for each job'],
    ['Shell', 'directly on the runner machine', 'simple, but jobs share the machine and its leftovers'],
    ['Kubernetes', 'in a pod in a cluster', 'scales out for many parallel jobs']])}
{fxs(
    fx('Project variables', 'Settings, CI/CD, Variables', 'Masked hides the value in job logs. Protected passes it only to pipelines on protected branches and tags.', key=True),
    fx('Predefined variables', '<code>$CI_COMMIT_SHA</code>, <code>$CI_PROJECT_DIR</code>, <code>$CI_JOB_TOKEN</code>, <code>$CI_API_V4_URL</code>', 'Set by GitLab in every job.'),
    fx('Pick a runner', '<code>tags: [linux, docker]</code>', 'A job only runs on runners that have all of its tags.'))}
{devqa('<ul><li>Uses needs to get feedback faster.</li><li>Keeps secrets protected so feature branches cannot read production keys.</li><li>Moves shared setup into a template with extends or include.</li></ul>',
       '<ul><li>Uses parallel to split slow suites across runners.</li><li>Uses scheduled pipelines and rules on CI_PIPELINE_SOURCE for nightly regression.</li><li>Keeps test environments in protected variables and uses services for a test database.</li></ul>',
       'GitLab features each side reaches for')}
{ladder(
    '<p>One YAML file lists stages and jobs, and runners run them. rules decide which jobs appear in each pipeline.</p>',
    '<p>Jobs need script and stage. default, variables, image and services set the environment. rules match top down with when, workflow:rules control whole pipelines and prevent duplicates. needs makes a graph, parallel splits work, extends and include reuse YAML.</p>',
    '<p>Pipeline source, branch, tag and merge request variables drive the rules. Protected and masked variables limit secret exposure. Executors trade isolation against speed.</p>',
    '<p>CI/CD components and the catalog version pipeline building blocks like libraries, with inputs and semantic versions, so many projects can share one tested pipeline definition.</p>')}
''', kw=['runner', 'instance runner', 'group runner', 'project runner', 'executor', 'docker executor', 'shell executor', 'kubernetes', 'tags', 'masked', 'protected variable', 'CI_JOB_TOKEN'])

K.quiz('e', 'What is the name of the GitLab CI/CD file?', ['gitlab.yml', '.gitlab-ci.yml', '.github/workflows/ci.yml', 'pipeline.yml'], 1, 'Dot, gitlab, ci.', 'At the root of the repository.')
K.quiz('e', 'Which key is required in every job?', ['stage', 'script', 'image', 'rules'], 1, 'Commands.', 'stage defaults to test.')
K.quiz('e', 'Without a stages key, what are the stages?', ['only test', '.pre, build, test, deploy, .post', 'lint, test', 'none'], 1, 'Defaults.', 'Jobs without stage go to test.')
K.quiz('m', 'Jobs in the same stage run', ['one after another', 'in parallel', 'only on main', 'only manually'], 1, 'Side by side.', 'If enough runners are free.')
K.quiz('m', 'A job has rules and none matches. What happens?', ['It runs', 'It is not added to the pipeline', 'It fails', 'It waits'], 1, 'No match, no job.', 'Add a final rule if you want a fallback.')
K.quiz('m', 'Which variable is not set in a merge request pipeline?', ['CI_PIPELINE_SOURCE', 'CI_COMMIT_BRANCH', 'CI_COMMIT_SHA', 'CI_PROJECT_DIR'], 1, 'Branch pipelines only.', 'Use CI_MERGE_REQUEST_SOURCE_BRANCH_NAME there.')
K.quiz('m', 'What does needs: [build] change?', ['Nothing', 'The job starts as soon as build finishes, without waiting for its whole stage', 'build runs twice', 'The job skips artifacts'], 1, 'DAG.', 'It also fetches artifacts from build by default.')
K.quiz('h', 'A push to a branch with an open MR starts two pipelines. The documented fix?', ['Delete the MR', 'workflow:rules that skip branch pipelines when CI_OPEN_MERGE_REQUESTS is set', 'Use only/except', 'Remove stages'], 1, 'workflow.', 'The MR pipeline covers the change.')
K.quiz('h', 'What is a job whose name starts with a dot?', ['A failing job', 'A hidden job used as a template with extends', 'A manual job', 'A deploy job'], 1, 'Hidden.', 'It never runs on its own.')
K.quiz('x', 'A protected variable is defined. A pipeline on feature/x (not protected) uses it. Value?', ['The real value', 'Empty, protected variables reach only protected branches and tags', 'Masked stars', 'An error'], 1, 'Protection.', 'This keeps production secrets away from untrusted branches.')

K.calc('e', 'Stages build (1 job) and test (3 jobs). How many jobs in the pipeline?', '4', 'Add.',
       ['build: 1.', 'test: 3.', eq('4 jobs')], check=4)
K.calc('e', 'parallel: 4 on one job. How many job instances run?', '4', 'Copies.',
       ['parallel: N creates N jobs.', 'Named 1/4 to 4/4.', eq('4')], check=4)
K.calc('m', 'parallel:matrix with PROVIDER: [aws, gcp] and STACK: [web, db, cache]. How many jobs?', '6', 'Multiply.',
       ['2 providers.', '3 stacks.', eq('2 × 3 = 6 jobs')], check=6)
K.calc('m', 'Stage build has jobs of 2 and 9 minutes, stage test has a 3 minute job that needs only the 2 minute one. Total with stages only?', '12', 'Wait for the slowest.',
       ['build stage ends at 9.', 'test job runs 9 to 12.', eq('12 minutes')], check=12)
K.calc('m', 'Same jobs, but the test job has needs on the 2 minute job. Total?', '9', 'Longest path.',
       ['test job runs 2 to 5.', 'The 9 minute job ends at 9.', eq('max(5, 9) = 9 minutes')], check=9)
K.calc('h', 'Rules: 1) if MR then on_success, 2) if schedule then never, 3) if branch main then manual. A scheduled pipeline on main. Which rule number decides?', '2', 'First match.',
       ['Rule 1: not an MR.', 'Rule 2: schedule matches, when never.', eq('rule 2 decides, the job is not added')], check=2)

K.must('File and stages', '.gitlab-ci.yml at the root. Default stages .pre, build, test, deploy, .post. Same stage in parallel, next stage after the previous one succeeds. script is required.')
K.must('Rules', 'Top down, first match decides, when never excludes, no match excludes. workflow:rules decide the whole pipeline and stop duplicate branch plus MR pipelines.')
K.must('Pipeline types', 'Branch (CI_COMMIT_BRANCH), tag (CI_COMMIT_TAG), merge request (CI_PIPELINE_SOURCE merge_request_event), schedule, web.')
K.must('Speed and reuse', 'needs (up to 50, needs: [] starts at once), parallel N or matrix (up to 200), hidden .jobs with extends, include for shared YAML.')
K.must('Runners and variables', 'Instance, group, project runners. Docker, shell, Kubernetes executors. tags select runners. Masked and protected variables for secrets.')

T = K.topic(
    slug='gitlab-concepts', topic='gitlab-concepts', step=(8, 'GitLab CI/CD', 'gitlab-ci', 'Write GitLab pipelines from the first line: stages, rules, needs and runners, then the same Dev and QA pipeline built from scratch on GitLab, then artifacts, reports and how to pull a build with the API and glab.', 'Intermediate'),
    title='GitLab CI/CD: stages, rules, needs and runners', short='GitLab concepts', badge='8.1', minutes=55, added='2026-11-02',
    lead='Read and write any .gitlab-ci.yml: stages and jobs, how rules and workflow:rules decide what runs, how to avoid duplicate pipelines, how needs and parallel speed things up, and what runners and executors are.',
    desc='.gitlab-ci.yml structure, stages and default stages, jobs, script, default, image and services, variables and predefined variables, rules and when, workflow:rules and duplicate pipelines, branch, tag, merge request and scheduled pipelines, needs and DAG pipelines, parallel and parallel:matrix, extends and include, runners, executors, tags, masked and protected variables.',
    summary='GitLab pipeline structure, rules and workflow, pipeline types, needs, parallel, extends, include, runners and variables.',
    keywords=['gitlab ci', '.gitlab-ci.yml', 'stages', 'rules', 'workflow rules', 'needs', 'runner', 'executor'],
    recap='<p>One file of stages and jobs, rules that match top down, workflow rules that prevent duplicates, needs and parallel for speed, and runners that execute it all.</p>')
