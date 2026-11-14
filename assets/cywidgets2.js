/* ===== Complete Cybersecurity animations, part 2: Cryptography. Built on MLZ.trace and CYZ (assets/cywidgets.js). ===== */

/* AES-128 pieces shared by the cryptography animations: the S-box built from GF(2^8) inverses and the affine map,
   ShiftRows, MixColumns, AddRoundKey and the key schedule. The state is 16 bytes in column order, as in FIPS 197.
   Checked against FIPS 197 Appendix C.1 (ciphertext 69c4e0d86a7b0430d8cdb78070b4c55a) and its worked examples
   {57}.{83} = {c1} and S-box(53) = ed. */
const CYAES = (() => {
  const xt = a => ((a << 1) ^ (a & 0x80 ? 0x1b : 0)) & 255;
  const mul = (a, b) => { let r = 0; while (b) { if (b & 1) r ^= a; a = xt(a); b >>= 1; } return r; };
  const inv = a => { if (!a) return 0; let r = 1; for (let i = 0; i < 254; i++) r = mul(r, a); return r; };
  const SB = [];
  for (let x = 0; x < 256; x++) {
    const b = inv(x); let s = 0x63;
    for (let i = 0; i < 8; i++) { const bit = ((b >> i) ^ (b >> ((i + 4) % 8)) ^ (b >> ((i + 5) % 8)) ^ (b >> ((i + 6) % 8)) ^ (b >> ((i + 7) % 8))) & 1; s ^= bit << i; }
    SB.push(s);
  }
  const sub = st => st.map(v => SB[v]);
  const shift = st => st.map((_, i) => { const r = i % 4, c = Math.floor(i / 4); return st[r + 4 * ((c + r) % 4)]; });
  const mix = st => { const o = []; for (let c = 0; c < 4; c++) { const [a0, a1, a2, a3] = st.slice(4 * c, 4 * c + 4);
    o.push(mul(a0, 2) ^ mul(a1, 3) ^ a2 ^ a3, a0 ^ mul(a1, 2) ^ mul(a2, 3) ^ a3, a0 ^ a1 ^ mul(a2, 2) ^ mul(a3, 3), mul(a0, 3) ^ a1 ^ a2 ^ mul(a3, 2)); } return o; };
  const add = (st, k) => st.map((v, i) => v ^ k[i]);
  const expand = key => { const w = [key.slice()]; let rc = 1;
    for (let r = 1; r <= 10; r++) { const p = w[r - 1], t = [SB[p[13]] ^ rc, SB[p[14]], SB[p[15]], SB[p[12]]], k = [];
      for (let i = 0; i < 16; i++) k.push(p[i] ^ (i < 4 ? t[i] : k[i - 4]));
      w.push(k); rc = xt(rc); } return w; };
  const hex2 = v => v.toString(16).padStart(2, '0');
  const parse = (t, what) => { const s = String(t).replace(/\s+/g, '').toLowerCase(); if (!/^[0-9a-f]{32}$/.test(s)) throw new Error(`${what} must be 32 hex digits (16 bytes).`); return s.match(/../g).map(x => parseInt(x, 16)); };
  return { SB, sub, shift, mix, add, expand, mul, xt, hex2, parse };
})();

