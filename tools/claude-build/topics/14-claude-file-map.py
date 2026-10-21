# Chapter 14: capstone. Which file holds what, the real names behind common wrong ones, a router that decides
# where an instruction belongs, a complete project setup checked for real, and a homework helper built step by step.
from ckit import part, run, test, show, md, cli, prompt, js_, say, quiz, calc, ex, panel

MODULE = ('🏁', 'Capstone', 'claude-capstone', 'Put it all together: the full file map and a complete setup built step by step.')

ROUTER = r'''
// where.mjs: decides which file an instruction belongs in, using the rules from this subject.
function where(note) {
  const n = note.toLowerCase();
  if (/\b(allow|deny|don't let|never let)\b/.test(n))
    return ".claude/settings.json permissions (allow, ask or deny a tool call)";
  if (/\balways\b.*\b(run|after|before)\b|every time .* (edit|commit)/.test(n))
    return ".claude/settings.json hook (it must happen every time, not just be asked)";
  if (/\b(api key|token|password|secret)\b/.test(n))
    return "an environment variable or a secret store, never a Markdown file";
  if (/\b(jira|github|database|calendar|slack|drive)\b/.test(n))
    return ".mcp.json (an MCP server gives Claude that connection)";
  if (/\b(only when|files in|inside|for \*\.)/.test(n))
    return ".claude/rules/<topic>.md with paths: (loads only for matching files)";
  if (/\b(step by step|checklist|procedure|how to (do|write|make)|every month)\b/.test(n))
    return ".claude/skills/<name>/SKILL.md (a procedure that loads when needed)";
  if (/\b(reviewer|researcher|specialist|separate helper)\b/.test(n))
    return ".claude/agents/<name>.md (a subagent with its own context)";
  if (/\b(tone|explain like|talk to me|answer style)\b/.test(n))
    return "~/.claude/output-styles/<name>.md (how every answer sounds)";
  if (/\b(my |personal|local url|my test account)\b/.test(n))
    return "CLAUDE.local.md (your private notes for this project)";
  return "CLAUDE.md (a short fact or rule the whole team needs in every session)";
}

const notes = [
  "Run tests with npm test, build with npm run build",
  "Always run prettier after every edit",
  "Never let Claude run rm -rf or git push --force",
  "API key for the payment sandbox is sk_test_123",
  "Let Claude read our Jira tickets",
  "React components inside src/components use hooks only, files in src/components",
  "The monthly invoice report: step by step checklist with totals",
  "A security reviewer that checks every change",
  "Explain like I am 10 and use cricket examples",
  "My local URL is http://localhost:4100",
  "Prices are stored in paise as integers",
];
for (const note of notes) console.log(`• ${note}\n    → ${where(note)}`);
'''

