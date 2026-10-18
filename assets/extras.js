/* ===== Shared learning extras: interactive comic infographic, real life examples, why-optimized box =====
   Data comes from EXTRA[id] on each page:
   { keywords:[], real:[[emoji,title,text]...], info:{title, panels:[{s:scene, h:head, t:text, more:back}], remember}, why:{...} } */
const XTRA = (() => {
  const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const W = 240;

  /* ---------- tiny SVG scene kit ---------- */
  function row(r, y) {
    const [kind, a, o = {}] = r;
    if (kind === 'e') {
      return { h: 46, svg: `<text x="${W / 2}" y="${y + 34}" text-anchor="middle" font-size="${o.size || 30}" class="xi-emo">${esc(a)}</text>` };
    }
    if (kind === 't') {
      return { h: 26, svg: `<text x="${W / 2}" y="${y + 18}" text-anchor="middle" class="xi-txt${o.b ? ' b' : ''}" font-size="${o.size || 13}">${esc(a)}</text>` };
    }
    if (kind === 'c') {
      const n = a.length, cw = Math.min(34, (W - 16) / n), x0 = (W - cw * n) / 2;
      const hasIx = o.ix !== false, hasP = o.p && Object.keys(o.p).length;
      let s = '';
      a.forEach((v, i) => {
        const cls = (o.hl && o.hl[i]) || '';
        const x = x0 + i * cw;
        s += `<g class="xi-cell ${cls}" style="--d:${i * 60}ms"><rect x="${x + 1.5}" y="${y + (hasIx ? 13 : 2)}" width="${cw - 3}" height="28" rx="6"/><text x="${x + cw / 2}" y="${y + (hasIx ? 32 : 21)}" text-anchor="middle" font-size="${String(v).length > 3 ? 10 : 13}">${esc(v)}</text></g>`;
        if (hasIx) s += `<text x="${x + cw / 2}" y="${y + 10}" text-anchor="middle" class="xi-ix">${o.ix0 !== undefined ? o.ix0 + i : i}</text>`;
        if (hasP && o.p[i] !== undefined) s += `<text x="${x + cw / 2}" y="${y + (hasIx ? 56 : 45)}" text-anchor="middle" class="xi-ptr">▲ ${esc(o.p[i])}</text>`;
      });
      return { h: (hasIx ? 44 : 33) + (hasP ? 18 : 0), svg: s };
    }
    if (kind === 'b') {
      const n = a.length, cw = Math.min(30, (W - 16) / n), x0 = (W - cw * n) / 2, mx = Math.max(...a.map(Math.abs), 1), H = o.h || 60;
      let s = '';
      a.forEach((v, i) => {
        const h = Math.max(3, Math.abs(v) / mx * H), cls = (o.hl && o.hl[i]) || '';
        s += `<g class="xi-bar ${cls}" style="--d:${i * 60}ms"><rect x="${x0 + i * cw + 2}" y="${y + H - h + 4}" width="${cw - 4}" height="${h}" rx="4"/><text x="${x0 + i * cw + cw / 2}" y="${y + H + 18}" text-anchor="middle" font-size="11">${esc(v)}</text></g>`;
      });
      return { h: H + 24, svg: s };
    }
    if (kind === 'g') {
      const R = a.length, C = a[0].length, cw = Math.min(30, (W - 20) / C), x0 = (W - cw * C) / 2;
      let s = '';
      a.forEach((rw, r) => rw.forEach((v, c) => {
        const cls = (o.hl && o.hl[r + ',' + c]) || '';
        s += `<g class="xi-cell ${cls}" style="--d:${(r * C + c) * 40}ms"><rect x="${x0 + c * cw + 1.5}" y="${y + r * 26 + 2}" width="${cw - 3}" height="23" rx="5"/><text x="${x0 + c * cw + cw / 2}" y="${y + r * 26 + 18}" text-anchor="middle" font-size="11.5">${esc(v)}</text></g>`;
      }));
      return { h: R * 26 + 6, svg: s };
    }
    if (kind === 'tree') { // a: array of levels, each a list of labels
      const L = a.length;
      let s = '';
      const pos = a.map((lv, d) => lv.map((_, k) => [W * (k + 0.5) / lv.length, y + 14 + d * 34]));
      a.forEach((lv, d) => { if (d) lv.forEach((_, k) => { const p = pos[d - 1][Math.floor(k * a[d - 1].length / lv.length)]; s += `<line x1="${p[0]}" y1="${p[1]}" x2="${pos[d][k][0]}" y2="${pos[d][k][1]}" class="xi-edge"/>`; }); });
      a.forEach((lv, d) => lv.forEach((v, k) => {
        const cls = (o.hl && o.hl[d + ',' + k]) || '';
        s += `<g class="xi-cell ${cls}" style="--d:${(d * 4 + k) * 70}ms"><rect x="${pos[d][k][0] - 20}" y="${pos[d][k][1] - 11}" width="40" height="22" rx="7"/><text x="${pos[d][k][0]}" y="${pos[d][k][1] + 4}" text-anchor="middle" font-size="11">${esc(v)}</text></g>`;
      }));
      return { h: L * 34 + 6, svg: s };
    }
    return { h: 0, svg: '' };
  }
  function scene(rows) {
    let y = 4, body = '';
    for (const r of rows) { const o = row(r, y); body += o.svg; y += o.h + 4; }
    return `<svg viewBox="0 0 ${W} ${y + 2}" class="xi-svg" role="img" aria-hidden="true">${body}</svg>`;
  }

  /* ---------- infographic: a comic strip of panels that flip and play ---------- */
  function infoHtml(info) {
    if (!info || !info.panels) return '';
    return `<div class="xi" data-xi>
      <div class="xi-head"><div><h3>🖼️ ${esc(info.title || 'Picture this')}</h3><p class="xi-sub">Tap any panel to flip it for the deeper idea, or press Play the comic.</p></div>
        <button class="xi-play" data-xi-play>▶ Play the comic</button></div>
      <div class="xi-strip">${info.panels.map((p, i) => `
        <button class="xi-panel reveal" style="--i:${i}" data-xi-panel aria-label="Panel ${i + 1}: ${esc(p.h)}. Tap to flip.">
          <span class="xi-inner">
            <span class="xi-front"><span class="xi-num">${i + 1}</span>${p.s ? scene(p.s) : ''}<b>${esc(p.h)}</b><span class="xi-cap">${p.t}</span><span class="xi-flip">tap to flip ↻</span></span>
            <span class="xi-back"><span class="xi-num">${i + 1}</span><b>Deeper</b><span class="xi-cap">${p.more || p.t}</span><span class="xi-flip">tap to flip back ↻</span></span>
          </span>
        </button>${i < info.panels.length - 1 ? '<span class="xi-arrow" aria-hidden="true">➜</span>' : ''}`).join('')}
      </div>
      ${info.remember ? `<div class="xi-note"><span>📌</span><div><b>Remember</b> ${info.remember}</div></div>` : ''}
    </div>`;
  }

  /* ---------- real life examples ---------- */
  function realHtml(list) {
    if (!list || !list.length) return '';
    return `<div class="xr"><h3>🌍 Real life, just funnier</h3><p class="xi-sub">The same idea is hiding in things you use every day.</p>
      <div class="xr-grid">${list.map(([e, t, d], i) => `<div class="xr-card reveal" style="--i:${i}"><span class="xr-em">${esc(e)}</span><b>${esc(t)}</b><p>${d}</p></div>`).join('')}</div></div>`;
  }

  /* ---------- why the optimized version wins ---------- */
  function whyHtml(w, opts = {}) {
    if (!w) return '';
    const row = (k, lab, c) => c ? `<tr><td><span class="xw-dot ${k}"></span><b>${lab}</b><div class="xw-n">${esc(c.name || '')}</div></td><td>${c.idea || ''}</td><td class="xw-o">${esc(c.time || '')}</td><td class="xw-o">${esc(c.space || '')}</td></tr>` : '';
    const table = (w.naive || w.opt) ? `<div class="xw-tw"><table class="xw-t"><thead><tr><th>Approach</th><th>Idea</th><th>Time</th><th>Extra space</th></tr></thead><tbody>${row('n', opts.naiveLabel || 'Brute force', w.naive)}${row('o', 'Optimized', w.opt)}</tbody></table></div>` : '';
    return `<div class="xw">${opts.title === false ? '' : `<div class="xw-h">🏆 ${esc(opts.title || 'Why the optimized solution wins')}</div>`}${table}<div class="xw-r">${w.reason || ''}</div></div>`;
  }

  /* ---------- behaviour ---------- */
  let playing = null;
  function wire(root) {
    root.querySelectorAll('[data-xi]').forEach(box => {
      if (box._wired) return;
      box._wired = true;
      const panels = [...box.querySelectorAll('[data-xi-panel]')];
      panels.forEach(p => p.addEventListener('click', () => { p.classList.toggle('flip'); poke(p); }));
      const btn = box.querySelector('[data-xi-play]');
      btn.addEventListener('click', () => {
        if (playing) { clearTimeout(playing); playing = null; panels.forEach(p => p.classList.remove('lit')); btn.textContent = '▶ Play the comic'; return; }
        let k = 0;
        btn.textContent = '❚❚ Stop';
        const stepF = () => {
          panels.forEach((p, j) => { p.classList.toggle('lit', j === k); p.classList.remove('flip'); });
          if (k < panels.length) { poke(panels[k]); k++; playing = setTimeout(stepF, 1800); }
          else { panels.forEach(p => p.classList.remove('lit')); playing = null; btn.textContent = '▶ Replay the comic'; if (window.FUN) { const r = btn.getBoundingClientRect(); FUN.confetti(r.left + r.width / 2, r.top, 40); } }
        };
        stepF();
      });
    });
  }
  function poke(p) { p.classList.remove('poke'); void p.offsetWidth; p.classList.add('poke'); }

  return { infoHtml, realHtml, whyHtml, scene, wire, esc };
})();
