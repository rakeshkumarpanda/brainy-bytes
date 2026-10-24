# Chapter 7: Map, Set and the new Set methods, weak collections, iterators and iterator helpers, generators, symbols.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('📦', 'Working with data', 'js-data', 'Objects, arrays, text, numbers, dates, JSON and collections: the data every app and every test handles.')

CODES = {
    'map': run('''
const tokens = new Map();
tokens.set("admin", "tok-a1");
tokens.set("customer", "tok-c9");
console.log(tokens.get("admin"), tokens.has("guest"), tokens.size);

const visits = new Map();
const page = { url: "/cart" };          // an object as a key, which plain objects cannot do
visits.set(page, 3);
console.log(visits.get(page));

for (const [role, token] of tokens) console.log(role, "->", token);   // insertion order
console.log([...tokens.keys()], Object.fromEntries(tokens));

tokens.delete("customer");
console.log(tokens);
''', 'Map: a dictionary with any kind of key'),
    'map-vs-object': run('''
const asObject = {};
asObject["1"] = "string key";
asObject[1] = "number key";               // object keys are always strings, so this overwrites
console.log(Object.keys(asObject).length);

const asMap = new Map([["1", "string key"], [1, "number key"]]);
console.log(asMap.size);

const counts = new Map();
for (const word of "to be or not to be".split(" ")) {
  counts.set(word, (counts.get(word) ?? 0) + 1);
}
console.log(counts);
console.log(counts.getOrInsert("maybe", 0), counts.size);   // ES2026: read or insert in one step
''', 'When a Map beats a plain object'),
    'set': run('''
const seen = new Set(["chromium", "firefox"]);
seen.add("webkit").add("chromium");      // duplicates are ignored
console.log(seen.size, seen.has("firefox"));

const expected = new Set(["Home", "Shop", "Deals", "Help", "Account"]);
const actual = new Set(["Home", "Shop", "Help", "Account", "Blog"]);

console.log("missing:", [...expected.difference(actual)]);      // ES2025 Set methods
console.log("extra:", [...actual.difference(expected)]);
console.log("both:", [...expected.intersection(actual)]);
console.log("all:", [...expected.union(actual)].length);
console.log("changed:", [...expected.symmetricDifference(actual)]);
console.log(new Set(["Home", "Shop"]).isSubsetOf(actual), expected.isDisjointFrom(new Set(["Login"])));
''', 'Set and the ES2025 set operations'),
    'weak': run('''
const meta = new WeakMap();      // keys must be objects and do not keep them alive
function track(element) {
  meta.set(element, { clicks: (meta.get(element)?.clicks ?? 0) + 1 });
}
const button = { id: "buy" };
track(button); track(button);
console.log(meta.get(button));
console.log(meta.has({ id: "buy" }));   // a different object

const cache = new WeakRef({ big: "report data" });
console.log(cache.deref()?.big);        // may be undefined once memory is reclaimed
''', 'WeakMap and WeakRef'),
    'iterables': run('''
const word = "QA";
const it = word[Symbol.iterator]();      // every iterable hands out an iterator
console.log(it.next(), it.next(), it.next());

// spread, for...of, destructuring and Array.from all use the same protocol
console.log([..."hey"], Array.from(new Set([3, 3, 4])));
const [first, ...rest] = new Map([["a", 1], ["b", 2]]);
console.log(first, rest);

const countdown = {
  from: 3,
  [Symbol.iterator]() {
    let n = this.from;
    return { next: () => (n > 0 ? { value: n--, done: false } : { value: undefined, done: true }) };
  },
};
console.log([...countdown]);
for (const n of countdown) console.log("T minus", n);
''', 'The iteration protocol'),
    'helpers': run('''
// ES2025 iterator helpers: map, filter, take, drop, flatMap, reduce, some, every, find, toArray.
// They work lazily, one value at a time, on any iterator.
function* naturals() {
  let n = 1;
  while (true) yield n++;                 // an endless sequence is fine when consumed lazily
}

const firstEvenSquares = naturals()
  .map(n => n * n)
  .filter(n => n % 2 === 0)
  .take(4)
  .toArray();
console.log(firstEvenSquares);

const map = new Map([["a", 1], ["b", 2], ["c", 3]]);
console.log(map.values().filter(v => v > 1).toArray());
console.log(Iterator.from({ next: () => ({ value: 7, done: false }) }).take(3).toArray());
''', 'Iterator helpers'),
    'generator': run('''
function* idMaker(prefix) {
  let n = 1;
  while (true) {
    const reset = yield `${prefix}-${String(n).padStart(4, "0")}`;
    n = reset ? 1 : n + 1;
  }
}

const ids = idMaker("TC");
console.log(ids.next().value);
console.log(ids.next().value);
console.log(ids.next(true).value);      // a value passed to next() comes out of yield
console.log(ids.next().value);

function* steps() {
  console.log("  (running until the first yield)");
  yield "open";
  console.log("  (resumed)");
  yield "click";
  return "done";
}
const g = steps();
console.log("created, nothing ran yet");
console.log(g.next());
console.log(g.next());
console.log(g.next());
console.log(g.next());
''', 'Generators pause and resume'),
    'async-gen': run('''
// A fake paginated API: 7 users, 3 per page
const ALL = ["asha", "ravi", "mei", "omar", "lena", "ken", "zoe"];
async function fetchPage(page) {
  await new Promise(r => setTimeout(r, 10));     // pretend network time
  const start = (page - 1) * 3;
  return { users: ALL.slice(start, start + 3), next: start + 3 < ALL.length ? page + 1 : null };
}

async function* allUsers() {
  let page = 1;
  while (page) {
    const body = await fetchPage(page);
    console.log(`  fetched page ${page}`);
    yield* body.users;                            // hand out each user of the page
    page = body.next;
  }
}

for await (const user of allUsers()) {
  console.log(user);
  if (user === "omar") break;                     // stop early: later pages are never fetched
}

console.log(await Array.fromAsync(allUsers()));
''', 'Async generators for paginated APIs'),
    'symbols': run('''
const id = Symbol("id");
const user = { name: "Asha", [id]: 42 };
console.log(user[id], Object.keys(user), JSON.stringify(user));   // symbol keys are hidden from most tools
console.log(Symbol("x") === Symbol("x"), Symbol.for("x") === Symbol.for("x"));

const money = {
  amount: 2695,
  [Symbol.toPrimitive](hint) {
    return hint === "number" ? this.amount : `₹${this.amount.toLocaleString("en-IN")}`;
  },
};
console.log(`${money}`, +money, money * 2);
''', 'Symbols and well known symbols'),
    'scenario': run('''
// Compare the menu a page shows with the menu the spec asks for, then read every page of the user list.
const specMenu = ["Home", "Shop", "Deals", "Help", "Account"];
const shownMenu = ["Home", "Shop", "Help", "Help", "Account", "Blog"];

const expected = new Set(specMenu);
const actual = new Set(shownMenu);
const report = {
  missing: [...expected.difference(actual)],
  unexpected: [...actual.difference(expected)],
  duplicated: shownMenu.filter((item, i) => shownMenu.indexOf(item) !== i),
  sameOrder: specMenu.filter(x => actual.has(x)).join() === [...actual].filter(x => expected.has(x)).join(),
};
console.log(report);

async function* pages(total, size) {
  for (let start = 0; start < total; start += size) {
    yield Array.from({ length: Math.min(size, total - start) }, (_, i) => `user${start + i + 1}`);
  }
}
let count = 0;
for await (const page of pages(23, 10)) {
  count += page.length;
  console.log(`page of ${page.length}, first ${page[0]}`);
}
console.log("total users:", count);
''', 'Compare menus and walk every page'),
}

