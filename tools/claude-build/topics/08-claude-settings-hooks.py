# Chapter 8: settings.json, permission rules and hooks. Scopes and precedence, allow, ask and deny, ready to copy settings, hook events, real hooks run with real JSON.
from ckit import part, run, show, cli, js_, say, quiz, calc, ex, panel, hook

MODULE = ('🛠️', 'Claude Code and its files', 'claude-code-files', 'Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.')

BLOCK = '''
// PreToolUse hook for Bash: block a few commands that should never run.
// Claude Code sends the tool call as JSON on stdin.
let raw = "";
for await (const chunk of process.stdin) raw += chunk;
const { tool_input } = JSON.parse(raw);
const cmd = tool_input.command ?? "";

const banned = [
  [/\\brm\\s+-rf\\s+(\\/|~|\\*)/, "deleting whole folders is not allowed"],
  [/git\\s+push\\b.*--force/, "force pushing is not allowed, open a pull request instead"],
  [/drop\\s+table/i, "dropping tables is not allowed"],
];

for (const [pattern, reason] of banned) {
  if (pattern.test(cmd)) {
    console.error(`Blocked: ${reason}. Command was: ${cmd}`);   // stderr goes back to Claude
    process.exit(2);                                              // exit 2 = block this tool call
  }
}
process.exit(0);                                                  // exit 0 = no objection
'''

PROTECT = '''
// PreToolUse hook for Edit and Write: refuse to touch secret or generated files.
// It answers with JSON instead of an exit code, so it can give a clear reason.
let raw = "";
for await (const chunk of process.stdin) raw += chunk;
const file = (JSON.parse(raw).tool_input.file_path ?? "").replaceAll("\\\\", "/");

const protectedParts = [".env", "package-lock.json", ".git/", "src/generated/"];
const hit = protectedParts.find(p => file.includes(p));

if (hit) {
  console.log(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: `${file} is protected (${hit}). Ask the user to change it by hand.`,
    },
  }));
}
'''

CONTEXT = '''
// UserPromptSubmit hook: add today's release status to every prompt.
import { readFileSync, existsSync } from "node:fs";

let raw = "";
for await (const chunk of process.stdin) raw += chunk;
const { prompt } = JSON.parse(raw);

const freeze = existsSync("release-freeze.txt") ? readFileSync("release-freeze.txt", "utf8").trim() : "";
if (freeze && /deploy|release|merge/i.test(prompt)) {
  console.log(JSON.stringify({
    hookSpecificOutput: { hookEventName: "UserPromptSubmit", additionalContext: "Release status: " + freeze },
  }));
}
'''

AUDIT = '''
// PostToolUse hook for Edit and Write: keep a simple audit log of every file Claude changed.
import { appendFileSync, readFileSync } from "node:fs";

let raw = "";
for await (const chunk of process.stdin) raw += chunk;
const { tool_name, tool_input, session_id } = JSON.parse(raw);

appendFileSync(".claude/edits.log", `${session_id} ${tool_name} ${tool_input.file_path}\\n`);
console.error("log now has", readFileSync(".claude/edits.log", "utf8").trim().split("\\n").length, "line(s)");
'''


def ev(name, tool=None, **inp):
    d = {'session_id': 'abc123', 'cwd': '/home/asha/shop', 'hook_event_name': name}
    if tool:
        d['tool_name'] = tool
        d['tool_input'] = inp
    else:
        d.update(inp)
    return d


