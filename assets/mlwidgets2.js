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
    sub: 'Blue dots are training data, hollow dots are test data. Each step fits a polynomial of a higher degree to the training dots and shows both errors.',
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
      const fr = [{ tr, te, say: `Here are ${p.n} training points (blue) and 60 test points (hollow), all from the same smooth curve plus noise. The model only learns from the blue ones.` }];
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
