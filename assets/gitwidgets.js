/* ===== Git and CI/CD animations.
   Every animation is declared with CVZ.def(name, spec) from assets/cvviz.js, so every value it uses has a control the
   reader can change, a Reset button, and a "Try this" list that sets suggested values.
   The bottom of the file also wires the boxes from tools/git-build/gitkit.py: Copy buttons, line notes in files,
   simple YAML and shell colouring, and the baby step tick boxes. ===== */
const GITZ = (() => {
  const { D, def, esc } = CVZ;
  const FONT = (o = {}) => `${o.b ? '800 ' : '600 '}${o.s || 13}px ${o.mono ? '"JetBrains Mono", monospace' : 'Nunito, system-ui, sans-serif'}`;
  function tw(g, s, o = {}) { g.save(); g.font = FONT(o); const w = g.measureText(String(s)).width; g.restore(); return w; }
  function rr(g, x, y, w, h, r, o = {}) {
    g.save(); g.beginPath();
    r = Math.max(0, Math.min(r, w / 2, h / 2));
    g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
    if (o.fill) { g.fillStyle = o.fill; g.fill(); }
    if (o.stroke) { g.strokeStyle = o.stroke; g.lineWidth = o.w || 1.5; if (o.dash) g.setLineDash(o.dash); g.stroke(); }
    g.restore();
  }
  /* a label in a rounded box centred on x, y. Returns its width */
  function tag(g, s, x, y, o = {}) {
    const fs = o.s || 12, w = tw(g, s, { s: fs, b: o.b !== false, mono: o.mono }) + 12, h = fs + 8;
    const cw = g.canvas.width / (g.getTransform().a || 1);
    x = Math.max(w / 2 + 2, Math.min(cw - w / 2 - 2, x));   /* keep the whole label on the canvas */
    rr(g, x - w / 2, y - h / 2, w, h, 6, { fill: o.fill, stroke: o.stroke, w: o.lw || 1.2 });
    D.text(g, s, x, y + 1, { a: 'center', bl: 'middle', s: fs, b: o.b !== false, mono: o.mono, c: o.c });
    return w;
  }
  function fitText(g, s, maxW, o = {}) {
    s = String(s);
    if (tw(g, s, o) <= maxW) return s;
    while (s.length > 1 && tw(g, s + '…', o) > maxW) s = s.slice(0, -1);
    return s + '…';
  }
  function wrap(g, s, x, y, maxW, o = {}) {
    const lh = o.lh || (o.s || 13) + 5;
    let line = '';
    String(s).split(/\s+/).filter(Boolean).forEach(w => {
      const t = line ? line + ' ' + w : w;
      if (line && tw(g, t, o) > maxW) { D.text(g, line, x, y, o); y += lh; line = w; } else line = t;
    });
    if (line) { D.text(g, line, x, y, o); y += lh; }
    return y;
  }
  /* a box with a title strip */
  function panel(g, z, x, y, w, h, title, colour) {
    rr(g, x, y, w, h, 10, { fill: z.col.surf, stroke: colour || z.col.line, w: 1.5 });
    rr(g, x, y, w, 24, 10, { fill: colour || z.col.bg });
    g.save(); g.fillStyle = colour || z.col.bg; g.fillRect(x, y + 12, w, 12); g.restore();
    D.text(g, fitText(g, title, w - 12, { s: 12, b: true }), x + w / 2, y + 16, { a: 'center', s: 12, b: true, c: colour ? '#fff' : z.col.ink });
  }

  /* ---------- hashing: SHA-1 and SHA-256 on bytes, as Git does for object ids ---------- */
  const enc = s => new TextEncoder().encode(s);
  const hex = b => Array.from(b, x => x.toString(16).padStart(2, '0')).join('');
  const unhex = h => new Uint8Array(h.match(/../g).map(x => parseInt(x, 16)));
  function pad64(bytes, bigLen) {
    const ml = bytes.length, total = ((ml + 9 + 63) >> 6) << 6, m = new Uint8Array(total);
    m.set(bytes); m[ml] = 0x80;
    const dv = new DataView(m.buffer), bits = ml * 8;
    dv.setUint32(total - 4, bits >>> 0); dv.setUint32(total - 8, Math.floor(bits / 4294967296));
    return { m, dv, total };
  }
  const rotl = (x, n) => (x << n) | (x >>> (32 - n));
  function sha1(bytes) {
    const { dv, total } = pad64(bytes);
    let h0 = 0x67452301, h1 = 0xEFCDAB89, h2 = 0x98BADCFE, h3 = 0x10325476, h4 = 0xC3D2E1F0;
    const w = new Uint32Array(80);
    for (let i = 0; i < total; i += 64) {
      for (let t = 0; t < 16; t++) w[t] = dv.getUint32(i + t * 4);
      for (let t = 16; t < 80; t++) w[t] = rotl(w[t - 3] ^ w[t - 8] ^ w[t - 14] ^ w[t - 16], 1);
      let a = h0, b = h1, c = h2, d = h3, e = h4;
      for (let t = 0; t < 80; t++) {
        let f, k;
        if (t < 20) { f = (b & c) | (~b & d); k = 0x5A827999; } else if (t < 40) { f = b ^ c ^ d; k = 0x6ED9EBA1; }
        else if (t < 60) { f = (b & c) | (b & d) | (c & d); k = 0x8F1BBCDC; } else { f = b ^ c ^ d; k = 0xCA62C1D6; }
        const tmp = (rotl(a, 5) + f + e + k + w[t]) >>> 0;
        e = d; d = c; c = rotl(b, 30) >>> 0; b = a; a = tmp;
      }
      h0 = (h0 + a) >>> 0; h1 = (h1 + b) >>> 0; h2 = (h2 + c) >>> 0; h3 = (h3 + d) >>> 0; h4 = (h4 + e) >>> 0;
    }
    const out = new Uint8Array(20), o = new DataView(out.buffer);
    [h0, h1, h2, h3, h4].forEach((v, i) => o.setUint32(i * 4, v));
    return out;
  }
  const K256 = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];
  function sha256(bytes) {
    const { dv, total } = pad64(bytes);
    const H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    const w = new Uint32Array(64), rotr = (x, n) => (x >>> n) | (x << (32 - n));
    for (let i = 0; i < total; i += 64) {
      for (let t = 0; t < 16; t++) w[t] = dv.getUint32(i + t * 4);
      for (let t = 16; t < 64; t++) {
        const s0 = rotr(w[t - 15], 7) ^ rotr(w[t - 15], 18) ^ (w[t - 15] >>> 3), s1 = rotr(w[t - 2], 17) ^ rotr(w[t - 2], 19) ^ (w[t - 2] >>> 10);
        w[t] = (w[t - 16] + s0 + w[t - 7] + s1) >>> 0;
      }
      let [a, b, c, d, e, f, g, h] = H;
      for (let t = 0; t < 64; t++) {
        const S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25), ch = (e & f) ^ (~e & g), t1 = (h + S1 + ch + K256[t] + w[t]) >>> 0;
        const S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22), mj = (a & b) ^ (a & c) ^ (b & c), t2 = (S0 + mj) >>> 0;
        h = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      [a, b, c, d, e, f, g, h].forEach((v, k) => { H[k] = (H[k] + v) >>> 0; });
    }
    const out = new Uint8Array(32), o = new DataView(out.buffer);
    H.forEach((v, i) => o.setUint32(i * 4, v));
    return out;
  }
  const cat = (...parts) => { const n = parts.reduce((s, p) => s + p.length, 0), out = new Uint8Array(n); let i = 0; parts.forEach(p => { out.set(p, i); i += p.length; }); return out; };
  /* the bytes Git hashes for one object: "<type> <size>\0<content>" */
  function objBytes(type, content) { const c = typeof content === 'string' ? enc(content) : content; return cat(enc(`${type} ${c.length}\0`), c); }
  const oid = (type, content, algo = 'sha1') => hex((algo === 'sha256' ? sha256 : sha1)(objBytes(type, content)));
  /* a tree object: entries [mode, name, hex id], sorted the way Git sorts them (a folder sorts as name + '/') */
  function treeBytes(entries) {
    const sorted = entries.slice().sort((a, b) => { const ka = a[1] + (a[0] === '40000' ? '/' : ''), kb = b[1] + (b[0] === '40000' ? '/' : ''); return ka < kb ? -1 : ka > kb ? 1 : 0; });
    return cat(...sorted.map(([mode, name, id]) => cat(enc(`${mode} ${name}\0`), unhex(id))));
  }

  /* ---------- a tiny Git that only knows about commits and refs, for the commit graph animations ---------- */
  function words(line) {
    const out = []; let cur = '', q = null, any = false;
    for (const ch of line) {
      if (q) { if (ch === q) q = null; else cur += ch; continue; }
      if (ch === '"' || ch === "'") { q = ch; any = true; continue; }
      if (/\s/.test(ch)) { if (cur || any) out.push(cur); cur = ''; any = false; continue; }
      cur += ch;
    }
    if (cur || any) out.push(cur);
    return out;
  }
  function Repo() {
    const R = { commits: {}, order: [], br: { main: 'C0' }, tags: {}, head: { ref: 'main' }, lanes: { main: 0 }, nextLane: 1, n: 1, reflog: [], squash: null, out: [] };
    R.commits.C0 = { id: 'C0', parents: [], msg: 'first commit', lane: 0, orig: 'C0' };
    R.order.push('C0');
    R.reflog.push({ id: 'C0', msg: 'commit (initial): first commit' });
    return R;
  }
  const headId = R => R.head.ref ? R.br[R.head.ref] : R.head.id;
  function ancestors(R, id) {
    const seen = new Set(), st = [id];
    while (st.length) { const c = st.pop(); if (!c || seen.has(c)) continue; seen.add(c); R.commits[c].parents.forEach(p => st.push(p)); }
    return seen;
  }
  const isAnc = (R, a, b) => ancestors(R, b).has(a);   /* a is an ancestor of b (or equal) */
  function mergeBase(R, a, b) {
    const A = ancestors(R, a), common = [...ancestors(R, b)].filter(x => A.has(x));
    /* best common ancestors: not an ancestor of another common ancestor */
    const best = common.filter(c => !common.some(o => o !== c && isAnc(R, c, o)));
    return best.sort((x, y) => R.order.indexOf(y) - R.order.indexOf(x));
  }
  function revparse(R, s) {
    s = String(s || '').trim();
    if (!s) throw new Error('empty revision');
    const m = s.match(/^(.*?)((?:[~^]\d*)*)$/);
    let base = m[1], suf = m[2], id;
    const rl = base.match(/^(HEAD|@)@\{(\d+)\}$/);
    if (rl) { const k = +rl[2], e = R.reflog[R.reflog.length - 1 - k]; if (!e) throw new Error(`log for 'HEAD' only has ${R.reflog.length} entries`); id = e.id; }
    else if (base === 'HEAD' || base === '@') id = headId(R);
    else if (R.br[base] !== undefined) id = R.br[base];
    else if (R.tags[base] !== undefined) id = R.tags[base];
    else if (R.commits[base]) id = base;
    else throw new Error(`ambiguous argument '${s}': unknown revision or path not in the working tree.`);
    const ops = suf.match(/[~^]\d*/g) || [];
    for (const op of ops) {
      const n = op.length > 1 ? +op.slice(1) : 1;
      if (op[0] === '~') { for (let i = 0; i < n; i++) { const p = R.commits[id].parents[0]; if (!p) throw new Error(`ambiguous argument '${s}': the history is not that long`); id = p; } }
      else { if (n === 0) continue; const p = R.commits[id].parents[n - 1]; if (!p) throw new Error(`ambiguous argument '${s}': ${id} has no parent number ${n}`); id = p; }
    }
    return id;
  }
  function laneOf(R, name) { if (R.lanes[name] === undefined) R.lanes[name] = Math.min(4, R.nextLane++); return R.lanes[name]; }
  function curLane(R) { return R.head.ref ? laneOf(R, R.head.ref) : laneOf(R, '(detached)'); }
  function newCommit(R, parents, msg, orig) {
    const id = orig && orig !== 'new' ? nextCopyName(R, orig) : 'C' + R.n++;
    R.commits[id] = { id, parents, msg, lane: curLane(R), orig: orig && orig !== 'new' ? R.commits[orig].orig : id };
    R.order.push(id);
    return id;
  }
  function nextCopyName(R, orig) { let base = R.commits[orig].orig, name = base + "'"; while (R.commits[name]) name += "'"; return name; }
  function moveHead(R, id, why) {
    if (R.head.ref) R.br[R.head.ref] = id; else R.head.id = id;
    R.reflog.push({ id, msg: why });
  }
  function exec(R, line) {
    const w = words(line.trim());
    if (!w.length || w[0].startsWith('#')) return null;
    if (w[0] !== 'git') throw new Error(`${w[0]}: only git commands work here`);
    const cmd = w[1], a = w.slice(2);
    const flag = f => { const i = a.indexOf(f); if (i >= 0) { a.splice(i, 1); return true; } return false; };
    const opt = f => { const i = a.indexOf(f); if (i >= 0) { const v = a[i + 1]; a.splice(i, 2); return v; } return null; };
    const cur = headId(R), where = R.head.ref || 'detached HEAD';
    if (cmd === 'commit') {
      const amend = flag('--amend'); flag('-a'); flag('-am');
      const msg = opt('-m') || (R.squash ? `Squashed commit of ${R.squash}` : `commit ${R.n}`);
      if (amend) {
        const old = R.commits[cur];
        const id = newCommit(R, old.parents.slice(), msg, 'new');
        moveHead(R, id, `commit (amend): ${msg}`);
        return `[${where} ${id}] ${msg} (amended, ${cur} is no longer on any branch)`;
      }
      const id = newCommit(R, [cur], msg, 'new');
      R.squash = null;
      moveHead(R, id, `commit: ${msg}`);
      return `[${where} ${id}] ${msg}`;
    }
    if (cmd === 'branch') {
      if (!a.length) return Object.keys(R.br).map(b => (b === R.head.ref ? '* ' : '  ') + b).join('\n');
      if (a[0] === '-d' || a[0] === '-D') {
        const b = a[1];
        if (R.br[b] === undefined) throw new Error(`branch '${b}' not found`);
        if (b === R.head.ref) throw new Error(`cannot delete branch '${b}' used by worktree`);
        if (a[0] === '-d' && !isAnc(R, R.br[b], cur)) throw new Error(`the branch '${b}' is not fully merged. If you are sure you want to delete it, run 'git branch -D ${b}'`);
        const was = R.br[b]; delete R.br[b];
        return `Deleted branch ${b} (was ${was}).`;
      }
      if (a[0] === '-m') {
        const [o, nn] = a.length === 3 ? [a[1], a[2]] : [R.head.ref, a[1]];
        if (R.br[o] === undefined) throw new Error(`no branch named '${o}'`);
        R.br[nn] = R.br[o]; delete R.br[o]; R.lanes[nn] = laneOf(R, o);
        if (R.head.ref === o) R.head.ref = nn;
        return `renamed ${o} to ${nn}`;
      }
      if (a[0] === '-f') { const id = revparse(R, a[2] || 'HEAD'); if (a[1] === R.head.ref) throw new Error(`cannot force update the branch '${a[1]}' used by worktree`); R.br[a[1]] = id; laneOf(R, a[1]); return `moved ${a[1]} to ${id}`; }
      const name = a[0];
      if (R.br[name] !== undefined) throw new Error(`a branch named '${name}' already exists`);
      R.br[name] = revparse(R, a[1] || 'HEAD'); laneOf(R, name);
      return `created ${name} at ${R.br[name]} (HEAD did not move)`;
    }
    if (cmd === 'switch' || cmd === 'checkout') {
      let create = flag(cmd === 'switch' ? '-c' : '-b') || flag('-C') || flag('-B');
      const detach = flag('--detach');
      const target = a[0];
      if (!target) throw new Error('missing branch name');
      if (create) {
        if (R.br[target] !== undefined) throw new Error(`a branch named '${target}' already exists`);
        const id = revparse(R, a[1] || 'HEAD');
        R.br[target] = id; laneOf(R, target); R.head = { ref: target };
        R.reflog.push({ id, msg: `checkout: moving from ${where} to ${target}` });
        return `Switched to a new branch '${target}'`;
      }
      if (R.br[target] !== undefined && !detach) {
        R.head = { ref: target }; R.reflog.push({ id: R.br[target], msg: `checkout: moving from ${where} to ${target}` });
        return `Switched to branch '${target}'`;
      }
      if (cmd === 'switch' && !detach) throw new Error(`a branch is expected, got '${target}'. Use git switch --detach ${target} to look at a commit`);
      const id = revparse(R, target);
      R.head = { id }; R.reflog.push({ id, msg: `checkout: moving from ${where} to ${target}` });
      return `HEAD is now at ${id} ${R.commits[id].msg}\nYou are in 'detached HEAD' state. New commits here belong to no branch until you create one with git switch -c <name>.`;
    }
    if (cmd === 'merge') {
      const noff = flag('--no-ff'), squash = flag('--squash'), ffonly = flag('--ff-only');
      const t = revparse(R, a[0]), name = a[0];
      if (isAnc(R, t, cur)) return 'Already up to date.';
      if (squash) { R.squash = name; return `Squash commit -- not updating HEAD\nThe changes of ${name} are staged. Run git commit to make one ordinary commit from them.`; }
      if (isAnc(R, cur, t) && !noff) { moveHead(R, t, `merge ${name}: Fast-forward`); return `Updating ${cur}..${t}\nFast-forward (no new commit, ${where} just moved to ${t})`; }
      if (ffonly) throw new Error('Not possible to fast-forward, aborting.');
      const id = newCommit(R, [cur, t], `Merge branch '${name}'`, 'new');
      moveHead(R, id, `merge ${name}: Merge made by the 'ort' strategy.`);
      return `Merge made by the 'ort' strategy. New merge commit ${id} has two parents: ${cur} and ${t} (merge base ${mergeBase(R, cur, t)[0]})`;
    }
    if (cmd === 'rebase') {
      const onto = opt('--onto');
      const upstream = a[0];
      if (!upstream) throw new Error('give the branch to rebase onto, for example git rebase main');
      if (a[1]) { if (R.br[a[1]] === undefined) throw new Error(`no branch named '${a[1]}'`); R.head = { ref: a[1] }; }
      const tip = headId(R), up = revparse(R, upstream), base = onto ? revparse(R, onto) : up;
      const upSet = ancestors(R, up), upPatches = new Set([...upSet].map(c => R.commits[c].orig));
      const todo = R.order.filter(c => isAnc(R, c, tip) && !upSet.has(c) && R.commits[c].parents.length < 2);
      if (!todo.length) {
        if (isAnc(R, tip, base) && tip !== base) { moveHead(R, base, `rebase (finish): fast-forward to ${base}`); return `Successfully rebased and updated ${R.head.ref || 'HEAD'} (fast-forward to ${base}).`; }
        return `Current branch ${R.head.ref || 'HEAD'} is up to date.`;
      }
      let at = base; const made = [], skipped = [];
      for (const c of todo) {
        if (upPatches.has(R.commits[c].orig) && !onto) { skipped.push(c); continue; }
        const id = newCommit(R, [at], R.commits[c].msg, c); made.push(`${c} → ${id}`); at = id;
      }
      moveHead(R, at, `rebase (finish): returning to ${R.head.ref ? 'refs/heads/' + R.head.ref : 'HEAD'}`);
      return `Successfully rebased and updated ${R.head.ref || 'HEAD'}.\nReplayed: ${made.join(', ') || 'nothing'}${skipped.length ? `\nSkipped (already upstream): ${skipped.join(', ')}` : ''}`;
    }
    if (cmd === 'cherry-pick') {
      const outs = [];
      for (const r of a) { const c = revparse(R, r), id = newCommit(R, [headId(R)], R.commits[c].msg, c); moveHead(R, id, `cherry-pick: ${R.commits[c].msg}`); outs.push(`[${where} ${id}] ${R.commits[c].msg} (copy of ${c})`); }
      return outs.join('\n');
    }
    if (cmd === 'revert') {
      const c = revparse(R, a[0]), msg = `Revert "${R.commits[c].msg}"`, id = newCommit(R, [cur], msg, 'new');
      moveHead(R, id, `revert: ${msg}`);
      return `[${where} ${id}] ${msg}\nA new commit that undoes ${c}. History is kept, so this is safe on shared branches.`;
    }
    if (cmd === 'reset') {
      const mode = flag('--hard') ? 'hard' : flag('--soft') ? 'soft' : (flag('--mixed'), 'mixed');
      const id = revparse(R, a[0] || 'HEAD');
      moveHead(R, id, `reset: moving to ${a[0] || 'HEAD'}`);
      const what = { soft: 'The index and your files keep the changes of the commits you stepped over, staged and ready to commit again.', mixed: 'Those changes are kept in your files but unstaged.', hard: 'The index and your files now match the commit. Uncommitted work is gone. Commits are still in the reflog.' }[mode];
      return `${mode === 'hard' ? `HEAD is now at ${id} ${R.commits[id].msg}` : `${where} now points at ${id}`}\n${what}`;
    }
    if (cmd === 'tag') {
      if (a[0] === '-d') { if (R.tags[a[1]] === undefined) throw new Error(`tag '${a[1]}' not found.`); delete R.tags[a[1]]; return `Deleted tag '${a[1]}'`; }
      const ann = flag('-a'); opt('-m');
      if (!a.length) return Object.keys(R.tags).join('\n') || '(no tags)';
      if (R.tags[a[0]] !== undefined) throw new Error(`tag '${a[0]}' already exists`);
      R.tags[a[0]] = revparse(R, a[1] || 'HEAD');
      return `${ann ? 'annotated ' : ''}tag ${a[0]} → ${R.tags[a[0]]}`;
    }
    if (cmd === 'log' || cmd === 'reflog' || cmd === 'status') return '(see the readout below)';
    throw new Error(`'${cmd}' is not supported in this animation. Try commit, branch, switch, checkout, merge, rebase, cherry-pick, revert, reset or tag.`);
  }
  function runScript(text, upto) {
    const R = Repo(), lines = String(text).split('\n'), log = [];
    let k = 0;
    for (let i = 0; i < lines.length && k < upto; i++) {
      const l = lines[i].trim();
      if (!l || l.startsWith('#')) continue;
      k++;
      try { const o = exec(R, l); log.push({ line: l, out: o, ok: true }); }
      catch (e) { log.push({ line: l, out: 'fatal: ' + e.message, ok: false }); }
    }
    return { R, log };
  }
  const cmdCount = text => String(text).split('\n').filter(l => l.trim() && !l.trim().startsWith('#')).length;
  function reachable(R) {
    const s = new Set();
    Object.values(R.br).concat(Object.values(R.tags), [headId(R)]).forEach(id => ancestors(R, id).forEach(c => s.add(c)));
    return s;
  }
  /* draw the commit graph. Commits sit left to right in the order they were made, one row per branch lane */
  function drawGraph(g, z, R, o = {}) {
    const ids = R.order, show = ids.slice(-17), x0 = o.x0 || 40, top = o.top || 64, dy = o.dy || 52;
    const dx = Math.min(56, (z.W - x0 - 40) / Math.max(1, show.length - 1));
    const P = {}; show.forEach((id, i) => { P[id] = [x0 + i * dx, top + R.commits[id].lane * dy]; });
    const reach = reachable(R), hid = headId(R);
    show.forEach(id => R.commits[id].parents.forEach((p, k) => {
      if (!P[p]) return;
      const [x1, y1] = P[id], [x2, y2] = P[p], c = reach.has(id) ? (k ? z.col.purple : z.col.ink2) : z.col.line;
      g.save(); g.strokeStyle = c; g.lineWidth = 2; if (!reach.has(id)) g.setLineDash([4, 4]);
      g.beginPath(); g.moveTo(x1 - 13, y1);
      if (y1 === y2) g.lineTo(x2 + 13, y2); else g.bezierCurveTo((x1 + x2) / 2, y1, (x1 + x2) / 2, y2, x2 + 13, y2);
      g.stroke(); g.restore();
      D.arrow(g, x2 + 22, y2, x2 + 14, y2, c, 2, 6);
    }));
    /* labels of neighbouring commits can collide: move a label up (branches) or down (tags) until it is free */
    const placed = [], cw = z.W;
    const free = (s, x, y, step) => {
      const w = tw(g, s, { s: 11, b: true }) + 12, cx = Math.max(w / 2 + 2, Math.min(cw - w / 2 - 2, x));
      for (let i = 0; i < 6 && placed.some(b => Math.abs(b.x - cx) < (b.w + w) / 2 + 2 && Math.abs(b.y - y) < 19); i++) y += step;
      placed.push({ x: cx, y, w });
      return y;
    };
    show.forEach(id => {
      const [x, y] = P[id], live = reach.has(id), isHead = id === hid;
      D.circle(g, x, y, 13, { fill: live ? (R.commits[id].parents.length > 1 ? z.col.purple : z.col.cv) : z.col.surf, stroke: isHead ? z.col.yellow : live ? z.col.surf : z.col.ink2, w: isHead ? 3 : 1.5 });
      D.text(g, id, x, y + 1, { a: 'center', bl: 'middle', s: id.length > 3 ? 9 : 11, b: true, c: live ? '#fff' : z.col.ink2 });
      const brs = Object.keys(R.br).filter(b => R.br[b] === id).map(b => b === R.head.ref ? `HEAD → ${b}` : b);
      if (!R.head.ref && isHead) brs.unshift('HEAD (detached)');
      brs.forEach((b, k) => tag(g, b, x, free(b, x, y - 26 - k * 19, -19), { s: 11, fill: b.startsWith('HEAD') ? z.col.yellow : z.col.surf, stroke: z.col.cv, c: b.startsWith('HEAD') ? '#3b2a00' : z.col.ink }));
      Object.keys(R.tags).filter(t => R.tags[t] === id).forEach((t, k) => tag(g, '◆ ' + t, x, free('◆ ' + t, x, y + 27 + k * 19, 19), { s: 11, fill: z.col.surf, stroke: z.col.orange, c: z.col.ink }));
    });
    if (ids.length > show.length) D.text(g, `… ${ids.length - show.length} older commits`, 8, 16, { s: 11, c: z.col.ink2 });
    return P;
  }
  function logText(R, from) {
    const seen = ancestors(R, from), list = R.order.filter(c => seen.has(c)).reverse();
    return list.map(c => {
      const refs = Object.keys(R.br).filter(b => R.br[b] === c).map(b => b === R.head.ref ? `HEAD -> ${b}` : b).concat(Object.keys(R.tags).filter(t => R.tags[t] === c).map(t => 'tag: ' + t));
      if (!R.head.ref && c === headId(R)) refs.unshift('HEAD');
      return `${c.padEnd(5)} ${refs.length ? '(' + refs.join(', ') + ') ' : ''}${R.commits[c].msg}`;
    }).join('\n');
  }

  def('gitsim', {
    title: 'Commit graph: type Git commands and watch the history',
    sub: 'Each circle is a commit. Arrows point to the parent. Yellow ring is where HEAD is. Faded commits are no longer on any branch.',
    W: 660, H: 330,
    params: [
      { k: 'cmds', label: 'Git commands, one per line (lines starting with # are notes)', type: 'area', v: 'git commit -m "add login page"\ngit switch -c feature\ngit commit -m "add button"\ngit commit -m "style button"\ngit switch main\ngit commit -m "fix typo"\ngit merge feature' },
      { k: 'show', label: 'Show under the picture', type: 'select', v: 'log', opts: [['log', 'git log --oneline from HEAD'], ['reflog', 'git reflog (where HEAD has been)'], ['both', 'both']] }
    ],
    tips: [
      { t: 'A fast-forward merge: main has not moved since the branch started, so main just slides forward. No merge commit.', set: { cmds: 'git switch -c feature\ngit commit -m "step 1"\ngit commit -m "step 2"\ngit switch main\ngit merge feature' }, play: true },
      { t: 'The same history with --no-ff keeps a merge commit, so the feature stays visible as a bubble.', set: { cmds: 'git switch -c feature\ngit commit -m "step 1"\ngit commit -m "step 2"\ngit switch main\ngit merge --no-ff feature' }, play: true },
      { t: 'Rebase instead of merge: C2 and C3 are copied onto the new main as C2\' and C3\'. The originals fade, because no branch points to them.', set: { cmds: 'git switch -c feature\ngit commit -m "add button"\ngit commit -m "style button"\ngit switch main\ngit commit -m "fix typo"\ngit switch feature\ngit rebase main\ngit switch main\ngit merge feature' }, play: true },
      { t: 'Detached HEAD: look at an old commit, make a commit there, then save it with a branch before it gets lost.', set: { cmds: 'git commit -m "v2"\ngit commit -m "v3"\ngit checkout C1\ngit commit -m "experiment"\ngit switch -c rescue' }, play: true },
      { t: 'Undo three ways: reset moves the branch back, revert adds an undo commit, and HEAD@{1} in the reflog brings the reset commits back.', set: { cmds: 'git commit -m "good"\ngit commit -m "bad"\ngit reset --hard HEAD~1\ngit reset --hard HEAD@{1}\ngit revert HEAD', show: 'both' }, play: true },
      { t: 'Cherry-pick copies one commit from another branch, and a tag marks a release.', set: { cmds: 'git switch -c hotfix\ngit commit -m "fix crash"\ngit commit -m "debug logs"\ngit switch main\ngit cherry-pick C2\ngit tag v1.0.1' }, play: true },
      { t: 'Type a mistake on purpose, like git switch nowhere, and read the error. The graph does not change.', set: { cmds: 'git commit -m "work"\ngit switch nowhere\ngit branch -d main' } }
    ],
    steps: z => cmdCount(z.p.cmds),
    draw(z) {
      const g = z.g, { R, log } = runScript(z.p.cmds, z.step);
      drawGraph(g, z, R);
      const last = log[log.length - 1];
      let h = last ? `<p><b>Step ${log.length}:</b> <code>${esc(last.line)}</code></p><pre class="${last.ok ? '' : 'gk-bad'}">${esc(last.out || '')}</pre>` : '<p>Press Play or Step to run the commands one at a time.</p>';
      if (z.p.show !== 'reflog') h += `<p><b>git log --oneline</b> (newest first, from HEAD)</p><pre>${esc(logText(R, headId(R)))}</pre>`;
      if (z.p.show !== 'log') h += `<p><b>git reflog</b> (HEAD@{0} is now)</p><pre>${esc(R.reflog.slice().reverse().slice(0, 8).map((e, i) => `${e.id.padEnd(5)} HEAD@{${i}}: ${e.msg}`).join('\n'))}</pre>`;
      return h;
    }
  });

  /* ---------- revision selection on a fixed history ---------- */
  function demoRepo() {
    const R = runScript('git commit -m "add login"\ngit switch -c feature C0\ngit commit -m "button"\ngit commit -m "style"\ngit switch main\ngit commit -m "fix typo"\ngit tag v1.0\ngit merge feature\ngit commit -m "release notes"', 99).R;
    return R;
  }
  function selectRange(R, expr) {
    expr = expr.trim();
    let m;
    if ((m = expr.match(/^(.+?)\.\.\.(.+)$/))) {
      const a = revparse(R, m[1]), b = revparse(R, m[2]), A = ancestors(R, a), B = ancestors(R, b);
      return { set: new Set([...A, ...B].filter(x => !(A.has(x) && B.has(x)))), what: `commits on either side but not on both (symmetric difference of ${m[1]} and ${m[2]})` };
    }
    if ((m = expr.match(/^(.*?)\.\.(.*)$/))) {
      const a = revparse(R, m[1] || 'HEAD'), b = revparse(R, m[2] || 'HEAD'), A = ancestors(R, a);
      return { set: new Set([...ancestors(R, b)].filter(x => !A.has(x))), what: `commits reachable from ${m[2] || 'HEAD'} but not from ${m[1] || 'HEAD'}` };
    }
    const parts = expr.split(/\s+/), inc = new Set(), exc = new Set();
    parts.forEach(p => { if (p.startsWith('^')) ancestors(R, revparse(R, p.slice(1))).forEach(c => exc.add(c)); else if (p === '--not') { /* handled as plain */ } else ancestors(R, revparse(R, p)).forEach(c => inc.add(c)); });
    if (parts.length === 1 && !expr.startsWith('^')) return { one: revparse(R, expr), set: inc, what: `the commit ${expr} names, and in git log everything reachable from it` };
    return { set: new Set([...inc].filter(c => !exc.has(c))), what: 'reachable from the plain names but not from the ^ names' };
  }
  def('revsel', {
    title: 'Naming commits: ~, ^, .. and ...',
    sub: 'Type a revision or a range. The picked commit gets a yellow ring, and every commit the range selects turns green.',
    W: 640, H: 250,
    params: [{ k: 'expr', label: 'Revision or range', type: 'text', v: 'main~2' },
      { k: 'ans', label: 'Reveal the answer', type: 'check', v: true, reveal: true }],
    tips: [
      { t: 'main~1 is the first parent of main. For a merge commit the first parent is the branch you were on when you merged.', set: { expr: 'main~1', ans: true } },
      { t: 'main~1^2 is the second parent of that merge: the tip of feature.', set: { expr: 'main~1^2', ans: true } },
      { t: 'main~3 walks first parents only: C4, C3, C1.', set: { expr: 'main~3', ans: true } },
      { t: 'v1.0..main is what main has that v1.0 does not: the new work since the release.', set: { expr: 'v1.0..main', ans: true } },
      { t: 'feature...v1.0 is the symmetric difference: commits on one side but not both.', set: { expr: 'feature...v1.0', ans: true } },
      { t: 'Untick Reveal, type HEAD~2^ yourself and predict before you look.', set: { expr: 'HEAD~2^', ans: false } }
    ],
    draw(z) {
      const g = z.g, R = demoRepo();
      let sel = null, err = '';
      try { sel = selectRange(R, z.p.expr); } catch (e) { err = e.message; }
      const P = drawGraph(g, z, R, { top: 70, dy: 70, x0: 60 });
      if (sel && z.p.ans) {
        Object.keys(P).forEach(id => {
          if (sel.one === id) D.circle(g, P[id][0], P[id][1], 18, { stroke: z.col.yellow, w: 4 });
          else if (!sel.one && sel.set.has(id)) D.circle(g, P[id][0], P[id][1], 18, { stroke: z.col.green, w: 4 });
        });
      }
      D.text(g, 'main lane', 8, 74, { s: 10, c: z.col.ink2 });
      D.text(g, 'feature lane', 8, 144, { s: 10, c: z.col.ink2 });
      if (err) return `<p class="gk-bad">fatal: ${esc(err)}</p>`;
      if (!z.p.ans) return '<p>Make your prediction, then tick Reveal the answer.</p>';
      const list = [...sel.set].sort((a, b) => R.order.indexOf(b) - R.order.indexOf(a));
      return sel.one ? `<p><b>${esc(z.p.expr)}</b> is <b>${sel.one}</b> (${esc(R.commits[sel.one].msg)}).</p>` :
        `<p><b>${esc(z.p.expr)}</b> selects ${list.length} commit${list.length === 1 ? '' : 's'}: <b>${list.join(', ') || 'none'}</b>. These are the ${sel.what}.</p>`;
    }
  });

  /* ---------- line diff (longest common subsequence) and a unified diff with hunks ---------- */
  function lcs(a, b) {
    const n = a.length, m = b.length, T = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
    for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) T[i][j] = a[i] === b[j] ? T[i + 1][j + 1] + 1 : Math.max(T[i + 1][j], T[i][j + 1]);
    const ops = []; let i = 0, j = 0;
    while (i < n && j < m) {
      if (a[i] === b[j]) { ops.push({ t: ' ', s: a[i], i, j }); i++; j++; }
      else if (T[i + 1][j] >= T[i][j + 1]) { ops.push({ t: '-', s: a[i], i }); i++; }
      else { ops.push({ t: '+', s: b[j], j }); j++; }
    }
    while (i < n) { ops.push({ t: '-', s: a[i], i }); i++; }
    while (j < m) { ops.push({ t: '+', s: b[j], j }); j++; }
    return ops;
  }
  const splitLines = s => { const L = String(s).split('\n'); if (L.length && L[L.length - 1] === '') L.pop(); return L; };
  function hunks(ops, ctx) {
    const out = [], ch = ops.map((o, k) => o.t !== ' ' ? k : -1).filter(k => k >= 0);
    if (!ch.length) return out;
    let start = Math.max(0, ch[0] - ctx), end = Math.min(ops.length - 1, ch[0] + ctx);
    for (let q = 1; q < ch.length; q++) {
      if (ch[q] - ctx <= end + 1) end = Math.min(ops.length - 1, ch[q] + ctx);
      else { out.push([start, end]); start = Math.max(0, ch[q] - ctx); end = Math.min(ops.length - 1, ch[q] + ctx); }
    }
    out.push([start, end]);
    return out.map(([s, e]) => {
      const part = ops.slice(s, e + 1);
      let oi = 0, ni = 0;
      for (let k = 0; k < s; k++) { if (ops[k].t !== '+') oi++; if (ops[k].t !== '-') ni++; }
      const oc = part.filter(o => o.t !== '+').length, nc = part.filter(o => o.t !== '-').length;
      const os = oc ? oi + 1 : oi, ns = nc ? ni + 1 : ni;
      return { head: `@@ -${os}${oc === 1 ? '' : ',' + oc} +${ns}${nc === 1 ? '' : ',' + nc} @@`, part };
    });
  }
  def('diffviz', {
    title: 'How git diff finds what changed',
    sub: 'Git lines up the two versions, keeps the longest run of shared lines, and marks the rest as removed (−) or added (+).',
    W: 640, H: 300,
    params: [
      { k: 'old', label: 'Old version (what the commit or index has)', type: 'area', v: 'Shopping list\nmilk\nbread\neggs\nbutter\njam\ntea' },
      { k: 'new', label: 'New version (your file now)', type: 'area', v: 'Shopping list\nmilk\nbrown bread\neggs\nbutter\njam\ntea\ncoffee' },
      { k: 'ctx', label: 'Context lines around each change (-U)', type: 'range', v: 1, min: 0, max: 3 }
    ],
    tips: [
      { t: 'With -U0 every change is its own hunk and no unchanged line is shown.', set: { ctx: 0 } },
      { t: 'With -U3 (the Git default) nearby changes merge into one hunk.', set: { ctx: 3 } },
      { t: 'A changed line is always shown as one line removed plus one line added. Git diff never edits a line in place.', set: { old: 'a\nb\nc', new: 'a\nB\nc', ctx: 1 } },
      { t: 'Move a line: diff reports it as a delete in one place and an add in another.', set: { old: 'one\ntwo\nthree\nfour', new: 'two\nthree\nfour\none', ctx: 1 } }
    ],
    draw(z) {
      const g = z.g, a = splitLines(z.p.old), b = splitLines(z.p.new), ops = lcs(a, b);
      const W = z.W, colW = (W - 60) / 2, top = 34, lh = Math.min(22, (z.H - top - 10) / Math.max(1, Math.max(a.length, b.length)));
      D.text(g, 'old', 20 + colW / 2, 22, { a: 'center', b: true, c: z.col.red });
      D.text(g, 'new', 40 + colW * 1.5, 22, { a: 'center', b: true, c: z.col.green });
      const yA = i => top + i * lh, yB = j => top + j * lh;
      ops.forEach(o => { if (o.t === ' ') { g.save(); g.globalAlpha = 0.35; D.line(g, 20 + colW, yA(o.i) + lh / 2, 40 + colW, yB(o.j) + lh / 2, z.col.ink2, 1.5); g.restore(); } });
      a.forEach((s, i) => { const gone = ops.some(o => o.t === '-' && o.i === i); rr(g, 20, yA(i) + 1, colW, lh - 3, 5, { fill: gone ? 'rgba(239,68,68,.18)' : z.col.bg }); D.text(g, fitText(g, (gone ? '− ' : '  ') + s, colW - 10, { s: Math.min(12, lh - 6), mono: true }), 26, yA(i) + lh / 2 + 1, { bl: 'middle', s: Math.min(12, lh - 6), mono: true, c: z.col.ink }); });
      b.forEach((s, j) => { const nw = ops.some(o => o.t === '+' && o.j === j); rr(g, 40 + colW, yB(j) + 1, colW, lh - 3, 5, { fill: nw ? 'rgba(34,197,94,.2)' : z.col.bg }); D.text(g, fitText(g, (nw ? '+ ' : '  ') + s, colW - 10, { s: Math.min(12, lh - 6), mono: true }), 46 + colW, yB(j) + lh / 2 + 1, { bl: 'middle', s: Math.min(12, lh - 6), mono: true, c: z.col.ink }); });
      const hs = hunks(ops, z.p.ctx), add = ops.filter(o => o.t === '+').length, del = ops.filter(o => o.t === '-').length;
      const body = hs.map(h => `<span class="gk-hunk">${esc(h.head)}</span>\n` + h.part.map(o => `<span class="${o.t === '+' ? 'gk-add' : o.t === '-' ? 'gk-del' : ''}">${esc(o.t + o.s)}</span>`).join('\n')).join('\n');
      return `<p>${add} insertion${add === 1 ? '' : 's'}(+), ${del} deletion${del === 1 ? '' : 's'}(−), ${hs.length} hunk${hs.length === 1 ? '' : 's'}. In <code>@@ -a,b +c,d @@</code>, a and c are the first line numbers, b and d how many lines the hunk covers.</p><pre>--- a/list.txt\n+++ b/list.txt\n${body || '(no changes)'}</pre>`;
    }
  });

  /* ---------- three way merge, line by line ---------- */
  function matchMap(o, x) { const m = new Array(o.length + 1).fill(-1); lcs(o, x).forEach(op => { if (op.t === ' ') m[op.i] = op.j; }); m[o.length] = x.length; return m; }
  function diff3(o, a, b) {
    const ma = matchMap(o, a), mb = matchMap(o, b), out = [];
    let i = 0, j = 0, k = 0;
    while (i <= o.length) {
      if (i < o.length && ma[i] === j && mb[i] === k) { out.push({ t: 'same', lines: [o[i]] }); i++; j++; k++; continue; }
      let x = i;
      while (x < o.length && !(ma[x] >= j && mb[x] >= k && ma[x] !== -1 && mb[x] !== -1)) x++;
      const O = o.slice(i, x), A = a.slice(j, ma[x]), B = b.slice(k, mb[x]);
      if (O.length || A.length || B.length) {
        const eq = (p, q) => p.length === q.length && p.every((v, n) => v === q[n]);
        if (eq(A, O)) out.push({ t: 'theirs', lines: B, base: O });
        else if (eq(B, O)) out.push({ t: 'ours', lines: A, base: O });
        else if (eq(A, B)) out.push({ t: 'both', lines: A, base: O });
        else out.push({ t: 'conflict', ours: A, theirs: B, base: O });
      }
      if (x >= o.length) break;
      i = x; j = ma[x]; k = mb[x];
    }
    return out;
  }
  def('merge3', {
    title: 'Three way merge: base, ours and theirs',
    sub: 'Git compares both branches with their common ancestor. A part changed on one side only is taken automatically. A part changed on both sides in different ways is a conflict.',
    W: 640, H: 230,
    params: [
      { k: 'base', label: 'Base (the merge base, common ancestor)', type: 'area', v: 'title: Shop\ncolour: blue\nprice: 10\nfooter: hello' },
      { k: 'ours', label: 'Ours (main, where you are)', type: 'area', v: 'title: Shop\ncolour: green\nprice: 10\nfooter: hello' },
      { k: 'theirs', label: 'Theirs (feature, being merged in)', type: 'area', v: 'title: Shop\ncolour: red\nprice: 12\nfooter: hello' },
      { k: 'style', label: 'Conflict style (merge.conflictStyle)', type: 'select', v: 'merge', opts: [['merge', 'merge (default)'], ['diff3', 'diff3 (also shows base)']] }
    ],
    tips: [
      { t: 'Both sides changed the colour line differently, so it conflicts. The price changed on one side only, so Git takes 12 by itself.', set: { theirs: 'title: Shop\ncolour: red\nprice: 12\nfooter: hello' } },
      { t: 'Make theirs pick green too. The same change on both sides is not a conflict.', set: { theirs: 'title: Shop\ncolour: green\nprice: 12\nfooter: hello' } },
      { t: 'Switch to diff3 to see the base between ||||||| and =======. It shows what both sides started from.', set: { style: 'diff3', theirs: 'title: Shop\ncolour: red\nprice: 12\nfooter: hello' } },
      { t: 'One side deletes a line the other side edits. That is also a conflict.', set: { ours: 'title: Shop\ncolour: blue\nprice: 10', theirs: 'title: Shop\ncolour: blue\nprice: 10\nfooter: welcome', style: 'merge' } }
    ],
    draw(z) {
      const g = z.g, o = splitLines(z.p.base), a = splitLines(z.p.ours), b = splitLines(z.p.theirs), parts = diff3(o, a, b);
      const COL = { same: z.col.bg, ours: 'rgba(59,130,246,.25)', theirs: 'rgba(168,85,247,.25)', both: 'rgba(34,197,94,.25)', conflict: 'rgba(239,68,68,.3)' };
      const NAME = { same: 'unchanged', ours: 'changed in ours only, taken', theirs: 'changed in theirs only, taken', both: 'same change on both, taken once', conflict: 'CONFLICT, you decide' };
      let y = 12; const rowH = Math.min(30, (z.H - 20) / Math.max(1, parts.length));
      parts.forEach(p => {
        rr(g, 12, y, z.W - 24, rowH - 4, 6, { fill: COL[p.t] });
        const txt = p.t === 'conflict' ? `ours: ${p.ours.join(' / ') || '(deleted)'}   theirs: ${p.theirs.join(' / ') || '(deleted)'}` : (p.lines.join(' / ') || '(deleted)');
        D.text(g, NAME[p.t], 22, y + rowH / 2, { bl: 'middle', s: 11, b: true, c: p.t === 'conflict' ? z.col.red : z.col.ink });
        D.text(g, fitText(g, txt, z.W - 250, { s: 11, mono: true }), 230, y + rowH / 2, { bl: 'middle', s: 11, mono: true, c: z.col.ink });
        y += rowH;
      });
      const res = [];
      parts.forEach(p => {
        if (p.t !== 'conflict') { p.lines.forEach(l => res.push(esc(l))); return; }
        res.push('<span class="gk-cf"><<<<<<< HEAD</span>'); p.ours.forEach(l => res.push(`<span class="gk-cf">${esc(l)}</span>`));
        if (z.p.style === 'diff3') { res.push('<span class="gk-cf">||||||| base</span>'); p.base.forEach(l => res.push(`<span class="gk-cf">${esc(l)}</span>`)); }
        res.push('<span class="gk-cf">=======</span>'); p.theirs.forEach(l => res.push(`<span class="gk-cf">${esc(l)}</span>`)); res.push('<span class="gk-cf">>>>>>>> feature</span>');
      });
      const nc = parts.filter(p => p.t === 'conflict').length;
      return (nc ? `<p class="gk-bad">${nc} conflict${nc > 1 ? 's' : ''}. Git stops and says: CONFLICT (content): Merge conflict in shop.yml. Edit the file, remove the markers, then git add shop.yml and git commit.</p>` : '<p class="gk-ok">No conflicts. Git writes the result and makes the merge commit by itself.</p>') +
        `<pre>${res.join('\n')}</pre>`;
    }
  });

  return { tw, rr, tag, wrap, fitText, panel, sha1, sha256, enc, hex, unhex, cat, objBytes, oid, treeBytes, Repo, exec, runScript, drawGraph, revparse, ancestors, mergeBase, lcs, diff3, splitLines, hunks, words };
})();

