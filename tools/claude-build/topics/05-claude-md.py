# Chapter 5: CLAUDE.md and memory. Locations, load order, what to put in, imports, CLAUDE.local.md, AGENTS.md, auto memory, /init and /memory.
from ckit import part, run, test, show, md, cli, prompt, say, quiz, calc, ex, panel, pkg

MODULE = ('🛠️', 'Claude Code and its files', 'claude-code-files', 'Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.')

EXPAND = '''
// A small model of how Claude Code reads a CLAUDE.md: block HTML comments are
// removed, and every @path import (relative to the importing file, at most four
// hops deep) is loaded too. Paths inside backticks are left alone.
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";

const loaded = [];
function load(file, from, depth) {
  const text = readFileSync(file, "utf8").replace(/^<!--[\\s\\S]*?-->\\n?/gm, "").trim();
  loaded.push({ file, from, text });
  for (const line of text.split("\\n")) {
    if (line.includes("`")) continue;                         // `@path` in backticks is not an import
    for (const m of line.matchAll(/(^|\\s)@([\\w./~-]+)/g)) {
      const target = join(dirname(file), m[2]);
      if (depth < 4 && existsSync(target)) load(target, file, depth + 1);
    }
  }
}

load("CLAUDE.md", null, 0);
for (const f of loaded) {
  console.log(`=== ${f.file}` + (f.from ? `  (imported by ${f.from})` : ""));
  console.log(f.text + "\\n");
}
const lines = loaded.reduce((n, f) => n + f.text.split("\\n").length, 0);
console.log(`files loaded: ${loaded.length}, lines Claude sees: ${lines}`);
'''

