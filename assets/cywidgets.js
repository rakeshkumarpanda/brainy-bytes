/* ===== Complete Cybersecurity animations, part 1: Foundations.
   Every animation is a step by step trace built on MLZ.trace (assets/mlwidgets.js), which wraps CVZ.def
   (assets/cvviz.js). It starts empty. Each press of Step adds one piece of the picture and explains that piece in
   plain words under it, until the picture is complete. Play runs the steps, Back undoes one, and Reset puts every
   value back. assets/voiceteach.js reads each step aloud when the reader turns the voice on.
   Part 2 (cryptography) is in assets/cywidgets2.js and part 3 (systems, applications, operations and advanced)
   in assets/cywidgets3.js. Every attack shown here is a model on made up data. ===== */
const CYZ = (() => {
  const { D, f2, box, rr, fit, wrap } = MLZ;
  /* a word wrapped into a box of fixed width, centred lines */
  function cbox(z, x, y, w, h, lines, o = {}) {
    box(z, x, y, w, h, '', o);
    const L = Array.isArray(lines) ? lines : [lines];
    const s = o.s || 12, lh = s + 4, top = y + h / 2 - (L.length - 1) * lh / 2 + 4;
    L.forEach((t, i) => D.text(z.g, t, x + w / 2, top + i * lh, { a: 'center', s: fit(z.g, t, w - 8, s, { b: o.b }), b: o.b, c: o.c || z.col.ink, mono: o.mono }));
  }
  /* lines of "name value" or "name: value" pairs */
  function pairs(s, need) {
    return String(s).split(/\n+/).map(l => l.trim()).filter(Boolean).map(l => {
      const m = l.replace(/−/g, '-').match(/^(.*?)[\s:=]+(-?[\d.]+)\s*$/);
      if (!m) throw new Error(`Write each line as a name and a number, for example "${need}"`);
      return { name: m[1].trim(), v: +m[2] };
    });
  }
  const pct = v => f2(v * 100, v * 100 < 1 ? 2 : 1) + '%';
  /* a number as fixed width binary */
  const bin = (v, n = 8) => (v >>> 0).toString(2).padStart(n, '0').slice(-n);
  const hex = (v, n = 2) => (v >>> 0).toString(16).toUpperCase().padStart(n, '0');
  return { cbox, pairs, pct, bin, hex, D, f2, box, rr, fit, wrap };
})();

