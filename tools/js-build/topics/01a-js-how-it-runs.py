# Chapter 2: how a JavaScript program executes inside the engine, step by step, from the text file to the output.
# The same journey the Java subject shows for javac and the JVM: load, scan, parse, scopes, bytecode, run, optimise, clean up.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🌱', 'Foundations', 'js-foundations', 'From your first program to functions and closures. Developers and testers both start here.')

TRACE = [
    (r'(?m)^\[(?![^\n]*lineTotal)[^\n]*\n', ''),
    (r'\[marking 0x\w+ <JSFunction lineTotal \(sfi = 0x\w+\)> for optimization to (\w+), [^\]]*reason: ([^\]]+)\]', r'[V8] lineTotal is \2, mark it for \1'),
    (r'\[compiling method [^\]]*lineTotal[^\]]*\(target (\w+)\)[^\]]*\]', r'[V8] compile lineTotal with \1'),
    (r'\[completed compiling [^\]]*lineTotal[^\]]*\(target (\w+)\)[^\]]*\]', r'[V8] lineTotal now runs as \1 machine code'),
    (r'\[bailout \(kind: ([\w-]+), reason: ([^)]+)\): begin\. deoptimizing [^\n]*lineTotal[^\n]*', r'[V8] DEOPTIMISE lineTotal (\1), reason: \2'),
]

CODES = {
    'versions': run('''
// Node.js is a runtime. Inside it sits the V8 engine and the libuv library.
const { node, v8, uv } = process.versions;
console.log("runtime  Node.js", node);
console.log("engine   V8", v8.split("-")[0]);
console.log("loop/io  libuv", uv);

// The engine gives the language. The runtime adds the extras.
console.log(typeof Array, typeof Promise, typeof JSON);          // from the engine
console.log(typeof setTimeout, typeof fetch, typeof process);     // from the runtime
console.log(typeof document);                                      // only a browser runtime has a page
''', 'Which engine and runtime is running this page', play=False),
    'wrapper': run('''
// Node.js wraps every CommonJS file in a function before the engine sees it.
// That is where require, module, exports, __filename and __dirname come from.
const { wrapper } = require("node:module");
console.log(wrapper[0] + "...your file..." + wrapper[1]);

console.log(typeof require, typeof module, typeof exports);
console.log(__filename.endsWith("main.cjs"));
console.log("arguments of the wrapper:", arguments.length);
''', 'The invisible wrapper around a CommonJS file', file='main.cjs', play=False),
    'scanner': run('''
import vm from "node:vm";

// vm.Script only scans and parses. Nothing runs unless we ask.
const samples = [
  "1.toString()",        // the scanner reads "1." as one number token, then sees a name
  "1..toString()",       // "1." is the number, ".toString" is the property
  "1 .toString()",       // the space ends the number token
  "let total = 1_000_000",
  "let 2fast = 1",       // a name may not start with a digit
  "let price = 10 // a comment is thrown away",
];
for (const src of samples) {
  try {
    new vm.Script(src);
    console.log("ok       ", src.padEnd(24), "->", vm.runInNewContext(src));
  } catch (e) {
    console.log("rejected ", src.padEnd(24), "->", e.name + ":", e.message);
  }
}
''', 'What the scanner accepts and rejects', play=False),
    'syntax-stop': run('''
console.log("line 1: this never prints");
const user = { name: "Asha" };
console.log("line 3: neither does this");
if (user.name === "Asha" {
  console.log("hello");
}
''', 'One typo on line 4 stops line 1 too', expect='throw', replace=[(r'file:///\S+main\.mjs', 'main.mjs')]),
    'lazy': run('''
import vm from "node:vm";

// Early errors: the parser finds these before running anything
const early = [
  "let a = 1; let a = 2;",
  "const limit;",
  "return 5",
  "function f() { 'use strict'; with (Math) {} }",
];
for (const src of early) {
  try { new vm.Script(src); console.log("parsed  ", src); }
  catch (e) { console.log("early   ", src.padEnd(42), e.message); }
}

// Errors that only appear when the line runs
const late = new vm.Script("console.log('before'); missingFn(); console.log('after');");
try { late.runInNewContext({ console }); }
catch (e) { console.log("runtime ", e.name + ":", e.message); }
''', 'Early errors against runtime errors', play=False),
    'creation': run('''
console.log(total, typeof applyTax);            // the names already exist
var total = 100;
let rate = 0.18;
function applyTax(t) { return t + t * rate; }
console.log(applyTax(total));

try {
  console.log(gst);                            // let is in the temporal dead zone here
  let gst = 5;
} catch (e) {
  console.log(e.name + ":", e.message);
}

// Every call makes a new execution context with its own variables
function greet(name) { const msg = `Hello ${name}`; return msg; }
console.log(greet("Ravi"), greet("Meena"), typeof msg);
''', 'The creation phase, then the execution phase', file='main.cjs'),
    'bytecode': run('''
function addTax(price, rate) {
  const tax = price * rate;
  return price + tax;
}
console.log(addTax(100, 0.18));
''', 'The real bytecode V8 makes for one function', play=False, flags=['--print-bytecode', '--print-bytecode-filter=addTax'],
        replace=[(r'0x[0-9a-f]+', '0x…'), (r'\(0x… <SharedFunctionInfo addTax>\)', ''), (r'0x… <Other heap object[^\n]*\n', '')]),
    'stack-heap': run('''
function makeOrder(id) {
  const items = ["pen"];
  return { id, items };
}
let qty = 2;
let copyQty = qty;           // a number is copied
copyQty = 5;

const order = makeOrder(7);
const copy = order;          // an object is shared: both names point at one heap object
copy.id = 8;
console.log(order.id, qty, copyQty, order === copy);

// The call stack has a limit. The heap is much larger.
function depth(n) { try { return depth(n + 1); } catch { return n; } }
console.log("stack frames before overflow > 5000:", depth(0) > 5000);
''', 'Values on the stack, objects on the heap'),
    'gc-weak': run('''
// Run with --expose-gc so the example can ask V8 to collect garbage now.
let cart = { items: new Array(100_000).fill("item") };
const watch = new WeakRef(cart);            // a weak reference does not keep the object alive

await new Promise(r => setTimeout(r, 0));  // let the current job finish first
console.log("still reachable:", watch.deref() !== undefined);

cart = null;                               // the last strong reference is gone
await new Promise(r => setTimeout(r, 0));
gc();
console.log("after gc:", watch.deref());
''', 'Unreachable objects are collected', play=False, flags=['--expose-gc']),
    'jit': run('''
// A function the checkout page calls for every cart line
function lineTotal(price, qty) {
  return price * qty;
}

let sum = 0;
for (let i = 0; i < 100_000; i++) sum += lineTotal(i % 50, 2);   // always numbers: the function gets hot
console.log("sum of numbers:", sum);

console.log("a string sneaks in:", lineTotal("12", 2));        // the guess "price is a small integer" breaks
for (let i = 0; i < 100_000; i++) sum += lineTotal(i % 50, 2);
console.log("done");
''', 'Watch V8 optimise and deoptimise a hot function (trace lines shortened)', play=False,
        flags=['--trace-opt', '--trace-deopt', '--no-concurrent-recompilation'], replace=TRACE),
    'loop': run('''
console.log("A sync");
setTimeout(() => console.log("B timer"), 0);
Promise.resolve().then(() => console.log("C promise"));
console.log("D sync");

setTimeout(() => {
  console.log("E timer");
  Promise.resolve().then(() => console.log("F promise inside the timer"));
}, 0);
setTimeout(() => console.log("G second timer"), 0);
''', 'The same orders the simulator shows, run for real'),
    'modules': run('''
console.log("main.mjs body runs last");
import { price, bump } from "./price.mjs";
import "./logger.mjs";

console.log("price is", price);
bump();
console.log("price after bump is", price);   // a live binding, not a copy
''', 'Modules: linked first, then evaluated in order', play=False, extra={
        'logger.mjs': '''
console.log("logger.mjs runs first, it is a dependency");
''',
        'price.mjs': '''
import "./logger.mjs";                 // already loaded, so it does not run twice
console.log("price.mjs runs second");
export let price = 100;
export function bump() { price += 10; }
'''}),
    'scenario': run('''
// Sale day: the "Apply coupon" button stops responding for a moment.
// A ticker that should fire every 50 ms shows how long the thread was busy.
function heavyWork(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {}             // one long synchronous job
}

function measure(label, work) {
  return new Promise(resolve => {
    const start = Date.now();
    setTimeout(() => {
      const late = Date.now() - start - 50;
      console.log(label.padEnd(24), "timer was late by more than 200 ms:", late > 200);
      resolve();
    }, 50);
    work();
  });
}

await measure("blocking 400 ms", () => heavyWork(400));

// The fix: split the work into small chunks and give the event loop a turn between them
async function chunked(total, chunk) {
  for (let done = 0; done < total; done += chunk) {
    heavyWork(chunk);
    await new Promise(r => setTimeout(r, 0));   // let timers, clicks and painting run
  }
}
await measure("chunked 20 x 20 ms", () => { chunked(400, 20); });
''', 'A frozen page on sale day, and the fix', play=False),
}