CODES = {
    'shop': md('''
# GreenLeaf shop website

Online plant shop. Next.js front end, Node API, PostgreSQL.

## Commands
- Install: `npm ci`
- Run locally: `npm run dev` (http://localhost:3000)
- Test one file: `npx vitest run path/to/file.test.ts`
- Before every commit: `npm run lint && npm run typecheck`

## Code style
- TypeScript strict mode. No `any`.
- Prices are stored in paise as integers. Format only in the UI with `formatINR()`.
- API handlers live in `src/api/handlers/`, one file per route.

## Workflow
- Branch names: `feat/short-name` or `fix/short-name`.
- Write or update a test for every bug fix.
- IMPORTANT: never edit files in `src/generated/`. Run `npm run codegen` instead.

## Gotchas
- The payment sandbox needs `RAZORPAY_KEY_ID` in `.env.local`. Ask the user if it is missing.
- Images must go through `next/image`, the CDN rejects raw `<img>` tags.
''', 'CLAUDE.md for a web shop'),
    'data': md('''
# Sales analytics notebooks

Python 3.12 with pandas. Data comes from the `sales` schema in BigQuery.

## Commands
- Set up: `uv sync`
- Run a report: `uv run python reports/monthly.py --month 2026-09`

## Rules for numbers
- Revenue is always net of returns and GST. Use `clean.net_revenue()`.
- Months follow the financial year starting 1 April.
- Round money to 2 decimals only when printing, never in calculations.

## Output
- Charts go in `out/charts/` as PNG, 1200x700.
- Every report starts with a 3 line summary a manager can read on a phone.
''', 'CLAUDE.md for a data team'),
    'writer': md('''
# My blog: "Weekend Treks Near Pune"

This folder holds my blog posts as Markdown files in `posts/`.

## Voice
- Friendly, first person, short paragraphs. Readers are beginners.
- Distances in km, heights in metres, times as "about 2 hours".

## Every new post
1. Start from `templates/post.md`.
2. File name: `posts/YYYY-MM-DD-trek-name.md`.
3. Include a "What to carry" list and a "Getting there" section.
4. Check facts against my notes in `notes/` and ask me if something is missing.
''', 'CLAUDE.md for someone who does not code'),
    'user': md('''
# About me
- I am Asha, a QA engineer. I prefer short answers with the command first.
- My machine is Windows 11 with PowerShell. Give PowerShell commands, not bash.

# Habits
- Explain any git command that rewrites history before running it.
- When you finish a task, list the files you changed.
''', '~/.claude/CLAUDE.md: your personal file for every project'),
    'local': md('''
# My local setup (not committed)
- My test store runs at http://localhost:4100, not 3000.
- Use the test customer asha.test@greenleaf.example for checkout flows.
''', 'CLAUDE.local.md: private notes for this project'),
    'imports': test({
        'CLAUDE.md': '''
<!-- Maintainers: keep this file under 200 lines. Claude never sees this comment. -->
# GreenLeaf

See @README.md for what the project does.

## Git workflow
- @docs/git.md

## Note
Mention a file without loading it by using backticks: `@docs/old-notes.md`
''',
        'README.md': 'GreenLeaf is an online plant shop. Customers order plants and pots.',
        'docs/git.md': '''
- Branches: feat/name or fix/name
- Squash merge pull requests. See @../RELEASE.md for releases.
''',
        'RELEASE.md': '- Releases are tagged vYYYY.MM.DD every Friday.',
        'docs/old-notes.md': 'Old notes that should not load.',
        'expand.mjs': EXPAND,
    }, 'node expand.mjs', '@ imports, expanded the way Claude Code loads them', show=['CLAUDE.md', 'docs/git.md', 'expand.mjs'],
        badge='▶ Runs a small model of the loader'),
    'order': run('''
// Claude Code loads CLAUDE.md and CLAUDE.local.md from the folder you start in
// and every folder above it. They are joined from the top folder down,
// so the instructions closest to you are read last.
const files = {
  "/home/asha/CLAUDE.md": "(not loaded: only ~/.claude/CLAUDE.md is your user file)",
  "/home/asha/.claude/CLAUDE.md": "user: short answers",
  "/home/asha/work/CLAUDE.md": "work: company rules",
  "/home/asha/work/shop/CLAUDE.md": "shop: npm ci, vitest",
  "/home/asha/work/shop/CLAUDE.local.md": "local: my port is 4100",
  "/home/asha/work/shop/api/CLAUDE.md": "api: loads later, when Claude touches a file in api/",
};

function loadOrder(cwd) {
  const order = ["/home/asha/.claude/CLAUDE.md"];
  const parts = cwd.split("/").filter(Boolean);
  for (let i = 1; i <= parts.length; i++) {
    const dir = "/" + parts.slice(0, i).join("/");
    for (const name of ["CLAUDE.md", "CLAUDE.local.md"]) {
      const f = dir + "/" + name;
      if (f in files && f !== "/home/asha/CLAUDE.md") order.push(f);
    }
  }
  return order;
}

loadOrder("/home/asha/work/shop").forEach((f, i) => console.log(i + 1, f.padEnd(40), files[f]));
''', 'Which files load, and in what order'),
    'init': cli('''
cd ~/projects/greenleaf
claude
/init            # Claude studies the project and writes a starter CLAUDE.md
/memory          # open CLAUDE.md files and the auto memory folder to edit them
/context         # check that the file loaded, under "Memory files"
''', 'Create and check a CLAUDE.md', result='/init writes build commands, test instructions and conventions it finds. If a CLAUDE.md exists, it suggests improvements instead of overwriting it.'),
    'agents-md': md('''
@AGENTS.md

## Claude Code only
- Use plan mode before changing anything in `src/billing/`.
''', 'CLAUDE.md that reuses an existing AGENTS.md'),
    'memory-dir': show('''
~/.claude/projects/<project>/memory/
├── MEMORY.md            # index, one line per memory, first 200 lines or 25KB load every session
├── user_role.md         # type: user       "Asha is a QA engineer, prefers PowerShell"
├── feedback_testing.md  # type: feedback   "Run only the changed test file, not the whole suite"
└── project_launch.md    # type: project    "Diwali sale launch freeze from 15 Oct 2026"
''', 'What auto memory looks like on disk', lang='text', note='📂 Written by Claude, yours to edit'),
    'audit': cli('''
/doctor prompt-audit                    # check every instruction file for conflicts and stale lines
/doctor prompt-audit .claude/rules      # or just one folder
''', 'Audit your instruction files', result='Claude reports outdated or conflicting instructions with proposed edits. Nothing changes until you ask it to apply them.'),
}

