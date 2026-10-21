# Chapter 2: prompt engineering. Clear and direct, context and why, examples, XML tags, roles, long documents, format, chains and templates.
from ckit import part, run, show, prompt, say, quiz, calc, ex, panel

MODULE = ('🌱', 'Foundations', 'claude-foundations', 'What Claude is, how to talk to it, and how to give it the right information at the right time.')

CODES = {
    'vague': prompt('''
Write something about our new product.
''', 'A vague prompt', result='Claude has to guess the product, the reader, the length and the purpose. You get a generic paragraph you cannot use.'),
    'clear': prompt('''
Write a 60 word Instagram caption for "Mango Lassi Ice Cream", our new flavour.

Reader: college students in Bengaluru who follow our cafe.
Goal: get them to visit this weekend for the 2 for 1 offer.
Tone: playful, one emoji at most.
End with the line: "Only at Scoops, Indiranagar."
''', 'The same task, said clearly', result='A caption of about 60 words, aimed at students, that mentions the weekend offer and ends with the exact closing line.'),
    'why': prompt('''
Summarise this lesson for my students.

Some of my students use a screen reader, which reads every symbol out loud.
So please write in full sentences and avoid tables, arrows and emoji.
''', 'Give the reason, not only the rule', result='Claude avoids tables, arrows and emoji, and also avoids other symbols you did not list, because it understands the reason.'),
    'examples': prompt('''
Sort each customer message into one of: refund, delivery, product_question, other.
Reply with the label only.

<examples>
<example>
<message>My parcel says delivered but I never got it</message>
<label>delivery</label>
</example>
<example>
<message>Is the steel bottle safe for hot tea?</message>
<label>product_question</label>
</example>
<example>
<message>I was charged twice, please return one payment</message>
<label>refund</label>
</example>
</examples>

<message>The lid of my lunch box cracked on day one, I want my money back</message>
''', 'Teach the pattern with examples', result='Claude replies with the single word refund, in the same format as the examples.'),
    'xml': run('''
// Wrapping each piece of a prompt in its own tag stops Claude mixing them up.
// This helper builds a prompt with several documents, the way the docs recommend:
// long documents first, the question last.
function buildPrompt(docs, question) {
  const body = docs.map((d, i) =>
    `  <document index="${i + 1}">\\n    <source>${d.source}</source>\\n` +
    `    <document_content>\\n${d.text}\\n    </document_content>\\n  </document>`).join("\\n");
  return `<documents>\\n${body}\\n</documents>\\n\\n${question}`;
}

const prompt = buildPrompt(
  [{ source: "leave-policy.pdf", text: "Staff get 18 days of paid leave a year." },
   { source: "holiday-list-2026.xlsx", text: "Office closed on 15 Aug, 2 Oct and 25 Dec." }],
  "Using only the documents above, how many paid days off does a new hire get in 2026? Quote the lines you used.");

console.log(prompt);
''', 'Several documents in XML tags'),
    'role': show('''
import anthropic

client = anthropic.Anthropic()            # reads ANTHROPIC_API_KEY from the environment

message = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    system="You are a friendly maths tutor for children aged 9 to 11. "
           "Explain with small numbers and everyday objects. Ask one question back.",
    messages=[{"role": "user", "content": "Why is 3 x 4 the same as 4 x 3?"}],
)
for block in message.content:
    if block.type == "text":
        print(block.text)
''', 'A role set in the system prompt (Python)', lang='py', note='🔑 Needs an API key, shown not run',
        result='Claude answers as a tutor, with something like rows of 3 apples and 4 apples, and ends with a small question for the child.'),
    'format': prompt('''
Read the meeting notes below and return the action items.

Write your answer as a numbered list. Each line has the owner's name,
then the task, then the due date in the form 12 Nov.
If a task has no owner, write "Owner needed".
Respond directly, without an introduction.

<notes>
Priya will update the price sheet by Thursday 13 Nov.
We need someone to call the printer about the brochure.
Ravi to send the client the revised quote on 14 Nov.
</notes>
''', 'Ask for the exact shape you want', result='1. Priya, update the price sheet, 13 Nov\n2. Owner needed, call the printer about the brochure, no date\n3. Ravi, send the revised quote, 14 Nov'),
    'think': prompt('''
Our shop sold 1,240 items in March and 1,550 in April.
Returns were 62 in March and 93 in April.

Before you answer, work through it step by step inside <thinking> tags.
Then give the final answer inside <answer> tags.

Question: did the return rate go up or down, and by how many percentage points?
''', 'Ask Claude to think first', result='Inside thinking: 62 ÷ 1,240 = 5.0% and 93 ÷ 1,550 = 6.0%. Inside answer: the return rate went up by 1 percentage point.'),
    'template': run('''
// A prompt template: write the prompt once, fill in the details every day.
const TEMPLATE = `You are helping {{name}}, who works as {{job}}.

<task>
{{task}}
</task>

Rules:
- Keep the answer under {{words}} words.
- Use simple English.`;

function fill(template, values) {
  return template.replace(/{{(\\w+)}}/g, (whole, key) => {
    if (!(key in values)) throw new Error("missing value for " + key);
    return values[key];
  });
}

console.log(fill(TEMPLATE, {
  name: "Anita", job: "an HR executive", words: 120,
  task: "Draft a polite reminder to staff to submit timesheets by Friday 5pm.",
}));
''', 'Fill a reusable prompt template'),
    'lint': run('''
// A tiny prompt checker. It looks for the things good prompts usually have.
function checkPrompt(p) {
  const tips = [];
  if (p.split(/\\s+/).length < 12) tips.push("Too short: add who it is for and why.");
  if (!/\\d+\\s*(words|lines|bullet|items|sentences)|table|list|json/i.test(p)) tips.push("Say the format or length you want.");
  if (/\\b(something|stuff|good|nice|etc)\\b/i.test(p)) tips.push("Replace vague words with specifics.");
  if (p.length > 400 && !/<\\w+>/.test(p)) tips.push("Long input: wrap data in tags like <notes>.");
  return tips.length ? tips : ["Looks clear."];
}

console.log(checkPrompt("Write something nice about our product"));
console.log(checkPrompt("Write a 60 word caption for college students about our 2 for 1 lassi offer this weekend, playful tone."));
''', 'A simple prompt checker'),
    'chain': prompt('''
Step 1 prompt:  "Draft a 150 word apology email to a customer whose order was late. <order>...</order>"
Step 2 prompt:  "Review this draft against the checklist: polite, gives a reason, gives a new date,
                 offers the 10% voucher, under 150 words. List what is missing. <draft>...</draft>"
Step 3 prompt:  "Rewrite the draft so it passes every item. <draft>...</draft> <review>...</review>"
''', 'A three step chain: draft, review, refine', result='Each step is a separate request, so you can read the review before the rewrite and catch problems early.'),
    'daily': prompt('''
<role>You are my executive assistant.</role>

<inbox>
(paste today's unread emails here)
</inbox>

For each email give me:
1. One line summary
2. Urgency: today, this week or no rush
3. A two sentence reply draft in my voice: friendly and short

Then list the three things I should do first today.
''', 'Daily inbox triage prompt', result='A short block per email with a summary, an urgency tag and a reply draft, then a top three list for the day.'),
}

