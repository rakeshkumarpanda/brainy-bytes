# Chapter 15: Claude 101 from Anthropic Academy, lesson by lesson, and preparing for the Claude Certified Associate exam.
# Facts come from the official Claude 101 course page (anthropic.skilljar.com/claude-101), the Claude Help Center
# articles on projects, artifacts, skills, memory, connectors, enterprise search, research and Cowork, and the
# Claude Certified Associate Foundations exam guide (version 1.0, July 2026). All were read in October 2026.
from ckit import part, prompt, md, say, quiz, calc, panel

MODULE = ('🎓', 'Certification prep', 'claude-cert', 'Claude 101 from Anthropic Academy lesson by lesson, and how to prepare for the Claude Certified Associate exam.')

DOMAINS = [
    ('Output evaluation and validation', 21),
    ('Workflow integration and solution design', 16),
    ('Governance, risk and responsible use', 15),
    ('Prompting and task execution', 14),
    ('Product and model selection', 12),
    ('Configuration and knowledge management', 12),
    ('Troubleshooting and optimisation', 10),
]
BARS = '<div class="cl-bars">' + ''.join(
    f'<div class="cl-bar" style="--w:{w / 21 * 100:.0f}%"><span>{name}</span><i></i><b>{w}%</b></div>' for name, w in DOMAINS) + '</div>'

CODES = {
    'vague-specific': prompt('''
Vague:     Write something about our new product.

Specific:  You are writing for busy shop owners in India who sell on WhatsApp.
           Write a 120 word announcement for our new billing app, "QuickBill".
           Mention three things: GST invoices in one tap, works offline, Rs 199 a month.
           Tone: friendly and plain. End with one line telling them how to try it free for 14 days.
''', 'The same request, vague and specific', result='The vague prompt gets a generic paragraph. The specific one says who it is for, what to include, how long, what tone and how to end, so the first draft is close to usable.'),
    'project-instr': md('''
# Project instructions: "Claude 101 study buddy"

You are my study partner for the Claude 101 course and the Claude Certified Associate exam.

- Explain each idea in plain words first, then give one real work example.
- When I say "quiz me", ask 5 multiple choice questions, one at a time.
  Wait for my answer before you show whether it was right and why.
- If you are not sure a fact is current, say so and tell me which Help Center page to check.
- Keep answers under 200 words unless I ask for more.
''', 'Project instructions for your own study project'),
    'research-prompt': prompt('''
Research how small clinics in India are using AI for appointment reminders.
I need: 5 real examples with sources, what each one costs if stated,
and the main privacy rules they had to follow. Put the sources at the end.
''', 'A good Research request', result='With Research on, Claude runs several searches that build on each other, reads the pages, and writes a cited answer. It takes longer than a normal reply and uses more of your plan.'),
}