LANES = {
    'creation': {'t': 'Creation phase, then execution phase',
                 'code': 'console.log(total, typeof applyTax);\nvar total = 100;\nlet rate = 0.18;\nfunction applyTax(t) { return t + t * rate; }\nconsole.log(applyTax(total));',
                 'lanes': ['Phase', 'Global scope (memory)', 'Call stack', 'Console'], 'tone': [3, 1, 2, 4],
                 'steps': [{'l': [], 'v': [['creation'], ['total = undefined', 'rate = <uninitialised>', 'applyTax = function'], ['global context'], []],
                            'm': 'Before any line runs, the engine walks the code once and makes a slot for every declared name. var starts as undefined, let waits uninitialised, and a function declaration is ready to call.'},
                           {'l': 1, 'v': [['execution'], ['total = undefined', 'rate = <uninitialised>', 'applyTax = function'], ['global context'], ['undefined function']],
                            'm': 'Line 1 runs. total exists but has no value yet, and applyTax is already a function. This early access is what people call hoisting.'},
                           {'l': 2, 'v': [['execution'], ['total = 100', 'rate = <uninitialised>', 'applyTax = function'], ['global context'], ['undefined function']], 'm': 'Line 2 gives total its value.'},
                           {'l': 3, 'v': [['execution'], ['total = 100', 'rate = 0.18', 'applyTax = function'], ['global context'], ['undefined function']], 'm': 'Line 3 initialises rate. Reading it any earlier would have thrown a ReferenceError.'},
                           {'l': 4, 'v': [['execution'], ['total = 100', 'rate = 0.18', 'applyTax = function'], ['global context'], ['undefined function']], 'm': 'Line 4 does nothing now. The function was created in the creation phase.'},
                           {'l': 5, 'v': [['execution'], ['total = 100', 'rate = 0.18', 'applyTax = function', 't = 100 (inside applyTax)'], ['global context', 'applyTax(100)'], ['undefined function']],
                            'm': 'Line 5 calls applyTax. A new function execution context goes on the call stack with its own variable t.'},
                           {'l': 5, 'v': [['execution'], ['total = 100', 'rate = 0.18', 'applyTax = function'], ['global context'], ['undefined function', '118']],
                            'm': 'The function returns 118, its context is popped off the stack, and console.log prints the result.'}]},
    'stackheap': {'t': 'The call stack and the heap',
                  'code': 'function makeOrder(id) {\n  const items = ["pen"];\n  return { id, items };\n}\nconst qty = 2;\nconst order = makeOrder(7);\nconst copy = order;\ncopy.id = 8;\nconsole.log(order.id, qty);',
                  'lanes': ['Call stack', 'Variables', 'Heap', 'Console'], 'tone': [2, 1, 0, 4],
                  'steps': [{'l': 5, 'v': [['global'], ['qty = 2'], [], []], 'm': 'A number is a primitive. The variable holds the value itself.'},
                            {'l': 6, 'v': [['global', 'makeOrder(7)'], ['qty = 2', 'id = 7'], [], []], 'm': 'Calling makeOrder pushes a new frame on the call stack. Its parameter id lives in that frame.'},
                            {'l': 2, 'v': [['global', 'makeOrder(7)'], ['qty = 2', 'id = 7', 'items -> #1'], ['#1 array ["pen"]'], []], 'm': 'An array is an object, so it is created on the heap. The variable items only holds a reference to it.'},
                            {'l': 3, 'v': [['global', 'makeOrder(7)'], ['qty = 2', 'id = 7', 'items -> #1'], ['#1 array ["pen"]', '#2 { id: 7, items: #1 }'], []], 'm': 'The returned object is another heap object. It points at the array.'},
                            {'l': 6, 'v': [['global'], ['qty = 2', 'order -> #2'], ['#1 array ["pen"]', '#2 { id: 7, items: #1 }'], []], 'm': 'makeOrder returns. Its frame and its local variables are gone, but both heap objects survive because order still reaches them.'},
                            {'l': 7, 'v': [['global'], ['qty = 2', 'order -> #2', 'copy -> #2'], ['#1 array ["pen"]', '#2 { id: 7, items: #1 }'], []], 'm': 'copy = order copies the reference, not the object. Two names, one object.'},
                            {'l': 8, 'v': [['global'], ['qty = 2', 'order -> #2', 'copy -> #2'], ['#1 array ["pen"]', '#2 { id: 8, items: #1 }'], []], 'm': 'Changing the object through copy changes what order sees too.'},
                            {'l': 9, 'v': [['global'], ['qty = 2', 'order -> #2', 'copy -> #2'], ['#1 array ["pen"]', '#2 { id: 8, items: #1 }'], ['8 2']], 'm': 'The console prints 8 and 2.'},
                            {'l': [], 'v': [[], [], ['#1 (unreachable)', '#2 (unreachable)'], ['8 2']], 'm': 'When the script ends and nothing points at #1 and #2 any more, the garbage collector frees their memory. You never call free yourself.'}]},
}

DG = {
    'pipeline': {'t': 'The whole journey of a JavaScript program', 'w': 980, 'h': 400,
                 'g': [[10, 6, 960, 92, 'Engine front end: from text to a tree', 2], [10, 120, 960, 112, 'Engine: interpreter and optimising compilers (V8 names)', 3], [10, 254, 960, 140, 'Runtime: memory and the outside world', 1]],
                 'n': [['src', 30, 34, 120, 52, 'your .js file', {'c': 5, 'sh': 'doc', 'i': 'Plain text. The engine knows nothing about it yet.'}],
                       ['load', 200, 34, 120, 52, 'loader', {'c': 2, 'sub': 'browser or Node.js', 'i': 'A browser downloads the file, Node.js reads it from disk. Modules also fetch every import.'}],
                       ['scan', 370, 34, 120, 52, 'scanner', {'c': 2, 'sub': 'text to tokens', 'i': 'Cuts the characters into tokens such as let, price, =, 250 and ;. Spaces and comments are dropped.'}],
                       ['parse', 540, 34, 120, 52, 'parser', {'c': 2, 'sub': 'tokens to tree', 'i': 'Builds the abstract syntax tree and finds early errors. One SyntaxError stops the whole file.'}],
                       ['ast', 710, 34, 240, 52, 'AST and scopes', {'c': 3, 'sh': 'pill', 'sub': 'which name belongs where', 'i': 'Scope analysis decides which variable every name refers to, before anything runs.'}],
                       ['ign', 770, 150, 180, 56, 'Ignition', {'c': 0, 'sub': 'bytecode interpreter', 'i': 'Turns the tree into bytecode and starts running at once. It also records type feedback: which types each line really sees.'}],
                       ['spark', 540, 150, 170, 56, 'Sparkplug', {'c': 0, 'sub': 'fast, simple compiler', 'i': 'Turns bytecode straight into machine code with no clever optimisation. Cheap and quick.'}],
                       ['mag', 305, 150, 165, 56, 'Maglev', {'c': 1, 'sub': 'mid tier optimiser', 'i': 'Uses the type feedback to build fairly fast code in very little time.'}],
                       ['tf', 30, 150, 190, 56, 'TurboFan', {'c': 4, 'sub': 'top tier optimiser', 'i': 'Spends more time to make the fastest code for the hottest functions. It relies on guesses about types and shapes.'}],
                       ['stack', 30, 290, 150, 56, 'call stack', {'c': 2, 'sub': 'one frame per call', 'i': 'Holds the execution context of every function that has not returned yet.'}],
                       ['heap', 220, 290, 150, 56, 'heap', {'c': 0, 'sub': 'objects, arrays, functions', 'i': 'A large memory area for everything that is not a small primitive value.'}],
                       ['gc', 410, 290, 150, 56, 'garbage collector', {'c': 1, 'sub': 'Orinoco in V8', 'i': 'Frees objects that nothing can reach any more.'}],
                       ['loop', 575, 290, 145, 56, 'event loop', {'c': 3, 'sub': 'one job at a time', 'i': 'When the stack is empty, it runs all microtasks, then the next task.'}],
                       ['apis', 790, 290, 160, 56, 'Web APIs or libuv', {'c': 4, 'sub': 'timers, network, files', 'i': 'The runtime does the waiting outside JavaScript and queues a callback when the work is done.'}]],
                 'e': [['src', 'load'], ['load', 'scan'], ['scan', 'parse'], ['parse', 'ast'], ['ast', 'ign', {'t': 'compile'}],
                       ['ign', 'spark', {'t': 'warm'}], ['spark', 'mag', {'t': 'hot'}], ['mag', 'tf', {'t': 'very hot'}],
                       ['tf', 'ign', {'t': 'deoptimise', 'd': 1, 'fs': 'b', 'ts': 'b', 'via': [[125, 232], [860, 232]]}],
                       ['heap', 'gc'], ['apis', 'loop', {'t': 'callback'}], ['loop', 'stack', {'t': 'run on empty stack', 'fs': 'b', 'ts': 'b', 'via': [[647, 380], [105, 380]]}]],
                 'st': [[['src', 'load', 'src>load'], 'The runtime loads the text. A browser downloads it, Node.js reads it from the disk.'],
                        [['scan', 'load>scan'], 'The scanner cuts the characters into tokens: keywords, names, numbers, strings and punctuation.'],
                        [['parse', 'scan>parse'], 'The parser checks the grammar and builds a tree. A single SyntaxError here means nothing in the file runs.'],
                        [['ast', 'parse>ast', 'g0'], 'Scope analysis works out which variable every name refers to. Hoisting comes from this step.'],
                        [['ign', 'ast>ign'], 'Ignition turns the tree into bytecode and runs it straight away, while recording which types each line sees.'],
                        [['spark', 'ign>spark'], 'Functions that keep running are compiled by Sparkplug into simple machine code.'],
                        [['mag', 'tf', 'spark>mag', 'mag>tf', 'g1'], 'Hot functions go to Maglev, and the hottest to TurboFan, which make faster code from the recorded types.'],
                        [['tf>ign'], 'If a guess turns out wrong, for example a string arrives where numbers always came, the fast code is thrown away and the bytecode takes over again.'],
                        [['stack', 'heap'], 'While running, each call gets a frame on the call stack, and objects live on the heap.'],
                        [['gc', 'heap>gc'], 'The garbage collector frees heap objects that nothing can reach.'],
                        [['apis', 'loop', 'apis>loop', 'loop>stack', 'g2'], 'Timers, network and files are handled by the runtime. When they finish, the event loop runs their callbacks on the empty stack.']]},
}

