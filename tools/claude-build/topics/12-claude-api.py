# Chapter 12: the Claude API. Keys, the first call, system prompts and conversations, choosing a model and cost,
# streaming, JSON output, effort and caching, and handling errors. SDK code runs against a local stand-in API.
from ckit import part, run, show, cli, say, quiz, calc, ex, panel, api_run

MODULE = ('🔌', 'Building with the API', 'claude-build-api', 'Call Claude from your own code: the Messages API, tools, agent loops and the Agent SDK.')

HELLO = '''
import anthropic

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from the environment

response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "What is the capital of India? One sentence."}
    ],
)

for block in response.content:
    if block.type == "text":
        print(block.text)

print("stop_reason:", response.stop_reason)
print("tokens in:", response.usage.input_tokens, "| tokens out:", response.usage.output_tokens)
'''

CHAT = '''
import anthropic

client = anthropic.Anthropic()

SYSTEM = """You are Pinky, a friendly maths tutor for a 9 year old.
Use short sentences and Indian examples like rupees and cricket.
Never give the final answer straight away. Give one hint at a time."""

history = []

def ask(text):
    history.append({"role": "user", "content": text})
    reply = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=500,
        system=SYSTEM,
        messages=history,          # the API remembers nothing, so send the whole chat each time
    )
    answer = reply.content[0].text
    history.append({"role": "assistant", "content": answer})
    print("Child:", text)
    print("Pinky:", answer, "\\n")

ask("What is 3 times 4?")
ask("Is it 7?")
ask("Oh! Then it is 12?")
print("messages sent in the last request:", len(history) - 1)
'''

STREAM = '''
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-5-5",
    max_tokens=2000,
    messages=[{"role": "user", "content": "Write a two line poem about monsoon rain."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)    # words appear as they are written
    final = stream.get_final_message()

print("\\n\\nstop_reason:", final.stop_reason, "| tokens out:", final.usage.output_tokens)
'''

JSON_OUT = '''
import json
import anthropic

client = anthropic.Anthropic()

review = "Delivery was 2 days late but the mixer grinder works great. Box was damaged."

response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1000,
    messages=[{"role": "user", "content": f"Read this product review and fill in the fields.\\n\\n<review>{review}</review>"}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "sentiment": {"type": "string", "enum": ["positive", "mixed", "negative"]},
                    "issues": {"type": "array", "items": {"type": "string"}},
                    "stars": {"type": "integer"},
                },
                "required": ["sentiment", "issues", "stars"],
                "additionalProperties": False,
            },
        }
    },
)

data = json.loads(response.content[0].text)   # valid JSON in the exact shape asked for
print(data)
print("needs follow-up:", data["sentiment"] != "positive" and len(data["issues"]) > 0)
'''

COST = r'''
// What a job costs on each model. Prices are dollars per million tokens (input / output).
const PRICES = {
  "claude-fable-5-1":  [10, 50],
  "claude-opus-5-5":   [4, 20],
  "claude-sonnet-5-5": [2, 10],
  "claude-haiku-5-5":  [0.10, 0.50],   // for prompts of 100K tokens or fewer
};

// A support team summarises 2,000 tickets a day: about 1,500 tokens in and 200 out each.
const tickets = 2000, inTok = 1500, outTok = 200;

for (const [model, [pin, pout]] of Object.entries(PRICES)) {
  const perDay = tickets * (inTok * pin + outTok * pout) / 1e6;
  console.log(model.padEnd(18), "$" + perDay.toFixed(2).padStart(7), "a day  $" + (perDay * 30).toFixed(0).padStart(5), "a month");
}
'''

CACHE = '''
import anthropic

client = anthropic.Anthropic()
POLICY = open("leave-policy.md").read()   # a long document you send with every question

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1000,
    output_config={"effort": "low"},       # low | medium | high | xhigh | max
    system=[
        {"type": "text", "text": "Answer HR questions using only the policy below."},
        {"type": "text", "text": POLICY, "cache_control": {"type": "ephemeral"}},   # cache everything up to here
    ],
    messages=[{"role": "user", "content": "How many casual leaves do I get?"}],
)
print(response.content[0].text)
print("written to cache:", response.usage.cache_creation_input_tokens,
      "| read from cache:", response.usage.cache_read_input_tokens)
'''