PARTS = [
    part('about', '🎓', 'What Claude 101 is and how you earn the certificate', '''
<p><b>Claude 101</b> is a free online course from <b>Anthropic Academy</b>, hosted on Skilljar. Its own description says it teaches you to "use Claude for everyday work tasks, understand core features, and explore resources for more advanced learning". No coding is needed.</p>
<div class="tw"><table class="jt"><tr><th>Module</th><th>Lessons in the official outline</th><th>Covered on this page in</th></tr>
<tr><td>1. Meet Claude</td><td>What is Claude? · Your first conversation with Claude · Getting better results · How you'll work with Claude on your desktop</td><td>Part 2 and Part 3</td></tr>
<tr><td>2. Organizing your work and knowledge</td><td>Introduction to projects · Creating with artifacts · Working with skills</td><td>Part 4</td></tr>
<tr><td>3. Expanding Claude's reach</td><td>Connecting your tools · Enterprise search · Research for deep dives</td><td>Part 5</td></tr>
<tr><td>4. Putting it all together</td><td>Claude in action: use-cases by role · Other ways to work with Claude</td><td>Part 6 and Part 7</td></tr>
<tr><td>5. Conclusion and certificate</td><td>What's next? · Certificate of completion</td><td>this part</td></tr></table></div>
<p><b>How to earn the certificate, step by step:</b></p>
<ol class="steps"><li>Open <code>anthropic.skilljar.com/claude-101</code> and click <b>Register</b>. You need a free Skilljar account, not a paid Claude plan.</li>
<li>Work through the 14 lessons in order. Try each feature in Claude as you read about it. That is how it sticks.</li>
<li>Reach the last lesson, <b>Certificate of completion</b>, and save your certificate.</li></ol>
<div class="viz" data-viz="flow" data-k="path"></div>
<div class="cl-name">Two different things share the word "certificate". The <b>Claude 101 certificate of completion</b> is free and you get it by finishing the course. The official course page lists no exam for it. The <b>Claude Certified Associate (Foundations)</b> is a separate paid exam with a pass mark, taken with a proctor. Part 9 covers it. This page prepares you for both.</div>
''', easy=True, files=['anthropic.skilljar.com/claude-101'], kw=['Claude 101', 'Anthropic Academy', 'Skilljar', 'certificate of completion', 'course outline', 'free course']),
    part('meet', '👋', 'Module 1: Meet Claude and get better results', '''
<p><b>What Claude is.</b> Claude is a large language model. It has read a huge amount of text and writes answers by predicting what text should come next. Two facts follow:</p>
<ul><li>It has a <b>knowledge cutoff</b>. It does not know about events after its training unless you give it the facts or turn on web search.</li>
<li>It can be <b>wrong and sound sure</b>. Check names, numbers, dates and quotes before you use them.</li></ul>
<p><b>Your first conversation.</b> Type a request, attach files if they help, and read the answer. If the answer is close but not right, <b>reply with feedback</b> such as "shorter, and add the price". Claude revises the draft instead of starting from zero.</p>
<p><b>Getting better results.</b> The biggest single tip is to be <b>specific</b>: who it is for, what to include, how long, what tone, and what the result should look like.</p>
[[vague-specific]]
<div class="tw"><table class="jt"><tr><th>Add this</th><th>Example</th></tr>
<tr><td>Who it is for</td><td>"for busy shop owners who sell on WhatsApp"</td></tr>
<tr><td>The task</td><td>"write a 120 word announcement"</td></tr>
<tr><td>Context and facts</td><td>"three features: GST invoices, offline, Rs 199 a month"</td></tr>
<tr><td>Format and tone</td><td>"friendly and plain, end with one call to action"</td></tr>
<tr><td>An example, if you have one</td><td>"here is last month's announcement we liked"</td></tr></table></div>
<div class="tip">Chapter 2 of this subject goes much deeper into prompting: examples, XML tags, step by step thinking and prompt chains.</div>
''', easy=True, kw=['what is Claude', 'large language model', 'knowledge cutoff', 'first conversation', 'better results', 'specific prompts', 'feedback']),
    part('desktop', '🖥️', 'Module 1: Chat, Cowork and Code on your desktop', '''
<p>The Claude Desktop app has three ways to work. They share one home screen and message box.</p>
<div class="tw"><table class="jt"><tr><th>Mode</th><th>Best for</th><th>Example</th></tr>
<tr><td><b>Chat</b></td><td>back and forth questions, drafts, ideas</td><td>"Rewrite this email to sound warmer."</td></tr>
<tr><td><b>Cowork</b></td><td>longer tasks with many steps, on your files</td><td>"Sort the 40 PDFs in my Invoices folder by month and make a summary sheet."</td></tr>
<tr><td><b>Code</b></td><td>software work: reading, changing and testing code</td><td>"Fix the failing login test."</td></tr></table></div>
<p><b>Cowork</b> uses the same agent design as Claude Code, without a terminal. You describe the task, review Claude's plan, then let it run. Facts worth knowing:</p>
<ul><li>It needs a paid plan: Pro, Max, Team or Enterprise.</li>
<li>Claude can open local files only in folders you connect, and it must ask you before deleting any file for good.</li>
<li>It has permission modes: <b>Manual</b> asks before actions, <b>Auto</b> checks each action for safety first, and <b>Skip</b> runs without checks. Use Skip only for tasks you fully trust.</li>
<li>Cowork uses more of your plan's usage than chat. Use chat for simple tasks and check <b>Settings</b>, then <b>Usage</b>.</li></ul>
<div class="scenario"><b>🏫 Real scenario: a school office</b>Every term the office gets 300 fee receipts as PDFs. In Chat, the clerk asks how to name files. In Cowork, she connects the Receipts folder and asks Claude to rename every file as class, roll number and date, then list any receipt with a missing amount. She reviews the plan, presses go, and checks the list at the end.</div>
''', easy=True, kw=['Claude Desktop', 'Chat', 'Cowork', 'Code', 'permission modes', 'usage limits']),
    part('organise', '🗂️', 'Module 2: Projects, artifacts and skills', '''
<div class="tw"><table class="jt"><tr><th>Feature</th><th>What it is</th><th>Use it when</th></tr>
<tr><td><b>Project</b></td><td>a workspace with its own chats, <b>instructions</b> and <b>knowledge</b> files</td><td>you keep coming back to one topic and do not want to repeat the background</td></tr>
<tr><td><b>Artifact</b></td><td>a standalone piece of work Claude makes: a document, slides, a design, a dashboard or a small tool</td><td>the result is something you would show someone or keep editing</td></tr>
<tr><td><b>Skill</b></td><td>a folder of instructions Claude loads only when a task needs it</td><td>a task has steps that should be done the same way every time</td></tr></table></div>
<p><b>Projects, the facts to remember</b></p>
<ul><li>Every plan can use projects. Free accounts can make up to <b>five</b>.</li>
<li>Instructions say how Claude should behave in every chat of the project. Knowledge holds the files it can look things up in.</li>
<li>On paid plans, when the knowledge grows near the context limit, Claude switches to <b>RAG</b> by itself and can hold up to <b>10 times</b> more content. It then searches the files and reads only the relevant parts.</li>
<li>On Team and Enterprise plans you can share a project with <b>Can view</b> or <b>Can edit</b> access.</li></ul>
[[project-instr]]
<p><b>Artifacts, the facts to remember</b></p>
<ul><li>Claude makes an artifact when the content is substantial and stands on its own, usually more than 15 lines, and you are likely to edit or reuse it.</li>
<li>Your artifacts are saved in the <b>Artifacts</b> tab of the sidebar. They <b>start private</b> to you until you share them.</li>
<li>Docs export to Word, PDF, Markdown or Google Docs. Decks export to PowerPoint, PDF or Google Slides.</li>
<li>An artifact can call Claude itself and work like a small app. No API key is needed, and each person who uses it spends their own plan's usage.</li></ul>
<p><b>Skills, the facts to remember</b></p>
<ul><li>Anthropic's built in skills for Excel, Word, PowerPoint and PDF files are there for every user, and Claude uses them by itself.</li>
<li>Skills need <b>code execution</b> turned on: <b>Settings</b>, then <b>Capabilities</b>, then <b>Code execution and file creation</b>.</li>
<li>Upload your own skill as a ZIP under <b>Customize</b>, then <b>Skills</b>. Chapter 7 has a screenshot for each step.</li></ul>
''', easy=True, files=['Project instructions', 'Project knowledge', 'Artifacts tab', 'SKILL.md'], kw=['projects', 'project knowledge', 'RAG', 'artifacts', 'skills', 'share project', 'Can view', 'Can edit']),
    part('memory', '🧠', 'Memory, past chats and incognito', '''
<p>Claude can remember things across chats, and you stay in control of it.</p>
<div class="tw"><table class="jt"><tr><th>Feature</th><th>What it does</th><th>Where you control it</th></tr>
<tr><td>Memory from chats</td><td>saves useful facts as topics while you chat</td><td><b>Settings</b>, then <b>Memory</b>, then <b>Generate memory from chats</b>. Read or delete topics there too.</td></tr>
<tr><td>Search past chats</td><td>lets Claude look up earlier conversations (paid plans)</td><td>the <b>Search and reference chats</b> toggle</td></tr>
<tr><td>Project memory</td><td>each project keeps its own memory, separate from other projects</td><td>turn off <b>Use account memory</b> on a project to keep it fully separate</td></tr>
<tr><td>Incognito chat</td><td>not saved to history or memory</td><td>the ghost icon at the top of a new chat</td></tr></table></div>
<p>You can also just say "remember that our financial year starts in April" or "forget my old address".</p>
<div class="warn">On Team and Enterprise plans, an owner decides whether memory is available. Memory is not available for organisations with HIPAA, public sector or custom data retention agreements.</div>
''', easy=True, kw=['memory', 'chat search', 'incognito', 'project memory', 'privacy']),
    part('reach', '🔌', 'Module 3: Connectors, enterprise search and Research', '''
<p><b>Connectors</b> let Claude read from and act in the apps you already use, such as Google Drive, Gmail, Slack or your own tools. They are built on MCP, the same standard Chapter 10 teaches.</p>
<ul><li>Claude gets <b>your permissions</b>. If you cannot open a file in the source app, Claude cannot either.</li>
<li>Turn connectors on for a chat with the <b>+</b> button, then <b>Connectors</b>. Add new ones under <b>Customize</b>, then <b>Connectors</b>.</li>
<li>On Team and Enterprise plans an owner enables each connector first, and can set each tool to <b>Always allow</b>, <b>Needs approval</b> or <b>Blocked</b>.</li></ul>
<p><b>Enterprise search</b> (Team and Enterprise) is a ready made project, shown as "Ask" plus your organisation's name, that searches across company tools in one place. An owner sets it up once. Results respect each person's permissions, and Anthropic does not index the data from those tools to answer queries.</p>
<p><b>Research</b> (paid plans) is for questions that need many sources. Claude runs several searches that build on each other, reads them, and writes an answer. Turn on web search, then click <b>+</b> and choose <b>Research</b>.</p>
[[research-prompt]]
<div class="tw"><table class="jt"><tr><th>You need...</th><th>Use</th></tr>
<tr><td>facts from your own Drive or email</td><td>a connector</td></tr>
<tr><td>one answer from all company tools at once</td><td>enterprise search</td></tr>
<tr><td>a deep, cited answer from the web</td><td>Research</td></tr></table></div>
''', easy=True, kw=['connectors', 'enterprise search', 'Ask your org', 'Research', 'web search', 'permissions', 'MCP']),
    part('roles', '🧑‍💼', 'Module 4: Claude in action, role by role', '''
<p>The course shows how different teams use the same features. These examples follow the same idea.</p>
<div class="tw"><table class="jt"><tr><th>Role</th><th>A daily job</th><th>Features</th></tr>
<tr><td>Marketing</td><td>a month of social posts in the brand voice</td><td>project with the brand guide as knowledge, a brand voice skill</td></tr>
<tr><td>Sales</td><td>prepare for a call with a new customer</td><td>Research on the company, CRM connector for past deals</td></tr>
<tr><td>HR</td><td>answer staff questions about leave policy</td><td>project with the policy files, instructions to quote the policy line</td></tr>
<tr><td>Finance</td><td>check 40 supplier invoices</td><td>Cowork on the invoice folder, an invoice skill with a script</td></tr>
<tr><td>Engineering</td><td>fix a bug and add a test</td><td>Claude Code</td></tr>
<tr><td>QA</td><td>test cases from a user story</td><td>a test-cases skill, see Chapter 7</td></tr>
<tr><td>Operations</td><td>a weekly status report from many tools</td><td>connectors plus a report artifact</td></tr></table></div>
''', easy=True, kw=['use cases by role', 'marketing', 'sales', 'HR', 'finance', 'engineering', 'operations']),
    part('other', '🧭', 'Module 4: Other ways to work with Claude', '''
<div class="tw"><table class="jt"><tr><th>Where</th><th>What it is for</th></tr>
<tr><td>claude.ai on the web</td><td>chat, projects, artifacts, research</td></tr>
<tr><td>Claude Desktop</td><td>Chat, Cowork and Code, plus local MCP servers</td></tr>
<tr><td>Claude mobile apps</td><td>chat on the go. Research on mobile searches only the web, not your connectors.</td></tr>
<tr><td>Claude Code</td><td>software work in the terminal, an editor, the desktop app or the web</td></tr>
<tr><td>The Claude API</td><td>Claude inside your own app. It is billed separately from Pro, Max, Team and Enterprise plans.</td></tr></table></div>
<p>The last module, <b>What's next?</b>, points to more Anthropic Academy courses. Chapters 4 to 13 of this subject cover the same ground step by step.</p>
<div class="viz" data-viz="flow" data-k="pick"></div>
''', easy=True, kw=['claude.ai', 'Claude Desktop', 'mobile', 'Claude Code', 'API', 'billing', 'which feature']),
    part('exam', '📝', 'The Claude Certified Associate exam (CCAO-F)', '''
<p>If you want a credential with a pass mark, Anthropic has a proctored exam called <b>Claude Certified Associate, Foundations</b>, code <b>CCAO-F</b>. It is for people who use Claude as a work tool, such as operations, marketing, project management, teaching and communications. It is not aimed at developers who build on the API.</p>
<div class="tw"><table class="jt"><tr><th>Item</th><th>Detail from the exam guide (version 1.0, July 2026)</th></tr>
<tr><td>Questions</td><td>60, multiple choice and multiple response. Each question says how many answers to pick.</td></tr>
<tr><td>Time</td><td>120 minutes</td></tr>
<tr><td>Pass mark</td><td>a scaled score of 720 on a scale of 100 to 1,000</td></tr>
<tr><td>Fee</td><td>USD 99</td></tr>
<tr><td>Where</td><td>proctored through Pearson VUE, online or at a test centre</td></tr>
<tr><td>Valid for</td><td>12 months. On time renewal is a free assessment without a proctor.</td></tr>
<tr><td>Retakes</td><td>wait 14 days after the first fail, 30 after the second, 90 after the third. At most four tries in 12 months.</td></tr></table></div>
<p><b>The seven domains and their weight in the exam.</b> Watch the bars: the biggest one is about checking Claude's answers, not about writing prompts.</p>
''' + BARS + '''
<div class="warn">Third party guides say registration is open only to people at organisations in the Claude Partner Network, using a work email from that organisation. Rules can change, so read the certifications page on the Anthropic Partner Academy before you plan your date.</div>
''', kw=['Claude Certified Associate', 'CCAO-F', 'exam', 'Pearson VUE', 'domains', 'pass mark', '720']),
    part('domains', '🎯', 'What each exam domain tests, with one tip each', '''
<div class="tw"><table class="jt"><tr><th>Domain</th><th>What you must be able to do</th><th>Tip to remember</th></tr>
<tr><td>Output evaluation (21%)</td><td>spot mistakes, made up facts, contradictions and bias. Decide when a human must review.</td><td>A specific looking citation is still a claim. Check it against the source.</td></tr>
<tr><td>Workflow integration (16%)</td><td>see where Claude fits in a process, and explain what it can and cannot do</td><td>Start with one repeated task, not the whole department.</td></tr>
<tr><td>Governance and responsible use (15%)</td><td>follow data rules and company AI policy, know unsuitable uses</td><td>Remove or mask personal data before you upload when policy says so.</td></tr>
<tr><td>Prompting (14%)</td><td>write clear prompts, break big tasks into steps, improve a prompt</td><td>Who, task, context, format. Then give feedback.</td></tr>
<tr><td>Product and model selection (12%)</td><td>pick chat, a project, Research or an artifact, and pick Haiku, Sonnet or Opus</td><td>Simple and high volume: a fast, cheaper model. Hard reasoning: a bigger one.</td></tr>
<tr><td>Configuration (12%)</td><td>set up project instructions, knowledge and connectors, and keep them current</td><td>Instructions say how. Knowledge holds facts.</td></tr>
<tr><td>Troubleshooting (10%)</td><td>find why output is poor and fix the prompt or setup</td><td>Change one thing at a time and compare.</td></tr></table></div>
<p>Chapter 1 has the full model table. Chapters 2 and 3 cover prompting and context in depth.</p>
''', kw=['exam domains', 'output evaluation', 'hallucination', 'governance', 'model selection', 'Haiku', 'Sonnet', 'Opus']),
    part('scenarios', '🧩', 'Exam style scenarios, worked through', '''
<p>The exam asks what you would <b>do</b> in a work situation. Here is how to think through three typical ones.</p>
<div class="scenario"><b>📜 Scenario 1: a confident citation</b>Claude summarises a new tax rule and names "Section 12(4)(b)". You are about to send it to your manager. <b>Best move:</b> open the official text and check that section says what Claude claims, before you send. <b>Why:</b> models can produce details that look exact but are wrong. This is Domain 2.</div>
<div class="scenario"><b>📨 Scenario 2: 2,000 short replies a day</b>A support team needs short, simple reply drafts, fast and cheap. <b>Best move:</b> a smaller, faster model such as Haiku, with a clear template. <b>Why:</b> the task is simple and high volume, so speed and cost matter more than deep reasoning. This is Domain 3.</div>
<div class="scenario"><b>🔒 Scenario 3: a sheet with customer accounts</b>You want trends from a spreadsheet with customer names and account numbers, and policy forbids uploading that kind of personal data. <b>Best move:</b> remove or mask the names and account numbers first, then upload. <b>Why:</b> Claude needs the patterns, not the identities. This is Domain 6.</div>
<div class="tip">For every scenario ask yourself three things in order: is it safe and allowed, is the answer checked, and is this the simplest tool that does the job.</div>
''', easy=True, kw=['exam scenarios', 'fact checking', 'model choice', 'personal data', 'responsible use']),
    part('plan', '📅', 'A seven day study plan', '''
<div class="tw"><table class="jt"><tr><th>Day</th><th>Do this</th><th>Try it in Claude</th></tr>
<tr><td>1</td><td>Claude 101 Module 1. Chapters 1 and 2 here.</td><td>rewrite one vague prompt from your work into a specific one</td></tr>
<tr><td>2</td><td>Module 2. Make a study project with the instructions above.</td><td>add two files as knowledge and ask questions about them</td></tr>
<tr><td>3</td><td>Artifacts and skills. Chapter 7 here.</td><td>make one artifact and upload one skill</td></tr>
<tr><td>4</td><td>Module 3. Connectors, enterprise search, Research.</td><td>run one Research request and check three of its sources</td></tr>
<tr><td>5</td><td>Module 4 and 5. Earn the Claude 101 certificate.</td><td>write down three uses for your own role</td></tr>
<tr><td>6</td><td>Exam domains, scenarios and the quiz on this page.</td><td>ask your study project to "quiz me" on Domains 2 and 6</td></tr>
<tr><td>7</td><td>Read the official exam guide once. Review mistakes.</td><td>redo every quiz question you missed</td></tr></table></div>
<div class="fun">Ten minutes of trying a feature teaches more than an hour of reading about it. Keep Claude open in a second window while you study.</div>
''', easy=True, kw=['study plan', 'seven days', 'exam preparation', 'practice']),
    part('cheat', '📌', 'Cheat sheet: numbers and menu paths', '''
<div class="tw"><table class="jt"><tr><th>Remember</th><th>Value</th></tr>
<tr><td>Projects on the Free plan</td><td><span class="eq">5</span></td></tr>
<tr><td>Extra project capacity with RAG (paid)</td><td><span class="eq">up to 10 ×</span></td></tr>
<tr><td>Artifact usually made when content is over</td><td><span class="eq">15 lines</span></td></tr>
<tr><td>Custom connectors on the Free plan</td><td><span class="eq">1</span></td></tr>
<tr><td>Exam: questions, minutes, fee</td><td><span class="eq">60 · 120 · USD 99</span></td></tr>
<tr><td>Exam pass mark</td><td><span class="eq">720 / 1,000</span></td></tr>
<tr><td>Credential valid for</td><td><span class="eq">12 months</span></td></tr></table></div>
<div class="tw"><table class="jt"><tr><th>To do this</th><th>Go here</th></tr>
<tr><td>turn on code execution for skills</td><td>Settings › Capabilities</td></tr>
<tr><td>upload a skill</td><td>Customize › Skills › + › Create skill › Upload a skill</td></tr>
<tr><td>add a connector</td><td>Customize › Connectors</td></tr>
<tr><td>turn on a connector or Research in a chat</td><td>+ in the message box</td></tr>
<tr><td>see or edit memory</td><td>Settings › Memory</td></tr>
<tr><td>check usage</td><td>Settings › Usage</td></tr></table></div>
''', easy=True, kw=['cheat sheet', 'numbers to remember', 'menu paths', 'revision']),
]