PARTS = [
    part('clear', '🎯', 'Be clear and direct', '''
<p>Anthropic's own advice is to treat Claude like a <b>brilliant but new employee</b>. It is very capable, but it does not know your customers, your style or what "good" means to you. The golden rule: if a colleague who knows nothing about the task would be confused by your prompt, Claude will be too.</p>
<div class="vs"><div><b>😕 Vague</b>[[vague]]</div><div><b>😀 Clear</b>[[clear]]</div></div>
<p>A clear prompt answers five questions: <b>what</b> to make, <b>for whom</b>, <b>why</b>, <b>how long</b> and <b>what it must include</b>. When the order of steps matters, number them.</p>
''', easy=True, kw=['clear prompt', 'specific', 'golden rule', 'new employee']),
    part('why', '💡', 'Say why, not only what', '''
<p>Claude follows a rule better when it knows the reason. A bare rule covers one case. A reason lets Claude handle cases you did not think of.</p>
[[why]]
<div class="tip">Ask for what you <b>want</b>, not only what you do not want. "Write in flowing paragraphs" works better than "do not use bullet points".</div>
''', easy=True, kw=['context', 'motivation', 'reason', 'positive instructions']),
    part('examples', '🧪', 'Show examples', '''
<p>Examples are one of the most reliable ways to control format and tone. This is called <b>few shot</b> or <b>multishot</b> prompting. The docs suggest three to five examples that are close to your real task, different from each other, and wrapped in <code>&lt;example&gt;</code> tags so Claude can tell them apart from your instructions.</p>
[[examples]]
<div class="warn">If all your examples look alike, Claude may copy accidental details too, such as always starting with the same word. Vary them.</div>
''', easy=True, kw=['few shot', 'multishot', 'examples', 'example tags', 'classification']),
    part('xml', '🏷️', 'Use XML tags to separate the pieces', '''
<p>A prompt often mixes instructions, background, examples and data. Put each kind in its own tag, such as <code>&lt;instructions&gt;</code>, <code>&lt;context&gt;</code> or <code>&lt;notes&gt;</code>. There are no magic tag names. Pick clear ones and use them the same way every time.</p>
<p>For long material, the docs give two tips: put the <b>documents at the top</b> and the <b>question at the end</b> (this improved answers by up to 30 percent in Anthropic's tests), and give each document its own tag with its source.</p>
[[xml]]
<div class="tip">Asking Claude to <b>quote the lines it used</b> before answering keeps it grounded in your documents instead of its general knowledge.</div>
''', kw=['XML tags', 'documents', 'long context', 'quotes', 'grounding']),
    part('role', '🎭', 'Give Claude a role', '''
<p>One sentence about who Claude is for this task changes tone and focus. In the API this goes in the <b>system prompt</b>. In claude.ai it goes in project instructions. In Claude Code the closest place is <code>CLAUDE.md</code> or an output style.</p>
[[role]]
''', files=['system prompt'], kw=['role', 'system prompt', 'persona', 'tutor']),
    part('format', '📐', 'Control the format of the answer', '''
<p>Tell Claude the exact shape: a numbered list, a table, JSON, a word limit, a closing line. Showing the shape works even better.</p>
[[format]]
<div class="cl-name">Older guides tell you to "prefill" the start of Claude's answer. Since the Claude 4.6 models, a prefilled final assistant message returns an error. Ask for the format in words, use tags, or use structured outputs in the API instead.</div>
''', easy=True, kw=['format', 'output format', 'list', 'JSON', 'prefill', 'preamble']),
    part('think', '🤔', 'Let Claude think before answering', '''
<p>For sums, comparisons and decisions, ask Claude to work through the problem first. Tags make it easy to keep the working separate from the final answer, so a script can read just the answer.</p>
[[think]]
<p>In the API, current models also have <b>adaptive thinking</b>: Claude decides how much to think on its own. You switch it on with <code>thinking: {type: "adaptive"}</code>. Chapter 12 shows it.</p>
''', kw=['step by step', 'thinking', 'chain of thought', 'adaptive thinking']),
    part('template', '🧩', 'Prompt templates for daily work', '''
<p>When you send the same kind of prompt every day, turn it into a <b>template</b> with blanks in double braces. Fill the blanks each time. Later, the same template becomes a skill (chapter 7) or a line in a script (chapter 11).</p>
[[template]]
[[daily]]
[[lint]]
''', easy=True, kw=['template', 'variables', 'daily automation', 'inbox triage', 'prompt checker']),
    part('chain', '⛓️', 'Chain prompts: draft, review, refine', '''
<p>Big jobs go better in steps. The most useful chain is <b>self correction</b>: one prompt drafts, one checks the draft against a list, one rewrites. You can read each step and stop if something is off.</p>
[[chain]]
<div class="scenario"><b>🏢 Real scenario: a monthly report</b>An operations lead pastes raw numbers. Prompt 1 writes the summary. Prompt 2 checks every number against the table. Prompt 3 fixes the two numbers that did not match. Errors that once reached the director now stop at step 2.</div>
''', kw=['prompt chaining', 'self correction', 'review', 'pipeline']),
    part('recipe', '📋', 'A recipe card for any prompt', '''
<ol class="steps"><li><b>Role:</b> who Claude is for this task.</li>
<li><b>Context:</b> who it is for and why it matters.</li>
<li><b>Data:</b> pasted inside tags, long material first.</li>
<li><b>Task:</b> numbered steps if order matters.</li>
<li><b>Format:</b> shape, length, what to include.</li>
<li><b>Examples:</b> three to five, inside example tags, when format matters.</li>
<li><b>Check:</b> ask for quotes or a short self check when facts matter.</li></ol>
<div class="fun">You do not need all seven every time. A quick question needs one line. A task you will repeat a hundred times deserves all seven.</div>
<div class="viz" data-viz="flow" data-k="anatomy"></div>
''', easy=True, kw=['prompt checklist', 'recipe', 'structure']),
]