ERRORS = '''
import anthropic

client = anthropic.Anthropic(max_retries=4)   # 429, 5xx and connection errors are retried for you (default 2)

try:
    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=300,
        messages=[{"role": "user", "content": "Summarise our refund policy"}],
    )
except anthropic.AuthenticationError:
    print("401: the API key is missing or wrong")
except anthropic.RateLimitError:
    print("429: too many requests, slow down and try later")
except anthropic.APIStatusError as e:
    print("API error", e.status_code, e.message)
else:
    if response.stop_reason == "max_tokens":
        print("The answer was cut off. Raise max_tokens.")
    elif response.stop_reason == "refusal":
        print("Claude declined this request.")
    else:
        print(response.content[0].text)
'''

CODES = {
    'setup': cli('''
# 1. Create a key at platform.claude.com (Settings, then API keys)
# 2. Keep it in an environment variable, never in code
export ANTHROPIC_API_KEY="sk-ant-..."        # macOS / Linux
setx ANTHROPIC_API_KEY "sk-ant-..."          # Windows (open a new terminal after)

# 3. Install the SDK for your language
pip install anthropic                        # Python
npm install @anthropic-ai/sdk                # JavaScript / TypeScript
''', 'Get a key and install the SDK'),
    'hello': api_run(HELLO, 'Your first API call', {'replies': {'capital': 'The capital of India is New Delhi.'}}),
    'hello-ts': show('''
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();   // reads ANTHROPIC_API_KEY

const response = await client.messages.create({
  model: "claude-haiku-5-5",
  max_tokens: 1000,
  messages: [{ role: "user", content: "What is the capital of India? One sentence." }],
});

for (const block of response.content) {
  if (block.type === "text") console.log(block.text);
}
''', 'The same call in TypeScript', lang='js', note='📄 Ready to copy'),
    'curl': cli('''
curl https://api.anthropic.com/v1/messages \\
  -H "x-api-key: $ANTHROPIC_API_KEY" \\
  -H "anthropic-version: 2023-06-01" \\
  -H "content-type: application/json" \\
  -d '{"model": "claude-haiku-5-5", "max_tokens": 1000,
       "messages": [{"role": "user", "content": "What is the capital of India?"}]}'
''', 'And with plain HTTP'),
    'chat': api_run(CHAT, 'A tutor with a system prompt and memory of the chat', {
        'replies': {'oh!': 'Yes! 3 groups of 4 make 12. Well done, champion! 🏏',
                    'is it 7': 'Close, but 7 is what you get when you add 3 and 4. Times means groups. Try counting 4, 8, ...',
                    '3 times 4': 'Think of 3 overs where you score 4 runs in each. How many runs is that in total?'}}),
    'cost': run(COST, 'The same job priced on four models'),
    'stream': api_run(STREAM, 'Stream the answer as it is written', {'default': 'Grey clouds hum a song on the tin roof,\nand the dry earth smells of first rain.'}),
    'json': api_run(JSON_OUT, 'Get JSON in a fixed shape', {'default': '{"sentiment": "mixed", "issues": ["late delivery", "damaged box"], "stars": 3}'}, log=False),
    'cache': api_run(CACHE, 'Effort and prompt caching', {'default': 'You get 12 casual leaves a year. (stand-in reply)'}, log=False,
                     more={'leave-policy.md': '# Leave policy\n\nCasual leave: 12 days a year.\nSick leave: 10 days a year.\n'}),
    'errors': show(ERRORS, 'errors.py: handle what can go wrong', lang='py', note='📄 Ready to copy'),
}

