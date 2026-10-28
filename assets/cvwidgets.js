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
  /* ---------------------------------------------------------------- Chapter 6: motion and video */
  const hueOf = (u, v) => ((Math.atan2(v, u) * 180 / Math.PI) + 360) % 360;
  def('flow', {
    title: 'Optical flow between frame T and frame T + 1',
    sub: 'The car moves between two frames. Each arrow is a flow vector (u, v): how far that point moved. Up is positive v. Arrows are drawn 3 times longer than the real motion so they are easy to see.',
    W: 560, H: 250,
    params: [
      { k: 'u', label: 'Car motion u (pixels per frame, right is +)', type: 'range', min: -8, max: 8, v: 3 },
      { k: 'v', label: 'Car motion v (pixels per frame, up is +)', type: 'range', min: -8, max: 8, v: 4 },
      { k: 'pan', label: 'Camera pans right by', type: 'range', min: -6, max: 6, v: 0 },
      { k: 'fps', label: 'Frame rate (fps)', type: 'select', v: 30, num: true, opts: [[24, '24'], [30, '30'], [60, '60']] },
      { k: 'mode', label: 'Show flow as', type: 'select', v: 'arrows', opts: [['arrows', 'Arrows'], ['colour', 'Colour (hue = direction, strength = speed)']] },
      { k: 'dense', label: 'Points tracked', type: 'select', v: 'dense', opts: [['dense', 'Dense: every grid point'], ['sparse', 'Sparse: a few corners only']] }
    ],
    tips: [
      { t: 'The default is the lecture problem: (u, v) = (3, 4). The magnitude is √(9 + 16) = 5 pixels per frame, which is 150 pixels per second at 30 fps.', set: { u: 3, v: 4, pan: 0, fps: 30 } },
      { t: 'Switch to Colour. Every direction gets its own hue, and a stronger colour means faster motion. This is how dense flow is usually shown.', set: { mode: 'colour' } },
      { t: 'Set the car still (u = 0, v = 0) and pan the camera by 4. Now the whole background seems to move left, although nothing in the world moved.', set: { u: 0, v: 0, pan: 4, mode: 'arrows' } },
      { t: 'Choose Sparse. Only a handful of corners are tracked, so the cost drops a lot. That is enough when the background is still and you follow one object.', set: { dense: 'sparse', pan: 0, u: 3, v: 4 } }
    ],
    draw(z) {
      const { g, p } = z;
      const X = 10, Y = 10, CW = 300, CH = 200, step = 20;
      const bu = -p.pan, ou = p.u - p.pan, ov = p.v;
      const car = [110, 80, 70, 40];
      const inCar = (x, y) => x >= car[0] && x <= car[0] + car[2] && y >= car[1] && y <= car[1] + car[3];
      D.rect(g, X, Y, CW, CH, { fill: z.col.bg, stroke: z.col.line });
      g.save(); g.beginPath(); g.rect(X, Y, CW, CH); g.clip();
      for (let i = -2; i < 9; i++) { const x0 = X + 15 + i * 40 + bu * 3; D.rect(g, x0, Y + 140, 8, 60, { fill: z.col.dark ? '#3b4b5e' : '#c9d6e3' }); D.circle(g, x0 + 4, Y + 136, 12, { fill: z.col.dark ? '#2f6b4f' : '#a7d7b8' }); }
      D.rect(g, X + car[0], Y + car[1], car[2], car[3], { stroke: z.col.ink2, w: 1.5, dash: [4, 3] });
      D.rect(g, X + car[0] + ou * 3, Y + car[1] - ov * 3, car[2], car[3], { fill: z.col.dark ? 'rgba(255,255,255,.25)' : 'rgba(14,116,144,.25)', stroke: z.col.cv, w: 2 });
      const pts = [];
      if (p.dense === 'dense') { for (let y = step / 2; y < CH; y += step) for (let x = step / 2; x < CW; x += step) pts.push([x, y]); }
      else { pts.push([car[0], car[1]], [car[0] + car[2], car[1]], [car[0], car[1] + car[3]], [car[0] + car[2], car[1] + car[3]]); for (let i = 0; i < 6; i++) pts.push([15 + i * 40 + 8, 140]); }
      pts.forEach(([x, y]) => {
        const [fu, fv] = inCar(x, y) ? [ou, ov] : [bu, 0];
        const m = Math.hypot(fu, fv);
        if (p.mode === 'colour') {
          const L = 100 - 50 * Math.min(1, m / 8);
          g.fillStyle = `hsl(${hueOf(fu, fv)},85%,${L}%)`;
          if (p.dense === 'dense') g.fillRect(X + x - step / 2, Y + y - step / 2, step, step);
          else D.circle(g, X + x, Y + y, 7, { fill: g.fillStyle, stroke: z.col.ink2, w: 1 });
        } else {
          D.circle(g, X + x, Y + y, 2, { fill: z.col.ink2 });
          D.arrow(g, X + x, Y + y, X + x + fu * 3, Y + y - fv * 3, inCar(x, y) ? z.col.red : z.col.cv, 1.6, 6);
        }
      });
      g.restore();
      D.text(g, 'dashed: car in frame T, filled: frame T + 1', X, Y + CH + 18, { s: 11, c: z.col.ink2 });
      const cx = 440, cy = 70, R = 46;
      for (let a = 0; a < 360; a += 6) { g.save(); g.beginPath(); g.moveTo(cx, cy); g.arc(cx, cy, R, -(a + 3.5) * Math.PI / 180, -(a - 3.5) * Math.PI / 180); g.closePath(); g.fillStyle = `hsl(${a},85%,55%)`; g.fill(); g.restore(); }
      D.circle(g, cx, cy, 14, { fill: '#fff' });
      D.text(g, 'right', cx + R + 4, cy + 4, { s: 10, c: z.col.ink2 }); D.text(g, 'up', cx, cy - R - 4, { s: 10, c: z.col.ink2, a: 'center' });
      D.text(g, 'left', cx - R - 4, cy + 4, { s: 10, c: z.col.ink2, a: 'right' }); D.text(g, 'down', cx, cy + R + 12, { s: 10, c: z.col.ink2, a: 'center' });
      const m = Math.hypot(ou, ov), ang = hueOf(ou, ov);
      [`car flow (u, v) = (${ou}, ${ov})`, `magnitude √(u² + v²) = ${f(m, 2)}`, `direction ${m ? f(ang, 1) + '°' : 'none'}`, `speed ${f(m * p.fps, 1)} px per second`, `vectors computed: ${pts.length}`].forEach((t, i) => D.text(g, t, 336, 152 + i * 19, { s: 12, mono: true, c: z.col.ink }));
      return `<span class="big">magnitude = √(u² + v²), &nbsp; direction θ = atan2(v, u), &nbsp; speed = magnitude × fps</span><br>${p.pan ? `The camera pan adds (${-p.pan}, 0) to every pixel, so the car's flow in the image is its own motion plus the pan. Separating the two is the job of MBH, later in this chapter.` : 'With a still camera, only the moving car produces flow.'} ${p.dense === 'sparse' ? 'Sparse flow tracks only well textured corners.' : 'Dense flow estimates a vector at every grid point (every pixel in a real system).'}`;
    }
  });

  def('aperture', {
    title: 'The aperture problem',
    sub: 'A long edge moves behind a small round window. Inside the window you can only measure the motion across the edge, not along it. Press Play to move the edge.',
    W: 560, H: 240,
    params: [
      { k: 'th', label: 'Edge angle (degrees)', type: 'range', min: 0, max: 175, step: 5, v: 45 },
      { k: 'phi', label: 'True motion direction (degrees)', type: 'range', min: 0, max: 355, step: 5, v: 0 },
      { k: 's', label: 'True speed (pixels per frame)', type: 'range', min: 1, max: 6, v: 4 },
      { k: 'corner', label: 'Let a corner of the shape enter the window', type: 'check', v: false }
    ],
    tips: [
      { t: 'A 45° edge moving straight right. Through the window it seems to move diagonally, down and to the right, at only about 70% of its true speed.', set: { th: 45, phi: 0, s: 4, corner: false }, play: true },
      { t: 'Make the motion run along the edge (edge angle 45°, motion 45°). Inside the window nothing seems to move at all.', set: { th: 45, phi: 45, corner: false }, play: true },
      { t: 'Tick the corner. A corner has edges in two directions, so the true motion becomes measurable. This is why sparse trackers pick corners.', set: { corner: true }, play: true }
    ],
    startAtZero: true,
    steps: () => 12,
    speed: () => 160,
    draw(z) {
      const { g, p, step } = z;
      const rad = d => d * Math.PI / 180;
      const dx = Math.cos(rad(p.phi)), dy = -Math.sin(rad(p.phi));
      const ex = Math.cos(rad(p.th)), ey = -Math.sin(rad(p.th));
      const nAng = p.th + 90, nx = Math.cos(rad(nAng)), ny = -Math.sin(rad(nAng));
      const normal = p.s * Math.cos(rad(p.phi - nAng));
      const drawEdge = (cx, cy, t, col, w, clipR) => {
        const ox = cx + dx * p.s * t * 1.6, oy = cy + dy * p.s * t * 1.6;
        g.save(); g.strokeStyle = col; g.lineWidth = w; g.beginPath();
        if (p.corner) { g.moveTo(ox + ex * 200, oy + ey * 200); g.lineTo(ox, oy); g.lineTo(ox + nx * 200, oy + ny * 200); }
        else { g.moveTo(ox - ex * 300, oy - ey * 300); g.lineTo(ox + ex * 300, oy + ey * 300); }
        g.stroke(); g.restore();
      };
      D.rect(g, 10, 10, 250, 210, { fill: z.col.bg, stroke: z.col.line });
      g.save(); g.beginPath(); g.rect(10, 10, 250, 210); g.clip();
      drawEdge(110, 120, 0, z.col.line, 3); drawEdge(110, 120, step, z.col.ink, 3);
      D.arrow(g, 110, 120, 110 + dx * p.s * 14, 120 + dy * p.s * 14, z.col.red, 2.5, 9);
      g.restore();
      D.text(g, 'Whole scene: true motion in red', 14, 236, { s: 11, c: z.col.ink2, b: true });
      const cx = 400, cy = 115, R = 80;
      g.save(); g.beginPath(); g.arc(cx, cy, R, 0, Math.PI * 2); g.fillStyle = z.col.bg; g.fill(); g.clip();
      drawEdge(cx - (p.corner ? 10 : 0), cy - (p.corner ? 10 : 0), step, z.col.ink, 3);
      g.restore();
      D.circle(g, cx, cy, R, { stroke: z.col.ink2, w: 2 });
      if (p.corner) D.arrow(g, cx, cy, cx + dx * p.s * 14, cy + dy * p.s * 14, z.col.red, 2.5, 9);
      else D.arrow(g, cx, cy, cx + nx * normal * 14, cy + ny * normal * 14, z.col.orange, 2.5, 9);
      D.text(g, p.corner ? 'Window: the corner reveals the true motion' : 'Window: only the normal motion is visible', 400, 236, { s: 11, c: z.col.ink2, b: true, a: 'center' });
      return `<span class="big">I<sub>x</sub> u + I<sub>y</sub> v + I<sub>t</sub> = 0</span><br>This brightness constancy equation is one equation with two unknowns, u and v. It fixes only the part of the motion across the edge: here ${f(Math.abs(normal), 2)} of the true ${p.s} pixels per frame. ${p.corner ? 'At a corner the gradients point two ways, so two independent equations pin down both u and v.' : 'Lucas and Kanade solve this by assuming every pixel in a small window shares one (u, v) and solving the equations together, which works when the window holds gradients in two directions.'}`;
    }
  });

  const DIRS = ['→', '↗', '↑', '↖', '←', '↙', '↓', '↘'];
  def('hofmbh', {
    title: 'HOF and MBH on the same flow field',
    sub: 'Left: the flow of each cell. Middle: motion boundaries, where the flow changes from one cell to the next. Bottom: the HOF and MBH histograms over 8 directions, weighted by strength.',
    W: 560, H: 305,
    params: [
      { k: 'scene', label: 'Scene', type: 'select', v: 'walk', opts: [['walk', 'Person walking'], ['two', 'Two people walking in opposite directions'], ['ball', 'Ball moving up in front of a wall'], ['cycle', 'Cyclist (legs pedal, torso steady)']] },
      { k: 'sp', label: 'Body speed (right or up is +)', type: 'range', min: -4, max: 4, step: 0.5, v: 2 },
      { k: 'limb', label: 'Arm and leg swing', type: 'range', min: 0, max: 4, step: 0.5, v: 1.5 },
      { k: 'pan', label: 'Camera pans right by', type: 'range', min: -4, max: 4, step: 0.5, v: 0 }
    ],
    tips: [
      { t: 'Person walking right, camera fixed. HOF has one strong → bar: the dominant direction.', set: { scene: 'walk', sp: 2, pan: 0 } },
      { t: 'Now pan the camera by 3. The background floods HOF with ← votes and the walker is lost. MBH ignores the uniform background and still outlines the person.', set: { scene: 'walk', sp: 2, pan: 3 } },
      { t: 'Two people in opposite directions: HOF shows two peaks, → and ←. Their HOF features are different, as the lecture concluded.', set: { scene: 'two', sp: 2, pan: 0 } },
      { t: 'A ball moving up with a fixed camera. HOF alone shows the ↑ direction clearly, so MBH adds little here.', set: { scene: 'ball', sp: 3, pan: 0 } },
      { t: 'Cyclist with speed 2 and swing 3. HOF says right. MBH lights up the pedalling legs, where motion differs from the steady torso.', set: { scene: 'cycle', sp: 2, limb: 3, pan: 0 } }
    ],
    draw(z) {
      const { g, p } = z;
      const NX = 24, NY = 16;
      const U = [], V = [], who = [];
      for (let r = 0; r < NY; r++) { U.push(new Array(NX).fill(-p.pan)); V.push(new Array(NX).fill(0)); who.push(new Array(NX).fill(0)); }
      const put = (c0, c1, r0, r1, u, v, id) => { for (let r = r0; r <= r1; r++) for (let c = c0; c <= c1; c++) if (r >= 0 && r < NY && c >= 0 && c < NX) { U[r][c] = u - p.pan; V[r][c] = v; who[r][c] = id; } };
      const person = (c, sp, id) => {
        put(c, c, 1, 2, sp, 0, id); put(c - 1, c + 1, 3, 8, sp, 0, id);
        put(c - 2, c - 2, 4, 7, sp + p.limb, 0, id); put(c + 2, c + 2, 4, 7, sp - p.limb, 0, id);
        put(c - 1, c - 1, 9, 14, sp - p.limb, 0, id); put(c + 1, c + 1, 9, 14, sp + p.limb, 0, id);
      };
      if (p.scene === 'walk') person(11, p.sp, 1);
      else if (p.scene === 'two') { person(6, p.sp, 1); person(17, -p.sp, 2); }
      else if (p.scene === 'ball') put(10, 13, 6, 9, 0, p.sp, 1);
      else { put(11, 11, 1, 2, p.sp, 0, 1); put(10, 12, 3, 8, p.sp, 0, 1); put(10, 10, 9, 13, p.sp, p.limb, 1); put(12, 12, 9, 13, p.sp, -p.limb, 1); put(8, 9, 12, 14, p.sp, 0, 1); put(13, 14, 12, 14, p.sp, 0, 1); }
      const cell = 11, X = 10, Y = 22;
      D.text(g, 'Flow field', X, 14, { b: true, s: 12, c: z.col.ink });
      for (let r = 0; r < NY; r++) for (let c = 0; c < NX; c++) D.rect(g, X + c * cell, Y + r * cell, cell, cell, { fill: who[r][c] ? (who[r][c] === 2 ? z.col.purple : z.col.ink2) : z.col.bg });
      for (let r = 0; r < NY; r++) for (let c = 0; c < NX; c++) {
        if (!who[r][c] && (r % 2 || c % 2)) continue;
        const x = X + (c + 0.5) * cell, y = Y + (r + 0.5) * cell;
        D.arrow(g, x, y, x + U[r][c] * 4, y - V[r][c] * 4, who[r][c] ? z.col.orange : z.col.cv, 1.3, 5);
      }
      const at = (A, r, c) => A[clamp(r, 0, NY - 1)][clamp(c, 0, NX - 1)];
      const hof = new Array(8).fill(0), mbh = new Array(8).fill(0), M = [];
      let hofBg = 0, hofAll = 0, mbhNear = 0, mbhAll = 0;
      const near = (r, c) => { for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) if (at(who, r + a, c + b)) return true; return false; };
      const bin = (x, y) => ((Math.round(Math.atan2(y, x) / (Math.PI / 4)) % 8) + 8) % 8;
      for (let r = 0; r < NY; r++) {
        M.push([]);
        for (let c = 0; c < NX; c++) {
          const u = U[r][c], v = V[r][c], m = Math.hypot(u, v);
          if (m > 1e-6) { hof[bin(u, v)] += m; hofAll += m; if (!who[r][c]) hofBg += m; }
          const ux = (at(U, r, c + 1) - at(U, r, c - 1)) / 2, uy = (at(U, r - 1, c) - at(U, r + 1, c)) / 2;
          const vx = (at(V, r, c + 1) - at(V, r, c - 1)) / 2, vy = (at(V, r - 1, c) - at(V, r + 1, c)) / 2;
          const mu = Math.hypot(ux, uy), mv = Math.hypot(vx, vy);
          if (mu > 1e-6) mbh[bin(ux, uy)] += mu;
          if (mv > 1e-6) mbh[bin(vx, vy)] += mv;
          M[r].push(mu + mv); mbhAll += mu + mv; if (near(r, c)) mbhNear += mu + mv;
        }
      }
      const mM = Math.max(1e-9, ...M.flat()), c2 = 7, X2 = 300;
      D.text(g, 'Motion boundaries |∇u| + |∇v|', X2, 14, { b: true, s: 12, c: z.col.ink });
      for (let r = 0; r < NY; r++) for (let c = 0; c < NX; c++) {
        const a = M[r][c] / mM;
        D.rect(g, X2 + c * c2, Y + r * c2, c2, c2, { fill: z.col.bg });
        if (a > 0) { g.save(); g.globalAlpha = 0.15 + 0.85 * a; D.rect(g, X2 + c * c2, Y + r * c2, c2, c2, { fill: z.col.red }); g.restore(); }
      }
      D.rect(g, X2, Y, NX * c2, NY * c2, { stroke: z.col.line, w: 1 });
      [`HOF from background: ${hofAll ? f(100 * hofBg / hofAll, 0) : 0}%`, `MBH at the moving parts: ${mbhAll ? f(100 * mbhNear / mbhAll, 0) : 0}%`].forEach((t, i) => D.text(g, t, X2, Y + NY * c2 + 22 + i * 18, { s: 11.5, mono: true, c: z.col.ink }));
      const hb = [X, 226, 250, 52], mb = [X2, 226, 250, 52];
      D.text(g, 'HOF (flow directions)', X, 218, { b: true, s: 12, c: z.col.ink });
      D.text(g, 'MBH (directions of flow change)', X2, 218, { b: true, s: 12, c: z.col.ink });
      D.bars(g, z, hb, hof, { gap: 4 }); D.bars(g, z, mb, mbh, { gap: 4, colour: () => z.col.red });
      DIRS.forEach((d, i) => { D.text(g, d, hb[0] + (i + 0.5) * 250 / 8, 296, { a: 'center', s: 13, c: z.col.ink2 }); D.text(g, d, mb[0] + (i + 0.5) * 250 / 8, 296, { a: 'center', s: 13, c: z.col.ink2 }); });
      const top = hof.indexOf(Math.max(...hof));
      return `HOF = how things move. MBH = where motion differs. ${hofAll ? `The tallest HOF bar is ${DIRS[top]}.` : 'Nothing moves, so HOF is empty.'} ${p.pan ? 'Camera motion adds the same vector everywhere. That shifts every HOF vote but leaves the flow gradients, and so MBH, unchanged.' : ''}`;
    }
  });

  def('bovw', {
    title: 'A vocabulary of visual words with k-means',
    sub: 'Each dot is one descriptor (in reality a long HOG, HOF or MBH vector, shown here in 2D). Circles come from a walking clip, triangles from a jumping clip. Step through k-means, then read each clip as a histogram of words.',
    W: 560, H: 280,
    params: [
      { k: 'k', label: 'Vocabulary size k', type: 'range', min: 2, max: 6, v: 4 },
      { k: 'seed', label: 'Starting centres (seed)', type: 'range', min: 1, max: 20, v: 3 }
    ],
    tips: [
      { t: 'Press Play with k = 4. Each round first assigns every dot to its nearest centre, then moves each centre to the mean of its dots. The total squared distance falls every round.', set: { k: 4, seed: 3 }, play: true },
      { t: 'Set k = 2 and press Play, then compare with k = 4. Fewer words give a coarser description, so different actions are more likely to share the same words.', set: { k: 2 }, play: true },
      { t: 'Change the seed. k-means can settle on different answers from different starts, which is why libraries run it several times and keep the best.', set: { k: 4, seed: 11 }, play: true }
    ],
    startAtZero: true,
    steps: () => 12,
    speed: () => 700,
    draw(z) {
      const { g, p, step } = z;
      const r = CVZ.rng(42), blobs = [[0.2, 0.3], [0.3, 0.75], [0.75, 0.25], [0.8, 0.72]];
      const mk = (counts, clip) => counts.flatMap((n, b) => Array.from({ length: n }, () => ({ x: blobs[b][0] + CVZ.gauss(r) * 0.07, y: blobs[b][1] + CVZ.gauss(r) * 0.07, clip })));
      const pts = mk([14, 12, 2, 2], 0).concat(mk([2, 3, 13, 12], 1));
      const rs = CVZ.rng(p.seed * 131), K = p.k;
      let C = []; const used = new Set();
      while (C.length < K) { const i = Math.floor(rs() * pts.length); if (!used.has(i)) { used.add(i); C.push([pts[i].x, pts[i].y]); } }
      let lab = pts.map(() => -1);
      const assign = () => { lab = pts.map(q => { let b = 0, bd = Infinity; C.forEach((c, j) => { const d = (q.x - c[0]) ** 2 + (q.y - c[1]) ** 2; if (d < bd) { bd = d; b = j; } }); return b; }); };
      const update = () => { C = C.map((c, j) => { const m = pts.filter((_, i) => lab[i] === j); return m.length ? [m.reduce((s, q) => s + q.x, 0) / m.length, m.reduce((s, q) => s + q.y, 0) / m.length] : c; }); };
      for (let s = 1; s <= step; s++) { if (s % 2) assign(); else update(); }
      const cols = [z.col.cv, z.col.orange, z.col.purple, z.col.green, z.col.red, z.col.pink];
      const box = [10, 10, 290, 240], sx = v => box[0] + v * box[2], sy = v => box[1] + box[3] - v * box[3];
      D.rect(g, ...box, { fill: z.col.bg, stroke: z.col.line });
      pts.forEach((q, i) => {
        const c = lab[i] < 0 ? z.col.ink2 : cols[lab[i]], x = sx(q.x), y = sy(q.y);
        if (q.clip === 0) D.circle(g, x, y, 4.5, { fill: c });
        else { g.save(); g.fillStyle = c; g.beginPath(); g.moveTo(x, y - 6); g.lineTo(x + 5.5, y + 4); g.lineTo(x - 5.5, y + 4); g.closePath(); g.fill(); g.restore(); }
      });
      C.forEach((c, j) => { const x = sx(c[0]), y = sy(c[1]); D.line(g, x - 8, y - 8, x + 8, y + 8, cols[j], 3.5); D.line(g, x - 8, y + 8, x + 8, y - 8, cols[j], 3.5); D.text(g, 'w' + (j + 1), x + 10, y - 6, { s: 11, b: true, c: cols[j] }); });
      D.text(g, 'descriptor space (2D sketch)', 14, 268, { s: 11, c: z.col.ink2 });
      const hist = clip => C.map((_, j) => pts.filter((q, i) => q.clip === clip && lab[i] === j).length);
      ['Walking clip', 'Jumping clip'].forEach((t, ci) => {
        const y0 = 22 + ci * 128;
        D.text(g, t + ' as a histogram of words', 320, y0, { b: true, s: 12, c: z.col.ink });
        if (step === 0) { D.text(g, 'appears after the first assignment', 320, y0 + 40, { s: 11, c: z.col.ink2 }); return; }
        const h = hist(ci);
        D.bars(g, z, [320, y0 + 8, 220, 80], h, { max: 30, gap: 6, colour: i => cols[i] });
        h.forEach((v, j) => D.text(g, 'w' + (j + 1) + ': ' + v, 320 + (j + 0.5) * 220 / K, y0 + 104, { a: 'center', s: 10, c: z.col.ink2 }));
      });
      let J = 0; if (step) pts.forEach((q, i) => { const c = C[lab[i]]; J += (q.x - c[0]) ** 2 + (q.y - c[1]) ** 2; });
      const what = step === 0 ? 'Start: k centres are picked at random from the dots. Press Play or Step.' : step % 2 ? `Round ${(step + 1) / 2}, assign: each dot joins its nearest centre.` : `Round ${step / 2}, update: each centre moves to the mean of its dots.`;
      return `<b>${what}</b> ${step ? `Total squared distance J = ${f(J, 3)}.` : ''}<br><span class="big">J = Σ<sub>i</sub> ‖x<sub>i</sub> − μ<sub>c(i)</sub>‖²</span><br>Each clip becomes one fixed length vector of k counts, whatever its length. That vector is what the SVM classifies.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 7: classification and CNNs */
  const FILTERS = {
    vert: [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
    horz: [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
    diag: [[0, 1, 2], [-1, 0, 1], [-2, -1, 0]],
    spot: [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]],
    blur: [[1, 1, 1], [1, 1, 1], [1, 1, 1]].map(r => r.map(v => v / 9))
  };
  def('convlayer', {
    title: 'Inside one convolution layer: filter, ReLU, pooling',
    sub: 'A CNN layer slides a small filter over the image, keeps only positive responses with ReLU, then shrinks the map with pooling. In a real network the filter numbers are learned. Here you pick them.',
    W: 560, H: 245,
    params: [
      { k: 'filt', label: 'Filter', type: 'select', v: 'vert', opts: [['vert', 'Vertical edges (Sobel x)'], ['horz', 'Horizontal edges (Sobel y)'], ['diag', 'Diagonal edges'], ['spot', 'Spots and corners (centre minus surround)'], ['blur', 'Blur (average)']] },
      { k: 'act', label: 'Activation', type: 'select', v: 'relu', opts: [['none', 'None (negative values kept)'], ['relu', 'ReLU: max(0, x)']] },
      { k: 'pool', label: 'Pooling', type: 'select', v: 'max', opts: [['none', 'None'], ['max', 'Max pooling 2 × 2, stride 2'], ['avg', 'Average pooling 2 × 2, stride 2']] },
      { k: 'flip', label: 'Flip the filter sign', type: 'check', v: false }
    ],
    tips: [
      { t: 'Vertical edges with ReLU: only edges of one polarity survive, so the house, tree and sun show on one side only. The other sides gave negative responses, which ReLU set to 0.', set: { filt: 'vert', act: 'relu', flip: false } },
      { t: 'Now tick Flip the filter sign. The opposite edges light up. A real layer learns both versions as separate channels.', set: { filt: 'vert', act: 'relu', flip: true } },
      { t: 'Set Activation to None. Grey means 0, darker means negative, brighter means positive. ReLU throws away the negative half.', set: { act: 'none' } },
      { t: 'Compare Max and Average pooling. Max keeps the strongest response in each 2 × 2 block, so thin edges survive. Average dilutes them.', set: { pool: 'avg', act: 'relu' } }
    ],
    draw(z) {
      const { g, p } = z;
      const img = CVZ.sceneGray(64, 44);
      const k = FILTERS[p.filt].map(r => r.map(v => p.flip ? -v : v));
      const raw = CVZ.convolve(img, k, 'replicate', true);
      const act = raw.map(r => r.map(v => p.act === 'relu' ? Math.max(0, v) : v));
      let out = act;
      if (p.pool !== 'none') {
        out = [];
        for (let y = 0; y + 1 < act.length; y += 2) { const row = []; for (let x = 0; x + 1 < act[0].length; x += 2) { const q = [act[y][x], act[y][x + 1], act[y + 1][x], act[y + 1][x + 1]]; row.push(p.pool === 'max' ? Math.max(...q) : q.reduce((a, b) => a + b, 0) / 4); } out.push(row); }
      }
      const blurish = p.filt === 'blur';
      const show = m => m.map(r => r.map(v => blurish ? clamp(Math.round(v)) : (p.act === 'relu' ? clamp(Math.round(v * 1.2)) : clamp(Math.round(128 + v * 0.6)))));
      const S = 2.6;
      D.image(g, img, 10, 10, S);
      D.image(g, show(act), 196, 10, S);
      D.image(g, show(out), 382, 10, S * 64 / out[0].length);
      D.text(g, 'Input 64 × 44', 10, 140, { b: true, s: 12, c: z.col.ink });
      D.text(g, `After filter${p.act === 'relu' ? ' + ReLU' : ''} 64 × 44`, 196, 140, { b: true, s: 12, c: z.col.ink });
      D.text(g, p.pool === 'none' ? 'No pooling 64 × 44' : `After ${p.pool} pool ${out[0].length} × ${out.length}`, 382, 140, { b: true, s: 12, c: z.col.ink });
      D.text(g, 'Filter', 10, 168, { b: true, s: 12, c: z.col.ink });
      k.forEach((r, i) => D.text(g, r.map(v => f(v, 2).padStart(5)).join(' '), 10, 186 + i * 16, { mono: true, s: 11.5, c: z.col.ink2 }));
      const flat = raw.flat(), neg = flat.filter(v => v < 0).length;
      [`weights in this filter: 3 × 3 × 1 + 1 bias = 10`, `negative responses: ${f(100 * neg / flat.length, 0)}%${p.act === 'relu' ? ', all set to 0 by ReLU' : ''}`, `values after pooling: ${out.length * out[0].length} (was ${flat.length})`].forEach((t, i) => D.text(g, t, 196, 186 + i * 18, { s: 11.5, mono: true, c: z.col.ink }));
      return `<span class="big">feature map = ReLU(w ∗ x + b), &nbsp; ReLU(x) = max(0, x)</span><br>A real first layer has many filters, for example 64, each producing its own map, and later layers combine those maps into textures, parts and objects.`;
    }
  });

  def('softmax', {
    title: 'From scores to probabilities: SoftMax and sigmoid',
    sub: 'The network outputs one raw score (logit) per class. SoftMax turns them into probabilities that compete and add up to 1. Independent sigmoids give each class its own yes or no probability.',
    W: 560, H: 240,
    params: [
      { k: 'z1', label: 'Logit for dog', type: 'range', min: -4, max: 6, step: 0.1, v: 2 },
      { k: 'z2', label: 'Logit for cat', type: 'range', min: -4, max: 6, step: 0.1, v: 1 },
      { k: 'z3', label: 'Logit for wolf', type: 'range', min: -4, max: 6, step: 0.1, v: 0.1 },
      { k: 'T', label: 'Temperature T (divide logits by T)', type: 'range', min: 0.2, max: 5, step: 0.1, v: 1 },
      { k: 'y', label: 'True class', type: 'select', v: 0, num: true, opts: [[0, 'Dog'], [1, 'Cat'], [2, 'Wolf']] }
    ],
    tips: [
      { t: 'The default is the lecture example: logits 2.0, 1.0, 0.1 give probabilities 0.659, 0.242 and 0.099.', set: { z1: 2, z2: 1, z3: 0.1, T: 1 } },
      { t: 'Add 3 to every logit (5, 4, 3.1). The SoftMax bars do not move at all, only differences matter. The sigmoids all rise.', set: { z1: 5, z2: 4, z3: 3.1, T: 1 } },
      { t: 'Raise the temperature to 4. The probabilities flatten and the model looks unsure. Lower it to 0.3 and the top class takes almost everything.', set: { z1: 2, z2: 1, z3: 0.1, T: 4 } },
      { t: 'Set the true class to Wolf. The loss jumps, and the gradient p − y pushes the wolf logit up and the others down.', set: { z1: 2, z2: 1, z3: 0.1, T: 1, y: 2 } }
    ],
    draw(z) {
      const { g, p } = z;
      const L = [p.z1, p.z2, p.z3], names = ['dog', 'cat', 'wolf'];
      const s = L.map(v => v / p.T), mx = Math.max(...s), e = s.map(v => Math.exp(v - mx)), S = e.reduce((a, b) => a + b, 0);
      const P = e.map(v => v / S), sig = L.map(v => 1 / (1 + Math.exp(-v)));
      const cols = [z.col.cv, z.col.orange, z.col.purple];
      const bar = (x0, title, vals, note) => {
        D.text(g, title, x0, 16, { b: true, s: 12, c: z.col.ink });
        D.rect(g, x0, 26, 240, 150, { stroke: z.col.line, w: 1 });
        vals.forEach((v, i) => {
          const h = v * 140, x = x0 + 18 + i * 76;
          D.rect(g, x, 176 - h, 52, h, { fill: cols[i] });
          D.text(g, f(v, 3), x + 26, 170 - h, { a: 'center', s: 12, mono: true, c: z.col.ink, b: i === p.y });
          D.text(g, names[i] + (i === p.y ? ' (true)' : ''), x + 26, 194, { a: 'center', s: 11.5, c: i === p.y ? z.col.ink : z.col.ink2, b: i === p.y });
        });
        D.text(g, note, x0, 216, { s: 11.5, mono: true, c: z.col.ink2 });
      };
      bar(10, 'SoftMax (they compete)', P, `sum = ${f(P.reduce((a, b) => a + b, 0), 3)}`);
      bar(300, 'Independent sigmoids', sig, `sum = ${f(sig.reduce((a, b) => a + b, 0), 3)}`);
      const loss = -Math.log(P[p.y]), grad = P.map((v, i) => v - (i === p.y ? 1 : 0));
      return `<span class="big">p<sub>i</sub> = e<sup>z<sub>i</sub>/T</sup> ÷ Σ<sub>j</sub> e<sup>z<sub>j</sub>/T</sup>, &nbsp; σ(z) = 1 ÷ (1 + e<sup>−z</sup>), &nbsp; loss = −ln p<sub>true</sub></span><br>Cross entropy loss = −ln ${f(P[p.y], 3)} = <b>${f(loss, 3)}</b>. Gradient p − y = [${grad.map(v => f(v, 3)).join(', ')}]. Use SoftMax when exactly one class is right, sigmoids when several labels can be true at once.`;
    }
  });

  def('receptive', {
    title: 'How far each neuron can see: the receptive field',
    sub: 'Each row is one layer, drawn in input pixel positions. The red neuron at the top depends on the blue neurons in each layer below it. Stacking layers, and especially striding or pooling, makes that region grow.',
    W: 560, H: 260,
    params: [
      { k: 'n', label: 'Number of layers', type: 'range', min: 1, max: 5, v: 3 },
      { k: 'k', label: 'Kernel size k', type: 'select', v: 3, num: true, opts: [[3, '3'], [5, '5'], [7, '7']] },
      { k: 's', label: 'Stride of every layer', type: 'select', v: 1, num: true, opts: [[1, '1'], [2, '2 (like pooling)']] }
    ],
    tips: [
      { t: 'Three 3 × 3 layers with stride 1 see a 7 pixel wide region, the same as one 7 × 7 layer, with fewer weights and three ReLUs instead of one. This is the VGG idea.', set: { n: 3, k: 3, s: 1 } },
      { t: 'Switch the stride to 2. The receptive field now grows much faster, because each unit in a deeper layer sits further apart in the input.', set: { n: 3, k: 3, s: 2 } },
      { t: 'One layer with k = 7 has the same reach as three layers with k = 3. Compare the weight counts in the readout.', set: { n: 1, k: 7, s: 1 } }
    ],
    draw(z) {
      const { g, p } = z;
      let r = 1, j = 1; const R = [1], J = [1];
      for (let l = 0; l < p.n; l++) { r += (p.k - 1) * j; j *= p.s; R.push(r); J.push(j); }
      const cnt = new Array(p.n + 1); cnt[p.n] = 1;
      for (let l = p.n; l > 0; l--) cnt[l - 1] = (cnt[l] - 1) * p.s + p.k;
      const N = Math.max(23, r + 8) | 1, cw = Math.min(16, 480 / N), X0 = 60 + (480 - cw * N) / 2, mid = (N - 1) / 2;
      const rowH = Math.min(44, 200 / (p.n + 1)), Y0 = 16;
      for (let l = p.n; l >= 0; l--) {
        const y = Y0 + (p.n - l) * rowH, J0 = J[l];
        const first = mid - (cnt[l] - 1) / 2 * J0;
        for (let i = -40; i <= 40; i++) {
          const pos = mid + i * J0;
          if (pos < 0 || pos > N - 1) continue;
          const t = (pos - first) / J0, inside = t >= -1e-9 && t <= cnt[l] - 1 + 1e-9;
          D.rect(g, X0 + pos * cw, y, Math.max(2, cw - 1), rowH * 0.55, { fill: inside ? (l === p.n ? z.col.red : z.col.cv) : z.col.bg, stroke: z.col.line, w: 0.6 });
        }
        D.text(g, l === 0 ? 'input' : 'layer ' + l, X0 - 8, y + rowH * 0.42, { a: 'right', s: 11, c: z.col.ink2 });
      }
      const w1 = p.n * p.k * p.k, w2 = r * r;
      return `<span class="big">r<sub>l</sub> = r<sub>l−1</sub> + (k − 1) × j<sub>l−1</sub>, &nbsp; j<sub>l</sub> = j<sub>l−1</sub> × s, &nbsp; r<sub>0</sub> = j<sub>0</sub> = 1</span><br>Receptive field after each layer: ${R.slice(1).join(', ')} input pixels wide. The top neuron sees <b>${r} × ${r}</b> pixels. Weights per input and output channel pair: ${p.n} × ${p.k}² = ${w1}, against ${w2} for one ${r} × ${r} filter${p.s > 1 ? ' (with stride the two are not equivalent, so this is only a rough comparison)' : ' with the same reach'}.`;
    }
  });

  def('residual', {
    title: 'Why very deep networks need shortcuts',
    sub: 'During training the error signal flows backwards through every layer and is multiplied by each layer\'s local slope. Without a shortcut it can shrink to almost nothing. With H(x) = F(x) + x, each block multiplies it by 1 plus a small slope instead.',
    W: 560, H: 250,
    params: [
      { k: 'depth', label: 'Number of layers', type: 'range', min: 5, max: 60, v: 30 },
      { k: 'gain', label: 'Slope of each plain layer', type: 'range', min: 0.3, max: 1.3, step: 0.05, v: 0.8 },
      { k: 'eps', label: 'Slope of each residual branch ∂F/∂x', type: 'range', min: -0.05, max: 0.05, step: 0.01, v: 0.01 },
      { k: 'res', label: 'Show the residual network', type: 'check', v: true }
    ],
    tips: [
      { t: 'With slope 0.8 and 30 layers, the plain network passes back 0.8³⁰ ≈ 0.0012 of the signal to the first layer. Its early layers barely learn.', set: { depth: 30, gain: 0.8, res: true } },
      { t: 'Set the plain slope to 1.2. Now the signal explodes instead, about 237 times over 30 layers. Both extremes make training unstable.', set: { depth: 30, gain: 1.2 } },
      { t: 'Use 60 layers and a residual branch slope of −0.03. The residual signal is 0.97⁶⁰ ≈ 0.16, while the plain one at slope 0.8 is about 0.0000015.', set: { depth: 60, gain: 0.8, eps: -0.03, res: true } }
    ],
    draw(z) {
      const { g, p } = z;
      const plain = [], resid = [];
      for (let l = 0; l <= p.depth; l++) { plain.push(Math.pow(p.gain, l)); resid.push(Math.pow(1 + p.eps, l)); }
      const lg = v => Math.log10(Math.max(1e-12, v));
      const m = D.axes(g, z, [70, 14, 460, 180], [0, p.depth], [-8, 4], { nx: 5, ny: 6, xl: 'layers travelled backwards from the loss', yl: 'signal size', fx: v => Math.round(v), fy: v => '1e' + Math.round(v) });
      D.line(g, m.sx(0), m.sy(0), m.sx(p.depth), m.sy(0), z.col.line, 1, [4, 4]);
      const plot = (arr, c) => { g.save(); g.strokeStyle = c; g.lineWidth = 2.4; g.beginPath(); arr.forEach((v, i) => { const y = m.sy(clamp(lg(v), -8, 4)); if (i) g.lineTo(m.sx(i), y); else g.moveTo(m.sx(i), y); }); g.stroke(); g.restore(); };
      plot(plain, z.col.red);
      if (p.res) plot(resid, z.col.green);
      const yP = m.sy(clamp(lg(plain[p.depth]), -8, 4)), yR = m.sy(clamp(lg(resid[p.depth]), -8, 4));
      D.text(g, 'plain', m.sx(p.depth) - 4, yP + (yP < yR ? -6 : 16), { a: 'right', s: 12, b: true, c: z.col.red });
      if (p.res) D.text(g, 'residual', m.sx(p.depth) - 4, yR + (yR <= yP ? -6 : 16), { a: 'right', s: 12, b: true, c: z.col.green });
      const fm = v => v < 1e-3 || v > 1e3 ? v.toExponential(2) : f(v, 4);
      return `<span class="big">plain: signal = g<sup>L</sup>, &nbsp; residual: H(x) = F(x) + x, so ∂H/∂x = ∂F/∂x + 1</span><br>After ${p.depth} plain layers with slope ${f(p.gain, 2)} the signal is ${fm(plain[p.depth])}.${p.res ? ` With shortcuts it is (1 ${p.eps < 0 ? '−' : '+'} ${f(Math.abs(p.eps), 2)})<sup>${p.depth}</sup> = ${fm(resid[p.depth])}.` : ''} This is a one number sketch of the vanishing and exploding gradient problem. Real gradients are matrices, but the multiplying effect is the same.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 8: sliding windows and anchors */
  def('slidewin', {
    title: 'Sliding windows: counting the cost',
    sub: 'A fixed window scans a 640 × 480 image one stride at a time, and a classifier runs on every crop. Press Play to watch it scan, then change the stride and the window shape.',
    W: 560, H: 270,
    params: [
      { k: 'shape', label: 'Window shape', type: 'select', v: 'person', opts: [['person', 'Person 64 × 128 (tall)'], ['square', 'Square 96 × 96'], ['car', 'Car 128 × 64 (wide)']] },
      { k: 's', label: 'Stride (pixels)', type: 'range', min: 4, max: 64, step: 4, v: 8 },
      { k: 'gflops', label: 'Cost of one classifier pass (GFLOPs)', type: 'range', min: 0.5, max: 8, step: 0.5, v: 4 }
    ],
    tips: [
      { t: 'The lecture count: a 64 × 128 window at stride 8 gives 73 × 45 = 3,285 windows for one shape.', set: { shape: 'person', s: 8, gflops: 4 } },
      { t: 'Halve the stride to 4. The windows multiply by about 4, to 12,905. Fine strides are accurate but slow.', set: { s: 4 } },
      { t: 'Set the stride to 64. Only a few windows, but a person standing between two positions is cut in half and may be missed.', set: { s: 64 } }
    ],
    startAtZero: true,
    steps: () => 40,
    speed: () => 120,
    draw(z) {
      const { g, p, step } = z;
      const [w, h] = { person: [64, 128], square: [96, 96], car: [128, 64] }[p.shape];
      const W = 640, H = 480, sc = 0.45, X = 10, Y = 10;
      const nx = Math.floor((W - w) / p.s) + 1, ny = Math.floor((H - h) / p.s) + 1, N = nx * ny;
      D.rect(g, X, Y, W * sc, H * sc, { fill: z.col.bg, stroke: z.col.line });
      D.rect(g, X + 300 * sc, Y + 250 * sc, 60 * sc, 150 * sc, { fill: z.col.dark ? '#64748b' : '#94a3b8' });
      D.circle(g, X + 330 * sc, Y + 230 * sc, 20 * sc, { fill: z.col.dark ? '#64748b' : '#94a3b8' });
      g.save(); g.fillStyle = z.col.ink2; g.globalAlpha = 0.5;
      if (N <= 4000) for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) g.fillRect(X + (i * p.s + w / 2) * sc - 0.6, Y + (j * p.s + h / 2) * sc - 0.6, 1.2, 1.2);
      g.restore();
      const idx = step === 0 ? 0 : Math.round((step / 40) * (N - 1)), ci = idx % nx, cj = Math.floor(idx / nx);
      D.rect(g, X + ci * p.s * sc, Y + cj * p.s * sc, w * sc, h * sc, { stroke: z.col.red, w: 2.2 });
      D.text(g, 'dots: centre of every window position', X, Y + H * sc + 16, { s: 11, c: z.col.ink2 });
      const tf = N * p.gflops / 1000, secs = tf / 10;
      [`across: ⌊${640 - w} ÷ ${p.s}⌋ + 1 = ${nx}`, `down: ⌊${480 - h} ÷ ${p.s}⌋ + 1 = ${ny}`, `windows = ${nx} × ${ny} = ${N.toLocaleString('en-GB')}`, `window ${(idx + 1).toLocaleString('en-GB')} of ${N.toLocaleString('en-GB')}`, `compute ≈ ${f(tf, 2)} TFLOPs`, `≈ ${f(secs, 2)} s on a 10 TFLOP/s GPU`, `real time needs about 0.03 s`].forEach((t, i) => D.text(g, t, 312, 22 + i * 21, { s: 12, mono: true, c: i === 5 ? (secs > 0.03 ? z.col.red : z.col.green) : z.col.ink }));
      return `<span class="big">windows = (⌊(W − w) ÷ s⌋ + 1) × (⌊(H − h) ÷ s⌋ + 1)</span><br>And this is for one window shape at one scale. Real objects come in many sizes and shapes, so the count multiplies again. Neighbouring windows also recompute almost the same pixels. These are the four problems from the lecture: location, scale, shape and computation.`;
    }
  });

  const cornersOf = (xc, yc, w, h) => [xc - w / 2, yc - h / 2, xc + w / 2, yc + h / 2];
  const iouC = (a, b) => { const iw = Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])), ih = Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1])), I = iw * ih; const U = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - I; return U > 0 ? I / U : 0; };
  CVZ.iouC = iouC;
  def('anchor', {
    title: 'Anchor box plus correction: decoding and encoding',
    sub: 'Grey dashed: the anchor, a rough starting box. Green dotted: the true object. Blue: the box the network predicts by applying its four corrections t to the anchor.',
    W: 560, H: 275,
    params: [
      { k: 'tx', label: 't<sub>x</sub> (shift right, in anchor widths)', type: 'range', min: -0.6, max: 0.6, step: 0.01, v: 0.1 },
      { k: 'ty', label: 't<sub>y</sub> (shift down, in anchor heights)', type: 'range', min: -0.6, max: 0.6, step: 0.01, v: -0.05 },
      { k: 'tw', label: 't<sub>w</sub> (log of width ratio)', type: 'range', min: -1, max: 1, step: 0.01, v: 0.2 },
      { k: 'th', label: 't<sub>h</sub> (log of height ratio)', type: 'range', min: -1, max: 1, step: 0.01, v: -0.1 },
      { k: 'gt', label: 'True object', type: 'select', v: 'lec', opts: [['lec', 'Lecture: centre (108, 112), 75 × 110'], ['wide', 'A wide object: centre (90, 130), 130 × 70'], ['small', 'A small object: centre (120, 100), 30 × 40']] }
    ],
    tips: [
      { t: 'The defaults are the lecture decoding example: t = (0.10, −0.05, 0.20, −0.10) turns the anchor into a box centred at (106, 114), 73.28 × 108.58.', set: { tx: 0.1, ty: -0.05, tw: 0.2, th: -0.1, gt: 'lec' } },
      { t: 'Set t to the encoded target of the lecture object, (0.13, −0.07, 0.22, −0.09). The blue box now sits on the green one. This target is exactly what training asks the network to output.', set: { tx: 0.13, ty: -0.07, tw: 0.22, th: -0.09, gt: 'lec' } },
      { t: 'Pick the wide object. The anchor is tall, so the targets are large and the anchor overlaps it poorly. This is why detectors use several anchor shapes.', set: { gt: 'wide' } },
      { t: 'Move t<sub>w</sub> to −1 and then to +1. The width is multiplied by e<sup>−1</sup> ≈ 0.37 or e ≈ 2.72. It can never become negative.', set: { tw: -1 } }
    ],
    draw(z) {
      const { g, p } = z;
      const A = [100, 120, 60, 120];
      const G = { lec: [108, 112, 75, 110], wide: [90, 130, 130, 70], small: [120, 100, 30, 40] }[p.gt];
      const P = [A[0] + p.tx * A[2], A[1] + p.ty * A[3], A[2] * Math.exp(p.tw), A[3] * Math.exp(p.th)];
      const T = [(G[0] - A[0]) / A[2], (G[1] - A[1]) / A[3], Math.log(G[2] / A[2]), Math.log(G[3] / A[3])];
      const X = 20, Y = 8, S = 1.05, bx = b => { const c = cornersOf(...b); return [X + c[0] * S, Y + c[1] * S, (c[2] - c[0]) * S, (c[3] - c[1]) * S]; };
      D.rect(g, X, Y, 240 * S, 245 * S, { fill: z.col.bg, stroke: z.col.line });
      g.save(); g.beginPath(); g.rect(X, Y, 240 * S, 245 * S); g.clip();
      D.rect(g, ...bx(A), { stroke: z.col.ink2, w: 2, dash: [6, 4] });
      D.rect(g, ...bx(G), { stroke: z.col.green, w: 2.5, dash: [2, 3] });
      D.rect(g, ...bx(P), { stroke: z.col.cv, w: 2.5 });
      D.arrow(g, X + A[0] * S, Y + A[1] * S, X + P[0] * S, Y + P[1] * S, z.col.red, 2, 6);
      g.restore();
      const c = cornersOf(...P), fr = v => f(v, 2);
      const lines = [
        ['anchor', `(${A[0]}, ${A[1]}), ${A[2]} × ${A[3]}`],
        ['x = x_a + t_x w_a', fr(P[0])], ['y = y_a + t_y h_a', fr(P[1])], ['w = w_a e^t_w', fr(P[2])], ['h = h_a e^t_h', fr(P[3])],
        ['corners', `(${f(c[0], 1)}, ${f(c[1], 1)}, ${f(c[2], 1)}, ${f(c[3], 1)})`],
        ['target t*', `(${T.map(v => f(v, 3)).join(', ')})`],
        ['IoU anchor, object', f(iouC(cornersOf(...A), cornersOf(...G)), 3)], ['IoU predicted, object', f(iouC(cornersOf(...P), cornersOf(...G)), 3)]];
      lines.forEach(([a, b], i) => { D.text(g, a, 288, 22 + i * 26, { s: 11, c: z.col.ink2 }); D.text(g, b, 288, 35 + i * 26, { s: 12, mono: true, c: z.col.ink, b: i >= 7 }); });
      return `<span class="big">t<sub>x</sub> = (x − x<sub>a</sub>) ÷ w<sub>a</sub>, &nbsp; t<sub>y</sub> = (y − y<sub>a</sub>) ÷ h<sub>a</sub>, &nbsp; t<sub>w</sub> = ln(w ÷ w<sub>a</sub>), &nbsp; t<sub>h</sub> = ln(h ÷ h<sub>a</sub>)</span><br>Training turns the true box into the target t* with these formulas (encoding). At test time the network outputs t and the formulas run backwards (decoding). Shifts are measured in anchor sizes, so the same numbers work for small and large objects.`;
    }
  });

  def('anchorgrid', {
    title: 'How dense must the anchors be?',
    sub: 'Anchors of the same size as the object sit on a grid with stride s. The object can land anywhere between grid points. The best anchor must still overlap it well enough (IoU ≥ 0.5) for a small correction to work.',
    W: 560, H: 260,
    params: [
      { k: 'w', label: 'Object (and anchor) size w', type: 'range', min: 16, max: 96, step: 4, v: 32 },
      { k: 's', label: 'Anchor stride s', type: 'range', min: 4, max: 48, step: 2, v: 8 },
      { k: 'ox', label: 'Object position between grid points (0 = on a point, 0.5 = worst case)', type: 'range', min: 0, max: 0.5, step: 0.05, v: 0.5 }
    ],
    tips: [
      { t: 'RetinaNet finest level: stride 8, anchors of size 32. Even in the worst position the best anchor has IoU 0.62.', set: { w: 32, s: 8, ox: 0.5 } },
      { t: 'Raise the stride to 16 with the same 32 pixel object. The worst case drops below 0.5, so some objects get no good anchor.', set: { w: 32, s: 16, ox: 0.5 } },
      { t: 'Keep stride 16 but make the object 48 wide. s ÷ w = 0.33 is under 0.367 again, so it works. This is why larger anchors live on coarser grids.', set: { w: 48, s: 16, ox: 0.5 } }
    ],
    draw(z) {
      const { g, p } = z;
      const X = 10, Y = 10, A = 230, sc = A / 128;
      D.rect(g, X, Y, A, A, { fill: z.col.bg, stroke: z.col.line });
      for (let gx = 0; gx <= 128; gx += p.s) for (let gy = 0; gy <= 128; gy += p.s) D.circle(g, X + gx * sc, Y + gy * sc, 1.6, { fill: z.col.ink2 });
      const g0 = Math.floor(64 / p.s) * p.s, cx = g0 + p.ox * p.s, cy = g0 + p.ox * p.s;
      const obj = cornersOf(cx, cy, p.w, p.w), anc = cornersOf(g0, g0, p.w, p.w);
      g.save(); g.beginPath(); g.rect(X, Y, A, A); g.clip();
      D.rect(g, X + anc[0] * sc, Y + anc[1] * sc, p.w * sc, p.w * sc, { stroke: z.col.cv, w: 2, dash: [5, 3] });
      D.rect(g, X + obj[0] * sc, Y + obj[1] * sc, p.w * sc, p.w * sc, { stroke: z.col.green, w: 2.5 });
      g.restore();
      const iou = iouC(obj, anc);
      D.text(g, `nearest anchor IoU = ${f(iou, 3)}`, X, Y + A + 18, { s: 12, mono: true, b: true, c: iou >= 0.5 ? z.col.green : z.col.red });
      const m = D.axes(g, z, [300, 14, 240, 190], [0, 0.8], [0, 1], { nx: 4, ny: 4, xl: 'stride ÷ size, s ÷ w', fx: v => f(v, 1), fy: v => f(v, 2) });
      D.curve(g, r => { const I = Math.max(0, 1 - r / 2) ** 2; return I / (2 - I); }, [0, 0.8], m, z.col.cv, 2.2);
      D.line(g, m.sx(0), m.sy(0.5), m.sx(0.8), m.sy(0.5), z.col.red, 1, [4, 3]);
      D.line(g, m.sx(0.367), m.sy(0), m.sx(0.367), m.sy(1), z.col.ink2, 1, [2, 3]);
      const r = p.s / p.w, Iw = Math.max(0, 1 - r / 2) ** 2;
      D.circle(g, m.sx(Math.min(0.8, r)), m.sy(Iw / (2 - Iw)), 5, { fill: z.col.orange });
      D.text(g, 'worst case IoU', 306, 30, { s: 11, c: z.col.ink2, b: true });
      return `<span class="big">worst case: I = (w − s/2)², &nbsp; IoU = I ÷ (2w² − I) ≥ 0.5 &nbsp;⟺&nbsp; s ≤ 0.367 w</span><br>Here s ÷ w = ${f(r, 3)}, so the worst case IoU is ${f(Iw / (2 - Iw), 3)}${Iw / (2 - Iw) >= 0.5 ? ', which is enough' : ', which is too low'}. The orange dot marks your setting on the curve.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 9: targets and losses */
  def('assign', {
    title: 'Target assignment: which anchor learns which object',
    sub: 'Green boxes are the ground truth (a person and a dog). Each anchor is labelled by its best IoU: positive above the upper threshold, background below the lower one, ignored in between.',
    W: 560, H: 280,
    params: [
      { k: 'preset', label: 'Rule', type: 'select', v: 'retina', opts: [['retina', 'RetinaNet: positive ≥ 0.5, negative < 0.4'], ['rpn', 'Faster R-CNN RPN: positive ≥ 0.7, negative < 0.3'], ['custom', 'My own thresholds']] },
      { k: 'hi', label: 'Positive if IoU ≥', type: 'range', min: 0.3, max: 0.9, step: 0.05, v: 0.5, show: p => p.preset === 'custom' },
      { k: 'lo', label: 'Background if IoU <', type: 'range', min: 0.1, max: 0.7, step: 0.05, v: 0.4, show: p => p.preset === 'custom' }
    ],
    tips: [
      { t: 'RetinaNet rule: A1 and A3 become positives, A2 at 0.465 is ignored, A4 and A5 are background. Only 2 of 5 anchors will learn a box.', set: { preset: 'retina' } },
      { t: 'Switch to the RPN rule. A1 at 0.695 falls just short of 0.7 and is ignored, so only A3 stays positive. Stricter rules give fewer but cleaner positives.', set: { preset: 'rpn' } },
      { t: 'Choose your own thresholds and set both to 0.45. Nothing is ignored any more, so borderline anchors get a hard label either way.', set: { preset: 'custom', hi: 0.45, lo: 0.45 } }
    ],
    draw(z) {
      const { g, p } = z;
      const [hi, lo] = p.preset === 'retina' ? [0.5, 0.4] : p.preset === 'rpn' ? [0.7, 0.3] : [p.hi, Math.min(p.lo, p.hi)];
      const GT = [['person', [40, 30, 120, 190]], ['dog', [150, 110, 260, 190]]];
      const AN = [[30, 20, 110, 180], [55, 65, 135, 225], [160, 115, 270, 195], [280, 20, 330, 90], [70, 70, 150, 230]];
      const X = 10, Y = 10, S = 0.78;
      D.rect(g, X, Y, 340 * S, 260 * S, { fill: z.col.bg, stroke: z.col.line });
      const r = b => [X + b[0] * S, Y + b[1] * S, (b[2] - b[0]) * S, (b[3] - b[1]) * S];
      GT.forEach(([n, b]) => D.rect(g, ...r(b), { stroke: z.col.green, w: 3 }));
      D.text(g, 'green: true boxes, person on the left, dog on the right', X, Y + 260 * S + 18, { s: 11, b: true, c: z.col.green });
      const rows = AN.map((a, i) => {
        const ious = GT.map(([, b]) => iouC(a, b)), best = Math.max(...ious), j = ious.indexOf(best);
        const lab = best >= hi ? 'positive, ' + GT[j][0] : best < lo ? 'background' : 'ignored';
        const col = best >= hi ? z.col.cv : best < lo ? z.col.ink2 : z.col.orange;
        D.rect(g, ...r(a), { stroke: col, w: 1.8, dash: best >= hi ? null : [5, 3] });
        D.text(g, 'A' + (i + 1), X + a[2] * S - 3, Y + (i === 4 ? a[1] * S + 13 : a[3] * S - 4), { s: 11, b: true, c: col, a: 'right' });
        return [i, best, lab, col];
      });
      D.text(g, 'anchor   best IoU   label', 290, 24, { s: 11.5, mono: true, b: true, c: z.col.ink });
      rows.forEach(([i, b, l, c], k) => D.text(g, `A${i + 1}       ${f(b, 3).padEnd(6)}     ${l}`, 290, 50 + k * 24, { s: 11.5, mono: true, c }));
      const pos = rows.filter(x => x[2].startsWith('positive')).length, ign = rows.filter(x => x[2] === 'ignored').length;
      D.text(g, `box loss from ${pos} anchor${pos === 1 ? '' : 's'}`, 290, 190, { s: 12, b: true, c: z.col.ink });
      D.text(g, `class loss from ${5 - ign} anchors`, 290, 210, { s: 12, b: true, c: z.col.ink });
      return `<span class="big">IoU ≥ ${f(hi, 2)} → positive (class and box loss), &nbsp; IoU < ${f(lo, 2)} → background (class loss only), &nbsp; otherwise ignored</span><br>Real images have tens of thousands of anchors and only a handful of objects, so nearly every anchor ends up as background. That imbalance is the subject of the focal loss lesson.`;
    }
  });

  def('huber', {
    title: 'MSE, MAE and Huber: one bad box among four',
    sub: 'Left: each loss and its slope. Right: how much of the total loss and of the total gradient comes from the one bad box. The gradient is what training actually feels.',
    W: 560, H: 270,
    params: [
      { k: 'e4', label: 'Error of the bad box', type: 'range', min: 0, max: 20, step: 0.5, v: 10 },
      { k: 'd', label: 'Huber threshold δ', type: 'range', min: 0.25, max: 3, step: 0.25, v: 1 },
      { k: 'show', label: 'Left plot shows', type: 'select', v: 'loss', opts: [['loss', 'Loss'], ['grad', 'Gradient (slope)']] }
    ],
    tips: [
      { t: 'Lecture example: errors 0.2, 0.3, 0.4 and 10. With squared error the bad box gives 100 against 0.29 for the other three, about 345 times more.', set: { e4: 10, d: 1, show: 'loss' } },
      { t: 'Switch the plot to Gradient. MSE slope keeps growing with the error, Huber flattens at δ. With Huber the bad box pushes only about 1.1 times as hard as the three good boxes together.', set: { show: 'grad' } },
      { t: 'Set the bad error to 0.5. Now every box is inside the quadratic zone and Huber behaves exactly like ½e².', set: { e4: 0.5 } }
    ],
    draw(z) {
      const { g, p } = z;
      const d = p.d, hub = e => Math.abs(e) <= d ? 0.5 * e * e : d * (Math.abs(e) - 0.5 * d), hg = e => Math.max(-d, Math.min(d, e));
      const m = D.axes(g, z, [50, 14, 230, 190], [-4, 4], p.show === 'loss' ? [0, 8] : [-4, 4], { nx: 4, ny: 4, xl: 'error e', fy: v => f(v, 0) });
      if (p.show === 'loss') { D.curve(g, e => 0.5 * e * e, [-4, 4], m, z.col.red, 2); D.curve(g, e => Math.abs(e), [-4, 4], m, z.col.purple, 2, 200, [5, 3]); D.curve(g, hub, [-4, 4], m, z.col.cv, 2.6); }
      else { D.curve(g, e => e, [-4, 4], m, z.col.red, 2); D.curve(g, e => Math.sign(e), [-4, 4], m, z.col.purple, 2, 400, [5, 3]); D.curve(g, hg, [-4, 4], m, z.col.cv, 2.6); }
      [['½e² (MSE)', z.col.red], ['|e| (MAE)', z.col.purple], ['Huber', z.col.cv]].forEach(([t, c], i) => D.text(g, t, 128, 30 + i * 16, { s: 11, b: true, c, a: 'center' }));
      const E = [0.2, 0.3, 0.4, p.e4];
      const sq = E.map(e => e * e), hu = E.map(hub), gq = E, gh = E.map(hg);
      const share = a => a[3] / Math.max(1e-9, a[0] + a[1] + a[2]);
      const rows = [['', 'e²', 'Huber'], ...E.map((e, i) => [`box ${i + 1}, e = ${e}`, f(sq[i], 2), f(hu[i], 3)]), ['bad ÷ rest, loss', f(share(sq), 1) + '×', f(share(hu), 1) + '×'], ['bad ÷ rest, slope', f(share(gq), 1) + '×', f(share(gh), 1) + '×']];
      rows.forEach((r, i) => { D.text(g, r[0], 310, 26 + i * 25, { s: 11.5, c: i ? z.col.ink2 : z.col.ink, b: !i || i > 4 }); D.text(g, r[1], 470, 26 + i * 25, { s: 11.5, mono: true, a: 'right', c: z.col.red, b: !i || i > 4 }); D.text(g, r[2], 545, 26 + i * 25, { s: 11.5, mono: true, a: 'right', c: z.col.cv, b: !i || i > 4 }); });
      return `<span class="big">Huber<sub>δ</sub>(e) = ½e² if |e| ≤ δ, &nbsp; δ(|e| − ½δ) otherwise, &nbsp; slope = clip(e, −δ, δ)</span><br>Quadratic near zero, so it settles smoothly on the answer. Linear far away, so one wild box cannot drown out the rest. With δ = 1 this is the Smooth L1 loss on the lecture slide.`;
    }
  });

  def('focal', {
    title: 'Focal loss: stop easy background from drowning the objects',
    sub: 'An image has many easy background anchors and a few hard object anchors. Compare who owns the loss under cross entropy and under focal loss. p<sub>t</sub> is the probability the model gives to the correct answer.',
    W: 560, H: 270,
    params: [
      { k: 'gam', label: 'Focusing parameter γ', type: 'range', min: 0, max: 5, step: 0.5, v: 2 },
      { k: 'ne', label: 'Easy background anchors (power of 10)', type: 'range', min: 2, max: 6, step: 0.5, v: 5, fmt: v => Math.round(10 ** v).toLocaleString('en-GB') },
      { k: 'pe', label: 'p<sub>t</sub> of an easy anchor', type: 'range', min: 0.8, max: 0.999, step: 0.001, v: 0.99 },
      { k: 'ph', label: 'p<sub>t</sub> of a hard object anchor (10 of them)', type: 'range', min: 0.05, max: 0.6, step: 0.01, v: 0.1 }
    ],
    tips: [
      { t: 'Lecture example: 100,000 easy anchors at 0.99 and 10 hard ones at 0.10. Under cross entropy the easy ones own 97.8% of the loss. Under focal loss with γ = 2 they own about 0.5%.', set: { gam: 2, ne: 5, pe: 0.99, ph: 0.1 } },
      { t: 'Set γ to 0. Focal loss becomes plain cross entropy, and the background takes over again.', set: { gam: 0 } },
      { t: 'Set γ to 5. Even moderately easy examples are almost silenced. The RetinaNet paper found γ = 2 worked best.', set: { gam: 5 } }
    ],
    draw(z) {
      const { g, p } = z;
      const ce = q => -Math.log(q), fl = (q, gm) => Math.pow(1 - q, gm) * ce(q);
      const m = D.axes(g, z, [50, 14, 230, 190], [0, 1], [0, 3], { nx: 4, ny: 3, xl: 'p of the correct class, p_t', fx: v => f(v, 2), fy: v => f(v, 0) });
      [[0, z.col.ink2], [1, z.col.purple], [2, z.col.orange], [5, z.col.red]].forEach(([gm, c]) => D.curve(g, q => fl(q, gm), [0.02, 1], m, c, 1.4, 200, [4, 3]));
      D.curve(g, q => fl(q, p.gam), [0.02, 1], m, z.col.cv, 2.8);
      D.text(g, 'dashed: γ = 0, 1, 2, 5', 150, 30, { s: 11, c: z.col.ink2 }); D.text(g, `solid: γ = ${p.gam}`, 150, 46, { s: 11, b: true, c: z.col.cv });
      const N = Math.round(10 ** p.ne);
      const eCE = N * ce(p.pe), hCE = 10 * ce(p.ph), eFL = N * fl(p.pe, p.gam), hFL = 10 * fl(p.ph, p.gam);
      const bar = (y, lab, e, h) => {
        const tot = e + h, se = e / tot;
        D.text(g, lab, 310, y - 8, { s: 12, b: true, c: z.col.ink });
        D.rect(g, 310, y, 230 * se, 26, { fill: z.col.ink2 }); D.rect(g, 310 + 230 * se, y, 230 * (1 - se), 26, { fill: z.col.cv });
        D.text(g, `background ${f(100 * se, 2)}%`, 310, y + 44, { s: 11.5, mono: true, c: z.col.ink2 });
        D.text(g, `objects ${f(100 * (1 - se), 2)}%`, 540, y + 44, { s: 11.5, mono: true, a: 'right', c: z.col.cv });
      };
      bar(36, 'Cross entropy', eCE, hCE); bar(140, `Focal loss, γ = ${p.gam}`, eFL, hFL);
      return `<span class="big">CE = −ln p<sub>t</sub>, &nbsp; FL = −(1 − p<sub>t</sub>)<sup>γ</sup> ln p<sub>t</sub></span><br>Easy anchor: CE ${f(ce(p.pe), 5)}, FL ${fl(p.pe, p.gam).toExponential(2)}. Hard anchor: CE ${f(ce(p.ph), 3)}, FL ${f(fl(p.ph, p.gam), 3)}. The factor (1 − p<sub>t</sub>)<sup>γ</sup> shrinks the loss of confident, correct answers and barely touches the hard ones.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 10: IoU, NMS and architectures */
  def('iou', {
    title: 'Intersection over union',
    sub: 'Green is the true box A = (50, 50, 150, 150). Move the predicted box B. The shaded part is the intersection, the outline of both together is the union.',
    W: 560, H: 250,
    params: [
      { k: 'x', label: 'B left edge x<sub>1</sub>', type: 'range', min: 0, max: 200, v: 80 },
      { k: 'y', label: 'B top edge y<sub>1</sub>', type: 'range', min: 0, max: 200, v: 70 },
      { k: 'w', label: 'B width', type: 'range', min: 10, max: 200, v: 100 },
      { k: 'h', label: 'B height', type: 'range', min: 10, max: 200, v: 100 },
      { k: 'thr', label: 'Threshold α for a hit', type: 'range', min: 0.3, max: 0.95, step: 0.05, v: 0.5 }
    ],
    tips: [
      { t: 'The lecture box B = (80, 70, 180, 170): intersection 70 × 80 = 5,600, union 14,400, IoU 0.389. A miss at α = 0.5.', set: { x: 80, y: 70, w: 100, h: 100 } },
      { t: 'The second lecture prediction (60, 55, 160, 155) gives IoU 0.747, a hit.', set: { x: 60, y: 55, w: 100, h: 100 } },
      { t: 'Make B huge (x = 0, y = 0, 200 × 200). It covers A completely, yet IoU is only 0.25 because the union is large. IoU punishes boxes that are too big as well as too small.', set: { x: 0, y: 0, w: 200, h: 200 } },
      { t: 'Raise α to 0.75, the stricter COCO style criterion. Boxes that passed at 0.5 now fail.', set: { x: 60, y: 55, w: 100, h: 100, thr: 0.75 } }
    ],
    draw(z) {
      const { g, p } = z;
      const A = [50, 50, 150, 150], B = [p.x, p.y, p.x + p.w, p.y + p.h];
      const X = 10, Y = 10, S = 0.95;
      D.rect(g, X, Y, 230 * S, 230 * S, { fill: z.col.bg, stroke: z.col.line });
      g.save(); g.beginPath(); g.rect(X, Y, 230 * S, 230 * S); g.clip();
      const ix1 = Math.max(A[0], B[0]), iy1 = Math.max(A[1], B[1]), ix2 = Math.min(A[2], B[2]), iy2 = Math.min(A[3], B[3]);
      if (ix2 > ix1 && iy2 > iy1) D.rect(g, X + ix1 * S, Y + iy1 * S, (ix2 - ix1) * S, (iy2 - iy1) * S, { fill: z.col.dark ? 'rgba(250,204,21,.45)' : 'rgba(250,204,21,.6)' });
      D.rect(g, X + A[0] * S, Y + A[1] * S, 100 * S, 100 * S, { stroke: z.col.green, w: 2.5 });
      D.rect(g, X + B[0] * S, Y + B[1] * S, p.w * S, p.h * S, { stroke: z.col.cv, w: 2.5 });
      g.restore();
      const iw = Math.max(0, ix2 - ix1), ih = Math.max(0, iy2 - iy1), I = iw * ih, U = 10000 + p.w * p.h - I, v = I / U;
      const lines = [`A = (50, 50, 150, 150), area 10,000`, `B = (${B.join(', ')}), area ${(p.w * p.h).toLocaleString('en-GB')}`, `overlap ${iw} × ${ih} = ${I.toLocaleString('en-GB')}`, `union = ${(10000).toLocaleString('en-GB')} + ${(p.w * p.h).toLocaleString('en-GB')} − ${I.toLocaleString('en-GB')} = ${U.toLocaleString('en-GB')}`, `IoU = ${f(v, 3)}`, v > p.thr ? `hit at α = ${f(p.thr, 2)} (true positive)` : `miss at α = ${f(p.thr, 2)}`];
      lines.forEach((t, i) => D.text(g, t, 250, 30 + i * 26, { s: 12, mono: true, b: i >= 4, c: i === 5 ? (v > p.thr ? z.col.green : z.col.red) : z.col.ink }));
      return `<span class="big">IoU(A, B) = |A ∩ B| ÷ |A ∪ B| = |A ∩ B| ÷ (|A| + |B| − |A ∩ B|)</span><br>IoU is 0 exactly when the boxes do not overlap and 1 exactly when they are identical. It does not change if you scale the whole picture, because both areas scale by the same factor.`;
    }
  });

  const NMSBOX = [
    { id: 'P1', c: 'person', s: 0.92, b: [40, 40, 120, 200] }, { id: 'P4', c: 'person', s: 0.88, b: [108, 52, 186, 212] }, { id: 'P2', c: 'person', s: 0.85, b: [46, 48, 126, 206] },
    { id: 'D1', c: 'dog', s: 0.75, b: [200, 130, 300, 200] }, { id: 'P3', c: 'person', s: 0.60, b: [30, 30, 112, 195] }, { id: 'C1', c: 'cat', s: 0.55, b: [204, 126, 298, 198] }, { id: 'D2', c: 'dog', s: 0.40, b: [212, 138, 306, 206] }];
  def('nms', {
    title: 'Non-maximum suppression, one box at a time',
    sub: 'Seven raw detections: two people, a dog, and one cat box on the dog. Boxes are taken in order of score. Each kept box removes lower scoring boxes of the same class that overlap it by more than the threshold.',
    W: 560, H: 285,
    params: [
      { k: 'thr', label: 'IoU threshold', type: 'range', min: 0.05, max: 0.9, step: 0.05, v: 0.5 },
      { k: 'mode', label: 'Method', type: 'select', v: 'hard', opts: [['hard', 'Standard NMS (delete)'], ['soft', 'Soft-NMS (decay the score, σ = 0.5)']] },
      { k: 'agn', label: 'Ignore classes (class agnostic)', type: 'check', v: false }
    ],
    tips: [
      { t: 'Press Play at threshold 0.5. P2 and P3 are duplicates of P1, D2 of D1. The result is P1, P4, D1 and C1.', set: { thr: 0.5, mode: 'hard', agn: false }, play: true },
      { t: 'The cat box C1 survives on top of the dog because NMS runs per class. Tick class agnostic and D1 removes it.', set: { thr: 0.5, agn: true }, play: true },
      { t: 'Lower the threshold to 0.05. P4, a real second person who overlaps P1 slightly (IoU 0.076), is now wrongly deleted. Crowds suffer most.', set: { thr: 0.05, mode: 'hard', agn: false }, play: true },
      { t: 'Switch to Soft-NMS. Nothing is deleted. Duplicates lose most of their score while P4 keeps almost all of it.', set: { thr: 0.05, mode: 'soft', agn: false }, play: true }
    ],
    startAtZero: true,
    steps: () => NMSBOX.length,
    speed: () => 900,
    draw(z) {
      const { g, p, step } = z;
      const st = NMSBOX.map(o => ({ ...o, score: o.s, state: 'pending', by: '' }));
      let cur = -1;
      for (let k = 0; k < step; k++) {
        const order = st.map((o, i) => i).filter(i => st[i].state === 'pending').sort((a, b) => st[b].score - st[a].score);
        if (!order.length) break;
        const i = order[0]; cur = i; st[i].state = 'kept';
        st.forEach((o, j) => {
          if (o.state !== 'pending' || (!p.agn && o.c !== st[i].c)) return;
          const v = iouC(o.b, st[i].b);
          if (p.mode === 'hard') { if (v > p.thr) { o.state = 'gone'; o.by = `${st[i].id}, IoU ${f(v, 3)}`; } }
          else if (v > 0) { o.score = o.score * Math.exp(-v * v / 0.5); o.by = `× ${f(Math.exp(-v * v / 0.5), 3)} by ${st[i].id}`; }
        });
      }
      const X = 10, Y = 10, S = 0.8;
      D.rect(g, X, Y, 320 * S, 240 * S, { fill: z.col.bg, stroke: z.col.line });
      const colOf = o => o.c === 'person' ? z.col.cv : o.c === 'dog' ? z.col.orange : z.col.purple;
      st.forEach((o, i) => {
        const r = [X + o.b[0] * S, Y + o.b[1] * S, (o.b[2] - o.b[0]) * S, (o.b[3] - o.b[1]) * S];
        g.save(); g.globalAlpha = o.state === 'gone' ? 0.25 : o.state === 'pending' ? 0.6 : 1;
        D.rect(g, ...r, { stroke: colOf(o), w: o.state === 'kept' ? 3 : 1.5, dash: o.state === 'kept' ? null : [5, 3] });
        g.restore();
        if (i === cur) D.rect(g, r[0] - 3, r[1] - 3, r[2] + 6, r[3] + 6, { stroke: z.col.red, w: 1.5 });
      });
      D.text(g, 'blue person, orange dog, purple cat', X, Y + 240 * S + 16, { s: 11, c: z.col.ink2 });
      D.text(g, 'box   class    score   status', 280, 22, { s: 11.5, mono: true, b: true, c: z.col.ink });
      st.slice().sort((a, b) => b.s - a.s).forEach((o, k) => {
        const status = o.state === 'kept' ? 'KEPT' : o.state === 'gone' ? 'removed' : 'waiting';
        D.text(g, `${o.id}    ${o.c.padEnd(7)}  ${f(o.score, 3).padEnd(5)}   ${status}`, 280, 46 + k * 30, { s: 11.5, mono: true, b: o.state === 'kept', c: o.state === 'gone' ? z.col.ink2 : colOf(o) });
        if (o.by) D.text(g, o.state === 'gone' ? 'by ' + o.by : o.by, 312, 60 + k * 30, { s: 10, mono: true, c: z.col.ink2 });
      });
      const kept = st.filter(o => o.state === 'kept').map(o => o.id);
      return `<b>${step === 0 ? 'Press Play or Step. Boxes are processed in order of score: P1 0.92, P4 0.88, P2 0.85, D1 0.75, P3 0.60, C1 0.55, D2 0.40.' : `Kept so far: ${kept.join(', ') || 'none'}.`}</b><br>${p.mode === 'soft' ? 'Soft-NMS multiplies each overlapping score by e<sup>−IoU² ÷ σ</sup> instead of deleting it. A final score threshold then removes the boxes that fell low.' : 'NMS uses only scores and box to box IoU. No ground truth is involved at test time.'}`;
    }
  });

  def('bilinear', {
    title: 'Bilinear interpolation: reading between pixels',
    sub: 'A feature map only has values at whole number positions. To read it at (x, y) in between, blend the four neighbours. Each corner\'s weight is the area of the rectangle on the opposite side of the point.',
    W: 560, H: 260,
    params: [
      { k: 'x', label: 'Sample x (between 2 and 3)', type: 'range', min: 2, max: 3, step: 0.05, v: 2.3 },
      { k: 'y', label: 'Sample y (between 4 and 5)', type: 'range', min: 4, max: 5, step: 0.05, v: 4.6 },
      { k: 'v', label: 'Corner values f(2,4) f(3,4) f(2,5) f(3,5)', type: 'text', v: '10 20 30 50' }
    ],
    tips: [
      { t: 'The lecture point (2.3, 4.6) with corners 10, 20, 30 and 50 gives 26.8. The nearest corner, (2, 5), has the largest weight, 0.42.', set: { x: 2.3, y: 4.6, v: '10 20 30 50' } },
      { t: 'Move the point onto a corner, for example (3, 5). That corner\'s weight becomes 1 and the answer is exactly its value.', set: { x: 3, y: 5 } },
      { t: 'Use the values 42 43 52 53, which follow f = 10y + x. At (2.5, 4.5) you get 47.5 = 10 × 4.5 + 2.5 exactly. Bilinear interpolation reproduces such formulas exactly, which the RoIAlign example relies on.', set: { v: '42 43 52 53', x: 2.5, y: 4.5 } }
    ],
    draw(z) {
      const { g, p } = z;
      let v = String(p.v).trim().split(/[\s,]+/).map(Number);
      if (v.length < 4 || v.some(a => !isFinite(a))) v = [10, 20, 30, 50];
      const u = p.x - 2, t = p.y - 4;
      const w = [(1 - u) * (1 - t), u * (1 - t), (1 - u) * t, u * t];
      const X0 = 60, Y0 = 38, L = 180;
      const px = X0 + u * L, py = Y0 + t * L;
      const cols = [z.col.cv, z.col.orange, z.col.purple, z.col.green];
      g.save(); g.globalAlpha = 0.3;
      D.rect(g, px, py, X0 + L - px, Y0 + L - py, { fill: cols[0] });
      D.rect(g, X0, py, px - X0, Y0 + L - py, { fill: cols[1] });
      D.rect(g, px, Y0, X0 + L - px, py - Y0, { fill: cols[2] });
      D.rect(g, X0, Y0, px - X0, py - Y0, { fill: cols[3] });
      g.restore();
      D.rect(g, X0, Y0, L, L, { stroke: z.col.ink2, w: 1.5 });
      const corners = [[X0, Y0, '(2, 4)'], [X0 + L, Y0, '(3, 4)'], [X0, Y0 + L, '(2, 5)'], [X0 + L, Y0 + L, '(3, 5)']];
      corners.forEach(([cx, cy, lab], i) => { D.circle(g, cx, cy, 7, { fill: cols[i] }); D.text(g, `${lab} = ${v[i]}`, cx, cy + (i < 2 ? -14 : 22), { s: 11.5, mono: true, a: 'center', c: z.col.ink, b: true }); });
      D.circle(g, px, py, 6, { fill: z.col.red });
      const val = w.reduce((s, a, i) => s + a * v[i], 0);
      const rows = [`u = x − 2 = ${f(u, 2)}, v = y − 4 = ${f(t, 2)}`, ...['(2, 4)', '(3, 4)', '(2, 5)', '(3, 5)'].map((lab, i) => `w${lab} = ${['(1 − u)(1 − v)', 'u(1 − v)', '(1 − u)v', 'uv'][i]} = ${f(w[i], 3)}`), `sum of weights = ${f(w.reduce((a, b) => a + b, 0), 3)}`, `f(${f(p.x, 2)}, ${f(p.y, 2)}) = ${f(val, 3)}`];
      rows.forEach((r, i) => D.text(g, r, 300, 30 + i * 28, { s: 12, mono: true, b: i === 6, c: i >= 1 && i <= 4 ? cols[i - 1] : z.col.ink }));
      return `<span class="big">f(x, y) = (1 − u)(1 − v) f<sub>00</sub> + u(1 − v) f<sub>10</sub> + (1 − u)v f<sub>01</sub> + uv f<sub>11</sub></span><br>The weights always add to 1, and the result changes smoothly with x and y. That smoothness is why the crop and resize step (RoIAlign) can pass gradients back, so a two stage detector trains end to end.`;
    }
  });

  def('pyramid', {
    title: 'Feature pyramid and anchor count',
    sub: 'A backbone halves the map size at each stage. RetinaNet predicts from five levels, P3 to P7. Change the input size and the anchors per cell to see how many predictions one image produces.',
    W: 560, H: 250,
    params: [
      { k: 'n', label: 'Input size (square)', type: 'range', min: 320, max: 1280, step: 64, v: 640 },
      { k: 'A', label: 'Anchors per cell A', type: 'range', min: 1, max: 9, v: 9 },
      { k: 'K', label: 'Classes K', type: 'range', min: 1, max: 100, v: 80 }
    ],
    tips: [
      { t: 'The lecture case: 640 × 640 gives levels of 80, 40, 20, 10 and 5 cells, 8,525 cells, 76,725 anchors and about 6.1 million class scores.', set: { n: 640, A: 9, K: 80 } },
      { t: 'Set A to 1. Anchor free detectors such as FCOS predict one box per cell, nine times fewer predictions.', set: { A: 1 } },
      { t: 'Double the input to 1280. Every level grows 4 times, and so does the work. Larger images help small objects but cost time.', set: { n: 1280, A: 9 } }
    ],
    draw(z) {
      const { g, p } = z;
      const lv = [3, 4, 5, 6, 7].map(l => ({ l, st: 2 ** l, s: Math.ceil(p.n / 2 ** l) }));
      let cells = 0;
      lv.forEach((o, i) => {
        cells += o.s * o.s;
        const w = Math.max(12, 200 * o.s / 160), x = 120 - w / 2, y = 205 - i * 40;
        D.rect(g, x, y - 26, w, 26, { fill: z.col.cv, stroke: z.col.line });
        D.text(g, `P${o.l}: ${o.s} × ${o.s}, stride ${o.st}${i === 0 ? ', small objects' : i === 4 ? ', large objects' : ''}`, 236, y - 9, { s: 12, mono: true, c: z.col.ink });
      });
      const an = cells * p.A;
      [`cells ${cells.toLocaleString('en-GB')}`, `anchors ${an.toLocaleString('en-GB')}`, `class scores ${(an * p.K).toLocaleString('en-GB')}`].forEach((t, i) => D.text(g, t, 20 + i * 180, 236, { s: 12, mono: true, b: true, c: z.col.ink }));
      return `<span class="big">cells per level = (input ÷ stride)², &nbsp; anchors = cells × A, &nbsp; class scores = anchors × K</span><br>Fine levels (P3) have small strides and catch small objects. Coarse levels (P7) see the whole scene and catch large ones. The same class and box heads are shared across all levels.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 11: evaluating detectors */
  const parseDets = s => String(s).split('\n').map(l => l.trim().split(/\s+/)).filter(a => a.length >= 3 && isFinite(+a[1]))
    .map(a => ({ n: a[0], s: +a[1], tp: /^(t|tp|y|1)$/i.test(a[2]) }));
  /* cumulative precision and recall down a ranked list */
  const prList = (tps, nGT) => { let tp = 0, fp = 0; return tps.map(t => { if (t) tp++; else fp++; return { p: tp / (tp + fp), r: nGT ? tp / nGT : 0, tp, fp }; }); };
  const envAt = (pts, r) => Math.max(0, ...pts.filter(q => q.r >= r - 1e-9).map(q => q.p));
  const apOf = (pts, mode) => {
    if (mode === '11' || mode === '101') { const n = mode === '11' ? 10 : 100; let s = 0; for (let i = 0; i <= n; i++) s += envAt(pts, i / n); return s / (n + 1); }
    let s = 0, prev = 0; pts.forEach(q => { if (q.r > prev + 1e-9) { s += (q.r - prev) * envAt(pts, q.r); prev = q.r; } }); return s;
  };

  def('prsweep', {
    title: 'The score threshold trades precision against recall',
    sub: 'The slide 84 detections. Cup, Cat and Dog are real objects. Keep only the boxes whose score is at least the threshold, then count.',
    W: 560, H: 270,
    params: [
      { k: 'thr', label: 'Score threshold', type: 'range', min: 0, max: 1, step: 0.01, v: 0.4 },
      { k: 'gt', label: 'Real objects in the image', type: 'range', min: 1, max: 8, step: 1, v: 3, help: 'Objects beyond the true detections below were never found.' },
      { k: 'd', label: 'Detections: name, score, T (true) or F (false)', type: 'area', v: 'Dog 0.99 T\nCat 0.90 T\nHuman 0.50 F\nCup 0.30 T\nLaundry 0.10 F\nTortilla 0.02 F' }
    ],
    tips: [
      { t: 'Threshold 0.4 keeps Dog, Cat and Human. TP 2, FP 1, so precision and recall are both 0.67.', set: { thr: 0.4, gt: 3 } },
      { t: 'Threshold 0.6 drops the false Human. Precision becomes 1.00, recall stays 0.67.', set: { thr: 0.6, gt: 3 } },
      { t: 'Threshold 0 keeps all six boxes. Recall is 1.00 but precision falls to 0.50.', set: { thr: 0, gt: 3 } },
      { t: 'Compare 0.2 and 0.4. Precision goes from 0.75 down to 0.67 even though the threshold rose. This zig-zag is why AP uses the envelope.', set: { thr: 0.2, gt: 3 } },
      { t: 'Set real objects to 5. Two objects were never detected, so no threshold can give recall above 0.6.', set: { gt: 5 } }
    ],
    draw(z) {
      const { g, p } = z;
      let ds = parseDets(p.d); if (!ds.length) ds = parseDets('Dog 0.99 T\nCat 0.90 T');
      ds.sort((a, b) => b.s - a.s);
      const nGT = Math.max(p.gt, ds.filter(d => d.tp).length);
      const kept = ds.filter(d => d.s >= p.thr), TP = kept.filter(d => d.tp).length, FP = kept.length - TP;
      const P = kept.length ? TP / kept.length : 1, R = TP / nGT, F1 = P + R ? 2 * P * R / (P + R) : 0;
      D.text(g, 'name        score   truth', 14, 22, { s: 11.5, mono: true, b: true, c: z.col.ink });
      const rowY = i => 44 + i * Math.min(24, 170 / Math.max(1, ds.length - 1));
      let lineDrawn = false;
      ds.forEach((d, i) => {
        const on = d.s >= p.thr;
        if (!on && !lineDrawn) { D.line(g, 10, rowY(i) - 15, 250, rowY(i) - 15, z.col.red, 2, [6, 4]); lineDrawn = true; }
        D.text(g, `${d.n.slice(0, 10).padEnd(10)}  ${d.s.toFixed(2).padEnd(5)}   ${d.tp ? 'TP' : 'FP'}`, 14, rowY(i), { s: 11.5, mono: true, b: on, c: on ? (d.tp ? z.col.green : z.col.red) : z.col.ink2 });
      });
      D.text(g, `threshold ${f(p.thr, 2)}: kept ${kept.length}, TP ${TP}, FP ${FP}, FN ${nGT - TP}`, 14, 250, { s: 12, b: true, c: z.col.ink });
      const m = D.axes(g, z, [340, 16, 196, 186], [0, 1], [0, 1], { xl: 'recall', yl: 'precision', nx: 2, ny: 2 });
      const ths = [...new Set(ds.map(d => d.s))].sort((a, b) => b - a);
      const pts = ths.map(t => { const k = ds.filter(d => d.s >= t), tp = k.filter(d => d.tp).length; return [tp / nGT, tp / k.length]; });
      g.save(); g.strokeStyle = z.col.ink2; g.lineWidth = 1; g.setLineDash([3, 3]); g.beginPath();
      pts.forEach(([r, pp], i) => i ? g.lineTo(m.sx(r), m.sy(pp)) : g.moveTo(m.sx(r), m.sy(pp))); g.stroke(); g.restore();
      pts.forEach(([r, pp]) => D.circle(g, m.sx(r), m.sy(pp), 3.5, { fill: z.col.ink2 }));
      if (kept.length) D.circle(g, m.sx(R), m.sy(P), 7, { stroke: z.col.cv, w: 3 });
      return `<span class="big">P = TP ÷ (TP + FP) = ${kept.length ? f(P, 2) : 'undefined'}, &nbsp; R = TP ÷ (TP + FN) = ${f(R, 2)}, &nbsp; F1 = ${f(F1, 3)}</span><br>Raising the threshold usually raises precision and lowers recall. The grey dots are every possible threshold, the blue ring is yours. Rather than argue about one threshold, the PR curve looks at all of them.`;
    }
  });

  def('apcurve', {
    title: 'Average precision, rank by rank',
    sub: 'Ten detections of one class, ranked by score, marked TP or FP. Red is the raw precision, blue is the envelope, and the shaded area is AP.',
    W: 560, H: 275,
    params: [
      { k: 'seq', label: 'TP or FP for each rank, best first', type: 'text', v: 'T T F T F T F T F F' },
      { k: 'gt', label: 'Ground truth objects', type: 'range', min: 1, max: 12, step: 1, v: 6 },
      { k: 'mode', label: 'Method', type: 'select', v: 'all', opts: [['all', 'All points (area under the envelope)'], ['11', '11 points (PASCAL VOC 2007)'], ['101', '101 points (COCO)']] }
    ],
    tips: [
      { t: 'Press Play to add one detection at a time. Rank 3 is an FP, so precision drops to 0.667 while recall stays 0.333.', set: { seq: 'T T F T F T F T F F', gt: 6, mode: 'all' }, play: true },
      { t: 'The lecture answer is AP = 0.674. Switch to 11 points: it also gives 0.674 for this list.', set: { seq: 'T T F T F T F T F F', gt: 6, mode: '11' } },
      { t: 'Move the false positives to the end: T T T T T F F F F F. Same counts, but AP rises to 0.833, the highest recall reached. Ranking matters.', set: { seq: 'T T T T T F F F F F', gt: 6, mode: 'all' } },
      { t: 'Put them first instead: F F F F F T T T T T. AP falls to 0.417, half of the best order.', set: { seq: 'F F F F F T T T T T', gt: 6, mode: 'all' } },
      { t: 'Raise the ground truth count to 10. The same detections now miss more objects and AP falls.', set: { seq: 'T T F T F T F T F F', gt: 10, mode: 'all' } }
    ],
    steps: z => Math.max(1, String(z.p.seq).trim().split(/[\s,]+/).filter(Boolean).length),
    speed: () => 650,
    draw(z) {
      const { g, p, step } = z;
      let all = String(p.seq).trim().split(/[\s,]+/).filter(Boolean).map(s => /^t/i.test(s));
      if (!all.length) all = [true];
      const nGT = Math.max(p.gt, all.filter(Boolean).length);
      const shown = all.slice(0, step), pts = prList(shown, nGT);
      D.text(g, 'rank  TP?  P      R', 12, 20, { s: 11, mono: true, b: true, c: z.col.ink });
      const dy = Math.min(22, 225 / all.length);
      pts.forEach((q, i) => D.text(g, `${String(i + 1).padStart(3)}   ${shown[i] ? 'TP' : 'FP'}  ${q.p.toFixed(3)}  ${q.r.toFixed(3)}`, 12, 40 + i * dy, { s: 11, mono: true, c: shown[i] ? z.col.green : z.col.red, b: i === pts.length - 1 }));
      const m = D.axes(g, z, [250, 14, 290, 210], [0, 1], [0, 1.05], { xl: 'recall', yl: 'precision', nx: 5, ny: 2, fy: v => f(v, 1) });
      if (pts.length) {
        const ap = apOf(pts, p.mode);
        g.save(); g.fillStyle = z.col.cv; g.globalAlpha = 0.18; g.beginPath(); g.moveTo(m.sx(0), m.sy(0));
        let prev = 0;
        pts.forEach(q => { if (q.r > prev + 1e-9) { const e = envAt(pts, q.r); g.lineTo(m.sx(prev), m.sy(e)); g.lineTo(m.sx(q.r), m.sy(e)); prev = q.r; } });
        g.lineTo(m.sx(prev), m.sy(0)); g.closePath(); g.fill(); g.restore();
        prev = 0; let first = true;
        g.save(); g.strokeStyle = z.col.cv; g.lineWidth = 2.5; g.beginPath();
        pts.forEach(q => { if (q.r > prev + 1e-9) { const e = envAt(pts, q.r); if (first) { g.moveTo(m.sx(prev), m.sy(e)); first = false; } else g.lineTo(m.sx(prev), m.sy(e)); g.lineTo(m.sx(q.r), m.sy(e)); prev = q.r; } });
        g.stroke(); g.restore();
        g.save(); g.strokeStyle = z.col.red; g.lineWidth = 1.5; g.beginPath();
        pts.forEach((q, i) => i ? g.lineTo(m.sx(q.r), m.sy(q.p)) : g.moveTo(m.sx(q.r), m.sy(q.p))); g.stroke(); g.restore();
        pts.forEach(q => D.circle(g, m.sx(q.r), m.sy(q.p), 3, { fill: z.col.red }));
        if (p.mode !== 'all') { const n = p.mode === '11' ? 10 : 100; for (let i = 0; i <= n; i += (n === 100 ? 5 : 1)) D.circle(g, m.sx(i / n), m.sy(envAt(pts, i / n)), 2.5, { fill: z.col.orange }); }
        D.text(g, `AP = ${f(ap, 3)}`, 530, 40, { a: 'right', s: 15, b: true, c: z.col.cv });
        const name = p.mode === 'all' ? 'Σ (r<sub>k</sub> − r<sub>k−1</sub>) · p<sub>interp</sub>(r<sub>k</sub>)' : `mean of p<sub>interp</sub> at ${p.mode} recall points`;
        return `<span class="big">p<sub>interp</sub>(r) = max precision at any recall ≥ r, &nbsp; AP = ${name} = ${f(ap, 3)}</span><br>After ${pts.length} of ${all.length} detections: precision ${f(pts[pts.length - 1].p, 3)}, recall ${f(pts[pts.length - 1].r, 3)}. Recall can never pass ${f(all.filter(Boolean).length / nGT, 3)}, because only ${all.filter(Boolean).length} of ${nGT} objects are ever found.`;
      }
      return 'Press Play or Step to add the detections one by one.';
    }
  });

  def('cocoap', {
    title: 'COCO AP: averaging over ten IoU thresholds',
    sub: 'The same detector is scored at IoU 0.50, 0.55 up to 0.95. A stricter threshold demands tighter boxes, so AP falls. COCO reports the mean of all ten.',
    W: 560, H: 255,
    params: [
      { k: 'v', label: 'AP at IoU 0.50, 0.55, ..., 0.95', type: 'text', v: '0.80 0.78 0.75 0.71 0.66 0.60 0.52 0.42 0.27 0.08' },
      { k: 'hl', label: 'Highlight IoU threshold', type: 'range', min: 0.5, max: 0.95, step: 0.05, v: 0.75 }
    ],
    tips: [
      { t: 'The lecture numbers. AP at 0.5 is 0.80 but the COCO average is only 0.559, because tight boxes are demanded.', set: { v: '0.80 0.78 0.75 0.71 0.66 0.60 0.52 0.42 0.27 0.08' } },
      { t: 'A detector with sloppy boxes: same 0.80 at IoU 0.5, but the COCO AP drops to 0.289.', set: { v: '0.80 0.70 0.55 0.40 0.25 0.12 0.05 0.02 0 0' } },
      { t: 'A detector with very tight boxes: the curve stays high and the COCO AP reaches 0.692. Both detectors look equal under the PASCAL VOC rule.', set: { v: '0.80 0.80 0.79 0.78 0.77 0.75 0.72 0.66 0.55 0.30' } }
    ],
    draw(z) {
      const { g, p } = z;
      let v = String(p.v).trim().split(/[\s,]+/).map(Number).filter(isFinite).slice(0, 10);
      while (v.length < 10) v.push(0);
      v = v.map(a => clamp(a, 0, 1));
      const mean = v.reduce((a, b) => a + b, 0) / 10, hi = Math.round((p.hl - 0.5) / 0.05);
      const X = 60, Y = 30, Wd = 470, Ht = 170;
      const m = D.axes(g, z, [X, Y, Wd, Ht], [0, 10], [0, 1], { nx: 1, ny: 4, fx: () => '', yl: 'AP' });
      D.bars(g, z, [X, Y, Wd, Ht], v, { max: 1, gap: 6, colour: i => i === hi ? z.col.orange : z.col.cv });
      v.forEach((a, i) => { D.text(g, f(0.5 + 0.05 * i, 2), X + (i + 0.5) * Wd / 10, Y + Ht + 16, { a: 'center', s: 11, c: z.col.ink2 }); D.text(g, a.toFixed(2), X + (i + 0.5) * Wd / 10, m.sy(a) - 5, { a: 'center', s: 11, b: true, c: z.col.ink }); });
      D.line(g, X, m.sy(mean), X + Wd, m.sy(mean), z.col.red, 2, [6, 4]);
      D.text(g, `dashed line: COCO AP = mean = ${f(mean, 3)}`, X + Wd, 16, { a: 'right', s: 12, b: true, c: z.col.red });
      D.text(g, 'IoU threshold', X + Wd / 2, Y + Ht + 32, { a: 'center', s: 12, b: true, c: z.col.ink2 });
      return `<span class="big">AP<sub>COCO</sub> = (1 ÷ 10) Σ AP<sub>t</sub>, &nbsp; t = 0.50, 0.55, ..., 0.95</span><br>AP@0.5 = ${f(v[0], 2)}, AP@${f(p.hl, 2)} = ${f(v[hi], 2)}, COCO AP = ${f(mean, 3)}. This is why COCO numbers (30 to 50) look small next to PASCAL VOC AP@0.5 numbers (70 to 90).`;
    }
  });

  def('pareto', {
    title: 'Speed against accuracy: the Pareto frontier',
    sub: 'Each dot is a detector. A model is dominated if another one is at least as accurate and at least as fast, and better in one of the two. The rest form the frontier.',
    W: 560, H: 270,
    params: [
      { k: 'm', label: 'Models: name, mAP, latency in ms', type: 'area', v: 'A 21 30\nB 24 45\nC 30 90\nD 32 80\nE 34 150\nF 37 200\nG 28 120' },
      { k: 'b', label: 'Latency budget (ms)', type: 'range', min: 20, max: 260, step: 5, v: 100 }
    ],
    tips: [
      { t: 'The lecture example. C and G are dominated by D, which is both more accurate and faster. The frontier is A, B, D, E and F.', set: { m: 'A 21 30\nB 24 45\nC 30 90\nD 32 80\nE 34 150\nF 37 200\nG 28 120', b: 100 } },
      { t: 'A phone app with a 50 ms budget. The best choice is B with mAP 24.', set: { b: 50 } },
      { t: 'Change G to "G 33 100". No model is both at least as accurate and at least as fast, so G joins the frontier.', set: { m: 'A 21 30\nB 24 45\nC 30 90\nD 32 80\nE 34 150\nF 37 200\nG 33 100' } },
      { t: 'Add a new model "H 38 120". It dominates both E and F, and the frontier gets shorter.', set: { m: 'A 21 30\nB 24 45\nC 30 90\nD 32 80\nE 34 150\nF 37 200\nG 28 120\nH 38 120', b: 260 } }
    ],
    draw(z) {
      const { g, p } = z;
      let ms = String(p.m).split('\n').map(l => l.trim().split(/\s+/)).filter(a => a.length >= 3 && isFinite(+a[1]) && isFinite(+a[2])).map(a => ({ n: a[0].slice(0, 6), a: +a[1], t: +a[2] }));
      if (!ms.length) ms = [{ n: 'A', a: 21, t: 30 }];
      ms.forEach(x => { x.by = ms.filter(y => y !== x && y.a >= x.a && y.t <= x.t && (y.a > x.a || y.t < x.t)).sort((u, w) => w.a - u.a || u.t - w.t)[0]; });
      const front = ms.filter(x => !x.by).sort((a, b) => a.t - b.t);
      const tMax = Math.max(p.b, ...ms.map(x => x.t)) * 1.1, aMin = Math.min(...ms.map(x => x.a)), aMax = Math.max(...ms.map(x => x.a));
      const pad = Math.max(2, (aMax - aMin) * 0.15);
      const m = D.axes(g, z, [60, 14, 300, 210], [0, tMax], [aMin - pad, aMax + pad], { xl: 'latency (ms), lower is better', yl: 'mAP', fx: v => Math.round(v), fy: v => Math.round(v) });
      g.save(); g.fillStyle = z.col.green; g.globalAlpha = 0.08; g.fillRect(60, 14, m.sx(p.b) - 60, 210); g.restore();
      D.line(g, m.sx(p.b), 14, m.sx(p.b), 224, z.col.green, 2, [6, 4]);
      g.save(); g.strokeStyle = z.col.cv; g.lineWidth = 2; g.beginPath();
      front.forEach((x, i) => i ? g.lineTo(m.sx(x.t), m.sy(x.a)) : g.moveTo(m.sx(x.t), m.sy(x.a))); g.stroke(); g.restore();
      const ok = ms.filter(x => x.t <= p.b), best = ok.length ? ok.reduce((a, b) => b.a > a.a || (b.a === a.a && b.t < a.t) ? b : a) : null;
      ms.forEach(x => {
        D.circle(g, m.sx(x.t), m.sy(x.a), 6, x.by ? { stroke: z.col.ink2, w: 2, fill: z.col.bg } : { fill: z.col.cv });
        if (x === best) D.circle(g, m.sx(x.t), m.sy(x.a), 10, { stroke: z.col.orange, w: 3 });
        D.text(g, x.n, m.sx(x.t) + 9, m.sy(x.a) + (x.by ? 16 : -9), { s: 12, b: true, c: x.by ? z.col.ink2 : z.col.ink });
      });
      D.text(g, 'frontier', 384, 26, { s: 12, b: true, c: z.col.cv });
      front.slice(0, 7).forEach((x, i) => D.text(g, `${x.n}  mAP ${x.a}, ${x.t} ms`, 384, 46 + i * 18, { s: 11, mono: true, c: z.col.ink }));
      const dom = ms.filter(x => x.by);
      D.text(g, 'dominated', 384, 60 + Math.min(7, front.length) * 18, { s: 12, b: true, c: z.col.ink2 });
      dom.slice(0, 4).forEach((x, i) => D.text(g, `${x.n}  by ${x.by.n}`, 384, 80 + Math.min(7, front.length) * 18 + i * 18, { s: 11, mono: true, c: z.col.ink2 }));
      return `<b>${best ? `Best model within ${p.b} ms: ${best.n} (mAP ${best.a}, ${best.t} ms).` : `No model fits within ${p.b} ms.`}</b> Frontier: ${front.map(x => x.n).join(', ')}.<br>Moving along the frontier you cannot gain accuracy without losing speed. A dominated model is never the right pick, whatever the budget.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 12: what segmentation predicts */
  def('pixelsm', {
    title: 'One pixel, five classes: SoftMax then argmax',
    sub: 'The network gives every pixel one raw score (logit) per class. SoftMax turns them into probabilities that add to 1, and the largest one names the pixel.',
    W: 560, H: 250,
    params: [
      { k: 'z0', label: 'Road logit', type: 'range', min: -4, max: 4, step: 0.01, v: 0 },
      { k: 'z1', label: 'Car logit', type: 'range', min: -4, max: 4, step: 0.01, v: -0.51 },
      { k: 'z2', label: 'Person logit', type: 'range', min: -4, max: 4, step: 0.01, v: -0.91 },
      { k: 'z3', label: 'Building logit', type: 'range', min: -4, max: 4, step: 0.01, v: 0.7 },
      { k: 'z4', label: 'Sky logit', type: 'range', min: -4, max: 4, step: 0.01, v: 2.78 },
      { k: 'sig', label: 'Use separate sigmoids instead', type: 'check', v: false }
    ],
    tips: [
      { t: 'The lecture pixel. SoftMax gives 0.05, 0.03, 0.02, 0.10 and 0.80, so the pixel becomes Sky.', set: { z0: 0, z1: -0.51, z2: -0.91, z3: 0.7, z4: 2.78, sig: false } },
      { t: 'Raise Building to 2.78 as well. Sky and Building tie at about 0.47 each. A boundary pixel often looks like this.', set: { z3: 2.78 } },
      { t: 'Add 2 to every logit. The probabilities do not change at all, only the differences matter.', set: { z0: 2, z1: 1.49, z2: 1.09, z3: 2.7, z4: 4, sig: false } },
      { t: 'Tick sigmoids. Each class now gets its own yes or no probability and they no longer add to 1. That suits multi-label pixels, not one label per pixel.', set: { sig: true } }
    ],
    draw(z) {
      const { g, p } = z;
      const names = ['Road', 'Car', 'Person', 'Building', 'Sky'];
      const zs = [p.z0, p.z1, p.z2, p.z3, p.z4];
      const mx = Math.max(...zs), ex = zs.map(v => Math.exp(v - mx)), S = ex.reduce((a, b) => a + b, 0);
      const pr = p.sig ? zs.map(v => 1 / (1 + Math.exp(-v))) : ex.map(e => e / S);
      const win = zs.indexOf(mx);
      const cols = [z.col.ink2, z.col.cv, z.col.orange, z.col.purple, z.col.green];
      D.text(g, 'class', 14, 24, { s: 12, b: true, c: z.col.ink });
      D.text(g, 'logit', 110, 24, { s: 12, b: true, c: z.col.ink });
      D.text(g, p.sig ? 'sigmoid' : 'probability', 180, 24, { s: 12, b: true, c: z.col.ink });
      names.forEach((n, i) => {
        const y = 52 + i * 36;
        D.text(g, n, 14, y + 4, { s: 13, b: i === win, c: i === win ? z.col.ink : z.col.ink2 });
        D.text(g, zs[i].toFixed(2), 110, y + 4, { s: 12, mono: true, c: z.col.ink2 });
        D.rect(g, 180, y - 10, 300, 18, { fill: z.col.bg, stroke: z.col.line, w: 1 });
        D.rect(g, 180, y - 10, 300 * pr[i], 18, { fill: cols[i] });
        D.text(g, pr[i].toFixed(3), 488, y + 4, { s: 12, mono: true, b: i === win, c: z.col.ink });
      });
      const sum = pr.reduce((a, b) => a + b, 0);
      D.text(g, `sum = ${sum.toFixed(3)}`, 180, 238, { s: 12, mono: true, b: true, c: Math.abs(sum - 1) < 1e-6 ? z.col.green : z.col.red });
      D.text(g, `argmax: ${names[win].toUpperCase()}`, 488, 238, { a: 'right', s: 13, b: true, c: cols[win] });
      return `<span class="big">p<sub>c</sub> = e<sup>z<sub>c</sub></sup> ÷ Σ<sub>k</sub> e<sup>z<sub>k</sub></sup>, &nbsp; label = argmax<sub>c</sub> p<sub>c</sub> = argmax<sub>c</sub> z<sub>c</sub></span><br>The exponential keeps the order of the logits, so the winning class is the same with or without SoftMax. At test time you can take the argmax of the logits directly. SoftMax is needed for the loss and for confidence values.`;
    }
  });

  /* a 16 x 16 mask: a 6 x 6 blob, a thin line and a 2 x 2 object */
  const segMask = off => {
    const m = Array.from({ length: 16 }, () => Array(16).fill(0));
    for (let r = 2; r <= 7; r++) for (let c = 2 + off; c <= 7 + off; c++) m[r][c] = 1;
    for (let r = 11; r <= 12; r++) for (let c = 1; c <= 14; c++) m[r][c] = 2;
    for (let r = 1; r <= 2; r++) for (let c = 13; c <= 14; c++) m[r][c] = 3;
    return m;
  };
  def('downup', {
    title: 'Shrink a mask, grow it back, measure the damage',
    sub: 'A 16 × 16 mask with a blob (36 pixels), a line 2 pixels thick (28 pixels) and a small 2 × 2 object. Each block of the coarse map takes a class only if that class fills more than half of it.',
    W: 560, H: 280,
    params: [
      { k: 'fac', label: 'Downsampling factor', type: 'select', num: true, v: 4, opts: [[1, '×1 (no change)'], [2, '×2'], [4, '×4'], [8, '×8'], [16, '×16']] },
      { k: 'off', label: 'Shift the blob right (pixels)', type: 'range', min: 0, max: 4, step: 1, v: 0 },
      { k: 'rule', label: 'Block rule', type: 'select', v: 'maj', opts: [['maj', 'Strict majority (more than half)'], ['any', 'Any pixel present (like max pooling)']] }
    ],
    tips: [
      { t: 'The lecture case, ×4. Only one block of the blob survives (IoU 0.444), and the line and the small object vanish. All foreground together scores 0.235.', set: { fac: 4, off: 0, rule: 'maj' } },
      { t: 'Try ×2. The blob lines up with the blocks and comes back perfectly, but the 2 pixel structures still never win a block.', set: { fac: 2, off: 0, rule: 'maj' } },
      { t: 'Try ×8. The blob IoU rises to 0.562, higher than at ×4. Damage depends on how a shape sits on the grid, not only on the factor.', set: { fac: 8, off: 0, rule: 'maj' } },
      { t: 'Stay at ×8 and shift the blob 2 pixels right. It now straddles two blocks, wins neither, and disappears completely (IoU 0).', set: { fac: 8, off: 2, rule: 'maj' } },
      { t: 'Switch the rule to any pixel present. Nothing is lost, but every shape grows into fat blocks. Neither rule can recover the true outline.', set: { fac: 4, off: 0, rule: 'any' } }
    ],
    draw(z) {
      const { g, p } = z;
      const m = segMask(p.off), F = p.fac, n = 16 / F;
      const coarse = Array.from({ length: n }, (_, R) => Array.from({ length: n }, (_, C) => {
        const cnt = [0, 0, 0, 0];
        for (let r = R * F; r < (R + 1) * F; r++) for (let c = C * F; c < (C + 1) * F; c++) cnt[m[r][c]]++;
        if (p.rule === 'any') { let best = 0; for (let k = 1; k < 4; k++) if (cnt[k] > (best ? cnt[best] : 0)) best = k; return best; }
        for (let k = 1; k < 4; k++) if (cnt[k] * 2 > F * F) return k;
        return 0;
      }));
      const up = m.map((row, r) => row.map((_, c) => coarse[Math.floor(r / F)][Math.floor(c / F)]));
      const pal = [z.col.bg, z.col.cv, z.col.orange, z.col.purple];
      const grid = (mm, X, cell, lines) => {
        mm.forEach((row, r) => row.forEach((v, c) => D.rect(g, X + c * cell, 30 + r * cell, cell, cell, { fill: pal[v] })));
        D.rect(g, X, 30, mm.length * cell, mm.length * cell, { stroke: z.col.line, w: 1 });
        if (lines) for (let k = 1; k < lines; k++) { const t = k * mm.length * cell / lines; D.line(g, X + t, 30, X + t, 30 + mm.length * cell, z.col.ink2, 0.6); D.line(g, X, 30 + t, X + mm.length * cell, 30 + t, z.col.ink2, 0.6); }
      };
      grid(m, 10, 10, n); grid(coarse, 196, 160 / n, 0); grid(up, 382, 10, 0);
      D.text(g, 'original 16 × 16', 10, 20, { s: 12, b: true, c: z.col.ink });
      D.text(g, `coarse ${n} × ${n}`, 196, 20, { s: 12, b: true, c: z.col.ink });
      D.text(g, 'upsampled back', 382, 20, { s: 12, b: true, c: z.col.ink });
      const iou = k => { let i = 0, u = 0; m.forEach((row, r) => row.forEach((v, c) => { const a = k ? v === k : v > 0, b = k ? up[r][c] === k : up[r][c] > 0; if (a && b) i++; if (a || b) u++; })); return u ? i / u : 1; };
      const res = [['blob', 1], ['line', 2], ['small object', 3], ['all foreground', 0]].map(([nm, k]) => `${nm} ${iou(k).toFixed(3)}`);
      D.text(g, 'IoU with the original:', 10, 222, { s: 12, b: true, c: z.col.ink });
      D.text(g, res.slice(0, 2).join('     '), 10, 244, { s: 12, mono: true, c: z.col.ink2 });
      D.text(g, res.slice(2).join('     '), 10, 264, { s: 12, mono: true, c: z.col.ink2 });
      return `<b>No upsampling method can bring back what the coarse map never held.</b> A structure narrower than about two cells of the coarse grid (here ${2 * F} pixels) cannot survive. This is the reason segmentation networks pass early, high resolution features to the decoder.`;
    }
  });

  def('rfstack', {
    title: 'Which input pixels can one neuron see?',
    sub: 'A stack of four 3 × 3 layers drawn in one dimension. The top cell is one output neuron. Each row below shows the cells that feed it, down to the input. Edit the stride and dilation of each layer.',
    W: 560, H: 270,
    params: [
      { k: 'L', label: 'Layers as stride,dilation (first layer first)', type: 'text', v: '1,1 2,1 1,2 1,4' }
    ],
    tips: [
      { t: 'The practice problem: (1,1) (2,1) (1,2) (1,4). The receptive field grows 3, 5, 13, 29.', set: { L: '1,1 2,1 1,2 1,4' } },
      { t: 'Four plain layers: 1,1 1,1 1,1 1,1. Each adds 2, so the field is only 9.', set: { L: '1,1 1,1 1,1 1,1' } },
      { t: 'Stride 2 on layers 2 and 4: the field reaches 13, but the map is now 4 times smaller in each direction.', set: { L: '1,1 2,1 1,1 2,1' } },
      { t: 'Dilations 1, 2, 4, 8 with no stride: a field of 31 and the map keeps its full size.', set: { L: '1,1 1,2 1,4 1,8' } },
      { t: 'Gridding: four layers all with dilation 2. Only every second input pixel is ever used, so the gaps never influence the output.', set: { L: '1,2 1,2 1,2 1,2' } }
    ],
    draw(z) {
      const { g, p } = z;
      let layers = String(p.L).trim().split(/\s+/).map(t => t.split(',').map(Number)).filter(a => a.length === 2 && a.every(v => Number.isInteger(v) && v >= 1 && v <= 8)).slice(0, 5);
      if (!layers.length) layers = [[1, 1]];
      let sets = [new Set([0])];
      for (let l = layers.length - 1; l >= 0; l--) {
        const [s, d] = layers[l], nxt = new Set();
        sets[0].forEach(q => { for (let t = -1; t <= 1; t++) nxt.add(q * s + t * d); });
        sets.unshift(nxt);
      }
      const inp = [...sets[0]], lo = Math.min(...inp), hi = Math.max(...inp), span = hi - lo + 1;
      const cell = Math.min(14, 420 / span), X0 = 340 - span * cell / 2 - lo * cell;
      const rows = sets.length, dy = Math.min(40, 190 / (rows - 1));
      const jumps = [1]; layers.forEach(([s]) => jumps.push(jumps[jumps.length - 1] * s));
      sets.forEach((st, i) => {
        const y = 230 - i * dy, j = jumps[i];
        [...st].forEach(q => D.rect(g, X0 + q * j * cell, y, Math.max(2, cell - 1), 12, { fill: i === 0 ? z.col.cv : i === rows - 1 ? z.col.red : z.col.orange }));
        D.text(g, i === 0 ? `input: field ${span}` : i === rows - 1 ? 'output neuron' : `after layer ${i}`, 8, y + 10, { s: 11, b: true, c: z.col.ink2 });
      });
      let r = 1, j = 1; const seq = [1];
      layers.forEach(([s, d]) => { r += 2 * d * j; j *= s; seq.push(r); });
      const used = inp.length;
      D.text(g, `receptive field after each layer: ${seq.join(', ')}`, 8, 22, { s: 12, b: true, c: z.col.ink });
      D.text(g, `input pixels actually used: ${used} of ${span}${used < span ? ' (gaps: gridding)' : ''}. Map shrinks by ${j}× in each direction.`, 8, 42, { s: 12, c: used < span ? z.col.red : z.col.ink2 });
      return `<span class="big">r<sub>l</sub> = r<sub>l−1</sub> + (k − 1) · d<sub>l</sub> · j<sub>l−1</sub>, &nbsp; j<sub>l</sub> = j<sub>l−1</sub> · s<sub>l</sub></span><br>j is the jump, the distance in input pixels between neighbouring cells of a layer. Stride grows the field by shrinking the map. Dilation grows it while keeping the map at full size, which is what segmentation wants.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 13: segmentation architectures */
  const parseGrid = (s, fb) => {
    const rows = String(s).split(/[;\n]/).map(r => r.trim().split(/[\s,]+/).filter(Boolean).map(Number)).filter(r => r.length);
    if (!rows.length || rows.some(r => r.length !== rows[0].length || r.some(v => !isFinite(v)))) return fb;
    return rows;
  };
  const gridDraw = (g, z, m, X, Y, cell, o = {}) => {
    const flat = m.flat(), lo = Math.min(...flat), hi = Math.max(...flat);
    m.forEach((row, r) => row.forEach((v, c) => {
      const t = hi > lo ? (v - lo) / (hi - lo) : 0.5;
      D.rect(g, X + c * cell, Y + r * cell, cell, cell, { fill: o.fill ? o.fill(v, r, c) : `rgba(18,110,130,${0.12 + 0.75 * t})`, stroke: z.col.line, w: 1 });
      D.text(g, o.fmt ? o.fmt(v) : String(+v.toFixed(1)), X + (c + 0.5) * cell, Y + (r + 0.5) * cell + 4, { a: 'center', s: o.s || 11, mono: true, b: true, c: z.col.ink });
    }));
  };

  def('upsample', {
    title: 'Making a map bigger: copy or blend',
    sub: 'A 2 × 2 score map is enlarged. Nearest neighbour copies each value into a block. Bilinear blends the neighbours. Neither one adds information the small map did not have.',
    W: 560, H: 270,
    params: [
      { k: 'v', label: 'Small map values (row by row)', type: 'text', v: '0 100; 100 200' },
      { k: 'm', label: 'Method', type: 'select', v: 'bil', opts: [['near', 'Nearest neighbour (copy)'], ['bil', 'Bilinear, half pixel centres'], ['ac', 'Bilinear, align corners']] },
      { k: 'F', label: 'Factor', type: 'select', num: true, v: 2, opts: [[2, '×2'], [3, '×3'], [4, '×4']] }
    ],
    tips: [
      { t: 'The lecture case. Bilinear gives rows 0, 25, 75, 100 then 25, 50, 100, 125 and so on: a smooth ramp.', set: { v: '0 100; 100 200', m: 'bil', F: 2 } },
      { t: 'Switch to nearest neighbour. Each value is copied into a 2 × 2 block. Simple and exact, but blocky edges.', set: { v: '0 100; 100 200', m: 'near', F: 2 } },
      { t: 'Align corners keeps the corner values on the corners and spreads the rest evenly: 0, 33, 67, 100. Frameworks differ, so check which one yours uses.', set: { v: '0 100; 100 200', m: 'ac', F: 2 } },
      { t: 'Use the class IDs 1 3; 1 3 (road and car). Bilinear invents 1.5 and 2.5, values that are not classes. Masks must be resized with nearest neighbour.', set: { v: '1 3; 1 3', m: 'bil', F: 2 } }
    ],
    draw(z) {
      const { g, p } = z;
      const a = parseGrid(p.v, [[0, 100], [100, 200]]);
      const n = a.length, mcol = a[0].length, F = p.F, N = n * F, M = mcol * F;
      const at = (y, x) => {
        const x0 = Math.floor(x), y0 = Math.floor(y), x1 = Math.min(x0 + 1, mcol - 1), y1 = Math.min(y0 + 1, n - 1), u = x - x0, v = y - y0;
        return (1 - u) * (1 - v) * a[y0][x0] + u * (1 - v) * a[y0][x1] + (1 - u) * v * a[y1][x0] + u * v * a[y1][x1];
      };
      const src = (i, Nn, nn) => p.m === 'ac' ? (Nn > 1 ? i * (nn - 1) / (Nn - 1) : 0) : clamp((i + 0.5) / F - 0.5, 0, nn - 1);
      const out = Array.from({ length: N }, (_, r) => Array.from({ length: M }, (_, c) => p.m === 'near' ? a[Math.floor(r / F)][Math.floor(c / F)] : at(src(r, N, n), src(c, M, mcol))));
      const cs = Math.min(46, 120 / Math.max(n, mcol)), co = Math.min(40, 230 / Math.max(N, M));
      D.text(g, `small map ${n} × ${mcol}`, 14, 22, { s: 12, b: true, c: z.col.ink });
      gridDraw(g, z, a, 14, 34, cs, { s: 12 });
      D.arrow(g, 30 + mcol * cs, 34 + n * cs / 2, 150 + 20, 34 + n * cs / 2, z.col.ink2, 2);
      D.text(g, `enlarged ${N} × ${M}`, 200, 22, { s: 12, b: true, c: z.col.ink });
      gridDraw(g, z, out, 200, 34, co, { s: co < 30 ? 9 : 11, fmt: v => String(Math.round(v * 10) / 10) });
      const ints = new Set(a.flat()), fake = p.m !== 'near' && out.flat().some(v => !ints.has(v) && Math.abs(v - Math.round(v)) > 1e-9);
      return `<b>${p.m === 'near' ? 'Copying keeps the original values but makes blocky boundaries.' : 'Blending makes a smooth ramp but nothing knows where a real boundary lies between two cells.'}</b>${fake && [...ints].every(Number.isInteger) && [...ints].length <= 6 ? ' If these numbers were class IDs, the in-between values would be classes that are not there.' : ''} Images and score maps may be resized bilinearly. Label masks must use nearest neighbour.`;
    }
  });

  const TK = { corner: [[1, 0, 1], [0, 1, 0], [1, 0, 1]], ones3: [[1, 1, 1], [1, 1, 1], [1, 1, 1]], ones4: [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], ones2: [[1, 1], [1, 1]] };
  def('tconv', {
    title: 'Transposed convolution: learned upsampling, step by step',
    sub: 'Each input value multiplies the whole kernel and the result is added into the output at a position that moves by the stride. Where placements overlap, values add up.',
    W: 560, H: 290,
    params: [
      { k: 'x', label: 'Input map', type: 'text', v: '1 2; 3 4' },
      { k: 'k', label: 'Kernel', type: 'select', v: 'corner', opts: [['corner', '3 × 3 corners and centre (lecture)'], ['ones3', '3 × 3 all ones'], ['ones4', '4 × 4 all ones'], ['ones2', '2 × 2 all ones']] },
      { k: 's', label: 'Stride', type: 'select', num: true, v: 2, opts: [[1, '1'], [2, '2'], [3, '3']] },
      { k: 'cnt', label: 'Show how many placements cover each cell', type: 'check', v: false }
    ],
    tips: [
      { t: 'Press Play. The lecture case gives a 5 × 5 output. The centre receives 1 + 2 + 3 + 4 = 10 because all four corner weights land there.', set: { x: '1 2; 3 4', k: 'corner', s: 2, cnt: false }, play: true },
      { t: 'Use the 3 × 3 ones kernel and tick the count. Cells are covered 1, 2 or 4 times in a regular pattern. That uneven overlap causes checkerboard artefacts.', set: { k: 'ones3', s: 2, cnt: true } },
      { t: 'Use the 4 × 4 kernel with stride 2. The kernel size is divisible by the stride, so the inner cells are covered evenly. This is the usual fix.', set: { k: 'ones4', s: 2, cnt: true } },
      { t: 'The 2 × 2 kernel with stride 2 never overlaps: each value fills its own 2 × 2 block, exactly like nearest neighbour with learnable weights.', set: { k: 'ones2', s: 2, cnt: false } }
    ],
    steps: z => { const a = parseGrid(z.p.x, [[1, 2], [3, 4]]); return Math.min(9, a.length * a[0].length); },
    speed: () => 900,
    draw(z) {
      const { g, p, step } = z;
      let a = parseGrid(p.x, [[1, 2], [3, 4]]); a = a.slice(0, 3).map(r => r.slice(0, 3));
      const K = TK[p.k], k = K.length, s = p.s, n = a.length, mm = a[0].length;
      const H = (n - 1) * s + k, W = (mm - 1) * s + k;
      const out = Array.from({ length: H }, () => Array(W).fill(0)), cov = Array.from({ length: H }, () => Array(W).fill(0));
      let cur = null;
      for (let q = 0; q < Math.min(step, n * mm); q++) {
        const i = Math.floor(q / mm), j = q % mm; cur = [i, j];
        for (let u = 0; u < k; u++) for (let v = 0; v < k; v++) { out[i * s + u][j * s + v] += a[i][j] * K[u][v]; cov[i * s + u][j * s + v]++; }
      }
      D.text(g, 'input', 14, 22, { s: 12, b: true, c: z.col.ink });
      gridDraw(g, z, a, 14, 32, 34, { fill: (v, r, c) => cur && cur[0] === r && cur[1] === c ? z.col.orange : z.col.bg });
      D.text(g, `kernel ${k} × ${k}`, 14, 160, { s: 12, b: true, c: z.col.ink });
      gridDraw(g, z, K, 14, 170, 20, { fill: v => v ? 'rgba(18,110,130,0.35)' : z.col.bg, s: 10 });
      const cell = Math.min(36, 250 / Math.max(H, W)), X = 190;
      D.text(g, `output ${H} × ${W} = (${n} − 1) × ${s} + ${k}`, X, 22, { s: 12, b: true, c: z.col.ink });
      const show = p.cnt ? cov : out;
      gridDraw(g, z, show, X, 32, cell, { s: cell < 26 ? 9 : 11, fill: (v, r, c) => cur && r >= cur[0] * s && r < cur[0] * s + k && c >= cur[1] * s && c < cur[1] * s + k ? 'rgba(240,140,40,0.35)' : `rgba(18,110,130,${0.08 + 0.12 * (p.cnt ? cov[r][c] : (out[r][c] ? 2 : 0))})` });
      return `<span class="big">H<sub>out</sub> = (H<sub>in</sub> − 1) · s − 2p + k</span><br>${step === 0 ? 'Press Play or Step to place the first input value.' : `Placed ${Math.min(step, n * mm)} of ${n * mm} values.`} The kernel weights are learned, so the network learns how to spread each coarse value. Transposed convolution is the transpose of the matrix of an ordinary convolution, which is how it got its name.`;
    }
  });

  def('dilation', {
    title: 'Dilated convolution and ASPP',
    sub: 'A 3 × 3 kernel whose taps are spread r cells apart. It still has 9 weights, but it reaches further. Enter several rates to see ASPP, which runs them side by side.',
    W: 560, H: 300,
    params: [
      { k: 'r', label: 'Dilation rates (one for a single kernel, several for ASPP)', type: 'text', v: '2' },
      { k: 'os', label: 'Output stride of the feature map', type: 'select', num: true, v: 1, opts: [[1, '1 (full resolution)'], [8, '8'], [16, '16 (DeepLabv3)']] }
    ],
    tips: [
      { t: 'Rate 1 is an ordinary 3 × 3 kernel. Rate 2 covers 5 × 5 with the same 9 weights.', set: { r: '2', os: 1 } },
      { t: 'Rate 4 covers 9 × 9. The skipped pixels are simply not multiplied. Atrous means with holes in French.', set: { r: '4', os: 1 } },
      { t: 'ASPP with rates 1, 3 and 6 on one map: three views of the same pixel, from local to wide, then concatenated.', set: { r: '1 3 6', os: 1 } },
      { t: 'DeepLabv3 uses rates 6, 12 and 18 at output stride 16. Each feature cell is 16 pixels, so the branches see about 208, 400 and 592 input pixels across.', set: { r: '6 12 18', os: 16 } }
    ],
    draw(z) {
      const { g, p } = z;
      let rs = String(p.r).trim().split(/[\s,]+/).map(Number).filter(v => Number.isInteger(v) && v >= 1 && v <= 24).slice(0, 4);
      if (!rs.length) rs = [1];
      const span = 2 * Math.max(...rs) + 1, G = Math.max(span + 2, 9), cell = Math.min(24, 260 / G), X = 14, Y = 26, c0 = Math.floor(G / 2);
      for (let r = 0; r < G; r++) for (let c = 0; c < G; c++) D.rect(g, X + c * cell, Y + r * cell, cell, cell, { fill: z.col.bg, stroke: z.col.line, w: 0.6 });
      const cols = [z.col.cv, z.col.orange, z.col.purple, z.col.green];
      rs.slice().reverse().forEach((rate, idx) => {
        const i = rs.length - 1 - idx, col = cols[i % 4], e = 2 * rate + 1;
        D.rect(g, X + (c0 - rate) * cell, Y + (c0 - rate) * cell, e * cell, e * cell, { stroke: col, w: 1.5, dash: [4, 3] });
        for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) D.rect(g, X + (c0 + a * rate) * cell + 2, Y + (c0 + b * rate) * cell + 2, cell - 4, cell - 4, { fill: col });
      });
      const tx = 310;
      D.text(g, 'rate   covers     input pixels', tx, 34, { s: 12, mono: true, b: true, c: z.col.ink });
      rs.forEach((rate, i) => { const e = 2 * rate + 1; D.text(g, `${String(rate).padStart(3)}    ${(e + ' × ' + e).padEnd(9)}  ${e * p.os}`, tx, 58 + i * 22, { s: 12, mono: true, c: cols[i % 4], b: true }); });
      D.text(g, 'weights per kernel: 9 for every rate', tx, 70 + rs.length * 22, { s: 12, c: z.col.ink2 });
      D.text(g, 'parameters of a 256 → 256 layer:', tx, 92 + rs.length * 22, { s: 12, c: z.col.ink2 });
      D.text(g, '3 × 3 × 256 × 256 = 589,824', tx, 112 + rs.length * 22, { s: 12, mono: true, c: z.col.ink });
      if (rs.length > 1) D.text(g, 'ASPP: concatenate the branches,', tx, 144 + rs.length * 22, { s: 12, b: true, c: z.col.ink }), D.text(g, 'then mix them with a 1 × 1 conv', tx, 162 + rs.length * 22, { s: 12, b: true, c: z.col.ink });
      return `<span class="big">k<sub>eff</sub> = k + (k − 1)(r − 1) = 2r + 1 for k = 3, &nbsp; padding r keeps the size</span><br>Dilation enlarges the view without pooling, so the map keeps its resolution and no parameters are added. ${rs.length > 1 ? 'Parallel rates give several zoom levels at once, which handles a tiny pedestrian and a large building in the same image.' : 'Stacking one large rate repeatedly leaves holes (gridding), which is why DeepLab runs several rates in parallel.'}`;
    }
  });

  def('unet', {
    title: 'U-Net: sizes, skips and parameters',
    sub: 'The contracting path halves the size and doubles the channels. The expanding path does the reverse, and each level receives a copy of the encoder map of the same size.',
    W: 560, H: 300,
    params: [
      { k: 'in', label: 'Input size', type: 'select', num: true, v: 572, opts: [[572, '572 (original paper)'], [256, '256 (lecture slide)'], [512, '512'], [128, '128']] },
      { k: 'pad', label: '3 × 3 convolutions', type: 'select', v: 'valid', opts: [['valid', 'Valid, no padding (2015 paper)'], ['same', 'Same padding (modern code)']] },
      { k: 'b', label: 'Base channels', type: 'select', num: true, v: 64, opts: [[16, '16'], [32, '32'], [64, '64']] },
      { k: 'd', label: 'Number of poolings', type: 'range', min: 2, max: 5, step: 1, v: 4 },
      { k: 'fuse', label: 'Skip fusion', type: 'select', v: 'cat', opts: [['cat', 'Concatenate (U-Net)'], ['add', 'Add (FPN style)']] }
    ],
    tips: [
      { t: 'The original U-Net: 572 in, 388 out, because every unpadded 3 × 3 conv trims 2 pixels and skips must be cropped. About 31.0 million parameters.', set: { in: 572, pad: 'valid', b: 64, d: 4, fuse: 'cat' } },
      { t: 'The lecture slide: 256 with same padding goes 256, 128, 64, 32, 16 and back. Output equals input.', set: { in: 256, pad: 'same', b: 64, d: 4, fuse: 'cat' } },
      { t: 'Halve the base channels to 32. Parameters fall about 4 times, because each conv cost grows with input channels times output channels.', set: { b: 32 } },
      { t: 'Switch the fusion to add. The first decoder conv at each level takes half the channels, so the decoder gets cheaper.', set: { fuse: 'add' } }
    ],
    draw(z) {
      const { g, p } = z;
      const cp = (i, o, k = 3) => k * k * i * o + o, t = p.pad === 'valid' ? 4 : 0;
      let s = p.in, ok = true; const enc = [], skips = [];
      let ch = p.b, cin = 1, params = 0;
      for (let l = 0; l < p.d; l++) { s -= t; skips.push(s); enc.push([s, ch]); params += cp(cin, ch) + cp(ch, ch); if (s % 2) ok = false; s = Math.floor(s / 2); cin = ch; ch *= 2; }
      s -= t; const bott = [s, ch]; params += cp(cin, ch) + cp(ch, ch);
      const dec = [];
      for (let l = p.d - 1; l >= 0; l--) { const o = ch / 2; params += 4 * ch * o + o; s *= 2; const crop = s; params += cp(p.fuse === 'cat' ? 2 * o : o, o) + cp(o, o); s -= t; dec.unshift([s, o, crop]); ch = o; }
      params += p.b * 2 + 2;
      if (s <= 0 || bott[0] <= 0) ok = false;
      const rows = p.d + 1, dy = Math.min(46, 230 / rows), bw = 120, bh = 24;
      const Y = l => 22 + l * dy;
      enc.forEach(([sz, c], l) => {
        D.rect(g, 20 + l * 12, Y(l), bw, bh, { fill: 'rgba(18,110,130,0.18)', stroke: z.col.cv });
        D.text(g, `${sz}² × ${c}`, 20 + l * 12 + bw / 2, Y(l) + 16, { a: 'center', s: 11, mono: true, b: true, c: z.col.ink });
        const [dsz, dc, crop] = dec[l];
        D.rect(g, 420 - l * 12, Y(l), bw, bh, { fill: 'rgba(240,140,40,0.18)', stroke: z.col.orange });
        D.text(g, `${dsz}² × ${dc}`, 420 - l * 12 + bw / 2, Y(l) + 16, { a: 'center', s: 11, mono: true, b: true, c: z.col.ink });
        D.arrow(g, 20 + l * 12 + bw + 4, Y(l) + bh / 2, 420 - l * 12 - 4, Y(l) + bh / 2, z.col.red, 1.5, 6);
        const lab = p.pad === 'valid' && crop !== skips[l] ? `copy, crop ${skips[l]} → ${crop}` : 'copy';
        D.text(g, lab, 280, Y(l) + bh / 2 - 4, { a: 'center', s: 10.5, c: z.col.red, b: true });
      });
      const bl = p.d;
      D.rect(g, 220, Y(bl), bw, bh, { fill: 'rgba(130,90,220,0.2)', stroke: z.col.purple });
      D.text(g, `${bott[0]}² × ${bott[1]}`, 280, Y(bl) + 16, { a: 'center', s: 11, mono: true, b: true, c: z.col.ink });
      D.text(g, 'bottleneck', 280, Y(bl) - 4, { a: 'center', s: 10.5, c: z.col.ink2, b: true });
      D.text(g, `in ${p.in}² × 1`, 20, 14, { s: 11, b: true, c: z.col.ink2 });
      D.text(g, `out ${dec[0][0]}² × 2 classes`, 540, 14, { a: 'right', s: 11, b: true, c: z.col.ink2 });
      return ok ? `<span class="big">parameters ≈ ${params.toLocaleString('en-US')} (${(params / 1e6).toFixed(1)} M), &nbsp; output ${dec[0][0]} × ${dec[0][0]}</span><br>A 3 × 3 conv from C<sub>in</sub> to C<sub>out</sub> has 9 C<sub>in</sub> C<sub>out</sub> + C<sub>out</sub> parameters. The deepest block holds the largest share. Deep features say this is probably a car, the skip says exactly where its edge is.` : '<b>This size does not work: a map becomes odd before pooling or shrinks to nothing.</b> The original paper chose 572 so that every pooling step gets an even size.';
    }
  });

  /* ---------------------------------------------------------------- Chapter 14: training and evaluating segmentation */
  def('pixloss', {
    title: 'Pixel losses: plain, weighted, focal, and the ignore label',
    sub: 'Each line is one pixel: its true class and the probability the model gives to that class. Pixels marked ignore are skipped. Compare how much each pixel adds to the loss.',
    W: 560, H: 290,
    params: [
      { k: 'px', label: 'Pixels: true class, p of the true class', type: 'area', v: 'road 0.99\nroad 0.90\ncar 0.50\ncar 0.45\nperson 0.10\nignore 0.20' },
      { k: 'mode', label: 'Loss', type: 'select', v: 'ce', opts: [['ce', 'Cross-entropy'], ['wce', 'Weighted cross-entropy'], ['fl', 'Focal loss']] },
      { k: 'w', label: 'Class weights (for weighted CE)', type: 'text', v: 'road 0.5 car 2 person 5', show: p => p.mode === 'wce' },
      { k: 'gam', label: 'Focusing parameter γ', type: 'range', min: 0, max: 5, step: 0.5, v: 2, show: p => p.mode === 'fl' }
    ],
    tips: [
      { t: 'Plain cross-entropy. The confident road pixel adds only 0.010, the badly predicted person adds 2.303 and dominates.', set: { mode: 'ce' } },
      { t: 'Weighted CE with the slide weights. The person pixel is multiplied by 5. The mean is divided by the total weight of the valid pixels.', set: { mode: 'wce', w: 'road 0.5 car 2 person 5' } },
      { t: 'Focal loss with γ = 2. Easy pixels near 1 almost vanish, so the boundary pixels and the person carry nearly all of the loss.', set: { mode: 'fl', gam: 2 } },
      { t: 'Look at the bottom line. Dividing by all pixels, including the ignored one, gives a lower and wrong mean.', set: { mode: 'ce' } }
    ],
    draw(z) {
      const { g, p } = z;
      let px = String(p.px).split('\n').map(l => l.trim().split(/\s+/)).filter(a => a.length >= 2 && isFinite(+a[1])).map(a => ({ c: a[0].toLowerCase(), p: clamp(+a[1], 1e-4, 1) })).slice(0, 8);
      if (!px.length) px = [{ c: 'road', p: 0.9 }];
      const wt = {}; String(p.w).trim().split(/\s+/).forEach((t, i, a) => { if (i % 2 === 0 && isFinite(+a[i + 1])) wt[t.toLowerCase()] = +a[i + 1]; });
      const L = px.map(q => {
        if (q.c === 'ignore') return { ...q, l: 0, wgt: 0, ign: true };
        const ce = -Math.log(q.p);
        if (p.mode === 'wce') { const w = wt[q.c] ?? 1; return { ...q, l: w * ce, wgt: w }; }
        if (p.mode === 'fl') return { ...q, l: Math.pow(1 - q.p, p.gam) * ce, wgt: 1 };
        return { ...q, l: ce, wgt: 1 };
      });
      const mx = Math.max(0.5, ...L.map(q => q.l)), valid = L.filter(q => !q.ign);
      const tot = valid.reduce((s, q) => s + q.l, 0), wsum = valid.reduce((s, q) => s + q.wgt, 0);
      D.text(g, 'pixel    class    p(true)   loss', 14, 22, { s: 12, mono: true, b: true, c: z.col.ink });
      L.forEach((q, i) => {
        const y = 46 + i * 28;
        D.text(g, `${String(i + 1).padStart(3)}      ${q.c.slice(0, 7).padEnd(7)}  ${q.p.toFixed(2)}`, 14, y, { s: 12, mono: true, c: q.ign ? z.col.ink2 : z.col.ink });
        if (q.ign) D.text(g, 'skipped', 290, y, { s: 12, b: true, c: z.col.ink2 });
        else { D.rect(g, 290, y - 12, 190 * q.l / mx, 14, { fill: q.l / tot > 0.4 ? z.col.red : z.col.cv }); D.text(g, q.l < 0.001 ? q.l.toExponential(1) : q.l.toFixed(3), 486, y, { s: 11.5, mono: true, c: z.col.ink }); }
      });
      const y0 = 56 + L.length * 28;
      const mean = tot / (p.mode === 'wce' ? wsum : valid.length), wrong = tot / L.length;
      D.text(g, `mean over ${valid.length} valid pixels = ${mean.toFixed(3)}`, 14, y0, { s: 12.5, b: true, c: z.col.green });
      if (valid.length < L.length) D.text(g, `wrong: divide by all ${L.length} pixels = ${wrong.toFixed(3)}`, 14, y0 + 20, { s: 12, c: z.col.red });
      const f1 = p.mode === 'wce' ? 'L = Σ w<sub>y</sub> · (−ln p<sub>y</sub>) ÷ Σ w<sub>y</sub>' : p.mode === 'fl' ? 'FL = −(1 − p<sub>t</sub>)<sup>γ</sup> ln p<sub>t</sub>' : 'L = −(1 ÷ |Ω|) Σ<sub>i ∈ Ω</sub> ln p<sub>i, y<sub>i</sub></sub>';
      return `<span class="big">${f1}</span><br>Ω is the set of valid (not ignored) pixels. ${p.mode === 'fl' ? 'Focal loss scales by difficulty, weighted CE scales by class.' : p.mode === 'wce' ? 'Very large weights can make training unstable or add false positives.' : 'The loss is small when the model is confident and right, and grows sharply as p of the true class falls.'}`;
    }
  });

  def('overlap', {
    title: 'Dice and IoU for one predicted mask',
    sub: 'G is the true region and P the predicted one. Set their sizes and their overlap. Both scores measure the same overlap, on different scales.',
    W: 560, H: 270,
    params: [
      { k: 'G', label: 'True pixels |G|', type: 'range', min: 10, max: 300, step: 5, v: 100 },
      { k: 'P', label: 'Predicted pixels |P|', type: 'range', min: 0, max: 300, step: 5, v: 120 },
      { k: 'I', label: 'Overlap |P ∩ G|', type: 'range', min: 0, max: 300, step: 5, v: 80 }
    ],
    tips: [
      { t: 'The lecture tumour: |G| = 100, |P| = 120, overlap 80. Dice 0.727, IoU 0.571. Same prediction, two numbers.', set: { G: 100, P: 120, I: 80 } },
      { t: 'Predict nothing at all. Both scores are 0, even though most pixels of the image would still be correct.', set: { P: 0, I: 0 } },
      { t: 'Predict a huge region that covers the tumour: |P| = 300, overlap 100. Recall is perfect, but IoU falls to 0.333.', set: { G: 100, P: 300, I: 100 } },
      { t: 'Practice problem: |P| = 200, |G| = 250, overlap 150. Dice 0.667 and IoU exactly 0.5.', set: { G: 250, P: 200, I: 150 } }
    ],
    draw(z) {
      const { g, p } = z;
      const I = Math.min(p.I, p.G, p.P), TP = I, FP = p.P - I, FN = p.G - I;
      const dice = p.P + p.G ? 2 * I / (p.P + p.G) : 1, iou = TP + FP + FN ? TP / (TP + FP + FN) : 1;
      const R = v => Math.sqrt(v / Math.PI) * 6.5;
      const rg = R(p.G), rp = R(Math.max(p.P, 0.01));
      const dist = (r1, r2, a) => { if (a <= 0) return r1 + r2 + 4; let lo = Math.abs(r1 - r2), hi = r1 + r2; const ar = d => { if (d >= r1 + r2) return 0; if (d <= Math.abs(r1 - r2)) return Math.PI * Math.min(r1, r2) ** 2; const a1 = r1 * r1 * Math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1)), a2 = r2 * r2 * Math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2)); return a1 + a2 - 0.5 * Math.sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2)); }; const target = a * 42.25; for (let k = 0; k < 40; k++) { const m = (lo + hi) / 2; if (ar(m) > target) lo = m; else hi = m; } return (lo + hi) / 2; };
      const d = dist(rg, rp, I), cx = 150, cy = 125;
      g.save(); g.globalAlpha = 0.35;
      D.circle(g, cx - d / 2, cy, rg, { fill: z.col.green });
      if (p.P > 0) D.circle(g, cx + d / 2, cy, rp, { fill: z.col.cv });
      g.restore();
      D.circle(g, cx - d / 2, cy, rg, { stroke: z.col.green, w: 2 });
      if (p.P > 0) D.circle(g, cx + d / 2, cy, rp, { stroke: z.col.cv, w: 2 });
      D.text(g, 'G (truth)', cx - d / 2, cy + rg + 18, { a: 'center', s: 12, b: true, c: z.col.green });
      if (p.P > 0) D.text(g, 'P (prediction)', cx + d / 2, cy - rp - 8, { a: 'center', s: 12, b: true, c: z.col.cv });
      D.text(g, `TP = ${TP}, FP = ${FP}, FN = ${FN}`, 14, 258, { s: 12, mono: true, c: z.col.ink });
      const m = D.axes(g, z, [370, 20, 160, 160], [0, 1], [0, 1], { xl: 'IoU', yl: 'Dice', nx: 2, ny: 2 });
      D.curve(g, j => 2 * j / (1 + j), [0, 1], m, z.col.purple, 2);
      D.line(g, m.sx(0), m.sy(0), m.sx(1), m.sy(1), z.col.line, 1, [4, 4]);
      D.circle(g, m.sx(iou), m.sy(dice), 6, { fill: z.col.orange });
      D.text(g, `Dice ${dice.toFixed(3)}`, 370, 236, { s: 13, b: true, c: z.col.ink });
      D.text(g, `IoU  ${iou.toFixed(3)}`, 370, 256, { s: 13, b: true, c: z.col.ink });
      return `<span class="big">Dice = 2|P ∩ G| ÷ (|P| + |G|) = 2TP ÷ (2TP + FP + FN), &nbsp; IoU = TP ÷ (TP + FP + FN), &nbsp; Dice = 2·IoU ÷ (1 + IoU)</span><br>Dice is never below IoU, and they agree only at 0 and 1. Never compare a Dice from one paper with an IoU from another.${p.I > Math.min(p.G, p.P) ? ' The overlap cannot exceed the smaller region, so it was capped.' : ''}`;
    }
  });

  def('confmat', {
    title: 'From a confusion matrix to mIoU',
    sub: 'Rows are the true class, columns the predicted class, values are pixel counts. Every class gets its own IoU from its row, its column and the diagonal.',
    W: 560, H: 280,
    params: [
      { k: 'm', label: 'Matrix rows (truth), comma or space separated', type: 'area', v: '900 20 5\n30 140 10\n15 5 30' },
      { k: 'names', label: 'Class names', type: 'text', v: 'road car person' }
    ],
    tips: [
      { t: 'The lecture matrix. Pixel accuracy is 0.926 but mIoU is only 0.691, because person scores 0.462.', set: { m: '900 20 5\n30 140 10\n15 5 30', names: 'road car person' } },
      { t: 'Practice problem 15: classes A, B, C. IoU 0.667, 0.667 and 0.600, mIoU 0.644, accuracy 0.792.', set: { m: '50 5 5\n10 30 0\n5 0 15', names: 'A B C' } },
      { t: 'The accuracy trap: 9,000 background and 1,000 tumour pixels, all predicted background. Accuracy 0.900, mIoU 0.450.', set: { m: '9000 0\n1000 0', names: 'background tumour' } }
    ],
    draw(z) {
      const { g, p } = z;
      let M = parseGrid(p.m, [[900, 20, 5], [30, 140, 10], [15, 5, 30]]);
      if (M.length !== M[0].length || M.length > 5) M = [[900, 20, 5], [30, 140, 10], [15, 5, 30]];
      const n = M.length, names = String(p.names).trim().split(/\s+/);
      while (names.length < n) names.push('class ' + (names.length + 1));
      const row = M.map(r => r.reduce((a, b) => a + b, 0)), col = M[0].map((_, j) => M.reduce((a, r) => a + r[j], 0)), N = row.reduce((a, b) => a + b, 0);
      const st = M.map((r, i) => { const tp = r[i], fn = row[i] - tp, fp = col[i] - tp, u = tp + fp + fn; return { tp, fn, fp, iou: u ? tp / u : NaN, dice: 2 * tp + fp + fn ? 2 * tp / (2 * tp + fp + fn) : NaN, rec: row[i] ? tp / row[i] : NaN }; });
      const okI = st.filter(s => isFinite(s.iou)), miou = okI.reduce((a, s) => a + s.iou, 0) / okI.length;
      const pa = M.reduce((a, r, i) => a + r[i], 0) / N, mca = st.filter(s => isFinite(s.rec)).reduce((a, s) => a + s.rec, 0) / st.filter(s => isFinite(s.rec)).length;
      const fw = st.reduce((a, s, i) => a + (isFinite(s.iou) ? row[i] / N * s.iou : 0), 0);
      const cell = Math.min(52, 190 / n), X = 70, Y = 40, mx = Math.max(...M.flat(), 1);
      D.text(g, 'predicted →', X, 18, { s: 11, b: true, c: z.col.ink2 });
      names.slice(0, n).forEach((nm, i) => { D.text(g, nm.slice(0, 7), X + (i + 0.5) * cell, 34, { a: 'center', s: 10.5, b: true, c: z.col.ink2 }); D.text(g, nm.slice(0, 8), X - 6, Y + (i + 0.5) * cell + 4, { a: 'right', s: 10.5, b: true, c: z.col.ink2 }); });
      M.forEach((r, i) => r.forEach((v, j) => {
        D.rect(g, X + j * cell, Y + i * cell, cell, cell, { fill: i === j ? `rgba(40,160,100,${0.15 + 0.6 * v / mx})` : `rgba(220,70,70,${0.08 + 0.6 * v / mx})`, stroke: z.col.line, w: 1 });
        D.text(g, String(v), X + (j + 0.5) * cell, Y + (i + 0.5) * cell + 4, { a: 'center', s: cell < 40 ? 10 : 12, mono: true, b: i === j, c: z.col.ink });
      }));
      const tx = 300;
      D.text(g, 'class      TP    FP    FN   IoU', tx, 24, { s: 11.5, mono: true, b: true, c: z.col.ink });
      st.forEach((s, i) => D.text(g, `${names[i].slice(0, 8).padEnd(9)} ${String(s.tp).padStart(4)}  ${String(s.fp).padStart(4)}  ${String(s.fn).padStart(4)}  ${isFinite(s.iou) ? s.iou.toFixed(3) : ' n/a'}`, tx, 46 + i * 20, { s: 11.5, mono: true, c: s.iou < 0.5 ? z.col.red : z.col.ink }));
      const y2 = 66 + n * 20;
      [['mIoU', miou], ['pixel accuracy', pa], ['mean class accuracy', mca], ['frequency weighted IoU', fw]].forEach(([k, v], i) => D.text(g, `${k.padEnd(23)}${v.toFixed(3)}`, tx, y2 + i * 20, { s: 11.5, mono: true, b: i === 0, c: i === 0 ? z.col.cv : z.col.ink }));
      return `<span class="big">IoU<sub>c</sub> = TP ÷ (TP + FP + FN), &nbsp; FP = column sum − TP, &nbsp; FN = row sum − TP, &nbsp; mIoU = mean over classes</span><br>Pixel accuracy and frequency weighted IoU follow the big classes. mIoU gives every class one equal vote, so a weak rare class shows up. Benchmarks add up one matrix over the whole dataset before computing IoU.`;
    }
  });

  def('leak', {
    title: 'Data leakage through normalisation',
    sub: 'Min-max scaling maps the training range to 0 to 1. Fit it on the training data only, or the scaler quietly learns the range of the test data.',
    W: 560, H: 230,
    params: [
      { k: 'tr', label: 'Training values', type: 'text', v: '10 20 30' },
      { k: 'te', label: 'A test value', type: 'range', min: 0, max: 120, step: 1, v: 100 },
      { k: 'fit', label: 'Fit min and max on', type: 'select', v: 'train', opts: [['train', 'Training data only (right)'], ['all', 'All data, train and test (leak)']] }
    ],
    tips: [
      { t: 'Fit on training only. The test value maps to 4.5, far outside 0 to 1. The shift is visible, which is the honest result.', set: { tr: '10 20 30', te: 100, fit: 'train' } },
      { t: 'Fit on all data. Everything squeezes into 0 to 1, the test point lands at exactly 1, and the shift is hidden. Validation scores will look better than reality.', set: { fit: 'all' } },
      { t: 'Bring the test value to 25, inside the training range. Both fits now agree closely. Leakage hurts most when the test data really is different.', set: { te: 25, fit: 'all' } }
    ],
    draw(z) {
      const { g, p } = z;
      let tr = String(p.tr).trim().split(/[\s,]+/).map(Number).filter(isFinite); if (tr.length < 2) tr = [10, 20, 30];
      const all = p.fit === 'all' ? tr.concat([p.te]) : tr, lo = Math.min(...all), hi = Math.max(...all), sc = v => hi > lo ? (v - lo) / (hi - lo) : 0;
      const raw = D.axes(g, z, [40, 44, 480, 0.001], [0, Math.max(120, ...tr)], [0, 1], { nx: 6, ny: 1, fy: () => '' });
      D.text(g, 'raw values', 40, 22, { s: 12, b: true, c: z.col.ink });
      tr.forEach(v => D.circle(g, raw.sx(v), 44, 6, { fill: z.col.cv }));
      D.circle(g, raw.sx(p.te), 44, 7, { fill: z.col.orange });
      const mxs = Math.max(1, sc(p.te)) * 1.05;
      const s = D.axes(g, z, [40, 150, 480, 0.001], [Math.min(0, sc(p.te)) - 0.05, mxs], [0, 1], { nx: 5, ny: 1, fy: () => '', fx: v => v.toFixed(1) });
      D.text(g, `scaled with min ${lo}, max ${hi}`, 40, 112, { s: 12, b: true, c: z.col.ink });
      g.save(); g.fillStyle = z.col.green; g.globalAlpha = 0.12; g.fillRect(s.sx(0), 136, s.sx(1) - s.sx(0), 28); g.restore();
      tr.forEach(v => D.circle(g, s.sx(sc(v)), 150, 6, { fill: z.col.cv }));
      D.circle(g, s.sx(sc(p.te)), 150, 7, { fill: z.col.orange });
      D.text(g, `test → ${sc(p.te).toFixed(3)}`, s.sx(sc(p.te)), 134, { a: 'center', s: 12, b: true, c: z.col.orange });
      D.text(g, 'blue: training values, orange: the test value, green band: 0 to 1', 40, 205, { s: 12, c: z.col.ink2 });
      return `<b>${p.fit === 'all' ? 'Leak: the scaler has seen the test value, so nothing looks unusual.' : sc(p.te) > 1 || sc(p.te) < 0 ? 'Honest: the test value falls outside the training range, so you know the model faces new data.' : 'The test value lies inside the training range.'}</b> Split first, then fit every statistic on the training split. In segmentation, also split by patient, scene or video, never by random image, or near copies leak across.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 15: vision and language */
  const unitArrow = (g, z, cx, cy, R, deg, col, dash, lab) => {
    const a = deg * Math.PI / 180, x = cx + R * Math.cos(a), y = cy - R * Math.sin(a);
    if (dash) D.line(g, cx, cy, x, y, col, 2, [5, 4]); else D.arrow(g, cx, cy, x, y, col, 2.2, 8);
    if (lab) D.text(g, lab, cx + (R + 14) * Math.cos(a), cy - (R + 14) * Math.sin(a) + 4, { a: 'center', s: 11, b: true, c: col });
  };
  const parseAngles = (s, n, fb) => { const v = String(s).trim().split(/[\s,]+/).map(Number).filter(isFinite); return v.length >= n ? v.slice(0, n) : fb; };

  def('cliptrain', {
    title: 'CLIP training: pull matching pairs together',
    sub: 'Real CLIP embeddings have hundreds of dimensions. Here each one is a direction in 2D so it can be drawn. Solid arrows are images, dashed are captions. Similarity is the cosine of the angle between them.',
    W: 560, H: 290,
    params: [
      { k: 'im', label: 'Image directions in degrees (dog, cat, car)', type: 'text', v: '20 95 210' },
      { k: 'tx', label: 'Caption directions in degrees (same order)', type: 'text', v: '35 80 195' },
      { k: 'tau', label: 'Temperature τ', type: 'select', num: true, v: 0.1, opts: [[0.01, '0.01 (CLIP learns about this)'], [0.1, '0.1'], [0.5, '0.5'], [1, '1']] }
    ],
    tips: [
      { t: 'A well trained batch. Each image is closest to its own caption, so the diagonal wins every row and the loss is low.', set: { im: '20 95 210', tx: '35 80 195', tau: 0.1 } },
      { t: 'Swap the dog and cat captions (80 35 195). The diagonal now loses two rows and the loss jumps. Training would push them back.', set: { tx: '80 35 195' } },
      { t: 'Put the dog and cat close together (20 40 and 25 45). Hard negatives: the rows are no longer confident. This is what forces fine distinctions.', set: { im: '20 40 210', tx: '25 45 195', tau: 0.1 } },
      { t: 'Raise τ to 1. All probabilities flatten towards one third and the model cannot be confident. A small temperature sharpens the SoftMax.', set: { im: '20 95 210', tx: '35 80 195', tau: 1 } }
    ],
    draw(z) {
      const { g, p } = z;
      const im = parseAngles(p.im, 3, [20, 95, 210]), tx = parseAngles(p.tx, 3, [35, 80, 195]), names = ['dog', 'cat', 'car'];
      const cols = [z.col.cv, z.col.orange, z.col.purple], cx = 110, cy = 140, R = 90;
      D.circle(g, cx, cy, R, { stroke: z.col.line, w: 1 });
      im.forEach((a, i) => unitArrow(g, z, cx, cy, R, a, cols[i], false, 'I' + (i + 1)));
      tx.forEach((a, i) => unitArrow(g, z, cx, cy, R * 0.8, a, cols[i], true, ''));
      D.text(g, 'solid: images, dashed: captions', 14, 270, { s: 11, c: z.col.ink2 });
      const S = im.map(a => tx.map(b => Math.cos((a - b) * Math.PI / 180)));
      const sm = row => { const m = Math.max(...row), e = row.map(v => Math.exp((v - m) / p.tau)), s = e.reduce((x, y) => x + y, 0); return e.map(v => v / s); };
      const P = S.map(sm), Pc = [0, 1, 2].map(j => sm(S.map(r => r[j])));
      const li = -P.reduce((s, r, i) => s + Math.log(r[i]), 0) / 3, lt = -Pc.reduce((s, c, j) => s + Math.log(c[j]), 0) / 3;
      const X = 270, Y = 50, c = 72;
      D.text(g, 'cosine similarity (row SoftMax below)', X, 22, { s: 11.5, b: true, c: z.col.ink });
      names.forEach((n, j) => D.text(g, '"' + n + '"', X + (j + 0.5) * c, Y - 8, { a: 'center', s: 11, b: true, c: cols[j] }));
      S.forEach((r, i) => {
        D.text(g, 'I' + (i + 1), X - 8, Y + (i + 0.5) * c / 1.1, { a: 'right', s: 11, b: true, c: cols[i] });
        r.forEach((v, j) => {
          const y = Y + i * c / 1.1;
          D.rect(g, X + j * c, y, c, c / 1.1, { fill: i === j ? `rgba(40,160,100,${0.1 + 0.5 * P[i][j]})` : `rgba(220,70,70,${0.05 + 0.5 * P[i][j]})`, stroke: z.col.line, w: 1 });
          D.text(g, v.toFixed(2), X + (j + 0.5) * c, y + 26, { a: 'center', s: 12, mono: true, b: true, c: z.col.ink });
          D.text(g, P[i][j].toFixed(2), X + (j + 0.5) * c, y + 46, { a: 'center', s: 10.5, mono: true, c: z.col.ink2 });
        });
      });
      D.text(g, `image to text ${li.toFixed(3)}, text to image ${lt.toFixed(3)}`, X - 20, 262, { s: 11, c: z.col.ink2 }); D.text(g, `loss = ½(sum) = ${((li + lt) / 2).toFixed(3)}`, X - 20, 278, { s: 12, b: true, c: z.col.ink });
      return `<span class="big">s<sub>ij</sub> = cos(I<sub>i</sub>, T<sub>j</sub>) = I<sub>i</sub> · T<sub>j</sub> ÷ (‖I<sub>i</sub>‖ ‖T<sub>j</sub>‖), &nbsp; L = −½ [ (1/N) Σ<sub>i</sub> ln softmax<sub>j</sub>(s<sub>ij</sub> ÷ τ)<sub>i</sub> + (1/N) Σ<sub>j</sub> ln softmax<sub>i</sub>(s<sub>ij</sub> ÷ τ)<sub>j</sub> ]</span><br>The correct pairs are the diagonal. Every other cell in the batch is a negative. Training pulls the diagonal up and pushes the rest down, in both directions.`;
    }
  });

  def('zeroshot', {
    title: 'Zero-shot classification with text prompts',
    sub: 'Write one prompt per class. The image is given the class whose prompt embedding is most similar. New classes need only new prompts, no retraining. Directions stand in for the real embeddings.',
    W: 560, H: 260,
    params: [
      { k: 'img', label: 'Image embedding direction (degrees)', type: 'range', min: 0, max: 359, step: 1, v: 40 },
      { k: 'pr', label: 'Prompts: text then direction', type: 'area', v: 'a photo of a dog | 30\na photo of a cat | 70\na photo of a horse | 150\na photo of a car | 250' },
      { k: 'scale', label: 'Logit scale (1 ÷ τ)', type: 'select', num: true, v: 100, opts: [[1, '1'], [10, '10'], [100, '100 (CLIP)']] }
    ],
    tips: [
      { t: 'The image points at 40°, closest to the dog prompt. With CLIP\'s scale of 100, dog wins with high confidence.', set: { img: 40, scale: 100 } },
      { t: 'Turn the image to 50°, halfway between dog and cat. Small changes in wording or embedding now decide the answer. That is why prompt design matters.', set: { img: 50 } },
      { t: 'Add a class with no training at all: append the line "a photo of a zebra | 120". It immediately becomes a choice.', set: { pr: 'a photo of a dog | 30\na photo of a cat | 70\na photo of a horse | 150\na photo of a car | 250\na photo of a zebra | 120', img: 115 } },
      { t: 'Set the scale to 1. Cosines lie between −1 and 1, so without scaling the SoftMax is nearly flat.', set: { scale: 1, img: 40 } }
    ],
    draw(z) {
      const { g, p } = z;
      let pr = String(p.pr).split('\n').map(l => l.split('|')).filter(a => a.length === 2 && isFinite(+a[1])).map(a => ({ t: a[0].trim().slice(0, 28), a: +a[1] })).slice(0, 6);
      if (!pr.length) pr = [{ t: 'a photo of a dog', a: 30 }];
      const cols = [z.col.cv, z.col.orange, z.col.purple, z.col.green, z.col.red, z.col.pink];
      const cx = 100, cy = 130, R = 85;
      D.circle(g, cx, cy, R, { stroke: z.col.line, w: 1 });
      pr.forEach((q, i) => unitArrow(g, z, cx, cy, R * 0.85, q.a, cols[i % 6], true, ''));
      unitArrow(g, z, cx, cy, R, p.img, z.col.ink, false, 'image');
      const s = pr.map(q => Math.cos((p.img - q.a) * Math.PI / 180)), m = Math.max(...s), e = s.map(v => Math.exp((v - m) * p.scale)), S = e.reduce((a, b) => a + b, 0), P = e.map(v => v / S);
      const best = P.indexOf(Math.max(...P));
      D.text(g, 'prompt                       cos    p', 230, 24, { s: 11.5, mono: true, b: true, c: z.col.ink });
      pr.forEach((q, i) => {
        const y = 50 + i * 32;
        D.text(g, q.t.padEnd(28), 230, y, { s: 11, mono: true, b: i === best, c: cols[i % 6] });
        D.text(g, `${s[i].toFixed(2).padStart(5)}  ${P[i].toFixed(2)}`, 430, y, { s: 11, mono: true, b: i === best, c: z.col.ink });
        D.rect(g, 230, y + 6, 300 * P[i], 6, { fill: cols[i % 6] });
      });
      return `<b>Prediction: ${pr[best].t}</b> (p = ${P[best].toFixed(2)}).<br>p<sub>k</sub> = softmax(scale × cos(image, prompt<sub>k</sub>)). The class list is just text, so it can change at test time. Accuracy depends on how the prompts are worded, and averaging several wordings per class (prompt ensembling) usually helps.`;
    }
  });

  def('vitcost', {
    title: 'Vision transformer tokens and attention cost',
    sub: 'The image is cut into patches, each patch becomes one token, and global self-attention compares every token with every other one. Windowed attention only compares tokens inside each window.',
    W: 560, H: 280,
    params: [
      { k: 'n', label: 'Image size (square)', type: 'range', min: 64, max: 1024, step: 32, v: 224 },
      { k: 'ps', label: 'Patch size', type: 'select', num: true, v: 16, opts: [[4, '4 (Swin first stage)'], [8, '8'], [14, '14'], [16, '16 (ViT-B/16)'], [32, '32']] },
      { k: 'w', label: 'Attention window (tokens per side)', type: 'select', num: true, v: 0, opts: [[0, 'Global (whole image)'], [7, '7 × 7 (Swin)'], [12, '12 × 12']] }
    ],
    tips: [
      { t: 'The ViT case: 224 with 16 × 16 patches gives 14 × 14 = 196 tokens and 38,416 attention pairs per head.', set: { n: 224, ps: 16, w: 0 } },
      { t: 'A segmentation sized 512 image: 1,024 tokens and 1,048,576 pairs, 27.3 times more for 5.2 times more pixels.', set: { n: 512, ps: 16, w: 0 } },
      { t: 'Patch 4 on 224 gives 56 × 56 = 3,136 tokens. Global attention needs 9.8 million pairs.', set: { n: 224, ps: 4, w: 0 } },
      { t: 'Now use 7 × 7 windows: 64 windows of 49 tokens, 153,664 pairs, 64 times fewer. Swin shifts the windows between layers so information still spreads.', set: { n: 224, ps: 4, w: 7 } }
    ],
    draw(z) {
      const { g, p } = z;
      const t = Math.ceil(p.n / p.ps), N = t * t, glob = N * N;
      const w = p.w && p.w < t ? p.w : 0, nw = w ? Math.ceil(t / w) ** 2 : 1, win = w ? nw * (w * w) ** 2 : glob;
      const S = 220, cell = S / t, X = 14, Y = 30;
      D.rect(g, X, Y, S, S, { fill: z.col.bg, stroke: z.col.line });
      if (t <= 64) for (let k = 1; k < t; k++) { D.line(g, X + k * cell, Y, X + k * cell, Y + S, z.col.line, 0.5); D.line(g, X, Y + k * cell, X + S, Y + k * cell, z.col.line, 0.5); }
      if (w) { for (let k = 0; k <= t; k += w) { D.line(g, X + Math.min(k, t) * cell, Y, X + Math.min(k, t) * cell, Y + S, z.col.orange, 1.5); D.line(g, X, Y + Math.min(k, t) * cell, X + S, Y + Math.min(k, t) * cell, z.col.orange, 1.5); } D.rect(g, X, Y, Math.min(w, t) * cell, Math.min(w, t) * cell, { fill: 'rgba(240,140,40,0.25)' }); }
      else D.rect(g, X, Y, S, S, { fill: 'rgba(18,110,130,0.08)' });
      D.rect(g, X, Y, cell, cell, { fill: z.col.red });
      D.text(g, `${p.n} × ${p.n} image, ${t} × ${t} tokens`, X, 20, { s: 12, b: true, c: z.col.ink });
      const tx = 260, L = [
        ['tokens', N.toLocaleString('en-US')],
        ['numbers per patch', (p.ps * p.ps * 3).toLocaleString('en-US')],
        ['global pairs per head', glob.toLocaleString('en-US')],
        [w ? `${nw} windows × ${w * w}²` : 'windowed pairs', w ? win.toLocaleString('en-US') : 'off'],
        ['saving', w ? `${(glob / win).toFixed(1)}×` : 'none']];
      L.forEach(([a, b], i) => { D.text(g, a, tx, 50 + i * 30, { s: 12.5, c: z.col.ink2 }); D.text(g, b, 540, 50 + i * 30, { a: 'right', s: 13, mono: true, b: true, c: z.col.ink }); });
      D.text(g, 'red: one token. Orange: the window it may attend to.', tx, 210, { s: 11, c: z.col.ink2 });
      return `<span class="big">tokens = (n ÷ p)², &nbsp; global attention pairs = tokens²</span><br>Attention cost grows with the square of the number of tokens, so doubling the image side multiplies it by 16. Segmentation transformers therefore use hierarchical stages, windows or spatially reduced keys and values. The trade is global context in one layer against cost.`;
    }
  });

  def('triangulate', {
    title: 'Depth from two cameras: triangulation',
    sub: 'Top view. Two cameras a baseline B apart both see point P. Its image shifts between the two views by the disparity d, and depth follows from the similar triangles of the two rays.',
    W: 560, H: 290,
    params: [
      { k: 'Z', label: 'True depth of P (m)', type: 'range', min: 0.5, max: 10, step: 0.1, v: 2 },
      { k: 'X', label: 'Sideways position of P (m)', type: 'range', min: -1, max: 1, step: 0.05, v: 0.2 },
      { k: 'B', label: 'Baseline B (m)', type: 'range', min: 0.05, max: 0.6, step: 0.01, v: 0.12 },
      { k: 'f', label: 'Focal length f (pixels)', type: 'range', min: 300, max: 1500, step: 10, v: 700 },
      { k: 'e', label: 'Matching error (pixels)', type: 'range', min: 0, max: 3, step: 0.25, v: 1 }
    ],
    tips: [
      { t: 'f = 700 px, B = 0.12 m, P at 2 m: disparity 42 px. A 1 pixel matching error moves the estimate by about 5 cm.', set: { Z: 2, X: 0.2, B: 0.12, f: 700, e: 1 } },
      { t: 'Move P to 8 m. The disparity shrinks to 10.5 px and the same 1 pixel error now costs about 0.8 m. Error grows with depth squared.', set: { Z: 8 } },
      { t: 'Widen the baseline to 0.5 m at 8 m. Disparity grows and the error drops by about 4 times. Wide baselines see far, but matching gets harder.', set: { Z: 8, B: 0.5 } },
      { t: 'Set the matching error to 0. Triangulation is exact when the match and the camera geometry are perfect. Real errors come from bad matches and poor calibration.', set: { e: 0, Z: 2, B: 0.12 } }
    ],
    draw(z) {
      const { g, p } = z;
      const d = p.f * p.B / p.Z, de = Math.max(0.01, d - p.e), Ze = p.f * p.B / de, err = Ze - p.Z;
      const zMax = Math.max(10, Ze) * 1.05, sc = 230 / zMax, X0 = 200, Y0 = 268, xs = 60;
      const toS = (x, zz) => [X0 + x * xs, Y0 - zz * sc];
      const c1 = toS(-p.B / 2, 0), c2 = toS(p.B / 2, 0), P = toS(p.X, p.Z);
      D.line(g, 20, Y0, 380, Y0, z.col.line, 1);
      for (let k = 2; k <= zMax; k += 2) { const yy = Y0 - k * sc; D.line(g, 20, yy, 380, yy, z.col.line, 0.5, [2, 4]); D.text(g, k + ' m', 24, yy - 3, { s: 10, c: z.col.ink2 }); }
      D.line(g, ...c1, ...P, z.col.cv, 1.8); D.line(g, ...c2, ...P, z.col.orange, 1.8);
      if (p.e > 0) { const Pe = toS(p.X * Ze / p.Z, Ze); D.line(g, ...c1, ...Pe, z.col.cv, 1, [4, 4]); D.circle(g, ...Pe, 5, { stroke: z.col.red, w: 2 }); D.text(g, 'estimate', Pe[0] - 9, Pe[1] + 4, { a: 'right', s: 11, b: true, c: z.col.red }); }
      D.circle(g, ...P, 6, { fill: z.col.green }); D.text(g, 'P', P[0] + 9, P[1] - 4, { s: 12, b: true, c: z.col.green });
      [c1, c2].forEach((c, i) => { D.rect(g, c[0] - 7, c[1] - 4, 14, 10, { fill: i ? z.col.orange : z.col.cv }); });
      D.text(g, `B = ${p.B.toFixed(2)} m`, X0, Y0 + 16, { a: 'center', s: 11, b: true, c: z.col.ink2 });
      const tx = 400, rows = [['disparity d', `${d.toFixed(1)} px`], ['true depth', `${p.Z.toFixed(2)} m`], ['with error', `${Ze.toFixed(2)} m`], ['depth error', `${err >= 0 ? '+' : ''}${err.toFixed(3)} m`], ['rule of thumb', `${(p.Z * p.Z / (p.f * p.B) * p.e).toFixed(3)} m`]];
      rows.forEach(([a, b], i) => { D.text(g, a, tx, 34 + i * 46, { s: 12, c: z.col.ink2 }); D.text(g, b, tx, 52 + i * 46, { s: 13, mono: true, b: true, c: i === 3 ? z.col.red : z.col.ink }); });
      return `<span class="big">Z = f B ÷ d, &nbsp; ΔZ ≈ (Z² ÷ (f B)) Δd</span><br>The two viewing rays meet at P. Depth is inversely proportional to disparity, so far points have tiny disparities and a one pixel matching mistake matters much more. With many photos and unknown cameras, the camera poses are estimated together with the points, which is how 3D models are built from internet photo collections.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 16: project lab */
  const cvSigma = k => 0.3 * ((k - 1) * 0.5 - 1) + 0.8;
  const gTaps = (k, s) => { const w = []; let t = 0; for (let i = 0; i < k; i++) { const d = i - (k - 1) / 2, v = Math.exp(-d * d / (2 * s * s)); w.push(v); t += v; } return w.map(v => v / t); };
  const cvTaps = k => k === 3 ? [0.25, 0.5, 0.25] : k === 5 ? [0.0625, 0.25, 0.375, 0.25, 0.0625] : gTaps(k, cvSigma(k));
  const refl = (i, n) => { while (i < 0 || i >= n) i = i < 0 ? -i : 2 * n - 2 - i; return i; };
  const blur2 = (A, w) => {
    const n = A.length, R = (w.length - 1) / 2;
    const H = A.map(r => r.map((_, x) => w.reduce((s, c, j) => s + c * r[refl(x + j - R, n)], 0)));
    return H.map((r, y) => r.map((_, x) => w.reduce((s, c, j) => s + c * H[refl(y + j - R, n)][x], 0)));
  };
  const sharpen2 = (A, a) => {
    const n = A.length;
    return A.map((r, y) => r.map((v, x) => { const nb = A[refl(y - 1, n)][x] + A[refl(y + 1, n)][x] + r[refl(x - 1, n)] + r[refl(x + 1, n)]; return v + a * (v - nb / 4); }));
  };
  const u8 = A => { let c = 0; const B = A.map(r => r.map(v => { const q = Math.round(v); if (q < 0 || q > 255) c++; return clamp(q, 0, 255); })); return [B, c]; };
  const labScene = (noise) => {
    const n = 40, r = CVZ.rng(16);
    const A = [];
    for (let y = 0; y < n; y++) { const row = []; for (let x = 0; x < n; x++) {
      let v = x < 20 ? 70 : 150;
      if (x >= 6 && x <= 13 && y >= 24 && y <= 33) v = 200;
      if (y === 8 && x >= 22) v = 40;
      if (x === 30 && y >= 12) v = 230;
      if ((x - 8) ** 2 + (y - 8) ** 2 <= 1) v = 240;
      if (x >= 23 && x <= 37 && y >= 26 && y <= 37 && x !== 30) v = ((x + y) % 2) ? 190 : 110;
      row.push(v + CVZ.gauss(r) * noise);
    } A.push(row); }
    return A;
  };
  def('labpipe', {
    title: 'The notebook pipeline on a small test image',
    sub: 'A 40 × 40 test image with an edge, a thin bright line, a thin dark line, a tiny dot and a fine checker texture. It goes through the same two steps as the project: GaussianBlur, then filter2D with a sharpening kernel, rounded and clipped to 0 to 255.',
    W: 560, H: 250,
    params: [
      { k: 'k', label: 'Blur kernel size', type: 'select', num: true, v: 9, opts: [[1, '1 (no blur)'], [3, '3 × 3'], [5, '5 × 5'], [9, '9 × 9 (project)'], [15, '15 × 15']] },
      { k: 's', label: 'σ (0 lets OpenCV choose from the size)', type: 'range', min: 0, max: 4, step: 0.1, v: 0, fmt: v => v ? f(v, 1) : 'auto' },
      { k: 'a', label: 'Sharpening amount a (4 gives the project kernel)', type: 'range', min: 0, max: 8, step: 0.5, v: 4 },
      { k: 'noise', label: 'Sensor noise (standard deviation)', type: 'range', min: 0, max: 20, v: 2 },
      { k: 'show', label: 'Show', type: 'select', v: 'img', opts: [['img', 'Images'], ['row', 'Row 20 as a curve (edge and thin bright line)']] }
    ],
    tips: [
      { t: 'The project setting: 9 × 9 with σ chosen by OpenCV (1.7), then the kernel with 5 in the centre. Compare the middle and right panels. Edges come back, the checker texture does not.', set: { k: 9, s: 0, a: 4, noise: 2, show: 'img' } },
      { t: 'Switch to the row view. The edge at column 20 becomes a slope and the one pixel bright line at column 30 shrinks to a small bump. Sharpening steepens both but cannot rebuild the original spike.', set: { show: 'row' } },
      { t: 'Raise noise to 15. The sharpened panel gets grainy, because the kernel boosts every fine change, real or not. This is how sharpening can add false boxes and lower precision.', set: { noise: 15, show: 'img' } },
      { t: 'Use a 3 × 3 blur. Mild blur leaves enough detail for sharpening to restore most of it. The size of the loss decides how much can be won back.', set: { k: 3, s: 0, noise: 2 } },
      { t: 'Push a to 8. Halos and clipped pixels appear at every edge. The clipped count in the readout shows values that left the 0 to 255 range.', set: { k: 9, a: 8, noise: 2 } }
    ],
    draw(z) {
      const { g, p } = z;
      const sg = p.k === 1 ? 0 : (p.s || cvSigma(p.k));
      const A = labScene(p.noise);
      const Bf = p.k === 1 ? A : blur2(A, p.s ? gTaps(p.k, p.s) : cvTaps(p.k));
      const [B] = u8(Bf);
      const [S, clipped] = u8(sharpen2(B, p.a));
      const [O] = u8(A);
      const c0 = 1 + p.a, cn = p.a / 4;
      if (p.show === 'img') {
        const cell = 4.2;
        [[O, 'original'], [B, 'blurred'], [S, 'sharpened']].forEach(([M, t], i) => {
          const x0 = 12 + i * 182;
          D.image(g, M, x0, 22, cell);
          D.text(g, t, x0 + 84, 16, { a: 'center', s: 12, b: true, c: z.col.ink });
        });
      } else {
        const m = D.axes(g, z, [50, 14, 490, 186], [0, 40], [0, 255], { nx: 4, ny: 3, xl: 'column', yl: 'intensity', fx: v => Math.round(v), fy: v => Math.round(v) });
        const plot = (M, c, w, dash) => { g.save(); g.strokeStyle = c; g.lineWidth = w; if (dash) g.setLineDash(dash); g.beginPath(); M[20].forEach((v, i) => { if (i) g.lineTo(m.sx(i), m.sy(v)); else g.moveTo(m.sx(i), m.sy(v)); }); g.stroke(); g.restore(); };
        plot(O, z.col.ink2, 1.4, [4, 4]); plot(B, z.col.cv, 2); plot(S, z.col.orange, 2.2);
        D.text(g, 'dashed original, blue blurred, orange sharpened', 54, 238, { s: 11, c: z.col.ink2 });
      }
      return `<span class="big">σ used: ${p.k === 1 ? 'none' : p.k < 9 && !p.s ? 'fixed binomial weights' : f(sg, 2) + (p.s ? '' : ' from 0.3 ((k − 1) ÷ 2 − 1) + 0.8')}, &nbsp; kernel centre ${f(c0, 1)}, neighbours −${f(cn, 2)}</span><br>The sharpening kernel is the image plus a times (the image minus the average of its four neighbours). With a = 4 it is exactly [[0, −1, 0], [−1, 5, −1], [0, −1, 0]], whose weights add to 1, so flat areas keep their brightness. Pixels clipped to 0 or 255 after sharpening: ${clipped}.`;
    }
  });

  def('freqgain', {
    title: 'What blur removes and sharpening gives back, by frequency',
    sub: 'Every image is a sum of waves. Low frequency means slow changes such as large shapes, high frequency means fine detail such as edges and texture. Each curve shows how much of a wave survives a filter.',
    W: 560, H: 260,
    params: [
      { k: 'k', label: 'Blur kernel size', type: 'select', num: true, v: 9, opts: [[3, '3 × 3'], [5, '5 × 5'], [9, '9 × 9 (project)'], [15, '15 × 15']] },
      { k: 'a', label: 'Sharpening amount a', type: 'range', min: 0, max: 8, step: 0.5, v: 4 },
      { k: 'w', label: 'Probe frequency (fraction of the finest wave)', type: 'range', min: 0.05, max: 1, step: 0.05, v: 0.5 },
      { k: 'log', label: 'Logarithmic gain axis', type: 'check', v: false }
    ],
    tips: [
      { t: 'The project case at half the finest frequency: the 9 × 9 blur keeps about 3 percent, the kernel multiplies by 3, and only about 9 percent comes back.', set: { k: 9, a: 4, w: 0.5, log: false } },
      { t: 'Turn on the log axis and move the probe to 1. Blur leaves about 0.5 percent of the finest wave. Multiplying a tiny number by 5 is still tiny, and any noise at that frequency is multiplied by 5 too.', set: { log: true, w: 1 } },
      { t: 'Try a 3 × 3 blur. Much more survives at middle frequencies, so the same kernel restores far more. Recovery depends on what the blur left.', set: { k: 3, log: false, w: 0.5 } },
      { t: 'Set a to 0. The orange curve flattens at 1, meaning no change. Sharpening is a high pass boost layered on top of the image.', set: { a: 0, k: 9 } }
    ],
    draw(z) {
      const { g, p } = z;
      const t = cvTaps(p.k), R = (p.k - 1) / 2;
      const Hg = w => t.reduce((s, c, i) => s + c * Math.cos(w * Math.PI * (i - R)), 0);
      const Hs = w => 1 + p.a * (1 - Math.cos(w * Math.PI)) / 2;
      const ymax = 2 * Math.ceil((2 + p.a) / 2);
      const tr = v => p.log ? Math.log10(Math.max(Math.abs(v), 1e-4)) : Math.abs(v);
      const m = D.axes(g, z, [50, 14, 330, 210], [0, 1], p.log ? [-4, 1] : [0, ymax], { nx: 4, ny: p.log ? 5 : ymax / 2, xl: 'frequency (1 = finest)', yl: p.log ? '' : 'gain', fx: v => f(v, 2), fy: v => p.log ? String(+Math.pow(10, Math.round(v)).toPrecision(1)) : f(v, 1) });
      D.curve(g, w => tr(Hg(w)), [0, 1], m, z.col.cv, 2.2);
      D.curve(g, w => tr(Hs(w)), [0, 1], m, z.col.orange, 2.2);
      D.curve(g, w => tr(Hg(w) * Hs(w)), [0, 1], m, z.col.purple, 2.6, 200, [6, 3]);
      D.line(g, m.sx(0), m.sy(tr(1)), m.sx(1), m.sy(tr(1)), z.col.ink2, 1, [2, 3]);
      D.line(g, m.sx(p.w), 14, m.sx(p.w), 224, z.col.red, 1.2, [4, 3]);
      const gb = Math.abs(Hg(p.w)), gs = Hs(p.w);
      const tx = 400;
      [['blur keeps', gb, z.col.cv], ['kernel multiplies by', gs, z.col.orange], ['after both', gb * gs, z.col.purple]].forEach(([l, v, c], i) => {
        D.text(g, l, tx, 34 + i * 46, { s: 12, c: z.col.ink2 });
        D.text(g, v < 0.01 ? f(v, 4) : f(v, 3), tx, 52 + i * 46, { s: 14, mono: true, b: true, c });
      });
      D.text(g, 'red line: probe', tx, 176, { s: 11, c: z.col.red });
      return `<span class="big">H<sub>blur</sub>(ω) = Σ<sub>i</sub> w<sub>i</sub> cos(ω i), &nbsp; H<sub>sharpen</sub>(ω) = 1 + a (1 − cos ω) ÷ 2, &nbsp; after both = H<sub>blur</sub> · H<sub>sharpen</sub></span><br>Blue: the Gaussian blur. Orange: the sharpening kernel along one axis (3 − 2 cos ω for the project kernel). Dashed purple: blur followed by sharpening. A filter multiplies each wave by its gain, so a wave reduced to almost nothing cannot be brought back by any finite boost.`;
    }
  });

  const Phi = x => { const s = x < 0 ? -1 : 1, a = Math.abs(x) / Math.SQRT2, t = 1 / (1 + 0.3275911 * a); const e = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-a * a); return 0.5 * (1 + s * e); };
  def('opshift', {
    title: 'Why blur can raise precision while recall falls',
    sub: 'A toy model, not the real detector. Green: confidence scores of 100 real objects. Red: scores of false alarms triggered by texture and clutter. Blur lowers the object scores and also removes many texture alarms.',
    W: 560, H: 250,
    params: [
      { k: 'b', label: 'Blur strength', type: 'range', min: 0, max: 1, step: 0.05, v: 0 },
      { k: 'sh', label: 'Sharpen after blurring', type: 'check', v: false },
      { k: 't', label: 'Confidence threshold', type: 'range', min: 0.1, max: 0.9, step: 0.05, v: 0.4 }
    ],
    tips: [
      { t: 'No blur at threshold 0.4. Most objects pass, along with some texture alarms.', set: { b: 0, sh: false, t: 0.4 } },
      { t: 'Blur 0.5. The green hill slides left so recall drops. The red area shrinks even more, so precision rises. This is the pattern in the project table: P 0.6633 to 0.6802, R 0.5894 to 0.5358.', set: { b: 0.5, sh: false, t: 0.4 } },
      { t: 'Now tick Sharpen. Objects regain a little confidence and recall rises, but amplified noise brings back false alarms and precision falls. The project saw R 0.5358 to 0.5468 and P 0.6802 to 0.6583.', set: { b: 0.5, sh: true, t: 0.4 } },
      { t: 'Move the threshold. Precision and recall always trade against each other, which is why mAP sums over every threshold instead of trusting one.', set: { t: 0.6 } }
    ],
    draw(z) {
      const { g, p } = z;
      const sb = p.sh ? 1 : 0;
      const mo = 0.62 - 0.25 * p.b + 0.05 * p.b * sb, so = 0.15;
      const nf = 80 * (1 - 0.7 * p.b) * (1 + 0.5 * p.b * sb), mf = 0.3 - 0.05 * p.b, sf = 0.12;
      const pdf = (x, mu, s) => Math.exp(-((x - mu) ** 2) / (2 * s * s)) / (s * Math.sqrt(2 * Math.PI));
      const m = D.axes(g, z, [40, 14, 330, 200], [0, 1], [0, 3.4], { nx: 5, ny: 2, xl: 'confidence', fx: v => f(v, 1), fy: v => '' });
      const fill = (fn, c) => { g.save(); g.fillStyle = c; g.beginPath(); g.moveTo(m.sx(p.t), m.sy(0)); for (let i = 0; i <= 100; i++) { const x = p.t + (1 - p.t) * i / 100; g.lineTo(m.sx(x), m.sy(fn(x))); } g.lineTo(m.sx(1), m.sy(0)); g.closePath(); g.fill(); g.restore(); };
      const fo = x => pdf(x, mo, so), ff = x => nf / 100 * pdf(x, mf, sf);
      fill(fo, 'rgba(40,160,100,.25)'); fill(ff, 'rgba(220,70,70,.25)');
      D.curve(g, fo, [0, 1], m, z.col.green, 2.2);
      D.curve(g, ff, [0, 1], m, z.col.red, 2.2);
      D.line(g, m.sx(p.t), 14, m.sx(p.t), 214, z.col.ink, 1.4, [4, 3]);
      const tp = 100 * (1 - Phi((p.t - mo) / so)), fp = nf * (1 - Phi((p.t - mf) / sf));
      const P = tp / Math.max(tp + fp, 1e-9), Rc = tp / 100, F = 2 * P * Rc / Math.max(P + Rc, 1e-9);
      const tx = 400;
      [['kept objects (TP)', f(tp, 1)], ['kept alarms (FP)', f(fp, 1)], ['precision', f(P, 3)], ['recall', f(Rc, 3)]].forEach(([l, v], i) => {
        D.text(g, l, tx, 30 + i * 46, { s: 12, c: z.col.ink2 });
        D.text(g, v, tx, 48 + i * 46, { s: 14, mono: true, b: true, c: i === 2 ? z.col.cv : i === 3 ? z.col.orange : z.col.ink });
      });
      return `<span class="big">P = TP ÷ (TP + FP), &nbsp; R = TP ÷ 100, &nbsp; F1 = 2PR ÷ (P + R) = ${f(F, 3)}</span><br>The shaded areas right of the threshold are what the detector reports. Precision only counts what was reported, so losing many false alarms can raise it even while real objects are missed. The shapes here are made up to show the mechanism. The real numbers are in the project table.`;
    }
  });

  def('stagebars', {
    title: 'Compare the three stages, or your own run',
    sub: 'The default values are the notebook results on COCO128 with YOLO11n. Replace them with your own numbers to see the same comparison.',
    W: 560, H: 260,
    params: [
      { k: 'rows', label: 'Stage | precision recall mAP50 mAP50-95', type: 'area', v: 'Baseline | 0.6633 0.5894 0.6706 0.5026\nBlur | 0.6802 0.5358 0.6176 0.4434\nSharpened | 0.6583 0.5468 0.6277 0.4556' },
      { k: 'view', label: 'Show', type: 'select', v: 'abs', opts: [['abs', 'Values'], ['delta', 'Change from the first stage'], ['rec', 'Share of the loss won back by the last stage']] }
    ],
    tips: [
      { t: 'Values: blur lowers recall and both mAP numbers. Precision is the one metric that rose.', set: { view: 'abs' } },
      { t: 'Change view: mAP50-95 fell by 0.0592 under blur, the largest drop, because the strict IoU thresholds punish blurred box edges most.', set: { view: 'delta' } },
      { t: 'Share won back: sharpening recovered about 20 percent of the loss in recall, mAP50 and mAP50-95. Most of the damage stayed. Precision rose under blur, so it has no loss to win back.', set: { view: 'rec', rows: 'Baseline | 0.6633 0.5894 0.6706 0.5026\nBlur | 0.6802 0.5358 0.6176 0.4434\nSharpened | 0.6583 0.5468 0.6277 0.4556' } },
      { t: 'Imagine a stronger restoration method with made up scores: Deblurred | 0.66 0.57 0.65 0.48. About 60 percent of each loss would come back.', set: { view: 'rec', rows: 'Baseline | 0.6633 0.5894 0.6706 0.5026\nBlur | 0.6802 0.5358 0.6176 0.4434\nDeblurred | 0.66 0.57 0.65 0.48' } }
    ],
    draw(z) {
      const { g, p } = z;
      const st = p.rows.split('\n').map(l => l.split('|')).filter(a => a.length === 2).map(([n, v]) => [n.trim(), v.trim().split(/\s+/).map(Number)]).filter(([, v]) => v.length === 4 && v.every(x => isFinite(x))).slice(0, 4);
      if (st.length < 2) { D.text(g, 'Enter at least two rows: name | four numbers', 20, 40, { s: 13, c: z.col.red }); return 'Each row needs a name, a bar, and four numbers.'; }
      const names = ['Precision', 'Recall', 'mAP50', 'mAP50-95'], cols = [z.col.ink2, z.col.cv, z.col.orange, z.col.purple];
      const base = st[0][1], prev = st[st.length - 2][1], last = st[st.length - 1][1];
      let vals, lo, hi, fy;
      if (p.view === 'abs') { vals = st.map(s => s[1]); lo = 0; hi = 1; fy = v => f(v, 1); }
      else if (p.view === 'delta') { vals = st.slice(1).map(s => s[1].map((v, i) => v - base[i])); const mx = Math.ceil(Math.max(0.02, ...vals.flat().map(Math.abs)) * 1.1 / 0.02) * 0.02; lo = -mx; hi = mx; fy = v => f(v, 2); }
      else { vals = [last.map((v, i) => { const loss = base[i] - prev[i]; return loss <= 1e-9 ? null : (v - prev[i]) / loss; })]; const ok = vals[0].filter(v => v !== null); lo = Math.min(-0.5, Math.floor(Math.min(0, ...ok) * 2) / 2); hi = Math.max(1, Math.ceil(Math.max(0, ...ok) * 2) / 2); fy = v => Math.round(v * 100) + '%'; }
      const m = D.axes(g, z, [56, 14, 470, 196], [0, 4], [lo, hi], { nx: 4, ny: p.view === 'rec' ? Math.round((hi - lo) * 2) : 4, xl: '', fx: () => '', fy });
      D.line(g, m.sx(0), m.sy(0), m.sx(4), m.sy(0), z.col.ink2, 1);
      const groups = vals.length, bw = 0.8 / groups;
      names.forEach((nm, j) => {
        D.text(g, nm, m.sx(j + 0.5), 228, { a: 'center', s: 11.5, b: true, c: z.col.ink });
        vals.forEach((v, i) => {
          if (v[j] === null) { D.text(g, 'no loss', m.sx(j + 0.5), m.sy(0) - 6, { a: 'center', s: 11, c: z.col.ink2 }); return; }
          const x = m.sx(j + 0.1 + i * bw), w = m.sx(j + 0.1 + (i + 1) * bw) - x - 2, y0 = m.sy(0), y1 = m.sy(v[j]);
          D.rect(g, x, Math.min(y0, y1), w, Math.abs(y1 - y0), { fill: cols[(i + (p.view === 'delta' ? 1 : 0) + (p.view === 'rec' ? 3 : 0)) % 4] });
          if (groups <= 3) D.text(g, p.view === 'rec' ? Math.round(v[j] * 100) + '%' : (p.view === 'delta' && v[j] > 0 ? '+' : '') + f(v[j], p.view === 'abs' ? 3 : 4), x + w / 2, (v[j] >= 0 ? y1 - 4 : y1 + 12), { a: 'center', s: groups > 2 ? 9 : 10.5, mono: true, c: z.col.ink });
        });
      });
      const legendNames = p.view === 'abs' ? st.map(s => s[0]) : p.view === 'delta' ? st.slice(1).map(s => s[0] + ' minus ' + st[0][0]) : [st[st.length - 1][0] + ' share won back'];
      legendNames.forEach((n, i) => { const c = cols[(i + (p.view === 'delta' ? 1 : 0) + (p.view === 'rec' ? 3 : 0)) % 4]; D.rect(g, 60 + i * 170, 244, 10, 10, { fill: c }); D.text(g, n, 74 + i * 170, 253, { s: 11, c: z.col.ink2 }); });
      const F1 = st.map(([n, v]) => `${n} ${f(2 * v[0] * v[1] / (v[0] + v[1]), 4)}`).join(', ');
      return `<span class="big">share won back = (restored − degraded) ÷ (baseline − degraded)</span><br>F1 at the reported operating point: ${F1}. A share of 100 percent would mean sharpening fully undid the blur, 0 percent means no help, and a negative share means it made things worse.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 17: exam revision */
  def('netsheet', {
    title: 'Exam calculator: a stack of layers, checked line by line',
    sub: 'Type one layer per line. conv k s p channels, optionally followed by a dilation, or pool k s. The table gives every number examiners ask for: output size, channels, weights, multiply adds and receptive field.',
    W: 560, H: 270,
    params: [
      { k: 'n', label: 'Input size (square)', type: 'range', min: 8, max: 512, step: 8, v: 224 },
      { k: 'c', label: 'Input channels', type: 'select', num: true, v: 3, opts: [[1, '1 (grey)'], [3, '3 (RGB)'], [64, '64']] },
      { k: 'L', label: 'Layers: conv k s p out [dilation] or pool k s', type: 'area', v: 'conv 3 1 1 64\nconv 3 1 1 64\npool 2 2\nconv 3 1 1 128' },
      { k: 'bias', label: 'Count bias terms', type: 'check', v: true }
    ],
    tips: [
      { t: 'The VGG opening: two 3 × 3 convs with 64 channels and a 2 × 2 pool. The first conv has 3 × 3 × 3 × 64 + 64 = 1,792 weights, the second 36,928.', set: { n: 224, c: 3, L: 'conv 3 1 1 64\nconv 3 1 1 64\npool 2 2\nconv 3 1 1 128', bias: true } },
      { t: 'A classic exam line: 32 × 32 input, 5 × 5 kernel, stride 2, padding 2. Output ⌊(32 + 4 − 5) ÷ 2⌋ + 1 = 16.', set: { n: 32, c: 3, L: 'conv 5 2 2 16' } },
      { t: 'Five stride 2 stages take 224 down to 7, the size of the last feature map in ResNet and VGG.', set: { n: 224, c: 3, L: 'conv 3 2 1 32\nconv 3 2 1 64\nconv 3 2 1 128\nconv 3 2 1 256\nconv 3 2 1 512' } },
      { t: 'Dilation 2 makes a 3 × 3 kernel reach 5 pixels with 9 weights. Padding 2 keeps the size. Watch the receptive field grow from 5 to 9 to 17 over three layers with dilations 2, 2 and 4.', set: { n: 64, c: 64, L: 'conv 3 1 2 64 2\nconv 3 1 2 64 2\nconv 3 1 4 64 4' } },
      { t: 'Two 3 × 3 layers reach 5 pixels with 73,856 weights. Replace both lines with conv 5 1 2 64: the reach is the same but the weights rise to 102,464, because 2 × 9 = 18 is less than 25.', set: { n: 56, c: 64, L: 'conv 3 1 1 64\nconv 3 1 1 64' } }
    ],
    draw(z) {
      const { g, p } = z;
      let n = p.n, c = p.c, r = 1, j = 1, totP = 0, totM = 0;
      const rows = [['layer', 'output', 'weights', 'mult adds', 'RF']];
      const lines = p.L.split('\n').map(l => l.trim()).filter(Boolean).slice(0, 7);
      let err = '';
      lines.forEach((l, i) => {
        if (err) return;
        const a = l.split(/\s+/), t = a[0], v = a.slice(1).map(Number);
        if (t === 'conv' && v.length >= 4 && v.every(x => Number.isFinite(x) && x >= 0)) {
          const [k, s, pd, co, d = 1] = v, ke = d * (k - 1) + 1;
          const o = Math.floor((n + 2 * pd - ke) / Math.max(1, s)) + 1;
          if (o < 1) { err = `line ${i + 1}: the kernel no longer fits`; return; }
          const w = k * k * c * co + (p.bias ? co : 0), mac = o * o * k * k * c * co;
          r += (ke - 1) * j; j *= s; totP += w; totM += mac;
          rows.push([`conv ${k}×${k}${d > 1 ? ' d' + d : ''} s${s}`, `${o}×${o}×${co}`, w.toLocaleString('en-US'), (mac / 1e6).toFixed(1) + ' M', r]);
          n = o; c = co;
        } else if (t === 'pool' && v.length >= 2 && v.every(x => Number.isFinite(x) && x > 0)) {
          const [k, s] = v, o = Math.floor((n - k) / s) + 1;
          if (o < 1) { err = `line ${i + 1}: the window no longer fits`; return; }
          r += (k - 1) * j; j *= s;
          rows.push([`pool ${k}×${k} s${s}`, `${o}×${o}×${c}`, '0', '0', r]);
          n = o;
        } else err = `line ${i + 1}: write conv k s p out [d] or pool k s`;
      });
      const xs = [14, 240, 340, 450, 540];
      rows.forEach((rw, i) => rw.forEach((v, q) => D.text(g, String(v), xs[q] + (q ? 0 : 0), 24 + i * 26, { a: q === 0 ? 'left' : 'right', s: i ? 12 : 11, mono: i > 0, b: i === 0 || q === 1, c: i ? z.col.ink : z.col.ink2 })));
      D.line(g, 14, 31, 546, 31, z.col.line, 1);
      const yb = 24 + rows.length * 26;
      D.line(g, 14, yb - 18, 546, yb - 18, z.col.line, 1);
      D.text(g, 'total', 14, yb, { s: 12, b: true, c: z.col.ink });
      D.text(g, totP.toLocaleString('en-US'), 340, yb, { a: 'right', s: 12, mono: true, b: true, c: z.col.cv });
      D.text(g, (totM / 1e6).toFixed(1) + ' M', 450, yb, { a: 'right', s: 12, mono: true, b: true, c: z.col.orange });
      if (err) D.text(g, err, 14, 258, { s: 12, b: true, c: z.col.red });
      return `<span class="big">out = ⌊(n + 2p − d(k − 1) − 1) ÷ s⌋ + 1, &nbsp; weights = k² C<sub>in</sub> C<sub>out</sub> + C<sub>out</sub>, &nbsp; mult adds = out² k² C<sub>in</sub> C<sub>out</sub>, &nbsp; r ← r + d(k − 1) j, &nbsp; j ← j s</span><br>The column header RF is the receptive field in input pixels, and j is the distance between neighbouring outputs measured in input pixels. Pooling has no weights but still grows the receptive field and the jump.`;
    }
  });

})();