CHECK = r'''
// check-setup.mjs: walks a project and reports every Claude file it finds, with the problems a reviewer would flag.
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join } from "node:path";

const walk = d => readdirSync(d).flatMap(f => { const p = join(d, f); return statSync(p).isDirectory() ? walk(p) : [p]; });
const files = walk(".").map(f => f.replace(/^\.\//, "")).filter(f => !f.startsWith("node_modules") && f !== "check-setup.mjs");
const front = t => Object.fromEntries([...(t.match(/^---\n([\s\S]*?)\n---/)?.[1] ?? "").matchAll(/^([\w-]+):[ \t]*(.*)$/gm)].map(m => [m[1], m[2]]));
let problems = 0;
const flag = msg => { problems++; console.log("   ✘ " + msg); };

for (const f of files.sort()) {
  const text = readFileSync(f, "utf8");
  const lines = text.split("\n").length;
  if (f === "CLAUDE.md") { console.log(`📘 ${f} (${lines} lines): project memory`); if (lines > 200) flag("over 200 lines, move detail into rules or skills"); }
  else if (f === "CLAUDE.local.md") console.log(`🔒 ${f}: private notes`);
  else if (f.startsWith(".claude/rules/")) console.log(`📏 ${f}: rule for ${[...(text.match(/^---\n([\s\S]*?)\n---/)?.[1] ?? "").matchAll(/^\s+- "?([^"\n]+)"?$/gm)].map(m => m[1]).join(", ") || "every file"}`);
  else if (f.endsWith("/SKILL.md")) { const m = front(text); console.log(`🧰 ${f}: skill /${m.name}`); if (!m.description) flag("skill has no description"); }
  else if (f.startsWith(".claude/agents/")) { const m = front(text); console.log(`🤖 ${f}: agent ${m.name} (tools: ${m.tools ?? "all"})`); }
  else if (f === ".claude/settings.json") {
    const s = JSON.parse(text);
    console.log(`⚙️  ${f}: ${s.permissions?.allow?.length ?? 0} allow, ${s.permissions?.deny?.length ?? 0} deny, hooks on ${Object.keys(s.hooks ?? {}).join(", ") || "nothing"}`);
  }
  else if (f === ".mcp.json") {
    const m = JSON.parse(text).mcpServers;
    console.log(`🔌 ${f}: ${Object.keys(m).join(", ")}`);
    if (/sk[-_][A-Za-z0-9_-]{8,}|Bearer [A-Za-z0-9]{8,}/.test(text)) flag("a real key is written in .mcp.json, use ${VAR}");
  }
  else if (f.startsWith(".claude/hooks/")) console.log(`🪝 ${f}: hook script`);
  else if (f === ".gitignore") { if (!text.includes("CLAUDE.local.md") && files.includes("CLAUDE.local.md")) flag(".gitignore does not list CLAUDE.local.md"); }
}
console.log(problems ? `\n${problems} problem(s) to fix` : "\n✔ setup looks right");
'''

SETUP = {
    'CLAUDE.md': '''# GreenLeaf shop

Online plant shop. Next.js front end, Node API, PostgreSQL.

## Commands
- Test one file: `npx vitest run path/to/file.test.ts`
- Before a commit: `npm run lint && npm run typecheck`

## Rules
- Prices are stored in paise as integers. Format with `formatINR()`.
- IMPORTANT: never edit `src/generated/`. Run `npm run codegen`.
''',
    'CLAUDE.local.md': '- My dev server runs on port 4100\n- Test login: asha@test.local\n',
    '.gitignore': 'node_modules/\n.env.local\n',
    '.claude/rules/api.md': '---\npaths:\n  - "src/api/**/*.ts"\n---\n\n- Validate every request body with zod.\n- Return errors as { error: { code, message } }.\n',
    '.claude/skills/release-notes/SKILL.md': '---\nname: release-notes\ndescription: Write customer friendly release notes from git log since the last tag.\ndisable-model-invocation: true\n---\n\n1. Find the last tag.\n2. Group commits into Added, Changed, Fixed.\n',
    '.claude/agents/code-reviewer.md': '---\nname: code-reviewer\ndescription: Reviews changed code before a commit.\ntools: Read, Grep, Glob, Bash\n---\n\nRun git diff and list Must fix, Should fix, Nice to have.\n',
    '.claude/settings.json': '''{
  "permissions": {
    "allow": ["Bash(npm run lint)", "Bash(npm run test *)", "mcp__claude-code-docs__*"],
    "deny": ["Read(./.env*)", "Bash(git push --force *)"]
  },
  "hooks": {
    "PostToolUse": [{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "node .claude/hooks/format.mjs" }] }]
  }
}
''',
    '.claude/hooks/format.mjs': '// reads the edited file path from stdin and formats it\n',
    '.mcp.json': '''{
  "mcpServers": {
    "claude-code-docs": { "type": "http", "url": "https://code.claude.com/docs/mcp" },
    "payments": { "type": "http", "url": "https://pay.example.com/mcp", "headers": { "Authorization": "Bearer sk_live_abcdef123456" } }
  }
}
''',
    'check-setup.mjs': CHECK,
}

