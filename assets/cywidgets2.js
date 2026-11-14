/* ===== Complete Cybersecurity animations, part 2: Cryptography. Built on MLZ.trace and CYZ (assets/cywidgets.js). ===== */

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
