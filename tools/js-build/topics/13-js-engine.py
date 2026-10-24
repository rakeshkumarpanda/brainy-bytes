# Chapter 13: how the engine really runs code: execution contexts, scope chains, this, the Node.js event loop phases, V8 shapes and garbage collection.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🔬', 'JavaScript in depth', 'js-depth', 'How the engine really works, errors and debugging, regular expressions, functional style, metaprogramming and Node.js in depth.')

CODES = {
    'stack': run('''
function placeOrder() { return chargeCard(); }
function chargeCard() { return callBank(); }
function callBank() {
  // Error().stack is a snapshot of the call stack at this moment
  return new Error("snapshot").stack.split("\\n").slice(1, 4).map(l => l.trim().split(" (")[0]);
}
console.log(placeOrder());

// Each call adds a frame. Too many frames and the engine stops you.
function countDown(n) { return n === 0 ? "done" : countDown(n - 1); }
console.log(countDown(1000));
try { countDown(1e6); } catch (e) { console.log(e.name + ":", e.message); }
''', 'The call stack and stack overflow', replace=[(r'"at file:///[^"]*"', '"at <module>"')]),
    'contexts': run('''
// Creation phase: the engine scans the function before running a single line
function checkout() {
  console.log(typeof total, typeof applyCoupon);           // var is undefined, the function exists
  try { console.log(discount); } catch (e) { console.log(e.name + ":", e.message); }
  try { typeof Cart; } catch (e) { console.log("even typeof throws in the TDZ:", e.name); }

  var total = 100;
  let discount = 10;                                             // in the temporal dead zone until here
  function applyCoupon(t) { return t - discount; }
  class Cart {}
  return applyCoupon(total);
}
console.log(checkout());

// Each loop iteration with let gets a fresh binding. var shares one.
const withVar = [], withLet = [];
for (var i = 0; i < 3; i++) withVar.push(() => i);
for (let j = 0; j < 3; j++) withLet.push(() => j);
console.log(withVar.map(f => f()), withLet.map(f => f()));

// The scope chain is fixed where the function is written, not where it is called
const label = "global";
function show() { return label; }
function caller() { const label = "caller"; return show(); }
console.log(caller());
''', 'Execution contexts, the TDZ and the scope chain'),
    'this-rules': run('''
"use strict";
function who() { return this?.name ?? String(this); }
const page = { name: "LoginPage", who };
const other = { name: "CartPage" };

console.log("1 default:", who());                       // plain call: undefined in strict mode
console.log("2 implicit:", page.who());                 // called on an object
console.log("3 explicit:", who.call(other));            // call, apply
const bound = who.bind(other);
console.log("4 bound:", bound(), bound.call(page));     // bind wins over call
function Page(name) { this.name = name; }
console.log("5 new:", new Page("Home").name);           // new creates a fresh this

// Arrow functions have no this of their own. They use the one around them.
const timer = {
  name: "Timer",
  regular() { return [1].map(function () { return this?.name; })[0]; },
  arrow() { return [1].map(() => this.name)[0]; },
};
console.log("arrow:", timer.arrow(), "regular:", timer.regular());
''', 'The five rules of this', file='this.cjs'),
    'lost-this': run('''
class SearchPage {
  results = [];
  query = "pen";
  // A normal method: "this" depends on how it is called
  collect(item) { this.results.push(`${this.query}:${item}`); }
  // A class field arrow: "this" is fixed to the instance
  collectSafe = item => { this.results.push(`${this.query}:${item}`); };
}

const page = new SearchPage();
try { ["blue", "red"].forEach(page.collect); }
catch (e) { console.log("passing the method:", e.constructor.name, "-", e.message); }

["blue", "red"].forEach(page.collect.bind(page));
["green"].forEach(page.collectSafe);
["black"].forEach(item => page.collect(item));
console.log(page.results);
''', 'Losing this when you pass a method'),
    'loop': run('''
const fs = require("node:fs");

console.log("1 sync start");
setTimeout(() => console.log("6 timers phase: setTimeout 0"), 0);
Promise.resolve().then(() => console.log("4 microtask: promise then"));
queueMicrotask(() => console.log("5 microtask: queueMicrotask"));
process.nextTick(() => console.log("3 nextTick queue"));

fs.readFile(__filename, () => {
  console.log("7 poll phase: I/O callback");
  setTimeout(() => console.log("9 timers phase, next loop"), 0);
  setImmediate(() => console.log("8 check phase: setImmediate"));
  process.nextTick(() => console.log("7b nextTick after the callback"));
});
console.log("2 sync end");
''', 'Node.js event loop phases in order', file='loop.cjs'),
    'await-ticks': run('''
const log = [];
async function step(name) {
  log.push(`${name} start`);
  await null;                        // one microtask hop, even for a value that is not a promise
  log.push(`${name} after await`);
}
step("A");
step("B");
Promise.resolve().then(() => log.push("then C"));
log.push("sync done");
await new Promise(r => setTimeout(r, 0));
console.log(log);
''', 'Every await gives other code a turn'),
    'shapes': run('''
// V8 gives objects with the same properties added in the same order the same hidden class ("map").
// Code that always sees one shape stays fast. %HaveSameMap is a V8 debugging helper.
function Point(x, y) { this.x = x; this.y = y; }
const a = new Point(1, 2), b = new Point(3, 4);
console.log("same constructor:", %HaveSameMap(a, b));

const c = new Point(5, 6);
c.label = "extra";                                   // a new property moves c to a new shape
console.log("extra property:", %HaveSameMap(a, c));

console.log("different order:", %HaveSameMap({ x: 1, y: 2 }, { y: 2, x: 1 }));

const d = new Point(7, 8);
delete d.x;                                          // delete makes V8 fall back to a slow dictionary
console.log("after delete:", %HaveSameMap(a, d), "| dictionary mode:", !%HasFastProperties(d));
''', 'Hidden classes: objects with the same shape', play=False, flags=['--allow-natives-syntax']),
    'gc': run('''
import v8 from "node:v8";

// The heap is split into a young generation (new objects) and an old generation (survivors)
const spaces = v8.getHeapSpaceStatistics().map(s => s.space_name);
console.log("young:", spaces.includes("new_space"), "| old:", spaces.includes("old_space"), "| big objects:", spaces.includes("large_object_space"));

// Short lived objects are cheap: most die young and are collected in a quick "scavenge"
let kept = [];
for (let i = 0; i < 100_000; i++) {
  const temp = { id: i, tags: ["a", "b"] };          // garbage right after this iteration
  if (i % 10_000 === 0) kept.push(temp);              // only these survive
}
console.log("kept", kept.length, "objects out of 100000");
console.log("heap limit is a few GB:", v8.getHeapStatistics().heap_size_limit > 1e9);
''', 'Generations in the V8 heap', play=False),
    'scenario': run('''
// A retry helper used by many page objects
async function retry(action, times = 3) {
  for (let i = 1; i <= times; i++) {
    try { return await action(); }
    catch (e) { if (i === times) throw e; }
  }
}

class CheckoutPage {
  attempts = 0;
  constructor(api) { this.api = api; }
  async submit() { this.attempts++; return this.api.post("/orders"); }
}

const flakyApi = { calls: 0, async post() { if (++this.calls < 2) throw new Error("503"); return { id: 1042 }; } };
const page = new CheckoutPage(flakyApi);

// The bug from the ticket: "Cannot read properties of undefined (reading 'attempts')"
await retry(page.submit).catch(e => console.log("bug:", e.message));

// Three fixes, each keeps "this" pointing at the page
console.log(await retry(() => page.submit()), "attempts:", page.attempts);
console.log(await retry(page.submit.bind(page)), "attempts:", page.attempts);
''', 'Fix "Cannot read properties of undefined" in a page object'),
}

