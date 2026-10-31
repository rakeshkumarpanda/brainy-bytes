/* ===== Advanced AI animations, part 1: one agent deciding (rational choice, risk, time).
   Every animation is declared with CVZ.def(name, spec) from assets/cvviz.js, so every value it uses has a control the
   reader can change, and its "Try this" list says which values to change and what to look for.
   Part 2 (games, dominance, IESDS and the quiz) is in assets/aigames.js and uses the helpers exported here as AIZ. ===== */
const AIZ = (() => {
  const { D, def } = CVZ;
  const FONT = (o = {}) => `${o.b ? '800 ' : '600 '}${o.s || 13}px ${o.mono ? '"JetBrains Mono", monospace' : 'Nunito, system-ui, sans-serif'}`;
  function tw(g, s, o = {}) { g.save(); g.font = FONT(o); const w = g.measureText(String(s)).width; g.restore(); return w; }
  function rr(g, x, y, w, h, r, o = {}) {
    g.save(); g.beginPath();
    r = Math.max(0, Math.min(r, w / 2, h / 2));
    g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
    if (o.fill) { g.fillStyle = o.fill; g.fill(); }
    if (o.stroke) { g.strokeStyle = o.stroke; g.lineWidth = o.w || 1.5; if (o.dash) g.setLineDash(o.dash); g.stroke(); }
    g.restore();
  }
  function fit(g, s, maxW, size = 13, o = {}) { let fs = size; while (fs > 8 && tw(g, s, Object.assign({}, o, { s: fs })) > maxW) fs -= 0.5; return fs; }
  /* a label in a rounded box centred on x, y. Returns its width */
  function tag(g, s, x, y, o = {}) {
    const fs = o.s || 12, w = tw(g, s, { s: fs, b: o.b !== false, mono: o.mono }) + 12, h = fs + 9;
    rr(g, x - w / 2, y - h / 2, w, h, 6, { fill: o.fill, stroke: o.stroke, w: o.lw || 1.2 });
    D.text(g, s, x, y + 1, { a: 'center', bl: 'middle', s: fs, b: o.b !== false, mono: o.mono, c: o.c });
    return w;
  }
  function wrap(g, s, x, y, maxW, o = {}) {
    const lh = o.lh || (o.s || 13) + 5;
    let line = '';
    String(s).split(/\s+/).filter(Boolean).forEach(w => {
      const t = line ? line + ' ' + w : w;
      if (line && tw(g, t, o) > maxW) { D.text(g, line, x, y, o); y += lh; line = w; } else line = t;
    });
    if (line) { D.text(g, line, x, y, o); y += lh; }
    return y;
  }
  const fmt = (v, d = 3) => {
    if (v === Infinity) return '∞';
    if (v === -Infinity) return '−∞';
    if (!isFinite(v)) return '?';
    const s = (Math.round(v * 10 ** d) / 10 ** d).toString();
    return s.replace('-', '−');
  };
  const num = s => +String(s).replace('−', '-');
  /* lines of "name value value ..." */
  function rows(text) {
    return String(text).split('\n').map(l => l.trim()).filter(Boolean).map(l => {
      const parts = l.split(/[\s,|]+/).filter(Boolean);
      const nums = [], names = [];
      parts.forEach(p => { if (/^[−-]?\d*\.?\d+$/.test(p)) nums.push(num(p)); else names.push(p); });
      return { name: names.join(' '), nums };
    });
  }
  /* utility functions used across the chapters */
  const UF = {
    lin: { name: 'u(x) = x', f: x => x, inv: y => y },
    sqrt: { name: 'u(x) = √x', f: x => Math.sqrt(Math.max(0, x)), inv: y => y * y },
    ln: { name: 'u(x) = ln x', f: x => x > 0 ? Math.log(x) : -Infinity, inv: y => Math.exp(y) },
    sq: { name: 'u(x) = x²', f: x => x * x, inv: y => Math.sqrt(Math.max(0, y)) },
    exp: { name: 'u(x) = 1 − e^(−x/10)', f: x => 1 - Math.exp(-x / 10), inv: y => -10 * Math.log(1 - y) }
  };
  const UOPTS = Object.keys(UF).map(k => [k, UF[k].name]);

  /* ---------- a tree drawer: nodes {label, kind: 'd' (decision) | 'n' (nature) | 'leaf', kids: [{edge, node}], val} ---------- */
  function layoutTree(root, x0, x1, y0, dy) {
    let leaves = 0;
    const count = n => { if (!n.kids || !n.kids.length) { n.leafIndex = leaves++; return; } n.kids.forEach(k => count(k.node)); };
    count(root);
    const place = (n, depth) => {
      n.y = y0 + depth * dy;
      if (!n.kids || !n.kids.length) { n.x = leaves === 1 ? (x0 + x1) / 2 : x0 + (x1 - x0) * n.leafIndex / (leaves - 1); return; }
      n.kids.forEach(k => place(k.node, depth + 1));
      n.x = (n.kids[0].node.x + n.kids[n.kids.length - 1].node.x) / 2;
    };
    place(root, 0);
    return leaves;
  }
  /* horizontal tree: depth goes to the right, leaves spread top to bottom */
  function layoutH(root, x0, dx, y0, y1) {
    let leaves = 0;
    const count = n => { if (!n.kids || !n.kids.length) { n.leafIndex = leaves++; return; } n.kids.forEach(k => count(k.node)); };
    count(root);
    const place = (n, depth) => {
      n.x = x0 + depth * dx;
      if (!n.kids || !n.kids.length) { n.y = leaves === 1 ? (y0 + y1) / 2 : y0 + (y1 - y0) * n.leafIndex / (leaves - 1); return; }
      n.kids.forEach(k => place(k.node, depth + 1));
      n.y = (n.kids[0].node.y + n.kids[n.kids.length - 1].node.y) / 2;
    };
    place(root, 0);
  }
  function drawTree(g, z, n, o = {}) {
    (n.kids || []).forEach(k => {
      const c = k.on ? z.col.cv : k.off ? z.col.line : z.col.ink2;
      D.line(g, n.x, n.y, k.node.x, k.node.y, c, k.on ? 3 : 1.4, k.off ? [4, 4] : null);
      if (k.edge) {
        const mx = n.x + (k.node.x - n.x) * (o.at || 0.5), my = n.y + (k.node.y - n.y) * (o.at || 0.5);
        tag(g, k.edge, mx, my - (o.lift || 0), { s: o.es || 10.5, fill: z.col.surf, stroke: k.on ? z.col.cv : z.col.line, c: k.on ? z.col.cv : z.col.ink, b: !!k.on });
      }
      drawTree(g, z, k.node, o);
    });
    const leaf = !n.kids || !n.kids.length;
    if (leaf) {
      tag(g, n.label, n.x + (o.leafDx || 0), n.y + (o.leafDy || 0), { s: o.ls || 11, fill: n.hot ? z.col.cv : z.col.bg, stroke: n.hot ? z.col.cv : z.col.line, c: n.hot ? '#fff' : z.col.ink, mono: o.mono });
    } else if (n.kind === 'n') {
      D.circle(g, n.x, n.y, 13, { fill: z.col.orange, stroke: z.col.surf, w: 2 });
      D.text(g, 'N', n.x, n.y + 1, { a: 'center', bl: 'middle', s: 12, b: true, c: '#fff' });
    } else {
      D.rect(g, n.x - 12, n.y - 12, 24, 24, { fill: z.col.cv });
      D.text(g, 'D', n.x, n.y + 1, { a: 'center', bl: 'middle', s: 12, b: true, c: '#fff' });
    }
    if (n.val !== undefined && !leaf) tag(g, fmt(n.val, 3), n.x, n.y - 24, { s: 11, fill: z.col.yellow, stroke: z.col.yellow, c: '#1f1300', mono: true });
  }

  /* ================= 1.1 preference relations ================= */
  function parseRel(text) {
    const pieces = String(text).split(/[,\n]/).map(s => s.trim()).filter(Boolean);
    const items = [], R = new Set();
    const add = x => { if (x && !items.includes(x)) items.push(x); };
    const key = (x, y) => x + '|' + y;
    if (pieces.length === 1 && /[>~=≻∼]/.test(pieces[0])) {
      /* a single chain such as A > B ~ C > D is a full ranking */
      const tok = pieces[0].split(/\s*(>|~|=|≻|∼)\s*/).filter(Boolean);
      const level = {};
      let lv = 0;
      tok.forEach((t, i) => {
        if (i % 2 === 0) { add(t); level[t] = lv; } else if (t === '>' || t === '≻') lv++;
      });
      items.forEach(x => items.forEach(y => { if (level[x] <= level[y]) R.add(key(x, y)); }));
      return { items, R, chain: true };
    }
    pieces.forEach(p => {
      const m = p.match(/^(.+?)\s*(>=|⪰|>|≻|~|∼|=)\s*(.+)$/);
      if (!m) { add(p); return; }
      const [, x, op, y] = m;
      add(x); add(y);
      R.add(key(x, y));
      if (op === '~' || op === '∼' || op === '=') R.add(key(y, x));
    });
    items.forEach(x => R.add(key(x, x)));
    return { items, R, chain: false };
  }
  function relChecks(rel) {
    const { items, R } = rel, has = (x, y) => R.has(x + '|' + y);
    const missing = [], bad = [];
    items.forEach((x, i) => items.forEach((y, j) => { if (j > i && !has(x, y) && !has(y, x)) missing.push([x, y]); }));
    outer: for (const x of items) for (const y of items) for (const w of items) {
      if (has(x, y) && has(y, w) && !has(x, w)) { bad.push([x, y, w]); if (bad.length > 2) break outer; }
    }
    const strict = [], indiff = [];
    items.forEach(x => items.forEach(y => {
      if (has(x, y) && !has(y, x)) strict.push([x, y]);
      if (x < y && has(x, y) && has(y, x)) indiff.push([x, y]);
    }));
    return { missing, bad, strict, indiff, has };
  }
  def('prefmatrix', {
    title: 'A preference relation as a table of ordered pairs',
    sub: 'Write a ranking like A > B ~ C > D, or separate statements like A > B, B ~ C. A filled cell in row x, column y means x ⪰ y.',
    W: 560, H: 330,
    params: [
      { k: 'rel', label: 'Preferences', type: 'area', v: 'A > B ~ C', help: '> strictly better, ~ indifferent, >= at least as good. One chain is read as a full ranking. With commas each statement is taken on its own.' }
    ],
    tips: [
      { t: 'The lecture example A ≻ B, A ≻ C, B ∼ C. Count the filled cells: 7 pairs, exactly the weak relation from the notes.', set: { rel: 'A > B ~ C' } },
      { t: 'Incomplete: the agent cannot compare B and C. The two empty cells are red and the relation is not complete.', set: { rel: 'A > B, A > C' } },
      { t: 'A cycle: A ≻ B, B ≻ C, C ≻ A. Transitivity fails and no utility function can represent it.', set: { rel: 'A > B, B > C, C > A' } },
      { t: 'The four outcome ranking A ≻ B ∼ C ≻ D from the worked example. Read off the strict pairs and the indifference pairs.', set: { rel: 'A > B ~ C > D' } },
      { t: 'Everyone indifferent. Every cell is filled, strict preference is empty, and every outcome is both best and worst.', set: { rel: 'A ~ B ~ C ~ D' } }
    ],
    draw(z) {
      const { g } = z;
      const rel = parseRel(z.p.rel), it = rel.items.slice(0, 7);
      if (it.length < 2) return 'Write at least two outcomes, for example A > B.';
      const ck = relChecks(rel), n = it.length;
      const cs = Math.min(40, 230 / n), x0 = 56, y0 = 48;
      D.text(g, 'row x ⪰ column y ?', x0, 24, { s: 12, b: true, c: z.col.ink2 });
      it.forEach((x, i) => {
        D.text(g, x, x0 - 8, y0 + i * cs + cs / 2 + 4, { a: 'right', s: fit(g, x, 44, 12), b: true, c: z.col.ink });
        D.text(g, x, x0 + i * cs + cs / 2, y0 - 8, { a: 'center', s: fit(g, x, cs, 12), b: true, c: z.col.ink });
      });
      it.forEach((x, i) => it.forEach((y, j) => {
        const a = ck.has(x, y), b = ck.has(y, x);
        let fill = null;
        if (a && b) fill = i === j ? z.col.line : z.col.teal;
        else if (a) fill = z.col.cv;
        D.rect(g, x0 + j * cs + 1, y0 + i * cs + 1, cs - 2, cs - 2, { fill: fill || z.col.surf, stroke: !a && !b && i !== j ? z.col.red : z.col.line, dash: !a && !b ? [3, 3] : null, w: 1 });
        if (a) D.text(g, a && b ? '∼' : '≻', x0 + j * cs + cs / 2, y0 + i * cs + cs / 2 + 1, { a: 'center', bl: 'middle', s: 13, b: true, c: '#fff' });
      }));
      const lx = x0 + n * cs + 22, lw = z.W - lx - 10;
      let y = 30;
      const line = (s, c) => { y = wrap(g, s, lx, y, lw, { s: 12, c: c || z.col.ink, b: true, lh: 16 }); y += 4; };
      line('≻ = { ' + ck.strict.map(p => `(${p[0]},${p[1]})`).join(' ') + ' }', z.col.cv);
      line('∼ (off the diagonal) = { ' + ck.indiff.map(p => `(${p[0]},${p[1]}) (${p[1]},${p[0]})`).join(' ') + ' }', z.col.teal);
      y += 6;
      line(ck.missing.length ? '✗ Not complete: ' + ck.missing.map(p => p.join(' and ')).join(', ') + ' cannot be compared' : '✓ Complete: every pair is compared', ck.missing.length ? z.col.red : z.col.green);
      line(ck.bad.length ? `✗ Not transitive: ${ck.bad[0][0]} ⪰ ${ck.bad[0][1]} and ${ck.bad[0][1]} ⪰ ${ck.bad[0][2]} but not ${ck.bad[0][0]} ⪰ ${ck.bad[0][2]}` : '✓ Transitive: no chain breaks', ck.bad.length ? z.col.red : z.col.green);
      const rational = !ck.missing.length && !ck.bad.length;
      if (rational) {
        const u = it.map(x => it.filter(y => ck.has(x, y)).length);
        line('Utility: ' + it.map((x, i) => `u(${x}) = ${u[i]}`).join(', '), z.col.ink);
      }
      D.rect(g, x0, y0 + n * cs + 14, 12, 12, { fill: z.col.cv }); D.text(g, 'strict', x0 + 16, y0 + n * cs + 24, { s: 11, c: z.col.ink2 });
      D.rect(g, x0 + 62, y0 + n * cs + 14, 12, 12, { fill: z.col.teal }); D.text(g, 'indifferent', x0 + 78, y0 + n * cs + 24, { s: 11, c: z.col.ink2 });
      D.rect(g, x0 + 150, y0 + n * cs + 14, 12, 12, { stroke: z.col.red, dash: [3, 3], w: 1 }); D.text(g, 'missing', x0 + 166, y0 + n * cs + 24, { s: 11, c: z.col.ink2 });
      return rational ? '<b>Rational.</b> The relation is complete and transitive, so a utility function represents it. The one shown counts how many outcomes each one is at least as good as.'
        : '<b>Not rational.</b> ' + (ck.bad.length ? 'A broken chain means a cycle or a gap, so no number line can hold this ranking. ' : '') + (ck.missing.length ? 'An empty pair is incompleteness, which is different from indifference: the agent has not said the two are equal, it has said nothing.' : '');
    }
  });

  /* ================= 1.2 building a utility function ================= */
  def('utilbuild', {
    title: 'Building a utility function from a ranking, one class at a time',
    sub: 'Press Step: take the best outcomes still left, give them the next value, remove them, repeat. Then try a transformation.',
    W: 560, H: 300,
    params: [
      { k: 'rank', label: 'Ranking (best first)', type: 'text', v: 'A > B ~ C > D' },
      { k: 'top', label: 'Value for the best class', type: 'range', v: 3, min: -10, max: 100 },
      { k: 'gap', label: 'Gap between classes', type: 'range', v: 1, min: 1, max: 40 },
      { k: 'tf', label: 'Then apply', type: 'select', v: 'none', opts: [['none', 'nothing'], ['aff', 'v = 2u + 7'], ['cube', 'v = u³'], ['exp', 'v = e^u'], ['neg', 'v = −u'], ['sq', 'v = u²']] }
    ],
    tips: [
      { t: 'Play the construction. Each step removes one indifference class, which is the proof that a finite rational ranking always has a utility function.', play: true },
      { t: 'Set the best value to 100 and the gap to 20. The numbers change, the order does not. Ordinal utility is not unique.', set: { top: 100, gap: 20 } },
      { t: 'Apply v = 2u + 7 or v = u³. Both are strictly increasing, so the order survives.', set: { tf: 'cube' } },
      { t: 'Apply v = −u. The ranking flips, so v no longer represents the same preferences.', set: { tf: 'neg' } },
      { t: 'Set the best value to 1 with gap 2, then apply u². The values 1, −1, −3 square to 1, 1, 9 and the order breaks. u² is increasing only for non negative u.', set: { top: 1, gap: 2, tf: 'sq' } }
    ],
    steps(z) { const r = parseRel(z.p.rank); const lv = new Set(); classes(r).forEach((_, i) => lv.add(i)); return lv.size; },
    draw(z) {
      const { g, p } = z;
      const rel = parseRel(p.rank);
      if (!rel.chain) return 'Write one chain, for example A > B ~ C > D.';
      const cl = classes(rel);
      const val = cl.map((_, i) => p.top - i * p.gap);
      const T = { none: u => u, aff: u => 2 * u + 7, cube: u => u * u * u, exp: u => Math.exp(u), neg: u => -u, sq: u => u * u }[p.tf];
      D.text(g, 'Classes found so far', 16, 22, { s: 12, b: true, c: z.col.ink2 });
      cl.forEach((c, i) => {
        const on = i < z.step, x = 16 + i * 132;
        if (x > z.W - 120) return;
        rr(g, x, 32, 122, 56, 10, { fill: on ? z.col.cv : z.col.bg, stroke: z.col.line });
        D.text(g, c.join(' ∼ '), x + 61, 54, { a: 'center', s: fit(g, c.join(' ∼ '), 110, 14), b: true, c: on ? '#fff' : z.col.ink2 });
        D.text(g, on ? 'u = ' + fmt(val[i]) : 'not yet', x + 61, 76, { a: 'center', s: 12, b: true, c: on ? '#fff' : z.col.ink2, mono: true });
      });
      const shown = cl.slice(0, z.step);
      if (!shown.length) return 'Step 0: nothing assigned yet. The best class is the set of outcomes x with x ⪰ y for every remaining y.';
      const draw = (vals, y, label, col) => {
        const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
        D.text(g, label, 16, y - 18, { s: 12, b: true, c: col });
        D.line(g, 40, y, z.W - 30, y, z.col.line, 2);
        shown.forEach((c, i) => {
          const x = 40 + (vals[i] - lo) / span * (z.W - 90);
          D.circle(g, x, y, 6, { fill: col });
          D.text(g, c.join('∼'), x, y + 20, { a: 'center', s: 12, b: true, c: z.col.ink });
          D.text(g, fmt(vals[i], 2), x, y - 9, { a: 'center', s: 10.5, c: z.col.ink2, mono: true });
        });
      };
      const u = shown.map((_, i) => val[i]), v = u.map(T);
      draw(u, 150, 'u on a number line (right is better)', z.col.cv);
      let kept = true;
      for (let i = 1; i < v.length; i++) if (!(v[i - 1] > v[i])) kept = false;
      if (p.tf !== 'none') draw(v, 240, 'after the transformation', kept ? z.col.green : z.col.red);
      return `Assigned ${shown.length} of ${cl.length} classes. Outcomes in one class share one value, values fall as you go down the ranking.` +
        (p.tf === 'none' ? '' : kept ? ' <b>The transformation keeps the order</b>, so it represents the same preferences.' : ' <b>The transformation breaks the order</b>, so it is not a valid representation.');
    }
  });
  function classes(rel) {
    const ck = relChecks(rel), left = rel.items.slice(), out = [];
    while (left.length) {
      const top = left.filter(x => left.every(y => ck.has(x, y)));
      if (!top.length) break;
      out.push(top);
      top.forEach(t => left.splice(left.indexOf(t), 1));
    }
    return out;
  }

  def('orderings', {
    title: 'How many rankings of n outcomes are there?',
    sub: 'Strict rankings (no ties) number n!. Allowing ties gives the weak orders, which grow even faster. Both stay finite.',
    W: 560, H: 260,
    params: [{ k: 'n', label: 'Number of outcomes n', type: 'range', v: 5, min: 1, max: 10 }],
    tips: [
      { t: 'n = 3 gives 6 strict rankings and 13 weak orders. List them by hand to check.', set: { n: 3 } },
      { t: 'n = 5 gives 5! = 120 strict rankings, the number from the lecture.', set: { n: 5 } },
      { t: 'n = 10 already gives 3,628,800 strict rankings and over 102 million weak orders, yet both are finite, which is all the existence theorem needs.', set: { n: 10 } }
    ],
    draw(z) {
      const { g, p } = z;
      const fact = k => k <= 1 ? 1 : k * fact(k - 1);
      const C = (a, b) => fact(a) / (fact(b) * fact(a - b));
      const fub = [1];
      for (let m = 1; m <= 10; m++) { let s = 0; for (let k = 1; k <= m; k++) s += C(m, k) * fub[m - k]; fub.push(s); }
      const m = D.axes(g, z, [70, 20, 460, 190], [0.5, 10.5], [0, 9], { nx: 10, ny: 3, fx: v => String(Math.round(v)), fy: v => '10^' + Math.round(v), xl: 'number of outcomes n', yl: 'count (log scale)' });
      for (let k = 1; k <= 10; k++) {
        const a = Math.log10(fact(k)), b = Math.log10(fub[k]);
        const on = k === p.n;
        D.rect(g, m.sx(k) - 13, m.sy(a), 12, m.sy(0) - m.sy(a), { fill: on ? z.col.cv : z.col.line });
        D.rect(g, m.sx(k) + 1, m.sy(b), 12, m.sy(0) - m.sy(b), { fill: on ? z.col.orange : z.col.bg, stroke: z.col.line, w: 1 });
      }
      D.rect(g, 90, 28, 12, 12, { fill: z.col.cv }); D.text(g, 'strict rankings n!', 106, 38, { s: 11.5, c: z.col.ink2 });
      D.rect(g, 90, 46, 12, 12, { fill: z.col.orange }); D.text(g, 'weak orders (ties allowed)', 106, 56, { s: 11.5, c: z.col.ink2 });
      return `With n = ${p.n}: <b>${fact(p.n).toLocaleString('en')}</b> strict rankings and <b>${fub[p.n].toLocaleString('en')}</b> weak orders. Large, but finite, so the agent's ranking is always one of a finite list.`;
    }
  });

  /* ================= 1.3 choosing the best action ================= */
  def('movie', {
    title: 'A decision tree for the cinema choice, with travel costs',
    sub: 'The first branch is the theatre, the second is the movie you end up watching there. Each leaf shows movie utility minus travel cost.',
    W: 560, H: 330,
    params: [
      { k: 'films', label: 'Theatre, movie, utility (one per line)', type: 'area', v: 'INOX Aliens 6\nINOX BladeRunner 5\nINOX Casablanca 4\nPVR DoctorStrange 3\nPVR GoneWithTheWind 2\nPVR TheMatrix 1' },
      { k: 'd1', label: 'Distance to the first theatre (miles)', type: 'range', v: 1, min: 0, max: 10, step: 0.5 },
      { k: 'd2', label: 'Distance to the second theatre (miles)', type: 'range', v: 3, min: 0, max: 10, step: 0.5 },
      { k: 'cpm', label: 'Utility lost per mile walked', type: 'range', v: 1, min: 0, max: 3, step: 0.1 }
    ],
    tips: [
      { t: 'Set the cost per mile to 0. The best movie decides alone: go to INOX for Aliens.', set: { cpm: 0 } },
      { t: 'The lecture numbers: INOX 1 mile, PVR 3 miles, 1 unit per mile. Aliens still wins with net payoff 5.', set: { d1: 1, d2: 3, cpm: 1 } },
      { t: 'Move INOX far away (8 miles). Now the nearer, worse theatre wins. The best movie is not always the best complete outcome.', set: { d1: 8, d2: 1, cpm: 1 } },
      { t: 'Give the second theatre a better movie: change PVR TheMatrix 1 to PVR TheMatrix 9.', set: { films: 'INOX Aliens 6\nINOX BladeRunner 5\nINOX Casablanca 4\nPVR DoctorStrange 3\nPVR GoneWithTheWind 2\nPVR TheMatrix 9' } }
    ],
    draw(z) {
      const { g, p } = z;
      const list = rows(p.films).filter(r => r.nums.length).slice(0, 8).map(r => { const w = r.name.split(' '); return { th: w[0], mv: w.slice(1).join(' ') || '?', u: r.nums[0] }; });
      if (!list.length) return 'Write lines like "INOX Aliens 6".';
      const ths = [...new Set(list.map(r => r.th))].slice(0, 3);
      const dist = th => ths.indexOf(th) === 0 ? p.d1 : ths.indexOf(th) === 1 ? p.d2 : p.d2;
      const net = r => r.u - p.cpm * dist(r.th);
      const best = Math.max(...list.map(net));
      const root = { kind: 'd', kids: ths.map(th => ({ edge: `${th} (${fmt(dist(th), 1)} mi)`, node: { kind: 'n', kids: list.filter(r => r.th === th).map(r => ({ edge: '', node: { label: `${r.mv}: ${fmt(r.u, 2)} − ${fmt(p.cpm * dist(r.th), 2)} = ${fmt(net(r), 2)}`, hot: net(r) === best } })) } })) };
      layoutH(root, 40, 150, 22, z.H - 22);
      root.kids.forEach(k => { k.on = k.node.kids.some(q => q.node.hot); k.node.kind = 'd'; k.node.kids.forEach(q => { q.on = q.node.hot; }); });
      drawTree(g, z, root, { leafDx: 120, ls: 10.5, at: 0.55 });
      const win = list.find(r => net(r) === best);
      return `Net payoff = movie utility − cost per mile × distance. The best leaf is <b>${win.mv} at ${win.th}</b> with ${fmt(best, 2)}. A rational agent compares complete outcomes, not just the movies.`;
    }
  });

  def('fruit', {
    title: 'Problem 1.6: which fruit trees to plant',
    sub: 'Every way to plant at most the allowed number of trees, with the change in total spending. Lower spending is better.',
    W: 560, H: 330,
    params: [
      { k: 'ac', label: 'Apple maintenance $', type: 'range', v: 100, min: 0, max: 200 },
      { k: 'ar', label: 'Apple food bill cut $', type: 'range', v: 130, min: 0, max: 250 },
      { k: 'oc', label: 'Orange maintenance $', type: 'range', v: 70, min: 0, max: 200 },
      { k: 'or', label: 'Orange food bill cut $', type: 'range', v: 90, min: 0, max: 250 },
      { k: 'pc', label: 'Pear maintenance $', type: 'range', v: 120, min: 0, max: 200 },
      { k: 'pr', label: 'Pear food bill cut $', type: 'range', v: 145, min: 0, max: 250 },
      { k: 'max', label: 'Most trees you may plant', type: 'range', v: 2, min: 1, max: 3 },
      { k: 'second', label: 'Share of the cut a repeated type still gives', type: 'range', v: 1, min: 0, max: 1, step: 0.05, help: '1 = no variety preference (part b). 0.5 = part d.' }
    ],
    tips: [
      { t: 'Part (b): every tree gives its full cut. Two apples save $60 and win.', set: { second: 1, max: 2 } },
      { t: 'Part (d): a second tree of the same type gives only half its cut. Two apples now cost $5 more, and apple plus pear wins with −$55.', set: { second: 0.5, max: 2 } },
      { t: 'Allow three trees with full cuts. Three apples save $90. Without diminishing returns the agent repeats the single best tree.', set: { second: 1, max: 3 } },
      { t: 'Make apple maintenance $140. Its saving drops below the orange and the ranking reshuffles.', set: { ac: 140, second: 1, max: 2 } }
    ],
    draw(z) {
      const { g, p } = z;
      const T = [['A', p.ac, p.ar], ['O', p.oc, p.or], ['P', p.pc, p.pr]];
      const acts = [[]];
      const rec = (start, cur) => { if (cur.length) acts.push(cur.slice()); if (cur.length === p.max) return; for (let i = start; i < 3; i++) { cur.push(i); rec(i, cur); cur.pop(); } };
      rec(0, []);
      const val = a => {
        let d = 0; const seen = {};
        a.forEach(i => { const k = seen[i] || 0; d += T[i][1] - T[i][2] * (k === 0 ? 1 : p.second); seen[i] = k + 1; });
        return d;
      };
      const list = acts.map(a => ({ name: a.length ? a.map(i => T[i][0]).join('') : 'none', d: val(a) })).sort((a, b) => a.d - b.d);
      const best = list[0].d;
      const lo = Math.min(0, ...list.map(r => r.d)), hi = Math.max(0, ...list.map(r => r.d)), span = (hi - lo) || 1;
      const rowH = Math.min(22, (z.H - 40) / list.length), x0 = 80, wd = z.W - x0 - 80, zx = x0 + (0 - lo) / span * wd;
      D.text(g, 'final spending = X + maintenance − food bill cut', 16, 18, { s: 12, b: true, c: z.col.ink2 });
      list.forEach((r, i) => {
        const y = 30 + i * rowH, x = x0 + (r.d - lo) / span * wd;
        D.text(g, r.name, x0 - 8, y + rowH * 0.7, { a: 'right', s: 12, b: true, c: z.col.ink, mono: true });
        D.rect(g, Math.min(x, zx), y + 2, Math.max(2, Math.abs(x - zx)), rowH - 5, { fill: r.d === best ? z.col.cv : r.d < 0 ? z.col.teal : z.col.red });
        D.text(g, 'X ' + (r.d >= 0 ? '+ ' : '− ') + fmt(Math.abs(r.d), 2), Math.max(x, zx) + 6, y + rowH * 0.7, { s: 11, c: z.col.ink2, mono: true });
      });
      D.line(g, zx, 26, zx, 30 + list.length * rowH, z.col.ink2, 1, [3, 3]);
      return `${list.length} actions (order does not matter, so AO is the same as OA). Best: <b>${list.filter(r => r.d === best).map(r => r.name).join(', ')}</b> with spending X ${best >= 0 ? '+' : '−'} ${fmt(Math.abs(best), 2)}. Minimising spending is the same as maximising u = −spending.`;
    }
  });

  def('parks', {
    title: 'Problem 1.7: how much should the city spend on parks?',
    sub: 'Benefit v(c) = √(k c) − c ⁄ m. The orange line is the legal limit. The best feasible spending is the green dot.',
    W: 560, H: 300,
    params: [
      { k: 'k', label: 'k in √(k c)', type: 'range', v: 400, min: 100, max: 3200, step: 100 },
      { k: 'm', label: 'm in c ⁄ m', type: 'range', v: 80, min: 20, max: 200, step: 5 },
      { k: 'budget', label: 'City budget ($ million)', type: 'range', v: 20, min: 5, max: 60 },
      { k: 'cap', label: 'Most that may go to parks (% of budget)', type: 'range', v: 5, min: 1, max: 15 },
      { k: 'slope', label: 'Show marginal benefit and marginal cost', type: 'check', v: false }
    ],
    tips: [
      { t: 'Part (b): k = 400. The peak at c = 640,000 is inside the limit of 1,000,000, so spend $640,000.', set: { k: 400, m: 80, budget: 20, cap: 5 } },
      { t: 'Part (c): k = 1600. The peak moves to 2,560,000, past the limit, so the best feasible choice is the limit itself.', set: { k: 1600 } },
      { t: 'Show the slopes. At the interior optimum marginal benefit √k ⁄ (2√c) equals marginal cost 1 ⁄ m.', set: { slope: true, k: 400 } },
      { t: 'Raise the cap to 15%. With k = 1600 the peak becomes feasible again.', set: { k: 1600, cap: 15 } }
    ],
    draw(z) {
      const { g, p } = z;
      const v = c => Math.sqrt(p.k * c) - c / p.m;
      const star = p.k * p.m * p.m / 4, lim = p.budget * 1e6 * p.cap / 100;
      const pick = Math.min(star, lim);
      const xmax = Math.max(star, lim) * 1.25;
      const ymax = Math.max(v(star), 1) * 1.15, ymin = Math.min(0, v(xmax));
      const mm = D.axes(g, z, [70, 18, 460, 220], [0, xmax], [ymin, ymax], { nx: 4, ny: 4, fx: x => fmt(x / 1e6, 2) + 'M', fy: y => fmt(y / 1e3, 1) + 'k', xl: 'spending c ($)', yl: 'benefit v(c)' });
      D.curve(g, v, [0, xmax], mm, z.col.cv, 2.5);
      D.line(g, mm.sx(lim), 18, mm.sx(lim), 238, z.col.orange, 2, [6, 4]);
      D.text(g, 'limit', mm.sx(lim) + 4, 32, { s: 11, b: true, c: z.col.orange });
      D.circle(g, mm.sx(star), mm.sy(v(star)), 5, { stroke: z.col.ink2, w: 2, fill: z.col.surf });
      D.circle(g, mm.sx(pick), mm.sy(v(pick)), 7, { fill: z.col.green, stroke: '#fff', w: 2 });
      if (p.slope) {
        const s2 = mm.sy(0);
        D.curve(g, c => c > 0 ? (Math.sqrt(p.k) / (2 * Math.sqrt(c))) * ymax * p.m / 4 : NaN, [xmax * 0.01, xmax], mm, z.col.teal, 1.5, 200, [4, 3]);
        D.line(g, 70, mm.sy(ymax / 4), 530, mm.sy(ymax / 4), z.col.red, 1.5, [4, 3]);
        D.text(g, 'marginal benefit (scaled)', 380, mm.sy(ymax / 4) - 30, { s: 10.5, c: z.col.teal, b: true });
        D.text(g, 'marginal cost 1 ⁄ m (scaled)', 380, mm.sy(ymax / 4) + 14, { s: 10.5, c: z.col.red, b: true });
        void s2;
      }
      const inside = star <= lim;
      return `v′(c) = √k ⁄ (2√c) − 1 ⁄ m = 0 gives c* = k m² ⁄ 4 = <b>${Math.round(star).toLocaleString('en')}</b>. v″(c) < 0, so it is a maximum. The limit is ${Math.round(lim).toLocaleString('en')}. ` +
        (inside ? `The peak is feasible: spend <b>$${Math.round(star).toLocaleString('en')}</b>.` : `The peak is not feasible and v rises all the way to the limit, so spend <b>$${Math.round(lim).toLocaleString('en')}</b>.`);
    }
  });

  /* ================= 2.1 lotteries and the CDF ================= */
  def('cdf', {
    title: 'A lottery, its probability picture and its CDF',
    sub: 'Top: how likely each outcome is. Bottom: F(x) = P(X ≤ x). The shaded height F(s) − F(r) is the chance of landing between r and s.',
    W: 560, H: 340,
    params: [
      { k: 'kind', label: 'Kind of lottery', type: 'select', v: 'disc', opts: [['disc', 'discrete outcomes'], ['unif', 'uniform between two values'], ['norm', 'normal (bell curve)'], ['expo', 'exponential']] },
      { k: 'list', label: 'Outcome and probability, one per line', type: 'area', v: '10 0.3\n20 0.5\n50 0.2', show: p => p.kind === 'disc' },
      { k: 'a', label: 'Low end, or mean', type: 'range', v: 20, min: 0, max: 80, show: p => p.kind !== 'disc' },
      { k: 'b', label: 'High end, or spread', type: 'range', v: 15, min: 1, max: 80, show: p => p.kind !== 'disc' },
      { k: 'r', label: 'r', type: 'range', v: 15, min: 0, max: 100 },
      { k: 's', label: 's', type: 'range', v: 40, min: 0, max: 100 }
    ],
    tips: [
      { t: 'Discrete lottery: the CDF climbs in jumps exactly at 10, 20 and 50, and each jump is that outcome\'s probability. The filled dots show right continuity.', set: { kind: 'disc', list: '10 0.3\n20 0.5\n50 0.2' } },
      { t: 'Problem 8 from the notes: put r = 20 and s = 50 with the normal curve. Read F(50) − F(20) under the bottom panel.', set: { kind: 'norm', a: 35, b: 12, r: 20, s: 50 } },
      { t: 'A crop yield that is uniform between 20 and 60. The CDF is a straight ramp and P(X = x) is 0 for every single x.', set: { kind: 'unif', a: 20, b: 60 } },
      { t: 'Move r above s. The interval is empty and the probability is 0, never negative, because F never goes down.', set: { r: 60, s: 30 } }
    ],
    draw(z) {
      const { g, p } = z;
      let F, pts = null, dens = null;
      if (p.kind === 'disc') {
        pts = rows(p.list).filter(r => r.nums.length >= 1).map(r => r.nums.length >= 2 ? [r.nums[0], r.nums[1]] : [num(r.name), r.nums[0]]).filter(q => isFinite(q[0]) && q[1] >= 0).sort((a, b) => a[0] - b[0]);
        const tot = pts.reduce((a, q) => a + q[1], 0) || 1;
        pts = pts.map(q => [q[0], q[1] / tot]);
        F = x => pts.filter(q => q[0] <= x).reduce((a, q) => a + q[1], 0);
      } else if (p.kind === 'unif') {
        const lo = Math.min(p.a, p.b), hi = Math.max(p.a, p.b) || lo + 1;
        F = x => x <= lo ? 0 : x >= hi ? 1 : (x - lo) / (hi - lo); dens = x => x >= lo && x <= hi ? 1 / (hi - lo) : 0;
      } else if (p.kind === 'norm') {
        const erf = x => { const t = 1 / (1 + 0.3275911 * Math.abs(x)); const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x); return x >= 0 ? y : -y; };
        F = x => 0.5 * (1 + erf((x - p.a) / (p.b * Math.SQRT2))); dens = x => Math.exp(-((x - p.a) ** 2) / (2 * p.b * p.b)) / (p.b * Math.sqrt(2 * Math.PI));
      } else {
        const lam = 1 / Math.max(1, p.b);
        F = x => x <= 0 ? 0 : 1 - Math.exp(-lam * x); dens = x => x < 0 ? 0 : lam * Math.exp(-lam * x);
      }
      const X = [0, 100];
      const top = D.axes(g, z, [60, 14, 470, 110], X, [0, pts ? Math.max(...pts.map(q => q[1]), 0.1) * 1.15 : Math.max(dens(p.a), dens((p.a + p.b) / 2), dens(0), 0.02) * 1.2], { nx: 5, ny: 2, yl: pts ? 'P(X = x)' : 'density f(x)' });
      if (pts) pts.forEach(q => { D.line(g, top.sx(q[0]), top.sy(0), top.sx(q[0]), top.sy(q[1]), z.col.cv, 3); D.circle(g, top.sx(q[0]), top.sy(q[1]), 4, { fill: z.col.cv }); });
      else {
        g.save(); g.fillStyle = z.col.cv + '33'; g.beginPath(); g.moveTo(top.sx(Math.max(0, Math.min(p.r, p.s))), top.sy(0));
        for (let x = Math.min(p.r, p.s); x <= Math.max(p.r, p.s); x += 0.5) g.lineTo(top.sx(x), top.sy(dens(x)));
        g.lineTo(top.sx(Math.max(p.r, p.s)), top.sy(0)); g.closePath(); if (p.s > p.r) g.fill(); g.restore();
        D.curve(g, dens, X, top, z.col.cv, 2);
      }
      const bot = D.axes(g, z, [60, 160, 470, 140], X, [0, 1], { nx: 5, ny: 2, xl: 'outcome x', yl: 'F(x)' });
      if (pts) {
        let prev = 0, px = 0;
        pts.forEach(q => { D.line(g, bot.sx(px), bot.sy(prev), bot.sx(q[0]), bot.sy(prev), z.col.orange, 2.5); D.circle(g, bot.sx(q[0]), bot.sy(prev), 3.5, { stroke: z.col.orange, fill: z.col.surf }); prev += q[1]; px = q[0]; D.circle(g, bot.sx(q[0]), bot.sy(prev), 4, { fill: z.col.orange }); });
        D.line(g, bot.sx(px), bot.sy(prev), bot.sx(100), bot.sy(prev), z.col.orange, 2.5);
      } else D.curve(g, F, X, bot, z.col.orange, 2.5);
      const Fr = F(p.r), Fs = F(p.s), pr = Math.max(0, Fs - Fr);
      [[p.r, Fr, 'r'], [p.s, Fs, 's']].forEach(([x, y, l]) => { D.line(g, bot.sx(x), bot.sy(0), bot.sx(x), bot.sy(y), z.col.ink2, 1, [3, 3]); D.line(g, bot.sx(0), bot.sy(y), bot.sx(x), bot.sy(y), z.col.ink2, 1, [3, 3]); D.text(g, l, bot.sx(x), bot.sy(0) - 4, { a: 'center', s: 11, b: true, c: z.col.ink }); });
      if (p.s > p.r) D.rect(g, 534, bot.sy(Fs), 10, bot.sy(Fr) - bot.sy(Fs), { fill: z.col.green });
      return `F(${p.r}) = ${fmt(Fr)} and F(${p.s}) = ${fmt(Fs)}. So P(${p.r} < X ≤ ${p.s}) = F(${p.s}) − F(${p.r}) = <b>${fmt(pr)}</b>. ` + (pts ? `The CDF is non decreasing, starts at 0, ends at 1 and is right continuous at every jump.` : 'For a continuous outcome P(X = x) = 0 at every single point. Only intervals have positive probability.');
    }
  });

  /* ================= 2.2 compound lotteries and expected utility ================= */
  def('compound', {
    title: 'Reducing the R&D compound lottery to a simple one',
    sub: 'Multiply along each path, then add the paths that end in the same payoff. Step through to see each product.',
    W: 560, H: 320,
    params: [
      { k: 'ps', label: 'P(R&D succeeds)', type: 'range', v: 0.625, min: 0, max: 1, step: 0.005 },
      { k: 'gs', label: 'P(good market | success)', type: 'range', v: 0.9, min: 0, max: 1, step: 0.05 },
      { k: 'gf', label: 'P(good market | failure)', type: 'range', v: 0.5, min: 0, max: 1, step: 0.05 },
      { k: 'gn', label: 'P(good market) if you do not invest', type: 'range', v: 0.5, min: 0, max: 1, step: 0.05 },
      { k: 'hi', label: 'Payoff in a good market', type: 'range', v: 10, min: 0, max: 30 },
      { k: 'lo', label: 'Payoff in a bad market', type: 'range', v: 0, min: -20, max: 10 }
    ],
    tips: [
      { t: 'The lecture numbers. Play it: the four paths give 0.5625, 0.0625, 0.1875 and 0.1875, so G is 10 with 0.75 and EU(G) = 7.5 against EU(S) = 5.', set: { ps: 0.625, gs: 0.9, gf: 0.5, gn: 0.5, hi: 10, lo: 0 }, play: true },
      { t: 'Make failure as bad as no research: P(good | failure) = 0.5 already equals the no R&D market, so research can only help. Lower it to 0.2 and watch EU(G) fall.', set: { gf: 0.2 } },
      { t: 'Make the bad market a loss of 10. Both expected payoffs move, and the gap between them grows.', set: { lo: -10 } }
    ],
    steps: () => 6,
    startAtZero: true,
    draw(z) {
      const { g, p } = z;
      const paths = [[p.ps * p.gs, p.hi, 'success, good'], [p.ps * (1 - p.gs), p.lo, 'success, bad'], [(1 - p.ps) * p.gf, p.hi, 'failure, good'], [(1 - p.ps) * (1 - p.gf), p.lo, 'failure, bad']];
      const root = { kind: 'n', kids: [
        { edge: 'success ' + fmt(p.ps), node: { kind: 'n', kids: [{ edge: fmt(p.gs, 2), node: { label: '' } }, { edge: fmt(1 - p.gs, 2), node: { label: '' } }] } },
        { edge: 'failure ' + fmt(1 - p.ps), node: { kind: 'n', kids: [{ edge: fmt(p.gf, 2), node: { label: '' } }, { edge: fmt(1 - p.gf, 2), node: { label: '' } }] } }] };
      layoutH(root, 40, 120, 30, 230);
      let i = 0;
      const lab = n => { if (!n.kids) { const q = paths[i]; n.label = `${q[2]}: ${z.step > i ? fmt(q[0], 4) : '?'} → ${q[1]}`; n.hot = z.step === i + 1; i++; } else n.kids.forEach(k => lab(k.node)); };
      lab(root);
      D.text(g, 'G: invest in R&D', 16, 18, { s: 12, b: true, c: z.col.cv });
      drawTree(g, z, root, { leafDx: 100, ls: 11 });
      const pHi = paths[0][0] + paths[2][0], EG = pHi * p.hi + (1 - pHi) * p.lo, ES = p.gn * p.hi + (1 - p.gn) * p.lo;
      let y = 262;
      if (z.step >= 5) { D.text(g, `Reduced G: ${p.hi} with ${fmt(paths[0][0], 4)} + ${fmt(paths[2][0], 4)} = ${fmt(pHi, 4)},  ${p.lo} with ${fmt(1 - pHi, 4)}`, 16, y, { s: 12.5, b: true, c: z.col.ink }); y += 22; }
      if (z.step >= 6) D.text(g, `EU(G) = ${fmt(EG, 4)}     EU(S) = ${fmt(p.gn, 2)} × ${p.hi} + ${fmt(1 - p.gn, 2)} × ${p.lo} = ${fmt(ES, 4)}`, 16, y, { s: 12.5, b: true, c: EG >= ES ? z.col.cv : z.col.orange });
      if (z.step < 5) return `Step ${z.step}: multiply the probabilities along each branch to get the chance of that whole path.`;
      if (z.step === 5) return 'Add the paths that end at the same payoff. The internal structure no longer matters, only the final distribution.';
      return `Choose <b>${EG > ES ? 'G, invest' : EG < ES ? 'S, do not invest' : 'either, they tie'}</b>, since ${fmt(EG, 3)} ${EG >= ES ? '≥' : '<'} ${fmt(ES, 3)}. The optimistic test (more chance of the best payoff) and the pessimistic test (less chance of the worst) agree here.`;
    }
  });

  def('affine', {
    title: 'Same ranking, different numbers, opposite choice',
    sub: 'G gives A or B, S gives C or D. All four utility rows rank C ≻ A ≻ D ≻ B, yet the expected utility winner can flip.',
    W: 560, H: 290,
    params: [
      { k: 'uA', label: 'u(A)', type: 'range', v: 9, min: -10, max: 20 },
      { k: 'uB', label: 'u(B)', type: 'range', v: -1, min: -20, max: 10 },
      { k: 'uC', label: 'u(C)', type: 'range', v: 10, min: -10, max: 20 },
      { k: 'uD', label: 'u(D)', type: 'range', v: 0, min: -10, max: 10 },
      { k: 'pg', label: 'P(A) in lottery G', type: 'range', v: 0.75, min: 0, max: 1, step: 0.05 },
      { k: 'ps', label: 'P(C) in lottery S', type: 'range', v: 0.5, min: 0, max: 1, step: 0.05 },
      { k: 'a', label: 'a in v = a u + b', type: 'range', v: 2, min: 0.1, max: 5, step: 0.1 },
      { k: 'b', label: 'b in v = a u + b', type: 'range', v: 3, min: -20, max: 20 }
    ],
    tips: [
      { t: 'The lecture numbers: u = 9, −1, 10, 0. EU(G) = 6.5 beats EU(S) = 5.', set: { uA: 9, uB: -1, uC: 10, uD: 0 } },
      { t: 'Change only u(B) to −8. The order C ≻ A ≻ D ≻ B is the same, but EU(G) = 4.75 now loses to 5.', set: { uB: -8 } },
      { t: 'Change a and b. The affine row always picks the same lottery as the u row, because E[a u + b] = a E[u] + b with a > 0.', set: { a: 4, b: -15 } },
      { t: 'Look at the cube row. u³ keeps the order of outcomes but stretches the gaps, and it can flip the lottery choice too.', set: { uA: 9, uB: -1, uC: 10, uD: 0, pg: 0.75 } }
    ],
    draw(z) {
      const { g, p } = z;
      const base = [p.uA, p.uB, p.uC, p.uD];
      const order = base[2] > base[0] && base[0] > base[3] && base[3] > base[1];
      const rowsU = [['u', base], ['a u + b', base.map(u => p.a * u + p.b)], ['u³', base.map(u => u ** 3)], ['rank 4,1,... (ordinal only)', [3, 1, 4, 2]]];
      const xs = [190, 250, 310, 370];
      ['A', 'B', 'C', 'D'].forEach((n, i) => D.text(g, n, xs[i], 22, { a: 'center', s: 13, b: true, c: z.col.ink }));
      D.text(g, 'EU(G)', 440, 22, { a: 'center', s: 12, b: true, c: z.col.cv });
      D.text(g, 'EU(S)', 505, 22, { a: 'center', s: 12, b: true, c: z.col.orange });
      rowsU.forEach(([name, u], r) => {
        const y = 56 + r * 52;
        D.text(g, name, 16, y + 4, { s: 12, b: true, c: z.col.ink2 });
        u.forEach((v, i) => tag(g, fmt(v, 2), xs[i], y, { s: 11.5, fill: z.col.bg, stroke: z.col.line, c: z.col.ink, mono: true }));
        const eg = p.pg * u[0] + (1 - p.pg) * u[1], es = p.ps * u[2] + (1 - p.ps) * u[3];
        tag(g, fmt(eg, 2), 440, y, { s: 11.5, fill: eg > es ? z.col.cv : z.col.surf, stroke: z.col.cv, c: eg > es ? '#fff' : z.col.cv, mono: true });
        tag(g, fmt(es, 2), 505, y, { s: 11.5, fill: es > eg ? z.col.orange : z.col.surf, stroke: z.col.orange, c: es > eg ? '#fff' : z.col.orange, mono: true });
      });
      const eg0 = p.pg * base[0] + (1 - p.pg) * base[1], es0 = p.ps * base[2] + (1 - p.ps) * base[3];
      return (order ? 'The outcome ranking C ≻ A ≻ D ≻ B holds. ' : '<b>Your u values no longer rank C ≻ A ≻ D ≻ B</b>, so the rows are not the same preferences. ') +
        `With u the agent picks <b>${eg0 > es0 ? 'G' : es0 > eg0 ? 'S' : 'either'}</b>. The a u + b row always agrees. Other order preserving rows may not, which is why expected utility needs cardinal utility, unique only up to a positive affine change.`;
    }
  });

  /* ================= 2.3 risk attitudes ================= */
  def('risk', {
    title: 'Risk attitude: compare E[u(X)] with u(E[X])',
    sub: 'A two outcome lottery on the curve u. The chord joins the two outcomes. Where the chord sits against the curve decides the attitude.',
    W: 560, H: 320,
    params: [
      { k: 'u', label: 'Utility of money', type: 'select', v: 'sqrt', opts: UOPTS },
      { k: 'x1', label: 'Low outcome x₁', type: 'range', v: 0, min: 0, max: 100 },
      { k: 'x2', label: 'High outcome x₂', type: 'range', v: 100, min: 0, max: 100 },
      { k: 'p', label: 'P(high outcome)', type: 'range', v: 0.5, min: 0, max: 1, step: 0.05 }
    ],
    tips: [
      { t: 'u = √x is concave: the chord lies under the curve, E[u] < u(E[X]) and the certainty equivalent is below the mean. Risk averse.', set: { u: 'sqrt', x1: 0, x2: 100, p: 0.5 } },
      { t: 'Switch to u = x². The chord lies above the curve. The certainty equivalent is above the mean. Risk loving, as in practice problem 5.', set: { u: 'sq', x1: 0, x2: 10, p: 0.5 } },
      { t: 'Switch to u = x. The chord is the curve. Certainty equivalent equals the mean. Risk neutral.', set: { u: 'lin' } },
      { t: 'Practice problem 4: √x with 100 at probability 0.2 and 0 otherwise. EU = 2, so the certainty equivalent is only 4, far below the sure 30.', set: { u: 'sqrt', x1: 0, x2: 100, p: 0.2 } }
    ],
    draw(z) {
      const { g, p } = z;
      const U = UF[p.u], lo = Math.min(p.x1, p.x2), hi = Math.max(p.x1, p.x2);
      const f = x => (p.u === 'ln' && x <= 0) ? U.f(0.5) : U.f(x);
      const xs = [0, 100], ys = [Math.min(0, f(0.5)), f(100) * 1.05];
      const m = D.axes(g, z, [60, 14, 300, 250], xs, ys, { nx: 4, ny: 4, xl: 'money x', yl: 'u(x)' });
      D.curve(g, x => p.u === 'ln' && x < 0.5 ? NaN : f(x), xs, m, z.col.cv, 2.5);
      const a = p.x1, b = p.x2, ex = (1 - p.p) * a + p.p * b, eu = (1 - p.p) * f(a) + p.p * f(b), uex = f(ex), ce = U.inv(eu);
      D.line(g, m.sx(a), m.sy(f(a)), m.sx(b), m.sy(f(b)), z.col.orange, 2, [5, 4]);
      D.circle(g, m.sx(a), m.sy(f(a)), 5, { fill: z.col.orange }); D.circle(g, m.sx(b), m.sy(f(b)), 5, { fill: z.col.orange });
      D.circle(g, m.sx(ex), m.sy(eu), 6, { fill: z.col.orange, stroke: '#fff', w: 2 });
      D.circle(g, m.sx(ex), m.sy(uex), 6, { fill: z.col.cv, stroke: '#fff', w: 2 });
      if (isFinite(ce)) { D.line(g, m.sx(ce), m.sy(eu), m.sx(ex), m.sy(eu), z.col.green, 3); D.circle(g, m.sx(ce), m.sy(eu), 5, { fill: z.col.green }); }
      const lx = 390;
      const L = [['E[X]', fmt(ex, 3), z.col.ink], ['u(E[X])', fmt(uex, 3), z.col.cv], ['E[u(X)]', fmt(eu, 3), z.col.orange], ['CE = u⁻¹(E[u])', fmt(ce, 3), z.col.green], ['risk premium', fmt(ex - ce, 3), z.col.ink2]];
      L.forEach(([k, v, c], i) => { D.text(g, k, lx, 36 + i * 36, { s: 12, b: true, c: z.col.ink2 }); D.text(g, v, lx, 54 + i * 36, { s: 14, b: true, c, mono: true }); });
      const att = Math.abs(eu - uex) < 1e-9 ? 'risk neutral' : eu < uex ? 'risk averse' : 'risk loving';
      void lo; void hi;
      return `${U.name}: E[u(X)] = ${fmt(eu, 3)} ${Math.abs(eu - uex) < 1e-9 ? '=' : eu < uex ? '<' : '>'} u(E[X]) = ${fmt(uex, 3)}, so this agent is <b>${att}</b>. The certainty equivalent ${fmt(ce, 2)} is the sure amount worth exactly as much as the lottery.`;
    }
  });

  def('stpete', {
    title: 'The St. Petersburg game, toss by toss',
    sub: 'Toss a fair coin until the first tail. If it comes on toss n you win 2ⁿ⁻¹. Bars show what each toss adds to the expected sum.',
    W: 560, H: 300,
    params: [
      { k: 'u', label: 'Value the money with', type: 'select', v: 'lin', opts: [['lin', 'money itself, u(x) = x'], ['ln', 'u(x) = ln x'], ['sqrt', 'u(x) = √x'], ['sq', 'u(x) = x²']] },
      { k: 'N', label: 'Tosses counted', type: 'range', v: 12, min: 1, max: 40 }
    ],
    tips: [
      { t: 'Money itself: every toss adds exactly 0.5, so the partial sum grows without limit. Expected money is infinite.', set: { u: 'lin', N: 30 } },
      { t: 'Log utility: the added terms (n − 1) ln 2 ⁄ 2ⁿ shrink fast and the sum settles at ln 2. The certainty equivalent is e^(ln 2) = 2.', set: { u: 'ln', N: 30 } },
      { t: 'Square root utility also converges, to about 1.707, so the game is worth about 2.91 for sure.', set: { u: 'sqrt', N: 30 } },
      { t: 'u(x) = x²: the terms 2ⁿ⁻² grow, so even expected utility is infinite. A concave u is what tames the paradox.', set: { u: 'sq', N: 10 } }
    ],
    draw(z) {
      const { g, p } = z;
      const fu = { lin: x => x, ln: x => Math.log(x), sqrt: x => Math.sqrt(x), sq: x => x * x }[p.u];
      const inv = { lin: y => y, ln: y => Math.exp(y), sqrt: y => y * y, sq: y => Math.sqrt(y) }[p.u];
      const terms = [];
      for (let n = 1; n <= p.N; n++) terms.push(Math.pow(0.5, n) * fu(Math.pow(2, n - 1)));
      const part = []; terms.reduce((a, t, i) => (part[i] = a + t), 0);
      const tmax = Math.max(...terms.map(Math.abs), 1e-9), smax = Math.max(...part.map(Math.abs), 1e-9);
      const m1 = D.axes(g, z, [60, 14, 210, 220], [0.5, p.N + 0.5], [0, tmax * 1.1], { nx: Math.min(4, p.N), ny: 2, fx: v => String(Math.round(v)), xl: 'toss n', yl: 'term' });
      const bw = 200 / p.N;
      terms.forEach((t, i) => D.rect(g, m1.sx(i + 1) - bw * 0.4, m1.sy(Math.max(0, t)), bw * 0.8, Math.abs(m1.sy(0) - m1.sy(t)), { fill: z.col.cv }));
      const m2 = D.axes(g, z, [330, 14, 210, 220], [0.5, p.N + 0.5], [0, smax * 1.1], { nx: Math.min(4, p.N), ny: 2, fx: v => String(Math.round(v)), xl: 'tosses counted', yl: 'partial sum' });
      part.forEach((s, i) => { D.circle(g, m2.sx(i + 1), m2.sy(s), 3, { fill: z.col.orange }); if (i) D.line(g, m2.sx(i), m2.sy(part[i - 1]), m2.sx(i + 1), m2.sy(s), z.col.orange, 1.5); });
      const S = part[part.length - 1];
      const lim = { lin: 'grows by 0.5 per toss, no limit', ln: 'limit ln 2 = 0.6931', sqrt: 'limit 1 ⁄ (2 − √2) = 1.7071', sq: 'grows without limit' }[p.u];
      return `After ${p.N} tosses the expected ${p.u === 'lin' ? 'money' : 'utility'} sum is <b>${fmt(S, 4)}</b> (${lim}). ` + (p.u === 'ln' || p.u === 'sqrt' ? `So the game is worth about <b>${fmt(inv(S), 3)}</b> for sure to this agent.` : 'With this u no finite price would stop a believer from paying.');
    }
  });

  /* ================= 3.1 backward induction ================= */
  def('backind', {
    title: 'Backward induction on the R&D and marketing tree',
    sub: 'Fold the tree from the right. At an N node take the expected value, at a D node keep the better branch. Press Step.',
    W: 560, H: 360,
    params: [
      { k: 'ps', label: 'P(R&D succeeds)', type: 'range', v: 0.625, min: 0, max: 1, step: 0.005 },
      { k: 'gs', label: 'P(good market | success)', type: 'range', v: 0.9, min: 0, max: 1, step: 0.05 },
      { k: 'gf', label: 'P(good market | failure)', type: 'range', v: 0.5, min: 0, max: 1, step: 0.05 },
      { k: 'mg', label: 'Market (m): good payoff', type: 'range', v: 13, min: -10, max: 30 },
      { k: 'mb', label: 'Market (m): bad payoff', type: 'range', v: -7, min: -20, max: 10 },
      { k: 'dg', label: 'Do not market (d): good payoff', type: 'range', v: 9, min: -10, max: 30 },
      { k: 'db', label: 'Do not market (d): bad payoff', type: 'range', v: -1, min: -20, max: 10 },
      { k: 'sk', label: 'Skip R&D: P(10) (else 0)', type: 'range', v: 0.5, min: 0, max: 1, step: 0.05 }
    ],
    tips: [
      { t: 'The lecture tree. Play it: market after success (11 > 8), do not market after failure (4 > 3), so go for R&D with 8.375 against 5.', set: { ps: 0.625, gs: 0.9, gf: 0.5, mg: 13, mb: -7, dg: 9, db: -1, sk: 0.5 }, play: true },
      { t: 'Make the bad market for a campaign only −2. Now marketing wins after failure too and the plan becomes "always market".', set: { mb: -2 }, play: true },
      { t: 'Drop the success chance to 0.2. The R&D branch falls to 0.2 × 11 + 0.8 × 4 = 5.4, barely above skipping.', set: { ps: 0.2 }, play: true }
    ],
    steps: () => 5,
    startAtZero: true,
    draw(z) {
      const { g, p } = z;
      const e = (q, a, b) => q * a + (1 - q) * b;
      const sm = e(p.gs, p.mg, p.mb), sd = e(p.gs, p.dg, p.db), fm = e(p.gf, p.mg, p.mb), fd = e(p.gf, p.dg, p.db);
      const vs = Math.max(sm, sd), vf = Math.max(fm, fd), vg = e(p.ps, vs, vf), vk = p.sk * 10;
      const leaf = s => ({ label: s });
      const sub = (pg, val, on, mk) => ({ kind: 'd', val: z.step >= on ? val : undefined, kids: [
        { edge: 'm', on: z.step >= on && mk, off: z.step >= on && !mk, node: { kind: 'n', val: z.step >= on ? e(pg, p.mg, p.mb) : undefined, kids: [{ edge: fmt(pg, 2), node: leaf(String(p.mg)) }, { edge: fmt(1 - pg, 2), node: leaf(String(p.mb)) }] } },
        { edge: 'd', on: z.step >= on && !mk, off: z.step >= on && mk, node: { kind: 'n', val: z.step >= on ? e(pg, p.dg, p.db) : undefined, kids: [{ edge: fmt(pg, 2), node: leaf(String(p.dg)) }, { edge: fmt(1 - pg, 2), node: leaf(String(p.db)) }] } }] });
      const goR = vg >= vk;
      const root = { kind: 'd', val: z.step >= 5 ? Math.max(vg, vk) : undefined, kids: [
        { edge: 'g', on: z.step >= 5 && goR, off: z.step >= 5 && !goR, node: { kind: 'n', val: z.step >= 3 ? vg : undefined, kids: [
          { edge: 'success ' + fmt(p.ps, 3), node: sub(p.gs, vs, 1, sm >= sd) },
          { edge: 'failure ' + fmt(1 - p.ps, 3), node: sub(p.gf, vf, 2, fm >= fd) }] } },
        { edge: 's', on: z.step >= 5 && !goR, off: z.step >= 5 && goR, node: { kind: 'n', val: z.step >= 4 ? vk : undefined, kids: [{ edge: fmt(p.sk, 2), node: leaf('10') }, { edge: fmt(1 - p.sk, 2), node: leaf('0') }] } }] };
      layoutTree(root, 30, z.W - 30, 40, 78);
      drawTree(g, z, root, { es: 10, ls: 11, mono: true });
      const msg = [
        'Start at the last decisions, the marketing choices after success and after failure.',
        `After success: E[m] = ${fmt(sm, 3)}, E[d] = ${fmt(sd, 3)}, keep <b>${sm >= sd ? 'm' : 'd'}</b> worth ${fmt(vs, 3)}.`,
        `After failure: E[m] = ${fmt(fm, 3)}, E[d] = ${fmt(fd, 3)}, keep <b>${fm >= fd ? 'm' : 'd'}</b> worth ${fmt(vf, 3)}.`,
        `R&D chance node: ${fmt(p.ps, 3)} × ${fmt(vs, 3)} + ${fmt(1 - p.ps, 3)} × ${fmt(vf, 3)} = <b>${fmt(vg, 4)}</b>.`,
        `Skip branch: ${fmt(p.sk, 2)} × 10 = <b>${fmt(vk, 3)}</b>.`,
        `Root: ${fmt(vg, 4)} against ${fmt(vk, 3)}. Plan: <b>${goR ? `go for R&D, then ${sm >= sd ? 'm' : 'd'} after success and ${fm >= fd ? 'm' : 'd'} after failure` : 'skip R&D'}</b>.`];
      return msg[z.step];
    }
  });

  /* ================= 3.2 discounting and consumption ================= */
  def('discount', {
    title: 'Bringing future payments back to today',
    sub: 'Each bar is a payment. The violet part is what it is worth today: amount × δᵗ for exponential, amount ⁄ (1 + k t) for hyperbolic.',
    W: 560, H: 290,
    params: [
      { k: 'pay', label: 'Payments at the end of years 1, 2, 3, …', type: 'text', v: '200, 150, 300' },
      { k: 'r', label: 'Interest rate r (%)', type: 'range', v: 11.1, min: 0, max: 100, step: 0.1 },
      { k: 'kind', label: 'Discounting', type: 'select', v: 'exp', opts: [['exp', 'exponential, δ = 1 ⁄ (1 + r)'], ['hyp', 'hyperbolic, 1 ⁄ (1 + k t)']] },
      { k: 'k', label: 'k for hyperbolic', type: 'range', v: 0.2, min: 0, max: 2, step: 0.05, show: p => p.kind === 'hyp' }
    ],
    tips: [
      { t: 'Practice problem B: 200, 150, 300 with δ = 0.9 (r = 11.1%). The present value is about 520.2.', set: { pay: '200, 150, 300', r: 11.1111, kind: 'exp' } },
      { t: 'Set r = 0. δ = 1 and the future is worth exactly as much as today, a perfectly patient agent.', set: { r: 0 } },
      { t: 'Set r = 100%. δ = 0.5 and each year halves the value, like the impatient patient who needs money for an operation now.', set: { r: 100 } },
      { t: 'Switch to hyperbolic. Early years fall fast but later years fall slowly, the shape that makes plans time inconsistent.', set: { kind: 'hyp', k: 0.5, pay: '100, 100, 100, 100, 100, 100, 100, 100' } }
    ],
    draw(z) {
      const { g, p } = z;
      const pay = String(p.pay).split(/[\s,]+/).map(num).filter(v => isFinite(v)).slice(0, 12);
      if (!pay.length) return 'Write payments like 200, 150, 300.';
      const d = 1 / (1 + p.r / 100);
      const w = t => p.kind === 'exp' ? Math.pow(d, t) : 1 / (1 + p.k * t);
      const mx = Math.max(...pay.map(Math.abs), 1);
      const m = D.axes(g, z, [60, 16, 470, 210], [0.4, pay.length + 0.6], [0, mx * 1.1], { nx: Math.min(pay.length, 6), ny: 3, fx: v => 'year ' + Math.round(v), yl: 'amount' });
      const bw = Math.min(46, 400 / pay.length);
      let pv = 0;
      pay.forEach((a, i) => {
        const t = i + 1, now = a * w(t); pv += now;
        D.rect(g, m.sx(t) - bw / 2, m.sy(a), bw, m.sy(0) - m.sy(a), { fill: z.col.bg, stroke: z.col.line });
        D.rect(g, m.sx(t) - bw / 2, m.sy(now), bw, m.sy(0) - m.sy(now), { fill: z.col.cv });
        D.text(g, fmt(now, 1), m.sx(t), m.sy(now) - 4, { a: 'center', s: 10.5, b: true, c: z.col.ink });
      });
      return `δ = 1 ⁄ (1 + r) = <b>${fmt(d, 4)}</b>. Present value = Σ amountₜ × ${p.kind === 'exp' ? 'δᵗ' : '1 ⁄ (1 + k t)'} = <b>${fmt(pv, 2)}</b> from a total of ${fmt(pay.reduce((a, b) => a + b, 0), 2)}.`;
    }
  });

  def('consume', {
    title: 'Splitting a budget K over time',
    sub: 'Maximise u(x₁) + δ u(x₂) + δ² u(x₃). The bars are the best plan. For two periods the curve shows the total payoff of every split.',
    W: 560, H: 300,
    params: [
      { k: 'T', label: 'Periods', type: 'select', v: '3', opts: [['2', '2 periods'], ['3', '3 periods']] },
      { k: 'u', label: 'Per period payoff', type: 'select', v: 'ln', opts: [['ln', 'u(x) = ln x (concave)'], ['sqrt', 'u(x) = √x (concave)'], ['lin', 'u(x) = x (linear)'], ['sq', 'u(x) = x² (convex)']] },
      { k: 'd', label: 'Discount factor δ', type: 'range', v: 0.9, min: 0.05, max: 1, step: 0.05 },
      { k: 'K', label: 'Total income K', type: 'range', v: 100, min: 10, max: 300, step: 1 }
    ],
    tips: [
      { t: 'ln with 3 periods: the plan is K ⁄ (1 + δ + δ²), δ K ⁄ (…), δ² K ⁄ (…). Consumption falls a little each period.', set: { T: '3', u: 'ln', d: 0.9 } },
      { t: 'Linear utility: no reason to smooth, and δ < 1 makes today the best period. Everything is spent in period 1.', set: { u: 'lin' } },
      { t: 'Convex u = x² with two periods: the curve has a minimum in the middle, so the best plan is a corner. Setting the derivative to zero would find the worst split.', set: { T: '2', u: 'sq', d: 0.8, K: 10 } },
      { t: 'Quiz 1, question 4: three periods, u = x², δ = 0.5. The answer is (K, 0, 0).', set: { T: '3', u: 'sq', d: 0.5 } },
      { t: 'Practice problem D: √x with K = 181 and δ = 0.9 gives 100 and 81.', set: { T: '2', u: 'sqrt', d: 0.9, K: 181 } }
    ],
    draw(z) {
      const { g, p } = z;
      const T = +p.T, d = p.d, K = p.K, w = [1, d, d * d].slice(0, T);
      let plan;
      if (p.u === 'ln') { const s = w.reduce((a, b) => a + b, 0); plan = w.map(x => K * x / s); }
      else if (p.u === 'sqrt') { const s = w.reduce((a, b) => a + b * b, 0); plan = w.map(x => K * x * x / s); }
      else { const best = w.indexOf(Math.max(...w)); plan = w.map((_, i) => i === best ? K : 0); }
      const U = { ln: x => Math.log(x), sqrt: x => Math.sqrt(x), lin: x => x, sq: x => x * x }[p.u];
      const tot = plan.reduce((a, x, i) => a + w[i] * (x > 0 ? U(x) : (p.u === 'ln' ? -Infinity : 0)), 0);
      const m = D.axes(g, z, [60, 16, 190, 220], [0.4, T + 0.6], [0, K], { nx: T - 1 || 1, ny: 2, fx: v => 'x' + Math.round(v), yl: 'amount' });
      plan.forEach((x, i) => { D.rect(g, m.sx(i + 1) - 22, m.sy(x), 44, m.sy(0) - m.sy(x), { fill: z.col.cv }); D.text(g, fmt(x, 2), m.sx(i + 1), m.sy(x) - 5, { a: 'center', s: 11, b: true, c: z.col.ink }); });
      if (T === 2) {
        const v = x => U(Math.max(1e-9, x)) + d * U(Math.max(1e-9, K - x));
        const lo = p.u === 'ln' ? v(K * 0.02) : Math.min(v(0), v(K), v(K / 2)), hi = Math.max(v(plan[0]), v(0), v(K));
        const m2 = D.axes(g, z, [330, 16, 200, 220], [0, K], [lo, hi + (hi - lo) * 0.1 + 1e-9], { nx: 2, ny: 2, xl: 'x₁ (rest is x₂)', yl: 'total payoff' });
        D.curve(g, x => p.u === 'ln' && (x <= K * 0.02 || x >= K * 0.98) ? NaN : v(x), [0, K], m2, z.col.orange, 2);
        D.circle(g, m2.sx(plan[0]), m2.sy(v(plan[0])), 6, { fill: z.col.green, stroke: '#fff', w: 2 });
      } else {
        const lx = 300;
        D.text(g, 'Optimal plan', lx, 40, { s: 13, b: true, c: z.col.ink });
        const form = { ln: ['K ⁄ (1 + δ + δ²)', 'δ K ⁄ (1 + δ + δ²)', 'δ² K ⁄ (1 + δ + δ²)'], sqrt: ['K ⁄ (1 + δ² + δ⁴)', 'δ² K ⁄ (…)', 'δ⁴ K ⁄ (…)'], lin: ['K', '0', '0'], sq: ['K', '0', '0'] }[p.u];
        form.forEach((f, i) => D.text(g, `x${i + 1} = ${f} = ${fmt(plan[i], 3)}`, lx, 66 + i * 24, { s: 12, c: z.col.ink, mono: true }));
        D.text(g, p.u === 'ln' ? 'FOC: 1 ⁄ x₁ = δ ⁄ x₂ = δ² ⁄ x₃' : p.u === 'sqrt' ? 'FOC: 1 ⁄ √x₁ = δ ⁄ √x₂ = δ² ⁄ √x₃' : 'Corner: the largest weight wins', lx, 150, { s: 12, b: true, c: z.col.cv });
      }
      const curve = p.u === 'ln' || p.u === 'sqrt' ? 'Concave u rewards spreading, discounting tilts the spread toward today.' : p.u === 'lin' ? 'Linear u: all weight goes to the period with the biggest discount weight, period 1.' : 'Convex u: splitting is worse than either extreme, so the answer is a corner. With δ < 1 the corner is period 1.';
      return `Best plan ${plan.map(x => fmt(x, 2)).join(', ')} with total payoff ${fmt(tot, 3)}. ${curve}`;
    }
  });

  /* ================= 3.3 value of information ================= */
  def('voi', {
    title: 'What is perfect information worth?',
    sub: 'Without information you pick one action for every state. With an oracle you pick the best action state by state. The gap is the value of information.',
    W: 560, H: 300,
    params: [
      { k: 'names', label: 'Action names', type: 'text', v: 'MBA, No MBA' },
      { k: 'tab', label: 'State, probability, payoff of each action', type: 'area', v: 'Good 0.25 22 12\nMedium 0.5 6 8\nPoor 0.25 2 4' },
      { k: 'fee', label: 'Price the oracle asks', type: 'range', v: 1, min: 0, max: 20, step: 0.25 }
    ],
    tips: [
      { t: 'The MBA example (net of its cost 10). No information: 9 against 8, get the MBA. With the oracle: 10.5. Information is worth 1.5.', set: { names: 'MBA, No MBA', tab: 'Good 0.25 22 12\nMedium 0.5 6 8\nPoor 0.25 2 4', fee: 1 } },
      { t: 'Practice problem C: outdoor or indoor venue. 27.5 without a forecast, 37.5 with one, so a perfect forecast is worth 10.', set: { names: 'Outdoor, Indoor', tab: 'Sunny 0.5 50 30\nRainy 0.5 -20 25', fee: 5 } },
      { t: 'Make one action best in every state. The oracle never changes the decision and information is worth exactly 0, never less.', set: { names: 'A, B', tab: 'S1 0.5 10 5\nS2 0.5 8 3', fee: 0 } },
      { t: 'Raise the oracle price above the value of information. Paying would leave you worse off than deciding now.', set: { fee: 3 } }
    ],
    draw(z) {
      const { g, p } = z;
      const names = String(p.names).split(',').map(s => s.trim()).filter(Boolean);
      const st = rows(p.tab).filter(r => r.nums.length >= 2).slice(0, 6);
      if (!st.length) return 'Write lines like "Good 0.25 22 12".';
      const na = Math.max(1, Math.min(4, Math.min(...st.map(r => r.nums.length - 1))));
      const tot = st.reduce((a, r) => a + r.nums[0], 0) || 1;
      const pr = st.map(r => r.nums[0] / tot);
      const eu = [...Array(na)].map((_, a) => st.reduce((s, r, i) => s + pr[i] * r.nums[1 + a], 0));
      const bestA = eu.indexOf(Math.max(...eu));
      const withI = st.reduce((s, r, i) => s + pr[i] * Math.max(...r.nums.slice(1, 1 + na)), 0);
      const voi = withI - eu[bestA];
      const cx = [150, 230, 310, 390].slice(0, na), y0 = 30, rh = 30;
      D.text(g, 'state (p)', 16, y0, { s: 12, b: true, c: z.col.ink2 });
      cx.forEach((x, a) => D.text(g, names[a] || 'action ' + (a + 1), x, y0, { a: 'center', s: fit(g, names[a] || 'action', 76, 12), b: true, c: z.col.ink }));
      D.text(g, 'oracle picks', 470, y0, { a: 'center', s: 12, b: true, c: z.col.orange });
      st.forEach((r, i) => {
        const y = y0 + 26 + i * rh, best = Math.max(...r.nums.slice(1, 1 + na));
        D.text(g, `${r.name} (${fmt(pr[i], 3)})`, 16, y + 4, { s: 12, c: z.col.ink });
        cx.forEach((x, a) => tag(g, fmt(r.nums[1 + a], 2), x, y, { s: 11.5, fill: r.nums[1 + a] === best ? z.col.orange : z.col.bg, stroke: z.col.line, c: r.nums[1 + a] === best ? '#fff' : z.col.ink, mono: true }));
        D.text(g, fmt(best, 2), 470, y + 4, { a: 'center', s: 12, b: true, c: z.col.orange, mono: true });
      });
      const yb = y0 + 26 + st.length * rh + 10;
      D.text(g, 'expected', 16, yb + 4, { s: 12, b: true, c: z.col.ink2 });
      cx.forEach((x, a) => tag(g, fmt(eu[a], 3), x, yb, { s: 11.5, fill: a === bestA ? z.col.cv : z.col.surf, stroke: z.col.cv, c: a === bestA ? '#fff' : z.col.cv, mono: true }));
      tag(g, fmt(withI, 3), 470, yb, { s: 11.5, fill: z.col.orange, stroke: z.col.orange, c: '#fff', mono: true });
      const yb2 = Math.min(z.H - 40, yb + 40);
      const sc = 380 / Math.max(Math.abs(withI), Math.abs(eu[bestA]), 1e-9);
      D.rect(g, 140, yb2, Math.max(2, eu[bestA] * sc), 12, { fill: z.col.cv });
      D.rect(g, 140, yb2 + 16, Math.max(2, withI * sc), 12, { fill: z.col.orange });
      D.text(g, 'no info', 132, yb2 + 10, { a: 'right', s: 11, c: z.col.ink2 }); D.text(g, 'with oracle', 132, yb2 + 26, { a: 'right', s: 11, c: z.col.ink2 });
      return `No information: choose <b>${names[bestA] || 'action ' + (bestA + 1)}</b> with ${fmt(eu[bestA], 3)}. With the oracle: ${fmt(withI, 3)}. Value of information = <b>${fmt(voi, 3)}</b>. ` +
        (p.fee < voi ? `At a price of ${p.fee} the oracle is worth buying (you keep ${fmt(voi - p.fee, 3)}).` : p.fee > voi ? `At a price of ${p.fee} do not buy it, you would lose ${fmt(p.fee - voi, 3)}.` : 'At this price you are indifferent.');
    }
  });

  return { tw, rr, fit, tag, wrap, fmt, num, rows, UF, layoutTree, layoutH, drawTree };
})();