KID_CLAUDE = '''
# Riya's homework helper

Riya is 10 and in class 5. She is learning maths, science and English.

## How to help
- Never give the final answer first. Ask what she already knows, then give one hint.
- Use short sentences and examples from cricket, cooking and Bengaluru.
- After she answers, say what she did well, then what to fix.
- If she is stuck after three hints, show the answer step by step and ask her to try a similar one.

## Safety
- Do not ask for her full name, school, address or photos.
- For anything about health or feeling unsafe, tell her to talk to a parent or teacher.
'''

KID_SKILL = '''
---
name: quiz-me
description: Make a 5 question practice quiz on a topic for a class 5 student, then mark the answers.
---

1. Ask which topic, if it is not given: $ARGUMENTS
2. Write 5 questions, easiest first. Number them.
3. Wait for all 5 answers.
4. Mark each with ✅ or ❌, explain each ❌ in one sentence, and give a score out of 5.
5. Finish with one star sticker line, for example "⭐ Fractions champion!"
'''

CODES = {
    'map': show('''
my-project/
├── CLAUDE.md                     facts and rules for everyone, every session (under 200 lines)
├── CLAUDE.local.md               your private notes for this project (in .gitignore)
├── .mcp.json                     MCP servers the team shares
├── .claude/
│   ├── settings.json             permissions, hooks, model, env (shared)
│   ├── settings.local.json       your own overrides (not committed)
│   ├── rules/
│   │   └── api.md                rules that load only for matching paths
│   ├── skills/
│   │   └── release-notes/
│   │       └── SKILL.md          a procedure, called as /release-notes
│   ├── agents/
│   │   └── code-reviewer.md      a subagent with its own tools and prompt
│   ├── hooks/
│   │   └── format.mjs            a script a hook runs
│   └── output-styles/
│       └── teach-me.md           how answers sound
└── .github/workflows/claude.yml  Claude in GitHub Actions

~/.claude/CLAUDE.md               your rules in every project
~/.claude/settings.json           your settings in every project
~/.claude.json                    your local and user scoped MCP servers
''', 'Every Claude file in one picture', lang='text', note='📂 The full map'),
    'router': run(ROUTER, 'Where does this instruction go?'),
    'setup-check': test(SETUP, 'node check-setup.mjs', 'Check a complete project setup', show=['check-setup.mjs'],
                        badge='▶ Reads every Claude file in a real project folder'),
    'kid-md': md(KID_CLAUDE, 'homework-helper/CLAUDE.md'),
    'kid-skill': md(KID_SKILL, 'homework-helper/.claude/skills/quiz-me/SKILL.md'),
    'kid-steps': cli('''
mkdir homework-helper && cd homework-helper
# save CLAUDE.md and the quiz-me skill from this page into the folder
claude
> /output-style learning
> /quiz-me fractions
''', 'Start the helper'),
    'kid-chat': prompt('''
Riya: what is 3/4 + 1/8
Claude: Good question! What do you need first when you add fractions with different bottoms?
Riya: the same bottom number?
Claude: Yes! Can you turn 3/4 into eighths? Think of a roti cut into 8 pieces.
''', 'What a session looks like', result='The rules in CLAUDE.md make Claude give hints, not answers, in every session, with no need to repeat them.'),
    'ai-project': prompt('''
Project instructions (claude.ai, Projects, then Instructions):
  You help Riya, age 10, with class 5 homework. Give hints, not answers.
  Use short sentences and examples from cricket and cooking.

Project knowledge (upload): class-5-syllabus.pdf, maths-textbook-ch4.pdf
''', 'No terminal? The same helper as a claude.ai Project', result='Project instructions play the role of CLAUDE.md, and knowledge files are what Claude can read. Every chat in the project follows them.'),
}

