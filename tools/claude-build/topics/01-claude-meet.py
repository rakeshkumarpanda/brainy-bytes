# Chapter 1: what Claude is, where it lives, the models, tokens and the context window, claude.ai Projects and Skills.
from ckit import part, show, md, prompt, say, quiz, calc, panel

MODULE = ('🌱', 'Foundations', 'claude-foundations', 'What Claude is, how to talk to it, and how to give it the right information at the right time.')

CODES = {
    'project-instr': md('''
# Project instructions: "Shop Support Replies"

You help the support team of GreenLeaf, an online plant shop in Pune, write replies to customers.

## Tone
- Warm, short and clear. Most customers read on a phone.
- Use the customer's first name once, at the start.
- Never promise a refund. Say "I have passed this to our refunds team" instead.

## What to do with each message
1. Find the order number (format GL-12345). If it is missing, ask for it.
2. Check the policy files in this project before answering anything about returns or delivery.
3. End with one clear next step for the customer.

## Format
Plain text, no headings, at most 120 words.
''', 'Project instructions for a support team'),
    'skill-zip': show('''
invoice-checker.zip
└── invoice-checker/
    ├── SKILL.md            <- required: name, description, then the steps
    ├── checklist.md        <- optional: extra detail Claude reads only when needed
    └── scripts/
        └── totals.py       <- optional: code Claude can run
''', 'What a skill upload looks like', lang='text', note='📦 Upload in Customize, Skills'),
    'first-prompt': prompt('''
I run a small home bakery. Every Sunday I get about 30 WhatsApp orders.
Here are this week's orders, pasted below.

Please:
1. Make a table with name, item, quantity and pickup time.
2. Add up how many of each item I need to bake.
3. List anyone who did not give a pickup time.

<orders>
Riya: 2 chocolate cakes, pickup 10am
Arjun: 12 cupcakes
Meera: 1 chocolate cake and 6 cupcakes, 4pm
</orders>
''', 'A first useful prompt', result='Claude returns a three column table, totals of 3 chocolate cakes and 18 cupcakes, and flags Arjun for a missing pickup time.'),
}

