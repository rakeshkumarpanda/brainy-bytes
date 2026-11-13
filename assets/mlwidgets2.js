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

/* =====================================================================================================
   Supervised 3.1  choosing a split: try every cut point and keep the lowest weighted Gini
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, klass, rr } = MLZ;
  const gini = L => { if (!L.length) return 0; const n = {}; L.forEach(c => { n[c] = (n[c] || 0) + 1; }); return 1 - Object.values(n).reduce((s, k) => s + (k / L.length) ** 2, 0); };
  trace('mlgini', {
    title: 'Decision tree split: try every cut, keep the purest',
    sub: 'Type values with a class (value class). A tree tries a cut between every pair of neighbouring values, measures how mixed each side is with the Gini impurity, and keeps the cut with the lowest weighted Gini.',
    W: 600, H: 330,
    params: [{ k: 'pts', label: 'Values (value class)', type: 'area', v: '1 no; 2 no; 3 no; 4 no; 5 yes; 6 no; 7 yes; 8 yes' }],
    tips: [
      { t: 'Perfectly separable values: the best cut gives Gini 0 on both sides.', set: { pts: '1 no; 2 no; 3 no; 6 yes; 7 yes; 8 yes' }, play: true },
      { t: 'Three classes: Gini works the same way, 1 minus the sum of squared shares.', set: { pts: '1 a; 2 a; 3 b; 4 b; 5 b; 6 c; 7 c; 8 a' }, play: true }
    ],
    frames(p) {
      const P = String(p.pts).split(/[\n;]+/).map(s => s.trim()).filter(Boolean).map(s => { const t = s.replace(/−/g, '-').split(/[\s,]+/); return { x: +t[0], c: t[1] || 'A' }; }).filter(a => !isNaN(a.x)).sort((a, b) => a.x - b.x).slice(0, 14);
      if (P.length < 2) throw new Error('Type at least two values with a class, for example 3 yes');
      const classes = [...new Set(P.map(a => a.c))].sort();
      const g0 = gini(P.map(a => a.c));
      const cuts = [];
      for (let i = 1; i < P.length; i++) {
        if (P[i].x === P[i - 1].x) continue;
        const cut = (P[i - 1].x + P[i].x) / 2, L = P.filter(a => a.x < cut).map(a => a.c), R = P.filter(a => a.x >= cut).map(a => a.c);
        cuts.push({ cut, nl: L.length, nr: R.length, gl: gini(L), gr: gini(R), w: (L.length * gini(L) + R.length * gini(R)) / P.length });
      }
      let best = 0; cuts.forEach((c, i) => { if (c.w < cuts[best].w - 1e-12) best = i; });
      const b = { P, classes, g0, cuts };
      const share = classes.map(c => `${c} ${P.filter(a => a.c === c).length}`).join(', ');
      const fr = [{ ...b, st: 1, say: `${P.length} examples (${share}). Before any split the Gini impurity is 1 − Σ(share)² = <b>${f2(g0, 3)}</b>. 0 would mean one class only.` }];
      cuts.forEach((c, i) => fr.push({ ...b, st: 2, upto: i, say: `Cut at ${f2(c.cut)}: left ${c.nl} example${c.nl === 1 ? "" : "s"} with Gini ${f2(c.gl, 3)}, right ${c.nr} with Gini ${f2(c.gr, 3)}. Weighted Gini = (${c.nl} × ${f2(c.gl, 3)} + ${c.nr} × ${f2(c.gr, 3)}) ÷ ${P.length} = <b>${f2(c.w, 3)}</b>.` }));
      fr.push({ ...b, st: 3, upto: cuts.length - 1, best, say: `The best cut is at <b>${f2(cuts[best].cut)}</b> with weighted Gini ${f2(cuts[best].w, 3)}, a drop of ${f2(g0 - cuts[best].w, 3)} from ${f2(g0, 3)}. The tree asks "value < ${f2(cuts[best].cut)}?" and then repeats the same search inside each side.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const xs = f.P.map(a => a.x), lo = Math.min(...xs), hi = Math.max(...xs), pad = (hi - lo) * 0.08 + 0.5;
      const P = plot(z, [10, 10, 580, 130], [lo - pad, hi + pad], [-1, 1], { dx: 1, dy: 0, grid: false });
      D.line(g, P.X(lo - pad), P.Y(0), P.X(hi + pad), P.Y(0), c.line, 1.2);
      const cur = f.st === 3 ? f.cuts[f.best] : f.st === 2 ? f.cuts[f.upto] : null;
      if (cur) D.line(g, P.X(cur.cut), P.Y(0.9), P.X(cur.cut), P.Y(-0.9), f.st === 3 ? c.cv : c.ink2, 2, f.st === 3 ? undefined : [5, 4]);
      f.P.forEach((a, i) => {
        const k = f.classes.indexOf(a.c), same = f.P.filter((q, j) => j < i && q.x === a.x).length;
        D.circle(g, P.X(a.x), P.Y(0) - same * 14, 7, { fill: klass(z, k) });
        D.text(g, a.c, P.X(a.x), P.Y(0) - 14 - same * 14, { a: 'center', s: 10, b: true, c: c.ink2 });
        D.text(g, f2(a.x, 1), P.X(a.x), P.Y(0) + 20, { a: 'center', s: 10, c: c.ink2 });
      });
      if (f.st >= 2) {
        head(z, 'Weighted Gini for each cut (lower is purer)', 16, 166);
        const n = f.cuts.length, bw = Math.min(56, 540 / n - 6), mx = Math.max(f.g0, ...f.cuts.map(t => t.w)) || 1;
        f.cuts.forEach((t, i) => {
          if (i > f.upto) return;
          const x = 30 + i * (540 / n), h = t.w / mx * 110;
          rr(g, x, 300 - h, bw, Math.max(2, h), 3, { fill: f.st === 3 && i === f.best ? c.cv : klass(z, 1) });
          D.text(g, f2(t.w, 3), x + bw / 2, 294 - h, { a: 'center', s: 10, b: true, c: c.ink });
          D.text(g, f2(t.cut, 1), x + bw / 2, 316, { a: 'center', s: 10, c: c.ink2 });
        });
        D.line(g, 24, 300 - f.g0 / mx * 110, 580, 300 - f.g0 / mx * 110, c.ink2, 1, [3, 3]);
        D.text(g, `before split ${f2(f.g0, 3)}`, 580, 296 - f.g0 / mx * 110, { a: 'right', s: 10, c: c.ink2 });
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 3.1  growing a tree: each split cuts one box in two, parallel to an axis
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rng, klass } = MLZ;
  function data(kind, seed) {
    const r = rng(seed), P = [];
    for (let i = 0; i < 70; i++) {
      const x = r() * 10, y = r() * 10;
      let c;
      if (kind === 'diag') c = y > x + (r() - 0.5) * 1.2 ? 1 : 0;
      else if (kind === 'ring') c = Math.hypot(x - 5, y - 5) < 3 + (r() - 0.5) * 0.8 ? 1 : 0;
      else c = (x > 4 && y > 5.5) || (x > 7.5) ? 1 : 0;
      if (r() < 0.04) c = 1 - c;
      P.push({ x, y, c });
    }
    return P;
  }
  const gini = (P, I) => { if (!I.length) return 0; const k = I.filter(i => P[i].c === 1).length / I.length; return 2 * k * (1 - k); };
  function bestSplit(P, I) {
    let best = null;
    ['x', 'y'].forEach(ax => {
      const v = [...new Set(I.map(i => P[i][ax]))].sort((a, b) => a - b);
      for (let j = 1; j < v.length; j++) {
        const t = (v[j - 1] + v[j]) / 2, L = I.filter(i => P[i][ax] <= t), R = I.filter(i => P[i][ax] > t);
        const w = (L.length * gini(P, L) + R.length * gini(P, R)) / I.length;
        if (!best || w < best.w - 1e-12) best = { ax, t, L, R, w };
      }
    });
    return best;
  }
  trace('mltreegrow', {
    title: 'Growing a decision tree, one split at a time',
    sub: 'Each step finds the best question "x ≤ t?" or "y ≤ t?" for one box and cuts it in two. Every box (leaf) predicts its majority class. Cuts are always parallel to an axis.',
    W: 600, H: 330,
    params: [
      { k: 'kind', label: 'Data', type: 'select', v: 'blocks', opts: [['blocks', 'Blocks (easy for trees)'], ['diag', 'Diagonal boundary'], ['ring', 'Ring']] },
      { k: 'depth', label: 'Maximum depth', type: 'range', v: 3, min: 1, max: 6, step: 1 }
    ],
    tips: [
      { t: 'The diagonal: a tree needs a staircase of many cuts for one slanted line.', set: { kind: 'diag', depth: 5 }, play: true },
      { t: 'Depth 6 on the blocks: the extra cuts chase the few noisy points (overfitting).', set: { kind: 'blocks', depth: 6 }, play: true }
    ],
    frames(p) {
      const P = data(p.kind, 7);
      const all = P.map((_, i) => i);
      const maj = I => (I.filter(i => P[i].c === 1).length * 2 > I.length ? 1 : 0);
      let leaves = [{ I: all, b: [0, 10, 0, 10], d: 0, m: maj(all) }];
      const cuts = [];
      const acc = () => leaves.reduce((s, l) => s + l.I.filter(i => P[i].c === l.m).length, 0) / P.length;
      const fr = [{ P, leaves: leaves.slice(), cuts: [], acc: acc(), say: `${P.length} training points, two classes. Before any question the tree is one leaf that predicts the majority class everywhere: training accuracy ${f2(acc() * 100, 1)}%.` }];
      let q = 0;
      while (q < leaves.length && cuts.length < 24) {
        const l = leaves[q];
        if (l.d >= p.depth || gini(P, l.I) === 0 || l.I.length < 2) { q++; continue; }
        const s = bestSplit(P, l.I);
        if (!s) { q++; continue; }
        const [x0, x1, y0, y1] = l.b;
        const A = { I: s.L, b: s.ax === 'x' ? [x0, s.t, y0, y1] : [x0, x1, y0, s.t], d: l.d + 1, m: maj(s.L) };
        const B = { I: s.R, b: s.ax === 'x' ? [s.t, x1, y0, y1] : [x0, x1, s.t, y1], d: l.d + 1, m: maj(s.R) };
        leaves.splice(q, 1, A, B);
        cuts.push({ ax: s.ax, t: s.t, b: l.b, d: l.d + 1 });
        fr.push({ P, leaves: leaves.slice(), cuts: cuts.slice(), acc: acc(), say: `Split ${cuts.length} (depth ${l.d + 1}): in a box with ${l.I.length} points, ask <b>${s.ax} ≤ ${f2(s.t)}</b>. Weighted Gini falls from ${f2(gini(P, l.I), 3)} to ${f2(s.w, 3)}. Training accuracy is now ${f2(acc() * 100, 1)}%.` });
        q = 0;
        leaves.sort((u, v) => u.d - v.d);
      }
      fr.push({ P, leaves, cuts, acc: acc(), done: true, say: `Finished: ${cuts.length} questions, ${leaves.length} leaves, training accuracy <b>${f2(acc() * 100, 1)}%</b>. ${p.kind === 'diag' ? 'A slanted boundary needs a staircase of axis parallel cuts. A linear model would need one line.' : 'Limit the depth (or prune) so the tree does not grow tiny boxes around single noisy points.'}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 310], [0, 10], [0, 10], { dx: 0, dy: 0 });
      g.save(); g.globalAlpha = 0.18;
      f.leaves.forEach(l => { g.fillStyle = klass(z, l.m); g.fillRect(P.X(l.b[0]), P.Y(l.b[3]), P.X(l.b[1]) - P.X(l.b[0]), P.Y(l.b[2]) - P.Y(l.b[3])); });
      g.restore();
      f.cuts.forEach((s, i) => {
        const last = i === f.cuts.length - 1 && !f.done;
        if (s.ax === 'x') D.line(g, P.X(s.t), P.Y(s.b[2]), P.X(s.t), P.Y(s.b[3]), last ? c.cv : c.ink, last ? 3 : 1.6);
        else D.line(g, P.X(s.b[0]), P.Y(s.t), P.X(s.b[1]), P.Y(s.t), last ? c.cv : c.ink, last ? 3 : 1.6);
      });
      f.P.forEach(a => D.circle(g, P.X(a.x), P.Y(a.y), 4, { fill: klass(z, a.c), stroke: c.surf, w: 1 }));
      head(z, 'The tree so far', 425, 24);
      D.text(g, `questions: ${f.cuts.length}`, 425, 48, { s: 12, mono: true, c: c.ink });
      D.text(g, `leaves: ${f.leaves.length}`, 425, 68, { s: 12, mono: true, c: c.ink });
      D.text(g, `train accuracy: ${f2(f.acc * 100, 1)}%`, 425, 88, { s: 12, mono: true, b: true, c: c.cv });
      f.cuts.slice(0, 10).forEach((s, i) => D.text(g, `${' '.repeat(2 * (s.d - 1))}${s.ax} ≤ ${f2(s.t, 1)}`, 425, 116 + i * 18, { s: 11, mono: true, c: i === f.cuts.length - 1 ? c.cv : c.ink2 }));
      if (f.cuts.length > 10) D.text(g, `… ${f.cuts.length - 10} more`, 425, 116 + 10 * 18, { s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Supervised 3.2  a bootstrap sample: draw rows with replacement, some repeat and some are left out
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, rng, rr, klass } = MLZ;
  trace('mlbootstrap', {
    title: 'Bootstrap sample: draw rows with replacement',
    sub: 'Each tree in a random forest trains on a bootstrap sample: as many rows as the data has, drawn at random with replacement. Some rows come up twice or more, others not at all (out of bag).',
    W: 600, H: 330,
    params: [
      { k: 'n', label: 'Rows in the data', type: 'range', v: 10, min: 5, max: 15, step: 1 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 3, min: 1, max: 30, step: 1 }
    ],
    tips: [{ t: 'Change the seed: a different tree gets a different sample, with different rows out of bag.', set: { seed: 11 }, play: true }],
    frames(p) {
      const r = rng(p.seed * 7 + 1), n = p.n, draws = [];
      for (let i = 0; i < n; i++) draws.push(1 + Math.floor(r() * n));
      const b = { n, draws };
      const fr = [{ ...b, upto: 0, say: `The training data has ${n} rows, numbered 1 to ${n}. We will draw ${n} times, and after each draw the row goes back in the bag.` }];
      draws.forEach((d, i) => {
        const before = draws.slice(0, i).filter(x => x === d).length;
        fr.push({ ...b, upto: i + 1, say: `Draw ${i + 1}: row <b>${d}</b>${before ? `, already drawn ${before === 1 ? 'once' : before + ' times'} before. Repeats are normal with replacement.` : '.'}` });
      });
      const uniq = new Set(draws).size, oob = [];
      for (let k = 1; k <= n; k++) if (!draws.includes(k)) oob.push(k);
      fr.push({ ...b, upto: n, done: true, uniq, oob, say: `The sample has ${uniq} different rows out of ${n} (${f2(100 * uniq / n, 0)}%). Rows ${oob.join(', ') || 'none'} were never drawn: they are <b>out of bag</b> for this tree and can test it for free. On average a bootstrap sample holds 1 − 1/e ≈ 63.2% of the rows.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const cnt = {};
      f.draws.slice(0, f.upto).forEach(d => { cnt[d] = (cnt[d] || 0) + 1; });
      head(z, 'Original rows (the bag)', 16, 24);
      const bw = Math.min(36, 560 / f.n - 4);
      for (let k = 1; k <= f.n; k++) {
        const x = 16 + (k - 1) * (bw + 4), used = cnt[k] || 0, oob = f.done && !used;
        rr(g, x, 36, bw, 34, 5, { fill: oob ? c.surf : used ? klass(z, 0) : c.bg, stroke: oob ? klass(z, 1) : c.line, w: oob ? 2 : 1 });
        D.text(g, String(k), x + bw / 2, 58, { a: 'center', s: 13, b: true, c: used ? '#fff' : c.ink });
        if (used > 1) D.text(g, `×${used}`, x + bw / 2, 86, { a: 'center', s: 11, b: true, c: c.ink });
        if (oob) D.text(g, 'OOB', x + bw / 2, 86, { a: 'center', s: 10, b: true, c: klass(z, 1) });
      }
      head(z, 'Bootstrap sample (in the order drawn)', 16, 124);
      f.draws.slice(0, f.upto).forEach((d, i) => {
        const x = 16 + i * (bw + 4), rep = f.draws.slice(0, i).includes(d);
        rr(g, x, 136, bw, 34, 5, { fill: rep ? klass(z, 1) : klass(z, 0) });
        D.text(g, String(d), x + bw / 2, 158, { a: 'center', s: 13, b: true, c: '#fff' });
      });
      if (f.done) {
        D.text(g, `different rows: ${f.uniq} of ${f.n}`, 16, 214, { s: 14, b: true, c: c.ink });
        D.text(g, `out of bag: ${f.oob.length ? f.oob.join(', ') : 'none'}`, 16, 240, { s: 14, b: true, c: klass(z, 1) });
        D.text(g, 'orange boxes in the sample are repeats', 16, 270, { s: 12, c: c.ink2 });
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 3.2  a random forest: many different trees, one majority vote
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rng, klass } = MLZ;
  function moons(n, noise, seed) {
    const r = rng(seed), g = () => { let s = 0; for (let i = 0; i < 6; i++) s += r(); return (s - 3) * Math.SQRT2; };
    const P = [];
    for (let i = 0; i < n; i++) {
      const t = Math.PI * r(), up = i % 2 === 0;
      P.push({ x: (up ? Math.cos(t) : 1 - Math.cos(t)) + noise * g(), y: (up ? Math.sin(t) : 0.5 - Math.sin(t)) + noise * g(), c: up ? 0 : 1 });
    }
    return P;
  }
  const gini = (P, I) => { if (!I.length) return 0; const k = I.filter(i => P[i].c === 1).length / I.length; return 2 * k * (1 - k); };
  function grow(P, I, d, r, maxd, randomFeature) {
    const ones = I.filter(i => P[i].c === 1).length;
    const leaf = { leaf: true, m: ones * 2 > I.length ? 1 : 0 };
    if (d >= maxd || I.length < 4 || ones === 0 || ones === I.length) return leaf;
    const axes = randomFeature ? [r() < 0.5 ? 'x' : 'y'] : ['x', 'y'];
    let best = null;
    axes.forEach(ax => {
      const v = [...new Set(I.map(i => P[i][ax]))].sort((a, b) => a - b);
      for (let j = 1; j < v.length; j++) {
        const t = (v[j - 1] + v[j]) / 2, L = I.filter(i => P[i][ax] <= t), R = I.filter(i => P[i][ax] > t);
        const w = L.length * gini(P, L) + R.length * gini(P, R);
        if (!best || w < best.w) best = { ax, t, L, R, w };
      }
    });
    if (!best) return leaf;
    return { ax: best.ax, t: best.t, l: grow(P, best.L, d + 1, r, maxd, randomFeature), r: grow(P, best.R, d + 1, r, maxd, randomFeature) };
  }
  const pred = (T, x, y) => { let n = T; while (!n.leaf) n = (n.ax === 'x' ? x : y) <= n.t ? n.l : n.r; return n.m; };
  trace('mlforestvote', {
    title: 'Random forest: many different trees vote',
    sub: 'Each tree trains on its own bootstrap sample and picks a random feature at every split, so the trees differ. Each one alone is jagged. Their majority vote is smoother and more accurate.',
    W: 600, H: 330,
    params: [
      { k: 'trees', label: 'Number of trees', type: 'range', v: 7, min: 1, max: 15, step: 2 },
      { k: 'depth', label: 'Depth of each tree', type: 'range', v: 6, min: 2, max: 10, step: 1 }
    ],
    tips: [
      { t: 'One tree only: the forest is just a single jagged tree.', set: { trees: 1 }, play: true },
      { t: 'Shallow trees (depth 2): each tree underfits, and voting cannot fix bias.', set: { depth: 2 }, play: true }
    ],
    frames(p) {
      const tr = moons(120, 0.3, 5), te = moons(300, 0.3, 77), r = rng(41);
      const forest = [], accs = [];
      const acc = f => te.filter(a => f(a.x, a.y) === a.c).length / te.length;
      const fr = [{ tr, say: '120 training points from two noisy moon shaped classes. We will grow several trees and let them vote.' }];
      for (let b = 0; b < p.trees; b++) {
        const I = tr.map(() => Math.floor(r() * tr.length));
        const T = grow(tr, I, 0, r, p.depth, true);
        forest.push(T);
        const a = acc((x, y) => pred(T, x, y));
        accs.push(a);
        fr.push({ tr, show: T, k: b + 1, accs: accs.slice(), say: `Tree ${b + 1}: trained on a bootstrap sample (${new Set(I).size} different rows), random feature at each split. Alone it scores <b>${f2(a * 100, 1)}%</b> on 300 test points. Its regions are boxy and full of mistakes.` });
      }
      const vote = (x, y) => (forest.reduce((s, T) => s + pred(T, x, y), 0) * 2 > forest.length ? 1 : 0);
      const fa = acc(vote), mean = accs.reduce((s, a) => s + a, 0) / accs.length;
      fr.push({ tr, forest, vote: true, accs, fa, say: `Now let all ${forest.length} trees vote. The forest scores <b>${f2(fa * 100, 1)}%</b>, while the single trees average ${f2(mean * 100, 1)}%. Their mistakes are in different places, so the vote cancels many of them.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 310], [-1.5, 2.5], [-1.2, 1.7], { dx: 1, dy: 1, grid: false });
      const fn = f.vote ? (x, y) => (f.forest.reduce((s, T) => s + pred(T, x, y), 0) * 2 > f.forest.length ? 1 : 0) : f.show ? (x, y) => pred(f.show, x, y) : null;
      if (fn) {
        const cell = 7;
        g.save(); g.globalAlpha = 0.22;
        for (let px = P.x0 + 26; px < P.x0 + P.w - 10; px += cell) for (let py = P.y0 + 10; py < P.y0 + P.h - 20; py += cell) {
          const x = -1.5 + (px + cell / 2 - P.x0 - 26) / (P.w - 36) * 4, y = -1.2 + (P.y0 + P.h - 20 - (py + cell / 2)) / (P.h - 30) * 2.9;
          g.fillStyle = klass(z, fn(x, y)); g.fillRect(px, py, cell, cell);
        }
        g.restore();
      }
      f.tr.forEach(a => D.circle(g, P.X(a.x), P.Y(a.y), 4, { fill: klass(z, a.c), stroke: c.surf, w: 1 }));
      if (f.accs) {
        head(z, 'Test accuracy', 425, 24);
        f.accs.slice(0, 10).forEach((a, i) => D.text(g, `tree ${String(i + 1).padStart(2)}  ${f2(a * 100, 1)}%`, 425, 48 + i * 19, { s: 11, mono: true, b: !f.vote && i === f.accs.length - 1, c: !f.vote && i === f.accs.length - 1 ? c.ink : c.ink2 }));
        if (f.accs.length > 10) D.text(g, `… ${f.accs.length - 10} more`, 425, 48 + 10 * 19, { s: 11, c: c.ink2 });
        if (f.vote) D.text(g, `forest  ${f2(f.fa * 100, 1)}%`, 425, 270, { s: 15, b: true, c: c.cv });
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 3.3  gradient boosting: each small tree fits what the model still gets wrong
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rng, klass } = MLZ;
  function stump(x, r) {
    let best = null;
    for (let i = 1; i < x.length; i++) {
      const t = (x[i - 1] + x[i]) / 2;
      let sl = 0, nl = 0, sr = 0, nr = 0;
      for (let j = 0; j < x.length; j++) { if (x[j] < t) { sl += r[j]; nl++; } else { sr += r[j]; nr++; } }
      const ml = sl / nl, mr = sr / nr;
      let e = 0; for (let j = 0; j < x.length; j++) e += (r[j] - (x[j] < t ? ml : mr)) ** 2;
      if (!best || e < best.e) best = { t, ml, mr, e };
    }
    return best;
  }
  trace('mlboostres', {
    title: 'Gradient boosting: fit the leftovers, step by step',
    sub: 'Start from the average. Each round fits a one question tree (a stump) to the residuals, what the model still gets wrong, and adds a small step of it. The fit improves round by round.',
    W: 600, H: 330,
    params: [
      { k: 'lr', label: 'Learning rate', type: 'range', v: 0.5, min: 0.1, max: 1, step: 0.1 },
      { k: 'rounds', label: 'Rounds', type: 'range', v: 8, min: 1, max: 20, step: 1 }
    ],
    tips: [
      { t: 'Learning rate 1: big steps, fast progress, but each tree’s noise is added at full size.', set: { lr: 1 }, play: true },
      { t: 'Learning rate 0.1: tiny careful steps, so many more rounds are needed.', set: { lr: 0.1, rounds: 20 }, play: true }
    ],
    frames(p) {
      const r = rng(11), n = 40, x = [], y = [];
      for (let i = 0; i < n; i++) x.push(6 * i / (n - 1) + 0.05 * (r() - 0.5));
      x.forEach(v => { let s = 0; for (let k = 0; k < 6; k++) s += r(); y.push(Math.sin(v) + 0.18 * (s - 3) * Math.SQRT2); });
      const mse = f => f.reduce((s, v, i) => s + (y[i] - v) ** 2, 0) / n;
      let F = Array(n).fill(y.reduce((s, v) => s + v, 0) / n);
      const hist = [mse(F)], stumps = [];
      const fr = [{ x, y, F: F.slice(), hist: hist.slice(), say: `Round 0: the model predicts the average, ${f2(F[0], 2)}, everywhere. Mean squared error ${f2(hist[0], 4)}.` }];
      for (let m = 1; m <= p.rounds; m++) {
        const res = y.map((v, i) => v - F[i]);
        const s = stump(x, res);
        fr.push({ x, y, F: F.slice(), res, s, hist: hist.slice(), m, say: `Round ${m}: the residuals y − F(x) (red) show what is still wrong. A stump fitted to them asks "x < ${f2(s.t)}?" and predicts ${f2(s.ml, 2)} on the left, ${f2(s.mr, 2)} on the right.` });
        F = F.map((v, i) => v + p.lr * (x[i] < s.t ? s.ml : s.mr));
        stumps.push(s); hist.push(mse(F));
        fr.push({ x, y, F: F.slice(), hist: hist.slice(), m, say: `Add ${p.lr} × that stump to the model. Mean squared error falls to <b>${f2(hist[m], 4)}</b>. The model is now the average plus ${m} small step${m > 1 ? 's' : ''}.` });
      }
      fr.push({ x, y, F, hist, done: true, say: `After ${p.rounds} rounds the error went from ${f2(hist[0], 4)} to <b>${f2(hist[p.rounds], 4)}</b>. Each stump alone is a crude two step function, but added up they follow the curve. With too many rounds the model starts to fit the noise, so real projects stop early using a validation set.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 310], [0, 6], [-1.8, 1.8], { dx: 0, dy: 1 });
      if (f.res) f.x.forEach((v, i) => D.line(g, P.X(v), P.Y(f.y[i]), P.X(v), P.Y(f.F[i]), c.red || '#dc2626', 1.4));
      f.x.forEach((v, i) => D.circle(g, P.X(v), P.Y(f.y[i]), 3.5, { fill: klass(z, 0) }));
      g.save(); g.beginPath();
      f.x.forEach((v, i) => { const X = P.X(v), Y = P.Y(f.F[i]); if (!i) g.moveTo(X, Y); else { g.lineTo(X, P.Y(f.F[i - 1])); g.lineTo(X, Y); } });
      g.strokeStyle = klass(z, 1); g.lineWidth = 2.6; g.stroke(); g.restore();
      if (f.s) {
        D.line(g, P.X(f.s.t), P.Y(-1.8), P.X(f.s.t), P.Y(1.8), c.cv, 1.4, [5, 4]);
        D.text(g, `x < ${f2(f.s.t, 2)}?`, P.X(f.s.t) + 4, P.Y(1.6), { s: 11, b: true, c: c.cv });
      }
      head(z, 'Error by round', 425, 24);
      const mx = f.hist[0] || 1;
      f.hist.slice(0, 21).forEach((h, i) => {
        const bw = 150 / Math.max(f.hist.length, 8);
        g.fillStyle = i === f.hist.length - 1 ? klass(z, 1) : c.line;
        g.fillRect(430 + i * bw, 200 - h / mx * 150, Math.max(2, bw - 2), h / mx * 150);
      });
      D.line(g, 428, 200, 590, 200, c.ink2, 1);
      D.text(g, `MSE ${f2(f.hist[f.hist.length - 1], 4)}`, 425, 226, { s: 13, b: true, c: klass(z, 1) });
      D.text(g, 'orange line: the model F(x)', 425, 254, { s: 11, c: c.ink2 });
      D.text(g, 'blue dots: the data', 425, 272, { s: 11, c: c.ink2 });
      if (f.res) D.text(g, 'red: residuals y − F(x)', 425, 290, { s: 11, c: c.red || '#dc2626' });
    }
  });
})();

/* =====================================================================================================
   Supervised 3.3  AdaBoost: wrong points get heavier, the next stump focuses on them
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, klass } = MLZ;
  trace('mladaboost', {
    title: 'AdaBoost: make the hard points heavier',
    sub: 'Eight points on a line, labelled + or −. Each round picks the stump (one cut) with the lowest weighted error, gives it a say α, and then makes the points it got wrong heavier so the next stump pays attention to them.',
    W: 600, H: 330,
    params: [
      { k: 'labels', label: 'Labels for x = 1 to 8', type: 'text', v: '+ + - - + + - -' },
      { k: 'rounds', label: 'Rounds', type: 'range', v: 3, min: 1, max: 6, step: 1 }
    ],
    tips: [{ t: 'Labels a single cut can split: one stump is enough and its error is 0, so we stop.', set: { labels: '+ + + + - - - -' }, play: true }],
    frames(p) {
      const y = String(p.labels).replace(/−/g, '-').split(/[\s,]+/).filter(Boolean).slice(0, 8).map(s => (s[0] === '-' ? -1 : 1));
      while (y.length < 8) y.push(1);
      const x = [1, 2, 3, 4, 5, 6, 7, 8];
      let w = Array(8).fill(1 / 8);
      const st = [];
      const fr = [{ x, y, w: w.slice(), st: [], say: 'Every point starts with the same weight, 1/8 = 0.125 (dot size shows weight).' }];
      for (let m = 1; m <= p.rounds; m++) {
        let best = null;
        [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5].forEach(cut => [1, -1].forEach(sg => {
          const pr = x.map(v => (v < cut ? sg : -sg));
          const e = pr.reduce((s, q, i) => s + (q !== y[i] ? w[i] : 0), 0);
          if (!best || e < best.e - 1e-12) best = { cut, sg, pr, e };
        }));
        if (best.e < 1e-9) { st.push({ ...best, a: Infinity }); fr.push({ x, y, w: w.slice(), st: st.slice(), say: `Round ${m}: the stump x &lt; ${best.cut} gets every point right (error 0). It decides alone, so boosting stops here.` }); break; }
        const a = 0.5 * Math.log((1 - best.e) / best.e);
        st.push({ ...best, a });
        fr.push({ x, y, w: w.slice(), st: st.slice(), cur: best, say: `Round ${m}: best stump "x &lt; ${best.cut} → ${best.sg > 0 ? '+' : '−'}, else ${best.sg > 0 ? '−' : '+'}". Weighted error ε = ${f2(best.e, 3)}. Its say α = ½ ln((1 − ε)/ε) = <b>${f2(a, 3)}</b>.` });
        w = w.map((v, i) => v * Math.exp(-a * y[i] * best.pr[i]));
        const s = w.reduce((u, v) => u + v, 0); w = w.map(v => v / s);
        const wrong = x.filter((_, i) => best.pr[i] !== y[i]);
        fr.push({ x, y, w: w.slice(), st: st.slice(), cur: best, say: `Reweight: multiply wrong points by e<sup>α</sup> and right points by e<sup>−α</sup>, then rescale to sum 1. Points x = ${wrong.join(', ')} were wrong and now weigh ${f2(w[x.indexOf(wrong[0])], 3)} each.` });
      }
      const score = x.map((_, i) => st.reduce((s, t) => s + (isFinite(t.a) ? t.a : 1e3) * t.pr[i], 0));
      const ok = score.filter((s, i) => Math.sign(s) === y[i]).length;
      fr.push({ x, y, w, st, score, say: `Final model: add up α × prediction of every stump and take the sign. ${ok} of 8 points are right. ${ok === 8 && st.length > 1 ? 'No single stump could do that, but the weighted vote of several can.' : ''}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 580, 150], [0.5, 8.5], [-1, 1], { dx: 0, dy: 0, grid: false });
      D.line(g, P.X(0.5), P.Y(0), P.X(8.5), P.Y(0), c.line, 1.2);
      if (f.cur) {
        D.line(g, P.X(f.cur.cut), P.Y(0.95), P.X(f.cur.cut), P.Y(-0.95), c.cv, 2);
        D.text(g, f.cur.sg > 0 ? '+ side' : '− side', P.X(f.cur.cut) - 6, P.Y(0.8), { a: 'right', s: 11, b: true, c: c.cv });
      }
      f.x.forEach((v, i) => {
        const r = 4 + Math.sqrt(f.w[i] / 0.125) * 7, wrong = f.cur && f.cur.pr[i] !== f.y[i];
        D.circle(g, P.X(v), P.Y(0), r, { fill: klass(z, f.y[i] > 0 ? 0 : 1), stroke: wrong ? c.ink : undefined, w: 2.5 });
        D.text(g, f.y[i] > 0 ? '+' : '−', P.X(v), P.Y(0) + 5, { a: 'center', s: 14, b: true, c: '#fff' });
        D.text(g, f2(f.w[i], 3), P.X(v), P.Y(0) + 40, { a: 'center', s: 10, mono: true, c: c.ink2 });
      });
      head(z, 'Stumps so far', 16, 186);
      f.st.forEach((t, i) => D.text(g, `${i + 1}. x < ${t.cut} → ${t.sg > 0 ? '+' : '−'}   ε = ${f2(t.e, 3)}   α = ${isFinite(t.a) ? f2(t.a, 3) : '∞'}`, 16, 210 + i * 18, { s: 12, mono: true, c: c.ink }));
      if (f.score) {
        head(z, 'Final score Σ α × prediction', 330, 186);
        f.score.forEach((s, i) => D.text(g, `x=${i + 1}: ${f2(Math.max(-99, Math.min(99, s)), 2)} → ${s > 0 ? '+' : '−'}`, 330 + (i % 2) * 130, 210 + Math.floor(i / 2) * 18, { s: 11, mono: true, b: Math.sign(s) === f.y[i], c: Math.sign(s) === f.y[i] ? c.ink : (c.red || '#dc2626') }));
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 4.1  the confusion matrix at a threshold, and the ROC curve from sweeping it
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, klass, rr, box } = MLZ;
  const DEF = '0.95 1; 0.9 1; 0.8 0; 0.75 1; 0.7 1; 0.6 0; 0.55 1; 0.4 0; 0.35 1; 0.3 0; 0.2 0; 0.1 0';
  function parse(s) {
    const P = String(s).split(/[\n;]+/).map(t => t.trim()).filter(Boolean).map(t => { const q = t.split(/[\s,]+/); return { s: +q[0], y: +q[1] === 1 ? 1 : 0 }; }).filter(a => !isNaN(a.s)).slice(0, 20);
    if (P.length < 2 || !P.some(a => a.y) || P.every(a => a.y)) throw new Error('Type scores with labels 1 and 0, for example 0.8 1; 0.3 0');
    return P;
  }
  function counts(P, t) {
    const c = { tp: 0, fp: 0, fn: 0, tn: 0 };
    P.forEach(a => { const p = a.s >= t; if (p && a.y) c.tp++; else if (p) c.fp++; else if (a.y) c.fn++; else c.tn++; });
    return c;
  }
  function scoreLine(z, f, t, y0) {
    const c = z.col, g = z.g;
    const X = v => 30 + v * 540;
    D.line(g, X(0), y0, X(1), y0, c.line, 1.2);
    [0, 0.25, 0.5, 0.75, 1].forEach(v => D.text(g, f2(v, 2), X(v), y0 + 30, { a: 'center', s: 10, c: c.ink2 }));
    D.text(g, 'model score →', X(1), y0 + 46, { a: 'right', s: 10, c: c.ink2 });
    if (t !== undefined) { D.line(g, X(t), y0 - 40, X(t), y0 + 18, c.cv, 2.2); D.text(g, `threshold ${f2(t, 2)}`, X(t) + 4, y0 - 30, { s: 11, b: true, c: c.cv }); }
    const seen = {};
    f.P.forEach(a => {
      const k = Math.round(a.s * 100); seen[k] = (seen[k] || 0) + 1;
      const yy = y0 - (seen[k] - 1) * 16;
      D.circle(g, X(a.s), yy, 7, { fill: klass(z, a.y ? 1 : 0), stroke: f.hl && f.hl(a) ? c.ink : undefined, w: 2.5 });
      D.text(g, a.y ? '1' : '0', X(a.s), yy + 4, { a: 'center', s: 9, b: true, c: '#fff' });
    });
  }
  trace('mlconfusion', {
    title: 'Confusion matrix: what a threshold turns into',
    sub: 'Each dot is a test example placed at its model score (orange = really positive, blue = really negative). Everything at or above the threshold is predicted positive. Count the four kinds of outcome, then compute precision and recall.',
    W: 600, H: 330,
    params: [
      { k: 'pts', label: 'Scores and true labels (score label)', type: 'area', v: DEF },
      { k: 't', label: 'Threshold', type: 'range', v: 0.5, min: 0.05, max: 0.95, step: 0.05 }
    ],
    tips: [
      { t: 'Threshold 0.25: almost every positive is caught (high recall), but more false alarms (lower precision).', set: { t: 0.25 }, play: true },
      { t: 'Threshold 0.85: few false alarms (high precision), but many positives are missed.', set: { t: 0.85 }, play: true }
    ],
    frames(p) {
      const P = parse(p.pts), t = p.t, c = counts(P, t);
      const prec = c.tp + c.fp ? c.tp / (c.tp + c.fp) : 0, rec = c.tp / (c.tp + c.fn), f1 = prec + rec ? 2 * prec * rec / (prec + rec) : 0;
      const b = { P, t, c, prec, rec, f1 };
      return [
        { ...b, st: 1, say: `${P.length} test examples, ${P.filter(a => a.y).length} really positive (orange) and ${P.filter(a => !a.y).length} really negative (blue), placed at the score the model gave them.` },
        { ...b, st: 2, say: `Draw the threshold at ${f2(t, 2)}. The model says <b>positive</b> for every dot at or to the right of the line, negative for the rest.` },
        { ...b, st: 3, hl: a => a.s >= t && a.y, say: `<b>True positives (TP) = ${c.tp}</b>: really positive and predicted positive.` },
        { ...b, st: 4, hl: a => a.s >= t && !a.y, say: `<b>False positives (FP) = ${c.fp}</b>: really negative but predicted positive, false alarms.` },
        { ...b, st: 5, hl: a => a.s < t && a.y, say: `<b>False negatives (FN) = ${c.fn}</b>: really positive but predicted negative, misses.` },
        { ...b, st: 6, hl: a => a.s < t && !a.y, say: `<b>True negatives (TN) = ${c.tn}</b>: really negative and predicted negative. Accuracy = (TP + TN) ÷ all = ${c.tp + c.tn} ÷ ${P.length} = ${f2((c.tp + c.tn) / P.length, 3)}.` },
        { ...b, st: 7, say: `<b>Precision</b> = TP ÷ (TP + FP) = ${c.tp} ÷ ${c.tp + c.fp} = ${f2(prec, 3)}: how many alarms are real. <b>Recall</b> = TP ÷ (TP + FN) = ${c.tp} ÷ ${c.tp + c.fn} = ${f2(rec, 3)}: how many positives we caught. <b>F1</b> = ${f2(f1, 3)}. Move the threshold to trade one against the other.` }
      ];
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      scoreLine(z, f, f.st >= 2 ? f.t : undefined, 90);
      if (f.st >= 3) {
        head(z, 'Confusion matrix', 30, 160);
        D.text(g, 'predicted 1', 175, 178, { a: 'center', s: 11, b: true, c: c.ink2 });
        D.text(g, 'predicted 0', 275, 178, { a: 'center', s: 11, b: true, c: c.ink2 });
        D.text(g, 'actual 1', 115, 210, { a: 'right', s: 11, b: true, c: c.ink2 });
        D.text(g, 'actual 0', 115, 260, { a: 'right', s: 11, b: true, c: c.ink2 });
        const cell = (x, y, label, v, on, col) => box(z, x, y, 96, 44, on ? `${label} ${v}` : label, { fill: on ? col : c.surf, c: on ? '#fff' : c.ink2, s: 13, b: true, r: 6 });
        cell(127, 188, 'TP', f.c.tp, f.st >= 3, c.green || '#16a34a');
        cell(227, 238, 'TN', f.c.tn, f.st >= 6, c.green || '#16a34a');
        cell(127, 238, 'FP', f.c.fp, f.st >= 4, c.red || '#dc2626');
        cell(227, 188, 'FN', f.c.fn, f.st >= 5, c.red || '#dc2626');
      }
      if (f.st >= 7) {
        head(z, 'Scores', 370, 160);
        [['precision', f.prec], ['recall', f.rec], ['F1', f.f1]].forEach(([n, v], i) => {
          D.text(g, n, 370, 196 + i * 32, { s: 12, b: true, c: c.ink });
          rr(g, 450, 184 + i * 32, Math.max(2, v * 100), 16, 3, { fill: c.cv });
          D.text(g, f2(v, 3), 556, 197 + i * 32, { s: 12, mono: true, b: true, c: c.ink });
        });
      }
    }
  });
  trace('mlroc', {
    title: 'ROC curve: sweep the threshold from high to low',
    sub: 'Start with a threshold above every score (nothing predicted positive) and lower it past one example at a time. Each step adds a point (false positive rate, true positive rate). The area under the curve is the AUC.',
    W: 600, H: 330,
    params: [{ k: 'pts', label: 'Scores and true labels (score label)', type: 'area', v: DEF }],
    tips: [
      { t: 'A perfect model: every positive scores above every negative, so the curve hugs the top left corner and AUC = 1.', set: { pts: '0.9 1; 0.8 1; 0.7 1; 0.4 0; 0.3 0; 0.2 0' }, play: true },
      { t: 'A useless model: labels mixed evenly along the scores, so the curve follows the diagonal, AUC about 0.5.', set: { pts: '0.9 1; 0.8 0; 0.7 1; 0.6 0; 0.5 1; 0.4 0; 0.3 1; 0.2 0' }, play: true }
    ],
    frames(p) {
      const P = parse(p.pts).sort((a, b) => b.s - a.s);
      const npos = P.filter(a => a.y).length, nneg = P.length - npos;
      let tp = 0, fp = 0;
      const pts = [[0, 0]];
      const fr = [{ P, pts: pts.slice(), say: `${npos} positives and ${nneg} negatives, sorted by score. Threshold above every score: nothing is predicted positive, so TPR = 0 and FPR = 0.` }];
      let area = 0;
      P.forEach((a, i) => {
        if (a.y) tp++; else fp++;
        const prev = pts[pts.length - 1], cur = [fp / nneg, tp / npos];
        area += (cur[0] - prev[0]) * (cur[1] + prev[1]) / 2;
        pts.push(cur);
        fr.push({ P, pts: pts.slice(), upto: i + 1, say: `Lower the threshold to ${f2(a.s, 2)}: this example is really <b>${a.y ? 'positive, so TPR goes up' : 'negative, so FPR goes right'}</b>. Now TPR = ${tp}/${npos} = ${f2(tp / npos, 2)} and FPR = ${fp}/${nneg} = ${f2(fp / nneg, 2)}.` });
      });
      fr.push({ P, pts, upto: P.length, area, done: true, say: `The threshold is below every score, so everything is positive: (1, 1). The area under the curve is <b>AUC = ${f2(area, 3)}</b>. It equals the chance that a random positive scores higher than a random negative. 0.5 is guessing, 1 is perfect.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const Pl = plot(z, [10, 10, 330, 310], [0, 1], [0, 1], { dx: 2, dy: 2, xl: 'FPR', yl: 'TPR' });
      D.line(g, Pl.X(0), Pl.Y(0), Pl.X(1), Pl.Y(1), c.line, 1, [4, 4]);
      if (f.done) {
        g.save(); g.beginPath(); g.moveTo(Pl.X(0), Pl.Y(0));
        f.pts.forEach(q => g.lineTo(Pl.X(q[0]), Pl.Y(q[1])));
        g.lineTo(Pl.X(1), Pl.Y(0)); g.closePath(); g.globalAlpha = 0.16; g.fillStyle = c.cv; g.fill(); g.restore();
      }
      g.save(); g.beginPath();
      f.pts.forEach((q, i) => (i ? g.lineTo(Pl.X(q[0]), Pl.Y(q[1])) : g.moveTo(Pl.X(q[0]), Pl.Y(q[1]))));
      g.strokeStyle = c.cv; g.lineWidth = 2.6; g.stroke(); g.restore();
      f.pts.forEach(q => D.circle(g, Pl.X(q[0]), Pl.Y(q[1]), 3.5, { fill: c.cv }));
      head(z, 'Sorted by score', 360, 24);
      f.P.slice(0, 14).forEach((a, i) => {
        const done = i < (f.upto || 0);
        D.circle(g, 370, 46 + i * 19, 6, { fill: klass(z, a.y ? 1 : 0) });
        D.text(g, `${f2(a.s, 2)}  ${a.y ? 'positive' : 'negative'}`, 384, 50 + i * 19, { s: 11, mono: true, b: done, c: done ? c.ink : c.ink2 });
      });
      if (f.done) D.text(g, `AUC ${f2(f.area, 3)}`, 500, 300, { s: 15, b: true, c: c.cv });
    }
  });
})();

/* =====================================================================================================
   Supervised 4.2  cross validation splits: plain, stratified, grouped and time ordered
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, rr, klass, box } = MLZ;
  const N = 20;
  const label = i => (i >= 16 ? 1 : 0);
  const patient = i => i % 5;
  function folds(mode) {
    const F = [];
    const all = [...Array(N).keys()];
    if (mode === 'kfold') for (let k = 0; k < 5; k++) { const v = all.slice(k * 4, k * 4 + 4); F.push({ val: v, train: all.filter(i => !v.includes(i)) }); }
    if (mode === 'strat') {
      const neg = all.filter(i => !label(i)), pos = all.filter(i => label(i));
      for (let k = 0; k < 5; k++) { const v = neg.slice(k * 3.2 | 0, (k + 1) * 3.2 | 0).concat(pos[k] !== undefined ? [pos[k]] : []); F.push({ val: v, train: all.filter(i => !v.includes(i)) }); }
    }
    if (mode === 'group') for (let k = 0; k < 5; k++) { const v = all.filter(i => patient(i) === k); F.push({ val: v, train: all.filter(i => !v.includes(i)) }); }
    if (mode === 'time') for (let k = 1; k <= 4; k++) F.push({ train: all.slice(0, 4 * k), val: all.slice(4 * k, 4 * k + 4) });
    return F;
  }
  const NAMES = { kfold: 'KFold (no shuffle)', strat: 'StratifiedKFold', group: 'GroupKFold', time: 'TimeSeriesSplit' };
  trace('mlkfold', {
    title: 'Cross validation: every row gets a turn in validation',
    sub: 'Twenty rows in their stored order (4 positives at the end, rows of 5 patients mixed together). Each step shows one split: blue rows train the model, the purple rows score it. Change the splitter to see how each one chooses its folds.',
    W: 600, H: 330,
    params: [{ k: 'mode', label: 'Splitter', type: 'select', v: 'kfold', opts: [['kfold', 'KFold without shuffling'], ['strat', 'StratifiedKFold'], ['group', 'GroupKFold (by patient)'], ['time', 'TimeSeriesSplit']] }],
    tips: [
      { t: 'StratifiedKFold: every validation fold gets one of the 4 positives.', set: { mode: 'strat' }, play: true },
      { t: 'TimeSeriesSplit: always train on the past and validate on the next block, never the other way round.', set: { mode: 'time' }, play: true }
    ],
    frames(p) {
      const F = folds(p.mode);
      const fr = [{ F, mode: p.mode, say: `${N} rows. Rows 17 to 20 are the positives (orange). The letter under each row is its patient (A to E). The splitter is <b>${NAMES[p.mode]}</b>.` }];
      F.forEach((f, k) => {
        const pos = f.val.filter(label).length, pats = [...new Set(f.val.map(patient))].length;
        let extra = '';
        if (p.mode === 'kfold') extra = pos === 0 ? ' This validation fold has <b>no positives</b>, so recall cannot even be measured here.' : pos === 4 ? ' All 4 positives sit in this fold and none are left for training.' : '';
        if (p.mode === 'strat') extra = ` It holds ${pos} positive, the same share as the whole data.`;
        if (p.mode === 'group') extra = ` Every row of patient ${'ABCDE'[k]} is here and none in training, so the model is scored on a person it has never seen.`;
        if (p.mode === 'time') extra = ` Train on rows 1 to ${f.train.length}, validate on the next ${f.val.length}. The future is never used to predict the past.`;
        fr.push({ F, mode: p.mode, k, say: `Split ${k + 1} of ${F.length}: ${f.train.length} rows train the model and ${f.val.length} score it (${pats} patient${pats > 1 ? 's' : ''} in validation).${extra}` });
      });
      const msg = {
        kfold: 'Without shuffling, sorted data gives lopsided folds. Shuffle (KFold(shuffle=True)) or, for classification, use StratifiedKFold.',
        strat: 'Stratified folds keep the class balance in every fold, so every score is measured on comparable data. It is the default for classifiers in cross_val_score.',
        group: 'Grouped folds stop the model from recognising a patient it already saw. Use GroupKFold whenever rows from the same person, device or session can appear more than once.',
        time: 'Time ordered splits mimic deployment: the model only ever knows the past. Shuffled folds on time series give scores that are too optimistic.'
      };
      fr.push({ F, mode: p.mode, done: true, say: `Every row was used for validation ${p.mode === 'time' ? 'at most' : 'exactly'} once. The cross validation score is the mean of the ${F.length} fold scores. ${msg[p.mode]}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, NAMES[f.mode], 16, 24);
      const cw = 26, x0 = 30;
      for (let i = 0; i < N; i++) {
        D.text(g, String(i + 1), x0 + i * cw + 11, 46, { a: 'center', s: 9, c: c.ink2 });
        D.circle(g, x0 + i * cw + 11, 60, 6, { fill: klass(z, label(i) ? 1 : 0) });
        D.text(g, 'ABCDE'[patient(i)], x0 + i * cw + 11, 82, { a: 'center', s: 10, b: true, c: c.ink2 });
      }
      f.F.forEach((s, k) => {
        const y = 100 + k * 34, active = f.k === k || f.done;
        D.text(g, `${k + 1}`, 16, y + 17, { s: 11, b: true, c: active ? c.ink : c.ink2 });
        for (let i = 0; i < N; i++) {
          const inV = s.val.includes(i), inT = s.train.includes(i);
          const fill = !active ? c.bg : inV ? c.cv : inT ? klass(z, 0) : c.surf;
          rr(g, x0 + i * cw, y, cw - 3, 24, 4, { fill, stroke: c.line, w: 0.6 });
        }
      });
      if (f.k !== undefined || f.done) {
        rr(g, 30, 290, 14, 14, 3, { fill: klass(z, 0) }); D.text(g, 'train', 50, 302, { s: 11, c: c.ink2 });
        rr(g, 100, 290, 14, 14, 3, { fill: c.cv }); D.text(g, 'validation', 120, 302, { s: 11, c: c.ink2 });
        rr(g, 200, 290, 14, 14, 3, { fill: c.surf, stroke: c.line }); D.text(g, 'not used', 220, 302, { s: 11, c: c.ink2 });
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 4.2  learning curves: does more data help? (polynomial regression of growing degree)
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rng, klass } = MLZ;
  function fit(xs, ys, d) {
    const m = d + 1, A = Array.from({ length: m }, () => Array(m + 1).fill(0));
    xs.forEach((x, n) => { const pw = [1]; for (let j = 1; j < m; j++) pw.push(pw[j - 1] * x); for (let i = 0; i < m; i++) { for (let j = 0; j < m; j++) A[i][j] += pw[i] * pw[j]; A[i][m] += pw[i] * ys[n]; } });
    for (let i = 0; i < m; i++) A[i][i] += 1e-6;
    for (let i = 0; i < m; i++) {
      let piv = i; for (let r = i + 1; r < m; r++) if (Math.abs(A[r][i]) > Math.abs(A[piv][i])) piv = r;
      [A[i], A[piv]] = [A[piv], A[i]];
      for (let r = 0; r < m; r++) if (r !== i) { const q = A[r][i] / A[i][i]; for (let cc = i; cc <= m; cc++) A[r][cc] -= q * A[i][cc]; }
    }
    const w = A.map((row, i) => row[m] / row[i]);
    return x => { let s = 0, pw = 1; for (let j = 0; j < m; j++) { s += w[j] * pw; pw *= x; } return s; };
  }
  function sample(n, seed) {
    const r = rng(seed), P = [];
    for (let i = 0; i < n; i++) { const x = 2 * r() - 1; let s = 0; for (let k = 0; k < 6; k++) s += r(); P.push({ x, y: Math.sin(Math.PI * x) + 0.3 * (s - 3) * Math.SQRT2 }); }
    return P;
  }
  trace('mllearncurve', {
    title: 'Learning curve: train and validation error as data grows',
    sub: 'Fit a polynomial of the chosen degree to more and more training points and measure the error on the training points and on 200 fresh validation points. The shape of the two curves says whether more data or a different model will help.',
    W: 600, H: 330,
    params: [{ k: 'deg', label: 'Polynomial degree (model complexity)', type: 'range', v: 1, min: 1, max: 9, step: 1 }],
    tips: [
      { t: 'Degree 3: both curves meet low, near the noise level. A good fit.', set: { deg: 3 }, play: true },
      { t: 'Degree 9: with 8 or 12 points the validation error is huge (high variance), then the gap closes as data grows.', set: { deg: 9 }, play: true }
    ],
    frames(p) {
      const pool = sample(80, 5), val = sample(200, 901);
      const mse = (f, S) => S.reduce((s, q) => s + (q.y - f(q.x)) ** 2, 0) / S.length;
      const res = [];
      const fr = [{ res: [], say: `We fit a degree ${p.deg} polynomial. The noise in the data has variance 0.09, so no model can get a validation error much below about 0.09.` }];
      [8, 12, 16, 24, 32, 48, 64, 80].forEach(n => {
        const S = pool.slice(0, n), f = fit(S.map(q => q.x), S.map(q => q.y), p.deg);
        const t = mse(f, S), v = mse(f, val);
        res.push({ n, t, v });
        fr.push({ res: res.slice(), f, S, say: `${n} training points: training error ${f2(t, 3)}, validation error <b>${f2(v, 3)}</b>${t < 0.02 && v > 0.5 ? '. The curve passes almost exactly through the training points but swings wildly between them.' : '.'}` });
      });
      const last = res[res.length - 1], gap = last.v - last.t;
      const diag = last.v > 0.2 && gap < 0.08 ? `<b>High bias</b>: both errors are high and close together (${f2(last.t, 3)} and ${f2(last.v, 3)}). More data will not help. Use a more flexible model.`
        : gap > 0.04 ? `<b>Some variance left</b>: validation error ${f2(last.v, 3)} is still above training error ${f2(last.t, 3)}. More data or regularisation would help.`
        : res[0].v - res[0].t > 0.3 ? `<b>High variance with little data</b>: at 8 points the gap was ${res[0].v - res[0].t > 10 ? 'over 10' : f2(res[0].v - res[0].t, 2)}, by 80 points it has closed to ${f2(gap, 3)}. For this flexible model, more data was the cure.`
        : `<b>A good fit</b>: both errors end close to the noise level (${f2(last.t, 3)} and ${f2(last.v, 3)}).`;
      fr.push({ res, f: fr[fr.length - 1].f, S: pool, done: true, say: diag });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const top = Math.min(1.2, Math.max(0.3, ...f.res.map(r => Math.min(r.v, 1.2)), 0.3));
      const P = plot(z, [10, 10, 300, 310], [0, 80], [0, top], { dx: 0, dy: 2, xl: 'training points', yl: 'error' });
      D.line(g, P.X(0), P.Y(0.09), P.X(80), P.Y(0.09), c.line, 1, [4, 4]);
      D.text(g, 'noise 0.09', P.X(78), P.Y(0.09) - 4, { a: 'right', s: 9, c: c.ink2 });
      [['t', klass(z, 0), 'train'], ['v', klass(z, 1), 'validation']].forEach(([k, col, name], j) => {
        g.save(); g.beginPath();
        f.res.forEach((r, i) => { const X = P.X(r.n), Y = P.Y(Math.min(r[k], top)); i ? g.lineTo(X, Y) : g.moveTo(X, Y); });
        g.strokeStyle = col; g.lineWidth = 2.4; g.stroke(); g.restore();
        f.res.forEach(r => D.circle(g, P.X(r.n), P.Y(Math.min(r[k], top)), 3.5, { fill: col }));
        D.text(g, name, 230, 30 + j * 16, { s: 11, b: true, c: col });
      });
      if (f.f) {
        const Q = plot(z, [320, 10, 270, 310], [-1, 1], [-2, 2], { dx: 1, dy: 0 });
        f.S.forEach(q => D.circle(g, Q.X(q.x), Q.Y(q.y), 3, { fill: klass(z, 0) }));
        g.save(); g.beginPath(); g.rect(Q.x0, Q.y0, Q.w, Q.h); g.clip(); g.beginPath();
        for (let i = 0; i <= 120; i++) { const x = -1 + 2 * i / 120, X = Q.X(x), Y = Q.Y(Math.max(-3, Math.min(3, f.f(x)))); i ? g.lineTo(X, Y) : g.moveTo(X, Y); }
        g.strokeStyle = klass(z, 1); g.lineWidth = 2.2; g.stroke(); g.restore();
        D.text(g, 'the fitted curve', 330, 30, { s: 11, b: true, c: c.ink2 });
      }
    }
  });
})();

/* =====================================================================================================
   Supervised 4.3  grid search against random search when only one setting really matters
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rng, klass } = MLZ;
  const score = (x, y) => 0.6 + 0.35 * Math.exp(-(((x - 0.63) / 0.07) ** 2)) + 0.03 * y;
  trace('mlgridrandom', {
    title: 'Grid search or random search?',
    sub: 'Two settings on a 0 to 1 scale. The score (shading) depends a lot on the first setting and hardly at all on the second. Both searches get 9 tries. Watch how many different values of the important setting each one tests.',
    W: 600, H: 330,
    params: [{ k: 'seed', label: 'Random seed', type: 'range', v: 4, min: 1, max: 30, step: 1 }],
    tips: [{ t: 'Try other seeds: random search is not always better, but on average it covers the important setting far more finely.', set: { seed: 12 }, play: true }],
    frames(p) {
      const G = [], R = [], r = rng(p.seed * 13 + 5);
      [1 / 6, 0.5, 5 / 6].forEach(x => [1 / 6, 0.5, 5 / 6].forEach(y => G.push({ x, y, s: score(x, y) })));
      for (let i = 0; i < 9; i++) { const x = r(), y = r(); R.push({ x, y, s: score(x, y) }); }
      const bg = G.reduce((a, b) => (b.s > a.s ? b : a)), br = R.reduce((a, b) => (b.s > a.s ? b : a));
      const fr = [{ G: [], R: [], say: 'Darker means a better score. The best region is a narrow band around 0.63 on the first setting. The second setting barely matters, but we do not know that in advance.' }];
      for (let i = 3; i <= 9; i += 3) fr.push({ G: G.slice(0, i), R: [], say: `Grid search, tries ${i - 2} to ${i}: a 3 × 3 grid. ${i === 9 ? `All 9 tries test only <b>3 different values</b> of the important setting (0.17, 0.5, 0.83). Best score ${f2(bg.s, 3)}.` : 'Each column repeats the same value of the first setting.'}` });
      for (let i = 3; i <= 9; i += 3) fr.push({ G, R: R.slice(0, i), say: `Random search, tries ${i - 2} to ${i}: each try picks both settings at random. ${i === 9 ? `9 tries test <b>9 different values</b> of the important setting. Best score ${f2(br.s, 3)}${br.s > bg.s ? ', better than the grid' : ''}.` : ''}` });
      fr.push({ G, R, bg, br, done: true, say: `Grid best ${f2(bg.s, 3)} at first setting ${f2(bg.x, 2)}, random best ${f2(br.s, 3)} at ${f2(br.x, 2)}. When only a few settings matter, which is usual, random search explores each of them more finely for the same cost (Bergstra and Bengio, 2012).` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 330, 310], [0, 1], [0, 1], { dx: 1, dy: 1, xl: 'setting 1 (matters)', yl: 'setting 2' });
      const cell = 8;
      g.save();
      for (let px = P.X(0); px < P.X(1); px += cell) for (let py = P.Y(1); py < P.Y(0); py += cell) {
        const x = (px + cell / 2 - P.X(0)) / (P.X(1) - P.X(0)), y = (P.Y(0) - py - cell / 2) / (P.Y(0) - P.Y(1));
        g.globalAlpha = Math.max(0, (score(x, y) - 0.58) / 0.42) * 0.55; g.fillStyle = c.cv; g.fillRect(px, py, cell, cell);
      }
      g.restore();
      f.G.forEach(q => { D.circle(g, P.X(q.x), P.Y(q.y), 7, { fill: klass(z, 0), stroke: c.surf, w: 1.5 }); D.line(g, P.X(q.x), P.Y(0), P.X(q.x), P.Y(0) + 8, klass(z, 0), 3); });
      f.R.forEach(q => { D.circle(g, P.X(q.x), P.Y(q.y), 7, { fill: klass(z, 1), stroke: c.surf, w: 1.5 }); D.line(g, P.X(q.x), P.Y(0) + 4, P.X(q.x), P.Y(0) + 12, klass(z, 1), 3); });
      head(z, 'Best score found', 360, 24);
      const best = S => (S.length ? S.reduce((a, b) => (b.s > a.s ? b : a)).s : null);
      D.text(g, 'grid search', 360, 52, { s: 12, b: true, c: klass(z, 0) });
      D.text(g, best(f.G) === null ? '...' : f2(best(f.G), 3), 500, 52, { s: 13, mono: true, b: true, c: c.ink });
      D.text(g, 'random search', 360, 76, { s: 12, b: true, c: klass(z, 1) });
      D.text(g, best(f.R) === null ? '...' : f2(best(f.R), 3), 500, 76, { s: 13, mono: true, b: true, c: c.ink });
      D.text(g, 'ticks under the plot show which', 360, 120, { s: 11, c: c.ink2 });
      D.text(g, 'values of setting 1 were tested', 360, 136, { s: 11, c: c.ink2 });
      D.text(g, `grid: ${new Set(f.G.map(q => q.x)).size} values`, 360, 166, { s: 12, mono: true, c: klass(z, 0) });
      D.text(g, `random: ${f.R.length} values`, 360, 186, { s: 12, mono: true, c: klass(z, 1) });
    }
  });
})();

/* =====================================================================================================
   Supervised 4.3  calibration: does "70% sure" really mean right 70% of the time?
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, rng, klass } = MLZ;
  const sig = t => 1 / (1 + Math.exp(-t)), logit = p => Math.log(p / (1 - p));
  trace('mlcalib', {
    title: 'Calibration: are the probabilities honest?',
    sub: 'An overconfident model scores 600 examples. Group the predictions into bins, and in each bin compare the average predicted probability with how often the label really was 1. Then fit Platt scaling and check again.',
    W: 600, H: 330,
    params: [{ k: 'over', label: 'How overconfident the model is', type: 'range', v: 2.5, min: 0.5, max: 4, step: 0.5 }],
    tips: [
      { t: 'Overconfidence 1: the model is already honest, the points sit on the diagonal.', set: { over: 1 }, play: true },
      { t: 'Overconfidence 0.5: an underconfident model (too close to 0.5), the curve is too steep.', set: { over: 0.5 }, play: true }
    ],
    frames(p) {
      const r = rng(23), D0 = [];
      for (let i = 0; i < 600; i++) { const q = 0.03 + 0.94 * r(); D0.push({ q, y: r() < q ? 1 : 0, p: sig(p.over * logit(q)) }); }
      const bins = ps => [0, 1, 2, 3, 4].map(b => { const S = D0.filter((d, i) => Math.min(4, Math.floor(ps[i] * 5)) === b); return S.length ? { m: S.reduce((s, d, j) => s + ps[D0.indexOf(d)], 0) / S.length, o: S.reduce((s, d) => s + d.y, 0) / S.length, n: S.length } : null; }).filter(Boolean);
      const brier = ps => D0.reduce((s, d, i) => s + (ps[i] - d.y) ** 2, 0) / D0.length;
      const raw = D0.map(d => d.p), B1 = bins(raw);
      let a = 1, b = 0;
      for (let it = 0; it < 600; it++) {
        let ga = 0, gb = 0;
        D0.forEach(d => { const t = logit(Math.min(0.999, Math.max(0.001, d.p))), e = sig(a * t + b) - d.y; ga += e * t; gb += e; });
        a -= 0.5 * ga / D0.length; b -= 0.5 * gb / D0.length;
      }
      const cal = D0.map(d => sig(a * logit(Math.min(0.999, Math.max(0.001, d.p))) + b)), B2 = bins(cal);
      const fr = [{ B1: [], say: 'The dashed diagonal is perfect calibration: among predictions of 0.7, exactly 70% should really be 1.' }];
      B1.forEach((q, i) => fr.push({ B1: B1.slice(0, i + 1), say: `Bin ${i + 1}: ${q.n} predictions with average probability ${f2(q.m, 2)}. The label was really 1 in <b>${f2(q.o * 100, 0)}%</b> of them. ${Math.abs(q.m - q.o) < 0.05 ? 'Close to honest.' : q.m > q.o ? 'The model predicts too high here.' : 'The model predicts too low here.'}` }));
      fr.push({ B1, bri1: brier(raw), say: `Brier score ${f2(brier(raw), 4)}. ${p.over > 1.2 ? 'The points form an S that is too flat: when the model says 0.95 it is right much less often. Typical for naive Bayes and boosted trees.' : p.over < 0.9 ? 'The points are too steep: the model hedges towards 0.5. Typical for random forests and SVM scores.' : 'The points follow the diagonal.'}` });
      fr.push({ B1, B2, bri1: brier(raw), bri2: brier(cal), a, b, say: `<b>Platt scaling</b> fits p' = sigmoid(A × logit(p) + B), in practice on held out data. Here A = ${f2(a, 2)}, B = ${f2(b, 2)}. The calibrated points (green) sit on the diagonal and the Brier score ${brier(cal) < brier(raw) - 0.002 ? 'drops to' : 'stays at'} <b>${f2(brier(cal), 4)}</b>. The ranking, and so the AUC, does not change.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 330, 310], [0, 1], [0, 1], { dx: 1, dy: 1, xl: 'predicted probability', yl: 'observed share of 1s' });
      D.line(g, P.X(0), P.Y(0), P.X(1), P.Y(1), c.ink2, 1.2, [5, 4]);
      const draw = (B, col) => {
        g.save(); g.beginPath(); B.forEach((q, i) => (i ? g.lineTo(P.X(q.m), P.Y(q.o)) : g.moveTo(P.X(q.m), P.Y(q.o)))); g.strokeStyle = col; g.lineWidth = 2.4; g.stroke(); g.restore();
        B.forEach(q => D.circle(g, P.X(q.m), P.Y(q.o), 5, { fill: col }));
      };
      draw(f.B1, klass(z, 1));
      if (f.B2) draw(f.B2, c.green || '#16a34a');
      head(z, 'Reliability', 360, 24);
      D.text(g, 'model as it is', 360, 50, { s: 12, b: true, c: klass(z, 1) });
      if (f.bri1 !== undefined) D.text(g, `Brier ${f2(f.bri1, 4)}`, 480, 50, { s: 12, mono: true, c: c.ink });
      if (f.B2) {
        D.text(g, 'after Platt scaling', 360, 74, { s: 12, b: true, c: c.green || '#16a34a' });
        D.text(g, `Brier ${f2(f.bri2, 4)}`, 480, 74, { s: 12, mono: true, c: c.ink });
        D.text(g, `A = ${f2(f.a, 2)}, B = ${f2(f.b, 2)}`, 360, 104, { s: 12, mono: true, c: c.ink2 });
      }
    }
  });
})();

/* =====================================================================================================
   Unsupervised 1.1  k-means: assign every point to the nearest centre, move each centre to its points' mean
   ===================================================================================================== */
