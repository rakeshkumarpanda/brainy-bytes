# Chapter 10: MCP. What it is, connecting servers, scopes and .mcp.json, building a server in Python
# step by step, what travels on the wire, using tools, resources and prompts, and Claude Desktop.
from ckit import part, test, show, cli, prompt, js_, say, quiz, calc, panel, shots

MODULE = ('🛠️', 'Claude Code and its files', 'claude-code-files', 'Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.')

SERVER = r'''
# server.py: a small MCP server that saves expenses to a file.
import json
from pathlib import Path
from typing import Annotated

from pydantic import Field
from mcp.server import MCPServer

FILE = Path("expenses.json")
mcp = MCPServer("expenses")


def load():
    return json.loads(FILE.read_text()) if FILE.exists() else []


# Tool 1: save one expense. The docstring tells Claude when to use it.
@mcp.tool()
def add_expense(
    item: Annotated[str, Field(description="What the money was spent on")],
    amount: Annotated[float, Field(gt=0, description="Amount in rupees")],
) -> str:
    """Save one expense with what it was for and the amount in rupees."""
    expenses = load()
    expenses.append({"item": item, "amount": amount})
    FILE.write_text(json.dumps(expenses, indent=2))
    return f"Saved {item} for ₹{amount:g}. Expenses saved: {len(expenses)}."


# Tool 2: add everything up.
@mcp.tool()
def total_spent() -> str:
    """Add up every saved expense and say the total in rupees."""
    total = sum(e["amount"] for e in load())
    return f"Total spent: ₹{total:g}"


# A resource: read only data Claude can pull in with @expenses:expenses://all
@mcp.resource("expenses://all")
def all_expenses() -> str:
    """Every saved expense, one per line."""
    return "\n".join(f"{e['item']}: ₹{e['amount']:g}" for e in load()) or "No expenses yet."


if __name__ == "__main__":
    mcp.run()   # stdio by default. Never print() here, stdout carries the messages.
'''

CLIENT = r'''
# try_it.py: plays the part of Claude Code. It starts the server, lists its tools and calls them.
import asyncio
import sys

from mcp import Client
from mcp.client.stdio import StdioServerParameters


async def main():
    server = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with Client(server) as client:
        tools = await client.list_tools()
        print("Tools the server offers:")
        for t in tools.tools:
            print(" -", t.name + ":", t.description)

        async def call(name, args=None):
            r = await client.call_tool(name, args or {})
            flag = "ERROR " if r.is_error else ""
            print(f"{name}({args or {}}) -> {flag}{r.content[0].text.splitlines()[0]}")

        await call("add_expense", {"item": "auto rickshaw", "amount": 120})
        await call("add_expense", {"item": "team lunch", "amount": 850})
        await call("total_spent")
        await call("add_expense", {"item": "refund", "amount": -50})   # the schema says more than 0, so this is refused

        week = await client.read_resource("expenses://all")
        print("resource expenses://all:")
        print(week.contents[0].text)


asyncio.run(main())
'''

WIRE = '''
CLAUDE CODE -> {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "demo", "version": "1"}}}
SERVER      <- {"capabilities": {"prompts": {...}, "resources": {...}, "tools": {"listChanged": false}}, "protocolVersion": "2025-11-25", "serverInfo": {"name": "expenses"}}

CLAUDE CODE -> {"jsonrpc": "2.0", "method": "notifications/initialized"}

CLAUDE CODE -> {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
SERVER      <- {"tools": [{"name": "add_expense", "description": "Save one expense with what it was for and the amount in rupees.",
                "inputSchema": {"type": "object", "required": ["item", "amount"], "properties": {
                  "item": {"type": "string", "description": "What the money was spent on"},
                  "amount": {"type": "number", "exclusiveMinimum": 0, "description": "Amount in rupees"}}}},
               {"name": "total_spent", ...}]}

CLAUDE CODE -> {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "add_expense", "arguments": {"item": "chai", "amount": 20}}}
SERVER      <- {"content": [{"type": "text", "text": "Saved chai for ₹20. Expenses saved: 1."}], "isError": false}
'''

