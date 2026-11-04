"""Build the Git and CI/CD chapter pages in content/git/ from the topic files in topics/.

The pages use the same layout, checks and tabs as the Computer Vision and NLP subjects, so this file only changes the
settings in tools/cv-build/build.py and runs it. Topic files use the same kit (tools/cv-build/cvkit.py) plus gitkit.py
(terminal blocks, files with line notes, Dev and QA views, baby steps). The animations live in assets/gitwidgets.js on
top of the framework in assets/cvviz.js.

The formula cards of other subjects hold commands here, so the Formulas tab is called Commands (CFG fx_word).

The sample project in starter/ is the one the GitHub Actions and GitLab CI chapters build from scratch. Its pipelines
were checked with actionlint and the GitLab CI schema, and its commands were run for real. The build copies it to
content/git/starter/ and zips it as content/git/calc-app-starter.zip so readers can download it.

Usage:  python3 tools/git-build/build.py [--fast] [slug ...]      (no slug builds every chapter, --fast skips the cheatsheet)
The Interview Questions page is built by:  python3 tools/interview-build/build.py git
"""
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
import build as B  # noqa: E402

sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder

B.CFG.update({
    'subject': 'git', 'name': 'Git and CI/CD', 'topics': os.path.join(HERE, 'topics'),
    'func': 'gitModules', 'marker': 'git-build', 'builder': 'tools/git-build/build.py', 'badge': 'GIT',
    'widgets': ['cvviz.js', 'gitwidgets.js'], 'css': ['cv.css', 'git.css'], 'body': 'cvp gitp',
    'min_calc': 6, 'min_assign': 0, 'fx_word': ('Command', 'Commands', 'command card'),
})

WORDS = [('Every formula,', 'Every command,'), ('every formula,', 'every command,'), ('>Formulas<', '>Commands<'),
         (' formulas</span>', ' command cards</span>'), ('exam favourite formulas', 'exam favourite commands'),
         ('Exam favourite formulas only', 'Exam favourite commands only'), ('Find a formula,', 'Find a command,'),
         ('every formula, table', 'every command, table')]


def relabel(fn):
    def wrapped(*a, **k):
        s = fn(*a, **k)
        for x, y in WORDS:
            s = s.replace(x, y)
        return s
    return wrapped


def starter():
    """Copy the sample project next to the pages and zip it for download."""
    src = os.path.join(HERE, 'starter')
    dst = os.path.join(B.out_dir(), 'starter')
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '.venv', 'dist', 'reports', '.pytest_cache'))
    z = os.path.join(B.out_dir(), 'calc-app-starter.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as f:
        for root, dirs, files in os.walk(dst):
            dirs.sort()
            for n in sorted(files):
                p = os.path.join(root, n)
                info = zipfile.ZipInfo('calc-app/' + os.path.relpath(p, dst).replace(os.sep, '/'), (2026, 11, 2, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                f.writestr(info, open(p, 'rb').read())
    print(f'starter project: content/git/starter/ and content/git/calc-app-starter.zip ({os.path.getsize(z)} bytes)')


if __name__ == '__main__':
    fast = '--fast' in sys.argv     # pages and catalog only, no starter copy and no cheatsheet PDFs
    chs = B.build([a for a in sys.argv[1:] if a != '--fast'])
    if fast:
        sys.exit(0)
    starter()
    import cheatsheet
    cheatsheet.KINDS = [('must', 'Key ideas'), ('fx', 'Commands'), ('table', 'Tables'), ('tip', 'Remember'),
                        ('warn', 'Common mistakes'), ('exam', 'In the exam')]
    cheatsheet.page = relabel(cheatsheet.page)
    cheatsheet.compact_page = relabel(cheatsheet.compact_page)
    cheatsheet.write(chs, B.CFG, B.ROOT)
