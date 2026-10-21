# Chapter 7: skills. SKILL.md step by step, where skills live, frontmatter, arguments, supporting files and scripts, dynamic context, who invokes, real skills, claude.ai uploads.
from ckit import part, test, show, md, cli, say, quiz, calc, panel

MODULE = ('🛠️', 'Claude Code and its files', 'claude-code-files', 'Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.')


TOTALS = '''
"""Add up an invoice CSV and check it against the total line. Prints a short report."""
import csv
import sys

rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
items = [r for r in rows if r["item"] != "TOTAL"]
stated = next(float(r["amount"]) for r in rows if r["item"] == "TOTAL")
computed = round(sum(float(r["qty"]) * float(r["rate"]) for r in items), 2)

for r in items:
    line = round(float(r["qty"]) * float(r["rate"]), 2)
    flag = "" if abs(line - float(r["amount"])) < 0.01 else "   <-- line amount does not match qty x rate"
    print(f'{r["item"]:<18} {r["qty"]:>3} x {float(r["rate"]):>8.2f} = {float(r["amount"]):>9.2f}{flag}')
print(f"{'stated total':<34} {stated:>9.2f}")
print(f"{'computed total':<34} {computed:>9.2f}")
print("RESULT:", "OK" if abs(stated - computed) < 0.01 else f"MISMATCH of {round(stated - computed, 2)}")
'''

INVOICE_SKILL = '''
---
name: invoice-checker
description: Checks supplier invoices for arithmetic errors and missing details. Use when the user shares an invoice CSV or PDF, or asks to verify, audit or check an invoice.
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/totals.py *)
---

# Invoice checker

1. If the invoice is a CSV, run:
   `python ${CLAUDE_SKILL_DIR}/scripts/totals.py <file>`
   Trust the script's arithmetic. Do not redo the sums yourself.
2. Check the invoice against [checklist.md](checklist.md).
3. Reply with:
   - RESULT line from the script
   - each problem as one bullet with the line item and the amount
   - a two sentence email to the supplier if anything is wrong
'''


