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
