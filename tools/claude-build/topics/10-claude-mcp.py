# Chapter 10: MCP. What it is, connecting servers, scopes and .mcp.json, building a server in Node.js and in Python
# step by step, what travels on the wire, using tools, resources and prompts, and Claude Desktop.
from ckit import part, run, test, show, md, cli, prompt, js_, say, quiz, calc, ex, panel, node_files

MODULE = ('🛠️', 'Claude Code and its files', 'claude-code-files', 'Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.')

SERVER = r'''
// server.mjs: a small MCP server that saves expenses to a file.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync, writeFileSync, existsSync } from "node:fs";

const FILE = "expenses.json";
const load = () => (existsSync(FILE) ? JSON.parse(readFileSync(FILE, "utf8")) : []);

const server = new McpServer({ name: "expenses", version: "1.0.0" });

// Tool 1: save one expense. The description tells Claude when to use it.
server.registerTool("add_expense", {
  title: "Add an expense",
  description: "Save one expense with what it was for and the amount in rupees.",
  inputSchema: {
    item: z.string().describe("What the money was spent on"),
    amount: z.number().positive().describe("Amount in rupees"),
  },
}, async ({ item, amount }) => {
  const list = load();
  list.push({ item, amount });
  writeFileSync(FILE, JSON.stringify(list, null, 2));
  return { content: [{ type: "text", text: `Saved ${item} for ₹${amount}. Expenses saved: ${list.length}.` }] };
});

// Tool 2: add everything up.
server.registerTool("total_spent", {
  title: "Total spent",
  description: "Add up every saved expense and say the total in rupees.",
  inputSchema: {},
}, async () => {
  const total = load().reduce((sum, e) => sum + e.amount, 0);
  return { content: [{ type: "text", text: `Total spent: ₹${total}` }] };
});

// stdio servers talk on stdin and stdout, so log to stderr only.
await server.connect(new StdioServerTransport());
console.error("expenses MCP server is running");
'''

CLIENT = r'''
// try-it.mjs: plays the part of Claude Code. It starts the server, lists its tools and calls them.
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const client = new Client({ name: "try-it", version: "1.0.0" });
await client.connect(new StdioClientTransport({ command: "node", args: ["server.mjs"], stderr: "ignore" }));

const { tools } = await client.listTools();
console.log("Tools the server offers:");
for (const t of tools) console.log(" -", t.name + ":", t.description);

const call = async (name, args = {}) => {
  const r = await client.callTool({ name, arguments: args });
  console.log(`${name}(${JSON.stringify(args)}) ->`, r.isError ? "ERROR " : "", r.content[0].text.split("\n")[0]);
};
await call("add_expense", { item: "auto rickshaw", amount: 120 });
await call("add_expense", { item: "team lunch", amount: 850 });
await call("total_spent");
await call("add_expense", { item: "refund", amount: -50 });   // the schema says positive, so this is refused

await client.close();
'''

PYSERVER = '''
# timetable.py: a small MCP server in Python with one tool and one resource.
from mcp.server import MCPServer

mcp = MCPServer("timetable")

TIMETABLE = {
    "monday": ["Maths", "English", "Science", "Art"],
    "tuesday": ["Hindi", "Maths", "Games", "Computers"],
}


@mcp.tool()
def classes_on(day: str) -> str:
    """List the classes for one school day, for example monday."""
    lessons = TIMETABLE.get(day.lower())
    if not lessons:
        return f"No timetable saved for {day}."
    return f"{day.title()}: " + ", ".join(lessons)


@mcp.resource("timetable://week")
def whole_week() -> str:
    """The whole week's timetable."""
    return "\\n".join(f"{d}: {', '.join(l)}" for d, l in TIMETABLE.items())


if __name__ == "__main__":
    mcp.run()   # stdio by default
'''