DG = {
    'path': {'t': 'From sign up to certificate, and the optional exam', 'w': 900, 'h': 250,
             'n': [['reg', 20, 20, 130, 56, 'Register free', {'c': 5, 'sh': 'pill', 'i': 'A free Skilljar account at anthropic.skilljar.com.'}],
                   ['m1', 180, 20, 150, 56, 'Meet Claude', {'c': 0, 'sub': '4 lessons'}],
                   ['m2', 360, 20, 150, 56, 'Organise work', {'c': 1, 'sub': '3 lessons', 'i': 'Projects, artifacts, skills.'}],
                   ['m3', 540, 20, 150, 56, 'Expand reach', {'c': 2, 'sub': '3 lessons', 'i': 'Connectors, enterprise search, Research.'}],
                   ['m4', 720, 20, 160, 56, 'All together', {'c': 3, 'sub': '2 lessons', 'i': 'Use cases by role, other ways to work.'}],
                   ['m5', 720, 170, 160, 56, 'Conclusion', {'c': 4, 'sub': '2 lessons'}],
                   ['cert', 450, 170, 200, 56, 'Certificate of completion', {'c': 5, 'sh': 'doc', 'i': 'Free. Earned by finishing the course.'}],
                   ['exam', 130, 170, 220, 56, 'CCAO-F exam (optional)', {'c': 2, 'sub': 'proctored, paid', 'i': 'A separate exam with a pass mark of 720 out of 1,000.'}]],
             'e': [['reg', 'm1'], ['m1', 'm2'], ['m2', 'm3'], ['m3', 'm4'], ['m4', 'm5'], ['m5', 'cert'], ['cert', 'exam', {'t': 'next level'}]],
             'st': [[['reg'], 'Register for free. No paid plan and no coding needed.'],
                    [['m1', 'reg>m1'], 'Module 1: what Claude is, your first chat, better results, the desktop app.'],
                    [['m2', 'm1>m2'], 'Module 2: projects, artifacts and skills.'],
                    [['m3', 'm2>m3'], 'Module 3: connectors, enterprise search and Research.'],
                    [['m4', 'm3>m4'], 'Module 4: use cases by role and other ways to use Claude.'],
                    [['m5', 'cert', 'm4>m5', 'm5>cert'], 'Module 5 ends with the certificate of completion.'],
                    [['exam', 'cert>exam'], 'Want a scored credential? The CCAO-F exam is a separate, proctored step.']]},
    'pick': {'t': 'Which Claude feature fits the job', 'w': 900, 'h': 330,
             'n': [['job', 20, 137, 160, 56, 'Your job', {'c': 5, 'sh': 'pill'}],
                   ['chat', 300, 4, 250, 44, 'a quick answer or draft', {'c': 0}],
                   ['proj', 300, 58, 250, 44, 'same topic, again and again', {'c': 1}],
                   ['skill', 300, 112, 250, 44, 'same steps every time', {'c': 2}],
                   ['conn', 300, 166, 250, 44, 'facts from your own apps', {'c': 3}],
                   ['res', 300, 220, 250, 44, 'a deep answer from the web', {'c': 4}],
                   ['cow', 300, 274, 250, 44, 'many steps on your files', {'c': 5}],
                   ['a1', 640, 4, 220, 44, 'Chat', {'c': 0, 'sh': 'doc'}],
                   ['a2', 640, 58, 220, 44, 'Project', {'c': 1, 'sh': 'doc'}],
                   ['a3', 640, 112, 220, 44, 'Skill', {'c': 2, 'sh': 'doc'}],
                   ['a4', 640, 166, 220, 44, 'Connector', {'c': 3, 'sh': 'doc'}],
                   ['a5', 640, 220, 220, 44, 'Research', {'c': 4, 'sh': 'doc'}],
                   ['a6', 640, 274, 220, 44, 'Cowork', {'c': 5, 'sh': 'doc'}]],
             'e': [['job', t, {'fs': 'r', 'ts': 'l', 'via': [[240, y + 22]]}] for t, y in (('chat', 4), ('proj', 58), ('skill', 112), ('conn', 166), ('res', 220), ('cow', 274))] + [
                   ['chat', 'a1'], ['proj', 'a2'], ['skill', 'a3'], ['conn', 'a4'], ['res', 'a5'], ['cow', 'a6']],
             'st': [[['job'], 'Start from the job, not the feature.'],
                    [['chat', 'a1', 'job>chat', 'chat>a1'], 'A one off question or draft: a normal chat.'],
                    [['proj', 'a2', 'job>proj', 'proj>a2'], 'You keep returning to one topic: a project with instructions and knowledge.'],
                    [['skill', 'a3', 'job>skill', 'skill>a3'], 'A task with fixed steps: a skill.'],
                    [['conn', 'a4', 'job>conn', 'conn>a4'], 'The facts live in Drive, email or another app: a connector.'],
                    [['res', 'a5', 'job>res', 'res>a5'], 'Many web sources and citations: Research.'],
                    [['cow', 'a6', 'job>cow', 'cow>a6'], 'A long task across many files: Cowork.']]},
}