CODES = {
    'first': md('''
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks
you notice such as missing error handling, hardcoded values, or tests that need
updating. If the diff is empty, say there are no uncommitted changes.
''', '~/.claude/skills/summarize-changes/SKILL.md'),
    'first-steps': cli('''
mkdir -p ~/.claude/skills/summarize-changes
# save the file above as ~/.claude/skills/summarize-changes/SKILL.md
claude
> what did I change?              # Claude picks the skill because the description matches
> /summarize-changes              # or run it yourself by name
''', 'Create and try it', result='Claude answers with two or three bullets about your real diff and a list of risks. The git diff was pasted into the skill before Claude read it.'),
    'name-tree': show('''
.claude/skills/
├── weekly-report/
│   └── SKILL.md                 ->  /weekly-report
├── invoice-checker/
│   ├── SKILL.md                 ->  /invoice-checker
│   ├── checklist.md             (read only when SKILL.md points to it)
│   └── scripts/totals.py        (run, never loaded into context)
└── brand-voice/
    └── SKILL.md                 ->  name: brand-voice, user-invocable: false

.claude/commands/deploy.md       ->  /deploy   (older format, still works)
''', 'Folder names become commands', lang='text', note='📂 Folder layout'),
    'standup': md('''
---
name: standup
description: Writes my daily stand-up update from yesterday's git commits. Use when I ask for a standup, daily update or what I did yesterday.
argument-hint: "[name] [date]"
arguments: [person, day]
---

Write a stand-up update for $person for $day.

## Commits since yesterday
!`git log --since=yesterday --pretty=format:"- %s"`

## Open tasks
!`cat TODO.md`

## Format
Three headings: Done, Doing, Blocked. At most 3 bullets each. Plain English, no commit hashes.
''', '.claude/skills/standup/SKILL.md'),
    'render': show('''
Write a stand-up update for Asha for 2026-10-19.

## Commits since yesterday
- Add tests for free delivery rule
- Fix coupon rounding on checkout

## Open tasks
- Add GST to the invoice PDF
- Waiting on design for the new cart page

## Format
Three headings: Done, Doing, Blocked. At most 3 bullets each. Plain English, no commit hashes.
''', 'What Claude receives after /standup Asha 2026-10-19', lang='text', note='📨 After the placeholders and commands are filled in'),
    'invoice-skill': md(INVOICE_SKILL, '.claude/skills/invoice-checker/SKILL.md'),
    'checklist': md('''
# Invoice checklist
- Supplier GSTIN present and 15 characters long
- Invoice number and date present
- Our PO number quoted (format PO-2026-xxxx)
- Payment terms are 30 days or more
''', '.claude/skills/invoice-checker/checklist.md'),
    'totals': test({
        '.claude/skills/invoice-checker/scripts/totals.py': TOTALS,
        'invoices/inv-001.csv': '''
item,qty,rate,amount
A4 paper ream,10,245.00,2450.00
Stapler,4,180.00,720.00
Whiteboard markers,12,35.50,462.00
TOTAL,,,3632.00
''',
    }, '$PY .claude/skills/invoice-checker/scripts/totals.py invoices/inv-001.csv', 'The skill\'s script, run on a real invoice',
        shown_cmd='python .claude/skills/invoice-checker/scripts/totals.py invoices/inv-001.csv', badge='🐍 Python script run for real'),
    'deploy': md('''
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
allowed-tools: Bash(python -m build) Bash(pytest *)
---

Deploy $ARGUMENTS to production:

1. Run the test suite. Stop if anything fails.
2. Build the application.
3. Push to the deployment target.
4. Check the health URL and report the result.
''', 'A skill only you can start'),
    'voice': md('''
---
name: brand-voice
description: GreenLeaf brand voice for any customer facing text such as emails, product pages and social posts.
user-invocable: false
---

- Warm and simple. Write for someone reading on a phone.
- Say "plants" and "plant parents", never "SKUs" or "users".
- One exclamation mark per message at most.
- Sign off as "Team GreenLeaf".
''', 'A background knowledge skill only Claude uses'),
    'research': md('''
---
name: deep-research
description: Research a topic thoroughly in the codebase
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyse the code
3. Summarise findings with specific file references
''', 'A skill that runs in its own subagent'),
    'meeting': md('''
---
name: meeting-actions
description: Turns raw meeting notes or a transcript into a clean action list with owners and dates. Use when the user pastes meeting notes, a transcript or asks for action items.
---

From the notes the user gave:

1. List decisions made, one line each.
2. List action items as a table: Owner, Task, Due date.
   If no owner is named, write "Owner needed". If no date, write "No date".
3. List open questions.
4. Write a 3 line summary email the organiser can send.

Use the names exactly as written in the notes.
''', 'Daily work: meeting notes to actions'),
    'commit': md('''
---
name: commit
description: Stage and commit the current changes with a clear message
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *) Bash(git diff *)
---

1. Run `git status` and `git diff` to see what changed.
2. Write a commit message: a summary line under 60 characters in the imperative
   ("Add", "Fix", "Remove"), a blank line, then why the change was needed.
3. Stage only files related to this change and commit.
''', 'Daily work: commit messages'),
    'zip': cli('''
cd ~/.claude/skills
zip -r invoice-checker.zip invoice-checker      # the ZIP holds the folder, SKILL.md inside it
# then in claude.ai: Settings, Capabilities, Skills, Upload skill
''', 'Package a skill for claude.ai', result='The upload checks the front matter. A skill that passes can be turned on for your account and used in chats.'),
}