CODES = {
    'team': js_('''
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Bash(git status)",
      "Bash(git diff *)"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "WebFetch(domain:pastebin.com)"
    ]
  },
  "env": {
    "NODE_ENV": "development"
  }
}
''', '.claude/settings.json (shared with the team)'),
    'personal': js_('''
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "claude-opus-5-5",
  "permissions": {
    "defaultMode": "acceptEdits"
  },
  "autoMemoryEnabled": true
}
''', '~/.claude/settings.json (just you, every project)'),
    'local': js_('''
{
  "permissions": {
    "allow": ["Bash(docker compose up *)"]
  },
  "env": {
    "SHOP_API_URL": "http://localhost:4100"
  }
}
''', '.claude/settings.local.json (just you, this project, not committed)'),
    'match': run('''
// A model of how Claude Code checks permission rules for a Bash command:
// deny first, then ask, then allow. The first list with a match decides.
const rules = {
  deny:  ["Bash(rm *)", "Bash(curl *)"],
  ask:   ["Bash(git push *)"],
  allow: ["Bash(npm run *)", "Bash(git *)"],
};

function matches(rule, cmd) {
  const pattern = rule.slice(5, -1);                       // text inside Bash(...)
  const re = new RegExp("^" + pattern.split("*").map(s => s.replace(/[.+?^${}()|[\\]\\\\]/g, "\\\\$&")).join(".*") + "$");
  return re.test(cmd);
}

function decide(cmd) {
  for (const list of ["deny", "ask", "allow"]) {
    if (rules[list].some(r => matches(r, cmd))) return list;
  }
  return "ask (no rule, so the mode decides)";
}

for (const cmd of ["npm run test", "git status", "git push origin main", "rm -rf build", "/bin/rm -rf build", "python manage.py migrate"]) {
  console.log(cmd.padEnd(26), "->", decide(cmd));
}
''', 'deny, then ask, then allow'),
    'block': hook(BLOCK, [ev('PreToolUse', 'Bash', command='npm test'), ev('PreToolUse', 'Bash', command='rm -rf ~'), ev('PreToolUse', 'Bash', command='git push origin main --force')],
                  'Block dangerous commands', name='.claude/hooks/block-dangerous.mjs',
                  settings={'hooks': {'PreToolUse': [{'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': 'node "$CLAUDE_PROJECT_DIR"/.claude/hooks/block-dangerous.mjs'}]}]}}),
    'protect': hook(PROTECT, [ev('PreToolUse', 'Edit', file_path='/home/asha/shop/src/cart.ts'), ev('PreToolUse', 'Write', file_path='/home/asha/shop/.env')],
                    'Protect secret and generated files', name='.claude/hooks/protect-files.mjs',
                    settings={'hooks': {'PreToolUse': [{'matcher': 'Edit|Write', 'hooks': [{'type': 'command', 'command': 'node "$CLAUDE_PROJECT_DIR"/.claude/hooks/protect-files.mjs'}]}]}}),
    'context': hook(CONTEXT, [ev('UserPromptSubmit', prompt='fix the typo on the about page'), ev('UserPromptSubmit', prompt='deploy the new cart to production')],
                    'Add live facts to every prompt', name='.claude/hooks/release-status.mjs',
                    settings={'hooks': {'UserPromptSubmit': [{'hooks': [{'type': 'command', 'command': 'node "$CLAUDE_PROJECT_DIR"/.claude/hooks/release-status.mjs'}]}]}},
                    more={'release-freeze.txt': 'FROZEN until Friday 24 Oct for the Diwali sale. Only hotfixes with a ticket.'}),
    'audit': hook(AUDIT, [ev('PostToolUse', 'Edit', file_path='src/cart.ts'), ev('PostToolUse', 'Write', file_path='tests/cart.test.ts')],
                  'Log every file Claude changes', name='.claude/hooks/audit-log.mjs',
                  settings={'hooks': {'PostToolUse': [{'matcher': 'Edit|Write', 'hooks': [{'type': 'command', 'command': 'node "$CLAUDE_PROJECT_DIR"/.claude/hooks/audit-log.mjs'}]}]}}),
    'notify': js_('''
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \\"Claude Code needs your attention\\" with title \\"Claude Code\\"'"
          }
        ]
      }
    ]
  }
}
''', '~/.claude/settings.json: a desktop alert when Claude is waiting (macOS)'),
    'prettier': js_('''
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }
        ]
      }
    ]
  }
}
''', '.claude/settings.json: format every file Claude edits'),
    'hook-cmds': cli('''
/hooks              # browse every hook that is configured, by event
/permissions        # view and edit allow, ask and deny rules by scope
/status             # check which settings files loaded
chmod +x .claude/hooks/*.sh      # shell script hooks must be executable on macOS and Linux
claude --debug      # see full hook output and errors
''', 'Check your settings and hooks', result='/hooks lists each hook under its event. If a hook does not fire, check the event name, the matcher and that the script runs on its own.'),
}

