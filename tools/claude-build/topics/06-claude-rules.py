# Chapter 6: rules. The .claude/rules/ folder, the paths field, glob patterns, real rule files, user rules, symlinks, and choosing rules versus CLAUDE.md and skills.
from ckit import part, run, test, show, md, cli, say, quiz, calc, ex, panel

MODULE = ('🛠️', 'Claude Code and its files', 'claude-code-files', 'Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.')

WHICH = '''
// A model of how Claude Code picks rules: a rule with no paths loads at launch,
// a rule with paths loads when Claude reads, writes or edits a matching file.
import { readFileSync, readdirSync } from "node:fs";
import { join, matchesGlob } from "node:path";

function rules(dir) {
  return readdirSync(dir, { recursive: true }).filter(f => f.endsWith(".md")).map(f => {
    const text = readFileSync(join(dir, f), "utf8");
    const front = text.match(/^---\\n([\\s\\S]*?)\\n---/);
    const paths = front ? [...front[1].matchAll(/^\\s*-\\s*"(.+)"/gm)].map(m => m[1]) : [];
    return { file: f, paths };
  });
}

const all = rules(".claude/rules");
console.log("At launch:", all.filter(r => !r.paths.length).map(r => r.file).join(", "));
for (const touched of ["src/api/orders.ts", "tests/cart.test.ts", "README.md", "content/blog/diwali-sale.md"]) {
  const extra = all.filter(r => r.paths.some(p => matchesGlob(touched, p))).map(r => r.file);
  console.log(`Claude edits ${touched.padEnd(28)} -> also loads: ${extra.join(", ") || "(nothing new)"}`);
}
'''

RULES = {
    '.claude/rules/code-style.md': '''
# Code style
- TypeScript strict mode. No `any`.
- Name files in kebab-case: `order-summary.ts`.
- Prefer small pure functions. Keep side effects at the edges.
''',
    '.claude/rules/security.md': '''
# Security
- Never log full card numbers, OTPs or passwords.
- Read secrets from environment variables, never from source files.
''',
    '.claude/rules/backend/api.md': '''
---
paths:
  - "src/api/**/*.ts"
---

# API rules
- Validate every request body with the schemas in `src/api/schemas/`.
- Errors use the shape `{ error: { code, message } }` with a 4xx or 5xx status.
- Every new endpoint gets an entry in `docs/openapi.yaml`.
''',
    '.claude/rules/testing.md': '''
---
paths:
  - "tests/**/*.test.ts"
  - "src/**/*.test.ts"
---

# Testing rules
- Use Vitest. One `describe` per function, plain English test names.
- No real network calls. Use the fakes in `tests/fakes/`.
- Run only the changed file: `npx vitest run <file>`.
''',
    '.claude/rules/content/blog.md': '''
---
paths:
  - "content/**/*.md"
---

# Blog writing rules
- Title under 60 characters. One H1 only.
- Every post ends with a call to action linking to /shop.
- Prices in rupees as "Rs 499", never "INR 499".
''',
}

CODES = {
    'tree': show('''
your-project/
├── CLAUDE.md                    <- short: commands and the big picture
└── .claude/
    └── rules/
        ├── code-style.md        <- no paths: loads every session
        ├── security.md          <- no paths: loads every session
        ├── testing.md           <- paths: tests only
        ├── backend/
        │   └── api.md           <- paths: src/api only
        └── content/
            └── blog.md          <- paths: blog posts only
''', 'A project with rules', lang='text', note='📂 Folder layout'),
    'style': md(RULES['.claude/rules/code-style.md'], '.claude/rules/code-style.md (no paths, always loaded)'),
    'api': md(RULES['.claude/rules/backend/api.md'], '.claude/rules/backend/api.md (loaded for API files)'),
    'testing': md(RULES['.claude/rules/testing.md'], '.claude/rules/testing.md (loaded for test files)'),
    'blog': md(RULES['.claude/rules/content/blog.md'], '.claude/rules/content/blog.md (for a content team)'),
    'contracts': md('''
---
paths: "contracts/**/*.docx, contracts/**/*.pdf"
---

# Contract review rules
- Flag any clause with unlimited liability or auto renewal longer than 12 months.
- Quote the exact clause number for every point you raise.
- Our standard payment term is 30 days. Flag anything longer.
''', '.claude/rules/contracts.md (comma separated paths, for a legal team)'),
    'which': test({**RULES, 'which-rules.mjs': WHICH}, 'node which-rules.mjs', 'Which rules load for which file', show=['which-rules.mjs'],
                  badge='▶ Runs a model of rule loading on the five rule files above'),
    'user-rules': show('''
~/.claude/rules/
├── preferences.md     # "Answer with the command first, then one line of explanation"
└── git.md             # "Never force push. Explain any rebase before running it."
''', 'Personal rules for every project', lang='text', note='📂 Your home folder'),
    'symlink': cli('''
# keep company rules in one folder and link them into each project
ln -s ~/company-standards/security.md .claude/rules/security.md
ln -s ~/shared-claude-rules .claude/rules/shared
''', 'Share rules between projects with symlinks', result='The first session asks you once to approve rules linked from outside the project. After approval, linked rules without paths load. Rules in ~/.claude/rules/ need no approval.'),
    'debug': cli('''
/context          # rules that loaded appear in the memory files list
/memory           # open and edit rule files
claude --debug    # shows a YAML parse error if a rule's frontmatter is broken
''', 'Check that your rules load', result='A rule whose frontmatter does not parse is loaded as if it had no paths, so it loads every session. --debug shows why.'),
}