INFO = {'title': 'Claude 101: from first chat to certificate', 'panels': [
    panel([['e', '👋'], ['t', 'be specific', {'b': 1}]], 'Meet Claude', 'Say who, what, how long and what shape.', 'Then give feedback.'),
    panel([['e', '🗂️'], ['t', 'project · artifact · skill', {'b': 1, 'size': 11}]], 'Organise', 'Instructions, results and repeatable steps.', 'Each has one job.'),
    panel([['e', '🔌'], ['t', 'connectors · Research', {'b': 1, 'size': 11}]], 'Reach further', 'Your apps and the web.', 'With your own permissions.'),
    panel([['e', '🎓'], ['t', 'certificate ✓', {'b': 1}]], 'Finish', 'Free certificate at the end.', 'The CCAO-F exam is a separate step.')],
    'remember': 'Free course for the certificate. Separate proctored exam for the credential. Check every important answer.'}

REAL = [
    ['🏥', 'A clinic manager', 'Keeps a project with the clinic\'s SOPs as knowledge. New receptionists ask it "how do we book a follow up" and get the clinic\'s own steps, not a generic answer.'],
    ['🎒', 'A college student', 'Makes a study project with the course notes, asks Claude to "quiz me", and uses Research for an assignment, checking three sources by hand before citing them.'],
    ['🏢', 'An operations lead', 'Uses enterprise search to answer "what did we decide about the vendor contract" from Slack, Drive and email in one place, each person seeing only what they are allowed to see.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter walks through Claude 101 from Anthropic Academy lesson by lesson, shows how to earn its free certificate, and prepares you for the Claude Certified Associate exam.',
        'यह अध्याय Claude 101 course को पाठ दर पाठ समझाता है, मुफ्त certificate पाने का तरीका, और Claude Certified Associate exam की तैयारी।',
        'ಈ ಅಧ್ಯಾಯ Claude 101 course ಅನ್ನು ಪಾಠವಾರು ವಿವರಿಸುತ್ತದೆ, ಉಚಿತ certificate ಮತ್ತು exam ತಯಾರಿ.',
        'ଏହି ଅଧ୍ୟାୟ Claude 101 course କୁ ପାଠ ଅନୁସାରେ ବୁଝାଏ, ମାଗଣା certificate ଓ exam ପ୍ରସ୍ତୁତି।',
        'يشرح هذا الفصل دورة Claude 101 درسًا درسًا وكيف تحصل على شهادتها المجانية ويجهزك لاختبار Claude Certified Associate.',
        'Dieses Kapitel geht Claude 101 Lektion für Lektion durch, zeigt das kostenlose Zertifikat und bereitet auf die Prüfung Claude Certified Associate vor.'),
    say('about', 'The course', 'Claude 101 is a free course with five modules and fourteen lessons. You earn the certificate of completion by finishing every lesson. The paid exam is a separate step.',
        'Claude 101 मुफ्त course है, पांच modules और चौदह पाठ। सब पाठ पूरे करने पर certificate मिलता है।',
        'Claude 101 ಉಚಿತ course, ಐದು modules, ಹದಿನಾಲ್ಕು ಪಾಠ. ಎಲ್ಲ ಮುಗಿಸಿದರೆ certificate.',
        'Claude 101 ମାଗଣା course, ପାଞ୍ଚ modules, ଚଉଦ ପାଠ। ସବୁ ଶେଷ କଲେ certificate.',
        'Claude 101 دورة مجانية من خمس وحدات وأربعة عشر درسًا، والشهادة تأتي بعد إكمالها.',
        'Claude 101 ist ein kostenloser Kurs mit fünf Modulen und vierzehn Lektionen. Das Zertifikat gibt es nach Abschluss.'),
    say('meet', 'Meet Claude', 'Claude is a large language model with a knowledge cutoff, and it can be wrong. Be specific about who, what, length, tone and format, then give feedback.',
        'Claude एक बड़ा language model है, गलत भी हो सकता है। साफ बताएं: किसके लिए, क्या, कितना लंबा, कैसा।',
        'Claude ದೊಡ್ಡ language model, ತಪ್ಪಾಗಬಹುದು. ಯಾರಿಗೆ, ಏನು, ಎಷ್ಟು ಉದ್ದ ಎಂದು ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿ.',
        'Claude ଏକ ବଡ language model, ଭୁଲ ହୋଇପାରେ। କାହା ପାଇଁ, କଣ, କେତେ ଲମ୍ବା ସ୍ପଷ୍ଟ କୁହନ୍ତୁ।',
        'Claude نموذج لغوي كبير له تاريخ توقف للمعرفة وقد يخطئ. كن محددًا ثم أعطِ ملاحظاتك.',
        'Claude ist ein großes Sprachmodell mit Wissensstichtag und kann sich irren. Sei konkret und gib Rückmeldung.'),
    say('desktop', 'Desktop modes', 'The desktop app has Chat for conversations, Cowork for multi step tasks on your files, and Code for software work.',
        'Desktop app में Chat बातचीत के लिए, Cowork files पर लंबे काम के लिए, और Code software के लिए।',
        'Desktop app ನಲ್ಲಿ Chat, Cowork ಮತ್ತು Code ಮೂರು ರೀತಿಗಳು.',
        'Desktop app ରେ Chat, Cowork ଓ Code ତିନି ଉପାୟ।',
        'في تطبيق سطح المكتب: Chat للمحادثة وCowork للمهام الطويلة على ملفاتك وCode للبرمجة.',
        'Die Desktop-App hat Chat, Cowork für mehrstufige Aufgaben mit Dateien und Code für Softwarearbeit.'),
    say('organise', 'Organise', 'Projects hold instructions and knowledge, artifacts are finished pieces of work, and skills are steps Claude loads only when needed.',
        'Projects में instructions और knowledge, artifacts तैयार काम, और skills ज़रूरत पर चलने वाले कदम।',
        'Projects ನಲ್ಲಿ instructions ಮತ್ತು knowledge, artifacts ಮುಗಿದ ಕೆಲಸ, skills ಹಂತಗಳು.',
        'Projects ରେ instructions ଓ knowledge, artifacts ପୂରା କାମ, skills ପାଦ।',
        'المشاريع تحمل التعليمات والمعرفة، والعناصر أعمال مكتملة، والمهارات خطوات تُحمّل عند الحاجة.',
        'Projekte enthalten Anweisungen und Wissen, Artefakte sind fertige Arbeiten, Skills sind Schritte bei Bedarf.'),
    say('memory', 'Memory', 'Claude can save memory from chats and search past chats. You control it in Settings, Memory, and incognito chats are never saved.',
        'Claude chats से memory बना सकता है। Settings, Memory में नियंत्रण, incognito chat सेव नहीं होती।',
        'Claude memory ಉಳಿಸಬಹುದು. Settings, Memory ನಲ್ಲಿ ನಿಯಂತ್ರಣ. incognito ಉಳಿಯುವುದಿಲ್ಲ.',
        'Claude memory ରଖିପାରେ। Settings, Memory ରେ ନିୟନ୍ତ୍ରଣ। incognito ସେଭ୍ ହୁଏ ନାହିଁ।',
        'يمكن لـ Claude حفظ ذاكرة من المحادثات، وتتحكم بها من Settings ثم Memory، والمحادثة الخفية لا تُحفظ.',
        'Claude kann sich aus Chats erinnern. Steuerung unter Settings, Memory. Inkognito-Chats werden nie gespeichert.'),
    say('reach', 'Reach', 'Connectors bring in your apps with your own permissions, enterprise search looks across company tools, and Research builds a cited answer from many web sources.',
        'Connectors आपकी apps जोड़ते हैं, enterprise search कंपनी के tools में खोजता है, Research कई स्रोतों से जवाब देता है।',
        'Connectors ನಿಮ್ಮ apps, enterprise search ಕಂಪನಿ tools, Research ಅನೇಕ ಮೂಲಗಳು.',
        'Connectors ଆପଣଙ୍କ apps, enterprise search କମ୍ପାନୀ tools, Research ଅନେକ ଉତ୍ସ।',
        'الموصلات تربط تطبيقاتك بصلاحياتك، والبحث المؤسسي يبحث في أدوات الشركة، وResearch يبني إجابة موثقة.',
        'Connectors binden deine Apps mit deinen Rechten ein, Enterprise Search sucht in Firmentools, Research liefert belegte Antworten.'),
    say('roles', 'Roles', 'Every team uses the same features in its own way: marketing, sales, HR, finance, engineering, QA and operations.',
        'हर टीम वही features अपने तरीके से इस्तेमाल करती है।',
        'ಪ್ರತಿ ತಂಡ ಅದೇ features ಅನ್ನು ತನ್ನದೇ ರೀತಿಯಲ್ಲಿ ಬಳಸುತ್ತದೆ.',
        'ପ୍ରତି ଦଳ ସେହି features ନିଜ ଢଙ୍ଗରେ ବ୍ୟବହାର କରେ।',
        'كل فريق يستخدم الميزات نفسها بطريقته.',
        'Jedes Team nutzt dieselben Funktionen auf seine Weise.'),
    say('other', 'Other ways', 'Claude is on the web, the desktop app, mobile, Claude Code and the API. The API is billed separately from the plans.',
        'Claude web, desktop, mobile, Claude Code और API पर है। API का बिल अलग है।',
        'Claude web, desktop, mobile, Claude Code, API ನಲ್ಲಿ. API ಬಿಲ್ ಬೇರೆ.',
        'Claude web, desktop, mobile, Claude Code, API ରେ। API ବିଲ୍ ଅଲଗା।',
        'يتوفر Claude على الويب وسطح المكتب والجوال وClaude Code والواجهة البرمجية التي تُحاسب منفصلة.',
        'Claude gibt es im Web, als Desktop-App, mobil, als Claude Code und per API. Die API wird separat abgerechnet.'),
    say('exam', 'The exam', 'The Claude Certified Associate exam has sixty questions in one hundred and twenty minutes. You pass with a scaled score of seven hundred and twenty out of one thousand.',
        'Claude Certified Associate exam में साठ प्रश्न, एक सौ बीस मिनट, पास के लिए एक हज़ार में सात सौ बीस।',
        'Exam ನಲ್ಲಿ ಅರವತ್ತು ಪ್ರಶ್ನೆ, ನೂರ ಇಪ್ಪತ್ತು ನಿಮಿಷ, ಪಾಸ್ ಏಳುನೂರ ಇಪ್ಪತ್ತು.',
        'Exam ରେ ଷାଠିଏ ପ୍ରଶ୍ନ, ଏକ ଶହ କୋଡିଏ ମିନିଟ୍, ପାସ୍ ସାତ ଶହ କୋଡିଏ।',
        'الاختبار ستون سؤالًا في مئة وعشرين دقيقة، والنجاح بسبعمئة وعشرين من ألف.',
        'Die Prüfung hat sechzig Fragen in hundertzwanzig Minuten. Bestanden ab siebenhundertzwanzig von tausend.'),
    say('domains', 'Domains', 'The biggest domain is checking Claude\'s output. Others cover workflows, responsible use, prompting, choosing products and models, configuration and troubleshooting.',
        'सबसे बड़ा domain Claude के जवाब जांचना है।',
        'ಅತಿದೊಡ್ಡ domain Claude ಉತ್ತರ ಪರಿಶೀಲನೆ.',
        'ସବୁଠୁ ବଡ domain Claude ଉତ୍ତର ଯାଞ୍ଚ।',
        'أكبر مجال هو تقييم مخرجات Claude.',
        'Der größte Bereich ist die Prüfung der Antworten von Claude.'),
    say('scenarios', 'Scenarios', 'Check a citation against the source, pick a fast model for simple high volume work, and mask personal data before you upload it.',
        'Citation स्रोत से जांचें, सरल काम के लिए तेज़ model, और upload से पहले personal data छुपाएं।',
        'Citation ಪರಿಶೀಲಿಸಿ, ಸರಳ ಕೆಲಸಕ್ಕೆ ವೇಗದ model, personal data ಮರೆಮಾಡಿ.',
        'Citation ଯାଞ୍ଚ, ସରଳ କାମ ପାଇଁ ଦ୍ରୁତ model, personal data ଲୁଚାନ୍ତୁ।',
        'تحقق من الاستشهاد واختر نموذجًا سريعًا للعمل البسيط وأخفِ البيانات الشخصية قبل الرفع.',
        'Prüfe Zitate an der Quelle, nimm ein schnelles Modell für einfache Massenarbeit und maskiere persönliche Daten.'),
    say('plan', 'Study plan', 'Seven days: one module a day with a hands on try each time, the certificate on day five, then exam domains and the official guide.',
        'सात दिन: हर दिन एक module और अभ्यास, पांचवें दिन certificate, फिर exam तैयारी।',
        'ಏಳು ದಿನ: ದಿನಕ್ಕೆ ಒಂದು module, ಐದನೇ ದಿನ certificate.',
        'ସାତ ଦିନ: ଦିନକୁ ଗୋଟିଏ module, ପଞ୍ଚମ ଦିନ certificate.',
        'سبعة أيام: وحدة يوميًا مع تجربة عملية، والشهادة في اليوم الخامس ثم التحضير للاختبار.',
        'Sieben Tage: jeden Tag ein Modul mit Praxis, am fünften Tag das Zertifikat, dann die Prüfungsbereiche.'),
    say('cheat', 'Cheat sheet', 'Five free projects, up to ten times more project content with RAG, sixty questions, one hundred and twenty minutes, and a pass mark of seven hundred and twenty.',
        'पांच मुफ्त projects, RAG से दस गुना, साठ प्रश्न, पास सात सौ बीस।',
        'ಐದು ಉಚಿತ projects, RAG ಹತ್ತು ಪಟ್ಟು, ಅರವತ್ತು ಪ್ರಶ್ನೆ, ಪಾಸ್ ಏಳುನೂರ ಇಪ್ಪತ್ತು.',
        'ପାଞ୍ଚ ମାଗଣା projects, RAG ଦଶ ଗୁଣ, ଷାଠିଏ ପ୍ରଶ୍ନ, ପାସ୍ ସାତ ଶହ କୋଡିଏ।',
        'خمسة مشاريع مجانية وعشرة أضعاف مع RAG وستون سؤالًا والنجاح بسبعمئة وعشرين.',
        'Fünf kostenlose Projekte, bis zu zehnfach mit RAG, sechzig Fragen, Bestehensgrenze siebenhundertzwanzig.'),
    say('practice', 'Practice', 'Answer the quiz like the real exam: read the whole situation, rule out unsafe answers, then pick the simplest tool that works.',
        'Quiz असली exam की तरह करें: पूरी स्थिति पढ़ें, असुरक्षित जवाब हटाएं।',
        'Quiz ಅನ್ನು ನಿಜ exam ತರ ಮಾಡಿ.',
        'Quiz କୁ ପ୍ରକୃତ exam ପରି କରନ୍ତୁ।',
        'أجب كالاختبار الحقيقي: اقرأ الموقف كله واستبعد الإجابات غير الآمنة.',
        'Beantworte das Quiz wie die echte Prüfung: ganze Situation lesen, unsichere Antworten ausschließen.'),
]

