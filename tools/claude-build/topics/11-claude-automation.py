# Chapter 11: daily automation. Plugins that bundle everything, claude -p in scripts, structured output,
# GitHub Actions, schedules and a set of ready to use daily recipes.
from ckit import part, test, show, md, cli, prompt, js_, say, quiz, calc, panel

MODULE = ('🛠️', 'Claude Code and its files', 'claude-code-files', 'Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.')

MANIFEST = '''
{
  "name": "team-toolkit",
  "description": "Our review agent, release notes skill, format hook and docs MCP server",
  "version": "1.0.0",
  "author": { "name": "Platform team" }
}
'''

SKILL = '''
---
name: release-notes
description: Write release notes from the git log since the last tag. Use when asked for release notes or a changelog.
disable-model-invocation: true
---

1. Run `git describe --tags --abbrev=0` to find the last tag.
2. Run `git log <tag>..HEAD --oneline`.
3. Group commits into Added, Changed and Fixed. Skip merge commits.
4. Write each line for a customer, not a developer.
'''

HOOKS = '''
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "ruff format \\"$CLAUDE_PROJECT_DIR\\"/src" }]
      }
    ]
  }
}
'''

READ_JSON = r'''
# read_result.py: a script reading the JSON that claude -p --output-format json prints.
# result.json below is a hand written example of that shape, so the script can run here without a login.
import json
import sys

r = json.load(open("result.json"))
if r["is_error"] or "structured_output" not in r:
    sys.exit("Claude did not return the data: " + r["result"])

invoices = r["structured_output"]["invoices"]
overdue = [i for i in invoices if i["days_late"] > 30]
print(f"{len(invoices)} invoices, {len(overdue)} more than 30 days late:")
for i in overdue:
    print(f" - {i['customer']}: ₹{i['amount']:,} ({i['days_late']} days)")
print(f"cost of this run: ${r['total_cost_usd']:.4f}")
'''

RESULT = '''
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "result": "Found 4 invoices.",
  "session_id": "9f1c2e7a-0000-4000-8000-000000000000",
  "total_cost_usd": 0.0213,
  "structured_output": {
    "invoices": [
      { "customer": "Sharma Traders", "amount": 48000, "days_late": 45 },
      { "customer": "Green Leaf Cafe", "amount": 7200, "days_late": 12 },
      { "customer": "Patel Hardware", "amount": 125000, "days_late": 61 },
      { "customer": "City Clinic", "amount": 15500, "days_late": 0 }
    ]
  }
}
'''