PARTS = [
    part('map', '🗺️', 'Map', '''
<p>A <b>Map</b> stores key and value pairs, like an object, with three differences that matter: keys can be any value (objects, numbers, functions), it remembers insertion order, and it has a <code>size</code>.</p>
[[map]]
[[map-vs-object]]
<div class="tip">Use a plain object for fixed shapes such as a user or a config. Use a Map for lookups that grow at run time: caches, counters, "element to data" tables. <code>getOrInsert</code> and <code>getOrInsertComputed</code> (ES2026) replace the "get, check, set" dance.</div>
<div class="qa-box">A Map is a clean way to cache one login token per role during a test run, so each role logs in once: <code>tokens.getOrInsertComputed(role, () =&gt; login(role))</code> for a synchronous helper, or the get, check and set steps around an <code>await</code>.</div>
''', qa=True, kw=['Map', 'set', 'get', 'has', 'delete', 'size', 'insertion order', 'object keys', 'counter', 'getOrInsert', 'cache']),
    part('set', '🧺', 'Set and set operations', '''
<p>A <b>Set</b> holds unique values. Adding a value twice keeps one copy. ES2025 added the operations from school maths, so comparing two lists no longer needs nested loops.</p>
[[set]]
<div class="tw"><table class="jt"><tr><th>Method</th><th>Returns</th></tr>
<tr><td><code>a.union(b)</code></td><td>everything in either</td></tr>
<tr><td><code>a.intersection(b)</code></td><td>only what is in both</td></tr>
<tr><td><code>a.difference(b)</code></td><td>in a but not in b</td></tr>
<tr><td><code>a.symmetricDifference(b)</code></td><td>in exactly one of them</td></tr>
<tr><td><code>a.isSubsetOf(b)</code>, <code>isSupersetOf</code>, <code>isDisjointFrom</code></td><td>true or false</td></tr>
</table></div>
<div class="qa-box">Checking a dropdown, a menu or a list of columns against the spec is a set comparison. Report <code>expected.difference(actual)</code> as missing and <code>actual.difference(expected)</code> as unexpected, and the failure message says exactly what is wrong.</div>
''', qa=['Playwright', 'Cypress', 'Selenium'], kw=['Set', 'unique', 'add', 'has', 'union', 'intersection', 'difference', 'symmetricDifference', 'isSubsetOf', 'compare lists', 'missing items']),
    part('weak', '🪶', 'WeakMap, WeakSet and WeakRef', '''
<p>Weak collections hold objects without keeping them alive. When nothing else uses the object, the garbage collector may remove it and its entry disappears. They cannot be listed or counted, because their contents can change at any moment.</p>
[[weak]]
<p>Libraries use a WeakMap to attach extra data to DOM elements or objects they do not own without causing memory leaks. App code rarely needs WeakRef or FinalizationRegistry, and their timing must never be relied on.</p>
''', kw=['WeakMap', 'WeakSet', 'WeakRef', 'FinalizationRegistry', 'garbage collection', 'memory leak']),
    part('iterators', '🔁', 'Iterators and iterator helpers', '''
<p>An <b>iterable</b> is anything with a <code>Symbol.iterator</code> method: arrays, strings, Maps, Sets, NodeLists and arguments. That method returns an <b>iterator</b>, an object whose <code>next()</code> hands out <code>{ value, done }</code> one at a time. <code>for...of</code>, spread and destructuring all use it.</p>
[[iterables]]
<h3>Iterator helpers (ES2025)</h3>
<p>Iterators now have <code>map</code>, <code>filter</code>, <code>take</code>, <code>drop</code> and friends. Unlike the array methods, they are <b>lazy</b>: no work happens until a value is asked for, so they work on huge or endless sequences.</p>
[[helpers]]
''', kw=['iterable', 'iterator', 'Symbol.iterator', 'next', 'done', 'iteration protocol', 'iterator helpers', 'take', 'drop', 'toArray', 'Iterator.from', 'lazy evaluation']),
    part('generators', '⏯️', 'Generators and async generators', '''
<p>A <b>generator</b> function (<code>function*</code>) can pause at every <code>yield</code> and continue later from the same place. Calling it runs nothing. It returns an iterator, and each <code>next()</code> runs the body up to the next <code>yield</code>.</p>
<div class="viz" data-viz="lanes" data-k="gen"></div>
[[generator]]
<h3>Async generators and for await</h3>
<p>An <code>async function*</code> can <code>await</code> between yields. Consumed with <code>for await</code>, it turns a paginated API into a simple loop, and it only fetches pages that are actually needed.</p>
[[async-gen]]
<div class="qa-box">Paginated endpoints are a classic API test target: page sizes, the last page, an empty page, a stable order across pages. An async generator gives you every item in one loop, and <code>Array.fromAsync</code> collects them for one big assertion.</div>
''', qa=['Jest', 'Playwright'], qa_why='API tests often have to walk paginated endpoints, and async generators make that a plain loop.',
        kw=['generator', 'function*', 'yield', 'yield*', 'next', 'lazy', 'async generator', 'for await', 'pagination', 'Array.fromAsync']),
    part('symbols', '🔣', 'Symbols', '''
<p>A <b>symbol</b> is a unique value used as a hidden key. Two symbols with the same description are still different, unless they come from the shared registry with <code>Symbol.for</code>. Symbol keys are skipped by <code>Object.keys</code> and <code>JSON.stringify</code>.</p>
[[symbols]]
<p><b>Well known symbols</b> let your objects plug into the language: <code>Symbol.iterator</code> makes them work with <code>for...of</code>, <code>Symbol.toPrimitive</code> controls how they turn into text and numbers, <code>Symbol.asyncIterator</code> works with <code>for await</code>, and <code>Symbol.dispose</code> works with <code>using</code> ({{ch:js-modern}}).</p>
''', kw=['Symbol', 'Symbol.for', 'unique key', 'well known symbols', 'Symbol.iterator', 'Symbol.toPrimitive', 'Symbol.asyncIterator']),
    part('scenario', '🎬', 'Real world scenario: compare a menu and walk every page', '''
<div class="scenario"><b>The situation</b>A release changed the site menu. You must report which items the spec asks for but the page lacks, which the page has that the spec does not mention, any duplicates, and whether the shared items keep their order. Then you must count every user across a paginated list.</div>
[[scenario]]
<p>Set operations produce the missing and unexpected lists in one line each, and duplicates are easy to spot once you compare each item's first position with its own. The async generator hides the paging, so the count is a plain loop.</p>
''', qa=True, kw=['compare menu', 'expected vs actual', 'set difference', 'duplicates', 'pagination', 'async generator', 'for await']),
]

