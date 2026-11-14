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

/* =====================================================================================================
   Reinforcement 1.3  Markov chains and the Bellman equation: a weather chain walk, and value backups on a small MRP
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, rng } = MLZ;
  const nf = v => (Number.isInteger(v) ? String(v).replace('-', '−') : f2(v, 3));
  function parseP(s, n) {
    const P = String(s).split(/[;\n]+/).map(r => r.trim()).filter(Boolean).map(r => r.split(/[\s,]+/).map(Number));
    if (P.length !== n || P.some(r => r.length !== n || r.some(v => isNaN(v) || v < 0))) throw new Error(`Type ${n} rows of ${n} chances, one row per state`);
    P.forEach((r, i) => { if (Math.abs(r.reduce((a, b) => a + b, 0) - 1) > 0.011) throw new Error(`Row ${i + 1} must add up to 1`); });
    return P;
  }
  /* an arrow from node a to node b, pushed sideways so that a and b can have arrows both ways */
  function link(z, A, B, rad, label, col, w) {
    const g = z.g, dx = B.x - A.x, dy = B.y - A.y, L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, ox = -uy * 7, oy = ux * 7;
    D.arrow(g, A.x + ux * rad + ox, A.y + uy * rad + oy, B.x - ux * rad + ox, B.y - uy * rad + oy, col, w, 8);
    if (label) D.text(g, label, (A.x + B.x) / 2 + ox * 2.6, (A.y + B.y) / 2 + oy * 2.6 + 4, { a: 'center', s: 11, b: true, c: col });
  }
  function loop(z, A, rad, label, col, w, up = true) {
    const g = z.g, cy = up ? A.y - rad - 12 : A.y + rad + 12;
    g.save(); g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.arc(A.x, cy, 12, 0, Math.PI * 2); g.stroke(); g.restore();
    if (label) D.text(g, label, A.x + 18, cy + (up ? -6 : 14), { s: 11, b: true, c: col });
  }

  const WEATHER = ['sunny', 'cloudy', 'rainy'];
  trace('mlmarkov', {
    title: 'A Markov chain: tomorrow depends only on today',
    sub: 'Three kinds of weather. Each arrow gives the chance of moving from today’s weather to tomorrow’s. We walk the chain one day at a time and count how often each state comes up. In the long run the shares settle at the stationary distribution, whatever the starting day.',
    W: 600, H: 330,
    params: [
      { k: 'P', label: 'Transition chances (row = today: sunny, cloudy, rainy)', type: 'area', v: '0.7 0.2 0.1; 0.3 0.4 0.3; 0.2 0.4 0.4' },
      { k: 'seed', label: 'Random seed', type: 'range', v: 4, min: 1, max: 30 }
    ],
    tips: [
      { t: 'Sticky weather: each state keeps itself with chance 0.9, so the walk stays in long runs and even 5,000 days are not enough for the shares to settle.', set: { P: '0.9 0.05 0.05; 0.05 0.9 0.05; 0.05 0.05 0.9', seed: 2 }, play: true },
      { t: 'A chain that never rains after sunshine: the shares still settle, just at different values.', set: { P: '0.6 0.4 0; 0.3 0.3 0.4; 0.5 0.3 0.2', seed: 2 }, play: true }
    ],
    frames(p) {
      const P = parseP(p.P, 3), R = rng(+p.seed * 6151);
      let pi = [1 / 3, 1 / 3, 1 / 3];
      for (let i = 0; i < 2000; i++) pi = [0, 1, 2].map(j => pi.reduce((a, v, k) => a + v * P[k][j], 0));
      let s = 0;
      const cnt = [0, 0, 0], base = { P, pi };
      const fr = [{ ...base, s, cnt: cnt.slice(), day: 0, say: 'Day 0 is sunny. Each row of chances adds up to 1. The next day depends only on today, not on the days before: this is the <b>Markov property</b>.' }];
      const show = [1, 2, 3, 4, 5, 6, 7, 8, 10, 20, 50, 100, 500, 5000];
      cnt[0] = 1;
      for (let d = 1; d <= 5000; d++) {
        const u = R(), prev = s;
        s = u < P[s][0] ? 0 : u < P[s][0] + P[s][1] ? 1 : 2;
        cnt[s]++;
        if (show.includes(d)) {
          const sh = cnt.map(c => c / (d + 1));
          fr.push({ ...base, s, prev: d <= 8 ? prev : undefined, cnt: cnt.slice(), day: d, say: d <= 8
            ? `Day ${d}: from ${WEATHER[prev]}, the chances are ${P[prev].map(v => f2(v, 2)).join(', ')}. The walk lands on <b>${WEATHER[s]}</b>.`
            : `After ${d} days the shares are ${sh.map(v => f2(v, 3)).join(', ')}.${d === 5000 ? ` The stationary distribution π, solving π = πP, is ${pi.map(v => f2(v, 3)).join(', ')}. ${Math.max(...sh.map((v, i) => Math.abs(v - pi[i]))) < 0.02 ? 'The long walk matches it closely.' : 'The walk is near it but not there yet: a chain that stays in long runs needs a much longer walk.'}` : ''}` });
        }
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, N = [{ x: 80, y: 90 }, { x: 300, y: 90 }, { x: 190, y: 250 }], rad = 30;
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
        if (!f.P[i][j]) continue;
        const hot = f.prev === i && f.s === j, col = hot ? klass(z, 1) : c.ink2, w = hot ? 3 : 1.4;
        if (i === j) loop(z, N[i], rad, f2(f.P[i][j], 2), col, w, i < 2); else link(z, N[i], N[j], rad, f2(f.P[i][j], 2), col, w);
      }
      N.forEach((q, i) => {
        D.circle(g, q.x, q.y, rad, { fill: i === f.s ? klass(z, 0) : c.surf, stroke: c.ink2, w: 1.5 });
        D.text(g, WEATHER[i], q.x, q.y + 5, { a: 'center', s: 12, b: true, c: i === f.s ? '#fff' : c.ink });
      });
      const x = 420, tot = f.cnt.reduce((a, b) => a + b, 0);
      head(z, `day ${f.day}`, x, 30);
      D.text(g, 'share of days so far', x, 54, { s: 11, c: c.ink2 });
      WEATHER.forEach((w, i) => {
        const y = 74 + i * 52, sh = f.cnt[i] / tot;
        D.text(g, w, x, y + 12, { s: 12, b: true, c: c.ink });
        rr(g, x + 56, y, 110 * sh, 16, 3, { fill: klass(z, i) });
        D.line(g, x + 56 + 110 * f.pi[i], y - 4, x + 56 + 110 * f.pi[i], y + 20, c.ink, 2, [3, 2]);
        D.text(g, f2(sh, 2), x + 56, y + 32, { s: 11, mono: true, c: c.ink });
      });
      D.text(g, '- - stationary π', x, 250, { s: 11, c: c.ink });
    }
  });

  const MRP = { names: ['Wake', 'Gym', 'Work', 'Couch', 'End'], pos: [{ x: 60, y: 150 }, { x: 175, y: 60 }, { x: 320, y: 95 }, { x: 175, y: 255 }, { x: 330, y: 255 }],
    P: [[0, 0.5, 0, 0.5, 0], [0, 0, 0.8, 0.2, 0], [0, 0, 0, 0.4, 0.6], [0.4, 0, 0, 0.6, 0], [0, 0, 0, 0, 1]] };
  trace('mlbackup', {
    title: 'The Bellman equation: a value from rewards and the values next door',
    sub: 'A day as a Markov reward process. Each state gives a reward when you leave it, and arrows show where you go next. The value V(s) is the expected discounted return from s. The Bellman equation V(s) = R(s) + γ Σ P(s′|s) V(s′) links each value to its neighbours, and repeating it as an update finds every value.',
    W: 600, H: 330,
    params: [
      { k: 'g', label: 'Discount γ', type: 'range', v: 0.9, min: 0, max: 0.99, step: 0.01 },
      { k: 'rw', label: 'Reward for leaving Work', type: 'range', v: 10, min: -5, max: 20 }
    ],
    tips: [
      { t: 'γ = 0: every value is just its own reward, since nothing after the next step counts.', set: { g: 0, rw: 10 }, play: true },
      { t: 'Work pays nothing: every value turns negative, and Couch is worst because it keeps looping.', set: { g: 0.9, rw: 0 }, play: true }
    ],
    frames(p) {
      const g = +p.g, R = [-1, -2, +p.rw, -1, 0], n = 5;
      let V = Array(n).fill(0);
      const base = { g, R };
      const fr = [{ ...base, V: null, say: `Five states. Rewards: Wake −1, Gym −2, Work ${nf(R[2])}, Couch −1, End 0 (the day is over and End keeps you forever with no reward). γ = ${f2(g, 2)}.` }];
      fr.push({ ...base, V: V.slice(), say: 'Start with every value at 0. Each sweep replaces every V(s) with R(s) + γ × (the average of the next values, weighted by the arrows).' });
      const show = [1, 2, 3, 5, 10, 30, 100];
      for (let k = 1; k <= 100; k++) {
        const old = V;
        V = R.map((r, s) => (s === 4 ? 0 : r + g * MRP.P[s].reduce((a, pv, t) => a + pv * old[t], 0)));
        if (show.includes(k)) {
          const s = k === 1 ? 2 : k === 2 ? 1 : 0;
          const terms = MRP.P[s].map((pv, t) => (pv ? `${f2(pv, 1)} × ${old[t] < 0 ? '(' + f2(old[t], 2) + ')' : f2(old[t], 2)}` : null)).filter(Boolean).join(' + ');
          fr.push({ ...base, V: V.slice(), k, hot: k <= 3 ? s : undefined, say: k <= 3
            ? `Sweep ${k}. For example V(${MRP.names[s]}) = ${nf(R[s])} + ${f2(g, 2)} × (${terms}) = <b>${f2(V[s], 3)}</b>.`
            : `After ${k} sweeps the values are ${V.slice(0, 4).map((v, i) => MRP.names[i] + ' ' + f2(v, 2)).join(', ')}.${k === 100 ? ' They have stopped changing: these are the exact solution of the Bellman equation.' : ''}` });
        }
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, rad = 28, Np = MRP.pos;
      MRP.P.forEach((row, i) => row.forEach((pv, j) => {
        if (!pv || i === 4) return;
        const hot = f.hot === i, col = hot ? klass(z, 1) : c.ink2;
        if (i === j) loop(z, Np[i], rad, f2(pv, 1), col, hot ? 2.5 : 1.3, false); else link(z, Np[i], Np[j], rad, f2(pv, 1), col, hot ? 2.5 : 1.3);
      }));
      Np.forEach((q, i) => {
        const v = f.V ? f.V[i] : null, hot = f.hot === i;
        D.circle(g, q.x, q.y, rad, { fill: hot ? klass(z, 0) : c.surf, stroke: c.ink2, w: 1.5 });
        D.text(g, MRP.names[i], q.x, q.y - 4, { a: 'center', s: 11, b: true, c: hot ? '#fff' : c.ink });
        D.text(g, `R ${nf(f.R[i])}`, q.x, q.y + 11, { a: 'center', s: 10, mono: true, c: hot ? '#fff' : c.ink2 });
      });
      const x = 420;
      head(z, f.k ? `sweep ${f.k}` : 'values', x, 30);
      MRP.names.forEach((nm, i) => {
        D.text(g, nm, x, 60 + i * 26, { s: 12, b: true, c: c.ink });
        if (f.V) D.text(g, f2(f.V[i], 3), x + 70, 60 + i * 26, { s: 12, mono: true, b: f.hot === i, c: f.V[i] > 0 ? c.green : f.V[i] < 0 ? c.red : c.ink });
      });
      D.text(g, 'V(s) = R(s) + γ Σ P(s′|s) V(s′)', 380, 304, { s: 11, mono: true, b: true, c: c.cv });
      D.text(g, `γ = ${f2(f.g, 2)}`, x, 236, { s: 13, b: true, c: klass(z, 1) });
    }
  });
})();