PARTS = [
    part('files', '⚙️', 'The settings files and which one wins', '''
<p>Settings are plain JSON files. Each one has a different reach. When two files set the same key, the higher one in this list wins. Lists such as permission rules are <b>combined</b> from all files.</p>
<div class="tw"><table class="jt"><tr><th>Priority</th><th>File</th><th>Reaches</th></tr>
<tr><td>1 (highest)</td><td>managed settings from your organisation</td><td>everyone on managed machines, cannot be overridden</td></tr>
<tr><td>2</td><td><code>--settings</code> on the command line</td><td>this one session</td></tr>
<tr><td>3</td><td><code>.claude/settings.local.json</code></td><td>you, in this project (not committed)</td></tr>
<tr><td>4</td><td><code>.claude/settings.json</code></td><td>the whole team, through git</td></tr>
<tr><td>5</td><td><code>~/.claude/settings.json</code></td><td>you, in every project</td></tr>
</table></div>
<div class="viz" data-viz="flow" data-k="stack"></div>
<div class="warn">Settings files are strict JSON. A comment or a trailing comma breaks the file. Add the <code>$schema</code> line to get autocomplete and checks in your editor, and run <code>/status</code> to confirm what loaded.</div>
''', easy=True, files=['~/.claude/settings.json', '.claude/settings.json', '.claude/settings.local.json'], kw=['settings.json', 'settings precedence', 'managed settings', 'settings.local.json', '$schema']),
    part('perms', '🚦', 'Permission rules: allow, ask and deny', '''
<p>A rule names a tool, and optionally what it may touch: <code>Bash(npm run test *)</code>, <code>Read(./.env)</code>, <code>Edit(src/**)</code>, <code>WebFetch(domain:example.com)</code>. A <code>*</code> matches anything.</p>
<ul><li><b>allow</b>: run without asking.</li><li><b>ask</b>: always ask, even in a relaxed mode.</li><li><b>deny</b>: never run.</li></ul>
<p>Rules are checked <b>deny first, then ask, then allow</b>. An allow rule can never make an exception to a deny rule.</p>
[[match]]
<div class="warn">Look at the <code>/bin/rm</code> line. Pattern rules match the command as written, so <code>Bash(rm *)</code> does not catch <code>/bin/rm</code> or <code>bash -c 'rm ...'</code>. Use deny rules for clear cases and a <b>hook</b> for anything that truly must be stopped.</div>
''', easy=True, files=['.claude/settings.json'], kw=['permissions', 'allow', 'ask', 'deny', 'rule syntax', 'Bash()', 'Read()', 'WebFetch domain']),
    part('copy', '📄', 'Ready to copy settings files', '''
[[team]]
[[personal]]
[[local]]
<div class="cl-put"><ul><li><code>.claude/settings.json</code>: safe commands to allow, risky ones to ask about, secrets to deny, team hooks.</li>
<li><code>~/.claude/settings.json</code>: your model, your default mode, your personal hooks such as notifications.</li>
<li><code>.claude/settings.local.json</code>: your local URLs and extra allows. "Yes, and don't ask again" writes here.</li></ul></div>
<p>A safety detail: <code>defaultMode</code> values <code>auto</code> and <code>bypassPermissions</code> are ignored in project files, so a repository cannot switch your safety checks off. Allow rules in a project file apply only after you trust the folder. Deny and ask rules apply straight away.</p>
''', easy=True, files=['.claude/settings.json', '~/.claude/settings.json', '.claude/settings.local.json'], kw=['settings example', 'env', 'model', 'defaultMode', 'workspace trust']),
    part('hooks', '🪝', 'Hooks: code that runs on events', '''
<p>A <b>hook</b> is a command Claude Code runs at a fixed moment, such as just before a tool runs or when Claude is waiting for you. Unlike <code>CLAUDE.md</code>, a hook <b>always</b> runs. It is your tool for rules that must never be broken and for automation that must happen every time.</p>
<div class="viz" data-viz="lanes" data-k="events"></div>
<div class="tw"><table class="jt"><tr><th>Event</th><th>Fires</th><th>Typical use</th></tr>
<tr><td><code>SessionStart</code></td><td>a session begins or resumes</td><td>load fresh facts</td></tr>
<tr><td><code>UserPromptSubmit</code></td><td>you send a prompt</td><td>add context, block secrets in prompts</td></tr>
<tr><td><code>PreToolUse</code></td><td>before a tool runs, can block it</td><td>stop dangerous commands, protect files</td></tr>
<tr><td><code>PostToolUse</code></td><td>after a tool succeeds</td><td>format, lint, log</td></tr>
<tr><td><code>Notification</code></td><td>Claude needs your attention</td><td>desktop alert</td></tr>
<tr><td><code>Stop</code></td><td>Claude finishes its answer</td><td>run checks before it stops</td></tr>
<tr><td><code>PreCompact</code>, <code>SessionEnd</code></td><td>before compaction, at the end</td><td>save notes, clean up</td></tr>
</table></div>
<p>Each hook gets a JSON description of the event on <b>stdin</b>. It replies with an exit code: <b>0</b> means no objection, <b>2</b> means block, and the text on stderr is sent to Claude as the reason. For finer control it can print JSON instead.</p>
''', easy=True, files=['settings.json', '.claude/hooks/'], kw=['hooks', 'events', 'PreToolUse', 'PostToolUse', 'UserPromptSubmit', 'Notification', 'exit code 2', 'stdin JSON']),
    part('block', '⛔', 'Hook 1: block dangerous commands', '''
<ol class="steps"><li>Save the script in <code>.claude/hooks/</code>.</li>
<li>Register it under <code>PreToolUse</code> with the matcher <code>Bash</code> in <code>.claude/settings.json</code>.</li>
<li>Use <code>"$CLAUDE_PROJECT_DIR"</code> in the command so it works from any folder.</li>
<li>Test it by piping a sample event into it, exactly as below.</li></ol>
[[block]]
<p>Claude sees the "Blocked" message and tries a safer way, or asks you.</p>
''', easy=True, files=['.claude/hooks/block-dangerous.mjs', '.claude/settings.json'], kw=['PreToolUse', 'block command', 'exit 2', 'rm -rf', 'force push']),
    part('protect', '🔒', 'Hook 2: protect secret files, with a JSON answer', '''
<p>Instead of an exit code, a <code>PreToolUse</code> hook can print JSON with <code>permissionDecision</code> set to <code>deny</code>, <code>ask</code> or <code>allow</code>, plus a reason Claude will read.</p>
[[protect]]
<div class="tip">A hook that says <code>allow</code> still cannot override a deny rule in settings. Deny always wins.</div>
''', files=['.claude/hooks/protect-files.mjs'], kw=['protect files', 'permissionDecision', 'deny', 'JSON output', '.env']),
    part('context', '📣', 'Hook 3: add live facts to prompts', '''
<p>A <code>UserPromptSubmit</code> hook can add text to Claude's context with <code>additionalContext</code>, nested inside <code>hookSpecificOutput</code>. Here it tells Claude about a release freeze, but only when the prompt is about deploying.</p>
[[context]]
''', files=['.claude/hooks/release-status.mjs'], kw=['UserPromptSubmit', 'additionalContext', 'release freeze', 'inject context']),
    part('after', '🧹', 'Hook 4: after every edit, log, format or notify', '''
[[audit]]
<p>Two more from the official guide, ready to paste:</p>
[[prettier]]
[[notify]]
<p>On Linux, swap the notification command for <code>notify-send 'Claude Code' 'Claude Code needs your attention'</code>. On Windows, use a PowerShell message box command.</p>
''', files=['.claude/hooks/audit-log.mjs', '.claude/settings.json', '~/.claude/settings.json'], kw=['PostToolUse', 'audit log', 'prettier', 'Notification hook', 'osascript']),
    part('check', '🩺', 'Check and debug', '''
[[hook-cmds]]
<ul><li><b>Hook not firing?</b> Event names are case sensitive (<code>PreToolUse</code>, not <code>preToolUse</code>). The matcher must match the tool name.</li>
<li><b>Hook seems ignored?</b> Test the script on its own by piping JSON into it, as on this page.</li>
<li><b>JSON has no effect?</b> Make sure nothing else is printed before it, and that fields like <code>additionalContext</code> sit inside <code>hookSpecificOutput</code>.</li></ul>
<div class="warn">Hooks run with your user's permissions. Read every hook in a repository you clone before you trust the folder.</div>
''', files=['settings.json'], kw=['/hooks', '/permissions', '/status', 'debug hooks', 'claude --debug']),
]