QUIZ = [
    quiz('e', 'How do you earn the Claude 101 certificate of completion?', ['Finish every lesson of the free course', 'Pass a 60 question proctored exam', 'Buy a Pro plan', 'Build an app with the API'], 0, 'It is a course certificate.', 'The last lesson of the course is the certificate. The official course page lists no exam for it.'),
    quiz('e', 'Claude gives a confident answer about last week\'s news without web search. What should you keep in mind?', ['It has a knowledge cutoff and may be wrong about recent events', 'It always knows today\'s news', 'It is reading your email', 'Nothing, it is never wrong'], 0, 'Training has an end date.', 'Turn on web search or give it the facts, and check them.'),
    quiz('e', 'Which prompt will usually get the better first draft?', ['One that says who it is for, what to include, length, tone and format', 'The shortest possible prompt', 'One in all capital letters', 'One that repeats "please" many times'], 0, 'Be specific.', 'Specific prompts remove guessing.'),
    quiz('e', 'You return to the same topic every week with the same background files. What fits best?', ['A project with instructions and knowledge', 'A new chat each time with everything pasted', 'Research', 'Incognito chat'], 0, 'Background that repeats.', 'Projects keep instructions and files for every chat inside them.'),
    quiz('m', 'You want Claude to sort 40 PDFs in a folder and make a summary sheet. Which desktop mode fits?', ['Cowork', 'Chat only', 'Incognito', 'Enterprise search'], 0, 'Many steps on your files.', 'Cowork handles multi step tasks on folders you connect.'),
    quiz('m', 'What happens on a paid plan when a project\'s knowledge nears the context limit?', ['Claude switches to RAG and can hold up to 10 times more', 'Uploads stop forever', 'The project is deleted', 'Claude reads only the first file'], 0, 'Retrieval.', 'It searches the files and pulls only relevant parts.'),
    quiz('m', 'A colleague cannot open a Drive folder. Can Claude read it through their Drive connector?', ['No, Claude gets the same permissions as the person', 'Yes, connectors see everything', 'Only on Fridays', 'Only in incognito'], 0, 'Inherited permissions.', 'Claude cannot reach what the person cannot reach.'),
    quiz('m', 'Which needs web search turned on first?', ['Research', 'Projects', 'Memory', 'Incognito chat'], 0, 'Many web sources.', 'Turn on web search, then choose Research from the + menu.'),
    quiz('h', 'Claude cites "Section 12(4)(b)" in a summary you must send to your manager. What is the best next step?', ['Check that section in the official text before sending', 'Send it, the citation looks exact', 'Ask Claude if it is sure and send', 'Delete the citation and send'], 0, 'Domain 2.', 'Specific looking details can still be wrong. Verify against the source.'),
    quiz('h', 'Policy forbids uploading customer names and account numbers, but you need trends from that sheet. What do you do?', ['Remove or mask the identifiers, then upload', 'Upload it in incognito', 'Upload it and delete the chat later', 'Email it to yourself first'], 0, 'Domain 6.', 'Incognito does not change what you are allowed to share. Claude needs the patterns, not the identities.'),
    quiz('h', 'A team needs thousands of short, simple reply drafts a day, fast and cheap. Which model choice fits?', ['A smaller, faster model such as Haiku', 'Always the largest model', 'Research mode', 'No model, write them by hand'], 0, 'Domain 3.', 'Simple, high volume work rewards speed and low cost.'),
    quiz('x', 'Which domain carries the most weight in the CCAO-F exam?', ['Output evaluation and validation, 21%', 'Prompting, 14%', 'Troubleshooting, 10%', 'Configuration, 12%'], 0, 'Checking answers.', 'Knowing when and how to check Claude\'s work matters most.'),
    quiz('x', 'Your CCAO-F credential is 11 months old. What is the cheapest way to keep it?', ['Take the free on time renewal assessment', 'Retake the full exam at full fee', 'Nothing, it never expires', 'Finish Claude 101 again'], 0, 'Valid 12 months.', 'On time renewal is free and has no proctor. A lapsed credential needs a full retake.'),
]