CODES = {
    'first': cli('''
# 1. Add the free Claude Code docs server (no login needed)
claude mcp add --transport http claude-code-docs https://code.claude.com/docs/mcp

# 2. Check it connected
claude mcp list

# 3. Use it
claude
> Use the claude-code-docs server to find how hooks block a command
''', 'Your first MCP server in three steps', result='claude mcp list shows the server with a connected tick. In the session Claude calls the server\'s search tool and answers from the official pages.'),
    'add': cli('''
# A hosted (remote) server: use http
claude mcp add --transport http notion https://mcp.notion.com/mcp

# A remote server that needs a key in a header
claude mcp add --transport http secure-api https://api.example.com/mcp \\
  --header "Authorization: Bearer your-token"

# A local program (stdio). Everything after -- is the command that starts it
claude mcp add --transport stdio --env AIRTABLE_API_KEY=YOUR_KEY airtable \\
  -- npx -y airtable-mcp-server

# Manage
claude mcp list            # all servers
claude mcp get notion      # one server
claude mcp remove notion   # remove it
/mcp                       # inside a session: status, sign in, tools
''', 'Adding and managing servers', result='http is for hosted services and is the recommended remote transport. stdio starts a program on your computer. SSE still works but is deprecated.'),
    'mcpjson': js_('''
{
  "mcpServers": {
    "claude-code-docs": {
      "type": "http",
      "url": "https://code.claude.com/docs/mcp"
    },
    "expenses": {
      "type": "stdio",
      "command": "python3",
      "args": ["${CLAUDE_PROJECT_DIR:-.}/mcp/server.py"]
    },
    "company-api": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": { "Authorization": "Bearer ${API_KEY}" }
    }
  }
}
''', '.mcp.json (at the project root, committed for the team)'),
    'scope-cmds': cli('''
claude mcp add --transport http stripe https://mcp.stripe.com                    # local (default)
claude mcp add --transport http shared --scope project https://example.com/mcp  # writes .mcp.json
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
claude mcp reset-project-choices   # forget your approvals of .mcp.json servers
''', 'Choosing a scope'),
    'py-steps': cli('''
mkdir expenses-mcp && cd expenses-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install "mcp>=2"
# write server.py (below), test it with try_it.py (below), then:
claude mcp add --transport stdio expenses -- "$PWD/.venv/bin/python" "$PWD/server.py"
''', 'Set up a Python server project'),
    'py-server': show(SERVER, 'server.py', lang='py', note='📄 Ready to copy'),
    'py-try': test({'server.py': SERVER, 'try_it.py': CLIENT}, '$PY try_it.py 2>/dev/null', 'Start the server and call its tools',
                   show=['try_it.py'], shown_cmd='python try_it.py', badge='▶ A real MCP client talks to the real server'),
    'wire': show(WIRE, 'The JSON messages on the wire', lang='text', note='📨 Captured from the server above, trimmed where it says ...'),
    'use': prompt('''
Add a ₹450 expense for printer ink, then tell me the total
Compare @github:issue://123 with @docs:file://api/authentication
/mcp__github__pr_review 456
''', 'Using tools, resources and prompts', result='Claude calls mcp__expenses__add_expense and mcp__expenses__total_spent. The @ mentions pull in two resources. The slash command runs a prompt the github server offers.'),
    'perm': js_('''
{
  "permissions": {
    "allow": ["mcp__expenses__*", "mcp__claude-code-docs__*"],
    "ask":   ["mcp__github__create_pull_request"],
    "deny":  ["mcp__company-api__delete_customer"]
  }
}
''', '.claude/settings.json: rules for MCP tools'),
    'desktop': js_('''
{
  "mcpServers": {
    "expenses": {
      "command": "/Users/asha/expenses-mcp/.venv/bin/python",
      "args": ["/Users/asha/expenses-mcp/server.py"]
    }
  }
}
''', 'claude_desktop_config.json (Claude Desktop app)'),
    'desktop-cmds': cli('''
claude mcp add-from-claude-desktop   # copy Desktop servers into Claude Code (macOS, WSL)
claude mcp serve                     # run Claude Code itself as an MCP server for other apps
''', 'Moving between Claude Desktop and Claude Code'),
}

