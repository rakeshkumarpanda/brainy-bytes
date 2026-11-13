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