LANES = {
    'phases': {'t': 'One turn of the Node.js event loop',
               'code': 'setTimeout(t, 0)          // timers\nfs.readFile(f, io)        // poll\nsetImmediate(i)           // check\nprocess.nextTick(n)       // between every step\nPromise.resolve().then(p) // microtasks',
               'lanes': ['Running now', 'nextTick and microtasks', 'Loop phase', 'Console'], 'tone': [2, 1, 3, 4],
               'steps': [{'l': [1, 2, 3, 4, 5], 'v': [['main script'], ['n', 'p'], ['timers: t', 'poll: waiting for io', 'check: i'], []], 'm': 'The main script registers everything. Nothing has run yet.'},
                         {'l': 4, 'v': [[], ['p'], ['timers: t', 'poll: io', 'check: i'], ['n']], 'm': 'The script ends. In CommonJS, process.nextTick callbacks run first.'},
                         {'l': 5, 'v': [[], [], ['timers: t', 'poll: io', 'check: i'], ['n', 'p']], 'm': 'Then the promise microtasks. Both queues are emptied after every single callback.'},
                         {'l': 1, 'v': [['t'], [], ['poll: io', 'check: i'], ['n', 'p', 't']], 'm': 'Timers phase: expired setTimeout and setInterval callbacks run.'},
                         {'l': 2, 'v': [['io'], [], ['check: i'], ['n', 'p', 't', 'io']], 'm': 'Poll phase: finished I/O such as files and sockets runs its callbacks.'},
                         {'l': 3, 'v': [['i'], [], [], ['n', 'p', 't', 'io', 'i']], 'm': 'Check phase: setImmediate callbacks run. Then the loop starts the next turn.'}]},
    'this': {'t': 'Which this does the call get',
             'code': 'new Page()          // 1. new\nfn.bind(obj)()      // 2. bound\nfn.call(obj)        // 3. explicit\nobj.fn()            // 4. implicit\nfn()                // 5. default',
             'lanes': ['Call form', 'Rule', 'this is'], 'tone': [2, 1, 3],
             'steps': [{'l': 1, 'v': [['new Page()'], ['new binding'], ['the new object']], 'm': 'new always wins. It creates an object and runs the function with this set to it.'},
                       {'l': 2, 'v': [['bound()'], ['bind'], ['the bound object']], 'm': 'A bound function ignores call and apply. Only new can override it.'},
                       {'l': 3, 'v': [['fn.call(obj)'], ['explicit'], ['obj']], 'm': 'call and apply set this for one call.'},
                       {'l': 4, 'v': [['obj.fn()'], ['implicit'], ['obj, the thing before the dot']], 'm': 'A method call uses the object before the dot.'},
                       {'l': 5, 'v': [['fn()'], ['default'], ['undefined in strict code']], 'm': 'A plain call gets undefined in strict mode and modules, and globalThis in old sloppy scripts.'},
                       {'l': [], 'v': [['() => this'], ['arrow'], ['this from the surrounding code']], 'm': 'Arrow functions skip all five rules and keep the this of the code around them.'}]},
}

