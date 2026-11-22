/* ===== Complete Cybersecurity animations, part 4: blockchains, smart contracts, social engineering, mobile,
   IoT and industrial control, and API security.
   Every animation is a step by step trace built on MLZ.trace (assets/mlwidgets.js). It starts empty. Each press
   of Step adds one piece of the picture and explains it in plain words under the picture. assets/voiceteach.js
   reads that line aloud when the voice is on. These pictures are playful on purpose: a happy face and confetti
   when something works, a sad face and a red shake mark when it fails. Every attack shown here is a model on made
   up data inside the page. ===== */
const CYP = (() => {
  const { D, rr } = MLZ;
  /* a small face. mood: 'happy', 'sad', 'think', 'wow' */
  function face(z, x, y, r, mood, col) {
    const g = z.g, c = z.col;
    const fill = col || (mood === 'happy' ? c.green : mood === 'sad' ? c.red : mood === 'wow' ? c.orange : c.yellow);
    D.circle(g, x, y, r, { fill, stroke: c.ink, w: 1.5 });
    D.circle(g, x - r * 0.35, y - r * 0.25, r * 0.11, { fill: '#1f2937' });
    D.circle(g, x + r * 0.35, y - r * 0.25, r * 0.11, { fill: '#1f2937' });
    g.save(); g.strokeStyle = '#1f2937'; g.lineWidth = Math.max(1.5, r * 0.1); g.beginPath();
    if (mood === 'happy') g.arc(x, y + r * 0.05, r * 0.5, 0.15 * Math.PI, 0.85 * Math.PI);
    else if (mood === 'sad') g.arc(x, y + r * 0.6, r * 0.42, 1.15 * Math.PI, 1.85 * Math.PI);
    else if (mood === 'wow') { g.arc(x, y + r * 0.35, r * 0.18, 0, Math.PI * 2); }
    else { g.moveTo(x - r * 0.35, y + r * 0.4); g.lineTo(x + r * 0.35, y + r * 0.3); }
    g.stroke(); g.restore();
  }
  /* confetti around a box, the same pattern every time for the same seed */
  function party(z, x, y, w, h, seed = 1) {
    const R = MLZ.rng(seed), c = z.col, cols = [c.green, c.orange, c.accent, c.pink, c.purple, c.yellow, c.teal];
    for (let i = 0; i < 46; i++) {
      const px = x + R() * w, py = y + R() * h, s = 3 + R() * 5;
      const g = z.g;
      g.save(); g.translate(px, py); g.rotate(R() * Math.PI); g.fillStyle = cols[i % cols.length];
      g.fillRect(-s / 2, -s / 4, s, s / 2); g.restore();
    }
  }
  /* a red zig zag that says "this broke" */
  function zap(z, x, y, len = 26) {
    const g = z.g;
    g.save(); g.strokeStyle = z.col.red; g.lineWidth = 3; g.beginPath(); g.moveTo(x - len / 2, y - len / 2);
    g.lineTo(x + 2, y - 2); g.lineTo(x - 4, y + 3); g.lineTo(x + len / 2, y + len / 2); g.stroke(); g.restore();
  }
  /* a rounded banner across the bottom of the picture */
  function banner(z, y, text, good) {
    const c = z.col;
    rr(z.g, 14, y, z.W - 28, 30, 10, { fill: good === true ? c.green : good === false ? c.red : c.accent, stroke: c.ink, w: 1 });
    D.text(z.g, text, z.W / 2, y + 16, { a: 'center', bl: 'middle', s: MLZ.fit(z.g, text, z.W - 60, 14, { b: true }), b: true, c: '#fff' });
  }
  const tint = (z, k, a = 0.22) => {
    const m = { green: `rgba(22,163,74,${a})`, red: `rgba(225,29,72,${a})`, blue: `rgba(37,99,235,${a})`, orange: `rgba(234,88,12,${a})`, purple: `rgba(124,58,237,${a})`, yellow: `rgba(234,179,8,${a})` };
    return m[k] || z.col.surf;
  };
  const hexs = bytes => bytes.map(b => CYZ.hex(b)).join('').toLowerCase();
  const sha = s => hexs(CYZ.sha256(CYZ.utf8(s)));
  return { face, party, zap, banner, tint, hexs, sha };
})();

/* =====================================================================================================
   Advanced 3.1  A hash chain: every block stores the fingerprint of the block before it
   ===================================================================================================== */