CALC = [
    calc('e', 'Claude 101 has 4, 3, 3, 2 and 2 lessons in its five modules. How many lessons in total?', '14', 'Add them.', ['<span class="eq">4 + 3 + 3 + 2 + 2 = 14</span>']),
    calc('e', 'The exam has 60 questions in 120 minutes. How many minutes per question?', '2', 'Divide.', ['<span class="eq">120 ÷ 60 = 2</span>']),
    calc('m', 'Output evaluation is 21% of 60 questions. About how many questions is that?', '13', 'Multiply, then round.', ['<span class="eq">60 × 0.21 = 12.6</span>', 'About 13 questions.'], alt=['12.6', '12', 'about 13']),
    calc('m', 'Which three domains together make up more than half the exam? Give their total percent.', '52', 'Take the three biggest.', ['<span class="eq">21 + 16 + 15 = 52</span>', '52% is more than half.'], alt=['52%']),
    calc('h', 'The pass mark is 720 on a scale that runs from 100 to 1,000. How far is 720 along that scale, in percent? Round to a whole number.', '69', 'The scale starts at 100, not 0.', ['<span class="eq">(720 − 100) ÷ (1,000 − 100) = 620 ÷ 900 ≈ 0.689</span>', 'About 69%. A scaled score is not the same as percent correct.'], alt=['68.9', '69%']),
    calc('x', 'You fail twice. How many days must you wait in total before your third attempt?', '44', 'Add the first two waits.', ['<span class="eq">14 + 30 = 44</span>']),
]

