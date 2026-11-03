# Chapter 3.2: stash, clean, tags (lightweight and annotated, semantic versioning), .gitignore rules, git check-ignore,
# .gitattributes for line endings, binary files and Git LFS. Sources: Pro Git 2.6, 7.3, 8.2, gitignore(5),
# gitattributes(5), git-stash, git-clean, git-tag manuals, semver.org 2.0.0.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow, file

K = Kit()

K.code('semver', r'''
# Semantic versioning: MAJOR.MINOR.PATCH and which part to bump
def bump(version, change):
    major, minor, patch = (int(x) for x in version.split("."))
    if change == "breaking":
        return f"{major + 1}.0.0"
    if change == "feature":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"

v = "1.4.2"
for change in ["fix", "feature", "fix", "breaking", "feature"]:
    v = bump(v, change)
    print(f"{change:8} -> v{v}")
''')

K.lesson('stash', 'git stash: put work aside for a moment', f'''
<p>You are halfway through a feature when an urgent bug comes in. Your work is not ready to commit, and Git will not let you switch branches if your edits clash. <b>git stash</b> saves your uncommitted changes on a stack and gives you a clean working tree. Later you take them back.</p>
{viz('areas', cmds='edit app.py\ngit stash\nedit README.md\ngit commit -am "urgent fix"\ngit stash pop')}
{fxs(
    fx('Save and clean', '<code>git stash</code> or <code>git stash push -m "note"</code>', 'Saves staged and unstaged changes to tracked files. -u also saves untracked files.', key=True),
    fx('Bring back', '<code>git stash pop</code>, <code>git stash apply</code>', 'pop applies the newest stash and drops it. apply keeps it on the stack.', key=True),
    fx('Look and tidy', '<code>git stash list</code>, <code>git stash show -p stash@{1}</code>, <code>git stash drop</code>', 'stash@{0} is the newest.'),
    fx('Turn a stash into a branch', '<code>git stash branch &lt;name&gt;</code>', 'Creates a branch at the commit where you stashed and applies the stash there, avoiding conflicts.'))}
{note('A stash is easy to forget. If it holds real work, a work in progress commit on a branch is often safer and shows up in git log.', 'tip')}
{deep('git clean', '<p>git clean removes untracked files. Always run git clean -n first, a dry run that lists what would go. -d also removes untracked folders, -x also removes ignored files such as build output. -f is required to actually delete. Files removed by clean were never in Git, so nothing can restore them.</p>')}
''', kw=['git stash', 'stash pop', 'stash apply', 'stash list', 'stash -u', 'stash branch', 'git clean', 'clean -n'])

K.lesson('tags', 'Tags and version numbers', f'''
<p>A <b>tag</b> is a name for one commit that never moves, unlike a branch. Teams tag the commit they release: <code>v1.0.0</code>, <code>v1.1.0</code>. CI pipelines often start a release job when a tag is pushed.</p>
{table(['Kind', 'Command', 'Stores', 'Use for'], [
    ['Lightweight', '<code>git tag v1.0.0</code>', 'Only a ref pointing at the commit', 'private or temporary marks'],
    ['Annotated', '<code>git tag -a v1.0.0 -m "Release 1.0.0"</code>', 'A tag object with tagger, date, message (and optional signature)', 'releases']])}
{fxs(
    fx('Push tags', '<code>git push origin v1.0.0</code>, <code>git push --tags</code>', 'git push alone does not send tags. --follow-tags sends annotated tags that point at pushed commits.', key=True),
    fx('List and inspect', '<code>git tag -l "v1.*"</code>, <code>git show v1.0.0</code>, <code>git describe</code>', 'git describe names HEAD by the nearest tag, for example v1.0.0-3-g7c9e1d0 (3 commits after the tag).'),
    fx('Semantic versioning', 'MAJOR.MINOR.PATCH', 'MAJOR for breaking changes, MINOR for new backwards compatible features, PATCH for backwards compatible bug fixes.', key=True))}
{code('semver')}
{note('Moving a tag that others have fetched is like changing a published book\'s edition number. Do not do it. Make a new tag instead.', 'warn')}
''', kw=['git tag', 'annotated tag', 'lightweight tag', 'push tags', 'follow-tags', 'git describe', 'semantic versioning', 'semver'])