PARTS = [
    part('setup', '🔑', 'Get a key and install the SDK', '''
<p>The <b>Claude API</b> lets your own program talk to Claude. You pay per token used, separate from a Claude.ai subscription.</p>
<ol class="steps"><li>Sign in at <code>platform.claude.com</code> and add billing.</li><li>Create an API key.</li><li>Store it in the <code>ANTHROPIC_API_KEY</code> environment variable.</li><li>Install the official SDK.</li></ol>
[[setup]]
<div class="cl-put"><b>Never</b> put the key in code, in a Git repository or in a web page. Anyone with the key can spend your money. Keep it in an environment variable or a secrets manager.</div>
''', easy=True, kw=['API key', 'ANTHROPIC_API_KEY', 'pip install anthropic', '@anthropic-ai/sdk', 'Claude Console']),
    part('first', '👋', 'Your first call, line by line', '''
[[hello]]
<div class="tw"><table class="jt"><tr><th>Part</th><th>What it means</th></tr>
<tr><td><code>model</code></td><td>which Claude to use</td></tr>
<tr><td><code>max_tokens</code></td><td>the most it may write. A token is about three quarters of an English word.</td></tr>
<tr><td><code>messages</code></td><td>the conversation so far, as a list of user and assistant turns</td></tr>
<tr><td><code>response.content</code></td><td>a list of blocks. Check <code>block.type</code> before reading <code>.text</code>.</td></tr>
<tr><td><code>stop_reason</code></td><td><code>end_turn</code> (finished), <code>max_tokens</code> (cut off), <code>tool_use</code>, or <code>refusal</code></td></tr>
<tr><td><code>usage</code></td><td>tokens in and out, which is what you pay for</td></tr></table></div>
[[hello-ts]]
[[curl]]
''', easy=True, kw=['messages.create', 'model', 'max_tokens', 'messages', 'stop_reason', 'usage']),
    part('system', '🧑‍🏫', 'System prompts and conversations', '''
<p>The <code>system</code> prompt sets the role and rules for the whole chat. The API does <b>not remember</b> anything between calls, so your code keeps the history and sends it every time.</p>
[[chat]]
<div class="cl-put"><b>What goes in a system prompt:</b> who Claude is in this app, who the user is, the tone, the rules it must always follow, and the format of answers. The same advice as chapter 2 applies: be clear, give reasons, use examples and XML tags.</div>
''', easy=True, kw=['system prompt', 'conversation history', 'stateless', 'multi-turn']),
    part('models', '⚖️', 'Choose a model and know the cost', '''
<div class="tw"><table class="jt"><tr><th>Model</th><th>Id</th><th>$ per million in / out</th><th>Good for</th></tr>
<tr><td>Fable 5.1</td><td><code>claude-fable-5-1</code></td><td>10 / 50</td><td>the hardest, longest tasks</td></tr>
<tr><td>Opus 5.5</td><td><code>claude-opus-5-5</code></td><td>4 / 20</td><td>complex agents, coding, deep analysis</td></tr>
<tr><td>Sonnet 5.5</td><td><code>claude-sonnet-5-5</code></td><td>2 / 10</td><td>most apps: strong and quick</td></tr>
<tr><td>Haiku 5.5</td><td><code>claude-haiku-5-5</code></td><td>0.10 / 0.50</td><td>sorting, extracting, high volume</td></tr></table></div>
<p>All four have a 1 million token context window and up to 128K output tokens. Haiku 5.5 costs $0.50 / $2.50 for prompts over 100K tokens.</p>
<p class="eq">cost = (input tokens × input price + output tokens × output price) ÷ 1,000,000</p>
[[cost]]
<p>Start with Sonnet. Move simple, high volume steps to Haiku, and hard steps to Opus. Test with your own examples before you switch.</p>
''', easy=True, kw=['models', 'pricing', 'Haiku', 'Sonnet', 'Opus', 'Fable', 'tokens', 'cost']),
    part('stream', '🌊', 'Streaming: show words as they arrive', '''
<p>Long answers take time. Streaming sends the text piece by piece, so your app can show it at once. Use it for anything long, because it also avoids request timeouts.</p>
[[stream]]
''', kw=['streaming', 'messages.stream', 'text_stream', 'get_final_message']),
    part('json', '🧾', 'Get JSON your code can trust', '''
<p>With <code>output_config.format</code> and a JSON schema, the reply is valid JSON in exactly that shape. No more "please answer only in JSON" and hoping.</p>
[[json]]
''', kw=['structured outputs', 'json_schema', 'output_config', 'JSON']),
    part('cache', '💾', 'Effort and prompt caching', '''
<ul><li><b>Effort</b> (<code>output_config.effort</code>) sets how hard Claude thinks: <code>low</code>, <code>medium</code>, <code>high</code>, <code>xhigh</code> or <code>max</code>. Low is faster and cheaper, high is better for hard problems.</li>
<li><b>Prompt caching</b> stores the start of a prompt you send again and again, such as a long policy. Later calls read it from the cache at a fraction of the price: $0.20 per million instead of $4 on Opus 5.5.</li></ul>
[[cache]]
<p>The stand-in API does not cache, so it reports 0 for both. Against the real API the first call writes the policy to the cache and calls in the next 5 minutes read it.</p>
''', kw=['effort', 'prompt caching', 'cache_control', 'ephemeral', 'cache_read_input_tokens']),
    part('errors', '🧯', 'When things go wrong', '''
[[errors]]
<div class="tw"><table class="jt"><tr><th>Code</th><th>Meaning</th><th>What to do</th></tr>
<tr><td>400</td><td>the request is wrong</td><td>read the message, fix the field</td></tr>
<tr><td>401</td><td>bad or missing key</td><td>check <code>ANTHROPIC_API_KEY</code></td></tr>
<tr><td>429</td><td>rate limit</td><td>the SDK retries. Slow down if it keeps happening.</td></tr>
<tr><td>500, 529</td><td>server busy or error</td><td>the SDK retries. Try again later.</td></tr></table></div>
''', kw=['errors', '429', 'retries', 'max_tokens', 'refusal']),
]

