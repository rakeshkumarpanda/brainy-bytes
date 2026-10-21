# Chapter 9: subagents and output styles. What a subagent is, built-ins, the agent file, every field, ready to copy agents, invoking them, memory, and output styles.
from ckit import part, md, cli, prompt, say, quiz, calc, panel

MODULE = ('🛠️', 'Claude Code and its files', 'claude-code-files', 'Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.')

REVIEWER = '''
---
name: code-reviewer
description: Expert code reviewer. Use right after writing or changing code, and before any commit.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer for this repository.

When invoked:
1. Run `git diff` to see recent changes and focus on the changed files.
2. Check for: unclear names, duplicated code, missing error handling,
   secrets in code, missing input validation and missing tests.
3. Report findings in three groups: Must fix, Should fix, Nice to have.
   For each, give the file, the line and a concrete fix.

Be specific and brief. Do not rewrite files yourself.
'''

TESTER = '''
---
name: test-runner
description: Runs the test suite and fixes failing tests. Use proactively after code changes or when the user mentions failing tests.
tools: Read, Edit, Bash, Grep, Glob
model: inherit
maxTurns: 25
---

You run tests and fix failures.

1. Run the smallest test command that covers the change (see CLAUDE.md).
2. For each failure, find the cause in the code under test, not in the test.
3. Fix it, rerun, and repeat until green.
4. Reply with: what failed, the cause, the fix, and the final test summary.

Never delete or skip a test to make it pass.
'''

RESEARCH = '''
---
name: doc-researcher
description: Reads long documents, policies or reports and returns a short cited summary. Use when a question needs many files read.
tools: Read, Grep, Glob, WebFetch
model: haiku
color: cyan
---

You research questions in documents and return only what matters.

- Search first, then read only the relevant sections.
- Return at most 10 bullet points.
- Cite the file and heading for every point.
'''

BROKEN = '''
---
name: team:helper
descripton: Helps the team
max_turns: 10
---

You help the team with anything.
'''

CODES = {
    'ask-create': prompt('''
Create a personal code-improver subagent in ~/.claude/agents/ that scans
files and suggests improvements for readability, performance, and best
practices. It should explain each issue, show the current code, and
provide an improved version. Make it read-only and have it use Sonnet.
''', 'Ask Claude to write the agent file for you', result='Claude writes ~/.claude/agents/code-improver.md with a name, description, a read-only tools list, model: sonnet and a system prompt. You review it and keep or edit it.'),
    'reviewer': md(REVIEWER, '.claude/agents/code-reviewer.md'),
    'tester': md(TESTER, '.claude/agents/test-runner.md'),
    'research': md(RESEARCH, '.claude/agents/doc-researcher.md'),
    'broken': md(BROKEN, '.claude/agents/broken.md'),
    'invoke': prompt('''
Use the test-runner subagent to fix the failing checkout tests
@"code-reviewer (agent)" look at my changes to src/payments
Use 3 doc-researcher subagents in parallel: one on the leave policy, one on travel, one on expenses
''', 'Three ways to call a subagent', result='The first lets Claude decide to delegate. The @-mention makes sure that exact agent runs. The third runs three helpers at once, each returning a short summary.'),
    'session': cli('''
claude --agent code-reviewer        # the whole session runs as that agent
/agents                             # prints a reminder of where agent files live
''', 'Run a whole session as one agent', result='With --agent, the agent\'s system prompt, tools and model apply to the main conversation. Setting "agent": "code-reviewer" in .claude/settings.json makes it the project default.'),
    'memory-agent': md('''
---
name: support-triage
description: Triages new support tickets by product area and urgency. Use for any batch of tickets.
tools: Read, Grep
memory: project
---

Sort each ticket into: billing, delivery, product, account.
Mark urgency as P1 (money or data at risk), P2 (blocked) or P3 (other).
Check your memory for recurring issues and update it with new patterns you see.
''', 'An agent that remembers between sessions'),
    'style': md('''
---
name: Teach me
description: Explains every step in plain words for a beginner and checks understanding
keep-coding-instructions: true
---

You are working with a beginner who is learning while you work.

- Before each change, say in one sentence what you are about to do and why.
- After each change, explain any new word or command in plain English.
- Every few steps, ask one short question to check understanding.
- Keep the actual work the same quality as usual.
''', '~/.claude/output-styles/teach-me.md'),
    'style-cmds': cli('''
/output-style                 # list styles and see the current one
/output-style concise         # switch to a built-in style
/output-style "Teach me"      # switch to your own style
''', 'Switch output styles', result='The choice is saved to .claude/settings.local.json as "outputStyle". Set it in ~/.claude/settings.json to make it your default everywhere.'),
}