PARTS = [
    part('what', '🧰', 'What a skill is', '''
<p>A <b>skill</b> is a folder with a file called <code>SKILL.md</code>. The top of the file has a short description of <b>when</b> to use it. The rest has the <b>steps</b>. Claude Code, claude.ai and the API all use this format.</p>
<p>Skills use <b>progressive disclosure</b>, which means Claude reads them in layers and only as far as it needs:</p>
<div class="viz" data-viz="lanes" data-k="levels"></div>
<div class="tw"><table class="jt"><tr><th>Level</th><th>When it loads</th><th>Size</th></tr>
<tr><td>1. name and description</td><td>always, at start</td><td>about 100 tokens per skill</td></tr>
<tr><td>2. the body of <code>SKILL.md</code></td><td>when the skill is used</td><td>keep it under 5,000 tokens</td></tr>
<tr><td>3. other files and scripts</td><td>only if the steps point to them</td><td>scripts run, only their output is read</td></tr>
</table></div>
<div class="tip">Use a skill when you notice you are pasting the same instructions for the third time.</div>
''', easy=True, files=['SKILL.md'], kw=['skill', 'SKILL.md', 'progressive disclosure', 'levels']),
    part('first', '🚀', 'Build your first skill in three steps', '''
<ol class="steps"><li>Make a folder named after the skill in <code>~/.claude/skills/</code> (just for you) or <code>.claude/skills/</code> (for the team).</li>
<li>Create <code>SKILL.md</code> inside it with a <code>description</code> at the top and the steps below.</li>
<li>Start Claude Code and either ask naturally or type <code>/</code> and the folder name.</li></ol>
[[first]]
[[first-steps]]
<p>The line <code>!`git diff HEAD`</code> is <b>dynamic context</b>: Claude Code runs the command first and pastes the output into the skill, so Claude reads your real changes.</p>
''', easy=True, files=['~/.claude/skills/<name>/SKILL.md'], kw=['first skill', 'create skill', 'step by step', 'summarize-changes']),
    part('where', '📍', 'Where skills live and how they get their name', '''
<div class="tw"><table class="jt"><tr><th>Where</th><th>Path</th><th>Who gets it</th></tr>
<tr><td>Personal</td><td><code>~/.claude/skills/&lt;name&gt;/SKILL.md</code></td><td>you, in every project</td></tr>
<tr><td>Project</td><td><code>.claude/skills/&lt;name&gt;/SKILL.md</code></td><td>everyone who clones the repo</td></tr>
<tr><td>Plugin</td><td><code>&lt;plugin&gt;/skills/&lt;name&gt;/SKILL.md</code></td><td>anyone who installs it, as <code>/plugin:name</code></td></tr>
<tr><td>Organisation</td><td>the managed settings folder</td><td>everyone on managed machines</td></tr>
</table></div>
[[name-tree]]
<div class="cl-name">There is no <code>skills.md</code> or <code>Skills.md</code> file. Each skill is its own folder, and the file inside is always named <code>SKILL.md</code> in capitals. The older <code>.claude/commands/&lt;name&gt;.md</code> files still work as simple slash commands, but new work should use skills because they can hold extra files.</div>
''', easy=True, files=['~/.claude/skills/', '.claude/skills/', '.claude/commands/'], kw=['skill locations', 'personal skills', 'project skills', 'command name', 'skills.md', '.claude/commands']),
    part('front', '🏷️', 'The front matter: what goes at the top', '''
<p>Every field is optional, but <code>description</code> matters most: Claude reads it to decide when to use the skill. Put the main use first and include the words people actually type.</p>
<div class="tw"><table class="jt"><tr><th>Field</th><th>What it does</th></tr>
<tr><td><code>name</code></td><td>the command name. Defaults to the folder name.</td></tr>
<tr><td><code>description</code></td><td>what it does and when to use it. With <code>when_to_use</code>, cut at 1,536 characters in the listing.</td></tr>
<tr><td><code>when_to_use</code></td><td>extra trigger phrases or example requests</td></tr>
<tr><td><code>argument-hint</code>, <code>arguments</code></td><td>hint shown while typing, and names for each argument</td></tr>
<tr><td><code>disable-model-invocation</code></td><td><code>true</code>: only you can start it</td></tr>
<tr><td><code>user-invocable</code></td><td><code>false</code>: only Claude can use it, hidden from the menu</td></tr>
<tr><td><code>allowed-tools</code></td><td>tools Claude may use without asking while the skill runs</td></tr>
<tr><td><code>disallowed-tools</code></td><td>tools removed while the skill is active</td></tr>
<tr><td><code>model</code>, <code>effort</code></td><td>model and effort level while the skill is active</td></tr>
<tr><td><code>context</code>, <code>agent</code></td><td><code>context: fork</code> runs it in a subagent of the given type</td></tr>
<tr><td><code>paths</code></td><td>only use it automatically for matching files</td></tr>
<tr><td><code>hooks</code>, <code>shell</code></td><td>hooks while it runs, and <code>bash</code> or <code>powershell</code> for its commands</td></tr>
</table></div>
<div class="vs"><div><b>😕 Weak description</b><code>Helps with invoices</code></div><div><b>😀 Strong description</b><code>Checks supplier invoices for arithmetic errors and missing details. Use when the user shares an invoice CSV or PDF, or asks to verify, audit or check an invoice.</code></div></div>
''', files=['SKILL.md'], kw=['frontmatter', 'description', 'disable-model-invocation', 'user-invocable', 'allowed-tools', 'context fork', 'when_to_use']),
    part('args', '🔣', 'Arguments and live data', '''
<p>Text typed after the skill name becomes its arguments. Use <code>$ARGUMENTS</code> for all of it, <code>$0</code>, <code>$1</code> for each word (counting from zero), or names listed in <code>arguments</code>. Lines with <code>!`command`</code> are replaced by the command's output before Claude sees the skill.</p>
[[standup]]
<p>Here is what Claude actually receives once the arguments and the two <code>!`git ...`</code> commands are filled in on a real repository.</p>
[[render]]
<div class="tw"><table class="jt"><tr><th>Placeholder</th><th>Becomes</th></tr>
<tr><td><code>$ARGUMENTS</code></td><td>everything typed after the name</td></tr>
<tr><td><code>$0</code>, <code>$ARGUMENTS[0]</code></td><td>the first word (use quotes for several words)</td></tr>
<tr><td><code>$person</code></td><td>a named argument from <code>arguments: [person, day]</code></td></tr>
<tr><td><code>${CLAUDE_SKILL_DIR}</code></td><td>the skill's own folder, for scripts</td></tr>
<tr><td><code>${CLAUDE_PROJECT_DIR}</code></td><td>the project root</td></tr>
</table></div>
''', files=['SKILL.md'], kw=['$ARGUMENTS', '$0', 'arguments', 'dynamic context', '!command', 'CLAUDE_SKILL_DIR']),
    part('files', '📎', 'Supporting files and scripts', '''
<p>Keep <code>SKILL.md</code> short (under 500 lines) and put detail in other files in the same folder. Link to them from <code>SKILL.md</code> so Claude knows when to open them. Scripts are <b>run</b>, not read, so a long script costs almost nothing in context.</p>
[[invoice-skill]]
[[checklist]]
[[totals]]
<p>Because the arithmetic comes from a script, the answer is the same every time. Claude spends its effort on the judgment part: what is wrong and how to word the email to the supplier.</p>
''', files=['SKILL.md', 'checklist.md', 'scripts/totals.py'], kw=['supporting files', 'scripts', 'reference files', '500 lines', 'invoice']),
    part('who', '🎛️', 'Who can start a skill', '''
<div class="tw"><table class="jt"><tr><th>Front matter</th><th>You can start it</th><th>Claude can start it</th><th>In context before use</th></tr>
<tr><td>(default)</td><td>yes</td><td>yes</td><td>the description</td></tr>
<tr><td><code>disable-model-invocation: true</code></td><td>yes</td><td>no</td><td>nothing</td></tr>
<tr><td><code>user-invocable: false</code></td><td>no</td><td>yes</td><td>the description</td></tr>
</table></div>
<p>Use <code>disable-model-invocation</code> for anything with side effects, like deploying or sending a message. You do not want Claude deciding to deploy because the code "looks ready".</p>
[[deploy]]
[[voice]]
[[research]]
<div class="warn"><code>allowed-tools</code> skips permission prompts while the skill runs. Read the <code>allowed-tools</code> of skills in a repository before you trust it.</div>
''', files=['SKILL.md'], kw=['disable-model-invocation', 'user-invocable', 'context fork', 'agent', 'side effects']),
    part('daily', '📅', 'Skills for daily work', '''
<p>The best first skills are jobs you already do every week. Here are two more to copy.</p>
[[meeting]]
[[commit]]
<div class="scenario"><b>👩‍💼 Real scenario: an HR team</b>The team makes three skills: <code>offer-letter</code> (fills the template from a candidate sheet), <code>policy-answer</code> (answers staff questions using the policy files in the folder), and <code>exit-checklist</code>. New joiners get the same quality as the senior staff on day one.</div>
''', easy=True, files=['.claude/skills/meeting-actions/SKILL.md', '.claude/skills/commit/SKILL.md'], kw=['daily automation', 'meeting notes', 'commit message', 'skill examples']),
    part('upload', '☁️', 'Skills in claude.ai and the API', '''
<p>The same folder can be uploaded to claude.ai as a ZIP, or sent through the Skills API. Uploads follow the open <b>Agent Skills</b> format, which is stricter than Claude Code:</p>
<ul><li>Only six front matter fields: <code>name</code>, <code>description</code>, <code>license</code>, <code>compatibility</code>, <code>metadata</code>, <code>allowed-tools</code>.</li>
<li><code>name</code>: up to 64 characters, lowercase letters, numbers and hyphens, and it may not contain "anthropic" or "claude".</li>
<li><code>description</code>: not empty, up to 1,024 characters, no XML tags.</li>
<li>Claude Code only features such as <code>!`command`</code> do not work in claude.ai or the API.</li></ul>
[[zip]]
''', files=['SKILL.md', 'skill.zip'], kw=['claude.ai upload', 'Skills API', 'Agent Skills spec', 'zip', 'name rules']),
    part('tips', '💡', 'Make skills that work every time', '''
<ul><li><b>Description first.</b> If a skill does not trigger, add the words people really use to its description.</li>
<li><b>Key steps at the top.</b> After compaction a skill keeps only its first 5,000 tokens.</li>
<li><b>Say what to do</b>, not long reasons. The body stays in context once loaded, so every line has a cost.</li>
<li><b>Scripts for exact work</b> like sums, dates and file conversions.</li>
<li><b>Test it</b> with three real requests, then fix the description or steps. The <code>skill-creator</code> plugin can run tests on a skill for you.</li>
<li><code>/skills</code> lists every skill, and you can sort by token cost to find heavy ones.</li></ul>
''', easy=True, files=['SKILL.md'], kw=['skill tips', 'testing skills', '/skills', 'skill-creator', 'troubleshooting']),
]

