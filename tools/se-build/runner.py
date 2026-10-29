"""Run one Selenium example for real, in Java, Python or JavaScript, and return what it printed.

The topic files call sekit.tri(...), which calls run() here. A result is saved in runs.json, keyed by the language,
the mode, the files and RUN_STAMP, so a page can be rebuilt without a browser. A missing result is only run when the
environment variable SE_RUN=1 is set, otherwise the build stops and says which example needs a run.

Modes
  script   py: python main.py    js: node main.js    java: java Main.java (single file source launch)
  pytest   py: pytest -q          (the main file is test_example.py)
  mocha    js: mocha main.spec.js
  junit    java: javac every file, then the JUnit 5 console launcher on the class named in the main file
needs='grid' starts a Selenium Grid standalone server on http://localhost:4444 before the example runs.

Set up the tools once with tools/se-build/setup.sh.
"""
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BOX = os.path.join(HERE, 'box')
CACHE = os.path.join(HERE, 'runs.json')
RUN_STAMP = 'se-4.51.0-chrome-153'
VERSIONS = 'Selenium 4.51.0 with Chrome 153'
_cache = None
_procs = []
USED = set()


def cache():
    global _cache
    if _cache is None:
        _cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    return _cache


def save():
    if _cache is not None:
        json.dump(dict(sorted(_cache.items())), open(CACHE, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        open(CACHE, 'a').write('\n')


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(('127.0.0.1', port)) == 0


def env(lang='java'):
    # Python and JavaScript find box/chromedriver on PATH through Selenium Manager. Only Java gets SE_CHROMEDRIVER,
    # because in Python that variable would override a driver path an example gives on purpose to its Service.
    e = {k: v for k, v in os.environ.items() if k not in ('JAVA_TOOL_OPTIONS', 'SE_CHROMEDRIVER')}
    e.update(DISPLAY=':99', SE_OFFLINE='true', SE_AVOID_STATS='true',
             NODE_PATH=os.path.join(BOX, 'node', 'node_modules'), PYTHONDONTWRITEBYTECODE='1')
    if lang == 'java':
        e['SE_CHROMEDRIVER'] = os.path.join(BOX, 'chromedriver')
    e['PATH'] = BOX + os.pathsep + e.get('PATH', '')
    return e


def start_services(grid=False):
    if not os.path.exists(os.path.join(BOX, 'chromedriver')):
        raise SystemExit('the Selenium tools are not set up. Run tools/se-build/setup.sh first')
    if not os.path.exists('/tmp/.X11-unix/X99'):
        _procs.append(subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1366x900x24'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(1)
    if not port_open(8443):
        _procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, 'siteserver.py')]))
        for _ in range(50):
            if port_open(8443):
                break
            time.sleep(0.1)
    if grid and not port_open(4444):
        log = open(os.path.join(BOX, 'grid.log'), 'w')
        _procs.append(subprocess.Popen(['java', '-cp', os.path.join(BOX, 'java', 'lib', '*'), 'org.openqa.selenium.grid.Main', 'standalone',
                                        '--port', '4444', '--max-sessions', '2'], env=env(), stdout=log, stderr=subprocess.STDOUT))
        for _ in range(120):
            if port_open(4444):
                break
            time.sleep(0.25)
        time.sleep(3)


def stop_services():
    for p in _procs:
        p.terminate()
    _procs.clear()


def key(lang, mode, files, needs):
    return hashlib.sha256(json.dumps([lang, mode, files, needs, RUN_STAMP], sort_keys=True).encode()).hexdigest()[:24]


def clean(out, d):
    out = out.replace(d + '/', '').replace(d, '.')
    out = re.sub(r'Picked up JAVA_TOOL_OPTIONS[^\n]*\n', '', out)
    return out.rstrip()


