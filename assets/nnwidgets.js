/* ===== NLP section animations (neural methods), one block per step. The framework is assets/cvviz.js and the
   drawing helpers come from NLZ in assets/nlpwidgets.js. Every value an animation uses has a control, and its
   "Try this" list says which values to change and what to look for. ===== */
(() => {
  const { def, D, esc } = CVZ;
  const { tw, rr, pill, wrap, fit, fmt, nums } = NLZ;

  /* ---------- shared maths ---------- */
  const sig = x => 1 / (1 + Math.exp(-x));
  const softmax = a => { const m = Math.max(...a), e = a.map(v => Math.exp(v - m)), s = e.reduce((x, y) => x + y, 0); return e.map(v => v / s); };
  const dot = (a, b) => a.reduce((s, v, i) => s + v * (b[i] || 0), 0);
  const norm = a => Math.sqrt(dot(a, a));
  const cos = (a, b) => { const n = norm(a) * norm(b); return n ? dot(a, b) / n : 0; };
  const rng = seed => { let s = (seed >>> 0) || 1; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; };
  const gauss = r => { let u = 0, v = 0; while (!u) u = r(); while (!v) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  const rows = s => String(s).split('\n').map(l => l.trim()).filter(Boolean);
  const vecs = s => rows(s).map(l => nums(l.replace(/[\[\]()]/g, ' ')));
  const f2 = (v, d = 3) => fmt(v, d);
  const vstr = (v, d = 3) => '[' + v.map(x => f2(x, d)).join(', ') + ']';
  /* project points to 2D with the top two principal components (power iteration), for drawing embeddings */
  function pca2(X) {
    const n = X.length, d = X[0].length;
    if (d <= 2) return X.map(r => [r[0], r[1] || 0]);
    const mu = Array(d).fill(0); X.forEach(r => r.forEach((v, j) => { mu[j] += v / n; }));
    const C = X.map(r => r.map((v, j) => v - mu[j]));
    const cov = Array.from({ length: d }, (_, i) => Array.from({ length: d }, (_, j) => C.reduce((s, r) => s + r[i] * r[j], 0)));
    const comp = [];
    for (let k = 0; k < 2; k++) {
      let v = Array.from({ length: d }, (_, i) => 1 / (i + 1 + k));
      for (let it = 0; it < 80; it++) {
        let w = cov.map(r => dot(r, v));
        comp.forEach(c => { const p = dot(w, c); w = w.map((x, i) => x - p * c[i]); });
        const nw = norm(w) || 1; v = w.map(x => x / nw);
      }
      comp.push(v);
    }
    return C.map(r => [dot(r, comp[0]), dot(r, comp[1])]);
  }
  /* a scatter of labelled points in a box, scaled to fit */
  function scatter(g, z, box, pts, labels, o = {}) {
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    let x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    if (o.zero) { x0 = Math.min(x0, 0); x1 = Math.max(x1, 0); y0 = Math.min(y0, 0); y1 = Math.max(y1, 0); }
    const px = (x1 - x0) * 0.15 || 1, py = (y1 - y0) * 0.15 || 1;
    const m = D.axes(g, z, box, [x0 - px, x1 + px], [y0 - py, y1 + py], { nx: 2, ny: 2, fx: v => fmt(v, 1), fy: v => fmt(v, 1) });
    const placed = [];
    pts.forEach((p, i) => {
      const c = (o.colors && o.colors[i]) || z.col.cv;
      D.circle(g, m.sx(p[0]), m.sy(p[1]), o.r || 5, { fill: c });
      if (!labels) return;
      /* move a label down or up until it does not cover an earlier one */
      /* labels go right of the dot, or left of it when they would run past the plot */
      const w = tw(g, labels[i], { s: 12, b: true }), x = m.sx(p[0]) + 7 + w > box[0] + box[2] - 2 ? m.sx(p[0]) - 7 - w : m.sx(p[0]) + 7;
      let y = m.sy(p[1]) - 6;
      const hit = yy => placed.some(r => x < r[0] + r[2] && x + w > r[0] && yy - 11 < r[1] && yy + 2 > r[1] - 13);
      for (let k = 1; k < 8 && hit(y); k++) y = m.sy(p[1]) - 6 + (k % 2 ? 1 : -1) * Math.ceil(k / 2) * 13;
      placed.push([x, y, w]);
      D.text(g, labels[i], x, y, { s: 12, b: true, c: z.col.ink });
    });
    return m;
  }
  /* bars with labels under them, values on top */
  function bars(g, z, box, vals, labels, o = {}) {
    const [X, Y, W, H] = box, n = vals.length, mx = o.max || Math.max(...vals.map(Math.abs), 1e-9), bw = W / n;
    D.line(g, X, Y + H, X + W, Y + H, z.col.line, 1);
    vals.forEach((v, i) => {
      const h = Math.abs(v) / mx * (H - 14), x = X + i * bw;
      rr(g, x + bw * 0.14, Y + H - h, bw * 0.72, h, 3, { fill: (o.colors && o.colors[i]) || o.c || z.col.cv });
      D.text(g, o.fmt ? o.fmt(v) : fmt(v, 3), x + bw / 2, Y + H - h - 4, { a: 'center', s: fit(g, o.fmt ? o.fmt(v) : fmt(v, 3), bw, 10.5), b: true, c: z.col.ink });
      if (labels) D.text(g, labels[i], x + bw / 2, Y + H + 14, { a: 'center', s: fit(g, labels[i], bw - 2, 11.5), b: true, c: z.col.ink2 });
    });
  }

  /* ================================================================ Step 1: neurons and gradient descent */
  const PW = '1 2\n2 4\n4 5';
  def('regline', {
    title: 'A line through the data and its cost',
    sub: 'wags(pats) = w × pats + b. Each red bar is one error. The cost is the sum of the squared errors.',
    W: 560, H: 300,
    params: [
      { k: 'w', label: 'Weight w (slope)', v: 0.25, min: -1, max: 3, step: 0.01 },
      { k: 'b', label: 'Bias b (where the line starts)', v: 0.68, min: -2, max: 5, step: 0.01 },
      { k: 'data', label: 'Data, one "pats wags" pair per line', type: 'area', v: PW },
      { k: 'sq', label: 'Draw each squared error as a square', type: 'check', v: false }
    ],
    tips: [
      { t: 'The first guess on the slide: w = 0.25 and b = 0.68. The line sits far under the dots, so the cost is large.', set: { w: 0.25, b: 0.68 } },
      { t: 'The slide guess w = 1.00 and b = 1.37. Errors 0.37, 0.63 and 0.37 give cost 0.67.', set: { w: 1, b: 1.37 } },
      { t: 'Try w = 0.43 and b = 1.50, then w = 1.00 and b = 1.50. Which one has the lower cost?', set: { w: 0.43, b: 1.5 } },
      { t: 'Least squares answer for this data: w = 0.929 and b = 1.5. No other line has a lower cost (0.643).', set: { w: 0.929, b: 1.5 } },
      { t: 'Switch on the squares. Big errors get much bigger squares, which is why squared error punishes outliers.', set: { sq: true } }
    ],
    draw(z) {
      const { g, p } = z;
      const pts = rows(p.data).map(l => nums(l)).filter(r => r.length >= 2);
      if (!pts.length) return 'Write pairs like "1 2" on separate lines.';
      const box = [60, 16, 270, 236];
      const xmax = Math.max(...pts.map(q => q[0])) + 1, ymax = Math.max(...pts.map(q => q[1]), p.w * xmax + p.b) + 1;
      const ymin = Math.min(0, ...pts.map(q => q[1]), p.b);
      const m = D.axes(g, z, box, [0, xmax], [ymin, ymax], { nx: 4, ny: 4, xl: 'pats', yl: 'wags' });
      g.save(); g.beginPath(); g.rect(box[0], box[1], box[2], box[3]); g.clip();
      let cost = 0;
      pts.forEach(([x, y]) => {
        const yh = p.w * x + p.b, e = yh - y; cost += e * e;
        if (p.sq) { const s = Math.abs(m.sy(y) - m.sy(yh)); g.save(); g.globalAlpha = 0.18; D.rect(g, m.sx(x), Math.min(m.sy(y), m.sy(yh)), s, s, { fill: z.col.red }); g.restore(); }
        D.line(g, m.sx(x), m.sy(y), m.sx(x), m.sy(yh), z.col.red, 2.5);
      });
      D.line(g, m.sx(0), m.sy(p.b), m.sx(xmax), m.sy(p.w * xmax + p.b), z.col.cv, 3);
      g.restore();
      pts.forEach(([x, y]) => D.circle(g, m.sx(x), m.sy(y), 6, { fill: z.col.orange }));
      let y = 34;
      D.text(g, 'pats  wags  model   error²', 350, y, { s: 11.5, b: true, mono: true, c: z.col.ink2 });
      pts.slice(0, 8).forEach(([x, yy]) => {
        y += 20; const yh = p.w * x + p.b;
        D.text(g, `${String(x).padEnd(5)} ${String(yy).padEnd(5)} ${f2(yh, 2).padEnd(7)} ${f2((yh - yy) ** 2, 3)}`, 350, y, { s: 11.5, mono: true, c: z.col.ink });
      });
      D.text(g, `cost = ${f2(cost, 4)}`, 350, y + 32, { s: 16, b: true, c: z.col.cv });
      return `Cost C(w, b) = ∑ (w·x + b − y)² = <b>${f2(cost, 4)}</b>. Move a slider and the cost changes. Learning means finding the w and b that make this number as small as possible.`;
    }
  });

  def('gd1d', {
    title: 'Gradient descent on one parameter',
    sub: 'The model is NN() = b and the target is 4, so the cost is (b − 4)². Each step moves b against the slope 2(b − 4).',
    W: 560, H: 290,
    params: [
      { k: 'b0', label: 'Starting value of b', v: 0, min: -4, max: 12, step: 0.1 },
      { k: 'lr', label: 'Learning rate η', v: 0.1, min: 0.01, max: 1.2, step: 0.01 },
      { k: 'target', label: 'Target value', v: 4, min: -2, max: 8, step: 0.5 },
      { k: 'n', label: 'Number of steps', v: 12, min: 1, max: 40 }
    ],
    tips: [
      { t: 'η = 0.1: b creeps toward 4 and every step is 0.8 times the last one. Press Play.', set: { lr: 0.1, b0: 0 }, play: true },
      { t: 'η = 0.5: one step lands exactly on 4, because b − η × 2(b − 4) = 4 for any start.', set: { lr: 0.5, b0: 0 }, play: true },
      { t: 'η = 0.9: b jumps across the valley and back, an oscillation that still settles.', set: { lr: 0.9, b0: 0 }, play: true },
      { t: 'η = 1.05: every jump is bigger than the last. The steps diverge, the cost explodes.', set: { lr: 1.05, b0: 2, n: 14 }, play: true },
      { t: 'η = 0.02: so small that 40 steps are not enough. Too small is slow, too big is unstable.', set: { lr: 0.02, b0: 0, n: 40 }, play: true }
    ],
    startAtZero: true,
    steps: z => z.p.n,
    speed: () => 450,
    draw(z) {
      const { g, p } = z;
      const T = p.target, path = [p.b0];
      for (let i = 0; i < p.n; i++) { const b = path[path.length - 1]; path.push(b - p.lr * 2 * (b - T)); }
      const shown = path.slice(0, z.step + 1);
      const lo = Math.min(T - 6, ...shown.filter(isFinite)), hi = Math.max(T + 6, ...shown.filter(isFinite));
      const span = Math.min(60, Math.max(Math.abs(lo - T), Math.abs(hi - T)));
      const xr = [T - span, T + span], C = b => (b - T) ** 2;
      const box = [60, 14, 290, 230];
      const m = D.axes(g, z, box, xr, [0, span * span], { nx: 4, ny: 4, xl: 'b', yl: 'cost', fx: v => fmt(v, 1), fy: v => fmt(v, 0) });
      g.save(); g.beginPath(); g.rect(box[0], box[1], box[2], box[3]); g.clip();
      g.strokeStyle = z.col.cv; g.lineWidth = 2.5; g.beginPath();
      for (let i = 0; i <= 120; i++) { const b = xr[0] + (xr[1] - xr[0]) * i / 120; i ? g.lineTo(m.sx(b), m.sy(C(b))) : g.moveTo(m.sx(b), m.sy(C(b))); }
      g.stroke();
      for (let i = 1; i < shown.length; i++) D.arrow(g, m.sx(shown[i - 1]), m.sy(C(shown[i - 1])), m.sx(shown[i]), m.sy(C(shown[i])), z.col.orange, 1.6, 6);
      shown.forEach((b, i) => D.circle(g, m.sx(b), m.sy(C(b)), i === shown.length - 1 ? 6 : 3.5, { fill: i === shown.length - 1 ? z.col.red : z.col.orange }));
      g.restore();
      const b = shown[shown.length - 1], slope = 2 * (b - T);
      D.text(g, `step ${z.step}`, 370, 34, { s: 13, b: true, c: z.col.ink2 });
      D.text(g, `b = ${f2(b, 4)}`, 370, 60, { s: 14, b: true, mono: true, c: z.col.ink });
      D.text(g, `slope = 2(b − ${T}) = ${f2(slope, 3)}`, 370, 84, { s: 11.5, mono: true, c: z.col.ink });
      D.text(g, `cost = ${f2(C(b), 4)}`, 370, 108, { s: 11.5, mono: true, c: z.col.ink });
      D.text(g, `next b = b − η × slope`, 370, 140, { s: 11.5, mono: true, c: z.col.cv });
      D.text(g, `= ${f2(b - p.lr * slope, 4)}`, 370, 160, { s: 11.5, mono: true, b: true, c: z.col.cv });
      const r = 1 - 2 * p.lr;
      D.text(g, `factor 1 − 2η = ${f2(r, 3)}`, 370, 196, { s: 11.5, mono: true, c: Math.abs(r) < 1 ? z.col.green : z.col.red });
      D.text(g, Math.abs(r) < 1 ? (r < 0 ? 'oscillates, then settles' : 'settles smoothly') : 'diverges', 370, 216, { s: 12, b: true, c: Math.abs(r) < 1 ? z.col.green : z.col.red });
      return `Every step multiplies the distance to the target by 1 − 2η = ${f2(r, 3)}. When that factor lies between −1 and 1 gradient descent converges, so for this cost any η below 1 works and η = 0.5 is the one step answer.`;
    }
  });

  def('gdbowl', {
    title: 'The cost bowl over w and b, seen from above',
    sub: 'Each ring joins points with the same cost for the pats and wags data. Gradient descent walks downhill using the two partial derivatives.',
    W: 560, H: 320,
    params: [
      { k: 'w0', label: 'Start w', v: -0.5, min: -1, max: 3, step: 0.05 },
      { k: 'b0', label: 'Start b', v: 4, min: -2, max: 5, step: 0.05 },
      { k: 'lr', label: 'Learning rate η', v: 0.02, min: 0.001, max: 0.05, step: 0.001 },
      { k: 'n', label: 'Number of steps', v: 150, min: 1, max: 300 },
      { k: 'data', label: 'Data, one "pats wags" pair per line', type: 'area', v: PW }
    ],
    tips: [
      { t: 'Press Play. The path first drops down the steep side, then crawls along the long narrow valley toward the bottom at w = 0.929, b = 1.5.', set: { w0: -0.5, b0: 4, lr: 0.02, n: 150 }, play: true },
      { t: 'Raise η to 0.04. The path zig-zags across the valley because the bowl is far steeper in one direction than the other.', set: { lr: 0.04, n: 60 }, play: true },
      { t: 'η = 0.045 is past the limit 2 ÷ 46.8 = 0.0427 for this bowl. Watch the path bounce outwards and the cost explode.', set: { lr: 0.045, n: 40 }, play: true },
      { t: 'Start somewhere else. Every start ends at the same bottom, because this cost is a single bowl with one lowest point.', set: { w0: 2.8, b0: -1.5, lr: 0.03, n: 250 }, play: true }
    ],
    startAtZero: true,
    steps: z => z.p.n,
    speed: () => 120,
    draw(z) {
      const { g, p } = z;
      const pts = rows(p.data).map(l => nums(l)).filter(r => r.length >= 2);
      if (!pts.length) return 'Write pairs like "1 2" on separate lines.';
      const C = (w, b) => pts.reduce((s, [x, y]) => s + (w * x + b - y) ** 2, 0);
      const G = (w, b) => pts.reduce((a, [x, y]) => { const e = 2 * (w * x + b - y); return [a[0] + e * x, a[1] + e]; }, [0, 0]);
      const box = [56, 12, 300, 260], wr = [-1, 3], br = [-2, 5];
      const m = D.axes(g, z, box, wr, br, { nx: 4, ny: 7, xl: 'w', yl: 'b' });
      const cell = 6;
      for (let px = 0; px < box[2]; px += cell) for (let py = 0; py < box[3]; py += cell) {
        const w = wr[0] + (px + cell / 2) / box[2] * (wr[1] - wr[0]), b = br[1] - (py + cell / 2) / box[3] * (br[1] - br[0]);
        const c = Math.log(1 + C(w, b));
        const t = Math.min(1, c / 6);
        g.fillStyle = z.col.dark ? `rgba(251,146,60,${0.08 + t * 0.55})` : `rgba(194,65,12,${0.05 + t * 0.5})`;
        g.fillRect(box[0] + px, box[1] + py, cell, cell);
      }
      const path = [[p.w0, p.b0]];
      for (let i = 0; i < p.n; i++) { const [w, b] = path[path.length - 1]; const gr = G(w, b); path.push([w - p.lr * gr[0], b - p.lr * gr[1]]); }
      const shown = path.slice(0, z.step + 1);
      g.save(); g.beginPath(); g.rect(box[0], box[1], box[2], box[3]); g.clip();
      for (let i = 1; i < shown.length; i++) D.line(g, m.sx(shown[i - 1][0]), m.sy(shown[i - 1][1]), m.sx(shown[i][0]), m.sy(shown[i][1]), z.col.ink, 1.8);
      shown.forEach((q, i) => D.circle(g, m.sx(q[0]), m.sy(q[1]), i === shown.length - 1 ? 5.5 : 2.2, { fill: i === shown.length - 1 ? z.col.cv : z.col.ink }));
      g.restore();
      const [w, b] = shown[shown.length - 1], gr = G(w, b);
      const lx = 390;
      D.text(g, `step ${z.step}`, lx, 30, { s: 13, b: true, c: z.col.ink2 });
      D.text(g, `w = ${f2(w, 4)}`, lx, 56, { s: 13, mono: true, b: true, c: z.col.ink });
      D.text(g, `b = ${f2(b, 4)}`, lx, 76, { s: 13, mono: true, b: true, c: z.col.ink });
      D.text(g, `∂C/∂w = ${f2(gr[0], 3)}`, lx, 106, { s: 12, mono: true, c: z.col.ink });
      D.text(g, `∂C/∂b = ${f2(gr[1], 3)}`, lx, 126, { s: 12, mono: true, c: z.col.ink });
      D.text(g, `cost = ${f2(C(w, b), 4)}`, lx, 156, { s: 14, b: true, c: z.col.cv });
      D.text(g, 'darker = higher cost', lx, 196, { s: 11.5, c: z.col.ink2 });
      return `∂C/∂w = ∑ 2(wx + b − y)·x and ∂C/∂b = ∑ 2(wx + b − y). Each step does w ← w − η ∂C/∂w and b ← b − η ∂C/∂b at the same time. ${isFinite(C(w, b)) && C(w, b) < 1e6 ? '' : '<b>The steps diverged. Lower η.</b>'}`;
    }
  });

  const FLOWERS = '3 1.5 1\n2 1 0\n4 1.5 1\n3 1 0\n3.5 0.5 1\n2 0.5 0\n5.5 1 1\n1 1 0';
  function trainNeuron(data, w1, w2, b, lr, iters, seed) {
    const r = rng(seed), costs = [];
    const total = () => data.reduce((s, q) => s + (sig(w1 * q[0] + w2 * q[1] + b) - q[2]) ** 2, 0);
    for (let i = 0; i <= iters; i++) {
      if (i % Math.max(1, Math.round(iters / 60)) === 0) costs.push(total());
      if (i === iters) break;
      const q = data[Math.floor(r() * data.length)];
      const zz = q[0] * w1 + q[1] * w2 + b, pred = sig(zz);
      const dz = 2 * (pred - q[2]) * pred * (1 - pred);
      w1 -= lr * dz * q[0]; w2 -= lr * dz * q[1]; b -= lr * dz;
    }
    return { w1, w2, b, costs, cost: total() };
  }
  def('flowers', {
    title: 'One neuron sorts the flowers',
    sub: 'Red flowers are type 1, blue are type 0. The neuron says sigmoid(w1·length + w2·width + b). The shading is its answer at every point and the line is where it says 0.5.',
    W: 560, H: 320,
    params: [
      { k: 'mode', label: 'Weights come from', type: 'select', v: 'hand', opts: [['hand', 'the sliders below'], ['train', 'training with gradient descent']] },
      { k: 'w1', label: 'w1 (weight on length)', v: 0.5, min: -4, max: 4, step: 0.05, show: p => p.mode === 'hand' },
      { k: 'w2', label: 'w2 (weight on width)', v: 0.2, min: -4, max: 4, step: 0.05, show: p => p.mode === 'hand' },
      { k: 'b', label: 'bias b', v: 0.3, min: -12, max: 6, step: 0.1, show: p => p.mode === 'hand' },
      { k: 'lr', label: 'Learning rate', v: 0.1, min: 0.01, max: 1, step: 0.01, show: p => p.mode === 'train' },
      { k: 'iters', label: 'Training steps (one random flower each)', v: 10000, min: 0, max: 20000, step: 100, show: p => p.mode === 'train' },
      { k: 'seed', label: 'Random seed', v: 1, min: 1, max: 50, show: p => p.mode === 'train' },
      { k: 'ml', label: 'Mystery flower length', v: 4.5, min: 0, max: 6, step: 0.1 },
      { k: 'mw', label: 'Mystery flower width', v: 1, min: 0, max: 2, step: 0.05 },
      { k: 'data', label: 'Flowers: length width type', type: 'area', v: FLOWERS }
    ],
    tips: [
      { t: 'The slide example w1 = 0.5, w2 = 0.2, b = 0.3 at the flower (2, 1): z = 1.5 and sigmoid gives 0.82. These weights call almost everything red.', set: { mode: 'hand', w1: 0.5, w2: 0.2, b: 0.3, ml: 2, mw: 1 } },
      { t: 'Switch to training with 10,000 steps as in the notebook. The line moves between the blue and red groups and the mystery flower (4.5, 1) comes out red, close to 0.99.', set: { mode: 'train', iters: 10000, lr: 0.1, ml: 4.5, mw: 1 } },
      { t: 'Set training steps to 0, then 200, then 2000. Watch the cost curve and the line improve step by step.', set: { mode: 'train', iters: 200 } },
      { t: 'Use a learning rate of 1. Training is faster but the cost curve is noisier.', set: { mode: 'train', lr: 1, iters: 3000 } },
      { t: 'Move the mystery flower to length 2.6. It now sits near the line, so the neuron is unsure and answers close to 0.5.', set: { ml: 2.6, mw: 1 } }
    ],
    draw(z) {
      const { g, p } = z;
      const data = rows(p.data).map(l => nums(l)).filter(r => r.length >= 3);
      let w1 = p.w1, w2 = p.w2, b = p.b, costs = null;
      if (p.mode === 'train') { const t = trainNeuron(data, 0.3, -0.2, 0.1, p.lr, p.iters, p.seed); ({ w1, w2, b, costs } = t); }
      const box = [52, 12, 290, 250], xr = [0, 6], yr = [0, 2];
      const m = D.axes(g, z, box, xr, yr, { nx: 6, ny: 4, xl: 'length', yl: 'width' });
      const cell = 8;
      for (let px = 0; px < box[2]; px += cell) for (let py = 0; py < box[3]; py += cell) {
        const x = xr[0] + (px + cell / 2) / box[2] * 6, y = yr[1] - (py + cell / 2) / box[3] * 2;
        const s = sig(w1 * x + w2 * y + b);
        g.fillStyle = s > 0.5 ? `rgba(220,38,38,${(s - 0.5) * 0.5})` : `rgba(37,99,235,${(0.5 - s) * 0.5})`;
        g.fillRect(box[0] + px, box[1] + py, cell, cell);
      }
      g.save(); g.beginPath(); g.rect(box[0], box[1], box[2], box[3]); g.clip();
      if (Math.abs(w2) > 1e-6) D.line(g, m.sx(0), m.sy(-b / w2), m.sx(6), m.sy(-(b + w1 * 6) / w2), z.col.ink, 2, [6, 4]);
      else if (Math.abs(w1) > 1e-6) D.line(g, m.sx(-b / w1), m.sy(0), m.sx(-b / w1), m.sy(2), z.col.ink, 2, [6, 4]);
      g.restore();
      data.forEach(q => D.circle(g, m.sx(q[0]), m.sy(q[1]), 7, { fill: q[2] ? '#dc2626' : '#2563eb', stroke: '#fff', w: 1.5 }));
      const pm = sig(w1 * p.ml + w2 * p.mw + b);
      D.circle(g, m.sx(p.ml), m.sy(p.mw), 8, { fill: '#9ca3af', stroke: z.col.ink, w: 2 });
      const lx = 370;
      D.text(g, `w1 = ${f2(w1, 3)}   w2 = ${f2(w2, 3)}`, lx, 26, { s: 12, mono: true, b: true, c: z.col.ink });
      D.text(g, `b = ${f2(b, 3)}`, lx, 46, { s: 12, mono: true, b: true, c: z.col.ink });
      const zz = w1 * p.ml + w2 * p.mw + b;
      D.text(g, `mystery z = ${f2(zz, 3)}`, lx, 74, { s: 12, mono: true, c: z.col.ink });
      D.text(g, `sigmoid(z) = ${f2(pm, 4)}`, lx, 94, { s: 13, mono: true, b: true, c: pm > 0.5 ? '#dc2626' : '#2563eb' });
      D.text(g, pm > 0.5 ? 'so: red (type 1)' : 'so: blue (type 0)', lx, 114, { s: 12, b: true, c: z.col.ink2 });
      if (costs && costs.length > 1) {
        const cb = [lx, 140, 170, 110], mx = Math.max(...costs);
        D.rect(g, cb[0], cb[1], cb[2], cb[3], { stroke: z.col.line, w: 1 });
        D.text(g, 'total cost while training', cb[0], cb[1] - 6, { s: 11, b: true, c: z.col.ink2 });
        g.strokeStyle = z.col.cv; g.lineWidth = 2; g.beginPath();
        costs.forEach((c, i) => { const x = cb[0] + i / (costs.length - 1) * cb[2], y = cb[1] + cb[3] - c / mx * (cb[3] - 4); i ? g.lineTo(x, y) : g.moveTo(x, y); });
        g.stroke();
        D.text(g, `end: ${f2(costs[costs.length - 1], 3)}`, cb[0] + cb[2], cb[1] + 14, { a: 'right', s: 11, b: true, c: z.col.ink });
      }
      const wrong = data.filter(q => (sig(w1 * q[0] + w2 * q[1] + b) > 0.5 ? 1 : 0) !== q[2]).length;
      return `The dashed line is w1·length + w2·width + b = 0, where the neuron says exactly 0.5. ${wrong ? `It puts ${wrong} of ${data.length} flowers on the wrong side.` : `All ${data.length} flowers are on the correct side.`} Training uses the chain rule: ∂cost/∂w1 = 2(pred − target) · σ′(z) · length.`;
    }
  });

  const ACTS = {
    step: { n: 'threshold', f: x => (x >= 0 ? 1 : 0), d: () => 0 },
    sigmoid: { n: 'sigmoid', f: sig, d: x => sig(x) * (1 - sig(x)) },
    tanh: { n: 'tanh', f: Math.tanh, d: x => 1 - Math.tanh(x) ** 2 },
    hardtanh: { n: 'hard tanh', f: x => Math.max(-1, Math.min(1, x)), d: x => (x > -1 && x < 1 ? 1 : 0) },
    relu: { n: 'ReLU', f: x => Math.max(0, x), d: x => (x > 0 ? 1 : 0) },
    leaky: { n: 'leaky ReLU', f: (x, a) => (x > 0 ? x : a * x), d: (x, a) => (x > 0 ? 1 : a) },
    swish: { n: 'swish', f: x => x * sig(x), d: x => sig(x) + x * sig(x) * (1 - sig(x)) },
    gelu: { n: 'GELU (approx.)', f: x => x * sig(1.702 * x), d: x => sig(1.702 * x) + 1.702 * x * sig(1.702 * x) * (1 - sig(1.702 * x)) }
  };
  def('activations', {
    title: 'Activation functions and their slopes',
    sub: 'The solid curve is f(z), the dashed curve is its slope f′(z). Learning needs the slope, so a flat region means no learning.',
    W: 560, H: 300,
    params: [
      { k: 'fn', label: 'Function', type: 'select', v: 'sigmoid', opts: Object.keys(ACTS).map(k => [k, ACTS[k].n]) },
      { k: 'cmp', label: 'Compare with', type: 'select', v: 'tanh', opts: [['none', 'nothing']].concat(Object.keys(ACTS).map(k => [k, ACTS[k].n])) },
      { k: 'z', label: 'Input z', v: 1, min: -6, max: 6, step: 0.05 },
      { k: 'a', label: 'Leaky slope a (leaky ReLU only)', v: 0.1, min: 0, max: 0.5, step: 0.01 },
      { k: 'deriv', label: 'Show the slope curve', type: 'check', v: true }
    ],
    tips: [
      { t: 'Sigmoid at z = 5: the output is 0.993 but the slope is only 0.0066. A saturated neuron barely learns.', set: { fn: 'sigmoid', z: 5, cmp: 'none' } },
      { t: 'Sigmoid against tanh: tanh is zero centred and twice as steep at 0 (slope 1 against 0.25), because tanh(z) = 2·sigmoid(2z) − 1.', set: { fn: 'sigmoid', cmp: 'tanh', z: 0 } },
      { t: 'ReLU at z = −2: output 0 and slope 0. If a neuron is always negative it never updates again, a dead neuron.', set: { fn: 'relu', z: -2, cmp: 'none' } },
      { t: 'Leaky ReLU with a = 0.1 keeps a small slope for negative inputs, so the neuron can recover.', set: { fn: 'leaky', z: -2, a: 0.1, cmp: 'relu' } },
      { t: 'GELU against ReLU: GELU bends smoothly and even lets small negative values through. Transformers like BERT use it.', set: { fn: 'gelu', cmp: 'relu', z: -0.5 } },
      { t: 'The threshold unit has slope 0 everywhere. Gradient descent gets no signal, which is why it was replaced.', set: { fn: 'step', cmp: 'sigmoid', z: 0.5 } }
    ],
    draw(z) {
      const { g, p } = z;
      const box = [52, 14, 330, 240], xr = [-6, 6], yr = [-1.5, 3];
      const m = D.axes(g, z, box, xr, yr, { nx: 6, ny: 3, xl: 'z' });
      D.line(g, m.sx(0), box[1], m.sx(0), box[1] + box[3], z.col.line, 1);
      D.line(g, box[0], m.sy(0), box[0] + box[2], m.sy(0), z.col.line, 1);
      const curve = (fn, c, dash) => {
        g.save(); g.beginPath(); g.rect(box[0], box[1], box[2], box[3]); g.clip();
        g.strokeStyle = c; g.lineWidth = 2.5; if (dash) g.setLineDash(dash); g.beginPath();
        for (let i = 0; i <= 240; i++) { const x = -6 + 12 * i / 240, y = fn(x); i ? g.lineTo(m.sx(x), m.sy(y)) : g.moveTo(m.sx(x), m.sy(y)); }
        g.stroke(); g.restore();
      };
      const A = ACTS[p.fn], B = ACTS[p.cmp];
      if (B) { curve(x => B.f(x, p.a), z.col.purple); if (p.deriv) curve(x => B.d(x, p.a), z.col.purple, [5, 4]); }
      curve(x => A.f(x, p.a), z.col.cv); if (p.deriv) curve(x => A.d(x, p.a), z.col.cv, [5, 4]);
      const fz = A.f(p.z, p.a), dz = A.d(p.z, p.a);
      D.circle(g, m.sx(p.z), m.sy(fz), 6, { fill: z.col.cv });
      if (p.deriv) D.circle(g, m.sx(p.z), m.sy(dz), 4.5, { fill: z.col.orange });
      const lx = 405;
      D.text(g, A.n, lx, 30, { s: 15, b: true, c: z.col.cv });
      D.text(g, `z = ${f2(p.z, 2)}`, lx, 56, { s: 12.5, mono: true, c: z.col.ink });
      D.text(g, `f(z) = ${f2(fz, 4)}`, lx, 78, { s: 12.5, mono: true, b: true, c: z.col.ink });
      D.text(g, `f′(z) = ${f2(dz, 4)}`, lx, 100, { s: 12.5, mono: true, b: true, c: z.col.orange });
      if (B) {
        D.text(g, B.n, lx, 140, { s: 14, b: true, c: z.col.purple });
        D.text(g, `f(z) = ${f2(B.f(p.z, p.a), 4)}`, lx, 162, { s: 12.5, mono: true, c: z.col.ink });
        D.text(g, `f′(z) = ${f2(B.d(p.z, p.a), 4)}`, lx, 184, { s: 12.5, mono: true, c: z.col.ink });
      }
      const note = dz < 0.01 ? 'The slope is almost zero here, so a weight feeding this neuron hardly changes.' : 'A healthy slope, so gradient descent can move the weights.';
      return `${note} Without any of these functions, two layers W1 and W2 collapse into one matrix W = W2·W1, so depth would add nothing.`;
    }
  });

  /* ================================================================ Step 2: word vectors */
  def('onehot', {
    title: 'One-hot vectors against dense word vectors',
    sub: 'Pick two words. One-hot vectors share no position, so their dot product is always 0. Dense vectors can be close or far.',
    W: 560, H: 300,
    params: [
      { k: 'vocab', label: 'Vocabulary (one word per line, then its dense vector)', type: 'area', v: 'hotel 0.8 0.6 0.1\nmotel 0.75 0.65 0.05\nbanking 0.1 0.2 0.9\nmonetary 0.15 0.1 0.85\nbanana -0.6 0.5 -0.2' },
      { k: 'a', label: 'First word (position in the list)', v: 1, min: 1, max: 8 },
      { k: 'b', label: 'Second word (position in the list)', v: 2, min: 1, max: 8 }
    ],
    tips: [
      { t: 'hotel and motel: one-hot dot product 0, dense cosine about 0.99. A search for "Seattle motel" can now find "Seattle hotel".', set: { a: 1, b: 2 } },
      { t: 'banking and monetary: also close in the dense space, because they appear in similar contexts.', set: { a: 3, b: 4 } },
      { t: 'hotel and banana: the dense cosine is negative, they are unrelated. The one-hot answer is still 0, the same as for hotel and motel.', set: { a: 1, b: 5 } },
      { t: 'Add a sixth line such as "inn 0.7 0.7 0.0" and compare it with hotel. One-hot vectors also grow by one place for every new word.', set: { vocab: 'hotel 0.8 0.6 0.1\nmotel 0.75 0.65 0.05\nbanking 0.1 0.2 0.9\nmonetary 0.15 0.1 0.85\nbanana -0.6 0.5 -0.2\ninn 0.7 0.7 0.0', a: 1, b: 6 } }
    ],
    draw(z) {
      const { g, p } = z;
      const V = rows(p.vocab).map(l => { const t = l.split(/\s+/); return [t[0], t.slice(1).map(Number).filter(v => !isNaN(v))]; });
      if (V.length < 2) return 'Write at least two words, each followed by its numbers.';
      const ia = Math.min(V.length, p.a) - 1, ib = Math.min(V.length, p.b) - 1, n = V.length;
      let y = 26;
      D.text(g, 'One-hot (size = vocabulary)', 16, y, { s: 13, b: true, c: z.col.ink });
      [ia, ib].forEach((k, r) => {
        y += 30;
        D.text(g, V[k][0], 16, y + 14, { s: 12.5, b: true, c: r ? z.col.purple : z.col.cv });
        const cw = Math.min(26, 230 / n);
        for (let j = 0; j < n; j++) { rr(g, 96 + j * cw, y, cw - 4, 22, 4, { fill: j === k ? (r ? z.col.purple : z.col.cv) : z.col.bg, stroke: z.col.line, w: 1 }); D.text(g, j === k ? '1' : '0', 96 + j * cw + (cw - 4) / 2, y + 15, { a: 'center', s: Math.min(11, cw * 0.5), b: true, c: j === k ? '#fff' : z.col.ink2 }); }
      });
      const ohdot = ia === ib ? 1 : 0;
      D.text(g, `dot product = ${ohdot}`, 16, y + 46, { s: 12, mono: true, c: z.col.ink });
      D.text(g, ia === ib ? 'the same word' : 'orthogonal: no notion of similarity', 16, y + 64, { s: 11.5, c: z.col.ink2 });
      const va = V[ia][1], vb = V[ib][1];
      y += 96;
      D.text(g, 'Dense vectors (learned from context)', 16, y, { s: 13, b: true, c: z.col.ink });
      D.text(g, `${V[ia][0]} = ${vstr(va, 2)}`, 16, y + 24, { s: 12, mono: true, c: z.col.cv });
      D.text(g, `${V[ib][0]} = ${vstr(vb, 2)}`, 16, y + 44, { s: 12, mono: true, c: z.col.purple });
      const c = cos(va, vb);
      D.text(g, `dot = ${f2(dot(va, vb), 3)}   cosine = ${f2(c, 3)}`, 16, y + 70, { s: 13, mono: true, b: true, c: z.col.ink });
      const pts = pca2(V.map(v => v[1].length ? v[1] : [0, 0]));
      scatter(g, z, [360, 20, 180, 230], pts, V.map(v => v[0]), { colors: V.map((_, i) => i === ia ? z.col.cv : i === ib ? z.col.purple : z.col.ink2) });
      return `Cosine similarity = a·b ÷ (‖a‖ ‖b‖) = <b>${f2(c, 3)}</b>. One-hot vectors cannot say that ${esc(V[ia][0])} is ${c > 0.8 ? 'close to' : 'far from'} ${esc(V[ib][0])}. The picture on the right shows the dense vectors squeezed to two dimensions.`;
    }
  });

  def('sgwindow', {
    title: 'Sliding the context window: skip-gram training pairs',
    sub: 'Every word takes a turn as the centre word. Each neighbour within the window makes one (centre, context) pair.',
    W: 560, H: 270,
    params: [
      { k: 'text', label: 'Sentence', type: 'text', v: 'problems turning into banking crises as' },
      { k: 'm', label: 'Window size m (words on each side)', v: 2, min: 1, max: 4 }
    ],
    tips: [
      { t: 'The slide sentence with m = 2. Press Play and watch "banking" collect into, turning, crises and as.', set: { text: 'problems turning into banking crises as', m: 2 }, play: true },
      { t: 'The notebook sentence "cats like milk" with m = 1 gives 4 pairs. All five notebook sentences give 20.', set: { text: 'cats like milk', m: 1 }, play: true },
      { t: 'The class question: 8 words, m = 2. Count the pairs: edge words lose neighbours, so the answer is 26, not 32.', set: { text: 'w1 w2 w3 w4 w5 w6 w7 w8', m: 2 }, play: true },
      { t: 'Make the window wider. Pairs grow quickly and far words count as context too, which brings in more topic and less syntax.', set: { m: 4 } }
    ],
    startAtZero: true,
    steps: z => String(z.p.text).trim().split(/\s+/).filter(Boolean).length,
    speed: () => 900,
    draw(z) {
      const { g, p } = z;
      const w = String(p.text).trim().split(/\s+/).filter(Boolean).slice(0, 14);
      if (!w.length) return 'Type a sentence.';
      const t = Math.max(0, z.step - 1);
      const pos = []; let x = 16;
      w.forEach((s, i) => { const wd = tw(g, s, { s: 13, b: true }) + 16; if (x + wd > 544) x = 544 - wd; pos.push([x, wd]); x += wd + 6; });
      const total = w.reduce((a, _, i) => a + Math.min(w.length - 1, i + p.m) - Math.max(0, i - p.m), 0);
      const fitAll = pos[pos.length - 1][0] + pos[pos.length - 1][1] <= 544;
      const sc = fitAll ? 1 : 528 / (pos[pos.length - 1][0] + pos[pos.length - 1][1]);
      w.forEach((s, i) => {
        const inWin = z.step > 0 && i !== t && Math.abs(i - t) <= p.m, isC = z.step > 0 && i === t;
        pill(g, s, 16 + (pos[i][0] - 16) * sc, 40, { s: 13 * Math.min(1, sc + 0.1), b: true, fill: isC ? z.col.cv : inWin ? z.col.orange : z.col.bg, stroke: z.col.line, c: isC || inWin ? '#fff' : z.col.ink });
      });
      if (z.step > 0) {
        D.text(g, 'centre', 16 + (pos[t][0] - 16) * sc, 28, { s: 11, b: true, c: z.col.cv });
        const pairs = [];
        for (let j = Math.max(0, t - p.m); j <= Math.min(w.length - 1, t + p.m); j++) if (j !== t) pairs.push(`(${w[t]}, ${w[j]})  offset ${j - t > 0 ? '+' : ''}${j - t}`);
        D.text(g, `Pairs for centre word "${w[t]}":`, 16, 100, { s: 13, b: true, c: z.col.ink });
        pairs.forEach((s, i) => D.text(g, s, 30 + (i % 2) * 260, 124 + Math.floor(i / 2) * 20, { s: 12, mono: true, c: z.col.ink }));
      } else D.text(g, 'Press Step or Play to slide the window.', 16, 110, { s: 13, c: z.col.ink2 });
      let done = 0; for (let i = 0; i < Math.min(z.step, w.length); i++) done += Math.min(w.length - 1, i + p.m) - Math.max(0, i - p.m);
      D.text(g, `pairs so far ${done} of ${total}`, 16, 250, { s: 13, b: true, c: z.col.cv });
      return `With T words and window m, a middle word makes 2m pairs. Words near the ends make fewer. This sentence of ${w.length} words gives <b>${total}</b> pairs, at most 2m × T = ${2 * p.m * w.length}.`;
    }
  });

  /* the class notebook: skip-gram on five tiny sentences */
  const NB = 'cats like milk\ncats drink milk\ndogs like milk\ndogs chase balls\ncats chase balls';
  function corpusPairs(text, m) {
    const sents = rows(text).map(s => s.toLowerCase().split(/\s+/).filter(Boolean));
    const vocab = [...new Set(sents.flat())].sort();
    const id = Object.fromEntries(vocab.map((v, i) => [v, i]));
    const pairs = [], counts = Array(vocab.length).fill(0);
    sents.forEach(s => s.forEach((wd, i) => { counts[id[wd]]++; for (let j = Math.max(0, i - m); j <= Math.min(s.length - 1, i + m); j++) if (j !== i) pairs.push([id[wd], id[s[j]]]); }));
    return { vocab, pairs, counts, sents };
  }
  function trainSG(o) {
    const { vocab, pairs, counts } = corpusPairs(o.text, o.m), V = vocab.length, d = o.d, r = rng(o.seed);
    const E = Array.from({ length: V }, () => Array.from({ length: d }, () => gauss(r) * 0.1));
    const W = Array.from({ length: V }, () => Array.from({ length: d }, () => gauss(r) * 0.1)); /* one output vector per word */
    const negP = counts.map(c => c ** o.alpha), ns = negP.reduce((a, b) => a + b, 0);
    const draw = () => { let u = r() * ns; for (let i = 0; i < V; i++) { u -= negP[i]; if (u <= 0) return i; } return V - 1; };
    const losses = [], P = pairs.slice();
    for (let ep = 0; ep < o.epochs; ep++) {
      for (let i = P.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [P[i], P[j]] = [P[j], P[i]]; }
      let tot = 0;
      P.forEach(([c, ctx]) => {
        const h = E[c].slice();
        if (o.mode === 'softmax') {
          const pr = softmax(W.map(u => dot(h, u)));
          tot += -Math.log(pr[ctx] + 1e-12);
          const err = pr.map((v, k) => v - (k === ctx ? 1 : 0));
          const gh = Array(d).fill(0);
          W.forEach((u, k) => { for (let a = 0; a < d; a++) { gh[a] += u[a] * err[k]; u[a] -= o.lr * h[a] * err[k]; } });
          for (let a = 0; a < d; a++) E[c][a] -= o.lr * gh[a];
        } else {
          const tg = [[ctx, 1]]; let guard = 0;
          while (tg.length < o.K + 1 && guard++ < 100) { const n = draw(); if (n !== ctx) tg.push([n, 0]); }
          const gh = Array(d).fill(0);
          tg.forEach(([k, lab]) => {
            const s = sig(dot(h, W[k])); tot += lab ? -Math.log(s + 1e-12) : -Math.log(1 - s + 1e-12);
            const e = s - lab;
            for (let a = 0; a < d; a++) { gh[a] += e * W[k][a]; W[k][a] -= o.lr * e * h[a]; }
          });
          for (let a = 0; a < d; a++) E[c][a] -= o.lr * gh[a];
        }
      });
      losses.push(tot / P.length);
    }
    return { vocab, E, W, losses, pairs };
  }
  def('w2vtrain', {
    title: 'Train word2vec on the class notebook corpus',
    sub: 'Each dot is a word vector E[word], drawn in 2D. Words that share neighbours drift together while training. The small chart is the average loss per epoch.',
    W: 560, H: 330,
    params: [
      { k: 'mode', label: 'Loss', type: 'select', v: 'softmax', opts: [['softmax', 'full softmax (notebook part 1)'], ['neg', 'negative sampling (notebook part 2)']] },
      { k: 'epochs', label: 'Epochs', v: 500, min: 0, max: 1000, step: 10 },
      { k: 'lr', label: 'Learning rate η', v: 0.05, min: 0.005, max: 0.3, step: 0.005 },
      { k: 'd', label: 'Embedding size d', v: 3, min: 2, max: 8 },
      { k: 'm', label: 'Window size', v: 1, min: 1, max: 3 },
      { k: 'K', label: 'Negative samples K', v: 3, min: 1, max: 6, show: p => p.mode === 'neg' },
      { k: 'alpha', label: 'Sampling power α in U(w)^α', v: 0.75, min: 0, max: 1, step: 0.05, show: p => p.mode === 'neg' },
      { k: 'seed', label: 'Random seed', v: 42, min: 1, max: 99 },
      { k: 'probe', label: 'Show neighbours of', type: 'text', v: 'cats' },
      { k: 'text', label: 'Corpus, one sentence per line', type: 'area', v: NB }
    ],
    tips: [
      { t: 'The notebook settings: full softmax, 500 epochs, η = 0.05, d = 3, window 1. Look for which words end up near cats.', set: { mode: 'softmax', epochs: 500, lr: 0.05, d: 3, m: 1, seed: 42 } },
      { t: 'Switch to negative sampling with K = 3. In the notebook cats and dogs then became the closest pair (cosine 0.98). Check the readout.', set: { mode: 'neg', K: 3, alpha: 0.75 } },
      { t: 'Set epochs to 0. Every vector is still tiny random noise near the centre, so neighbours mean nothing yet.', set: { epochs: 0 } },
      { t: 'Use d = 2 so the picture is the real vectors and not a projection.', set: { d: 2 } },
      { t: 'Change the seed. The exact numbers change but the groups stay, which is what a learned meaning should do.', set: { seed: 7 } },
      { t: 'Add the line "dogs drink milk" to the corpus. Now dogs share even more contexts with cats.', set: { text: NB + '\ndogs drink milk' } }
    ],
    draw(z) {
      const { g, p } = z;
      const r = trainSG({ text: p.text, m: p.m, d: p.d, lr: p.lr, epochs: p.epochs, seed: p.seed, mode: p.mode, K: p.K, alpha: p.alpha });
      if (r.vocab.length < 2) return 'Write a few sentences.';
      const pts = pca2(r.E);
      scatter(g, z, [52, 14, 300, 270], pts, r.vocab, { zero: true });
      const cb = [390, 22, 160, 90];
      D.rect(g, cb[0], cb[1], cb[2], cb[3], { stroke: z.col.line, w: 1 });
      D.text(g, 'loss per epoch', cb[0], cb[1] - 6, { s: 11, b: true, c: z.col.ink2 });
      if (r.losses.length > 1) {
        const mx = Math.max(...r.losses), mn = Math.min(...r.losses);
        g.strokeStyle = z.col.cv; g.lineWidth = 2; g.beginPath();
        r.losses.forEach((l, i) => { const x = cb[0] + i / (r.losses.length - 1) * cb[2], y = cb[1] + cb[3] - (l - mn) / (mx - mn || 1) * (cb[3] - 6) - 3; i ? g.lineTo(x, y) : g.moveTo(x, y); });
        g.stroke();
        D.text(g, `${f2(r.losses[0], 3)} → ${f2(r.losses[r.losses.length - 1], 3)}`, cb[0], cb[1] + cb[3] + 16, { s: 11.5, mono: true, b: true, c: z.col.ink });
      }
      const pi = r.vocab.indexOf(String(p.probe).trim().toLowerCase());
      let out = '';
      if (pi >= 0) {
        const sims = r.vocab.map((w, j) => [w, cos(r.E[pi], r.E[j])]).filter((_, j) => j !== pi).sort((a, b) => b[1] - a[1]).slice(0, 3);
        D.text(g, `nearest to ${r.vocab[pi]}:`, 390, 156, { s: 12.5, b: true, c: z.col.ink });
        sims.forEach(([w, s], i) => D.text(g, `${w}  ${f2(s, 3)}`, 400, 178 + i * 19, { s: 12, mono: true, c: z.col.ink }));
        out = `Cosine neighbours of <b>${esc(r.vocab[pi])}</b>: ${sims.map(s => `${esc(s[0])} ${f2(s[1], 3)}`).join(', ')}. `;
      }
      D.text(g, `${r.pairs.length} pairs, V = ${r.vocab.length}`, 390, 260, { s: 11.5, c: z.col.ink2 });
      D.text(g, p.d > 2 ? `drawn with PCA from ${p.d}D` : 'drawn as the real 2D vectors', 390, 278, { s: 11.5, c: z.col.ink2 });
      return out + (p.mode === 'softmax' ? 'Full softmax scores every word in the vocabulary for every pair.' : `Negative sampling scores only 1 + K = ${1 + p.K} words per pair with a sigmoid.`) + ' This runs the notebook algorithm in your browser with its own random numbers, so the values differ from the notebook printout but the behaviour is the same.';
    }
  });

  def('sgstep', {
    title: 'One skip-gram step with full softmax, number by number',
    sub: 'Centre vector h = E[centre]. Scores s = h·W for every word. Softmax turns scores into probabilities. The error p − y drives the update.',
    W: 560, H: 320,
    params: [
      { k: 'E', label: 'Input vectors E, one row per word "word x y"', type: 'area', v: 'cats 0.2 0.1\nlike 0.0 0.3\nmilk 0.4 -0.1\ndogs 0.1 0.2' },
      { k: 'W', label: 'Output vectors U, one row per word (same order)', type: 'area', v: '0.1 0.3\n0.5 -0.2\n0.2 0.4\n-0.3 0.1' },
      { k: 'c', label: 'Centre word (row number)', v: 1, min: 1, max: 6 },
      { k: 'o', label: 'True context word (row number)', v: 2, min: 1, max: 6 },
      { k: 'lr', label: 'Learning rate η', v: 0.5, min: 0, max: 2, step: 0.05 }
    ],
    tips: [
      { t: 'Centre cats, context like. Read the four probabilities, then the loss −log p(like | cats).', set: { c: 1, o: 2 } },
      { t: 'Set η = 0. Nothing moves. Then η = 1: the updated probability of "like" goes up, which is the whole point of the step.', set: { lr: 1 } },
      { t: 'Make context = centre (row 1 and row 1). Word2vec never makes that pair, because the window skips the centre itself.', set: { o: 1 } },
      { t: 'Multiply one output vector by 10 (for example row 3 to "2 4"). Large scores make softmax almost one-hot.', set: { W: '0.1 0.3\n0.5 -0.2\n2 4\n-0.3 0.1' } }
    ],
    draw(z) {
      const { g, p } = z;
      const E = rows(p.E).map(l => { const t = l.split(/\s+/); return [t[0], t.slice(1).map(Number)]; });
      const U = vecs(p.W);
      const V = Math.min(E.length, U.length);
      if (V < 2) return 'Give at least two words in both boxes.';
      const c = Math.min(V, p.c) - 1, o = Math.min(V, p.o) - 1, h = E[c][1];
      const s = U.slice(0, V).map(u => dot(h, u)), pr = softmax(s);
      const loss = -Math.log(pr[o]);
      const err = pr.map((v, k) => v - (k === o ? 1 : 0));
      const gh = h.map((_, a) => U.slice(0, V).reduce((acc, u, k) => acc + u[a] * err[k], 0));
      const h2 = h.map((v, a) => v - p.lr * gh[a]);
      const U2 = U.slice(0, V).map((u, k) => u.map((v, a) => v - p.lr * h[a] * err[k]));
      const pr2 = softmax(U2.map(u => dot(h2, u)));
      const names = E.slice(0, V).map(e => e[0]);
      D.text(g, `h = E[${names[c]}] = ${vstr(h, 2)}`, 16, 22, { s: 12.5, mono: true, b: true, c: z.col.cv });
      D.text(g, 'word', 16, 50, { s: 11.5, b: true, c: z.col.ink2 });
      ['score h·u', 'p before', 'p − y', 'p after'].forEach((t, i) => D.text(g, t, 110 + i * 92, 50, { s: 11.5, b: true, c: z.col.ink2 }));
      names.forEach((n, k) => {
        const y = 74 + k * 24;
        if (k === o) rr(g, 10, y - 16, 470, 22, 5, { fill: z.col.cv + '22' });
        D.text(g, n + (k === o ? '  (context)' : ''), 16, y, { s: 12, b: k === o, c: z.col.ink });
        [s[k], pr[k], err[k], pr2[k]].forEach((v, i) => D.text(g, f2(v, 4), 110 + i * 92, y, { s: 12, mono: true, c: i === 3 ? z.col.green : z.col.ink }));
      });
      const y0 = 74 + V * 24 + 14;
      D.text(g, `loss = −log p(${names[o]} | ${names[c]}) = −log ${f2(pr[o], 4)} = ${f2(loss, 4)}`, 16, y0, { s: 12.5, mono: true, b: true, c: z.col.ink });
      D.text(g, `∂J/∂h = U·(p − y) = ${vstr(gh, 4)}`, 16, y0 + 22, { s: 12, mono: true, c: z.col.ink });
      D.text(g, `new h = h − η ∂J/∂h = ${vstr(h2, 4)}`, 16, y0 + 44, { s: 12, mono: true, c: z.col.ink });
      D.text(g, `new loss = ${f2(-Math.log(pr2[o]), 4)}`, 16, y0 + 66, { s: 12.5, mono: true, b: true, c: z.col.green });
      return `Softmax: p(o | c) = exp(u<sub>o</sub>·v<sub>c</sub>) ÷ ∑<sub>w</sub> exp(u<sub>w</sub>·v<sub>c</sub>). The denominator touches every word, so with V = 100,000 one step costs 100,000 dot products. That cost is why negative sampling exists.`;
    }
  });

  def('negsample', {
    title: 'Which words become negative samples',
    sub: 'Negatives are drawn from the unigram distribution raised to the power α and renormalised. α = 0.75 lifts rare words and tames very common ones.',
    W: 560, H: 300,
    params: [
      { k: 'counts', label: 'Word counts, one "word count" per line', type: 'area', v: 'the 1000\nof 600\nbank 40\nriver 20\nskillet 5\naardvark 1' },
      { k: 'alpha', label: 'Power α', v: 0.75, min: 0, max: 1, step: 0.05 },
      { k: 'K', label: 'Negatives to draw K', v: 5, min: 1, max: 15 },
      { k: 'seed', label: 'Random seed for the draw', v: 3, min: 1, max: 99 }
    ],
    tips: [
      { t: 'α = 1 is the plain unigram distribution. "the" and "of" take almost every draw, and they tell the model very little.', set: { alpha: 1 } },
      { t: 'α = 0.75, the word2vec choice. "the" falls and the rare words rise. Compare the two bar colours.', set: { alpha: 0.75 } },
      { t: 'α = 0 makes every word equally likely. Very rare words are now oversampled.', set: { alpha: 0 } },
      { t: 'The notebook counts: cats 3, like 2, milk 3, drink 1, dogs 2, chase 2, balls 2. With α = 0.75 the rarest word, drink, rises from 0.067 to 0.081 and the commonest fall a little.', set: { counts: 'balls 2\ncats 3\nchase 2\ndogs 2\ndrink 1\nlike 2\nmilk 3', alpha: 0.75 } },
      { t: 'Draw more negatives with K = 15 and change the seed a few times to see the spread.', set: { K: 15, seed: 11 } }
    ],
    draw(z) {
      const { g, p } = z;
      const C = NLZ.pairs(p.counts).filter(r => r[1] > 0).slice(0, 9);
      if (!C.length) return 'Write lines like "the 1000".';
      const tot = C.reduce((a, r) => a + r[1], 0), pa = C.map(r => r[1] ** p.alpha), ts = pa.reduce((a, b) => a + b, 0);
      const U = C.map(r => r[1] / tot), Pn = pa.map(v => v / ts);
      const box = [40, 20, 330, 220], n = C.length, bw = box[2] / n, mx = Math.max(...U, ...Pn);
      D.line(g, box[0], box[1] + box[3], box[0] + box[2], box[1] + box[3], z.col.line, 1);
      C.forEach((r, i) => {
        const x = box[0] + i * bw, h1 = U[i] / mx * (box[3] - 20), h2 = Pn[i] / mx * (box[3] - 20);
        rr(g, x + bw * 0.1, box[1] + box[3] - h1, bw * 0.38, h1, 3, { fill: z.col.ink2 });
        rr(g, x + bw * 0.52, box[1] + box[3] - h2, bw * 0.38, h2, 3, { fill: z.col.cv });
        D.text(g, f2(Pn[i], 3), x + bw * 0.71, box[1] + box[3] - h2 - 4, { a: 'center', s: 10, b: true, c: z.col.cv });
        D.text(g, r[0], x + bw / 2, box[1] + box[3] + 15, { a: 'center', s: fit(g, r[0], bw - 2, 11.5), b: true, c: z.col.ink });
      });
      D.rect(g, box[0], 262, 10, 10, { fill: z.col.ink2 }); D.text(g, 'U(w)', box[0] + 14, 271, { s: 11.5, c: z.col.ink2 });
      D.rect(g, box[0] + 70, 262, 10, 10, { fill: z.col.cv }); D.text(g, `U(w)^${f2(p.alpha, 2)} ÷ Z`, box[0] + 84, 271, { s: 11.5, c: z.col.ink2 });
      const r = rng(p.seed), drawn = [];
      for (let k = 0; k < p.K; k++) { let u = r(), i = 0; while (i < n - 1 && u > Pn[i]) { u -= Pn[i]; i++; } drawn.push(C[i][0]); }
      D.text(g, `K = ${p.K} draws:`, 392, 30, { s: 12.5, b: true, c: z.col.ink });
      wrap(g, drawn.join(', '), 392, 52, 160, { s: 12, mono: true, c: z.col.ink });
      return `P<sub>n</sub>(w) = U(w)<sup>α</sup> ÷ ∑ U(w′)<sup>α</sup>. For "${esc(C[0][0])}" the share moves from ${f2(U[0], 3)} to ${f2(Pn[0], 3)}${C.length > 1 ? ` and for "${esc(C[n - 1][0])}" from ${f2(U[n - 1], 4)} to ${f2(Pn[n - 1], 4)}` : ''}.`;
    }
  });

  def('sgns', {
    title: 'Negative sampling: one true pair against K noise pairs',
    sub: 'Pull σ(u_o·v_c) toward 1 for the true context and push σ(u_k·v_c) toward 0 for each noise word. Only 1 + K output vectors change.',
    W: 560, H: 300,
    params: [
      { k: 'pos', label: 'Score of the true pair u_o·v_c', v: 1.0, min: -6, max: 6, step: 0.1 },
      { k: 'negs', label: 'Scores of the K noise pairs, separated by spaces', type: 'text', v: '0.5 -1 2' },
      { k: 'ctx', label: 'Context words around the centre (for counting sigmoids)', v: 4, min: 1, max: 10 }
    ],
    tips: [
      { t: 'A good model: true score 4, noise scores −3. The loss is small because σ(4) ≈ 0.98 and σ(3) ≈ 0.95 for each noise term.', set: { pos: 4, negs: '-3 -3 -3' } },
      { t: 'A confused model: true score −2, noise score 3. The loss is large and the gradients are strong.', set: { pos: -2, negs: '3 3 3' } },
      { t: 'The class question: K = 10 and window 2 (4 context words). Sigmoids per centre word = (1 + 10) × 4 = 44.', set: { negs: '0 0 0 0 0 0 0 0 0 0', ctx: 4 } },
      { t: 'Compare the cost with full softmax: for V = 10,000 each pair needs 10,000 exponentials, here only 1 + K sigmoids.', set: { negs: '0.5 -1 2 0 1', ctx: 4 } }
    ],
    draw(z) {
      const { g, p } = z;
      const N = nums(p.negs).slice(0, 12);
      const terms = [['true', sig(p.pos), -Math.log(sig(p.pos))]].concat(N.map((s, i) => [`noise ${i + 1}`, sig(-s), -Math.log(sig(-s))]));
      const loss = terms.reduce((a, t) => a + t[2], 0);
      const box = [40, 24, 330, 200];
      bars(g, z, box, terms.map(t => t[2]), terms.map(t => t[0]), { colors: terms.map((_, i) => i ? z.col.purple : z.col.cv), fmt: v => fmt(v, 3) });
      D.text(g, 'loss of each term', box[0], 16, { s: 11.5, b: true, c: z.col.ink2 });
      const lx = 392;
      D.text(g, `σ(u_o·v_c) = ${f2(sig(p.pos), 4)}`, lx, 40, { s: 12, mono: true, c: z.col.cv });
      N.slice(0, 5).forEach((s, i) => D.text(g, `σ(−u_${i + 1}·v_c) = ${f2(sig(-s), 4)}`, lx, 62 + i * 20, { s: 12, mono: true, c: z.col.purple }));
      D.text(g, `J = ${f2(loss, 4)}`, lx, 180, { s: 15, b: true, c: z.col.ink });
      D.text(g, `sigmoids per centre`, lx, 214, { s: 12, b: true, c: z.col.ink2 });
      D.text(g, `= (1 + ${N.length}) × ${p.ctx} = ${(1 + N.length) * p.ctx}`, lx, 234, { s: 13, mono: true, b: true, c: z.col.cv });
      return `J<sub>neg</sub> = −log σ(u<sub>o</sub>·v<sub>c</sub>) − ∑<sub>k</sub> log σ(−u<sub>k</sub>·v<sub>c</sub>) = <b>${f2(loss, 4)}</b>. Using σ(−x) = 1 − σ(x), each noise term rewards a low score.`;
    }
  });

  function cooc(text, m, mode, sym) {
    const sents = rows(text).map(s => s.split(/\s+/).filter(Boolean));
    const vocab = []; sents.flat().forEach(w => { if (!vocab.includes(w)) vocab.push(w); });
    const id = Object.fromEntries(vocab.map((v, i) => [v, i])), n = vocab.length;
    const X = Array.from({ length: n }, () => Array(n).fill(0));
    sents.forEach(s => s.forEach((w, i) => {
      for (let j = Math.max(0, i - m); j <= Math.min(s.length - 1, i + m); j++) {
        if (j === i || (!sym && j < i)) continue;
        X[id[w]][id[s[j]]] += mode === 'inv' ? 1 / Math.abs(i - j) : 1;
      }
    }));
    return { vocab, X };
  }
  def('cooc', {
    title: 'Build a window co-occurrence matrix',
    sub: 'Row word i, column word j: how often j appears within the window of i. Darker cells hold bigger counts.',
    W: 560, H: 330,
    params: [
      { k: 'text', label: 'Corpus, one sentence per line', type: 'area', v: 'I like deep learning .\nI like NLP .\nI enjoy flying .' },
      { k: 'm', label: 'Window size', v: 1, min: 1, max: 4 },
      { k: 'mode', label: 'Each neighbour adds', type: 'select', v: 'one', opts: [['one', '1 (plain count)'], ['inv', '1 ÷ distance (GloVe notebook)']] },
      { k: 'sym', label: 'Symmetric (count left and right)', type: 'check', v: true },
      { k: 'logx', label: 'Show log(1 + X) instead of X', type: 'check', v: false }
    ],
    tips: [
      { t: 'The slide corpus with window 1. Check the row "I": like 2, enjoy 1. The row "like": I 2, deep 1, NLP 1.', set: { text: 'I like deep learning .\nI like NLP .\nI enjoy flying .', m: 1, mode: 'one', sym: true } },
      { t: 'Window 2 with 1 ÷ distance, as the GloVe notebook does. A word two places away adds 0.5.', set: { m: 2, mode: 'inv' } },
      { t: 'Untick symmetric. Only right neighbours count, so the matrix is no longer equal to its transpose.', set: { sym: false } },
      { t: 'Load the ice and steam sentences from the GloVe notebook and look at which words share columns.', set: { text: 'ice is solid\nice melts in water\nsteam is a gas\nwater turns into steam\nice and water are related\nsteam and gas are related', m: 2, mode: 'inv', sym: true } }
    ],
    draw(z) {
      const { g, p } = z;
      const { vocab, X } = cooc(p.text, p.m, p.mode, p.sym);
      const n = Math.min(vocab.length, 14);
      if (!n) return 'Write some sentences.';
      const cell = Math.min(30, Math.floor(260 / n)), x0 = 100, y0 = 70;
      const mx = Math.max(1e-9, ...X.flat());
      for (let i = 0; i < n; i++) {
        D.text(g, vocab[i], x0 - 6, y0 + i * cell + cell / 2 + 4, { a: 'right', s: fit(g, vocab[i], 90, 11.5), b: true, c: z.col.ink });
        g.save(); g.translate(x0 + i * cell + cell / 2 + 4, y0 - 6); g.rotate(-Math.PI / 3); D.text(g, vocab[i], 0, 0, { s: fit(g, vocab[i], 70, 11), b: true, c: z.col.ink }); g.restore();
        for (let j = 0; j < n; j++) {
          const v = p.logx ? Math.log(1 + X[i][j]) : X[i][j], t = (p.logx ? v / Math.log(1 + mx) : v / mx);
          g.fillStyle = z.col.dark ? `rgba(251,146,60,${0.06 + t * 0.8})` : `rgba(194,65,12,${0.04 + t * 0.75})`;
          g.fillRect(x0 + j * cell, y0 + i * cell, cell - 1, cell - 1);
          if (X[i][j] && cell >= 18) D.text(g, f2(v, v % 1 ? 2 : 0), x0 + j * cell + cell / 2, y0 + i * cell + cell / 2 + 4, { a: 'center', s: Math.min(11, cell * 0.4), b: true, c: t > 0.5 ? '#fff' : z.col.ink });
        }
      }
      const nz = X.flat().filter(v => v).length;
      return `${vocab.length} words give a ${vocab.length} × ${vocab.length} matrix with ${nz} non-zero cells (${f2(100 * nz / (vocab.length ** 2), 1)} percent). Real vocabularies are 100,000 words wide, which is why the matrix is reduced with SVD or modelled by GloVe.`;
    }
  });

  def('glove', {
    title: 'GloVe: the weighting function and the probability ratio',
    sub: 'Left: f(X) decides how much each pair counts in the loss. Right: the ratio P(k | ice) ÷ P(k | steam) shows which probe words carry meaning.',
    W: 560, H: 300,
    params: [
      { k: 'xmax', label: 'x_max (where f stops growing)', v: 100, min: 1, max: 200 },
      { k: 'alpha', label: 'Power α', v: 0.75, min: 0.1, max: 1.5, step: 0.05 },
      { k: 'x', label: 'A count X_ij to check', v: 20, min: 0, max: 250 },
      { k: 'ratio', label: 'Probe words: "word P(k|ice) P(k|steam)"', type: 'area', v: 'solid 0.00019 0.000022\ngas 0.000066 0.00078\nwater 0.003 0.0022\nfashion 0.000017 0.000018' }
    ],
    tips: [
      { t: 'The paper values x_max = 100 and α = 0.75. A pair seen 20 times gets weight 0.30, a pair seen 500 times is capped at 1.', set: { xmax: 100, alpha: 0.75, x: 20 } },
      { t: 'The notebook used x_max = 10. Most counts in a tiny corpus are below 10, so most pairs get less than full weight.', set: { xmax: 10, x: 2 } },
      { t: 'α = 1 makes f a straight ramp, α below 1 lifts small counts. Compare the curve at x = 5.', set: { alpha: 1, x: 5 } },
      { t: 'Read the ratio bars: solid is about 8.6 with these rounded numbers (8.9 in the paper), gas about 0.085 (a steam word), water and fashion near 1 (no help telling them apart).', set: { xmax: 100 } }
    ],
    draw(z) {
      const { g, p } = z;
      const f = x => (x < p.xmax ? (x / p.xmax) ** p.alpha : 1);
      const box = [52, 16, 230, 210], top = Math.max(250, p.xmax * 1.3);
      const m = D.axes(g, z, box, [0, top], [0, 1.1], { nx: 4, ny: 2, xl: 'X_ij', yl: 'f(X_ij)', fx: v => fmt(v, 0) });
      g.strokeStyle = z.col.cv; g.lineWidth = 2.5; g.beginPath();
      for (let i = 0; i <= 200; i++) { const x = top * i / 200; i ? g.lineTo(m.sx(x), m.sy(f(x))) : g.moveTo(m.sx(x), m.sy(f(x))); }
      g.stroke();
      D.circle(g, m.sx(Math.min(top, p.x)), m.sy(f(p.x)), 6, { fill: z.col.orange });
      D.text(g, `f(${p.x}) = ${f2(f(p.x), 3)}`, box[0] + 6, box[1] + 18, { s: 12.5, mono: true, b: true, c: z.col.orange });
      const R = rows(p.ratio).map(l => l.split(/\s+/)).filter(t => t.length >= 3).map(t => [t[0], +t[1] / +t[2]]).slice(0, 6);
      if (R.length) {
        const bx = 320, by = 40, bw = 220, rh = 32, lmax = Math.max(...R.map(r => Math.abs(Math.log10(r[1]))), 1);
        D.line(g, bx + bw / 2, by - 10, bx + bw / 2, by + R.length * rh, z.col.ink2, 1.5, [4, 3]);
        D.text(g, 'more ice', bx + bw - 2, by - 16, { a: 'right', s: 11, b: true, c: z.col.cv });
        D.text(g, 'more steam', bx, by - 16, { s: 11, b: true, c: z.col.purple });
        R.forEach(([w, r], i) => {
          const l = Math.log10(r), len = l / lmax * (bw / 2 - 6), y = by + i * rh;
          rr(g, Math.min(bx + bw / 2, bx + bw / 2 + len), y, Math.abs(len), 18, 3, { fill: l > 0 ? z.col.cv : z.col.purple });
          D.text(g, `${w}  ${f2(r, r < 0.1 ? 3 : 2)}`, bx + bw / 2 + (l > 0 ? -6 : 6), y + 13, { a: l > 0 ? 'right' : 'left', s: 11.5, b: true, c: z.col.ink });
        });
      }
      return `f(x) = (x ÷ x<sub>max</sub>)<sup>α</sup> below x<sub>max</sub>, else 1, and f(0) = 0, so never-seen pairs drop out. Loss J = ∑ f(X<sub>ij</sub>)(w<sub>i</sub>·w̃<sub>j</sub> + b<sub>i</sub> + b̃<sub>j</sub> − log X<sub>ij</sub>)².`;
    }
  });

  def('analogy', {
    title: 'Analogies by vector arithmetic',
    sub: 'a is to b as c is to ?: compute b − a + c and pick the nearest word by cosine (the three input words are left out).',
    W: 560, H: 320,
    params: [
      { k: 'vocab', label: 'Toy 2D vectors, "word x y" per line', type: 'area', v: 'man 1 1\nwoman 1 3\nking 4 1.2\nqueen 4 3.2\nprince 3.4 0.8\napple -2 -1' },
      { k: 'a', label: 'a', type: 'text', v: 'man' },
      { k: 'b', label: 'b', type: 'text', v: 'king' },
      { k: 'c', label: 'c', type: 'text', v: 'woman' }
    ],
    tips: [
      { t: 'man : king :: woman : ? The arrow man to king is copied to start at woman and lands on queen.', set: { a: 'man', b: 'king', c: 'woman' } },
      { t: 'Reverse it: king : man :: queen : ? The answer is woman.', set: { a: 'king', b: 'man', c: 'queen' } },
      { t: 'Move queen to "queen 2 3" and run the first analogy again. The nearest word changes. Real embeddings are only roughly parallel.', set: { vocab: 'man 1 1\nwoman 1 3\nking 4 1.2\nqueen 2 3\nprince 3.4 0.8\napple -2 -1', a: 'man', b: 'king', c: 'woman' } },
      { t: 'The bias example from the lecture works the same way. If text says programmer near man more often, the arithmetic copies the stereotype.', set: { vocab: 'man 1 1\nwoman 1 3\nprogrammer 4 1.1\nhomemaker 4 3.1\nengineer 3.8 1.4\nnurse 3.5 3.2', a: 'man', b: 'programmer', c: 'woman' } }
    ],
    draw(z) {
      const { g, p } = z;
      const V = rows(p.vocab).map(l => { const t = l.split(/\s+/); return [t[0], [+t[1], +t[2]]]; }).filter(v => isFinite(v[1][0]) && isFinite(v[1][1]));
      const get = w => V.find(v => v[0] === String(w).trim());
      const A = get(p.a), B = get(p.b), Cc = get(p.c);
      const m = scatter(g, z, [52, 14, 320, 270], V.map(v => v[1]), V.map(v => v[0]), { zero: true, colors: V.map(v => [A, B, Cc].includes(v) ? z.col.cv : z.col.ink2) });
      if (!A || !B || !Cc) return 'Type three words that are in the list.';
      const t = [B[1][0] - A[1][0] + Cc[1][0], B[1][1] - A[1][1] + Cc[1][1]];
      D.arrow(g, m.sx(A[1][0]), m.sy(A[1][1]), m.sx(B[1][0]), m.sy(B[1][1]), z.col.orange, 2.5);
      D.arrow(g, m.sx(Cc[1][0]), m.sy(Cc[1][1]), m.sx(t[0]), m.sy(t[1]), z.col.orange, 2.5);
      D.circle(g, m.sx(t[0]), m.sy(t[1]), 8, { stroke: z.col.red, w: 2.5 });
      const cand = V.filter(v => ![A, B, Cc].includes(v)).map(v => [v[0], cos(v[1], t)]).sort((x, y) => y[1] - x[1]);
      const lx = 400;
      D.text(g, `b − a + c =`, lx, 34, { s: 12.5, b: true, c: z.col.ink });
      D.text(g, vstr(t, 2), lx, 54, { s: 12.5, mono: true, b: true, c: z.col.red });
      D.text(g, 'cosine with the target:', lx, 86, { s: 12, b: true, c: z.col.ink2 });
      cand.slice(0, 5).forEach(([w, s], i) => D.text(g, `${w}  ${f2(s, 3)}`, lx + 6, 108 + i * 20, { s: 12, mono: true, b: i === 0, c: i === 0 ? z.col.cv : z.col.ink }));
      return cand.length ? `Answer: <b>${esc(cand[0][0])}</b>. This is the intrinsic analogy test (Google analogy set, BATS). It only works when the same relation points the same way everywhere in the space.` : 'Add more words.';
    }
  });

  def('subword', {
    title: 'Character n-grams: how fastText builds a word',
    sub: 'Add boundary marks < and >, take every slice of n letters for n from the smallest to the largest size, and add the whole word.',
    W: 560, H: 290,
    params: [
      { k: 'word', label: 'Word', type: 'text', v: 'where' },
      { k: 'lo', label: 'Smallest n', v: 3, min: 1, max: 6 },
      { k: 'hi', label: 'Largest n', v: 6, min: 1, max: 8 },
      { k: 'other', label: 'Compare with', type: 'text', v: 'here' }
    ],
    tips: [
      { t: 'The slide example "where" with n = 3 to 6. The trigram <her> of "her" is different from the trigram her inside "where", thanks to the marks.', set: { word: 'where', lo: 3, hi: 6, other: 'her' } },
      { t: 'The fastText slide "playing" with trigrams only. The suffix ing> is shared with every -ing word.', set: { word: 'playing', lo: 3, hi: 3, other: 'running' } },
      { t: 'cat against cats: most pieces are shared, so their vectors start out close even if cats was rare.', set: { word: 'cats', lo: 3, hi: 4, other: 'cat' } },
      { t: 'An unseen word such as "catsy" still gets a vector from its pieces. Word2vec would have nothing for it.', set: { word: 'catsy', lo: 3, hi: 4, other: 'cats' } }
    ],
    draw(z) {
      const { g, p } = z;
      const grams = (w, lo, hi) => { const s = '<' + w + '>', out = []; for (let n = lo; n <= hi; n++) for (let i = 0; i + n <= s.length; i++) out.push(s.slice(i, i + n)); return out; };
      const w = String(p.word).trim().toLowerCase(), o = String(p.other).trim().toLowerCase();
      if (!w) return 'Type a word.';
      const lo = Math.min(p.lo, p.hi), hi = Math.max(p.lo, p.hi);
      const G = grams(w, lo, hi), O = new Set(grams(o, lo, hi));
      let y = 22;
      D.text(g, `<${w}>  gives ${G.length} n-grams plus the word itself`, 16, y, { s: 13, b: true, c: z.col.ink });
      y += 14;
      for (let n = lo; n <= hi; n++) {
        const row = G.filter(x => x.length === n);
        if (!row.length) continue;
        D.text(g, `n=${n}`, 16, y + 18, { s: 11.5, b: true, c: z.col.ink2 });
        let x = 58;
        row.forEach(t => { const wd = tw(g, t, { s: 12, mono: true }) + 12; if (x + wd > 544) { x = 58; y += 26; } pill(g, t, x, y + 4, { s: 12, mono: true, fill: O.has(t) ? z.col.cv : z.col.bg, stroke: z.col.line, c: O.has(t) ? '#fff' : z.col.ink }); x += wd + 4; });
        y += 28;
      }
      const shared = G.filter(t => O.has(t)).length;
      D.text(g, `shared with "${o}": ${shared}`, 16, Math.min(y + 18, 280), { s: 12.5, b: true, c: z.col.cv });
      return `v(${esc(w)}) = v<sub>word</sub> + ∑ z<sub>g</sub> over its ${G.length} n-grams. Shared pieces (filled) give related words related vectors, and an out of vocabulary word still gets a vector.`;
    }
  });

  def('debias', {
    title: 'Neutralise a bias direction',
    sub: 'The bias direction g is the unit vector from one word of a pair to the other. Neutralising removes the part of a word that lies along g.',
    W: 560, H: 320,
    params: [
      { k: 'vocab', label: 'Toy 2D vectors, "word x y" per line', type: 'area', v: 'he 0 -1\nshe 0 1\nprogrammer 3 -0.8\nhomemaker 3 0.9\nnurse 2 1.2\ndoctor 2.5 -0.6' },
      { k: 'a', label: 'Pair word 1', type: 'text', v: 'he' },
      { k: 'b', label: 'Pair word 2', type: 'text', v: 'she' },
      { k: 'words', label: 'Words that should be neutral (comma separated)', type: 'text', v: 'programmer, homemaker, nurse, doctor' },
      { k: 'amt', label: 'How much of the bias part to remove', v: 0, min: 0, max: 1, step: 0.05 }
    ],
    tips: [
      { t: 'Slide the amount from 0 to 1. Each neutral word moves straight across until it sits on the line through the origin at right angles to g.', set: { amt: 1 } },
      { t: 'At amount 0 the projection of programmer on g is −0.8 and of homemaker +0.9: the stereotype from the slide.', set: { amt: 0 } },
      { t: 'Half way: the bias part is halved. Bolukbasi and others remove all of it (amount 1) and then equalise pairs such as he and she.', set: { amt: 0.5 } },
      { t: 'Use a pair that is not exactly vertical. g is still the unit difference, so the arrows follow its direction.', set: { vocab: 'man 0.2 -1\nwoman -0.3 1\nengineer 3 -0.5\nreceptionist 2.6 1.1', a: 'man', b: 'woman', words: 'engineer, receptionist', amt: 1 } }
    ],
    draw(z) {
      const { g, p } = z;
      const V = rows(p.vocab).map(l => { const t = l.split(/\s+/); return [t[0], [+t[1], +t[2]]]; }).filter(v => isFinite(v[1][0]) && isFinite(v[1][1]));
      const get = w => V.find(v => v[0] === String(w).trim());
      const A = get(p.a), B = get(p.b);
      if (!A || !B) return 'Type two pair words that are in the list.';
      const d = [B[1][0] - A[1][0], B[1][1] - A[1][1]], n = norm(d) || 1, gd = [d[0] / n, d[1] / n];
      const neutral = String(p.words).split(',').map(s => s.trim()).filter(Boolean);
      const moved = V.map(([w, v]) => {
        if (!neutral.includes(w)) return [w, v, v, 0];
        const pr = dot(v, gd);
        return [w, v, [v[0] - p.amt * pr * gd[0], v[1] - p.amt * pr * gd[1]], pr];
      });
      const m = scatter(g, z, [52, 14, 290, 280], moved.map(r => r[2]), moved.map(r => r[0]), { zero: true, colors: moved.map(r => neutral.includes(r[0]) ? z.col.cv : z.col.purple) });
      const L = 50;
      g.save(); g.beginPath(); g.rect(52, 14, 290, 280); g.clip();
      D.line(g, m.sx(-gd[1] * -L), m.sy(-gd[0] * L), m.sx(-gd[1] * L), m.sy(gd[0] * L), z.col.ink2, 1.2, [5, 4]);
      g.restore();
      D.arrow(g, m.sx(0), m.sy(0), m.sx(gd[0]), m.sy(gd[1]), z.col.orange, 2.5);
      moved.forEach(r => { if (neutral.includes(r[0]) && p.amt > 0) D.line(g, m.sx(r[1][0]), m.sy(r[1][1]), m.sx(r[2][0]), m.sy(r[2][1]), z.col.ink2, 1, [3, 3]); });
      const lx = 410;
      D.text(g, 'g = ' + vstr(gd, 2), lx, 30, { s: 12.5, mono: true, b: true, c: z.col.orange });
      D.text(g, 'along g: before, after', lx, 58, { s: 11.5, b: true, c: z.col.ink2 });
      moved.filter(r => neutral.includes(r[0])).slice(0, 8).forEach((r, i) => { const t = `${r[0]} ${f2(r[3], 2)}, ${f2(r[3] * (1 - p.amt), 2)}`; D.text(g, t, lx, 80 + i * 20, { s: fit(g, t, 144, 11.5), mono: true, c: z.col.ink }); });
      return `Neutralise: v′ = v − (v·g)g. With the full amount every listed word has 0 along g, so "${esc(p.a)}" and "${esc(p.b)}" are equally far from it.`;
    }
  });

  def('crossling', {
    title: 'Align two languages with one rotation',
    sub: 'English points (orange) and Spanish points (purple) have the same shape but a different orientation. Turn the English space until the pairs meet.',
    W: 560, H: 320,
    params: [
      { k: 'theta', label: 'Rotation of the English space (degrees)', v: 0, min: -180, max: 180 },
      { k: 'noise', label: 'How different the two shapes are', v: 0.1, min: 0, max: 1, step: 0.05 },
      { k: 'pairs', label: 'Pairs, "english spanish x y" (English coordinates)', type: 'area', v: 'dog perro 1 0\ncat gato 0.8 0.6\nhouse casa -0.5 1\nwater agua -1 -0.4\nsun sol 0.2 -1' },
      { k: 'true', label: 'Real rotation between the spaces (degrees)', v: 90, min: -180, max: 180 }
    ],
    tips: [
      { t: 'Turn the slider to 90 degrees. All five pairs meet and the mean distance drops to almost 0.', set: { theta: 90, noise: 0.1 } },
      { t: 'Raise the difference to 0.6. Even at the best angle the pairs do not meet exactly, as with real languages whose spaces are only roughly the same shape.', set: { theta: 90, noise: 0.6 } },
      { t: 'Start far off at −90 degrees. The distance is largest when the spaces point opposite ways.', set: { theta: -90, noise: 0.1 } }
    ],
    draw(z) {
      const { g, p } = z;
      const P = rows(p.pairs).map(l => l.split(/\s+/)).filter(t => t.length >= 4 && isFinite(+t[2]) && isFinite(+t[3])).map(t => [t[0], t[1], [+t[2], +t[3]]]);
      if (!P.length) return 'Add some pairs.';
      const rot = (v, a) => { const r = a * Math.PI / 180, c = Math.cos(r), s = Math.sin(r); return [c * v[0] - s * v[1], s * v[0] + c * v[1]]; };
      const R = rng(7);
      const es = P.map(q => rot(q[2], p.theta));
      const sp = P.map(q => { const v = rot(q[2], p.true); return [v[0] + p.noise * 0.4 * gauss(R), v[1] + p.noise * 0.4 * gauss(R)]; });
      const m = scatter(g, z, [52, 14, 300, 280], es.concat(sp), P.map(q => q[0]).concat(P.map(q => q[1])), { zero: true, colors: es.map(() => z.col.cv).concat(sp.map(() => z.col.purple)) });
      es.forEach((v, i) => D.line(g, m.sx(v[0]), m.sy(v[1]), m.sx(sp[i][0]), m.sy(sp[i][1]), z.col.ink2, 1, [3, 3]));
      const dist = es.reduce((s, v, i) => s + norm([v[0] - sp[i][0], v[1] - sp[i][1]]), 0) / P.length;
      const lx = 400;
      D.text(g, `rotation ${p.theta}°`, lx, 34, { s: 13, b: true, c: z.col.ink });
      D.text(g, `mean pair distance`, lx, 62, { s: 12, b: true, c: z.col.ink2 });
      D.text(g, f2(dist, 3), lx, 84, { s: 18, mono: true, b: true, c: dist < 0.2 ? z.col.cv : z.col.orange });
      return `The mapping W is a rotation, W<sup>T</sup>W = I. With a dictionary it has a closed form (orthogonal Procrustes: W = UV<sup>T</sup> from the SVD of YX<sup>T</sup>). Without one, identical strings or adversarial training find it.`;
    }
  });

  /* ================================================================ Step 3: language models and RNNs */
  def('rnnunroll', {
    title: 'An RNN unrolled in time, with one number per state',
    sub: 'h_t = tanh(w_h · h_{t−1} + w_x · x_t + b). The same w_h, w_x and b are used at every step. Press Play to feed the inputs one by one.',
    W: 560, H: 300,
    params: [
      { k: 'xs', label: 'Inputs x_1 … x_T', type: 'text', v: '1 0 0 0 0 0 0 0' },
      { k: 'wh', label: 'Recurrent weight w_h', v: 0.9, min: -2, max: 2, step: 0.05 },
      { k: 'wx', label: 'Input weight w_x', v: 1, min: -3, max: 3, step: 0.05 },
      { k: 'b', label: 'Bias b', v: 0, min: -2, max: 2, step: 0.05 },
      { k: 'h0', label: 'Initial state h_0', v: 0, min: -1, max: 1, step: 0.05 },
      { k: 'grad', label: 'Show how much h_T depends on h_1 (the gradient)', type: 'check', v: true }
    ],
    tips: [
      { t: 'One pulse at the start, w_h = 0.9. The memory of the pulse fades a little at each step.', set: { xs: '1 0 0 0 0 0 0 0', wh: 0.9 }, play: true },
      { t: 'w_h = 0.5: the memory halves every step. After 8 steps the gradient back to step 1 is below 0.01, a vanishing gradient.', set: { wh: 0.5 }, play: true },
      { t: 'w_h = 1.5 with a steady input. tanh saturates near 1, its slope goes to 0, and the gradient vanishes for a different reason.', set: { wh: 1.5, xs: '1 1 1 1 1 1 1 1' }, play: true },
      { t: 'w_h = −0.9: the state flips sign at every step, an oscillating memory.', set: { wh: -0.9, xs: '1 0 0 0 0 0 0 0' }, play: true },
      { t: 'Type a longer input of 14 values. The model size does not change, which is the RNN advantage over a fixed window.', set: { xs: '1 0 1 0 1 1 0 0 1 0 0 1 0 1', wh: 0.7 }, play: true }
    ],
    startAtZero: true,
    steps: z => nums(z.p.xs).slice(0, 14).length,
    speed: () => 650,
    draw(z) {
      const { g, p } = z;
      const xs = nums(p.xs).slice(0, 14), T = xs.length;
      if (!T) return 'Type some numbers as inputs.';
      const hs = [p.h0], ds = [];
      xs.forEach(x => { const a = p.wh * hs[hs.length - 1] + p.wx * x + p.b, h = Math.tanh(a); hs.push(h); ds.push(1 - h * h); });
      const gap = Math.min(64, 520 / T), x0 = 30;
      for (let t = 0; t < T; t++) {
        const cx = x0 + t * gap + gap / 2, on = t < z.step;
        if (t > 0) D.arrow(g, cx - gap + 18, 120, cx - 18, 120, on ? z.col.cv : z.col.line, 2);
        rr(g, cx - 17, 102, 34, 36, 7, { fill: on ? z.col.cv : z.col.bg, stroke: z.col.line });
        D.text(g, on ? f2(hs[t + 1], 2) : 'h', cx, 125, { a: 'center', s: 11, b: true, c: on ? '#fff' : z.col.ink2 });
        D.arrow(g, cx, 186, cx, 140, on ? z.col.orange : z.col.line, 1.8);
        D.text(g, f2(xs[t], 2), cx, 202, { a: 'center', s: 12, mono: true, b: true, c: z.col.ink });
        D.text(g, `t=${t + 1}`, cx, 96, { a: 'center', s: 10.5, c: z.col.ink2 });
      }
      D.text(g, 'hidden state', 16, 80, { s: 11.5, b: true, c: z.col.cv });
      D.text(g, 'inputs', 16, 222, { s: 11.5, b: true, c: z.col.orange });
      const s = Math.max(1, z.step);
      let gprod = 1; for (let t = 1; t < s; t++) gprod *= p.wh * ds[t];
      if (p.grad) {
        D.text(g, `∂h_${s}/∂h_1 = ∏ w_h·(1 − h_t²) = ${f2(gprod, 5)}`, 16, 256, { s: 12.5, mono: true, b: true, c: Math.abs(gprod) < 0.01 ? z.col.red : z.col.ink });
        const bw = Math.min(260, Math.abs(gprod) * 260);
        rr(g, 16, 266, 260, 10, 4, { fill: z.col.bg });
        rr(g, 16, 266, Math.max(2, bw), 10, 4, { fill: Math.abs(gprod) < 0.01 ? z.col.red : z.col.green });
      }
      return `Each factor w<sub>h</sub>·tanh′ is the local slope. When their size stays below 1 the product shrinks exponentially with distance, so early words stop influencing learning. ${Math.abs(gprod) < 0.01 && z.step > 2 ? '<b>The gradient has vanished.</b>' : ''}`;
    }
  });

  def('paramcount', {
    title: 'Count the trainable parameters',
    sub: 'Pick a model and set its sizes. The breakdown lists every weight matrix with its shape, ignoring biases unless you include them.',
    W: 560, H: 300,
    params: [
      { k: 'model', label: 'Model', type: 'select', v: 'rnnlm', opts: [['rnnlm', 'RNN language model (one-hot input)'], ['tagger', 'RNN tagger with embeddings'], ['bilstm', 'BiLSTM tagger'], ['lstm', 'LSTM layer'], ['gru', 'GRU layer'], ['skipgram', 'Skip-gram with full softmax'], ['seq2seq', 'Seq2seq RNN with attention']] },
      { k: 'V', label: 'Vocabulary or input size V', v: 5, min: 2, max: 50000, step: 1 },
      { k: 'E', label: 'Embedding size', v: 300, min: 1, max: 1024, show: p => ['tagger', 'bilstm', 'lstm', 'gru', 'skipgram', 'seq2seq'].includes(p.model) },
      { k: 'H', label: 'Hidden size (encoder for seq2seq)', v: 6, min: 1, max: 1024 },
      { k: 'H2', label: 'Decoder hidden size', v: 256, min: 1, max: 1024, show: p => p.model === 'seq2seq' },
      { k: 'V2', label: 'Target vocabulary size', v: 45000, min: 2, max: 100000, show: p => p.model === 'seq2seq' },
      { k: 'K', label: 'Number of output labels', v: 50, min: 1, max: 1000, show: p => ['tagger', 'bilstm'].includes(p.model) },
      { k: 'bias', label: 'Include bias vectors', type: 'check', v: false }
    ],
    tips: [
      { t: 'The lecture exercise: V = 5, hidden 6, no biases. 5×6 + 6×6 + 6×5 = 96.', set: { model: 'rnnlm', V: 5, H: 6, bias: false } },
      { t: 'POS tagger: 300 dim embeddings, hidden 50, 50 tags: 300×50 + 50×50 + 50×50 = 20,000.', set: { model: 'tagger', E: 300, H: 50, K: 50, bias: false } },
      { t: 'NER with 5 entity types and BIO: 2×5 + 1 = 11 labels, so the output layer is 50 × 11.', set: { model: 'tagger', E: 300, H: 50, K: 11, bias: false } },
      { t: 'BiLSTM language identification: embeddings 60, each direction 32, 4 tags. 2 × 4 × 32 × (60 + 32) + 64 × 4 = 23,808.', set: { model: 'bilstm', E: 60, H: 32, K: 4, bias: false } },
      { t: 'Skip-gram with V = 10,000 and d = 300: two matrices of 3,000,000 each, 6,000,000 in total.', set: { model: 'skipgram', V: 10000, E: 300, bias: false } },
      { t: 'The seq2seq question: source V 35,000, target 45,000, embeddings 256, encoder 128, decoder 256. Read the breakdown and its assumptions.', set: { model: 'seq2seq', V: 35000, V2: 45000, E: 256, H: 128, H2: 256, bias: false } }
    ],
    draw(z) {
      const { g, p } = z;
      const b = p.bias, L = [];
      const add = (name, r, c, note) => L.push([name, r, c, note]);
      if (p.model === 'rnnlm') { add('W_xh input to hidden', p.V, p.H); add('W_hh hidden to hidden', p.H, p.H); add('W_hy hidden to output', p.H, p.V); if (b) { add('b_h', 1, p.H); add('b_y', 1, p.V); } }
      if (p.model === 'tagger') { add('W_xh embedding to hidden', p.E, p.H); add('W_hh hidden to hidden', p.H, p.H); add('W_hy hidden to labels', p.H, p.K); if (b) { add('b_h', 1, p.H); add('b_y', 1, p.K); } }
      if (p.model === 'lstm' || p.model === 'gru' || p.model === 'bilstm') {
        const gates = p.model === 'gru' ? 3 : 4, dirs = p.model === 'bilstm' ? 2 : 1;
        for (let d = 0; d < dirs; d++) {
          const tag = dirs > 1 ? (d ? 'backward ' : 'forward ') : '';
          add(`${tag}input weights (${gates} gates)`, gates * p.H, p.E);
          add(`${tag}recurrent weights (${gates} gates)`, gates * p.H, p.H);
          if (b) add(`${tag}biases`, 1, gates * p.H);
        }
        if (p.model === 'bilstm') { add('output layer on [h→; h←]', 2 * p.H, p.K); if (b) add('output bias', 1, p.K); }
      }
      if (p.model === 'skipgram') { add('input embeddings E', p.V, p.E); add('output weights W', p.E, p.V); if (b) add('output bias', 1, p.V); }
      if (p.model === 'seq2seq') {
        add('source embeddings', p.V, p.E); add('target embeddings', p.V2, p.E);
        add('encoder W_xh', p.E, p.H); add('encoder W_hh', p.H, p.H);
        add('bridge encoder to decoder state', p.H, p.H2);
        add('decoder W_xh', p.E, p.H2); add('decoder W_hh', p.H2, p.H2);
        add('attention projection (decoder to encoder size)', p.H2, p.H);
        add('output on [s_t; context]', p.H2 + p.H, p.V2);
      }
      let y = 26, tot = 0;
      D.text(g, 'matrix', 16, y, { s: 11.5, b: true, c: z.col.ink2 }); D.text(g, 'shape', 330, y, { s: 11.5, b: true, c: z.col.ink2 }); D.text(g, 'count', 544, y, { a: 'right', s: 11.5, b: true, c: z.col.ink2 });
      L.forEach(([n, r, c]) => {
        y += 21; tot += r * c;
        D.text(g, n, 16, y, { s: fit(g, n, 300, 12), c: z.col.ink });
        D.text(g, `${r} × ${c}`, 330, y, { s: 12, mono: true, c: z.col.ink });
        D.text(g, (r * c).toLocaleString('en-US'), 544, y, { a: 'right', s: 12, mono: true, b: true, c: z.col.ink });
      });
      D.line(g, 16, y + 10, 544, y + 10, z.col.line, 1);
      D.text(g, `total = ${tot.toLocaleString('en-US')}`, 544, y + 32, { a: 'right', s: 15, b: true, c: z.col.cv });
      const extra = p.model === 'seq2seq' ? ' The seq2seq total depends on choices the question must state, such as how the encoder state starts the decoder and how attention scores are computed. Write your assumptions in the exam.' : '';
      return `An RNN reuses the same matrices at every time step, so the count does not depend on sentence length.${extra}`;
    }
  });

  def('celoss', {
    title: 'Cross-entropy loss and perplexity',
    sub: 'The loss at one step is −log of the probability the model gave the true next word. Perplexity is exp of the average loss.',
    W: 560, H: 290,
    params: [
      { k: 'probs', label: 'Predicted distribution over the words', type: 'text', v: '0.1 0.6 0.2 0.1' },
      { k: 'gold', label: 'Position of the true word (1 = first)', v: 2, min: 1, max: 8 },
      { k: 'seq', label: 'Probabilities of the true words over a sentence (for perplexity)', type: 'text', v: '0.6 0.3 0.5 0.4' }
    ],
    tips: [
      { t: 'The slide example: gold is word 2 and the model gives it 0.6. Loss = −ln 0.6 = 0.51.', set: { probs: '0.1 0.6 0.2 0.1', gold: 2 } },
      { t: 'The second slide example: the model gives the true word only 0.05. Loss = −ln 0.05 = 2.99, a strong penalty for being confidently wrong.', set: { probs: '0.4 0.3 0.05 0.25', gold: 3 } },
      { t: 'A perfect model gives the true word 1 at every step. The loss is 0 and the perplexity is 1.', set: { seq: '1 1 1 1' } },
      { t: 'Give every word 0.25. The perplexity is exactly 4, the model is guessing among 4 words.', set: { seq: '0.25 0.25 0.25 0.25' } }
    ],
    draw(z) {
      const { g, p } = z;
      const P = nums(p.probs).slice(0, 8), gi = Math.min(P.length, p.gold) - 1;
      if (!P.length) return 'Type some probabilities.';
      const s = P.reduce((a, b) => a + b, 0);
      bars(g, z, [30, 26, 260, 180], P, P.map((_, i) => i === gi ? 'gold' : `w${i + 1}`), { colors: P.map((_, i) => i === gi ? z.col.cv : z.col.ink2), max: 1 });
      const loss = -Math.log(P[gi]);
      D.text(g, `loss = −ln ${f2(P[gi], 3)} = ${f2(loss, 4)}`, 30, 250, { s: 13, mono: true, b: true, c: z.col.cv });
      const Q = nums(p.seq).filter(v => v > 0 && v <= 1), T = Q.length;
      const avg = T ? Q.reduce((a, q) => a - Math.log(q), 0) / T : 0;
      const lx = 330;
      D.text(g, 'over the sentence', lx, 34, { s: 12.5, b: true, c: z.col.ink });
      Q.slice(0, 8).forEach((q, i) => D.text(g, `step ${i + 1}: −ln ${f2(q, 3)} = ${f2(-Math.log(q), 3)}`, lx, 58 + i * 19, { s: 11.5, mono: true, c: z.col.ink }));
      D.text(g, `J = average = ${f2(avg, 4)}`, lx, 230, { s: 12.5, mono: true, b: true, c: z.col.ink });
      D.text(g, `perplexity = e^J = ${f2(Math.exp(avg), 4)}`, lx, 252, { s: 13, mono: true, b: true, c: z.col.cv });
      return `${Math.abs(s - 1) > 1e-6 ? `These numbers add to ${f2(s, 3)}, not 1, so they are not a proper distribution. ` : ''}Cross entropy with a one-hot gold vector keeps only the gold term: J = −∑ y<sub>w</sub> log ŷ<sub>w</sub> = −log ŷ<sub>gold</sub>. Lower perplexity is better.`;
    }
  });

  const TYPES = ['PER', 'ORG', 'LOC', 'GPE', 'MISC', 'DATE'];
  def('bio', {
    title: 'From entity spans to one BIO tag per word',
    sub: 'Write entities in square brackets with their type, as on the slide. Every word gets B (begins a span), I (inside) or O (outside).',
    W: 560, H: 300,
    params: [
      { k: 'text', label: 'Sentence with [TYPE words] spans', type: 'area', v: '[PER Jane Villanueva] of [ORG United] , a unit of [ORG United Airlines Holding] , said the fare applies to the [LOC Chicago] route .' },
      { k: 'scheme', label: 'Scheme', type: 'select', v: 'bio', opts: [['bio', 'BIO'], ['io', 'IO (no B tags)'], ['bioes', 'BIOES (adds E end and S single)']] },
      { k: 'n', label: 'Number of entity types n', v: 4, min: 1, max: 20 }
    ],
    tips: [
      { t: 'The slide sentence in BIO. "United Airlines Holding" becomes B-ORG I-ORG I-ORG.', set: { scheme: 'bio' } },
      { t: 'Switch to IO. Two different organisations that sit next to each other could no longer be told apart, which is why B exists.', set: { scheme: 'io', text: 'He sold [ORG Google] [ORG Microsoft] shares .' } },
      { t: 'BIOES marks the end word and single word spans. More tags, sharper boundaries.', set: { scheme: 'bioes' } },
      { t: 'Count the tags: with n types BIO needs 2n + 1. The lecture question uses n = 5, so 11 output labels.', set: { n: 5, scheme: 'bio' } }
    ],
    draw(z) {
      const { g, p } = z;
      const toks = []; const re = /\[(\w+)\s+([^\]]+)\]|(\S+)/g; let m;
      while ((m = re.exec(p.text))) {
        if (m[3]) toks.push([m[3], 'O']);
        else { const ws = m[2].trim().split(/\s+/); ws.forEach((w, i) => {
          let t;
          if (p.scheme === 'io') t = 'I-' + m[1];
          else if (p.scheme === 'bioes') t = (ws.length === 1 ? 'S-' : i === 0 ? 'B-' : i === ws.length - 1 ? 'E-' : 'I-') + m[1];
          else t = (i === 0 ? 'B-' : 'I-') + m[1];
          toks.push([w, t]);
        }); }
      }
      let x = 16, y = 20;
      const col = t => t === 'O' ? z.col.bg : t[0] === 'B' || t[0] === 'S' ? z.col.cv : t[0] === 'E' ? z.col.purple : z.col.orange;
      toks.slice(0, 40).forEach(([w, t]) => {
        const wd = Math.max(tw(g, w, { s: 12.5, b: true }), tw(g, t, { s: 10.5, mono: true })) + 14;
        if (x + wd > 548) { x = 16; y += 50; }
        rr(g, x, y, wd, 22, 5, { fill: z.col.surf, stroke: z.col.line });
        D.text(g, w, x + wd / 2, y + 15, { a: 'center', s: 12.5, b: true, c: z.col.ink });
        rr(g, x, y + 24, wd, 18, 5, { fill: col(t) });
        D.text(g, t, x + wd / 2, y + 37, { a: 'center', s: 10.5, mono: true, b: true, c: t === 'O' ? z.col.ink2 : '#fff' });
        x += wd + 5;
      });
      const per = { bio: 2, io: 1, bioes: 4 }[p.scheme], total = per * p.n + 1;
      D.text(g, `${p.scheme.toUpperCase()} with n = ${p.n} types: ${per}n + 1 = ${total} labels`, 16, 286, { s: 13, b: true, c: z.col.cv });
      return 'Now NER is a sequence labelling task like POS tagging: one label per token, so an RNN or BiLSTM can predict it word by word, and spans are read back from the tags.';
    }
  });

  def('gates', {
    title: 'How long a memory survives: RNN against LSTM and GRU',
    sub: 'A single fact enters at step 1. The bars show how much of it is still in memory at each later step.',
    W: 560, H: 300,
    params: [
      { k: 'T', label: 'Number of steps', v: 20, min: 2, max: 40 },
      { k: 'wh', label: 'RNN recurrent factor w_h · tanh′', v: 0.6, min: 0, max: 1.2, step: 0.01 },
      { k: 'f', label: 'LSTM forget gate f (1 = keep everything)', v: 0.95, min: 0, max: 1, step: 0.01 },
      { k: 'zg', label: 'GRU update gate z (0 = keep old memory)', v: 0.05, min: 0, max: 1, step: 0.01 },
      { k: 'show', label: 'Show', type: 'select', v: 'all', opts: [['all', 'all three'], ['rnn', 'RNN only'], ['lstm', 'LSTM only'], ['gru', 'GRU only']] }
    ],
    tips: [
      { t: 'RNN factor 0.6 against LSTM f = 0.95. After 20 steps the RNN keeps 0.6¹⁹ ≈ 0.00006, the LSTM keeps 0.95¹⁹ ≈ 0.38.', set: { wh: 0.6, f: 0.95, T: 20 } },
      { t: 'Set f = 1. The LSTM cell is a straight wire: c_t = c_{t−1} and the memory is kept forever. This is the slide point "forget gate set to remember everything".', set: { f: 1 } },
      { t: 'Set the RNN factor above 1. The memory and the gradient explode instead of vanish. Gradient clipping is the usual fix.', set: { wh: 1.1, show: 'rnn' } },
      { t: 'GRU with z = 0.05: h_t = (1 − z)h_{t−1} + z·h̃_t, so it keeps 95 percent each step, like the LSTM.', set: { zg: 0.05, show: 'all' } }
    ],
    draw(z) {
      const { g, p } = z;
      const series = [['RNN', t => p.wh ** t, z.col.red], ['LSTM', t => p.f ** t, z.col.cv], ['GRU', t => (1 - p.zg) ** t, z.col.purple]].filter(s => p.show === 'all' || s[0].toLowerCase() === p.show);
      const box = [52, 16, 330, 230];
      const mx = Math.max(1, ...series.map(s => s[1](p.T - 1)));
      const m = D.axes(g, z, box, [1, p.T], [0, mx], { nx: 4, ny: 4, xl: 'step', yl: 'memory left', fx: v => fmt(v, 0) });
      series.forEach(([n, f, c]) => {
        g.strokeStyle = c; g.lineWidth = 2.5; g.beginPath();
        for (let t = 1; t <= p.T; t++) { const v = f(t - 1); t > 1 ? g.lineTo(m.sx(t), m.sy(Math.min(mx, v))) : g.moveTo(m.sx(t), m.sy(Math.min(mx, v))); }
        g.stroke();
      });
      let y = 40;
      series.forEach(([n, f, c]) => { D.text(g, `${n}: ${f2(f(p.T - 1), 5)}`, 400, y, { s: 13, b: true, mono: true, c }); y += 24; });
      D.text(g, `left after ${p.T} steps`, 400, y + 4, { s: 11.5, c: z.col.ink2 });
      return 'LSTM: c<sub>t</sub> = f<sub>t</sub> ⊙ c<sub>t−1</sub> + i<sub>t</sub> ⊙ c̃<sub>t</sub>. The path through the cell is a sum with a gate, not a squashing matrix product, so the gradient along it is just f<sub>t</sub>. The network learns to keep f near 1 for facts it must remember.';
    }
  });

  def('lstmcell', {
    title: 'One LSTM or GRU step, gate by gate',
    sub: 'Set the gate values directly and watch the new memory. Gates are sigmoids, so each lies between 0 (closed) and 1 (open).',
    W: 560, H: 300,
    params: [
      { k: 'cell', label: 'Cell type', type: 'select', v: 'lstm', opts: [['lstm', 'LSTM'], ['gru', 'GRU']] },
      { k: 'cprev', label: 'Old memory c_{t−1} (LSTM) or h_{t−1} (GRU)', v: 0.8, min: -1, max: 1, step: 0.05 },
      { k: 'cand', label: 'New candidate c̃_t or h̃_t', v: -0.5, min: -1, max: 1, step: 0.05 },
      { k: 'f', label: 'Forget gate f', v: 0.9, min: 0, max: 1, step: 0.05, show: p => p.cell === 'lstm' },
      { k: 'i', label: 'Input gate i', v: 0.2, min: 0, max: 1, step: 0.05, show: p => p.cell === 'lstm' },
      { k: 'o', label: 'Output gate o', v: 0.7, min: 0, max: 1, step: 0.05, show: p => p.cell === 'lstm' },
      { k: 'zg', label: 'Update gate z', v: 0.3, min: 0, max: 1, step: 0.05, show: p => p.cell === 'gru' }
    ],
    tips: [
      { t: 'Keep the old fact: f = 1, i = 0. The new memory equals the old memory, whatever the candidate says.', set: { cell: 'lstm', f: 1, i: 0 } },
      { t: 'Replace it: f = 0, i = 1. The memory is now the candidate. This is how a model forgets the subject when a new sentence starts.', set: { cell: 'lstm', f: 0, i: 1 } },
      { t: 'Hide it: o = 0. The memory is kept inside the cell but h_t = 0, so the next layer sees nothing yet.', set: { cell: 'lstm', f: 0.9, i: 0.2, o: 0 } },
      { t: 'GRU with z = 0 keeps h_{t−1}, with z = 1 takes the candidate. One gate does the work of forget and input together.', set: { cell: 'gru', zg: 0 } }
    ],
    draw(z) {
      const { g, p } = z;
      let lines;
      if (p.cell === 'lstm') {
        const c = p.f * p.cprev + p.i * p.cand, h = p.o * Math.tanh(c);
        lines = [
          ['c_t = f ⊙ c_{t−1} + i ⊙ c̃_t', ''],
          [`    = ${f2(p.f, 2)} × ${f2(p.cprev, 2)} + ${f2(p.i, 2)} × ${f2(p.cand, 2)}`, ''],
          [`    = ${f2(c, 4)}`, 'c'],
          ['h_t = o ⊙ tanh(c_t)', ''],
          [`    = ${f2(p.o, 2)} × tanh(${f2(c, 3)}) = ${f2(h, 4)}`, 'h']
        ];
        bars(g, z, [330, 20, 210, 200], [p.cprev, p.f * p.cprev, p.i * p.cand, c, h], ['old', 'kept', 'added', 'c_t', 'h_t'], { max: 1.2, colors: [z.col.ink2, z.col.cv, z.col.orange, z.col.purple, z.col.green] });
      } else {
        const h = (1 - p.zg) * p.cprev + p.zg * p.cand;
        lines = [
          ['h_t = (1 − z) ⊙ h_{t−1} + z ⊙ h̃_t', ''],
          [`    = ${f2(1 - p.zg, 2)} × ${f2(p.cprev, 2)} + ${f2(p.zg, 2)} × ${f2(p.cand, 2)}`, ''],
          [`    = ${f2(h, 4)}`, 'h']
        ];
        bars(g, z, [330, 20, 210, 200], [p.cprev, (1 - p.zg) * p.cprev, p.zg * p.cand, h], ['old', 'kept', 'added', 'h_t'], { max: 1.2, colors: [z.col.ink2, z.col.cv, z.col.orange, z.col.green] });
      }
      lines.forEach(([t, k], i) => D.text(g, t, 16, 40 + i * 30, { s: 12.5, mono: true, b: !!k, c: k ? z.col.cv : z.col.ink }));
      D.text(g, 'bar heights show sizes, signs are in the numbers', 548, 268, { a: 'right', s: fit(g, 'bar heights show sizes, signs are in the numbers', 228, 11), c: z.col.ink2 });
      return p.cell === 'lstm' ? 'Gates: f = σ(W<sub>f</sub>[h<sub>t−1</sub>, x<sub>t</sub>] + b<sub>f</sub>), and the same form for i and o. The candidate is c̃<sub>t</sub> = tanh(W<sub>c</sub>[h<sub>t−1</sub>, x<sub>t</sub>] + b<sub>c</sub>).' : 'GRU: z = σ(W<sub>z</sub>x<sub>t</sub> + U<sub>z</sub>h<sub>t−1</sub>), r = σ(W<sub>r</sub>x<sub>t</sub> + U<sub>r</sub>h<sub>t−1</sub>), h̃<sub>t</sub> = tanh(W<sub>h</sub>x<sub>t</sub> + U<sub>h</sub>(r ⊙ h<sub>t−1</sub>)). The reset gate r decides how much of the past the candidate may use.';
    }
  });

  /* ================================================================ Step 4: seq2seq, attention, decoding */
  def('seq2seq', {
    title: 'Encoder and decoder: translating one word at a time',
    sub: 'The encoder reads the source. The decoder writes the target, feeding each output word back in as the next input. Press Play.',
    W: 560, H: 300,
    params: [
      { k: 'src', label: 'Source sentence', type: 'text', v: 'il a m’ entarté' },
      { k: 'tgt', label: 'Target sentence', type: 'text', v: 'he hit me with a pie' },
      { k: 'attn', label: 'Use attention (the decoder looks back at every encoder state)', type: 'check', v: false }
    ],
    tips: [
      { t: 'Without attention, every target word must come out of the single orange vector, the bottleneck.', set: { attn: false }, play: true },
      { t: 'With attention each decoder step draws lines to all encoder states, with a fresh mix every step.', set: { attn: true }, play: true },
      { t: 'Try a long source. The bottleneck vector stays the same size however long the input gets.', set: { src: 'the protests escalated over the weekend after the police arrived in the old city centre', tgt: 'die Proteste waren am Wochenende eskaliert', attn: false }, play: true }
    ],
    startAtZero: true,
    steps: z => String(z.p.src).trim().split(/\s+/).length + String(z.p.tgt).trim().split(/\s+/).length + 1,
    speed: () => 600,
    draw(z) {
      const { g, p } = z;
      const S = String(p.src).trim().split(/\s+/).slice(0, 16), T = String(p.tgt).trim().split(/\s+/).slice(0, 10);
      const ns = S.length, nt = T.length + 1;
      const sw = Math.min(46, 250 / ns), tw2 = Math.min(46, 250 / nt);
      const ex = i => 16 + i * sw + sw / 2, dx = j => 290 + j * tw2 + tw2 / 2;
      const encOn = i => z.step > i, decOn = j => z.step > ns + j;
      /* one label per box. Level text when every word fits its box, else the words turn upright so neighbours never touch */
      const labels = (words, xs, slot, y, dir, col, on = () => true) => {
        const need = Math.max(...words.map(w => tw(g, w, { s: 11.5, b: true })));
        const fs = Math.min(11.5, 11.5 * (slot - 4) / need);
        if (fs >= 9.5) { words.forEach((w, i) => on(i) && D.text(g, w, xs(i), dir > 0 ? y + 11 : y, { a: 'center', s: fs, b: true, c: col(i) })); return; }
        const up = Math.min(11.5, slot - 2);
        words.forEach((w, i) => { if (!on(i)) return; g.save(); g.translate(xs(i), y); g.rotate(dir * Math.PI / 2); D.text(g, w, 0, 0, { s: fit(g, w, dir > 0 ? 92 : 84, up, { b: true }), b: true, bl: 'middle', c: col(i) }); g.restore(); });
      };
      S.forEach((w, i) => {
        rr(g, ex(i) - sw / 2 + 3, 130, sw - 6, 34, 6, { fill: encOn(i) ? z.col.cv : z.col.bg, stroke: z.col.line });
        if (i) D.line(g, ex(i - 1) + sw / 2 - 3, 147, ex(i) - sw / 2 + 3, 147, z.col.line, 1.5);
      });
      labels(S, ex, sw, 172, 1, () => z.col.ink);
      D.text(g, 'encoder', 16, 120, { s: 12, b: true, c: z.col.cv });
      const last = ex(ns - 1) + sw / 2 - 3;
      if (z.step >= ns) { D.circle(g, 272, 147, 10, { fill: z.col.orange }); D.line(g, last, 147, 262, 147, z.col.orange, 2.5); }
      D.text(g, 'one vector', 272, 102, { a: 'center', s: 10.5, b: true, c: z.col.orange });
      const ins = ['<START>'].concat(T);
      ins.forEach((w, j) => rr(g, dx(j) - tw2 / 2 + 3, 130, tw2 - 6, 34, 6, { fill: decOn(j) ? z.col.purple : z.col.bg, stroke: z.col.line }));
      labels(ins, dx, tw2, 172, 1, () => z.col.ink);
      labels(ins.map((_, j) => j < T.length ? T[j] : '<END>'), dx, tw2, 122, -1, () => z.col.purple, decOn);
      D.text(g, 'decoder', 290, 284, { s: 12, b: true, c: z.col.purple });
      const cur = z.step - ns - 1;
      if (p.attn && cur >= 0 && cur < nt) {
        const r = rng(cur + 3), wts = softmax(S.map(() => r() * 3)), mxw = Math.max(...wts);
        S.forEach((_, i) => { g.save(); g.globalAlpha = 0.15 + 0.85 * wts[i] / mxw; D.line(g, ex(i), 130, dx(cur), 130, z.col.green, 1 + 4 * wts[i]); g.restore(); });
      } else if (cur >= 0 && cur < nt) D.line(g, 282, 147, dx(cur) - tw2 / 2 + 3, 147, z.col.orange, 2, [5, 4]);
      return p.attn ? 'With attention the decoder builds a new context vector at every step from all encoder states (green lines, thicker means more weight). The weights here are only illustrative, the next animation computes real ones.' : 'Without attention the decoder sees the source only through the last encoder state. Everything about a long sentence has to fit into that one vector, which is the bottleneck problem.';
    }
  });

  def('attention', {
    title: 'Dot-product attention, computed step by step',
    sub: 'Score each encoder state against the decoder state, turn the scores into weights with softmax, and mix the encoder states with those weights.',
    W: 560, H: 320,
    params: [
      { k: 'enc', label: 'Encoder states h_1 … h_n, one vector per line', type: 'area', v: '2 0\n-1 2\n1 -1\n0 1' },
      { k: 'dec', label: 'Decoder state s_t', type: 'text', v: '1 -2' },
      { k: 'scale', label: 'Divide scores by √d (scaled dot product)', type: 'check', v: false },
      { k: 'temp', label: 'Extra temperature (1 = plain softmax)', v: 1, min: 0.1, max: 5, step: 0.1 }
    ],
    tips: [
      { t: 'The lecture problem: scores 2, −5, 3, −2. Weights ≈ 0.268, 0.0002, 0.727, 0.005. Context ≈ [1.262, −0.722].', set: { enc: '2 0\n-1 2\n1 -1\n0 1', dec: '1 -2', scale: false, temp: 1 } },
      { t: 'Tick the √d scaling used by transformers. Scores shrink by √2, so the weights spread out a little.', set: { scale: true } },
      { t: 'Raise the temperature to 5. Attention becomes almost uniform, an average of all states.', set: { temp: 5, scale: false } },
      { t: 'Lower it to 0.2. Attention becomes almost hard, it copies the single best state h_3.', set: { temp: 0.2 } },
      { t: 'Flip the decoder to "-1 2". Now h_2 wins, the state that points the same way.', set: { dec: '-1 2', temp: 1 } }
    ],
    draw(z) {
      const { g, p } = z;
      const H = vecs(p.enc).filter(v => v.length).slice(0, 8), s = nums(p.dec);
      if (!H.length || !s.length) return 'Give encoder states and a decoder state.';
      const d = s.length, sc = H.map(h => dot(h, s) / (p.scale ? Math.sqrt(d) : 1) / p.temp);
      const a = softmax(sc), ctx = s.map((_, k) => H.reduce((acc, h, i) => acc + a[i] * (h[k] || 0), 0));
      D.text(g, 'i', 16, 26, { s: 11.5, b: true, c: z.col.ink2 });
      ['h_i', 'score e_i', 'weight α_i'].forEach((t, i) => D.text(g, t, 40 + i * 92, 26, { s: 11.5, b: true, c: z.col.ink2 }));
      H.forEach((h, i) => {
        const y = 50 + i * 24;
        D.text(g, String(i + 1), 16, y, { s: 12, b: true, c: z.col.ink });
        D.text(g, vstr(h, 1), 40, y, { s: 12, mono: true, c: z.col.ink });
        D.text(g, f2(sc[i], 3), 132, y, { s: 12, mono: true, c: z.col.ink });
        rr(g, 224, y - 12, 80 * a[i], 14, 3, { fill: z.col.cv });
        D.text(g, f2(a[i], 4), 310, y, { s: 12, mono: true, b: true, c: z.col.cv });
      });
      const y0 = 50 + H.length * 24 + 10;
      D.text(g, `context c_t = ∑ α_i h_i = ${vstr(ctx, 4)}`, 16, y0, { s: 12.5, mono: true, b: true, c: z.col.purple });
      if (d === 2) {
        const all = H.concat([s, ctx]);
        const m = scatter(g, z, [400, 16, 150, 150], all, null, { zero: true, r: 0.1 });
        H.forEach((h, i) => { D.arrow(g, m.sx(0), m.sy(0), m.sx(h[0]), m.sy(h[1]), z.col.ink2, 1 + 3 * a[i]); D.text(g, `h${i + 1}`, m.sx(h[0]) + 3, m.sy(h[1]) - 3, { s: 10.5, b: true, c: z.col.ink }); });
        D.arrow(g, m.sx(0), m.sy(0), m.sx(s[0]), m.sy(s[1]), z.col.orange, 2.2); D.text(g, 's', m.sx(s[0]) + 3, m.sy(s[1]) + 12, { s: 11, b: true, c: z.col.orange });
        D.arrow(g, m.sx(0), m.sy(0), m.sx(ctx[0]), m.sy(ctx[1]), z.col.purple, 2.6); D.text(g, 'c', m.sx(ctx[0]) + 4, m.sy(ctx[1]) + 4, { s: 11, b: true, c: z.col.purple });
      }
      return `e<sub>i</sub> = s<sub>t</sub>·h<sub>i</sub>${p.scale ? ' ÷ √d' : ''}, α = softmax(e), c<sub>t</sub> = ∑ α<sub>i</sub>h<sub>i</sub>. The weights add to 1, and the context leans toward the encoder states that agree with what the decoder is looking for.`;
    }
  });

  /* a small next-word tree: each line is "prefix → word prob" with prefixes written with spaces or ∅ for the start */
  const TREE = 'START a 0.5\nSTART the 0.4\nSTART one 0.1\na cat 0.4\na dog 0.3\na mat 0.3\nthe cat 0.9\nthe dog 0.1\none cat 0.5\none dog 0.5\na_cat END 1\na_dog END 1\na_mat END 1\nthe_cat END 1\nthe_dog END 1\none_cat END 1\none_dog END 1';
  def('beam', {
    title: 'Greedy decoding against beam search',
    sub: 'Each edge is a next-word probability. Greedy keeps only the single best word at each step. Beam search keeps the k best partial sentences.',
    W: 560, H: 320,
    params: [
      { k: 'k', label: 'Beam size k', v: 2, min: 1, max: 4 },
      { k: 'tree', label: 'Tree, one "prefix word probability" per line (join prefix words with _)', type: 'area', v: TREE },
      { k: 'logs', label: 'Score with log probabilities', type: 'check', v: true }
    ],
    tips: [
      { t: 'k = 1 is greedy. It takes "a" (0.5) and then "cat" (0.4): total 0.20. But "the cat" scores 0.4 × 0.9 = 0.36.', set: { k: 1 } },
      { t: 'k = 2 keeps "a" and "the" alive after step 1, and finds "the cat" with 0.36, the best sentence here.', set: { k: 2 } },
      { t: 'Change the edge "the cat 0.9" to 0.4. Now greedy and beam agree. Beam only helps when a weak start leads to a strong finish.', set: { tree: TREE.replace('the cat 0.9', 'the cat 0.4').replace('the dog 0.1', 'the dog 0.6'), k: 2 } },
      { t: 'Untick the log option. Products and sums of logs pick the same winner, logs only avoid tiny numbers on long sentences.', set: { logs: false } }
    ],
    startAtZero: true,
    steps: () => 3,
    speed: () => 1100,
    draw(z) {
      const { g, p } = z;
      const E = {};
      rows(p.tree).forEach(l => { const t = l.split(/\s+/); if (t.length >= 3) (E[t[0]] = E[t[0]] || []).push([t[1], +t[2]]); });
      const key = seq => seq.length ? seq.join('_') : 'START';
      let beam = [[[], 1]];
      const hist = [beam];
      for (let s = 0; s < 3; s++) {
        const cand = [];
        beam.forEach(([seq, pr]) => { if (seq[seq.length - 1] === 'END') { cand.push([seq, pr]); return; } (E[key(seq)] || []).forEach(([w, q]) => cand.push([seq.concat(w), pr * q])); });
        cand.sort((a, b) => b[1] - a[1]);
        beam = cand.slice(0, p.k); hist.push(beam);
      }
      const all = []; const walk = (seq, pr) => { const ch = E[key(seq)]; if (!ch || !ch.length) { all.push([seq, pr]); return; } ch.forEach(([w, q]) => walk(seq.concat(w), pr * q)); };
      walk([], 1); all.sort((a, b) => b[1] - a[1]);
      const sc = v => (p.logs ? f2(Math.log(v), 3) : f2(v, 4));
      const cols = [16, 150, 290, 420];
      ['start', 'step 1', 'step 2', 'step 3'].forEach((t, i) => D.text(g, t, cols[i], 22, { s: 12, b: true, c: i <= z.step ? z.col.ink : z.col.line }));
      hist.slice(0, z.step + 1).forEach((bm, s) => {
        bm.forEach(([seq, pr], r) => {
          const txt = seq.length ? seq.filter(w => w !== 'END').join(' ') + (seq[seq.length - 1] === 'END' ? ' ■' : '') : '<s>';
          const y = 34 + r * 46;
          rr(g, cols[s], y, 124, 38, 6, { fill: r === 0 ? z.col.cv : z.col.bg, stroke: z.col.line });
          D.text(g, txt, cols[s] + 6, y + 16, { s: fit(g, txt, 112, 12), b: true, c: r === 0 ? '#fff' : z.col.ink });
          D.text(g, `${p.logs ? 'log p' : 'p'} = ${sc(pr)}`, cols[s] + 6, y + 31, { s: 10.5, mono: true, c: r === 0 ? '#fff' : z.col.ink2 });
        });
      });
      const best = hist[hist.length - 1][0];
      D.text(g, `best of all ${all.length} sentences: ${all[0][0].filter(w => w !== 'END').join(' ')}  (p = ${f2(all[0][1], 4)})`, 16, 282, { s: 12.5, b: true, c: z.col.green });
      D.text(g, `beam k = ${p.k} returns: ${best[0].filter(w => w !== 'END').join(' ')}  (p = ${f2(best[1], 4)})`, 16, 304, { s: 12.5, b: true, c: best[1] >= all[0][1] - 1e-12 ? z.col.green : z.col.red });
      return `Beam search keeps k hypotheses and scores each by log P(y<sub>1</sub> … y<sub>t</sub> | x) = ∑ log P(y<sub>i</sub> | y<sub>&lt;i</sub>, x). It costs about k times greedy and still is not guaranteed to find the best sentence, only to look at more of them.`;
    }
  });

  def('sampling', {
    title: 'Sampling the next word: temperature, top-k and top-p',
    sub: 'Greedy and beam search are deterministic. Sampling adds controlled randomness. The bars show the final distribution that is sampled from.',
    W: 560, H: 300,
    params: [
      { k: 'logits', label: 'Next-word scores "word score" per line', type: 'area', v: 'books 3.0\nlaptops 2.5\nexams 2.0\nminds 1.0\nzoo -1.0\nbananas -2.0' },
      { k: 'T', label: 'Temperature T', v: 1, min: 0.1, max: 3, step: 0.05 },
      { k: 'topk', label: 'Top-k (0 = off)', v: 0, min: 0, max: 6 },
      { k: 'topp', label: 'Top-p nucleus (1 = off)', v: 1, min: 0.1, max: 1, step: 0.05 },
      { k: 'seed', label: 'Random seed for 20 samples', v: 5, min: 1, max: 99 }
    ],
    tips: [
      { t: 'T = 0.3 makes the distribution sharp, almost greedy: "books" nearly every time. High quality, low diversity.', set: { T: 0.3, topk: 0, topp: 1 } },
      { t: 'T = 2 flattens it. Even "bananas" now gets picked sometimes, more diverse but less sensible.', set: { T: 2, topk: 0, topp: 1 } },
      { t: 'Top-k = 3 cuts every word outside the best three, then renormalises.', set: { T: 1, topk: 3, topp: 1 } },
      { t: 'Top-p = 0.9 keeps the smallest set of words whose probabilities add to at least 0.9. Its size adapts to how sure the model is.', set: { T: 1, topk: 0, topp: 0.9 } }
    ],
    draw(z) {
      const { g, p } = z;
      const L = NLZ.pairs(p.logits).slice(0, 8);
      if (!L.length) return 'Write lines like "books 3.0".';
      let P = softmax(L.map(r => r[1] / p.T));
      const order = P.map((v, i) => [v, i]).sort((a, b) => b[0] - a[0]);
      const keep = new Set();
      let cum = 0;
      order.forEach(([v, i], r) => { if ((p.topk === 0 || r < p.topk) && (cum < p.topp - 1e-12 || r === 0)) keep.add(i); cum += v; });
      const Q = P.map((v, i) => keep.has(i) ? v : 0), s = Q.reduce((a, b) => a + b, 0), F = Q.map(v => v / s);
      bars(g, z, [30, 26, 330, 210], F, L.map(r => r[0]), { max: 1, colors: F.map(v => v ? z.col.cv : z.col.line) });
      const r = rng(p.seed), draws = [];
      for (let k = 0; k < 20; k++) { let u = r(), i = 0; while (i < F.length - 1 && u > F[i]) { u -= F[i]; i++; } draws.push(L[i][0]); }
      const cnt = {}; draws.forEach(d => { cnt[d] = (cnt[d] || 0) + 1; });
      D.text(g, '20 samples:', 392, 34, { s: 12.5, b: true, c: z.col.ink });
      Object.entries(cnt).sort((a, b) => b[1] - a[1]).forEach(([w, c], i) => D.text(g, `${w} × ${c}`, 400, 58 + i * 20, { s: 12, mono: true, c: z.col.ink }));
      const H = -F.reduce((a, v) => a + (v > 0 ? v * Math.log2(v) : 0), 0);
      return `p<sub>i</sub> = exp(s<sub>i</sub>/T) ÷ ∑ exp(s<sub>j</sub>/T). Kept ${keep.size} of ${L.length} words. Entropy of what is sampled: ${f2(H, 3)} bits. Lower T, smaller k or smaller p give safer and more repetitive text.`;
    }
  });
})();