K.lesson('ignore', '.gitignore: keep junk out', f'''
<p>Some files must never be committed: build output, dependency folders, logs, editor files and above all secrets such as <code>.env</code> files with passwords. A <code>.gitignore</code> file lists patterns, and git status stops showing matching untracked files.</p>
{file('.gitignore', """# Python
__pycache__/
*.pyc
.venv/
# build output and test reports
dist/
reports/
# logs, but keep one example
*.log
!example.log
# secrets: only the file in the top folder
/.env""", {2: 'A trailing slash matches folders only, at any depth.', 3: 'A star matches any characters except a slash.', 10: 'A leading ! re-includes a file an earlier rule ignored. The last matching rule wins.', 12: 'A leading slash anchors the rule to the folder that holds this .gitignore.'}, lang='text')}
{viz('ignore')}
{table(['Pattern', 'Matches'], [
    ['<code>*.log</code>', 'any .log file in any folder'],
    ['<code>/todo.txt</code>', 'only todo.txt next to the .gitignore'],
    ['<code>build/</code>', 'any folder called build, and everything inside'],
    ['<code>docs/**/*.pdf</code>', 'PDFs anywhere under docs'],
    ['<code>!keep.log</code>', 'brings keep.log back, unless its parent folder is ignored']])}
{fxs(fx('Why is this file ignored?', '<code>git check-ignore -v &lt;path&gt;</code>', 'Prints the .gitignore file, line number and pattern that matched.', key=True),
     fx('Already committed by mistake', '<code>git rm --cached &lt;file&gt;</code> then commit', '.gitignore only affects untracked files. A tracked file stays tracked until you remove it from the index.', key=True))}
{note('If a secret was ever committed and pushed, removing it in a new commit is not enough: it is still in history. Treat it as leaked and rotate the password or key at once.', 'warn')}
{deep('Other ignore files', '<p>.git/info/exclude works like .gitignore but is never shared. core.excludesFile (often ~/.config/git/ignore) holds personal patterns for every repository, a good place for .DS_Store or editor folders. Order of precedence: patterns on the command line, .gitignore files from the folder of the path up to the top, .git/info/exclude, then core.excludesFile.</p>')}
''', kw=['.gitignore', 'ignore pattern', 'negation', 'check-ignore', 'rm --cached', 'info/exclude', 'excludesFile', 'secrets'])

K.lesson('attrs', '.gitattributes, line endings and big files', f'''
<p>Windows ends lines with CRLF, macOS and Linux with LF. Without rules, a whole file can look changed because only the line endings differ. <code>.gitattributes</code> fixes this per path and is committed, so the whole team follows it.</p>
{file('.gitattributes', """* text=auto
*.sh text eol=lf
*.bat text eol=crlf
*.png binary
*.psd filter=lfs diff=lfs merge=lfs -text""", {1: 'Let Git detect text files and store them with LF inside the repository.', 2: 'Shell scripts must keep LF even on Windows, or bash fails.', 4: 'binary means no line ending changes and no text diff.', 5: 'Written by git lfs track "*.psd": the content goes to Git LFS storage, the repository keeps a small pointer.'}, lang='text')}
{ladder(
    '<p>stash is a drawer for unfinished work, tags are name labels on finished versions, and .gitignore is a list of things that should never go in the box.</p>',
    '<p>A stash is stored as commits under refs/stash. Annotated tags are tag objects, lightweight tags are plain refs. .gitignore patterns follow the rules in gitignore(5), last match wins, and a file cannot be re-included if a parent folder is excluded.</p>',
    '<p>Line ending normalisation happens in the clean and smudge steps between the working tree and the index. Git LFS uses the same filter mechanism: clean replaces large content with a pointer file, smudge downloads it on checkout.</p>',
    '<p>Signed tags (git tag -s) and signed commits, now also with SSH keys, are part of software supply chain security. Projects such as Sigstore and reproducible builds aim to prove that a released artifact really came from a given tagged commit.</p>')}
''', kw=['.gitattributes', 'line endings', 'CRLF', 'LF', 'text=auto', 'binary', 'Git LFS', 'signed tags'])