/* ===== part 2: the three areas, ignore rules, remotes, bisect, objects, plumbing, workflows, hooks, config ===== */
(() => {
  const { D, def, esc } = CVZ;
  const { tw, rr, tag, wrap, fitText, panel, enc, hex, oid, treeBytes, words } = GITZ;

  /* ---------- working tree, index, local repository and remote ---------- */
  function areasRun(text, upto) {
    const S = { wt: { 'README.md': 1, 'app.py': 1 }, ix: { 'README.md': 1, 'app.py': 1 }, commits: [{ msg: 'first commit', snap: { 'README.md': 1, 'app.py': 1 } }], head: 0, remote: 0, ver: { 'README.md': 1, 'app.py': 1 }, stash: [] };
    const snap = () => S.commits[S.head].snap, log = [];
    const lines = String(text).split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));
    lines.slice(0, upto).forEach(l => {
      const w = words(l); let out = '';
      try {
        if (w[0] === 'edit' || w[0] === 'new') {
          const f = w[1]; if (!f) throw new Error('name a file');
          if (w[0] === 'edit' && S.wt[f] === undefined) throw new Error(`${f} does not exist, use new ${f}`);
          S.ver[f] = (S.ver[f] || 0) + 1; S.wt[f] = S.ver[f]; out = `you saved ${f} (now version v${S.wt[f]}) in your editor`;
        } else if (w[0] === 'delete') { delete S.wt[w[1]]; out = `you deleted ${w[1]} from the folder`; }
        else if (w[0] !== 'git') throw new Error('start with git, edit, new or delete');
        else if (w[1] === 'add') {
          const fs = w[2] === '.' || w[2] === '-A' ? Object.keys(Object.assign({}, S.wt, S.ix)) : w.slice(2);
          fs.forEach(f => { if (S.wt[f] === undefined) { if (S.ix[f] === undefined) throw new Error(`pathspec '${f}' did not match any files`); delete S.ix[f]; } else S.ix[f] = S.wt[f]; });
          out = `staged ${fs.join(', ')}`;
        } else if (w[1] === 'commit') {
          if (w.includes('-a') || w.includes('-am')) Object.keys(S.ix).forEach(f => { if (S.wt[f] === undefined) delete S.ix[f]; else S.ix[f] = S.wt[f]; });
          const mi = w.findIndex(x => x === '-m' || x === '-am'), msg = mi >= 0 ? w[mi + 1] : 'commit';
          if (JSON.stringify(S.ix) === JSON.stringify(snap())) throw new Error('nothing to commit (nothing is staged)');
          S.commits = S.commits.slice(0, S.head + 1); S.commits.push({ msg, snap: Object.assign({}, S.ix) }); S.head++;
          out = `[main] ${msg}: a snapshot of the staging area is saved`;
        } else if (w[1] === 'restore') {
          const staged = w.includes('--staged'), fs = w.slice(2).filter(x => !x.startsWith('--'));
          fs.forEach(f => { if (staged) { if (snap()[f] === undefined) delete S.ix[f]; else S.ix[f] = snap()[f]; } else { if (S.ix[f] === undefined) throw new Error(`pathspec '${f}' did not match any file known to git`); S.wt[f] = S.ix[f]; } });
          out = staged ? `unstaged ${fs.join(', ')} (your file keeps its edits)` : `threw away the unstaged edits in ${fs.join(', ')}`;
        } else if (w[1] === 'rm') {
          const cached = w.includes('--cached'), f = w.filter(x => !x.startsWith('-'))[2];
          delete S.ix[f]; if (!cached) delete S.wt[f];
          out = cached ? `${f} will be removed from the next commit but stays in your folder` : `${f} removed from the folder and staged for deletion`;
        } else if (w[1] === 'push') {
          if (S.remote === S.head) out = 'Everything up-to-date';
          else { out = `pushed ${S.head - S.remote} commit${S.head - S.remote > 1 ? 's' : ''} to origin/main`; S.remote = S.head; }
        } else if (w[1] === 'reset') {
          const mode = w.includes('--hard') ? 'hard' : w.includes('--soft') ? 'soft' : 'mixed';
          const t = w.find(x => /^HEAD/.test(x)) || 'HEAD', n = t === 'HEAD' ? 0 : +(t.match(/~(\d*)/) || [0, 1])[1] || 1;
          if (S.head - n < 0) throw new Error('the history is not that long');
          S.head -= n;
          if (mode !== 'soft') S.ix = Object.assign({}, snap());
          if (mode === 'hard') { Object.keys(S.wt).forEach(f => { if (S.ix[f] === undefined && !Object.values(S.commits).some(c => c.snap[f] !== undefined)) return; if (snap()[f] === undefined) delete S.wt[f]; }); Object.assign(S.wt, snap()); }
          out = `reset --${mode}: HEAD moved back ${n} commit${n === 1 ? '' : 's'}` + { soft: ', index and files untouched', mixed: ', index reset, files untouched', hard: ', index and tracked files reset' }[mode];
        } else if (w[1] === 'stash') {
          if (w[2] === 'pop') { const s = S.stash.pop(); if (!s) throw new Error('No stash entries found.'); Object.assign(S.wt, s.wt); out = 'Dropped refs/stash@{0}, your edits are back in the files'; }
          else {
            const wt = {}, ix = {};
            Object.keys(S.wt).forEach(f => { if (S.ix[f] !== undefined && S.wt[f] !== snap()[f]) wt[f] = S.wt[f]; });
            Object.keys(S.ix).forEach(f => { if (S.ix[f] !== snap()[f]) { ix[f] = S.ix[f]; if (wt[f] === undefined) wt[f] = S.wt[f]; } });
            if (!Object.keys(wt).length) throw new Error('No local changes to save');
            S.stash.push({ wt, ix }); Object.keys(wt).forEach(f => { S.wt[f] = snap()[f]; }); S.ix = Object.assign({}, snap());
            out = `Saved working directory and index state WIP on main (stash@{0}). Untracked files stay where they are.`;
          }
        } else throw new Error(`git ${w[1]} is not part of this animation`);
        log.push({ l, out, ok: true });
      } catch (e) { log.push({ l, out: 'error: ' + e.message, ok: false }); }
    });
    return { S, log, snap: snap() };
  }
  function shortStatus(S, H) {
    const files = [...new Set([...Object.keys(H), ...Object.keys(S.ix), ...Object.keys(S.wt)])].sort(), out = [];
    files.forEach(f => {
      const h = H[f], i = S.ix[f], w = S.wt[f];
      if (i === undefined && h === undefined) { if (w !== undefined) out.push(`?? ${f}`); return; }
      const X = h === undefined ? 'A' : i === undefined ? 'D' : h !== i ? 'M' : ' ';
      const Y = i === undefined ? ' ' : w === undefined ? 'D' : w !== i ? 'M' : ' ';
      if (X !== ' ' || Y !== ' ') out.push(`${X}${Y} ${f}`);
      if (i === undefined && w !== undefined) out.push(`?? ${f}`);
    });
    return out;
  }
  def('areas', {
    title: 'Working tree, staging area, repository and remote',
    sub: 'Type commands and watch each file version (v1, v2 ...) move between the four places. edit, new and delete stand for what you do in your editor.',
    W: 660, H: 280,
    params: [{ k: 'cmds', label: 'Commands, one per line', type: 'area', v: 'edit app.py\ngit add app.py\nedit app.py\ngit commit -m "faster search"\ngit add app.py\ngit commit -m "tidy"\ngit push' }],
    tips: [
      { t: 'Edit, stage, edit again, commit. The commit saves the staged v2, not the v3 in your folder. Then stage v3 and commit it too.', set: { cmds: 'edit app.py\ngit add app.py\nedit app.py\ngit commit -m "faster search"\ngit add app.py\ngit commit -m "tidy"\ngit push' }, play: true },
      { t: 'A new file is untracked (??) until you add it. Watch the short status codes change.', set: { cmds: 'new notes.txt\ngit add notes.txt\ngit commit -m "add notes"' }, play: true },
      { t: 'Undo at each level: restore --staged unstages, restore throws away your edit.', set: { cmds: 'edit README.md\ngit add README.md\ngit restore --staged README.md\ngit restore README.md' }, play: true },
      { t: 'The three resets. Make two commits, then reset --soft keeps the changes staged.', set: { cmds: 'edit app.py\ngit commit -am "one"\nedit app.py\ngit commit -am "two"\ngit reset --soft HEAD~1' }, play: true },
      { t: 'Same, with --mixed (the default): the changes stay in your file but are unstaged.', set: { cmds: 'edit app.py\ngit commit -am "one"\nedit app.py\ngit commit -am "two"\ngit reset HEAD~1' }, play: true },
      { t: 'And with --hard: the file itself goes back. Only the reflog remembers commit two.', set: { cmds: 'edit app.py\ngit commit -am "one"\nedit app.py\ngit commit -am "two"\ngit reset --hard HEAD~1' }, play: true },
      { t: 'Stash puts half done work away so you can switch tasks, and pop brings it back.', set: { cmds: 'edit app.py\ngit stash\nedit README.md\ngit commit -am "urgent fix"\ngit stash pop' }, play: true },
      { t: 'git rm --cached stops tracking a file but keeps it on your disk. Status shows D and ?? together.', set: { cmds: 'git rm --cached app.py' }, play: true }
    ],
    steps: z => String(z.p.cmds).split('\n').filter(l => l.trim() && !l.trim().startsWith('#')).length,
    draw(z) {
      const g = z.g, { S, log, snap } = areasRun(z.p.cmds, z.step), remote = S.commits[Math.min(S.remote, S.commits.length - 1)].snap;
      const names = [['Working tree', 'your folder', S.wt, z.col.orange], ['Staging area', 'the index', S.ix, z.col.green], ['Local repository', `HEAD = commit ${S.head + 1} of ${S.commits.length}`, snap, z.col.cv], ['Remote', `origin/main = commit ${S.remote + 1}`, remote, z.col.purple]];
      const bw = (z.W - 50) / 4;
      names.forEach(([t, s, files, c], k) => {
        const x = 10 + k * (bw + 10);
        panel(g, z, x, 34, bw, 170, t, c);
        D.text(g, fitText(g, s, bw - 10, { s: 11 }), x + bw / 2, 72, { a: 'center', s: 11, c: z.col.ink2 });
        Object.keys(files).sort().forEach((f, i) => {
          const v = files[f], diff = (k === 0 && S.ix[f] !== v) || (k === 1 && snap[f] !== v) || (k === 3 && snap[f] !== v);
          rr(g, x + 8, 84 + i * 26, bw - 16, 22, 6, { fill: diff ? 'rgba(245,158,11,.25)' : z.col.bg, stroke: diff ? z.col.orange : z.col.line, w: 1 });
          D.text(g, fitText(g, `${f}  v${v}`, bw - 26, { s: 11, mono: true }), x + 14, 99 + i * 26, { s: 11, mono: true, c: z.col.ink });
        });
        if (k < 3) D.arrow(g, x + bw + 1, 22, x + bw + 9, 22, z.col.ink2, 1.5, 5);
      });
      D.text(g, 'git add', 10 + bw + 5, 14, { a: 'center', s: 10, c: z.col.ink2, mono: true });
      D.text(g, 'git commit', 10 + 2 * bw + 15, 14, { a: 'center', s: 10, c: z.col.ink2, mono: true });
      D.text(g, 'git push', 10 + 3 * bw + 25, 14, { a: 'center', s: 10, c: z.col.ink2, mono: true });
      if (S.stash.length) tag(g, `stash: ${S.stash.length} entr${S.stash.length > 1 ? 'ies' : 'y'}`, 10 + bw / 2, 224, { s: 11, fill: z.col.surf, stroke: z.col.orange, c: z.col.ink });
      D.text(g, 'Orange boxes differ from the next place to the right, so that place does not have this version yet.', 10, 262, { s: 11, c: z.col.ink2 });
      const last = log[log.length - 1], st = shortStatus(S, snap);
      return (last ? `<p><b>Step ${log.length}:</b> <code>${esc(last.l)}</code>: <span class="${last.ok ? '' : 'gk-bad'}">${esc(last.out)}</span></p>` : '<p>Press Play or Step.</p>') +
        `<p><b>git status --short</b> (left letter: staged change, right letter: unstaged change)</p><pre>${esc(st.join('\n') || '(clean: nothing to commit, working tree clean)')}</pre>`;
    }
  });

  /* ---------- .gitignore rules ---------- */
  function globRe(p) {
    let r = '', i = 0;
    while (i < p.length) {
      const c = p[i];
      if (c === '*') {
        if (p[i + 1] === '*') {
          const before = i === 0 || p[i - 1] === '/', after = p[i + 2] === '/' || i + 2 === p.length;
          if (before && after) { if (p[i + 2] === '/') { r += '(?:.*/)?'; i += 3; } else { r += '.*'; i += 2; } continue; }
        }
        r += '[^/]*'; i++; continue;
      }
      if (c === '?') { r += '[^/]'; i++; continue; }
      if (c === '[') { const j = p.indexOf(']', i + 1); if (j > i) { r += '[' + p.slice(i + 1, j).replace(/^!/, '^') + ']'; i = j + 1; continue; } }
      r += c.replace(/[.+^${}()|\\]/g, '\\$&'); i++;
    }
    return r;
  }
  function ignoreRules(text) {
    return String(text).split('\n').map((raw, n) => ({ raw: raw.replace(/\s+$/, ''), n: n + 1 })).filter(x => x.raw && !x.raw.startsWith('#')).map(x => {
      let p = x.raw, neg = false, dir = false;
      if (p.startsWith('!')) { neg = true; p = p.slice(1); } else if (p.startsWith('\\')) p = p.slice(1);
      if (p.endsWith('/')) { dir = true; p = p.slice(0, -1); }
      const anchored = p.includes('/');
      if (p.startsWith('/')) p = p.slice(1);
      const re = new RegExp('^' + (anchored ? '' : '(?:.*/)?') + globRe(p) + '$');
      return { raw: x.raw, n: x.n, neg, dir, re };
    });
  }
  function ignored(rules, path) {
    const isDir = path.endsWith('/'), clean = path.replace(/\/$/, ''), parts = clean.split('/');
    for (let k = 1; k < parts.length; k++) {
      const d = parts.slice(0, k).join('/'); let hit = null;
      rules.forEach(r => { if (r.re.test(d)) hit = r; });
      if (hit && !hit.neg) return { ig: true, by: hit, parent: d };
    }
    let hit = null;
    rules.forEach(r => { if (r.dir && !isDir) return; if (r.re.test(clean)) hit = r; });
    return { ig: !!(hit && !hit.neg), by: hit };
  }
  def('ignore', {
    title: '.gitignore pattern tester',
    sub: 'Rules are read from top to bottom and the last rule that matches wins. A file inside an ignored folder cannot be brought back with !.',
    W: 640, H: 250,
    params: [
      { k: 'rules', label: '.gitignore', type: 'area', v: '# build output\ndist/\n*.log\n!keep.log\n/secret.env\n**/__pycache__/' },
      { k: 'paths', label: 'Paths to test (end a folder with /)', type: 'area', v: 'dist/app.zip\nserver.log\nkeep.log\nlogs/keep.log\nsecret.env\nconfig/secret.env\nsrc/__pycache__/x.pyc\napp.py' }
    ],
    tips: [
      { t: 'A leading slash anchors a rule to the folder of the .gitignore. /secret.env ignores the top one only.', set: { rules: '/secret.env', paths: 'secret.env\nconfig/secret.env' } },
      { t: 'Without any slash a rule matches at every depth.', set: { rules: 'secret.env', paths: 'secret.env\nconfig/secret.env\na/b/c/secret.env' } },
      { t: 'The parent folder trap: logs/ is ignored, so !logs/keep.log cannot bring the file back.', set: { rules: 'logs/\n!logs/keep.log', paths: 'logs/keep.log\nlogs/other.log' } },
      { t: 'The fix: ignore the contents instead of the folder, then re-include.', set: { rules: 'logs/*\n!logs/keep.log', paths: 'logs/keep.log\nlogs/other.log' } },
      { t: '** matches any number of folders: docs/**/*.pdf.', set: { rules: 'docs/**/*.pdf', paths: 'docs/a.pdf\ndocs/2026/q1/report.pdf\nother/docs/a.pdf' } }
    ],
    draw(z) {
      const g = z.g, rules = ignoreRules(z.p.rules), paths = String(z.p.paths).split('\n').map(s => s.trim()).filter(Boolean);
      const lh = Math.min(26, (z.H - 20) / Math.max(1, paths.length)), rows = [];
      paths.forEach((p, i) => {
        const r = ignored(rules, p), y = 10 + i * lh;
        rr(g, 10, y, z.W - 20, lh - 4, 6, { fill: r.ig ? 'rgba(239,68,68,.15)' : 'rgba(34,197,94,.15)' });
        D.text(g, fitText(g, p, 250, { s: 12, mono: true }), 20, y + lh / 2, { bl: 'middle', s: Math.min(12, lh - 8), mono: true, c: z.col.ink });
        const why = r.ig ? (r.parent ? `ignored, its folder ${r.parent}/ matches line ${r.by.n}` : `ignored by line ${r.by.n}: ${r.by.raw}`) : r.by ? `tracked, line ${r.by.n} (${r.by.raw}) re-includes it` : 'tracked, no rule matches';
        D.text(g, fitText(g, why, z.W - 300, { s: 11 }), 280, y + lh / 2, { bl: 'middle', s: Math.min(11, lh - 8), b: true, c: r.ig ? z.col.red : z.col.green });
        rows.push(`${r.ig ? '!!' : '  '} ${p}`);
      });
      return `<p>Check one path in a real repository with <code>git check-ignore -v &lt;path&gt;</code>. It prints the file, line and rule that decided.</p>`;
    }
  });

  /* ---------- local and remote: fetch, pull, push ---------- */
  def('remotes', {
    title: 'Your clone and origin: fetch, pull and push',
    sub: 'Top row: the server. Bottom row: your clone. origin/main is your clone\'s memory of where the server\'s main was at the last fetch.',
    W: 660, H: 270,
    params: [
      { k: 'mine', label: 'Commits you made locally', type: 'range', v: 2, min: 0, max: 3 },
      { k: 'theirs', label: 'Commits a teammate pushed to the server', type: 'range', v: 1, min: 0, max: 3 },
      { k: 'act', label: 'What you run', type: 'select', v: 'push', opts: [['status', 'git status (after git fetch)'], ['fetch', 'git fetch'], ['push', 'git push'], ['pull', 'git pull (merge)'], ['rebase', 'git pull --rebase'], ['ffonly', 'git pull --ff-only'], ['force', 'git push --force'], ['lease', 'git push --force-with-lease'], ['lease2', 'git push --force-with-lease (after a fetch)']] }
    ],
    tips: [
      { t: 'Both sides have new commits, so a plain push is rejected. Git asks you to integrate first.', set: { mine: 2, theirs: 1, act: 'push' } },
      { t: 'git pull merges: one merge commit joins the two lines.', set: { mine: 2, theirs: 1, act: 'pull' } },
      { t: 'git pull --rebase replays your commits on top of the teammate\'s, so history stays a straight line.', set: { mine: 2, theirs: 1, act: 'rebase' } },
      { t: 'git push --force overwrites the server and the teammate\'s commit is lost from main. Never do this on a shared branch.', set: { mine: 2, theirs: 1, act: 'force' } },
      { t: '--force-with-lease refuses because origin/main is out of date: you have not seen the teammate\'s work yet.', set: { mine: 2, theirs: 1, act: 'lease' } },
      { t: 'Only you changed things: push is a simple fast-forward on the server.', set: { mine: 2, theirs: 0, act: 'push' } },
      { t: 'Only the teammate changed things: --ff-only pull just moves your main forward.', set: { mine: 0, theirs: 2, act: 'ffonly' } }
    ],
    draw(z) {
      const g = z.g, m = z.p.mine, t = z.p.theirs, act = z.p.act;
      const base = ['A', 'B'], L = [...base, ...Array.from({ length: m }, (_, i) => 'L' + (i + 1))], S = [...base, ...Array.from({ length: t }, (_, i) => 'T' + (i + 1))];
      let srv = S.slice(), loc = L.slice(), track = act === 'status' || act === 'fetch' || act === 'lease2' ? S.slice() : base.slice(), merged = false, msg = '', ok = true, rebased = false;
      const diverged = m > 0 && t > 0;
      if (act === 'status') msg = `Your branch ${diverged ? `and 'origin/main' have diverged, and have ${m} and ${t} different commits each` : m ? `is ahead of 'origin/main' by ${m} commit${m > 1 ? 's' : ''}` : t ? `is behind 'origin/main' by ${t} commit${t > 1 ? 's' : ''}, and can be fast-forwarded` : `is up to date with 'origin/main'`}.`;
      if (act === 'fetch') msg = `fetch downloaded ${t} commit${t === 1 ? '' : 's'} and moved origin/main. Your main and your files did not change.`;
      if (act === 'push') { if (t > 0 && m > 0) { ok = false; msg = '! [rejected] main -> main (fetch first). Updates were rejected because the remote contains work that you do not have locally. Integrate the remote changes (git pull) before pushing again.'; } else if (m) { srv = loc.slice(); track = loc.slice(); msg = `${base[1]}..L${m}  main -> main. The server moved forward, no one lost anything.`; } else msg = 'Everything up-to-date'; }
      if (act === 'pull') { track = S.slice(); if (diverged) { loc = [...L, 'M']; merged = true; msg = 'Merge made by the \'ort\' strategy. A merge commit M joins both lines. Now git push works.'; } else { loc = m ? L : S.slice(); msg = m ? 'Already up to date.' : 'Fast-forward.'; } }
      if (act === 'rebase') { track = S.slice(); loc = [...S, ...Array.from({ length: m }, (_, i) => `L${i + 1}'`)]; rebased = m > 0 && t > 0; msg = rebased ? 'Successfully rebased and updated refs/heads/main. Your commits were copied on top of the teammate\'s (new ids with \').' : 'Fast-forward or nothing to do.'; }
      if (act === 'ffonly') { track = S.slice(); if (diverged) { ok = false; msg = 'fatal: Not possible to fast-forward, aborting. Use git pull --rebase or git pull --no-rebase.'; } else { loc = m ? L : S.slice(); msg = 'Fast-forward, main now matches origin/main.'; } }
      if (act === 'force') { srv = loc.slice(); track = loc.slice(); msg = t ? `+ ${S[S.length - 1]}...L${m || ''} main -> main (forced update). The teammate\'s commit${t > 1 ? 's' : ''} ${S.slice(2).join(', ')} no longer on main for anyone.` : 'forced update, but nothing was lost this time.'; ok = !t; }
      if (act === 'lease') { if (t) { ok = false; msg = '! [rejected] main -> main (stale info). origin/main says B, the server says ' + S[S.length - 1] + '. Someone pushed after your last fetch, so the lease protects their work.'; } else { srv = loc.slice(); track = loc.slice(); msg = 'Lease held (server still at B), push done.'; } }
      if (act === 'lease2') { srv = loc.slice(); track = loc.slice(); ok = !t; msg = t ? 'You fetched, so origin/main already showed T commits, and the lease holds. The push goes through and still wipes them. A lease only checks what you have seen, so look at git log origin/main first.' : 'Lease held, push done.'; }
      const row = (list, y, label, extra) => {
        D.text(g, label, 12, y + 4, { s: 12, b: true, c: z.col.ink2 });
        list.forEach((c, i) => {
          const x = 130 + i * 70, mine = c[0] === 'L', mg = c === 'M';
          if (i) D.arrow(g, x - 16, y, x - 54, y, z.col.ink2, 1.5, 6);
          D.circle(g, x, y, 15, { fill: mg ? z.col.purple : mine ? z.col.cv : c[0] === 'T' ? z.col.teal : z.col.ink2 });
          D.text(g, c, x, y + 1, { a: 'center', bl: 'middle', s: 11, b: true, c: '#fff' });
        });
        if (extra) extra();
      };
      row(srv, 60, 'origin (server)');
      row(loc, 170, 'your clone');
      const tipX = list => 130 + (list.length - 1) * 70;
      tag(g, 'main', tipX(srv), 30, { s: 11, fill: z.col.surf, stroke: z.col.purple, c: z.col.ink });
      tag(g, 'HEAD → main', tipX(loc), 140, { s: 11, fill: z.col.yellow, stroke: z.col.cv, c: '#3b2a00' });
      const tx = 130 + (track.length - 1) * 70;
      tag(g, 'origin/main', tx, 206, { s: 11, fill: z.col.surf, stroke: z.col.purple, c: z.col.ink });
      if (merged) D.text(g, 'M has two parents: L' + m + ' and ' + S[S.length - 1], 130, 240, { s: 11, c: z.col.ink2 });
      if (rebased) D.text(g, 'Old L commits are replaced by copies with new ids', 130, 240, { s: 11, c: z.col.ink2 });
      return `<p class="${ok ? 'gk-ok' : 'gk-bad'}">${esc(msg)}</p><p>Ahead and behind: your main has ${m} commit${m === 1 ? '' : 's'} origin/main lacks and lacks ${t} it has (count them with <code>git rev-list --left-right --count main...origin/main</code> after a fetch).</p>`;
    }
  });

  /* ---------- git bisect ---------- */
  def('bisect', {
    title: 'git bisect: binary search for the commit that broke things',
    sub: 'Green commits are good, red are bad. Each test halves the suspects, so n commits need about log₂ n tests.',
    W: 660, H: 210,
    params: [
      { k: 'n', label: 'Commits between the good and the bad one', type: 'range', v: 32, min: 4, max: 64 },
      { k: 'bad', label: 'The commit that really broke it (a secret Git does not know)', type: 'range', v: 21, min: 1, max: 64 }
    ],
    tips: [
      { t: '32 commits need at most 5 tests, because 2⁵ = 32.', set: { n: 32, bad: 21 }, play: true },
      { t: '64 commits need only 6 tests. Doubling the history adds one test.', set: { n: 64, bad: 50 }, play: true },
      { t: 'The bug was in the very first commit after the good one.', set: { n: 16, bad: 1 }, play: true }
    ],
    startAtZero: true,
    steps(z) { let lo = 0, hi = Math.min(z.p.bad, z.p.n) >= 1 ? z.p.n : z.p.n, k = 0; const b = Math.min(z.p.bad, z.p.n); while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (mid >= b) hi = mid; else lo = mid; k++; } return k; },
    draw(z) {
      const g = z.g, n = z.p.n, b = Math.min(z.p.bad, n), W = (z.W - 40) / (n + 1);
      let lo = 0, hi = n; const tested = [];
      for (let s = 0; s < z.step && hi - lo > 1; s++) { const mid = (lo + hi) >> 1; const bad = mid >= b; tested.push([mid, bad]); if (bad) hi = mid; else lo = mid; }
      for (let i = 0; i <= n; i++) {
        const x = 20 + i * W, out = i < lo || i > hi;
        const c = i === 0 ? z.col.green : i === n ? z.col.red : i <= lo ? 'rgba(34,197,94,.55)' : i >= hi ? 'rgba(239,68,68,.55)' : z.col.bg;
        rr(g, x + 1, 70, Math.max(2, W - 2), 40, 3, { fill: c, stroke: out ? null : z.col.line, w: 1 });
      }
      const rows = [[], [], []];   /* up to three label rows, each label goes in the first row where it does not touch another */
      tested.forEach(([m, bad], k) => {
        const x = 20 + m * W + W / 2, lw = tw(g, `test ${k + 1}`, { s: 10, b: true }) + 6;
        let r = rows.findIndex(row => row.every(px => Math.abs(px - x) > lw));
        if (r < 0) r = k % 3;
        rows[r].push(x);
        D.arrow(g, x, 46 - r * 14, x, 68, bad ? z.col.red : z.col.green, 2, 6);
        D.text(g, `test ${k + 1}`, x, 40 - r * 14, { a: 'center', s: 10, b: true, c: bad ? z.col.red : z.col.green });
      });
      D.text(g, 'good (v1.0)', 20, 130, { s: 11, c: z.col.green, b: true });
      D.text(g, 'bad (HEAD)', z.W - 20, 130, { a: 'right', s: 11, c: z.col.red, b: true });
      D.text(g, `Suspects left: ${hi - lo}  (commits ${lo + 1} to ${hi})`, 20, 160, { s: 13, b: true, c: z.col.ink });
      D.text(g, `Tests so far: ${tested.length}. At most ⌈log₂ ${n}⌉ = ${Math.ceil(Math.log2(n))} tests are needed.`, 20, 184, { s: 12, c: z.col.ink2 });
      const done = hi - lo === 1 && tested.length === z.n;
      return done ? `<p class="gk-ok">Commit ${hi} is the first bad commit. Git prints "${hi} is the first bad commit" and you run git bisect reset.</p>` : '<p>Each step Git checks out the middle commit. You test it and type <code>git bisect good</code> or <code>git bisect bad</code>, or let <code>git bisect run ./test.sh</code> do it for you.</p>';
    }
  });

  /* ---------- objects and their ids ---------- */
  def('hashobj', {
    title: 'How Git names an object: header + content, then a hash',
    sub: 'Git adds "type size" and a zero byte in front of the content and hashes the bytes. The same content always gets the same id.',
    W: 640, H: 220,
    params: [
      { k: 'type', label: 'Object type', type: 'select', v: 'blob', opts: [['blob', 'blob (file content)'], ['commit', 'commit'], ['tag', 'tag (annotated)']] },
      { k: 'body', label: 'Content (a file ends with a newline, so press Enter at the end)', type: 'area', v: 'hello\n' },
      { k: 'algo', label: 'Hash', type: 'select', v: 'sha1', opts: [['sha1', 'SHA-1 (40 hex digits, the default today)'], ['sha256', 'SHA-256 (64 hex digits, git init --object-format=sha256)']] }
    ],
    tips: [
      { t: 'The classic: hello plus a newline is ce013625... in every Git repository in the world.', set: { type: 'blob', body: 'hello\n', algo: 'sha1' } },
      { t: 'Remove the newline. One byte changes, so the whole id changes.', set: { type: 'blob', body: 'hello', algo: 'sha1' } },
      { t: 'The empty file has a famous id too: e69de29b...', set: { type: 'blob', body: '', algo: 'sha1' } },
      { t: 'A commit is just text too: a tree line, parents, author, committer, a blank line and the message.', set: { type: 'commit', body: 'tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904\nauthor Asha <asha@example.com> 1700000000 +0530\ncommitter Asha <asha@example.com> 1700000000 +0530\n\nempty start\n', algo: 'sha1' } },
      { t: 'Switch to SHA-256: same idea, longer id. New repositories will default to it in Git 3.0.', set: { algo: 'sha256', type: 'blob', body: 'hello\n' } }
    ],
    draw(z) {
      const g = z.g, body = String(z.p.body), bytes = enc(body), id = oid(z.p.type, body, z.p.algo);
      const head = `${z.p.type} ${bytes.length}\\0`;
      rr(g, 12, 16, 200, 46, 8, { fill: 'rgba(245,158,11,.2)', stroke: z.col.orange });
      D.text(g, 'header', 112, 32, { a: 'center', s: 11, c: z.col.ink2 });
      D.text(g, head, 112, 52, { a: 'center', s: 13, b: true, mono: true, c: z.col.ink });
      rr(g, 220, 16, z.W - 232, 46, 8, { fill: z.col.bg, stroke: z.col.line });
      D.text(g, `content: ${bytes.length} bytes`, 220 + (z.W - 232) / 2, 32, { a: 'center', s: 11, c: z.col.ink2 });
      D.text(g, fitText(g, JSON.stringify(body).slice(1, -1), z.W - 250, { s: 12, mono: true }), 220 + (z.W - 232) / 2, 52, { a: 'center', s: 12, mono: true, c: z.col.ink });
      D.arrow(g, z.W / 2, 68, z.W / 2, 96, z.col.cv, 2.5, 8);
      D.text(g, z.p.algo === 'sha1' ? 'SHA-1' : 'SHA-256', z.W / 2 + 10, 86, { s: 12, b: true, c: z.col.cv });
      rr(g, 12, 102, z.W - 24, 34, 8, { fill: z.col.cv });
      D.text(g, fitText(g, id, z.W - 40, { s: 13, mono: true, b: true }), z.W / 2, 124, { a: 'center', s: z.p.algo === 'sha1' ? 13 : 10, mono: true, b: true, c: '#fff' });
      D.text(g, 'stored as (zlib compressed)', 12, 164, { s: 11, c: z.col.ink2 });
      D.text(g, fitText(g, `.git/objects/${id.slice(0, 2)}/${id.slice(2)}`, z.W - 24, { s: 12, mono: true }), 12, 184, { s: z.p.algo === 'sha1' ? 12 : 10, mono: true, b: true, c: z.col.ink });
      D.text(g, `short form you usually type: ${id.slice(0, 7)}`, 12, 206, { s: 11, c: z.col.ink2 });
      return `<p>Check it in a terminal: <code>printf ${esc(JSON.stringify(body).replace(/^"|"$/g, "'"))} | git hash-object ${z.p.type === 'blob' ? '' : '-t ' + z.p.type + ' '}--stdin</code>. The first two hex digits become a folder so no folder holds too many files.</p>`;
    }
  });

  /* ---------- commit, tree and blob graph with real ids ---------- */
  function objRepo(nc, edit) {
    const blobs = { readme1: oid('blob', '# Shop\n'), app1: oid('blob', 'print("hi")\n'), readme2: oid('blob', '# Shop\nNow with search\n'), util: oid('blob', 'def add(a, b):\n    return a + b\n') };
    const commits = [];
    const mk = (entries, parent, msg, t) => {
      const tree = oid('tree', treeBytes(entries.map(e => [e[0], e[1], e[2]])));
      const text = `tree ${tree}\n${parent ? `parent ${parent}\n` : ''}author Asha <asha@example.com> ${t} +0530\ncommitter Asha <asha@example.com> ${t} +0530\n\n${msg}\n`;
      return { id: oid('commit', text), tree, entries, msg, parent };
    };
    const t1 = [['100644', 'README.md', blobs.readme1, '# Shop'], ['100644', 'app.py', blobs.app1, 'print("hi")']];
    commits.push(mk(t1, null, 'first', 1700000000));
    const t2 = [[ '100644', 'README.md', edit ? blobs.readme2 : blobs.readme1, edit ? '# Shop / Now with search' : '# Shop'], ['100644', 'app.py', blobs.app1, 'print("hi")']];
    if (nc > 1) commits.push(mk(t2, commits[0].id, 'update readme', 1700003600));
    if (nc > 2) {
      const sub = oid('tree', treeBytes([['100644', 'util.py', blobs.util]]));
      commits.push(mk([...t2, ['40000', 'lib', sub, 'tree: util.py']], commits[1].id, 'add lib', 1700007200));
      commits[2].sub = { id: sub, blob: blobs.util };
    }
    return commits;
  }
  def('objgraph', {
    title: 'Commits point to trees, trees point to blobs',
    sub: 'The ids are real SHA-1 values worked out on this page. An unchanged file keeps its blob id, so Git stores it once and points to it again.',
    W: 660, H: 330,
    params: [
      { k: 'nc', label: 'Commits', type: 'range', v: 2, min: 1, max: 3 },
      { k: 'edit', label: 'Commit 2 changes README.md', type: 'check', v: true }
    ],
    tips: [
      { t: 'One commit: one tree, two blobs. Three objects plus the commit.', set: { nc: 1 } },
      { t: 'Commit 2 changes only README.md. The new tree points at the old app.py blob. Count the new objects: commit, tree, one blob.', set: { nc: 2, edit: true } },
      { t: 'Untick the change: commit 2 then has the very same tree id as commit 1, because the content is identical.', set: { nc: 2, edit: false } },
      { t: 'Commit 3 adds a folder. A folder is a tree inside the tree.', set: { nc: 3, edit: true } }
    ],
    draw(z) {
      const g = z.g, cs = objRepo(z.p.nc, z.p.edit), colX = k => 20 + k * 215;
      const blobPos = {}; let by = 250;
      const put = (id, label) => { if (!blobPos[id]) { const n = Object.keys(blobPos).length; blobPos[id] = [20 + n * 160, by, label]; } return blobPos[id]; };
      cs.forEach((c, k) => {
        const x = colX(k);
        rr(g, x, 20, 190, 46, 8, { fill: z.col.cv });
        D.text(g, `commit ${c.id.slice(0, 7)}`, x + 95, 38, { a: 'center', s: 12, b: true, mono: true, c: '#fff' });
        D.text(g, fitText(g, `"${c.msg}"`, 180, { s: 11 }), x + 95, 56, { a: 'center', s: 11, c: '#fff' });
        if (k) D.arrow(g, x, 43, colX(k - 1) + 190, 43, z.col.ink2, 2, 7);
        rr(g, x + 20, 112, 150, 40, 8, { fill: z.col.green });
        D.text(g, `tree ${c.tree.slice(0, 7)}`, x + 95, 137, { a: 'center', s: 12, b: true, mono: true, c: '#fff' });
        D.arrow(g, x + 95, 66, x + 95, 110, z.col.green, 2, 7);
      });
      cs.forEach((c, k) => {
        const x = colX(k);
        c.entries.forEach(e => {
          const p = put(e[2], e[0] === '40000' ? 'tree lib/' : e[1]);
          D.arrow(g, x + 95, 152, p[0] + 70, p[1] - 2, e[0] === '40000' ? z.col.green : z.col.orange, 1.5, 6);
        });
      });
      Object.entries(blobPos).forEach(([id, [x, y, label]]) => {
        const isTree = label.startsWith('tree');
        rr(g, x, y, 140, 40, 8, { fill: isTree ? z.col.green : z.col.orange });
        D.text(g, `${isTree ? 'tree' : 'blob'} ${id.slice(0, 7)}`, x + 70, y + 17, { a: 'center', s: 11, b: true, mono: true, c: '#fff' });
        D.text(g, fitText(g, label, 130, { s: 10 }), x + 70, y + 32, { a: 'center', s: 10, c: '#fff' });
      });
      D.text(g, 'blobs (file contents)', 20, 236, { s: 11, b: true, c: z.col.ink2 });
      const nObj = new Set(cs.flatMap(c => [c.id, c.tree, ...c.entries.map(e => e[2])].concat(c.sub ? [c.sub.blob] : []))).size;
      return `<p>${cs.length} commit${cs.length > 1 ? 's' : ''}, ${nObj} different objects in .git/objects. ${cs.length > 1 && cs[1].tree === cs[0].tree ? 'Commits 1 and 2 share one tree object because their snapshots are identical.' : ''}</p><pre>${esc(cs.map(c => `commit ${c.id}\n  tree ${c.tree}\n` + c.entries.map(e => `    ${e[0] === '40000' ? '040000 tree' : '100644 blob'} ${e[2].slice(0, 12)}…  ${e[1]}`).join('\n')).join('\n'))}</pre>`;
    }
  });

  /* ---------- plumbing: make a commit by hand ---------- */
  const PLUMB = [
    ['echo "hello" > hello.txt', 'Only your folder changes. Git knows nothing yet.', {}],
    ['git hash-object -w hello.txt', 'Writes a blob into .git/objects and prints its id ce01362.', { blob: 1 }],
    ['git update-index --add --cacheinfo 100644,ce01362...,hello.txt', 'Puts a line for hello.txt into the index (.git/index). This is what git add does.', { blob: 1, index: 1 }],
    ['git write-tree', 'Turns the index into a tree object and prints its id.', { blob: 1, index: 1, tree: 1 }],
    ['git commit-tree <tree> -m "first"', 'Makes a commit object that points at the tree. It has no parent because it is the first.', { blob: 1, index: 1, tree: 1, commit: 1 }],
    ['git update-ref refs/heads/main <commit>', 'Writes the commit id into .git/refs/heads/main. Now the branch exists.', { blob: 1, index: 1, tree: 1, commit: 1, ref: 1 }],
    ['cat .git/HEAD', 'HEAD holds "ref: refs/heads/main", a pointer to the branch. git log now shows your commit.', { blob: 1, index: 1, tree: 1, commit: 1, ref: 1, head: 1 }]
  ];
  def('plumbing', {
    title: 'git add and git commit, done by hand with plumbing commands',
    sub: 'Porcelain commands like add and commit are made of these smaller plumbing steps. Step through and watch .git fill up.',
    W: 660, H: 250,
    params: [{ k: 'notes', label: 'Show what each box holds', type: 'check', v: true }],
    tips: [{ t: 'Play it from the start and watch which box each step fills.', set: { notes: true }, play: true }],
    startAtZero: true,
    steps: () => PLUMB.length,
    draw(z) {
      const g = z.g, st = z.step ? PLUMB[z.step - 1][2] : {};
      const boxes = [['objects', 20, 30, 300, 150, z.col.cv], ['index', 340, 30, 140, 70, z.col.green], ['refs/heads/main', 500, 30, 140, 70, z.col.purple], ['HEAD', 500, 120, 140, 60, z.col.yellow]];
      boxes.forEach(([t, x, y, w, h, c]) => panel(g, z, x, y, w, h, t === 'objects' ? '.git/objects' : t === 'index' ? '.git/index' : '.git/' + t, c));
      const obj = [];
      if (st.blob) obj.push(['blob ce01362', 'hello']);
      if (st.tree) obj.push(['tree aaa96ce', '100644 blob ce01362 hello.txt']);
      if (st.commit) obj.push(['commit (new id)', 'tree aaa96ce, message first']);
      obj.forEach(([a, b], i) => { rr(g, 30, 62 + i * 38, 280, 32, 6, { fill: z.col.bg }); D.text(g, a, 40, 76 + i * 38, { s: 12, b: true, mono: true, c: z.col.ink }); if (z.p.notes) D.text(g, fitText(g, b, 260, { s: 10 }), 40, 89 + i * 38, { s: 10, c: z.col.ink2 }); });
      if (st.index) D.text(g, 'hello.txt ce01362', 410, 72, { a: 'center', s: 11, mono: true, c: z.col.ink });
      if (st.ref) D.text(g, '<commit id>', 570, 72, { a: 'center', s: 11, mono: true, c: z.col.ink });
      if (st.head) D.text(g, 'ref: refs/heads/main', 570, 160, { a: 'center', s: 10, mono: true, c: z.col.ink });
      if (z.step) { rr(g, 20, 196, z.W - 40, 40, 8, { fill: z.col.surf, stroke: z.col.line }); D.text(g, fitText(g, '$ ' + PLUMB[z.step - 1][0], z.W - 60, { s: 12, mono: true }), 30, 221, { s: 12, mono: true, b: true, c: z.col.ink }); }
      return z.step ? `<p>${esc(PLUMB[z.step - 1][1])}</p>` : '<p>Press Play or Step. Before step 1, .git is a fresh empty repository from git init.</p>';
    }
  });

  /* ---------- branching workflows ---------- */
  const FLOWS = {
    github: { name: 'GitHub flow', lanes: ['main', 'feature/login'], ev: [[0, 0, 'deployable'], [1, 1, 'branch'], [1, 2, 'commit'], [1, 3, 'pull request + CI'], [1, 4, 'review fixes'], [0, 5, 'merge, deploy']], note: 'One long lived branch, main, always deployable. Short feature branches go through a pull request with CI and review, then merge and deploy.' },
    gitflow: { name: 'Gitflow', lanes: ['main', 'hotfix', 'release/1.2', 'develop', 'feature/x'], ev: [[0, 0, 'v1.1'], [3, 1, 'develop'], [4, 2, 'feature'], [4, 3, 'commit'], [3, 4, 'merge feature'], [2, 5, 'release branch'], [2, 6, 'fix'], [0, 7, 'v1.2 tag'], [3, 7, 'back to develop'], [1, 8, 'hotfix'], [0, 9, 'v1.2.1']], note: 'Two long lived branches: main holds releases, develop holds the next release. Feature, release and hotfix branches have strict rules. Suits versioned products with scheduled releases.' },
    trunk: { name: 'Trunk based', lanes: ['main (trunk)', 'tiny branch'], ev: [[0, 0, 'commit'], [1, 1, 'hours old'], [0, 2, 'merge'], [0, 3, 'commit'], [1, 4, 'tiny'], [0, 5, 'merge'], [0, 6, 'release from trunk']], note: 'Everyone merges small changes into main at least daily. Unfinished features hide behind feature flags. Needs strong automated tests in CI.' },
    fork: { name: 'Forking workflow', lanes: ['upstream main', 'your fork main', 'your fork feature'], ev: [[0, 0, 'project'], [1, 1, 'fork'], [2, 2, 'branch'], [2, 3, 'commits'], [0, 4, 'pull request merged'], [1, 5, 'sync fork']], note: 'You cannot push to the project, so you push to your own copy (fork) and open a pull request upstream. Common in open source.' }
  };
  def('flows', {
    title: 'Branching workflows side by side',
    sub: 'Each row is a branch, time runs to the right. Step through to see the order of events.',
    W: 660, H: 280,
    params: [{ k: 'f', label: 'Workflow', type: 'select', v: 'github', opts: Object.keys(FLOWS).map(k => [k, FLOWS[k].name]) }],
    tips: Object.keys(FLOWS).map(k => ({ t: `Play ${FLOWS[k].name}.`, set: { f: k }, play: true })),
    steps: z => FLOWS[z.p.f].ev.length,
    draw(z) {
      const g = z.g, F = FLOWS[z.p.f], n = F.lanes.length, dy = Math.min(50, 220 / n), dx = (z.W - 170) / 10;
      F.lanes.forEach((l, i) => { const y = 30 + i * dy; D.text(g, fitText(g, l, 120, { s: 11, b: true }), 10, y + 4, { s: 11, b: true, c: z.col.ink2 }); D.line(g, 140, y, z.W - 10, y, z.col.line, 1, [3, 4]); });
      const ev = F.ev.slice(0, z.step);
      ev.forEach(([lane, t, label], k) => {
        const x = 150 + t * dx, y = 30 + lane * dy;
        if (k) { const [pl, pt] = ev[k - 1]; D.arrow(g, 150 + pt * dx + 8, 30 + pl * dy, x - 9, y, z.col.ink2, 1.5, 6); }
        D.circle(g, x, y, 8, { fill: z.col.cv });
        D.text(g, label, x, y + (k % 2 ? 22 : -14), { a: 'center', s: 10, b: true, c: z.col.ink });
      });
      return `<p><b>${F.name}.</b> ${F.note}</p>`;
    }
  });

  /* ---------- hooks ---------- */
  const HOOKS = [['pre-commit', 'client', 'before the message is asked for: lint, format, secret scan'], ['prepare-commit-msg', 'client', 'fill in a message template'], ['commit-msg', 'client', 'check the message, for example Conventional Commits'], ['post-commit', 'client', 'notify, cannot stop the commit'], ['pre-push', 'client', 'run fast tests before anything leaves your machine'], ['pre-receive', 'server', 'the server can refuse the whole push'], ['update', 'server', 'runs once per branch being pushed'], ['post-receive', 'server', 'start CI, send emails, deploy']];
  def('hooks', {
    title: 'Where Git hooks run during commit and push',
    sub: 'A hook is a script in .git/hooks (or core.hooksPath). If a pre hook exits with a non zero code, Git stops right there.',
    W: 660, H: 240,
    params: [{ k: 'fail', label: 'Make this hook exit with code 1', type: 'select', v: 'none', opts: [['none', 'none, all pass']].concat(HOOKS.filter(h => /^pre|commit-msg|update/.test(h[0])).map(h => [h[0], h[0]])) }],
    tips: [{ t: 'All pass: commit and push complete.', set: { fail: 'none' }, play: true }, { t: 'pre-commit fails: no commit is made, so nothing later runs.', set: { fail: 'pre-commit' }, play: true }, { t: 'commit-msg fails: the message was rejected, fix it and commit again.', set: { fail: 'commit-msg' }, play: true }, { t: 'pre-receive fails on the server: the commit exists locally but the push is refused.', set: { fail: 'pre-receive' }, play: true }],
    steps: () => HOOKS.length, startAtZero: true,
    draw(z) {
      const g = z.g, bw = (z.W - 30) / 4;
      let stopped = -1;
      HOOKS.forEach((h, i) => {
        const x = 10 + (i % 4) * (bw + 3), y = i < 4 ? 40 : 150, ran = i < z.step && (stopped < 0);
        if (ran && h[0] === z.p.fail) stopped = i;
        const isStop = i === stopped, skipped = stopped >= 0 && i > stopped && i < z.step;
        rr(g, x, y, bw - 4, 70, 8, { fill: isStop ? 'rgba(239,68,68,.25)' : ran ? 'rgba(34,197,94,.2)' : z.col.bg, stroke: h[1] === 'server' ? z.col.purple : z.col.cv, dash: skipped ? [4, 4] : null });
        D.text(g, h[0], x + (bw - 4) / 2, y + 20, { a: 'center', s: 12, b: true, mono: true, c: z.col.ink });
        wrap(g, h[2], x + 8, y + 38, bw - 20, { s: 10, c: z.col.ink2, lh: 13 });
      });
      D.text(g, 'git commit (your machine)', 10, 28, { s: 11, b: true, c: z.col.cv });
      D.text(g, 'git push: pre-push on your machine, then the server hooks', 10, 138, { s: 11, b: true, c: z.col.purple });
      return stopped >= 0 ? `<p class="gk-bad">${HOOKS[stopped][0]} exited with 1, so Git stopped. ${stopped < 4 ? 'No commit was created.' : stopped === 4 ? 'The commit exists, but nothing was sent.' : 'The server refused the push. Your local commit is still there.'}</p>` : z.step === HOOKS.length ? '<p class="gk-ok">Every hook passed. Note that git commit --no-verify skips pre-commit and commit-msg, so the server side and CI must check again.</p>' : '<p>Press Play.</p>';
    }
  });

  /* ---------- config levels ---------- */
  def('configlv', {
    title: 'Which git config value wins',
    sub: 'Git reads system, then global, then local settings. A later level overrides an earlier one, so the most specific wins.',
    W: 640, H: 200,
    params: [
      { k: 'sys', label: 'System (/etc/gitconfig) user.email', type: 'text', v: '' },
      { k: 'glob', label: 'Global (~/.gitconfig) user.email', type: 'text', v: 'asha@home.example' },
      { k: 'loc', label: 'Local (.git/config of this repo) user.email', type: 'text', v: 'asha@work.example' }
    ],
    tips: [{ t: 'Clear the local value: the global one is used in this repository.', set: { loc: '' } }, { t: 'Work repo trick: set your work email locally once, keep your personal email global.', set: { glob: 'asha@home.example', loc: 'asha@work.example' } }, { t: 'Clear everything: Git refuses to commit and asks you to set user.email.', set: { sys: '', glob: '', loc: '' } }],
    draw(z) {
      const g = z.g, L = [['system', '--system', z.p.sys], ['global', '--global', z.p.glob], ['local', '--local', z.p.loc]];
      let win = -1; L.forEach((l, i) => { if (l[2]) win = i; });
      L.forEach((l, i) => {
        const x = 20 + i * 205;
        rr(g, x, 30, 190, 80, 10, { fill: i === win ? 'rgba(34,197,94,.22)' : z.col.bg, stroke: i === win ? z.col.green : z.col.line, w: i === win ? 2.5 : 1.5 });
        D.text(g, `${l[0]} (${l[1]})`, x + 95, 54, { a: 'center', s: 12, b: true, c: z.col.ink });
        D.text(g, fitText(g, l[2] || '(not set)', 175, { s: 12, mono: true }), x + 95, 84, { a: 'center', s: 12, mono: true, c: l[2] ? z.col.ink : z.col.ink2 });
        if (i < 2) D.arrow(g, x + 192, 70, x + 203, 70, z.col.ink2, 1.5, 5);
      });
      D.text(g, 'read in this order, later wins →', 20, 20, { s: 11, c: z.col.ink2 });
      D.text(g, win >= 0 ? `git config user.email  →  ${L[win][2]}` : 'git config user.email  →  (nothing, exit code 1)', 20, 150, { s: 14, b: true, mono: true, c: win >= 0 ? z.col.green : z.col.red });
      return win >= 0 ? `<p>Commits in this repository are signed with <b>${esc(L[win][2])}</b>. Run <code>git config --show-origin user.email</code> to see which file it came from.</p>` : '<p class="gk-bad">Author identity unknown. Please tell me who you are: git config --global user.email "you@example.com"</p>';
    }
  });

  /* ---------- centralised and distributed version control ---------- */
  def('vcs', {
    title: 'Centralised and distributed version control',
    sub: 'With a central system only the server has the history. With Git every clone has all of it.',
    W: 640, H: 240,
    params: [{ k: 'kind', label: 'Model', type: 'select', v: 'dist', opts: [['central', 'Centralised (for example Subversion)'], ['dist', 'Distributed (Git)']] }, { k: 'down', label: 'The server is down', type: 'check', v: false }],
    tips: [{ t: 'Centralised with the server down: nobody can commit or read old versions.', set: { kind: 'central', down: true } }, { t: 'Git with the server down: everyone still commits, branches and reads history. They push later.', set: { kind: 'dist', down: true } }],
    draw(z) {
      const g = z.g, dist = z.p.kind === 'dist', down = z.p.down;
      rr(g, z.W / 2 - 90, 16, 180, 60, 10, { fill: down ? 'rgba(239,68,68,.2)' : z.col.bg, stroke: down ? z.col.red : z.col.cv, w: 2 });
      D.text(g, 'Server', z.W / 2, 38, { a: 'center', s: 13, b: true, c: z.col.ink });
      D.text(g, down ? 'offline' : 'full history', z.W / 2, 60, { a: 'center', s: 11, c: down ? z.col.red : z.col.ink2 });
      ['Asha', 'Ravi', 'Meera'].forEach((n, i) => {
        const x = 40 + i * 205, y = 140;
        D.line(g, z.W / 2, 76, x + 75, y, down ? z.col.red : z.col.line, 2, down ? [5, 5] : null);
        rr(g, x, y, 150, 76, 10, { fill: z.col.surf, stroke: z.col.line });
        D.text(g, n, x + 75, y + 20, { a: 'center', s: 13, b: true, c: z.col.ink });
        D.text(g, dist ? 'full history clone' : 'latest files only', x + 75, y + 40, { a: 'center', s: 11, c: z.col.ink2 });
        const can = dist || !down;
        D.text(g, can ? 'can commit, see log' : 'cannot commit or log', x + 75, y + 60, { a: 'center', s: 11, b: true, c: can ? z.col.green : z.col.red });
      });
      return dist ? '<p>Every clone is a full backup. Commit, branch, diff and log all work offline and are fast because they read your own disk.</p>' : '<p>Every commit and every look at history needs the server. One server failure stops the whole team.</p>';
    }
  });
})();

