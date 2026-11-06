/* ===== Core AI animations, part 2: AND OR search, logic, planning, probability and reinforcement learning.
   Same rules as part 1 (assets/coreai.js): every animation starts empty and each Step adds one explained piece. ===== */
(() => {
  const { trace, esc } = CAI;
  const { D } = CVZ;
  const { tag, rr, tw, fit, wrap } = AIZ;

  /* =====================================================================================================
     3.4  AND OR search in the erratic and slippery vacuum worlds (AIMA 4.3)
     ===================================================================================================== */
  /* state numbers of AIMA figure 4.9: [location, A dirty, B dirty] */
  const VS = { 1: ['A', 1, 1], 2: ['B', 1, 1], 3: ['A', 1, 0], 4: ['B', 1, 0], 5: ['A', 0, 1], 6: ['B', 0, 1], 7: ['A', 0, 0], 8: ['B', 0, 0] };
  const vnum = (l, a, b) => +Object.keys(VS).find(k => VS[k][0] === l && VS[k][1] === a && VS[k][2] === b);
  function vres(s, act, world) {
    const [l, a, b] = VS[s];
    const here = l === 'A' ? a : b;
    if (act === 'Suck') {
      const clean = l === 'A' ? vnum(l, 0, b) : vnum(l, a, 0);
      if (world !== 'erratic') return [clean];
      if (here) { const both = vnum(l, 0, 0); return clean === both ? [clean] : [clean, both]; }
      const dirty = l === 'A' ? vnum(l, 1, b) : vnum(l, a, 1);
      return [s, dirty];
    }
    const to = act === 'Right' ? vnum('B', a, b) : vnum('A', a, b);
    if (world === 'slippery' && to !== s) return [to, s];
    return [to];
  }
  const goalV = s => s === 7 || s === 8;
  function planStr(pl) {
    if (!pl.length) return '[]';
    return '[' + pl.map(x => typeof x === 'string' ? x : x.map((c, i) => i === x.length - 1 ? `else ${planStr(c.p)}` : `${i ? 'else if' : 'if'} State = ${c.s} then ${planStr(c.p)}`).join(' ')).join(', ') + ']';
  }
  trace('andor', {
    title: 'AND OR search for a plan that works whatever happens',
    sub: 'OR rows: the agent picks one action. AND rows: nature picks the outcome, so every outcome needs its own plan. The little picture shows squares A and B, dirt as brown dots and the robot as a blue dot.',
    W: 600, H: 430,
    params: [
      { k: 'world', label: 'World', type: 'select', v: 'erratic', opts: [['erratic', 'Erratic vacuum: Suck sometimes also cleans the other square, or drops dirt on a clean one'], ['slippery', 'Slippery vacuum: Left and Right sometimes fail'], ['det', 'Ordinary vacuum: every action does exactly one thing']] },
      { k: 's', label: 'Start state (1 to 8, numbered as in the textbook)', type: 'range', v: 1, min: 1, max: 8 }
    ],
    tips: [
      { t: 'The textbook example. From state 1, Suck leads to 5 or 7. State 7 is a goal. For 5, Suck could make things worse (back to 1, a loop), so the search tries Right and then Suck. The plan: [Suck, if State = 5 then [Right, Suck] else []].', set: { world: 'erratic', s: 1 }, play: true },
      { t: 'The slippery world. Right may leave the robot where it is, so every plan runs into a state already on its path, and AND OR search finds no plan without loops. A cyclic plan with a label does work: keep trying Right until it succeeds.', set: { world: 'slippery', s: 1 }, play: true },
      { t: 'The ordinary world. Every AND node has just one outcome, so AND OR search is plain depth first search and the plan is a simple list of actions.', set: { world: 'det', s: 1 }, play: true }
    ],
    frames(p) {
      const rows = [], fr = [];
      const snap = (say, cur) => fr.push({ rows: rows.map(r => ({ ...r })), cur, say });
      const W = p.world;
      let guard = 0;
      function orS(s, path, d) {
        const row = { d, kind: 'or', s, st: 'open', txt: '' };
        rows.push(row); const me = rows.length - 1;
        if (guard++ > 60) { row.st = 'fail'; row.txt = 'stopped, too long'; return null; }
        if (goalV(s)) { row.st = 'goal'; row.txt = 'goal, nothing more to do'; snap(`OR node: state ${s}. Both squares are clean, so this is a goal. The plan here is the empty plan [].`, me); return []; }
        if (path.includes(s)) { row.st = 'loop'; row.txt = 'already on this path: a loop, give up here'; snap(`OR node: state ${s} is already on the path from the start (${path.slice().reverse().join(', ')}). Going on would loop, so this branch fails.`, me); return null; }
        snap(`OR node: state ${s}. It is not a goal. The agent may choose any action, so try them in the order Suck, Right, Left until one works.`, me);
        for (const a of ['Suck', 'Right', 'Left']) {
          const res = vres(s, a, W);
          const plan = andS(res, [s].concat(path), d + 1, a, s);
          if (plan) { row.st = 'ok'; row.txt = 'solved by ' + a; row.plan = [a].concat(plan); snap(`Back at state ${s}: action <b>${a}</b> works for every outcome, so the plan from ${s} is ${esc(planStr(row.plan))}.`, me); return row.plan; }
        }
        row.st = 'fail'; row.txt = 'no action works';
        snap(`Back at state ${s}: no action leads to a plan, so state ${s} fails.`, me);
        return null;
      }
      function andS(res, path, d, a, from) {
        const row = { d, kind: 'and', st: 'open', txt: `${a} from ${from} gives {${res.join(', ')}}` };
        rows.push(row); const me = rows.length - 1;
        snap(`AND node: doing ${a} in state ${from} can end in ${res.length === 1 ? 'only state ' + res[0] : 'state ' + res.join(' or state ')}. ${res.length > 1 ? 'We cannot choose which, so we need a plan for every one of them.' : 'There is just one outcome.'}`, me);
        const parts = [];
        for (const s of res) {
          const pl = orS(s, path, d + 1);
          if (!pl) { row.st = 'fail'; snap(`AND node fails: state ${s} has no plan, so ${a} from ${from} cannot be trusted.`, me); return null; }
          parts.push({ s, p: pl });
        }
        row.st = 'ok';
        snap(`AND node solved: every outcome of ${a} from ${from} has a plan.`, me);
        return parts.length === 1 ? parts[0].p : [parts];
      }
      const plan = orS(p.s, [], 0);
      if (plan) snap(`Done. The conditional plan from state ${p.s} is <b>${esc(planStr(plan))}</b>. It reaches a clean world whatever the outcomes turn out to be.`, 0);
      else if (W === 'slippery') snap(`AND OR search fails: every plan meets a state already on its path. No plan without loops exists. A <b>cyclic plan</b> does exist, for example from state 1: [Suck, L1: Right, if State = 5 then L1 else Suck]. It keeps trying Right, and it works as long as each try has some chance to succeed.`, 0);
      else snap('AND OR search fails: no plan reaches a goal from this state for every outcome.', 0);
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const MAXR = 20, H0 = 24, RH = 19.5;
      let rows = f.rows, off = 0;
      if (rows.length > MAXR) { off = rows.length - MAXR; rows = rows.slice(off); D.text(g, `(${off} earlier rows above, open "Earlier steps" to read them)`, 20, 14, { s: 10.5, c: c.ink2 }); }
      rows.forEach((r, i) => {
        const y = H0 + i * RH + 8, x = 16 + r.d * 22;
        const col = r.st === 'ok' || r.st === 'goal' ? c.green : r.st === 'fail' || r.st === 'loop' ? c.red : c.orange;
        if (r.d > 0) D.line(g, x - 12, y - RH + 6, x - 12, y, c.line, 1), D.line(g, x - 12, y, x - 2, y, c.line, 1);
        const cur = i + off === f.cur;
        if (r.kind === 'or') {
          const [l, a, b] = VS[r.s];
          [['A', a], ['B', b]].forEach(([q, dirty], k) => {
            const bx = x + k * 15;
            g.save(); g.fillStyle = c.bg; g.strokeStyle = cur ? c.cv : c.line; g.lineWidth = cur ? 2 : 1; g.fillRect(bx, y - 7, 14, 14); g.strokeRect(bx, y - 7, 14, 14); g.restore();
            if (dirty) { D.circle(g, bx + 4, y + 3, 2, { fill: '#92400e' }); D.circle(g, bx + 10, y - 2, 2, { fill: '#92400e' }); }
            if (l === q) D.circle(g, bx + 7, y, 3.5, { fill: c.cv });
          });
          D.text(g, 'state ' + r.s, x + 36, y + 4, { s: 12, b: true, c: cur ? c.cv : c.ink });
          if (r.txt) D.text(g, r.txt, x + 92, y + 4, { s: 11, c: col, b: r.st !== 'open' });
        } else {
          D.circle(g, x + 7, y, 7, { fill: c.surf, stroke: cur ? c.cv : col, w: cur ? 2.5 : 1.5 });
          D.text(g, '&', x + 7, y + 1, { a: 'center', bl: 'middle', s: 9, b: true, c: c.ink });
          D.text(g, r.txt, x + 20, y + 4, { s: 11.5, c: cur ? c.cv : c.ink2, b: cur });
          if (r.st !== 'open') D.text(g, r.st === 'ok' ? 'all outcomes solved' : 'fails', x + 26 + tw(g, r.txt, { s: 11.5, b: cur }), y + 4, { s: 11, b: true, c: col });
        }
      });
    }
  });
  /* =====================================================================================================
     7.x  A small logic toolkit shared by the logic animations: a parser for propositional and first order
     sentences, printing, truth values, conversion to clauses and unification.
     ===================================================================================================== */
  const LG = (() => {
    function lex(s) {
      s = String(s).replace(/<=>|<->|⇔/g, ' ⇔ ').replace(/=>|->|⇒/g, ' ⇒ ').replace(/[~!¬]/g, ' ¬ ')
        .replace(/&|∧|\^/g, ' ∧ ').replace(/\|\||\||∨/g, ' ∨ ').replace(/\bforall\b|∀/gi, ' ∀ ').replace(/\bexists\b|∃/gi, ' ∃ ')
        .replace(/[(),]/g, m => ' ' + m + ' ');
      return s.split(/\s+/).filter(Boolean);
    }
    function parse(text) {
      const t = lex(text);
      let i = 0;
      const peek = () => t[i], take = x => { if (x && t[i] !== x) throw new Error(`Expected "${x}" but found "${t[i] || 'the end'}" in: ${text}`); return t[i++]; };
      const isName = w => w && /^[A-Za-z_][A-Za-z0-9_]*$/.test(w);
      function term() {
        const w = take();
        if (!isName(w)) throw new Error(`"${w || 'the end'}" is not a name, in: ${text}`);
        if (peek() === '(') { take('('); const args = [term()]; while (peek() === ',') { take(','); args.push(term()); } take(')'); return { t: 'fn', name: w, args }; }
        return /^[a-z]/.test(w) ? { t: 'var', name: w } : { t: 'const', name: w };
      }
      function prim() {
        const w = peek();
        if (w === '(') { take('('); const a = iff(); take(')'); return a; }
        if (w === '¬') { take(); return { op: 'not', a: prim() }; }
        if (w === '∀' || w === '∃') { take(); const vs = []; while (isName(peek()) && /^[a-z]/.test(peek())) vs.push(take()); if (!vs.length) throw new Error(`A quantifier needs a variable in lower case, in: ${text}`); let body = iff(); for (let k = vs.length - 1; k >= 0; k--) body = { op: w === '∀' ? 'all' : 'ex', v: vs[k], a: body }; return body; }
        if (!isName(w)) throw new Error(`Unexpected "${w || 'end of input'}" in: ${text}`);
        take();
        if (w === 'True' || w === 'False') return { op: w === 'True' ? 'T' : 'F' };
        const args = [];
        if (peek() === '(') { take('('); args.push(term()); while (peek() === ',') { take(','); args.push(term()); } take(')'); }
        return { op: 'atom', pred: w, args };
      }
      function and() { let a = prim(); while (peek() === '∧') { take(); a = { op: 'and', a, b: prim() }; } return a; }
      function or() { let a = and(); while (peek() === '∨') { take(); a = { op: 'or', a, b: and() }; } return a; }
      function imp() { const a = or(); if (peek() === '⇒') { take(); return { op: 'imp', a, b: imp() }; } return a; }
      function iff() { let a = imp(); while (peek() === '⇔') { take(); a = { op: 'iff', a, b: imp() }; } return a; }
      const r = iff();
      if (i < t.length) throw new Error(`Could not read "${t.slice(i).join(' ')}" in: ${text}`);
      return r;
    }
    const PR = { iff: 1, imp: 2, or: 3, and: 4, not: 5, all: 0, ex: 0, atom: 6, T: 6, F: 6 };
    const tstr = x => x.t === 'fn' ? `${x.name}(${x.args.map(tstr).join(', ')})` : x.name;
    function str(n, outer = 0) {
      let s;
      switch (n.op) {
        case 'atom': s = n.args.length ? `${n.pred}(${n.args.map(tstr).join(', ')})` : n.pred; break;
        case 'T': s = 'True'; break;
        case 'F': s = 'False'; break;
        case 'not': s = '¬' + str(n.a, 5); break;
        case 'and': s = str(n.a, 4) + ' ∧ ' + str(n.b, 4.1); break;
        case 'or': s = str(n.a, 3) + ' ∨ ' + str(n.b, 3.1); break;
        case 'imp': s = str(n.a, 2.1) + ' ⇒ ' + str(n.b, 2); break;
        case 'iff': s = str(n.a, 1) + ' ⇔ ' + str(n.b, 1.1); break;
        case 'all': case 'ex': s = (n.op === 'all' ? '∀' : '∃') + n.v + ' ' + str(n.a, 0); break;
      }
      const p = PR[n.op];
      return (p < outer || ((n.op === 'all' || n.op === 'ex') && outer > 0)) ? '(' + s + ')' : s;
    }
    function syms(n, out = []) {
      if (n.op === 'atom') { const k = str(n); if (!out.includes(k)) out.push(k); }
      ['a', 'b'].forEach(k => n[k] && syms(n[k], out));
      return out;
    }
    function val(n, m) {
      switch (n.op) {
        case 'atom': return !!m[str(n)];
        case 'T': return true;
        case 'F': return false;
        case 'not': return !val(n.a, m);
        case 'and': return val(n.a, m) && val(n.b, m);
        case 'or': return val(n.a, m) || val(n.b, m);
        case 'imp': return !val(n.a, m) || val(n.b, m);
        case 'iff': return val(n.a, m) === val(n.b, m);
      }
      throw new Error('Quantifiers are not allowed here.');
    }
    /* conversion to conjunctive normal form, keeping each stage for the explanation */
    function noIff(n) {
      if (n.op === 'iff') { const a = noIff(n.a), b = noIff(n.b); return { op: 'and', a: { op: 'imp', a, b }, b: { op: 'imp', a: b, b: a } }; }
      return n.a ? Object.assign({}, n, { a: noIff(n.a), b: n.b && noIff(n.b) }) : n;
    }
    function noImp(n) {
      if (n.op === 'imp') return { op: 'or', a: { op: 'not', a: noImp(n.a) }, b: noImp(n.b) };
      return n.a ? Object.assign({}, n, { a: noImp(n.a), b: n.b && noImp(n.b) }) : n;
    }
    function inNot(n) {
      if (n.op === 'not') {
        const a = n.a;
        if (a.op === 'not') return inNot(a.a);
        if (a.op === 'and') return { op: 'or', a: inNot({ op: 'not', a: a.a }), b: inNot({ op: 'not', a: a.b }) };
        if (a.op === 'or') return { op: 'and', a: inNot({ op: 'not', a: a.a }), b: inNot({ op: 'not', a: a.b }) };
        if (a.op === 'T') return { op: 'F' };
        if (a.op === 'F') return { op: 'T' };
        return n;
      }
      return n.a ? Object.assign({}, n, { a: inNot(n.a), b: n.b && inNot(n.b) }) : n;
    }
    /* clauses as sorted arrays of literal strings such as "P" and "¬P" */
    const neg = l => l[0] === '¬' ? l.slice(1) : '¬' + l;
    function clauses(n) {
      if (n.op === 'and') return clauses(n.a).concat(clauses(n.b));
      if (n.op === 'or') { const A = clauses(n.a), B = clauses(n.b), out = []; A.forEach(x => B.forEach(y => out.push(x.concat(y)))); return out; }
      if (n.op === 'T') return [];
      if (n.op === 'F') return [[]];
      if (n.op === 'not') return [[neg(str(n.a))]];
      return [[str(n)]];
    }
    const tidy = cs => {
      const seen = new Set(), out = [];
      cs.forEach(c => {
        const u = [...new Set(c)].sort((x, y) => x.replace('¬', '').localeCompare(y.replace('¬', '')) || x.length - y.length);
        if (u.some(l => u.includes(neg(l)))) return;
        const k = u.join(' ∨ ');
        if (!seen.has(k)) { seen.add(k); out.push(u); }
      });
      return out;
    };
    function cnf(n) {
      const s1 = noIff(n), s2 = noImp(s1), s3 = inNot(s2), cs = tidy(clauses(s3));
      return { s1, s2, s3, cs };
    }
    const cstr = c => c.length ? c.join(' ∨ ') : '{ } (the empty clause)';
    /* first order terms: unification with the occurs check */
    const isVar = x => x.t === 'var';
    function walk(x, th) { while (isVar(x) && th[x.name]) x = th[x.name]; return x; }
    function subst(x, th) {
      if (x.op === 'atom') return Object.assign({}, x, { args: x.args.map(a => subst(a, th)) });
      if (x.op) return Object.assign({}, x, { a: x.a && subst(x.a, th), b: x.b && subst(x.b, th) });
      if (isVar(x)) { const w = th[x.name]; return w ? subst(w, th) : x; }
      if (x.t === 'fn') return { t: 'fn', name: x.name, args: x.args.map(a => subst(a, th)) };
      return x;
    }
    function occurs(v, x, th) {
      x = walk(x, th);
      if (isVar(x)) return x.name === v;
      if (x.t === 'fn') return x.args.some(a => occurs(v, a, th));
      return false;
    }
    /* unify two atoms or terms; log(kind, text) is told about every step */
    function unify(x, y, th, log = () => {}) {
      if (th === null) return null;
      if (x.op === 'atom' || y.op === 'atom') {
        if (x.op !== 'atom' || y.op !== 'atom' || x.pred !== y.pred || x.args.length !== y.args.length) { log('fail', `The predicates differ (${x.pred || tstr(x)} and ${y.pred || tstr(y)}), or they have a different number of arguments. Unification fails.`, x, y); return null; }
        log('pair', `Both are ${x.pred} with ${x.args.length} argument${x.args.length > 1 ? 's' : ''}. Unify the arguments one pair at a time, left to right.`, x, y);
        for (let k = 0; k < x.args.length; k++) { th = unify(x.args[k], y.args[k], th, log); if (!th) return null; }
        return th;
      }
      const a = walk(x, th), b = walk(y, th);
      if (a !== x || b !== y) log('look', `${tstr(x)}${a !== x ? ' is already bound to ' + tstr(subst(a, th)) : ''}${b !== y ? (a !== x ? ', and ' : ' and ') + tstr(y) + ' is already bound to ' + tstr(subst(b, th)) : ''}. Use the bound value${a !== x && b !== y ? 's' : ''} instead.`, a, b);
      if (isVar(a) && isVar(b) && a.name === b.name) { log('same', `${a.name} and ${b.name} are the same variable. Nothing to do.`, a, b); return th; }
      if (!isVar(a) && !isVar(b) && a.t === 'const' && b.t === 'const') {
        if (a.name === b.name) { log('same', `${a.name} and ${b.name} are the same constant. They match.`, a, b); return th; }
        log('fail', `${a.name} and ${b.name} are different constants. Two different names cannot be made equal, so unification fails.`, a, b); return null;
      }
      if (isVar(a) || isVar(b)) {
        const v = isVar(a) ? a : b, o = isVar(a) ? b : a;
        if (occurs(v.name, o, th)) { log('fail', `Occurs check: ${v.name} appears inside ${tstr(subst(o, th))}. Binding ${v.name} to a term that contains ${v.name} would make an endless term, so unification fails.`, a, b); return null; }
        const nt = Object.assign({}, th, { [v.name]: o });
        log('bind', `${v.name} is a variable, so bind it: <b>${v.name} / ${tstr(subst(o, th))}</b>.`, a, b, nt);
        return nt;
      }
      if (a.t === 'fn' && b.t === 'fn') {
        if (a.name !== b.name || a.args.length !== b.args.length) { log('fail', `${tstr(a)} and ${tstr(b)} use different functions (or a different number of arguments). Unification fails.`, a, b); return null; }
        log('pair', `Both are the function ${a.name}. Unify their arguments.`, a, b);
        for (let k = 0; k < a.args.length; k++) { th = unify(a.args[k], b.args[k], th, log); if (!th) return null; }
        return th;
      }
      log('fail', `${tstr(a)} is a constant and ${tstr(b)} is a function term${a.t === 'fn' ? ' (or the other way round)' : ''}. They cannot match, so unification fails.`, a, b);
      return null;
    }
    const thStr = th => { const k = Object.keys(th); return k.length ? '{' + k.map(v => `${v}/${tstr(subst(th[v], th))}`).join(', ') + '}' : '{ }'; };
    /* rename every variable of a sentence with a suffix, to keep rules apart */
    function rename(x, sfx) {
      if (x.op) return Object.assign({}, x, x.op === 'atom' ? { args: x.args.map(a => rename(a, sfx)) } : { a: x.a && rename(x.a, sfx), b: x.b && rename(x.b, sfx) });
      if (isVar(x)) return { t: 'var', name: x.name + sfx };
      if (x.t === 'fn') return { t: 'fn', name: x.name, args: x.args.map(a => rename(a, sfx)) };
      return x;
    }
    /* a definite clause "p1 ∧ p2 ⇒ q" or a fact "q" */
    function definite(n) {
      const prem = [];
      const flat = m => { if (m.op === 'and') { flat(m.a); flat(m.b); } else if (m.op === 'atom') prem.push(m); else throw new Error(`Only atoms joined by ∧ may stand before ⇒, found ${str(m)}.`); };
      if (n.op === 'imp') { flat(n.a); if (n.b.op !== 'atom') throw new Error(`After ⇒ there must be one atom, found ${str(n.b)}.`); return { prem, head: n.b }; }
      if (n.op === 'atom') return { prem: [], head: n };
      throw new Error(`"${str(n)}" is not a definite clause. Write a fact, or atoms joined by ∧ followed by ⇒ and one atom.`);
    }
    const lines = s => String(s).split(/\n|;/).map(x => x.trim()).filter(Boolean);
    return { parse, str, tstr, syms, val, cnf, cstr, neg, unify, subst, thStr, rename, definite, lines, tidy };
  })();

  /* a simple wrapped list of text rows, used by several logic animations. rows: [{t, col, b, d}] */
  function rowsPaint(z, rows, x0, y0, rh, maxRows, w) {
    const { g } = z, c = z.col;
    let off = 0;
    if (rows.length > maxRows) { off = rows.length - maxRows; D.text(g, `(${off} earlier rows above. Open "Earlier steps" to read them.)`, x0, y0 - 4, { s: 10.5, c: c.ink2 }); rows = rows.slice(off); y0 += 12; }
    rows.forEach((r, i) => {
      const y = y0 + i * rh + rh / 2, x = x0 + (r.d || 0) * 18;
      if (r.box) rr(g, x - 4, y - rh / 2 + 1.5, (w || z.W - 30) - x + x0, rh - 3, 5, { fill: r.box, stroke: r.edge || r.box, w: 1.2 });
      const s = fit(g, r.t, (w || z.W - 30) - (x - x0) - 8, r.s || 12, { b: r.b, mono: r.mono });
      D.text(g, r.t, x, y + 4, { s, b: r.b, mono: r.mono, c: r.col || c.ink });
    });
  }

  /* =====================================================================================================
     7.1  Model checking with a truth table: does KB entail α?
     ===================================================================================================== */
  trace('truthtable', {
    title: 'Model checking: is α true in every model where the KB is true?',
    sub: 'Each row is one model, a choice of true (T) or false (F) for every symbol. Green rows make the whole KB true. KB ⊨ α when α is true in all green rows.',
    W: 640, H: 420, speed: 900,
    params: [
      { k: 'kb', label: 'Knowledge base, one sentence per line (use ¬ ∧ ∨ ⇒ ⇔, or ~ & | => <=>)', type: 'area', v: 'P ∨ Q\nP ⇒ R\nQ ⇒ R' },
      { k: 'q', label: 'Query α', type: 'text', v: 'R' }
    ],
    tips: [
      { t: 'Proof by cases: from P ∨ Q, P ⇒ R and Q ⇒ R, R follows. Only 3 of the 8 models make the KB true, and R is true in all of them.', set: { kb: 'P ∨ Q\nP ⇒ R\nQ ⇒ R', q: 'R' }, play: true },
      { t: 'The wumpus world in small: no breeze in [1,1], and a breeze in [1,1] means a pit in [1,2] or [2,1]. The KB entails ¬P12: no pit in [1,2].', set: { kb: 'B11 ⇔ (P12 ∨ P21)\n¬B11', q: '¬P12' }, play: true },
      { t: 'A query that does not follow. From P ⇒ Q and Q, we cannot conclude P. The row P = F, Q = T makes the KB true and P false. This mistake is called affirming the consequent.', set: { kb: 'P ⇒ Q\nQ', q: 'P' }, play: true },
      { t: 'An unsatisfiable KB: P and ¬P. No row is green, so the KB entails everything, even False. A KB with a contradiction is useless.', set: { kb: 'P\n¬P', q: 'Q' }, play: true }
    ],
    frames(p, z) {
      const S = LG.lines(p.kb).map(LG.parse), A = LG.parse(p.q);
      const sy = [];
      S.concat([A]).forEach(n => LG.syms(n).forEach(x => { if (!sy.includes(x)) sy.push(x); }));
      if (sy.some(x => x.includes('('))) throw new Error('Please use plain symbols such as P, Q or B11 here, not first order atoms.');
      if (sy.length > 5) throw new Error(`This table allows at most 5 symbols so that it fits, and your sentences use ${sy.length}: ${sy.join(', ')}.`);
      z.state.TT = { S: S.map(n => LG.str(n)), A: LG.str(A), sy };
      const rows = [], fr = [];
      fr.push({ rows: [], say: `The sentences use ${sy.length} symbol${sy.length > 1 ? 's' : ''}: ${sy.join(', ')}. So there are 2<sup>${sy.length}</sup> = ${1 << sy.length} models to check, one per row. Each new step adds one row.` });
      let good = 0, bad = null;
      for (let r = 0; r < (1 << sy.length); r++) {
        const m = {};
        sy.forEach((x, k) => { m[x] = !((r >> (sy.length - 1 - k)) & 1); });
        const sv = S.map(n => LG.val(n, m)), kb = sv.every(Boolean), av = LG.val(A, m);
        rows.push({ m, sv, kb, av });
        const mStr = sy.map(x => `${x} = ${m[x] ? 'T' : 'F'}`).join(', ');
        let say;
        if (!kb) { const k = sv.indexOf(false); say = `Row ${r + 1}: ${mStr}. Sentence S${k + 1} (${esc(LG.str(S[k]))}) is false here, so the KB is false. This model does not matter for entailment.`; }
        else if (av) { good++; say = `Row ${r + 1}: ${mStr}. Every KB sentence is true, so this is a model of the KB. α = ${esc(LG.str(A))} is <b>true</b> here too. Good.`; }
        else { good++; bad = bad || r + 1; say = `Row ${r + 1}: ${mStr}. Every KB sentence is true, but α = ${esc(LG.str(A))} is <b>false</b>. This one row is enough to show that the KB does not entail α.`; }
        fr.push({ rows: rows.slice(), cur: r, say });
      }
      const kbN = rows.filter(x => x.kb).length;
      fr.push({ rows: rows.slice(), done: true, say: kbN === 0 ? `No row makes the KB true. The KB is unsatisfiable, so by the definition it entails every sentence, including α.` : bad ? `Done. The KB is true in ${kbN} row${kbN > 1 ? 's' : ''}, but α is false in row ${bad}. So <b>KB does not entail α</b>.` : `Done. The KB is true in ${kbN} of ${rows.length} rows, and α is true in all of them. So <b>KB ⊨ α</b>: α follows from the KB.` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col, T = z.state.TT;
      let y = 16;
      T.S.forEach((s, k) => { D.text(g, `S${k + 1}: ${s}`, 16, y, { s: fit(g, `S${k + 1}: ${s}`, z.W - 32, 12, { mono: true }), mono: true, c: c.ink }); y += 16; });
      D.text(g, `α: ${T.A}`, 16, y, { s: 12, mono: true, b: true, c: c.cv }); y += 14;
      const cols = T.sy.concat(T.S.map((s, k) => 'S' + (k + 1)), ['KB', 'α']);
      const cw = Math.min(64, (z.W - 40) / cols.length), x0 = 20;
      const maxR = Math.max(4, Math.floor((z.H - y - 40) / 17));
      let rows = f.rows, off = 0;
      if (rows.length > maxR) { off = rows.length - maxR; rows = rows.slice(off); }
      y += 8;
      cols.forEach((h, k) => D.text(g, h, x0 + k * cw + cw / 2, y + 10, { a: 'center', s: fit(g, h, cw - 4, 12, { b: true }), b: true, c: k >= T.sy.length + T.S.length ? c.cv : c.ink2 }));
      D.line(g, x0, y + 16, x0 + cols.length * cw, y + 16, c.line, 1);
      if (off) D.text(g, `(${off} earlier rows)`, x0 + cols.length * cw + 6, y + 10, { s: 10, c: c.ink2 });
      y += 20;
      rows.forEach((r, i) => {
        const yy = y + i * 17, cur = (i + off) === f.cur;
        if (r.kb) rr(g, x0 - 4, yy - 1, cols.length * cw + 8, 16, 4, { fill: r.av ? 'rgba(34,197,94,.18)' : 'rgba(239,68,68,.20)', stroke: r.av ? c.green : c.red, w: 1 });
        if (cur) rr(g, x0 - 6, yy - 2, cols.length * cw + 12, 18, 4, { stroke: c.cv, w: 2 });
        const vals = T.sy.map(x => r.m[x]).concat(r.sv, [r.kb, r.av]);
        vals.forEach((v, k) => D.text(g, v ? 'T' : 'F', x0 + k * cw + cw / 2, yy + 11, { a: 'center', s: 11.5, mono: true, b: k >= T.sy.length, c: v ? c.ink : c.ink2 }));
      });
      if (f.done) D.text(g, 'Green: KB and α true. Red: KB true but α false.', 16, z.H - 10, { s: 11, c: c.ink2 });
    }
  });

  /* =====================================================================================================
     7.2  Resolution: convert to clauses, add ¬α, resolve until the empty clause appears
     ===================================================================================================== */
  trace('resolution', {
    title: 'Proof by resolution: add ¬α and look for a contradiction',
    sub: 'Every sentence is turned into clauses (ORs of literals). Two clauses with a literal and its opposite are resolved: the pair cancels and the rest is joined. Getting the empty clause { } proves KB ⊨ α.',
    W: 640, H: 430, speed: 1100,
    params: [
      { k: 'kb', label: 'Knowledge base, one sentence per line', type: 'area', v: 'B11 ⇔ (P12 ∨ P21)\n¬B11' },
      { k: 'q', label: 'Query α', type: 'text', v: '¬P12' }
    ],
    tips: [
      { t: 'The textbook example: no breeze in [1,1] means no pit in [1,2]. The ⇔ sentence gives three clauses. With ¬α = P12, two resolution steps reach the empty clause.', set: { kb: 'B11 ⇔ (P12 ∨ P21)\n¬B11', q: '¬P12' }, play: true },
      { t: 'Proof by cases again: P ∨ Q, P ⇒ R, Q ⇒ R. Resolution needs four steps to reach { }.', set: { kb: 'P ∨ Q\nP ⇒ R\nQ ⇒ R', q: 'R' }, play: true },
      { t: 'A query that does not follow: from P ⇒ Q and Q, try to prove P. Resolution runs out of new clauses without finding { }, so P does not follow.', set: { kb: 'P ⇒ Q\nQ', q: 'P' }, play: true }
    ],
    frames(p, z) {
      const S = LG.lines(p.kb).map(LG.parse), A = LG.parse(p.q);
      const fr = [], cl = [];
      const snap = (say, cur, ex = {}) => fr.push(Object.assign({ cl: cl.map(x => ({ ...x })), cur, say }, ex));
      const key = c => c.join(' ∨ ');
      const add = (c, from, sos) => { cl.push({ c, from, sos, k: key(c) }); return cl.length - 1; };
      S.forEach((n, k) => {
        const r = LG.cnf(n);
        const first = cl.length;
        r.cs.forEach(c => { if (!cl.some(x => x.k === key(c))) add(c, `S${k + 1}`, false); });
        const made = cl.slice(first).map(x => LG.cstr(x.c));
        snap(`Sentence S${k + 1}: ${esc(LG.str(n))}. ${n.op === 'iff' ? `Replace ⇔ by two ⇒: ${esc(LG.str(r.s1))}. ` : ''}${LG.str(r.s2) !== LG.str(r.s1) ? `Replace each A ⇒ B by ¬A ∨ B: ${esc(LG.str(r.s2))}. ` : ''}${LG.str(r.s3) !== LG.str(r.s2) ? `Move ¬ inwards: ${esc(LG.str(r.s3))}. ` : ''}${made.length ? `Clauses added: ${made.map(esc).join(' and ')}.` : 'No new clause.'}`, cl.length - 1);
      });
      const nA = LG.cnf({ op: 'not', a: A });
      const g0 = cl.length;
      nA.cs.forEach(c => { if (!cl.some(x => x.k === key(c))) add(c, '¬α', true); else cl.find(x => x.k === key(c)).sos = true; });
      snap(`Now assume the opposite of what we want to prove: ¬α = ¬(${esc(LG.str(A))}), which gives ${nA.cs.map(c => esc(LG.cstr(c))).join(' and ')}. If the KB together with ¬α leads to a contradiction, α must follow from the KB.`, cl.length - 1);
      if (cl.some(x => !x.c.length)) { snap('The empty clause is already here, so the proof is done.', null, { done: 'yes' }); return fr; }
      const tried = new Set();
      for (let step = 0; step < 40; step++) {
        let best = null;
        cl.forEach((a, i) => {
          if (!a.sos) return;
          cl.forEach((b, j) => {
            if (i === j || tried.has(i + ',' + j)) return;
            a.c.forEach(l => {
              if (!b.c.includes(LG.neg(l))) return;
              const r = LG.tidy([a.c.filter(x => x !== l).concat(b.c.filter(x => x !== LG.neg(l)))]);
              if (!r.length) return;           /* a tautology, useless */
              const c = r[0];
              if (cl.some(x => x.k === key(c))) return;
              const sc = c.length * 1000 + Math.max(i, j);
              if (!best || sc < best.sc) best = { i, j, l, c, sc };
            });
          });
        });
        if (!best) { snap(`No pair of clauses gives a new clause any more. We found no contradiction, so <b>α does not follow</b> from the KB (as long as the KB itself has no contradiction).`, null, { done: 'no' }); return fr; }
        tried.add(best.i + ',' + best.j);
        const n = add(best.c, `${best.i + 1}, ${best.j + 1}`, true);
        const L = best.l.replace('¬', '');
        if (!best.c.length) { snap(`Resolve clause ${best.i + 1} (${esc(LG.cstr(cl[best.i].c))}) with clause ${best.j + 1} (${esc(LG.cstr(cl[best.j].c))}): ${L} and ¬${L} cancel and nothing is left. This is the <b>empty clause</b>, a contradiction. So the KB with ¬α cannot be true, and <b>KB ⊨ α</b>.`, n, { done: 'yes' }); return fr; }
        snap(`Resolve clause ${best.i + 1} (${esc(LG.cstr(cl[best.i].c))}) with clause ${best.j + 1} (${esc(LG.cstr(cl[best.j].c))}) on ${L}: ${L} and ¬${L} cancel, and what is left is joined: <b>${esc(LG.cstr(best.c))}</b>. We pick pairs that use ¬α or a clause made from it, and we prefer short results.`, n);
      }
      snap('Stopped after 40 new clauses. Try a smaller knowledge base.', null);
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      const rows = f.cl.map((x, i) => ({ t: `${String(i + 1).padStart(2, ' ')}.  ${LG.cstr(x.c)}`, from: x.from, i, sos: x.sos }));
      const maxR = 17, RH = 22;
      let off = Math.max(0, rows.length - maxR);
      D.text(g, 'clause', 50, 16, { s: 11, b: true, c: c.ink2 });
      D.text(g, 'comes from', z.W - 130, 16, { s: 11, b: true, c: c.ink2 });
      if (off) D.text(g, `(${off} earlier clauses above)`, 160, 16, { s: 10.5, c: c.ink2 });
      rows.slice(off).forEach((r, k) => {
        const y = 30 + k * RH, cur = r.i === f.cur, empty = !f.cl[r.i].c.length;
        rr(g, 14, y, z.W - 28, RH - 4, 5, { fill: empty ? 'rgba(34,197,94,.22)' : cur ? 'rgba(14,116,144,.14)' : r.sos ? c.surf : c.bg, stroke: cur ? c.cv : empty ? c.green : c.line, w: cur ? 2 : 1 });
        D.text(g, r.t, 24, y + 13, { s: fit(g, r.t, z.W - 200, 12.5, { mono: true, b: cur }), mono: true, b: cur, c: r.from === '¬α' ? c.purple : c.ink });
        D.text(g, r.from.includes(',') ? 'resolve ' + r.from : r.from === '¬α' ? 'negated query' : 'from ' + r.from, z.W - 130, y + 13, { s: 11, c: r.from.includes(',') ? c.cv : c.ink2, b: r.from.includes(',') });
      });
      if (f.done) tag(g, f.done === 'yes' ? 'KB ⊨ α proved' : 'α does not follow', z.W / 2, z.H - 14, { s: 12.5, fill: f.done === 'yes' ? c.green : c.red, stroke: f.done === 'yes' ? c.green : c.red, c: '#fff' });
    }
  });

  /* =====================================================================================================
     7.3  Forward and backward chaining with Horn clauses
     ===================================================================================================== */
  trace('chaining', {
    title: 'Forward and backward chaining with definite clauses',
    sub: 'Forward chaining starts from the facts and fires every rule whose premises are all known. Backward chaining starts from the query and works back to the facts.',
    W: 640, H: 420, speed: 1000,
    params: [
      { k: 'kb', label: 'Definite clauses, one per line (facts like A, rules like A ∧ B ⇒ L)', type: 'area', v: 'P ⇒ Q\nL ∧ M ⇒ P\nB ∧ L ⇒ M\nA ∧ P ⇒ L\nA ∧ B ⇒ L\nA\nB' },
      { k: 'q', label: 'Query (one symbol)', type: 'text', v: 'Q' },
      { k: 'mode', label: 'Method', type: 'select', v: 'fc', opts: [['fc', 'Forward chaining (data driven)'], ['bc', 'Backward chaining (goal driven)']] }
    ],
    tips: [
      { t: 'The textbook example with forward chaining. The count next to each rule is how many of its premises are still unknown. A rule fires when its count reaches 0.', set: { mode: 'fc', q: 'Q' }, play: true },
      { t: 'The same knowledge base with backward chaining. It starts at Q and only looks at rules that could help prove Q. Note the loop check: L needs P, and P needs L.', set: { mode: 'bc', q: 'Q' }, play: true },
      { t: 'Add an unrelated fact and rule, such as C and C ⇒ D. Forward chaining also derives D, which does not help with Q. Backward chaining never looks at it.', set: { kb: 'P ⇒ Q\nL ∧ M ⇒ P\nB ∧ L ⇒ M\nA ∧ P ⇒ L\nA ∧ B ⇒ L\nA\nB\nC\nC ⇒ D', mode: 'fc', q: 'Q' }, play: true }
    ],
    frames(p, z) {
      const R = LG.lines(p.kb).map(s => LG.definite(LG.parse(s))).map(r => ({ prem: r.prem.map(a => LG.str(a)), head: LG.str(r.head) }));
      const q = LG.str(LG.parse(p.q));
      z.state.R = R;
      const fr = [];
      if (p.mode === 'fc') {
        const count = R.map(r => r.prem.length), inferred = {}, agenda = R.filter(r => !r.prem.length).map(r => r.head), fired = R.map(() => false);
        const snap = (say, cur, ex = {}) => fr.push(Object.assign({ count: count.slice(), inferred: { ...inferred }, agenda: agenda.slice(), fired: fired.slice(), cur, say }, ex));
        snap(`Start. Each rule gets a count: the number of its premises not yet known. The facts ${agenda.join(', ')} go on the agenda, the list of symbols known to be true but not yet used.`, null);
        let n = 0;
        while (agenda.length && n++ < 60) {
          const s = agenda.shift();
          if (s === q) { inferred[s] = true; snap(`Take ${s} from the agenda. It is the query, so <b>${q} is proved</b>. Forward chaining stops.`, null, { got: s, done: 'yes' }); return fr; }
          if (inferred[s]) { snap(`Take ${s} from the agenda. It is already known, so skip it.`, null, { got: s }); continue; }
          inferred[s] = true;
          const dec = [], fire = [];
          R.forEach((r, i) => { if (r.prem.includes(s)) { count[i] -= r.prem.filter(x => x === s).length; dec.push(i); if (count[i] === 0 && !fired[i]) { fired[i] = true; agenda.push(r.head); fire.push(i); } } });
          snap(`Take <b>${s}</b> from the agenda and mark it as known. ${dec.length ? (dec.length > 1 ? `It appears in the premises of rules ${dec.slice(0, -1).map(i => i + 1).join(', ')} and ${dec[dec.length - 1] + 1}, so their counts drop by 1.` : `It appears in the premises of rule ${dec[0] + 1}, so its count drops by 1.`) : 'It appears in no premise.'} ${fire.length ? fire.map(i => `Rule ${i + 1} now has count 0, so it fires and adds ${R[i].head} to the agenda.`).join(' ') : ''}`, dec, { got: s, fire });
        }
        snap(`The agenda is empty and ${q} was never reached. So ${q} <b>does not follow</b> from these clauses.`, null, { done: 'no' });
        return fr;
      }
      /* backward chaining: rows of an outline */
      const rows = [];
      const snap = (say, cur, ex = {}) => fr.push(Object.assign({ rows: rows.map(r => ({ ...r })), cur, say }, ex));
      const known = {};
      let guard = 0;
      function prove(g, path, d) {
        const row = { d, t: g, st: 'open', txt: '' }; rows.push(row); const me = rows.length - 1;
        if (guard++ > 80) { row.st = 'fail'; row.txt = 'stopped, too long'; return false; }
        if (known[g]) { row.st = 'ok'; row.txt = 'already proved'; snap(`Goal ${g}: it was proved earlier, so it is true.`, me); return true; }
        if (path.includes(g)) { row.st = 'fail'; row.txt = 'loop: already a goal on this path'; snap(`Goal ${g}: we are already trying to prove ${g} higher up (${path.join(' needs ')} needs ${g}). Going on would loop for ever, so this way fails.`, me); return false; }
        const fact = R.find(r => r.head === g && !r.prem.length);
        if (fact) { row.st = 'ok'; row.txt = 'a fact in the KB'; known[g] = true; snap(`Goal ${g}: it is a fact in the knowledge base. Proved.`, me); return true; }
        const rs = R.map((r, i) => ({ r, i })).filter(x => x.r.head === g);
        if (!rs.length) { row.st = 'fail'; row.txt = 'no fact or rule gives it'; snap(`Goal ${g}: no fact says ${g} and no rule concludes ${g}. It cannot be proved.`, me); return false; }
        snap(`Goal ${g}: it is not a fact. Rule${rs.length > 1 ? 's' : ''} ${rs.map(x => x.i + 1).join(' and ')} conclude${rs.length > 1 ? '' : 's'} ${g}. Try ${rs.length > 1 ? 'them in order' : 'it'}: prove every premise.`, me);
        for (const { r, i } of rs) {
          row.txt = `try rule ${i + 1}: ${r.prem.join(' ∧ ')} ⇒ ${g}`;
          let ok = true;
          for (const s of r.prem) { if (!prove(s, path.concat([g]), d + 1)) { ok = false; break; } }
          if (ok) { row.st = 'ok'; row.txt = `proved by rule ${i + 1}`; known[g] = true; snap(`Every premise of rule ${i + 1} (${r.prem.join(', ')}) is proved, so <b>${g} is proved</b>.`, me); return true; }
          snap(`Rule ${i + 1} fails for ${g} because one of its premises cannot be proved.${rs.length > 1 ? ' Try the next rule.' : ''}`, me);
        }
        row.st = 'fail'; row.txt = 'every rule failed';
        snap(`No rule proves ${g}.`, me);
        return false;
      }
      const ok = prove(q, [], 0);
      snap(ok ? `Done: <b>${q} is proved</b> by backward chaining. It only looked at the rules that could help with ${q}.` : `Done: ${q} <b>cannot be proved</b>.`, null, { done: ok ? 'yes' : 'no' });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col, R = z.state.R;
      if (z.p.mode === 'fc') {
        D.text(g, 'Rules and facts', 18, 18, { s: 12, b: true, c: c.ink2 });
        D.text(g, 'count', 300, 18, { s: 12, b: true, c: c.ink2 });
        const RH = Math.min(26, (z.H - 60) / R.length);
        R.forEach((r, i) => {
          const y = 30 + i * RH, hot = Array.isArray(f.cur) && f.cur.includes(i), fire = f.fire && f.fire.includes(i);
          rr(g, 14, y, 320, RH - 4, 5, { fill: f.fired[i] || !r.prem.length ? 'rgba(34,197,94,.16)' : c.surf, stroke: fire ? c.green : hot ? c.cv : c.line, w: fire || hot ? 2.2 : 1 });
          const t = `${i + 1}. ${r.prem.length ? r.prem.join(' ∧ ') + ' ⇒ ' : ''}${r.head}`;
          D.text(g, t, 22, y + RH / 2 + 2, { s: fit(g, t, 250, 12.5, { mono: true }), mono: true, c: c.ink });
          if (r.prem.length) tag(g, String(f.count[i]), 312, y + RH / 2 - 2, { s: 11, fill: f.count[i] ? c.orange : c.green, stroke: f.count[i] ? c.orange : c.green, c: '#fff', mono: true });
        });
        D.text(g, 'Agenda (to use next)', 360, 18, { s: 12, b: true, c: c.ink2 });
        let x = 364;
        f.agenda.forEach(s => { x += tag(g, s, x + tw(g, s, { s: 12, b: true }) / 2 + 6, 40, { s: 12, fill: c.surf, stroke: c.orange, c: c.ink }) + 6; });
        D.text(g, 'Known (inferred)', 360, 82, { s: 12, b: true, c: c.ink2 });
        x = 364;
        Object.keys(f.inferred).forEach(s => { x += tag(g, s, x + tw(g, s, { s: 12, b: true }) / 2 + 6, 104, { s: 12, fill: s === f.got ? c.cv : c.green, stroke: s === f.got ? c.cv : c.green, c: '#fff' }) + 6; });
        if (f.done) tag(g, f.done === 'yes' ? 'query proved' : 'query not proved', 490, 160, { s: 13, fill: f.done === 'yes' ? c.green : c.red, stroke: f.done === 'yes' ? c.green : c.red, c: '#fff' });
        return;
      }
      const rows = f.rows.map((r, i) => ({ d: r.d, t: `${r.t}   ${r.txt}`, b: i === f.cur, col: r.st === 'ok' ? c.green : r.st === 'fail' ? c.red : i === f.cur ? c.cv : c.ink, mono: false, box: i === f.cur ? 'rgba(14,116,144,.12)' : null, edge: c.cv }));
      rowsPaint(z, rows, 18, 18, 22, 17);
      if (f.done) tag(g, f.done === 'yes' ? 'query proved' : 'query not proved', z.W / 2, z.H - 14, { s: 13, fill: f.done === 'yes' ? c.green : c.red, stroke: f.done === 'yes' ? c.green : c.red, c: '#fff' });
    }
  });

  /* =====================================================================================================
     7.3  First order models: is a quantified sentence true in this world?
     ===================================================================================================== */
  trace('folmodel', {
    title: 'Is a first order sentence true in this model?',
    sub: 'The model lists the objects and which relations hold between them. ∀x checks every object for x. ∃x looks for one object that works.',
    W: 640, H: 400, speed: 900,
    params: [
      { k: 'facts', label: 'The model: true atoms, one per line (every name used becomes an object)', type: 'area', v: 'Person(Richard)\nPerson(John)\nKing(John)\nBrother(Richard, John)\nBrother(John, Richard)\nCrown(TheCrown)\nOnHead(TheCrown, John)' },
      { k: 's', label: 'Sentence (∀x or forall x, ∃x or exists x)', type: 'text', v: '∀x King(x) ⇒ Person(x)' }
    ],
    tips: [
      { t: '"All kings are persons." ∀ goes with ⇒. For Richard and TheCrown the premise King(x) is false, so the implication is true. For John both sides are true.', set: { s: '∀x King(x) ⇒ Person(x)' }, play: true },
      { t: 'A common mistake: ∀x King(x) ∧ Person(x) says that everything is a king and a person. It is false already for Richard.', set: { s: '∀x King(x) ∧ Person(x)' }, play: true },
      { t: '∃ goes with ∧: "there is a crown on John\'s head". TheCrown works.', set: { s: '∃x Crown(x) ∧ OnHead(x, John)' }, play: true },
      { t: 'The other common mistake: ∃x Crown(x) ⇒ OnHead(x, John) is true as soon as one object is not a crown, here Richard. It says almost nothing.', set: { s: '∃x Crown(x) ⇒ OnHead(x, John)' }, play: true },
      { t: 'Nested quantifiers: "everyone who is a person has a brother". For each x we search for a y.', set: { s: '∀x Person(x) ⇒ ∃y Brother(x, y)' }, play: true }
    ],
    frames(p, z) {
      const F = LG.lines(p.facts).map(LG.parse);
      const objs = [], facts = new Set();
      F.forEach(a => { if (a.op !== 'atom') throw new Error('The model may only list true atoms such as King(John).'); a.args.forEach(t => { if (t.t !== 'const') throw new Error(`In the model, use names that start with a capital letter, not ${LG.tstr(t)}.`); if (!objs.includes(t.name)) objs.push(t.name); }); facts.add(LG.str(a)); });
      const S = LG.parse(p.s);
      z.state.M = { objs, facts: [...facts], s: LG.str(S) };
      const fr = [];
      fr.push({ env: {}, say: `The model has ${objs.length} objects: ${objs.join(', ')}. Every atom listed is true, and every other atom is false. Now check: ${esc(LG.str(S))}.` });
      let n = 0;
      function ev(x, env, d) {
        if (n++ > 400) throw new Error('This sentence needs too many checks for the animation.');
        switch (x.op) {
          case 'atom': { const g1 = LG.subst(x, Object.fromEntries(Object.entries(env).map(([k, v]) => [k, { t: 'const', name: v }]))); const free = t => t.t === 'var' || (t.args || []).some(free); if (g1.args.some(free)) throw new Error(`A variable in ${LG.str(x)} has no quantifier.`); return facts.has(LG.str(g1)); }
          case 'T': return true;
          case 'F': return false;
          case 'not': return !ev(x.a, env, d);
          case 'and': return ev(x.a, env, d) && ev(x.b, env, d);
          case 'or': return ev(x.a, env, d) || ev(x.b, env, d);
          case 'imp': return !ev(x.a, env, d) || ev(x.b, env, d);
          case 'iff': return ev(x.a, env, d) === ev(x.b, env, d);
          case 'all': case 'ex': {
            const want = x.op === 'all';
            for (const o of objs) {
              const e2 = Object.assign({}, env, { [x.v]: o });
              const v = ev(x.a, e2, d + 1);
              const inst = LG.str(LG.subst(x.a, Object.fromEntries(Object.entries(e2).map(([k, w]) => [k, { t: 'const', name: w }]))));
              fr.push({ env: e2, inst, v, d, say: `${want ? '∀' : '∃'}${x.v}${d ? ` (inside, with ${Object.entries(env).map(([k, w]) => k + ' = ' + w).join(', ')})` : ''}: try ${x.v} = <b>${o}</b>. ${esc(inst)} is <b>${v ? 'true' : 'false'}</b>${want ? (v ? '. Fine, go on.' : `. One counterexample is enough: the ∀ sentence is false.`) : (v ? `. One example is enough: the ∃ sentence is true.` : '. Try the next object.')}` });
              if (want && !v) return false;
              if (!want && v) return true;
            }
            fr.push({ env, d, say: want ? `${x.v} has taken every object and the body was always true, so ∀${x.v} is <b>true</b>.` : `No object works for ${x.v}, so ∃${x.v} is <b>false</b>.` });
            return want;
          }
        }
      }
      const v = ev(S, {}, 0);
      fr.push({ env: {}, final: v, say: `So the sentence ${esc(LG.str(S))} is <b>${v ? 'true' : 'false'}</b> in this model.` });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col, M = z.state.M;
      D.text(g, M.s, z.W / 2, 22, { a: 'center', s: fit(g, M.s, z.W - 40, 15, { mono: true, b: true }), mono: true, b: true, c: c.ink });
      const n = M.objs.length, bw = Math.min(130, (z.W - 40) / n - 10);
      const used = Object.entries(f.env || {});
      M.objs.forEach((o, i) => {
        const x = 20 + i * (bw + 10), y = 46;
        const vars = used.filter(([k, v]) => v === o).map(([k]) => k);
        rr(g, x, y, bw, 46, 8, { fill: vars.length ? 'rgba(14,116,144,.16)' : c.surf, stroke: vars.length ? c.cv : c.line, w: vars.length ? 2.2 : 1 });
        D.text(g, o, x + bw / 2, y + 20, { a: 'center', s: fit(g, o, bw - 8, 13, { b: true }), b: true, c: c.ink });
        if (vars.length) D.text(g, vars.join(', ') + ' = here', x + bw / 2, y + 37, { a: 'center', s: 11, b: true, c: c.cv });
      });
      D.text(g, 'True atoms in the model', 20, 116, { s: 12, b: true, c: c.ink2 });
      let x = 20, y = 136;
      M.facts.forEach(a => { const w = tw(g, a, { s: 11.5, mono: true }) + 14; if (x + w > z.W - 20) { x = 20; y += 24; } tag(g, a, x + w / 2, y, { s: 11.5, mono: true, b: false, fill: c.bg, stroke: c.line, c: c.ink }); x += w + 6; });
      y += 34;
      if (f.inst) {
        D.text(g, 'Checking now', 20, y, { s: 12, b: true, c: c.ink2 });
        D.text(g, f.inst, 20, y + 24, { s: fit(g, f.inst, z.W - 140, 14, { mono: true }), mono: true, b: true, c: c.ink });
        tag(g, f.v ? 'true' : 'false', z.W - 60, y + 20, { s: 13, fill: f.v ? c.green : c.red, stroke: f.v ? c.green : c.red, c: '#fff' });
      }
      if (f.final !== undefined) tag(g, f.final ? 'the sentence is true in this model' : 'the sentence is false in this model', z.W / 2, z.H - 20, { s: 13, fill: f.final ? c.green : c.red, stroke: f.final ? c.green : c.red, c: '#fff' });
    }
  });

  /* =====================================================================================================
     7.4  Unification, step by step
     ===================================================================================================== */
  trace('unify', {
    title: 'Unification: find a substitution that makes two atoms the same',
    sub: 'Names in lower case are variables, names with a capital are constants or functions. θ collects the bindings, written variable / value.',
    W: 640, H: 330, speed: 1100,
    params: [
      { k: 'a', label: 'First atom', type: 'text', v: 'Knows(John, x)' },
      { k: 'b', label: 'Second atom', type: 'text', v: 'Knows(y, Mother(y))' }
    ],
    tips: [
      { t: 'The textbook examples. Knows(John, x) and Knows(y, Mother(y)): y / John, and then x / Mother(John).', set: { a: 'Knows(John, x)', b: 'Knows(y, Mother(y))' }, play: true },
      { t: 'Knows(John, x) and Knows(x, Elizabeth) fail, because x cannot be John and Elizabeth at once. Rename the second x to x17 (standardising apart) and it works.', set: { a: 'Knows(John, x)', b: 'Knows(x, Elizabeth)' }, play: true },
      { t: 'The same pair after standardising apart: Knows(John, x) and Knows(x17, Elizabeth).', set: { a: 'Knows(John, x)', b: 'Knows(x17, Elizabeth)' }, play: true },
      { t: 'The occurs check: x cannot be unified with F(x), since x would have to contain itself.', set: { a: 'P(x)', b: 'P(F(x))' }, play: true },
      { t: 'The most general unifier: Knows(John, x) and Knows(y, z) give {y/John, x/z}, not {y/John, x/John, z/John}, which is less general.', set: { a: 'Knows(John, x)', b: 'Knows(y, z)' }, play: true }
    ],
    frames(p, z) {
      const A = LG.parse(p.a), B = LG.parse(p.b);
      if (A.op !== 'atom' || B.op !== 'atom') throw new Error('Please give two atoms, such as Knows(John, x).');
      z.state.U = { a: LG.str(A), b: LG.str(B) };
      const fr = [];
      let th = {};
      fr.push({ th, say: `Unify ${esc(LG.str(A))} with ${esc(LG.str(B))}. We start with an empty substitution θ = { }.` });
      const log = (kind, text, x, y, nt) => { if (nt) th = nt; fr.push({ th, kind, x: x.op ? LG.str(x) : LG.tstr(x), y: y.op ? LG.str(y) : LG.tstr(y), say: text }); };
      const r = LG.unify(A, B, {}, log);
      if (r) fr.push({ th: r, done: 'yes', res: LG.str(LG.subst(A, r)), say: `Done. θ = <b>${esc(LG.thStr(r))}</b>. Both atoms become ${esc(LG.str(LG.subst(A, r)))}. This is the most general unifier: it binds only what it must.` });
      else fr.push({ th, done: 'no', say: 'Done. The two atoms <b>do not unify</b>: no substitution makes them the same.' });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col, U = z.state.U;
      D.text(g, U.a, z.W / 4, 30, { a: 'center', s: fit(g, U.a, z.W / 2 - 30, 16, { mono: true, b: true }), mono: true, b: true, c: c.ink });
      D.text(g, U.b, 3 * z.W / 4, 30, { a: 'center', s: fit(g, U.b, z.W / 2 - 30, 16, { mono: true, b: true }), mono: true, b: true, c: c.ink });
      D.text(g, 'and', z.W / 2, 30, { a: 'center', s: 12, c: c.ink2 });
      if (f.x) {
        const col = f.kind === 'fail' ? c.red : f.kind === 'bind' ? c.green : c.cv;
        D.text(g, 'comparing', z.W / 2, 74, { a: 'center', s: 12, b: true, c: c.ink2 });
        tag(g, f.x, z.W / 2 - 90, 100, { s: 13, mono: true, fill: c.surf, stroke: col, c: c.ink });
        D.text(g, f.kind === 'fail' ? '≠' : '=', z.W / 2, 104, { a: 'center', s: 16, b: true, c: col });
        tag(g, f.y, z.W / 2 + 90, 100, { s: 13, mono: true, fill: c.surf, stroke: col, c: c.ink });
      }
      D.text(g, 'θ (the substitution so far)', 20, 150, { s: 12, b: true, c: c.ink2 });
      let x = 24;
      const ks = Object.keys(f.th || {});
      if (!ks.length) D.text(g, '{ } empty', 24, 176, { s: 13, mono: true, c: c.ink2 });
      ks.forEach(v => { const s = `${v} / ${LG.tstr(LG.subst(f.th[v], f.th))}`; x += tag(g, s, x + tw(g, s, { s: 13, mono: true, b: true }) / 2 + 6, 176, { s: 13, mono: true, fill: 'rgba(34,197,94,.16)', stroke: c.green, c: c.ink }) + 8; });
      if (f.done === 'yes') { D.text(g, 'Both atoms become', 20, 226, { s: 12, b: true, c: c.ink2 }); D.text(g, f.res, 20, 252, { s: fit(g, f.res, z.W - 40, 15, { mono: true, b: true }), mono: true, b: true, c: c.green }); }
      if (f.done === 'no') tag(g, 'no unifier exists', z.W / 2, 240, { s: 13, fill: c.red, stroke: c.red, c: '#fff' });
    }
  });

  /* =====================================================================================================
     7.4  First order forward and backward chaining (the crime example of the textbook)
     ===================================================================================================== */
  trace('folchain', {
    title: 'First order chaining: is Colonel West a criminal?',
    sub: 'Rules have variables. Forward chaining matches rule premises against known facts by unification. Backward chaining unifies the goal with rule heads and proves the premises one by one, passing the bindings along.',
    W: 660, H: 440, speed: 1100,
    params: [
      { k: 'kb', label: 'Definite clauses, one per line', type: 'area', v: 'American(x) ∧ Weapon(y) ∧ Sells(x, y, z) ∧ Hostile(z) ⇒ Criminal(x)\nOwns(Nono, M1)\nMissile(M1)\nMissile(x) ∧ Owns(Nono, x) ⇒ Sells(West, x, Nono)\nMissile(x) ⇒ Weapon(x)\nEnemy(x, America) ⇒ Hostile(x)\nAmerican(West)\nEnemy(Nono, America)' },
      { k: 'q', label: 'Query', type: 'text', v: 'Criminal(West)' },
      { k: 'mode', label: 'Method', type: 'select', v: 'fc', opts: [['fc', 'Forward chaining'], ['bc', 'Backward chaining']] }
    ],
    tips: [
      { t: 'Forward chaining on the crime example. Round 1 adds Sells(West, M1, Nono), Weapon(M1) and Hostile(Nono). Round 2 adds Criminal(West).', set: { mode: 'fc', q: 'Criminal(West)' }, play: true },
      { t: 'Backward chaining on the same example. It starts at Criminal(West) and builds the proof tree depth first, left to right, as Prolog does.', set: { mode: 'bc', q: 'Criminal(West)' }, play: true },
      { t: 'A query with a variable: who is hostile? Backward chaining answers with a binding for x.', set: { mode: 'bc', q: 'Hostile(x)' }, play: true }
    ],
    frames(p, z) {
      const R = LG.lines(p.kb).map(s => LG.definite(LG.parse(s)));
      const Q = LG.parse(p.q);
      if (Q.op !== 'atom') throw new Error('The query must be one atom.');
      const fr = [];
      if (p.mode === 'fc') {
        const facts = R.filter(r => !r.prem.length).map(r => ({ a: r.head, round: 0 }));
        const has = a => facts.some(f => LG.str(f.a) === LG.str(a));
        const snap = (say, ex = {}) => fr.push(Object.assign({ facts: facts.map(f => ({ ...f })), say }, ex));
        snap(`Round 0: the facts of the knowledge base are known: ${facts.map(f => esc(LG.str(f.a))).join(', ')}. Now try every rule against them.`);
        for (let round = 1; round <= 6; round++) {
          const fresh = [];
          R.forEach((r, ri) => {
            if (!r.prem.length) return;
            const rr2 = { prem: r.prem.map(a => LG.rename(a, '')), head: r.head };
            const match = (k, th) => {
              if (k === rr2.prem.length) { const h = LG.subst(rr2.head, th); if (!has(h) && !fresh.some(x => LG.str(x.a) === LG.str(h))) fresh.push({ a: h, round, rule: ri, th }); return; }
              facts.forEach(f => { const t2 = LG.unify(rr2.prem[k], f.a, th); if (t2) match(k + 1, t2); });
            };
            match(0, {});
          });
          if (!fresh.length) { snap(`Round ${round}: no rule gives a new fact. This is a fixed point, and ${esc(LG.str(Q))} was not found, so it does not follow.`, { done: 'no' }); return fr; }
          for (const x of fresh) {
            facts.push(x);
            const r = R[x.rule];
            snap(`Round ${round}: rule ${x.rule + 1} (${esc(LG.str(r.prem.reduce((a, b) => ({ op: 'and', a, b }))))} ⇒ ${esc(LG.str(r.head))}). Its premises match known facts with θ = ${esc(LG.thStr(x.th))}, so add <b>${esc(LG.str(x.a))}</b>.`, { cur: LG.str(x.a) });
            const t = LG.unify(Q, x.a, {});
            if (t) { snap(`${esc(LG.str(x.a))} matches the query ${esc(LG.str(Q))}. <b>Proved</b> in ${round} round${round > 1 ? 's' : ''}.`, { cur: LG.str(x.a), done: 'yes' }); return fr; }
          }
        }
        snap('Stopped after 6 rounds.');
        return fr;
      }
      const rows = [];
      const snap = (say, cur, ex = {}) => fr.push(Object.assign({ rows: rows.map(r => ({ ...r })), cur, say }, ex));
      let uid = 0, guard = 0;
      function* bcOr(goal, th, d) {
        const g0 = LG.subst(goal, th);
        const row = { d, t: LG.str(g0), st: 'open', txt: '' }; rows.push(row); const me = rows.length - 1;
        if (guard++ > 60 || d > 8) { row.st = 'fail'; row.txt = 'too deep, stop'; snap(`Goal ${esc(row.t)}: the search is too deep, so stop here.`, me); return; }
        snap(`Goal <b>${esc(row.t)}</b>. Look for facts and rule heads that unify with it.`, me);
        let any = false;
        for (let ri = 0; ri < R.length; ri++) {
          const sfx = '_' + (++uid);
          const r = { prem: R[ri].prem.map(a => LG.rename(a, sfx)), head: LG.rename(R[ri].head, sfx) };
          const t2 = LG.unify(r.head, g0, th);
          if (!t2) continue;
          any = true;
          row.txt = r.prem.length ? `use rule ${ri + 1}` : `fact ${LG.str(R[ri].head)}`;
          if (!r.prem.length) { row.st = 'ok'; snap(`${esc(row.t)} unifies with the fact ${esc(LG.str(R[ri].head))}. Proved${Object.keys(t2).length > Object.keys(th).length ? `, with ${esc(LG.thStr(t2))}` : ''}.`, me); yield t2; row.st = 'open'; continue; }
          snap(`${esc(row.t)} unifies with the head of rule ${ri + 1}. The rule's variables are renamed apart (suffix ${sfx}). Now prove its ${r.prem.length} premise${r.prem.length > 1 ? 's' : ''}: ${r.prem.map(a => esc(LG.str(LG.subst(a, t2)))).join(', ')}.`, me);
          for (const t3 of bcAnd(r.prem, t2, d + 1)) { row.st = 'ok'; row.txt = `proved by rule ${ri + 1}`; snap(`All premises of rule ${ri + 1} hold, so <b>${esc(LG.str(LG.subst(goal, t3)))}</b> is proved.`, me); yield t3; row.st = 'open'; }
        }
        if (!any) { row.st = 'fail'; row.txt = 'no fact or rule matches'; snap(`Nothing in the KB unifies with ${esc(row.t)}. This goal fails.`, me); }
        else if (row.st !== 'ok') { row.st = 'fail'; }
      }
      function* bcAnd(goals, th, d) {
        if (!goals.length) { yield th; return; }
        for (const t1 of bcOr(goals[0], th, d)) yield* bcAnd(goals.slice(1), t1, d);
      }
      const it = bcOr(Q, {}, 0).next();
      if (!it.done) {
        const qv = LG.str(LG.subst(Q, it.value));
        const vars = [];
        const coll = t => { if (t.t === 'var') vars.push(t.name); if (t.args) t.args.forEach(coll); };
        Q.args.forEach(coll);
        snap(`Done: <b>${esc(qv)}</b> is proved.${vars.length ? ` The answer binds ${vars.map(v => v + ' = ' + LG.tstr(LG.subst({ t: 'var', name: v }, it.value))).join(', ')}.` : ''}`, null, { done: 'yes' });
      } else snap(`Done: ${esc(LG.str(Q))} cannot be proved.`, null, { done: 'no' });
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      if (z.p.mode === 'fc') {
        const byRound = {};
        f.facts.forEach(x => (byRound[x.round] = byRound[x.round] || []).push(x));
        let y = 22;
        Object.keys(byRound).forEach(r => {
          D.text(g, r === '0' ? 'Facts at the start' : `Added in round ${r}`, 18, y, { s: 12, b: true, c: r === '0' ? c.ink2 : c.cv });
          y += 22;
          let x = 18;
          byRound[r].forEach(o => {
            const s = LG.str(o.a), w = tw(g, s, { s: 12, mono: true, b: true }) + 14;
            if (x + w > z.W - 18) { x = 18; y += 28; }
            const cur = s === f.cur;
            tag(g, s, x + w / 2, y, { s: 12, mono: true, fill: cur ? c.cv : r === '0' ? c.bg : 'rgba(14,116,144,.14)', stroke: cur ? c.cv : r === '0' ? c.line : c.cv, c: cur ? '#fff' : c.ink });
            x += w + 8;
          });
          y += 36;
        });
        if (f.done) tag(g, f.done === 'yes' ? 'query proved' : 'query not proved', z.W / 2, z.H - 16, { s: 13, fill: f.done === 'yes' ? c.green : c.red, stroke: f.done === 'yes' ? c.green : c.red, c: '#fff' });
        return;
      }
      const rows = f.rows.map((r, i) => ({ d: r.d, t: `${r.t}${r.txt ? '   ' + r.txt : ''}`, mono: true, s: 12, b: i === f.cur, col: r.st === 'ok' ? c.green : r.st === 'fail' ? c.red : i === f.cur ? c.cv : c.ink, box: i === f.cur ? 'rgba(14,116,144,.12)' : null, edge: c.cv }));
      rowsPaint(z, rows, 18, 16, 22, 17);
      if (f.done) tag(g, f.done === 'yes' ? 'query proved' : 'query not proved', z.W / 2, z.H - 14, { s: 13, fill: f.done === 'yes' ? c.green : c.red, stroke: f.done === 'yes' ? c.green : c.red, c: '#fff' });
    }
  });
})();