/* =====================================================================================================
   Foundations 1.1  the CIA triad: which security goal does an incident break?
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, D, wrap } = CYZ;
  const CASES = {
    leak: { name: 'A copy of a shop’s customer list is sold online', c: 1, i: 0, a: 0,
      cq: 'Yes. Names and phone numbers were seen by people who should never see them.', iq: 'No. The data itself was not changed, only copied.', aq: 'No. The shop could still use its list as normal.',
      fix: 'Encrypt the database, give staff access only to what they need, and log who reads it.' },
    marks: { name: 'A student logs in as a teacher and raises their own marks', c: 0, i: 1, a: 0,
      cq: 'Hardly. Marks are not very secret. The real damage is somewhere else.', iq: 'Yes. A record was changed by someone who had no right to change it.', aq: 'No. The marks system kept working.',
      fix: 'Strong logins with a second factor, change logs, and a check that only teachers can edit marks.' },
    ransom: { name: 'Ransomware locks every file in a hospital', c: 1, i: 1, a: 1,
      cq: 'Often yes. Modern gangs copy the files before locking them and threaten to publish them.', iq: 'Yes. The files were changed (encrypted) without permission.', aq: 'Yes, badly. Doctors cannot open patient records, so care stops.',
      fix: 'Offline backups that are tested, fast patching, splitting the network into parts, and a practised response plan.' },
    ddos: { name: 'A flood of fake traffic takes a ticket website down', c: 0, i: 0, a: 1,
      cq: 'No. Nothing secret was read.', iq: 'No. Nothing was changed.', aq: 'Yes. Real buyers cannot reach the site while it is flooded.',
      fix: 'A content delivery network and DDoS filtering service, rate limits, and extra capacity.' },
    tamper: { name: 'Someone changes the account number on a bill sent by email', c: 0, i: 1, a: 0,
      cq: 'Not the main problem. The bill was not very secret.', iq: 'Yes. The message was changed on the way, so money goes to the wrong account.', aq: 'No. The email arrived.',
      fix: 'Digital signatures on invoices, and a phone call to a known number before paying a changed account.' },
    shoulder: { name: 'A person reads your ATM PIN over your shoulder', c: 1, i: 0, a: 0,
      cq: 'Yes. A secret was seen by the wrong person.', iq: 'Not yet. Nothing has been changed so far.', aq: 'No. Your card still works.',
      fix: 'Cover the keypad, and use a second factor so a PIN alone is not enough.' }
  };
  const GOAL = [['c', 'Confidentiality', 'Only the right people can read it'], ['i', 'Integrity', 'Nobody can change it without being caught'], ['a', 'Availability', 'It works when the right people need it']];
  trace('cycia', {
    title: 'Which goal did the attack break? Confidentiality, integrity or availability',
    sub: 'Pick an incident. The animation asks the three questions a security analyst asks and lights up each goal that was broken.',
    W: 600, H: 330,
    params: [{ k: 'case', label: 'Incident', type: 'select', v: 'leak', opts: Object.keys(CASES).map(k => [k, CASES[k].name]) }],
    tips: [
      { t: 'Try the ransomware case. It breaks all three goals, which is why it is the most feared attack today.', set: { case: 'ransom' }, play: true },
      { t: 'Try the flood of fake traffic. Nothing is read or changed, yet the site is useless. That is an attack on availability only.', set: { case: 'ddos' }, play: true }
    ],
    frames(p) {
      const t = CASES[p.case];
      const fr = [{ k: 0, say: `The incident: <b>${t.name}</b>. Every security goal fits in three letters, C, I and A. We check them one at a time.` }];
      fr.push({ k: 1, say: `<b>Confidentiality</b>: was something secret seen by the wrong person? ${t.cq}` });
      fr.push({ k: 2, say: `<b>Integrity</b>: was something changed by someone who had no right to change it? ${t.iq}` });
      fr.push({ k: 3, say: `<b>Availability</b>: could the right people still use it when they needed it? ${t.aq}` });
      const hit = GOAL.filter(g => t[g[0]]).map(g => g[1]);
      fr.push({ k: 4, done: true, say: `So this incident breaks <b>${hit.join(', ').replace(/, ([^,]*)$/, ' and $1')}</b>. A defender picks controls for the goals that broke: ${t.fix}` });
      return fr;
    },
    paint(z, f) {
      const t = CASES[z.p.case], c = z.col, g = z.g;
      cbox(z, 14, 10, 572, 38, t.name, { b: true, s: 14, fill: c.bg });
      const P = [[300, 84], [140, 208], [460, 208]];
      D.line(g, P[0][0], P[0][1], P[1][0], P[1][1], c.line, 2); D.line(g, P[1][0], P[1][1], P[2][0], P[2][1], c.line, 2); D.line(g, P[2][0], P[2][1], P[0][0], P[0][1], c.line, 2);
      D.text(g, 'the data or service', 300, 172, { a: 'center', s: 12, c: c.ink2 });
      GOAL.forEach(([k, name, mean], i) => {
        const shown = f.k > i, broke = shown && t[k];
        const [x, y] = P[i];
        D.circle(g, x, y, 30, { fill: !shown ? c.surf : broke ? c.red : c.green, stroke: shown ? (broke ? c.red : c.green) : c.line, w: 2 });
        D.text(g, k.toUpperCase(), x, y + 7, { a: 'center', s: 22, b: true, c: shown ? '#fff' : c.ink2 });
        const ly = i === 0 ? y - 4 : y + 48, lx = i === 0 ? x + 44 : x;
        D.text(g, name, lx, ly, { a: i === 0 ? 'left' : 'center', s: 13, b: true, c: c.ink });
        if (shown) D.text(g, broke ? 'broken' : 'safe', lx, ly + 16, { a: i === 0 ? 'left' : 'center', s: 12, b: true, c: broke ? c.red : c.green });
        if (shown && i > 0) wrap(g, mean, lx - 80, ly + 32, 160, { s: 11, c: c.ink2, lh: 14 });
        else if (shown) wrap(g, mean, lx, ly + 32, 160, { s: 11, c: c.ink2, lh: 14 });
      });
      if (f.done) head(z, 'Red means this goal was broken', 14, 70, { c: c.red });
    }
  });
})();

/* =====================================================================================================
   Foundations 1.1  defence in depth: how layers multiply the attacker's chance of failure
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, pairs, pct, D, f2, rr } = CYZ;
  trace('cylayers', {
    title: 'Defence in depth: each layer stops some attacks',
    sub: 'Each line is one layer of defence and the chance that it misses an attack. The animation sends attacks through the layers one by one and counts how many get past each.',
    W: 600, H: 340,
    params: [
      { k: 'layers', label: 'Layers: name and miss chance (0 to 1)', type: 'area', v: 'email filter 0.3\nuser training 0.5\nantivirus 0.4\nMFA login 0.1' },
      { k: 'n', label: 'Attacks tried', type: 'range', v: 1000, min: 100, max: 10000, step: 100 }
    ],
    tips: [
      { t: 'Play it. Watch 1000 phishing emails shrink to a handful, even though no single layer is perfect.', play: true },
      { t: 'Delete the MFA line and play again. The breaches jump about ten times, because that one layer missed only 1 in 10.', set: { layers: 'email filter 0.3\nuser training 0.5\nantivirus 0.4' }, play: true },
      { t: 'Use one very strong layer, "firewall 0.02", alone. One layer can be good, but if it fails or is switched off there is nothing behind it.', set: { layers: 'firewall 0.02' }, play: true }
    ],
    frames(p) {
      const L = pairs(p.layers, 'antivirus 0.4');
      if (!L.length) throw new Error('Give at least one layer.');
      L.forEach(l => { if (l.v < 0 || l.v > 1) throw new Error(`The miss chance of ${l.name} must be between 0 and 1.`); });
      if (L.length > 7) throw new Error('Use at most 7 layers so the picture fits.');
      const fr = [{ k: 0, left: [p.n], say: `<b>${p.n}</b> attacks arrive, for example phishing emails sent to a company. In front of the company there are ${L.length} layers of defence. No layer is perfect. Each one misses some attacks.` }];
      let left = p.n, prod = 1;
      const hist = [p.n];
      L.forEach((l, i) => {
        const before = left;
        left = left * l.v; prod *= l.v;
        hist.push(left);
        fr.push({ k: i + 1, left: hist.slice(), say: `Layer ${i + 1}, <b>${l.name}</b>, misses ${pct(l.v)} of what reaches it. ${f2(before, 1)} attacks reach it, ${f2(before - left, 1)} are stopped and <b>${f2(left, 1)}</b> get past. Chance of getting this far: ${L.slice(0, i + 1).map(x => x.v).join(' × ')} = ${f2(prod, 4)}.` });
      });
      fr.push({ k: L.length + 1, left: hist, done: true, prod, say: `An attack succeeds only if <b>every</b> layer misses it. If the layers fail independently, the chances multiply: P(breach) = ${L.map(x => x.v).join(' × ')} = <b>${f2(prod, 4)}</b>. So about <b>${f2(p.n * prod, 1)}</b> of ${p.n} attacks get through. Many ordinary layers together beat one great layer, and that idea is called <b>defence in depth</b>. Real layers are not fully independent (a clever attacker may beat two at once), so treat this as the best case.` });
      return fr.map(x => ({ ...x, L }));
    },
    paint(z, f) {
      const c = z.col, g = z.g, L = f.L, n = z.p.n;
      head(z, 'Attacks still alive after each layer', 14, 20);
      const top = 34, rowH = Math.min(36, 262 / (L.length + 1));
      const all = [{ name: 'arrive', v: 1 }].concat(L);
      all.forEach((l, i) => {
        const y = top + i * rowH;
        if (i > f.k) return;
        const v = f.left[i];
        cbox(z, 14, y, 130, rowH - 6, i === 0 ? 'attacks arrive' : `${i}. ${l.name}`, { s: 12, b: i === 0, fill: i === 0 ? c.bg : c.surf });
        const w = Math.max(2, v / n * 330);
        rr(g, 156, y + 3, w, rowH - 12, 4, { fill: i === 0 ? c.orange : i === L.length && f.done ? c.red : c.cv });
        D.text(g, f2(v, v < 10 ? 2 : 0), 162 + w, y + rowH / 2, { s: 12, b: true, c: c.ink });
        if (i > 0) D.text(g, `misses ${pct(l.v)}`, 590, y + rowH / 2, { a: 'right', s: 11, c: c.ink2 });
      });
      if (f.done) cbox(z, 14, 300, 572, 32, `P(breach) = product of the miss chances = ${f2(f.prod, 4)}   about ${f2(n * f.prod, 1)} of ${n} get through`, { s: 13, b: true, fill: c.bg, c: c.red });
    }
  });
})();

/* =====================================================================================================
   Foundations 1.2  the risk matrix: likelihood times impact on a heat map
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, D, rr } = CYZ;
  const ZONE = s => s >= 16 ? ['critical', 'red'] : s >= 10 ? ['high', 'orange'] : s >= 5 ? ['medium', 'yellow'] : ['low', 'green'];
  function parse(txt) {
    const out = String(txt).split(/\n+/).map(l => l.trim()).filter(Boolean).map(l => {
      const m = l.match(/^(.*?)\s+(\d)\s+(\d)\s*$/);
      if (!m) throw new Error('Write each risk as a name, a likelihood 1 to 5 and an impact 1 to 5, for example "phishing 4 3".');
      const L = +m[2], I = +m[3];
      if (L < 1 || L > 5 || I < 1 || I > 5) throw new Error(`Likelihood and impact of "${m[1]}" must be from 1 to 5.`);
      return { name: m[1], L, I, s: L * I };
    });
    if (!out.length) throw new Error('Give at least one risk.');
    if (out.length > 8) throw new Error('Use at most 8 risks so the picture stays readable.');
    return out;
  }
  trace('cyrisk', {
    title: 'The risk matrix: place each risk by likelihood and impact',
    sub: 'Each line is a risk with a likelihood and an impact from 1 (very low) to 5 (very high). The animation places them one by one, works out the score, and lists which ones go above the risk appetite.',
    W: 600, H: 340,
    params: [
      { k: 'risks', label: 'Risks: name likelihood impact', type: 'area', v: 'phishing 4 3\nlaptop theft 3 2\nransomware 2 5\nwebsite down 3 3\nflood 1 4' },
      { k: 'app', label: 'Risk appetite (highest score we accept)', type: 'range', v: 8, min: 1, max: 25 }
    ],
    tips: [
      { t: 'Play it. Ransomware is not the most likely risk, but its impact puts it in the high zone.', play: true },
      { t: 'Lower the appetite to 4, a very careful bank. Now almost every risk needs treatment.', set: { app: 4 }, play: true },
      { t: 'Add "insider 5 5". A score of 25 is the worst possible: likely and very damaging.', set: { risks: 'phishing 4 3\nlaptop theft 3 2\nransomware 2 5\nwebsite down 3 3\nflood 1 4\ninsider 5 5' }, play: true }
    ],
    frames(p) {
      const R = parse(p.risks);
      const fr = [{ k: 0, say: 'This is an empty <b>risk matrix</b>. Across is <b>likelihood</b> (how often it may happen), up is <b>impact</b> (how bad one event is). Each cell has a score: likelihood × impact. The colour bands go from low (green) to critical (red).' }];
      R.forEach((r, i) => fr.push({ k: i + 1, say: `<b>${r.name}</b>: likelihood ${r.L}, impact ${r.I}. Score = ${r.L} × ${r.I} = <b>${r.s}</b>, which is <b>${ZONE(r.s)[0]}</b>. ${r.s > p.app ? `That is above the appetite of ${p.app}, so it must be treated.` : `That is within the appetite of ${p.app}, so it can be accepted and watched.`}` }));
      const sorted = R.slice().sort((a, b) => b.s - a.s);
      const over = sorted.filter(r => r.s > p.app);
      fr.push({ k: R.length + 1, done: true, sorted, say: `Sorted by score: ${sorted.map(r => `${r.name} ${r.s}`).join(', ')}. ${over.length ? `<b>${over.map(r => r.name).join(', ')}</b> ${over.length > 1 ? 'are' : 'is'} above the appetite and need a response: reduce, transfer, avoid or (with sign off) accept.` : 'Nothing is above the appetite, so every risk can be accepted and watched.'} This picture is the most common way to show risk to a manager in one look.` });
      return fr.map(x => ({ ...x, R }));
    },
    paint(z, f) {
      const c = z.col, g = z.g, R = f.R, x0 = 60, y0 = 24, cw = 52, ch = 52;
      for (let L = 1; L <= 5; L++) for (let I = 1; I <= 5; I++) {
        const x = x0 + (L - 1) * cw, y = y0 + (5 - I) * ch, col = c[ZONE(L * I)[1]];
        rr(g, x, y, cw - 3, ch - 3, 5, { fill: col, stroke: c.line, w: 0.6 });
        g.save(); g.globalAlpha = 0.72; rr(g, x, y, cw - 3, ch - 3, 5, { fill: c.surf }); g.restore();
        D.text(g, String(L * I), x + cw - 8, y + 13, { a: 'right', s: 10, c: c.ink2 });
      }
      for (let i = 1; i <= 5; i++) {
        D.text(g, String(i), x0 + (i - 0.5) * cw - 1, y0 + 5 * ch + 14, { a: 'center', s: 11, b: true, c: c.ink2 });
        D.text(g, String(i), x0 - 10, y0 + (5 - i + 0.5) * ch + 4, { a: 'center', s: 11, b: true, c: c.ink2 });
      }
      D.text(g, 'likelihood', x0 + 2.5 * cw, y0 + 5 * ch + 32, { a: 'center', s: 12, b: true, c: c.ink2 });
      g.save(); g.translate(22, y0 + 2.5 * ch); g.rotate(-Math.PI / 2); D.text(g, 'impact', 0, 0, { a: 'center', s: 12, b: true, c: c.ink2 }); g.restore();
      const cellCount = {};
      R.slice(0, f.k).forEach((r, i) => {
        const key = r.L + ',' + r.I, n = cellCount[key] = (cellCount[key] || 0) + 1;
        const x = x0 + (r.L - 0.5) * cw - 1 + (n - 1) * 12 - 6 * (n > 1), y = y0 + (5 - r.I + 0.5) * ch + 2 + (n - 1) * 6;
        D.circle(g, x, y, 11, { fill: c[ZONE(r.s)[1]], stroke: c.ink, w: i === f.k - 1 && !f.done ? 2.5 : 1 });
        D.text(g, String(i + 1), x, y + 4, { a: 'center', s: 11, b: true, c: '#fff' });
      });
      head(z, f.done ? 'Sorted by score' : 'Risks placed so far', 350, 26);
      const list = f.done ? f.sorted : R.slice(0, f.k);
      list.forEach((r, i) => {
        const y = 38 + i * 32, n = R.indexOf(r) + 1, over = r.s > z.p.app;
        cbox(z, 350, y, 236, 27, `${n}. ${r.name}   ${r.L} × ${r.I} = ${r.s}`, { s: 12, b: over && f.done, fill: over && f.done ? 'rgba(220,38,38,0.12)' : c.surf, stroke: over && f.done ? c.red : c.line });
      });
      if (f.done) D.text(g, `appetite: accept scores up to ${z.p.app}`, 350, 322, { s: 12, b: true, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Foundations 1.2  an attack tree: the cheapest way in and the chance of success, worked out from the leaves up
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, D, f2, pct } = CYZ;
  const TREE = { id: 'root', name: 'Steal customer data', op: 'OR', kids: [
    { id: 'phish', name: 'Take over an admin', op: 'AND', kids: [{ id: 'mail', name: 'phishing email' }, { id: 'mfa', name: 'beat MFA' }] },
    { id: 'sqli', name: 'SQL injection' },
    { id: 'bribe', name: 'Bribe an insider' },
    { id: 'backup', name: 'Steal a backup', op: 'AND', kids: [{ id: 'disk', name: 'steal disk' }, { id: 'crack', name: 'crack encryption' }] }] };
  const POS = { root: [300, 22], phish: [85, 112], sqli: [235, 112], bribe: [375, 112], backup: [515, 112], mail: [55, 214], mfa: [160, 214], disk: [440, 214], crack: [545, 214] };
  const LEAVES = ['mail', 'mfa', 'sqli', 'bribe', 'disk', 'crack'];
  function parse(txt) {
    const v = {};
    String(txt).split(/\n+/).map(l => l.trim()).filter(Boolean).forEach(l => {
      const m = l.match(/^(\w+)\s+([\d.]+)\s+([\d.]+)$/);
      if (!m) throw new Error('Write each leaf as: id cost chance, for example "sqli 3 0.1".');
      if (!LEAVES.includes(m[1])) throw new Error(`Unknown leaf "${m[1]}". Use ${LEAVES.join(', ')}.`);
      if (+m[3] > 1) throw new Error(`The chance of ${m[1]} must be between 0 and 1.`);
      v[m[1]] = { cost: +m[2], p: +m[3] };
    });
    LEAVES.forEach(k => { if (!v[k]) throw new Error(`Give a cost and a chance for the leaf "${k}".`); });
    return v;
  }
  trace('cyattacktree', {
    title: 'Attack tree: what is the cheapest way in?',
    sub: 'The goal sits at the top. An OR node needs any one child, an AND node needs every child. The animation works from the leaves up, so you see the cost and the chance of every route.',
    W: 600, H: 340,
    params: [
      { k: 'leaves', label: 'Leaves: id cost(thousand) chance', type: 'area', v: 'mail 1 0.3\nmfa 5 0.2\nsqli 3 0.1\nbribe 20 0.5\ndisk 4 0.2\ncrack 50 0.01' },
      { k: 'mode', label: 'Work out', type: 'select', v: 'cost', opts: [['cost', 'the cheapest cost of each route'], ['p', 'the chance that each route works']] }
    ],
    tips: [
      { t: 'Play it in cost mode. The cheapest route decides the attacker’s price, so that is the route to fix first.', play: true },
      { t: 'Switch to chance mode. Bribing an insider is expensive but very likely to work.', set: { mode: 'p' }, play: true },
      { t: 'Fix the SQL injection bug: make it cost 100 with chance 0.001. The cheapest route moves to the admin takeover.', set: { leaves: 'mail 1 0.3\nmfa 5 0.2\nsqli 100 0.001\nbribe 20 0.5\ndisk 4 0.2\ncrack 50 0.01' }, play: true }
    ],
    frames(p) {
      const v = parse(p.leaves), val = {}, fr = [], cost = p.mode === 'cost';
      fr.push({ val: {}, say: `The goal at the top is <b>${TREE.name}</b>. Below it are four routes. Two routes need two things to work together (AND). We will compute ${cost ? 'the <b>cheapest cost</b>' : 'the <b>chance of success</b>'} from the bottom up.` });
      LEAVES.forEach(k => { val[k] = cost ? v[k].cost : v[k].p; });
      fr.push({ val: { ...val }, leaves: true, say: `First the leaves, the real actions an attacker can take. Each has ${cost ? 'a cost in thousands' : 'a chance of working'}: ${LEAVES.map(k => `${k} ${cost ? v[k].cost : v[k].p}`).join(', ')}.` });
      TREE.kids.forEach(n => {
        if (!n.kids) { fr.push({ val: { ...val, [n.id]: val[n.id] }, cur: n.id, say: `<b>${n.name}</b> is a single action, so its value stays ${cost ? val[n.id] : f2(val[n.id], 3)}.` }); return; }
        const xs = n.kids.map(k => val[k.id]);
        val[n.id] = cost ? xs.reduce((a, b) => a + b, 0) : xs.reduce((a, b) => a * b, 1);
        fr.push({ val: { ...val }, cur: n.id, say: `<b>${n.name}</b> is an AND node: every child must succeed. ${cost ? `Costs add: ${xs.join(' + ')} = <b>${val[n.id]}</b>.` : `Chances multiply: ${xs.map(x => f2(x, 3)).join(' × ')} = <b>${f2(val[n.id], 4)}</b>.`}` });
      });
      const xs = TREE.kids.map(k => val[k.id]);
      if (cost) {
        val.root = Math.min(...xs);
        const best = TREE.kids[xs.indexOf(val.root)];
        fr.push({ val: { ...val }, cur: 'root', best: best.id, done: true, say: `The root is an OR node: one route is enough, so the attacker picks the cheapest. min(${xs.join(', ')}) = <b>${val.root}</b> by <b>${best.name}</b>. Defenders should raise the cost of this route first, because a strong lock elsewhere does not help while this one is cheap.` });
      } else {
        val.root = 1 - xs.reduce((a, b) => a * (1 - b), 1);
        fr.push({ val: { ...val }, cur: 'root', done: true, say: `The root is an OR node. If the attacker tries every route and they are independent, the goal fails only when every route fails: P = 1 − ${xs.map(x => `(1 − ${f2(x, 3)})`).join(' × ')} = <b>${f2(val.root, 4)}</b>, about ${pct(val.root)}.` });
      }
      return fr.map(x => ({ ...x, cost }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const draw = (n, par) => {
        const [x, y] = POS[n.id];
        if (par) { const [px, py] = POS[par.id]; D.line(g, px, py + 40, x, y, c.line, 1.4); }
        (n.kids || []).forEach(k => draw(k, n));
        const leaf = !n.kids, small = ['mail', 'mfa', 'disk', 'crack'].includes(n.id);
        const w = n.id === 'root' ? 200 : small ? 100 : 124;
        const shown = n.id in f.val, isBest = f.best === n.id, cur = f.cur === n.id;
        const v = shown ? (f.cost ? String(f.val[n.id]) : f2(f.val[n.id], 3)) : '';
        const lines = leaf ? (shown ? [n.name, (f.cost ? 'cost ' : 'chance ') + v] : [n.name]) : [shown ? `${n.name}: ${v}` : n.name, n.op + ' node'];
        cbox(z, x - w / 2, y, w, 40, lines, { s: 11, b: shown, fill: isBest ? c.red : cur ? c.cv : shown ? c.bg : c.surf, c: isBest || cur ? '#fff' : c.ink, stroke: isBest ? c.red : cur ? c.cv : c.line, w: cur || isBest ? 2.5 : 1.2 });
      };
      draw(TREE);
      head(z, f.cost ? 'AND: add the costs.  OR: take the cheapest.' : 'AND: multiply the chances.  OR: 1 minus the product of the failure chances.', 14, 300);
      if (f.done) D.text(g, f.cost ? `Cheapest attack costs ${f.val.root} thousand` : `Chance the goal is reached: ${f2(f.val.root, 4)}`, 14, 324, { s: 13, b: true, c: c.red });
    }
  });
})();
