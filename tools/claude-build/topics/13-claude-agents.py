# Chapter 13: build agents. Tools and the agent loop by hand, the tool runner, safety gates, the Claude Agent SDK,
# and how to choose between the ways of building an agent. SDK code runs against a local stand-in API.
from ckit import part, show, cli, say, quiz, calc, panel, api_run

MODULE = ('🔌', 'Building with the API', 'claude-build-api', 'Call Claude from your own code: the Messages API, tools, agent loops and the Agent SDK.')

SHOP = '''
STOCK = {"basmati rice": 6, "toor dal": 14, "sugar": 25}      # bags in the store room
PRICE = {"basmati rice": 900, "toor dal": 1400, "sugar": 2100}  # rupees per bag
'''

TOOLS_JSON = '''
TOOLS = [
    {
        "name": "check_stock",
        "description": "Look up how many bags of one item are in the store room. Use before ordering.",
        "input_schema": {
            "type": "object",
            "properties": {"item": {"type": "string", "description": "Item name, for example toor dal"}},
            "required": ["item"],
        },
    },
    {
        "name": "place_order",
        "description": "Order more bags of an item from the wholesaler. Only order when stock is low.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item": {"type": "string"},
                "bags": {"type": "integer", "description": "How many bags to order"},
            },
            "required": ["item", "bags"],
        },
    },
]
'''

MANUAL = '''
import anthropic
from shop import STOCK, PRICE
from tools import TOOLS

client = anthropic.Anthropic()

def run_tool(name, args):
    """Your code does the real work. Claude only asks."""
    if name == "check_stock":
        return f"{STOCK.get(args['item'], 0)} bags of {args['item']} in stock"
    if name == "place_order":
        cost = args["bags"] * PRICE[args["item"]]
        return f"Order placed: {args['bags']} bags of {args['item']} for ₹{cost:,}"
    return f"Unknown tool {name}"

messages = [{"role": "user", "content": "Do we have enough basmati rice? If fewer than 10 bags, order 20."}]

for step in range(1, 11):                      # never loop for ever
    response = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=2000, tools=TOOLS, messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":     # Claude is finished
        print("FINAL:", response.content[0].text)
        break

    results = []
    for block in response.content:
        if block.type == "text":
            print(f"step {step} | Claude: {block.text}")
        if block.type == "tool_use":
            output = run_tool(block.name, block.input)
            print(f"step {step} | tool {block.name}({block.input}) -> {output}")
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
    messages.append({"role": "user", "content": results})
'''

RUNNER = '''
import anthropic
from anthropic import beta_tool
from shop import STOCK, PRICE

client = anthropic.Anthropic()
LIMIT = 10_000   # rupees: bigger orders need the owner

@beta_tool
def check_stock(item: str) -> str:
    """Look up how many bags of one item are in the store room. Use before ordering.

    Args:
        item: Item name, for example toor dal.
    """
    return f"{STOCK.get(item, 0)} bags of {item} in stock"

@beta_tool
def place_order(item: str, bags: int) -> str:
    """Order more bags of an item from the wholesaler. Only order when stock is low.

    Args:
        item: Item name.
        bags: How many bags to order.
    """
    cost = bags * PRICE[item]
    if cost > LIMIT:                            # a safety gate in plain code
        return f"Not placed: ₹{cost:,} is over the ₹{LIMIT:,} limit. Ask the owner to approve."
    return f"Order placed: {bags} bags of {item} for ₹{cost:,}"

runner = client.beta.messages.tool_runner(
    model="claude-sonnet-5-5",
    max_tokens=2000,
    tools=[check_stock, place_order],
    messages=[{"role": "user", "content": "Do we have enough basmati rice? If fewer than 10 bags, order 20."}],
)

for message in runner:                          # the SDK runs the loop and calls your functions
    for block in message.content:
        if block.type == "text":
            print("Claude:", block.text)
        elif block.type == "tool_use":
            print("  calls", block.name, block.input)
'''