/* =====================================================================================================
   Cryptography 1.1  the Caesar cipher: shift every letter by k places, C = (P + k) mod 26
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', CW = 21, X0 = 27;
  trace('cycaesar', {
    title: 'The Caesar cipher: shift every letter',
    sub: 'Julius Caesar shifted each letter of his messages three places along the alphabet. Pick a message and a shift and encrypt it letter by letter.',
    W: 600, H: 340,
    params: [
      { k: 'text', label: 'Message (letters and spaces)', type: 'text', v: 'ATTACK AT DAWN' },
      { k: 'k', label: 'Shift (the key)', type: 'range', v: 3, min: 0, max: 25 }
    ],
    tips: [
      { t: 'Play it with shift 3, the shift Caesar used. A becomes D, T becomes W.', play: true },
      { t: 'Try shift 13 (ROT13). Encrypting twice with 13 gives the message back, because 13 + 13 = 26.', set: { k: 13 }, play: true },
      { t: 'Try shift 0. The "cipher" does nothing. Together with 25 real shifts, there are only 26 keys, so an attacker simply tries them all.', set: { k: 0 }, play: true }
    ],
    frames(p) {
      const t = String(p.text).toUpperCase().replace(/[^A-Z ]/g, '').slice(0, 16), k = +p.k;
      if (!t.replace(/ /g, '')) throw new Error('Type a message with some letters.');
      const out = [], fr = [{ n: 0, say: `Write the alphabet, then the same alphabet moved ${k} place${k === 1 ? '' : 's'} to the left. Each letter on top is replaced by the letter under it. The shift ${k} is the <b>key</b>.` }];
      for (let i = 0; i < t.length; i++) {
        const ch = t[i];
        if (ch === ' ') { out.push(' '); continue; }
        const P = ABC.indexOf(ch), C = (P + k) % 26;
        out.push(ABC[C]);
        fr.push({ n: i + 1, P, C, say: `${ch} is letter number ${P} (A = 0). C = (${P} + ${k}) mod 26 = ${C}, which is <b>${ABC[C]}</b>.${P + k >= 26 ? ' The count went past Z, so it wraps round to the start: that is what mod 26 means.' : ''}` });
      }
      fr.push({ n: t.length, done: true, say: `Ciphertext: <b>${out.join('')}</b>. To decrypt, shift back: P = (C &minus; ${k}) mod 26. An attacker without the key just tries all 26 shifts and reads which one makes sense. A key space of 26 is far too small.` });
      return fr.map(x => ({ ...x, t, k, out }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      for (let i = 0; i < 26; i++) {
        const hot = f.P === i && !f.done;
        cbox(z, X0 + i * CW, 14, CW - 2, 24, ABC[i], { s: 12, b: true, mono: true, fill: hot ? c.orange : c.surf, c: hot ? '#fff' : c.ink, r: 3 });
        cbox(z, X0 + i * CW, 74, CW - 2, 24, ABC[(i + f.k) % 26], { s: 12, b: true, mono: true, fill: hot ? c.cv : c.bg, c: hot ? '#fff' : c.ink, r: 3 });
      }
      D.text(g, 'plain', X0, 52, { s: 10, b: true, c: c.ink2 }); D.text(g, 'cipher (shift ' + f.k + ')', X0, 68, { s: 10, b: true, c: c.ink2 });
      if (f.P !== undefined && !f.done) D.arrow(g, X0 + f.P * CW + 10, 40, X0 + f.P * CW + 10, 72, c.orange, 2, 6);
      const W = Math.min(34, 560 / f.t.length);
      for (let i = 0; i < f.n; i++) {
        const x = X0 + i * W;
        cbox(z, x, 124, W - 3, 28, f.t[i], { s: 14, b: true, mono: true, fill: c.surf });
        cbox(z, x, 160, W - 3, 28, f.out[i], { s: 14, b: true, mono: true, fill: f.t[i] === ' ' ? c.surf : 'rgba(15,118,110,0.18)' });
      }
      if (f.n) { D.text(g, 'message', X0, 118, { s: 10, b: true, c: c.ink2 }); }
      if (f.P !== undefined && !f.done) cbox(z, X0, 206, 546, 34, `C = (P + k) mod 26 = (${f.P} + ${f.k}) mod 26 = ${f.C}  →  ${ABC[f.C]}`, { s: 14, b: true, mono: true, fill: c.bg });
      if (f.done) {
        cbox(z, X0, 206, 546, 34, 'ciphertext  ' + f.out.join(''), { s: 15, b: true, mono: true, fill: c.cv, c: '#fff' });
        cbox(z, X0, 250, 546, 30, 'key space = 26 shifts  →  try them all (brute force)', { s: 13, b: true, fill: c.surf, c: c.red });
        cbox(z, X0, 288, 546, 30, 'decrypt: P = (C − k) mod 26', { s: 13, b: true, mono: true, fill: c.bg });
      }
    }
  });
})();

/* =====================================================================================================
   Cryptography 1.1  frequency analysis: letter counts and a chi-squared score find a Caesar shift
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  /* split text into lines of at most n characters, breaking at spaces */
  const lineSplit = (t, n) => { const out = []; let cur = ''; t.split(' ').forEach(w => { if ((cur + ' ' + w).trim().length > n) { out.push(cur); cur = w; } else cur = (cur + ' ' + w).trim(); }); if (cur) out.push(cur); return out; };
  const EN = [8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4, 6.7, 7.5, 1.9, 0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074];
  const MSG = {
    long: ['A long message (shift 7)', 7, 'THE SECURITY OF A SYSTEM SHOULD DEPEND ONLY ON THE SECRECY OF THE KEY AND NOT ON THE SECRECY OF THE METHOD. ATTACKERS WILL LEARN HOW YOUR SYSTEM WORKS SOONER OR LATER BECAUSE PROGRAMS ARE STOLEN AND PEOPLE TALK. THE ONLY THING THAT MUST STAY SECRET IS THE SMALL KEY WHICH YOU CAN CHANGE QUICKLY.'],
    mid: ['A medium message (shift 19)', 19, 'MEET ME NEAR THE OLD LIBRARY AT NINE TONIGHT AND BRING THE NOTES FROM THE LAST MEETING. DO NOT TELL ANYONE ELSE WHERE WE ARE GOING.'],
    tiny: ['A very short message (shift 4)', 4, 'ZOO QUIZ']
  };
  const shift = (s, k) => s.replace(/[A-Z]/g, ch => ABC[(ABC.indexOf(ch) + k + 26) % 26]);
  const counts = s => { const n = new Array(26).fill(0); for (const ch of s) { const i = ABC.indexOf(ch); if (i >= 0) n[i]++; } return n; };
  const chi = s => { const n = counts(s), N = n.reduce((a, b) => a + b, 0); return n.reduce((a, o, i) => { const e = EN[i] / 100 * N; return a + (o - e) ** 2 / e; }, 0); };
  trace('cyfreq', {
    title: 'Breaking a Caesar cipher with letter frequencies',
    sub: 'In English, E, T and A are common and Z is rare. A Caesar cipher keeps that pattern, only shifted. Count the letters, compare with English for every shift, and the best match gives the key.',
    W: 600, H: 340,
    params: [{ k: 'm', label: 'Secret message', type: 'select', v: 'long', opts: Object.keys(MSG).map(k => [k, MSG[k][0]]) }],
    tips: [
      { t: 'Play it on the long message. The tallest bar is the letter that stands for E.', play: true },
      { t: 'Try the medium message. It still works, with less margin.', set: { m: 'mid' }, play: true },
      { t: 'Try the very short message. With seven letters the counts are too small, and the best score picks the wrong shift. Statistics need enough data.', set: { m: 'tiny' }, play: true }
    ],
    frames(p) {
      const [, key, plain] = MSG[p.m];
      const cipher = shift(plain, key), letters = cipher.replace(/[^A-Z]/g, '');
      const n = counts(letters), N = letters.length;
      const scores = []; for (let k = 0; k < 26; k++) scores.push(chi(shift(letters, -k)));
      let best = 0; scores.forEach((s, k) => { if (s < scores[best]) best = k; });
      const top = n.indexOf(Math.max(...n));
      const fr = [
        { k: 1, say: `The intercepted ciphertext has ${N} letters. Count how often each letter appears. The most common is <b>${ABC[top]}</b> (${n[top]} times).` },
        { k: 2, say: 'The outlines show normal English: E about 12.7%, T 9.1%, A 8.2%. The ciphertext bars have the same shape, moved sideways by the key.' },
        { k: 3, say: 'For every shift k from 0 to 25, decrypt and score how far the counts are from English with the chi-squared sum &chi;<sup>2</sup> = &Sigma; (observed &minus; expected)<sup>2</sup> / expected. Small means "looks like English".' },
        { k: 4, say: `The smallest score is at <b>k = ${best}</b>${best === key ? ', the real key' : `, but the real key was ${key}. The message is too short for the counts to mean anything`}.` },
        { k: 5, done: true, say: best === key ? `Decrypting with ${best} gives readable English. Caesar falls to one count and 26 tries. Any cipher that keeps letter frequencies, even one with 26! keys, falls to frequency analysis, as al-Kindi described in the 9th century.` : 'A wrong key gives nonsense. Frequency analysis needs enough letters: roughly 50 or more for a Caesar shift and a few hundred for a full substitution cipher.' }
      ];
      return fr.map(x => ({ ...x, cipher, plain, n, N, scores, best, key }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const lines = lineSplit(f.k >= 5 ? shift(f.cipher, -f.best) : f.cipher, 92).slice(0, 3);
      lines.forEach((l, i) => D.text(g, l, 14, 18 + i * 14, { s: 10, mono: true, c: f.k >= 5 ? (f.best === f.key ? c.green : c.red) : c.ink }));
      const bx = 20, bw = 21, base = 196, hs = 6;
      for (let i = 0; i < 26; i++) {
        const x = bx + i * bw;
        D.text(g, ABC[i], x + bw / 2 - 1, base + 14, { a: 'center', s: 10, b: true, mono: true, c: c.ink2 });
        const pctv = f.n[i] / f.N * 100;
        g.fillStyle = c.cv; g.globalAlpha = 0.8; g.fillRect(x + 2, base - pctv * hs, bw - 5, pctv * hs); g.globalAlpha = 1;
        if (f.k >= 2) { g.strokeStyle = c.orange; g.lineWidth = 2; g.strokeRect(x + 1, base - EN[i] * hs, bw - 3, EN[i] * hs); }
      }
      D.text(g, 'bars: ciphertext letters (%)', 568, 66, { a: 'right', s: 10, b: true, c: c.cv });
      if (f.k >= 2) D.text(g, 'outlines: English (%)', 568, 80, { a: 'right', s: 10, b: true, c: c.orange });
      if (f.k >= 3) {
        const max = Math.max(...f.scores), y0 = 318, hh = 84;
        D.text(g, 'χ² for each shift k (lower is better)', 14, 228, { s: 10, b: true, c: c.ink2 });
        f.scores.forEach((s, k) => {
          const h = s / max * hh, x = bx + k * bw;
          const win = f.k >= 4 && k === f.best;
          g.fillStyle = win ? c.green : 'rgba(100,116,139,0.45)'; g.fillRect(x + 2, y0 - Math.max(h, win ? 6 : 0), bw - 5, Math.max(h, win ? 6 : 0));
          if (win) D.text(g, 'best', x + bw / 2 - 1, y0 - Math.max(h, 6) - 4, { a: 'center', s: 10, b: true, c: c.green });
          D.text(g, String(k), x + bw / 2 - 1, y0 + 12, { a: 'center', s: 8, c: c.ink2 });
        });
      }
    }
  });
})();