INFO = {'title': 'The Claude API in one page', 'panels': [
    panel([['e', '🔑'], ['t', 'ANTHROPIC_API_KEY', {'b': 1, 'size': 11}]], 'Key', 'From platform.claude.com.', 'Only in the environment.'),
    panel([['e', '📨'], ['t', 'messages.create', {'b': 1}]], 'Call', 'model, max_tokens, messages.', 'Optional system prompt.'),
    panel([['e', '🧾'], ['t', 'json_schema', {'b': 1}]], 'Shape', 'JSON your code can trust.', 'Stream long answers.'),
    panel([['e', '💰'], ['t', 'usage', {'b': 1}]], 'Cost', 'Pay per token in and out.', 'Haiku for volume, Opus for hard.')],
    'remember': 'The API remembers nothing. Your code sends the history every time.'}

REAL = [
    ['🛍️', 'An online store', 'Sends each new review to Haiku with a JSON schema. Mixed and negative reviews with issues go straight to the support queue.'],
    ['📚', 'An edtech startup', 'Built a maths tutor like Pinky above with a system prompt and saved chat history, then streamed answers to the app.'],
    ['🏢', 'An HR team', 'Caches a 60 page policy in the system prompt so each employee question costs a fraction of the first one.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter calls Claude from your own code with the Messages API, step by step.',
        'यह अध्याय आपके code से Messages API के ज़रिए Claude को बुलाता है।',
        'ಈ ಅಧ್ಯಾಯ ನಿಮ್ಮ code ನಿಂದ Messages API ಮೂಲಕ Claude ಅನ್ನು ಕರೆಯುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ ଆପଣଙ୍କ code ରୁ Messages API ଦ୍ୱାରା Claude କୁ ଡାକେ।',
        'يستدعي هذا الفصل Claude من شيفرتك عبر واجهة الرسائل خطوة بخطوة.',
        'Dieses Kapitel ruft Claude Schritt für Schritt aus deinem Code über die Messages API auf.'),
    say('setup', 'Setup', 'Create a key, keep it in an environment variable, and install the SDK.',
        'Key बनाएँ, environment variable में रखें, SDK install करें।',
        'Key ರಚಿಸಿ, environment variable ನಲ್ಲಿ ಇಡಿ, SDK install ಮಾಡಿ.',
        'Key ତିଆରି କରି environment variable ରେ ରଖନ୍ତୁ, SDK install କରନ୍ତୁ।',
        'أنشئ مفتاحًا واحفظه في متغير بيئة وثبّت الحزمة.',
        'Erstelle einen Schlüssel, lege ihn in eine Umgebungsvariable und installiere das SDK.'),
    say('first', 'First call', 'Send a model, max tokens and messages. Read the text blocks, the stop reason and the token usage.',
        'Model, max_tokens और messages भेजें। Text, stop_reason और usage पढ़ें।',
        'Model, max_tokens, messages ಕಳುಹಿಸಿ. Text, stop_reason, usage ಓದಿ.',
        'Model, max_tokens ଓ messages ପଠାନ୍ତୁ। Text, stop_reason ଓ usage ପଢନ୍ତୁ।',
        'أرسل النموذج والحد الأقصى والرسائل، ثم اقرأ النص وسبب التوقف والاستهلاك.',
        'Sende Modell, max_tokens und Nachrichten. Lies Text, Stoppgrund und Verbrauch.'),
    say('system', 'System prompt', 'The system prompt sets the role. The API remembers nothing, so send the whole history each time.',
        'System prompt भूमिका तय करता है। पूरा history हर बार भेजें।',
        'System prompt ಪಾತ್ರ ನಿರ್ಧರಿಸುತ್ತದೆ. ಪೂರ್ಣ history ಪ್ರತಿಬಾರಿ ಕಳುಹಿಸಿ.',
        'System prompt ଭୂମିକା ସ୍ଥିର କରେ। ପୂରା history ପ୍ରତିଥର ପଠାନ୍ତୁ।',
        'موجّه النظام يحدد الدور، والواجهة لا تتذكر، فأرسل السجل كاملًا كل مرة.',
        'Der Systemprompt legt die Rolle fest. Sende jedes Mal den ganzen Verlauf.'),
    say('models', 'Models', 'Haiku is cheapest, Sonnet suits most apps, Opus and Fable handle the hardest work. Cost is tokens times price.',
        'Haiku सबसे सस्ता, Sonnet ज़्यादातर apps के लिए, Opus कठिन काम के लिए।',
        'Haiku ಅಗ್ಗ, Sonnet ಹೆಚ್ಚಿನ apps ಗೆ, Opus ಕಠಿಣ ಕೆಲಸಕ್ಕೆ.',
        'Haiku ଶସ୍ତା, Sonnet ଅଧିକାଂଶ apps ପାଇଁ, Opus କଠିନ କାମ ପାଇଁ।',
        'Haiku الأرخص وSonnet لمعظم التطبيقات وOpus للأصعب.',
        'Haiku ist am günstigsten, Sonnet für die meisten Apps, Opus für das Schwerste.'),
    say('stream', 'Streaming', 'Streaming shows words as they arrive and avoids timeouts on long answers.',
        'Streaming शब्दों को आते ही दिखाता है।',
        'Streaming ಪದಗಳನ್ನು ಬಂದಂತೆ ತೋರಿಸುತ್ತದೆ.',
        'Streaming ଶବ୍ଦ ଆସୁଆସୁ ଦେଖାଏ।',
        'البث يعرض الكلمات فور وصولها.',
        'Streaming zeigt Wörter sofort an.'),
    say('json', 'JSON', 'A JSON schema in output config makes the reply valid JSON in exactly that shape.',
        'Output config में JSON schema देने से जवाब सही JSON होता है।',
        'Output config ನಲ್ಲಿ JSON schema ಕೊಟ್ಟರೆ ಸರಿಯಾದ JSON ಬರುತ್ತದೆ.',
        'Output config ରେ JSON schema ଦେଲେ ଠିକ୍ JSON ଆସେ।',
        'مخطط JSON في الإعدادات يجعل الرد JSON صالحًا بالشكل المطلوب.',
        'Ein JSON-Schema sorgt für gültiges JSON in genau dieser Form.'),
    say('cache', 'Effort and caching', 'Effort sets how hard Claude thinks. Caching makes a repeated long prompt much cheaper.',
        'Effort सोचने की गहराई तय करता है। Caching दोहराए prompt को सस्ता करता है।',
        'Effort ಆಲೋಚನೆಯ ಆಳ, caching ಪುನರಾವರ್ತಿತ prompt ಅಗ್ಗ.',
        'Effort ଚିନ୍ତାର ଗଭୀରତା, caching ପୁନରାବୃତ୍ତ prompt ଶସ୍ତା କରେ।',
        'الجهد يحدد عمق التفكير والتخزين المؤقت يخفض كلفة الموجّه المكرر.',
        'Effort steuert die Denktiefe, Caching verbilligt wiederholte Prompts.'),
    say('errors', 'Errors', 'The SDK retries rate limits and server errors. Check the stop reason for cut off answers and refusals.',
        'SDK 429 और 5xx पर फिर कोशिश करता है। Stop reason जाँचें।',
        'SDK 429, 5xx ಗೆ ಮರುಪ್ರಯತ್ನಿಸುತ್ತದೆ. Stop reason ನೋಡಿ.',
        'SDK 429 ଓ 5xx ରେ ପୁଣି ଚେଷ୍ଟା କରେ। Stop reason ଦେଖନ୍ତୁ।',
        'تعيد الحزمة المحاولة عند 429 و5xx. افحص سبب التوقف.',
        'Das SDK wiederholt bei 429 und 5xx. Prüfe den Stoppgrund.'),
    say('practice', 'Practice', 'Practise counting tokens, pricing jobs and building message lists.',
        'Tokens, कीमत और message lists का अभ्यास।',
        'Tokens, ಬೆಲೆ, message lists ಅಭ್ಯಾಸ.',
        'Tokens, ମୂଲ୍ୟ ଓ message lists ଅଭ୍ୟାସ।',
        'تدرّب على حساب الرموز والكلفة وبناء قوائم الرسائل.',
        'Übe Tokens, Preise und Nachrichtenlisten.'),
]