PARTS = [
    part('big-picture', '🗺️', 'The journey of a JavaScript program', '''
<p>When you press Run, your <code>.js</code> file is only text. Two programs work together to turn that text into output. The <b>engine</b> understands the JavaScript language. The <b>runtime</b> (also called the host) is the program the engine lives inside, such as Chrome or Node.js, and it adds everything the language itself does not have: timers, the network, files and the web page.</p>
<div class="tw"><table class="jt"><tr><th>Piece</th><th>What it does</th><th>Real examples</th></tr>
<tr><td>Engine</td><td>Scans, parses, compiles and runs the code, and cleans up memory</td><td>V8 (Chrome, Edge, Node.js, Deno), SpiderMonkey (Firefox), JavaScriptCore (Safari, Bun)</td></tr>
<tr><td>Runtime</td><td>Loads files, provides the event loop and the extra APIs</td><td>A browser tab, Node.js, Deno, Bun, Electron apps, Cloudflare Workers</td></tr>
<tr><td>Extras from a browser</td><td><code>document</code>, <code>fetch</code>, <code>setTimeout</code>, <code>localStorage</code>, events</td><td>The Web APIs</td></tr>
<tr><td>Extras from Node.js</td><td><code>fs</code>, <code>http</code>, <code>process</code>, <code>setTimeout</code>, <code>fetch</code></td><td>Built on the libuv library</td></tr></table></div>
<div class="viz" data-viz="flow" data-k="pipeline"></div>
[[versions]]
<p>Think about what happens when you open a shopping site on your phone. Chrome downloads the page and its scripts, V8 turns those scripts into running code in a few milliseconds, and the same V8 keeps optimising the code that runs most, such as the function that recalculates your cart. When you tap "Add to cart", the browser notices the tap, and the event loop hands your click handler to V8 to run. Every part of this chapter is one step of that story.</p>
<div class="tw"><table class="jt"><tr><th>Step</th><th>Java</th><th>JavaScript</th></tr>
<tr><td>Who compiles first</td><td>You run <code>javac</code>, which writes a <code>.class</code> file of bytecode</td><td>Nobody. You ship the source text and the engine compiles it when it loads</td></tr>
<tr><td>What runs it</td><td>The JVM: class loader, bytecode verifier, interpreter, JIT, garbage collector</td><td>The engine: parser, Ignition interpreter, Sparkplug, Maglev and TurboFan, garbage collector</td></tr>
<tr><td>When errors show up</td><td>Type and syntax errors at compile time</td><td>Syntax errors when the file is parsed, type errors only when the line runs</td></tr>
<tr><td>Threads</td><td>Many threads by default</td><td>One thread per page or process, plus an event loop. Workers add more threads.</td></tr>
<tr><td>Python for comparison</td><td colspan="2">CPython compiles your <code>.py</code> to bytecode (<code>.pyc</code>) and interprets it. Since Python 3.13 it can also try an experimental JIT.</td></tr></table></div>
<div class="tip">You never call the compiler in JavaScript, but it is still there. V8 compiles in the background while your page runs. That is why the same code can get faster after it has run a few thousand times.</div>
''', kw=['JavaScript engine', 'runtime', 'host', 'V8', 'SpiderMonkey', 'JavaScriptCore', 'Node.js', 'libuv', 'Web APIs', 'how JavaScript runs', 'JavaScript vs Java', 'JIT']),
    part('loading', '📥', 'Step 1: loading the source text', '''
<p>The engine cannot read files or download anything itself. The <b>runtime</b> fetches the text and hands it over.</p>
<ul>
<li>In a <b>browser</b>, the HTML parser meets a <code>&lt;script&gt;</code> tag and downloads the file. A classic script blocks the page while it downloads and runs, <code>defer</code> and <code>type="module"</code> scripts wait until the HTML is parsed ({{ch:js-getting-started}} shows the timeline).</li>
<li>In <b>Node.js</b>, <code>node app.js</code> reads the file from disk. The file extension and the <code>"type"</code> field in package.json decide whether it is an ES module or a CommonJS file.</li>
<li>For an <b>ES module</b>, the runtime also finds and loads every file it imports before running any of them. That is covered in the modules part below.</li>
</ul>
<p>A CommonJS file gets a small surprise first: Node.js wraps your whole file in a function. That is why <code>require</code>, <code>module</code> and <code>__dirname</code> exist without being declared, and why a top level <code>return</code> works in a <code>.cjs</code> file but not in a <code>.mjs</code> one.</p>
[[wrapper]]
<div class="note">Big websites ship one or a few <b>bundled</b> files instead of hundreds of small ones. Bundlers such as Vite, esbuild and webpack join and shrink the files so the loading step takes fewer network trips.</div>
''', kw=['script loading', 'module wrapper', 'CommonJS', 'require', '__dirname', '__filename', 'ES module', 'type module', 'bundler', 'defer']),
    part('scanning', '🔤', 'Step 2: the scanner cuts text into tokens', '''
<p>The first thing the engine does with the text is <b>scanning</b> (also called lexing or tokenising). It reads the characters from left to right and groups them into <b>tokens</b>, the smallest pieces that mean something.</p>
<div class="tw"><table class="jt"><tr><th>Token kind</th><th>Examples from <code>let total = price * 2; // tax</code></th></tr>
<tr><td>Keyword</td><td><code>let</code></td></tr>
<tr><td>Identifier (name)</td><td><code>total</code>, <code>price</code></td></tr>
<tr><td>Punctuator (operator)</td><td><code>=</code>, <code>*</code>, <code>;</code></td></tr>
<tr><td>Literal</td><td><code>2</code>, and strings such as <code>"pen"</code></td></tr>
<tr><td>Thrown away</td><td>spaces, line breaks (it remembers where they were) and the comment <code>// tax</code></td></tr></table></div>
<p>Try it yourself below. Type a few lines and press the button. The animation walks your own code through scanning, parsing, the creation phase, bytecode and running, the same five steps this chapter explains one by one.</p>
<div class="viz" data-viz="engine"></div>
<p>The scanner always takes the <b>longest</b> token it can. That rule explains some puzzles you may meet in quizzes and code reviews.</p>
[[scanner]]
<div class="tip">Line breaks matter to the scanner because of <b>automatic semicolon insertion</b>. If a line ends where a statement could end, a semicolon is added. That is why <code>return</code> on its own line followed by an object returns <code>undefined</code> ({{ch:js-getting-started}} shows it).</div>
''', kw=['scanner', 'lexer', 'tokenizer', 'tokens', 'keyword', 'identifier', 'punctuator', 'literal', 'longest match', 'automatic semicolon insertion', 'ASI', 'numeric separator']),
    part('parsing', '🌳', 'Step 3: the parser builds a syntax tree', '''
<p>The <b>parser</b> reads the tokens and checks them against the grammar of JavaScript. If they fit, it builds an <b>abstract syntax tree</b> (AST): a tree of nodes such as <code>VariableDeclaration</code>, <code>BinaryExpression</code> and <code>CallExpression</code>. The tree keeps the meaning and drops the noise. In <code>price * qty + 40</code> the multiply sits lower in the tree than the add, so it is worked out first.</p>
<p>If the tokens do not fit the grammar, the parser throws a <code>SyntaxError</code> and the <b>whole file</b> is rejected. Not even line 1 runs.</p>
[[syntax-stop]]
<p>Some mistakes are grammatically fine but forbidden anyway. The specification calls them <b>early errors</b>, and the parser reports them before anything runs too: declaring the same <code>let</code> twice, a <code>const</code> with no value, or a <code>return</code> outside a function. Other problems, such as calling a function that does not exist, can only be found when the line actually runs.</p>
[[lazy]]
<h3>Lazy parsing</h3>
<p>Parsing a big web app fully at start up would be slow, so V8 <b>pre-parses</b> functions it has not needed yet. It only checks their grammar and remembers where they are. The full parse happens the first time the function is called. Functions wrapped in brackets, such as <code>(function () { ... })()</code>, are parsed fully at once because V8 guesses they run immediately.</p>
<div class="qa-box">A spec file with one missing bracket fails with a SyntaxError and <b>zero</b> tests run, so the report may show "0 tests" instead of a red test. Run <code>node --check file.js</code> or your linter in CI to catch it before the test run starts.</div>
''', qa=True, qa_why='A single syntax error makes a whole spec file report zero tests, and knowing early errors helps you read the message fast.',
        kw=['parser', 'AST', 'abstract syntax tree', 'SyntaxError', 'early errors', 'lazy parsing', 'pre-parsing', 'IIFE', 'node --check', 'grammar']),
    part('creation', '🏗️', 'Step 4: scopes and the creation phase', '''
<p>Before a script or a function runs, the engine sets up an <b>execution context</b> for it. This happens in two phases.</p>
<ol class="steps">
<li><b>Creation phase.</b> The engine creates the scope and a slot for every name declared in it. Function declarations are created whole. <code>var</code> names start as <code>undefined</code>. <code>let</code>, <code>const</code> and <code>class</code> names exist but are <b>uninitialised</b>: reading them throws, which is called the <b>temporal dead zone</b> (TDZ). The value of <code>this</code> is decided here too.</li>
<li><b>Execution phase.</b> The code runs line by line, giving variables their values and calling functions. Each function call repeats both phases for that function.</li>
</ol>
<div class="viz" data-viz="lanes" data-k="creation"></div>
[[creation]]
<p>Nothing is physically moved to the top of your file. "Hoisting" is simply the result of the creation phase: the names exist before their line runs. {{Ch:js-engine}} goes further into scope chains, closures and the rules of <code>this</code>.</p>
<div class="tw"><table class="jt"><tr><th>Declaration</th><th>After the creation phase</th><th>Read before its line</th></tr>
<tr><td><code>function f() {}</code></td><td>the whole function</td><td>works</td></tr>
<tr><td><code>var x = 1</code></td><td><code>undefined</code></td><td>gives <code>undefined</code></td></tr>
<tr><td><code>let x = 1</code>, <code>const x = 1</code></td><td>uninitialised (TDZ)</td><td>ReferenceError</td></tr>
<tr><td><code>class A {}</code></td><td>uninitialised (TDZ)</td><td>ReferenceError</td></tr>
<tr><td><code>const f = () =&gt; {}</code></td><td>uninitialised (TDZ)</td><td>ReferenceError, so arrow helpers must be defined before use</td></tr></table></div>
''', kw=['execution context', 'creation phase', 'execution phase', 'hoisting', 'temporal dead zone', 'TDZ', 'var', 'let', 'const', 'function declaration', 'global execution context']),
    part('bytecode', '⚙️', 'Step 5: Ignition turns the tree into bytecode', '''
<p>V8 does not run the tree directly. Its interpreter, <b>Ignition</b>, first turns the tree into <b>bytecode</b>: a list of small, simple instructions. Bytecode is much smaller than machine code, so it starts fast and saves memory on phones.</p>
<p>Ignition is a <b>register machine</b> with one special register, the <b>accumulator</b>. Most instructions read or write it. You can ask Node.js to print the real bytecode of a function with a V8 flag:</p>
[[bytecode]]
<div class="tw"><table class="jt"><tr><th>Instruction</th><th>Meaning in plain words</th></tr>
<tr><td><code>Ldar a1</code></td><td>Load argument 1 (<code>rate</code>) into the accumulator</td></tr>
<tr><td><code>Mul a0, FBV[0]</code></td><td>Multiply argument 0 (<code>price</code>) by the accumulator. <code>FBV[0]</code> is a feedback slot where V8 writes down the types it saw</td></tr>
<tr><td><code>Star0</code></td><td>Store the accumulator in register r0 (that is <code>tax</code>)</td></tr>
<tr><td><code>Ldar r0</code></td><td>Load r0 back into the accumulator</td></tr>
<tr><td><code>Add a0, FBV[1]</code></td><td>Add <code>price</code> to it, and record the types in feedback slot 1</td></tr>
<tr><td><code>Return</code></td><td>Give the accumulator back to the caller</td></tr></table></div>
<p>The <b>feedback slots</b> are the important part. Every time the line runs, Ignition notes what it saw: "always small whole numbers" or "a number and a string". The optimising compilers in step 7 read these notes. The engine animation above uses the same instruction names, so you can watch the accumulator change for your own code.</p>
<div class="note">The exact bytecode changes between V8 versions, and the flag is a debugging tool, not something to use in production. The numbers on the left are positions in the source text, which is how a stack trace knows your line and column.</div>
''', kw=['bytecode', 'Ignition', 'interpreter', 'accumulator', 'register machine', 'feedback vector', 'type feedback', '--print-bytecode', 'Ldar', 'Star']),
    part('execution', '📚', 'Step 6: running: the call stack, the heap and garbage collection', '''
<p>While the bytecode runs, the engine uses two areas of memory.</p>
<ul>
<li>The <b>call stack</b> holds one <b>frame</b> for every function that has started and not yet returned: its arguments, its local variables and where to go back to. It is small and very fast. Too many nested calls give <code>RangeError: Maximum call stack size exceeded</code>.</li>
<li>The <b>heap</b> holds objects, arrays, functions and long strings. Variables keep a <b>reference</b> (an address) to them. Copying the variable copies the reference, so two names can share one object.</li>
</ul>
<div class="viz" data-viz="lanes" data-k="stackheap"></div>
[[stack-heap]]
<h3>Garbage collection</h3>
<p>You never free memory yourself. The <b>garbage collector</b> keeps every object that can be reached from the <b>roots</b> (global variables and the variables on the stack) and frees the rest. V8's collector is called Orinoco. New objects start in a small young area that is cleaned very often, because most objects are thrown away quickly, like the temporary arrays a <code>map</code> creates. Objects that survive move to the old area, which is cleaned less often with mark and sweep. Most of the work happens on helper threads, so pauses stay short.</p>
[[gc-weak]]
<div class="qa-box">A memory leak in JavaScript means something still <b>reaches</b> an object you no longer need: a global array that keeps growing, a listener that was never removed, or a cache with no limit. In long UI test runs, watch the memory graph in Chrome DevTools or compare two heap snapshots ({{ch:js-expert}}).</div>
''', qa=True, qa_why='Reference copies explain test data that changes between tests, and reachability explains memory leaks in long test runs.',
        kw=['call stack', 'stack frame', 'heap', 'reference', 'primitive', 'copy by value', 'shared object', 'garbage collection', 'roots', 'reachability', 'young generation', 'old generation', 'Orinoco', 'WeakRef', 'memory leak', 'Maximum call stack size exceeded']),
    part('jit', '🚀', 'Step 7: hot code gets compiled: Sparkplug, Maglev and TurboFan', '''
<p>Interpreting bytecode is quick to start but slower to run. So V8 watches which functions run often and compiles them to <b>machine code</b> while the program is running. This is <b>just in time</b> (JIT) compilation, and V8 has three compilers for it, each one slower to compile but producing faster code.</p>
<div class="tw"><table class="jt"><tr><th>Tier</th><th>Used for</th><th>How it works</th></tr>
<tr><td>Ignition</td><td>Everything, at first</td><td>Interprets bytecode and collects type feedback</td></tr>
<tr><td>Sparkplug</td><td>Functions that are warm</td><td>Turns bytecode into machine code almost one to one, no optimisation</td></tr>
<tr><td>Maglev</td><td>Functions that are hot</td><td>Uses the feedback to make good machine code quickly</td></tr>
<tr><td>TurboFan</td><td>The hottest code, such as tight loops</td><td>Uses the feedback to make the fastest code, and takes the longest to compile</td></tr></table></div>
<p>Optimised code is built on <b>guesses</b>. If <code>lineTotal</code> has only ever seen small whole numbers, the fast code handles only small whole numbers. When a string arrives, the guess is wrong, so V8 <b>deoptimises</b>: it throws the fast code away, continues in the bytecode and may optimise again later with the new knowledge. This run is real. Watch the V8 messages between the program's own lines:</p>
[[jit]]
<p>How to read the trace: "hot and stable" means the function ran often and its type feedback stopped changing. "not a Smi" means the value was not a <b>Smi</b>, V8's name for a small integer that fits directly in a register. This flag does not list Sparkplug compiles, which have a separate trace flag. Notice that the program still printed the right answers. Deoptimisation only costs speed, never correctness. In daily work this matters for code that runs millions of times, such as parsing a large log file or drawing a chart, and it is the reason for a simple habit: keep the types going into a hot function the same.</p>
<div class="tip">Firefox and Safari use the same idea with different names. SpiderMonkey has a baseline interpreter, a baseline compiler and the Warp optimiser. JavaScriptCore has LLInt, Baseline, DFG and FTL.</div>
''', kw=['JIT', 'just in time', 'Sparkplug', 'Maglev', 'TurboFan', 'machine code', 'optimisation', 'deoptimisation', 'deopt', 'type feedback', 'hot function', '--trace-opt', '--trace-deopt', 'SpiderMonkey Warp', 'JavaScriptCore FTL']),
    part('runtime', '🔄', 'Step 8: the runtime, Web APIs and the event loop', '''
<p>The engine runs one piece of code at a time on one thread. So how does a page wait for a server without freezing? It does not wait. A call such as <code>setTimeout</code> or <code>fetch</code> hands the waiting to the <b>runtime</b>, which does it outside JavaScript (the browser's timers and network code, or libuv in Node.js). When the waiting is over, the runtime puts a callback into a <b>queue</b>.</p>
<ol class="steps">
<li>The <b>call stack</b> runs the current job until it is empty.</li>
<li>Then the <b>microtask queue</b> is emptied completely: promise callbacks, <code>await</code> continuations and <code>queueMicrotask</code>.</li>
<li>Then the event loop takes <b>one</b> task from the <b>task queue</b>: a timer, a click, a network response. Then back to step 2.</li>
<li>Between tasks, the browser may repaint the screen, roughly every 16 ms on a 60 Hz display.</li>
</ol>
<p>Write your own lines in the simulator and predict the console before you press Play.</p>
<div class="viz" data-viz="loopsim"></div>
[[loop]]
<p>Node.js follows the same idea and splits the task side into phases (timers, poll for I/O, check for <code>setImmediate</code>), which {{ch:js-engine}} shows. Promises and <code>async</code> code get a full chapter in {{ch:js-async}}.</p>
<div class="qa-box">This order is why a test that forgets an <code>await</code> can finish and report "passed" before the check inside a <code>.then</code> has even run. It is also why Playwright's auto waiting works: it keeps giving the page turns of the event loop until the element is ready.</div>
''', qa=True, qa_why='The event loop explains missing await bugs, log orders and why fixed sleeps make tests slow and flaky.',
        kw=['event loop', 'call stack', 'Web APIs', 'libuv', 'task queue', 'macrotask', 'callback queue', 'microtask queue', 'setTimeout', 'Promise then', 'queueMicrotask', 'single thread', 'non blocking', 'rendering']),
    part('modules', '📦', 'Modules: load, link, then evaluate', '''
<p>An ES module is not run the moment it is read. The runtime and the engine go through three phases for the whole graph of files.</p>
<ol class="steps">
<li><b>Construction</b>: find, download and parse the entry file, read its <code>import</code> lines, then do the same for every imported file. No code runs yet.</li>
<li><b>Linking</b>: connect every <code>import</code> to the matching <code>export</code>. A misspelled export name fails here, before any code runs.</li>
<li><b>Evaluation</b>: run each module body once, dependencies first. A module imported by many files still runs only once.</li>
</ol>
[[modules]]
<p>Two things in that output surprise people. The <code>console.log</code> at the top of main.mjs ran <b>last</b>, because imports are processed before the body. And <code>price</code> changed after <code>bump()</code>, because an import is a <b>live binding</b> to the exporting module's variable, not a copy of its value. CommonJS <code>require</code> works differently: it runs the file when the line is reached and returns a copy of <code>module.exports</code>.</p>
<div class="note">Top level <code>await</code> fits into the evaluation phase: a module that awaits pauses its own evaluation and the modules that depend on it, while other branches of the graph carry on.</div>
''', kw=['ES modules', 'module graph', 'construction', 'linking', 'evaluation', 'live binding', 'import hoisting', 'module runs once', 'top level await', 'CommonJS vs ESM']),
    part('scenario', '🎬', 'Real world scenario: a frozen page on sale day', '''
<div class="scenario"><b>The situation</b>During a big sale, users report that the "Apply coupon" button does nothing for half a second after the cart loads. The code has no errors. A tester records the problem and a developer measures it.</div>
<p>The cart runs a long synchronous calculation over every item. While it runs, the call stack is never empty, so the event loop cannot run click handlers, timers or painting. The code below measures this with a timer that should fire after 50 ms.</p>
[[scenario]]
<p>The fix does the same total work in small chunks and gives the event loop a turn between them. Clicks and paints now get in between the chunks, so the page feels responsive. In a browser, the newer <code>scheduler.yield()</code> does the same job in Chrome and Edge, and very heavy work can move to a Web Worker on another thread ({{ch:js-expert}}).</p>
<div class="qa-box">Lighthouse and the Performance panel in DevTools mark any task over 50 ms as a <b>long task</b>, and the Interaction to Next Paint (INP) metric shows how long users waited after a tap. Both are good evidence to attach to a bug report about a slow page.</div>
''', qa=True, qa_why='Long tasks are a common cause of slow, flaky UI tests and of performance bugs that testers report.',
        kw=['long task', 'blocking the event loop', 'responsive UI', 'chunking', 'setTimeout 0', 'scheduler.yield', 'Web Worker', 'INP', 'Interaction to Next Paint', 'Lighthouse', 'performance bug']),
]