PARTS = [
    part('what', '👋', 'What Claude is, in plain words', '''
<p><b>Claude</b> is an AI model made by Anthropic. You write to it in normal language and it writes back. It can read and write text, look at images and PDFs, write and run code, and use tools you connect to it.</p>
<p>Think of a very well read helper who has just joined your team. It knows a lot in general but knows <b>nothing about your work</b> until you tell it. Most of this subject is about one skill: telling Claude the right things, in the right file, at the right time.</p>
<div class="tw"><table class="jt"><tr><th>I want to...</th><th>Use</th><th>What it is</th></tr>
<tr><td>chat, write, plan, study</td><td><b>claude.ai</b>, the desktop app or the mobile app</td><td>A chat window. Add files, use Projects and Skills.</td></tr>
<tr><td>let Claude work inside my files and code</td><td><b>Claude Code</b></td><td>An agent that reads, edits and runs things in a folder. Works in the terminal, VS Code, JetBrains, the desktop app and the web.</td></tr>
<tr><td>put Claude inside my own app or script</td><td><b>Claude API</b></td><td>Send messages from code and get answers back.</td></tr>
</table></div>
<div class="tip">You do not need to be a programmer for the first chapters. Every step names the exact button, file or command.</div>
''', easy=True, kw=['what is Claude', 'Anthropic', 'claude.ai', 'Claude Code', 'Claude API', 'desktop app']),
    part('models', '🧠', 'The Claude models and when to pick each', '''
<p>Claude comes in a family of models. Bigger models think more deeply. Smaller ones are faster and cheaper. All four current models read up to <b>1 million tokens</b> at once and can write up to <b>128 thousand tokens</b> in one answer.</p>
<div class="tw"><table class="jt"><tr><th>Model</th><th>API name</th><th>Price per million tokens (in / out)</th><th>Pick it for</th></tr>
<tr><td>Claude Fable 5.1</td><td><code>claude-fable-5-1</code></td><td>$10 / $50</td><td>the hardest, longest tasks</td></tr>
<tr><td>Claude Opus 5.5</td><td><code>claude-opus-5-5</code></td><td>$4 / $20</td><td>most serious work, coding and agents. The usual default.</td></tr>
<tr><td>Claude Sonnet 5.5</td><td><code>claude-sonnet-5-5</code></td><td>$2 / $10</td><td>everyday work at a good speed</td></tr>
<tr><td>Claude Haiku 5.5</td><td><code>claude-haiku-5-5</code></td><td>from $0.10 / $0.50</td><td>quick, simple, high volume jobs like sorting emails</td></tr>
</table></div>
<p>In claude.ai and Claude Code you switch models from the model menu or with <code>/model</code>. In the API you put the name in the <code>model</code> field.</p>
<div class="warn">Model names and prices change over time. Before you build something that costs money, check the models page in the Claude docs.</div>
''', easy=True, kw=['models', 'Opus', 'Sonnet', 'Haiku', 'Fable', 'pricing', 'model id']),
    part('tokens', '🔢', 'Tokens and the context window', '''
<p>Claude does not read letters or whole words. It reads <b>tokens</b>, which are small pieces of text. A short word is usually one token. A long word may be two or three.</p>
<p>The <b>context window</b> is everything Claude can see at one moment: your messages, its replies, files you attach and any instructions. It is measured in tokens. 1 million tokens is roughly 555 thousand English words.</p>
<p>Price is also counted in tokens. <b>Input tokens</b> are what you send. <b>Output tokens</b> are what Claude writes, and they cost five times more.</p>
<div class="fun">Even with a huge window, less is more. A focused page of the right facts beats a pile of loosely related files. Chapter 3 is all about this.</div>
''', easy=True, files=[], kw=['tokens', 'context window', '1M tokens', 'input tokens', 'output tokens', 'cost']),
    part('turns', '🔁', 'How a conversation really works', '''
<p>Claude has no hidden memory between messages. Each time you press send, the app sends the <b>whole conversation so far</b>, and Claude reads all of it again before replying.</p>
<div class="viz" data-viz="lanes" data-k="chat"></div>
<p>Two habits follow from this:</p>
<ul><li>Start a <b>new chat</b> when you switch to a new task. Old messages about the last task only distract.</li>
<li>Put facts Claude needs <b>every time</b> in a place that is loaded every time: project instructions in claude.ai, <code>CLAUDE.md</code> in Claude Code, or the system prompt in the API.</li></ul>
''', easy=True, kw=['conversation', 'messages', 'system prompt', 'new chat', 'stateless']),
    part('first', '✍️', 'Your first useful prompt', '''
<p>A good prompt says <b>who you are</b>, <b>what you have</b>, <b>what you want</b> and <b>what shape the answer should take</b>. Here is one a home baker could send on any Sunday.</p>
[[first-prompt]]
<p>Notice the three numbered steps and the <code>&lt;orders&gt;</code> tags around the data. Numbered steps tell Claude the order of work. Tags show where the data starts and ends. Chapter 2 explains both.</p>
''', easy=True, kw=['first prompt', 'daily automation', 'table', 'orders']),
    part('projects', '🗂️', 'claude.ai Projects: instructions plus knowledge', '''
<p>A <b>Project</b> in claude.ai is a folder for chats about one topic. It has two places to put information:</p>
<div class="vs"><div><b>📝 Project instructions</b>How Claude should behave in every chat of this project: tone, rules, format, steps. Keep it short.</div>
<div><b>📚 Project knowledge</b>Files Claude can look things up in: policies, price lists, style guides, past reports.</div></div>
<ol class="steps"><li>Open claude.ai and choose <b>Projects</b>, then <b>Create project</b>.</li>
<li>Give it a name and a short description.</li>
<li>Paste your instructions into the project instructions box.</li>
<li>Add files to the project knowledge.</li>
<li>Start chats inside the project. Each one gets the instructions and can read the files.</li></ol>
[[project-instr]]
<div class="cl-put"><ul><li><b>Instructions:</b> who Claude is helping, tone, steps to follow, output format, things it must never do.</li>
<li><b>Knowledge:</b> facts that are too long for the instructions, such as a full returns policy.</li></ul></div>
<p>Free accounts can create up to five projects. On paid plans, when the knowledge grows large, Claude searches it and pulls in only the relevant pieces.</p>
''', easy=True, files=['claude.ai Project instructions', 'Project knowledge'], kw=['claude.ai Projects', 'project instructions', 'project knowledge', 'custom instructions']),
    part('skills-intro', '🧰', 'Skills: teach Claude a task once', '''
<p>A <b>Skill</b> is a folder with a file called <code>SKILL.md</code>. The file has a short name and description at the top and the steps for one task below. Claude reads only the name and description at first. When a request matches, it opens the full file. That way you can have many skills without filling the context window.</p>
[[skill-zip]]
<p>To add a skill in claude.ai:</p>
<ol class="steps"><li>Open <b>Settings</b>, then <b>Capabilities</b>, and turn on <b>Code execution and file creation</b>.</li>
<li>Open <b>Customize</b>, then <b>Skills</b>. Click <b>+</b>, then <b>+ Create skill</b>, then <b>Upload a skill</b>, and pick a ZIP file of the skill folder.</li>
<li>Ask for the task in a normal chat, for example "check this invoice". Claude uses the skill when the description matches.</li></ol>
<p>The same <code>SKILL.md</code> format works in Claude Code and the API. Chapter 7 builds skills step by step.</p>
''', easy=True, files=['SKILL.md'], kw=['skills', 'SKILL.md', 'upload skill', 'zip', 'capabilities']),
    part('map', '🗺️', 'The map of this subject', '''
<p>Each tool and file you will learn has one job. Hover or tap a box to see where it lives.</p>
<div class="viz" data-viz="flow" data-k="map"></div>
<div class="tw"><table class="jt"><tr><th>When you want Claude to...</th><th>Use</th><th>Chapter</th></tr>
<tr><td>do one thing well right now</td><td>a clear prompt</td><td>2</td></tr>
<tr><td>always know facts about your project</td><td><code>CLAUDE.md</code></td><td>5</td></tr>
<tr><td>follow rules only for some files</td><td><code>.claude/rules/*.md</code></td><td>6</td></tr>
<tr><td>do a repeatable task the same way each time</td><td><code>SKILL.md</code></td><td>7</td></tr>
<tr><td>never do something, with no exceptions</td><td>permissions and hooks in <code>settings.json</code></td><td>8</td></tr>
<tr><td>hand a side task to a helper</td><td><code>.claude/agents/*.md</code></td><td>9</td></tr>
<tr><td>reach a tool or service outside your computer</td><td>an MCP server in <code>.mcp.json</code></td><td>10</td></tr>
</table></div>
''', easy=True, files=['CLAUDE.md', '.claude/rules/', 'SKILL.md', 'settings.json', '.claude/agents/', '.mcp.json'], kw=['overview', 'which file', 'map']),
    part('habits', '🛡️', 'Safe habits from day one', '''
<ul><li><b>Check important facts.</b> Claude can be wrong and sound sure. Ask it to quote the source line from your file when facts matter.</li>
<li><b>Never paste passwords or API keys</b> into a chat or a <code>CLAUDE.md</code>. Keys belong in environment variables.</li>
<li><b>Read before you approve.</b> When Claude Code asks to run a command or edit a file, read what it wants to do.</li>
<li><b>Keep humans in charge of sending.</b> Let Claude draft the email or the post. You press send.</li></ul>
<div class="scenario"><b>🧑‍🏫 Real scenario: a teacher</b>A maths teacher pastes a class list with phone numbers to make a seating plan. Better: replace phone numbers with roll numbers first. Claude only needs names and heights to plan seats.</div>
''', easy=True, kw=['safety', 'privacy', 'API keys', 'review']),
]

