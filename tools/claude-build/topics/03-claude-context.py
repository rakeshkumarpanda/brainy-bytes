# Chapter 3: context engineering. What fills the window, context rot, the right altitude, just in time retrieval, compaction, notes and subagents.
from ckit import part, run, show, md, cli, prompt, say, quiz, calc, ex, panel

MODULE = ('🌱', 'Foundations', 'claude-foundations', 'What Claude is, how to talk to it, and how to give it the right information at the right time.')

CODES = {
    'budget': run('''
// Everything Claude sees in one request shares the same context window.
// Rough sizes in tokens for a typical Claude Code session:
const parts = {
  "system prompt and tools":        18_000,
  "CLAUDE.md (180 lines)":           2_500,
  "skill descriptions (12 skills)":  1_200,
  "MCP tool names (3 servers)":        900,
  "conversation so far":            64_000,
  "files Claude has read":          95_000,
};
const WINDOW = 1_000_000;
let used = 0;
for (const [name, tokens] of Object.entries(parts)) {
  used += tokens;
  console.log(name.padEnd(32), String(tokens).padStart(7));
}
console.log("-".repeat(40));
console.log("used".padEnd(32), String(used).padStart(7), `(${(used / WINDOW * 100).toFixed(1)}% of 1M)`);
console.log("biggest item:", Object.entries(parts).sort((a, b) => b[1] - a[1])[0][0]);
''', 'Where the tokens go in a session'),
    'altitude': md('''
<!-- Too low: brittle if-else rules -->
If the customer says "refund" reply with template R1.
If the customer says "return" reply with template R2.
If the customer says "money back" reply with template R1.

<!-- Too high: vague, assumes shared context -->
Be helpful to customers.

<!-- Right altitude: clear goal, principles and the few rules that matter -->
## Goal
Resolve the customer's issue in one reply when possible.

## How to decide
- Money back requests of any wording follow the refund policy in policies/refunds.md.
- If the order is older than 30 days, explain the policy kindly and offer store credit.
- If you are not sure which policy applies, ask one clarifying question.
''', 'Three system prompts at different altitudes'),
    'jit': run('''
// Just in time retrieval: keep light pointers, load the details only when needed.
// Instead of pasting all 400 policy pages, give Claude an index and a search tool.
const library = {
  "policies/refunds.md":  "Refunds within 30 days to the original payment method. Store credit after 30 days.",
  "policies/delivery.md": "Metro cities 2 days, other cities 5 days. Free delivery above Rs 499.",
  "policies/warranty.md": "Electronics 1 year warranty. Accidental damage not covered.",
  "policies/privacy.md":  "We never sell customer data. Delete requests within 7 days.",
};

function search(query) {
  const words = query.toLowerCase().split(/\\W+/).filter(w => w.length > 4);   // skip short words such as "days"
  return Object.entries(library)
    .map(([path, text]) => [path, words.filter(w => text.toLowerCase().includes(w)).length])
    .filter(([, score]) => score > 0)
    .sort((a, b) => b[1] - a[1])
    .map(([path]) => path);
}

const question = "How many days until delivery reaches a small town, and is delivery free?";
const hits = search(question);
console.log("index sent up front:", Object.keys(library).length, "paths");
console.log("files loaded for this question:", hits);
console.log("text loaded:", hits.map(h => library[h]).join(" "));
''', 'Load only what the question needs'),
    'compact': run('''
// Compaction: when the window fills up, replace old turns with a summary
// and keep the most recent turns word for word.
function compact(turns, keepLast, summarise) {
  if (turns.length <= keepLast) return turns;
  const old = turns.slice(0, -keepLast);
  return [{ role: "summary", text: summarise(old) }, ...turns.slice(-keepLast)];
}

const turns = [
  { role: "user", text: "Fix the login bug in auth.js" },
  { role: "claude", text: "Found it: token expiry compared in seconds vs ms. Fixed line 42." },
  { role: "user", text: "Now add a test" },
  { role: "claude", text: "Added tests/auth.test.js with 3 cases. All pass." },
  { role: "user", text: "Update the changelog" },
  { role: "claude", text: "Added an entry under 2.4.1." },
];

const summary = old => "Done so far: " + old.filter(t => t.role === "claude").map(t => t.text.split(". ")[0]).join("; ");
for (const t of compact(turns, 2, summary)) console.log(t.role.padEnd(8), t.text);
''', 'Summarise old turns, keep the latest'),
    'notes': run('''
// Structured note taking: Claude keeps a small progress file outside the chat,
// so work survives /clear, compaction or a brand new session.
import { writeFileSync, readFileSync } from "node:fs";

const progress = {
  goal: "Move 40 product pages to the new template",
  done: ["home", "pens", "notebooks"],
  next: "bags",
  notes: ["Prices must keep two decimals", "Old URLs need redirects"],
};
writeFileSync("progress.json", JSON.stringify(progress, null, 2));

// ...later, in a fresh session, the first step is to read it back:
const p = JSON.parse(readFileSync("progress.json", "utf8"));
console.log(`Resume: ${p.done.length}/40 done, next is "${p.next}".`);
console.log("Remember:", p.notes.join(" | "));
''', 'A progress file that survives a fresh start', play=False),
    'cc-cmds': cli('''
/context                        # see what is using the window right now
/clear                          # start fresh when you switch to unrelated work
/compact keep the API changes and the failing test names
/btw what was the port number again?     # quick side question, not saved to history
''', 'Context commands in Claude Code', result='/context prints a breakdown by category, including which CLAUDE.md and memory files loaded. /compact replaces the history with a summary that keeps what you asked for.'),
    'sub-prompt': prompt('''
Use a subagent to read every file in src/payments/ and find where refunds are calculated.
Report back only: the file names, the function names, and one line on what each does.
''', 'Send a big investigation to a subagent', result='The subagent reads dozens of files in its own context. Your main conversation receives a short list, not thousands of lines of code.'),
}