PARTS = [
    part('map', '🗺️', 'Every file, and what goes in it', '''
[[map]]
<div class="tw"><table class="jt"><tr><th>File</th><th>Put in it</th><th>Keep out of it</th></tr>
<tr><td><code>CLAUDE.md</code></td><td>build and test commands, code style, project facts, "IMPORTANT" rules</td><td>long procedures, secrets, things a linter already enforces</td></tr>
<tr><td><code>CLAUDE.local.md</code></td><td>your ports, test accounts, personal shortcuts</td><td>anything the team needs</td></tr>
<tr><td><code>.claude/rules/*.md</code></td><td>rules for one area, with <code>paths:</code></td><td>rules for every file (those go in CLAUDE.md)</td></tr>
<tr><td><code>.claude/skills/&lt;name&gt;/SKILL.md</code></td><td>a repeatable procedure, with scripts and templates beside it</td><td>always-on facts</td></tr>
<tr><td><code>.claude/agents/&lt;name&gt;.md</code></td><td>a specialist: description, tools, model, system prompt</td><td>project facts (it reads CLAUDE.md already)</td></tr>
<tr><td><code>.claude/settings.json</code></td><td>permissions, hooks, model, env</td><td>instructions in words</td></tr>
<tr><td><code>.mcp.json</code></td><td>MCP servers, with <code>${VARS}</code> for keys</td><td>real keys</td></tr>
<tr><td>output style</td><td>tone, role and answer format</td><td>project rules</td></tr>
<tr><td><code>plugin.json</code></td><td>name, description, version of a bundle</td><td>skills or agents (they sit beside it)</td></tr></table></div>
''', easy=True, files=['CLAUDE.md', 'CLAUDE.local.md', '.claude/rules/', '.claude/skills/', '.claude/agents/', '.claude/settings.json', '.mcp.json'], kw=['file map', 'which file', 'what goes where']),
    part('names', '🔎', 'The real names behind the names people use', '''
<div class="tw"><table class="jt"><tr><th>People say</th><th>What really exists</th></tr>
<tr><td>"rules.md"</td><td>a folder: <code>.claude/rules/</code>, one Markdown file per topic, optional <code>paths:</code></td></tr>
<tr><td>"skills.md"</td><td><code>SKILL.md</code> inside its own folder: <code>.claude/skills/&lt;name&gt;/SKILL.md</code></td></tr>
<tr><td>"agents.md"</td><td>one file per agent in <code>.claude/agents/</code>. A root <code>AGENTS.md</code> is shared instructions, read only when there is no CLAUDE.md</td></tr>
<tr><td>"prompt file"</td><td>there is no prompt file Claude reads. Save a reusable prompt as a skill (<code>/name</code>), a legacy command in <code>.claude/commands/</code>, or an MCP prompt</td></tr>
<tr><td>"mcp.json"</td><td><code>.mcp.json</code> at the project root, or <code>~/.claude.json</code> for local and user scope</td></tr>
<tr><td>"memory.md"</td><td>auto memory's <code>MEMORY.md</code> index, which Claude writes itself. Your own memory file is <code>CLAUDE.md</code></td></tr>
<tr><td>"system prompt file"</td><td>CLAUDE.md for Claude Code, Project instructions on claude.ai, the <code>system</code> field in the API</td></tr></table></div>
''', easy=True, kw=['rules.md', 'skills.md', 'agents.md', 'prompt file', 'name check']),
    part('decide', '🧭', 'Decide where an instruction belongs', '''
<p>Ask four questions in order. <b>Must it happen every time?</b> Use a hook. <b>Is it about what Claude may do?</b> Use permissions. <b>Is it a procedure or only for some files?</b> Use a skill or a path rule. <b>Otherwise</b> it is a short line in <code>CLAUDE.md</code>.</p>
[[router]]
''', easy=True, kw=['decision guide', 'hook or CLAUDE.md', 'skill or rule']),
    part('setup', '🏗️', 'A complete project, checked for real', '''
<p>Here is a whole shop project with every kind of Claude file. The checker reads each one and flags what a careful reviewer would.</p>
[[setup-check]]
<div class="scenario"><b>🔧 Fix the two problems</b>Change the payments header to <code>"Bearer ${PAYMENTS_TOKEN}"</code> and add <code>CLAUDE.local.md</code> to <code>.gitignore</code>. Run the checker again and it reports a clean setup.</div>
''', files=['CLAUDE.md', '.claude/settings.json', '.mcp.json', '.claude/rules/api.md'], kw=['project setup', 'full example', 'checker']),
    part('kid', '🧒', 'Build a homework helper, step by step', '''
<p>This is small enough for a child and a parent to build together in 15 minutes.</p>
<ol class="steps"><li>Make a folder called <code>homework-helper</code>.</li><li>Save the <code>CLAUDE.md</code> below in it. These are the rules Claude follows every time.</li><li>Save the <code>quiz-me</code> skill.</li><li>Open Claude Code in the folder and pick the Learning output style.</li><li>Type <code>/quiz-me fractions</code>.</li></ol>
[[kid-md]]
[[kid-skill]]
[[kid-steps]]
[[kid-chat]]
[[ai-project]]
''', easy=True, files=['homework-helper/CLAUDE.md', 'homework-helper/.claude/skills/quiz-me/SKILL.md'], kw=['homework helper', 'kids', 'claude.ai Projects', 'beginner build']),
    part('next', '🚀', 'Your next level, one week at a time', '''
<div class="tw"><table class="jt"><tr><th>Week</th><th>Do this</th><th>You will have</th></tr>
<tr><td>1</td><td>Run <code>/init</code>, trim CLAUDE.md under 200 lines, add two path rules</td><td>Claude that knows your project</td></tr>
<tr><td>2</td><td>Turn your most repeated request into a skill</td><td>one command for a 10 minute job</td></tr>
<tr><td>3</td><td>Add a format hook and deny rules for secrets</td><td>guarantees, not hopes</td></tr>
<tr><td>4</td><td>Connect one MCP server you use daily</td><td>Claude working in your real tools</td></tr>
<tr><td>5</td><td>Write a reviewer subagent and a <code>claude -p</code> recipe</td><td>checks and automation</td></tr>
<tr><td>6</td><td>Build a small agent with the API for one business task</td><td>your own AI tool</td></tr></table></div>
''', easy=True, kw=['learning path', 'next steps', 'practice plan']),
]