/* =====================================================================================================
   Reinforcement 2.1  dynamic programming: policy evaluation on the 4 x 4 gridworld, value iteration on FrozenLake
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr } = MLZ;
  const ARW = ['↑', '↓', '←', '→'];
  /* draw an arrow glyph set in a cell: dirs is a list of indices into ARW */
  function arrows(z, x, y, s, dirs, col) {
    const g = z.g, cy = y + s * 0.4, off = [[0, -13], [0, 13], [-16, 0], [16, 0]];
    dirs.forEach(d => D.text(g, ARW[d], x + s / 2 + off[d][0], cy + off[d][1] + 5, { a: 'center', s: 13, b: true, c: col }));
  }

  trace('mlpolicyeval', {
    title: 'Policy evaluation: sweep the Bellman equation until the values settle',
    sub: 'The 4 × 4 gridworld: the shaded corners are exits, every move costs −1, and the policy moves up, down, left or right with chance 1/4 each. Each sweep sets every value to the average over the four moves of −1 + γ × (value of the cell you land in). The small arrows show the greedy moves for the current values.',
    W: 600, H: 330,
    params: [{ k: 'g', label: 'Discount γ', type: 'range', v: 1, min: 0.5, max: 1, step: 0.05 }],
    tips: [
      { t: 'γ = 0.5: far future costs hardly count, so values stay between −1 and −2 and settle in a few sweeps.', set: { g: 0.5 }, play: true },
      { t: 'γ = 0.9: values settle much faster than with γ = 1, and the greedy arrows still point to the exits.', set: { g: 0.9 }, play: true }
    ],
    frames(p) {
      const g = +p.g, mv = [-4, 4, -1, 1];
      const nx = (s, m) => { const r = Math.floor(s / 4), c = s % 4; return (m === -4 && r === 0) || (m === 4 && r === 3) || (m === -1 && c === 0) || (m === 1 && c === 3) ? s : s + m; };
      const greedy = V => V.map((_, s) => { if (s === 0 || s === 15) return []; const q = mv.map(m => -1 + g * V[nx(s, m)]), b = Math.max(...q); return q.map((v, i) => (Math.abs(v - b) < 1e-6 ? i : -1)).filter(i => i >= 0); });
      let V = Array(16).fill(0);
      const fr = [{ V: V.slice(), k: 0, G: greedy(V), g, say: 'Sweep 0: every value starts at 0. All moves look equally good, so every cell shows all four greedy arrows.' }];
      const show = [1, 2, 3, 5, 10, 30];
      let k = 0, delta = 1;
      while (delta > 1e-4 && k < 2000) {
        k++;
        const nw = V.map((_, s) => (s === 0 || s === 15 ? 0 : mv.reduce((a, m) => a + 0.25 * (-1 + g * V[nx(s, m)]), 0)));
        delta = Math.max(...nw.map((v, i) => Math.abs(v - V[i])));
        const old = V; V = nw;
        if (show.includes(k)) fr.push({ V: V.slice(), k, G: greedy(V), g, say: k === 1 ? 'Sweep 1: one move costs −1 and all next values were 0, so every non exit cell becomes −1. Cells next to an exit already prefer stepping into it.'
          : k === 2 ? `Sweep 2: cell 1 = ¼ × (−1 + ${f2(g, 2)} × 0) + ¾ × (−1 + ${f2(g, 2)} × (−1)) = ${f2(V[1], 3)}. Cells near an exit lose less.`
            : `After ${k} sweeps the largest change in one sweep was ${f2(delta, 4)}. The greedy arrows ${k >= 3 ? 'already form shortest paths to the exits' : 'are sorting themselves out'}.` });
        void old;
      }
      fr.push({ V: V.slice(), k, G: greedy(V), g, done: true, say: `Converged after ${k} sweeps (largest change below 0.0001). ${g === 1 ? 'These are the values −14, −18, −20 and −22 from Sutton and Barto’s example 4.1.' : ''} The policy was random, yet acting greedily on its values gives an optimal policy here.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, s = 66, x0 = 20, y0 = 26;
      const lo = Math.min(-1, ...f.V);
      for (let i = 0; i < 16; i++) {
        const r = Math.floor(i / 4), cc = i % 4, x = x0 + cc * s, y = y0 + r * s, exit = i === 0 || i === 15;
        const t = exit ? 0 : f.V[i] / lo;
        rr(g, x, y, s - 3, s - 3, 6, { fill: exit ? 'rgba(22,163,74,0.25)' : `rgba(220,38,38,${(0.06 + 0.4 * t).toFixed(3)})`, stroke: c.line });
        D.text(g, exit ? 'exit' : f2(f.V[i], 1), x + s / 2 - 1, exit ? y + s / 2 + 5 : y + s - 9, { a: 'center', s: exit ? 13 : 11, b: true, mono: !exit, c: exit ? c.green : c.ink });
        if (!exit) arrows(z, x, y, s - 3, f.G[i], klass(z, 0));
      }
      const x = 310;
      head(z, f.done ? `converged, sweep ${f.k}` : `sweep ${f.k}`, x, 30);
      D.text(g, `γ = ${f2(f.g, 2)}`, x, 56, { s: 13, b: true, c: klass(z, 1) });
      D.text(g, 'v(s) ← Σₐ 0.25 (−1 + γ v(s′))', x, 88, { s: 12, mono: true, b: true, c: c.cv });
      D.text(g, 'darker red: more costly to finish', x, 116, { s: 11, c: c.ink2 });
      D.text(g, 'arrows: greedy moves for these values', x, 134, { s: 11, c: klass(z, 0) });
    }
  });

  const MAP = 'SFFFFHFHFFFHHFFG', DIRS = [[0, -1], [1, 0], [0, 1], [-1, 0]], GL = ['←', '↓', '→', '↑'];
  trace('mlvalueiter', {
    title: 'Value iteration on slippery ice',
    sub: 'The FrozenLake map from Gymnasium: start S, holes H, goal G (reward 1). On slippery ice the agent may slide to either side of the way it chose. Each sweep sets every value to the best action’s expected next value. The arrows show the best action. Watch the value spread back from the goal.',
    W: 600, H: 330,
    params: [
      { k: 'slip', label: 'Chance of sliding sideways', type: 'range', v: 0.67, min: 0, max: 0.67, step: 0.01 },
      { k: 'g', label: 'Discount γ', type: 'range', v: 0.99, min: 0.5, max: 0.99, step: 0.01 }
    ],
    tips: [
      { t: 'No sliding: the agent walks a shortest 6 move route and always succeeds, so the start is worth 0.99⁵ = 0.951, because the reward arrives on the sixth move.', set: { slip: 0, g: 0.99 }, play: true },
      { t: 'γ = 0.7 on slippery ice: long careful routes are not worth it, so the values near the start shrink a lot.', set: { slip: 0.67, g: 0.7 }, play: true }
    ],
    frames(p) {
      const sl = +p.slip, g = +p.g;
      const T = (s, a) => {
        if (MAP[s] === 'H' || MAP[s] === 'G') return [];
        const out = [];
        [[a - 1, sl / 2], [a, 1 - sl], [a + 1, sl / 2]].forEach(([b, pr]) => {
          if (pr <= 0) return;
          const [dr, dc] = DIRS[(b + 4) % 4];
          const r = Math.min(3, Math.max(0, Math.floor(s / 4) + dr)), c = Math.min(3, Math.max(0, (s % 4) + dc)), s2 = 4 * r + c;
          out.push([pr, s2, MAP[s2] === 'G' ? 1 : 0, MAP[s2] === 'H' || MAP[s2] === 'G']);
        });
        return out;
      };
      const Q = (V, s, a) => T(s, a).reduce((acc, [pr, s2, r, done]) => acc + pr * (r + (done ? 0 : g * V[s2])), 0);
      const pol = V => V.map((_, s) => { if (MAP[s] === 'H' || MAP[s] === 'G') return -1; const q = [0, 1, 2, 3].map(a => Q(V, s, a)), m = Math.max(...q); return m < 1e-9 ? -1 : q.findIndex(v => v > m - 1e-9); });
      let V = Array(16).fill(0);
      const fr = [{ V: V.slice(), k: 0, pi: pol(V), sl, g, say: `All values start at 0. The only reward is 1 for stepping onto G. Chance of going the chosen way: ${f2(1 - sl, 2)}, sliding to each side: ${f2(sl / 2, 2)}.` }];
      const show = [1, 2, 3, 4, 5, 6, 8, 10, 20, 50, 100];
      let k = 0, delta = 1;
      while (delta > 1e-6 && k < 3000) {
        k++;
        const nw = V.map((_, s) => Math.max(...[0, 1, 2, 3].map(a => Q(V, s, a))));
        delta = Math.max(...nw.map((v, i) => Math.abs(v - V[i])));
        V = nw;
        if (show.includes(k)) fr.push({ V: V.slice(), k, pi: pol(V), sl, g, say: k <= 3 ? `Sweep ${k}: value has reached the cells ${k} step${k > 1 ? 's' : ''} from the goal. Cells with no route yet stay at 0 and show no arrow.` : `After ${k} sweeps the start is worth ${f2(V[0], 3)} and the largest change was ${f2(delta, 5)}.` });
      }
      const PF = pol(V);
      fr.push({ V: V.slice(), k, pi: PF, sl, g, done: true, say: `Converged after ${k} sweeps. The start is worth <b>${f2(V[0], 3)}</b>${sl > 0 ? (g >= 0.95 ? ', a little below the chance of reaching the goal with the best policy, because γ shrinks late rewards' : '. With γ this small the value mostly says how soon the goal can be reached, not how likely it is, and far cells are worth almost nothing') : ''}. ${sl > 0.5 && PF[0] === 0 ? 'On very slippery ice the best first move at S points left, into the wall: it can never slide into a hole that way.' : sl === 0 ? 'Without sliding the policy walks a shortest path.' : 'Look at how the arrows steer away from the holes.'}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, s = 66, x0 = 20, y0 = 26;
      for (let i = 0; i < 16; i++) {
        const r = Math.floor(i / 4), cc = i % 4, x = x0 + cc * s, y = y0 + r * s, ch = MAP[i];
        const fill = ch === 'H' ? 'rgba(15,23,42,0.55)' : ch === 'G' ? 'rgba(22,163,74,0.35)' : `rgba(37,99,235,${(0.05 + 0.5 * f.V[i]).toFixed(3)})`;
        rr(g, x, y, s - 3, s - 3, 6, { fill, stroke: c.line });
        if (ch === 'H') { D.text(g, 'hole', x + s / 2 - 1, y + s / 2 + 5, { a: 'center', s: 12, b: true, c: '#fff' }); continue; }
        if (ch === 'G') { D.text(g, 'goal', x + s / 2 - 1, y + s / 2 + 5, { a: 'center', s: 12, b: true, c: c.green }); continue; }
        D.text(g, f2(f.V[i], 2), x + s / 2 - 1, y + s - 12, { a: 'center', s: 11, mono: true, c: c.ink });
        if (f.pi[i] >= 0) D.text(g, GL[f.pi[i]], x + s / 2 - 1, y + 30, { a: 'center', s: 20, b: true, c: klass(z, 1) });
        if (ch === 'S') D.text(g, 'S', x + 8, y + 16, { s: 11, b: true, c: c.ink2 });
      }
      const x = 310;
      head(z, f.done ? `converged, sweep ${f.k}` : `sweep ${f.k}`, x, 30);
      D.text(g, `slide sideways ${f2(f.sl, 2)}   γ = ${f2(f.g, 2)}`, x, 56, { s: 12, mono: true, c: c.ink });
      D.text(g, 'v(s) ← maxₐ Σ p (r + γ v(s′))', x, 88, { s: 12, mono: true, b: true, c: c.cv });
      D.text(g, `value of start ${f2(f.V[0], 3)}`, x, 120, { s: 14, b: true, c: klass(z, 0) });
      D.text(g, 'orange arrow: best action', x, 150, { s: 11, c: klass(z, 1) });
      D.text(g, 'deeper blue: higher value', x, 168, { s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Reinforcement 2.2  Monte Carlo and temporal difference learning on the five state random walk
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, rng, plot } = MLZ;
  const NAMES = ['end', 'A', 'B', 'C', 'D', 'E', 'end'], TRUE = [0, 1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6, 0];
  function walk(z, f, y0) {
    const c = z.col, g = z.g, x0 = 30, w = 62;
    for (let i = 0; i <= 6; i++) {
      const x = x0 + i * w, endc = i === 0 || i === 6;
      if (endc) rr(g, x - 20, y0 - 18, 40, 36, 6, { fill: i === 6 ? 'rgba(22,163,74,0.2)' : c.surf, stroke: c.line });
      else D.circle(g, x, y0, 20, { fill: f.s === i ? klass(z, 0) : c.surf, stroke: c.ink2, w: 1.5 });
      D.text(g, endc ? (i === 6 ? '+1' : '0') : NAMES[i], x, y0 + 5, { a: 'center', s: 12, b: true, c: f.s === i && !endc ? '#fff' : i === 6 ? c.green : c.ink });
      if (i < 6) D.line(g, x + 21, y0, x + w - 21, y0, c.line, 1.5);
    }
    return { x0, w };
  }

  trace('mltdstep', {
    title: 'One episode of TD(0): learn after every step',
    sub: 'A random walk: start in C, step left or right with chance ½, reward +1 only for leaving on the right. TD(0) does not wait for the episode to end. After every step it compares its old guess V(s) with the TD target r + γV(s′) and moves V(s) a fraction α towards it.',
    W: 600, H: 330,
    params: [
      { k: 'a', label: 'Step size α', type: 'range', v: 0.5, min: 0.05, max: 1, step: 0.05 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 16, min: 1, max: 30 }
    ],
    tips: [
      { t: 'α = 1: each value jumps all the way to its target, so one step decides it and earlier learning is thrown away.', set: { a: 1, seed: 16 }, play: true },
      { t: 'A walk that ends on the left: the last target is 0 + V(end) = 0, so V(A) drops sharply.', set: { a: 0.5, seed: 2 }, play: true }
    ],
    frames(p) {
      const a = +p.a, R = rng(+p.seed * 3571), V = [0, 0.3, 0.4, 0.5, 0.6, 0.8, 0];
      let s = 3, t = 0;
      const fr = [{ V: V.slice(), s, say: 'The guesses are left over from earlier episodes: 0.3, 0.4, 0.5, 0.6 and 0.8 for A to E, close to the truth but not exact. The two ends are worth 0. The walker starts in C.' }];
      while (s >= 1 && s <= 5 && t < 30) {
        t++;
        const s2 = s + (R() < 0.5 ? -1 : 1), r = s2 === 6 ? 1 : 0, target = r + V[s2], err = target - V[s], old = V[s];
        V[s] += a * err;
        fr.push({ V: V.slice(), s: s2, from: s, upd: s, say: `Step ${t}: ${NAMES[s]} to ${s2 === 0 || s2 === 6 ? 'the ' + (s2 === 6 ? 'right' : 'left') + ' end' : NAMES[s2]}, reward ${r}. TD target = ${r} + V(${NAMES[s2]}) = ${f2(target, 3)}. TD error δ = ${f2(target, 3)} − ${f2(old, 3)} = <b>${f2(err, 3)}</b>. V(${NAMES[s]}) becomes ${f2(old, 3)} + ${f2(a, 2)} × ${err < 0 ? '(' + f2(err, 3) + ')' : f2(err, 3)} = <b>${f2(V[s], 3)}</b>.${err === 0 ? ' The error is 0, so nothing changes: the guess already agrees with its neighbour.' : ''}` });
        s = s2;
      }
      fr.push({ V: V.slice(), s, done: true, say: `The episode ended after ${t} steps on the ${s === 6 ? 'right (+1)' : 'left (0)'}. Monte Carlo would only now update every visited state with the final return. TD has already updated as it went, using its own guesses for the next state. This is called <b>bootstrapping</b>.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, { x0, w } = walk(z, f, 50);
      if (f.from !== undefined) D.arrow(g, x0 + f.from * w, 82, x0 + f.s * w, 82, klass(z, 1), 2.5, 9);
      const by = 280, H = 150;
      D.line(g, x0 + w / 2, by, x0 + 5.6 * w, by, c.ink2, 1);
      for (let i = 1; i <= 5; i++) {
        const x = x0 + i * w;
        rr(g, x - 16, by - f.V[i] * H, 32, f.V[i] * H, 3, { fill: f.upd === i ? klass(z, 1) : 'rgba(37,99,235,0.5)' });
        D.line(g, x - 22, by - TRUE[i] * H, x + 22, by - TRUE[i] * H, c.ink, 2, [4, 3]);
        D.text(g, f2(f.V[i], 2), x, by - f.V[i] * H - 6, { a: 'center', s: 11, mono: true, c: c.ink });
        D.text(g, NAMES[i], x, by + 15, { a: 'center', s: 11, b: true, c: c.ink2 });
      }
      const x = 440;
      head(z, 'TD(0)', x, 120);
      D.text(g, 'V(s) ← V(s) + α δ', x, 144, { s: 11, mono: true, b: true, c: c.cv });
      D.text(g, 'δ = r + γV(s′) − V(s)', x, 164, { s: 11, mono: true, c: c.ink });
      D.text(g, '▬ estimate', x, 196, { s: 11, c: klass(z, 0) });
      D.text(g, '- - true value', x, 214, { s: 11, c: c.ink });
    }
  });

  trace('mlmctd', {
    title: 'Monte Carlo against TD: who learns faster?',
    sub: 'Both learn the random walk values from the same episodes. Monte Carlo waits until each episode ends and moves every visited state towards the final return. TD(0) moves each state towards r + V(next) after every step. The chart tracks the average error against the true values 1/6 to 5/6.',
    W: 600, H: 330,
    params: [
      { k: 'amc', label: 'Monte Carlo step size α', type: 'range', v: 0.03, min: 0.01, max: 0.2, step: 0.01 },
      { k: 'atd', label: 'TD step size α', type: 'range', v: 0.05, min: 0.01, max: 0.3, step: 0.01 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 1, min: 1, max: 30 }
    ],
    tips: [
      { t: 'A large TD step size of 0.3: TD drops fast at first, then keeps bouncing because each step jumps too far.', set: { amc: 0.03, atd: 0.3, seed: 1 }, play: true },
      { t: 'Give Monte Carlo a large step size too (0.2): its error also bounces, and more than TD’s, because whole returns are noisier targets.', set: { amc: 0.2, atd: 0.05, seed: 1 }, play: true }
    ],
    frames(p) {
      const amc = +p.amc, atd = +p.atd, R = rng(+p.seed * 2311);
      const Vm = [0, 0.5, 0.5, 0.5, 0.5, 0.5, 0], Vt = Vm.slice(), rms = V => Math.sqrt([1, 2, 3, 4, 5].reduce((a, i) => a + (V[i] - TRUE[i]) ** 2, 0) / 5);
      const hm = [rms(Vm)], ht = [rms(Vt)];
      const fr = [{ Vm: Vm.slice(), Vt: Vt.slice(), hm: hm.slice(), ht: ht.slice(), ep: 0, say: `Both start with every value at 0.5, an error of ${f2(hm[0], 3)}. The dashed lines mark the true values.` }];
      const show = [1, 2, 3, 5, 10, 20, 50, 100, 200];
      for (let ep = 1; ep <= 200; ep++) {
        let s = 3; const path = [];
        while (s >= 1 && s <= 5) {
          const s2 = s + (R() < 0.5 ? -1 : 1), r = s2 === 6 ? 1 : 0;
          Vt[s] += atd * (r + Vt[s2] - Vt[s]);
          path.push(s); s = s2;
        }
        const G = s === 6 ? 1 : 0;
        path.forEach(x => { Vm[x] += amc * (G - Vm[x]); });
        hm.push(rms(Vm)); ht.push(rms(Vt));
        if (show.includes(ep)) fr.push({ Vm: Vm.slice(), Vt: Vt.slice(), hm: hm.slice(), ht: ht.slice(), ep, say: ep <= 3
          ? `Episode ${ep} visited ${path.map(i => NAMES[i]).join(' ')} and ended ${G ? 'right (+1)' : 'left (0)'}. Monte Carlo pushed every visited state towards ${G}. TD changed only where a neighbour’s value differed.`
          : `After ${ep} episodes the error is ${f2(hm[ep], 3)} for Monte Carlo and ${f2(ht[ep], 3)} for TD.${ep === 200 ? (ht[ep] < hm[ep] ? ' TD is ahead: its one step targets are less noisy than whole returns, which is why it usually learns faster on problems like this.' : ' Monte Carlo is ahead here: with these step sizes, TD’s steps are too large or too small for this run.') : ''}` });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, x0 = 40, w = 46, by = 150, H = 120;
      head(z, 'values', 20, 22);
      for (let i = 1; i <= 5; i++) {
        const x = x0 + (i - 1) * w;
        rr(g, x, by - f.Vm[i] * H, 16, f.Vm[i] * H, 3, { fill: klass(z, 1) });
        rr(g, x + 18, by - f.Vt[i] * H, 16, f.Vt[i] * H, 3, { fill: klass(z, 0) });
        D.line(g, x - 3, by - TRUE[i] * H, x + 37, by - TRUE[i] * H, c.ink, 2, [4, 3]);
        D.text(g, NAMES[i], x + 17, by + 16, { a: 'center', s: 11, b: true, c: c.ink2 });
      }
      D.text(g, '▬ Monte Carlo', 20, 196, { s: 11, b: true, c: klass(z, 1) });
      D.text(g, '▬ TD(0)', 120, 196, { s: 11, b: true, c: klass(z, 0) });
      D.text(g, `episode ${f.ep}`, 20, 230, { s: 14, b: true, c: c.ink });
      D.text(g, `error MC ${f2(f.hm[f.hm.length - 1], 3)}`, 20, 256, { s: 12, mono: true, c: klass(z, 1) });
      D.text(g, `error TD ${f2(f.ht[f.ht.length - 1], 3)}`, 20, 276, { s: 12, mono: true, c: klass(z, 0) });
      const Pl = plot(z, [280, 14, 310, 300], [0, 200], [0, 0.3], { dx: 0, dy: 2, xl: 'episodes', yl: 'RMS error' });
      [[f.hm, klass(z, 1)], [f.ht, klass(z, 0)]].forEach(([h, col]) => { for (let i = 1; i < h.length; i++) D.line(g, Pl.X(i - 1), Pl.Y(Math.min(0.3, h[i - 1])), Pl.X(i), Pl.Y(Math.min(0.3, h[i])), col, 2); });
    }
  });
})();

/* =====================================================================================================
   Reinforcement 2.3  control with TD: a Q table filling up step by step, and Q learning against SARSA on the cliff
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, rng, plot, box } = MLZ;
  const pick = (q, eps, R) => { if (R() < eps) return Math.floor(R() * q.length); const m = Math.max(...q), t = q.map((v, i) => (v === m ? i : -1)).filter(i => i >= 0); return t[Math.floor(R() * t.length)]; };
  const pn = v => (v < 0 ? '(' + f2(v, 3) + ')' : f2(v, 3));

  trace('mlqstep', {
    title: 'Filling a Q table one step at a time',
    sub: 'A corridor of 5 cells. The agent starts in cell 0, and reaching cell 4 gives +1 and ends the episode. It keeps a table Q(s, a) for left and right in each cell and picks actions ε greedily. Q learning learns from the best next action, SARSA from the next action it really takes.',
    W: 600, H: 330,
    params: [
      { k: 'm', label: 'Method', type: 'select', v: 'q', opts: [['q', 'Q learning'], ['sarsa', 'SARSA']] },
      { k: 'a', label: 'Step size α', type: 'range', v: 0.5, min: 0.1, max: 1, step: 0.1 },
      { k: 'eps', label: 'ε (chance of a random action)', type: 'range', v: 0.2, min: 0, max: 0.5, step: 0.05 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 4, min: 1, max: 30 }
    ],
    tips: [
      { t: 'SARSA with ε = 0.5: random moves are frequent, and SARSA’s values include their cost, so its numbers end up lower than Q learning’s.', set: { m: 'sarsa', eps: 0.5, a: 0.5, seed: 4 }, play: true },
      { t: 'ε = 0: no exploration. Ties are broken at random, so the agent still wanders at first, then repeats the first route that worked.', set: { m: 'q', eps: 0, a: 0.5, seed: 4 }, play: true }
    ],
    frames(p) {
      const isQ = p.m === 'q', al = +p.a, eps = +p.eps, R = rng(+p.seed * 4111), g = 0.9;
      const Q = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]];
      const base = { isQ };
      const fr = [{ ...base, Q: Q.map(r => r.slice()), s: 0, ep: 1, say: `Every Q value starts at 0. γ = 0.9. Method: <b>${isQ ? 'Q learning' : 'SARSA'}</b>.` }];
      let shown = 0;
      for (let ep = 1; ep <= 30; ep++) {
        let s = 0, a = pick(Q[s], eps, R), t = 0;
        while (s !== 4 && t < 60) {
          t++;
          const s2 = Math.max(0, s + (a === 1 ? 1 : -1)), r = s2 === 4 ? 1 : 0, done = s2 === 4;
          const a2 = done ? 0 : pick(Q[s2], eps, R);
          const nxt = done ? 0 : isQ ? Math.max(...Q[s2]) : Q[s2][a2], target = r + g * nxt, old = Q[s][a];
          Q[s][a] += al * (target - old);
          if (shown < 22 && ep <= 3) {
            shown++;
            fr.push({ ...base, Q: Q.map(rw => rw.slice()), s: s2, from: s, upd: [s, a], ep, say: `Episode ${ep}, cell ${s}, action <b>${a ? 'right' : 'left'}</b> to cell ${s2}${done ? ' (goal, +1)' : ''}. ${done ? 'Terminal, so the target is just r = 1.' : isQ ? `Target = r + γ max Q(${s2}, ·) = ${r} + 0.9 × ${pn(nxt)} = ${f2(target, 3)}.` : `Next action chosen: ${a2 ? 'right' : 'left'}. Target = r + γ Q(${s2}, ${a2 ? 'right' : 'left'}) = ${r} + 0.9 × ${pn(nxt)} = ${f2(target, 3)}.`} Q(${s}, ${a ? 'right' : 'left'}) = ${f2(old, 3)} + ${f2(al, 1)} × (${f2(target, 3)} − ${f2(old, 3)}) = <b>${f2(Q[s][a], 3)}</b>.` });
          }
          s = s2; a = a2;
        }
        if (ep === 10 || ep === 30) fr.push({ ...base, Q: Q.map(rw => rw.slice()), s: 0, ep, say: `After ${ep} episodes. ${Q.slice(0, 4).every(q => q[1] > q[0]) ? 'Right is now the better action in every cell.' : 'Right is not yet the better action in every cell, so keep going.'} With γ = 0.9 the ideal values for right are 0.9³, 0.9², 0.9 and 1 = 0.729, 0.81, 0.9 and 1, which Q learning approaches. ${isQ ? '' : 'SARSA aims lower when ε is large, because its targets include the random moves it will keep making.'}` });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, x0 = 40, w = 100, y0 = 40;
      for (let i = 0; i < 5; i++) {
        const x = x0 + i * w;
        rr(g, x, y0, w - 8, 44, 6, { fill: i === 4 ? 'rgba(22,163,74,0.25)' : c.surf, stroke: c.line });
        D.text(g, i === 4 ? 'goal +1' : 'cell ' + i, x + (w - 8) / 2, y0 + 27, { a: 'center', s: 12, b: true, c: i === 4 ? c.green : c.ink });
        if (f.s === i) D.circle(g, x + (w - 8) / 2, y0 - 12, 9, { fill: klass(z, 0) });
      }
      if (f.from !== undefined && f.from !== f.s) D.arrow(g, x0 + f.from * w + 46, y0 - 12, x0 + f.s * w + 46, y0 - 12, klass(z, 1), 2, 8);
      head(z, 'Q table', x0, 130);
      ['left', 'right'].forEach((nm, a) => {
        D.text(g, nm, x0 - 6, 168 + a * 40, { a: 'right', s: 12, b: true, c: c.ink2 });
        for (let s = 0; s < 4; s++) {
          const hot = f.upd && f.upd[0] === s && f.upd[1] === a, best = f.Q[s][a] > f.Q[s][1 - a];
          box(z, x0 + s * w, 148 + a * 40, w - 8, 34, f2(f.Q[s][a], 3), { fill: hot ? klass(z, 1) : best ? 'rgba(22,163,74,0.18)' : c.surf, c: hot ? '#fff' : c.ink, mono: true, s: 13, r: 5 });
        }
      });
      D.text(g, f.isQ ? 'Q learning: Q(s,a) += α [r + γ maxₐ′ Q(s′,a′) − Q(s,a)]' : 'SARSA: Q(s,a) += α [r + γ Q(s′,a′) − Q(s,a)], a′ = next action taken', x0, 260, { s: 12, mono: true, b: true, c: c.cv });
      D.text(g, `episode ${f.ep}   green: the better action in that cell`, x0, 290, { s: 11, c: c.ink2 });
    }
  });

  const CL = { R: 4, C: 12 };
  trace('mlcliff', {
    title: 'The cliff walk: Q learning against SARSA',
    sub: 'Start S at bottom left, goal G at bottom right. The bottom row between them is a cliff: falling costs −100 and sends you back to S. Every move costs −1. Both methods explore with ε greedy. The orange line is the greedy path learned so far, and the chart shows the reward of each episode while learning.',
    W: 600, H: 330,
    params: [
      { k: 'm', label: 'Method', type: 'select', v: 'q', opts: [['q', 'Q learning'], ['sarsa', 'SARSA'], ['es', 'Expected SARSA']] },
      { k: 'eps', label: 'ε', type: 'range', v: 0.1, min: 0, max: 0.3, step: 0.05 },
      { k: 'a', label: 'Step size α', type: 'range', v: 0.5, min: 0.1, max: 1, step: 0.1 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 1, min: 1, max: 30 }
    ],
    tips: [
      { t: 'SARSA learns a path one or more rows away from the edge, because its values count the random steps that sometimes fall off. Its reward while learning is better.', set: { m: 'sarsa', eps: 0.1, a: 0.5, seed: 1 }, play: true },
      { t: 'Q learning with ε = 0.3: the greedy path still hugs the edge, but with so much exploring it falls in very often while learning.', set: { m: 'q', eps: 0.3, a: 0.5, seed: 1 }, play: true }
    ],
    frames(p) {
      const R = rng(+p.seed * 9001), eps = +p.eps, al = +p.a, m = p.m, mv = [[-1, 0], [1, 0], [0, -1], [0, 1]];
      const Q = Array.from({ length: CL.R * CL.C }, () => [0, 0, 0, 0]);
      const step = (s, a) => { let r = Math.floor(s / CL.C) + mv[a][0], c = (s % CL.C) + mv[a][1]; r = Math.min(3, Math.max(0, r)); c = Math.min(11, Math.max(0, c)); if (r === 3 && c >= 1 && c <= 10) return [36, -100, false, true]; const s2 = r * CL.C + c; return [s2, -1, s2 === 47, false]; };
      const greedy = () => { let s = 36; const path = [s]; for (let i = 0; i < 40 && s !== 47; i++) { const q = Q[s]; s = step(s, q.indexOf(Math.max(...q)))[0]; path.push(s); } return path; };
      const hist = [], show = [1, 5, 10, 25, 50, 100, 200, 500];
      const fr = [{ path: [36], walk: [], hist: [], ep: 0, m, say: 'All Q values start at 0. The shortest route runs right along the cliff edge: 13 moves, reward −13.' }];
      for (let ep = 1; ep <= 500; ep++) {
        let s = 36, a = pick(Q[s], eps, R), tot = 0, falls = 0, t = 0;
        const walk = [s];
        while (s !== 47 && t < 1000) {
          t++;
          const [s2, r, done, fell] = step(s, a);
          const a2 = pick(Q[s2], eps, R);
          let nxt = 0;
          if (!done) {
            if (m === 'q') nxt = Math.max(...Q[s2]);
            else if (m === 'sarsa') nxt = Q[s2][a2];
            else { const b = Q[s2].indexOf(Math.max(...Q[s2])); nxt = Q[s2].reduce((acc, v, i) => acc + v * (eps / 4 + (i === b ? 1 - eps : 0)), 0); }
          }
          Q[s][a] += al * (r + nxt - Q[s][a]);
          tot += r; falls += fell ? 1 : 0;
          s = s2; a = a2; walk.push(s);
        }
        hist.push(tot);
        if (show.includes(ep)) {
          const last20 = hist.slice(-20), avg = last20.reduce((x, y) => x + y, 0) / last20.length, path = greedy(), ok = path[path.length - 1] === 47;
          const edge = ok && path.slice(1, -1).every(q => Math.floor(q / CL.C) >= 2) && path.some(q => Math.floor(q / CL.C) === 2);
          fr.push({ path, walk: ep <= 10 ? walk : [], hist: hist.slice(), ep, m, say: ep <= 10
            ? `Episode ${ep}: ${t} moves, ${falls} fall${falls === 1 ? '' : 's'} off the cliff, reward ${tot}.${ep === 1 ? ' Early on the agent wanders and falls, and each fall makes the moves next to the cliff look bad.' : ''}`
            : `After ${ep} episodes the average reward of the last 20 episodes is ${f2(avg, 1)}. ${ok ? `The greedy path takes ${path.length - 1} moves${edge ? ', right along the edge of the cliff' : ', keeping away from the edge'}.` : 'The greedy path does not reach the goal yet.'}${ep === 500 ? (m === 'q' ? ' Q learning learns the values of the best path (assuming it stops exploring), but while it still explores it falls off now and then, so its reward during learning is worse than SARSA’s.' : ' SARSA learns the value of the policy it actually follows, random steps included, so it prefers a safer path and earns more while learning.') : ''}` });
        }
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, cs = 40, x0 = 60, y0 = 12;
      for (let r = 0; r < 4; r++) for (let cc = 0; cc < 12; cc++) {
        const cliff = r === 3 && cc >= 1 && cc <= 10;
        rr(g, x0 + cc * cs, y0 + r * cs, cs - 2, cs - 2, 4, { fill: cliff ? 'rgba(220,38,38,0.35)' : c.surf, stroke: c.line });
      }
      D.text(g, 'S', x0 + 19, y0 + 3 * cs + 24, { a: 'center', s: 13, b: true, c: c.ink });
      D.text(g, 'G', x0 + 11 * cs + 19, y0 + 3 * cs + 24, { a: 'center', s: 13, b: true, c: c.green });
      D.text(g, 'cliff  −100', x0 + 6 * cs, y0 + 3 * cs + 24, { a: 'center', s: 12, b: true, c: c.red });
      const P = q => [x0 + (q % CL.C) * cs + 19, y0 + Math.floor(q / CL.C) * cs + 19];
      f.walk.forEach(q => { const [x, y] = P(q); D.circle(g, x, y, 3, { fill: 'rgba(37,99,235,0.35)' }); });
      for (let i = 1; i < f.path.length; i++) { const [a, b] = P(f.path[i - 1]), [cx, cy] = P(f.path[i]); D.line(g, a, b, cx, cy, klass(z, 1), 4); }
      const name = { q: 'Q learning', sarsa: 'SARSA', es: 'Expected SARSA' }[f.m];
      D.text(g, `${name}, episode ${f.ep}`, 10, 196, { s: 12, b: true, c: c.ink });
      if (f.hist.length) {
        const Pl = plot(z, [10, 204, 580, 122], [0, 500], [-200, 0], { dx: 0, dy: 0, xl: 'episode', yl: 'reward per episode' });
        let acc = 0, prev = 0;
        f.hist.forEach((v, i) => { prev = acc; acc = i ? 0.9 * acc + 0.1 * Math.max(-200, v) : Math.max(-200, v); if (i) D.line(g, Pl.X(i - 1), Pl.Y(prev), Pl.X(i), Pl.Y(acc), klass(z, 0), 1.5); });
        D.text(g, 'smoothed', 520, 222, { s: 10, c: c.ink2 });
      }
    }
  });
})();

/* =====================================================================================================
   Reinforcement 3.1  function approximation: state aggregation on the 1000 state random walk, and the parts of DQN
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, rng, plot, box } = MLZ;
  const nf = v => (Number.isInteger(v) ? String(v).replace('-', '−') : f2(v, 3));
  const pn = v => (v < 0 ? '(' + f2(v, 3) + ')' : f2(v, 3));
  let TRUE = null;
  const trueValues = () => {
    if (TRUE) return TRUE;
    const N = 1000, J = 100;
    let v = new Float64Array(N);
    for (let it = 0; it < 6000; it++) {
      const c = new Float64Array(N + 2 * J + 1);
      for (let i = 0; i < N + 2 * J; i++) c[i + 1] = c[i] + (i < J ? -1 : i >= N + J ? 1 : v[i - J]);
      const nv = new Float64Array(N);
      let diff = 0;
      for (let s = 0; s < N; s++) { const k = s + J; nv[s] = ((c[k] - c[k - J]) + (c[k + J + 1] - c[k + 1])) / (2 * J); diff = Math.max(diff, Math.abs(nv[s] - v[s])); }
      v = nv;
      if (diff < 1e-7) break;
    }
    TRUE = v;
    return v;
  };

  trace('mlaggregate', {
    title: 'State aggregation: 1000 states, a handful of weights',
    sub: 'A random walk over states 1 to 1000 starts at 500 and jumps 1 to 100 states left or right. Leaving on the left gives −1, on the right +1. The grey curve is the true value of each state. The blue staircase is the estimate: every state in a group shares one weight.',
    W: 600, H: 330,
    params: [
      { k: 'm', label: 'Method', type: 'select', v: 'mc', opts: [['mc', 'Gradient Monte Carlo'], ['td', 'Semi gradient TD(0)']] },
      { k: 'g', label: 'Number of groups', type: 'select', v: '10', opts: [['5', '5 groups'], ['10', '10 groups'], ['20', '20 groups'], ['50', '50 groups']] },
      { k: 'a', label: 'Step size α (TD only, Monte Carlo uses 1/n)', type: 'range', v: 0.01, min: 0.002, max: 0.05, step: 0.002 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 3, min: 1, max: 30 }
    ],
    tips: [
      { t: '50 groups with Monte Carlo: the staircase gets much closer to the curve, but each weight sees fewer visits, so it is noisier after only a few episodes.', set: { m: 'mc', g: '50', seed: 3 }, play: true },
      { t: 'Semi gradient TD with 10 groups: the steps near both ends stay closer to 0 than Monte Carlo’s, because TD bootstraps from the neighbouring group’s weight, which is itself a rough average.', set: { m: 'td', g: '10', a: 0.01, seed: 3 }, play: true }
    ],
    frames(p) {
      const v = trueValues(), G = +p.g, R = rng(+p.seed * 7907), al = +p.a, isMC = p.m === 'mc';
      const w = new Array(G).fill(0), n = new Array(G).fill(0), grp = s => Math.floor((s - 1) * G / 1000);
      const rmse = () => { let e = 0; for (let s = 1; s <= 1000; s++) e += (w[grp(s)] - v[s - 1]) ** 2; return Math.sqrt(e / 1000); };
      const fr = [{ w: w.slice(), G, isMC, path: [], say: `${G} groups of ${1000 / G} states, so ${G} weights instead of 1000 table entries. All weights start at 0. ${isMC ? 'Gradient Monte Carlo moves each visited group’s weight towards the final reward G (+1 or −1), with step 1/n, a running average.' : `Semi gradient TD(0) moves each visited group’s weight towards the weight of the next state’s group (or the final reward), with α = ${f2(al, 3)}.`}` }];
      const show = [1, 2, 5, 20, 100, 300, 1000, 2000];
      for (let ep = 1; ep <= 2000; ep++) {
        let s = 500; const states = [];
        while (s >= 1 && s <= 1000) { states.push(s); s += (1 + Math.floor(R() * 100)) * (R() < 0.5 ? 1 : -1); }
        const Gret = s > 1000 ? 1 : -1;
        states.forEach((st, i) => {
          const k = grp(st);
          if (isMC) { n[k]++; w[k] += (Gret - w[k]) / n[k]; }
          else { const tgt = i + 1 < states.length ? w[grp(states[i + 1])] : Gret; w[k] += al * (tgt - w[k]); }
        });
        if (show.includes(ep)) {
          fr.push({ w: w.slice(), G, isMC, path: ep <= 2 ? states : [], end: Gret, say: ep <= 2
            ? `Episode ${ep}: ${states.length} jumps, it leaves on the ${Gret > 0 ? 'right, reward +1' : 'left, reward −1'}. The dots show the states it visited. ${isMC ? 'Every visited group moves towards ' + nf(Gret) + ', the return.' : 'Only the group just before the exit sees the reward directly. The others move towards their neighbours’ weights.'} Error over all states: ${f2(rmse(), 3)}.`
            : `After ${ep} episodes the root mean squared error over all 1000 states is <b>${f2(rmse(), 3)}</b>.${ep === 2000 ? ` Inside a group every state gets the same value, so some error stays however long we train. ${isMC ? 'Monte Carlo finds the best staircase for the states the walk visits most.' : 'TD settles near, but not at, the best staircase: bootstrapping adds bias.'}` : ''}` });
        }
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, v = trueValues();
      const P = plot(z, [10, 10, 580, 300], [1, 1000], [-1, 1], { dx: 0, dy: 1, xl: 'state', yl: 'value' });
      for (let s = 1; s < 1000; s += 3) D.line(g, P.X(s), P.Y(v[s - 1]), P.X(s + 3), P.Y(v[Math.min(999, s + 2)]), c.ink2, 2);
      const gw = 1000 / f.G;
      f.w.forEach((wv, k) => {
        D.line(g, P.X(1 + k * gw), P.Y(wv), P.X((k + 1) * gw), P.Y(wv), klass(z, 0), 3);
        if (k) D.line(g, P.X(1 + k * gw), P.Y(f.w[k - 1]), P.X(1 + k * gw), P.Y(wv), klass(z, 0), 1, [3, 3]);
      });
      f.path.forEach(s => D.circle(g, P.X(s), P.Y(0), 3, { fill: klass(z, 1) }));
      D.text(g, 'grey: true value   blue: estimate   ' + (f.isMC ? 'gradient Monte Carlo' : 'semi gradient TD(0)'), 120, 30, { s: 11, c: c.ink2 });
    }
  });
})();

(() => {
  const { trace, D, f2, head, klass, rr, rng, plot, box } = MLZ;
  const pn = v => (v < 0 ? '(' + f2(v, 3) + ')' : f2(v, 3));
  const phi = s => [1, s / 5];
  const qv = (W, s, a) => W[a][0] + W[a][1] * s / 5;
  const ideal = (s, a) => (a === 1 ? 0.9 ** (4 - s) : 0.9 * 0.9 ** (4 - Math.max(s - 1, 0)));

  trace('mldqn', {
    title: 'Inside DQN: replay memory and a target network',
    sub: 'A corridor of states 0 to 5, reaching 5 gives +1. Q is a tiny model: Q(s, a) = w₀ + w₁ × s/5 for each action, so 4 weights replace the table. Transitions go into a replay memory of 8, updates use random minibatches of 3, and targets come from a frozen copy of the weights.',
    W: 600, H: 330,
    params: [
      { k: 'C', label: 'Copy to the target network every C updates', type: 'range', v: 5, min: 1, max: 30 },
      { k: 'rep', label: 'Replay memory', type: 'select', v: 'on', opts: [['on', 'On: random minibatch of 3'], ['off', 'Off: learn from the newest step only']] },
      { k: 'lr', label: 'Learning rate', type: 'range', v: 0.3, min: 0.05, max: 1, step: 0.05 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 2, min: 1, max: 30 }
    ],
    tips: [
      { t: 'C = 30: the target network (orange) stays still for 30 updates and then jumps, while the online line (blue) moves towards it between jumps. Early learning is slower than with C = 5.', set: { C: 30, rep: 'on', lr: 0.3, seed: 2 }, play: true },
      { t: 'C = 1 and replay off: this is plain online Q learning with a model. Every update chases a target that changed one step ago, using only the newest transition.', set: { C: 1, rep: 'off', lr: 0.3, seed: 2 }, play: true }
    ],
    frames(p) {
      const C = +p.C, rep = p.rep === 'on', lr = +p.lr, R = rng(+p.seed * 3571), g = 0.9, eps = 0.3;
      const W = [[0, 0], [0, 0]];
      let T = W.map(r => r.slice()), buf = [], updates = 0, s = Math.floor(R() * 5), t = 0, steps = 0, extra = 0, goals = 0;
      const snap = extra => ({ W: W.map(r => r.slice()), T: T.map(r => r.slice()), buf: buf.slice(), s, ...extra });
      const fr = [snap({ say: `Online weights and target weights all start at 0. The memory is empty. The agent starts in state ${s} and acts ε greedily with ε = 0.3. Training starts once the memory holds 3 transitions.` })];
      const showAt = [60, 120, 250, 500];
      for (steps = 1; steps <= 500; steps++) {
        const best = qv(W, s, 1) > qv(W, s, 0) ? 1 : qv(W, s, 1) < qv(W, s, 0) ? 0 : (R() < 0.5 ? 1 : 0);
        const a = R() < eps ? Math.floor(R() * 2) : best;
        const s2 = Math.max(0, s + (a ? 1 : -1)), done = s2 === 5, r = done ? 1 : 0;
        const tr = { s, a, r, s2, done };
        buf.push(tr); if (buf.length > 8) buf.shift();
        let batch = [], info = '';
        if (buf.length >= 3) {
          const idx = rep ? [0, 1, 2].map(() => Math.floor(R() * buf.length)) : [buf.length - 1];
          batch = idx;
          const grads = [[0, 0], [0, 0]], parts = [];
          idx.forEach(i => {
            const b = buf[i], y = b.r + (b.done ? 0 : g * Math.max(qv(T, b.s2, 0), qv(T, b.s2, 1))), q = qv(W, b.s, b.a), e = y - q;
            grads[b.a][0] += e * phi(b.s)[0] / idx.length; grads[b.a][1] += e * phi(b.s)[1] / idx.length;
            parts.push(`(${b.s}, ${b.a ? 'R' : 'L'}): ${b.done ? 'y = r = 1 (goal)' : `y = ${b.r} + 0.9 × ${pn(Math.max(qv(T, b.s2, 0), qv(T, b.s2, 1)))} = ${f2(y, 3)}`}, Q = ${f2(q, 3)}`);
          });
          for (let a2 = 0; a2 < 2; a2++) for (let j = 0; j < 2; j++) W[a2][j] += lr * grads[a2][j];
          updates++;
          info = ` ${rep ? 'Minibatch' : 'Newest transition only'} ${parts.join('. ')}. Each weight moves by learning rate × error × feature.`;
          if (updates % C === 0) { T = W.map(r => r.slice()); info += ` Update ${updates}: <b>copy the online weights into the target network</b>.`; }
        }
        const copied = C > 1 && buf.length >= 3 && updates % C === 0 && updates <= 2 * C;
        if (steps <= 5 || ((done && goals++ < 4) || copied) && extra < 7) {
          if (steps > 5) extra++;
          fr.push(snap({ batch, last: buf.length - 1, s: s2, from: s, say: `Step ${steps}: state ${s}, action ${a ? 'right' : 'left'}, reward ${r}, next state ${s2}${done ? ' (the goal, so the episode ends)' : ''}. ${buf.length === 8 && steps > 8 ? 'The memory is full, so the oldest transition was dropped to make room.' : `Stored in memory slot ${buf.length}.`}${buf.length < 3 ? ' Not enough memories to train yet.' : info}` }));
        }
        s = s2; t++;
        if (done || t >= 20) { s = Math.floor(R() * 5); t = 0; }
        if (showAt.includes(steps)) {
          let err = 0; for (let k = 0; k <= 4; k++) err = Math.max(err, Math.abs(qv(W, k, 1) - ideal(k, 1)));
          const right = [0, 1, 2, 3, 4].every(k => qv(W, k, 1) > qv(W, k, 0));
          fr.push(snap({ batch: [], say: `After ${steps} steps and ${updates} updates. ${right ? 'Q(s, right) is above Q(s, left) in every state, so the greedy policy goes right everywhere.' : 'The greedy policy does not yet go right in every state.'} The largest gap between the blue line and the ideal values (green) is ${f2(err, 3)}.${steps === 500 ? ' A straight line cannot match the curved ideal exactly, so a gap remains. A deep network has enough flexibility to bend.' : ''}` }));
        }
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      for (let i = 0; i < 6; i++) {
        rr(g, 10 + i * 48, 22, 42, 30, 5, { fill: i === 5 ? 'rgba(22,163,74,0.25)' : c.surf, stroke: c.line });
        D.text(g, i === 5 ? '5 +1' : String(i), 31 + i * 48, 42, { a: 'center', s: 12, b: true, c: i === 5 ? c.green : c.ink });
      }
      if (f.s !== undefined) D.circle(g, 31 + f.s * 48, 12, 7, { fill: klass(z, 0) });
      head(z, 'Replay memory (newest on the right)', 10, 74);
      for (let i = 0; i < 8; i++) {
        const b = f.buf[i], hot = f.batch && f.batch.includes(i);
        box(z, 10 + i * 36, 82, 32, 40, b ? `${b.s}${b.a ? '→' : '←'}${b.s2}` : '', { fill: hot ? klass(z, 1) : c.surf, c: hot ? '#fff' : c.ink, s: 11, mono: true, r: 4 });
      }
      D.text(g, 'orange: in this minibatch', 10, 138, { s: 10, c: c.ink2 });
      head(z, 'Weights  [w₀, w₁]', 10, 162);
      [['online left', f.W[0]], ['online right', f.W[1]], ['target left', f.T[0]], ['target right', f.T[1]]].forEach(([nm, w], i) => {
        D.text(g, nm, 10, 186 + i * 22, { s: 11, c: i < 2 ? klass(z, 0) : klass(z, 1), b: true });
        D.text(g, `[${f2(w[0], 3)}, ${f2(w[1], 3)}]`, 110, 186 + i * 22, { s: 11, mono: true, c: c.ink });
      });
      D.text(g, 'y = r + γ maxₐ′ Q_target(s′, a′)', 10, 286, { s: 11, mono: true, b: true, c: c.cv });
      D.text(g, 'w += lr × (y − Q(s, a)) × [1, s/5]', 10, 306, { s: 11, mono: true, b: true, c: c.cv });
      const P = plot(z, [312, 10, 278, 300], [0, 4], [-0.2, 1.1], { dx: 0, dy: 1, xl: 'state s', yl: 'Q(s, right)' });
      for (let k = 0; k <= 4; k++) D.circle(g, P.X(k), P.Y(ideal(k, 1)), 4, { fill: c.green });
      D.line(g, P.X(0), P.Y(qv(f.T, 0, 1)), P.X(4), P.Y(qv(f.T, 4, 1)), klass(z, 1), 2, [6, 4]);
      D.line(g, P.X(0), P.Y(qv(f.W, 0, 1)), P.X(4), P.Y(qv(f.W, 4, 1)), klass(z, 0), 3);
      D.text(g, 'blue: online   orange dashed: target   green: ideal', 320, 324, { s: 10, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Reinforcement 3.2  policy gradients: REINFORCE on the short corridor, and the PPO clipped objective
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, rng, plot, box } = MLZ;
  const nf = v => (Number.isInteger(v) ? String(v).replace('-', '−') : f2(v, 3).replace('-', '−'));
  const J = p => {                                         // start value of the short corridor for p(right) = p
    // v0 = v1 - 1/p, v2 = -1 + q v1, and v1 = -1 + p v0 + q v2 gives v1 = (-2 - q) / (1 - p - q^2)
    const q = 1 - p, v1 = (-2 - q) / (1 - p - q * q);
    return v1 - 1 / p;
  };
  const step = (s, right) => { let m = right ? 1 : -1; if (s === 1) m = -m; return Math.max(0, s + m); };

  trace('mlcorridorpg', {
    title: 'REINFORCE learns a stochastic policy',
    sub: 'The short corridor: in the middle cell the actions are swapped, and the agent cannot tell the cells apart, so it picks “right” with one probability p everywhere. Every step costs −1. The right chart shows the true value J(p) of every p, the left chart how p changes while REINFORCE learns.',
    W: 600, H: 330,
    params: [
      { k: 'b', label: 'Baseline', type: 'select', v: 'yes', opts: [['yes', 'Learned baseline'], ['no', 'No baseline']] },
      { k: 'a', label: 'Step size α', type: 'select', v: '9', opts: [['9', '2⁻⁹'], ['11', '2⁻¹¹'], ['13', '2⁻¹³']] },
      { k: 'p0', label: 'Starting p(right)', type: 'range', v: 0.1, min: 0.05, max: 0.95, step: 0.05 },
      { k: 'seed', label: 'Random seed', type: 'range', v: 1, min: 1, max: 30 }
    ],
    tips: [
      { t: 'No baseline with α = 2⁻¹³: every step is small, so p creeps up from 0.1 and is still well below 0.59 after 1000 episodes.', set: { b: 'no', a: '13', p0: 0.1, seed: 1 }, play: true },
      { t: 'Start at p = 0.9: the agent often gets stuck pressing right in the swapped cell, episodes are long, and REINFORCE pushes p down towards 0.59.', set: { b: 'yes', a: '9', p0: 0.9, seed: 1 }, play: true }
    ],
    frames(p) {
      const R = rng(+p.seed * 6007), al = 2 ** -(+p.a), useB = p.b === 'yes', aw = 2 ** -6;
      let h = Math.log(+p.p0 / (1 - +p.p0)), b = 0;
      const sig = x => 1 / (1 + Math.exp(-x)), hist = [];
      const fr = [{ pr: sig(h), hist: [], s: 0, say: `Start with p(right) = ${f2(sig(h), 2)}. The value of this policy is J = ${nf(J(sig(h)))}. The best possible is p = 0.59 with J = −11.66. Neither always right nor always left ever reaches the goal.` }];
      const show = [1, 2, 10, 50, 100, 200, 400, 700, 1000];
      for (let ep = 1; ep <= 1000; ep++) {
        const pr = sig(h);
        let s = 0; const acts = [];
        while (s !== 3 && acts.length < 1000) { const a = R() < pr ? 1 : 0; acts.push(a); s = step(s, a); }
        const T = acts.length, h0 = h;
        acts.forEach((a, t) => { const G = -(T - t), d = G - (useB ? b : 0); if (useB) b += aw * d; h += al * d * (a - pr); });
        hist.push(pr);
        if (show.includes(ep)) {
          const np = sig(h);
          fr.push({ pr: np, hist: hist.slice(), s: 3, acts: ep <= 2 ? acts : null, say: ep <= 2
            ? `Episode ${ep}: ${T} steps (${acts.slice(0, 14).map(a => (a ? 'R' : 'L')).join(' ')}${T > 14 ? ' …' : ''}), return ${nf(-T)}. Each step t adds α × (G<sub>t</sub>${useB ? ' − b' : ''}) × (a<sub>t</sub> − p) to the preference. p moves from ${f2(pr, 3)} to ${f2(np, 3)}.`
            : `After ${ep} episodes: p(right) = <b>${f2(np, 3)}</b>, true value J = ${nf(J(np))}${Math.abs(np - 0.59) < 0.05 ? ', close to the best −11.66' : ''}.${ep === 1000 ? ` The best policy is random on purpose: with these features a value based method that acts greedily could only pick always right or always left.` : ''}` });
        }
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      ['S', 'swap', '', 'G'].forEach((nm, i) => {
        rr(g, 14 + i * 68, 24, 60, 36, 6, { fill: i === 3 ? 'rgba(22,163,74,0.25)' : i === 1 ? 'rgba(234,88,12,0.18)' : c.surf, stroke: c.line });
        D.text(g, nm, 44 + i * 68, 47, { a: 'center', s: 12, b: true, c: i === 3 ? c.green : c.ink });
      });
      D.text(g, `p(right) = ${f2(f.pr, 3)}`, 14, 84, { s: 12, b: true, c: klass(z, 0) });
      const P = plot(z, [10, 96, 282, 228], [0, 1000], [0, 1], { dx: 0, dy: 1, xl: 'episode', yl: 'p(right)' });
      D.line(g, P.X(0), P.Y(0.59), P.X(1000), P.Y(0.59), c.green, 1.2, [5, 4]);
      for (let i = 1; i < f.hist.length; i++) D.line(g, P.X(i - 1), P.Y(f.hist[i - 1]), P.X(i), P.Y(f.hist[i]), klass(z, 0), 1.5);
      const Q = plot(z, [302, 10, 288, 314], [0, 1], [-60, 0], { dx: 1, dy: 0, xl: 'p(right)', yl: 'J(p), the start value' });
      let prev = null;
      for (let k = 2; k <= 98; k++) { const x = k / 100, y = Math.max(-60, J(x)); if (prev) D.line(g, Q.X(prev[0]), Q.Y(prev[1]), Q.X(x), Q.Y(y), c.ink2, 2); prev = [x, y]; }
      D.circle(g, Q.X(0.59), Q.Y(J(0.59)), 4, { fill: c.green });
      D.circle(g, Q.X(f.pr), Q.Y(Math.max(-60, J(f.pr))), 7, { fill: klass(z, 0) });
      D.text(g, 'green: best p = 0.59', 380, 300, { s: 10, c: c.ink2 });
    }
  });

  trace('mlppoclip', {
    title: 'The PPO clipped objective, piece by piece',
    sub: 'r is the probability ratio π_new(a|s) / π_old(a|s) for one sample, and A its advantage. PPO maximises min(r A, clip(r, 1 − ε, 1 + ε) A). Where the minimum is flat, the sample gives no gradient, so the policy cannot move too far from the old one.',
    W: 600, H: 330,
    params: [
      { k: 'sA', label: 'Advantage A', type: 'select', v: '1', opts: [['1', 'A = +1 (a good action)'], ['-1', 'A = −1 (a bad action)']] },
      { k: 'e', label: 'Clip range ε', type: 'range', v: 0.2, min: 0.1, max: 0.4, step: 0.05 },
      { k: 'r', label: 'Ratio r of one sample', type: 'range', v: 1.3, min: 0.4, max: 1.6, step: 0.05 }
    ],
    tips: [
      { t: 'A = −1 with r = 0.7: the bad action has already been made much less likely (r < 1 − ε), so the objective is flat there and the gradient is 0.', set: { sA: '-1', e: 0.2, r: 0.7 }, play: true },
      { t: 'A = +1 with r = 0.7: the good action became less likely, which the clip does not forgive. The min keeps the unclipped r A, and the gradient pushes r back up.', set: { sA: '1', e: 0.2, r: 0.7 }, play: true }
    ],
    frames(p) {
      const A = +p.sA, e = +p.e, r = +p.r, cl = Math.min(Math.max(r, 1 - e), 1 + e), L = Math.min(r * A, cl * A);
      const flat = (A > 0 && r > 1 + e) || (A < 0 && r < 1 - e), base = { A, e, r };
      return [
        { ...base, show: 1, say: `The plain surrogate r × A (blue). With A = ${A > 0 ? '+1' : '−1'}, ${A > 0 ? 'raising r always raises it, so without limits the update would push r as high as it can.' : 'lowering r always raises it, so without limits the update would push r towards 0.'}` },
        { ...base, show: 2, say: `The clipped version clip(r, ${f2(1 - e, 2)}, ${f2(1 + e, 2)}) × A (orange dashed). Outside the range [1 − ε, 1 + ε] it stays constant.` },
        { ...base, show: 3, say: `PPO takes the <b>minimum</b> of the two (thick line). It is a pessimistic bound: improvements beyond the clip are not counted, but losses always are.` },
        { ...base, show: 4, say: `Shaded: where the minimum is flat, so the gradient is 0. For A ${A > 0 ? '> 0 that is r > 1 + ε' : '< 0 that is r < 1 − ε'}: the policy has already moved far enough in the helpful direction.` },
        { ...base, show: 5, say: `This sample has r = ${f2(r, 2)}: r A = ${nf(+(r * A).toFixed(3))}, clipped term = ${nf(+(cl * A).toFixed(3))}, objective = <b>${nf(+L.toFixed(3))}</b>. ${flat ? 'It sits on the flat part, so it gives <b>no gradient</b>.' : 'It is on a sloped part, so it still gives a gradient.'}` }
      ];
    },
    paint(z, f) {
      const c = z.col, g = z.g, A = f.A, e = f.e;
      const P = plot(z, [10, 10, 580, 292], [0, 2], [-2, 2], { dx: 1, dy: 0, xl: 'ratio r', yl: 'objective for one sample' });
      D.line(g, P.X(0), P.Y(0), P.X(2), P.Y(0), c.ink2, 1);
      D.line(g, P.X(1), P.Y(-2), P.X(1), P.Y(2), c.ink2, 1, [3, 3]);
      const cl = r => Math.min(Math.max(r, 1 - e), 1 + e);
      if (f.show >= 4) {
        const [x0, x1] = A > 0 ? [1 + e, 2] : [0, 1 - e];
        g.save(); g.fillStyle = 'rgba(148,163,184,0.25)'; g.fillRect(P.X(x0), P.Y(2), P.X(x1) - P.X(x0), P.Y(-2) - P.Y(2)); g.restore();
        D.text(g, 'gradient 0', (P.X(x0) + P.X(x1)) / 2, P.Y(A > 0 ? -1 : 1), { a: 'center', s: 12, b: true, c: c.ink2 });
      }
      D.line(g, P.X(0), P.Y(0), P.X(2), P.Y(2 * A), klass(z, 0), 2);
      if (f.show >= 2) { const pts = [0, 1 - e, 1 + e, 2]; for (let i = 1; i < 4; i++) D.line(g, P.X(pts[i - 1]), P.Y(cl(pts[i - 1]) * A), P.X(pts[i]), P.Y(cl(pts[i]) * A), klass(z, 1), 2, [6, 4]); }
      if (f.show >= 3) { const pts = [0, 1 - e, 1, 1 + e, 2], m = r => Math.min(r * A, cl(r) * A); for (let i = 1; i < pts.length; i++) D.line(g, P.X(pts[i - 1]), P.Y(m(pts[i - 1])), P.X(pts[i]), P.Y(m(pts[i])), c.ink, 4); }
      if (f.show >= 5) { const y = Math.min(f.r * A, cl(f.r) * A); D.circle(g, P.X(f.r), P.Y(y), 8, { fill: c.red }); }
      D.text(g, `A = ${A > 0 ? '+1' : '−1'}, ε = ${f2(e, 2)}    blue: r A    orange: clip(r) A    black: the minimum`, 14, 322, { s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Reinforcement 3.3  RL in practice: Dyna-Q planning in a maze, and RLHF with a Bradley-Terry reward model
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, klass, rr, rng, plot, box } = MLZ;
  const MAZE = ['       #G', '  #    # ', 'S #    # ', '  #      ', '     #   ', '         '];
  const RW = 6, CW = 9, START = [2, 0], GOAL = [0, 8], MV = [[-1, 0], [1, 0], [0, -1], [0, 1]], ARW = ['↑', '↓', '←', '→'];
  const mstep = (s, a) => { let r = s[0] + MV[a][0], c = s[1] + MV[a][1]; if (r < 0 || r >= RW || c < 0 || c >= CW || MAZE[r][c] === '#') { r = s[0]; c = s[1]; } return [[r, c], r === GOAL[0] && c === GOAL[1] ? 1 : 0]; };

  trace('mldyna', {
    title: 'Dyna-Q: planning with a learned model',
    sub: 'The maze of Sutton and Barto example 8.1. Reaching G gives +1, everything else 0, γ = 0.95. After every real step the agent also replays n remembered steps from its model. Cell shading shows max Q, arrows the greedy action where Q is not zero.',
    W: 600, H: 330,
    params: [
      { k: 'n', label: 'Planning steps n per real step', type: 'select', v: '50', opts: [['0', 'n = 0 (plain Q learning)'], ['5', 'n = 5'], ['50', 'n = 50']] },
      { k: 'seed', label: 'Random seed', type: 'range', v: 1, min: 1, max: 30 }
    ],
    tips: [
      { t: 'n = 0: after two episodes only the cells right next to the goal have a value, because one real step updates one value.', set: { n: '0', seed: 1 }, play: true },
      { t: 'n = 50: by the end of episode 2, planning has spread value across most of the maze, and episode 2 is already short.', set: { n: '50', seed: 1 }, play: true }
    ],
    frames(p) {
      const n = +p.n, R = rng(+p.seed * 5303), al = 0.1, g = 0.95, eps = 0.1;
      const Q = {}, model = new Map(), keyOf = s => s[0] * CW + s[1], q = s => (Q[keyOf(s)] ||= [0, 0, 0, 0]);
      const greedy = s => { const v = q(s), m = Math.max(...v), t = [0, 1, 2, 3].filter(a => v[a] === m); return t[Math.floor(R() * t.length)]; };
      const snap = () => { const V = {}; for (const k in Q) V[k] = Q[k].slice(); return V; };
      const lens = [];
      const fr = [{ V: {}, lens: [], pos: START, say: `All Q values start at 0, so every action looks the same and the first episode is a random walk. Planning steps per real step: <b>${n}</b>.` }];
      for (let ep = 1; ep <= 30; ep++) {
        let s = START, t = 0, half = null;
        while (!(s[0] === GOAL[0] && s[1] === GOAL[1]) && t < 4000) {
          const a = R() < eps ? Math.floor(R() * 4) : greedy(s);
          const [s2, r] = mstep(s, a), done = r === 1;
          q(s)[a] += al * (r + (done ? 0 : g * Math.max(...q(s2))) - q(s)[a]);
          model.set(keyOf(s) * 4 + a, [s, a, s2, r]);
          const keys = [...model.values()];
          for (let i = 0; i < n; i++) { const [ps, pa, ps2, pr] = keys[Math.floor(R() * keys.length)]; const pd = pr === 1; q(ps)[pa] += al * (pr + (pd ? 0 : g * Math.max(...q(ps2))) - q(ps)[pa]); }
          s = s2; t++;
          if (ep === 2 && t === 10) half = { V: snap(), pos: s };
        }
        lens.push(t);
        if (ep === 2 && half) {
          const known = Object.values(half.V).filter(v => Math.max(...v) > 0).length;
          fr.push({ V: half.V, lens: lens.slice(0, 1), pos: half.pos, say: `Ten steps into episode 2. <b>${known}</b> ${known === 1 ? 'cell has' : 'cells have'} a value above 0. ${n === 0 ? 'Without planning, only the last step of episode 1 was learned, so value sits next to the goal.' : `Each real step also ran ${n} planning updates, so value from the goal has spread backwards through the remembered moves.`}` });
        }
        if ([1, 2, 3, 5, 10, 30].includes(ep)) {
          const known = Object.values(Q).filter(v => Math.max(...v) > 0).length;
          fr.push({ V: snap(), lens: lens.slice(), pos: GOAL, say: `Episode ${ep} took <b>${t}</b> steps (the shortest path is 14). ${known} ${known === 1 ? 'cell has' : 'cells have'} a value above 0.${ep === 1 ? ' Only now has the agent seen the reward once.' : ''}${ep === 30 ? ` Average over the last 5 episodes: ${f2(lens.slice(-5).reduce((x, y) => x + y, 0) / 5, 1)} steps. Exploration with ε = 0.1 keeps it a little above 14.` : ''}` });
        }
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, cs = 32, x0 = 10, y0 = 14;
      let vmax = 0; for (const k in f.V) vmax = Math.max(vmax, ...f.V[k]);
      for (let r = 0; r < RW; r++) for (let cc = 0; cc < CW; cc++) {
        const wall = MAZE[r][cc] === '#', v = f.V[r * CW + cc], m = v ? Math.max(...v) : 0;
        rr(g, x0 + cc * cs, y0 + r * cs, cs - 2, cs - 2, 4, { fill: wall ? c.ink2 : m > 0 ? `rgba(37,99,235,${0.12 + 0.6 * m / (vmax || 1)})` : c.surf, stroke: c.line });
        if (!wall && m > 0 && !(r === GOAL[0] && cc === GOAL[1])) D.text(g, ARW[v.indexOf(m)], x0 + cc * cs + 15, y0 + r * cs + 21, { a: 'center', s: 14, b: true, c: c.ink });
      }
      D.text(g, 'S', x0 + START[1] * cs + 15, y0 + START[0] * cs + 21, { a: 'center', s: 12, b: true, c: c.red });
      D.text(g, 'G', x0 + GOAL[1] * cs + 15, y0 + GOAL[0] * cs + 21, { a: 'center', s: 13, b: true, c: c.green });
      if (f.pos) D.circle(g, x0 + f.pos[1] * cs + 15, y0 + f.pos[0] * cs + 8, 4, { fill: klass(z, 1) });
      D.text(g, 'darker blue: higher max Q', x0, 226, { s: 11, c: c.ink2 });
      const P = plot(z, [310, 10, 280, 310], [1, 30], [0, 800], { dx: 0, dy: 0, xl: 'episode', yl: 'steps per episode (capped at 800)' });
      D.line(g, P.X(1), P.Y(14), P.X(30), P.Y(14), c.green, 1.2, [5, 4]);
      f.lens.forEach((v, i) => { D.circle(g, P.X(i + 1), P.Y(Math.min(800, v)), 3, { fill: klass(z, 0) }); if (i) D.line(g, P.X(i), P.Y(Math.min(800, f.lens[i - 1])), P.X(i + 1), P.Y(Math.min(800, v)), klass(z, 0), 1.5); });
    }
  });

  const ANS = ['wrong', 'vague', 'correct', 'correct and clear', 'too long', 'made up but confident'];
  const QUAL = [-2, -0.5, 1, 2, 0, -1], REF = [0.15, 0.30, 0.25, 0.05, 0.20, 0.05];
  const sig = x => 1 / (1 + Math.exp(-x));
  trace('mlrlhf', {
    title: 'RLHF in miniature: preferences, a reward model, and a KL leash',
    sub: 'One prompt with 6 possible answers. The reference model picks them with the grey probabilities. Labellers compare pairs, a Bradley–Terry reward model is fitted to their choices, and the tuned policy is π(y) ∝ π_ref(y) exp(r(y) / β).',
    W: 600, H: 330,
    params: [
      { k: 'fool', label: 'Labellers', type: 'select', v: 'yes', opts: [['no', 'Honest: they judge true quality'], ['yes', 'Fooled: a confident made up answer seems great']] },
      { k: 'beta', label: 'KL strength β', type: 'select', v: '1', opts: [['10', 'β = 10'], ['2', 'β = 2'], ['1', 'β = 1'], ['0.3', 'β = 0.3'], ['0.1', 'β = 0.1']] },
      { k: 'N', label: 'Number of comparisons', type: 'select', v: '400', opts: [['50', '50'], ['400', '400']] },
      { k: 'seed', label: 'Random seed', type: 'range', v: 1, min: 1, max: 30 }
    ],
    tips: [
      { t: 'Fooled labellers with β = 0.1: the policy puts almost everything on the made up answer, and true quality drops below the reference. This is reward hacking.', set: { fool: 'yes', beta: '0.1', N: '400', seed: 1 }, play: true },
      { t: 'Honest labellers with β = 0.3: the reward model is right, so a weak leash is safe and most probability moves to the best answers.', set: { fool: 'no', beta: '0.3', N: '400', seed: 1 }, play: true }
    ],
    frames(p) {
      const R = rng(+p.seed * 4441), beta = +p.beta, N = +p.N, seems = QUAL.slice();
      if (p.fool === 'yes') seems[5] = 3;
      const draw = () => { let u = R(), k = 0; while (k < 5 && u >= REF[k]) { u -= REF[k]; k++; } return k; };
      const pairs = [];
      while (pairs.length < N) { const i = draw(), j = draw(); if (i === j) continue; pairs.push(R() < sig(seems[i] - seems[j]) ? [i, j] : [j, i]); }
      const r = [0, 0, 0, 0, 0, 0];
      for (let it = 0; it < 1500; it++) { const gr = [0, 0, 0, 0, 0, 0]; pairs.forEach(([w, l]) => { const d = 1 - sig(r[w] - r[l]); gr[w] += d; gr[l] -= d; }); for (let k = 0; k < 6; k++) r[k] += 0.01 * gr[k] * 400 / N; const m = r.reduce((a, b) => a + b, 0) / 6; for (let k = 0; k < 6; k++) r[k] -= m; }
      const w = REF.map((pr, k) => pr * Math.exp(r[k] / beta)), Z = w.reduce((a, b) => a + b, 0), pi = w.map(x => x / Z);
      const EQ = v => v.reduce((a, x, k) => a + x * QUAL[k], 0), kl = pi.reduce((a, x, k) => a + (x > 0 ? x * Math.log(x / REF[k]) : 0), 0);
      const cnt = [0, 0, 0, 0, 0, 0]; pairs.forEach(([a, b]) => { cnt[a]++; cnt[b]++; });
      const base = { seems, fool: p.fool === 'yes' };
      return [
        { ...base, show: 1, say: `The reference model (after supervised fine tuning) gives these probabilities. Its expected true quality is ${f2(EQ(REF), 2)}. True qualities are hidden from the model: −2 for wrong up to +2 for correct and clear.` },
        { ...base, show: 2, pairs: pairs.slice(0, 4), say: `${N} comparisons of two answers drawn from the reference model. For example: ${pairs.slice(0, 3).map(([a, b]) => `“${ANS[a]}” beat “${ANS[b]}”`).join(', ')}. ${p.fool === 'yes' ? 'The labellers cannot check facts, so the made up answer seems better than it is.' : 'The labellers judge true quality.'} Rare answers are compared less often: ${ANS[3]} ${cnt[3]} times, ${ANS[5]} ${cnt[5]} times.` },
        { ...base, show: 3, r, say: `Fit the reward model by maximising Σ ln σ(r<sub>winner</sub> − r<sub>loser</sub>). Highest learned reward: <b>${ANS[r.indexOf(Math.max(...r))]}</b> (${f2(Math.max(...r), 2)}).${p.fool === 'yes' ? (r.indexOf(Math.max(...r)) === 5 ? ' The reward model faithfully learns what the labellers prefer, including their mistake.' : ' The labellers’ mistake still lifts the made up answer, though in this sample it is not the top reward.') : ''}` },
        { ...base, show: 4, r, pi, say: `Tune with β = ${beta}: π(y) ∝ π_ref(y) exp(r(y) / ${beta}). P(correct and clear) = ${f2(pi[3], 2)}, P(made up) = ${f2(pi[5], 2)}. KL from the reference = ${f2(kl, 2)}.` },
        { ...base, show: 5, r, pi, say: `Expected true quality: reference ${f2(EQ(REF), 2)}, tuned <b>${f2(EQ(pi), 2)}</b>. ${EQ(pi) < EQ(REF) ? 'Tuning made answers worse: the policy exploited an error in the reward model.' : EQ(pi) > EQ(REF) + 0.3 ? 'Tuning clearly helped.' : 'Tuning changed little.'} ${beta >= 2 ? 'A large β keeps the policy close to the reference.' : 'A small β lets the policy move far from the reference.'}` }
      ];
    },
    paint(z, f) {
      const c = z.col, g = z.g, y0 = 40, rh = 44;
      D.text(g, 'answer', 10, 24, { s: 11, b: true, c: c.ink2 });
      D.text(g, 'reference π_ref', 200, 24, { s: 11, b: true, c: c.ink2 });
      if (f.show >= 3) D.text(g, 'learned reward r', 330, 24, { s: 11, b: true, c: c.ink2 });
      if (f.show >= 4) D.text(g, 'tuned π', 480, 24, { s: 11, b: true, c: c.ink2 });
      ANS.forEach((nm, k) => {
        const y = y0 + k * rh;
        D.text(g, nm, 10, y + 16, { s: 12, b: true, c: c.ink });
        D.text(g, `true quality ${QUAL[k] > 0 ? '+' : ''}${String(QUAL[k]).replace('-', '−')}`, 10, y + 32, { s: 10, c: c.ink2 });
        rr(g, 200, y + 6, 110 * REF[k] / 0.35 + 2, 16, 3, { fill: c.ink2 });
        D.text(g, f2(REF[k], 2), 206 + 110 * REF[k] / 0.35, y + 19, { s: 10, c: c.ink2 });
        if (f.show >= 3) {
          const v = f.r[k], wbar = Math.min(60, Math.abs(v) * 20), mid = 400;
          rr(g, v >= 0 ? mid : mid - wbar, y + 6, wbar + 1, 16, 3, { fill: v >= 0 ? klass(z, 0) : c.red });
          D.line(g, mid, y + 2, mid, y + 26, c.line, 1);
          D.text(g, f2(v, 2).replace('-', '−'), v >= 0 ? mid - 6 : mid + 6, y + 19, { a: v >= 0 ? 'right' : 'left', s: 10, c: c.ink });
        }
        if (f.show >= 4) { rr(g, 480, y + 6, 90 * f.pi[k] + 2, 16, 3, { fill: klass(z, 1) }); D.text(g, f2(f.pi[k], 2), 486 + 90 * f.pi[k], y + 19, { s: 10, c: c.ink }); }
        if (f.show === 2 && k === 5 && f.fool) D.text(g, 'seems great to labellers', 200, y + 38, { s: 10, b: true, c: c.red });
      });
    }
  });
})();