PARTS = [
    part('what', '🔌', 'What MCP is', '''
<p><b>MCP</b> (Model Context Protocol) is an open standard that lets Claude use tools and data from other programs: your issue tracker, a database, a calendar, or a script you wrote yourself. One program, the <b>MCP server</b>, offers the tools. Claude Code, Claude Desktop and claude.ai are <b>MCP clients</b> that connect to it.</p>
<div class="viz" data-viz="flow" data-k="mcp"></div>
<div class="tw"><table class="jt"><tr><th>A server can offer</th><th>What it is</th><th>How you use it</th></tr>
<tr><td><b>Tools</b></td><td>actions Claude can run, like "add expense"</td><td>Claude calls them when they fit your request</td></tr>
<tr><td><b>Resources</b></td><td>read only data, like a file or a record</td><td>type <code>@server:uri</code> in your prompt</td></tr>
<tr><td><b>Prompts</b></td><td>ready made prompt templates</td><td>type <code>/mcp__server__prompt</code></td></tr></table></div>
''', easy=True, kw=['MCP', 'Model Context Protocol', 'server', 'client', 'tools', 'resources', 'prompts']),
    part('connect', '🧷', 'Connect a server, step by step', '''
<ol class="steps"><li>Find a server: the Anthropic Directory, or the vendor's own docs.</li>
<li>Run <code>claude mcp add</code> in your terminal, outside a session.</li>
<li>Check it with <code>claude mcp list</code>, or <code>/mcp</code> inside a session.</li>
<li>If it needs a login, open <code>/mcp</code> and pick it to sign in.</li>
<li>Ask for something the server can do.</li></ol>
[[first]]
[[add]]
<div class="cl-name">For a local server, the <code>--</code> matters. Everything after it is the command that starts the server, so flags like <code>--port</code> go to the server and not to Claude.</div>
''', easy=True, kw=['claude mcp add', '--transport http', 'stdio', 'claude mcp list', '/mcp']),
    part('setup-shots', '📸', 'Set up MCP in Claude Code, with screenshots', '''
<p>Here is the expenses server from this chapter added to Claude Code for real, then a shared server added for the whole team. The terminal pictures are real output, with the home folder shown as <code>~</code>.</p>
''' + shots('Connect MCP servers to Claude Code', [
        ('term-version', 'Check Claude Code is installed', 'Run <code>claude --version</code>. The <code>claude mcp</code> commands below work without starting a session.'),
        ('term-mcp-add', 'Add your own server, then check it', 'Use <code>--transport stdio</code> for a program on your computer. Everything after <code>--</code> is the command that starts it. Use full paths. <code>claude mcp list</code> starts each server and shows <b>✔ Connected</b> when the handshake works. <code>claude mcp get</code> shows the scope and command.'),
        ('term-mcp-project', 'Add a server for the whole team', '<code>--scope project</code> writes the server into <code>.mcp.json</code> at the project root, so it can be committed. For safety, Claude Code shows it as <b>Pending approval</b> until each person approves it once.'),
        ('ui-cc-mcp', 'Approve and use it inside a session', 'Run <code>claude</code>, approve the project server when asked, then type <code>/mcp</code> to see every server, its tools and its status. Now ask "add Rs 450 for printer ink and tell me the total".'),
    ]) + '''
<div class="tip">If <code>claude mcp list</code> shows <b>✘ Failed</b>, run the start command yourself in the terminal. The error you see there is the real reason, most often a wrong path or a missing package.</div>
''', easy=True, files=['~/.claude.json', '.mcp.json'], kw=['setup MCP', 'screenshots', 'claude mcp list', 'claude mcp get', 'pending approval', 'step by step']),
    part('scopes', '📍', 'Scopes and the .mcp.json file', '''
<div class="tw"><table class="jt"><tr><th>Scope</th><th>Loads in</th><th>Shared with team</th><th>Stored in</th></tr>
<tr><td>local (default)</td><td>this project only</td><td>no</td><td><code>~/.claude.json</code>, under this project</td></tr>
<tr><td>project</td><td>this project only</td><td>yes, through git</td><td><code>.mcp.json</code> at the project root</td></tr>
<tr><td>user</td><td>all your projects</td><td>no</td><td><code>~/.claude.json</code></td></tr></table></div>
[[scope-cmds]]
[[mcpjson]]
<div class="cl-put"><b>What goes in .mcp.json:</b> one entry per server under <code>mcpServers</code>. Each has a <code>type</code> (<code>http</code> or <code>stdio</code>), then <code>url</code> and <code>headers</code> for http, or <code>command</code>, <code>args</code> and <code>env</code> for stdio. Never write a real key here. Use <code>${API_KEY}</code> so each person's key comes from their own environment, and <code>${VAR:-default}</code> for a fallback.</div>
<div class="cl-name">The file is <code>.mcp.json</code> at the project root. Claude Code does not read <code>~/.claude/mcp.json</code> or <code>.claude/.mcp.json</code>. An http entry without <code>"type"</code> is an error, because an entry with no type is read as stdio.</div>
<p>When the same name is in several scopes, local wins, then project, then user. Claude Code asks once before it uses servers from a project's <code>.mcp.json</code>.</p>
''', files=['.mcp.json', '~/.claude.json'], kw=['scope', 'local', 'project', 'user', '.mcp.json', 'environment variables', '${VAR}']),
    part('build', '🐍', 'Build your own server in Python', '''
<p>Here is a server that saves expenses. Claude will be able to say "Saved team lunch for ₹850" because it called your code.</p>
<ol class="steps"><li>Make a folder, a virtual environment, and install the <code>mcp</code> package.</li><li>Write <code>server.py</code>: create an <code>MCPServer</code>, mark each tool with <code>@mcp.tool()</code>, then call <code>mcp.run()</code>. The type hints become the input schema and the docstring becomes the description.</li><li>Test it with a small client before you add it to Claude.</li><li>Add it with <code>claude mcp add</code> and ask Claude to use it.</li></ol>
[[py-steps]]
[[py-server]]
[[py-try]]
<div class="cl-put"><b>What makes a good tool:</b> a short verb name like <code>add_expense</code>, a docstring that says when to use it, a description on every input, and a reply that tells Claude what happened. Never <code>print()</code> in a stdio server, because stdout carries the messages. Log to stderr instead.</div>
<div class="cl-name">Version 2 of the Python <code>mcp</code> package imports <code>MCPServer</code> from <code>mcp.server</code>. Older tutorials use <code>FastMCP</code>, which version 2 no longer has.</div>
''', easy=True, files=['server.py'], kw=['build MCP server', 'Python MCP server', 'MCPServer', '@mcp.tool', '@mcp.resource', 'pip install mcp']),
    part('wire', '📨', 'What travels between Claude and a server', '''
<p>Under the hood, MCP is a conversation of small JSON messages (JSON-RPC). For a stdio server they go one per line on stdin and stdout. First a handshake, then Claude asks for the tool list, then it calls a tool. You never write these yourself, the SDK does it, but seeing them once makes the idea clear.</p>
[[wire]]
<p>Each tool's name, description and schema are what Claude reads to decide when to call it. That is why clear descriptions matter so much.</p>
''', kw=['JSON-RPC', 'initialize', 'tools/list', 'tools/call', 'protocol']),
    part('use', '🎛️', 'Using MCP inside Claude Code', '''
[[use]]
<p>Every MCP tool gets a full name <code>mcp__&lt;server&gt;__&lt;tool&gt;</code>. Use that name in permission rules, in a skill's <code>allowed-tools</code>, in an agent's <code>tools</code> and in hook matchers.</p>
[[perm]]
<ul><li>Claude warns when one tool result is over 10,000 tokens. The default limit is 25,000, set by <code>MAX_MCP_OUTPUT_TOKENS</code>.</li>
<li><b>Tool search</b> loads only tool names at start and fetches full definitions when needed, so many servers cost little context.</li>
<li>Only add servers you trust. A server can read what you send it and its replies go into Claude's context.</li></ul>
''', easy=True, files=['.claude/settings.json'], kw=['mcp__server__tool', 'permissions', 'resources @', 'MCP prompts', 'MAX_MCP_OUTPUT_TOKENS', 'tool search']),
    part('desktop', '🖥️', 'The same servers in Claude Desktop', '''
<p>The Claude Desktop chat app reads its own file, <code>claude_desktop_config.json</code>. Open it from Settings, then Developer, then Edit Config. On macOS it is in <code>~/Library/Application Support/Claude/</code> and on Windows in <code>%APPDATA%\\Claude\\</code>. Use full paths, then restart the app.</p>
[[desktop]]
[[desktop-cmds]]
<div class="scenario"><b>🧾 Real scenario: a shop owner</b>Asha runs a small bakery. Her nephew builds the expenses server above on her laptop and adds it to Claude Desktop. Now she types "add ₹1,200 for flour and tell me this week's total", and Claude saves it to her file and answers with the sum.</div>
''', files=['claude_desktop_config.json'], kw=['Claude Desktop', 'claude_desktop_config.json', 'add-from-claude-desktop', 'claude mcp serve']),
    part('connectors', '🧩', 'MCP in claude.ai: connectors, with screenshots', '''
<p>In claude.ai an MCP server is called a <b>connector</b>. Popular services are in the Connectors Directory. Your own server can be added as a <b>custom connector</b>. The difference from Claude Code: claude.ai connects to your server <b>from Anthropic's cloud</b>, so the server must be a remote (http) server that the internet can reach. A stdio server on your laptop cannot be added this way. Use Claude Desktop or Claude Code for that.</p>
''' + shots('Add and use a connector in claude.ai and Claude Desktop', [
        ('ui-connector-add', 'Add a custom connector', 'Open <b>Customize</b>, then <b>Connectors</b>, click <b>Add</b>, hover <b>Custom</b> and pick <b>Web</b>. Give it a name, paste the remote MCP server URL, and click <b>Continue</b>. Then choose how people sign in and click <b>Add</b>.'),
        ('ui-chat-plus', 'Turn it on in a chat', 'Click <b>+</b> in the message box, hover <b>Connectors</b> and switch on the ones this chat needs. <b>Tool access</b> is <b>Auto</b> by default. With ten or more connectors, <b>On demand</b> keeps the context small.'),
        ('ui-desktop-config', 'Local servers in Claude Desktop', 'For a server that runs on your own computer, open Claude Desktop, then <b>Settings</b>, <b>Developer</b>, <b>Edit Config</b>. Add the server to <code>claude_desktop_config.json</code> as shown above and restart the app.'),
    ]) + '''
<div class="tw"><table class="jt"><tr><th>Fact</th><th>What it means for you</th></tr>
<tr><td>Claude gets your permissions</td><td>if you cannot open a file in the source app, Claude cannot either</td></tr>
<tr><td>Free plan: one custom connector</td><td>paid plans can add more</td></tr>
<tr><td>Team and Enterprise</td><td>an owner enables a connector first, then each person signs in with their own account</td></tr>
<tr><td>Owners set tool permissions</td><td>each tool can be <b>Always allow</b>, <b>Needs approval</b> or <b>Blocked</b> for the whole organisation</td></tr></table></div>
<div class="warn">Custom connectors are not checked by Anthropic. Only add servers from people and companies you trust, because a connector can read and sometimes change data with your permissions.</div>
''', easy=True, files=['claude.ai Customize, Connectors', 'claude_desktop_config.json'], kw=['connectors', 'custom connector', 'claude.ai MCP', 'remote MCP', 'tool access', 'Connectors Directory']),
]