DG = {
    'anatomy': {'t': 'How the pieces of a prompt fit together', 'w': 900, 'h': 300,
                'n': [['role', 20, 20, 190, 52, 'role', {'c': 3, 'sub': 'system prompt', 'i': 'One sentence about who Claude is for this task.'}],
                      ['ctx', 20, 90, 190, 52, 'context and why', {'c': 2, 'i': 'Who the answer is for and why it matters.'}],
                      ['data', 20, 160, 190, 52, '<documents>', {'c': 0, 'sub': 'long data first', 'i': 'Pasted material in tags, at the top of the message.'}],
                      ['ex', 20, 230, 190, 52, '<examples>', {'c': 5, 'sub': '3 to 5', 'i': 'Varied examples of the output you want.'}],
                      ['task', 300, 90, 200, 70, 'task and format', {'c': 1, 'sub': 'question at the end', 'i': 'Numbered steps, the shape and the length of the answer.'}],
                      ['cl', 580, 100, 120, 52, 'Claude', {'c': 1, 'sh': 'pill'}],
                      ['out', 760, 100, 120, 52, 'answer', {'c': 4, 'sh': 'doc'}]],
                'e': [['role', 'task'], ['ctx', 'task'], ['data', 'task'], ['ex', 'task'], ['task', 'cl'], ['cl', 'out']],
                'st': [[['role', 'ctx', 'role>task', 'ctx>task'], 'Role and context tell Claude who it is and why the job matters.'],
                       [['data', 'ex', 'data>task', 'ex>task'], 'Data and examples go in their own tags, with long material first.'],
                       [['task', 'cl', 'out', 'task>cl', 'cl>out'], 'The task and the format come last, right before Claude answers.']]},
}