PARTS = [
    part('name', '🔎', 'First, the name: there is no rules.md', '''
<p>Many guides and videos talk about a "rules.md" file. <b>Claude Code does not read a file with that name.</b> What it does have is a <b>folder</b> of rule files:</p>
<div class="vs"><div><b>❌ Not a Claude Code file</b><code>rules.md</code> at the project root does nothing on its own.</div>
<div><b>✅ What really exists</b><code>.claude/rules/*.md</code> in the project and <code>~/.claude/rules/*.md</code> for you. Any number of Markdown files, one topic each.</div></div>
<div class="cl-name">Other tools have their own rule files, such as a <code>.cursorrules</code> file. Those are not read by Claude Code either. To reuse one, copy its contents into a file in <code>.claude/rules/</code> or import it from <code>CLAUDE.md</code> with <code>@</code>.</div>
''', easy=True, files=['.claude/rules/', '~/.claude/rules/'], kw=['rules.md', 'name check', '.claude/rules', 'cursorrules']),
    part('setup', '🧱', 'Create your first rules, step by step', '''
<ol class="steps"><li>In your project, create the folder <code>.claude/rules/</code>.</li>
<li>Add one Markdown file per topic, with a clear name like <code>testing.md</code> or <code>security.md</code>.</li>
<li>Write short, checkable bullet points, just like in <code>CLAUDE.md</code>.</li>
<li>Optional: add a <code>paths</code> list at the top so the rule loads only for matching files.</li>
<li>Start a new session and run <code>/context</code> to see which rules loaded.</li></ol>
[[tree]]
<p>Claude Code finds every <code>.md</code> file in <code>.claude/rules/</code>, including subfolders like <code>backend/</code>. A rule <b>without</b> <code>paths</code> loads at launch with the same priority as <code>.claude/CLAUDE.md</code>.</p>
[[style]]
''', easy=True, files=['.claude/rules/code-style.md', '.claude/rules/security.md'], kw=['create rules', 'one topic per file', 'subfolders', 'setup']),
    part('paths', '🎯', 'Path rules: load only for matching files', '''
<p>Add YAML front matter with a <code>paths</code> list. The rule then loads only when Claude <b>reads, writes or edits</b> a file that matches one of the patterns. <code>paths</code> is the <b>only</b> field rules use. Any other field is ignored.</p>
[[api]]
<div class="tw"><table class="jt"><tr><th>Pattern</th><th>Matches</th></tr>
<tr><td><code>**/*.ts</code></td><td>every TypeScript file, in any folder</td></tr>
<tr><td><code>src/**/*</code></td><td>everything under <code>src/</code></td></tr>
<tr><td><code>*.md</code></td><td>Markdown files in the project root only</td></tr>
<tr><td><code>src/**/*.{ts,tsx}</code></td><td>both <code>.ts</code> and <code>.tsx</code> under <code>src/</code></td></tr>
</table></div>
<p>You can write <code>paths</code> as a list, or as one comma separated string.</p>
<div class="viz" data-viz="flow" data-k="load"></div>
[[which]]
''', files=['.claude/rules/backend/api.md'], kw=['paths', 'frontmatter', 'glob', 'path-specific rules', 'brace expansion']),
    part('examples', '🧾', 'Ready to copy rule files', '''
<p>Rules are not only for code. Any team that keeps files in a folder can use them.</p>
[[testing]]
[[blog]]
[[contracts]]
<div class="cl-put"><ul><li>One topic per file, with a name that says what it covers.</li>
<li>Rules that apply everywhere: no <code>paths</code>.</li>
<li>Rules for one area: <code>paths</code> that match that area.</li>
<li>Short, concrete bullets that can be checked.</li></ul></div>
''', easy=True, files=['.claude/rules/testing.md', '.claude/rules/content/blog.md', '.claude/rules/contracts.md'], kw=['rule examples', 'testing rules', 'content rules', 'legal rules']),
    part('user', '🙋', 'Personal rules in ~/.claude/rules/', '''
<p>Rules in your home folder apply to <b>every project</b> on your machine. They load before project rules. Neither overrides the other, so if they disagree Claude may follow either. Keep them consistent.</p>
[[user-rules]]
''', easy=True, files=['~/.claude/rules/'], kw=['user rules', 'personal rules', 'home folder']),
    part('share', '🔗', 'Share one set of rules across many projects', '''
<p>The rules folder follows symlinks, so a company can keep its standards in one place and link them into every repository.</p>
[[symlink]]
''', files=['.claude/rules/'], kw=['symlink', 'shared rules', 'company standards']),
    part('choose', '⚖️', 'Rules, CLAUDE.md, skills or hooks?', '''
<div class="tw"><table class="jt"><tr><th>You want...</th><th>Use</th><th>Loads</th></tr>
<tr><td>a few facts for every session</td><td><code>CLAUDE.md</code></td><td>every session</td></tr>
<tr><td>a topic kept in its own file, for everyone</td><td>rule without <code>paths</code></td><td>every session</td></tr>
<tr><td>guidance only for certain files</td><td>rule with <code>paths</code></td><td>when a matching file is touched</td></tr>
<tr><td>a multi step procedure, run sometimes</td><td>skill</td><td>description always, steps when used</td></tr>
<tr><td>something that must never happen</td><td>hook or permission rule</td><td>runs as code, outside Claude</td></tr>
</table></div>
<div class="warn">A path rule joins the conversation when its file is touched, so <code>/compact</code> summarises it away with everything else. It loads again the next time Claude touches a matching file. If a rule must survive compaction, remove its <code>paths</code> or move it to the root <code>CLAUDE.md</code>.</div>
''', easy=True, files=['CLAUDE.md', '.claude/rules/', 'SKILL.md', 'settings.json'], kw=['rules vs CLAUDE.md', 'rules vs skills', 'compaction', 'when to use']),
    part('debug', '🩺', 'When a rule does not seem to work', '''
[[debug]]
<ul><li><b>Never loads?</b> Check the path pattern. <code>*.md</code> matches only the root folder. Use <code>**/*.md</code> for every folder.</li>
<li><b>Always loads?</b> The front matter may not parse, for example a missing closing <code>---</code>. Then the rule loads as if it had no paths.</li>
<li><b>Loads but is ignored?</b> Look for a rule elsewhere that says the opposite. Run <code>/doctor prompt-audit</code>.</li></ul>
''', files=['.claude/rules/'], kw=['debug rules', '/context', 'claude --debug', 'troubleshooting']),
]

