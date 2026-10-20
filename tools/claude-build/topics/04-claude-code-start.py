# Chapter 4: Claude Code first steps. Install, first session, the agent loop, permission modes, plan mode, checkpoints, sessions, the .claude folder.
from ckit import part, run, test, show, cli, prompt, say, quiz, calc, ex, panel, pkg

MODULE = ('🛠️', 'Claude Code and its files', 'claude-code-files', 'Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.')

NODE_TEST_TIMES = [(r'duration_ms [\d.]+', 'duration_ms 0.5'), (r'\(\d+(\.\d+)?ms\)', '(0.5ms)')]

CODES = {
    'install': cli('''
# macOS, Linux or WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex

# or with a package manager
brew install --cask claude-code          # macOS
winget install Anthropic.ClaudeCode      # Windows

# check it worked
claude --version
''', 'Install Claude Code', result='The installer puts the claude command on your PATH. claude --version prints the installed version number.'),
    'first': cli('''
cd ~/projects/my-shop        # go to your project folder
claude                       # start a session here. The first time, it asks you to log in.
''', 'Start your first session', result='Claude Code opens in the terminal, shows the folder it is working in, and waits for your request. It asks before editing files or running commands.'),
    'first-asks': prompt('''
what does this project do? give me a 5 line summary
where is the code that calculates the delivery charge?
add a free delivery rule for orders above Rs 499, then run the tests
what files have I changed?
commit my changes with a descriptive message
''', 'First requests to try, one at a time', result='Claude reads files to answer the first two, edits the delivery code for the third and runs the tests, then uses git for the last two.'),
    'loop': run('''
// What Claude Code does with one request: gather context, act, verify, repeat.
// The "model" here is a stand-in that follows a fixed plan, so the loop can run without an API key.
const plan = [
  { tool: "Grep",  input: "deliveryCharge",       note: "find where delivery is calculated" },
  { tool: "Read",  input: "src/delivery.js",      note: "read the function" },
  { tool: "Edit",  input: "src/delivery.js",      note: "add the free delivery rule" },
  { tool: "Bash",  input: "npm test",             note: "verify with the tests" },
  { tool: null,    input: "Done. Orders above Rs 499 now ship free. 2 tests pass." },
];

for (let turn = 1; ; turn++) {
  const step = plan[turn - 1];
  if (!step.tool) { console.log(`turn ${turn}: final answer -> ${step.input}`); break; }
  console.log(`turn ${turn}: ${step.tool.padEnd(5)} ${step.input.padEnd(22)} (${step.note})`);
}
''', 'The agent loop, step by step'),
    'verify': test({
        'package.json': pkg('my-shop', 'module', {'test': 'node --test --test-reporter=spec'}),
        'src/delivery.js': '''
export function deliveryCharge(orderTotal) {
  if (orderTotal >= 499) return 0;      // free delivery rule
  return 40;
}
''',
        'test/delivery.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { deliveryCharge } from "../src/delivery.js";

test("small orders pay Rs 40", () => assert.equal(deliveryCharge(200), 40));
test("Rs 499 and above ship free", () => {
  assert.equal(deliveryCharge(499), 0);
  assert.equal(deliveryCharge(1200), 0);
});
''',
    }, 'npm test --silent', 'Give Claude a way to check its own work', replace=NODE_TEST_TIMES, shown_cmd='npm test'),
    'plan': cli('''
claude --permission-mode plan        # start a session in plan mode
# or press Shift+Tab inside a session until the status bar shows "plan mode on"
''', 'Plan mode', result='Claude reads files and runs read only commands, then writes a plan. It does not edit your source files until you approve. Ctrl+G opens the plan in your editor.'),
    'epcc': prompt('''
1. (plan mode) read src/checkout and explain how coupons are applied today
2. (plan mode) I want coupons to expire. What files change? Write a plan.
3. (normal mode) implement the plan. Add tests for an expired coupon and run them.
4. commit with a message that explains why, and open a pull request
''', 'Explore, plan, code, commit', result='Each step builds on the last. Mistakes are caught in the plan, where they are cheap to fix, instead of in the code.'),
    'sessions': cli('''
claude --continue        # carry on with the most recent conversation in this folder
claude --resume          # pick an older conversation from a list (or /resume inside a session)
claude -p "summarise the last 5 commits"     # one question, print the answer, exit
''', 'Come back to earlier work', result='--continue reopens the latest session, --resume shows a picker. -p runs once without the interactive screen, which is how scripts use Claude Code (chapter 11).'),
}

PARTS = [
    part('what', '💻', 'What Claude Code is', '''
<p><b>Claude Code</b> is Claude working as an <b>agent</b> inside a folder on your computer. It can read your files, search them, edit them, run commands such as tests, and use git. You describe the goal in plain words. It works out the steps and asks before doing anything risky.</p>
<p>It runs in the terminal, in VS Code and JetBrains, in the Claude desktop app and on the web at claude.ai/code. All of them read the same files you will learn about: <code>CLAUDE.md</code>, <code>.claude/</code> and <code>.mcp.json</code>.</p>
<div class="tip">It is not only for programmers. People use it to tidy folders of documents, turn CSV files into reports, rename hundreds of photos and write scripts they could not write themselves.</div>
''', easy=True, kw=['Claude Code', 'agent', 'terminal', 'VS Code', 'JetBrains', 'desktop app']),
    part('install', '📥', 'Install and start, step by step', '''
<ol class="steps"><li>Open a terminal. On Windows use PowerShell.</li>
<li>Run the install command for your system.</li>
<li>Close and reopen the terminal, then check with <code>claude --version</code>.</li>
<li>Go to a project folder with <code>cd</code> and type <code>claude</code>.</li>
<li>Log in when asked. A Claude Pro, Max, Team or Enterprise plan works, or a Claude Console account.</li></ol>
[[install]]
[[first]]
[[first-asks]]
''', easy=True, kw=['install', 'curl install.sh', 'winget', 'brew', 'claude --version', 'login']),
    part('loop', '🔄', 'How it works: the agent loop', '''
<p>For each request, Claude repeats a simple loop: <b>gather context</b> (search and read), <b>take action</b> (edit, run a command), <b>check the result</b>, then decide the next step. It stops when the task is done or it needs you.</p>
<div class="viz" data-viz="flow" data-k="loop"></div>
[[loop]]
<p>The single most useful habit: <b>give Claude a way to check its work</b>, such as tests, a sample input with the expected output, or a screenshot to compare. With a check, Claude can fix its own mistakes before you see them.</p>
[[verify]]
''', easy=True, kw=['agent loop', 'tools', 'Read', 'Edit', 'Bash', 'Grep', 'verify', 'tests']),
    part('perms', '🚦', 'Permission modes: how much Claude may do alone', '''
<p>The permission mode decides which actions Claude can take without asking. Press <b>Shift+Tab</b> to switch during a session, or set <code>defaultMode</code> in <code>settings.json</code> (chapter 8). In recent versions, new terminal and VS Code sessions start in <code>auto</code> mode, where a separate safety check reviews actions and blocks only what looks risky.</p>
<div class="tw"><table class="jt"><tr><th>Mode</th><th>What it means</th><th>Good for</th></tr>
<tr><td><code>default</code> (shown as Manual)</td><td>asks the first time each tool is used</td><td>learning, unfamiliar projects</td></tr>
<tr><td><code>acceptEdits</code></td><td>edits files and runs simple file commands without asking</td><td>trusted work where you review the diff later</td></tr>
<tr><td><code>plan</code></td><td>reads and explores only, no edits to your source</td><td>thinking a change through first</td></tr>
<tr><td><code>auto</code></td><td>no routine prompts, a safety check reviews risky actions</td><td>long tasks you supervise loosely</td></tr>
<tr><td><code>dontAsk</code></td><td>refuses anything that would need a prompt</td><td>locked down scripts</td></tr>
<tr><td><code>bypassPermissions</code></td><td>skips prompts</td><td>only inside a throwaway container</td></tr>
</table></div>
<div class="warn">When Claude asks, read the command. "Yes, and don't ask again" saves a rule to <code>.claude/settings.local.json</code>, so think before choosing it for commands like <code>git push</code>.</div>
''', easy=True, files=['.claude/settings.json', '.claude/settings.local.json'], kw=['permission modes', 'Shift+Tab', 'acceptEdits', 'plan mode', 'auto mode', 'bypassPermissions', 'defaultMode']),
    part('plan', '🗺️', 'Explore, plan, code, commit', '''
<p>Anthropic's recommended workflow for anything bigger than a one line fix has four steps. The first two happen in <b>plan mode</b>, so nothing changes until you agree.</p>
[[plan]]
[[epcc]]
<div class="scenario"><b>🏫 Real scenario: a school website</b>A volunteer wants a "notice board" page. In plan mode Claude finds that pages are built from Markdown files and proposes three changes. The volunteer edits the plan to drop a database they do not need, then approves. The result is smaller and fits the site.</div>
''', kw=['plan mode', 'explore plan code commit', 'Ctrl+G', 'workflow']),
    part('control', '⏪', 'Stop, undo and come back later', '''
<ul><li><b>Esc</b> stops Claude mid action. Your conversation stays, so you can redirect it.</li>
<li><b>Esc Esc</b> or <code>/rewind</code> opens the rewind menu. Claude snapshots files before each change, so you can restore the code, the conversation, or both.</li>
<li><code>/clear</code> starts fresh in the same window.</li></ul>
[[sessions]]
<div class="warn">Checkpoints cover edits Claude made with its file tools. They do not undo things outside your folder, such as a database change or a message sent by a command. Use git as well.</div>
''', easy=True, kw=['Esc', '/rewind', 'checkpoints', '--continue', '--resume', 'claude -p']),
    part('commands', '⌨️', 'The commands you will use most', '''
<p>Type <code>/</code> in a session to see every command and skill. These are the ones this subject uses.</p>
<div class="tw"><table class="jt"><tr><th>Command</th><th>What it does</th><th>Chapter</th></tr>
<tr><td><code>/init</code></td><td>writes a starter <code>CLAUDE.md</code> for the project</td><td>5</td></tr>
<tr><td><code>/memory</code></td><td>opens <code>CLAUDE.md</code> files and auto memory</td><td>5</td></tr>
<tr><td><code>/skills</code></td><td>lists the skills Claude can use</td><td>7</td></tr>
<tr><td><code>/permissions</code>, <code>/hooks</code></td><td>view and edit rules and hooks</td><td>8</td></tr>
<tr><td><code>/agents</code></td><td>reminds you how to create and manage subagents</td><td>9</td></tr>
<tr><td><code>/mcp</code></td><td>manage MCP server connections</td><td>10</td></tr>
<tr><td><code>/plugin</code></td><td>browse and install plugins</td><td>11</td></tr>
<tr><td><code>/model</code>, <code>/context</code>, <code>/usage</code></td><td>switch model, see context use, see cost and limits</td><td>1, 3</td></tr>
<tr><td><code>/doctor</code></td><td>checks your installation and setup</td><td></td></tr>
</table></div>
<p>Two more shortcuts: type <code>@</code> and a file name to point Claude at a file, and press the up arrow for your earlier requests.</p>
''', easy=True, kw=['slash commands', '/init', '/memory', '/skills', '/hooks', '/mcp', '/plugin', '/doctor', '@ mention']),
    part('folder', '📁', 'The .claude folder: where everything lives', '''
<p>Claude Code reads settings and instructions from two places: your <b>project</b> (shared with your team through git) and your <b>home folder</b> (just for you, in every project). The rest of this module fills in each file.</p>
<pre class="tree"><b>my-shop/</b>                        <i>your project</i>
├── CLAUDE.md                   <i>project instructions, loaded every session (ch 5)</i>
├── CLAUDE.local.md             <i>your private notes for this project, add to .gitignore</i>
├── .mcp.json                   <i>MCP servers the team shares (ch 10)</i>
└── <b>.claude/</b>
    ├── settings.json           <i>permissions, hooks, env for the team (ch 8)</i>
    ├── settings.local.json     <i>your personal overrides, not committed</i>
    ├── rules/                  <i>topic rules, some only for certain paths (ch 6)</i>
    ├── skills/&lt;name&gt;/SKILL.md   <i>repeatable tasks (ch 7)</i>
    ├── agents/&lt;name&gt;.md        <i>subagents (ch 9)</i>
    ├── output-styles/          <i>custom response styles (ch 9)</i>
    └── hooks/                  <i>scripts your hooks run (ch 8)</i>

<b>~/.claude/</b>                       <i>your home folder, applies to every project</i>
├── CLAUDE.md                   <i>your personal preferences</i>
├── settings.json               <i>your personal settings</i>
├── rules/  skills/  agents/  output-styles/
└── projects/&lt;project&gt;/memory/MEMORY.md   <i>auto memory Claude writes</i>

<b>~/.claude.json</b>                   <i>app state and your personal MCP servers</i></pre>
<div class="cl-name">You may hear about files like "rules.md", "agents.md" or "skills.md". Claude Code has no single file with those names. The real places are the folders <code>.claude/rules/</code>, <code>.claude/agents/</code> and <code>.claude/skills/&lt;name&gt;/SKILL.md</code>. One exception: Claude Code can read an <code>AGENTS.md</code> file, used by other coding tools, when the folder has no <code>CLAUDE.md</code>. Chapter 5 covers it.</div>
''', easy=True, files=['CLAUDE.md', 'CLAUDE.local.md', '.mcp.json', '.claude/', '~/.claude/', '~/.claude.json'], kw=['.claude folder', 'project settings', 'home folder', 'file map', 'rules.md', 'agents.md']),
]

DG = {
    'loop': {'t': 'One request, many small steps', 'w': 900, 'h': 260,
             'n': [['req', 20, 100, 140, 56, 'your request', {'c': 5, 'sh': 'doc'}],
                   ['g', 230, 20, 180, 56, 'gather context', {'c': 2, 'sub': 'Grep, Glob, Read', 'i': 'Search and read only the files that matter.'}],
                   ['a', 470, 100, 180, 56, 'take action', {'c': 0, 'sub': 'Edit, Write, Bash', 'i': 'Change files or run commands, asking first when the mode requires it.'}],
                   ['v', 230, 180, 180, 56, 'check the result', {'c': 4, 'sub': 'tests, output', 'i': 'Run tests or compare output, then decide the next step.'}],
                   ['done', 720, 100, 160, 56, 'answer', {'c': 1, 'sh': 'pill'}]],
             'e': [['req', 'g'], ['g', 'a'], ['a', 'v'], ['v', 'g', {'t': 'not done yet'}], ['a', 'done', {'t': 'done'}]],
             'st': [[['req', 'g', 'req>g'], 'Claude starts by finding the relevant code or files.'],
                    [['a', 'g>a'], 'It makes a change or runs a command.'],
                    [['v', 'a>v', 'v>g'], 'It checks the result and loops if something is still wrong.'],
                    [['done', 'a>done'], 'When the check passes, it reports back.']]},
}

INFO = {'title': 'Claude Code in four panels', 'panels': [
    panel([['e', '📥'], ['t', 'curl ... | bash', {'b': 1}]], 'Install', 'One command, then claude.', 'Works in the terminal, IDEs, desktop and web.'),
    panel([['e', '🔄'], ['t', 'gather, act, check', {'b': 1}]], 'The loop', 'Small steps until done.', 'Tests let it check itself.'),
    panel([['e', '🚦'], ['t', 'Shift+Tab', {'b': 1}]], 'Permission modes', 'You decide how much it does alone.', 'Plan mode first for big changes.'),
    panel([['e', '⏪'], ['t', 'Esc Esc', {'b': 1}]], 'Undo', 'Rewind code and chat.', 'Use git for everything else.')],
    'remember': 'Explore, plan, code, commit. And always give Claude a way to check its work.'}

REAL = [
    ['🧾', 'An accountant', 'Points Claude Code at a folder of 300 bank CSV files and asks for one monthly summary sheet. Claude writes and runs a small script, then shows the totals.'],
    ['📸', 'A photographer', 'Asks Claude Code to rename 1,200 photos by date and place from their metadata. Plan mode shows the new names first.'],
    ['🧑‍💻', 'A junior developer', 'Uses plan mode to understand an unfamiliar codebase on day one, then fixes a first bug with tests.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter installs Claude Code and teaches the agent loop, permission modes, plan mode, undo, sessions and the dot claude folder.',
        'यह अध्याय Claude Code install करना, agent loop, permission modes, plan mode, undo और .claude folder सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ Claude Code install, agent loop, permission modes, plan mode, undo ಮತ್ತು .claude folder ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ Claude Code install, agent loop, permission modes, plan mode, undo ଓ .claude folder ଶିଖାଏ।',
        'يثبّت هذا الفصل Claude Code ويشرح حلقة الوكيل وأوضاع الأذونات ووضع التخطيط والتراجع ومجلد .claude.',
        'Dieses Kapitel installiert Claude Code und erklärt die Agentenschleife, Berechtigungsmodi, Planmodus, Rückgängig und den .claude-Ordner.'),
    say('what', 'What it is', 'Claude Code is Claude working as an agent in a folder. It reads, edits and runs things, and asks before risky steps.',
        'Claude Code एक folder में agent की तरह काम करता है। पढ़ता, बदलता और चलाता है, जोखिम से पहले पूछता है।',
        'Claude Code folder ನಲ್ಲಿ agent ಆಗಿ ಕೆಲಸ ಮಾಡುತ್ತದೆ. ಓದುತ್ತದೆ, ಬದಲಿಸುತ್ತದೆ, ಓಡಿಸುತ್ತದೆ.',
        'Claude Code folder ରେ agent ଭାବେ କାମ କରେ। ପଢେ, ବଦଳାଏ ଓ ଚଲାଏ।',
        'Claude Code هو Claude يعمل كوكيل داخل مجلد. يقرأ ويعدّل ويشغّل ويسأل قبل الخطوات الخطرة.',
        'Claude Code ist Claude als Agent in einem Ordner. Es liest, ändert und führt aus und fragt vor riskanten Schritten.'),
    say('install', 'Install', 'Run the install command for your system, check with claude dash dash version, then type claude inside a project folder and log in.',
        'अपने system का install command चलाएं, claude --version से जांचें, फिर folder में claude लिखें।',
        'ನಿಮ್ಮ system ನ install command ಓಡಿಸಿ, claude --version ಪರಿಶೀಲಿಸಿ, folder ನಲ್ಲಿ claude ಟೈಪ್ ಮಾಡಿ.',
        'ନିଜ system ର install command ଚଲାନ୍ତୁ, claude --version ଯାଞ୍ଚ କରନ୍ତୁ, folder ରେ claude ଟାଇପ୍ କରନ୍ତୁ।',
        'شغّل أمر التثبيت لنظامك وتحقق بـ claude --version ثم اكتب claude داخل مجلد المشروع.',
        'Führe den Installationsbefehl aus, prüfe mit claude --version und tippe claude im Projektordner.'),
    say('loop', 'The loop', 'Claude gathers context, acts, checks the result and repeats. Tests or expected output let it fix its own mistakes.',
        'Claude context इकट्ठा करता है, काम करता है, नतीजा जांचता है और दोहराता है।',
        'Claude context ಸಂಗ್ರಹಿಸಿ, ಕೆಲಸ ಮಾಡಿ, ಫಲಿತಾಂಶ ಪರಿಶೀಲಿಸಿ ಪುನರಾವರ್ತಿಸುತ್ತದೆ.',
        'Claude context ସଂଗ୍ରହ କରେ, କାମ କରେ, ଫଳ ଯାଞ୍ଚ କରେ ଓ ପୁନରାବୃତ୍ତି କରେ।',
        'يجمع Claude السياق ثم يعمل ثم يتحقق من النتيجة ويكرر.',
        'Claude sammelt Kontext, handelt, prüft das Ergebnis und wiederholt.'),
    say('perms', 'Permission modes', 'Shift Tab switches modes. Default asks first, accept edits edits freely, plan only explores, auto uses a safety check.',
        'Shift+Tab से mode बदलें। Default पहले पूछता है, plan सिर्फ देखता है।',
        'Shift+Tab ನಿಂದ mode ಬದಲಿಸಿ. Default ಮೊದಲು ಕೇಳುತ್ತದೆ, plan ಕೇವಲ ನೋಡುತ್ತದೆ.',
        'Shift+Tab ରେ mode ବଦଳାନ୍ତୁ। Default ପ୍ରଥମେ ପଚାରେ, plan କେବଳ ଦେଖେ।',
        'Shift+Tab يبدّل الأوضاع. الافتراضي يسأل أولًا ووضع التخطيط يستكشف فقط.',
        'Shift+Tab wechselt den Modus. Standard fragt zuerst, Plan erkundet nur.'),
    say('plan', 'Workflow', 'Explore and plan in plan mode, then code and commit. Mistakes are cheap to fix in the plan.',
        'Plan mode में explore और plan करें, फिर code और commit।',
        'Plan mode ನಲ್ಲಿ explore ಮತ್ತು plan, ನಂತರ code ಮತ್ತು commit.',
        'Plan mode ରେ explore ଓ plan, ତାପରେ code ଓ commit.',
        'استكشف وخطط في وضع التخطيط ثم اكتب الشيفرة وثبّتها.',
        'Im Planmodus erkunden und planen, dann programmieren und committen.'),
    say('control', 'Undo', 'Escape stops Claude. Escape twice or slash rewind restores code and conversation. Continue and resume bring back old sessions.',
        'Esc रोकता है। दो बार Esc या /rewind code और बातचीत वापस लाता है।',
        'Esc ನಿಲ್ಲಿಸುತ್ತದೆ. ಎರಡು ಬಾರಿ Esc ಅಥವಾ /rewind ಹಿಂದಿನ ಸ್ಥಿತಿಗೆ ತರುತ್ತದೆ.',
        'Esc ବନ୍ଦ କରେ। ଦୁଇ ଥର Esc ବା /rewind ପୂର୍ବ ଅବସ୍ଥା ଫେରାଏ।',
        'Esc يوقف Claude. ضغطتان أو /rewind تعيد الشيفرة والمحادثة.',
        'Esc stoppt Claude. Zweimal Esc oder /rewind stellt Code und Gespräch wieder her.'),
    say('commands', 'Commands', 'Type slash to see every command. Init, memory, skills, hooks, agents, mcp and plugin are the ones this subject uses.',
        '/ लिखकर सारे commands देखें। /init, /memory, /skills, /hooks, /mcp मुख्य हैं।',
        '/ ಟೈಪ್ ಮಾಡಿ ಎಲ್ಲಾ commands ನೋಡಿ. /init, /memory, /skills, /hooks, /mcp ಮುಖ್ಯ.',
        '/ ଟାଇପ୍ କରି ସବୁ commands ଦେଖନ୍ତୁ। /init, /memory, /skills, /hooks, /mcp ମୁଖ୍ୟ।',
        'اكتب / لرؤية كل الأوامر. أهمها /init و/memory و/skills و/hooks و/mcp.',
        'Tippe / für alle Befehle. Wichtig sind /init, /memory, /skills, /hooks und /mcp.'),
    say('folder', 'The folder', 'Project files live in CLAUDE.md and the dot claude folder. Personal ones live in the home dot claude folder. There is no single rules.md or skills.md file.',
        'Project files CLAUDE.md और .claude folder में, personal files home के .claude में। कोई अकेली rules.md file नहीं है।',
        'Project files CLAUDE.md ಮತ್ತು .claude ನಲ್ಲಿ, personal files home .claude ನಲ್ಲಿ. ಒಂಟಿ rules.md ಇಲ್ಲ.',
        'Project files CLAUDE.md ଓ .claude ରେ, personal files home .claude ରେ। ଏକା rules.md ନାହିଁ।',
        'ملفات المشروع في CLAUDE.md ومجلد .claude والملفات الشخصية في .claude بالمجلد الرئيسي. لا يوجد ملف rules.md واحد.',
        'Projektdateien liegen in CLAUDE.md und .claude, persönliche in ~/.claude. Eine einzelne rules.md gibt es nicht.'),
    say('practice', 'Practice', 'Practise choosing permission modes, reading the agent loop and finding where each file lives.',
        'Permission mode चुनने और हर file की जगह पहचानने का अभ्यास करें।',
        'Permission mode ಆಯ್ಕೆ ಮತ್ತು file ಸ್ಥಳ ಗುರುತಿಸುವ ಅಭ್ಯಾಸ.',
        'Permission mode ବାଛିବା ଓ file ସ୍ଥାନ ଚିହ୍ନିବାର ଅଭ୍ୟାସ।',
        'تدرّب على اختيار وضع الأذونات ومعرفة مكان كل ملف.',
        'Übe Berechtigungsmodi zu wählen und den Ort jeder Datei zu finden.'),
]

QUIZ = [
    quiz('e', 'Which command checks that Claude Code is installed?', ['claude --version', 'claude install', 'npm claude', 'claude.ai --check'], 0, 'Prints a number.', 'It prints the installed version.'),
    quiz('e', 'Which key cycles permission modes?', ['Shift+Tab', 'Ctrl+C', 'F5', 'Alt+P'], 0, 'Shift and another key.', 'Shift+Tab switches modes during a session.'),
    quiz('e', 'You want Claude to only look and suggest, not change files. Which mode?', ['plan', 'acceptEdits', 'bypassPermissions', 'auto'], 0, 'Think first.', 'Plan mode explores and writes a plan without editing your source.'),
    quiz('m', 'What is the most useful thing to give Claude for a coding task?', ['A way to check its work, like tests', 'A longer chat', 'A bigger screen', 'More emoji'], 0, 'Verification.', 'With a check, Claude can find and fix its own mistakes.'),
    quiz('m', 'How do you undo the last few edits Claude made?', ['Esc Esc or /rewind', '/clear', 'Close the terminal', '/init'], 0, 'Checkpoints.', 'The rewind menu restores code, conversation or both.'),
    quiz('m', 'Where does "Yes, and don\'t ask again" save its rule?', ['.claude/settings.local.json', 'CLAUDE.md', '.mcp.json', '~/.claude.json'], 0, 'Your personal project settings.', 'It is a local file that is not meant to be committed.'),
    quiz('h', 'Which file do teammates share to configure permissions and hooks?', ['.claude/settings.json', '.claude/settings.local.json', 'CLAUDE.local.md', '~/.claude/settings.json'], 0, 'Committed to git.', 'settings.json in the project .claude folder is shared.'),
    quiz('h', 'Does Claude Code use a file called rules.md?', ['No, it uses the .claude/rules/ folder', 'Yes, at the project root', 'Yes, in ~/.claude', 'Only on Windows'], 0, 'Folder, not file.', 'Rules are one topic per Markdown file inside .claude/rules/.'),
    quiz('x', 'What can checkpoints not undo?', ['A database change made by a command', 'An edit to a source file', 'A new file Claude wrote', 'The conversation'], 0, 'Outside the folder.', 'They restore files Claude changed with its file tools, not remote effects.'),
    quiz('x', 'Which order does Anthropic recommend for bigger changes?', ['Explore, plan, code, commit', 'Code, commit, plan', 'Commit, explore, code', 'Plan, commit, code'], 0, 'Understand first.', 'Exploring and planning first catches mistakes when they are cheap.'),
]

CALC = [
    calc('e', 'The loop example used how many tool steps before the final answer?', '4', 'Count the tools.', ['Grep, Read, Edit, Bash.']),
    calc('e', 'deliveryCharge(499) returns what?', '0', 'Check the rule.', ['499 is at least 499, so delivery is free.']),
    calc('m', 'Three orders of Rs 200, 450 and 600. Total delivery charges in rupees?', '80', 'Below 499 pays 40.', ['200 and 450 pay 40 each.', '<span class="eq">40 + 40 + 0 = 80</span>']),
    calc('m', 'Renaming 1,200 photos takes you 20 seconds each by hand. How many hours is that?', '6.67', 'Seconds to hours.', ['<span class="eq">1,200 × 20 = 24,000 s</span>', '<span class="eq">24,000 ÷ 3,600 ≈ 6.67 h</span>'], alt=['6.7', '6.666', '6.67 h']),
    calc('h', 'How many permission modes are in the table?', '6', 'Count the rows.', ['default, acceptEdits, plan, auto, dontAsk, bypassPermissions.']),
    calc('x', 'A plan catches a mistake that would take 3 hours to fix in code and 10 minutes in the plan. How many minutes are saved?', '170', 'Hours to minutes.', ['<span class="eq">3 × 60 = 180</span>', '<span class="eq">180 − 10 = 170</span>']),
]

EX = [
    ex('pick-mode', 'e', 'Pick a permission mode', '<p>Write <code>pickMode(task)</code>. Return <code>"plan"</code> when <code>task.explainOnly</code> is true, <code>"acceptEdits"</code> when <code>task.trusted</code> is true, otherwise <code>"default"</code>.</p>',
       'function pickMode(task) {\n  \n}\n',
       [('pickMode({ explainOnly: true })', 'plan'), ('pickMode({ trusted: true })', 'acceptEdits'), ('pickMode({})', 'default')],
       'function pickMode(task) {\n  if (task.explainOnly) return "plan";\n  if (task.trusted) return "acceptEdits";\n  return "default";\n}',
       hint='Check the safest case first.', why='Choosing the mode on purpose is the first safety habit with Claude Code.'),
    ex('where', 'm', 'Where does it live?', '<p>Write <code>whereIs(thing)</code> for these: <code>"team instructions"</code> gives <code>"CLAUDE.md"</code>, <code>"team permissions"</code> gives <code>".claude/settings.json"</code>, <code>"my permissions"</code> gives <code>".claude/settings.local.json"</code>, <code>"team mcp"</code> gives <code>".mcp.json"</code>. Anything else gives <code>"unknown"</code>.</p>',
       'function whereIs(thing) {\n  \n}\n',
       [('whereIs("team instructions")', 'CLAUDE.md'), ('whereIs("my permissions")', '.claude/settings.local.json'), ('whereIs("team mcp")', '.mcp.json'), ('whereIs("rules.md")', 'unknown')],
       'function whereIs(thing) {\n  const map = {\n    "team instructions": "CLAUDE.md",\n    "team permissions": ".claude/settings.json",\n    "my permissions": ".claude/settings.local.json",\n    "team mcp": ".mcp.json",\n  };\n  return map[thing] ?? "unknown";\n}',
       hint='An object as a lookup table, and <code>??</code> for the default.', why='Knowing which file is shared and which is personal stops private settings leaking into the team repo.'),
    ex('tiny-loop', 'h', 'Run a tiny agent loop', '<p>Write <code>runLoop(steps)</code>. Each step is <code>{ tool, ok }</code>. Go through the steps in order and collect the tool names. Stop after the first step whose <code>ok</code> is false and return <code>{ used, stopped: true }</code>. If every step is ok, return <code>{ used, stopped: false }</code>.</p>',
       'function runLoop(steps) {\n  \n}\n',
       [('runLoop([{tool:"Read",ok:true},{tool:"Bash",ok:false},{tool:"Edit",ok:true}])', {'used': ['Read', 'Bash'], 'stopped': True}),
        ('runLoop([{tool:"Read",ok:true}])', {'used': ['Read'], 'stopped': False})],
       'function runLoop(steps) {\n  const used = [];\n  for (const s of steps) {\n    used.push(s.tool);\n    if (!s.ok) return { used, stopped: true };\n  }\n  return { used, stopped: false };\n}',
       hint='A <code>for...of</code> loop with an early <code>return</code>.', why='Agents stop and ask when a check fails, instead of piling more changes on a broken state.'),
]

T = {
    'slug': 'claude-code-start', 'title': 'Claude Code: First Steps', 'short': 'Claude Code first steps', 'emoji': '💻', 'module': MODULE, 'minutes': 15,
    'lead': 'Install Claude Code, run your first session, see how the agent loop works, choose permission modes, follow the explore, plan, code, commit workflow, undo safely, and learn where every Claude Code file lives.',
    'plain': 'Claude Code is Claude that can open, change and test files in a folder on your computer, and it asks you before doing anything risky.',
    'desc': 'Claude Code installation, first session, the agent loop, verification with tests, permission modes, plan mode, checkpoints and /rewind, sessions, slash commands and the .claude folder.',
    'summary': 'What Claude Code is, installing it on macOS, Linux and Windows, first requests, the gather, act and verify loop with a real test run, the six permission modes, plan mode and the explore, plan, code, commit workflow, Esc, /rewind and resuming sessions, the most used slash commands, and a full map of the .claude folder and home folder, including why there is no single rules.md file.',
    'keywords': ['Claude Code', 'install', 'permission modes', 'plan mode', 'Shift+Tab', 'agent loop', '/rewind', 'checkpoints', '--continue', '--resume', 'slash commands', '.claude folder', 'settings.local.json'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