/* =====================================================================================================
   Cryptography 1.1  the Vigenere cipher: a repeating key word, one Caesar shift per key letter
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', X0 = 70, CW = 37;
  trace('cyvigenere', {
    title: 'The Vigenère cipher: a different shift for each letter',
    sub: 'A key word sets the shift for each letter in turn (A = 0, B = 1, ...), then repeats. The same plain letter can become different cipher letters, which hides the letter counts.',
    W: 600, H: 340,
    params: [
      { k: 'text', label: 'Message (letters only)', type: 'text', v: 'ATTACKATDAWN' },
      { k: 'key', label: 'Key word', type: 'text', v: 'LEMON' }
    ],
    tips: [
      { t: 'Play it. The four A letters in ATTACKATDAWN become L, O, E and N: the counts are hidden.', play: true },
      { t: 'Try the key A. Every shift is 0, so nothing changes. Weak keys exist.', set: { key: 'A' }, play: true },
      { t: 'Try a key as long as the message, such as QWERTYUIOPAS. If it were truly random and never reused, this would be a one time pad.', set: { key: 'QWERTYUIOPAS' }, play: true }
    ],
    frames(p) {
      const t = String(p.text).toUpperCase().replace(/[^A-Z]/g, '').slice(0, 14);
      const key = String(p.key).toUpperCase().replace(/[^A-Z]/g, '');
      if (!t) throw new Error('Type a message with some letters.');
      if (!key) throw new Error('Type a key word with letters.');
      const out = [], fr = [];
      for (let i = 0; i < t.length; i++) {
        const P = ABC.indexOf(t[i]), K = ABC.indexOf(key[i % key.length]), C = (P + K) % 26;
        out.push(ABC[C]);
        fr.push({ n: i + 1, P, K, C, say: `Letter ${i + 1}: ${t[i]} (${P}) with key letter ${key[i % key.length]} (${K}). C = (${P} + ${K}) mod 26 = ${C} = <b>${ABC[C]}</b>.${i === key.length ? ' The key has run out, so it starts again from its first letter.' : ''}` });
      }
      fr.push({ n: t.length, done: true, say: `Ciphertext: <b>${out.join('')}</b>. The weakness: letters ${key.length} apart use the same shift. Once an attacker finds the key length m (Kasiski test or index of coincidence), the message splits into m Caesar ciphers, and frequency analysis breaks each one.` });
      return fr.map(x => ({ ...x, t, key, out }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      [['plain', 34], ['key', 74], ['cipher', 114]].forEach(([l, y]) => D.text(g, l, 14, y, { s: 11, b: true, c: c.ink2 }));
      for (let i = 0; i < f.n; i++) {
        const x = X0 + i * CW, cur = i === f.n - 1 && !f.done, col = i % f.key.length;
        cbox(z, x, 16, CW - 4, 28, f.t[i], { s: 15, b: true, mono: true, fill: cur ? c.orange : c.surf, c: cur ? '#fff' : c.ink });
        cbox(z, x, 56, CW - 4, 28, f.key[col], { s: 15, b: true, mono: true, fill: f.done ? ['rgba(15,118,110,0.25)', 'rgba(234,88,12,0.22)', 'rgba(124,58,237,0.22)', 'rgba(37,99,235,0.22)', 'rgba(219,39,119,0.22)'][col % 5] : c.bg });
        cbox(z, x, 96, CW - 4, 28, f.out[i], { s: 15, b: true, mono: true, fill: cur ? c.cv : 'rgba(15,118,110,0.15)', c: cur ? '#fff' : c.ink });
      }
      if (!f.done) cbox(z, 14, 146, 572, 34, `C = (P + K) mod 26 = (${f.P} + ${f.K}) mod 26 = ${f.C}  →  ${ABC[f.C]}`, { s: 14, b: true, mono: true, fill: c.bg });
      if (f.done) {
        D.text(g, `Split by key position (m = ${f.key.length}): each column is one Caesar cipher`, 14, 162, { s: 12, b: true, c: c.ink });
        for (let j = 0; j < Math.min(f.key.length, 5); j++) {
          const plainCol = [], cipherCol = [];
          for (let i = j; i < f.t.length; i += f.key.length) { plainCol.push(f.t[i]); cipherCol.push(f.out[i]); }
          cbox(z, 14, 174 + j * 30, 572, 26, `key ${f.key[j]} (shift ${ABC.indexOf(f.key[j])}):  ${plainCol.join(' ')}  →  ${cipherCol.join(' ')}`, { s: 12, b: true, mono: true, fill: c.surf });
        }
      }
    }
  });
})();

/* =====================================================================================================
   Cryptography 1.2  one AES round on the 4 x 4 state: AddRoundKey, SubBytes, ShiftRows, MixColumns, AddRoundKey
   ===================================================================================================== */