CODES = {
    'tree': show('''
team-toolkit/
├── .claude-plugin/
│   └── plugin.json          the manifest: name, description, version, author
├── skills/
│   └── release-notes/
│       └── SKILL.md         becomes /team-toolkit:release-notes
├── agents/
│   └── reviewer.md          a subagent
├── hooks/
│   └── hooks.json           { "hooks": { ... } } same shape as in settings.json
└── .mcp.json                MCP servers the plugin brings
''', 'A complete plugin', lang='text', note='📂 Folder layout'),
    'manifest': js_(MANIFEST, 'team-toolkit/.claude-plugin/plugin.json'),
    'plugin-cmds': cli('''
claude plugin validate ./team-toolkit        # check the manifest and frontmatter
claude --plugin-dir ./team-toolkit           # try it in one session
/team-toolkit:release-notes                  # run its skill

/plugin marketplace add anthropics/claude-plugins-official
/plugin install plugin-dev@claude-plugins-official
/plugin-dev:create-plugin a plugin with our review agent and release notes skill
''', 'Build, test and install plugins', result='validate prints ✔ Validation passed or names each field to fix. --plugin-dir loads the plugin for that session only.'),
    'plugin-skill': md(SKILL, 'team-toolkit/skills/release-notes/SKILL.md'),
    'plugin-hooks': js_(HOOKS, 'team-toolkit/hooks/hooks.json'),
    'headless': cli('''
# Ask once and print the answer
claude -p "What does the auth module do?"

# Pipe data in, write the answer out
cat build-error.txt | claude -p "explain the root cause in 3 lines" > why.txt

# Let it use only some tools, without prompts
claude -p "Run the tests and fix failures" --allowedTools "Bash,Read,Edit"

# Same result on every machine: skip local CLAUDE.md, hooks, plugins and MCP
claude --bare -p "Summarize README.md" --allowedTools "Read"

# Carry on the same conversation
claude -p "Review this codebase for performance issues"
claude -p "Now focus on the database queries" --continue
''', 'claude -p: Claude Code inside any script', result='Exit code 0 means success, so scripts can check it. --bare needs ANTHROPIC_API_KEY because it skips your login.'),
    'schema': cli('''
claude -p "Read invoices/*.pdf and list each customer, amount and days late" \\
  --allowedTools "Read" \\
  --output-format json \\
  --json-schema '{"type":"object","properties":{"invoices":{"type":"array","items":{"type":"object","properties":{"customer":{"type":"string"},"amount":{"type":"number"},"days_late":{"type":"integer"}},"required":["customer","amount","days_late"]}}},"required":["invoices"]}' \\
  > result.json
''', 'Ask for data in a fixed shape'),
    'read-json': test({'result.json': RESULT, 'read_result.py': READ_JSON}, '$PY read_result.py', 'Use the structured output in a script',
                      show=['result.json', 'read_result.py'], shown_cmd='python read_result.py', badge='▶ Runs on an example of the JSON shape'),
    'gha-setup': cli('''
gh auth login            # once, so Claude Code can talk to GitHub
claude
/install-github-app      # installs the app, saves the secret, opens a pull request with the workflow
''', 'Set up GitHub Actions the quick way'),
    'gha-mention': show('''
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
''', '.github/workflows/claude.yml: answer @claude in issues and pull requests', lang='yaml', note='📄 Ready to copy'),
    'gha-daily': show('''
name: Daily Report
on:
  schedule:
    - cron: "30 3 * * 1-5"      # 09:00 in India on weekdays
jobs:
  report:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: read
      id-token: write
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Summarize yesterday's commits and open issues for the stand-up"
          claude_args: |
            --model claude-sonnet-5-5
            --max-turns 10
            --allowedTools "mcp__github__list_commits,mcp__github__list_issues"
''', '.github/workflows/daily-report.yml: a weekday morning report', lang='yaml', note='📄 Ready to copy'),
    'loop': prompt('''
/loop 10m check whether the staging deploy finished and tell me when it does
/loop 1h /release-notes
''', 'Repeat something during a session', result='/loop runs a prompt or a slash command again on an interval while the session is open. Leave out the interval and Claude picks the pace.'),
    'recipes': cli('''
# 1. Commit message from staged changes
claude -p "Write a commit message for my staged changes and commit" \\
  --allowedTools "Bash(git diff *),Bash(git status *),Bash(git commit *)"

# 2. Typo check on a pull request diff
git diff main | claude -p "list each typo as file:line then the fix. nothing else."

# 3. Meeting notes to action items
claude -p "Turn notes/standup.md into a table of owner, task and due date" > actions.md

# 4. Clean a messy spreadsheet export
claude -p "Read sales.csv, fix the date formats to YYYY-MM-DD, remove duplicate rows, save clean.csv" \\
  --allowedTools "Read,Write"

# 5. Explain a failing build in CI
python -m pytest 2>&1 | tail -80 | claude -p "explain why this failed and the smallest fix"
''', 'Five daily recipes'),
}