LANES = {
    'chat': {'t': 'What Claude reads on each turn', 's': 'Step through three messages and watch the list grow.', 'code': 'You: Plan a trip to Goa\nYou: Make day 2 kid friendly\nYou: Now a packing list',
             'lanes': ['What is sent to Claude', 'What Claude writes'], 'tone': [2, 1],
             'steps': [{'l': 1, 'v': [['system prompt', 'You: plan a trip'], []], 'm': 'Turn 1: the instructions and your first message are sent.'},
                       {'l': 1, 'v': [['system prompt', 'You: plan a trip'], ['Day 1 beaches...']], 'm': 'Claude replies.'},
                       {'l': 2, 'v': [['system prompt', 'You: plan a trip', 'Claude: Day 1...', 'You: kid friendly'], ['Swap the forts...']], 'm': 'Turn 2: everything is sent again, plus the new message.'},
                       {'l': 3, 'v': [['system prompt', 'You: plan a trip', 'Claude: Day 1...', 'You: kid friendly', 'Claude: Swap...', 'You: packing list'], ['Sunscreen, hats...']], 'm': 'Turn 3: the list keeps growing. Long chats cost more and can drift.'}]},
}

DG = {
    'map': {'t': 'Where each kind of instruction lives', 'w': 900, 'h': 330,
            'n': [['you', 20, 135, 120, 60, 'You', {'c': 5, 'sh': 'pill'}],
                  ['p', 190, 20, 170, 56, 'prompt', {'c': 2, 'sub': 'this message', 'i': 'Used once. Best for the task in front of you.'}],
                  ['cm', 190, 95, 170, 56, 'CLAUDE.md', {'c': 0, 'sub': 'every session', 'i': 'Loaded at the start of every Claude Code session in this folder.'}],
                  ['ru', 190, 170, 170, 56, '.claude/rules/', {'c': 0, 'sub': 'for matching files', 'i': 'Rules can load only when Claude touches certain files.'}],
                  ['sk', 190, 245, 170, 56, 'SKILL.md', {'c': 3, 'sub': 'when the task matches', 'i': 'Only the description is loaded until the skill is needed.'}],
                  ['cl', 430, 135, 150, 60, 'Claude', {'c': 1, 'sh': 'pill'}],
                  ['ag', 650, 30, 220, 56, '.claude/agents/', {'c': 3, 'sub': 'helpers with their own context', 'i': 'A subagent works in a fresh context and returns only a summary.'}],
                  ['hk', 650, 135, 220, 56, 'settings.json hooks', {'c': 4, 'sub': 'rules that are enforced', 'i': 'Scripts that run on events and can block an action.'}],
                  ['mc', 650, 240, 220, 56, '.mcp.json', {'c': 2, 'sub': 'outside tools and data', 'i': 'MCP servers connect Claude to apps such as GitHub, a database or a browser.'}]],
            'e': [['you', 'p'], ['you', 'cm'], ['you', 'ru'], ['you', 'sk'], ['p', 'cl'], ['cm', 'cl'], ['ru', 'cl'], ['sk', 'cl'], ['cl', 'ag'], ['cl', 'hk'], ['cl', 'mc']],
            'st': [[['you', 'p', 'you>p', 'p>cl', 'cl'], 'A prompt is the simplest way in. It lasts for one request.'],
                   [['cm', 'ru', 'you>cm', 'you>ru', 'cm>cl', 'ru>cl'], 'Files you write once are loaded for you, every session or when matching files are touched.'],
                   [['sk', 'you>sk', 'sk>cl'], 'Skills wait until a task needs them.'],
                   [['ag', 'hk', 'mc', 'cl>ag', 'cl>hk', 'cl>mc'], 'Claude can hand work to helpers, is checked by hooks, and reaches outside tools through MCP.']]},
}