DG = {
    'stack': {'t': 'Which settings file wins', 'w': 900, 'h': 300,
              'n': [['m', 20, 20, 260, 46, 'managed settings', {'c': 3, 'sub': 'organisation', 'i': 'Nothing below can override these keys.'}],
                    ['c', 20, 76, 260, 46, '--settings flag', {'c': 2, 'sub': 'one session'}],
                    ['l', 20, 132, 260, 46, '.claude/settings.local.json', {'c': 5, 'sub': 'you, this project'}],
                    ['p', 20, 188, 260, 46, '.claude/settings.json', {'c': 0, 'sub': 'team'}],
                    ['u', 20, 244, 260, 46, '~/.claude/settings.json', {'c': 4, 'sub': 'you, everywhere'}],
                    ['r', 420, 110, 200, 70, 'final settings', {'c': 1, 'sh': 'pill'}],
                    ['k', 680, 60, 200, 56, 'single keys', {'c': 2, 'sub': 'highest wins', 'i': 'model, defaultMode and so on come from the highest file that sets them.'}],
                    ['ls', 680, 170, 200, 56, 'lists', {'c': 0, 'sub': 'combined', 'i': 'allow, ask and deny rules from every file are merged.'}]],
              'e': [['m', 'r'], ['c', 'r'], ['l', 'r'], ['p', 'r'], ['u', 'r'], ['r', 'k'], ['r', 'ls']],
              'st': [[['u', 'p', 'u>r', 'p>r'], 'Your user file and the team file are read.'],
                     [['l', 'c', 'l>r', 'c>r'], 'Your local file and any command line settings sit above them.'],
                     [['m', 'm>r', 'r'], 'Managed settings sit on top of everything.'],
                     [['k', 'ls', 'r>k', 'r>ls'], 'Single values come from the highest file. Rule lists are joined together.']]},
}