STEPS = {
    'steps': [
        {'say': 'I will check the basmati rice stock first.', 'calls': [{'name': 'check_stock', 'input': {'item': 'basmati rice'}}]},
        {'say': 'Only 6 bags are left, which is fewer than 10, so I will order 20.', 'calls': [{'name': 'place_order', 'input': {'item': 'basmati rice', 'bags': 20}}]},
    ],
}

SDK_AGENT = '''
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def main():
    async for message in query(
        prompt="Read sales.csv, find the 3 slowest selling items this month and write reorder.md with advice.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Glob"],     # what it may do without asking
            permission_mode="acceptEdits",
            system_prompt="You help a small shop owner. Use simple words and rupees.",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                elif hasattr(block, "name"):
                    print("Tool:", block.name)
        elif isinstance(message, ResultMessage):
            print("Done:", message.subtype)

asyncio.run(main())
'''

CODES = {
    'tools': show(TOOLS_JSON, 'tools.py: two tool definitions', lang='py', note='📄 Ready to copy'),
    'manual': api_run(MANUAL, 'The agent loop written by hand', {**STEPS, 'final': 'Done. {result}. You now have enough basmati rice.'},
                      name='agent.py', more={'shop.py': SHOP, 'tools.py': TOOLS_JSON}),
    'runner': api_run(RUNNER, 'The same agent with the tool runner and a spending limit', {**STEPS, 'final': 'I could not finish the order. {result}'},
                      name='runner.py', more={'shop.py': SHOP}),
    'sdk-install': cli('''
mkdir shop-agent && cd shop-agent
python3 -m venv .venv && source .venv/bin/activate
pip install claude-agent-sdk
export ANTHROPIC_API_KEY="sk-ant-..."
python agent.py
''', 'Install the Claude Agent SDK'),
    'sdk': show(SDK_AGENT, 'agent.py: an agent with Claude Code\'s own tools', lang='py', note='📄 Ready to copy'),
}