DG = {
    'load': {'t': 'When each rule joins the context', 'w': 900, 'h': 280,
             'n': [['start', 20, 110, 150, 56, 'session starts', {'c': 5, 'sh': 'pill'}],
                   ['always', 230, 20, 220, 56, 'code-style.md, security.md', {'c': 0, 'sub': 'no paths', 'i': 'Loaded at launch, like CLAUDE.md.'}],
                   ['edit', 230, 200, 220, 56, 'Claude edits src/api/orders.ts', {'c': 2, 'i': 'Read, Write or Edit on a file.'}],
                   ['api', 520, 200, 180, 56, 'backend/api.md', {'c': 3, 'sub': 'paths match', 'i': 'paths: src/api/**/*.ts matches the edited file.'}],
                   ['tst', 520, 110, 180, 56, 'testing.md', {'c': 4, 'sub': 'waits', 'i': 'Not loaded until a test file is touched.'}],
                   ['ctx', 760, 20, 120, 56, 'context', {'c': 1, 'sh': 'pill'}]],
             'e': [['start', 'always'], ['always', 'ctx'], ['start', 'edit', {'t': 'later'}], ['edit', 'api'], ['api', 'ctx']],
             'st': [[['start', 'always', 'start>always', 'always>ctx', 'ctx'], 'Rules without paths load as soon as the session starts.'],
                    [['edit', 'start>edit'], 'Later, Claude edits an API file.'],
                    [['api', 'edit>api', 'api>ctx'], 'The API rule matches that file, so it joins the context now.'],
                    [['tst'], 'The testing rule still waits. Its files have not been touched.']]},
}