INFO = {'title': 'From text to output in eight steps', 'panels': [
    panel([['e', '📥'], ['t', 'load → scan → parse', {'b': 1}]], 'Read and check', 'The text becomes tokens, then a tree.', 'One syntax error and nothing runs.'),
    panel([['e', '🏗️'], ['t', 'var = undefined, let = TDZ', {'b': 1}]], 'Set up names', 'The creation phase makes every slot first.', 'That is all hoisting really is.'),
    panel([['e', '⚙️'], ['t', 'Ignition → Maglev → TurboFan', {'b': 1}]], 'Run, then speed up', 'Bytecode starts quickly.', 'Hot code is compiled using the types it saw.'),
    panel([['e', '🔄'], ['t', 'stack → microtasks → task', {'b': 1}]], 'Wait without blocking', 'The runtime waits, the loop runs callbacks.', 'One job at a time, on one thread.')],
    'remember': 'The engine reads all of the file before running it, runs it as bytecode, makes hot code faster with guesses, and leaves the waiting to the runtime.'}

REAL = [
    ['🛒', 'A sale day freeze', 'A cart calculation blocked the main thread for 400 ms, so taps did nothing. Splitting the work into chunks fixed it without any server change.'],
    ['🧪', 'Zero tests ran', 'A CI job reported "0 tests" after a merge. One missing bracket in a shared helper made every spec that imported it fail to parse.'],
    ['📈', 'A slow log parser', 'A function that sometimes got numbers and sometimes strings kept deoptimising. Converting the input once at the start made it several times faster.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter follows one JavaScript program from a text file to the output: loading, scanning, parsing, the creation phase, bytecode, running, optimising and the event loop.',
        'यह अध्याय एक JavaScript program को text file से output तक ले जाता है: loading, scanning, parsing, creation phase, bytecode, चलना, optimising और event loop।',
        'ಈ ಅಧ್ಯಾಯ ಒಂದು JavaScript program ಅನ್ನು text file ನಿಂದ output ವರೆಗೆ ತೋರಿಸುತ್ತದೆ: loading, scanning, parsing, creation phase, bytecode, ಓಡುವುದು, optimising ಮತ್ತು event loop.',
        'ଏହି ଅଧ୍ୟାୟ ଗୋଟିଏ JavaScript program କୁ text file ରୁ output ପର୍ଯ୍ୟନ୍ତ ଦେଖାଏ: loading, scanning, parsing, creation phase, bytecode, ଚାଲିବା, optimising ଓ event loop।',
        'يتبع هذا الفصل برنامج JavaScript من ملف نصي حتى الناتج: التحميل والمسح والتحليل ومرحلة الإنشاء والبايت كود والتشغيل والتحسين وحلقة الأحداث.',
        'Dieses Kapitel folgt einem JavaScript-Programm von der Textdatei bis zur Ausgabe: Laden, Scannen, Parsen, Erstellungsphase, Bytecode, Ausführen, Optimieren und Event Loop.'),
    say('big-picture', 'The big picture', 'The engine understands the language. The runtime, such as Chrome or Node.js, loads files and adds timers, the network and the page. Java compiles first with javac, JavaScript is compiled by the engine while it loads.',
        'Engine भाषा समझता है। Runtime, जैसे Chrome या Node.js, files load करता है और timers, network और page देता है। Java पहले javac से compile होता है, JavaScript को engine load करते समय compile करता है।',
        'Engine ಭಾಷೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುತ್ತದೆ. Chrome ಅಥವಾ Node.js ನಂತಹ runtime files load ಮಾಡಿ timers, network ಮತ್ತು page ಕೊಡುತ್ತದೆ. Java ಮೊದಲು javac ನಿಂದ compile ಆಗುತ್ತದೆ.',
        'Engine ଭାଷା ବୁଝେ। Chrome କିମ୍ବା Node.js ପରି runtime files load କରେ ଓ timers, network ଓ page ଦିଏ। Java ପ୍ରଥମେ javac ରେ compile ହୁଏ।',
        'المحرك يفهم اللغة، وبيئة التشغيل مثل Chrome أو Node.js تحمّل الملفات وتضيف المؤقتات والشبكة والصفحة. تُترجم Java أولًا بـ javac، أما JavaScript فيترجمها المحرك أثناء التحميل.',
        'Die Engine versteht die Sprache. Die Laufzeit, etwa Chrome oder Node.js, lädt Dateien und liefert Timer, Netzwerk und Seite. Java wird vorher mit javac kompiliert, JavaScript beim Laden.'),
    say('loading', 'Loading', 'The runtime loads the text. A browser downloads it, Node.js reads it from disk, and a CommonJS file is wrapped in a function that provides require and module.',
        'Runtime text load करता है। Browser उसे download करता है, Node.js disk से पढ़ता है, और CommonJS file एक function में लपेटी जाती है जो require और module देता है।',
        'Runtime text load ಮಾಡುತ್ತದೆ. Browser download ಮಾಡುತ್ತದೆ, Node.js disk ನಿಂದ ಓದುತ್ತದೆ, CommonJS file ಒಂದು function ನಲ್ಲಿ ಸುತ್ತಲಾಗುತ್ತದೆ.',
        'Runtime text load କରେ। Browser download କରେ, Node.js disk ରୁ ପଢ଼େ, CommonJS file ଗୋଟିଏ function ରେ ଘୋଡ଼ା ହୁଏ।',
        'بيئة التشغيل تحمّل النص. المتصفح ينزّله وNode.js يقرأه من القرص، وملف CommonJS يُلف داخل دالة توفر require وmodule.',
        'Die Laufzeit lädt den Text. Ein Browser lädt ihn herunter, Node.js liest ihn von der Platte, und eine CommonJS-Datei wird in eine Funktion mit require und module gepackt.'),
    say('scanning', 'Scanning', 'The scanner reads characters and makes tokens such as keywords, names, numbers and symbols. It always takes the longest token it can, and it drops spaces and comments.',
        'Scanner characters पढ़कर tokens बनाता है, जैसे keywords, names, numbers और symbols। वह हमेशा सबसे लंबा token लेता है और spaces और comments छोड़ देता है।',
        'Scanner characters ಓದಿ keywords, names, numbers ಮತ್ತು symbols ನಂತಹ tokens ಮಾಡುತ್ತದೆ. ಅದು ಉದ್ದದ token ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ.',
        'Scanner characters ପଢ଼ି keywords, names, numbers ଓ symbols ପରି tokens ତିଆରି କରେ। ଏହା ସବୁଠାରୁ ଲମ୍ବା token ନିଏ।',
        'الماسح يقرأ الحروف ويصنع رموزًا مثل الكلمات المحجوزة والأسماء والأرقام والعلامات، ويأخذ دائمًا أطول رمز ممكن ويترك المسافات والتعليقات.',
        'Der Scanner liest Zeichen und bildet Tokens wie Schlüsselwörter, Namen, Zahlen und Zeichen. Er nimmt immer das längste Token und verwirft Leerzeichen und Kommentare.'),
    say('parsing', 'Parsing', 'The parser turns tokens into a syntax tree. One syntax error, or an early error such as declaring let twice, rejects the whole file, so not even line one runs.',
        'Parser tokens को syntax tree में बदलता है। एक syntax error, या let को दो बार declare करने जैसा early error, पूरी file रोक देता है, इसलिए पहली line भी नहीं चलती।',
        'Parser tokens ಅನ್ನು syntax tree ಆಗಿ ಮಾಡುತ್ತದೆ. ಒಂದು syntax error ಇಡೀ file ತಡೆಯುತ್ತದೆ, ಮೊದಲ ಸಾಲು ಕೂಡ ಓಡುವುದಿಲ್ಲ.',
        'Parser tokens କୁ syntax tree କରେ। ଗୋଟିଏ syntax error ପୂରା file ରୋକେ, ପ୍ରଥମ ଧାଡ଼ି ମଧ୍ୟ ଚାଲେ ନାହିଁ।',
        'المحلل يحول الرموز إلى شجرة بناء. خطأ نحوي واحد أو خطأ مبكر مثل تعريف let مرتين يرفض الملف كله، فلا يعمل حتى السطر الأول.',
        'Der Parser macht aus Tokens einen Syntaxbaum. Ein Syntaxfehler oder ein früher Fehler wie zweimal let lehnt die ganze Datei ab, nicht einmal Zeile eins läuft.'),
    say('creation', 'Creation phase', 'Before running, the engine makes a slot for every name. Functions are ready, var is undefined, and let, const and class stay uninitialised in the temporal dead zone.',
        'चलने से पहले engine हर नाम के लिए जगह बनाता है। Functions तैयार रहते हैं, var undefined होता है, और let, const और class temporal dead zone में रहते हैं।',
        'ಓಡುವ ಮೊದಲು engine ಪ್ರತಿ ಹೆಸರಿಗೆ ಜಾಗ ಮಾಡುತ್ತದೆ. Functions ಸಿದ್ಧ, var undefined, let const class TDZ ನಲ್ಲಿ.',
        'ଚାଲିବା ପୂର୍ବରୁ engine ପ୍ରତ୍ୟେକ ନାମ ପାଇଁ ସ୍ଥାନ କରେ। Functions ପ୍ରସ୍ତୁତ, var undefined, let const class TDZ ରେ।',
        'قبل التشغيل يصنع المحرك مكانًا لكل اسم. الدوال جاهزة وvar قيمته undefined، أما let وconst وclass فتبقى غير مهيأة في المنطقة الميتة مؤقتًا.',
        'Vor dem Start legt die Engine für jeden Namen einen Platz an. Funktionen sind fertig, var ist undefined, let, const und class bleiben in der TDZ.'),
    say('bytecode', 'Bytecode', 'Ignition turns the tree into short bytecode instructions that use an accumulator register, and it records which types each line sees in feedback slots.',
        'Ignition tree को छोटे bytecode instructions में बदलता है जो accumulator register इस्तेमाल करते हैं, और feedback slots में लिखता है कि हर line ने कौन से types देखे।',
        'Ignition tree ಅನ್ನು accumulator ಬಳಸುವ ಸಣ್ಣ bytecode instructions ಆಗಿ ಮಾಡುತ್ತದೆ ಮತ್ತು types ಅನ್ನು feedback slots ನಲ್ಲಿ ಬರೆಯುತ್ತದೆ.',
        'Ignition tree କୁ accumulator ବ୍ୟବହାର କରୁଥିବା ଛୋଟ bytecode instructions କରେ ଓ types କୁ feedback slots ରେ ଲେଖେ।',
        'يحول Ignition الشجرة إلى تعليمات بايت كود قصيرة تستخدم سجل التجميع، ويسجل في خانات التغذية الراجعة أنواع القيم التي يراها كل سطر.',
        'Ignition macht aus dem Baum kurze Bytecode-Befehle mit einem Akkumulator und notiert in Feedback-Slots, welche Typen jede Zeile sieht.'),
    say('execution', 'Stack and heap', 'Each call gets a frame on the call stack. Objects live on the heap and variables hold references to them. The garbage collector frees objects nothing can reach.',
        'हर call को call stack पर एक frame मिलता है। Objects heap पर रहते हैं और variables उनका reference रखते हैं। Garbage collector उन objects को हटाता है जिन तक कोई नहीं पहुँचता।',
        'ಪ್ರತಿ call ಗೆ call stack ನಲ್ಲಿ frame. Objects heap ನಲ್ಲಿ, variables reference ಹಿಡಿಯುತ್ತವೆ. ತಲುಪಲಾಗದ objects ಅನ್ನು garbage collector ತೆಗೆಯುತ್ತದೆ.',
        'ପ୍ରତ୍ୟେକ call ପାଇଁ call stack ରେ frame। Objects heap ରେ, variables reference ରଖନ୍ତି। ପହଞ୍ଚି ନ ହେଉଥିବା objects କୁ garbage collector ହଟାଏ।',
        'كل استدعاء يأخذ إطارًا على مكدس الاستدعاءات. الكائنات تعيش في الكومة والمتغيرات تحمل مراجع إليها، وجامع المهملات يحرر ما لا يمكن الوصول إليه.',
        'Jeder Aufruf bekommt einen Rahmen auf dem Stack. Objekte liegen im Heap, Variablen halten Referenzen. Der Garbage Collector gibt Unerreichbares frei.'),
    say('jit', 'JIT tiers', 'Warm functions go to Sparkplug, hot ones to Maglev and the hottest to TurboFan. If a type guess breaks, V8 deoptimises and the bytecode takes over again.',
        'Warm functions Sparkplug में, hot functions Maglev में और सबसे hot TurboFan में जाते हैं। Type का अनुमान गलत हो तो V8 deoptimise करता है और bytecode फिर चलता है।',
        'Warm functions Sparkplug ಗೆ, hot functions Maglev ಗೆ, ಅತಿ hot TurboFan ಗೆ. Type ಊಹೆ ತಪ್ಪಾದರೆ V8 deoptimise ಮಾಡುತ್ತದೆ.',
        'Warm functions Sparkplug କୁ, hot functions Maglev କୁ, ସବୁଠାରୁ hot TurboFan କୁ। Type ଅନୁମାନ ଭୁଲ ହେଲେ V8 deoptimise କରେ।',
        'الدوال الدافئة تذهب إلى Sparkplug والساخنة إلى Maglev والأشد سخونة إلى TurboFan. إذا خاب تخمين النوع يلغي V8 التحسين ويعود البايت كود للعمل.',
        'Warme Funktionen gehen zu Sparkplug, heiße zu Maglev, die heißesten zu TurboFan. Bricht eine Typannahme, deoptimiert V8 und der Bytecode übernimmt.'),
    say('runtime', 'Event loop', 'Waiting is done by the runtime. When the call stack is empty, the event loop runs every microtask, then one task such as a timer or a click, and repeats.',
        'इंतज़ार runtime करता है। Call stack खाली होने पर event loop सारे microtasks चलाता है, फिर एक task जैसे timer या click, और फिर दोहराता है।',
        'ಕಾಯುವುದನ್ನು runtime ಮಾಡುತ್ತದೆ. Stack ಖಾಲಿಯಾದಾಗ event loop ಎಲ್ಲಾ microtasks, ನಂತರ ಒಂದು task ಓಡಿಸುತ್ತದೆ.',
        'ଅପେକ୍ଷା runtime କରେ। Stack ଖାଲି ହେଲେ event loop ସବୁ microtasks, ତାପରେ ଗୋଟିଏ task ଚଲାଏ।',
        'الانتظار تقوم به بيئة التشغيل. عندما يفرغ المكدس تنفذ حلقة الأحداث كل المهام الدقيقة ثم مهمة واحدة مثل مؤقت أو نقرة، وتكرر ذلك.',
        'Das Warten übernimmt die Laufzeit. Ist der Stack leer, führt die Event Loop alle Microtasks aus, dann eine Aufgabe wie einen Timer oder Klick, und wiederholt das.'),
    say('modules', 'Modules', 'Modules are found and parsed first, then linked, then evaluated with dependencies first. Each module runs once, and imports are live bindings.',
        'Modules पहले ढूँढे और parse किए जाते हैं, फिर link, फिर dependencies पहले evaluate होती हैं। हर module एक बार चलता है और imports live bindings होते हैं।',
        'Modules ಮೊದಲು parse, ನಂತರ link, ನಂತರ dependencies ಮೊದಲು evaluate ಆಗುತ್ತವೆ. ಪ್ರತಿ module ಒಮ್ಮೆ ಓಡುತ್ತದೆ.',
        'Modules ପ୍ରଥମେ parse, ତାପରେ link, ତାପରେ dependencies ପ୍ରଥମେ evaluate ହୁଏ। ପ୍ରତ୍ୟେକ module ଥରେ ଚାଲେ।',
        'تُكتشف الوحدات وتُحلل أولًا ثم تُربط ثم تُقيّم بدءًا بالاعتماديات. كل وحدة تعمل مرة واحدة، والاستيرادات روابط حية.',
        'Module werden zuerst gefunden und geparst, dann verknüpft, dann ausgewertet, Abhängigkeiten zuerst. Jedes Modul läuft einmal, Importe sind lebende Bindungen.'),
    say('scenario', 'Scenario', 'A long synchronous job blocked the event loop, so taps did nothing. Splitting it into chunks with a pause between them kept the page responsive.',
        'एक लंबे synchronous काम ने event loop रोक दिया, इसलिए taps काम नहीं कर रहे थे। उसे टुकड़ों में बाँटने से page फिर जल्दी जवाब देने लगा।',
        'ಉದ್ದ synchronous ಕೆಲಸ event loop ತಡೆಯಿತು. ಅದನ್ನು ತುಂಡುಗಳಾಗಿ ಮಾಡಿದಾಗ page ಮತ್ತೆ ಸ್ಪಂದಿಸಿತು.',
        'ଲମ୍ବା synchronous କାମ event loop ରୋକିଲା। ଏହାକୁ ଖଣ୍ଡ କଲାରୁ page ପୁଣି ସାଡ଼ା ଦେଲା।',
        'عمل متزامن طويل أوقف حلقة الأحداث فلم تستجب النقرات، وتقسيمه إلى أجزاء مع استراحة بينها أبقى الصفحة سريعة الاستجابة.',
        'Eine lange synchrone Aufgabe blockierte die Event Loop, Taps taten nichts. In Stücke geteilt, mit Pausen dazwischen, blieb die Seite reaktionsschnell.'),
    say('practice', 'Hands-on', 'Practise predicting hoisting, running bytecode with an accumulator, ordering event loop output and finding the order in which modules run.',
        'Hoisting का अनुमान, accumulator के साथ bytecode चलाना, event loop output का क्रम और modules के चलने का क्रम निकालने का अभ्यास करें।',
        'Hoisting ಊಹೆ, accumulator ಜೊತೆ bytecode, event loop ಕ್ರಮ ಮತ್ತು modules ಓಡುವ ಕ್ರಮ ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Hoisting ଅନୁମାନ, accumulator ସହ bytecode, event loop କ୍ରମ ଓ modules ଚାଲିବା କ୍ରମ ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على توقع الرفع وتشغيل البايت كود بسجل التجميع وترتيب ناتج حلقة الأحداث ومعرفة ترتيب تشغيل الوحدات.',
        'Übe Hoisting vorherzusagen, Bytecode mit einem Akkumulator auszuführen, die Event-Loop-Ausgabe zu ordnen und die Reihenfolge der Module zu finden.'),
]