PARTS = [
    part('what', '🤖', 'What a subagent is', '''
<p>A <b>subagent</b> is a helper that Claude can hand a task to. It has its <b>own context window</b>, its own instructions and its own allowed tools. It does the work, then sends back <b>only a short result</b>. Your main conversation stays small and focused.</p>
<div class="viz" data-viz="flow" data-k="delegate"></div>
<div class="tw"><table class="jt"><tr><th>Use a subagent when...</th><th>Stay in the main chat when...</th></tr>
<tr><td>a task reads many files or long logs</td><td>you need quick back and forth</td></tr>
<tr><td>you want a specialist with fixed rules, like a reviewer</td><td>several steps share a lot of context</td></tr>
<tr><td>several independent searches can run in parallel</td><td>the change is small and quick</td></tr></table></div>
''', easy=True, files=['.claude/agents/'], kw=['subagent', 'delegation', 'own context window', 'summary']),
    part('builtin', '🧩', 'Built-in subagents you already have', '''
<div class="tw"><table class="jt"><tr><th>Agent</th><th>What it does</th></tr>
<tr><td><b>Explore</b></td><td>fast, read only search of a codebase. Starts without your <code>CLAUDE.md</code> to stay light.</td></tr>
<tr><td><b>Plan</b></td><td>read only research used in plan mode</td></tr>
<tr><td><b>general-purpose</b></td><td>complex tasks that need both exploring and changing</td></tr>
<tr><td><b>claude</b></td><td>the catch all when nothing more specific fits</td></tr>
<tr><td>statusline-setup, claude-code-guide</td><td>small helpers for the status line and for questions about Claude Code</td></tr>
</table></div>
<p>Claude uses these on its own. You will see a row in the transcript such as <code>Explore(Find the payment code)</code>.</p>
''', easy=True, kw=['Explore', 'Plan', 'general-purpose', 'built-in agents']),
    part('create', '🛠️', 'Create your first subagent, step by step', '''
<ol class="steps"><li>Decide the scope: <code>~/.claude/agents/</code> for you in every project, or <code>.claude/agents/</code> for the team.</li>
<li>Ask Claude to write it, or create a Markdown file yourself.</li>
<li>Check the front matter: <code>name</code> and <code>description</code> are required.</li>
<li>Write the body. It becomes the agent's <b>system prompt</b>.</li>
<li>Try it: "Use the code-reviewer agent to check my changes".</li></ol>
[[ask-create]]
[[reviewer]]
<div class="cl-name">This is the real "agents.md" people talk about: not one file, but <b>one Markdown file per agent</b> inside <code>.claude/agents/</code>. A root level <code>AGENTS.md</code> is something else: shared project instructions (chapter 5).</div>
''', easy=True, files=['.claude/agents/code-reviewer.md', '~/.claude/agents/'], kw=['create subagent', 'agent file', 'system prompt', 'agents.md']),
    part('fields', '🏷️', 'Every field in an agent file', '''
<p>Multi word fields use camelCase, such as <code>maxTurns</code>. A misspelled field is ignored without an error.</p>
<div class="tw"><table class="jt"><tr><th>Field</th><th>What it does</th></tr>
<tr><td><code>name</code> (required)</td><td>unique id, no <code>:</code></td></tr>
<tr><td><code>description</code> (required)</td><td>when Claude should delegate to it. Add "use proactively" to encourage it.</td></tr>
<tr><td><code>tools</code>, <code>disallowedTools</code></td><td>allow list or block list of tools. Leave <code>tools</code> out to inherit all.</td></tr>
<tr><td><code>model</code></td><td><code>sonnet</code>, <code>opus</code>, <code>haiku</code>, <code>fable</code>, a full model id, or <code>inherit</code></td></tr>
<tr><td><code>permissionMode</code></td><td><code>default</code>, <code>acceptEdits</code>, <code>auto</code>, <code>dontAsk</code>, <code>bypassPermissions</code>, <code>plan</code></td></tr>
<tr><td><code>maxTurns</code></td><td>stop after this many steps</td></tr>
<tr><td><code>skills</code></td><td>skills loaded in full at start</td></tr>
<tr><td><code>mcpServers</code></td><td>MCP servers only this agent can use</td></tr>
<tr><td><code>memory</code></td><td><code>user</code>, <code>project</code> or <code>local</code>: notes it keeps between sessions</td></tr>
<tr><td><code>hooks</code>, <code>effort</code>, <code>background</code></td><td>hooks while it runs, effort level, run in the background</td></tr>
<tr><td><code>isolation: worktree</code></td><td>work on a separate copy of the repository</td></tr>
<tr><td><code>omitClaudeMd</code>, <code>color</code>, <code>initialPrompt</code></td><td>skip <code>CLAUDE.md</code>, colour in the task list, first prompt when run with <code>--agent</code></td></tr>
</table></div>
<p>Here is an agent file with four mistakes. Try to spot them before reading the table.</p>
[[broken]]
<div class="tw"><table class="jt"><tr><th>Line</th><th>Problem</th><th>Fix</th></tr>
<tr><td><code>name: team:helper</code></td><td>a name may not contain <code>:</code></td><td><code>name: team-helper</code></td></tr>
<tr><td><code>descripton:</code></td><td>misspelled, so it is ignored and the agent has no description</td><td><code>description: ...</code></td></tr>
<tr><td>(missing)</td><td>without a description Claude never knows when to use it</td><td>say when to delegate, in plain words</td></tr>
<tr><td><code>max_turns: 10</code></td><td>unknown field, ignored without an error</td><td><code>maxTurns: 10</code></td></tr></table></div>
''', files=['.claude/agents/<name>.md'], kw=['frontmatter', 'tools', 'model', 'permissionMode', 'maxTurns', 'skills', 'mcpServers', 'memory', 'isolation worktree']),
    part('gallery', '🗂️', 'Ready to copy agents', '''
[[tester]]
[[research]]
<div class="cl-put"><ul><li><b>Description:</b> when to use it, in the words people use.</li>
<li><b>Tools:</b> only what the job needs. A reviewer does not need <code>Edit</code>.</li>
<li><b>Model:</b> <code>haiku</code> for quick reading jobs, <code>sonnet</code> or <code>inherit</code> for real work.</li>
<li><b>Body:</b> numbered steps, what to return and in what shape, and the one or two things it must never do.</li></ul></div>
''', easy=True, files=['.claude/agents/test-runner.md', '.claude/agents/doc-researcher.md'], kw=['test runner agent', 'research agent', 'agent examples']),
    part('use', '📣', 'Calling a subagent', '''
[[invoke]]
[[session]]
<div class="scenario"><b>🧑‍⚖️ Real scenario: a policy question</b>An HR manager asks "can a new joiner take leave in their first month and get travel paid for a training?". Claude starts two <code>doc-researcher</code> agents in parallel on the leave and travel policies. Each returns five cited bullets. The answer arrives with exact clause references and the main chat stays short.</div>
''', easy=True, kw=['invoke subagent', '@-mention', '--agent', 'parallel subagents']),
    part('memory', '🧠', 'Agents that remember', '''
<p>With <code>memory</code> set, the agent keeps its own notes folder and gets better over time, for example learning which support issues keep coming back.</p>
[[memory-agent]]
<ul><li><code>user</code>: notes shared across all your projects.</li><li><code>project</code>: notes for this project, can be shared with the team.</li><li><code>local</code>: notes for this project on your machine only.</li></ul>
''', files=['.claude/agents/support-triage.md'], kw=['agent memory', 'persistent memory', 'memory field']),
    part('styles', '🎨', 'Output styles: change how Claude talks for a whole session', '''
<p>An <b>output style</b> changes Claude's role, tone and answer format for the session. Four built-in styles sit on top of the Default:</p>
<div class="tw"><table class="jt"><tr><th>Style</th><th>What changes</th></tr>
<tr><td>Proactive</td><td>starts work right away and makes reasonable assumptions</td></tr>
<tr><td>Concise</td><td>leads with the result, no preamble or recap</td></tr>
<tr><td>Explanatory</td><td>adds short "Insight" notes explaining the choices</td></tr>
<tr><td>Learning</td><td>explains and leaves small pieces of code for you to write</td></tr>
</table></div>
<p>Make your own in <code>~/.claude/output-styles/</code> or <code>.claude/output-styles/</code>. Set <code>keep-coding-instructions: true</code> if Claude will still write code.</p>
[[style]]
[[style-cmds]]
<div class="vs"><div><b>📘 CLAUDE.md</b>facts and rules about your project</div><div><b>🎨 Output style</b>role, tone and format of every answer</div></div>
''', easy=True, files=['~/.claude/output-styles/', '.claude/output-styles/'], kw=['output styles', 'Concise', 'Explanatory', 'Learning', 'Proactive', 'keep-coding-instructions', '/output-style']),
]

