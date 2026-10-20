"""Small helpers the topic files use to describe a chapter. See build.py for what each kind of example does."""
import json


def part(id, emoji, title, html, qa=None, kw=None, qa_why=None):
    """One part of a chapter. qa marks it as needed for test automation: True, or a list of tool names."""
    return {'id': id, 'emoji': emoji, 'title': title, 'html': html, 'qa': qa, 'kw': kw or [], 'qa_why': qa_why}


def run(code, label, **kw):
    """Plain JavaScript run with Node.js. file='x.cjs' for CommonJS, play=False when it needs Node only APIs,
    expect='throw' when the example crashes on purpose."""
    return {'t': 'run', 'code': code, 'label': label, **kw}


def dom(page, code, label, **kw):
    """Browser code run against page (HTML) with jsdom at build time and in a sandboxed frame in the browser."""
    return {'t': 'dom', 'html': page, 'code': code, 'label': label, **kw}


def test(files, cmd, label, **kw):
    """A small project run with a real test runner. show lists the files to print (all by default),
    expect='fail' when a test fails on purpose."""
    return {'t': 'test', 'files': files, 'cmd': cmd, 'label': label, **kw}


def show(code, label, lang='js', note='Not run on this page', result=None):
    """Code that is shown but not run here. result is a sentence about what it does."""
    return {'t': 'show', 'code': code, 'label': label, 'lang': lang, 'note': note, 'result': result}


def say(id, h, en, hi, kn, od, ar, de):
    """Narration for one part in the six narrator languages."""
    return {'id': id, 'h': h, 'en': en, 'hi': hi, 'kn': kn, 'or': od, 'ar': ar, 'de': de}


def quiz(lv, q, o, a, hint, why, code=None):
    d = {'lv': lv, 'q': q, 'o': o, 'a': a, 'hint': hint, 'why': why}
    if code:
        d['code'] = code.strip('\n')
    return d


def calc(lv, q, ans, hint, steps, code=None, alt=None):
    d = {'lv': lv, 'q': q, 'ans': ans, 'hint': hint, 'steps': steps}
    if code:
        d['code'] = code.strip('\n')
    if alt:
        d['alt'] = alt
    return d


def ex(id, lv, title, task, starter, tests, solution, hint='', why=''):
    """A hands-on exercise. tests is a list of (expression, expected JSON value)."""
    return {'id': id, 'lv': lv, 'title': title, 'task': task, 'starter': starter.strip('\n'),
            'tests': [{'call': c, 'want': w} for c, w in tests], 'solution': solution.strip('\n'), 'hint': hint, 'why': why}


def panel(scene, h, t, more):
    return {'s': scene, 'h': h, 't': t, 'more': more}


# ---------- shared project files for the test runner examples ----------
def pkg(name='demo', type_=None, scripts=None):
    d = {'name': name, 'version': '1.0.0', 'private': True}
    if type_:
        d['type'] = type_
    if scripts:
        d['scripts'] = scripts
    return json.dumps(d, indent=2)


SELENIUM_DRIVER = r'''
// One place that knows how to start Chrome for every Selenium test.
// Selenium Manager finds a matching chromedriver by itself. CI machines can
// point CHROMEDRIVER and CHROME_BIN at fixed copies instead.
const { Builder } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');

async function buildDriver() {
  const options = new chrome.Options().addArguments('--headless=new', '--no-sandbox', '--window-size=1280,800');
  if (process.env.CHROME_BIN) options.setChromeBinaryPath(process.env.CHROME_BIN);
  const builder = new Builder().forBrowser('chrome').setChromeOptions(options);
  if (process.env.CHROMEDRIVER) builder.setChromeService(new chrome.ServiceBuilder(process.env.CHROMEDRIVER));
  return builder.build();
}

module.exports = { buildDriver };
'''


# ---------- TypeScript examples ----------
TSCONFIG = {
    'compilerOptions': {'target': 'esnext', 'module': 'nodenext', 'strict': True, 'noEmit': True,
                        'allowImportingTsExtensions': True, 'lib': ['esnext', 'dom'], 'types': ['node']},
    'include': ['src'],
}


def ts(code, label, errors=0, run=True, name='main.ts', more=None, options=None, **kw):
    """A TypeScript file checked by tsc with strict settings, then run by Node.js with type stripping.
    errors is how many type errors tsc must report. The build fails if the count is different."""
    cfg = json.loads(json.dumps(TSCONFIG))
    cfg['compilerOptions'].update(options or {})
    files = {'package.json': pkg('ts-demo', 'module'), 'tsconfig.json': json.dumps(cfg, indent=2), f'src/{name}': code, **(more or {})}
    cmd = '(npx tsc -p . --pretty false && echo "tsc: no type errors")' + (f'; echo; echo "$ node src/{name}"; node src/{name}' if run else '')
    shown = 'npx tsc' + (f' && node src/{name}' if run and not errors else (f'\n$ node src/{name}' if run else ''))
    badge = f'🔷 tsc finds {errors} error{"" if errors == 1 else "s"}' if errors else '🔷 tsc passes'
    if run:
        badge += ', then Node.js runs it'
    spec = {'t': 'test', 'files': files, 'cmd': cmd, 'label': label, 'show': [f'src/{name}', *(more or {})], 'shown_cmd': shown,
            'badge': badge, 'ts_errors': errors}
    if errors and not run:
        spec['expect'] = 'fail'
    spec.update(kw)
    return spec