INFO = {'title': 'Rules: the right advice for the right files', 'panels': [
    panel([['e', '🔎'], ['t', 'rules.md ✗  .claude/rules/ ✓', {'b': 1, 'size': 11}]], 'Name check', 'A folder, not one file.', 'One topic per Markdown file.'),
    panel([['e', '🎯'], ['t', 'paths: src/api/**', {'b': 1}]], 'Path rules', 'Load only for matching files.', 'paths is the only field.'),
    panel([['e', '🙋'], ['t', '~/.claude/rules/', {'b': 1}]], 'Personal rules', 'Apply to all your projects.', 'Loaded before project rules.'),
    panel([['e', '⚖️'], ['t', 'rule vs skill vs hook', {'b': 1}]], 'Pick the right tool', 'Rules guide, hooks enforce.', 'Procedures go in skills.')],
    'remember': 'No paths: every session. With paths: only when a matching file is touched.'}

REAL = [
    ['🏦', 'A bank\'s app team', 'Keeps security rules without paths so they load in every session, and API rules with paths so the front end team never sees them.'],
    ['📰', 'A news website', 'Has a content rule for content/**/*.md with headline length and style. Writers using Claude Code get it only when editing articles.'],
    ['⚖️', 'A legal team', 'Adds a contracts rule so any time Claude opens a contract it checks liability and renewal clauses the same way.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter explains rules: the dot claude rules folder, path rules that load only for matching files, and when to choose rules over other files.',
        'यह अध्याय rules समझाता है: .claude/rules folder, path rules, और कब कौन सी file चुनें।',
        'ಈ ಅಧ್ಯಾಯ rules ವಿವರಿಸುತ್ತದೆ: .claude/rules folder, path rules ಮತ್ತು ಯಾವಾಗ ಯಾವುದು.',
        'ଏହି ଅଧ୍ୟାୟ rules ବୁଝାଏ: .claude/rules folder, path rules ଓ କେବେ କଣ।',
        'يشرح هذا الفصل القواعد: مجلد .claude/rules وقواعد المسارات ومتى تختارها.',
        'Dieses Kapitel erklärt Regeln: den Ordner .claude/rules, Pfadregeln und wann man sie wählt.'),
    say('name', 'Name check', 'Claude Code has no rules dot md file. It reads Markdown files in the dot claude rules folder.',
        'Claude Code में rules.md file नहीं है। यह .claude/rules folder की files पढ़ता है।',
        'Claude Code ನಲ್ಲಿ rules.md ಇಲ್ಲ. .claude/rules folder ನ files ಓದುತ್ತದೆ.',
        'Claude Code ରେ rules.md ନାହିଁ। .claude/rules folder ର files ପଢେ।',
        'لا يوجد ملف rules.md في Claude Code. إنه يقرأ ملفات مجلد .claude/rules.',
        'Claude Code hat keine rules.md. Es liest Markdown-Dateien im Ordner .claude/rules.'),
    say('setup', 'Setup', 'Create the rules folder, add one file per topic, and check with slash context. Rules without paths load every session.',
        'Rules folder बनाएं, हर विषय की एक file जोड़ें, /context से जांचें।',
        'Rules folder ಮಾಡಿ, ಪ್ರತಿ ವಿಷಯಕ್ಕೆ ಒಂದು file, /context ಪರಿಶೀಲಿಸಿ.',
        'Rules folder ତିଆରି କରନ୍ତୁ, ପ୍ରତି ବିଷୟ ପାଇଁ ଗୋଟିଏ file, /context ଯାଞ୍ଚ।',
        'أنشئ مجلد القواعد وأضف ملفًا لكل موضوع وتحقق بـ /context.',
        'Lege den Ordner an, eine Datei pro Thema, und prüfe mit /context.'),
    say('paths', 'Path rules', 'A paths list in the front matter makes a rule load only when Claude reads, writes or edits a matching file.',
        'Front matter में paths सूची हो तो rule सिर्फ मिलती file पर लोड होता है।',
        'Front matter ನಲ್ಲಿ paths ಇದ್ದರೆ ಹೊಂದುವ file ಗೆ ಮಾತ್ರ ಲೋಡ್.',
        'Front matter ରେ paths ଥିଲେ ମେଳ ଖାଉଥିବା file ପାଇଁ ହିଁ ଲୋଡ୍।',
        'قائمة paths في الترويسة تجعل القاعدة تُحمّل فقط عند لمس ملف مطابق.',
        'Eine paths-Liste lädt die Regel nur, wenn Claude eine passende Datei bearbeitet.'),
    say('examples', 'Examples', 'Rules work for tests, blog posts and contracts alike. Keep one topic per file with short, checkable bullets.',
        'Rules tests, blog और contracts सबके लिए काम करते हैं।',
        'Rules tests, blog ಮತ್ತು contracts ಎಲ್ಲಕ್ಕೂ ಕೆಲಸ ಮಾಡುತ್ತವೆ.',
        'Rules tests, blog ଓ contracts ସବୁ ପାଇଁ କାମ କରେ।',
        'القواعد تصلح للاختبارات والمدونات والعقود.',
        'Regeln passen für Tests, Blogposts und Verträge.'),
    say('user', 'Personal rules', 'Rules in your home dot claude rules folder apply to every project and load before project rules.',
        '~/.claude/rules हर project पर लागू होते हैं।',
        '~/.claude/rules ಎಲ್ಲಾ projects ಗೆ ಅನ್ವಯ.',
        '~/.claude/rules ସବୁ projects ରେ ଲାଗୁ।',
        'قواعد ~/.claude/rules تنطبق على كل المشاريع.',
        'Regeln in ~/.claude/rules gelten für alle Projekte.'),
    say('share', 'Sharing', 'Symlink a shared folder of rules into each project. The first session asks you to approve outside rules.',
        'Shared rules को symlink से हर project में जोड़ें।',
        'Shared rules ಅನ್ನು symlink ಮೂಲಕ ಸೇರಿಸಿ.',
        'Shared rules କୁ symlink ଦ୍ୱାରା ଯୋଡନ୍ତୁ।',
        'اربط مجلد قواعد مشتركًا في كل مشروع برابط رمزي.',
        'Verlinke einen gemeinsamen Regelordner per Symlink in jedes Projekt.'),
    say('choose', 'Choosing', 'CLAUDE.md for every session, path rules for some files, skills for procedures, and hooks for things that must never happen.',
        'हर session के लिए CLAUDE.md, कुछ files के लिए path rules, प्रक्रियाओं के लिए skills, और hooks।',
        'ಪ್ರತಿ session ಗೆ CLAUDE.md, ಕೆಲವು files ಗೆ path rules, ಪ್ರಕ್ರಿಯೆಗಳಿಗೆ skills, hooks.',
        'ପ୍ରତି session ପାଇଁ CLAUDE.md, କିଛି files ପାଇଁ path rules, ପ୍ରକ୍ରିୟା ପାଇଁ skills, hooks.',
        'CLAUDE.md لكل جلسة وقواعد المسارات لبعض الملفات والمهارات للإجراءات والخطافات للممنوعات.',
        'CLAUDE.md für jede Sitzung, Pfadregeln für bestimmte Dateien, Skills für Abläufe, Hooks für Verbote.'),
    say('debug', 'Debugging', 'Check slash context, fix the path pattern, and use claude dash dash debug to find broken front matter.',
        '/context देखें, pattern ठीक करें, claude --debug से गलती खोजें।',
        '/context ನೋಡಿ, pattern ಸರಿಪಡಿಸಿ, claude --debug ಬಳಸಿ.',
        '/context ଦେଖନ୍ତୁ, pattern ଠିକ୍ କରନ୍ତୁ, claude --debug ବ୍ୟବହାର କରନ୍ତୁ।',
        'راجع /context وصحّح النمط واستخدم claude --debug.',
        'Prüfe /context, korrigiere das Muster und nutze claude --debug.'),
    say('practice', 'Practice', 'Practise matching paths, splitting front matter and deciding where an instruction belongs.',
        'Paths मिलाने और सही जगह चुनने का अभ्यास।',
        'Paths ಹೊಂದಿಸುವ ಮತ್ತು ಸರಿಯಾದ ಸ್ಥಳ ಆಯ್ಕೆಯ ಅಭ್ಯಾಸ.',
        'Paths ମେଳ ଓ ଠିକ୍ ସ୍ଥାନ ବାଛିବାର ଅଭ୍ୟାସ।',
        'تدرّب على مطابقة المسارات واختيار المكان الصحيح.',
        'Übe Pfade abzugleichen und den richtigen Ort zu wählen.'),
]