INFO = {'title': 'Which file holds what', 'panels': [
    panel([['e', '📘'], ['t', 'CLAUDE.md', {'b': 1}]], 'Always', 'Short facts and rules.', 'Under 200 lines.'),
    panel([['e', '🧰'], ['t', 'SKILL.md', {'b': 1}]], 'When needed', 'Procedures and scripts.', 'Rules with paths for some files.'),
    panel([['e', '⚙️'], ['t', 'settings.json', {'b': 1}]], 'Guaranteed', 'Permissions and hooks.', 'Code, not requests.'),
    panel([['e', '🔌'], ['t', '.mcp.json', {'b': 1}]], 'Connected', 'Other apps and data.', 'Keys in ${VARS}.')],
    'remember': 'Every time: hook. Allowed or not: permissions. Sometimes: skill or rule. Always true: CLAUDE.md.'}

REAL = [
    ['🏬', 'A retail tech team', 'Reviewed their setup with this map, moved a 900 line CLAUDE.md into six path rules and three skills, and cut every session\'s start by 14,000 tokens.'],
    ['👨‍👩‍👧', 'A parent', 'Built the homework helper on a family laptop. The hint first rule in CLAUDE.md means the child still does the thinking.'],
    ['🧾', 'A small accounting firm', 'Shares one plugin with an invoice skill, a GST checker agent and a Drive MCP server across all twelve laptops.'],
]