DG = {
    'mcp': {'t': 'Claude Code, an MCP server and your data', 'w': 900, 'h': 240,
            'n': [['you', 20, 90, 110, 56, 'You', {'c': 5, 'sh': 'pill'}],
                  ['cc', 170, 90, 180, 56, 'Claude Code', {'c': 1, 'sub': 'MCP client'}],
                  ['srv', 420, 90, 190, 56, 'MCP server', {'c': 3, 'sub': 'expenses', 'i': 'A small program that offers tools, resources and prompts.'}],
                  ['data', 690, 20, 180, 56, 'expenses.json', {'c': 0, 'sh': 'doc'}],
                  ['api', 690, 160, 180, 56, 'any app or API', {'c': 4, 'sh': 'doc'}]],
            'e': [['you', 'cc'], ['cc', 'srv', {'t': 'tools/call'}], ['srv', 'data'], ['srv', 'api']],
            'st': [[['you', 'cc', 'you>cc'], 'You ask: add ₹120 for an auto ride.'],
                   [['srv', 'cc>srv'], 'Claude Code sees the add_expense tool and calls it with item and amount.'],
                   [['data', 'api', 'srv>data', 'srv>api'], 'The server does the real work: it writes the file or calls an app.'],
                   [['cc', 'srv'], 'The server replies with text, and Claude tells you what happened.']]},
}

