/* ===== Complete Machine Learning animations, part 2: supervised and unsupervised learning.
   Uses the framework MLZ from assets/mlwidgets.js. Every animation starts empty and adds one step each time Step
   is pressed, with a plain English line for that step. ===== */

/* =====================================================================================================
   Supervised 1.1  least squares: the best straight line, its residuals and R squared
   ===================================================================================================== */
(() => {
  const { trace, plot, span, fline, points, D, f2, head } = MLZ;
  trace('mlols', {
    title: 'Least squares: find the line with the smallest squared errors',
    sub: 'Type some points (x y on each line or separated by semicolons). We compare the flat "just guess the average" line with the least squares line, and measure how much better it is with R².',
    W: 600, H: 330,
    params: [{ k: 'pts', label: 'Points (x y)', type: 'area', v: '1 52; 2 55; 3 61; 4 64; 5 70; 6 72' }],
    tips: [
      { t: 'Points with no pattern: the best line is almost flat and R² is close to 0.', set: { pts: '1 5; 2 9; 3 4; 4 8; 5 5; 6 7' }, play: true },
      { t: 'One far point pulls the whole line towards it, because its error is squared.', set: { pts: '1 2; 2 4; 3 6; 4 8; 5 10; 6 30' }, play: true }
    ],
    frames(p) {
      const P = points(p.pts).slice(0, 25);
      if (P.length < 2) throw new Error('Type at least two points');
      const n = P.length, mx = P.reduce((a, q) => a + q.x, 0) / n, my = P.reduce((a, q) => a + q.y, 0) / n;
      const sxy = P.reduce((a, q) => a + (q.x - mx) * (q.y - my), 0), sxx = P.reduce((a, q) => a + (q.x - mx) ** 2, 0);
      if (!sxx) throw new Error('The x values must not all be the same');
      const b1 = sxy / sxx, b0 = my - b1 * mx;
      const sst = P.reduce((a, q) => a + (q.y - my) ** 2, 0), sse = P.reduce((a, q) => a + (q.y - b0 - b1 * q.x) ** 2, 0);
      const base = { P, mx, my, b0, b1, sst, sse };
      return [
        { ...base, st: 1, say: `Here are ${n} points. We want a straight line ŷ = b₀ + b₁x that predicts y from x as well as possible.` },
        { ...base, st: 2, say: `The centre of the points is (x̄, ȳ) = (${f2(mx)}, ${f2(my)}). The least squares line always passes through this point.` },
        { ...base, st: 3, say: `First the laziest model: always predict ȳ = ${f2(my)} (the flat line). Its squared errors add up to <b>SST = ${f2(sst)}</b>, the total variation in y.` },
        { ...base, st: 4, say: `The least squares slope is b₁ = Σ(x − x̄)(y − ȳ) ÷ Σ(x − x̄)² = ${f2(sxy)} ÷ ${f2(sxx)} = <b>${f2(b1, 3)}</b>. The intercept is b₀ = ȳ − b₁x̄ = <b>${f2(b0, 3)}</b>.` },
        { ...base, st: 5, say: `Draw ŷ = ${f2(b0)} + ${f2(b1)}x. No other straight line has a smaller sum of squared errors for these points.` },
        { ...base, st: 6, say: `The residuals (red) are the vertical gaps y − ŷ. Their squares add up to <b>SSE = ${f2(sse)}</b>, much less than the flat line’s ${f2(sst)}${sse < sst * 0.5 ? '' : ' (only a little less here)'}.` },
        { ...base, st: 7, say: `<b>R² = 1 − SSE ÷ SST = 1 − ${f2(sse)} ÷ ${f2(sst)} = ${f2(1 - sse / (sst || 1), 3)}</b>. The line explains ${f2(100 * (1 - sse / (sst || 1)), 1)}% of the variation in y. R² = 1 is a perfect fit and 0 is no better than the average.` }
      ];
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const xs = f.P.map(q => q.x), ys = f.P.map(q => q.y);
      const Pl = plot(z, [10, 10, 400, 310], span(xs, 0.12), span(ys.concat([f.b0 + f.b1 * Math.min(...xs), f.b0 + f.b1 * Math.max(...xs)]), 0.12), { dx: 1, dy: 1 });
      if (f.st === 3 || f.st === 4) {
        fline(z, Pl, f.my, 0, c.orange, 2, [6, 4]);
        f.P.forEach(q => D.line(g, Pl.X(q.x), Pl.Y(q.y), Pl.X(q.x), Pl.Y(f.my), c.orange, 1.5));
      }
      if (f.st >= 5) fline(z, Pl, f.b0, f.b1, c.cv, 2.5);
      if (f.st >= 6) f.P.forEach(q => D.line(g, Pl.X(q.x), Pl.Y(q.y), Pl.X(q.x), Pl.Y(f.b0 + f.b1 * q.x), c.red, 2));
      f.P.forEach(q => D.circle(g, Pl.X(q.x), Pl.Y(q.y), 5, { fill: c.ink }));
      if (f.st >= 2) { D.circle(g, Pl.X(f.mx), Pl.Y(f.my), 7, { stroke: c.green, w: 2.5 }); D.text(g, 'mean point', Pl.X(f.mx) + 10, Pl.Y(f.my) + 16, { s: 11, b: true, c: c.green }); }
      const x = 425;
      head(z, 'Numbers', x, 26);
      const rows = [];
      if (f.st >= 2) rows.push([`mean x = ${f2(f.mx)}`, c.ink], [`mean y = ${f2(f.my)}`, c.ink]);
      if (f.st >= 3) rows.push([`SST = ${f2(f.sst)}`, c.orange]);
      if (f.st >= 4) rows.push([`b₁ = ${f2(f.b1, 3)}`, c.cv], [`b₀ = ${f2(f.b0, 3)}`, c.cv]);
      if (f.st >= 6) rows.push([`SSE = ${f2(f.sse)}`, c.red]);
      if (f.st >= 7) rows.push([`R² = ${f2(1 - f.sse / (f.sst || 1), 3)}`, c.green]);
      rows.forEach(([t, col], i) => D.text(g, t, x, 56 + i * 26, { s: 13, mono: true, b: true, c: col }));
    }
  });
})();

/* =====================================================================================================
   Supervised 1.1  gradient descent fitting a line, one step at a time
   ===================================================================================================== */