PARTS = [
    part('stack', '📚', 'Execution contexts and the call stack', '''
<p>Every time a function is called, the engine creates an <b>execution context</b>: a record of its variables, its scope chain and its <code>this</code>. Contexts sit on the <b>call stack</b>. The one on top is running, and when it returns it is popped off. A stack trace in an error is simply a print of this stack.</p>
[[stack]]
<div class="qa-box">Read a failing test's stack trace from the top: the first line that points into <b>your</b> code (a page object, a helper, a spec file) is usually where the fix belongs. Lines inside <code>node_modules</code> are the framework calling you.</div>
''', qa=True, qa_why='Reading stack traces quickly is the first step in debugging every failed automated test.',
        kw=['execution context', 'call stack', 'stack frame', 'stack trace', 'stack overflow', 'RangeError', 'Maximum call stack size exceeded', 'recursion']),
    part('contexts', '🏗️', 'Creation phase, hoisting and the scope chain', '''
<p>Before a function runs, the engine scans it and sets up its bindings. <code>var</code> names start as <code>undefined</code>, function declarations are ready to call, and <code>let</code>, <code>const</code> and <code>class</code> exist but sit in the <b>temporal dead zone</b> until their line runs. This scan is what people call <b>hoisting</b>.</p>
[[contexts]]
<p>Scope is <b>lexical</b>: a function looks up names in the place it was written, then outwards, never in the place it was called from. Closures ({{ch:js-functions}}) are this rule plus the fact that the outer variables stay alive as long as the inner function does.</p>
''', kw=['creation phase', 'hoisting', 'temporal dead zone', 'TDZ', 'lexical scope', 'scope chain', 'lexical environment', 'var in loops', 'closure', 'let per iteration']),
    part('this', '👉', 'this in depth: five rules and a precedence', '''
<p>The value of <code>this</code> is decided by <b>how a function is called</b>, not where it is written. Five rules cover every case, and when several apply, the one higher in this list wins.</p>
<div class="viz" data-viz="lanes" data-k="this"></div>
[[this-rules]]
<p>The most common bug in test code is passing a method as a callback. The method is detached from its object, so the call becomes a plain call and <code>this</code> is <code>undefined</code>.</p>
[[lost-this]]
''', qa=['Playwright', 'Selenium'], qa_why='Page object methods passed to forEach, retry helpers or event handlers lose this, which crashes the test.',
        kw=['this', 'default binding', 'implicit binding', 'explicit binding', 'call', 'apply', 'bind', 'new', 'arrow function this', 'class field arrow', 'lost this', 'strict mode']),
    part('loop', '🔄', 'The Node.js event loop, phase by phase', '''
<p>{{Ch:js-async}} showed the browser view: microtasks first, then one task. Node.js splits the task side into <b>phases</b> that run in a fixed order on every turn: <b>timers</b> (setTimeout and setInterval), <b>poll</b> (finished I/O such as files and sockets) and <b>check</b> (setImmediate). Between every callback, Node.js empties the <code>process.nextTick</code> queue and then the promise microtask queue.</p>
<div class="viz" data-viz="lanes" data-k="phases"></div>
[[loop]]
[[await-ticks]]
<div class="note">Inside an I/O callback, <code>setImmediate</code> always runs before <code>setTimeout(fn, 0)</code>, because the check phase comes straight after poll. At the top level of a script, the order of those two depends on how fast the process starts, so never write a test that relies on it.</div>
''', qa=True, qa_why='Knowing which callback runs first explains log orders, race conditions and why a missing await lets a test finish too early.',
        kw=['event loop phases', 'timers phase', 'poll phase', 'check phase', 'setImmediate', 'process.nextTick', 'microtask', 'queueMicrotask', 'libuv', 'await microtask']),
    part('v8', '⚙️', 'Inside V8: JIT, hidden classes and inline caches', '''
<p>V8, the engine in Chrome and Node.js, first turns your code into bytecode and runs it with the <b>Ignition</b> interpreter. Functions that run often are compiled to machine code by the optimising compilers (<b>Sparkplug</b>, <b>Maglev</b> and <b>TurboFan</b>). The optimised code makes guesses, such as "this object always has x then y". If a guess turns out wrong, V8 <b>deoptimises</b> and falls back to slower code.</p>
[[shapes]]
<p>Each property access remembers the shapes it has seen in an <b>inline cache</b>. One shape is monomorphic and fastest, a few is polymorphic, and many is megamorphic and slow. In practice: create objects with all their properties in the constructor, in the same order, and avoid <code>delete</code> on hot objects.</p>
<div class="tip">Do not tune for the engine before you measure ({{ch:js-expert}}). Shapes matter in tight loops over millions of objects, such as parsing a large log file, and almost never in test code.</div>
''', kw=['V8', 'Ignition', 'TurboFan', 'Maglev', 'Sparkplug', 'JIT', 'bytecode', 'hidden class', 'shape', 'map', 'inline cache', 'monomorphic', 'megamorphic', 'deoptimisation', 'delete']),
    part('gc', '🧹', 'Garbage collection', '''
<p>JavaScript frees memory for you. V8 uses a <b>generational</b> collector because most objects die young. New objects go into the small <b>young generation</b>, which is cleaned often with a fast copying "scavenge". Objects that survive twice move to the <b>old generation</b>, which is cleaned less often with <b>mark and sweep</b>: mark everything reachable from the roots (globals and the stack), then free the rest. Most of the work happens in parallel and in small steps, so pauses stay short.</p>
[[gc]]
<div class="qa-box">If memory keeps rising in a long test run, take two heap snapshots in Chrome DevTools (Memory tab) or with <code>v8.writeHeapSnapshot()</code> and compare them. The objects that grow between the snapshots, and the "retainers" that hold them, point to the leak ({{ch:js-expert}}).</div>
''', qa=True, qa_why='Soak tests and long UI sessions expose memory leaks, and heap snapshots are how testers report them precisely.',
        kw=['garbage collection', 'generational GC', 'young generation', 'old generation', 'scavenge', 'mark and sweep', 'roots', 'reachability', 'heap snapshot', 'v8.getHeapStatistics', 'memory']),
    part('scenario', '🎬', 'Real world scenario: a crash only in the retry helper', '''
<div class="scenario"><b>The situation</b>A test fails with "Cannot read properties of undefined (reading 'attempts')". The page object works when called directly, and fails only when it is passed to the shared retry helper.</div>
[[scenario]]
<p>The helper calls <code>action()</code> as a plain function, so <code>this</code> is undefined inside <code>submit</code>. Wrapping it in an arrow or binding it keeps the page object as <code>this</code>. The team also added a lint rule, <code>@typescript-eslint/unbound-method</code>, which flags this mistake in review.</p>
''', qa=True, kw=['debugging', 'this undefined', 'retry helper', 'page object', 'bind', 'arrow wrapper', 'unbound-method']),
]