INFO = {'title': 'MCP: connect Claude to anything', 'panels': [
    panel([['e', '🔌'], ['t', 'claude mcp add', {'b': 1}]], 'Connect', 'http for hosted services.', 'stdio for programs on your computer.'),
    panel([['e', '📄'], ['t', '.mcp.json', {'b': 1}]], 'Share', 'Project scope goes in .mcp.json.', 'Keys stay in ${VARS}.'),
    panel([['e', '🛠️'], ['t', '@mcp.tool()', {'b': 1}]], 'Build', 'A Python function with a docstring.', 'Type hints become the schema.'),
    panel([['e', '🔐'], ['t', 'mcp__server__tool', {'b': 1}]], 'Control', 'Allow, ask or deny per tool.', 'Only add servers you trust.')],
    'remember': 'A clear tool description is what makes Claude pick the right tool.'}

REAL = [
    ['🐛', 'A product team', 'Connects Jira and GitHub servers. "Implement PROJ-412 and open a pull request" now works end to end in one session.'],
    ['📊', 'An analyst', 'Adds a read only Postgres server with project scope, so everyone on the team can ask "how many sign-ups last week" in plain words.'],
    ['🏫', 'A school teacher', 'Builds a small timetable server in Python for the class laptop, the same way as the expenses server. Students ask Claude "what do I have on Tuesday" and get the real answer.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter connects Claude to other apps with MCP, and builds a real Python server step by step.',
        'यह अध्याय MCP से Claude को दूसरे apps से जोड़ता है और Python में एक असली server बनाता है।',
        'ಈ ಅಧ್ಯಾಯ MCP ಮೂಲಕ Claude ಅನ್ನು ಇತರ apps ಗೆ ಜೋಡಿಸಿ Python ನಲ್ಲಿ ಒಂದು server ಕಟ್ಟುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ MCP ଦ୍ୱାରା Claude କୁ ଅନ୍ୟ apps ସହ ଯୋଡେ ଓ Python ରେ ଗୋଟିଏ server ତିଆରି କରେ।',
        'يربط هذا الفصل Claude بتطبيقات أخرى عبر MCP ويبني خادمًا حقيقيًا بلغة Python.',
        'Dieses Kapitel verbindet Claude per MCP mit anderen Apps und baut einen echten Python-Server.'),
    say('what', 'What it is', 'MCP is an open standard. A server offers tools, resources and prompts, and Claude Code connects to it as a client.',
        'MCP एक खुला मानक है। Server tools, resources और prompts देता है।',
        'MCP ಒಂದು ಮುಕ್ತ ಮಾನಕ. Server tools, resources, prompts ನೀಡುತ್ತದೆ.',
        'MCP ଏକ ମୁକ୍ତ ମାନକ। Server tools, resources ଓ prompts ଦିଏ।',
        'MCP معيار مفتوح. الخادم يقدّم أدوات وموارد وموجّهات.',
        'MCP ist ein offener Standard. Ein Server bietet Tools, Ressourcen und Prompts.'),
    say('connect', 'Connect', 'Run claude mcp add with http for hosted services or stdio for local programs, then check with claude mcp list.',
        'Hosted के लिए http, local के लिए stdio के साथ claude mcp add चलाएँ।',
        'Hosted ಗೆ http, local ಗೆ stdio ಜೊತೆ claude mcp add ಚಲಾಯಿಸಿ.',
        'Hosted ପାଇଁ http, local ପାଇଁ stdio ସହ claude mcp add ଚଲାନ୍ତୁ।',
        'شغّل claude mcp add مع http للخدمات المستضافة أو stdio للبرامج المحلية.',
        'Nutze claude mcp add mit http für gehostete Dienste oder stdio für lokale Programme.'),
    say('scopes', 'Scopes', 'Local is just you in this project, project goes in the shared dot mcp dot json file, and user is all your projects.',
        'Local सिर्फ आप, project साझा .mcp.json में, user सभी projects।',
        'Local ನೀವು ಮಾತ್ರ, project ಹಂಚಿದ .mcp.json, user ಎಲ್ಲಾ projects.',
        'Local କେବଳ ଆପଣ, project ଅଂଶୀଦାର .mcp.json, user ସବୁ projects।',
        'المحلي لك وحدك، والمشروع في .mcp.json المشترك، والمستخدم لكل مشاريعك.',
        'Local nur für dich, project in der geteilten .mcp.json, user für alle Projekte.'),
    say('build', 'Python server', 'Decorate a Python function with mcp dot tool. Type hints become the schema, the docstring becomes the description, and a small client tests it.',
        'Python में function पर @mcp.tool लगाएँ। Type hints schema बनते हैं।',
        'Python ನಲ್ಲಿ function ಗೆ @mcp.tool ಹಾಕಿ. Type hints schema ಆಗುತ್ತವೆ.',
        'Python ରେ function ଉପରେ @mcp.tool ଦିଅନ୍ତୁ। Type hints schema ହୁଏ।',
        'في Python زيّن الدالة بـ mcp.tool وتصبح التلميحات مخططًا.',
        'In Python dekorierst du eine Funktion mit mcp.tool. Typhinweise werden zum Schema.'),
    say('wire', 'On the wire', 'Client and server swap small JSON messages: a handshake, a tools list request, then tool calls.',
        'Client और server छोटे JSON संदेश भेजते हैं: handshake, tools list, फिर calls।',
        'Client ಮತ್ತು server ಸಣ್ಣ JSON ಸಂದೇಶಗಳನ್ನು ವಿನಿಮಯ ಮಾಡುತ್ತವೆ.',
        'Client ଓ server ଛୋଟ JSON ବାର୍ତ୍ତା ଅଦଳବଦଳ କରନ୍ତି।',
        'يتبادل العميل والخادم رسائل JSON صغيرة: مصافحة ثم قائمة أدوات ثم استدعاءات.',
        'Client und Server tauschen kleine JSON-Nachrichten: Handshake, Toolliste, dann Aufrufe.'),
    say('use', 'Using it', 'Each tool is named mcp, server, tool. Use that name in permission rules. Mention resources with at and run prompts with a slash.',
        'हर tool का नाम mcp__server__tool होता है। इसे permission rules में लिखें।',
        'ಪ್ರತಿ tool ಹೆಸರು mcp__server__tool. ಅದನ್ನು permission rules ನಲ್ಲಿ ಬಳಸಿ.',
        'ପ୍ରତି tool ର ନାମ mcp__server__tool. ଏହାକୁ permission rules ରେ ଲେଖନ୍ତୁ।',
        'اسم كل أداة mcp__server__tool. استخدمه في قواعد الأذونات.',
        'Jedes Tool heißt mcp__server__tool. Nutze den Namen in Berechtigungsregeln.'),
    say('setup-shots', 'Setup with screenshots', 'Add your server with claude mcp add, check it with claude mcp list, add a team server with scope project, then approve it and look at slash mcp.',
        'claude mcp add से server जोड़ें, claude mcp list से जांचें, scope project से team server, फिर /mcp देखें।',
        'claude mcp add ಇಂದ ಸೇರಿಸಿ, claude mcp list ಇಂದ ಪರಿಶೀಲಿಸಿ, scope project, ನಂತರ /mcp.',
        'claude mcp add ରେ ଯୋଡନ୍ତୁ, claude mcp list ରେ ଯାଞ୍ଚ, scope project, ପରେ /mcp.',
        'أضف الخادم بـ claude mcp add وتحقق بـ claude mcp list ثم خادم الفريق ثم /mcp.',
        'Server mit claude mcp add hinzufügen, mit claude mcp list prüfen, Team-Server mit scope project, dann /mcp.'),
    say('connectors', 'Connectors', 'In claude dot ai an MCP server is a connector. Add a custom one under Customize, Connectors, then switch it on from the plus menu in a chat.',
        'claude.ai में MCP server को connector कहते हैं। Customize, Connectors में जोड़ें, फिर chat के + menu से चालू करें।',
        'claude.ai ನಲ್ಲಿ MCP server ಅಂದರೆ connector. Customize, Connectors ನಲ್ಲಿ ಸೇರಿಸಿ, + menu ಇಂದ ಆನ್ ಮಾಡಿ.',
        'claude.ai ରେ MCP server କୁ connector କୁହାଯାଏ। Customize, Connectors ରେ ଯୋଡନ୍ତୁ, + menu ରୁ ଚାଲୁ କରନ୍ତୁ।',
        'في claude.ai يسمى خادم MCP موصلًا. أضفه من Customize ثم Connectors وفعّله من قائمة + في المحادثة.',
        'In claude.ai heißt ein MCP-Server Connector. Unter Customize, Connectors hinzufügen und im Chat über + einschalten.'),
    say('desktop', 'Desktop', 'Claude Desktop reads claude desktop config dot json. Use full paths and restart the app.',
        'Claude Desktop claude_desktop_config.json पढ़ता है। पूरे paths लिखें।',
        'Claude Desktop claude_desktop_config.json ಓದುತ್ತದೆ. ಪೂರ್ಣ paths ಬಳಸಿ.',
        'Claude Desktop claude_desktop_config.json ପଢେ। ପୂରା paths ଲେଖନ୍ତୁ।',
        'يقرأ Claude Desktop الملف claude_desktop_config.json. استخدم مسارات كاملة.',
        'Claude Desktop liest claude_desktop_config.json. Nutze volle Pfade.'),
    say('practice', 'Practice', 'Test yourself on tool names, scopes and environment variables.',
        'Tool नाम, scopes और variables का अभ्यास करें।',
        'Tool ಹೆಸರು, scopes, variables ಅಭ್ಯಾಸ.',
        'Tool ନାମ, scopes ଓ variables ଅଭ୍ୟାସ।',
        'تدرّب على أسماء الأدوات والنطاقات والمتغيرات.',
        'Übe Toolnamen, Scopes und Variablen.'),
]

