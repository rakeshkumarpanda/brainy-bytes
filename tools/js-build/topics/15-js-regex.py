# Chapter 15: regular expressions in depth: matching engine, lookarounds, unicode, replacing, tokenising, ReDoS and testing patterns.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🔬', 'JavaScript in depth', 'js-depth', 'How the engine really works, errors and debugging, regular expressions, functional style, metaprogramming and Node.js in depth.')

CODES = {
    'greedy': run('''
const html = '<b>Sale</b> and <b>New</b>';

console.log(html.match(/<b>.*<\\/b>/)[0]);       // greedy: as much as possible
console.log(html.match(/<b>.*?<\\/b>/)[0]);      // lazy: as little as possible
console.log(html.match(/<b>[^<]*<\\/b>/g));      // a negated class is often clearer and faster

// The engine tries every start position, and backtracks inside each one
const re = /a.*c/;
console.log(re.exec("xxabcbc"), "| found at index", re.exec("xxabcbc").index);
''', 'Greedy, lazy and how the engine searches'),
    'lookaround': run('''
const prices = "Pen ₹40, Book ₹250, Bag $30, Mug ₹120";

console.log(prices.match(/(?<=₹)\\d+/g));             // lookbehind: digits after ₹, without the ₹
console.log(prices.match(/\\b\\w+(?= ₹)/g));          // lookahead: words followed by " ₹"
console.log(prices.match(/(?<!₹)\\b\\d+/g));          // negative lookbehind: numbers not in rupees

// Password rules as lookaheads: each (?=...) checks a rule without moving forward
const strong = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^\\w\\s]).{8,}$/;
for (const pw of ["Secret1!", "secret1!", "Sec1!", "Secret12"]) console.log(pw.padEnd(9), strong.test(pw));

// Backreferences: \\1 matches the same text the first group matched
console.log("the the test passed passed".match(/\\b(\\w+) \\1\\b/g));
console.log('<a href="x">'.match(/(["']).*?\\1/)[0]);
''', 'Lookahead, lookbehind and backreferences'),
    'flags': run('''
const log = `INFO  start
ERROR db timeout
info  retry
ERROR card declined`;

console.log(log.match(/^ERROR.*$/gm));                // m: ^ and $ work per line
console.log(log.match(/^info.*$/gim).length);          // i: ignore case
console.log(/start.ERROR/.test(log), /start.ERROR/s.test(log));   // s: dot matches a new line

// g with test() remembers lastIndex between calls, a classic bug
const hasError = /ERROR/g;
console.log(hasError.test(log), hasError.test(log), hasError.test(log), "| lastIndex", hasError.lastIndex);

// y (sticky) only matches exactly at lastIndex, which is how tokenisers work
const word = /\\w+/y;
word.lastIndex = 6;
console.log(word.exec(log)?.[0], (word.lastIndex = 5, word.exec(log)));
''', 'Flags in depth: g, m, s, y and the lastIndex trap'),
    'unicode': run('''
const names = ["Zoë", "Ravi", "José", "Łukasz", "東京", "😀 smile"];

console.log(names.filter(n => /^[a-z]+$/i.test(n)));          // ASCII only: drops real names
console.log(names.filter(n => /^\\p{L}+$/u.test(n)));         // any letter in any script
console.log("😀".length, [..."😀"].length, /^.$/.test("😀"), /^.$/u.test("😀"));
console.log("Grüße, Привет, नमस्ते".match(/\\p{Script=Devanagari}+/u)[0]);
console.log("café".normalize("NFD").replace(/\\p{M}/gu, ""));  // strip accents
''', 'Unicode: letters in every language'),
    'replace': run('''
// Replace with named groups and with a function
const iso = "Shipped 2026-10-18, due 2026-10-25";
console.log(iso.replace(/(?<y>\\d{4})-(?<m>\\d\\d)-(?<d>\\d\\d)/g, "$<d>/$<m>/$<y>"));

const cart = "PEN x2 @40, BOOK x1 @250";
console.log(cart.replace(/(\\w+) x(\\d+) @(\\d+)/g, (all, sku, qty, price) => `${sku}=${qty * price}`));

// Mask secrets in logs before they are saved
const line = 'POST /login {"user":"asha","password":"s3cret","card":"4111111111111111"} token=eyJhbGciOi.abc.def';
const masked = line
  .replace(/("password":")[^"]*/, "$1***")
  .replace(/\\b(\\d{4})\\d{8}(\\d{4})\\b/, "$1********$2")
  .replace(/token=[\\w.-]+/, "token=[hidden]");
console.log(masked);

// split keeps captured separators
console.log("a1b22c333".split(/(\\d+)/));
''', 'Replacing with groups and functions, masking secrets'),
    'tokenize': run('''
// A tiny tokeniser for filter expressions such as: status == "failed" && ms > 1000
const rules = [
  ["space", /\\s+/y], ["string", /"(?:[^"\\\\]|\\\\.)*"/y], ["number", /\\d+(?:\\.\\d+)?/y],
  ["op", /==|!=|>=|<=|&&|\\|\\||[<>!]/y], ["name", /[A-Za-z_]\\w*/y], ["paren", /[()]/y],
];

function tokenize(src) {
  const out = [];
  let pos = 0;
  outer: while (pos < src.length) {
    for (const [type, re] of rules) {
      re.lastIndex = pos;
      const m = re.exec(src);
      if (m) {
        if (type !== "space") out.push(`${type}:${m[0]}`);
        pos = re.lastIndex;
        continue outer;
      }
    }
    throw new SyntaxError(`Unexpected "${src[pos]}" at ${pos}`);
  }
  return out;
}
console.log(tokenize('status == "failed" && ms > 1000'));
try { tokenize("ms # 2"); } catch (e) { console.log(e.message); }
''', 'Sticky regexes as a tokeniser'),
    'redos': run('''
// Catastrophic backtracking: nested quantifiers try every way to split the input
const evil = /^(a+)+$/;
const safe = /^a+$/;

function time(re, n) {
  const input = "a".repeat(n) + "!";                  // the ! forces a failure at the end
  const start = performance.now();
  re.test(input);
  return performance.now() - start;
}

time(evil, 5);                                        // warm up, so compiling the regex is not measured
const t22 = time(evil, 22), t26 = time(evil, 26);
console.log("4 more characters made it more than 5 times slower:", t26 / t22 > 5);
console.log("the safe pattern on 100000 characters is instant:", time(safe, 100_000) < 50);
''', 'ReDoS: a pattern that takes forever'),
    'validate': run('''
// Practical patterns. Each one is a trade off, write tests that show the choice.
const patterns = {
  email: /^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/,             // pragmatic, not the full RFC 5322
  isoDate: /^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$/, // shape only: 2026-02-31 passes
  uuid: /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
  indianPin: /^[1-9]\\d{5}$/,
  semver: /^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-[\\w.-]+)?$/,
};
const samples = {
  email: ["asha@example.com", "a@b", "no spaces@x.io"],
  isoDate: ["2026-10-20", "2026-13-01", "2026-02-31"],
  uuid: [crypto.randomUUID(), "1234"],
  indianPin: ["560001", "056001"],
  semver: ["1.56.1", "1.02.0", "2.0.0-rc.1"],
};
for (const [name, list] of Object.entries(samples))
  console.log(name.padEnd(9), list.map(s => patterns[name].test(s)).join(" "));
''', 'Validation patterns and their limits'),
    'regex-tests': test({
        'package.json': pkg('patterns', 'module'),
        'src/patterns.js': '''
export const orderId = /^ORD-\\d{6}$/;
export const price = /^₹(?:0|[1-9]\\d{0,2}(?:,\\d{3})*|[1-9]\\d*)(?:\\.\\d{2})?$/;
''',
        'test/patterns.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { orderId, price } from "../src/patterns.js";

// A table of examples that must match and examples that must not
const cases = {
  orderId: { yes: ["ORD-000001", "ORD-104233"], no: ["ord-104233", "ORD-10423", "ORD-1042333", " ORD-104233"] },
  price: { yes: ["₹0", "₹40", "₹1,250", "₹12,500", "₹99.50"], no: ["₹040", "₹1,25", "₹9.5", "40", "₹-5"] },
};

for (const [name, { yes, no }] of Object.entries(cases)) {
  const re = { orderId, price }[name];
  for (const s of yes) test(`${name} accepts ${JSON.stringify(s)}`, () => assert.match(s, re));
  for (const s of no) test(`${name} rejects ${JSON.stringify(s)}`, () => assert.doesNotMatch(s, re));
}
''',
    }, 'node --test --test-reporter=spec', 'Test a regex with a table of cases', show=['src/patterns.js', 'test/patterns.test.js'],
        replace=[(r' \([\d.]+ms\)', ''), (r'ℹ duration_ms [\d.]+', 'ℹ duration_ms 41.2')]),
    'scenario': run('''
// Turn raw access log lines into rows you can check
const logs = `203.0.113.9 - - [20/Oct/2026:09:14:03 +0000] "GET /api/products?page=2 HTTP/1.1" 200 5123 412ms
203.0.113.9 - - [20/Oct/2026:09:14:04 +0000] "POST /api/orders HTTP/1.1" 503 87 2210ms
198.51.100.4 - - [20/Oct/2026:09:14:05 +0000] "GET /health HTTP/1.1" 200 2 3ms
198.51.100.4 - - [20/Oct/2026:09:14:07 +0000] "POST /api/orders HTTP/1.1" 201 312 640ms
garbage line`;

const LINE = /^(?<ip>\\S+) \\S+ \\S+ \\[(?<time>[^\\]]+)\\] "(?<method>[A-Z]+) (?<path>[^ ?"]+)(?:\\?[^ "]*)? HTTP\\/[\\d.]+" (?<status>\\d{3}) (?<bytes>\\d+) (?<ms>\\d+)ms$/;

const rows = [], bad = [];
for (const line of logs.split("\\n")) {
  const m = LINE.exec(line);
  if (m) rows.push({ ...m.groups, status: +m.groups.status, ms: +m.groups.ms });
  else bad.push(line);
}
const errors = rows.filter(r => r.status >= 500);
const slow = rows.filter(r => r.ms > 1000 && r.path !== "/health");
console.log(rows.length, "parsed,", bad.length, "rejected:", bad);
console.log("5xx:", errors.map(r => `${r.method} ${r.path} at ${r.time.split(":").slice(1, 4).join(":")}`));
console.log("slow:", slow.map(r => `${r.path} ${r.ms}ms`), "| p50 of orders:", rows.filter(r => r.path === "/api/orders").map(r => r.ms).toSorted((a, b) => a - b)[0], "ms");
''', 'Parse access logs and find the failures'),
}

PARTS = [
    part('engine', '⚙️', 'How the regex engine matches', '''
<p>JavaScript uses a <b>backtracking</b> engine. It tries the pattern at the first position of the text and, when a step fails, goes back to the last choice it made and tries another. If nothing works, it moves one character on and starts again. Quantifiers are <b>greedy</b> by default: they take as much as they can, then give back. Add <code>?</code> to make them <b>lazy</b>.</p>
<div class="viz" data-viz="regex"></div>
[[greedy]]
<div class="tip">When you can say exactly what is allowed, a negated class such as <code>[^&lt;]*</code> or <code>[^"]*</code> is clearer and much faster than <code>.*?</code>, because the engine never needs to backtrack.</div>
''', kw=['regex engine', 'backtracking', 'greedy', 'lazy', 'non greedy', '.*?', 'negated character class', 'match position']),
    part('lookaround', '👀', 'Lookarounds and backreferences', '''
<p>A <b>lookaround</b> checks what comes before or after a position without including it in the match. <code>(?=x)</code> and <code>(?!x)</code> look ahead, <code>(?&lt;=x)</code> and <code>(?&lt;!x)</code> look behind. A <b>backreference</b> such as <code>\\1</code> or <code>\\k&lt;name&gt;</code> matches the same text a group already matched.</p>
[[lookaround]]
<div class="qa-box">Several lookaheads in a row are the standard way to express "must contain a lower case letter, a capital, a digit and a symbol". Each rule becomes a separate test case in your password suite.</div>
''', qa=True, qa_why='Password rules, price extraction and duplicate word checks in content are everyday test tasks.',
        kw=['lookahead', 'lookbehind', 'negative lookahead', 'negative lookbehind', 'backreference', 'password regex', '\\1', '\\k']),
    part('flags', '🚩', 'Flags in depth and the lastIndex trap', '''
<p>Flags change how the whole pattern works. The <code>g</code> and <code>y</code> flags also make a regex <b>stateful</b>: it remembers <code>lastIndex</code>, the position after the last match.</p>
[[flags]]
<div class="warn">Never reuse a regex with the <code>g</code> flag for <code>test()</code> across different strings or calls. The second call starts at the old <code>lastIndex</code> and can fail on text that clearly matches. Drop the <code>g</code> flag for yes or no checks.</div>
''', qa=True, qa_why='A shared /g regex in a test helper makes checks pass and fail in turn, a confusing source of flaky tests.',
        kw=['g flag', 'm flag', 'multiline', 's flag', 'dotAll', 'y flag', 'sticky', 'i flag', 'lastIndex', 'stateful regex']),
    part('unicode', '🌍', 'Unicode and every language', '''
<p><code>[a-z]</code> only knows English. With the <code>u</code> or <code>v</code> flag, <code>\\p{L}</code> matches a letter in any script, <code>\\p{Script=Devanagari}</code> one script, and <code>\\p{Emoji}</code> emoji. The <code>u</code> flag also treats an emoji as one character instead of two halves.</p>
[[unicode]]
<div class="qa-box">Test name and address fields with names such as Zoë, José, Łukasz, 東京 and right to left Arabic. A form that rejects real names is a bug that hits real customers.</div>
''', qa=True, qa_why='Internationalisation testing catches validation that only works for English input.',
        kw=['unicode', 'u flag', 'v flag', '\\p{L}', 'Unicode property escapes', 'Script', 'emoji', 'normalize', 'NFD', 'accents', 'i18n testing']),
    part('replace', '✂️', 'Replacing, masking and splitting', '''
<p><code>replace</code> and <code>replaceAll</code> can use <code>$1</code>, <code>$&lt;name&gt;</code> and <code>$&amp;</code> in the replacement text, or a function that receives every group and returns the new text.</p>
[[replace]]
<p>For anything with structure, such as a whole language of filters, use the sticky flag to read one token at a time from an exact position.</p>
[[tokenize]]
''', qa=True, qa_why='Masking passwords, card numbers and tokens before logs and reports are saved is a security requirement in test frameworks.',
        kw=['replace', 'replaceAll', 'replace function', '$1', '$<name>', 'masking', 'PII', 'split', 'tokenizer', 'sticky', 'lexer']),
    part('redos', '💣', 'ReDoS and safe patterns', '''
<p>Some patterns make the engine try an exponential number of ways to split the input. <code>^(a+)+$</code> on a long run of "a" that ends with "!" never finishes in practice. An attacker who can send such input to a server can freeze it with one request. This is called <b>regular expression denial of service</b>.</p>
[[redos]]
<div class="warn">Danger signs: a quantifier inside a quantified group, such as <code>(a+)+</code>, <code>(\\w*)*</code> or <code>(a|aa)+</code>. Safe habits: limit input length first, prefer specific classes, and run the linter rule <code>regexp/no-super-linear-backtracking</code> from eslint-plugin-regexp.</div>
''', qa=True, qa_why='Sending long crafted strings to search and validation fields is a standard security and performance test.',
        kw=['ReDoS', 'catastrophic backtracking', 'nested quantifier', 'denial of service', 'exponential', 'eslint-plugin-regexp', 'input length limit']),
    part('validate', '✅', 'Validation patterns and testing them', '''
<p>A regex can check the <b>shape</b> of text, not its meaning. A date pattern accepts 31 February, and no practical email pattern follows the full standard. Use a regex for the shape, then real code for the rest, such as <code>Temporal.PlainDate.from</code> for dates.</p>
[[validate]]
<p>Treat a regex like any other code: keep it in one module and test it with a table of strings that must match and strings that must not.</p>
[[regex-tests]]
''', qa=True, qa_why='Regex validation rules are a frequent source of bugs, and table driven tests show exactly which inputs they accept.',
        kw=['validation', 'email regex', 'date regex', 'UUID regex', 'PIN code', 'semver regex', 'assert.match', 'table driven tests', 'boundary cases']),
    part('scenario', '🎬', 'Real world scenario: mine the access logs', '''
<div class="scenario"><b>The situation</b>After a load test, the team wants every failed request and every slow one from the server access log, with the time of each.</div>
[[scenario]]
<p>One pattern with named groups turns each line into an object. Lines that do not match are counted instead of silently dropped, which tells you when the log format changes. The same idea works for test runner output, browser console logs and CI logs.</p>
''', qa=True, kw=['log parsing', 'access log', 'named groups', 'load test', '5xx errors', 'slow requests', 'performance analysis']),
]

INFO = {'title': 'Patterns with power', 'panels': [
    panel([['e', '⚙️'], ['t', '.*  vs  .*?', {'b': 1}]], 'Greedy or lazy', 'The engine backtracks to find a match.', 'Negated classes avoid the work.'),
    panel([['e', '👀'], ['t', '(?=.*\\d)(?=.*[A-Z])', {'b': 1, 'size': 11}]], 'Lookarounds', 'Check without consuming.', 'Ideal for password rules.'),
    panel([['e', '🌍'], ['t', '/\\p{L}+/u', {'b': 1}]], 'Every language', 'Letters in any script.', 'Real names pass.'),
    panel([['e', '💣'], ['t', '(a+)+', {'b': 1}]], 'Beware ReDoS', 'Nested quantifiers explode.', 'Limit input and lint patterns.')],
    'remember': 'Know how the engine backtracks, drop g for yes or no checks, use \\p{L} for names, and test every pattern with a table of cases.'}

REAL = [
    ['🧑\u200d🤝\u200d🧑', 'A sign up form', 'Rejected the name "Zoë" because its pattern was [A-Za-z]+. QA added names from twelve languages to the test data and the pattern became \\p{L}.'],
    ['🔥', 'A web API outage', 'Was caused by a regex with nested quantifiers in a user agent check. One long header froze every worker for minutes.'],
    ['🧾', 'A test reporting tool', 'Masks passwords, card numbers and tokens with three replace calls before any log is uploaded to the dashboard.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter goes deep into regular expressions: how the engine backtracks, lookarounds, flags, unicode, replacing, tokenising, ReDoS and testing patterns.',
        'यह अध्याय regular expressions में गहराई से जाता है: engine backtracking, lookarounds, flags, unicode, replace, tokenising, ReDoS और patterns की testing।',
        'ಈ ಅಧ್ಯಾಯ regular expressions ಆಳವಾಗಿ: backtracking, lookarounds, flags, unicode, replace, ReDoS ಮತ್ತು testing.',
        'ଏହି ଅଧ୍ୟାୟ regular expressions ଗଭୀରରେ: backtracking, lookarounds, flags, unicode, replace, ReDoS ଓ testing।',
        'يتعمق هذا الفصل في التعابير النمطية: التراجع في المحرك والنظر حول الموضع والأعلام ويونيكود والاستبدال وهجمات ReDoS واختبار الأنماط.',
        'Dieses Kapitel geht tief in reguläre Ausdrücke: Backtracking, Lookarounds, Flags, Unicode, Ersetzen, ReDoS und Tests.'),
    say('engine', 'The engine', 'The engine tries the pattern at each position and backtracks when a step fails. Greedy takes as much as it can, lazy as little as it can.',
        'Engine हर position पर pattern आज़माता है और step fail होने पर पीछे जाता है। Greedy ज़्यादा लेता है, lazy कम।',
        'Engine ಪ್ರತಿ position ನಲ್ಲಿ pattern ಪ್ರಯತ್ನಿಸಿ ವಿಫಲವಾದರೆ ಹಿಂದೆ ಹೋಗುತ್ತದೆ. Greedy ಹೆಚ್ಚು, lazy ಕಡಿಮೆ.',
        'Engine ପ୍ରତି position ରେ pattern ଚେଷ୍ଟା କରେ, ବିଫଳ ହେଲେ ପଛକୁ ଯାଏ। Greedy ଅଧିକ, lazy କମ୍।',
        'يجرب المحرك النمط عند كل موضع ويتراجع عند فشل خطوة. الجشع يأخذ أكثر ما يمكن والكسول أقل ما يمكن.',
        'Die Engine probiert das Muster an jeder Stelle und geht bei Fehlern zurück. Gierig nimmt viel, faul wenig.'),
    say('lookaround', 'Lookarounds', 'Lookaheads and lookbehinds check text around a position without taking it. Backreferences match the same text again.',
        'Lookaheads और lookbehinds position के आसपास का text बिना लिए जांचते हैं। Backreferences वही text दोबारा मिलाते हैं।',
        'Lookaheads ಮತ್ತು lookbehinds ಸುತ್ತಲಿನ text ಪರಿಶೀಲಿಸುತ್ತವೆ. Backreferences ಅದೇ text ಮತ್ತೆ ಹೊಂದಿಸುತ್ತವೆ.',
        'Lookaheads ଓ lookbehinds ଚାରିପାଖ text ଯାଞ୍ଚ କରନ୍ତି। Backreferences ସେହି text ପୁଣି ମେଳାଏ।',
        'تتحقق النظرات الأمامية والخلفية من النص حول الموضع دون أخذه، وتطابق المراجع الخلفية النص نفسه مرة أخرى.',
        'Lookaheads und Lookbehinds prüfen den Text um eine Stelle, ohne ihn zu nehmen. Rückverweise finden denselben Text erneut.'),
    say('flags', 'Flags', 'The m flag works per line, s lets the dot match new lines, and g and y remember lastIndex. Drop g for yes or no checks.',
        'm flag हर line पर, s dot को new line तक, और g व y lastIndex याद रखते हैं। हां या ना checks के लिए g हटाएं।',
        'm flag ಪ್ರತಿ ಸಾಲಿಗೆ, s dot ಗೆ new line, g ಮತ್ತು y lastIndex ನೆನಪಿಡುತ್ತವೆ.',
        'm flag ପ୍ରତି ଧାଡ଼ିରେ, s dot କୁ new line, g ଓ y lastIndex ମନେ ରଖନ୍ତି।',
        'يعمل العلم m لكل سطر، ويجعل s النقطة تطابق السطر الجديد، ويتذكر g وy قيمة lastIndex. أزل g في فحوص نعم أو لا.',
        'Das m-Flag wirkt pro Zeile, s lässt den Punkt Zeilenumbrüche finden, g und y merken sich lastIndex.'),
    say('unicode', 'Unicode', 'With the u flag, p L matches a letter in any language and an emoji counts as one character.',
        'u flag के साथ p L किसी भी भाषा का अक्षर मिलाता है और emoji एक character गिना जाता है।',
        'u flag ಜೊತೆ p L ಯಾವುದೇ ಭಾಷೆಯ ಅಕ್ಷರ ಹೊಂದಿಸುತ್ತದೆ, emoji ಒಂದು character.',
        'u flag ସହ p L ଯେକୌଣସି ଭାଷାର ଅକ୍ଷର ମେଳାଏ, emoji ଗୋଟିଏ character।',
        'مع العلم u يطابق p L حرفًا من أي لغة ويُعد الرمز التعبيري حرفًا واحدًا.',
        'Mit dem u-Flag findet p L einen Buchstaben jeder Sprache, und ein Emoji zählt als ein Zeichen.'),
    say('replace', 'Replace', 'replace can use group numbers, group names or a function. Use it to mask passwords and card numbers, and use sticky patterns to read tokens.',
        'replace group numbers, names या function इस्तेमाल कर सकता है। Passwords और card numbers छिपाने के लिए इसका उपयोग करें।',
        'replace group numbers, names ಅಥವಾ function ಬಳಸಬಹುದು. Passwords ಮತ್ತು card numbers ಮರೆಮಾಡಲು ಬಳಸಿ.',
        'replace group numbers, names କିମ୍ବା function ବ୍ୟବହାର କରିପାରେ। Passwords ଓ card numbers ଲୁଚାନ୍ତୁ।',
        'يمكن لـ replace استخدام أرقام المجموعات أو أسمائها أو دالة. استخدمه لإخفاء كلمات المرور وأرقام البطاقات.',
        'replace kann Gruppennummern, Namen oder eine Funktion nutzen. Damit maskierst du Passwörter und Kartennummern.'),
    say('redos', 'ReDoS', 'Nested quantifiers can make matching take exponential time. Limit input length, prefer specific classes and lint your patterns.',
        'Nested quantifiers matching को exponential समय तक ले जा सकते हैं। Input की लंबाई सीमित करें और patterns को lint करें।',
        'Nested quantifiers exponential ಸಮಯ ತೆಗೆದುಕೊಳ್ಳಬಹುದು. Input ಉದ್ದ ಮಿತಿಗೊಳಿಸಿ, patterns lint ಮಾಡಿ.',
        'Nested quantifiers exponential ସମୟ ନେଇପାରେ। Input ଲମ୍ବ ସୀମିତ କରନ୍ତୁ, patterns lint କରନ୍ତୁ।',
        'قد تجعل المكممات المتداخلة المطابقة تستغرق وقتًا أسيًا. حدد طول المدخلات وافحص أنماطك بأداة فحص.',
        'Verschachtelte Quantoren können exponentiell lange brauchen. Begrenze die Eingabe und prüfe Muster mit einem Linter.'),
    say('validate', 'Validation', 'A regex checks the shape of text, not its meaning. Keep patterns in one module and test them with tables of matching and non matching strings.',
        'Regex text का आकार जांचता है, अर्थ नहीं। Patterns एक module में रखें और matching व non matching strings की tables से test करें।',
        'Regex text ನ ಆಕಾರ ಪರಿಶೀಲಿಸುತ್ತದೆ, ಅರ್ಥವಲ್ಲ. Patterns ಅನ್ನು tables ನಿಂದ test ಮಾಡಿ.',
        'Regex text ର ଆକାର ଯାଞ୍ଚ କରେ, ଅର୍ଥ ନୁହେଁ। Patterns କୁ tables ରେ test କରନ୍ତୁ।',
        'يتحقق التعبير النمطي من شكل النص لا معناه. احفظ الأنماط في وحدة واحدة واختبرها بجداول من النصوص المطابقة وغير المطابقة.',
        'Ein Regex prüft die Form, nicht die Bedeutung. Teste Muster mit Tabellen passender und unpassender Texte.'),
    say('scenario', 'Scenario', 'One pattern with named groups turns each log line into an object, so failed and slow requests are easy to list.',
        'Named groups वाला एक pattern हर log line को object बना देता है, जिससे failed और slow requests आसानी से मिलते हैं।',
        'Named groups ಇರುವ pattern ಪ್ರತಿ log line ಅನ್ನು object ಮಾಡುತ್ತದೆ.',
        'Named groups ଥିବା pattern ପ୍ରତି log line କୁ object କରେ।',
        'نمط واحد بمجموعات مسماة يحول كل سطر سجل إلى كائن، فيسهل سرد الطلبات الفاشلة والبطيئة.',
        'Ein Muster mit benannten Gruppen macht aus jeder Logzeile ein Objekt, so findest du fehlerhafte und langsame Anfragen.'),
    say('practice', 'Hands-on', 'Practise extracting prices, a password policy with lookaheads, masking card numbers, and parsing key value pairs.',
        'Prices निकालना, lookaheads से password policy, card numbers छिपाना और key value pairs parse करने का अभ्यास करें।',
        'Prices ತೆಗೆಯುವುದು, password policy, card numbers ಮರೆಮಾಡುವುದು ಮತ್ತು key value pairs ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Prices ବାହାର କରିବା, password policy, card numbers ଲୁଚାଇବା ଓ key value pairs ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على استخراج الأسعار وسياسة كلمة مرور بالنظر الأمامي وإخفاء أرقام البطاقات وتحليل أزواج المفتاح والقيمة.',
        'Übe Preise auslesen, eine Passwortregel mit Lookaheads, Kartennummern maskieren und Schlüssel-Wert-Paare lesen.'),
]

QUIZ = [
    quiz('e', 'What does the lazy pattern match?', ['&lt;b&gt;A&lt;/b&gt;', '&lt;b&gt;A&lt;/b&gt;&lt;b&gt;B&lt;/b&gt;', 'A', 'Nothing'], 0, 'Lazy.', 'The ? after * stops at the first closing tag.', code='"<b>A</b><b>B</b>".match(/<b>.*?<\\/b>/)[0];'),
    quiz('e', 'Which flag makes ^ and $ work on every line?', ['m', 's', 'g', 'y'], 0, 'Multiline.', 's is for the dot, g for all matches.'),
    quiz('e', 'Which pattern matches a letter in any language?', ['/\\p{L}/u', '/[a-z]/i', '/\\w/', '/./'], 0, 'Unicode property.', '\\w only covers A to Z, digits and underscore.'),
    quiz('m', 'What does (?<=₹)\\d+ return from "₹40"?', ['40', '₹40', '₹', 'Nothing'], 0, 'Lookbehind does not consume.', 'The ₹ is checked but left out of the match.'),
    quiz('m', 'Why can calling test() twice on the same /x/g regex give different results?', ['It remembers lastIndex between calls', 'Regexes are random', 'test() changes the string', 'The g flag is ignored'], 0, 'State.', 'Drop g for yes or no checks, or reset lastIndex.'),
    quiz('m', 'What does \\1 mean in /(\\w+) \\1/?', ['The same text that group 1 matched', 'The digit 1', 'Group 1 again as a pattern', 'One repetition'], 0, 'Backreference.', 'It finds repeated words such as "the the".'),
    quiz('m', 'In replace(re, fn), what does fn receive after the full match?', ['Each captured group in order', 'Only the index', 'Nothing', 'The flags'], 0, 'Groups first.', 'Then the offset, the whole string and the named groups object.'),
    quiz('h', 'Which pattern is at risk of catastrophic backtracking?', ['/^(a+)+$/', '/^a+$/', '/^[a-z]{3}$/', '/^\\d{6}$/'], 0, 'Nested quantifier.', 'The engine tries every way to split the run of a characters.'),
    quiz('h', 'What does the y flag do?', ['Matches only exactly at lastIndex', 'Ignores case', 'Matches all occurrences', 'Allows lookbehind'], 0, 'Sticky.', 'That is how tokenisers read one token at a time.'),
    quiz('h', 'An ISO date regex accepts 2026-02-31. What is the right fix?', ['Check the shape with the regex, then parse the date with real code', 'Write a longer regex for every month', 'Remove the check', 'Use the s flag'], 0, 'Shape against meaning.', 'Temporal.PlainDate.from rejects 31 February.'),
    quiz('x', 'Why is "😀".length 2?', ['Strings count UTF-16 code units, and this emoji needs two', 'Emoji are two characters', 'A bug in V8', 'Because of the u flag'], 0, 'Surrogate pairs.', 'Spread or the u flag count code points instead.'),
    quiz('x', 'What does "a1b22".split(/(\\d+)/) return?', ['["a", "1", "b", "22", ""]', '["a", "b"]', '["a1", "b22"]', '["1", "22"]'], 0, 'Captured separators stay.', 'A capture group in split keeps the separators in the result.'),
]

CALC = [
    calc('e', 'How many matches does /\\d+/g find in "PEN 2, BOOK 10, BAG 3"?', '3', 'Runs of digits.', ['2, 10 and 3.']),
    calc('e', '/^\\d{6}$/ accepts PIN codes. How many digits must the input have?', '6', 'Exactly.', ['{6} means exactly six, and ^ $ forbid anything else.']),
    calc('m', 'How many strings of only "a" and "b" of length 3 does /^[ab]{3}$/ accept?', '8', 'Two choices per position.', ['<span class="eq">2<sup>3</sup> = 8</span>']),
    calc('m', 'A password must have 4 kinds of character. A test suite checks each missing kind once, plus one valid password and one too short. How many cases?', '6', 'One per rule plus two.', ['<span class="eq">4 + 1 + 1 = 6</span>']),
    calc('m', 'A card number 4111111111111111 is masked to keep the first 4 and last 4 digits. How many asterisks?', '8', '16 digits in total.', ['<span class="eq">16 − 4 − 4 = 8</span>']),
    calc('h', 'With ^(a+)+$, the number of ways to split n letters doubles with each extra letter. Going from 22 to 26 letters multiplies the work by how much?', '16', 'Four doublings.', ['<span class="eq">2<sup>4</sup> = 16</span>']),
    calc('h', 'In the log scenario, how many of the 5 lines failed to match the pattern?', '1', 'Only the garbage line.', ['Four real log lines parsed, one rejected.']),
    calc('x', 'A tokeniser reads status == "failed" && ms > 1000 and skips spaces. How many tokens does it produce?', '7', 'Count names, operators, values.', ['status, ==, "failed", &&, ms, >, 1000.']),
]

EX = [
    ex('prices', 'e', 'Extract rupee prices', '<p>Write <code>rupees(text)</code> that returns every rupee amount in the text as numbers. Amounts look like <code>₹40</code> or <code>₹1,250</code>. Ignore amounts in other currencies.</p>',
       'function rupees(text) {\n  \n}\n',
       [('rupees("Pen ₹40, Bag $30, Book ₹1,250")', [40, 1250]), ('rupees("no prices")', [])],
       'function rupees(text) {\n  return [...text.matchAll(/₹([\\d,]+)/g)].map(m => Number(m[1].replaceAll(",", "")));\n}', hint='<code>matchAll</code> with a group for the digits and commas, then remove the commas.', why='matchAll returns an iterator, and spreading it gives every match with its groups.'),
    ex('policy', 'm', 'A password policy', '<p>Write <code>isStrong(pw)</code> that returns true when the password has at least 8 characters, a lower case letter, a capital, a digit and a symbol (anything that is not a letter, digit or space).</p>',
       'function isStrong(pw) {\n  \n}\n',
       [('isStrong("Secret1!")', True), ('isStrong("secret1!")', False), ('isStrong("SECRET1!")', False), ('isStrong("Secret!!")', False), ('isStrong("Secret12")', False), ('isStrong("Se1!")', False)],
       'function isStrong(pw) {\n  return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^\\w\\s]).{8,}$/.test(pw);\n}', hint='One lookahead per rule, then <code>.{8,}</code> for the length.', why='Each failing test in the list misses exactly one rule, which is how you design a password test suite.'),
    ex('mask', 'h', 'Mask card numbers', '<p>Write <code>maskCards(text)</code> that replaces every run of 13 to 19 digits with the first 4 digits, then one <code>*</code> per hidden digit, then the last 4 digits. Leave shorter numbers alone.</p>',
       'function maskCards(text) {\n  \n}\n',
       [('maskCards("card 4111111111111111 ok")', 'card 4111********1111 ok'), ('maskCards("order 1042 and 1234567890123")', 'order 1042 and 1234*****0123'), ('maskCards("none")', 'none')],
       'function maskCards(text) {\n  return text.replace(/\\b(\\d{4})(\\d{5,11})(\\d{4})\\b/g, (all, a, mid, b) => a + "*".repeat(mid.length) + b);\n}', hint='Three groups: 4 digits, the middle, 4 digits. A replace function can count the middle.', why='A function replacement is the only way to make the number of stars depend on the input.'),
    ex('kv', 'x', 'Parse key=value pairs', '<p>Write <code>parsePairs(text)</code> that reads pairs such as <code>env=staging retries=2 name="smoke run"</code> into an object. Values in double quotes may contain spaces. Values that are whole numbers become numbers.</p>',
       'function parsePairs(text) {\n  \n}\n',
       [('parsePairs(\'env=staging retries=2 name="smoke run"\')', {'env': 'staging', 'retries': 2, 'name': 'smoke run'}), ('parsePairs("")', {}), ('parsePairs(\'a="1"\')', {'a': 1})],
       'function parsePairs(text) {\n  const out = {};\n  for (const m of text.matchAll(/(\\w+)=(?:"([^"]*)"|(\\S+))/g)) {\n    const raw = m[2] ?? m[3];\n    out[m[1]] = /^-?\\d+$/.test(raw) ? Number(raw) : raw;\n  }\n  return out;\n}',
       hint='An alternation: a quoted value <code>"([^"]*)"</code> or a plain one <code>(\\S+)</code>. Only one of the two groups is filled.', why='CLI flags, test tags and environment strings all use this format.'),
]

T = {
    'slug': 'js-regex', 'title': 'Regular expressions in depth', 'short': 'Regex in depth', 'emoji': '🧷', 'module': MODULE, 'minutes': 18,
    'lead': 'Go beyond the basics of chapter 6: how the backtracking engine finds a match, greedy and lazy quantifiers, lookarounds and backreferences, every flag and the lastIndex trap, unicode letters in every language, replacing and masking, a sticky tokeniser, ReDoS, and testing patterns with tables.',
    'desc': 'JavaScript regex in depth: backtracking, greedy and lazy, lookahead, lookbehind, backreferences, flags g m s y u v, lastIndex, unicode property escapes, replace with functions, masking, tokenizer, ReDoS and testing regular expressions.',
    'summary': 'How the backtracking engine matches, greedy against lazy, lookarounds for password rules and backreferences, the m, s, g and y flags and the lastIndex trap, unicode letters and emoji, replacing with groups and functions to mask secrets, a sticky tokeniser, catastrophic backtracking, validation patterns with table driven tests, and parsing access logs.',
    'keywords': ['regex', 'regular expressions', 'backtracking', 'lazy quantifier', 'lookahead', 'lookbehind', 'backreference', 'lastIndex', 'unicode regex', 'replace function', 'masking', 'tokenizer', 'ReDoS', 'validation', 'log parsing', 'interview'],
    'qa_intro': 'Regular expressions check text in assertions, extract ids from pages and logs, mask secrets in reports and find bugs in validation rules. This chapter makes you fluent and safe with them.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
