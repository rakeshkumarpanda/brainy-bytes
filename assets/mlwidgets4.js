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
