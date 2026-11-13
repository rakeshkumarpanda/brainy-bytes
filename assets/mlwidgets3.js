/* ===== Complete Machine Learning animations, part 3: reinforcement learning, deep learning and MLOps.
   Uses the framework MLZ from assets/mlwidgets.js. Every animation starts empty and adds one step each time Step
   is pressed, with a plain English line for that step. ===== */

/* =====================================================================================================
   Reinforcement 1.1  agents, rewards and returns: the agent and environment loop on a corridor, and discounting
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, box, nums, rng } = MLZ;
  const nf = v => (Number.isInteger(v) ? String(v).replace('-', '−') : f2(v, 3));
  const sg = v => (v > 0 ? '+' : '') + nf(v);

  trace('mlagent', {
    title: 'The agent and environment loop on a corridor',
    sub: 'An agent stands in a corridor. The left end is a pit (−10), the right end holds treasure (+10), and every move costs −1. Each step the agent sees its cell (the state), picks left or right (the action), and the corridor answers with a reward and the next cell.',
    W: 600, H: 330,
    params: [
      { k: 'n', label: 'Corridor length (cells)', type: 'range', v: 6, min: 4, max: 9 },
      { k: 'p', label: 'Chance the policy picks right', type: 'range', v: 0.5, min: 0, max: 1, step: 0.05 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 3, min: 1, max: 30 }
    ],
    tips: [
      { t: 'A policy that always goes right: the shortest path to the treasure and the best total reward.', set: { n: 6, p: 1, seed: 3 }, play: true },
      { t: 'A long corridor with a random policy: the agent wanders back and forth, and the move costs eat almost all of the treasure.', set: { n: 9, p: 0.5, seed: 4 }, play: true }
    ],
    frames(p) {
      const n = +p.n, pr = +p.p, R = rng(+p.seed * 7919), start = Math.floor((n - 1) / 2), CAP = 30;
      let pos = start, total = 0;
      const log = [], base = { n, start };
      const fr = [{ ...base, pos, log: [], total, say: `A corridor of ${n} cells. The agent starts in cell ${start}. Its policy picks right with chance ${f2(pr, 2)} and left otherwise. The episode ends at the pit (cell 0) or the treasure (cell ${n - 1}).` }];
      for (let t = 1; t <= CAP; t++) {
        const a = R() < pr ? 1 : -1, s = pos;
        pos += a;
        const r = pos === n - 1 ? 10 : pos === 0 ? -10 : -1;
        total += r;
        log.push({ t, s, a, r, s2: pos });
        const end = pos === 0 || pos === n - 1;
        const say = `Step ${t}: in state ${s} the agent goes <b>${a > 0 ? 'right' : 'left'}</b>. The environment returns reward <b>${sg(r)}</b> and next state ${pos}. Total so far ${nf(total)}.` +
          (end ? (pos === n - 1 ? ` <b>Treasure!</b> The episode ends with total reward ${nf(total)}.` : ` <b>The pit.</b> The episode ends with total reward ${nf(total)}.`) : t === CAP ? ` We stop the episode after ${CAP} steps. This cut is called truncation.` : '');
        fr.push({ ...base, pos, log: log.slice(), total, last: r, act: a, end, say });
        if (end) break;
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, cw = Math.min(64, 560 / f.n), x0 = 300 - cw * f.n / 2, y0 = 28;
      for (let i = 0; i < f.n; i++) {
        const pit = i === 0, gold = i === f.n - 1;
        box(z, x0 + i * cw, y0, cw - 4, 50, '', { fill: pit ? 'rgba(220,38,38,0.18)' : gold ? 'rgba(22,163,74,0.18)' : c.surf, r: 6 });
        D.text(g, pit ? 'pit −10' : gold ? 'gold +10' : String(i), x0 + i * cw + cw / 2 - 2, y0 + 66, { a: 'center', s: 10, b: pit || gold, c: pit ? c.red : gold ? c.green : c.ink2 });
      }
      const ax = x0 + f.pos * cw + cw / 2 - 2;
      D.circle(g, ax, y0 + 25, 13, { fill: klass(z, 0) });
      D.text(g, 'A', ax, y0 + 30, { a: 'center', s: 13, b: true, c: '#fff' });
      if (f.act) D.text(g, f.act > 0 ? '→' : '←', ax - f.act * 22, y0 + 30, { a: 'center', s: 18, b: true, c: klass(z, 1) });
      /* the loop */
      const ly = 130;
      box(z, 30, ly, 110, 44, 'Agent', { fill: klass(z, 0), c: '#fff', b: true });
      box(z, 30, ly + 110, 110, 44, 'Environment', { fill: c.surf, b: true });
      D.line(g, 150, ly + 22, 190, ly + 22, c.ink2, 1.5); D.line(g, 190, ly + 22, 190, ly + 132, c.ink2, 1.5); D.line(g, 190, ly + 132, 150, ly + 132, c.ink2, 1.5);
      D.text(g, '◀', 146, ly + 137, { a: 'center', s: 12, c: c.ink2 }); D.text(g, '▶', 26, ly + 27, { a: 'center', s: 12, c: c.ink2 });
      D.text(g, 'action', 198, ly + 80, { s: 11, b: true, c: klass(z, 1) });
      D.line(g, 20, ly + 132, 10, ly + 132, c.ink2, 1.5); D.line(g, 10, ly + 132, 10, ly + 22, c.ink2, 1.5); D.line(g, 10, ly + 22, 24, ly + 22, c.ink2, 1.5);
      D.text(g, 'state, reward', 14, ly + 74, { s: 11, b: true, c: klass(z, 2) });
      /* the log */
      head(z, 'Step   state  action  reward  next', 270, ly - 6);
      f.log.slice(-7).forEach((e, i) => D.text(g, `${String(e.t).padStart(3)}     ${e.s}     ${e.a > 0 ? 'right' : 'left '}   ${(e.r > 0 ? '+' : '') + e.r}`.replace('-', '−').padEnd(32) + `${e.s2}`, 270, ly + 16 + i * 20, { s: 12, mono: true, c: e.r > 0 ? c.green : e.r < -1 ? c.red : c.ink }));
      D.text(g, `total reward ${nf(f.total)}`, 270, ly + 168, { s: 15, b: true, c: f.total > 0 ? c.green : f.total < 0 ? c.red : c.ink });
    }
  });

  trace('mlreturn', {
    title: 'The return: adding up future rewards with a discount',
    sub: 'The return G is the sum of all rewards from now on, where a reward k steps ahead is multiplied by γᵏ. A discount γ below 1 makes near rewards count more than far ones. We compute it backwards with G = r + γG.',
    W: 600, H: 330,
    params: [
      { k: 'r', label: 'Rewards of one episode, in order', type: 'text', v: '-1 -1 -1 10' },
      { k: 'g', label: 'Discount γ', type: 'range', v: 0.9, min: 0, max: 1, step: 0.05 }
    ],
    tips: [
      { t: 'γ = 0: the agent only cares about the very next reward, so the treasure at the end is invisible from the start.', set: { r: '-1 -1 -1 10', g: 0 }, play: true },
      { t: 'A big reward far away against a small one now: with γ = 0.5 the far reward of 20 is worth only 1.25 from the start.', set: { r: '2 0 0 0 20', g: 0.5 }, play: true }
    ],
    frames(p) {
      const r = nums(p.r).slice(0, 10), g = +p.g, T = r.length;
      if (!T) throw new Error('Type at least one reward');
      const G = Array(T).fill(null), base = { r, g };
      const fr = [{ ...base, G: G.slice(), say: `An episode with ${T} rewards: ${r.map(nf).join(', ')}. The plain sum is ${nf(r.reduce((a, b) => a + b, 0))}. With discount γ = ${f2(g, 2)}, a reward k steps ahead counts as γᵏ times its size.` }];
      fr.push({ ...base, G: G.slice(), w: true, say: `The weights seen from the first step are ${r.map((_, k) => f2(g ** k, 3)).join(', ')}. ${g < 1 ? 'They shrink the further ahead a reward is.' : 'With γ = 1 every reward counts fully.'}` });
      let acc = 0;
      for (let t = T - 1; t >= 0; t--) {
        const prev = acc;
        acc = r[t] + g * acc;
        G[t] = acc;
        fr.push({ ...base, G: G.slice(), w: true, cur: t, say: t === T - 1 ? `Start at the last step: nothing comes after it, so G<sub>${t + 1}</sub> = ${nf(r[t])}.` : `Step ${t + 1}: G = r + γ × (G of the next step) = ${nf(r[t])} + ${f2(g, 2)} × ${nf(prev)} = <b>${nf(acc)}</b>.` });
      }
      fr.push({ ...base, G: G.slice(), w: true, done: true, say: `The return from the start is <b>${nf(G[0])}</b>, against a plain sum of ${nf(r.reduce((a, b) => a + b, 0))}. Reinforcement learning chooses actions to make this expected return as large as possible.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, T = f.r.length, cw = Math.min(56, 360 / T), x0 = 40, zero = 120;
      const mx = Math.max(1, ...f.r.map(Math.abs), ...f.G.filter(v => v !== null).map(Math.abs));
      const sc = 80 / mx;
      D.line(g, x0 - 10, zero, x0 + T * cw, zero, c.ink2, 1);
      D.text(g, '0', x0 - 14, zero + 4, { a: 'right', s: 10, c: c.ink2 });
      f.r.forEach((v, t) => {
        const x = x0 + t * cw, h = v * sc;
        rr(g, x + 4, h >= 0 ? zero - h : zero, cw - 8, Math.max(1, Math.abs(h)), 3, { fill: v >= 0 ? klass(z, 2) : c.red });
        D.text(g, f2(v, v % 1 ? 1 : 0), x + cw / 2, h >= 0 ? zero - h - 5 : zero - h + 13, { a: 'center', s: 11, b: true, c: c.ink });
        D.text(g, 't = ' + (t + 1), x + cw / 2, 228, { a: 'center', s: 10, c: c.ink2 });
        if (f.w) D.text(g, f2(f.g ** t, 2), x + cw / 2, 252, { a: 'center', s: 11, mono: true, c: klass(z, 1) });
        if (f.G[t] !== null) box(z, x + 3, 266, cw - 6, 26, f2(f.G[t], 2), { fill: t === f.cur ? klass(z, 0) : c.surf, c: t === f.cur ? '#fff' : c.ink, s: 11, mono: true, r: 4 });
      });
      D.text(g, 'reward', 4, 40, { s: 11, b: true, c: c.ink2 });
      if (f.w) D.text(g, 'γᵏ', 4, 252, { s: 11, b: true, c: klass(z, 1) });
      if (f.G.some(v => v !== null)) D.text(g, 'G', 4, 284, { s: 12, b: true, c: klass(z, 0) });
      const x = 425;
      head(z, 'Formula', x, 26);
      D.text(g, 'G = r₁ + γr₂ + γ²r₃ …', x, 50, { s: 11, mono: true, c: c.ink });
      D.text(g, 'G = r + γ · G(next)', x, 72, { s: 11, mono: true, b: true, c: c.cv });
      D.text(g, `γ = ${f2(f.g, 2)}`, x, 104, { s: 14, b: true, c: klass(z, 1) });
      D.text(g, `plain sum ${nf(f.r.reduce((a, b) => a + b, 0))}`, x, 130, { s: 12, mono: true, c: c.ink });
      if (f.done) D.text(g, `return ${nf(f.G[0])}`, x, 156, { s: 15, b: true, c: klass(z, 0) });
    }
  });
})();