PARTS = [
    part('what', '🧠', 'Context engineering in one sentence', '''
<p>Prompt engineering is about <b>how you ask</b>. Context engineering is about <b>everything Claude can see</b> when it answers: instructions, files, tools, past messages and notes. Anthropic describes it as finding the smallest set of high value tokens that gives the result you want.</p>
<div class="vs"><div><b>✍️ Prompt engineering</b>Writing one good request.</div><div><b>🧠 Context engineering</b>Deciding what goes into the window, when it is loaded, and what is left out, across many turns.</div></div>
<div class="fun">A student with a huge pile of photocopies does worse in an open book exam than one with five well chosen pages. Claude is the same.</div>
''', easy=True, kw=['context engineering', 'context', 'tokens', 'what Claude sees']),
    part('rot', '🫧', 'Why more is not always better', '''
<p>Claude's attention is a <b>limited budget</b>. Every extra token takes a little of it. As the window fills, the model gets slightly worse at recalling any one fact. Anthropic calls this <b>context rot</b>. So even with a one million token window, a focused context gives better answers than a stuffed one.</p>
[[budget]]
<div class="tip">In Claude Code, run <code>/context</code> to see the real numbers for your session. The biggest item is usually files read and old conversation, not your instructions.</div>
''', easy=True, kw=['context rot', 'attention budget', 'window size', '/context']),
    part('altitude', '🎚️', 'Write instructions at the right altitude', '''
<p>A system prompt, <code>CLAUDE.md</code> or <code>SKILL.md</code> can be too low (a long list of brittle if this then that rules) or too high (vague advice that assumes Claude knows your business). The right altitude gives a clear goal, the principles to decide with, and only the few hard rules that matter.</p>
[[altitude]]
<p>Organise long instructions into sections with headings or tags, such as background, steps, tools and output format. Start small, test, and add a line only when Claude gets something wrong.</p>
''', files=['CLAUDE.md', 'SKILL.md', 'system prompt'], kw=['system prompt', 'altitude', 'principles', 'instructions']),
    part('tools', '🔧', 'Tools and examples are context too', '''
<p>Every tool Claude has comes with a name and description that sit in the context. Good tool sets are <b>small</b>, <b>do not overlap</b> and have <b>clear names</b>. If a human could not say which of two tools fits a job, Claude cannot either.</p>
<p>Examples work the same way. A few varied, typical examples teach more than a long list of every edge case.</p>
<div class="cl-put"><ul><li>One tool per clear job: <code>search_orders</code>, <code>refund_order</code>, not three tools that all "get order data".</li>
<li>Tools that return short, useful results, not a whole database table.</li></ul></div>
''', kw=['tools', 'tool descriptions', 'MCP tools', 'examples']),
    part('jit', '🎯', 'Just in time retrieval', '''
<p>Do not paste everything up front. Give Claude <b>light pointers</b> such as file paths, a list of document titles or a search tool, and let it load details only when a question needs them. Claude Code works this way: it keeps file paths and uses search and read tools instead of reading your whole project at the start.</p>
[[jit]]
<p>A mix often works best: load a little up front (like <code>CLAUDE.md</code>) and fetch the rest on demand (files, skills, MCP tools).</p>
''', easy=True, kw=['just in time', 'retrieval', 'search', 'progressive disclosure', 'RAG']),
    part('long', '⏳', 'Long tasks: compaction, notes and subagents', '''
<p>Some jobs run for hours and outgrow any window. Three techniques keep them on track.</p>
<div class="viz" data-viz="lanes" data-k="window"></div>
<p><b>1. Compaction.</b> Summarise the old conversation and continue with the summary plus the latest turns. Claude Code does this automatically near the limit.</p>
[[compact]]
<p><b>2. Structured notes.</b> Claude writes progress to a file such as <code>progress.json</code>, a to do list or <code>NOTES.md</code>. A fresh session reads it and carries on.</p>
[[notes]]
<p><b>3. Subagents.</b> A helper explores in its own clean window and returns only a short summary. Chapter 9 builds them.</p>
[[sub-prompt]]
''', kw=['compaction', 'structured notes', 'progress file', 'subagents', 'long running tasks']),
    part('cc', '💻', 'Context tools in Claude Code', '''
<p>Claude Code gives you direct control over the window.</p>
[[cc-cmds]]
<div class="tw"><table class="jt"><tr><th>Feature</th><th>When it loads</th><th>Context cost</th></tr>
<tr><td><code>CLAUDE.md</code></td><td>session start</td><td>every request, full text</td></tr>
<tr><td>Skills</td><td>description at start, body when used</td><td>low until used</td></tr>
<tr><td>MCP servers</td><td>tool names at start, full details on demand</td><td>low until a tool is used</td></tr>
<tr><td>Subagents</td><td>when started</td><td>separate window, only the summary comes back</td></tr>
<tr><td>Hooks</td><td>on events, run outside Claude</td><td>zero unless the hook returns text</td></tr>
</table></div>
<p>After compaction, the project root <code>CLAUDE.md</code>, rules without <code>paths</code>, and auto memory are loaded again from disk. Rules with <code>paths</code> and nested <code>CLAUDE.md</code> files come back only when Claude touches a matching file again. Skill bodies come back capped at 5,000 tokens each, keeping the start, so put the key steps at the top of a <code>SKILL.md</code>.</p>
''', easy=True, files=['CLAUDE.md', 'SKILL.md', '.mcp.json'], kw=['/context', '/clear', '/compact', '/btw', 'compaction', 'context cost']),
    part('checklist', '✅', 'A context checklist for any task', '''
<ol class="steps"><li><b>Always needed?</b> Put it in <code>CLAUDE.md</code> or project instructions. Keep it short.</li>
<li><b>Needed for one kind of task?</b> Put it in a skill.</li>
<li><b>Needed only for some files?</b> Put it in a path rule in <code>.claude/rules/</code>.</li>
<li><b>Big and only sometimes needed?</b> Leave it in files and let Claude search.</li>
<li><b>Noisy investigation?</b> Send it to a subagent.</li>
<li><b>Long job?</b> Keep a progress file and use <code>/compact</code> with a focus.</li>
<li><b>New topic?</b> <code>/clear</code> or a new chat.</li></ol>
''', easy=True, files=['CLAUDE.md', '.claude/rules/', 'SKILL.md', '.claude/agents/'], kw=['checklist', 'where to put context']),
]

