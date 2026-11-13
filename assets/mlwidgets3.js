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

/* =====================================================================================================
   Reinforcement 1.2  multi armed bandits: greedy, epsilon greedy and UCB pulls, and Thompson sampling posteriors
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, nums, rng, plot } = MLZ;
  const ruleName = { greedy: 'greedy', eps: 'ε greedy', ucb: 'UCB' };

  trace('mlbandit', {
    title: 'A multi armed bandit: which slot machine pays best?',
    sub: 'Each arm pays 1 with its own hidden chance and 0 otherwise. The agent keeps an estimate Q (the average payout so far) for every arm and decides which arm to pull next. Greedy always pulls the best estimate, ε greedy sometimes pulls at random, and UCB adds a bonus to arms it has tried less.',
    W: 600, H: 330,
    params: [
      { k: 'p', label: 'Hidden payout chance of each arm', type: 'text', v: '0.3 0.5 0.7 0.4' },
      { k: 'rule', label: 'Rule', type: 'select', v: 'eps', opts: [['greedy', 'Greedy'], ['eps', 'ε greedy'], ['ucb', 'UCB']] },
      { k: 'eps', label: 'ε (chance of a random arm)', type: 'range', v: 0.1, min: 0, max: 0.5, step: 0.05 },
      { k: 'c', label: 'UCB bonus size c', type: 'range', v: 1, min: 0.2, max: 3, step: 0.1 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 5, min: 1, max: 30 }
    ],
    tips: [
      { t: 'Greedy with seed 2: an early lucky payout fixes it on a worse arm, and it never checks the others again.', set: { p: '0.3 0.5 0.7 0.4', rule: 'greedy', seed: 2 }, play: true },
      { t: 'UCB: every arm is tried first, the orange bonus shrinks as an arm is pulled more, and the clearly worse arms get few pulls while the two best arms keep sharing them.', set: { p: '0.3 0.5 0.7 0.4', rule: 'ucb', c: 1, seed: 5 }, play: true }
    ],
    frames(p) {
      const P = nums(p.p).slice(0, 6);
      if (P.length < 2 || P.some(v => v < 0 || v > 1)) throw new Error('Type 2 to 6 chances between 0 and 1');
      const k = P.length, R = rng(+p.seed * 104729), eps = +p.eps, c = +p.c, best = Math.max(...P);
      const Q = Array(k).fill(0), N = Array(k).fill(0);
      let total = 0, regret = 0;
      const base = { P, rule: p.rule };
      const fr = [{ ...base, Q: Q.slice(), N: N.slice(), total, regret, t: 0, say: `${k} arms. Their payout chances are hidden from the agent (dashed marks show them to you). Every estimate starts at 0. The rule is <b>${ruleName[p.rule]}</b>.` }];
      const show = t => t <= 15 || t % 5 === 0;
      for (let t = 1; t <= 100; t++) {
        let a, why;
        const bonus = Q.map((q, i) => (N[i] ? c * Math.sqrt(Math.log(t) / N[i]) : Infinity));
        if (p.rule === 'ucb') {
          const sc = Q.map((q, i) => q + bonus[i]);
          a = sc.indexOf(Math.max(...sc));
          why = N[a] === 0 ? `arm ${a + 1} has never been pulled, so its bonus is unlimited` : `arm ${a + 1} has the highest Q + bonus = ${f2(Q[a], 2)} + ${f2(bonus[a], 2)}`;
        } else if (p.rule === 'eps' && R() < eps) {
          a = Math.floor(R() * k); why = `a random number fell below ε = ${f2(eps, 2)}, so it explores and picks arm ${a + 1} at random`;
        } else {
          const m = Math.max(...Q), ties = Q.map((q, i) => (q === m ? i : -1)).filter(i => i >= 0);
          a = ties[Math.floor(R() * ties.length)];
          why = ties.length > 1 ? `arms ${ties.map(i => i + 1).join(', ')} tie for the best estimate, so it picks arm ${a + 1}` : `arm ${a + 1} has the best estimate, ${f2(Q[a], 2)}`;
        }
        const r = R() < P[a] ? 1 : 0;
        N[a]++; Q[a] += (r - Q[a]) / N[a]; total += r; regret += best - P[a];
        if (show(t)) fr.push({ ...base, Q: Q.slice(), N: N.slice(), total, regret, t, a, r, bonus: p.rule === 'ucb' ? Q.map((q, i) => (N[i] ? c * Math.sqrt(Math.log(t + 1) / N[i]) : 0)) : null,
          say: t <= 15 ? `Pull ${t}: ${why}. It pays <b>${r}</b>. Q for arm ${a + 1} becomes ${f2(Q[a], 3)} after ${N[a]} pull${N[a] > 1 ? 's' : ''}.`
            : `After ${t} pulls: total payout ${total}, and the pulls per arm are ${N.join(', ')}. Regret so far ${f2(regret, 1)}: the payout lost on average against always pulling the best arm.${t === 100 ? (N[P.indexOf(best)] > 50 ? ' Most pulls went to the best arm.' : ' The best arm got only ' + N[P.indexOf(best)] + ' of the 100 pulls, so payout was lost while the agent was still testing.') : ''}` });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, k = f.P.length, bw = Math.min(70, 340 / k), x0 = 40, y0 = 40, H = 200;
      const Y = v => y0 + H - v * H;
      D.line(g, x0 - 6, Y(0), x0 + k * bw, Y(0), c.ink2, 1);
      [0, 0.5, 1].forEach(v => D.text(g, f2(v, 1), x0 - 10, Y(v) + 4, { a: 'right', s: 10, c: c.ink2 }));
      f.P.forEach((pv, i) => {
        const x = x0 + i * bw + 8, w = bw - 16;
        rr(g, x, Y(f.Q[i]), w, Math.max(1, f.Q[i] * H), 3, { fill: i === f.a ? klass(z, 0) : 'rgba(37,99,235,0.45)' });
        if (f.bonus && f.N[i]) { const top = Math.min(1.15, f.Q[i] + f.bonus[i]); rr(g, x, Y(top), w, (top - f.Q[i]) * H, 3, { fill: 'rgba(234,88,12,0.25)', stroke: klass(z, 1), w: 1 }); }
        D.line(g, x - 4, Y(pv), x + w + 4, Y(pv), c.ink, 2, [4, 3]);
        D.text(g, `arm ${i + 1}`, x + w / 2, Y(0) + 16, { a: 'center', s: 11, b: true, c: i === f.a ? klass(z, 0) : c.ink });
        D.text(g, `n ${f.N[i]}`, x + w / 2, Y(0) + 32, { a: 'center', s: 11, mono: true, c: c.ink2 });
        D.text(g, `Q ${f2(f.Q[i], 2)}`, x + w / 2, Y(0) + 48, { a: 'center', s: 11, mono: true, c: c.ink });
      });
      if (f.a !== undefined && f.t <= 15) D.text(g, f.r ? '+1' : '0', x0 + f.a * bw + bw / 2, Y(Math.max(f.Q[f.a], f.P[f.a])) - 10, { a: 'center', s: 14, b: true, c: f.r ? c.green : c.ink2 });
      const x = 420;
      head(z, ruleName[f.rule], x, 30);
      D.text(g, `pull ${f.t}`, x, 56, { s: 13, b: true, c: c.ink });
      D.text(g, `total payout ${f.total}`, x, 80, { s: 12, mono: true, c: c.green });
      D.text(g, `regret ${f2(f.regret, 1)}`, x, 102, { s: 12, mono: true, c: c.red });
      D.text(g, '▬ estimate Q', x, 140, { s: 11, c: klass(z, 0) });
      D.text(g, '- - hidden chance', x, 158, { s: 11, c: c.ink });
      if (f.rule === 'ucb') D.text(g, '▢ UCB bonus', x, 176, { s: 11, c: klass(z, 1) });
    }
  });

  /* Beta(a, b) with whole numbers a and b: the a-th smallest of a + b - 1 uniform numbers */
  const betaSample = (R, a, b) => { const u = Array.from({ length: a + b - 1 }, R).sort((x, y) => x - y); return u[a - 1]; };
  const lgam = x => { const c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.001208650973866179, -0.000005395239384953]; let y = x, t = x + 5.5; t -= (x + 0.5) * Math.log(t); let s = 1.000000000190015; c.forEach(v => { y += 1; s += v / y; }); return -t + Math.log(2.5066282746310005 * s / x); };
  const betaPdf = (x, a, b) => (x <= 0 || x >= 1 ? 0 : Math.exp((a - 1) * Math.log(x) + (b - 1) * Math.log(1 - x) + lgam(a + b) - lgam(a) - lgam(b)));

  trace('mlthompson', {
    title: 'Thompson sampling: pick by drawing from what you believe',
    sub: 'For each design we keep a Beta curve of plausible click rates, starting flat. Each visitor: draw one random rate from every curve, show the design whose draw is highest, see if the visitor clicks, and update that curve. Uncertain designs still get chances, and clear losers fade out.',
    W: 600, H: 330,
    params: [
      { k: 'p', label: 'Hidden click rate of each design', type: 'text', v: '0.3 0.45 0.6' },
      { k: 'seed', label: 'Random seed', type: 'range', v: 4, min: 1, max: 30 }
    ],
    tips: [
      { t: 'Two designs that are almost equal: both keep getting visitors for a long time, because the data cannot yet tell them apart.', set: { p: '0.5 0.52', seed: 3 }, play: true },
      { t: 'One clearly better design: it takes over after a few dozen visitors.', set: { p: '0.1 0.2 0.8', seed: 3 }, play: true }
    ],
    frames(p) {
      const P = nums(p.p).slice(0, 4);
      if (P.length < 2 || P.some(v => v <= 0 || v >= 1)) throw new Error('Type 2 to 4 click rates between 0 and 1');
      const k = P.length, R = rng(+p.seed * 7907), W = Array(k).fill(1), L = Array(k).fill(1);
      const base = { P };
      const fr = [{ ...base, W: W.slice(), L: L.slice(), t: 0, say: `${k} designs. Every curve starts flat, Beta(1, 1): any click rate from 0 to 1 is equally plausible. The dashed lines mark the hidden true rates.` }];
      const show = [1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 50, 100, 200];
      for (let t = 1; t <= 200; t++) {
        const draws = W.map((w, i) => betaSample(R, w, L[i])), a = draws.indexOf(Math.max(...draws)), click = R() < P[a] ? 1 : 0;
        if (click) W[a]++; else L[a]++;
        if (show.includes(t)) {
          const shown = W.map((w, i) => w + L[i] - 2);
          fr.push({ ...base, W: W.slice(), L: L.slice(), t, draws, a, click, say: t <= 6
            ? `Visitor ${t}: the draws are ${draws.map(d => f2(d, 2)).join(', ')}. Design ${a + 1} drew highest and is shown. The visitor ${click ? '<b>clicks</b>, so its curve moves right' : '<b>does not click</b>, so its curve moves left'}: now Beta(${W[a]}, ${L[a]}).`
            : `After ${t} visitors, the designs were shown ${shown.join(', ')} times. ${t >= 100 ? (Math.max(...shown) > 0.8 * t ? `Design ${shown.indexOf(Math.max(...shown)) + 1} took most of the visitors. Its curve is narrow, while rarely shown designs keep wide curves.` : 'No design dominates yet. The curves still overlap, so the data cannot tell the designs apart and they keep sharing visitors.') : 'Curves narrow as data piles up.'}` });
        }
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, xs = Array.from({ length: 101 }, (_, i) => i / 100);
      const curves = f.W.map((w, i) => xs.map(x => betaPdf(x, w, f.L[i])));
      const ymax = Math.max(1.5, ...curves.flat()) * 1.08;
      const Pl = plot(z, [10, 10, 400, 300], [0, 1], [0, ymax], { dx: 2, dy: 1, xl: 'click rate', yl: 'belief' });
      curves.forEach((cv, i) => {
        const col = klass(z, i);
        for (let j = 1; j < xs.length; j++) D.line(g, Pl.X(xs[j - 1]), Pl.Y(Math.min(cv[j - 1], ymax)), Pl.X(xs[j]), Pl.Y(Math.min(cv[j], ymax)), col, i === f.a ? 3 : 2);
        D.line(g, Pl.X(f.P[i]), Pl.Y(0), Pl.X(f.P[i]), Pl.Y(ymax * 0.95), col, 1, [4, 4]);
        if (f.draws && f.t <= 6) D.circle(g, Pl.X(f.draws[i]), Pl.Y(0) - 6, 5, { fill: col });
      });
      const x = 425;
      head(z, `visitor ${f.t}`, x, 30);
      f.W.forEach((w, i) => {
        const y = 58 + i * 46;
        D.text(g, `design ${i + 1}`, x, y, { s: 12, b: true, c: klass(z, i) });
        D.text(g, `Beta(${w}, ${f.L[i]})`, x, y + 16, { s: 11, mono: true, c: c.ink });
        D.text(g, `shown ${w + f.L[i] - 2}`, x + 92, y + 16, { s: 11, mono: true, c: c.ink2 });
      });
      if (f.draws && f.t <= 6) D.text(g, `dots: this visitor’s draws`, x, 260, { s: 11, c: c.ink2 });
    }
  });
})();