QUIZ = [
    quiz('e', 'Does Claude Code read a file named rules.md at the project root?', ['No', 'Yes, always', 'Only on Mac', 'Only with /init'], 0, 'Folder, not file.', 'Rules live in .claude/rules/ as separate Markdown files.'),
    quiz('e', 'A rule has no paths field. When does it load?', ['At the start of every session', 'Never', 'Only when you type its name', 'Once a day'], 0, 'Unconditional.', 'It loads at launch like .claude/CLAUDE.md.'),
    quiz('e', 'Where do personal rules for all your projects go?', ['~/.claude/rules/', '.claude/rules/', 'CLAUDE.local.md', '.mcp.json'], 0, 'Home folder.', 'User rules apply to every project on your machine.'),
    quiz('m', 'Which pattern matches every Markdown file in any folder?', ['**/*.md', '*.md', 'md/**', '*.markdown'], 0, 'Two stars.', '*.md matches only the root folder.'),
    quiz('m', 'Which front matter field do rules read?', ['paths', 'name', 'description', 'model'], 0, 'Only one.', 'Any other field is ignored without an error.'),
    quiz('m', 'When does a path rule load?', ['When Claude reads, writes or edits a matching file', 'At launch', 'When you open the folder in your editor', 'After /compact'], 0, 'A file is touched.', 'Matching happens on Read, Write and Edit, and on single file reads like cat.'),
    quiz('h', 'A rule\'s YAML does not parse. What happens?', ['It loads as if it had no paths', 'Claude Code crashes', 'The rule is deleted', 'It never loads'], 0, 'Front matter ignored.', 'Run claude --debug to see the parse error.'),
    quiz('h', 'After /compact, what happens to a path rule that had loaded?', ['It is summarised away until a matching file is touched again', 'It stays word for word', 'It is deleted from disk', 'It turns into CLAUDE.md'], 0, 'It joined as a message.', 'Root CLAUDE.md and rules without paths are reloaded, path rules return on demand.'),
    quiz('x', 'A user rule and a project rule disagree. What happens?', ['Claude may follow either, so keep them consistent', 'The project rule always wins', 'The user rule always wins', 'Both are dropped'], 0, 'Neither overrides.', 'Both load, user rules first, so contradictions are risky.'),
    quiz('x', 'Your team has a 9 step release checklist used once a week. Where should it go?', ['A skill', 'A rule without paths', 'CLAUDE.md', 'A path rule for every file'], 0, 'Procedure, used sometimes.', 'Skills load their steps only when used.'),
]