LANES = {
    'events': {'t': 'Hooks along one request', 's': 'Step through a request and see which events fire.', 'code': 'session starts\nyou: "deploy the cart"\nClaude runs: git push --force\nClaude edits src/cart.ts\nClaude finishes',
               'lanes': ['What happens', 'Hook that fires'], 'tone': [2, 3],
               'steps': [{'l': 1, 'v': [['session starts'], ['SessionStart']], 'm': 'A SessionStart hook can load fresh facts.'},
                         {'l': 2, 'v': [['session starts', 'you send a prompt'], ['SessionStart', 'UserPromptSubmit: adds freeze notice']], 'm': 'Your prompt mentions deploy, so the release status is added.'},
                         {'l': 3, 'v': [['session starts', 'you send a prompt', 'Bash: git push --force'], ['SessionStart', 'UserPromptSubmit', 'PreToolUse: exit 2, blocked']], 'm': 'PreToolUse blocks the force push. Claude reads the reason.'},
                         {'l': 4, 'v': [['session starts', 'you send a prompt', 'Bash: blocked', 'Edit src/cart.ts'], ['SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PostToolUse: logged']], 'm': 'After the edit, PostToolUse logs or formats the file.'},
                         {'l': 5, 'v': [['session starts', 'you send a prompt', 'Bash: blocked', 'Edit src/cart.ts', 'answer'], ['SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PostToolUse', 'Stop']], 'm': 'When Claude finishes, a Stop hook can run final checks.'}]},
}

INFO = {'title': 'Settings guide Claude, hooks guard it', 'panels': [
    panel([['e', '⚙️'], ['t', 'managed > local > project > user', {'b': 1, 'size': 11}]], 'Five levels', 'Higher files win for single keys.', 'Rule lists are merged.'),
    panel([['e', '🚦'], ['t', 'deny → ask → allow', {'b': 1}]], 'Permission rules', 'Deny always wins.', 'Patterns match the command as written.'),
    panel([['e', '🪝'], ['t', 'PreToolUse, exit 2', {'b': 1}]], 'Hooks', 'Code that always runs.', 'Exit 2 blocks and tells Claude why.'),
    panel([['e', '📣'], ['t', 'additionalContext', {'b': 1}]], 'Add facts', 'Hooks can inform, not only block.', 'Freeze notices, branch names, dates.')],
    'remember': 'CLAUDE.md asks nicely. Permission rules and hooks make sure.'}

