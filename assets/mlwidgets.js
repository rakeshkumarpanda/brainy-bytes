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
      D.text(z.g, 'blue: v   green: M v', 318, 312, { s: 11, c: c.ink2 });
    }
  });
})();