CALC = [
    calc('e', 'In the example project, how many rules load at launch?', '2', 'Rules without paths.', ['code-style.md and security.md.']),
    calc('e', 'How many expanded patterns does src/*.{ts,tsx} become?', '2', 'One per option in the braces.', ['src/*.ts and src/*.tsx.']),
    calc('m', 'How many patterns does {a,b}/{c,d}/*.{ts,tsx} expand to?', '8', 'Multiply the options.', ['<span class="eq">2 × 2 × 2 = 8</span>']),
    calc('m', 'Claude edits tests/cart.test.ts. How many rules are loaded in total now?', '3', 'Launch rules plus matches.', ['2 at launch plus testing.md.', '<span class="eq">2 + 1 = 3</span>']),
    calc('h', 'An API rule is 600 tokens. Front end developers make 80 requests a day and never touch API files. How many tokens a day does the paths field save them?', '48000', 'It never loads for them.', ['<span class="eq">600 × 80 = 48,000</span>'], alt=['48,000']),
    calc('x', 'What is the expanded pattern budget for one rule\'s paths list?', '1000', 'From the docs.', ['1,000 expanded patterns and 4 MiB per rule.'], alt=['1,000']),
]

EX = [
    ex('has-paths', 'e', 'Does it have paths?', '<p>Write <code>hasPaths(text)</code>. Return true when the text starts with a front matter block (<code>---</code> on the first line, a closing <code>---</code> later) that contains a line starting with <code>paths:</code>.</p>',
       'function hasPaths(text) {\n  \n}\n',
       [('hasPaths("---\\npaths:\\n  - \\"src/**\\"\\n---\\n# API")', True), ('hasPaths("# Style\\n- tabs")', False), ('hasPaths("---\\nname: x\\n---\\nhi")', False)],
       'function hasPaths(text) {\n  const m = text.match(/^---\\n([\\s\\S]*?)\\n---/);\n  return !!m && /^paths:/m.test(m[1]);\n}',
       hint='Match the block with a regular expression, then look inside it.', why='Knowing whether a rule is conditional tells you when it costs context.'),
    ex('ext-match', 'm', 'Match by extension', '<p>Write <code>matchesExt(file, exts)</code>. <code>exts</code> is a list like <code>["ts", "tsx"]</code>. Return true when the file name ends with a dot and one of them.</p>',
       'function matchesExt(file, exts) {\n  \n}\n',
       [('matchesExt("src/a.tsx", ["ts", "tsx"])', True), ('matchesExt("src/a.js", ["ts"])', False), ('matchesExt("notes.ts.md", ["ts"])', False)],
       'function matchesExt(file, exts) {\n  return exts.some(e => file.endsWith("." + e));\n}',
       hint='<code>endsWith</code> with the dot included.', why='This is what a brace pattern like <code>*.{ts,tsx}</code> does for the file name part.'),
    ex('where-goes', 'h', 'Where does this instruction go?', '<p>Write <code>placeFor(item)</code>. <code>item</code> has <code>always</code>, <code>forPaths</code>, <code>steps</code> and <code>mustNever</code>. Return <code>"hook"</code> if <code>mustNever</code>, else <code>"skill"</code> if <code>steps</code> is more than 3, else <code>"path rule"</code> if <code>forPaths</code>, else <code>"CLAUDE.md"</code>.</p>',
       'function placeFor(item) {\n  \n}\n',
       [('placeFor({ mustNever: true })', 'hook'), ('placeFor({ steps: 9 })', 'skill'), ('placeFor({ forPaths: true, steps: 1 })', 'path rule'), ('placeFor({ always: true })', 'CLAUDE.md')],
       'function placeFor(item) {\n  if (item.mustNever) return "hook";\n  if ((item.steps ?? 0) > 3) return "skill";\n  if (item.forPaths) return "path rule";\n  return "CLAUDE.md";\n}',
       hint='Check the strongest need first.', why='Putting each instruction in the right place keeps context small and rules reliable.'),
]