INFO = {'title': 'What happens when your code runs', 'panels': [
    panel([['e', '📚'], ['t', 'call stack', {'b': 1}]], 'One stack', 'Each call adds a context on top.', 'An error prints the stack as a trace.'),
    panel([['e', '👉'], ['t', 'obj.fn() vs fn()', {'b': 1}]], 'this follows the call', 'Five rules, new is the strongest.', 'Arrows keep the outer this.'),
    panel([['e', '🔄'], ['t', 'timers → poll → check', {'b': 1}]], 'Loop phases', 'nextTick and microtasks run between them.', 'Each await is one microtask hop.'),
    panel([['e', '⚙️'], ['t', 'same shape = fast', {'b': 1}]], 'V8 guesses', 'Stable shapes keep code optimised.', 'Young objects are collected cheaply.')],
    'remember': 'The call decides this, the place you write a function decides its scope, and the loop runs microtasks before the next phase.'}

REAL = [
    ['🐞', 'A Selenium suite', 'Passed a page object method to an array forEach and got "this is undefined" only on one screen. A class field arrow fixed it for every caller.'],
    ['📈', 'A log parser', 'Built its objects with different property orders, which made a hot loop megamorphic. Creating every record with the same constructor made it four times faster.'],
    ['⏱️', 'An API mock', 'Used setImmediate inside a socket callback to send a reply after the request was fully read, which the poll and check phase order guarantees.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter looks under the hood: execution contexts, hoisting, the rules of this, the Node event loop phases, V8 optimisation and garbage collection.',
        'यह अध्याय अंदर की बात दिखाता है: execution contexts, hoisting, this के नियम, Node event loop phases, V8 optimisation और garbage collection।',
        'ಈ ಅಧ್ಯಾಯ ಒಳಗಿನ ಕೆಲಸ ತೋರಿಸುತ್ತದೆ: execution contexts, hoisting, this ನಿಯಮಗಳು, Node event loop phases, V8 ಮತ್ತು garbage collection.',
        'ଏହି ଅଧ୍ୟାୟ ଭିତରର କାମ ଦେଖାଏ: execution contexts, hoisting, this ନିୟମ, Node event loop phases, V8 ଓ garbage collection।',
        'يكشف هذا الفصل ما يجري في الداخل: سياقات التنفيذ والرفع وقواعد this ومراحل حلقة أحداث Node وتحسينات V8 وجمع المهملات.',
        'Dieses Kapitel schaut unter die Haube: Ausführungskontexte, Hoisting, die Regeln von this, Event-Loop-Phasen, V8 und Garbage Collection.'),
    say('stack', 'Call stack', 'Each call creates an execution context on the call stack. A stack trace prints that stack, and the first line in your own code is usually where to look.',
        'हर call stack पर एक execution context बनाता है। Stack trace वही stack दिखाता है, और आपके code की पहली line अक्सर सही जगह होती है।',
        'ಪ್ರತಿ call stack ನಲ್ಲಿ execution context ಮಾಡುತ್ತದೆ. Stack trace ನಲ್ಲಿ ನಿಮ್ಮ code ನ ಮೊದಲ ಸಾಲು ನೋಡಿ.',
        'ପ୍ରତ୍ୟେକ call stack ରେ execution context ତିଆରି କରେ। Stack trace ରେ ଆପଣଙ୍କ code ର ପ୍ରଥମ ଧାଡ଼ି ଦେଖନ୍ତୁ।',
        'كل استدعاء ينشئ سياق تنفيذ على المكدس. أثر المكدس يطبعه، وأول سطر من شيفرتك هو غالبًا مكان المشكلة.',
        'Jeder Aufruf legt einen Kontext auf den Stack. Ein Stack-Trace druckt ihn, die erste Zeile aus deinem Code ist meist die richtige Stelle.'),
    say('contexts', 'Hoisting', 'Before running, the engine sets up names. var starts as undefined, functions are ready, and let, const and class wait in the temporal dead zone.',
        'चलने से पहले engine नाम तैयार करता है। var undefined से शुरू होता है, functions तैयार रहते हैं, और let, const, class TDZ में रहते हैं।',
        'ಓಡುವ ಮೊದಲು engine ಹೆಸರುಗಳನ್ನು ಸಿದ್ಧಪಡಿಸುತ್ತದೆ. var undefined, functions ಸಿದ್ಧ, let const class TDZ ನಲ್ಲಿ.',
        'ଚାଲିବା ପୂର୍ବରୁ engine ନାମ ପ୍ରସ୍ତୁତ କରେ। var undefined, functions ପ୍ରସ୍ତୁତ, let const class TDZ ରେ।',
        'قبل التشغيل يجهز المحرك الأسماء. يبدأ var بقيمة undefined، والدوال جاهزة، وlet وconst وclass في المنطقة الميتة مؤقتًا.',
        'Vor dem Start legt die Engine Namen an. var beginnt als undefined, Funktionen sind bereit, let, const und class warten in der TDZ.'),
    say('this', 'this', 'this is decided by the call. new wins, then bind, then call and apply, then the object before the dot, then a plain call. Arrows keep the outer this.',
        'this call से तय होता है। पहले new, फिर bind, फिर call और apply, फिर dot से पहले का object, फिर plain call। Arrow बाहर का this रखते हैं।',
        'this call ನಿಂದ ನಿರ್ಧಾರ. ಮೊದಲು new, ನಂತರ bind, call apply, dot ಮುಂದಿನ object, ಕೊನೆಗೆ plain call.',
        'this call ରୁ ସ୍ଥିର ହୁଏ। ପ୍ରଥମେ new, ତାପରେ bind, call apply, dot ପୂର୍ବ object, ଶେଷରେ plain call।',
        'يحدد الاستدعاء قيمة this. أولًا new ثم bind ثم call وapply ثم الكائن قبل النقطة ثم الاستدعاء العادي. الدوال السهمية تحتفظ بـ this الخارجي.',
        'this hängt vom Aufruf ab. Zuerst new, dann bind, dann call und apply, dann das Objekt vor dem Punkt, dann ein normaler Aufruf.'),
    say('loop', 'Event loop phases', 'Node runs timers, then poll for finished I O, then check for setImmediate. Between callbacks it empties nextTick and then the promise microtasks.',
        'Node पहले timers, फिर finished I O के लिए poll, फिर setImmediate के लिए check चलाता है। बीच में nextTick और promise microtasks खाली होते हैं।',
        'Node ಮೊದಲು timers, ನಂತರ poll, ನಂತರ check ಓಡಿಸುತ್ತದೆ. ಮಧ್ಯೆ nextTick ಮತ್ತು microtasks ಖಾಲಿಯಾಗುತ್ತವೆ.',
        'Node ପ୍ରଥମେ timers, ତାପରେ poll, ତାପରେ check ଚଲାଏ। ମଝିରେ nextTick ଓ microtasks ଖାଲି ହୁଏ।',
        'ينفذ Node المؤقتات ثم مرحلة الاستطلاع للإدخال والإخراج ثم مرحلة التحقق لـ setImmediate، ويفرغ بينها nextTick ثم المهام الدقيقة.',
        'Node führt Timer aus, dann Poll für fertige I/O, dann Check für setImmediate. Dazwischen leert es nextTick und die Microtasks.'),
    say('v8', 'Inside V8', 'V8 compiles hot code and guesses object shapes. Objects built the same way share a hidden class, which keeps property access fast.',
        'V8 बार बार चलने वाले code को compile करता है और object shapes का अनुमान लगाता है। एक जैसे बने objects एक hidden class साझा करते हैं।',
        'V8 ಹೆಚ್ಚು ಓಡುವ code compile ಮಾಡಿ object shapes ಊಹಿಸುತ್ತದೆ. ಒಂದೇ ರೀತಿ ಮಾಡಿದ objects hidden class ಹಂಚುತ್ತವೆ.',
        'V8 ଅଧିକ ଚାଲୁଥିବା code compile କରି object shapes ଅନୁମାନ କରେ। ସମାନ objects hidden class ବାଣ୍ଟନ୍ତି।',
        'يترجم V8 الشيفرة المتكررة ويخمن أشكال الكائنات. الكائنات المبنية بالطريقة نفسها تتشارك صنفًا مخفيًا فيبقى الوصول سريعًا.',
        'V8 kompiliert häufigen Code und rät Objektformen. Gleich gebaute Objekte teilen eine versteckte Klasse, das hält Zugriffe schnell.'),
    say('gc', 'Garbage collection', 'New objects live in the young generation and most die there cheaply. Survivors move to the old generation, which is cleaned with mark and sweep.',
        'नए objects young generation में रहते हैं और ज़्यादातर वहीं खत्म होते हैं। बचे हुए old generation में जाते हैं, जहां mark and sweep होता है।',
        'ಹೊಸ objects young generation ನಲ್ಲಿ, ಹೆಚ್ಚಿನವು ಅಲ್ಲೇ ಸಾಯುತ್ತವೆ. ಉಳಿದವು old generation ಗೆ ಹೋಗುತ್ತವೆ.',
        'ନୂଆ objects young generation ରେ, ଅଧିକାଂଶ ସେଠାରେ ଶେଷ ହୁଅନ୍ତି। ବଞ୍ଚିଥିବା old generation କୁ ଯାଆନ୍ତି।',
        'تعيش الكائنات الجديدة في الجيل الصغير ويموت أغلبها هناك بتكلفة قليلة، وينتقل الناجون إلى الجيل القديم الذي ينظف بالتعليم والكنس.',
        'Neue Objekte leben in der jungen Generation, die meisten sterben dort. Überlebende kommen in die alte Generation mit Mark and Sweep.'),
    say('scenario', 'Scenario', 'A retry helper called a page object method as a plain function, so this was undefined. An arrow wrapper or bind fixed it.',
        'Retry helper ने page object method को plain function की तरह call किया, इसलिए this undefined था। Arrow wrapper या bind से ठीक हुआ।',
        'Retry helper page object method ಅನ್ನು plain function ಆಗಿ call ಮಾಡಿತು, this undefined ಆಯಿತು. Arrow ಅಥವಾ bind ಸರಿಪಡಿಸಿತು.',
        'Retry helper page object method କୁ plain function ଭାବେ call କଲା, this undefined ହେଲା। Arrow କିମ୍ବା bind ଠିକ୍ କଲା।',
        'استدعت دالة إعادة المحاولة دالة كائن الصفحة كدالة عادية فصار this غير معرف، وأصلحه غلاف سهمي أو bind.',
        'Ein Retry-Helfer rief eine Page-Object-Methode als normale Funktion auf, also war this undefined. Ein Arrow oder bind half.'),
    say('practice', 'Hands-on', 'Practise predicting log order, fixing a lost this, writing your own bind, and building a tiny event loop with phases.',
        'Log का क्रम पहचानने, खोया this ठीक करने, अपना bind लिखने और phases वाला छोटा event loop बनाने का अभ्यास करें।',
        'Log ಕ್ರಮ ಊಹಿಸುವುದು, ಕಳೆದ this ಸರಿಪಡಿಸುವುದು, ನಿಮ್ಮ bind ಬರೆಯುವುದು ಮತ್ತು ಸಣ್ಣ event loop ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Log କ୍ରମ ଅନୁମାନ, ହଜିଥିବା this ଠିକ୍, ନିଜ bind ଲେଖିବା ଓ ଛୋଟ event loop ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على توقع ترتيب السجل وإصلاح this المفقود وكتابة bind بنفسك وبناء حلقة أحداث صغيرة بمراحل.',
        'Übe, die Log-Reihenfolge vorherzusagen, ein verlorenes this zu reparieren, bind selbst zu schreiben und eine kleine Event Loop zu bauen.'),
]