LANES = {
    'gen': {'t': 'A generator pauses at every yield', 'code': 'function* steps() {\n  yield "open";\n  yield "click";\n  return "done";\n}\nconst g = steps();\ng.next();\ng.next();\ng.next();',
            'lanes': ['Caller', 'Generator', 'next() returned'], 'tone': [2, 3, 1],
            'steps': [{'l': 6, 'v': [['g = steps()'], ['paused before line 2'], []], 'm': 'Calling steps() runs nothing. It only creates the paused generator g.'},
                      {'l': [7, 2], 'v': [['g.next()'], ['runs to yield "open"', 'paused'], ['{ value: "open", done: false }']], 'm': 'The first next() runs the body until the first yield and hands out its value.'},
                      {'l': [8, 3], 'v': [['g.next()'], ['resumes after yield', 'runs to yield "click"', 'paused'], ['{ value: "open", done: false }', '{ value: "click", done: false }']], 'm': 'The next call resumes exactly where it stopped.'},
                      {'l': [9, 4], 'v': [['g.next()'], ['runs to return', 'finished'], ['{ value: "open", done: false }', '{ value: "click", done: false }', '{ value: "done", done: true }']], 'm': 'return ends the generator. done becomes true. for...of ignores this final value.'}]},
}

INFO = {'title': 'Collections that do one job well', 'panels': [
    panel([['e', '🗺️'], ['t', 'map.set(page, 3)', {'b': 1}]], 'Map', 'Any value can be a key.', 'Great for caches and counters that grow while the program runs.'),
    panel([['e', '🧺'], ['t', 'expected.difference(actual)', {'b': 1, 'size': 11}]], 'Set', 'Unique values with real set operations.', 'Missing and unexpected items fall out in one line each.'),
    panel([['e', '🔁'], ['t', '{ value, done }', {'b': 1}]], 'Iterators', 'One value at a time, on demand.', 'for...of, spread and destructuring all use this protocol.'),
    panel([['e', '⏯️'], ['t', 'yield, pause, resume', {'b': 1}]], 'Generators', 'Functions that pause.', 'Async generators turn paginated APIs into simple loops.')],
    'remember': 'Set for unique, Map for lookups, generators for sequences you consume one by one.'}