PARTS = [
    part('what', '🔁', 'What an agent really is', '''
<p>An <b>agent</b> is Claude plus <b>tools</b> plus a <b>loop</b>. Claude reads the goal, asks for a tool, your code runs it and sends back the result, and this repeats until Claude says it is done.</p>
<div class="viz" data-viz="flow" data-k="loop"></div>
<ol class="steps"><li>You send the goal and the list of tools.</li><li>Claude replies with <code>stop_reason: "tool_use"</code> and a <code>tool_use</code> block: a name and inputs.</li><li>Your code runs the tool and sends a <code>tool_result</code> with the same id.</li><li>Repeat until <code>stop_reason</code> is <code>end_turn</code>.</li></ol>
<div class="cl-put">Claude never runs anything itself. It only asks. Your code decides what actually happens, which is where you put limits and checks.</div>
''', easy=True, kw=['agent', 'agent loop', 'tool_use', 'tool_result', 'stop_reason']),
    part('tools', '🧰', 'Define tools Claude can use', '''
<p>A tool is a name, a description and an <b>input schema</b>. Claude chooses tools by reading the descriptions, so write them for a new colleague: what it does, when to use it and what each input means.</p>
[[tools]]
<div class="tw"><table class="jt"><tr><th>Good</th><th>Weak</th></tr>
<tr><td><code>check_stock</code>: "Look up how many bags... Use before ordering."</td><td><code>tool1</code>: "stock"</td></tr>
<tr><td>one clear job per tool</td><td>one tool with a <code>mode</code> field that does five things</td></tr>
<tr><td>results that say what happened, in words</td><td>a bare <code>true</code></td></tr></table></div>
''', easy=True, kw=['tool definition', 'input_schema', 'tool description', 'JSON schema']),
    part('manual', '✍️', 'Build the loop by hand, step by step', '''
<p>Here is a shopkeeper's assistant. It checks the rice stock, sees it is low and places an order, in two rounds of tool use.</p>
[[manual]]
<ul><li>Append Claude's whole reply to <code>messages</code>, then your tool results as the next user turn.</li><li>Each <code>tool_result</code> carries the <code>tool_use_id</code> it answers.</li><li>The <code>for step in range(1, 11)</code> is a hard limit so a confused agent stops.</li></ul>
''', easy=True, files=['agent.py', 'tools.py'], kw=['manual agent loop', 'tool_use_id', 'messages', 'max steps']),
    part('runner', '🏃', 'Less code with the tool runner', '''
<p>The SDK's <b>tool runner</b> writes the loop for you. Decorate a normal Python function with <code>@beta_tool</code>: the type hints become the schema and the docstring becomes the description.</p>
[[runner]]
<div class="scenario"><b>🛑 The safety gate worked</b>20 bags at ₹900 is ₹18,000, over the ₹10,000 limit. The order function refused in plain code and Claude reported back instead of trying again. Put money, deletes and emails behind checks like this.</div>
''', files=['runner.py'], kw=['tool runner', '@beta_tool', 'tool_runner', 'safety gate', 'human approval']),
    part('sdk', '🧠', 'The Claude Agent SDK: Claude Code as a library', '''
<p>The <b>Agent SDK</b> gives your program the same tools, loop, permissions, hooks, skills and MCP support as Claude Code. You do not write tools for reading files or running commands. You just say which ones are allowed.</p>
[[sdk-install]]
[[sdk]]
<div class="tw"><table class="jt"><tr><th>Tools allowed</th><th>What the agent can do</th></tr>
<tr><td><code>Read</code>, <code>Glob</code>, <code>Grep</code></td><td>look but not touch</td></tr>
<tr><td><code>Read</code>, <code>Edit</code>, <code>Glob</code></td><td>read and change files</td></tr>
<tr><td>plus <code>Bash</code></td><td>run commands and tests too</td></tr></table></div>
<p>The Agent SDK also loads <code>CLAUDE.md</code>, skills and settings from <code>.claude/</code>, so everything from the earlier chapters works here too.</p>
''', easy=True, kw=['Claude Agent SDK', 'claude-agent-sdk', 'query', 'ClaudeAgentOptions', 'allowed_tools']),
    part('choose', '🧭', 'Which way to build your agent', '''
<div class="tw"><table class="jt"><tr><th>You want</th><th>Use</th></tr>
<tr><td>one answer, no tools</td><td>a single <code>messages.create</code> call (chapter 12)</td></tr>
<tr><td>your own tools, full control of each step</td><td>the hand written loop</td></tr>
<tr><td>your own tools, less code</td><td>the tool runner</td></tr>
<tr><td>files, commands, web, skills, MCP, ready made</td><td>the Claude Agent SDK</td></tr>
<tr><td>Anthropic to run the loop and the sandbox for you</td><td>Managed Agents on the Claude API</td></tr>
<tr><td>help inside your own coding sessions</td><td>Claude Code subagents (chapter 9)</td></tr></table></div>
<div class="cl-put"><b>Start simple.</b> Many jobs that sound like agents are a fixed chain of two or three calls. Use a real agent only when the steps cannot be known in advance. Then give it few tools, clear descriptions, a step limit and checks on anything risky.</div>
''', easy=True, kw=['choose agent approach', 'Managed Agents', 'workflow vs agent', 'start simple']),
]

DG = {
    'loop': {'t': 'The agent loop', 'w': 900, 'h': 250,
             'n': [['goal', 20, 95, 140, 56, 'Goal + tools', {'c': 5, 'sh': 'pill'}],
                   ['claude', 230, 95, 170, 56, 'Claude', {'c': 1, 'sub': 'decides the next step'}],
                   ['ask', 470, 20, 170, 56, 'tool_use', {'c': 3, 'sub': 'name + inputs', 'sh': 'doc'}],
                   ['code', 710, 95, 170, 56, 'Your code', {'c': 0, 'sub': 'runs the tool', 'i': 'Checks, limits and approvals live here.'}],
                   ['res', 470, 170, 170, 56, 'tool_result', {'c': 4, 'sub': 'what happened', 'sh': 'doc'}]],
             'e': [['goal', 'claude'], ['claude', 'ask'], ['ask', 'code'], ['code', 'res'], ['res', 'claude']],
             'st': [[['goal', 'claude', 'goal>claude'], 'You send the goal and the tools.'],
                    [['ask', 'claude>ask'], 'Claude asks for a tool by name with inputs.'],
                    [['code', 'ask>code'], 'Your code runs it. Claude never runs anything itself.'],
                    [['res', 'code>res', 'res>claude'], 'The result goes back and the loop repeats until Claude is done.']]},
}