SAY = [
    say('top', 'Welcome', 'This capstone puts everything together: which file holds what, a full project setup, and a homework helper anyone can build.',
        'यह अंतिम अध्याय सब जोड़ता है: कौन सी file क्या रखती है।',
        'ಈ ಕೊನೆಯ ಅಧ್ಯಾಯ ಎಲ್ಲವನ್ನೂ ಜೋಡಿಸುತ್ತದೆ.',
        'ଏହି ଶେଷ ଅଧ୍ୟାୟ ସବୁ ଯୋଡେ।',
        'يجمع هذا الفصل الختامي كل شيء: أي ملف يحمل ماذا.',
        'Dieses Abschlusskapitel bringt alles zusammen.'),
    say('map', 'File map', 'CLAUDE.md for always-true facts, rules for some files, skills for procedures, settings for guarantees, and dot mcp dot json for connections.',
        'CLAUDE.md हमेशा के तथ्य, rules कुछ files, skills प्रक्रियाएँ।',
        'CLAUDE.md ಸದಾ ಸತ್ಯ, rules ಕೆಲವು files, skills ಪ್ರಕ್ರಿಯೆ.',
        'CLAUDE.md ସର୍ବଦା ସତ୍ୟ, rules କିଛି files, skills ପ୍ରକ୍ରିୟା।',
        'CLAUDE.md للحقائق الدائمة والقواعد لبعض الملفات والمهارات للإجراءات.',
        'CLAUDE.md für Fakten, Regeln für bestimmte Dateien, Skills für Abläufe.'),
    say('names', 'Real names', 'There is no rules dot md or prompt file. Rules are a folder, skills live in their own folder, and agents are one file each.',
        'rules.md या prompt file नहीं होती। Rules एक folder है।',
        'rules.md ಅಥವಾ prompt file ಇಲ್ಲ. Rules ಒಂದು folder.',
        'rules.md ବା prompt file ନାହିଁ। Rules ଏକ folder.',
        'لا يوجد rules.md ولا ملف موجّه. القواعد مجلد.',
        'Es gibt keine rules.md und keine Prompt-Datei. Regeln sind ein Ordner.'),
    say('decide', 'Decide', 'Every time means a hook. Permission means settings. Procedures mean skills. Everything else is a short line in CLAUDE.md.',
        'हर बार: hook। अनुमति: settings। प्रक्रिया: skill।',
        'ಪ್ರತಿಬಾರಿ: hook. ಅನುಮತಿ: settings. ಪ್ರಕ್ರಿಯೆ: skill.',
        'ପ୍ରତିଥର: hook। ଅନୁମତି: settings। ପ୍ରକ୍ରିୟା: skill।',
        'كل مرة: خطاف. الإذن: الإعدادات. الإجراء: مهارة.',
        'Jedes Mal: Hook. Erlaubnis: Settings. Ablauf: Skill.'),
    say('setup', 'Full setup', 'The checker reads every Claude file in a real project and finds a key written in plain text and a missing gitignore line.',
        'Checker हर file पढ़ता है और दो समस्याएँ पाता है।',
        'Checker ಪ್ರತಿ file ಓದಿ ಎರಡು ಸಮಸ್ಯೆ ಕಂಡುಹಿಡಿಯುತ್ತದೆ.',
        'Checker ପ୍ରତି file ପଢି ଦୁଇଟି ସମସ୍ୟା ପାଏ।',
        'يقرأ المدقق كل ملف ويجد مشكلتين.',
        'Der Prüfer liest jede Datei und findet zwei Probleme.'),
    say('kid', 'Homework helper', 'A CLAUDE.md with hint first rules and a quiz skill make a safe helper a child can use.',
        'Hint वाले नियम और quiz skill से बच्चों का helper बनता है।',
        'Hint ನಿಯಮ ಮತ್ತು quiz skill ಮಕ್ಕಳ helper ಮಾಡುತ್ತವೆ.',
        'Hint ନିୟମ ଓ quiz skill ପିଲାଙ୍କ helper ତିଆରି କରେ।',
        'قواعد التلميح ومهارة الاختبار تصنعان مساعدًا آمنًا للطفل.',
        'Hinweisregeln und ein Quiz-Skill ergeben einen sicheren Helfer für Kinder.'),
    say('next', 'Next steps', 'Take one step a week: memory, a skill, hooks, MCP, automation, then your own agent.',
        'हर हफ्ते एक कदम: memory, skill, hooks, MCP, agent।',
        'ಪ್ರತಿ ವಾರ ಒಂದು ಹೆಜ್ಜೆ.',
        'ପ୍ରତି ସପ୍ତାହ ଗୋଟିଏ ପାଦ।',
        'خطوة كل أسبوع: الذاكرة ثم مهارة ثم خطافات ثم وكيل.',
        'Jede Woche ein Schritt: Gedächtnis, Skill, Hooks, MCP, Agent.'),
    say('practice', 'Practice', 'Practise placing instructions in the right file.',
        'निर्देशों को सही file में रखने का अभ्यास।',
        'ಸರಿಯಾದ file ಆಯ್ಕೆ ಅಭ್ಯಾಸ.',
        'ଠିକ୍ file ବାଛିବା ଅଭ୍ୟାସ।',
        'تدرّب على وضع التعليمات في الملف الصحيح.',
        'Übe, Anweisungen in die richtige Datei zu legen.'),
]