QUIZ = [
    quiz('e', 'Which part turns your JavaScript text into running code?', ['The engine, such as V8', 'The runtime only', 'npm', 'The DOM'], 0, 'Chrome and Node.js both contain it.', 'The engine scans, parses, compiles and runs. The runtime around it loads files and adds timers, the network and the page.'),
    quiz('e', 'A file has a typo on line 40. What happens to line 1?', ['It never runs, the whole file is rejected', 'It runs, then the error appears on line 40', 'Only line 40 is skipped', 'The browser fixes the typo'], 0, 'Parsing comes before running.', 'The parser reads the whole file first. A SyntaxError anywhere means nothing in the file runs.'),
    quiz('e', 'What does the scanner produce?', ['Tokens', 'Machine code', 'A heap snapshot', 'HTML'], 0, 'Small pieces such as let, price and =.', 'Tokens go to the parser, which builds the syntax tree.'),
    quiz('m', 'Where do require and __dirname come from in a CommonJS file?', ['Node.js wraps the file in a function with those parameters', 'They are JavaScript keywords', 'npm adds them', 'The browser provides them'], 0, 'Look at the wrapper example.', 'The module wrapper is (function (exports, require, module, __filename, __dirname) { ... }).'),
    quiz('m', 'What does the first line print?', ['undefined', '100', 'It throws a ReferenceError', 'null'], 0, 'var is set to undefined in the creation phase.', 'The slot for total exists from the creation phase, but its value 100 is only assigned when line 2 runs.', code='console.log(total);\nvar total = 100;'),
    quiz('m', 'What is the accumulator in V8 bytecode?', ['A special register most instructions read and write', 'The garbage collector', 'The list of tokens', 'A queue of promises'], 0, 'Ldar loads it, Star stores it.', 'Ignition is a register machine with one implicit accumulator register.'),
    quiz('m', 'Two variables point at the same object. You change a property through one. What does the other see?', ['The change, because they share one heap object', 'The old value, objects are copied', 'undefined', 'A TypeError'], 0, 'Copying a variable copies the reference.', 'Only primitive values are copied. Objects stay on the heap and are shared.'),
    quiz('h', 'Why does V8 deoptimise a function?', ['A guess the fast code was built on, such as the type of an argument, turned out wrong', 'The function threw an error', 'The garbage collector ran', 'The function was called too few times'], 0, 'Optimised code relies on type feedback.', 'When the guess fails, V8 drops the fast code and continues in the bytecode, which handles every type.'),
    quiz('h', 'What prints first after the script ends?', ['The promise callback', 'The setTimeout callback', 'They alternate', 'Neither runs'], 0, 'Microtasks before tasks.', 'The microtask queue is emptied before the event loop takes the next task, even for a 0 ms timer.', code='setTimeout(() => console.log("timer"), 0);\nPromise.resolve().then(() => console.log("promise"));'),
    quiz('h', 'main.mjs logs "main", then imports a.mjs which logs "a". What is the output order?', ['a, then main', 'main, then a', 'Only main', 'It depends on the network'], 0, 'Imports are processed before the body.', 'In an ES module, all imports are loaded, linked and evaluated before the importing module body runs.'),
    quiz('x', 'Which is the correct order of V8 tiers from first to last?', ['Ignition, Sparkplug, Maglev, TurboFan', 'TurboFan, Maglev, Sparkplug, Ignition', 'Sparkplug, Ignition, TurboFan, Maglev', 'Maglev, Ignition, TurboFan, Sparkplug'], 0, 'Interpreter first, best optimiser last.', 'Each tier compiles more slowly and produces faster code.'),
    quiz('x', 'Which mistake is an early error found before any line runs?', ['Declaring the same let twice in one scope', 'Calling a function that does not exist', 'Reading a property of undefined', 'Dividing by zero'], 0, 'Early errors are part of parsing.', 'Duplicate let, const with no value and return outside a function are early errors. The others only fail when the line runs, and dividing by zero just gives Infinity.'),
]

