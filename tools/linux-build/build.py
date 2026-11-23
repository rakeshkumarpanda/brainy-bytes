"""Build the Unix and Linux subject (content/linux/) from the topic files in this folder.

The subject has five sections. Each one is a tab on the learning path (the 'parts' of the subject in data/catalog.js),
split into steps, so the path reads Section, then Step, then Chapter:
  Foundations           basics-topics/     what Unix and Linux are, the terminal and the shell, help, the file tree,
                                           files and folders, reading files, permissions, editors
  Shell Power Tools     power-topics/      redirection and pipes, grep and regular expressions, text tools, sed and
                                           awk, finding files, processes and signals, the environment, archives
  Shell Scripting       script-topics/     first scripts, expansions, conditions and loops, functions and robust
                                           scripts, scheduling
  System Administration admin-topics/      users and sudo, packages, boot and systemd, disks and filesystems, logs
                                           and monitoring, networking, SSH, firewalls and hardening
  Internals and Advanced adv-topics/       the kernel and system calls, processes inside, files inside, memory,
                                           containers under the hood, performance, exam revision

The pages use the layout, checks and tabs of tools/cv-build/build.py, so this file changes its settings and runs it
once per section. Topic files use tools/cv-build/cvkit.py and lxkit.py in this folder:
  lxkit.run()     commands run for real in bash as the user learner while the page is built (needs Linux and root,
                  because the build makes the user learner with uid 1000)
  lxkit.lab()     the practice shell (assets/lxshell.js) with missions. Every mission hint is run in the practice
                  shell with node, and the build stops if a hint does not complete its mission
  lxkit.play()    playful step animations (assets/lxwidgets.js on assets/playkit.js and assets/viz.js)
  lxkit.talk()    the background voice talk of each lesson, read by assets/voiceteach.js

After writing the pages it adds the Material 3 layer (tools/md3-build/inject.py).

Usage:  sudo python3 tools/linux-build/build.py [--part basics|power|scripting|admin|advanced] [--fast] [slug ...]
--fast skips the cheatsheets. The search index:  node tools/search-build/build.js linux
The Interview Questions page:  python3 tools/interview-build/build.py linux
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(TOOLS, 'cv-build'))
import build as B  # noqa: E402

sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder
import lxkit  # noqa: E402

WIDGETS = ['cvviz.js', 'viz.js', 'playkit.js', 'lxwidgets.js', 'lxshell.js']
BASE = {'builder': 'tools/linux-build/build.py', 'css': ['cv.css', 'viz.css', 'playkit.css', 'linux.css'],
        'body': 'cvp lxp', 'widgets': WIDGETS, 'subject': 'linux', 'badge': 'LX', 'name': 'Unix and Linux',
        'min_calc': 6, 'min_assign': 0, 'fx_word': ('Command', 'Commands', 'command card')}
PARTS = [
    {'part': 'basics', 'part_name': 'Foundations', 'topics': 'basics-topics', 'func': 'lxBasicsModules'},
    {'part': 'power', 'part_name': 'Shell Power Tools', 'topics': 'power-topics', 'func': 'lxPowerModules'},
    {'part': 'scripting', 'part_name': 'Shell Scripting', 'topics': 'script-topics', 'func': 'lxScriptModules'},
    {'part': 'admin', 'part_name': 'System Administration', 'topics': 'admin-topics', 'func': 'lxAdminModules'},
    {'part': 'advanced', 'part_name': 'Internals and Advanced', 'topics': 'adv-topics', 'func': 'lxAdvModules'},
]
COMPACT_MAX = 12
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


def pk_names():
    src = open(os.path.join(B.ROOT, 'assets', 'lxwidgets.js'), encoding='utf-8').read()
    return set(re.findall(r"def\('([\w-]+)'", src))


_viz_names = B.viz_names
B.viz_names = lambda: _viz_names() | {'pk'}


def check_extra(chs):
    """Playful animation names exist, and every practice shell mission can be done with its own hint."""
    known, bad = pk_names(), []
    for T in chs:
        allhtml = ''.join(p['html'] for p in T['lessons'])
        for n in set(re.findall(r'data-pk="([^"]+)"', allhtml)) - known:
            bad.append(f'{T["slug"]}: playful animation {n} is not defined in assets/lxwidgets.js')
        for p in T['lessons']:
            if 'class="vt-talk"' not in p['html']:
                bad.append(f'{T["slug"]}: lesson {p["id"]} has no talk()')
    labs = [(T['slug'], L) for T in chs for L in T.get('labs', [])]
    if labs:
        import json
        r = subprocess.run(['node', os.path.join(HERE, 'checklab.js')], input=json.dumps(labs), capture_output=True, text=True)
        if r.returncode:
            bad.append(r.stdout + r.stderr)
    if bad:
        raise SystemExit('\n'.join(bad))


def drop_placeholder(fn):
    path = os.path.join(B.ROOT, 'data', 'catalog.js')
    text = open(path, encoding='utf-8').read()
    stub = ('\n/* placeholder until the first chapter of this section is built by tools/linux-build/build.py */\n'
            f'function {fn}() {{ return []; }}\n')
    if stub in text:
        open(path, 'w', encoding='utf-8').write(text.replace(stub, ''))


def load_part():
    """Like B.chapters, but records the labs of each topic file on its chapter."""
    if B.HERE not in sys.path:
        sys.path.insert(0, B.HERE)
    import cheatsheet
    import importlib.util
    cheatsheet.record()
    out = []
    for f in sorted(f for f in os.listdir(B.CFG['topics']) if re.match(r'\d\d[a-z]?-.*\.py$', f)):
        spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(B.CFG['topics'], f))
        m = importlib.util.module_from_spec(spec)
        cheatsheet.begin()
        lxkit.LABS.clear()
        spec.loader.exec_module(m)
        T = m.T
        T['sheet'] = cheatsheet.take()
        T['file'] = f[:-3]
        T['labs'] = list(lxkit.LABS)
        out.append(T)
    return out


B.chapters = load_part


def main():
    args = sys.argv[1:]
    only, fast = None, False
    if '--fast' in args:
        fast = True
        args.remove('--fast')
    if args[:1] == ['--part']:
        only, args = args[1], args[2:]
    every, written = [], []
    for P in PARTS:
        folder = os.path.join(HERE, P['topics'])
        if not os.path.isdir(folder) or not [f for f in os.listdir(folder) if f.endswith('.py')]:
            continue
        B.CFG.clear()
        B.CFG.update(BASE)
        B.CFG.update(P, topics=folder, marker='lx-' + P['part'] + '-build')
        if (only and P['part'] != only) or (args and not any(a in ' '.join(os.listdir(folder)) for a in args)):
            chs = B.chapters()
            for T in chs:
                T['part'], T['part_name'] = P['part'], P['part_name']
        else:
            drop_placeholder(P['func'])
            loaded = load_part()
            check_extra(loaded)
            B.chapters = lambda: loaded      # B.build loads the chapters again otherwise, and runs every command twice
            try:
                chs = B.build(args)
            finally:
                B.chapters = load_part
            written += [T['slug'] for T in chs if not args or T['slug'] in args]
        every += chs
    if written:
        subprocess.run([sys.executable, os.path.join(TOOLS, 'md3-build', 'inject.py')] +
                       [os.path.join(B.ROOT, 'content', 'linux', s + '.html') for s in written], check=True)
    if fast or not every:
        return
    import cheatsheet
    cheatsheet.KINDS = [('must', 'Key ideas'), ('fx', 'Commands'), ('table', 'Tables'), ('tip', 'Remember'),
                        ('warn', 'Common mistakes'), ('exam', 'In the exam')]
    cheatsheet.page = relabel(cheatsheet.page)
    cheatsheet.compact_page = relabel(cheatsheet.compact_page)
    cheatsheet.write(every, dict(BASE, compact_max=COMPACT_MAX), B.ROOT)


if __name__ == '__main__':
    main()