PARTS = [
    part('what', '📘', 'What CLAUDE.md is for', '''
<p><code>CLAUDE.md</code> is a plain Markdown file of <b>instructions Claude Code reads at the start of every session</b>. Write down what you would otherwise explain again and again: how to run the project, the house rules, the traps.</p>
<p>Anthropic's guidance on when to add a line:</p>
<ul><li>Claude made the same mistake a second time.</li>
<li>A review caught something Claude should have known.</li>
<li>You typed the same correction you typed last session.</li>
<li>A new teammate would need the same context.</li></ul>
<div class="warn">Claude treats <code>CLAUDE.md</code> as <b>guidance, not enforcement</b>. It usually follows it, but it can slip. For "must never happen" rules, use a hook (chapter 8).</div>
''', easy=True, files=['CLAUDE.md'], kw=['CLAUDE.md', 'project instructions', 'memory', 'persistent context']),
    part('where', '📍', 'Where CLAUDE.md files live', '''
<div class="tw"><table class="jt"><tr><th>Scope</th><th>File</th><th>Shared with</th><th>Put here</th></tr>
<tr><td>Organisation</td><td>macOS <code>/Library/Application Support/ClaudeCode/CLAUDE.md</code>, Linux <code>/etc/claude-code/CLAUDE.md</code>, Windows <code>C:\\Program Files\\ClaudeCode\\CLAUDE.md</code></td><td>everyone on managed machines</td><td>company standards, security policy</td></tr>
<tr><td>You</td><td><code>~/.claude/CLAUDE.md</code></td><td>only you, all projects</td><td>your preferences and habits</td></tr>
<tr><td>Project</td><td><code>./CLAUDE.md</code> or <code>./.claude/CLAUDE.md</code></td><td>the team, through git</td><td>commands, conventions, architecture</td></tr>
<tr><td>You in this project</td><td><code>./CLAUDE.local.md</code> (add to <code>.gitignore</code>)</td><td>only you</td><td>your local URLs, test accounts</td></tr>
</table></div>
<p>Claude Code loads these from the folder you start in <b>and every folder above it</b>, joined from the top down. A <code>CLAUDE.md</code> inside a <b>subfolder</b> loads later, when Claude reads or edits a file in that subfolder.</p>
<div class="viz" data-viz="flow" data-k="levels"></div>
[[order]]
''', easy=True, files=['~/.claude/CLAUDE.md', './CLAUDE.md', './.claude/CLAUDE.md', './CLAUDE.local.md'], kw=['locations', 'load order', 'managed policy', 'user CLAUDE.md', 'CLAUDE.local.md', 'subdirectory']),
    part('put', '📥', 'What to put in, and what to leave out', '''
<p>This table comes from Anthropic's best practices guide. For every line, ask: <b>would removing this cause Claude to make mistakes?</b> If not, cut it.</p>
<div class="tw"><table class="jt"><tr><th>✅ Include</th><th>❌ Leave out</th></tr>
<tr><td>commands Claude cannot guess</td><td>anything Claude can work out by reading the code</td></tr>
<tr><td>style rules that differ from the usual</td><td>standard conventions Claude already knows</td></tr>
<tr><td>how to run tests, which runner you prefer</td><td>long API documentation (link to it instead)</td></tr>
<tr><td>branch names and pull request habits</td><td>information that changes every week</td></tr>
<tr><td>architecture decisions specific to you</td><td>tutorials and long explanations</td></tr>
<tr><td>environment quirks, required variables</td><td>a description of every file</td></tr>
<tr><td>gotchas that are not obvious</td><td>"write clean code" and other things that go without saying</td></tr>
</table></div>
<div class="cl-put"><ul><li>Concrete and checkable lines: "Run <code>npm test</code> before committing", not "test your changes".</li>
<li>Headings and bullets, not long paragraphs.</li>
<li>Under <b>200 lines</b>. Longer files cost context on every request and are followed less well.</li>
<li>One line with <b>IMPORTANT</b> when Claude keeps skipping it. If everything is important, nothing stands out.</li></ul></div>
''', easy=True, files=['CLAUDE.md'], kw=['what to include', 'what to exclude', '200 lines', 'IMPORTANT', 'best practices']),
    part('examples', '🧾', 'Three real CLAUDE.md files', '''
<p>Each file is short, specific and written for its own audience. Copy the one closest to your work and change the details.</p>
[[shop]]
[[data]]
[[writer]]
<div class="tip">Notice what is missing: no explanation of how Next.js or pandas work, no list of every file. Claude already knows those or can look.</div>
''', easy=True, files=['CLAUDE.md'], kw=['CLAUDE.md example', 'web app', 'data team', 'writer', 'template']),
    part('personal', '🙋', 'Your personal files: ~/.claude/CLAUDE.md and CLAUDE.local.md', '''
<p>Some instructions are about <b>you</b>, not the project. Keep them out of the team file.</p>
[[user]]
[[local]]
<p>Add <code>CLAUDE.local.md</code> to <code>.gitignore</code> so it is never committed. Within each folder it is read after <code>CLAUDE.md</code>, so your notes come last at that level.</p>
''', easy=True, files=['~/.claude/CLAUDE.md', 'CLAUDE.local.md', '.gitignore'], kw=['user CLAUDE.md', 'CLAUDE.local.md', 'personal preferences', 'gitignore']),
    part('imports', '🔗', 'Split a long file with @ imports', '''
<p>Write <code>@path/to/file</code> anywhere in a <code>CLAUDE.md</code> to pull another file in. Paths are relative to the file that contains the import. Imported files may import others, up to <b>four hops</b> deep. A path inside backticks is not imported. Block HTML comments are removed before Claude sees the file, so you can leave notes for humans.</p>
[[imports]]
<div class="warn">Imports help you organise, but they do not save context: imported files load at launch too. To load something only for certain files, use a path rule (chapter 6). To load it only for a task, use a skill (chapter 7).</div>
<p>The first time a project imports a file from <b>outside</b> the project folder, Claude Code asks you to approve it.</p>
''', files=['CLAUDE.md'], kw=['@ imports', 'import', 'four hops', 'HTML comments', 'backticks']),
    part('agentsmd', '🤝', 'AGENTS.md and other tools', '''
<p>Some teams already have an <code>AGENTS.md</code> file for other coding tools. Claude Code reads it as project instructions <b>only when there is no</b> <code>CLAUDE.md</code>, <code>.claude/CLAUDE.md</code> or <code>CLAUDE.local.md</code> in your folder or above it. If you have both, only the <code>CLAUDE.md</code> files load.</p>
<p>To use both, import one from the other:</p>
[[agents-md]]
<div class="cl-name">If someone tells you to write an "agents.md" to create Claude Code helpers, that is a different thing. Subagents live in <code>.claude/agents/&lt;name&gt;.md</code> (chapter 9). <code>AGENTS.md</code> at the project root is only shared project instructions.</div>
<p>You can change this with the <b>Project instructions</b> setting: read both files, only <code>CLAUDE.md</code>, or only your organisation's managed file.</p>
''', files=['AGENTS.md', 'CLAUDE.md'], kw=['AGENTS.md', 'other tools', 'project instructions setting']),
    part('auto', '🧠', 'Auto memory: notes Claude writes for itself', '''
<p>Besides your <code>CLAUDE.md</code>, Claude Code keeps its own notes per project. When you correct it ("use PowerShell, not bash"), it may save that so you do not have to repeat it next week.</p>
<div class="vs"><div><b>📘 CLAUDE.md</b>Written by you. Instructions and rules. Shared with the team if committed.</div><div><b>🧠 Auto memory</b>Written by Claude. Your preferences, corrections, project facts it cannot read from code. Stays on your machine.</div></div>
[[memory-dir]]
<ul><li>Memories have four types: <code>user</code>, <code>feedback</code>, <code>project</code> and <code>reference</code>.</li>
<li>Only the first 200 lines or 25KB of <code>MEMORY.md</code> load each session. Topic files are read when needed.</li>
<li>Turn it off with the toggle in <code>/memory</code>, with <code>"autoMemoryEnabled": false</code> in settings, or with <code>CLAUDE_CODE_DISABLE_AUTO_MEMORY=1</code>.</li></ul>
''', easy=True, files=['~/.claude/projects/<project>/memory/MEMORY.md'], kw=['auto memory', 'MEMORY.md', 'autoMemoryEnabled', 'memory types']),
    part('workflow', '🔁', 'Create, check and improve it', '''
[[init]]
<ol class="steps"><li>Run <code>/init</code> for a first draft.</li>
<li>Delete lines Claude could work out by itself.</li>
<li>Add the commands, rules and gotchas only your team knows.</li>
<li>Run <code>/context</code> to confirm it loaded.</li>
<li>When Claude gets something wrong twice, add one line. When a line stops mattering, remove it.</li></ol>
[[audit]]
<div class="scenario"><b>🏢 Real scenario: a growing file</b>A team's <code>CLAUDE.md</code> grew to 600 lines and Claude started ignoring rules. They kept the 120 lines everyone needs, moved database rules to <code>.claude/rules/database.md</code> with a path filter, and turned the release checklist into a skill. Claude followed the rules again.</div>
''', easy=True, files=['CLAUDE.md'], kw=['/init', '/memory', '/context', '/doctor prompt-audit', 'maintain']),
]

