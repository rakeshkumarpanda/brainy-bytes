# Chapter 14: capstone. Which file holds what, the real names behind common wrong ones, a table that shows
# where an instruction belongs, a complete project setup to review, and a homework helper built step by step.
from ckit import part, show, md, cli, prompt, js_, say, quiz, calc, panel

MODULE = ('🏁', 'Capstone', 'claude-capstone', 'Put it all together: the full file map and a complete setup built step by step.')

SETUP_TREE = '''
greenleaf-shop/
├── CLAUDE.md                          📘 project memory, 12 lines: commands and the paise rule
├── CLAUDE.local.md                    🔒 private notes: my dev port and test login
├── .gitignore                         .venv/ and .env.local only
├── .mcp.json                          🔌 claude-code-docs and payments
└── .claude/
    ├── settings.json                  ⚙️ 3 allow, 2 deny, a PostToolUse hook
    ├── hooks/format.py                🪝 formats each edited file
    ├── rules/api.md                   📏 rule for app/api/**/*.py
    ├── skills/release-notes/SKILL.md  🧰 skill /release-notes
    └── agents/code-reviewer.md        🤖 agent code-reviewer (tools: Read, Grep, Glob, Bash)
'''

SETUP_CLAUDE = '''
# GreenLeaf shop

Online plant shop. FastAPI back end, PostgreSQL, pytest.

## Commands
- Test one file: `pytest tests/test_cart.py -q`
- Before a commit: `ruff check . && mypy app`

## Rules
- Prices are stored in paise as integers. Format with `format_inr()`.
- IMPORTANT: never edit `app/generated/`. Run `make codegen`.
'''

SETUP_SETTINGS = '''
{
  "permissions": {
    "allow": ["Bash(ruff check *)", "Bash(pytest *)", "mcp__claude-code-docs__*"],
    "deny": ["Read(./.env*)", "Bash(git push --force *)"]
  },
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python3 \\"$CLAUDE_PROJECT_DIR\\"/.claude/hooks/format.py" }] }
    ]
  }
}
'''

SETUP_MCP = '''
{
  "mcpServers": {
    "claude-code-docs": { "type": "http", "url": "https://code.claude.com/docs/mcp" },
    "payments": {
      "type": "http",
      "url": "https://pay.example.com/mcp",
      "headers": { "Authorization": "Bearer sk_live_abcdef123456" }
    }
  }
}
'''

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
│   │   └── format.py             a script a hook runs
│   └── output-styles/
│       └── teach-me.md           how answers sound
└── .github/workflows/claude.yml  Claude in GitHub Actions

