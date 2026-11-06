/* ===== Core AI animations, part 2: AND OR search, logic, planning, probability and reinforcement learning.
   Same rules as part 1 (assets/coreai.js): every animation starts empty and each Step adds one explained piece. ===== */
(() => {
  const { trace, esc } = CAI;
  const { D } = CVZ;
  const { tag, rr, tw, fit, wrap } = AIZ;

  /* =====================================================================================================
     3.4  AND OR search in the erratic and slippery vacuum worlds (AIMA 4.3)
     ===================================================================================================== */
  /* state numbers of AIMA figure 4.9: [location, A dirty, B dirty] */
  const VS = { 1: ['A', 1, 1], 2: ['B', 1, 1], 3: ['A', 1, 0], 4: ['B', 1, 0], 5: ['A', 0, 1], 6: ['B', 0, 1], 7: ['A', 0, 0], 8: ['B', 0, 0] };
  const vnum = (l, a, b) => +Object.keys(VS).find(k => VS[k][0] === l && VS[k][1] === a && VS[k][2] === b);
  function vres(s, act, world) {
    const [l, a, b] = VS[s];
    const here = l === 'A' ? a : b;
    if (act === 'Suck') {
      const clean = l === 'A' ? vnum(l, 0, b) : vnum(l, a, 0);
      if (world !== 'erratic') return [clean];
      if (here) { const both = vnum(l, 0, 0); return clean === both ? [clean] : [clean, both]; }
      const dirty = l === 'A' ? vnum(l, 1, b) : vnum(l, a, 1);
      return [s, dirty];
    }
    const to = act === 'Right' ? vnum('B', a, b) : vnum('A', a, b);
    if (world === 'slippery' && to !== s) return [to, s];
    return [to];
  }
  const goalV = s => s === 7 || s === 8;
  function planStr(pl) {
    if (!pl.length) return '[]';
    return '[' + pl.map(x => typeof x === 'string' ? x : x.map((c, i) => i === x.length - 1 ? `else ${planStr(c.p)}` : `${i ? 'else if' : 'if'} State = ${c.s} then ${planStr(c.p)}`).join(' ')).join(', ') + ']';
  }
  trace('andor', {
    title: 'AND OR search for a plan that works whatever happens',
    sub: 'OR rows: the agent picks one action. AND rows: nature picks the outcome, so every outcome needs its own plan. The little picture shows squares A and B, dirt as brown dots and the robot as a blue dot.',
    W: 600, H: 430,
    params: [
      { k: 'world', label: 'World', type: 'select', v: 'erratic', opts: [['erratic', 'Erratic vacuum: Suck sometimes also cleans the other square, or drops dirt on a clean one'], ['slippery', 'Slippery vacuum: Left and Right sometimes fail'], ['det', 'Ordinary vacuum: every action does exactly one thing']] },
      { k: 's', label: 'Start state (1 to 8, numbered as in the textbook)', type: 'range', v: 1, min: 1, max: 8 }
    ],
    tips: [
      { t: 'The textbook example. From state 1, Suck leads to 5 or 7. State 7 is a goal. For 5, Suck could make things worse (back to 1, a loop), so the search tries Right and then Suck. The plan: [Suck, if State = 5 then [Right, Suck] else []].', set: { world: 'erratic', s: 1 }, play: true },
      { t: 'The slippery world. Right may leave the robot where it is, so every plan runs into a state already on its path, and AND OR search finds no plan without loops. A cyclic plan with a label does work: keep trying Right until it succeeds.', set: { world: 'slippery', s: 1 }, play: true },
      { t: 'The ordinary world. Every AND node has just one outcome, so AND OR search is plain depth first search and the plan is a simple list of actions.', set: { world: 'det', s: 1 }, play: true }
    ],
    frames(p) {
      const rows = [], fr = [];
      const snap = (say, cur) => fr.push({ rows: rows.map(r => ({ ...r })), cur, say });
      const W = p.world;
      let guard = 0;
      function orS(s, path, d) {
        const row = { d, kind: 'or', s, st: 'open', txt: '' };
        rows.push(row); const me = rows.length - 1;
        if (guard++ > 60) { row.st = 'fail'; row.txt = 'stopped, too long'; return null; }
        if (goalV(s)) { row.st = 'goal'; row.txt = 'goal, nothing more to do'; snap(`OR node: state ${s}. Both squares are clean, so this is a goal. The plan here is the empty plan [].`, me); return []; }
        if (path.includes(s)) { row.st = 'loop'; row.txt = 'already on this path: a loop, give up here'; snap(`OR node: state ${s} is already on the path from the start (${path.slice().reverse().join(', ')}). Going on would loop, so this branch fails.`, me); return null; }
        snap(`OR node: state ${s}. It is not a goal. The agent may choose any action, so try them in the order Suck, Right, Left until one works.`, me);
        for (const a of ['Suck', 'Right', 'Left']) {
          const res = vres(s, a, W);
          const plan = andS(res, [s].concat(path), d + 1, a, s);
          if (plan) { row.st = 'ok'; row.txt = 'solved by ' + a; row.plan = [a].concat(plan); snap(`Back at state ${s}: action <b>${a}</b> works for every outcome, so the plan from ${s} is ${esc(planStr(row.plan))}.`, me); return row.plan; }
        }
        row.st = 'fail'; row.txt = 'no action works';
        snap(`Back at state ${s}: no action leads to a plan, so state ${s} fails.`, me);
        return null;
      }
      function andS(res, path, d, a, from) {
        const row = { d, kind: 'and', st: 'open', txt: `${a} from ${from} gives {${res.join(', ')}}` };
        rows.push(row); const me = rows.length - 1;
        snap(`AND node: doing ${a} in state ${from} can end in ${res.length === 1 ? 'only state ' + res[0] : 'state ' + res.join(' or state ')}. ${res.length > 1 ? 'We cannot choose which, so we need a plan for every one of them.' : 'There is just one outcome.'}`, me);
        const parts = [];
        for (const s of res) {
          const pl = orS(s, path, d + 1);
          if (!pl) { row.st = 'fail'; snap(`AND node fails: state ${s} has no plan, so ${a} from ${from} cannot be trusted.`, me); return null; }
          parts.push({ s, p: pl });
        }
        row.st = 'ok';
        snap(`AND node solved: every outcome of ${a} from ${from} has a plan.`, me);
        return parts.length === 1 ? parts[0].p : [parts];
      }
      const plan = orS(p.s, [], 0);
      if (plan) snap(`Done. The conditional plan from state ${p.s} is <b>${esc(planStr(plan))}</b>. It reaches a clean world whatever the outcomes turn out to be.`, 0);
      else if (W === 'slippery') snap(`AND OR search fails: every plan meets a state already on its path. No plan without loops exists. A <b>cyclic plan</b> does exist, for example from state 1: [Suck, L1: Right, if State = 5 then L1 else Suck]. It keeps trying Right, and it works as long as each try has some chance to succeed.`, 0);
      else snap('AND OR search fails: no plan reaches a goal from this state for every outcome.', 0);
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const MAXR = 20, H0 = 24, RH = 19.5;
      let rows = f.rows, off = 0;
      if (rows.length > MAXR) { off = rows.length - MAXR; rows = rows.slice(off); D.text(g, `(${off} earlier rows above, open "Earlier steps" to read them)`, 20, 14, { s: 10.5, c: c.ink2 }); }
      rows.forEach((r, i) => {
        const y = H0 + i * RH + 8, x = 16 + r.d * 22;
        const col = r.st === 'ok' || r.st === 'goal' ? c.green : r.st === 'fail' || r.st === 'loop' ? c.red : c.orange;
        if (r.d > 0) D.line(g, x - 12, y - RH + 6, x - 12, y, c.line, 1), D.line(g, x - 12, y, x - 2, y, c.line, 1);
        const cur = i + off === f.cur;
        if (r.kind === 'or') {
          const [l, a, b] = VS[r.s];
          [['A', a], ['B', b]].forEach(([q, dirty], k) => {
            const bx = x + k * 15;
            g.save(); g.fillStyle = c.bg; g.strokeStyle = cur ? c.cv : c.line; g.lineWidth = cur ? 2 : 1; g.fillRect(bx, y - 7, 14, 14); g.strokeRect(bx, y - 7, 14, 14); g.restore();
            if (dirty) { D.circle(g, bx + 4, y + 3, 2, { fill: '#92400e' }); D.circle(g, bx + 10, y - 2, 2, { fill: '#92400e' }); }
            if (l === q) D.circle(g, bx + 7, y, 3.5, { fill: c.cv });
          });
          D.text(g, 'state ' + r.s, x + 36, y + 4, { s: 12, b: true, c: cur ? c.cv : c.ink });
          if (r.txt) D.text(g, r.txt, x + 92, y + 4, { s: 11, c: col, b: r.st !== 'open' });
        } else {
          D.circle(g, x + 7, y, 7, { fill: c.surf, stroke: cur ? c.cv : col, w: cur ? 2.5 : 1.5 });
          D.text(g, '&', x + 7, y + 1, { a: 'center', bl: 'middle', s: 9, b: true, c: c.ink });
          D.text(g, r.txt, x + 20, y + 4, { s: 11.5, c: cur ? c.cv : c.ink2, b: cur });
          if (r.st !== 'open') D.text(g, r.st === 'ok' ? 'all outcomes solved' : 'fails', x + 26 + tw(g, r.txt, { s: 11.5, b: cur }), y + 4, { s: 11, b: true, c: col });
        }
      });
    }
  });
})();