PARTS = [
    part('plugins', '📦', 'Plugins: share your whole setup in one folder', '''
<p>By now you have skills, agents, hooks and MCP servers. A <b>plugin</b> puts them in one folder so a whole team can install them with one command. Use plain <code>.claude/</code> files for one project, and a plugin when several projects or people need the same setup.</p>
[[tree]]
[[manifest]]
<div class="cl-put"><b>What goes where:</b> only <code>plugin.json</code> goes inside <code>.claude-plugin/</code>. Skills, agents, <code>hooks/hooks.json</code> and <code>.mcp.json</code> sit next to that folder at the plugin root. Plugin skills are called with the plugin name in front, such as <code>/team-toolkit:release-notes</code>.</div>
[[plugin-skill]]
[[plugin-hooks]]
<div class="tw"><table class="jt"><tr><th>Common mistake</th><th>What happens</th><th>Fix</th></tr>
<tr><td><code>"name": "broken kit"</code></td><td>a plugin name may not contain spaces</td><td><code>"name": "broken-kit"</code></td></tr>
<tr><td><code>.claude-plugin/skills.md</code></td><td>never loads, only <code>plugin.json</code> goes in that folder</td><td>move skills to <code>skills/&lt;name&gt;/SKILL.md</code></td></tr>
<tr><td><code>skills/notes/README.md</code></td><td>the skill folder has no <code>SKILL.md</code>, so there is no skill</td><td>rename it to <code>SKILL.md</code> with front matter</td></tr></table></div>
[[plugin-cmds]]
''', easy=True, files=['.claude-plugin/plugin.json', 'skills/', 'agents/', 'hooks/hooks.json', '.mcp.json'], kw=['plugin', 'plugin.json', 'manifest', 'marketplace', '--plugin-dir', 'claude plugin validate']),
    part('headless', '🧾', 'claude -p: use Claude in scripts', '''
<p>The <code>-p</code> flag runs Claude Code once, prints the answer and exits. That makes it a normal command you can put in shell scripts, Makefiles and scheduled jobs.</p>
[[headless]]
<div class="tw"><table class="jt"><tr><th>Flag</th><th>What it does</th></tr>
<tr><td><code>--allowedTools</code></td><td>tools it may use without asking, in permission rule syntax</td></tr>
<tr><td><code>--permission-mode</code></td><td>a baseline such as <code>acceptEdits</code> or <code>dontAsk</code></td></tr>
<tr><td><code>--output-format</code></td><td><code>text</code>, <code>json</code> or <code>stream-json</code></td></tr>
<tr><td><code>--json-schema</code></td><td>the exact shape of data you want back</td></tr>
<tr><td><code>--append-system-prompt</code></td><td>extra instructions on top of the default</td></tr>
<tr><td><code>--bare</code></td><td>skip local hooks, skills, plugins, MCP and CLAUDE.md for repeatable runs</td></tr></table></div>
''', easy=True, kw=['claude -p', 'headless', '--allowedTools', '--bare', '--continue', 'scripts']),
    part('json', '🧮', 'Get data back, not just text', '''
<p>Ask for JSON in a fixed shape with <code>--json-schema</code>. The data arrives in the <code>structured_output</code> field, ready for the next step of your script.</p>
[[schema]]
[[read-json]]
<p>Always check that <code>structured_output</code> is there before you use it. If Claude could not do the task, the field is missing.</p>
''', kw=['--output-format json', '--json-schema', 'structured_output', 'total_cost_usd', 'jq']),
    part('gha', '🐙', 'Claude in GitHub Actions', '''
<ol class="steps"><li>Run <code>/install-github-app</code> in Claude Code inside your repository.</li>
<li>It installs the Claude GitHub App and saves a secret named <code>ANTHROPIC_API_KEY</code> (or <code>CLAUDE_CODE_OAUTH_TOKEN</code> for a subscription).</li>
<li>Merge the pull request it opens with the workflow file.</li>
<li>Write <code>@claude</code> in an issue or pull request comment.</li></ol>
[[gha-setup]]
[[gha-mention]]
<div class="cl-put"><b>Never</b> paste a key into a workflow file. Always use <code>${{ secrets.ANTHROPIC_API_KEY }}</code>. Put your review standards in <code>CLAUDE.md</code>, because the action reads it too.</div>
''', easy=True, files=['.github/workflows/claude.yml'], kw=['GitHub Actions', 'claude-code-action', '@claude', '/install-github-app', 'secrets']),
    part('schedule', '⏰', 'Run it on a schedule', '''
<p>With a <code>prompt</code> input, the action runs on any event, including a timer. GitHub schedules use cron lines in UTC.</p>
[[gha-daily]]
<div class="tw"><table class="jt"><tr><th>Cron line (minute hour day month weekday)</th><th>When it runs</th></tr>
<tr><td><code>0 9 * * *</code></td><td>every day at 09:00 UTC</td></tr>
<tr><td><code>30 3 * * 1-5</code></td><td>every weekday at 03:30 UTC, which is 09:00 in India</td></tr>
<tr><td><code>0 17 * * 5</code></td><td>every Friday at 17:00 UTC</td></tr>
<tr><td><code>0 6 1 * *</code></td><td>on day 1 of every month at 06:00 UTC</td></tr></table></div>
<p>A plain prompt gets no shell or GitHub tools until you allow them in <code>claude_args</code>. GitHub runs schedules only from the default branch.</p>
[[loop]]
''', files=['.github/workflows/daily-report.yml'], kw=['schedule', 'cron', 'UTC', 'claude_args', '--max-turns', '/loop']),
    part('recipes', '🍳', 'Daily automation recipes', '''
[[recipes]]
<div class="scenario"><b>🏢 Real scenario: an accounts team</b>Every Monday a scheduled job runs the invoice script from this chapter. It reads the PDFs, returns JSON, and the script posts the list of invoices more than 30 days late to the team channel. Nobody opens a spreadsheet.</div>
<div class="cl-put"><b>A safe recipe has four parts:</b> a clear prompt, the smallest <code>--allowedTools</code> list, an output you can check (a file, JSON or an exit code), and <code>--max-turns</code> so it cannot run for ever.</div>
''', easy=True, kw=['automation recipes', 'commit message', 'meeting notes', 'CSV cleaning', 'CI failure']),
]