PYCLIENT = r'''
// try-python.mjs: starts the Python server the same way Claude Code would and uses it.
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const client = new Client({ name: "try-python", version: "1.0.0" });
await client.connect(new StdioClientTransport({ command: process.env.PY, args: ["timetable.py"], stderr: "ignore" }));

const { tools } = await client.listTools();
for (const t of tools) console.log("tool:", t.name, "| input:", JSON.stringify(t.inputSchema.properties));

for (const day of ["Monday", "sunday"]) {
  const r = await client.callTool({ name: "classes_on", arguments: { day } });
  console.log(`classes_on(${day}) ->`, r.content[0].text);
}

const { resources } = await client.listResources();
console.log("resources:", resources.map(r => r.uri).join(", "));
const week = await client.readResource({ uri: "timetable://week" });
console.log(week.contents[0].text);
await client.close();
'''

WIRE = r'''
// wire.mjs: shows the exact JSON messages that travel between Claude Code and an MCP server.
import { spawn } from "node:child_process";
import { createInterface } from "node:readline";

const server = spawn("node", ["server.mjs"], { stdio: ["pipe", "pipe", "ignore"] });
const replies = createInterface({ input: server.stdout });
const waiting = new Map();
replies.on("line", line => { const m = JSON.parse(line); waiting.get(m.id)?.(m); });

let id = 0;
const send = (method, params) => new Promise(resolve => {
  const msg = { jsonrpc: "2.0", id: ++id, method, params };
  console.log("CLAUDE CODE ->", JSON.stringify(msg));
  waiting.set(id, m => { console.log("SERVER      <-", JSON.stringify(m.result).slice(0, 150) + "\n"); resolve(m); });
  server.stdin.write(JSON.stringify(msg) + "\n");
});

await send("initialize", { protocolVersion: "2025-11-25", capabilities: {}, clientInfo: { name: "demo", version: "1" } });
server.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
await send("tools/list", {});
await send("tools/call", { name: "add_expense", arguments: { item: "chai", amount: 20 } });
server.kill();
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
      "command": "node",
      "args": ["${CLAUDE_PROJECT_DIR:-.}/mcp/server.mjs"]
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
    'node-steps': cli('''
mkdir expenses-mcp && cd expenses-mcp
npm init -y
npm pkg set type=module
npm install @modelcontextprotocol/sdk zod
# write server.mjs (below), then test it (below), then:
claude mcp add --transport stdio expenses -- node "$PWD/server.mjs"
''', 'Set up a Node.js server project'),
    'node-server': show(SERVER, 'server.mjs', lang='js', note='📄 Ready to copy'),
    'node-try': test(node_files({'server.mjs': SERVER, 'try-it.mjs': CLIENT}), 'node try-it.mjs', 'Start the server and call its tools',
                     show=['try-it.mjs'], badge='▶ A real MCP client talks to the real server'),
    'py-steps': cli('''
mkdir timetable-mcp && cd timetable-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install "mcp>=2"
# write timetable.py (below), then:
claude mcp add --transport stdio timetable -- "$PWD/.venv/bin/python" "$PWD/timetable.py"
''', 'Set up a Python server project'),
    'py-server': show(PYSERVER, 'timetable.py', lang='py', note='📄 Ready to copy'),
    'py-try': test(node_files({'timetable.py': PYSERVER, 'try-python.mjs': PYCLIENT}), 'node try-python.mjs', 'Start the Python server and use it',
                   show=['try-python.mjs'], badge='▶ The Python server answers a real MCP client'),
    'wire': test(node_files({'server.mjs': SERVER, 'wire.mjs': WIRE}), 'node wire.mjs', 'The JSON messages on the wire',
                 show=['wire.mjs'], badge='▶ Every line below was really sent and received'),
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
      "command": "node",
      "args": ["/Users/asha/expenses-mcp/server.mjs"]
    },
    "timetable": {
      "command": "/Users/asha/timetable-mcp/.venv/bin/python",
      "args": ["/Users/asha/timetable-mcp/timetable.py"]
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
    part('build-node', '🟩', 'Build your own server in Node.js', '''
