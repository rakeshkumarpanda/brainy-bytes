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