INFO = {'title': 'Automate daily work with Claude', 'panels': [
    panel([['e', '📦'], ['t', 'plugin.json', {'b': 1}]], 'Plugins', 'Skills, agents, hooks and MCP in one folder.', 'Install with /plugin install.'),
    panel([['e', '🧾'], ['t', 'claude -p', {'b': 1}]], 'Scripts', 'Run once, print, exit.', 'Check the exit code.'),
    panel([['e', '🧮'], ['t', '--json-schema', {'b': 1}]], 'Data', 'Get structured_output back.', 'Feed it to the next step.'),
    panel([['e', '🐙'], ['t', '@claude', {'b': 1}]], 'GitHub', 'Mentions, reviews and schedules.', 'Keys only in secrets.')],
    'remember': 'Small prompt, few tools, checkable output, turn limit.'}

REAL = [
    ['🛒', 'An online shop', 'A nightly job asks Claude for any product page with a missing price or image and opens one issue listing them.'],
    ['🏦', 'A finance team', 'Uses claude -p with a JSON schema to read vendor invoices and load them straight into their accounts sheet.'],
    ['👩‍💻', 'An open source project', 'Answers @claude in issues and reviews every pull request with the code-review plugin.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter turns Claude into everyday automation: plugins, scripts, structured data, GitHub Actions and schedules.',
        'यह अध्याय Claude से रोज़ का automation बनाता है: plugins, scripts, GitHub Actions।',
        'ಈ ಅಧ್ಯಾಯ Claude ಮೂಲಕ ದಿನನಿತ್ಯದ automation ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ Claude ଦ୍ୱାରା ଦୈନିକ automation ଶିଖାଏ।',
        'يحوّل هذا الفصل Claude إلى أتمتة يومية: إضافات وسكربتات وGitHub Actions.',
        'Dieses Kapitel macht Claude zur Alltagsautomatisierung: Plugins, Skripte, GitHub Actions.'),
    say('plugins', 'Plugins', 'A plugin bundles skills, agents, hooks and MCP servers. Only plugin dot json goes in the dot claude plugin folder.',
        'Plugin skills, agents, hooks और MCP को एक folder में रखता है।',
        'Plugin skills, agents, hooks, MCP ಅನ್ನು ಒಂದೇ folder ನಲ್ಲಿ ಇಡುತ್ತದೆ.',
        'Plugin skills, agents, hooks ଓ MCP କୁ ଗୋଟିଏ folder ରେ ରଖେ।',
        'الإضافة تجمع المهارات والوكلاء والخطافات وخوادم MCP في مجلد واحد.',
        'Ein Plugin bündelt Skills, Agenten, Hooks und MCP-Server in einem Ordner.'),
    say('headless', 'Scripts', 'Dash p runs Claude once and exits, so it works inside scripts. Limit tools with allowed tools.',
        '-p Claude को एक बार चलाकर बंद करता है, scripts में काम आता है।',
        '-p Claude ಅನ್ನು ಒಮ್ಮೆ ಚಲಾಯಿಸಿ ನಿಲ್ಲಿಸುತ್ತದೆ.',
        '-p Claude କୁ ଥରେ ଚଲାଇ ବନ୍ଦ କରେ।',
        'الخيار -p يشغّل Claude مرة واحدة ثم يخرج، فيعمل داخل السكربتات.',
        '-p startet Claude einmal und beendet sich, ideal für Skripte.'),
    say('json', 'Data', 'Ask for a JSON schema and read the structured output field in your script.',
        'JSON schema माँगें और structured_output पढ़ें।',
        'JSON schema ಕೇಳಿ, structured_output ಓದಿ.',
        'JSON schema ମାଗି structured_output ପଢନ୍ତୁ।',
        'اطلب مخطط JSON واقرأ الحقل structured_output.',
        'Fordere ein JSON-Schema an und lies structured_output.'),
    say('gha', 'GitHub', 'Install the GitHub app from Claude Code, keep the key in secrets, and mention at Claude in a comment.',
        'GitHub app लगाएँ, key secrets में रखें, comment में @claude लिखें।',
        'GitHub app ಹಾಕಿ, key secrets ನಲ್ಲಿ ಇಡಿ, @claude ಬರೆಯಿರಿ.',
        'GitHub app ଲଗାନ୍ତୁ, key secrets ରେ ରଖନ୍ତୁ, @claude ଲେଖନ୍ତୁ।',
        'ثبّت تطبيق GitHub واحفظ المفتاح في الأسرار واكتب @claude في تعليق.',
        'Installiere die GitHub-App, lege den Schlüssel in Secrets ab und erwähne @claude.'),
    say('schedule', 'Schedules', 'A cron line runs the action on a timer in UTC. Allow only the tools the prompt needs.',
        'Cron line UTC में समय पर action चलाती है।',
        'Cron line UTC ನಲ್ಲಿ action ಚಲಾಯಿಸುತ್ತದೆ.',
        'Cron line UTC ରେ action ଚଲାଏ।',
        'سطر cron يشغّل الإجراء في موعد بتوقيت UTC.',
        'Eine Cron-Zeile startet die Action nach Zeitplan in UTC.'),
    say('recipes', 'Recipes', 'Commit messages, typo checks, action items, clean spreadsheets and failed builds, each a one line command.',
        'Commit message, typo check, action items, साफ़ spreadsheet, हर एक एक line में।',
        'Commit message, typo, action items, spreadsheet, ಒಂದೇ line.',
        'Commit message, typo, action items, spreadsheet, ଗୋଟିଏ line ରେ।',
        'رسائل الإيداع والأخطاء الإملائية والمهام والجداول، كل منها بسطر واحد.',
        'Commit-Nachrichten, Tippfehler, Aufgaben und Tabellen, jeweils eine Zeile.'),
    say('practice', 'Practice', 'Test yourself on plugin layout, flags and cron times.',
        'Plugin layout, flags और cron का अभ्यास।',
        'Plugin layout, flags, cron ಅಭ್ಯಾಸ.',
        'Plugin layout, flags ଓ cron ଅଭ୍ୟାସ।',
        'تدرّب على بنية الإضافة والخيارات وأوقات cron.',
        'Übe Plugin-Aufbau, Flags und Cron-Zeiten.'),
]