LANES = {
    'levels': {'t': 'How Claude reads a skill, layer by layer', 's': 'Step through a request that needs the invoice skill.', 'code': 'session starts\nuser: "check this invoice"\nClaude opens SKILL.md\nClaude runs scripts/totals.py\nClaude opens checklist.md',
               'lanes': ['In the context window', 'Still on disk'], 'tone': [2, 4],
               'steps': [{'l': 1, 'v': [['invoice-checker: description', 'weekly-report: description', 'brand-voice: description'], ['SKILL.md bodies', 'checklist.md', 'scripts/']], 'm': 'At start, only names and descriptions load: about 100 tokens each.'},
                         {'l': 2, 'v': [['invoice-checker: description', 'weekly-report: description', 'brand-voice: description', 'user: check this invoice'], ['SKILL.md bodies', 'checklist.md', 'scripts/']], 'm': 'The request matches the invoice description.'},
                         {'l': 3, 'v': [['descriptions', 'user request', 'invoice-checker SKILL.md'], ['other SKILL.md bodies', 'checklist.md', 'scripts/']], 'm': 'Only that skill\'s body is loaded.'},
                         {'l': 4, 'v': [['descriptions', 'user request', 'invoice-checker SKILL.md', 'output of totals.py'], ['other SKILL.md bodies', 'checklist.md', 'script code']], 'm': 'The script runs. Only its short output enters the context, never its code.'},
                         {'l': 5, 'v': [['descriptions', 'user request', 'invoice-checker SKILL.md', 'output of totals.py', 'checklist.md'], ['other SKILL.md bodies', 'script code']], 'm': 'The checklist is read because SKILL.md pointed to it.'}]},
}

