/* ===== Complete Machine Learning animations, part 1: the framework and the Foundations widgets.
   Every animation is a step by step trace. It starts empty. Each press of Step adds one piece of the picture and
   explains that piece in plain words under it, until the picture is complete. Play runs the steps, Back undoes one,
   and Reset puts every value back to how the page first showed it. Every trace is worked out again from the
   reader's own input whenever a value changes. assets/mlvoice.js can read each step aloud.

   MLZ.trace(name, spec) wraps CVZ.def (assets/cvviz.js):
     spec.frames(p) -> [ { say: 'what happens in this step', ...anything paint needs } ]
     spec.paint(z, frame, frames, index)   draws one frame on z.g
   Part 2 (supervised and unsupervised) is in assets/mlwidgets2.js and part 3 (reinforcement, deep learning and
   MLOps) in assets/mlwidgets3.js. Drawing helpers come from CVZ.D and AIZ (assets/aiwidgets.js). ===== */
const MLZ = (() => {
  const { D, def } = CVZ;
  const { tag, wrap, rr, tw, fit } = AIZ;
  const esc = CVZ.esc;
  const MAXF = 240;

  function blank(z) {
    D.text(z.g, 'Press Step to begin. The picture builds up one step at a time.', z.W / 2, z.H / 2, { a: 'center', s: 14, c: z.col.ink2 });
  }
  function trace(name, spec) {
    def(name, {
      title: spec.title, sub: spec.sub, W: spec.W || 600, H: spec.H || 340, params: spec.params || [], tips: spec.tips || [],
      startAtZero: true, init: spec.init, change: spec.change,
      speed: () => spec.speed || 1400,
      steps(z) {
        try { z.state.fr = spec.frames(z.p, z); z.state.err = ''; } catch (e) { z.state.fr = []; z.state.err = e.message; }
        if (z.state.fr.length > MAXF) z.state.fr = z.state.fr.slice(0, MAXF).concat([{ ...z.state.fr[MAXF - 1], say: `The trace is long, so it stops here after ${MAXF} steps. Try a smaller input.`, cut: true }]);
        return z.state.fr.length;
      },
      draw(z) {
        const fr = z.state.fr || [];
        if (z.state.err) { D.text(z.g, 'Please check the input.', z.W / 2, z.H / 2, { a: 'center', s: 14, c: z.col.red }); return `<p class="cai-now"><b class="k">Input problem.</b> ${esc(z.state.err)}</p>`; }
        if (!z.step) { blank(z); return '<p class="cai-now cai-start">Nothing is shown yet. Press <b>Step</b> to see the first step, or <b>Play</b> to watch every step. Each step adds one new piece and explains it here.</p>'; }
        const f = fr[z.step - 1];
        spec.paint(z, f, fr, z.step - 1);
        const log = fr.slice(0, z.step - 1).map(x => `<li>${x.say}</li>`).join('');
        return `<div class="cai-now"><b class="k">Step ${z.step} of ${fr.length}.</b> ${f.say}</div>` + (f.extra || '') +
          (z.step > 1 ? `<details class="cai-log"><summary>Earlier steps (${z.step - 1})</summary><ol>${log}</ol></details>` : '');
      }
    });
  }

  /* ---------- drawing helpers ---------- */
  function box(z, x, y, w, h, label, o = {}) {
    const c = z.col;
    rr(z.g, x, y, w, h, o.r ?? 8, { fill: o.fill || c.surf, stroke: o.stroke || c.line, w: o.w || 1.5, dash: o.dash });
    if (label !== undefined && label !== '') {
      const s = fit(z.g, String(label), w - 8, o.s || 13, { mono: o.mono, b: o.b });
      D.text(z.g, String(label), x + w / 2, y + h / 2 + 1, { a: 'center', bl: 'middle', s, mono: o.mono, b: o.b, c: o.c || c.ink });
    }
  }
  const head = (z, s, x, y, o = {}) => D.text(z.g, s, x, y, { s: o.s || 12, b: true, c: o.c || z.col.ink2, a: o.a || 'left' });
  const list = s => String(s).split(/[\s,]+/).map(x => x.trim()).filter(Boolean);
  const nums = s => list(String(s).replace(/−/g, '-')).map(Number).filter(v => !isNaN(v));
  /* "x y" or "x y label" per line (or separated by semicolons) */
  function points(s, withLabel) {
    return String(s).split(/[\n;]+/).map(l => l.trim()).filter(Boolean).map(l => {
      const p = l.replace(/−/g, '-').split(/[\s,]+/).filter(Boolean);
      const x = +p[0], y = +p[1];
      if (isNaN(x) || isNaN(y)) throw new Error('Each point needs two numbers, for example 2 3' + (withLabel ? ' A' : ''));
      return withLabel ? { x, y, c: p[2] || 'A' } : { x, y };
    });
  }
  const f2 = (v, d = 2) => {
    if (!isFinite(v)) return v > 0 ? '∞' : '−∞';
    const s = (Math.round(v * 10 ** d) / 10 ** d).toFixed(d);
    return s === '-0.00' || s === '-0.0' || s === '-0' ? s.slice(1) : s.replace('-', '−');
  };
  /* class colours that stay readable in light and dark mode */
  function klass(z, i) {
    const c = z.col;
    return [c.accent || '#2563eb', c.orange || '#ea580c', c.green || '#16a34a', c.purple || '#7c3aed', c.pink || '#db2777', c.teal || '#0d9488'][((i % 6) + 6) % 6];
  }

  /* a 2D plot box. Returns { X(x), Y(y), x0, y0, w, h } that maps data to the canvas */
  function plot(z, area, xr, yr, o = {}) {
    const [x0, y0, w, h] = area, c = z.col, g = z.g;
    rr(g, x0, y0, w, h, 6, { fill: c.surf, stroke: c.line });
    const X = v => x0 + 26 + (v - xr[0]) / (xr[1] - xr[0] || 1) * (w - 36);
    const Y = v => y0 + h - 20 - (v - yr[0]) / (yr[1] - yr[0] || 1) * (h - 30);
    if (o.grid !== false) {
      for (let i = 0; i <= 4; i++) {
        const xv = xr[0] + (xr[1] - xr[0]) * i / 4, yv = yr[0] + (yr[1] - yr[0]) * i / 4;
        D.line(g, X(xv), Y(yr[0]), X(xv), Y(yr[1]), c.line, 0.6, [2, 3]);
        D.line(g, X(xr[0]), Y(yv), X(xr[1]), Y(yv), c.line, 0.6, [2, 3]);
        D.text(g, f2(xv, o.dx ?? 1), X(xv), y0 + h - 6, { a: 'center', s: 10, c: c.ink2 });
        D.text(g, f2(yv, o.dy ?? 1), x0 + 22, Y(yv) + 3, { a: 'right', s: 10, c: c.ink2 });
      }
    }
    if (o.xl) D.text(g, o.xl, x0 + w - 6, y0 + h - 22, { a: 'right', s: 11, b: true, c: c.ink2 });
    if (o.yl) D.text(g, o.yl, x0 + 30, y0 + 14, { s: 11, b: true, c: c.ink2 });
    return { X, Y, x0, y0, w, h, xr, yr };
  }
  /* the range of some numbers with a little margin */
  function span(vals, pad = 0.1) {
    let lo = Math.min(...vals), hi = Math.max(...vals);
    if (!isFinite(lo)) { lo = 0; hi = 1; }
    if (lo === hi) { lo -= 1; hi += 1; }
    const m = (hi - lo) * pad;
    return [lo - m, hi + m];
  }
  /* draw a line y = a + b x across the plot */
  function fline(z, P, a, b, col, w = 2, dash) {
    const xa = P.xr[0], xb = P.xr[1];
    const g = z.g;
    g.save(); g.beginPath(); g.rect(P.x0, P.y0, P.w, P.h); g.clip();
    D.line(g, P.X(xa), P.Y(a + b * xa), P.X(xb), P.Y(a + b * xb), col, w, dash);
    g.restore();
  }
  /* a small horizontal bar chart: items [{ label, v, col }] */
  function bars(z, items, x, y, w, rowH = 22, o = {}) {
    const max = o.max ?? Math.max(1e-9, ...items.map(t => Math.abs(t.v)));
    const lw = o.lw ?? 90;
    items.forEach((t, i) => {
      const yy = y + i * rowH;
      const s = fit(z.g, t.label, lw - 6, 12);
      D.text(z.g, t.label, x + lw - 6, yy + rowH / 2 + 4, { a: 'right', s, c: z.col.ink });
      const bw = Math.max(1, Math.abs(t.v) / max * (w - lw - 60));
      rr(z.g, x + lw, yy + 3, bw, rowH - 7, 4, { fill: t.col || z.col.cv });
      D.text(z.g, o.fmt ? o.fmt(t.v) : f2(t.v), x + lw + bw + 6, yy + rowH / 2 + 4, { s: 12, b: true, c: z.col.ink });
    });
    return y + items.length * rowH;
  }
  /* a table of numbers drawn on the canvas */
  function grid(z, rows, x, y, cw, ch, o = {}) {
    rows.forEach((r, i) => r.forEach((v, j) => {
      const hl = o.hl && o.hl(i, j);
      box(z, x + j * cw, y + i * ch, cw - 2, ch - 2, v, { fill: hl ? (o.hlc || z.col.cv) : (i === 0 && o.headRow ? z.col.bg : z.col.surf), c: hl ? '#fff' : z.col.ink, s: o.s || 12, mono: o.mono, r: 4, b: i === 0 && o.headRow });
    }));
  }
  /* repeatable pseudo random numbers (Park and Miller), so a trace looks the same every time */
  function rng(seed) {
    let s = (Math.abs(Math.floor(seed)) % 2147483646) + 1;
    return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
  }

  return { trace, box, head, list, nums, points, f2, klass, plot, span, fline, bars, grid, rng, esc, D, tag, wrap, rr, tw, fit };
})();

/* =====================================================================================================
   Foundations 1.1  the learning loop: guess, measure the error, adjust, repeat
   ===================================================================================================== */