DG = {
    'levels': {'t': 'Four levels, joined into one set of instructions', 'w': 900, 'h': 300,
               'n': [['org', 20, 20, 250, 52, 'managed CLAUDE.md', {'c': 3, 'sub': 'set by IT', 'i': 'Company wide policy. Cannot be excluded by users.'}],
                     ['usr', 20, 88, 250, 52, '~/.claude/CLAUDE.md', {'c': 2, 'sub': 'you, every project', 'i': 'Your personal preferences.'}],
                     ['prj', 20, 156, 250, 52, './CLAUDE.md', {'c': 0, 'sub': 'the team, via git', 'i': 'Commands, conventions and gotchas for this project.'}],
                     ['loc', 20, 224, 250, 52, './CLAUDE.local.md', {'c': 5, 'sub': 'you, this project', 'i': 'Private notes. Read after CLAUDE.md in the same folder.'}],
                     ['ctx', 400, 110, 200, 70, 'context at launch', {'c': 1, 'sh': 'pill'}],
                     ['sub', 680, 40, 200, 56, 'src/api/CLAUDE.md', {'c': 4, 'sub': 'loads on demand', 'i': 'Joins the context when Claude reads or edits a file in src/api/.'}],
                     ['cl', 680, 160, 200, 56, 'Claude', {'c': 1, 'sh': 'pill'}]],
               'e': [['org', 'ctx'], ['usr', 'ctx'], ['prj', 'ctx'], ['loc', 'ctx'], ['ctx', 'cl'], ['sub', 'cl', {'t': 'later'}]],
               'st': [[['org', 'usr', 'org>ctx', 'usr>ctx'], 'Broad files come first: your organisation, then you.'],
                      [['prj', 'loc', 'prj>ctx', 'loc>ctx'], 'Then the project file and your private local notes.'],
                      [['ctx', 'cl', 'ctx>cl'], 'All of them are joined, not overridden. The closest instructions are read last.'],
                      [['sub', 'sub>cl'], 'Subfolder files arrive only when Claude works in that folder.']]},
}