LANES = {
    'window': {'t': 'A long task inside one context window', 's': 'Step through to see the window fill, compact and continue.', 'code': 'read 12 files\nfix bug\nwrite tests\n(window nearly full)\n/compact\ncontinue',
               'lanes': ['Context window', 'Saved outside'], 'tone': [2, 4],
               'steps': [{'l': 1, 'v': [['CLAUDE.md', 'task', '12 files read'], []], 'm': 'Reading files fills the window quickly.'},
                         {'l': 2, 'v': [['CLAUDE.md', 'task', '12 files read', 'fix discussion'], ['progress.json']], 'm': 'Claude writes progress notes to a file as it works.'},
                         {'l': 3, 'v': [['CLAUDE.md', 'task', '12 files read', 'fix discussion', 'test output'], ['progress.json']], 'm': 'Test output adds more.'},
                         {'l': 4, 'v': [['CLAUDE.md', 'task', '12 files read', 'fix discussion', 'test output', 'nearly full'], ['progress.json']], 'm': 'The window is nearly full. Recall gets weaker.'},
                         {'l': 5, 'v': [['CLAUDE.md', 'summary of work', '5 recent files'], ['progress.json']], 'm': 'Compaction keeps a summary, reloads CLAUDE.md and re-reads up to five recent files.'},
                         {'l': 6, 'v': [['CLAUDE.md', 'summary of work', '5 recent files', 'next step'], ['progress.json']], 'm': 'Work continues with plenty of room, guided by the notes file.'}]},
}