INFO = {'title': 'Skills: teach a task once, use it forever', 'panels': [
    panel([['e', '📁'], ['t', '<name>/SKILL.md', {'b': 1}]], 'A folder', 'SKILL.md plus any helper files.', 'The folder name becomes /name.'),
    panel([['e', '🏷️'], ['t', 'description: ... Use when ...', {'b': 1, 'size': 11}]], 'The description', 'Decides when Claude uses it.', 'Use the words people really type.'),
    panel([['e', '🔣'], ['t', '$ARGUMENTS  !`cmd`', {'b': 1}]], 'Arguments and live data', 'Fill in what you typed and real command output.', 'Claude reads facts, not guesses.'),
    panel([['e', '🎛️'], ['t', 'disable-model-invocation', {'b': 1, 'size': 11}]], 'Control', 'Choose who can start it.', 'Side effects: only you.')],
    'remember': 'Description says when, body says how, scripts do exact work.'}

REAL = [
    ['🧾', 'A finance team', 'An invoice-checker skill with a Python script catches a Rs 4,000 overbilling in its first week, because the script never miscounts.'],
    ['🧑‍💻', 'A developer team', 'A commit skill with allowed-tools for git means every commit message follows the same format without anyone reminding anyone.'],
    ['📣', 'A marketing team', 'A brand-voice skill that only Claude can use keeps every email, post and product page in one voice.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter builds skills step by step: the SKILL dot md file, where it lives, its front matter, arguments, scripts, who can start it and uploading it to claude dot ai.',
        'यह अध्याय skills कदम दर कदम बनाता है: SKILL.md, उसकी जगह, front matter, arguments, scripts और upload।',
        'ಈ ಅಧ್ಯಾಯ skills ಹಂತ ಹಂತವಾಗಿ ಕಟ್ಟುತ್ತದೆ: SKILL.md, ಸ್ಥಳ, front matter, arguments, scripts, upload.',
        'ଏହି ଅଧ୍ୟାୟ skills ପାଦେ ପାଦେ ତିଆରି କରେ: SKILL.md, ସ୍ଥାନ, front matter, arguments, scripts, upload.',
        'يبني هذا الفصل المهارات خطوة بخطوة: ملف SKILL.md ومكانه والترويسة والوسائط والسكربتات والرفع.',
        'Dieses Kapitel baut Skills Schritt für Schritt: SKILL.md, Speicherort, Frontmatter, Argumente, Skripte und Upload.'),
    say('what', 'What a skill is', 'A skill is a folder with SKILL dot md. Claude reads only the description at first, the body when needed, and other files only if pointed to.',
        'Skill एक folder है जिसमें SKILL.md है। पहले सिर्फ description, फिर ज़रूरत पर बाकी।',
        'Skill ಎಂದರೆ SKILL.md ಇರುವ folder. ಮೊದಲು description ಮಾತ್ರ, ನಂತರ ಉಳಿದವು.',
        'Skill ହେଉଛି SKILL.md ଥିବା folder. ପ୍ରଥମେ description, ପରେ ବାକି।',
        'المهارة مجلد فيه SKILL.md. يُقرأ الوصف أولًا ثم المحتوى عند الحاجة.',
        'Ein Skill ist ein Ordner mit SKILL.md. Erst die Beschreibung, der Rest bei Bedarf.'),
    say('first', 'First skill', 'Make a folder in the skills directory, write SKILL dot md with a description and steps, then ask naturally or type slash and its name.',
        'Skills directory में folder बनाएं, SKILL.md लिखें, फिर /name से चलाएं।',
        'Skills directory ನಲ್ಲಿ folder ಮಾಡಿ, SKILL.md ಬರೆಯಿರಿ, /name ಬಳಸಿ.',
        'Skills directory ରେ folder କରନ୍ତୁ, SKILL.md ଲେଖନ୍ତୁ, /name ଚଲାନ୍ତୁ।',
        'أنشئ مجلدًا واكتب SKILL.md ثم اطلبه أو اكتب / واسمه.',
        'Ordner anlegen, SKILL.md schreiben, dann normal fragen oder /Name tippen.'),
    say('where', 'Locations', 'Personal skills go in the home dot claude skills folder, team skills in the project. There is no single skills dot md file.',
        'Personal skills ~/.claude/skills में, team skills project में। कोई skills.md file नहीं।',
        'Personal skills ~/.claude/skills ನಲ್ಲಿ, team skills project ನಲ್ಲಿ. skills.md ಇಲ್ಲ.',
        'Personal skills ~/.claude/skills ରେ, team skills project ରେ। skills.md ନାହିଁ।',
        'المهارات الشخصية في ~/.claude/skills ومهارات الفريق في المشروع. لا يوجد ملف skills.md.',
        'Persönliche Skills in ~/.claude/skills, Team-Skills im Projekt. Eine skills.md gibt es nicht.'),
    say('front', 'Front matter', 'The description decides when Claude uses a skill. Other fields control the name, arguments, tools, model and who can start it.',
        'Description तय करता है कि skill कब चले। बाकी fields नाम, tools और model तय करते हैं।',
        'Description skill ಯಾವಾಗ ಬಳಕೆ ಎಂದು ನಿರ್ಧರಿಸುತ್ತದೆ.',
        'Description ସ୍ଥିର କରେ skill କେବେ ଚାଲିବ।',
        'الوصف يحدد متى تُستخدم المهارة، وبقية الحقول تضبط الاسم والأدوات والنموذج.',
        'Die Beschreibung entscheidet, wann der Skill genutzt wird.'),
    say('args', 'Arguments', 'Dollar ARGUMENTS holds what you typed. Lines with an exclamation mark command are replaced by real command output before Claude reads them.',
        '$ARGUMENTS में आपका लिखा होता है। ! command की जगह असली output आता है।',
        '$ARGUMENTS ನಲ್ಲಿ ನೀವು ಟೈಪ್ ಮಾಡಿದ್ದು. ! command ಬದಲು ನಿಜ output.',
        '$ARGUMENTS ରେ ଆପଣ ଲେଖିଥିବା। ! command ବଦଳରେ ପ୍ରକୃତ output.',
        '$ARGUMENTS تحمل ما كتبته، وأسطر الأوامر تُستبدل بمخرجاتها الحقيقية.',
        '$ARGUMENTS enthält deine Eingabe. Befehlszeilen werden durch echte Ausgabe ersetzt.'),
    say('files', 'Supporting files', 'Keep SKILL dot md short. Put details in other files and exact work in scripts. Scripts run, only their output is read.',
        'SKILL.md छोटा रखें। विवरण दूसरी files में और सटीक काम scripts में।',
        'SKILL.md ಚಿಕ್ಕದು. ವಿವರ ಇತರ files ನಲ್ಲಿ, ನಿಖರ ಕೆಲಸ scripts ನಲ್ಲಿ.',
        'SKILL.md ଛୋଟ ରଖନ୍ତୁ। ବିବରଣୀ ଅନ୍ୟ files ରେ, ସଠିକ୍ କାମ scripts ରେ।',
        'اجعل SKILL.md قصيرًا وضع التفاصيل في ملفات أخرى والعمل الدقيق في سكربتات.',
        'SKILL.md kurz halten, Details in andere Dateien, exakte Arbeit in Skripte.'),
    say('who', 'Who starts it', 'Disable model invocation means only you can start it. User invocable false means only Claude can use it.',
        'disable-model-invocation से सिर्फ आप, user-invocable false से सिर्फ Claude।',
        'disable-model-invocation ಆದರೆ ನೀವು ಮಾತ್ರ, user-invocable false ಆದರೆ Claude ಮಾತ್ರ.',
        'disable-model-invocation ହେଲେ କେବଳ ଆପଣ, user-invocable false ହେଲେ କେବଳ Claude.',
        'disable-model-invocation يعني أنت فقط، وuser-invocable false يعني Claude فقط.',
        'disable-model-invocation: nur du. user-invocable false: nur Claude.'),
    say('daily', 'Daily skills', 'Start with jobs you already do every week, like meeting notes to actions and commit messages.',
        'हर हफ्ते के कामों से शुरू करें, जैसे meeting notes और commit messages।',
        'ಪ್ರತಿ ವಾರದ ಕೆಲಸಗಳಿಂದ ಆರಂಭಿಸಿ.',
        'ପ୍ରତି ସପ୍ତାହର କାମରୁ ଆରମ୍ଭ କରନ୍ତୁ।',
        'ابدأ بمهام أسبوعية مثل محاضر الاجتماعات ورسائل الإيداع.',
        'Beginne mit wöchentlichen Aufgaben wie Meeting-Notizen und Commit-Nachrichten.'),
    say('upload', 'Uploading', 'claude dot ai and the API accept only six front matter fields, and the name must be lowercase without the words anthropic or claude.',
        'claude.ai और API सिर्फ छह fields मानते हैं, नाम lowercase हो।',
        'claude.ai ಮತ್ತು API ಆರು fields ಮಾತ್ರ, ಹೆಸರು lowercase.',
        'claude.ai ଓ API କେବଳ ଛଅଟି fields, ନାମ lowercase.',
        'claude.ai والواجهة البرمجية تقبلان ستة حقول فقط، والاسم بحروف صغيرة.',
        'claude.ai und die API akzeptieren nur sechs Felder, der Name klein geschrieben.'),
    say('tips', 'Tips', 'Write a strong description, put key steps first, use scripts for exact work, and test with real requests.',
        'मज़बूत description, ज़रूरी कदम ऊपर, scripts और असली परीक्षण।',
        'ಬಲವಾದ description, ಮುಖ್ಯ ಹಂತ ಮೇಲೆ, scripts, ನಿಜ ಪರೀಕ್ಷೆ.',
        'ଶକ୍ତ description, ମୁଖ୍ୟ ପାଦ ଉପରେ, scripts, ପ୍ରକୃତ ପରୀକ୍ଷା।',
        'وصف قوي وخطوات مهمة أولًا وسكربتات واختبار حقيقي.',
        'Starke Beschreibung, wichtige Schritte zuerst, Skripte und echte Tests.'),
    say('practice', 'Practice', 'Practise reading front matter, filling arguments and checking skill names in code.',
        'Front matter पढ़ने, arguments भरने और नाम जांचने का अभ्यास।',
        'Front matter, arguments ಮತ್ತು ಹೆಸರು ಪರಿಶೀಲನೆಯ ಅಭ್ಯಾಸ.',
        'Front matter, arguments ଓ ନାମ ଯାଞ୍ଚର ଅଭ୍ୟାସ।',
        'تدرّب على قراءة الترويسة وملء الوسائط وفحص الأسماء.',
        'Übe Frontmatter lesen, Argumente füllen und Namen prüfen.'),
]