INFO = {'title': 'Meet Claude', 'panels': [
    panel([['e', '👋'], ['t', 'Hi! What do you need?', {'b': 1}]], 'A helper that reads and writes', 'Claude answers in plain language.', 'It knows a lot in general and nothing about your work until you tell it.'),
    panel([['e', '🔢'], ['t', '1 word ≈ 1.8 tokens', {'b': 1}]], 'Tokens', 'Text is read in small pieces.', 'Size and price are counted in tokens.'),
    panel([['e', '🔁'], ['t', 'whole chat sent again', {'b': 1}]], 'No hidden memory', 'Each turn re-reads the whole chat.', 'Put lasting facts where they load every time.'),
    panel([['e', '🗂️'], ['t', 'instructions + knowledge', {'b': 1}]], 'Projects and Skills', 'Projects hold your context. Skills hold a task.', 'Write them once, use them every day.')],
    'remember': 'Claude knows the world but not your work. Tell it once, in the right place.'}

REAL = [
    ['🧁', 'A home baker', 'Pastes the Sunday WhatsApp orders and gets a baking list and a pickup timetable in one minute.'],
    ['🏫', 'A school office', 'Keeps a Project with the school calendar and fee rules, so every parent reply uses the right dates.'],
    ['💼', 'A sales manager', 'Uses Haiku to sort 2,000 enquiries a day into hot, warm and cold leads for a few cents.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter introduces Claude, the four models, tokens, the context window, claude.ai Projects and Skills.',
        'यह अध्याय Claude, चार models, tokens, context window, claude.ai Projects और Skills से परिचय कराता है।',
        'ಈ ಅಧ್ಯಾಯ Claude, ನಾಲ್ಕು models, tokens, context window, claude.ai Projects ಮತ್ತು Skills ಪರಿಚಯಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ Claude, ଚାରୋଟି models, tokens, context window, claude.ai Projects ଓ Skills ସହ ପରିଚୟ କରାଏ।',
        'يعرّفك هذا الفصل على Claude والنماذج الأربعة والرموز ونافذة السياق والمشاريع والمهارات في claude.ai.',
        'Dieses Kapitel stellt Claude vor, die vier Modelle, Tokens, das Kontextfenster sowie Projekte und Skills in claude.ai.'),
    say('what', 'What Claude is', 'Claude is an AI model you talk to in plain language. Use claude.ai to chat, Claude Code to work in your files, and the API to build it into your own app.',
        'Claude एक AI model है जिससे आप सामान्य भाषा में बात करते हैं। Chat के लिए claude.ai, files में काम के लिए Claude Code, और अपने app के लिए API.',
        'Claude ಸಾಮಾನ್ಯ ಭಾಷೆಯಲ್ಲಿ ಮಾತನಾಡುವ AI model. Chat ಗೆ claude.ai, files ನಲ್ಲಿ ಕೆಲಸಕ್ಕೆ Claude Code, ನಿಮ್ಮ app ಗೆ API.',
        'Claude ଏକ AI model ଯାହା ସହ ସାଧାରଣ ଭାଷାରେ କଥା ହୁଏ। Chat ପାଇଁ claude.ai, files ପାଇଁ Claude Code, app ପାଇଁ API.',
        'Claude نموذج ذكاء اصطناعي تتحدث معه بلغة عادية. استخدم claude.ai للمحادثة وClaude Code للعمل على ملفاتك والواجهة البرمجية لتطبيقك.',
        'Claude ist ein KI-Modell, mit dem du in normaler Sprache sprichst. claude.ai zum Chatten, Claude Code für deine Dateien, die API für eigene Apps.'),
    say('models', 'The models', 'Fable is the most capable, Opus is the usual default, Sonnet is fast for everyday work, and Haiku is the cheapest for simple jobs. All read one million tokens.',
        'Fable सबसे सक्षम है, Opus सामान्य default है, Sonnet रोज़ के काम के लिए तेज़ है, Haiku सरल कामों के लिए सबसे सस्ता है।',
        'Fable ಅತ್ಯಂತ ಸಮರ್ಥ, Opus ಸಾಮಾನ್ಯ default, Sonnet ದಿನನಿತ್ಯದ ಕೆಲಸಕ್ಕೆ ವೇಗ, Haiku ಸರಳ ಕೆಲಸಕ್ಕೆ ಅಗ್ಗ.',
        'Fable ସବୁଠୁ ସକ୍ଷମ, Opus ସାଧାରଣ default, Sonnet ଦୈନନ୍ଦିନ କାମ ପାଇଁ ଦ୍ରୁତ, Haiku ସରଳ କାମ ପାଇଁ ଶସ୍ତା।',
        'Fable الأقوى وOpus الخيار المعتاد وSonnet سريع للعمل اليومي وHaiku الأرخص للمهام البسيطة. كلها تقرأ مليون رمز.',
        'Fable ist am stärksten, Opus der übliche Standard, Sonnet schnell für den Alltag und Haiku am günstigsten für einfache Aufgaben.'),
    say('tokens', 'Tokens', 'Claude reads text in small pieces called tokens. One English word is about 1.8 tokens. Output tokens cost five times more than input tokens.',
        'Claude text को tokens नाम के छोटे टुकड़ों में पढ़ता है। एक English शब्द लगभग 1.8 tokens होता है। Output tokens पांच गुना महंगे हैं।',
        'Claude text ಅನ್ನು tokens ಎಂಬ ಸಣ್ಣ ತುಂಡುಗಳಲ್ಲಿ ಓದುತ್ತದೆ. ಒಂದು English ಪದ ಸುಮಾರು 1.8 tokens. Output tokens ಐದು ಪಟ್ಟು ದುಬಾರಿ.',
        'Claude text କୁ tokens ନାମକ ଛୋଟ ଖଣ୍ଡରେ ପଢେ। ଗୋଟିଏ English ଶବ୍ଦ ପ୍ରାୟ 1.8 tokens. Output tokens ପାଞ୍ଚ ଗୁଣ ମହଙ୍ଗା।',
        'يقرأ Claude النص في قطع صغيرة تسمى الرموز. الكلمة الإنجليزية نحو 1.8 رمز. رموز الإخراج أغلى بخمس مرات.',
        'Claude liest Text in kleinen Stücken, den Tokens. Ein englisches Wort sind etwa 1,8 Tokens. Ausgabe-Tokens kosten fünfmal so viel.'),
    say('turns', 'Conversations', 'Every time you send a message, the whole chat is sent again. Start a new chat for a new task, and keep lasting facts in instructions.',
        'हर बार message भेजने पर पूरी chat फिर से भेजी जाती है। नए काम के लिए नई chat शुरू करें।',
        'ಪ್ರತಿ message ಕಳುಹಿಸಿದಾಗ ಸಂಪೂರ್ಣ chat ಮತ್ತೆ ಕಳುಹಿಸಲಾಗುತ್ತದೆ. ಹೊಸ ಕೆಲಸಕ್ಕೆ ಹೊಸ chat ಆರಂಭಿಸಿ.',
        'ପ୍ରତି ଥର message ପଠାଇଲେ ସମ୍ପୂର୍ଣ୍ଣ chat ପୁଣି ପଠାଯାଏ। ନୂଆ କାମ ପାଇଁ ନୂଆ chat ଆରମ୍ଭ କରନ୍ତୁ।',
        'كل مرة ترسل رسالة تُرسل المحادثة كاملة من جديد. ابدأ محادثة جديدة لكل مهمة جديدة.',
        'Bei jeder Nachricht wird der ganze Chat erneut gesendet. Beginne für eine neue Aufgabe einen neuen Chat.'),
    say('first', 'First prompt', 'A good prompt says who you are, what you have, what you want and the shape of the answer. Numbered steps and tags help a lot.',
        'अच्छा prompt बताता है आप कौन हैं, क्या है, क्या चाहिए और जवाब का रूप क्या हो।',
        'ಒಳ್ಳೆಯ prompt ನೀವು ಯಾರು, ಏನಿದೆ, ಏನು ಬೇಕು ಮತ್ತು ಉತ್ತರದ ರೂಪ ಹೇಳುತ್ತದೆ.',
        'ଭଲ prompt କହେ ଆପଣ କିଏ, କଣ ଅଛି, କଣ ଦରକାର ଓ ଉତ୍ତରର ରୂପ।',
        'الموجّه الجيد يذكر من أنت وما لديك وما تريد وشكل الإجابة.',
        'Ein guter Prompt sagt, wer du bist, was du hast, was du willst und wie die Antwort aussehen soll.'),
    say('projects', 'Projects', 'A claude.ai Project has instructions for how Claude behaves and knowledge files it can look things up in.',
        'claude.ai Project में instructions होते हैं कि Claude कैसे काम करे, और knowledge files जिनमें वह जानकारी देखता है।',
        'claude.ai Project ನಲ್ಲಿ Claude ಹೇಗೆ ವರ್ತಿಸಬೇಕು ಎಂಬ instructions ಮತ್ತು knowledge files ಇರುತ್ತವೆ.',
        'claude.ai Project ରେ Claude କିପରି କାମ କରିବ ତାହାର instructions ଓ knowledge files ଥାଏ।',
        'مشروع claude.ai فيه تعليمات لسلوك Claude وملفات معرفة يبحث فيها.',
        'Ein Projekt in claude.ai hat Anweisungen für Claudes Verhalten und Wissensdateien zum Nachschlagen.'),
    say('skills-intro', 'Skills', 'A skill is a folder with a SKILL.md file. Claude reads only its description until a task needs it. Upload it as a ZIP in claude.ai.',
        'Skill एक folder है जिसमें SKILL.md file होती है। ज़रूरत तक Claude सिर्फ उसका description पढ़ता है।',
        'Skill ಎಂದರೆ SKILL.md file ಇರುವ folder. ಅಗತ್ಯವಾಗುವವರೆಗೆ Claude ಅದರ description ಮಾತ್ರ ಓದುತ್ತದೆ.',
        'Skill ହେଉଛି SKILL.md file ଥିବା folder. ଦରକାର ନହେବା ଯାଏ Claude କେବଳ description ପଢେ।',
        'المهارة مجلد فيه ملف SKILL.md. يقرأ Claude وصفها فقط حتى تحتاجها مهمة.',
        'Ein Skill ist ein Ordner mit einer SKILL.md. Claude liest nur die Beschreibung, bis eine Aufgabe ihn braucht.'),
    say('map', 'The map', 'Prompts are for now, CLAUDE.md for every session, rules for some files, skills for repeat tasks, hooks to enforce, agents to delegate and MCP to reach outside tools.',
        'Prompt अभी के लिए, CLAUDE.md हर session के लिए, rules कुछ files के लिए, skills दोहराए कामों के लिए, hooks लागू करने, agents सौंपने और MCP बाहरी tools के लिए।',
        'Prompt ಈಗಿನದಕ್ಕೆ, CLAUDE.md ಪ್ರತಿ session ಗೆ, rules ಕೆಲವು files ಗೆ, skills ಪುನರಾವರ್ತಿತ ಕೆಲಸಕ್ಕೆ, hooks, agents ಮತ್ತು MCP.',
        'Prompt ଏବେ ପାଇଁ, CLAUDE.md ପ୍ରତି session ପାଇଁ, rules କିଛି files ପାଇଁ, skills ପୁନରାବୃତ୍ତ କାମ ପାଇଁ, hooks, agents ଓ MCP.',
        'الموجّه للآن وCLAUDE.md لكل جلسة والقواعد لبعض الملفات والمهارات للمهام المتكررة والخطافات للفرض والوكلاء للتفويض وMCP للأدوات الخارجية.',
        'Prompts für jetzt, CLAUDE.md für jede Sitzung, Regeln für bestimmte Dateien, Skills für Wiederholtes, Hooks zum Erzwingen, Agenten zum Delegieren und MCP für externe Tools.'),
    say('habits', 'Safe habits', 'Check important facts, never paste passwords or keys, read before you approve, and send messages yourself.',
        'ज़रूरी तथ्य जांचें, password या keys कभी paste न करें, approve से पहले पढ़ें।',
        'ಮುಖ್ಯ ಸತ್ಯಗಳನ್ನು ಪರಿಶೀಲಿಸಿ, password ಅಥವಾ keys paste ಮಾಡಬೇಡಿ, approve ಮಾಡುವ ಮೊದಲು ಓದಿ.',
        'ଜରୁରୀ ତଥ୍ୟ ଯାଞ୍ଚ କରନ୍ତୁ, password ବା keys paste କରନ୍ତୁ ନାହିଁ, approve ପୂର୍ବରୁ ପଢନ୍ତୁ।',
        'تحقق من الحقائق المهمة ولا تلصق كلمات المرور أو المفاتيح واقرأ قبل الموافقة.',
        'Prüfe wichtige Fakten, füge nie Passwörter oder Schlüssel ein und lies, bevor du zustimmst.'),
    say('practice', 'Practice', 'Practise counting tokens, working out costs and choosing the right model for a job.',
        'Tokens गिनने, लागत निकालने और सही model चुनने का अभ्यास करें।',
        'Tokens ಎಣಿಸುವ, ವೆಚ್ಚ ಲೆಕ್ಕಿಸುವ ಮತ್ತು ಸರಿಯಾದ model ಆಯ್ಕೆಯ ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Tokens ଗଣିବା, ଖର୍ଚ୍ଚ ହିସାବ ଓ ଠିକ୍ model ବାଛିବାର ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرّب على عد الرموز وحساب التكلفة واختيار النموذج المناسب.',
        'Übe Tokens zählen, Kosten berechnen und das passende Modell wählen.'),
]