INFO = {'title': 'Give Claude the right pages, not the whole library', 'panels': [
    panel([['e', '🫧'], ['t', 'more tokens, weaker recall', {'b': 1}]], 'Context rot', 'Attention is a budget.', 'Every token you add spends a little.'),
    panel([['e', '🎚️'], ['t', 'goal + principles + few rules', {'b': 1}]], 'Right altitude', 'Not brittle, not vague.', 'Start small and add when it fails.'),
    panel([['e', '🎯'], ['t', 'index now, details later', {'b': 1}]], 'Just in time', 'Pointers first, content on demand.', 'Search beats pasting everything.'),
    panel([['e', '⏳'], ['t', 'compact, notes, subagents', {'b': 1}]], 'Long tasks', 'Three ways to keep going.', 'Notes files survive any reset.')],
    'remember': 'Smallest set of high value tokens. Load late, summarise often, delegate noise.'}

REAL = [
    ['📚', 'A law firm', 'Keeps 3,000 contracts in a folder and gives Claude a search tool, instead of uploading them all. Answers cite the two contracts that matter.'],
    ['🛠️', 'A developer', 'Runs /compact with "keep the API changes and failing tests" before lunch. After lunch the session picks up with a clean window.'],
    ['🔬', 'A research team', 'Sends three subagents to read papers on three topics. Each returns a one page summary, so the main chat stays small.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter teaches context engineering: choosing what Claude sees, when it sees it, and what to leave out.',
        'यह अध्याय context engineering सिखाता है: Claude क्या देखे, कब देखे और क्या छोड़ा जाए।',
        'ಈ ಅಧ್ಯಾಯ context engineering ಕಲಿಸುತ್ತದೆ: Claude ಏನು ನೋಡಬೇಕು, ಯಾವಾಗ ಮತ್ತು ಏನು ಬಿಡಬೇಕು.',
        'ଏହି ଅଧ୍ୟାୟ context engineering ଶିଖାଏ: Claude କଣ ଦେଖିବ, କେବେ ଓ କଣ ଛାଡିବ।',
        'يعلّمك هذا الفصل هندسة السياق: ماذا يرى Claude ومتى وما الذي يُترك.',
        'Dieses Kapitel lehrt Context Engineering: was Claude sieht, wann und was weggelassen wird.'),
    say('what', 'What it is', 'Context engineering is choosing the smallest set of useful tokens: instructions, files, tools, history and notes.',
        'Context engineering का मतलब है सबसे छोटा उपयोगी tokens का सेट चुनना।',
        'Context engineering ಎಂದರೆ ಅತಿ ಚಿಕ್ಕ ಉಪಯುಕ್ತ tokens ಸೆಟ್ ಆಯ್ಕೆ.',
        'Context engineering ମାନେ ସବୁଠୁ ଛୋଟ ଉପଯୋଗୀ tokens ସେଟ୍ ବାଛିବା।',
        'هندسة السياق هي اختيار أصغر مجموعة مفيدة من الرموز.',
        'Context Engineering heißt, die kleinste nützliche Menge an Tokens zu wählen.'),
    say('rot', 'Context rot', 'Attention is limited. The fuller the window, the weaker the recall of any one fact, so keep context focused.',
        'ध्यान सीमित है। Window जितनी भरी, किसी एक तथ्य की याद उतनी कमज़ोर।',
        'ಗಮನ ಸೀಮಿತ. Window ತುಂಬಿದಷ್ಟು ಒಂದು ಸತ್ಯದ ನೆನಪು ದುರ್ಬಲ.',
        'ଧ୍ୟାନ ସୀମିତ। Window ଯେତେ ଭରା, ଗୋଟିଏ ତଥ୍ୟର ସ୍ମୃତି ସେତେ ଦୁର୍ବଳ।',
        'الانتباه محدود. كلما امتلأت النافذة ضعف تذكر أي معلومة.',
        'Aufmerksamkeit ist begrenzt. Je voller das Fenster, desto schwächer die Erinnerung an einzelne Fakten.'),
    say('altitude', 'Altitude', 'Good instructions give a goal, principles and a few hard rules. Not a long list of brittle rules, and not vague advice.',
        'अच्छे निर्देश लक्ष्य, सिद्धांत और कुछ सख्त नियम देते हैं।',
        'ಒಳ್ಳೆಯ ಸೂಚನೆಗಳು ಗುರಿ, ತತ್ವಗಳು ಮತ್ತು ಕೆಲವು ಕಠಿಣ ನಿಯಮಗಳನ್ನು ನೀಡುತ್ತವೆ.',
        'ଭଲ ନିର୍ଦ୍ଦେଶ ଲକ୍ଷ୍ୟ, ନୀତି ଓ କିଛି କଠୋର ନିୟମ ଦିଏ।',
        'التعليمات الجيدة تعطي هدفًا ومبادئ وقواعد صارمة قليلة.',
        'Gute Anweisungen geben ein Ziel, Prinzipien und wenige feste Regeln.'),
    say('tools', 'Tools', 'Tool descriptions take up context too. Keep tools few, clear and not overlapping.',
        'Tool descriptions भी context लेते हैं। Tools कम, साफ़ और अलग रखें।',
        'Tool descriptions ಕೂಡ context ಬಳಸುತ್ತವೆ. Tools ಕಡಿಮೆ, ಸ್ಪಷ್ಟ ಇರಲಿ.',
        'Tool descriptions ବି context ନିଏ। Tools କମ୍ ଓ ସ୍ପଷ୍ଟ ରଖନ୍ତୁ।',
        'أوصاف الأدوات تشغل السياق أيضًا. اجعلها قليلة وواضحة.',
        'Tool-Beschreibungen belegen auch Kontext. Halte Tools wenige, klar und überschneidungsfrei.'),
    say('jit', 'Just in time', 'Give Claude pointers like file paths or a search tool, and load the details only when a question needs them.',
        'Claude को file paths या search tool जैसे संकेत दें और ज़रूरत पर ही विवरण लोड करें।',
        'Claude ಗೆ file paths ಅಥವಾ search tool ನೀಡಿ, ಅಗತ್ಯವಾದಾಗ ಮಾತ್ರ ವಿವರ ಲೋಡ್ ಮಾಡಿ.',
        'Claude କୁ file paths ବା search tool ଦିଅନ୍ତୁ, ଦରକାର ହେଲେ ହିଁ ବିବରଣୀ ଲୋଡ୍ କରନ୍ତୁ।',
        'أعطِ Claude مؤشرات مثل مسارات الملفات وحمّل التفاصيل عند الحاجة فقط.',
        'Gib Claude Verweise wie Dateipfade und lade Details erst bei Bedarf.'),
    say('long', 'Long tasks', 'For long jobs, compact old turns into a summary, keep progress notes in a file, and send noisy work to subagents.',
        'लंबे काम में पुराने turns का सार बनाएं, progress file रखें और subagents का उपयोग करें।',
        'ದೀರ್ಘ ಕೆಲಸದಲ್ಲಿ ಹಳೆಯ turns ಸಾರಾಂಶ, progress file ಮತ್ತು subagents ಬಳಸಿ.',
        'ଲମ୍ବା କାମରେ ପୁରୁଣା turns ର ସାରାଂଶ, progress file ଓ subagents ବ୍ୟବହାର କରନ୍ତୁ।',
        'في المهام الطويلة لخّص الأدوار القديمة واحفظ الملاحظات في ملف واستخدم الوكلاء الفرعيين.',
        'Bei langen Aufgaben: alte Runden zusammenfassen, Fortschritt in einer Datei notieren, Subagenten nutzen.'),
    say('cc', 'Claude Code', 'Use slash context to see usage, slash clear between tasks, and slash compact with a focus before a long new task.',
        'Usage देखने के लिए /context, काम बदलने पर /clear और लंबे काम से पहले /compact।',
        'ಬಳಕೆ ನೋಡಲು /context, ಕೆಲಸ ಬದಲಿಸಿದಾಗ /clear, ದೀರ್ಘ ಕೆಲಸಕ್ಕೆ ಮೊದಲು /compact.',
        'ବ୍ୟବହାର ଦେଖିବାକୁ /context, କାମ ବଦଳିଲେ /clear, ଲମ୍ବା କାମ ପୂର୍ବରୁ /compact.',
        'استخدم /context لرؤية الاستهلاك و/clear بين المهام و/compact قبل مهمة طويلة.',
        'Nutze /context für die Übersicht, /clear zwischen Aufgaben und /compact vor einer langen Aufgabe.'),
    say('checklist', 'Checklist', 'Always needed goes in CLAUDE.md, one task goes in a skill, some files go in a path rule, big data stays searchable.',
        'हमेशा ज़रूरी CLAUDE.md में, एक काम skill में, कुछ files के लिए path rule।',
        'ಯಾವಾಗಲೂ ಬೇಕಾದದ್ದು CLAUDE.md, ಒಂದು ಕೆಲಸ skill, ಕೆಲವು files ಗೆ path rule.',
        'ସବୁବେଳେ ଦରକାରୀ CLAUDE.md ରେ, ଗୋଟିଏ କାମ skill ରେ, କିଛି files ପାଇଁ path rule.',
        'ما يلزم دائمًا في CLAUDE.md والمهمة الواحدة في مهارة وبعض الملفات في قاعدة مسار.',
        'Immer Nötiges in CLAUDE.md, eine Aufgabe in einen Skill, bestimmte Dateien in eine Pfadregel.'),
    say('practice', 'Practice', 'Practise budgeting tokens, picking relevant files and compacting a conversation in code.',
        'Tokens का बजट, सही files चुनना और बातचीत compact करने का अभ्यास करें।',
        'Tokens ಬಜೆಟ್, ಸರಿಯಾದ files ಆಯ್ಕೆ ಮತ್ತು compact ಅಭ್ಯಾಸ.',
        'Tokens ବଜେଟ୍, ଠିକ୍ files ବାଛିବା ଓ compact ର ଅଭ୍ୟାସ।',
        'تدرّب على ميزانية الرموز واختيار الملفات وضغط المحادثة.',
        'Übe Token-Budgets, passende Dateien wählen und Gespräche verdichten.'),
]

