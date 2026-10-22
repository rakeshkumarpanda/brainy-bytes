// Draw the step by step screenshots for the skills, rules and MCP chapters into content/claude/shots/.
//
// Two kinds of picture, and every picture says which kind it is in its corner:
//   term-*  Real terminal output. The text comes word for word from captures.json, made by capture.py.
//   ui-*    Illustrated mockups of claude.ai, Claude Desktop and a Claude Code session. They follow the menu
//           names in the Claude Help Center and Claude Code docs (October 2026) but are drawn, not captured,
//           because those screens need a signed in account. Real screens may look a little different.
//
// Usage:  node tools/claude-build/shots/render.mjs        (needs the playwright package, as in tools/js-build)
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
let pw;
for (const p of ['playwright', '/opt/node22/lib/node_modules/playwright']) { try { pw = require(p); break; } catch {} }
if (!pw) throw new Error('playwright was not found');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../../..');
const OUT = path.join(ROOT, 'content', 'claude', 'shots');
const cap = JSON.parse(fs.readFileSync(path.join(HERE, 'captures.json'), 'utf8'));
const VERSION = cap._meta.claude_version.replace(' (Claude Code)', '');

const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const BASE = `
*{box-sizing:border-box} body{margin:0; padding:18px; background:#e9eef5; font-family:"Segoe UI",system-ui,-apple-system,Roboto,sans-serif}
.frame{position:relative; width:860px; border-radius:12px; overflow:hidden; box-shadow:0 10px 30px rgba(20,40,80,.18); background:#fff}
.bar{display:flex; align-items:center; gap:7px; padding:10px 14px; background:#2a2f38; color:#c9d1dc; font-size:13px}
.bar i{width:12px; height:12px; border-radius:50%; display:inline-block} .bar i:nth-child(1){background:#ff5f57} .bar i:nth-child(2){background:#febc2e} .bar i:nth-child(3){background:#28c840}
.bar span{margin-left:10px}
.badge{position:absolute; right:10px; bottom:10px; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:.02em}
.badge.real{background:#1fa774; color:#fff} .badge.mock{background:#ffc928; color:#3b2a00}
.term{background:#14171c; color:#d7dde6; font:13.5px/1.55 "JetBrains Mono","DejaVu Sans Mono",Menlo,monospace; padding:14px 16px 44px; white-space:pre-wrap; word-break:break-all}
.term .p{color:#7ee787} .term .c{color:#ffffff; font-weight:700} .term .ok{color:#7ee787} .term .wait{color:#f2cc60} .term .warn{color:#ff9e64}
.app{display:flex; min-height:360px; background:#faf9f5; color:#1f1e1b; font-size:14px}
.side{width:200px; background:#f0eee6; padding:14px 10px; border-right:1px solid #e2ded2}
.side div{padding:7px 10px; border-radius:8px; color:#55524a; margin-bottom:2px}
.side .on{background:#e4e0d3; color:#1f1e1b; font-weight:700}
.main{flex:1; padding:20px 26px 46px; position:relative}
h3{margin:0 0 4px; font-size:19px} .muted{color:#77736a; font-size:13px; margin:0 0 14px}
.row{display:flex; justify-content:space-between; align-items:center; padding:11px 14px; border:1px solid #e2ded2; border-radius:10px; background:#fff; margin-bottom:8px}
.row b{display:block} .row small{color:#77736a}
.tg{width:38px; height:22px; border-radius:999px; background:#cfcabd; position:relative; flex:none}
.tg::after{content:""; position:absolute; top:3px; left:3px; width:16px; height:16px; border-radius:50%; background:#fff}
.tg.on{background:#d97757} .tg.on::after{left:19px}
.btn{display:inline-block; padding:7px 13px; border-radius:8px; background:#1f1e1b; color:#fff; font-weight:700; font-size:13px}
.btn.ghost{background:#fff; color:#1f1e1b; border:1px solid #cfcabd}
.menu{position:absolute; background:#fff; border:1px solid #d8d3c5; border-radius:10px; box-shadow:0 10px 24px rgba(0,0,0,.12); padding:6px; min-width:200px; font-size:14px}
.menu div{padding:8px 10px; border-radius:6px} .menu .hi{background:#f3eee2; font-weight:700}
.n{position:absolute; width:26px; height:26px; border-radius:50%; background:#e9485a; color:#fff; font-weight:800; font-size:14px; display:grid; place-items:center; box-shadow:0 0 0 3px #fff}
.ring{position:absolute; border:3px solid #e9485a; border-radius:10px}
.field{margin:10px 0} .field label{display:block; font-weight:700; font-size:13px; margin-bottom:4px}
.field .in{border:1px solid #cfcabd; border-radius:8px; padding:8px 10px; background:#fff; font-family:"JetBrains Mono",monospace; font-size:13px}
.modal{position:absolute; left:120px; top:84px; width:470px; background:#fff; border:1px solid #d8d3c5; border-radius:14px; box-shadow:0 20px 40px rgba(0,0,0,.18); padding:18px 20px}
.chatbox{position:absolute; left:26px; right:26px; bottom:52px; border:1px solid #d8d3c5; border-radius:16px; background:#fff; padding:12px 14px; color:#77736a}
.plus{display:inline-grid; place-items:center; width:28px; height:28px; border-radius:8px; border:1px solid #cfcabd; color:#1f1e1b; font-weight:700; margin-top:10px}
.cc{white-space:pre; background:#14171c; color:#d7dde6; font:13.5px/1.6 "JetBrains Mono","DejaVu Sans Mono",Menlo,monospace; padding:16px 18px 46px; min-height:300px; position:relative}
.cc .box{border:1px solid #4a5160; border-radius:8px; padding:8px 12px; margin:8px 0} .cc .dim{color:#8b93a1} .cc .sel{background:#2d3442; color:#fff} .cc .acc{color:#ff9e64} .cc .ok{color:#7ee787}
`;

