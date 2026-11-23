"""Build assets/codejourney.js from the animation file Rakesh shared (code_journey_animations_v2.html).

The source is kept split in tools/md3-build/codejourney-src (app.js, style.css, body.html).
Each widget runs inside its own shadow root, so the original ids and class names cannot clash with a chapter page,
and the page's Material colour tokens still reach it (custom properties pass into a shadow root).

Widgets on a page:
  <div class="cj-card" data-cj="journey" data-lang="java"></div>   source code to screen, one language
  <div class="cj-card" data-cj="ci"></div>                          compiler vs interpreter, kitchen and code demo
Languages: java, python, js. C# is left out on purpose (asked 2026-11-23).
Needs assets/vendor/gsap.min.js and assets/vendor/MotionPathPlugin.min.js loaded first.

Run: python3 tools/md3-build/build_codejourney.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'codejourney-src')
OUT = os.path.join(HERE, '..', '..', 'assets', 'codejourney.js')

app = open(os.path.join(SRC, 'app.js'), encoding='utf-8').read()
css = open(os.path.join(SRC, 'style.css'), encoding='utf-8').read()
body = open(os.path.join(SRC, 'body.html'), encoding='utf-8').read()


def cut(s, start, end, repl=''):
    i = s.index(start); j = s.index(end, i)
    return s[:i] + repl + s[j:]


def sub1(s, old, new):
    assert s.count(old) == 1, (s.count(old), old[:70])
    return s.replace(old, new)


# ---------- script ----------
app = sub1(app, 'gsap.registerPlugin(MotionPathPlugin);', '')
app = sub1(app, "const $=s=>document.querySelector(s);", "const $=s=>R.querySelector(s);")
app = app.replace('document.getElementById(', 'R.getElementById(').replace('document.querySelectorAll(', 'R.querySelectorAll(')
app = sub1(app, "gsap.to('#blank',", "gsap.to($('#blank'),")
app = sub1(app, "gsap.fromTo('#nShape',", "gsap.fromTo($('#nShape'),")
app = sub1(app, "gsap.fromTo(['#nWho','#nTitle','#nText'],", "gsap.fromTo([$('#nWho'),$('#nTitle'),$('#nText')],")
# drop C#
app = cut(app, '/* ------------------------------ C# ', '\n};\n', '\n')
app = re.sub(r'\},\s*\n\s*\n\};', '}\n};', app)
# the tab bar, theme and full screen buttons of the original page are not used: the site has its own
app = cut(app, '/* ===================================================================\n   Tabs, theme, full screen, keyboard', "setLang('java');p2.reset();p3.reset();",
          '''/* keyboard: only while this widget has focus, so two widgets on one page do not fight */
host.tabIndex=0;
host.addEventListener('keydown',e=>{
  if(['SELECT','INPUT','BUTTON'].includes((e.composedPath()[0]||{}).tagName)&&e.key!==' ')return;
  const target=mode==='journey'?p1:(R.activeElement&&R.getElementById('c3').contains(R.activeElement)?p3:p2);
  if(e.key===' '){e.preventDefault();target.toggle()}
  else if(e.key==='ArrowRight'){e.preventDefault();target.pause();target.step()}
  else if(e.key==='ArrowLeft'){e.preventDefault();target.pause();target.back()}
  else if(e.key==='r'||e.key==='R'){target.reset()}
});
/* edges are measured from the layout, so draw them again whenever the widget changes size (a lesson opening, full screen) */
if(window.ResizeObserver)new ResizeObserver(()=>{drawEdges(lastEdges,false);[p1,p2,p3].forEach(p=>drawWavy(p.wavy,p.pf.f))}).observe(R.getElementById('stage'));
''')
app = app.replace("setLang('java');p2.reset();p3.reset();", '')
app += "\nsetLang(LANGS[lang]?lang:'java');p2.reset();p3.reset();\n"

# ---------- markup ----------
b = body[body.index('<section class="page on" id="p1">'):body.index('<footer>')]
b = re.sub(r'\s*<button class="chip" data-lang="cs">.*?</button>', '', b)
b = b.replace('Key ideas true for all four languages', 'Key ideas true for every language')
b = b.replace('Java bytecode, Python bytecode, V8 bytecode and .NET CIL are completely different', 'Java bytecode, Python bytecode and V8 bytecode are completely different')
b = b.replace(' Python uses the PVM inside CPython, JavaScript uses an engine such as V8, and C# uses the CLR.', ' Python uses the PVM inside CPython, and JavaScript uses an engine such as V8.')
b = b.replace('Bytecode / IL</span>', 'Bytecode</span>')
b = b.replace('(machine code, or bytecode/IL)', '(machine code or bytecode)')
b = b.replace('<code>Hello.class</code>, <code>Hello.dll</code>)', '<code>Hello.class</code>)')
b = b.replace('javac, Roslyn csc (to bytecode/IL).', 'javac (to Java bytecode).')
b = b.replace('or bytecode (Java, C#).', 'or bytecode (Java).')
b = b.replace(' C#: Roslyn compiles to IL, then the CLR JIT compiles it to machine code.', '')
b = b.replace('<h2 class="sec-title">Part B. The same idea with real code</h2>', '<h2 class="sec-title">Part B. The same idea with real code</h2>\n  <p class="sec-desc">The demo program uses simple Python style lines, because the idea is the same in every language.</p>')
assert 'C#' not in b and 'Roslyn' not in b and 'CLR' not in b, 'C# text left in the markup'
b = b.replace('<div class="dots" data-role="dots" id="dots1"></div>', '<div class="dots" data-role="dots" id="dots1"></div>')

# ---------- styles: the original tokens, mapped onto the site's Material tokens ----------
root = css[css.index(':root{'):css.index('*{box-sizing')]
css = css.replace(root, '')
css = re.sub(r'html,body\{[^}]*\}\s*body\{[^}]*\}\s*', '', css)
css = re.sub(r'\.wrap\{[^}]*\}', '', css)
css = re.sub(r'/\* ---------- Header ---------- \*/.*?/\* ---------- Toolbar', '/* ---------- Toolbar', css, flags=re.S)
css = re.sub(r'footer\{[^}]*\}', '', css)
host = ''':host{display:block;
  --bg:var(--md-surface,#f4f5fb); --surface:var(--md-sc-lowest,#fff); --s1:var(--md-sc-low,#eef0f9); --s2:var(--md-sc-high,#e4e8f6); --s3:var(--md-sc-highest,#d8ddf0);
  --on:var(--md-on-surface,#1a1c26); --on-var:var(--md-on-surface-variant,#4b5064); --outline:var(--md-outline-variant,#c9cee0);
  --primary:var(--md-primary,#3b5bdb); --on-primary:var(--md-on-primary,#fff); --pc:var(--md-primary-container,#dce3ff); --on-pc:var(--md-on-primary-container,#0c1f6e);
  --sc:var(--md-secondary-container,#ffd9e8); --on-sc:var(--md-on-secondary-container,#5d0b2e); --tc:var(--md-tertiary-container,#c9f2e3); --on-tc:var(--md-on-tertiary-container,#00382f);
  --wc:var(--md-warn-container,#ffe7ad); --on-wc:var(--md-on-warn-container,#4a3300); --ec:var(--md-error-container,#ffdad6); --on-ec:var(--md-on-error-container,#5c0006);
  --code-bg:#1c1e2b; --code-fg:#e8eaf6; --code-dim:#6c7290;
  --k-text:#4c7dff; --k-bc:#f2a516; --k-native:#ff6363; --k-bytes:#16b97f; --k-pixels:#9a63ff; --k-ctl:#8a90a6;
  --kitchen:color-mix(in srgb,#ff9a52 24%,var(--surface)); --market:color-mix(in srgb,#16b97f 22%,var(--surface));
  --spring:cubic-bezier(.34,1.56,.64,1); --shadow:var(--md-elev-1,0 1px 2px rgba(20,25,60,.08),0 4px 14px rgba(20,25,60,.07));
  color:var(--on); font-family:var(--md-font,"Google Sans Flex",Roboto,system-ui,sans-serif); line-height:1.5}
*{box-sizing:border-box}
button,select{font:inherit;color:inherit}
.page{display:block}
.stage{min-width:760px}
.toolbar{padding-right:62px}
'''
css = host + css
css = css.replace('.page{display:none}.page.on{display:block}', '')

out = '''/* ===== Code journey animations (generated by tools/md3-build/build_codejourney.py, do not edit by hand) =====
   From the file Rakesh shared: how source code becomes output on the screen (Java, Python, JavaScript)
   and the compiler versus interpreter story (kitchen and code), each with its teaching notes.
   Each widget lives in a shadow root. Mount: <div class="cj-card" data-cj="journey" data-lang="java"></div>
   or <div class="cj-card" data-cj="ci"></div>. Needs GSAP and its MotionPathPlugin (assets/vendor). */
(() => {
  if (typeof gsap === 'undefined' || typeof MotionPathPlugin === 'undefined') { console.warn('codejourney: GSAP is missing'); return; }
  gsap.registerPlugin(MotionPathPlugin);
  const CSS = ''' + json.dumps(css) + ''';
  const HTML = ''' + json.dumps(b) + ''';
  function mount(card) {
    if (card.dataset.cjOn) return;
    card.dataset.cjOn = '1';
    const mode = card.dataset.cj === 'ci' ? 'ci' : 'journey', lang = card.dataset.lang || 'java';
    const host = document.createElement('div');
    host.className = 'cj-host';
    card.appendChild(host);
    const R = host.attachShadow({ mode: 'open' });
    R.innerHTML = '<style>' + CSS + '</style>' + HTML;
    /* one widget shows one part: the journey for one language, or the compiler and interpreter story */
    R.getElementById(mode === 'journey' ? 'p2' : 'p1').style.display = 'none';
    if (mode === 'journey') { R.getElementById('langChips').style.display = 'none'; const v = R.querySelector('#c1 .vsep'); if (v) v.style.display = 'none'; }
    try { app(R, host, mode, lang); } catch (e) { console.warn('codejourney', e); }
  }
  function app(R, host, mode, lang) {
''' + app + '''
  }
  const all = () => document.querySelectorAll('.cj-card[data-cj]').forEach(mount);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', all); else all();
  window.CODEJOURNEY = { mount, mountAll: all };
})();
'''
open(OUT, 'w', encoding='utf-8').write(out)
print('wrote', os.path.relpath(OUT), len(out), 'bytes')