QUIZ = [
    quiz('e', 'What does a stack trace show?', ['The chain of function calls that led to the error', 'Every variable in the program', 'The network requests', 'The order of tests'], 0, 'The call stack.', 'Read from the top to see the innermost call first.'),
    quiz('e', 'What does typeof x print on the line before var x = 5?', ['undefined', 'number', 'It throws', 'null'], 0, 'var is hoisted with undefined.', 'The declaration is set up early, the value 5 is assigned only when that line runs.'),
    quiz('e', 'Inside an arrow function, where does this come from?', ['The code around the arrow', 'The object before the dot', 'Always globalThis', 'The arguments'], 0, 'Arrows have no own this.', 'That is why arrows are handy inside callbacks of methods.'),
    quiz('m', 'Which wins: fn.bind(a).call(b)?', ['a', 'b', 'undefined', 'globalThis'], 0, 'bind is stronger than call.', 'A bound function ignores call and apply. Only new can override bind.'),
    quiz('m', 'Why does accessing a let variable before its line throw?', ['It is in the temporal dead zone', 'let is not hoisted at all', 'Strict mode forbids it', 'It is a syntax error'], 0, 'TDZ.', 'let is hoisted but not initialised until its declaration runs.'),
    quiz('m', 'A function uses a variable named label. Which label does it see?', ['The one in scope where the function was written', 'The one where it was called', 'The global one always', 'The newest one created'], 0, 'Lexical scope.', 'JavaScript scope is decided by where code is written.'),
    quiz('m', 'In CommonJS, which runs first after the main script: process.nextTick or a promise then?', ['process.nextTick', 'The promise then', 'They run in random order', 'setTimeout'], 0, 'The nextTick queue goes first.', 'Node.js empties the nextTick queue before the promise microtask queue.'),
    quiz('h', 'Inside an fs.readFile callback, setTimeout(a, 0) and setImmediate(b). Which runs first?', ['b, the check phase follows poll', 'a, timers always first', 'Random', 'Neither runs'], 0, 'Poll, then check, then timers on the next turn.', 'This order is guaranteed inside I/O callbacks.'),
    quiz('h', 'What makes two objects share a V8 hidden class?', ['The same properties added in the same order', 'The same values', 'The same variable name', 'Being created on the same line'], 0, 'Shape.', '{x, y} and {y, x} have different shapes.'),
    quiz('h', 'Why are most objects collected cheaply?', ['Most die young, and the young generation is cleaned with a fast copy', 'They are never collected', 'They are stored on disk', 'The browser restarts often'], 0, 'Generational hypothesis.', 'Only survivors pay for the slower old generation collection.'),
    quiz('x', 'What does the last line return?', ['undefined, class bodies are strict', 'The P instance', 'globalThis', 'It throws a SyntaxError'], 0, 'Classes run in strict mode.', 'The detached method is a plain call, which gives undefined in strict code.', code='class P { m() { return this; } }\nconst f = new P().m;\nf();'),
    quiz('x', 'Two async functions each await null once. In what order do their second halves run?', ['In the order the functions were called', 'Reverse order', 'After all timers', 'Random'], 0, 'Each await queues one microtask.', 'Microtasks run first in, first out.'),
]

