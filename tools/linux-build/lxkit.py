"""Boxes the Unix and Linux topic files use, on top of tools/cv-build/cvkit.py.

    run(title, script, note='', root=False, keep=False, cwd='~')
        Commands that are run for real in bash on Linux while the page is built, as the user learner in
        /home/learner, which holds the same starting files as the practice shell (LXSH.SEED in assets/lxshell.js).
        The page shows each command with its real output. A command may span several lines (a loop, a here
        document): lines are joined until bash -n says the command is complete. Lines that start with # are shown
        as comments. keep=True keeps the files left by the previous run() instead of starting fresh, so a lesson can
        build up step by step. root=True runs the commands as root (shown with a # prompt).
    sample(title, script, out, note='')
        A command whose output cannot be produced in the build machine (it needs real disks, systemd, a network or
        many users). The box says that the output is a typical example and yours will differ.
    lab(title, missions, files=None, dirs=None, cwd=None, exec_scripts=False)
        The practice shell (assets/lxshell.js) with missions. missions are (text, hint, [conditions]).
        The build runs every hint in the practice shell with node and stops if a hint does not complete its mission.
    play(name, **cfg)
        A playful step animation from assets/lxwidgets.js. cfg gives starting values for its inputs.
    talk(text)
        The background voice talk of a lesson (hidden, read first by "Listen to this lesson").

Prose rules of the CV builder apply: no em dashes, en dashes, semicolons or emojis in prose, and no backslashes
outside <pre> and <code>.
"""
import html as _h
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
USER, HOME = 'learner', '/home/learner'
STAMP = '2026-11-23 09:30:00'
LABS = []          # every lab of the chapter being loaded, checked by build.py
_seed = None


def _esc(s):
    return _h.escape(s, quote=False)


def talk(text):
    return f'<div class="vt-talk" hidden>{text}</div>'


def play(name, **cfg):
    c = f' data-cfg="{_h.escape(json.dumps(cfg, ensure_ascii=False))}"' if cfg else ''
    return f'<div class="viz" data-viz="pk" data-pk="{name}"{c}></div>'


# ---------- the real shell ----------
def seed():
    """The starting files of the practice shell, read from assets/lxshell.js so both always match."""
    global _seed
    if _seed is None:
        js = os.path.join(ROOT, 'assets', 'lxshell.js')
        out = subprocess.run(['node', '-e', f'const L=require({json.dumps(js)});console.log(JSON.stringify(L.SEED))'],
                             capture_output=True, text=True, check=True).stdout
        _seed = json.loads(out)
    return _seed


def _ensure_user():
    """The build user learner gets uid and gid 1000 and the sudo group, as in the practice shell, so that id and
    ls -n show the same numbers. On a cloud image where uid 1000 belongs to the default user (ubuntu), that user is
    moved to 2999 first. This only changes the build machine."""
    if subprocess.run(['id', USER], capture_output=True).returncode:
        subprocess.run(['useradd', '-m', '-s', '/bin/bash', USER], check=True)
    uid = subprocess.run(['id', '-u', USER], capture_output=True, text=True).stdout.strip()
    if uid != '1000':
        other = subprocess.run(['getent', 'passwd', '1000'], capture_output=True, text=True).stdout.split(':')[0]
        if other and other != USER:
            subprocess.run(['usermod', '-u', '2999', other], check=True)
            subprocess.run(['groupmod', '-g', '2999', other], check=False)
        subprocess.run(['usermod', '-u', '1000', USER], check=True)
        subprocess.run(['groupmod', '-g', '1000', USER], check=True)
    subprocess.run(['usermod', '-aG', 'sudo', USER], check=False, capture_output=True)


def reset_home():
    _ensure_user()
    if os.path.isdir(HOME):
        for n in os.listdir(HOME):
            p = os.path.join(HOME, n)
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
    else:
        os.makedirs(HOME)
    S = seed()
    for p, mode, owner in S['dirs']:
        if p.startswith(HOME + '/'):
            os.makedirs(p, exist_ok=True)
            os.chmod(p, mode)
    for row in S['files']:
        p, content, mode = row[0], row[1], row[2]
        if p.startswith(HOME + '/'):
            open(p, 'w', encoding='utf-8').write(content)
            os.chmod(p, mode)
    os.symlink('logs/app.log', os.path.join(HOME, 'latest.log'))
    os.chmod(HOME, 0o750)
    subprocess.run(['chown', '-R', '-h', f'{USER}:{USER}', HOME], check=True)
    subprocess.run(['find', HOME, '-exec', 'touch', '-h', '-d', STAMP, '{}', '+'], check=True)


def _complete(text):
    r = subprocess.run(['bash', '-n'], input=text + '\n', capture_output=True, text=True)
    return r.returncode == 0 and 'here-document' not in r.stderr