INFO = {'title': 'Talk to Claude like a great manager', 'panels': [
    panel([['e', '🎯'], ['t', 'what, who, why, how long', {'b': 1}]], 'Be specific', 'Vague in, vague out.', 'Imagine a smart new colleague reading it.'),
    panel([['e', '💡'], ['t', 'because...', {'b': 1}]], 'Give the reason', 'Rules with reasons generalise.', 'Claude then handles cases you did not list.'),
    panel([['e', '🧪'], ['t', '<example> x 3', {'b': 1}]], 'Show, do not only tell', 'Examples fix format and tone.', 'Keep them varied.'),
    panel([['e', '🏷️'], ['t', '<notes> ... </notes>', {'b': 1}]], 'Tag your data', 'Tags keep instructions and data apart.', 'Documents on top, question at the end.')],
    'remember': 'Role, context, data, task, format, examples, check.'}

REAL = [
    ['📧', 'An office manager', 'Pastes the morning inbox into a saved triage prompt and gets replies drafted for 25 emails before 9:30.'],
    ['🛍️', 'A small online shop', 'Uses a few shot prompt with four labelled examples to sort every review into praise, complaint or question.'],
    ['📊', 'A finance analyst', 'Puts the quarterly PDF at the top, the question at the end, and asks for quoted lines, so every number can be traced.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter teaches prompt writing: be clear, give reasons, show examples, use tags, set a role, control format, let Claude think, and reuse templates.',
        'यह अध्याय अच्छे prompt लिखना सिखाता है: साफ़ बोलें, कारण दें, उदाहरण दिखाएं, tags लगाएं और templates दोहराएं।',
        'ಈ ಅಧ್ಯಾಯ ಒಳ್ಳೆಯ prompt ಬರೆಯುವುದನ್ನು ಕಲಿಸುತ್ತದೆ: ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿ, ಕಾರಣ ನೀಡಿ, ಉದಾಹರಣೆ ತೋರಿಸಿ, tags ಬಳಸಿ.',
        'ଏହି ଅଧ୍ୟାୟ ଭଲ prompt ଲେଖିବା ଶିଖାଏ: ସ୍ପଷ୍ଟ କୁହନ୍ତୁ, କାରଣ ଦିଅନ୍ତୁ, ଉଦାହରଣ ଦେଖାନ୍ତୁ, tags ବ୍ୟବହାର କରନ୍ତୁ।',
        'يعلّمك هذا الفصل كتابة الموجّهات: كن واضحًا واذكر السبب واعرض أمثلة واستخدم الوسوم والقوالب.',
        'Dieses Kapitel lehrt gute Prompts: klar sein, Gründe nennen, Beispiele zeigen, Tags nutzen und Vorlagen wiederverwenden.'),
    say('clear', 'Be clear', 'Treat Claude like a brilliant new employee. Say what to make, for whom, why, how long and what it must include.',
        'Claude को एक होशियार नए कर्मचारी की तरह समझें। बताएं क्या बनाना है, किसके लिए, क्यों और कितना लंबा।',
        'Claude ಅನ್ನು ಬುದ್ಧಿವಂತ ಹೊಸ ನೌಕರನಂತೆ ನೋಡಿ. ಏನು, ಯಾರಿಗೆ, ಏಕೆ, ಎಷ್ಟು ಉದ್ದ ಎಂದು ಹೇಳಿ.',
        'Claude କୁ ଜଣେ ବୁଦ୍ଧିମାନ ନୂଆ କର୍ମଚାରୀ ଭାବନ୍ତୁ। କଣ, କାହା ପାଇଁ, କାହିଁକି ଓ କେତେ ଲମ୍ବା କୁହନ୍ତୁ।',
        'عامل Claude كموظف جديد ذكي. قل ماذا تريد ولمن ولماذا وبأي طول.',
        'Behandle Claude wie einen klugen neuen Mitarbeiter. Sag, was, für wen, warum und wie lang.'),
    say('why', 'Give reasons', 'A rule with a reason works better, because Claude can apply the reason to cases you did not list.',
        'कारण के साथ नियम बेहतर काम करता है, क्योंकि Claude उसे नए मामलों पर भी लागू कर सकता है।',
        'ಕಾರಣ ಸಹಿತ ನಿಯಮ ಉತ್ತಮ, ಏಕೆಂದರೆ Claude ಅದನ್ನು ಹೊಸ ಸಂದರ್ಭಗಳಿಗೂ ಅನ್ವಯಿಸುತ್ತದೆ.',
        'କାରଣ ସହ ନିୟମ ଭଲ କାମ କରେ, କାରଣ Claude ତାହା ନୂଆ ପରିସ୍ଥିତିରେ ବି ଲାଗୁ କରେ।',
        'القاعدة مع سببها أفضل لأن Claude يطبق السبب على حالات لم تذكرها.',
        'Eine Regel mit Begründung wirkt besser, weil Claude sie auf neue Fälle anwenden kann.'),
    say('examples', 'Examples', 'Three to five varied examples inside example tags are one of the most reliable ways to control format and tone.',
        'Example tags में तीन से पांच अलग उदाहरण format और tone नियंत्रित करने का सबसे भरोसेमंद तरीका हैं।',
        'Example tags ಒಳಗೆ ಮೂರು ರಿಂದ ಐದು ವಿಭಿನ್ನ ಉದಾಹರಣೆಗಳು format ನಿಯಂತ್ರಿಸಲು ಉತ್ತಮ.',
        'Example tags ଭିତରେ ତିନିରୁ ପାଞ୍ଚଟି ଭିନ୍ନ ଉଦାହରଣ format ନିୟନ୍ତ୍ରଣ ପାଇଁ ଭରସାଯୋଗ୍ୟ।',
        'من ثلاثة إلى خمسة أمثلة متنوعة داخل وسوم example من أفضل طرق ضبط الشكل والنبرة.',
        'Drei bis fünf verschiedene Beispiele in example-Tags steuern Format und Ton sehr zuverlässig.'),
    say('xml', 'XML tags', 'Put each kind of content in its own tag. Long documents go at the top and the question at the end.',
        'हर तरह की सामग्री को अपने tag में रखें। लंबे documents ऊपर और सवाल अंत में।',
        'ಪ್ರತಿ ವಿಷಯವನ್ನು ತನ್ನದೇ tag ನಲ್ಲಿ ಇಡಿ. ಉದ್ದ documents ಮೇಲೆ, ಪ್ರಶ್ನೆ ಕೊನೆಯಲ್ಲಿ.',
        'ପ୍ରତ୍ୟେକ ବିଷୟକୁ ନିଜ tag ରେ ରଖନ୍ତୁ। ଲମ୍ବା documents ଉପରେ, ପ୍ରଶ୍ନ ଶେଷରେ।',
        'ضع كل نوع من المحتوى في وسم خاص. المستندات الطويلة في الأعلى والسؤال في النهاية.',
        'Jede Art von Inhalt in ein eigenes Tag. Lange Dokumente oben, die Frage am Ende.'),
    say('role', 'Roles', 'A one sentence role in the system prompt changes Claude\'s tone and focus for the whole conversation.',
        'System prompt में एक वाक्य की भूमिका पूरी बातचीत का tone बदल देती है।',
        'System prompt ನಲ್ಲಿ ಒಂದು ವಾಕ್ಯದ ಪಾತ್ರ ಸಂಪೂರ್ಣ ಸಂಭಾಷಣೆಯ tone ಬದಲಿಸುತ್ತದೆ.',
        'System prompt ରେ ଗୋଟିଏ ବାକ୍ୟର ଭୂମିକା ପୂରା କଥାବାର୍ତ୍ତାର tone ବଦଳାଏ।',
        'جملة واحدة عن الدور في موجّه النظام تغيّر نبرة المحادثة كلها.',
        'Eine Rolle in einem Satz im Systemprompt ändert Ton und Fokus des ganzen Gesprächs.'),
    say('format', 'Format', 'Describe or show the exact shape of the answer. Prefilling the answer no longer works on current models.',
        'जवाब का सटीक रूप बताएं या दिखाएं। Prefill अब नए models पर काम नहीं करता।',
        'ಉತ್ತರದ ನಿಖರ ರೂಪ ಹೇಳಿ ಅಥವಾ ತೋರಿಸಿ. Prefill ಹೊಸ models ನಲ್ಲಿ ಕೆಲಸ ಮಾಡುವುದಿಲ್ಲ.',
        'ଉତ୍ତରର ସଠିକ୍ ରୂପ କୁହନ୍ତୁ ବା ଦେଖାନ୍ତୁ। Prefill ନୂଆ models ରେ କାମ କରେନାହିଁ।',
        'صف شكل الإجابة أو اعرضه. التعبئة المسبقة لا تعمل في النماذج الحالية.',
        'Beschreibe oder zeige die genaue Form der Antwort. Prefill funktioniert bei aktuellen Modellen nicht mehr.'),
    say('think', 'Thinking', 'For sums and decisions, ask Claude to think step by step in thinking tags and give the answer in answer tags.',
        'हिसाब और फैसलों के लिए Claude से thinking tags में कदम दर कदम सोचने को कहें।',
        'ಲೆಕ್ಕ ಮತ್ತು ನಿರ್ಧಾರಗಳಿಗೆ thinking tags ನಲ್ಲಿ ಹಂತ ಹಂತವಾಗಿ ಯೋಚಿಸಲು ಹೇಳಿ.',
        'ହିସାବ ଓ ନିଷ୍ପତ୍ତି ପାଇଁ thinking tags ରେ ପାଦେ ପାଦେ ଭାବିବାକୁ କୁହନ୍ତୁ।',
        'للحسابات والقرارات اطلب من Claude التفكير خطوة بخطوة داخل وسوم thinking.',
        'Bei Rechnungen und Entscheidungen bitte Claude, Schritt für Schritt in thinking-Tags zu denken.'),
    say('template', 'Templates', 'Turn a prompt you use every day into a template with blanks, and fill the blanks each time.',
        'रोज़ के prompt को खाली जगहों वाला template बनाएं और हर बार भरें।',
        'ದಿನನಿತ್ಯದ prompt ಅನ್ನು ಖಾಲಿ ಜಾಗಗಳ template ಆಗಿ ಮಾಡಿ, ಪ್ರತಿ ಬಾರಿ ತುಂಬಿ.',
        'ଦୈନିକ prompt କୁ ଖାଲି ସ୍ଥାନ ଥିବା template କରନ୍ତୁ ଓ ପ୍ରତି ଥର ଭରନ୍ତୁ।',
        'حوّل الموجّه اليومي إلى قالب بفراغات واملأها في كل مرة.',
        'Mach aus einem täglichen Prompt eine Vorlage mit Lücken und fülle sie jedes Mal.'),
    say('chain', 'Chains', 'Split big jobs into draft, review and refine steps, and read each result before the next step.',
        'बड़े काम को draft, review और सुधार में बांटें।',
        'ದೊಡ್ಡ ಕೆಲಸವನ್ನು draft, review ಮತ್ತು ಸುಧಾರಣೆಯಾಗಿ ವಿಭಜಿಸಿ.',
        'ବଡ କାମକୁ draft, review ଓ ସୁଧାର ରେ ଭାଗ କରନ୍ତୁ।',
        'قسّم العمل الكبير إلى مسودة ومراجعة وتحسين.',
        'Teile große Aufgaben in Entwurf, Prüfung und Verbesserung.'),
    say('recipe', 'Recipe', 'Role, context, data, task, format, examples and a check. Use all seven for prompts you repeat often.',
        'भूमिका, संदर्भ, data, काम, format, उदाहरण और जांच।',
        'ಪಾತ್ರ, ಸಂದರ್ಭ, data, ಕೆಲಸ, format, ಉದಾಹರಣೆ ಮತ್ತು ಪರಿಶೀಲನೆ.',
        'ଭୂମିକା, ପ୍ରସଙ୍ଗ, data, କାମ, format, ଉଦାହରଣ ଓ ଯାଞ୍ଚ।',
        'الدور والسياق والبيانات والمهمة والشكل والأمثلة والتحقق.',
        'Rolle, Kontext, Daten, Aufgabe, Format, Beispiele und Prüfung.'),
    say('practice', 'Practice', 'Practise filling templates, wrapping data in tags and building few shot prompts in code.',
        'Templates भरने, data को tags में लपेटने और few shot prompts बनाने का अभ्यास करें।',
        'Templates ತುಂಬುವ, tags ಬಳಸುವ ಮತ್ತು few shot prompts ಮಾಡುವ ಅಭ್ಯಾಸ.',
        'Templates ଭରିବା, tags ଓ few shot prompts ର ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرّب على ملء القوالب ووضع البيانات في وسوم وبناء أمثلة.',
        'Übe Vorlagen füllen, Daten in Tags packen und Few-Shot-Prompts bauen.'),
]