REAL = [
    ['🏥', 'A hospital IT team', 'Denies Read on every folder with patient exports and adds a PreToolUse hook that blocks any command containing their database host.'],
    ['🛍️', 'An online shop', 'Uses a UserPromptSubmit hook during the festival sale freeze, so anyone asking Claude to deploy is reminded of the rules first.'],
    ['🏗️', 'A platform team', 'Formats every edited file with a PostToolUse hook, so reviews never argue about spacing again.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers settings files, permission rules, and hooks that run real code on events, with every hook run for real.',
        'यह अध्याय settings files, permission rules और hooks सिखाता है, हर hook असल में चलाकर।',
        'ಈ ಅಧ್ಯಾಯ settings files, permission rules ಮತ್ತು hooks ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ settings files, permission rules ଓ hooks ଶିଖାଏ।',
        'يغطي هذا الفصل ملفات الإعدادات وقواعد الأذونات والخطافات مع تشغيل كل خطاف فعليًا.',
        'Dieses Kapitel behandelt Einstellungsdateien, Berechtigungsregeln und Hooks, jeder Hook echt ausgeführt.'),
    say('files', 'Settings files', 'Managed settings win, then the command line, local, project and user files. Single keys come from the highest file, rule lists are merged.',
        'Managed settings सबसे ऊपर, फिर command line, local, project और user।',
        'Managed settings ಮೇಲೆ, ನಂತರ command line, local, project, user.',
        'Managed settings ଉପରେ, ତାପରେ command line, local, project, user.',
        'الإعدادات المُدارة أعلى، ثم سطر الأوامر والمحلي والمشروع والمستخدم.',
        'Verwaltete Einstellungen gewinnen, dann Kommandozeile, lokal, Projekt und Benutzer.'),
    say('perms', 'Permission rules', 'Rules are checked deny first, then ask, then allow. Patterns match the command as written, so use hooks for must never rules.',
        'पहले deny, फिर ask, फिर allow। ज़रूरी रोक के लिए hooks।',
        'ಮೊದಲು deny, ನಂತರ ask, ನಂತರ allow. ಕಡ್ಡಾಯಕ್ಕೆ hooks.',
        'ପ୍ରଥମେ deny, ତାପରେ ask, ତାପରେ allow. ବାଧ୍ୟତାମୂଳକ ପାଇଁ hooks.',
        'الرفض أولًا ثم السؤال ثم السماح. استخدم الخطافات لما يجب منعه دائمًا.',
        'Erst verweigern, dann fragen, dann erlauben. Für absolute Verbote Hooks nutzen.'),
    say('copy', 'Settings to copy', 'The team file holds safe allows and secret denies, your user file holds your model and mode, and the local file holds your machine details.',
        'Team file में allow और deny, user file में model, local file में मशीन की जानकारी।',
        'Team file ನಲ್ಲಿ allow ಮತ್ತು deny, user file ನಲ್ಲಿ model, local file ನಲ್ಲಿ ಯಂತ್ರ ವಿವರ.',
        'Team file ରେ allow ଓ deny, user file ରେ model, local file ରେ ଯନ୍ତ୍ର ବିବରଣୀ।',
        'ملف الفريق للسماح والرفض وملفك للنموذج والملف المحلي لتفاصيل جهازك.',
        'Teamdatei für Erlauben und Verbieten, Benutzerdatei für Modell, lokale Datei für deinen Rechner.'),
    say('hooks', 'Hooks', 'A hook is a command that always runs on an event. It reads JSON on standard input and answers with exit code zero, exit code two to block, or JSON.',
        'Hook एक command है जो event पर हमेशा चलता है। Exit 2 रोकता है।',
        'Hook ಎಂದರೆ event ನಲ್ಲಿ ಯಾವಾಗಲೂ ಓಡುವ command. Exit 2 ತಡೆಯುತ್ತದೆ.',
        'Hook ହେଉଛି event ରେ ସବୁବେଳେ ଚାଲୁଥିବା command. Exit 2 ଅଟକାଏ।',
        'الخطاف أمر يعمل دائمًا عند حدث. رمز الخروج 2 يمنع.',
        'Ein Hook ist ein Befehl, der bei einem Ereignis immer läuft. Exit 2 blockiert.'),
    say('block', 'Block commands', 'A PreToolUse hook on Bash blocks force pushes and deleting whole folders, and tells Claude why.',
        'PreToolUse hook force push और folder मिटाने को रोकता है।',
        'PreToolUse hook force push ಮತ್ತು folder ಅಳಿಸುವಿಕೆ ತಡೆಯುತ್ತದೆ.',
        'PreToolUse hook force push ଓ folder ବିଲୋପ ଅଟକାଏ।',
        'خطاف PreToolUse يمنع الدفع القسري وحذف المجلدات.',
        'Ein PreToolUse-Hook blockiert Force-Push und das Löschen ganzer Ordner.'),
    say('protect', 'Protect files', 'A hook can answer with JSON to deny an edit to secret files with a clear reason.',
        'Hook JSON से secret files की edit मना कर सकता है।',
        'Hook JSON ಮೂಲಕ secret files edit ನಿರಾಕರಿಸಬಹುದು.',
        'Hook JSON ଦ୍ୱାରା secret files edit ମନା କରିପାରେ।',
        'يمكن للخطاف أن يرد بـ JSON ليرفض تعديل الملفات السرية.',
        'Ein Hook kann mit JSON Änderungen an geheimen Dateien verweigern.'),
    say('context', 'Add facts', 'A UserPromptSubmit hook adds live facts, like a release freeze, to the prompts that need them.',
        'UserPromptSubmit hook ज़रूरी prompts में ताज़ा जानकारी जोड़ता है।',
        'UserPromptSubmit hook ಅಗತ್ಯ prompts ಗೆ ಹೊಸ ಮಾಹಿತಿ ಸೇರಿಸುತ್ತದೆ.',
        'UserPromptSubmit hook ଦରକାରୀ prompts ରେ ନୂଆ ତଥ୍ୟ ଯୋଡେ।',
        'خطاف UserPromptSubmit يضيف معلومات حية للموجّهات.',
        'Ein UserPromptSubmit-Hook fügt aktuelle Fakten zu passenden Prompts hinzu.'),
    say('after', 'After edits', 'PostToolUse hooks log, format or check every file Claude changes, and Notification hooks alert you when Claude is waiting.',
        'PostToolUse hooks हर बदली file को log या format करते हैं।',
        'PostToolUse hooks ಪ್ರತಿ file log ಅಥವಾ format ಮಾಡುತ್ತವೆ.',
        'PostToolUse hooks ପ୍ରତି file log ବା format କରେ।',
        'خطافات PostToolUse تسجّل أو تنسّق كل ملف يغيره Claude.',
        'PostToolUse-Hooks protokollieren oder formatieren jede geänderte Datei.'),
    say('check', 'Debugging', 'Use slash hooks, slash permissions and slash status to check, and test each hook by piping JSON into it.',
        '/hooks, /permissions और /status से जांचें।',
        '/hooks, /permissions, /status ಬಳಸಿ ಪರಿಶೀಲಿಸಿ.',
        '/hooks, /permissions, /status ରେ ଯାଞ୍ଚ କରନ୍ତୁ।',
        'استخدم /hooks و/permissions و/status للتحقق.',
        'Prüfe mit /hooks, /permissions und /status.'),
    say('practice', 'Practice', 'Practise matching rules, reading hook input and writing a tiny blocking hook.',
        'Rules मिलाने और hook लिखने का अभ्यास।',
        'Rules ಹೊಂದಿಸುವ ಮತ್ತು hook ಬರೆಯುವ ಅಭ್ಯಾಸ.',
        'Rules ମେଳ ଓ hook ଲେଖିବାର ଅଭ୍ୟାସ।',
        'تدرّب على مطابقة القواعد وكتابة خطاف.',
        'Übe Regeln abzugleichen und einen Hook zu schreiben.'),
]

