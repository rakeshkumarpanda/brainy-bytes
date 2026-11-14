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

/* =====================================================================================================
   Cryptography 1.3  a Merkle-Damgard hash chain and the length extension attack on H(secret || message)
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D, sha256, utf8 } = CYZ;
  const SECRET = utf8('k3y-sec!'), BS = 8, IV = [0x6a, 0x09, 0xe6, 0x67];
  const hx = a => a.map(v => v.toString(16).padStart(2, '0')).join('');
  /* toy compression: 4 byte state, 8 byte blocks, built from real SHA-256 */
  const f = (st, blk) => sha256(st.concat(blk)).slice(0, 4);
  const pad = total => { const out = [0x80]; while ((total + out.length + 1) % BS) out.push(0); out.push(total & 255); return out; };
  const chain = (bytes, st, done) => { const all = bytes.concat(pad(done + bytes.length)), blocks = [], states = [st]; for (let i = 0; i < all.length; i += BS) { blocks.push(all.slice(i, i + BS)); st = f(st, all.slice(i, i + BS)); states.push(st); } return { blocks, states, padded: all }; };
  const show = (blk, from) => blk.map((v, i) => from + i < 8 ? '•' : (v >= 32 && v < 127 ? String.fromCharCode(v) : '·')).join('');
  trace('cymd', {
    title: 'How SHA-256 chains blocks, and the length extension attack',
    sub: 'Hashes like MD5, SHA-1 and SHA-256 cut the input into blocks and feed each block into a compression function together with the result so far. A toy version with 8 byte blocks shows the chain, and why the final hash lets an attacker keep going.',
    W: 600, H: 340,
    params: [
      { k: 'msg', label: 'Message the server signs', type: 'text', v: 'user=riya&role=reader' },
      { k: 'ext', label: 'What the attacker adds', type: 'text', v: '&role=admin' }
    ],
    tips: [
      { t: 'Play it. The server signs SHA(secret ‖ message). The attacker never sees the secret (shown as dots) yet produces a valid tag for a longer message.', play: true },
      { t: 'The fix is HMAC, or SHA-3, whose sponge design hides part of its state, so the output is not a full chaining value.', play: true }
    ],
    frames(p) {
      const msg = utf8(String(p.msg)).slice(0, 24), ext = utf8(String(p.ext)).slice(0, 14);
      if (!msg.length || !ext.length) throw new Error('Type a message and something to add.');
      const srv = chain(SECRET.concat(msg), IV, 0);
      const tag = srv.states[srv.states.length - 1];
      const glue = srv.padded.slice(SECRET.length + msg.length);
      const done = srv.padded.length;
      const atk = chain(ext, tag, done);
      const forged = atk.states[atk.states.length - 1];
      const check = chain(SECRET.concat(msg, glue, ext), IV, 0);
      const real = check.states[check.states.length - 1];
      const fr = [{ n: 0, say: `The server computes a tag as SHA(secret ‖ message). The secret (8 bytes, hidden as dots) and the message are cut into 8 byte blocks. The last block is padded with 0x80, zeros and the total length. The chain starts from a fixed IV, ${hx(IV)}.` }];
      srv.blocks.forEach((b, i) => fr.push({ n: i + 1, say: `Block ${i + 1} goes into the compression function f with the state so far: state = f(${hx(srv.states[i])}, block ${i + 1}) = <b>${hx(srv.states[i + 1])}</b>.${i === srv.blocks.length - 1 ? ' This was the padding block.' : ''}` }));
      fr.push({ n: srv.blocks.length, tag: true, say: `The final state <b>${hx(tag)}</b> is the hash, and the server publishes it as the tag of the message. But the final state is also exactly what f needs to continue the chain.` });
      fr.push({ n: srv.blocks.length, tag: true, atk: true, say: `The attacker knows the message and guesses the secret length. They start from the tag as if it were the state, and hash "${String.fromCharCode(...ext)}" with new padding: forged tag = <b>${hx(forged)}</b>. No secret needed.` });
      fr.push({ n: srv.blocks.length, tag: true, atk: true, done: true, ok: hx(real) === hx(forged), say: `The forged message is message ‖ old padding ‖ "${String.fromCharCode(...ext)}". The server checks SHA(secret ‖ forged message) = <b>${hx(real)}</b>, ${hx(real) === hx(forged) ? 'the same as the forged tag, so it accepts' : 'different'}. This broke the Flickr API signatures in 2009. Use HMAC instead.` });
      return fr.map(x => ({ ...x, srv, atk, tag, forged, real, msgLen: msg.length }));
    },
    paint(z, fz) {
      const c = z.col, g = z.g;
      const n = fz.srv.blocks.length, W = Math.min(96, 470 / n);
      D.text(g, 'server', 14, 22, { s: 11, b: true, c: c.ink2 });
      cbox(z, 14, 104, 72, 26, 'IV ' + hx(IV), { s: 10, b: true, mono: true, fill: c.bg });
      for (let i = 0; i < fz.n; i++) {
        const x = 104 + i * W, b = fz.srv.blocks[i];
        cbox(z, x, 30, W - 10, 30, show(b, i * BS), { s: 11, b: true, mono: true, fill: i === n - 1 ? 'rgba(234,88,12,0.18)' : c.surf });
        D.arrow(g, x + (W - 10) / 2, 60, x + (W - 10) / 2, 72, c.ink2, 1.5, 5);
        cbox(z, x, 72, W - 10, 24, 'f', { s: 13, b: true, fill: c.cv, c: '#fff' });
        D.arrow(g, x - 16, 117, x + (W - 10) / 2 - 4, 98, c.ink2, 1.2, 5);
        cbox(z, x, 104, W - 10, 26, hx(fz.srv.states[i + 1]), { s: 11, b: true, mono: true, fill: i === n - 1 && fz.tag ? 'rgba(15,118,110,0.25)' : c.bg });
      }
      if (fz.tag) D.text(g, 'tag = ' + hx(fz.tag), 104 + (n - 1) * W, 146, { s: 11, b: true, mono: true, c: c.cv });
      if (fz.atk) {
        D.text(g, 'attacker (no secret)', 14, 178, { s: 11, b: true, c: c.red });
        cbox(z, 14, 238, 72, 26, hx(fz.tag), { s: 10, b: true, mono: true, fill: 'rgba(15,118,110,0.25)' });
        fz.atk.blocks.forEach((b, i) => {
          const x = 104 + i * 110;
          cbox(z, x, 186, 100, 30, b.map(v => (v >= 32 && v < 127 ? String.fromCharCode(v) : '·')).join(''), { s: 11, b: true, mono: true, fill: 'rgba(225,29,72,0.15)' });
          cbox(z, x, 222, 100, 18, 'f', { s: 11, b: true, fill: c.cv, c: '#fff' });
          cbox(z, x, 246, 100, 24, hx(fz.atk.states[i + 1]), { s: 11, b: true, mono: true, fill: c.bg });
        });
        D.text(g, 'forged tag = ' + hx(fz.forged), 104, 290, { s: 12, b: true, mono: true, c: c.red });
      }
      if (fz.done) cbox(z, 14, 302, 572, 30, `server checks SHA(secret ‖ msg ‖ pad ‖ ext) = ${hx(fz.real)}  ${fz.ok ? '✓ accepted' : ''}`, { s: 12, b: true, mono: true, fill: fz.ok ? c.red : c.surf, c: fz.ok ? '#fff' : c.ink });
    }
  });
})();