(() => {
  const { trace, head } = MLZ;
  const { cbox, D } = CYZ;
  const A = CYAES, H = A.hex2;
  const CELL = 46;
  trace('cyaesround', {
    title: 'Inside AES: one round on the 4 × 4 state',
    sub: 'AES puts 16 bytes into a 4 × 4 grid called the state and changes it in four steps per round, ten rounds for a 128 bit key. These are the real AES numbers, the example from the standard FIPS 197.',
    W: 600, H: 340,
    params: [
      { k: 'pt', label: 'Plaintext block (32 hex digits)', type: 'text', v: '00112233445566778899aabbccddeeff' },
      { k: 'key', label: 'Key (32 hex digits)', type: 'text', v: '000102030405060708090a0b0c0d0e0f' }
    ],
    tips: [
      { t: 'Play it with the FIPS 197 example. The last step shows the ciphertext 69c4e0d8..., exactly as the standard prints it.', play: true },
      { t: 'Change the last plaintext digit from f to e. After all ten rounds about half the ciphertext bits change.', set: { pt: '00112233445566778899aabbccddeefe' }, play: true }
    ],
    frames(p) {
      const pt = A.parse(p.pt, 'The plaintext'), key = A.parse(p.key, 'The key');
      const ks = A.expand(key);
      const s0 = A.add(pt, ks[0]), s1 = A.sub(s0), s2 = A.shift(s1), s3 = A.mix(s2), s4 = A.add(s3, ks[1]);
      let st = s4;
      for (let r = 2; r <= 10; r++) { st = A.sub(st); st = A.shift(st); if (r < 10) st = A.mix(st); st = A.add(st, ks[r]); }
      const m0 = s2.slice(0, 4);
      const fr = [
        { a: pt, b: key, la: 'plaintext', lb: 'key', op: 'load', say: 'Write the 16 plaintext bytes into the state column by column: the first four bytes are column 1. The 16 key bytes go into a grid the same way.' },
        { a: pt, b: s0, la: 'plaintext', lb: 'after AddRoundKey', op: '⊕ key', say: `<b>AddRoundKey</b>: XOR every byte with the matching key byte. ${H(pt[0])} ⊕ ${H(key[0])} = ${H(s0[0])}. Without the key, nothing after this can be undone.` },
        { a: s0, b: s1, la: 'state', lb: 'after SubBytes', op: 'S-box', say: `<b>SubBytes</b>: replace every byte using the S-box, a fixed table built from inverses in the field GF(2<sup>8</sup>). ${H(s0[0])} becomes ${H(s1[0])}. This is the only non linear step, and it stops attacks that solve equations.` },
        { a: s1, b: s2, la: 'state', lb: 'after ShiftRows', op: 'rotate', rows: true, say: '<b>ShiftRows</b>: row 0 stays, row 1 moves one place left, row 2 two places, row 3 three places. Now every column holds bytes from four different columns.' },
        { a: s2, b: s3, la: 'state', lb: 'after MixColumns', op: 'mix', col: true, say: `<b>MixColumns</b>: each column is multiplied by a fixed matrix in GF(2<sup>8</sup>). New top byte of column 1 = 2·${H(m0[0])} ⊕ 3·${H(m0[1])} ⊕ ${H(m0[2])} ⊕ ${H(m0[3])} = ${H(s3[0])}. Changing one input byte changes all four output bytes.` },
        { a: s3, b: s4, la: 'state', lb: 'after round 1', op: '⊕ key 1', say: `<b>AddRoundKey</b> with round key 1, made from the main key by the key schedule. Round 1 is done. ShiftRows spreads bytes across columns and MixColumns mixes within columns, so after two rounds every byte depends on every input byte.` },
        { a: s4, b: st, la: 'after round 1', lb: 'ciphertext', op: '9 more', done: true, say: `Rounds 2 to 10 repeat the same four steps (round 10 skips MixColumns). Ciphertext: <b>${st.map(H).join('')}</b>.${st.map(H).join('') === '69c4e0d86a7b0430d8cdb78070b4c55a' ? ' This is exactly the answer printed in FIPS 197 Appendix C.1.' : ''}` }
      ];
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const grid = (st, x, y, label, other, hl) => {
        D.text(g, label, x + 2 * CELL, y - 8, { a: 'center', s: 12, b: true, c: c.ink });
        for (let i = 0; i < 16; i++) {
          const r = i % 4, col = Math.floor(i / 4), changed = other && other[i] !== st[i];
          let fill = c.surf;
          if (hl && f.rows) fill = ['rgba(15,118,110,0.18)', 'rgba(234,88,12,0.2)', 'rgba(124,58,237,0.2)', 'rgba(37,99,235,0.2)'][r];
          else if (hl && f.col && col === 0) fill = 'rgba(234,88,12,0.25)';
          else if (hl && changed) fill = 'rgba(15,118,110,0.2)';
          cbox(z, x + col * CELL, y + r * CELL, CELL - 4, CELL - 4, H(st[i]), { s: 15, b: true, mono: true, fill, r: 4 });
        }
      };
      grid(f.a, 24, 34, f.la, null, f.rows || f.col);
      grid(f.b, 384, 34, f.lb, f.a, true);
      D.arrow(g, 222, 124, 372, 124, c.cv, 2.5, 9);
      cbox(z, 236, 88, 124, 26, f.op, { s: 13, b: true, fill: c.cv, c: '#fff' });
      if (f.done) cbox(z, 24, 232, 552, 30, f.b.map(H).join(''), { s: 15, b: true, mono: true, fill: c.bg });
      const names = ['AddRoundKey', 'SubBytes', 'ShiftRows', 'MixColumns', 'AddRoundKey'];
      const at = { '⊕ key': 0, 'S-box': 1, rotate: 2, mix: 3, '⊕ key 1': 4 }[f.op];
      names.forEach((n, i) => cbox(z, 24 + i * 112, 300, 104, 26, n, { s: 11, b: true, fill: at === i ? c.orange : (at > i || f.done ? 'rgba(15,118,110,0.2)' : c.surf), c: at === i ? '#fff' : c.ink }));
      D.text(g, 'one round:', 24, 292, { s: 10, b: true, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Cryptography 1.2  the ECB penguin problem on a small picture: ECB keeps patterns, CBC and CTR hide them
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { D, sha256, utf8 } = CYZ;
  const PICS = {
    lock: ['................', '.....######.....', '....##....##....', '...##......##...', '...#........#...', '...#........#...', '..############..', '..#oooooooooo#..', '..#oooo##oooo#..', '..#oooo##oooo#..', '..#oooo##oooo#..', '..#oooooooooo#..', '..#oooooooooo#..', '..############..', '................', '................'],
    smile: ['................', '....########....', '...#........#...', '..#..........#..', '..#..##..##..#..', '..#..##..##..#..', '..#..........#..', '..#..........#..', '..#.#......#.#..', '..#..#....#..#..', '..#...####...#..', '...#........#...', '....########....', '................', '................', '................']
  };
  const CODE = { '.': 0, '#': 1, o: 2 };
  const PAL = ['#f8fafc', '#1e293b', '#f97316'];
  const CELL = 8, PANEL = 16 * CELL;
  trace('cyecb', {
    title: 'Why ECB mode leaks: encrypting a picture block by block',
    sub: 'A block cipher encrypts fixed size blocks. Here every block is 4 pixels. ECB encrypts each block on its own, CBC chains each block to the one before, and CTR mixes in a counter. Watch which one still shows the picture.',
    W: 600, H: 340,
    params: [
      { k: 'pic', label: 'Picture', type: 'select', v: 'lock', opts: [['lock', 'A padlock'], ['smile', 'A smiling face']] },
      { k: 'key', label: 'Key', type: 'text', v: 'demo key' }
    ],
    tips: [
      { t: 'Play it. In the ECB picture, every plain white block becomes the same coloured block, so the outline survives.', play: true },
      { t: 'Change the key. The colours change, but ECB still shows the shape. A stronger cipher cannot fix a weak mode.', set: { key: 'another key' }, play: true },
      { t: 'Try the smiling face. Same story: identical input blocks give identical output blocks in ECB only.', set: { pic: 'smile' }, play: true }
    ],
    frames(p) {
      const rows = PICS[p.pic], key = utf8(String(p.key));
      const blocks = [];
      rows.forEach(r => { for (let b = 0; b < 4; b++) blocks.push(r.slice(4 * b, 4 * b + 4).split('').map(ch => CODE[ch])); });
      const E = bytes => sha256(key.concat([0x42], bytes)).slice(0, 4);
      const ecb = blocks.map(b => E(b));
      let prev = sha256(key.concat([0x49, 0x56])).slice(0, 4);
      const cbc = blocks.map(b => { const x = b.map((v, i) => v ^ prev[i]); prev = E(x); return prev; });
      const ctr = blocks.map((b, n) => { const ks = sha256(key.concat([0x43, n])).slice(0, 4); return b.map((v, i) => v ^ ks[i]); });
      const seen = {}; ecb.forEach(c => { const k = c.join(','); seen[k] = (seen[k] || 0) + 1; });
      const distinct = Object.keys(seen).length;
      const fr = [
        { k: 1, say: `The picture is 16 × 16 pixels, cut into ${blocks.length} blocks of 4 pixels. Many blocks are identical: all white, all dark, or all orange.` },
        { k: 2, say: '<b>ECB</b> (electronic codebook) encrypts each block on its own with the same key: C<sub>i</sub> = E<sub>k</sub>(P<sub>i</sub>). The colours look random, yet the padlock is still there.' },
        { k: 3, say: `Why: identical plaintext blocks give identical ciphertext blocks. The ${blocks.length} blocks produce only <b>${distinct}</b> different ciphertext blocks. An attacker learns which parts of the data repeat, without the key.` },
        { k: 4, say: '<b>CBC</b> (cipher block chaining) XORs each plaintext block with the previous ciphertext block before encrypting: C<sub>i</sub> = E<sub>k</sub>(P<sub>i</sub> ⊕ C<sub>i&minus;1</sub>), starting from a random IV. Every block now differs.' },
        { k: 5, done: true, say: '<b>CTR</b> (counter) encrypts a nonce and a counter to make a key stream, and XORs it with the data: C<sub>i</sub> = P<sub>i</sub> ⊕ E<sub>k</sub>(nonce ‖ i). It also hides the picture, and blocks can be done in parallel. Never use ECB for data longer than one block.' }
      ];
      return fr.map(x => ({ ...x, blocks, ecb, cbc, ctr }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const panel = (x, list, label, plain) => {
        D.text(g, label, x + PANEL / 2, 34, { a: 'center', s: 12, b: true, c: c.ink });
        list.forEach((blk, n) => {
          const row = Math.floor(n / 4), col = n % 4;
          /* an encrypted block gets one colour made from its first bytes, so equal blocks look equal */
          const enc = `hsl(${Math.round(blk[0] * 360 / 256)}, 65%, ${32 + blk[1] % 36}%)`;
          blk.forEach((v, i) => { g.fillStyle = plain ? PAL[v] : enc; g.fillRect(x + (col * 4 + i) * CELL, 46 + row * CELL, CELL, CELL); });
        });
        g.strokeStyle = c.line; g.lineWidth = 1; g.strokeRect(x - 0.5, 45.5, PANEL + 1, PANEL + 1);
        if (plain) { g.strokeStyle = 'rgba(100,116,139,0.35)'; for (let b = 1; b < 4; b++) { g.beginPath(); g.moveTo(x + b * 4 * CELL, 46); g.lineTo(x + b * 4 * CELL, 46 + PANEL); g.stroke(); } }
      };
      const xs = [14, 162, 310, 458];
      panel(xs[0], f.blocks, 'original', true);
      if (f.k >= 2) panel(xs[1], f.ecb, 'ECB', false);
      if (f.k >= 4) panel(xs[2], f.cbc, 'CBC', false);
      if (f.k >= 5) panel(xs[3], f.ctr, 'CTR', false);
      if (f.k === 3) { g.strokeStyle = c.red; g.lineWidth = 2; g.strokeRect(xs[1] - 3, 43, PANEL + 6, PANEL + 6); D.text(g, 'the shape survives', xs[1] + PANEL / 2, 196, { a: 'center', s: 11, b: true, c: c.red }); }
      const rows = [['ECB', 'C<i> = E(P<i>)', 'same input block, same output block', c.red], ['CBC', 'C<i> = E(P<i> ⊕ C<i−1>)', 'needs a random IV, encrypts one block at a time', c.green], ['CTR', 'C<i> = P<i> ⊕ E(nonce ‖ i)', 'parallel, never repeat a nonce', c.green]];
      rows.forEach(([n, fml, why, col], i) => {
        if (f.k < [2, 4, 5][i]) return;
        const y = 222 + i * 34;
        D.text(g, n, 14, y + 18, { s: 13, b: true, c: col });
        D.text(g, fml.replace(/<i>/g, 'ᵢ').replace(/<i−1>/g, 'ᵢ₋₁'), 64, y + 18, { s: 12, b: true, mono: true, c: c.ink });
        D.text(g, why, 300, y + 18, { s: 11, c: c.ink2 });
      });
    }
  });
})();

/* =====================================================================================================
   Cryptography 1.2  CBC mode as a chain: P1 xor IV, encrypt, then each ciphertext feeds the next block
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const A = CYAES, H = v => A.hex2(v).toUpperCase();
  const XS = [150, 300, 450];
  trace('cycbc', {
    title: 'CBC mode step by step',
    sub: 'A toy block cipher with 1 byte blocks, E(x) = S-box(x ⊕ key), shows the chain. Each plaintext block is XORed with the previous ciphertext block, so two equal blocks encrypt differently.',
    W: 600, H: 340,
    params: [
      { k: 'msg', label: 'Message (3 letters)', type: 'text', v: 'AAB' },
      { k: 'iv', label: 'IV (2 hex digits)', type: 'text', v: '3C' },
      { k: 'key', label: 'Key (2 hex digits)', type: 'text', v: '9F' }
    ],
    tips: [
      { t: 'Play it with AAB. The two A blocks give different ciphertexts in CBC, but the same ciphertext in ECB (bottom row).', play: true },
      { t: 'Change only the IV. Every ciphertext block changes, so the same message sent twice looks different each time.', set: { iv: 'A7' }, play: true }
    ],
    frames(p) {
      const msg = String(p.msg).slice(0, 3);
      if (msg.length !== 3) throw new Error('Type exactly 3 characters.');
      const hx = (t, w) => { const s = String(t).trim(); if (!/^[0-9a-fA-F]{2}$/.test(s)) throw new Error(`${w} must be 2 hex digits, such as 3C.`); return parseInt(s, 16); };
      const iv = hx(p.iv, 'The IV'), key = hx(p.key, 'The key');
      const P = Array.from(msg).map(ch => ch.charCodeAt(0) & 255);
      const E = x => A.SB[x ^ key];
      const X = [], C = [];
      let prev = iv;
      P.forEach(v => { X.push(v ^ prev); C.push(E(v ^ prev)); prev = C[C.length - 1]; });
      const ecb = P.map(E);
      const fr = [];
      P.forEach((v, i) => {
        const feed = i ? `C${i} = ${H(C[i - 1])}` : `IV = ${H(iv)}`;
        fr.push({ n: i, half: true, say: `Block ${i + 1}: "${msg[i]}" = ${H(v)}. XOR it with ${i ? 'the previous ciphertext' : 'the random IV'}: ${H(v)} ⊕ ${feed.split('= ')[1]} = <b>${H(X[i])}</b>.` });
        fr.push({ n: i, say: `Encrypt: C${i + 1} = E(${H(X[i])}) = S-box(${H(X[i])} ⊕ ${H(key)}) = <b>${H(C[i])}</b>. ${i < 2 ? `C${i + 1} now feeds into block ${i + 2}.` : ''}` });
      });
      fr.push({ n: 2, done: true, say: `CBC ciphertext: ${C.map(H).join(' ')}. ECB on the same message: ${ecb.map(H).join(' ')}${P[0] === P[1] ? ', where the two equal blocks give equal ciphertexts' : ''}. To decrypt CBC: P<sub>i</sub> = D(C<sub>i</sub>) ⊕ C<sub>i&minus;1</sub>. Flipping a bit of C<sub>i&minus;1</sub> flips the same bit of P<sub>i</sub>, which is why CBC needs a MAC as well.` });
      return fr.map(x => ({ ...x, P, X, C, iv, key, ecb, msg }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      cbox(z, 14, 96, 70, 30, 'IV ' + H(f.iv), { s: 12, b: true, mono: true, fill: c.bg });
      D.text(g, 'plaintext', 14, 32, { s: 11, b: true, c: c.ink2 }); D.text(g, 'XOR', 14, 150, { s: 11, b: true, c: c.ink2 }); D.text(g, 'encrypt', 14, 196, { s: 11, b: true, c: c.ink2 }); D.text(g, 'ciphertext', 14, 250, { s: 11, b: true, c: c.ink2 });
      for (let i = 0; i <= f.n; i++) {
        const x = XS[i], full = i < f.n || !f.half || f.done;
        cbox(z, x - 45, 16, 90, 30, `"${f.msg[i]}" ${H(f.P[i])}`, { s: 13, b: true, mono: true, fill: c.surf });
        D.arrow(g, x, 46, x, 128, c.ink2, 1.5, 7);
        g.strokeStyle = c.cv; g.lineWidth = 2; g.beginPath(); g.arc(x, 142, 12, 0, Math.PI * 2); g.stroke();
        D.text(g, '⊕', x, 148, { a: 'center', s: 16, b: true, c: c.cv });
        const fx = i ? XS[i - 1] + 45 : 84, fy = i ? 252 : 111;
        D.arrow(g, fx, fy, x - 13, 142, c.orange, 2, 7);
        D.text(g, H(f.X[i]), x + 18, 166, { s: 12, b: true, mono: true, c: c.ink });
        if (!full) continue;
        D.arrow(g, x, 154, x, 180, c.ink2, 1.5, 7);
        cbox(z, x - 45, 180, 90, 30, 'E (key ' + H(f.key) + ')', { s: 11, b: true, fill: c.cv, c: '#fff' });
        D.arrow(g, x, 210, x, 236, c.ink2, 1.5, 7);
        cbox(z, x - 45, 236, 90, 32, 'C' + (i + 1) + ' ' + H(f.C[i]), { s: 13, b: true, mono: true, fill: 'rgba(15,118,110,0.2)' });
      }
      if (f.done) {
        D.text(g, 'ECB instead:', 14, 312, { s: 11, b: true, c: c.ink2 });
        f.ecb.forEach((v, i) => cbox(z, XS[i] - 45, 294, 90, 28, H(v), { s: 13, b: true, mono: true, fill: i && f.ecb[i] === f.ecb[i - 1] ? 'rgba(225,29,72,0.2)' : c.surf }));
      }
    }
  });
})();