DG = {
    'delegate': {'t': 'Main conversation and a subagent', 'w': 900, 'h': 260,
                 'n': [['you', 20, 100, 120, 56, 'You', {'c': 5, 'sh': 'pill'}],
                       ['main', 190, 100, 200, 56, 'main conversation', {'c': 1, 'sub': 'stays small'}],
                       ['sub', 470, 20, 200, 56, 'subagent', {'c': 3, 'sub': 'own context window', 'i': 'Has its own system prompt, tools and model.'}],
                       ['files', 740, 20, 140, 56, '38 files', {'c': 0, 'sh': 'doc', 'i': 'Read inside the subagent only.'}],
                       ['sum', 470, 180, 200, 56, 'short summary', {'c': 4, 'sh': 'doc'}]],
                 'e': [['you', 'main'], ['main', 'sub', {'t': 'task'}], ['sub', 'files'], ['sub', 'sum'], ['sum', 'main', {'t': 'result'}]],
                 'st': [[['you', 'main', 'you>main'], 'You ask a question that needs a big search.'],
                        [['sub', 'main>sub'], 'Claude hands the search to a subagent with clear instructions.'],
                        [['files', 'sub>files'], 'The subagent reads many files in its own window.'],
                        [['sum', 'sub>sum', 'sum>main'], 'Only the short summary returns. Your chat stays clean.']]},
}