CALC = [
    calc('e', 'placeOrder calls chargeCard, which calls callBank. How many of these frames are on the stack while callBank runs?', '3', 'Count the calls not yet returned.', ['placeOrder, chargeCard and callBank are all still running.']),
    calc('e', 'What does fns[0]() return?', '3', 'One shared i.', ['All three arrows read the same i, which ends at 3.'], code='const fns = [];\nfor (var i = 0; i < 3; i++) fns.push(() => i);'),
    calc('m', 'With let instead, what does fns[0]() + fns[1]() + fns[2]() give?', '3', 'A fresh binding per turn.', ['<span class="eq">0 + 1 + 2 = 3</span>'], code='const fns = [];\nfor (let i = 0; i < 3; i++) fns.push(() => i);'),
    calc('m', 'A CommonJS file logs: sync A, nextTick B, promise C, timeout D, sync E. Write the position (1 to 5) of D in the output.', '5', 'Sync, then nextTick, then microtasks, then timers.', ['Order: A, E, B, C, D.', 'D is fifth.']),
    calc('m', 'countDown(n) recurses until 0. How many frames does countDown(1000) push, counting the first call?', '1001', 'n from 1000 down to 0.', ['<span class="eq">1000 − 0 + 1 = 1001</span>']),
    calc('h', 'An object survives two scavenges and is promoted. Scavenges run every 8 MB of new objects. After how many MB of allocation at the earliest is it in the old generation?', '16', 'Two scavenges.', ['<span class="eq">2 × 8 = 16</span>']),
    calc('h', 'A property access sees 1 shape (fast), 3 shapes (polymorphic) or more than 4 (megamorphic). How many shapes can a polymorphic cache hold at most?', '4', 'V8 keeps up to four.', ['A polymorphic inline cache stores up to 4 shapes.', 'A fifth shape makes it megamorphic.']),
    calc('x', 'An async function has 3 awaits on already resolved values. How many microtask hops before it returns?', '3', 'One per await.', ['Each await, even on a plain value, schedules the rest as a microtask.']),
]

