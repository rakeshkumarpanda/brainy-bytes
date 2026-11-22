/* ===== Playful step animations for the newer DSA chapters (tools/dsa-build/playkit.js) =====
   The builder copies this file into every page whose topic sets 'play': True, right after the shared VIZ engine.
   A widget is written as a list of frames. Each frame is a picture of the data plus a sentence from Pip, the guide.
   The shared VIZ Player (play, pause, step, scrub, speed) moves through the frames, so voice teaching and Reset work
   the same as on every other animation.

   PK.widget(el, {
     title, sub,                     heading of the card
     inputs: [ {k, label, type: 'list' | 'num' | 'text' | 'seg', val, opts: [[value, label]...], min, max, w} ],
     random: () => ({k: value}),     optional, adds a "Surprise me" button that fills the inputs
     check: vals => '' or a message  optional, rejects bad input with a friendly note
     frames: vals => [frame...],     builds the story for the current inputs
     ms                              time per frame at 1x speed
   })
   frame = { msg: 'html shown and read aloud', say: 'optional longer spoken text',
             mood: 'idle' | 'think' | 'look' | 'happy' | 'sad' | 'wow' | 'work',
             fx: 'burst' | 'shake' | 'rain', layers: [layer...], vars: {name: value} }
   layers:
     {t: 'row', label, cells: [...], cls: {i: cls}, ptr: {i: 'name'}, idx: true, tag: {i: 'small text'}}
     {t: 'grid', label, rows: [[...]], cls: {'r,c': cls}, rlab: [...], clab: [...], sq: true}
     {t: 'graph', label, w, h, nodes: [[id, x, y, text]], edges: [[a, b, label]], ncls: {id: cls}, ecls: {'a-b': cls}, dir: true, tag: {id: 'text'}}
     {t: 'stack', label, items: [...], cls: {i: cls}, top: 'top'}
     {t: 'bits', label, v, n, cls: {bit: cls}, name}
     {t: 'buckets', label, buckets: [[...]], cls: {'b,i': cls}, bcls: {b: cls}, blab: [...]}
     {t: 'bars', label, vals: [...], cls: {i: cls}, max}
     {t: 'note', html}
   cell classes: look (being checked), yes (found or kept), no (rejected), done (finished, faded), cur, sel, mv, piv, win, ghost
*/
(() => {
  const K = VIZ.kit, W = VIZ.widgets;
  const { esc, $, shell, Player } = K;
  const FACE = { idle: '🙂', think: '🤔', look: '🧐', happy: '🥳', sad: '🤷', wow: '🤩', work: '🛠️' };
  const CHEER = ['Yay', 'Found it', 'Woohoo', 'Gotcha', 'Bingo'];
  const OOPS = ['Oh no', 'Not here', 'Hmm', 'Whoops'];
  const strip = h => String(h).replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
  /* Material 3 Expressive style spring (a damped bounce), written as a CSS linear() easing */
  const SPRING = 'linear(0, 0.009, 0.035 2.1%, 0.141, 0.281 6.7%, 0.723 12.9%, 0.938 16.7%, 1.017, 1.077, 1.121, 1.149 24.3%, 1.159, 1.163, 1.161, 1.154 29.9%, 1.129 32.8%, 1.051 39.6%, 1.017 43.1%, 0.991, 0.977 51%, 0.974 53.8%, 0.975 57.1%, 0.997 69.8%, 1.003 76.9%, 1)';
  const reduce = () => window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function parseList(s, numeric = true) {
    const parts = String(s).split(/[\s,]+/).filter(Boolean);
    if (!numeric) return parts;
    const out = parts.map(Number);
    return out.some(x => !Number.isFinite(x)) ? null : out;
  }

  /* ---------- layer drawing ---------- */
  function cellHtml(v, cls, ptr, idx, tag, key) {
    return `<div class="pk-slot"${key !== undefined ? ` data-fk="${esc(key)}"` : ''}>${ptr ? `<span class="pk-ptr">${esc(ptr)}<i>▼</i></span>` : '<span class="pk-ptr pk-np"></span>'}`
      + `<div class="pk-cell ${cls || ''}">${v === null || v === undefined ? '' : esc(v)}</div>`
      + `${idx !== undefined ? `<span class="pk-idx">${esc(idx)}</span>` : ''}${tag ? `<span class="pk-tag">${esc(tag)}</span>` : ''}</div>`;
  }
  const lab = l => l ? `<div class="pk-lab">${l}</div>` : '';
  const D = {
    row(L) {
      const cls = L.cls || {}, ptr = L.ptr || {}, tag = L.tag || {};
      const cells = L.cells.map((v, i) => cellHtml(v, cls[i], ptr[i], L.idx === false ? undefined : (L.base || 0) + i, tag[i], L.keys ? (L.id || 'r') + ':' + L.keys[i] : undefined)).join('');
      return `${lab(L.label)}<div class="pk-row${L.small ? ' pk-small' : ''}">${cells || '<span class="pk-empty">empty</span>'}</div>`;
    },
    grid(L) {
      const cls = L.cls || {};
      const head = L.clab ? `<tr>${L.rlab ? '<th></th>' : ''}${L.clab.map(c => `<th>${esc(c)}</th>`).join('')}</tr>` : '';
      const body = L.rows.map((r, ri) => `<tr>${L.rlab ? `<th>${esc(L.rlab[ri])}</th>` : ''}${r.map((v, ci) => `<td class="${cls[ri + ',' + ci] || ''}">${v === null || v === undefined ? '' : esc(v)}</td>`).join('')}</tr>`).join('');
      return `${lab(L.label)}<div class="pk-gw"><table class="pk-grid${L.sq ? ' sq' : ''}">${head}${body}</table></div>`;
    },
    graph(L) {
      const w = L.w || 420, h = L.h || 240, pos = {}, ncls = L.ncls || {}, ecls = L.ecls || {}, tag = L.tag || {};
      L.nodes.forEach(n => { pos[n[0]] = n; });
      const r = L.r || 17;
      const edges = (L.edges || []).map(e => {
        const a = pos[e[0]], b = pos[e[1]];
        if (!a || !b) return '';
        const c = ecls[e[0] + '-' + e[1]] || (L.dir ? '' : ecls[e[1] + '-' + e[0]]) || '';
        const dx = b[1] - a[1], dy = b[2] - a[2], len = Math.hypot(dx, dy) || 1;
        const x2 = b[1] - dx / len * (r + 3), y2 = b[2] - dy / len * (r + 3);
        const mx = (a[1] + b[1]) / 2, my = (a[2] + b[2]) / 2;
        return `<line class="pk-e ${c}" x1="${a[1]}" y1="${a[2]}" x2="${L.dir ? x2 : b[1]}" y2="${L.dir ? y2 : b[2]}"${L.dir ? ' marker-end="url(#pk-arrow)"' : ''}/>`
          + (e[2] !== undefined && e[2] !== '' ? `<g class="pk-ew ${c}"><rect x="${mx - 11}" y="${my - 9}" width="22" height="18" rx="6"/><text x="${mx}" y="${my + 4}">${esc(e[2])}</text></g>` : '');
      }).join('');
      const nodes = L.nodes.map(n => `<g class="pk-n ${ncls[n[0]] || ''}"><circle cx="${n[1]}" cy="${n[2]}" r="${r}"/><text x="${n[1]}" y="${n[2] + 5}">${esc(n[3] === undefined ? n[0] : n[3])}</text>${tag[n[0]] !== undefined ? `<text class="pk-nt" x="${n[1]}" y="${n[2] + r + 15}">${esc(tag[n[0]])}</text>` : ''}</g>`).join('');
      return `${lab(L.label)}<div class="pk-gw"><svg class="pk-svg" viewBox="0 0 ${w} ${h}" style="max-width:${w}px" role="img" aria-label="${esc(strip(L.label || 'diagram'))}"><defs><marker id="pk-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>${edges}${nodes}</svg></div>`;
    },
    stack(L) {
      const cls = L.cls || {}, n = L.items.length;
      const items = L.items.map((v, i) => `<div class="pk-plate ${cls[i] || ''}">${esc(v)}${i === n - 1 ? `<small>${esc(L.top || 'top')}</small>` : ''}</div>`).join('');
      return `${lab(L.label)}<div class="pk-stack">${items || '<span class="pk-empty">empty</span>'}</div>`;
    },
    bits(L) {
      const n = L.n || 8, cls = L.cls || {}, v = Number(L.v);
      let cells = '';
      for (let b = n - 1; b >= 0; b--) {
        const on = Math.floor(v / 2 ** b) % 2 === 1;
        cells += `<div class="pk-bitw"><div class="pk-bit ${on ? 'on' : ''} ${cls[b] || ''}">${on ? 1 : 0}</div><span>${2 ** b}</span></div>`;
      }
      return `${lab(L.label)}<div class="pk-bits">${L.name ? `<b class="pk-bn">${esc(L.name)}</b>` : ''}${cells}<em class="pk-bv">= ${esc(L.v)}</em></div>`;
    },
    buckets(L) {
      const cls = L.cls || {}, bcls = L.bcls || {};
      return `${lab(L.label)}<div class="pk-bks">${L.buckets.map((bk, b) => `<div class="pk-bk ${bcls[b] || ''}"><span class="pk-bkl">${esc(L.blab ? L.blab[b] : b)}</span><div class="pk-bkc">${bk.map((v, i) => `<div class="pk-chip ${cls[b + ',' + i] || ''}">${esc(v)}</div>`).join('') || '<span class="pk-dash">·</span>'}</div></div>`).join('')}</div>`;
    },
    bars(L) {
      const cls = L.cls || {}, mx = L.max || Math.max(1, ...L.vals.map(Math.abs));
      return `${lab(L.label)}<div class="pk-bars">${L.vals.map((v, i) => `<div class="pk-barw"><div class="pk-bar ${cls[i] || ''}" style="height:${Math.max(4, Math.round(Math.abs(v) / mx * 100))}%"><span>${esc(v)}</span></div><small>${i}</small></div>`).join('')}</div>`;
    },
    note(L) { return `<div class="pk-note">${L.html}</div>`; }
  };

  /* ---------- effects ---------- */
  function burst(stage) {
    if (reduce()) return;
    const host = stage.querySelector('.pk-cell.yes, .pk-n.yes, .pk-bit.yes, .pk-chip.yes, td.yes, .pk-plate.yes') || stage.querySelector('.pk-face');
    const box = stage.getBoundingClientRect(), hb = host.getBoundingClientRect();
    const x = hb.left - box.left + hb.width / 2, y = hb.top - box.top + hb.height / 2;
    const colors = ['var(--yellow)', 'var(--pink)', 'var(--green)', 'var(--blue)', 'var(--orange)', 'var(--purple)'];
    for (let k = 0; k < 18; k++) {
      const p = document.createElement('i');
      p.className = 'pk-bit-fx';
      const ang = (k / 18) * Math.PI * 2, dist = 40 + Math.random() * 50;
      p.style.cssText = `left:${x}px; top:${y}px; background:${colors[k % colors.length]}; --dx:${Math.cos(ang) * dist}px; --dy:${Math.sin(ang) * dist}px`;
      stage.appendChild(p);
      setTimeout(() => p.remove(), 900);
    }
  }
  function shake(stage) {
    if (reduce()) return;
    stage.classList.remove('pk-shake');
    void stage.offsetWidth;
    stage.classList.add('pk-shake');
  }

  /* ---------- the widget ---------- */
  PK_widget.count = 0;
  function PK_widget(el, o) {
    const b = shell(el, o.title, o.sub);
    const id = 'pk' + (++PK_widget.count);
    const inputs = o.inputs || [];
    const field = f => {
      if (f.type === 'seg') return `<label class="pk-in"><span>${f.label}</span>${K.seg(f.k, f.opts, f.val)}</label>`;
      return `<label class="pk-in"><span>${f.label}</span><input data-k="${f.k}" type="${f.type === 'num' ? 'number' : 'text'}" value="${esc(f.val)}"${f.min !== undefined ? ` min="${f.min}"` : ''}${f.max !== undefined ? ` max="${f.max}"` : ''} style="width:${f.w || (f.type === 'num' ? 80 : 220)}px" spellcheck="false" autocomplete="off"></label>`;
    };
    b.innerHTML = `${inputs.length ? `<div class="pk-form">${inputs.map(field).join('')}<button type="button" class="pk-go">✨ Show me</button>${o.random ? '<button type="button" class="pk-rand">🎲 Surprise me</button>' : ''}</div>` : ''}
      <div class="pk-stage" id="${id}"><div class="pk-layers"></div><div class="pk-vars"></div></div>
      <div class="pk-talk"><div class="pk-face" aria-hidden="true">🙂</div><div class="pk-bub"><b class="pk-who">Pip</b><div class="vz-msg" aria-live="polite"></div></div></div>
      <div class="vz-p"></div>`;
    const stage = $('.pk-stage', b), layers = $('.pk-layers', b), vars = $('.pk-vars', b), msg = $('.vz-msg', b), face = $('.pk-face', b), who = $('.pk-who', b);
    let frames = [], last = -1;
    const vals = {};
    inputs.forEach(f => { vals[f.k] = f.val; });
    const P = Player($('.vz-p', b), show, o.ms || 1100);
    function read() {
      inputs.forEach(f => {
        if (f.type === 'seg') return;
        const inp = $(`input[data-k="${f.k}"]`, b);
        vals[f.k] = f.type === 'num' ? Number(inp.value) : inp.value;
      });
    }
    function build() {
      read();
      const bad = o.check ? o.check(vals) : '';
      if (bad) {
        frames = [{ msg: bad, mood: 'think', fx: 'shake', layers: [{ t: 'note', html: '✏️ Fix the input above and press <b>Show me</b> again.' }] }];
      } else {
        try { frames = o.frames(Object.assign({}, vals)); } catch (e) { frames = [{ msg: 'That input confused me. Please try simpler values.', mood: 'think', layers: [] }]; }
      }
      last = -1;
      P.load(frames.length);
    }
    function show(k) {
      const f = frames[k] || {};
      const before = {};
      if (!reduce()) layers.querySelectorAll('[data-fk]').forEach(x => { before[x.dataset.fk] = x.getBoundingClientRect(); });
      let ls = f.layers, back = k;
      while (ls === undefined && back > 0) ls = (frames[--back] || {}).layers;  /* no layers given: keep the last picture */
      layers.innerHTML = (ls || []).map(L => `<div class="pk-layer">${D[L.t](L)}</div>`).join('');
      const vs = f.vars ? Object.entries(f.vars) : [];
      vars.innerHTML = vs.map(([n, v]) => `<span class="pk-var"><b>${esc(n)}</b> ${esc(v)}</span>`).join('');
      vars.hidden = !vs.length;
      /* FLIP: anything with the same key slides from where it was to where it is now, on a spring */
      layers.querySelectorAll('[data-fk]').forEach(x => {
        const o = before[x.dataset.fk];
        if (!o || !x.animate) return;
        const n = x.getBoundingClientRect(), dx = o.left - n.left, dy = o.top - n.top;
        if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
        x.animate([{ transform: `translate(${dx}px, ${dy}px)` }, { transform: 'none' }], { duration: 650, easing: SPRING });
      });
      msg.innerHTML = f.msg || '';
      const spoken = f.say || strip(f.msg || '');
      if (spoken) msg.dataset.say = spoken; else delete msg.dataset.say;
      const mood = f.mood || 'idle';
      face.textContent = FACE[mood] || FACE.idle;
      face.className = 'pk-face m-' + mood;
      who.textContent = mood === 'happy' ? `Pip · ${CHEER[k % CHEER.length]}!` : mood === 'sad' ? `Pip · ${OOPS[k % OOPS.length]}!` : 'Pip';
      if (k !== last && k === last + 1) {
        if (f.fx === 'burst') burst(stage);
        if (f.fx === 'shake') shake(stage);
        if (f.fx === 'rain') { burst(stage); setTimeout(() => burst(stage), 250); }
      }
      last = k;
    }
    const go = $('.pk-go', b), rnd = $('.pk-rand', b);
    if (go) go.addEventListener('click', build);
    if (rnd) rnd.addEventListener('click', () => {
      const r = o.random();
      Object.entries(r).forEach(([k2, v]) => { const inp = $(`input[data-k="${k2}"]`, b); if (inp) inp.value = Array.isArray(v) ? v.join(', ') : v; });
      build();
    });
    b.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.matches('.pk-in input')) { e.preventDefault(); build(); } });
    inputs.filter(f => f.type === 'seg').forEach(f => K.wireSeg(b, f.k, v => { vals[f.k] = v; build(); }));
    build();
    return { rebuild: build, player: P };
  }

  /* tree layout helper: nodes given as {id: [left, right]} from a root, returns graph nodes and edges */
  function treeLayout(kids, root, label = id => id, w = 440, h = 230) {
    const nodes = [], edges = [], depth = {};
    let order = 0;
    const pos = {};
    (function walk(id, d) {
      if (id === null || id === undefined) return;
      const [l, r] = kids[id] || [];
      walk(l, d + 1);
      pos[id] = { o: order++, d };
      walk(r, d + 1);
      if (l !== null && l !== undefined) edges.push([id, l]);
      if (r !== null && r !== undefined) edges.push([id, r]);
    })(root, 0);
    const maxd = Math.max(0, ...Object.values(pos).map(p => p.d)), n = order;
    Object.entries(pos).forEach(([id, p]) => {
      depth[id] = p.d;
      nodes.push([id, Math.round(24 + (n > 1 ? p.o * (w - 48) / (n - 1) : (w - 48) / 2)), Math.round(26 + (maxd ? p.d * (h - 60) / maxd : 0)), label(id)]);
    });
    return { nodes, edges, depth };
  }

  /* place n nodes on a circle */
  function ring(ids, w = 420, h = 240, labels) {
    const cx = w / 2, cy = h / 2, rr = Math.min(w, h) / 2 - 30;
    return ids.map((id, k) => [id, Math.round(cx + rr * Math.cos(-Math.PI / 2 + k * 2 * Math.PI / ids.length)), Math.round(cy + rr * Math.sin(-Math.PI / 2 + k * 2 * Math.PI / ids.length)), labels ? labels[k] : id]);
  }

  window.PK = { widget: PK_widget, parseList, strip, treeLayout, ring, draw: D };
  W.pk = el => { const f = PK.defs[el.dataset.pk]; if (f) f(el); else el.textContent = 'Unknown playful animation: ' + el.dataset.pk; };
  PK.defs = {};
})();