QUIZ = [
    quiz('e', 'Which settings file is shared with your team through git?', ['.claude/settings.json', '.claude/settings.local.json', '~/.claude/settings.json', '~/.claude.json'], 0, 'In the project, not local.', 'The local file is personal and not committed.'),
    quiz('e', 'Which hook event can block a tool before it runs?', ['PreToolUse', 'PostToolUse', 'SessionEnd', 'Notification'], 0, 'Before.', 'PreToolUse runs before the tool and can stop it.'),
    quiz('e', 'What exit code from a hook blocks the action?', ['2', '0', '1', '200'], 0, 'Not zero.', 'Exit 2 blocks, and stderr goes to Claude as the reason.'),
    quiz('m', 'A command matches an allow rule and a deny rule. What happens?', ['It is denied', 'It is allowed', 'Claude picks one', 'The newer rule wins'], 0, 'Order of checking.', 'Deny is checked first and an allow cannot override it.'),
    quiz('m', 'Which rule stops Claude reading your .env file?', ['"deny": ["Read(./.env)"]', '"allow": ["Read(./.env)"]', '"ask": ["Edit(.env)"]', '"env": {".env": false}'], 0, 'Deny a read.', 'Read(./.env) in the deny list blocks reading it.'),
    quiz('m', 'Where must additionalContext go in a UserPromptSubmit hook\'s JSON?', ['Inside hookSpecificOutput', 'At the top level', 'In stderr', 'In the settings file'], 0, 'Nested.', 'At the top level it is silently ignored.'),
    quiz('h', 'Why can Bash(rm *) fail to stop /bin/rm -rf build?', ['Rules match the command as written', 'rm is always allowed', 'Deny rules only work on Windows', 'Hooks override it'], 0, 'Spelling of the command.', 'Use a hook when a rule must hold for every way of writing a command.'),
    quiz('h', 'A project file sets defaultMode to bypassPermissions. What happens?', ['It is ignored, it must be set in user or managed settings', 'Every teammate loses prompts', 'Claude Code refuses to start', 'Only deny rules are skipped'], 0, 'Safety.', 'A repository cannot switch your safety checks off.'),
    quiz('x', 'A PreToolUse hook returns "allow" but a deny rule matches. Result?', ['Denied', 'Allowed', 'Asked', 'The hook crashes'], 0, 'Deny first.', 'Hook decisions never override deny rules.'),
    quiz('x', 'Your hook must see every file Claude changes, even through Bash. What is the safest addition?', ['A Stop hook that scans the working tree each turn', 'A longer CLAUDE.md', 'A PostToolUse hook on Edit only', 'An output style'], 0, 'Bash can write files too.', 'The docs suggest a Stop hook or matching Bash and checking git status.'),
]