INFO = {'title': 'CLAUDE.md: the note Claude reads first', 'panels': [
    panel([['e', '📘'], ['t', 'commands, rules, gotchas', {'b': 1}]], 'What goes in', 'What you would explain again and again.', 'Not what Claude can read from the code.'),
    panel([['e', '📍'], ['t', '~/.claude, project, local', {'b': 1}]], 'Where it lives', 'Personal, team or private.', 'Folders above load at launch, subfolders on demand.'),
    panel([['e', '✂️'], ['t', '< 200 lines', {'b': 1}]], 'Keep it short', 'Long files are followed less.', 'Move topics to rules and tasks to skills.'),
    panel([['e', '🧠'], ['t', 'MEMORY.md', {'b': 1}]], 'Auto memory', 'Claude keeps its own notes.', 'You can read, edit or turn it off.')],
    'remember': 'Would removing this line cause a mistake? If not, cut it.'}

REAL = [
    ['🛒', 'An e-commerce team', 'Adds "prices are paise integers, format only in the UI" to CLAUDE.md after Claude rounded prices twice. The bug never returns.'],
    ['📈', 'A data analyst', 'Keeps the financial year rule in CLAUDE.md, so every report counts April as month one without being told.'],
    ['✍️', 'A blogger', 'Uses a CLAUDE.md in a folder of posts so Claude always writes in the same voice and file format.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter shows exactly what goes in CLAUDE.md, where each file lives, how imports work, and how auto memory helps.',
        'यह अध्याय बताता है CLAUDE.md में क्या लिखें, files कहाँ रहती हैं, imports और auto memory कैसे काम करते हैं।',
        'ಈ ಅಧ್ಯಾಯ CLAUDE.md ನಲ್ಲಿ ಏನು ಬರೆಯಬೇಕು, files ಎಲ್ಲಿವೆ, imports ಮತ್ತು auto memory ತೋರಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ CLAUDE.md ରେ କଣ ଲେଖିବେ, files କେଉଁଠି, imports ଓ auto memory ଦେଖାଏ।',
        'يوضح هذا الفصل ما يوضع في CLAUDE.md وأين تعيش الملفات وكيف تعمل الاستيرادات والذاكرة التلقائية.',
        'Dieses Kapitel zeigt, was in CLAUDE.md gehört, wo die Dateien liegen und wie Importe und Auto-Memory funktionieren.'),
    say('what', 'Purpose', 'CLAUDE.md holds instructions Claude reads every session. It is guidance, not enforcement.',
        'CLAUDE.md में वे निर्देश हैं जो Claude हर session में पढ़ता है। यह मार्गदर्शन है, लागू नियम नहीं।',
        'CLAUDE.md ಪ್ರತಿ session ನಲ್ಲಿ ಓದುವ ಸೂಚನೆಗಳು. ಇದು ಮಾರ್ಗದರ್ಶನ, ಕಡ್ಡಾಯ ಅಲ್ಲ.',
        'CLAUDE.md ପ୍ରତି session ରେ ପଢାଯାଉଥିବା ନିର୍ଦ୍ଦେଶ। ଏହା ମାର୍ଗଦର୍ଶନ, ବାଧ୍ୟତାମୂଳକ ନୁହେଁ।',
        'CLAUDE.md يحمل تعليمات يقرأها Claude في كل جلسة. إنها إرشاد وليست فرضًا.',
        'CLAUDE.md enthält Anweisungen für jede Sitzung. Es ist Anleitung, kein Zwang.'),
    say('where', 'Locations', 'Use the home dot claude file for you, the project file for the team, and CLAUDE dot local for private notes. Folders above load at start.',
        'अपने लिए ~/.claude, टीम के लिए project file, निजी नोट्स के लिए CLAUDE.local.md।',
        'ನಿಮಗೆ ~/.claude, ತಂಡಕ್ಕೆ project file, ಖಾಸಗಿ ಟಿಪ್ಪಣಿಗೆ CLAUDE.local.md.',
        'ନିଜ ପାଇଁ ~/.claude, ଦଳ ପାଇଁ project file, ବ୍ୟକ୍ତିଗତ ପାଇଁ CLAUDE.local.md.',
        'ملف ~/.claude لك وملف المشروع للفريق وCLAUDE.local.md لملاحظاتك الخاصة.',
        '~/.claude für dich, die Projektdatei fürs Team und CLAUDE.local.md für private Notizen.'),
    say('put', 'What to include', 'Include commands, unusual style rules, test steps and gotchas. Leave out what Claude can read from code. Stay under 200 lines.',
        'Commands, खास नियम, test steps और gotchas रखें। 200 lines से कम रखें।',
        'Commands, ವಿಶೇಷ ನಿಯಮ, test steps ಮತ್ತು gotchas ಸೇರಿಸಿ. 200 lines ಒಳಗೆ.',
        'Commands, ବିଶେଷ ନିୟମ, test steps ଓ gotchas ରଖନ୍ତୁ। 200 lines ତଳେ।',
        'ضمّن الأوامر وقواعد الأسلوب الخاصة وخطوات الاختبار والمزالق. أقل من 200 سطر.',
        'Befehle, besondere Stilregeln, Testschritte und Fallstricke. Unter 200 Zeilen bleiben.'),
    say('examples', 'Examples', 'Three short files: a web shop, a data team and a blogger. Each says only what its reader needs.',
        'तीन छोटी files: web shop, data team और blogger।',
        'ಮೂರು ಚಿಕ್ಕ files: web shop, data team ಮತ್ತು blogger.',
        'ତିନୋଟି ଛୋଟ files: web shop, data team ଓ blogger.',
        'ثلاثة ملفات قصيرة لمتجر وفريق بيانات ومدوّن.',
        'Drei kurze Dateien: ein Webshop, ein Datenteam und ein Blogger.'),
    say('personal', 'Personal files', 'Put your own habits in the home file and your local setup in CLAUDE dot local dot md, which you keep out of git.',
        'अपनी आदतें home file में और local setup CLAUDE.local.md में रखें।',
        'ನಿಮ್ಮ ಅಭ್ಯಾಸ home file ನಲ್ಲಿ, local setup CLAUDE.local.md ನಲ್ಲಿ.',
        'ନିଜ ଅଭ୍ୟାସ home file ରେ, local setup CLAUDE.local.md ରେ।',
        'ضع عاداتك في الملف الرئيسي وإعدادك المحلي في CLAUDE.local.md خارج git.',
        'Eigene Gewohnheiten in die Home-Datei, lokales Setup in CLAUDE.local.md außerhalb von git.'),
    say('imports', 'Imports', 'At sign path imports another file, relative to the importing file, up to four hops. Imports organise but do not save context.',
        '@path दूसरी file जोड़ता है, चार स्तर तक। यह context नहीं बचाता।',
        '@path ಇನ್ನೊಂದು file ಸೇರಿಸುತ್ತದೆ, ನಾಲ್ಕು ಹಂತಗಳವರೆಗೆ.',
        '@path ଅନ୍ୟ file ଯୋଡେ, ଚାରି ସ୍ତର ପର୍ଯ୍ୟନ୍ତ।',
        '@path يستورد ملفًا آخر حتى أربع قفزات، لكنه لا يوفّر السياق.',
        '@Pfad importiert eine Datei, bis zu vier Ebenen tief, spart aber keinen Kontext.'),
    say('agentsmd', 'AGENTS.md', 'Claude Code reads AGENTS.md only when there is no CLAUDE.md. To use both, import AGENTS.md from CLAUDE.md.',
        'CLAUDE.md न होने पर ही Claude Code AGENTS.md पढ़ता है।',
        'CLAUDE.md ಇಲ್ಲದಿದ್ದಾಗ ಮಾತ್ರ AGENTS.md ಓದುತ್ತದೆ.',
        'CLAUDE.md ନଥିଲେ ହିଁ AGENTS.md ପଢେ।',
        'يقرأ Claude Code ملف AGENTS.md فقط عند غياب CLAUDE.md.',
        'Claude Code liest AGENTS.md nur, wenn es keine CLAUDE.md gibt.'),
    say('auto', 'Auto memory', 'Claude writes its own notes in a memory folder. The first 200 lines of MEMORY dot md load each session. You can edit or turn it off.',
        'Claude अपनी notes memory folder में लिखता है। MEMORY.md की पहली 200 lines हर session में लोड होती हैं।',
        'Claude ತನ್ನ notes memory folder ನಲ್ಲಿ ಬರೆಯುತ್ತದೆ. MEMORY.md ಮೊದಲ 200 lines ಲೋಡ್.',
        'Claude ନିଜ notes memory folder ରେ ଲେଖେ। MEMORY.md ର ପ୍ରଥମ 200 lines ଲୋଡ୍।',
        'يكتب Claude ملاحظاته في مجلد الذاكرة. تُحمّل أول 200 سطر من MEMORY.md.',
        'Claude schreibt eigene Notizen. Die ersten 200 Zeilen von MEMORY.md werden geladen.'),
    say('workflow', 'Workflow', 'Run slash init, prune it, add what only your team knows, check with slash context, and audit with doctor prompt audit.',
        '/init चलाएं, छांटें, टीम की जानकारी जोड़ें, /context से जांचें।',
        '/init ಓಡಿಸಿ, ಕತ್ತರಿಸಿ, ತಂಡದ ಮಾಹಿತಿ ಸೇರಿಸಿ, /context ನಿಂದ ಪರಿಶೀಲಿಸಿ.',
        '/init ଚଲାନ୍ତୁ, କାଟନ୍ତୁ, ଦଳର ତଥ୍ୟ ଯୋଡନ୍ତୁ, /context ରେ ଯାଞ୍ଚ କରନ୍ତୁ।',
        'شغّل /init ثم شذّبه وأضف ما يعرفه فريقك وتحقق بـ /context.',
        '/init ausführen, kürzen, Teamwissen ergänzen, mit /context prüfen.'),
    say('practice', 'Practice', 'Practise sorting lines into include or leave out, checking file length and finding imports.',
        'Lines छांटने, लंबाई जांचने और imports ढूंढने का अभ्यास।',
        'Lines ವಿಂಗಡಿಸುವ, ಉದ್ದ ಪರಿಶೀಲಿಸುವ ಮತ್ತು imports ಹುಡುಕುವ ಅಭ್ಯಾಸ.',
        'Lines ବାଛିବା, ଲମ୍ବ ଯାଞ୍ଚ ଓ imports ଖୋଜିବାର ଅଭ୍ୟାସ।',
        'تدرّب على فرز الأسطر وفحص الطول وإيجاد الاستيرادات.',
        'Übe Zeilen zu sortieren, Länge zu prüfen und Importe zu finden.'),
]

