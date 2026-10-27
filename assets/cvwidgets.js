/* ===== Computer Vision animations, one block per chapter. The framework is assets/cvviz.js. ===== */
(() => {
  const { def, D, f, clamp } = CVZ;

  /* ---------------------------------------------------------------- Chapter 1: what vision is */
  def('pixels', {
    title: 'A picture is a grid of numbers',
    sub: 'Change the resolution and the number of bits. Click the picture to read one pixel.',
    W: 560, H: 250,
    params: [
      { k: 'w', label: 'Width in pixels', type: 'range', min: 6, max: 96, v: 24, help: 'The height is two thirds of the width.' },
      { k: 'mode', label: 'Colour', type: 'select', v: 'rgb', opts: [['rgb', 'Colour (3 numbers per pixel)'], ['gray', 'Grey (1 number per pixel)']] },
      { k: 'bits', label: 'Bits per number', type: 'range', min: 1, max: 8, v: 8, help: '8 bits give 256 levels, 1 bit gives only 2.' },
      { k: 'nums', label: 'Write the values in the cells', type: 'check', v: false }
    ],
    tips: [
      { t: 'Drop the width to 8. The house is still there, but only as blocks. This is why tiny images are hard to recognise.', set: { w: 8, nums: false } },
      { t: 'Turn on the values at width 12 in grey. This grid of numbers is all the computer ever receives.', set: { w: 12, mode: 'gray', nums: true, bits: 8 } },
      { t: 'Set 2 bits per number. Smooth sky turns into bands, because only 4 levels are left.', set: { bits: 2, w: 96, nums: false } },
      { t: 'Compare the memory line for width 96 in colour and in grey. Colour needs exactly three times as many numbers.', set: { w: 96, mode: 'rgb', bits: 8 } }
    ],
    init(z) { z.state.probe = null; },
    click(z, x, y) { z.state.probe = [x, y]; },
    draw(z) {
      const { g, p } = z;
      const w = p.w, h = Math.max(4, Math.round(w * 2 / 3));
      let img = CVZ.sceneRGB(w, h);
      const lv = 2 ** p.bits, q = v => Math.round(Math.round(v / 255 * (lv - 1)) * 255 / (lv - 1));
      img = img.map(r => r.map(c => c.map(q)));
      const gimg = CVZ.toGray(img).map(r => r.map(q));
      const show = p.mode === 'gray' ? gimg : img;
      const cell = Math.min(340 / w, 220 / h);
      const ox = 10, oy = 14;
      D.image(g, show, ox, oy, cell, { grid: cell >= 12 ? 'rgba(0,0,0,.25)' : null, vals: p.nums && cell >= 18 ? (v => Array.isArray(v) ? '' : String(v)) : null });
      if (p.nums && cell >= 18 && p.mode === 'rgb') D.text(g, 'Switch to grey to see one number per cell', ox, oy + h * cell + 16, { s: 12, c: z.col.ink2 });
      if (p.nums && cell < 18) D.text(g, 'Lower the width to fit the numbers in the cells', ox, oy + h * cell + 16, { s: 12, c: z.col.ink2 });
      let probe = '';
      if (z.state.probe) {
        const c = Math.floor((z.state.probe[0] - ox) / cell), r = Math.floor((z.state.probe[1] - oy) / cell);
        if (r >= 0 && r < h && c >= 0 && c < w) {
          D.rect(g, ox + c * cell, oy + r * cell, cell, cell, { stroke: z.col.red, w: 2.5 });
          const v = img[r][c];
          probe = p.mode === 'gray' ? `Pixel at row ${r}, column ${c}: grey value <b>${gimg[r][c]}</b>` : `Pixel at row ${r}, column ${c}: R <b>${v[0]}</b>, G <b>${v[1]}</b>, B <b>${v[2]}</b>`;
        }
      }
      const X = 368;
      D.text(g, 'What the computer stores', X, 30, { b: true, s: 14, c: z.col.ink });
      const C = p.mode === 'gray' ? 1 : 3, N = w * h * C;
      const lines = [`height H = ${h}`, `width W = ${w}`, `channels C = ${C}`, `numbers = ${N.toLocaleString()}`, `levels = 2^${p.bits} = ${lv}`, `bits = ${(N * p.bits).toLocaleString()}`, `bytes = ${f(N * p.bits / 8, 1)}`];
      lines.forEach((s, i) => D.text(g, s, X, 58 + i * 24, { mono: true, s: 13, c: z.col.ink2 }));
      return `<span class="big">numbers = H × W × C = ${h} × ${w} × ${C} = ${N.toLocaleString()}</span><br>Each number uses ${p.bits} bits, so it can take one of ${lv} values from 0 to ${lv - 1} (shown here rescaled to 0 to 255). ${probe}`;
    }
  });

  /* the template matching demo: what changes break a naive pixel comparison */
  function mug(u, v) {
    if (u >= -0.45 && u <= 0.22 && v >= -0.5 && v <= 0.5) return v < -0.38 ? 200 : 170;
    const d = Math.hypot(u - 0.24, v + 0.02);
    if (u > 0.22 && d > 0.13 && d < 0.27) return 170;
    return -1;
  }
  def('nuisance', {
    title: 'Why the same object can look different',
    sub: 'The left picture is the stored template. The right is what the camera sees today. Two match scores compare them.',
    W: 560, H: 300,
    params: [
      { k: 'bright', label: 'Lighting shift', type: 'range', min: -120, max: 120, v: 0 },
      { k: 'contrast', label: 'Contrast', type: 'range', min: 0.2, max: 2, step: 0.1, v: 1 },
      { k: 'rot', label: 'Rotation (degrees)', type: 'range', min: 0, max: 90, v: 0 },
      { k: 'scale', label: 'Scale (distance)', type: 'range', min: 0.5, max: 1.6, step: 0.05, v: 1 },
      { k: 'occ', label: 'Occlusion (% hidden)', type: 'range', min: 0, max: 80, v: 0 },
      { k: 'clutter', label: 'Background clutter', type: 'range', min: 0, max: 100, v: 0 }
    ],
    tips: [
      { t: 'Shift the lighting to 50. The raw difference jumps to 50, but the normalised score stays at 1, because normalising removes brightness and contrast.', set: { bright: 50, contrast: 1, rot: 0, scale: 1, occ: 0, clutter: 0 } },
      { t: 'Rotate the mug by 45 degrees with normal lighting. Now even the normalised score drops. Rotation is a viewpoint change that simple maths cannot undo.', set: { bright: 0, rot: 45, scale: 1, occ: 0, clutter: 0 } },
      { t: 'Hide 50% of the mug. A person still sees a mug. The score falls a lot.', set: { rot: 0, occ: 50, clutter: 0 } },
      { t: 'Add clutter of 80. The background no longer matches the plain template.', set: { occ: 0, clutter: 80, rot: 0 } }
    ],
    draw(z) {
      const { g, p } = z;
      const N = 48, cell = 4;
      const r = CVZ.rng(11);
      const bgTex = Array.from({ length: N }, () => Array.from({ length: N }, () => r()));
      const make = (alter) => {
        const a = alter ? p.rot * Math.PI / 180 : 0, s = alter ? p.scale : 1;
        const out = [];
        for (let y = 0; y < N; y++) {
          const row = [];
          for (let x = 0; x < N; x++) {
            let u = (x + 0.5) / N * 2 - 1, v = (y + 0.5) / N * 2 - 1;
            const ur = (Math.cos(a) * u + Math.sin(a) * v) / s, vr = (-Math.sin(a) * u + Math.cos(a) * v) / s;
            let val = mug(ur * 1.25, vr * 1.25);
            if (val < 0) val = alter && p.clutter ? 60 + (bgTex[y][x] - 0.5) * p.clutter * 3.2 + (((x >> 3) + (y >> 3)) % 2 ? p.clutter * 0.6 : 0) : 60;
            if (alter && p.occ && x >= N * (1 - p.occ / 100)) val = 120;
            if (alter) val = (val - 128) * p.contrast + 128 + p.bright;
            row.push(Math.round(clamp(val)));
          }
          out.push(row);
        }
        return out;
      };
      const T = make(false), I = make(true);
      D.text(g, 'Stored template', 20, 22, { b: true, c: z.col.ink });
      D.text(g, 'What the camera sees', 300, 22, { b: true, c: z.col.ink });
      D.image(g, T, 20, 32, cell);
      D.image(g, I, 300, 32, cell);
      let sad = 0, mt = 0, mi = 0;
      const n = N * N;
      for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) { sad += Math.abs(T[y][x] - I[y][x]); mt += T[y][x]; mi += I[y][x]; }
      mt /= n; mi /= n;
      let num = 0, dt = 0, di = 0;
      for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) { const a = T[y][x] - mt, b = I[y][x] - mi; num += a * b; dt += a * a; di += b * b; }
      const ncc = di && dt ? num / Math.sqrt(dt * di) : 0;
      const mad = sad / n;
      const ok = ncc >= 0.8;
      D.text(g, `Mean absolute difference ${f(mad, 1)} (0 is a perfect match)`, 20, 252, { s: 13, c: z.col.ink2 });
      D.text(g, `Normalised correlation ${f(ncc, 3)} (1 is a perfect match)`, 20, 274, { s: 13, c: ok ? z.col.green : z.col.red, b: true });
      return `<span class="big">NCC = Σ (T − T̄)(I − Ī) ÷ √( Σ (T − T̄)² · Σ (I − Ī)² )</span><br>With a threshold of 0.8 the matcher says: <span class="${ok ? 'good' : 'bad'}">${ok ? 'same object' : 'not the same object'}</span>. Subtracting the mean and dividing by the spread makes the score blind to lighting and contrast, but not to rotation, scale, occlusion or clutter. Those need features or learning.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 2: Marr, edges and features */
  const PATTERNS = {
    vedge: (r, c) => c < 4 ? 40 : 210,
    hedge: (r, c) => r < 4 ? 210 : 40,
    diag: (r, c) => r + c < 8 ? 40 : 210,
    corner: (r, c) => r >= 4 && c >= 4 ? 220 : 40,
    ramp: (r, c) => 30 + c * 25,
    blob: (r, c) => Math.hypot(r - 4, c - 4) < 2.6 ? 230 : 50,
    flat: () => 120
  };
  const PAT_OPTS = [['vedge', 'Vertical edge'], ['hedge', 'Horizontal edge'], ['diag', 'Diagonal edge'], ['corner', 'Corner'], ['ramp', 'Smooth ramp'], ['blob', 'Bright blob'], ['flat', 'Flat region']];
  const OPS = {
    sobel: [[[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]],
    prewitt: [[[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]],
    central: [[[0, 0, 0], [-1, 0, 1], [0, 0, 0]], [[0, -1, 0], [0, 0, 0], [0, 1, 0]]]
  };
  def('gradient', {
    title: 'Image gradients: where and which way the brightness changes',
    sub: 'Each arrow points from dark to bright. Its length is the gradient magnitude. Click a pixel to see the sums.',
    W: 560, H: 330,
    params: [
      { k: 'pat', label: 'Patch', type: 'select', v: 'vedge', opts: PAT_OPTS },
      { k: 'op', label: 'Operator', type: 'select', v: 'sobel', opts: [['sobel', 'Sobel'], ['prewitt', 'Prewitt'], ['central', 'Central difference']] },
      { k: 'noise', label: 'Noise', type: 'range', min: 0, max: 60, v: 0 },
      { k: 'thr', label: 'Hide arrows below magnitude', type: 'range', min: 0, max: 400, step: 10, v: 30 }
    ],
    tips: [
      { t: 'Pick Vertical edge. All arrows point right and none point up, because brightness only changes from left to right.', set: { pat: 'vedge', noise: 0 } },
      { t: 'Pick Corner. Arrows near the corner point two ways. Corners are good keypoints because they are unique in both directions.', set: { pat: 'corner', noise: 0 } },
      { t: 'Pick Flat region and add noise of 40. Small random arrows appear everywhere. Raise the threshold until they vanish.', set: { pat: 'flat', noise: 40, thr: 30 } },
      { t: 'Compare Sobel with Central difference on a noisy edge. Sobel averages three rows, so it is less upset by noise.', set: { pat: 'vedge', noise: 30, op: 'central' } }
    ],
    init(z) { z.state.sel = [4, 4]; },
    click(z, x, y) { const c = Math.floor((x - 10) / 34), r = Math.floor((y - 10) / 34); if (r >= 0 && r < 9 && c >= 0 && c < 9) z.state.sel = [r, c]; },
    draw(z) {
      const { g, p } = z;
      const rr = CVZ.rng(5);
      const img = Array.from({ length: 9 }, (_, r) => Array.from({ length: 9 }, (_, c) => Math.round(clamp(PATTERNS[p.pat](r, c) + CVZ.gauss(rr) * p.noise))));
      const [kx, ky] = OPS[p.op];
      const gx = CVZ.convolve(img, kx, 'replicate', true), gy = CVZ.convolve(img, ky, 'replicate', true);
      const cell = 34;
      D.image(g, img, 10, 10, cell, { grid: 'rgba(0,0,0,.2)', vals: true, fs: 10 });
      let mx = 1;
      gx.forEach((row, r) => row.forEach((v, c) => { mx = Math.max(mx, Math.hypot(v, gy[r][c])); }));
      gx.forEach((row, r) => row.forEach((v, c) => {
        const m = Math.hypot(v, gy[r][c]);
        if (m < p.thr || m === 0) return;
        const L = 15 * m / mx, cx = 10 + (c + 0.5) * cell, cy = 10 + (r + 0.5) * cell;
        D.arrow(g, cx, cy, cx + v / m * L, cy + gy[r][c] / m * L, z.col.red, 2, 6);
      }));
      const [sr, sc] = z.state.sel;
      D.rect(g, 10 + (sc - 1) * cell, 10 + (sr - 1) * cell, 3 * cell, 3 * cell, { stroke: z.col.orange, w: 2.5 });
      const X = 330;
      D.text(g, `Pixel row ${sr}, column ${sc}`, X, 24, { b: true, c: z.col.ink });
      const nb = [-1, 0, 1].map(i => [-1, 0, 1].map(j => CVZ.D && img[clamp(sr + i, 0, 8)][clamp(sc + j, 0, 8)]));
      D.image(g, nb, X, 36, 30, { grid: 'rgba(0,0,0,.25)', vals: true, fs: 10 });
      D.text(g, 'Gx kernel', X + 100, 50, { s: 11, c: z.col.ink2 });
      kx.forEach((row, i) => D.text(g, row.map(v => String(v).padStart(2)).join(' '), X + 100, 66 + i * 14, { mono: true, s: 11, c: z.col.ink }));
      D.text(g, 'Gy kernel', X + 172, 50, { s: 11, c: z.col.ink2 });
      ky.forEach((row, i) => D.text(g, row.map(v => String(v).padStart(2)).join(' '), X + 172, 66 + i * 14, { mono: true, s: 11, c: z.col.ink }));
      const Gx = gx[sr][sc], Gy = gy[sr][sc], M = Math.hypot(Gx, Gy), A = Math.atan2(Gy, Gx) * 180 / Math.PI;
      [`Gx = ${Gx}`, `Gy = ${Gy}`, `|G| = ${f(M, 1)}`, `θ = ${M ? f(A, 1) + '°' : 'undefined'}`].forEach((t, i) => D.text(g, t, X, 152 + i * 22, { mono: true, s: 13, c: z.col.ink }));
      D.text(g, 'θ is measured from the +x axis,', X, 250, { s: 11, c: z.col.ink2 });
      D.text(g, 'with y pointing down the image.', X, 264, { s: 11, c: z.col.ink2 });
      return `<span class="big">|G| = √(G<sub>x</sub>² + G<sub>y</sub>²) = √(${Gx}² + ${Gy}²) = ${f(M, 2)}, θ = atan2(G<sub>y</sub>, G<sub>x</sub>) = ${M ? f(A, 1) + '°' : 'undefined (no change)'}</span><br>G<sub>x</sub> is the sum of the 3 × 3 neighbourhood times the G<sub>x</sub> kernel, value by value. A big magnitude means a strong edge. The direction is across the edge, not along it.`;
    }
  });

  /* HOG on a small person-like silhouette */
  function personImg(W, H, lean) {
    const img = [];
    for (let y = 0; y < H; y++) {
      const row = [];
      for (let x = 0; x < W; x++) {
        const u = x / W - 0.5 - lean * (y / H - 0.5) * 0.3, v = y / H;
        let val = 70;
        if (Math.hypot(u * 1.4, v - 0.13) < 0.075) val = 200;
        if (v > 0.2 && v < 0.58 && Math.abs(u) < 0.13 + (v < 0.28 ? (v - 0.2) * 1.2 : 0.1)) val = 190;
        if (v >= 0.56 && v < 0.95 && Math.abs(Math.abs(u) - 0.05 - (v - 0.56) * 0.25) < 0.06) val = 185;
        row.push(val);
      }
      img.push(row);
    }
    return img;
  }
  def('hog', {
    title: 'HOG: a histogram of edge directions in every cell',
    sub: 'The window is cut into cells. Each cell votes its gradient directions into bins, weighted by magnitude. Click a cell to see its histogram.',
    W: 560, H: 340,
    params: [
      { k: 'cell', label: 'Cell size (pixels)', type: 'select', v: 8, num: true, opts: [[4, '4 × 4'], [8, '8 × 8'], [16, '16 × 16']] },
      { k: 'bins', label: 'Orientation bins', type: 'range', min: 4, max: 18, v: 9 },
      { k: 'signed', label: 'Signed directions (0 to 360°)', type: 'check', v: false },
      { k: 'lean', label: 'Pose: lean of the person', type: 'range', min: -1, max: 1, step: 0.1, v: 0 },
      { k: 'contrast', label: 'Contrast', type: 'range', min: 0.2, max: 2, step: 0.1, v: 1 }
    ],
    tips: [
      { t: 'Keep the classic setting from the paper: 8 × 8 cells and 9 unsigned bins. The descriptor for a 64 × 128 window has 3,780 numbers.', set: { cell: 8, bins: 9, signed: false } },
      { t: 'Lower the contrast to 0.3. The glyphs get shorter but keep their shape, and block normalisation in real HOG removes this change.', set: { contrast: 0.3 } },
      { t: 'Lean the person to 1. The glyphs change. HOG is not invariant to pose, which is why it struggles with people sitting or bending.', set: { lean: 1, contrast: 1 } },
      { t: 'Use 4 × 4 cells. You get finer detail but a much longer descriptor. Check the length in the readout.', set: { cell: 4, lean: 0 } }
    ],
    init(z) { z.state.sel = null; },
    click(z, x, y) { z.state.click = [x, y]; },
    draw(z) {
      const { g, p } = z;
      const Wd = 64, Ht = 128, S = 2.4;
      let img = personImg(Wd, Ht, p.lean).map(r => r.map(v => clamp((v - 128) * p.contrast + 128)));
      const { gx, gy } = CVZ.sobel(img);
      const ox = 10, oy = 12;
      D.image(g, img, ox, oy, S);
      const cs = +p.cell, nx = Wd / cs, ny = Ht / cs, B = p.bins, span = p.signed ? 360 : 180;
      if (z.state.click) {
        const c = Math.floor((z.state.click[0] - ox) / (cs * S)), r = Math.floor((z.state.click[1] - oy) / (cs * S));
        if (r >= 0 && r < ny && c >= 0 && c < nx) z.state.sel = [r, c];
        z.state.click = null;
      }
      
      const H2 = [];
      let gmax = 1e-9;
      for (let r = 0; r < ny; r++) {
        const row = [];
        for (let c = 0; c < nx; c++) {
          const h = new Array(B).fill(0);
          for (let y = r * cs; y < (r + 1) * cs; y++) for (let x = c * cs; x < (c + 1) * cs; x++) {
            const m = Math.hypot(gx[y][x], gy[y][x]);
            if (!m) continue;
            let a = Math.atan2(gy[y][x], gx[y][x]) * 180 / Math.PI;
            a = ((a % span) + span) % span;
            const pos = a / (span / B) - 0.5, b0 = Math.floor(pos), t = pos - b0;
            h[(b0 + B) % B] += m * (1 - t); h[(b0 + 1) % B] += m * t;
          }
          h.forEach(v => { gmax = Math.max(gmax, v); });
          row.push(h);
        }
        H2.push(row);
      }
      if (!z.state.sel || z.state.sel[0] >= ny || z.state.sel[1] >= nx) {
        let best = -1;
        H2.forEach((row, r) => row.forEach((h, c) => { const t = h.reduce((a, b) => a + b, 0); if (t > best) { best = t; z.state.sel = [r, c]; } }));
      }
      const gx0 = 190;
      D.rect(g, gx0, oy, Wd * S, Ht * S, { fill: '#0b1a2e' });
      for (let r = 0; r < ny; r++) for (let c = 0; c < nx; c++) {
        const cx = gx0 + (c + 0.5) * cs * S, cy = oy + (r + 0.5) * cs * S, L = cs * S * 0.48;
        H2[r][c].forEach((v, b) => {
          const ang = ((b + 0.5) * span / B + 90) * Math.PI / 180;
          const k = v / gmax;
          if (k < 0.03) return;
          D.line(g, cx - Math.cos(ang) * L * (p.signed ? 0 : 1), cy - Math.sin(ang) * L * (p.signed ? 0 : 1), cx + Math.cos(ang) * L, cy + Math.sin(ang) * L, `rgba(255,255,255,${Math.min(1, k * 1.3)})`, 1.3);
        });
      }
      const [sr, sc] = z.state.sel;
      [ox, gx0].forEach(X => D.rect(g, X + sc * cs * S, oy + sr * cs * S, cs * S, cs * S, { stroke: z.col.orange, w: 2 }));
      for (let c = 1; c < nx; c++) D.line(g, ox + c * cs * S, oy, ox + c * cs * S, oy + Ht * S, 'rgba(255,255,255,.25)', 0.7);
      for (let r = 1; r < ny; r++) D.line(g, ox, oy + r * cs * S, ox + Wd * S, oy + r * cs * S, 'rgba(255,255,255,.25)', 0.7);
      D.text(g, 'Image and cells', ox, Ht * S + oy + 14 > z.H ? z.H - 2 : Ht * S + oy + 14, { s: 11, c: z.col.ink2 });
      const hx = 370, hy = 40;
      D.text(g, `Histogram of cell (${sr}, ${sc})`, hx, 28, { b: true, c: z.col.ink });
      D.bars(g, z, [hx, hy, 180, 140], H2[sr][sc], { max: Math.max(...H2[sr][sc], 1e-9) });
      for (let b = 0; b < B; b += Math.ceil(B / 6)) D.text(g, Math.round(b * span / B) + '°', hx + (b + 0.5) * 180 / B, hy + 154, { a: 'center', s: 10, c: z.col.ink2 });
      const bx = 64 / cs - 1, by = 128 / cs - 1, len = bx * by * 4 * B;
      D.text(g, `Blocks of 2 × 2 cells: ${bx} × ${by} = ${bx * by}`, hx, 225, { s: 12, c: z.col.ink });
      D.text(g, `Numbers per block: 4 × ${B} = ${4 * B}`, hx, 245, { s: 12, c: z.col.ink });
      D.text(g, `Descriptor length: ${len.toLocaleString()}`, hx, 265, { s: 12, b: true, c: z.col.cv });
      return `<span class="big">length = (${64 / cs} − 1) × (${128 / cs} − 1) blocks × 4 cells × ${B} bins = ${len.toLocaleString()}</span><br>Each pixel votes into the two nearest bins, split by how close its angle is to each bin centre, with a weight equal to its gradient magnitude. ${p.signed ? 'Signed bins keep dark to bright and bright to dark apart.' : 'Unsigned bins treat an angle and the angle plus 180° as the same, so a dark coat on a light wall and a light coat on a dark wall give the same glyph.'}`;
    }
  });

  def('scalespace', {
    title: 'Finding the right scale: the blob detector inside SIFT',
    sub: 'A bright disc of radius r is blurred at many scales σ. The difference of two blurs (DoG) at the centre is plotted against σ. The peak tells the detector how big the blob is.',
    W: 560, H: 300,
    params: [
      { k: 'r', label: 'Blob radius r (pixels)', type: 'range', min: 2, max: 14, v: 6 },
      { k: 'k', label: 'Scale step k', type: 'range', min: 1.1, max: 2, step: 0.05, v: 1.6 }
    ],
    tips: [
      { t: 'Double the radius from 4 to 8. The peak moves to roughly double the σ. That is what makes the detector scale invariant.', set: { r: 8 } },
      { t: 'Set r to 4 and compare the peak with r ÷ √2 ≈ 2.83. For the Laplacian of Gaussian the theory predicts the peak at σ = r ÷ √2.', set: { r: 4 } },
      { t: 'Change k to 1.2 and then 2. The two blurs move, but measured at their middle scale √k σ the peak stays near r ÷ √2. That is why DoG can stand in for the Laplacian.', set: { k: 1.2 } }
    ],
    draw(z) {
      const { g, p } = z;
      const N = 61, c = 30, R = p.r;
      const disc = []; for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) if (Math.hypot(x - c, y - c) <= R) disc.push([x - c, y - c]);
      const G = (s, x, y) => Math.exp(-(x * x + y * y) / (2 * s * s)) / (2 * Math.PI * s * s);
      const sig = [], resp = [];
      for (let s = 0.6; s <= 14; s += 0.1) {
        let v = 0;
        for (const [x, y] of disc) v += G(s * p.k, x, y) - G(s, x, y);
        sig.push(s * Math.sqrt(p.k)); resp.push(-v / (p.k - 1));
      }
      let bi = 0; resp.forEach((v, i) => { if (v > resp[bi]) bi = i; });
      const m = D.axes(g, z, [60, 20, 330, 220], [0, 14], [Math.min(0, ...resp), Math.max(...resp) * 1.1], { xl: 'scale σ', yl: 'DoG response', fy: v => f(v, 2) });
      g.save(); g.strokeStyle = z.col.cv; g.lineWidth = 2.5; g.beginPath();
      sig.forEach((s, i) => { if (s > 14) return; if (i) g.lineTo(m.sx(s), m.sy(resp[i])); else g.moveTo(m.sx(s), m.sy(resp[i])); });
      g.stroke(); g.restore();
      D.line(g, m.sx(sig[bi]), 20, m.sx(sig[bi]), 240, z.col.orange, 1.5, [4, 4]);
      D.line(g, m.sx(R / Math.SQRT2), 20, m.sx(R / Math.SQRT2), 240, z.col.green, 1.5, [2, 3]);
      D.text(g, 'peak', m.sx(sig[bi]) + 4, 34, { s: 11, c: z.col.orange, b: true });
      D.text(g, 'r ÷ √2', m.sx(R / Math.SQRT2) + 4, 52, { s: 11, c: z.col.green, b: true });
      const cx = 470, cy = 110;
      D.circle(g, cx, cy, 60, { fill: '#0b1a2e' });
      D.circle(g, cx, cy, R * 4, { fill: '#f2f2f2' });
      D.circle(g, cx, cy, sig[bi] * Math.SQRT2 * 4, { stroke: z.col.orange, w: 2 });
      D.text(g, 'blob and the detected size', cx, 195, { a: 'center', s: 11, c: z.col.ink2 });
      return `<span class="big">DoG(x, y, σ) = G(x, y, kσ) ∗ I − G(x, y, σ) ∗ I ≈ (k − 1) σ² ∇²G ∗ I</span><br>Peak at σ = <b>${f(sig[bi], 2)}</b> (σ is the middle scale √k × σ<sub>1</sub> of the two blurs). The theory for the Laplacian of Gaussian gives r ÷ √2 = <b>${f(R / Math.SQRT2, 2)}</b>. The orange circle of radius √2 σ marks the size the detector reports.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 3: pixels, colour and compression */
  def('colour', {
    title: 'One colour, many colour models',
    sub: 'Mix a colour with red, green and blue light, then read it in the other models.',
    W: 560, H: 250,
    params: [
      { k: 'r', label: 'Red', type: 'range', min: 0, max: 255, v: 230 },
      { k: 'g', label: 'Green', type: 'range', min: 0, max: 255, v: 120 },
      { k: 'b', label: 'Blue', type: 'range', min: 0, max: 255, v: 40 }
    ],
    tips: [
      { t: 'Set all three to 255. Adding all lights gives white, which is why RGB is called additive.', set: { r: 255, g: 255, b: 255 } },
      { t: 'Set pure red. The "read as BGR" swatch turns blue. That is what happens when OpenCV data is shown without converting.', set: { r: 255, g: 0, b: 0 } },
      { t: 'Set pure green and pure blue in turn and watch the grey swatch. Green looks much brighter, so it gets the largest weight, 0.587.', set: { r: 0, g: 255, b: 0 } },
      { t: 'Set a grey such as 128, 128, 128. Saturation is 0, hue has no meaning, Cb and Cr sit at 128.', set: { r: 128, g: 128, b: 128 } }
    ],
    draw(z) {
      const { g, p } = z;
      const R = p.r, G = p.g, B = p.b;
      const r = R / 255, gg = G / 255, b = B / 255, mx = Math.max(r, gg, b), mn = Math.min(r, gg, b), d = mx - mn;
      const L = (mx + mn) / 2, S = d === 0 ? 0 : d / (1 - Math.abs(2 * L - 1));
      let H = 0;
      if (d) { if (mx === r) H = 60 * (((gg - b) / d) % 6); else if (mx === gg) H = 60 * ((b - r) / d + 2); else H = 60 * ((r - gg) / d + 4); }
      if (H < 0) H += 360;
      const K = 1 - mx, C = K < 1 ? (1 - r - K) / (1 - K) : 0, M = K < 1 ? (1 - gg - K) / (1 - K) : 0, Yk = K < 1 ? (1 - b - K) / (1 - K) : 0;
      const Y = 0.299 * R + 0.587 * G + 0.114 * B, Cb = 128 - 0.168736 * R - 0.331264 * G + 0.5 * B, Cr = 128 + 0.5 * R - 0.418688 * G - 0.081312 * B;
      const sw = (x, y, w, h, col, lab) => { D.rect(g, x, y, w, h, { fill: col, stroke: z.col.line, w: 1 }); D.text(g, lab, x + w / 2, y + h + 15, { a: 'center', s: 12, c: z.col.ink2, b: true }); };
      sw(16, 20, 130, 130, `rgb(${R},${G},${B})`, 'Your colour (RGB)');
      sw(166, 20, 80, 80, `rgb(${B},${G},${R})`, 'Read as BGR');
      sw(266, 20, 80, 80, `rgb(${Math.round(Y)},${Math.round(Y)},${Math.round(Y)})`, 'Grey (Y)');
      const ycc = (cb, cr) => { const yy = 128; return `rgb(${clamp(Math.round(yy + 1.402 * (cr - 128)))},${clamp(Math.round(yy - 0.344136 * (cb - 128) - 0.714136 * (cr - 128)))},${clamp(Math.round(yy + 1.772 * (cb - 128)))})`; };
      sw(366, 20, 80, 80, ycc(Cb, 128), 'Cb only');
      sw(466, 20, 80, 80, ycc(128, Cr), 'Cr only');
      const rows = [['RGB', `${R}, ${G}, ${B}`], ['HSL', `${f(H, 0)}°, ${f(S * 100, 0)}%, ${f(L * 100, 0)}%`], ['CMYK', `${f(C, 2)}, ${f(M, 2)}, ${f(Yk, 2)}, ${f(K, 2)}`], ['YCbCr', `${f(Y, 1)}, ${f(Cb, 1)}, ${f(Cr, 1)}`]];
      rows.forEach((rw, i) => { D.text(g, rw[0], 170, 150 + i * 24, { b: true, c: z.col.ink }); D.text(g, rw[1], 230, 150 + i * 24, { mono: true, c: z.col.ink2 }); });
      return `<span class="big">Y = 0.299 R + 0.587 G + 0.114 B = ${f(Y, 2)}</span><br>K = 1 − max(R′, G′, B′) = ${f(K, 3)}, C = (1 − R′ − K) ÷ (1 − K) = ${f(C, 3)} where R′ = R ÷ 255. Lightness L = (max + min) ÷ 2 = ${f(L, 3)}. JPEG keeps Y at full detail and shrinks Cb and Cr, because the eye is far more sensitive to brightness than to colour.`;
    }
  });

  const QTAB = [[16, 11, 10, 16, 24, 40, 51, 61], [12, 12, 14, 19, 26, 58, 60, 55], [14, 13, 16, 24, 40, 57, 69, 56], [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77], [24, 35, 55, 64, 81, 104, 113, 92], [49, 64, 78, 87, 103, 121, 120, 101], [72, 92, 95, 98, 112, 100, 103, 99]];
  const BLOCKS = {
    smooth: (r, c) => 90 + 8 * c + 5 * r,
    edge: (r, c) => c < 4 ? 60 : 190,
    texture: (r, c) => (r + c) % 2 ? 60 : 190,
    stripes: (r, c) => c % 4 < 2 ? 70 : 180,
    scene: (r, c) => (BLOCKS._s || (BLOCKS._s = CVZ.sceneGray(48, 32)))[12 + r][10 + c],
    flat: () => 140
  };
  const cosT = Array.from({ length: 8 }, (_, x) => Array.from({ length: 8 }, (_, u) => Math.cos((2 * x + 1) * u * Math.PI / 16)));
  const Cu = u => u === 0 ? Math.SQRT1_2 : 1;
  function dct2(b) { return Array.from({ length: 8 }, (_, v) => Array.from({ length: 8 }, (_, u) => { let s = 0; for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) s += (b[y][x] - 128) * cosT[x][u] * cosT[y][v]; return 0.25 * Cu(u) * Cu(v) * s; })); }
  function idct2(F) { return Array.from({ length: 8 }, (_, y) => Array.from({ length: 8 }, (_, x) => { let s = 0; for (let v = 0; v < 8; v++) for (let u = 0; u < 8; u++) s += Cu(u) * Cu(v) * F[v][u] * cosT[x][u] * cosT[y][v]; return clamp(Math.round(0.25 * s + 128)); })); }
  def('dct', {
    title: 'JPEG on one 8 × 8 block',
    sub: 'The block is turned into 64 frequency coefficients, divided by the quantisation table and rounded. Lower quality means bigger divisors and more zeros.',
    W: 560, H: 250,
    params: [
      { k: 'blk', label: 'Block', type: 'select', v: 'scene', opts: [['scene', 'Piece of a photo'], ['smooth', 'Smooth gradient'], ['edge', 'Sharp edge'], ['stripes', 'Stripes'], ['texture', 'Fine checkerboard'], ['flat', 'Flat grey']] },
      { k: 'q', label: 'JPEG quality', type: 'range', min: 1, max: 100, v: 50 }
    ],
    tips: [
      { t: 'Pick Smooth gradient at quality 50. Only a handful of coefficients survive, yet the block comes back almost perfect. Smooth areas compress very well.', set: { blk: 'smooth', q: 50 } },
      { t: 'Pick Fine checkerboard at quality 20. The pattern lives in the highest frequencies, which are divided by large numbers, so it is wiped out.', set: { blk: 'texture', q: 20 } },
      { t: 'Pick Sharp edge at quality 10. Look for ripples beside the edge in the output. These are the ringing artefacts the notes mention.', set: { blk: 'edge', q: 10 } },
      { t: 'Pick Flat grey. Only the top left (DC) coefficient is non zero. It equals 8 times the average after subtracting 128.', set: { blk: 'flat', q: 50 } }
    ],
    draw(z) {
      const { g, p } = z;
      const b = Array.from({ length: 8 }, (_, r) => Array.from({ length: 8 }, (_, c) => Math.round(BLOCKS[p.blk](r, c))));
      const sc = p.q < 50 ? 5000 / p.q : 200 - 2 * p.q;
      const Q = QTAB.map(r => r.map(v => clamp(Math.floor((v * sc + 50) / 100), 1, 255)));
      const F = dct2(b), Fq = F.map((r, v) => r.map((x, u) => Math.round(x / Q[v][u])));
      const R = idct2(Fq.map((r, v) => r.map((x, u) => x * Q[v][u])));
      const cell = 22, y0 = 26;
      D.text(g, 'Original block', 10, 16, { b: true, s: 12, c: z.col.ink });
      D.image(g, b, 10, y0, cell);
      D.text(g, 'Quantised coefficients', 196, 16, { b: true, s: 12, c: z.col.ink });
      let nz = 0;
      for (let v = 0; v < 8; v++) for (let u = 0; u < 8; u++) {
        const x = Fq[v][u]; if (x) nz++;
        D.rect(g, 196 + u * cell, y0 + v * cell, cell, cell, { fill: x ? (x > 0 ? 'rgba(14,116,144,.35)' : 'rgba(233,72,90,.35)') : z.col.surf, stroke: z.col.line, w: 0.6 });
        D.text(g, String(x), 196 + (u + 0.5) * cell, y0 + (v + 0.5) * cell + 4, { a: 'center', s: 10, mono: true, c: x ? z.col.ink : z.col.ink2 });
      }
      D.text(g, 'After decoding', 382, 16, { b: true, s: 12, c: z.col.ink });
      D.image(g, R, 382, y0, cell);
      let err = 0, mse = 0;
      b.forEach((r, i) => r.forEach((v, j) => { const e = Math.abs(v - R[i][j]); err = Math.max(err, e); mse += e * e; }));
      mse /= 64;
      const ps = mse ? 10 * Math.log10(255 * 255 / mse) : Infinity;
      D.text(g, `${nz} of 64 coefficients kept`, 196, 224, { s: 12, b: true, c: z.col.cv });
      D.text(g, `largest pixel error ${err}`, 382, 224, { s: 12, c: z.col.ink2 });
      return `<span class="big">F(u, v) = ¼ C(u) C(v) Σ<sub>x</sub> Σ<sub>y</sub> (f(x, y) − 128) cos((2x + 1)uπ ÷ 16) cos((2y + 1)vπ ÷ 16), &nbsp; F<sub>q</sub> = round(F ÷ Q)</span><br>DC coefficient F(0, 0) = ${f(F[0][0], 1)}, quantised with Q(0, 0) = ${Q[0][0]} to ${Fq[0][0]}. Quality ${p.q} scales the standard table by ${f(sc, 0)}%. PSNR of the decoded block: ${isFinite(ps) ? f(ps, 1) + ' dB' : 'perfect'}. Zeros are cheap to store, so fewer kept coefficients means a smaller file.`;
    }
  });

  def('gop', {
    title: 'I, P and B frames: size against delay',
    sub: 'Type a group of pictures. Arrows show which frames each one is predicted from. B frames need a future frame, so the decoder has to wait.',
    W: 560, H: 245,
    params: [
      { k: 'pat', label: 'Frame pattern (I, P, B)', type: 'text', v: 'IBBPBBPBBPBB' },
      { k: 'si', label: 'I frame size (KB)', type: 'range', min: 20, max: 200, v: 80 },
      { k: 'sp', label: 'P frame size (KB)', type: 'range', min: 5, max: 100, v: 25 },
      { k: 'sb', label: 'B frame size (KB)', type: 'range', min: 2, max: 60, v: 10 },
      { k: 'fps', label: 'Frames per second', type: 'range', min: 10, max: 60, v: 30 }
    ],
    tips: [
      { t: 'Type IIIIIIIIIIII. Every frame is a full picture. Easy to seek and robust to errors, but the stream is huge.', set: { pat: 'IIIIIIIIIIII' } },
      { t: 'Type IPPPPPPPPPPP. This is what a video call uses: much smaller than all I frames and no waiting for the future.', set: { pat: 'IPPPPPPPPPPP' } },
      { t: 'Type IBBBBBBBBBBP. The stream shrinks again, but the decoder must hold ten frames before it can show the first B frame.', set: { pat: 'IBBBBBBBBBBP' } }
    ],
    draw(z) {
      const { g, p } = z;
      const pat = (String(p.pat).toUpperCase().replace(/[^IPB]/g, '') || 'I').slice(0, 24);
      const n = pat.length, w = Math.min(40, (z.W - 20) / n), y = 145;
      const size = { I: p.si, P: p.sp, B: p.sb }, colr = { I: z.col.cv, P: z.col.orange, B: z.col.purple };
      const refs = [...pat].map((t, i) => i).filter(i => pat[i] !== 'B');
      for (let i = 0; i < n; i++) {
        const t = pat[i], x = 10 + i * w;
        const h = 20 + 60 * size[t] / Math.max(p.si, p.sp, p.sb);
        D.rect(g, x + 3, y - h, w - 6, h, { fill: colr[t] });
        D.text(g, t, x + w / 2, y + 16, { a: 'center', b: true, c: z.col.ink });
        D.text(g, String(i + 1), x + w / 2, y + 30, { a: 'center', s: 10, c: z.col.ink2 });
        const prev = refs.filter(j => j < i).pop(), next = refs.find(j => j > i);
        const arc = (j, c) => { const x1 = 10 + j * w + w / 2, x2 = x + w / 2; g.save(); g.strokeStyle = c; g.lineWidth = 1.3; g.beginPath(); g.moveTo(x1, y + 36); g.quadraticCurveTo((x1 + x2) / 2, y + 36 + Math.min(40, Math.abs(x2 - x1) * 0.4), x2, y + 36); g.stroke(); g.restore(); D.circle(g, x2, y + 36, 2.5, { fill: c }); };
        if (t === 'P' && prev !== undefined) arc(prev, z.col.orange);
        if (t === 'B') { if (prev !== undefined) arc(prev, z.col.purple); if (next !== undefined) arc(next, z.col.purple); }
      }
      let run = 0, best = 0;
      for (const t of pat) { run = t === 'B' ? run + 1 : 0; best = Math.max(best, run); }
      const total = [...pat].reduce((a, t) => a + size[t], 0), allI = n * p.si;
      const broken = pat.endsWith('B') ? ' The pattern ends with B frames that have no future reference, so in a real stream they wait for the next group.' : '';
      D.text(g, `Average ${f(total / n, 1)} KB per frame, ${f(allI / total, 2)}× smaller than all I frames`, 10, 20, { b: true, s: 13, c: z.col.ink });
      D.text(g, `Longest run of B frames: ${best}, extra delay about ${f(best * 1000 / p.fps, 1)} ms`, 10, 40, { s: 13, c: best ? z.col.red : z.col.green, b: true });
      return `<span class="big">average size = (n<sub>I</sub>·s<sub>I</sub> + n<sub>P</sub>·s<sub>P</sub> + n<sub>B</sub>·s<sub>B</sub>) ÷ n = ${f(total, 1)} ÷ ${n} = ${f(total / n, 2)} KB</span><br>Bit rate at ${p.fps} frames per second is about ${f(total / n * p.fps * 8 / 1000, 2)} Mbit/s. A B frame cannot be shown until the next I or P frame has arrived and been decoded, so each B in a row adds one frame time (${f(1000 / p.fps, 1)} ms) of waiting.${broken}`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 4: histograms and point operations */
  function exposed(kind) {
    const base = CVZ.sceneGray(96, 64);
    if (kind === 'under') return base.map(r => r.map(v => Math.round(v * 0.32 + 8)));
    if (kind === 'over') return base.map(r => r.map(v => Math.round(clamp(v * 0.35 + 170))));
    if (kind === 'flat') return base.map(r => r.map(v => Math.round(v * 0.25 + 90)));
    return base;
  }
  function eqMap(img, L = 256) {
    const h = CVZ.hist(img, L, L), N = img.length * img[0].length;
    let c = 0; const cdf = h.map(v => (c += v) / N);
    const cmin = cdf.find(v => v > 0);
    return cdf.map(v => cmin >= 1 ? 0 : Math.round(Math.max(0, (v - cmin) / (1 - cmin)) * (L - 1)));
  }
  def('pointops', {
    title: 'Point operations and the histogram',
    sub: 'Each output pixel depends only on the input pixel at the same place. The curve is the mapping, the bars are the histograms before and after. The dials change with the operation you pick.',
    W: 560, H: 270,
    params: [
      { k: 'src', label: 'Input photo', type: 'select', v: 'flat', opts: [['flat', 'Low contrast (grey, foggy)'], ['under', 'Underexposed (too dark)'], ['over', 'Overexposed (washed out)'], ['normal', 'Well exposed']] },
      { k: 'op', label: 'Operation', type: 'select', v: 'linear', opts: [['linear', 'Contrast and brightness g = αf + β'], ['neg', 'Negative g = 255 − f'], ['log', 'Log s = c log(1 + r)'], ['gamma', 'Gamma s = 255 (r ÷ 255)^γ'], ['slice', 'Grey level slicing [A, B]'], ['eq', 'Histogram equalisation']] },
      { k: 'a', label: 'Contrast α', type: 'range', min: 0.2, max: 4, step: 0.1, v: 1, show: p => p.op === 'linear' },
      { k: 'b', label: 'Brightness β', type: 'range', min: -250, max: 150, v: 0, show: p => p.op === 'linear' },
      { k: 'gam', label: 'Gamma γ', type: 'range', min: 0.2, max: 3, step: 0.1, v: 1, show: p => p.op === 'gamma' },
      { k: 'A', label: 'Slice from A', type: 'range', min: 0, max: 255, v: 100, show: p => p.op === 'slice' },
      { k: 'B', label: 'Slice to B', type: 'range', min: 0, max: 255, v: 160, show: p => p.op === 'slice' },
      { k: 'keep', label: 'Slicing keeps the background', type: 'check', v: false, show: p => p.op === 'slice' }
    ],
    tips: [
      { t: 'Pick the low contrast photo and set α = 3 and β = −220. The narrow histogram stretches across most of the range.', set: { src: 'flat', op: 'linear', a: 3, b: -220 } },
      { t: 'Underexposed photo with Log. Dark values are lifted a lot and bright ones only a little, so shadow detail appears.', set: { src: 'under', op: 'log' } },
      { t: 'Underexposed photo with Gamma 0.4. Similar effect to log, with γ as the dial. Gamma above 1 darkens instead.', set: { src: 'under', op: 'gamma', gam: 0.4 } },
      { t: 'Low contrast photo with Histogram equalisation. No dials needed, the CDF decides the curve.', set: { src: 'flat', op: 'eq' } },
      { t: 'Well exposed photo with slicing A = 150 and B = 200. Only that band of greys stays bright, as when highlighting tissue in a scan.', set: { src: 'normal', op: 'slice', A: 150, B: 200, keep: false } }
    ],
    draw(z) {
      const { g, p } = z;
      const img = exposed(p.src);
      let map;
      if (p.op === 'linear') map = v => clamp(Math.round(p.a * v + p.b));
      else if (p.op === 'neg') map = v => 255 - v;
      else if (p.op === 'log') { const c = 255 / Math.log(256); map = v => Math.round(c * Math.log(1 + v)); }
      else if (p.op === 'gamma') map = v => Math.round(255 * Math.pow(v / 255, p.gam));
      else if (p.op === 'slice') map = v => v >= Math.min(p.A, p.B) && v <= Math.max(p.A, p.B) ? 255 : (p.keep ? v : 20);
      else { const m = eqMap(img); map = v => m[v]; }
      const out = img.map(r => r.map(map));
      D.image(g, img, 10, 10, 1.75);
      D.image(g, out, 186, 10, 1.75);
      D.text(g, 'Input', 10, 136, { s: 11, c: z.col.ink2, b: true });
      D.text(g, 'Output', 186, 136, { s: 11, c: z.col.ink2, b: true });
      const h1 = CVZ.hist(img, 64), h2 = CVZ.hist(out, 64), mx = Math.max(...h1, ...h2);
      D.bars(g, z, [10, 150, 168, 70], h1, { max: mx, gap: 0.2 });
      D.bars(g, z, [186, 150, 168, 70], h2, { max: mx, gap: 0.2, colour: () => z.col.orange });
      D.text(g, '0', 10, 234, { s: 10, c: z.col.ink2 }); D.text(g, '255', 178, 234, { s: 10, c: z.col.ink2, a: 'right' });
      D.text(g, '0', 186, 234, { s: 10, c: z.col.ink2 }); D.text(g, '255', 354, 234, { s: 10, c: z.col.ink2, a: 'right' });
      const m = D.axes(g, z, [400, 20, 140, 140], [0, 255], [0, 255], { nx: 2, ny: 2, xl: 'input r', fx: v => Math.round(v), fy: v => Math.round(v) });
      D.line(g, m.sx(0), m.sy(0), m.sx(255), m.sy(255), z.col.line, 1, [3, 3]);
      g.save(); g.strokeStyle = z.col.cv; g.lineWidth = 2.2; g.beginPath();
      for (let v = 0; v <= 255; v++) { const y = map(v); if (v) g.lineTo(m.sx(v), m.sy(y)); else g.moveTo(m.sx(v), m.sy(y)); }
      g.stroke(); g.restore();
      const stat = a => { let s = 0, s2 = 0, n = 0; const seen = new Set(); a.forEach(r => r.forEach(v => { s += v; s2 += v * v; n++; seen.add(v); })); const mu = s / n; return [mu, Math.sqrt(Math.max(0, s2 / n - mu * mu)), seen.size]; };
      const [b1, c1, d1] = stat(img), [b2, c2, d2] = stat(out);
      [`brightness ${f(b1, 1)} → ${f(b2, 1)}`, `contrast σ ${f(c1, 1)} → ${f(c2, 1)}`, `levels used ${d1} → ${d2}`].forEach((t, i) => D.text(g, t, 400, 210 + i * 20, { s: 12, mono: true, c: z.col.ink }));
      return `Brightness is the mean B(I) = (1 ÷ wh) Σ Σ I(u, v). Contrast here is the standard deviation σ, the spread of the histogram. Levels used is the dynamic range. ${p.op === 'linear' && (p.a * 0 + p.b < 0 || p.a * 255 + p.b > 255) ? 'Values pushed past 0 or 255 are clipped, and clipped detail is lost for good.' : ''}`;
    }
  });

  def('histeq', {
    title: 'Histogram equalisation, one step at a time',
    sub: 'Edit the small image (rows on separate lines). Press Play to compute the histogram, the probabilities, the CDF, the mapping and the result.',
    W: 560, H: 220,
    params: [
      { k: 'm', label: 'Image values (0 to 255)', type: 'area', v: '80 80 80 80\n100 100 100 100\n120 120 120 120\n140 140 140 140' }
    ],
    tips: [
      { t: 'The default is the lecture example. The four levels 80, 100, 120, 140 become 0, 85, 170, 255.', set: { m: '80 80 80 80\n100 100 100 100\n120 120 120 120\n140 140 140 140' }, play: true },
      { t: 'Make most pixels one value: 50 50 50 50 / 50 50 50 50 / 50 50 200 200 / 200 220 220 250. Popular values take a big share of the output range.', set: { m: '50 50 50 50\n50 50 50 50\n50 50 200 200\n200 220 220 250' }, play: true },
      { t: 'Try an image with only two values, 10 and 20. Equalisation sends them to 0 and 255, the strongest possible contrast.', set: { m: '10 10 20 20\n10 10 20 20' }, play: true }
    ],
    startAtZero: true,
    steps: () => 5,
    speed: () => 1100,
    draw(z) {
      const { g, p, step } = z;
      let img = CVZ.parseGrid(p.m).map(r => r.map(v => clamp(Math.round(v || 0))));
      const w = Math.max(...img.map(r => r.length));
      img = img.map(r => r.concat(new Array(w - r.length).fill(r[r.length - 1] || 0)));
      const N = img.length * w;
      const levels = [...new Set(img.flat())].sort((a, b) => a - b);
      const cnt = levels.map(l => img.flat().filter(v => v === l).length);
      let c = 0; const cdf = cnt.map(n => (c += n) / N), cmin = cdf[0];
      const s = cdf.map(v => cmin >= 1 ? 0 : Math.round((v - cmin) / (1 - cmin) * 255));
      const out = img.map(r => r.map(v => s[levels.indexOf(v)]));
      const cell = Math.min(34, 190 / Math.max(img.length, w));
      D.text(g, 'Input', 10, 14, { b: true, s: 12, c: z.col.ink });
      D.image(g, img, 10, 22, cell, { vals: true, grid: 'rgba(0,0,0,.2)', fs: 10 });
      if (step >= 5) { D.text(g, 'Equalised', 290, 14, { b: true, s: 12, c: z.col.ink }); D.image(g, out, 290, 22, cell, { vals: true, grid: 'rgba(0,0,0,.2)', fs: 10 }); }
      else D.text(g, 'The equalised image appears at step 5', 290, 40, { s: 12, c: z.col.ink2 });
      const row = (lab, arr, k) => `<tr><th>${lab}</th>${arr.map(v => `<td${k ? ' class="hi"' : ''}>${v}</td>`).join('')}</tr>`;
      let t = '<table>' + row('level r', levels, false);
      if (step >= 1) t += row('count h(r)', cnt, step === 1);
      if (step >= 2) t += row('p(r) = h ÷ ' + N, cnt.map(n => f(n / N, 4)), step === 2);
      if (step >= 3) t += row('CDF(r)', cdf.map(v => f(v, 4)), step === 3);
      if (step >= 4) t += row('s = round((CDF − ' + f(cmin, 4) + ') ÷ ' + f(1 - cmin, 4) + ' × 255)', s, step === 4);
      t += '</table>';
      const words = ['Press Play or Step.', 'Step 1: count how many pixels have each value.', `Step 2: divide each count by the number of pixels, ${N}.`, 'Step 3: add the probabilities up as you go. This running total is the CDF.', `Step 4: map each level with s = round[(CDF(r) − CDFmin) ÷ (1 − CDFmin) × 255], where CDFmin = ${f(cmin, 4)}.`, 'Step 5: replace every pixel with its new value.'];
      return `<b>${words[step]}</b>${t}`;
    }
  });

  def('samehist', {
    title: 'Same histogram, different pictures',
    sub: 'All three 8 × 8 pictures have 32 grey pixels and 32 white pixels, so their histograms are identical. A histogram tells you how many, never where.',
    W: 560, H: 230,
    params: [
      { k: 'seed', label: 'Shuffle the third picture', type: 'range', min: 1, max: 30, v: 1 }
    ],
    tips: [{ t: 'Move the shuffle slider. The third picture changes completely while its histogram stays the same, two bars of 32.', set: { seed: 17 } }],
    draw(z) {
      const { g, p } = z;
      const half = Array.from({ length: 8 }, (_, r) => Array.from({ length: 8 }, (_, c) => c < 4 ? 128 : 255));
      const check = Array.from({ length: 8 }, (_, r) => Array.from({ length: 8 }, (_, c) => (r + c) % 2 ? 128 : 255));
      const flat = [].concat(...half); const rr = CVZ.rng(p.seed * 97);
      for (let i = flat.length - 1; i > 0; i--) { const j = Math.floor(rr() * (i + 1)); [flat[i], flat[j]] = [flat[j], flat[i]]; }
      const shuf = Array.from({ length: 8 }, (_, r) => flat.slice(r * 8, r * 8 + 8));
      [half, check, shuf].forEach((im, i) => {
        const x = 20 + i * 180;
        D.image(g, im, x, 10, 16, { grid: 'rgba(0,0,0,.15)' });
        D.bars(g, z, [x + 20, 150, 90, 50], [32, 32], { max: 32, gap: 12 });
        D.text(g, '128', x + 42, 214, { a: 'center', s: 11, c: z.col.ink2 }); D.text(g, '255', x + 88, 214, { a: 'center', s: 11, c: z.col.ink2 });
      });
      return 'This is why histogram features are rarely used alone. HOG and the motion descriptors later on still use histograms, but over small cells, which brings back some information about where things are.';
    }
  });

  /* ---------------------------------------------------------------- Chapter 5: noise, convolution and filtering */
  def('noiselab', {
    title: 'Noise lab: match the filter to the noise',
    sub: 'Add a type of noise, then clean it with a filter. PSNR compares each picture with the clean original (higher is better).',
    W: 560, H: 200,
    params: [
      { k: 'noise', label: 'Noise type', type: 'select', v: 'saltpepper', opts: [['gaussian', 'Gaussian (additive)'], ['saltpepper', 'Salt and pepper (impulse)'], ['speckle', 'Speckle (multiplicative)'], ['poisson', 'Poisson (shot noise)']] },
      { k: 'amt', label: 'Noise amount', type: 'range', min: 0, max: 60, v: 20 },
      { k: 'filt', label: 'Filter', type: 'select', v: 'mean', opts: [['none', 'No filter'], ['mean', 'Mean (box)'], ['gauss', 'Gaussian'], ['median', 'Median']] },
      { k: 'size', label: 'Filter size', type: 'select', v: 3, num: true, opts: [[3, '3 × 3'], [5, '5 × 5'], [7, '7 × 7']] }
    ],
    tips: [
      { t: 'Salt and pepper with a mean filter leaves grey smudges. Switch to median and the dots vanish while edges stay sharp. Compare the PSNR.', set: { noise: 'saltpepper', amt: 20, filt: 'median', size: 3 } },
      { t: 'Gaussian noise with a Gaussian filter works well. Median also helps but slightly less. Averaging suits noise that is small and everywhere.', set: { noise: 'gaussian', amt: 25, filt: 'gauss', size: 5 } },
      { t: 'Use a 7 × 7 mean filter on light noise. The noise goes, but so do the roof edge and the window. Bigger is not always better.', set: { noise: 'gaussian', amt: 8, filt: 'mean', size: 7 } },
      { t: 'Speckle: look at the bright sky and the dark road. The bright parts are noisier, because the noise is multiplied by the signal.', set: { noise: 'speckle', amt: 40, filt: 'none' } }
    ],
    draw(z) {
      const { g, p } = z;
      const clean = CVZ.sceneGray(84, 56);
      const noisy = p.amt ? CVZ.noisy(clean, p.noise, p.amt, 3) : clean;
      const n = +p.size;
      let out = noisy;
      if (p.filt === 'mean') out = CVZ.convolve(noisy, Array.from({ length: n }, () => new Array(n).fill(1 / (n * n))));
      else if (p.filt === 'gauss') out = CVZ.convolve(noisy, CVZ.gaussKernel(n, 0));
      else if (p.filt === 'median') out = CVZ.median(noisy, n);
      const S = 2;
      [[clean, 'Clean original'], [noisy, 'Noisy'], [out, p.filt === 'none' ? 'No filter' : 'Filtered']].forEach((a, i) => {
        D.image(g, a[0], 10 + i * 182, 10, S);
        D.text(g, a[1], 10 + i * 182, 136, { b: true, s: 12, c: z.col.ink });
      });
      const p1 = CVZ.psnr(clean, noisy), p2 = CVZ.psnr(clean, out);
      const fm = v => isFinite(v) ? f(v, 2) + ' dB' : 'perfect';
      D.text(g, `PSNR ${fm(p1)}`, 192, 156, { s: 12, mono: true, c: z.col.ink2 });
      D.text(g, `PSNR ${fm(p2)}`, 374, 156, { s: 12, mono: true, c: p2 > p1 ? z.col.green : z.col.red, b: true });
      return `<span class="big">PSNR = 10 log<sub>10</sub>(255² ÷ MSE), &nbsp; MSE = (1 ÷ N) Σ (clean − result)²</span><br>${p.noise === 'speckle' ? 'Speckle is g = f(1 + n): the noise grows with the brightness.' : p.noise === 'saltpepper' ? 'Impulse noise forces a few pixels to 0 or 255. The median ignores such outliers.' : p.noise === 'poisson' ? 'Shot noise comes from counting photons. Its variance equals its mean, so it is worst in low light relative to the signal.' : 'Gaussian noise g = f + n adds a small random number to every pixel.'} Each 3 dB of PSNR is about half the squared error.`;
    }
  });

  const KERNELS = {
    box: [[1, 1, 1], [1, 1, 1], [1, 1, 1]].map(r => r.map(v => v / 9)),
    gauss: [[1, 2, 1], [2, 4, 2], [1, 2, 1]].map(r => r.map(v => v / 16)),
    sharpen: [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
    highpass: [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]].map(r => r.map(v => v / 9)),
    sobelx: [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
    identity: [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
  };
  const INPUTS = {
    edge: [[10, 10, 10, 90, 90, 90, 90], [10, 10, 10, 90, 90, 90, 90], [10, 10, 10, 90, 90, 90, 90], [10, 10, 10, 90, 90, 90, 90], [10, 10, 10, 90, 90, 90, 90], [10, 10, 10, 90, 90, 90, 90], [10, 10, 10, 90, 90, 90, 90]],
    spike: [[20, 20, 20, 20, 20, 20, 20], [20, 20, 20, 20, 20, 20, 20], [20, 20, 20, 20, 20, 20, 20], [20, 20, 20, 255, 20, 20, 20], [20, 20, 20, 20, 20, 20, 20], [20, 20, 20, 20, 20, 20, 20], [20, 20, 20, 20, 20, 20, 20]],
    lecture: [[10, 20, 10, 20, 10, 20, 10], [100, 20, 10, 20, 10, 20, 10], [10, 10, 20, 10, 20, 10, 20], [20, 10, 20, 10, 20, 10, 20], [10, 20, 10, 200, 10, 20, 10], [20, 10, 20, 10, 20, 10, 20], [10, 20, 10, 20, 10, 20, 10]]
  };
  def('conv', {
    title: 'Convolution, one output pixel at a time',
    sub: 'The kernel slides over the input. At each place, multiply the overlapping numbers and add them up. Press Play, or edit your own kernel.',
    W: 560, H: 310,
    params: [
      { k: 'inp', label: 'Input', type: 'select', v: 'edge', opts: [['edge', 'Vertical edge'], ['spike', 'One bright spike'], ['lecture', 'Noisy patch']] },
      { k: 'ker', label: 'Kernel', type: 'select', v: 'box', opts: [['box', 'Mean (box) 1/9'], ['gauss', 'Gaussian 1/16'], ['sharpen', 'Sharpen (notebook)'], ['highpass', 'High pass 1/9 (lecture)'], ['sobelx', 'Sobel x'], ['identity', 'Identity'], ['custom', 'My own kernel']] },
      { k: 'custom', label: 'My own kernel (3 rows)', type: 'area', v: '0 0 0\n0 2 0\n0 0 0', show: p => p.ker === 'custom' },
      { k: 'pad', label: 'Border', type: 'select', v: 'zero', opts: [['zero', 'Zero padding (same size)'], ['replicate', 'Replicate the edge (same size)'], ['valid', 'No padding (output shrinks)']] },
      { k: 'stride', label: 'Stride', type: 'select', v: 1, num: true, opts: [[1, '1'], [2, '2']] }
    ],
    tips: [
      { t: 'Vertical edge with the mean filter: the sharp jump from 10 to 90 becomes a ramp. Smoothing blurs edges.', set: { inp: 'edge', ker: 'box' }, play: true },
      { t: 'One bright spike with the identity kernel, then with the mean filter. A single spike spreads into a 3 × 3 square of 1/9 of its height.', set: { inp: 'spike', ker: 'box' } },
      { t: 'Vertical edge with the lecture high pass kernel. Flat areas give 0 and only the edge lights up, because its weights add to 0.', set: { inp: 'edge', ker: 'highpass' } },
      { t: 'Choose No padding and stride 2. The output shrinks to ((7 − 3) ÷ 2) + 1 = 3 by 3.', set: { pad: 'valid', stride: 2 } }
    ],
    startAtZero: false,
    steps(z) { const o = this.geom(z.p); return o.oh * o.ow; },
    speed: () => 450,
    geom(p) { const P = p.pad === 'valid' ? 0 : 1, S = +p.stride; const oh = Math.floor((7 - 3 + 2 * P) / S) + 1; return { P, S, oh, ow: oh }; },
    draw(z) {
      const { g, p } = z;
      const img = INPUTS[p.inp];
      let k = p.ker === 'custom' ? CVZ.parseGrid(p.custom) : KERNELS[p.ker];
      if (k.length !== 3 || k.some(r => r.length !== 3)) { k = KERNELS.identity; }
      const { P, S, oh, ow } = this.geom(p);
      const get = (r, c) => { if (r >= 0 && r < 7 && c >= 0 && c < 7) return img[r][c]; return p.pad === 'replicate' ? img[clamp(r, 0, 6)][clamp(c, 0, 6)] : 0; };
      const out = [];
      for (let i = 0; i < oh; i++) { const row = []; for (let j = 0; j < ow; j++) { let sm = 0; for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) sm += k[a][b] * get(i * S - P + a, j * S - P + b); row.push(sm); } out.push(row); }
      const cell = P ? 30 : 34, X0 = 14 + (P ? cell : 0), Y0 = 24 + (P ? cell : 0);
      D.text(g, 'Input' + (P ? ' with padding' : ''), 14, 14, { b: true, s: 12, c: z.col.ink });
      for (let r = -P; r < 7 + P; r++) for (let c = -P; c < 7 + P; c++) {
        const v = get(r, c), inside = r >= 0 && r < 7 && c >= 0 && c < 7;
        D.rect(g, X0 + c * cell, Y0 + r * cell, cell, cell, { fill: `rgb(${v},${v},${v})`, stroke: inside ? 'rgba(0,0,0,.25)' : z.col.orange, w: inside ? 0.8 : 1, dash: inside ? null : [3, 2] });
        D.text(g, String(v), X0 + (c + 0.5) * cell, Y0 + (r + 0.5) * cell + 4, { a: 'center', s: 10, mono: true, c: v > 128 ? '#0b1a2e' : '#fff' });
      }
      const cur = z.step > 0 ? z.step - 1 : -1;
      const ci = cur >= 0 ? Math.floor(cur / ow) : -1, cj = cur >= 0 ? cur % ow : -1;
      if (cur >= 0) D.rect(g, X0 + (cj * S - P) * cell, Y0 + (ci * S - P) * cell, 3 * cell, 3 * cell, { stroke: z.col.red, w: 3 });
      const OX = 340, oc = Math.min(28, 175 / ow);
      D.text(g, `Output ${oh} × ${ow}`, OX, 14, { b: true, s: 12, c: z.col.ink });
      for (let i = 0; i < oh; i++) for (let j = 0; j < ow; j++) {
        const idx = i * ow + j, shown = idx < z.step;
        const v = out[i][j], gv = clamp(Math.round(Math.abs(v)));
        D.rect(g, OX + j * oc, 24 + i * oc, oc, oc, { fill: shown ? `rgb(${gv},${gv},${gv})` : z.col.surf, stroke: idx === cur ? z.col.red : z.col.line, w: idx === cur ? 2.5 : 0.8 });
        if (shown) D.text(g, f(v, 1), OX + (j + 0.5) * oc, 24 + (i + 0.5) * oc + 4, { a: 'center', s: oc > 26 ? 9.5 : 8, mono: true, c: gv > 128 ? '#0b1a2e' : '#fff' });
      }
      D.text(g, 'Kernel', OX, 24 + oh * oc + 22, { b: true, s: 12, c: z.col.ink });
      k.forEach((r, a) => D.text(g, r.map(v => f(v, 3).padStart(6)).join(' '), OX, 24 + oh * oc + 40 + a * 15, { mono: true, s: 11, c: z.col.ink2 }));
      let sum = '';
      if (cur >= 0) {
        const terms = [];
        for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) terms.push(`${f(k[a][b], 3)}×${get(ci * S - P + a, cj * S - P + b)}`);
        sum = `Output (${ci}, ${cj}) = ${terms.join(' + ')} = <b>${f(out[ci][cj], 2)}</b>`;
      }
      return `<span class="big">g(x, y) = Σ<sub>i</sub> Σ<sub>j</sub> h(i, j) · f(x + i, y + j), &nbsp; output size = ⌊(W − k + 2P) ÷ S⌋ + 1 = ⌊(7 − 3 + ${2 * P}) ÷ ${S}⌋ + 1 = ${oh}</span><br>${sum || 'Press Play to watch each output pixel being computed.'} Negative results are drawn by their size, because a screen cannot show negative light.`;
    }
  });

  def('edge1d', {
    title: 'Sharpening up close: one edge as a curve',
    sub: 'The blue curve is one row of pixels across an edge. Sharpening adds back k times the detail (the signal minus its blur). Watch the overshoot and the noise.',
    W: 560, H: 260,
    params: [
      { k: 'blur', label: 'Camera blur σ', type: 'range', min: 0.3, max: 4, step: 0.1, v: 2 },
      { k: 'noise', label: 'Noise', type: 'range', min: 0, max: 20, v: 3 },
      { k: 'k', label: 'Sharpening amount k', type: 'range', min: 0, max: 4, step: 0.1, v: 1 },
      { k: 'r', label: 'Detail blur radius σ<sub>d</sub>', type: 'range', min: 0.5, max: 4, step: 0.1, v: 1.5 }
    ],
    tips: [
      { t: 'Set k to 0. The orange curve sits on the blue one. Raise k slowly and the edge gets steeper.', set: { k: 0 } },
      { t: 'Set k to 3. Bumps appear on both sides of the edge. These overshoots are the halos you see around over sharpened photos.', set: { k: 3, noise: 0 } },
      { t: 'Set noise to 15 and k to 2. Sharpening boosts the noise as much as the edge. In the project notebook, precision fell from 0.6802 on the blurred images to 0.6583 after sharpening.', set: { noise: 15, k: 2 } }
    ],
    draw(z) {
      const { g, p } = z;
      const N = 120, r = CVZ.rng(9);
      const ideal = Array.from({ length: N }, (_, i) => i < N / 2 ? 60 : 190);
      const blur1 = (a, s) => { const R = Math.ceil(3 * s), w = []; let t = 0; for (let i = -R; i <= R; i++) { const v = Math.exp(-i * i / (2 * s * s)); w.push(v); t += v; } return a.map((_, i) => { let m = 0; for (let j = -R; j <= R; j++) m += w[j + R] / t * a[clamp(i + j, 0, N - 1)]; return m; }); };
      const seen = blur1(ideal, p.blur).map(v => v + CVZ.gauss(r) * p.noise);
      const det = blur1(seen, p.r);
      const sharp = seen.map((v, i) => v + p.k * (v - det[i]));
      const m = D.axes(g, z, [50, 14, 490, 196], [0, N - 1], [0, 255], { nx: 4, ny: 3, xl: 'position along the row', yl: 'intensity', fx: v => Math.round(v), fy: v => Math.round(v) });
      const plot = (a, c, w, dash) => { g.save(); g.strokeStyle = c; g.lineWidth = w; if (dash) g.setLineDash(dash); g.beginPath(); a.forEach((v, i) => { const y = m.sy(clamp(v, -20, 275)); if (i) g.lineTo(m.sx(i), y); else g.moveTo(m.sx(i), y); }); g.stroke(); g.restore(); };
      g.save(); g.beginPath(); g.rect(50, 14, 490, 196); g.clip();
      plot(ideal, z.col.ink2, 1.2, [4, 4]); plot(seen, z.col.cv, 2); plot(sharp, z.col.orange, 2.2);
      g.restore();
      const over = Math.max(...sharp) - 190, under = 60 - Math.min(...sharp);
      const flatN = a => { const seg = a.slice(5, 40); const mu = seg.reduce((x, y) => x + y, 0) / seg.length; return Math.sqrt(seg.reduce((x, y) => x + (y - mu) ** 2, 0) / seg.length); };
      return `<span class="big">sharpened = f + k (f − G<sub>σ<sub>d</sub></sub> ∗ f)</span><br>Dashed: the true edge. Blue: what the camera saw. Orange: after sharpening. Overshoot above the bright side ${f(Math.max(0, over), 1)}, below the dark side ${f(Math.max(0, under), 1)}. Noise in the flat part: ${f(flatN(seen), 2)} before, ${f(flatN(sharp), 2)} after.`;
    }
  });
})();