CALC = [
    calc('e', 'How many tokens does the scanner make from this line? Count every keyword, name, number and symbol.', '7', 'Comments and spaces are not tokens.', ['<code>let</code>, <code>total</code>, <code>=</code>, <code>price</code>, <code>*</code>, <code>2</code> and the semicolon at the end.', 'That is 7 tokens.'], code='let total = price * 2; // tax'),
    calc('e', 'The bytecode for addTax had a "Bytecode length" of 12 bytes. Ldar takes 2 bytes, Mul 3, Star0 1, Ldar 2, Add 3. How many bytes does Return take?', '1', 'Subtract the others from 12.', ['<span class="eq">2 + 3 + 1 + 2 + 3 = 11</span>', '<span class="eq">12 − 11 = 1</span>']),
    calc('m', 'What does addTax(250, 0.2) return?', '300', 'tax is price times rate.', ['<span class="eq">tax = 250 × 0.2 = 50</span>', '<span class="eq">250 + 50 = 300</span>']),
    calc('m', 'A page runs 3 synchronous logs, 2 promise callbacks and 4 timers. How many lines print before the first timer?', '5', 'Sync first, then all microtasks.', ['<span class="eq">3 + 2 = 5</span>']),
    calc('m', 'A display refreshes 60 times a second. About how many whole milliseconds does each frame get?', '16', 'One second is 1000 ms.', ['<span class="eq">1000 ÷ 60 ≈ 16.7</span>', 'So about 16 whole ms, which is why long tasks cause dropped frames.']),
    calc('h', 'A 400 ms job is split into 20 ms chunks. How many times does the event loop get a turn between chunks?', '19', 'Count the gaps between chunks.', ['<span class="eq">400 ÷ 20 = 20</span> chunks', 'There are <span class="eq">20 − 1 = 19</span> gaps between them.']),
    calc('h', 'makeOrder runs, creates an array and an object, and returns the object into order. After the call, how many heap objects are still reachable?', '2', 'The object points at the array.', ['order reaches the object, and the object reaches the array.', 'Both stay alive: 2.']),
    calc('x', 'A module graph: main imports a and b, a imports c, b imports c. How many module bodies run in total?', '4', 'Each module runs once.', ['c, a, b and main each run once, even though c is imported twice.', 'That is 4.']),
]