QUIZ = [
    quiz('e', 'What is the only file inside .claude-plugin/?', ['plugin.json', 'SKILL.md', 'hooks.json', '.mcp.json'], 0, 'The manifest.', 'Everything else sits at the plugin root.'),
    quiz('e', 'What does claude -p do?', ['Runs once, prints the answer and exits', 'Opens plan mode', 'Prints the price', 'Pauses Claude'], 0, 'Print mode.', 'It makes Claude usable in scripts.'),
    quiz('e', 'Where should the API key for GitHub Actions be?', ['In repository secrets', 'In the workflow file', 'In CLAUDE.md', 'In the README'], 0, 'Never in a file.', 'Use ${{ secrets.ANTHROPIC_API_KEY }}.'),
    quiz('m', 'How is the release-notes skill in the team-toolkit plugin called?', ['/team-toolkit:release-notes', '/release-notes', '/plugin release-notes', '@release-notes'], 0, 'Plugin name first.', 'Plugin skills are namespaced.'),
    quiz('m', 'Which flag makes a script run the same on every machine?', ['--bare', '--verbose', '--continue', '--debug'], 0, 'Skips local setup.', 'It skips hooks, plugins, MCP, memory and CLAUDE.md.'),
    quiz('m', 'Where does --json-schema data appear?', ['structured_output', 'result', 'session_id', 'stdout only as text'], 0, 'Structured.', 'Check it is present before use.'),
    quiz('h', 'What does "0 9 * * *" mean in a GitHub schedule?', ['Every day at 09:00 UTC', 'Every 9 minutes', 'At 09:00 local time', 'On the 9th'], 0, 'UTC.', 'GitHub cron lines are in UTC.'),
    quiz('h', 'Why add --max-turns to an unattended run?', ['So it cannot run for ever', 'To make it smarter', 'To save the key', 'It is required'], 0, 'A safety limit.', 'It caps the number of turns.'),
    quiz('x', 'Bash(git diff *) allows which command?', ['git diff --staged', 'git diff-index', 'git push', 'rm -rf'], 0, 'The space before * matters.', 'Without the space it would also match git diff-index.'),
    quiz('x', 'A broken plugin has skills.md inside .claude-plugin/. What happens?', ['It does not load', 'It loads as a skill', 'It replaces plugin.json', 'Claude asks'], 0, 'Wrong place.', 'Components saved there do not load.'),
]

