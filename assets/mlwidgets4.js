/* ===== Complete Machine Learning animations, part 4: deep learning.
   Uses the framework MLZ from assets/mlwidgets.js. Every animation starts empty and adds one step each time Step
   is pressed, with a plain English line for that step. ===== */

/* =====================================================================================================
   Deep learning 1.1  neural networks: the perceptron learning rule, and hidden units that bend the boundary
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, rng, plot, box } = MLZ;
  const nf = v => (Number.isInteger(v) ? String(v).replace('-', '−') : f2(v, 2).replace('-', '−'));
  const PTS = {
    sep: [[0.2, 0.9, 1], [0.5, 0.8, 1], [0.8, 0.95, 1], [0.35, 0.6, 1], [0.9, 0.6, 1], [0.6, 0.55, 1], [0.1, 0.3, 0], [0.4, 0.2, 0], [0.7, 0.1, 0], [0.2, 0.05, 0], [0.55, 0.3, 0], [0.9, 0.25, 0]],
    xor: [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]
  };

  trace('mlperceptron', {
    title: 'The perceptron learning rule',
    sub: 'A perceptron draws one straight line w₁x₁ + w₂x₂ + b = 0 and fires (class 1, blue) on one side. It visits the points in turn. When it is wrong, it adds the point to w (or subtracts it), which turns the line towards the right answer.',
    W: 600, H: 330,
    params: [
      { k: 'd', label: 'Data', type: 'select', v: 'sep', opts: [['sep', '12 points a line can separate'], ['xor', 'XOR: 4 corner points']] },
      { k: 'lr', label: 'Learning rate', type: 'range', v: 1, min: 0.2, max: 2, step: 0.2 }
    ],
    tips: [
      { t: 'XOR: no straight line puts (0, 1) and (1, 0) on one side and (0, 0) and (1, 1) on the other, so the perceptron keeps making mistakes forever.', set: { d: 'xor', lr: 1 }, play: true },
      { t: 'Learning rate 0.2: the steps are smaller, but because the line only depends on the direction of w and b, the perceptron still finds a separating line.', set: { d: 'sep', lr: 0.2 }, play: true }
    ],
    frames(p) {
      const pts = PTS[p.d], lr = +p.lr;
      let w = [0, 0], b = 0;
      const fr = [{ w: w.slice(), b, pts, say: 'All weights start at 0, so the perceptron outputs 0 (orange) for every point. It will now visit the points in order.' }];
      let shown = 0, done = false;
      for (let ep = 1; ep <= 12 && !done; ep++) {
        let mist = 0;
        pts.forEach((q, i) => {
          const s = w[0] * q[0] + w[1] * q[1] + b, pred = s > 0 ? 1 : 0;
          if (pred !== q[2]) {
            mist++;
            const d = lr * (q[2] - pred), old = [w[0], w[1], b];
            w = [w[0] + d * q[0], w[1] + d * q[1]]; b += d;
            if (shown < 14) { shown++; fr.push({ w: w.slice(), b, pts, hot: i, ep, say: `Epoch ${ep}: point (${f2(q[0], 2)}, ${f2(q[1], 2)}) is class ${q[2]} but w·x + b = ${nf(+s.toFixed(2))} gives ${pred}. ${q[2] ? 'Add' : 'Subtract'} ${f2(lr, 1)} × the point: w = (${nf(+old[0].toFixed(2))}, ${nf(+old[1].toFixed(2))}) becomes (${nf(+w[0].toFixed(2))}, ${nf(+w[1].toFixed(2))}), b becomes ${nf(+b.toFixed(2))}.` }); }
          }
        });
        if (mist === 0) { done = true; fr.push({ w: w.slice(), b, pts, ep, say: `Epoch ${ep} makes <b>no mistakes</b>: every point is on its correct side, so learning stops. Rosenblatt proved this always happens when some line can separate the classes.` }); }
        else if (ep === 12 || (p.d === 'xor' && ep % 4 === 0)) fr.push({ w: w.slice(), b, pts, ep, say: `End of epoch ${ep}: still ${mist} mistake${mist === 1 ? '' : 's'}. ${p.d === 'xor' ? 'The line keeps swinging back and forth, because XOR cannot be split by any straight line.' : ''}` });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, isX = f.pts.length === 4, lo = isX ? -0.4 : -0.1, hi = isX ? 1.4 : 1.1;
      const P = plot(z, [10, 10, 400, 310], [lo, hi], [lo, hi], { dx: 1, dy: 1, xl: 'x₁', yl: 'x₂' });
      const [w1, w2] = f.w, b = f.b;
      if (w1 || w2) {
        const cell = 10; g.save(); g.globalAlpha = 0.16;
        for (let px = P.x0 + 26; px < P.x0 + P.w - 10; px += cell) for (let py = P.y0 + 10; py < P.y0 + P.h - 20; py += cell) {
          const x = lo + (px + cell / 2 - P.x0 - 26) / (P.w - 36) * (hi - lo), y = lo + (P.y0 + P.h - 20 - (py + cell / 2)) / (P.h - 30) * (hi - lo);
          g.fillStyle = klass(z, w1 * x + w2 * y + b > 0 ? 0 : 1); g.fillRect(px, py, cell, cell);
        }
        g.restore();
        if (Math.abs(w2) > 1e-9) D.line(g, P.X(lo), P.Y((-b - w1 * lo) / w2), P.X(hi), P.Y((-b - w1 * hi) / w2), c.ink, 2.5);
        else D.line(g, P.X(-b / w1), P.Y(lo), P.X(-b / w1), P.Y(hi), c.ink, 2.5);
      }
      f.pts.forEach((q, i) => D.circle(g, P.X(q[0]), P.Y(q[1]), i === f.hot ? 9 : 6, { fill: klass(z, q[2] ? 0 : 1), stroke: i === f.hot ? c.red : c.surf, w: i === f.hot ? 3 : 1 }));
      head(z, 'Weights', 430, 40);
      box(z, 430, 52, 150, 32, `w₁ = ${nf(+w1.toFixed(2))}`, { mono: true, s: 13 });
      box(z, 430, 92, 150, 32, `w₂ = ${nf(+w2.toFixed(2))}`, { mono: true, s: 13 });
      box(z, 430, 132, 150, 32, `b = ${nf(+b.toFixed(2))}`, { mono: true, s: 13 });
      D.text(g, 'blue dot: class 1', 430, 196, { s: 11, c: klass(z, 0), b: true });
      D.text(g, 'orange dot: class 0', 430, 214, { s: 11, c: klass(z, 1), b: true });
      D.text(g, 'red ring: the point just used', 430, 232, { s: 11, c: c.red });
      D.text(g, 'rule: w += lr (y − ŷ) x', 430, 270, { s: 11, mono: true, b: true, c: c.cv });
      D.text(g, '        b += lr (y − ŷ)', 430, 288, { s: 11, mono: true, b: true, c: c.cv });
    }
  });

  const makeData = (kind, R) => {
    const pts = [];
    if (kind === 'xor') { for (let i = 0; i < 60; i++) { const x = R() * 2 - 1, y = R() * 2 - 1; pts.push([x, y, x * y > 0 ? 0 : 1]); } }
    else if (kind === 'circle') { for (let i = 0; i < 80; i++) { const x = R() * 2 - 1, y = R() * 2 - 1; pts.push([x, y, x * x + y * y < 0.4 ? 1 : 0]); } }
    else { for (let i = 0; i < 80; i++) { const x = R() * 2 - 1, y = R() * 2 - 1; pts.push([x, y, y > 0.3 * x - 0.1 ? 1 : 0]); } }
    return pts;
  };
  trace('mlhidden', {
    title: 'Hidden units bend the boundary',
    sub: 'A network with one hidden layer of tanh units and a sigmoid output, trained by gradient descent. Each hidden unit draws its own line, and the output combines them, so the boundary can curve. The shading is the network’s probability of blue.',
    W: 600, H: 330,
    params: [
      { k: 'd', label: 'Data', type: 'select', v: 'xor', opts: [['xor', 'XOR quadrants'], ['circle', 'A circle inside a square'], ['line', 'A straight line']] },
      { k: 'h', label: 'Hidden units', type: 'select', v: '4', opts: [['1', '1'], ['2', '2'], ['4', '4'], ['8', '8']] },
      { k: 'seed', label: 'Random seed', type: 'range', v: 2, min: 1, max: 30 }
    ],
    tips: [
      { t: '1 hidden unit on XOR: one unit can only draw one line, so the network cannot get the four quadrants right.', set: { d: 'xor', h: '1', seed: 2 }, play: true },
      { t: '8 hidden units on the circle: many lines together approximate a round boundary.', set: { d: 'circle', h: '8', seed: 2 }, play: true }
    ],
    frames(p) {
      const R = rng(+p.seed * 7717), H = +p.h, pts = makeData(p.d, rng(99)), lr = 0.5;
      const W1 = Array.from({ length: H }, () => [R() * 2 - 1, R() * 2 - 1].map(v => v * 1.5)), b1 = Array.from({ length: H }, () => (R() - 0.5));
      const W2 = Array.from({ length: H }, () => R() * 2 - 1), b2 = [0];
      const fwd = (x, y) => { const h = W1.map((w, j) => Math.tanh(w[0] * x + w[1] * y + b1[j])); const o = h.reduce((a, v, j) => a + v * W2[j], b2[0]); return [h, 1 / (1 + Math.exp(-o))]; };
      const stats = () => { let L = 0, ok = 0; pts.forEach(q => { const pr = fwd(q[0], q[1])[1]; L -= q[2] ? Math.log(pr + 1e-9) : Math.log(1 - pr + 1e-9); ok += (pr > 0.5 ? 1 : 0) === q[2] ? 1 : 0; }); return [L / pts.length, ok / pts.length]; };
      const snap = () => ({ W1: W1.map(r => r.slice()), b1: b1.slice(), W2: W2.slice(), b2: b2[0] });
      const [L0, A0] = stats();
      const fr = [{ net: snap(), pts, H, say: `Random starting weights for ${H} hidden unit${H > 1 ? 's' : ''}. Loss ${f2(L0, 3)}, accuracy ${f2(A0 * 100, 0)}%. The thin lines show where each hidden unit changes sign.` }];
      const show = [20, 100, 300, 1000, 3000];
      for (let it = 1; it <= 3000; it++) {
        const gW1 = W1.map(() => [0, 0]), gb1 = new Array(H).fill(0), gW2 = new Array(H).fill(0); let gb2 = 0;
        pts.forEach(q => {
          const [h, pr] = fwd(q[0], q[1]), d = (pr - q[2]) / pts.length;
          gb2 += d;
          h.forEach((hv, j) => { gW2[j] += d * hv; const dh = d * W2[j] * (1 - hv * hv); gW1[j][0] += dh * q[0]; gW1[j][1] += dh * q[1]; gb1[j] += dh; });
        });
        for (let j = 0; j < H; j++) { W1[j][0] -= lr * gW1[j][0]; W1[j][1] -= lr * gW1[j][1]; b1[j] -= lr * gb1[j]; W2[j] -= lr * gW2[j]; }
        b2[0] -= lr * gb2;
        if (show.includes(it)) {
          const [L, A] = stats();
          fr.push({ net: snap(), pts, H, say: `After ${it} gradient steps: loss ${f2(L, 3)}, accuracy <b>${f2(A * 100, 0)}%</b>.${it === 3000 ? (A >= 0.95 ? ' The hidden units have learned features that make the classes separable.' : ` With ${H} hidden unit${H > 1 ? 's' : ''} the network is not flexible enough, or got stuck, so some points stay wrong.`) : ''}` });
        }
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, n = f.net;
      const fwd = (x, y) => { const h = n.W1.map((w, j) => Math.tanh(w[0] * x + w[1] * y + n.b1[j])); const o = h.reduce((a, v, j) => a + v * n.W2[j], n.b2); return 1 / (1 + Math.exp(-o)); };
      const P = plot(z, [10, 10, 400, 310], [-1, 1], [-1, 1], { dx: 1, dy: 1, xl: 'x₁', yl: 'x₂' });
      const cell = 8; g.save();
      for (let px = P.x0 + 26; px < P.x0 + P.w - 10; px += cell) for (let py = P.y0 + 10; py < P.y0 + P.h - 20; py += cell) {
        const x = -1 + (px + cell / 2 - P.x0 - 26) / (P.w - 36) * 2, y = -1 + (P.y0 + P.h - 20 - (py + cell / 2)) / (P.h - 30) * 2, pr = fwd(x, y);
        g.globalAlpha = 0.08 + 0.3 * Math.abs(pr - 0.5) * 2; g.fillStyle = klass(z, pr > 0.5 ? 0 : 1); g.fillRect(px, py, cell, cell);
      }
      g.restore();
      g.save(); g.beginPath(); g.rect(P.x0 + 26, P.y0 + 10, P.w - 36, P.h - 30); g.clip();
      n.W1.forEach((w, j) => { if (Math.abs(w[1]) > 1e-6) D.line(g, P.X(-1), P.Y((-n.b1[j] + w[0]) / w[1]), P.X(1), P.Y((-n.b1[j] - w[0]) / w[1]), c.ink2, 1, [4, 4]); });
      g.restore();
      f.pts.forEach(q => D.circle(g, P.X(q[0]), P.Y(q[1]), 4, { fill: klass(z, q[2] ? 0 : 1), stroke: c.surf, w: 1 }));
      head(z, 'Network', 430, 30);
      const hx = 505, ox = 570;
      [0, 1].forEach(i => { D.circle(g, 445, 90 + i * 90, 12, { fill: c.surf, stroke: c.line, w: 1.5 }); D.text(g, 'x' + (i ? '₂' : '₁'), 445, 94 + i * 90, { a: 'center', s: 11, b: true, c: c.ink }); });
      const H = n.W1.length;
      n.W1.forEach((w, j) => {
        const y = 60 + j * (180 / Math.max(1, H - 1 || 1)) * (H > 1 ? 1 : 0) + (H === 1 ? 75 : 0);
        [0, 1].forEach(i => D.line(g, 457, 90 + i * 90, hx - 10, y, w[i] > 0 ? klass(z, 0) : klass(z, 1), Math.min(4, 0.5 + Math.abs(w[i]))));
        D.line(g, hx + 10, y, ox - 12, 135, n.W2[j] > 0 ? klass(z, 0) : klass(z, 1), Math.min(4, 0.5 + Math.abs(n.W2[j])));
        D.circle(g, hx, y, 9, { fill: c.surf, stroke: c.ink2, w: 1.5 });
      });
      D.circle(g, ox, 135, 12, { fill: c.surf, stroke: c.line, w: 1.5 }); D.text(g, 'p', ox, 139, { a: 'center', s: 11, b: true, c: c.ink });
      D.text(g, 'line colour: sign of the weight', 425, 268, { s: 10, c: c.ink2 });
      D.text(g, 'line width: its size', 425, 284, { s: 10, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Deep learning 1.2  backpropagation: a computational graph forward and backward, and gradients through depth
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, rng, plot, box } = MLZ;
  const nf = v => { const r = Math.abs(v) < 5e-4 ? 0 : v; return (Number.isInteger(r) ? String(r) : f2(r, 3)).replace('-', '−'); };
  const pn = v => (v < 0 ? '(' + nf(v) + ')' : nf(v));
  const GRAPHS = {
    add: { nodes: [
      { id: 'x', x: 60, y: 60 }, { id: 'y', x: 60, y: 150 }, { id: 'z', x: 60, y: 250 },
      { id: 'q', op: '+', ins: ['x', 'y'], x: 250, y: 105 }, { id: 'f', op: '×', ins: ['q', 'z'], x: 440, y: 170 }] },
    neuron: { nodes: [
      { id: 'w0', x: 40, y: 30 }, { id: 'x0', x: 40, y: 90 }, { id: 'w1', x: 40, y: 160 }, { id: 'x1', x: 40, y: 220 }, { id: 'b', x: 40, y: 290 },
      { id: 'm0', op: '×', ins: ['w0', 'x0'], x: 170, y: 60 }, { id: 'm1', op: '×', ins: ['w1', 'x1'], x: 170, y: 190 },
      { id: 's1', op: '+', ins: ['m0', 'm1'], x: 290, y: 125 }, { id: 's2', op: '+', ins: ['s1', 'b'], x: 400, y: 200 }, { id: 'f', op: 'σ', ins: ['s2'], x: 520, y: 200 }] }
  };

  trace('mlcompgraph', {
    title: 'Backpropagation on a computational graph',
    sub: 'Every calculation is a graph of small operations. The forward pass computes each value (green) from left to right. The backward pass starts with a gradient of 1 at the output and sends gradients (red) back with the chain rule: each node multiplies the incoming gradient by its own local slope.',
    W: 600, H: 330,
    params: [
      { k: 'g', label: 'Graph', type: 'select', v: 'add', opts: [['add', 'f = (x + y) × z'], ['neuron', 'A sigmoid neuron: f = σ(w₀x₀ + w₁x₁ + b)']] },
      { k: 'x', label: 'x (first graph)', type: 'range', v: -2, min: -5, max: 5, step: 1 },
      { k: 'y', label: 'y (first graph)', type: 'range', v: 5, min: -5, max: 5, step: 1 },
      { k: 'z', label: 'z (first graph)', type: 'range', v: -4, min: -5, max: 5, step: 1 }
    ],
    tips: [
      { t: 'The neuron graph: the sigmoid’s local slope is σ(1)(1 − σ(1)) = 0.197, and every input then gets its share through the adds and multiplies.', set: { g: 'neuron' }, play: true },
      { t: 'Set z = 0: then f = 0 for any x and y, and the gradients reaching x and y are 0 too, because the multiply sends z × (incoming gradient) to q.', set: { g: 'add', x: -2, y: 5, z: 0 }, play: true }
    ],
    frames(p) {
      const G = GRAPHS[p.g], val = {}, grad = {};
      if (p.g === 'add') { val.x = +p.x; val.y = +p.y; val.z = +p.z; } else Object.assign(val, { w0: 2, x0: -1, w1: -3, x1: -2, b: -3 });
      const ops = G.nodes.filter(n => n.op), snap = (extra) => ({ g: p.g, val: { ...val }, grad: { ...grad }, ...extra });
      const fr = [snap({ say: `The inputs: ${G.nodes.filter(n => !n.op).map(n => `${n.id} = ${nf(val[n.id])}`).join(', ')}. Nothing else is computed yet.` })];
      ops.forEach(n => {
        const a = n.ins.map(i => val[i]);
        val[n.id] = n.op === '+' ? a[0] + a[1] : n.op === '×' ? a[0] * a[1] : 1 / (1 + Math.exp(-a[0]));
        fr.push(snap({ hot: n.id, say: `Forward: ${n.id} = ${n.op === 'σ' ? `σ(${nf(a[0])})` : `${pn(a[0])} ${n.op} ${pn(a[1])}`} = <b>${nf(val[n.id])}</b>.` }));
      });
      const out = ops[ops.length - 1].id;
      grad[out] = 1;
      fr.push(snap({ hot: out, say: `Backward starts at the output with ∂f/∂f = 1.` }));
      [...ops].reverse().forEach(n => {
        const g0 = grad[n.id], a = n.ins.map(i => val[i]);
        let parts;
        if (n.op === '+') { n.ins.forEach(i => (grad[i] = (grad[i] || 0) + g0)); parts = `an add passes the gradient ${nf(g0)} unchanged to ${n.ins.join(' and ')}`; }
        else if (n.op === '×') { grad[n.ins[0]] = (grad[n.ins[0]] || 0) + g0 * a[1]; grad[n.ins[1]] = (grad[n.ins[1]] || 0) + g0 * a[0]; parts = `a multiply swaps its inputs: ∂/∂${n.ins[0]} = ${pn(g0)} × ${pn(a[1])} = ${nf(g0 * a[1])} and ∂/∂${n.ins[1]} = ${pn(g0)} × ${pn(a[0])} = ${nf(g0 * a[0])}`; }
        else { const s = val[n.id], d = s * (1 - s); grad[n.ins[0]] = (grad[n.ins[0]] || 0) + g0 * d; parts = `the sigmoid’s local slope is σ(1 − σ) = ${nf(s)} × ${nf(1 - s)} = ${nf(d)}, so ∂/∂${n.ins[0]} = ${nf(g0 * d)}`; }
        fr.push(snap({ hot: n.id, say: `Backward through ${n.id}: ${parts}.` }));
      });
      const ins = G.nodes.filter(n => !n.op);
      fr.push(snap({ say: `Done. Gradients of f: ${ins.map(n => `∂f/∂${n.id} = <b>${nf(grad[n.id])}</b>`).join(', ')}. One forward and one backward pass gave every gradient at once.` }));
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, G = GRAPHS[f.g], pos = {};
      G.nodes.forEach(n => (pos[n.id] = n));
      G.nodes.filter(n => n.op).forEach(n => n.ins.forEach(i => D.arrow(g, pos[i].x + (pos[i].op ? 22 : 42), pos[i].y, n.x - 24, n.y, c.ink2, 1.5, 7)));
      G.nodes.forEach(n => {
        const hot = f.hot === n.id;
        if (n.op) D.circle(g, n.x, n.y, 22, { fill: hot ? 'rgba(234,88,12,0.2)' : c.surf, stroke: hot ? klass(z, 1) : c.line, w: hot ? 3 : 1.5 });
        else rr(g, n.x - 22, n.y - 16, 64, 32, 6, { fill: c.surf, stroke: c.line });
        if (n.op) {
          D.text(g, n.op, n.x, n.y + 5, { a: 'center', s: 16, b: true, c: c.ink });
          D.text(g, n.id, n.x, n.y - 27, { a: 'center', s: 10, c: c.ink2 });
          if (f.val[n.id] !== undefined) D.text(g, nf(f.val[n.id]), n.x + 26, n.y - 14, { a: 'left', s: 12, b: true, c: c.green });
          if (f.grad[n.id] !== undefined) D.text(g, nf(f.grad[n.id]), n.x, n.y + 38, { a: 'center', s: 12, b: true, c: c.red });
        } else {
          D.text(g, n.id, n.x - 15, n.y + 5, { a: 'left', s: 13, b: true, c: c.ink });
          if (f.val[n.id] !== undefined) D.text(g, nf(f.val[n.id]), n.x + 36, n.y + 5, { a: 'right', s: 12, b: true, c: c.green });
          if (f.grad[n.id] !== undefined) D.text(g, nf(f.grad[n.id]), n.x + 10, n.y + 30, { a: 'center', s: 12, b: true, c: c.red });
        }
      });
      D.text(g, 'green: value (forward)    red: gradient ∂f/∂node (backward)', 590, 322, { a: 'right', s: 11, c: c.ink2 });
    }
  });

  const gauss = R => { let u = 0; while (u === 0) u = R(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * R()); };
  trace('mlvanish', {
    title: 'Vanishing and exploding gradients',
    sub: 'A batch goes forward through a deep stack of layers. Then a gradient of 1s comes back from the top, and we measure its average size at each layer on a log scale. Healthy training needs sizes that stay roughly level from layer to layer.',
    W: 600, H: 330,
    params: [
      { k: 'act', label: 'Activation', type: 'select', v: 'sigmoid', opts: [['sigmoid', 'sigmoid'], ['tanh', 'tanh'], ['relu', 'ReLU']] },
      { k: 'init', label: 'Weight initialisation', type: 'select', v: 'xavier', opts: [['small', 'small: N(0, 0.01²)'], ['xavier', 'Xavier: N(0, 1/n)'], ['he', 'He: N(0, 2/n)'], ['big', 'too big: N(0, 4/n)']] },
      { k: 'L', label: 'Number of layers', type: 'select', v: '20', opts: [['10', '10'], ['20', '20'], ['30', '30']] }
    ],
    tips: [
      { t: 'ReLU with He initialisation: the gradient size stays roughly the same at every layer, which is what He and colleagues designed it for.', set: { act: 'relu', init: 'he', L: '20' }, play: true },
      { t: 'ReLU with “too big” weights: each layer multiplies the gradient by more than 1, so it explodes on the way back, about 2000 times larger at layer 1.', set: { act: 'relu', init: 'big', L: '20' }, play: true }
    ],
    frames(p) {
      const R = rng(1234), L = +p.L, n = 32, B = 48, act = p.act;
      const sc = { small: 0.01, xavier: Math.sqrt(1 / n), he: Math.sqrt(2 / n), big: Math.sqrt(4 / n) }[p.init];
      let x = Array.from({ length: B }, () => Array.from({ length: n }, () => gauss(R)));
      const Ws = [], Zs = [];
      for (let l = 0; l < L; l++) {
        const W = Array.from({ length: n }, () => Array.from({ length: n }, () => gauss(R) * sc));
        const Z = x.map(r => W[0].map((_, j) => r.reduce((a, v, k) => a + v * W[k][j], 0)));
        x = Z.map(r => r.map(v => (act === 'sigmoid' ? 1 / (1 + Math.exp(-v)) : act === 'tanh' ? Math.tanh(v) : Math.max(0, v))));
        Ws.push(W); Zs.push(Z);
      }
      let gmat = x.map(r => r.map(() => 1));
      const sizes = new Array(L);
      for (let l = L - 1; l >= 0; l--) {
        const Z = Zs[l], W = Ws[l];
        const dz = gmat.map((r, i) => r.map((v, j) => { const zv = Z[i][j]; const d = act === 'sigmoid' ? (s => s * (1 - s))(1 / (1 + Math.exp(-zv))) : act === 'tanh' ? 1 - Math.tanh(zv) ** 2 : zv > 0 ? 1 : 0; return v * d; }));
        gmat = dz.map(r => W.map((wr) => wr.reduce((a, wv, j) => a + wv * r[j], 0)));
        sizes[l] = gmat.reduce((a, r) => a + r.reduce((b, v) => b + Math.abs(v), 0), 0) / (B * n);
      }
      const fr = [{ sizes, upto: L, L, say: `${L} layers of ${n} units, ${act} activations, ${p.init} initialisation. The forward pass is done. Now the gradient travels back from layer ${L}.` }];
      const chunk = Math.max(2, Math.round(L / 5));
      for (let k = L - chunk; k > 0; k -= chunk) fr.push({ sizes, upto: k, L, say: `Back to layer ${k + 1}: average gradient size ${sizes[k].toExponential(1)}, compared with ${sizes[L - 1].toExponential(1)} at layer ${L}.` });
      const ratio = sizes[0] / sizes[L - 1];
      fr.push({ sizes, upto: 0, L, say: `At layer 1 the gradient is ${sizes[0].toExponential(1)}, ${ratio < 1 ? `${(1 / ratio).toExponential(1)} times smaller` : `${ratio.toExponential(1)} times larger`} than at layer ${L}. ${ratio < 1e-3 ? '<b>Vanishing</b>: the first layers would barely learn.' : ratio < 0.1 ? '<b>Shrinking</b>: the first layers would learn much more slowly than the last.' : ratio > 1e3 ? '<b>Exploding</b>: updates to the first layers would be huge.' : ratio > 10 ? '<b>Growing</b>: a mild form of exploding, the first layers get much larger updates.' : '<b>Healthy</b>: every layer gets a gradient of a similar size.'}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, L = f.L;
      const P = plot(z, [10, 10, 580, 300], [0.5, L + 0.5], [-24, 4], { dx: 0, dy: 0, xl: 'layer (1 = first)', yl: 'log₁₀ of average gradient size', grid: true });
      D.line(g, P.X(0.5), P.Y(0), P.X(L + 0.5), P.Y(0), c.ink2, 1, [4, 4]);
      const bw = (P.X(2) - P.X(1)) * 0.7;
      for (let l = 0; l < L; l++) {
        if (l < f.upto) continue;
        const v = Math.max(-24, Math.min(4, Math.log10(f.sizes[l] + 1e-30)));
        const x = P.X(l + 1) - bw / 2, y0 = P.Y(v), yb = P.Y(0), h = Math.max(3, Math.abs(yb - y0));
        rr(g, x, v >= 0 ? yb - h : yb, bw, h, 2, { fill: v < -3 ? c.red : v > 3 ? klass(z, 1) : klass(z, 0) });
      }
      D.text(g, 'bars grow from size 1 (dashed)   blue: healthy   red: below 0.001   orange: above 1000', 585, 270, { a: 'right', s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Deep learning 1.3  training in practice: optimisers in a narrow valley, and regularisation against overfitting
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, rng, plot } = MLZ;
  const KAP = 100, START = [-4, 1.5];
  const lossAt = p => 0.5 * (p[0] * p[0] + KAP * p[1] * p[1]);
  const OPTS = ['SGD', 'Momentum', 'RMSprop', 'Adam'];
  const LRS = { tuned: { SGD: 0.019, Momentum: 0.01, RMSprop: 0.1, Adam: 0.1 }, same: { SGD: 0.021, Momentum: 0.021, RMSprop: 0.021, Adam: 0.021 } };
  const SHOW = [0, 1, 2, 3, 5, 8, 12, 20, 30, 45, 60];
  const fe = v => (!isFinite(v) || v > 1e6 ? 'diverged' : v < 1e-3 ? v.toExponential(1).replace('-', '−') : f2(v, 3));

  function path(name, lr) {
    let p = START.slice(), v = [0, 0], s = [0, 0];
    const out = [p.slice()];
    for (let t = 1; t <= 60; t++) {
      const g = [p[0], KAP * p[1]];
      for (let i = 0; i < 2; i++) {
        if (name === 'SGD') p[i] -= lr * g[i];
        else if (name === 'Momentum') { v[i] = 0.9 * v[i] + g[i]; p[i] -= lr * v[i]; }
        else if (name === 'RMSprop') { s[i] = 0.9 * s[i] + 0.1 * g[i] * g[i]; p[i] -= lr * g[i] / (Math.sqrt(s[i]) + 1e-8); }
        else { v[i] = 0.9 * v[i] + 0.1 * g[i]; s[i] = 0.999 * s[i] + 0.001 * g[i] * g[i]; p[i] -= lr * (v[i] / (1 - 0.9 ** t)) / (Math.sqrt(s[i] / (1 - 0.999 ** t)) + 1e-8); }
      }
      out.push(p.slice());
    }
    return out;
  }

  trace('mloptim', {
    title: 'Optimisers in a long, narrow valley',
    sub: 'The loss f = ½(x² + 100y²) is a valley 100 times more curved across (y) than along (x). Every optimiser starts at (−4, 1.5) and aims for the minimum at (0, 0). Watch how each one moves over 60 steps.',
    W: 600, H: 330,
    params: [
      { k: 'show', label: 'Optimisers', type: 'select', v: 'all', opts: [['all', 'All four'], ...OPTS.map(o => [o, o + ' only'])] },
      { k: 'lr', label: 'Learning rates', type: 'select', v: 'tuned', opts: [['tuned', 'Tuned for each (SGD 0.019, Momentum 0.01, RMSprop and Adam 0.1)'], ['same', 'All 0.021, just above the SGD limit 2/100']] }
    ],
    tips: [
      { t: 'All at 0.021: plain SGD crosses the valley further each step and diverges, because its rate is above 2/100. Momentum, RMSprop and Adam stay stable at the same rate.', set: { show: 'all', lr: 'same' }, play: true },
      { t: 'SGD only: with the largest safe rate it zigzags across the steep y direction while crawling along the shallow x direction.', set: { show: 'SGD', lr: 'tuned' }, play: true }
    ],
    frames(p) {
      const names = p.show === 'all' ? OPTS : [p.show], lr = LRS[p.lr];
      const paths = {}; names.forEach(n => (paths[n] = path(n, lr[n])));
      return SHOW.map((t, k) => {
        const L = names.map(n => [n, lossAt(paths[n][t])]);
        let say;
        if (t === 0) say = `Step 0. Every optimiser starts at (−4, 1.5), where the loss is ${f2(lossAt(START), 1)}. ${p.lr === 'same' ? 'All use learning rate 0.021.' : 'Each uses its own tuned learning rate.'}`;
        else if (k < SHOW.length - 1) say = `After ${t} step${t > 1 ? 's' : ''}: ` + L.map(([n, v]) => `${n} ${fe(v)}`).join(', ') + '.';
        else {
          const ok = L.filter(([, v]) => isFinite(v) && v < 1e6).sort((a, b) => a[1] - b[1]);
          say = `After 60 steps: ` + L.map(([n, v]) => `${n} <b>${fe(v)}</b>`).join(', ') + '.' + (ok.length > 1 ? ` Lowest: ${ok[0][0]}.` : '') + (L.some(([, v]) => !(v < 1e6)) ? ' A diverged run has a learning rate too large for the steep direction.' : '');
        }
        return { t, names, paths, say };
      });
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 310], [-5, 5], [-2, 2], { dx: 1, dy: 0, xl: 'x', yl: 'y' });
      g.save(); g.beginPath(); g.rect(P.x0 + 26, P.y0 + 10, P.w - 36, P.h - 30); g.clip();
      [0.5, 2, 5, 10, 20, 40, 80, 120].forEach(lv => {
        g.beginPath();
        for (let a = 0; a <= 64; a++) { const th = a / 64 * 2 * Math.PI, x = Math.sqrt(2 * lv) * Math.cos(th), y = Math.sqrt(2 * lv / KAP) * Math.sin(th); a ? g.lineTo(P.X(x), P.Y(y)) : g.moveTo(P.X(x), P.Y(y)); }
        g.strokeStyle = c.line; g.lineWidth = 1; g.stroke();
      });
      f.names.forEach(n => {
        const col = klass(z, OPTS.indexOf(n)), pts = f.paths[n].slice(0, f.t + 1);
        const inside = q => Math.abs(q[0]) < 6 && Math.abs(q[1]) < 3, last = pts.findIndex(q => !inside(q));
        g.beginPath(); pts.slice(0, last < 0 ? pts.length : last + 1).forEach((q, i) => { const X = P.X(Math.max(-6, Math.min(6, q[0]))), Y = P.Y(Math.max(-3, Math.min(3, q[1]))); i ? g.lineTo(X, Y) : g.moveTo(X, Y); });
        g.strokeStyle = col; g.lineWidth = 2; g.stroke();
        const q = pts[pts.length - 1];
        if (Math.abs(q[0]) < 5 && Math.abs(q[1]) < 2.5) D.circle(g, P.X(q[0]), P.Y(q[1]), 5, { fill: col, stroke: c.surf, w: 1.5 });
      });
      g.restore();
      D.circle(g, P.X(0), P.Y(0), 3, { fill: c.ink });
      head(z, `Loss after ${f.t} step${f.t === 1 ? '' : 's'}`, 428, 30);
      f.names.forEach((n, i) => {
        const v = lossAt(f.paths[n][f.t]), y = 58 + i * 58;
        rr(g, 428, y - 16, 12, 12, 3, { fill: klass(z, OPTS.indexOf(n)) });
        D.text(g, n, 446, y - 6, { s: 13, b: true, c: c.ink });
        D.text(g, fe(v), 446, y + 14, { s: 13, mono: true, c: v < 1e6 ? c.ink2 : c.red });
      });
      D.text(g, 'grey ovals: equal loss', 428, 318, { s: 10, c: c.ink2 });
    }
  });

  /* a 1 → 24 → 24 → 1 tanh network trained with Adam on 16 noisy points of sin(x) */
  const DATA = (() => {
    const R = rng(11), gs = () => { let u = 0; while (u === 0) u = R(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * R()); };
    const tr = [], va = [];
    for (let i = 0; i < 16; i++) { const x = -3 + 6 * R(); tr.push([x, Math.sin(x) + 0.3 * gs()]); }
    for (let i = 0; i < 60; i++) { const x = -3 + 6 * (i + 0.5) / 60; va.push([x, Math.sin(x) + 0.3 * gs()]); }
    return { tr, va };
  })();
  const REG = { none: 'no regularisation', decay: 'weight decay 0.01', dropout: 'dropout, keep 0.8', early: 'early stopping, patience 200' };
  const CHECK = [0, 50, 150, 400, 1000, 2000];
  let baseVa = null;
  const base = () => { if (baseVa === null) { const sh = trainNet('none').shots; baseVa = sh[sh.length - 1].va; } return baseVa; };

  function trainNet(reg) {
    const R = rng(5), H = 24, sizes = [1, H, H, 1];
    const gs = () => { let u = 0; while (u === 0) u = R(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * R()); };
    const W = sizes.slice(1).map((b, l) => Array.from({ length: sizes[l] }, () => Array.from({ length: b }, () => gs() / Math.sqrt(sizes[l]))));
    const B = sizes.slice(1).map(b => new Array(b).fill(0));
    const params = [...W.flatMap(m => m), ...B];
    const M = params.map(r => new Array(r.length).fill(0)), V = params.map(r => new Array(r.length).fill(0));
    const keep = reg === 'dropout' ? 0.8 : 1, decay = reg === 'decay' ? 0.01 : 0;
    const fwd = (x, drop) => {
      const hs = [[x]], raw = [], masks = [];
      for (let l = 0; l < 2; l++) {
        const prev = hs[l], h = B[l].map((b, j) => Math.tanh(prev.reduce((a, v, i) => a + v * W[l][i][j], b)));
        const m = h.map(() => (drop ? (R() < keep ? 1 / keep : 0) : 1));
        raw.push(h); masks.push(m); hs.push(h.map((v, j) => v * m[j]));
      }
      return { hs, raw, masks, out: hs[2].reduce((a, v, i) => a + v * W[2][i][0], B[2][0]) };
    };
    const mse = set => set.reduce((a, [x, y]) => a + (fwd(x, false).out - y) ** 2, 0) / set.length;
    const curve = () => Array.from({ length: 61 }, (_, i) => { const x = -3 + i / 10; return [x, fwd(x, false).out]; });
    const snap = () => JSON.stringify([W, B]);
    const hist = [], shots = [];
    let best = Infinity, bestEp = 0, bestState = null, stopped = 0;
    for (let ep = 0; ep <= 2000; ep++) {
      if (ep % 10 === 0 || CHECK.includes(ep)) hist.push([ep, mse(DATA.tr), mse(DATA.va)]);
      if (reg === 'early') {
        const va = mse(DATA.va);
        if (va < best) { best = va; bestEp = ep; bestState = snap(); }
        else if (ep - bestEp >= 200) { const s = JSON.parse(bestState); s[0].forEach((m, l) => m.forEach((r, i) => r.forEach((v, j) => (W[l][i][j] = v)))); s[1].forEach((r, l) => r.forEach((v, j) => (B[l][j] = v))); stopped = ep; shots.push({ ep, bestEp, curve: curve(), tr: mse(DATA.tr), va: mse(DATA.va), hist: hist.slice() }); break; }
      }
      if (CHECK.includes(ep)) shots.push({ ep, curve: curve(), tr: mse(DATA.tr), va: mse(DATA.va), hist: hist.slice() });
      if (ep === 2000) break;
      const gW = W.map(m => m.map(r => r.map(() => 0))), gB = B.map(r => r.map(() => 0));
      DATA.tr.forEach(([x, y]) => {
        const { hs, raw, masks, out } = fwd(x, true);
        let d = [2 * (out - y) / DATA.tr.length];
        for (let l = 2; l >= 0; l--) {
          hs[l].forEach((v, i) => d.forEach((dj, j) => (gW[l][i][j] += v * dj)));
          d.forEach((dj, j) => (gB[l][j] += dj));
          if (l > 0) d = hs[l].map((_, i) => d.reduce((a, dj, j) => a + dj * W[l][i][j], 0) * masks[l - 1][i] * (1 - raw[l - 1][i] ** 2));
        }
      });
      const grads = [...gW.flatMap((m, l) => m.map((r, i) => r.map((v, j) => v + decay * W[l][i][j]))), ...gB];
      const t = ep + 1;
      params.forEach((r, k) => r.forEach((_, j) => {
        M[k][j] = 0.9 * M[k][j] + 0.1 * grads[k][j]; V[k][j] = 0.999 * V[k][j] + 0.001 * grads[k][j] ** 2;
        r[j] -= 0.01 * (M[k][j] / (1 - 0.9 ** t)) / (Math.sqrt(V[k][j] / (1 - 0.999 ** t)) + 1e-8);
      }));
    }
    return { shots, stopped };
  }

  trace('mlfitreg', {
    title: 'Overfitting, and three ways to stop it',
    sub: 'A network with two hidden layers of 24 tanh units learns from 16 noisy points of sin(x) (blue dots). Its fit (orange) is checked against 60 fresh validation points (grey). The dashed line is the true sin(x). The right panel tracks training and validation error as training goes on.',
    W: 600, H: 330,
    params: [{ k: 'reg', label: 'Regularisation', type: 'select', v: 'none', opts: Object.keys(REG).map(k => [k, REG[k]]) }],
    tips: [
      { t: 'No regularisation: training error keeps falling towards 0 while validation error turns upwards. The curve bends to pass through the noise.', set: { reg: 'none' }, play: true },
      { t: 'Early stopping: training halts once validation error has not improved for 200 epochs, and the weights from the best epoch are restored.', set: { reg: 'early' }, play: true }
    ],
    frames(p) {
      const { shots, stopped } = trainNet(p.reg);
      if (p.reg === 'none') baseVa = shots[shots.length - 1].va;
      return shots.map((s, k) => {
        let say;
        if (s.ep === 0) say = `Epoch 0 with ${REG[p.reg]}. The network starts from random weights and has learned nothing yet. Training error ${f2(s.tr, 3)}, validation error ${f2(s.va, 3)}. The noise alone gives about 0.09.`;
        else if (s.bestEp !== undefined) say = `Validation error has not improved for 200 epochs, so training <b>stops at epoch ${s.ep}</b> and the weights from epoch ${s.bestEp} come back. Training error ${f2(s.tr, 3)}, validation error <b>${f2(s.va, 3)}</b>.`;
        else say = `Epoch ${s.ep}: training error ${f2(s.tr, 3)}, validation error <b>${f2(s.va, 3)}</b>.` + (k === shots.length - 1 && !stopped ? (p.reg === 'none' ? ` Training error is ${f2(s.va / s.tr, 0)} times smaller than validation error: the network has <b>overfitted</b> the noise.` : ` Without regularisation the validation error ends at ${f2(base(), 3)}, so ${p.reg === 'decay' ? 'weight decay' : 'dropout'} ${s.va < base() ? 'lowers' : 'does not lower'} it here.`) : '');
        return { ...s, reg: p.reg, say };
      });
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 330, 310], [-3, 3], [-2, 2], { dx: 1, dy: 0, xl: 'x', yl: 'y' });
      g.save(); g.beginPath(); g.rect(P.x0 + 26, P.y0 + 10, P.w - 36, P.h - 30); g.clip();
      g.beginPath(); for (let i = 0; i <= 60; i++) { const x = -3 + i / 10; i ? g.lineTo(P.X(x), P.Y(Math.sin(x))) : g.moveTo(P.X(x), P.Y(Math.sin(x))); }
      g.setLineDash([4, 4]); g.strokeStyle = c.ink2; g.lineWidth = 1; g.stroke(); g.setLineDash([]);
      DATA.va.forEach(([x, y]) => D.circle(g, P.X(x), P.Y(y), 2, { fill: c.line }));
      g.beginPath(); f.curve.forEach(([x, y], i) => (i ? g.lineTo(P.X(x), P.Y(y)) : g.moveTo(P.X(x), P.Y(y)))); g.strokeStyle = klass(z, 1); g.lineWidth = 2.5; g.stroke();
      g.restore();
      DATA.tr.forEach(([x, y]) => D.circle(g, P.X(x), P.Y(y), 4, { fill: klass(z, 0), stroke: c.surf, w: 1 }));
      const Q = plot(z, [350, 10, 240, 310], [0, 2000], [-3, 1], { dx: 0, dy: 0, xl: 'epoch', yl: 'log₁₀ error' });
      const line = (k, col) => { g.beginPath(); f.hist.forEach((h, i) => { const X = Q.X(h[0]), Y = Q.Y(Math.max(-3, Math.min(1, Math.log10(h[k] + 1e-9)))); i ? g.lineTo(X, Y) : g.moveTo(X, Y); }); g.strokeStyle = col; g.lineWidth = 2; g.stroke(); };
      line(1, klass(z, 0)); line(2, klass(z, 1));
      D.text(g, 'blue: training', 580, 40, { a: 'right', s: 11, b: true, c: klass(z, 0) });
      D.text(g, 'orange: validation', 580, 56, { a: 'right', s: 11, b: true, c: klass(z, 1) });
    }
  });
})();