def split_cmds(script):
    """Group the lines of a script into whole commands, using bash's own parser."""
    out, cur = [], []
    for line in script.strip('\n').split('\n'):
        if not cur and (line.startswith('#') or not line.strip()):
            out.append(('#', line))
            continue
        cur.append(line)
        if _complete('\n'.join(cur)):
            out.append(('$', '\n'.join(cur)))
            cur = []
    if cur:
        raise SystemExit('run(): this command is not complete:\n' + '\n'.join(cur))
    return out


def execute(script, root=False, keep=False, cwd='~'):
    """Run the commands, return [(kind, command, output)]."""
    if not keep:
        reset_home()
    parts = split_cmds(script)
    body = ['exec 2>&1', "__m() { printf '\\036%s\\n' \"$1\"; }", "HISTIGNORE='__m *'", f'cd {cwd}']
    for k, (kind, c) in enumerate(parts):
        if kind == '$':
            body.append(f'__m {k}')
            body.append(c)
    body.append('__m end')
    with tempfile.NamedTemporaryFile('w', suffix='.sh', delete=False, dir='/tmp') as f:
        f.write('\n'.join(body) + '\n')
        path = f.name
    os.chmod(path, 0o755)
    env = ['env', '-i', f'HOME={"/root" if root else HOME}', f'USER={"root" if root else USER}', f'LOGNAME={"root" if root else USER}',
           'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LANG=C.UTF-8', 'TZ=UTC', 'TERM=dumb', 'SHELL=/bin/bash']
    cmd = env + ['bash', '--noprofile', '--norc', path]
    if not root:
        cmd = ['runuser', '-u', USER, '--'] + cmd
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=HOME if not root else '/root')
    finally:
        os.remove(path)
    chunks, cur, buf = {}, None, []
    for line in r.stdout.split('\n'):
        if line.startswith('\x1e'):
            if cur is not None:
                chunks[cur] = '\n'.join(buf)
            cur, buf = line[1:], []
        else:
            buf.append(line)
    if cur != 'end':
        raise SystemExit(f'run(): the script stopped early, last output:\n{r.stdout[-800:]}')
    # bash names the script file in its own error messages, an interactive shell says bash instead
    chunks = {k: re.sub(r'(?m)^' + re.escape(path) + r': line \d+: ', 'bash: ', v) for k, v in chunks.items()}
    res = []
    for k, (kind, c) in enumerate(parts):
        res.append((kind, c, chunks.get(str(k), '').rstrip('\n') if kind == '$' else ''))
    return res


def _box(title, rows, note, real, root=False):
    body = []
    for kind, c, o in rows:
        if kind == '#':
            body.append(f'<span class="lx-cmt">{_esc(c)}</span>')
            continue
        body.append(f'<span class="lx-cmd{" lx-root" if root else ""}">{_esc(c)}</span>')
        if o:
            body.append(f'<span class="lx-o">{_esc(o)}</span>')
    tag = 'Run for real on Linux while this page was built' if real else 'Typical output, yours will differ'
    n = f'<div class="lx-note">{note}</div>' if note else ''
    return (f'<div class="lx-run"><div class="lx-rh"><span>{_esc(title)}</span><span class="lx-real">{tag}</span>'
            f'<button type="button" class="lx-copy">Copy</button></div><pre>{chr(10).join(body)}</pre>{n}</div>')


def run(title, script, note='', root=False, keep=False, cwd='~'):
    return _box(title, execute(script, root, keep, cwd), note, True, root)


def sample(title, script, out='', note='', root=False):
    rows = [('#', l, '') if l.startswith('#') else ('$', l, '') for l in script.strip('\n').split('\n')]
    if out:
        rows[-1] = (rows[-1][0], rows[-1][1], out.strip('\n'))
    return _box(title, rows, note, False, root)


def lab(title, missions, files=None, dirs=None, cwd=None, exec_scripts=False):
    d = {'title': title, 'missions': [{'t': t, 'hint': h, 'check': c} for t, h, c in missions]}
    if files:
        d['files'] = files
    if dirs:
        d['dirs'] = dirs
    if cwd:
        d['cwd'] = cwd
    if exec_scripts:
        d['exec'] = True
    LABS.append(d)
    return f'<div class="lx-term" data-lab="{_h.escape(json.dumps(d, ensure_ascii=False))}"></div>'


def cmdtable(rows, head=('Command', 'What it does', 'Example')):
    """A table of commands. Each row is (command, meaning, example). Commands and examples are shown as code."""
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join(f'<tr><td><code>{_esc(a)}</code></td><td>{m}</td><td><code>{_esc(e)}</code></td></tr>' for a, m, e in rows)
    return f'<div class="tw"><table class="cvt lx-ct"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