INFO = {'title': 'Agents: model, tools, loop', 'panels': [
    panel([['e', '🧰'], ['t', 'name + description + schema', {'b': 1, 'size': 11}]], 'Tools', 'Descriptions decide which tool is used.', 'One job per tool.'),
    panel([['e', '🔁'], ['t', 'tool_use → tool_result', {'b': 1, 'size': 11}]], 'Loop', 'Repeat until end_turn.', 'Cap the steps.'),
    panel([['e', '🛑'], ['t', 'if cost > LIMIT', {'b': 1}]], 'Gates', 'Your code has the final say.', 'Money, deletes, emails.'),
    panel([['e', '🧠'], ['t', 'claude-agent-sdk', {'b': 1}]], 'Agent SDK', 'Claude Code as a library.', 'Built-in tools ready.')],
    'remember': 'Claude asks, your code acts. Put the rules in the code.'}

REAL = [
    ['🏪', 'A kirana chain', 'Runs the stock agent from this chapter every night across 12 stores. Orders under ₹10,000 go through, bigger ones wait for the owner.'],
    ['🧑‍💼', 'An HR team', 'Built an onboarding agent with the Agent SDK that reads the joining checklist, creates accounts through MCP tools and writes a welcome note.'],
    ['🔧', 'A support desk', 'Gives an agent three tools: search the help centre, read an order and draft a reply. A person approves every reply before it is sent.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter builds agents: Claude plus tools plus a loop, first by hand, then with the tool runner and the Agent SDK.',
        'यह अध्याय agents बनाता है: Claude, tools और loop।',
        'ಈ ಅಧ್ಯಾಯ agents ಕಟ್ಟುತ್ತದೆ: Claude, tools ಮತ್ತು loop.',
        'ଏହି ଅଧ୍ୟାୟ agents ତିଆରି କରେ: Claude, tools ଓ loop।',
        'يبني هذا الفصل الوكلاء: Claude مع الأدوات والحلقة.',
        'Dieses Kapitel baut Agenten: Claude, Tools und eine Schleife.'),
    say('what', 'What an agent is', 'Claude asks for a tool, your code runs it and sends the result back, and this repeats until Claude is done.',
        'Claude tool माँगता है, आपका code चलाता है और नतीजा लौटाता है।',
        'Claude tool ಕೇಳುತ್ತದೆ, ನಿಮ್ಮ code ಚಲಾಯಿಸಿ ಫಲಿತಾಂಶ ಕಳುಹಿಸುತ್ತದೆ.',
        'Claude tool ମାଗେ, ଆପଣଙ୍କ code ଚଲାଇ ଫଳାଫଳ ପଠାଏ।',
        'يطلب Claude أداة فتشغّلها شيفرتك وتعيد النتيجة حتى ينتهي.',
        'Claude fordert ein Tool an, dein Code führt es aus und schickt das Ergebnis zurück.'),
    say('tools', 'Tools', 'A tool has a name, a description and an input schema. Clear descriptions decide which tool Claude picks.',
        'Tool का नाम, विवरण और schema होता है। साफ़ विवरण ज़रूरी है।',
        'Tool ಗೆ ಹೆಸರು, ವಿವರಣೆ, schema ಇರುತ್ತದೆ.',
        'Tool ର ନାମ, ବର୍ଣ୍ଣନା ଓ schema ଥାଏ।',
        'للأداة اسم ووصف ومخطط مدخلات، والوصف الواضح يحدد الاختيار.',
        'Ein Tool hat Name, Beschreibung und Eingabeschema.'),
    say('manual', 'By hand', 'Append the reply, run each tool, send results with the matching id, and stop after a fixed number of steps.',
        'जवाब जोड़ें, tool चलाएँ, सही id के साथ नतीजा भेजें।',
        'ಉತ್ತರ ಸೇರಿಸಿ, tool ಚಲಾಯಿಸಿ, id ಜೊತೆ ಫಲಿತಾಂಶ ಕಳುಹಿಸಿ.',
        'ଉତ୍ତର ଯୋଡି tool ଚଲାନ୍ତୁ ଓ id ସହ ଫଳାଫଳ ପଠାନ୍ତୁ।',
        'أضف الرد وشغّل الأداة وأرسل النتيجة بالمعرّف نفسه.',
        'Antwort anhängen, Tool ausführen, Ergebnis mit passender ID senden.'),
    say('runner', 'Tool runner', 'The tool runner writes the loop. Put safety limits inside the tool function itself.',
        'Tool runner loop लिखता है। सुरक्षा सीमा function में रखें।',
        'Tool runner loop ಬರೆಯುತ್ತದೆ. ಸುರಕ್ಷತಾ ಮಿತಿ function ನಲ್ಲಿ.',
        'Tool runner loop ଲେଖେ। ସୁରକ୍ଷା ସୀମା function ରେ।',
        'منفّذ الأدوات يكتب الحلقة، وضع حدود الأمان داخل الدالة.',
        'Der Tool Runner schreibt die Schleife. Sicherheitsgrenzen gehören in die Funktion.'),
    say('sdk', 'Agent SDK', 'The Agent SDK gives your program Claude Code\'s own tools and loop. You only choose which tools are allowed.',
        'Agent SDK आपके program को Claude Code के tools देता है।',
        'Agent SDK ನಿಮ್ಮ program ಗೆ Claude Code tools ನೀಡುತ್ತದೆ.',
        'Agent SDK ଆପଣଙ୍କ program କୁ Claude Code tools ଦିଏ।',
        'تمنح حزمة الوكلاء برنامجك أدوات Claude Code وحلقته.',
        'Das Agent SDK gibt deinem Programm die Tools von Claude Code.'),
    say('choose', 'Choosing', 'Start with the simplest option. Use a full agent only when the steps cannot be known in advance.',
        'सबसे सरल तरीके से शुरू करें।',
        'ಸರಳ ಮಾರ್ಗದಿಂದ ಆರಂಭಿಸಿ.',
        'ସରଳ ଉପାୟରୁ ଆରମ୍ଭ କରନ୍ତୁ।',
        'ابدأ بأبسط خيار.',
        'Beginne mit der einfachsten Lösung.'),
    say('practice', 'Practice', 'Test yourself on tool results, loop limits and spending gates.',
        'Tool results, loop सीमा और खर्च सीमा का अभ्यास।',
        'Tool results, loop ಮಿತಿ ಅಭ್ಯಾಸ.',
        'Tool results ଓ loop ସୀମା ଅଭ୍ୟାସ।',
        'تدرّب على نتائج الأدوات وحدود الحلقة.',
        'Übe Tool-Ergebnisse und Schleifengrenzen.'),
]