INFO = {'title': 'Subagents: helpers with their own desk', 'panels': [
    panel([['e', '🤖'], ['t', 'own context window', {'b': 1}]], 'A helper', 'Does one job in its own space.', 'Sends back only a summary.'),
    panel([['e', '📄'], ['t', '.claude/agents/<name>.md', {'b': 1, 'size': 11}]], 'One file each', 'Front matter plus a system prompt.', 'name and description are required.'),
    panel([['e', '🔧'], ['t', 'tools: Read, Grep', {'b': 1}]], 'Least power', 'Give only the tools it needs.', 'Pick a cheaper model for reading jobs.'),
    panel([['e', '🎨'], ['t', '/output-style concise', {'b': 1}]], 'Output styles', 'Change tone and format for a session.', 'Built-in or your own.')],
    'remember': 'Delegate noisy work, keep the main chat for decisions.'}

REAL = [
    ['🔍', 'A security team', 'Keeps a read-only security-reviewer agent with only Read, Grep and Glob. It checks every pull request and cannot change a line.'],
    ['📚', 'A university library', 'Runs three doc-researcher agents on Haiku in parallel across thesis guidelines, citation rules and formatting rules, then merges the answers.'],
    ['🧑‍🏫', 'A coding bootcamp', 'Gives students a "Teach me" output style so Claude explains every step while still finishing the work.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter builds subagents, helpers with their own context, and shows output styles that change how Claude talks.',
        'यह अध्याय subagents बनाता है और output styles दिखाता है।',
        'ಈ ಅಧ್ಯಾಯ subagents ಕಟ್ಟುತ್ತದೆ ಮತ್ತು output styles ತೋರಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ subagents ତିଆରି କରେ ଓ output styles ଦେଖାଏ।',
        'يبني هذا الفصل الوكلاء الفرعيين ويعرض أنماط الإخراج.',
        'Dieses Kapitel baut Subagenten und zeigt Ausgabestile.'),
    say('what', 'What it is', 'A subagent works in its own context window and sends back only a short summary, so the main chat stays small.',
        'Subagent अपनी context window में काम करता है और सिर्फ सार भेजता है।',
        'Subagent ತನ್ನ context window ನಲ್ಲಿ ಕೆಲಸ ಮಾಡಿ ಸಾರಾಂಶ ಮಾತ್ರ ಕಳುಹಿಸುತ್ತದೆ.',
        'Subagent ନିଜ context window ରେ କାମ କରି କେବଳ ସାରାଂଶ ପଠାଏ।',
        'الوكيل الفرعي يعمل في نافذته الخاصة ويرسل ملخصًا فقط.',
        'Ein Subagent arbeitet im eigenen Kontextfenster und liefert nur eine Zusammenfassung.'),
    say('builtin', 'Built-ins', 'Explore searches, Plan researches in plan mode, and general purpose handles complex tasks. Claude uses them on its own.',
        'Explore खोजता है, Plan योजना के लिए, general-purpose जटिल कामों के लिए।',
        'Explore ಹುಡುಕುತ್ತದೆ, Plan ಯೋಜನೆಗೆ, general-purpose ಸಂಕೀರ್ಣ ಕೆಲಸಕ್ಕೆ.',
        'Explore ଖୋଜେ, Plan ଯୋଜନା ପାଇଁ, general-purpose ଜଟିଳ କାମ ପାଇଁ।',
        'Explore للبحث وPlan للتخطيط وgeneral-purpose للمهام المعقدة.',
        'Explore sucht, Plan recherchiert im Planmodus, general-purpose erledigt komplexe Aufgaben.'),
    say('create', 'Create one', 'Put one Markdown file per agent in the agents folder. Name and description are required, and the body is its system prompt.',
        'हर agent के लिए agents folder में एक file। Name और description ज़रूरी।',
        'ಪ್ರತಿ agent ಗೆ agents folder ನಲ್ಲಿ ಒಂದು file. Name, description ಕಡ್ಡಾಯ.',
        'ପ୍ରତି agent ପାଇଁ agents folder ରେ ଗୋଟିଏ file. Name ଓ description ଜରୁରୀ।',
        'ملف واحد لكل وكيل في مجلد agents. الاسم والوصف مطلوبان.',
        'Eine Datei pro Agent im agents-Ordner. Name und Beschreibung sind Pflicht.'),
    say('fields', 'Fields', 'Fields set tools, model, permission mode, turn limit, skills, MCP servers, memory and more. Misspelled fields are ignored.',
        'Fields tools, model, mode, skills और memory तय करते हैं। गलत नाम अनदेखा होता है।',
        'Fields tools, model, mode, skills, memory ನಿರ್ಧರಿಸುತ್ತವೆ.',
        'Fields tools, model, mode, skills, memory ସ୍ଥିର କରେ।',
        'الحقول تضبط الأدوات والنموذج والوضع والمهارات والذاكرة.',
        'Felder legen Tools, Modell, Modus, Skills und Gedächtnis fest.'),
    say('gallery', 'Examples', 'A test runner, a document researcher and a code reviewer. Give each only the tools it needs.',
        'Test runner, document researcher और code reviewer, हर एक को ज़रूरी tools ही।',
        'Test runner, document researcher, code reviewer. ಅಗತ್ಯ tools ಮಾತ್ರ.',
        'Test runner, document researcher, code reviewer. ଦରକାରୀ tools ହିଁ।',
        'مشغّل اختبارات وباحث مستندات ومراجع شيفرة، كل منها بالأدوات اللازمة فقط.',
        'Testläufer, Dokumentrechercheur und Code-Reviewer, jeweils nur mit nötigen Tools.'),
    say('use', 'Calling', 'Name the agent in your prompt, at mention it to be sure, or run a whole session with dash dash agent.',
        'Prompt में नाम लें, @ से पक्का करें, या --agent से पूरा session।',
        'Prompt ನಲ್ಲಿ ಹೆಸರು, @ ಮೂಲಕ ಖಚಿತ, ಅಥವಾ --agent.',
        'Prompt ରେ ନାମ, @ ଦ୍ୱାରା ନିଶ୍ଚିତ, ବା --agent.',
        'اذكر الوكيل في الموجّه أو استخدم @ أو شغّل الجلسة كلها بـ --agent.',
        'Nenne den Agenten, erwähne ihn mit @ oder starte die Sitzung mit --agent.'),
    say('memory', 'Memory', 'With the memory field an agent keeps notes between sessions at user, project or local level.',
        'Memory field से agent sessions के बीच notes रखता है।',
        'Memory field ಮೂಲಕ agent notes ಉಳಿಸುತ್ತದೆ.',
        'Memory field ଦ୍ୱାରା agent notes ରଖେ।',
        'بحقل memory يحتفظ الوكيل بملاحظات بين الجلسات.',
        'Mit dem memory-Feld behält ein Agent Notizen zwischen Sitzungen.'),
    say('styles', 'Output styles', 'Output styles change role, tone and format for a session. Use built-in ones or write your own Markdown file.',
        'Output styles पूरे session का tone और format बदलते हैं।',
        'Output styles session ನ tone ಮತ್ತು format ಬದಲಿಸುತ್ತವೆ.',
        'Output styles session ର tone ଓ format ବଦଳାଏ।',
        'أنماط الإخراج تغيّر النبرة والشكل للجلسة كلها.',
        'Ausgabestile ändern Ton und Format für die ganze Sitzung.'),
    say('practice', 'Practice', 'Test yourself on agent files, picking tools and the context saved by delegation.',
        'Agent files जांचने और context बचत का अभ्यास।',
        'Agent files ಪರಿಶೀಲನೆ ಮತ್ತು context ಉಳಿತಾಯ ಅಭ್ಯಾಸ.',
        'Agent files ଯାଞ୍ଚ ଓ context ସଞ୍ଚୟ ଅଭ୍ୟାସ।',
        'تدرّب على فحص ملفات الوكلاء وتقدير التوفير.',
        'Übe Agentendateien zu prüfen und Kontextersparnis zu schätzen.'),
]

