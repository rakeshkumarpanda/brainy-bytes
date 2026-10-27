"""Helpers the Playwright topic files use to describe a chapter. See build.py for how a chapter becomes a page.

A chapter shows most examples in four languages. Each language is a small real project that the build runs
against Brainy Shop (app/server.mjs) and records:

    four('Sign in and check the greeting',
         java=jv({'LoginTest.java': JAVA_CODE}),
         py=py({'test_login.py': PY_CODE}),
         js=js({'login.spec.js': JS_CODE}),
         ts=ts({'login.spec.ts': TS_CODE}))

Test files go into the usual folder for their language (src/test/java/com/brainy, tests/). Code always uses
http://localhost:4173. The build gives every run its own port and its own fresh copy of the shop, then writes
4173 back into the output, so runs never disturb each other.
"""
import json

LANGS4 = ['java', 'py', 'js', 'ts']
APP = 'http://localhost:4173'


def part(id, emoji, title, html, easy=False, kw=None):
    """One part of a chapter. easy=True keeps it on the beginner path."""
    return {'id': id, 'emoji': emoji, 'title': title, 'html': html, 'easy': easy, 'kw': kw or []}


def say(id, h, en, hi, kn, od, ar, de):
    """Narration for one part in the six narrator languages."""
    return {'id': id, 'h': h, 'en': en, 'hi': hi, 'kn': kn, 'or': od, 'ar': ar, 'de': de}


def quiz(lv, q, o, a, hint, why, code=None):
    d = {'lv': lv, 'q': q, 'o': o, 'a': a, 'hint': hint, 'why': why}
    if code:
        d['code'] = code.strip('\n')
    return d


def calc(lv, q, ans, hint, steps, alt=None):
    d = {'lv': lv, 'q': q, 'ans': ans, 'hint': hint, 'steps': steps}
    if alt:
        d['alt'] = alt
    return d


def panel(scene, h, t, more):
    return {'s': scene, 'h': h, 't': t, 'more': more}


# ---------- project templates for each language ----------
def pom(kind='junit', extra_deps='', extra_build=''):
    """A Maven pom.xml. kind is junit (JUnit 5 with Playwright's @UsePlaywright) or testng."""
    runner = ('''    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>5.13.4</version>
      <scope>test</scope>
    </dependency>''' if kind == 'junit' else '''    <dependency>
      <groupId>org.testng</groupId>
      <artifactId>testng</artifactId>
      <version>7.11.0</version>
      <scope>test</scope>
    </dependency>''')
    return f'''<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.brainy</groupId>
  <artifactId>shop-tests</artifactId>
  <version>1.0.0</version>

  <properties>
    <maven.compiler.release>21</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <dependencies>
    <dependency>
      <groupId>com.microsoft.playwright</groupId>
      <artifactId>playwright</artifactId>
      <version>1.63.0</version>
    </dependency>
{runner}{extra_deps}
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.5.4</version>{extra_build}
      </plugin>
    </plugins>
  </build>
</project>'''


SHOP_OPTIONS = '''package com.brainy;

import com.microsoft.playwright.junit.Options;
import com.microsoft.playwright.junit.OptionsFactory;

// Shared settings for every test class that says @UsePlaywright(ShopOptions.class)
public class ShopOptions implements OptionsFactory {
  @Override
  public Options getOptions() {
    return new Options()
        .setHeadless(true)
        .setBaseUrl("http://localhost:4173");
  }
}'''

PW_CONFIG_JS = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  reporter: 'list',
  use: { baseURL: 'http://localhost:4173' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});'''

PYTEST_INI = '''[pytest]
addopts = --base-url http://localhost:4173'''

TSCONFIG = json.dumps({'compilerOptions': {'target': 'ES2022', 'module': 'ESNext', 'moduleResolution': 'Bundler', 'strict': True,
                                           'noEmit': True, 'skipLibCheck': True, 'types': ['node']}}, indent=2)


def _files(name_or_files, code, folder):
    if isinstance(name_or_files, dict):
        return {(k if '/' in k or k.startswith(('pom', 'playwright', 'pytest', 'conftest', 'package', 'tsconfig', 'testng', '.env', 'requirements')) else folder + k): v
                for k, v in name_or_files.items()}
    return {folder + name_or_files: code}


def js(files, code=None, config=PW_CONFIG_JS, cmd='npx playwright test', show=None, expect='pass', replace=None, more=None,
       shown_cmd=None, note=None, tail=None):
    """A JavaScript Playwright Test project. files is {'name.spec.js': code} or a name plus code."""
    f = _files(files, code, 'tests/' if 'playwright test' in cmd else '')
    allf = {'package.json': json.dumps({'name': 'shop-tests', 'private': True, 'type': 'module'}, indent=2),
            **({'playwright.config.js': config} if config else {}), **f, **(more or {})}
    return {'lang': 'js', 'files': allf, 'cmd': cmd, 'shown_cmd': shown_cmd or cmd, 'show': show or list(f), 'expect': expect,
            'replace': replace or [], 'note': note, 'tail': tail}