K.quiz('e', 'Which command saves your uncommitted changes and cleans the working tree?', ['git save', 'git stash', 'git clean', 'git reset'], 1, 'Drawer.', 'git stash puts changes on a stack.')
K.quiz('e', 'What is the difference between git stash pop and git stash apply?', ['None', 'pop also removes the stash from the list', 'apply removes it', 'pop only shows it'], 1, 'Pop takes it off.', 'apply keeps it for later use too.')
K.quiz('e', 'A tag is', ['A branch that moves', 'A fixed name for one commit', 'A remote', 'A commit message'], 1, 'Never moves.', 'Tags mark releases.')
K.quiz('m', 'Does git push send your tags?', ['Yes, always', 'No, use git push origin <tag> or --tags', 'Only annotated', 'Only on main'], 1, 'Separate.', 'Tags are pushed explicitly or with --follow-tags.')
K.quiz('m', 'You add secrets.env to .gitignore but git status still shows it modified. Why?', ['Bad pattern', 'It is already tracked, ignore rules only affect untracked files', 'Cache problem', 'Wrong folder'], 1, 'Tracked already.', 'git rm --cached secrets.env, then commit.')
K.quiz('m', 'Which pattern ignores a file named .env only in the top folder?', ['.env', '/.env', '**/.env', '.env/'], 1, 'Anchor.', 'A leading slash anchors the rule.')
K.quiz('m', 'Version 2.3.1 gets a backwards compatible new feature. The next version is', ['2.3.2', '2.4.0', '3.0.0', '2.4.1'], 1, 'MINOR.', 'MINOR goes up and PATCH resets to 0.')
K.quiz('h', 'logs/ is ignored and a later line says !logs/keep.log. Is logs/keep.log tracked?', ['Yes', 'No, a file cannot be re-included when its parent folder is excluded', 'Only on Windows', 'Only with -f'], 1, 'Parent trap.', 'Use logs/* then !logs/keep.log instead.')
K.quiz('h', 'Which command tells you which rule ignores a path?', ['git status --ignored', 'git check-ignore -v path', 'git ls-files', 'git log --ignored'], 1, '-v for verbose.', 'It prints the source file, line and pattern.')
K.quiz('x', 'A password was committed and pushed last week. What must happen first?', ['Delete the file in a new commit', 'Rotate (change) the password, because it is in history and may be copied', 'Add it to .gitignore', 'Force push'], 1, 'Assume leaked.', 'Rewriting history helps later, but clones and caches may already have it.')

K.calc('e', 'Starting at 1.4.2: a fix, then a feature, then a fix. What is the patch number?', '1', 'Feature resets patch.',
       ['fix: 1.4.3.', 'feature: 1.5.0.', eq('fix: 1.5.1, patch = 1')], check=1)
K.calc('e', 'You run git stash three times without popping. Which number n is the oldest, in stash@{n}?', '2', 'Newest is 0.',
       ['stash@{0} is the latest.', 'Three stashes: 0, 1, 2.', eq('Oldest is stash@{2}')], check=2)
K.calc('m', 'From 2.7.3 a breaking change ships. Write the new version as a number by removing the dots (for example 1.2.3 is 123).', '300', 'MAJOR up, others zero.',
       ['Breaking change: MAJOR goes from 2 to 3.', 'MINOR and PATCH reset to 0.', eq('3.0.0, written 300')], check=300)
K.calc('m', 'git describe prints v2.1.0-5-g3f2a9c1. How many commits is HEAD past the tag?', '5', 'The middle number.',
       ['Format: tag, count, g plus short id.', 'Count = 5.', eq('5 commits after v2.1.0')], check=5)
K.calc('h', 'Rules: *.log, !keep.log. Paths: a.log, keep.log, x/keep.log, b.txt. How many are ignored?', '1', 'keep.log is re-included at any depth.',
       ['a.log matches *.log: ignored.', 'keep.log and x/keep.log match !keep.log last: tracked.', eq('b.txt matches nothing: so 1 ignored')], check=1)
K.calc('h', 'Rules: build/ then !build/keep.txt. Paths: build/a.o, build/keep.txt. How many are ignored?', '2', 'Parent folder trap.',
       ['build/ ignores the folder.', 'A file inside an ignored folder cannot be re-included.', eq('Both ignored: 2')], check=2)