<p>Here is a server that saves expenses. Claude will be able to say "Saved team lunch for ₹850" because it called your code.</p>
<ol class="steps"><li>Make a folder and install the SDK and zod.</li><li>Write <code>server.mjs</code>: create an <code>McpServer</code>, register each tool with a name, a description and an input schema, then connect over stdio.</li><li>Test it with a small client before you add it to Claude.</li><li>Add it with <code>claude mcp add</code> and ask Claude to use it.</li></ol>
[[node-steps]]
[[node-server]]
[[node-try]]
<div class="cl-put"><b>What makes a good tool:</b> a short verb name like <code>add_expense</code>, a description that says when to use it, an input schema with a description on every field, and a reply that tells Claude what happened. Never <code>console.log</code> in a stdio server, because stdout carries the messages. Use <code>console.error</code>.</div>
''', easy=True, files=['server.mjs', 'package.json'], kw=['build MCP server', 'McpServer', 'registerTool', 'zod', 'StdioServerTransport', 'Node.js']),
    part('build-py', '🐍', 'Build your own server in Python', '''
<p>The same idea in Python: a school timetable that a child could ask about. The function's type hints become the input schema and the docstring becomes the description.</p>
[[py-steps]]
[[py-server]]
[[py-try]]
<div class="cl-name">Version 2 of the Python <code>mcp</code> package imports <code>MCPServer</code> from <code>mcp.server</code>. Older tutorials use <code>FastMCP</code>, which version 2 no longer has.</div>
''', easy=True, files=['timetable.py'], kw=['Python MCP server', 'MCPServer', '@mcp.tool', '@mcp.resource', 'pip install mcp']),
    part('wire', '📨', 'What travels between Claude and a server', '''
<p>Under the hood, MCP is a conversation of small JSON messages (JSON-RPC). For a stdio server they go one per line on stdin and stdout. First a handshake, then Claude asks for the tool list, then it calls a tool.</p>
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
    panel([['e', '🛠️'], ['t', 'registerTool', {'b': 1}]], 'Build', 'Name, description, schema, handler.', 'Node.js or Python.'),
    panel([['e', '🔐'], ['t', 'mcp__server__tool', {'b': 1}]], 'Control', 'Allow, ask or deny per tool.', 'Only add servers you trust.')],
    'remember': 'A clear tool description is what makes Claude pick the right tool.'}

