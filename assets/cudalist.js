/* CUDA listings (tools/cuda-build/cudakit.py): syntax colours, Copy buttons and line notes that light up the line. */
(() => {
  const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  const KW = /^(if|else|for|while|do|return|break|continue|switch|case|default|const|static|struct|class|template|typename|sizeof|new|delete|using|namespace|auto|extern|inline|volatile|unsigned|signed|true|false|nullptr|def|import|from|as|in|not|and|or|None|True|False|lambda|with|print)$/;
  const TY = /^(void|int|float|double|char|bool|long|short|size_t|dim3|half|__half|__nv_bfloat16|cudaError_t|cudaStream_t|cudaEvent_t|float2|float4|int2|uint32_t|uint64_t|int64_t)$/;
  const QU = /^(__global__|__device__|__host__|__shared__|__constant__|__managed__|__restrict__|__syncthreads|__syncwarp|__shfl_down_sync|__shfl_sync|__shfl_xor_sync|__ballot_sync|__activemask|__threadfence|atomicAdd|atomicCAS|atomicExch|atomicMax|atomicMin|threadIdx|blockIdx|blockDim|gridDim|warpSize)$/;
  function hl(line, lang) {
    let out = '', i = 0;
    const cm = lang === 'py' ? '#' : '//';
    while (i < line.length) {
      const rest = line.slice(i);
      if (rest.startsWith(cm) || (lang !== 'py' && rest.startsWith('/*'))) { out += `<span class="c">${esc(rest)}</span>`; break; }
      if (lang !== 'py' && /^#\s*\w+/.test(rest) && !line.slice(0, i).trim()) { const m = rest.match(/^#\s*\w+/)[0]; out += `<span class="q">${esc(m)}</span>`; i += m.length; continue; }
      const ch = line[i];
      if (ch === '"' || ch === "'") { let j = i + 1; while (j < line.length && line[j] !== ch) { if (line[j] === '\\') j++; j++; } out += `<span class="s">${esc(line.slice(i, j + 1))}</span>`; i = j + 1; continue; }
      if (rest.startsWith('<<<') || rest.startsWith('>>>')) { out += `<span class="b">${esc(rest.slice(0, 3))}</span>`; i += 3; continue; }
      const w = rest.match(/^[A-Za-z_]\w*/);
      if (w) { const t = w[0]; const cls = QU.test(t) || /^cuda[A-Z]\w*$/.test(t) || /^wmma$/.test(t) ? 'q' : TY.test(t) ? 't' : KW.test(t) ? 'k' : ''; out += cls ? `<span class="${cls}">${t}</span>` : t; i += t.length; continue; }
      const n = rest.match(/^\d+(\.\d+)?([eE][-+]?\d+)?[fFuUlL]*/);
      if (n) { out += `<span class="n">${n[0]}</span>`; i += n[0].length; continue; }
      out += esc(ch); i++;
    }
    return out;
  }
  function wire(root = document) {
    root.querySelectorAll('.ck-hl').forEach(pre => {
      if (pre.dataset.done) return; pre.dataset.done = '1';
      pre.querySelectorAll('.ln').forEach(ln => { const t = ln.textContent; if (t.trim()) ln.innerHTML = hl(t, pre.dataset.hl); });
    });
  }
  document.addEventListener('click', e => {
    const b = e.target.closest('.ck-copy');
    if (b) {
      const box = b.closest('.cv-code');
      const text = [...box.querySelectorAll('.cc-src .ln')].filter(l => !l.classList.contains('ck-c')).map(l => l.textContent.replace(/^\s$/, '')).join('\n') + '\n';
      const done = () => { b.textContent = 'Copied'; b.classList.add('done'); setTimeout(() => { b.textContent = 'Copy'; b.classList.remove('done'); }, 1400); };
      try { navigator.clipboard.writeText(text).then(done, done); } catch (er) { done(); }
      return;
    }
    const ln = e.target.closest('.ck-file .ln.ck-has, .ck-notes li[data-n]');
    if (ln) {
      const box = ln.closest('.ck-file'), n = ln.dataset.n;
      box.querySelectorAll('.ck-on').forEach(x => x.classList.remove('ck-on'));
      box.querySelectorAll(`[data-n="${n}"]`).forEach(x => x.classList.add('ck-on'));
      const det = box.querySelector('.ck-notes'); if (det) det.open = true;
    }
  });
  const go = () => wire();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
  new MutationObserver(() => go()).observe(document.documentElement, { childList: true, subtree: true });
})();