QUIZ = [
    quiz('e', 'Which prompt is clearer?', ['Write a 60 word caption for students about our weekend offer', 'Write something good', 'Make content', 'Do marketing'], 0, 'Who, what, how long.', 'It names the length, the reader and the purpose.'),
    quiz('e', 'Why wrap pasted notes in &lt;notes&gt; tags?', ['So Claude can tell data apart from instructions', 'Tags make Claude faster', 'Claude only reads tags', 'It is required by law'], 0, 'Separation.', 'Tags show exactly where the data starts and ends.'),
    quiz('e', 'How many examples does the guide suggest for few shot prompting?', ['3 to 5', '1', '20 or more', 'None'], 0, 'A small handful.', 'Three to five relevant, varied examples work best.'),
    quiz('m', 'Where should a 50 page report go in a prompt?', ['At the top, with the question at the end', 'At the end, after the question', 'In a separate chat', 'It does not matter'], 0, 'Long data first.', 'Anthropic measured up to 30 percent better answers with the query at the end.'),
    quiz('m', 'Which instruction works better?', ['Write in flowing paragraphs', 'Do not use bullet points', 'NEVER use lists!!!', 'No markdown'], 0, 'Say what you want.', 'Positive instructions are easier to follow than bans.'),
    quiz('m', 'In the API, where does a role like "You are a maths tutor" usually go?', ['The system prompt', 'The model name', 'max_tokens', 'The API key'], 0, 'Applies to the whole chat.', 'The system field sets the role for every turn.'),
    quiz('h', 'What happens if you prefill the final assistant message on a Claude 4.6 or newer model?', ['The request returns an error', 'Claude continues from it', 'It is ignored', 'It doubles the cost'], 0, 'No longer supported.', 'Use format instructions, tags or structured outputs instead.'),
    quiz('h', 'Your examples all start with "Great question!". What may happen?', ['Claude copies that opening too', 'Claude ignores the examples', 'Nothing', 'Claude refuses'], 0, 'Patterns are copied.', 'Vary examples so accidental details are not learned.'),
    quiz('x', 'What is the most common prompt chain pattern?', ['Draft, review against criteria, refine', 'Translate, translate back', 'Ask the same thing twice', 'Summarise, delete'], 0, 'Self correction.', 'Each step is a separate request you can inspect.'),
    quiz('x', 'Why ask Claude to quote the lines it used from a document?', ['It keeps answers grounded in the document', 'Quotes are cheaper', 'It hides the answer', 'Claude cannot answer otherwise'], 0, 'Grounding.', 'Quoting first ties the answer to your text, and you can check it.'),
]