function page(body, badge, title) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>${BASE}</style></head><body><div class="frame">
<div class="bar"><i></i><i></i><i></i><span>${esc(title)}</span></div>${body}
<div class="badge ${badge === 'real' ? 'real' : 'mock'}">${badge === 'real' ? `Real output · Claude Code ${VERSION}` : 'Illustrated mockup · not a real screenshot'}</div></div></body></html>`;
}

function colour(line) {
  let t = esc(line);
  t = t.replace(/✔ Connected/g, '<span class="ok">✔ Connected</span>').replace(/⏸ Pending approval/g, '<span class="wait">⏸ Pending approval</span>');
  t = t.replace(/^NO TESTS FOUND.*/, m => `<span class="warn">${m}</span>`);
  return t;
}

function term(keys, title = 'Terminal: ~/shop-app') {
  const lines = [];
  for (const k of keys) for (const s of cap[k]) {
    lines.push(`<span class="p">asha@laptop ~/shop-app $</span> <span class="c">${esc(s.cmd)}</span>`);
    if (s.out) lines.push(s.out.split('\n').map(colour).join('\n'));
  }
  return page(`<div class="term">${lines.join('\n')}</div>`, 'real', title);
}

const SIDE = (on, items) => `<div class="side">${items.map(i => `<div class="${i === on ? 'on' : ''}">${i}</div>`).join('')}</div>`;
const n = (k, x, y) => `<div class="n" style="left:${x}px; top:${y}px">${k}</div>`;
const ring = (x, y, w, h) => `<div class="ring" style="left:${x}px; top:${y}px; width:${w}px; height:${h}px"></div>`;

const SHOTS = {
  // ---------- terminal, real ----------
  'term-version': term(['version']),
  'term-skill-make': term(['skill-make']),
  'term-skill-run': term(['skill-run']),
  'term-skill-zip': term(['skill-zip']),
  'term-rules-make': term(['rules-make']),
  'term-mcp-add': term(['mcp-add', 'mcp-list']),
  'term-mcp-project': term(['mcp-project']),

  // ---------- claude.ai, illustrated ----------
  'ui-capabilities': page(`<div class="app">${SIDE('Capabilities', ['General', 'Usage', 'Memory', 'Capabilities', 'Cowork'])}