QUIZ = [
    quiz('e', 'When does Claude Code read the project CLAUDE.md?', ['At the start of every session', 'Only when you type /init', 'Once a week', 'Never'], 0, 'Every time.', 'It is loaded at launch into every session in that folder.'),
    quiz('e', 'Where do personal preferences for all your projects go?', ['~/.claude/CLAUDE.md', './CLAUDE.md', '.mcp.json', 'README.md'], 0, 'Your home folder.', 'The user file applies to every project and is only yours.'),
    quiz('e', 'Which file should be in .gitignore?', ['CLAUDE.local.md', 'CLAUDE.md', '.claude/settings.json', 'AGENTS.md'], 0, 'Private.', 'CLAUDE.local.md holds your personal notes for one project.'),
    quiz('m', 'Which line belongs in CLAUDE.md?', ['Run npm run typecheck before committing', 'Write clean code', 'JavaScript has arrays', 'src/ has many files'], 0, 'Concrete and project specific.', 'The others are obvious or can be read from the code.'),
    quiz('m', 'What is the target length for a CLAUDE.md file?', ['Under 200 lines', 'Over 1,000 lines', 'Exactly 50 lines', 'No limit, longer is better'], 0, 'Short is followed better.', 'Longer files cost more context and reduce adherence.'),
    quiz('m', 'A CLAUDE.md sits in src/api/. When does it load?', ['When Claude reads or edits a file in src/api/', 'At launch', 'Never', 'Only with /memory'], 0, 'Subfolder.', 'Subfolder files load on demand.'),
    quiz('h', 'How deep can @ imports nest?', ['Four hops', 'One hop', 'Ten hops', 'Unlimited'], 0, 'A small number.', 'Imported files can import others up to four hops.'),
    quiz('h', 'The repo has AGENTS.md and CLAUDE.md. What does Claude read by default?', ['Only the CLAUDE.md files', 'Only AGENTS.md', 'Both', 'Neither'], 0, 'CLAUDE.md wins.', 'AGENTS.md is read only when no CLAUDE.md is present, unless you import it or change the setting.'),
    quiz('x', 'Claude keeps ignoring a rule in a 700 line CLAUDE.md. Best fix?', ['Shorten the file and move topics to rules and skills', 'Add IMPORTANT to every line', 'Repeat the rule ten times', 'Switch to a smaller model'], 0, 'The rule is getting lost.', 'Shorter files are followed better. Emphasis on everything stands out nowhere.'),
    quiz('x', 'Which must be enforced every time, with no exceptions?', ['Use a PreToolUse hook', 'Write it in CLAUDE.md in capitals', 'Put it in auto memory', 'Add it to README'], 0, 'Guidance versus enforcement.', 'CLAUDE.md is context. Hooks run code that can block an action.'),
]