QUIZ = [
    quiz('e', 'What three things make an agent?', ['Model, tools and a loop', 'A key, a prompt and a file', 'Two models', 'A chat window'], 0, 'Think of the diagram.', 'Claude, tools and a loop that repeats.'),
    quiz('e', 'Who actually runs a tool?', ['Your code', 'Claude', 'The browser', 'Anthropic, always'], 0, 'Claude only asks.', 'Your code runs it and returns the result.'),
    quiz('e', 'Which stop_reason means Claude wants a tool?', ['tool_use', 'end_turn', 'max_tokens', 'refusal'], 0, 'The name says it.', 'Run the tool and send a tool_result.'),
    quiz('m', 'What must a tool_result include?', ['The tool_use_id it answers', 'The API key', 'The model name', 'The full chat'], 0, 'Matching.', 'The id links the result to the request.'),
    quiz('m', 'What decides which tool Claude picks?', ['The tool names and descriptions', 'The order of the list only', 'The price', 'Random choice'], 0, 'Write them well.', 'Clear descriptions lead to the right tool.'),
    quiz('m', 'What does @beta_tool turn into the input schema?', ['The type hints', 'The function body', 'The return value', 'Comments'], 0, 'Python typing.', 'The docstring becomes the description.'),
    quiz('h', 'Where should a spending limit live?', ['In the tool function code', 'Only in the system prompt', 'In the tool name', 'Nowhere'], 0, 'Code always runs.', 'A prompt can be ignored. Code cannot.'),
    quiz('h', 'Why cap the number of loop steps?', ['So a confused agent stops', 'To save the key', 'The API needs it', 'To stream faster'], 0, 'Safety.', 'It bounds time and cost.'),
    quiz('x', 'Which option gives your program file and shell tools without writing them?', ['The Claude Agent SDK', 'A single messages.create call', 'A JSON schema', 'Prompt caching'], 0, 'Claude Code as a library.', 'It includes Read, Edit, Bash, Glob and more.'),
    quiz('x', 'A task is always: extract fields, then translate, then email. Best design?', ['A fixed chain of calls', 'A fully autonomous agent', 'Ten subagents', 'No code'], 0, 'Steps are known.', 'Use agents only when steps are not known ahead.'),
]

