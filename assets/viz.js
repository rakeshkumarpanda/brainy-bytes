/* ===== Step animations for the lesson pages =====
   The same player and diagram engine the DSA, TestNG and Complete Java Session pages carry inline.
   <div class="viz" data-viz="flow" data-k="key"></div> becomes a live diagram when VIZ.mountAll(root) runs.
   Every widget draws with CSS classes from viz.css, so light and dark themes both work. */
const VIZ = (() => {
  const W = {};
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const $ = (s, r) => r.querySelector(s);
  const fmt = n => Number(n).toLocaleString('en-US');

  function shell(el, title, sub) {
    el.innerHTML = `<div class="vz"><div class="vz-head"><span class="vz-badge">🎬 Try it</span><h3>${title}</h3><p>${sub}</p></div><div class="vz-body"></div></div>`;
    return $('.vz-body', el);
  }
  function seg(name, items, on) {
    return `<div class="vz-seg" role="group" data-seg="${name}">${items.map(([v, t]) => `<button type="button" data-v="${esc(v)}"${String(v) === String(on) ? ' class="on"' : ''}>${t}</button>`).join('')}</div>`;
  }
  function wireSeg(root, name, cb) {
    const g = $(`[data-seg="${name}"]`, root);
    g.addEventListener('click', e => {
      const b = e.target.closest('button');
      if (!b) return;
      g.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
      cb(b.dataset.v);
    });
  }
  function slider(name, label, min, max, val, step = 1) {
    return `<label class="vz-sl">${label} <input type="range" data-sl="${name}" min="${min}" max="${max}" step="${step}" value="${val}"> <b data-slv="${name}">${val}</b></label>`;
  }
  function wireSlider(root, name, cb) {
    const s = $(`[data-sl="${name}"]`, root), v = $(`[data-slv="${name}"]`, root);
    s.addEventListener('input', () => { v.textContent = s.value; cb(+s.value); });
  }

  /* ----- a step player: ⏮ ◀ ▶ ▶ ⏭ with a scrubber and speed ----- */
  function Player(host, show, ms = 700) {
    host.innerHTML = `<div class="vz-ctl"><button type="button" data-a="reset" title="Go to the start" aria-label="Go to the start">⏮</button><button type="button" data-a="back" title="Step back" aria-label="Step back">◀</button><button type="button" data-a="play" class="vz-play">▶ Play</button><button type="button" data-a="fwd" title="Step forward" aria-label="Step forward">▶</button><button type="button" data-a="end" title="Go to the end" aria-label="Go to the end">⏭</button><input type="range" min="0" max="0" value="0" aria-label="Animation position"><span class="vz-cnt">0 / 0</span><select aria-label="Speed"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option><option value="4">4×</option></select></div>`;
    const range = $('input', host), cnt = $('.vz-cnt', host), pb = $('.vz-play', host), sp = $('select', host);
    let n = 1, i = 0, timer = null;
    const go = j => { i = clamp(j, 0, n - 1); range.value = i; cnt.textContent = `${i} / ${n - 1}`; show(i); };
    const pause = () => { clearTimeout(timer); timer = null; pb.textContent = '▶ Play'; };
    const tick = () => { if (i >= n - 1) { pause(); return; } go(i + 1); timer = setTimeout(tick, ms / +sp.value); };
    const play = () => { if (i >= n - 1) go(0); pb.textContent = '⏸ Pause'; timer = setTimeout(tick, 250); };
    host.addEventListener('click', e => {
      const a = (e.target.closest('button') || {}).dataset;
      if (!a || !a.a) return;
      if (a.a === 'play') { timer ? pause() : play(); return; }
      pause();
      if (a.a === 'reset') go(0); else if (a.a === 'back') go(i - 1); else if (a.a === 'fwd') go(i + 1); else if (a.a === 'end') go(n - 1);
    });
    range.addEventListener('input', () => { pause(); go(+range.value); });
    return { load(N, start = 0) { pause(); n = Math.max(1, N); range.max = n - 1; go(start); }, pause, play, get i() { return i; }, get n() { return n; } };
  }

  /* a cancellable timed sequence for one-shot operations */
  function Seq() {
    let t = [];
    return {
      run(steps, delay = 520) { this.stop(); steps.forEach((f, k) => t.push(setTimeout(f, k * delay))); },
      stop() { t.forEach(clearTimeout); t = []; }
    };
  }
  const cell = (v, cls = '', sub = '') => `<div class="vz-cell ${cls}">${v === null || v === undefined ? '' : esc(v)}${sub !== '' ? `<small>${esc(sub)}</small>` : ''}</div>`;

  function mountAll(root) {
    root.querySelectorAll('.viz[data-viz]:not(.vz-done)').forEach(el => {
      const f = W[el.dataset.viz];
      el.classList.add('vz-done');
      if (f) f(el); else el.textContent = 'Unknown animation: ' + el.dataset.viz;
    });
  }
  return { mountAll, refresh() { /* drawn with CSS classes, nothing to redraw */ }, widgets: W, kit: { esc, clamp, $, fmt, shell, seg, wireSeg, slider, wireSlider, Player, Seq, cell } };
})();