QUIZ = [
    quiz('e', 'What is the file inside every skill folder called?', ['SKILL.md', 'skills.md', 'skill.json', 'README.md'], 0, 'Capital letters.', 'Each skill is a folder containing SKILL.md.'),
    quiz('e', 'Where do personal skills for all your projects go?', ['~/.claude/skills/<name>/', '.claude/skills/<name>/', 'CLAUDE.md', '.mcp.json'], 0, 'Home folder.', 'Personal skills load in every project on your machine.'),
    quiz('e', 'Which field helps Claude decide when to use a skill?', ['description', 'license', 'shell', 'metadata'], 0, 'It says when.', 'Write the main use first, with words people really type.'),
    quiz('m', 'Before a skill is used, what is in Claude\'s context?', ['Its name and description', 'The whole folder', 'Only its scripts', 'Nothing at all'], 0, 'Level 1.', 'Bodies and files load only when needed.'),
    quiz('m', 'You run /fix-issue 123. What does $ARGUMENTS become?', ['123', 'fix-issue', 'The whole skill', 'Nothing'], 0, 'What follows the name.', 'Everything typed after the skill name.'),
    quiz('m', 'Which setting stops Claude from starting a deploy skill by itself?', ['disable-model-invocation: true', 'user-invocable: false', 'context: fork', 'model: haiku'], 0, 'Model invocation.', 'Only you can start it with /deploy.'),
    quiz('h', 'What does !`git diff HEAD` do inside a skill?', ['Runs the command first and pastes its output in', 'Shows the command to Claude', 'Deletes the diff', 'Asks Claude to run it later'], 0, 'Dynamic context.', 'Claude receives the real output, not the command.'),
    quiz('h', 'Why put sums in a script instead of asking Claude to add up numbers?', ['Scripts give the same exact result every time and cost little context', 'Claude cannot add', 'Scripts are required', 'It is faster to type'], 0, 'Deterministic.', 'Only the script output is read, and the arithmetic never varies.'),
    quiz('x', 'A skill with argument-hint fails to upload to claude.ai. Why?', ['argument-hint is not one of the six allowed upload fields', 'The ZIP is too small', 'Skills cannot be uploaded', 'The description is too short'], 0, 'Stricter format.', 'Uploads allow name, description, license, compatibility, metadata and allowed-tools.'),
    quiz('x', 'Which name is valid for a claude.ai upload?', ['invoice-checker', 'Invoice Checker', 'claude-helper', 'my_skill!'], 0, 'Lowercase, hyphens, no reserved words.', 'Spaces, capitals, symbols and the word claude are not allowed.'),
]

