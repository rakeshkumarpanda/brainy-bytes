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
