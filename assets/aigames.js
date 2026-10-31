/* ===== Advanced AI animations, part 2: games, dominance, iterated elimination and Quiz 1.
   Uses CVZ (assets/cvviz.js) and the helpers AIZ from assets/aiwidgets.js. A two player table is written as text:
     rows: M C
     cols: M C
     -2,-2  -5,-1
     -1,-5  -4,-4
   Each cell is "row player's payoff, column player's payoff". ===== */
(() => {
  const { D, def } = CVZ;
  const { tw, rr, fit, tag, fmt, num, UF } = AIZ;

  const GAMES = {
    pd: "rows: M C\ncols: M C\n-2,-2  -5,-1\n-1,-5  -4,-4",
    altru: "rows: M C\ncols: M C\n-3,-3  -5.5,-3.5\n-3.5,-5.5  -6,-6",
    rps: "rows: R P S\ncols: R P S\n0,0  -1,1  1,-1\n1,-1  0,0  -1,1\n-1,1  1,-1  0,0",
    mkt: "rows: L M H\ncols: L M H\n6,6  2,8  0,4\n8,2  4,4  1,3\n4,0  3,1  2,2",
    slide11: "rows: U M D\ncols: L C R\n4,3  5,1  6,2\n2,1  8,4  3,6\n3,0  9,6  2,8",
    farmers: "rows: H Mod\ncols: H Mod\n2,2  5,0\n0,5  3,3",
    ride: "rows: S Md Lg\ncols: S Md Lg\n5,5  9,2  3,3\n2,9  6,6  1,4\n3,3  4,1  2,2",
    b1: "rows: T B\ncols: L R\n4,3  2,4\n3,1  1,2",
    b3: "rows: T M B\ncols: L C R\n2,0  1,1  4,2\n3,4  1,2  2,3\n1,3  0,2  3,0",
    d2: "rows: A B C D\ncols: W X Y Z\n5,2  2,6  1,4  0,4\n0,0  3,2  0,1  1,1\n7,0  2,2  1,5  5,1\n9,5  1,3  0,2  4,8",
    stag: "rows: S H\ncols: S H\n4,4  0,3\n3,0  3,3",
    pennies: "rows: H T\ncols: H T\n1,-1  -1,1\n-1,1  1,-1",
    weak: "rows: T M B\ncols: L R\n1,1  0,0\n1,1  2,1\n0,0  2,1",
    hotel: "rows: 1 2 3 4 5\ncols: 1 2 3 4 5\n2.5,2.5  1,4  1.5,3.5  2,3  2.5,2.5\n4,1  2.5,2.5  2,3  2.5,2.5  3,2\n3.5,1.5  3,2  2.5,2.5  3,2  3.5,1.5\n3,2  2.5,2.5  2,3  2.5,2.5  4,1\n2.5,2.5  2,3  1.5,3.5  1,4  2.5,2.5",
    dbert: "rows: 1 2 3 4 5\ncols: 1 2 3 4 5\n0,0  0,0  0,0  0,0  0,0\n0,0  5,5  10,0  10,0  10,0\n0,0  0,10  10,10  20,0  20,0\n0,0  0,10  0,20  15,15  30,0\n0,0  0,10  0,20  0,30  20,20",
    subsidy: "rows: L M H\ncols: L M H\n9,9  5,8  3,4\n8,5  4,4  1,3\n4,3  3,1  2,2"
  };
  const GOPTS = [['pd', "Prisoner's Dilemma"], ['altru', "Prisoner's Dilemma with altruism"], ['rps', 'Rock, Paper, Scissors'], ['mkt', 'Marketing Campaign War'],
    ['slide11', 'The 3 × 3 game of slide 11'], ['farmers', 'Two farmers and one aquifer'], ['ride', 'Ride hailing incentives'], ['b1', 'A clean dominant strategy game (B1)'],
    ['b3', 'Practice B3 (3 × 3)'], ['d2', 'Practice D2 (4 × 4)'], ['stag', 'Stag Hunt'], ['pennies', 'Matching Pennies'], ['weak', 'Weak dominance order game'],
    ['hotel', 'Location game, positions 1 to 5'], ['dbert', 'Discrete Bertrand, prices 1 to 5'], ['subsidy', 'Marketing War with a subsidy on L'], ['custom', 'My own table']];

  function parseGame(txt) {
    let R = null, C = null;
    const cells = [];
    String(txt).split('\n').map(l => l.trim()).filter(Boolean).forEach(l => {
      const m = l.match(/^(rows|cols)\s*:\s*(.*)$/i);
      if (m) { const names = m[2].split(/[\s,]+/).filter(Boolean); if (m[1].toLowerCase() === 'rows') R = names; else C = names; return; }
      const pairs = [...l.replace(/−/g, '-').matchAll(/(-?\d*\.?\d+)\s*,\s*(-?\d*\.?\d+)/g)].map(q => [+q[1], +q[2]]);
      if (pairs.length) cells.push(pairs);
    });
    if (!cells.length) return null;
    const nc = Math.min(...cells.map(r => r.length));
    const a = cells.map(r => r.slice(0, nc).map(q => q[0])), b = cells.map(r => r.slice(0, nc).map(q => q[1]));
    R = (R || []).slice(0, a.length); C = (C || []).slice(0, nc);
    while (R.length < a.length) R.push('r' + (R.length + 1));
    while (C.length < nc) C.push('c' + (C.length + 1));
    return { R, C, a, b, nr: a.length, nc };
  }
  /* keep the text area in step with the preset menu */
  function sync(z) {
    const p = z.p;
    if (z.state.pre !== p.pre) {
      z.state.pre = p.pre;
      if (p.pre !== 'custom' && GAMES[p.pre]) {
        p.txt = GAMES[p.pre];
        const ta = z.el.querySelector('[data-k="txt"]');
        if (ta) ta.value = p.txt;
      }
    }
    return parseGame(p.txt);
  }
  const gameParams = (pre, extra = []) => [
    { k: 'pre', label: 'Game', type: 'select', v: pre, opts: GOPTS },
    { k: 'txt', label: 'Payoff table (edit any number)', type: 'area', v: GAMES[pre] || '', help: 'Each cell is: row player payoff, column player payoff.' }
  ].concat(extra);
  /* best responses and pure Nash equilibria */
  function analyse(G) {
    const br1 = G.C.map((_, c) => { const m = Math.max(...G.a.map(r => r[c])); return G.R.map((_, r) => G.a[r][c] === m); });
    const br2 = G.R.map((_, r) => { const m = Math.max(...G.b[r]); return G.C.map((_, c) => G.b[r][c] === m); });
    const ne = [];
    G.R.forEach((_, r) => G.C.forEach((_, c) => { if (br1[c][r] && br2[r][c]) ne.push([r, c]); }));
    return { br1, br2, ne };
  }
  /* draw a payoff table. o: x, y, cw, ch, deadR, deadC, sel [r, c], mark(r, c) -> colour, brs */
  function drawGame(g, z, G, o) {
    const { x, y } = o, cw = o.cw, ch = o.ch;
    D.text(g, 'Player 1 (rows)', x - 6, y + ch * G.nr / 2 + 18, { a: 'right', s: 10.5, b: true, c: z.col.cv });
    D.text(g, 'Player 2 (columns)', x + cw * G.nc / 2, y - 26, { a: 'center', s: 10.5, b: true, c: z.col.orange });
    G.C.forEach((n, c) => D.text(g, n, x + c * cw + cw / 2, y - 8, { a: 'center', s: fit(g, n, cw - 4, 12.5), b: true, c: (o.deadC && o.deadC.has(c)) ? z.col.line : z.col.ink }));
    G.R.forEach((n, r) => D.text(g, n, x - 8, y + r * ch + ch / 2 + 4, { a: 'right', s: fit(g, n, 40, 12.5), b: true, c: (o.deadR && o.deadR.has(r)) ? z.col.line : z.col.ink }));
    G.R.forEach((_, r) => G.C.forEach((_, c) => {
      const dead = (o.deadR && o.deadR.has(r)) || (o.deadC && o.deadC.has(c));
      const mk = o.mark ? o.mark(r, c) : null;
      D.rect(g, x + c * cw, y + r * ch, cw, ch, { fill: mk || z.col.surf, stroke: z.col.line, w: 1 });
      const s1 = fmt(G.a[r][c], 2), s2 = fmt(G.b[r][c], 2), fs = Math.min(13, cw / 5.2);
      const w1 = tw(g, s1, { s: fs, b: true, mono: true }), w2 = tw(g, ', ' + s2, { s: fs, b: true, mono: true });
      const sx = x + c * cw + cw / 2 - (w1 + w2) / 2, sy = y + r * ch + ch / 2 + 4;
      D.text(g, s1, sx, sy, { s: fs, b: true, mono: true, c: dead ? z.col.line : mk ? '#fff' : z.col.cv });
      D.text(g, ', ' + s2, sx + w1, sy, { s: fs, b: true, mono: true, c: dead ? z.col.line : mk ? '#fff' : z.col.orange });
      if (o.brs && !dead) {
        if (o.brs.br1[c][r]) D.circle(g, x + c * cw + 7, y + r * ch + 7, 3.5, { fill: z.col.cv });
        if (o.brs.br2[r][c]) D.circle(g, x + c * cw + cw - 7, y + r * ch + 7, 3.5, { fill: z.col.orange });
      }
      if (dead) D.line(g, x + c * cw + 4, y + r * ch + ch / 2, x + c * cw + cw - 4, y + r * ch + ch / 2, z.col.red, 1.5);
    }));
    if (o.sel) D.rect(g, x + o.sel[1] * cw + 1.5, y + o.sel[0] * ch + 1.5, cw - 3, ch - 3, { stroke: z.col.ink, w: 3 });
    return { cell: (r, c) => [x + c * cw + cw / 2, y + r * ch + ch / 2] };
  }
  const geom = (z, G, left = 70, maxW = 300) => {
    const cw = Math.min(92, maxW / G.nc), ch = Math.min(46, 230 / G.nr);
    return { x: left, y: 52, cw, ch };
  };

  /* ================= 4.1 normal form games, best responses and unilateral deviations ================= */
  def('bimatrix', {
    title: 'A game in normal form: payoffs, best responses and deviations',
    sub: 'Click a cell to propose it. Arrows show every unilateral deviation: green if the mover strictly gains. Dots mark best responses.',
    W: 560, H: 320,
    params: gameParams('pd', [
      { k: 'r', label: 'Proposed row', type: 'range', v: 2, min: 1, max: 5 },
      { k: 'c', label: 'Proposed column', type: 'range', v: 2, min: 1, max: 5 },
      { k: 'br', label: 'Show best response dots', type: 'check', v: true }
    ]),
    tips: [
      { t: "Prisoner's Dilemma at (C, C): both deviation arrows are red, nobody gains by moving alone. It is self enforcing even though (M, M) is better for both.", set: { pre: 'pd', r: 2, c: 2 } },
      { t: 'Now propose (M, M). Both arrows turn green: each prisoner gains by confessing alone. The lawyer threat is what held it, not the game.', set: { pre: 'pd', r: 1, c: 1 } },
      { t: 'Rock, Paper, Scissors: try every cell. Someone always wants to move, so no pure profile is self enforcing.', set: { pre: 'rps', r: 1, c: 1 } },
      { t: 'Slide 11 at (U, L): no profitable move for either player. At (M, C) = (8, 4) both want to move.', set: { pre: 'slide11', r: 1, c: 1 } },
      { t: 'Stag Hunt has two self enforcing cells, (S, S) and (H, H). Where both dots meet is a pure Nash equilibrium.', set: { pre: 'stag', r: 2, c: 2 } }
    ],
    click(z, x, y, kind) {
      if (kind !== 'down') return;
      const G = parseGame(z.p.txt); if (!G) return;
      const o = geom(z, G);
      const c = Math.floor((x - o.x) / o.cw), r = Math.floor((y - o.y) / o.ch);
      if (r >= 0 && r < G.nr && c >= 0 && c < G.nc) z.set({ r: r + 1, c: c + 1 });
    },
    draw(z) {
      const { g, p } = z;
      const G = sync(z); if (!G) return 'Write a table like "-2,-2 -5,-1" on each row.';
      const r = Math.min(p.r, G.nr) - 1, c = Math.min(p.c, G.nc) - 1;
      const A = analyse(G), o = geom(z, G);
      const at = drawGame(g, z, G, Object.assign({ sel: [r, c], brs: p.br ? A : null }, o));
      const [cx, cy] = at.cell(r, c);
      G.R.forEach((_, r2) => { if (r2 === r) return; const [tx, ty] = at.cell(r2, c); const gain = G.a[r2][c] > G.a[r][c]; D.arrow(g, cx - 10, cy + (ty > cy ? 10 : -10), tx - 10, ty + (ty > cy ? -10 : 10), gain ? z.col.green : z.col.red, 2); });
      G.C.forEach((_, c2) => { if (c2 === c) return; const [tx, ty] = at.cell(r, c2); const gain = G.b[r][c2] > G.b[r][c]; D.arrow(g, cx + (tx > cx ? 18 : -18), cy + 10, tx + (tx > cx ? -18 : 18), ty + 10, gain ? z.col.green : z.col.red, 2); });
      const g1 = G.R.map((_, r2) => G.a[r2][c] - G.a[r][c]).filter((_, r2) => r2 !== r), g2 = G.C.map((_, c2) => G.b[r][c2] - G.b[r][c]).filter((_, c2) => c2 !== c);
      const ok = g1.every(v => v <= 0) && g2.every(v => v <= 0);
      const lx = o.x + o.cw * G.nc + 30;
      let yy = 40;
      const L = (s, col) => { D.text(g, s, lx, yy, { s: 12, b: true, c: col || z.col.ink }); yy += 20; };
      L(`Profile (${G.R[r]}, ${G.C[c]})`);
      L(`v₁ = ${fmt(G.a[r][c], 2)},  v₂ = ${fmt(G.b[r][c], 2)}`);
      L(`Best gain for player 1: ${fmt(Math.max(0, ...g1), 2)}`, z.col.cv);
      L(`Best gain for player 2: ${fmt(Math.max(0, ...g2), 2)}`, z.col.orange);
      L(ok ? 'Self enforcing ✓' : 'Not self enforcing ✗', ok ? z.col.green : z.col.red);
      yy += 6;
      L('Pure Nash equilibria:', z.col.ink2);
      L(A.ne.length ? A.ne.map(([a, b]) => `(${G.R[a]}, ${G.C[b]})`).join('  ') : 'none in pure strategies', z.col.ink);
      return `${ok ? '<b>No player gains by deviating alone</b>, so this profile is self enforcing.' : '<b>Someone gains by deviating alone</b>, so this proposal would not hold without outside enforcement.'} Player 1 compares the first numbers down a column. Player 2 compares the second numbers along a row.`;
    }
  });

  /* ================= 4.2 modelling games ================= */
  def('cournot', {
    title: 'Cournot duopoly: two reaction curves and where they cross',
    sub: 'Each firm picks a quantity. Its best quantity falls as the rival produces more. The crossing is a mutual best response.',
    W: 560, H: 320,
    params: [
      { k: 'a', label: 'Demand intercept a', type: 'range', v: 100, min: 20, max: 200 },
      { k: 'b', label: 'Demand slope b', type: 'range', v: 1, min: 0.25, max: 4, step: 0.25 },
      { k: 'c1', label: 'Firm 1 unit cost c₁', type: 'range', v: 10, min: 0, max: 80 },
      { k: 'c2', label: 'Firm 2 unit cost c₂', type: 'range', v: 10, min: 0, max: 80 },
      { k: 's2', label: 'Suppose firm 2 makes', type: 'range', v: 50, min: 0, max: 150 }
    ],
    tips: [
      { t: 'The lecture numbers a = 100, b = 1, c = 10. The curves cross at (30, 30): price 40, profit 900 each.', set: { a: 100, b: 1, c1: 10, c2: 10 } },
      { t: 'Practice B: a = 40, c = 10. Equilibrium 10 each, price 20, profit 100.', set: { a: 40, b: 1, c1: 10, c2: 10, s2: 10 } },
      { t: 'Practice F: a = 60, c₁ = 12, c₂ = 18. The cheaper firm makes 18, the other 12. Equal looking constant costs do not mean equal outcomes.', set: { a: 60, b: 1, c1: 12, c2: 18, s2: 12 } },
      { t: 'Slide "firm 2 makes" to 0. Firm 1 then produces the monopoly quantity (a − c) ⁄ (2b).', set: { a: 100, b: 1, c1: 10, c2: 10, s2: 0 } }
    ],
    draw(z) {
      const { g, p } = z;
      const br1 = s => Math.max(0, (p.a - p.c1 - p.b * s) / (2 * p.b)), br2 = s => Math.max(0, (p.a - p.c2 - p.b * s) / (2 * p.b));
      let q1 = (p.a - 2 * p.c1 + p.c2) / (3 * p.b), q2 = (p.a - 2 * p.c2 + p.c1) / (3 * p.b);
      if (q2 < 0) { q2 = 0; q1 = br1(0); } if (q1 < 0) { q1 = 0; q2 = br2(0); }
      const M = Math.max(p.a / p.b, 1);
      const m = D.axes(g, z, [60, 14, 250, 250], [0, M], [0, M], { nx: 4, ny: 4, xl: 'q₁', yl: 'q₂' });
      D.curve(g, s2 => s2, [0, 0], m, z.col.cv, 0);
      g.save(); g.strokeStyle = z.col.cv; g.lineWidth = 2.5; g.beginPath();
      for (let i = 0; i <= 100; i++) { const s2 = M * i / 100, s1 = br1(s2); if (i) g.lineTo(m.sx(s1), m.sy(s2)); else g.moveTo(m.sx(s1), m.sy(s2)); } g.stroke(); g.restore();
      D.curve(g, br2, [0, M], m, z.col.orange, 2.5);
      D.circle(g, m.sx(q1), m.sy(q2), 7, { fill: z.col.green, stroke: '#fff', w: 2 });
      const s2 = Math.min(p.s2, M);
      D.line(g, m.sx(0), m.sy(s2), m.sx(br1(s2)), m.sy(s2), z.col.ink2, 1, [4, 3]);
      D.circle(g, m.sx(br1(s2)), m.sy(s2), 5, { fill: z.col.cv });
      D.text(g, 'BR₁', m.sx(br1(M * 0.05)) + 6, m.sy(M * 0.05) - 6, { s: 11.5, b: true, c: z.col.cv });
      D.text(g, 'BR₂', m.sx(M * 0.05) + 6, m.sy(br2(M * 0.05)) - 6, { s: 11.5, b: true, c: z.col.orange });
      const P = Math.max(0, p.a - p.b * (q1 + q2)), pr1 = (P - p.c1) * q1, pr2 = (P - p.c2) * q2;
      const lx = 345, L = [['Firm 1 best reply to ' + fmt(s2, 1), fmt(br1(s2), 2)], ['Equilibrium q₁, q₂', fmt(q1, 2) + ', ' + fmt(q2, 2)], ['Price a − b(q₁ + q₂)', fmt(P, 2)], ['Profits', fmt(pr1, 1) + ', ' + fmt(pr2, 1)], ['Monopoly q = (a − c₁) ⁄ 2b', fmt(br1(0), 2)]];
      L.forEach(([k, v], i) => { D.text(g, k, lx, 30 + i * 44, { s: 11.5, b: true, c: z.col.ink2 }); D.text(g, v, lx, 48 + i * 44, { s: 14, b: true, c: z.col.ink, mono: true }); });
      return `Best response sᵢ = (a − cᵢ − b sⱼ) ⁄ (2b). Solving both together gives q₁ = (a − 2c₁ + c₂) ⁄ 3b = <b>${fmt(q1, 3)}</b> and q₂ = (a − 2c₂ + c₁) ⁄ 3b = <b>${fmt(q2, 3)}</b>. At the green dot neither firm wants to change its quantity alone.`;
    }
  });

  def('bertrand', {
    title: 'Bertrand price competition: the payoff jumps',
    sub: 'Firm 1 picks a price p₁. Cheaper takes the whole market, a tie splits it, dearer sells nothing. The rival price is fixed.',
    W: 560, H: 300,
    params: [
      { k: 'a', label: 'Demand intercept a', type: 'range', v: 100, min: 20, max: 200 },
      { k: 'b', label: 'Demand slope b', type: 'range', v: 1, min: 0.5, max: 4, step: 0.5 },
      { k: 'c', label: 'Unit cost c', type: 'range', v: 10, min: 0, max: 60 },
      { k: 'p2', label: 'Rival price p₂', type: 'range', v: 40, min: 0, max: 200 },
      { k: 'p1', label: 'Your price p₁', type: 'range', v: 39.9, min: 0, max: 200, step: 0.1 }
    ],
    tips: [
      { t: 'The numbers from the notes: rival at 40. At 39.9 you earn about 1797, at 40 only 900, at 40.1 nothing. Undercutting by a paisa nearly doubles profit.', set: { a: 100, b: 1, c: 10, p2: 40, p1: 39.9 } },
      { t: 'Put the rival at the unit cost, 10. Every price you choose earns 0 or a loss. This is the Bertrand paradox: two firms are enough to push price to cost.', set: { p2: 10, p1: 10 } },
      { t: 'Price below cost at 5 with the rival at 3. You sell nothing and earn 0, the same as pricing at cost. That tie is why below cost prices are only weakly dominated.', set: { p2: 3, p1: 5 } }
    ],
    draw(z) {
      const { g, p } = z;
      const q = pr => Math.max(0, (p.a - pr) / p.b);
      const v = pr => pr < p.p2 ? (pr - p.c) * q(pr) : pr === p.p2 ? (pr - p.c) * q(pr) / 2 : 0;
      const P = Math.max(p.a, 1), vals = []; for (let i = 0; i <= 400; i++) vals.push(v(P * i / 400));
      const top = Math.max(...vals, 10), bot = Math.min(0, ...vals);
      const m = D.axes(g, z, [70, 14, 460, 220], [0, P], [bot, top * 1.1], { nx: 5, ny: 4, xl: 'firm 1 price p₁', yl: 'profit v₁' });
      g.save(); g.strokeStyle = z.col.cv; g.lineWidth = 2.5; g.beginPath(); let started = false;
      for (let i = 0; i <= 400; i++) { const x = P * i / 400; if (x >= p.p2) break; const y = v(x); if (!started) { g.moveTo(m.sx(x), m.sy(y)); started = true; } else g.lineTo(m.sx(x), m.sy(y)); }
      g.stroke(); g.restore();
      if (p.p2 < P) D.line(g, m.sx(Math.min(P, p.p2)), m.sy(0), m.sx(P), m.sy(0), z.col.cv, 2.5);
      if (p.p2 <= P) { D.circle(g, m.sx(p.p2), m.sy((p.p2 - p.c) * q(p.p2) / 2), 5, { fill: z.col.orange }); D.circle(g, m.sx(p.p2), m.sy((p.p2 - p.c) * q(p.p2)), 5, { stroke: z.col.cv, fill: z.col.surf, w: 2 }); }
      D.line(g, m.sx(p.c), 14, m.sx(p.c), 234, z.col.ink2, 1, [3, 3]); D.text(g, 'cost', m.sx(p.c) + 4, 28, { s: 11, c: z.col.ink2 });
      const p1 = Math.min(p.p1, P), here = v(p1);
      D.circle(g, m.sx(p1), m.sy(here), 7, { fill: z.col.green, stroke: '#fff', w: 2 });
      const cs = p1 < p.p2 ? 'cheaper: whole market' : p1 === p.p2 ? 'tie: half the market' : 'dearer: no sales';
      return `At p₁ = ${fmt(p1, 2)} you are ${cs}, selling ${fmt(p1 < p.p2 ? q(p1) : p1 === p.p2 ? q(p1) / 2 : 0, 2)} units for profit <b>${fmt(here, 2)}</b>. The open circle is the limit from just below p₂, the orange dot is the tie. The payoff has no smooth peak.`;
    }
  });

  def('lamp', {
    title: 'The streetlamp: a public good that needs enough contributors',
    sub: 'Each player pays c or nothing. The lamp is built if at least k pay, and then everyone gets V. Pick a profile and test each player\'s move.',
    W: 560, H: 300,
    params: [
      { k: 'n', label: 'Players n', type: 'range', v: 3, min: 2, max: 7 },
      { k: 'k', label: 'Contributors needed k', type: 'range', v: 2, min: 1, max: 7 },
      { k: 'V', label: 'Value of the lamp V', type: 'range', v: 3, min: 0.5, max: 10, step: 0.5 },
      { k: 'c', label: 'Cost of contributing c', type: 'range', v: 1, min: 0.5, max: 10, step: 0.5 },
      { k: 'm', label: 'Contributors in the shown profile', type: 'range', v: 3, min: 0, max: 7 },
      { k: 'refund', label: 'Refund if the lamp is not built', type: 'check', v: false }
    ],
    tips: [
      { t: 'The lecture game (n = 3, k = 2, V = 3, c = 1) with all three paying. Each would rather stop, 3 > 2, so (1, 1, 1) is not self enforcing.', set: { n: 3, k: 2, V: 3, c: 1, m: 3, refund: false } },
      { t: 'Exactly two pay. Each payer is pivotal (stopping kills the lamp) and the third has no reason to join. Stable.', set: { m: 2 } },
      { t: 'Nobody pays. A lone contributor just loses c, so this sad profile is also stable when k ≥ 2.', set: { m: 0 } },
      { t: 'Turn on refunds. Contributing is now never a loss, but with two others paying it still beats paying, so free riding survives.', set: { refund: true, m: 3 } }
    ],
    draw(z) {
      const { g, p } = z;
      const n = p.n, k = Math.min(p.k, n), m = Math.min(p.m, n);
      const pay = (si, mt) => (mt >= k ? p.V : 0) - (si && !(p.refund && mt < k) ? p.c : 0);
      const built = m >= k;
      D.text(g, built ? 'Lamp built' : 'No lamp', 280, 26, { a: 'center', s: 14, b: true, c: built ? z.col.orange : z.col.ink2 });
      D.circle(g, 280, 60, 16, { fill: built ? z.col.yellow : z.col.bg, stroke: z.col.line });
      D.line(g, 280, 76, 280, 110, z.col.ink2, 3);
      const xs = [...Array(n)].map((_, i) => 280 + (i - (n - 1) / 2) * 70);
      let stable = true;
      xs.forEach((x, i) => {
        const si = i < m ? 1 : 0, now = pay(si, m), alt = pay(1 - si, m + (si ? -1 : 1)), gain = alt > now + 1e-12;
        if (gain) stable = false;
        D.circle(g, x, 150, 18, { fill: si ? z.col.cv : z.col.bg, stroke: z.col.line });
        D.text(g, si ? 'pays' : 'free', x, 151, { a: 'center', bl: 'middle', s: 10.5, b: true, c: si ? '#fff' : z.col.ink });
        D.text(g, 'gets ' + fmt(now, 2), x, 186, { a: 'center', s: 11, b: true, c: z.col.ink });
        D.text(g, (si ? 'stop: ' : 'join: ') + fmt(alt, 2), x, 204, { a: 'center', s: 10.5, c: gain ? z.col.green : z.col.ink2 });
      });
      const st = [];
      for (let t = 0; t <= n; t++) {
        let ok = true;
        if (t > 0 && pay(0, t - 1) > pay(1, t)) ok = false;
        if (t < n && pay(1, t + 1) > pay(0, t)) ok = false;
        if (ok) st.push(t);
      }
      D.text(g, 'Self enforcing when the number of payers is: ' + (st.join(', ') || 'never'), 280, 240, { a: 'center', s: 12.5, b: true, c: z.col.cv });
      D.text(g, 'payoff vᵢ = V · 1[Σ sⱼ ≥ k] − c sᵢ', 280, 264, { a: 'center', s: 12, c: z.col.ink2, mono: true });
      return `With ${m} of ${n} paying, ${stable ? '<b>no player gains by switching alone</b>' : '<b>at least one player gains by switching</b> (green)'}. A contributor only helps when pivotal, exactly k − 1 others paying. That is the free rider problem.`;
    }
  });

  /* ================= 4.3 Pareto optimality ================= */
  def('pareto', {
    title: 'Pareto optimality: is any outcome better for everyone?',
    sub: 'Each dot is one profile at (v₁, v₂). Green dots are Pareto optimal. Altruism adds a share α of the other player\'s payoff to your own.',
    W: 560, H: 320,
    params: gameParams('pd', [{ k: 'al', label: 'Altruism weight α', type: 'range', v: 0, min: 0, max: 1, step: 0.05 }]),
    tips: [
      { t: "Prisoner's Dilemma: (C, C) is the only grey dot, Pareto dominated by (M, M), and it is exactly what dominance picks.", set: { pre: 'pd', al: 0 } },
      { t: 'Set α = 0.5, the lecture altruism. The orange ring (the dominant strategy outcome) moves to (M, M), which is now the only Pareto optimal profile.', set: { pre: 'pd', al: 0.5 } },
      { t: 'Rock, Paper, Scissors is zero sum: every dot lies on the line v₁ + v₂ = 0 and every profile is Pareto optimal.', set: { pre: 'rps', al: 0 } },
      { t: 'Marketing Campaign War: (L, L), (L, M) and (M, L) are optimal. The lopsided (2, 8) is optimal too, so Pareto says nothing about fairness.', set: { pre: 'mkt', al: 0 } }
    ],
    draw(z) {
      const { g, p } = z;
      const G0 = sync(z); if (!G0) return 'Write a payoff table.';
      const G = Object.assign({}, G0, { a: G0.a.map((r, i) => r.map((v, j) => v + p.al * G0.b[i][j])), b: G0.b.map((r, i) => r.map((v, j) => v + p.al * G0.a[i][j])) });
      const pts = [];
      G.R.forEach((rn, r) => G.C.forEach((cn, c) => pts.push({ r, c, x: G.a[r][c], y: G.b[r][c], n: rn + ',' + cn })));
      const dom = (s, t) => s.x >= t.x && s.y >= t.y && (s.x > t.x || s.y > t.y);
      pts.forEach(q => { q.opt = !pts.some(s => dom(s, q)); });
      const xs = pts.map(q => q.x), ys = pts.map(q => q.y);
      const pad = v => (v || 1) * 0.15;
      const xr = [Math.min(...xs) - pad(Math.max(...xs) - Math.min(...xs)), Math.max(...xs) + pad(Math.max(...xs) - Math.min(...xs))];
      const yr = [Math.min(...ys) - pad(Math.max(...ys) - Math.min(...ys)), Math.max(...ys) + pad(Math.max(...ys) - Math.min(...ys))];
      const m = D.axes(g, z, [60, 14, 300, 260], xr, yr, { nx: 4, ny: 4, xl: 'v₁ (player 1)', yl: 'v₂ (player 2)' });
      const d1 = G.R.findIndex((_, r) => G.R.every((_, r2) => r2 === r || G.C.every((_, c) => G.a[r][c] > G.a[r2][c])));
      const d2 = G.C.findIndex((_, c) => G.C.every((_, c2) => c2 === c || G.R.every((_, r) => G.b[r][c] > G.b[r][c2])));
      const seen = {};
      pts.forEach(q => {
        const key = q.x + '|' + q.y; seen[key] = (seen[key] || 0) + 1;
        D.circle(g, m.sx(q.x), m.sy(q.y), 6, { fill: q.opt ? z.col.green : z.col.line, stroke: '#fff', w: 1.5 });
        if (q.r === d1 && q.c === d2) D.circle(g, m.sx(q.x), m.sy(q.y), 11, { stroke: z.col.orange, w: 3 });
        D.text(g, q.n, m.sx(q.x) + 9, m.sy(q.y) - 6 + (seen[key] - 1) * 13, { s: 10.5, b: true, c: z.col.ink });
      });
      const opt = pts.filter(q => q.opt).map(q => `(${q.n})`);
      const lx = 400; let y = 36;
      D.text(g, 'Pareto optimal', lx, y, { s: 12, b: true, c: z.col.green }); y += 18;
      opt.forEach(s => { if (y < z.H - 60) { D.text(g, s, lx, y, { s: 12, c: z.col.ink, mono: true }); y += 16; } });
      y += 10;
      D.text(g, 'Dominant strategy outcome', lx, y, { s: 12, b: true, c: z.col.orange }); y += 18;
      D.text(g, d1 >= 0 && d2 >= 0 ? `(${G.R[d1]}, ${G.C[d2]})` : 'none', lx, y, { s: 12, c: z.col.ink, mono: true });
      return `${opt.length} of ${pts.length} profiles are Pareto optimal. ` + (d1 >= 0 && d2 >= 0 ? (pts.find(q => q.r === d1 && q.c === d2).opt ? 'The dominant strategy outcome is Pareto optimal here.' : '<b>The dominant strategy outcome is Pareto dominated</b>: self interest leaves payoff on the table.') : 'There is no dominant strategy outcome to judge.');
    }
  });

  /* ================= 5.1 dominance ================= */
  def('dominance', {
    title: 'Does one strategy dominate another?',
    sub: 'Pick a player and two of their strategies. Compare only that player\'s own payoffs, one opponent move at a time.',
    W: 560, H: 330,
    params: gameParams('mkt', [
      { k: 'pl', label: 'Player', type: 'select', v: '1', opts: [['1', 'Player 1 (rows, first numbers)'], ['2', 'Player 2 (columns, second numbers)']] },
      { k: 's', label: 'Strategy number to test as the winner', type: 'range', v: 2, min: 1, max: 5 },
      { k: 't', label: 'Strategy number to test as the loser', type: 'range', v: 1, min: 1, max: 5 }
    ]),
    tips: [
      { t: 'Marketing War, player 1, M against L: 8 > 6, 4 > 2, 1 > 0. M strictly dominates L.', set: { pre: 'mkt', pl: '1', s: 2, t: 1 } },
      { t: 'Now M against H: 8 > 4, 4 > 3, but 1 < 2. One reversal is enough to kill dominance.', set: { pre: 'mkt', pl: '1', s: 2, t: 3 } },
      { t: "Prisoner's Dilemma, C against M: C wins against both moves. With two strategies, dominating is the same as dominant.", set: { pre: 'pd', pl: '1', s: 2, t: 1 } },
      { t: 'Slide 11, player 2, R against C: 2 > 1, 6 > 4, 8 > 6. C is strictly dominated, so it is deleted first in IESDS.', set: { pre: 'slide11', pl: '2', s: 3, t: 2 } },
      { t: 'Weak dominance game, player 1, M against T: 1 = 1 and 2 > 0. Weak but not strict.', set: { pre: 'weak', pl: '1', s: 2, t: 1 } }
    ],
    draw(z) {
      const { g, p } = z;
      const G = sync(z); if (!G) return 'Write a payoff table.';
      const one = p.pl === '1', names = one ? G.R : G.C, opp = one ? G.C : G.R, n = names.length;
      const s = Math.min(p.s, n) - 1, t = Math.min(p.t, n) - 1;
      const v = (i, j) => one ? G.a[i][j] : G.b[j][i];
      const o = geom(z, G, 70, 240);
      drawGame(g, z, G, Object.assign({ mark: (r, c) => (one ? (r === s ? z.col.green : r === t ? z.col.red : null) : (c === s ? z.col.green : c === t ? z.col.red : null)) }, o));
      const lx = o.x + o.cw * G.nc + 26;
      D.text(g, `${names[s]} vs ${names[t]}`, lx, 30, { s: 13, b: true, c: z.col.ink });
      let strict = s !== t, weak = s !== t, oneStrict = false;
      opp.forEach((on, j) => {
        const a = v(s, j), b = v(t, j), y = 54 + j * 22;
        if (y > z.H - 70) return;
        const mark = a > b ? '>' : a === b ? '=' : '<';
        if (!(a > b)) strict = false; if (a < b) weak = false; if (a > b) oneStrict = true;
        D.text(g, `vs ${on}:  ${fmt(a, 2)} ${mark} ${fmt(b, 2)}`, lx, y, { s: 12, b: true, mono: true, c: a > b ? z.col.green : a === b ? z.col.ink2 : z.col.red });
      });
      const verdict = s === t ? 'Pick two different strategies.' : strict ? `${names[s]} strictly dominates ${names[t]}` : weak && oneStrict ? `${names[s]} weakly dominates ${names[t]}` : weak ? 'They tie everywhere (weak both ways under the slide definition)' : 'No dominance';
      D.text(g, verdict, lx, z.H - 76, { s: 12.5, b: true, c: strict ? z.col.green : weak ? z.col.orange : z.col.red });
      /* vocabulary for every strategy of this player */
      const beats = (i, k) => opp.every((_, j) => v(i, j) > v(k, j));
      const cls = names.map((nm, i) => {
        const others = names.map((_, k) => k).filter(k => k !== i);
        const dg = others.some(k => beats(i, k)), dd = others.some(k => beats(k, i)), dt = others.length && others.every(k => beats(i, k)), sb = others.length && others.every(k => beats(k, i));
        return `${nm}: ${[dg && 'dominating', dd && 'dominated', dt && 'DOMINANT', sb && 'submissive'].filter(Boolean).join(', ') || 'none'}`;
      });
      let yy = z.H - 54;
      cls.forEach(s2 => { if (yy < z.H - 4) { D.text(g, s2, lx, yy, { s: 10.5, c: z.col.ink2 }); yy += 14; } });
      return `${verdict}. Strict dominance needs > against <b>every</b> move of the opponent. A strategy is deleted by IESDS if <b>at least one</b> other strategy strictly dominates it.`;
    }
  });

  def('altruism', {
    title: 'How much altruism flips the Prisoner\'s Dilemma?',
    sub: 'Player 1 values w₁ = v₁ + α v₂. The lines show C minus M for player 1, against each move of player 2. Above 0, confessing is better.',
    W: 560, H: 290,
    params: [{ k: 'al', label: 'Altruism weight α', type: 'range', v: 0.5, min: 0, max: 1, step: 0.01 }],
    tips: [
      { t: 'α = 0, pure self interest: both lines are above 0, so C dominates M.', set: { al: 0 } },
      { t: 'α = 0.5, the class example: both lines are below 0, so M dominates C.', set: { al: 0.5 } },
      { t: 'α = 1 ⁄ 3 exactly: both differences are 0 and every comparison ties.', set: { al: 0.33 } }
    ],
    draw(z) {
      const { g, p } = z;
      const dM = a => (-1 - 5 * a) - (-2 - 2 * a), dC = a => (-4 - 4 * a) - (-5 - a);
      const m = D.axes(g, z, [70, 16, 440, 210], [0, 1], [-2.5, 1.5], { nx: 4, ny: 4, xl: 'α', yl: 'w₁(C) − w₁(M)' });
      D.line(g, m.sx(0), m.sy(0), m.sx(1), m.sy(0), z.col.ink2, 1, [4, 3]);
      D.curve(g, dM, [0, 1], m, z.col.cv, 2.5); D.curve(g, a => dC(a) - 0.02, [0, 1], m, z.col.orange, 2.5, 200, [6, 4]);
      D.line(g, m.sx(1 / 3), 16, m.sx(1 / 3), 226, z.col.green, 1.5, [3, 3]);
      D.text(g, 'α = 1 ⁄ 3', m.sx(1 / 3) + 4, 30, { s: 11, b: true, c: z.col.green });
      D.circle(g, m.sx(p.al), m.sy(dM(p.al)), 6, { fill: z.col.cv, stroke: '#fff', w: 2 });
      D.text(g, 'both lines are 1 − 3α', m.sx(0.62), m.sy(dM(0.62)) - 10, { s: 11.5, b: true, c: z.col.ink });
      const w = (s, o) => ({ MM: -2 - 2 * p.al, CM: -1 - 5 * p.al, MC: -5 - p.al, CC: -4 - 4 * p.al })[s + o];
      return `At α = ${fmt(p.al, 2)}: against M, C gives ${fmt(w('C', 'M'), 3)} and M gives ${fmt(w('M', 'M'), 3)}. Against C, C gives ${fmt(w('C', 'C'), 3)} and M gives ${fmt(w('M', 'C'), 3)}. ` +
        (p.al < 1 / 3 - 1e-9 ? '<b>C strictly dominates M.</b>' : p.al > 1 / 3 + 1e-9 ? '<b>M strictly dominates C.</b>' : '<b>Every comparison ties.</b>') + ' A small change in what players care about flips the prediction, so dominant strategy equilibrium is not invariant.';
    }
  });

  /* ================= 5.2 IESDS ================= */
  function iesdsRun(G, mode, order) {
    const R = new Set(G.R.map((_, i) => i)), C = new Set(G.C.map((_, i) => i)), log = [];
    const dom1 = (s, t, strict) => [...C].every(c => strict ? G.a[s][c] > G.a[t][c] : G.a[s][c] >= G.a[t][c]) && (strict || [...C].some(c => G.a[s][c] > G.a[t][c]));
    const dom2 = (s, t, strict) => [...R].every(r => strict ? G.b[r][s] > G.b[r][t] : G.b[r][s] >= G.b[r][t]) && (strict || [...R].some(r => G.b[r][s] > G.b[r][t]));
    let round = 0;
    for (let guard = 0; guard < 40; guard++) {
      const strict = mode !== 'weak';
      const c1 = [], c2 = [];
      [...R].forEach(t => { const by = [...R].find(s => s !== t && dom1(s, t, strict)); if (by !== undefined) c1.push([t, by]); });
      [...C].forEach(t => { const by = [...C].find(s => s !== t && dom2(s, t, strict)); if (by !== undefined) c2.push([t, by]); });
      if (!c1.length && !c2.length) break;
      round++;
      if (mode === 'all') {
        const ev = { round, rows: c1, cols: c2 };
        c1.forEach(([t]) => R.delete(t)); c2.forEach(([t]) => C.delete(t)); log.push(ev);
      } else {
        const pool = c1.map(x => ['r', x]).concat(c2.map(x => ['c', x]));
        const pick = order === 'last' ? pool[pool.length - 1] : pool[0];
        if (R.size === 1 && pick[0] === 'r') { /* never remove the last strategy */ }
        if (pick[0] === 'r') { R.delete(pick[1][0]); log.push({ round, rows: [pick[1]], cols: [] }); } else { C.delete(pick[1][0]); log.push({ round, rows: [], cols: [pick[1]] }); }
      }
    }
    return log;
  }
  def('iesds', {
    title: 'Iterated elimination of strictly dominated strategies',
    sub: 'Each step deletes what is dominated in the game that is left, then looks again. Watch new dominance appear once a row or column is gone.',
    W: 560, H: 330,
    params: gameParams('slide11', [
      { k: 'mode', label: 'Rule', type: 'select', v: 'all', opts: [['all', 'strict, delete everything dominated each round'], ['one', 'strict, one strategy at a time'], ['weak', 'weak dominance, one at a time']] },
      { k: 'order', label: 'When several can go, delete', type: 'select', v: 'first', opts: [['first', 'the first one found (rows first)'], ['last', 'the last one found (columns first)']], show: p => p.mode !== 'all' }
    ]),
    tips: [
      { t: 'Slide 11: C goes first (R beats it), then M and D (U beats both once C is gone), then R. The survivor is (U, L) with (4, 3).', set: { pre: 'slide11', mode: 'all' }, play: true },
      { t: 'Marketing War: L goes for both players in round 1, then nothing. Four profiles survive, so IESDS is not always unique.', set: { pre: 'mkt', mode: 'all' }, play: true },
      { t: 'Change the deletion order on slide 11. Strict elimination always ends at (U, L), whatever the order.', set: { pre: 'slide11', mode: 'one', order: 'last' }, play: true },
      { t: 'Weak dominance with the order game: rows first ends at payoff (2, 1), columns first ends at (1, 1). With weak dominance the order matters.', set: { pre: 'weak', mode: 'weak', order: 'first' }, play: true },
      { t: 'The location game: positions 1 and 5 go, then 2 and 4. Both candidates end at the median voter, 3.', set: { pre: 'hotel', mode: 'all' }, play: true },
      { t: 'Rock, Paper, Scissors: nothing is ever dominated, so nothing is deleted.', set: { pre: 'rps', mode: 'all' } }
    ],
    steps(z) { const G = parseGame(z.p.txt); return G ? iesdsRun(G, z.p.mode, z.p.order).length : 0; },
    startAtZero: true,
    draw(z) {
      const { g, p } = z;
      const G = sync(z); if (!G) return 'Write a payoff table.';
      const log = iesdsRun(G, p.mode, p.order), shown = log.slice(0, z.step);
      const deadR = new Set(), deadC = new Set();
      shown.forEach(e => { e.rows.forEach(([t]) => deadR.add(t)); e.cols.forEach(([t]) => deadC.add(t)); });
      const o = geom(z, G, 70, 250);
      const last = shown[shown.length - 1];
      drawGame(g, z, G, Object.assign({ deadR, deadC, mark: (r, c) => !deadR.has(r) && !deadC.has(c) && z.step === log.length ? z.col.green : null }, o));
      const lx = o.x + o.cw * G.nc + 26;
      let y = 30;
      D.text(g, 'Deleted so far', lx, y, { s: 12.5, b: true, c: z.col.ink }); y += 20;
      shown.forEach((e, i) => {
        const bits = e.rows.map(([t, by]) => `${G.R[t]} (by ${G.R[by]}, P1)`).concat(e.cols.map(([t, by]) => `${G.C[t]} (by ${G.C[by]}, P2)`));
        bits.forEach(b => { if (y < z.H - 8) { D.text(g, `${p.mode === 'all' ? 'round ' + e.round : 'step ' + (i + 1)}: ${b}`, lx, y, { s: 11.5, c: i === shown.length - 1 ? z.col.red : z.col.ink2, b: i === shown.length - 1 }); y += 17; } });
      });
      if (!log.length) D.text(g, 'nothing is dominated', lx, y, { s: 11.5, c: z.col.ink2 });
      const sr = G.R.filter((_, i) => !deadR.has(i)), sc = G.C.filter((_, i) => !deadC.has(i));
      if (z.step < log.length) return z.step === 0 ? 'Step 0: the full game. Press Step or Play.' : `Deleted ${[...last.rows.map(x => G.R[x[0]]), ...last.cols.map(x => G.C[x[0]])].join(', ')}. ${z.step < log.length ? 'Look again: the smaller game may expose new dominance.' : ''}`;
      return `Done. Surviving rows {${sr.join(', ')}} and columns {${sc.join(', ')}}` + (sr.length === 1 && sc.length === 1 ? `: a unique prediction (${sr[0]}, ${sc[0]}), which is then the unique Nash equilibrium.` : '. More than one profile survives, so IESDS alone cannot pick one.');
    }
  });

  /* ================= 5.3 IESDS in continuous games and auctions ================= */
  def('cournotiesds', {
    title: 'IESDS in the Cournot duopoly: the interval halves',
    sub: 'Round 1 deletes quantities above the monopoly amount. Each later round uses the best reply to the surviving extremes. The square shrinks to one point.',
    W: 560, H: 320,
    params: [
      { k: 'a', label: 'Demand intercept a', type: 'range', v: 100, min: 20, max: 200 },
      { k: 'c', label: 'Unit cost c (both firms)', type: 'range', v: 10, min: 0, max: 60 },
      { k: 'b', label: 'Demand slope b', type: 'range', v: 1, min: 0.5, max: 4, step: 0.5 }
    ],
    tips: [
      { t: 'The class homework: a = 100, c = 10. Intervals [0, 45], [22.5, 45], [22.5, 33.75], … close in on 30.', set: { a: 100, c: 10, b: 1 }, play: true },
      { t: 'Practice E1: a = 130, c = 10. Five rounds give [37.5, 41.25] and the limit is 40.', set: { a: 130, c: 10, b: 1 }, play: true },
      { t: 'Double b. Every quantity halves but the shape of the process stays the same: each round halves the distance to the limit.', set: { b: 2 }, play: true }
    ],
    steps: () => 8,
    startAtZero: true,
    draw(z) {
      const { g, p } = z;
      const BR = q => Math.max(0, (p.a - p.c - p.b * q) / (2 * p.b)), qm = BR(0), qs = (p.a - p.c) / (3 * p.b);
      const iv = [[0, Infinity]];
      let lo = 0, hi = Infinity;
      for (let k = 1; k <= 8; k++) { if (k % 2 === 1) hi = BR(lo); else lo = BR(hi); iv.push([lo, hi]); }
      const [L, H] = iv[z.step], M = qm * 1.25;
      const m = D.axes(g, z, [60, 14, 240, 240], [0, M], [0, M], { nx: 3, ny: 3, xl: 'q₁', yl: 'q₂' });
      const top = Math.min(H, M);
      D.rect(g, m.sx(L), m.sy(top), m.sx(top) - m.sx(L), m.sy(L) - m.sy(top), { fill: z.col.cv + '33', stroke: z.col.cv, w: 1.5 });
      g.save(); g.strokeStyle = z.col.cv; g.lineWidth = 2; g.beginPath();
      for (let i = 0; i <= 60; i++) { const q2 = M * i / 60; const x = m.sx(BR(q2)), y = m.sy(q2); if (i) g.lineTo(x, y); else g.moveTo(x, y); } g.stroke(); g.restore();
      D.curve(g, BR, [0, M], m, z.col.orange, 2);
      D.circle(g, m.sx(qs), m.sy(qs), 6, { fill: z.col.green, stroke: '#fff', w: 2 });
      const lx = 330; let y = 28;
      D.text(g, 'Surviving quantities', lx, y, { s: 12.5, b: true, c: z.col.ink }); y += 20;
      iv.slice(0, z.step + 1).forEach((q, k) => { D.text(g, `round ${k}: [${fmt(q[0], 3)}, ${q[1] === Infinity ? '∞' : fmt(q[1], 3)}]`, lx, y, { s: 11.5, mono: true, c: k === z.step ? z.col.cv : z.col.ink2, b: k === z.step }); y += 17; });
      return `BR(q) = max{0, (a − c − b q) ⁄ 2b}. The monopoly amount ${fmt(qm, 3)} caps round 1. Each new end is BR of the old one, and BR(q) − q* = −½ (q − q*), so the distance to q* = (a − c) ⁄ 3b = <b>${fmt(qs, 3)}</b> halves every round.`;
    }
  });

  def('auction', {
    title: 'Is bidding your true value a dominant strategy?',
    sub: 'Your value v, your bid b, and the highest rival bid B along the bottom. Violet is the payoff from bidding v, orange from bidding b.',
    W: 560, H: 300,
    params: [
      { k: 'kind', label: 'Auction', type: 'select', v: '2', opts: [['2', 'second price (pay the rival bid)'], ['1', 'first price (pay your own bid)']] },
      { k: 'v', label: 'Your value v', type: 'range', v: 60, min: 0, max: 100 },
      { k: 'b', label: 'Alternative bid b', type: 'range', v: 80, min: 0, max: 100 }
    ],
    tips: [
      { t: 'Second price, overbid at 80 with value 60. Between 60 and 80 the overbid wins and loses money. Truthful is never worse.', set: { kind: '2', v: 60, b: 80 } },
      { t: 'Second price, underbid at 40. Between 40 and 60 you lose an auction you would have won with profit. Truthful again never worse.', set: { kind: '2', v: 60, b: 40 } },
      { t: 'First price, underbid at 40. When rivals bid below 40 you win and keep 20, while truthful wins nothing. Truthful is not dominant here, so bidders shade.', set: { kind: '1', v: 60, b: 40 } }
    ],
    draw(z) {
      const { g, p } = z;
      const pay = (bid, B) => bid > B ? p.v - (p.kind === '2' ? B : bid) : 0;
      const m = D.axes(g, z, [70, 16, 440, 210], [0, 100], [-60, 70], { nx: 5, ny: 4, xl: 'highest rival bid B', yl: 'your payoff' });
      D.line(g, m.sx(0), m.sy(0), m.sx(100), m.sy(0), z.col.line, 1);
      D.curve(g, B => pay(p.v, B), [0, 100], m, z.col.cv, 3, 400);
      D.curve(g, B => pay(p.b, B) + 0.8, [0, 100], m, z.col.orange, 2.5, 400, [6, 4]);
      let better = 0, worse = 0;
      for (let B = 0; B <= 100; B += 0.25) { const a = pay(p.v, B), c = pay(p.b, B); if (a > c + 1e-9) better++; if (c > a + 1e-9) worse++; }
      return (p.kind === '2' ? 'Second price: you pay B if you win. ' : 'First price: you pay your own bid if you win. ') +
        (worse === 0 ? (better ? '<b>Bidding v is never worse and sometimes strictly better than b</b>, so it weakly dominates b.' : 'Bidding v and b give the same payoff everywhere.') : '<b>For some rival bids, b beats truthful bidding</b>, so truthful bidding is not weakly dominant against this b.');
    }
  });

  /* ================= 6.1 Quiz 1 ================= */
  def('q1cournot', {
    title: 'Quiz 1, question 1: Cournot with demand p = a ⁄ (q + 1)',
    sub: 'Left: both reaction curves and the true equilibrium against the claimed (a − c) ⁄ 3. Right: joint profit of a monopoly with cost 2cQ.',
    W: 560, H: 310,
    params: [
      { k: 'a', label: 'a', type: 'range', v: 10, min: 0.5, max: 50, step: 0.5 },
      { k: 'c', label: 'c', type: 'range', v: 1, min: 0.1, max: 10, step: 0.1 }
    ],
    tips: [
      { t: 'a = 10, c = 1. The curves cross at about 2.427, not at (a − c) ⁄ 3 = 3. Statement S1 is false.', set: { a: 10, c: 1 } },
      { t: 'The monopoly curve with a = 10, c = 1 peaks at Q = √(a ⁄ 2c) − 1 = 1.236. A maximum exists, so S2 is false here.', set: { a: 10, c: 1 } },
      { t: 'Make a ≤ 2c, for example a = 1.5, c = 1. Joint profit falls from the start, and since Q = 0 is not allowed, no best quantity exists. S2 is true only in this case.', set: { a: 1.5, c: 1 } }
    ],
    draw(z) {
      const { g, p } = z;
      const BR = qj => Math.max(0, Math.sqrt(p.a * (qj + 1) / p.c) - qj - 1);
      const qs = ((p.a - 4 * p.c) + Math.sqrt(p.a * p.a + 8 * p.a * p.c)) / (8 * p.c), claim = (p.a - p.c) / 3;
      const M = Math.max(qs, claim, BR(0), 1) * 1.4;
      const m = D.axes(g, z, [56, 14, 220, 230], [0, M], [0, M], { nx: 3, ny: 3, xl: 'q₁', yl: 'q₂' });
      g.save(); g.strokeStyle = z.col.cv; g.lineWidth = 2.2; g.beginPath();
      for (let i = 0; i <= 80; i++) { const q2 = M * i / 80, x = m.sx(Math.min(M, BR(q2))), y = m.sy(q2); if (i) g.lineTo(x, y); else g.moveTo(x, y); } g.stroke(); g.restore();
      D.curve(g, q1 => BR(q1), [0, M], m, z.col.orange, 2.2);
      D.circle(g, m.sx(qs), m.sy(qs), 6, { fill: z.col.green, stroke: '#fff', w: 2 });
      if (claim > 0 && claim < M) { D.circle(g, m.sx(claim), m.sy(claim), 6, { stroke: z.col.red, w: 2.5 }); D.text(g, 'claimed', m.sx(claim) + 8, m.sy(claim) - 6, { s: 10.5, b: true, c: z.col.red }); }
      const pi = Q => p.a * Q / (Q + 1) - 2 * p.c * Q, Qs = Math.sqrt(p.a / (2 * p.c)) - 1;
      const QM = Math.max(Qs, 1) * 2.5, ys = []; for (let i = 1; i <= 100; i++) ys.push(pi(QM * i / 100));
      const m2 = D.axes(g, z, [336, 14, 200, 230], [0, QM], [Math.min(0, ...ys), Math.max(0.1, ...ys) * 1.15], { nx: 2, ny: 2, xl: 'total Q', yl: 'joint profit' });
      D.curve(g, Q => Q <= 0 ? NaN : pi(Q), [0, QM], m2, z.col.cv, 2.2);
      D.circle(g, m2.sx(0), m2.sy(0), 4, { stroke: z.col.ink2, fill: z.col.surf, w: 1.5 });
      if (Qs > 0) D.circle(g, m2.sx(Qs), m2.sy(pi(Qs)), 6, { fill: z.col.green, stroke: '#fff', w: 2 });
      return `Equilibrium from a(q + 1) = c(2q + 1)²: q* = <b>${fmt(qs, 4)}</b> each, against the claimed ${fmt(claim, 4)}. ` +
        (Qs > 0 ? `The monopoly has a best total Q = √(a ⁄ 2c) − 1 = <b>${fmt(Qs, 4)}</b>, so S2 fails. Both statements are false: option B.` : 'Here a ≤ 2c, profit falls for every Q > 0 and the open end Q → 0 is never reached, so no maximum exists and S2 holds in this special case.');
    }
  });

  def('snacks', {
    title: 'Quiz 1, question 2: bananas, candy and the money you keep',
    sub: 'Each cell is a bundle you can afford. Its number is total value eaten plus money kept. The best cell is green.',
    W: 560, H: 300,
    params: [
      { k: 'cash', label: 'Money in your pocket $', type: 'range', v: 1.25, min: 0.25, max: 3, step: 0.05 },
      { k: 'pb', label: 'Banana price $', type: 'range', v: 0.5, min: 0.05, max: 1.5, step: 0.05 },
      { k: 'pc', label: 'Candy price $', type: 'range', v: 0.25, min: 0.05, max: 1.5, step: 0.05 },
      { k: 'vb', label: 'Value of the first banana $', type: 'range', v: 1.2, min: 0, max: 3, step: 0.05 },
      { k: 'vc', label: 'Value of the first candy $', type: 'range', v: 0.4, min: 0, max: 3, step: 0.05 },
      { k: 'r', label: 'Each extra one is worth this share of the last', type: 'range', v: 0.5, min: 0, max: 1, step: 0.05 }
    ],
    tips: [
      { t: 'The quiz numbers. Two bananas and one candy cost exactly $1.25 and give 1.20 + 0.60 + 0.40 = 2.20. Answer A: yes, spend it all.', set: { cash: 1.25, pb: 0.5, pc: 0.25, vb: 1.2, vc: 0.4, r: 0.5 } },
      { t: 'Make candy worth only $0.20 at first. Now the third quarter is better kept as money, so you stop at two bananas.', set: { vc: 0.2 } },
      { t: 'Give yourself $3. Even so the best plan does not spend it all, because the third banana is worth 0.30 but costs 0.50.', set: { cash: 3, vc: 0.4 } }
    ],
    draw(z) {
      const { g, p } = z;
      const val = (n, v0) => { let s = 0, v = v0; for (let i = 0; i < n; i++) { s += v; v *= p.r; } return s; };
      const NB = Math.floor(p.cash / p.pb + 1e-9), NC = Math.floor(p.cash / p.pc + 1e-9);
      const nbS = Math.min(NB, 6), ncS = Math.min(NC, 10);
      let best = null;
      const cw = Math.min(46, 420 / (ncS + 1)), ch = Math.min(30, 220 / (nbS + 1)), x0 = 90, y0 = 40;
      D.text(g, 'candies →', x0, 24, { s: 11.5, b: true, c: z.col.ink2 });
      D.text(g, 'bananas ↓', x0 - 10, y0 - 4, { a: 'right', s: 11.5, b: true, c: z.col.ink2 });
      const cells = [];
      for (let b = 0; b <= nbS; b++) for (let c = 0; c <= ncS; c++) {
        const cost = b * p.pb + c * p.pc; if (cost > p.cash + 1e-9) continue;
        const tot = val(b, p.vb) + val(c, p.vc) + (p.cash - cost);
        cells.push({ b, c, tot, cost });
        if (!best || tot > best.tot + 1e-12) best = { b, c, tot, cost };
      }
      for (let c = 0; c <= ncS; c++) D.text(g, String(c), x0 + c * cw + cw / 2, y0 - 4, { a: 'center', s: 11, c: z.col.ink2 });
      for (let b = 0; b <= nbS; b++) D.text(g, String(b), x0 - 10, y0 + b * ch + ch / 2 + 4, { a: 'right', s: 11, c: z.col.ink2 });
      cells.forEach(q => {
        const hot = q.b === best.b && q.c === best.c;
        D.rect(g, x0 + q.c * cw, y0 + q.b * ch, cw - 2, ch - 2, { fill: hot ? z.col.green : z.col.bg, stroke: z.col.line, w: 1 });
        D.text(g, fmt(q.tot, 2), x0 + q.c * cw + cw / 2 - 1, y0 + q.b * ch + ch / 2 + 3, { a: 'center', s: Math.min(11, cw / 3.6), b: true, mono: true, c: hot ? '#fff' : z.col.ink });
      });
      const spendAll = Math.abs(best.cost - p.cash) < 1e-9;
      return `Best: <b>${best.b} banana${best.b === 1 ? '' : 's'} and ${best.c} cand${best.c === 1 ? 'y' : 'ies'}</b>, spending $${fmt(best.cost, 2)} of $${fmt(p.cash, 2)} for a total of ${fmt(best.tot, 2)} (doing nothing gives ${fmt(p.cash, 2)}). ${spendAll ? 'You spend all your money.' : 'You keep some money, because the next item is worth less than its price.'} Buy an item only while its marginal value is at least its price.`;
    }
  });

  def('buylottery', {
    title: 'Quiz 1, question 3: when does a √w agent buy the lottery?',
    sub: 'The violet curve is expected utility after buying at price p. The orange line is utility of not buying. Buy while violet is above orange.',
    W: 560, H: 300,
    params: [
      { k: 'w', label: 'Current wealth', type: 'range', v: 400, min: 0, max: 2000, step: 10 },
      { k: 'hi', label: 'High prize', type: 'range', v: 900, min: 0, max: 3000, step: 10 },
      { k: 'lo', label: 'Low prize', type: 'range', v: 10, min: 0, max: 500, step: 5 },
      { k: 'q', label: 'P(high prize)', type: 'range', v: 0.4, min: 0, max: 1, step: 0.05 },
      { k: 'u', label: 'Utility', type: 'select', v: 'sqrt', opts: [['sqrt', 'u(w) = √w'], ['ln', 'u(w) = ln w'], ['lin', 'u(w) = w']] },
      { k: 'p', label: 'Price p', type: 'range', v: 18, min: 0, max: 600 }
    ],
    tips: [
      { t: 'The quiz numbers. Buying is worth it up to a price of about 268, so at p = 18 or below the agent certainly buys. Options A and B both hold.', set: { w: 400, hi: 900, lo: 10, q: 0.4, u: 'sqrt', p: 18 } },
      { t: 'Ignore wealth by setting it to 0. Then the lottery alone is worth E[√X] = 13.9, a certainty equivalent of about 193.', set: { w: 0, p: 18 } },
      { t: 'Switch to u(w) = w, risk neutral. The break even price is exactly the expected prize 0.4 × 900 + 0.6 × 10 = 366.', set: { w: 400, u: 'lin' } }
    ],
    draw(z) {
      const { g, p } = z;
      const U = { sqrt: x => Math.sqrt(Math.max(0, x)), ln: x => x > 0 ? Math.log(x) : -Infinity, lin: x => x }[p.u];
      const EU = pr => p.q * U(p.w - pr + p.hi) + (1 - p.q) * U(p.w - pr + p.lo);
      const base = U(p.w);
      const top = p.w + p.lo + 0.999 * (p.hi - p.lo + 1);
      let a = 0, b = Math.max(1, p.w + p.lo + (p.q > 0 ? p.hi : 0));
      if (EU(0) < base) b = 0;
      for (let i = 0; i < 80; i++) { const mdl = (a + b) / 2; if (EU(mdl) >= base) a = mdl; else b = mdl; }
      const ps = a, PM = Math.max(ps * 1.5, p.p * 1.2, 50);
      void top;
      const vals = [EU(0), base, EU(Math.min(PM, p.w + p.lo))].filter(isFinite);
      const m = D.axes(g, z, [70, 16, 440, 210], [0, PM], [Math.min(...vals) - 1, Math.max(...vals) + 1], { nx: 4, ny: 4, xl: 'price p', yl: 'utility' });
      D.curve(g, EU, [0, PM], m, z.col.cv, 2.5);
      D.line(g, m.sx(0), m.sy(base), m.sx(PM), m.sy(base), z.col.orange, 2, [6, 4]);
      if (ps > 0 && ps < PM) { D.line(g, m.sx(ps), 16, m.sx(ps), 226, z.col.green, 1.5, [3, 3]); D.text(g, 'p* ≈ ' + fmt(ps, 1), m.sx(ps) + 4, 30, { s: 11.5, b: true, c: z.col.green }); }
      const here = EU(p.p);
      D.circle(g, m.sx(Math.min(p.p, PM)), m.sy(here), 6, { fill: here >= base ? z.col.green : z.col.red, stroke: '#fff', w: 2 });
      return `At p = ${p.p}: E[u] after buying = ${fmt(here, 3)}, u(${p.w}) = ${fmt(base, 3)}. ${here >= base ? '<b>Buy.</b>' : '<b>Do not buy.</b>'} The break even price is p* ≈ <b>${fmt(ps, 2)}</b>, so the agent buys for every price below it.`;
    }
  });
})();
