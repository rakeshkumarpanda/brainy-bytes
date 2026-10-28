/* ===== Computer Vision animations =====
   Every animation is declared with CVZ.def(name, spec). The framework draws the controls from spec.params,
   so every value the animation uses can be changed by the reader, and it lists spec.tips as "Try this"
   suggestions with a button that sets the suggested values.

   spec = {
     title, sub,                       heading and one line on what to look at
     W, H,                             the drawing size in canvas units (the canvas scales to the page width)
     params: [ { k, label, type: 'range' | 'select' | 'check' | 'text' | 'area', v, min, max, step, opts: [[value, label]], help, show(p) } ],
                                       show(p) is optional: the control is hidden while it returns false
     tips: [ { t: 'what to try and what you will see', set: { k: v }, play: true } ],
     steps(p) -> n                     optional: the animation has n steps, with Play, Step and Reset buttons
     draw(z) -> html                   draws on z.g and returns the readout html shown under the picture
     click(z, x, y)                    optional: the reader clicked the picture at canvas units x, y
   }
   z = { p: current values, step, n, g: 2D context, W, H, col: theme colours, set(values) }
   A lesson can give starting values: <div class="cvz" data-viz="name" data-cfg='{"k": v}'>. */
const CVZ = (() => {
  const REG = {};
  const live = [];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const def = (name, spec) => { REG[name] = spec; };

  function colours() {
    const cs = getComputedStyle(document.documentElement);
    const v = n => cs.getPropertyValue(n).trim();
    return {
      ink: v('--ink'), ink2: v('--ink2'), line: v('--line'), bg: v('--surface2'), surf: v('--surface'), cv: v('--cv') || '#0e7490',
      accent: v('--accent'), green: v('--green'), red: v('--red'), orange: v('--orange'), purple: v('--purple'), yellow: v('--yellow'), teal: v('--teal'), pink: v('--pink'),
      hl: v('--hl'), dark: document.documentElement.dataset.theme === 'dark' || (!document.documentElement.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches)
    };
  }

  function control(p, val) {
    const id = 'z' + Math.random().toString(36).slice(2, 9);
    const help = p.help ? `<small>${p.help}</small>` : '';
    if (p.type === 'select') return `<div class="z-p"><label for="${id}">${p.label}</label><select id="${id}" data-k="${p.k}">${p.opts.map(o => `<option value="${esc(o[0])}"${String(o[0]) === String(val) ? ' selected' : ''}>${esc(o[1])}</option>`).join('')}</select>${help}</div>`;
    if (p.type === 'check') return `<div class="z-p chk"><label><input type="checkbox" data-k="${p.k}"${val ? ' checked' : ''}>${p.label}</label>${help}</div>`;
    if (p.type === 'text') return `<div class="z-p"><label for="${id}">${p.label}</label><input id="${id}" type="text" data-k="${p.k}" value="${esc(val)}" spellcheck="false">${help}</div>`;
    if (p.type === 'area') return `<div class="z-p"><label for="${id}">${p.label}</label><textarea id="${id}" data-k="${p.k}" spellcheck="false">${esc(val)}</textarea>${help}</div>`;
    return `<div class="z-p"><label for="${id}"><span>${p.label}</span><output>${fmtv(p, val)}</output></label><input id="${id}" type="range" data-k="${p.k}" min="${p.min}" max="${p.max}" step="${p.step || 1}" value="${val}">${help}</div>`;
  }
  const fmtv = (p, v) => p.fmt ? p.fmt(+v) : (p.step && p.step < 1 ? (+v).toFixed(String(p.step).split('.')[1].length) : String(v));
  const readVal = (p, el) => p.type === 'check' ? el.checked : (p.type === 'range' || p.type === undefined) ? +el.value : (p.num ? +el.value : el.value);

  function mount(el) {
    if (el.dataset.on) return;
    const spec = REG[el.dataset.viz];
    if (!spec) { el.innerHTML = `<div class="z-head"><b>Missing animation ${esc(el.dataset.viz)}</b></div>`; return; }
    el.dataset.on = '1';
    let cfg = {};
    try { cfg = el.dataset.cfg ? JSON.parse(el.dataset.cfg) : {}; } catch (e) { /* bad config, use defaults */ }
    const p = {};
    (spec.params || []).forEach(q => { p[q.k] = cfg[q.k] !== undefined ? cfg[q.k] : q.v; });
    const z = { p, step: 0, n: 0, W: spec.W || 560, H: spec.H || 320, spec, el, state: {} };
    const stepped = !!spec.steps;
    el.innerHTML = `<div class="z-head"><b>${spec.title}</b><span>${spec.sub || ''}</span></div>
      <div class="z-body"><div class="z-stage"><div class="z-cwrap"><canvas></canvas></div>${stepped ? `<div class="z-ctl"><button type="button" class="play">Play</button><button type="button" class="stp">Step</button><button type="button" class="bk">Back</button><button type="button" class="rs">Reset</button><span class="z-pos"></span></div>` : ''}</div>
      <div class="z-panel">${(spec.params || []).map(q => control(q, p[q.k])).join('')}</div></div>
      <div class="z-read"></div>
      ${spec.tips && spec.tips.length ? `<div class="z-tips"><h4>Try this</h4><ol>${spec.tips.map((t, i) => `<li>${t.t}${t.set || t.play ? `<button type="button" data-tip="${i}">Set it</button>` : ''}</li>`).join('')}</ol></div>` : ''}`;
    const cv = el.querySelector('canvas');
    z.cv = cv;
    z.g = cv.getContext('2d');
    const size = () => {
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      cv.width = Math.round(z.W * dpr); cv.height = Math.round(z.H * dpr);
      z.g.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    size();
    let timer = null;
    const stopPlay = () => { if (timer) { clearInterval(timer); timer = null; } const b = el.querySelector('.z-ctl .play'); if (b) b.textContent = 'Play'; };
    function redraw() {
      (spec.params || []).forEach(q => { if (q.show) { const c = el.querySelector(`.z-panel [data-k="${q.k}"]`); if (c) c.closest('.z-p').hidden = !q.show(p); } });
      if (stepped) { z.n = spec.steps(z); if (z.step > z.n) z.step = z.n; }
      z.col = colours();
      z.g.save();
      z.g.clearRect(0, 0, z.W, z.H);
      z.g.font = '13px Nunito, system-ui, sans-serif';
      let html = '';
      try { html = spec.draw(z) || ''; } catch (e) { html = `<span class="bad">This animation hit an error: ${esc(e.message)}</span>`; console.error(e); }
      z.g.restore();
      el.querySelector('.z-read').innerHTML = html;
      if (stepped) el.querySelector('.z-pos').textContent = `Step ${z.step} of ${z.n}`;
    }
    z.redraw = redraw;
    z.set = vals => {
      Object.assign(p, vals);
      (spec.params || []).forEach(q => {
        if (!(q.k in vals)) return;
        const c = el.querySelector(`.z-panel [data-k="${q.k}"]`);
        if (!c) return;
        if (q.type === 'check') c.checked = !!p[q.k]; else c.value = p[q.k];
        const o = c.closest('.z-p').querySelector('output'); if (o) o.textContent = fmtv(q, p[q.k]);
      });
      if (stepped) { z.n = spec.steps(z); z.step = spec.startAtZero ? 0 : z.n; }
      redraw();
    };
    el.querySelector('.z-panel').addEventListener('input', e => {
      const c = e.target.closest('[data-k]');
      if (!c) return;
      const q = spec.params.find(x => x.k === c.dataset.k);
      p[q.k] = readVal(q, c);
      const o = c.closest('.z-p').querySelector('output'); if (o) o.textContent = fmtv(q, p[q.k]);
      stopPlay();
      if (stepped) { z.n = spec.steps(z); z.step = spec.startAtZero ? 0 : z.n; }
      if (spec.change) spec.change(z, q.k);
      redraw();
    });
    function play() {
      if (timer) { stopPlay(); return; }
      if (z.step >= z.n) z.step = 0;
      el.querySelector('.z-ctl .play').textContent = 'Pause';
      redraw();
      timer = setInterval(() => {
        if (!el.isConnected || z.step >= z.n) { stopPlay(); return; }
        z.step++; redraw();
      }, spec.speed ? spec.speed(z) : 700);
    }
    if (stepped) {
      el.querySelector('.z-ctl .play').onclick = play;
      el.querySelector('.z-ctl .stp').onclick = () => { stopPlay(); if (z.step < z.n) z.step++; redraw(); };
      el.querySelector('.z-ctl .bk').onclick = () => { stopPlay(); if (z.step > 0) z.step--; redraw(); };
      el.querySelector('.z-ctl .rs').onclick = () => { stopPlay(); z.step = 0; redraw(); };
    }
    el.querySelectorAll('[data-tip]').forEach(b => b.onclick = () => {
      const t = spec.tips[+b.dataset.tip];
      stopPlay();
      if (t.set) z.set(t.set);
      if (t.play && stepped) { z.step = 0; play(); }
    });
    if (spec.click) {
      const at = e => { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) * z.W / r.width, (e.clientY - r.top) * z.H / r.height]; };
      cv.addEventListener('pointerdown', e => { const [x, y] = at(e); spec.click(z, x, y, 'down'); redraw(); });
      cv.addEventListener('pointermove', e => { if (e.buttons !== 1) return; const [x, y] = at(e); spec.click(z, x, y, 'move'); redraw(); });
      cv.style.cursor = 'crosshair';
    }
    if (spec.init) spec.init(z);
    if (stepped) { z.n = spec.steps(z); z.step = spec.startAtZero ? 0 : z.n; }
    redraw();
    live.push(z);
  }
  function mountAll(root = document) { root.querySelectorAll('.cvz[data-viz]').forEach(mount); }
  new MutationObserver(() => live.forEach(z => z.el.isConnected && z.redraw())).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => live.forEach(z => z.redraw()));

  /* ---------- drawing helpers ---------- */
  const D = {
    text(g, s, x, y, o = {}) {
      g.save();
      g.fillStyle = o.c || g.fillStyle;
      g.font = `${o.b ? '800 ' : '600 '}${o.s || 13}px ${o.mono ? '"JetBrains Mono", monospace' : 'Nunito, system-ui, sans-serif'}`;
      g.textAlign = o.a || 'left'; g.textBaseline = o.bl || 'alphabetic';
      g.fillText(s, x, y);
      g.restore();
    },
    line(g, x1, y1, x2, y2, c, w = 1.5, dash) {
      g.save(); g.strokeStyle = c; g.lineWidth = w; if (dash) g.setLineDash(dash);
      g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); g.restore();
    },
    arrow(g, x1, y1, x2, y2, c, w = 2, head = 7) {
      const a = Math.atan2(y2 - y1, x2 - x1), L = Math.hypot(x2 - x1, y2 - y1);
      if (L < 0.5) return;
      const h = Math.min(head, L * 0.6);
      g.save(); g.strokeStyle = c; g.fillStyle = c; g.lineWidth = w;
      g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2 - Math.cos(a) * h * 0.6, y2 - Math.sin(a) * h * 0.6); g.stroke();
      g.beginPath(); g.moveTo(x2, y2); g.lineTo(x2 - h * Math.cos(a - 0.45), y2 - h * Math.sin(a - 0.45)); g.lineTo(x2 - h * Math.cos(a + 0.45), y2 - h * Math.sin(a + 0.45)); g.closePath(); g.fill();
      g.restore();
    },
    rect(g, x, y, w, h, o = {}) {
      g.save();
      if (o.fill) { g.fillStyle = o.fill; g.fillRect(x, y, w, h); }
      if (o.stroke) { g.strokeStyle = o.stroke; g.lineWidth = o.w || 1.5; if (o.dash) g.setLineDash(o.dash); g.strokeRect(x, y, w, h); }
      g.restore();
    },
    circle(g, x, y, r, o = {}) {
      g.save(); g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2);
      if (o.fill) { g.fillStyle = o.fill; g.fill(); }
      if (o.stroke) { g.strokeStyle = o.stroke; g.lineWidth = o.w || 1.5; g.stroke(); }
      g.restore();
    },
    /* a grey or colour image (array of rows) drawn as square cells, with optional values written inside */
    image(g, img, x, y, cell, o = {}) {
      const h = img.length, w = img[0].length;
      for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) {
        const v = img[r][c];
        g.fillStyle = Array.isArray(v) ? `rgb(${v[0]},${v[1]},${v[2]})` : `rgb(${v},${v},${v})`;
        g.fillRect(x + c * cell, y + r * cell, Math.ceil(cell), Math.ceil(cell));
      }
      if (o.grid) {
        g.save(); g.strokeStyle = o.grid; g.lineWidth = 1;
        for (let r = 0; r <= h; r++) { g.beginPath(); g.moveTo(x, y + r * cell); g.lineTo(x + w * cell, y + r * cell); g.stroke(); }
        for (let c = 0; c <= w; c++) { g.beginPath(); g.moveTo(x + c * cell, y); g.lineTo(x + c * cell, y + h * cell); g.stroke(); }
        g.restore();
      }
      if (o.vals) {
        for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) {
          const v = img[r][c], lum = Array.isArray(v) ? (v[0] * 0.299 + v[1] * 0.587 + v[2] * 0.114) : v;
          D.text(g, o.vals === true ? String(Array.isArray(v) ? '' : Math.round(v)) : o.vals(v, r, c), x + (c + 0.5) * cell, y + (r + 0.5) * cell + 1,
            { a: 'center', bl: 'middle', s: o.fs || Math.max(8, Math.min(13, cell * 0.36)), c: lum > 128 ? '#0b1a2e' : '#ffffff', mono: true });
        }
      }
    },
    /* simple x-y plot area. Returns functions that map data to canvas units */
    axes(g, z, box, xr, yr, o = {}) {
      const [X, Y, Wd, Ht] = box;
      const sx = v => X + (v - xr[0]) / (xr[1] - xr[0]) * Wd;
      const sy = v => Y + Ht - (v - yr[0]) / (yr[1] - yr[0]) * Ht;
      g.save();
      g.strokeStyle = z.col.line; g.lineWidth = 1;
      g.strokeRect(X, Y, Wd, Ht);
      const tick = (a, b, n) => { const out = []; for (let i = 0; i <= n; i++) out.push(a + (b - a) * i / n); return out; };
      tick(xr[0], xr[1], o.nx || 4).forEach(v => { D.line(g, sx(v), Y + Ht, sx(v), Y + Ht + 4, z.col.ink2, 1); D.text(g, o.fx ? o.fx(v) : (+v.toFixed(2)).toString(), sx(v), Y + Ht + 16, { a: 'center', s: 11, c: z.col.ink2 }); });
      tick(yr[0], yr[1], o.ny || 4).forEach(v => { D.line(g, X - 4, sy(v), X, sy(v), z.col.ink2, 1); D.text(g, o.fy ? o.fy(v) : (+v.toFixed(2)).toString(), X - 6, sy(v) + 4, { a: 'right', s: 11, c: z.col.ink2 }); });
      if (o.xl) D.text(g, o.xl, X + Wd / 2, Y + Ht + 30, { a: 'center', s: 12, c: z.col.ink2, b: true });
      if (o.yl) { g.save(); g.translate(X - 36, Y + Ht / 2); g.rotate(-Math.PI / 2); D.text(g, o.yl, 0, 0, { a: 'center', s: 12, c: z.col.ink2, b: true }); g.restore(); }
      g.restore();
      return { sx, sy };
    },
    curve(g, f, xr, m, c, w = 2, n = 200, dash) {
      g.save(); g.strokeStyle = c; g.lineWidth = w; if (dash) g.setLineDash(dash); g.beginPath();
      let first = true;
      for (let i = 0; i <= n; i++) {
        const x = xr[0] + (xr[1] - xr[0]) * i / n, y = f(x);
        if (!isFinite(y)) { first = true; continue; }
        if (first) { g.moveTo(m.sx(x), m.sy(y)); first = false; } else g.lineTo(m.sx(x), m.sy(y));
      }
      g.stroke(); g.restore();
    },
    bars(g, z, box, vals, o = {}) {
      const [X, Y, Wd, Ht] = box;
      const mx = o.max || Math.max(1e-9, ...vals);
      const bw = Wd / vals.length;
      vals.forEach((v, i) => {
        const h = Math.max(0, v / mx) * Ht;
        g.fillStyle = o.colour ? o.colour(i, v) : z.col.cv;
        g.fillRect(X + i * bw + (o.gap ?? 0.5), Y + Ht - h, Math.max(1, bw - 2 * (o.gap ?? 0.5)), h);
      });
      g.strokeStyle = z.col.line; g.lineWidth = 1; g.strokeRect(X, Y, Wd, Ht);
    },
    box(g, b, c, label, w = 2.5, dash) {
      D.rect(g, b[0], b[1], b[2], b[3], { stroke: c, w, dash });
      if (label) {
        g.save(); g.font = '800 12px Nunito, system-ui, sans-serif';
        const tw = g.measureText(label).width + 8;
        g.fillStyle = c; g.fillRect(b[0] - w / 2, b[1] - 17, tw, 17);
        g.fillStyle = '#fff'; g.textBaseline = 'middle'; g.fillText(label, b[0] + 4 - w / 2, b[1] - 8);
        g.restore();
      }
    }
  };

  /* ---------- image helpers: a synthetic scene, filters and noise ---------- */
  function rng(seed) {
    let a = seed >>> 0;
    return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  function gauss(r) { let u = 0, v = 0; while (u === 0) u = r(); while (v === 0) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  const clamp = (v, a = 0, b = 255) => v < a ? a : v > b ? b : v;
  /* a small outdoor picture: sky, sun, house with a window and door, a tree and a road. Colour [r,g,b] per pixel */
  function sceneRGB(w, h) {
    const img = [];
    for (let y = 0; y < h; y++) {
      const row = [];
      for (let x = 0; x < w; x++) {
        const u = x / w, v = y / h;
        let c;
        if (v < 0.62) c = [120 + 80 * v, 170 + 60 * v, 235];
        else c = [90 - 30 * (v - 0.62), 150 - 40 * (v - 0.62), 70];
        if (Math.hypot(u - 0.82, v - 0.18) < 0.09) c = [255, 214, 90];
        if (u > 0.2 && u < 0.5 && v > 0.42 && v < 0.72) c = [214, 120, 80];
        if (v > 0.24 && v <= 0.42 && Math.abs(u - 0.35) < (v - 0.24) * 0.95) c = [150, 50, 50];
        if (u > 0.25 && u < 0.32 && v > 0.48 && v < 0.56) c = [250, 240, 160];
        if (u > 0.38 && u < 0.45 && v > 0.56 && v < 0.72) c = [90, 55, 35];
        if (u > 0.66 && u < 0.7 && v > 0.48 && v < 0.74) c = [110, 70, 40];
        if (Math.hypot((u - 0.68) * 1.2, v - 0.42) < 0.12) c = [40, 130, 60];
        if (v > 0.78 && Math.abs(u - 0.5 - (v - 0.78) * 0.4) < 0.08 + (v - 0.78) * 0.5) c = [80, 80, 90];
        row.push(c.map(t => Math.round(clamp(t))));
      }
      img.push(row);
    }
    return img;
  }
  const toGray = img => img.map(r => r.map(c => Math.round(0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2])));
  const sceneGray = (w, h) => toGray(sceneRGB(w, h));
  function pad(img, r, c, mode) {
    const h = img.length, w = img[0].length;
    if (r >= 0 && r < h && c >= 0 && c < w) return img[r][c];
    if (mode === 'zero') return 0;
    if (mode === 'reflect') { const rr = r < 0 ? -r - 1 : r >= h ? 2 * h - r - 1 : r, cc = c < 0 ? -c - 1 : c >= w ? 2 * w - c - 1 : c; return img[clamp(rr, 0, h - 1)][clamp(cc, 0, w - 1)]; }
    return img[clamp(r, 0, h - 1)][clamp(c, 0, w - 1)];
  }
  function convolve(img, k, mode = 'replicate', noClamp) {
    const h = img.length, w = img[0].length, kh = k.length, kw = k[0].length, oy = kh >> 1, ox = kw >> 1;
    const out = [];
    for (let y = 0; y < h; y++) {
      const row = [];
      for (let x = 0; x < w; x++) {
        let s = 0;
        for (let i = 0; i < kh; i++) for (let j = 0; j < kw; j++) s += k[i][j] * pad(img, y + i - oy, x + j - ox, mode);
        row.push(noClamp ? s : clamp(Math.round(s)));
      }
      out.push(row);
    }
    return out;
  }
  function gaussKernel(n, sigma) {
    if (!(sigma > 0)) sigma = 0.3 * ((n - 1) * 0.5 - 1) + 0.8;  /* the OpenCV rule when sigma is 0 */
    const r = n >> 1, k = [];
    let s = 0;
    for (let i = -r; i <= r; i++) { const row = []; for (let j = -r; j <= r; j++) { const v = Math.exp(-(i * i + j * j) / (2 * sigma * sigma)); row.push(v); s += v; } k.push(row); }
    return k.map(row => row.map(v => v / s));
  }
  function median(img, n) {
    const h = img.length, w = img[0].length, r = n >> 1;
    return img.map((row, y) => row.map((_, x) => {
      const a = [];
      for (let i = -r; i <= r; i++) for (let j = -r; j <= r; j++) a.push(pad(img, y + i, x + j, 'replicate'));
      a.sort((p, q) => p - q);
      return a[a.length >> 1];
    }));
  }
  function noisy(img, type, amt, seed = 7) {
    const r = rng(seed);
    return img.map(row => row.map(v => {
      if (type === 'gaussian') return clamp(Math.round(v + gauss(r) * amt));
      if (type === 'saltpepper') { const u = r(); return u < amt / 200 ? 0 : u > 1 - amt / 200 ? 255 : v; }
      if (type === 'speckle') return clamp(Math.round(v * (1 + gauss(r) * amt / 100)));
      if (type === 'poisson') { const lam = v * amt / 50 + 1e-6; let k = 0, p = 1, L = Math.exp(-Math.min(lam, 700)); if (lam > 60) return clamp(Math.round((lam + gauss(r) * Math.sqrt(lam)) * 50 / amt)); do { k++; p *= r(); } while (p > L); return clamp(Math.round((k - 1) * 50 / amt)); }
      return v;
    }));
  }
  function psnr(a, b) {
    let s = 0, n = 0;
    a.forEach((row, y) => row.forEach((v, x) => { const d = v - b[y][x]; s += d * d; n++; }));
    const mse = s / n;
    return mse === 0 ? Infinity : 10 * Math.log10(255 * 255 / mse);
  }
  function hist(img, bins = 256, L = 256) {
    const hgt = new Array(bins).fill(0);
    img.forEach(row => row.forEach(v => { hgt[Math.min(bins - 1, Math.floor(v * bins / L))]++; }));
    return hgt;
  }
  const SOBEL_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], SOBEL_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]];
  function sobel(img) {
    const gx = convolve(img, SOBEL_X, 'replicate', true), gy = convolve(img, SOBEL_Y, 'replicate', true);
    return { gx, gy, mag: gx.map((r, y) => r.map((v, x) => Math.hypot(v, gy[y][x]))), ang: gx.map((r, y) => r.map((v, x) => Math.atan2(gy[y][x], v))) };
  }
  function parseGrid(s) {
    return String(s).trim().split(/\n|\|/).map(r => r.trim().split(/[\s,]+/).filter(Boolean).map(Number)).filter(r => r.length);
  }
  const iou = (a, b) => {
    const x1 = Math.max(a[0], b[0]), y1 = Math.max(a[1], b[1]), x2 = Math.min(a[0] + a[2], b[0] + b[2]), y2 = Math.min(a[1] + a[3], b[1] + b[3]);
    const inter = Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
    return { inter, union: a[2] * a[3] + b[2] * b[3] - inter, iou: inter / (a[2] * a[3] + b[2] * b[3] - inter || 1) };
  };
  const f = (v, d = 3) => (Math.round(v * 10 ** d) / 10 ** d).toString();

  return { def, mount, mountAll, D, rng, gauss, clamp, sceneRGB, sceneGray, toGray, convolve, gaussKernel, median, noisy, psnr, hist, sobel, parseGrid, iou, f, esc, REG };
})();