const MLKM = (() => {
  const { rng } = MLZ;
  function blobs(n, centres, sd, seed) {
    const r = rng(seed), g = () => { let s = 0; for (let i = 0; i < 6; i++) s += r(); return (s - 3) * Math.SQRT2; };
    const P = [];
    for (let i = 0; i < n; i++) { const c = centres[i % centres.length]; P.push({ x: c[0] + sd * g(), y: c[1] + sd * g(), t: i % centres.length }); }
    return P;
  }
  const d2 = (a, c) => (a.x - c.x) ** 2 + (a.y - c.y) ** 2;
  function seedCentres(P, k, how, seed) {
    const r = rng(seed);
    if (how === 'random') { const C = []; while (C.length < k) { const q = P[Math.floor(r() * P.length)]; if (!C.includes(q)) C.push(q); } return C.map(q => ({ x: q.x, y: q.y })); }
    const C = [P[Math.floor(r() * P.length)]];
    while (C.length < k) {
      const w = P.map(a => Math.min(...C.map(c => d2(a, c)))), s = w.reduce((u, v) => u + v, 0);
      let t = r() * s, i = 0; while (t > w[i] && i < P.length - 1) { t -= w[i]; i++; }
      C.push(P[i]);
    }
    return C.map(q => ({ x: q.x, y: q.y }));
  }
  function run(P, C) {
    const hist = [];
    for (let it = 0; it < 20; it++) {
      const lab = P.map(a => { let b = 0; C.forEach((c, j) => { if (d2(a, c) < d2(a, C[b])) b = j; }); return b; });
      const inertia = P.reduce((s, a, i) => s + d2(a, C[lab[i]]), 0);
      const N = C.map((c, j) => { const S = P.filter((_, i) => lab[i] === j); return S.length ? { x: S.reduce((s, a) => s + a.x, 0) / S.length, y: S.reduce((s, a) => s + a.y, 0) / S.length } : c; });
      hist.push({ C: C.map(c => ({ ...c })), lab, inertia, N });
      const moved = N.reduce((s, c, j) => s + Math.hypot(c.x - C[j].x, c.y - C[j].y), 0);
      C = N;
      if (moved < 1e-9) break;
    }
    return hist;
  }
  return { blobs, seedCentres, run, d2 };
})();
(() => {
  const { trace, plot, D, f2, head, klass } = MLZ;
  const DATA = { three: [[2, 2], [7, 3], [4.5, 7.5]], four: [[2, 2], [7, 2], [2, 7], [7, 7]], close: [[3, 3], [5, 4], [8, 8]] };
  trace('mlkmeans', {
    title: 'k-means: assign, update, repeat',
    sub: 'Pick k starting centres. Then repeat two steps until nothing changes: give every point to its nearest centre, and move every centre to the mean of its points. Each round can only lower the total squared distance (inertia).',
    W: 600, H: 330,
    params: [
      { k: 'data', label: 'Data', type: 'select', v: 'three', opts: [['three', 'Three groups'], ['four', 'Four groups'], ['close', 'Two groups close together']] },
      { k: 'k', label: 'k (number of clusters)', type: 'range', v: 3, min: 2, max: 5, step: 1 },
      { k: 'init', label: 'Starting centres', type: 'select', v: 'random', opts: [['random', 'Random points'], ['pp', 'k-means++ (spread out)']] },
      { k: 'seed', label: 'Random seed', type: 'range', v: 3, min: 1, max: 20, step: 1 }
    ],
    tips: [
      { t: 'Four groups but k = 3: k-means must merge two of them. It always returns exactly k clusters.', set: { data: 'four', k: 3 }, play: true },
      { t: 'Try seeds with random starts on four groups and k = 4: some runs get stuck with two centres in one group.', set: { data: 'four', k: 4, init: 'random', seed: 6 }, play: true }
    ],
    frames(p) {
      const P = MLKM.blobs(60, DATA[p.data], 0.9, 11), C0 = MLKM.seedCentres(P, p.k, p.init, p.seed);
      const H = MLKM.run(P, C0);
      const fr = [{ P, say: `${P.length} points with no labels. We ask k-means for <b>${p.k}</b> clusters.` }];
      fr.push({ P, C: H[0].C, say: `Choose ${p.k} starting centres (crosses) ${p.init === 'pp' ? 'with k-means++: the first at random, each next one far from those already chosen' : 'by picking random points'}.` });
      H.forEach((h, i) => {
        fr.push({ P, C: h.C, lab: h.lab, inertia: h.inertia, say: `Round ${i + 1}, assign: every point joins its nearest centre. Inertia (sum of squared distances to the centres) = <b>${f2(h.inertia, 1)}</b>.` });
        if (i < H.length - 1) fr.push({ P, C: h.N, old: h.C, lab: h.lab, inertia: h.inertia, say: `Round ${i + 1}, update: move each centre to the mean of its points (the arrows).` });
      });
      const last = H[H.length - 1];
      fr.push({ P, C: last.C, lab: last.lab, inertia: last.inertia, done: true, say: `No point changed cluster, so k-means has converged after ${H.length} rounds with inertia <b>${f2(last.inertia, 1)}</b>. This is a local minimum: a different start can end somewhere else, which is why KMeans runs n_init starts and keeps the best.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 310], [-1, 10.5], [-1, 10.5], { dx: 0, dy: 0 });
      f.P.forEach((a, i) => D.circle(g, P.X(a.x), P.Y(a.y), 4.5, { fill: f.lab ? klass(z, f.lab[i]) : c.ink2, stroke: c.surf, w: 1 }));
      if (f.old) f.old.forEach((o, j) => D.arrow ? D.arrow(g, P.X(o.x), P.Y(o.y), P.X(f.C[j].x), P.Y(f.C[j].y), c.ink, 1.6) : D.line(g, P.X(o.x), P.Y(o.y), P.X(f.C[j].x), P.Y(f.C[j].y), c.ink, 1.6));
      (f.C || []).forEach((q, j) => {
        const X = P.X(q.x), Y = P.Y(q.y), col = klass(z, j);
        D.line(g, X - 9, Y - 9, X + 9, Y + 9, c.ink, 5); D.line(g, X - 9, Y + 9, X + 9, Y - 9, c.ink, 5);
        D.line(g, X - 8, Y - 8, X + 8, Y + 8, col, 3); D.line(g, X - 8, Y + 8, X + 8, Y - 8, col, 3);
      });
      head(z, 'k-means', 425, 24);
      if (f.inertia !== undefined) D.text(g, `inertia ${f2(f.inertia, 1)}`, 425, 50, { s: 14, b: true, c: c.cv });
      if (f.lab) (f.C || []).forEach((q, j) => D.text(g, `cluster ${j + 1}: ${f.lab.filter(l => l === j).length} points`, 425, 80 + j * 20, { s: 12, mono: true, c: klass(z, j) }));
    }
  });
})();

/* =====================================================================================================
   Unsupervised 1.1  choosing k: the elbow of the inertia curve and the silhouette score
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, klass } = MLZ;
  trace('mlelbow', {
    title: 'Choosing k: elbow and silhouette',
    sub: 'Run k-means for k = 1 to 8 on the same points. Inertia always falls as k grows, so look for the bend (elbow). The silhouette score measures how much closer points are to their own cluster than to the next one, higher is better.',
    W: 600, H: 330,
    params: [{ k: 'groups', label: 'True number of groups in the data', type: 'range', v: 4, min: 2, max: 6, step: 1 }],
    tips: [{ t: 'Two true groups: the elbow and the silhouette both point clearly at k = 2.', set: { groups: 2 }, play: true }],
    frames(p) {
      const centres = [[2, 2], [8, 2], [2, 8], [8, 8], [5, 5], [5, 9]].slice(0, p.groups);
      const P = MLKM.blobs(150, centres, 0.8, 21);
      const res = [];
      const sil = lab => {
        let tot = 0;
        P.forEach((a, i) => {
          const by = {};
          P.forEach((b, j) => { if (i !== j) { const d = Math.sqrt(MLKM.d2(a, b)); (by[lab[j]] = by[lab[j]] || []).push(d); } });
          const own = by[lab[i]] ? by[lab[i]].reduce((s, v) => s + v, 0) / by[lab[i]].length : 0;
          const other = Math.min(...Object.keys(by).filter(k => +k !== lab[i]).map(k => by[k].reduce((s, v) => s + v, 0) / by[k].length));
          tot += isFinite(other) ? (other - own) / Math.max(own, other) : 0;
        });
        return tot / P.length;
      };
      const fr = [{ P, res: [], say: `150 points. In truth there are ${p.groups} groups, but k-means does not know that. We try every k from 1 to 8.` }];
      for (let k = 1; k <= 8; k++) {
        let best = null;
        for (let s = 1; s <= 3; s++) { const H = MLKM.run(P, MLKM.seedCentres(P, k, 'pp', s * 7 + k)); const h = H[H.length - 1]; if (!best || h.inertia < best.inertia) best = h; }
        const sv = k > 1 ? sil(best.lab) : null;
        res.push({ k, inertia: best.inertia, sil: sv, lab: best.lab, C: best.C });
        fr.push({ P, res: res.slice(), show: res[k - 1], say: `k = ${k}: inertia <b>${f2(best.inertia, 0)}</b>${sv === null ? ' (silhouette needs at least 2 clusters)' : `, silhouette <b>${f2(sv, 3)}</b>`}.${k > 1 ? ` Inertia fell by ${f2(100 * (1 - best.inertia / res[k - 2].inertia), 0)}% from k = ${k - 1}.` : ''}` });
      }
      const bs = res.filter(r => r.sil !== null).reduce((a, b) => (b.sil > a.sil ? b : a));
      fr.push({ P, res, show: bs, done: true, bs, say: `The inertia curve bends sharply around k = ${p.groups}, and after that each extra cluster helps little. The silhouette is highest at <b>k = ${bs.k}</b>. When the two disagree, or the data has no clear groups, choose k by what the clusters will be used for.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const mx = f.res.length ? f.res[0].inertia : 1;
      const P = plot(z, [10, 10, 280, 310], [0, 8], [0, mx * 1.05 || 1], { dx: 0, dy: 0, xl: 'k', yl: 'inertia' });
      g.save(); g.beginPath(); f.res.forEach((r, i) => (i ? g.lineTo(P.X(r.k), P.Y(r.inertia)) : g.moveTo(P.X(r.k), P.Y(r.inertia)))); g.strokeStyle = c.cv; g.lineWidth = 2.4; g.stroke(); g.restore();
      f.res.forEach(r => D.circle(g, P.X(r.k), P.Y(r.inertia), 4, { fill: c.cv }));
      f.res.forEach(r => { if (r.sil !== null) { const h = Math.max(0, r.sil) * 120; g.fillStyle = f.bs && r.k === f.bs.k ? klass(z, 1) : c.line; g.fillRect(P.X(r.k) - 6, P.Y(0) - h, 12, h); } });
      D.text(g, 'bars: silhouette', 200, 30, { s: 10, b: true, c: klass(z, 1) });
      const Q = plot(z, [300, 10, 290, 310], [-1, 11], [-1, 11], { dx: 0, dy: 0, grid: false });
      f.P.forEach((a, i) => D.circle(g, Q.X(a.x), Q.Y(a.y), 3.5, { fill: f.show ? klass(z, f.show.lab[i]) : c.ink2 }));
      if (f.show) D.text(g, `k = ${f.show.k}`, 310, 30, { s: 13, b: true, c: c.ink });
    }
  });
})();

/* =====================================================================================================
   Unsupervised 1.2  agglomerative clustering: merge the two closest clusters and grow a dendrogram
   ===================================================================================================== */
(() => {
  const { trace, plot, points, D, f2, head, klass } = MLZ;
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  function link(A, B, P, how) {
    if (how === 'ward') {
      const m = S => ({ x: S.reduce((s, i) => s + P[i].x, 0) / S.length, y: S.reduce((s, i) => s + P[i].y, 0) / S.length });
      return Math.sqrt(2 * A.length * B.length / (A.length + B.length)) * dist(m(A), m(B));
    }
    const ds = [];
    A.forEach(i => B.forEach(j => ds.push(dist(P[i], P[j]))));
    if (how === 'single') return Math.min(...ds);
    if (how === 'complete') return Math.max(...ds);
    return ds.reduce((s, v) => s + v, 0) / ds.length;
  }
  const NAME = { single: 'single linkage (closest pair)', complete: 'complete linkage (farthest pair)', average: 'average linkage (mean of all pairs)', ward: 'Ward (smallest rise in squared error)' };
  trace('mldendro', {
    title: 'Agglomerative clustering and the dendrogram',
    sub: 'Start with every point as its own cluster. Again and again, merge the two closest clusters. The dendrogram on the right records every merge at the height of its distance. Cut it where the jump is biggest.',
    W: 600, H: 330,
    params: [
      { k: 'pts', label: 'Points (x y)', type: 'area', v: '1 1; 1.6 2; 2.2 1.2; 6 6; 6.6 7.2; 7.4 6.2; 8 1.5; 8.8 2.2' },
      { k: 'how', label: 'Linkage (distance between clusters)', type: 'select', v: 'single', opts: [['single', 'Single (closest pair)'], ['complete', 'Complete (farthest pair)'], ['average', 'Average'], ['ward', 'Ward']] }
    ],
    tips: [
      { t: 'A chain of points with single linkage: each point is close to the next, so the chain merges early, one link at a time.', set: { pts: '1 1; 2 1.6; 3 2.2; 4 2.8; 5 3.4; 8.5 8.5; 9.2 8; 8.6 7.6', how: 'single' }, play: true },
      { t: 'Same chain with complete linkage: the far ends make the chain look wide, so its pieces join much higher up the tree than with single linkage.', set: { pts: '1 1; 2 1.6; 3 2.2; 4 2.8; 5 3.4; 8.5 8.5; 9.2 8; 8.6 7.6', how: 'complete' }, play: true },
      { t: 'Two groups with stray points between them: single linkage hops across the strays, so the two groups join at a low height. Switch to Ward and they join much higher.', set: { pts: '1 1; 1.6 2; 2.2 1.2; 6 6; 6.6 7.2; 7.4 6.2; 3.2 3; 4.6 4.6', how: 'single' }, play: true }
    ],
    frames(p) {
      const P = points(p.pts).slice(0, 12);
      if (P.length < 3) throw new Error('Type at least three points');
      let C = P.map((_, i) => ({ m: [i], id: i }));
      const merges = [];
      let next = P.length;
      while (C.length > 1) {
        let best = null;
        for (let i = 0; i < C.length; i++) for (let j = i + 1; j < C.length; j++) {
          const d = link(C[i].m, C[j].m, P, p.how);
          if (!best || d < best.d - 1e-12) best = { d, i, j };
        }
        const a = C[best.i], b = C[best.j], nc = { m: a.m.concat(b.m), id: next++, a, b, h: best.d };
        merges.push(nc);
        C = C.filter((_, k) => k !== best.i && k !== best.j).concat([nc]);
      }
      const order = []; (function walk(n) { if (n.a) { walk(n.a); walk(n.b); } else order.push(n.id); })(C[0]);
      let gap = 0, cut = 0;
      for (let k = 1; k < merges.length; k++) { const g2 = merges[k].h - merges[k - 1].h; if (g2 > gap) { gap = g2; cut = k; } }
      const cutH = (merges[cut - 1].h + merges[cut].h) / 2, nClus = merges.length - cut + 1;
      const groupsAt = k => { let G = P.map((_, i) => [i]); merges.slice(0, k).forEach(mg => { G = G.filter(g => !mg.a.m.includes(g[0]) && !mg.b.m.includes(g[0])); G.push(mg.m); }); return G; };
      const fr = [{ P, merges, order, k: 0, G: groupsAt(0), say: `${P.length} points, each starting as its own cluster. Distance between clusters: <b>${NAME[p.how]}</b>.` }];
      merges.forEach((mg, k) => {
        fr.push({ P, merges, order, k: k + 1, G: groupsAt(k + 1), last: mg, say: `Merge ${k + 1}: the closest two clusters (${mg.a.m.length} and ${mg.b.m.length} point${mg.b.m.length > 1 ? 's' : ''}) are ${f2(mg.h, 2)} apart, so they join into one cluster of ${mg.m.length}. ${C.length === 1 && k === merges.length - 1 ? 'Everything is now one cluster.' : `${P.length - k - 1} clusters remain.`}` });
      });
      fr.push({ P, merges, order, k: merges.length, G: groupsAt(cut), cutH, done: true, say: `The biggest jump in merge height is between ${f2(merges[cut - 1].h, 2)} and ${f2(merges[cut].h, 2)}. Cutting the tree at height ${f2(cutH, 2)} (dashed line) gives <b>${nClus} clusters</b>. You never had to choose k in advance: the tree holds every answer from ${P.length} clusters down to 1.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const xs = f.P.map(q => q.x), ys = f.P.map(q => q.y);
      const lo = Math.min(...xs, ...ys) - 1, hi = Math.max(...xs, ...ys) + 1;
      const P = plot(z, [10, 10, 280, 310], [lo, hi], [lo, hi], { dx: 0, dy: 0 });
      const gid = i => f.G.findIndex(G => G.includes(i));
      f.merges.slice(0, f.k).forEach(mg => {
        let best = null;
        mg.a.m.forEach(i => mg.b.m.forEach(j => { const d = dist(f.P[i], f.P[j]); if (!best || d < best.d) best = { d, i, j }; }));
        D.line(g, P.X(f.P[best.i].x), P.Y(f.P[best.i].y), P.X(f.P[best.j].x), P.Y(f.P[best.j].y), f.last === mg ? c.cv : c.ink2, f.last === mg ? 2 : 1, [4, 3]);
      });
      f.P.forEach((q, i) => {
        const G = f.G[gid(i)], col = G.length > 1 ? klass(z, gid(i)) : c.ink2;
        D.circle(g, P.X(q.x), P.Y(q.y), f.last && f.last.m.includes(i) ? 7 : 5, { fill: col, stroke: f.last && f.last.m.includes(i) ? c.ink : c.surf, w: 1.5 });
        D.text(g, String(i + 1), P.X(q.x) + 7, P.Y(q.y) - 6, { s: 10, c: c.ink2 });
      });
      const top = f.merges[f.merges.length - 1].h * 1.08 || 1;
      const Q = plot(z, [300, 10, 290, 310], [-0.5, f.P.length - 0.5], [0, top], { dx: 0, dy: 2, grid: false });
      const pos = {}, hgt = {};
      f.order.forEach((id, k) => { pos[id] = k; hgt[id] = 0; D.text(g, String(id + 1), Q.X(k), Q.Y(0) + 14, { a: 'center', s: 10, c: c.ink2 }); });
      D.line(g, Q.X(-0.5), Q.Y(0), Q.X(f.P.length - 0.5), Q.Y(0), c.line, 1);
      for (let t = 0; t <= 4; t++) { const v = top * t / 4; D.text(g, f2(v, 1), Q.x0 + 22, Q.Y(v) + 3, { a: 'right', s: 10, c: c.ink2 }); }
      f.merges.forEach((mg, k) => {
        pos[mg.id] = (pos[mg.a.id] + pos[mg.b.id]) / 2; hgt[mg.id] = mg.h;
        if (k >= f.k) return;
        const col = f.last === mg ? c.cv : c.ink;
        D.line(g, Q.X(pos[mg.a.id]), Q.Y(hgt[mg.a.id]), Q.X(pos[mg.a.id]), Q.Y(mg.h), col, 1.8);
        D.line(g, Q.X(pos[mg.b.id]), Q.Y(hgt[mg.b.id]), Q.X(pos[mg.b.id]), Q.Y(mg.h), col, 1.8);
        D.line(g, Q.X(pos[mg.a.id]), Q.Y(mg.h), Q.X(pos[mg.b.id]), Q.Y(mg.h), col, 1.8);
      });
      if (f.cutH) { D.line(g, Q.X(-0.5), Q.Y(f.cutH), Q.X(f.P.length - 0.5), Q.Y(f.cutH), c.red, 1.6, [6, 4]); D.text(g, 'cut', Q.X(f.P.length - 0.5) - 2, Q.Y(f.cutH) - 5, { a: 'right', s: 11, b: true, c: c.red }); }
      D.text(g, 'merge height', 340, 26, { s: 11, b: true, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Unsupervised 1.2  DBSCAN: core points, growing clusters through dense regions, border points and noise
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, klass, rng } = MLZ;
  function data(kind) {
    const r = rng(kind === 'moons' ? 5 : kind === 'blobs' ? 9 : 13), g = () => { let s = 0; for (let i = 0; i < 6; i++) s += r(); return (s - 3) * Math.SQRT2; };
    const P = [];
    if (kind === 'moons') for (let i = 0; i < 160; i++) { const t = Math.PI * r(); P.push(i % 2 ? { x: Math.cos(t) + 0.06 * g(), y: Math.sin(t) + 0.06 * g() } : { x: 1 - Math.cos(t) + 0.06 * g(), y: 0.5 - Math.sin(t) + 0.06 * g() }); }
    if (kind === 'blobs') { [[-0.6, 0.1, 0.12, 60], [1.6, 0.2, 0.3, 60], [0.6, 1.4, 0.2, 40]].forEach(([cx, cy, s, n]) => { for (let i = 0; i < n; i++) P.push({ x: cx + s * g(), y: cy + s * g() }); }); }
    if (kind === 'ring') for (let i = 0; i < 160; i++) { const t = 2 * Math.PI * r(), rad = i % 3 ? 1.3 : 0.35; P.push({ x: 0.5 + rad * Math.cos(t) + 0.05 * g(), y: 0.5 + rad * Math.sin(t) + 0.05 * g() }); }
    for (let i = 0; i < 12; i++) P.push({ x: -1.5 + 4 * r(), y: -1 + 3 * r() });
    return P;
  }
  trace('mldbscan', {
    title: 'DBSCAN: clusters are dense regions',
    sub: 'A point with at least minPts points within distance eps (itself included) is a core point. Clusters grow from core point to core point. Points near a cluster but not core are border points. Everything else is noise.',
    W: 600, H: 330,
    params: [
      { k: 'data', label: 'Data', type: 'select', v: 'moons', opts: [['moons', 'Two moons plus noise'], ['blobs', 'Blobs of different spread'], ['ring', 'A ring around a blob']] },
      { k: 'eps', label: 'eps (neighbourhood radius)', type: 'range', v: 0.2, min: 0.05, max: 0.6, step: 0.05 },
      { k: 'mp', label: 'minPts', type: 'range', v: 5, min: 2, max: 12, step: 1 }
    ],
    tips: [
      { t: 'eps too small: most points are noise and the moons break into pieces.', set: { data: 'moons', eps: 0.1 }, play: true },
      { t: 'eps too large: the two moons touch and become one cluster.', set: { data: 'moons', eps: 0.45 }, play: true },
      { t: 'Blobs of different spread: one eps cannot suit the tight blob and the wide blob at the same time.', set: { data: 'blobs', eps: 0.15, mp: 5 }, play: true }
    ],
    frames(p) {
      const P = data(p.data), n = P.length;
      const near = P.map(a => P.map((b, j) => j).filter(j => Math.hypot(a.x - P[j].x, a.y - P[j].y) <= p.eps + 1e-12));
      const core = near.map(N => N.length >= p.mp);
      const nc = core.filter(Boolean).length;
      const ex = core.findIndex(Boolean) >= 0 ? core.findIndex(Boolean) : 0;
      const lab = new Array(n).fill(-1);
      const fr = [{ P, lab: lab.slice(), say: `${n} points, no labels. DBSCAN needs two settings: eps = <b>${f2(p.eps, 2)}</b> and minPts = <b>${p.mp}</b>. It does not need the number of clusters.` }];
      fr.push({ P, lab: lab.slice(), ring: ex, eps: p.eps, say: `Look at one point: ${near[ex].length} points lie within eps of it (the circle), counting itself. ${near[ex].length >= p.mp ? `That is at least ${p.mp}, so it is a <b>core point</b>.` : `That is fewer than ${p.mp}, so it is not a core point.`}` });
      fr.push({ P, lab: lab.slice(), core, say: `Do the same count for every point. <b>${nc}</b> of ${n} points are core points (outlined). The rest are not dense enough on their own.` });
      let k = 0, shown = 0;
      for (let i = 0; i < n; i++) {
        if (!core[i] || lab[i] !== -1) continue;
        lab[i] = k; let front = [i], waves = 0;
        while (front.length) {
          const nf = [];
          front.forEach(q => near[q].forEach(j => { if (lab[j] === -1) { lab[j] = k; if (core[j]) nf.push(j); } }));
          front = nf; waves++;
          if (shown < 3 && k < 2 && (waves === 2 || waves === 6)) fr.push({ P, lab: lab.slice(), core, say: `Cluster ${k + 1} is growing: from each core point, add every point within eps, and keep going from the new core points (${lab.filter(l => l === k).length} points so far).` });
        }
        const size = lab.filter(l => l === k).length, border = lab.map((l, j) => l === k && !core[j]).filter(Boolean).length;
        if (k < 6) fr.push({ P, lab: lab.slice(), core, say: `Cluster ${k + 1} cannot grow any more: <b>${size} points</b>, of which ${border} are border points (reached from a core point but not core themselves).` });
        k++; shown++;
      }
      const noise = lab.filter(l => l === -1).length;
      fr.push({ P, lab: lab.slice(), core, done: true, say: `Done: <b>${k} cluster${k === 1 ? '' : 's'}</b> and <b>${noise} noise points</b> (grey crosses). ${k > 6 ? 'Many tiny clusters usually mean eps is too small. ' : ''}${k === 1 && p.data !== 'blobs' ? 'One big cluster usually means eps is too large. ' : ''}The clusters can have any shape, because they follow the dense regions.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 310], [-1.6, 2.6], [-1.1, 2.13], { dx: 1, dy: 1 });
      const sx = (P.X(1) - P.X(0));
      if (f.ring !== undefined) { const q = f.P[f.ring]; D.circle(g, P.X(q.x), P.Y(q.y), sx * f.eps, { fill: 'rgba(124,58,237,0.12)', stroke: c.cv, w: 1.5 }); }
      f.P.forEach((q, i) => {
        const X = P.X(q.x), Y = P.Y(q.y), l = f.lab[i];
        if (f.done && l === -1) { D.line(g, X - 3.5, Y - 3.5, X + 3.5, Y + 3.5, c.ink2, 1.6); D.line(g, X - 3.5, Y + 3.5, X + 3.5, Y - 3.5, c.ink2, 1.6); return; }
        D.circle(g, X, Y, f.core && f.core[i] ? 4.2 : 3, f.core && f.core[i] ? { fill: l >= 0 ? klass(z, l) : c.line, stroke: c.ink, w: 1 } : { fill: l >= 0 ? klass(z, l) : c.ink2 });
      });
      head(z, 'DBSCAN', 425, 24);
      const k = Math.max(-1, ...f.lab) + 1, noise = f.lab.filter(l => l === -1).length;
      D.text(g, `clusters so far: ${k}`, 425, 50, { s: 13, b: true, c: c.cv });
      for (let j = 0; j < Math.min(k, 8); j++) D.text(g, `cluster ${j + 1}: ${f.lab.filter(l => l === j).length}`, 425, 76 + j * 18, { s: 12, mono: true, c: klass(z, j) });
      if (k > 8) D.text(g, `and ${k - 8} more`, 425, 76 + 8 * 18, { s: 12, c: c.ink2 });
      D.text(g, `${f.done ? 'noise' : 'not yet in a cluster'}: ${noise}`, 425, 250, { s: 12, mono: true, c: c.ink2 });
      if (f.core) D.text(g, 'outlined = core point', 425, 272, { s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Unsupervised 1.3  EM for a 1D Gaussian mixture: E step responsibilities, M step new means, spreads, weights
   ===================================================================================================== */
const MLGM = (() => {
  const npdf = (x, m, s) => Math.exp(-0.5 * ((x - m) / s) ** 2) / (s * Math.sqrt(2 * Math.PI));
  function em1(x, mu, sd, w, rounds) {
    const H = [];
    for (let it = 0; it < rounds; it++) {
      const R = x.map(v => { const d = mu.map((m, k) => w[k] * npdf(v, m, sd[k])); const s = d.reduce((a, b) => a + b, 0) || 1e-300; return { r: d.map(q => q / s), s }; });
      const ll = R.reduce((a, q) => a + Math.log(q.s), 0);
      const nk = mu.map((_, k) => R.reduce((a, q) => a + q.r[k], 0));
      const nmu = mu.map((_, k) => R.reduce((a, q, i) => a + q.r[k] * x[i], 0) / (nk[k] || 1e-12));
      const nsd = mu.map((_, k) => Math.max(0.05, Math.sqrt(R.reduce((a, q, i) => a + q.r[k] * (x[i] - nmu[k]) ** 2, 0) / (nk[k] || 1e-12))));
      const nw = nk.map(n => n / x.length);
      H.push({ mu: mu.slice(), sd: sd.slice(), w: w.slice(), R: R.map(q => q.r), ll, nmu, nsd, nw });
      const move = nmu.reduce((a, m, k) => a + Math.abs(m - mu[k]) + Math.abs(nsd[k] - sd[k]), 0);
      mu = nmu; sd = nsd; w = nw;
      if (move < 1e-3) break;
    }
    return H;
  }
  return { npdf, em1 };
})();
(() => {
  const { trace, plot, nums, D, f2, head, klass, span } = MLZ;
  trace('mlem', {
    title: 'EM for a Gaussian mixture, one round at a time',
    sub: 'Each point gets a probability of belonging to each bell curve (E step). Then each curve moves to fit the points it is responsible for, weighted by those probabilities (M step). Repeat until nothing changes.',
    W: 600, H: 330,
    params: [
      { k: 'x', label: 'Data values', type: 'area', v: '150 152 155 157 160 170 174 176 179 182' },
      { k: 'k', label: 'Number of bell curves', type: 'range', v: 2, min: 2, max: 3, step: 1 },
      { k: 'start', label: 'Starting means', type: 'select', v: 'close', opts: [['close', 'Close together'], ['spread', 'Spread over the range']] }
    ],
    tips: [
      { t: 'Starting means spread over the range: EM reaches the same answer in fewer rounds.', set: { start: 'spread' }, play: true },
      { t: 'Three tight groups with three curves: each curve settles on one group and the weights match the group sizes.', set: { x: '1 1.3 1.5 1.8 5 5.2 5.5 9 9.2 9.4 9.5 9.8', k: 3, start: 'spread' }, play: true }
    ],
    frames(p) {
      const x = nums(p.x).slice(0, 40);
      if (x.length < 4) throw new Error('Type at least four numbers');
      const lo = Math.min(...x), hi = Math.max(...x), rg = hi - lo || 1, mean = x.reduce((a, b) => a + b, 0) / x.length;
      const sd0 = Math.sqrt(x.reduce((a, v) => a + (v - mean) ** 2, 0) / x.length) || 1;
      const K = p.k;
      const mu0 = Array.from({ length: K }, (_, k) => p.start === 'close' ? mean + (k - (K - 1) / 2) * 0.5 * sd0 : lo + rg * (k + 0.5) / K);
      const H = MLGM.em1(x, mu0, mu0.map(() => sd0), mu0.map(() => 1 / K), 100);
      const xr = span(x, 0.25), base = { x, xr };
      const fmt = h => h.mu.map((m, k) => `curve ${k + 1}: mean ${f2(m, 1)}, sd ${f2(h.sd[k], 1)}, weight ${f2(h.w[k], 2)}`).join('. ');
      const fr = [{ ...base, say: `${x.length} values and no labels. We believe they come from <b>${K}</b> bell curves (Gaussians), but we do not know where the curves are, how wide they are, or which value came from which.` }];
      fr.push({ ...base, mu: H[0].mu, sd: H[0].sd, w: H[0].w, say: `Start with a guess. ${fmt(H[0])}.` });
      const show = H.length <= 8 ? H.map((_, i) => i) : [0, 1, 2, 3, 5, 8, 12, 20, H.length - 1].filter((v, i, a) => v < H.length && a.indexOf(v) === i);
      show.forEach(i => {
        const h = H[i];
        const ex = x.reduce((b, v, j) => (Math.max(...h.R[j]) < Math.max(...h.R[b]) ? j : b), 0);
        fr.push({ ...base, mu: h.mu, sd: h.sd, w: h.w, R: h.R, ll: h.ll, mark: ex, say: `Round ${i + 1}, E step: for each value, the share of the bars says how likely each curve produced it. The value ${f2(x[ex], 1)} is the most uncertain: ${h.R[ex].map((r, k) => `${f2(100 * r, 0)}% curve ${k + 1}`).join(', ')}. Log likelihood of the data under these curves: <b>${f2(h.ll, 3)}</b>.` });
        fr.push({ ...base, mu: h.nmu, sd: h.nsd, w: h.nw, old: h.mu, R: h.R, ll: h.ll, say: `Round ${i + 1}, M step: each curve moves to the weighted mean of the values, using those probabilities as weights. ${fmt({ mu: h.nmu, sd: h.nsd, w: h.nw })}.` });
      });
      const L = H[H.length - 1];
      fr.push({ ...base, mu: L.nmu, sd: L.nsd, w: L.nw, R: L.R, ll: L.ll, done: true, say: `${H.length < 100 ? `Converged after ${H.length} rounds: the curves stopped moving and the log likelihood stopped rising (it never falls in EM).` : 'Stopped after 100 rounds, still creeping: the log likelihood rises a little each round but has not settled. A different start would converge faster.'} Every value keeps a probability for every curve, which is a <b>soft</b> clustering. k-means would give each value to exactly one group.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const ymax = f.mu ? Math.max(...f.mu.map((m, k) => f.w[k] * MLGM.npdf(m, m, f.sd[k]))) * 1.15 : 1;
      const P = plot(z, [10, 10, 580, 310], f.xr, [-0.45 * ymax, ymax], { dx: 0, dy: 3 });
      D.line(g, P.X(f.xr[0]), P.Y(0), P.X(f.xr[1]), P.Y(0), c.line, 1);
      if (f.mu) f.mu.forEach((m, k) => {
        g.save(); g.beginPath();
        for (let i = 0; i <= 200; i++) { const v = f.xr[0] + (f.xr[1] - f.xr[0]) * i / 200, y = f.w[k] * MLGM.npdf(v, m, f.sd[k]); i ? g.lineTo(P.X(v), P.Y(y)) : g.moveTo(P.X(v), P.Y(y)); }
        g.strokeStyle = klass(z, k); g.lineWidth = 2.4; g.stroke(); g.restore();
        D.line(g, P.X(m), P.Y(0), P.X(m), P.Y(f.w[k] * MLGM.npdf(m, m, f.sd[k])), klass(z, k), 1, [3, 3]);
        if (f.old) D.line(g, P.X(f.old[k]), P.Y(-0.04 * ymax), P.X(m), P.Y(-0.04 * ymax), klass(z, k), 2);
      });
      const bh = P.Y(-0.4 * ymax) - P.Y(-0.1 * ymax);
      f.x.forEach((v, j) => {
        const X = P.X(v);
        if (f.R) { let y0 = P.Y(-0.1 * ymax); f.R[j].forEach((r, k) => { g.fillStyle = klass(z, k); g.fillRect(X - 3, y0, 6, bh * r); y0 += bh * r; }); }
        D.circle(g, X, P.Y(0), f.mark === j ? 6 : 4, { fill: c.ink, stroke: f.mark === j ? c.red : c.surf, w: f.mark === j ? 2 : 1 });
      });
      if (f.R) D.text(g, 'bars: probability of each curve', 590 - 8, 26, { a: 'right', s: 11, b: true, c: c.ink2 });
      if (f.ll !== undefined) D.text(g, `log likelihood ${f2(f.ll, 3)}`, 590 - 8, 44, { a: 'right', s: 12, b: true, c: c.cv });
    }
  });
})();

/* =====================================================================================================
   Unsupervised 1.3  a 2D Gaussian mixture fitted by EM: ellipses, soft assignments, compared with k-means
   ===================================================================================================== */
(() => {
  const { trace, plot, D, f2, head, klass, rng } = MLZ;
  const SETS = {
    flat: [[[0, 0], [[6, 0], [0, 0.3]], 90], [[0, 2.5], [[6, 0], [0, 0.3]], 90]],
    tilted: [[[-2.5, 1], [[3, 2.4], [2.4, 3]], 90], [[3.5, 1], [[0.4, 0], [0, 2.5]], 90]],
    blobs: [[[-3, 0], [[0.5, 0], [0, 0.5]], 60], [[2, -1], [[1.5, 0], [0, 1.5]], 60], [[1, 4], [[0.8, 0.5], [0.5, 0.8]], 60]]
  };
  function make(kind) {
    const r = rng(17), n = () => { let s = 0; for (let i = 0; i < 6; i++) s += r(); return (s - 3) * Math.SQRT2; };
    const P = [];
    SETS[kind].forEach(([m, S, cnt], t) => {
      const a = Math.sqrt(S[0][0]), b = S[1][0] / a, cc = Math.sqrt(Math.max(1e-9, S[1][1] - b * b));
      for (let i = 0; i < cnt; i++) { const u = n(), v = n(); P.push({ x: m[0] + a * u, y: m[1] + b * u + cc * v, t }); }
    });
    return P;
  }
  const gpdf = (p, m, S) => {
    const det = S[0] * S[2] - S[1] * S[1], dx = p.x - m.x, dy = p.y - m.y;
    const q = (S[2] * dx * dx - 2 * S[1] * dx * dy + S[0] * dy * dy) / det;
    return Math.exp(-0.5 * q) / (2 * Math.PI * Math.sqrt(det));
  };
  function em(P, K, seed) {
    const r = rng(seed);
    let M = []; while (M.length < K) { const q = P[Math.floor(r() * P.length)]; if (!M.includes(q)) M.push(q); }
    M = M.map(q => ({ x: q.x, y: q.y }));
    let S = M.map(() => [1, 0, 1]), W = M.map(() => 1 / K);
    const H = [];
    for (let it = 0; it < 150; it++) {
      let ll = 0;
      const R = P.map(p => { const d = M.map((m, k) => W[k] * gpdf(p, m, S[k])); const s = d.reduce((a, b) => a + b, 0) || 1e-300; ll += Math.log(s); return d.map(v => v / s); });
      H.push({ M: M.map(m => ({ ...m })), S: S.map(s => s.slice()), W: W.slice(), R, ll });
      const nk = M.map((_, k) => R.reduce((a, q) => a + q[k], 0) + 1e-9);
      const NM = M.map((_, k) => ({ x: R.reduce((a, q, i) => a + q[k] * P[i].x, 0) / nk[k], y: R.reduce((a, q, i) => a + q[k] * P[i].y, 0) / nk[k] }));
      S = NM.map((m, k) => {
        let a = 0, b = 0, d = 0;
        P.forEach((p, i) => { const w = R[i][k], dx = p.x - m.x, dy = p.y - m.y; a += w * dx * dx; b += w * dx * dy; d += w * dy * dy; });
        return [a / nk[k] + 1e-3, b / nk[k], d / nk[k] + 1e-3];
      });
      W = nk.map(v => v / P.length);
      if (it > 0 && Math.abs(ll - H[it - 1].ll) < 1e-4) break;
      M = NM;
    }
    return H;
  }
  trace('mlgmm2d', {
    title: 'A Gaussian mixture in 2D: ellipses instead of circles',
    sub: 'Each cluster is a Gaussian with its own mean, its own shape and tilt (covariance), and its own weight. EM fits them all. The ellipses show where each Gaussian holds most of its points, and the colour strength shows how sure the model is.',
    W: 600, H: 330,
    params: [
      { k: 'data', label: 'Data', type: 'select', v: 'flat', opts: [['flat', 'Two long flat clusters'], ['tilted', 'A tilted and a tall cluster'], ['blobs', 'Three blobs of different size']] },
      { k: 'k', label: 'Number of components', type: 'range', v: 2, min: 1, max: 4, step: 1 },
      { k: 'seed', label: 'Random start', type: 'range', v: 5, min: 1, max: 12, step: 1 }
    ],
    tips: [
      { t: 'A tilted and a tall cluster: k-means could only cut them with a straight line between centres, but the ellipses follow each shape.', set: { data: 'tilted', k: 2, seed: 2 }, play: true },
      { t: 'Another random start on the flat clusters: EM crawls for many rounds and ends in a worse local maximum with a lower log likelihood. That is why GaussianMixture has n_init.', set: { data: 'flat', k: 2, seed: 2 }, play: true }
    ],
    frames(p) {
      const P = make(p.data), H = em(P, p.k, p.seed);
      const fr = [{ P, say: `${P.length} points. We fit a mixture of <b>${p.k}</b> Gaussian${p.k > 1 ? 's' : ''}, each with a mean, a 2 by 2 covariance (its shape and tilt) and a weight.` }];
      const show = H.length <= 10 ? H.map((_, i) => i) : [0, 1, 2, 3, 5, 8, 12, 18, 26, 40, 60, 90, 120, H.length - 1].filter((v, i, a) => v < H.length && a.indexOf(v) === i);
      show.forEach((i, j) => {
        const h = H[i];
        fr.push({ P, h, say: i === 0 ? `Start: ${p.k} means at random points, round covariances, equal weights. The colours are the first E step: each point’s colour mixes the components by probability. Log likelihood <b>${f2(h.ll, 1)}</b>.` : `Round ${i + 1}: the M step refitted each mean, covariance and weight, then the E step recomputed the probabilities. Log likelihood <b>${f2(h.ll, 1)}</b>${i > show[j - 1] + 1 ? ` (${i - show[j - 1] - 1 === 1 ? `round ${i}` : `rounds ${show[j - 1] + 2} to ${i}`} skipped here)` : ''}.` });
      });
      const L = H[H.length - 1];
      const unsure = L.R.filter(r => Math.max(...r) < 0.9).length;
      fr.push({ P, h: L, done: true, say: `${H.length < 150 ? 'Converged' : 'Stopped'} after ${H.length} rounds with log likelihood <b>${f2(L.ll, 1)}</b>. Weights: ${L.W.map(w => f2(w, 2)).join(', ')}. ${unsure} point${unsure === 1 ? ' is less than 90% sure of its' : 's are less than 90% sure of their'} component (pale colours), mostly where the ellipses overlap.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const P = plot(z, [10, 10, 400, 310], [-7, 7], [-4.2, 6.6], { dx: 0, dy: 0 });
      const mixc = r => { let R2 = 0, G2 = 0, B2 = 0; r.forEach((v, k) => { const h = klass(z, k).replace('#', ''); R2 += v * parseInt(h.slice(0, 2), 16); G2 += v * parseInt(h.slice(2, 4), 16); B2 += v * parseInt(h.slice(4, 6), 16); }); return `rgb(${R2 | 0},${G2 | 0},${B2 | 0})`; };
      f.P.forEach((q, i) => {
        const r = f.h ? f.h.R[i] : null, sure = r ? Math.max(...r) : 1;
        g.globalAlpha = r && r.length > 1 ? 0.35 + 0.65 * (sure - 1 / r.length) / (1 - 1 / r.length) : 1;
        D.circle(g, P.X(q.x), P.Y(q.y), 3.5, { fill: r && /^#/.test(klass(z, 0)) ? mixc(r) : r ? klass(z, r.indexOf(sure)) : c.ink2 });
        g.globalAlpha = 1;
      });
      if (f.h) f.h.M.forEach((m, k) => {
        const [a, b, d] = f.h.S[k], tr = a + d, dt = a * d - b * b, l1 = tr / 2 + Math.sqrt(Math.max(0, tr * tr / 4 - dt)), l2 = Math.max(1e-9, tr / 2 - Math.sqrt(Math.max(0, tr * tr / 4 - dt)));
        const th = Math.abs(b) < 1e-12 ? (a >= d ? 0 : Math.PI / 2) : Math.atan2(l1 - a, b);
        const v1 = [Math.cos(th), Math.sin(th)], v2 = [-Math.sin(th), Math.cos(th)];
        g.save(); g.beginPath();
        for (let i = 0; i <= 72; i++) { const t = 2 * Math.PI * i / 72, u = 2 * Math.sqrt(l1) * Math.cos(t), v = 2 * Math.sqrt(l2) * Math.sin(t); const X = P.X(m.x + u * v1[0] + v * v2[0]), Y = P.Y(m.y + u * v1[1] + v * v2[1]); i ? g.lineTo(X, Y) : g.moveTo(X, Y); }
        g.strokeStyle = klass(z, k); g.lineWidth = 2.4; g.stroke(); g.restore();
        D.circle(g, P.X(m.x), P.Y(m.y), 5, { fill: klass(z, k), stroke: c.ink, w: 1.5 });
      });
      head(z, 'Gaussian mixture', 425, 24);
      if (f.h) {
        D.text(g, `log likelihood ${f2(f.h.ll, 1)}`, 425, 50, { s: 13, b: true, c: c.cv });
        f.h.W.forEach((w, k) => D.text(g, `component ${k + 1}: weight ${f2(w, 2)}`, 425, 76 + 18 * k, { s: 12, mono: true, c: klass(z, k) }));
        D.text(g, 'ellipse = 2 standard deviations', 425, 250, { s: 11, c: c.ink2 });
        D.text(g, 'pale point = unsure', 425, 268, { s: 11, c: c.ink2 });
      }
    }
  });
})();