QUIZ = [
    quiz('e', 'Where do team subagents live?', ['.claude/agents/<name>.md', 'AGENTS.md', '.claude/skills/', 'CLAUDE.md'], 0, 'One file per agent.', 'Each agent is a Markdown file in the agents folder.'),
    quiz('e', 'Which two fields are required in an agent file?', ['name and description', 'tools and model', 'name and model', 'description and tools'], 0, 'Identity and purpose.', 'Everything else is optional.'),
    quiz('e', 'What does a subagent send back to the main chat?', ['A short result', 'Every file it read', 'Its full context', 'Nothing'], 0, 'Keeps the chat clean.', 'Only the summary returns.'),
    quiz('m', 'What does the body of an agent file become?', ['The agent\'s system prompt', 'A comment', 'A test', 'The first user message'], 0, 'Below the front matter.', 'The Markdown after the front matter is its system prompt.'),
    quiz('m', 'Which built-in agent is fast and read only for searching code?', ['Explore', 'general-purpose', 'claude', 'statusline-setup'], 0, 'It explores.', 'Explore cannot write or edit.'),
    quiz('m', 'How do you make sure a specific agent runs for one task?', ['@-mention it', 'Write its name in CLAUDE.md', 'Restart Claude Code', 'Use /clear'], 0, 'Like mentioning a file.', 'The @-mention guarantees that agent is used.'),
    quiz('h', 'You write max_turns: 10. What happens?', ['It is ignored because the field is maxTurns', 'It works', 'The agent fails to load', 'It becomes a tool'], 0, 'camelCase.', 'Unknown fields are ignored without an error.'),
    quiz('h', 'Which model value is best for a cheap reading and summarising agent?', ['haiku', 'fable', 'opus', 'bypass'], 0, 'Fast and low cost.', 'Haiku suits simple, high volume reading.'),
    quiz('x', 'Which file sets tone and format for every answer in a session?', ['An output style', 'A subagent', 'A path rule', '.mcp.json'], 0, 'Style.', 'Output styles change role, tone and format.'),
    quiz('x', 'A subagent should never change files. What is the cleanest setup?', ['tools: Read, Grep, Glob', 'Write "do not edit" in the description', 'model: haiku', 'color: red'], 0, 'Least power.', 'Without Edit or Write it cannot change files at all.'),
]

