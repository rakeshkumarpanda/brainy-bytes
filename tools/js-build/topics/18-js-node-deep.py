# Chapter 18: Node.js in depth: events, streams and backpressure, buffers and crypto, the built in SQLite database, processes and signals, and command line tools.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🔬', 'JavaScript in depth', 'js-depth', 'How the engine really works, errors and debugging, regular expressions, functional style, metaprogramming and Node.js in depth.')

CODES = {
    'events': run('''
import { EventEmitter, once, on } from "node:events";

// A tiny test runner that reports progress with events
class Runner extends EventEmitter {
  async run(tests) {
    this.emit("start", tests.length);
    for (const [name, fn] of tests) {
      try { await fn(); this.emit("pass", name); }
      catch (e) { this.emit("fail", name, e.message); }
    }
    this.emit("end");
  }
}

const runner = new Runner();
let passed = 0;
runner.on("start", n => console.log(`running ${n} tests`));
runner.on("pass", () => passed++);
runner.on("fail", (name, msg) => console.log(`✖ ${name}: ${msg}`));
runner.once("end", () => console.log(`${passed} passed`));

const finished = once(runner, "end");               // a promise for one event
await runner.run([["login", async () => {}], ["cart", async () => { throw new Error("expected 2, got 3"); }], ["search", async () => {}]]);
await finished;

// An "error" event with no listener throws, so always listen for it
try { new EventEmitter().emit("error", new Error("socket closed")); } catch (e) { console.log("unhandled error event:", e.message); }

// Events as an async iterator, stopped by an AbortSignal
const ticker = new EventEmitter(), ac = new AbortController();
setTimeout(() => { ticker.emit("tick", 1); ticker.emit("tick", 2); ac.abort(); }, 5);
try { for await (const [n] of on(ticker, "tick", { signal: ac.signal })) console.log("tick", n); }
catch (e) { console.log("stopped:", e.name); }
''', 'EventEmitter: on, once, error and async iteration'),
    'streams': run('''
import { Readable, Transform, Writable } from "node:stream";
import { pipeline } from "node:stream/promises";
import { createWriteStream, createReadStream } from "node:fs";
import { createInterface } from "node:readline";

// 1. Generate a large log file without holding it in memory
function* lines() {
  for (let i = 1; i <= 50_000; i++) yield `${i} ${i % 97 === 0 ? 500 : 200} /api/item/${i % 50}\\n`;
}
await pipeline(Readable.from(lines()), createWriteStream("big.log"));

// 2. Transform stream: keep only the 5xx lines and turn them into JSON
const onlyErrors = new Transform({
  objectMode: true,
  transform(line, _enc, done) {
    const [id, status, path] = line.split(" ");
    if (status >= 500) this.push({ id: +id, status: +status, path });
    done();
  },
});

// 3. Writable sink that counts
let errors = 0, first;
const counter = new Writable({ objectMode: true, write(row, _enc, done) { errors++; first ??= row; done(); } });

const rl = createInterface({ input: createReadStream("big.log"), crlfDelay: Infinity });
await pipeline(Readable.from(rl), onlyErrors, counter);
console.log("5xx lines:", errors, "| first:", first);
console.log("memory stays small: the file was never read into one string");
''', 'Streams: generate, filter and count a big file', play=False),
    'backpressure': run('''
import { Writable } from "node:stream";

// A slow writer with a small buffer
const slow = new Writable({
  highWaterMark: 4,                                    // bytes before write() asks you to wait
  write(chunk, _enc, done) { setTimeout(done, 1); },
});

let refused = 0, drained = 0;
slow.on("drain", () => drained++);
for (let i = 0; i < 10; i++) if (!slow.write("ab")) refused++;
console.log("write() returned false", refused, "times: stop and wait for drain");

// The right way: await drain when write() returns false (pipeline does this for you)
async function writeAll(stream, chunks) {
  for (const c of chunks) if (!stream.write(c)) await new Promise(r => stream.once("drain", r));
}
await writeAll(slow, Array(10).fill("ab"));
console.log("drain events so far:", drained > 0);
''', 'Backpressure: when the reader is slower than the writer', play=False),
    'buffers': run('''
import { createHash, createHmac, randomUUID, timingSafeEqual, randomInt } from "node:crypto";

const buf = Buffer.from("Héllo ₹", "utf8");
console.log(buf, buf.length, "bytes for", "Héllo ₹".length, "characters");
console.log(buf.toString("hex"), buf.toString("base64"), Buffer.from("SMOpbGxvIOKCuQ==", "base64").toString());
console.log(buf instanceof Uint8Array);

// Hash a file's bytes for golden file tests: same bytes, same hash
const report = JSON.stringify({ passed: 41, failed: 1 });
console.log("sha256:", createHash("sha256").update(report).digest("hex").slice(0, 16), "...");

// HMAC signatures, as used by webhooks: compare in constant time
const secret = "whsec_test";
const sign = body => createHmac("sha256", secret).update(body).digest();
const sent = sign('{"event":"order.paid"}');
console.log("valid signature:", timingSafeEqual(sent, sign('{"event":"order.paid"}')));
console.log("tampered body:", timingSafeEqual(sent, sign('{"event":"order.refunded"}')));
console.log("unique ids:", typeof randomUUID(), randomInt(1, 7) >= 1);
''', 'Buffers, hashes and HMAC signatures', play=False),
    'sqlite': run('''
import { DatabaseSync } from "node:sqlite";

// A real SQL database built into Node.js: perfect for test data and quick checks
const db = new DatabaseSync(":memory:");
db.exec(`
  CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, role TEXT NOT NULL);
  CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), total REAL, status TEXT);
`);
const addUser = db.prepare("INSERT INTO users (email, role) VALUES (?, ?)");
const addOrder = db.prepare("INSERT INTO orders (user_id, total, status) VALUES (?, ?, ?)");
for (const [email, role] of [["asha@shop.test", "admin"], ["ravi@shop.test", "customer"], ["li@shop.test", "customer"]]) addUser.run(email, role);
for (const [u, t, s] of [[2, 450, "paid"], [2, 120, "refunded"], [3, 980, "paid"], [3, 40, "new"]]) addOrder.run(u, t, s);

// Parameters, never string building, so test data with quotes is safe
console.log(db.prepare("SELECT id, role FROM users WHERE email = ?").get("ravi@shop.test"));

const report = db.prepare(`
  SELECT u.email, COUNT(o.id) AS orders, SUM(CASE WHEN o.status = 'paid' THEN o.total ELSE 0 END) AS paid
  FROM users u LEFT JOIN orders o ON o.user_id = u.id GROUP BY u.id ORDER BY paid DESC`).all();
console.table(report.map(r => ({ ...r })));

try { addUser.run("asha@shop.test", "customer"); } catch (e) { console.log("constraint:", e.message); }
''', 'The built in SQLite database', play=False),
    'process': run('''
import { spawn } from "node:child_process";

// spawn streams output as it arrives, unlike exec which waits for the end
const child = spawn(process.execPath, ["-e", `
  let n = 0;
  const t = setInterval(() => console.log("test", ++n, "passed"), 10);
  process.on("SIGTERM", () => { clearInterval(t); console.log("cleaning up, closing the browser"); process.exit(0); });
`]);

let lines = 0;
child.stdout.setEncoding("utf8");
child.stdout.on("data", chunk => {
  for (const line of chunk.trim().split("\\n")) {
    console.log("child:", line);
    if (++lines === 3) child.kill("SIGTERM");          // ask it to stop nicely
  }
});
const [code, signal] = await new Promise(r => child.on("exit", (c, s) => r([c, s])));
console.log("exit code", code, "signal", signal);
''', 'Child processes, streaming output and graceful shutdown', play=False),
    'cli': test({
        'package.json': pkg('log-check', 'module', {'test': 'node --test'}) .replace('"private": true', '"private": true,\n  "bin": { "log-check": "./bin/log-check.js" }'),
        'bin/log-check.js': '''
#!/usr/bin/env node
import { parseArgs, styleText } from "node:util";
import { createReadStream } from "node:fs";
import { createInterface } from "node:readline";

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    "max-errors": { type: "string", default: "0" },
    json: { type: "boolean", default: false },
    help: { type: "boolean", short: "h" },
  },
});
if (values.help || positionals.length === 0) {
  console.log("usage: log-check [--max-errors N] [--json] FILE");
  process.exit(values.help ? 0 : 2);                      // 2 means "used wrongly"
}

let total = 0, errors = 0;
for await (const line of createInterface({ input: createReadStream(positionals[0]) })) {
  total++;
  if (/ 5\\d\\d /.test(line)) errors++;
}
const ok = errors <= Number(values["max-errors"]);
if (values.json) console.log(JSON.stringify({ total, errors, ok }));
else console.log(styleText(ok ? "green" : "red", `${errors} errors in ${total} lines`));
process.exitCode = ok ? 0 : 1;                            // CI fails the job on 1
''',
        'test/cli.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";

const cli = (...args) => spawnSync(process.execPath, ["bin/log-check.js", ...args], { encoding: "utf8" });
writeFileSync("ok.log", "GET /a 200 \\nGET /b 200 \\n");
writeFileSync("bad.log", "GET /a 200 \\nPOST /orders 503 \\nGET /b 500 \\n");

test("no file prints usage and exits with 2", () => {
  const r = cli();
  assert.equal(r.status, 2);
  assert.match(r.stdout, /usage/);
});
test("a clean log passes", () => {
  assert.deepEqual(JSON.parse(cli("--json", "ok.log").stdout), { total: 2, errors: 0, ok: true });
});
test("errors over the limit fail with exit code 1", () => {
  const r = cli("bad.log");
  assert.equal(r.status, 1);
  assert.equal(r.stdout.trim(), "2 errors in 3 lines");
});
test("--max-errors raises the limit", () => assert.equal(cli("--max-errors", "2", "bad.log").status, 0));
''',
    }, 'npm test', 'A command line tool with parseArgs, tested with spawnSync', show=['bin/log-check.js', 'test/cli.test.js'],
        replace=[(r' \([\d.]+ms\)', ''), (r'ℹ duration_ms [\d.]+', 'ℹ duration_ms 212.4')]),
}

LANES = {
    'backpressure': {'t': 'Backpressure: write, pause, drain, resume', 'code': 'const out = fs.createWriteStream("big.csv", { highWaterMark: 16 * 1024 });\nfor (const row of rows) {\n  if (!out.write(row)) await once(out, "drain");\n}', 'lanes': ['Your loop', 'Buffer in memory (16 KB limit)', 'Disk'], 'tone': [2, 5, 1], 'steps': [{'l': 3, 'v': [['write 4 KB: true'], ['4 KB'], []], 'm': "write puts the chunk in the stream's buffer and returns true: there is room for more."}, {'l': 3, 'v': [['write 4 KB: true'], ['8 KB'], ['writing...']], 'm': 'The disk starts writing in the background, but the loop is faster.'}, {'l': 3, 'v': [['write 4 KB: true'], ['12 KB'], ['writing...']], 'm': 'The buffer keeps growing because the producer is faster than the disk.'}, {'l': 3, 'v': [['write 4 KB: false'], ['16 KB, full'], ['writing...']], 'm': 'The buffer reached highWaterMark, so write returns false. That is the signal to stop.'}, {'l': 3, 'v': [['await once(out, "drain")'], ['8 KB'], ['8 KB written']], 'm': 'The loop pauses. Memory stays small while the disk catches up.'}, {'l': 3, 'v': [['drain fired, keep going'], ['0 KB'], ['16 KB written']], 'm': 'When the buffer is empty, the stream emits drain and the loop continues. Ignoring false would let memory grow until the process crashes on a big file.'}]},
}

PARTS = [
    part('events', '📣', 'Events and EventEmitter', '''
<p>Much of Node.js is built on <b>EventEmitter</b>: servers, sockets, streams, child processes and test runners. Listeners register with <code>on</code> or <code>once</code>, and <code>emit</code> calls them in order, synchronously. <code>events.once</code> turns one event into a promise and <code>events.on</code> turns a stream of events into an async iterator.</p>
[[events]]
<div class="warn">An <code>"error"</code> event with no listener throws and can crash the process. Every emitter you create, and every stream and socket you use, needs an error listener or a <code>pipeline</code> that handles errors for you.</div>
''', qa=True, qa_why='Test runners, reporters and browser drivers report progress through events, and custom reporters listen to them.',
        kw=['EventEmitter', 'on', 'once', 'emit', 'error event', 'events.once', 'events.on', 'async iterator', 'AbortSignal', 'listener', 'reporter']),
    part('streams', '🌊', 'Streams and backpressure', '''
<p>A <b>stream</b> moves data in small chunks, so a 5 GB log file never has to fit in memory. <b>Readable</b> streams produce data, <b>Writable</b> streams consume it, and <b>Transform</b> streams change it on the way. <code>pipeline</code> connects them, passes errors along and closes everything at the end.</p>
[[streams]]
<p>The animation shows what happens inside a write stream when your code produces data faster than the disk or the network can take it.</p>
<div class="viz" data-viz="lanes" data-k="backpressure"></div>
<p><b>Backpressure</b> is how a slow consumer tells a fast producer to wait. When <code>write()</code> returns false, stop writing until the <code>"drain"</code> event. <code>pipeline</code> and <code>for await</code> do this automatically, which is the main reason to use them.</p>
[[backpressure]]
''', qa=True, qa_why='Reading huge logs, HAR files and test result exports needs streams, or the test tool runs out of memory.',
        kw=['streams', 'Readable', 'Writable', 'Transform', 'pipeline', 'stream/promises', 'backpressure', 'highWaterMark', 'drain', 'readline', 'Readable.from', 'objectMode', 'big files']),
    part('buffers', '🔢', 'Buffers, encodings and crypto', '''
<p>A <b>Buffer</b> is a fixed block of bytes, a <code>Uint8Array</code> with extra methods. Text needs an <b>encoding</b> to become bytes: in UTF-8, "é" takes 2 bytes and "₹" takes 3, so byte length and string length differ. The <code>crypto</code> module gives hashes, HMAC signatures, random ids and safe comparison.</p>
[[buffers]]
<div class="qa-box">Testing webhooks means checking signatures: compute the HMAC of the exact raw body with the shared secret and compare with <code>timingSafeEqual</code>. Also test a changed body, a wrong secret and a missing signature header, which must all be rejected.</div>
''', qa=True, qa_why='Webhook signatures, file checksums and binary uploads all need bytes, hashes and HMACs in tests.',
        kw=['Buffer', 'Uint8Array', 'encoding', 'UTF-8', 'base64', 'hex', 'crypto', 'createHash', 'sha256', 'HMAC', 'timingSafeEqual', 'randomUUID', 'webhook signature']),
    part('sqlite', '🗄️', 'The built in SQLite database', '''
<p>Node.js ships with <code>node:sqlite</code>, a full SQL database that runs in memory or in a file with no server and no install. It is ideal for seeding test data, checking reports, and learning SQL alongside JavaScript.</p>
[[sqlite]]
<div class="tip">Always use prepared statements with <code>?</code> placeholders. Test data such as <code>O'Brien</code> then works, and so does an SQL injection test that tries <code>' OR '1'='1</code>.</div>
''', qa=True, qa_why='Database checks after an API or UI action confirm that data was really saved, which UI checks alone cannot prove.',
        kw=['node:sqlite', 'SQLite', 'DatabaseSync', 'SQL', 'prepared statement', 'placeholder', 'JOIN', 'GROUP BY', 'test data', 'database testing', 'constraint']),
    part('process', '⚙️', 'Processes, signals and graceful shutdown', '''
<p><code>spawn</code> starts another program and streams its output as it arrives, which suits long runs such as a test suite or a dev server. Programs are stopped with <b>signals</b>: <code>SIGINT</code> when you press Ctrl+C and <code>SIGTERM</code> when CI or Docker stops a job. A well written tool catches them, cleans up, and then exits.</p>
[[process]]
<div class="note">Exit codes are the contract with CI: 0 means success, 1 means the check failed, and 2 is the usual code for "used wrongly". Set <code>process.exitCode</code> instead of calling <code>process.exit()</code> so pending output is still written.</div>
''', qa=['CI', 'Node.js'], qa_why='Starting servers for tests, stopping them cleanly and returning the right exit code are what make a suite reliable in CI.',
        kw=['child_process', 'spawn', 'exec', 'stdout', 'signals', 'SIGTERM', 'SIGINT', 'graceful shutdown', 'exit code', 'process.exitCode', 'kill']),
    part('cli', '💻', 'Building and testing a command line tool', '''
<div class="scenario"><b>The situation</b>The release pipeline needs a small tool that reads a server log and fails the job when there are more 5xx errors than allowed.</div>
<p><code>util.parseArgs</code> reads flags with no extra package, <code>readline</code> reads the file line by line, <code>styleText</code> adds colour that respects <code>NO_COLOR</code>, and the exit code tells CI the result. The <code>bin</code> field in package.json turns the file into a command after <code>npm install</code>.</p>
[[cli]]
<p>The tests run the real tool with <code>spawnSync</code> and check its output and exit code, exactly the way CI will use it.</p>
''', qa=True, qa_why='Small CLI tools glue test pipelines together, and they need tests of their own exit codes and output.',
        kw=['CLI', 'command line tool', 'parseArgs', 'util.parseArgs', 'bin', 'shebang', 'styleText', 'NO_COLOR', 'spawnSync', 'exit code', 'readline', 'CI gate']),
]

INFO = {'title': 'Node.js under the surface', 'panels': [
    panel([['e', '📣'], ['t', 'emitter.on("fail", …)', {'b': 1, 'size': 11}]], 'Events', 'Most of Node is event driven.', 'Always listen for "error".'),
    panel([['e', '🌊'], ['t', 'pipeline(read, transform, write)', {'b': 1, 'size': 10}]], 'Streams', 'Chunks, not whole files.', 'pipeline handles backpressure.'),
    panel([['e', '🔐'], ['t', 'createHmac("sha256", secret)', {'b': 1, 'size': 10}]], 'Crypto', 'Hashes and signatures.', 'Compare in constant time.'),
    panel([['e', '💻'], ['t', 'process.exitCode = 1', {'b': 1, 'size': 11}]], 'Tools', 'Flags in, exit code out.', 'Test them like CI uses them.')],
    'remember': 'Listen for errors, stream big data through pipeline, use prepared statements, and give every tool a clear exit code.'}

REAL = [
    ['📜', 'A load test team', 'Analysed a 12 GB access log with a Transform stream on a laptop with 8 GB of memory. Reading it as one string had crashed every time.'],
    ['🔔', 'A payments webhook', 'Failed signature checks in tests because the body was parsed and re-serialised before hashing. Hashing the raw bytes fixed it.'],
    ['🚦', 'A release pipeline', 'Uses a small log check CLI as a gate: more than five 5xx errors after a canary deploy and the job exits with 1 and rolls back.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter goes deep into Node: events, streams and backpressure, buffers and crypto, the built in SQLite database, processes and signals, and command line tools.',
        'यह अध्याय Node में गहराई से जाता है: events, streams और backpressure, buffers और crypto, SQLite, processes, signals और command line tools।',
        'ಈ ಅಧ್ಯಾಯ Node ಆಳವಾಗಿ: events, streams, backpressure, buffers, crypto, SQLite, processes ಮತ್ತು CLI tools.',
        'ଏହି ଅଧ୍ୟାୟ Node ଗଭୀରରେ: events, streams, backpressure, buffers, crypto, SQLite, processes ଓ CLI tools।',
        'يتعمق هذا الفصل في Node: الأحداث والتدفقات والضغط العكسي والمخازن والتشفير وقاعدة SQLite المدمجة والعمليات والإشارات وأدوات سطر الأوامر.',
        'Dieses Kapitel geht tief in Node: Events, Streams, Backpressure, Buffer, Crypto, SQLite, Prozesse, Signale und Kommandozeilen-Tools.'),
    say('events', 'Events', 'EventEmitter calls listeners in order when an event is emitted. events once gives a promise, and an error event with no listener throws.',
        'EventEmitter event होने पर listeners को क्रम से call करता है। events once promise देता है, और बिना listener का error event throw करता है।',
        'EventEmitter listeners ಅನ್ನು ಕ್ರಮವಾಗಿ call ಮಾಡುತ್ತದೆ. Listener ಇಲ್ಲದ error event throw ಮಾಡುತ್ತದೆ.',
        'EventEmitter listeners କୁ କ୍ରମରେ call କରେ। Listener ନଥିବା error event throw କରେ।',
        'يستدعي EventEmitter المستمعين بالترتيب عند إطلاق الحدث، ويعطي events.once وعدًا، ويرمي حدث الخطأ بلا مستمع استثناء.',
        'EventEmitter ruft Listener der Reihe nach auf. events.once liefert ein Promise, ein error-Event ohne Listener wirft.'),
    say('streams', 'Streams', 'Streams move data in chunks. pipeline connects them, passes errors on and handles backpressure, so a slow writer is never flooded.',
        'Streams data को टुकड़ों में भेजते हैं। pipeline उन्हें जोड़ता है, errors आगे भेजता है और backpressure संभालता है।',
        'Streams data ತುಂಡುಗಳಲ್ಲಿ ಸಾಗಿಸುತ್ತವೆ. pipeline ಜೋಡಿಸಿ backpressure ನಿಭಾಯಿಸುತ್ತದೆ.',
        'Streams data ଖଣ୍ଡରେ ପଠାନ୍ତି। pipeline ଯୋଡ଼େ ଓ backpressure ସମ୍ଭାଳେ।',
        'تنقل التدفقات البيانات على دفعات، ويربطها pipeline وينقل الأخطاء ويعالج الضغط العكسي.',
        'Streams bewegen Daten in Stücken. pipeline verbindet sie, reicht Fehler weiter und regelt den Rückstau.'),
    say('buffers', 'Buffers and crypto', 'A Buffer holds bytes, and text needs an encoding to become bytes. Use HMAC with timing safe equal to check webhook signatures.',
        'Buffer bytes रखता है, और text को bytes बनने के लिए encoding चाहिए। Webhook signatures के लिए HMAC और timing safe equal इस्तेमाल करें।',
        'Buffer bytes ಹಿಡಿಯುತ್ತದೆ, text ಗೆ encoding ಬೇಕು. Webhook ಗೆ HMAC ಬಳಸಿ.',
        'Buffer bytes ରଖେ, text ପାଇଁ encoding ଦରକାର। Webhook ପାଇଁ HMAC ବ୍ୟବହାର କରନ୍ତୁ।',
        'يحفظ Buffer البايتات ويحتاج النص إلى ترميز ليصبح بايتات. استخدم HMAC مع المقارنة الآمنة زمنيًا لفحص توقيعات الويب هوك.',
        'Ein Buffer hält Bytes, Text braucht eine Kodierung. Prüfe Webhook-Signaturen mit HMAC und zeitsicherem Vergleich.'),
    say('sqlite', 'SQLite', 'Node includes a SQLite database with no server. Use prepared statements with placeholders for safe test data and queries.',
        'Node में बिना server वाला SQLite database है। सुरक्षित test data के लिए placeholders वाले prepared statements इस्तेमाल करें।',
        'Node ನಲ್ಲಿ server ಇಲ್ಲದ SQLite ಇದೆ. Placeholders ಇರುವ prepared statements ಬಳಸಿ.',
        'Node ରେ server ବିନା SQLite ଅଛି। Placeholders ଥିବା prepared statements ବ୍ୟବହାର କରନ୍ତୁ।',
        'يتضمن Node قاعدة SQLite بلا خادم. استخدم عبارات معدة بعناصر نائبة لبيانات اختبار واستعلامات آمنة.',
        'Node enthält eine SQLite-Datenbank ohne Server. Nutze vorbereitete Anweisungen mit Platzhaltern.'),
    say('process', 'Processes', 'spawn streams the output of another program. Catch SIGTERM to clean up, and use exit codes: zero for success, one for failure.',
        'spawn दूसरे program का output stream करता है। साफ करने के लिए SIGTERM पकड़ें, और exit codes: शून्य सफलता, एक विफलता।',
        'spawn ಮತ್ತೊಂದು program output stream ಮಾಡುತ್ತದೆ. SIGTERM ಹಿಡಿದು clean up ಮಾಡಿ.',
        'spawn ଅନ୍ୟ program output stream କରେ। SIGTERM ଧରି clean up କରନ୍ତୁ।',
        'تبث spawn مخرجات برنامج آخر. التقط SIGTERM للتنظيف، واستخدم رموز الخروج: صفر للنجاح وواحد للفشل.',
        'spawn streamt die Ausgabe eines Programms. Fange SIGTERM zum Aufräumen ab, Exit-Code null heißt Erfolg.'),
    say('cli', 'A CLI tool', 'parseArgs reads the flags, readline reads the file, and the exit code tells CI the result. Test the tool by running it with spawnSync.',
        'parseArgs flags पढ़ता है, readline file पढ़ता है, और exit code CI को नतीजा बताता है। spawnSync से tool test करें।',
        'parseArgs flags, readline file ಓದುತ್ತವೆ, exit code CI ಗೆ ಫಲಿತಾಂಶ. spawnSync ನಿಂದ test ಮಾಡಿ.',
        'parseArgs flags, readline file ପଢ଼େ, exit code CI କୁ ଫଳାଫଳ। spawnSync ରେ test କରନ୍ତୁ।',
        'يقرأ parseArgs الخيارات ويقرأ readline الملف، ويخبر رمز الخروج نظام CI بالنتيجة. اختبر الأداة بتشغيلها عبر spawnSync.',
        'parseArgs liest Flags, readline die Datei, der Exit-Code meldet das Ergebnis. Teste das Tool mit spawnSync.'),
    say('practice', 'Hands-on', 'Practise a typed event bus, a line splitter for chunks, an HMAC style checksum check, and parsing command line flags.',
        'Event bus, chunks के लिए line splitter, checksum check और command line flags parse करने का अभ्यास करें।',
        'Event bus, line splitter, checksum check ಮತ್ತು command line flags ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Event bus, line splitter, checksum check ଓ command line flags ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على ناقل أحداث ومقسم أسطر للدفعات وفحص مجموع تحقق وتحليل خيارات سطر الأوامر.',
        'Übe einen Event-Bus, einen Zeilenteiler für Chunks, eine Prüfsummenkontrolle und Kommandozeilen-Flags.'),
]

QUIZ = [
    quiz('e', 'What does emitter.once("end", fn) do?', ['Calls fn for the first "end" event only', 'Calls fn for every event', 'Emits "end" once', 'Removes all listeners'], 0, 'One time.', 'The listener is removed after the first call.'),
    quiz('e', 'Why use streams for a 5 GB file?', ['So it never has to fit in memory at once', 'Streams are always faster', 'Files cannot be read otherwise', 'To compress it'], 0, 'Chunks.', 'Each chunk is processed and then released.'),
    quiz('e', 'Which exit code tells CI that a check failed?', ['1', '0', '200', '-1'], 0, 'Non zero means failure.', '0 means success. 2 often means the tool was used wrongly.'),
    quiz('m', 'What happens when an EventEmitter emits "error" with no listener?', ['It throws, which can crash the process', 'Nothing', 'It logs a warning', 'It retries'], 0, 'Special event.', 'Always add an error listener or use pipeline.'),
    quiz('m', 'write() on a stream returns false. What should you do?', ['Wait for the "drain" event before writing more', 'Write faster', 'Close the stream', 'Ignore it'], 0, 'Backpressure.', 'The internal buffer is full.'),
    quiz('m', 'How many bytes does "₹" take in UTF-8?', ['3', '1', '2', '4'], 0, 'Outside the first 2048 code points.', 'Buffer.byteLength("₹") is 3.'),
    quiz('m', 'Why use ? placeholders in SQL statements?', ['Values are passed separately, which prevents SQL injection and quoting bugs', 'It is faster to type', 'SQLite needs them', 'To hide the query'], 0, 'Parameters.', "O'Brien works without any escaping."),
    quiz('h', 'Why compare HMAC signatures with timingSafeEqual instead of ===?', ['=== can stop at the first different byte, which leaks timing information', '=== does not work on buffers', 'It is shorter', 'It hashes again'], 0, 'Timing attacks.', 'Constant time comparison takes the same time whatever the bytes are.'),
    quiz('h', 'What does pipeline give you over chaining .pipe()?', ['Error handling and clean up of every stream, as a promise', 'Faster code', 'Compression', 'Nothing'], 0, 'Errors and closing.', '.pipe() does not forward errors, so failures could leak open files.'),
    quiz('h', 'Which signal does CI usually send to stop a job?', ['SIGTERM', 'SIGKILL first', 'SIGHUP', 'SIGSTOP'], 0, 'Polite stop.', 'SIGKILL follows only if the process does not exit in time.'),
    quiz('x', 'Why set process.exitCode = 1 instead of calling process.exit(1)?', ['Pending output and async work can still finish', 'exit() is not allowed', 'It changes the code later', 'It is required by npm'], 0, 'Clean exit.', 'process.exit() stops at once and can cut off logs.'),
    quiz('x', 'A webhook test parses the JSON body and re-serialises it before computing the HMAC. Why do valid signatures fail?', ['The bytes differ, for example spacing or key order, so the hash differs', 'HMAC cannot hash JSON', 'The secret changed', 'JSON is binary'], 0, 'Hash the raw bytes.', 'Always sign and verify the exact bytes that were sent.'),
]

CALC = [
    calc('e', 'In the streams example, every line number divisible by 97 is a 500. How many 5xx lines are in 50,000 lines?', '515', 'Whole multiples.', ['<span class="eq">⌊50000 ÷ 97⌋ = 515</span>']),
    calc('e', 'Buffer.byteLength("Héllo") where é is 2 bytes. How many bytes?', '6', '5 characters, one of them 2 bytes.', ['<span class="eq">4 × 1 + 1 × 2 = 6</span>']),
    calc('m', 'A stream with highWaterMark 16 KB reads a 1 MB file. About how many chunks is that?', '64', '1 MB is 1024 KB.', ['<span class="eq">1024 ÷ 16 = 64</span>']),
    calc('m', 'A SHA-256 hash in hex has how many characters?', '64', '256 bits, 4 bits per hex digit.', ['<span class="eq">256 ÷ 4 = 64</span>']),
    calc('m', 'Users 2 and 3 have paid orders of 450 and 980. What is the sum of paid totals in the report?', '1430', 'Only status paid.', ['<span class="eq">450 + 980 = 1430</span>']),
    calc('h', 'base64 turns every 3 bytes into 4 characters. How long is the base64 of 9 bytes?', '12', 'Groups of 3.', ['<span class="eq">9 ÷ 3 × 4 = 12</span>']),
    calc('h', 'A log check allows at most 5 errors. A canary run has 3 errors in 2,000 lines. What exit code does the tool return?', '0', 'Within the limit.', ['3 is not more than 5, so the check passes.']),
    calc('x', 'A child test runner prints one line every 10 ms and is sent SIGTERM after its 3rd line. About how many ms did it run?', '30', 'Three intervals.', ['<span class="eq">3 × 10 = 30</span>']),
]

EX = [
    ex('bus', 'e', 'A tiny event bus', '<p>Write <code>createBus()</code> that returns <code>{ on, emit }</code>. <code>on(name, fn)</code> registers a listener and returns a function that removes it. <code>emit(name, ...args)</code> calls every listener for that name in order.</p>',
       'function createBus() {\n  \n}\n',
       [('(() => { const bus = createBus(); const log = []; const off = bus.on("pass", n => log.push("a" + n)); bus.on("pass", n => log.push("b" + n)); bus.emit("pass", 1); off(); bus.emit("pass", 2); bus.emit("other"); return log; })()', ['a1', 'b1', 'b2'])],
       'function createBus() {\n  const map = new Map();\n  return {\n    on(name, fn) {\n      if (!map.has(name)) map.set(name, new Set());\n      map.get(name).add(fn);\n      return () => map.get(name).delete(fn);\n    },\n    emit(name, ...args) {\n      for (const fn of map.get(name) ?? []) fn(...args);\n    },\n  };\n}', hint='A Map from event name to a Set of listeners.', why='Returning an unsubscribe function avoids the listener leaks from {{ch:js-expert}}.'),
    ex('splitter', 'm', 'Split chunks into lines', '<p>Streams deliver text in chunks that can cut a line in half. Write <code>lineSplitter()</code> that returns <code>{ push(chunk), end() }</code>. <code>push</code> returns the complete lines found so far, and <code>end</code> returns what is left as a final line, or an empty array.</p>',
       'function lineSplitter() {\n  \n}\n',
       [('(() => { const s = lineSplitter(); return [s.push("GET /a 200\\nGET /b"), s.push(" 500\\nPOST"), s.push(" /c 201\\n"), s.end()]; })()', [['GET /a 200'], ['GET /b 500'], ['POST /c 201'], []]),
        ('(() => { const s = lineSplitter(); return [s.push("a"), s.end()]; })()', [[], ['a']])],
       'function lineSplitter() {\n  let rest = "";\n  return {\n    push(chunk) {\n      const parts = (rest + chunk).split("\\n");\n      rest = parts.pop();\n      return parts;\n    },\n    end() {\n      return rest ? [rest] : [];\n    },\n  };\n}', hint='Keep the last, unfinished piece between calls.', why='This is what readline does inside. Forgetting the leftover piece loses or breaks lines at chunk edges.'),
    ex('checksum', 'h', 'Verify a checksum', '<p>Write <code>checksum(text)</code> that returns the sum of the UTF-8 byte values of the text modulo 256, and <code>verify(text, sum)</code> that returns true only when they match. Use <code>new TextEncoder().encode(text)</code> for the bytes.</p>',
       'function checksum(text) {\n  \n}\nfunction verify(text, sum) {\n  \n}\n',
       [('checksum("A")', 65), ('checksum("₹")', (0xE2 + 0x82 + 0xB9) % 256), ('verify("order.paid", checksum("order.paid"))', True), ('verify("order.refunded", checksum("order.paid"))', False)],
       'function checksum(text) {\n  return new TextEncoder().encode(text).reduce((s, b) => (s + b) % 256, 0);\n}\nfunction verify(text, sum) {\n  return checksum(text) === sum;\n}', hint='Encode to bytes, then reduce with addition modulo 256.', why='Real systems use SHA-256 or HMAC, but the idea is the same: compute over the exact bytes, then compare.'),
    ex('flags', 'x', 'Parse command line flags', '<p>Write <code>parseFlags(argv)</code> for arguments such as <code>["--json", "--max-errors", "3", "app.log", "--env=staging"]</code>. Return <code>{ flags, files }</code>. <code>--name=value</code> and <code>--name value</code> set a string, a <code>--name</code> followed by another flag or by nothing is <code>true</code>, and everything else is a file.</p>',
       'function parseFlags(argv) {\n  \n}\n',
       [('parseFlags(["--json", "--max-errors", "3", "app.log", "--env=staging"])', {'flags': {'json': True, 'max-errors': '3', 'env': 'staging'}, 'files': ['app.log']}),
        ('parseFlags(["a.log", "b.log", "--verbose"])', {'flags': {'verbose': True}, 'files': ['a.log', 'b.log']}), ('parseFlags([])', {'flags': {}, 'files': []})],
       'function parseFlags(argv) {\n  const flags = {}, files = [];\n  for (let i = 0; i < argv.length; i++) {\n    const a = argv[i];\n    if (!a.startsWith("--")) { files.push(a); continue; }\n    const [name, value] = a.slice(2).split("=");\n    if (value !== undefined) flags[name] = value;\n    else if (i + 1 < argv.length && !argv[i + 1].startsWith("--") && !/\\.\\w+$/.test(argv[i + 1])) flags[name] = argv[++i];\n    else flags[name] = true;\n  }\n  return { flags, files };\n}',
       hint='Loop with an index so you can take the next argument as a value. Here a word that looks like a file name, such as app.log, is a file, not a value.', why='In real tools, declare which flags take values, as util.parseArgs does, instead of guessing.'),
]

T = {
    'slug': 'js-node-deep', 'title': 'Node.js in depth', 'short': 'Node.js in depth', 'emoji': '🟩', 'module': MODULE, 'minutes': 19,
    'lead': 'The parts of Node.js that power real tools: EventEmitter and async event iteration, streams, pipeline and backpressure for huge files, buffers, encodings, hashes and webhook signatures, the built in SQLite database, child processes and signals, and a tested command line tool for CI.',
    'desc': 'Node.js in depth: EventEmitter, events.once, streams, Transform, pipeline, backpressure, readline, Buffer, UTF-8, crypto, HMAC, timingSafeEqual, node:sqlite, spawn, signals, graceful shutdown, exit codes, util.parseArgs and testing a CLI.',
    'summary': 'EventEmitter with once, error events and async iteration, generating and filtering a big file with streams, backpressure and drain, buffers, encodings, SHA-256 and HMAC webhook signatures, the built in SQLite database with prepared statements, spawn with streaming output and SIGTERM clean up, and a log check CLI tested with spawnSync.',
    'keywords': ['Node.js', 'EventEmitter', 'streams', 'pipeline', 'backpressure', 'Buffer', 'crypto', 'HMAC', 'webhook', 'node:sqlite', 'SQLite', 'spawn', 'SIGTERM', 'exit code', 'parseArgs', 'CLI', 'interview'],
    'qa_intro': 'Test tools are Node.js programs. Streams read huge logs, crypto checks webhooks, SQLite holds test data, and exit codes make your tools work in CI.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
