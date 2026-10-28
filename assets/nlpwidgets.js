/* ===== Natural Language Processing animations, one block per chapter. The framework is assets/cvviz.js.
   Every animation is declared with CVZ.def(name, spec), so every value it uses has a control the reader can change,
   and its "Try this" list suggests which values to change and what to look for. ===== */
const NLZ = (() => {
  const { D } = CVZ;
  const FONT = (o = {}) => `${o.b ? '800 ' : '600 '}${o.s || 13}px ${o.mono ? '"JetBrains Mono", monospace' : 'Nunito, system-ui, sans-serif'}`;
  /* width of a string in the given font */
  function tw(g, s, o = {}) { g.save(); g.font = FONT(o); const w = g.measureText(String(s)).width; g.restore(); return w; }
  /* rounded rectangle */
  function rr(g, x, y, w, h, r, o = {}) {
    g.save(); g.beginPath();
    r = Math.min(r, w / 2, h / 2);
    g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
    if (o.fill) { g.fillStyle = o.fill; g.fill(); }
    if (o.stroke) { g.strokeStyle = o.stroke; g.lineWidth = o.w || 1.5; if (o.dash) g.setLineDash(o.dash); g.stroke(); }
    g.restore();
  }
  /* a word in a rounded box. Returns its width so the next one can be placed after it */
  function pill(g, s, x, y, o = {}) {
    const fs = o.s || 13, pad = o.pad ?? 7, h = o.h || fs + 10;
    const w = tw(g, s, { s: fs, b: o.b, mono: o.mono }) + 2 * pad;
    rr(g, x, y, w, h, o.r ?? 7, { fill: o.fill, stroke: o.stroke, w: o.lw || 1.2, dash: o.dash });
    D.text(g, s, x + w / 2, y + h / 2 + 1, { a: 'center', bl: 'middle', s: fs, b: o.b, mono: o.mono, c: o.c });
    return w;
  }
  /* lay out pills left to right and wrap to a new row when the next one would not fit. Returns the y below the last row */
  function flow(g, items, x, y, maxW, o = {}) {
    const gap = o.gap ?? 6, fs = o.s || 13, h = o.h || fs + 10, rowGap = o.rowGap ?? 8;
    let cx = x, cy = y;
    const pos = [];
    items.forEach((it, i) => {
      const s = typeof it === 'string' ? it : it.t;
      const w = tw(g, s, { s: fs, b: it.b || o.b, mono: o.mono }) + 2 * (o.pad ?? 7);
      if (cx > x && cx + w > x + maxW) { cx = x; cy += h + rowGap; }
      const st = typeof it === 'string' ? {} : it;
      pill(g, s, cx, cy, Object.assign({}, o, st));
      pos.push([cx, cy, w, h]);
      if (o.under && it.u) D.text(g, it.u, cx + w / 2, cy + h + 12, { a: 'center', s: o.us || 10.5, c: it.uc || o.uc, mono: o.umono });
      cx += w + gap;
    });
    return { y: cy + h, pos };
  }
  /* write text that wraps at maxW. Returns the y of the next line */
  function wrap(g, s, x, y, maxW, o = {}) {
    const lh = o.lh || (o.s || 13) + 5;
    const words = String(s).split(/\s+/).filter(Boolean);
    let line = '';
    words.forEach(w => {
      const t = line ? line + ' ' + w : w;
      if (line && tw(g, t, o) > maxW) { D.text(g, line, x, y, o); y += lh; line = w; } else line = t;
    });
    if (line) { D.text(g, line, x, y, o); y += lh; }
    return y;
  }
  /* shrink a font size until the string fits */
  function fit(g, s, maxW, size = 13, o = {}) { let fs = size; while (fs > 8 && tw(g, s, Object.assign({}, o, { s: fs })) > maxW) fs -= 0.5; return fs; }
  const log2 = x => Math.log(x) / Math.LN2;
  const fmt = (v, d = 4) => {
    if (!isFinite(v)) return v > 0 ? '∞' : '−∞';
    if (v !== 0 && Math.abs(v) < 1e-3) return v.toExponential(2).replace('-', '−');
    return (Math.round(v * 10 ** d) / 10 ** d).toString().replace('-', '−');
  };
  /* split text into words and punctuation the simple way */
  const words = s => (String(s).toLowerCase().match(/[a-z0-9']+|[^\sa-z0-9']/g) || []);
  /* parse "word number" lines into [[word, number], ...] */
  function pairs(s) {
    return String(s).split(/\n/).map(l => l.trim()).filter(Boolean).map(l => { const m = l.match(/^(.*?)[\s,:=]+(-?[\d.eE+-]+)\s*$/); return m ? [m[1].trim(), +m[2]] : null; }).filter(Boolean);
  }
  const nums = s => String(s).split(/[\s,]+/).filter(Boolean).map(Number).filter(v => !isNaN(v));
  return { tw, rr, pill, flow, wrap, fit, log2, fmt, words, pairs, nums };
})();