/* =====================================================================================================
   Cryptography 1.3  the birthday paradox: random values in N boxes collide after about the square root of N
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D, f2 } = CYZ;
  const rng = seed => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const prob = (n, N) => { let q = 1; for (let i = 0; i < n; i++) q *= (N - i) / N; return 1 - q; };
  trace('cybirthday', {
    title: 'The birthday paradox: why collisions come so early',
    sub: 'Put people (or hash values) one by one into N equally likely boxes. How many until two share a box? Far fewer than N: about the square root of N. This decides how long a hash must be.',
    W: 600, H: 340,
    params: [
      { k: 'N', label: 'Number of boxes N', type: 'select', v: '365', opts: [['365', '365 birthdays'], ['256', '256 (an 8 bit hash)'], ['4096', '4,096 (a 12 bit hash)']] },
      { k: 'seed', label: 'Random run', type: 'range', v: 5, min: 1, max: 9 }
    ],
    tips: [
      { t: 'Play it with birthdays. With 23 people the chance of a shared birthday is already 50.7%.', play: true },
      { t: 'Try run 3: a shared birthday after only 8 people. Run 6 needs 49. Single runs vary, but most land near the 50% point.', set: { seed: 3 }, play: true },
      { t: 'Try the 12 bit hash. 4,096 boxes, yet a collision appears after 82 values here, close to 1.18 × √4096 ≈ 75.', set: { N: '4096', seed: 3 }, play: true }
    ],
    frames(p) {
      const N = +p.N, r = rng(+p.seed * 7919 + N), seen = new Map(), order = [];
      let hit = null;
      while (!hit && order.length < N + 1) { const v = Math.floor(r() * N); if (seen.has(v)) hit = { v, a: seen.get(v), b: order.length }; else seen.set(v, order.length); order.push(v); }
      const step = Math.max(1, Math.ceil(Math.sqrt(N) / 4)), fr = [];
      for (let n = step; n < order.length; n += step) fr.push({ n, say: `${n} values placed, all in different boxes so far. The chance of a collision by now is 1 &minus; (1 &minus; 1/N)(1 &minus; 2/N)... = <b>${(prob(n, N) * 100).toFixed(1)}%</b>.` });
      const n50 = Math.ceil(1.1774 * Math.sqrt(N));
      fr.push({ n: order.length, hit: true, say: `Collision: value number ${hit.b + 1} landed in box ${hit.v}, already taken by value number ${hit.a + 1}. That took ${order.length} values out of ${N} boxes.` });
      fr.push({ n: order.length, hit: true, done: true, say: `The rule: P(collision) &asymp; 1 &minus; e<sup>&minus;n<sup>2</sup>/2N</sup>, which reaches 50% at n &asymp; 1.18 &radic;N = <b>${n50}</b> for N = ${N}. For an n bit hash, N = 2<sup>n</sup>, so collisions appear after about 2<sup>n/2</sup> tries. That is why SHA-256 gives 128 bit collision resistance.` });
      return fr.map(x => ({ ...x, N, order, hit, n50 }));
    },
    paint(z, f) {
      const c = z.col, g = z.g, N = f.N;
      const cols = Math.ceil(Math.sqrt(N * 1.7)), cell = Math.min(12, 290 / cols), rows = Math.ceil(N / cols);
      const filled = new Map(); f.order.slice(0, f.n).forEach((v, i) => filled.set(v, (filled.get(v) || 0) + 1));
      for (let i = 0; i < N; i++) {
        const x = 14 + (i % cols) * cell, y = 30 + Math.floor(i / cols) * cell, k = filled.get(i) || 0;
        g.fillStyle = k > 1 ? c.red : k ? c.cv : 'rgba(100,116,139,0.15)';
        g.fillRect(x, y, cell - 1, cell - 1);
      }
      D.text(g, `${N} boxes, ${f.n} values`, 14, 22, { s: 11, b: true, c: c.ink2 });
      const X0 = 340, Y0 = 200, Wd = 240, Hd = 160, nmax = Math.ceil(3 * Math.sqrt(N));
      g.strokeStyle = c.line; g.lineWidth = 1; g.strokeRect(X0, Y0 - Hd, Wd, Hd);
      g.beginPath(); for (let n = 0; n <= nmax; n++) { const x = X0 + n / nmax * Wd, y = Y0 - prob(n, N) * Hd; if (n) g.lineTo(x, y); else g.moveTo(x, y); }
      g.strokeStyle = c.cv; g.lineWidth = 2; g.stroke();
      D.line(g, X0, Y0 - Hd / 2, X0 + Wd, Y0 - Hd / 2, c.ink2, 1, [4, 3]);
      D.text(g, '50%', X0 - 4, Y0 - Hd / 2 + 4, { a: 'right', s: 10, c: c.ink2 });
      D.text(g, 'P(collision) as values are added', X0, Y0 - Hd - 8, { s: 10, b: true, c: c.ink2 });
      D.text(g, '0', X0, Y0 + 14, { s: 10, c: c.ink2 }); D.text(g, String(nmax), X0 + Wd, Y0 + 14, { a: 'right', s: 10, c: c.ink2 });
      const nx = X0 + Math.min(f.n, nmax) / nmax * Wd;
      D.line(g, nx, Y0, nx, Y0 - Hd, c.orange, 2);
      D.text(g, 'n = ' + f.n, nx + 4, Y0 - 6, { s: 10, b: true, c: c.orange });
      if (f.done) {
        const x50 = X0 + f.n50 / nmax * Wd;
        g.fillStyle = c.green; g.beginPath(); g.arc(x50, Y0 - Hd / 2, 4, 0, 7); g.fill();
        cbox(z, 14, 232, 572, 30, `P ≈ 1 − e^(−n²/2N)   →   50% at n ≈ 1.18 √N = ${f.n50}`, { s: 13, b: true, mono: true, fill: c.bg });
        cbox(z, 14, 270, 572, 30, 'n bit hash: N = 2ⁿ, collisions after ≈ 2^(n/2) tries', { s: 13, b: true, fill: c.cv, c: '#fff' });
      } else if (f.hit) cbox(z, 14, 232, 572, 30, `collision after ${f.n} values`, { s: 13, b: true, fill: c.red, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Cryptography 1.3  HMAC-SHA256 step by step: key padding, inner hash with ipad, outer hash with opad
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D, sha256, utf8 } = CYZ;
  const hx = (a, n) => a.slice(0, n).map(v => v.toString(16).padStart(2, '0')).join('');
  trace('cyhmac', {
    title: 'HMAC: a hash with a key, done twice',
    sub: 'HMAC turns any hash into a message authentication code: only someone with the key can make or check the tag. These are real HMAC-SHA256 values, the same as Python’s hmac module gives.',
    W: 600, H: 340,
    params: [
      { k: 'key', label: 'Secret key', type: 'text', v: 'shared secret' },
      { k: 'msg', label: 'Message', type: 'text', v: 'PAY RIYA 100' }
    ],
    tips: [
      { t: 'Play it. Two hashes: the inner one hashes the message with one key mask, the outer one hashes that result with another.', play: true },
      { t: 'Change 100 to 900. The tag changes completely, and without the key nobody can compute the new one.', set: { msg: 'PAY RIYA 900' }, play: true }
    ],
    frames(p) {
      let key = utf8(String(p.key));
      const msg = utf8(String(p.msg));
      if (!key.length) throw new Error('Type a key.');
      if (key.length > 64) key = sha256(key);
      const K0 = key.concat(new Array(64 - key.length).fill(0));
      const ki = K0.map(v => v ^ 0x36), ko = K0.map(v => v ^ 0x5c);
      const inner = sha256(ki.concat(msg)), tag = sha256(ko.concat(inner));
      const fr = [
        { k: 1, say: `Pad the key with zero bytes to the hash block size, 64 bytes for SHA-256 (a longer key is hashed first). K0 starts ${hx(K0, 8)}...` },
        { k: 2, say: `Inner key: K0 &oplus; ipad, where ipad is the byte 0x36 repeated 64 times. ${hx(K0, 1)} &oplus; 36 = ${hx(ki, 1)}.` },
        { k: 3, say: `Inner hash = SHA-256( (K0 &oplus; ipad) ‖ message ) = <b>${hx(inner, 8)}...</b>` },
        { k: 4, say: `Outer key: K0 &oplus; opad, with opad = 0x5c repeated. ${hx(K0, 1)} &oplus; 5c = ${hx(ko, 1)}.` },
        { k: 5, say: `Tag = SHA-256( (K0 &oplus; opad) ‖ inner hash ) = <b>${hx(tag, 32)}</b>.` },
        { k: 6, done: true, say: 'Why two hashes: the outer hash hides the inner chaining value, so the length extension trick that breaks SHA(key ‖ message) does not work. HMAC is secure if the hash’s compression function behaves like a random function (Bellare, Canetti and Krawczyk, 1996). Always check tags with hmac.compare_digest.' }
      ];
      return fr.map(x => ({ ...x, K0, ki, ko, inner, tag, msgText: String(p.msg) }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const row = (y, label, val, on, col) => { D.text(g, label, 14, y + 18, { s: 11, b: true, c: c.ink2 }); cbox(z, 150, y, 436, 28, val, { s: 12, b: true, mono: true, fill: on ? col : c.surf, c: c.ink }); };
      if (f.k >= 1) row(12, 'K0 (64 bytes)', hx(f.K0, 16) + '...', f.k === 1, 'rgba(234,88,12,0.18)');
      if (f.k >= 2) row(52, 'K0 ⊕ ipad (36)', hx(f.ki, 16) + '...', f.k === 2, 'rgba(234,88,12,0.18)');
      if (f.k >= 3) { row(92, 'inner hash', hx(f.inner, 16) + '...', f.k === 3, 'rgba(15,118,110,0.22)'); D.text(g, `= SHA-256(K0 ⊕ ipad ‖ "${f.msgText.slice(0, 20)}")`, 150, 136, { s: 10, c: c.ink2 }); }
      if (f.k >= 4) row(146, 'K0 ⊕ opad (5c)', hx(f.ko, 16) + '...', f.k === 4, 'rgba(234,88,12,0.18)');
      if (f.k >= 5) { row(186, 'tag', hx(f.tag, 16) + '...', true, 'rgba(15,118,110,0.3)'); D.text(g, '= SHA-256(K0 ⊕ opad ‖ inner hash)', 150, 230, { s: 10, c: c.ink2 }); }
      if (f.k >= 5) cbox(z, 14, 244, 572, 28, 'HMAC(K, m) = H( (K0 ⊕ opad) ‖ H( (K0 ⊕ ipad) ‖ m ) )', { s: 13, b: true, mono: true, fill: c.bg });
      if (f.done) cbox(z, 14, 282, 572, 40, ['full tag', hx(f.tag, 32)], { s: 11, b: true, mono: true, fill: c.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Cryptography 2.1  the extended Euclidean algorithm: gcd, Bezout coefficients and the modular inverse
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const COLS = [['i', 30, 40], ['q', 90, 60], ['r', 165, 80], ['s', 245, 70], ['t', 325, 80], ['check: s·a + t·b', 480, 220]];
  trace('cyeuclid', {
    title: 'The extended Euclidean algorithm',
    sub: 'Euclid’s algorithm finds the greatest common divisor by repeated division. Keeping two extra columns, s and t, also writes the gcd as s·a + t·b, which gives modular inverses, the key step of RSA.',
    W: 600, H: 340,
    params: [
      { k: 'a', label: 'a', type: 'text', v: '3120' },
      { k: 'b', label: 'b', type: 'text', v: '17' }
    ],
    tips: [
      { t: 'Play it with 3120 and 17. The last t is the inverse of 17 modulo 3120, which is the RSA private exponent in the classic textbook example: d = 2753.', play: true },
      { t: 'Try 240 and 46. The gcd is 2, so 46 has no inverse modulo 240.', set: { a: '240', b: '46' }, play: true },
      { t: 'Try two Fibonacci numbers, 144 and 89. They need the most steps for their size (Lamé, 1844).', set: { a: '144', b: '89' }, play: true }
    ],
    frames(p) {
      const a = Math.floor(+p.a), b = Math.floor(+p.b);
      if (!(a > 0 && b > 0) || a > 1e9 || b > 1e9) throw new Error('Type two whole numbers from 1 to 1,000,000,000.');
      const rows = [{ i: 0, q: '', r: a, s: 1, t: 0 }, { i: 1, q: '', r: b, s: 0, t: 1 }];
      while (rows[rows.length - 1].r !== 0) {
        const x = rows[rows.length - 2], y = rows[rows.length - 1], q = Math.floor(x.r / y.r);
        rows.push({ i: rows.length, q, r: x.r - q * y.r, s: x.s - q * y.s, t: x.t - q * y.t });
      }
      const fr = [{ n: 2, say: `Start with two rows: r = a = ${a} written as 1·a + 0·b, and r = b = ${b} written as 0·a + 1·b.` }];
      for (let k = 2; k < rows.length; k++) {
        const x = rows[k - 2], y = rows[k - 1], R = rows[k];
        fr.push({ n: k + 1, say: `q = floor(${x.r} / ${y.r}) = ${R.q}. New row = row ${k - 2} &minus; ${R.q} &times; row ${k - 1}: r = ${x.r} &minus; ${R.q}·${y.r} = <b>${R.r}</b>, s = ${R.s}, t = ${R.t}.${R.r === 0 ? ' The remainder is 0, so we stop.' : ''}` });
      }
      const g = rows[rows.length - 2];
      const inv = g.r === 1 ? ((g.t % a) + a) % a : null;
      fr.push({ n: rows.length, done: true, say: `gcd(${a}, ${b}) = <b>${g.r}</b> = (${g.s})·${a} + (${g.t})·${b}. ${inv !== null ? `Since the gcd is 1, ${b} has an inverse modulo ${a}: t mod ${a} = <b>${inv}</b>, and ${b} &times; ${inv} mod ${a} = 1.` : `The gcd is not 1, so ${b} has no inverse modulo ${a}.`}` });
      return fr.map(x => ({ ...x, rows, a, b, g, inv }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      COLS.forEach(([h, x]) => D.text(g, h, x, 22, { a: 'center', s: 12, b: true, c: c.ink2 }));
      const shown = f.rows.slice(0, f.n), start = Math.max(0, shown.length - 9);
      shown.slice(start).forEach((R, j) => {
        const y = 32 + j * 26, last = R.i === f.n - 1 && !f.done, gcdRow = f.done && R.i === f.g.i;
        const vals = [R.i, R.q, R.r, R.s, R.t, `${R.s}·${f.a} + ${R.t}·${f.b} = ${R.s * f.a + R.t * f.b}`];
        vals.forEach((v, k) => cbox(z, COLS[k][1] - COLS[k][2] / 2, y, COLS[k][2] - 4, 22, String(v), { s: 12, b: true, mono: true, fill: gcdRow ? 'rgba(15,118,110,0.25)' : last ? 'rgba(234,88,12,0.2)' : c.surf }));
      });
      if (f.done) cbox(z, 14, 272, 572, 52, [`gcd = ${f.g.r} = (${f.g.s})·${f.a} + (${f.g.t})·${f.b}`, f.inv !== null ? `inverse of ${f.b} mod ${f.a} = ${f.inv}` : 'no inverse (gcd ≠ 1)'], { s: 13, b: true, mono: true, fill: c.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Cryptography 2.1  square and multiply: b^e mod n with about 2 log2(e) multiplications
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cypowmod', {
    title: 'Fast modular powers: square and multiply',
    sub: 'RSA needs numbers like m^65537 mod n. Multiplying 65,536 times is far too slow. Instead read the exponent in binary: square for every bit, and also multiply when the bit is 1.',
    W: 600, H: 340,
    params: [
      { k: 'b', label: 'Base b', type: 'text', v: '4' },
      { k: 'e', label: 'Exponent e', type: 'text', v: '13' },
      { k: 'n', label: 'Modulus n', type: 'text', v: '497' }
    ],
    tips: [
      { t: 'Play it with 4^13 mod 497. 13 = 1101 in binary. The first bit just sets r = 4, then 3 squarings and 2 multiplications give 445.', play: true },
      { t: 'Try the exponent 65537, the usual RSA public exponent. It is 2^16 + 1, so only 16 squarings and 1 extra multiplication.', set: { e: '65537', b: '7', n: '991' }, play: true }
    ],
    frames(p) {
      const b = Math.floor(+p.b), e = Math.floor(+p.e), n = Math.floor(+p.n);
      if (!(b >= 0 && e >= 1 && n >= 2) || n > 1e6 || e > 1e7) throw new Error('Use b ≥ 0, e from 1 to 10,000,000 and n from 2 to 1,000,000.');
      const bits = e.toString(2), log = [];
      let r = 1, muls = 0;
      const fr = [{ k: -1, r, log: [], say: `Write e = ${e} in binary: <b>${bits}</b>. Start with r = 1 and read the bits from left to right.` }];
      for (let i = 0; i < bits.length; i++) {
        const before = r;
        r = (r * r) % n; if (i) muls++;
        log.push(`bit ${bits[i]}: square  ${before}² mod ${n} = ${r}`);
        let say = `Bit ${i + 1} is ${bits[i]}. Square: r = ${before}² mod ${n} = <b>${r}</b>.`;
        if (bits[i] === '1') { const sq = r; r = (r * (b % n)) % n; if (i) muls++; log.push(`         multiply ${sq}·${b} mod ${n} = ${r}`); say += ` The bit is 1, so multiply by b: r = ${sq} &times; ${b} mod ${n} = <b>${r}</b>.`; }
        fr.push({ k: i, r, log: log.slice(), say });
      }
      fr.push({ k: bits.length, r, log: log.slice(), done: true, muls, say: `${b}<sup>${e}</sup> mod ${n} = <b>${r}</b>, using ${muls} multiplications instead of ${e - 1}. The cost grows with the number of bits, about 2 log<sub>2</sub> e, so even 2048 bit exponents need only a few thousand steps. Taking the remainder after every step keeps the numbers small.` });
      return fr.map(x => ({ ...x, b, e, n, bits }));
    },
    paint(z, f) {
      const c = z.col, g = z.g, L = f.bits.length, w = Math.min(34, 560 / L);
      D.text(g, `e = ${f.e} in binary`, 14, 20, { s: 11, b: true, c: c.ink2 });
      for (let i = 0; i < L; i++) cbox(z, 14 + i * w, 28, w - 3, 30, f.bits[i], { s: 15, b: true, mono: true, fill: i === f.k ? c.orange : i < f.k || f.done ? 'rgba(15,118,110,0.25)' : c.surf, c: i === f.k ? '#fff' : c.ink });
      const lines = f.log.slice(-8);
      lines.forEach((t, i) => D.text(g, t, 18, 86 + i * 20, { s: 12, mono: true, c: c.ink }));
      cbox(z, 420, 76, 166, 60, ['r =', String(f.r)], { s: 18, b: true, mono: true, fill: c.bg });
      if (f.done) {
        cbox(z, 14, 252, 572, 30, `${f.b}^${f.e} mod ${f.n} = ${f.r}`, { s: 15, b: true, mono: true, fill: c.cv, c: '#fff' });
        cbox(z, 14, 290, 572, 30, `${f.muls} multiplications instead of ${(f.e - 1).toLocaleString('en-US')}`, { s: 13, b: true, fill: c.surf });
      }
    }
  });
})();

/* =====================================================================================================
   Cryptography 2.1  the Chinese remainder theorem as a sieve, then the formula that builds the answer
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const gcd = (a, b) => (b ? gcd(b, a % b) : a);
  const inv = (a, m) => { for (let x = 1; x < m; x++) if ((a * x) % m === 1) return x; return 1; };
  trace('cycrt', {
    title: 'The Chinese remainder theorem',
    sub: 'Sun Zi asked, about 1,600 years ago: a number leaves 2 when divided by 3, 3 when divided by 5, and 2 when divided by 7. What is it? Cross out the numbers that fail each condition and one survives.',
    W: 600, H: 340,
    params: [{ k: 'sys', label: 'Conditions (remainder mod modulus)', type: 'text', v: '2 mod 3, 3 mod 5, 2 mod 7' }],
    tips: [
      { t: 'Play Sun Zi’s puzzle. Exactly one number from 0 to 104 survives: 23.', play: true },
      { t: 'Try 1 mod 4, 2 mod 9, 3 mod 5. The moduli share no factor, so there is again exactly one answer below 4 × 9 × 5 = 180.', set: { sys: '1 mod 4, 2 mod 9, 3 mod 5' }, play: true }
    ],
    frames(p) {
      const parts = String(p.sys).split(',').map(s => s.trim().match(/^(\d+)\s*mod\s*(\d+)$/i));
      if (parts.length < 2 || parts.length > 3 || parts.some(m => !m)) throw new Error('Write 2 or 3 conditions like "2 mod 3, 3 mod 5, 2 mod 7".');
      const A = parts.map(m => +m[1]), Mo = parts.map(m => +m[2]);
      for (let i = 0; i < Mo.length; i++) for (let j = i + 1; j < Mo.length; j++) if (gcd(Mo[i], Mo[j]) !== 1) throw new Error(`${Mo[i]} and ${Mo[j]} share a factor. The theorem needs moduli with no common factor.`);
      const M = Mo.reduce((x, y) => x * y, 1);
      if (M > 200 || Mo.some(m => m < 2)) throw new Error('Keep the product of the moduli at 200 or less so the grid fits.');
      const ans = [...Array(M).keys()].find(x => A.every((a, i) => x % Mo[i] === a % Mo[i]));
      const terms = Mo.map((m, i) => { const Mi = M / m, yi = inv(Mi % m, m); return { m, a: A[i] % m, Mi, yi }; });
      const fr = [{ k: 0, say: `Any answer repeats every ${Mo.join(' &times; ')} = <b>${M}</b>, so look at 0 to ${M - 1}.` }];
      Mo.forEach((m, i) => fr.push({ k: i + 1, say: `Keep only numbers with remainder ${A[i] % m} when divided by ${m}. ${i === Mo.length - 1 ? `One number is left: <b>${ans}</b>.` : `Every ${m}th number survives.`}` }));
      fr.push({ k: Mo.length, done: true, say: `The formula builds it directly: for each condition take M<sub>i</sub> = M / m<sub>i</sub> and its inverse y<sub>i</sub> mod m<sub>i</sub>, then x = &Sigma; a<sub>i</sub> M<sub>i</sub> y<sub>i</sub> mod M = ${terms.map(t => `${t.a}·${t.Mi}·${t.yi}`).join(' + ')} mod ${M} = <b>${ans}</b>. RSA uses this to decrypt about 4 times faster.` });
      return fr.map(x => ({ ...x, A, Mo, M, ans, terms }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const cols = f.M <= 105 ? 15 : Math.ceil(f.M / 10), rows = Math.ceil(f.M / cols), w = 572 / cols, h = Math.min(26, 200 / rows);
      for (let x = 0; x < f.M; x++) {
        const alive = f.A.slice(0, f.k).every((a, i) => x % f.Mo[i] === a % f.Mo[i]);
        const win = alive && f.k === f.Mo.length;
        cbox(z, 14 + (x % cols) * w, 14 + Math.floor(x / cols) * h, w - 2, h - 2, String(x), { s: 10, b: alive, mono: true, fill: win ? c.cv : alive ? 'rgba(15,118,110,0.18)' : 'rgba(100,116,139,0.08)', c: win ? '#fff' : alive ? c.ink : 'rgba(100,116,139,0.45)', r: 3 });
      }
      const y0 = 30 + rows * h;
      f.Mo.forEach((m, i) => cbox(z, 14 + i * 150, y0, 140, 26, `x ≡ ${f.A[i] % m} (mod ${m})`, { s: 12, b: true, mono: true, fill: i < f.k ? 'rgba(15,118,110,0.22)' : c.surf }));
      if (f.done) cbox(z, 14, y0 + 36, 572, 30, `x = Σ aᵢ·Mᵢ·yᵢ mod ${f.M} = ${f.ans}`, { s: 14, b: true, mono: true, fill: c.cv, c: '#fff' });
    }
  });
})();