(() => {
  const { trace, box, head, plot, span, fline, f2, D, rr, points } = MLZ;
  trace('mlloop', {
    title: 'How a machine learns: guess, check, adjust, repeat',
    sub: 'Type a few (hours studied, marks) pairs. The machine starts with a bad guess for the rule "marks = w × hours" and improves it one round at a time.',
    W: 600, H: 340,
    params: [
      { k: 'pts', label: 'Data: hours marks (one pair per line)', type: 'area', v: '1 12\n2 19\n3 31\n4 38\n5 52' },
      { k: 'w0', label: 'First guess for w', type: 'range', v: 2, min: 0, max: 20, step: 1 },
      { k: 'lr', label: 'Learning rate (size of each correction)', type: 'range', v: 0.02, min: 0.005, max: 0.06, step: 0.005 },
      { k: 'rounds', label: 'Rounds of learning', type: 'range', v: 6, min: 2, max: 12 }
    ],
    tips: [
      { t: 'Play it. Watch the line turn towards the dots and the error number shrink each round.', play: true },
      { t: 'Make the learning rate 0.06. The corrections are too big, so w jumps past the best value and the error grows. This is called overshooting.', set: { lr: 0.06 }, play: true },
      { t: 'Start from w = 20, a guess that is too high. The machine still finds its way down to about 10.', set: { w0: 20 }, play: true }
    ],
    frames(p) {
      const pts = points(p.pts);
      if (pts.length < 2) throw new Error('Give at least two pairs.');
      const n = pts.length;
      const fr = [];
      let w = p.w0;
      const err = w => pts.reduce((s, q) => s + (w * q.x - q.y) ** 2, 0) / n;
      fr.push({ w, hist: [], show: 'data', say: `These ${n} dots are our data. Each dot is one student: how many hours they studied (across) and the marks they got (up). The machine has never seen a rule. Its job is to find one from these examples.` });
      fr.push({ w, hist: [], show: 'guess', say: `Round 0: the machine makes a first guess, marks = <b>${f2(w)}</b> × hours. The orange line shows this guess. It is far from the dots, which is fine. Every learner starts by guessing.` });
      const hist = [err(w)];
      fr.push({ w, hist: hist.slice(), show: 'err', say: `Check the guess. For each dot we measure how far the line is from it (the dashed red gaps), square each gap and take the average. This is the <b>error</b> (mean squared error): <b>${f2(err(w))}</b>. Big number, bad guess.` });
      for (let r = 1; r <= p.rounds; r++) {
        let grad = 0;
        pts.forEach(q => { grad += 2 * (w * q.x - q.y) * q.x; });
        grad /= n;
        const old = w;
        w = w - p.lr * grad;
        hist.push(err(w));
        const better = hist[hist.length - 1] < hist[hist.length - 2];
        fr.push({ w, hist: hist.slice(), show: 'err', say: `Round ${r}: the error says which way to move. Its slope is ${f2(grad)}, so w moves ${grad > 0 ? 'down' : 'up'} by learning rate × slope = ${f2(p.lr)} × ${f2(grad)}. New w = ${f2(old)} − (${f2(p.lr * grad)}) = <b>${f2(w)}</b>. Error now ${f2(hist[hist.length - 1])}, ${better ? 'smaller than before, so the machine is learning.' : 'bigger than before. The step was too large and jumped past the best value.'}` });
      }
      fr.push({ w, hist, show: 'err', done: true, say: `After ${p.rounds} rounds the rule is marks = <b>${f2(w)}</b> × hours. Nobody typed this rule. The machine found it from the examples by repeating four things: <b>guess, measure the error, adjust, repeat</b>. That loop is the heart of machine learning. A student who studies 6 hours is predicted to get about ${f2(w * 6, 0)} marks.` });
      return fr;
    },
    paint(z, f) {
      const pts = points(z.p.pts), c = z.col;
      const P = plot(z, [10, 10, 360, 300], span([0, ...pts.map(q => q.x)]), span([0, ...pts.map(q => q.y)]), { xl: 'hours', yl: 'marks' });
      if (f.show !== 'data') {
        if (f.show === 'err') pts.forEach(q => D.line(z.g, P.X(q.x), P.Y(q.y), P.X(q.x), P.Y(f.w * q.x), c.red, 1.4, [4, 3]));
        fline(z, P, 0, f.w, c.orange, 2.5);
      }
      pts.forEach(q => D.circle(z.g, P.X(q.x), P.Y(q.y), 5, { fill: c.cv, stroke: c.surf, w: 1.5 }));
      box(z, 385, 10, 205, 54, `marks = ${f2(f.w)} × hours`, { mono: true, s: 13, b: true, fill: c.bg });
      head(z, 'Error after each round', 385, 86);
      const h = f.hist || [];
      if (h.length) {
        const max = Math.max(...h, 1e-9);
        const bw = Math.min(26, 190 / h.length - 3);
        h.forEach((v, i) => {
          const bh = Math.max(2, v / max * 190);
          rr(z.g, 388 + i * (bw + 3), 290 - bh, bw, bh, 3, { fill: i === h.length - 1 ? c.orange : c.cv });
        });
        D.text(z.g, 'round 0 → ' + (h.length - 1), 388, 308, { s: 11, c: c.ink2 });
      }
      if (f.done) D.text(z.g, 'Learned!', 590, 86, { a: 'right', s: 13, b: true, c: c.green });
    }
  });
})();

/* =====================================================================================================
   Foundations 1.1  three kinds of learning: which one fits the task
   ===================================================================================================== */