CALC = [
    calc('e', 'How many levels are in the settings precedence list?', '5', 'Count them.', ['Managed, command line, local, project, user.']),
    calc('e', 'In the hook run, which exit code did npm test get?', '0', 'Read the output.', ['npm test is not banned, so the hook exits 0.']),
    calc('m', 'In the rule matching run, how many of the 6 commands were denied?', '1', 'Read the output.', ['Only rm -rf build matched a deny rule. /bin/rm was not matched.']),
    calc('m', 'The team file allows 4 commands and your local file allows 1 more. How many allow rules apply?', '5', 'Lists are merged.', ['<span class="eq">4 + 1 = 5</span>']),
    calc('h', 'A hook takes 40 ms and runs on 300 tool calls a day. How many seconds a day does it add?', '12', 'Milliseconds to seconds.', ['<span class="eq">40 × 300 = 12,000 ms</span>', '<span class="eq">12,000 ÷ 1,000 = 12 s</span>']),
    calc('x', 'The audit log ran on 2 events. How many lines does .claude/edits.log hold at the end?', '2', 'One line per event.', ['Each PostToolUse event appends one line.']),
]

EX = [
    ex('banned', 'e', 'Spot a banned command', '<p>Write <code>isBanned(cmd)</code>. Return true when the command contains <code>rm -rf /</code>, <code>--force</code> together with <code>git push</code>, or <code>drop table</code> in any case.</p>',
       'function isBanned(cmd) {\n  \n}\n',
       [('isBanned("git push origin main --force")', True), ('isBanned("DROP TABLE users")', True), ('isBanned("npm test")', False), ('isBanned("git push origin main")', False)],
       'function isBanned(cmd) {\n  const c = cmd.toLowerCase();\n  return c.includes("rm -rf /") || (c.includes("git push") && c.includes("--force")) || c.includes("drop table");\n}',
       hint='Lowercase first, then <code>includes</code>.', why='This is the heart of a PreToolUse hook: look at the command, decide, and say why.'),
    ex('decide', 'm', 'deny, ask, allow', '<p>Write <code>decide(cmd, rules)</code>. <code>rules</code> has lists <code>deny</code>, <code>ask</code>, <code>allow</code> of prefixes. Return the first list name, in that order, that has a prefix the command starts with. Return <code>"none"</code> if no list matches.</p>',
       'function decide(cmd, rules) {\n  \n}\n',
       [('decide("rm -rf x", { deny: ["rm "], ask: [], allow: ["rm "] })', 'deny'), ('decide("git push", { deny: [], ask: ["git push"], allow: ["git "] })', 'ask'), ('decide("npm test", { deny: [], ask: [], allow: ["npm "] })', 'allow'), ('decide("ls", { deny: [], ask: [], allow: [] })', 'none')],
       'function decide(cmd, rules) {\n  for (const list of ["deny", "ask", "allow"]) {\n    if (rules[list].some(p => cmd.startsWith(p))) return list;\n  }\n  return "none";\n}',
       hint='Loop over the three names in order.', why='The order is the whole point: deny can never be overruled by a broader allow.'),
    ex('hook-answer', 'h', 'Build a hook answer', '<p>Write <code>answer(filePath)</code>. If the path contains <code>.env</code>, return the object <code>{ hookSpecificOutput: { hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "protected" } }</code>. Otherwise return <code>null</code>.</p>',
       'function answer(filePath) {\n  \n}\n',
       [('answer("/app/.env")', {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': 'protected'}}), ('answer("/app/src/cart.ts")', None)],
       'function answer(filePath) {\n  if (!filePath.includes(".env")) return null;\n  return { hookSpecificOutput: { hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "protected" } };\n}',
       hint='Return early for the safe case.', why='Getting the nesting exactly right is the most common hook mistake.'),
]

T = {
    'slug': 'claude-settings-hooks', 'title': 'settings.json, Permissions and Hooks', 'short': 'Settings and hooks', 'emoji': '🪝', 'module': MODULE, 'minutes': 18,
    'lead': 'The five settings levels and which one wins, allow, ask and deny rules and how they are matched, ready to copy settings files for the team, for you and for your machine, and four real hooks that block commands, protect files, add live facts and log edits, each run with the JSON Claude Code sends.',
    'plain': 'Settings are the house rules for Claude Code. Hooks are guards at the door: small programs that run every time something happens and can say "stop".',
    'desc': 'Claude Code settings.json and hooks: settings precedence, permission rules, allow ask deny, settings examples, hook events, PreToolUse, PostToolUse, UserPromptSubmit and Notification hooks.',
    'summary': 'Settings files and precedence, permission rules with a run of deny, ask and allow matching, ready to copy team, personal and local settings, hook events and how hooks talk through stdin and exit codes, four hooks run for real (block dangerous commands, protect files with a JSON answer, add a release freeze notice, log every edit), the official format and notification hooks, and debugging with /hooks, /permissions and /status.',
    'keywords': ['settings.json', 'settings.local.json', 'permissions', 'allow', 'deny', 'ask', 'hooks', 'PreToolUse', 'PostToolUse', 'UserPromptSubmit', 'Notification', 'exit code 2', '/hooks', 'defaultMode'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