CALC = [
    calc('e', 'A CLAUDE.md has 150 lines and imports a 70 line file. How many lines load at launch?', '220', 'Imports load too.', ['<span class="eq">150 + 70 = 220</span>']),
    calc('e', 'How many lines of MEMORY.md load at most?', '200', 'Or 25KB.', ['The first 200 lines or 25KB, whichever comes first.']),
    calc('m', 'In the imports example, how many files did Claude load in total?', '4', 'Read the output.', ['CLAUDE.md, README.md, docs/git.md and RELEASE.md. The old notes in backticks were skipped.']),
    calc('m', 'Running Claude in /home/asha/work/shop, how many files loaded in the load order example?', '4', 'Count the rows.', ['user file, work, shop and shop local.']),
    calc('h', 'A 600 line CLAUDE.md costs 9,000 tokens. You cut it to 120 lines. About how many tokens now, assuming the same tokens per line?', '1800', 'Tokens per line first.', ['<span class="eq">9,000 ÷ 600 = 15 per line</span>', '<span class="eq">120 × 15 = 1,800</span>'], alt=['1,800']),
    calc('x', 'That saving applies to each of 50 requests a day. How many tokens saved per day?', '360000', 'Saving per request times requests.', ['<span class="eq">9,000 − 1,800 = 7,200</span>', '<span class="eq">7,200 × 50 = 360,000</span>'], alt=['360,000']),
]