<div class="main"><h3>Capabilities</h3><p class="muted">Settings › Capabilities</p>
<div class="row"><div><b>Code execution and file creation</b><small>Lets Claude run code and create files. Skills need this.</small></div><div class="tg on"></div></div>
${ring(16, 70, 598, 58)}${n(1, 590, 56)}</div></div>`, 'mock', 'claude.ai · Settings'),

  'ui-skills-upload': page(`<div class="app">${SIDE('Skills', ['Chats', 'Projects', 'Artifacts', 'Customize', 'Skills', 'Connectors'])}
<div class="main"><div style="display:flex; justify-content:space-between; align-items:center"><div><h3>Skills</h3><p class="muted">Customize › Skills</p></div><div class="btn ghost" style="font-size:16px">+</div></div>
<div class="row"><div><b>Excel, Word, PowerPoint, PDF</b><small>Built in skills from Anthropic</small></div><div class="tg on"></div></div>
<div class="menu" style="right:26px; top:64px"><div class="hi">+ Create skill</div></div>
<div class="menu" style="right:26px; top:124px"><div style="color:#aaa">...</div><div class="hi">Upload a skill</div></div>
${n(1, 590, 8)}${n(2, 600, 70)}${n(3, 600, 164)}</div></div>`, 'mock', 'claude.ai · Customize'),

  'ui-skills-list': page(`<div class="app">${SIDE('Skills', ['Chats', 'Projects', 'Artifacts', 'Customize', 'Skills', 'Connectors'])}
<div class="main"><h3>Skills</h3><p class="muted">Customize › Skills · your uploaded skills appear here</p>
<div class="row"><div><b>pick-regression</b><small>Picks which tests to run for the current changes. Use when the user asks what to test...</small></div><div class="tg on"></div></div>
<div class="row"><div><b>test-cases</b><small>Writes manual test cases from a user story or acceptance criteria...</small></div><div class="tg on"></div></div>
<div class="row"><div><b>Excel, Word, PowerPoint, PDF</b><small>Built in skills from Anthropic</small></div><div class="tg on"></div></div>
${ring(16, 64, 598, 60)}${n(4, 590, 50)}</div></div>`, 'mock', 'claude.ai · Customize'),

  'ui-connector-add': page(`<div class="app">${SIDE('Connectors', ['Chats', 'Projects', 'Artifacts', 'Customize', 'Skills', 'Connectors'])}
<div class="main" style="min-height:460px"><h3>Connectors</h3><p class="muted">Customize › Connectors › Add › Custom › Web</p>
<div class="modal"><h3 style="font-size:17px">Add custom connector</h3><p class="muted">Only connect to servers you trust.</p>
<div class="field"><label>Name</label><div class="in">Expenses</div></div>
<div class="field"><label>Remote MCP server URL</label><div class="in">https://mcp.example.com/mcp</div></div>
<div style="text-align:right; margin-top:14px"><span class="btn ghost">Cancel</span> <span class="btn">Continue</span></div></div>
${n(1, 96, 154)}${n(2, 96, 230)}${n(3, 600, 306)}</div></div>`, 'mock', 'claude.ai · Customize'),

  'ui-chat-plus': page(`<div class="app">${SIDE('Chats', ['New chat', 'Chats', 'Projects', 'Artifacts', 'Customize'])}