EX = [
    ex('order', 'e', 'Predict the log order', '<p>Write <code>logOrder()</code> that returns an array of the labels in the order this CommonJS code prints them: <code>console.log("A"); setTimeout(() => console.log("B")); Promise.resolve().then(() => console.log("C")); process.nextTick(() => console.log("D")); console.log("E");</code></p>',
       'function logOrder() {\n  return [];\n}\n',
       [('logOrder()', ['A', 'E', 'D', 'C', 'B'])],
       'function logOrder() {\n  return ["A", "E", "D", "C", "B"];\n}', hint='Synchronous lines first, then nextTick, then promise microtasks, then timers.', why='This exact order is what the loop example on this page printed.'),
    ex('bindme', 'm', 'Write your own bind', '<p>Write <code>myBind(fn, thisArg, ...preset)</code> that returns a function which calls <code>fn</code> with <code>this</code> set to <code>thisArg</code>, the preset arguments first and then the new ones. Do not use the built in <code>bind</code>.</p>',
       'function myBind(fn, thisArg, ...preset) {\n  \n}\n',
       [('myBind(function (x, y) { return this.base + x + y; }, { base: 10 }, 1)(2)', 13),
        ('(() => { const page = { name: "Login", hello(g) { return g + " " + this.name; } }; const f = myBind(page.hello, page); return ["hi", "yo"].map(f); })()', ['hi Login', 'yo Login'])],
       'function myBind(fn, thisArg, ...preset) {\n  return (...args) => fn.apply(thisArg, [...preset, ...args]);\n}', hint='Return an arrow that calls <code>fn.apply</code>.', why='The returned arrow ignores the this it is called with, which is exactly why bound functions cannot be rebound by call.'),
    ex('fixthis', 'h', 'Fix the lost this', '<p><code>class Counter { count = 0; inc() { this.count++; } }</code> crashes when <code>inc</code> is passed to <code>forEach</code>. Write <code>makeCounter()</code> that returns an object with a <code>count</code> of 0 and an <code>inc</code> that still works when detached: <code>[1, 2, 3].forEach(c.inc)</code> must leave <code>c.count</code> at 3.</p>',
       'function makeCounter() {\n  return { count: 0, inc() { this.count++; } };\n}\n',
       [('(() => { const c = makeCounter(); [1, 2, 3].forEach(c.inc); return c.count; })()', 3), ('(() => { const c = makeCounter(); c.inc(); const f = c.inc; f(); return c.count; })()', 2)],
       'function makeCounter() {\n  const c = { count: 0 };\n  c.inc = () => { c.count++; };\n  return c;\n}', hint='Close over the object instead of using <code>this</code>.', why='A class field arrow, <code>inc = () => this.count++</code>, does the same thing inside a class.'),
    ex('miniloop', 'x', 'A tiny event loop', '<p>Write <code>runLoop(jobs)</code>. Each job is <code>{ kind, name }</code> where kind is <code>"sync"</code>, <code>"micro"</code>, <code>"timer"</code> or <code>"immediate"</code>. Return the names in the order Node.js would run them from the main script: all sync jobs, then all micro jobs, then timers, then immediates, each group keeping its input order.</p>',
       'function runLoop(jobs) {\n  \n}\n',
       [('runLoop([{ kind: "timer", name: "t" }, { kind: "sync", name: "s1" }, { kind: "micro", name: "m" }, { kind: "immediate", name: "i" }, { kind: "sync", name: "s2" }])', ['s1', 's2', 'm', 't', 'i']),
        ('runLoop([{ kind: "micro", name: "a" }, { kind: "micro", name: "b" }])', ['a', 'b']), ('runLoop([])', [])],
       'function runLoop(jobs) {\n  const order = ["sync", "micro", "timer", "immediate"];\n  return order.flatMap(kind => jobs.filter(j => j.kind === kind).map(j => j.name));\n}', hint='Go through the kinds in a fixed order and filter the jobs for each one.', why='Real loops also run new microtasks created by a timer before the next timer, which is the "between every callback" rule.'),
]

