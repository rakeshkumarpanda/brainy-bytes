/* ===== Core AI animations, part 1: agents, search, local search, constraint satisfaction and games.
   Every Core AI animation is a step by step trace. It starts empty. Each press of Step adds one piece of the
   picture and explains that piece in plain words under it, until the picture is complete. Play runs the steps,
   Back undoes one, and Reset puts every value back to how the page first showed it.

   CAI.trace(name, spec) wraps CVZ.def (assets/cvviz.js):
     spec.frames(p) -> [ { say: 'what happens in this step', ...anything paint needs } ]
                       worked out again whenever a value changes, so the reader's own input is always traced
     spec.paint(z, frame, frames, index)   draws one frame on z.g
   Part 2 (logic, planning, probability, reinforcement learning) is in assets/coreai2.js. Helpers come from AIZ
   (assets/aiwidgets.js). ===== */
const CAI = (() => {
  const { D, def } = CVZ;
  const { tag, wrap, rr, fmt, tw, fit, layoutTree } = AIZ;
  const esc = CVZ.esc;
  const MAXF = 220;

  function blank(z) {
    D.text(z.g, 'Press Step to begin. The picture builds up one step at a time.', z.W / 2, z.H / 2, { a: 'center', s: 14, c: z.col.ink2 });
  }
  function trace(name, spec) {
    def(name, {
      title: spec.title, sub: spec.sub, W: spec.W || 600, H: spec.H || 340, params: spec.params || [], tips: spec.tips || [],
      startAtZero: true, init: spec.init, change: spec.change,
      speed: () => spec.speed || 1100,
      steps(z) {
        try { z.state.fr = spec.frames(z.p, z); z.state.err = ''; } catch (e) { z.state.fr = []; z.state.err = e.message; }
        if (z.state.fr.length > MAXF) z.state.fr = z.state.fr.slice(0, MAXF).concat([{ ...z.state.fr[MAXF - 1], say: `The trace is long, so it stops here after ${MAXF} steps. Try a smaller input.`, cut: true }]);
        return z.state.fr.length;
      },
      draw(z) {
        const fr = z.state.fr || [];
        if (z.state.err) { D.text(z.g, 'Please check the input.', z.W / 2, z.H / 2, { a: 'center', s: 14, c: z.col.red }); return `<p class="cai-now"><b class="k">Input problem.</b> ${esc(z.state.err)}</p>`; }
        if (!z.step) { blank(z); return '<p class="cai-now cai-start">Nothing is shown yet. Press <b>Step</b> to see the first step, or <b>Play</b> to watch every step. Each step adds one new piece and explains it here.</p>'; }
        const f = fr[z.step - 1];
        spec.paint(z, f, fr, z.step - 1);
        const log = fr.slice(0, z.step - 1).map(x => `<li>${x.say}</li>`).join('');
        return `<div class="cai-now"><b class="k">Step ${z.step} of ${fr.length}.</b> ${f.say}</div>` + (f.extra || '') +
          (z.step > 1 ? `<details class="cai-log"><summary>Earlier steps (${z.step - 1})</summary><ol>${log}</ol></details>` : '');
      }
    });
  }
  /* a node of a graph or tree. kind: idle, frontier, cur, done, path, bad */
  function node(z, x, y, label, kind = 'idle', o = {}) {
    const r = o.r || 9, c = z.col;
    const fill = { idle: c.surf, frontier: c.surf, cur: c.cv, done: c.ink2, path: c.green, bad: c.red, goal: c.surf }[kind] || c.surf;
    const stroke = { idle: c.line, frontier: c.orange, cur: c.cv, done: c.ink2, path: c.green, bad: c.red, goal: c.green }[kind] || c.line;
    D.circle(z.g, x, y, r, { fill, stroke, w: kind === 'frontier' || kind === 'goal' ? 3 : 1.6 });
    if (o.inside) D.text(z.g, o.inside, x, y + 1, { a: 'center', bl: 'middle', s: o.is || 11, b: true, c: ['cur', 'done', 'path', 'bad'].includes(kind) ? '#fff' : c.ink });
    if (label) D.text(z.g, label, x + (o.dx || 0), y + (o.dy ?? -r - 5), { a: o.a || 'center', s: o.s || 11, b: kind === 'cur' || kind === 'path', c: kind === 'cur' ? c.cv : c.ink });
  }
  const COL = { R: '#ef4444', G: '#22c55e', B: '#3b82f6', Y: '#eab308' };
  const COLNAME = { R: 'red', G: 'green', B: 'blue', Y: 'yellow' };
  const list = s => String(s).split(/[\s,]+/).map(x => x.trim()).filter(Boolean);
  const nums = s => list(String(s).replace(/−/g, '-')).map(Number).filter(v => !isNaN(v));

  /* =====================================================================================================
     1.1  The vacuum world agent
     ===================================================================================================== */
  trace('vacuum', {
    title: 'An agent in the two square vacuum world',
    sub: 'Each step the agent senses (a percept), picks an action with its agent program, and acts. Watch the score.',
    W: 600, H: 250,
    params: [
      { k: 'agent', label: 'Agent program', type: 'select', v: 'reflex', opts: [['reflex', 'Simple reflex agent'], ['model', 'Model based reflex agent'], ['table', 'Table driven agent (looks up the whole percept history)']] },
      { k: 'start', label: 'Agent starts in', type: 'select', v: 'A', opts: [['A', 'Square A'], ['B', 'Square B']] },
      { k: 'da', label: 'Square A is dirty at the start', type: 'check', v: true },
      { k: 'db', label: 'Square B is dirty at the start', type: 'check', v: true },
      { k: 'T', label: 'Time steps to run', type: 'range', v: 6, min: 1, max: 10 },
      { k: 'mc', label: 'Each move costs 1 point', type: 'check', v: false }
    ],
    tips: [
      { t: 'Simple reflex agent, both squares dirty. It cleans both in 3 steps, then keeps moving left and right for ever because it cannot remember that the job is done.', set: { agent: 'reflex', da: true, db: true, mc: false }, play: true },
      { t: 'Tick "each move costs 1 point". The reflex agent now loses points after the work is done. Switch to the model based agent, which stops (NoOp) once its model says both squares are clean.', set: { mc: true, agent: 'model' }, play: true },
      { t: 'Table driven agent. It acts the same as the reflex agent here, but its table needs one row for every possible percept history: 4 + 16 + 64 + ... rows. That is why nobody builds agents this way.', set: { agent: 'table' } }
    ],
    frames(p) {
      const fr = [];
      let loc = p.start, dirt = { A: !!p.da, B: !!p.db }, score = 0;
      const model = { A: null, B: null };
      fr.push({ loc, dirt: { ...dirt }, score, t: 0, act: '', per: '', say: `The world has two squares, A and B. The agent starts in ${loc}. A is ${dirt.A ? 'dirty' : 'clean'} and B is ${dirt.B ? 'dirty' : 'clean'}. The score rises by 1 for every clean square after each time step${p.mc ? ', and falls by 1 for every move' : ''}.` });
      let rows = 0;
      for (let t = 1; t <= p.T; t++) {
        const per = `[${loc}, ${dirt[loc] ? 'Dirty' : 'Clean'}]`;
        model[loc] = dirt[loc] ? 'Dirty' : 'Clean';
        let act, why;
        rows += Math.pow(4, t);
        if (dirt[loc]) { act = 'Suck'; why = 'the rule "if the square is dirty then Suck" fires'; }
        else if (p.agent === 'model' && model.A === 'Clean' && model.B === 'Clean') { act = 'NoOp'; why = 'its internal model says both squares are already clean, so there is nothing to do'; }
        else { act = loc === 'A' ? 'Right' : 'Left'; why = `the square is clean, so the rule "if in ${loc} and clean then go ${loc === 'A' ? 'Right' : 'Left'}" fires`; }
        if (p.agent === 'table') why = `it looks up the whole percept history (${t} percept${t > 1 ? 's' : ''}) in a table that needs ${rows} rows so far`;
        let moved = false;
        if (act === 'Suck') { dirt[loc] = false; model[loc] = 'Clean'; }
        else if (act === 'Right') { loc = 'B'; moved = true; } else if (act === 'Left') { loc = 'A'; moved = true; }
        const gain = (dirt.A ? 0 : 1) + (dirt.B ? 0 : 1) - (moved && p.mc ? 1 : 0);
        score += gain;
        fr.push({ loc, dirt: { ...dirt }, score, t, act, per, model: { ...model }, say: `Time ${t}. The percept is ${per}. The agent chooses <b>${act}</b> because ${why}. Score change ${gain >= 0 ? '+' : ''}${gain}, total <b>${score}</b>.` });
      }
      fr.push({ ...fr[fr.length - 1], say: `Done after ${p.T} steps with a score of <b>${score}</b>. ${p.agent === 'model' ? 'The model based agent remembers what it has seen, so it can stop when the work is finished.' : 'A simple reflex agent only sees the current square, so it cannot know when both squares are clean.'}` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      ['A', 'B'].forEach((s, i) => {
        const x = 70 + i * 240, y = 40;
        rr(g, x, y, 220, 130, 12, { fill: c.bg, stroke: c.line });
        D.text(g, 'Square ' + s, x + 110, y + 22, { a: 'center', s: 14, b: true, c: c.ink });
        if (f.dirt[s]) for (let k = 0; k < 7; k++) D.circle(g, x + 30 + (k * 37) % 160, y + 70 + (k * 23) % 45, 5, { fill: '#92400e' });
        D.text(g, f.dirt[s] ? 'dirty' : 'clean', x + 110, y + 122, { a: 'center', s: 12, c: f.dirt[s] ? '#92400e' : c.green, b: true });
        if (f.loc === s) { D.circle(g, x + 110, y + 75, 24, { fill: c.cv, stroke: c.surf, w: 3 }); D.text(g, 'agent', x + 110, y + 76, { a: 'center', bl: 'middle', s: 11, b: true, c: '#fff' }); }
      });
      D.text(g, `time ${f.t}`, 20, 205, { s: 13, b: true, c: c.ink2 });
      if (f.per) tag(g, 'percept ' + f.per, 200, 205, { s: 12, fill: c.surf, stroke: c.line, c: c.ink });
      if (f.act) tag(g, 'action ' + f.act, 360, 205, { s: 12, fill: c.cv, stroke: c.cv, c: '#fff' });
      tag(g, 'score ' + f.score, 510, 205, { s: 12, fill: c.yellow, stroke: c.yellow, c: '#1f1300' });
    }
  });

  /* =====================================================================================================
     Graph search: one widget for BFS, DFS, depth limited, iterative deepening, uniform cost, greedy and A*
     ===================================================================================================== */
  const RO = {
    Arad: [91, 492], Zerind: [108, 531], Oradea: [131, 571], Sibiu: [207, 457], Timisoara: [94, 410], Lugoj: [165, 379], Mehadia: [168, 339],
    Dobreta: [165, 299], Craiova: [253, 288], 'Rimnicu Vilcea': [233, 410], Fagaras: [305, 449], Pitesti: [320, 368], Bucharest: [400, 327],
    Giurgiu: [375, 270], Urziceni: [456, 350], Hirsova: [534, 350], Eforie: [562, 293], Vaslui: [509, 444], Iasi: [473, 506], Neamt: [406, 537]
  };
  /* neighbours in the order the slides list them (Arad: Zerind, Timisoara, Sibiu, and Sibiu: Arad, Oradea, Fagaras, Rimnicu Vilcea) */
  const ROADJ = {
    Arad: [['Zerind', 75], ['Timisoara', 118], ['Sibiu', 140]], Zerind: [['Arad', 75], ['Oradea', 71]], Oradea: [['Zerind', 71], ['Sibiu', 151]],
    Sibiu: [['Arad', 140], ['Oradea', 151], ['Fagaras', 99], ['Rimnicu Vilcea', 80]], Timisoara: [['Arad', 118], ['Lugoj', 111]],
    Lugoj: [['Timisoara', 111], ['Mehadia', 70]], Mehadia: [['Lugoj', 70], ['Dobreta', 75]], Dobreta: [['Mehadia', 75], ['Craiova', 120]],
    Craiova: [['Dobreta', 120], ['Rimnicu Vilcea', 146], ['Pitesti', 138]], 'Rimnicu Vilcea': [['Sibiu', 80], ['Craiova', 146], ['Pitesti', 97]],
    Fagaras: [['Sibiu', 99], ['Bucharest', 211]], Pitesti: [['Rimnicu Vilcea', 97], ['Craiova', 138], ['Bucharest', 101]],
    Bucharest: [['Fagaras', 211], ['Pitesti', 101], ['Giurgiu', 90], ['Urziceni', 85]], Giurgiu: [['Bucharest', 90]],
    Urziceni: [['Bucharest', 85], ['Hirsova', 98], ['Vaslui', 142]], Hirsova: [['Urziceni', 98], ['Eforie', 86]], Eforie: [['Hirsova', 86]],
    Vaslui: [['Urziceni', 142], ['Iasi', 92]], Iasi: [['Vaslui', 92], ['Neamt', 87]], Neamt: [['Iasi', 87]]
  };
  const SLD = { Arad: 366, Bucharest: 0, Craiova: 160, Dobreta: 242, Eforie: 161, Fagaras: 176, Giurgiu: 77, Hirsova: 151, Iasi: 226, Lugoj: 244,
    Mehadia: 241, Neamt: 234, Oradea: 380, Pitesti: 100, 'Rimnicu Vilcea': 193, Sibiu: 253, Timisoara: 329, Urziceni: 80, Vaslui: 199, Zerind: 374 };
  const ROSHORT = { 'Rimnicu Vilcea': 'Rimnicu V.' };
  const RODY = { Oradea: -12, Zerind: -12, Arad: -12, Timisoara: 18, Lugoj: -12, Mehadia: -12, Dobreta: 18, Craiova: 18, Giurgiu: 18, Eforie: 18, Hirsova: -12, Urziceni: 18, Bucharest: 18, Pitesti: -12, Fagaras: -12, Sibiu: -12, 'Rimnicu Vilcea': 18, Vaslui: -12, Iasi: -12, Neamt: -12 };

  function romania(W, H) {
    const nodes = Object.keys(RO).map(id => ({ id, x: 36 + (RO[id][0] - 91) / (562 - 91) * (W - 90), y: 28 + (571 - RO[id][1]) / (571 - 270) * (H - 70), lab: ROSHORT[id] || id, dy: RODY[id] || -12 }));
    return { nodes, adj: ROADJ, h: goal => goal === 'Bucharest' ? SLD : null, costs: true };
  }
  function treeGraph(W, H, depth = 3) {
    const L = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    const nodes = [], adj = {};
    const n = Math.pow(2, depth + 1) - 1;
    for (let i = 0; i < n; i++) {
      const d = Math.floor(Math.log2(i + 1)), k = i + 1 - Math.pow(2, d), span = Math.pow(2, d);
      nodes.push({ id: L[i], x: 30 + (W - 60) * (k + 0.5) / span, y: 30 + d * (H - 80) / depth, lab: '', inside: L[i] });
      adj[L[i]] = [];
      if (i) { const par = L[Math.floor((i - 1) / 2)]; adj[par].push([L[i], 1]); }
    }
    return { nodes, adj, h: () => null, costs: false, directed: true, big: true };
  }
  function trapGraph(W, H) {
    const pos = { S: [60, 170], n1: [200, 70], n2: [360, 70], Goal: [520, 170], n3: [300, 270] };
    const nodes = Object.keys(pos).map(id => ({ id, x: pos[id][0] * W / 600, y: pos[id][1] * H / 340, lab: id, dy: id === 'n3' ? 24 : -16 }));
    const adj = { S: [['n1', 10], ['n3', 100]], n1: [['S', 10], ['n2', 10]], n2: [['n1', 10], ['Goal', 10]], n3: [['S', 100], ['Goal', 10]], Goal: [['n2', 10], ['n3', 10]] };
    return { nodes, adj, h: () => ({ S: 30, n1: 20, n2: 10, n3: 10, Goal: 0 }), costs: true };
  }
  function jugGraph(W, H, A, B, want) {
    const key = (a, b) => `(${a},${b})`;
    const adj = {}, depth = {}, order = [];
    const q = [[0, 0]];
    depth[key(0, 0)] = 0;
    while (q.length) {
      const [a, b] = q.shift(), k = key(a, b);
      order.push(k);
      const pa = Math.min(a, B - b), pb = Math.min(b, A - a);
      const nx = [[A, b, 'Fill ' + A], [a, B, 'Fill ' + B], [0, b, 'Empty ' + A], [a, 0, 'Empty ' + B], [a - pa, b + pa, `Pour ${A} into ${B}`], [a + pb, b - pb, `Pour ${B} into ${A}`]];
      adj[k] = [];
      nx.forEach(([x, y, act]) => {
        const kk = key(x, y);
        if (kk === k || adj[k].some(e => e[0] === kk)) return;
        adj[k].push([kk, 1, act]);
        if (depth[kk] === undefined) { depth[kk] = depth[k] + 1; q.push([x, y]); }
      });
    }
    const byD = {};
    order.forEach(k => (byD[depth[k]] = byD[depth[k]] || []).push(k));
    const maxD = Math.max(...Object.keys(byD).map(Number));
    const nodes = [];
    Object.keys(byD).forEach(d => byD[d].forEach((k, i) => nodes.push({ id: k, x: 40 + (W - 80) * (+d) / Math.max(1, maxD), y: 30 + (H - 70) * (i + 0.5) / byD[d].length, lab: k, dy: -12 })));
    return { nodes, adj, h: () => null, costs: false, isGoal: s => { const m = s.match(/\((\d+),(\d+)\)/); return +m[1] === want || +m[2] === want; } };
  }
  function customGraph(W, H, edges, hs) {
    const adj = {}, ids = [];
    const add = id => { if (!adj[id]) { adj[id] = []; ids.push(id); } };
    String(edges).split('\n').map(l => l.trim()).filter(Boolean).forEach(l => {
      const t = l.split(/[\s,]+/);
      if (t.length < 2) return;
      const c = t[2] !== undefined ? +t[2] : 1;
      if (isNaN(c) || c <= 0) throw new Error(`The cost in "${l}" must be a positive number.`);
      add(t[0]); add(t[1]);
      adj[t[0]].push([t[1], c]); adj[t[1]].push([t[0], c]);
    });
    if (!ids.length) throw new Error('Write one road per line, for example: S A 4');
    if (ids.length > 16) throw new Error('Please keep the graph to 16 places or fewer so the picture stays readable.');
    const h = {};
    String(hs).split('\n').map(l => l.trim()).filter(Boolean).forEach(l => { const t = l.split(/[\s,]+/); if (t.length >= 2 && !isNaN(+t[1])) h[t[0]] = +t[1]; });
    const nodes = ids.map((id, i) => { const a = -Math.PI / 2 + 2 * Math.PI * i / ids.length; return { id, x: W / 2 + Math.cos(a) * (W / 2 - 60), y: H / 2 - 10 + Math.sin(a) * (H / 2 - 45), lab: id, dy: Math.sin(a) > 0.3 ? 20 : -14 }; });
    return { nodes, adj, h: () => h, costs: true };
  }
  function findId(G, s) {
    const t = String(s).trim().toLowerCase();
    const ids = G.nodes.map(n => n.id);
    return ids.find(i => i.toLowerCase() === t) || ids.find(i => i.toLowerCase().startsWith(t) && t);
  }
  const ALGN = { bfs: 'breadth first search', dfs: 'depth first search', dls: 'depth limited search', ids: 'iterative deepening search', ucs: 'uniform cost search', greedy: 'greedy best first search', astar: 'A* search' };

  function runSearch(G, alg, start, isGoal, H, lim) {
    const fr = [], h = s => (H && H[s] !== undefined ? H[s] : 0);
    const nm = s => `<b>${esc(s)}</b>`;
    const show = (o) => fr.push(o);
    const pathOf = n => { const p = []; for (let x = n; x; x = x.par) p.unshift(x.s); return p; };
    const tbl = (front, key) => '<table class="cai-tb"><tr><th>frontier</th><th>g (cost so far)</th>' + (H ? '<th>h (estimate)</th><th>f = g + h</th>' : '') + '</tr>' +
      front.map((n, i) => `<tr class="${i === 0 ? 'on' : ''}"><td>${esc(n.s)}</td><td>${n.g}</td>${H ? `<td>${h(n.s)}</td><td>${n.g + h(n.s)}</td>` : ''}</tr>`).join('') + '</table>';
    const snap = (cur, front, explored, tree, say, extra = {}) => show(Object.assign({ cur, front: front.map(n => n.s), explored: [...explored], tree: tree.slice(), say }, extra));
    const tree = [];
    if (alg === 'dls' || alg === 'ids') {
      const limits = alg === 'dls' ? [lim] : Array.from({ length: lim + 1 }, (_, i) => i);
      let found = null;
      for (const L of limits) {
        const seen = [];
        const tr = [];
        snap(null, [], [], [], alg === 'ids' ? `Iteration with depth limit <b>${L}</b>. Start again from ${nm(start)} with an empty tree. Nodes deeper than ${L} are cut off.` : `Depth limited search with limit <b>${L}</b>. Run depth first search, but never go deeper than ${L}.`, { limit: L });
        let cut = false;
        const rec = (n, d) => {
          if (found) return;
          seen.push(n.s);
          if (isGoal(n.s)) { found = n; snap(n.s, [], seen, tr, `Visit ${nm(n.s)} at depth ${d}. It is the goal. Path: ${pathOf(n).map(esc).join(' → ')}, cost ${n.g}.`, { sol: pathOf(n), limit: L }); return; }
          if (d === L) { cut = cut || (G.adj[n.s] || []).some(([c]) => !pathOf(n).includes(c)); snap(n.s, [], seen, tr, `Visit ${nm(n.s)} at depth ${d}. Not the goal, and depth ${d} is the limit, so its children are cut off.`, { limit: L }); return; }
          snap(n.s, [], seen, tr, `Visit ${nm(n.s)} at depth ${d}. Not the goal, so go down to its first child.`, { limit: L });
          for (const [c, cost] of (G.adj[n.s] || [])) {
            if (pathOf(n).includes(c)) continue;
            tr.push([n.s, c]);
            rec({ s: c, par: n, g: n.g + cost }, d + 1);
            if (found) return;
          }
        };
        rec({ s: start, par: null, g: 0 }, 0);
        if (found) break;
        if (!cut) { snap(null, [], seen, tr, `Nothing was cut off and no goal was found, so there is no solution at any depth.`, { limit: L }); return fr; }
        snap(null, [], seen, tr, `No goal within depth ${L}. ${alg === 'ids' ? `Some nodes were cut off, so raise the limit to ${L + 1} and start again.` : 'Some nodes were cut off, so a goal may exist deeper. Depth limited search reports a cutoff.'}`, { limit: L });
      }
      return fr;
    }
    let front = [{ s: start, par: null, g: 0 }];
    const explored = new Set();
    const pri = n => alg === 'ucs' ? n.g : alg === 'greedy' ? h(n.s) : n.g + h(n.s);
    const order = () => { if (['ucs', 'greedy', 'astar'].includes(alg)) front.sort((a, b) => pri(a) - pri(b) || a.t - b.t); };
    let tick = 0;
    front[0].t = tick++;
    snap(null, front, explored, tree, `Put the start ${nm(start)} in the frontier. The frontier holds the paths we know about but have not expanded yet. ${alg === 'bfs' ? 'Breadth first keeps it as a FIFO queue.' : alg === 'dfs' ? 'Depth first keeps it as a LIFO stack.' : alg === 'ucs' ? 'Uniform cost orders it by g, the path cost so far.' : alg === 'greedy' ? 'Greedy best first orders it by h, the estimated distance to the goal.' : 'A* orders it by f = g + h.'}`, { extra: tbl(front) });
    if (alg === 'bfs' && isGoal(start)) { snap(start, [], [], tree, 'The start is already the goal.', { sol: [start] }); return fr; }
    while (front.length) {
      const n = alg === 'dfs' ? front.pop() : front.shift();
      if (alg === 'dfs' && explored.has(n.s)) continue;
      if (alg !== 'bfs' && isGoal(n.s)) {
        const p = pathOf(n);
        snap(n.s, front, explored, tree, `Take ${nm(n.s)} out of the frontier${alg === 'dfs' ? ' (the top of the stack)' : ` (lowest ${alg === 'greedy' ? 'h' : alg === 'ucs' ? 'g' : 'f'})`}. It passes the goal test. Solution: ${p.map(esc).join(' → ')}, total cost <b>${n.g}</b>.${alg === 'ucs' || alg === 'astar' ? ' Testing the goal when a node is taken out, not when it is added, is what makes this cost the cheapest.' : ''}`, { sol: p });
        return fr;
      }
      explored.add(n.s);
      const added = [], skipped = [], better = [];
      const kids = (G.adj[n.s] || []).slice();
      if (alg === 'dfs') kids.reverse();
      for (const [c, cost] of kids) {
        const g = n.g + cost;
        const inF = front.find(x => x.s === c);
        if (explored.has(c)) { skipped.push(c); continue; }
        if (inF && alg !== 'dfs') {
          if ((alg === 'ucs' || alg === 'astar') && g < inF.g) { inF.g = g; inF.par = n; better.push(c); const k = tree.findIndex(e => e[1] === c); if (k >= 0) tree[k] = [n.s, c]; }
          else skipped.push(c);
          continue;
        }
        if (inF && alg === 'dfs') front = front.filter(x => x.s !== c);
        const ch = { s: c, par: n, g, t: tick++ };
        tree.push([n.s, c]);
        if (alg === 'bfs' && isGoal(c)) {
          const p = pathOf(ch);
          snap(n.s, front, explored, tree, `Expand ${nm(n.s)}. Its child ${nm(c)} is the goal. Breadth first tests a node as soon as it is generated, so it stops here. Solution: ${p.map(esc).join(' → ')}, cost <b>${g}</b>. It has the fewest steps, but not always the lowest cost.`, { sol: p });
          return fr;
        }
        front.push(ch);
        added.push(c);
      }
      order();
      const shown = alg === 'dfs' ? front.slice().reverse() : front;
      const add = added.length ? `Add ${added.map(esc).join(', ')} to the frontier.` : 'No new children to add.';
      const sk = skipped.length ? ` Skip ${skipped.map(esc).join(', ')}, already explored or already waiting in the frontier.` : '';
      const bt = better.length ? ` Found a cheaper path to ${better.map(esc).join(', ')}, so its entry in the frontier is replaced.` : '';
      snap(n.s, shown, explored, tree, `Take ${nm(n.s)} out of the frontier${alg === 'dfs' ? ' (top of the stack)' : alg === 'bfs' ? ' (front of the queue)' : ` (lowest ${alg === 'greedy' ? 'h' : alg === 'ucs' ? 'g' : 'f'})`}${alg !== 'bfs' ? ', it is not the goal,' : ''} and expand it. ${add}${sk}${bt}`, { extra: tbl(shown) });
    }
    snap(null, [], explored, tree, 'The frontier is empty, so there is no path to the goal.');
    return fr;
  }

  trace('searchgraph', {
    title: 'Graph search, one step at a time',
    sub: 'Orange ring: in the frontier. Violet: being expanded now. Grey: explored. Green: the solution path.',
    W: 620, H: 400,
    params: [
      { k: 'alg', label: 'Algorithm', type: 'select', v: 'bfs', opts: Object.keys(ALGN).map(k => [k, ALGN[k][0].toUpperCase() + ALGN[k].slice(1)]) },
      { k: 'gr', label: 'Problem', type: 'select', v: 'romania', opts: [['romania', 'Romania road map (slides)'], ['tree', 'Binary tree A to O (slides)'], ['trap', 'Greedy trap (slide 58)'], ['jugs', 'Water jugs'], ['custom', 'My own graph']] },
      { k: 'start', label: 'Start', type: 'text', v: 'Arad', show: p => p.gr !== 'jugs' },
      { k: 'goal', label: 'Goal', type: 'text', v: 'Bucharest', show: p => p.gr !== 'jugs' },
      { k: 'lim', label: 'Depth limit (depth limited) or largest limit (iterative deepening)', type: 'range', v: 3, min: 0, max: 8, show: p => p.alg === 'dls' || p.alg === 'ids' },
      { k: 'ja', label: 'Jug A holds', type: 'range', v: 3, min: 1, max: 9, show: p => p.gr === 'jugs' },
      { k: 'jb', label: 'Jug B holds', type: 'range', v: 4, min: 1, max: 9, show: p => p.gr === 'jugs' },
      { k: 'jw', label: 'Goal: either jug holds exactly', type: 'range', v: 2, min: 0, max: 9, show: p => p.gr === 'jugs' },
      { k: 'edges', label: 'Roads, one per line: from to cost', type: 'area', v: 'S A 1\nS B 4\nA B 2\nA C 5\nB C 1\nC G 3', show: p => p.gr === 'custom' },
      { k: 'hs', label: 'Heuristic h, one per line: place value', type: 'area', v: 'S 6\nA 5\nB 3\nC 2\nG 0', show: p => p.gr === 'custom' }
    ],
    tips: [
      { t: 'BFS from Arad to Bucharest. It finds Arad, Sibiu, Fagaras, Bucharest with cost 450, the path with the fewest roads, exactly as on the slides.', set: { alg: 'bfs', gr: 'romania', start: 'Arad', goal: 'Bucharest' }, play: true },
      { t: 'Switch to uniform cost search. It keeps going after it first sees Bucharest (450) and finds the cheaper route through Rimnicu Vilcea and Pitesti, 418.', set: { alg: 'ucs', gr: 'romania', start: 'Arad', goal: 'Bucharest' }, play: true },
      { t: 'Try A*. It reaches the same 418 but expands far fewer cities, because h pulls it toward Bucharest.', set: { alg: 'astar', gr: 'romania', start: 'Arad', goal: 'Bucharest' }, play: true },
      { t: 'Greedy best first on Romania: fast but it returns 450, not 418.', set: { alg: 'greedy', gr: 'romania', start: 'Arad', goal: 'Bucharest' }, play: true },
      { t: 'The greedy trap from slide 58. Greedy runs to n3 because h(n3) = 10 looks close, and pays 110. A* pays 30.', set: { alg: 'greedy', gr: 'trap', start: 'S', goal: 'Goal' }, play: true },
      { t: 'Depth first on the slide tree with goal M. Watch it dive down the left side first: A B D H I E J K C F L M.', set: { alg: 'dfs', gr: 'tree', start: 'A', goal: 'M' }, play: true },
      { t: 'Iterative deepening on the same tree. Each iteration starts again from A with a bigger limit, and M is found at limit 3.', set: { alg: 'ids', gr: 'tree', start: 'A', goal: 'M', lim: 3 }, play: true },
      { t: 'The water jug puzzle with jugs of 3 and 4. Breadth first finds the shortest way to get exactly 2 litres.', set: { alg: 'bfs', gr: 'jugs', ja: 3, jb: 4, jw: 2 }, play: true }
    ],
    change(z, k) {
      if (k !== 'gr') return;
      const d = { romania: ['Arad', 'Bucharest'], tree: ['A', 'M'], trap: ['S', 'Goal'], custom: ['S', 'G'] }[z.p.gr];
      if (d) z.set({ start: d[0], goal: d[1] });
    },
    frames(p, z) {
      const W = 620, H = 400;
      const G = p.gr === 'romania' ? romania(W, H) : p.gr === 'tree' ? treeGraph(W, H) : p.gr === 'trap' ? trapGraph(W, H) : p.gr === 'jugs' ? jugGraph(W, H, p.ja, p.jb, p.jw) : customGraph(W, H, p.edges, p.hs);
      let start, goal, isGoal;
      if (p.gr === 'jugs') { start = '(0,0)'; isGoal = G.isGoal; goal = null; }
      else {
        start = findId(G, p.start); goal = findId(G, p.goal);
        if (!start) throw new Error(`"${p.start}" is not a place on this map.`);
        if (!goal) throw new Error(`"${p.goal}" is not a place on this map.`);
        isGoal = s => s === goal;
      }
      const Hm = G.h(goal);
      const informed = p.alg === 'greedy' || p.alg === 'astar';
      z.state.G = G; z.state.goal = goal; z.state.start = start;
      const fr = runSearch(G, p.alg, start, isGoal, informed ? (Hm || {}) : null, p.lim);
      if (informed && !Hm) fr[0].say += ' This map has no heuristic table for this goal, so h = 0 everywhere and the search behaves like uniform cost search.';
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col, G = z.state.G;
      const pos = {};
      G.nodes.forEach(n => pos[n.id] = n);
      const sol = f.sol || [];
      const onSol = (a, b) => sol.some((s, i) => i && ((sol[i - 1] === a && s === b) || (sol[i - 1] === b && s === a)));
      const inTree = (a, b) => f.tree.some(e => (e[0] === a && e[1] === b) || (e[0] === b && e[1] === a));
      const drawn = new Set();
      G.nodes.forEach(n => (G.adj[n.id] || []).forEach(([m, cost]) => {
        const k = [n.id, m].sort().join('|');
        if (drawn.has(k)) return; drawn.add(k);
        const a = pos[n.id], b = pos[m];
        const col = onSol(n.id, m) ? c.green : inTree(n.id, m) ? c.cv : c.line;
        D.line(g, a.x, a.y, b.x, b.y, col, onSol(n.id, m) ? 4 : inTree(n.id, m) ? 2.4 : 1.3);
        if (G.costs) {
          const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
          D.text(g, String(cost), mx + 4, my - 3, { s: 9.5, c: c.ink2, mono: true });
        }
      }));
      G.nodes.forEach(n => {
        let kind = 'idle';
        if (f.explored.includes(n.id)) kind = 'done';
        if (f.front.includes(n.id)) kind = 'frontier';
        if (sol.includes(n.id)) kind = 'path';
        if (f.cur === n.id && !sol.length) kind = 'cur';
        const r = G.big ? 12 : 7;
        node(z, n.x, n.y, n.lab, kind, { r, inside: n.inside, dy: n.dy, s: 10.5 });
        if (n.id === z.state.goal && kind !== 'path') D.circle(g, n.x, n.y, r + 4, { stroke: c.green, w: 1.5 });
      });
      if (f.limit !== undefined) tag(g, `depth limit ${f.limit}`, z.W - 70, z.H - 16, { s: 11, fill: c.yellow, stroke: c.yellow, c: '#1f1300' });
    }
  });

  /* =====================================================================================================
     3.2  The 8 puzzle heuristics
     ===================================================================================================== */
  trace('puzzle8', {
    title: 'Two heuristics for the 8 puzzle',
    sub: 'h1 counts tiles in the wrong place. h2 adds how many rows and columns each tile is from its home. The blank does not count.',
    W: 600, H: 250,
    params: [
      { k: 's', label: 'Start, row by row (0 is the blank)', type: 'text', v: '7 2 4 5 0 6 8 3 1' },
      { k: 't', label: 'Goal, row by row', type: 'text', v: '0 1 2 3 4 5 6 7 8' }
    ],
    tips: [
      { t: 'The textbook start state. h1 = 8 (all tiles misplaced) and h2 = 3 + 1 + 2 + 2 + 2 + 3 + 3 + 2 = 18.', set: { s: '7 2 4 5 0 6 8 3 1', t: '0 1 2 3 4 5 6 7 8' }, play: true },
      { t: 'One move away from the goal. Both heuristics give 1, and the true cost is 1.', set: { s: '1 0 2 3 4 5 6 7 8' }, play: true },
      { t: 'Swap two tiles of the goal (1 and 2). The inversion count becomes odd, so this state can never reach the goal. Heuristics do not tell you that, the parity check does.', set: { s: '0 2 1 3 4 5 6 7 8' }, play: true }
    ],
    frames(p) {
      const a = nums(p.s), b = nums(p.t);
      const ok = v => v.length === 9 && [...v].sort((x, y) => x - y).every((x, i) => x === i);
      if (!ok(a) || !ok(b)) throw new Error('Each state needs the nine numbers 0 to 8, each used once.');
      const fr = [];
      let h1 = 0, h2 = 0;
      const marks = {};
      fr.push({ a, b, marks: {}, h1, h2, say: 'Left: the start state. Right: the goal. We go through the tiles 1 to 8 and score each one.' });
      for (let t = 1; t <= 8; t++) {
        const i = a.indexOf(t), j = b.indexOf(t);
        const d = Math.abs(Math.floor(i / 3) - Math.floor(j / 3)) + Math.abs(i % 3 - j % 3);
        const mis = i !== j ? 1 : 0;
        h1 += mis; h2 += d;
        marks[t] = d;
        fr.push({ a, b, marks: { ...marks }, cur: t, h1, h2, say: `Tile ${t} is at row ${Math.floor(i / 3) + 1}, column ${i % 3 + 1}. Its home is row ${Math.floor(j / 3) + 1}, column ${j % 3 + 1}. ${mis ? 'It is misplaced, so h1 adds 1.' : 'It is home, so h1 adds 0.'} Its Manhattan distance is ${d}, so h2 adds ${d}. Running totals: h1 = ${h1}, h2 = ${h2}.` });
      }
      const inv = v => { const s = v.filter(x => x); let n = 0; for (let i = 0; i < s.length; i++) for (let j = i + 1; j < s.length; j++) if (s[i] > s[j]) n++; return n; };
      const ia = inv(a), ib = inv(b);
      fr.push({ a, b, marks: { ...marks }, h1, h2, say: `Final: <b>h1 = ${h1}</b> and <b>h2 = ${h2}</b>. h2 is never smaller than h1 (h2 dominates h1), and both never overestimate, so A* with h2 expands fewer nodes. Solvability check: the start has ${ia} inversions and the goal has ${ib}. ${(ia % 2) === (ib % 2) ? 'Same parity, so the goal can be reached.' : 'Different parity, so the goal can never be reached from this start.'}` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const grid = (v, x0, title, showMarks) => {
        D.text(g, title, x0 + 75, 22, { a: 'center', s: 13, b: true, c: c.ink });
        v.forEach((t, i) => {
          const x = x0 + (i % 3) * 50, y = 34 + Math.floor(i / 3) * 50;
          if (!t) { D.rect(g, x, y, 46, 46, { stroke: c.line, dash: [3, 3] }); return; }
          const hot = f.cur === t;
          rr(g, x, y, 46, 46, 8, { fill: hot ? c.cv : c.bg, stroke: hot ? c.cv : c.line });
          D.text(g, String(t), x + 23, y + 25, { a: 'center', bl: 'middle', s: 18, b: true, c: hot ? '#fff' : c.ink });
          if (showMarks && f.marks[t] !== undefined) D.text(g, 'd=' + f.marks[t], x + 42, y + 42, { a: 'right', s: 9.5, c: hot ? '#fff' : c.ink2, mono: true });
        });
      };
      grid(f.a, 40, 'Start', true);
      grid(f.b, 260, 'Goal', false);
      tag(g, 'h1 = ' + f.h1, 490, 80, { s: 14, fill: c.surf, stroke: c.cv, c: c.cv });
      tag(g, 'h2 = ' + f.h2, 490, 130, { s: 14, fill: c.cv, stroke: c.cv, c: '#fff' });
    }
  });

  /* =====================================================================================================
     3.3  IDA* and RBFS on the Romania map
     ===================================================================================================== */
  function roTree() { return { adj: ROADJ, h: SLD }; }
  trace('idastar', {
    title: 'IDA*: depth first search with an f limit that grows',
    sub: 'Each iteration explores every path whose f = g + h stays within the limit. The next limit is the smallest f that went over.',
    W: 620, H: 400,
    params: [
      { k: 'start', label: 'Start city', type: 'text', v: 'Arad' }
    ],
    tips: [
      { t: 'From Arad. The limits go 366, 393, 413, 415, 417, 418 and the goal is found at 418, the optimal cost.', set: { start: 'Arad' }, play: true },
      { t: 'From Sibiu, the problem of slide 34. The limits go 253, 273, 275, 277, 278, and Bucharest is found at 278.', set: { start: 'Sibiu' }, play: true }
    ],
    frames(p, z) {
      const G = romania(620, 400);
      z.state.G = G;
      const start = findId(G, p.start);
      if (!start) throw new Error(`"${p.start}" is not a city on the map.`);
      const fr = [];
      let limit = SLD[start], found = null;
      for (let it = 1; it <= 12 && !found; it++) {
        let next = Infinity;
        const seen = [], tree = [];
        fr.push({ cur: null, explored: [], front: [], tree: [], limit, say: `Iteration ${it}: f limit = <b>${limit}</b>. Start depth first from ${esc(start)}, f = 0 + ${SLD[start]} = ${SLD[start]}.` });
        const rec = (s, g, path) => {
          if (found) return;
          const f = g + SLD[s];
          if (f > limit) { next = Math.min(next, f); fr.push({ cur: s, explored: seen.slice(), front: [s], tree: tree.slice(), limit, say: `${esc(s)}: f = ${g} + ${SLD[s]} = ${f}, more than the limit ${limit}. Cut it off and remember ${f} as a candidate for the next limit (smallest so far ${next}).` }); return; }
          seen.push(s);
          if (s === 'Bucharest') { found = path; fr.push({ cur: s, explored: seen.slice(), front: [], tree: tree.slice(), limit, sol: path.slice(), say: `${esc(s)}: f = ${f} is within the limit and it is the goal. Path ${path.map(esc).join(' → ')}, cost <b>${g}</b>.` }); return; }
          fr.push({ cur: s, explored: seen.slice(), front: [], tree: tree.slice(), limit, say: `${esc(s)}: f = ${g} + ${SLD[s]} = ${f} is within ${limit}, so expand it.` });
          for (const [c, cost] of ROADJ[s]) {
            if (path.includes(c)) continue;
            tree.push([s, c]);
            rec(c, g + cost, path.concat(c));
            if (found) return;
          }
        };
        rec(start, 0, [start]);
        if (!found) { fr.push({ cur: null, explored: seen.slice(), front: [], tree: tree.slice(), limit, say: `Iteration ${it} ends without the goal. The smallest f that went over the limit was <b>${next}</b>, so that is the new limit. Memory used is only the current path.` }); limit = next; }
      }
      return fr;
    },
    paint(z, f) { CAI._paintRo(z, f); }
  });

  trace('rbfs', {
    title: 'Recursive best first search (RBFS)',
    sub: 'Go down the best child while its f stays below the best alternative. When it goes over, come back and remember the better f.',
    W: 620, H: 400,
    params: [{ k: 'start', label: 'Start city', type: 'text', v: 'Arad' }],
    tips: [{ t: 'From Arad, exactly as on the slide: dive to Rimnicu Vilcea, come back when Pitesti (417) beats the limit 415, try Fagaras, come back with 450, then go through Pitesti to Bucharest at 418.', set: { start: 'Arad' }, play: true }],
    frames(p, z) {
      const G = romania(620, 400);
      z.state.G = G;
      const start = findId(G, p.start);
      if (!start) throw new Error(`"${p.start}" is not a city on the map.`);
      const fr = [];
      const tree = [], seen = [];
      const lab = v => v === Infinity ? '∞' : String(v);
      let sol = null;
      const rec = (s, g, fs, flim, path) => {
        seen.push(s);
        if (s === 'Bucharest') { sol = path; fr.push({ cur: s, explored: seen.slice(), front: [], tree: tree.slice(), sol: path.slice(), say: `Reach ${esc(s)}, the goal. Path ${path.map(esc).join(' → ')}, cost <b>${g}</b>.` }); return [true, fs]; }
        const kids = ROADJ[s].map(([c, cost]) => ({ c, g: g + cost, f: Math.max(g + cost + SLD[c], fs) }));
        kids.forEach(k => tree.push([s, k.c]));
        fr.push({ cur: s, explored: seen.slice(), front: kids.map(k => k.c), tree: tree.slice(), flim, say: `Expand ${esc(s)} with f limit ${lab(flim)}. Children: ${kids.map(k => `${esc(k.c)} ${k.f}`).join(', ')}.` });
        for (let guard = 0; guard < 20; guard++) {
          kids.sort((a, b) => a.f - b.f);
          const best = kids[0], alt = kids[1] ? kids[1].f : Infinity;
          if (best.f > flim) {
            fr.push({ cur: s, explored: seen.slice(), front: [], tree: tree.slice(), flim, say: `At ${esc(s)}: the best child ${esc(best.c)} has f = ${best.f}, more than the limit ${lab(flim)}. Unwind: go back up and report ${best.f} as the new f of ${esc(s)}.` });
            return [false, best.f];
          }
          fr.push({ cur: best.c, explored: seen.slice(), front: kids.map(k => k.c), tree: tree.slice(), flim: Math.min(flim, alt), say: `At ${esc(s)}: best child ${esc(best.c)} (f = ${best.f}), best alternative ${lab(alt)}. Go down into ${esc(best.c)} with limit min(${lab(flim)}, ${lab(alt)}) = ${lab(Math.min(flim, alt))}.` });
          const [ok, nf] = rec(best.c, best.g, best.f, Math.min(flim, alt), path.concat(best.c));
          if (ok) return [true, nf];
          best.f = nf;
          fr.push({ cur: s, explored: seen.slice(), front: kids.map(k => k.c), tree: tree.slice(), flim, say: `Back at ${esc(s)}. ${esc(best.c)} now has the backed up value f = ${nf}. Choose again.` });
        }
        return [false, Infinity];
      };
      fr.push({ cur: start, explored: [], front: [start], tree: [], flim: Infinity, say: `Start at ${esc(start)} with f = ${SLD[start]} and f limit ∞.` });
      rec(start, 0, SLD[start], Infinity, [start]);
      return fr;
    },
    paint(z, f) { CAI._paintRo(z, f); if (f.flim !== undefined) tag(z.g, 'f limit ' + (f.flim === Infinity ? '∞' : f.flim), z.W - 70, z.H - 16, { s: 11, fill: z.col.yellow, stroke: z.col.yellow, c: '#1f1300' }); }
  });

  function paintRo(z, f) {
    const { g } = z, c = z.col, G = z.state.G;
    const pos = {};
    G.nodes.forEach(n => pos[n.id] = n);
    const sol = f.sol || [];
    const onSol = (a, b) => sol.some((s, i) => i && ((sol[i - 1] === a && s === b) || (sol[i - 1] === b && s === a)));
    const inTree = (a, b) => (f.tree || []).some(e => (e[0] === a && e[1] === b) || (e[0] === b && e[1] === a));
    const drawn = new Set();
    G.nodes.forEach(n => (G.adj[n.id] || []).forEach(([m, cost]) => {
      const k = [n.id, m].sort().join('|'); if (drawn.has(k)) return; drawn.add(k);
      const a = pos[n.id], b = pos[m];
      D.line(g, a.x, a.y, b.x, b.y, onSol(n.id, m) ? c.green : inTree(n.id, m) ? c.cv : c.line, onSol(n.id, m) ? 4 : inTree(n.id, m) ? 2.4 : 1.3);
      D.text(g, String(cost), (a.x + b.x) / 2 + 4, (a.y + b.y) / 2 - 3, { s: 9.5, c: c.ink2, mono: true });
    }));
    G.nodes.forEach(n => {
      let kind = 'idle';
      if ((f.explored || []).includes(n.id)) kind = 'done';
      if ((f.front || []).includes(n.id)) kind = 'frontier';
      if (sol.includes(n.id)) kind = 'path';
      if (f.cur === n.id && !sol.length) kind = 'cur';
      node(z, n.x, n.y, n.lab, kind, { r: 7, dy: n.dy, s: 10.5 });
    });
    if (f.limit !== undefined) tag(g, 'f limit ' + f.limit, z.W - 70, z.H - 16, { s: 11, fill: c.yellow, stroke: c.yellow, c: '#1f1300' });
  }

  /* =====================================================================================================
     3.4  AO* on the AND-OR graph of the slides
     ===================================================================================================== */
  trace('aostar', {
    title: 'AO* on an AND-OR graph',
    sub: 'An arc joins the children of an AND connector: all of them must be solved. The bottom nodes E to J are simple tasks whose value is their exact cost. Values next to nodes are the current estimates.',
    W: 600, H: 330,
    params: [
      { k: 'hs', label: 'Heuristic of each node', type: 'text', v: 'B 5, C 2, D 4, E 7, F 9, G 3, H 0, I 0, J 0' },
      { k: 'ec', label: 'Cost of every edge', type: 'range', v: 1, min: 1, max: 5 }
    ],
    tips: [
      { t: 'The slide example. A first prefers B (6 against 8). After B is expanded h(B) rises to 8, so A → B costs 9, more than C AND D at 8, and A switches. C AND D then ends at 5 and A is solved.', set: { hs: 'B 5, C 2, D 4, E 7, F 9, G 3, H 0, I 0, J 0', ec: 1 }, play: true },
      { t: 'Make H cost 6. C then prefers G (cost 4), so C AND D looks like 10, and A switches back to B, which is already solved through E. AO* stops at 9, yet the true best is 7, because h(D) = 4 is more than the real cost of D (1). An h that overestimates breaks the guarantee.', set: { hs: 'B 5, C 2, D 4, E 7, F 9, G 3, H 6, I 0, J 0' }, play: true }
    ],
    frames(p) {
      const H = { A: 0 };
      String(p.hs).split(',').forEach(t => { const m = t.trim().split(/\s+/); if (m.length === 2 && !isNaN(+m[1])) H[m[0]] = +m[1]; });
      'BCDEFGHIJ'.split('').forEach(k => { if (H[k] === undefined) throw new Error('Give a value for every node B to J, for example "B 5, C 2, ..."'); });
      const ec = p.ec;
      const conns = { A: [['B'], ['C', 'D']], B: [['E'], ['F']], C: [['G'], ['H', 'I']], D: [['J']] };
      const est = { ...H }, solved = {}, expanded = {}, best = {};
      'EFGHIJ'.split('').forEach(k => { solved[k] = true; });
      const cost = (n, con) => con.reduce((s, k) => s + ec + est[k], 0);
      const fr = [];
      const snap = (say, cur) => fr.push({ est: { ...est }, solved: { ...solved }, expanded: { ...expanded }, best: { ...best }, cur, say });
      snap(`Start at A. Only A is known. Its children will be B (an OR choice) or C and D together (an AND connector, both needed). Every edge costs ${ec}.`, 'A');
      const revise = n => {
        const opts = conns[n].map(con => ({ con, c: cost(n, con) }));
        opts.sort((a, b) => a.c - b.c);
        best[n] = opts[0].con.join('+');
        est[n] = opts[0].c;
        solved[n] = opts[0].con.every(k => solved[k]);
        return opts;
      };
      expanded.A = true;
      let opts = revise('A');
      snap(`Expand A. f(A → B) = ${ec} + ${est.B} = ${cost('A', ['B'])}. f(A → C + D) = ${ec} + ${est.C} + ${ec} + ${est.D} = ${cost('A', ['C', 'D'])}. The cheaper connector is <b>${best.A}</b>, so the current best partial solution goes there. h(A) = ${est.A}.`, 'A');
      for (let guard = 0; guard < 10 && !solved.A; guard++) {
        /* find an unexpanded, unsolved node in the current best partial solution graph */
        const tip = [];
        const walk = n => { if (solved[n]) return; if (!conns[n]) return; if (!expanded[n]) { tip.push(n); return; } best[n].split('+').forEach(walk); };
        walk('A');
        if (!tip.length) break;
        const n = tip[0];
        expanded[n] = true;
        opts = revise(n);
        const parts = opts.map(o => `f(${n} → ${o.con.join(' + ')}) = ${o.con.map(k => `${ec} + ${H[k]}`).join(' + ')} = ${o.c}`).join(', ');
        snap(`Expand ${n}, a tip of the current best solution. ${parts}. Keep <b>${n} → ${best[n]}</b>, so h(${n}) becomes ${est[n]}${solved[n] ? ' and ' + n + ' is solved because every child on that connector is solved' : ''}.`, n);
        /* propagate upward */
        const ancestors = Object.keys(conns).filter(m => conns[m].some(con => con.includes(n)) && expanded[m]);
        ancestors.forEach(m => {
          const old = best[m], oldv = est[m];
          revise(m);
          snap(`Update the parent ${m}: ${conns[m].map(con => `f(${m} → ${con.join(' + ')}) = ${cost(m, con)}`).join(' and ')}. Best is <b>${best[m]}</b> with ${est[m]}${old !== best[m] ? `, so the best partial solution switches from ${old} to ${best[m]}` : ''}${oldv !== est[m] ? ` (was ${oldv})` : ''}.${solved[m] ? ` ${m} is now solved.` : ''}`, m);
        });
      }
      snap(solved.A ? `A is solved with cost <b>${est.A}</b>. The solution graph is A → ${best.A}${best.C && best.A.includes('C') ? ', C → ' + best.C : ''}${best.D && best.A.includes('D') ? ', D → ' + best.D : ''}${best.B && best.A === 'B' ? ', B → ' + best.B : ''}.` : `A cannot be solved with these values: the best option still ends at a dead end.`, 'A');
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const P = { A: [300, 40], B: [130, 135], C: [300, 135], D: [470, 135], E: [80, 250], F: [180, 250], G: [240, 250], H: [300, 250], I: [360, 250], J: [470, 250] };
      const conns = { A: [['B'], ['C', 'D']], B: [['E'], ['F']], C: [['G'], ['H', 'I']], D: [['J']] };
      Object.keys(conns).forEach(n => {
        if (!f.expanded[n]) return;
        conns[n].forEach(con => {
          const on = f.best[n] === con.join('+');
          con.forEach(k => D.line(g, P[n][0], P[n][1], P[k][0], P[k][1], on ? c.cv : c.line, on ? 3 : 1.5));
          if (con.length > 1) {
            const a1 = Math.atan2(P[con[0]][1] - P[n][1], P[con[0]][0] - P[n][0]), a2 = Math.atan2(P[con[1]][1] - P[n][1], P[con[1]][0] - P[n][0]);
            g.save(); g.strokeStyle = on ? c.cv : c.ink2; g.lineWidth = 2; g.beginPath(); g.arc(P[n][0], P[n][1], 34, Math.min(a1, a2), Math.max(a1, a2)); g.stroke(); g.restore();
          }
        });
      });
      Object.keys(P).forEach(n => {
        const vis = n === 'A' || Object.keys(conns).some(m => f.expanded[m] && conns[m].some(con => con.includes(n)));
        if (!vis) return;
        const kind = f.cur === n ? 'cur' : f.solved[n] && conns[n] ? 'path' : f.expanded[n] ? 'done' : 'frontier';
        node(z, P[n][0], P[n][1], '', kind, { r: 15, inside: n, is: 13 });
        if (n !== 'A' || f.expanded.A) tag(g, String(f.est[n]), P[n][0] + 28, P[n][1] - 4, { s: 11, fill: c.yellow, stroke: c.yellow, c: '#1f1300', mono: true });
        if (f.solved[n] && conns[n]) D.text(g, 'solved', P[n][0], P[n][1] + 30, { a: 'center', s: 10, b: true, c: c.green });
      });
    }
  });

  /* =====================================================================================================
     4.1  Hill climbing and simulated annealing on a landscape
     ===================================================================================================== */
  const LAND = {
    slide: x => {
      const sh = x < 14 ? 10 + 1.4 * x : x <= 24 ? 30 : 0;
      const glob = 90 * Math.exp(-Math.pow((x - 34) / 9, 2));
      const loc = 56 * Math.exp(-Math.pow((x - 62) / 4.5, 2));
      const flat = x >= 79 && x <= 86 ? 34 : 34 * Math.exp(-Math.pow((x < 79 ? x - 79 : x - 86) / 2.2, 2));
      return Math.round(Math.max(sh, glob, loc, flat, 10));
    },
    bumpy: x => Math.round(45 + 18 * Math.sin(x / 4.2) + 14 * Math.sin(x / 11 + 1) + 0.25 * x),
    single: x => Math.round(90 - Math.pow(x - 60, 2) / 40)
  };
  trace('hillclimb', {
    title: 'Climbing the state space landscape',
    sub: 'x is the state, the height is the objective value. The dot is the current state, the trail shows where it has been.',
    W: 600, H: 300,
    params: [
      { k: 'alg', label: 'Method', type: 'select', v: 'hc', opts: [['hc', 'Steepest ascent hill climbing'], ['side', 'Hill climbing with sideways moves'], ['restart', 'Random restart hill climbing'], ['sa', 'Simulated annealing']] },
      { k: 'land', label: 'Landscape', type: 'select', v: 'slide', opts: [['slide', 'Slide landscape (shoulder, peaks, flat top)'], ['bumpy', 'Many small hills'], ['single', 'One smooth hill']] },
      { k: 'x0', label: 'Start state x', type: 'range', v: 56, min: 0, max: 100 },
      { k: 'side', label: 'Sideways moves allowed', type: 'range', v: 12, min: 0, max: 30, show: p => p.alg === 'side' },
      { k: 'rs', label: 'Restarts', type: 'range', v: 4, min: 1, max: 8, show: p => p.alg === 'restart' },
      { k: 'T0', label: 'Starting temperature T0', type: 'range', v: 30, min: 1, max: 100, show: p => p.alg === 'sa' },
      { k: 'al', label: 'Cooling factor α (T ← α T)', type: 'range', v: 0.9, min: 0.5, max: 0.99, step: 0.01, show: p => p.alg === 'sa' },
      { k: 'seed', label: 'Random seed', type: 'range', v: 4, min: 1, max: 50, show: p => p.alg === 'restart' || p.alg === 'sa' }
    ],
    tips: [
      { t: 'Start at x = 56 on the slide landscape. Hill climbing walks up to the local maximum at x = 62 and stops there, far below the global peak.', set: { alg: 'hc', land: 'slide', x0: 56 }, play: true },
      { t: 'Start at x = 8. It climbs onto the shoulder and stops, because a flat neighbour is not better. Then allow sideways moves and see it cross the shoulder.', set: { alg: 'hc', land: 'slide', x0: 8 }, play: true },
      { t: 'Simulated annealing from x = 56 with T0 = 30. Early on it accepts some downhill moves, which lets it leave the local peak.', set: { alg: 'sa', land: 'slide', x0: 56, T0: 30, al: 0.9, seed: 4 }, play: true },
      { t: 'Same start, seed 3. This time the cooling wins before it escapes and it freezes on the local peak. Annealing is random: it finds the global peak often, not always.', set: { alg: 'sa', land: 'slide', x0: 56, T0: 30, al: 0.9, seed: 3 }, play: true },
      { t: 'Random restarts on the bumpy landscape. Each restart climbs a hill, and the best hill found so far is kept.', set: { alg: 'restart', land: 'bumpy', rs: 5 }, play: true }
    ],
    frames(p) {
      const f = LAND[p.land], fr = [];
      const r = CVZ.rng(p.seed * 7919 + 13);
      const at = x => ({ x, v: f(x) });
      const climb = (x, trail, best, tag0, sideLeft) => {
        let side = sideLeft;
        for (let guard = 0; guard < 60; guard++) {
          const L = x > 0 ? f(x - 1) : -Infinity, R = x < 100 ? f(x + 1) : -Infinity, v = f(x);
          const nb = R >= L ? x + 1 : x - 1, nv = Math.max(L, R);
          if (nv > v || (nv === v && side > 0)) {
            if (nv === v) side--;
            x = nb; trail.push(x);
            fr.push({ x, trail: trail.slice(), best, say: `${tag0}Neighbours have values ${L === -Infinity ? '–' : L} (left) and ${R === -Infinity ? '–' : R} (right). The best is ${nv}${nv === v ? `, equal to the current ${v}, so take a sideways move (${side} left)` : `, higher than the current ${v}, so move`} to x = ${x}.` });
          } else {
            fr.push({ x, trail: trail.slice(), best, stop: true, say: `${tag0}At x = ${x} with value ${v}. The neighbours give ${L === -Infinity ? '–' : L} and ${R === -Infinity ? '–' : R}, ${nv === v ? 'no better (a flat area)' : 'both lower'}. Hill climbing stops here. ${v === 90 && p.land === 'slide' ? 'This is the global maximum.' : 'This is a local maximum or a plateau, not necessarily the best state.'}` });
            return x;
          }
        }
        return x;
      };
      fr.push({ x: p.x0, trail: [p.x0], best: null, say: `Start at x = ${p.x0}, value ${f(p.x0)}. Only the current state is kept in memory, not a path.` });
      if (p.alg === 'hc' || p.alg === 'side') climb(p.x0, [p.x0], null, '', p.alg === 'side' ? p.side : 0);
      else if (p.alg === 'restart') {
        let best = null, x = p.x0;
        for (let k = 0; k < p.rs; k++) {
          if (k) { x = Math.floor(r() * 101); fr.push({ x, trail: [x], best, say: `Restart ${k + 1}: jump to a random state x = ${x} (value ${f(x)}).` }); }
          const top = climb(x, [x], best, `Run ${k + 1}. `, 0);
          if (!best || f(top) > best.v) best = at(top);
          fr.push({ x: top, trail: [top], best, say: `Run ${k + 1} ends at x = ${top} with ${f(top)}. Best so far: x = ${best.x} with ${best.v}.` });
        }
      } else {
        let x = p.x0, T = p.T0, best = at(x);
        for (let k = 0; k < 70 && T > 0.05; k++) {
          const nx = Math.max(0, Math.min(100, x + Math.round((r() * 2 - 1) * 6) || 1));
          const dE = f(nx) - f(x);
          const P = dE > 0 ? 1 : Math.exp(dE / T);
          const u = r();
          const acc = u < P;
          const old = x;
          if (acc) x = nx;
          if (f(x) > best.v) best = at(x);
          fr.push({ x, trail: [old, x], best, T, say: `T = ${fmt(T, 2)}. Try a random neighbour x = ${nx}: ΔE = ${f(nx)} − ${f(old)} = ${dE}. ${dE > 0 ? 'It is better, so always accept.' : `It is worse, accept with probability e^(ΔE/T) = e^(${dE}/${fmt(T, 2)}) = ${fmt(P, 3)}. The random number is ${fmt(u, 3)}, so ${acc ? '<b>accept</b> the worse move' : '<b>reject</b> it and stay'}.`} Then cool: T ← ${p.al} × T.` });
          T *= p.al;
        }
        fr.push({ x, trail: [x], best, T, say: `The temperature is now close to 0, so the search has frozen at x = ${x} (value ${f(x)}). Best state seen: x = ${best.x} with ${best.v}.` });
      }
      return fr;
    },
    paint(z, fr) {
      const { g } = z, c = z.col, f = LAND[z.p.land];
      const m = D.axes(g, z, [50, 20, 520, 220], [0, 100], [0, 100], { xl: 'state x', yl: 'objective', nx: 10, ny: 4 });
      D.curve(g, f, [0, 100], m, c.ink2, 2, 200);
      if (fr.trail && fr.trail.length > 1) for (let i = 1; i < fr.trail.length; i++) D.line(g, m.sx(fr.trail[i - 1]), m.sy(f(fr.trail[i - 1])), m.sx(fr.trail[i]), m.sy(f(fr.trail[i])), c.orange, 3);
      if (fr.best) D.circle(g, m.sx(fr.best.x), m.sy(fr.best.v), 7, { stroke: c.green, w: 3 });
      D.circle(g, m.sx(fr.x), m.sy(f(fr.x)), 7, { fill: fr.stop ? c.red : c.cv, stroke: c.surf, w: 2 });
      if (fr.T !== undefined) tag(g, 'T = ' + fmt(fr.T, 2), 520, 34, { s: 11, fill: c.yellow, stroke: c.yellow, c: '#1f1300' });
    }
  });

  /* =====================================================================================================
     4.2  Genetic algorithm, the f(x) = x² example of the slides
     ===================================================================================================== */
  trace('genetic', {
    title: 'A genetic algorithm maximising f(x) = x² on 5 bit strings',
    sub: 'Selection by roulette wheel, one point crossover, then mutation. Each step does one stage of a generation.',
    W: 600, H: 300,
    params: [
      { k: 'mode', label: 'Choices', type: 'select', v: 'slide', opts: [['slide', 'Use the slide choices in generation 1'], ['rand', 'Random choices from the seed']] },
      { k: 'pop', label: 'Starting population (4 strings)', type: 'text', v: '01101 11000 01000 10011' },
      { k: 'gens', label: 'Generations', type: 'range', v: 1, min: 1, max: 5 },
      { k: 'mu', label: 'Mutation chance per bit', type: 'range', v: 0, min: 0, max: 0.2, step: 0.01 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 5, min: 1, max: 50 }
    ],
    tips: [
      { t: 'The slide example. Fitness 169, 576, 64, 361, total 1170. String 2 gets two copies, string 3 none. After crossover the best child is 11011 = 27 with fitness 729.', set: { mode: 'slide', pop: '01101 11000 01000 10011', gens: 1, mu: 0 }, play: true },
      { t: 'Run 4 generations with random choices and a small mutation chance. The best fitness climbs toward 31² = 961.', set: { mode: 'rand', gens: 4, mu: 0.05 }, play: true }
    ],
    frames(p) {
      let pop = list(p.pop);
      if (pop.length !== 4 || pop.some(s => !/^[01]{5}$/.test(s))) throw new Error('Write four strings of five 0s and 1s, for example 01101 11000 01000 10011.');
      const r = CVZ.rng(p.seed * 31 + 7);
      const fit = s => Math.pow(parseInt(s, 2), 2);
      const fr = [];
      for (let gen = 1; gen <= p.gens; gen++) {
        const F = pop.map(fit), tot = F.reduce((a, b) => a + b, 0), avg = tot / 4;
        const prob = F.map(v => v / tot), exp = F.map(v => v / avg);
        const rows = pop.map((s, i) => ({ s, x: parseInt(s, 2), f: F[i], p: prob[i], e: exp[i] }));
        fr.push({ gen, stage: 'fit', rows, say: `Generation ${gen}. Decode each string to x and score it with f(x) = x²: ${rows.map(q => `${q.s} → ${q.x} → ${q.f}`).join(', ')}. Total ${tot}, average ${fmt(avg, 1)}.` });
        fr.push({ gen, stage: 'prob', rows, say: `Roulette wheel: each string gets a slice of size f ⁄ total. Probabilities ${rows.map(q => fmt(q.p, 2)).join(', ')}. Expected copies f ⁄ average: ${rows.map(q => fmt(q.e, 2)).join(', ')}.` });
        let pool;
        if (p.mode === 'slide' && gen === 1) pool = [0, 1, 1, 3];
        else { pool = []; for (let k = 0; k < 4; k++) { let u = r(), a = 0; while (u > prob[a] && a < 3) { u -= prob[a]; a++; } pool.push(a); } }
        const cnt = [0, 1, 2, 3].map(i => pool.filter(x => x === i).length);
        fr.push({ gen, stage: 'sel', rows, cnt, pool, say: `Spin the wheel four times. Copies picked: ${cnt.join(', ')}. ${p.mode === 'slide' && gen === 1 ? 'These are the actual counts on the slide (the expected counts rounded): string 2 twice, string 3 never.' : ''} Strong strings tend to be picked more often, but luck plays a part.` });
        let pairs, cuts;
        if (p.mode === 'slide' && gen === 1) { pairs = [[1, 0], [1, 3]]; cuts = [4, 2]; }
        else { const sh = pool.slice().sort(() => r() - 0.5); pairs = [[sh[0], sh[1]], [sh[2], sh[3]]]; cuts = [1 + Math.floor(r() * 4), 1 + Math.floor(r() * 4)]; }
        const kids = [], par = [];
        pairs.forEach(([a, b], k) => { const A = pop[a], B = pop[b], c = cuts[k]; kids.push(A.slice(0, c) + B.slice(c), B.slice(0, c) + A.slice(c)); par.push(A, B); });
        fr.push({ gen, stage: 'cross', rows, pairs, cuts, kids, par, say: `One point crossover. Pair ${pairs[0].map(i => pop[i]).join(' and ')} cut after bit ${cuts[0]}, pair ${pairs[1].map(i => pop[i]).join(' and ')} cut after bit ${cuts[1]}. Swap the tails. Children: ${kids.join(', ')}.` });
        const mut = kids.map(s => s.split('').map(b => (r() < p.mu ? (b === '0' ? '1' : '0') : b)).join(''));
        const changed = mut.filter((s, i) => s !== kids[i]).length;
        pop = mut;
        const best = pop.reduce((a, b) => (fit(b) > fit(a) ? b : a));
        fr.push({ gen, stage: 'mut', rows: pop.map(s => ({ s, x: parseInt(s, 2), f: fit(s) })), kids, mut, par, cuts, say: `Mutation flips each bit with chance ${p.mu}. ${changed ? changed + ' string(s) changed.' : 'No bit flipped.'} New population: ${pop.map(s => `${s} (${parseInt(s, 2)}, ${fit(s)})`).join(', ')}. Best: <b>${best} = ${parseInt(best, 2)} with fitness ${fit(best)}</b>.` });
      }
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      D.text(g, 'Generation ' + f.gen, 20, 22, { s: 14, b: true, c: c.ink });
      const bits = (s, x, y, hiFrom, col) => s.split('').forEach((b, i) => { rr(g, x + i * 26, y, 23, 26, 5, { fill: hiFrom !== undefined && i >= hiFrom ? col : c.bg, stroke: c.line }); D.text(g, b, x + i * 26 + 11.5, y + 14, { a: 'center', bl: 'middle', s: 14, b: true, mono: true, c: c.ink }); });
      const heads = ['string', 'x', 'f(x)', 'P', 'expected', 'picked'];
      const hx = [30, 200, 250, 310, 370, 450];
      if (f.stage === 'cross' || f.stage === 'mut') {
        D.text(g, 'Parents', 30, 50, { s: 12, b: true, c: c.ink2 });
        D.text(g, f.stage === 'mut' ? 'After mutation' : 'Children', 330, 50, { s: 12, b: true, c: c.ink2 });
        f.kids.forEach((s, i) => {
          bits(f.par[i], 30, 62 + i * 52, f.cuts[i >> 1], c.cv + '55');
          bits(f.stage === 'mut' ? f.mut[i] : s, 330, 62 + i * 52, f.cuts ? f.cuts[i >> 1] : undefined, c.orange + '55');
          if (f.stage === 'mut') D.text(g, `x = ${parseInt(f.mut[i], 2)}, f = ${Math.pow(parseInt(f.mut[i], 2), 2)}`, 470, 80 + i * 52, { s: 12, c: c.ink, mono: true });
        });
        return;
      }
      heads.forEach((h, i) => { if (i < 3 || (i < 5 && f.stage !== 'fit') || (i === 5 && f.stage === 'sel')) D.text(g, h, hx[i], 50, { s: 12, b: true, c: c.ink2 }); });
      f.rows.forEach((q, i) => {
        const y = 62 + i * 52;
        bits(q.s, 30, y);
        D.text(g, String(q.x), hx[1], y + 18, { s: 13, mono: true, c: c.ink });
        D.text(g, String(q.f), hx[2], y + 18, { s: 13, mono: true, c: c.ink });
        if (f.stage !== 'fit') { D.text(g, fmt(q.p, 2), hx[3], y + 18, { s: 13, mono: true, c: c.ink }); D.text(g, fmt(q.e, 2), hx[4], y + 18, { s: 13, mono: true, c: c.ink }); }
        if (f.stage === 'sel') tag(g, String(f.cnt[i]), hx[5] + 14, y + 13, { s: 13, fill: f.cnt[i] ? c.cv : c.bg, stroke: c.cv, c: f.cnt[i] ? '#fff' : c.ink });
        if (f.stage !== 'fit') D.rect(g, 510, y + 6, Math.max(2, q.p * 80), 14, { fill: c.cv });
      });
    }
  });

  /* =====================================================================================================
     5.1  AC-3 arc consistency
     ===================================================================================================== */
  const AUS = { WA: [80, 150], NT: [210, 70], SA: [230, 185], Q: [350, 80], NSW: [400, 190], V: [330, 270], T: [450, 280] };
  const AUSE = [['WA', 'NT'], ['WA', 'SA'], ['NT', 'SA'], ['NT', 'Q'], ['SA', 'Q'], ['SA', 'NSW'], ['SA', 'V'], ['Q', 'NSW'], ['NSW', 'V']];
  function parseCSP(dom, cons) {
    const D0 = {}, vars = [];
    String(dom).split('\n').map(l => l.trim()).filter(Boolean).forEach(l => {
      const m = l.match(/^([A-Za-z]\w*)\s*:\s*(.*)$/);
      if (!m) throw new Error(`Write each domain as "X: 1 2 3". This line is not like that: ${l}`);
      vars.push(m[1]); D0[m[1]] = list(m[2]);
    });
    const C = [], U = [];
    String(cons).split(/\n|,/).map(l => l.trim()).filter(Boolean).forEach(l => {
      const m = l.match(/^(\w+)\s*(<=|>=|!=|≠|<|>|=)\s*(\w+)$/);
      const op = m ? (m[2] === '≠' ? '!=' : m[2]) : '';
      if (m && D0[m[1]] && D0[m[3]]) C.push([m[1], op, m[3]]);
      else if (m && D0[m[1]]) U.push([m[1], op, m[3]]);
      else throw new Error(`Write constraints like "A < B", "A != B" or "A != 1". Problem with: ${l}`);
    });
    return { vars, D: D0, C, U };
  }
  const OPS = { '<': (a, b) => a < b, '>': (a, b) => a > b, '<=': (a, b) => a <= b, '>=': (a, b) => a >= b, '=': (a, b) => a === b, '!=': (a, b) => a !== b };
  const FLIP = { '<': '>', '>': '<', '<=': '>=', '>=': '<=', '=': '=', '!=': '!=' };
  const cmpv = (a, b, op) => { const x = isNaN(+a) ? a : +a, y = isNaN(+b) ? b : +b; return OPS[op](x, y); };

  trace('ac3', {
    title: 'AC-3: making every arc consistent',
    sub: 'An arc X → Y is consistent when every value left in X has some value in Y that satisfies the constraint. Struck out values have been removed.',
    W: 600, H: 330,
    params: [
      { k: 'pre', label: 'Problem', type: 'select', v: 'abc', opts: [['abc', 'A < B < C with domains 1 to 3 (slide)'], ['aus', 'Australia after WA = red and Q = green'], ['custom', 'My own problem']] },
      { k: 'dom', label: 'Domains, one variable per line', type: 'area', v: 'A: 1 2 3 4\nB: 1 2 3 4\nC: 1 2 3 4', show: p => p.pre === 'custom' },
      { k: 'cons', label: 'Constraints, one per line', type: 'area', v: 'A < B\nB < C\nC != 4', show: p => p.pre === 'custom' }
    ],
    tips: [
      { t: 'The slide network A < B, B < C with domains {1, 2, 3}. AC-3 shrinks every domain to a single value: A = 1, B = 2, C = 3. A unique solution, found without any search.', set: { pre: 'abc' }, play: true },
      { t: 'Australia after WA = red and Q = green. Forward checking would leave NT = {blue} and SA = {blue}. AC-3 also checks the arc NT → SA and empties a domain, so it detects the failure early.', set: { pre: 'aus' }, play: true },
      { t: 'Your own problem: add the constraint "A != 1" and see how the removals spread through the network.', set: { pre: 'custom', dom: 'A: 1 2 3 4\nB: 1 2 3 4\nC: 1 2 3 4', cons: 'A < B\nB < C\nA != 1' }, play: true }
    ],
    frames(p, z) {
      let csp;
      if (p.pre === 'abc') csp = parseCSP('A: 1 2 3\nB: 1 2 3\nC: 1 2 3', 'A < B\nB < C');
      else if (p.pre === 'aus') csp = parseCSP('WA: R\nNT: R G B\nSA: R G B\nQ: G\nNSW: R G B\nV: R G B\nT: R G B', AUSE.map(e => e.join(' != ')).join('\n'));
      else csp = parseCSP(p.dom, p.cons);
      if (csp.vars.length > 9) throw new Error('Please keep to 9 variables or fewer.');
      z.state.csp = csp; z.state.pre = p.pre;
      const dom = {}; csp.vars.forEach(v => dom[v] = csp.D[v].slice());
      const removed = {}; csp.vars.forEach(v => removed[v] = []);
      const arcs = [];
      csp.C.forEach(([x, op, y]) => { arcs.push([x, y, op]); arcs.push([y, x, FLIP[op]]); });
      const q = arcs.slice();
      const fr = [];
      const snap = (say, arc, extra = {}) => fr.push(Object.assign({ dom: JSON.parse(JSON.stringify(dom)), removed: JSON.parse(JSON.stringify(removed)), arc, q: q.length, say }, extra));
      snap(`Here is the constraint graph. Each variable shows its domain, the values it may still take.`);
      (csp.U || []).forEach(([x, op, k]) => {
        const gone = dom[x].filter(a => !cmpv(a, k, op));
        dom[x] = dom[x].filter(a => cmpv(a, k, op));
        removed[x].push(...gone);
        snap(`Unary constraint ${x} ${op} ${k}: this only involves ${x}, so just remove the values that break it (node consistency)${gone.length ? ': ' + gone.join(', ') : ', nothing to remove'}.`, null, { hot: x });
        if (!dom[x].length) snap(`The domain of ${x} is empty, so there is <b>no solution</b>.`, null, { fail: x });
      });
      if (csp.vars.some(v => !dom[v].length)) return fr;
      snap(`Put every arc in the work list: ${arcs.length} arcs (each binary constraint gives two, X → Y and Y → X).`);
      let guard = 0;
      while (q.length && guard++ < 150) {
        const [x, y, op] = q.shift();
        const gone = [];
        dom[x] = dom[x].filter(a => { const ok = dom[y].some(b => cmpv(a, b, op)); if (!ok) gone.push(a); return ok; });
        removed[x].push(...gone);
        if (gone.length) {
          const back = arcs.filter(([u, w]) => w === x && u !== y && !q.some(t => t[0] === u && t[1] === w));
          back.forEach(a => q.push(a));
          snap(`Check ${x} → ${y} (${x} ${op} ${y}). Value${gone.length > 1 ? 's' : ''} ${gone.join(', ')} of ${x} ${gone.length > 1 ? 'have' : 'has'} no partner in ${y} = {${dom[y].join(', ')}}, so remove ${gone.length > 1 ? 'them' : 'it'}. ${x} changed, so put back the arcs into ${x}: ${back.map(a => a[0] + ' → ' + a[1]).join(', ') || 'none new'}.`, [x, y], { hot: x });
          if (!dom[x].length) { snap(`The domain of ${x} is empty. No assignment can satisfy all constraints, so the problem has <b>no solution</b>. AC-3 found this without any search.`, [x, y], { fail: x }); return fr; }
        } else snap(`Check ${x} → ${y} (${x} ${op} ${y}). Every value of ${x} = {${dom[x].join(', ')}} has a partner in ${y}. Nothing to remove.`, [x, y]);
      }
      const single = csp.vars.every(v => dom[v].length === 1);
      snap(single ? `The work list is empty and every domain has one value: ${csp.vars.map(v => v + ' = ' + dom[v][0]).join(', ')}. That is the <b>unique solution</b>.` : `The work list is empty. The network is arc consistent, but some domains still have several values, so arc consistency alone may not be enough. Search (backtracking) is needed to finish.`, null);
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col, csp = z.state.csp;
      const pos = {};
      if (z.state.pre === 'aus') csp.vars.forEach(v => pos[v] = AUS[v]);
      else csp.vars.forEach((v, i) => { const a = Math.PI + 2 * Math.PI * i / csp.vars.length; pos[v] = [300 + Math.cos(a) * 200, 160 + Math.sin(a) * 105]; });
      csp.C.forEach(([x, op, y]) => {
        const on = f.arc && ((f.arc[0] === x && f.arc[1] === y) || (f.arc[0] === y && f.arc[1] === x));
        D.line(g, pos[x][0], pos[x][1], pos[y][0], pos[y][1], on ? c.cv : c.line, on ? 3 : 1.4);
        if (z.state.pre !== 'aus') tag(g, op, (pos[x][0] + pos[y][0]) / 2, (pos[x][1] + pos[y][1]) / 2, { s: 11, fill: c.surf, stroke: c.line, c: c.ink, mono: true });
      });
      if (f.arc) { const [a, b] = f.arc; D.arrow(g, pos[b][0] + (pos[a][0] - pos[b][0]) * 0.2, pos[b][1] + (pos[a][1] - pos[b][1]) * 0.2, pos[b][0] + (pos[a][0] - pos[b][0]) * 0.75, pos[b][1] + (pos[a][1] - pos[b][1]) * 0.75, c.orange, 3); }
      csp.vars.forEach(v => {
        const [x, y] = pos[v];
        node(z, x, y, '', f.fail === v ? 'bad' : f.hot === v ? 'cur' : 'idle', { r: 17, inside: v, is: 11 });
        const all = csp.D[v];
        const w = all.length * 20;
        all.forEach((a, i) => {
          const gone = f.removed[v].includes(a);
          const cx = x - w / 2 + i * 20 + 10, cy = y + 30;
          const fill = COL[a] && !gone ? COL[a] : gone ? c.bg : c.surf;
          rr(g, cx - 9, cy - 9, 18, 18, 4, { fill, stroke: c.line });
          D.text(g, String(a), cx, cy + 1, { a: 'center', bl: 'middle', s: 11, b: true, c: gone ? c.ink2 : COL[a] ? '#fff' : c.ink, mono: true });
          if (gone) D.line(g, cx - 8, cy + 8, cx + 8, cy - 8, c.red, 2);
        });
      });
      tag(g, `work list: ${f.q} arcs`, 520, 20, { s: 11, fill: c.surf, stroke: c.line, c: c.ink });
    }
  });

  /* =====================================================================================================
     5.2  Backtracking search for map colouring, with MRV, degree, LCV, forward checking and MAC
     ===================================================================================================== */
  trace('mapcolor', {
    title: 'Backtracking search colours the map of Australia',
    sub: 'Neighbours must get different colours. Small squares show the colours each region still has left.',
    W: 600, H: 340,
    params: [
      { k: 'vo', label: 'Choose the next region by', type: 'select', v: 'fixed', opts: [['fixed', 'Fixed order WA, NT, NSW, Q, SA, V, T'], ['mrv', 'MRV: fewest colours left'], ['deg', 'MRV, ties broken by degree'], ['degonly', 'Degree: most constraints on unassigned regions']] },
      { k: 'val', label: 'Try colours in order', type: 'select', v: 'fixed', opts: [['fixed', 'Red, green, blue'], ['lcv', 'LCV: least constraining colour first']] },
      { k: 'inf', label: 'Inference after each choice', type: 'select', v: 'none', opts: [['none', 'None (plain backtracking)'], ['fc', 'Forward checking'], ['mac', 'Maintaining arc consistency (MAC)']] },
      { k: 'k', label: 'Number of colours', type: 'range', v: 3, min: 2, max: 4 }
    ],
    tips: [
      { t: 'Plain backtracking in the fixed order. WA red, NT green and NSW red force Q to be blue, and then SA has no colour left. The search must back up and recolour NSW.', set: { vo: 'fixed', val: 'fixed', inf: 'none', k: 3 }, play: true },
      { t: 'Same order with forward checking. Each choice removes that colour from the neighbours, so a dead end is spotted as soon as a domain becomes empty.', set: { vo: 'fixed', inf: 'fc' }, play: true },
      { t: 'MRV with degree tie breaking and forward checking. SA goes first (degree 5) and the map is coloured with no backtracking at all.', set: { vo: 'deg', val: 'lcv', inf: 'fc' }, play: true },
      { t: 'Only 2 colours. WA, NT and SA all touch each other, so it is impossible. Watch how quickly MAC proves it.', set: { k: 2, vo: 'deg', inf: 'mac' }, play: true }
    ],
    frames(p) {
      const V = ['WA', 'NT', 'NSW', 'Q', 'SA', 'V', 'T'];
      const nb = {}; V.forEach(v => nb[v] = []);
      AUSE.forEach(([a, b]) => { nb[a].push(b); nb[b].push(a); });
      const cols = ['R', 'G', 'B', 'Y'].slice(0, p.k);
      const fr = [];
      let back = 0;
      const snap = (asg, dom, say, extra = {}) => fr.push(Object.assign({ asg: { ...asg }, dom: JSON.parse(JSON.stringify(dom)), say }, extra));
      const dom0 = {}; V.forEach(v => dom0[v] = cols.slice());
      snap({}, dom0, `Seven regions, ${p.k} colours. No region is coloured yet. Every region can still take ${cols.map(x => COLNAME[x]).join(', ')}.`);
      const pick = (asg, dom) => {
        const un = V.filter(v => !asg[v]);
        const deg = v => nb[v].filter(w => !asg[w]).length;
        if (p.vo === 'fixed') return [un[0], 'it is next in the fixed order'];
        if (p.vo === 'degonly') { const b = un.slice().sort((a, b) => deg(b) - deg(a))[0]; return [b, `it has the most constraints on uncoloured regions (degree ${deg(b)})`]; }
        const m = Math.min(...un.map(v => dom[v].length));
        let c = un.filter(v => dom[v].length === m);
        if (p.vo === 'deg' && c.length > 1) { const d = Math.max(...c.map(deg)); c = c.filter(v => deg(v) === d); return [c[0], `it has the fewest colours left (${m}), and among those the highest degree (${d})`]; }
        return [c[0], `it has the fewest colours left (${m})`];
      };
      const order = (v, asg, dom) => {
        if (p.val !== 'lcv') return dom[v].slice();
        const lost = x => nb[v].filter(w => !asg[w] && dom[w].includes(x)).length;
        return dom[v].slice().sort((a, b) => lost(a) - lost(b));
      };
      const infer = (v, asg, dom) => {
        const d = JSON.parse(JSON.stringify(dom));
        d[v] = [asg[v]];
        const pruned = [];
        if (p.inf === 'none') return [d, pruned, null];
        nb[v].forEach(w => { if (!asg[w] && d[w].includes(asg[v])) { d[w] = d[w].filter(x => x !== asg[v]); pruned.push(`${COLNAME[asg[v]]} from ${w}`); } });
        let empty = V.find(w => !asg[w] && !d[w].length);
        if (p.inf === 'mac' && !empty) {
          const q = []; V.forEach(x => nb[x].forEach(y => { if (!asg[x]) q.push([x, y]); }));
          while (q.length) {
            const [x, y] = q.shift();
            const before = d[x].length;
            d[x] = d[x].filter(a => d[y].some(b => b !== a));
            if (d[x].length < before) { pruned.push(`arc ${x} → ${y} trims ${x}`); if (!d[x].length) { empty = x; break; } nb[x].forEach(z2 => { if (z2 !== y) q.push([z2, x]); }); }
          }
        }
        return [d, pruned, empty];
      };
      const solve = (asg, dom) => {
        if (fr.length > 180) return null;
        if (V.every(v => asg[v])) return asg;
        const [v, why] = pick(asg, dom);
        for (const x of order(v, asg, dom)) {
          const clash = nb[v].find(w => asg[w] === x);
          if (clash) { snap(asg, dom, `Try ${COLNAME[x]} for ${v}: it clashes with ${clash}, which is already ${COLNAME[x]}. Reject it.`, { cur: v }); continue; }
          const a2 = { ...asg, [v]: x };
          const [d2, pruned, empty] = infer(v, a2, dom);
          snap(a2, d2, `Choose ${v} because ${why}. Give it <b>${COLNAME[x]}</b>${p.val === 'lcv' ? ' (it rules out the fewest options for the neighbours)' : ''}. ${pruned.length ? 'Inference removes ' + pruned.join(', ') + '.' : ''}${empty ? ` Now ${empty} has no colour left, so this choice cannot work. Undo it at once (backtracks so far: ${back + 1}).` : ''}`, { cur: v, bad: empty });
          if (empty) { back++; continue; }
          const res = solve(a2, d2);
          if (res) return res;
          back++;
          snap(asg, dom, `Every colour for the regions after ${v} failed, so back up and undo ${v} = ${COLNAME[x]}. (Backtracks so far: ${back}.)`, { cur: v, undo: true });
        }
        return null;
      };
      const res = solve({}, dom0);
      if (res) snap(res, Object.fromEntries(V.map(v => [v, [res[v]]])), `Every region is coloured and no two neighbours share a colour: ${V.map(v => v + ' ' + COLNAME[res[v]]).join(', ')}. Backtracks needed: <b>${back}</b>.`, { done: true });
      else snap({}, dom0, `Every option has been tried. There is <b>no solution</b> with ${p.k} colours. Backtracks: ${back}.`, { fail: true });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      AUSE.forEach(([a, b]) => D.line(g, AUS[a][0], AUS[a][1], AUS[b][0], AUS[b][1], c.line, 1.6));
      Object.keys(AUS).forEach(v => {
        const [x, y] = AUS[v], col = f.asg[v];
        D.circle(g, x, y, 20, { fill: col ? COL[col] : c.surf, stroke: f.cur === v ? c.ink : f.bad === v ? c.red : c.line, w: f.cur === v || f.bad === v ? 3.5 : 1.6 });
        D.text(g, v, x, y + 1, { a: 'center', bl: 'middle', s: 11.5, b: true, c: col ? '#fff' : c.ink });
        const d = f.dom[v] || [];
        d.forEach((k, i) => D.rect(g, x - d.length * 7 + i * 14 + 1, y + 26, 12, 12, { fill: COL[k], stroke: c.surf }));
        if (!d.length) D.text(g, 'empty', x, y + 36, { a: 'center', s: 10, b: true, c: c.red });
      });
      D.text(g, 'Tasmania (T) touches no region', 450, 320, { a: 'center', s: 10.5, c: c.ink2 });
    }
  });

  /* =====================================================================================================
     5.3  Min-conflicts local search for N queens
     ===================================================================================================== */
  trace('minconflicts', {
    title: 'Min-conflicts local search for N queens',
    sub: 'One queen per column. Each step picks a queen that is attacked and moves it, within its column, to the row with the fewest attacks.',
    W: 600, H: 340,
    params: [
      { k: 'n', label: 'Board size N', type: 'range', v: 6, min: 4, max: 10 },
      { k: 'seed', label: 'Random seed for the start', type: 'range', v: 48, min: 1, max: 60 },
      { k: 'max', label: 'Most moves allowed', type: 'range', v: 30, min: 5, max: 80 }
    ],
    tips: [
      { t: 'Six queens. A random full placement is fixed in a handful of moves. The numbers in the chosen column are the attacks a queen would face in each row.', set: { n: 6, seed: 48 }, play: true },
      { t: 'Six queens with seed 9. Here it wanders for a while through placements with one attacking pair before it finds a solution. Plateaus slow min-conflicts down.', set: { n: 6, seed: 9, max: 40 }, play: true },
      { t: 'Ten queens. Min-conflicts still needs only a few moves, which is why it solves even a million queens quickly.', set: { n: 10, seed: 15 }, play: true }
    ],
    frames(p) {
      const n = p.n, r = CVZ.rng(p.seed * 97 + 1);
      let q = Array.from({ length: n }, () => Math.floor(r() * n));
      const att = (col, row, Q) => Q.reduce((s, rr2, c2) => s + (c2 !== col && (rr2 === row || Math.abs(rr2 - row) === Math.abs(c2 - col)) ? 1 : 0), 0);
      const total = Q => { let s = 0; for (let a = 0; a < n; a++) for (let b = a + 1; b < n; b++) if (Q[a] === Q[b] || Math.abs(Q[a] - Q[b]) === b - a) s++; return s; };
      const fr = [];
      fr.push({ q: q.slice(), say: `Start with a random complete placement: one queen in every column. Attacking pairs: <b>${total(q)}</b>. The goal is 0.` });
      for (let s = 0; s < p.max; s++) {
        if (!total(q)) break;
        const bad = q.map((row, c2) => c2).filter(c2 => att(c2, q[c2], q) > 0);
        const col = bad[Math.floor(r() * bad.length)];
        const counts = Array.from({ length: n }, (_, row) => att(col, row, q));
        const m = Math.min(...counts);
        const best = counts.map((v, i) => i).filter(i => counts[i] === m);
        const others = best.filter(i => i !== q[col]);
        const to = (others.length ? others : best)[Math.floor(r() * (others.length ? others : best).length)];
        fr.push({ q: q.slice(), col, counts, say: `Queen in column ${col + 1} is attacked ${att(col, q[col], q)} time(s). Count the attacks for every row of that column: ${counts.join(', ')}. The smallest is ${m}.` });
        const stay = to === q[col];
        q[col] = to;
        fr.push({ q: q.slice(), col, moved: to, say: stay ? `Row ${to + 1}, where it already stands, is the only best row, so it stays. Nothing changes this time, and another attacked queen will be picked next. Attacking pairs: <b>${total(q)}</b>.` : `Move it to row ${to + 1}${best.length > 1 ? ' (ties are broken at random)' : ''}. Attacking pairs now: <b>${total(q)}</b>.` });
      }
      fr.push({ q: q.slice(), done: !total(q), say: total(q) ? `Stopped after ${p.max} moves with ${total(q)} attacking pairs left. Allow more moves or try another seed.` : `Solved: no two queens attack each other. Rows from left to right: ${q.map(x => x + 1).join(', ')}.` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col, n = f.q.length;
      const s = Math.min(300 / n, 34), x0 = 300 - n * s / 2, y0 = 18;
      for (let r2 = 0; r2 < n; r2++) for (let c2 = 0; c2 < n; c2++) {
        D.rect(g, x0 + c2 * s, y0 + r2 * s, s, s, { fill: (r2 + c2) % 2 ? c.bg : c.surf, stroke: c.line });
        if (f.counts && c2 === f.col && f.q[c2] !== r2) D.text(g, String(f.counts[r2]), x0 + c2 * s + s / 2, y0 + r2 * s + s / 2 + 1, { a: 'center', bl: 'middle', s: Math.max(9, s * 0.38), b: true, c: c.orange, mono: true });
      }
      if (f.col !== undefined) D.rect(g, x0 + f.col * s, y0, s, n * s, { stroke: c.orange, w: 3 });
      f.q.forEach((r2, c2) => {
        const x = x0 + c2 * s + s / 2, y = y0 + r2 * s + s / 2;
        D.circle(g, x, y, s * 0.32, { fill: f.done ? c.green : c2 === f.col ? c.cv : c.ink, stroke: c.surf, w: 1.5 });
        D.text(g, 'Q', x, y + 1, { a: 'center', bl: 'middle', s: Math.max(9, s * 0.34), b: true, c: '#fff' });
      });
    }
  });

  /* =====================================================================================================
     6.x  Game trees: minimax, alpha beta, expectimax and expectiminimax
     ===================================================================================================== */
  const PATTERNS = { mm2: ['max', 'min'], mm3: ['max', 'min', 'max'], mm4: ['max', 'min', 'max', 'min'], ex: ['max', 'chance'], emm: ['max', 'chance', 'min'], mme: ['max', 'min', 'chance'] };
  function buildGame(p) {
    const pat = PATTERNS[p.pat], b = p.b, d = pat.length, need = Math.pow(b, d);
    if (need > 27) throw new Error(`That tree would need ${need} leaves. Please keep b to the power depth at 27 or less.`);
    let leaves = nums(p.leaves);
    let warn = '';
    if (leaves.length < need) { warn = ` You gave ${leaves.length} leaf values but the tree has ${need} leaves, so the rest are 0.`; while (leaves.length < need) leaves.push(0); }
    if (leaves.length > need) { warn = ` Only the first ${need} leaf values are used.`; leaves = leaves.slice(0, need); }
    let probs = nums(p.probs).slice(0, b);
    while (probs.length < b) probs.push(1);
    const ps = probs.reduce((a, x) => a + x, 0) || 1;
    probs = probs.map(x => x / ps);
    const L = 'ABCDEFG';
    let li = 0;
    const make = (depth, idx) => {
      if (depth === d) return { leaf: true, v: leaves[li++], name: '' };
      const nd = { type: pat[depth], name: L[depth] + (depth ? idx + 1 : ''), kids: [], depth };
      for (let k = 0; k < b; k++) nd.kids.push(make(depth + 1, idx * b + k));
      return nd;
    };
    return { root: make(0, 0), probs, warn, pat };
  }
  const fv = v => v === Infinity ? '∞' : v === -Infinity ? '−∞' : fmt(v, 2);
  trace('gametree', {
    title: 'Searching a game tree',
    sub: '▲ MAX picks the largest value, ▼ MIN the smallest, ● a chance node takes the probability weighted average. Leaves hold the utility for MAX.',
    W: 640, H: 330, speed: 1000,
    params: [
      { k: 'mode', label: 'Algorithm', type: 'select', v: 'minimax', opts: [['minimax', 'Minimax'], ['ab', 'Alpha beta pruning'], ['exp', 'Expectimax and expectiminimax']] },
      { k: 'pat', label: 'Layers from the top', type: 'select', v: 'mm3', opts: [['mm2', 'MAX, MIN'], ['mm3', 'MAX, MIN, MAX'], ['mm4', 'MAX, MIN, MAX, MIN'], ['ex', 'MAX, CHANCE'], ['emm', 'MAX, CHANCE, MIN'], ['mme', 'MAX, MIN, CHANCE']] },
      { k: 'b', label: 'Branching factor b', type: 'range', v: 3, min: 2, max: 4 },
      { k: 'leaves', label: 'Leaf values, left to right', type: 'text', v: '2 1 5 6 2 11 8 5 1 3 2 4 10 11 12 1 2 1 2 1 3 6 1 11 2 5 1' },
      { k: 'probs', label: 'Chance probabilities for each child (scaled to add up to 1)', type: 'text', v: '1 1 1', show: p => /ex|emm|mme/.test(p.pat) }
    ],
    tips: [
      { t: 'The minimax example of the slides: three levels, 27 leaves. C1 = 5, C2 = 11, C3 = 8 give B1 = 5, and the root A is 5 through B1.', set: { mode: 'minimax', pat: 'mm3', b: 3, leaves: '2 1 5 6 2 11 8 5 1 3 2 4 10 11 12 1 2 1 2 1 3 6 1 11 2 5 1' }, play: true },
      { t: 'The alpha beta example of the slides: leaves 2 3 5 9 0 1 7 5. The 9 under E is never looked at, and the whole subtree G is pruned. The root value 3 is the same as plain minimax.', set: { mode: 'ab', pat: 'mm3', b: 2, leaves: '2 3 5 9 0 1 7 5' }, play: true },
      { t: 'Alpha beta on the 27 leaf tree of the slides. It reads only 11 leaves and prunes 16. That is the best any order can do for b = 3 and depth 3: 3² + 3 − 1 = 11.', set: { mode: 'ab', pat: 'mm3', b: 3, leaves: '2 1 5 6 2 11 8 5 1 3 2 4 10 11 12 1 2 1 2 1 3 6 1 11 2 5 1' }, play: true },
      { t: 'The same 27 leaves in the worst order: every node sees its worst child first. Alpha beta now reads all 27 leaves and prunes nothing, but the root is still 5.', set: { mode: 'ab', pat: 'mm3', b: 3, leaves: '10 11 12 2 3 4 1 1 2 1 6 11 1 2 5 1 2 3 2 6 11 1 5 8 1 2 5' }, play: true },
      { t: 'The expectimax example of the slides: chance nodes with 1/3 each over 3 12 9, 2 4 6 and 15 6 0 give 8, 4 and 7, so MAX takes 8.', set: { mode: 'exp', pat: 'ex', b: 3, leaves: '3 12 9 2 4 6 15 6 0', probs: '1 1 1' }, play: true },
      { t: 'Expectiminimax with probabilities 0.5, 0.4, 0.1. The middle chance node of the slide has MIN children 2, 1, 3, so its value is 0.5 × 2 + 0.4 × 1 + 0.1 × 3 = 1.7. The other two branches here are our own example values.', set: { mode: 'exp', pat: 'emm', b: 3, leaves: '6 8 7 3 5 9 4 6 8 5 4 2 1 7 2 3 4 5 2 9 4 6 1 7 3 8 5', probs: '0.5 0.4 0.1' }, play: true }
    ],
    frames(p, z) {
      const G = buildGame(p);
      if (p.mode !== 'exp' && G.pat.includes('chance')) throw new Error('This layer pattern has chance nodes. Choose "Expectimax and expectiminimax" as the algorithm, or a MAX and MIN pattern.');
      z.state.G = G;
      const fr = [];
      const st = {};   /* per node name: value, alpha, beta, pruned */
      const leafKey = (n) => n;
      const vals = new Map(), ab = new Map(), pruned = new Set(), seen = new Set();
      const snap = (say, cur, extra = {}) => fr.push(Object.assign({ vals: new Map(vals), ab: new Map(ab), pruned: new Set(pruned), seen: new Set(seen), cur, say }, extra));
      const kidsVals = n => n.kids.map(k => fv(vals.get(k))).join(', ');
      snap(`Here is the game tree. ${G.pat.map(t => t.toUpperCase()).join(', then ')}, then the leaves.${G.warn} We work from the leaves back up to the root A.`, null);
      const markPruned = n => { pruned.add(n); (n.kids || []).forEach(markPruned); };
      if (p.mode === 'minimax' || p.mode === 'exp') {
        const rec = n => {
          if (n.leaf) { vals.set(n, n.v); seen.add(n); return n.v; }
          n.kids.forEach(rec);
          let v;
          if (n.type === 'max') v = Math.max(...n.kids.map(k => vals.get(k)));
          else if (n.type === 'min') v = Math.min(...n.kids.map(k => vals.get(k)));
          else v = n.kids.reduce((s, k, i) => s + G.probs[i] * vals.get(k), 0);
          vals.set(n, v); seen.add(n);
          const how = n.type === 'max' ? `MAX picks the largest` : n.type === 'min' ? `MIN picks the smallest` : `a chance node averages: ${n.kids.map((k, i) => `${fmt(G.probs[i], 3)} × ${fv(vals.get(k))}`).join(' + ')}`;
          snap(`${n.name} is a ${n.type.toUpperCase()} node. Its children are worth ${kidsVals(n)}. ${how}: <b>${fv(v)}</b>.`, n);
          return v;
        };
        rec(G.root);
      } else {
        const rec = (n, a, b) => {
          if (n.leaf) { vals.set(n, n.v); seen.add(n); snap(`Read the leaf: ${n.v}.`, n); return n.v; }
          ab.set(n, [a, b]); seen.add(n);
          snap(`Enter ${n.name} (${n.type.toUpperCase()}) with α = ${fv(a)} and β = ${fv(b)} passed down from its parent.`, n);
          let v = n.type === 'max' ? -Infinity : Infinity;
          for (let i = 0; i < n.kids.length; i++) {
            const cv = rec(n.kids[i], a, b);
            if (n.type === 'max') { v = Math.max(v, cv); a = Math.max(a, v); } else { v = Math.min(v, cv); b = Math.min(b, v); }
            vals.set(n, v); ab.set(n, [a, b]);
            const rest = n.kids.slice(i + 1);
            if (a >= b && rest.length) {
              rest.forEach(markPruned);
              snap(`${n.name} gets ${fv(cv)} from a child, so its value is now ${fv(v)} and ${n.type === 'max' ? 'α' : 'β'} = ${fv(n.type === 'max' ? a : b)}. Now α = ${fv(a)} ≥ β = ${fv(b)}: ${n.type === 'max' ? 'MIN above would never let play reach here' : 'MAX above already has something at least as good'}, so <b>prune</b> the remaining ${rest.length} child${rest.length > 1 ? 'ren' : ''}.`, n);
              break;
            }
            snap(`${n.name} gets ${fv(cv)} from child ${i + 1}. ${n.type === 'max' ? `Value = max so far = ${fv(v)}, α = ${fv(a)}` : `Value = min so far = ${fv(v)}, β = ${fv(b)}`}. α = ${fv(a)} < β = ${fv(b)}, so keep looking.`, n);
          }
          return v;
        };
        rec(G.root, -Infinity, Infinity);
      }
      /* the principal variation */
      const pv = [];
      let n = G.root;
      while (!n.leaf) { pv.push(n); if (n.type === 'chance') break; const want = vals.get(n); const k = n.kids.find(c => !pruned.has(c) && vals.get(c) === want); if (!k) break; n = k; }
      if (n.leaf) pv.push(n);
      const leavesAll = [];
      const coll = x => { if (x.leaf) leavesAll.push(x); else x.kids.forEach(coll); };
      coll(G.root);
      const np = leavesAll.filter(x => pruned.has(x)).length;
      const best = G.root.kids.findIndex(c => vals.get(c) === vals.get(G.root));
      snap(`The root A is worth <b>${fv(vals.get(G.root))}</b>. MAX should play move ${best + 1} (towards ${G.root.kids[best].name}).${p.mode === 'ab' ? ` Alpha beta looked at ${leavesAll.length - np} of ${leavesAll.length} leaves and pruned ${np}, yet gives the same answer as minimax.` : ''}`, null, { pv });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col, G = z.state.G;
      const root = G.root;
      const toT = n => ({ label: n.leaf ? String(n.v) : n.name, kind: 'x', ref: n, kids: n.leaf ? [] : n.kids.map(k => ({ node: toT(k) })) });
      const T = toT(root);
      const depth = G.pat.length;
      layoutTree(T, 22, z.W - 22, 34, Math.min(80, (z.H - 70) / depth));
      const on = n => f.pv && f.pv.includes(n);
      const drawE = t => t.kids.forEach(k => { const pr = f.pruned.has(k.node.ref); D.line(g, t.x, t.y, k.node.x, k.node.y, on(t.ref) && on(k.node.ref) ? c.green : pr ? c.line : c.ink2, on(t.ref) && on(k.node.ref) ? 3.5 : 1.3, pr ? [4, 4] : null); if (pr && !f.pruned.has(t.ref)) { const mx = (t.x + k.node.x) / 2, my = (t.y + k.node.y) / 2; D.text(g, '✕', mx, my + 4, { a: 'center', s: 12, b: true, c: c.red }); } drawE(k.node); });
      drawE(T);
      const leafW = Math.min(22, (z.W - 44) / Math.pow(z.p.b, depth) - 2);
      const drawN = t => {
        const n = t.ref, cur = f.cur === n, pr = f.pruned.has(n);
        if (n.leaf) {
          const seen = f.seen.has(n);
          rr(g, t.x - leafW / 2, t.y - 9, leafW, 18, 4, { fill: cur ? c.cv : pr ? c.bg : seen ? c.surf : c.bg, stroke: on(n) ? c.green : c.line, w: on(n) ? 2.5 : 1 });
          D.text(g, String(n.v), t.x, t.y + 1, { a: 'center', bl: 'middle', s: leafW < 18 ? 9.5 : 11, b: true, mono: true, c: cur ? '#fff' : pr ? c.ink2 : c.ink });
        } else {
          const col = cur ? c.cv : on(n) ? c.green : pr ? c.line : c.ink;
          g.save(); g.fillStyle = col; g.beginPath();
          if (n.type === 'max') { g.moveTo(t.x, t.y - 11); g.lineTo(t.x + 11, t.y + 8); g.lineTo(t.x - 11, t.y + 8); }
          else if (n.type === 'min') { g.moveTo(t.x, t.y + 11); g.lineTo(t.x + 11, t.y - 8); g.lineTo(t.x - 11, t.y - 8); }
          else g.arc(t.x, t.y, 10, 0, Math.PI * 2);
          g.closePath(); g.fill(); g.restore();
          const v = f.vals.get(n);
          if (v !== undefined) tag(g, fv(v), t.x + 22, t.y - 2, { s: 10.5, fill: c.yellow, stroke: c.yellow, c: '#1f1300', mono: true });
          const abv = f.ab.get(n);
          if (abv && z.p.mode === 'ab') D.text(g, `α ${fv(abv[0])} β ${fv(abv[1])}`, t.x, t.y - 16, { a: 'center', s: 9.5, c: c.cv, mono: true, b: true });
          if (n.depth === 0) D.text(g, n.name, t.x - 18, t.y + 4, { a: 'right', s: 11, b: true, c: c.ink2 });
        }
        t.kids.forEach(k => drawN(k.node));
      };
      drawN(T);
    }
  });

  /* =====================================================================================================
     6.3  Monte Carlo tree search: UCB1 at the root
     ===================================================================================================== */
  trace('mcts', {
    title: 'Monte Carlo tree search at the root: select, simulate, back up',
    sub: 'Three possible moves with hidden chances of winning. Each round picks a move by UCB1, plays one random game, and updates its record.',
    W: 600, H: 300,
    params: [
      { k: 'p1', label: 'Hidden win chance of move 1', type: 'range', v: 0.3, min: 0, max: 1, step: 0.05 },
      { k: 'p2', label: 'Hidden win chance of move 2', type: 'range', v: 0.6, min: 0, max: 1, step: 0.05 },
      { k: 'p3', label: 'Hidden win chance of move 3', type: 'range', v: 0.45, min: 0, max: 1, step: 0.05 },
      { k: 'C', label: 'Exploration constant C', type: 'range', v: 1.4, min: 0, max: 3, step: 0.1 },
      { k: 'N', label: 'Rounds', type: 'range', v: 20, min: 3, max: 40 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 4, min: 1, max: 50 }
    ],
    tips: [
      { t: 'C = 1.4. After the first three rounds (each move tried once) the search spends most rounds on move 2, the best move, but still checks the others now and then.', set: { C: 1.4 }, play: true },
      { t: 'C = 0 means no exploration. One unlucky early loss can make it ignore the best move for a long time.', set: { C: 0 }, play: true }
    ],
    frames(p) {
      const P = [p.p1, p.p2, p.p3], r = CVZ.rng(p.seed * 13 + 5);
      const w = [0, 0, 0], n = [0, 0, 0];
      const fr = [];
      fr.push({ w: w.slice(), n: n.slice(), ucb: [null, null, null], say: 'The root has three moves. We do not know their real chances of winning, so we learn them by playing random games (rollouts) from each.' });
      for (let t = 1; t <= p.N; t++) {
        const tot = n[0] + n[1] + n[2];
        const ucb = n.map((ni, i) => ni ? w[i] / ni + p.C * Math.sqrt(Math.log(tot) / ni) : Infinity);
        let pick = ucb.indexOf(Math.max(...ucb));
        const win = r() < P[pick] ? 1 : 0;
        n[pick]++; w[pick] += win;
        fr.push({ w: w.slice(), n: n.slice(), ucb, pick, win, say: `Round ${t}. Selection: ${n.some((x, i) => i !== pick && !x) || ucb[pick] === Infinity ? 'an untried move is always picked first' : `UCB1 = wins ⁄ visits + C × √(ln N ⁄ visits) gives ${ucb.map(fv).join(', ')}, so pick move ${pick + 1}`}. Simulation: a random game from move ${pick + 1} ends in a <b>${win ? 'win' : 'loss'}</b>. Back up: move ${pick + 1} now has ${w[pick]} wins in ${n[pick]} visits.` });
      }
      const best = n.indexOf(Math.max(...n));
      fr.push({ w: w.slice(), n: n.slice(), ucb: [null, null, null], pick: best, say: `After ${p.N} rounds, play the move with the most visits: <b>move ${best + 1}</b> (${n[best]} visits). The true best is move ${P.indexOf(Math.max(...P)) + 1}.` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      node(z, 300, 40, '', 'cur', { r: 16, inside: 'root', is: 10 });
      [120, 300, 480].forEach((x, i) => {
        D.line(g, 300, 56, x, 120, f.pick === i ? c.cv : c.line, f.pick === i ? 3 : 1.5);
        node(z, x, 136, '', f.pick === i ? 'cur' : 'idle', { r: 16, inside: 'm' + (i + 1), is: 11 });
        D.text(g, `${f.w[i]} / ${f.n[i]} wins`, x, 176, { a: 'center', s: 12, b: true, c: c.ink, mono: true });
        if (f.ucb[i] !== null && f.ucb[i] !== undefined) D.text(g, 'UCB ' + fv(f.ucb[i]), x, 194, { a: 'center', s: 11, c: c.cv, mono: true });
        const h = Math.min(70, f.n[i] * 4);
        D.rect(g, x - 18, 280 - h, 36, h, { fill: c.cv });
        D.text(g, 'visits', x - 28, 280, { a: 'right', s: 9.5, c: c.ink2 });
        if (f.win !== undefined && f.pick === i) tag(g, f.win ? 'win' : 'loss', x + 40, 136, { s: 11, fill: f.win ? c.green : c.red, stroke: f.win ? c.green : c.red, c: '#fff' });
      });
    }
  });

  return { trace, node, COL, COLNAME, list, nums, fv, _paintRo: paintRo, esc };
})();