REAL = [
    ['🐛', 'A product team', 'Connects Jira and GitHub servers. "Implement PROJ-412 and open a pull request" now works end to end in one session.'],
    ['📊', 'An analyst', 'Adds a read only Postgres server with project scope, so everyone on the team can ask "how many sign-ups last week" in plain words.'],
    ['🏫', 'A school teacher', 'Builds the timetable server in Python for the class laptop. Students ask Claude "what do I have on Tuesday" and get the real answer.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter connects Claude to other apps with MCP, and builds two real servers step by step, one in Node and one in Python.',
        'यह अध्याय MCP से Claude को दूसरे apps से जोड़ता है और दो असली servers बनाता है।',
        'ಈ ಅಧ್ಯಾಯ MCP ಮೂಲಕ Claude ಅನ್ನು ಇತರ apps ಗೆ ಜೋಡಿಸಿ ಎರಡು servers ಕಟ್ಟುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ MCP ଦ୍ୱାରା Claude କୁ ଅନ୍ୟ apps ସହ ଯୋଡେ ଓ ଦୁଇଟି server ତିଆରି କରେ।',
        'يربط هذا الفصل Claude بتطبيقات أخرى عبر MCP ويبني خادمين حقيقيين.',
        'Dieses Kapitel verbindet Claude per MCP mit anderen Apps und baut zwei echte Server.'),
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
    say('build-node', 'Node server', 'Create an MCP server, register each tool with a name, description and schema, connect over stdio, and test it with a client.',
        'McpServer बनाएँ, हर tool को नाम, विवरण और schema दें, फिर test करें।',
        'McpServer ರಚಿಸಿ, ಪ್ರತಿ tool ಗೆ ಹೆಸರು, ವಿವರಣೆ, schema ಕೊಡಿ.',
        'McpServer ତିଆରି କରି ପ୍ରତି tool କୁ ନାମ, ବର୍ଣ୍ଣନା ଓ schema ଦିଅନ୍ତୁ।',
        'أنشئ خادمًا وسجّل كل أداة باسم ووصف ومخطط ثم اختبره.',
        'Erstelle einen Server, registriere jedes Tool mit Name, Beschreibung und Schema und teste ihn.'),
    say('build-py', 'Python server', 'In Python, decorate a function with mcp dot tool. Type hints become the schema and the docstring becomes the description.',
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
    say('desktop', 'Desktop', 'Claude Desktop reads claude desktop config dot json. Use full paths and restart the app.',
        'Claude Desktop claude_desktop_config.json पढ़ता है। पूरे paths लिखें।',
        'Claude Desktop claude_desktop_config.json ಓದುತ್ತದೆ. ಪೂರ್ಣ paths ಬಳಸಿ.',
        'Claude Desktop claude_desktop_config.json ପଢେ। ପୂରା paths ଲେଖନ୍ତୁ।',
        'يقرأ Claude Desktop الملف claude_desktop_config.json. استخدم مسارات كاملة.',
        'Claude Desktop liest claude_desktop_config.json. Nutze volle Pfade.'),
    say('practice', 'Practice', 'Practise tool names, scopes and environment variable expansion.',
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
    quiz('m', 'Why must a stdio server not print with console.log?', ['stdout carries the protocol messages', 'It is slow', 'It is not allowed in Node', 'It deletes files'], 0, 'Think about the wire.', 'Log to stderr so the JSON stream stays clean.'),
    quiz('m', 'What is the full name of the add_expense tool on the expenses server?', ['mcp__expenses__add_expense', 'expenses.add_expense', 'add_expense@expenses', 'mcp:expenses:add_expense'], 0, 'Two underscores each.', 'MCP tools are named mcp__server__tool.'),
    quiz('h', 'How should an API key appear in a shared .mcp.json?', ['${API_KEY}', 'The real key', 'In a comment', 'Base64 encoded'], 0, 'Each person has their own.', 'Environment variable expansion keeps secrets out of git.'),
    quiz('h', 'In version 2 of the Python mcp package, what do you import?', ['MCPServer from mcp.server', 'FastMCP from mcp.server.fastmcp', 'Server from anthropic', 'McpServer from zod'], 0, 'The name changed.', 'FastMCP was removed in version 2.'),
    quiz('x', 'An http entry in .mcp.json has a url but no type. What happens?', ['It is skipped with an error', 'It works as http', 'It works as sse', 'Claude asks which'], 0, 'No type means stdio.', 'Add "type": "http".'),
    quiz('x', 'A tool returns 30,000 tokens with default settings. What happens?', ['It is saved to a file and Claude gets the path', 'Claude crashes', 'It is cut to 100 words', 'Nothing'], 0, 'Default limit 25,000.', 'Large results are written to a file Claude can read when needed.'),
]

CALC = [
    calc('e', 'After the auto rickshaw (₹120) and team lunch (₹850), what total does total_spent report?', '970', 'Add the two.', ['<span class="eq">120 + 850 = 970</span>'], alt=['₹970']),
    calc('e', 'How many tools does the expenses server offer?', '2', 'Read the list.', ['add_expense and total_spent.']),
    calc('m', 'A server has 40 tools at 300 tokens each. How many tokens would loading them all up front cost?', '12000', 'Multiply.', ['<span class="eq">40 × 300 = 12,000</span>'], alt=['12,000']),
    calc('m', 'With tool search only names load, about 15 tokens each. How many tokens for the same 40 tools?', '600', 'Multiply.', ['<span class="eq">40 × 15 = 600</span>']),
    calc('h', 'A result is 18,000 tokens. How many tokens over the 10,000 warning line is it?', '8000', 'Subtract.', ['<span class="eq">18,000 − 10,000 = 8,000</span>'], alt=['8,000']),
    calc('x', 'In the wire demo, how many requests with an id did the client send?', '3', 'Count the CLAUDE CODE lines.', ['initialize, tools/list and tools/call. The initialized notification has no id.']),
]

EX = [
    ex('full-name', 'e', 'Full tool name', '<p>Write <code>toolName(server, tool)</code> that returns the full MCP tool name, such as <code>mcp__expenses__add_expense</code>. Replace any <code>.</code> or space in the server name with <code>_</code>.</p>',
       'function toolName(server, tool) {\n  \n}\n',
       [('toolName("expenses", "add_expense")', 'mcp__expenses__add_expense'), ('toolName("my.server", "go")', 'mcp__my_server__go'), ('toolName("team db", "query")', 'mcp__team_db__query')],
       'function toolName(server, tool) {\n  return "mcp__" + server.replace(/[. ]/g, "_") + "__" + tool;\n}',
       hint='Use a regular expression with the g flag.', why='You need the exact name for permission rules, skills and hooks.'),
    ex('which-file', 'm', 'Which file?', '<p>Write <code>fileFor(scope)</code> that returns where a server added with that scope is stored: <code>"~/.claude.json"</code> for <code>local</code> and <code>user</code>, <code>".mcp.json"</code> for <code>project</code>, and <code>null</code> for anything else.</p>',
       'function fileFor(scope) {\n  \n}\n',
       [('fileFor("local")', '~/.claude.json'), ('fileFor("project")', '.mcp.json'), ('fileFor("user")', '~/.claude.json'), ('fileFor("team")', None)],
       'function fileFor(scope) {\n  if (scope === "project") return ".mcp.json";\n  if (scope === "local" || scope === "user") return "~/.claude.json";\n  return null;\n}',
       hint='Only project scope writes a file in the repository.', why='Knowing the file tells you who will see the server.'),
    ex('expand', 'h', 'Expand ${VAR}', '<p>Write <code>expand(text, env)</code> that replaces <code>${NAME}</code> with <code>env.NAME</code> and <code>${NAME:-fallback}</code> with <code>env.NAME</code> or the fallback when it is not set. Leave an unset <code>${NAME}</code> with no fallback as it is.</p>',
       'function expand(text, env) {\n  \n}\n',
       [('expand("${A}/mcp", { A: "https://x.io" })', 'https://x.io/mcp'), ('expand("${B:-https://api.example.com}/mcp", {})', 'https://api.example.com/mcp'), ('expand("Bearer ${KEY}", {})', 'Bearer ${KEY}')],
       'function expand(text, env) {\n  return text.replace(/\\$\\{(\\w+)(?::-([^}]*))?\\}/g, (whole, name, fallback) =>\n    env[name] ?? fallback ?? whole);\n}',
       hint='One regular expression with an optional group for the fallback.', why='This is how .mcp.json keeps keys and machine paths out of git.'),
]

T = {
    'slug': 'claude-mcp', 'title': 'MCP: Connect and Build Servers', 'short': 'MCP servers', 'emoji': '🔌', 'module': MODULE, 'minutes': 20,
    'lead': 'What MCP is, connecting your first server in three steps, scopes and exactly what goes in .mcp.json, building a real expenses server in Node.js and a timetable server in Python step by step, the JSON that travels between them, and using MCP in Claude Code and Claude Desktop.',
    'plain': 'MCP lets Claude use other programs. You write a small program that says "I can add an expense", and when you ask Claude to add one, Claude asks your program to do it.',
    'desc': 'MCP for Claude Code: claude mcp add, http and stdio, scopes, .mcp.json with environment variables, building MCP servers in Node.js and Python, JSON-RPC messages, mcp__ tool names and Claude Desktop config.',
    'summary': 'What MCP servers offer, connecting a first server, managing servers, local, project and user scopes with a full .mcp.json, a Node.js expenses server and a Python timetable server built and tested with a real client, the JSON-RPC handshake on the wire, tool names and permission rules, output limits and tool search, and claude_desktop_config.json.',
    'keywords': ['MCP', 'Model Context Protocol', 'claude mcp add', '.mcp.json', 'scopes', 'McpServer', 'registerTool', 'MCPServer', 'Python MCP', 'JSON-RPC', 'mcp__', 'Claude Desktop', 'claude_desktop_config.json'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