(() => {
  const { trace, D } = MLZ;
  const { cbox } = CYZ;
  const { face, party, zap, banner, tint, sha } = CYP;
  trace('cychain', {
    title: 'Build a chain of blocks, then try to cheat',
    sub: 'Each block holds some payments, the fingerprint (SHA-256 hash) of the block before it, and its own fingerprint. The hashes here are real SHA-256 values worked out in your browser. Type your own payments, one per line.',
    W: 640, H: 360,
    params: [
      { k: 'data', label: 'Payments, one per block (up to 3 lines)', type: 'area', v: 'Asha pays Ravi 5\nRavi pays Meena 2\nMeena pays Arjun 1' },
      { k: 'cheat', label: 'Then cheat', type: 'select', v: '1', opts: [['0', 'Nobody cheats'], ['1', 'Change block 1'], ['2', 'Change block 2']] }
    ],
    tips: [
      { t: 'Play it. Block 1 is changed at the end, its hash changes, and the link to block 2 snaps.', play: true },
      { t: 'Choose "Nobody cheats" and play. Every link holds, and the chain is valid.', set: { cheat: '0' }, play: true },
      { t: 'Type a new payment in the box, such as "Arjun pays Asha 9", and watch every later hash change.' }
    ],
    frames(p) {
      const lines = String(p.data).split(/\n+/).map(s => s.trim()).filter(Boolean).slice(0, 3);
      if (!lines.length) throw new Error('Type at least one payment.');
      const blocks = [{ n: 0, data: 'genesis', prev: '0'.repeat(64) }];
      lines.forEach((d, i) => blocks.push({ n: i + 1, data: d, prev: '' }));
      const fr = [];
      const B = [];
      blocks.forEach((b, i) => {
        if (i) b.prev = B[i - 1].hash;
        b.hash = sha(`${b.n}|${b.prev}|${b.data}`);
        B.push({ ...b });
        fr.push({ B: B.map(x => ({ ...x })), say: i === 0
          ? `Block 0, the genesis block, has no parent, so its "previous" field is all zeros. Its fingerprint is SHA-256 of its number, that field and its data: <code>${b.hash.slice(0, 12)}…</code>.`
          : `Block ${i} copies the fingerprint of block ${i - 1} (<code>${b.prev.slice(0, 8)}…</code>) into its "previous" field, then hashes everything: <code>${b.hash.slice(0, 12)}…</code>. That copy is the link in the chain.` });
      });
      const t = +p.cheat;
      if (t && t < B.length) {
        const C = B.map(x => ({ ...x }));
        const old = C[t].data;
        C[t].data = old.replace(/\d+/, m => m + '0') === old ? old + ' 100' : old.replace(/\d+/, m => m + '0');
        C[t].hash = sha(`${C[t].n}|${C[t].prev}|${C[t].data}`);
        C[t].bad = true;
        fr.push({ B: C, cheat: t, say: `A cheater edits block ${t} to read "${C[t].data}". Its fingerprint changes completely to <code>${C[t].hash.slice(0, 12)}…</code>, even though only one character or two changed.` });
        if (t + 1 < C.length) {
          fr.push({ B: C, cheat: t, snap: t + 1, say: `Block ${t + 1} still remembers the old fingerprint <code>${C[t + 1].prev.slice(0, 8)}…</code>, which no longer matches. The link snaps, so every computer checking the chain sees the cheat at once.` });
          fr.push({ B: C, cheat: t, snap: t + 1, end: 'bad', say: `To hide it, the cheater would have to redo every block after ${t}, and in a real blockchain each redo costs a lot of work (the next lesson), faster than the whole honest network. That is why old blocks are so hard to change.` });
        } else fr.push({ B: C, cheat: t, end: 'bad', say: `This was the newest block, so no later block points to it yet. But the network already holds the honest copy with the old fingerprint, and the next honest block will build on that one.` });
      } else fr.push({ B, end: 'good', say: `Every "previous" field matches the fingerprint of the block before it. The chain is valid. Change any letter anywhere and a link breaks.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, n = f.B.length, gap = 18, bw = Math.min(140, (z.W - 28 - gap * (n - 1)) / n);
      f.B.forEach((b, i) => {
        const x = 14 + i * (bw + gap), y = 40;
        const broken = f.snap === i, fill = b.bad ? tint(z, 'red') : broken ? tint(z, 'orange') : f.end === 'good' ? tint(z, 'green') : tint(z, 'blue', 0.12);
        MLZ.box(z, x, y, bw, 196, '', { fill, stroke: b.bad || broken ? c.red : c.line, w: b.bad || broken ? 2.5 : 1.5, r: 12 });
        D.text(z.g, `Block ${b.n}`, x + bw / 2, y + 22, { a: 'center', s: 14, b: true, c: c.ink });
        D.text(z.g, 'previous', x + 8, y + 48, { s: 11, b: true, c: c.ink2 });
        cbox(z, x + 6, y + 54, bw - 12, 24, b.prev.slice(0, 10) + '…', { s: 11, mono: true, fill: broken ? tint(z, 'red', 0.35) : c.surf });
        D.text(z.g, 'data', x + 8, y + 98, { s: 11, b: true, c: c.ink2 });
        cbox(z, x + 6, y + 104, bw - 12, 34, b.data, { s: 11, fill: c.surf, b: b.bad });
        D.text(z.g, 'hash', x + 8, y + 158, { s: 11, b: true, c: c.ink2 });
        cbox(z, x + 6, y + 164, bw - 12, 24, b.hash.slice(0, 10) + '…', { s: 11, mono: true, b: true, fill: b.bad ? tint(z, 'red', 0.35) : tint(z, 'green', 0.25) });
        if (i < n - 1 && f.B[i + 1]) {
          const ax = x + bw, ay = y + 176;
          if (f.snap === i + 1) zap(z, ax + gap / 2, y + 120, 22);
          else D.arrow(z.g, ax + 1, ay, ax + gap - 1, y + 66, f.end === 'good' ? c.green : c.accent, 2.2);
        }
      });
      if (f.end === 'good') { party(z, 14, 6, z.W - 28, 30, 4); face(z, z.W / 2, 272, 18, 'happy'); banner(z, 304, 'Chain is valid: every link matches', true); }
      if (f.end === 'bad') { face(z, z.W / 2, 272, 18, 'sad'); banner(z, 304, 'Cheat caught: a link no longer matches', false); }
    }
  });
})();

/* =====================================================================================================
   Advanced 3.1  Proof of work: keep changing a number until the hash starts with enough zeros
   ===================================================================================================== */
(() => {
  const { trace, D, f2, rr } = MLZ;
  const { cbox } = CYZ;
  const { face, party, banner, tint, sha } = CYP;
  trace('cypow', {
    title: 'Mining: hunt for a lucky number',
    sub: 'A miner adds a number called the nonce to the block and hashes it. The block is accepted only if the hash starts with enough zeros. Nobody can predict which nonce works, so the miner just keeps trying. The hashes are real SHA-256.',
    W: 640, H: 340,
    params: [
      { k: 'data', label: 'Block data', type: 'text', v: 'Block 7: Asha pays Ravi 5' },
      { k: 'zeros', label: 'Difficulty: zeros needed in hex', type: 'select', v: '2', opts: [['1', '1 zero (about 16 tries)'], ['2', '2 zeros (about 256 tries)'], ['3', '3 zeros (about 4,096 tries)']] }
    ],
    tips: [
      { t: 'Play with 2 zeros. Watch the first few misses, then the search skips ahead until a lucky nonce appears.', play: true },
      { t: 'Choose 3 zeros. Each extra zero makes the work about 16 times bigger. Bitcoin needs about 19 hex zeros today.', set: { zeros: '3' }, play: true },
      { t: 'Change the data by one letter. The winning nonce is now completely different.' }
    ],
    frames(p) {
      const k = +p.zeros, want = '0'.repeat(k), exp = 16 ** k, fr = [];
      let nonce = 0, h = '';
      const seen = [];
      for (; nonce < 300000; nonce++) {
        h = sha(`${p.data}|${nonce}`);
        if (h.startsWith(want)) break;
        if (nonce < 5) {
          seen.push({ nonce, h });
          fr.push({ nonce, h, ok: false, exp, k, tries: nonce + 1, say: `Try nonce ${nonce}: the hash starts <code>${h.slice(0, k + 3)}</code>. It needs to start with ${k === 1 ? 'one zero' : k + ' zeros'}, so this is a miss. Try the next number.` });
        }
      }
      const found = nonce;
      if (found > 8) [0.25, 0.5, 0.75].forEach(q => {
        const n = Math.floor(found * q);
        if (n > 5) fr.push({ nonce: n, h: sha(`${p.data}|${n}`), ok: false, exp, k, tries: n + 1, skip: true, say: `Skipping ahead: ${n.toLocaleString('en-IN')} tries so far and still no luck. A real miner does this trillions of times every second.` });
      });
      fr.push({ nonce: found, h, ok: true, exp, k, tries: found + 1, say: `Nonce ${found.toLocaleString('en-IN')} works: <code>${h.slice(0, 16)}…</code> starts with ${want}. It took ${(found + 1).toLocaleString('en-IN')} tries, and the average is ${exp.toLocaleString('en-IN')}. Anyone can check it with just one hash, which is the clever part: hard to find, easy to check.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      D.text(z.g, 'nonce', 30, 46, { s: 13, b: true, c: c.ink2 });
      cbox(z, 30, 54, 150, 52, f.nonce.toLocaleString('en-IN'), { s: 26, b: true, mono: true, fill: f.ok ? tint(z, 'green') : tint(z, 'yellow', 0.25) });
      D.text(z.g, 'SHA-256 of data | nonce', 200, 46, { s: 13, b: true, c: c.ink2 });
      const hx = 200, hy = 70;
      const s = f.h.slice(0, 32);
      for (let i = 0; i < s.length; i++) {
        const good = i < f.k && s[i] === '0', need = i < f.k;
        rr(z.g, hx + i * 13, hy - 14, 12, 26, 3, { fill: need ? (good ? tint(z, 'green', 0.6) : tint(z, 'red', 0.45)) : c.surf, stroke: c.line, w: 0.6 });
        D.text(z.g, s[i], hx + i * 13 + 6, hy + 4, { a: 'center', s: 12, mono: true, b: need, c: c.ink });
      }
      D.text(z.g, `target: the first ${f.k} must be 0`, hx, hy + 32, { s: 12, b: true, c: c.ink2 });
      const by = 140, bw = z.W - 60;
      D.text(z.g, `tries ${f.tries.toLocaleString('en-IN')}   average needed ${f.exp.toLocaleString('en-IN')}`, 30, by - 6, { s: 12, b: true, c: c.ink });
      rr(z.g, 30, by, bw, 18, 9, { fill: c.surf, stroke: c.line });
      rr(z.g, 30, by, Math.max(10, bw * Math.min(1, f.tries / (f.exp * 3))), 18, 9, { fill: f.ok ? c.green : c.orange });
      D.line(z.g, 30 + bw / 3, by - 3, 30 + bw / 3, by + 21, c.ink, 1.5, [3, 3]);
      D.text(z.g, 'average', 30 + bw / 3, by + 34, { a: 'center', s: 11, c: c.ink2 });
      face(z, z.W / 2, 220, 26, f.ok ? 'happy' : f.skip ? 'think' : 'wow');
      if (f.ok) { party(z, 20, 180, z.W - 40, 80, f.nonce % 97 + 1); banner(z, 290, `Block mined with nonce ${f.nonce.toLocaleString('en-IN')}`, true); }
      else banner(z, 290, f.skip ? 'Still searching ...' : 'Miss. Try the next nonce', null);
    }
  });
})();

/* =====================================================================================================
   Advanced 3.1  A Merkle tree and a short proof that one payment is inside a block
   ===================================================================================================== */
(() => {
  const { trace, D } = MLZ;
  const { cbox } = CYZ;
  const { face, party, banner, tint, sha } = CYP;
  trace('cymerkle', {
    title: 'A Merkle tree: one hash for a whole block of payments',
    sub: 'Hash every payment, then hash the hashes in pairs, again and again, until one hash is left: the Merkle root. It goes in the block header. A phone can then check that one payment is in the block with only a few hashes.',
    W: 640, H: 360,
    params: [
      { k: 'tx', label: 'Payments, one per line (2 to 8)', type: 'area', v: 'Asha pays Ravi 5\nRavi pays Meena 2\nMeena pays Arjun 1\nArjun pays Zoya 3' },
      { k: 'pick', label: 'Prove this payment is inside', type: 'select', v: '2', opts: [['0', 'Payment 1'], ['1', 'Payment 2'], ['2', 'Payment 3'], ['3', 'Payment 4'], ['4', 'Payment 5'], ['5', 'Payment 6'], ['6', 'Payment 7'], ['7', 'Payment 8']] }
    ],
    tips: [
      { t: 'Play it. The tree is built bottom up, then the proof for payment 3 lights up.', play: true },
      { t: 'Add a fifth payment. With an odd count, the last hash is paired with itself, as Bitcoin does.' }
    ],
    frames(p) {
      const tx = String(p.tx).split(/\n+/).map(s => s.trim()).filter(Boolean).slice(0, 8);
      if (tx.length < 2) throw new Error('Type at least two payments.');
      const pick = Math.min(+p.pick, tx.length - 1);
      const L = [tx.map(t => sha(t))];
      while (L[L.length - 1].length > 1) {
        const prev = L[L.length - 1], nxt = [];
        for (let i = 0; i < prev.length; i += 2) nxt.push(sha(prev[i] + (prev[i + 1] ?? prev[i])));
        L.push(nxt);
      }
      const fr = [];
      fr.push({ L, tx, lv: 0, say: `Hash each of the ${tx.length} payments on its own. These are the leaves of the tree.` });
      for (let lv = 1; lv < L.length; lv++) fr.push({ L, tx, lv, say: lv === L.length - 1 ? `One hash is left: the Merkle root <code>${L[lv][0].slice(0, 12)}…</code>. Change any payment and the root changes.` : `Join neighbouring hashes in pairs and hash each pair. ${L[lv - 1].length % 2 ? 'The odd one out is paired with itself. ' : ''}Level ${lv} has ${L[lv].length} hashes.` });
      const path = [];
      let idx = pick;
      for (let lv = 0; lv < L.length - 1; lv++) { const sib = idx ^ 1; path.push({ lv, i: Math.min(sib, L[lv].length - 1), on: idx }); idx >>= 1; }
      fr.push({ L, tx, lv: L.length - 1, pick, path, show: 1, say: `To prove payment ${pick + 1} is in the block, the full node sends only the orange sibling hashes, ${path.length} of them, not all ${tx.length} payments.` });
      fr.push({ L, tx, lv: L.length - 1, pick, path, show: 2, end: true, say: `The phone hashes the payment, joins it with each sibling in turn, and gets the same root as the block header. Proof checked with ${path.length} hashes. For 4,000 payments it would be only 12.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, rows = f.L.length, top = 30, rowH = Math.min(62, 230 / rows);
      const pos = (lv, i) => { const n = f.L[lv].length, w = (z.W - 28) / n; return [14 + w * i + w / 2, top + (rows - 1 - lv) * rowH + 12]; };
      const onPath = new Set(), sibs = new Set();
      if (f.path) { let idx = f.pick; for (let lv = 0; lv < rows; lv++) { onPath.add(lv + ':' + idx); idx >>= 1; } f.path.forEach(q => sibs.add(q.lv + ':' + q.i)); }
      for (let lv = 0; lv <= f.lv; lv++) f.L[lv].forEach((h, i) => {
        const [x, y] = pos(lv, i);
        if (lv > 0) { const a = pos(lv - 1, 2 * i), b = pos(lv - 1, Math.min(2 * i + 1, f.L[lv - 1].length - 1)); D.line(z.g, a[0], a[1] - 10, x, y + 10, c.line, 1.5); D.line(z.g, b[0], b[1] - 10, x, y + 10, c.line, 1.5); }
        const key = lv + ':' + i;
        const fill = f.show && sibs.has(key) ? tint(z, 'orange', 0.55) : f.show === 2 && onPath.has(key) ? tint(z, 'green', 0.55) : lv === rows - 1 ? tint(z, 'purple', 0.3) : tint(z, 'blue', 0.15);
        cbox(z, x - 36, y - 11, 72, 22, h.slice(0, 7), { s: 11, mono: true, b: lv === rows - 1, fill });
      });
      f.tx.forEach((t, i) => { const [x, y] = pos(0, i); D.text(z.g, `P${i + 1}`, x, y + 26, { a: 'center', s: 11, b: true, c: f.pick === i ? c.green : c.ink2 }); });
      if (f.end) { party(z, z.W / 2 - 160, 4, 320, 40, 7); face(z, z.W - 46, 300, 16, 'happy'); banner(z, 318, 'Proof checked: the payment is in the block', true); }
    }
  });
})();

/* =====================================================================================================
   Advanced 3.1  The double spend race: an attacker mines a secret chain against the honest network
   ===================================================================================================== */
(() => {
  const { trace, D, f2 } = MLZ;
  const { cbox } = CYZ;
  const { face, party, banner, tint } = CYP;
  /* Nakamoto (2008), section 11: chance the attacker ever catches up from z blocks behind */
  function nakamoto(q, z) {
    const p = 1 - q;
    if (q >= p) return 1;
    const lam = z * q / p;
    let s = 1, pois = Math.exp(-lam);
    for (let k = 0; k <= z; k++) { if (k) pois *= lam / k; s -= pois * (1 - (q / p) ** (z - k)); }
    return Math.max(0, s);
  }
  trace('cy51', {
    title: 'The double spend race',
    sub: 'An attacker pays a shop, then secretly mines a second chain where that payment never happened. The shop hands over the goods after z confirmations. If the secret chain ever catches up, the attacker can overtake, publish it, and the payment vanishes. Each round, the next block goes to the attacker with probability q, their share of the mining power.',
    W: 640, H: 350,
    params: [
      { k: 'q', label: 'Attacker share of mining power q', type: 'select', v: '0.3', opts: [['0.1', '10%'], ['0.3', '30%'], ['0.45', '45%'], ['0.55', '55% (a 51% attack)']] },
      { k: 'zc', label: 'Confirmations the shop waits for', type: 'select', v: '3', opts: [['1', '1'], ['3', '3'], ['6', '6 (the Bitcoin custom)']] },
      { k: 'seed', label: 'Luck (a different random race)', type: 'select', v: '1', opts: [['1', 'Race 1'], ['2', 'Race 2'], ['3', 'Race 3'], ['4', 'Race 4']] }
    ],
    tips: [
      { t: 'Play with 30% and 3 confirmations. The attacker usually falls behind and gives up.', play: true },
      { t: 'Choose 55%. With more than half the power the attacker catches up in the end, whatever the shop waits for.', set: { q: '0.55' }, play: true },
      { t: 'Keep 30% and choose 6 confirmations. The formula under the picture drops to a tiny chance.', set: { zc: '6', q: '0.3' }, play: true }
    ],
    frames(p) {
      const q = +p.q, zc = +p.zc, R = MLZ.rng(+p.seed * 17 + Math.round(q * 100) + zc), P = nakamoto(q, zc), fr = [];
      let h = 0, a = 0, round = 0, paid = false;
      const pr = `The formula from Satoshi Nakamoto’s paper gives the attacker a ${f2(P * 100, P < 0.01 ? 3 : 1)}% chance overall.`;
      fr.push({ h, a, q, zc, P, say: `The attacker pays the shop in block 1 of the honest chain and starts a secret chain from the block before it. ${pr}` });
      while (round < 60) {
        round++;
        const att = R() < q;
        if (att) a++; else h++;
        const conf = h;
        let say = att ? `Round ${round}: the attacker finds a block. Secret chain ${a}, honest chain ${h}.` : `Round ${round}: honest miners find a block. Honest chain ${h}, secret chain ${a}.`;
        if (!paid && conf >= zc) { paid = true; say += ` The payment now has ${zc} confirmation${zc > 1 ? 's' : ''}, so the shop hands over the goods.`; }
        if (paid && a >= h) { fr.push({ h, a, q, zc, P, paid, end: 'win', say: say + ` The secret chain has caught up. One more lucky block makes it the longest, it is published, and every node switches to it. The payment to the shop disappears: a double spend.` }); return fr; }
        if (h - a >= 6) { fr.push({ h, a, q, zc, P, paid, end: 'lose', say: say + ` The attacker is ${h - a} blocks behind and gives up. All that mining was wasted, and the shop is safe.` }); return fr; }
        fr.push({ h, a, q, zc, P, paid, say });
      }
      fr.push({ h, a, q, zc, P, paid, end: 'lose', say: 'After 60 rounds the race is stopped here. The attacker has not overtaken the honest chain.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, max = Math.max(f.h, f.a, f.zc + 1, 8), bw = Math.min(40, (z.W - 140) / max);
      const lane = (y, n, col, label, mood) => {
        D.text(z.g, label, 14, y + 18, { s: 13, b: true, c: c.ink });
        for (let i = 0; i < n; i++) cbox(z, 120 + i * bw, y, bw - 4, 30, String(i + 1), { s: 11, b: true, fill: col });
        face(z, 120 + n * bw + 18, y + 15, 13, mood);
      };
      lane(50, f.h, tint(z, 'green', 0.5), 'Honest chain', f.end === 'win' ? 'sad' : 'happy');
      lane(120, f.a, tint(z, 'red', 0.45), 'Secret chain', f.end === 'win' ? 'happy' : f.end === 'lose' ? 'sad' : 'think');
      const cx = 120 + f.zc * bw - 2;
      D.line(z.g, cx, 40, cx, 160, c.orange, 2, [5, 4]);
      D.text(z.g, `goods handed over after ${f.zc}`, cx + 4, 36, { s: 11, b: true, c: c.orange });
      cbox(z, 14, 186, z.W - 28, 40, `attacker share q = ${f.q}   confirmations z = ${f.zc}   Nakamoto chance of success = ${f2(f.P * 100, f.P < 0.01 ? 3 : 1)}%`, { s: 13, b: true, fill: c.surf });
      if (f.end === 'win') banner(z, 300, 'Double spend: the secret chain won the race', false);
      if (f.end === 'lose') { party(z, 14, 236, z.W - 28, 56, 5); banner(z, 300, 'The shop is safe: the attacker gave up', true); }
    }
  });
})();

/* =====================================================================================================
   Advanced 3.2  Reentrancy: the bug behind The DAO (June 2016)
   ===================================================================================================== */
(() => {
  const { trace, D, rr } = MLZ;
  const { cbox } = CYZ;
  const { face, party, zap, banner, tint } = CYP;
  trace('cyreentry', {
    title: 'Reentrancy: calling back in before the books are updated',
    sub: 'A tiny bank contract holds 10 ether for other customers. The attacker deposits 1 ether, then asks for it back. When the bank sends ether, the attacker’s contract gets control and can call withdraw again. Choose how the bank is written.',
    W: 640, H: 360,
    params: [{ k: 'mode', label: 'How the bank is written', type: 'select', v: 'vuln', opts: [['vuln', 'Send first, update the balance after (buggy)'], ['cei', 'Update the balance first, then send (checks effects interactions)'], ['guard', 'A reentrancy lock (nonReentrant)']] }],
    tips: [
      { t: 'Play the buggy bank. The attacker re-enters again and again until the bank is empty.', play: true },
      { t: 'Choose "Update the balance first". The second call finds a balance of 0 and fails.', set: { mode: 'cei' }, play: true },
      { t: 'Choose the lock. The second call is refused because withdraw is already running.', set: { mode: 'guard' }, play: true }
    ],
    frames(p) {
      const fr = [], m = p.mode;
      let bank = 10, att = 0, bal = 0, stack = [];
      const S = (say, o = {}) => fr.push({ bank, att, bal, stack: stack.slice(), say, ...o });
      S('The bank contract holds 10 ether that belongs to honest customers. The attacker’s contract has nothing yet.');
      bank += 1; bal = 1; S('The attacker deposits 1 ether. The bank now holds 11, and its ledger says the attacker may withdraw 1.');
      stack.push('withdraw()'); S('The attacker calls <code>withdraw()</code>. The bank checks the ledger: balance 1, more than 0, so the check passes.');
      if (m === 'vuln') {
        let depth = 1;
        while (bank >= 1) {
          bank -= 1; att += 1;
          S(`Call ${depth}: the bank sends 1 ether <b>before</b> touching the ledger. Sending ether runs the attacker’s <code>receive()</code> function. Bank ${bank}, attacker ${att}.`, { hot: true });
          if (bank < 1) break;
          depth++; stack.push('withdraw()');
          S(`Inside <code>receive()</code>, the attacker calls <code>withdraw()</code> again. The ledger still says 1, because the first call has not finished. The check passes again. The call stack is ${depth} deep.`, { hot: true });
        }
        S('The bank is empty, so the attacker stops. Now every call on the stack finishes and each one sets the ledger to 0, far too late.', { unwind: true });
        stack = []; bal = 0;
        S('The attacker turned 1 ether into 11. This is how The DAO lost about 3.6 million ether in June 2016, and why Ethereum split into Ethereum and Ethereum Classic.', { end: 'bad' });
      } else {
        if (m === 'cei') { bal = 0; S('The bank sets the ledger to 0 <b>first</b> (the effect), then sends the ether (the interaction).'); }
        else S('The function is marked <code>nonReentrant</code>, so it sets a lock flag as it starts.', { lock: true });
        bank -= 1; att += 1; if (m === 'guard') bal = 1;
        S(`The bank sends 1 ether and the attacker’s <code>receive()</code> runs. Bank ${bank}, attacker ${att}.`, { hot: true, lock: m === 'guard' });
        stack.push('withdraw()');
        S(m === 'cei' ? 'The attacker calls <code>withdraw()</code> again, but the ledger now says 0, so the check fails and this call is reverted.' : 'The attacker calls <code>withdraw()</code> again, but the lock is still set, so the call is reverted at once.', { refused: true, lock: m === 'guard' });
        stack = ['withdraw()']; bal = 0;
        S('The first call finishes normally. The attacker got back only the 1 ether they put in.');
        stack = []; S('The 10 ether of honest customers is safe. Update state before calling out, and add a lock for extra safety.', { end: 'good' });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      cbox(z, 20, 30, 170, 34, 'Bank contract', { s: 14, b: true, fill: tint(z, 'blue', 0.2) });
      rr(g, 40, 76, 130, 170, 12, { fill: c.surf, stroke: c.line, w: 1.5 });
      for (let i = 0; i < f.bank; i++) D.circle(g, 62 + (i % 4) * 28, 228 - Math.floor(i / 4) * 30, 11, { fill: c.yellow, stroke: c.orange, w: 2 });
      D.text(g, `${f.bank} ether`, 105, 264, { a: 'center', s: 13, b: true, c: c.ink });
      cbox(z, 20, 278, 170, 26, `ledger: attacker = ${f.bal}`, { s: 12, mono: true, fill: f.unwind ? tint(z, 'orange') : c.surf });
      cbox(z, 450, 30, 170, 34, 'Attacker contract', { s: 14, b: true, fill: tint(z, 'red', 0.2) });
      rr(g, 470, 76, 130, 170, 12, { fill: c.surf, stroke: c.line, w: 1.5 });
      for (let i = 0; i < f.att; i++) D.circle(g, 492 + (i % 4) * 28, 228 - Math.floor(i / 4) * 30, 11, { fill: c.yellow, stroke: c.orange, w: 2 });
      D.text(g, `${f.att} ether`, 535, 264, { a: 'center', s: 13, b: true, c: c.ink });
      D.text(g, 'call stack', 320, 40, { a: 'center', s: 12, b: true, c: c.ink2 });
      f.stack.forEach((s, i) => cbox(z, 250, 246 - i * 22, 140, 19, `${s} #${i + 1}`, { s: 11, mono: true, fill: f.refused && i === f.stack.length - 1 ? tint(z, 'red', 0.4) : tint(z, 'purple', 0.25) }));
      if (f.refused) zap(z, 400, 246 - (f.stack.length - 1) * 22 + 10, 18);
      if (f.hot) D.arrow(g, 192, 160, 446, 160, c.orange, 2.5);
      if (f.lock) cbox(z, 250, 50, 140, 22, 'lock: ON', { s: 12, b: true, fill: tint(z, 'green', 0.4) });
      if (f.end === 'bad') { face(z, 105, 130, 20, 'sad'); face(z, 535, 130, 20, 'happy'); banner(z, 318, 'Drained: 1 ether became 11', false); }
      if (f.end === 'good') { party(z, 220, 60, 200, 200, 9); face(z, 105, 130, 20, 'happy'); banner(z, 318, 'Bank safe: the second call was refused', true); }
    }
  });
})();

/* =====================================================================================================
   Advanced 3.2  Integer overflow: an 8 bit counter wraps around like a car's odometer
   ===================================================================================================== */
(() => {
  const { trace, D } = MLZ;
  const { cbox, bin } = CYZ;
  const { face, party, zap, banner, tint } = CYP;
  trace('cyoverflow', {
    title: 'Integer overflow: a number that wraps around',
    sub: 'A uint8 holds whole numbers from 0 to 255 in 8 bits. Go one past 255 and old Solidity (before 0.8) silently wraps to 0, and 0 minus 1 becomes 255. Solidity 0.8 and later stops the transaction instead. The dial shows all 256 values.',
    W: 640, H: 340,
    params: [
      { k: 'op', label: 'Calculation', type: 'select', v: 'sub', opts: [['sub', 'balance 0, withdraw 1 (0 − 1)'], ['add', 'balance 250, add 10 (250 + 10)'], ['ok', 'balance 7, withdraw 3 (7 − 3)']] },
      { k: 'ver', label: 'Compiler', type: 'select', v: '07', opts: [['07', 'Solidity 0.7 (no checks)'], ['08', 'Solidity 0.8 (checked maths)']] }
    ],
    tips: [
      { t: 'Play 0 − 1 with Solidity 0.7. The balance becomes 255, so a broke user suddenly looks rich.', play: true },
      { t: 'Switch to Solidity 0.8. The same calculation stops with an error, and nothing changes.', set: { ver: '08' }, play: true },
      { t: 'Try 250 + 10 with Solidity 0.7. The total wraps to 4.', set: { op: 'add', ver: '07' }, play: true }
    ],
    frames(p) {
      const [a, d] = p.op === 'sub' ? [0, -1] : p.op === 'add' ? [250, 10] : [7, -3];
      const fr = [], checked = p.ver === '08';
      let v = a;
      fr.push({ v, a, d, say: `The balance is stored in a uint8: ${a}, which is <code>${bin(a)}</code> in binary.` });
      for (let i = 0; i < Math.abs(d); i++) {
        const nv = v + Math.sign(d), wrap = nv < 0 || nv > 255;
        if (wrap && checked) { fr.push({ v, a, d, err: true, say: `The next step would leave the range 0 to 255. Solidity 0.8 checks every addition and subtraction, so the transaction reverts with <code>Panic(0x11)</code>. The balance stays ${a}.` }); fr.push({ v: a, a, d, end: 'good', say: 'Nothing was changed. This one compiler change in December 2020 removed a whole family of token bugs.' }); return fr; }
        v = (nv + 256) % 256;
        fr.push({ v, a, d, wrap, say: wrap ? `Step ${i + 1}: ${nv < 0 ? '0 − 1' : '255 + 1'} has no room in 8 bits, so it wraps to <b>${v}</b> (<code>${bin(v)}</code>). No error, no warning.` : `Step ${i + 1}: the dial moves to ${v}.` });
      }
      const wrapped = (a + d < 0 || a + d > 255);
      fr.push({ v, a, d, end: wrapped ? 'bad' : 'good', say: wrapped ? `The result is ${v}, not ${String(a + d).replace('-', '−')}. In April 2018 the BeautyChain token had this bug in its batchTransfer function: one multiplication overflowed and attackers created an astronomically large number of tokens out of nothing.` : `The result is ${v}, inside the range, so no overflow happened.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, cx = 150, cy = 160, R = 110;
      D.circle(g, cx, cy, R, { fill: c.surf, stroke: c.line, w: 2 });
      for (let i = 0; i < 256; i += 16) { const t = -Math.PI / 2 + i / 256 * 2 * Math.PI; D.text(g, String(i), cx + Math.cos(t) * (R - 18), cy + Math.sin(t) * (R - 18) + 4, { a: 'center', s: 10, c: c.ink2 }); }
      D.text(g, '255 | 0', cx, cy - R - 8, { a: 'center', s: 11, b: true, c: c.red });
      const t = -Math.PI / 2 + f.v / 256 * 2 * Math.PI;
      D.arrow(g, cx, cy, cx + Math.cos(t) * (R - 34), cy + Math.sin(t) * (R - 34), f.wrap || f.end === 'bad' ? c.red : c.accent, 3);
      D.circle(g, cx, cy, 6, { fill: c.ink });
      for (let b = 0; b < 8; b++) { const bit = (f.v >> (7 - b)) & 1; cbox(z, 310 + b * 36, 70, 32, 40, String(bit), { s: 18, b: true, mono: true, fill: bit ? tint(z, 'blue', 0.45) : c.surf }); }
      D.text(g, '8 bits of the uint8', 310, 60, { s: 12, b: true, c: c.ink2 });
      cbox(z, 310, 130, 284, 44, `value = ${f.v}`, { s: 20, b: true, fill: f.wrap || f.end === 'bad' ? tint(z, 'red', 0.35) : tint(z, 'green', 0.2) });
      if (f.err) { zap(z, 560, 200, 24); cbox(z, 310, 190, 230, 30, 'revert: Panic(0x11)', { s: 13, b: true, mono: true, fill: tint(z, 'orange', 0.4) }); }
      if (f.end === 'bad') { face(z, 450, 240, 20, 'sad'); banner(z, 300, `Wrapped: the answer should be ${String(f.a + f.d).replace('-', '−')}`, false); }
      if (f.end === 'good') { party(z, 300, 200, 300, 80, 3); face(z, 450, 240, 20, 'happy'); banner(z, 300, 'Safe: no silent wrap around', true); }
    }
  });
})();

/* =====================================================================================================
   Advanced 3.2  A flash loan bends a price oracle (a constant product pool, x times y = k)
   ===================================================================================================== */
(() => {
  const { trace, D, f2, rr } = MLZ;
  const { cbox } = CYZ;
  const { face, party, banner, tint } = CYP;
  const swap = (inR, outR, amt) => outR - inR * outR / (inR + amt * 0.997);
  const money = v => (v < 0 ? '−' : '') + '$' + Math.round(Math.abs(v)).toLocaleString('en-US');
  trace('cyflash', {
    title: 'Flash loan plus a weak price oracle',
    sub: 'A pool holds 200,000 USDC and 100 ETH, so 1 ETH costs 2,000 USDC. A lending app asks this pool for the ETH price and lends up to 75% of a deposit’s value. The attacker owns 10 ETH. A flash loan lends any amount, as long as it is repaid in the same transaction.',
    W: 640, H: 360,
    params: [
      { k: 'Q', label: 'Flash loan size', type: 'select', v: '200000', opts: [['100000', '100,000 USDC'], ['200000', '200,000 USDC'], ['400000', '400,000 USDC']] },
      { k: 'orc', label: 'Where the lending app gets its price', type: 'select', v: 'spot', opts: [['spot', 'The pool price right now (spot)'], ['twap', 'A 30 minute average (TWAP)']] }
    ],
    tips: [
      { t: 'Play with the spot price. The attacker pumps the price inside one transaction and walks away with free money.', play: true },
      { t: 'Switch to the 30 minute average. The pump lasts 12 seconds out of 1,800, so the price barely moves and the attack loses money.', set: { orc: 'twap' }, play: true }
    ],
    frames(p) {
      const Q = +p.Q, fr = [];
      let x = 200000, y = 100;
      const S = (say, o = {}) => fr.push({ x, y, say, ...o });
      S('The pool starts with 200,000 USDC and 100 ETH. Price = 200,000 / 100 = 2,000 USDC per ETH. The product x × y = 20,000,000 must stay the same after every trade (fees aside).');
      S(`First, the attacker flash borrows ${Q.toLocaleString('en-US')} USDC. No deposit is needed, because the whole transaction is cancelled if the loan is not repaid at the end.`, { loan: Q });
      const eth = swap(x, y, Q); x += Q; y -= eth;
      const spot = x / y;
      S(`Next, they buy ETH with all of it and get ${f2(eth, 2)} ETH. The pool now holds fewer ETH, so its price jumps to ${Math.round(spot).toLocaleString('en-US')} USDC.`, { loan: Q, eth, pump: true });
      const price = p.orc === 'spot' ? spot : 2000 * (1 - 12 / 1800) + spot * 12 / 1800, borrow = 0.75 * 10 * price;
      S(p.orc === 'spot' ? `Then they deposit their own 10 ETH in the lending app. It asks the pool for a price, sees ${Math.round(price).toLocaleString('en-US')}, values the deposit at ${money(10 * price)} and lends ${money(borrow)}.` : `Then they deposit 10 ETH. The lending app uses the 30 minute average, which moved only to ${Math.round(price).toLocaleString('en-US')}, so it lends just ${money(borrow)}.`, { loan: Q, eth, borrow, price });
      const back = swap(y, x, eth); y += eth; x -= back;
      S(`Now they sell the ${f2(eth, 2)} ETH back to the pool and get ${money(back)}. The price falls back to about ${Math.round(x / y).toLocaleString('en-US')}.`, { loan: Q, eth: 0, borrow, back });
      const fee = Q * 0.0009, profit = borrow + back - Q - fee - 20000;
      S(`Finally they repay the loan plus a 0.09% fee (${money(fee)}). They leave their 10 ETH (worth ${money(20000)}) behind in the lending app.`, { borrow, back, repaid: true });
      fr.push({ x, y, end: profit > 0 ? 'bad' : 'good', profit, borrow, say: profit > 0 ? `Profit ${money(profit)}, all inside one transaction of about 12 seconds. The lending app is left holding 10 ETH against a loan worth far more. Real cases: bZx (February 2020), Harvest Finance (October 2020, about 34 million dollars) and Mango Markets (October 2022, about 110 million dollars).` : `Result ${money(profit)}: the attack loses money, so it is not worth trying. Average prices, or several independent price feeds, defeat one block pumps.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      cbox(z, 20, 24, 200, 30, 'Trading pool  x × y = k', { s: 13, b: true, fill: tint(z, 'blue', 0.2) });
      const hx = Math.min(200, f.x / 2000), hy = Math.min(200, f.y);
      rr(g, 40, 260 - hx, 60, hx, 6, { fill: c.teal || c.cv }); rr(g, 130, 260 - hy, 60, hy, 6, { fill: c.purple });
      D.text(g, `${Math.round(f.x).toLocaleString('en-US')} USDC`, 70, 276, { a: 'center', s: 11, b: true, c: c.ink });
      D.text(g, `${f2(f.y, 1)} ETH`, 160, 276, { a: 'center', s: 11, b: true, c: c.ink });
      cbox(z, 20, 286, 200, 26, `price ${Math.round(f.x / f.y).toLocaleString('en-US')} per ETH`, { s: 13, b: true, fill: f.pump ? tint(z, 'orange', 0.45) : c.surf });
      cbox(z, 260, 24, 170, 30, 'Lending app', { s: 13, b: true, fill: tint(z, 'green', 0.2) });
      if (f.price) cbox(z, 260, 64, 170, 26, `oracle says ${Math.round(f.price).toLocaleString('en-US')}`, { s: 12, b: true, fill: f.price > 2500 ? tint(z, 'red', 0.35) : tint(z, 'green', 0.3) });
      if (f.borrow) cbox(z, 260, 100, 170, 26, `lent out ${money(f.borrow)}`, { s: 12, b: true, fill: c.surf });
      cbox(z, 460, 24, 160, 30, 'Attacker', { s: 13, b: true, fill: tint(z, 'red', 0.2) });
      const lines = [];
      if (f.loan && !f.repaid) lines.push(`owes ${money(f.loan)}`);
      if (f.eth) lines.push(`holds ${f2(f.eth, 1)} ETH`);
      if (f.borrow) lines.push(`borrowed ${money(f.borrow)}`);
      if (f.back) lines.push(`sold for ${money(f.back)}`);
      lines.forEach((t, i) => cbox(z, 460, 64 + i * 32, 160, 26, t, { s: 12, fill: c.surf }));
      if (f.end) {
        face(z, 345, 200, 22, f.end === 'bad' ? 'sad' : 'happy'); face(z, 540, 200, 22, f.end === 'bad' ? 'happy' : 'sad');
        if (f.end === 'good') party(z, 250, 150, 180, 100, 11);
        banner(z, 320, f.end === 'bad' ? `Attacker profit ${money(f.profit)}: the lending app lost` : `Attack fails: result ${money(f.profit)}`, f.end !== 'bad');
      }
    }
  });
})();

/* =====================================================================================================
   Advanced 3.2  Front running and the sandwich attack: everyone can see the waiting room
   ===================================================================================================== */
(() => {
  const { trace, D, f2 } = MLZ;
  const { cbox } = CYZ;
  const { face, party, banner, tint } = CYP;
  const buy = (x, y, amt) => y - x * y / (x + amt * 0.997);
  const money = v => (v < 0 ? '−' : '') + '$' + Math.round(Math.abs(v)).toLocaleString('en-US');
  trace('cysandwich', {
    title: 'A sandwich attack in the mempool',
    sub: 'Before a transaction is put in a block it waits in a public waiting room, the mempool. Priya wants to buy ETH with 20,000 USDC from a pool of 200,000 USDC and 100 ETH. She sets a slippage limit: the trade is cancelled if she would get too little ETH. A bot watches the mempool.',
    W: 640, H: 350,
    params: [{ k: 'slip', label: 'Priya’s slippage limit', type: 'select', v: '0.05', opts: [['0.005', '0.5%'], ['0.02', '2%'], ['0.05', '5%'], ['0.1', '10%']] }],
    tips: [
      { t: 'Play with a 5% limit. The bot buys just before Priya and sells just after her.', play: true },
      { t: 'Choose 0.5%. There is almost no room to squeeze, so the bot’s profit falls below its fees and it does not attack.', set: { slip: '0.005' }, play: true }
    ],
    frames(p) {
      const slip = +p.slip, X = 200000, Y = 100, V = 20000, fair = buy(X, Y, V), minOut = fair * (1 - slip), gas = 30;
      let lo = 0, hi = 400000;
      for (let i = 0; i < 60; i++) { const a = (lo + hi) / 2, e = buy(X, Y, a); (buy(X + a, Y - e, V) >= minOut ? lo = a : hi = a); }
      const a = lo, ea = buy(X, Y, a), x1 = X + a, y1 = Y - ea, ev = buy(x1, y1, V), x2 = x1 + V, y2 = y1 - ev;
      const sell = y2 * 0 + (x2 - x2 * y2 / (y2 + ea * 0.997)), profit = sell - a - gas;
      const fr = [];
      fr.push({ q: ['Priya: buy ETH with 20,000 USDC'], say: `Priya sends her trade. Alone, it would give her ${f2(fair, 3)} ETH. Her ${f2(slip * 100, 1)}% limit means she accepts no less than ${f2(minOut, 3)} ETH.` });
      if (profit <= 0) {
        fr.push({ q: ['Priya: buy ETH with 20,000 USDC'], say: `The bot works out the best squeeze: it could only push in ${money(a)} first, for a profit of ${money(profit + gas)} before about ${money(gas)} of fees. Not worth it.` });
        fr.push({ q: ['Priya: buy ETH with 20,000 USDC'], end: 'good', got: fair, say: `Priya gets her ${f2(fair, 3)} ETH. A tight slippage limit, or a private transaction route that hides trades from the public mempool, protects users.` });
        return fr;
      }
      fr.push({ q: ['Bot: buy first, higher tip', 'Priya: buy ETH with 20,000 USDC'], front: true, say: `The bot copies the idea and sends its own buy of ${money(a)} with a higher tip, so the block builder puts it first. It gets ${f2(ea, 3)} ETH and the price rises.` });
      fr.push({ q: ['Bot: buy first, higher tip', 'Priya: buy ETH with 20,000 USDC'], victim: true, got: ev, say: `Priya’s trade runs at the worse price and she gets ${f2(ev, 3)} ETH, right at her limit of ${f2(minOut, 3)}, so the trade still goes through. She paid about ${money(V * (1 - ev / fair))} more than she should have.` });
      fr.push({ q: ['Bot: buy first, higher tip', 'Priya: buy ETH with 20,000 USDC', 'Bot: sell right after'], back: true, got: ev, say: `The bot sells its ${f2(ea, 3)} ETH right after Priya, at the price she pushed up, and gets ${money(sell)}.` });
      fr.push({ q: ['Bot: buy first, higher tip', 'Priya: buy ETH with 20,000 USDC', 'Bot: sell right after'], end: 'bad', got: ev, profit, say: `The bot keeps ${money(profit)} after fees, taken from Priya. This is called MEV, maximal extractable value. Bots took hundreds of millions of dollars this way, which is why wallets now offer private routes and tight default limits.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      D.text(z.g, 'Order inside the next block', 20, 34, { s: 13, b: true, c: c.ink2 });
      f.q.forEach((t, i) => cbox(z, 20, 46 + i * 44, 300, 36, `${i + 1}. ${t}`, { s: 13, b: true, fill: t.startsWith('Bot') ? tint(z, 'red', 0.3) : tint(z, 'blue', 0.25) }));
      face(z, 400, 90, 26, f.end === 'bad' ? 'sad' : f.end === 'good' ? 'happy' : f.victim ? 'wow' : 'think');
      D.text(z.g, 'Priya', 400, 134, { a: 'center', s: 12, b: true, c: c.ink });
      face(z, 540, 90, 26, f.end === 'bad' ? 'happy' : f.end === 'good' ? 'sad' : 'think', c.purple);
      D.text(z.g, 'Bot', 540, 134, { a: 'center', s: 12, b: true, c: c.ink });
      if (f.got) cbox(z, 340, 170, 280, 30, `Priya receives ${f2(f.got, 3)} ETH`, { s: 13, b: true, fill: f.end === 'bad' ? tint(z, 'red', 0.3) : tint(z, 'green', 0.3) });
      if (f.end === 'good') { party(z, 340, 210, 280, 70, 13); banner(z, 300, 'No sandwich: Priya gets a fair price', true); }
      if (f.end === 'bad') banner(z, 300, `Sandwiched: the bot earned ${money(f.profit)} from Priya’s trade`, false);
    }
  });
})();

/* =====================================================================================================
   Advanced 4.1  Spot the phish: check a message clue by clue
   ===================================================================================================== */
(() => {
  const { trace, D, rr } = MLZ;
  const { cbox } = CYZ;
  const { face, party, zap, banner, tint } = CYP;
  const MAILS = {
    kyc: { from: 'SBI Alerts', addr: 'alerts@sbi-kyc-update.co', subj: 'URGENT: Your account will be blocked today', hello: 'Dear Customer,', body: ['Your KYC has expired. Update within 2 hours', 'or your account will be suspended.'], link: 'Update KYC now', url: 'http://sbi-kyc-update.co/login', phish: true,
      checks: [['Sender address', false, 'The name says SBI, but the address is sbi-kyc-update.co, a lookalike domain anyone could buy. Real SBI mail comes from sbi.co.in.'],
        ['Pressure and fear', false, '"Blocked today" and "within 2 hours" push you to act before you think. Urgency is the most common trick.'],
        ['The real link', false, 'Hovering shows http://sbi-kyc-update.co/login: not the bank, and not even https.'],
        ['What it asks for', false, 'It wants your login. Banks never ask you to log in from an email link to "update KYC".'],
        ['Greeting', false, '"Dear Customer" means the sender does not know your name.']] },
    ceo: { from: 'Anita Rao (CEO)', addr: 'anita.rao.ceo@gmail.com', subj: 'Quick favour, keep this confidential', hello: 'Hi Rahul,', body: ['I am in a board meeting. Buy 10 Amazon gift cards', 'of Rs 10,000 and send me the codes. I will repay.'], link: '', url: '', phish: true,
      checks: [['Sender address', false, 'A CEO writing from a free Gmail address, not the company domain. Anyone can create that name.'],
        ['Pressure and secrecy', false, '"Board meeting" and "confidential" stop you from checking with anyone. That is a classic pretext.'],
        ['The real link', true, 'There is no link at all. Business email compromise often has no link or attachment, so filters miss it.'],
        ['What it asks for', false, 'Gift card codes are as good as cash and cannot be traced back. No real manager pays like this.'],
        ['Authority', false, 'It borrows the CEO’s authority so you feel you cannot say no. Call her on a known number to check.']] },
    courier: { from: 'IndiaPost Delivery', addr: 'support@indiapost.gov.in.track-parcel.top', subj: 'Parcel on hold: address incomplete', hello: 'Dear user,', body: ['Your parcel could not be delivered.', 'Pay Rs 25 redelivery fee by scanning the QR code.'], link: '[QR code]', url: 'https://track-parcel.top/pay', phish: true,
      checks: [['Sender address', false, 'Read domains from the right: this one ends in track-parcel.top. The indiapost.gov.in part at the front is just a decoy subdomain.'],
        ['Pressure', false, 'A small fee feels harmless, so people pay without thinking. The real goal is your card details.'],
        ['The real link', false, 'The QR code hides the link, so you cannot hover over it. This is called quishing. Your phone shows track-parcel.top.'],
        ['What it asks for', false, 'Card number and OTP for a tiny fee. With those, the attacker can make much bigger payments.'],
        ['Greeting', false, '"Dear user" again. A real courier message would show your tracking number.']] },
    real: { from: 'People Team', addr: 'people@yourcompany.com', subj: 'Holiday calendar for next year', hello: 'Hi Rahul,', body: ['The holiday calendar is now on the intranet.', 'No action is needed. Questions? Ask your manager.'], link: 'Open the intranet page', url: 'https://intranet.yourcompany.com/holidays', phish: false,
      checks: [['Sender address', true, 'The address uses the real company domain, and the mail passed SPF, DKIM and DMARC (next lessons).'],
        ['Pressure', true, 'No deadline, no threat, and it says no action is needed.'],
        ['The real link', true, 'Hovering shows https://intranet.yourcompany.com, the company’s own site, matching the text.'],
        ['What it asks for', true, 'It asks for nothing: no password, money or codes.'],
        ['Greeting', true, 'It uses your name and gives a normal way to ask questions.']] }
  };
  trace('cyphishspot', {
    title: 'Spot the phish: check five clues',
    sub: 'Pick a message. Each step checks one clue that security teams teach everyone to look for. A green tick means the clue looks fine, a red cross means a warning sign.',
    W: 640, H: 370,
    params: [{ k: 'mail', label: 'Message', type: 'select', v: 'kyc', opts: [['kyc', 'Bank KYC update email'], ['ceo', 'Message from the "CEO"'], ['courier', 'Parcel on hold with a QR code'], ['real', 'Holiday calendar from HR']] }],
    tips: [
      { t: 'Play the bank email. Every clue is a red flag.', play: true },
      { t: 'Try the CEO message. It has no link at all, yet it is still a scam.', set: { mail: 'ceo' }, play: true },
      { t: 'Try the HR email. A real message passes every check.', set: { mail: 'real' }, play: true }
    ],
    frames(p) {
      const M = MAILS[p.mail], fr = [];
      fr.push({ M, n: 0, say: `A message arrives: "${M.subj}". Before clicking anything, slow down and check five clues.` });
      M.checks.forEach((c, i) => fr.push({ M, n: i + 1, say: `${c[1] ? 'Looks fine' : 'Warning'}. ${c[0]}: ${c[2]}` }));
      const bad = M.checks.filter(c => !c[1]).length;
      fr.push({ M, n: M.checks.length, end: true, say: M.phish ? `${bad} warning signs: this is a phishing message. Do not click, reply or pay. Report it with your mail’s "Report phishing" button, or forward bank fraud SMS to 7726 (SPAM) in India and report cyber fraud at cybercrime.gov.in or on 1930.` : 'Every clue looks fine, so this message is genuine. Being careful does not mean distrusting everything, it means checking before you act.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, M = f.M, hl = i => f.n === i + 1;
      rr(g, 14, 20, 380, 300, 12, { fill: c.surf, stroke: c.line, w: 1.5 });
      rr(g, 14, 20, 380, 30, 12, { fill: tint(z, 'blue', 0.2) });
      D.text(g, 'Inbox', 28, 40, { s: 12, b: true, c: c.ink2 });
      const row = (y, label, val, i, o = {}) => {
        if (hl(i)) rr(g, 20, y - 15, 368, 22, 6, { fill: tint(z, M.checks[i][1] ? 'green' : 'red', 0.3) });
        D.text(g, label, 28, y, { s: 11, b: true, c: c.ink2 });
        D.text(g, val, 84, y, { s: o.s || 12, b: o.b, mono: o.mono, c: c.ink });
      };
      row(72, 'From', `${M.from} <${M.addr}>`, 0, { s: 11, mono: false });
      row(96, 'Subject', M.subj, 1, { b: true, s: 11 });
      D.text(g, M.hello, 28, 128, { s: 12, c: c.ink });
      M.body.forEach((l, i) => D.text(g, l, 28, 152 + i * 20, { s: 12, c: c.ink }));
      if (hl(4)) rr(g, 20, 113, 368, 22, 6, { fill: tint(z, M.checks[4][1] ? 'green' : 'red', 0.3) });
      if (M.link) {
        cbox(z, 28, 200, 180, 30, M.link, { s: 12, b: true, fill: tint(z, 'blue', 0.35) });
        if (f.n >= 3) cbox(z, 28, 238, 356, 24, 'real link: ' + M.url, { s: 11, mono: true, fill: hl(2) ? tint(z, M.checks[2][1] ? 'green' : 'red', 0.35) : c.bg });
      } else if (f.n >= 3) D.text(g, '(no link or attachment)', 28, 220, { s: 12, c: c.ink2 });
      if (hl(3)) rr(g, 20, 136, 368, 44, 6, { stroke: M.checks[3][1] ? c.green : c.red, w: 2.5 });
      M.checks.forEach((ch, i) => {
        const y = 36 + i * 46, shown = f.n > i;
        cbox(z, 410, y, 216, 36, ch[0], { s: 12, b: true, fill: shown ? tint(z, ch[1] ? 'green' : 'red', 0.35) : c.surf, stroke: hl(i) ? c.ink : undefined });
        if (shown) { if (ch[1]) D.text(g, '✓', 610, y + 24, { a: 'center', s: 18, b: true, c: c.green }); else zap(z, 610, y + 18, 14); }
      });
      if (f.end) {
        face(z, 518, 280, 20, M.phish ? 'wow' : 'happy');
        if (M.phish) { party(z, 404, 250, 226, 60, 21); banner(z, 330, 'Caught it: phishing. Report it, do not click', false); }
        else { party(z, 404, 250, 226, 60, 22); banner(z, 330, 'Genuine: every clue checks out', true); }
      }
    }
  });
})();

/* =====================================================================================================
   Advanced 4.1  Lookalike domains: confusable letters and edit distance
   ===================================================================================================== */
(() => {
  const { trace, D, rr } = MLZ;
  const { cbox } = CYZ;
  const { face, party, banner, tint } = CYP;
  const BRANDS = ['google', 'paypal', 'amazon', 'apple', 'microsoft', 'sbi', 'hdfcbank', 'icicibank', 'flipkart', 'paytm', 'netflix', 'facebook'];
  const CONF = { '0': 'o', '1': 'l', '3': 'e', '5': 's', '@': 'a', 'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'х': 'x', 'і': 'i', 'ӏ': 'l', 'ԁ': 'd', 'ɡ': 'g' };
  const lev = (a, b) => { const d = Array.from({ length: a.length + 1 }, (_, i) => [i]); for (let j = 1; j <= b.length; j++) d[0][j] = j; for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)); return d[a.length][b.length]; };
  trace('cyhomoglyph', {
    title: 'Is this domain pretending to be a brand?',
    sub: 'Type any web address. The checker finds the part that was really registered, swaps letters that look alike (0 for o, 1 for l, rn for m, Cyrillic letters for Latin ones), then measures how many letter edits it is from well known brands.',
    W: 640, H: 350,
    params: [{ k: 'dom', label: 'Web address to check', type: 'text', v: 'login.paypa1-secure.com' }],
    tips: [
      { t: 'Play the example. "paypa1" becomes "paypal" once 1 is read as l.', play: true },
      { t: 'Try hdfcbank.com. It matches the brand exactly, so it is the real one.', set: { dom: 'hdfcbank.com' }, play: true },
      { t: 'Try аpple.com, where the first letter is Cyrillic. Your browser turns it into punycode starting with xn--.', set: { dom: 'аpple.com' }, play: true },
      { t: 'Try arnazon.in. Look closely: r and n together look like m.', set: { dom: 'arnazon.in' }, play: true }
    ],
    frames(p) {
      let raw = String(p.dom).trim().toLowerCase().replace(/^[a-z]+:\/\//, '').split(/[\/?#]/)[0];
      if (!raw || !raw.includes('.')) throw new Error('Type a domain such as example.com');
      let puny = raw;
      try { puny = new URL('http://' + raw).hostname; } catch (e) { /* keep raw */ }
      const labels = raw.split('.'), two = ['co.in', 'co.uk', 'com.au', 'gov.in', 'org.in', 'net.in'];
      const tail = labels.slice(-2).join('.'), reg = two.includes(tail) && labels.length > 2 ? labels.slice(-3).join('.') : tail;
      const name = reg.split('.')[0];
      const fr = [];
      fr.push({ raw, puny, reg, name, st: 1, say: `Read the address from the right. The part that was actually registered is <b>${reg}</b>. Everything to its left${labels.length > reg.split('.').length ? ` ("${labels.slice(0, labels.length - reg.split('.').length).join('.')}")` : ''} is chosen freely by whoever owns it.` });
      if (puny !== raw) fr.push({ raw, puny, reg, name, st: 2, say: `This address uses non Latin letters. Browsers convert it to punycode: <code>${puny}</code>. In 2017 a researcher registered a domain that looked exactly like apple.com this way.` });
      let norm = name.replace(/rn/g, 'm').replace(/vv/g, 'w');
      norm = Array.from(norm).map(ch => CONF[ch] || ch).join('').replace(/-?(secure|login|verify|support|update|account|kyc|online)-?/g, '');
      fr.push({ raw, puny, reg, name, norm, st: 3, say: norm !== name ? `After swapping lookalike letters and removing bait words such as "secure" or "login", "${name}" reads as <b>${norm}</b>.` : `No lookalike letters or bait words were found: the name stays "${name}".` });
      const scores = BRANDS.map(b => ({ b, d: lev(norm, b) })).sort((a, b) => a.d - b.d).slice(0, 3);
      fr.push({ raw, puny, reg, name, norm, scores, st: 4, say: `Edit distance counts the letters to add, remove or change to turn one word into another. Closest brands: ${scores.map(s => `${s.b} (${s.d})`).join(', ')}.` });
      const best = scores[0], exact = name === best.b && best.d === 0;
      const verdict = exact ? 'real' : best.d <= 1 ? 'fake' : best.d <= 2 ? 'sus' : 'none';
      fr.push({ raw, puny, reg, name, norm, scores, st: 5, verdict, say: verdict === 'real' ? `The registered name is exactly "${best.b}". That matches the brand, so this looks genuine (still check the ending, such as .com or .co.in, is the one the brand uses).` : verdict === 'fake' ? `It is ${best.d === 0 ? 'identical' : 'one edit away'} once disguises are removed, but the real registered name is "${name}". This is a <b>lookalike</b> made to trick you into thinking it is ${best.b}.` : verdict === 'sus' ? `Two edits from ${best.b}. Possibly a typo domain (typosquatting). Be careful.` : 'Not close to any brand on our list. That does not make it safe, only that it is not copying these brands.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      D.text(g, 'address', 20, 34, { s: 12, b: true, c: c.ink2 });
      const pre = f.raw.slice(0, f.raw.length - f.reg.length);
      const x0 = 20; let x = x0;
      g.save(); g.font = '600 16px "JetBrains Mono", monospace'; const wpre = g.measureText(pre).width, wreg = g.measureText(f.reg).width; g.restore();
      rr(g, x - 4, 44, wpre + wreg + 8, 30, 6, { fill: c.surf, stroke: c.line });
      D.text(g, pre, x, 65, { s: 16, mono: true, c: c.ink2 }); x += wpre;
      rr(g, x - 2, 46, wreg + 4, 26, 4, { fill: tint(z, 'yellow', 0.5) });
      D.text(g, f.reg, x, 65, { s: 16, mono: true, b: true, c: c.ink });
      D.text(g, 'registered part', x, 90, { s: 11, b: true, c: c.orange });
      if (f.st >= 2 && f.puny !== f.raw) cbox(z, 20, 100, 400, 26, 'punycode: ' + f.puny, { s: 12, mono: true, fill: tint(z, 'orange', 0.35) });
      if (f.norm !== undefined) { D.text(g, `"${f.name}"  reads as  "${f.norm}"`, 20, 150, { s: 15, b: true, mono: true, c: c.ink }); }
      if (f.scores) f.scores.forEach((s, i) => {
        const y = 172 + i * 34, w = Math.max(20, 240 - s.d * 40);
        D.text(g, s.b, 20, y + 18, { s: 13, b: true, c: c.ink });
        rr(g, 120, y + 4, w, 20, 6, { fill: s.d === 0 ? c.red : s.d <= 2 ? c.orange : c.green });
        D.text(g, `${s.d} edit${s.d === 1 ? '' : 's'}`, 128 + w, y + 19, { s: 12, b: true, c: c.ink });
      });
      if (f.verdict) {
        const good = f.verdict === 'real' || f.verdict === 'none';
        face(z, 540, 210, 26, f.verdict === 'real' ? 'happy' : f.verdict === 'fake' ? 'wow' : 'think');
        if (f.verdict === 'real') party(z, 460, 160, 160, 100, 31);
        banner(z, 310, f.verdict === 'real' ? 'Genuine brand name' : f.verdict === 'fake' ? 'Lookalike domain: do not trust it' : f.verdict === 'sus' ? 'Suspicious: close to a brand' : 'Not copying a known brand', good ? true : false);
      }
    }
  });
})();

/* =====================================================================================================
   Advanced 4.1  SPF, DKIM and DMARC: three gates every email passes through
   ===================================================================================================== */
(() => {
  const { trace, D, rr } = MLZ;
  const { cbox } = CYZ;
  const { face, party, zap, banner, tint } = CYP;
  const SC = {
    legit: { from: 'alerts@bank.example', ip: '203.0.113.25', sdom: 'bank.example', spf: true, dkim: 'bank.example', who: 'The bank’s own mail server sends a real alert.' },
    spoof: { from: 'alerts@bank.example', ip: '198.51.100.66', sdom: 'bank.example', spf: false, dkim: '', who: 'An attacker’s server sends mail that only claims to be from bank.example.' },
    look: { from: 'alerts@bank-example.com', ip: '192.0.2.10', sdom: 'bank-example.com', spf: true, dkim: 'bank-example.com', who: 'An attacker registered bank-example.com and set up SPF and DKIM for it properly.' },
    fwd: { from: 'alerts@bank.example', ip: '233.252.0.5', sdom: 'bank.example', spf: false, dkim: 'bank.example', who: 'A real bank mail is forwarded by a mailing list server, which changes the sending IP.' }
  };
  trace('cydmarc', {
    title: 'SPF, DKIM and DMARC: is this email really from the bank?',
    sub: 'bank.example publishes three DNS records: SPF lists the servers allowed to send its mail, DKIM gives a public key to check signatures, and DMARC says what to do when a message fails. The receiving mail server checks all three.',
    W: 640, H: 360,
    params: [
      { k: 'sc', label: 'Who sends the message', type: 'select', v: 'spoof', opts: [['legit', 'The bank itself'], ['spoof', 'An attacker faking the From address'], ['look', 'An attacker using a lookalike domain'], ['fwd', 'A forwarding mailing list']] },
      { k: 'pol', label: 'Bank’s DMARC policy', type: 'select', v: 'reject', opts: [['none', 'p=none (only report)'], ['quarantine', 'p=quarantine (spam folder)'], ['reject', 'p=reject (refuse)']] }
    ],
    tips: [
      { t: 'Play the spoofed mail with p=reject. It fails both checks and is refused.', play: true },
      { t: 'Set the policy to p=none. The same fake reaches the inbox, which is why p=none is only a first step.', set: { pol: 'none' }, play: true },
      { t: 'Try the lookalike domain. Every check passes, because the attacker owns that domain. DMARC cannot stop lookalikes, people and filters must.', set: { sc: 'look', pol: 'reject' }, play: true },
      { t: 'Try the mailing list. SPF fails after forwarding, but the DKIM signature survives, so DMARC still passes.', set: { sc: 'fwd', pol: 'reject' }, play: true }
    ],
    frames(p) {
      const S = SC[p.sc], pol = p.pol, fd = S.from.split('@')[1], fr = [];
      const spfOk = S.spf, spfAl = spfOk && S.sdom === fd, dkOk = !!S.dkim, dkAl = dkOk && S.dkim === fd, dm = spfAl || dkAl;
      fr.push({ S, st: 0, say: `${S.who} The From line says <code>${S.from}</code> and the mail comes from IP ${S.ip}.` });
      fr.push({ S, st: 1, spfOk, say: spfOk ? `SPF: the receiver looks up the SPF record of ${S.sdom}. IP ${S.ip} is on its allowed list, so SPF passes.` : `SPF: the record for ${S.sdom} allows only 203.0.113.0/24. IP ${S.ip} is not on the list, so SPF fails.` });
      fr.push({ S, st: 2, spfOk, dkOk, say: dkOk ? `DKIM: the message carries a signature from d=${S.dkim}. The receiver fetches that domain’s public key from DNS and the signature checks out, so the message was not changed.` : 'DKIM: there is no valid signature from bank.example, because the attacker does not have the bank’s private key.' });
      fr.push({ S, st: 3, spfOk, dkOk, dm, say: `DMARC alignment: does a passing check belong to the same domain as the From line (${fd})? ${dm ? 'Yes' : 'No'}${spfAl ? ', SPF aligns' : ''}${dkAl ? ', DKIM aligns' : ''}. DMARC ${dm ? 'passes' : 'fails'}.` });
      const fate = dm ? 'inbox' : pol === 'reject' ? 'rejected' : pol === 'quarantine' ? 'spam' : 'inbox';
      const bad = p.sc === 'spoof' || p.sc === 'look';
      fr.push({ S, st: 4, spfOk, dkOk, dm, fate, bad, say: dm ? (p.sc === 'look' ? `It lands in the inbox. Every check passed because the attacker really owns ${fd}. Only the reader, or a filter that spots lookalike names, can catch this one.` : 'It lands in the inbox. The mail is genuine.') : fate === 'rejected' ? 'The bank’s policy is p=reject, so the receiving server refuses the fake. Nobody ever sees it.' : fate === 'spam' ? 'The policy is p=quarantine, so the fake goes to the spam folder.' : 'The policy is p=none, so the receiver only sends a report to the bank, and the fake still reaches the inbox.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, S = f.S;
      cbox(z, 10, 30, 176, 70, ['From:', S.from, 'IP ' + S.ip], { s: 11, mono: true, fill: tint(z, 'blue', 0.2) });
      const gate = (x, label, st, ok) => {
        const shown = f.st >= st;
        cbox(z, x, 30, 100, 70, label, { s: 15, b: true, fill: shown ? tint(z, ok ? 'green' : 'red', 0.4) : c.surf });
        if (shown) { if (ok) D.text(g, '✓', x + 50, 120, { a: 'center', s: 20, b: true, c: c.green }); else zap(z, x + 50, 114, 16); }
      };
      D.arrow(g, 188, 65, 204, 65, c.ink2, 2);
      gate(206, 'SPF', 1, f.spfOk); D.arrow(g, 308, 65, 324, 65, c.ink2, 2);
      gate(326, 'DKIM', 2, f.dkOk); D.arrow(g, 428, 65, 444, 65, c.ink2, 2);
      gate(446, 'DMARC', 3, f.dm);
      const bins = [['Inbox', 'inbox', 'green'], ['Spam', 'spam', 'yellow'], ['Rejected', 'rejected', 'red']];
      bins.forEach(([t, k, col], i) => cbox(z, 120 + i * 140, 160, 120, 60, t, { s: 14, b: true, fill: f.fate === k ? tint(z, col, 0.55) : c.surf, stroke: f.fate === k ? c.ink : undefined }));
      if (f.fate) {
        const i = bins.findIndex(b => b[1] === f.fate);
        D.arrow(g, 530, 100, 180 + i * 140, 156, c.ink, 2);
        const happy = (f.bad && f.fate !== 'inbox') || (!f.bad && f.fate === 'inbox');
        face(z, 580, 190, 22, happy ? 'happy' : f.bad ? 'wow' : 'sad');
        if (happy) party(z, 100, 230, 440, 60, 41);
        banner(z, 310, happy ? (f.bad ? 'Fake stopped before it reached anyone' : 'Genuine mail delivered') : (f.bad ? 'The fake reached the inbox' : 'Genuine mail was blocked'), happy);
      }
    }
  });
})();

/* =====================================================================================================
   Advanced 4.2  App sandbox and permissions: what a sneaky torch app can reach
   ===================================================================================================== */
(() => {
  const { trace, D, rr } = MLZ;
  const { cbox } = CYZ;
  const { face, party, zap, banner, tint } = CYP;
  const ASK = [['Camera', 'to turn on the torch light', true], ['Contacts', 'to "share with friends"', false], ['SMS', 'to "verify your number"', false], ['Location', 'to "show local weather"', false], ['Photos', 'to "set a wallpaper"', false]];
  trace('cysandbox', {
    title: 'A torch app asks for permissions',
    sub: 'Every app runs in its own sandbox, a locked room with its own files. To reach anything outside, such as your contacts or messages, it must ask the operating system for a permission. A torch only needs the camera flash. Choose how the phone handles permissions.',
    W: 640, H: 350,
    params: [{ k: 'model', label: 'Permission model', type: 'select', v: 'runtime', opts: [['install', 'All at install (old Android before 6.0)'], ['runtime', 'Ask when needed, you decide (Android 6+, iOS)'], ['careful', 'Ask when needed, and you deny what makes no sense']] }],
    tips: [
      { t: 'Play the old install time model. One tap at install gives the torch everything.', play: true },
      { t: 'Choose "you deny what makes no sense". The torch gets only the camera.', set: { model: 'careful' }, play: true }
    ],
    frames(p) {
      const fr = [], got = [];
      fr.push({ got: [], n: 0, say: 'The torch app is installed. It sits in its own sandbox and cannot read other apps’ files or your data until the operating system lets it.' });
      if (p.model === 'install') {
        ASK.forEach(a => got.push(a[0]));
        fr.push({ got: got.slice(), n: 5, all: true, say: 'Old Android showed one long list of permissions at install time. Almost nobody reads it, so tapping Install granted all five at once.' });
      } else ASK.forEach((a, i) => {
        const allow = p.model === 'runtime' ? true : a[2];
        if (allow) got.push(a[0]);
        fr.push({ got: got.slice(), n: i + 1, cur: i, allow, say: `The app asks for <b>${a[0]}</b> ${a[1]}. ${allow ? (a[2] ? 'That makes sense for a torch, so you allow it.' : 'You tap Allow without thinking, as many people do.') : 'A torch has no reason to need this, so you tap Deny. The app still works.'}` });
      });
      const bad = got.filter(g => g !== 'Camera').length;
      fr.push({ got, n: 5, end: bad ? 'bad' : 'good', say: bad ? `The torch can now read ${got.filter(g => g !== 'Camera').join(', ')}. Fake instant loan apps in India used exactly this to copy borrowers’ contact lists and harass their families, and Google removed thousands of such apps.` : 'The torch has only what it needs, the camera. Your contacts, messages, location and photos stay out of reach. This is least privilege on your own phone.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      rr(g, 20, 40, 180, 230, 18, { fill: tint(z, 'blue', 0.12), stroke: c.accent, w: 2.5, dash: [6, 4] });
      D.text(g, 'sandbox', 110, 60, { a: 'center', s: 12, b: true, c: c.accent });
      cbox(z, 50, 120, 120, 60, 'Torch app', { s: 14, b: true, fill: tint(z, 'yellow', 0.5) });
      face(z, 110, 220, 18, f.end === 'bad' ? 'happy' : f.end === 'good' ? 'sad' : 'think', c.yellow);
      ASK.forEach((a, i) => {
        const y = 40 + i * 48, has = f.got.includes(a[0]), cur = f.cur === i;
        cbox(z, 440, y, 180, 38, a[0], { s: 14, b: true, fill: has ? tint(z, a[2] ? 'green' : 'red', 0.4) : c.surf, stroke: cur ? c.ink : undefined });
        if (has) D.arrow(g, 202, 150, 438, y + 19, a[2] ? c.green : c.red, 2);
        else if (f.n > i && !f.all && f.cur !== undefined) zap(z, 420, y + 19, 14);
      });
      if (f.end === 'good') { party(z, 220, 40, 200, 220, 51); banner(z, 300, 'Only the camera: your data stays private', true); }
      if (f.end === 'bad') banner(z, 300, 'The torch can read far more than a torch needs', false);
    }
  });
})();

/* =====================================================================================================
   Advanced 4.2  App signing: only the real developer can ship an update
   ===================================================================================================== */
(() => {
  const { trace, D } = MLZ;
  const { cbox } = CYZ;
  const { face, party, zap, banner, tint, sha } = CYP;
  trace('cysigning', {
    title: 'App signing: is this update really from the developer?',
    sub: 'A developer signs every version of an app with a private key. The phone remembers which key signed the installed app and accepts an update only if it carries a valid signature from the same key. Hashes are real SHA-256 of the app text.',
    W: 640, H: 340,
    params: [{ k: 'sc', label: 'What arrives', type: 'select', v: 'repack', opts: [['real', 'A genuine update from the developer'], ['repack', 'A repackaged copy with hidden malware'], ['side', 'A fake app from a link, signed with a new key']] }],
    tips: [
      { t: 'Play the repackaged copy. Adding code changes the hash, and the attacker cannot sign with the developer’s key.', play: true },
      { t: 'Choose the genuine update. Same key, valid signature, installed.', set: { sc: 'real' }, play: true },
      { t: 'Choose the fake app from a link. It has a valid signature, but from an unknown key, so the phone warns you.', set: { sc: 'side' }, play: true }
    ],
    frames(p) {
      const code = 'BrainyBank v2.1: login, balance, transfer', bad = code + ', send_sms_to_attacker()';
      const app = p.sc === 'real' ? code : bad, h = sha(app), fr = [];
      fr.push({ st: 1, app, h, say: `The phone receives an app file. It hashes the contents: <code>${h.slice(0, 16)}…</code>.` });
      if (p.sc === 'real') {
        fr.push({ st: 2, app, h, key: 'dev', ok: true, say: 'The file carries a signature made with the developer’s private key over exactly this hash. The phone checks it with the developer’s public key: valid.' });
        fr.push({ st: 3, app, h, key: 'dev', ok: true, same: true, say: 'The key matches the one that signed the installed version, so the update is accepted.' });
        fr.push({ st: 4, app, h, key: 'dev', ok: true, same: true, end: 'good', say: 'Installed. Only someone holding the developer’s private key could have made this update.' });
      } else if (p.sc === 'repack') {
        fr.push({ st: 2, app, h, key: 'dev', ok: false, say: 'The attacker copied the real app and added a hidden function. The old signature was made over a different hash, so it no longer matches these contents.' });
        fr.push({ st: 3, app, h, key: 'att', ok: true, same: false, say: 'So the attacker re signs it with their own key. The signature is now valid, but the key differs from the one that signed the installed app.' });
        fr.push({ st: 4, app, h, key: 'att', ok: true, same: false, end: 'good', say: 'The phone refuses to install it as an update over the real app. The attacker would need the developer’s private key, which is why developers guard signing keys so carefully.' });
      } else {
        fr.push({ st: 2, app, h, key: 'att', ok: true, say: 'A message says "download the new bank app" with a link. The file is signed, by a brand new key nobody knows.' });
        fr.push({ st: 3, app, h, key: 'att', ok: true, side: true, say: 'It is not an update, it is a new app, so the key check cannot help. Android blocks installs from unknown sources unless you allow them, and Play Protect scans and warns.' });
        fr.push({ st: 4, app, h, key: 'att', ok: true, side: true, end: 'warn', say: 'If you override the warnings, the fake app installs. Banking trojans such as Anatsa spread this way. Install apps only from the official store, and never allow unknown sources because a message told you to.' });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      cbox(z, 14, 30, 300, 50, f.app.includes(', send') ? f.app.split(', send').map((t, i) => i ? 'send' + t : t + ',') : f.app, { s: 11, mono: true, fill: f.app.includes('attacker') ? tint(z, 'red', 0.25) : tint(z, 'blue', 0.2) });
      D.text(g, 'app contents', 14, 24, { s: 11, b: true, c: c.ink2 });
      cbox(z, 14, 96, 300, 28, 'SHA-256 ' + f.h.slice(0, 24) + '…', { s: 11, mono: true, fill: c.surf });
      if (f.st >= 2) cbox(z, 14, 140, 300, 36, f.key === 'dev' ? 'signed with: developer key' : 'signed with: attacker key', { s: 13, b: true, fill: f.key === 'dev' ? tint(z, 'green', 0.35) : tint(z, 'orange', 0.4) });
      if (f.st >= 2) { cbox(z, 340, 30, 280, 36, `signature valid for these contents: ${f.ok ? 'yes' : 'no'}`, { s: 12, b: true, fill: f.ok ? tint(z, 'green', 0.35) : tint(z, 'red', 0.35) }); if (!f.ok) zap(z, 606, 48, 14); }
      if (f.st >= 3 && f.same !== undefined) { cbox(z, 340, 80, 280, 36, `same key as installed app: ${f.same ? 'yes' : 'no'}`, { s: 12, b: true, fill: f.same ? tint(z, 'green', 0.35) : tint(z, 'red', 0.35) }); if (!f.same) zap(z, 606, 98, 14); }
      if (f.side) cbox(z, 340, 80, 280, 36, 'unknown source: Play Protect warns', { s: 12, b: true, fill: tint(z, 'yellow', 0.45) });
      if (f.end) {
        const good = f.end === 'good';
        face(z, 480, 200, 26, good ? 'happy' : 'wow');
        if (good) party(z, 340, 150, 280, 110, 61);
        banner(z, 296, f.end === 'warn' ? 'Only your caution stops this one: use the official store' : f.app.includes('attacker') ? 'Fake update refused' : 'Genuine update installed', good ? true : false);
      }
    }
  });
})();

/* =====================================================================================================
   Advanced 4.2  Certificate pinning on café Wi-Fi
   ===================================================================================================== */
(() => {
  const { trace, D } = MLZ;
  const { cbox } = CYZ;
  const { face, party, zap, banner, tint } = CYP;
  trace('cypinning', {
    title: 'Café Wi-Fi, a sneaky certificate, and pinning',
    sub: 'The café Wi-Fi is run by an attacker who sits in the middle. Earlier they tricked the user into installing a "Wi-Fi profile" that adds the attacker’s certificate authority (CA) to the phone. Now they show the banking app a fake certificate for bank.example signed by that CA.',
    W: 640, H: 340,
    params: [
      { k: 'pin', label: 'The banking app', type: 'select', v: 'none', opts: [['none', 'Trusts any CA on the phone'], ['sys', 'Trusts only system CAs (Android 7+ default)'], ['pin', 'Pins the bank’s own public key']] },
      { k: 'net', label: 'Network', type: 'select', v: 'cafe', opts: [['cafe', 'Attacker’s café Wi-Fi'], ['home', 'Home Wi-Fi, no attacker']] }
    ],
    tips: [
      { t: 'Play with an app that trusts any CA. The fake certificate is accepted and the attacker reads the password.', play: true },
      { t: 'Pin the bank’s key. The fake certificate has a different key, so the app refuses to connect.', set: { pin: 'pin' }, play: true },
      { t: 'Switch to home Wi-Fi with pinning on. The real certificate matches the pin and everything works.', set: { pin: 'pin', net: 'home' }, play: true }
    ],
    frames(p) {
      const evil = p.net === 'cafe', fr = [];
      fr.push({ evil, st: 1, say: evil ? 'The app connects to bank.example. The café router intercepts the connection and answers itself.' : 'The app connects to bank.example over your home Wi-Fi.' });
      fr.push({ evil, st: 2, say: evil ? 'The router sends a certificate for bank.example signed by the attacker’s CA, with the attacker’s public key inside.' : 'The bank sends its real certificate, signed by a public CA, with the bank’s own public key.' });
      let ok;
      if (!evil) { ok = true; fr.push({ evil, st: 3, ok, say: p.pin === 'pin' ? 'The app hashes the public key in the certificate and compares it with the pin built into the app. They match.' : 'The certificate chains to a trusted system CA, so it is accepted.' }); }
      else if (p.pin === 'none') { ok = true; fr.push({ evil, st: 3, ok, say: 'The app accepts any CA the phone trusts, including the one the user installed. The fake certificate passes.' }); }
      else if (p.pin === 'sys') { ok = false; fr.push({ evil, st: 3, ok, say: 'Since Android 7, apps ignore CAs that users install unless they opt in. The attacker’s CA is user installed, so the certificate is rejected.' }); }
      else { ok = false; fr.push({ evil, st: 3, ok, say: 'The app hashes the public key in the certificate. It does not match the pin of the bank’s real key, whoever signed it. Connection refused.' }); }
      const leak = evil && ok;
      fr.push({ evil, st: 4, ok, end: leak ? 'bad' : 'good', say: leak ? 'The app sends the login over a connection the attacker can decrypt. The password is stolen. Never install profiles or certificates that a Wi-Fi page asks for.' : evil ? 'The app shows a connection error instead of leaking anything. The attacker sees only encrypted bytes or nothing.' : 'A normal, private connection. Pinning costs nothing on a safe network.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      cbox(z, 14, 100, 130, 60, 'Banking app', { s: 14, b: true, fill: tint(z, 'blue', 0.25) });
      cbox(z, 496, 100, 130, 60, 'bank.example', { s: 14, b: true, fill: tint(z, 'green', 0.25) });
      if (f.evil) { cbox(z, 255, 100, 130, 60, 'Café router', { s: 14, b: true, fill: tint(z, 'red', 0.3) }); face(z, 320, 70, 16, f.end === 'bad' ? 'happy' : f.end === 'good' ? 'sad' : 'think', c.purple); }
      if (f.st >= 1) { if (f.evil) { D.arrow(g, 146, 130, 252, 130, c.ink2, 2); D.line(g, 388, 130, 494, 130, c.line, 2, [4, 4]); } else D.arrow(g, 146, 130, 494, 130, c.ink2, 2); }
      if (f.st >= 2) cbox(z, 150, 180, 340, 40, f.evil ? 'certificate: bank.example, signed by "Free WiFi CA"' : 'certificate: bank.example, signed by a public CA', { s: 12, b: true, mono: false, fill: f.evil ? tint(z, 'orange', 0.4) : tint(z, 'green', 0.3) });
      if (f.st >= 3) { cbox(z, 150, 230, 340, 30, f.ok ? 'app check: accepted' : 'app check: REJECTED', { s: 13, b: true, fill: f.ok ? (f.evil ? tint(z, 'red', 0.35) : tint(z, 'green', 0.35)) : tint(z, 'green', 0.35) }); if (!f.ok) zap(z, 470, 245, 14); }
      if (f.end === 'bad') { face(z, 79, 200, 18, 'sad'); banner(z, 296, 'Password stolen through a fake certificate', false); }
      if (f.end === 'good') { party(z, 14, 166, 130, 100, 71); face(z, 79, 200, 18, 'happy'); banner(z, 296, f.evil ? 'Attack stopped: the app refused the fake' : 'Safe connection', true); }
    }
  });
})();

/* =====================================================================================================
   Advanced 4.3  A Mirai style worm spreads through devices with default passwords
   ===================================================================================================== */
(() => {
  const { trace, D, rr, f2 } = MLZ;
  const { cbox } = CYZ;
  const { face, party, banner, tint } = CYP;
  const N = 120;
  trace('cymirai', {
    title: 'Default passwords and a worm',
    sub: 'A neighbourhood of 120 cameras and routers. Some still use the factory password, such as admin and admin. One infected device scans for others each round and tries a short list of default passwords. Every infected device joins the botnet and scans too.',
    W: 640, H: 350,
    params: [
      { k: 'p', label: 'Devices still on a default password', type: 'select', v: '0.6', opts: [['0.6', '60%'], ['0.2', '20%'], ['0.02', '2% (unique passwords by law)']] },
      { k: 'tries', label: 'Devices each bot probes per round', type: 'select', v: '3', opts: [['1', '1'], ['3', '3'], ['6', '6']] }
    ],
    tips: [
      { t: 'Play with 60% default passwords. The botnet grows fast, then slows when few weak devices are left.', play: true },
      { t: 'Choose 2%, as when every device ships with a unique password. The worm barely spreads.', set: { p: '0.02' }, play: true }
    ],
    frames(p) {
      const R = MLZ.rng(7), weak = Array.from({ length: N }, () => R() < +p.p), inf = new Array(N).fill(false), fr = [];
      inf[0] = true; weak[0] = true;
      const count = () => inf.filter(Boolean).length;
      fr.push({ weak: weak.slice(), inf: inf.slice(), r: 0, say: `Round 0: one device is infected. ${weak.filter(Boolean).length} of ${N} devices still use a factory password (shown with a red dot).` });
      for (let r = 1; r <= 10; r++) {
        const now = inf.slice();
        now.forEach((on, i) => { if (!on) return; for (let t = 0; t < +p.tries; t++) { const j = Math.floor(R() * N); if (weak[j]) inf[j] = true; } });
        const c = count(), added = c - now.filter(Boolean).length;
        fr.push({ weak: weak.slice(), inf: inf.slice(), r, say: `Round ${r}: ${added} new device${added === 1 ? '' : 's'} logged into with a default password. The botnet has ${c} devices.` });
        if (added === 0 && r > 3) break;
      }
      const c = count(), gbps = c * 0.005 * 1000;
      fr.push({ weak, inf: inf.slice(), r: -1, end: c > 10 ? 'bad' : 'good', c, say: c > 10 ? `${c} bots, each sending about 5 Mbit/s, can flood a target with about ${f2(gbps / 1000, 2)} Gbit/s. The real Mirai botnet of 2016 reached around 600,000 devices and knocked major websites offline through an attack on the DNS company Dyn.` : `Only ${c} device${c === 1 ? '' : 's'} infected. With unique passwords the worm has almost nothing to log into. That is why the UK has banned default passwords since April 2024.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, cols = 15;
      f.inf.forEach((on, i) => {
        const x = 30 + (i % cols) * 26, y = 36 + Math.floor(i / cols) * 30;
        rr(g, x, y, 20, 20, 5, { fill: on ? c.red : c.surf, stroke: on ? c.red : c.line, w: 1.2 });
        if (f.weak[i] && !on) D.circle(g, x + 16, y + 4, 3, { fill: c.red });
        if (on) { D.circle(g, x + 7, y + 8, 1.6, { fill: '#fff' }); D.circle(g, x + 13, y + 8, 1.6, { fill: '#fff' }); D.line(g, x + 6, y + 14, x + 14, y + 14, '#fff', 1.4); }
      });
      const cnt = f.inf.filter(Boolean).length;
      cbox(z, 440, 40, 180, 50, `bots: ${cnt}`, { s: 20, b: true, fill: cnt > 10 ? tint(z, 'red', 0.35) : tint(z, 'green', 0.3) });
      rr(g, 440, 104, 180, 16, 8, { fill: c.surf, stroke: c.line });
      rr(g, 440, 104, Math.max(6, 180 * cnt / N), 16, 8, { fill: c.red });
      D.text(g, `${f.r >= 0 ? 'round ' + f.r : 'final'}`, 530, 140, { a: 'center', s: 13, b: true, c: c.ink2 });
      if (f.end) {
        face(z, 530, 200, 26, f.end === 'bad' ? 'sad' : 'happy');
        if (f.end === 'good') party(z, 440, 150, 180, 110, 81);
        banner(z, 300, f.end === 'bad' ? `Botnet of ${f.c} devices ready to flood a target` : 'Unique passwords stopped the worm', f.end === 'good');
      }
    }
  });
})();

/* =====================================================================================================
   Advanced 4.3  A Modbus command has no password: a toy water tank
   ===================================================================================================== */
(() => {
  const { trace, D, rr } = MLZ;
  const { cbox, hex } = CYZ;
  const { face, party, zap, banner, tint } = CYP;
  trace('cymodbus', {
    title: 'Modbus: the factory language with no password',
    sub: 'A PLC controls the inlet valve of a water tank. Commands arrive as Modbus TCP frames. Modbus was designed in 1979 for closed factory networks, so a frame has no username, password or signature. Here a stranger on the network sends "open the valve".',
    W: 640, H: 360,
    params: [{ k: 'def', label: 'Protection', type: 'select', v: 'none', opts: [['none', 'None: flat network, plain Modbus'], ['fw', 'Industrial firewall allows only the HMI to write'], ['sis', 'None, but a separate safety system watches the level']] }],
    tips: [
      { t: 'Play with no protection. The PLC obeys anyone and the tank overflows.', play: true },
      { t: 'Choose the industrial firewall. Writes from anything but the operator’s HMI are dropped.', set: { def: 'fw' }, play: true },
      { t: 'Choose the safety system. The bad command gets through, but an independent safety controller closes a second valve before the tank overflows.', set: { def: 'sis' }, play: true }
    ],
    frames(p) {
      const fr = [];
      const bytes = [0x00, 0x2A, 0x00, 0x00, 0x00, 0x06, 0x01, 0x05, 0x00, 0x10, 0xFF, 0x00];
      fr.push({ lvl: 40, st: 1, bytes, say: 'The tank is at 40% and the valve is closed. A device that is not the operator’s screen sends a Modbus TCP frame to the PLC on port 502.' });
      fr.push({ lvl: 40, st: 2, bytes, hl: [7], say: 'Byte 8 is the function code. 05 means "write single coil": switch one output on or off.' });
      fr.push({ lvl: 40, st: 3, bytes, hl: [8, 9, 10, 11], say: 'The next bytes say which coil (address 0x0010, the inlet valve) and the value FF00, which means ON. Notice what is missing: nothing in the frame says who sent it.' });
      if (p.def === 'fw') {
        fr.push({ lvl: 40, st: 4, bytes, drop: true, say: 'An industrial firewall in front of the PLC understands Modbus. Its rule allows function code 05 only from the operator’s HMI address. This sender is not the HMI, so the frame is dropped.' });
        fr.push({ lvl: 40, st: 5, bytes, end: 'good', say: 'The valve stays closed and the attempt is logged for the security team. Segmenting the network and allowing only known writers is the main defence for old protocols that cannot be fixed.' });
        return fr;
      }
      fr.push({ lvl: 40, st: 4, bytes, valve: true, say: 'The PLC checks only that the frame is well formed, then obeys. The inlet valve opens.' });
      [60, 80, 92].forEach(l => fr.push({ lvl: l, st: 5, bytes, valve: true, say: `Water keeps flowing in. Level ${l}%.${l === 92 && p.def !== 'sis' ? ' The operator’s screen could even be fooled into showing a normal level, as Stuxnet did.' : ''}` }));
      if (p.def === 'sis') {
        fr.push({ lvl: 95, st: 6, bytes, valve: true, sis: true, say: 'At 95% an independent safety instrumented system, with its own level sensor and its own valve, trips. It does not trust the PLC at all.' });
        fr.push({ lvl: 95, st: 7, bytes, sis: true, end: 'good', say: 'The safety valve shuts and the tank never overflows. Safety systems are the last line of defence, which is why the Triton malware of 2017 targeting one was so alarming.' });
      } else fr.push({ lvl: 100, st: 6, bytes, valve: true, end: 'bad', say: 'The tank overflows. In a real plant this could damage equipment or hurt people. Industrial security is about safety, not only data.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      D.text(g, 'Modbus TCP frame', 20, 30, { s: 12, b: true, c: c.ink2 });
      f.bytes.forEach((b, i) => cbox(z, 20 + i * 32, 38, 30, 28, hex(b), { s: 12, mono: true, b: true, fill: f.hl && f.hl.includes(i) ? tint(z, 'yellow', 0.6) : i < 7 ? c.surf : tint(z, 'blue', 0.2) }));
      D.text(g, 'header (7 bytes)', 20, 82, { s: 10, c: c.ink2 }); D.text(g, 'function, address, value', 244, 82, { s: 10, c: c.ink2 });
      cbox(z, 20, 110, 120, 50, 'Stranger’s laptop', { s: 12, b: true, fill: tint(z, 'red', 0.25) });
      cbox(z, 200, 110, 100, 50, 'PLC', { s: 15, b: true, fill: tint(z, 'purple', 0.25) });
      if (f.drop) { cbox(z, 150, 170, 120, 30, 'firewall: DROP', { s: 12, b: true, fill: tint(z, 'green', 0.45) }); zap(z, 170, 135, 18); } else D.arrow(g, 142, 135, 198, 135, c.red, 2.2);
      const tx = 430, ty = 60, th = 220, tw = 120;
      rr(g, tx, ty, tw, th, 10, { fill: c.surf, stroke: c.ink2, w: 2 });
      const h = th * f.lvl / 100;
      rr(g, tx + 2, ty + th - h, tw - 4, h, 8, { fill: f.lvl >= 100 ? c.red : c.accent });
      D.text(g, `${f.lvl}%`, tx + tw / 2, ty + th / 2, { a: 'center', s: 18, b: true, c: f.lvl >= 50 ? '#fff' : c.ink });
      cbox(z, 320, 96, 90, 28, f.valve ? 'valve OPEN' : 'valve shut', { s: 11, b: true, fill: f.valve ? tint(z, 'orange', 0.5) : tint(z, 'green', 0.3) });
      D.line(g, 410, 110, tx, 110, c.accent, 4);
      if (f.sis) cbox(z, 560, 130, 74, 50, ['safety', 'trip'], { s: 12, b: true, fill: tint(z, 'green', 0.5) });
      if (f.end) {
        face(z, 250, 230, 22, f.end === 'bad' ? 'sad' : 'happy');
        if (f.end === 'good') party(z, 20, 200, 380, 80, 91);
        banner(z, 318, f.end === 'bad' ? 'Overflow: the PLC obeyed a stranger' : 'Tank safe', f.end === 'good');
      }
    }
  });
})();

/* =====================================================================================================
   Advanced 4.3  The Purdue model: can an email attack reach the factory floor?
   ===================================================================================================== */
(() => {
  const { trace, D, rr } = MLZ;
  const { cbox } = CYZ;
  const { face, party, zap, banner, tint } = CYP;
  const LV = [['Level 5', 'Internet and cloud'], ['Level 4', 'Office IT: email, ERP'], ['Level 3.5', 'Industrial DMZ'], ['Level 3', 'Site operations, historian'], ['Level 2', 'Control: HMI, SCADA'], ['Level 1', 'PLCs and controllers'], ['Level 0', 'Pumps, valves, sensors']];
  trace('cypurdue', {
    title: 'From a phishing email to the factory floor',
    sub: 'The Purdue model stacks a plant’s networks in levels, from the internet at the top to physical machines at the bottom. An attacker phishes an office worker (level 4) and tries to move down. Choose how the levels are separated.',
    W: 640, H: 370,
    params: [{ k: 'seg', label: 'Separation', type: 'select', v: 'flat', opts: [['flat', 'Flat: office and plant on one network'], ['dmz', 'Firewalls and a DMZ: no direct office to plant traffic'], ['diode', 'DMZ plus a one way data diode out of the plant']] }],
    tips: [
      { t: 'Play the flat network. The attacker walks from the inbox to the PLCs. This is close to what happened in Ukraine in December 2015.', play: true },
      { t: 'Add the DMZ. The attacker is stuck in the office network and must break a second, separate set of defences.', set: { seg: 'dmz' }, play: true },
      { t: 'Add the data diode. Data can flow out of the plant for reports, but nothing can flow in.', set: { seg: 'diode' }, play: true }
    ],
    frames(p) {
      const fr = [], stop = p.seg === 'flat' ? 7 : p.seg === 'dmz' ? 2 : 2;
      fr.push({ at: 1, path: [1], say: 'An engineer at level 4 opens a phishing attachment. The attacker now controls one office PC. The real attack on Ukrainian power companies in 2015 started exactly this way, with BlackEnergy malware in email attachments.' });
      if (p.seg === 'flat') {
        fr.push({ at: 3, path: [1, 3], say: 'On a flat network the office PC can reach the historian and site servers directly. The attacker steals passwords stored there.' });
        fr.push({ at: 4, path: [1, 3, 4], say: 'With those passwords they log into the operator screens (HMI) using the plant’s own remote access tool.' });
        fr.push({ at: 5, path: [1, 3, 4, 5], say: 'From the HMI they can send commands to the PLCs and breakers, which trust any command from the control network.' });
        fr.push({ at: 6, path: [1, 3, 4, 5, 6], end: 'bad', say: 'Breakers open and real equipment stops. In Ukraine about 225,000 customers lost power for several hours on 23 December 2015.' });
      } else {
        fr.push({ at: 1, path: [1], block: 2, say: 'The firewall between levels 4 and 3.5 allows no direct connection from office PCs into the plant. Only specific servers in the DMZ talk to each side.' });
        if (p.seg === 'diode') fr.push({ at: 1, path: [1], block: 2, diode: true, say: 'The plant’s historian pushes data out through a data diode, hardware that physically carries signals in one direction only. Even a perfect hacker cannot send a packet back in through it.' });
        fr.push({ at: 1, path: [1], block: 2, diode: p.seg === 'diode', end: 'good', say: 'The attacker controls an office PC but cannot reach the plant. In 2019 India’s Kudankulam nuclear plant confirmed malware on its administrative network, and said the plant control network was isolated and not affected. That separation is the point of the model.' });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      LV.forEach((l, i) => {
        const y = 14 + i * 42, on = f.path.includes(i), cur = f.at === i;
        const fill = on ? tint(z, 'red', cur ? 0.5 : 0.3) : i <= 1 ? tint(z, 'blue', 0.15) : i === 2 ? tint(z, 'yellow', 0.3) : tint(z, 'green', 0.15);
        cbox(z, 20, y, 330, 36, `${l[0]}  ${l[1]}`, { s: 13, b: true, fill, stroke: cur ? c.ink : undefined });
        if (f.block === i) { rr(g, 14, y - 3, 342, 4, 2, { fill: c.ink }); zap(z, 370, y + 2, 18); D.text(g, 'firewall', 384, y + 6, { s: 12, b: true, c: c.ink }); }
      });
      if (f.diode) { cbox(z, 380, 140, 120, 30, 'data diode: out only', { s: 11, b: true, fill: tint(z, 'green', 0.4) }); D.arrow(g, 440, 172, 440, 142, c.green, 2); }
      for (let k = 1; k < f.path.length; k++) D.arrow(g, 360, 14 + f.path[k - 1] * 42 + 18, 360, 14 + f.path[k] * 42 + 18, c.red, 2.5);
      if (f.end) {
        face(z, 560, 200, 26, f.end === 'bad' ? 'sad' : 'happy');
        if (f.end === 'good') party(z, 470, 120, 160, 160, 101);
        banner(z, 318, f.end === 'bad' ? 'Phishing email to power cut: no walls in between' : 'Office breach stayed out of the plant', f.end === 'good');
      }
    }
  });
})();