QUIZ = [
    quiz('e', '"Always format code after an edit." Where does it go?', ['A hook in .claude/settings.json', 'CLAUDE.md', 'A skill', '.mcp.json'], 0, 'Every time.', 'Hooks run every time, instructions can be missed.'),
    quiz('e', 'Where do the build and test commands go?', ['CLAUDE.md', '.mcp.json', 'An output style', 'plugin.json'], 0, 'Always needed.', 'Claude needs them in every session.'),
    quiz('e', 'Where is a skill file saved?', ['.claude/skills/<name>/SKILL.md', '.claude/skills.md', 'skills.md at the root', 'CLAUDE.md'], 0, 'Own folder.', 'Each skill has its own folder.'),
    quiz('m', 'Is there a rules.md file?', ['No, rules are files in .claude/rules/', 'Yes, at the root', 'Yes, in ~/.claude', 'Only on Windows'], 0, 'A folder.', 'One Markdown file per topic.'),
    quiz('m', 'Where do you save a prompt you use every week?', ['As a skill, then call /name', 'In prompt.md', 'In .mcp.json', 'In settings.json'], 0, 'Reusable.', 'Skills are saved prompts and procedures.'),
    quiz('m', 'Your personal dev port belongs in...', ['CLAUDE.local.md', 'CLAUDE.md', '.claude/rules/port.md', 'plugin.json'], 0, 'Only you.', 'Keep it out of the shared file.'),
    quiz('h', 'A rule for files in src/api/ only goes in...', ['.claude/rules/api.md with paths:', 'CLAUDE.md', 'a hook', '.mcp.json'], 0, 'Path scoped.', 'It loads only when matching files are touched.'),
    quiz('h', 'What did the setup checker flag in .mcp.json?', ['A real key in a header', 'A missing type', 'Too many servers', 'Nothing'], 0, 'Secrets.', 'Use ${VAR} instead.'),
    quiz('x', 'On claude.ai without a terminal, what plays the role of CLAUDE.md?', ['Project instructions', 'A chat title', 'Styles only', 'Nothing'], 0, 'Projects.', 'Every chat in the project follows them.'),
    quiz('x', '"Never let Claude push with --force" is best as...', ['A deny rule in permissions', 'A line in CLAUDE.md', 'An output style', 'A skill'], 0, 'Enforced.', 'Deny rules block the call itself.'),
]

CALC = [
    calc('e', 'In the router run, how many notes went to CLAUDE.md?', '2', 'Count the CLAUDE.md lines.', ['The commands note and the paise note.']),
    calc('e', 'How many problems did the setup checker find?', '2', 'Read the last line.', ['The key in .mcp.json and the missing .gitignore line.']),
    calc('m', 'A CLAUDE.md of 900 lines at about 12 tokens a line. Tokens loaded at every start?', '10800', 'Multiply.', ['<span class="eq">900 × 12 = 10,800</span>'], alt=['10,800']),
    calc('m', 'Cut to 180 lines. Tokens saved per session?', '8640', 'Lines removed × 12.', ['<span class="eq">(900 − 180) × 12 = 8,640</span>'], alt=['8,640']),
    calc('h', 'A team runs 40 sessions a day. Tokens saved per day?', '345600', 'Multiply.', ['<span class="eq">8,640 × 40 = 345,600</span>'], alt=['345,600']),
    calc('x', 'At $4 per million input tokens, dollars saved per 22 day month?', '30.41', 'Tokens × days × price.', ['<span class="eq">345,600 × 22 × 4 ÷ 10⁶ ≈ 30.41</span>'], alt=['$30.41', '30.4']),
]