QUIZ = [
    quiz('e', 'Where should your API key live?', ['In an environment variable', 'In the code', 'In the README', 'In a web page'], 0, 'Keep it secret.', 'The SDK reads ANTHROPIC_API_KEY.'),
    quiz('e', 'Which three fields does every messages.create call need?', ['model, max_tokens, messages', 'key, prompt, model', 'system, tools, model', 'model, temperature, user'], 0, 'Model, limit, conversation.', 'system and tools are optional.'),
    quiz('e', 'Does the API remember earlier calls?', ['No, send the history each time', 'Yes, for one hour', 'Yes, forever', 'Only with Opus'], 0, 'Stateless.', 'Your code keeps the history.'),
    quiz('m', 'stop_reason is max_tokens. What happened?', ['The answer was cut off', 'It finished normally', 'It wants a tool', 'It refused'], 0, 'It hit the limit.', 'Raise max_tokens or ask for less.'),
    quiz('m', 'Which model is cheapest for sorting thousands of short messages?', ['claude-haiku-5-5', 'claude-fable-5-1', 'claude-opus-5-5', 'claude-sonnet-5-5'], 0, 'High volume.', 'Haiku is built for fast, simple, high volume work.'),
    quiz('m', 'Why stream a long answer?', ['Show text sooner and avoid timeouts', 'It is cheaper', 'It is more accurate', 'It skips the key'], 0, 'Speed for the user.', 'Streaming sends text as it is written.'),
    quiz('h', 'What guarantees the reply is valid JSON in your shape?', ['output_config.format with a json_schema', 'Asking nicely', 'A higher max_tokens', 'Streaming'], 0, 'Structured outputs.', 'The schema constrains the output.'),
    quiz('h', 'What does cache_control on a long system block do?', ['Later calls read that prefix cheaply', 'Hides it from Claude', 'Saves it to disk', 'Deletes it after use'], 0, 'Prompt caching.', 'Cache reads cost a small fraction of normal input.'),
    quiz('x', 'Which errors does the SDK retry on its own?', ['429, 5xx and connection errors', '400 and 401', 'Only 404', 'None'], 0, 'Temporary ones.', 'Fix 400 and 401 yourself.'),
    quiz('x', 'Which effort value is best for a quick, simple extraction?', ['low', 'max', 'xhigh', 'high'], 0, 'Speed and cost.', 'Low effort answers faster and cheaper.'),
]