(() => {
  const { def, D, esc } = CVZ;
  const { tw, rr, pill, flow, wrap, fit, log2, fmt } = NLZ;

  /* ---------------------------------------------------------------- Chapter 1.1: what language is */
  const LEVELS = [
    ['Pragmatics', 'Meaning in context', 'What does the speaker intend here and now?'],
    ['Semantics', 'Literal meaning', 'What does the sentence mean on its own?'],
    ['Syntax', 'Phrases and sentences', 'How do words combine into sentences?'],
    ['Morphology', 'Words and word parts', 'How are words built from smaller meaningful parts?'],
    ['Phonology', 'Sound system (phonemes)', 'Which sound differences change meaning in this language?'],
    ['Phonetics', 'Raw speech sounds', 'How are sounds made, carried and heard?']
  ];
  const LEVEL_EX = [
    ['pb', 'In English, /p/ and /b/ make "pat" and "bat" different words.', 'Phonology', 'A swap of one sound changes the word, so these two sounds are different phonemes in English. That is a fact about the sound system of one language.'],
    ['k', 'The sound [k] is made by stopping air with the back of the tongue, with no voice.', 'Phonetics', 'This describes how a sound is physically produced. It is true in every language that uses the sound.'],
    ['un', '"unhappiness" splits into un + happy + ness.', 'Morphology', 'The word is built from three meaningful parts: a prefix, a root and a suffix.'],
    ['dis', '"distaste" is dis + taste, and dis- means the opposite.', 'Morphology', 'dis- is a bound morpheme. It cannot stand alone but adds meaning to the root.'],
    ['green', '"Colourless green ideas sleep furiously" is well formed but makes no sense.', 'Syntax', 'The word order and the grammar are fine, which is a syntax judgement. The oddness is semantic, which is why Chomsky used it to show the two levels are separate.'],
    ['order', '"The dog bit the man" and "The man bit the dog" use the same words.', 'Syntax', 'Only the order of the words changes, and with it who did what to whom.'],
    ['cat', '"The cat jumped" describes a jumping event done by a cat.', 'Semantics', 'This is the literal meaning, true or false in the world, with no speaker intention involved.'],
    ['cold', 'Saying "It is cold in here" next to an open window, meaning "please close it".', 'Pragmatics', 'The literal meaning is a statement about temperature. The intended meaning is a request, and only the situation tells you that.'],
    ['bank', '"I sat near a bank" read as a river bank because the talk was about fishing.', 'Pragmatics', 'The word alone is ambiguous. The earlier conversation, the shared knowledge and the setting pick the sense.'],
    ['hindi', 'Hindi speakers start with "Bharat" when the topic so far was India.', 'Pragmatics', 'Both word orders mean the same thing. Which one sounds natural depends on what was said before, which is information structure in discourse.']
  ];
  def('levels', {
    title: 'The six levels of language',
    sub: 'Pick an observation, guess its level, then reveal the answer. The level used is lit up in the stack.',
    W: 560, H: 300,
    params: [
      { k: 'ex', label: 'Observation', type: 'select', v: 'pb', opts: LEVEL_EX.map(e => [e[0], e[1].length > 60 ? e[1].slice(0, 58) + '…' : e[1]]) },
      { k: 'guess', label: 'Your guess', type: 'select', v: 'none', opts: [['none', 'No guess yet']].concat(LEVELS.map(l => [l[0], l[0]])) },
      { k: 'show', label: 'Reveal the answer', type: 'check', v: false }
    ],
    tips: [
      { t: 'Pick the "colourless green ideas" sentence. It is a classic trap: the grammar is fine, so the problem is not syntax.', set: { ex: 'green', guess: 'none', show: false } },
      { t: 'Compare "It is cold in here" with "The cat jumped". One needs the situation, one does not.', set: { ex: 'cold', show: true } },
      { t: 'Pick the [k] sound and then the /p/ and /b/ pair. Physical sound is phonetics, the meaning-changing contrast is phonology.', set: { ex: 'k', show: true } }
    ],
    draw(z) {
      const { g, p } = z;
      const ex = LEVEL_EX.find(e => e[0] === p.ex) || LEVEL_EX[0];
      const ans = ex[2], shown = p.show;
      const X = 16, Y = 14, Wd = 250, H = 40, gap = 6;
      LEVELS.forEach((l, i) => {
        const y = Y + i * (H + gap);
        const isAns = shown && l[0] === ans, isGuess = p.guess === l[0];
        const fill = isAns ? z.col.cv : isGuess ? z.col.hl || z.col.bg : z.col.bg;
        rr(g, X + i * 4, y, Wd - i * 8, H, 8, { fill, stroke: isGuess ? z.col.orange : z.col.line, w: isGuess ? 2.5 : 1 });
        D.text(g, l[0], X + i * 4 + 12, y + 17, { b: true, s: 13.5, c: isAns ? '#fff' : z.col.ink });
        D.text(g, l[1], X + i * 4 + 12, y + 33, { s: 11.5, c: isAns ? '#fff' : z.col.ink2 });
      });
      D.text(g, 'meaning', X + Wd + 26, Y + 10, { a: 'center', s: 11, c: z.col.ink2 });
      D.arrow(g, X + Wd + 26, Y + 6 * (H + gap) - 18, X + Wd + 26, Y + 18, z.col.ink2, 1.5);
      D.text(g, 'sound', X + Wd + 26, Y + 6 * (H + gap) - 4, { a: 'center', s: 11, c: z.col.ink2 });
      const RX = 330, RW = 220;
      D.text(g, 'Observation', RX, 30, { b: true, s: 13, c: z.col.ink });
      let y = wrap(g, ex[1], RX, 52, RW, { s: 12.5, c: z.col.ink2 });
      y += 8;
      if (p.guess !== 'none') {
        const ok = p.guess === ans;
        D.text(g, `Your guess: ${p.guess}`, RX, y, { b: true, s: 12.5, c: shown ? (ok ? z.col.green : z.col.red) : z.col.orange });
        y += 20;
      }
      if (shown) {
        D.text(g, `Answer: ${ans}`, RX, y, { b: true, s: 13, c: z.col.cv }); y += 20;
        const L = LEVELS.find(l => l[0] === ans);
        y = wrap(g, `Question it answers: ${L[2]}`, RX, y, RW, { s: 12, c: z.col.ink2 });
      } else D.text(g, 'Tick "Reveal the answer" to check.', RX, y, { s: 12, c: z.col.ink2 });
      return shown ? `<b>${esc(ans)}.</b> ${esc(ex[3])}` : 'Each level combines the units of the level below it: sounds make words, words make sentences, sentences carry meaning, and context decides what the speaker meant.';
    }
  });

  const TRI = {
    cat: { sym: 'cat  [kæt]', con: 'small, furry, four legged pet', ref: 'a real cat', real: true, note: 'The sound or the letters never touch the animal. They call up a concept in your mind, and the concept points at cats in the world.' },
    dollar: { sym: '$', con: 'money, US currency', ref: 'actual dollar notes', real: true, note: 'Nothing about the shape $ looks like money. A community agreed to pair this form with this meaning. That agreement is a convention.' },
    pear: { sym: 'pear  [pɛə]', con: 'sweet green or yellow fruit', ref: 'a real pear', real: true, note: 'Sight, touch, smell and taste are combined into one concept. The same sounds also form "peer", a homophone, so context must choose.' },
    unicorn: { sym: 'unicorn', con: 'horse + single horn + white', ref: 'nothing in the real world', real: false, note: 'The word still means something. Its concept is built from parts that do have referents. Frege called this having a sense without a reference.' },
    justice: { sym: 'justice', con: 'fairness, what people deserve', ref: 'no physical object', real: false, note: 'An abstract reality. People use other symbols for it, such as scales, the same way the class named a flag or a white bird for freedom and peace.' }
  };
  def('triangle', {
    title: 'The semiotic triangle: word, concept and thing',
    sub: 'Pick a word. Play the steps to follow the lecture pipeline from the world to the spoken form.',
    W: 560, H: 300,
    params: [
      { k: 'w', label: 'Word', type: 'select', v: 'cat', opts: [['cat', 'cat'], ['dollar', 'the $ sign'], ['pear', 'pear'], ['unicorn', 'unicorn (no referent)'], ['justice', 'justice (abstract)']] },
      { k: 'pipe', label: 'Show the pipeline steps', type: 'check', v: true }
    ],
    tips: [
      { t: 'Pick unicorn. The bottom corner is empty, yet the word works. Meaning comes from the concept, not from the thing.', set: { w: 'unicorn' } },
      { t: 'Pick the $ sign and play. The dashed bottom edge is the lecture point: a symbol is linked to the world only through a mind.', set: { w: 'dollar' }, play: true }
    ],
    steps: () => 5,
    draw(z) {
      const { g, p } = z;
      const t = TRI[p.w] || TRI.cat;
      const A = [160, 40], B = [78, 220], C = [242, 220];
      const st = p.pipe ? z.step : 5;
      D.line(g, A[0], A[1], B[0], B[1], z.col.cv, 2.5);
      D.line(g, A[0], A[1], C[0], C[1], z.col.cv, 2.5);
      D.line(g, B[0], B[1], C[0], C[1], z.col.ink2, 1.5, [6, 5]);
      D.text(g, 'no direct link', 160, 262, { a: 'center', s: 11, c: z.col.ink2 });
      const node = (pt, head, body, on) => {
        const w = Math.max(tw(g, head, { b: true, s: 12 }), tw(g, body, { s: 11.5 })) + 18;
        const ww = Math.min(w, 170);
        rr(g, pt[0] - ww / 2, pt[1] - 22, ww, 44, 8, { fill: on ? z.col.cv : z.col.surf, stroke: z.col.cv });
        D.text(g, head, pt[0], pt[1] - 6, { a: 'center', b: true, s: 12, c: on ? '#fff' : z.col.ink });
        D.text(g, body, pt[0], pt[1] + 12, { a: 'center', s: fit(g, body, ww - 10, 11.5), c: on ? '#fff' : z.col.ink2 });
      };
      node(A, 'Concept (thought)', t.con, st >= 2 && st <= 4);
      node(B, 'Symbol (form)', t.sym, st >= 5);
      node(C, 'Referent (thing)', t.ref, st >= 0 && st <= 1);
      D.text(g, 'mind', A[0] + 60, A[1] + 50, { s: 11, c: z.col.ink2 });
      const stages = ['World out there', 'Percept (senses)', 'Concept', 'Linguistic meaning', 'Form (sound or letters)'];
      const X = 330;
      D.text(g, 'Lecture pipeline', X, 30, { b: true, s: 13, c: z.col.ink });
      stages.forEach((s, i) => {
        const y = 50 + i * 42, on = i < st;
        const ghost = !t.real && i < 2;
        rr(g, X, y, 200, 30, 8, { fill: on ? (ghost ? z.col.bg : z.col.cv) : z.col.bg, stroke: z.col.line, dash: ghost ? [4, 4] : null });
        D.text(g, ghost ? s + ' (none)' : s, X + 100, y + 19, { a: 'center', s: 12, b: on, c: on && !ghost ? '#fff' : z.col.ink2 });
        if (i < 4) D.arrow(g, X + 100, y + 30, X + 100, y + 42, z.col.ink2, 1.5, 6);
      });
      return `${esc(t.note)}`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 1.2: ambiguity */
  def('ppattach', {
    title: 'One sentence, two trees: prepositional phrase attachment',
    sub: 'The phrase at the end can hang from the verb (how the action was done) or from the object noun (which one).',
    W: 560, H: 300,
    params: [
      { k: 'subj', label: 'Subject', type: 'text', v: 'John' },
      { k: 'verb', label: 'Verb', type: 'text', v: 'saw' },
      { k: 'obj', label: 'Object', type: 'text', v: 'Mary' },
      { k: 'pp', label: 'Prepositional phrase', type: 'text', v: 'with a telescope' },
      { k: 'att', label: 'Attach the phrase to', type: 'select', v: 'vp', opts: [['vp', 'the verb phrase (high)'], ['np', 'the object noun phrase (low)']] },
      { k: 'cv', label: 'Corpus count: verb + preposition', type: 'range', min: 0, max: 100, v: 60, help: 'How often this verb was seen with this preposition attached to it.' },
      { k: 'cn', label: 'Corpus count: noun + preposition', type: 'range', min: 0, max: 100, v: 25, help: 'How often this noun was seen with this preposition attached to it.' }
    ],
    tips: [
      { t: 'Switch the attachment back and forth. The words never change, only the tree, and with it the meaning.', set: { att: 'np' } },
      { t: 'Change the object to "the man" and the phrase to "with a hat". Now the noun count should win. Set it to 80 and the verb count to 5.', set: { obj: 'the man', pp: 'with a hat', cn: 80, cv: 5, att: 'np' } },
      { t: 'Try "ate pizza with a fork" against "ate pizza with olives". Same structure, different winner, decided by world knowledge.', set: { verb: 'ate', obj: 'pizza', pp: 'with a fork', cv: 70, cn: 10, att: 'vp' } }
    ],
    draw(z) {
      const { g, p } = z;
      const ppw = p.pp.trim().split(/\s+/);
      const prep = ppw[0] || 'with', rest = ppw.slice(1).join(' ') || '…';
      const node = (x, y, s, o = {}) => { const w = tw(g, s, { b: true, s: 12 }) + 14; rr(g, x - w / 2, y - 11, w, 22, 6, { fill: o.fill || z.col.bg, stroke: o.stroke || z.col.line }); D.text(g, s, x, y + 1, { a: 'center', bl: 'middle', b: true, s: 12, c: o.c || z.col.ink }); };
      const leaf = (x, y, s) => D.text(g, s, x, y, { a: 'center', s: fit(g, s, 110, 12.5), c: z.col.cv, b: true });
      const e = (x1, y1, x2, y2, hot) => D.line(g, x1, y1 + 11, x2, y2 - 11, hot ? z.col.orange : z.col.ink2, hot ? 2.5 : 1.3);
      const hi = { fill: z.col.orange, stroke: z.col.orange, c: '#fff' };
      // S -> NP VP
      node(280, 22, 'S'); e(280, 22, 70, 70); e(280, 22, 320, 70);
      node(70, 70, 'NP'); e(70, 70, 70, 250); leaf(70, 270, p.subj);
      node(320, 70, 'VP');
      if (p.att === 'vp') {
        e(320, 70, 170, 120); e(320, 70, 280, 120); e(320, 70, 440, 120, true);
        node(170, 120, 'V'); e(170, 120, 170, 250); leaf(170, 270, p.verb);
        node(280, 120, 'NP'); e(280, 120, 280, 250); leaf(280, 270, p.obj);
        node(440, 120, 'PP', hi); e(440, 120, 400, 180); e(440, 120, 490, 180);
        node(400, 180, 'P'); e(400, 180, 400, 250); leaf(400, 270, prep);
        node(490, 180, 'NP'); e(490, 180, 490, 250); leaf(490, 270, rest);
      } else {
        e(320, 70, 170, 120); e(320, 70, 380, 120);
        node(170, 120, 'V'); e(170, 120, 170, 250); leaf(170, 270, p.verb);
        node(380, 120, 'NP'); e(380, 120, 290, 180); e(380, 120, 450, 180, true);
        node(290, 180, 'NP'); e(290, 180, 290, 250); leaf(290, 270, p.obj);
        node(450, 180, 'PP', hi); e(450, 180, 410, 222); e(450, 180, 500, 222);
        node(410, 222, 'P'); leaf(410, 270, prep);
        node(500, 222, 'NP'); leaf(500, 270, rest);
      }
      const tot = p.cv + p.cn;
      const pv = tot ? p.cv / tot : 0.5;
      const win = pv >= 0.5 ? 'vp' : 'np';
      const meaning = p.att === 'vp'
        ? `${esc(p.subj)} ${esc(p.verb)} ${esc(p.obj)}, and "${esc(p.pp)}" tells how ${esc(p.subj)} did it.`
        : `${esc(p.subj)} ${esc(p.verb)} ${esc(p.obj)}, and it is ${esc(p.obj)} that is "${esc(p.pp)}".`;
      return `<b>Reading:</b> ${meaning}<br>A simple statistical parser compares counts: P(verb attachment) = ${p.cv} ÷ (${p.cv} + ${p.cn}) = <b>${fmt(pv, 3)}</b>, so it would choose the <b>${win === 'vp' ? 'verb' : 'noun'}</b> attachment${win === p.att ? ', the tree shown' : ', not the tree shown'}. Grammar allows both trees. Only data or world knowledge picks one.`;
    }
  });

  const SENSES = {
    bank: [['financial institution', 'money deposit loan account cash cheque interest manager branch withdraw savings credit sbi'],
      ['river bank', 'river water stream fishing grass shore edge boat flowed slope sat flood fish']],
    bat: [['flying mammal', 'night cave wings flew animal fly mammal dark fruit blind'],
      ['cricket or baseball bat', 'ball hit cricket player swing wooden batsman game sixes runs']],
    mother: [['female parent', 'child son daughter family love parent birth home care her'],
      ['vinegar starter (old sense)', 'vinegar cask vat ferment barrel bacteria cider wine slime acid']],
    over: [['above and across', 'jumped wall fence across above flew landed side cleared hill'],
      ['finished', 'meeting match game ended finished done end class time']]
  };
  def('sensepick', {
    title: 'Word sense disambiguation by counting shared words',
    sub: 'A simplified Lesk method: each sense has a gloss, and the sense whose gloss shares the most words with the sentence wins.',
    W: 560, H: 250,
    params: [
      { k: 'word', label: 'Ambiguous word', type: 'select', v: 'bank', opts: [['bank', 'bank'], ['bat', 'bat'], ['mother', 'mother'], ['over', 'over']] },
      { k: 'sent', label: 'Sentence', type: 'text', v: 'I sat near the bank and watched the river water flow' },
      { k: 'stop', label: 'Ignore small common words (the, a, and)', type: 'check', v: true }
    ],
    tips: [
      { t: 'Change "river water" to "my savings account". The winner flips to the money sense.', set: { word: 'bank', sent: 'I went to the bank to check my savings account' } },
      { t: 'Try "the bat flew out of the cave at night". Then "he hit the ball with his bat".', set: { word: 'bat', sent: 'the bat flew out of the cave at night' } },
      { t: 'Type "I sat near a bank" with no clues. Both senses score 0, so the method has to guess, exactly as the lecture says context is needed.', set: { word: 'bank', sent: 'I sat near a bank' } }
    ],
    draw(z) {
      const { g, p } = z;
      const STOP = new Set('the a an and of to in on at i my his her he she it was is with near by for from out we you they'.split(' '));
      let ws = NLZ.words(p.sent).filter(w => /[a-z0-9]/.test(w) && w !== p.word);
      if (p.stop) ws = ws.filter(w => !STOP.has(w));
      const senses = SENSES[p.word] || SENSES.bank;
      const scored = senses.map(([name, gloss]) => { const G = new Set(gloss.split(' ')); const hits = [...new Set(ws.filter(w => G.has(w)))]; return { name, gloss, hits }; });
      const best = Math.max(...scored.map(s => s.hits.length));
      const winners = scored.filter(s => s.hits.length === best);
      D.text(g, 'Sentence words compared', 16, 24, { b: true, s: 13, c: z.col.ink });
      const allHits = new Set(scored.flatMap(s => s.hits));
      const r = flow(g, ws.length ? ws.map(w => ({ t: w, fill: allHits.has(w) ? z.col.cv : z.col.bg, c: allHits.has(w) ? '#fff' : z.col.ink2 })) : [{ t: '(no content words)' }], 16, 34, 528, { s: 12, stroke: z.col.line });
      let y = r.y + 22;
      scored.forEach((s, i) => {
        const win = best > 0 && winners.length === 1 && winners[0] === s;
        D.text(g, `Sense ${i + 1}: ${s.name}`, 16, y, { b: true, s: 13, c: win ? z.col.green : z.col.ink });
        D.text(g, `shared words: ${s.hits.length}`, 544, y, { a: 'right', b: true, s: 12.5, c: win ? z.col.green : z.col.ink2 });
        const bw = Math.min(528, s.hits.length * 80);
        rr(g, 16, y + 6, Math.max(4, bw), 12, 4, { fill: win ? z.col.green : z.col.line });
        y = wrap(g, 'gloss: ' + s.gloss, 16, y + 34, 528, { s: 11.5, c: z.col.ink2 }) + 10;
      });
      const verdict = best === 0 ? 'No gloss word appears, so the method cannot decide and falls back to the most common sense.'
        : winners.length > 1 ? 'A tie. The method needs more context.' : `Chosen sense: <b>${esc(winners[0].name)}</b>, with ${best} shared word${best > 1 ? 's' : ''} (${winners[0].hits.map(esc).join(', ')}).`;
      return `${verdict} This is Firth's idea in its simplest form: a word is known by the company it keeps. Real systems use full dictionary glosses or context vectors from a neural model.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 1.3: can machines understand */
  const ELIZA_RULES = `.* all alike => IN WHAT WAY?
.*\\balways\\b.* => CAN YOU THINK OF A SPECIFIC EXAMPLE?
.*\\bi'?m (depressed|sad|unhappy).* => I'M SORRY TO HEAR THAT YOU ARE $1
.*\\bi am (.*) => HOW LONG HAVE YOU BEEN $1?
.*\\bmy (.*) => YOUR $1
.*\\bmother\\b.* => TELL ME MORE ABOUT YOUR FAMILY
.* => PLEASE GO ON`;
  def('eliza', {
    title: 'ELIZA: keyword patterns and templates',
    sub: 'Type a line. The first rule whose pattern matches is used, the pronouns are swapped and the words are pasted into a template.',
    W: 560, H: 270,
    params: [
      { k: 'inp', label: 'You say', type: 'text', v: 'Well, my boyfriend made me come here' },
      { k: 'rules', label: 'Rules, one per line: pattern => reply ($1 is the captured text)', type: 'area', v: ELIZA_RULES },
      { k: 'swap', label: 'Swap pronouns (me → you, my → your)', type: 'check', v: true }
    ],
    tips: [
      { t: 'Type "Men are all alike", the first line of the lecture dialogue.', set: { inp: 'Men are all alike' } },
      { t: 'Type "He says I\'m depressed much of the time". The reply copies your own word back.', set: { inp: "He says I'm depressed much of the time" } },
      { t: 'Type "My dog died yesterday". ELIZA answers YOUR DOG DIED YESTERDAY with no idea what death is. Fluent is not the same as understanding.', set: { inp: 'My dog died yesterday' } },
      { t: 'Turn off the pronoun swap and see how quickly the illusion breaks.', set: { swap: false, inp: 'Well, my boyfriend made me come here' } }
    ],
    draw(z) {
      const { g, p } = z;
      const SW = { i: 'you', me: 'you', my: 'your', am: 'are', "i'm": "you're", you: 'I', your: 'my', mine: 'yours', myself: 'yourself' };
      const clean = String(p.inp).trim().replace(/[.!?]+$/, '');
      const low = clean.toLowerCase();
      const rules = String(p.rules).split('\n').map(l => l.split('=>')).filter(a => a.length === 2).map(([a, b]) => [a.trim(), b.trim()]);
      let hit = -1, out = 'PLEASE GO ON', cap = '';
      for (let i = 0; i < rules.length; i++) {
        let re;
        try { re = new RegExp('^' + rules[i][0] + '$', 'i'); } catch (e) { continue; }
        const m = low.match(re);
        if (m) {
          hit = i; cap = m[1] || '';
          const sw = p.swap ? cap.split(/\s+/).map(w => SW[w] || w).join(' ') : cap;
          out = rules[i][1].replace('$1', sw).toUpperCase();
          break;
        }
      }
      const boxes = [['You say', clean || '(nothing)'], ['Rule that matched', hit >= 0 ? rules[hit][0] : 'none'], ['Captured text', cap || '(none)'], ['ELIZA replies', out]];
      boxes.forEach((b, i) => {
        const y = 14 + i * 62;
        rr(g, 16, y, 528, 48, 9, { fill: i === 3 ? z.col.cv : z.col.bg, stroke: z.col.line });
        D.text(g, b[0], 28, y + 18, { b: true, s: 11.5, c: i === 3 ? '#fff' : z.col.ink2 });
        D.text(g, b[1], 28, y + 37, { s: fit(g, b[1], 500, 13, { mono: i === 1 }), mono: i === 1, b: i === 3, c: i === 3 ? '#fff' : z.col.ink });
        if (i < 3) D.arrow(g, 280, y + 48, 280, y + 62, z.col.ink2, 1.5, 6);
      });
      return `Rule ${hit + 1} of ${rules.length} fired. No meaning is represented anywhere, only string matching. The lecture lesson: <b>producing an appropriate looking response is not the same as understanding</b>.`;
    }
  });

  /* SHRDLU style blocks world: the words must be grounded in objects before the arm can act */
  const WORLD = [
    { id: 1, kind: 'block', size: 'big', colour: 'red', x: 40, w: 70, h: 70 },
    { id: 2, kind: 'block', size: 'small', colour: 'red', x: 125, w: 40, h: 40 },
    { id: 3, kind: 'pyramid', size: 'small', colour: 'green', x: 180, w: 50, h: 50 },
    { id: 4, kind: 'block', size: 'big', colour: 'green', x: 245, w: 60, h: 80 },
    { id: 5, kind: 'pyramid', size: 'big', colour: 'blue', x: 320, w: 64, h: 64 },
    { id: 6, kind: 'box', size: 'big', colour: 'blue', x: 400, w: 120, h: 60 }
  ];
  def('blocks', {
    title: 'A tiny SHRDLU: words grounded in a world',
    sub: 'Give a command. The system must find exactly one object that fits every word before it acts and says OK.',
    W: 560, H: 280,
    params: [
      { k: 'cmd', label: 'Command', type: 'text', v: 'Pick up a big red block' }
    ],
    tips: [
      { t: 'Type "Grasp the pyramid". There are two pyramids, so a grounded system asks which one instead of guessing.', set: { cmd: 'Grasp the pyramid' } },
      { t: 'Type "Grasp the blue pyramid". Adding one word removes the ambiguity.', set: { cmd: 'Grasp the blue pyramid' } },
      { t: 'Type "Pick up a purple block". Nothing in the world fits, so the honest answer is that it cannot see one.', set: { cmd: 'Pick up a purple block' } },
      { t: 'Type "Pick up the box". In this little world the box is a container the arm cannot lift, so the honest reply is I CAN\'T, like the SHRDLU reply to "Stack up two pyramids".', set: { cmd: 'Pick up the box' } }
    ],
    draw(z) {
      const { g, p } = z;
      const w = NLZ.words(p.cmd);
      const kinds = ['block', 'pyramid', 'box'], sizes = ['big', 'small', 'large', 'little'], cols = ['red', 'green', 'blue', 'purple', 'yellow', 'white'];
      const kind = kinds.find(k => w.includes(k) || w.includes(k + 's'));
      const size = sizes.find(s => w.includes(s));
      const sz = size === 'large' ? 'big' : size === 'little' ? 'small' : size;
      const col = cols.find(c => w.includes(c));
      const def_ = w.includes('the');
      const act = /pick|grasp|lift|take|hold/.test(w.join(' '));
      const fits = WORLD.filter(o => (!kind || o.kind === kind) && (!sz || o.size === sz) && (!col || o.colour === col));
      let reply, chosen = null;
      if (!kind) reply = "I DON'T KNOW WHICH KIND OF OBJECT YOU MEAN.";
      else if (!fits.length) reply = `I DON'T SEE ANY ${[sz, col, kind].filter(Boolean).join(' ').toUpperCase()}.`;
      else if (fits.length > 1 && def_) reply = `I DON'T UNDERSTAND WHICH ${kind.toUpperCase()} YOU MEAN.`;
      else { chosen = fits[0]; reply = chosen.kind === 'box' && act ? "I CAN'T. THE BOX HOLDS OTHER THINGS." : act ? 'OK.' : 'I FOUND IT.'; }
      const lift = chosen && act && chosen.kind !== 'box';
      const base = 210;
      D.line(g, 20, base, 540, base, z.col.ink2, 2);
      const C = { red: '#dc2626', green: '#16a34a', blue: '#2563eb' };
      WORLD.forEach(o => {
        const up = lift && o === chosen ? 70 : 0;
        const y = base - o.h - up;
        const hot = fits.includes(o);
        if (o.kind === 'block') D.rect(g, o.x, y, o.w, o.h, { fill: C[o.colour], stroke: hot ? z.col.orange : null, w: 3 });
        else if (o.kind === 'pyramid') { g.save(); g.beginPath(); g.moveTo(o.x, y + o.h); g.lineTo(o.x + o.w / 2, y); g.lineTo(o.x + o.w, y + o.h); g.closePath(); g.fillStyle = C[o.colour]; g.fill(); if (hot) { g.strokeStyle = z.col.orange; g.lineWidth = 3; g.stroke(); } g.restore(); }
        else { D.rect(g, o.x, y, o.w, o.h, { stroke: C[o.colour], w: 4 }); if (hot) D.rect(g, o.x - 3, y - 3, o.w + 6, o.h + 6, { stroke: z.col.orange, w: 2, dash: [4, 3] }); }
        D.text(g, `${o.size} ${o.colour}`, o.x + o.w / 2, base + 13, { a: 'center', s: 10, c: z.col.ink2 });
        D.text(g, o.kind, o.x + o.w / 2, base + 24, { a: 'center', s: 10, c: z.col.ink2 });
      });
      const ax = lift ? chosen.x + chosen.w / 2 : 470;
      const ay = lift ? base - chosen.h - 70 : 20;
      D.line(g, ax, 0, ax, ay, z.col.ink2, 3);
      D.rect(g, ax - 14, ay - 2, 28, 6, { fill: z.col.ink2 });
      rr(g, 16, 240, 528, 32, 8, { fill: z.col.cv });
      D.text(g, reply, 30, 261, { b: true, s: 13, c: '#fff', mono: true });
      return `Words found: kind <b>${kind || '?'}</b>, size <b>${sz || 'any'}</b>, colour <b>${col || 'any'}</b>, article <b>${def_ ? 'the (exactly one expected)' : 'a (any one will do)'}</b>. Objects that fit: <b>${fits.length}</b> (outlined). Unlike ELIZA, every word is checked against a model of the world, and the reply reports what really happened.`;
    }
  });

  def('surprisal', {
    title: 'Surprisal: rare words carry more information',
    sub: 'Edit the possible next words and their probabilities. Surprisal is −log₂ of the probability, measured in bits.',
    W: 560, H: 230,
    params: [
      { k: 'ctx', label: 'Context', type: 'text', v: 'apples and ___' },
      { k: 'list', label: 'Next word and its probability, one per line', type: 'area', v: 'oranges 0.5\nbananas 0.2\npears 0.15\ngrapes 0.1\ncoconut 0.05' }
    ],
    tips: [
      { t: 'Make "oranges" 0.9 and the others tiny. The expected word now costs almost no bits, and coconut costs many.', set: { list: 'oranges 0.9\nbananas 0.04\npears 0.03\ngrapes 0.02\ncoconut 0.01' } },
      { t: 'Make all five equal at 0.2. Every word carries the same log₂ 5 = 2.32 bits, the most uncertain case.', set: { list: 'oranges 0.2\nbananas 0.2\npears 0.2\ngrapes 0.2\ncoconut 0.2' } }
    ],
    draw(z) {
      const { g, p } = z;
      const rows = NLZ.pairs(p.list).filter(r => r[1] > 0).slice(0, 8);
      if (!rows.length) return 'Write lines like "oranges 0.5".';
      const tot = rows.reduce((a, r) => a + r[1], 0);
      const P = rows.map(r => r[1] / tot);
      const S = P.map(q => -log2(q));
      const mx = Math.max(...S, 1);
      D.text(g, `Context: ${p.ctx}`, 16, 22, { b: true, s: 13, c: z.col.ink });
      D.text(g, 'probability', 210, 46, { a: 'center', s: 11.5, b: true, c: z.col.ink2 });
      D.text(g, 'surprisal in bits', 430, 46, { a: 'center', s: 11.5, b: true, c: z.col.ink2 });
      const rh = Math.min(26, 200 / rows.length);
      rows.forEach((r, i) => {
        const y = 58 + i * rh;
        D.text(g, r[0], 110, y + rh * 0.65, { a: 'right', s: fit(g, r[0], 95, 12.5), c: z.col.ink });
        rr(g, 120, y + 3, Math.max(2, P[i] * 180), rh - 8, 4, { fill: z.col.cv });
        D.text(g, fmt(P[i], 3), 126 + P[i] * 180, y + rh * 0.65, { s: 11, c: z.col.ink2 });
        rr(g, 340, y + 3, Math.max(2, S[i] / mx * 170), rh - 8, 4, { fill: z.col.orange });
        D.text(g, fmt(S[i], 2), 346 + S[i] / mx * 170, y + rh * 0.65, { s: 11, c: z.col.ink2 });
      });
      const H = P.reduce((a, q, i) => a + q * S[i], 0);
      return `Average surprisal (the entropy) = Σ p × (−log₂ p) = <b>${fmt(H, 3)} bits</b>. ${Math.abs(tot - 1) > 1e-6 ? `Your numbers added to ${fmt(tot, 3)}, so they were rescaled to add to 1.` : ''} People read high surprisal words more slowly, which is why surprisal is used as a cognitive check on language models.`;
    }
  });

  def('bleu', {
    title: 'BLEU: scoring a translation by n-gram overlap',
    sub: 'Edit the machine output and the human reference. BLEU multiplies a brevity penalty by the geometric mean of the clipped n-gram precisions.',
    W: 560, H: 280,
    params: [
      { k: 'cand', label: 'Machine output (candidate)', type: 'text', v: 'the cat is on the mat' },
      { k: 'refs', label: 'Human references, one per line', type: 'area', v: 'there is a cat on the mat\nthe cat sat on the mat' },
      { k: 'N', label: 'Largest n-gram size N', type: 'range', min: 1, max: 4, v: 4 },
      { k: 'smooth', label: 'Smoothing: add 1 to matches and totals for n of 2 and up (Lin and Och, NLTK method2)', type: 'check', v: true }
    ],
    tips: [
      { t: 'Type "the the the the the the" as the output. Plain precision would be perfect, but clipping caps "the" at 2.', set: { cand: 'the the the the the the', N: 1 } },
      { t: 'Shorten the output to "the cat". Precision stays high but the brevity penalty crushes the score.', set: { cand: 'the cat', N: 2 } },
      { t: 'Write a correct paraphrase such as "a cat is sitting on the rug". The meaning is right yet the score is low, the main weakness of BLEU.', set: { cand: 'a cat is sitting on the rug', N: 4 } }
    ],
    draw(z) {
      const { g, p } = z;
      const tok = s => String(s).toLowerCase().split(/\s+/).filter(Boolean);
      const c = tok(p.cand), refs = String(p.refs).split('\n').map(tok).filter(r => r.length);
      if (!c.length || !refs.length) return 'Write a candidate and at least one reference.';
      const grams = (t, n) => { const m = new Map(); for (let i = 0; i + n <= t.length; i++) { const k = t.slice(i, i + n).join(' '); m.set(k, (m.get(k) || 0) + 1); } return m; };
      const P = [];
      for (let n = 1; n <= p.N; n++) {
        const cg = grams(c, n);
        let match = 0, total = 0;
        cg.forEach((cnt, k) => { const mx = Math.max(0, ...refs.map(r => grams(r, n).get(k) || 0)); match += Math.min(cnt, mx); total += cnt; });
        P.push({ n, match, total, p: p.smooth && n > 1 ? (match + 1) / (total + 1) : total ? match / total : 0 });
      }
      const L = c.length;
      const r = refs.map(x => x.length).reduce((best, x) => (Math.abs(x - L) < Math.abs(best - L) || (Math.abs(x - L) === Math.abs(best - L) && x < best)) ? x : best, refs[0].length);
      const BP = L > r ? 1 : Math.exp(1 - r / L);
      const ok = P.every(q => q.p > 0);
      const geo = ok ? Math.exp(P.reduce((a, q) => a + Math.log(q.p), 0) / P.length) : 0;
      const bleu = BP * geo;
      D.text(g, 'Clipped n-gram precision', 16, 24, { b: true, s: 13, c: z.col.ink });
      P.forEach((q, i) => {
        const y = 40 + i * 44;
        D.text(g, `p${q.n}`, 16, y + 20, { b: true, s: 13, mono: true, c: z.col.ink });
        rr(g, 50, y + 6, 300, 20, 5, { fill: z.col.bg, stroke: z.col.line });
        rr(g, 50, y + 6, Math.max(2, q.p * 300), 20, 5, { fill: z.col.cv });
        D.text(g, p.smooth && q.n > 1 ? `(${q.match} + 1) ÷ (${q.total} + 1) = ${fmt(q.p, 4)}` : `${q.match} of ${q.total} match = ${fmt(q.p, 4)}`, 360, y + 20, { s: 12, c: z.col.ink2 });
      });
      const y0 = 40 + P.length * 44 + 10;
      D.text(g, `candidate length c = ${L}, closest reference length r = ${r}`, 16, y0, { s: 12, c: z.col.ink2 });
      D.text(g, `brevity penalty BP = ${L > r ? '1 (c > r)' : `e^(1 − r/c) = ${fmt(BP, 4)}`}`, 16, y0 + 20, { s: 12, c: z.col.ink2 });
      D.text(g, `BLEU = ${fmt(bleu, 4)}`, 16, y0 + 46, { b: true, s: 16, c: z.col.cv });
      return `BLEU = BP × exp( (1/N) Σ log p<sub>n</sub> ) = <b>${fmt(bleu, 4)}</b>${!ok ? ' (one precision is 0, so the geometric mean is 0. Tick smoothing to see a small non zero score.)' : ''}. Clipping means a candidate word is counted at most as many times as it appears in any one reference.`;
    }
  });
})();

/* ---------------------------------------------------------------- Chapter 2.1 and 2.2: tokens, stems and lemmas */
(() => {
  const { def, D, esc } = CVZ;
  const { tw, rr, pill, flow, wrap, fit, fmt } = NLZ;
  const ABBR = 'Dr. Mr. Mrs. Ms. Prof. St. etc. e.g. i.e. vs. U.S. Jan. Feb.';
  /* split text into sentences: a period, ! or ? ends a sentence unless the word is a known abbreviation */
  function sentences(text, abbr, needCap) {
    const A = new Set(String(abbr).split(/\s+/).filter(Boolean).map(a => a.toLowerCase()));
    const out = [];
    let cur = '';
    const parts = String(text).split(/(\s+)/);
    for (let i = 0; i < parts.length; i++) {
      const t = parts[i];
      cur += t;
      if (/\s/.test(t) || !t) continue;
      if (/[.!?]["')\]]*$/.test(t)) {
        if (A.has(t.toLowerCase())) continue;
        const next = (parts[i + 2] || '');
        if (needCap && next && !/^["'(\[]?[A-Z0-9]/.test(next)) continue;
        out.push(cur.trim()); cur = '';
      }
    }
    if (cur.trim()) out.push(cur.trim());
    return out;
  }
  /* a Treebank style word tokenizer in the spirit of nltk.word_tokenize */
  function treebank(sent) {
    let s = ' ' + sent + ' ';
    s = s.replace(/([,;:@#$%&?!])/g, ' $1 ');
    s = s.replace(/"/g, ' " ');
    s = s.replace(/([^\s])\.(\s*)$/, '$1 .$2');
    s = s.replace(/([A-Za-z])(n't)\b/gi, '$1 $2');
    s = s.replace(/([A-Za-z])('s|'re|'ll|'m|'ve|'d)\b/gi, '$1 $2');
    s = s.replace(/([()\[\]{}])/g, ' $1 ');
    return s.split(/\s+/).filter(Boolean);
  }
  NLZ.sentences = sentences; NLZ.treebank = treebank;

  def('sentsplit', {
    title: 'Sentence segmentation: where does a sentence end?',
    sub: 'A full stop is not always the end of a sentence. Turn the rules on and off and watch the split change.',
    W: 560, H: 250,
    params: [
      { k: 'text', label: 'Paragraph', type: 'area', v: "All work and no play make Dr. jack a dull boy. It's a beautiful day out there in Jodhpur. Don't you think, it will rain today?" },
      { k: 'useAbbr', label: 'Keep known abbreviations together', type: 'check', v: true },
      { k: 'abbr', label: 'Abbreviation list', type: 'text', v: ABBR, show: p => p.useAbbr },
      { k: 'cap', label: 'Only split when the next word starts with a capital', type: 'check', v: false }
    ],
    tips: [
      { t: 'Untick the abbreviation list. "Dr." now ends a sentence and you get 4 pieces instead of the 3 that NLTK sent_tokenize returned in the notebook.', set: { useAbbr: false, cap: false } },
      { t: 'Keep abbreviations off but require a capital after the stop. "jack" is lower case, so the split is fixed again by a different rule.', set: { useAbbr: false, cap: true } },
      { t: 'Type "I paid $3.50 at 5 p.m. today. It was fine." and see how many rules a real splitter needs.', set: { text: 'I paid $3.50 at 5 p.m. today. It was fine.', useAbbr: true, cap: false } }
    ],
    draw(z) {
      const { g, p } = z;
      const S = sentences(p.text, p.useAbbr ? p.abbr : '', p.cap);
      D.text(g, `${S.length} sentence${S.length === 1 ? '' : 's'}`, 16, 24, { b: true, s: 14, c: z.col.ink });
      let y = 40;
      S.forEach((s, i) => {
        if (y > z.H - 30) return;
        const fs = 12.5;
        const lines = [];
        let line = '';
        s.split(/\s+/).forEach(w => { const t = line ? line + ' ' + w : w; if (line && tw(g, t, { s: fs }) > 470) { lines.push(line); line = w; } else line = t; });
        if (line) lines.push(line);
        const h = lines.length * 17 + 12;
        rr(g, 16, y, 528, h, 8, { fill: i % 2 ? z.col.bg : z.col.surf, stroke: z.col.cv });
        D.text(g, String(i + 1), 30, y + 19, { b: true, s: 13, c: z.col.cv });
        lines.forEach((l, j) => D.text(g, l, 50, y + 19 + j * 17, { s: fs, c: z.col.ink }));
        y += h + 8;
      });
      return `Python list: <code>[${S.map(x => esc(JSON.stringify(x))).join(', ')}]</code><br>NLTK's sent_tokenize uses the Punkt model, which learned from a large corpus which words are abbreviations, so it needs no hand made list.`;
    }
  });

  def('tokenizer', {
    title: 'Tokenisation: from a string to a list of tokens',
    sub: 'Compare three tokenisers on the same text. The counts show how the choice changes the vocabulary.',
    W: 560, H: 220,
    params: [
      { k: 'text', label: 'Text', type: 'area', v: "All work and no play make Dr. jack a dull boy. It's a beautiful day out there in Jodhpur. Don't you think, it will rain today?" },
      { k: 'how', label: 'Tokeniser', type: 'select', v: 'tb', opts: [['ws', 'Split on spaces: text.split()'], ['re', 'Letters and digits only: re.findall(r"\\w+")'], ['tb', 'Treebank style, like nltk.word_tokenize']] },
      { k: 'lower', label: 'Lower case every token', type: 'check', v: false }
    ],
    tips: [
      { t: 'Choose "split on spaces". "boy." and "think," keep their punctuation, so "boy" and "boy." would become two different words.', set: { how: 'ws' } },
      { t: 'Choose the Treebank style. "Don\'t" becomes Do and n\'t, and "It\'s" becomes It and \'s, exactly the notebook output.', set: { how: 'tb', lower: false } },
      { t: 'Use the notebook FreqDist sentence and tick lower case. "This" and "this" merge, so types drop from 11 to 10.', set: { text: 'This is an example sentence to tell you how this example works', how: 'tb', lower: true } }
    ],
    draw(z) {
      const { g, p } = z;
      let toks;
      if (p.how === 'ws') toks = String(p.text).split(/\s+/).filter(Boolean);
      else if (p.how === 're') toks = String(p.text).match(/[A-Za-z0-9_]+/g) || [];
      else toks = sentences(p.text, ABBR, false).flatMap(s => treebank(s, ABBR));
      if (p.lower) toks = toks.map(t => t.toLowerCase());
      const types = new Set(toks);
      D.text(g, `${toks.length} tokens, ${types.size} types`, 16, 24, { b: true, s: 14, c: z.col.ink });
      const r = flow(g, toks.slice(0, 60).map(t => ({ t, fill: /^[^A-Za-z0-9]+$/.test(t) ? z.col.orange : /'/.test(t) ? z.col.purple : z.col.bg, c: /^[^A-Za-z0-9]+$/.test(t) || /'/.test(t) ? '#fff' : z.col.ink })), 16, 38, 528, { s: 12, stroke: z.col.line, gap: 5, rowGap: 6 });
      if (toks.length > 60) D.text(g, `… ${toks.length - 60} more`, 16, r.y + 16, { s: 12, c: z.col.ink2 });
      return `Orange tokens are punctuation, purple ones are split contractions. Python list: <code>[${toks.slice(0, 40).map(x => esc(JSON.stringify(x))).join(', ')}${toks.length > 40 ? ', …' : ''}]</code>`;
    }
  });

  /* a small lemma dictionary in the style of WordNet: unknown words come back unchanged, as WordNetLemmatizer does */
  const LEX = {
    n: { children: 'child', leaves: 'leaf', games: 'game', geese: 'goose', mice: 'mouse', feet: 'foot', teeth: 'tooth', women: 'woman', men: 'man', cats: 'cat', ideas: 'idea', studies: 'study', wolves: 'wolf', knives: 'knife', alumni: 'alumnus', alumnae: 'alumna', chocolates: 'chocolate', boxes: 'box', churches: 'church', universities: 'university', data: 'datum', corpora: 'corpus', analyses: 'analysis' },
    v: { loving: 'love', saw: 'see', seen: 'see', running: 'run', ran: 'run', gaming: 'game', gamed: 'game', cared: 'care', studies: 'study', studied: 'study', went: 'go', gone: 'go', was: 'be', were: 'be', is: 'be', are: 'be', been: 'be', has: 'have', had: 'have', ate: 'eat', eaten: 'eat', snowing: 'snow', flying: 'fly', flew: 'fly', bought: 'buy', thought: 'think', sleeping: 'sleep', jumped: 'jump', leaves: 'leave', left: 'leave' },
    a: { better: 'good', best: 'good', worse: 'bad', worst: 'bad', happier: 'happy', bigger: 'big', larger: 'large' }
  };
  const lemma = (w, pos) => { const x = String(w).toLowerCase(); return (LEX[pos] && LEX[pos][x]) || x; };
  NLZ.lemma = lemma;

  def('porter', {
    title: 'The Porter stemmer, one step at a time',
    sub: 'Type a word and play. Each step removes or rewrites one kind of ending. The result is the same as NLTK PorterStemmer.',
    W: 560, H: 300,
    params: [
      { k: 'w', label: 'Word', type: 'text', v: 'sportingly' },
      { k: 'pos', label: 'Part of speech for the lemma', type: 'select', v: 'n', opts: [['n', 'noun (the NLTK default)'], ['v', 'verb'], ['a', 'adjective']] }
    ],
    tips: [
      { t: 'Try "leaves". Porter stops at leav, which is not a word. The lemma as a noun is leaf.', set: { w: 'leaves', pos: 'n' } },
      { t: 'Try "relational". Step 2 turns ational into ate (relate), then step 5a drops the final e, leaving relat.', set: { w: 'relational' } },
      { t: 'Try "loving" with noun and then verb. The lemmatiser only gives love when told it is a verb, as in the notebook.', set: { w: 'loving', pos: 'v' } },
      { t: 'Try "generously". Porter gives gener but Snowball keeps generous, because Snowball protects the start gener.', set: { w: 'generously' } }
    ],
    steps: () => 8,
    draw(z) {
      const { g, p } = z;
      const tr = [];
      const word = String(p.w).trim().split(/\s+/)[0] || '';
      const out = NLSTEM.porter(word, tr);
      const sb = NLSTEM.snowball(word);
      D.text(g, 'Word', 16, 26, { s: 12, c: z.col.ink2 });
      D.text(g, word.toLowerCase(), 60, 26, { b: true, s: 16, mono: true, c: z.col.ink });
      D.text(g, `measure m of the word = ${NLSTEM.measure(word.toLowerCase())}`, 544, 26, { a: 'right', s: 12, c: z.col.ink2 });
      let prev = word.toLowerCase();
      tr.forEach((t, i) => {
        const y = 42 + i * 28;
        const on = i < z.step || tr.length === 1;
        const changed = t[1] !== prev;
        rr(g, 16, y, 528, 24, 6, { fill: on ? (changed ? z.col.cv : z.col.bg) : z.col.surf, stroke: z.col.line });
        D.text(g, t[0], 26, y + 16, { s: fit(g, t[0], 360, 12), c: on && changed ? '#fff' : z.col.ink2, b: on && changed });
        if (on) D.text(g, t[1], 534, y + 16, { a: 'right', s: 13, mono: true, b: true, c: changed ? '#fff' : z.col.ink });
        if (on) prev = t[1];
      });
      const y0 = 42 + tr.length * 28 + 14;
      if (y0 < z.H - 10) D.text(g, `Porter: ${out}     Snowball: ${sb}     lemma (${p.pos}): ${lemma(word, p.pos)}`, 16, Math.min(y0, z.H - 12), { b: true, s: 13, mono: true, c: z.col.cv });
      return `Porter <b>${esc(out)}</b>, Snowball <b>${esc(sb)}</b>, lemma <b>${esc(lemma(word, p.pos))}</b>. A stem is whatever the rules leave and need not be a word. A lemma is a dictionary word and depends on the part of speech. The lemma column uses a small built in dictionary, and like WordNetLemmatizer it returns a word it does not know unchanged.`;
    }
  });

  def('stemcompare', {
    title: 'Porter against Snowball against a lemmatiser',
    sub: 'Edit the word list. Rows where the two stemmers disagree are marked. The default list is the notebook exercise.',
    W: 560, H: 380,
    params: [
      { k: 'list', label: 'Words, separated by spaces or commas', type: 'area', v: 'alumnus running alumnu alumni alumna alumnae cats catty cat chocolates chocolatey choco children' },
      { k: 'pos', label: 'Part of speech for the lemma', type: 'select', v: 'n', opts: [['n', 'noun'], ['v', 'verb'], ['a', 'adjective']] }
    ],
    tips: [
      { t: 'Load the notebook tutorial words. Porter and Snowball disagree on sportingly, fairly and boy\'s.', set: { list: "game gaming gamed games leaves cared children sportingly fairly saw loving boy's" } },
      { t: 'Try university universe universal. All three collapse to univers, an over stemming error.', set: { list: 'university universe universal universities' } },
      { t: 'Try saw went better with the verb lemma and then the adjective lemma.', set: { list: 'saw went better running', pos: 'v' } }
    ],
    draw(z) {
      const { g, p } = z;
      const ws = String(p.list).split(/[\s,]+/).filter(Boolean).slice(0, 15);
      const cols = [16, 160, 290, 420];
      ['word', 'Porter', 'Snowball', `lemma (${p.pos})`].forEach((h, i) => D.text(g, h, cols[i], 24, { b: true, s: 13, c: z.col.ink }));
      D.line(g, 16, 32, 544, 32, z.col.line, 1);
      let diff = 0;
      ws.forEach((w, i) => {
        const y = 52 + i * 21.5;
        const a = NLSTEM.porter(w), b = NLSTEM.snowball(w), l = lemma(w, p.pos);
        const d = a !== b;
        if (d) { diff++; rr(g, 12, y - 15, 536, 20, 5, { fill: z.col.hl || z.col.bg }); }
        D.text(g, w, cols[0], y, { s: 12.5, mono: true, c: z.col.ink });
        D.text(g, a, cols[1], y, { s: 12.5, mono: true, b: d, c: d ? z.col.orange : z.col.ink2 });
        D.text(g, b, cols[2], y, { s: 12.5, mono: true, b: d, c: d ? z.col.cv : z.col.ink2 });
        D.text(g, l, cols[3], y, { s: 12.5, mono: true, c: l !== w.toLowerCase() ? z.col.green : z.col.ink2 });
      });
      return `${ws.length} words, the stemmers disagree on <b>${diff}</b>. In the notebook exercise the only difference was alumnus: Porter alumnu, Snowball alumnus. Snowball (Porter2) is the newer, better tuned version of Porter, which is why the notebook chose it. Green lemmas were found in the small dictionary.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 2.3: counting */
  def('freqdist', {
    title: 'FreqDist: counting tokens',
    sub: 'Type any text. The bars are the most common tokens, as FreqDist.most_common() would list them.',
    W: 560, H: 300,
    params: [
      { k: 'text', label: 'Text', type: 'area', v: 'This is an example sentence to tell you how this example works' },
      { k: 'lower', label: 'Lower case first', type: 'check', v: false },
      { k: 'punct', label: 'Drop punctuation tokens', type: 'check', v: false },
      { k: 'top', label: 'Show the top', type: 'range', min: 3, max: 15, v: 8 },
      { k: 'q', label: 'Look up one token', type: 'text', v: 'example' }
    ],
    tips: [
      { t: 'Tick lower case. "This" and "this" merge: samples go from 11 to 10 and outcomes stay 12, as in the notebook.', set: { lower: true } },
      { t: 'Type the notebook list a b a a c b a. FreqDist reports 3 samples and 7 outcomes, and freq(a) = 4 ÷ 7 = 0.5714.', set: { text: 'a b a a c b a', lower: false, q: 'a' } },
      { t: 'Paste a long paragraph. A few words take most of the count and many appear once. That is the start of Zipf\'s law (chapter 3.1).', set: { text: 'the cat sat on the mat and the dog sat on the log and the cat saw the dog and the dog saw the cat on the mat', lower: true, top: 12, q: 'the' } }
    ],
    draw(z) {
      const { g, p } = z;
      let toks = NLZ.sentences(p.text, ABBR, false).flatMap(s => NLZ.treebank(s, ABBR));
      if (p.lower) toks = toks.map(t => t.toLowerCase());
      if (p.punct) toks = toks.filter(t => /[A-Za-z0-9]/.test(t));
      const c = new Map();
      toks.forEach(t => c.set(t, (c.get(t) || 0) + 1));
      const arr = [...c.entries()].sort((a, b) => b[1] - a[1]);
      const N = toks.length, B = c.size, hap = arr.filter(e => e[1] === 1).length;
      const top = arr.slice(0, p.top);
      const mx = top.length ? top[0][1] : 1;
      D.text(g, `<FreqDist with ${B} samples and ${N} outcomes>`, 16, 24, { b: true, s: 13, mono: true, c: z.col.ink });
      const rh = Math.min(26, 230 / Math.max(1, top.length));
      top.forEach(([w, n], i) => {
        const y = 40 + i * rh;
        const hot = w === p.q || (p.lower && w === String(p.q).toLowerCase());
        D.text(g, w, 120, y + rh * 0.62, { a: 'right', s: fit(g, w, 100, 12.5), mono: true, c: z.col.ink });
        rr(g, 128, y + 3, Math.max(3, n / mx * 330), rh - 7, 4, { fill: hot ? z.col.orange : z.col.cv });
        D.text(g, String(n), 134 + n / mx * 330, y + rh * 0.62, { s: 12, c: z.col.ink2 });
      });
      const qn = c.get(p.lower ? String(p.q).toLowerCase() : p.q) || 0;
      return `N() = <b>${N}</b> outcomes (tokens), B() = <b>${B}</b> samples (types), hapaxes (seen once) = <b>${hap}</b>. fdist['${esc(p.q)}'] = <b>${qn}</b>, freq = ${qn} ÷ ${N} = <b>${N ? fmt(qn / N, 4) : 0}</b>. max() = <b>${arr.length ? esc(arr[0][0]) : '-'}</b>.`;
    }
  });

  const CORP = {
    'brown-words': ['NLTK Brown corpus, top words', 1161192, [['the', 62713], [',', 58334], ['.', 49346], ['of', 36080], ['and', 27915], ['to', 25732], ['a', 21881], ['in', 19536], ['that', 10237], ['is', 10011]], '56,057 types'],
    'ptb-words': ['Penn Treebank sample, top words', 100676, [[',', 4885], ['the', 4045], ['.', 3828], ['of', 2319], ['to', 2164], ['a', 1878], ['in', 1572], ['and', 1511], ['*-1', 1123], ['0', 1099]], '12,408 types. *-1 and 0 are empty elements tagged -NONE-, not real words'],
    'brown-sample': ['brown.txt class sample, top tags', 2242, [['nn', 327], ['at', 217], ['in', 203], ['nns', 119], ['np', 105], ['.', 88], ['jj', 87], [',', 87], ['nn-tl', 82], ['vbd', 75]], '84 distinct tags in 2,242 tokens'],
    'brown-tags': ['NLTK Brown corpus, top tags', 1161192, [['NN', 152470], ['IN', 120557], ['AT', 97959], ['JJ', 64028], ['.', 60638], [',', 58156], ['NNS', 55110], ['CC', 37718], ['RB', 36464], ['NP', 34476]], '472 distinct tags, because compound tags like NN-TL count separately'],
    'ptb-tags': ['Penn Treebank, PTB tagset', 100676, [['NN', 13166], ['IN', 9857], ['NNP', 9410], ['DT', 8165], ['-NONE-', 6592], ['NNS', 6047], ['JJ', 5834], [',', 4886], ['.', 3874], ['CD', 3546]], '46 distinct tags. RB occurs 2,822 times'],
    'ptb-uni': ['Penn Treebank, universal tagset', 100676, [['NOUN', 28867], ['VERB', 13564], ['.', 11715], ['ADP', 9857], ['DET', 8725], ['X', 6613], ['ADJ', 6397], ['NUM', 3546], ['PRT', 3219], ['ADV', 3171]], '12 tags. RB does not exist here: ADV 3,171 = RB 2,822 + RBR 136 + RBS 35 + WRB 178']
  };
  def('tagcount', {
    title: 'What the notebook counted: words and tags in Brown and the Penn Treebank',
    sub: 'Real counts from the class notebook. Switch corpus and tagset to compare them.',
    W: 560, H: 300,
    params: [
      { k: 'c', label: 'Corpus and count', type: 'select', v: 'brown-words', opts: Object.entries(CORP).map(([k, v]) => [k, v[0]]) },
      { k: 'pct', label: 'Show the share of all tokens', type: 'check', v: true },
      { k: 'top', label: 'Show the top', type: 'range', min: 3, max: 10, v: 10 }
    ],
    tips: [
      { t: 'Compare Brown words with PTB words. "the" is 5.40% of Brown but 4.02% of PTB, and in PTB the comma beats "the".', set: { c: 'ptb-words', pct: true } },
      { t: 'Switch PTB tags to the universal tagset. 46 tags shrink to 12 and NOUN alone covers 28.7% of tokens.', set: { c: 'ptb-uni' } },
      { t: 'Look at the small class sample. Its tags are lower case and NN still wins, the same pattern as the full Brown corpus.', set: { c: 'brown-sample' } }
    ],
    draw(z) {
      const { g, p } = z;
      const [name, N, rows, note] = CORP[p.c];
      const top = rows.slice(0, p.top), mx = top[0][1];
      D.text(g, `${name}: N = ${N.toLocaleString()} tokens`, 16, 24, { b: true, s: 13, c: z.col.ink });
      const rh = 230 / top.length;
      top.forEach(([w, n], i) => {
        const y = 40 + i * rh;
        D.text(g, w, 100, y + rh * 0.62, { a: 'right', s: 12.5, mono: true, c: z.col.ink });
        rr(g, 108, y + 3, Math.max(3, n / mx * 320), rh - 7, 4, { fill: z.col.cv });
        D.text(g, p.pct ? `${(100 * n / N).toFixed(2)}%` : n.toLocaleString(), 114 + n / mx * 320, y + rh * 0.62, { s: 12, c: z.col.ink2 });
      });
      return `${esc(note)}. The share is the count divided by all ${N.toLocaleString()} tokens, which is what <code>fdist.freq()</code> returns.`;
    }
  });
})();