K.assign('bump', 'e', 'Bump a semantic version',
         '<p>Write <code>bump(version, change)</code> where change is "fix", "feature" or "breaking". Return the next version string.</p>',
         '''
def bump(version, change):
    # your code here
    pass
''', [("bump('1.4.2', 'fix')", '1.4.3'), ("bump('1.4.2', 'feature')", '1.5.0'), ("bump('1.4.2', 'breaking')", '2.0.0'), ("bump('0.9.9', 'feature')", '0.10.0')],
         '''
def bump(version, change):
    major, minor, patch = (int(x) for x in version.split('.'))
    if change == 'breaking':
        return f'{major + 1}.0.0'
    if change == 'feature':
        return f'{major}.{minor + 1}.0'
    return f'{major}.{minor}.{patch + 1}'
''', 'Split on dots, turn into numbers, reset the lower parts.', '<p>Note 0.9.9 becomes 0.10.0, not 1.0.0. Numbers are not decimals.</p>')
K.assign('ign', 'h', 'A tiny .gitignore matcher',
         '<p>Write <code>ignored(rules, path)</code> for rules made only of simple patterns: <code>*.ext</code> (any depth), <code>name/</code> (a folder at any depth), <code>/name</code> (top level only) and <code>!</code> in front to re-include. Last matching rule wins, but a file inside an ignored folder stays ignored.</p>',
         '''
def ignored(rules, path):
    # your code here
    pass
''', [("ignored(['*.log', '!keep.log'], 'x/keep.log')", False), ("ignored(['*.log'], 'a/b/c.log')", True), ("ignored(['build/', '!build/keep.txt'], 'build/keep.txt')", True),
      ("ignored(['/.env'], 'config/.env')", False), ("ignored(['/.env'], '.env')", True)],
         '''
def match(rule, path):
    parts = path.split('/')
    if rule.endswith('/'):
        return rule[:-1] in parts[:-1]
    if rule.startswith('/'):
        return path == rule[1:]
    if rule.startswith('*.'):
        return parts[-1].endswith(rule[1:])
    return parts[-1] == rule

def ignored(rules, path):
    for r in rules:
        if r.endswith('/') and not r.startswith('!') and match(r, path):
            return True
    result = False
    for r in rules:
        neg = r.startswith('!')
        if match(r[1:] if neg else r, path):
            result = not neg
    return result
''', 'Check ignored folders first, then walk the rules and remember the last match.', '<p>Real Git supports more (**, ?, [a-z], patterns with a slash in the middle), as the animation shows.</p>')

K.must('Stash', 'git stash (-u for untracked), stash list, pop (apply and drop), apply (keep), stash branch. A WIP commit is often safer.')
K.must('Tags', 'Lightweight = plain ref, annotated (-a -m) = tag object for releases. Push with git push origin <tag> or --tags. Never move a shared tag.')
K.must('Semver', 'MAJOR.MINOR.PATCH: breaking, feature, fix. Lower parts reset to 0.')
K.must('.gitignore', 'Last match wins, ! re-includes, leading / anchors, trailing / means folder, no re-include inside an ignored folder. check-ignore -v explains.')
K.must('Tracked stays tracked', 'Ignore rules do not untrack files: git rm --cached. A committed secret is leaked: rotate it.')

T = K.topic(
    slug='stash-tags-ignore', topic='stash-tags-ignore', step=(3, 'Undo, stash, tags and ignore rules', 'git-undo', 'Undo safely at every level, rescue lost commits, park work in the stash, mark releases with tags and keep junk out with .gitignore.', 'Intermediate'),
    title='Stash, tags, .gitignore and .gitattributes', short='Stash, tags, ignore', badge='3.2', minutes=45, added='2026-11-02',
    lead='Park unfinished work, mark releases with version tags, keep build output and secrets out of the repository, and stop line ending noise.',
    desc='git stash push, pop, apply and branch, git clean, lightweight and annotated tags, pushing tags, git describe, semantic versioning, .gitignore patterns and precedence, check-ignore, rm --cached, .gitattributes, line endings and Git LFS.',
    summary='Stash, clean, tags and semantic versions, .gitignore patterns and traps, line endings and Git LFS.',
    keywords=['git stash', 'git tag', 'semver', 'gitignore', 'check-ignore', 'gitattributes', 'line endings', 'git lfs'],
    recap='<p>Stash parks work, tags mark releases, .gitignore keeps untracked junk out, and .gitattributes keeps line endings and big files sane.</p>')