QUIZ = [
    quiz('e', 'What is context engineering about?', ['Choosing everything Claude can see and when', 'Writing longer prompts', 'Buying a bigger plan', 'Typing faster'], 0, 'More than one prompt.', 'It covers instructions, files, tools, history and notes across many turns.'),
    quiz('e', 'Which command shows what fills your Claude Code context?', ['/context', '/clear', '/model', '/init'], 0, 'It shows usage.', '/context gives a live breakdown by category.'),
    quiz('e', 'You finish a bug fix and start writing a blog post. What should you do?', ['/clear or start a new chat', 'Keep going in the same chat', 'Paste the bug again', 'Switch model'], 0, 'Unrelated work.', 'Old turns about the bug only add noise and cost.'),
    quiz('m', 'What is context rot?', ['Recall gets weaker as the window fills', 'Files get deleted', 'Claude forgets after one day', 'Tokens expire'], 0, 'Attention budget.', 'More tokens means less attention for each one.'),
    quiz('m', 'Which instruction is at the right altitude?', ['Money back requests follow refunds.md, ask one question if unsure', 'If they say refund use R1, if they say return use R2...', 'Be helpful', 'Do your best'], 0, 'Goal plus principle.', 'It is clear and general enough to handle new wordings.'),
    quiz('m', 'What does a subagent send back to the main conversation?', ['A short summary of its findings', 'Every file it read', 'Nothing', 'Its whole context'], 0, 'Isolation.', 'Its exploration stays in its own window.'),
    quiz('h', 'After /compact, which loads again from disk automatically?', ['The project root CLAUDE.md', 'Rules with paths frontmatter', 'Every file ever read', 'All old messages'], 0, 'Session start content.', 'Path rules and nested CLAUDE.md files return only when matching files are touched.'),
    quiz('h', 'Skill bodies after compaction are capped at how many tokens per skill?', ['5,000', '500', '50,000', 'No cap'], 0, 'Keep key steps at the top.', 'Truncation keeps the start of the file.'),
    quiz('x', 'Why give Claude a search tool instead of pasting 400 policy pages?', ['It loads only the relevant pages, keeping context focused', 'Search is free', 'Claude cannot read pages', 'Pasting is not allowed'], 0, 'Just in time.', 'Pointers up front and content on demand.'),
    quiz('x', 'How does a long task survive a brand new session?', ['A progress notes file Claude reads first', 'Claude remembers automatically', 'By using a bigger model', 'It cannot'], 0, 'Write it down.', 'Structured notes outside the chat carry state across resets.'),
]