def _exec(lang, mode, files, d):
    e = env(lang)
    main = next(iter(files))
    if lang == 'py':
        py = os.path.join(BOX, '.venv', 'bin', 'python')
        cmd = [py, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', main] if mode == 'pytest' else [py, main]
    elif lang == 'js':
        cmd = [os.path.join(BOX, 'node', 'node_modules', '.bin', 'mocha'), '--timeout', '60000', main] if mode == 'mocha' else ['node', main]
    else:
        cp = os.path.join(BOX, 'java', 'lib', '*')
        if mode == 'junit':
            r = subprocess.run(['javac', '-cp', cp, '-d', 'classes', *files], cwd=d, capture_output=True, text=True, env=e)
            if r.returncode:
                raise SystemExit(f'javac failed:\n{r.stdout}{r.stderr}')
            cls = re.search(r'class\s+(\w+)', files[main]).group(1)
            pkg = re.search(r'^package\s+([\w.]+);', files[main], re.M)
            cls = (pkg.group(1) + '.' if pkg else '') + cls
            jar = os.path.join(BOX, 'java', 'lib', 'junit-platform-console-standalone-1.11.4.jar')
            cmd = ['java', '-jar', jar, 'execute', '--class-path', 'classes' + os.pathsep + cp, '--select-class', cls,
                   '--disable-banner', '--details=tree', '--disable-ansi-colors']
        elif len(files) > 1:
            r = subprocess.run(['javac', '-cp', cp, '-d', 'classes', *files], cwd=d, capture_output=True, text=True, env=e)
            if r.returncode:
                raise SystemExit(f'javac failed:\n{r.stdout}{r.stderr}')
            cls = re.search(r'class\s+(\w+)', files[main]).group(1)
            pkg = re.search(r'^package\s+([\w.]+);', files[main], re.M)
            cmd = ['java', '-cp', 'classes' + os.pathsep + cp, (pkg.group(1) + '.' if pkg else '') + cls]
        else:
            cmd = ['java', '-cp', cp, main]
    # Output goes to files, not pipes, so a browser left running cannot hold the run open. The example runs in its
    # own process group, and anything it leaves behind (a driver or a browser) is stopped afterwards.
    with open(os.path.join(d, '.out'), 'w+') as fo, open(os.path.join(d, '.err'), 'w+') as fe:
        p = subprocess.Popen(cmd, cwd=d, stdout=fo, stderr=fe, text=True, env=e, start_new_session=True)
        try:
            rc = p.wait(timeout=240)
        except subprocess.TimeoutExpired:
            rc = 'timeout'
        try:
            os.killpg(p.pid, 15)
        except ProcessLookupError:
            pass
        fo.seek(0)
        fe.seek(0)
        so, se = fo.read(), fe.read()
    if rc == 'timeout':
        raise SystemExit(f'{lang} run timed out after 240 s:\n{so}\n{se}')
    out = so + (('\n' if so and se else '') + se if rc or lang == 'js' and se else '')
    return clean(out, d), rc


def run(lang, files, mode='script', needs=None, label=''):
    """files: {path: source}, the first one is the main file. Returns (output, exit code)."""
    k = key(lang, mode, files, needs)
    USED.add(k)
    c = cache()
    if k in c:
        return c[k]['out'], c[k]['rc']
    if os.environ.get('SE_RUN') != '1':
        raise SystemExit(f'example {label} ({lang}) has not been run yet. Set SE_RUN=1 to run it (needs setup.sh)')
    start_services(grid=needs == 'grid')
    d = tempfile.mkdtemp(prefix='se-')
    try:
        for p, s in files.items():
            os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
            open(os.path.join(d, p), 'w', encoding='utf-8').write(s + '\n')
        t = time.time()
        out, rc = _exec(lang, mode, files, d)
        print(f'  ran {label} {lang} in {time.time() - t:.1f}s, exit {rc}', file=sys.stderr)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    c[k] = {'label': label, 'lang': lang, 'out': out, 'rc': rc}
    save()
    return out, rc
