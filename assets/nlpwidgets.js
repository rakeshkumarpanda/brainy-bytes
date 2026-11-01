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
    r = Math.max(0, Math.min(r, w / 2, h / 2));
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
    /* a word longer than the line (a run of random letters, say) is cut into pieces that fit */
    const words = String(s).split(/\s+/).filter(Boolean).flatMap(w => {
      if (tw(g, w, o) <= maxW) return [w];
      const out = []; let cur = '';
      for (const ch of w) { if (cur && tw(g, cur + ch, o) > maxW) { out.push(cur); cur = ch; } else cur += ch; }
      if (cur) out.push(cur);
      return out;
    });
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
      { k: 'show', label: 'Reveal the answer', type: 'check', v: false, reveal: true }
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

/* ---------------------------------------------------------------- Step 3: Zipf, entropy and information */
(() => {
  const { def, D, esc, rng } = CVZ;
  const { tw, rr, pill, wrap, fit, log2, fmt } = NLZ;

  /* a short original English passage used to train the small models below */
  const SAMPLE = `the history of the written word is a history of people trying to say more with less. a farmer who sends a message to the market town does not write every word he would say aloud. he writes the name of the crop, the number of bags and the day he will arrive, and he trusts the reader to fill in the rest. the reader can do this because the language is full of patterns. after the word number we expect the word of, after a full stop we expect a capital letter, and after the letter q we expect the letter u. these patterns are what make a language easy to learn and easy to understand, and they are also what make it possible to send a long message in a short form. in the same way a student who takes notes in class writes only the words that matter and leaves out the words that anyone could guess. the notes are short, but the student can read them again a month later and remember the whole lecture. a good teacher knows this and speaks so that the important words stand out from the words that only hold the sentence together. the small words of the language, such as the, of, and, to, a and in, appear again and again in every kind of text. the large words, such as harvest, telescope or parliament, appear only when the topic calls for them. if you count the words in any book you will find that a few words fill most of the pages and most of the words appear only once or twice. this simple fact was noticed long ago by people who printed books and by people who taught shorthand, and it was later studied with great care by scientists who wanted to know how much information a message really carries. their answer was that the information in a message depends on how surprising it is. a word that the reader could have guessed carries little information, and a word that nobody expected carries a great deal. when the reader knows the topic, the speaker and the words that came before, many words become easy to guess, and the message can be made shorter without any loss. this is the idea behind the compressed files on a computer, the short forms in a text message and the models that predict the next word on a phone keyboard.`;
  NLZ.SAMPLE = SAMPLE;

  /* least squares slope of y on x */
  function slope(xs, ys) {
    const n = xs.length; if (n < 2) return NaN;
    const mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n;
    let sxy = 0, sxx = 0;
    for (let i = 0; i < n; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; }
    return sxx ? sxy / sxx : NaN;
  }
  const SUP = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' };
  /* log-log axes with ticks at powers of ten */
  function loglog(g, z, box, xmax, ymax, ymin = 1) {
    const [X, Y, W, H] = box;
    const lx0 = 0, lx1 = Math.max(1, Math.ceil(Math.log10(xmax)));
    const ly0 = Math.floor(Math.log10(Math.max(ymin, 1e-9))), ly1 = Math.max(ly0 + 1, Math.ceil(Math.log10(ymax)));
    const sx = v => X + (Math.log10(v) - lx0) / (lx1 - lx0) * W;
    const sy = v => Y + H - (Math.log10(v) - ly0) / (ly1 - ly0) * H;
    D.rect(g, X, Y, W, H, { stroke: z.col.line, w: 1 });
    const lab = e => e >= 0 && e < 4 ? String(10 ** e) : '10' + String(e).split('').map(ch => SUP[ch]).join('');
    for (let e = lx0; e <= lx1; e++) { D.line(g, sx(10 ** e), Y + H, sx(10 ** e), Y + H + 4, z.col.ink2, 1); D.text(g, lab(e), sx(10 ** e), Y + H + 16, { a: 'center', s: 10.5, c: z.col.ink2 }); }
    for (let e = ly0; e <= ly1; e++) { D.line(g, X - 4, sy(10 ** e), X, sy(10 ** e), z.col.ink2, 1); D.text(g, lab(e), X - 6, sy(10 ** e) + 4, { a: 'right', s: 10.5, c: z.col.ink2 }); }
    return { sx, sy };
  }

  /* ---------------------------------------------------------------- Chapter 3.1: Zipf */
  const BROWN_ZIPF = [[1, 'the', 69971], [2, 'of', 36412], [3, 'and', 28853], [10, 'he', 9548], [50, 'no', 2139], [100, 'well', 897], [150, 'three', 610], [500, 'private', 191], [1000, 'eight', 104], [5000, 'dairy', 19], [10000, 'incredibly', 7]];
  def('zipf', {
    title: "Zipf's law: frequency falls like one over rank",
    sub: 'Dots are real counts. The line is the law f = k ÷ (r + b)^a. Change k, a and b until the line passes through the dots.',
    W: 560, H: 300,
    params: [
      { k: 'src', label: 'Data', type: 'select', v: 'brown', opts: [['brown', 'Brown corpus, lower cased (11 ranks)'], ['text', 'Count the words of my own text']] },
      { k: 'text', label: 'Your text', type: 'area', v: SAMPLE, show: p => p.src === 'text' },
      { k: 'k', label: 'k, the frequency of rank 1', type: 'range', min: 10, max: 150000, step: 10, v: 69970 },
      { k: 'a', label: 'Exponent a (Zipf: 1)', type: 'range', min: 0.5, max: 1.5, step: 0.01, v: 1 },
      { k: 'b', label: 'Mandelbrot shift b (Zipf: 0)', type: 'range', min: 0, max: 10, step: 0.1, v: 0 },
      { k: 'log', label: 'Log scale on both axes', type: 'check', v: true }
    ],
    tips: [
      { t: 'Untick the log scale. The same data is a steep hyperbola: a handful of words tower over a very long tail.', set: { log: false } },
      { t: 'Set a to 1.08, the slope measured on Brown for ranks 10 to 10,000. The line now follows the tail more closely.', set: { a: 1.08, k: 100000, log: true } },
      { t: 'Switch to your own text. Even this short passage shows the falling line, though its tail is a staircase of words seen once or twice.', set: { src: 'text', k: 60, a: 1, b: 0 } },
      { t: 'Set b to 2.7 and k to 100000. The Mandelbrot shift flattens the top of the curve, as real corpora do.', set: { src: 'brown', k: 100000, a: 1, b: 2.7 } }
    ],
    draw(z) {
      const { g, p } = z;
      let pts;
      if (p.src === 'brown') pts = BROWN_ZIPF.map(r => [r[0], r[2], r[1]]);
      else {
        const c = new Map();
        (String(p.text).toLowerCase().match(/[a-z']+/g) || []).forEach(w => c.set(w, (c.get(w) || 0) + 1));
        pts = [...c.entries()].sort((x, y) => y[1] - x[1]).map((e, i) => [i + 1, e[1], e[0]]);
      }
      if (!pts.length) return 'Type some text.';
      const law = r => p.k / Math.pow(r + p.b, p.a);
      const rmax = Math.max(...pts.map(q => q[0])), fmax = Math.max(pts[0][1], law(1));
      const box = [62, 16, 300, 236];
      let m;
      if (p.log) m = loglog(g, z, box, rmax, fmax, Math.min(1, ...pts.map(q => q[1])));
      else m = D.axes(g, z, box, [0, rmax], [0, fmax], { nx: 4, ny: 4, fx: v => Math.round(v).toLocaleString(), fy: v => Math.round(v).toLocaleString() });
      D.text(g, 'rank r', box[0] + box[2] / 2, box[1] + box[3] + 32, { a: 'center', s: 11.5, b: true, c: z.col.ink2 });
      g.save(); g.beginPath(); g.rect(box[0], box[1], box[2], box[3]); g.clip();
      D.curve(g, r => law(r), [1, rmax], { sx: m.sx, sy: m.sy }, z.col.orange, 2, 300);
      pts.forEach(q => D.circle(g, m.sx(q[0]), m.sy(q[1]), 3.5, { fill: z.col.cv }));
      g.restore();
      /* right panel: f × r for the listed ranks */
      const show = p.src === 'brown' ? pts : pts.filter((q, i) => i < 5 || [10, 20, 50, 100].includes(q[0])).slice(0, 10);
      D.text(g, 'rank', 414, 26, { a: 'right', s: 11.5, b: true, c: z.col.ink2 });
      D.text(g, 'word', 422, 26, { s: 11.5, b: true, c: z.col.ink2 });
      D.text(g, 'f × r', 548, 26, { a: 'right', s: 11.5, b: true, c: z.col.ink2 });
      show.slice(0, 11).forEach((q, i) => {
        const y = 46 + i * 21;
        D.text(g, String(q[0]), 414, y, { a: 'right', s: 11, c: z.col.ink, mono: true });
        D.text(g, q[2], 422, y, { s: fit(g, q[2], 64, 11.5), c: z.col.ink });
        D.text(g, (q[0] * q[1]).toLocaleString(), 548, y, { a: 'right', s: 11.5, c: z.col.cv, mono: true, b: true });
      });
      const fitp = pts.filter(q => q[0] >= 2);
      const sl = slope(fitp.map(q => Math.log10(q[0])), fitp.map(q => Math.log10(q[1])));
      return `Fitted slope of the dots on log log axes: <b>${isFinite(sl) ? sl.toFixed(2).replace('-', '−') : '-'}</b> (Zipf predicts −1). The law with your values gives rank 2 a frequency of <b>${Math.round(law(2)).toLocaleString()}</b> and rank 10 <b>${Math.round(law(10)).toLocaleString()}</b>. If f × r were exactly constant, the last column would show one number. On Brown it stays between about 70,000 and 107,000 across four powers of ten.`;
    }
  });

  def('monkey', {
    title: 'Monkey typing: random keys also give a power law',
    sub: 'A monkey presses M letter keys and a space bar at random. A word is whatever falls between two spaces. Count the words, rank them and plot.',
    W: 560, H: 300,
    params: [
      { k: 'M', label: 'Number of letter keys M', type: 'range', min: 2, max: 26, v: 4 },
      { k: 's', label: 'Probability of the space bar s', type: 'range', min: 0.02, max: 0.5, step: 0.001, v: 0.2 },
      { k: 'n', label: 'Characters typed', type: 'range', min: 20000, max: 300000, step: 10000, v: 200000 },
      { k: 'seed', label: 'Random seed', type: 'range', min: 1, max: 50, v: 7 }
    ],
    tips: [
      { t: 'Use the lecture setting: 26 letters and a space, all 1/27. The predicted exponent is ln 27 ÷ ln 26 = 1.0116, almost exactly Zipf. Most words are now long and seen once, so only the top of the curve shows the steps.', set: { M: 26, s: 0.037, n: 300000 } },
      { t: 'Use 2 letters with s = 0.33. The exponent becomes 1 − ln(0.67) ÷ ln 2 ≈ 1.58 and the staircase steps are large.', set: { M: 2, s: 0.33 } },
      { t: 'Change only the seed. The steps move a little but the slope stays, because it comes from counting, not from luck.', set: { seed: 23 } }
    ],
    draw(z) {
      const { g, p } = z;
      const r = rng(p.seed * 7919);
      const letters = 'etaoinshrdlucmfwypvbgkqjxz'.slice(0, p.M);
      const c = new Map();
      let w = '';
      for (let i = 0; i < p.n; i++) {
        if (r() < p.s) { if (w) c.set(w, (c.get(w) || 0) + 1); w = ''; }
        else w += letters[Math.floor(r() * p.M)];
      }
      const f = [...c.values()].sort((a, b) => b - a);
      const alpha = 1 - Math.log(1 - p.s) / Math.log(p.M);
      const box = [62, 16, 330, 236];
      const m = loglog(g, z, box, f.length, f[0], 1);
      D.text(g, 'rank r', box[0] + box[2] / 2, box[1] + box[3] + 32, { a: 'center', s: 11.5, b: true, c: z.col.ink2 });
      g.save(); g.beginPath(); g.rect(box[0], box[1], box[2], box[3]); g.clip();
      for (let i = 0; i < f.length; i += i < 2000 ? 1 : Math.max(1, Math.floor(f.length / 2000))) D.circle(g, m.sx(i + 1), m.sy(f[i]), 1.6, { fill: z.col.cv });
      /* predicted line through the middle of the data */
      const mid = Math.max(1, Math.floor(Math.sqrt(f.length)));
      const k = f[mid - 1] * Math.pow(mid, alpha);
      D.curve(g, x => k / Math.pow(x, alpha), [1, f.length], { sx: m.sx, sy: m.sy }, z.col.orange, 2, 200, [6, 4]);
      g.restore();
      const xs = [], ys = [];
      for (let i = 9; i < f.length; i++) if (f[i] >= 3) { xs.push(Math.log10(i + 1)); ys.push(Math.log10(f[i])); }
      const sl = slope(xs, ys);
      D.text(g, 'What the monkey typed', 410, 30, { s: 12, b: true, c: z.col.ink });
      let y = 52;
      [...c.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8).forEach(([wd, n]) => { D.text(g, wd, 410, y, { s: 12, mono: true, c: z.col.ink }); D.text(g, n.toLocaleString(), 548, y, { a: 'right', s: 12, mono: true, c: z.col.ink2 }); y += 19; });
      D.text(g, `${f.length.toLocaleString()} distinct words`, 410, y + 8, { s: 11.5, c: z.col.ink2 });
      return `Predicted exponent α = 1 − ln(1 − s) ÷ ln M = <b>${fmt(alpha, 4)}</b>. Slope fitted to the dots (words seen 3 or more times, from rank 10): <b>${fmt(-sl, 3)}</b>. The flat steps are words of the same length, which all have the same probability. The monkey gets the power law but none of the predictability of real language.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 3.2: entropy and codes */
  const UNIT = { '2': 'bits', e: 'nats', '10': 'hartleys' };
  const lg = (x, base) => Math.log(x) / (base === 'e' ? 1 : Math.log(+base));
  def('entropy', {
    title: 'Entropy: the average surprise of a distribution',
    sub: 'Edit the outcomes and their probabilities. Each orange bar is one term −p log p of the sum.',
    W: 560, H: 280,
    params: [
      { k: 'list', label: 'Outcome and probability, one per line', type: 'area', v: 'heads 0.5\ntails 0.5' },
      { k: 'base', label: 'Logarithm base', type: 'select', v: '2', opts: [['2', 'base 2 (bits)'], ['e', 'base e (nats)'], ['10', 'base 10 (hartleys)']] }
    ],
    tips: [
      { t: 'Make the coin 0.9 and 0.1. The entropy falls from 1 bit to 0.469, the dot slides down the curve on the right.', set: { list: 'heads 0.9\ntails 0.1' } },
      { t: 'Load the fair 8 sided die from class. Eight equal outcomes give exactly log₂ 8 = 3 bits.', set: { list: '1 0.125\n2 0.125\n3 0.125\n4 0.125\n5 0.125\n6 0.125\n7 0.125\n8 0.125' } },
      { t: 'Load a die with P(6) = 0.5. Entropy drops from 2.585 to 2.161 bits. Skewed means less uncertain.', set: { list: '1 0.1\n2 0.1\n3 0.1\n4 0.1\n5 0.1\n6 0.5' } },
      { t: 'Make one outcome certain with probability 1. Every term is 0 and so is the entropy.', set: { list: 'sunrise 1\nno sunrise 0' } }
    ],
    draw(z) {
      const { g, p } = z;
      const rows = NLZ.pairs(p.list).filter(r => r[1] >= 0).slice(0, 10);
      const tot = rows.reduce((a, r) => a + r[1], 0);
      if (!rows.length || tot <= 0) return 'Write lines like "heads 0.5".';
      const P = rows.map(r => r[1] / tot);
      const T = P.map(q => q > 0 ? -q * lg(q, p.base) : 0);
      const H = T.reduce((a, b) => a + b, 0), Hmax = lg(rows.length, p.base);
      const twoPanel = rows.length === 2;
      const W1 = twoPanel ? 300 : 528;
      const rh = Math.min(24, 220 / rows.length);
      D.text(g, 'p', 120 + 60, 22, { a: 'center', s: 11.5, b: true, c: z.col.ink2 });
      D.text(g, '−p log p', 120 + (W1 - 110) * 0.75, 22, { a: 'center', s: 11.5, b: true, c: z.col.ink2 });
      const half = (W1 - 120) / 2 - 10;
      const tmax = Math.max(...T, 1e-9);
      rows.forEach((r, i) => {
        const y = 32 + i * rh;
        D.text(g, r[0], 110, y + rh * 0.66, { a: 'right', s: fit(g, r[0], 95, 12), c: z.col.ink });
        rr(g, 120, y + 3, Math.max(2, P[i] * (half - 36)), rh - 7, 4, { fill: z.col.cv });
        D.text(g, fmt(P[i], 3), 124 + P[i] * (half - 36), y + rh * 0.66, { s: 10.5, c: z.col.ink2 });
        const x2 = 130 + half;
        rr(g, x2, y + 3, Math.max(2, T[i] / tmax * (half - 40)), rh - 7, 4, { fill: z.col.orange });
        D.text(g, fmt(T[i], 3), x2 + 4 + T[i] / tmax * (half - 40), y + rh * 0.66, { s: 10.5, c: z.col.ink2 });
      });
      const yb = 32 + rows.length * rh + 22;
      if (yb < z.H - 8) D.text(g, `H = ${fmt(H, 4)} ${UNIT[p.base]}     maximum log n = ${fmt(Hmax, 4)}`, 16, yb, { b: true, s: 13, c: z.col.cv });
      if (twoPanel) {
        const m = D.axes(g, z, [366, 20, 180, 200], [0, 1], [0, lg(2, p.base)], { nx: 2, ny: 2, xl: `P(${rows[0][0]})` });
        D.curve(g, x => x <= 0 || x >= 1 ? 0 : -(x * lg(x, p.base) + (1 - x) * lg(1 - x, p.base)), [0, 1], m, z.col.orange, 2);
        D.circle(g, m.sx(P[0]), m.sy(H), 6, { fill: z.col.cv, stroke: '#fff', w: 2 });
      }
      return `Entropy H = −Σ p log p = <b>${fmt(H, 4)} ${UNIT[p.base]}</b>. The most it could be for ${rows.length} outcomes is log ${rows.length} = ${fmt(Hmax, 4)}, reached only when all are equally likely. ${Math.abs(tot - 1) > 1e-6 ? `Your numbers added to ${fmt(tot, 3)} and were rescaled. ` : ''}In bits this is also the fewest yes or no questions needed on average to learn the outcome with the best strategy.`;
    }
  });

  def('huffman', {
    title: 'Huffman coding: frequent symbols get short codes',
    sub: 'Play to merge the two least likely items again and again. When the tree is complete, read each code from the root: left is 0, right is 1.',
    W: 560, H: 300,
    params: [
      { k: 'list', label: 'Symbol and probability, one per line', type: 'area', v: 'a 0.4\nb 0.3\nc 0.2\nd 0.1' }
    ],
    tips: [
      { t: 'Use the dyadic source 1/2, 1/4, 1/8, 1/8. The average code length equals the entropy, 1.75 bits.', set: { list: 'A 0.5\nB 0.25\nC 0.125\nD 0.125' }, play: true },
      { t: 'Make all four equal. Every code has 2 bits, the same as a fixed length code. Huffman only helps when the probabilities are unequal.', set: { list: 'a 0.25\nb 0.25\nc 0.25\nd 0.25' } },
      { t: 'Try the most common English letters. e and t get the shortest codes, as in Morse code.', set: { list: 'e 0.125\nt 0.093\na 0.081\no 0.075\ni 0.07\nn 0.067\ns 0.063\nh 0.06' } }
    ],
    steps: z => Math.max(1, NLZ.pairs(z.p.list).filter(r => r[1] > 0).slice(0, 8).length - 1) + 1,
    draw(z) {
      const { g, p } = z;
      const rows = NLZ.pairs(p.list).filter(r => r[1] > 0).slice(0, 8);
      if (rows.length < 2) return 'Give at least two symbols.';
      const tot = rows.reduce((a, r) => a + r[1], 0);
      const nodes = rows.map((r, i) => ({ s: r[0], p: r[1] / tot, ord: i, leaf: true }));
      let q = nodes.slice(), ord = nodes.length;
      const merges = [];
      while (q.length > 1) {
        q.sort((a, b) => (a.p - b.p) || (a.ord - b.ord));
        const x = q.shift(), y = q.shift();
        const [L, R] = x.ord < y.ord ? [x, y] : [y, x];
        const n = { s: '', p: x.p + y.p, ord: ord++, L, R, at: merges.length + 1 };
        merges.push(n); q.push(n);
      }
      const root = q[0];
      const codes = {};
      const walk = (n, c, d) => { n.d = d; if (n.leaf) { codes[n.s] = c || '0'; return; } walk(n.L, c + '0', d + 1); walk(n.R, c + '1', d + 1); };
      walk(root, '', 0);
      /* place leaves left to right in tree order, parents above the middle of their children */
      const leaves = []; const coll = n => { if (n.leaf) leaves.push(n); else { coll(n.L); coll(n.R); } }; coll(root);
      const depth = Math.max(...leaves.map(l => l.d));
      const gap = 528 / leaves.length;
      leaves.forEach((l, i) => { l.x = 16 + gap * (i + 0.5); });
      const lev = d => 36 + (depth - d) / Math.max(1, depth) * 0 + d * Math.min(52, 190 / Math.max(1, depth));
      const pos = n => { if (n.leaf) { n.y = 240; return; } pos(n.L); pos(n.R); n.x = (n.L.x + n.R.x) / 2; n.y = lev(n.d); };
      pos(root);
      const shown = n => n.leaf || n.at <= z.step;
      const edges = n => { if (n.leaf) return; edges(n.L); edges(n.R); if (shown(n)) { D.line(g, n.x, n.y, n.L.x, n.L.y, z.col.ink2, 1.6); D.line(g, n.x, n.y, n.R.x, n.R.y, z.col.ink2, 1.6); if (z.step >= z.n) { D.text(g, '0', (n.x + n.L.x) / 2 - 8, (n.y + n.L.y) / 2, { a: 'center', s: 11, b: true, c: z.col.cv }); D.text(g, '1', (n.x + n.R.x) / 2 + 8, (n.y + n.R.y) / 2, { a: 'center', s: 11, b: true, c: z.col.orange }); } } };
      edges(root);
      const dots = n => { if (!n.leaf) { dots(n.L); dots(n.R); } if (!shown(n)) return; const last = !n.leaf && n.at === z.step && z.step < z.n; D.circle(g, n.x, n.y, n.leaf ? 17 : 15, { fill: last ? z.col.orange : n.leaf ? z.col.cv : z.col.bg, stroke: z.col.line, w: 1.2 }); D.text(g, n.leaf ? n.s : fmt(n.p, 3), n.x, n.y + (n.leaf ? 1 : 1), { a: 'center', bl: 'middle', s: n.leaf ? fit(g, n.s, 28, 13) : 10, b: true, c: n.leaf || last ? '#fff' : z.col.ink }); };
      dots(root);
      leaves.forEach(l => { D.text(g, fmt(l.p, 3), l.x, 272, { a: 'center', s: 10.5, c: z.col.ink2 }); if (z.step >= z.n) D.text(g, codes[l.s], l.x, 290, { a: 'center', s: 12, b: true, mono: true, c: z.col.cv }); });
      const H = leaves.reduce((a, l) => a - l.p * log2(l.p), 0), Lbar = leaves.reduce((a, l) => a + l.p * codes[l.s].length, 0);
      const fixed = Math.ceil(log2(leaves.length));
      if (z.step < z.n) { const m = merges[z.step]; return z.step === 0 ? 'Start: every symbol is its own small tree. Press Step to merge the two least likely.' : `Merge ${z.step}: joined two items into a node of probability <b>${fmt(merges[z.step - 1].p, 3)}</b>. ${m ? 'Next, the two smallest remaining are joined again.' : ''}`; }
      return `Codes: ${leaves.map(l => `${esc(l.s)} = <b>${codes[l.s]}</b>`).join(', ')}. Average length = Σ p × length = <b>${fmt(Lbar, 3)} bits</b>, entropy H = <b>${fmt(H, 3)} bits</b>, a fixed length code needs ${fixed} bits. No code is the start of another, so a string of bits decodes in only one way.`;
    }
  });

  def('shannon', {
    title: "Shannon's approximations to English",
    sub: 'Text is generated from the statistics of a training passage. Raise the order and the output looks more and more like English.',
    W: 560, H: 200,
    params: [
      { k: 'unit', label: 'Unit', type: 'select', v: 'char', opts: [['char', 'letters (27 symbols: a to z and space)'], ['word', 'words']] },
      { k: 'n', label: 'Order (how many symbols of context plus one)', type: 'range', min: 0, max: 5, v: 2 },
      { k: 'len', label: 'Length to generate', type: 'range', min: 40, max: 300, step: 10, v: 160 },
      { k: 'seed', label: 'Random seed', type: 'range', min: 1, max: 99, v: 3 },
      { k: 'text', label: 'Training text', type: 'area', v: SAMPLE }
    ],
    tips: [
      { t: 'Order 0 picks each of the 27 symbols with equal chance. It is gibberish like Shannon\'s XFOML RXKHRJFF.', set: { unit: 'char', n: 0 } },
      { t: 'Order 1 uses letter frequencies only. You see many e, t and spaces, and word lengths start to look right.', set: { unit: 'char', n: 1 } },
      { t: 'Order 3 uses the two previous letters. Real words like the, and, of appear.', set: { unit: 'char', n: 3 } },
      { t: 'Switch to words, order 2. Pairs of words read naturally but the whole is meaningless, just like Shannon\'s second order word sample.', set: { unit: 'word', n: 2, len: 40 } },
      { t: 'Go to letters, order 5. The text copies long chunks of the training passage. That is over fitting: too little data for so much context.', set: { unit: 'char', n: 5 } }
    ],
    draw(z) {
      const { g, p } = z;
      const clean = String(p.text).toLowerCase().replace(/[^a-z\s]/g, ' ').replace(/\s+/g, ' ').trim();
      if (clean.length < 20) return 'Paste a longer training text.';
      const r = rng(p.seed * 104729);
      const word = p.unit === 'word';
      const seq = word ? clean.split(' ') : clean.split('');
      const alpha = word ? [...new Set(seq)] : 'abcdefghijklmnopqrstuvwxyz '.split('');
      const n = word ? Math.min(p.n, 3) : p.n;
      const ctxLen = Math.max(0, n - 1);
      const table = new Map();
      if (n >= 1) for (let i = ctxLen; i < seq.length; i++) {
        const k = seq.slice(i - ctxLen, i).join('\u0001');
        if (!table.has(k)) table.set(k, new Map());
        const m = table.get(k); m.set(seq[i], (m.get(seq[i]) || 0) + 1);
      }
      const pick = m => { let t = 0; m.forEach(v => t += v); let u = r() * t; for (const [k, v] of m) { u -= v; if (u <= 0) return k; } return [...m.keys()][0]; };
      const out = [];
      const start = Math.floor(r() * Math.max(1, seq.length - ctxLen));
      for (let i = 0; i < ctxLen; i++) out.push(seq[start + i]);
      const L = word ? Math.round(p.len / 5) : p.len;
      while (out.length < L) {
        if (n === 0) { out.push(alpha[Math.floor(r() * alpha.length)]); continue; }
        const k = out.slice(out.length - ctxLen).join('\u0001');
        const m = table.get(k);
        if (!m) { out.push(seq[Math.floor(r() * seq.length)]); continue; }
        out.push(pick(m));
      }
      const txt = (word ? out.join(' ') : out.join('')).toUpperCase();
      D.text(g, `${word ? 'Word' : 'Letter'} approximation of order ${n}${word && p.n > 3 ? ' (words stop at order 3)' : ''}`, 16, 24, { b: true, s: 13, c: z.col.ink });
      rr(g, 12, 36, 536, 154, 10, { fill: z.col.bg });
      wrap(g, txt, 24, 60, 512, { s: 13, mono: true, c: z.col.ink, lh: 20 });
      /* plug-in conditional entropy of the next symbol given the context, on the training text */
      let Hc = 0, N = 0;
      if (n === 0) Hc = log2(alpha.length);
      else { table.forEach(m => { let t = 0; m.forEach(v => t += v); m.forEach(v => { Hc -= v * log2(v / t); }); N += t; }); Hc /= N; }
      const Hmax = log2(alpha.length);
      return `Estimated entropy of the next ${word ? 'word' : 'letter'} with ${ctxLen} symbol${ctxLen === 1 ? '' : 's'} of context: <b>${fmt(Hc, 3)} bits</b> out of a maximum of log₂ ${alpha.length} = ${fmt(Hmax, 2)}. Redundancy 1 − H ÷ H<sub>max</sub> = <b>${fmt(100 * (1 - Hc / Hmax), 1)}%</b>. With a short training text, high orders look certain only because most contexts were seen once.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 3.3: two variables */
  const H2 = arr => arr.reduce((a, q) => a - (q > 0 ? q * log2(q) : 0), 0);
  def('jointent', {
    title: 'Joint entropy, conditional entropy and mutual information',
    sub: 'Set how X affects Y. The bars show how the joint uncertainty splits into what each variable keeps to itself and what they share.',
    W: 560, H: 290,
    params: [
      { k: 'xn', label: 'Names of X and its two values', type: 'text', v: 'weather: sunny, rainy' },
      { k: 'yn', label: 'Names of Y and its two values', type: 'text', v: 'umbrella: yes, no' },
      { k: 'px', label: 'P(first value of X)', type: 'range', min: 0, max: 1, step: 0.01, v: 0.6 },
      { k: 'a', label: 'P(first Y | first X)', type: 'range', min: 0, max: 1, step: 0.01, v: 0.2 },
      { k: 'b', label: 'P(first Y | second X)', type: 'range', min: 0, max: 1, step: 0.01, v: 0.9 }
    ],
    tips: [
      { t: 'Set both conditional probabilities to 0.48. Y no longer depends on X, the shared part I(X : Y) shrinks to 0, and H(X,Y) = H(X) + H(Y).', set: { a: 0.48, b: 0.48 } },
      { t: 'Set them to 0 and 1. Knowing X now fixes Y, so H(Y|X) = 0 and all of H(Y) is shared.', set: { a: 0, b: 1 } },
      { t: 'Load the studying and passing example: 60% study, 90% of those pass, 20% of the rest pass. I(X : Y) = 0.388 bits.', set: { xn: 'student: studies, does not', yn: 'result: pass, fail', px: 0.6, a: 0.9, b: 0.2 } },
      { t: 'Load practice problem P5: P(X = a) = 0.5, P(Y = 0 | a) = 0.5, P(Y = 0 | b) = 0.8. I(X : Y) is only 0.073 bits.', set: { xn: 'X: a, b', yn: 'Y: 0, 1', px: 0.5, a: 0.5, b: 0.8 } }
    ],
    draw(z) {
      const { g, p } = z;
      const parse = s => { const m = String(s).split(':'); const vals = (m[1] || 'x1, x2').split(',').map(t => t.trim()).filter(Boolean); return [m[0].trim() || 'X', vals[0] || 'v1', vals[1] || 'v2']; };
      const [XN, x1, x2] = parse(p.xn), [YN, y1, y2] = parse(p.yn);
      const J = [[p.px * p.a, p.px * (1 - p.a)], [(1 - p.px) * p.b, (1 - p.px) * (1 - p.b)]];
      const PX = [p.px, 1 - p.px], PY = [J[0][0] + J[1][0], J[0][1] + J[1][1]];
      const HX = H2(PX), HY = H2(PY), HXY = H2(J.flat()), HYgX = HXY - HX, HXgY = HXY - HY, I = HX + HY - HXY;
      /* joint table */
      const tx = 16, ty = 34, cw = 74, ch = 30;
      D.text(g, 'Joint probabilities p(x, y)', tx, 20, { b: true, s: 12.5, c: z.col.ink });
      [y1, y2].forEach((v, j) => D.text(g, v, tx + 92 + j * cw + cw / 2, ty + 14, { a: 'center', s: fit(g, v, cw - 6, 12), b: true, c: z.col.ink2 }));
      D.text(g, 'p(x)', tx + 92 + 2 * cw + 30, ty + 14, { a: 'center', s: 11.5, b: true, c: z.col.ink2 });
      [x1, x2].forEach((v, i) => {
        const y = ty + 22 + i * ch;
        D.text(g, v, tx + 86, y + ch / 2 + 4, { a: 'right', s: fit(g, v, 82, 12), b: true, c: z.col.ink2 });
        J[i].forEach((q, j) => { rr(g, tx + 92 + j * cw + 2, y + 2, cw - 4, ch - 4, 5, { fill: z.col.bg, stroke: z.col.line }); D.text(g, fmt(q, 3), tx + 92 + j * cw + cw / 2, y + ch / 2 + 4, { a: 'center', s: 12.5, mono: true, c: z.col.ink }); });
        D.text(g, fmt(PX[i], 3), tx + 92 + 2 * cw + 30, y + ch / 2 + 4, { a: 'center', s: 12, mono: true, c: z.col.ink2 });
      });
      const yr = ty + 22 + 2 * ch;
      D.text(g, 'p(y)', tx + 86, yr + 16, { a: 'right', s: 11.5, b: true, c: z.col.ink2 });
      PY.forEach((q, j) => D.text(g, fmt(q, 3), tx + 92 + j * cw + cw / 2, yr + 16, { a: 'center', s: 12, mono: true, c: z.col.ink2 }));
      /* entropy list */
      const lx = 360;
      [['H(X)', HX], ['H(Y)', HY], ['H(X, Y)', HXY], ['H(Y | X)', HYgX], ['H(X | Y)', HXgY], ['I(X : Y)', I]].forEach(([l, v], i) => {
        D.text(g, l, lx, 30 + i * 21, { s: 12.5, b: true, c: i === 5 ? z.col.orange : z.col.ink });
        D.text(g, `${fmt(v, 3)} bits`, 548, 30 + i * 21, { a: 'right', s: 12.5, mono: true, c: i === 5 ? z.col.orange : z.col.ink });
      });
      /* information diagram as aligned bars */
      const bx = 110, bw = 420, sc = bw / Math.max(HXY, 1e-9), by = 182;
      D.text(g, `H(${XN})`, bx - 8, by + 15, { a: 'right', s: fit(g, `H(${XN})`, 92, 12), b: true, c: z.col.ink });
      rr(g, bx, by, HXgY * sc, 22, 4, { fill: z.col.cv });
      rr(g, bx + HXgY * sc, by, I * sc, 22, 4, { fill: z.col.orange });
      D.text(g, `H(${YN})`, bx - 8, by + 47, { a: 'right', s: fit(g, `H(${YN})`, 92, 12), b: true, c: z.col.ink });
      rr(g, bx + HXgY * sc, by + 32, I * sc, 22, 4, { fill: z.col.orange });
      rr(g, bx + (HXgY + I) * sc, by + 32, HYgX * sc, 22, 4, { fill: z.col.purple });
      D.line(g, bx, by + 66, bx + HXY * sc, by + 66, z.col.ink2, 1.5);
      D.text(g, `H(X, Y) = ${fmt(HXY, 3)}`, bx + HXY * sc / 2, by + 82, { a: 'center', s: 11.5, b: true, c: z.col.ink2 });
      const lab = (t, x, w, y) => { if (w > tw(g, t, { s: 10.5, b: true }) + 6) D.text(g, t, x + w / 2, y, { a: 'center', s: 10.5, b: true, c: '#fff' }); };
      lab('H(X|Y)', bx, HXgY * sc, by + 15); lab('I', bx + HXgY * sc, I * sc, by + 15); lab('I', bx + HXgY * sc, I * sc, by + 47); lab('H(Y|X)', bx + (HXgY + I) * sc, HYgX * sc, by + 47);
      return `Chain rule: H(X) + H(Y|X) = ${fmt(HX, 3)} + ${fmt(HYgX, 3)} = <b>${fmt(HXY, 3)}</b> = H(X, Y). Knowing ${esc(XN)} lowers the uncertainty about ${esc(YN)} from ${fmt(HY, 3)} to ${fmt(HYgX, 3)} bits. The saving, <b>I(X : Y) = ${fmt(I, 3)} bits</b>, is the orange overlap, and it is the same in both directions.`;
    }
  });

  def('pmi', {
    title: 'Pointwise mutual information: which word pairs belong together',
    sub: 'Each line is a pair with three counts: c(x), c(y) and c(x y). PMI compares how often the pair occurs with how often chance alone would put them together.',
    W: 560, H: 270,
    params: [
      { k: 'N', label: 'Corpus size N (tokens)', type: 'range', min: 100000, max: 5000000, step: 100000, v: 1000000 },
      { k: 'list', label: 'x y c(x) c(y) c(x y), one pair per line', type: 'area', v: 'New Delhi 2000 500 400\nice cream 3000 2500 900\nwhite house 6000 4000 700\nnew car 2000 1000 20\nof the 40000 70000 10000\npowerful tea 800 600 0' },
      { k: 'min', label: 'Ignore pairs seen fewer than this many times', type: 'range', min: 0, max: 50, v: 0 }
    ],
    tips: [
      { t: 'Look at "of the". It is by far the most frequent pair, yet its PMI is only 1.84 bits: of and the are so common that they meet by chance.', set: {} },
      { t: 'Add a pair of two rare words seen once together: "zygote zebra 1 1 1". Its PMI is about 20 bits, higher than New Delhi. Raise the minimum count to 5 to remove it.', set: { list: 'New Delhi 2000 500 400\nice cream 3000 2500 900\nof the 40000 70000 10000\nzygote zebra 1 1 1' } },
      { t: 'Double N. Every PMI rises by exactly 1 bit, because the chance level halves. Compare scores only inside one corpus.', set: { N: 2000000 } }
    ],
    draw(z) {
      const { g, p } = z;
      const rows = String(p.list).split('\n').map(l => l.trim().split(/\s+/)).filter(a => a.length >= 5).map(a => { const n = a.slice(-3).map(Number); return { pair: a.slice(0, a.length - 3).join(' '), cx: n[0], cy: n[1], cxy: n[2] }; }).filter(r => r.cx > 0 && r.cy > 0).slice(0, 8);
      if (!rows.length) return 'Write lines like "New Delhi 2000 500 400".';
      rows.forEach(r => { r.pmi = r.cxy > 0 ? log2(r.cxy * p.N / (r.cx * r.cy)) : -Infinity; r.skip = r.cxy < p.min; });
      const fin = rows.filter(r => isFinite(r.pmi) && !r.skip).map(r => r.pmi);
      const pos = Math.max(1, ...fin), neg = Math.max(0, ...fin.map(v => -v));
      const x0 = neg > 0 ? 220 : 140, sc = Math.min(290 / pos, neg > 0 ? 90 / neg : Infinity);
      D.line(g, x0, 18, x0, 30 + rows.length * 28, z.col.ink2, 1.5);
      D.text(g, 'PMI in bits', x0, 14, { a: 'center', s: 11, b: true, c: z.col.ink2 });
      D.text(g, 'P(y | x)', 548, 14, { a: 'right', s: 11, b: true, c: z.col.ink2 });
      rows.forEach((r, i) => {
        const y = 26 + i * 28;
        D.text(g, r.pair, x0 - (neg > 0 ? 96 : 8), y + 15, { a: 'right', s: fit(g, r.pair, 110, 12.5), b: true, c: r.skip ? z.col.ink2 : z.col.ink });
        D.text(g, fmt(r.cxy / r.cx, 3), 548, y + 15, { a: 'right', s: 11, mono: true, c: z.col.ink2 });
        if (r.skip) { D.text(g, 'below the minimum count', x0 + 8, y + 15, { s: 11, c: z.col.ink2 }); return; }
        if (!isFinite(r.pmi)) { D.text(g, '−∞, never seen together', x0 + 8, y + 15, { s: 11, b: true, c: z.col.red }); return; }
        const w = r.pmi * sc;
        rr(g, w >= 0 ? x0 : x0 + w, y + 4, Math.max(2, Math.abs(w)), 18, 4, { fill: w >= 0 ? z.col.orange : z.col.purple });
        D.text(g, fmt(r.pmi, 2), w >= 0 ? x0 + w + 5 : x0 + 5, y + 17, { s: 11.5, b: true, c: z.col.ink });
      });
      const top = rows.filter(r => !r.skip && isFinite(r.pmi)).sort((a, b) => b.pmi - a.pmi)[0];
      return `PMI(x, y) = log₂ [ c(x y) × N ÷ (c(x) × c(y)) ]. Above 0 the words attract, at 0 they are independent, below 0 they avoid each other. ${top ? `The strongest pair is <b>${esc(top.pair)}</b> at ${fmt(top.pmi, 2)} bits: after x, y is ${fmt(top.cxy / top.cx / (top.cy / p.N), 1)} times more likely than usual.` : ''}`;
    }
  });

  def('kl', {
    title: 'KL divergence and cross entropy: the cost of the wrong model',
    sub: 'p is the truth, q is the model. Edit both. KL counts the extra bits per symbol you pay for coding p with a code built for q.',
    W: 560, H: 270,
    params: [
      { k: 'p', label: 'True distribution p (outcome and probability per line)', type: 'area', v: 'sunny 0.7\ncloudy 0.2\nrainy 0.1' },
      { k: 'q', label: 'Model q (same outcomes)', type: 'area', v: 'sunny 0.3\ncloudy 0.3\nrainy 0.4' }
    ],
    tips: [
      { t: 'Make q equal to p. Every bar meets its partner, KL is 0 and cross entropy equals entropy.', set: { q: 'sunny 0.7\ncloudy 0.2\nrainy 0.1' } },
      { t: 'Load the lecture example p = (0.5, 0.25, 0.25), q uniform. D(p‖q) = 0.085 but D(q‖p) = 0.082. KL is not symmetric.', set: { p: 'a 0.5\nb 0.25\nc 0.25', q: 'a 0.3333\nb 0.3333\nc 0.3334' } },
      { t: 'Give rainy probability 0 in the model. Any rainy day now costs infinitely many bits. This is why language models must be smoothed.', set: { q: 'sunny 0.5\ncloudy 0.5\nrainy 0' } }
    ],
    draw(z) {
      const { g, p } = z;
      const P = NLZ.pairs(p.p), Q = new Map(NLZ.pairs(p.q).map(r => [r[0], r[1]]));
      if (!P.length) return 'Write lines like "sunny 0.7".';
      const ps = P.reduce((a, r) => a + r[1], 0), qs = P.reduce((a, r) => a + (Q.get(r[0]) || 0), 0) || 1;
      const rows = P.slice(0, 8).map(r => ({ s: r[0], p: r[1] / ps, q: (Q.get(r[0]) || 0) / qs }));
      const Hp = rows.reduce((a, r) => a - (r.p > 0 ? r.p * log2(r.p) : 0), 0);
      const Hpq = rows.reduce((a, r) => a + (r.p > 0 ? (r.q > 0 ? -r.p * log2(r.q) : Infinity) : 0), 0);
      const Dpq = rows.reduce((a, r) => a + (r.p > 0 ? (r.q > 0 ? r.p * log2(r.p / r.q) : Infinity) : 0), 0);
      const Dqp = rows.reduce((a, r) => a + (r.q > 0 ? (r.p > 0 ? r.q * log2(r.q / r.p) : Infinity) : 0), 0);
      const gw = 300 / rows.length, bh = 170;
      D.text(g, 'p (truth)', 24, 18, { s: 11.5, b: true, c: z.col.cv });
      D.text(g, 'q (model)', 100, 18, { s: 11.5, b: true, c: z.col.orange });
      rows.forEach((r, i) => {
        const x = 20 + i * gw, base = 206;
        rr(g, x + gw * 0.12, base - r.p * bh, gw * 0.36, Math.max(1, r.p * bh), 3, { fill: z.col.cv });
        rr(g, x + gw * 0.52, base - r.q * bh, gw * 0.36, Math.max(1, r.q * bh), 3, { fill: z.col.orange });
        D.text(g, r.s, x + gw / 2, base + 16, { a: 'center', s: fit(g, r.s, gw - 4, 12), b: true, c: z.col.ink });
        const term = r.p > 0 ? (r.q > 0 ? r.p * log2(r.p / r.q) : Infinity) : 0;
        D.text(g, fmt(term, 3), x + gw / 2, base + 34, { a: 'center', s: 11, mono: true, c: term < 0 ? z.col.purple : z.col.ink2 });
      });
      D.text(g, 'term p log₂(p/q)', 20, 258, { s: 10.5, c: z.col.ink2 });
      const lx = 350;
      [['H(p)', Hp], ['H(p, q)', Hpq], ['D(p ‖ q)', Dpq], ['D(q ‖ p)', Dqp]].forEach(([l, v], i) => {
        rr(g, lx, 26 + i * 50, 198, 40, 8, { fill: i === 2 ? z.col.orange : z.col.bg });
        D.text(g, l, lx + 12, 51 + i * 50, { s: 13, b: true, c: i === 2 ? '#fff' : z.col.ink });
        D.text(g, `${fmt(v, 4)} bits`, lx + 186, 51 + i * 50, { a: 'right', s: 13, mono: true, b: true, c: i === 2 ? '#fff' : z.col.ink });
      });
      return `Cross entropy = entropy + KL: ${fmt(Hpq, 4)} = ${fmt(Hp, 4)} + ${fmt(Dpq, 4)}. Single terms can be negative (purple) but the total D(p‖q) never is, by Gibbs' inequality. Swapping p and q changes the value, so KL is not a distance. A language model trained by cross entropy loss is pushed to lower exactly this KL.`;
    }
  });

  def('noisychannel', {
    title: 'The noisy channel: correcting a typo',
    sub: 'For each candidate, multiply how common the word is (the language model) by how likely this typo is from it (the channel model). The largest product wins.',
    W: 560, H: 200,
    params: [
      { k: 'obs', label: 'What was typed', type: 'text', v: 'acress' },
      { k: 'list', label: 'Candidate, P(word), P(typo | word), one per line', type: 'area', v: 'actress 1.4e-5 1.2e-4\nacross 2.9e-4 2.1e-6\nacres 3.2e-5 3.1e-5\naccess 1.8e-4 1.0e-6' },
      { k: 'ctx', label: 'Context boost: multiply P(word) of the first candidate by', type: 'range', min: 0.1, max: 10, step: 0.1, v: 1 }
    ],
    tips: [
      { t: 'Ignore the channel by giving every candidate the same P(typo | word). Now the most common word, across, wins. The channel model is what saves actress.', set: { list: 'actress 1.4e-5 1e-5\nacross 2.9e-4 1e-5\nacres 3.2e-5 1e-5\naccess 1.8e-4 1e-5' } },
      { t: 'Imagine the context "a versatile ___". Boost actress by 5 and its share of the posterior rises from 0.485 to about 0.825.', set: { ctx: 5 } },
      { t: 'Imagine a context where actress is unlikely. A boost of 0.2 drops it below acres, which now wins.', set: { ctx: 0.2 } }
    ],
    draw(z) {
      const { g, p } = z;
      const rows = String(p.list).split('\n').map(l => l.trim().split(/[\s,]+/)).filter(a => a.length >= 3).map(a => ({ w: a[0], pw: +a[1], po: +a[2] })).filter(r => r.pw > 0 && r.po >= 0).slice(0, 6);
      if (!rows.length) return 'Write lines like "actress 1.4e-5 1.2e-4".';
      rows[0].pw *= p.ctx;
      rows.forEach(r => { r.s = r.pw * r.po; });
      const tot = rows.reduce((a, r) => a + r.s, 0) || 1;
      const best = rows.reduce((a, r) => r.s > a.s ? r : a, rows[0]);
      pill(g, `typed: ${p.obs}`, 16, 10, { s: 13, b: true, mono: true, fill: z.col.red, c: '#fff' });
      const cols = [['P(word)', 'pw', z.col.cv], ['P(typo | word)', 'po', z.col.purple], ['share of P(word | typo)', 'sh', z.col.orange]];
      const x0 = 110, cw = 146;
      cols.forEach((c, j) => D.text(g, c[0], x0 + j * cw + cw / 2, 56, { a: 'center', s: 11.5, b: true, c: z.col.ink2 }));
      const mxs = { pw: Math.max(...rows.map(r => r.pw)), po: Math.max(...rows.map(r => r.po), 1e-30), sh: 1 };
      rows.forEach((r, i) => {
        const y = 66 + i * 30;
        r.sh = r.s / tot;
        D.text(g, r.w, x0 - 10, y + 17, { a: 'right', s: fit(g, r.w, 90, 13), b: r === best, mono: true, c: r === best ? z.col.orange : z.col.ink });
        cols.forEach((c, j) => {
          const v = r[c[1]], w = Math.max(2, v / mxs[c[1]] * (cw - 64));
          rr(g, x0 + j * cw, y + 6, w, 16, 4, { fill: c[2] });
          D.text(g, c[1] === 'sh' ? fmt(v, 3) : v.toExponential(1), x0 + j * cw + w + 4, y + 18, { s: 10.5, c: z.col.ink2 });
        });
      });
      return `Best correction: <b>${esc(best.w)}</b>, with P(word) × P(typo | word) = ${best.s.toExponential(2)} and a posterior share of <b>${fmt(best.sh, 3)}</b>. Bayes' rule gives P(word | typo) = P(word) P(typo | word) ÷ P(typo). P(typo) is the same for every candidate, so it can be dropped when choosing the winner.`;
    }
  });
})();

/* ===== Step 4: n-gram language models, perplexity and smoothing ===== */
(() => {
  const { def, D, esc } = CVZ;
  const { tw, rr, pill, wrap, fit, log2, fmt } = NLZ;

  /* the five sentence corpus of the in-class activity (adapted from Jurafsky and Martin) */
  const TOY = 'I am Sam\nSam I am\nSam I like\nSam I do like\ndo I like Sam';
  NLZ.TOY = TOY;
  const toks = s => String(s).trim().split(/\s+/).filter(Boolean);
  const lines = s => String(s).split('\n').map(toks).filter(a => a.length);
  const g6 = v => !isFinite(v) ? (v > 0 ? 'inf' : '-inf') : String(Number(v.toPrecision(6)));
  const L10 = Math.log10;
  /* 9.6 × 10⁻³ style, for the readouts */
  const sci = v => { if (!(v > 0)) return String(v); const e = Math.floor(Math.log10(v)); return e > -3 && e < 4 ? fmt(v, 5) : `${(v / 10 ** e).toFixed(4)} × 10<sup>${String(e).replace('-', '−')}</sup>`; };

  /* count every order from 1 to maxN. Order m pads each sentence with m − 1 start tags and one end tag.
     <s> is only ever context, </s> is predicted, exactly as in class and in SRILM */
  function train(text, maxN) {
    const sents = lines(text);
    const C = [];
    for (let m = 1; m <= maxN; m++) {
      const ng = new Map(), hist = new Map(), foll = new Map();
      sents.forEach(s => {
        const t = Array(m - 1).fill('<s>').concat(s, ['</s>']);
        for (let i = m - 1; i < t.length; i++) {
          const h = t.slice(i - m + 1, i).join(' '), key = h + '|' + t[i];
          ng.set(key, (ng.get(key) || 0) + 1);
          hist.set(h, (hist.get(h) || 0) + 1);
          if (!foll.has(h)) foll.set(h, new Map());
          foll.get(h).set(t[i], (foll.get(h).get(t[i]) || 0) + 1);
        }
      });
      C[m] = { ng, hist, foll };
    }
    const words = [];
    sents.flat().forEach(w => { if (!words.includes(w)) words.push(w); });
    return { sents, C, words, N: C[1].hist.get('') || 0 };
  }
  NLZ.lmTrain = train;
  /* add-k estimate of P(w | h) from the counts of order h.length + 1. k = 0 is the plain MLE */
  function est(lm, h, w, k, V) {
    const c = lm.C[h.length + 1], hs = h.join(' ');
    const n = c.ng.get(hs + '|' + w) || 0, d = c.hist.get(hs) || 0;
    return { p: d + k * V > 0 ? (n + k) / (d + k * V) : 0, n, d };
  }
  /* score every test sentence. o = { n, k, unk, lam, ku }. lam null means no interpolation */
  function score(lm, test, o) {
    const vocab = new Set(lm.words.concat(['</s>']));
    if (o.unk) vocab.add('<unk>');
    const V = vocab.size;
    const out = lines(test).map(ws => {
      let hist = Array(o.n - 1).fill('<s>');
      const f = [];
      ws.concat(['</s>']).forEach(w => {
        let w2 = w;
        if (!vocab.has(w)) {
          if (o.unk) w2 = '<unk>';
          else { f.push({ w, oov: true, h: o.n > 1 ? hist.slice(-(o.n - 1)) : [] }); hist = []; return; }
        }
        const h = o.n > 1 ? hist.slice(-(o.n - 1)) : [];
        const r = est(lm, h, w2, o.k, V);
        let p = r.p, u = null;
        if (o.lam != null) { u = est(lm, [], w2, o.ku, V).p; p = o.lam * r.p + (1 - o.lam) * u; }
        f.push({ w, w2, h, m: h.length + 1, n: r.n, d: r.d, pn: r.p, u, p });
        hist.push(w2);
      });
      const words = ws.length, oov = f.filter(x => x.oov).length, zero = f.filter(x => !x.oov && x.p === 0).length;
      const lp = f.reduce((a, x) => a + (!x.oov && x.p > 0 ? L10(x.p) : 0), 0);
      return { ws, f, words, oov, zero, lp };
    });
    const tot = { sents: out.length, words: 0, oov: 0, zero: 0, lp: 0 };
    out.forEach(s => { tot.words += s.words; tot.oov += s.oov; tot.zero += s.zero; tot.lp += s.lp; });
    const pp = (lp, words, oov, zero, sents) => ({ ppl: 10 ** (-lp / (words - oov - zero + sents)), ppl1: 10 ** (-lp / Math.max(1, words - oov - zero)) });
    out.forEach(s => Object.assign(s, pp(s.lp, s.words, s.oov, s.zero, 1)));
    Object.assign(tot, pp(tot.lp, tot.words, tot.oov, tot.zero, tot.sents));
    return { out, tot, V };
  }
  NLZ.lmScore = score;
  const ctx = h => h.length ? h.join(' ') : '';
  const label = x => `P(${x.w}${x.w2 && x.w2 !== x.w ? '→' + x.w2 : ''}${x.h.length ? ' | ' + ctx(x.h) : ''})`;

  /* ---------------------------------------------------------------- the n-gram model and its SRILM printout */
  def('ngramlm', {
    title: 'Train an n-gram model and score a sentence',
    sub: 'The model is trained on the corpus on the left. Each test word becomes one factor of the chain rule, read straight from the counts.',
    W: 560, H: 300,
    params: [
      { k: 'train', label: 'Training corpus (one sentence per line, tags are added for you)', type: 'area', v: TOY },
      { k: 'test', label: 'Test sentences (one per line)', type: 'area', v: 'Sam I do I like' },
      { k: 'n', label: 'Model order n', type: 'select', v: '2', opts: [['1', 'unigram (n = 1)'], ['2', 'bigram (n = 2)'], ['3', 'trigram (n = 3)']] },
      { k: 'k', label: 'Add-k smoothing k (0 is plain counting, 1 is Laplace)', type: 'range', min: 0, max: 2, step: 0.01, v: 0 },
      { k: 'unk', label: 'Map unseen words to &lt;unk&gt;', type: 'check', v: false },
      { k: 'mix', label: 'Interpolate with a unigram model', type: 'check', v: false },
      { k: 'lam', label: 'λ, the weight of the n-gram', type: 'range', min: 0, max: 1, step: 0.01, v: 0.7, show: p => p.mix },
      { k: 'ku', label: 'Add-k for that unigram', type: 'range', min: 0, max: 2, step: 0.01, v: 1, show: p => p.mix },
      { k: 'view', label: 'Show', type: 'select', v: 'table', opts: [['table', 'the factors as a table'], ['srilm', 'the output of ngram -ppl -debug 2']] }
    ],
    tips: [
      { t: 'Question 1 of the activity: type "Sam I am" as a second test line. The file total is −3.16040 and ppl 2.07033, exactly SRILM\'s last line.', set: { test: 'Sam I do I like\nSam I am', n: '2', k: 0, unk: false, mix: false } },
      { t: 'Question 2: switch to the unigram. S1 drops to 3.3 × 10⁻⁵ because word order no longer helps.', set: { test: 'Sam I do I like\nSam I am', n: '1', k: 0, mix: false } },
      { t: 'Question 3: test "Sam I do like linguistics" with the bigram, then tick &lt;unk&gt;. Without &lt;unk&gt; SRILM skips the word as an OOV. With it, plain counting gives probability 0.', set: { test: 'Sam I do like linguistics', n: '2', k: 0, unk: false, mix: false } },
      { t: 'Laplace bigram: tick &lt;unk&gt; and set k to 1. The sentence gets 1/17010 and PP 5.07.', set: { test: 'Sam I do like linguistics', n: '2', k: 1, unk: true, mix: false } },
      { t: 'Interpolation: k = 0, mix with a Laplace unigram at λ = 0.7. P ≈ 9.99 × 10⁻⁶ and PP ≈ 6.81, nothing is zero any more.', set: { test: 'Sam I do like linguistics', n: '2', k: 0, unk: true, mix: true, lam: 0.7, ku: 1 } },
      { t: 'Trigram on "Sam I do I like": the factor P(I | I do) is 0 because "I do I" never occurred, although both bigrams did.', set: { test: 'Sam I do I like', n: '3', k: 0, unk: false, mix: false } },
      { t: 'See the same numbers as the toolkit prints them.', set: { test: 'Sam I do I like\nSam I am', n: '2', k: 0, unk: false, mix: false, view: 'srilm' } }
    ],
    draw(z) {
      const { g, p } = z;
      const n = +p.n, lm = train(p.train, n);
      if (!lm.sents.length) return 'Type at least one training sentence.';
      const r = score(lm, p.test, { n, k: p.k, unk: p.unk, lam: p.mix ? p.lam : null, ku: p.ku });
      if (!r.out.length) return 'Type a test sentence.';
      const T = r.tot;
      if (p.view === 'srilm') {
        const L = [];
        r.out.forEach(s => {
          L.push([s.ws.join(' '), z.col.ink, true]);
          s.f.forEach(x => {
            const c = x.h.length ? (x.h.length > 1 ? x.h[x.h.length - 1] + ' ...' : x.h[0]) : '';
            if (x.oov) L.push([`    p( ${x.w} | ${c} )  = [OOV] 0 [ -inf ]`, z.col.red]);
            else L.push([`    p( ${x.w2} | ${c} )  = [${x.m}gram] ${g6(x.p)} [ ${x.p > 0 ? g6(L10(x.p)) : '-inf'} ]`, x.p > 0 ? z.col.ink : z.col.red]);
          });
          L.push([`1 sentences, ${s.words} words, ${s.oov} OOVs`, z.col.ink2]);
          L.push([`${s.zero} zeroprobs, logprob= ${g6(s.lp)} ppl= ${g6(s.ppl)} ppl1= ${g6(s.ppl1)}`, z.col.cv, true]);
          L.push(['', z.col.ink]);
        });
        L.push([`file test.txt: ${T.sents} sentences, ${T.words} words, ${T.oov} OOVs`, z.col.ink2]);
        L.push([`${T.zero} zeroprobs, logprob= ${g6(T.lp)} ppl= ${g6(T.ppl)} ppl1= ${g6(T.ppl1)}`, z.col.orange, true]);
        rr(g, 8, 8, z.W - 16, z.H - 16, 10, { fill: z.col.bg, stroke: z.col.line });
        const lh = Math.min(17, (z.H - 36) / L.length);
        const fs = Math.min(12, lh - 3);
        L.forEach(([s, c, b], i) => { if (s) D.text(g, s, 22, 30 + i * lh, { s: fit(g, s, z.W - 44, fs, { mono: true }), mono: true, c, b }); });
      } else {
        const rows = [];
        r.out.forEach((s, i) => { if (i) rows.push(null); s.f.forEach(x => rows.push(x)); });
        const cols = [16, 222, 380, 470, 548];
        ['factor', 'counts used', 'value', 'log₁₀'].forEach((t, i) => D.text(g, t, i < 2 ? cols[i] : (i === 2 ? 452 : cols[4]), 20, { a: i < 2 ? 'left' : 'right', s: 11.5, b: true, c: z.col.ink2 }));
        const maxRows = 11, rh = Math.min(21, 232 / Math.max(1, Math.min(rows.length, maxRows)));
        rows.slice(0, maxRows).forEach((x, i) => {
          const y = 30 + i * rh;
          if (!x) { D.line(g, 16, y + rh / 2, 548, y + rh / 2, z.col.line, 1, [4, 4]); return; }
          const lab = label(x);
          D.text(g, lab, cols[0], y + rh * 0.7, { s: fit(g, lab, 200, 12.5), b: true, c: x.oov ? z.col.red : z.col.ink });
          if (x.oov) { D.text(g, 'not in the vocabulary: skipped as an OOV', cols[1], y + rh * 0.7, { s: 11.5, c: z.col.red }); return; }
          let cu;
          if (p.mix) cu = `${fmt(p.lam, 2)}×${fmt(x.pn, 3)} + ${fmt(1 - p.lam, 2)}×${fmt(x.u, 3)}`;
          else if (p.k > 0) cu = `(${x.n} + ${fmt(p.k, 2)}) ÷ (${x.d} + ${fmt(p.k, 2)}×${r.V})`;
          else cu = x.d ? `${x.n} ÷ ${x.d}` : `${x.n} ÷ 0, history never seen`;
          D.text(g, cu, cols[1], y + rh * 0.7, { s: fit(g, cu, 150, 11.5, { mono: true }), mono: true, c: z.col.ink2 });
          rr(g, 380, y + 4, Math.max(1.5, x.p * 30), rh - 8, 3, { fill: x.p > 0 ? z.col.cv : z.col.red });
          D.text(g, fmt(x.p, 4), 452, y + rh * 0.7, { a: 'right', s: 12, mono: true, c: x.p > 0 ? z.col.ink : z.col.red, b: x.p === 0 });
          D.text(g, x.p > 0 ? fmt(L10(x.p), 5) : '−∞', 548, y + rh * 0.7, { a: 'right', s: 12, mono: true, c: x.p > 0 ? z.col.ink : z.col.red });
        });
        if (rows.length > maxRows) D.text(g, `and ${rows.length - maxRows} more rows. Shorten the test to see them all.`, 16, 30 + maxRows * rh + 12, { s: 11, c: z.col.ink2 });
        const y = z.H - 14;
        const hand = T.zero ? 'P = 0, so log₁₀ P = −∞ and PP = ∞' : `log₁₀ P = ${fmt(T.lp, 5)}    PP = ${fmt(T.ppl, 4)}    PP1 = ${fmt(T.ppl1, 4)}`;
        rr(g, 8, y - 20, z.W - 16, 28, 8, { fill: T.zero ? z.col.red : z.col.cv });
        D.text(g, hand, z.W / 2, y - 1, { a: 'center', s: fit(g, hand, z.W - 40, 13.5), b: true, c: '#fff' });
      }
      const s0 = r.out[0];
      const P = s0.zero ? 0 : 10 ** s0.lp;
      let msg = `Vocabulary V = ${r.V} (${lm.words.length} words, &lt;/s&gt;${p.unk ? ' and &lt;unk&gt;' : ''}). Training tokens N = ${lm.N}. `;
      if (r.out.length === 1) msg += `P(sentence) = <b>${s0.oov && !s0.zero ? 'not defined without &lt;unk&gt;' : P === 0 ? '0' : sci(P)}</b> over ${s0.words} words + &lt;/s&gt;. `;
      else msg += `File: ${T.sents} sentences, ${T.words} words, logprob <b>${fmt(T.lp, 5)}</b>, ppl <b>${fmt(T.ppl, 5)}</b>, ppl1 ${fmt(T.ppl1, 5)}. The file perplexity is not the average of the sentence perplexities. `;
      if (T.oov) msg += `SRILM skips the ${T.oov} OOV word${T.oov > 1 ? 's' : ''} and scores the rest, so its perplexity is not comparable with a run that has no OOVs. `;
      if (T.zero) msg += `By hand one zero factor makes the whole product 0. SRILM instead reports ${T.zero} zeroprob${T.zero > 1 ? 's' : ''}, leaves ${T.zero > 1 ? 'them' : 'it'} out and prints ppl ${fmt(T.ppl, 4)}. `;
      if (p.k > 0 && n > 1) msg += 'With add-k every unseen n-gram gets a share. SRILM\'s own -addsmooth backs off for unseen n-grams, so its numbers can differ slightly from this textbook form.';
      return msg;
    }
  });

  /* ---------------------------------------------------------------- the bigram table */
  def('bigramtable', {
    title: 'The bigram table: counts, probabilities and zeros',
    sub: 'Rows are the previous word (the history), columns the next word. Every row of probabilities adds up to 1. Red cells are bigrams never seen.',
    W: 560, H: 300,
    params: [
      { k: 'train', label: 'Training corpus (one sentence per line)', type: 'area', v: TOY },
      { k: 'view', label: 'Show', type: 'select', v: 'count', opts: [['count', 'counts C(h w)'], ['mle', 'MLE probabilities C(h w) ÷ C(h)'], ['addk', 'add-k probabilities']] },
      { k: 'k', label: 'k for add-k', type: 'range', min: 0.01, max: 2, step: 0.01, v: 1, show: p => p.view === 'addk' },
      { k: 'unk', label: 'Add an &lt;unk&gt; row and column', type: 'check', v: false },
      { k: 'row', label: 'Highlight the row of the history', type: 'text', v: 'I' }
    ],
    tips: [
      { t: 'Count the red cells: 22 of the 36 bigrams never occur, even in a corpus built from six words. Real corpora are far sparser.', set: { view: 'count', unk: false } },
      { t: 'Switch to MLE and read the row of I: am 2/5, like 2/5, do 1/5. The row sums to 1 because every I is followed by exactly one token.', set: { view: 'mle', row: 'I' } },
      { t: 'Choose add-k with k = 1 and tick &lt;unk&gt;. No cell is 0 any more, and the row of do becomes 2/9 for I and like, 1/9 for the rest.', set: { view: 'addk', k: 1, unk: true, row: 'do' } },
      { t: 'Lower k to 0.05. The table moves back towards the counts, while unseen cells keep a small share.', set: { view: 'addk', k: 0.05, unk: true } }
    ],
    draw(z) {
      const { g, p } = z;
      const lm = train(p.train, 2);
      if (!lm.sents.length) return 'Type at least one training sentence.';
      const W = lm.words.slice(0, 8);
      const rowsL = ['<s>'].concat(W, p.unk ? ['<unk>'] : []), colsL = W.concat(['</s>'], p.unk ? ['<unk>'] : []);
      const V = colsL.length;
      const c = lm.C[2];
      const x0 = 74, y0 = 40, cw = Math.min(64, (z.W - x0 - 56) / colsL.length), ch = Math.min(28, (z.H - y0 - 20) / rowsL.length);
      D.text(g, 'next word →', x0, 16, { s: 11, b: true, c: z.col.ink2 });
      D.text(g, 'history ↓', 8, 16, { s: 11, b: true, c: z.col.ink2 });
      colsL.forEach((w, j) => D.text(g, w, x0 + j * cw + cw / 2, y0 - 8, { a: 'center', s: fit(g, w, cw - 4, 12), b: true, mono: true, c: z.col.ink }));
      D.text(g, p.view === 'count' ? 'C(h)' : 'sum', x0 + V * cw + 26, y0 - 8, { a: 'center', s: 11, b: true, c: z.col.ink2 });
      let zeros = 0, cells = 0;
      const hi = String(p.row).trim();
      rowsL.forEach((h, i) => {
        const y = y0 + i * ch, d = c.hist.get(h) || 0;
        if (h === hi) rr(g, 4, y, x0 + V * cw + 54, ch, 6, { fill: z.col.hl || z.col.bg });
        D.text(g, h, x0 - 8, y + ch / 2 + 4, { a: 'right', s: fit(g, h, x0 - 12, 12), b: true, mono: true, c: z.col.ink });
        let sum = 0;
        colsL.forEach((w, j) => {
          const n = c.ng.get(h + '|' + w) || 0;
          cells++; if (!n) zeros++;
          let v, s;
          if (p.view === 'count') { v = n; s = String(n); }
          else if (p.view === 'mle') { v = d ? n / d : 0; s = d ? (n ? `${n}/${d}` : '0') : '–'; }
          else { v = (n + p.k) / (d + p.k * V); s = fmt(v, 3).replace(/^0\./, '.'); }
          sum += p.view === 'count' ? n : v;
          const x = x0 + j * cw;
          const mx = p.view === 'count' ? 5 : 1;
          g.save(); g.globalAlpha = 0.1 + 0.75 * Math.min(1, v / mx);
          rr(g, x + 2, y + 2, cw - 4, ch - 4, 4, { fill: n ? z.col.cv : (p.view === 'addk' ? z.col.orange : z.col.red) });
          g.restore();
          if (!n && p.view !== 'addk') rr(g, x + 2, y + 2, cw - 4, ch - 4, 4, { stroke: z.col.red, dash: [3, 3], w: 1 });
          D.text(g, s, x + cw / 2, y + ch / 2 + 4, { a: 'center', s: fit(g, s, cw - 6, 12), mono: true, b: !!n, c: n ? z.col.ink : z.col.red });
        });
        D.text(g, p.view === 'count' ? String(d) : (d || p.view === 'addk' ? fmt(sum, 3) : '–'), x0 + V * cw + 26, y + ch / 2 + 4, { a: 'center', s: 12, mono: true, b: true, c: z.col.ink2 });
      });
      const rowH = rowsL.indexOf(hi);
      let extra = '';
      if (rowH >= 0) {
        const d = c.hist.get(hi) || 0;
        const f = colsL.filter(w => c.ng.get(hi + '|' + w)).map(w => `${esc(w)} ${c.ng.get(hi + '|' + w)}`);
        extra = d ? ` The history <b>${esc(hi)}</b> occurs ${d} times as a history and is followed by ${f.join(', ')}.` : ` The history ${esc(hi)} never occurs, so its MLE row is undefined (0 ÷ 0).`;
      }
      return `<b>${zeros}</b> of ${cells} cells have a count of 0 (${Math.round(100 * zeros / cells)}%). The row total C(h) is the denominator of every probability in the row: P(w | h) = C(h w) ÷ C(h).${extra}${p.view === 'addk' ? ` Add-k divides by C(h) + kV with V = ${V}.` : ''}`;
    }
  });

  /* curved arrow between two circles. Returns the middle point of the curve for a label */
  function carc(g, x1, y1, x2, y2, r, b, c, w) {
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1;
    const cx = mx - dy / L * b, cy = my + dx / L * b;
    const a1 = Math.atan2(cy - y1, cx - x1), a2 = Math.atan2(cy - y2, cx - x2);
    const sx = x1 + Math.cos(a1) * r, sy = y1 + Math.sin(a1) * r, ex = x2 + Math.cos(a2) * (r + 2), ey = y2 + Math.sin(a2) * (r + 2);
    g.save(); g.strokeStyle = c; g.fillStyle = c; g.lineWidth = w;
    g.beginPath(); g.moveTo(sx, sy); g.quadraticCurveTo(cx, cy, ex, ey); g.stroke();
    const an = Math.atan2(ey - cy, ex - cx), h = 7 + w;
    g.beginPath(); g.moveTo(ex, ey); g.lineTo(ex - h * Math.cos(an - 0.42), ey - h * Math.sin(an - 0.42)); g.lineTo(ex - h * Math.cos(an + 0.42), ey - h * Math.sin(an + 0.42)); g.closePath(); g.fill();
    g.restore();
    return [0.25 * sx + 0.5 * cx + 0.25 * ex, 0.25 * sy + 0.5 * cy + 0.25 * ey];
  }
  NLZ.carc = carc;
  /* a self loop drawn outside the circle in direction ang */
  function loop(g, x, y, r, ang, c, w) {
    const lx = x + Math.cos(ang) * (r + 13), ly = y + Math.sin(ang) * (r + 13);
    g.save(); g.strokeStyle = c; g.fillStyle = c; g.lineWidth = w;
    g.beginPath(); g.arc(lx, ly, 15, ang + Math.PI + 1.05, ang + Math.PI - 1.05 + 2 * Math.PI); g.stroke();
    const ea = ang + Math.PI - 1.05, ex = lx + Math.cos(ea) * 15, ey = ly + Math.sin(ea) * 15, t = ea - Math.PI / 2, h = 7 + w;
    g.beginPath(); g.moveTo(ex, ey); g.lineTo(ex - h * Math.cos(t - 0.42), ey - h * Math.sin(t - 0.42)); g.lineTo(ex - h * Math.cos(t + 0.42), ey - h * Math.sin(t + 0.42)); g.closePath(); g.fill();
    g.restore();
    return [x + Math.cos(ang) * (r + 40), y + Math.sin(ang) * (r + 40)];
  }
  NLZ.loop = loop;

  /* ---------------------------------------------------------------- Markov chain */
  def('markov', {
    title: 'A bigram model drawn as a Markov chain',
    sub: 'Each word is a state, each arrow the probability of the next word. Press Play to walk the sentence one factor at a time.',
    W: 560, H: 300,
    params: [
      { k: 'names', label: 'The three states', type: 'text', v: 'He, cool, is' },
      { k: 'pi', label: 'Start probabilities π, in the same order', type: 'text', v: '0.7, 0.1, 0.2' },
      { k: 'T', label: 'Transitions: one row per state, P(next | this state)', type: 'area', v: '0.1 0.3 0.6\n0.2 0 0.8\n0.5 0.5 0' },
      { k: 'seq', label: 'Sentence to score', type: 'text', v: 'is He cool' }
    ],
    steps: z => toks(z.p.seq).length, startAtZero: true,
    tips: [
      { t: 'Press Play on "is He cool": 0.2 × 0.5 × 0.3 = 0.03, the value on the slide.', set: { seq: 'is He cool' }, play: true },
      { t: 'Score "He is He" and "He is cool". Both give 0.21, a tie for the most probable three word string.', set: { seq: 'He is cool' }, play: true },
      { t: 'Try "cool cool is". The arrow cool → cool has probability 0, so the whole product is 0.', set: { seq: 'cool cool is' }, play: true },
      { t: 'Change the row of He to 0.1 0.3 0.7. It now adds to 1.1, which a probability row must never do. The readout warns you.', set: { T: '0.1 0.3 0.7\n0.2 0 0.8\n0.5 0.5 0' } }
    ],
    draw(z) {
      const { g, p } = z;
      const S = String(p.names).split(',').map(s => s.trim()).filter(Boolean).slice(0, 3);
      while (S.length < 3) S.push('s' + (S.length + 1));
      const pi = NLZ.nums(p.pi).slice(0, 3); while (pi.length < 3) pi.push(0);
      const T = String(p.T).split('\n').map(l => NLZ.nums(l).slice(0, 3)).filter(r => r.length).slice(0, 3);
      while (T.length < 3) T.push([0, 0, 0]);
      T.forEach(r => { while (r.length < 3) r.push(0); });
      const P = [[110, 200], [300, 200], [205, 72]], R = 30;
      const seq = toks(p.seq), idx = seq.map(w => S.indexOf(w));
      const used = new Set();
      for (let i = 1; i < Math.min(z.step, seq.length); i++) used.add(idx[i - 1] + ',' + idx[i]);
      const cen = [205, 157];
      /* edges */
      const labs = [];
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
        const v = T[i][j]; if (!(v > 0)) continue;
        const on = used.has(i + ',' + j), col = on ? z.col.orange : z.col.ink2, w = on ? 3.2 : 1 + 2 * v;
        let at;
        if (i === j) at = loop(g, P[i][0], P[i][1], R, Math.atan2(P[i][1] - cen[1], P[i][0] - cen[0]), col, w);
        else at = carc(g, P[i][0], P[i][1], P[j][0], P[j][1], R, 22, col, w);
        labs.push([fmt(v, 3), at, on]);
      }
      labs.forEach(([t, [x, y], on]) => { const w = tw(g, t, { s: 11.5, b: true }) + 10; rr(g, x - w / 2, y - 10, w, 20, 6, { fill: on ? z.col.orange : z.col.surf, stroke: on ? z.col.orange : z.col.line, w: 1 }); D.text(g, t, x, y + 4, { a: 'center', s: 11.5, b: true, c: on ? '#fff' : z.col.ink }); });
      /* start arrows */
      const st = [[22, 268], [388, 268], [118, 26]];
      P.forEach(([x, y], i) => {
        if (!(pi[i] > 0)) return;
        const on = z.step >= 1 && idx[0] === i;
        D.arrow(g, st[i][0], st[i][1], x + (st[i][0] - x) * R / Math.hypot(st[i][0] - x, st[i][1] - y), y + (st[i][1] - y) * R / Math.hypot(st[i][0] - x, st[i][1] - y), on ? z.col.orange : z.col.purple, on ? 3 : 1.6);
        D.text(g, `π ${fmt(pi[i], 3)}`, st[i][0], st[i][1] + (i === 2 ? -6 : 16), { a: 'center', s: 11.5, b: true, c: on ? z.col.orange : z.col.purple });
      });
      /* nodes */
      P.forEach(([x, y], i) => {
        const cur = z.step >= 1 && idx[Math.min(z.step, seq.length) - 1] === i;
        D.circle(g, x, y, R, { fill: cur ? z.col.cv : z.col.surf, stroke: z.col.cv, w: 2.5 });
        D.text(g, S[i], x, y + 5, { a: 'center', s: fit(g, S[i], 2 * R - 8, 14), b: true, c: cur ? '#fff' : z.col.ink });
      });
      /* right panel: the factors so far */
      const lx = 412;
      D.text(g, 'Factors', lx, 22, { s: 12.5, b: true, c: z.col.ink });
      let prod = 1, bad = false;
      seq.slice(0, z.step).forEach((w, i) => {
        let t, v;
        if (idx[i] < 0 || (i && idx[i - 1] < 0)) { t = `${w} is not a state`; v = 0; bad = true; }
        else if (i === 0) { t = `π(${w})`; v = pi[idx[0]]; }
        else { t = `P(${w} | ${seq[i - 1]})`; v = T[idx[i - 1]][idx[i]]; }
        prod *= v;
        D.text(g, t, lx, 46 + i * 21, { s: fit(g, t, 100, 12), c: v > 0 ? z.col.ink : z.col.red });
        D.text(g, fmt(v, 3), 548, 46 + i * 21, { a: 'right', s: 12, mono: true, b: true, c: v > 0 ? z.col.ink : z.col.red });
      });
      const yP = 46 + Math.min(z.step, 8) * 21 + 6;
      if (z.step) { D.line(g, lx, yP - 12, 548, yP - 12, z.col.line, 1); D.text(g, 'product', lx, yP + 4, { s: 12, b: true, c: z.col.cv }); D.text(g, fmt(prod, 5), 548, yP + 4, { a: 'right', s: 12.5, mono: true, b: true, c: z.col.cv }); }
      /* best sequences of the same length */
      const Lq = Math.max(1, Math.min(seq.length, 6));
      const all = [];
      const rec = (pre, pr) => { if (pre.length === Lq) { all.push([pre, pr]); return; } for (let j = 0; j < 3; j++) rec(pre.concat(j), pre.length ? pr * T[pre[pre.length - 1]][j] : pi[j]); };
      rec([], 1);
      all.sort((a, b) => b[1] - a[1]);
      const tot = all.reduce((a, b) => a + b[1], 0);
      const rowsums = T.map(r => r.reduce((a, b) => a + b, 0)), pis = pi.reduce((a, b) => a + b, 0);
      const warn = rowsums.map((s, i) => Math.abs(s - 1) > 1e-6 ? `row ${esc(S[i])} adds to ${fmt(s, 3)}` : '').filter(Boolean).concat(Math.abs(pis - 1) > 1e-6 ? [`π adds to ${fmt(pis, 3)}`] : []);
      return `${z.step < seq.length ? `Step ${z.step} of ${seq.length}. ` : ''}P(${esc(seq.join(' '))}) = π × transitions = <b>${bad ? '0 (a word is not a state)' : fmt(prod, 5)}</b>. The most probable ${Lq} word strings: ${all.slice(0, 3).map(a => `${esc(a[0].map(j => S[j]).join(' '))} ${fmt(a[1], 3)}`).join(', ')}. All ${all.length} strings of this length add to ${fmt(tot, 4)}. ${warn.length ? `<b>Not a valid chain:</b> ${warn.join(', ')}.` : 'Every row adds to 1. There is no end state, so this chain only scores strings of a fixed length.'}`;
    }
  });

  /* ---------------------------------------------------------------- perplexity */
  def('perplexity', {
    title: 'Perplexity: how many equally likely words the model is choosing between',
    sub: 'Each bar is the surprise −log₂ p of one word. Their average is the cross entropy Ĥ, and PP = 2 to the power Ĥ.',
    W: 560, H: 290,
    params: [
      { k: 'list', label: 'Each word and the probability the model gave it', type: 'area', v: 'He 0.2\nput 0.1\nthe 0.25\ncoffee 0.05\non 0.4' },
      { k: 'base', label: 'Logarithm base for the working', type: 'select', v: '2', opts: [['2', 'base 2 (bits)'], ['10', 'base 10, as SRILM prints'], ['e', 'base e (nats)']] }
    ],
    tips: [
      { t: 'The worked example from class: total 13.288 bits, Ĥ = 2.658 bits, PP = 6.31. The model behaves as if picking among about six words each time.', set: { list: 'He 0.2\nput 0.1\nthe 0.25\ncoffee 0.05\non 0.4' } },
      { t: 'Give every word 1/7, a uniform model over V = 7. PP is exactly 7: perplexity is a branching factor.', set: { list: 'Sam 0.142857\nI 0.142857\ndo 0.142857\nI 0.142857\nlike 0.142857\n</s> 0.142857' } },
      { t: 'Load the bigram factors of S1 = Sam I do I like. PP = 2.169, the number SRILM printed.', set: { list: 'Sam 0.6\nI 0.6\ndo 0.2\nI 0.5\nlike 0.4\n</s> 0.666667' } },
      { t: 'Make one word very unlikely: coffee 0.0001. One surprising word raises the perplexity of the whole sentence from 6.31 to 25.', set: { list: 'He 0.2\nput 0.1\nthe 0.25\ncoffee 0.0001\non 0.4' } },
      { t: 'Change the base. The surprises change units but PP stays the same, as long as you raise the same base you logged with.', set: { base: '10' } }
    ],
    draw(z) {
      const { g, p } = z;
      const rows = NLZ.pairs(p.list).filter(r => r[1] > 0 && r[1] <= 1).slice(0, 10);
      if (!rows.length) return 'Write lines like "He 0.2" with a probability between 0 and 1.';
      const b = p.base === 'e' ? Math.E : +p.base, unit = { 2: 'bits', 10: 'hartleys', e: 'nats' }[p.base];
      const S = rows.map(r => -Math.log(r[1]) / Math.log(b));
      const tot = S.reduce((a, c) => a + c, 0), Hh = tot / rows.length, PP = b ** Hh;
      const box = [56, 20, 310, 200], mx = Math.max(...S, Hh) * 1.12;
      const m = D.axes(g, z, box, [0, rows.length], [0, mx], { nx: 1, ny: 4, fx: () => '', fy: v => fmt(v, 2) });
      const bw = box[2] / rows.length;
      rows.forEach((r, i) => {
        const x = box[0] + i * bw;
        rr(g, x + bw * 0.15, m.sy(S[i]), bw * 0.7, box[1] + box[3] - m.sy(S[i]), 4, { fill: z.col.cv });
        D.text(g, fmt(S[i], 3), x + bw / 2, m.sy(S[i]) - 5, { a: 'center', s: 10.5, b: true, c: z.col.ink });
        D.text(g, r[0], x + bw / 2, box[1] + box[3] + 15, { a: 'center', s: fit(g, r[0], bw - 2, 11.5), b: true, c: z.col.ink });
        D.text(g, fmt(r[1], 4), x + bw / 2, box[1] + box[3] + 30, { a: 'center', s: fit(g, fmt(r[1], 4), bw - 2, 10.5), c: z.col.ink2 });
      });
      D.line(g, box[0], m.sy(Hh), box[0] + box[2], m.sy(Hh), z.col.orange, 2, [6, 4]);
      /* the label sits above the plot, so it never lands on the bar values that share the Ĥ line */
      D.line(g, box[0] + box[2] - 92, box[1] - 10, box[0] + box[2] - 72, box[1] - 10, z.col.orange, 2, [6, 4]);
      D.text(g, `Ĥ = ${fmt(Hh, 3)}`, box[0] + box[2], box[1] - 6, { a: 'right', s: 11.5, b: true, c: z.col.orange });
      g.save(); g.translate(18, box[1] + box[3] / 2); g.rotate(-Math.PI / 2); D.text(g, `surprise in ${unit}`, 0, 0, { a: 'center', s: 11.5, b: true, c: z.col.ink2 }); g.restore();
      /* right: PP as a row of equally likely choices */
      const lx = 392;
      D.text(g, 'Same uncertainty as a fair', lx, 30, { s: 12, b: true, c: z.col.ink });
      D.text(g, `choice among ${fmt(PP, 3)} words`, lx, 48, { s: 12, b: true, c: z.col.ink });
      const nFull = Math.min(40, Math.floor(PP)), frac = PP - Math.floor(PP);
      for (let i = 0; i < Math.min(40, Math.ceil(PP)); i++) {
        const cx = lx + (i % 8) * 20, cy = 64 + Math.floor(i / 8) * 20;
        rr(g, cx, cy, i < nFull ? 16 : 16 * frac, 16, 3, { fill: z.col.purple });
      }
      if (PP > 40) D.text(g, `(40 of ${Math.round(PP)} shown)`, lx, 176, { s: 11, c: z.col.ink2 });
      D.text(g, `total = ${fmt(tot, 4)} ${unit}`, lx, 200, { s: 12, mono: true, c: z.col.ink });
      D.text(g, `Ĥ = total ÷ ${rows.length} = ${fmt(Hh, 4)}`, lx, 220, { s: 12, mono: true, c: z.col.ink });
      D.text(g, `PP = ${p.base === 'e' ? 'e' : p.base}^Ĥ = ${fmt(PP, 4)}`, lx, 240, { s: 12, mono: true, b: true, c: z.col.cv });
      const prod = rows.reduce((a, r) => a * r[1], 1);
      return `P(sequence) = ${sci(prod)}. Root form: PP = P<sup>−1/N</sup> = (${sci(prod)})<sup>−1/${rows.length}</sup> = <b>${fmt(PP, 4)}</b>. Lower is better, but only when two models are scored on the same test text with the same vocabulary.`;
    }
  });

  /* ---------------------------------------------------------------- add-k on a unigram */
  def('addk', {
    title: 'Add-k smoothing: where the borrowed probability comes from',
    sub: 'Dark bars are the counted (MLE) probabilities, light bars after adding k to every count. Unseen words get a share, paid for by the others.',
    W: 560, H: 280,
    params: [
      { k: 'list', label: 'Each word and its count (count 0 means unseen)', type: 'area', v: 'I 5\nSam 5\n</s> 5\nlike 3\nam 2\ndo 2\n<unk> 0' },
      { k: 'k', label: 'k, the amount added to every count', type: 'range', min: 0, max: 3, step: 0.01, v: 1 },
      { k: 'extra', label: 'Extra unseen word types in the vocabulary', type: 'range', min: 0, max: 200, step: 1, v: 0 }
    ],
    tips: [
      { t: 'Laplace on the toy corpus: N = 22, V = 7. &lt;unk&gt; rises from 0 to 1/29 = 0.0345 while I, Sam and &lt;/s&gt; fall from 0.227 to 0.207.', set: { k: 1, extra: 0 } },
      { t: 'The bag of fruit from class: 2 bananas, 2 apples, no orange. Add 1 to each and the orange gets 1/7.', set: { list: 'banana 2\napple 2\norange 0', k: 1, extra: 0 } },
      { t: 'Keep k = 1 and add 200 unseen types, as a real vocabulary would. Most of the probability now goes to words never seen. This is why add-one is too strong for large V.', set: { list: 'I 5\nSam 5\n</s> 5\nlike 3\nam 2\ndo 2\n<unk> 0', k: 1, extra: 200 } },
      { t: 'Lower k to 0.05 with the same 200 types. The seen words keep most of their mass. Choosing k on a dev set is how add-k is tuned.', set: { k: 0.05, extra: 200 } }
    ],
    draw(z) {
      const { g, p } = z;
      const rows = NLZ.pairs(p.list).filter(r => r[1] >= 0).slice(0, 10);
      if (!rows.length) return 'Write lines like "Sam 5".';
      const N = rows.reduce((a, r) => a + r[1], 0), V = rows.length + p.extra, den = N + p.k * V;
      if (N <= 0 && p.k <= 0) return 'Give at least one word a count above 0, or a k above 0.';
      const show = rows.concat(p.extra ? [[`${p.extra} more unseen`, 0, p.extra]] : []);
      const mle = r => N > 0 ? r[1] / N * (r[2] ? 0 : 1) : 0;
      const sm = r => (r[1] + p.k) / den * (r[2] || 1);
      const mx = Math.max(...show.map(r => Math.max(mle(r), sm(r))), 0.01);
      const box = [60, 18, 480, 190];
      const m = D.axes(g, z, box, [0, show.length], [0, mx * 1.1], { nx: 1, ny: 4, fx: () => '', fy: v => fmt(v, 2) });
      const bw = box[2] / show.length;
      show.forEach((r, i) => {
        const x = box[0] + i * bw, a = mle(r), b = sm(r);
        rr(g, x + bw * 0.12, m.sy(a), bw * 0.36, box[1] + box[3] - m.sy(a), 3, { fill: z.col.cv });
        g.save(); g.globalAlpha = 0.55; rr(g, x + bw * 0.52, m.sy(b), bw * 0.36, box[1] + box[3] - m.sy(b), 3, { fill: z.col.orange }); g.restore();
        D.text(g, fmt(b, 3), x + bw * 0.7, m.sy(b) - 4, { a: 'center', s: 10, c: z.col.ink2 });
        D.text(g, r[0], x + bw / 2, box[1] + box[3] + 15, { a: 'center', s: fit(g, r[0], bw - 2, 11.5), b: true, c: z.col.ink });
        const cs = r[2] ? '0 each' : `c* = ${fmt((r[1] + p.k) * N / den, 2)}`;
        D.text(g, cs, x + bw / 2, box[1] + box[3] + 30, { a: 'center', s: fit(g, cs, bw - 2, 10), c: z.col.ink2 });
      });
      rr(g, 64, 252, 12, 12, 2, { fill: z.col.cv }); D.text(g, 'MLE  C(w) ÷ N', 82, 262, { s: 11.5, c: z.col.ink });
      g.save(); g.globalAlpha = 0.55; rr(g, 200, 252, 12, 12, 2, { fill: z.col.orange }); g.restore(); D.text(g, '(C(w) + k) ÷ (N + kV)', 218, 262, { s: 11.5, c: z.col.ink });
      const unseen = rows.filter(r => r[1] === 0).length + p.extra;
      const moved = unseen * p.k / den;
      return `N = ${N}, V = ${V}, denominator N + kV = ${fmt(den, 3)}. Words never seen now hold <b>${fmt(100 * moved, 2)}%</b> of the probability. The reconstituted count c* = (C + k) × N ÷ (N + kV) shows the discount: frequent words shrink, rare words grow. Everything still adds to 1 because adding k to V counts adds kV to the total.`;
    }
  });

  /* ---------------------------------------------------------------- one history row under six smoothers */
  def('smoothrow', {
    title: 'One history, six ways to share out the probability',
    sub: 'Pick a history word and a method. The bars are P(w | history) for every next word. Dark means the bigram was seen, light means unseen.',
    W: 560, H: 290,
    params: [
      { k: 'train', label: 'Training corpus (one sentence per line)', type: 'area', v: TOY },
      { k: 'h', label: 'History word', type: 'text', v: 'like' },
      { k: 'm', label: 'Method', type: 'select', v: 'kn', opts: [['mle', 'MLE (plain counting)'], ['addk', 'Add-k'], ['abs', 'Absolute discounting'], ['kn', 'Kneser-Ney (interpolated)'], ['katz', 'Katz style backoff'], ['wb', 'Witten-Bell']] },
      { k: 'k', label: 'k', type: 'range', min: 0.01, max: 2, step: 0.01, v: 1, show: p => p.m === 'addk' },
      { k: 'd', label: 'Discount d', type: 'range', min: 0.05, max: 0.95, step: 0.05, v: 0.75, show: p => ['abs', 'kn', 'katz'].includes(p.m) }
    ],
    tips: [
      { t: 'Problem D10: Kneser-Ney with d = 0.75 after like. &lt;/s&gt; 0.5238, Sam 0.1905, and am only 0.0357 because am follows just one word.', set: { m: 'kn', h: 'like', d: 0.75 } },
      { t: 'Problem D8: absolute discounting with d = 0.5 after like. λ = 1/3 and &lt;/s&gt; gets 0.5758.', set: { m: 'abs', h: 'like', d: 0.5 } },
      { t: 'Problem E9: Katz style backoff after do with d = 0.5. Seen words get 0.25 each and α = 11/14 scales the unigram for the rest.', set: { m: 'katz', h: 'do', d: 0.5 } },
      { t: 'Switch to MLE. Four of the six bars vanish: plain counting has nothing to say about unseen pairs.', set: { m: 'mle', h: 'like' } },
      { t: 'Witten-Bell after I: I was followed by 3 different words in 5 uses, so 3/8 of the mass is kept for the unigram.', set: { m: 'wb', h: 'I' } }
    ],
    draw(z) {
      const { g, p } = z;
      const lm = train(p.train, 2);
      if (!lm.sents.length) return 'Type at least one training sentence.';
      const h = String(p.h).trim() || '<s>';
      const cols = lm.words.slice(0, 9).concat(['</s>']), V = cols.length;
      const c2 = lm.C[2], c1 = lm.C[1];
      const Ch = c2.hist.get(h) || 0;
      const cnt = w => c2.ng.get(h + '|' + w) || 0;
      const uni = w => (c1.ng.get('|' + w) || 0) / lm.N;
      const seen = cols.filter(w => cnt(w) > 0), N1 = seen.length;
      /* continuation probability: in how many different histories does w appear */
      let types = 0; const pred = new Map();
      c2.ng.forEach((n, key) => { const w = key.split('|')[1]; types++; pred.set(w, (pred.get(w) || 0) + 1); });
      const cont = w => (pred.get(w) || 0) / types;
      let P, note, lam = null;
      if (!Ch && p.m !== 'addk') { P = cols.map(uni); note = `The history ${esc(h)} was never seen, so every method falls back to the unigram.`; }
      else if (p.m === 'mle') { P = cols.map(w => cnt(w) / Ch); note = `P(w | ${esc(h)}) = C(${esc(h)} w) ÷ ${Ch}. Unseen pairs get exactly 0.`; }
      else if (p.m === 'addk') { P = cols.map(w => (cnt(w) + p.k) / (Ch + p.k * V)); note = `(C + ${fmt(p.k, 2)}) ÷ (${Ch} + ${fmt(p.k, 2)} × ${V}). Every unseen word gets the same share whatever its frequency.`; }
      else if (p.m === 'abs' || p.m === 'kn') {
        lam = p.d * N1 / Ch;
        const low = p.m === 'kn' ? cont : uni;
        P = cols.map(w => Math.max(cnt(w) - p.d, 0) / Ch + lam * low(w));
        note = `max(C − ${fmt(p.d, 2)}, 0) ÷ ${Ch} + λ × ${p.m === 'kn' ? 'P<sub>cont</sub>(w)' : 'P(w)'}, with λ = d × ${N1} ÷ ${Ch} = ${fmt(lam, 4)}.${p.m === 'kn' ? ` P<sub>cont</sub>(w) counts the different words that come before w, out of ${types} bigram types.` : ''}`;
      } else if (p.m === 'katz') {
        const beta = p.d * N1 / Ch, um = cols.filter(w => !cnt(w)).reduce((a, w) => a + uni(w), 0);
        const alpha = um > 0 ? beta / um : 0; lam = alpha;
        P = cols.map(w => cnt(w) ? (cnt(w) - p.d) / Ch : alpha * uni(w));
        note = `Seen: (C − ${fmt(p.d, 2)}) ÷ ${Ch}. Left over β = ${fmt(beta, 4)}. Unseen: α × P(w) with α = β ÷ ${fmt(um, 4)} = ${fmt(alpha, 4)}.`;
      } else {
        lam = N1 / (N1 + Ch);
        P = cols.map(w => (1 - lam) * cnt(w) / Ch + lam * uni(w));
        note = `λ = N₁₊ ÷ (N₁₊ + C(h)) = ${N1} ÷ (${N1} + ${Ch}) = ${fmt(lam, 4)} goes to the unigram.`;
      }
      const box = [60, 22, 480, 190], mx = Math.max(...P, 0.05) * 1.15;
      const m = D.axes(g, z, box, [0, V], [0, mx], { nx: 1, ny: 4, fx: () => '', fy: v => fmt(v, 2) });
      const bw = box[2] / V;
      cols.forEach((w, i) => {
        const x = box[0] + i * bw, s = cnt(w) > 0;
        g.save(); if (!s) g.globalAlpha = 0.5;
        rr(g, x + bw * 0.18, m.sy(P[i]), bw * 0.64, box[1] + box[3] - m.sy(P[i]), 4, { fill: s ? z.col.cv : z.col.orange });
        g.restore();
        D.text(g, fmt(P[i], 4), x + bw / 2, m.sy(P[i]) - 5, { a: 'center', s: fit(g, fmt(P[i], 4), bw - 2, 11), b: true, c: z.col.ink });
        D.text(g, w, x + bw / 2, box[1] + box[3] + 15, { a: 'center', s: fit(g, w, bw - 2, 12), b: true, mono: true, c: z.col.ink });
        const sub = p.m === 'kn' ? `cont ${pred.get(w) || 0}` : `C = ${cnt(w)}`;
        D.text(g, sub, x + bw / 2, box[1] + box[3] + 31, { a: 'center', s: fit(g, sub, bw - 2, 10.5), c: z.col.ink2 });
      });
      const sum = P.reduce((a, b) => a + b, 0);
      D.text(g, `history: ${h}    C(h) = ${Ch}    followers seen: ${N1}`, 60, 268, { s: 12, b: true, c: z.col.ink2 });
      return `${note} The row adds to <b>${fmt(sum, 4)}</b>${Math.abs(sum - 1) < 1e-9 ? ', a proper distribution' : ''}. Unseen words in this row share ${fmt(cols.filter(w => !cnt(w)).reduce((a, w, i) => a + P[cols.indexOf(w)], 0), 4)} of the mass.`;
    }
  });

  /* ---------------------------------------------------------------- Good-Turing */
  def('goodturing', {
    title: 'Good-Turing: use the things seen once to estimate the unseen',
    sub: 'Nc is how many types were seen exactly c times. Each count c is replaced by c* = (c + 1) N(c+1) ÷ Nc, and N1 ÷ N goes to everything unseen.',
    W: 560, H: 270,
    params: [
      { k: 'list', label: 'Counts of the seen types (one number per type)', type: 'area', v: '3 3 2 2 2 2 1 1 1 1 1 1 1 1' },
      { k: 'possible', label: 'Number of possible types (seen and unseen)', type: 'range', min: 1, max: 200, v: 36 }
    ],
    tips: [
      { t: 'Problem D9: the 14 seen bigram types of the toy corpus. N1 = 8 of N = 22, so 8/22 = 0.364 is kept for the 22 unseen bigrams, 0.0165 each.', set: { list: '3 3 2 2 2 2 1 1 1 1 1 1 1 1', possible: 36 } },
      { t: 'A fishing trip from the textbook: 10 carp, 3 perch, 2 whitefish, 1 trout, 1 salmon, 1 eel. P(a new species) = 3/18.', set: { list: '10 3 2 1 1 1', possible: 8 } },
      { t: 'Make every type seen at least twice. N1 = 0, so Good-Turing gives nothing to the unseen. It needs some singletons to work.', set: { list: '3 3 2 2 2 2', possible: 36 } }
    ],
    draw(z) {
      const { g, p } = z;
      const cs = NLZ.nums(p.list).filter(v => v > 0 && Number.isInteger(v));
      if (!cs.length) return 'Type whole number counts, like 3 2 1 1.';
      const N = cs.reduce((a, b) => a + b, 0), Nc = new Map();
      cs.forEach(c => Nc.set(c, (Nc.get(c) || 0) + 1));
      const maxc = Math.max(...cs);
      const unseenTypes = Math.max(0, p.possible - cs.length), N1 = Nc.get(1) || 0;
      const head = ['c', 'Nc', 'c × Nc', 'c*', 'P per type'];
      const xs = [40, 100, 170, 250, 340];
      head.forEach((t, i) => D.text(g, t, xs[i], 22, { a: 'right', s: 11.5, b: true, c: z.col.ink2 }));
      const rows = [[0, unseenTypes]];
      for (let c = 1; c <= Math.min(maxc, 9); c++) if (Nc.get(c) || c <= 3) rows.push([c, Nc.get(c) || 0]);
      rows.forEach(([c, n], i) => {
        const y = 44 + i * 22;
        const nn = Nc.get(c + 1) || 0;
        const cstar = c === 0 ? (unseenTypes ? N1 / unseenTypes : 0) : (n ? (c + 1) * nn / n : NaN);
        const pt = c === 0 ? (unseenTypes ? N1 / N / unseenTypes : 0) : (n ? cstar / N : NaN);
        if (c === 0) rr(g, 4, y - 15, 350, 22, 5, { fill: z.col.hl || z.col.bg });
        D.text(g, String(c), xs[0], y, { a: 'right', s: 12, mono: true, b: true, c: z.col.ink });
        D.text(g, String(n), xs[1], y, { a: 'right', s: 12, mono: true, c: z.col.ink });
        D.text(g, c ? String(c * n) : '-', xs[2], y, { a: 'right', s: 12, mono: true, c: z.col.ink2 });
        D.text(g, n && isFinite(cstar) ? fmt(cstar, 3) : '-', xs[3], y, { a: 'right', s: 12, mono: true, b: true, c: n && cstar === 0 && c > 0 ? z.col.red : z.col.cv });
        D.text(g, n && isFinite(pt) ? fmt(pt, 4) : '-', xs[4], y, { a: 'right', s: 12, mono: true, c: z.col.ink });
      });
      /* right: share of the probability */
      const lx = 380, bw = 168;
      D.text(g, 'Where the probability goes', lx, 22, { s: 12, b: true, c: z.col.ink });
      const pu = N1 / N;
      rr(g, lx, 36, bw, 26, 5, { fill: z.col.bg, stroke: z.col.line });
      rr(g, lx, 36, Math.max(2, bw * pu), 26, 5, { fill: z.col.orange });
      D.text(g, `unseen ${fmt(pu, 3)}`, lx, 80, { s: 12, b: true, c: z.col.orange });
      D.text(g, `= N1 ÷ N = ${N1} ÷ ${N}`, lx, 98, { s: 12, mono: true, c: z.col.ink });
      wrap(g, `Seen types keep ${fmt(1 - pu, 3)}. The largest counts have no N(c+1), so in practice counts above about 5 are left as they are (Katz).`, lx, 128, bw, { s: 11.5, c: z.col.ink2 });
      return `N = ${N} tokens over ${cs.length} seen types. The unseen mass is <b>${N1} ÷ ${N} = ${fmt(pu, 4)}</b>${unseenTypes ? `, which is ${fmt(pu / unseenTypes, 4)} for each of the ${unseenTypes} unseen types if spread evenly` : ''}. A c* of 0 (red) shows where N(c+1) is missing: the raw formula breaks for the largest counts, which is why real systems smooth the Nc values first.`;
    }
  });

  /* ---------------------------------------------------------------- tuning lambda on a dev set */
  def('lambdagrid', {
    title: 'Tune λ on the dev set, report on the test set',
    sub: 'Mixture = λ × MLE bigram + (1 − λ) × add-k unigram. The curves are perplexity for every λ. The dot is the λ you chose.',
    W: 560, H: 290,
    params: [
      { k: 'train', label: 'Training corpus', type: 'area', v: TOY },
      { k: 'dev', label: 'Dev sentences', type: 'area', v: 'Sam I do like linguistics' },
      { k: 'test', label: 'Test sentences', type: 'area', v: 'I like Sam\ndo I like linguistics' },
      { k: 'ku', label: 'Add-k for the unigram', type: 'range', min: 0.01, max: 2, step: 0.01, v: 1 },
      { k: 'lam', label: 'Your λ', type: 'range', min: 0.01, max: 0.99, step: 0.01, v: 0.5 }
    ],
    tips: [
      { t: 'Problem E8: on this dev sentence λ = 0.5 gives PP 6.438, and the curve bottoms out near λ = 0.48.', set: { lam: 0.48 } },
      { t: 'Push λ to 0.99. Context is used fully, but the unseen word now gets only 1% of a tiny unigram share, and perplexity shoots up.', set: { lam: 0.99 } },
      { t: 'Problem E10: keep λ = 0.5 and read the test perplexity, 5.9003. It is honest because the test data took no part in the choice.', set: { lam: 0.5, ku: 1 } },
      { t: 'Change the unigram k to 0.1. The best λ moves. In assignment 2 the same search was run over k and λ together.', set: { ku: 0.1 } }
    ],
    draw(z) {
      const { g, p } = z;
      const lm = train(p.train, 2);
      if (!lm.sents.length) return 'Type a training corpus.';
      const run = (txt, l) => score(lm, txt, { n: 2, k: 0, unk: true, lam: l, ku: p.ku }).tot.ppl;
      const xs = []; for (let i = 1; i <= 99; i++) xs.push(i / 100);
      const dev = xs.map(l => run(p.dev, l)), tst = lines(p.test).length ? xs.map(l => run(p.test, l)) : [];
      const all = dev.concat(tst).filter(isFinite);
      if (!all.length) return 'Type a dev sentence.';
      const box = [60, 16, 330, 220];
      const ymax = Math.min(Math.max(...all), Math.min(...all) * 4);
      const m = D.axes(g, z, box, [0, 1], [0, ymax * 1.05], { nx: 5, ny: 4, xl: 'λ, the weight of the bigram', fy: v => fmt(v, 1) });
      g.save(); g.beginPath(); g.rect(box[0], box[1], box[2], box[3]); g.clip();
      const line = (arr, c, dash) => { g.save(); g.strokeStyle = c; g.lineWidth = 2.2; if (dash) g.setLineDash(dash); g.beginPath(); arr.forEach((v, i) => { const X = m.sx(xs[i]), Y = m.sy(v); i ? g.lineTo(X, Y) : g.moveTo(X, Y); }); g.stroke(); g.restore(); };
      line(dev, z.col.cv); if (tst.length) line(tst, z.col.purple, [6, 4]);
      g.restore();
      let bi = 0; dev.forEach((v, i) => { if (v < dev[bi]) bi = i; });
      D.circle(g, m.sx(xs[bi]), m.sy(dev[bi]), 5, { stroke: z.col.cv, w: 2, fill: z.col.surf });
      const dv = run(p.dev, p.lam), tv = tst.length ? run(p.test, p.lam) : NaN;
      D.line(g, m.sx(p.lam), box[1], m.sx(p.lam), box[1] + box[3], z.col.orange, 1.5, [3, 3]);
      D.circle(g, m.sx(p.lam), m.sy(Math.min(dv, ymax)), 6, { fill: z.col.orange });
      const lx = 412;
      D.text(g, 'dev', lx + 22, 30, { s: 12, b: true, c: z.col.cv }); D.line(g, lx, 26, lx + 16, 26, z.col.cv, 2.5);
      if (tst.length) { D.text(g, 'test', lx + 22, 50, { s: 12, b: true, c: z.col.purple }); D.line(g, lx, 46, lx + 16, 46, z.col.purple, 2.5, [5, 3]); }
      D.text(g, `best λ on dev: ${fmt(xs[bi], 2)}`, lx, 84, { s: 12, b: true, c: z.col.ink });
      D.text(g, `dev PP there: ${fmt(dev[bi], 4)}`, lx, 104, { s: 12, mono: true, c: z.col.ink });
      D.text(g, `your λ = ${fmt(p.lam, 2)}`, lx, 140, { s: 12, b: true, c: z.col.orange });
      D.text(g, `dev PP:  ${fmt(dv, 4)}`, lx, 160, { s: 12, mono: true, c: z.col.ink });
      if (tst.length) D.text(g, `test PP: ${fmt(tv, 4)}`, lx, 180, { s: 12, mono: true, b: true, c: z.col.purple });
      return `The dev curve is U shaped: a small λ throws away the bigram context, a large λ leaves unseen words almost unprotected. Pick λ where the dev curve is lowest (${fmt(xs[bi], 2)} here), then report the test perplexity once. Picking λ by looking at the test curve would be the same cheating as training on the test set.`;
    }
  });

  /* ---------------------------------------------------------------- assignment 2 on the Brown corpus */
  const A2 = {
    methods: ['addsmooth 1', 'Absolute discounting', 'Good-Turing', 'Witten-Bell', 'Kneser-Ney'],
    flags: ['-addsmooth 1', '-cdiscount', '(default)', '-wbdiscount', '-kndiscount'],
    bi: [[2493.24, 3600.57], [391.85, 518.76], [642.33, 870.35], [396.83, 525.66], [352.45, 464.28]],
    tri: [[3620.71, 5321.27], [384.91, 509.14], [629.24, 851.77], [385.06, 509.35], [340.18, 447.38]],
    unk: [-5.428, -1.401, -5.408, -1.298, -0.878]
  };
  NLZ.A2 = A2;
  def('srilmtable', {
    title: 'Assignment 2: five smoothing methods on the Brown corpus',
    sub: 'Real SRILM results from the assignment. Pick what to compare. Lower perplexity is better, all on the same test set and vocabulary.',
    W: 560, H: 270,
    params: [
      { k: 'metric', label: 'Measure', type: 'select', v: 'ppl', opts: [['ppl', 'ppl (words and </s>)'], ['ppl1', 'ppl1 (words only)'], ['unk', 'log₁₀ P(<unk>) in the model']] },
      { k: 'order', label: 'Order', type: 'select', v: 'both', opts: [['2', 'bigram'], ['3', 'trigram'], ['both', 'bigram and trigram side by side']], show: p => p.metric !== 'unk' },
      { k: 'drop', label: 'Hide addsmooth 1 (it dwarfs the others)', type: 'check', v: false }
    ],
    tips: [
      { t: 'Compare the five methods as bigrams. Kneser-Ney is best at 352.45, add-one is worst at 2493.24, about 7 times higher.', set: { metric: 'ppl', order: '2', drop: false } },
      { t: 'Hide add-one and show both orders. Every discounting method improves from bigram to trigram. Add-one gets worse.', set: { metric: 'ppl', order: 'both', drop: true } },
      { t: 'Look at log P(&lt;unk&gt;). Add-one and Good-Turing give &lt;unk&gt; about 10⁻⁵·⁴, Kneser-Ney about 10⁻⁰·⁹. Much of the gap comes from how much mass &lt;unk&gt; receives.', set: { metric: 'unk', drop: false } }
    ],
    draw(z) {
      const { g, p } = z;
      const idx = A2.methods.map((m, i) => i).filter(i => !(p.drop && i === 0));
      const series = p.metric === 'unk' ? [['log₁₀ P(<unk>)', idx.map(i => -A2.unk[i]), z.col.orange]]
        : [['2', 'bigram', z.col.cv], ['3', 'trigram', z.col.purple]].filter(s => p.order === 'both' || p.order === s[0]).map(s => [s[1], idx.map(i => (s[0] === '2' ? A2.bi : A2.tri)[i][p.metric === 'ppl' ? 0 : 1]), s[2]]);
      const mx = Math.max(...series.flatMap(s => s[1]));
      const x0 = 156, bwMax = 330, rowH = 200 / idx.length, bh = Math.min(16, (rowH - 8) / series.length);
      idx.forEach((i, r) => {
        const y = 20 + r * rowH;
        D.text(g, A2.methods[i], x0 - 10, y + rowH / 2 - 2, { a: 'right', s: 12.5, b: true, c: z.col.ink });
        D.text(g, A2.flags[i], x0 - 10, y + rowH / 2 + 12, { a: 'right', s: 10.5, mono: true, c: z.col.ink2 });
        series.forEach((s, j) => {
          const v = s[1][r], w = Math.max(2, v / mx * bwMax), yy = y + rowH / 2 - series.length * bh / 2 + j * bh;
          rr(g, x0, yy, w, bh - 2, 3, { fill: s[2] });
          const t = p.metric === 'unk' ? '−' + fmt(v, 3) : fmt(v, 2);
          D.text(g, t, x0 + w + 5, yy + bh - 4, { s: 11, b: true, c: z.col.ink });
        });
      });
      series.forEach((s, j) => { rr(g, x0 + j * 110, 238, 12, 12, 2, { fill: s[2] }); D.text(g, s[0], x0 + 18 + j * 110, 248, { s: 11.5, b: true, c: z.col.ink }); });
      if (p.metric === 'unk') return 'Bars show how negative log₁₀ P(&lt;unk&gt;) is, so a longer bar means less probability for unknown words. Kneser-Ney and Witten-Bell keep far more mass for &lt;unk&gt;, and the Brown test set has many unknown words, which is a large part of why they score better.';
      const best = idx.reduce((a, i) => A2.bi[i][0] < A2.bi[a][0] ? i : a, idx[0]);
      return `Best: <b>${A2.methods[best]}</b>. Every discounting method beats add-one by a factor of 4 to 7. Moving from bigram to trigram lowers perplexity for the discounting methods but raises it for add-one, which spreads mass over far more unseen trigrams. ppl1 is always higher than ppl because the same log probability is divided by fewer tokens.`;
    }
  });

  def('stopwords', {
    title: 'What removing punctuation and stop words does to perplexity',
    sub: 'Three versions of the Brown data, Witten-Bell bigram. The vocabulary and token count change too, so read this as a trend, not a strict comparison.',
    W: 560, H: 250,
    params: [
      { k: 'metric', label: 'Show', type: 'select', v: 'ppl', opts: [['ppl', 'ppl'], ['ppl1', 'ppl1'], ['words', 'test words'], ['uni', 'model unigrams (vocabulary)']] },
      { k: 'log', label: 'Log scale', type: 'check', v: false }
    ],
    tips: [
      { t: 'Perplexity rises from 397 to 611 to 3235 as the easy tokens are removed.', set: { metric: 'ppl' } },
      { t: 'Look at test words: removing stop words halves the test set. Fewer, harder tokens remain.', set: { metric: 'words' } },
      { t: 'Turn on the log scale to compare the growth steps fairly.', set: { metric: 'ppl1', log: true } }
    ],
    draw(z) {
      const { g, p } = z;
      const D3 = [['Original', 305056, 40607, 396.83, 525.66], ['Punctuation removed', 268236, 40590, 610.78, 859.35], ['Punctuation and stop words removed', 148503, 40262, 3234.52, 7019.32]];
      const col = { words: 1, uni: 2, ppl: 3, ppl1: 4 }[p.metric];
      const vals = D3.map(r => r[col]);
      const f = v => p.log ? Math.log10(v) : v;
      const mx = Math.max(...vals.map(f)), mn = p.log ? Math.min(...vals.map(f)) - 0.3 : 0;
      const x0 = 220, W = 270;
      D3.forEach((r, i) => {
        const y = 30 + i * 62;
        wrap(g, r[0], 12, y + 14, x0 - 24, { s: 12.5, b: true, c: z.col.ink });
        const w = Math.max(3, (f(r[col]) - mn) / (mx - mn) * W);
        rr(g, x0, y, w, 30, 5, { fill: [z.col.cv, z.col.purple, z.col.orange][i] });
        D.text(g, r[col].toLocaleString(), x0 + w + 6, y + 20, { s: 12.5, b: true, mono: true, c: z.col.ink });
      });
      return 'Punctuation and stop words such as the, of and and are frequent and easy to predict, so they pull the average surprise down. Remove them and only the harder content words remain, and words that were never neighbours become adjacent, which weakens the bigram context. Perplexities are only comparable with the same vocabulary and tokenisation, so this is a trend, not a fair contest.';
    }
  });

  def('addkgrid', {
    title: 'Searching k and λ together on the dev set',
    sub: 'Assignment 2, question 5: an add-k bigram interpolated with a unigram. For each k the best λ was found on dev. The search picks the lowest point.',
    W: 560, H: 260,
    params: [
      { k: 'pick', label: 'Your choice of k', type: 'select', v: '0.001', opts: [['1', '1'], ['0.1', '0.1'], ['0.01', '0.01'], ['0.001', '0.001'], ['0.0001', '0.0001']] }
    ],
    tips: [
      { t: 'Choose k = 1. The best λ is only 0.3 and dev perplexity is 1123.66: add-one is far too strong.', set: { pick: '1' } },
      { t: 'Choose k = 0.001, the winner: λ = 0.7, dev ppl 581.03. On the unseen test set it gives 681.35.', set: { pick: '0.001' } },
      { t: 'Choose k = 0.0001. The curve has flattened (582.25): smaller k no longer helps.', set: { pick: '0.0001' } }
    ],
    draw(z) {
      const { g, p } = z;
      const G = [[1, 0.3, 1123.66], [0.1, 0.6, 833.51], [0.01, 0.7, 656.01], [0.001, 0.7, 581.03], [0.0001, 0.6, 582.25]];
      const box = [70, 20, 300, 180];
      const m = D.axes(g, z, box, [-4, 0], [500, 1200], { nx: 4, ny: 7, fx: v => '10' + ({ '-4': '⁻⁴', '-3': '⁻³', '-2': '⁻²', '-1': '⁻¹', 0: '⁰' }[Math.round(v)] || ''), fy: v => String(Math.round(v)), xl: 'k (log scale)' });
      g.save(); g.strokeStyle = z.col.cv; g.lineWidth = 2.2; g.beginPath();
      G.forEach((r, i) => { const X = m.sx(Math.log10(r[0])), Y = m.sy(r[2]); i ? g.lineTo(X, Y) : g.moveTo(X, Y); }); g.stroke(); g.restore();
      G.forEach(r => {
        const on = String(r[0]) === p.pick, X = m.sx(Math.log10(r[0])), Y = m.sy(r[2]);
        D.circle(g, X, Y, on ? 7 : 4.5, { fill: on ? z.col.orange : z.col.cv, stroke: '#fff', w: 1.5 });
        D.text(g, `λ ${r[1]}`, r[0] === 0.0001 ? X + 9 : X, r[0] === 0.0001 ? Y - 9 : Y - 11, { a: r[0] === 0.0001 ? 'left' : 'center', s: 10.5, b: true, c: z.col.ink2 });
      });
      const r = G.find(x => String(x[0]) === p.pick);
      const lx = 402;
      D.text(g, `k = ${r[0]}`, lx, 40, { s: 13, b: true, c: z.col.orange });
      D.text(g, `best λ = ${r[1]}`, lx, 64, { s: 12.5, mono: true, c: z.col.ink });
      D.text(g, `dev ppl = ${r[2]}`, lx, 86, { s: 12.5, mono: true, c: z.col.ink });
      if (r[0] === 0.001) { D.text(g, 'test ppl = 681.35', lx, 120, { s: 12.5, mono: true, b: true, c: z.col.purple }); D.text(g, 'test ppl1 = 925.77', lx, 140, { s: 12.5, mono: true, c: z.col.purple }); }
      wrap(g, 'For comparison, Kneser-Ney alone reached 352.45 on test.', lx, 176, 150, { s: 11.5, c: z.col.ink2 });
      return 'The minimum is k = 0.001 with λ = 0.7 (dev ppl 581.03). The test set was used once, after the choice, and gave ppl 681.35. Even tuned, add-k with interpolation loses clearly to Kneser-Ney, which is why discounting methods are the standard.';
    }
  });
})();

/* ===== Step 5: tagging, finite state machines, HMMs, Viterbi, chunking and syntax ===== */
(() => {
  const { def, D, esc } = CVZ;
  const { tw, rr, pill, flow, wrap, fit, fmt } = NLZ;
  const toks = s => String(s).trim().split(/\s+/).filter(Boolean);
  const nums = NLZ.nums;
  /* a small fraction such as 3/5 when the value is one, else a decimal */
  function frac(n, d) { if (!d) return '–'; if (!n) return '0'; const g = (a, b) => b ? g(b, a % b) : a, k = g(n, d); return d / k === 1 ? String(n / k) : `${n / k}/${d / k}`; }
  const sci = v => v === 0 ? '0' : (v >= 0.001 ? fmt(v, 5) : v.toExponential(2).replace('-', '−'));
  const andList = a => a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1];

  /* ---------------------------------------------------------------- Chapter 5.1: look up taggers with backoff */
  const TAGGED = 'I/PRP read/VBP a/DT book/NN ./.\nPlease/UH book/VB a/DT ticket/NN ./.\nShe/PRP can/MD dance/VB ./.\nA/DT can/NN of/IN soda/NN ./.\nThey/PRP can/MD fish/VB ./.\nThe/DT student/NN reads/VBZ books/NNS ./.\nWe/PRP book/VBP rooms/NNS early/RB ./.';
  const readTagged = s => String(s).split('\n').map(l => toks(l).map(t => { const i = t.lastIndexOf('/'); return i > 0 ? [t.slice(0, i), t.slice(i + 1)] : [t, '?']; })).filter(a => a.length);
  const best = m => { let bk = null, bv = -1; m.forEach((v, k) => { if (v > bv) { bv = v; bk = k; } }); return bk; };
  def('lookup', {
    title: 'Look up taggers chained with backoff',
    sub: 'Each word is tagged by the most specific tagger that has seen it. The colour shows which one decided: bigram, unigram or the default.',
    W: 560, H: 230,
    params: [
      { k: 'train', label: 'Tagged training sentences (word/TAG)', type: 'area', v: TAGGED },
      { k: 'test', label: 'Sentence to tag', type: 'text', v: 'Please book a can of fish .' },
      { k: 'chain', label: 'Tagger', type: 'select', v: 'bigram', opts: [['default', 'Default tagger only'], ['unigram', 'Unigram, backing off to the default'], ['bigram', 'Bigram, backing off to unigram, then default']] },
      { k: 'dflt', label: 'Tag used by the default tagger', type: 'text', v: 'NN' }
    ],
    tips: [
      { t: 'Use the default tagger alone. Every word becomes NN. That is the floor every real tagger must beat.', set: { chain: 'default' } },
      { t: 'Use the unigram tagger. book gets its most frequent tag, but it is the same in every sentence, whatever the context.', set: { chain: 'unigram', test: 'I book a ticket .' } },
      { t: 'Use the bigram tagger on "I book a ticket". After a pronoun, book is now a verb, because the pair (PRP, book) was seen.', set: { chain: 'bigram', test: 'I book a ticket .' } },
      { t: 'Tag "Please book a can of fish". fish after of was never seen, so the bigram backs off and the unigram says VB. Look up taggers know only what they have counted.', set: { chain: 'bigram', test: 'Please book a can of fish .' } }
    ],
    draw(z) {
      const { g, p } = z;
      const sents = readTagged(p.train);
      const uni = new Map(), bi = new Map();
      sents.forEach(s => { let prev = '<s>'; s.forEach(([w, t]) => { if (!uni.has(w)) uni.set(w, new Map()); uni.get(w).set(t, (uni.get(w).get(t) || 0) + 1); const k = prev + '|' + w; if (!bi.has(k)) bi.set(k, new Map()); bi.get(k).set(t, (bi.get(k).get(t) || 0) + 1); prev = t; }); });
      const words = toks(p.test).slice(0, 9);
      if (!words.length) return 'Type a sentence.';
      const dflt = String(p.dflt).trim() || 'NN';
      let prev = '<s>';
      const out = words.map(w => {
        let t, by;
        if (p.chain === 'bigram' && bi.has(prev + '|' + w)) { t = best(bi.get(prev + '|' + w)); by = 'bigram'; }
        else if (p.chain !== 'default' && uni.has(w)) { t = best(uni.get(w)); by = 'unigram'; }
        else { t = dflt; by = 'default'; }
        const r = { w, t, by, prev }; prev = t; return r;
      });
      const col = { bigram: z.col.cv, unigram: z.col.purple, default: z.col.orange };
      const cw = Math.min(64, (z.W - 24) / words.length);
      out.forEach((r, i) => {
        const x = 12 + i * cw;
        rr(g, x + 2, 26, cw - 4, 34, 7, { fill: z.col.surf, stroke: z.col.line });
        D.text(g, r.w, x + cw / 2, 48, { a: 'center', s: fit(g, r.w, cw - 10, 13.5), b: true, c: z.col.ink });
        D.arrow(g, x + cw / 2, 62, x + cw / 2, 82, z.col.ink2, 1.4);
        rr(g, x + 4, 86, cw - 8, 28, 7, { fill: col[r.by] });
        D.text(g, r.t, x + cw / 2, 105, { a: 'center', s: fit(g, r.t, cw - 12, 13), b: true, mono: true, c: '#fff' });
        D.text(g, r.by, x + cw / 2, 130, { a: 'center', s: fit(g, r.by, cw - 4, 10.5), c: col[r.by] });
        if (r.by === 'bigram') D.text(g, `after ${r.prev}`, x + cw / 2, 145, { a: 'center', s: fit(g, `after ${r.prev}`, cw - 4, 10), c: z.col.ink2 });
      });
      [['bigram: (previous tag, word) was seen', 'bigram'], ['unigram: the word was seen', 'unigram'], ['default: nothing was seen', 'default']].forEach(([t, k], i) => { rr(g, 14, 172 + i * 18, 12, 12, 3, { fill: col[k] }); D.text(g, t, 32, 182 + i * 18, { s: 11.5, c: z.col.ink }); });
      const amb = [...uni.entries()].filter(([w, m]) => m.size > 1).map(([w, m]) => `${esc(w)} (${[...m.keys()].join(', ')})`);
      return `The chain is the backoff idea of chapter 4.3 applied to tags. In NLTK: BigramTagger(train, backoff=UnigramTagger(train, backoff=DefaultTagger("${esc(dflt)}"))). Ambiguous words in this training data: ${amb.join(', ') || 'none'}.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 5.2: finite state automata */
  const FSA = {
    catcar: ['q0 c q1\nq1 a q2\nq2 t q3\nq2 r q3', 'q3', 'char'],
    sheep: ['q0 b q1\nq1 a q2\nq2 a q3\nq3 a q3\nq3 ! q4', 'q4', 'char'],
    words: ['q0 he q1\nq0 she q1\nq1 is q2\nq1 was q2\nq2 happy q3\nq2 sad q3', 'q3', 'word']
  };
  def('fsa', {
    title: 'A finite state automaton reads a string',
    sub: 'Press Play. The machine follows one arrow per symbol. It accepts only if every symbol has an arrow and it ends in a final state (double circle).',
    W: 560, H: 250,
    params: [
      { k: 'delta', label: 'Transitions: from, symbol, to (one per line)', type: 'area', v: FSA.catcar[0] },
      { k: 'final', label: 'Final states', type: 'text', v: 'q3' },
      { k: 'unit', label: 'Symbols are', type: 'select', v: 'char', opts: [['char', 'single characters'], ['word', 'whole words']] },
      { k: 'input', label: 'Input', type: 'text', v: 'cat' }
    ],
    steps: z => (z.p.unit === 'word' ? toks(z.p.input) : [...String(z.p.input).replace(/\s/g, '')]).length, startAtZero: true,
    tips: [
      { t: 'Play "cat", then try "ca". ca stops in q2, which is not final, so it is rejected.', set: { delta: FSA.catcar[0], final: 'q3', unit: 'char', input: 'ca' }, play: true },
      { t: 'Try "cut". In q1 there is no arrow for u, so the machine is stuck and rejects at once.', set: { delta: FSA.catcar[0], final: 'q3', unit: 'char', input: 'cut' }, play: true },
      { t: 'Load sheep talk /baa+!/ and play "baaaa!". The self loop on q3 eats the extra a\'s.', set: { delta: FSA.sheep[0], final: 'q4', unit: 'char', input: 'baaaa!' }, play: true },
      { t: 'Sheep talk with "ba!". Only one a, so q2 has no arrow for ! and the string is rejected.', set: { delta: FSA.sheep[0], final: 'q4', unit: 'char', input: 'ba!' }, play: true },
      { t: 'Problem H3: a machine over words. "she was happy" is one of its 2 × 2 × 2 = 8 sentences.', set: { delta: FSA.words[0], final: 'q3', unit: 'word', input: 'she was happy' }, play: true }
    ],
    draw(z) {
      const { g, p } = z;
      const T = String(p.delta).split('\n').map(toks).filter(a => a.length === 3);
      if (!T.length) return 'Write transitions like "q0 c q1".';
      const S = []; T.forEach(([a, , b]) => { if (!S.includes(a)) S.push(a); if (!S.includes(b)) S.push(b); });
      const F = new Set(toks(String(p.final).replace(/,/g, ' ')));
      const syms = p.unit === 'word' ? toks(p.input) : [...String(p.input).replace(/\s/g, '')];
      /* run the machine */
      let cur = S[0], stuck = -1; const path = [cur];
      for (let i = 0; i < syms.length; i++) { const tr = T.find(t => t[0] === cur && t[1] === syms[i]); if (!tr) { stuck = i; break; } cur = tr[2]; path.push(cur); }
      const shown = Math.min(z.step, syms.length);
      const live = stuck >= 0 && shown > stuck ? null : path[Math.min(shown, path.length - 1)];
      const n = S.length, R = 22, y0 = 150;
      const X = i => 50 + i * (z.W - 100) / Math.max(1, n - 1);
      /* merge arcs with the same endpoints */
      const E = new Map(); T.forEach(([a, s, b]) => { const k = a + '>' + b; if (!E.has(k)) E.set(k, []); E.get(k).push(s); });
      const usedEdge = new Set(); for (let i = 0; i < Math.min(shown, path.length - 1); i++) usedEdge.add(path[i] + '>' + path[i + 1]);
      E.forEach((ss, k) => {
        const [a, b] = k.split('>'), i = S.indexOf(a), j = S.indexOf(b), on = usedEdge.has(k);
        const c = on ? z.col.orange : z.col.ink2, w = on ? 3 : 1.6, lab = ss.join(', ');
        let at;
        if (i === j) at = NLZ.loop(g, X(i), y0, R, -Math.PI / 2, c, w);
        else if (j === i + 1) { D.arrow(g, X(i) + R, y0, X(j) - R - 1, y0, c, w); at = [(X(i) + X(j)) / 2, y0 - 12]; }
        else at = NLZ.carc(g, X(i), y0, X(j), y0, R, (j > i ? -1 : 1) * Math.min(90, 26 * Math.abs(j - i)), c, w);
        const tw0 = tw(g, lab, { s: 12, b: true, mono: true }) + 10;
        rr(g, at[0] - tw0 / 2, at[1] - 10, tw0, 19, 5, { fill: on ? z.col.orange : z.col.surf, stroke: on ? z.col.orange : z.col.line, w: 1 });
        D.text(g, lab, at[0], at[1] + 4, { a: 'center', s: 12, b: true, mono: true, c: on ? '#fff' : z.col.ink });
      });
      D.arrow(g, X(0) - R - 26, y0, X(0) - R - 1, y0, z.col.purple, 2);
      S.forEach((s, i) => {
        const on = s === live;
        D.circle(g, X(i), y0, R, { fill: on ? z.col.cv : z.col.surf, stroke: z.col.cv, w: 2.2 });
        if (F.has(s)) D.circle(g, X(i), y0, R - 4, { stroke: on ? '#fff' : z.col.cv, w: 1.5 });
        D.text(g, s, X(i), y0 + 5, { a: 'center', s: 12.5, b: true, mono: true, c: on ? '#fff' : z.col.ink });
      });
      /* the tape */
      const cw = Math.min(34, (z.W - 40) / Math.max(1, syms.length)), tx = 20;
      syms.forEach((s, i) => {
        const done = i < shown, bad = i === stuck && shown > stuck;
        rr(g, tx + i * (p.unit === 'word' ? 70 : cw), 12, (p.unit === 'word' ? 66 : cw - 4), 28, 5, { fill: bad ? z.col.red : done ? z.col.cv : z.col.bg, stroke: z.col.line, w: 1 });
        D.text(g, s, tx + i * (p.unit === 'word' ? 70 : cw) + (p.unit === 'word' ? 33 : (cw - 4) / 2), 31, { a: 'center', s: fit(g, s, p.unit === 'word' ? 60 : cw - 8, 13), b: true, mono: true, c: done || bad ? '#fff' : z.col.ink });
      });
      let verdict;
      if (shown < syms.length && !(stuck >= 0 && shown > stuck)) verdict = `Read ${shown} of ${syms.length} symbols. Now in <b>${esc(live)}</b>.`;
      else if (stuck >= 0) verdict = `<b>Rejected</b>: in ${esc(path[path.length - 1])} there is no arrow for "${esc(syms[stuck])}".`;
      else verdict = F.has(cur) ? `<b>Accepted</b>: the input ended in the final state ${esc(cur)}.` : `<b>Rejected</b>: the input ended in ${esc(cur)}, which is not a final state.`;
      return `${verdict} Five parts define the machine: states Q = {${S.map(esc).join(', ')}}, alphabet Σ = {${[...new Set(T.map(t => t[1]))].map(esc).join(', ')}}, start ${esc(S[0])}, transitions δ (${T.length} arrows) and finals F = {${[...F].map(esc).join(', ')}}.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 5.2: training an HMM by counting */
  const G5 = 'they/N can/M fish/V\nthey/N fish/V\nfish/N can/M swim/V\nthey/N can/V fish/N\nswim/V';
  def('hmmtrain', {
    title: 'Training an HMM is counting',
    sub: 'From tagged sentences, fill three tables: where sentences start (π), which tag follows which (A), and which word each tag emits (B).',
    W: 560, H: 270,
    params: [
      { k: 'train', label: 'Tagged sentences (word/TAG)', type: 'area', v: G5 },
      { k: 'view', label: 'Show', type: 'select', v: 'prob', opts: [['prob', 'probabilities (MLE)'], ['count', 'counts']] }
    ],
    tips: [
      { t: 'Problem G5. π = (N 4/5, V 1/5). N is followed by M or V half the time each. Read the zeros: N never follows N in this data.', set: { train: G5, view: 'prob' } },
      { t: 'Switch to counts to see where each fraction comes from. Every row of A and B is divided by its own total.', set: { view: 'count' } },
      { t: 'Add the sentence "fish/N fish/N". The cell N → N stops being 0 and the row of N is re-shared.', set: { train: G5 + '\nfish/N fish/N', view: 'prob' } }
    ],
    draw(z) {
      const { g, p } = z;
      const sents = readTagged(p.train);
      if (!sents.length) return 'Write tagged sentences such as "they/N can/M fish/V".';
      const tags = [], words = [];
      sents.flat().forEach(([w, t]) => { if (!tags.includes(t)) tags.push(t); if (!words.includes(w)) words.push(w); });
      tags.sort(); const Tg = tags.slice(0, 5), W = words.slice(0, 7);
      const st = new Map(), tr = new Map(), em = new Map(), outT = new Map(), outE = new Map();
      sents.forEach(s => { st.set(s[0][1], (st.get(s[0][1]) || 0) + 1); s.forEach(([w, t], i) => { em.set(t + '|' + w, (em.get(t + '|' + w) || 0) + 1); outE.set(t, (outE.get(t) || 0) + 1); if (i) { const k = s[i - 1][1] + '|' + t; tr.set(k, (tr.get(k) || 0) + 1); outT.set(s[i - 1][1], (outT.get(s[i - 1][1]) || 0) + 1); } }); });
      const cell = (n, d) => p.view === 'count' ? String(n) : frac(n, d);
      const box = (x, y, rows, cols, get, title, cw) => {
        D.text(g, title, x, y - 8, { s: 12, b: true, c: z.col.ink });
        cols.forEach((c, j) => D.text(g, c, x + 30 + j * cw + cw / 2, y + 14, { a: 'center', s: fit(g, c, cw - 4, 13), b: true, mono: true, c: z.col.ink2 }));
        rows.forEach((r, i) => {
          const yy = y + 22 + i * 28;
          D.text(g, r, x + 24, yy + 18, { a: 'right', s: 13, b: true, mono: true, c: z.col.ink2 });
          cols.forEach((c, j) => { const [n, d] = get(r, c); rr(g, x + 30 + j * cw + 1, yy + 1, cw - 2, 26, 5, { fill: n ? z.col.bg : 'transparent', stroke: z.col.line, w: 0.8 }); D.text(g, cell(n, d), x + 30 + j * cw + cw / 2, yy + 18, { a: 'center', s: fit(g, cell(n, d), cw - 6, 13), mono: true, b: !!n, c: n ? z.col.ink : z.col.red }); });
        });
      };
      box(10, 28, ['π'], Tg, (r, c) => [st.get(c) || 0, sents.length], 'Start π', 52);
      box(10, 112, Tg, Tg, (r, c) => [tr.get(r + '|' + c) || 0, outT.get(r) || 0], 'Transitions A (row → column)', 52);
      box(232, 28, Tg, W, (r, c) => [em.get(r + '|' + c) || 0, outE.get(r) || 0], 'Emissions B (tag → word)', Math.min(64, 290 / W.length));
      const zeros = [];
      Tg.forEach(a => Tg.forEach(b => { if (!tr.get(a + '|' + b) && outT.get(a)) zeros.push(`${a}→${b}`); }));
      return `MLE: π(t) = C(start with t) ÷ ${sents.length}, a(t → u) = C(t u) ÷ C(t followed by anything), b(w | t) = C(w tagged t) ÷ C(t). Unseen transitions such as ${zeros.slice(0, 4).map(esc).join(', ') || 'none'} are 0, so any tag sequence using them gets probability 0. Real taggers smooth A and B and add an end state.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 5.3: Viterbi and forward */
  const VB = {
    tags: 'N, M, V', pi: '0.7 0.1 0.2', A: '0.2 0.4 0.4\n0.1 0 0.9\n0.6 0.1 0.3',
    B: 'they 0.3 0 0\ncan 0.2 1 0.3\nfish 0.5 0 0.7'
  };
  def('viterbi', {
    title: 'The Viterbi trellis',
    sub: 'Columns are words, rows are tags. Each cell keeps only the best path into it and an arrow to where that path came from. Press Play to fill one column at a time.',
    W: 560, H: 236,
    params: [
      { k: 'tags', label: 'Tags', type: 'text', v: VB.tags },
      { k: 'pi', label: 'Start probabilities π', type: 'text', v: VB.pi },
      { k: 'A', label: 'Transitions A: one row per tag, P(next tag | this tag)', type: 'area', v: VB.A },
      { k: 'B', label: 'Emissions B: a word, then P(word | tag) for each tag', type: 'area', v: VB.B },
      { k: 'sent', label: 'Sentence', type: 'text', v: 'they can fish' },
      { k: 'mode', label: 'Combine paths with', type: 'select', v: 'max', opts: [['max', 'max (Viterbi: the best path)'], ['sum', 'sum (forward: the sentence probability)']] }
    ],
    steps: z => toks(z.p.sent).length, startAtZero: true,
    tips: [
      { t: 'Play "they can fish". The best path is N M V with 0.05292, "they are able to fish". The runner up N V N scores 0.00756.', set: { tags: VB.tags, pi: VB.pi, A: VB.A, B: VB.B, sent: 'they can fish', mode: 'max' }, play: true },
      { t: 'Problem G8: decode "fish can fish". The first word is ambiguous, yet the answer is again N M V, with 0.0882.', set: { tags: VB.tags, pi: VB.pi, A: VB.A, B: VB.B, sent: 'fish can fish', mode: 'max' }, play: true },
      { t: 'Switch to sum. The same table now adds the paths: P(they can fish) = 0.073164, so the model is 72% sure of N M V.', set: { tags: VB.tags, pi: VB.pi, A: VB.A, B: VB.B, sent: 'they can fish', mode: 'sum' }, play: true },
      { t: 'Make "can" more often a verb: set the can row to 0.2 0.3 0.9. The reading "they put fish in cans" now wins.', set: { tags: VB.tags, pi: VB.pi, A: VB.A, B: 'they 0.3 0 0\ncan 0.2 0.3 0.9\nfish 0.5 0 0.7', sent: 'they can fish', mode: 'max' }, play: true },
      { t: 'Problem G7: the HMM trained from the G5 corpus. Viterbi again picks N M V, now with 12/125 = 0.096.', set: { tags: 'N, M, V', pi: '0.8 0 0.2', A: '0 0.5 0.5\n0 0 1\n1 0 0', B: 'they 0.6 0 0\ncan 0 1 0.2\nfish 0.4 0 0.4\nswim 0 0 0.4', sent: 'they can fish', mode: 'max' }, play: true },
      { t: 'The slide 27 killer clown HMM with two tags. Only N N survives, with 0.045.', set: { tags: 'A, N', pi: '0.25 0.75', A: '0 1\n0.5 0.5', B: 'killer 0 0.3\nclown 0 0.4', sent: 'killer clown', mode: 'max' }, play: true },
      { t: 'Problem H8: British left waffles on Falkland Islands, with practice tables. Left as a verb wins, N V N P N N, 12.5 times ahead of the political reading.', set: { tags: 'N, V, P', pi: '0.6 0.3 0.1', A: '0.3 0.4 0.3\n0.5 0.1 0.4\n0.9 0.05 0.05', B: 'British 0.02 0 0\nleft 0.01 0.02 0\nwaffles 0.005 0.001 0\non 0 0 0.3\nFalkland 0.01 0 0\nIslands 0.01 0 0', sent: 'British left waffles on Falkland Islands', mode: 'max' }, play: true }
    ],
    draw(z) {
      const { g, p } = z;
      const tags = String(p.tags).split(',').map(s => s.trim()).filter(Boolean).slice(0, 4), q = tags.length;
      if (!q) return 'Name at least one tag.';
      const pi = nums(p.pi).slice(0, q); while (pi.length < q) pi.push(0);
      const A = String(p.A).split('\n').map(l => nums(l).slice(0, q)).filter(r => r.length).slice(0, q);
      while (A.length < q) A.push(Array(q).fill(0)); A.forEach(r => { while (r.length < q) r.push(0); });
      const B = new Map(); String(p.B).split('\n').forEach(l => { const t = toks(l); if (t.length >= 2) B.set(t[0], t.slice(1, q + 1).map(Number).concat(Array(q).fill(0)).slice(0, q)); });
      const ws = toks(p.sent).slice(0, 6), T = ws.length;
      if (!T) return 'Type a sentence.';
      const b = (j, w) => (B.get(w) || Array(q).fill(0))[j];
      const v = [], bp = [];
      for (let t = 0; t < T; t++) {
        v.push([]); bp.push([]);
        for (let j = 0; j < q; j++) {
          if (!t) { v[t][j] = pi[j] * b(j, ws[0]); bp[t][j] = -1; continue; }
          let best = -1, arg = -1, sum = 0;
          for (let i = 0; i < q; i++) { const c = v[t - 1][i] * A[i][j]; sum += c; if (c > best) { best = c; arg = i; } }
          v[t][j] = (p.mode === 'sum' ? sum : best) * b(j, ws[t]); bp[t][j] = v[t][j] > 0 ? arg : -1;
        }
      }
      const shown = Math.min(z.step, T);
      const x0 = 70, cw = (z.W - x0 - 14) / T, y0 = 44, rh = Math.min(58, 180 / q);
      const cx = t => x0 + t * cw + cw / 2, cy = j => y0 + j * rh + rh / 2;
      ws.forEach((w, t) => D.text(g, w, cx(t), 26, { a: 'center', s: fit(g, w, cw - 6, 14), b: true, c: t < shown ? z.col.ink : z.col.ink2 }));
      tags.forEach((s, j) => D.text(g, s, x0 - 14, cy(j) + 5, { a: 'right', s: 14, b: true, mono: true, c: z.col.ink }));
      /* best final cell and the back trace */
      const done = shown === T;
      let path = [];
      if (done && p.mode === 'max') { let j = 0; for (let k = 1; k < q; k++) if (v[T - 1][k] > v[T - 1][j]) j = k; if (v[T - 1][j] > 0) { for (let t = T - 1; t >= 0; t--) { path.unshift(j); j = bp[t][j]; } } }
      const onPath = (t, j) => path.length && path[t] === j;
      for (let t = 1; t < shown; t++) for (let j = 0; j < q; j++) {
        if (p.mode === 'max') { const i = bp[t][j]; if (i >= 0) D.arrow(g, cx(t - 1) + 38, cy(i), cx(t) - 40, cy(j), onPath(t, j) && onPath(t - 1, i) ? z.col.orange : z.col.line, onPath(t, j) && onPath(t - 1, i) ? 3 : 1.4); }
        else for (let i = 0; i < q; i++) if (v[t - 1][i] * A[i][j] > 0 && v[t][j] > 0) D.line(g, cx(t - 1) + 38, cy(i), cx(t) - 40, cy(j), z.col.line, 1);
      }
      for (let t = 0; t < T; t++) for (let j = 0; j < q; j++) {
        const vis = t < shown, val = v[t][j], hot = onPath(t, j);
        rr(g, cx(t) - 38, cy(j) - rh / 2 + 5, 76, rh - 10, 8, { fill: !vis ? z.col.bg : hot ? z.col.orange : val > 0 ? z.col.surf : z.col.bg, stroke: hot ? z.col.orange : z.col.line, w: 1.2 });
        if (vis) D.text(g, sci(val), cx(t), cy(j) + 5, { a: 'center', s: fit(g, sci(val), 70, 13), mono: true, b: val > 0, c: hot ? '#fff' : val > 0 ? z.col.ink : z.col.ink2 });
      }
      let msg;
      if (!shown) msg = 'Press Play or Step to fill the first column.';
      else if (!done) {
        const t = shown - 1;
        msg = t === 0 ? `Column 1: v(j) = π(j) × b<sub>j</sub>(${esc(ws[0])}). ${tags.map((s, j) => `${esc(s)}: ${fmt(pi[j], 3)} × ${fmt(b(j, ws[0]), 3)} = ${sci(v[0][j])}`).join(', ')}.`
          : `Column ${t + 1}: for each tag, ${p.mode === 'max' ? 'take the best' : 'add up'} v<sub>${t}</sub>(i) × a(i → j) over the ${q} previous tags, then multiply by b<sub>j</sub>(${esc(ws[t])}).${p.mode === 'max' ? ' The arrow points to the winning previous tag.' : ''}`;
      } else if (p.mode === 'max') {
        const pr = path.length ? v[T - 1][path[T - 1]] : 0;
        msg = path.length ? `Best path: <b>${ws.map((w, t) => `${esc(w)}/${esc(tags[path[t]])}`).join(' ')}</b> with P(words, tags) = <b>${sci(pr)}</b>. Found with ${T} × ${q}² = ${T * q * q} comparisons instead of scoring all ${q}<sup>${T}</sup> = ${q ** T} sequences.` : 'Every path has probability 0. Some word cannot be emitted by any reachable tag.';
      } else {
        const PW = v[T - 1].reduce((a, c) => a + c, 0);
        msg = `Forward: P(${esc(ws.join(' '))}) = Σ over all tag paths = <b>${sci(PW)}</b>. Divide the Viterbi score by this to get how sure the model is of its best path.`;
      }
      const bad = A.map((r, i) => Math.abs(r.reduce((a, c) => a + c, 0) - 1) > 1e-6 ? tags[i] : null).filter(Boolean);
      return msg + (bad.length ? ` <b>Check A:</b> the row of ${bad.map(esc).join(', ')} does not add to 1.` : '');
    }
  });

  def('searchsize', {
    title: 'Why brute force fails: q to the power T',
    sub: 'Brute force scores every tag sequence, q<sup>T</sup> of them. Viterbi does about T × q² steps. The vertical axis is a power of ten.',
    W: 560, H: 250,
    params: [
      { k: 'q', label: 'Number of tags q', type: 'range', min: 2, max: 90, v: 45 },
      { k: 'T', label: 'Sentence length T', type: 'range', min: 1, max: 40, v: 25 }
    ],
    tips: [
      { t: 'Penn Treebank, 45 tags, 25 words: 2.1 × 10⁴¹ sequences against 50,625 Viterbi steps.', set: { q: 45, T: 25 } },
      { t: 'Brown, 87 tags, 10 words: 2.5 × 10¹⁹ sequences against 75,690 steps.', set: { q: 87, T: 10 } },
      { t: 'The killer clown: 2 tags, 2 words. Brute force is fine for tiny cases, which is how the slide solved it.', set: { q: 2, T: 2 } }
    ],
    draw(z) {
      const { g, p } = z;
      const box = [62, 16, 330, 190];
      const brute = t => t * Math.log10(p.q), vit = t => Math.log10(t * p.q * p.q);
      const ymax = Math.max(4, Math.ceil(brute(40)));
      const m = D.axes(g, z, box, [1, 40], [0, ymax], { nx: 4, ny: 4, xl: 'sentence length T', fy: v => '10' + String(Math.round(v)).split('').map(c => ({ 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' }[c])).join(''), fx: v => String(Math.round(v)) });
      D.curve(g, brute, [1, 40], m, z.col.red, 2.4);
      D.curve(g, vit, [1, 40], m, z.col.purple, 2.4);
      D.line(g, m.sx(p.T), box[1], m.sx(p.T), box[1] + box[3], z.col.orange, 1.5, [4, 4]);
      D.circle(g, m.sx(p.T), m.sy(brute(p.T)), 5, { fill: z.col.red });
      D.circle(g, m.sx(p.T), m.sy(vit(p.T)), 5, { fill: z.col.purple });
      const lx = 412;
      D.text(g, 'brute force qᵀ', lx, 34, { s: 12, b: true, c: z.col.red });
      D.text(g, (p.q ** p.T).toExponential(2).replace('+', ''), lx, 54, { s: 13, mono: true, b: true, c: z.col.ink });
      D.text(g, 'Viterbi T × q²', lx, 90, { s: 12, b: true, c: z.col.purple });
      D.text(g, (p.T * p.q * p.q).toLocaleString(), lx, 110, { s: 13, mono: true, b: true, c: z.col.ink });
      wrap(g, 'At a billion sequences per second, 10⁴¹ would take far longer than the age of the universe.', lx, 150, 140, { s: 11.5, c: z.col.ink2 });
      return `With q = ${p.q} and T = ${p.T}: q<sup>T</sup> = ${(p.q ** p.T).toExponential(3).replace('e+', ' × 10<sup>') + '</sup>'} sequences, against ${(p.T * p.q * p.q).toLocaleString()} Viterbi steps. The red line is straight on this scale because it is exponential in T. The purple one is almost flat.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 5.4: IOB chunks and entities */
  def('iob', {
    title: 'IOB tags turn spans into a tagging problem',
    sub: 'B- begins a chunk, I- continues it, O is outside. Edit the tags and watch the spans change.',
    W: 560, H: 230,
    params: [
      { k: 'text', label: 'Tokens with tags (word/TAG)', type: 'area', v: 'United/B-ORG cancelled/O the/O flight/O from/O San/B-LOC Francisco/I-LOC' },
      { k: 'scheme', label: 'Also show', type: 'select', v: 'bioes', opts: [['none', 'nothing else'], ['bioes', 'the same spans in BIOES'], ['brackets', 'bracket notation']] }
    ],
    tips: [
      { t: 'The NER slide: two entities, [United] as an organisation and [San Francisco] as a location.', set: { text: 'United/B-ORG cancelled/O the/O flight/O from/O San/B-LOC Francisco/I-LOC' } },
      { t: 'Chunking with the same idea: [the yellow dog] is one noun phrase.', set: { text: 'We/B-NP saw/B-VP the/B-NP yellow/I-NP dog/I-NP ./O' } },
      { t: 'Problem H4: decode Sidharth Ranjan teaches at IIT Jodhpur.', set: { text: 'Sidharth/B-PER Ranjan/I-PER teaches/O at/O IIT/B-ORG Jodhpur/I-ORG' } },
      { t: 'Break it: change San to O. An I- after O is ill formed, and is repaired by treating it as a B-.', set: { text: 'United/B-ORG cancelled/O the/O flight/O from/O San/O Francisco/I-LOC' } }
    ],
    draw(z) {
      const { g, p } = z;
      const T = toks(p.text).slice(0, 10).map(t => { const i = t.lastIndexOf('/'); return i > 0 ? [t.slice(0, i), t.slice(i + 1)] : [t, 'O']; });
      if (!T.length) return 'Write tokens like "San/B-LOC".';
      const spans = []; let cur = null, fixed = 0;
      T.forEach(([w, t], i) => {
        const m = t.match(/^([BI])-(.+)$/);
        if (!m) { cur = null; return; }
        if (m[1] === 'B' || !cur || cur.type !== m[2]) { if (m[1] === 'I') fixed++; cur = { type: m[2], a: i, b: i }; spans.push(cur); }
        else cur.b = i;
      });
      const types = [...new Set(spans.map(s => s.type))];
      const pal = [z.col.cv, z.col.orange, z.col.purple, z.col.green, z.col.pink];
      const colOf = ty => pal[types.indexOf(ty) % pal.length];
      const gap = 6, fs = 13;
      const ws = T.map(([w]) => tw(g, w, { s: fs, b: true }) + 18);
      const tot = ws.reduce((a, c) => a + c, 0) + gap * (T.length - 1), sc = Math.min(1, (z.W - 24) / tot);
      let x = 12; const xs = [];
      T.forEach(([w, t], i) => { xs.push(x); const ww = ws[i] * sc; const sp = spans.find(s => i >= s.a && i <= s.b); rr(g, x, 40, ww, 30, 7, { fill: sp ? colOf(sp.type) : z.col.surf, stroke: sp ? colOf(sp.type) : z.col.line }); D.text(g, w, x + ww / 2, 60, { a: 'center', s: fit(g, w, ww - 6, fs), b: true, c: sp ? '#fff' : z.col.ink }); D.text(g, t, x + ww / 2, 90, { a: 'center', s: fit(g, t, ww, 11.5), mono: true, b: true, c: sp ? colOf(sp.type) : z.col.ink2 }); x += ww + gap * sc; });
      spans.forEach(s => { const x1 = xs[s.a], x2 = xs[s.b] + ws[s.b] * sc; D.line(g, x1, 104, x2, 104, colOf(s.type), 3); D.text(g, s.type, (x1 + x2) / 2, 122, { a: 'center', s: 12, b: true, c: colOf(s.type) }); });
      D.text(g, 'tags', 12, 28, { s: 11, b: true, c: z.col.ink2 });
      if (p.scheme !== 'none') {
        D.text(g, p.scheme === 'bioes' ? 'BIOES' : 'brackets', 12, 160, { s: 11, b: true, c: z.col.ink2 });
        if (p.scheme === 'bioes') T.forEach(([w], i) => { const s = spans.find(s => i >= s.a && i <= s.b); const t = !s ? 'O' : s.a === s.b ? 'S-' + s.type : i === s.a ? 'B-' + s.type : i === s.b ? 'E-' + s.type : 'I-' + s.type; D.text(g, t, xs[i] + ws[i] * sc / 2, 182, { a: 'center', s: fit(g, t, ws[i] * sc, 11.5), mono: true, b: true, c: s ? colOf(s.type) : z.col.ink2 }); });
        else { let s = ''; T.forEach(([w], i) => { const a = spans.find(q => q.a === i), b = spans.find(q => q.b === i); s += (a ? '[' : '') + w + (b ? ']' + b.type : '') + ' '; }); wrap(g, s.trim(), 12, 182, z.W - 24, { s: 13, mono: true, b: true, c: z.col.ink }); }
      }
      return `${spans.length} span${spans.length === 1 ? '' : 's'}: ${spans.map(s => `[${esc(T.slice(s.a, s.b + 1).map(r => r[0]).join(' '))}] ${esc(s.type)}`).join(', ') || 'none'}. ${fixed ? `<b>${fixed} ill formed I- tag${fixed > 1 ? 's were' : ' was'} repaired</b> by starting a new span. ` : ''}Chunks are flat and never nest, which is why chunking is called shallow parsing. Any tagger (HMM, CRF, neural) can learn these tags.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 5.5: trees */
  function parseS(s) {
    const t = String(s).replace(/\(/g, ' ( ').replace(/\)/g, ' ) ').split(/\s+/).filter(Boolean);
    let i = 0, id = 0;
    function node() {
      if (t[i] !== '(') return { label: t[i++], leaf: true, id: id++ };
      i++; const n = { label: t[i++] || '?', kids: [], id: id++ };
      while (i < t.length && t[i] !== ')') n.kids.push(node());
      i++; return n;
    }
    try { const r = node(); return r && r.label ? r : null; } catch (e) { return null; }
  }
  NLZ.parseS = parseS;
  /* lay out a tree: leaves evenly spaced on the bottom row, parents centred over their children */
  function drawTree(g, z, root, box, o = {}) {
    const [X, Y, W, H] = box;
    const leaves = []; let depth = 0;
    (function walk(n, d) { n.d = d; depth = Math.max(depth, d); if (n.leaf) leaves.push(n); else n.kids.forEach(k => walk(k, d + 1)); })(root, 0);
    const lw = W / Math.max(1, leaves.length), lh = Math.min(o.lh || 46, H / Math.max(1, depth));
    leaves.forEach((n, i) => { n.x = X + lw * (i + 0.5); n.y = Y + H; });
    (function pos(n) { if (n.leaf) return; n.kids.forEach(pos); n.x = (n.kids[0].x + n.kids[n.kids.length - 1].x) / 2; n.y = Y + n.d * lh; })(root);
    (function edges(n) { if (n.leaf) return; n.kids.forEach(k => { const hot = o.hi && o.hi(n, k); D.line(g, n.x, n.y + 9, k.x, k.y - 10, hot ? z.col.orange : z.col.line, hot ? 3 : 1.5); edges(k); }); })(root);
    (function nodes(n) {
      const s = n.label, fs = n.leaf ? 12.5 : 12;
      const w = Math.min(lw * (n.leaf ? 1.45 : 1.6), tw(g, s, { s: fs, b: true, mono: !n.leaf }) + 12);
      const hot = o.hiNode && o.hiNode(n);
      if (!n.leaf) rr(g, n.x - w / 2, n.y - 10, w, 20, 6, { fill: hot ? z.col.orange : z.col.cv });
      D.text(g, s, n.x, n.y + 4.5, { a: 'center', s: fit(g, s, w - 4, fs, { b: true, mono: !n.leaf }), b: true, mono: !n.leaf, c: n.leaf ? z.col.ink : '#fff' });
      if (!n.leaf) n.kids.forEach(nodes);
    })(root);
    return { leaves, depth };
  }
  NLZ.drawTree = drawTree;
  const span = n => n.leaf ? [n.label] : n.kids.flatMap(span);
  def('parsetree', {
    title: 'Constituency trees from bracket notation',
    sub: 'Type a tree in brackets, as treebanks store it. Each coloured node is a constituent: a group of words that acts as one unit.',
    W: 560, H: 260,
    params: [
      { k: 'tree', label: 'Tree in brackets', type: 'area', v: '(S (NP (N Fed)) (VP (V raises) (NP (N interest) (N rates))))' }
    ],
    tips: [
      { t: 'The slide\'s headline: Fed raises interest rates, with the verb phrase "raises interest rates" as the predicate.', set: { tree: '(S (NP (N Fed)) (VP (V raises) (NP (N interest) (N rates))))' } },
      { t: 'The other reading of the same headline: "Fed raises" are the subject and "interest" is the verb, as in "Fed raises interest rates of teenagers".', set: { tree: '(S (NP (N Fed) (N raises)) (VP (V interest) (NP (N rates))))' } },
      { t: 'Problem H5: the dog chased a cat. Count 4 phrase nodes, 5 part of speech nodes and 5 leaves.', set: { tree: '(S (NP (Det the) (N dog)) (VP (V chased) (NP (Det a) (N cat))))' } },
      { t: 'The elephant with the PP inside the verb phrase: I was in my pajamas.', set: { tree: '(S (NP (Pro I)) (VP (VP (V shot) (NP (Det an) (N elephant))) (PP (P in) (NP (Det my) (N pajamas)))))' } }
    ],
    draw(z) {
      const { g, p } = z;
      const r = parseS(p.tree);
      if (!r || r.leaf) return 'Write a tree such as (S (NP (N Fed)) (VP (V raises))).';
      const { leaves } = drawTree(g, z, r, [16, 24, z.W - 32, z.H - 50]);
      let phr = 0, pre = 0; const cons = [];
      (function walk(n) { if (n.leaf) return; if (n.kids.length === 1 && n.kids[0].leaf) pre++; else { phr++; cons.push(`[${esc(span(n).join(' '))}]<sub>${esc(n.label)}</sub>`); } n.kids.forEach(walk); })(r);
      return `${phr} phrase nodes, ${pre} part of speech nodes, ${leaves.length} words. Constituents: ${cons.join(', ')}. Each phrase contains a head of its own kind: an NP has a noun, a VP a verb.`;
    }
  });

  def('deptree', {
    title: 'Dependency trees: every word points to its head',
    sub: 'Each line gives a word, the number of its head (0 for the root) and the relation. Arcs go from head to dependent.',
    W: 560, H: 240,
    params: [
      { k: 'rows', label: 'word head relation (one per line, words numbered from 1)', type: 'area', v: 'The 2 det\nboy 3 subj\nput 0 root\nthe 5 det\ntortoise 3 obj\non 3 prep\nthe 8 det\nrug 6 pobj' }
    ],
    tips: [
      { t: 'The slide: put has three children, boy, tortoise and on. The and rug are grandchildren, not children.', set: { rows: 'The 2 det\nboy 3 subj\nput 0 root\nthe 5 det\ntortoise 3 obj\non 3 prep\nthe 8 det\nrug 6 pobj' } },
      { t: 'Universal Dependencies makes content words heads: put → rug (obl) and rug → on (case). Same sentence, different design choice.', set: { rows: 'The 2 det\nboy 3 nsubj\nput 0 root\nthe 5 det\ntortoise 3 obj\non 8 case\nthe 8 det\nrug 3 obl' } },
      { t: 'Problem H7: The student reads books. Four words, four arcs including the root.', set: { rows: 'The 2 det\nstudent 3 nsubj\nreads 0 root\nbooks 3 obj' } },
      { t: 'Break it: make boy\'s head 5 and tortoise\'s head 2. The arcs now cycle, and the readout says it is not a tree.', set: { rows: 'The 2 det\nboy 5 subj\nput 0 root\nthe 5 det\ntortoise 2 obj\non 3 prep\nthe 8 det\nrug 6 pobj' } }
    ],
    draw(z) {
      const { g, p } = z;
      const R = String(p.rows).split('\n').map(toks).filter(a => a.length >= 2).slice(0, 10).map(a => ({ w: a[0], h: +a[1] || 0, rel: a[2] || '' }));
      const n = R.length;
      if (!n) return 'Write lines like "boy 3 subj".';
      const fs = 13.5, wsz = R.map(r => tw(g, r.w, { s: fs, b: true }) + 14);
      const tot = wsz.reduce((a, c) => a + c, 0), gap = Math.max(6, (z.W - 24 - tot) / Math.max(1, n - 1));
      let x = 12; const cx = [];
      R.forEach((r, i) => { cx.push(x + wsz[i] / 2); x += wsz[i] + gap; });
      const base = z.H - 50;
      R.forEach((r, i) => { rr(g, cx[i] - wsz[i] / 2, base, wsz[i], 26, 6, { fill: r.h === 0 ? z.col.cv : z.col.surf, stroke: z.col.cv }); D.text(g, r.w, cx[i], base + 18, { a: 'center', s: fs, b: true, c: r.h === 0 ? '#fff' : z.col.ink }); D.text(g, String(i + 1), cx[i], base + 40, { a: 'center', s: 10, c: z.col.ink2 }); });
      /* arcs: height grows with distance */
      const arcs = R.map((r, i) => ({ d: i, h: r.h - 1, rel: r.rel })).filter(a => a.h >= 0 && a.h < n && a.h !== a.d);
      const crosses = (a, b) => { const [a1, a2] = [Math.min(a.d, a.h), Math.max(a.d, a.h)], [b1, b2] = [Math.min(b.d, b.h), Math.max(b.d, b.h)]; return (a1 < b1 && b1 < a2 && a2 < b2) || (b1 < a1 && a1 < b2 && b2 < a2); };
      let cross = 0; arcs.forEach((a, i) => arcs.forEach((b, j) => { if (i < j && crosses(a, b)) cross++; }));
      const tags = [];
      arcs.forEach(a => {
        const x1 = cx[a.h], x2 = cx[a.d], ht = Math.min(base - 30, 26 + 30 * Math.abs(a.d - a.h));
        g.save(); g.strokeStyle = z.col.purple; g.lineWidth = 1.8; g.beginPath(); g.moveTo(x1, base - 2); g.bezierCurveTo(x1, base - ht, x2, base - ht, x2, base - 4); g.stroke(); g.restore();
        D.arrow(g, x2, base - 12, x2, base - 2, z.col.purple, 1.8);
        const lx = (x1 + x2) / 2, lwid = tw(g, a.rel, { s: 11, b: true }) + 8;
        /* move a relation label along its arc until it does not cover an earlier label */
        let ly = base - ht * 0.75 - 4;
        const hit = yy => tags.some(r => lx - lwid / 2 < r[0] + r[2] && lx + lwid / 2 > r[0] && yy - 9 < r[1] + 16 && yy + 7 > r[1]);
        for (let k = 1; k < 7 && hit(ly); k++) ly = base - ht * 0.75 - 4 + (k % 2 ? 1 : -1) * Math.ceil(k / 2) * 17;
        tags.push([lx - lwid / 2, ly - 9, lwid]);
        rr(g, lx - lwid / 2, ly - 9, lwid, 16, 4, { fill: z.col.surf });
        D.text(g, a.rel, lx, ly + 3, { a: 'center', s: 11, b: true, c: z.col.purple });
      });
      const roots = R.filter(r => r.h === 0).length;
      let cyc = false;
      R.forEach((r, i) => { let k = i, seen = new Set(); while (k >= 0 && R[k] && R[k].h !== 0) { if (seen.has(k)) { cyc = true; break; } seen.add(k); k = R[k].h - 1; } });
      const kids = R.map((r, i) => ({ w: r.w, c: R.filter(q => q.h === i + 1).map(q => q.w) })).filter(k => k.c.length);
      const ok = roots === 1 && !cyc;
      return `${ok ? '<b>A valid tree</b>: one root, every word has one head, no cycles, ' + n + ' arcs including the root.' : `<b>Not a tree</b>: ${roots !== 1 ? `${roots} roots` : ''}${roots !== 1 && cyc ? ' and ' : ''}${cyc ? 'a cycle' : ''}.`} ${cross ? `${cross} pair${cross > 1 ? 's' : ''} of arcs cross, so it is not projective.` : 'No arcs cross, so it is projective.'} ${kids.map(k => `${esc(k.w)} has ${andList(k.c.map(esc))} as ${k.c.length > 1 ? 'children' : 'its child'}.`).join(' ')}`;
    }
  });

  def('pcfg', {
    title: 'A PCFG decides who wore the pajamas',
    sub: 'Both parses use the same rules except one. Change the rule probabilities and see which attachment wins.',
    W: 560, H: 280,
    params: [
      { k: 'vppp', label: 'P(VP → VP PP)', type: 'range', min: 0, max: 1, step: 0.01, v: 0.3 },
      { k: 'nppp', label: 'P(NP → NP PP)', type: 'range', min: 0, max: 1, step: 0.01, v: 0.2 },
      { k: 'npdn', label: 'P(NP → Det N)', type: 'range', min: 0, max: 1, step: 0.01, v: 0.5 }
    ],
    tips: [
      { t: 'Problem H9: VP → VP PP 0.3, NP → NP PP 0.2. The verb attachment wins by 0.21 to 0.14, a ratio of 1.5: I was in my pajamas.', set: { vppp: 0.3, nppp: 0.2, npdn: 0.5 } },
      { t: 'Raise NP → NP PP to 0.4. Now the elephant wears the pajamas. Nothing about elephants or pajamas was used: a plain PCFG only sees rule counts.', set: { vppp: 0.3, nppp: 0.4, npdn: 0.5 } },
      { t: 'Find the tie: with VP → VP PP = 0.3, the parses are equal when (1 − 0.3) × NP → NP PP equals 0.3 × 0.7, that is NP → NP PP = 0.3.', set: { vppp: 0.3, nppp: 0.3, npdn: 0.5 } }
    ],
    draw(z) {
      const { g, p } = z;
      const vpv = 1 - p.vppp, pro = 1 - p.nppp - p.npdn;
      const t1 = parseS('(S (NP (Pro I)) (VP (VP (V shot) (NP (Det an) (N elephant))) (PP (P in) (NP (Det my) (N pajamas)))))');
      const t2 = parseS('(S (NP (Pro I)) (VP (V shot) (NP (NP (Det an) (N elephant)) (PP (P in) (NP (Det my) (N pajamas))))))');
      const hi1 = (n, k) => n.label === 'VP' && k.label === 'PP', hi2 = (n, k) => n.label === 'NP' && k.label === 'PP';
      drawTree(g, z, t1, [8, 28, 268, 196], { hi: hi1, hiNode: n => n.label === 'VP' && n.kids.some(k => k.label === 'PP') });
      drawTree(g, z, t2, [284, 28, 268, 196], { hi: hi2, hiNode: n => n.label === 'NP' && n.kids.some(k => k.label === 'PP') });
      const shared = 1 * Math.max(0, pro) * p.npdn * 1 * p.npdn;
      const P1 = shared * p.vppp * vpv, P2 = shared * vpv * p.nppp;
      D.text(g, 'PP attached to the verb phrase', 142, 14, { a: 'center', s: 12, b: true, c: P1 >= P2 ? z.col.orange : z.col.ink2 });
      D.text(g, 'PP attached to the noun phrase', 418, 14, { a: 'center', s: 12, b: true, c: P2 > P1 ? z.col.orange : z.col.ink2 });
      D.text(g, `rules ∝ ${fmt(p.vppp, 2)} × ${fmt(vpv, 2)} = ${fmt(p.vppp * vpv, 4)}`, 142, 266, { a: 'center', s: 12, mono: true, b: true, c: z.col.ink });
      D.text(g, `rules ∝ ${fmt(vpv, 2)} × ${fmt(p.nppp, 2)} = ${fmt(vpv * p.nppp, 4)}`, 418, 266, { a: 'center', s: 12, mono: true, b: true, c: z.col.ink });
      const warn = pro < -1e-9 ? ` <b>Check the NP rules:</b> NP → NP PP and NP → Det N already add to ${fmt(p.nppp + p.npdn, 2)}, leaving nothing for NP → Pro.` : '';
      const ratio = P2 > 0 ? P1 / P2 : Infinity;
      return `VP → V NP = 1 − ${fmt(p.vppp, 2)} = ${fmt(vpv, 2)} and NP → Pro = ${fmt(Math.max(0, pro), 2)}, so each left hand side adds to 1. The shared rules give the same factor ${fmt(shared, 4)} to both trees, so only the orange rules decide. Full rule products: ${fmt(P1, 5)} against ${fmt(P2, 5)}, ratio ${isFinite(ratio) ? fmt(ratio, 3) : '∞'}. ${P1 > P2 ? 'Verb attachment: I was wearing them.' : P2 > P1 ? 'Noun attachment: the elephant was wearing them.' : 'A tie.'}${warn}`;
    }
  });
})();
