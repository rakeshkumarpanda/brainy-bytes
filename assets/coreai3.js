/* ===== Core AI animations, part 3: probability, Bayesian networks, causality and reinforcement learning.
   Same rules as parts 1 and 2: every animation starts empty and each Step adds one explained piece. ===== */
(() => {
  const { trace, esc } = CAI;
  const { D } = CVZ;
  const { tag, rr, tw, fit, wrap } = AIZ;
  const f3 = v => (Math.round(v * 1000) / 1000).toString();
  const f4 = v => (Math.round(v * 10000) / 10000).toString();
  const TF = v => v ? 'true' : 'false';

  /* ---------- a small toolkit for Bayesian networks with true or false variables ---------- */
  const BN = (() => {
    /* net: { order: [names in topological order], par: {X: [parents]}, cpt: {X: {key: P(X = true | parents)}} }
       key is the parents' values as a string of T and F, in the order of par[X] ('' for a root) */
    const key = (net, X, a) => net.par[X].map(u => a[u] ? 'T' : 'F').join('');
    const pr = (net, X, v, a) => { const p = net.cpt[X][key(net, X, a)]; return v ? p : 1 - p; };
    function joint(net, a) { let p = 1; net.order.forEach(X => { p *= pr(net, X, a[X], a); }); return p; }
    function all(vars) {
      const out = [];
      for (let m = 0; m < (1 << vars.length); m++) { const a = {}; vars.forEach((v, i) => { a[v] = !((m >> (vars.length - 1 - i)) & 1); }); out.push(a); }
      return out;
    }
    /* exact P(Q = true | e) by summing the full joint */
    function exact(net, Q, ev) {
      let t = 0, s = 0;
      all(net.order).forEach(a => { if (Object.keys(ev).every(k => a[k] === ev[k])) { const p = joint(net, a); s += p; if (a[Q]) t += p; } });
      return s ? t / s : NaN;
    }
    /* factors: { vars: [...], t: [values] } with index bits in vars order, first var = highest bit, bit 0 means true */
    const idx = (vars, a) => vars.reduce((m, v) => m * 2 + (a[v] ? 0 : 1), 0);
    function fromCpt(net, X, ev) {
      const vars = [...net.par[X], X].filter(v => !(v in ev));
      const t = all(vars).map(a => pr(net, X, (X in ev ? ev[X] : a[X]), Object.assign({}, a, ev)));
      return { vars, t, name: `P(${X}${net.par[X].length ? ' | ' + net.par[X].join(', ') : ''})` };
    }
    function mul(f, g) {
      const vars = [...f.vars, ...g.vars.filter(v => !f.vars.includes(v))];
      return { vars, t: all(vars).map(a => f.t[idx(f.vars, a)] * g.t[idx(g.vars, a)]) };
    }
    function sumOut(f, X) {
      const vars = f.vars.filter(v => v !== X);
      return { vars, t: all(vars).map(a => f.t[idx(f.vars, Object.assign({}, a, { [X]: true }))] + f.t[idx(f.vars, Object.assign({}, a, { [X]: false }))]) };
    }
    return { key, pr, joint, all, exact, idx, fromCpt, mul, sumOut };
  })();

  const ALARM = {
    order: ['Burglary', 'Earthquake', 'Alarm', 'JohnCalls', 'MaryCalls'],
    par: { Burglary: [], Earthquake: [], Alarm: ['Burglary', 'Earthquake'], JohnCalls: ['Alarm'], MaryCalls: ['Alarm'] },
    cpt: { Burglary: { '': 0.001 }, Earthquake: { '': 0.002 }, Alarm: { TT: 0.95, TF: 0.94, FT: 0.29, FF: 0.001 }, JohnCalls: { T: 0.90, F: 0.05 }, MaryCalls: { T: 0.70, F: 0.01 } },
    pos: { Burglary: [0.2, 0.15], Earthquake: [0.8, 0.15], Alarm: [0.5, 0.5], JohnCalls: [0.22, 0.85], MaryCalls: [0.78, 0.85] }
  };
  const SPRINK = {
    order: ['Cloudy', 'Sprinkler', 'Rain', 'WetGrass'],
    par: { Cloudy: [], Sprinkler: ['Cloudy'], Rain: ['Cloudy'], WetGrass: ['Sprinkler', 'Rain'] },
    cpt: { Cloudy: { '': 0.5 }, Sprinkler: { T: 0.1, F: 0.5 }, Rain: { T: 0.8, F: 0.2 }, WetGrass: { TT: 0.99, TF: 0.90, FT: 0.90, FF: 0.0 } },
    pos: { Cloudy: [0.5, 0.13], Sprinkler: [0.18, 0.5], Rain: [0.82, 0.5], WetGrass: [0.5, 0.87] }
  };

  /* draw a directed graph. pos in 0..1 of the box. o: { fill: name => colour, ink: name => colour, sub: name => text, cut: [[u, v]] } */
  function drawNet(z, net, box, o = {}) {
    const { g } = z, c = z.col;
    const [X0, Y0, W, H] = box;
    const P = {};
    net.order.forEach(v => { P[v] = [X0 + net.pos[v][0] * W, Y0 + net.pos[v][1] * H]; });
    const bw = v => Math.max(54, tw(g, v, { s: 11.5, b: true }) + 16), bh = 26;
    net.order.forEach(v => net.par[v].forEach(u => {
      const [x1, y1] = P[u], [x2, y2] = P[v];
      const cut = (o.cut || []).some(([a, b]) => a === u && b === v);
      const L = Math.hypot(x2 - x1, y2 - y1), ux = (x2 - x1) / L, uy = (y2 - y1) / L;
      const clip = (w, dx, dy) => Math.min(Math.abs(dx) > 0.01 ? (w / 2) / Math.abs(dx) : 1e9, Math.abs(dy) > 0.01 ? (bh / 2) / Math.abs(dy) : 1e9);
      const s1 = clip(bw(u), ux, uy) + 2, s2 = clip(bw(v), ux, uy) + 3;
      const col = o.edge ? o.edge(u, v) : c.ink2;
      if (cut) { D.line(g, x1 + ux * s1, y1 + uy * s1, x2 - ux * s2, y2 - uy * s2, c.line, 1.4, [5, 5]); const mx = (x1 + x2) / 2, my = (y1 + y2) / 2; D.line(g, mx - 7, my - 7, mx + 7, my + 7, c.red, 2.4); D.line(g, mx - 7, my + 7, mx + 7, my - 7, c.red, 2.4); }
      else D.arrow(g, x1 + ux * s1, y1 + uy * s1, x2 - ux * s2, y2 - uy * s2, col, o.edgeW ? o.edgeW(u, v) : 1.6);
    }));
    net.order.forEach(v => {
      const [x, y] = P[v], w = bw(v);
      const fill = o.fill ? o.fill(v) : c.surf;
      rr(g, x - w / 2, y - bh / 2, w, bh, 7, { fill, stroke: o.stroke ? o.stroke(v) : c.ink2, w: 1.5 });
      D.text(g, v, x, y + 1, { a: 'center', bl: 'middle', s: 11.5, b: true, c: o.ink ? o.ink(v) : c.ink });
      if (o.sub && o.sub(v)) { const st = o.sub(v), sw = tw(g, st, { s: 10.5, b: true }) + 8; rr(g, x - sw / 2, y + bh / 2 + 3, sw, 14, 4, { fill: c.bg }); D.text(g, st, x, y + bh / 2 + 13, { a: 'center', s: 10.5, b: true, c: o.subc ? o.subc(v) : c.cv }); }
    });
    return P;
  }

  /* =====================================================================================================
     9.1  Inference by enumeration over a full joint distribution (AIMA 13.3, the dentist example)
     ===================================================================================================== */
  trace('joint', {
    title: 'Answer a question from the full joint distribution',
    sub: 'The table lists the probability of every possible world. To get P(query | evidence): keep the rows that match the evidence, add them up for each value of the query, then divide by their total (normalise).',
    W: 660, H: 400, speed: 1300,
    params: [
      { k: 'q', label: 'Query variable', type: 'select', v: 'Cavity', opts: [['Cavity', 'Cavity'], ['Toothache', 'Toothache'], ['Catch', 'Catch']] },
      { k: 'et', label: 'Evidence on Toothache', type: 'select', v: 'T', opts: [['-', 'not known'], ['T', 'true'], ['F', 'false']] },
      { k: 'ec', label: 'Evidence on Catch', type: 'select', v: '-', opts: [['-', 'not known'], ['T', 'true'], ['F', 'false']] },
      { k: 'ev', label: 'Evidence on Cavity', type: 'select', v: '-', opts: [['-', 'not known'], ['T', 'true'], ['F', 'false']] },
      { k: 'probs', label: 'The 8 probabilities, in the table order (they must add up to 1)', type: 'text', v: '0.108 0.012 0.072 0.008 0.016 0.064 0.144 0.576' }
    ],
    tips: [
      { t: 'The textbook question: P(Cavity | toothache). The two matching rows with a cavity add up to 0.12, the total with a toothache is 0.2, so the answer is 0.6.', set: { q: 'Cavity', et: 'T', ec: '-', ev: '-' }, play: true },
      { t: 'More evidence: the probe also catches. P(Cavity | toothache, catch) rises to about 0.871.', set: { q: 'Cavity', et: 'T', ec: 'T', ev: '-' }, play: true },
      { t: 'No evidence at all. This is just the marginal (prior) probability P(Cavity) = 0.2: add up all rows with a cavity.', set: { q: 'Cavity', et: '-', ec: '-', ev: '-' }, play: true },
      { t: 'Conditional independence. P(Catch | cavity) = 0.9, and adding toothache as evidence leaves it at 0.9: given Cavity, Toothache tells us nothing more about Catch.', set: { q: 'Catch', et: 'T', ec: '-', ev: 'T' }, play: true }
    ],
    frames(p) {
      const vals = String(p.probs).replace(/−/g, '-').split(/[\s,]+/).filter(Boolean).map(Number);
      if (vals.length !== 8 || vals.some(v => isNaN(v) || v < 0)) throw new Error('Please give exactly 8 probabilities, each 0 or more, separated by spaces.');
      const tot = vals.reduce((a, b) => a + b, 0);
      if (Math.abs(tot - 1) > 0.002) throw new Error(`The 8 probabilities add up to ${f4(tot)}, not 1.`);
      const V = ['Toothache', 'Catch', 'Cavity'];
      /* table order of AIMA figure 13.3: cavity first, then toothache, then catch */
      const rows = [];
      [true, false].forEach(cv => [true, false].forEach(t => [true, false].forEach(ch => rows.push({ Toothache: t, Catch: ch, Cavity: cv }))));
      rows.forEach((r, i) => { r.p = vals[i]; });
      const ev = {};
      if (p.et !== '-') ev.Toothache = p.et === 'T';
      if (p.ec !== '-') ev.Catch = p.ec === 'T';
      if (p.ev !== '-') ev.Cavity = p.ev === 'T';
      if (p.q in ev) throw new Error(`${p.q} is the query, so it cannot also be evidence. Set its evidence to "not known".`);
      const es = Object.keys(ev).map(k => `${k} = ${TF(ev[k])}`).join(', ');
      const match = rows.map(r => Object.keys(ev).every(k => r[k] === ev[k]));
      const fr = [];
      fr.push({ rows, match: null, say: `The full joint distribution of three true or false variables has 2 × 2 × 2 = 8 rows, one for each possible world. Each row gives the probability of that world, and the 8 numbers add up to 1. We want P(${p.q}${es ? ' | ' + es : ''}).` });
      if (es) fr.push({ rows, match, say: `Keep only the rows that agree with the evidence (${es}). The grey rows are worlds the evidence rules out, so they play no part. ${match.filter(Boolean).length} rows remain.` });
      else fr.push({ rows, match, say: `There is no evidence, so every row is kept. The answer will be the prior (marginal) probability of ${p.q}.` });
      const tIdx = rows.map((r, i) => i).filter(i => match[i] && rows[i][p.q]);
      const fIdx = rows.map((r, i) => i).filter(i => match[i] && !rows[i][p.q]);
      const st = tIdx.reduce((a, i) => a + rows[i].p, 0), sf = fIdx.reduce((a, i) => a + rows[i].p, 0);
      const pe = st + sf;
      fr.push({ rows, match, hiT: tIdx, st, say: `Add the kept rows where ${p.q} is true (green): ${tIdx.map(i => f3(rows[i].p)).join(' + ')} = ${f4(st)}. This is P(${p.q} = true${es ? ', ' + es : ''}).` });
      fr.push({ rows, match, hiT: tIdx, hiF: fIdx, st, sf, say: `Add the kept rows where ${p.q} is false (orange): ${fIdx.map(i => f3(rows[i].p)).join(' + ')} = ${f4(sf)}. This is P(${p.q} = false${es ? ', ' + es : ''}).` });
      if (pe <= 0) { fr.push({ rows, match, st, sf, say: 'The evidence has probability 0 in this table, so the conditional probability is not defined.' }); return fr; }
      fr.push({ rows, match, hiT: tIdx, hiF: fIdx, st, sf, pe, say: `The two sums add up to ${f4(pe)}, which is P(${es || 'anything'}). The normalisation constant is α = 1 ÷ ${f4(pe)} = ${f3(1 / pe)}.` });
      const ans = st / pe;
      fr.push({ rows, match, hiT: tIdx, hiF: fIdx, st, sf, pe, ans, say: `Divide both sums by ${f4(pe)}: P(${p.q}${es ? ' | ' + es : ''}) = ⟨${f4(st)}, ${f4(sf)}⟩ ÷ ${f4(pe)} = ⟨${f3(ans)}, ${f3(1 - ans)}⟩. The two numbers now add up to 1.` });
      if (es) {
        const prior = rows.filter(r => r[p.q]).reduce((a, r) => a + r.p, 0);
        fr.push({ rows, match, hiT: tIdx, hiF: fIdx, st, sf, pe, ans, prior, say: `Compare with the prior P(${p.q} = true) = ${f3(prior)} (all rows with ${p.q} true). The evidence ${Math.abs(ans - prior) < 0.0005 ? 'leaves it unchanged, so here the query is independent of the evidence' : ans > prior ? `raises it to ${f3(ans)}` : `lowers it to ${f3(ans)}`}.`, done: true });
      } else fr[fr.length - 1].done = true;
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const V = ['Toothache', 'Catch', 'Cavity'];
      const x0 = 18, y0 = 30, cw = [92, 70, 72, 70], rh = 32;
      let x = x0;
      ['Toothache', 'Catch', 'Cavity', 'P'].forEach((h, i) => { D.text(g, h, x + cw[i] / 2, y0 - 8, { a: 'center', s: 12, b: true, c: c.ink }); x += cw[i]; });
      f.rows.forEach((r, i) => {
        const y = y0 + i * rh, off = f.match && !f.match[i];
        const hiT = (f.hiT || []).includes(i), hiF = (f.hiF || []).includes(i);
        rr(g, x0, y + 2, cw.reduce((a, b) => a + b, 0), rh - 4, 5, { fill: hiT ? c.green + '33' : hiF ? c.orange + '33' : c.surf, stroke: hiT ? c.green : hiF ? c.orange : c.line, w: hiT || hiF ? 2 : 1 });
        let xx = x0;
        [...V.map(v => TF(r[v])), f3(r.p)].forEach((s, k) => { D.text(g, s, xx + cw[k] / 2, y + rh / 2 + 4, { a: 'center', s: 12, mono: k === 3, b: k === 3, c: off ? c.line : c.ink }); xx += cw[k]; });
      });
      const rx = 350, ry = 50;
      const line = (s, y, col, b) => D.text(g, s, rx, y, { s: fit(g, s, z.W - rx - 14, 13, { b }), b, c: col || c.ink });
      if (f.st !== undefined) line(`sum where query is true: ${f4(f.st)}`, ry, c.green, true);
      if (f.sf !== undefined) line(`sum where query is false: ${f4(f.sf)}`, ry + 28, c.orange, true);
      if (f.pe !== undefined) line(`total P(evidence) = ${f4(f.pe)}`, ry + 56, c.ink, true);
      if (f.ans !== undefined) {
        const bx = rx, by = ry + 90, bw = z.W - rx - 30;
        D.text(g, 'Answer after dividing by the total', bx, by, { s: 12, b: true, c: c.ink2 });
        [[f.ans, 'true', c.green], [1 - f.ans, 'false', c.orange]].forEach(([v, lab, col], k) => {
          const yy = by + 18 + k * 40;
          rr(g, bx, yy, bw, 24, 5, { fill: c.bg, stroke: c.line, w: 1 });
          rr(g, bx, yy, Math.max(2, bw * v), 24, 5, { fill: col });
          D.text(g, `${lab}: ${f3(v)}`, bx + 8, yy + 17, { s: 12.5, b: true, c: v > 0.25 ? '#fff' : c.ink });
        });
      }
      if (f.prior !== undefined) line(`prior, with no evidence: ${f3(f.prior)}`, ry + 210, c.ink2, true);
      if (f.done) tag(g, 'done', z.W - 40, 20, { s: 12.5, fill: c.green, stroke: c.green, c: '#fff' });
    }
  });

  /* =====================================================================================================
     9.2  d-separation: is every path between X and Y blocked by the evidence Z?
     ===================================================================================================== */
  const DNETS = {
    alarm: ALARM,
    sprinkler: SPRINK,
    chain: { order: ['A', 'B', 'C', 'D', 'E'], par: { A: [], B: ['A'], C: ['B'], D: ['C', 'B'], E: ['C'] }, pos: { A: [0.12, 0.2], B: [0.38, 0.2], C: [0.64, 0.2], D: [0.5, 0.8], E: [0.88, 0.8] } }
  };
  function parseNet(text) {
    const par = {}, names = [];
    const add = v => { if (!names.includes(v)) { names.push(v); par[v] = []; } };
    String(text).split(/\n|,/).map(s => s.trim()).filter(Boolean).forEach(l => {
      const m = l.match(/^([A-Za-z][\w]*)\s*(?:->|→)\s*([A-Za-z][\w]*)$/);
      if (!m) { if (/^[A-Za-z]\w*$/.test(l)) { add(l); return; } throw new Error(`"${l}" is not an edge. Write edges like "A -> B", one per line.`); }
      add(m[1]); add(m[2]); if (!par[m[2]].includes(m[1])) par[m[2]].push(m[1]);
    });
    if (names.length < 2) throw new Error('Please give at least one edge, such as "A -> B".');
    if (names.length > 8) throw new Error('Please use at most 8 variables, so the drawing stays readable.');
    const order = [], left = names.slice();
    while (left.length) {
      const i = left.findIndex(v => par[v].every(u => order.includes(u)));
      if (i < 0) throw new Error('The edges make a cycle. A Bayesian network must be a directed graph with no cycles.');
      order.push(left.splice(i, 1)[0]);
    }
    const rank = {};
    order.forEach(v => { rank[v] = par[v].length ? Math.max(...par[v].map(u => rank[u])) + 1 : 0; });
    const R = Math.max(...Object.values(rank));
    const pos = {};
    for (let r = 0; r <= R; r++) { const row = order.filter(v => rank[v] === r); row.forEach((v, k) => { pos[v] = [(k + 0.5) / row.length, R ? 0.12 + 0.76 * r / R : 0.5]; }); }
    return { order, par, pos };
  }
  trace('dsep', {
    title: 'd-separation: are X and Y independent given the evidence?',
    sub: 'X and Y are d-separated by Z when every path between them is blocked. A chain or fork is blocked when its middle node is in Z. A collider (both arrows point in) is blocked unless the middle node or one of its descendants is in Z.',
    W: 660, H: 420, speed: 1400,
    params: [
      { k: 'net', label: 'Network', type: 'select', v: 'alarm', opts: [['alarm', 'Burglary alarm (AIMA)'], ['sprinkler', 'Sprinkler and rain'], ['chain', 'Five nodes A to E'], ['custom', 'My own edges']] },
      { k: 'edges', label: 'My own edges, one per line ("A -> B")', type: 'area', v: 'A -> C\nB -> C\nC -> D', show: p => p.net === 'custom' },
      { k: 'x', label: 'X', type: 'text', v: 'Burglary' },
      { k: 'y', label: 'Y', type: 'text', v: 'Earthquake' },
      { k: 'zs', label: 'Evidence Z (names separated by commas, or empty)', type: 'text', v: '' }
    ],
    tips: [
      { t: 'Burglary and Earthquake with no evidence. The only path meets at Alarm, a collider, which blocks it. So they are independent.', set: { net: 'alarm', x: 'Burglary', y: 'Earthquake', zs: '' }, play: true },
      { t: 'Explaining away: observe JohnCalls, a descendant of the collider Alarm. The path opens, so Burglary and Earthquake become dependent.', set: { net: 'alarm', x: 'Burglary', y: 'Earthquake', zs: 'JohnCalls' }, play: true },
      { t: 'JohnCalls and MaryCalls with no evidence: the fork at Alarm is open, so they are dependent (both depend on the alarm).', set: { net: 'alarm', x: 'JohnCalls', y: 'MaryCalls', zs: '' }, play: true },
      { t: 'Now give Alarm. The fork is blocked, so JohnCalls and MaryCalls are independent given Alarm.', set: { net: 'alarm', x: 'JohnCalls', y: 'MaryCalls', zs: 'Alarm' }, play: true },
      { t: 'Sprinkler and Rain given Cloudy: the fork at Cloudy is blocked and the collider at WetGrass is blocked, so they are d-separated.', set: { net: 'sprinkler', x: 'Sprinkler', y: 'Rain', zs: 'Cloudy' }, play: true },
      { t: 'Add WetGrass to the evidence. The collider opens and the two causes become dependent again.', set: { net: 'sprinkler', x: 'Sprinkler', y: 'Rain', zs: 'Cloudy, WetGrass' }, play: true }
    ],
    frames(p) {
      const net = p.net === 'custom' ? parseNet(p.edges) : DNETS[p.net];
      const find = s => { const t = String(s).trim(); const v = net.order.find(n => n.toLowerCase() === t.toLowerCase()); if (!v) throw new Error(`"${t}" is not a node. The nodes are ${net.order.join(', ')}.`); return v; };
      const X = find(p.x), Y = find(p.y);
      if (X === Y) throw new Error('X and Y must be two different nodes.');
      const Z = String(p.zs).split(',').map(s => s.trim()).filter(Boolean).map(find);
      if (Z.includes(X) || Z.includes(Y)) throw new Error('X and Y cannot be in the evidence Z.');
      const kids = v => net.order.filter(u => net.par[u].includes(v));
      const desc = v => { const out = [], st = [v]; while (st.length) { const x = st.pop(); kids(x).forEach(k => { if (!out.includes(k)) { out.push(k); st.push(k); } }); } return out; };
      const nb = v => [...net.par[v], ...kids(v)];
      const paths = [];
      (function walk(path) { const last = path[path.length - 1]; if (last === Y) { paths.push(path.slice()); return; } nb(last).forEach(n => { if (!path.includes(n)) { path.push(n); walk(path); path.pop(); } }); })([X]);
      const fr = [];
      const base = { net, X, Y, Z };
      const zs = Z.length ? Z.join(', ') : 'no evidence', gz = Z.length ? `given ${zs}` : 'with no evidence', bar = Z.length ? ` | ${zs}` : '';
      fr.push({ ...base, say: `The network has ${net.order.length} nodes. We ask whether ${X} and ${Y} are independent ${gz}. Shaded nodes are the evidence. d-separation answers this from the graph alone, before we look at any numbers.` });
      if (!paths.length) { fr.push({ ...base, say: `There is no path at all between ${X} and ${Y}, so they are d-separated and independent.`, done: true, sep: true }); return fr; }
      fr.push({ ...base, say: `There ${paths.length === 1 ? 'is 1 path' : `are ${paths.length} paths`} between ${X} and ${Y}, ignoring the arrow directions. Each one is checked, three nodes at a time.` });
      let open = null;
      const res = [];
      for (let k = 0; k < paths.length && fr.length < 200; k++) {
        const P = paths[k];
        fr.push({ ...base, path: P, res: res.slice(), say: `Path ${k + 1}: ${P.join(' - ')}.` });
        let blocked = false;
        for (let i = 1; i < P.length - 1; i++) {
          const a = P[i - 1], m = P[i], b = P[i + 1];
          const inA = net.par[m].includes(a), inB = net.par[m].includes(b);
          let kind, isBlock, why;
          if (inA && inB) {
            kind = 'collider';
            const d = desc(m).filter(v => Z.includes(v));
            isBlock = !Z.includes(m) && !d.length;
            why = Z.includes(m) ? `${m} is in the evidence, so the collider is open` : d.length ? `${m} is not observed, but its descendant ${d[0]} is, so the collider is open` : `neither ${m} nor any of its descendants is in the evidence, so the collider blocks the path`;
          } else if (!inA && !inB) {
            kind = 'fork (common cause)'; isBlock = Z.includes(m);
            why = isBlock ? `${m} is in the evidence, so the fork is blocked` : `${m} is not in the evidence, so the fork lets dependence pass`;
          } else {
            kind = 'chain'; isBlock = Z.includes(m);
            why = isBlock ? `${m} is in the evidence, so the chain is blocked` : `${m} is not in the evidence, so the chain lets dependence pass`;
          }
          const arrow = (u, v) => net.par[v].includes(u) ? `${u} → ${v}` : `${u} ← ${v}`;
          fr.push({ ...base, path: P, tri: [a, m, b], triBlock: isBlock, res: res.slice(), say: `Triple ${arrow(a, m)}, ${arrow(m, b)} is a ${kind} at ${m}: ${why}.` });
          if (isBlock) { blocked = true; break; }
        }
        res.push({ P, blocked });
        fr.push({ ...base, path: P, pathBlock: blocked, res: res.slice(), say: blocked ? `So path ${k + 1} is blocked.` : `Every triple on path ${k + 1} lets dependence pass, so this path is active. One active path is enough: ${X} and ${Y} are not d-separated.` });
        if (!blocked) { open = P; break; }
      }
      if (open) fr.push({ ...base, path: open, pathBlock: false, res, done: true, sep: false, say: `${X} and ${Y} are not d-separated ${gz}. The graph does not promise independence, so in most distributions that fit this graph they are dependent.` });
      else fr.push({ ...base, res, done: true, sep: true, say: `${paths.length > 1 ? `All ${paths.length} paths are` : 'The only path is'} blocked. ${X} and ${Y} are d-separated ${gz}, so ${X} ⫫ ${Y}${bar} holds in every distribution that fits this graph.` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const onPath = (u, v) => f.path && f.path.some((x, i) => i && ((f.path[i - 1] === u && x === v) || (f.path[i - 1] === v && x === u)));
      const pc = f.pathBlock === true ? c.red : f.pathBlock === false ? c.green : c.cv;
      drawNet(z, f.net, [20, 20, z.W - 40, 270], {
        fill: v => f.Z.includes(v) ? c.ink2 : (v === f.X || v === f.Y) ? c.cv : c.surf,
        ink: v => (f.Z.includes(v) || v === f.X || v === f.Y) ? '#fff' : c.ink,
        stroke: v => f.tri && f.tri[1] === v ? (f.triBlock ? c.red : c.green) : c.ink2,
        edge: (u, v) => onPath(u, v) ? pc : c.line,
        edgeW: (u, v) => onPath(u, v) ? 3 : 1.4,
        sub: v => f.tri && f.tri[1] === v ? (f.triBlock ? 'blocks' : 'passes') : v === f.X ? 'X' : v === f.Y ? 'Y' : f.Z.includes(v) ? 'evidence' : '',
        subc: v => f.tri && f.tri[1] === v ? (f.triBlock ? c.red : c.green) : c.ink2
      });
      let y = 318;
      (f.res || []).slice(-3).forEach(r => { const s = `${r.blocked ? 'blocked' : 'active'}: ${r.P.join(' - ')}`; D.text(g, s, 20, y, { s: fit(g, s, z.W - 40, 12, { b: true }), b: true, c: r.blocked ? c.red : c.green }); y += 20; });
      D.text(g, 'Blue: X and Y. Grey: evidence. Thick line: the path being checked.', 20, z.H - 12, { s: 11, c: c.ink2 });
      if (f.done) tag(g, f.sep ? 'd-separated' : 'not d-separated', z.W - 80, 20, { s: 12.5, fill: f.sep ? c.green : c.red, stroke: f.sep ? c.green : c.red, c: '#fff' });
    }
  });

  /* =====================================================================================================
     9.2  An undirected model (Markov network): factor products and the partition function Z
     ===================================================================================================== */
  trace('markovnet', {
    title: 'A Markov network: multiply the factors, then divide by Z',
    sub: 'An undirected model gives each edge a factor (a table of positive numbers, not probabilities). The score of a world is the product of its factors. Dividing by Z, the sum of all scores, turns scores into probabilities.',
    W: 660, H: 440, speed: 700,
    params: [
      { k: 'f', label: 'Factors, one per edge: "X Y: value for 00 01 10 11" (0 is false, 1 is true)', type: 'area', v: 'A B: 30 5 1 10\nB C: 100 1 1 100\nC D: 1 100 100 1\nD A: 100 1 1 100' },
      { k: 'q', label: 'Show the marginal of', type: 'text', v: 'B' }
    ],
    tips: [
      { t: 'The misconception example of Koller and Friedman (2009): four students in a study loop. Z = 7,201,840, and the most likely world (A = 0, B = 1, C = 1, D = 0) has probability about 0.69.', set: { f: 'A B: 30 5 1 10\nB C: 100 1 1 100\nC D: 1 100 100 1\nD A: 100 1 1 100', q: 'B' }, play: true },
      { t: 'A three node chain where neighbours like to agree. Each factor gives 4 to equal values and 1 to different ones.', set: { f: 'A B: 4 1 1 4\nB C: 4 1 1 4', q: 'A' }, play: true }
    ],
    frames(p) {
      const facs = String(p.f).split('\n').map(s => s.trim()).filter(Boolean).map(l => {
        const m = l.match(/^([A-Za-z]\w*)\s+([A-Za-z]\w*)\s*:\s*(.+)$/);
        if (!m) throw new Error(`"${l}" should look like "A B: 30 5 1 10".`);
        const v = m[3].split(/[\s,]+/).filter(Boolean).map(Number);
        if (v.length !== 4 || v.some(x => isNaN(x) || x < 0)) throw new Error(`The factor "${l}" needs 4 numbers, each 0 or more.`);
        if (m[1] === m[2]) throw new Error(`The factor "${l}" must join two different variables.`);
        return { a: m[1], b: m[2], v };
      });
      if (!facs.length) throw new Error('Please give at least one factor.');
      const vars = [];
      facs.forEach(F => [F.a, F.b].forEach(x => { if (!vars.includes(x)) vars.push(x); }));
      if (vars.length > 4) throw new Error('Please use at most 4 variables (16 worlds), so every world fits on the screen.');
      const Q = vars.find(v => v.toLowerCase() === String(p.q).trim().toLowerCase());
      if (!Q) throw new Error(`"${p.q}" is not one of the variables ${vars.join(', ')}.`);
      const worlds = [];
      for (let m = 0; m < (1 << vars.length); m++) {
        const a = {}; vars.forEach((v, i) => { a[v] = (m >> (vars.length - 1 - i)) & 1; });
        const parts = facs.map(F => F.v[a[F.a] * 2 + a[F.b]]);
        worlds.push({ a, parts, s: parts.reduce((x, y) => x * y, 1) });
      }
      const fr = [];
      const base = { vars, facs, worlds, Q };
      fr.push({ ...base, n: 0, say: `The graph has ${vars.length} variables and ${facs.length} factors, one per edge. A factor φ(X, Y) scores how well the values of X and Y fit together. Higher means more likely. The numbers are not probabilities and need not add up to 1.` });
      let Z = 0;
      worlds.forEach((w, i) => {
        Z += w.s;
        const ws = vars.map(v => `${v} = ${w.a[v]}`).join(', ');
        if (i < 3 || i === worlds.length - 1 || worlds.length <= 8) fr.push({ ...base, n: i + 1, Z, say: `World ${i + 1}: ${ws}. Its score is the product of its factor values: ${w.parts.join(' × ')} = ${w.s.toLocaleString('en')}.` });
        else fr.push({ ...base, n: i + 1, Z, say: `World ${i + 1}: ${ws}. Score ${w.parts.join(' × ')} = ${w.s.toLocaleString('en')}.` });
      });
      if (Z <= 0) { fr.push({ ...base, n: worlds.length, Z, say: 'Every world has score 0, so no distribution can be made. Use some positive values.' }); return fr; }
      fr.push({ ...base, n: worlds.length, Z, showZ: true, say: `Add up all ${worlds.length} scores. This is the partition function Z = ${Z.toLocaleString('en')}. Computing Z needs a sum over every world, which grows as 2 to the power of the number of variables. This is the hard part of undirected models.` });
      const best = worlds.reduce((b, w) => w.s > b.s ? w : b, worlds[0]);
      fr.push({ ...base, n: worlds.length, Z, showZ: true, norm: true, best, say: `Divide each score by Z to get P(world) = score ÷ Z. The most likely world is ${vars.map(v => `${v} = ${best.a[v]}`).join(', ')} with ${best.s.toLocaleString('en')} ÷ ${Z.toLocaleString('en')} = ${f3(best.s / Z)}.` });
      const m1 = worlds.filter(w => w.a[Q] === 1).reduce((x, w) => x + w.s, 0) / Z;
      fr.push({ ...base, n: worlds.length, Z, showZ: true, norm: true, best, q1: m1, done: true, say: `The marginal P(${Q} = 1) adds the probabilities of the worlds with ${Q} = 1: ${f3(m1)}. Note that it is not the normalised value of any single factor. In an undirected model, a factor is not a conditional probability table.` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const R = 70, cx = 110, cy = 110;
      const P = {};
      f.vars.forEach((v, i) => { const t = -Math.PI / 2 + i * 2 * Math.PI / f.vars.length; P[v] = [cx + R * Math.cos(t) * (f.vars.length > 2 ? 1 : 1.2), cy + R * Math.sin(t)]; });
      if (f.vars.length === 3) { P[f.vars[0]] = [cx - 80, cy]; P[f.vars[1]] = [cx, cy]; P[f.vars[2]] = [cx + 80, cy]; }
      const cur = f.best || (f.n ? f.worlds[f.n - 1] : null);
      f.facs.forEach(F => D.line(g, P[F.a][0], P[F.a][1], P[F.b][0], P[F.b][1], c.ink2, 1.8));
      f.vars.forEach(v => {
        const on = cur && cur.a[v] === 1;
        D.circle(g, P[v][0], P[v][1], 18, { fill: cur ? (on ? c.cv : c.surf) : c.surf, stroke: c.ink2, w: 1.6 });
        D.text(g, cur ? `${v}=${cur.a[v]}` : v, P[v][0], P[v][1] + 1, { a: 'center', bl: 'middle', s: cur ? 10.5 : 13, b: true, c: on ? '#fff' : c.ink });
      });
      let fy = 225;
      f.facs.forEach(F => { const s = `φ(${F.a}, ${F.b}): 00 → ${F.v[0]}, 01 → ${F.v[1]}, 10 → ${F.v[2]}, 11 → ${F.v[3]}`; D.text(g, s, 16, fy, { s: fit(g, s, 250, 11.5, { mono: true }), mono: true, c: c.ink }); fy += 20; });
      if (f.showZ) { D.text(g, `Z = ${f.Z.toLocaleString('en')}`, 16, fy + 16, { s: 15, b: true, c: c.cv }); }
      if (f.q1 !== undefined) D.text(g, `P(${f.Q} = 1) = ${f3(f.q1)}`, 16, fy + 42, { s: 14, b: true, c: c.green });
      const x0 = 285, y0 = 24, rh = Math.min(24, (z.H - 50) / f.worlds.length);
      D.text(g, f.vars.join(' ') + '   score' + (f.norm ? '   P' : ''), x0, y0, { s: 11.5, b: true, mono: true, c: c.ink2 });
      f.worlds.slice(0, f.n).forEach((w, i) => {
        const y = y0 + 6 + i * rh, hot = i === f.n - 1 && !f.showZ, best = f.best === w;
        rr(g, x0 - 4, y, z.W - x0 - 10, rh - 3, 4, { fill: best ? c.green + '33' : hot ? c.cv + '22' : c.surf, stroke: best ? c.green : hot ? c.cv : c.line, w: 1 });
        const s = f.vars.map(v => w.a[v]).join(' ') + '   ' + w.s.toLocaleString('en').padStart(9) + (f.norm ? '   ' + (w.s && w.s / f.Z < 0.001 ? '<0.001' : f3(w.s / f.Z)) : '');
        D.text(g, s, x0, y + rh / 2 + 2.5, { s: Math.min(12, rh * 0.55), mono: true, b: best, c: c.ink });
      });
      if (f.done) tag(g, 'done', z.W - 40, z.H - 16, { s: 12, fill: c.green, stroke: c.green, c: '#fff' });
    }
  });

  /* =====================================================================================================
     9.3  Variable elimination on the burglary network (AIMA 14.4.2)
     ===================================================================================================== */
  trace('varelim', {
    title: 'Variable elimination: multiply factors, sum out one variable at a time',
    sub: 'Every table of the network becomes a factor, with the evidence plugged in. To remove a hidden variable, multiply all factors that mention it and sum it out. At the end, multiply what is left and normalise.',
    W: 680, H: 440, speed: 1500,
    params: [
      { k: 'q', label: 'Query', type: 'select', v: 'Burglary', opts: [['Burglary', 'Burglary'], ['Earthquake', 'Earthquake'], ['Alarm', 'Alarm']] },
      { k: 'j', label: 'JohnCalls', type: 'select', v: 'T', opts: [['T', 'true (evidence)'], ['F', 'false (evidence)'], ['-', 'not known (hidden)']] },
      { k: 'm', label: 'MaryCalls', type: 'select', v: 'T', opts: [['T', 'true (evidence)'], ['F', 'false (evidence)'], ['-', 'not known (hidden)']] },
      { k: 'ord', label: 'Elimination order', type: 'select', v: 'leaf', opts: [['leaf', 'Leaves first, Alarm last (small factors)'], ['alarm', 'Alarm first (a bigger factor)']] }
    ],
    tips: [
      { t: 'The textbook query P(Burglary | john calls, mary calls) = ⟨0.284, 0.716⟩. Earthquake is summed out first, then Alarm.', set: { q: 'Burglary', j: 'T', m: 'T', ord: 'leaf' }, play: true },
      { t: 'Only John calls. MaryCalls is hidden but has no evidence below it: summing it out gives a factor of all 1s, so it could be dropped from the start (it is irrelevant).', set: { q: 'Burglary', j: 'T', m: '-', ord: 'leaf' }, play: true },
      { t: 'No evidence and Alarm first: the product of all factors that mention Alarm has 5 variables and 32 entries. A bad order makes big factors. Leaves first keeps every factor at 3 variables or fewer.', set: { q: 'Burglary', j: '-', m: '-', ord: 'alarm' }, play: true },
      { t: 'Explaining away with numbers: P(Earthquake | john calls, mary calls) is about 0.176.', set: { q: 'Earthquake', j: 'T', m: 'T', ord: 'leaf' }, play: true }
    ],
    frames(p) {
      const net = ALARM, Q = p.q;
      const ev = {};
      if (p.j !== '-') ev.JohnCalls = p.j === 'T';
      if (p.m !== '-') ev.MaryCalls = p.m === 'T';
      const es = Object.keys(ev).map(k => `${k} = ${TF(ev[k])}`).join(', ');
      const hidden = net.order.filter(v => v !== Q && !(v in ev));
      const order = p.ord === 'alarm' && hidden.includes('Alarm') ? ['Alarm', ...hidden.filter(v => v !== 'Alarm')] : [...hidden.filter(v => v !== 'Alarm').reverse(), ...(hidden.includes('Alarm') ? ['Alarm'] : [])];
      let F = net.order.map(X => { const f = BN.fromCpt(net, X, ev); return { ...f, name: `f${X[0]}(${f.vars.map(v => v[0]).join(', ')})`, src: X }; });
      const fr = [];
      const tbl = f => f.vars.length ? BN.all(f.vars).map((a, i) => `${f.vars.map(v => (a[v] ? '' : '¬') + v[0].toLowerCase()).join(' ')}: ${f4(f.t[i])}`).join(', ') : f4(f.t[0]);
      const snap = (say, ex = {}) => fr.push({ F: F.map(f => ({ name: f.name, vars: f.vars, n: f.t.length, txt: tbl(f), hot: ex.hot && ex.hot.includes(f.name), neu: ex.neu === f.name })), ev, Q, gone: ex.gone || [], say, ...ex });
      snap(`We want P(${Q}${es ? ' | ' + es : ''}). The evidence is ${es || 'empty'}. The hidden variables, which must be summed out, are ${hidden.join(', ')}. They will be removed in the order ${order.join(', ')}.`, { stage: 'start' });
      snap(`Turn each table into a factor. The evidence is plugged in, so it drops out of the factor's variables. For example ${F.find(f => f.src === 'Alarm').name} has ${F.find(f => f.src === 'Alarm').t.length} entries.${'JohnCalls' in ev ? ` ${F.find(f => f.src === 'JohnCalls').name} is P(JohnCalls = ${TF(ev.JohnCalls)} | Alarm), a factor over Alarm only.` : ''}`, { stage: 'facs' });
      let biggest = Math.max(...F.map(f => f.vars.length)), gone = [];
      let k = 0;
      for (const X of order) {
        const use = F.filter(f => f.vars.includes(X)), rest = F.filter(f => !f.vars.includes(X));
        let prod = use[0]; for (let i = 1; i < use.length; i++) prod = BN.mul(prod, use[i]);
        biggest = Math.max(biggest, prod.vars.length);
        snap(`Eliminate ${X}. The factors that mention ${X} are ${use.map(f => f.name).join(', ')}. Their product is a factor over ${prod.vars.join(', ')}, with ${prod.t.length} entries.`, { hot: use.map(f => f.name), gone: gone.slice(), stage: 'mul', X, prodN: prod.t.length });
        const s = BN.sumOut(prod, X);
        k++;
        const nm = `g${k}(${s.vars.map(v => v[0]).join(', ')})`;
        F = [...rest, { ...s, name: nm }];
        gone.push(X);
        const ones = s.t.every(v => Math.abs(v - 1) < 1e-9);
        snap(`Sum out ${X}: add the entries for ${X} = true and ${X} = false. The new factor ${nm} has ${s.t.length} entr${s.t.length === 1 ? 'y' : 'ies'}.${ones ? ` Every entry is 1, so ${X} had no effect: a hidden variable with no evidence below it is irrelevant and can be dropped before starting.` : ''}`, { neu: nm, gone: gone.slice(), stage: 'sum', X });
      }
      let fin = F[0]; for (let i = 1; i < F.length; i++) fin = BN.mul(fin, F[i]);
      const t = fin.t[BN.idx(fin.vars, { [Q]: true })], f = fin.t[BN.idx(fin.vars, { [Q]: false })];
      F = [{ ...fin, name: `product(${Q[0]})` }];
      snap(`Multiply the factors that are left. They all mention only ${Q}: ⟨${f4(t) === '0' ? t.toExponential(3) : t.toPrecision(4)}, ${f.toPrecision(4)}⟩ for ${Q} = true and false.`, { gone: gone.slice(), neu: `product(${Q[0]})`, stage: 'fin' });
      const ans = t / (t + f), exact = BN.exact(net, Q, ev);
      snap(`Normalise: divide by their sum. P(${Q}${es ? ' | ' + es : ''}) = ⟨${f3(ans)}, ${f3(1 - ans)}⟩. Enumeration of the full joint gives ${f3(exact)}, the same. The largest factor used had ${biggest} variable${biggest > 1 ? 's' : ''}, so ${2 ** biggest} entries.`, { gone: gone.slice(), ans, done: true, stage: 'done' });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      drawNet(z, ALARM, [10, 14, 250, 230], {
        fill: v => v in f.ev ? c.ink2 : v === f.Q ? c.cv : f.gone.includes(v) ? c.bg : c.surf,
        ink: v => (v in f.ev || v === f.Q) ? '#fff' : f.gone.includes(v) ? c.ink2 : c.ink,
        sub: v => v in f.ev ? `= ${TF(f.ev[v])}` : f.gone.includes(v) ? 'summed out' : v === f.Q ? 'query' : '',
        subc: v => v in f.ev ? c.ink2 : f.gone.includes(v) ? c.ink2 : c.cv
      });
      const x0 = 290, w = z.W - x0 - 12;
      let y = 24;
      D.text(g, 'Factors now', x0, y, { s: 12.5, b: true, c: c.ink2 }); y += 10;
      f.F.forEach(F => {
        const parts = F.txt.split(', '), nl = Math.ceil(parts.length / 4), h = 26 + 12 * nl;
        rr(g, x0 - 4, y, w, h - 4, 5, { fill: F.neu ? c.green + '2a' : F.hot ? c.cv + '22' : c.surf, stroke: F.neu ? c.green : F.hot ? c.cv : c.line, w: F.neu || F.hot ? 2 : 1 });
        D.text(g, `${F.name}  (${F.n} entr${F.n === 1 ? 'y' : 'ies'})`, x0 + 4, y + 14, { s: 11.5, b: true, c: c.ink });
        for (let i = 0; i < nl; i++) { const s = parts.slice(4 * i, 4 * i + 4).join(', '); D.text(g, s, x0 + 4, y + 28 + i * 12, { s: fit(g, s, w - 10, 10.5, { mono: true }), mono: true, c: c.ink2 }); }
        y += h;
      });
      if (f.ans !== undefined) {
        const bx = 20, by = 290, bw = 240;
        D.text(g, `P(${f.Q} | evidence)`, bx, by, { s: 12.5, b: true, c: c.ink });
        [[f.ans, 'true', c.green], [1 - f.ans, 'false', c.orange]].forEach(([v, lab, col], k) => {
          const yy = by + 12 + k * 34;
          rr(g, bx, yy, bw, 24, 5, { fill: c.bg, stroke: c.line, w: 1 });
          rr(g, bx, yy, Math.max(2, bw * v), 24, 5, { fill: col });
          D.text(g, `${lab}: ${f3(v)}`, bx + 8, yy + 17, { s: 12.5, b: true, c: v > 0.3 ? '#fff' : c.ink });
        });
      }
      if (f.prodN) D.text(g, `product size: ${f.prodN} entries`, 20, 300, { s: 13, b: true, c: c.cv });
      if (f.done) tag(g, 'done', z.W - 40, z.H - 16, { s: 12, fill: c.green, stroke: c.green, c: '#fff' });
    }
  });

  /* =====================================================================================================
     9.3  Approximate inference by sampling: rejection sampling, likelihood weighting, Gibbs sampling (AIMA 14.5)
     ===================================================================================================== */
  trace('sampling', {
    title: 'Estimate a probability by drawing random samples',
    sub: 'Each sample sets every variable in turn, using the network tables and random numbers. Counting samples gives an estimate that gets closer to the exact answer (dashed line) as the number of samples grows.',
    W: 680, H: 440, speed: 900,
    params: [
      { k: 'alg', label: 'Method', type: 'select', v: 'rej', opts: [['rej', 'Rejection sampling'], ['lw', 'Likelihood weighting'], ['gibbs', 'Gibbs sampling (MCMC)']] },
      { k: 'ev', label: 'Evidence', type: 'select', v: 'S', opts: [['S', 'Sprinkler = true'], ['SW', 'Sprinkler = true, WetGrass = true'], ['W', 'WetGrass = true'], ['C', 'Cloudy = false']] },
      { k: 'N', label: 'Number of samples', type: 'range', v: 200, min: 20, max: 2000, step: 20 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 1, min: 1, max: 30 }
    ],
    tips: [
      { t: 'Rejection sampling for P(Rain | Sprinkler = true), exact 0.3. About 70 percent of the samples have the sprinkler off and are thrown away.', set: { alg: 'rej', ev: 'S', N: 200 }, play: true },
      { t: 'Likelihood weighting for P(Rain | Sprinkler = true, WetGrass = true), exact 0.3204. No sample is thrown away: each one is weighted by how well it explains the evidence.', set: { alg: 'lw', ev: 'SW', N: 200 }, play: true },
      { t: 'Gibbs sampling for the same question. It changes one hidden variable at a time, sampling it from its Markov blanket.', set: { alg: 'gibbs', ev: 'SW', N: 400 }, play: true },
      { t: 'More samples, a closer estimate. The error shrinks roughly as 1 ÷ √N.', set: { alg: 'lw', ev: 'W', N: 2000 }, play: true }
    ],
    frames(p) {
      const net = SPRINK;
      const ev = { S: { Sprinkler: true }, SW: { Sprinkler: true, WetGrass: true }, W: { WetGrass: true }, C: { Cloudy: false } }[p.ev];
      const es = Object.keys(ev).map(k => `${k} = ${TF(ev[k])}`).join(', ');
      const exact = BN.exact(net, 'Rain', ev);
      const r = CVZ.rng(p.seed * 7919 + 31);
      const N = Math.max(1, Math.round(p.N));
      const fr = [];
      const hist = [];
      let num = 0, den = 0, kept = 0;
      const base = () => ({ exact, hist: hist.slice(), alg: p.alg, ev, es });
      const name = { rej: 'Rejection sampling', lw: 'Likelihood weighting', gibbs: 'Gibbs sampling' }[p.alg];
      fr.push({ ...base(), say: `${name} estimates P(Rain | ${es}). The exact answer, found by enumeration, is ${f4(exact)}, drawn as the dashed line. Each of the first samples is shown in full, then the samples come in batches.` });
      const show = i => i < 5;   /* the first 5 samples in full, plus the first kept one in rejection sampling */
      const marks = new Set([10, 20, 50, 100, 200, 500, 1000, 1500, 2000, N]);
      let state = null;
      if (p.alg === 'gibbs') {
        state = Object.assign({}, ev);
        net.order.forEach(v => { if (!(v in ev)) state[v] = r() < 0.5; });
        fr.push({ ...base(), cur: Object.assign({}, state), say: `Gibbs sampling starts from the evidence plus random values for the hidden variables: ${net.order.map(v => `${v} = ${TF(state[v])}`).join(', ')}.` });
      }
      const hiddenV = net.order.filter(v => !(v in ev));
      for (let i = 0; i < N; i++) {
        let s = {}, w = 1, parts = [], ok = true;
        if (p.alg === 'rej') {
          net.order.forEach(v => { const pv = BN.pr(net, v, true, s), u = r(); s[v] = u < pv; parts.push(`${v}: P(true) = ${pv}, random ${f3(u)}, so ${TF(s[v])}`); });
          ok = Object.keys(ev).every(k => s[k] === ev[k]);
          if (ok) { kept++; den++; if (s.Rain) num++; }
        } else if (p.alg === 'lw') {
          net.order.forEach(v => {
            const pv = BN.pr(net, v, true, s);
            if (v in ev) { s[v] = ev[v]; const l = ev[v] ? pv : 1 - pv; w *= l; parts.push(`${v} is evidence (${TF(ev[v])}): weight × ${f3(l)}`); }
            else { const u = r(); s[v] = u < pv; parts.push(`${v}: P(true) = ${pv}, random ${f3(u)}, so ${TF(s[v])}`); }
          });
          den += w; if (s.Rain) num += w;
        } else {
          const v = hiddenV[i % hiddenV.length];
          const score = val => { const a = Object.assign({}, state, { [v]: val }); let q = BN.pr(net, v, val, a); net.order.filter(k => net.par[k].includes(v)).forEach(k => { q *= BN.pr(net, k, a[k], a); }); return q; };
          const pt = score(true), pf = score(false), pv = pt / (pt + pf), u = r();
          state[v] = u < pv;
          parts.push(`resample ${v} from its Markov blanket: P(${v} = true | blanket) = ${f3(pt)} ÷ (${f3(pt)} + ${f3(pf)}) = ${f3(pv)}, random ${f3(u)}, so ${TF(state[v])}`);
          s = Object.assign({}, state);
          den++; if (s.Rain) num++;
        }
        const est = den > 0 ? num / den : NaN;
        if ((i + 1) % Math.max(1, Math.floor(N / 120)) === 0 || i < 20) hist.push([i + 1, est]);
        const firstKeep = p.alg === 'rej' && ok && kept === 1 && i >= 5;
        if (show(i) || firstKeep) {
          const verdict = p.alg === 'rej' ? (ok ? `It agrees with the evidence, so it is kept. Rain = ${TF(s.Rain)}.` : 'It disagrees with the evidence, so it is thrown away.') : p.alg === 'lw' ? `Its weight is ${f4(w)}. Rain = ${TF(s.Rain)}.` : `The new state has Rain = ${TF(s.Rain)}.`;
          fr.push({ ...base(), cur: s, ok, w: p.alg === 'lw' ? w : null, n: i + 1, num, den, est, say: `Sample ${i + 1}: ${parts.join('. ')}. ${verdict} Estimate so far: ${isNaN(est) ? 'none yet' : f3(est)}.` });
        } else if (marks.has(i + 1)) {
          const txt = p.alg === 'rej' ? `${kept} of ${i + 1} samples were kept (${Math.round(100 * kept / (i + 1))} percent), and ${num} of them have Rain = true` : p.alg === 'lw' ? `the total weight is ${f3(den)}, and the samples with Rain = true carry ${f3(num)} of it` : `${num} of ${i + 1} states have Rain = true`;
          fr.push({ ...base(), cur: s, n: i + 1, num, den, est, say: `After ${i + 1} samples: ${txt}. Estimate ${isNaN(est) ? 'none yet' : f3(est)}, exact ${f4(exact)}, error ${isNaN(est) ? '?' : f3(Math.abs(est - exact))}.` });
        }
      }
      const last = fr[fr.length - 1];
      const est = den > 0 ? num / den : NaN;
      fr.push({ ...base(), cur: last.cur, n: N, num, den, est, done: true, say: `Final estimate after ${N} samples: ${isNaN(est) ? 'none, every sample was rejected' : f3(est)}. Exact: ${f4(exact)}. ${p.alg === 'rej' ? `Rejection sampling wasted ${N - kept} samples, which gets worse when the evidence is unlikely.` : p.alg === 'lw' ? 'Likelihood weighting used every sample, but samples with tiny weights add little.' : 'Gibbs samples are not independent, since each state is a small change of the last, so more samples are needed for the same accuracy.'}` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const s = f.cur;
      drawNet(z, SPRINK, [10, 10, 250, 200], {
        fill: v => v in f.ev ? c.ink2 : s ? (s[v] ? c.cv : c.surf) : c.surf,
        ink: v => (v in f.ev || (s && s[v])) ? '#fff' : c.ink,
        sub: v => s ? TF(s[v]) + (v in f.ev ? ' (evidence)' : '') : v in f.ev ? `= ${TF(f.ev[v])}` : '',
        subc: v => v in f.ev ? c.ink2 : c.cv
      });
      if (f.n) {
        const lines = [`samples: ${f.n}`, f.alg === 'lw' ? `total weight: ${f3(f.den)}` : f.alg === 'rej' ? `kept: ${f.den}` : '', `estimate: ${isNaN(f.est) ? 'none yet' : f3(f.est)}`, `exact: ${f4(f.exact)}`];
        let y = 248;
        lines.filter(Boolean).forEach(t => { D.text(g, t, 20, y, { s: 13, b: true, c: t.startsWith('estimate') ? c.cv : c.ink }); y += 22; });
        if (f.ok === false) tag(g, 'rejected', 210, 252, { s: 12, fill: c.red, stroke: c.red, c: '#fff' });
        if (f.w !== null && f.w !== undefined) tag(g, `weight ${f4(f.w)}`, 210, 252, { s: 12, fill: c.cv, stroke: c.cv, c: '#fff' });
      }
      const box = [330, 30, z.W - 350, z.H - 90];
      const xmax = Math.max(20, ...f.hist.map(h => h[0]), f.n || 0);
      const m = D.axes(g, z, box, [0, xmax], [0, 1], { nx: 4, ny: 4, xl: 'number of samples', yl: 'estimate of P(Rain)', fx: v => String(Math.round(v)) });
      D.line(g, m.sx(0), m.sy(f.exact), m.sx(xmax), m.sy(f.exact), c.ink2, 1.6, [6, 5]);
      const pts = f.hist.filter(h => !isNaN(h[1]));
      if (pts.length) { g.save(); g.strokeStyle = c.cv; g.lineWidth = 2.2; g.beginPath(); pts.forEach(([x, y], i) => { if (i) g.lineTo(m.sx(x), m.sy(y)); else g.moveTo(m.sx(x), m.sy(y)); }); g.stroke(); g.restore(); }
      if (f.done) tag(g, 'done', z.W - 40, 16, { s: 12, fill: c.green, stroke: c.green, c: '#fff' });
    }
  });

  /* =====================================================================================================
     9.4  Seeing versus doing: Simpson's paradox and the back door adjustment (Pearl, 2009)
     ===================================================================================================== */
  trace('causal', {
    title: 'Seeing versus doing: the back door adjustment',
    sub: 'Observed rates P(R | T) mix the effect of the treatment with the effect of a common cause Z. The intervention do(T) cuts the arrow Z → T. The adjustment formula P(R | do(t)) = Σ P(R | t, z) P(z) computes it from the same data.',
    W: 680, H: 420, speed: 1700,
    params: [
      { k: 'd', label: 'Counts: "group treatment recovered total", one line each', type: 'area', v: 'small A 81 87\nsmall B 234 270\nlarge A 192 263\nlarge B 55 80' }
    ],
    tips: [
      { t: 'Kidney stones (Charig and others, 1986, as used by Pearl). B looks better overall (83 versus 78 percent), yet A is better for small stones and for large stones. Adjusting for stone size shows that A is the better treatment.', set: { d: 'small A 81 87\nsmall B 234 270\nlarge A 192 263\nlarge B 55 80' }, play: true },
      { t: 'Balanced groups: when both treatments are given equally often in each group, seeing and doing give the same answer, because Z no longer affects T.', set: { d: 'small A 90 100\nsmall B 80 100\nlarge A 60 100\nlarge B 50 100' }, play: true }
    ],
    frames(p) {
      const rows = String(p.d).split('\n').map(s => s.trim()).filter(Boolean).map(l => {
        const m = l.split(/\s+/);
        if (m.length !== 4 || isNaN(+m[2]) || isNaN(+m[3])) throw new Error(`"${l}" should look like "small A 81 87".`);
        const r = { z: m[0], t: m[1], k: +m[2], n: +m[3] };
        if (r.n <= 0 || r.k < 0 || r.k > r.n) throw new Error(`In "${l}" the recovered count must be between 0 and the total, and the total above 0.`);
        return r;
      });
      const Zs = [...new Set(rows.map(r => r.z))], Ts = [...new Set(rows.map(r => r.t))];
      if (Ts.length !== 2 || Zs.length < 2) throw new Error('Please give exactly 2 treatments and at least 2 groups, with one line for every group and treatment.');
      Zs.forEach(zz => Ts.forEach(tt => { if (!rows.find(r => r.z === zz && r.t === tt)) throw new Error(`The line for group ${zz} and treatment ${tt} is missing.`); }));
      const get = (zz, tt) => rows.find(r => r.z === zz && r.t === tt);
      const all = rows.reduce((a, r) => a + r.n, 0);
      const obs = tt => { const rs = rows.filter(r => r.t === tt); return rs.reduce((a, r) => a + r.k, 0) / rs.reduce((a, r) => a + r.n, 0); };
      const pz = zz => rows.filter(r => r.z === zz).reduce((a, r) => a + r.n, 0) / all;
      const doT = tt => Zs.reduce((a, zz) => a + get(zz, tt).k / get(zz, tt).n * pz(zz), 0);
      const pc = v => `${(100 * v).toFixed(1)}%`;
      const [A, B] = Ts;
      const fr = [];
      const base = { rows, Zs, Ts };
      fr.push({ ...base, stage: 1, say: `The causal graph: the group Z (here ${Zs.join(' or ')}) affects which treatment T a patient gets, and also affects recovery R. T also affects R. So there are two paths from T to R: the direct arrow T → R and the back door path T ← Z → R.` });
      fr.push({ ...base, stage: 2, say: `The data: for each group and treatment, how many patients recovered out of how many. ${all} patients in all.` });
      fr.push({ ...base, stage: 3, obs: true, say: `Seeing: compare recovery rates over everyone. P(R | T = ${A}) = ${pc(obs(A))} and P(R | T = ${B}) = ${pc(obs(B))}. On this view ${obs(A) > obs(B) ? A : B} looks better.` });
      const better = Zs.map(zz => get(zz, A).k / get(zz, A).n > get(zz, B).k / get(zz, B).n ? A : B);
      fr.push({ ...base, stage: 4, obs: true, grp: true, say: `Now compare inside each group. ${Zs.map(zz => `${zz}: ${A} ${pc(get(zz, A).k / get(zz, A).n)}, ${B} ${pc(get(zz, B).k / get(zz, B).n)}`).join('. ')}. ${better.every(b => b === better[0]) ? `${better[0]} is better in every group.` : 'The groups disagree.'}${better.every(b => b === better[0]) && better[0] !== (obs(A) > obs(B) ? A : B) ? ' The overall comparison points the other way: this reversal is Simpson\'s paradox.' : ''}` });
      const share = tt => Zs.map(zz => `${zz} ${pc(get(zz, tt).n / rows.filter(r => r.t === tt).reduce((a, r) => a + r.n, 0))}`).join(', ');
      fr.push({ ...base, stage: 5, obs: true, grp: true, say: `Why: the groups are not shared out evenly. Patients given ${A} were ${share(A)}. Patients given ${B} were ${share(B)}. The group changes both who gets which treatment and how likely recovery is, so Z is a confounder. The back door path T ← Z → R mixes its effect into the observed rates.` });
      fr.push({ ...base, stage: 6, cut: true, obs: true, grp: true, say: `Doing: imagine we set T ourselves for everyone, written do(T = t). This cuts the arrow Z → T, so the group no longer decides the treatment. The back door path is closed. Z blocks every back door path and is not caused by T, so it meets the back door criterion and adjustment is allowed.` });
      fr.push({ ...base, stage: 7, cut: true, obs: true, grp: true, pz: Zs.map(zz => [zz, pz(zz)]), say: `The adjustment formula weights each group by its share of all patients, not its share within one treatment: ${Zs.map(zz => `P(${zz}) = ${f3(pz(zz))}`).join(', ')}.` });
      fr.push({ ...base, stage: 8, cut: true, obs: true, grp: true, pz: Zs.map(zz => [zz, pz(zz)]), dA: doT(A), dB: doT(B), done: true, say: `P(R | do(${A})) = ${Zs.map(zz => `${f3(get(zz, A).k / get(zz, A).n)} × ${f3(pz(zz))}`).join(' + ')} = ${pc(doT(A))}. P(R | do(${B})) = ${Zs.map(zz => `${f3(get(zz, B).k / get(zz, B).n)} × ${f3(pz(zz))}`).join(' + ')} = ${pc(doT(B))}. The average causal effect of ${A} over ${B} is ${(100 * (doT(A) - doT(B))).toFixed(1)} percentage points${Math.abs(doT(A) - doT(B) - (obs(A) - obs(B))) > 0.001 ? ', which differs from the observed difference' : ', the same as the observed difference here'}.` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const net = { order: ['Z', 'T', 'R'], par: { Z: [], T: ['Z'], R: ['Z', 'T'] }, pos: { Z: [0.5, 0.14], T: [0.15, 0.82], R: [0.85, 0.82] } };
      const lab = { Z: 'Z group', T: 'T treatment', R: 'R recovery' };
      const net2 = { order: ['Z group', 'T treatment', 'R recovery'], par: { 'Z group': [], 'T treatment': ['Z group'], 'R recovery': ['Z group', 'T treatment'] }, pos: { 'Z group': net.pos.Z, 'T treatment': net.pos.T, 'R recovery': net.pos.R } };
      drawNet(z, net2, [16, 16, 250, 150], { cut: f.cut ? [['Z group', 'T treatment']] : [], fill: v => v === 'T treatment' && f.cut ? c.cv : c.surf, ink: v => v === 'T treatment' && f.cut ? '#fff' : c.ink, sub: v => v === 'T treatment' && f.cut ? 'set by do( )' : '' });
      if (f.stage >= 2) {
        const x0 = 300, y0 = 30, cw = [70, 70, 140, 80];
        ['group', 'treatment', 'recovered / total', 'rate'].forEach((h, i) => D.text(g, h, x0 + cw.slice(0, i).reduce((a, b) => a + b, 0), y0, { s: 11.5, b: true, c: c.ink2 }));
        f.rows.forEach((r, i) => {
          const y = y0 + 22 + i * 22, rate = r.k / r.n;
          const best = f.grp && f.rows.filter(q => q.z === r.z).every(q => q.k / q.n <= rate);
          [r.z, r.t, `${r.k} / ${r.n}`, `${(100 * rate).toFixed(1)}%`].forEach((s, k) => D.text(g, s, x0 + cw.slice(0, k).reduce((a, b) => a + b, 0), y, { s: 12, b: k === 3 && best, mono: k > 1, c: k === 3 && best ? c.green : c.ink }));
        });
      }
      const bar = (y, label, v, col) => {
        const bx = 140, bw = z.W - bx - 90;
        D.text(g, label, 20, y + 16, { s: fit(g, label, 115, 12, { b: true }), b: true, c: c.ink });
        rr(g, bx, y, bw, 22, 5, { fill: c.bg, stroke: c.line, w: 1 });
        rr(g, bx, y, Math.max(2, bw * v), 22, 5, { fill: col });
        D.text(g, `${(100 * v).toFixed(1)}%`, bx + bw + 8, y + 16, { s: 12.5, b: true, mono: true, c: c.ink });
      };
      const [A, B] = f.Ts;
      const obs = tt => { const rs = f.rows.filter(r => r.t === tt); return rs.reduce((a, r) => a + r.k, 0) / rs.reduce((a, r) => a + r.n, 0); };
      let y = 220;
      if (f.obs) { D.text(g, 'Seeing: P(R | T)', 20, y - 6, { s: 12, b: true, c: c.ink2 }); bar(y, `T = ${A}`, obs(A), c.orange); bar(y + 28, `T = ${B}`, obs(B), c.orange); y += 72; }
      if (f.pz) D.text(g, 'Weights: ' + f.pz.map(([zz, v]) => `P(${zz}) = ${f3(v)}`).join(', '), 20, y + 2, { s: 12, b: true, c: c.cv });
      if (f.dA !== undefined) { D.text(g, 'Doing: P(R | do(T))', 20, y + 30, { s: 12, b: true, c: c.ink2 }); bar(y + 36, `do(T = ${A})`, f.dA, c.green); bar(y + 64, `do(T = ${B})`, f.dB, c.green); }
      if (f.done) tag(g, 'done', z.W - 40, z.H - 16, { s: 12, fill: c.green, stroke: c.green, c: '#fff' });
    }
  });
})();