(() => {
  const { trace, box, head, D, rr, wrap } = MLZ;
  const TASKS = {
    spam: { name: 'Mark emails as spam or not spam', kind: 'sup', task: 'classification', data: 'Old emails, each one labelled spam or not spam by people', out: 'A label for a new email' },
    price: { name: 'Guess the price of a house', kind: 'sup', task: 'regression', data: 'Past sales: size, rooms, area and the price paid', out: 'A number (the price)' },
    groups: { name: 'Split shop customers into groups', kind: 'unsup', task: 'clustering', data: 'What each customer bought, with no labels at all', out: 'Groups of similar customers' },
    fraud: { name: 'Spot strange card payments', kind: 'unsup', task: 'anomaly detection', data: 'Millions of normal payments, almost none labelled', out: 'A flag on payments that look unusual' },
    game: { name: 'Teach a robot to walk', kind: 'rl', task: 'control', data: 'No data at the start. The robot tries moves and gets a reward for moving forward', out: 'A policy: which move to make in each situation' },
    ads: { name: 'Pick which ad to show next', kind: 'rl', task: 'bandit', data: 'Clicks come back after each ad is shown', out: 'A choice that earns the most clicks over time' }
  };
  const KIND = { sup: ['Supervised learning', 'learn from examples that have the right answer (labels)'], unsup: ['Unsupervised learning', 'find patterns in data that has no answers'], rl: ['Reinforcement learning', 'learn by trying actions and getting rewards'] };
  trace('mltypes', {
    title: 'Supervised, unsupervised or reinforcement?',
    sub: 'Pick a task. The animation asks the three questions an expert asks and lands on the right kind of learning.',
    W: 600, H: 320,
    params: [{ k: 'task', label: 'Task', type: 'select', v: 'spam', opts: Object.keys(TASKS).map(k => [k, TASKS[k].name]) }],
    tips: [
      { t: 'Try "Split shop customers into groups". Nobody gave the right groups, so it is unsupervised.', set: { task: 'groups' }, play: true },
      { t: 'Try "Teach a robot to walk". There is no dataset at all, only rewards, so it is reinforcement learning.', set: { task: 'game' }, play: true }
    ],
    frames(p) {
      const t = TASKS[p.task];
      const fr = [];
      fr.push({ q: 1, say: `The task: <b>${t.name}</b>. First question: what data do we have? Answer: ${t.data}.` });
      const hasLabels = t.kind === 'sup';
      fr.push({ q: 2, say: `Second question: does each example come with the right answer (a <b>label</b>)? ${hasLabels ? 'Yes. People already marked the answer for every example.' : t.kind === 'rl' ? 'No. Nobody tells the learner the right move. It only gets a reward after it acts.' : 'No. We only have the raw data, with no answers.'}` });
      fr.push({ q: 3, say: `Third question: what should come out? ${t.out}. ${t.kind === 'sup' ? (t.task === 'regression' ? 'A number, so this is <b>regression</b>.' : 'A category, so this is <b>classification</b>.') : t.kind === 'unsup' ? 'There is no single right answer to copy, so the machine has to discover the structure itself.' : 'A sequence of decisions, judged by the total reward.'}` });
      fr.push({ q: 4, done: true, say: `So this is <b>${KIND[t.kind][0]}</b> (${t.task}): ${KIND[t.kind][1]}.` });
      return fr;
    },
    paint(z, f) {
      const t = TASKS[z.p.task], c = z.col;
      const cols = [['sup', 30], ['unsup', 220], ['rl', 410]];
      box(z, 20, 12, 560, 40, t.name, { b: true, s: 15, fill: c.bg });
      const qs = ['What data do we have?', 'Does each example have the right answer?', 'What should come out?'];
      qs.forEach((q, i) => {
        if (f.q > i) {
          rr(z.g, 20, 64 + i * 46, 560, 38, 8, { fill: c.surf, stroke: c.line });
          D.text(z.g, `${i + 1}. ${q}`, 32, 88 + i * 46, { s: 13, b: true, c: c.ink });
        }
      });
      if (f.q >= 4) {
        cols.forEach(([k, x]) => {
          const on = k === t.kind;
          box(z, x, 214, 160, 90, '', { fill: on ? c.cv : c.surf, stroke: on ? c.cv : c.line, w: on ? 3 : 1.5 });
          D.text(z.g, KIND[k][0], x + 80, 240, { a: 'center', s: 13, b: true, c: on ? '#fff' : c.ink2 });
          wrap(z.g, KIND[k][1], x + 10, 262, 140, { s: 11, c: on ? '#fff' : c.ink2 });
        });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 1.2  the life of an ML project, stage by stage, for a chosen product
   ===================================================================================================== */
(() => {
  const { trace, box, D, wrap, rr } = MLZ;
  const STAGES = ['Frame the problem', 'Get the data', 'Explore and clean', 'Split the data', 'Baseline', 'Train and tune', 'Evaluate on test', 'Deploy', 'Monitor'];
  const CASES = {
    eta: { name: 'Food delivery: predict the arrival time', s: [
      'Goal: show customers an arrival time they can trust. Output: minutes (a number), so regression. Success: 80% of orders arrive within 5 minutes of the promise.',
      'Two years of past orders: restaurant, distance, time of day, weather, rider, and the real minutes each took.',
      'Remove orders with a negative delivery time (clock errors), fill missing weather, and plot minutes against distance. Rush hour is clearly slower.',
      'Keep the last month as the test set. Time order matters: we must predict the future from the past, so a random split would cheat.',
      'Baseline: "distance in km times 3 minutes plus 10". Its average error is 9 minutes. Any model must beat that.',
      'Try linear regression, then gradient boosting with features like hour of day and rain. Tune on a validation month. Best average error: 4.8 minutes.',
      'One final check on the untouched test month: 5.1 minutes. Close to validation, so the model generalises.',
      'Put the model behind an API. The app sends the order details and gets minutes back in under 50 milliseconds.',
      'Watch the error every day. A new city or a festival changes traffic, so the model is retrained when the error drifts up.'] },
    churn: { name: 'Mobile network: who will leave next month', s: [
      'Goal: phone the customers likely to leave and offer a better plan. Output: leave or stay, so classification. Success: catch most leavers without calling everyone.',
      'Twelve months of customer records: plan, bills, dropped calls, support tickets, and whether each customer left.',
      'Only 5% of customers left, so the classes are imbalanced. Remove test accounts, merge duplicates and turn plan names into numbers.',
      'Split customers 70 / 15 / 15 into train, validation and test, keeping 5% leavers in each part (a stratified split).',
      'Baseline: "nobody leaves" is 95% accurate and useless. So we measure recall (leavers caught) and precision (calls that were right) instead.',
      'Train logistic regression and a random forest. Tune the decision threshold on validation to catch 70% of leavers with 40% precision.',
      'On the test customers: 68% recall, 39% precision. The business agrees this saves money.',
      'Run the model every night on all customers and send a call list to the retention team.',
      'Check every month that the leaver rate and the input data look the same as before. A new competitor would change both.'] }
  };
  trace('mlflow', {
    title: 'The life of a machine learning project',
    sub: 'Pick a product. Each step adds one stage of the project and says what the team really does in it.',
    W: 600, H: 330,
    params: [{ k: 'c', label: 'Project', type: 'select', v: 'eta', opts: Object.keys(CASES).map(k => [k, CASES[k].name]) }],
    tips: [{ t: 'Compare both projects at the "Split the data" stage: one splits by time, the other keeps the class balance.', set: { c: 'churn' }, play: true }],
    frames(p) {
      const C = CASES[p.c];
      return STAGES.map((s, i) => ({ i, say: `<b>Stage ${i + 1}: ${s}.</b> ${C.s[i]}` })).concat([{ i: 9, done: true, say: 'That is the whole loop. Notice that training the model is only one stage of nine. Real teams spend most of their time on the problem, the data and keeping the model healthy. The arrow from Monitor back to the start means the loop never really ends.' }]);
    },
    paint(z, f) {
      const c = z.col;
      STAGES.forEach((s, i) => {
        if (i > f.i) return;
        const col = i % 3, row = Math.floor(i / 3);
        const x = 20 + col * 195, y = 20 + row * 100;
        const on = i === f.i;
        box(z, x, y, 170, 60, '', { fill: on ? c.cv : c.surf, stroke: on ? c.cv : c.line, w: on ? 2.5 : 1.5 });
        D.text(z.g, String(i + 1), x + 14, y + 22, { s: 16, b: true, c: on ? '#fff' : c.cv });
        wrap(z.g, s, x + 32, y + 24, 130, { s: 13, b: true, c: on ? '#fff' : c.ink });
        if (i < 8 && i < f.i) {
          if (col < 2) D.arrow(z.g, x + 172, y + 30, x + 193, y + 30, c.ink2, 1.6);
          else D.arrow(z.g, x + 85, y + 62, x + 85, y + 98, c.ink2, 1.6);
        }
      });
      if (f.done) {
        D.arrow(z.g, 410, 300, 300, 318, c.green, 2);
        D.line(z.g, 300, 318, 10, 318, c.green, 2);
        D.line(z.g, 10, 318, 10, 50, c.green, 2);
        D.arrow(z.g, 10, 50, 18, 50, c.green, 2);
        D.text(z.g, 'retrain and improve', 150, 312, { a: 'center', s: 11, b: true, c: c.green });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 1.2  train, validation and test split, with or without stratifying
   ===================================================================================================== */
(() => {
  const { trace, head, D, rr, rng, f2 } = MLZ;
  trace('mlsplit', {
    title: 'Splitting data into train, validation and test sets',
    sub: 'Each square is one example. Orange squares are the rare class (for example "customer left"). Watch how the split is made and how many rare examples land in each part.',
    W: 600, H: 330,
    params: [
      { k: 'n', label: 'Number of examples', type: 'range', v: 40, min: 20, max: 80, step: 10 },
      { k: 'rare', label: 'Share of the rare class', type: 'range', v: 0.2, min: 0.05, max: 0.5, step: 0.05 },
      { k: 'val', label: 'Validation share', type: 'range', v: 0.2, min: 0, max: 0.3, step: 0.05 },
      { k: 'test', label: 'Test share', type: 'range', v: 0.2, min: 0.1, max: 0.4, step: 0.05 },
      { k: 'strat', label: 'Stratify (keep the class balance in every part)', type: 'check', v: false },
      { k: 'seed', label: 'Shuffle seed', type: 'range', v: 7, min: 1, max: 30 }
    ],
    tips: [
      { t: 'Set the rare share to 0.1 and play without stratify. Often the test set gets too few or too many rare examples, so its score is unreliable.', set: { rare: 0.1, strat: false }, play: true },
      { t: 'Now tick Stratify. Every part gets the same share of rare examples as the whole dataset.', set: { rare: 0.1, strat: true }, play: true }
    ],
    frames(p) {
      const n = p.n, R = rng(p.seed);
      const nr = Math.max(1, Math.round(n * p.rare));
      const items = [];
      for (let i = 0; i < n; i++) items.push({ id: i, rare: i < nr });
      const fr = [];
      const nt = Math.round(n * p.test), nv = Math.round(n * p.val), ntr = n - nt - nv;
      if (ntr < 2) throw new Error('Validation and test take almost everything. Make them smaller.');
      fr.push({ items: items.map(x => ({ ...x, part: 'all' })), say: `We start with ${n} examples in the order they were collected. ${nr} of them (${f2(nr / n * 100, 0)}%) belong to the rare class, shown in orange.` });
      const sh = items.slice();
      for (let i = sh.length - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [sh[i], sh[j]] = [sh[j], sh[i]]; }
      fr.push({ items: sh.map(x => ({ ...x, part: 'all' })), say: `Shuffle first (seed ${p.seed}). Data is often stored in a pattern, for example by date or by class. Shuffling makes every part a fair sample. (For time series we do not shuffle, we split by time instead.)` });
      let parts;
      if (p.strat) {
        parts = {};
        const assign = (list) => {
          const t = Math.round(list.length * p.test), v = Math.round(list.length * p.val);
          list.forEach((x, k) => { parts[x.id] = k < t ? 'test' : k < t + v ? 'val' : 'train'; });
        };
        assign(sh.filter(x => x.rare));
        assign(sh.filter(x => !x.rare));
      } else {
        parts = {};
        sh.forEach((x, k) => { parts[x.id] = k < nt ? 'test' : k < nt + nv ? 'val' : 'train'; });
      }
      const final = sh.map(x => ({ ...x, part: parts[x.id] }));
      const count = (part) => final.filter(x => x.part === part).length;
      const rcount = (part) => final.filter(x => x.part === part && x.rare).length;
      const order = ['test', 'val', 'train'];
      const names = { train: 'training set', val: 'validation set', test: 'test set' };
      const why = { test: 'It is locked away and used only once, at the very end, to estimate how the model will do in real life.', val: 'We use it again and again to compare models and settings, so we never touch the test set while choosing.', train: 'The model learns its parameters only from these examples.' };
      const shown = [];
      order.forEach(pt => {
        if (pt === 'val' && !nv) return;
        shown.push(pt);
        fr.push({ items: final.map(x => ({ ...x, part: shown.includes(x.part) ? x.part : 'all' })), say: `Cut off the <b>${names[pt]}</b>: ${count(pt)} examples, with ${rcount(pt)} rare ones (${count(pt) ? f2(rcount(pt) / count(pt) * 100, 0) : 0}%). ${why[pt]}` });
      });
      const sh2 = order.filter(pt => count(pt)).map(pt => `${names[pt]} ${count(pt) ? f2(rcount(pt) / count(pt) * 100, 0) : 0}%`).join(', ');
      fr.push({ items: final, done: true, say: `Done. Rare share in each part: ${sh2}, against ${f2(nr / n * 100, 0)}% overall. ${p.strat ? 'With stratifying the shares match, so every score we measure is fair.' : 'Without stratifying the shares can drift apart by luck, especially with few examples. Tick Stratify to fix that.'}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      const col = { all: c.surf, train: c.cv, val: c.teal || '#0d9488', test: c.ink2 };
      const groups = { all: [], train: [], val: [], test: [] };
      f.items.forEach(x => groups[x.part].push(x));
      const rows = [['all', 'not split yet'], ['train', 'train'], ['val', 'validation'], ['test', 'test']];
      let y = 16;
      rows.forEach(([k, lbl]) => {
        if (!groups[k].length) return;
        head(z, `${lbl} (${groups[k].length})`, 16, y + 12);
        groups[k].forEach((x, i) => {
          const xx = 130 + (i % 30) * 15, yy = y + Math.floor(i / 30) * 16;
          rr(z.g, xx, yy, 12, 12, 2, { fill: x.rare ? c.orange : col[k], stroke: k === 'all' ? c.line : col[k], w: 1 });
        });
        y += Math.ceil(groups[k].length / 30) * 16 + 24;
      });
      D.text(z.g, 'orange = rare class', 584, 320, { a: 'right', s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Foundations 1.3  NumPy broadcasting: how two shapes line up
   ===================================================================================================== */
(() => {
  const { trace, box, head, D, nums } = MLZ;
  trace('mlbroadcast', {
    title: 'NumPy broadcasting, step by step',
    sub: 'Type two array shapes. NumPy lines them up from the right and checks each pair of sizes. A size of 1 is stretched to match.',
    W: 600, H: 300,
    params: [
      { k: 'a', label: 'Shape of A', type: 'text', v: '4, 3' },
      { k: 'b', label: 'Shape of B', type: 'text', v: '3' }
    ],
    tips: [
      { t: 'A (4, 3) plus B (3): a row of 3 numbers is added to every one of the 4 rows. This is how you subtract the column means from a data table.', set: { a: '4, 3', b: '3' }, play: true },
      { t: 'A (4, 1) and B (1, 3) give a (4, 3) table: every pair of a row value and a column value.', set: { a: '4, 1', b: '1, 3' }, play: true },
      { t: 'A (4, 3) and B (4): the last sizes 3 and 4 differ and neither is 1, so NumPy raises an error. Reshape B to (4, 1) to fix it.', set: { a: '4, 3', b: '4' }, play: true }
    ],
    frames(p) {
      const A = nums(p.a).map(Math.round), B = nums(p.b).map(Math.round);
      if (!A.length || !B.length || A.concat(B).some(v => v < 1 || v > 99)) throw new Error('Type shapes such as 4, 3 with sizes from 1 to 99.');
      const L = Math.max(A.length, B.length);
      const pa = Array(L - A.length).fill(null).concat(A), pb = Array(L - B.length).fill(null).concat(B);
      const fr = [];
      fr.push({ pa, pb, k: -1, res: [], say: `A has shape (${A.join(', ')}) and B has shape (${B.join(', ')}). NumPy compares the shapes starting from the <b>right</b> end, one size at a time.` });
      if (A.length !== B.length) fr.push({ pa, pb, k: -1, res: [], pad: true, say: `The shapes have different lengths, so NumPy pretends the shorter one has extra sizes of 1 on the left. They are shown as 1 in grey.` });
      const res = Array(L).fill(null);
      let bad = false;
      for (let i = L - 1; i >= 0; i--) {
        const x = pa[i] ?? 1, y = pb[i] ?? 1;
        let say, r;
        if (x === y) { r = x; say = `Position ${L - i} from the right: ${x} and ${y} are equal, so this size is <b>${r}</b>.`; }
        else if (x === 1) { r = y; say = `Position ${L - i} from the right: A has 1 and B has ${y}. A is <b>stretched</b> (copied) ${y} times along this axis. Result size ${r}.`; }
        else if (y === 1) { r = x; say = `Position ${L - i} from the right: B has 1 and A has ${x}. B is <b>stretched</b> ${x} times. Result size ${r}.`; }
        else { bad = true; say = `Position ${L - i} from the right: ${x} and ${y} are different and neither is 1. NumPy stops with <b>ValueError: operands could not be broadcast together</b>.`; }
        res[i] = bad ? '✗' : r;
        fr.push({ pa, pb, k: i, res: res.slice(), bad, say });
        if (bad) break;
      }
      if (!bad) fr.push({ pa, pb, k: -1, res, done: true, say: `Every pair matched, so A and B can be combined element by element. The result has shape <b>(${res.join(', ')})</b>. NumPy never really copies the data, it just reuses the same numbers, so broadcasting is fast and saves memory.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, L = f.pa.length, cw = 70, x0 = 300 - L * cw / 2;
      const row = (lbl, arr, y, isRes) => {
        head(z, lbl, x0 - 14, y + 26, { a: 'right', s: 13 });
        arr.forEach((v, i) => {
          const on = i === f.k;
          const ghost = v === null;
          box(z, x0 + i * cw, y, cw - 8, 40, ghost ? (f.pad ? '1' : '') : String(v), { fill: on ? c.cv : (isRes && v === '✗' ? c.red : c.surf), c: on || (isRes && v === '✗') ? '#fff' : (ghost ? c.ink2 : c.ink), b: true, s: 16, mono: true, dash: ghost ? [4, 3] : null });
        });
      };
      row('A', f.pa, 40, false);
      row('B', f.pb, 110, false);
      if (f.res.some(v => v !== null)) row('result', f.res.map(v => v), 200, true);
      D.text(z.g, '← NumPy compares from the right', 300 + L * cw / 2 - 8, 26, { a: 'right', s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Foundations 1.3  pandas groupby: split, apply, combine
   ===================================================================================================== */
(() => {
  const { trace, head, D, rr, klass, f2, fit } = MLZ;
  trace('mlgroupby', {
    title: 'pandas groupby: split, apply, combine',
    sub: 'Type a small table of (group, value) rows. groupby splits the rows by group, applies a function to each pile, and combines the answers into a new table.',
    W: 600, H: 330,
    params: [
      { k: 'rows', label: 'Rows: group value', type: 'area', v: 'Pune 31\nDelhi 38\nPune 29\nChennai 34\nDelhi 41\nChennai 33\nPune 30' },
      { k: 'fn', label: 'Function to apply', type: 'select', v: 'mean', opts: [['mean', 'mean()'], ['sum', 'sum()'], ['max', 'max()'], ['count', 'count()']] }
    ],
    tips: [{ t: 'Change the function to count(). It tells how many rows each group has, a quick way to spot rare groups.', set: { fn: 'count' }, play: true }],
    frames(p) {
      const rows = String(p.rows).split(/\n+/).map(l => l.trim()).filter(Boolean).map(l => { const t = l.split(/[\s,]+/); const v = +t[t.length - 1]; if (isNaN(v) || t.length < 2) throw new Error('Each row needs a group name and a number.'); return { g: t.slice(0, -1).join(' '), v }; });
      if (rows.length > 12) throw new Error('Use at most 12 rows.');
      const groups = [];
      rows.forEach(r => { if (!groups.includes(r.g)) groups.push(r.g); });
      groups.sort();
      const F = { mean: a => a.reduce((s, x) => s + x, 0) / a.length, sum: a => a.reduce((s, x) => s + x, 0), max: a => Math.max(...a), count: a => a.length };
      const fr = [];
      fr.push({ rows, stage: 0, say: `This is the table with ${rows.length} rows. We want one answer per group: df.groupby("group")["value"].${p.fn}().` });
      fr.push({ rows, groups, stage: 1, say: `<b>Split</b>: pandas puts the rows into ${groups.length} piles, one per group (${groups.join(', ')}). Groups come out sorted by name.` });
      const out = [];
      groups.forEach((g, i) => {
        const vals = rows.filter(r => r.g === g).map(r => r.v);
        out.push({ g, v: F[p.fn](vals) });
        fr.push({ rows, groups, stage: 2, upto: i, out: out.slice(), say: `<b>Apply</b> to ${g}: values ${vals.join(', ')} give ${p.fn}() = <b>${f2(F[p.fn](vals), p.fn === 'mean' ? 2 : 0)}</b>.` });
      });
      fr.push({ rows, groups, stage: 3, out, done: true, say: `<b>Combine</b>: the answers form a new, smaller table indexed by group. In ML we use this to make features such as "average temperature of the customer’s city".` });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      head(z, 'Table', 16, 18);
      f.rows.forEach((r, i) => {
        const gi = f.groups ? f.groups.indexOf(r.g) : -1;
        rr(z.g, 16, 26 + i * 22, 150, 19, 4, { fill: gi >= 0 ? klass(z, gi) : c.surf, stroke: c.line });
        D.text(z.g, r.g, 22, 40 + i * 22, { s: 12, b: true, c: gi >= 0 ? '#fff' : c.ink });
        D.text(z.g, String(r.v), 160, 40 + i * 22, { a: 'right', s: 12, mono: true, c: gi >= 0 ? '#fff' : c.ink });
      });
      if (f.stage >= 1) {
        head(z, 'Split into piles', 200, 18);
        f.groups.forEach((g, gi) => {
          const vals = f.rows.filter(r => r.g === g).map(r => r.v);
          const y = 26 + gi * 56;
          rr(z.g, 200, y, 200, 48, 6, { fill: c.surf, stroke: klass(z, gi), w: 2 });
          const s = fit(z.g, g, 80, 12, { b: true });
          D.text(z.g, g, 208, y + 18, { s, b: true, c: klass(z, gi) });
          D.text(z.g, vals.join('  '), 208, y + 38, { s: 12, mono: true, c: c.ink });
          if (f.out && f.out[gi]) D.arrow(z.g, 402, y + 24, 430, y + 24, c.ink2, 1.5);
        });
      }
      if (f.out) {
        head(z, 'Combined result', 440, 18);
        f.out.forEach((o, gi) => {
          const y = 26 + gi * 56;
          rr(z.g, 440, y + 8, 145, 32, 6, { fill: f.done ? c.cv : c.bg, stroke: c.line });
          D.text(z.g, `${o.g}: ${f2(o.v, Number.isInteger(o.v) ? 0 : 2)}`, 512, y + 29, { a: 'center', s: 12, b: true, c: f.done ? '#fff' : c.ink });
        });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 2.1  distance between two examples: Euclidean, Manhattan and cosine
   ===================================================================================================== */
(() => {
  const { trace, box, head, plot, D, f2, nums } = MLZ;
  trace('mldist', {
    title: 'How far apart are two examples?',
    sub: 'Each example is a point (a vector). Pick a way to measure distance and watch it being worked out piece by piece.',
    W: 600, H: 330,
    params: [
      { k: 'a', label: 'Point A (x, y)', type: 'text', v: '1, 2' },
      { k: 'b', label: 'Point B (x, y)', type: 'text', v: '4, 6' },
      { k: 'm', label: 'Distance', type: 'select', v: 'euc', opts: [['euc', 'Euclidean (straight line, L2)'], ['man', 'Manhattan (city blocks, L1)'], ['cos', 'Cosine (angle between the arrows)']] }
    ],
    tips: [
      { t: 'Manhattan distance walks along the grid like a taxi in a city. It is always at least as long as the straight line.', set: { m: 'man' }, play: true },
      { t: 'Cosine: set B to 2, 4, which points the same way as A = 1, 2 but is twice as long. Cosine distance is 0 because only the direction matters. Text search uses this.', set: { m: 'cos', b: '2, 4' }, play: true }
    ],
    frames(p) {
      const A = nums(p.a), B = nums(p.b);
      if (A.length !== 2 || B.length !== 2) throw new Error('Each point needs exactly two numbers, such as 1, 2.');
      const dx = B[0] - A[0], dy = B[1] - A[1];
      const fr = [];
      fr.push({ A, B, s: 0, say: `Point A is (${A.join(', ')}) and point B is (${B.join(', ')}). In ML each example is a list of feature values, so it is a point in space. Similar examples are close together.` });
      if (p.m === 'euc') {
        fr.push({ A, B, s: 1, say: `Find the gap on each axis: across ${B[0]} − ${A[0]} = <b>${f2(dx)}</b>, up ${B[1]} − ${A[1]} = <b>${f2(dy)}</b>.` });
        fr.push({ A, B, s: 2, say: `Square each gap so the sign does not matter: ${f2(dx)}² = ${f2(dx * dx)} and ${f2(dy)}² = ${f2(dy * dy)}. Add them: ${f2(dx * dx + dy * dy)}.` });
        fr.push({ A, B, s: 3, done: true, say: `Take the square root: √${f2(dx * dx + dy * dy)} = <b>${f2(Math.hypot(dx, dy))}</b>. This is Pythagoras, the straight line length. With more features you just add more squared gaps. k nearest neighbours and k means use it.` });
      } else if (p.m === 'man') {
        fr.push({ A, B, s: 1, say: `Gap across: |${f2(dx)}| = ${f2(Math.abs(dx))}. Gap up: |${f2(dy)}| = ${f2(Math.abs(dy))}. We use the size of each gap, ignoring the sign.` });
        fr.push({ A, B, s: 4, done: true, say: `Add them: ${f2(Math.abs(dx))} + ${f2(Math.abs(dy))} = <b>${f2(Math.abs(dx) + Math.abs(dy))}</b>. Like a taxi that can only drive along the streets of a grid city. It is less affected by one huge gap than Euclidean distance.` });
      } else {
        const dot = A[0] * B[0] + A[1] * B[1], na = Math.hypot(...A), nb = Math.hypot(...B);
        if (!na || !nb) throw new Error('Cosine needs points that are not at (0, 0).');
        const cs = dot / (na * nb);
        fr.push({ A, B, s: 5, say: `Dot product A · B = ${A[0]}×${B[0]} + ${A[1]}×${B[1]} = <b>${f2(dot)}</b>.` });
        fr.push({ A, B, s: 5, say: `Lengths: |A| = √(${A[0]}² + ${A[1]}²) = ${f2(na)} and |B| = ${f2(nb)}.` });
        fr.push({ A, B, s: 6, done: true, say: `Cosine similarity = ${f2(dot)} / (${f2(na)} × ${f2(nb)}) = <b>${f2(cs, 3)}</b>, an angle of about ${f2(Math.acos(Math.max(-1, Math.min(1, cs))) * 180 / Math.PI, 0)} degrees. Cosine distance = 1 − similarity = <b>${f2(1 - cs, 3)}</b>. Only the direction counts, not the length.` });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, A = f.A, B = f.B;
      const xs = [0, A[0], B[0]], ys = [0, A[1], B[1]];
      const lo = Math.min(...xs, ...ys) - 1, hi = Math.max(...xs, ...ys) + 1;
      const P = plot(z, [10, 10, 330, 310], [lo, hi], [lo, hi], { dx: 0, dy: 0 });
      if (f.s >= 5) { D.arrow(z.g, P.X(0), P.Y(0), P.X(A[0]), P.Y(A[1]), c.cv, 2.5); D.arrow(z.g, P.X(0), P.Y(0), P.X(B[0]), P.Y(B[1]), c.orange, 2.5); }
      if (f.s === 1 || f.s === 2 || f.s === 4) {
        D.line(z.g, P.X(A[0]), P.Y(A[1]), P.X(B[0]), P.Y(A[1]), c.green, 2.5);
        D.line(z.g, P.X(B[0]), P.Y(A[1]), P.X(B[0]), P.Y(B[1]), c.green, 2.5);
      }
      if (f.s === 2 || f.s === 3) D.line(z.g, P.X(A[0]), P.Y(A[1]), P.X(B[0]), P.Y(B[1]), c.red, 2.5, f.s === 2 ? [5, 4] : null);
      D.circle(z.g, P.X(A[0]), P.Y(A[1]), 6, { fill: c.cv });
      D.circle(z.g, P.X(B[0]), P.Y(B[1]), 6, { fill: c.orange });
      D.text(z.g, 'A', P.X(A[0]) + 8, P.Y(A[1]) - 6, { s: 13, b: true, c: c.cv });
      D.text(z.g, 'B', P.X(B[0]) + 8, P.Y(B[1]) - 6, { s: 13, b: true, c: c.orange });
      head(z, 'Formulas', 360, 30);
      const rows = [['Euclidean (L2)', '√(Σ (aᵢ − bᵢ)²)'], ['Manhattan (L1)', 'Σ |aᵢ − bᵢ|'], ['Cosine similarity', 'A·B / (|A| |B|)']];
      const which = { euc: 0, man: 1, cos: 2 }[z.p.m];
      rows.forEach((r, i) => box(z, 360, 44 + i * 58, 228, 48, `${r[0]}:  ${r[1]}`, { fill: i === which ? c.cv : c.surf, c: i === which ? '#fff' : c.ink, s: 12, b: i === which }));
      if (f.done) D.text(z.g, 'Done', 588, 236, { a: 'right', s: 13, b: true, c: c.green });
    }
  });
})();

/* =====================================================================================================
   Foundations 2.1  a matrix times a vector, row by row, and what it does to the plane
   ===================================================================================================== */
(() => {
  const { trace, box, head, plot, D, f2, nums, grid } = MLZ;
  trace('mlmatvec', {
    title: 'A matrix times a vector: one dot product per row',
    sub: 'Type a 2 × 2 matrix and a vector. Each row of the matrix gives one number of the answer. At the end you see what the matrix does to every point: it stretches, turns or flips the plane.',
    W: 600, H: 330,
    params: [
      { k: 'm', label: 'Matrix rows (a b, c d)', type: 'text', v: '2 1, 0 1' },
      { k: 'v', label: 'Vector (x, y)', type: 'text', v: '1, 2' }
    ],
    tips: [
      { t: 'Matrix 0 -1, 1 0 turns every point a quarter turn (90 degrees) to the left.', set: { m: '0 -1, 1 0' }, play: true },
      { t: 'Matrix 2 0, 0 0.5 stretches across and squashes up. Scaling features does the same to the data cloud.', set: { m: '2 0, 0 0.5' }, play: true }
    ],
    frames(p) {
      const r = String(p.m).split(',').map(s => nums(s));
      if (r.length !== 2 || r.some(x => x.length !== 2)) throw new Error('Type two rows of two numbers, for example 2 1, 0 1.');
      const v = nums(p.v);
      if (v.length !== 2) throw new Error('The vector needs two numbers.');
      const out = [r[0][0] * v[0] + r[0][1] * v[1], r[1][0] * v[0] + r[1][1] * v[1]];
      const det = r[0][0] * r[1][1] - r[0][1] * r[1][0];
      return [
        { r, v, s: 0, say: `We want M × v, where M = [[${r[0].join(', ')}], [${r[1].join(', ')}]] and v = (${v.join(', ')}). The answer is a new vector with one number per row of M.` },
        { r, v, s: 1, out, say: `Row 1 · v = ${r[0][0]}×${v[0]} + ${r[0][1]}×${v[1]} = <b>${f2(out[0])}</b>. This is the first number of the answer.` },
        { r, v, s: 2, out, say: `Row 2 · v = ${r[1][0]}×${v[0]} + ${r[1][1]}×${v[1]} = <b>${f2(out[1])}</b>. So M × v = (${f2(out[0])}, ${f2(out[1])}). A linear model with many outputs does exactly this, one row of weights per output.` },
        { r, v, s: 3, out, det, done: true, say: `The picture shows the effect on the whole plane: the grey unit square becomes the orange shape. Its area is multiplied by the <b>determinant</b> ad − bc = ${f2(det)}. ${det === 0 ? 'A determinant of 0 squashes the plane onto a line, so the matrix has no inverse.' : det < 0 ? 'A negative determinant also flips the plane like a mirror.' : 'Every point moves the same way, which is why it is called a linear transformation.'}` }
      ];
    },
    paint(z, f) {
      const c = z.col, r = f.r, v = f.v;
      grid(z, [[r[0][0], r[0][1]], [r[1][0], r[1][1]]].map(x => x.map(y => f2(y, Number.isInteger(y) ? 0 : 2))), 20, 40, 46, 36, { hl: (i) => (f.s === 1 && i === 0) || (f.s === 2 && i === 1), mono: true, s: 14 });
      D.text(z.g, '×', 120, 82, { s: 20, b: true, c: c.ink });
      grid(z, [[v[0]], [v[1]]], 140, 40, 46, 36, { mono: true, s: 14 });
      if (f.out) {
        D.text(z.g, '=', 200, 82, { s: 20, b: true, c: c.ink });
        grid(z, [[f2(f.out[0])], [f.s >= 2 ? f2(f.out[1]) : '?']], 222, 40, 60, 36, { hl: (i) => i === f.s - 1, mono: true, s: 14 });
      }
      head(z, 'M (matrix)', 20, 30); head(z, 'v', 140, 30); if (f.out) head(z, 'M v', 222, 30);
      const pts = [[0, 0], [1, 0], [1, 1], [0, 1]];
      const T = q => [r[0][0] * q[0] + r[0][1] * q[1], r[1][0] * q[0] + r[1][1] * q[1]];
      const all = pts.concat(pts.map(T), [v, f.out || v]);
      const ext = Math.max(2, ...all.map(q => Math.max(Math.abs(q[0]), Math.abs(q[1])))) + 0.5;
      const P = plot(z, [310, 10, 280, 310], [-ext, ext], [-ext, ext], { dx: 0, dy: 0 });
      D.line(z.g, P.X(-ext), P.Y(0), P.X(ext), P.Y(0), c.ink2, 1);
      D.line(z.g, P.X(0), P.Y(-ext), P.X(0), P.Y(ext), c.ink2, 1);
      const poly = (qs, col, fill) => { const g = z.g; g.save(); g.beginPath(); qs.forEach((q, i) => i ? g.lineTo(P.X(q[0]), P.Y(q[1])) : g.moveTo(P.X(q[0]), P.Y(q[1]))); g.closePath(); g.globalAlpha = 0.25; g.fillStyle = fill; g.fill(); g.globalAlpha = 1; g.strokeStyle = col; g.lineWidth = 2; g.stroke(); g.restore(); };
      poly(pts, c.ink2, c.ink2);
      if (f.s >= 3) poly(pts.map(T), c.orange, c.orange);
      D.arrow(z.g, P.X(0), P.Y(0), P.X(v[0]), P.Y(v[1]), c.cv, 2.5);
      if (f.out && f.s >= 2) D.arrow(z.g, P.X(0), P.Y(0), P.X(f.out[0]), P.Y(f.out[1]), c.green, 2.5);
      D.text(z.g, 'purple: v   green: M v', 318, 312, { s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Foundations 2.2  the derivative as the limit of a slope
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head } = MLZ;
  const FN = {
    sq: { name: 'f(x) = x²', f: x => x * x, d: x => 2 * x, dn: '2x' },
    cube: { name: 'f(x) = x³ − 3x', f: x => x ** 3 - 3 * x, d: x => 3 * x * x - 3, dn: '3x² − 3' },
    sig: { name: 'f(x) = sigmoid(x) = 1 / (1 + e^(−x))', f: x => 1 / (1 + Math.exp(-x)), d: x => { const s = 1 / (1 + Math.exp(-x)); return s * (1 - s); }, dn: 'σ(x)(1 − σ(x))' }
  };
  trace('mlslope', {
    title: 'What a derivative is: the slope at one point',
    sub: 'Pick a function and a point. We draw a line through two points on the curve and slide the second point closer. The slope of that line settles on the derivative.',
    W: 600, H: 330,
    params: [
      { k: 'fn', label: 'Function', type: 'select', v: 'sq', opts: Object.keys(FN).map(k => [k, FN[k].name]) },
      { k: 'x0', label: 'Point x', type: 'range', v: 1, min: -2, max: 2, step: 0.5 }
    ],
    tips: [
      { t: 'Try the sigmoid at x = 0. The slope settles on 0.25, the largest slope a sigmoid ever has.', set: { fn: 'sig', x0: 0 }, play: true },
      { t: 'Try x³ − 3x at x = 1. The slope goes to 0: the curve is flat there, a bottom of a valley.', set: { fn: 'cube', x0: 1 }, play: true }
    ],
    frames(p) {
      const F = FN[p.fn], x = p.x0;
      const fr = [{ h: null, say: `The curve is ${F.name}. We want its slope at x = ${x}, where f(x) = ${f2(F.f(x), 3)}. A curve has no single slope, so we zoom in.` }];
      [2, 1, 0.5, 0.1, 0.01].forEach(h => {
        const s = (F.f(x + h) - F.f(x)) / h;
        fr.push({ h, say: `Take a second point h = ${h} to the right. Slope of the line through both points = (f(${f2(x + h, 2)}) − f(${x})) / ${h} = <b>${f2(s, 4)}</b>.` });
      });
      fr.push({ h: 0, done: true, say: `As h shrinks to 0 the slope settles on <b>${f2(F.d(x), 4)}</b>. That limit is the <b>derivative</b>, written f′(x) = ${F.dn}. It says how fast f changes when x moves a tiny bit. Gradient descent uses it to know which way is downhill.` });
      return fr;
    },
    paint(z, f) {
      const F = FN[z.p.fn], c = z.col, x = z.p.x0;
      const xs = [], ys = [];
      for (let t = -3; t <= 3.0001; t += 0.05) { xs.push(t); ys.push(F.f(t)); }
      const lo = Math.min(...ys), hi = Math.max(...ys);
      const P = plot(z, [10, 10, 400, 310], [-3, 3], [lo - 0.1 * (hi - lo), hi + 0.1 * (hi - lo)], { dx: 0, dy: 1 });
      z.g.save(); z.g.beginPath(); xs.forEach((t, i) => i ? z.g.lineTo(P.X(t), P.Y(ys[i])) : z.g.moveTo(P.X(t), P.Y(ys[i]))); z.g.strokeStyle = c.cv; z.g.lineWidth = 2.5; z.g.stroke(); z.g.restore();
      const clipLine = (s, col, dash) => { const g = z.g; g.save(); g.beginPath(); g.rect(P.x0, P.y0, P.w, P.h); g.clip(); D.line(g, P.X(-3), P.Y(F.f(x) + s * (-3 - x)), P.X(3), P.Y(F.f(x) + s * (3 - x)), col, 2, dash); g.restore(); };
      if (f.h) { const s = (F.f(x + f.h) - F.f(x)) / f.h; clipLine(s, c.orange, [6, 4]); D.circle(z.g, P.X(x + f.h), P.Y(F.f(x + f.h)), 5, { fill: c.orange }); }
      if (f.done) clipLine(F.d(x), c.green);
      D.circle(z.g, P.X(x), P.Y(F.f(x)), 6, { fill: c.red });
      head(z, 'Slope of the line', 425, 30);
      D.text(z.g, f.h === null ? '?' : f2(f.done ? F.d(x) : (F.f(x + f.h) - F.f(x)) / f.h, 4), 425, 66, { s: 24, b: true, c: f.done ? c.green : c.orange, mono: true });
      if (f.h) D.text(z.g, `h = ${f.h}`, 425, 96, { s: 14, mono: true, c: c.ink });
      if (f.done) D.text(z.g, `f′(x) = ${F.dn}`, 425, 96, { s: 13, mono: true, c: c.green, b: true });
    }
  });
})();

/* =====================================================================================================
   Foundations 2.2  gradient descent rolling down a curve
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rr } = MLZ;
  const FN = {
    bowl: { name: 'f(x) = (x − 2)²  (one valley)', f: x => (x - 2) ** 2, d: x => 2 * (x - 2), r: [-3, 6] },
    two: { name: 'f(x) = x⁴ − 3x² + x  (two valleys)', f: x => x ** 4 - 3 * x * x + x, d: x => 4 * x ** 3 - 6 * x + 1, r: [-2.2, 2.2] }
  };
  trace('mlgd', {
    title: 'Gradient descent: walk downhill one step at a time',
    sub: 'The ball starts at x and moves against the slope. The learning rate sets how big each step is. Try different starts and rates.',
    W: 600, H: 330,
    params: [
      { k: 'fn', label: 'Loss curve', type: 'select', v: 'bowl', opts: Object.keys(FN).map(k => [k, FN[k].name]) },
      { k: 'x0', label: 'Start x', type: 'range', v: -2, min: -2, max: 5, step: 0.5 },
      { k: 'lr', label: 'Learning rate', type: 'range', v: 0.2, min: 0.02, max: 1.1, step: 0.02 },
      { k: 'n', label: 'Steps', type: 'range', v: 8, min: 3, max: 20 }
    ],
    tips: [
      { t: 'Learning rate 0.9 on the bowl: the ball jumps from side to side but still settles. At 1.02 it flies away (diverges).', set: { fn: 'bowl', lr: 0.9 }, play: true },
      { t: 'Learning rate 0.04: tiny safe steps, but after 8 steps it is still far from the bottom.', set: { fn: 'bowl', lr: 0.04 }, play: true },
      { t: 'Two valleys, start at 1.5 with rate 0.05: the ball stops in the right valley, which is not the deepest one. That is a local minimum.', set: { fn: 'two', x0: 1.5, lr: 0.05, n: 15 }, play: true }
    ],
    frames(p) {
      const F = FN[p.fn];
      let x = Math.max(F.r[0], Math.min(F.r[1], p.x0));
      const path = [x];
      const fr = [{ path: path.slice(), say: `Start at x = ${f2(x)}, where the loss is ${f2(F.f(x), 3)}. The goal is the lowest point of the curve.` }];
      for (let i = 1; i <= p.n; i++) {
        const g = F.d(x), nx = x - p.lr * g;
        const far = !isFinite(nx) || Math.abs(nx) > 50;
        fr.push({ path: path.concat([nx]), say: `Step ${i}: slope at ${f2(x)} is ${f2(g, 3)}. New x = ${f2(x)} − ${f2(p.lr)} × (${f2(g, 3)}) = <b>${f2(nx, 3)}</b>${far ? '. The steps keep growing: the learning rate is too big, so it diverges.' : `, loss ${f2(F.f(nx), 4)}.`}` });
        if (far) return fr;
        x = nx; path.push(x);
      }
      fr.push({ path, done: true, say: `After ${p.n} steps x = ${f2(x, 3)} with slope ${f2(F.d(x), 3)}. ${Math.abs(F.d(x)) < 0.05 ? 'The slope is almost 0, so we are at the bottom of a valley.' : 'The slope is not yet 0, so more steps (or a bigger rate) are needed.'} Real models do the same with millions of weights at once.` });
      return fr;
    },
    paint(z, f) {
      const F = FN[z.p.fn], c = z.col;
      const xs = [], ys = [];
      for (let t = F.r[0]; t <= F.r[1] + 1e-9; t += (F.r[1] - F.r[0]) / 120) { xs.push(t); ys.push(F.f(t)); }
      const P = plot(z, [10, 10, 400, 310], F.r, [Math.min(...ys) - 0.5, Math.max(...ys)], { dx: 1, dy: 0 });
      z.g.save(); z.g.beginPath(); xs.forEach((t, i) => i ? z.g.lineTo(P.X(t), P.Y(ys[i])) : z.g.moveTo(P.X(t), P.Y(ys[i]))); z.g.strokeStyle = c.cv; z.g.lineWidth = 2.5; z.g.stroke(); z.g.restore();
      const inR = x => x >= F.r[0] && x <= F.r[1];
      f.path.forEach((x, i) => {
        if (i && inR(x) && inR(f.path[i - 1])) D.arrow(z.g, P.X(f.path[i - 1]), P.Y(F.f(f.path[i - 1])), P.X(x), P.Y(F.f(x)), c.orange, 1.5, 6);
      });
      f.path.forEach((x, i) => { if (inR(x)) D.circle(z.g, P.X(x), P.Y(F.f(x)), i === f.path.length - 1 ? 7 : 3.5, { fill: i === f.path.length - 1 ? c.red : c.orange }); });
      head(z, 'Loss at each step', 425, 26);
      const L = f.path.map(x => F.f(x)).filter(isFinite);
      const max = Math.max(...L.map(Math.abs), 1e-9);
      const bw = Math.min(16, 160 / L.length);
      L.forEach((v, i) => { const h = Math.max(2, Math.min(240, Math.abs(v) / max * 240)); rr(z.g, 428 + i * (bw + 2), 290 - h, bw, h, 2, { fill: i === L.length - 1 ? c.red : c.cv }); });
      D.text(z.g, `x = ${f2(f.path[f.path.length - 1], 3)}`, 425, 310, { s: 12, mono: true, c: c.ink });
    }
  });
})();

/* =====================================================================================================
   Foundations 2.3  Bayes rule with a crowd of people (a medical test)
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, rng, box } = MLZ;
  const N = 400;
  trace('mlbayes', {
    title: 'Bayes rule: what does a positive test really mean?',
    sub: 'Picture 400 people. Some have a disease. A test catches most sick people but also wrongly flags some healthy ones. Step through to count who is really sick among the positives.',
    W: 600, H: 330,
    params: [
      { k: 'prev', label: 'People who are sick (%)', type: 'range', v: 2, min: 1, max: 50, step: 1 },
      { k: 'sens', label: 'Test finds sick people (%)', type: 'range', v: 90, min: 50, max: 100, step: 1 },
      { k: 'fpr', label: 'Test wrongly flags healthy people (%)', type: 'range', v: 5, min: 0, max: 30, step: 1 }
    ],
    tips: [
      { t: 'A rare disease (1%) with a very good test (99% and 1%): still only about half of the positives are sick.', set: { prev: 1, sens: 99, fpr: 1 }, play: true },
      { t: 'A common disease (30%): now a positive test is very convincing. The prior matters a lot.', set: { prev: 30, sens: 90, fpr: 5 }, play: true }
    ],
    frames(p) {
      const sick = Math.round(N * p.prev / 100), well = N - sick;
      const tp = Math.round(sick * p.sens / 100), fp = Math.round(well * p.fpr / 100);
      const exact = (p.sens / 100) * (p.prev / 100) / ((p.sens / 100) * (p.prev / 100) + (p.fpr / 100) * (1 - p.prev / 100) || 1);
      const c = { sick, well, tp, fp };
      return [
        { s: 1, ...c, say: `Here are ${N} people. Before any test, we only know that ${p.prev}% of people are sick. This starting belief is called the <b>prior</b>, P(sick) = ${f2(p.prev / 100)}.` },
        { s: 2, ...c, say: `Colour the sick people red: ${N} × ${p.prev}% = <b>${sick}</b> people. The other ${well} are healthy (grey).` },
        { s: 3, ...c, say: `Everyone takes the test. It finds ${p.sens}% of the sick people, so <b>${tp}</b> of the ${sick} sick people test positive (red with a dark ring). These are <b>true positives</b>.` },
        { s: 4, ...c, say: `The test also wrongly says yes for ${p.fpr}% of the ${well} healthy people: <b>${fp}</b> grey people with a ring. These are <b>false positives</b>.` },
        { s: 5, ...c, say: `Your test is positive, so you are one of the ringed people. Fade everyone else. There are ${tp} + ${fp} = <b>${tp + fp}</b> positives in total.` },
        { s: 6, ...c, say: `Chance you are sick, given a positive test = sick positives ÷ all positives = ${tp} ÷ ${tp + fp} = <b>${tp + fp ? f2(tp / (tp + fp), 3) : '0'}</b>. Bayes rule gives the exact value P(sick | +) = P(+ | sick) P(sick) ÷ P(+) = <b>${f2(exact, 3)}</b>. This updated belief is the <b>posterior</b>.${Math.abs((tp + fp ? tp / (tp + fp) : 0) - exact) > 0.0005 ? ' The small gap between the two numbers comes from rounding to whole people.' : ''}` }
      ];
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const r = rng(7);
      const order = Array.from({ length: N }, (_, i) => i);
      for (let i = N - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
      /* person k (in the shuffled order) is sick if k < sick, a true positive if k < tp,
         and a false positive if sick <= k < sick + fp */
      const where = new Array(N);
      order.forEach((pos, k) => { where[pos] = k; });
      const cell = 15.5, x0 = 14, y0 = 12;
      for (let pos = 0; pos < N; pos++) {
        const k = where[pos], col = pos % 20, row = Math.floor(pos / 20);
        const x = x0 + col * cell + cell / 2, y = y0 + row * cell + cell / 2;
        const isSick = f.s >= 2 && k < f.sick;
        const pos1 = (f.s >= 3 && k < f.tp) || (f.s >= 4 && k >= f.sick && k < f.sick + f.fp);
        const fade = f.s >= 5 && !pos1;
        g.save(); g.globalAlpha = fade ? 0.15 : 1;
        D.circle(g, x, y, 5, { fill: isSick ? c.red : c.ink2 });
        if (pos1) D.circle(g, x, y, 7, { stroke: c.ink, w: 1.6 });
        g.restore();
      }
      const bx = 340;
      head(z, 'Counts', bx, 26);
      const rows = [['People', N, 1], ['Sick (red)', f.sick, 2], ['Healthy (grey)', f.well, 2], ['True positives', f.tp, 3], ['False positives', f.fp, 4], ['All positives', f.tp + f.fp, 5]];
      rows.forEach(([t, v, s], i) => {
        if (f.s < s) return;
        D.text(g, t, bx, 54 + i * 26, { s: 13, c: c.ink });
        D.text(g, String(v), bx + 240, 54 + i * 26, { s: 14, b: true, mono: true, a: 'right', c: c.ink });
      });
      if (f.s >= 6) {
        box(z, bx, 220, 245, 70, '', { fill: c.bg });
        D.text(g, 'P(sick | positive)', bx + 12, 244, { s: 13, b: true, c: c.ink2 });
        D.text(g, `${f.tp} ÷ ${f.tp + f.fp} = ${f.tp + f.fp ? f2(f.tp / (f.tp + f.fp), 3) : '0'}`, bx + 12, 274, { s: 18, b: true, mono: true, c: c.cv });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 2.3  the central limit theorem: averages become bell shaped
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rng, rr } = MLZ;
  const SRC = {
    die: { name: 'A fair die (flat: 1 to 6)', vals: [1, 2, 3, 4, 5, 6], w: [1, 1, 1, 1, 1, 1] },
    wait: { name: 'Waiting time in minutes (skewed)', vals: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], w: [30, 22, 15, 10, 8, 6, 4, 2, 2, 1] },
    coin: { name: 'A coin that lands heads 20% of the time (0 or 1)', vals: [0, 1], w: [8, 2] }
  };
  const SIZES = [1, 2, 5, 10, 30];
  trace('mlclt', {
    title: 'Central limit theorem: averages turn into a bell curve',
    sub: 'Take n values from any distribution and average them. Do that 2,000 times and draw a histogram of the averages. As n grows the histogram gets narrower and bell shaped.',
    W: 600, H: 330,
    params: [{ k: 'src', label: 'Where the values come from', type: 'select', v: 'wait', opts: Object.keys(SRC).map(k => [k, SRC[k].name]) }],
    tips: [
      { t: 'Even the 0 or 1 coin gives a bell curve once you average 30 flips.', set: { src: 'coin' }, play: true },
      { t: 'The die starts flat, not bell shaped at all.', set: { src: 'die' }, play: true }
    ],
    frames(p) {
      const S = SRC[p.src], tot = S.w.reduce((a, b) => a + b, 0);
      const pr = S.w.map(w => w / tot);
      const mu = S.vals.reduce((a, v, i) => a + v * pr[i], 0);
      const sd = Math.sqrt(S.vals.reduce((a, v, i) => a + (v - mu) ** 2 * pr[i], 0));
      const r = rng(11);
      const draw = () => { let u = r(), i = 0; while (i < pr.length - 1 && u > pr[i]) { u -= pr[i]; i++; } return S.vals[i]; };
      const fr = [{ src: true, mu, sd, pr, say: `This is the starting distribution: ${S.name}. Its mean is μ = ${f2(mu)} and its standard deviation is σ = ${f2(sd)}. It does not look like a bell.` }];
      SIZES.forEach((n, idx) => {
        const means = [];
        for (let t = 0; t < 2000; t++) { let s = 0; for (let j = 0; j < n; j++) s += draw(); means.push(s / n); }
        const m = means.reduce((a, b) => a + b, 0) / means.length;
        const s = Math.sqrt(means.reduce((a, b) => a + (b - m) ** 2, 0) / means.length);
        const last = idx === SIZES.length - 1;
        fr.push({ n, means, mu, sd, m, s, bell: last, say: `Average n = ${n} value${n > 1 ? 's' : ''}, 2,000 times. The averages centre on ${f2(m)} (close to μ) and spread by ${f2(s, 3)}. Theory says σ ÷ √n = ${f2(sd, 2)} ÷ ${f2(Math.sqrt(n), 2)} = ${f2(sd / Math.sqrt(n), 3)}.${last ? ' The green curve is a normal distribution with that mean and spread, and it fits the histogram. This is why so many statistics tests assume a normal shape.' : ''}` });
      });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, S = SRC[z.p.src];
      const lo = Math.min(...S.vals), hi = Math.max(...S.vals);
      if (f.src) {
        const P = plot(z, [10, 10, 400, 310], [lo - 0.5, hi + 0.5], [0, Math.max(...f.pr) * 1.15], { dx: 0, dy: 2, yl: 'probability' });
        f.pr.forEach((q, i) => { const x = S.vals[i]; rr(g, P.X(x - 0.35), P.Y(q), P.X(x + 0.35) - P.X(x - 0.35), P.Y(0) - P.Y(q), 2, { fill: c.cv }); });
      } else {
        /* bin width is a whole number of 1/n steps, because an average of n whole numbers is always a multiple of 1/n */
        const bw = Math.max(1, Math.ceil((hi - lo) / 90 * f.n)) / f.n, bins = Math.round((hi - lo) / bw);
        const cnt = new Array(bins + 1).fill(0);
        f.means.forEach(v => { cnt[Math.min(bins, Math.round((v - lo) / bw))]++; });
        const dens = cnt.map(k => k / f.means.length / bw);
        const peak = Math.max(...dens, 1 / (f.sd / Math.sqrt(f.n) * Math.sqrt(2 * Math.PI)));
        const P = plot(z, [10, 10, 400, 310], [lo - bw / 2, hi + bw / 2], [0, peak * 1.1], { dx: 1, dy: 2, xl: `average of ${f.n}` });
        dens.forEach((d, i) => { if (d > 0) rr(g, P.X(lo + i * bw - bw / 2), P.Y(d), Math.max(1, P.X(bw) - P.X(0) - 1), P.Y(0) - P.Y(d), 1, { fill: c.cv }); });
        if (f.bell) {
          const s = f.sd / Math.sqrt(f.n);
          g.save(); g.beginPath();
          for (let i = 0; i <= 160; i++) { const x = lo + (hi - lo) * i / 160, y = Math.exp(-((x - f.mu) ** 2) / (2 * s * s)) / (s * Math.sqrt(2 * Math.PI)); i ? g.lineTo(P.X(x), P.Y(y)) : g.moveTo(P.X(x), P.Y(y)); }
          g.strokeStyle = c.green; g.lineWidth = 2.5; g.stroke(); g.restore();
        }
        D.line(g, P.X(f.mu), P.Y(0), P.X(f.mu), P.Y(peak * 1.05), c.red, 1.5, [4, 3]);
      }
      head(z, f.src ? 'Start' : `n = ${f.n}`, 425, 30, { s: 16 });
      D.text(g, `μ = ${f2(f.mu)}`, 425, 62, { s: 14, mono: true, c: c.ink });
      D.text(g, `σ = ${f2(f.sd)}`, 425, 86, { s: 14, mono: true, c: c.ink });
      if (!f.src) {
        D.text(g, `spread of averages`, 425, 124, { s: 12, b: true, c: c.ink2 });
        D.text(g, `measured ${f2(f.s, 3)}`, 425, 148, { s: 13, mono: true, c: c.ink });
        D.text(g, `σ/√n     ${f2(f.sd / Math.sqrt(f.n), 3)}`, 425, 170, { s: 13, mono: true, c: c.green });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 3.1  filling missing values (imputation)
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, box, list } = MLZ;
  const NAME = { mean: 'mean', median: 'median', mode: 'most common value (mode)', zero: 'a constant 0' };
  trace('mlimpute', {
    title: 'Filling missing values: mean, median or mode',
    sub: 'Type a column of numbers and use ? for a missing value. Pick how to fill the holes and step through. Watch what filling does to the spread of the data.',
    W: 600, H: 330,
    params: [
      { k: 'vals', label: 'Column (use ? for missing)', type: 'text', v: '25, ?, 35, 40, ?, 29, 90' },
      { k: 'how', label: 'Fill with', type: 'select', v: 'median', opts: Object.keys(NAME).map(k => [k, NAME[k]]) }
    ],
    tips: [
      { t: 'With the outlier 90 in the column, the mean fill (43.8) is pulled up but the median fill (35) is not.', set: { how: 'mean' }, play: true },
      { t: 'Many holes: filling them all with one number makes the column look less spread out than it really is.', set: { vals: '10, ?, ?, 30, ?, ?, 50', how: 'mean' }, play: true }
    ],
    frames(p) {
      const cells = list(p.vals).slice(0, 12);
      if (cells.length < 2) throw new Error('Type at least two values, for example 25, ?, 35');
      const known = cells.filter(c => c !== '?').map(Number);
      if (known.some(isNaN)) throw new Error('Use numbers, and ? for a missing value');
      if (!known.length) throw new Error('At least one value must be known');
      const holes = cells.map((c, i) => c === '?' ? i : -1).filter(i => i >= 0);
      const sorted = known.slice().sort((a, b) => a - b);
      const mean = known.reduce((a, b) => a + b, 0) / known.length;
      const mid = sorted.length >> 1;
      const median = sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
      const freq = {}; known.forEach(v => { freq[v] = (freq[v] || 0) + 1; });
      const mode = +Object.keys(freq).sort((a, b) => freq[b] - freq[a] || a - b)[0];
      const fill = { mean, median, mode, zero: 0 }[p.how];
      const std = a => { const m = a.reduce((x, y) => x + y, 0) / a.length; return Math.sqrt(a.reduce((x, y) => x + (y - m) ** 2, 0) / a.length); };
      const base = { cells, holes, fill, filled: [] };
      const how = {
        mean: `Mean = sum ÷ count = ${known.join(' + ')} ÷ ${known.length} = <b>${f2(mean)}</b>.`,
        median: `Sort the known values: ${sorted.join(', ')}. The middle value is the median = <b>${f2(median)}</b>. A very big or very small value does not move it much.`,
        mode: `Count each value. The most common one is <b>${mode}</b> (${freq[mode]} time${freq[mode] > 1 ? 's' : ''}). Mode filling is mostly used for categories like city names.`,
        zero: 'Fill every hole with <b>0</b>. Only do this when a missing value really means zero, like "no purchases".'
      }[p.how];
      const fr = [
        { ...base, say: `This column has ${cells.length} rows and <b>${holes.length}</b> missing value${holes.length === 1 ? '' : 's'} (shown as ?). Most models cannot work with a missing value, so we must drop the row or fill the hole.` },
        { ...base, known: true, say: `Keep only the ${known.length} known values: ${known.join(', ')}. The filling value is worked out from these, and in a real project only from the training rows.` },
        { ...base, known: true, stat: true, say: how }
      ];
      holes.forEach((h, i) => fr.push({ ...base, known: true, stat: true, filled: holes.slice(0, i + 1), say: `Row ${h + 1} was missing. Put <b>${f2(fill)}</b> in it.` }));
      const after = cells.map(c => c === '?' ? fill : +c);
      fr.push({ ...base, known: true, stat: true, filled: holes, done: true, sa: std(known), sb: std(after),
        say: `Done. The spread (standard deviation) was ${f2(std(known))} for the known values and is <b>${f2(std(after))}</b> after filling. Filling many holes with one number shrinks the spread, so add a "was missing" column to keep that information for the model.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      const ch = Math.min(24, 290 / f.cells.length);
      head(z, 'Column', 20, 22);
      f.cells.forEach((v, i) => {
        const miss = v === '?', isFilled = f.filled.includes(i);
        box(z, 20, 32 + i * ch, 110, ch - 3, miss ? (isFilled ? f2(f.fill) : '?') : v,
          { fill: miss ? (isFilled ? c.green : c.bg) : c.surf, stroke: miss ? (isFilled ? c.green : c.red) : c.line, c: isFilled ? '#fff' : (miss ? c.red : c.ink), mono: true, b: miss, r: 4, s: 12, dash: miss && !isFilled ? [4, 3] : undefined });
        D.text(z.g, `row ${i + 1}`, 140, 32 + i * ch + ch / 2 + 2, { s: 11, c: c.ink2 });
      });
      if (f.known) {
        head(z, 'Known values', 220, 22);
        const known = f.cells.filter(v => v !== '?');
        D.text(z.g, known.join(', '), 220, 46, { s: 13, mono: true, c: c.ink });
      }
      if (f.stat) {
        head(z, `Filling value (${z.p.how})`, 220, 90);
        D.text(z.g, f2(f.fill), 220, 126, { s: 26, b: true, mono: true, c: c.cv });
      }
      if (f.done) {
        head(z, 'Spread (std)', 220, 180);
        D.text(z.g, `known only   ${f2(f.sa)}`, 220, 206, { s: 13, mono: true, c: c.ink });
        D.text(z.g, `after fill   ${f2(f.sb)}`, 220, 230, { s: 13, mono: true, b: true, c: f.sb < f.sa ? c.orange : c.green });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 3.1  finding outliers with the IQR rule
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, nums, span, rr } = MLZ;
  const quant = (s, q) => { const pos = (s.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos); return s[lo] + (s[hi] - s[lo]) * (pos - lo); };
  trace('mliqr', {
    title: 'Outliers: the IQR rule (box plot fences)',
    sub: 'Type some numbers. The IQR rule finds values that sit far outside the middle half of the data. Step through to see the quartiles, the box and the fences.',
    W: 600, H: 300,
    params: [
      { k: 'vals', label: 'Values', type: 'text', v: '32, 35, 36, 38, 40, 41, 43, 45, 47, 150' },
      { k: 'k', label: 'Fence width (times IQR)', type: 'range', v: 1.5, min: 0.5, max: 3, step: 0.5 }
    ],
    tips: [
      { t: 'k = 3 is the "far outlier" rule: only very extreme values are flagged.', set: { k: 3 }, play: true },
      { t: 'Two low outliers as well as a high one.', set: { vals: '2, 5, 30, 32, 33, 35, 36, 38, 40, 90', k: 1.5 }, play: true }
    ],
    frames(p) {
      const v = nums(p.vals).slice(0, 40);
      if (v.length < 4) throw new Error('Type at least four numbers');
      const s = v.slice().sort((a, b) => a - b);
      const q1 = quant(s, 0.25), q3 = quant(s, 0.75), med = quant(s, 0.5), iqr = q3 - q1;
      const lo = q1 - p.k * iqr, hi = q3 + p.k * iqr;
      const out = s.filter(x => x < lo || x > hi);
      const mean = s.reduce((a, b) => a + b, 0) / s.length;
      const b = { s, q1, q3, med, iqr, lo, hi, out, mean };
      return [
        { ...b, st: 1, say: `Here are the ${s.length} values on a number line, sorted from small to large: ${s.join(', ')}.` },
        { ...b, st: 2, say: `The <b>median</b> splits the data in half: ${f2(med)}.` },
        { ...b, st: 3, say: `<b>Q1</b> (the first quartile) has a quarter of the values below it: ${f2(q1)}. <b>Q3</b> has three quarters below it: ${f2(q3)}. (Same method as pandas quantile.)` },
        { ...b, st: 4, say: `The box from Q1 to Q3 holds the middle half of the data. Its width is the <b>IQR</b> = Q3 − Q1 = ${f2(q3)} − ${f2(q1)} = <b>${f2(iqr)}</b>.` },
        { ...b, st: 5, say: `Fences: Q1 − ${p.k} × IQR = <b>${f2(lo)}</b> and Q3 + ${p.k} × IQR = <b>${f2(hi)}</b>. Values outside the fences are called outliers.` },
        { ...b, st: 6, say: out.length ? `Outlier${out.length > 1 ? 's' : ''}: <b>${out.join(', ')}</b> (red). Check each one: a typing mistake should be fixed or removed, but a real rare value (a very rich customer, a real fraud) may be the most important row you have.` : 'No value falls outside the fences, so this rule finds no outliers.' },
        { ...b, st: 7, say: `The mean is ${f2(mean)} and the median is ${f2(med)}. ${Math.abs(mean - med) > 0.1 * iqr ? 'Outliers drag the mean but hardly move the median or the quartiles. That is why the IQR rule is robust, and a z score rule (which uses the mean and std) can miss outliers.' : 'They are close, so the data has no strong pull to one side.'}` }
      ];
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const [a, bb] = span(f.s.concat([f.lo, f.hi]), 0.05);
      const X = v => 30 + (v - a) / (bb - a) * 540;
      const y = 170;
      D.line(g, 30, y, 570, y, c.ink2, 1.5);
      for (let i = 0; i <= 5; i++) { const v = a + (bb - a) * i / 5; D.line(g, X(v), y, X(v), y + 6, c.ink2, 1); D.text(g, f2(v, 1), X(v), y + 20, { a: 'center', s: 11, c: c.ink2 }); }
      const seen = {};
      f.s.forEach(v => {
        seen[v] = (seen[v] || 0) + 1;
        const isOut = f.st >= 6 && (v < f.lo || v > f.hi);
        D.circle(g, X(v), y - 12 - (seen[v] - 1) * 12, 5, { fill: isOut ? c.red : c.cv });
      });
      if (f.st >= 4) rr(g, X(f.q1), 70, X(f.q3) - X(f.q1), 50, 4, { fill: c.bg, stroke: c.cv, w: 2 });
      if (f.st >= 2) { D.line(g, X(f.med), 62, X(f.med), 128, c.green, 2.5); D.text(g, `median ${f2(f.med)}`, X(f.med), 56, { a: 'center', s: 11, b: true, c: c.green }); }
      if (f.st >= 3) {
        [[f.q1, 'Q1', -1], [f.q3, 'Q3', 1]].forEach(([v, t, side]) => { D.line(g, X(v), 66, X(v), 140, c.purple || c.cv, 1.5, [4, 3]); D.text(g, `${t} ${f2(v)}`, X(v) + side * 6, 100, { a: side < 0 ? 'right' : 'left', s: 11, b: true, c: c.ink }); });
      }
      if (f.st >= 5) {
        [[f.lo, 'low fence'], [f.hi, 'high fence']].forEach(([v, t]) => { D.line(g, X(v), 40, X(v), 200, c.orange, 2, [6, 4]); D.text(g, `${t} ${f2(v)}`, X(v), 232, { a: 'center', s: 11, b: true, c: c.orange }); });
      }
      if (f.st >= 7) { D.line(g, X(f.mean), 250, X(f.mean), 270, c.red, 2.5); D.text(g, `mean ${f2(f.mean)}`, X(f.mean), 288, { a: 'center', s: 11, b: true, c: c.red }); }
      head(z, 'Number line', 30, 22);
    }
  });
})();

/* =====================================================================================================
   Foundations 3.2  feature scaling: standard, min max, robust and log
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, nums, span } = MLZ;
  const NAME = { std: 'Standard (z score)', minmax: 'Min max (0 to 1)', robust: 'Robust (median and IQR)', log: 'Log, log(1 + x)' };
  const quant = (s, q) => { const pos = (s.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos); return s[lo] + (s[hi] - s[lo]) * (pos - lo); };
  trace('mlscale', {
    title: 'Feature scaling: put every feature on a similar scale',
    sub: 'Type some values of one feature and pick a scaler. The top line shows the raw values and the bottom line the scaled ones. Watch what one big value does.',
    W: 600, H: 300,
    params: [
      { k: 'vals', label: 'Values', type: 'text', v: '30, 35, 40, 45, 50, 400' },
      { k: 'how', label: 'Scaler', type: 'select', v: 'std', opts: Object.keys(NAME).map(k => [k, NAME[k]]) }
    ],
    tips: [
      { t: 'Min max with an outlier: five of the six values get squeezed into 0 to 0.05.', set: { how: 'minmax' }, play: true },
      { t: 'Robust scaling keeps the normal values nicely spread out and lets the outlier sit far away.', set: { how: 'robust' }, play: true },
      { t: 'Without an outlier every scaler looks similar.', set: { vals: '30, 35, 40, 45, 50, 55', how: 'minmax' }, play: true }
    ],
    frames(p) {
      const v = nums(p.vals).slice(0, 20);
      if (v.length < 2) throw new Error('Type at least two numbers');
      if (p.how === 'log' && v.some(x => x <= -1)) throw new Error('log(1 + x) needs every value above −1');
      const s = v.slice().sort((a, b) => a - b), n = v.length;
      const mean = v.reduce((a, b) => a + b, 0) / n, sd = Math.sqrt(v.reduce((a, b) => a + (b - mean) ** 2, 0) / n);
      const mn = s[0], mx = s[n - 1], med = quant(s, 0.5), iqr = quant(s, 0.75) - quant(s, 0.25);
      let tf, stat, formula;
      if (p.how === 'std') { tf = x => sd ? (x - mean) / sd : 0; stat = `mean = ${f2(mean)}, standard deviation = ${f2(sd)}`; formula = x => `(${x} − ${f2(mean)}) ÷ ${f2(sd)}`; }
      else if (p.how === 'minmax') { tf = x => mx > mn ? (x - mn) / (mx - mn) : 0; stat = `min = ${f2(mn)}, max = ${f2(mx)}`; formula = x => `(${x} − ${f2(mn)}) ÷ (${f2(mx)} − ${f2(mn)})`; }
      else if (p.how === 'robust') { tf = x => iqr ? (x - med) / iqr : 0; stat = `median = ${f2(med)}, IQR = ${f2(iqr)}`; formula = x => `(${x} − ${f2(med)}) ÷ ${f2(iqr)}`; }
      else { tf = x => Math.log1p(x); stat = 'no statistics are needed, the same formula works for every value'; formula = x => `log(1 + ${x})`; }
      const out = v.map(tf);
      const b = { v, out };
      const fr = [
        { ...b, st: 1, say: `These are the raw values: ${v.join(', ')}. Features like age (tens) and income (thousands) live on very different scales, which confuses models that use distances or gradients.` },
        { ...b, st: 2, say: `${NAME[p.how]} scaling first learns from the training values: ${stat}.` }
      ];
      v.forEach((x, i) => { if (i < 6) fr.push({ ...b, st: 3, upto: i + 1, say: `Value ${x} becomes ${formula(x)} = <b>${f2(out[i], 2)}</b>.` }); });
      fr.push({ ...b, st: 4, upto: v.length, say: `All values scaled: ${out.map(x => f2(x)).join(', ')}. ${{
        std: 'The result has mean 0 and standard deviation 1. One outlier still squeezes the others together because it inflates the standard deviation.',
        minmax: 'Everything now lies between 0 and 1. One outlier becomes 1 and squeezes all the normal values near 0.',
        robust: 'The median becomes 0 and the middle half spans about 1. The outlier does not change the scale of the other values.',
        log: 'Big values are pulled in much more than small ones, so a long right tail becomes compact. Good for prices, incomes and counts.'
      }[p.how]} ${p.how === 'log' ? 'Unlike the other three scalers, log changes the shape of the data.' : 'Notice the dots keep the same pattern: this scaler only shifts and stretches the line, it never changes the shape of the data.'}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const line = (vals, y, label, band) => {
        const [a, b] = span(band ? vals.concat([-1, 1]) : vals, 0.06);
        const X = t => 40 + (t - a) / (b - a) * 520;
        if (band) { g.save(); g.globalAlpha = 0.18; g.fillStyle = c.green; g.fillRect(X(-1), y - 26, X(1) - X(-1), 26); g.restore(); }
        D.line(g, 40, y, 560, y, c.ink2, 1.5);
        for (let i = 0; i <= 4; i++) { const t = a + (b - a) * i / 4; D.line(g, X(t), y, X(t), y + 5, c.ink2, 1); D.text(g, f2(t, 2), X(t), y + 18, { a: 'center', s: 10, c: c.ink2 }); }
        head(z, label, 40, y - 44);
        return X;
      };
      const X1 = line(f.v, 90, 'Raw values', false);
      f.v.forEach(x => D.circle(g, X1(x), 80, 6, { fill: c.cv }));
      if (f.st >= 3) {
        const X2 = line(f.out, 220, 'Scaled values (the shaded band runs from −1 to 1)', true);
        f.out.forEach((x, i) => {
          if (i >= f.upto) return;
          D.line(g, X1(f.v[i]), 86, X2(x), 204, c.line, 1, [3, 3]);
          D.circle(g, X2(x), 210, 6, { fill: c.green });
        });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 3.2  turning categories into numbers (one hot, dummy, ordinal)
   ===================================================================================================== */
(() => {
  const { trace, f2, head, box, list, D } = MLZ;
  const NAME = { onehot: 'One hot (one column per category)', dummy: 'Dummy (drop the first column)', ordinal: 'Ordinal (one number per category)' };
  trace('mlonehot', {
    title: 'Encoding categories: one hot, dummy and ordinal',
    sub: 'Models only understand numbers. Type a column of categories and pick an encoding. Each step builds one more piece of the encoded table.',
    W: 600, H: 320,
    params: [
      { k: 'vals', label: 'Categories', type: 'text', v: 'Delhi, Pune, Delhi, Mumbai, Pune' },
      { k: 'how', label: 'Encoding', type: 'select', v: 'onehot', opts: Object.keys(NAME).map(k => [k, NAME[k]]) }
    ],
    tips: [
      { t: 'Ordinal on sizes small, medium, large keeps a real order. Give the order yourself, because alphabetical order would put large first.', set: { vals: 'small, large, medium, small', how: 'ordinal' }, play: true },
      { t: 'Dummy encoding: Delhi is the row of all zeros, so k categories need only k − 1 columns.', set: { how: 'dummy' }, play: true }
    ],
    frames(p) {
      const rows = list(p.vals).slice(0, 8);
      if (rows.length < 2) throw new Error('Type at least two categories, separated by commas');
      const cats = [...new Set(rows)].sort();
      if (cats.length > 6) throw new Error('Use at most six different categories');
      const cols = p.how === 'dummy' ? cats.slice(1) : (p.how === 'ordinal' ? ['code'] : cats);
      const code = r => p.how === 'ordinal' ? [cats.indexOf(r)] : cols.map(cname => r === cname ? 1 : 0);
      const b = { rows, cats, cols, enc: rows.map(code) };
      const fr = [
        { ...b, st: 1, say: `The column has ${rows.length} rows of text: ${rows.join(', ')}. A model cannot multiply "${rows[0]}" by a weight, so we turn each category into numbers.` },
        { ...b, st: 2, say: `Find the different categories (sorted): <b>${cats.join(', ')}</b>. There are k = ${cats.length}.` },
        { ...b, st: 3, upto: 0, say: p.how === 'ordinal' ? `Ordinal encoding makes one column and gives each category a number: ${cats.map((cname, i) => `${cname} = ${i}`).join(', ')}.` :
          p.how === 'dummy' ? `Dummy encoding makes k − 1 = ${cols.length} columns: ${cols.join(', ')}. The first category, ${cats[0]}, gets no column. It is the row of all zeros.` :
          `One hot encoding makes one 0 or 1 column per category: ${cols.join(', ')}.` }
      ];
      rows.forEach((r, i) => fr.push({ ...b, st: 3, upto: i + 1, say: `Row ${i + 1} is ${r}, so it becomes <b>[${b.enc[i].join(', ')}]</b>.` }));
      fr.push({ ...b, st: 4, upto: rows.length, say: {
        onehot: 'Done. Each row has exactly one 1. No category is "bigger" than another, which is right for cities. With many categories the table gets very wide, so use target encoding or hashing then.',
        dummy: 'Done. Dropping one column removes the redundancy (the columns would always add up to 1), which matters for plain linear regression. Tree models and regularised models are fine with full one hot.',
        ordinal: `Done. One column only, but the model now thinks ${cats[cats.length - 1]} (${cats.length - 1}) is "bigger" than ${cats[0]} (0). Use ordinal only when the categories have a real order, like small, medium, large, or for tree models.`
      }[p.how] });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      const rh = Math.min(30, 250 / f.rows.length);
      head(z, 'Text column', 20, 24);
      box(z, 20, 34, 110, rh - 4, 'value', { fill: c.bg, b: true, r: 4, s: 11 });
      f.rows.forEach((r, i) => box(z, 20, 34 + (i + 1) * rh, 110, rh - 4, r, { r: 4, s: 12 }));
      if (f.st >= 2) {
        head(z, 'Categories', 150, 24);
        f.cats.forEach((cname, i) => D.text(z.g, z.p.how === 'ordinal' ? `${cname} = ${i}` : cname, 150, 52 + i * 20, { s: 12, mono: true, c: c.ink }));
      }
      if (f.st >= 3) {
        const x0 = 280, cw = Math.min(70, 300 / f.cols.length);
        head(z, 'Encoded table', x0, 24);
        f.cols.forEach((cname, j) => box(z, x0 + j * cw, 34, cw - 3, rh - 4, cname, { fill: c.bg, b: true, r: 4, s: 11 }));
        for (let i = 0; i < (f.upto || 0); i++) f.enc[i].forEach((v, j) => box(z, x0 + j * cw, 34 + (i + 1) * rh, cw - 3, rh - 4, String(v), { fill: v && z.p.how !== 'ordinal' ? c.cv : c.surf, c: v && z.p.how !== 'ordinal' ? '#fff' : c.ink, mono: true, b: true, r: 4, s: 12 }));
      }
    }
  });
})();