QUIZ = [
    quiz('e', 'You want Claude to edit files in a folder on your laptop. Which product fits?', ['Claude Code', 'claude.ai chat only', 'The Claude API with no code', 'A Project'], 0, 'It works inside a folder.', 'Claude Code reads, edits and runs things in your project folder.'),
    quiz('e', 'What is a token?', ['A small piece of text Claude reads', 'A password', 'A whole page', 'A paid credit'], 0, 'Smaller than a word, often.', 'Size and price are both counted in tokens.'),
    quiz('e', 'Where do you put rules for every chat in a claude.ai Project?', ['Project instructions', 'Project knowledge', 'The first chat only', 'The chat title'], 0, 'Behaviour versus facts.', 'Instructions shape every chat. Knowledge is for files to look things up in.'),
    quiz('m', 'Why does a very long chat cost more per message?', ['The whole chat is sent again every turn', 'Claude charges by the minute', 'Old messages are deleted', 'Images get bigger'], 0, 'No hidden memory.', 'Each new message makes Claude re-read everything before it.'),
    quiz('m', 'Which model would you choose to sort 10,000 short emails cheaply?', ['claude-haiku-5-5', 'claude-fable-5-1', 'claude-opus-5-5', 'It does not matter'], 0, 'High volume, simple job.', 'Haiku is the fastest and cheapest model and is good at simple sorting.'),
    quiz('m', 'What does Claude read from a skill before it is needed?', ['Only its name and description', 'Every file in the folder', 'Nothing at all', 'Only the scripts'], 0, 'Kept small on purpose.', 'This is called progressive disclosure. The full SKILL.md is read when a task matches.'),
    quiz('h', 'Output tokens on Opus 5.5 cost how many times the input price?', ['5 times', '2 times', 'The same', '10 times'], 0, '$4 in and $20 out.', '<span class="eq">20 ÷ 4 = 5</span>'),
    quiz('h', 'Which is the safest place for an API key?', ['An environment variable', 'CLAUDE.md', 'Project instructions', 'The first message of a chat'], 0, 'Not in text Claude reads.', 'Keys in files or chats can leak. Environment variables keep them out of shared text.'),
    quiz('x', 'A Project has 300 long PDFs on a paid plan. What does Claude do?', ['Searches the knowledge and pulls in the relevant parts', 'Refuses to answer', 'Reads only the first file', 'Deletes old files'], 0, 'Large knowledge.', 'When knowledge is large, paid plans search it instead of loading all of it.'),
    quiz('x', 'Your team wants the same invoice checking steps in claude.ai and Claude Code. What should you build?', ['One skill folder with SKILL.md', 'Two separate prompts', 'A Project per person', 'A long CLAUDE.md only'], 0, 'One format, many places.', 'The SKILL.md format works across claude.ai, Claude Code and the API.'),
]