EX = [
    ex('keep-or-cut', 'e', 'Keep or cut?', '<p>Write <code>keepLine(line)</code>. Return false for vague lines that contain <code>"clean code"</code>, <code>"best practices"</code> or <code>"be careful"</code> (any case). Return true otherwise.</p>',
       'function keepLine(line) {\n  \n}\n',
       [('keepLine("Write clean code")', False), ('keepLine("Follow BEST PRACTICES")', False), ('keepLine("Run npm test before committing")', True)],
       'function keepLine(line) {\n  const vague = ["clean code", "best practices", "be careful"];\n  return !vague.some(v => line.toLowerCase().includes(v));\n}',
       hint='Lowercase the line and use <code>some</code>.', why='Lines that say nothing specific cost tokens on every request and change nothing.'),
    ex('find-imports', 'm', 'Find the imports', '<p>Write <code>findImports(text)</code> that returns every <code>@path</code> in the text (without the @) where the @ is at the start of a line or after a space. Skip lines that contain a backtick.</p>',
       'function findImports(text) {\n  \n}\n',
       [('findImports("See @README.md and @docs/git.md")', ['README.md', 'docs/git.md']), ('findImports("email me at a@b.com")', []), ('findImports("`@old.md`\\n@new.md")', ['new.md'])],
       'function findImports(text) {\n  const out = [];\n  for (const line of text.split("\\n")) {\n    if (line.includes("`")) continue;\n    for (const m of line.matchAll(/(^|\\s)@([\\w./~-]+)/g)) out.push(m[2]);\n  }\n  return out;\n}',
       hint='<code>matchAll</code> with <code>/(^|\\s)@([\\w./~-]+)/g</code>.', why='Knowing exactly which files are imported tells you what really loads at launch.'),
    ex('review-md', 'h', 'Check a CLAUDE.md', '<p>Write <code>review(text)</code> that returns a list of warnings: <code>"too long"</code> when there are more than 200 lines, and <code>"too many IMPORTANT"</code> when more than 3 lines contain <code>IMPORTANT</code>. Return an empty list when all is well.</p>',
       'function review(text) {\n  \n}\n',
       [('review("a\\nb")', []), ('review(Array(201).fill("x").join("\\n"))', ['too long']), ('review("IMPORTANT a\\nIMPORTANT b\\nIMPORTANT c\\nIMPORTANT d")', ['too many IMPORTANT'])],
       'function review(text) {\n  const lines = text.split("\\n");\n  const out = [];\n  if (lines.length > 200) out.push("too long");\n  if (lines.filter(l => l.includes("IMPORTANT")).length > 3) out.push("too many IMPORTANT");\n  return out;\n}',
       hint='Split into lines, then count.', why='These are the two most common reasons Claude starts ignoring instructions.'),
]

T = {
    'slug': 'claude-md', 'title': 'CLAUDE.md and Memory: What Goes Where', 'short': 'CLAUDE.md and memory', 'emoji': '📘', 'module': MODULE, 'minutes': 17,
    'lead': 'Exactly what to put in CLAUDE.md and what to leave out, the four places it can live and the order they load in, @ imports, CLAUDE.local.md, AGENTS.md, auto memory, and how to create and maintain it with /init, /memory and a prompt audit.',
    'plain': 'CLAUDE.md is a note you leave for Claude in your project folder. Claude reads it every time it starts, so it already knows your rules and shortcuts.',
    'desc': 'CLAUDE.md explained: locations, load order, what to include and exclude, real examples, imports, CLAUDE.local.md, AGENTS.md, auto memory and MEMORY.md, /init and /memory.',
    'summary': 'What CLAUDE.md is for and why it is guidance not enforcement, managed, user, project and local locations with the real load order, Anthropic\'s include and exclude table, three ready to copy CLAUDE.md files, personal files, @ imports run through a model of the loader, AGENTS.md rules, auto memory with MEMORY.md and memory types, and a workflow with /init, /context and /doctor prompt-audit.',
    'keywords': ['CLAUDE.md', 'CLAUDE.local.md', '~/.claude/CLAUDE.md', 'memory', 'auto memory', 'MEMORY.md', '@ import', 'AGENTS.md', '/init', '/memory', 'load order', 'what to include'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