CALC = [
    calc('e', 'A session uses 181,600 tokens of a 1,000,000 window. Roughly what percent is that, to the nearest whole number?', '18', 'Divide and times 100.', ['<span class="eq">181,600 ÷ 1,000,000 = 0.1816</span>', 'About 18%.'], alt=['18%']),
    calc('e', 'CLAUDE.md is 2,500 tokens and is sent with every request. How many tokens over 40 requests?', '100000', 'Multiply.', ['<span class="eq">2,500 × 40 = 100,000</span>'], alt=['100,000']),
    calc('m', 'Twelve skills each have an 80 token description. How many tokens do they cost per request?', '960', 'Only descriptions load.', ['<span class="eq">12 × 80 = 960</span>']),
    calc('m', 'A subagent reads 120,000 tokens and returns a 600 token summary. How many tokens did the main window avoid?', '119400', 'Read minus returned.', ['<span class="eq">120,000 − 600 = 119,400</span>'], alt=['119,400']),
    calc('h', 'Compaction keeps the last 2 turns of 6 and adds 1 summary. How many items remain?', '3', 'Summary plus kept turns.', ['<span class="eq">1 + 2 = 3</span>']),
    calc('x', 'Moving a 9,000 token style guide from CLAUDE.md into a skill (90 token description) saves how many tokens per request when the skill is not used?', '8910', 'Old cost minus new cost.', ['<span class="eq">9,000 − 90 = 8,910</span>'], alt=['8,910']),
]