CALC = [
    calc('e', 'A template has the blanks {{name}}, {{job}} and {{task}}. How many values must you fill?', '3', 'Count the blanks.', ['Three different blanks, so three values.']),
    calc('e', 'You give 4 examples and add 1 more for an edge case. How many examples now?', '5', 'Add.', ['<span class="eq">4 + 1 = 5</span>']),
    calc('m', 'March: 62 returns from 1,240 sales. What percent is that?', '5', 'Divide, then times 100.', ['<span class="eq">62 ÷ 1,240 = 0.05</span>', '<span class="eq">0.05 × 100 = 5%</span>'], alt=['5%']),
    calc('m', 'A chain has 3 steps. Each step sends 1,200 tokens and gets 300 back. Total tokens?', '4500', 'Per step first.', ['<span class="eq">1,200 + 300 = 1,500</span>', '<span class="eq">3 × 1,500 = 4,500</span>'], alt=['4,500']),
    calc('h', 'Moving the question to the end improves answers by up to 30%. If 70 of 100 answers were right before, how many could be right at most after?', '91', '30% more than 70.', ['<span class="eq">70 × 1.3 = 91</span>']),
    calc('x', 'Inbox triage runs on 25 emails a day for 22 working days. How many emails a month?', '550', 'Multiply.', ['<span class="eq">25 × 22 = 550</span>']),
]