CALC = [
    calc('e', 'A subagent reads 38 files of 3,200 tokens each. How many tokens is that?', '121600', 'Multiply.', ['<span class="eq">38 × 3,200 = 121,600</span>'], alt=['121,600']),
    calc('e', 'It returns a 700 token summary. How many tokens did the main chat avoid?', '120900', 'Read minus returned.', ['<span class="eq">121,600 − 700 = 120,900</span>'], alt=['120,900']),
    calc('m', 'Three researchers run in parallel, taking 40 s, 55 s and 35 s. How long until all are done, in seconds?', '55', 'The slowest decides.', ['Parallel work finishes with the longest job.']),
    calc('m', 'The same three run one after another. How many seconds?', '130', 'Add them.', ['<span class="eq">40 + 55 + 35 = 130</span>']),
    calc('h', 'How many problems does the table list for broken.md?', '4', 'Count the rows.', ['Missing description, a colon in the name, the misspelled descripton field and the unknown max_turns field make 4.']),
    calc('x', 'An agent on Haiku ($0.10 per million input) reads 1,216,000 tokens. Input cost in dollars?', '0.12', 'Millions times price.', ['<span class="eq">1.216 × 0.10 ≈ 0.12</span>'], alt=['0.1216', '$0.12']),
]

EX = []

T = {
    'slug': 'claude-subagents', 'title': 'Subagents and Output Styles', 'short': 'Subagents and styles', 'emoji': '🤖', 'module': MODULE, 'minutes': 16,
    'lead': 'What a subagent is and when to use one, the built-in agents, writing .claude/agents files step by step with every field, ready to copy reviewer, tester and researcher agents, calling and remembering, and output styles that change how Claude talks.',
    'plain': 'A subagent is a helper Claude sends to do one job, like reading a pile of papers. The helper reads them at its own desk and comes back with a short note.',
    'desc': 'Claude Code subagents: .claude/agents files, frontmatter fields, built-in Explore and Plan agents, reviewer, test runner and research agents, @-mentions, agent memory and output styles.',
    'summary': 'What subagents are and how much context they save, built-in agents, creating an agent file step by step and the agents.md name check, every frontmatter field with a broken agent file and its four mistakes, ready to copy test-runner and doc-researcher agents, three ways to call an agent and --agent sessions, agent memory, and built-in and custom output styles.',
    'keywords': ['subagents', '.claude/agents', 'agents.md', 'agent file', 'Explore', 'Plan', 'tools', 'model', 'maxTurns', 'memory', '@-mention', '--agent', 'output styles', 'keep-coding-instructions'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