~/.claude/CLAUDE.md               your rules in every project
~/.claude/settings.json           your settings in every project
~/.claude.json                    your local and user scoped MCP servers
''', 'Every Claude file in one picture', lang='text', note='📂 The full map'),
    'setup-tree': show(SETUP_TREE, 'Every Claude file in the GreenLeaf shop', lang='text', note='📂 Folder layout'),
    'setup-claude': md(SETUP_CLAUDE, 'greenleaf-shop/CLAUDE.md'),
    'setup-settings': js_(SETUP_SETTINGS, 'greenleaf-shop/.claude/settings.json'),
    'setup-mcp': js_(SETUP_MCP, 'greenleaf-shop/.mcp.json (with a mistake)'),
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
<div class="tw"><table class="jt"><tr><th>Instruction</th><th>Where it goes</th></tr>
<tr><td>Run tests with pytest, check with ruff check .</td><td><code>CLAUDE.md</code>, a short fact the whole team needs every session</td></tr>
<tr><td>Always run ruff format after every edit</td><td><code>.claude/settings.json</code> hook, because it must happen every time</td></tr>
<tr><td>Never let Claude run rm -rf or git push --force</td><td><code>.claude/settings.json</code> permissions, as a deny rule</td></tr>
<tr><td>API key for the payment sandbox is sk_test_123</td><td>an environment variable or a secret store, never a Markdown file</td></tr>
<tr><td>Let Claude read our Jira tickets</td><td><code>.mcp.json</code>, an MCP server gives Claude that connection</td></tr>
<tr><td>Files in app/api use Pydantic models for every request</td><td><code>.claude/rules/api.md</code> with <code>paths:</code>, so it loads only for those files</td></tr>
<tr><td>The monthly invoice report, step by step with totals</td><td><code>.claude/skills/&lt;name&gt;/SKILL.md</code>, a procedure that loads when needed</td></tr>
<tr><td>A security reviewer that checks every change</td><td><code>.claude/agents/&lt;name&gt;.md</code>, a subagent with its own context</td></tr>
<tr><td>Explain like I am 10 and use cricket examples</td><td><code>~/.claude/output-styles/&lt;name&gt;.md</code>, how every answer sounds</td></tr>
<tr><td>My local URL is http://localhost:4100</td><td><code>CLAUDE.local.md</code>, your private notes for this project</td></tr>
<tr><td>Prices are stored in paise as integers</td><td><code>CLAUDE.md</code>, a rule everyone needs</td></tr></table></div>
''', easy=True, kw=['decision guide', 'hook or CLAUDE.md', 'skill or rule']),
    part('setup', '🏗️', 'A complete project, reviewed', '''
<p>Here is a whole shop project with every kind of Claude file. Read the tree, then the three main files, and look for what a careful reviewer would flag.</p>
[[setup-tree]]
[[setup-claude]]
[[setup-settings]]
[[setup-mcp]]
<div class="tw"><table class="jt"><tr><th>Problem</th><th>Why it matters</th><th>Fix</th></tr>
<tr><td>a real key in <code>.mcp.json</code></td><td>the file is committed, so everyone with the repository sees the key</td><td><code>"Bearer ${PAYMENTS_TOKEN}"</code></td></tr>
<tr><td><code>.gitignore</code> does not list <code>CLAUDE.local.md</code></td><td>private notes and test logins could be committed</td><td>add a <code>CLAUDE.local.md</code> line</td></tr></table></div>
''', files=['CLAUDE.md', '.claude/settings.json', '.mcp.json', '.claude/rules/api.md'], kw=['project setup', 'full example', 'review']),
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
    say('setup', 'Full setup', 'A full project uses every Claude file. Its review finds a key written in plain text and a missing gitignore line.',
        'पूरा project हर file दिखाता है, review में दो समस्याएँ मिलती हैं।',
        'ಪೂರ್ಣ project ನ review ಎರಡು ಸಮಸ್ಯೆ ತೋರಿಸುತ್ತದೆ.',
        'ପୂରା project ର review ଦୁଇଟି ସମସ୍ୟା ଦେଖାଏ।',
        'مراجعة المشروع الكامل تجد مشكلتين.',
        'Die Prüfung des ganzen Projekts findet zwei Probleme.'),
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
    say('practice', 'Practice', 'Test yourself on placing instructions in the right file.',
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
    quiz('h', 'What is wrong with the GreenLeaf .mcp.json?', ['A real key in a header', 'A missing type', 'Too many servers', 'Nothing'], 0, 'Secrets.', 'Use ${VAR} instead.'),
    quiz('x', 'On claude.ai without a terminal, what plays the role of CLAUDE.md?', ['Project instructions', 'A chat title', 'Styles only', 'Nothing'], 0, 'Projects.', 'Every chat in the project follows them.'),
    quiz('x', '"Never let Claude push with --force" is best as...', ['A deny rule in permissions', 'A line in CLAUDE.md', 'An output style', 'A skill'], 0, 'Enforced.', 'Deny rules block the call itself.'),
]

CALC = [
    calc('e', 'In the decision table, how many instructions go to CLAUDE.md?', '2', 'Count the CLAUDE.md rows.', ['The commands note and the paise note.']),
    calc('e', 'How many problems does the GreenLeaf review list?', '2', 'Count the rows.', ['The key in .mcp.json and the missing .gitignore line.']),
    calc('m', 'A CLAUDE.md of 900 lines at about 12 tokens a line. Tokens loaded at every start?', '10800', 'Multiply.', ['<span class="eq">900 × 12 = 10,800</span>'], alt=['10,800']),
    calc('m', 'Cut to 180 lines. Tokens saved per session?', '8640', 'Lines removed × 12.', ['<span class="eq">(900 − 180) × 12 = 8,640</span>'], alt=['8,640']),
    calc('h', 'A team runs 40 sessions a day. Tokens saved per day?', '345600', 'Multiply.', ['<span class="eq">8,640 × 40 = 345,600</span>'], alt=['345,600']),
    calc('x', 'At $4 per million input tokens, dollars saved per 22 day month?', '30.41', 'Tokens × days × price.', ['<span class="eq">345,600 × 22 × 4 ÷ 10⁶ ≈ 30.41</span>'], alt=['$30.41', '30.4']),
]

EX = []

T = {
    'slug': 'claude-file-map', 'title': 'Capstone: Which File Holds What', 'short': 'File map capstone', 'emoji': '🗺️', 'module': MODULE, 'minutes': 16,
    'lead': 'The full map of Claude files and exactly what goes in each, the real names behind rules.md, skills.md, agents.md and the "prompt file", a table that places any instruction, a complete project reviewed, a homework helper a child can build, and a six week path to the next level.',
    'plain': 'Each Claude file has one job. This chapter lists every file, says what to write in it, and shows a whole project that uses them all.',
    'desc': 'Which Claude file holds what: CLAUDE.md, CLAUDE.local.md, .claude/rules, SKILL.md, .claude/agents, settings.json, hooks, .mcp.json, output styles and plugin.json, with a full project example and a homework helper build.',
    'summary': 'The complete Claude file map with what goes in and stays out of each file, the real names behind common wrong ones, a decision table for eleven example instructions, a full project setup with two problems to fix, a homework helper with CLAUDE.md, a quiz skill and a claude.ai Project version, and a six week practice path.',
    'keywords': ['file map', 'CLAUDE.md', 'rules', 'SKILL.md', 'agents', 'settings.json', '.mcp.json', 'what goes where', 'homework helper', 'capstone'],
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