CALC = [
    calc('e', 'You have 12 skills with descriptions of about 100 tokens each. How many tokens before any is used?', '1200', 'Multiply.', ['<span class="eq">12 × 100 = 1,200</span>'], alt=['1,200']),
    calc('e', 'In /migrate SearchBar JavaScript TypeScript, what is $2?', 'TypeScript', 'Count from zero.', ['$0 is SearchBar, $1 is JavaScript, $2 is TypeScript.']),
    calc('m', 'What computed total did totals.py print for inv-001.csv?', '3596', 'Read the output.', ['<span class="eq">2,450 + 720 + 426 = 3,596</span>'], alt=['3596.00', '3,596']),
    calc('m', 'Whiteboard markers: 12 at 35.50. What should the line amount be?', '426', 'qty times rate.', ['<span class="eq">12 × 35.50 = 426.00</span>'], alt=['426.00']),
    calc('h', 'The invoice stated 462.00 for the markers. By how much is that line overbilled?', '36', 'Stated minus correct.', ['<span class="eq">462 − 426 = 36</span>'], alt=['36.00']),
    calc('x', 'What is the longest description, in characters, that a claude.ai skill upload accepts?', '1024', 'From the spec.', ['Up to 1,024 characters, not empty, no XML tags.'], alt=['1,024']),
]