(() => {
  const { trace, plot, span, fline, points, D, f2, head, rr } = MLZ;
  trace('mlgdline', {
    title: 'Gradient descent fits a line step by step',
    sub: 'The line starts flat at 0. Each step computes the gradient of the mean squared error and moves w (slope) and b (intercept) a little downhill.',
    W: 600, H: 330,
    params: [
      { k: 'pts', label: 'Points (x y)', type: 'area', v: '1 3; 2 5; 3 6; 4 9; 5 11' },
      { k: 'lr', label: 'Learning rate', type: 'range', v: 0.05, min: 0.01, max: 0.12, step: 0.01 },
      { k: 'n', label: 'Steps', type: 'range', v: 12, min: 4, max: 40 }
    ],
    tips: [
      { t: 'Learning rate 0.12: the line overshoots and the error goes up. That is divergence.', set: { lr: 0.12 }, play: true },
      { t: 'Learning rate 0.01: safe but slow, the line is still far off after 12 steps.', set: { lr: 0.01 }, play: true }
    ],
    frames(p) {
      const P = points(p.pts).slice(0, 25);
      if (P.length < 2) throw new Error('Type at least two points');
      const n = P.length;
      let w = 0, b = 0;
      const mse = (w, b) => P.reduce((a, q) => a + (w * q.x + b - q.y) ** 2, 0) / n;
      const hist = [mse(w, b)];
      const fr = [{ w, b, hist: hist.slice(), say: `Start with w = 0 and b = 0: a flat line at 0. The mean squared error is ${f2(hist[0], 3)}.` }];
      for (let i = 1; i <= p.n; i++) {
        const gw = 2 / n * P.reduce((a, q) => a + (w * q.x + b - q.y) * q.x, 0), gb = 2 / n * P.reduce((a, q) => a + (w * q.x + b - q.y), 0);
        w -= p.lr * gw; b -= p.lr * gb;
        const m = mse(w, b); hist.push(m);
        const bad = !isFinite(m) || m > 1e6;
        fr.push({ w, b, hist: hist.slice(), say: `Step ${i}: gradient ∂L/∂w = ${f2(gw, 2)}, ∂L/∂b = ${f2(gb, 2)}. New w = <b>${f2(w, 3)}</b>, b = <b>${f2(b, 3)}</b>, error ${f2(m, 3)}.${bad ? ' The error is exploding: lower the learning rate.' : ''}` });
        if (bad) return fr;
      }
      const mx = P.reduce((a, q) => a + q.x, 0) / n, my = P.reduce((a, q) => a + q.y, 0) / n;
      const b1 = P.reduce((a, q) => a + (q.x - mx) * (q.y - my), 0) / P.reduce((a, q) => a + (q.x - mx) ** 2, 0), b0 = my - b1 * mx;
      fr.push({ w, b, hist, done: true, b0, b1, say: `After ${p.n} steps: w = ${f2(w, 3)}, b = ${f2(b, 3)}. The exact least squares answer is w = ${f2(b1, 3)}, b = ${f2(b0, 3)} (green dashes). Gradient descent creeps towards it. The intercept is usually the slowest to settle when x is not centred, which is one reason to scale features.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = MLZ.points(z.p.pts).slice(0, 25);
      const Pl = plot(z, [10, 10, 400, 310], span(P.map(q => q.x).concat([0]), 0.1), span(P.map(q => q.y).concat([0]), 0.1), { dx: 0, dy: 0 });
      if (f.done) fline(z, Pl, f.b0, f.b1, c.green, 2, [6, 4]);
      fline(z, Pl, f.b, f.w, c.cv, 2.5);
      P.forEach(q => D.circle(g, Pl.X(q.x), Pl.Y(q.y), 5, { fill: c.ink }));
      head(z, 'Error after each step', 425, 26);
      const H = f.hist.filter(isFinite), max = Math.max(...H, 1e-9);
      const bw = Math.min(14, 160 / H.length);
      H.forEach((v, i) => { const h = Math.max(2, Math.min(220, v / max * 220)); rr(g, 428 + i * (bw + 1), 270 - h, bw, h, 2, { fill: i === H.length - 1 ? c.red : c.cv }); });
      D.text(g, `w = ${f2(f.w, 3)}`, 425, 292, { s: 12, mono: true, c: c.ink });
      D.text(g, `b = ${f2(f.b, 3)}`, 425, 310, { s: 12, mono: true, c: c.ink });
    }
  });
})();

/* =====================================================================================================
   Supervised 1.2  polynomial degree: underfitting, a good fit, and overfitting
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rng, rr } = MLZ;
  /* least squares polynomial fit on x scaled to [-1, 1], with a tiny ridge so high degrees stay solvable */
  function polyfit(xs, ys, deg, lam) {
    const m = deg + 1, A = Array.from({ length: m }, () => new Array(m + 1).fill(0));
    xs.forEach((x, k) => {
      const pw = [1]; for (let i = 1; i < m; i++) pw.push(pw[i - 1] * x);
      for (let i = 0; i < m; i++) { for (let j = 0; j < m; j++) A[i][j] += pw[i] * pw[j]; A[i][m] += pw[i] * ys[k]; }
    });
    for (let i = 1; i < m; i++) A[i][i] += lam;
    for (let c = 0; c < m; c++) {
      let piv = c; for (let r = c + 1; r < m; r++) if (Math.abs(A[r][c]) > Math.abs(A[piv][c])) piv = r;
      [A[c], A[piv]] = [A[piv], A[c]];
      for (let r = 0; r < m; r++) if (r !== c) { const t = A[r][c] / A[c][c]; for (let j = c; j <= m; j++) A[r][j] -= t * A[c][j]; }
    }
    return A.map((row, i) => row[m] / row[i]);
  }
  const val = (w, x) => w.reduce((a, c, i) => a + c * x ** i, 0);
  trace('mlpolyfit', {
    title: 'Polynomial degree: too simple, just right, too wiggly',
    sub: 'Filled purple dots are training data, hollow dots are test data. Each step fits a polynomial of a higher degree to the training dots and shows both errors.',
    W: 600, H: 330,
    params: [
      { k: 'n', label: 'Training points', type: 'range', v: 12, min: 8, max: 40 },
      { k: 'noise', label: 'Noise', type: 'range', v: 0.2, min: 0.05, max: 0.5, step: 0.05 },
      { k: 'lam', label: 'Ridge penalty (0 = none)', type: 'range', v: 0, min: 0, max: 1, step: 0.05 }
    ],
    tips: [
      { t: 'Add a small ridge penalty (0.05): the high degree curves calm down and the test error stays low.', set: { lam: 0.05 }, play: true },
      { t: 'With 40 training points even degree 12 behaves much better. More data fights overfitting.', set: { n: 40, lam: 0 }, play: true }
    ],
    frames(p) {
      const r = rng(5 + p.n);
      const gauss = () => { let s = 0; for (let i = 0; i < 6; i++) s += r(); return (s - 3) * Math.SQRT2; };
      const truth = x => Math.sin(Math.PI * (x + 1));
      const tr = Array.from({ length: p.n }, () => { const x = r() * 2 - 1; return { x, y: truth(x) + p.noise * gauss() }; });
      const te = Array.from({ length: 60 }, () => { const x = r() * 2 - 1; return { x, y: truth(x) + p.noise * gauss() }; });
      const mse = (w, S) => S.reduce((a, q) => a + (val(w, q.x) - q.y) ** 2, 0) / S.length;
      const fr = [{ tr, te, say: `Here are ${p.n} training points (filled purple) and 60 test points (hollow), all from the same smooth curve plus noise. The model only learns from the blue ones.` }];
      const all = [1, 2, 3, 5, 8, 12].map(d => {
        const w = polyfit(tr.map(q => q.x), tr.map(q => q.y), d, 1e-9 + p.lam);
        return { d, w, a: mse(w, tr), b: mse(w, te) };
      });
      const top = all.reduce((x, y) => y.b < x.b ? y : x);
      const hist = [];
      all.forEach(h => {
        hist.push({ d: h.d, a: h.a, b: h.b });
        const kind = h.b <= 1.6 * top.b ? 'Both errors are low: the curve follows the pattern, not the noise.' :
          h.d < top.d ? 'The curve is too stiff to follow the wave, so both errors are high. This is <b>underfitting</b> (high bias).' :
          'The training error is small but the test error grew: the curve chases the noise. This is <b>overfitting</b> (high variance).';
        fr.push({ tr, te, w: h.w, d: h.d, hist: hist.slice(), say: `Degree ${h.d}: training error ${f2(h.a, 3)}, test error <b>${f2(h.b, 3)}</b>. ${kind}` });
      });
      const best = top;
      fr.push({ tr, te, w: best.w, d: best.d, hist, done: true, say: `The lowest test error is at degree <b>${best.d}</b>. Training error alone always prefers the most complex model, so pick complexity with test or validation data. A ridge penalty (Ridge penalty slider) lets you keep a high degree and still avoid wild curves.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 310], [-1, 1], [-2, 2], { dx: 1, dy: 1 });
      f.te.forEach(q => D.circle(g, P.X(q.x), P.Y(q.y), 3.5, { stroke: c.ink2, w: 1 }));
      f.tr.forEach(q => D.circle(g, P.X(q.x), P.Y(q.y), 4.5, { fill: c.cv }));
      if (f.w) {
        g.save(); g.beginPath(); g.rect(P.x0, P.y0, P.w, P.h); g.clip(); g.beginPath();
        for (let i = 0; i <= 200; i++) { const x = -1 + i / 100, y = val(f.w, x); i ? g.lineTo(P.X(x), P.Y(y)) : g.moveTo(P.X(x), P.Y(y)); }
        g.strokeStyle = f.done ? c.green : c.orange; g.lineWidth = 2.5; g.stroke(); g.restore();
      }
      if (f.hist) {
        head(z, 'Error by degree', 425, 24);
        D.text(g, 'train', 470, 42, { s: 11, b: true, c: c.cv }); D.text(g, 'test', 520, 42, { s: 11, b: true, c: c.orange });
        /* scale the bars to the simple models, so one exploding test error does not flatten the rest */
        const max = Math.max(f.hist[0].a, f.hist[0].b, 0.05) * 1.25;
        f.hist.forEach((h, i) => {
          const y = 58 + i * 40;
          D.text(g, `d ${h.d}`, 425, y + 14, { s: 12, mono: true, b: true, c: h.d === f.d ? c.ink : c.ink2 });
          rr(g, 460, y, Math.max(2, Math.min(h.a, max) / max * 100), 12, 2, { fill: c.cv });
          rr(g, 460, y + 15, Math.max(2, Math.min(h.b, max) / max * 100), 12, 2, { fill: c.orange });
          if (h.b > max) D.text(g, 'more', 564, y + 25, { s: 10, b: true, c: c.orange });
        });
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 1.2  ridge shrinks weights, lasso sets some to exactly zero
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, rng, rr } = MLZ;
  const NAMES = ['size', 'rooms', 'age', 'noise1', 'noise2'];
  const TRUE = [3, 2, -1.5, 0, 0];
  function data() {
    const r = rng(4), g = () => { let s = 0; for (let i = 0; i < 6; i++) s += r(); return (s - 3) * Math.SQRT2; };
    const X = [], y = [];
    for (let i = 0; i < 60; i++) { const row = NAMES.map(() => g()); X.push(row); y.push(row.reduce((a, v, j) => a + v * TRUE[j], 0) + g()); }
    /* centre and scale the columns so one penalty treats every weight the same */
    for (let j = 0; j < 5; j++) { const m = X.reduce((a, r2) => a + r2[j], 0) / 60, s = Math.sqrt(X.reduce((a, r2) => a + (r2[j] - m) ** 2, 0) / 60); X.forEach(r2 => { r2[j] = (r2[j] - m) / s; }); }
    const my = y.reduce((a, b) => a + b, 0) / 60;
    return { X, y: y.map(v => v - my) };
  }
  function ridge(X, y, a) {
    const d = 5, A = Array.from({ length: d }, (_, i) => Array.from({ length: d + 1 }, (_, j) => j < d ? X.reduce((s, r) => s + r[i] * r[j], 0) / X.length + (i === j ? a : 0) : X.reduce((s, r, k) => s + r[i] * y[k], 0) / X.length));
    for (let c = 0; c < d; c++) for (let r = 0; r < d; r++) if (r !== c) { const t = A[r][c] / A[c][c]; for (let j = c; j <= d; j++) A[r][j] -= t * A[c][j]; }
    return A.map((row, i) => row[d] / row[i]);
  }
  function lasso(X, y, a) {
    const w = new Array(5).fill(0), n = X.length;
    for (let it = 0; it < 300; it++) for (let j = 0; j < 5; j++) {
      let rho = 0, zz = 0;
      X.forEach((r, k) => { const pred = r.reduce((s, v, m) => s + (m === j ? 0 : v * w[m]), 0); rho += r[j] * (y[k] - pred); zz += r[j] * r[j]; });
      rho /= n; zz /= n;
      w[j] = rho > a ? (rho - a) / zz : rho < -a ? (rho + a) / zz : 0;
    }
    return w;
  }
  trace('mlreg', {
    title: 'Ridge and lasso: what a penalty does to the weights',
    sub: 'Five features: three really matter (size, rooms, age) and two are pure noise. Each step makes the penalty α stronger and shows the weights of ridge (left bars) and lasso (right bars).',
    W: 600, H: 320,
    params: [{ k: 'show', label: 'Show', type: 'select', v: 'both', opts: [['both', 'Ridge and lasso'], ['ridge', 'Only ridge'], ['lasso', 'Only lasso']] }],
    frames(p) {
      const { X, y } = data();
      const alphas = [0, 0.1, 0.5, 1, 2, 4];
      return alphas.map((a, i) => {
        const R = ridge(X, y, a), L = lasso(X, y, a / 2);
        const zeros = L.filter(v => v === 0).length;
        return { a, R, L, say: i === 0 ? `With no penalty (α = 0) both are plain least squares: ${NAMES.map((n, j) => `${n} ${f2(R[j])}`).join(', ')}. The noise features get small weights that are not exactly 0.` :
          `α = ${a}. Ridge shrinks every weight a little towards 0 but none reaches 0 (biggest ${f2(Math.max(...R.map(Math.abs)))}). Lasso has set <b>${zeros}</b> weight${zeros === 1 ? '' : 's'} to exactly 0${zeros ? ` (${NAMES.filter((n, j) => L[j] === 0).join(', ')})` : ''}.${a >= 2 && zeros >= 3 ? ' A strong penalty starts to remove real features too, so α must be chosen with cross validation.' : ''}` };
      });
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, `Penalty α = ${f.a}`, 20, 24, { s: 15 });
      const zeroX = 330, sc = 70;
      D.line(g, zeroX, 40, zeroX, 300, c.ink2, 1.5);
      D.text(g, '0', zeroX, 314, { a: 'center', s: 11, c: c.ink2 });
      NAMES.forEach((n, j) => {
        const y = 52 + j * 50;
        D.text(g, n, 20, y + 20, { s: 13, b: true, c: j < 3 ? c.ink : c.ink2 });
        D.text(g, `true ${TRUE[j]}`, 100, y + 20, { s: 11, mono: true, c: c.ink2 });
        const bar = (v, dy, col, label) => {
          if (z.p.show !== 'both' && z.p.show !== label) return;
          const w = v * sc;
          rr(g, w >= 0 ? zeroX : zeroX + w, y + dy, Math.max(1.5, Math.abs(w)), 14, 3, { fill: col });
          D.text(g, `${label} ${v === 0 ? '0' : f2(v)}`, w >= 0 ? zeroX + w + 6 : zeroX + w - 6, y + dy + 11, { s: 11, mono: true, a: w >= 0 ? 'left' : 'right', c: col, b: v === 0 });
        };
        bar(f.R[j], 4, c.cv, 'ridge');
        bar(f.L[j], 22, c.orange, 'lasso');
      });
    }
  });
})();

/* =====================================================================================================
   Supervised 2.1  logistic regression: line, sigmoid, probability, threshold and log loss
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, points } = MLZ;
  const sig = z => 1 / (1 + Math.exp(-z));
  trace('mlsigmoid', {
    title: 'Logistic regression: from a score to a probability to a class',
    sub: 'Each point is a student: hours studied (x) and whether they passed (1) or failed (0). Set the weight w and bias b, then step through how the model turns x into a prediction and a loss.',
    W: 600, H: 330,
    params: [
      { k: 'pts', label: 'Points (hours label)', type: 'area', v: '0.5 0; 1 0; 1.5 0; 2 0; 2.5 1; 3 0; 3.5 1; 4 1; 4.5 1; 5 1' },
      { k: 'w', label: 'Weight w', type: 'range', v: 2.6, min: -3, max: 5, step: 0.1 },
      { k: 'b', label: 'Bias b', type: 'range', v: -7.1, min: -12, max: 4, step: 0.1 }
    ],
    tips: [
      { t: 'w = 1, b = −2.7: a gentle slope. Probabilities stay near 0.5, so the log loss is high even where the class is right.', set: { w: 1, b: -2.7 }, play: true },
      { t: 'w = −2.6, b = 7.1: the curve is flipped. Almost every prediction is wrong and the log loss is huge.', set: { w: -2.6, b: 7.1 }, play: true }
    ],
    frames(p) {
      const P = points(p.pts).slice(0, 20);
      if (P.length < 2) throw new Error('Type at least two points');
      if (P.some(q => q.y !== 0 && q.y !== 1)) throw new Error('Each label must be 0 or 1');
      const rows = P.map(q => { const z = p.w * q.x + p.b, pr = sig(z); return { ...q, z, pr, pred: pr >= 0.5 ? 1 : 0, loss: -(q.y ? Math.log(Math.max(pr, 1e-12)) : Math.log(Math.max(1 - pr, 1e-12))) }; });
      const L = rows.reduce((a, r) => a + r.loss, 0) / rows.length, acc = rows.filter(r => r.pred === r.y).length;
      const b = { rows, L, acc };
      const worst = rows.reduce((x, y) => y.loss > x.loss ? y : x);
      return [
        { ...b, st: 1, say: `${rows.length} students. Red dots failed (label 0) and purple dots passed (label 1). We want P(pass) for any number of hours.` },
        { ...b, st: 2, say: `Step 1, a straight line score: z = w x + b = ${f2(p.w, 1)}x ${p.b < 0 ? '−' : '+'} ${f2(Math.abs(p.b), 1)}. For x = ${rows[0].x}, z = ${f2(rows[0].z)}. A score can be any number, so it is not yet a probability.` },
        { ...b, st: 3, say: 'Step 2, squash the score with the sigmoid σ(z) = 1 ÷ (1 + e^(−z)). Big negative z gives almost 0, z = 0 gives 0.5, big positive z gives almost 1. The green S curve is the model.' },
        { ...b, st: 4, say: `Step 3, every student now has a probability of passing (the dots on the curve). For example x = ${rows[rows.length - 1].x} gives ${f2(rows[rows.length - 1].pr, 3)}.` },
        { ...b, st: 5, say: `Step 4, predict "pass" when the probability is at least 0.5. The boundary is where z = 0, at x = −b ÷ w = ${p.w ? f2(-p.b / p.w) : 'none'}. <b>${acc} of ${rows.length}</b> students are classified correctly (wrong ones have a dark ring).` },
        { ...b, st: 6, say: `Step 5, log loss scores the probabilities, not just the classes: −ln(p) for a pass and −ln(1 − p) for a fail. The worst point is x = ${worst.x} with loss ${f2(worst.loss, 3)}. The average log loss is <b>${f2(L, 4)}</b>. Training picks w and b to make this as small as possible.` }
      ];
    },
    paint(z, f) {
      const c = z.col, g = z.g, xs = f.rows.map(r => r.x);
      const lo = Math.min(...xs) - 0.5, hi = Math.max(...xs) + 0.5;
      const P = plot(z, [10, 10, 400, 310], [lo, hi], [-0.1, 1.1], { dx: 1, dy: 1 });
      if (f.st >= 5) { D.line(g, P.X(lo), P.Y(0.5), P.X(hi), P.Y(0.5), c.ink2, 1, [5, 4]); if (z.p.w) { const xb = -z.p.b / z.p.w; if (xb > lo && xb < hi) D.line(g, P.X(xb), P.Y(-0.1), P.X(xb), P.Y(1.1), c.orange, 2, [6, 4]); } }
      if (f.st >= 3) {
        g.save(); g.beginPath();
        for (let i = 0; i <= 160; i++) { const x = lo + (hi - lo) * i / 160, y = sig(z.p.w * x + z.p.b); i ? g.lineTo(P.X(x), P.Y(y)) : g.moveTo(P.X(x), P.Y(y)); }
        g.strokeStyle = c.green; g.lineWidth = 2.5; g.stroke(); g.restore();
      }
      f.rows.forEach(r => {
        const col = r.y ? c.cv : c.red;
        D.circle(g, P.X(r.x), P.Y(r.y), 5.5, { fill: col });
        if (f.st >= 4) { D.line(g, P.X(r.x), P.Y(r.y), P.X(r.x), P.Y(r.pr), c.line, 1, [2, 3]); D.circle(g, P.X(r.x), P.Y(r.pr), 4, { fill: c.green }); }
        if (f.st >= 5 && r.pred !== r.y) D.circle(g, P.X(r.x), P.Y(r.y), 9, { stroke: c.ink, w: 2 });
      });
      head(z, f.st >= 6 ? 'Log loss per point' : 'Score z = w x + b', 425, 24);
      if (f.st >= 2) f.rows.slice(0, 10).forEach((r, i) => {
        const y = 46 + i * 26;
        D.text(g, `x ${r.x}`, 425, y, { s: 11, mono: true, c: c.ink2 });
        if (f.st >= 6) { const w = Math.min(100, r.loss * 40); MLZ.rr(g, 470, y - 10, Math.max(2, w), 12, 2, { fill: r.y ? c.cv : c.red }); D.text(g, f2(r.loss, 2), 474 + w, y, { s: 11, mono: true, c: c.ink }); }
        else D.text(g, `z ${f2(r.z, 2)}${f.st >= 4 ? `  p ${f2(r.pr, 2)}` : ''}`, 470, y, { s: 11, mono: true, c: c.ink });
      });
    }
  });
})();

/* =====================================================================================================
   Supervised 2.1  training logistic regression with gradient descent
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, points, rr } = MLZ;
  const sig = z => 1 / (1 + Math.exp(-z));
  trace('mllogfit', {
    title: 'Training logistic regression: the S curve learns',
    sub: 'Start from w = 0 and b = 0 (a flat 0.5 for everyone). Each step moves w and b against the gradient of the log loss. Watch the curve get steeper and slide into place.',
    W: 600, H: 330,
    params: [
      { k: 'pts', label: 'Points (x label)', type: 'area', v: '0.5 0; 1 0; 1.5 0; 2 0; 2.5 1; 3 0; 3.5 1; 4 1; 4.5 1; 5 1' },
      { k: 'lr', label: 'Learning rate', type: 'range', v: 0.5, min: 0.1, max: 2, step: 0.1 },
      { k: 'every', label: 'Gradient steps between pictures', type: 'range', v: 50, min: 1, max: 200 }
    ],
    tips: [
      { t: 'Perfectly separated data (no overlap): the weights keep growing forever and the curve becomes a step. That is why logistic regression needs a penalty (C) for separable data.', set: { pts: '1 0; 2 0; 3 0; 4 1; 5 1; 6 1' }, play: true }
    ],
    frames(p) {
      const P = points(p.pts).slice(0, 20);
      if (P.length < 2 || P.some(q => q.y !== 0 && q.y !== 1)) throw new Error('Type at least two points, each label 0 or 1');
      const n = P.length;
      let w = 0, b = 0;
      const loss = () => P.reduce((a, q) => { const pr = Math.min(1 - 1e-12, Math.max(1e-12, sig(w * q.x + b))); return a - (q.y ? Math.log(pr) : Math.log(1 - pr)); }, 0) / n;
      const hist = [loss()];
      const fr = [{ w, b, hist: hist.slice(), say: `Start: w = 0, b = 0, so everyone gets probability 0.5. Log loss = ln 2 = ${f2(hist[0], 4)}.` }];
      for (let k = 1; k <= 10; k++) {
        let gw = 0, gb = 0;
        for (let s = 0; s < p.every; s++) {
          gw = 0; gb = 0;
          P.forEach(q => { const e = sig(w * q.x + b) - q.y; gw += e * q.x / n; gb += e / n; });
          w -= p.lr * gw; b -= p.lr * gb;
        }
        hist.push(loss());
        fr.push({ w, b, hist: hist.slice(), say: `After ${k * p.every} steps: gradient ∂L/∂w = Σ(p − y)x ÷ n = ${f2(gw, 3)}, so w = <b>${f2(w, 3)}</b> and b = <b>${f2(b, 3)}</b>. Log loss ${f2(hist[k], 4)}. The 50% point is at x = ${w ? f2(-b / w) : '?'}.` });
      }
      fr.push({ w, b, hist, done: true, say: `The gradient of the log loss has the same simple form as in linear regression: (prediction − label) × x. The loss is convex, so gradient descent cannot get stuck in a wrong valley. scikit-learn uses faster solvers (lbfgs) for the same job.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, P = points(z.p.pts).slice(0, 20), xs = P.map(q => q.x);
      const lo = Math.min(...xs) - 0.5, hi = Math.max(...xs) + 0.5;
      const Pl = plot(z, [10, 10, 400, 310], [lo, hi], [-0.1, 1.1], { dx: 1, dy: 1 });
      g.save(); g.beginPath();
      for (let i = 0; i <= 160; i++) { const x = lo + (hi - lo) * i / 160, y = sig(f.w * x + f.b); i ? g.lineTo(Pl.X(x), Pl.Y(y)) : g.moveTo(Pl.X(x), Pl.Y(y)); }
      g.strokeStyle = c.green; g.lineWidth = 2.5; g.stroke(); g.restore();
      P.forEach(q => D.circle(g, Pl.X(q.x), Pl.Y(q.y), 5.5, { fill: q.y ? c.cv : c.red }));
      head(z, 'Log loss', 425, 26);
      const max = Math.max(...f.hist, 1e-9);
      f.hist.forEach((v, i) => { const h = Math.max(2, v / max * 200); rr(g, 428 + i * 14, 250 - h, 12, h, 2, { fill: i === f.hist.length - 1 ? c.red : c.cv }); });
      D.text(g, `w = ${f2(f.w, 3)}`, 425, 280, { s: 12, mono: true, c: c.ink });
      D.text(g, `b = ${f2(f.b, 3)}`, 425, 300, { s: 12, mono: true, c: c.ink });
    }
  });
})();

/* =====================================================================================================
   Supervised 2.2  k nearest neighbours: measure, sort, take k, vote
   ===================================================================================================== */
(() => {
  const { trace, plot, span, points, D, f2, head, klass } = MLZ;
  trace('mlknn', {
    title: 'k nearest neighbours: ask the closest examples',
    sub: 'Type labelled points (x y class) and a new point. KNN measures the distance to every point, keeps the k closest and lets them vote.',
    W: 600, H: 330,
    params: [
      { k: 'pts', label: 'Points (x y class)', type: 'area', v: '1 2 A; 2 1 A; 2 3 A; 3 2 A; 6 5 B; 7 6 B; 6 7 B; 5 6 B; 4 4 B; 3 5 A' },
      { k: 'q', label: 'New point (x, y)', type: 'text', v: '4, 3.5' },
      { k: 'k', label: 'k (neighbours)', type: 'range', v: 3, min: 1, max: 9, step: 1 },
      { k: 'metric', label: 'Distance', type: 'select', v: 'euclid', opts: [['euclid', 'Euclidean (straight line)'], ['manhattan', 'Manhattan (city blocks)']] }
    ],
    tips: [
      { t: 'k = 1: the single closest point decides. One noisy point can flip the answer.', set: { k: 1 }, play: true },
      { t: 'k = 9: almost everyone votes, so the bigger class tends to win everywhere.', set: { k: 9 }, play: true }
    ],
    frames(p) {
      const P = points(p.pts, true).slice(0, 30);
      const q = MLZ.nums(p.q);
      if (P.length < 2 || q.length < 2) throw new Error('Type at least two points and a new point like 4, 3.5');
      const k = Math.min(p.k, P.length);
      const dist = (a) => p.metric === 'manhattan' ? Math.abs(a.x - q[0]) + Math.abs(a.y - q[1]) : Math.hypot(a.x - q[0], a.y - q[1]);
      const rows = P.map((a, i) => ({ ...a, i, d: dist(a) })).sort((a, b) => a.d - b.d);
      const near = rows.slice(0, k), votes = {};
      near.forEach(r => { votes[r.c] = (votes[r.c] || 0) + 1; });
      const ranked = Object.keys(votes).sort((a, b) => votes[b] - votes[a]);
      const tie = ranked.length > 1 && votes[ranked[0]] === votes[ranked[1]];
      const winner = tie ? near[0].c : ranked[0];
      const classes = [...new Set(P.map(a => a.c))];
      const b = { P, q, rows, k, near, votes, winner, classes };
      const fr = [
        { ...b, st: 1, say: `${P.length} labelled examples in ${classes.length} classes, and a new point at (${q[0]}, ${q[1]}) (the star). KNN has no training step: it just keeps all the examples.` },
        { ...b, st: 2, say: `Measure the ${p.metric === 'manhattan' ? 'Manhattan distance |Δx| + |Δy|' : 'Euclidean distance √(Δx² + Δy²)'} from the new point to every example. The closest is (${rows[0].x}, ${rows[0].y}) at ${f2(rows[0].d)}.` }
      ];
      near.forEach((r, j) => fr.push({ ...b, st: 3, upto: j + 1, say: `Neighbour ${j + 1} of ${k}: (${r.x}, ${r.y}), class <b>${r.c}</b>, distance ${f2(r.d)}.` }));
      fr.push({ ...b, st: 4, upto: k, say: `Votes: ${ranked.map(c => `${c} ${votes[c]}`).join(', ')}. ${tie ? `It is a tie, so we use the single closest neighbour, class <b>${winner}</b>. An odd k avoids ties with two classes.` : `The prediction is class <b>${winner}</b>.`}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const xs = f.P.map(a => a.x).concat([f.q[0]]), ys = f.P.map(a => a.y).concat([f.q[1]]);
      const Pl = plot(z, [10, 10, 400, 310], span(xs, 0.12), span(ys, 0.12), { dx: 0, dy: 0 });
      const col = name => klass(z, f.classes.indexOf(name));
      if (f.st >= 3) {
        const r = f.near[(f.upto || 1) - 1].d;
        if (z.p.metric !== 'manhattan') { g.save(); g.setLineDash([5, 4]); g.strokeStyle = c.ink2; g.lineWidth = 1.2; g.beginPath(); g.ellipse(Pl.X(f.q[0]), Pl.Y(f.q[1]), Math.abs(Pl.X(f.q[0] + r) - Pl.X(f.q[0])), Math.abs(Pl.Y(f.q[1] + r) - Pl.Y(f.q[1])), 0, 0, Math.PI * 2); g.stroke(); g.restore(); }
      }
      if (f.st >= 2) f.rows.forEach((a, j) => {
        const isNear = f.st >= 3 && j < (f.upto || 0);
        D.line(g, Pl.X(f.q[0]), Pl.Y(f.q[1]), Pl.X(a.x), Pl.Y(a.y), isNear ? col(a.c) : c.line, isNear ? 2.2 : 0.8, isNear ? undefined : [2, 3]);
      });
      f.P.forEach(a => D.circle(g, Pl.X(a.x), Pl.Y(a.y), 6, { fill: col(a.c) }));
      f.P.forEach(a => D.text(g, a.c, Pl.X(a.x), Pl.Y(a.y) - 9, { a: 'center', s: 10, b: true, c: c.ink2 }));
      const sx = Pl.X(f.q[0]), sy = Pl.Y(f.q[1]);
      g.save(); g.beginPath();
      for (let i = 0; i < 10; i++) { const rr = i % 2 ? 4 : 10, an = -Math.PI / 2 + i * Math.PI / 5; g.lineTo(sx + rr * Math.cos(an), sy + rr * Math.sin(an)); }
      g.closePath(); g.fillStyle = f.st >= 4 ? col(f.winner) : c.ink; g.fill(); g.restore();
      head(z, f.st >= 2 ? 'Nearest first' : 'Examples', 425, 24);
      if (f.st >= 2) f.rows.slice(0, 9).forEach((a, j) => {
        const isNear = f.st >= 3 && j < (f.upto || 0);
        D.text(g, `${j + 1}. ${a.c}  d = ${f2(a.d)}`, 425, 48 + j * 22, { s: 12, mono: true, b: isNear, c: isNear ? col(a.c) : c.ink2 });
      });
      if (f.st >= 4) D.text(g, `prediction: ${f.winner}`, 425, 260, { s: 15, b: true, c: col(f.winner) });
    }
  });
})();

/* =====================================================================================================
   Supervised 2.2  how k changes the decision regions
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rng, klass, rr } = MLZ;
  function moons(n, noise, seed) {
    const r = rng(seed), g = () => { let s = 0; for (let i = 0; i < 6; i++) s += r(); return (s - 3) * Math.SQRT2; };
    const P = [];
    for (let i = 0; i < n; i++) {
      const t = Math.PI * r(), up = i % 2 === 0;
      const x = up ? Math.cos(t) : 1 - Math.cos(t), y = up ? Math.sin(t) : 0.5 - Math.sin(t);
      P.push({ x: x + noise * g(), y: y + noise * g(), c: up ? 0 : 1 });
    }
    return P;
  }
  const vote = (P, x, y, k) => { const d = P.map(a => [(a.x - x) ** 2 + (a.y - y) ** 2, a.c]).sort((a, b) => a[0] - b[0]).slice(0, k); const s = d.reduce((a, t) => a + t[1], 0); return s * 2 > k ? 1 : 0; };
  trace('mlkregions', {
    title: 'Choosing k: wiggly or smooth decision regions',
    sub: 'Two moon shaped classes with noise. Each step colours the whole plane by the KNN vote for a bigger k and shows training and test accuracy.',
    W: 600, H: 330,
    params: [{ k: 'noise', label: 'Noise', type: 'range', v: 0.3, min: 0.05, max: 0.5, step: 0.05 }],
    tips: [{ t: 'With little noise even k = 1 does well, because the classes barely overlap.', set: { noise: 0.1 }, play: true }],
    frames(p) {
      const tr = moons(120, p.noise, 3), te = moons(200, p.noise, 99);
      const acc = (S, k) => S.filter(a => vote(tr, a.x, a.y, k) === a.c).length / S.length;
      const fr = [{ tr, say: '120 training points from two moon shaped classes. The classes overlap where the noise pushes points across.' }];
      const res = [];
      [1, 5, 15, 45, 119].forEach(k => {
        const a = acc(tr, k), b = acc(te, k);
        res.push({ k, a, b });
        fr.push({ tr, k, res: res.slice(), say: `k = ${k}: training accuracy ${f2(a * 100, 1)}%, test accuracy <b>${f2(b * 100, 1)}%</b>. ${k === 1 ? 'Every training point is its own nearest neighbour, so training accuracy is 100%, but the regions are full of islands around noisy points (overfitting).' : k >= 100 ? 'Almost every point votes, so the prediction is nearly the same everywhere (underfitting).' : 'The regions get smoother as more neighbours vote.'}` });
      });
      const best = res.reduce((x, y) => y.b > x.b ? y : x);
      fr.push({ tr, k: best.k, res, done: true, say: `The best test accuracy here is at k = <b>${best.k}</b>. Small k means low bias and high variance, large k means high bias and low variance. Choose k with cross validation, and prefer an odd k for two classes.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 310], [-1.5, 2.5], [-1.2, 1.7], { dx: 1, dy: 1, grid: false });
      if (f.k) {
        const cell = 8;
        g.save(); g.globalAlpha = 0.22;
        for (let px = P.x0 + 26; px < P.x0 + P.w - 10; px += cell) for (let py = P.y0 + 10; py < P.y0 + P.h - 20; py += cell) {
          const x = -1.5 + (px + cell / 2 - P.x0 - 26) / (P.w - 36) * 4, y = -1.2 + (P.y0 + P.h - 20 - (py + cell / 2)) / (P.h - 30) * 2.9;
          g.fillStyle = klass(z, vote(f.tr, x, y, f.k)); g.fillRect(px, py, cell, cell);
        }
        g.restore();
      }
      f.tr.forEach(a => D.circle(g, P.X(a.x), P.Y(a.y), 4, { fill: klass(z, a.c), stroke: c.surf, w: 1 }));
      if (f.res) {
        head(z, 'Accuracy by k', 425, 24);
        D.text(g, 'train', 470, 42, { s: 11, b: true, c: c.cv }); D.text(g, 'test', 520, 42, { s: 11, b: true, c: c.orange });
        f.res.forEach((r, i) => {
          const y = 56 + i * 44;
          D.text(g, `k ${r.k}`, 425, y + 14, { s: 12, mono: true, b: true, c: r.k === f.k ? c.ink : c.ink2 });
          rr(g, 470, y, Math.max(2, (r.a - 0.5) * 2 * 100), 12, 2, { fill: c.cv });
          rr(g, 470, y + 15, Math.max(2, (r.b - 0.5) * 2 * 100), 12, 2, { fill: c.orange });
          D.text(g, f2(r.b * 100, 0) + '%', 476 + Math.max(2, (r.b - 0.5) * 200), y + 26, { s: 10, b: true, c: c.orange });
        });
        D.text(g, 'bars start at 50%', 425, 300, { s: 10, c: c.ink2 });
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 2.3  naive Bayes on words: prior times one likelihood per word
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, rr, list } = MLZ;
  trace('mlnbspam', {
    title: 'Naive Bayes spam filter: multiply the clues',
    sub: 'Training messages are counted word by word. For a new message we start from the prior and multiply in P(word | class) for every word, for spam and for not spam (ham), then compare.',
    W: 600, H: 330,
    params: [
      { k: 'spam', label: 'Spam messages (one per line)', type: 'area', v: 'win money now\nwin a free prize\nfree money offer\nclaim your prize now' },
      { k: 'ham', label: 'Ham messages (one per line)', type: 'area', v: 'meeting at noon\nlunch money for friday\nproject meeting now\nsee you at lunch' },
      { k: 'msg', label: 'New message', type: 'text', v: 'free money now' },
      { k: 'alpha', label: 'Smoothing α', type: 'range', v: 1, min: 0, max: 2, step: 0.5 }
    ],
    tips: [
      { t: 'α = 0 and a word never seen in ham ("free"): P(free | ham) = 0 wipes out the whole ham score. Smoothing prevents that.', set: { alpha: 0 }, play: true },
      { t: 'A friendly message: "lunch meeting now".', set: { msg: 'lunch meeting now', alpha: 1 }, play: true }
    ],
    frames(p) {
      const lines = s => String(s).split(/\n+/).map(t => t.trim().toLowerCase()).filter(Boolean);
      const S = lines(p.spam), H = lines(p.ham);
      if (!S.length || !H.length) throw new Error('Give at least one spam and one ham message');
      const count = M => { const c = {}; let t = 0; M.forEach(m => m.split(/\s+/).forEach(w => { c[w] = (c[w] || 0) + 1; t++; })); return [c, t]; };
      const [sc, st] = count(S), [hc, ht] = count(H);
      const V = new Set([...Object.keys(sc), ...Object.keys(hc)]).size;
      const words = list(String(p.msg).toLowerCase()).slice(0, 6);
      if (!words.length) throw new Error('Type a new message');
      const a = p.alpha;
      const pw = (w, c, t) => (t + a * V) ? ((c[w] || 0) + a) / (t + a * V) : 0;
      let ps = S.length / (S.length + H.length), ph = 1 - ps;
      const rows = [];
      const fr = [{ rows: [], ps, ph, say: `Training: ${S.length} spam and ${H.length} ham messages, ${V} different words. The prior is P(spam) = ${f2(ps, 3)} and P(ham) = ${f2(ph, 3)}: before reading the new message, that is all we know.` }];
      words.forEach(w => {
        const a1 = pw(w, sc, st), b1 = pw(w, hc, ht);
        ps *= a1; ph *= b1;
        rows.push({ w, a1, b1 });
        fr.push({ rows: rows.slice(), ps, ph, say: `Word "${w}": seen ${sc[w] || 0} times in ${st} spam words and ${hc[w] || 0} times in ${ht} ham words. With smoothing α = ${a}, P(${w} | spam) = (${sc[w] || 0} + ${a}) ÷ (${st} + ${a} × ${V}) = ${f2(a1, 4)} and P(${w} | ham) = ${f2(b1, 4)}. Multiply them in.` });
      });
      const tot = ps + ph;
      fr.push({ rows, ps, ph, done: true, post: tot ? ps / tot : 0.5, say: tot ? `Scores: spam ${ps.toExponential(2)}, ham ${ph.toExponential(2)}. Divide each by their sum: <b>P(spam | message) = ${f2(ps / tot, 3)}</b>. "Naive" means we multiplied the words as if they were independent, which is not true, but the ranking is usually still right.` : 'Both scores are 0 because a word is missing from both classes and α = 0. Raise α.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, 'Word', 20, 26); head(z, 'P(word | spam)', 130, 26); head(z, 'P(word | ham)', 300, 26);
      f.rows.forEach((r, i) => {
        const y = 44 + i * 30;
        D.text(g, r.w, 20, y + 13, { s: 14, b: true, mono: true, c: c.ink });
        const bar = (x, v, col) => { rr(g, x, y, Math.max(2, v * 900), 16, 3, { fill: col }); D.text(g, f2(v, 4), x + Math.max(2, v * 900) + 4, y + 13, { s: 11, mono: true, c: col, b: v === 0 }); };
        bar(130, Math.min(r.a1, 0.15), c.orange); bar(300, Math.min(r.b1, 0.15), c.cv);
      });
      const y0 = 240;
      head(z, 'Running score (prior × word probabilities)', 20, y0);
      D.text(g, `spam  ${f.ps.toExponential(3)}`, 20, y0 + 26, { s: 13, mono: true, b: true, c: c.orange });
      D.text(g, `ham   ${f.ph.toExponential(3)}`, 20, y0 + 48, { s: 13, mono: true, b: true, c: c.cv });
      if (f.done) {
        rr(g, 330, y0 + 8, 240, 26, 6, { fill: c.bg });
        rr(g, 330, y0 + 8, 240 * f.post, 26, 6, { fill: c.orange });
        D.text(g, `P(spam) = ${f2(f.post, 3)}`, 340, y0 + 26, { s: 13, b: true, c: f.post > 0.5 ? '#fff' : c.ink });
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 2.3  Gaussian naive Bayes on one feature
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, nums, klass } = MLZ;
  const pdf = (x, m, v) => Math.exp(-((x - m) ** 2) / (2 * v)) / Math.sqrt(2 * Math.PI * v);
  trace('mlgnb', {
    title: 'Gaussian naive Bayes: a bell curve per class',
    sub: 'Two classes measured on one feature. The model fits a normal curve to each class, then for a new value compares prior × curve height.',
    W: 600, H: 320,
    params: [
      { k: 'a', label: 'Class A values', type: 'text', v: '1.4, 1.5, 1.3, 1.6, 1.4, 1.7, 1.5' },
      { k: 'b', label: 'Class B values', type: 'text', v: '4.2, 4.7, 3.9, 4.5, 5.1, 4.0' },
      { k: 'x', label: 'New value', type: 'range', v: 3, min: 0, max: 8, step: 0.1 }
    ],
    tips: [{ t: 'Try x = 2.4: much closer to A in distance, yet B can win because B has a much wider curve.', set: { x: 2.4 }, play: true }],
    frames(p) {
      const A = nums(p.a), B = nums(p.b);
      if (A.length < 2 || B.length < 2) throw new Error('Give each class at least two values');
      const st = v => { const m = v.reduce((s, t) => s + t, 0) / v.length; return [m, Math.max(1e-3, v.reduce((s, t) => s + (t - m) ** 2, 0) / v.length)]; };
      const [ma, va] = st(A), [mb, vb] = st(B), pa = A.length / (A.length + B.length), pb = 1 - pa;
      const la = pdf(p.x, ma, va), lb = pdf(p.x, mb, vb), sa = pa * la, sb = pb * lb, tot = sa + sb || 1;
      const base = { A, B, ma, va, mb, vb };
      return [
        { ...base, st: 1, say: `Class A has ${A.length} values and class B has ${B.length}. The prior P(A) = ${f2(pa, 3)}, P(B) = ${f2(pb, 3)}.` },
        { ...base, st: 2, say: `Fit a normal curve to A: mean ${f2(ma)}, variance ${f2(va, 3)}.` },
        { ...base, st: 3, say: `Fit a normal curve to B: mean ${f2(mb)}, variance ${f2(vb, 3)}. B is spread out much more${vb > va ? '' : ' (or less)'}.` },
        { ...base, st: 4, say: `New value x = ${p.x}. Curve heights: p(x | A) = ${la.toExponential(2)}, p(x | B) = ${lb.toExponential(2)}.` },
        { ...base, st: 5, x: p.x, post: sa / tot, say: `Multiply by the priors and normalise: <b>P(A | x) = ${f2(sa / tot, 3)}</b>, P(B | x) = ${f2(sb / tot, 3)}. Predict <b>${sa >= sb ? 'A' : 'B'}</b>. With several features, Gaussian naive Bayes multiplies one such curve per feature.` }
      ];
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 300], [0, 8], [0, Math.max(pdf(f.ma, f.ma, f.va), pdf(f.mb, f.mb, f.vb)) * 1.1], { dx: 0, dy: 1 });
      const curve = (m, v, col) => { g.save(); g.beginPath(); for (let i = 0; i <= 200; i++) { const x = 8 * i / 200; i ? g.lineTo(P.X(x), P.Y(pdf(x, m, v))) : g.moveTo(P.X(x), P.Y(pdf(x, m, v))); } g.strokeStyle = col; g.lineWidth = 2.5; g.stroke(); g.restore(); };
      f.A.forEach(v => D.circle(g, P.X(v), P.Y(0) - 6, 4.5, { fill: klass(z, 0) }));
      f.B.forEach(v => D.circle(g, P.X(v), P.Y(0) - 16, 4.5, { fill: klass(z, 1) }));
      if (f.st >= 2) curve(f.ma, f.va, klass(z, 0));
      if (f.st >= 3) curve(f.mb, f.vb, klass(z, 1));
      if (f.st >= 4) D.line(g, P.X(z.p.x), P.Y(0), P.X(z.p.x), P.y0 + 12, c.red, 2, [5, 4]);
      head(z, 'Class A', 425, 30, { c: klass(z, 0) }); D.text(g, `mean ${f2(f.ma)}  var ${f2(f.va, 3)}`, 425, 50, { s: 12, mono: true, c: c.ink });
      if (f.st >= 3) { head(z, 'Class B', 425, 84, { c: klass(z, 1) }); D.text(g, `mean ${f2(f.mb)}  var ${f2(f.vb, 3)}`, 425, 104, { s: 12, mono: true, c: c.ink }); }
      if (f.st >= 5) { head(z, `P(A | x = ${z.p.x})`, 425, 150); D.text(g, f2(f.post, 3), 425, 184, { s: 26, b: true, mono: true, c: f.post >= 0.5 ? klass(z, 0) : klass(z, 1) }); }
    }
  });
})();

/* =====================================================================================================
   Supervised 2.4  the widest street: a hard margin linear SVM, found by trying every direction
   ===================================================================================================== */
(() => {
  const { trace, plot, points, D, f2, head, klass } = MLZ;
  /* the gap between the classes when every point is projected onto the direction at angle t */
  function gap(P, t) {
    const ux = Math.cos(t), uy = Math.sin(t);
    let hiA = -Infinity, loB = Infinity;
    P.forEach(a => { const s = a.x * ux + a.y * uy; if (a.s < 0) hiA = Math.max(hiA, s); else loB = Math.min(loB, s); });
    return { g: loB - hiA, mid: (loB + hiA) / 2, t, ux, uy };
  }
  function widest(P) {
    let best = null;
    const ok = [];
    for (let i = 0; i < 1440; i++) {
      const r = gap(P, i * Math.PI / 720);
      if (r.g > 0) ok.push(r);
      if (!best || r.g > best.g) best = r;
    }
    let lo = best.t - Math.PI / 720, hi = best.t + Math.PI / 720;
    for (let i = 0; i < 60; i++) {
      const m1 = lo + (hi - lo) / 3, m2 = hi - (hi - lo) / 3;
      if (gap(P, m1).g < gap(P, m2).g) lo = m1; else hi = m2;
    }
    return { best: gap(P, (lo + hi) / 2), ok };
  }
  /* draw the line ux x + uy y = k inside the plot */
  function uline(z, P, ux, uy, k, col, w, dash) {
    const g = z.g;
    g.save(); g.beginPath(); g.rect(P.x0, P.y0, P.w, P.h); g.clip();
    if (Math.abs(uy) > Math.abs(ux)) {
      const ya = (k - ux * P.xr[0]) / uy, yb = (k - ux * P.xr[1]) / uy;
      D.line(g, P.X(P.xr[0]), P.Y(ya), P.X(P.xr[1]), P.Y(yb), col, w, dash);
    } else {
      const xa = (k - uy * P.yr[0]) / ux, xb = (k - uy * P.yr[1]) / ux;
      D.line(g, P.X(xa), P.Y(P.yr[0]), P.X(xb), P.Y(P.yr[1]), col, w, dash);
    }
    g.restore();
  }
  trace('mlsvm', {
    title: 'Support vector machine: find the widest street',
    sub: 'Type points of two classes (x y class). Many straight lines separate them. The SVM picks the one with the widest empty street on both sides, and only the points on the edge of the street matter.',
    W: 600, H: 330,
    params: [{ k: 'pts', label: 'Points (x y class)', type: 'area', v: '1 1 A; 2 1 A; 1 2 A; 4 4 B; 5 4 B; 4 5 B' }],
    tips: [
      { t: 'Add a far away point such as 0 0 A: it is not on the street, so the boundary does not move.', set: { pts: '1 1 A; 2 1 A; 1 2 A; 0 0 A; 4 4 B; 5 4 B; 4 5 B' }, play: true },
      { t: 'Move one B point closer (3 3 B): the street gets narrower and the support vectors change.', set: { pts: '1 1 A; 2 1 A; 1 2 A; 3 3 B; 5 4 B; 4 5 B' }, play: true },
      { t: 'Put a B point among the A points: no straight line separates them, so a hard margin is impossible.', set: { pts: '1 1 A; 2 1 A; 1 2 A; 1.5 1.5 B; 4 4 B; 5 4 B; 4 5 B' }, play: true }
    ],
    frames(p) {
      const raw = points(p.pts, true).slice(0, 30);
      const classes = [...new Set(raw.map(a => a.c))].sort();
      if (classes.length !== 2) throw new Error('Use exactly two class names, for example A and B');
      const P = raw.map(a => ({ ...a, s: a.c === classes[0] ? -1 : 1 }));
      const nA = P.filter(a => a.s < 0).length;
      const b0 = { P, classes };
      const fr = [{ ...b0, st: 1, say: `${nA} points of class ${classes[0]} and ${P.length - nA} of class ${classes[1]}. We want a straight line that puts the two classes on different sides.` }];
      const { best, ok } = widest(P);
      if (best.g <= 0) {
        fr.push({ ...b0, st: 1, say: 'No straight line can separate these two classes: every direction leaves the classes overlapping. A hard margin SVM has no answer here. The soft margin version (with C) allows a few points on the wrong side, and a kernel can bend the boundary.' });
        return fr;
      }
      const cand = [ok[Math.floor(ok.length * 0.15)], ok[Math.floor(ok.length * 0.8)]].filter(r => r && Math.abs(r.t - best.t) > 0.05);
      cand.forEach((r, i) => fr.push({ ...b0, st: 2, cand: cand.slice(0, i + 1), say: `${i ? 'Another' : 'One'} line that separates the classes. The empty street around it is only <b>${f2(r.g)}</b> wide. ${i ? 'Both lines get every training point right, so which one should we trust?' : 'It gets every training point right, but it passes close to some points.'}` }));
      const half = best.g / 2;
      const w = [best.ux / half, best.uy / half], b = -best.mid / half;
      const sv = P.filter(a => Math.abs(a.s * (w[0] * a.x + w[1] * a.y + b) - 1) < 1e-3);
      const base = { ...b0, best, w, b, sv };
      fr.push({ ...base, st: 3, say: `The SVM chooses the line with the <b>widest street</b>: width <b>${f2(best.g, 3)}</b>. A wide street means new points can land a little off from the training points and still be classified correctly.` });
      fr.push({ ...base, st: 4, say: `The ${sv.length} circled points touch the edges of the street. They are the <b>support vectors</b>. Move or delete any other point and the line does not change at all.` });
      fr.push({ ...base, st: 5, say: `Scale the line so that w·x + b = +1 and −1 on the two edges: <b>w = (${f2(w[0], 3)}, ${f2(w[1], 3)})</b>, <b>b = ${f2(b, 3)}</b>. Then the width is 2 ÷ |w| = 2 ÷ ${f2(Math.hypot(w[0], w[1]), 3)} = ${f2(2 / Math.hypot(w[0], w[1]), 3)}. Making the street wide is the same as making |w| small.` });
      fr.push({ ...base, st: 6, say: 'Every point has y(w·x + b) ≥ 1, and the support vectors have exactly 1. So training an SVM means: minimise ½|w|² subject to y(w·x + b) ≥ 1 for every point. With noisy data the soft margin version lets some points inside the street and pays a penalty C for each.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const xs = f.P.map(a => a.x), ys = f.P.map(a => a.y);
      let [xl, xh] = [Math.min(...xs), Math.max(...xs)], [yl, yh] = [Math.min(...ys), Math.max(...ys)];
      const s = Math.max((xh - xl + 2) / 354, (yh - yl + 2) / 280), cx = (xl + xh) / 2, cy = (yl + yh) / 2;
      const P = plot(z, [10, 10, 390, 310], [cx - 177 * s, cx + 177 * s], [cy - 140 * s, cy + 140 * s], { dx: 1, dy: 1 });
      const col = a => klass(z, a.s < 0 ? 0 : 1);
      (f.cand || []).forEach((r, i) => {
        if (f.st > 2) return;
        uline(z, P, r.ux, r.uy, r.mid, c.ink2, 1.6, [6, 4]);
        uline(z, P, r.ux, r.uy, r.mid - r.g / 2, c.line, 1, [2, 3]);
        uline(z, P, r.ux, r.uy, r.mid + r.g / 2, c.line, 1, [2, 3]);
      });
      if (f.st >= 3) {
        const r = f.best;
        g.save(); g.beginPath(); g.rect(P.x0, P.y0, P.w, P.h); g.clip();
        const k1 = r.mid - r.g / 2, k2 = r.mid + r.g / 2, L = 1e3;
        const px = -r.uy, py = r.ux;
        const pt = (k, t) => [P.X(r.ux * k + px * t), P.Y(r.uy * k + py * t)];
        g.beginPath();
        [[k1, -L], [k1, L], [k2, L], [k2, -L]].forEach(([k, t], i) => { const [X, Y] = pt(k, t); i ? g.lineTo(X, Y) : g.moveTo(X, Y); });
        g.closePath(); g.globalAlpha = 0.14; g.fillStyle = c.cv; g.fill();
        g.restore();
        uline(z, P, r.ux, r.uy, r.mid, c.ink, 2.4);
        uline(z, P, r.ux, r.uy, k1, klass(z, 0), 1.4, [6, 4]);
        uline(z, P, r.ux, r.uy, k2, klass(z, 1), 1.4, [6, 4]);
      }
      f.P.forEach(a => D.circle(g, P.X(a.x), P.Y(a.y), 6, { fill: col(a) }));
      if (f.st >= 4) f.sv.forEach(a => D.circle(g, P.X(a.x), P.Y(a.y), 11, { stroke: c.ink, w: 2 }));
      f.P.forEach(a => D.text(g, a.c, P.X(a.x) + 12, P.Y(a.y) - 10, { a: 'center', s: 10, b: true, c: c.ink2 }));
      if (f.st === 2) {
        head(z, 'Street width', 418, 24);
        f.cand.forEach((r, i) => D.text(g, `line ${i + 1}: ${f2(r.g)}`, 418, 50 + i * 22, { s: 12, mono: true, c: c.ink2 }));
      }
      if (f.st >= 3) {
        head(z, 'Widest street', 418, 24);
        D.text(g, `width ${f2(f.best.g, 3)}`, 418, 48, { s: 14, b: true, c: c.cv });
        if (f.st >= 4) D.text(g, `${f.sv.length} support vectors`, 418, 72, { s: 12, b: true, c: c.ink });
        if (f.st >= 5) {
          D.text(g, `w = (${f2(f.w[0], 2)}, ${f2(f.w[1], 2)})`, 418, 100, { s: 12, mono: true, c: c.ink });
          D.text(g, `b = ${f2(f.b, 2)}`, 418, 120, { s: 12, mono: true, c: c.ink });
          D.text(g, 'y(w·x + b) per point', 418, 146, { s: 11, b: true, c: c.ink2 });
          f.P.slice(0, 8).forEach((a, i) => {
            const m = a.s * (f.w[0] * a.x + f.w[1] * a.y + f.b);
            D.text(g, `(${a.x}, ${a.y})  ${f2(m, 2)}`, 418, 166 + i * 18, { s: 11, mono: true, b: Math.abs(m - 1) < 1e-3, c: Math.abs(m - 1) < 1e-3 ? c.ink : c.ink2 });
          });
        }
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 2.4  the kernel trick: add a feature x², then a straight cut works
   ===================================================================================================== */
(() => {
  const { trace, plot, nums, D, f2, head, klass } = MLZ;
  trace('mlkernel', {
    title: 'The kernel trick: lift the points, then cut straight',
    sub: 'Class A sits in the middle of the number line and class B on both sides, so no single cut point separates them. Adding the feature x² lifts the points onto a curve where a straight line does.',
    W: 600, H: 330,
    params: [
      { k: 'a', label: 'Class A values', type: 'text', v: '-1, -0.5, 0, 0.6, 1.1' },
      { k: 'b', label: 'Class B values', type: 'text', v: '-3, -2.4, -2, 2, 2.6, 3.2' }
    ],
    tips: [{ t: 'Put B only on the right (2, 2.6, 3.2): one cut point is already enough, no lifting needed.', set: { b: '2, 2.6, 3.2' }, play: true }],
    frames(p) {
      const A = nums(p.a).slice(0, 15), B = nums(p.b).slice(0, 15);
      if (!A.length || !B.length) throw new Error('Type some numbers for both classes');
      const all = A.map(x => ({ x, c: 0 })).concat(B.map(x => ({ x, c: 1 })));
      const xs = all.map(a => a.x).sort((u, v) => u - v);
      let bestErr = Infinity, bestCut = 0;
      for (let i = 0; i <= xs.length; i++) {
        const cut = i === 0 ? xs[0] - 1 : i === xs.length ? xs[xs.length - 1] + 1 : (xs[i - 1] + xs[i]) / 2;
        for (const left of [0, 1]) {
          const e = all.filter(a => (a.x < cut ? left : 1 - left) !== a.c).length;
          if (e < bestErr) { bestErr = e; bestCut = cut; }
        }
      }
      const hiA = Math.max(...A.map(x => x * x)), loB = Math.min(...B.map(x => x * x));
      const sep = hiA < loB, t = (hiA + loB) / 2, r = Math.sqrt(t);
      const b = { all, bestCut, bestErr, hiA, loB, sep, t, r };
      const fr = [
        { ...b, st: 1, say: `${A.length} points of class A and ${B.length} of class B on one number line (one feature x).` },
        { ...b, st: 2, say: bestErr === 0 ? `One cut at x = ${f2(bestCut)} already separates them, so a plain linear model works.` : `The best single cut point (x = ${f2(bestCut)}) still gets <b>${bestErr}</b> point${bestErr > 1 ? 's' : ''} wrong. A linear classifier on x alone cannot do better.` },
        { ...b, st: 3, say: 'Add a second feature, x². Every point moves up to the height x² on the curve. Points far from 0 rise a lot, points near 0 hardly move.' }
      ];
      if (!sep) { fr.push({ ...b, st: 3, say: 'Here even the lifted points overlap (some A point is further from 0 than some B point), so x² alone is not enough. An RBF kernel can still bend the boundary around each group.' }); return fr; }
      fr.push({ ...b, st: 4, say: `In the new space (x, x²) the straight line <b>x² = ${f2(t)}</b> separates the classes: every A point is below it and every B point above.` });
      fr.push({ ...b, st: 5, say: `Back on the original line that straight cut becomes <b>two</b> cut points, x = −${f2(r)} and x = +${f2(r)}. Between them is A, outside is B. A linear model in the lifted space is a curved model in the original space.` });
      fr.push({ ...b, st: 6, say: 'The trick: the SVM only needs dot products between points. For the feature x², φ(x)·φ(z) = x²z² = (xz)², so the kernel K(x, z) = (xz)² gives the lifted dot product without building the new feature. The RBF kernel exp(−γ(x − z)²) works like infinitely many such features.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const xs = f.all.map(a => a.x), lo = Math.min(...xs), hi = Math.max(...xs), pad = (hi - lo) * 0.1 + 0.3;
      const top = Math.max(...xs.map(x => x * x)) * 1.1 + 0.5;
      const lifted = f.st >= 3;
      const P = plot(z, [10, 10, 400, 310], [lo - pad, hi + pad], lifted ? [-top * 0.08, top] : [-1, 1], { dx: 1, dy: lifted ? 1 : 0, xl: 'x', yl: lifted ? 'x²' : '' });
      if (lifted) {
        g.save(); g.beginPath();
        for (let i = 0; i <= 120; i++) { const x = lo - pad + (hi - lo + 2 * pad) * i / 120; const X = P.X(x), Y = P.Y(Math.min(x * x, top)); i ? g.lineTo(X, Y) : g.moveTo(X, Y); }
        g.strokeStyle = c.line; g.lineWidth = 1.5; g.stroke(); g.restore();
      }
      const base = lifted ? 0 : 0;
      D.line(g, P.X(lo - pad), P.Y(base), P.X(hi + pad), P.Y(base), c.ink2, 1.2);
      if (f.st === 2 && f.bestErr > 0) D.line(g, P.X(f.bestCut), P.Y(lifted ? 0 : -0.8), P.X(f.bestCut), P.Y(lifted ? top : 0.8), c.red || '#dc2626', 1.6, [5, 4]);
      if (f.st >= 4 && f.sep) D.line(g, P.X(lo - pad), P.Y(f.t), P.X(hi + pad), P.Y(f.t), c.cv, 2.2);
      if (f.st >= 5 && f.sep) [-f.r, f.r].forEach(x => {
        D.line(g, P.X(x), P.Y(f.t), P.X(x), P.Y(0), c.cv, 1.4, [4, 3]);
        D.circle(g, P.X(x), P.Y(0), 4, { fill: c.cv });
      });
      f.all.forEach(a => {
        const y = lifted ? a.x * a.x : 0;
        if (lifted) D.line(g, P.X(a.x), P.Y(0), P.X(a.x), P.Y(y), c.line, 1, [2, 3]);
        D.circle(g, P.X(a.x), P.Y(y), 6, { fill: klass(z, a.c) });
      });
      head(z, 'Features', 425, 24);
      D.text(g, lifted ? 'x and x²' : 'x only', 425, 46, { s: 13, b: true, c: c.ink });
      D.text(g, 'A', 425, 76, { s: 12, b: true, c: klass(z, 0) }); D.text(g, 'B', 455, 76, { s: 12, b: true, c: klass(z, 1) });
      if (f.st >= 2) D.text(g, `best single cut: ${f.bestErr} wrong`, 425, 104, { s: 11, c: c.ink2 });
      if (f.st >= 4 && f.sep) D.text(g, `line x² = ${f2(f.t)}: 0 wrong`, 425, 126, { s: 11, b: true, c: c.cv });
      if (f.st >= 5 && f.sep) D.text(g, `cuts at ±${f2(f.r)}`, 425, 148, { s: 11, b: true, c: c.cv });
      if (f.st >= 6) D.text(g, 'K(x, z) = (x z)²', 425, 180, { s: 13, mono: true, b: true, c: c.ink });
    }
  });
})();