T = {
    'slug': 'claude-rules', 'title': 'Rules: The .claude/rules Folder and Path Rules', 'short': 'Rules', 'emoji': '📏', 'module': MODULE, 'minutes': 13,
    'lead': 'Why there is no rules.md, how to build a .claude/rules/ folder step by step, path rules that load only for matching files, ready to copy rules for code, content and contracts, personal and shared rules, and how to choose between rules, CLAUDE.md, skills and hooks.',
    'plain': 'Rules are small notes for Claude, one topic per note, kept in a folder. Some notes are always read. Others are read only when Claude opens certain files.',
    'desc': 'Claude Code rules explained: the .claude/rules folder, the paths frontmatter field, glob patterns, user rules, symlinks, and rules versus CLAUDE.md, skills and hooks.',
    'summary': 'The name check (no rules.md, the real .claude/rules/ folder), creating rule files step by step, path rules with the paths field and glob patterns, a run showing which rules load for which file, ready to copy rules for APIs, tests, blog posts and contracts, personal rules in ~/.claude/rules/, sharing rules with symlinks, choosing between rules, CLAUDE.md, skills and hooks, and debugging rules.',
    'keywords': ['rules', 'rules.md', '.claude/rules', 'paths', 'path rules', 'glob', 'frontmatter', 'user rules', 'symlink', 'CLAUDE.md vs rules'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
