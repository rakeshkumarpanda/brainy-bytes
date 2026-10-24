/* ===== Interactive animations for the newer Java chapters, added to the shared VIZ widgets =====
   Every widget takes the reader's own input and replays what Java does with it, step by step.
   <div class="viz" data-viz="jstream"></div>     a stream pipeline, one element at a time, showing laziness and short circuits
   <div class="viz" data-viz="jlambda"></div>     the built in functional interfaces, with a lambda you can call
   <div class="viz" data-viz="jswitch"></div>     a pattern matching switch choosing its case, guards included
   <div class="viz" data-viz="jvthreads"></div>   platform threads against virtual threads for blocking work
   <div class="viz" data-viz="jclassload"></div>  class loader delegation and the loading, linking, initialising phases
   <div class="viz" data-viz="jcf"></div>         CompletableFuture: calls one after another against calls in parallel
   <div class="viz" data-viz="jsql"></div>        a JDBC query built by gluing strings against a PreparedStatement
   <div class="viz" data-viz="jrelease"></div>    what you gain when you move from one Java version to another
   JAVAPAGE.start(opts) wires the whole page: comic, quiz, narrator, diagrams and the line by line viewer. */
(() => {
  const K = VIZ.kit, W = VIZ.widgets, esc = K.esc, $ = K.$;
  const row = (label, inner) => `<div class="vz-row"><span class="jv-lbl">${label}</span>${inner}</div>`;
  const nums = s => String(s).split(/[\s,]+/).filter(Boolean).map(Number).filter(n => Number.isFinite(n)).slice(0, 12);

  /* ---------- jstream: filter, map and limit, element by element ---------- */
  W.jstream = el => {
    const b = K.shell(el, 'Watch a stream pull one element at a time', 'Type your own numbers, change the pipeline, then press Play. Elements travel down one by one, and limit stops the source early.');
    b.innerHTML = `${row('Numbers', '<input class="jv-in" data-in="src" value="7, 2, 9, 4, 12, 5, 8, 3" style="width:260px">')}
      ${row('filter', 'keep x &gt; <input class="jv-in" data-in="min" value="4" style="width:60px">')}
      ${row('map', 'x × <input class="jv-in" data-in="mul" value="10" style="width:60px">')}
      ${row('limit', '<input class="jv-in" data-in="lim" value="3" style="width:60px">')}
      <pre class="jv-code" data-code style="margin:8px 0"></pre>
      <div class="jv-lanes" data-lanes></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const lanesEl = $('[data-lanes]', b), msg = $('.vz-msg', b);
    const names = ['Source', 'filter', 'map', 'limit', 'Result list'];
    lanesEl.innerHTML = names.map((n, i) => `<div class="jv-lane"><b>${n}</b><div data-lane="${i}"></div></div>`).join('');
    let steps = [];
    const P = K.Player($('.vz-p', b), f => show(f), 900);
    function build() {
      const src = nums($('[data-in="src"]', b).value), min = +$('[data-in="min"]', b).value || 0;
      const mul = +$('[data-in="mul"]', b).value || 1, lim = Math.max(0, Math.floor(+$('[data-in="lim"]', b).value || 0));
      $('[data-code]', b).innerHTML = esc(`List.of(${src.join(', ')}).stream()\n    .filter(x -> x > ${min})\n    .map(x -> x * ${mul})\n    .limit(${lim})\n    .toList();`);
      steps = [];
      const out = [];
      let pulled = 0;
      const lane = () => [src.slice(pulled).map(String), [], [], [], out.map(String)];
      if (lim === 0) { steps.push({ v: lane(), m: 'limit(0) needs nothing, so the source is never even read. That is laziness.' }); return; }
      for (const x of src) {
        pulled++;
        let v = lane(); v[1] = [String(x)];
        steps.push({ v, m: `The terminal operation asks for one more element. The source hands over <mark>${x}</mark> to filter.` });
        if (!(x > min)) { v = lane(); steps.push({ v, m: `${x} &gt; ${min} is false, so filter drops ${x} and asks the source for the next one.` }); continue; }
        v = lane(); v[2] = [String(x)];
        steps.push({ v, m: `${x} &gt; ${min} is true, so ${x} moves on to map.` });
        v = lane(); v[3] = [String(x * mul)];
        steps.push({ v, m: `map turns ${x} into ${x * mul}.` });
        out.push(x * mul);
        v = lane();
        steps.push({ v, m: `limit lets it through (${out.length} of ${lim}) and toList stores ${x * mul}.` });
        if (out.length >= lim) {
          steps.push({ v: lane(), m: `limit has its ${lim} elements, so the pipeline stops. ${src.length - pulled} element(s) were never read at all. Result: [${out.join(', ')}]` });
          return;
        }
      }
      steps.push({ v: lane(), m: `The source ran out. Result: [${out.join(', ')}]` });
    }
    function show(f) {
      const st = f ? steps[f - 1] : { v: [nums($('[data-in="src"]', b).value).map(String), [], [], [], []], m: 'Press ▶ Play. Nothing happens until a terminal operation (here toList) asks for elements.' };
      st.v.forEach((items, i) => { lanesEl.querySelector(`[data-lane="${i}"]`).innerHTML = items.map(x => `<span class="jv-chip t${i}">${esc(x)}</span>`).join(''); });
      msg.innerHTML = f ? `<b>Step ${f} of ${steps.length}.</b> ${st.m}` : st.m;
    }
    b.querySelectorAll('[data-in]').forEach(i => i.addEventListener('input', () => { build(); P.load(steps.length + 1); }));
    build();
    P.load(steps.length + 1);
  };

  /* ---------- jlambda: the core functional interfaces ---------- */
  W.jlambda = el => {
    const F = {
      Predicate: { sig: 'boolean test(T t)', lam: 's -> s.length() > 5', ref: 'String::isBlank', use: 'Filtering: keep only test names longer than 5 letters.', run: s => String(s.length > 5) },
      Function: { sig: 'R apply(T t)', lam: 's -> s.length()', ref: 'String::length', use: 'Mapping: turn each value into another value.', run: s => String(s.length) },
      Consumer: { sig: 'void accept(T t)', lam: 's -> System.out.println(s)', ref: 'System.out::println', use: 'Doing something with each value, such as printing or logging.', run: s => 'prints ' + s },
      Supplier: { sig: 'T get()', lam: '() -> "user_" + counter++', ref: 'UUID::randomUUID', use: 'Creating values on demand, such as test data or lazy defaults.', run: (s, n) => 'user_' + n },
      UnaryOperator: { sig: 'T apply(T t)', lam: 's -> s.toUpperCase()', ref: 'String::toUpperCase', use: 'Same type in and out: clean up or transform a value.', run: s => s.toUpperCase() },
      BiFunction: { sig: 'R apply(T t, U u)', lam: '(s, n) -> s.repeat(n)', ref: 'String::repeat', use: 'Two inputs, one output.', run: s => s.repeat(2) },
    };
    const b = K.shell(el, 'Pick an interface, then call its lambda', 'Every lambda is an object that implements one abstract method. Pick an interface, type an input and press Call.');
    b.innerHTML = `${K.seg('fi', Object.keys(F).map(k => [k, k]), 'Predicate')}
      <div class="jv-time" style="grid-template-columns:150px 1fr"><span>Abstract method</span><code data-o="sig"></code><span>As a lambda</span><code data-o="lam"></code><span>As a method ref</span><code data-o="ref"></code><span>Used for</span><span data-o="use"></span></div>
      ${row('Input t', '<input class="jv-in" data-in="t" value="checkout">')}<button type="button" class="vz-go" data-go>▶ Call it</button>
      <div class="vz-msg" aria-live="polite"></div>`;
    let cur = 'Predicate', calls = 0;
    const fill = () => { const f = F[cur]; ['sig', 'lam', 'ref', 'use'].forEach(k => { $(`[data-o="${k}"]`, b).textContent = f[k]; }); $('.vz-msg', b).innerHTML = 'Press ▶ Call it to run the lambda body with your input.'; };
    K.wireSeg(b, 'fi', v => { cur = v; calls = 0; fill(); });
    $('[data-go]', b).onclick = () => {
      const t = $('[data-in="t"]', b).value, f = F[cur];
      calls++;
      const arg = cur === 'Supplier' ? '' : cur === 'BiFunction' ? `"${t}", 2` : `"${t}"`;
      const res = f.run(t, calls - 1);
      $('.vz-msg', b).innerHTML = `<code>${esc(cur === 'Consumer' ? 'consumer.accept(' + arg + ')' : cur === 'Supplier' ? 'supplier.get()' : cur.toLowerCase() + '.' + f.sig.split(' ')[1].split('(')[0] + '(' + arg + ')')}</code> runs the body <code>${esc(f.lam.split('->')[1].trim())}</code> and gives <mark>${esc(res)}</mark>.`;
    };
    fill();
  };

  /* ---------- jswitch: pattern matching for switch ---------- */
  W.jswitch = el => {
    const b = K.shell(el, 'Which case wins', 'Choose a shape and its size. Java checks the cases from top to bottom, and the first pattern that matches (with its guard) wins.');
    const code = ['String describe(Shape s) {', '  return switch (s) {', '    case Circle c when c.r() > 10 -> "big circle";', '    case Circle c                 -> "circle, area " + area(c);', '    case Square sq when sq.side() == 0 -> "empty square";', '    case Square sq                -> "square, area " + area(sq);', '    case Rect(double w, double h) -> "rectangle " + w + " x " + h;', '  };', '}'];
    b.innerHTML = `${K.seg('shape', [['Circle', 'Circle'], ['Square', 'Square'], ['Rect', 'Rect']], 'Circle')}
      ${row('Size', '<input class="jv-in" data-in="a" value="12" style="width:80px"> <input class="jv-in" data-in="b" value="3" style="width:80px" hidden>')}
      <pre class="jv-code">${code.map((l, i) => `<div data-l="${i + 1}">${esc(l)}</div>`).join('')}</pre><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let shape = 'Circle', steps = [];
    const P = K.Player($('.vz-p', b), f => {
      b.querySelectorAll('.jv-code div').forEach(d => d.classList.toggle('on', f > 0 && +d.dataset.l === steps[f - 1].l));
      $('.vz-msg', b).innerHTML = f ? `<b>Step ${f} of ${steps.length}.</b> ${steps[f - 1].m}` : 'Press ▶ Play to see the cases checked in order.';
    }, 1100);
    function build() {
      const a = +$('[data-in="a"]', b).value || 0, h = +$('[data-in="b"]', b).value || 0;
      $('[data-in="b"]', b).hidden = shape !== 'Rect';
      const obj = shape === 'Circle' ? `Circle[r=${a}]` : shape === 'Square' ? `Square[side=${a}]` : `Rect[w=${a}, h=${h}]`;
      steps = [{ l: 2, m: `The switch receives <code>${obj}</code>.` }];
      const cases = [
        [3, 'Circle', () => a > 10, `Type matches Circle, and the guard r &gt; 10 is ${a > 10}.`, 'big circle'],
        [4, 'Circle', () => true, 'Type matches Circle, no guard.', `circle, area ${(Math.PI * a * a).toFixed(2)}`],
        [5, 'Square', () => a === 0, `Type matches Square, and the guard side == 0 is ${a === 0}.`, 'empty square'],
        [6, 'Square', () => true, 'Type matches Square, no guard.', `square, area ${(a * a).toFixed(1)}`],
        [7, 'Rect', () => true, `Record pattern: Java pulls out w = ${a} and h = ${h} for you.`, `rectangle ${a.toFixed(1)} x ${h.toFixed(1)}`]];
      for (const [l, t, g, why, res] of cases) {
        if (t !== shape) { steps.push({ l, m: `Not a ${t}, so this case is skipped.` }); continue; }
        if (!g()) { steps.push({ l, m: why + ' The guard fails, so Java moves on.' }); continue; }
        steps.push({ l, m: why + ` This case wins and the switch gives <mark>"${esc(res)}"</mark>.` });
        break;
      }
      P.load(steps.length + 1);
    }
    K.wireSeg(b, 'shape', v => { shape = v; build(); });
    b.querySelectorAll('[data-in]').forEach(i => i.addEventListener('input', build));
    build();
  };

  /* ---------- jvthreads: blocking work on platform and virtual threads ---------- */
  W.jvthreads = el => {
    const b = K.shell(el, 'Ten thousand waiting tasks', 'Each task waits for a slow service (blocking I/O). Change the numbers and compare a fixed pool of platform threads with one virtual thread per task.');
    b.innerHTML = `${K.slider('tasks', 'Tasks', 10, 10000, 1000, 10)} ${K.slider('wait', 'Wait per task (ms)', 50, 2000, 500, 50)} ${K.slider('pool', 'Platform pool size', 1, 400, 100, 1)}
      <div class="jv-time" data-t></div><div class="vz-msg" aria-live="polite"></div>`;
    function draw() {
      const n = +$('[data-sl="tasks"]', b).value, w = +$('[data-sl="wait"]', b).value, p = +$('[data-sl="pool"]', b).value;
      const plat = Math.ceil(n / p) * w, virt = w + Math.ceil(n / 2000) * 5, max = Math.max(plat, virt);
      const bar = (ms, c) => `<div style="display:flex;align-items:center;gap:8px;min-width:0"><div class="jv-bar" style="flex:0 0 auto;width:calc(${Math.max(2, ms / max * 100)}% - 60px);min-width:6px;padding:0;background:${c}"></div><b style="white-space:nowrap">${ms >= 1000 ? (ms / 1000).toFixed(1) + ' s' : ms + ' ms'}</b></div>`;
      $('[data-t]', b).innerHTML = `<span>Platform pool of ${p}</span>${bar(plat, 'var(--orange)')}<span>Virtual threads</span>${bar(virt, 'var(--green)')}`;
      $('.vz-msg', b).innerHTML = `With ${p} platform threads only ${p} tasks can wait at the same time, so ${n} tasks need ${Math.ceil(n / p)} rounds of ${w} ms. Each platform thread also holds about 1 MB of stack. A virtual thread that blocks is <b>unmounted</b> from its carrier thread, so all ${n} tasks can wait together on a few carrier threads (one per CPU core). That is about <mark>${(plat / virt).toFixed(1)}×</mark> faster here. Virtual threads help when tasks <b>wait</b>. For pure calculation, the number of CPU cores is still the limit.`;
    }
    ['tasks', 'wait', 'pool'].forEach(s => K.wireSlider(b, s, draw));
    draw();
  };

  /* ---------- jclassload: delegation and the three phases ---------- */
  W.jclassload = el => {
    const b = K.shell(el, 'Who loads this class', 'Type a class name, or pick one, then press Play. The application class loader always asks its parent first.');
    b.innerHTML = `${row('Class', '<input class="jv-in" data-in="cls" value="com.shop.Cart" style="width:240px">')}
      ${K.seg('pick', [['java.lang.String', 'String'], ['java.sql.Connection', 'java.sql'], ['com.shop.Cart', 'Your class'], ['org.missing.Ghost', 'Missing']], 'com.shop.Cart')}
      <div class="jv-tree"><div class="jv-node" data-n="boot">Bootstrap loader (java.base: java.lang, java.util ...)</div><div class="jv-node" data-n="plat">Platform loader (java.sql, java.net.http, java.xml ...)</div><div class="jv-node" data-n="app">Application loader (your classpath and module path)</div></div>
      <div class="jv-row" data-phases><span class="jv-node" data-n="load">1. Load</span><span class="jv-node" data-n="verify">2. Verify</span><span class="jv-node" data-n="prepare">3. Prepare</span><span class="jv-node" data-n="resolve">4. Resolve</span><span class="jv-node" data-n="init">5. Initialise</span></div>
      <div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let steps = [];
    const P = K.Player($('.vz-p', b), f => {
      const st = f ? steps[f - 1] : { on: [], ok: [], m: 'Press ▶ Play.' };
      b.querySelectorAll('.jv-node').forEach(n => { n.classList.toggle('on', st.on.includes(n.dataset.n)); n.classList.toggle('ok', (st.ok || []).includes(n.dataset.n)); });
      $('.vz-msg', b).innerHTML = f ? `<b>Step ${f} of ${steps.length}.</b> ${st.m}` : st.m;
    }, 1300);
    function build() {
      const c = $('[data-in="cls"]', b).value.trim() || 'com.shop.Cart';
      const where = /^java\.(lang|util|io|nio|time|math|net|text)\b/.test(c) ? 'boot' : /^java\.(sql|net\.http|xml|logging)\b|^javax\./.test(c) ? 'plat' : /missing|ghost/i.test(c) ? null : 'app';
      steps = [{ on: ['app'], m: `Your code mentions <code>${esc(c)}</code> for the first time. The JVM asks the application class loader.` },
        { on: ['plat'], m: 'Rule one is <b>delegation</b>: before looking itself, the application loader asks its parent, the platform loader.' },
        { on: ['boot'], m: 'The platform loader asks its own parent, the bootstrap loader, which is built into the JVM.' }];
      if (where === 'boot') steps.push({ on: ['boot'], ok: ['boot'], m: 'Found in java.base. Core classes always come from the bootstrap loader, so nobody can replace java.lang.String with a fake.' });
      else {
        steps.push({ on: ['plat'], m: 'Bootstrap does not have it, so the request comes back down to the platform loader.' });
        if (where === 'plat') steps.push({ on: ['plat'], ok: ['plat'], m: 'Found in a platform module.' });
        else {
          steps.push({ on: ['app'], m: 'Not there either, so the application loader finally searches the classpath.' });
          if (!where) { steps.push({ on: ['app'], m: `Nobody has it. The result is <mark>ClassNotFoundException</mark> when loading by name, or NoClassDefFoundError when a compiled class was there at build time but is missing now.` }); P.load(steps.length + 1); return; }
          steps.push({ on: ['app'], ok: ['app'], m: 'Found in your JAR or classes folder.' });
        }
      }
      steps.push({ on: ['load'], ok: [where], m: 'Loading: the bytes of the .class file are read and a Class object is created in the metaspace.' },
        { on: ['verify'], ok: [where, 'load'], m: 'Verifying: the bytecode verifier checks the code is safe, for example no jumps outside the method and correct types on the operand stack.' },
        { on: ['prepare'], ok: [where, 'load', 'verify'], m: 'Preparing: memory for static fields is set up with default values such as 0, false and null.' },
        { on: ['resolve'], ok: [where, 'load', 'verify', 'prepare'], m: 'Resolving: symbolic names such as java/util/List in the constant pool are turned into real references, often lazily.' },
        { on: ['init'], ok: [where, 'load', 'verify', 'prepare', 'resolve'], m: 'Initialising: static field values and static blocks run, once, just before first real use.' });
      P.load(steps.length + 1);
    }
    K.wireSeg(b, 'pick', v => { $('[data-in="cls"]', b).value = v; build(); });
    $('[data-in="cls"]', b).addEventListener('input', build);
    build();
  };

  /* ---------- jcf: sequential calls against CompletableFuture ---------- */
  W.jcf = el => {
    const b = K.shell(el, 'Three slow services', 'A product page needs price, stock and reviews from three services. Drag the delays and compare calling them one after another with supplyAsync and allOf.');
    b.innerHTML = `${K.slider('p', 'Price service (ms)', 50, 2000, 400, 50)} ${K.slider('s', 'Stock service (ms)', 50, 2000, 700, 50)} ${K.slider('r', 'Reviews service (ms)', 50, 2000, 300, 50)}
      <div class="jv-time" data-t style="grid-template-columns:150px 1fr"></div><div class="vz-msg" aria-live="polite"></div>`;
    function draw() {
      const p = +$('[data-sl="p"]', b).value, s = +$('[data-sl="s"]', b).value, r = +$('[data-sl="r"]', b).value;
      const seq = p + s + r, par = Math.max(p, s, r);
      const lane = (start, len, c) => `<div style="position:relative;height:26px;overflow:hidden"><div class="jv-bar" style="position:absolute;left:${Math.min(start / seq * 100, 98)}%;width:max(4px, ${len / seq * 100}%);padding:0;background:${c}"></div></div>`;
      $('[data-t]', b).innerHTML = `<b>One after another</b><span>${seq} ms in total</span>
        <span>price ${p} ms</span>${lane(0, p, 'var(--orange)')}<span>stock ${s} ms</span>${lane(p, s, 'var(--blue)')}<span>reviews ${r} ms</span>${lane(p + s, r, 'var(--purple)')}
        <b>supplyAsync + allOf</b><span>${par} ms in total</span>
        <span>price ${p} ms</span>${lane(0, p, 'var(--orange)')}<span>stock ${s} ms</span>${lane(0, s, 'var(--blue)')}<span>reviews ${r} ms</span>${lane(0, r, 'var(--purple)')}`;
      $('.vz-msg', b).innerHTML = `Sequential time is the <b>sum</b>: ${p} + ${s} + ${r} = ${seq} ms. In parallel the page waits only for the <b>slowest</b> call: max(${p}, ${s}, ${r}) = ${par} ms, a saving of <mark>${seq - par} ms</mark>. This only works when the calls do not need each other's results.`;
    }
    ['p', 's', 'r'].forEach(x => K.wireSlider(b, x, draw));
    draw();
  };

  /* ---------- jsql: string concatenation against PreparedStatement ---------- */
  W.jsql = el => {
    const users = [['asha', 'admin'], ['ravi', 'customer'], ['meera', 'customer']];
    const b = K.shell(el, 'Type a login name like an attacker would', 'Try a normal name such as ravi, then try  x\' OR \'1\'=\'1  and compare the two ways of building the query.');
    b.innerHTML = `${row('Name typed in the form', '<input class="jv-in" data-in="n" value="ravi" style="width:240px">')}
      <div class="jv-grid2"><div><b>❌ Glued string</b><pre class="jv-code" data-a style="margin:6px 0"></pre><div data-ra></div></div><div><b>✅ PreparedStatement</b><pre class="jv-code" data-b style="margin:6px 0"></pre><div data-rb></div></div></div><div class="vz-msg" aria-live="polite"></div>`;
    function draw() {
      const n = $('[data-in="n"]', b).value;
      const glued = `SELECT name, role FROM users WHERE name = '${n}'`;
      $('[data-a]', b).innerHTML = esc(`"SELECT ... WHERE name = '" + name + "'"\n\nsent to the database:\n${glued}`);
      $('[data-b]', b).innerHTML = esc(`"SELECT ... WHERE name = ?"\nps.setString(1, name)\n\nsent to the database:\nquery plan + one value: "${n}"`);
      const injected = /'\s*or\s*'?\d'?\s*=\s*'?\d/i.test(n) || /'\s*or\s+1\s*=\s*1/i.test(n);
      const ra = injected ? users : users.filter(u => u[0] === n);
      const rb = users.filter(u => u[0] === n);
      const list = rs => rs.length ? rs.map(u => `<span class="jv-res ${rs === ra && injected ? 'no' : 'yes'}">${u[0]} (${u[1]})</span>`).join(' ') : '<span class="jv-res">no rows</span>';
      $('[data-ra]', b).innerHTML = list(ra);
      $('[data-rb]', b).innerHTML = list(rb);
      $('.vz-msg', b).innerHTML = injected
        ? 'The quote in the input closed the string early, and <code>OR \'1\'=\'1\'</code> is always true, so the glued query returns <mark>every user</mark>. The prepared statement sent the text as one plain value, so it simply found no user with that strange name.'
        : 'With normal input both versions return the same rows. The difference only shows up with hostile input, which is exactly why security tests type quotes into every field.';
    }
    $('[data-in="n"]', b).addEventListener('input', draw);
    draw();
  };

  /* ---------- jrelease: what you gain by upgrading ---------- */
  const REL = [
    [8, 2014, 1, 'Lambdas, streams, Optional, java.time, default methods'], [9, 2017, 0, 'Modules (JPMS), jshell, List.of and Map.of, private interface methods'],
    [10, 2018, 0, 'var for local variables'], [11, 2018, 1, 'HttpClient, String.isBlank, lines, strip, repeat, run java Hello.java directly'],
    [12, 2019, 0, 'Switch expressions (preview)'], [13, 2019, 0, 'Text blocks (preview)'], [14, 2020, 0, 'Switch expressions final, helpful NullPointerException messages'],
    [15, 2020, 0, 'Text blocks final, ZGC ready for production'], [16, 2021, 0, 'Records and pattern matching for instanceof final, Stream.toList()'],
    [17, 2021, 1, 'Sealed classes final, strong encapsulation of JDK internals'], [18, 2022, 0, 'UTF-8 by default, simple web server (jwebserver)'],
    [19, 2022, 0, 'Virtual threads and record patterns (preview)'], [20, 2023, 0, 'Scoped values (incubator)'],
    [21, 2023, 1, 'Virtual threads, record patterns, pattern matching for switch, sequenced collections, generational ZGC'],
    [22, 2024, 0, 'Unnamed variables _, foreign function and memory API, launch multi file programs'], [23, 2024, 0, 'Markdown in documentation comments'],
    [24, 2025, 0, 'Stream gatherers, class file API, virtual threads no longer pinned by synchronized, quantum safe ML-KEM and ML-DSA'],
    [25, 2025, 1, 'Compact source files and instance main, module import declarations, flexible constructor bodies, scoped values, key derivation API, compact object headers'],
    [26, 2026, 0, 'HTTP/3 for HttpClient, applet API removed, warnings before final fields can be changed by reflection, AOT object caching with any GC'],
    [27, 2026, 0, 'G1 is the default collector everywhere, compact object headers by default, post quantum hybrid key exchange for TLS 1.3'],
  ];
  W.jrelease = el => {
    const b = K.shell(el, 'Plan an upgrade', 'Pick the Java version your project runs today and the one you want. The list shows every headline feature you gain. LTS versions get years of updates.');
    const opts = v => REL.map(r => `<option value="${r[0]}"${r[0] === v ? ' selected' : ''}>Java ${r[0]}${r[2] ? ' LTS' : ''}</option>`).join('');
    b.innerHTML = `${row('From', `<select class="jv-in" data-in="a">${opts(11)}</select>`)}${row('To', `<select class="jv-in" data-in="b">${opts(25)}</select>`)}<ol class="jv-steps" data-l></ol><div class="vz-msg" aria-live="polite"></div>`;
    function draw() {
      const a = +$('[data-in="a"]', b).value, z = +$('[data-in="b"]', b).value;
      const gain = REL.filter(r => r[0] > Math.min(a, z) && r[0] <= Math.max(a, z));
      $('[data-l]', b).innerHTML = gain.map(r => `<li${r[2] ? ' class="on"' : ''}><b>Java ${r[0]}</b> (${r[1]}${r[2] ? ', LTS' : ''}): ${esc(r[3])}</li>`).join('') || '<li>Pick two different versions.</li>';
      const lts = gain.filter(r => r[2]).length;
      $('.vz-msg', b).innerHTML = a === z ? 'Same version, nothing to gain.' : `${gain.length} releases and ${lts} LTS step(s). Teams usually jump from LTS to LTS (8, 11, 17, 21, 25), test on the new version in CI first, and use preview features only in experiments.`;
    }
    b.querySelectorAll('[data-in]').forEach(s => s.addEventListener('change', draw));
    draw();
  };

  /* ---------- the page ---------- */
  function start(opts) {
    document.getElementById('comic').innerHTML = PAGE.info ? XTRA.infoHtml(PAGE.info) : '';
    document.getElementById('real-life').innerHTML = PAGE.real ? XTRA.realHtml(PAGE.real) : '';
    document.getElementById('quiz').innerHTML = LEARN.quizHtml(PAGE.quiz || [], { lang: 'java' });
    document.getElementById('numbers').innerHTML = LEARN.calcHtml(PAGE.calc || [], { lang: 'java' });
    VIZ.mountAll(document);
    XTRA.wire(document);
    LEARN.wire();
    FUN.initScroll();
    FUN.observe();
    VOICE.setup({ title: opts.title, segments: PAGE.say || [] });
    document.getElementById('listenAll').onclick = () => VOICE.playAll();
    document.addEventListener('click', e => {
      const c = e.target.closest('.codebar .copy');
      if (c) {
        const txt = c.closest('.codewrap').querySelector('pre.src.main, pre.src').textContent;
        const done = () => { c.textContent = 'Copied'; setTimeout(() => { c.textContent = 'Copy'; }, 1200); };
        if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, done); else done();
        return;
      }
      const t = e.target.closest('.codebar .xv-try');
      if (!t) return;
      const wrap = t.closest('.codewrap');
      let host = wrap.querySelector(':scope > .xv-host');
      const on = t.getAttribute('aria-pressed') !== 'true';
      if (!host) {
        host = document.createElement('div');
        host.className = 'xv-host';
        wrap.querySelector('pre.src.main').after(host);
      }
      t.setAttribute('aria-pressed', String(on));
      t.textContent = on ? '✖ Close the replay' : '👣 Run line by line';
      if (on) {
        const pre = wrap.querySelector('pre.src.main');
        host.hidden = false;
        XV.mount(host, { key: wrap.dataset.trace, code: pre.textContent, lang: 'java', html: pre.innerHTML });
        host.querySelector('.xv').focus({ preventScroll: true });
      } else {
        XV.unmountIn(host);
        host.hidden = true;
      }
    });
    /* inside the portal, chapter links open in the portal so the contents list stays in sync */
    if (FUN.inFrame) document.querySelectorAll('.pager a[data-topic]').forEach(a => { a.href = '../../subject.html?s=java&t=' + a.dataset.topic; a.target = '_top'; });
    else document.querySelector('.home-link').removeAttribute('target');
  }
  window.JAVAPAGE = { start };
})();