QUIZ = [
    quiz('e', 'What does an MCP server give Claude?', ['Tools, resources and prompts', 'A new model', 'More context window', 'A login'], 0, 'Three kinds of things.', 'Servers offer tools, resources and prompts.'),
    quiz('e', 'Which transport is recommended for a hosted MCP server?', ['http', 'sse', 'ftp', 'stdio'], 0, 'SSE is deprecated.', 'Use --transport http for remote servers.'),
    quiz('e', 'Where do project scoped servers live?', ['.mcp.json at the project root', '.claude/mcp.json', 'CLAUDE.md', '~/.claude/settings.json'], 0, 'Shared through git.', 'Project scope writes .mcp.json at the root.'),
    quiz('m', 'In claude mcp add ... -- python server.py --port 8080, who gets --port?', ['The server', 'Claude Code', 'Nobody', 'npm'], 0, 'After the double dash.', 'Everything after -- is passed to the server untouched.'),
    quiz('m', 'Why must a stdio server not use print()?', ['stdout carries the protocol messages', 'It is slow', 'It is not allowed in Python', 'It deletes files'], 0, 'Think about the wire.', 'Log to stderr so the JSON stream stays clean.'),
    quiz('m', 'What is the full name of the add_expense tool on the expenses server?', ['mcp__expenses__add_expense', 'expenses.add_expense', 'add_expense@expenses', 'mcp:expenses:add_expense'], 0, 'Two underscores each.', 'MCP tools are named mcp__server__tool.'),
    quiz('h', 'How should an API key appear in a shared .mcp.json?', ['${API_KEY}', 'The real key', 'In a comment', 'Base64 encoded'], 0, 'Each person has their own.', 'Environment variable expansion keeps secrets out of git.'),
    quiz('h', 'In version 2 of the Python mcp package, what do you import?', ['MCPServer from mcp.server', 'FastMCP from mcp.server.fastmcp', 'Server from anthropic', 'McpServer from zod'], 0, 'The name changed.', 'FastMCP was removed in version 2.'),
    quiz('m', 'claude mcp list shows a project server as Pending approval. What do you do?', ['Start claude in the project and approve it once', 'Delete .mcp.json', 'Reinstall Claude Code', 'Add it again with scope user'], 0, 'A safety check.', 'Servers from a shared .mcp.json need each person to approve them once.'),
    quiz('h', 'Can you add a stdio server that runs on your laptop as a claude.ai custom connector?', ['No, claude.ai connects from the cloud to a remote server', 'Yes, paste the python command', 'Only on the Free plan', 'Only on mobile'], 0, 'Who connects to whom.', 'Use Claude Desktop or Claude Code for local servers, or host the server on the internet.'),
    quiz('e', 'In a claude.ai chat, where do you switch a connector on?', ['The + button in the message box, then Connectors', 'Settings, Billing', 'The Artifacts tab', 'You cannot choose'], 0, 'The message box.', 'Hover Connectors and toggle the ones this chat needs.'),
    quiz('x', 'An http entry in .mcp.json has a url but no type. What happens?', ['It is skipped with an error', 'It works as http', 'It works as sse', 'Claude asks which'], 0, 'No type means stdio.', 'Add "type": "http".'),
    quiz('x', 'A tool returns 30,000 tokens with default settings. What happens?', ['It is saved to a file and Claude gets the path', 'Claude crashes', 'It is cut to 100 words', 'Nothing'], 0, 'Default limit 25,000.', 'Large results are written to a file Claude can read when needed.'),
]