EX = [
    ex('kind', 'e', 'Hook or CLAUDE.md?', '<p>Write <code>kind(note)</code> that returns <code>"hook"</code> when the note contains <code>"always"</code> or <code>"every time"</code> (any case), and <code>"claude-md"</code> otherwise.</p>',
       'function kind(note) {\n  \n}\n',
       [('kind("Always run prettier")', 'hook'), ('kind("Run lint every time you edit")', 'hook'), ('kind("Prices are in paise")', 'claude-md')],
       'function kind(note) {\n  const n = note.toLowerCase();\n  return n.includes("always") || n.includes("every time") ? "hook" : "claude-md";\n}',
       hint='Lower case first, then includes.', why='The first question is always: must it happen every time?'),
    ex('skill-path', 'm', 'Skill path', '<p>Write <code>skillPath(name, scope)</code> that returns <code>.claude/skills/&lt;name&gt;/SKILL.md</code> for <code>"project"</code> and <code>~/.claude/skills/&lt;name&gt;/SKILL.md</code> for <code>"user"</code>.</p>',
       'function skillPath(name, scope) {\n  \n}\n',
       [('skillPath("quiz-me", "project")', '.claude/skills/quiz-me/SKILL.md'), ('skillPath("quiz-me", "user")', '~/.claude/skills/quiz-me/SKILL.md')],
       'function skillPath(name, scope) {\n  return (scope === "user" ? "~/" : "") + `.claude/skills/${name}/SKILL.md`;\n}',
       hint='Only the start changes.', why='The folder name becomes the command.'),
    ex('has-secret', 'h', 'Find a secret', '<p>Write <code>hasSecret(text)</code> that returns true when the text contains <code>sk-</code> or <code>sk_</code> followed by at least 8 letters or digits, or <code>Bearer </code> followed by at least 8 letters or digits. <code>Bearer ${TOKEN}</code> is fine.</p>',
       'function hasSecret(text) {\n  \n}\n',
       [('hasSecret("Bearer sk_live_abcdef123456")', True), ('hasSecret("Bearer ${PAYMENTS_TOKEN}")', False), ('hasSecret("key sk-ant-abcdefgh99")', True), ('hasSecret("no keys here")', False)],
       'function hasSecret(text) {\n  return /sk[-_][A-Za-z0-9_-]{8,}|Bearer [A-Za-z0-9]{8,}/.test(text);\n}',
       hint='One regular expression with two alternatives.', why='Keys in committed files are the most common and most costly mistake.'),
]

T = {
    'slug': 'claude-file-map', 'title': 'Capstone: Which File Holds What', 'short': 'File map capstone', 'emoji': '🗺️', 'module': MODULE, 'minutes': 16,
    'lead': 'The full map of Claude files and exactly what goes in each, the real names behind rules.md, skills.md, agents.md and the "prompt file", a router that places any instruction, a complete project checked for real, a homework helper a child can build, and a six week path to the next level.',
    'plain': 'Each Claude file has one job. This chapter lists every file, says what to write in it, and shows a whole project that uses them all.',
    'desc': 'Which Claude file holds what: CLAUDE.md, CLAUDE.local.md, .claude/rules, SKILL.md, .claude/agents, settings.json, hooks, .mcp.json, output styles and plugin.json, with a full project example and a homework helper build.',
    'summary': 'The complete Claude file map with what goes in and stays out of each file, the real names behind common wrong ones, a router run on eleven example instructions, a full project setup with a checker that finds two problems, a homework helper with CLAUDE.md, a quiz skill and a claude.ai Project version, and a six week practice path.',
    'keywords': ['file map', 'CLAUDE.md', 'rules', 'SKILL.md', 'agents', 'settings.json', '.mcp.json', 'what goes where', 'homework helper', 'capstone'],
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