EX = [
    ex('hoisted', 'e', 'What does early access give', '<p>Write <code>earlyRead(kind)</code>. It gets how a name was declared, <code>"var"</code>, <code>"let"</code>, <code>"const"</code>, <code>"class"</code> or <code>"function"</code>, and returns what reading that name <b>before</b> its line gives: <code>"undefined"</code>, <code>"ReferenceError"</code> or <code>"function"</code>.</p>',
       'function earlyRead(kind) {\n  return "undefined";\n}\n',
       [('earlyRead("var")', 'undefined'), ('earlyRead("let")', 'ReferenceError'), ('earlyRead("const")', 'ReferenceError'), ('earlyRead("class")', 'ReferenceError'), ('earlyRead("function")', 'function')],
       'function earlyRead(kind) {\n  if (kind === "var") return "undefined";\n  if (kind === "function") return "function";\n  return "ReferenceError";\n}',
       hint='Only two kinds have a usable value after the creation phase.', why='var gets undefined and function declarations are created whole. Everything else sits in the temporal dead zone.'),
    ex('accumulator', 'm', 'Run bytecode with an accumulator', '<p>Write <code>runBytecode(code, args)</code>. <code>code</code> is a list of instructions such as <code>["Ldar", "a1"]</code>. Support <code>LdaSmi n</code> (put n in the accumulator), <code>Ldar x</code> (load register or argument x), <code>Star x</code> (store the accumulator in register x), <code>Add x</code> and <code>Mul x</code> (x plus or times the accumulator) and <code>Return</code> (return the accumulator). Arguments are named <code>a0</code>, <code>a1</code> and so on.</p>',
       'function runBytecode(code, args) {\n  let acc;\n  const regs = {};\n  return acc;\n}\n',
       [('runBytecode([["Ldar", "a1"], ["Mul", "a0"], ["Star", "r0"], ["Ldar", "r0"], ["Add", "a0"], ["Return"]], [100, 0.5])', 150),
        ('runBytecode([["LdaSmi", 2], ["Star", "r0"], ["LdaSmi", 3], ["Mul", "r0"], ["Return"]], [])', 6),
        ('runBytecode([["LdaSmi", 7], ["Return"], ["LdaSmi", 9]], [])', 7)],
       'function runBytecode(code, args) {\n  let acc;\n  const regs = {};\n  const read = x => (x[0] === "a" ? args[Number(x.slice(1))] : regs[x]);\n  for (const [op, x] of code) {\n    if (op === "LdaSmi") acc = x;\n    else if (op === "Ldar") acc = read(x);\n    else if (op === "Star") regs[x] = acc;\n    else if (op === "Add") acc = read(x) + acc;\n    else if (op === "Mul") acc = read(x) * acc;\n    else if (op === "Return") return acc;\n  }\n  return acc;\n}',
       hint='Keep one variable for the accumulator and an object for the registers. Read <code>a0</code> from the arguments.', why='This is how Ignition works: most instructions take one operand and use the accumulator for the other.'),
    ex('loop-order', 'h', 'Predict the console', '<p>Write <code>consoleOrder(lines)</code>. Each line is <code>{ kind, text, ms }</code> where kind is <code>"sync"</code>, <code>"promise"</code> or <code>"timer"</code> and <code>ms</code> is the timer delay. Return the texts in the order a browser prints them: sync lines in order, then promise callbacks in order, then timers by delay, and timers with the same delay in the order they were created.</p>',
       'function consoleOrder(lines) {\n  return lines.map(l => l.text);\n}\n',
       [('consoleOrder([{ kind: "timer", text: "T", ms: 0 }, { kind: "sync", text: "S1" }, { kind: "promise", text: "P" }, { kind: "sync", text: "S2" }])', ['S1', 'S2', 'P', 'T']),
        ('consoleOrder([{ kind: "timer", text: "slow", ms: 100 }, { kind: "timer", text: "fast", ms: 10 }, { kind: "timer", text: "fast2", ms: 10 }])', ['fast', 'fast2', 'slow']),
        ('consoleOrder([])', [])],
       'function consoleOrder(lines) {\n  const pick = kind => lines.filter(l => l.kind === kind);\n  const timers = pick("timer").toSorted((a, b) => a.ms - b.ms);\n  return [...pick("sync"), ...pick("promise"), ...timers].map(l => l.text);\n}',
       hint='Filter by kind, then sort only the timers. <code>toSorted</code> is stable, so equal delays keep their order.', why='This is the order the event loop simulator showed: the stack, then every microtask, then tasks as their timers become due.'),
    ex('module-order', 'x', 'Which module runs first', '<p>Write <code>evalOrder(graph, entry)</code>. <code>graph</code> maps each module to the list it imports, in order. Return the order in which the module bodies run: before a module runs, each of its imports runs first (in order), and every module runs only once.</p>',
       'function evalOrder(graph, entry) {\n  return [entry];\n}\n',
       [('evalOrder({ main: ["a", "b"], a: ["c"], b: ["c"], c: [] }, "main")', ['c', 'a', 'b', 'main']),
        ('evalOrder({ app: ["logger", "db"], db: ["logger"], logger: [] }, "app")', ['logger', 'db', 'app']),
        ('evalOrder({ solo: [] }, "solo")', ['solo'])],
       'function evalOrder(graph, entry) {\n  const done = new Set();\n  const order = [];\n  const visit = name => {\n    if (done.has(name)) return;\n    done.add(name);\n    for (const dep of graph[name] ?? []) visit(dep);\n    order.push(name);\n  };\n  visit(entry);\n  return order;\n}',
       hint='Visit each import first, then push the module. Keep a Set so a module shared by two files is visited once.', why='This depth first, post order walk is how the evaluation phase of ES modules works. Real engines also handle import cycles with the same "already seen" check.'),
]

