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