REAL = [
    ['🧭', 'A navigation audit', 'A nightly job compares every menu on the site with the spec using Set.difference and posts the gaps to the team chat.'],
    ['🎟️', 'Ticket numbers', 'A generator hands out TC-0001, TC-0002 and so on to each new test case in a test management script.'],
    ['📜', 'Export every customer', 'An admin export reads a paginated customers API with an async generator and writes rows as they arrive.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers Map, Set and its new operations, weak collections, iterators, generators and symbols.',
        'यह अध्याय Map, Set और उसके नए operations, weak collections, iterators, generators और symbols सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ Map, Set ಮತ್ತು ಹೊಸ operations, weak collections, iterators, generators ಮತ್ತು symbols ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ Map, Set ଓ ଏହାର ନୂଆ operations, weak collections, iterators, generators ଓ symbols ଶିଖାଏ।',
        'يتناول هذا الفصل Map وSet وعملياتها الجديدة والمجموعات الضعيفة والمكررات والمولدات والرموز.',
        'Dieses Kapitel behandelt Map, Set und seine neuen Operationen, schwache Sammlungen, Iteratoren, Generatoren und Symbole.'),
    say('map', 'Map', 'A Map stores pairs with any kind of key, keeps insertion order and has a size. Use it for caches and counters.',
        'Map किसी भी तरह की key के साथ pairs रखता है, insertion order याद रखता है और उसका size होता है। Caches और counters के लिए इस्तेमाल करें।',
        'Map ಯಾವುದೇ key ಜೊತೆ pairs ಇಡುತ್ತದೆ, insertion order ನೆನಪಿಡುತ್ತದೆ, size ಇದೆ. Caches ಮತ್ತು counters ಗೆ ಬಳಸಿ.',
        'Map ଯେକୌଣସି key ସହ pairs ରଖେ, insertion order ମନେ ରଖେ ଏବଂ size ଅଛି। Caches ଓ counters ପାଇଁ ବ୍ୟବହାର କରନ୍ତୁ।',
        'يخزن Map أزواجًا بمفاتيح من أي نوع ويحفظ ترتيب الإدخال وله حجم. استخدمه للتخزين المؤقت والعدادات.',
        'Eine Map speichert Paare mit beliebigen Schlüsseln, behält die Reihenfolge und hat eine Größe. Ideal für Caches und Zähler.'),
    say('set', 'Set', 'A Set holds unique values. Union, intersection and difference compare two lists in one line, which makes expected against actual checks easy.',
        'Set unique values रखता है। Union, intersection और difference दो lists को एक line में compare करते हैं।',
        'Set unique values ಇಡುತ್ತದೆ. Union, intersection ಮತ್ತು difference ಎರಡು lists ಅನ್ನು ಒಂದು ಸಾಲಿನಲ್ಲಿ ಹೋಲಿಸುತ್ತವೆ.',
        'Set unique values ରଖେ। Union, intersection ଓ difference ଦୁଇଟି lists କୁ ଗୋଟିଏ ଧାଡ଼ିରେ ତୁଳନା କରନ୍ତି।',
        'تحتفظ Set بقيم فريدة. الاتحاد والتقاطع والفرق تقارن قائمتين في سطر واحد، مما يسهل فحص المتوقع مقابل الفعلي.',
        'Ein Set enthält eindeutige Werte. Vereinigung, Schnitt und Differenz vergleichen zwei Listen in einer Zeile.'),
    say('weak', 'Weak collections', 'Weak collections hold objects without keeping them alive, so entries can vanish. They help libraries avoid memory leaks.',
        'Weak collections objects को ज़िंदा रखे बिना रखते हैं, इसलिए entries गायब हो सकती हैं। ये libraries को memory leaks से बचाते हैं।',
        'Weak collections objects ಅನ್ನು ಜೀವಂತವಾಗಿಡದೆ ಇಡುತ್ತವೆ, entries ಕಾಣೆಯಾಗಬಹುದು. Libraries memory leaks ತಪ್ಪಿಸಲು ಬಳಸುತ್ತವೆ.',
        'Weak collections objects କୁ ଜୀବିତ ନରଖି ରଖନ୍ତି, ତେଣୁ entries ହଜିପାରେ। Libraries memory leaks ଏଡ଼ାଇବାକୁ ବ୍ୟବହାର କରନ୍ତି।',
        'تحتفظ المجموعات الضعيفة بالكائنات دون إبقائها حية، لذا قد تختفي المدخلات. تساعد المكتبات على تجنب تسرب الذاكرة.',
        'Schwache Sammlungen halten Objekte, ohne sie am Leben zu halten, Einträge können verschwinden. Bibliotheken vermeiden so Speicherlecks.'),
    say('iterators', 'Iterators', 'Iterables hand out values one at a time through next. Iterator helpers such as map, filter and take work lazily on any iterator.',
        'Iterables next से एक एक value देते हैं। map, filter और take जैसे iterator helpers किसी भी iterator पर lazily काम करते हैं।',
        'Iterables next ಮೂಲಕ ಒಂದೊಂದೇ value ಕೊಡುತ್ತವೆ. map, filter, take ನಂತಹ iterator helpers lazily ಕೆಲಸ ಮಾಡುತ್ತವೆ.',
        'Iterables next ମାଧ୍ୟମରେ ଗୋଟିଏ ଗୋଟିଏ value ଦିଅନ୍ତି। map, filter, take ପରି iterator helpers lazily କାମ କରନ୍ତି।',
        'تعطي القابلات للتكرار القيم واحدة تلو الأخرى عبر next. وتعمل مساعدات المكررات مثل map وfilter وtake بشكل كسول.',
        'Iterierbare liefern Werte einzeln über next. Iterator-Helfer wie map, filter und take arbeiten verzögert auf jedem Iterator.'),
    say('generators', 'Generators', 'A generator pauses at each yield and resumes on the next call. Async generators with for await turn paginated APIs into simple loops.',
        'Generator हर yield पर रुकता है और अगली call पर फिर चलता है। for await के साथ async generators paginated APIs को आसान loops बनाते हैं।',
        'Generator ಪ್ರತಿ yield ನಲ್ಲಿ ನಿಲ್ಲುತ್ತದೆ, ಮುಂದಿನ call ನಲ್ಲಿ ಮುಂದುವರಿಯುತ್ತದೆ. Async generators paginated APIs ಅನ್ನು ಸರಳ loops ಮಾಡುತ್ತವೆ.',
        'Generator ପ୍ରତ୍ୟେକ yield ରେ ଅଟକେ ଏବଂ ପରବର୍ତ୍ତୀ call ରେ ଚାଲେ। Async generators paginated APIs କୁ ସରଳ loops କରନ୍ତି।',
        'يتوقف المولد عند كل yield ويستأنف في الاستدعاء التالي. المولدات غير المتزامنة مع for await تحول واجهات الصفحات إلى حلقات بسيطة.',
        'Ein Generator pausiert bei jedem yield und macht beim nächsten Aufruf weiter. Asynchrone Generatoren machen seitenweise APIs zu einfachen Schleifen.'),
    say('symbols', 'Symbols', 'Symbols are unique hidden keys. Well known symbols such as Symbol iterator let your objects work with the language.',
        'Symbols unique छिपी keys हैं। Symbol.iterator जैसे well known symbols आपके objects को language के साथ जोड़ते हैं।',
        'Symbols unique ಅಡಗಿದ keys. Symbol.iterator ನಂತಹ well known symbols ನಿಮ್ಮ objects ಅನ್ನು language ಜೊತೆ ಕೆಲಸ ಮಾಡಿಸುತ್ತವೆ.',
        'Symbols unique ଲୁଚିଥିବା keys। Symbol.iterator ପରି well known symbols ଆପଣଙ୍କ objects କୁ language ସହ କାମ କରାନ୍ତି।',
        'الرموز مفاتيح مخفية فريدة. الرموز المعروفة مثل Symbol.iterator تجعل كائناتك تعمل مع اللغة.',
        'Symbole sind eindeutige versteckte Schlüssel. Bekannte Symbole wie Symbol.iterator binden deine Objekte an die Sprache an.'),
    say('scenario', 'Scenario', 'Set operations report missing, unexpected and duplicated menu items, and an async generator counts users across pages.',
        'Set operations missing, unexpected और duplicate menu items बताते हैं, और async generator pages में users गिनता है।',
        'Set operations missing, unexpected ಮತ್ತು duplicate menu items ವರದಿ ಮಾಡುತ್ತವೆ, async generator pages ನಲ್ಲಿ users ಎಣಿಸುತ್ತದೆ.',
        'Set operations missing, unexpected ଓ duplicate menu items ଜଣାନ୍ତି, ଏବଂ async generator pages ରେ users ଗଣେ।',
        'تبلغ عمليات Set عن عناصر القائمة المفقودة وغير المتوقعة والمكررة، ويعد المولد غير المتزامن المستخدمين عبر الصفحات.',
        'Set-Operationen melden fehlende, unerwartete und doppelte Menüpunkte, ein asynchroner Generator zählt Nutzer über Seiten.'),
    say('practice', 'Hands-on', 'Practise unique lists, list differences, a range generator and a small LRU cache.',
        'Unique lists, list differences, range generator और एक छोटा LRU cache का अभ्यास करें।',
        'Unique lists, list differences, range generator ಮತ್ತು ಚಿಕ್ಕ LRU cache ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Unique lists, list differences, range generator ଓ ଛୋଟ LRU cache ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على القوائم الفريدة والفروق بين القوائم ومولد نطاق وذاكرة LRU صغيرة.',
        'Übe eindeutige Listen, Listendifferenzen, einen Bereichsgenerator und einen kleinen LRU-Cache.'),
]

