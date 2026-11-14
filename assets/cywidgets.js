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

/* =====================================================================================================
   Foundations 1.3  decimal to binary by repeated division, then binary to hex by groups of four bits
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, D, bin, hex } = CYZ;
  trace('cybinary', {
    title: 'Decimal to binary and hex, the way a computer stores it',
    sub: 'Type a number from 0 to 4095. The animation divides it by 2 again and again, reads the remainders from the bottom up to get binary, then groups the bits in fours to get hexadecimal.',
    W: 600, H: 340,
    params: [{ k: 'n', label: 'Number (0 to 4095)', type: 'text', v: '202' }, { k: 'ch', label: 'Or a single character (leave the number empty)', type: 'text', v: '' }],
    tips: [
      { t: 'Play it with 202. You get 11001010 in binary and CA in hex.', play: true },
      { t: 'Clear the number and type the letter A. Characters are stored as numbers too: A is 65.', set: { n: '', ch: 'A' }, play: true },
      { t: 'Try 255, the biggest value of one byte: eight ones, and FF in hex.', set: { n: '255', ch: '' }, play: true }
    ],
    frames(p) {
      let n, from = '';
      if (String(p.n).trim() === '') {
        const ch = String(p.ch);
        if (ch.length !== 1) throw new Error('Type a number, or clear it and type exactly one character.');
        n = ch.codePointAt(0); from = `The character "${ch}" is stored as the number <b>${n}</b> (its Unicode code point). `;
        if (n > 4095) throw new Error('That character has a code above 4095. Try a letter, digit or symbol from the keyboard.');
      } else {
        n = Number(String(p.n).trim());
        if (!Number.isInteger(n) || n < 0 || n > 4095) throw new Error('Use a whole number from 0 to 4095.');
      }
      const rows = [];
      let q = n;
      if (q === 0) rows.push([0, 0, 0]);
      while (q > 0) { rows.push([q, Math.floor(q / 2), q % 2]); q = Math.floor(q / 2); }
      const bits = n.toString(2), width = Math.max(4, Math.ceil(bits.length / 4) * 4), padded = bits.padStart(width, '0');
      const fr = [{ k: 0, say: `${from}We want <b>${n}</b> in base 2 (binary). Binary uses only 0 and 1. The trick: divide by 2 and keep the remainder, again and again.` }];
      rows.forEach((r, i) => fr.push({ k: 1 + i, say: `${r[0]} ÷ 2 = ${r[1]} remainder <b>${r[2]}</b>. ${r[1] === 0 ? 'The quotient is 0, so we stop.' : `Carry on with ${r[1]}.`}` }));
      fr.push({ k: rows.length + 1, read: true, say: `Read the remainders from the <b>bottom up</b>: ${n} = <b>${bits}</b> in binary. Check: ${bits.split('').map((b, i) => b === '1' ? 2 ** (bits.length - 1 - i) : null).filter(v => v !== null).join(' + ') || '0'} = ${n}.` });
      const groups = padded.match(/.{4}/g);
      fr.push({ k: rows.length + 2, read: true, groups, say: `For hex, pad to ${width} bits and cut into groups of four: ${groups.join(' ')}. Each group of four is one hex digit from 0 to F.` });
      fr.push({ k: rows.length + 3, read: true, groups, done: true, say: `${groups.map(g => `${g} = ${parseInt(g, 2)} = <b>${parseInt(g, 2).toString(16).toUpperCase()}</b>`).join(', ')}. So ${n} = <b>0x${hex(n, groups.length)}</b>. Hex is popular in security because one byte is always exactly two hex digits.` });
      return fr.map(x => ({ ...x, rows, n, bits, groups: x.groups }));
    },
    paint(z, f) {
      const c = z.col, g = z.g, rowH = Math.min(22, 250 / f.rows.length);
      head(z, 'Divide by 2', 20, 22);
      f.rows.slice(0, f.k).forEach((r, i) => {
        const y = 32 + i * rowH;
        D.text(g, `${r[0]} ÷ 2 = ${r[1]}`, 20, y + rowH * 0.7, { s: 13, mono: true, c: c.ink });
        cbox(z, 190, y + 1, 30, rowH - 3, String(r[2]), { s: 13, b: true, mono: true, fill: f.read ? c.cv : c.bg, c: f.read ? '#fff' : c.ink });
      });
      if (f.read && f.rows.length > 1) { const y1 = 32 + (f.rows.length - 1) * rowH + rowH / 2, y2 = 40; D.arrow(g, 236, y1, 236, y2, c.orange, 2, 8); D.text(g, 'read up', 244, (y1 + y2) / 2, { s: 11, b: true, c: c.orange }); }
      if (f.read) {
        head(z, 'Binary', 320, 22);
        const b = f.bits, cw = Math.min(22, 250 / b.length);
        b.split('').forEach((d, i) => { cbox(z, 320 + i * cw, 32, cw - 2, 30, d, { s: 14, b: true, mono: true, fill: d === '1' ? c.cv : c.surf, c: d === '1' ? '#fff' : c.ink }); D.text(g, String(2 ** (b.length - 1 - i)), 320 + i * cw + cw / 2 - 1, 76, { a: 'center', s: 8, c: c.ink2 }); });
      }
      if (f.groups) {
        head(z, 'Groups of four bits', 320, 110);
        f.groups.forEach((gp, i) => {
          const x = 320 + i * 88;
          cbox(z, x, 120, 80, 30, gp, { s: 14, mono: true, b: true, fill: c.bg });
          if (f.done) { D.arrow(g, x + 40, 152, x + 40, 178, c.ink2, 1.4, 6); cbox(z, x + 15, 182, 50, 34, parseInt(gp, 2).toString(16).toUpperCase(), { s: 18, mono: true, b: true, fill: c.orange, c: '#fff' }); }
        });
        if (f.done) D.text(g, `${f.n} = 0b${f.bits} = 0x${f.groups.map(x => parseInt(x, 2).toString(16).toUpperCase()).join('')}`, 320, 250, { s: 13, b: true, mono: true, c: c.ink });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 1.3  XOR, bit by bit: encrypt with a key, then XOR again with the same key to get the message back
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, D, bin, hex } = CYZ;
  trace('cyxor', {
    title: 'XOR: the switch that undoes itself',
    sub: 'Type a short message and a key. Each letter becomes 8 bits. XOR gives 1 where the two bits differ and 0 where they match. XOR with the same key again brings the message back.',
    W: 600, H: 340,
    params: [{ k: 'msg', label: 'Message (1 to 6 letters)', type: 'text', v: 'HI' }, { k: 'key', label: 'Key (repeats if shorter)', type: 'text', v: 'K' }],
    tips: [
      { t: 'Play it. Watch each bit flip where the key has a 1 and stay where the key has a 0.', play: true },
      { t: 'Make the key the same as the message. Every bit matches, so the result is all zeros. That is why a⊕a = 0.', set: { msg: 'CAT', key: 'CAT' }, play: true },
      { t: 'Use a one letter key on a longer message. The same key byte repeats, and that repetition is what codebreakers hunt for.', set: { msg: 'AAAAAA', key: 'Z' }, play: true }
    ],
    frames(p) {
      const m = String(p.msg), k = String(p.key);
      if (m.length < 1 || m.length > 6) throw new Error('Use a message of 1 to 6 characters.');
      if (!k.length) throw new Error('The key needs at least one character.');
      if ([...m + k].some(ch => ch.charCodeAt(0) > 255)) throw new Error('Use plain keyboard characters.');
      const cols = [...m].map((ch, i) => { const a = ch.charCodeAt(0), b = k.charCodeAt(i % k.length); return { ch, kc: k[i % k.length], a, b, x: a ^ b }; });
      const fr = [{ k: 0, say: `Message <b>${m}</b>, key <b>${k}</b>. Computers store each character as a byte, 8 bits. XOR compares two bits: <b>different gives 1, same gives 0</b>.` }];
      cols.forEach((cl, i) => fr.push({ k: i + 1, say: `"${cl.ch}" = ${cl.a} = ${bin(cl.a)}. Key "${cl.kc}" = ${cl.b} = ${bin(cl.b)}. XOR bit by bit = <b>${bin(cl.x)}</b> = 0x${hex(cl.x)}. ${cl.x === 0 ? 'All bits matched, so the result is zero.' : `${bin(cl.a ^ cl.b).split('').filter(v => v === '1').length} bits flipped.`}` }));
      fr.push({ k: cols.length + 1, dec: true, say: `The encrypted bytes are <b>${cols.map(c => hex(c.x)).join(' ')}</b> (hex). They look like noise. Now XOR them with the same key again: (m ⊕ k) ⊕ k = m ⊕ (k ⊕ k) = m ⊕ 0 = <b>m</b>. The message <b>${m}</b> comes back. This is the heart of stream ciphers and the one time pad.` });
      return fr.map(x => ({ ...x, cols }));
    },
    paint(z, f) {
      const c = z.col, g = z.g, cols = f.cols, cw = Math.min(92, 470 / cols.length), x0 = 110;
      const rows = [['message', 26], ['bits', 60], ['key', 96], ['key bits', 130], ['XOR', 172], ['hex', 206]];
      rows.forEach(([t, y]) => D.text(g, t, 14, y + 18, { s: 12, b: true, c: c.ink2 }));
      D.line(g, x0 - 6, 162, x0 + cols.length * cw, 162, c.line, 1.5);
      cols.forEach((cl, i) => {
        if (i >= f.k) return;
        const x = x0 + i * cw, w = cw - 6;
        cbox(z, x, 26, w, 26, cl.ch, { s: 14, b: true, fill: c.bg });
        cbox(z, x, 60, w, 26, bin(cl.a), { s: 11, mono: true });
        cbox(z, x, 96, w, 26, cl.kc, { s: 14, b: true, fill: c.bg });
        cbox(z, x, 130, w, 26, bin(cl.b), { s: 11, mono: true });
        cbox(z, x, 172, w, 26, bin(cl.x), { s: 11, mono: true, b: true, fill: c.cv, c: '#fff' });
        cbox(z, x, 206, w, 26, '0x' + hex(cl.x), { s: 12, mono: true, b: true, fill: c.orange, c: '#fff' });
      });
      if (f.dec) {
        head(z, 'Decrypt: XOR the result with the same key', 14, 262);
        cols.forEach((cl, i) => { const x = x0 + i * cw; cbox(z, x, 272, cw - 6, 26, `${hex(cl.x)}⊕${hex(cl.b)}=${String.fromCharCode(cl.x ^ cl.b)}`, { s: 11, mono: true, b: true, fill: c.green, c: '#fff' }); });
        D.text(g, 'a ⊕ a = 0   and   a ⊕ 0 = a', 14, 324, { s: 13, b: true, mono: true, c: c.ink });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 1.3  the base rate trap: why most alarms are false even with a good detector (Bayes rule)
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, D, f2, pct } = CYZ;
  trace('cybayes', {
    title: 'Why most security alarms are false: the base rate trap',
    sub: 'A detector catches most attacks and rarely raises a false alarm. Yet when attacks are rare, most of its alarms are still false. Follow 10,000 events through the detector to see why.',
    W: 600, H: 340,
    params: [
      { k: 'base', label: 'Real attacks per 10,000 events', type: 'range', v: 10, min: 1, max: 2000 },
      { k: 'tpr', label: 'Detection rate (share of attacks caught)', type: 'range', v: 0.99, min: 0.5, max: 1, step: 0.01 },
      { k: 'fpr', label: 'False alarm rate (share of normal events flagged)', type: 'range', v: 0.01, min: 0, max: 0.2, step: 0.001 }
    ],
    tips: [
      { t: 'Play it. A detector that catches 99% of attacks, yet only about 1 alarm in 11 is a real attack.', play: true },
      { t: 'Cut the false alarm rate to 0.001. Now about half the alarms are real. Lowering false alarms helps far more than catching a few more attacks.', set: { fpr: 0.001 }, play: true },
      { t: 'Make attacks common, 2000 in 10,000. The same detector now looks excellent, because the base rate changed.', set: { base: 2000 }, play: true }
    ],
    frames(p) {
      const N = 10000, A = p.base, B = N - A, TP = A * p.tpr, FN = A - TP, FP = B * p.fpr, TN = B - FP;
      const post = TP + FP ? TP / (TP + FP) : 0;
      const fr = [];
      fr.push({ k: 1, say: `Start with <b>${N}</b> events, for example logins in a day.` });
      fr.push({ k: 2, say: `Only <b>${A}</b> are real attacks (the <b>base rate</b> is ${pct(A / N)}). The other <b>${B}</b> are normal.` });
      fr.push({ k: 3, say: `The detector catches ${pct(p.tpr)} of attacks: <b>${f2(TP, 1)}</b> true alarms, and ${f2(FN, 1)} attacks are missed.` });
      fr.push({ k: 4, say: `It wrongly flags ${pct(p.fpr)} of normal events: <b>${f2(FP, 1)}</b> false alarms. A small rate times a huge number of normal events gives many false alarms.` });
      fr.push({ k: 5, done: true, post, say: `Total alarms = ${f2(TP, 1)} + ${f2(FP, 1)} = ${f2(TP + FP, 1)}. Chance an alarm is a real attack = ${f2(TP, 1)} ÷ ${f2(TP + FP, 1)} = <b>${pct(post)}</b>. This is Bayes rule. Analysts drown in false alarms when attacks are rare, which is why lowering the false alarm rate matters so much.` });
      return fr.map(x => ({ ...x, N, A, B, TP, FN, FP, TN }));
    },
    paint(z, f) {
      const c = z.col, g = z.g, n = v => f2(v, Math.abs(v - Math.round(v)) < 1e-9 ? 0 : 1);
      if (f.k >= 1) cbox(z, 220, 12, 160, 40, [`${f.N} events`], { s: 14, b: true, fill: c.bg });
      if (f.k >= 2) {
        D.line(g, 300, 52, 150, 92, c.line, 1.5); D.line(g, 300, 52, 450, 92, c.line, 1.5);
        cbox(z, 70, 92, 160, 44, [`${f.A} attacks`, 'base rate'], { s: 13, b: true, fill: 'rgba(220,38,38,0.12)', stroke: c.red });
        cbox(z, 370, 92, 160, 44, [`${f.B} normal`], { s: 13, b: true, fill: c.surf });
      }
      if (f.k >= 3) {
        D.line(g, 150, 136, 85, 176, c.line, 1.5); D.line(g, 150, 136, 215, 176, c.line, 1.5);
        cbox(z, 20, 176, 130, 44, ['alarm', `${n(f.TP)} true`], { s: 12, b: true, fill: c.red, c: '#fff', stroke: c.red });
        cbox(z, 160, 176, 120, 44, ['missed', n(f.FN)], { s: 12, fill: c.surf });
      }
      if (f.k >= 4) {
        D.line(g, 450, 136, 385, 176, c.line, 1.5); D.line(g, 450, 136, 515, 176, c.line, 1.5);
        cbox(z, 320, 176, 130, 44, ['alarm', `${n(f.FP)} false`], { s: 12, b: true, fill: c.orange, c: '#fff', stroke: c.orange });
        cbox(z, 460, 176, 120, 44, ['quiet', n(f.TN)], { s: 12, fill: c.surf });
      }
      if (f.done) {
        head(z, 'Of all alarms, how many are real?', 20, 250);
        const tot = f.TP + f.FP || 1, w = 560;
        CYZ.rr(g, 20, 262, w * f.TP / tot, 28, 4, { fill: c.red });
        CYZ.rr(g, 20 + w * f.TP / tot, 262, w * f.FP / tot, 28, 4, { fill: c.orange });
        D.text(g, `P(attack | alarm) = TP / (TP + FP) = ${pct(f.post)}`, 20, 316, { s: 14, b: true, c: c.ink });
      }
    }
  });
})();

/* =====================================================================================================
   Foundations 2.1  Linux permissions: decode an octal mode, then decide if a user may read, write or run the file
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, D } = CYZ;
  const WHO = { owner: 'the owner of the file', group: 'a member of the file’s group', other: 'any other user', root: 'root (the administrator)' };
  const WANT = { r: ['read', 0], w: ['write', 1], x: ['execute', 2] };
  trace('cychmod', {
    title: 'File permissions: what does 754 mean, and may this user open the file?',
    sub: 'Type an octal mode like 640 or 4755. The animation turns each digit into read, write and execute bits for the owner, the group and everyone else, then checks a request the way the Linux kernel does.',
    W: 600, H: 340,
    params: [
      { k: 'mode', label: 'Mode (3 or 4 octal digits)', type: 'text', v: '754' },
      { k: 'who', label: 'Who asks', type: 'select', v: 'group', opts: Object.keys(WHO).map(k => [k, WHO[k]]) },
      { k: 'want', label: 'To', type: 'select', v: 'w', opts: Object.keys(WANT).map(k => [k, WANT[k][0]]) }
    ],
    tips: [
      { t: 'Play it. A group member may read and run a 754 file, but not write to it.', play: true },
      { t: 'Try 604 as the group asking to read. The group digit is 0, so the answer is no, even though "other" may read. Linux uses only the first class that matches you.', set: { mode: '604', who: 'group', want: 'r' }, play: true },
      { t: 'Try 4755. The extra 4 is the setuid bit: the program runs with its owner’s rights. On a root owned file this is powerful and dangerous.', set: { mode: '4755', who: 'other', want: 'x' }, play: true }
    ],
    frames(p) {
      const m = String(p.mode).trim();
      if (!/^[0-7]{3,4}$/.test(m)) throw new Error('Use 3 or 4 digits, each from 0 to 7, for example 644 or 4755.');
      const d = m.padStart(4, '0').split('').map(Number), sp = d[0], cls = d.slice(1);
      const rwx = v => [(v & 4) ? 'r' : '-', (v & 2) ? 'w' : '-', (v & 1) ? 'x' : '-'];
      const names = ['owner', 'group', 'other'];
      const fr = [{ k: 0, say: `The mode <b>${m}</b> is written in octal (base 8). Each digit is 3 bits: read is worth 4, write 2, execute 1. Add the ones you want: 7 = 4 + 2 + 1 = rwx.` }];
      cls.forEach((v, i) => fr.push({ k: i + 1, say: `${['First', 'Second', 'Third'][i]} digit, for the <b>${names[i]}</b>: ${v} = ${[4, 2, 1].filter(b => v & b).join(' + ') || '0'} = <b>${rwx(v).join('')}</b>.` }));
      let k = 4;
      if (m.length === 4) fr.push({ k: k++, sp: true, say: `The extra leading digit ${sp} holds special bits: setuid 4, setgid 2, sticky 1. ${sp & 4 ? '<b>setuid</b> is on: the program runs with the rights of its owner, not of the person who starts it. ' : ''}${sp & 2 ? '<b>setgid</b> is on: it runs with the file’s group. ' : ''}${sp & 1 ? '<b>sticky</b> is on: in a shared folder, only a file’s owner may delete it. ' : ''}${sp ? '' : 'None are set.'}` });
      const [wname, bit] = WANT[p.want];
      let ok, why, use = -1;
      if (p.who === 'root') {
        if (p.want === 'x') { ok = cls.some(v => v & 1); why = ok ? 'Root may run a file if at least one execute bit is set, and here one is.' : 'Root may run a file only if at least one execute bit is set. None is, so even root is refused.'; }
        else { ok = true; why = `Root skips the read and write checks, so root may ${wname} it whatever the mode says. That is why the root password is the most valuable secret on a Linux machine.`; }
      } else {
        use = names.indexOf(p.who);
        const v = cls[use];
        ok = !!(v & [4, 2, 1][bit]);
        why = `The kernel checks the classes in order: owner, then group, then other, and uses <b>only the first class that matches you</b>. You are ${WHO[p.who]}, so the <b>${names[use]}</b> digit ${v} = ${rwx(v).join('')} decides. Its ${wname} bit is ${ok ? 'on' : 'off'}.`;
      }
      fr.push({ k, use, ask: true, say: `Request: ${WHO[p.who]} wants to <b>${wname}</b> the file. ${why}` });
      fr.push({ k: k + 1, use, ask: true, done: true, ok, say: `Answer: <b>${ok ? 'allowed' : 'permission denied'}</b>. ${ok ? '' : 'A program would get the error EACCES ("Permission denied"). '}In the ls -l listing this file shows as <b>${(m.length === 4 && sp ? spl(cls, sp) : cls.map(v => rwx(v).join('')).join(''))}</b>.` });
      function spl(c, s) { const a = c.map(v => rwx(v)); if (s & 4) a[0][2] = a[0][2] === 'x' ? 's' : 'S'; if (s & 2) a[1][2] = a[1][2] === 'x' ? 's' : 'S'; if (s & 1) a[2][2] = a[2][2] === 'x' ? 't' : 'T'; return a.map(x => x.join('')).join(''); }
      return fr.map(x => ({ ...x, cls, sp, m, rwx }));
    },
    paint(z, f) {
      const c = z.col, g = z.g, names = ['owner', 'group', 'other'];
      head(z, `Mode ${f.m}`, 14, 22);
      f.cls.forEach((v, i) => {
        const x = 30 + i * 186, shown = f.k > i, used = f.use === i;
        cbox(z, x, 34, 170, 30, names[i], { s: 13, b: true, fill: used ? c.cv : c.bg, c: used ? '#fff' : c.ink, stroke: used ? c.cv : c.line });
        cbox(z, x + 65, 70, 40, 34, String(v), { s: 18, b: true, mono: true, fill: c.surf });
        if (!shown) return;
        f.rwx(v).forEach((b, j) => {
          const on = b !== '-';
          cbox(z, x + j * 58, 116, 52, 34, b === '-' ? '−' : b, { s: 16, mono: true, b: true, fill: on ? c.green : c.surf, c: on ? '#fff' : c.ink2 });
          D.text(g, ['4', '2', '1'][j], x + j * 58 + 26, 166, { a: 'center', s: 11, c: c.ink2 });
        });
      });
      if (f.sp !== undefined && f.k >= 4 && f.m.length === 4) {
        ['setuid 4', 'setgid 2', 'sticky 1'].forEach((t, j) => { const on = f.sp & [4, 2, 1][j]; cbox(z, 30 + j * 186, 182, 170, 28, t, { s: 12, b: !!on, fill: on ? c.orange : c.surf, c: on ? '#fff' : c.ink2 }); });
      }
      if (f.ask) {
        const lbl = { owner: 'owner', group: 'group member', other: 'other user', root: 'root' }[z.p.who];
        cbox(z, 30, 226, 540, 34, `${lbl} wants to ${{ r: 'read', w: 'write', x: 'execute' }[z.p.want]}`, { s: 14, b: true, fill: c.bg });
      }
      if (f.done) cbox(z, 150, 274, 300, 40, f.ok ? 'ALLOWED' : 'PERMISSION DENIED', { s: 18, b: true, fill: f.ok ? c.green : c.red, c: '#fff', stroke: f.ok ? c.green : c.red });
    }
  });
})();

/* =====================================================================================================
   Foundations 2.1  user mode and kernel mode: a program asks the kernel to open a file through a system call
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, D } = CYZ;
  const CASES = {
    own: { name: 'Riya’s editor opens Riya’s own notes', user: 'riya', path: '/home/riya/notes.txt', ok: true, check: 'The file belongs to riya and has mode 600 (rw for the owner only). riya is the owner, so read is allowed.' },
    shadow: { name: 'Riya’s program tries to read /etc/shadow', user: 'riya', path: '/etc/shadow', ok: false, check: '/etc/shadow holds the password hashes. On Ubuntu it is owned by root, group shadow, with mode 640. riya is not root and not in the shadow group, so read is denied.' },
    sudo: { name: 'Riya runs sudo to read /etc/shadow', user: 'root (via sudo)', path: '/etc/shadow', ok: true, check: 'sudo asked for riya’s password, checked that riya is allowed in /etc/sudoers, and started the program as root. The kernel sees root, so read is allowed, and the sudo call is written to the log.' },
    mem: { name: 'A game tries to change a banking app’s memory', user: 'riya', path: 'memory of another process', ok: false, check: 'Each process has its own virtual memory. The game’s addresses simply do not point into the banking app. Writing to another process needs debug rights that a normal program does not have.' }
  };
  trace('cyrings', {
    title: 'User mode and kernel mode: who really opens the file?',
    sub: 'Programs run in user mode and cannot touch the disk or other programs directly. They must ask the kernel through a system call, and the kernel checks permission every time.',
    W: 600, H: 330,
    params: [{ k: 'case', label: 'Request', type: 'select', v: 'shadow', opts: Object.keys(CASES).map(k => [k, CASES[k].name]) }],
    tips: [
      { t: 'Play the /etc/shadow case. The program cannot sneak past the kernel, because only the kernel can reach the disk.', play: true },
      { t: 'Now try the sudo case. The same file opens, because the process now runs as root, and the action is logged.', set: { case: 'sudo' }, play: true }
    ],
    frames(p) {
      const t = CASES[p.case];
      return [
        { k: 1, say: `A program runs in <b>user mode</b> (ring 3 on x86 chips) as the user <b>${t.user}</b>. In user mode the CPU refuses to run instructions that touch hardware directly.` },
        { k: 2, say: `To reach <b>${t.path}</b> the program makes a <b>system call</b> (for example open() on Linux, CreateFile on Windows). This is the only door into the kernel.` },
        { k: 3, say: 'The CPU switches to <b>kernel mode</b> (ring 0). Now trusted kernel code runs, with full access to the hardware and to every process’s memory.' },
        { k: 4, say: `The kernel checks permission: ${t.check}` },
        { k: 5, done: true, ok: t.ok, say: t.ok ? 'The kernel opens the file and hands back a small number called a <b>file descriptor</b>. The CPU drops back to user mode and the program reads through that number. It never touches the disk itself.' : 'The kernel refuses and returns an error (<b>EACCES</b>, permission denied). The CPU drops back to user mode. Because every request passes this check, a bug in one program cannot freely read other users’ data. This is <b>complete mediation</b> in action.' }
      ].map(x => ({ ...x, t }));
    },
    paint(z, f) {
      const c = z.col, g = z.g, t = f.t;
      CYZ.rr(g, 10, 10, 580, 140, 10, { fill: c.surf, stroke: c.line });
      CYZ.rr(g, 10, 166, 580, 150, 10, { fill: 'rgba(124,58,237,0.08)', stroke: c.purple || c.line });
      head(z, 'USER MODE (ring 3): programs', 578, 30, { a: 'right' });
      head(z, 'KERNEL MODE (ring 0): the operating system core', 578, 186, { c: c.purple, a: 'right' });
      cbox(z, 40, 50, 200, 56, ['program', `running as ${t.user}`], { s: 13, b: true, fill: f.k >= 1 ? c.bg : c.surf });
      if (f.k >= 2) { D.arrow(g, 140, 108, 140, 200, c.orange, 2.5, 9); D.text(g, 'system call', 112, 132, { s: 12, b: true, c: c.orange, a: 'right' }); }
      if (f.k >= 3) cbox(z, 40, 204, 200, 50, ['kernel code', 'full hardware access'], { s: 12, b: true, fill: c.purple || c.cv, c: '#fff' });
      if (f.k >= 4) { D.arrow(g, 242, 229, 320, 229, c.ink2, 1.6, 7); cbox(z, 324, 200, 250, 58, ['permission check', t.path], { s: 12, b: true, fill: c.surf }); }
      if (f.done) {
        D.arrow(g, 200, 200, 200, 108, f.ok ? c.green : c.red, 2.5, 9);
        cbox(z, 300, 56, 270, 46, f.ok ? 'file descriptor returned' : 'EACCES: permission denied', { s: 14, b: true, fill: f.ok ? c.green : c.red, c: '#fff', stroke: f.ok ? c.green : c.red });
        cbox(z, 324, 268, 250, 36, f.ok ? 'allowed' : 'denied', { s: 14, b: true, fill: f.ok ? c.green : c.red, c: '#fff', stroke: f.ok ? c.green : c.red });
      }
    }
  });
})();