EX = []

T = {
    'slug': 'claude-101', 'title': 'Claude 101 and Certification Prep', 'short': 'Claude 101 and certification', 'emoji': '🎓', 'module': MODULE, 'minutes': 30, 'added': '2026-10-22',
    'lead': 'Everything in Anthropic Academy\'s free Claude 101 course, lesson by lesson: what Claude is, better prompts, Chat, Cowork and Code, projects, artifacts, skills, memory, connectors, enterprise search and Research, use cases by role, how to earn the certificate of completion, and how to prepare for the proctored Claude Certified Associate exam.',
    'plain': 'Claude 101 is a free class from the makers of Claude. Finish all the lessons and you get a certificate. If you later want a tougher, scored test, there is a separate exam, and this page gets you ready for both.',
    'desc': 'Claude 101 course from Anthropic Academy explained lesson by lesson, how to earn the certificate, and preparation for the Claude Certified Associate Foundations (CCAO-F) exam: domains, weights, scenarios, study plan and quiz.',
    'summary': 'The official Claude 101 outline and how to earn its certificate, what Claude is and how to get better results, Chat, Cowork and Code, projects with RAG, artifacts and skills, memory and incognito, connectors, enterprise search and Research, use cases by role, other ways to use Claude, the Claude Certified Associate exam facts and its seven domains, worked exam scenarios, a seven day study plan and a cheat sheet.',
    'keywords': ['Claude 101', 'Anthropic Academy', 'certificate', 'certification', 'Claude Certified Associate', 'CCAO-F', 'exam', 'Skilljar', 'projects', 'artifacts', 'connectors', 'Research', 'Cowork', 'study plan'],
    'checked': 'Course outline from the official Claude 101 page on Anthropic Academy. Feature facts from the Claude Help Center. Exam facts from the Claude Certified Associate Foundations exam guide, version 1.0. All checked in October 2026. Plans and menus change, so check the Help Center if a screen looks different.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