QUIZ = [
    quiz('e', 'What is new Set([1, 1, 2, 2, 3]).size?', ['3', '5', '2', '1'], 0, 'Duplicates are kept once.', 'A Set keeps 1, 2 and 3.'),
    quiz('e', 'Which can be a key in a Map but not (as itself) in a plain object?', ['An object', 'A string', 'A symbol', 'A text key with spaces'], 0, 'Object keys become strings.', 'Plain objects turn keys into strings (or symbols). A Map keeps any value, including objects.'),
    quiz('e', 'What does calling a generator function do?', ['Returns a paused iterator without running the body', 'Runs the whole body', 'Runs until the first yield', 'Throws unless you use await'], 0, 'Nothing runs until next().', 'The body only starts on the first <code>next()</code>.'),
    quiz('m', 'expected = {A, B, C}, actual = {B, C, D}. What is expected.difference(actual)?', ['{A}', '{D}', '{A, D}', '{B, C}'], 0, 'In expected but not in actual.', 'Only A is in expected and missing from actual.'),
    quiz('m', 'Which loop reads values from an async generator?', ['for await (const x of gen())', 'for (const x of gen())', 'gen().forEach(...)', 'for (const x in gen())'], 0, 'Each value is a promise to wait for.', '<code>for await</code> waits for each value an async iterator hands out.'),
    quiz('m', 'Why does JSON.stringify skip a property whose key is a symbol?', ['Symbol keys are hidden from JSON and Object.keys', 'Symbols cannot be values', 'JSON only supports numbers', 'It is a bug'], 0, 'Symbols are meant to be hidden keys.', 'Symbol keyed properties are ignored by JSON and by <code>Object.keys</code>.'),
    quiz('h', 'What makes iterator helpers different from array methods?', ['They are lazy and work one value at a time', 'They are faster on small arrays', 'They change the original', 'They only work on Maps'], 0, 'Think of an endless sequence.', 'Nothing is computed until a value is asked for, so <code>take(4)</code> on an endless generator stops after four.'),
    quiz('h', 'A loop over an async generator of pages breaks after the 4th user, with 3 users per page. How many pages are fetched?', ['2', '3', '1', 'All of them'], 0, 'The 4th user is on page 2.', 'Users 1 to 3 come from page 1, the 4th from page 2. The loop stops before page 3 is requested.'),
    quiz('h', 'What does [...new Map([["a", 1]])] give?', ['[["a", 1]]', '["a"]', '[1]', '[{ a: 1 }]'], 0, 'A Map iterates as pairs.', 'Spreading a Map gives its entries as <code>[key, value]</code> arrays.'),
    quiz('x', 'Why can a WeakMap not be iterated or report its size?', ['Entries may disappear whenever the garbage collector runs', 'It is a bug kept for compatibility', 'Its keys are encrypted', 'It only has one entry'], 0, 'What does weak mean here?', 'Its contents depend on garbage collection timing, so listing them would give unpredictable results.'),
    quiz('x', 'What does next(true) do in the idMaker generator?', ['Makes the paused yield expression evaluate to true, which resets the counter', 'Skips one id', 'Ends the generator', 'Throws an error'], 0, 'Values can flow into a generator.', 'The argument of <code>next</code> becomes the result of the <code>yield</code> where the generator paused.'),
    quiz('x', 'Which is true of Symbol("id") === Symbol("id")?', ['false, every Symbol() call creates a new symbol', 'true, same description', 'It throws', 'true only with Symbol.for'], 0, 'Descriptions are just labels.', 'Each <code>Symbol()</code> is unique. <code>Symbol.for("id")</code> returns the same registered symbol each time.'),
]