EX = [
    ex('fits', 'e', 'Does it fit?', '<p>Write <code>fits(parts, window)</code>. <code>parts</code> is an object of token counts. Return true when their total is at most <code>window</code>.</p>',
       'function fits(parts, window) {\n  \n}\n',
       [('fits({ a: 100, b: 200 }, 300)', True), ('fits({ a: 100, b: 201 }, 300)', False), ('fits({}, 10)', True)],
       'function fits(parts, window) {\n  return Object.values(parts).reduce((s, n) => s + n, 0) <= window;\n}',
       hint='<code>Object.values</code> and <code>reduce</code>.', why='Checking the budget before a long job avoids surprise compaction in the middle of it.'),
    ex('relevant', 'm', 'Pick relevant files', '<p>Write <code>relevant(files, question)</code>. <code>files</code> maps a path to its text. Return the paths whose text contains at least one word from the question that is longer than 3 letters (ignore case), in the original order.</p>',
       'function relevant(files, question) {\n  \n}\n',
       [('relevant({ "a.md": "Refunds in 30 days", "b.md": "Delivery in 2 days" }, "When do refunds arrive?")', ['a.md']),
        ('relevant({ "a.md": "x", "b.md": "y" }, "hello there")', []),
        ('relevant({ "a.md": "DELIVERY fees", "b.md": "delivery times" }, "delivery")', ['a.md', 'b.md'])],
       'function relevant(files, question) {\n  const words = question.toLowerCase().split(/\\W+/).filter(w => w.length > 3);\n  return Object.keys(files).filter(p => words.some(w => files[p].toLowerCase().includes(w)));\n}',
       hint='Split the question into words, then <code>filter</code> the paths.', why='This is the core of just in time retrieval: load only what the question points at.'),
    ex('compact', 'h', 'Compact a conversation', '<p>Write <code>compact(turns, keep)</code>. If there are more than <code>keep</code> turns, return a new list that starts with <code>{ role: "summary", text: N + " earlier turns" }</code> (N is how many were removed) followed by the last <code>keep</code> turns. Otherwise return the turns unchanged.</p>',
       'function compact(turns, keep) {\n  \n}\n',
       [('compact([{role:"user",text:"a"},{role:"claude",text:"b"},{role:"user",text:"c"}], 1)', [{'role': 'summary', 'text': '2 earlier turns'}, {'role': 'user', 'text': 'c'}]),
        ('compact([{role:"user",text:"a"}], 3).length', 1)],
       'function compact(turns, keep) {\n  if (turns.length <= keep) return turns;\n  const removed = turns.length - keep;\n  return [{ role: "summary", text: removed + " earlier turns" }, ...turns.slice(-keep)];\n}',
       hint='<code>slice(-keep)</code> gives the last turns.', why='Keeping recent turns word for word and summarising the rest is exactly how compaction keeps long sessions useful.'),
]

T = {
    'slug': 'claude-context', 'title': 'Context Engineering: The Right Information at the Right Time', 'short': 'Context engineering', 'emoji': '🧠', 'module': MODULE, 'minutes': 15,
    'lead': 'Why a focused context beats a full one, how to write instructions at the right altitude, just in time retrieval, compaction, progress notes and subagents, and the context commands in Claude Code.',
    'plain': 'Claude can only pay attention to so much at once. Context engineering means giving it the few pages it needs right now, and keeping the rest on the shelf until it asks.',
    'desc': 'Context engineering for Claude: context rot, attention budget, system prompt altitude, tools, just in time retrieval, compaction, structured notes, subagents, /context and /compact.',
    'summary': 'Context engineering versus prompt engineering, context rot and the attention budget, instructions at the right altitude, tools and examples as context, just in time retrieval, compaction, progress files and subagents for long tasks, what Claude Code loads when and what survives /compact, and a checklist for where each piece of context belongs.',
    'keywords': ['context engineering', 'context window', 'context rot', 'attention budget', 'just in time', 'retrieval', 'compaction', '/compact', '/context', '/clear', 'progress notes', 'subagents'],
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