CALC = [
    calc('e', 'A call uses 2,000 input tokens on Sonnet 5.5 at $2 per million. Input cost in dollars?', '0.004', 'Tokens times price, divided by a million.', ['<span class="eq">2,000 × 2 ÷ 1,000,000 = 0.004</span>'], alt=['$0.004']),
    calc('e', 'It also writes 500 tokens at $10 per million. Output cost in dollars?', '0.005', 'Same formula.', ['<span class="eq">500 × 10 ÷ 1,000,000 = 0.005</span>'], alt=['$0.005']),
    calc('m', 'From the cost run, how many dollars a month does Haiku 5.5 cost for the ticket job?', '15', 'Read the output.', ['<span class="eq">2,000 × (1,500 × 0.10 + 200 × 0.50) ÷ 10⁶ × 30 = 15</span>'], alt=['$15']),
    calc('m', 'And Sonnet 5.5 for the same job, per month?', '300', 'Read the output.', ['<span class="eq">2,000 × (1,500 × 2 + 200 × 10) ÷ 10⁶ × 30 = 300</span>'], alt=['$300']),
    calc('h', 'In the tutor run, how many messages were in the last request?', '5', 'Read the last line.', ['Three child turns and two Pinky turns.']),
    calc('x', 'A 50,000 token policy is read 400 times a day on Opus 5.5. Saving per day with cache reads at $0.20 instead of $4 per million?', '76', 'Tokens per day × price difference.', ['<span class="eq">50,000 × 400 × (4 − 0.20) ÷ 10⁶ = 76</span>'], alt=['$76']),
]

