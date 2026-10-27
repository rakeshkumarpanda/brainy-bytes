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

})();