CALC = [
    calc('e', 'About how many tokens is a 100 word email? Use 1.8 tokens per word.', '180', 'Multiply.', ['<span class="eq">100 × 1.8 = 180</span>']),
    calc('e', 'Opus 5.5 costs $4 per million input tokens. What do 500,000 input tokens cost in dollars?', '2', 'Half a million.', ['<span class="eq">0.5 × 4 = 2</span>']),
    calc('m', 'A job sends 80,000 input and 24,000 output tokens to Sonnet 5.5 ($2 in, $10 out per million). Cost in dollars?', '0.4', 'Work out each part.', ['<span class="eq">80,000 × 2 ÷ 1,000,000 = 0.16</span>', '<span class="eq">24,000 × 10 ÷ 1,000,000 = 0.24</span>', '<span class="eq">0.16 + 0.24 = 0.40</span>'], alt=['0.40', '$0.40', '$0.4']),
    calc('m', 'A chat has 3 turns. Turn 1 sends 100 words, turn 2 sends 250, turn 3 sends 420. How many words did Claude read in total?', '770', 'Add them.', ['<span class="eq">100 + 250 + 420 = 770</span>']),
    calc('h', 'How many 90,000 word novels fit in 1,000,000 tokens at 1.8 tokens per word? Whole novels only.', '6', 'Tokens per novel first.', ['<span class="eq">90,000 × 1.8 = 162,000</span>', '<span class="eq">1,000,000 ÷ 162,000 ≈ 6.17</span>', 'So 6 whole novels.']),
    calc('x', 'Sorting 2,000 emails a day on Haiku 5.5 uses 400 input and 20 output tokens each, at $0.10 and $0.50 per million. Cost per day in dollars?', '0.1', 'Total tokens first.', ['<span class="eq">2,000 × 400 = 800,000 input</span>', '<span class="eq">2,000 × 20 = 40,000 output</span>', '<span class="eq">0.8 × 0.10 + 0.04 × 0.50 = 0.08 + 0.02 = 0.10</span>'], alt=['0.10', '$0.10', '$0.1']),
]

EX = []

T = {
    'slug': 'claude-meet', 'title': 'Meet Claude: Models, Tokens, Projects and Skills', 'short': 'Meet Claude', 'emoji': '👋', 'module': MODULE, 'minutes': 14,
    'lead': 'What Claude is, where you can use it, the four current models and what they cost, tokens and the context window, how a chat really works, and how claude.ai Projects and Skills save you from repeating yourself.',
    'plain': 'Claude is a helper you talk to in normal words. It is clever but new to your work, so you tell it about your work once, in the right place, and it reads that place every time.',
    'desc': 'Claude models, tokens, context window, pricing, claude.ai Projects, project instructions, project knowledge and uploading Skills.',
    'summary': 'The Claude products (claude.ai, Claude Code, the API), the four models with their API names and prices, tokens and the 1M token context window, why every turn re-sends the chat, a first practical prompt, claude.ai Projects with instructions and knowledge, Skills uploaded as a ZIP, and a map of every file this subject teaches.',
    'keywords': ['Claude', 'models', 'Opus', 'Sonnet', 'Haiku', 'Fable', 'tokens', 'context window', 'pricing', 'Projects', 'project instructions', 'Skills', 'claude.ai'],
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