CALC = [
    calc('e', 'After the auto rickshaw (₹120) and team lunch (₹850), what total does total_spent report?', '970', 'Add the two.', ['<span class="eq">120 + 850 = 970</span>'], alt=['₹970']),
    calc('e', 'How many tools does the expenses server offer?', '2', 'Read the list.', ['add_expense and total_spent.']),
    calc('m', 'A server has 40 tools at 300 tokens each. How many tokens would loading them all up front cost?', '12000', 'Multiply.', ['<span class="eq">40 × 300 = 12,000</span>'], alt=['12,000']),
    calc('m', 'With tool search only names load, about 15 tokens each. How many tokens for the same 40 tools?', '600', 'Multiply.', ['<span class="eq">40 × 15 = 600</span>']),
    calc('h', 'A result is 18,000 tokens. How many tokens over the 10,000 warning line is it?', '8000', 'Subtract.', ['<span class="eq">18,000 − 10,000 = 8,000</span>'], alt=['8,000']),
    calc('x', 'In the wire messages, how many requests carry an id?', '3', 'Count the CLAUDE CODE lines with an id.', ['initialize, tools/list and tools/call. The initialized notification has no id.']),
]

EX = []

T = {
    'slug': 'claude-mcp', 'title': 'MCP: Connect and Build Servers', 'short': 'MCP servers', 'emoji': '🔌', 'module': MODULE, 'minutes': 26,
    'lead': 'What MCP is, connecting your first server in three steps, scopes and exactly what goes in .mcp.json, building a real expenses server in Python step by step, the JSON that travels between them, using MCP in Claude Code and Claude Desktop, and adding connectors in claude.ai, with a screenshot for every setup step.',
    'plain': 'MCP lets Claude use other programs. You write a small program that says "I can add an expense", and when you ask Claude to add one, Claude asks your program to do it.',
    'desc': 'MCP for Claude Code: claude mcp add, http and stdio, scopes, .mcp.json with environment variables, building MCP servers in Python, JSON-RPC messages, mcp__ tool names and Claude Desktop config.',
    'summary': 'What MCP servers offer, connecting a first server, managing servers, local, project and user scopes with a full .mcp.json, a Python expenses server built and tested with a real client, the JSON-RPC handshake on the wire, tool names and permission rules, output limits and tool search, claude_desktop_config.json, a screenshot guide with real claude mcp output, and custom connectors in claude.ai.',
    'keywords': ['MCP', 'Model Context Protocol', 'claude mcp add', '.mcp.json', 'scopes', 'MCPServer', '@mcp.tool', 'Python MCP', 'JSON-RPC', 'mcp__', 'Claude Desktop', 'claude_desktop_config.json', 'connectors', 'custom connector', 'screenshots'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
