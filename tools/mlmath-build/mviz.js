/* ===== Maths for Machine Learning: a small plotting kit (MV) and the worked example player =====
   MV.frame(w, h, xRange, yRange) maps maths coordinates to SVG pixels. axes, curve, arrow, dot and text
   return SVG strings that draw with CSS classes from the page styles, so light and dark themes both work.
   MV.drag(svg, F, handles, onMove) lets the reader drag points with a mouse or a finger. */
const MV = (() => {
  const { esc } = VIZ.kit;
  let defsDone = false;
  function defs() {
    if (defsDone) return;
    defsDone = true;
    const d = document.createElement('div');
    d.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
    d.innerHTML = `<svg aria-hidden="true" focusable="false"><defs>${['a', 'o', 'g', 'p', 'r', 'k'].map(c => `<marker id="mvah-${c}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="mv-ah ${c}"/></marker>`).join('')}</defs></svg>`;
    document.body.appendChild(d);
  }
  function frame(w, h, xr, yr, pad = 30) {
    const sx = x => pad + (x - xr[0]) / (xr[1] - xr[0]) * (w - 2 * pad);
    const sy = y => h - pad - (y - yr[0]) / (yr[1] - yr[0]) * (h - 2 * pad);
    const ix = px => xr[0] + (px - pad) / (w - 2 * pad) * (xr[1] - xr[0]);
    const iy = py => yr[0] + (h - pad - py) / (h - 2 * pad) * (yr[1] - yr[0]);
    return { w, h, xr, yr, pad, sx, sy, ix, iy };
  }
  const r2 = v => Math.round(v * 100) / 100;
  function niceStep(span) {
    const raw = span / 8, p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    return (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p;
  }
  function num(v, d = 2) {
    if (!isFinite(v)) return v > 0 ? '∞' : v < 0 ? '−∞' : '?';
    const s = (+v.toFixed(d)).toString();
    return s.replace('-', '−');
  }
  function axes(F, o = {}) {
    const xs = o.xstep || niceStep(F.xr[1] - F.xr[0]), ys = o.ystep || niceStep(F.yr[1] - F.yr[0]);
    let s = '';
    const x0 = Math.ceil(F.xr[0] / xs) * xs, y0 = Math.ceil(F.yr[0] / ys) * ys;
    for (let x = x0; x <= F.xr[1] + 1e-9; x += xs) s += `<line class="mv-grid" x1="${r2(F.sx(x))}" y1="${F.pad}" x2="${r2(F.sx(x))}" y2="${F.h - F.pad}"/>`;
    for (let y = y0; y <= F.yr[1] + 1e-9; y += ys) s += `<line class="mv-grid" x1="${F.pad}" y1="${r2(F.sy(y))}" x2="${F.w - F.pad}" y2="${r2(F.sy(y))}"/>`;
    const ax = Math.min(Math.max(0, F.yr[0]), F.yr[1]), ay = Math.min(Math.max(0, F.xr[0]), F.xr[1]);
    s += `<line class="mv-axis" x1="${F.pad}" y1="${r2(F.sy(ax))}" x2="${F.w - F.pad}" y2="${r2(F.sy(ax))}"/><line class="mv-axis" x1="${r2(F.sx(ay))}" y1="${F.pad}" x2="${r2(F.sx(ay))}" y2="${F.h - F.pad}"/>`;
    if (o.labels !== false) {
      for (let x = x0; x <= F.xr[1] + 1e-9; x += xs) if (Math.abs(x) > 1e-9) s += `<text class="mv-tick" x="${r2(F.sx(x))}" y="${r2(Math.min(F.h - 4, F.sy(ax) + 15))}" text-anchor="middle">${num(x, 2)}</text>`;
      for (let y = y0; y <= F.yr[1] + 1e-9; y += ys) if (Math.abs(y) > 1e-9) s += `<text class="mv-tick" x="${r2(Math.max(14, F.sx(ay) - 5))}" y="${r2(F.sy(y) + 4)}" text-anchor="end">${num(y, 2)}</text>`;
    }
    if (o.xl) s += `<text class="mv-lab sm" x="${F.w - F.pad}" y="${r2(F.sy(ax) - 6)}" text-anchor="end">${esc(o.xl)}</text>`;
    if (o.yl) s += `<text class="mv-lab sm" x="${r2(F.sx(ay) + 6)}" y="${F.pad + 10}">${esc(o.yl)}</text>`;
    return s;
  }
  function curve(F, f, cls = '', o = {}) {
    const n = o.n || 300, a = o.from !== undefined ? o.from : F.xr[0], b = o.to !== undefined ? o.to : F.xr[1];
    const lo = F.yr[0] - (F.yr[1] - F.yr[0]) * 2, hi = F.yr[1] + (F.yr[1] - F.yr[0]) * 2;
    let d = '', pen = false;
    for (let i = 0; i <= n; i++) {
      const x = a + (b - a) * i / n, y = f(x);
      if (!isFinite(y) || y < lo || y > hi) { pen = false; continue; }
      d += (pen ? 'L' : 'M') + r2(F.sx(x)) + ',' + r2(F.sy(y));
      pen = true;
    }
    return `<path class="mv-curve ${cls}" d="${d}"/>`;
  }
  function area(F, f, a, b, cls = '') {
    const n = 120;
    let d = `M${r2(F.sx(a))},${r2(F.sy(0))}`;
    for (let i = 0; i <= n; i++) { const x = a + (b - a) * i / n; d += `L${r2(F.sx(x))},${r2(F.sy(Math.max(F.yr[0], Math.min(F.yr[1], f(x)))))}`; }
    d += `L${r2(F.sx(b))},${r2(F.sy(0))}Z`;
    return `<path class="mv-fill ${cls}" d="${d}"/>`;
  }
  function arrow(F, x1, y1, x2, y2, c = 'a', extra = '') {
    const X1 = F.sx(x1), Y1 = F.sy(y1), X2 = F.sx(x2), Y2 = F.sy(y2), L = Math.hypot(X2 - X1, Y2 - Y1);
    if (L < 1) return '';
    const ux = (X2 - X1) / L, uy = (Y2 - Y1) / L, h = Math.min(13, L * 0.45), w = h * 0.5;
    const bx = X2 - ux * h, by = Y2 - uy * h;
    const col = c.split(' ')[0];
    return `<line class="mv-v ${c} ${extra}" x1="${r2(X1)}" y1="${r2(Y1)}" x2="${r2(bx + ux * 2)}" y2="${r2(by + uy * 2)}"/>` +
      `<polygon class="mv-ah ${col}" points="${r2(X2)},${r2(Y2)} ${r2(bx - uy * w)},${r2(by + ux * w)} ${r2(bx + uy * w)},${r2(by - ux * w)}"/>`;
  }
  function line(F, x1, y1, x2, y2, cls = 'mv-v k dash') {
    return `<line class="${cls}" x1="${r2(F.sx(x1))}" y1="${r2(F.sy(y1))}" x2="${r2(F.sx(x2))}" y2="${r2(F.sy(y2))}"/>`;
  }
  function dot(F, x, y, c = '', r = 6, attrs = '') {
    return `<circle class="mv-pt ${c}" cx="${r2(F.sx(x))}" cy="${r2(F.sy(y))}" r="${r}" ${attrs}/>`;
  }
  function text(F, x, y, t, o = {}) {
    return `<text class="mv-lab ${o.cls || ''}" x="${r2(F.sx(x) + (o.dx || 0))}" y="${r2(F.sy(y) + (o.dy || 0))}" text-anchor="${o.anchor || 'start'}">${esc(t)}</text>`;
  }
  function svg(F, inner, label) {
    defs();
    return `<svg class="mv-svg" viewBox="0 0 ${F.w} ${F.h}" role="img" aria-label="${esc(label || 'Interactive graph')}">${inner}</svg>`;
  }
  /* drag points: handles is a list of {get: () => [x, y], set: (x, y) => {}}; elements carry data-h="index" */
  function drag(svgEl, F, handles, onMove) {
    let active = -1;
    const pt = e => {
      const r = svgEl.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width * F.w, py = (e.clientY - r.top) / r.height * F.h;
      return [F.ix(px), F.iy(py)];
    };
    svgEl.addEventListener('pointerdown', e => {
      const t = e.target.closest('[data-h]');
      if (!t) return;
      active = +t.dataset.h;
      svgEl.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    svgEl.addEventListener('pointermove', e => {
      if (active < 0) return;
      const [x, y] = pt(e);
      handles[active].set(Math.max(F.xr[0], Math.min(F.xr[1], x)), Math.max(F.yr[0], Math.min(F.yr[1], y)));
      onMove();
    });
    const end = () => { active = -1; };
    svgEl.addEventListener('pointerup', end);
    svgEl.addEventListener('pointercancel', end);
  }
  const fmtv = (v, d = 2) => num(v, d);
  return { frame, axes, curve, area, arrow, line, dot, text, svg, drag, num: fmtv, niceStep };
})();

/* ----- a worked example that reveals one step at a time ----- */
(() => {
  const { shell, Player, $ } = VIZ.kit;
  VIZ.widgets.walk = el => {
    const steps = JSON.parse(el.dataset.steps || '[]');
    const b = shell(el, el.dataset.title || 'Worked example', el.dataset.sub || 'Press Play, or step through it one line at a time.');
    b.innerHTML = `<ol class="wk-steps">${steps.map(s => `<li>${s}</li>`).join('')}</ol><div class="vz-p"></div>`;
    const lis = [...b.querySelectorAll('.wk-steps li')];
    const P = Player($('.vz-p', b), i => lis.forEach((li, k) => { li.classList.toggle('on', k < i); li.classList.toggle('cur', k === i - 1); }), 1400);
    P.load(steps.length + 1, steps.length);  // starts fully shown, Play replays it from the first step
  };
})();