T = {
    'slug': 'js-how-it-runs', 'title': 'How a JavaScript Program Runs Inside the Engine', 'short': 'How JavaScript runs', 'emoji': '⚙️', 'module': MODULE, 'minutes': 25, 'added': '2026-10-24',
    'lead': 'Follow one program from a text file to the output: loading, the scanner and its tokens, the parser and its syntax tree, the creation phase and hoisting, Ignition bytecode, the call stack and the heap, the JIT compilers Sparkplug, Maglev and TurboFan, the event loop and how modules are linked. Type your own code into two step by step simulators.',
    'desc': 'How JavaScript executes internally: engine and runtime, loading, scanning and tokens, parsing and the AST, early errors, creation phase and hoisting, V8 Ignition bytecode, call stack and heap, garbage collection, JIT tiers Sparkplug, Maglev and TurboFan, deoptimisation, the event loop and ES module linking.',
    'summary': 'The full journey of a JavaScript program compared with Java and Python: engine and runtime, loading and the CommonJS wrapper, scanning into tokens, parsing into an AST with early errors and lazy parsing, the creation phase and the temporal dead zone, real V8 Ignition bytecode, the call stack, the heap and garbage collection, the JIT tiers with a real deoptimisation trace, the event loop with a simulator, module construction, linking and evaluation, and a frozen page caused by a long task.',
    'keywords': ['how JavaScript runs', 'JavaScript execution', 'JavaScript internals', 'engine', 'runtime', 'V8', 'scanner', 'tokens', 'parser', 'AST', 'bytecode', 'Ignition', 'Sparkplug', 'Maglev', 'TurboFan', 'JIT', 'deoptimisation', 'call stack', 'heap', 'garbage collection', 'event loop', 'hoisting', 'execution context', 'module linking', 'interview'],
    'qa_intro': 'Testers who know these steps can tell a syntax error that stops a whole spec file from a runtime error in one test, explain odd log orders, and describe a frozen page with evidence instead of "it feels slow".',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