/* ===== part 3: CI/CD. Pipelines, triggers, matrices, caches, artifacts, GitLab rules and YAML ===== */
(() => {
  const { D, def, esc } = CVZ;
  const { tw, rr, tag, wrap, fitText, panel, sha1, enc, hex } = GITZ;

  /* ---------- a pipeline run over time ---------- */
  const PRESETS = {
    starter: { name: 'calc-app (the sample project)', stages: ['lint', 'test', 'build', 'qa'], jobs: [
      { n: 'lint', s: 0, d: 1, needs: [] }, { n: 'unit-tests', s: 1, d: 2, needs: ['lint'], makes: 'unit-report', always: 'upload' },
      { n: 'build', s: 2, d: 1, needs: ['unit-tests'], makes: 'calc-app.zip' }, { n: 'smoke-tests', s: 3, d: 2, needs: ['build'], uses: 'calc-app.zip', makes: 'smoke-report', always: 'upload' }] },
    dev: { name: 'Developer pipeline', stages: ['check', 'test', 'build', 'deploy'], jobs: [
      { n: 'lint', s: 0, d: 1, needs: [] }, { n: 'type-check', s: 0, d: 2, needs: [] }, { n: 'unit-tests', s: 1, d: 3, needs: ['lint'], makes: 'coverage' },
      { n: 'package', s: 2, d: 2, needs: ['unit-tests', 'type-check'], makes: 'app.zip' }, { n: 'deploy-dev', s: 3, d: 1, needs: ['package'], uses: 'app.zip' }] },
    qa: { name: 'QA pipeline', stages: ['build', 'test', 'report'], jobs: [
      { n: 'build', s: 0, d: 2, needs: [], makes: 'app.zip' }, { n: 'api-tests', s: 1, d: 3, needs: ['build'], uses: 'app.zip', makes: 'api-report' },
      { n: 'e2e shard 1/3', s: 1, d: 4, needs: ['build'], uses: 'app.zip', makes: 'e2e-1' }, { n: 'e2e shard 2/3', s: 1, d: 4, needs: ['build'], uses: 'app.zip', makes: 'e2e-2' },
      { n: 'e2e shard 3/3', s: 1, d: 5, needs: ['build'], uses: 'app.zip', makes: 'e2e-3' }, { n: 'test-report', s: 2, d: 1, needs: ['api-tests', 'e2e shard 1/3', 'e2e shard 2/3', 'e2e shard 3/3'], always: 'job', uses: 'all reports' }] },
    slow: { name: 'Why needs makes pipelines faster', stages: ['build', 'test', 'deploy'], jobs: [
      { n: 'build-web', s: 0, d: 1, needs: [] }, { n: 'build-docs', s: 0, d: 6, needs: [] }, { n: 'test-web', s: 1, d: 2, needs: ['build-web'] },
      { n: 'test-docs', s: 1, d: 1, needs: ['build-docs'] }, { n: 'deploy-web', s: 2, d: 1, needs: ['test-web'] }] }
  };
  function simulate(P, mode, fail) {
    const J = P.jobs.map(j => Object.assign({}, j, { st: 'pending', t0: null, t1: null })), by = Object.fromEntries(J.map(j => [j.n, j]));
    const deps = j => mode === 'dag' ? j.needs.map(n => by[n]) : J.filter(o => o.s < j.s);
    let t = 0;
    const frames = [];
    for (let guard = 0; guard < 60; guard++) {
      J.forEach(j => { if (j.st === 'running' && t >= j.t0 + j.d) { j.st = j.n === fail ? 'failed' : 'success'; j.t1 = j.t0 + j.d; } });
      let changed = true;
      while (changed) {
        changed = false;
        J.forEach(j => {
          if (j.st !== 'pending') return;
          const ds = deps(j);
          if (ds.some(d => d.st === 'pending' || d.st === 'running')) return;
          const bad = ds.some(d => d.st === 'failed' || d.st === 'skipped');
          if (bad && j.always !== 'job') { j.st = 'skipped'; j.t0 = j.t1 = t; changed = true; return; }
          j.st = 'running'; j.t0 = t; changed = true;
        });
      }
      frames.push({ t, J: J.map(j => Object.assign({}, j)) });
      if (J.every(j => j.st !== 'pending' && j.st !== 'running')) break;
      t++;
    }
    return frames;
  }
  def('pipeline', {
    title: 'A pipeline run, job by job',
    sub: 'Each bar is a job on its own fresh runner. A job starts when the jobs it waits for are done. Pick a job to fail and watch what gets skipped.',
    W: 660, H: 300,
    params: [
      { k: 'preset', label: 'Pipeline', type: 'select', v: 'starter', opts: Object.keys(PRESETS).map(k => [k, PRESETS[k].name]) },
      { k: 'plat', label: 'Platform words', type: 'select', v: 'gha', opts: [['gha', 'GitHub Actions'], ['gitlab', 'GitLab CI/CD']] },
      { k: 'mode', label: 'How jobs wait', type: 'select', v: 'dag', opts: [['dag', 'only for the jobs they need (needs)'], ['stages', 'for the whole previous stage (GitLab default)']] },
      { k: 'fail', label: 'Make this job fail', type: 'select', v: 'none', opts: [['none', 'none']].concat([...new Set(Object.values(PRESETS).flatMap(p => p.jobs.map(j => j.n)))].map(n => [n, n])) }
    ],
    tips: [
      { t: 'The sample project: lint, unit tests, build, then smoke tests on the built zip.', set: { preset: 'starter', fail: 'none', mode: 'dag' }, play: true },
      { t: 'Break the unit tests. Build and smoke tests are skipped, but the report still uploads because that step uses if: always() (when: always in GitLab).', set: { preset: 'starter', fail: 'unit-tests' }, play: true },
      { t: 'QA pipeline: three end to end shards run side by side after one build, and the report job runs even when a shard fails.', set: { preset: 'qa', fail: 'e2e shard 2/3', mode: 'dag' }, play: true },
      { t: 'Stage by stage, test-web waits for the slow build-docs. Count the time units.', set: { preset: 'slow', mode: 'stages', fail: 'none' }, play: true },
      { t: 'Now with needs: deploy-web finishes long before docs. Same jobs, shorter wait for the web team.', set: { preset: 'slow', mode: 'dag', fail: 'none' }, play: true }
    ],
    startAtZero: true,
    steps: z => simulate(PRESETS[z.p.preset], z.p.mode, z.p.fail).length - 1,
    draw(z) {
      const g = z.g, P = PRESETS[z.p.preset], frames = simulate(P, z.p.mode, z.p.fail), fr = frames[Math.min(z.step, frames.length - 1)], T = frames[frames.length - 1].t;
      const left = 130, unit = Math.min(60, (z.W - left - 20) / Math.max(1, T)), rowH = Math.min(36, (z.H - 60) / fr.J.length);
      for (let t = 0; t <= T; t++) { D.line(g, left + t * unit, 24, left + t * unit, 30 + fr.J.length * rowH, z.col.line, 1, [2, 4]); D.text(g, String(t), left + t * unit, 18, { a: 'center', s: 10, c: z.col.ink2 }); }
      D.text(g, 'time units →', left, 8, { s: 10, c: z.col.ink2 });
      const C = { success: z.col.green, failed: z.col.red, running: z.col.yellow, skipped: z.col.line, pending: z.col.bg };
      fr.J.forEach((j, i) => {
        const y = 30 + i * rowH;
        D.text(g, fitText(g, j.n, left - 14, { s: 11, b: true }), 8, y + rowH / 2, { bl: 'middle', s: 11, b: true, c: z.col.ink });
        if (j.st === 'pending') return;
        const t1 = j.st === 'running' ? fr.t : j.t1;
        const w = Math.max(j.st === 'skipped' ? 6 : 4, (t1 - j.t0) * unit);
        rr(g, left + j.t0 * unit, y + 4, w, rowH - 8, 5, { fill: C[j.st] });
        const lbl = j.st === 'skipped' ? 'skipped' : j.st === 'failed' ? 'failed' : j.st === 'running' ? 'running' : (j.makes ? '↑ ' + j.makes : 'passed');
        const lx = left + j.t0 * unit + w + 6;
        if (lx + tw(g, lbl, { s: 10, b: true }) > z.W - 4) D.text(g, lbl, lx - 12, y + rowH / 2, { a: 'right', bl: 'middle', s: 10, b: true, c: '#fff' });
        else D.text(g, lbl, lx, y + rowH / 2, { bl: 'middle', s: 10, b: true, c: j.st === 'failed' ? z.col.red : z.col.ink2 });
      });
      const done = z.step >= frames.length - 1;
      const sk = fr.J.filter(j => j.st === 'skipped').map(j => j.n), alw = P.jobs.filter(j => j.always);
      const wordAlways = z.p.plat === 'gha' ? 'if: always()' : 'when: always';
      const wordNeeds = z.p.plat === 'gha' ? 'needs:' : (z.p.mode === 'dag' ? 'needs:' : 'stages:');
      return `<p>${done ? `<b>Finished after ${T} time units.</b>` : `Time ${fr.t}.`} ${z.p.mode === 'dag' ? `Jobs wait only for what they list in <code>${wordNeeds}</code>.` : 'Each job waits for every job of the earlier stages.'} ${z.p.plat === 'gha' && z.p.mode === 'stages' ? 'In GitHub Actions jobs run side by side unless needs: chains them, so this mode is what you get by making each job need every job of the group before it.' : ''}</p>` +
        (sk.length ? `<p class="gk-warn">Skipped because something they wait for failed: ${esc(sk.join(', '))}.</p>` : '') +
        (alw.length ? `<p>${alw.map(j => `<b>${esc(j.n)}</b> ${j.always === 'upload' ? `uploads its report with ${wordAlways}, so the report survives a failure` : `has ${wordAlways}, so it runs even after a failure`}`).join('. ')}.</p>` : '') +
        `<p>Artifacts: ${P.jobs.filter(j => j.makes).map(j => `${esc(j.n)} uploads <b>${esc(j.makes)}</b>`).join(', ') || 'none'}${P.jobs.some(j => j.uses) ? '. ' + P.jobs.filter(j => j.uses).map(j => `${esc(j.n)} downloads ${esc(j.uses)}`).join(', ') : ''}.</p>`;
    }
  });

  /* ---------- GitHub Actions on: filters ---------- */
  function ghGlob(p) {
    let r = '';
    for (let i = 0; i < p.length; i++) {
      const c = p[i];
      if (c === '*') { if (p[i + 1] === '*') { r += '.*'; i++; } else r += '[^/]*'; }
      else if (c === '?' || c === '+') r += c;
      else if (c === '[') { const j = p.indexOf(']', i); r += p.slice(i, j + 1); i = j; }
      else r += c.replace(/[.^${}()|\\/]/g, '\\$&');
    }
    return new RegExp('^' + r + '$');
  }
  const list = s => String(s).split(/[\n,]/).map(x => x.trim()).filter(Boolean);
  function filterMatch(patterns, value) { let hit = false; patterns.forEach(p => { const neg = p.startsWith('!'); if (ghGlob(neg ? p.slice(1) : p).test(value)) hit = !neg; }); return hit; }
  def('trigger', {
    title: 'Will this workflow run? GitHub Actions on: filters',
    sub: 'Fill in the filters of the workflow and describe the event. Branch and path filters must both pass.',
    W: 640, H: 170,
    params: [
      { k: 'ev', label: 'Event', type: 'select', v: 'push', opts: [['push', 'push to a branch'], ['tag', 'push of a tag'], ['pr', 'pull_request'], ['dispatch', 'workflow_dispatch (Run workflow button)'], ['schedule', 'schedule (cron)']] },
      { k: 'ref', label: 'Branch pushed, tag pushed, or pull request target branch', type: 'text', v: 'feature/login' },
      { k: 'files', label: 'Changed files', type: 'area', v: 'src/app.py\nREADME.md' },
      { k: 'branches', label: 'on.<event>.branches (empty means no filter)', type: 'text', v: 'main, release/**' },
      { k: 'tags', label: 'on.push.tags', type: 'text', v: '' },
      { k: 'paths', label: 'paths', type: 'text', v: '' },
      { k: 'pathsIgnore', label: 'paths-ignore', type: 'text', v: 'docs/**, **.md' }
    ],
    tips: [
      { t: 'A push to a feature branch does not match main or release/**, so nothing runs.', set: { ev: 'push', ref: 'feature/login', branches: 'main, release/**' } },
      { t: 'Open a pull request into main: for pull_request the branch filter checks the target branch.', set: { ev: 'pr', ref: 'main' } },
      { t: 'Only README.md changed and paths-ignore covers **.md, so the run is skipped.', set: { ev: 'push', ref: 'main', files: 'README.md', pathsIgnore: 'docs/**, **.md', paths: '' } },
      { t: 'A tag push with only a branches filter: GitHub does not run it, because tags were never mentioned.', set: { ev: 'tag', ref: 'v1.2.0', branches: 'main', tags: '' } },
      { t: 'Add tags: v* and the release tag runs it.', set: { ev: 'tag', ref: 'v1.2.0', branches: 'main', tags: 'v*' } },
      { t: 'Order matters: with release/**, !release/**-alpha the alpha branch is excluded.', set: { ev: 'push', ref: 'release/2.0-alpha', branches: 'release/**, !release/**-alpha', files: 'src/app.py' } }
    ],
    draw(z) {
      const g = z.g, p = z.p, files = list(p.files), br = list(p.branches), tg = list(p.tags), pa = list(p.paths), pi = list(p.pathsIgnore);
      const checks = [];
      let run = true;
      if (p.ev === 'dispatch' || p.ev === 'schedule') { checks.push([true, p.ev === 'dispatch' ? 'workflow_dispatch has no branch or path filters. You pick the branch in the Run workflow menu.' : 'schedule runs on the latest commit of the default branch. Filters do not apply.']); }
      else {
        if (p.ev === 'tag') {
          if (!tg.length && br.length) { run = false; checks.push([false, 'Only branches are filtered, so pushes of tags never run this workflow.']); }
          else if (tg.length) { const ok = filterMatch(tg, p.ref); run = run && ok; checks.push([ok, `tags filter ${ok ? 'matches' : 'does not match'} ${p.ref}`]); }
          else checks.push([true, 'no ref filters, every push runs']);
        } else {
          if (!br.length && tg.length && p.ev === 'push') { run = false; checks.push([false, 'Only tags are filtered, so pushes to branches never run this workflow.']); }
          else if (br.length) { const ok = filterMatch(br, p.ref); run = run && ok; checks.push([ok, `${p.ev === 'pr' ? 'target branch' : 'branch'} ${p.ref} ${ok ? 'matches' : 'does not match'} the branches filter`]); }
          else checks.push([true, 'no branch filter']);
        }
        if (pa.length) { const ok = files.some(f => filterMatch(pa, f)); run = run && ok; checks.push([ok, ok ? 'at least one changed file matches paths' : 'no changed file matches paths']); }
        if (pi.length) { const all = files.length > 0 && files.every(f => filterMatch(pi.map(x => x.replace(/^!/, '')), f)); run = run && !all; checks.push([!all, all ? 'every changed file matches paths-ignore' : 'some changed file is outside paths-ignore']); }
      }
      checks.forEach(([ok, s], i) => { D.text(g, ok ? '✓' : '✗', 16, 30 + i * 26, { s: 16, b: true, c: ok ? z.col.green : z.col.red }); D.text(g, fitText(g, s, z.W - 60, { s: 12 }), 40, 30 + i * 26, { s: 12, c: z.col.ink }); });
      tag(g, run ? 'Workflow runs' : 'Workflow does not run', z.W / 2, 30 + checks.length * 26 + 22, { s: 14, fill: run ? z.col.green : z.col.red, c: '#fff' });
      return `<p>Patterns: <code>*</code> matches anything except /, <code>**</code> matches anything, a leading <code>!</code> excludes, and the last matching pattern wins.</p>`;
    }
  });

  /* ---------- matrix ---------- */
  def('matrix', {
    title: 'strategy.matrix: one job written, many jobs run',
    sub: 'GitHub makes one job for every combination, removes the exclude entries, then adds include entries.',
    W: 640, H: 250,
    params: [
      { k: 'os', label: 'os values', type: 'text', v: 'ubuntu-latest, windows-latest, macos-latest' },
      { k: 'py', label: 'python-version values', type: 'text', v: '3.12, 3.13' },
      { k: 'exclude', label: 'exclude (os:version per line)', type: 'area', v: 'macos-latest:3.12' },
      { k: 'include', label: 'include (os:version per line)', type: 'area', v: 'ubuntu-latest:3.14' },
      { k: 'fail', label: 'This job fails (os:version)', type: 'text', v: '' },
      { k: 'ff', label: 'fail-fast (default true)', type: 'check', v: true }
    ],
    tips: [
      { t: '3 × 2 = 6, minus 1 excluded, plus 1 included = 6 jobs.', set: { fail: '' } },
      { t: 'Make windows 3.13 fail with fail-fast on: GitHub cancels the jobs still running or waiting.', set: { fail: 'windows-latest:3.13', ff: true } },
      { t: 'Turn fail-fast off: the other jobs finish, so QA sees every failing combination in one run.', set: { fail: 'windows-latest:3.13', ff: false } },
      { t: 'An include that already exists adds nothing new.', set: { include: 'ubuntu-latest:3.12', exclude: '', fail: '' } }
    ],
    draw(z) {
      const g = z.g, os = list(z.p.os), py = list(z.p.py), ex = list(z.p.exclude), inc = list(z.p.include);
      let jobs = []; os.forEach(o => py.forEach(v => jobs.push(o + ':' + v)));
      const removed = jobs.filter(j => ex.includes(j)); jobs = jobs.filter(j => !ex.includes(j));
      const added = inc.filter(j => !jobs.includes(j)); jobs = jobs.concat(added);
      const fi = jobs.indexOf(z.p.fail.trim()), cols = 4, cw = (z.W - 20) / cols, ch = 40;
      jobs.forEach((j, i) => {
        const x = 10 + (i % cols) * cw, y = 12 + Math.floor(i / cols) * (ch + 8);
        if (y + ch > z.H - 30) return;
        const st = fi < 0 ? 'pass' : i === fi ? 'fail' : z.p.ff && i > fi ? 'cancel' : 'pass';
        rr(g, x, y, cw - 8, ch, 7, { fill: st === 'fail' ? 'rgba(239,68,68,.25)' : st === 'cancel' ? z.col.bg : 'rgba(34,197,94,.2)', stroke: added.includes(j) ? z.col.purple : z.col.line, w: added.includes(j) ? 2 : 1 });
        const [o, v] = j.split(':');
        D.text(g, fitText(g, o, cw - 20, { s: 11, b: true }), x + 8, y + 16, { s: 11, b: true, c: z.col.ink });
        D.text(g, `py ${v}  ${st === 'cancel' ? 'cancelled' : st === 'fail' ? 'failed' : 'passed'}`, x + 8, y + 32, { s: 10, c: z.col.ink2 });
      });
      D.text(g, `${os.length} × ${py.length} = ${os.length * py.length}, − ${removed.length} excluded, + ${added.length} included = ${jobs.length} jobs`, 10, z.H - 10, { s: 13, b: true, c: z.col.ink });
      return `<p>A matrix may make at most 256 jobs in one workflow run. Upload artifacts with a name that includes the matrix values, for example <code>report-\${{ matrix.os }}-\${{ matrix.python-version }}</code>, because two jobs cannot upload to the same artifact name.</p>`;
    }
  });

  /* ---------- dependency cache keys ---------- */
  def('cachekey', {
    title: 'Cache keys: exact hit, partial restore or miss',
    sub: 'actions/cache looks for the exact key first, then for the newest cache whose key starts with a restore key. Caches from the default branch can be used by every branch.',
    W: 640, H: 210,
    params: [
      { k: 'ver', label: 'Version of requirements.txt in this commit', type: 'range', v: 2, min: 1, max: 3 },
      { k: 'os', label: 'Runner OS', type: 'select', v: 'Linux', opts: [['Linux', 'Linux'], ['Windows', 'Windows']] },
      { k: 'branch', label: 'This run is on', type: 'select', v: 'main', opts: [['main', 'main (default branch)'], ['feature', 'feature/x']] },
      { k: 'm1', label: 'An earlier run on main saved the cache for version 1 on Linux', type: 'check', v: true },
      { k: 'm2', label: 'An earlier run on main saved it for version 2 on Linux', type: 'check', v: true },
      { k: 'f3', label: 'An earlier run on feature/x saved it for version 3 on Linux', type: 'check', v: false }
    ],
    tips: [
      { t: 'Version 2 on main: exact hit. cache-hit is true and nothing is saved at the end.', set: { ver: 2, branch: 'main', os: 'Linux' } },
      { t: 'Bump to version 3: no exact key, the restore key brings back the version 2 files, and a new cache is saved at the end.', set: { ver: 3, branch: 'main', f3: false } },
      { t: 'A feature branch can read main\'s caches but main cannot read the feature branch\'s.', set: { ver: 3, branch: 'main', f3: true } },
      { t: 'Windows never reuses a Linux cache because runner.os is part of the key.', set: { os: 'Windows', ver: 2 } }
    ],
    draw(z) {
      const g = z.g, h = v => hex(sha1(enc('requirements v' + v))).slice(0, 8), key = `pip-${z.p.os}-${h(z.p.ver)}`, pre = `pip-${z.p.os}-`;
      const saved = [];
      if (z.p.m1) saved.push({ key: `pip-Linux-${h(1)}`, br: 'main', age: 3 });
      if (z.p.m2) saved.push({ key: `pip-Linux-${h(2)}`, br: 'main', age: 2 });
      if (z.p.f3) saved.push({ key: `pip-Linux-${h(3)}`, br: 'feature', age: 1 });
      const visible = saved.filter(s => s.br === z.p.branch || s.br === 'main');
      const exact = visible.find(s => s.key === key), part = !exact && visible.filter(s => s.key.startsWith(pre)).sort((a, b) => a.age - b.age)[0];
      D.text(g, `key:          ${key}`, 14, 24, { s: 12, mono: true, b: true, c: z.col.ink });
      D.text(g, `restore-keys: ${pre}`, 14, 44, { s: 12, mono: true, c: z.col.ink2 });
      saved.forEach((s, i) => {
        const y = 66 + i * 34, vis = visible.includes(s), hit = s === exact || s === part;
        rr(g, 14, y, z.W - 28, 28, 6, { fill: hit ? 'rgba(34,197,94,.22)' : vis ? z.col.bg : 'transparent', stroke: vis ? z.col.line : z.col.line, dash: vis ? null : [4, 4] });
        D.text(g, `${s.key}   saved on ${s.br}${vis ? '' : '   (not visible from this branch)'}`, 24, y + 18, { s: 11, mono: true, c: vis ? z.col.ink : z.col.ink2 });
      });
      const verdict = exact ? 'Exact hit: cache-hit = true. Dependencies are already there, the save step is skipped.' : part ? `Partial restore of ${part.key}: cache-hit = false. Install the missing packages, then a new cache is saved under the new key.` : 'Miss: nothing restored. Install everything, then the cache is saved at the end of the job.';
      tag(g, exact ? 'exact hit' : part ? 'partial restore' : 'miss', z.W - 80, 24, { s: 12, fill: exact ? z.col.green : part ? z.col.orange : z.col.red, c: '#fff' });
      return `<p>${verdict}</p><p>A repository may keep up to 10 GB of caches. Caches not used for 7 days are removed. A cache is a speed up only, so the job must still work with an empty cache.</p>`;
    }
  });

  /* ---------- artifact lifetime ---------- */
  def('artlife', {
    title: 'How long an artifact lives, and how you can fetch it',
    sub: 'An artifact is stored with the run. After it expires it is deleted and every download way stops working.',
    W: 660, H: 230,
    params: [
      { k: 'plat', label: 'Platform', type: 'select', v: 'gha', opts: [['gha', 'GitHub Actions'], ['gitlab', 'GitLab CI/CD (GitLab.com)']] },
      { k: 'ret', label: 'retention-days (GitHub) or expire_in in days (GitLab). 0 means not set', type: 'range', v: 0, min: 0, max: 90 },
      { k: 'day', label: 'You try to download on day', type: 'range', v: 40, min: 0, max: 120 },
      { k: 'latest', label: 'GitLab: this is the latest successful pipeline on its branch', type: 'check', v: false, show: p => p.plat === 'gitlab' }
    ],
    tips: [
      { t: 'GitHub default: 90 days, so day 40 works.', set: { plat: 'gha', ret: 0, day: 40 } },
      { t: 'GitLab.com default: 30 days, so day 40 is too late.', set: { plat: 'gitlab', ret: 0, day: 40, latest: false } },
      { t: 'But GitLab keeps the artifacts of the latest successful pipeline on a branch, whatever expire_in says.', set: { plat: 'gitlab', ret: 0, day: 40, latest: true } },
      { t: 'A QA report you only need for two weeks: retention-days: 14 saves storage.', set: { plat: 'gha', ret: 14, day: 10 } }
    ],
    draw(z) {
      const g = z.g, gh = z.p.plat === 'gha', life = z.p.ret || (gh ? 90 : 30), keep = !gh && z.p.latest, alive = keep || z.p.day < life;
      const x0 = 30, x1 = z.W - 30, sx = d => x0 + (x1 - x0) * d / 120;
      rr(g, x0, 50, x1 - x0, 26, 6, { fill: z.col.bg });
      rr(g, x0, 50, sx(keep ? 120 : life) - x0, 26, 6, { fill: 'rgba(34,197,94,.35)' });
      [0, 30, 60, 90, 120].forEach(d => D.text(g, `day ${d}`, sx(d), 94, { a: 'center', s: 10, c: z.col.ink2 }));
      D.text(g, keep ? 'kept: latest successful pipeline' : `expires on day ${life}${z.p.ret ? '' : ' (default)'}`, sx(keep ? 60 : Math.min(life, 100)), 40, { a: 'center', s: 11, b: true, c: z.col.green });
      D.arrow(g, sx(z.p.day), 130, sx(z.p.day), 80, alive ? z.col.green : z.col.red, 2.5, 8);
      D.text(g, alive ? 'download works' : 'expired: 404 / gone', sx(z.p.day), 146, { a: 'center', s: 12, b: true, c: alive ? z.col.green : z.col.red });
      const ways = gh ? ['run page: Artifacts list', 'gh run download <run-id> -n <name>', 'REST: /actions/artifacts/{id}/zip', 'download-artifact (same run, or run-id + token)'] : ['job page: Download or Browse', 'glab job artifact <ref> <job>', 'API: /jobs/artifacts/<ref>/download?job=<job>', 'later jobs: needs or dependencies'];
      ways.forEach((w, i) => { const x = 14 + (i % 2) * ((z.W - 20) / 2); D.text(g, '• ' + w, x, 180 + Math.floor(i / 2) * 22, { s: 11, mono: true, c: alive ? z.col.ink : z.col.ink2 }); });
      return `<p>${gh ? 'GitHub keeps artifacts and logs 90 days by default. retention-days can only make it shorter, from 1 to the repository limit.' : 'GitLab uses the instance default (30 days on GitLab.com) when expire_in is missing. Use expire_in: never or the Keep button to keep one forever. For releases use the package registry instead.'}</p>`;
    }
  });

  /* ---------- GitLab rules ---------- */
  function glTokens(s) {
    const out = []; let i = 0;
    while (i < s.length) {
      const c = s[i];
      if (/\s/.test(c)) { i++; continue; }
      if (c === '$') { const m = s.slice(i).match(/^\$\{?(\w+)\}?/); out.push({ t: 'var', v: m[1] }); i += m[0].length; continue; }
      if (c === '"' || c === "'") { const j = s.indexOf(c, i + 1); out.push({ t: 'str', v: s.slice(i + 1, j) }); i = j + 1; continue; }
      if (c === '/') { const m = s.slice(i).match(/^\/((?:\\.|[^/])*)\/(\w*)/); out.push({ t: 're', v: new RegExp(m[1], m[2]) }); i += m[0].length; continue; }
      const two = s.slice(i, i + 2);
      if (['==', '!=', '=~', '!~', '&&', '||'].includes(two)) { out.push({ t: 'op', v: two }); i += 2; continue; }
      if (c === '(' || c === ')') { out.push({ t: c }); i++; continue; }
      if (s.slice(i, i + 4) === 'null') { out.push({ t: 'null' }); i += 4; continue; }
      throw new Error(`cannot read "${s.slice(i)}"`);
    }
    return out;
  }
  function glEval(expr, V) {
    const T = glTokens(expr); let k = 0;
    const val = () => { const t = T[k++]; if (!t) throw new Error('expression ends too early'); if (t.t === 'var') return V[t.v] === undefined || V[t.v] === '' ? null : V[t.v]; if (t.t === 'str') return t.v; if (t.t === 're') return t.v; if (t.t === 'null') return null; if (t.t === '(') { const v = or(); k++; return v; } throw new Error('unexpected ' + (t.v || t.t)); };
    const cmp = () => {
      const a = val(), t = T[k];
      if (t && t.t === 'op' && ['==', '!=', '=~', '!~'].includes(t.v)) {
        k++; const b = val();
        if (t.v === '==') return a === b; if (t.v === '!=') return a !== b;
        const m = a !== null && b instanceof RegExp && b.test(a); return t.v === '=~' ? m : !m;
      }
      return a !== null && a !== false;
    };
    const and = () => { let v = cmp(); while (T[k] && T[k].v === '&&') { k++; const r = cmp(); v = v && r; } return v; };
    const or = () => { let v = and(); while (T[k] && T[k].v === '||') { k++; const r = and(); v = v || r; } return v; };
    const r = or();
    if (k < T.length) throw new Error('extra text after the expression');
    return r;
  }
  function glRules(text) {
    const rules = []; let cur = null;
    String(text).split('\n').forEach(raw => {
      const l = raw.replace(/\s+#.*$/, '').trimEnd(); if (!l.trim()) return;
      let m = l.match(/^\s*-\s*(.*)$/);
      if (m) { cur = {}; rules.push(cur); if (!m[1]) return; }
      const kv = (m ? m[1] : l.trim()).match(/^(if|when|allow_failure|changes):\s*(.*)$/);
      if (kv && cur) cur[kv[1]] = kv[2].replace(/^(["'])(.*)\1$/, (a, q, v) => kv[1] === 'if' ? a : v);
    });
    return rules;
  }
  def('glrules', {
    title: 'GitLab rules: is the job added to this pipeline?',
    sub: 'GitLab checks the rules from the top. The first rule whose if is true decides. If none matches, the job is left out.',
    W: 640, H: 200,
    params: [
      { k: 'rules', label: 'rules: of the job', type: 'area', v: '- if: $CI_PIPELINE_SOURCE == "merge_request_event"\n- if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH\n- if: $CI_PIPELINE_SOURCE == "schedule"\n  when: never\n- if: $CI_COMMIT_TAG =~ /^v\\d+/\n  when: manual' },
      { k: 'src', label: 'Pipeline source ($CI_PIPELINE_SOURCE)', type: 'select', v: 'push', opts: [['push', 'push'], ['merge_request_event', 'merge_request_event'], ['schedule', 'schedule'], ['web', 'web (Run pipeline button)'], ['api', 'api']] },
      { k: 'ref', label: 'Branch, or tag when the push is a tag', type: 'text', v: 'main' },
      { k: 'isTag', label: 'The push is a tag', type: 'check', v: false, show: p => p.src === 'push' },
      { k: 'target', label: 'Merge request target branch', type: 'text', v: 'main', show: p => p.src === 'merge_request_event' }
    ],
    tips: [
      { t: 'A push to main matches rule 2, so the job runs (when: on_success is the default).', set: { src: 'push', ref: 'main', isTag: false } },
      { t: 'A push to a feature branch matches nothing, so the job is not in the pipeline at all.', set: { src: 'push', ref: 'feature/login', isTag: false } },
      { t: 'In a merge request pipeline $CI_COMMIT_BRANCH is not set, which is why rule 1 checks the source instead.', set: { src: 'merge_request_event', ref: 'feature/login' } },
      { t: 'A scheduled pipeline on main still matches rule 2 first. Order matters, so move the schedule rule to the top to block it.', set: { src: 'schedule', ref: 'main' } },
      { t: 'Push tag v2.1.0: the job is added as a manual job with a play button.', set: { src: 'push', ref: 'v2.1.0', isTag: true } }
    ],
    draw(z) {
      const g = z.g, p = z.p, mr = p.src === 'merge_request_event', tagP = p.src === 'push' && p.isTag;
      const V = { CI_PIPELINE_SOURCE: p.src, CI_DEFAULT_BRANCH: 'main', CI_COMMIT_REF_NAME: p.ref };
      if (tagP) V.CI_COMMIT_TAG = p.ref; else if (!mr) V.CI_COMMIT_BRANCH = p.ref;
      if (mr) { V.CI_MERGE_REQUEST_SOURCE_BRANCH_NAME = p.ref; V.CI_MERGE_REQUEST_TARGET_BRANCH_NAME = p.target; }
      const rules = glRules(p.rules); let decided = null, err = '';
      rules.forEach((r, i) => {
        const y = 22 + i * 30;
        let res = null;
        if (decided === null && !err) { try { res = r.if ? glEval(r.if, V) : true; } catch (e) { err = `rule ${i + 1}: ${e.message}`; } }
        if (res && decided === null) decided = i;
        rr(g, 10, y - 16, z.W - 20, 26, 6, { fill: decided === i ? 'rgba(34,197,94,.22)' : res === false ? z.col.bg : 'transparent', stroke: z.col.line });
        D.text(g, fitText(g, `${i + 1}. ${r.if ? 'if: ' + r.if : '(no if, always matches)'}${r.when ? '   when: ' + r.when : ''}`, z.W - 140, { s: 11, mono: true }), 18, y + 1, { s: 11, mono: true, c: z.col.ink });
        D.text(g, decided === i ? 'first match' : res === false ? 'false' : res === null ? 'not checked' : '', z.W - 18, y + 1, { a: 'right', s: 11, b: true, c: decided === i ? z.col.green : z.col.ink2 });
      });
      const when = decided === null ? null : rules[decided].when || 'on_success';
      const verdict = err ? err : decided === null ? 'No rule matched: the job is not added.' : when === 'never' ? `Rule ${decided + 1} says when: never, so the job is not added.` : `Added with when: ${when}${when === 'manual' ? ' (waits for someone to press play)' : ''}.`;
      tag(g, err ? 'error' : decided === null || when === 'never' ? 'not added' : 'added', z.W / 2, z.H - 18, { s: 13, fill: err ? z.col.orange : decided === null || when === 'never' ? z.col.red : z.col.green, c: '#fff' });
      const vs = Object.entries(V).map(([k, v]) => `$${k} = "${v}"`).join('\n');
      return `<p>${esc(verdict)}</p><pre>${esc(vs)}\n(variables not listed are not set in this pipeline)</pre>`;
    }
  });

  /* ---------- YAML to data ---------- */
  function yamlParse(src) {
    const L = [];
    String(src).split('\n').forEach((raw, i) => {
      if (/^\s*\t/.test(raw) || /^ *\t/.test(raw)) throw new Error(`line ${i + 1}: a tab in the indentation. YAML allows spaces only.`);
      let s = raw, q = null, cut = -1;
      for (let k = 0; k < s.length; k++) { const c = s[k]; if (q) { if (c === q) q = null; continue; } if (c === '"' || c === "'") q = c; else if (c === '#' && (k === 0 || /\s/.test(s[k - 1]))) { cut = k; break; } }
      if (cut >= 0) s = s.slice(0, cut);
      if (!s.trim()) { L.push({ blank: true, raw, n: i + 1 }); return; }
      L.push({ ind: s.match(/^ */)[0].length, text: s.trim(), raw, n: i + 1 });
    });
    const lines = L.filter(l => !l.blank);
    const scalar = v => {
      v = v.trim();
      if (/^".*"$/.test(v) || /^'.*'$/.test(v)) return v.slice(1, -1);
      if (/^\[.*\]$/.test(v)) return v.slice(1, -1).split(',').map(x => x.trim()).filter(Boolean).map(scalar);
      if (v === 'true' || v === 'false') return v === 'true';
      if (v === 'null' || v === '~' || v === '') return null;
      if (/^-?\d+(\.\d+)?$/.test(v)) return +v;
      return v;
    };
    let i = 0;
    const blockScalar = (ind, style) => {
      const out = []; let base = null; i++;
      while (i < lines.length && lines[i].ind > ind) { if (base === null) base = lines[i].ind; out.push(lines[i].raw.slice(base)); i++; }
      return style === '|' ? out.join('\n') + '\n' : out.join(' ') + '\n';
    };
    const block = ind => {
      if (i >= lines.length) return null;
      return lines[i].text.startsWith('- ') || lines[i].text === '-' ? seq(lines[i].ind) : map(lines[i].ind);
    };
    const value = (rest, ind) => {
      if (rest === '|' || rest === '>' || rest === '|-' || rest === '>-') return blockScalar(ind, rest[0]);
      i++;
      if (rest !== '') return scalar(rest);
      if (i < lines.length && lines[i].ind > ind) return block(lines[i].ind);
      if (i < lines.length && lines[i].ind === ind && lines[i].text.startsWith('-')) return seq(ind);
      return null;
    };
    const map = ind => {
      const m = {};
      while (i < lines.length && lines[i].ind === ind && !lines[i].text.startsWith('- ')) {
        const l = lines[i], mm = l.text.match(/^("[^"]*"|'[^']*'|[^:]+?):(?:\s+(.*))?$/);
        if (!mm) throw new Error(`line ${l.n}: expected "key: value". ${/^[^:]+:\S/.test(l.text) ? 'Put a space after the colon.' : ''}`);
        const k = mm[1].replace(/^["']|["']$/g, '');
        if (k in m) throw new Error(`line ${l.n}: the key "${k}" appears twice in the same mapping`);
        m[k] = value(mm[2] === undefined ? '' : mm[2].trim(), ind);
      }
      if (i < lines.length && lines[i].ind > ind) throw new Error(`line ${lines[i].n}: indented more than the line before it expects`);
      return m;
    };
    const seq = ind => {
      const a = [];
      while (i < lines.length && lines[i].ind === ind && (lines[i].text.startsWith('- ') || lines[i].text === '-')) {
        const l = lines[i], rest = l.text === '-' ? '' : l.text.slice(2), off = l.text.length - rest.length;
        if (rest === '') { i++; a.push(i < lines.length && lines[i].ind > ind ? block(lines[i].ind) : null); continue; }
        if (/^("[^"]*"|'[^']*'|[^:\s][^:]*?):(\s|$)/.test(rest) && !/^\S+:\/\//.test(rest)) {
          lines[i] = { ind: ind + off, text: rest, raw: ' '.repeat(ind + off) + rest, n: l.n };
          a.push(map(ind + off));
        } else { i++; a.push(scalar(rest)); }
      }
      return a;
    };
    const root = block(lines.length ? lines[0].ind : 0);
    if (i < lines.length) throw new Error(`line ${lines[i].n}: indentation does not line up with any key above it`);
    return root;
  }
  function flatten(v, depth, key, out) {
    if (Array.isArray(v)) { out.push({ depth, key, kind: `list of ${v.length}` }); v.forEach((x, k) => flatten(x, depth + 1, `[${k}]`, out)); }
    else if (v && typeof v === 'object') { out.push({ depth, key, kind: `map of ${Object.keys(v).length}` }); Object.keys(v).forEach(k => flatten(v[k], depth + 1, k, out)); }
    else out.push({ depth, key, val: v });
    return out;
  }
  def('yamlview', {
    title: 'YAML to data: what the CI server really reads',
    sub: 'Indentation decides what belongs to what. A dash starts a list item. Edit the YAML and watch the tree change, or break it on purpose.',
    W: 640, H: 320,
    params: [{ k: 'src', label: 'YAML', type: 'area', v: 'name: CI\non:\n  push:\n    branches: [main]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v7\n      - name: Run tests\n        run: |\n          pip install -r requirements.txt\n          python -m pytest' }],
    tips: [
      { t: 'Indent "run" by two fewer spaces. It stops belonging to the step and the file breaks.', set: { src: 'jobs:\n  test:\n    steps:\n      - name: Run tests\n      run: pytest' } },
      { t: 'A tab instead of spaces is an error in YAML.', set: { src: 'jobs:\n\ttest: x' } },
      { t: 'Forget the space after a colon: key:value is one plain string, not a key.', set: { src: 'stages:\n  - build\nimage:python:3.13' } },
      { t: 'A GitLab job: stage, script list and artifacts map.', set: { src: 'build:\n  stage: build\n  script:\n    - mkdir -p dist\n    - python -m zipfile -c dist/app.zip app\n  artifacts:\n    paths:\n      - dist/app.zip\n    expire_in: 30 days' } },
      { t: 'A key written twice in the same map is an error here and a hidden overwrite in some parsers.', set: { src: 'test:\n  script: pytest\n  script: echo hi' } }
    ],
    draw(z) {
      const g = z.g;
      let data, err = '';
      try { data = yamlParse(z.p.src); } catch (e) { err = e.message; }
      if (err) { rr(g, 10, 10, z.W - 20, 60, 8, { fill: 'rgba(239,68,68,.15)', stroke: z.col.red }); wrap(g, err, 22, 36, z.W - 44, { s: 13, b: true, c: z.col.red }); return `<p class="gk-bad">${esc(err)}</p><p>The CI server rejects the whole file with an error like this before any job runs.</p>`; }
      const rows = flatten(data, 0, '(file)', []), rh = 20, max = Math.floor((z.H - 10) / rh);
      rows.slice(0, max).forEach((r, k) => {
        const x = 12 + r.depth * 22, y = 8 + k * rh;
        if (r.depth) D.line(g, x - 12, y + 9, x - 3, y + 9, z.col.line, 1);
        const label = r.kind ? `${r.key}  (${r.kind})` : `${r.key}: ${typeof r.val === 'string' ? JSON.stringify(r.val) : String(r.val)}`;
        D.text(g, fitText(g, label, z.W - x - 12, { s: 12, mono: true }), x, y + 13, { s: 12, mono: true, b: !!r.kind, c: r.kind ? z.col.cv : z.col.ink });
      });
      if (rows.length > max) D.text(g, `… ${rows.length - max} more`, z.W - 12, z.H - 6, { a: 'right', s: 11, c: z.col.ink2 });
      return `<p class="gk-ok">Valid YAML.</p><pre>${esc(JSON.stringify(data, null, 2))}</pre>`;
    }
  });
})();

/* ===== page helpers for the boxes written by tools/git-build/gitkit.py ===== */
(() => {
  const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  function hl(line, lang) {
    if (lang === 'yaml') {
      const m = line.match(/^(\s*)(-\s+)?([^\s#'"][^:#]*?:)(\s|$)(.*)$/);
      let head = '', rest = line;
      if (m) { head = esc(m[1]) + (m[2] ? `<span class="p">${esc(m[2])}</span>` : '') + `<span class="k">${esc(m[3])}</span>` + esc(m[4]); rest = m[5]; }
      else { const d = line.match(/^(\s*)(-\s+)(.*)$/); if (d) { head = esc(d[1]) + `<span class="p">${esc(d[2])}</span>`; rest = d[3]; } }
      let body = '', q = null;
      for (let k = 0; k < rest.length; k++) { const c = rest[k]; if (!q && c === '#' && (k === 0 || /\s/.test(rest[k - 1]))) { body += `<span class="c">${esc(rest.slice(k))}</span>`; break; } if (q) { if (c === q) q = null; } else if (c === '"' || c === "'") q = c; body += esc(c); }
      body = body.replace(/(\$\{\{[^}]*\}\}|\$\{?\w+\}?)/g, '<span class="v">$1</span>').replace(/(&quot;|")([^"]*)(")/g, '<span class="s">$1$2$3</span>');
      return head + body;
    }
    if (lang === 'py') return esc(line).replace(/(#.*)$/, '<span class="c">$1</span>');
    return esc(line);
  }
  function wire(root = document) {
    root.querySelectorAll('.gk-hl').forEach(pre => {
      if (pre.dataset.done) return; pre.dataset.done = '1';
      pre.querySelectorAll('.ln').forEach(ln => { const t = ln.textContent; if (t.trim()) ln.innerHTML = hl(t, pre.dataset.hl); });
    });
  }
  document.addEventListener('click', e => {
    const b = e.target.closest('.gk-copy');
    if (b) {
      const box = b.closest('.cv-code'), lines = [...box.querySelectorAll('.cc-src .ln')].filter(l => !l.classList.contains('gc') || box.classList.contains('gk-file')).map(l => l.textContent.replace(/^\s$/, ''));
      const text = lines.join('\n') + '\n';
      const done = () => { b.textContent = 'Copied'; b.classList.add('done'); setTimeout(() => { b.textContent = 'Copy'; b.classList.remove('done'); }, 1400); };
      try { navigator.clipboard.writeText(text).then(done, done); } catch (er) { done(); }
      return;
    }
    const ln = e.target.closest('.gk-file .ln.gk-has, .gk-notes li[data-n]');
    if (ln) {
      const box = ln.closest('.gk-file'), n = ln.dataset.n;
      box.querySelectorAll('.gk-on').forEach(x => x.classList.remove('gk-on'));
      box.querySelectorAll(`[data-n="${n}"]`).forEach(x => x.classList.add('gk-on'));
      const det = box.querySelector('.gk-notes'); if (det) det.open = true;
    }
  });
  const KEY = 'bb-git-baby:' + location.pathname;
  let done = {};
  try { done = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { done = {}; }
  function babies() {
    document.querySelectorAll('.gk-baby').forEach((b, i) => {
      const cb = b.querySelector('.gk-done'); if (!cb || cb.dataset.on) return; cb.dataset.on = '1';
      cb.checked = !!done[i]; b.classList.toggle('done', cb.checked);
      cb.addEventListener('change', () => { done[i] = cb.checked; b.classList.toggle('done', cb.checked); try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) { /* private mode */ } });
    });
  }
  const go = () => { wire(); babies(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
  new MutationObserver(() => go()).observe(document.documentElement, { childList: true, subtree: true });
})();