CALC = [
    calc('e', 'In the hand written loop, how many API requests were made?', '3', 'Count the request lines.', ['Two rounds of tools and one final answer.']),
    calc('e', 'How many messages were in the last request?', '5', 'Read the request lines.', ['The goal, then two pairs of tool request and tool result.']),
    calc('m', 'What does an order of 20 bags of basmati rice cost at ₹900 a bag?', '18000', 'Multiply.', ['<span class="eq">20 × 900 = 18,000</span>'], alt=['18,000', '₹18,000']),
    calc('m', 'With a ₹10,000 limit, what is the most bags of rice the agent may order?', '11', 'Divide and round down.', ['<span class="eq">⌊10,000 ÷ 900⌋ = 11</span>']),
    calc('h', 'A loop sends about 3,000 input tokens per step for 6 steps on Sonnet 5.5 ($2 per million). Input cost in dollars?', '0.036', 'Tokens × steps × price.', ['<span class="eq">3,000 × 6 × 2 ÷ 10⁶ = 0.036</span>'], alt=['$0.036']),
    calc('x', 'The history grows by 800 tokens per step from 2,000. Total input tokens over 5 steps?', '18000', 'Add 2,000, 2,800, 3,600, 4,400 and 5,200.', ['<span class="eq">2,000 + 2,800 + 3,600 + 4,400 + 5,200 = 18,000</span>'], alt=['18,000']),
]

EX = []

T = {
    'slug': 'claude-agents', 'title': 'Build Your Own Agents', 'short': 'Build agents', 'emoji': '🤖', 'module': MODULE, 'minutes': 20,
    'lead': 'What an agent is, how to define tools, a shopkeeper\'s stock agent built by hand with the loop shown step by step, the same agent with the tool runner and a spending limit, the Claude Agent SDK, and how to choose the simplest approach that works.',
    'plain': 'An agent is Claude doing a job in several steps. It asks your program to do small things, like "check the rice", and decides the next step from each answer.',
    'desc': 'Build AI agents with Claude: tool definitions, the agentic loop with tool_use and tool_result, the Python tool runner with @beta_tool, safety gates, the Claude Agent SDK and choosing between agents and workflows.',
    'summary': 'The agent loop explained, writing tool definitions, a two round stock agent built by hand and run step by step, the tool runner version with a spending gate that refuses a big order, the Claude Agent SDK with built-in tools, and a table for choosing the right approach.',
    'keywords': ['agents', 'agent loop', 'tools', 'tool_use', 'tool_result', 'tool runner', '@beta_tool', 'Claude Agent SDK', 'claude-agent-sdk', 'safety gate', 'Managed Agents'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