def ts(files, code=None, config=None, cmd='npx playwright test', show=None, expect='pass', replace=None, more=None,
       shown_cmd=None, note=None, typecheck=True, tail=None):
    """A TypeScript Playwright Test project. tsc checks the types first, so a type mistake fails the build."""
    f = _files(files, code, 'tests/' if 'playwright test' in cmd else '')
    allf = {'package.json': json.dumps({'name': 'shop-tests', 'private': True, 'type': 'module'}, indent=2),
            'tsconfig.json': TSCONFIG, 'playwright.config.ts': config or PW_CONFIG_JS, **f, **(more or {})}
    run = ('npx tsc -p . && ' if typecheck else '') + cmd
    return {'lang': 'ts', 'files': allf, 'cmd': run, 'shown_cmd': shown_cmd or cmd, 'show': show or list(f), 'expect': expect,
            'replace': replace or [], 'note': note, 'typecheck': typecheck, 'tail': tail}


def py(files, code=None, ini=PYTEST_INI, cmd='pytest -v', show=None, expect='pass', replace=None, more=None, shown_cmd=None,
       note=None, tail=None):
    """A Python project run with pytest and the pytest-playwright plugin, or a plain script when cmd says python."""
    f = _files(files, code, 'tests/' if 'pytest' in cmd else '')
    allf = {**({'pytest.ini': ini} if ini else {}), **f, **(more or {})}
    return {'lang': 'py', 'files': allf, 'cmd': cmd, 'shown_cmd': shown_cmd or cmd, 'show': show or list(f), 'expect': expect,
            'replace': replace or [], 'note': note, 'tail': tail}


def jv(files, code=None, kind='junit', cmd='mvn test', show=None, expect='pass', replace=None, more=None, shown_cmd=None,
       note=None, options=True, pom_xml=None, tail=None):
    """A Maven project with Playwright for Java. kind='junit' adds ShopOptions for @UsePlaywright(ShopOptions.class)."""
    f = _files(files, code, 'src/test/java/com/brainy/')
    allf = {'pom.xml': pom_xml or pom(kind), **f, **(more or {})}
    if kind == 'junit' and options and 'src/test/java/com/brainy/ShopOptions.java' not in allf:
        allf['src/test/java/com/brainy/ShopOptions.java'] = SHOP_OPTIONS
    return {'lang': 'java', 'files': allf, 'cmd': cmd, 'shown_cmd': shown_cmd or cmd, 'show': show or list(f), 'expect': expect,
            'replace': replace or [], 'note': note, 'tail': tail}


def shown(files, lang, cmd='', result=None, note='Shown, not run here'):
    """Code that is shown but not run, such as CI files or features that need another browser build."""
    if isinstance(files, str):
        files = {'': files}
    return {'lang': lang, 'files': files, 'cmd': None, 'shown_cmd': cmd, 'show': list(files), 'result': result, 'note': note, 'shown': True}


def four(label, java=None, py=None, js=None, ts=None, result=None):
    """One example in up to four languages. The reader's chosen language is shown first."""
    langs = {k: v for k, v in (('java', java), ('py', py), ('js', js), ('ts', ts)) if v}
    return {'t': 'four', 'label': label, 'langs': langs, 'result': result}


def one(label, spec, result=None):
    """An example that only exists in one language, or a file such as a CI workflow."""
    return {'t': 'four', 'label': label, 'langs': {spec['lang']: spec}, 'result': result, 'single': True}


def step(caption, js, py, java, ts=None, shot=True):
    """One line of a recorded walk. js runs for real, the screenshot is taken after it."""
    return {'cap': caption, 'js': js, 'ts': ts or js, 'py': py, 'java': java, 'shot': shot}


def walk(title, steps, start='', size=(900, 520), sub=None):
    """A line by line run that is recorded with a screenshot after every step."""
    return {'t': 'walk', 'title': title, 'steps': steps, 'start': start, 'size': size, 'sub': sub}


# ---------- small HTML boxes the lessons share ----------
def table(head, rows, cls=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table class="jt {cls}"><tr>{h}</tr>{b}</table></div>'


def tip(text, kind='tip'):
    icon = {'tip': '💡', 'warn': '⚠️', 'life': '🌍', 'kid': '🧒', 'pro': '🏢', 'new': '🆕'}[kind]
    return f'<div class="pw-box pw-{kind}"><span class="pw-ic">{icon}</span><div>{text}</div></div>'


def by(java=None, py=None, js=None, ts=None):
    """Text that only shows for the reader's chosen language. js text is used for ts when ts is not given."""
    out = []
    for k, v in (('java', java), ('py', py), ('js', js), ('ts', ts if ts is not None else js)):
        if v:
            out.append(f'<span class="only-{k}">{v}</span>')
    return ''.join(out)


def viz(name, **data):
    import html as _h
    attrs = ''.join(f' data-{k}="{_h.escape(str(v))}"' for k, v in data.items())
    return f'<div class="viz" data-viz="{name}"{attrs}></div>'


def figure(src, alt, cap):
    """A real screenshot from content/playwright/img/ with a caption."""
    import html as _h
    return f'<figure class="pw-shot"><img src="img/{src}" alt="{_h.escape(alt)}" loading="lazy"><figcaption>{cap}</figcaption></figure>'


def real_file(path):
    """Read a file that a real tool wrote (see screens/), so the page shows it exactly."""
    import os
    return open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screens', 'out', path), encoding='utf-8').read().rstrip('\n')