<div class="main" style="min-height:500px"><h3>Good evening</h3><p class="muted">Click + in the message box to turn tools on for this chat</p>
<div class="menu" style="left:26px; top:96px; width:230px"><div class="hi">Connectors ›</div><div>Research</div><div style="color:#aaa">...</div></div>
<div class="menu" style="left:262px; top:126px; width:280px">
<div style="display:flex; justify-content:space-between">Expenses <span class="tg on"></span></div>
<div style="display:flex; justify-content:space-between">Google Drive <span class="tg"></span></div>
<div>Tool access: Auto</div><div>Manage connectors</div></div>
<div class="chatbox">Ask Claude about this week's expenses...<br><span class="plus">+</span></div>
${n(1, 6, 418)}${n(2, 236, 120)}${n(3, 548, 136)}</div></div>`, 'mock', 'claude.ai · chat'),

  'ui-desktop-config': page(`<div class="app">${SIDE('Developer', ['General', 'Developer'])}
<div class="main"><h3>Developer</h3><p class="muted">Claude Desktop › Settings › Developer</p>
<div class="row"><div><b>Local MCP servers</b><small>Servers in claude_desktop_config.json start with the app</small></div><span class="btn ghost">Edit Config</span></div>
<div class="row"><div><b>expenses</b><small>~/expenses-mcp/.venv/bin/python ~/expenses-mcp/server.py</small></div><span style="color:#1fa774; font-weight:700">running</span></div>
${ring(500, 68, 112, 46)}${n(1, 600, 54)}${n(2, 590, 136)}</div></div>`, 'mock', 'Claude Desktop · Settings'),

  // ---------- Claude Code session, illustrated ----------
  'ui-cc-slash': page(`<div class="cc"><span class="acc">✻</span> Claude Code <span class="dim">· ~/shop-app</span>
<div class="box">&gt; /</div>
<div class="sel">  /pick-regression     Picks which tests to run for the current changes...</div>
<div class="dim">  /test-cases          Writes manual test cases from a user story...</div>
<div class="dim">  /bug-report          Turns rough notes or a failing test log into a bug report...</div>
<div style="margin-top:14px" class="dim">Or ask in plain words: "which tests should I run for this branch?"</div>
${n(1, 330, 40)}${n(2, 800, 80)}</div>`, 'mock', 'Terminal: claude'),

  'ui-cc-context': page(`<div class="cc"><span class="acc">✻</span> Claude Code <span class="dim">· ~/shop-app</span>
<div class="box">&gt; /context</div>
<div style="margin-top:6px"><b>Memory files</b> <span class="dim">(loaded at session start)</span></div>
<div>  CLAUDE.md</div>
<div class="sel">  .claude/rules/dev/python.md</div>
<div class="sel">  .claude/rules/dev/pull-requests.md</div>
<div class="dim" style="margin-top:10px">  qa/*.md and dev/db-migrations.md have paths, so they wait
  until Claude touches a matching file.</div>
${n(1, 330, 40)}${n(2, 620, 110)}</div>`, 'mock', 'Terminal: claude'),

  'ui-cc-mcp': page(`<div class="cc"><span class="acc">✻</span> Claude Code <span class="dim">· ~/shop-app</span>
<div class="box">&gt; /mcp</div>
<div style="margin-top:6px"><b>Manage MCP servers</b></div>
<div class="sel">  ❯ expenses           <span class="ok">✔ connected</span>   · 2 tools</div>
<div>    claude-code-docs   <span class="ok">✔ connected</span>   · approved from .mcp.json</div>
<div class="dim" style="margin-top:10px">Pick a server to see its tools, sign in, or reconnect it.</div>
${n(1, 330, 40)}${n(2, 620, 100)}</div>`, 'mock', 'Terminal: claude'),
};

fs.mkdirSync(OUT, { recursive: true });
const browser = await pw.chromium.launch(fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const pg = await browser.newPage({ deviceScaleFactor: 1.5, viewport: { width: 900, height: 600 } });
for (const [name, html] of Object.entries(SHOTS)) {
  await pg.setContent(html.replace(/>\n</g, '><'));
  await pg.evaluate(() => document.fonts.ready);
  const el = await pg.$('.frame');
  await el.screenshot({ path: path.join(OUT, name + '.png') });
  console.log(name);
}
await browser.close();