CALC = [
    calc('e', 'In the invoice example, how many invoices are more than 30 days late?', '2', 'Read the output.', ['Sharma Traders (45) and Patel Hardware (61).']),
    calc('e', 'What is their total in rupees?', '173000', 'Add them.', ['<span class="eq">48,000 + 1,25,000 = 1,73,000</span>'], alt=['1,73,000', '173,000']),
    calc('m', 'You want 09:00 in India (UTC + 5:30). What UTC hour and minute is that? Answer as HH:MM.', '03:30', 'Subtract 5:30.', ['<span class="eq">09:00 − 05:30 = 03:30</span>'], alt=['3:30']),
    calc('m', 'A daily job costs $0.02 a run on weekdays only. About how many dollars in a 22 working day month?', '0.44', 'Multiply.', ['<span class="eq">22 × 0.02 = 0.44</span>'], alt=['$0.44']),
    calc('h', 'How many mistakes does the table list for the broken plugin?', '3', 'Count the rows.', ['A space in the name, a file inside .claude-plugin and a skill folder with no SKILL.md.']),
    calc('x', 'A team of 12 each saves 15 minutes a day with recipes. Hours saved in 22 working days?', '66', 'People × minutes × days ÷ 60.', ['<span class="eq">12 × 15 × 22 ÷ 60 = 66</span>']),
]

EX = []

T = {
    'slug': 'claude-automation', 'title': 'Daily Automation: Plugins, Scripts and GitHub', 'short': 'Daily automation', 'emoji': '⚙️', 'module': MODULE, 'minutes': 18,
    'lead': 'Bundle skills, agents, hooks and MCP into a plugin, run Claude inside scripts with claude -p, get JSON back with a schema, answer @claude in GitHub, run reports on a schedule, and five copy and paste recipes for daily work.',
    'plain': 'Instead of opening Claude and typing every morning, you write the request once and let the computer run it for you every day.',
    'desc': 'Automate daily work with Claude Code: plugins and plugin.json, claude -p in scripts, --json-schema structured output, GitHub Actions with claude-code-action, cron schedules and ready to use recipes.',
    'summary': 'A full plugin layout with its skill and hooks files and three common mistakes, plugin commands and marketplaces, claude -p flags, --bare, structured JSON output used by a real script, GitHub Actions set up for @claude and a weekday report, a table of cron lines, /loop, and five daily recipes.',
    'keywords': ['automation', 'plugin', 'plugin.json', 'claude -p', 'headless', '--json-schema', 'structured_output', 'GitHub Actions', 'claude-code-action', 'cron', 'schedule', '/loop', 'recipes'],
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