CALC = [
    calc('e', 'What is the size of the Map after these lines?', '2', 'Setting an existing key replaces its value.', ['"a" and "b" are set, then "a" is set again. Two keys.'], code='const m = new Map();\nm.set("a", 1);\nm.set("b", 2);\nm.set("a", 3);'),
    calc('e', 'How many unique letters are in "mississippi"?', '4', 'Use a Set in your head.', ['m, i, s, p.']),
    calc('m', 'A = {1,2,3,4}, B = {3,4,5}. What is the size of A.union(B)?', '5', 'Count each value once.', ['{1, 2, 3, 4, 5} has 5 values.']),
    calc('m', 'What is the size of A.symmetricDifference(B) for the same sets?', '3', 'In exactly one of them.', ['Only in A: 1, 2. Only in B: 5.', 'That is 3 values.']),
    calc('h', 'An API has 23 users and returns 10 per page. How many requests does reading every page take?', '3', 'Round up.', ['<span class="eq">23 ÷ 10 = 2.3</span>', 'Pages hold 10, 10 and 3 users, so 3 requests.']),
    calc('h', 'How many times does next() return done: false for a generator with three yields and a return?', '3', 'The return gives done: true.', ['Each yield gives one done: false result.', 'The return gives done: true.']),
    calc('x', 'What does naturals().map(n => n * n).filter(n => n % 2 === 0).take(4).toArray() return? Answer with the last number.', '64', 'Even squares come from even numbers.', ['Even squares: 4, 16, 36, 64.', 'The fourth one is 64.']),
    calc('x', 'An LRU cache with limit 2 receives set a, set b, get a, set c. Which key is evicted?', 'b', 'Least recently used.', ['After get a, a is the most recently used.', 'b has gone the longest without use, so it is removed when c is added.']),
]