EX = [
    ex('cost-of', 'e', 'Cost of one call', '<p>Write <code>cost(inTok, outTok, inPrice, outPrice)</code> that returns the dollar cost. Prices are per million tokens.</p>',
       'function cost(inTok, outTok, inPrice, outPrice) {\n  \n}\n',
       [('cost(2000, 500, 2, 10)', 0.009), ('cost(1000000, 0, 4, 20)', 4), ('cost(0, 1000000, 0.1, 0.5)', 0.5)],
       'function cost(inTok, outTok, inPrice, outPrice) {\n  return (inTok * inPrice + outTok * outPrice) / 1e6;\n}',
       hint='Add the two parts, then divide by a million.', why='Every model choice starts with this formula.'),
    ex('add-turn', 'm', 'Keep the history', '<p>Write <code>addTurn(history, role, text)</code> that returns a <b>new</b> array with <code>{ role, content: text }</code> added at the end. Do not change the original.</p>',
       'function addTurn(history, role, text) {\n  \n}\n',
       [('addTurn([], "user", "hi").length', 1), ('addTurn([{ role: "user", content: "hi" }], "assistant", "hello")[1].role', 'assistant'), ('(() => { const h = []; addTurn(h, "user", "x"); return h.length; })()', 0)],
       'function addTurn(history, role, text) {\n  return [...history, { role, content: text }];\n}',
       hint='Spread the old array into a new one.', why='Your code is the memory of the conversation.'),
    ex('pick-model', 'h', 'Pick a model', '<p>Write <code>pickModel(task)</code>. Return <code>"claude-haiku-5-5"</code> for <code>"classify"</code> and <code>"extract"</code>, <code>"claude-opus-5-5"</code> for <code>"agent"</code> and <code>"research"</code>, and <code>"claude-sonnet-5-5"</code> for anything else.</p>',
       'function pickModel(task) {\n  \n}\n',
       [('pickModel("classify")', 'claude-haiku-5-5'), ('pickModel("research")', 'claude-opus-5-5'), ('pickModel("chat")', 'claude-sonnet-5-5')],
       'function pickModel(task) {\n  if (["classify", "extract"].includes(task)) return "claude-haiku-5-5";\n  if (["agent", "research"].includes(task)) return "claude-opus-5-5";\n  return "claude-sonnet-5-5";\n}',
       hint='Two includes checks and a default.', why='Routing each step to the right model saves real money.'),
]

T = {
    'slug': 'claude-api', 'title': 'The Claude API Step by Step', 'short': 'Claude API', 'emoji': '🧩', 'module': MODULE, 'minutes': 20,
    'lead': 'Get a key and install the SDK, make your first call and read every field of the reply, build a tutor with a system prompt and chat history, choose a model and price a job, stream answers, get JSON in a fixed shape, use effort and prompt caching, and handle errors.',
    'plain': 'The API is a way for your own program to send Claude a message and get the answer back, the same as chatting, but from code.',
    'desc': 'Claude API tutorial with the Python SDK: API keys, messages.create, system prompts, conversation history, model choice and pricing, streaming, JSON structured outputs, effort, prompt caching and error handling.',
    'summary': 'API keys and SDK install, a first call with every response field explained plus TypeScript and curl versions, a tutor with a system prompt and history, models and prices with a cost run, streaming, json_schema outputs, effort and cache_control, and error codes with retries.',
    'keywords': ['Claude API', 'Messages API', 'anthropic', 'messages.create', 'system prompt', 'streaming', 'structured outputs', 'pricing', 'prompt caching', 'effort', 'errors'],
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