EX = [
    ex('fill', 'e', 'Fill a template', '<p>Write <code>fill(template, values)</code> that replaces every <code>{{key}}</code> with <code>values[key]</code>. Leave a blank untouched when the key is missing.</p>',
       'function fill(template, values) {\n  \n}\n',
       [('fill("Hi {{name}}!", { name: "Asha" })', 'Hi Asha!'), ('fill("{{a}} and {{a}}", { a: "x" })', 'x and x'), ('fill("Dear {{who}}", {})', 'Dear {{who}}')],
       'function fill(template, values) {\n  return template.replace(/{{(\\w+)}}/g, (whole, key) => key in values ? String(values[key]) : whole);\n}',
       hint='<code>replace</code> with a regular expression and a function.', why='Templates turn a good prompt into something you can run every day without retyping.'),
    ex('tag', 'm', 'Wrap data in tags', '<p>Write <code>tag(name, text)</code> that returns <code>&lt;name&gt;</code>, a new line, the trimmed text, a new line and <code>&lt;/name&gt;</code>.</p>',
       'function tag(name, text) {\n  \n}\n',
       [('tag("notes", "  call Ravi ")', '<notes>\ncall Ravi\n</notes>'), ('tag("q", "Why?")', '<q>\nWhy?\n</q>')],
       'function tag(name, text) {\n  return `<${name}>\\n${text.trim()}\\n</${name}>`;\n}',
       hint='Use a template literal.', why='Tagging every pasted input the same way makes prompts easy for Claude and for you to read.'),
    ex('fewshot', 'h', 'Build a few shot block', '<p>Write <code>fewShot(pairs)</code>. <code>pairs</code> is a list of <code>[input, output]</code>. Return them inside <code>&lt;examples&gt;</code> where each pair becomes <code>&lt;example&gt;&lt;input&gt;...&lt;/input&gt;&lt;output&gt;...&lt;/output&gt;&lt;/example&gt;</code>, with every tag on one line and examples joined by new lines.</p>',
       'function fewShot(pairs) {\n  \n}\n',
       [('fewShot([["hi", "greeting"]])', '<examples>\n<example><input>hi</input><output>greeting</output></example>\n</examples>'),
        ('fewShot([["a", "1"], ["b", "2"]]).split("\\n").length', 4)],
       'function fewShot(pairs) {\n  const rows = pairs.map(([i, o]) => `<example><input>${i}</input><output>${o}</output></example>`);\n  return ["<examples>", ...rows, "</examples>"].join("\\n");\n}',
       hint='Map each pair to one line, then join with the opening and closing tags.', why='Generating examples from a list lets you grow your example set without hand editing the prompt.'),
]

T = {
    'slug': 'claude-prompting', 'title': 'Prompt Engineering That Works', 'short': 'Prompt engineering', 'emoji': '✍️', 'module': MODULE, 'minutes': 16,
    'lead': 'The techniques from Anthropic\'s own prompting guide, each with a real daily task: clear instructions, reasons, examples, XML tags, roles, output format, thinking, templates and prompt chains.',
    'plain': 'A prompt is a message that tells Claude what you want. Good prompts are like good instructions to a new classmate: say what, for whom, why, how long, and show an example.',
    'desc': 'Prompt engineering for Claude: clear and direct prompts, context, few shot examples, XML tags, system prompt roles, output format, thinking, templates and chains.',
    'summary': 'Clear and direct prompts, giving reasons, few shot examples in example tags, XML tags with long documents first, roles in the system prompt, controlling output format and why prefill no longer works, step by step thinking, reusable prompt templates for daily work, prompt chains for self correction, and a seven step prompt recipe.',
    'keywords': ['prompt engineering', 'prompting', 'few shot', 'examples', 'XML tags', 'system prompt', 'role', 'output format', 'prefill', 'chain of thought', 'template', 'prompt chaining'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