/* =====================================================================================================
   Deep learning 2.1  convolutional networks: a kernel sliding over an image, and how far each unit can see
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr } = MLZ;
  const nf = v => String(Math.round(v * 100) / 100).replace('-', '−');
  const IMGS = {
    edge: { name: 'Dark left half, bright right half', px: Array.from({ length: 7 }, () => [0, 0, 0, 9, 9, 9, 9]) },
    square: { name: 'A bright 3 × 3 square', px: Array.from({ length: 7 }, (_, i) => Array.from({ length: 7 }, (_, j) => (i >= 2 && i <= 4 && j >= 2 && j <= 4 ? 9 : 0))) },
    cross: { name: 'A plus sign', px: Array.from({ length: 7 }, (_, i) => Array.from({ length: 7 }, (_, j) => (i === 3 || j === 3 ? 9 : 0))) }
  };
  const KERNELS = {
    vert: { name: 'Vertical edge', k: [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]] },
    horiz: { name: 'Horizontal edge', k: [[-1, -1, -1], [0, 0, 0], [1, 1, 1]] },
    blur: { name: 'Blur (average)', k: [[1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9]] },
    sharpen: { name: 'Sharpen', k: [[0, -1, 0], [-1, 5, -1], [0, -1, 0]] }
  };
  const kshow = v => (Math.abs(v - 1 / 9) < 1e-9 ? '1/9' : nf(v));

  trace('mlconv', {
    title: 'A convolution: one small filter slides over the image',
    sub: 'The 3 × 3 filter (middle) sits on a patch of the image (left). Multiply the 9 pairs of numbers and add them up: that sum is one output value (right). Then slide the filter by the stride and repeat. Padding adds a border of zeros.',
    W: 600, H: 330,
    params: [
      { k: 'img', label: 'Image', type: 'select', v: 'edge', opts: Object.keys(IMGS).map(k => [k, IMGS[k].name]) },
      { k: 'ker', label: 'Filter', type: 'select', v: 'vert', opts: Object.keys(KERNELS).map(k => [k, KERNELS[k].name]) },
      { k: 's', label: 'Stride', type: 'select', v: '1', opts: [['1', '1'], ['2', '2']] },
      { k: 'p', label: 'Padding', type: 'select', v: '0', opts: [['0', '0 (no border)'], ['1', '1 (border of zeros)']] }
    ],
    tips: [
      { t: 'The horizontal edge filter on the left and right halves: the picture has no horizontal edges, so every output is 0.', set: { img: 'edge', ker: 'horiz', s: '1', p: '0' }, play: true },
      { t: 'Padding 1 with stride 1 keeps the output the same size as the input, 7 × 7, which is why most modern networks pad.', set: { img: 'square', ker: 'vert', s: '1', p: '1' }, play: true },
      { t: 'Stride 2 skips every other position, so a 7 × 7 image gives only a 3 × 3 output.', set: { img: 'cross', ker: 'blur', s: '2', p: '0' }, play: true }
    ],
    frames(p) {
      const pad = +p.p, s = +p.s, K = KERNELS[p.ker].k, src = IMGS[p.img].px, n = 7 + 2 * pad;
      const img = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => { const a = i - pad, b = j - pad; return a >= 0 && a < 7 && b >= 0 && b < 7 ? src[a][b] : 0; }));
      const m = Math.floor((n - 3) / s) + 1, out = Array.from({ length: m }, () => new Array(m).fill(null));
      const fr = [{ img, out: out.map(r => r.slice()), m, pad, say: `The image is 7 × 7${pad ? ', padded with zeros to 9 × 9' : ''}. With a 3 × 3 filter and stride ${s}, the output is (${n} − 3) / ${s} + 1 = <b>${m} × ${m}</b>. It starts empty.` }];
      let shown = 0;
      for (let i = 0; i < m; i++) {
        for (let j = 0; j < m; j++) {
          let sum = 0; const terms = [];
          for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) { const v = img[i * s + a][j * s + b], w = K[a][b]; sum += v * w; if (v !== 0 && w !== 0) terms.push(`${v} × ${kshow(w)}`); }
          out[i][j] = sum;
          if (shown < 5) { shown++; fr.push({ img, out: out.map(r => r.slice()), m, pad, cur: [i, j], s, say: `Output (${i + 1}, ${j + 1}): the filter covers rows ${i * s + 1} to ${i * s + 3} and columns ${j * s + 1} to ${j * s + 3}. ${terms.length ? `The non zero products are ${terms.slice(0, 6).join(' + ')}${terms.length > 6 ? ' + …' : ''}` : 'Every product is 0'}, so the sum is <b>${nf(sum)}</b>.` }); }
        }
        if (shown >= 5 && (i + 1) * m > 5) fr.push({ img, out: out.map(r => r.slice()), m, pad, cur: [i, m - 1], s, say: `Row ${i + 1} of the output is done: ${out[i].map(nf).join(', ')}.` });
      }
      const flat = out.flat(), mx = Math.max(...flat.map(Math.abs));
      fr.push({ img, out, m, pad, say: `Done: ${m * m} outputs from the same 9 weights. ${mx < 1e-9 ? 'Every output is 0: the filter found nothing it responds to.' : `The largest response is ${nf(Math.max(...flat))} and the smallest ${nf(Math.min(...flat))}. Big values mark where the image matches the filter’s pattern.`}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, n = f.img.length, cs = n > 7 ? 24 : 28, x0 = 12, y0 = 40;
      head(z, f.pad ? 'Image with padding' : 'Image', x0, 26);
      f.img.forEach((r, i) => r.forEach((v, j) => {
        const isPad = f.pad && (i === 0 || j === 0 || i === n - 1 || j === n - 1);
        const t = v / 9;
        rr(g, x0 + j * cs, y0 + i * cs, cs - 2, cs - 2, 3, { fill: isPad ? c.bg : `rgba(37,99,235,${0.08 + 0.8 * t})`, stroke: c.line });
        D.text(g, String(v), x0 + j * cs + cs / 2 - 1, y0 + i * cs + cs / 2 + 4, { a: 'center', s: 11, c: t > 0.5 ? '#fff' : c.ink2 });
      }));
      if (f.cur) { const [i, j] = f.cur; g.save(); g.strokeStyle = klass(z, 1); g.lineWidth = 3; g.strokeRect(x0 + j * f.s * cs - 1, y0 + i * f.s * cs - 1, 3 * cs, 3 * cs); g.restore(); }
      const K = KERNELS[z.p.ker].k, kx = 262, ky = 120;
      head(z, 'Filter', kx, ky - 14);
      K.forEach((r, i) => r.forEach((w, j) => { rr(g, kx + j * 28, ky + i * 28, 26, 26, 3, { fill: c.surf, stroke: klass(z, 1), w: 1.5 }); D.text(g, kshow(w), kx + j * 28 + 13, ky + i * 28 + 17, { a: 'center', s: kshow(w).length > 2 ? 10 : 12, b: true, c: c.ink }); }));
      const oc = f.m > 5 ? 28 : 36, ox = 368, oy = 40;
      head(z, `Output ${f.m} × ${f.m}`, ox, 26);
      const mx = Math.max(1e-9, ...f.out.flat().filter(v => v !== null).map(Math.abs));
      f.out.forEach((r, i) => r.forEach((v, j) => {
        const cur = f.cur && f.cur[0] === i && f.cur[1] === j;
        const fill = v === null ? c.bg : v >= 0 ? `rgba(37,99,235,${0.08 + 0.7 * v / mx})` : `rgba(234,88,12,${0.08 + 0.7 * -v / mx})`;
        rr(g, ox + j * oc, oy + i * oc, oc - 2, oc - 2, 3, { fill, stroke: cur ? klass(z, 1) : c.line, w: cur ? 2.5 : 1 });
        if (v !== null) D.text(g, nf(v), ox + j * oc + oc / 2 - 1, oy + i * oc + oc / 2 + 4, { a: 'center', s: nf(v).length > 3 ? 9 : 11, c: Math.abs(v) / mx > 0.6 ? '#fff' : c.ink });
      }));
      D.text(g, 'blue: positive   orange: negative', ox, 318, { s: 10, c: c.ink2 });
    }
  });

  const ARCH = {
    three: { name: 'Three 3 × 3 convolutions', layers: [['conv 3×3', 3, 1, 1], ['conv 3×3', 3, 1, 1], ['conv 3×3', 3, 1, 1]] },
    big: { name: 'One 7 × 7 convolution', layers: [['conv 7×7', 7, 1, 1]] },
    pool: { name: 'conv, pool, conv, pool, conv', layers: [['conv 3×3', 3, 1, 1], ['max pool 2×2', 2, 2, 1], ['conv 3×3', 3, 1, 1], ['max pool 2×2', 2, 2, 1], ['conv 3×3', 3, 1, 1]] },
    dilated: { name: 'Dilated 3 × 3 convolutions (dilation 1, 2, 4)', layers: [['conv 3×3, dilation 1', 3, 1, 1], ['conv 3×3, dilation 2', 3, 1, 2], ['conv 3×3, dilation 4', 3, 1, 4]] }
  };
  const GRID = 21;

  trace('mlreceptive', {
    title: 'The receptive field: how much of the image one unit can see',
    sub: 'Each unit in a convolutional layer looks at a small window of the layer below. Stack layers and the window, measured in input pixels, grows. The shaded square is what one unit in the top layer can see.',
    W: 600, H: 330,
    params: [{ k: 'a', label: 'Layers', type: 'select', v: 'three', opts: Object.keys(ARCH).map(k => [k, ARCH[k].name]) }],
    tips: [
      { t: 'One 7 × 7 convolution sees the same 7 × 7 window as three 3 × 3 layers, but needs 49 weights per input and output channel pair instead of 27, and has only one ReLU instead of three. This is the idea behind VGG.', set: { a: 'big' }, play: true },
      { t: 'Dilated convolutions space out the 9 taps of the filter, so three layers see 15 × 15 pixels with no pooling and no loss of resolution.', set: { a: 'dilated' }, play: true }
    ],
    frames(p) {
      const A = ARCH[p.a];
      let r = 1, j = 1, w = 0;
      const rows = [], fr = [{ r, rows: [], say: 'Start at the input: one pixel sees only itself, so the receptive field is 1 × 1. The jump (distance in input pixels between neighbouring units) is 1.' }];
      A.layers.forEach(([name, k, s, d]) => {
        const add = (k - 1) * d * j, r0 = r;
        r += add; j *= s; if (name.startsWith('conv')) w += k * k;
        rows.push([name, r, j]);
        fr.push({ r, rows: rows.slice(), say: `${name}: the window grows by (k − 1) × dilation × jump = (${k} − 1) × ${d} × ${j / s} = ${add}, from ${r0} to <b>${r} × ${r}</b>.${s > 1 ? ` The stride ${s} multiplies the jump to ${j}, so every later layer grows the window faster.` : ''}` });
      });
      const lastConv = A.layers.filter(l => l[0].startsWith('conv'));
      fr.push({ r, rows, say: `Top unit sees <b>${r} × ${r}</b> input pixels after ${A.layers.length} layer${A.layers.length > 1 ? 's' : ''}, using ${w} weights per input and output channel pair in its ${lastConv.length} convolution${lastConv.length > 1 ? 's' : ''}.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, cs = 13, x0 = 20, y0 = 30, mid = Math.floor(GRID / 2);
      head(z, `Input pixels (${GRID} × ${GRID})`, x0, 22);
      const lo = mid - Math.floor((f.r - 1) / 2), hi = lo + f.r - 1;
      for (let i = 0; i < GRID; i++) for (let jj = 0; jj < GRID; jj++) {
        const inside = i >= lo && i <= hi && jj >= lo && jj <= hi;
        g.fillStyle = inside ? 'rgba(37,99,235,0.45)' : 'rgba(148,163,184,0.22)'; g.fillRect(x0 + jj * cs, y0 + i * cs, cs - 1, cs - 1);
      }
      g.fillStyle = klass(z, 1); g.fillRect(x0 + mid * cs + 2, y0 + mid * cs + 2, cs - 5, cs - 5);
      D.text(g, `${f.r} × ${f.r}`, x0 + GRID * cs / 2, y0 + GRID * cs + 18, { a: 'center', s: 13, b: true, c: c.ink });
      head(z, 'Layer', 330, 40); head(z, 'sees', 480, 40); head(z, 'jump', 540, 40);
      D.text(g, 'input', 330, 66, { s: 12, c: c.ink2 }); D.text(g, '1', 480, 66, { s: 12, mono: true, c: c.ink2 }); D.text(g, '1', 540, 66, { s: 12, mono: true, c: c.ink2 });
      f.rows.forEach(([name, r, j], i) => {
        const y = 92 + i * 26;
        D.text(g, name, 330, y, { s: 12, b: i === f.rows.length - 1, c: c.ink });
        D.text(g, `${r} × ${r}`, 480, y, { s: 12, mono: true, c: c.ink });
        D.text(g, String(j), 540, y, { s: 12, mono: true, c: c.ink });
      });
      D.text(g, 'r ← r + (k − 1) · dilation · jump', 330, 270, { s: 12, mono: true, c: c.ink2 });
      D.text(g, 'jump ← jump · stride', 330, 290, { s: 12, mono: true, c: c.ink2 });
      D.text(g, 'orange: the unit itself', 330, 316, { s: 10, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Deep learning 2.2  recurrent networks: an RNN unrolled through time, and the gates of an LSTM memory cell
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, plot } = MLZ;
  const nf = (v, d = 3) => f2(v, d);
  const SEQS = { pulse: { name: 'One input of 1, then zeros', x: [1, 0, 0, 0, 0, 0, 0, 0] }, steady: { name: 'A steady input of 0.5', x: [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5] } };

  trace('mlunroll', {
    title: 'An RNN unrolled through time, forward and backward',
    sub: 'A tiny RNN with one hidden number: hₜ = tanh(w·hₜ₋₁ + xₜ). The same w is used at every step. Forward, the state carries information along. Backward, the gradient of h₈ travels back and is multiplied by w·(1 − hₜ²) at every step.',
    W: 600, H: 330,
    params: [
      { k: 'w', label: 'Recurrent weight w', type: 'select', v: '0.5', opts: [['0.5', '0.5'], ['1', '1.0'], ['2', '2.0']] },
      { k: 'seq', label: 'Inputs', type: 'select', v: 'pulse', opts: Object.keys(SEQS).map(k => [k, SEQS[k].name]) }
    ],
    tips: [
      { t: 'w = 2 with a steady input: the state saturates near 1, where tanh is flat, so 1 − h² is tiny and the gradient vanishes even though w is large.', set: { w: '2', seq: 'steady' }, play: true },
      { t: 'w = 1 with one pulse: after the first steps the state is small, so most backward factors are close to 1 and the gradient at step 0 ends about 50 times larger than with w = 0.5.', set: { w: '1', seq: 'pulse' }, play: true }
    ],
    frames(p) {
      const w = +p.w, xs = SEQS[p.seq].x, T = xs.length, h = [0];
      const fr = [{ h: [0], x: xs, g: [], say: `Start with h₀ = 0. The inputs are ${xs.join(', ')}, and the recurrent weight is w = ${w}.` }];
      for (let t = 1; t <= T; t++) {
        h.push(Math.tanh(w * h[t - 1] + xs[t - 1]));
        if (t <= 3 || t === T) fr.push({ h: h.slice(), x: xs, g: [], say: `Step ${t}: h${'₀₁₂₃₄₅₆₇₈'[t]} = tanh(${w} × ${nf(h[t - 1])} + ${xs[t - 1]}) = <b>${nf(h[t])}</b>.${t === 3 && T > 4 ? ' The same rule runs for the remaining steps.' : ''}` });
      }
      const g = new Array(T + 1).fill(null); g[T] = 1;
      fr.push({ h, x: xs, g: g.slice(), say: 'Backward: start with ∂h₈/∂h₈ = 1 at the last step.' });
      for (let t = T; t >= 1; t--) {
        const fac = w * (1 - h[t] * h[t]);
        g[t - 1] = g[t] * fac;
        if (t >= T - 2 || t === 1) fr.push({ h, x: xs, g: g.slice(), say: `Back from step ${t}: multiply by w(1 − h²) = ${w} × (1 − ${nf(h[t])}²) = ${nf(fac)}, so ∂h₈/∂h${'₀₁₂₃₄₅₆₇₈'[t - 1]} = <b>${g[t - 1] < 1e-3 ? g[t - 1].toExponential(1).replace('-', '−') : nf(g[t - 1])}</b>.` });
      }
      const g0 = Math.abs(g[0]);
      fr.push({ h, x: xs, g, say: `After 8 steps back the gradient is ${g0 < 1e-3 ? g0.toExponential(1).replace('-', '−') : nf(g0)}. ${g0 < 0.01 ? '<b>Vanishing</b>: the first inputs barely affect learning.' : g0 > 10 ? '<b>Exploding</b>: updates would be unstable.' : 'The gradient survives these 8 steps, though longer sequences would still shrink or grow it.'}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, T = f.x.length, dx = 62, x0 = 70;
      head(z, 'step', 10, 24);
      for (let t = 0; t <= T; t++) {
        const X = x0 + t * dx;
        D.text(g, String(t), X, 24, { a: 'center', s: 11, c: c.ink2 });
        if (t > 0) {
          rr(g, X - 16, 250, 32, 24, 4, { fill: c.surf, stroke: c.line });
          D.text(g, String(f.x[t - 1]), X, 266, { a: 'center', s: 11, c: c.ink });
          D.arrow(g, X, 250, X, 166, c.ink2, 1, 6);
        }
        const has = t < f.h.length;
        D.circle(g, X, 140, 22, { fill: has ? `rgba(37,99,235,${0.1 + 0.7 * Math.abs(f.h[t])})` : c.bg, stroke: c.line, w: 1.5 });
        if (has) D.text(g, nf(f.h[t], 2), X, 145, { a: 'center', s: 11, b: true, c: Math.abs(f.h[t]) > 0.55 ? '#fff' : c.ink });
        if (t > 0 && has) D.arrow(g, X - dx + 22, 140, X - 24, 140, c.ink2, 1.5, 6);
        if (f.g[t] !== null && f.g[t] !== undefined) {
          const v = Math.abs(f.g[t]), hgt = Math.max(2, Math.min(60, 60 * (Math.log10(v + 1e-12) + 4) / 4));
          rr(g, X - 10, 100 - hgt, 20, hgt, 2, { fill: v < 0.01 ? c.red : klass(z, 1) });
          D.text(g, v < 0.01 ? v.toExponential(0).replace('-', '−') : f2(v, 2), X, 112 - hgt - 16, { a: 'center', s: 10, b: true, c: c.red });
        }
      }
      D.text(g, 'x (input)', 10, 300, { s: 11, c: c.ink2 });
      D.text(g, 'circles: hidden state h   orange bars: gradient ∂h₈/∂hₜ on a log scale (red below 0.01)', 10, 318, { s: 10, c: c.ink2 });
    }
  });

  const SCEN = {
    one: { name: 'Store 0.8 at step 1, read at step 12', store: { 1: 0.8 }, noise: [0, 0.3, -0.6, 0.9, -0.2, 0.5, -0.9, 0.4, 0.1, -0.4, 0.7, 0] },
    two: { name: 'Store 0.8 at step 1, store −0.5 at step 7, read at step 12', store: { 1: 0.8, 7: -0.5 }, noise: [0, 0.3, -0.6, 0.9, -0.2, 0.5, 0, 0.4, 0.1, -0.4, 0.7, 0] }
  };
  const sg = z => 1 / (1 + Math.exp(-z));

  trace('mllstm', {
    title: 'Inside an LSTM cell: three gates and a memory',
    sub: 'A hand set LSTM with one memory cell c. The input gate i lets a new value in when the store marker is on. The forget gate f decides how much of the memory to keep each step. The output gate o opens at the read step. The blue line is the memory and the dots are the inputs (green: stored). In a trained LSTM the network learns these gate rules from data.',
    W: 600, H: 330,
    params: [
      { k: 'f', label: 'Forget gate when not storing', type: 'select', v: '0.99', opts: [['0.5', '0.5 (forgets fast)'], ['0.9', '0.9'], ['0.99', '0.99 (remembers)']] },
      { k: 'sc', label: 'Sequence', type: 'select', v: 'one', opts: Object.keys(SCEN).map(k => [k, SCEN[k].name]) }
    ],
    tips: [
      { t: 'Forget gate 0.5: the memory halves every step, so after 11 steps it keeps only 0.5¹¹ ≈ 0.0005 of the stored value and ends close to 0.', set: { f: '0.5', sc: 'one' }, play: true },
      { t: 'Two stores: at step 7 the forget gate closes and the input gate opens, so the old value is replaced by the new one.', set: { f: '0.99', sc: 'two' }, play: true }
    ],
    frames(p) {
      const S = SCEN[p.sc], fb = Math.log(+p.f / (1 - +p.f));
      let cc = 0;
      const rows = [], fr = [{ rows: [], say: `The memory starts empty, c = 0. When nothing is stored, the forget gate is ${p.f}. Inputs without a store marker are distractions the cell should ignore.` }];
      for (let t = 1; t <= 12; t++) {
        const m = S.store[t] !== undefined ? 1 : 0, r = t === 12 ? 1 : 0, v = m ? S.store[t] : S.noise[t - 1];
        const i = sg(10 * m - 5), f = sg(fb - 10 * m), o = sg(10 * r - 5), gg = v;
        const old = cc;
        cc = f * old + i * gg;
        const h = o * Math.tanh(cc);
        rows.push({ t, v, m, r, i, f, o, c: cc, h });
        const what = m ? `Store marker on: i = ${nf(i)} lets ${v} in and f = ${nf(f)} wipes the old memory.` : r ? `Read step: o = ${nf(o)} opens, so the cell outputs h = o · tanh(c) = <b>${nf(h)}</b>.` : `No marker: i = ${nf(i)} blocks the input ${v}, and f = ${nf(f)} keeps that share of the memory.`;
        if (t <= 3 || m || r || t === 6 || t === 9) fr.push({ rows: rows.slice(), say: `Step ${t}. ${what} c = ${nf(f)} × ${nf(old)} + ${nf(i)} × ${v} = <b>${nf(cc)}</b>.` });
      }
      const last = rows[rows.length - 1], tgt = S.store[7] !== undefined ? -0.5 : 0.8;
      fr.push({ rows, say: `Done. The memory holds ${nf(last.c)} at step 12, against the last stored value ${String(tgt).replace("-", "−")}. ${Math.abs(last.c - tgt) < 0.1 ? 'The cell kept it through all the distractions.' : 'Too much leaked away, because the forget gate let the memory fade.'}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 380, 310], [0, 12], [-1, 1], { dx: 0, dy: 1, xl: 'step', yl: 'memory c' });
      const S = SCEN[z.p.sc];
      for (let t = 1; t <= 12; t++) {
        const m = S.store[t] !== undefined, v = m ? S.store[t] : S.noise[t - 1];
        if (m) { g.fillStyle = 'rgba(22,163,74,0.15)'; g.fillRect(P.X(t - 0.5), P.Y(1), P.X(1) - P.X(0), P.Y(-1) - P.Y(1)); }
        D.circle(g, P.X(t), P.Y(v), 3.5, { fill: m ? c.green : c.line });
      }
      if (f.rows.length) {
        g.beginPath(); g.moveTo(P.X(0), P.Y(0)); f.rows.forEach(r => g.lineTo(P.X(r.t), P.Y(r.c))); g.strokeStyle = klass(z, 0); g.lineWidth = 2.5; g.stroke();
        const L = f.rows[f.rows.length - 1];
        D.circle(g, P.X(L.t), P.Y(L.c), 5, { fill: klass(z, 0), stroke: c.surf, w: 1.5 });
      }
      const L = f.rows[f.rows.length - 1];
      head(z, L ? `Gates at step ${L.t}` : 'Gates', 410, 30);
      [['input i', 'i', klass(z, 2)], ['forget f', 'f', klass(z, 1)], ['output o', 'o', klass(z, 3)]].forEach(([lab, k, col], j) => {
        const y = 60 + j * 50, v = L ? L[k] : 0;
        D.text(g, lab, 410, y, { s: 12, b: true, c: c.ink });
        rr(g, 410, y + 8, 160, 14, 4, { fill: c.bg });
        if (L) rr(g, 410, y + 8, Math.max(2, 160 * v), 14, 4, { fill: col });
        if (L) D.text(g, nf(v), 570, y, { a: 'right', s: 11, mono: true, c: c.ink });
      });
      if (L) {
        D.text(g, `c = ${nf(L.c)}`, 410, 236, { s: 13, mono: true, b: true, c: c.ink });
        D.text(g, `h = ${nf(L.h)}`, 410, 258, { s: 13, mono: true, c: c.ink2 });
      }
      D.text(g, 'c ← f·c + i·g', 410, 290, { s: 12, mono: true, c: c.ink2 });
      D.text(g, 'h = o·tanh(c)', 410, 308, { s: 12, mono: true, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Deep learning 2.3  transformers: scaled dot product attention for one query, and sinusoidal positional encoding
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, plot } = MLZ;
  const TOK = ['the', 'cat', 'sat', 'on', 'mat'];
  const KEYS = [[0.2, 0.1], [1.5, 0.3], [0.2, 1.5], [-0.3, 0.4], [1.2, -0.4]];
  const QRY = [[1.0, 0.0], [0.3, 1.2], [1.4, 0.2], [0.9, -0.9], [0.0, 1.0]];
  const SC = { '1': 'divide by √2 (standard)', '0': 'do not scale', '4': 'scores × 4 (sharper)' };

  trace('mlattn', {
    title: 'Attention for one word: score, softmax, weighted sum',
    sub: 'Each word has a query (what it looks for) and a key (what it offers), here 2D vectors picked by hand. The chosen word scores every key with a dot product, turns the scores into weights with softmax, and outputs the weighted average of the values. To keep the picture simple, each value equals its key.',
    W: 600, H: 330,
    params: [
      { k: 'q', label: 'Query word', type: 'select', v: '2', opts: TOK.map((t, i) => [String(i), t]) },
      { k: 'mask', label: 'Causal mask', type: 'select', v: 'off', opts: [['off', 'Off: see every word (encoder, BERT)'], ['on', 'On: see only earlier words (decoder, GPT)']] },
      { k: 'sc', label: 'Scaling', type: 'select', v: '1', opts: Object.keys(SC).map(k => [k, SC[k]]) }
    ],
    tips: [
      { t: 'Query "cat" with the causal mask on: it may only look at "the" and itself, so the verb "sat" it would like to find is blocked.', set: { q: '1', mask: 'on', sc: '1' }, play: true },
      { t: 'Scores × 4: the same ranking, but softmax puts almost all the weight on the best match. Large unscaled dot products do this in big models, which is why scores are divided by √d.', set: { q: '2', mask: 'off', sc: '4' }, play: true }
    ],
    frames(p) {
      const qi = +p.q, q = QRY[qi], scale = p.sc === '1' ? 1 / Math.SQRT2 : p.sc === '4' ? 4 : 1;
      const allowed = TOK.map((_, j) => p.mask === 'off' || j <= qi);
      const raw = KEYS.map(k => q[0] * k[0] + q[1] * k[1]);
      const fr = [{ qi, shown: 0, say: `The query for "${TOK[qi]}" is (${f2(q[0], 1)}, ${f2(q[1], 1)}). It will be compared with the key of every word${p.mask === 'on' ? ' up to itself, because the causal mask hides later words' : ''}.` }];
      TOK.forEach((t, j) => fr.push({ qi, shown: j + 1, raw, allowed, say: allowed[j] ? `Score for "${t}": q · k = ${f2(q[0], 1)} × ${f2(KEYS[j][0], 1)} + ${f2(q[1], 1)} × ${f2(KEYS[j][1], 1)} = <b>${f2(raw[j], 2)}</b>.` : `"${t}" comes later, so the mask sets its score to −∞ and its weight will be 0.` }));
      const s = raw.map((v, j) => (allowed[j] ? v * scale : -Infinity)), mx = Math.max(...s), e = s.map(v => Math.exp(v - mx)), Z = e.reduce((a, b) => a + b, 0), w = e.map(v => v / Z);
      const best = w.indexOf(Math.max(...w));
      fr.push({ qi, shown: 5, raw, allowed, w, say: `${p.sc === '1' ? 'Divide each score by √2, then apply' : p.sc === '4' ? 'Multiply each score by 4, then apply' : 'Apply'} softmax: the weights are ${TOK.map((t, j) => `${t} ${f2(w[j], 2)}`).join(', ')}. They add up to 1, and "${TOK[best]}" gets the most.` });
      const out = [0, 1].map(d => w.reduce((a, wj, j) => a + wj * KEYS[j][d], 0));
      fr.push({ qi, shown: 5, raw, allowed, w, out, say: `Output = Σ weight × value = (<b>${f2(out[0], 2)}, ${f2(out[1], 2)}</b>), shown in green. The new vector for "${TOK[qi]}" mixes in information from the words it attended to.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 300, 310], [-0.6, 1.8], [-0.6, 1.8], { dx: 1, dy: 1 });
      KEYS.forEach((k, j) => {
        const hot = f.w ? f.w[j] : 0, blocked = f.allowed && !f.allowed[j];
        D.arrow(g, P.X(0), P.Y(0), P.X(k[0]), P.Y(k[1]), blocked ? c.line : klass(z, 0), 1.5 + 4 * hot, 7);
        D.text(g, TOK[j], P.X(k[0]) + 6, P.Y(k[1]) - 6, { s: 12, b: true, c: blocked ? c.ink2 : c.ink });
      });
      const q = QRY[f.qi];
      D.arrow(g, P.X(0), P.Y(0), P.X(q[0]), P.Y(q[1]), klass(z, 1), 2.5, 8);
      D.text(g, 'query', P.X(q[0]) + 6, P.Y(q[1]) - 8, { s: 11, b: true, c: klass(z, 1) });
      if (f.out) { D.arrow(g, P.X(0), P.Y(0), P.X(f.out[0]), P.Y(f.out[1]), c.green, 3, 8); D.text(g, 'output', P.X(f.out[0]) + 6, P.Y(f.out[1]) + 16, { s: 11, b: true, c: c.green }); }
      D.text(g, 'blue: keys   orange: query', 304, 26, { a: 'right', s: 10, c: c.ink2 });
      head(z, `Query word: "${TOK[f.qi]}"`, 330, 30);
      head(z, 'word', 330, 56); head(z, 'q · k', 390, 56); head(z, 'weight', 455, 56);
      TOK.forEach((t, j) => {
        const y = 84 + j * 34;
        D.text(g, t, 330, y, { s: 13, b: j === f.qi, c: c.ink });
        if (j < f.shown) D.text(g, f.allowed[j] ? f2(f.raw[j], 2) : '−∞', 390, y, { s: 12, mono: true, c: f.allowed[j] ? c.ink : c.ink2 });
        rr(g, 455, y - 11, 110, 14, 4, { fill: c.bg });
        if (f.w) { rr(g, 455, y - 11, Math.max(1, 110 * f.w[j]), 14, 4, { fill: klass(z, 0) }); D.text(g, f2(f.w[j], 2), 570, y, { a: 'right', s: 10, mono: true, c: c.ink }); }
      });
      D.text(g, 'weight = softmax(q · k / √d)', 330, 268, { s: 12, mono: true, c: c.ink2 });
      D.text(g, 'output = Σ weight · value', 330, 288, { s: 12, mono: true, c: c.ink2 });
    }
  });

  trace('mlposenc', {
    title: 'Sinusoidal positional encoding',
    sub: 'Attention alone ignores word order, so each position gets a vector of sines and cosines added to its embedding. Every pair of dimensions is a wave with its own wavelength, from fast to very slow. Rows are dimensions, columns are positions: blue is positive, orange negative.',
    W: 600, H: 330,
    params: [{ k: 'd', label: 'Model size d', type: 'select', v: '32', opts: [['16', '16'], ['32', '32'], ['64', '64']] }],
    tips: [
      { t: 'd = 64: the slowest waves barely change across 50 positions, so they act like a coarse clock while the fast ones tell neighbours apart.', set: { d: '64' }, play: true }
    ],
    frames(p) {
      const d = +p.d, pairs = d / 2, N = 50;
      const pe = Array.from({ length: N }, (_, pos) => Array.from({ length: d }, (_, j) => { const i = Math.floor(j / 2), ang = pos / Math.pow(10000, 2 * i / d); return j % 2 ? Math.cos(ang) : Math.sin(ang); }));
      const wl = i => 2 * Math.PI * Math.pow(10000, 2 * i / d);
      const fr = [{ pe, upto: 0, d, say: `Each of 50 positions will get a vector of ${d} numbers. Dimension pair i uses sin and cos of position / 10000^(2i/${d}). Nothing is drawn yet.` }];
      const marks = [1, 2, Math.ceil(pairs / 4), Math.ceil(pairs / 2), pairs].filter((v, k, a) => a.indexOf(v) === k);
      marks.forEach(u => fr.push({ pe, upto: u, d, say: `${u === 1 ? 'Pair 0 drawn' : `Pairs 0 to ${u - 1} drawn`}. Pair ${u - 1} has wavelength 2π × 10000^(${2 * (u - 1)}/${d}) ≈ <b>${wl(u - 1) < 1000 ? f2(wl(u - 1), 1) : Math.round(wl(u - 1)).toLocaleString('en')}</b> positions.${u === 1 ? ' The fastest wave repeats about every 6 positions.' : ''}` }));
      const dot = (a, b) => a.reduce((s, v, j) => s + v * b[j], 0);
      const sim = pe.map(r => dot(r, pe[10]) / pairs);
      fr.push({ pe, upto: pairs, d, sim, say: `The orange line is the dot product of position 10’s vector with every other position, divided by ${pairs}. It is exactly 1 at position 10 and ${sim[0] < sim[9] && sim[49] < sim[11] ? 'lower further away' : 'changes with distance'}, ${f2(sim[11], 2)} one step away and ${f2(sim[49], 2)} at position 49. The dot product depends only on the distance between positions, so attention can learn relative position.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, d = f.d, N = 50, x0 = 40, y0 = 30, cw = 10, ch = Math.min(6, 150 / d);
      head(z, 'position →', x0, 22);
      for (let j = 0; j < d; j++) for (let pos = 0; pos < N; pos++) {
        const on = Math.floor(j / 2) < f.upto, v = f.pe[pos][j];
        g.fillStyle = !on ? 'rgba(148,163,184,0.15)' : v >= 0 ? `rgba(37,99,235,${0.1 + 0.85 * v})` : `rgba(234,88,12,${0.1 + 0.85 * -v})`;
        g.fillRect(x0 + pos * cw, y0 + j * ch, cw - 1, Math.max(1, ch - 0.5));
      }
      D.text(g, 'dim 0', x0 - 4, y0 + 8, { a: 'right', s: 9, c: c.ink2 });
      D.text(g, `dim ${d - 1}`, x0 - 4, y0 + d * ch, { a: 'right', s: 9, c: c.ink2 });
      [0, 10, 20, 30, 40, 49].forEach(pos => D.text(g, String(pos), x0 + pos * cw + 4, y0 + d * ch + 14, { a: 'center', s: 9, c: c.ink2 }));
      if (f.sim) {
        const top = y0 + d * ch + 24, hgt = 290 - top;
        g.beginPath(); f.sim.forEach((v, pos) => { const X = x0 + pos * cw + 4, Y = top + hgt * (1 - (v + 0.2) / 1.2); pos ? g.lineTo(X, Y) : g.moveTo(X, Y); }); g.strokeStyle = klass(z, 1); g.lineWidth = 2; g.stroke();
        D.text(g, 'similarity to position 10', x0 + 505, top + 10, { a: 'right', s: 10, b: true, c: klass(z, 1) });
      }
      D.text(g, 'PE(pos, 2i) = sin(pos / 10000^(2i/d))', 40, 312, { s: 11, mono: true, c: c.ink2 });
    }
  });
})();