EX = []

T = {
    'slug': 'claude-skills', 'title': 'Skills: Build SKILL.md Step by Step', 'short': 'Skills', 'emoji': '🧰', 'module': MODULE, 'minutes': 20,
    'lead': 'Build a skill from an empty folder, learn where skills live and how they are named, every front matter field, arguments and live command output, supporting files and scripts, who can start a skill, real skills for daily work, and the stricter rules for uploading to claude.ai.',
    'plain': 'A skill is a recipe card for Claude. You write the steps once in a file called SKILL.md, and Claude follows the card whenever that job comes up.',
    'desc': 'Claude skills explained: SKILL.md, progressive disclosure, skill locations, frontmatter fields, $ARGUMENTS, dynamic context, scripts, disable-model-invocation, claude.ai upload rules.',
    'summary': 'What a skill is and its three loading levels, a first skill in three steps, personal, project and plugin locations and command names, every front matter field with good and weak descriptions, arguments and dynamic context with what Claude receives, supporting files and a Python script checking a real invoice, invocation control, daily work skills, the claude.ai upload rules, and tips for reliable skills.',
    'keywords': ['skills', 'SKILL.md', 'Skills.md', 'frontmatter', 'description', '$ARGUMENTS', 'dynamic context', 'allowed-tools', 'disable-model-invocation', 'user-invocable', 'context fork', 'claude.ai upload', 'Agent Skills', 'progressive disclosure'],
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