/* ===== Diagram engine: clean, theme aware SVG diagrams with an optional step by step story =====
   <div class="viz" data-viz="flow" data-k="key"></div> draws PAGE.dg[key].
   Spec:
     t, s        title and one line description
     w, h        size of the drawing in SVG units
     n           nodes: [id, x, y, w, h, label, {c: tone 0-5, sh: shape, ic: emoji, sub: small text, i: info shown on click}]
                 shapes: box (default), pill, circle, diamond, doc, db, actor, note, screen, plain
     g           frames: [x, y, w, h, label, tone]
     e           arrows: [from, to, {t: label, d: dashed, via: [[x, y]...], c: tone, bi: both ends, id, fs/ts: 'l'|'r'|'t'|'b' side}]
     tx          free text: [x, y, text, {a: anchor, c: tone, b: bold, s: size}]
     st          steps: [[ids of nodes, arrows ('a>b' or id) and frames ('g0', 'g1'...)], message]
   Without steps the diagram is static and each node with an info text explains itself when clicked. */
(() => {
  const K = VIZ.kit, W = VIZ.widgets;
  const esc = K.esc;
  const STROKE = ['var(--orange)', 'var(--green)', 'var(--blue)', 'var(--purple)', 'var(--pink)', 'var(--hl-line)', 'var(--red)', 'var(--teal)'];
  const FILL = ['var(--g0)', 'var(--g1)', 'var(--g2)', 'var(--g3)', 'var(--g4)', 'var(--g5)', 'var(--bad)', 'var(--win)'];

  function lines(text, x, y, size, anchor, cls) {
    const ls = String(text).split('\n');
    const lh = size * 1.22, y0 = y - (ls.length - 1) * lh / 2;
    return `<text class="${cls}" x="${x}" y="${y0}" text-anchor="${anchor}" font-size="${size}" dominant-baseline="middle">${ls.map((l, k) => `<tspan x="${x}" dy="${k ? lh : 0}">${esc(l)}</tspan>`).join('')}</text>`;
  }

  function nodeSvg(nd) {
    const [id, x, y, w, h, label, o = {}] = nd;
    const sh = o.sh || 'box', c = o.c === undefined ? 2 : o.c;
    const st = `stroke="${STROKE[c]}" fill="${FILL[c]}"`;
    const cx = x + w / 2, cy = y + h / 2;
    let s = '', ly = cy, lx = cx, anchor = 'middle';
    if (sh === 'box') s = `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" ${st}/>`;
    else if (sh === 'pill') s = `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${h / 2}" ${st}/>`;
    else if (sh === 'circle') s = `<ellipse cx="${cx}" cy="${cy}" rx="${w / 2}" ry="${h / 2}" ${st}/>`;
    else if (sh === 'diamond') s = `<polygon points="${cx},${y} ${x + w},${cy} ${cx},${y + h} ${x},${cy}" ${st}/>`;
    else if (sh === 'note') s = `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" stroke="var(--hl-line)" fill="var(--hl)"/>`;
    else if (sh === 'doc') {
      const f = Math.min(16, w / 5);
      s = `<path d="M${x} ${y + 4} q0 -4 4 -4 H${x + w - f} L${x + w} ${y + f} V${y + h - 4} q0 4 -4 4 H${x + 4} q-4 0 -4 -4 Z" ${st}/><path d="M${x + w - f} ${y} V${y + f} H${x + w}" fill="none" stroke="${STROKE[c]}"/>`;
    } else if (sh === 'db') {
      const e = Math.min(10, h / 5);
      s = `<path d="M${x} ${y + e} V${y + h - e} A${w / 2} ${e} 0 0 0 ${x + w} ${y + h - e} V${y + e}" ${st}/><ellipse cx="${cx}" cy="${y + e}" rx="${w / 2}" ry="${e}" ${st}/>`;
      ly = cy + e / 2;
    } else if (sh === 'screen') {
      s = `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" ${st}/><path d="M${x} ${y + 20} H${x + w}" stroke="${STROKE[c]}"/><circle cx="${x + 10}" cy="${y + 10}" r="3" fill="${STROKE[c]}"/><circle cx="${x + 20}" cy="${y + 10}" r="3" fill="${STROKE[c]}"/>`;
      ly = y + 20 + (h - 20) / 2;
    } else if (sh === 'actor') {
      const r = Math.min(w, h) * 0.16, hx = cx, hy = y + r + 2;
      s = `<circle cx="${hx}" cy="${hy}" r="${r}" ${st}/><path d="M${hx} ${hy + r} V${hy + r * 3.2} M${hx - r * 1.6} ${hy + r * 1.9} H${hx + r * 1.6} M${hx} ${hy + r * 3.2} L${hx - r * 1.3} ${hy + r * 5} M${hx} ${hy + r * 3.2} L${hx + r * 1.3} ${hy + r * 5}" stroke="${STROKE[c]}" stroke-width="2.4" fill="none" stroke-linecap="round"/>`;
      ly = y + h - 8;
    }
    const ic = o.ic ? `<text x="${sh === 'plain' ? cx : x + 8}" y="${y + 13}" font-size="13" dominant-baseline="middle" text-anchor="${sh === 'plain' ? 'middle' : 'start'}">${o.ic}</text>` : '';
    const size = o.fs || (h < 34 ? 12 : 13);
    let txt = '';
    if (label) {
      const hasSub = o.sub && sh !== 'actor';
      txt = lines(label, lx, hasSub ? ly - 8 : ly, size, anchor, 'fg-l');
      if (hasSub) txt += lines(o.sub, lx, ly + 10 + (String(label).split('\n').length - 1) * 7, 10.5, anchor, 'fg-s');
      else if (o.sub) txt += lines(o.sub, lx, ly + 13, 10.5, anchor, 'fg-s');
    }
    return `<g class="fg-n${o.i ? ' fg-click' : ''}" data-id="${esc(id)}">${s}${ic}${txt}</g>`;
  }

  /* where the line from the centre of a node towards point p leaves the node */
  function anchor(nd, p, side) {
    const [, x, y, w, h, , o = {}] = nd;
    const cx = x + w / 2, cy = y + h / 2;
    if (side) return { l: [x, cy], r: [x + w, cy], t: [cx, y], b: [cx, y + h] }[side];
    const dx = p[0] - cx, dy = p[1] - cy;
    if (!dx && !dy) return [cx, cy];
    const sh = o.sh || 'box';
    if (sh === 'circle' || sh === 'actor') {
      const a = Math.atan2(dy, dx);
      return [cx + Math.cos(a) * w / 2, cy + Math.sin(a) * h / 2];
    }
    if (sh === 'diamond') {
      const t = 1 / (Math.abs(dx) / (w / 2) + Math.abs(dy) / (h / 2));
      return [cx + dx * t, cy + dy * t];
    }
    const t = Math.min(dx ? (w / 2) / Math.abs(dx) : Infinity, dy ? (h / 2) / Math.abs(dy) : Infinity);
    return [cx + dx * t, cy + dy * t];
  }

  function edgeSvg(e, N, k) {
    const [a, b, o = {}] = e;
    const A = N[a], B = N[b];
    if (!A || !B) throw new Error('diagram arrow refers to a missing node: ' + a + ' > ' + b);
    const ca = [A[1] + A[3] / 2, A[2] + A[4] / 2], cb = [B[1] + B[3] / 2, B[2] + B[4] / 2];
    const via = o.via || [];
    const p0 = anchor(A, via[0] || cb, o.fs), p1 = anchor(B, via[via.length - 1] || ca, o.ts);
    const pts = [p0, ...via, p1];
    let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
    if (o.cv && !via.length) {
      const mx = (p0[0] + p1[0]) / 2, my = (p0[1] + p1[1]) / 2, dx = p1[0] - p0[0], dy = p1[1] - p0[1], L = Math.hypot(dx, dy) || 1;
      const qx = mx - dy / L * o.cv, qy = my + dx / L * o.cv;
      d += ` Q${qx.toFixed(1)} ${qy.toFixed(1)} ${p1[0].toFixed(1)} ${p1[1].toFixed(1)}`;
      pts.splice(1, 0, [(mx + qx) / 2, (my + qy) / 2]);
    } else for (let i = 1; i < pts.length; i++) d += ` L${pts[i][0].toFixed(1)} ${pts[i][1].toFixed(1)}`;
    const c = o.c === undefined ? null : o.c;
    const col = c === null ? 'var(--ink2)' : STROKE[c];
    const id = o.id || `${a}>${b}`;
    let lab = '';
    if (o.t) {
      const m = Math.floor((pts.length - 1) / 2), q = pts[m], r = pts[m + 1] || q;
      const lx = o.tx !== undefined ? o.tx : (q[0] + r[0]) / 2, ly = o.ty !== undefined ? o.ty : (q[1] + r[1]) / 2;
      const ls = String(o.t).split('\n'), wd = Math.max(...ls.map(l => l.length)) * 6.2 + 10, ht = ls.length * 13 + 4;
      lab = `<rect class="fg-lb" x="${lx - wd / 2}" y="${ly - ht / 2}" width="${wd}" height="${ht}" rx="6"/>${lines(o.t, lx, ly, 11, 'middle', 'fg-el')}`;
    }
    return [`<g class="fg-e${o.d ? ' dash' : ''}" data-id="${esc(id)}"><path d="${d}" fill="none" stroke="${col}" marker-end="url(#fgA${k})"${o.bi ? ` marker-start="url(#fgB${k})"` : ''}/></g>`,
      lab ? `<g class="fg-e fg-elab" data-id="${esc(id)}">${lab}</g>` : ''];
  }

  let uid = 0;
  function draw(spec) {
    const k = ++uid;
    const N = {};
    (spec.n || []).forEach(n => { N[n[0]] = n; });
    const defs = `<defs><marker id="fgA${k}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="context-stroke"/></marker><marker id="fgB${k}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="context-stroke"/></marker></defs>`;
    const groups = (spec.g || []).map((g, i) => {
      const [x, y, w, h, t, c = 2] = g;
      return `<g class="fg-g" data-id="g${i}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14" stroke="${STROKE[c]}" fill="${FILL[c]}"/>${t ? `<text class="fg-gt" x="${x + 12}" y="${y + 16}" font-size="12.5" dominant-baseline="middle" fill="${STROKE[c]}">${esc(t)}</text>` : ''}</g>`;
    }).join('');
    const ES = (spec.e || []).map(e => edgeSvg(e, N, k));
    const edges = ES.map(x => x[0]).join(''), elabs = ES.map(x => x[1]).join('');
    const nodes = (spec.n || []).map(nodeSvg).join('');
    const texts = (spec.tx || []).map(([x, y, t, o = {}]) => lines(t, x, y, o.s || 12, o.a || 'middle', 'fg-t' + (o.b ? ' b' : '')).replace('<text ', `<text ${o.c !== undefined ? `fill="${STROKE[o.c]}" ` : ''}`)).join('');
    const mw = Math.min(spec.w, spec.mw || 640);
    return `<svg class="fg-svg" viewBox="0 0 ${spec.w} ${spec.h}" style="min-width:${mw}px; max-width:${spec.w * 1.25}px" role="img" aria-label="${esc(spec.t)}">${defs}${groups}${edges}${nodes}${elabs}${texts}</svg>`;
  }

  W.flow = el => {
    const spec = (typeof PAGE !== 'undefined' && PAGE.dg && PAGE.dg[el.dataset.k]) || null;
    if (!spec) { el.textContent = 'Missing diagram ' + el.dataset.k; return; }
    const steps = spec.st || [];
    const b = K.shell(el, spec.t, spec.s || (steps.length ? 'Press Play, or step with the arrows, to follow the story one stage at a time.' : 'Click a box to read what it does.'));
    el.querySelector('.vz-badge').textContent = steps.length ? '🎬 Animated diagram' : '🗺️ Diagram';
    b.innerHTML = `<div class="fg-hint">↔ Swipe sideways to see the whole diagram</div><div class="vz-scroll fg-wrap">${draw(spec)}</div><div class="vz-msg" aria-live="polite"></div>${steps.length ? '<div class="vz-p"></div>' : ''}`;
    const svg = K.$('svg', b), msg = K.$('.vz-msg', b);
    const all = [...svg.querySelectorAll('[data-id]')];
    const used = new Set(steps.flatMap(s => s[0]));
    const info = {};
    (spec.n || []).forEach(n => { if (n[6] && n[6].i) info[n[0]] = n[6].i; });
    const intro = spec.m || (steps.length ? 'This is the whole picture. Press ▶ Play to walk through it step by step.' : (Object.keys(info).length ? 'Click any box with a dotted outline to learn more about it.' : ''));
    msg.innerHTML = intro;
    if (!intro) msg.hidden = true;
    svg.addEventListener('click', e => {
      const g = e.target.closest('.fg-n');
      if (!g || !info[g.dataset.id]) return;
      all.forEach(x => x.classList.remove('pick'));
      g.classList.add('pick');
      msg.hidden = false;
      msg.innerHTML = `<b>${esc(N(g.dataset.id))}</b>: ${info[g.dataset.id]}`;
    });
    function N(id) { const n = (spec.n || []).find(x => x[0] === id); return n ? String(n[5]).replace(/\n/g, ' ') : id; }
    if (!steps.length) return;
    const show = f => {
      const cur = f ? new Set(steps[f - 1][0]) : new Set();
      const past = new Set(f ? steps.slice(0, f - 1).flatMap(s => s[0]) : []);
      all.forEach(x => {
        const id = x.dataset.id;
        x.classList.toggle('on', cur.has(id));
        x.classList.toggle('fd', f > 0 && used.has(id) && !cur.has(id) && !past.has(id));
      });
      msg.innerHTML = f ? `<b>Step ${f} of ${steps.length}.</b> ${steps[f - 1][1]}` : intro;
    };
    const P = K.Player(K.$('.vz-p', b), show, spec.ms || 1500);
    P.load(steps.length + 1);
  };
  window.FLOW = { draw };
})();