EX = [
    ex('unique', 'e', 'Unique, in order', '<p>Write <code>unique(list)</code> that removes duplicates and keeps the order of first appearance.</p>',
       'function unique(list) {\n  \n}\n', [('unique([3, 1, 3, 2, 1])', [3, 1, 2]), ('unique(["a", "a"])', ['a']), ('unique([])', [])],
       'function unique(list) {\n  return [...new Set(list)];\n}', hint='A Set keeps insertion order.', why='Spreading a Set back into an array keeps the first time each value was added.'),
    ex('diff', 'm', 'Expected against actual', '<p>Write <code>compareLists(expected, actual)</code> that returns <code>{ missing, extra }</code>: items in expected but not actual, and items in actual but not expected. Both lists sorted alphabetically.</p>',
       'function compareLists(expected, actual) {\n  \n}\n',
       [('compareLists(["Home", "Shop", "Deals"], ["Shop", "Blog", "Home"])', {'missing': ['Deals'], 'extra': ['Blog']}),
        ('compareLists(["a"], ["a"])', {'missing': [], 'extra': []}), ('compareLists([], ["z", "b"])', {'missing': [], 'extra': ['b', 'z']})],
       'function compareLists(expected, actual) {\n  const e = new Set(expected), a = new Set(actual);\n  return {\n    missing: [...e.difference(a)].sort(),\n    extra: [...a.difference(e)].sort(),\n  };\n}',
       hint='Turn both into Sets and use <code>difference</code> twice. If your browser lacks it, use <code>filter</code> with <code>has</code>.', why='Sorting makes the result stable, so the test does not depend on the order items happened to appear in.'),
    ex('range', 'h', 'A range generator', '<p>Write a generator <code>range(start, end, step = 1)</code> that yields <code>start</code>, <code>start + step</code> and so on while the value is less than <code>end</code>.</p>',
       'function* range(start, end, step = 1) {\n  \n}\n',
       [('[...range(0, 5)]', [0, 1, 2, 3, 4]), ('[...range(0, 10, 3)]', [0, 3, 6, 9]), ('[...range(5, 5)]', []), ('(() => { const it = range(1, 100); it.next(); return it.next().value; })()', 2)],
       'function* range(start, end, step = 1) {\n  for (let n = start; n < end; n += step) {\n    yield n;\n  }\n}', hint='A normal counting loop with <code>yield</code> inside.', why='The loop only advances when someone asks for the next value, so even a huge range costs nothing until it is used.'),
    ex('lru', 'x', 'A small LRU cache', '<p>Write <code>lruCache(limit)</code> returning <code>{ get(key), set(key, value), keys() }</code>. <code>get</code> returns the value or <code>undefined</code> and marks the key as recently used. When <code>set</code> would go over the limit, remove the least recently used key. <code>keys()</code> returns the keys from least to most recently used.</p>',
       'function lruCache(limit) {\n  const map = new Map();\n  return {\n    get(key) {},\n    set(key, value) {},\n    keys() { return [...map.keys()]; },\n  };\n}\n',
       [('(() => { const c = lruCache(2); c.set("a", 1); c.set("b", 2); c.get("a"); c.set("c", 3); return c.keys(); })()', ['a', 'c']),
        ('(() => { const c = lruCache(2); c.set("a", 1); c.set("a", 5); c.set("b", 2); return [c.get("a"), c.keys()]; })()', [5, ['b', 'a']]),
        ('(() => { const c = lruCache(1); c.set("x", 1); return c.get("y") === undefined; })()', True)],
       'function lruCache(limit) {\n  const map = new Map();\n  return {\n    get(key) {\n      if (!map.has(key)) return undefined;\n      const value = map.get(key);\n      map.delete(key);\n      map.set(key, value);\n      return value;\n    },\n    set(key, value) {\n      map.delete(key);\n      map.set(key, value);\n      if (map.size > limit) map.delete(map.keys().next().value);\n    },\n    keys() { return [...map.keys()]; },\n  };\n}',
       hint='A Map keeps insertion order. Deleting and setting a key again moves it to the end, so the first key is always the least recently used.',
       why='Re-inserting on every use keeps the Map ordered from oldest to newest, and <code>map.keys().next().value</code> is the oldest key.'),
]

T = {
    'slug': 'js-collections-iterators', 'title': 'Map, Set, Iterators and Generators', 'short': 'Collections and generators', 'emoji': '🗂️', 'module': MODULE, 'minutes': 16,
    'lead': 'Map for lookups with any key, Set with the new union and difference methods, weak collections, the iteration protocol and lazy iterator helpers, generators, async generators for paginated APIs, and symbols.',
    'desc': 'Map, Set, set operations, WeakMap, WeakRef, iterators, iterator helpers, generators, async generators, for await and symbols.',
    'summary': 'Map and when it beats an object, getOrInsert, Set with union, intersection and difference, WeakMap and WeakRef, the iteration protocol, lazy iterator helpers, generators that pause and resume, async generators and for await for paginated APIs, symbols and well known symbols, and comparing an expected menu with the real one.',
    'keywords': ['Map', 'Set', 'union', 'intersection', 'difference', 'WeakMap', 'WeakRef', 'iterator', 'iterable', 'iterator helpers', 'generator', 'yield', 'async generator', 'for await', 'pagination', 'Symbol'],
    'qa_intro': 'Set operations make expected against actual list checks a one liner, and async generators make paginated API tests a plain loop.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