T = {
    'slug': 'js-engine', 'title': 'How JavaScript really works', 'short': 'Engine internals', 'emoji': '🔬', 'module': MODULE, 'minutes': 20,
    'lead': 'What the engine does with your code: execution contexts and the call stack, hoisting and the scope chain, the five rules of this, the Node.js event loop phase by phase, V8 hidden classes and inline caches, and generational garbage collection.',
    'desc': 'JavaScript internals: execution context, call stack, hoisting, TDZ, scope chain, this binding rules, Node.js event loop phases, nextTick, setImmediate, V8 JIT, hidden classes, inline caches and garbage collection.',
    'summary': 'The call stack and stack traces, the creation phase with hoisting, the temporal dead zone and lexical scope, the five rules of this and how methods lose it, the Node.js event loop phases with nextTick and microtasks, V8 compilers, hidden classes and inline caches, generational garbage collection, and a page object that crashes inside a retry helper.',
    'keywords': ['execution context', 'call stack', 'hoisting', 'TDZ', 'scope chain', 'this', 'bind', 'event loop phases', 'process.nextTick', 'setImmediate', 'V8', 'hidden class', 'inline cache', 'garbage collection', 'JavaScript internals', 'interview'],
    'qa_intro': 'Testers who know the engine read stack traces faster, explain odd log orders, and recognise the "this is undefined" crash in page objects at a glance.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
