/* ===== GPU Programming animations (tools/cuda-build), on the framework in assets/cvviz.js =====
   Every animation is declared with CVZ.def(name, spec). Every value it uses is a control the reader can change,
   stepped animations have Play, Step, Back and Reset, and answer boxes use reveal: true so a shown answer hides
   again when an input changes. The bottom of this file colours CUDA listings and wires Copy buttons and line notes. */
(() => {
  const { def, D, f, esc } = CVZ;
  const cdiv = (a, b) => Math.floor((a + b - 1) / b);
  const fmt = n => Number(n).toLocaleString('en-US', { maximumFractionDigits: 3 });
  const W = (z, s, x, y, o) => D.text(z.g, s, x, y, Object.assign({ c: z.col.ink }, o || {}));
  window.CUDAZ = { cdiv, fmt, W };
})();

/* ---------- 1.1 latency against throughput: a CPU and a GPU clear the same pile of jobs ---------- */
(() => {
  const { def, D } = CVZ, { cdiv, fmt, W } = CUDAZ;
  def('race', {
    title: 'CPU against GPU on a pile of jobs', sub: 'Press Play. The CPU finishes one job at a time. The GPU finishes a whole batch per round.',
    W: 600, H: 250,
    params: [
      { k: 'n', label: 'Jobs in the pile', v: 1000, min: 1, max: 4096, step: 1 },
      { k: 'cpu', label: 'CPU time per job (ms)', v: 10, min: 1, max: 50, step: 1 },
      { k: 'gpu', label: 'GPU time per round (ms)', v: 15, min: 1, max: 200, step: 1 },
      { k: 'c', label: 'Jobs the GPU does in one round', v: 1000, min: 1, max: 4096, step: 1 }
    ],
    tips: [
      { t: 'The lecture case: 1000 images, CPU 10 ms each, GPU 15 ms per round of 1000. The CPU wins one image, the GPU wins the pile by about 667 times.', set: { n: 1000, cpu: 10, gpu: 15, c: 1000 }, play: true },
      { t: 'Only one job. Now the CPU is faster, because latency is all that counts.', set: { n: 1, cpu: 10, gpu: 15, c: 1000 } },
      { t: 'Workbook P1.1.4: CPU 5 ms, GPU 40 ms for up to 256. Try 8 jobs (a tie) and 9 jobs (GPU wins).', set: { n: 8, cpu: 5, gpu: 40, c: 256 } },
      { t: 'Workbook P1.1.3: 1024 jobs, rounds of 256 take 40 ms. Watch four GPU rounds against 1024 CPU jobs.', set: { n: 1024, cpu: 5, gpu: 40, c: 256 }, play: true }
    ],
    steps: () => 20,
    draw(z) {
      const { n, cpu, gpu, c } = z.p, g = z.g;
      const rounds = cdiv(n, c), tc = n * cpu, tg = rounds * gpu, T = Math.max(tc, tg), now = T * z.step / 20;
      const doneC = Math.min(n, Math.floor(now / cpu)), doneG = Math.min(n, Math.floor(now / gpu) * c);
      const lane = (y, name, done, total, col) => {
        W(z, name, 20, y - 8, { b: true });
        D.rect(g, 20, y, 440, 26, { fill: z.col.bg, stroke: z.col.line });
        D.rect(g, 20, y, 440 * done / n, 26, { fill: col });
        W(z, `${fmt(done)} of ${fmt(n)} done`, 470, y + 17, { s: 12 });
        W(z, `finishes at ${fmt(total)} ms`, 470, y + 34, { s: 11, c: z.col.ink2 });
      };
      W(z, `Clock: ${fmt(Math.round(now * 100) / 100)} ms`, 20, 24, { b: true, s: 14, c: z.col.cv });
      lane(70, 'CPU: one job at a time', doneC, tc, z.col.orange);
      lane(150, `GPU: ${fmt(c)} jobs per round, ${rounds} round${rounds > 1 ? 's' : ''}`, doneG, tg, z.col.green);
      const thC = 1000 / cpu, thG = n * 1000 / tg;
      const win = tg < tc ? 'GPU' : tg > tc ? 'CPU' : 'Neither (a tie)';
      return `<b>Latency of one job:</b> CPU ${cpu} ms, GPU ${gpu} ms, so the ${cpu < gpu ? 'CPU' : cpu > gpu ? 'GPU' : 'two machines tie'} wins one job.<br>
        <b>Whole pile:</b> CPU ${fmt(n)} × ${cpu} = ${fmt(tc)} ms. GPU ⌈${fmt(n)} ÷ ${fmt(c)}⌉ = ${rounds} round${rounds > 1 ? 's' : ''} × ${gpu} = ${fmt(tg)} ms. Winner: <b>${win}</b>.<br>
        <b>Throughput:</b> CPU ${fmt(thC)} jobs per second, GPU ${fmt(thG)} jobs per second (${fmt(thG / thC)} times the CPU).`;
    }
  });

  def('peak', {
    title: 'Where peak FLOPs come from', sub: 'Step through peak = work per tick per core × ticks per second × cores, and the power each design needs.',
    W: 600, H: 260,
    params: [
      { k: 'cores', label: 'Cores', v: 2048, min: 1, max: 20000, step: 1 },
      { k: 'ghz', label: 'Clock (GHz)', v: 0.8, min: 0.1, max: 5, step: 0.01 },
      { k: 'fl', label: 'FLOPs per tick per core (FMA = 2)', v: 2, min: 1, max: 64, step: 1 },
      { k: 'v', label: 'Voltage (relative to 1.0)', v: 0.8, min: 0.5, max: 1.5, step: 0.05 },
      { k: 'ccores', label: 'Compare with: CPU cores', v: 8, min: 1, max: 128, step: 1 },
      { k: 'cghz', label: 'Compare with: CPU clock (GHz)', v: 2, min: 0.1, max: 6, step: 0.01 },
      { k: 'cfl', label: 'Compare with: CPU FLOPs per tick per core', v: 16, min: 1, max: 64, step: 1 }
    ],
    tips: [
      { t: 'Workbook worked example: 8 CPU cores at 2 GHz doing 16 FLOPs per tick against 2048 GPU cores at 0.8 GHz doing one FMA. The GPU is 12.8 times faster at a slower clock.', set: { cores: 2048, ghz: 0.8, fl: 2, ccores: 8, cghz: 2, cfl: 16 }, play: true },
      { t: 'NVIDIA T4: 40 SMs × 64 cores = 2560 cores, one FMA per tick at 1.59 GHz. You get about 8.14 TFLOP/s, the data sheet says 8.1.', set: { cores: 2560, ghz: 1.59, fl: 2 }, play: true },
      { t: 'A100 FP32: 108 × 64 = 6912 cores at 1.41 GHz. About 19.5 TFLOP/s.', set: { cores: 6912, ghz: 1.41, fl: 2 }, play: true },
      { t: 'Raise the voltage to 1.1 and the clock by 20 percent: power grows by about 45 percent (1.1² × 1.2 = 1.452).', set: { v: 1.1 } }
    ],
    steps: () => 4,
    draw(z) {
      const p = z.p, g = z.g, s = z.step;
      const perTick = p.fl * p.cores, peak = perTick * p.ghz * 1e9;
      const cpuPeak = p.cfl * p.ccores * p.cghz * 1e9;
      const pow = p.cores * p.v * p.v * p.ghz, cpow = p.ccores * 1 * 1 * p.cghz;
      const lines = [
        `1. Work per tick for the whole chip: ${p.fl} × ${fmt(p.cores)} = ${fmt(perTick)} FLOPs`,
        `2. Ticks per second: ${p.ghz} GHz = ${fmt(p.ghz * 1e9)} ticks`,
        `3. Peak: ${fmt(perTick)} × ${fmt(p.ghz * 1e9)} = ${fmt(peak / 1e9)} GFLOP/s`,
        `4. CPU for comparison: ${p.cfl} × ${p.ccores} × ${p.cghz} GHz = ${fmt(cpuPeak / 1e9)} GFLOP/s`
      ];
      lines.slice(0, s).forEach((l, i) => W(z, l, 16, 30 + i * 26, { s: 13, mono: true }));
      if (s >= 4) {
        const mx = Math.max(peak, cpuPeak);
        W(z, 'Peak', 16, 140, { b: true }); W(z, 'GPU', 100, 154, { s: 11 }); W(z, 'CPU', 100, 178, { s: 11 });
        D.rect(g, 140, 140, 400 * peak / mx, 18, { fill: z.col.green }); W(z, `GPU ${fmt(peak / 1e9)}`, 146 + 400 * peak / mx > 470 ? 146 : 146 + 400 * peak / mx, 154, { s: 11, c: 400 * peak / mx > 330 ? '#fff' : z.col.ink });
        D.rect(g, 140, 164, 400 * cpuPeak / mx, 18, { fill: z.col.orange }); W(z, `CPU ${fmt(cpuPeak / 1e9)}`, 400 * cpuPeak / mx > 330 ? 146 : 146 + 400 * cpuPeak / mx, 178, { s: 11, c: 400 * cpuPeak / mx > 330 ? '#fff' : z.col.ink });
        const pm = Math.max(pow, cpow);
        W(z, 'Power', 16, 208, { b: true }); W(z, 'GPU', 100, 222, { s: 11 }); W(z, 'CPU', 100, 246, { s: 11 });
        D.rect(g, 140, 208, 400 * pow / pm, 18, { fill: z.col.purple });
        D.rect(g, 140, 232, 400 * cpow / pm, 18, { fill: z.col.orange });
      }
      return s < 4 ? 'Press Step or Play to build the peak one factor at a time.' :
        `<b>GPU peak ${fmt(peak / 1e12)} TFLOP/s</b>, CPU peak ${fmt(cpuPeak / 1e12)} TFLOP/s, ratio ${fmt(peak / cpuPeak)}.<br>
         Power grows like cores × V² × f. With these settings the GPU uses about ${fmt(pow / cpow)} times the CPU power (CPU voltage taken as 1.0). The GPU wins on work per watt only when there is enough parallel work to keep every core busy.`;
    }
  });
})();

/* ---------- 1.2 Amdahl, Gustafson and the PCIe trip ---------- */
(() => {
  const { def, D } = CVZ, { fmt, W } = CUDAZ;
  def('amdahl', {
    title: "Amdahl's law: the serial part sets the ceiling", sub: 'Step through the run time of one job, then see the speedup curve for every processor count.',
    W: 640, H: 300,
    params: [
      { k: 'p', label: 'Parallel fraction P', v: 0.9, min: 0, max: 1, step: 0.01 },
      { k: 'n', label: 'Processors N', v: 16, min: 1, max: 1024, step: 1 },
      { k: 'gus', label: "Also show Gustafson's law (the work grows with N)", type: 'check', v: false }
    ],
    tips: [
      { t: 'P = 0.9 and N = 16. The serial 10 percent never shrinks, so the speedup is only 6.4 and can never pass 10.', set: { p: 0.9, n: 16 }, play: true },
      { t: 'Lecture 5 quiz: 1 percent serial on 61 cores. Speedup 38.125, efficiency 62.5 percent, ceiling 100.', set: { p: 0.99, n: 61 }, play: true },
      { t: 'P = 0.99 needs 891 processors to reach 90 of its 100 times ceiling (workbook P1.4.6).', set: { p: 0.99, n: 891 } },
      { t: "Tick Gustafson: if the problem grows with N, the scaled speedup is N − (1 − P)(N − 1), almost straight.", set: { p: 0.9, n: 64, gus: true } }
    ],
    steps: () => 4,
    draw(z) {
      const { p, n, gus } = z.p, g = z.g, s = z.step;
      const S = 1 / ((1 - p) + p / n), Smax = p < 1 ? 1 / (1 - p) : Infinity, Sg = n - (1 - p) * (n - 1);
      // run time bars
      W(z, 'Run time of the job', 16, 22, { b: true });
      const bw = 250;
      D.rect(g, 16, 32, bw * (1 - p), 22, { fill: z.col.red }); D.rect(g, 16 + bw * (1 - p), 32, bw * p, 22, { fill: z.col.green });
      W(z, '1 processor', 16 + bw + 8, 48, { s: 11 });
      if (s >= 1) {
        D.rect(g, 16, 64, bw * (1 - p), 22, { fill: z.col.red });
        if (s >= 2) D.rect(g, 16 + bw * (1 - p), 64, bw * p / n, 22, { fill: z.col.green });
        W(z, `${n} processors`, 16 + bw + 8, 80, { s: 11 });
      }
      const lines = ['1. Serial (red) stays: 1 − P = ' + f2(1 - p),
        `2. Parallel: ${f2(p)} ÷ ${n} = ${f2(p / n)}`,
        `3. S = 1 ÷ (${f2(1 - p)} + ${f2(p / n)}) = ${f2(S)}`,
        `4. Ceiling 1 ÷ (1 − P) = ${isFinite(Smax) ? f2(Smax) : 'none'}`];
      lines.slice(0, s).forEach((l, i) => W(z, l, 16, 112 + i * 20, { s: 12, mono: true }));
      // curve
      const box = [430, 20, 195, 230], top = Math.min(1100, Math.max(gus ? n : 4, isFinite(Smax) ? Smax * 1.1 : n));
      const m = D.axes(g, z, box, [1, 1024], [0, top], { nx: 2, ny: 4, xl: 'N', fy: v => Math.round(v) });
      D.curve(g, x => 1 / ((1 - p) + p / x), [1, 1024], m, z.col.cv, 2.5);
      if (gus) D.curve(g, x => x - (1 - p) * (x - 1), [1, 1024], m, z.col.purple, 2, 200, [5, 4]);
      if (isFinite(Smax) && Smax <= top) D.line(g, box[0], m.sy(Smax), box[0] + box[2], m.sy(Smax), z.col.red, 1, [4, 4]);
      if (s >= 3) D.circle(g, m.sx(n), m.sy(Math.min(S, top)), 5, { fill: z.col.orange });
      return `<b>Amdahl speedup ${f2(S)}</b> on ${n} processors, efficiency S ÷ N = ${f2(100 * S / n)} percent, ceiling ${isFinite(Smax) ? f2(Smax) : 'none (fully parallel)'}.` +
        (gus ? `<br><b>Gustafson</b> (bigger problem on more processors): scaled speedup = N − (1 − P)(N − 1) = ${f2(Sg)} (dashed purple).` : '') +
        '<br>Red dashed line: the ceiling 1 ÷ (1 − P) that no processor count can pass.';
    }
  });
  const f2 = v => (Math.round(v * 1000) / 1000).toString();

  def('pcie', {
    title: 'The trip over PCIe: copy in, compute, copy out', sub: 'Each step adds one part of the GPU time. Compare the total with the CPU.',
    W: 600, H: 230,
    params: [
      { k: 'mb', label: 'Data to copy in (MB)', v: 8, min: 0, max: 512, step: 1 },
      { k: 'mbo', label: 'Data to copy out (MB)', v: 4, min: 0, max: 512, step: 1 },
      { k: 'bw', label: 'PCIe bandwidth (GB/s)', v: 12, min: 1, max: 64, step: 1 },
      { k: 'k', label: 'Kernel time (ms)', v: 0.5, min: 0.01, max: 50, step: 0.01 },
      { k: 'cpu', label: 'CPU time (ms)', v: 2, min: 0.01, max: 1000, step: 0.01 },
      { k: 'reps', label: 'Time steps (kernel launches)', v: 1, min: 1, max: 200, step: 1 },
      { k: 'every', label: 'Copy in and out every step', type: 'check', v: false }
    ],
    tips: [
      { t: 'Workbook P1.3.3 style: the kernel is 4 times faster than the CPU, yet the copies make the GPU slower overall.', set: { mb: 36, mbo: 36, bw: 12, k: 0.5, cpu: 2, reps: 1, every: false }, play: true },
      { t: 'Workbook P1.3.5: a 4 MB grid for 100 steps, kernel 0.05 ms, CPU 9 ms per step. Copy once: about 158 times faster.', set: { mb: 4.194304, mbo: 4.194304, bw: 12, k: 0.05, cpu: 900, reps: 100, every: false }, play: true },
      { t: 'Same, but copy every step. The speedup falls to about 12 times. Keep data on the GPU.', set: { mb: 4.194304, mbo: 4.194304, bw: 12, k: 0.05, cpu: 900, reps: 100, every: true }, play: true }
    ],
    steps: () => 3,
    draw(z) {
      const { mb, mbo, bw, k, cpu, reps, every } = z.p, g = z.g, s = z.step;
      const tin = mb / 1000 / bw * 1000, tout = mbo / 1000 / bw * 1000;
      const cin = every ? tin * reps : tin, cout = every ? tout * reps : tout, kk = k * reps;
      const tot = cin + kk + cout, mx = Math.max(tot, cpu);
      const sc = 520 / mx;
      W(z, 'GPU', 16, 60, { b: true }); W(z, 'CPU', 16, 140, { b: true });
      let x = 60;
      const seg = (w, c, lab) => { D.rect(g, x, 40, Math.max(1, w * sc), 30, { fill: c }); if (w * sc > 70) W(z, lab, x + 4, 60, { s: 11, c: '#fff' }); x += w * sc; };
      if (s >= 1) seg(cin, z.col.orange, 'copy in');
      if (s >= 2) seg(kk, z.col.green, 'kernel');
      if (s >= 3) seg(cout, z.col.purple, 'copy out');
      D.rect(g, 60, 120, cpu * sc, 30, { fill: z.col.ink2 });
      W(z, `${fmt(cpu)} ms`, 60 + Math.min(cpu * sc, 450) + 6, 140, { s: 11 });
      W(z, 'orange copy in   green kernel   purple copy out', 60, 190, { s: 11, c: z.col.ink2 });
      return s < 3 ? 'Press Step to add copy in, kernel and copy out.' :
        `Copy in ${fmt(cin)} ms + kernel ${fmt(kk)} ms + copy out ${fmt(cout)} ms = <b>${fmt(tot)} ms</b> on the GPU against ${fmt(cpu)} ms on the CPU.<br>
         Kernel only speedup ${fmt(cpu / kk)}. End to end speedup <b>${fmt(cpu / tot)}</b> ${cpu / tot < 1 ? '<span class="bad">(a slowdown)</span>' : ''}. Copy time = bytes ÷ bandwidth.`;
    }
  });

  def('heat', {
    title: 'Heat spreading on a grid, one time step at a time', sub: 'Each cell takes the average pull of its four neighbours. Click a cell to heat it, then step.',
    W: 600, H: 300,
    params: [
      { k: 'n', label: 'Grid size', v: 12, min: 5, max: 24, step: 1 },
      { k: 'a', label: 'α (how fast heat spreads)', v: 0.2, min: 0.01, max: 0.35, step: 0.01 },
      { k: 'q', label: 'βQ (heat added to the hot spot each step)', v: 0, min: 0, max: 20, step: 0.5 },
      { k: 'steps', label: 'Time steps to animate', v: 30, min: 1, max: 80, step: 1 }
    ],
    tips: [
      { t: 'α = 0.2: the hot spot spreads smoothly and cools, like a hot battery cell warming its neighbours.', set: { a: 0.2, q: 0 }, play: true },
      { t: 'Add a heat source βQ = 10 at the centre: the battery keeps heating and a warm zone grows.', set: { a: 0.2, q: 10 }, play: true },
      { t: 'α = 0.3 is above the safe limit 0.25 for 2 D. The centre weight 1 − 4α turns negative and the values start to flip sign (unstable).', set: { a: 0.3, q: 0 }, play: true }
    ],
    init(z) { z.state.hot = [[Math.floor(z.p.n / 2), Math.floor(z.p.n / 2)]]; },
    change(z, k) { if (k === 'n') z.state.hot = [[Math.floor(z.p.n / 2), Math.floor(z.p.n / 2)]]; },
    click(z, x, y, kind) {
      if (kind !== 'down') return;
      const n = z.p.n, c = 260 / n, i = Math.floor((y - 20) / c), j = Math.floor((x - 20) / c);
      if (i >= 0 && j >= 0 && i < n && j < n) { z.state.hot.push([i, j]); z.step = 0; }
    },
    steps: z => z.p.steps,
    draw(z) {
      const { n, a, q } = z.p, g = z.g;
      let T = Array.from({ length: n }, () => new Array(n).fill(0));
      (z.state.hot || []).forEach(([i, j]) => { if (i < n && j < n) T[i][j] = 100; });
      const src = (z.state.hot || [])[0] || [0, 0];
      for (let s = 0; s < z.step; s++) {
        const N = T.map(r => r.slice());
        for (let i = 1; i < n - 1; i++) for (let j = 1; j < n - 1; j++)
          N[i][j] = T[i][j] + a * (T[i - 1][j] + T[i + 1][j] + T[i][j - 1] + T[i][j + 1] - 4 * T[i][j]) + ((i === src[0] && j === src[1]) ? q : 0);
        T = N;
      }
      const c = 260 / n;
      let mx = 0, mn = 0;
      T.forEach(r => r.forEach(v => { mx = Math.max(mx, v); mn = Math.min(mn, v); }));
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
        const v = T[i][j], u = Math.max(0, Math.min(1, v / 100));
        g.fillStyle = v < -0.01 ? 'rgb(40,80,220)' : `rgb(${Math.round(30 + 225 * u)},${Math.round(40 + 120 * u * (1 - u) * 2)},${Math.round(60 * (1 - u))})`;
        g.fillRect(20 + j * c, 20 + i * c, c - 1, c - 1);
      }
      const ci = Math.floor(n / 2);
      W(z, `Step ${z.step}`, 300, 40, { b: true, s: 15 });
      W(z, `centre cell ${CVZ.f(T[ci][ci], 2)}`, 300, 66, { s: 13 });
      W(z, `hottest ${CVZ.f(mx, 2)}`, 300, 88, { s: 13 });
      W(z, `coldest ${CVZ.f(mn, 2)}`, 300, 110, { s: 13 });
      W(z, `centre weight 1 − 4α = ${CVZ.f(1 - 4 * a, 2)}`, 300, 140, { s: 13, c: 1 - 4 * a < 0 ? z.col.red : z.col.ink });
      W(z, 'Border cells are held at 0 (fixed edges).', 300, 170, { s: 11, c: z.col.ink2 });
      W(z, 'One GPU thread updates one cell.', 300, 190, { s: 11, c: z.col.ink2 });
      return `T<sub>new</sub> = T + α(up + down + left + right − 4T) + βQ. Every cell uses only old values, so all ${n * n} cells can be updated at the same time by ${n * n} threads. The code keeps two grids (old and new) so no thread reads a value another thread already changed.` +
        (1 - 4 * a < 0 ? '<br><span class="bad">Unstable: α is above 0.25, so the centre weight is negative and the values oscillate.</span>' : '');
    }
  });

  def('sepconv', {
    title: 'Normal against depthwise separable convolution', sub: 'Step through the multiplication count of each layer and the saving.',
    W: 600, H: 220,
    params: [
      { k: 'h', label: 'Output height = width', v: 32, min: 1, max: 224, step: 1 },
      { k: 'cin', label: 'Input channels', v: 64, min: 1, max: 1024, step: 1 },
      { k: 'cout', label: 'Output channels', v: 128, min: 1, max: 1024, step: 1 },
      { k: 'k', label: 'Filter size K', v: 3, min: 1, max: 11, step: 2 }
    ],
    tips: [
      { t: 'Workbook worked example: K = 3, 64 to 128 channels, 32 × 32. Normal 75,497,472, separable 8,978,432, about 8.4 times fewer.', set: { h: 32, cin: 64, cout: 128, k: 3 }, play: true },
      { t: 'MobileNet style: 56 × 56, 64 to 64 channels. Ratio about 0.127.', set: { h: 56, cin: 64, cout: 64, k: 3 }, play: true },
      { t: 'Many output channels and K = 7: the saving approaches K² = 49 times.', set: { h: 14, cin: 256, cout: 1024, k: 7 }, play: true }
    ],
    steps: () => 3,
    draw(z) {
      const { h, cin, cout, k } = z.p, g = z.g, s = z.step;
      const norm = h * h * cin * cout * k * k, dw = h * h * cin * k * k, pw = h * h * cin * cout, sep = dw + pw;
      const mx = norm, L = 400;
      const bar = (y, v, c, lab) => { D.rect(g, 170, y, Math.max(1, L * v / mx), 24, { fill: c }); W(z, lab, 16, y + 16, { s: 12 }); W(z, fmt(v), 170 + Math.min(L * v / mx, 300) + 6, y + 16, { s: 11 }); };
      bar(20, norm, z.col.red, 'Normal');
      if (s >= 1) bar(60, dw, z.col.orange, 'Depthwise');
      if (s >= 2) bar(100, pw, z.col.purple, 'Pointwise 1 × 1');
      if (s >= 3) bar(140, sep, z.col.green, 'Separable total');
      return `Normal = H × W × C<sub>in</sub> × C<sub>out</sub> × K² = ${fmt(norm)}.` + (s >= 3 ? `<br>Separable = H × W × C<sub>in</sub> × K² + H × W × C<sub>in</sub> × C<sub>out</sub> = ${fmt(sep)}.<br>Ratio = (K² + C<sub>out</sub>) ÷ (K² × C<sub>out</sub>) = <b>${CVZ.f(sep / norm, 4)}</b>, so ${CVZ.f(norm / sep, 2)} times fewer multiplications.` : '');
    }
  });
})();

/* ---------- 2.1 to 2.4 the CUDA execution model ---------- */
(() => {
  const { def, D } = CVZ, { cdiv, fmt, W } = CUDAZ;

  def('hostflow', {
    title: 'The six steps of every CUDA program', sub: 'Press Step to watch data move between host (CPU) memory and device (GPU) memory.',
    W: 620, H: 270,
    params: [
      { k: 'n', label: 'Elements N', v: 8, min: 1, max: 16, step: 1 },
      { k: 'b', label: 'Threads per block', v: 4, min: 1, max: 16, step: 1 },
      { k: 'nocopy', label: 'Forget the copy back (a common bug)', type: 'check', v: false }
    ],
    tips: [
      { t: 'Vector add of 8 numbers with blocks of 4: two blocks, every thread adds one pair.', set: { n: 8, b: 4, nocopy: false }, play: true },
      { t: 'N = 10 with blocks of 4: three blocks are launched and two threads must do nothing (the if (i &lt; n) guard).', set: { n: 10, b: 4, nocopy: false }, play: true },
      { t: 'Forget cudaMemcpy back: the host array c stays zero even though the GPU computed the answer.', set: { n: 8, b: 4, nocopy: true }, play: true }
    ],
    steps: () => 6,
    draw(z) {
      const { n, b, nocopy } = z.p, g = z.g, s = z.step;
      const a = Array.from({ length: n }, (_, i) => i + 1), bb = a.map(v => 10 * v), c = a.map((v, i) => v + bb[i]);
      const names = ['1. cudaMalloc: reserve d_a, d_b, d_c on the GPU', '2. cudaMemcpy host to device: copy a and b', `3. Launch add<<<${cdiv(n, b)}, ${b}>>>: ${cdiv(n, b) * b} threads start`,
        '4. Each thread i < N computes d_c[i] = d_a[i] + d_b[i]', nocopy ? '5. (skipped) cudaMemcpy device to host' : '5. cudaMemcpy device to host: copy d_c into c', '6. cudaFree: give the GPU memory back'];
      W(z, 'HOST (CPU memory)', 16, 22, { b: true, c: z.col.orange }); W(z, 'DEVICE (GPU memory)', 330, 22, { b: true, c: z.col.green });
      const cw = Math.min(17, 270 / n);
      const row = (x, y, lab, vals, show, col) => {
        W(z, lab, x, y + 12, { s: 11, mono: true });
        for (let i = 0; i < n; i++) {
          D.rect(g, x + 36 + i * cw, y, cw - 1, 16, { fill: show ? col : z.col.bg, stroke: z.col.line, w: 1 });
          if (show && cw >= 15) W(z, String(vals[i]), x + 36 + i * cw + cw / 2, y + 12, { s: 7.5, a: 'center', c: '#fff', mono: true });
        }
      };
      row(16, 40, 'a', a, true, z.col.orange); row(16, 64, 'b', bb, true, z.col.orange); row(16, 88, 'c', c, s >= 5 && !nocopy, z.col.purple);
      if (s >= 1 && s < 6) { row(330, 40, 'd_a', a, s >= 2, z.col.green); row(330, 64, 'd_b', bb, s >= 2, z.col.green); row(330, 88, 'd_c', c, s >= 4, z.col.green); }
      if (s >= 6) { D.rect(g, 326, 34, 290, 76, { fill: z.col.surf }); W(z, 'freed', 440, 76, { s: 13, c: z.col.ink2 }); }
      if (s === 2) D.arrow(g, 300, 60, 340, 60, z.col.orange);
      if (s === 5 && !nocopy) D.arrow(g, 340, 96, 300, 96, z.col.purple);
      if (s >= 3) {
        const nb = cdiv(n, b), tw = Math.min(30, 560 / (nb * b + nb));
        let x = 16;
        for (let k = 0; k < nb; k++) {
          D.rect(g, x - 2, 128, b * tw + 4, 34, { stroke: z.col.cv, w: 1.5 });
          W(z, `block ${k}`, x, 176, { s: 10, c: z.col.ink2 });
          for (let t = 0; t < b; t++) {
            const i = k * b + t, idle = i >= n;
            D.rect(g, x + t * tw, 132, tw - 2, 26, { fill: idle ? z.col.bg : (s >= 4 ? z.col.green : z.col.yellow) });
            if (tw >= 18) W(z, String(i), x + t * tw + (tw - 2) / 2, 149, { s: 9, a: 'center', mono: true, c: idle ? z.col.ink2 : '#111' });
          }
          x += b * tw + tw;
        }
      }
      names.slice(0, s).forEach((l, i) => W(z, l, 16, 200 + i * 12, { s: 10.5, c: i === s - 1 ? z.col.cv : z.col.ink2, b: i === s - 1 }));
      return s < 6 ? 'Grey thread boxes are idle threads: their index is not below N, so the guard if (i &lt; n) stops them.' :
        (nocopy ? '<span class="bad">The host array c is still empty.</span> The GPU result lives only in d_c until you copy it back, and after cudaFree it is gone.' : '<span class="ok">Done.</span> Host array c holds a[i] + b[i]. Every CUDA program follows these six steps, or uses unified memory to hide steps 2 and 5.');
    }
  });

  def('launch1d', {
    title: 'Which element does each thread handle?', sub: 'i = blockIdx.x × blockDim.x + threadIdx.x. Pick a block and a thread, or let it step through every block.',
    W: 620, H: 230,
    params: [
      { k: 'n', label: 'Elements N', v: 20, min: 1, max: 64, step: 1 },
      { k: 'b', label: 'blockDim.x (threads per block)', v: 8, min: 1, max: 32, step: 1 },
      { k: 'stride', label: 'Grid stride loop with a fixed number of blocks', type: 'check', v: false },
      { k: 'g', label: 'Blocks in the grid (stride mode)', v: 2, min: 1, max: 8, step: 1, show: p => p.stride },
      { k: 'bx', label: 'Look at blockIdx.x', v: 1, min: 0, max: 63, step: 1 },
      { k: 'tx', label: 'Look at threadIdx.x', v: 3, min: 0, max: 31, step: 1 }
    ],
    tips: [
      { t: 'N = 20, blocks of 8: ⌈20 ÷ 8⌉ = 3 blocks, 24 threads, 4 idle.', set: { n: 20, b: 8, stride: false, bx: 1, tx: 3 }, play: true },
      { t: 'Workbook P2.1.5: two blocks of 4. Which thread handles element 5? Block 1, thread 1.', set: { n: 8, b: 4, stride: false, bx: 1, tx: 1 } },
      { t: 'Grid stride loop: only 2 blocks of 8 (16 threads) cover 40 elements. Thread 3 of block 0 handles 3, 19 and 35.', set: { n: 40, b: 8, stride: true, g: 2, bx: 0, tx: 3 }, play: true }
    ],
    steps: z => z.p.stride ? cdiv(z.p.n, z.p.g * z.p.b) : cdiv(z.p.n, z.p.b),
    draw(z) {
      const { n, b, stride } = z.p, g = z.g;
      const nb = stride ? z.p.g : cdiv(n, b), total = nb * b;
      const bx = Math.min(z.p.bx, nb - 1), tx = Math.min(z.p.tx, b - 1), me = bx * b + tx;
      const cw = Math.min(26, 580 / Math.max(n, stride ? n : total));
      W(z, 'Data array (element number)', 16, 18, { s: 11, b: true });
      for (let i = 0; i < Math.max(n, stride ? n : total); i++) {
        const x = 16 + i * cw, owner = stride ? (i % total) : i, blk = Math.floor(owner / b);
        const pass = stride ? Math.floor(i / total) : blk;
        const lit = pass < z.step;
        const mine = stride ? (i % total === me) : i === me;
        D.rect(g, x, 26, cw - 2, 26, { fill: i >= n ? z.col.bg : lit ? [z.col.green, z.col.cv, z.col.purple, z.col.orange][blk % 4] : z.col.surf, stroke: mine && i < n ? z.col.red : z.col.line, w: mine && i < n ? 2.5 : 1 });
        if (cw >= 16 && i < n) W(z, String(i), x + (cw - 2) / 2, 43, { s: 9, a: 'center', mono: true, c: lit ? '#fff' : z.col.ink2 });
      }
      W(z, `Threads: ${nb} blocks × ${b} = ${total}`, 16, 80, { s: 11, b: true });
      const tw = Math.min(26, 580 / (total + nb));
      let x = 16;
      for (let k = 0; k < nb; k++) {
        for (let t = 0; t < b; t++) {
          const gi = k * b + t, idle = !stride && gi >= n;
          D.rect(g, x + t * tw, 90, tw - 2, 22, { fill: idle ? z.col.bg : [z.col.green, z.col.cv, z.col.purple, z.col.orange][k % 4], stroke: (k === bx && t === tx) ? z.col.red : 'transparent', w: 2.5 });
          if (tw >= 16) W(z, String(t), x + t * tw + (tw - 2) / 2, 105, { s: 9, a: 'center', mono: true, c: idle ? z.col.ink2 : '#fff' });
        }
        if (b * tw > 40) W(z, `block ${k}`, x, 126, { s: 10, c: z.col.ink2 });
        x += b * tw + tw;
      }
      const lines = [`blockIdx.x = ${bx}, blockDim.x = ${b}, threadIdx.x = ${tx}`, `i = ${bx} × ${b} + ${tx} = ${me}`];
      if (stride) { const own = []; for (let i = me; i < n; i += total) own.push(i); lines.push(`stride = gridDim.x × blockDim.x = ${total}. This thread handles ${own.join(', ') || 'nothing'}`); }
      else lines.push(me < n ? `Element ${me} is in range, so the thread works.` : `${me} ≥ N = ${n}: the guard if (i < n) stops this idle thread.`);
      lines.forEach((l, i) => W(z, l, 16, 160 + i * 20, { s: 12, mono: true, c: i === 1 ? z.col.red : z.col.ink }));
      return stride ? `A grid stride loop launches a fixed grid and lets each thread jump ahead by the total number of threads: <code>for (int i = idx; i &lt; n; i += blockDim.x * gridDim.x)</code>.` :
        `Blocks needed = ⌈N ÷ B⌉ = (${n} + ${b} − 1) ÷ ${b} = ${nb}. Idle threads = ${nb} × ${b} − ${n} = ${total - n}. Going back: element e lives in block ⌊e ÷ B⌋, thread e − block × B.`;
    }
  });

  def('index2d', {
    title: 'A 2-D grid of 2-D blocks over an image', sub: 'Click any pixel. The panel shows its blockIdx, threadIdx, row, column and position in memory.',
    W: 620, H: 300,
    params: [
      { k: 'w', label: 'Image width', v: 20, min: 2, max: 40, step: 1 },
      { k: 'h', label: 'Image height', v: 12, min: 2, max: 24, step: 1 },
      { k: 'bx', label: 'blockDim.x', v: 8, min: 1, max: 16, step: 1 },
      { k: 'by', label: 'blockDim.y', v: 4, min: 1, max: 16, step: 1 },
      { k: 'col', label: 'Pixel column (or click)', v: 12, min: 0, max: 47, step: 1 },
      { k: 'row', label: 'Pixel row (or click)', v: 5, min: 0, max: 31, step: 1 }
    ],
    tips: [
      { t: '20 × 12 image with 8 × 4 blocks: a 3 × 3 grid, and the last column of blocks hangs over the right edge (grey idle threads).', set: { w: 20, h: 12, bx: 8, by: 4, col: 12, row: 5 } },
      { t: 'Square 16 × 16 style blocks shrunk to 4 × 4: more blocks, each covers a little square.', set: { w: 16, h: 12, bx: 4, by: 4, col: 6, row: 9 } },
      { t: 'Wide blocks 16 × 2: a whole warp of 32 threads covers 2 rows of 16 pixels, neighbours in memory.', set: { w: 32, h: 8, bx: 16, by: 2, col: 20, row: 3 } }
    ],
    click(z, x, y, kind) {
      const { w, h } = z.p, cs = Math.min(300 / (Math.ceil(w / z.p.bx) * z.p.bx), 260 / (Math.ceil(h / z.p.by) * z.p.by));
      const c = Math.floor((x - 16) / cs), r = Math.floor((y - 20) / cs);
      if (c >= 0 && r >= 0 && c < w && r < h) z.set({ col: c, row: r });
    },
    draw(z) {
      const { w, h, bx, by } = z.p, g = z.g;
      const gx = cdiv(w, bx), gy = cdiv(h, by), cs = Math.min(300 / (gx * bx), 260 / (gy * by));
      const col = Math.min(z.p.col, w - 1), row = Math.min(z.p.row, h - 1);
      for (let r = 0; r < gy * by; r++) for (let c = 0; c < gx * bx; c++) {
        const inside = r < h && c < w, blk = Math.floor(r / by) * gx + Math.floor(c / bx);
        const sameBlk = Math.floor(r / by) === Math.floor(row / by) && Math.floor(c / bx) === Math.floor(col / bx);
        g.fillStyle = !inside ? z.col.bg : sameBlk ? 'rgba(118,185,0,0.45)' : (blk % 2 ? 'rgba(14,116,144,0.18)' : 'rgba(124,58,237,0.16)');
        g.fillRect(16 + c * cs, 20 + r * cs, cs - 1, cs - 1);
      }
      for (let k = 0; k <= gx; k++) D.line(g, 16 + k * bx * cs, 20, 16 + k * bx * cs, 20 + gy * by * cs, z.col.ink, 1.5);
      for (let k = 0; k <= gy; k++) D.line(g, 16, 20 + k * by * cs, 16 + gx * bx * cs, 20 + k * by * cs, z.col.ink, 1.5);
      D.rect(g, 16 + col * cs, 20 + row * cs, cs - 1, cs - 1, { fill: z.col.red });
      const bX = Math.floor(col / bx), bY = Math.floor(row / by), tX = col - bX * bx, tY = row - bY * by;
      const L = [`grid ${gx} × ${gy} blocks`, `blockIdx = (${bX}, ${bY})`, `threadIdx = (${tX}, ${tY})`,
        `col = ${bX}·${bx} + ${tX} = ${col}`, `row = ${bY}·${by} + ${tY} = ${row}`, `memory = row·width + col`, `       = ${row}·${w} + ${col} = ${row * w + col}`,
        `thread number in block`, `  = tx + ty·Bx = ${tX + tY * bx}`, `warp ${Math.floor((tX + tY * bx) / 32)}, lane ${(tX + tY * bx) % 32}`];
      L.forEach((l, i) => W(z, l, 340, 34 + i * 23, { s: 12.5, mono: true, c: i === 6 ? z.col.red : z.col.ink }));
      const idle = gx * bx * gy * by - w * h;
      return `Grid = (⌈${w} ÷ ${bx}⌉, ⌈${h} ÷ ${by}⌉) = (${gx}, ${gy}). Threads launched ${gx * bx * gy * by}, pixels ${w * h}, idle threads ${idle} (grey). The kernel must check <code>if (col &lt; width &amp;&amp; row &lt; height)</code>.`;
    }
  });

  def('warps', {
    title: 'Cutting a block into warps of 32', sub: 'The hardware groups threads 0 to 31, 32 to 63 and so on into warps. A part full warp still occupies 32 lanes.',
    W: 620, H: 260,
    params: [
      { k: 'bx', label: 'blockDim.x', v: 100, min: 1, max: 256, step: 1 },
      { k: 'by', label: 'blockDim.y', v: 1, min: 1, max: 16, step: 1 },
      { k: 't', label: 'Look at thread number t', v: 70, min: 0, max: 1023, step: 1 }
    ],
    tips: [
      { t: 'Workbook worked example: a block of 100 threads makes 4 warps with 28 empty lanes (78 percent used). Thread 70 is lane 6 of warp 2.', set: { bx: 100, by: 1, t: 70 } },
      { t: 'A 16 × 16 block: each warp is two rows of 16. Thread (x 5, y 3) is t = 53, warp 1, lane 21.', set: { bx: 16, by: 16, t: 53 } },
      { t: 'A block of 48: 2 warps, 16 empty lanes, 75 percent. Prefer multiples of 32.', set: { bx: 48, by: 1, t: 40 } }
    ],
    draw(z) {
      const { bx, by } = z.p, g = z.g, B = bx * by, nw = cdiv(B, 32), t = Math.min(z.p.t, B - 1);
      const rows = Math.min(nw, 16), cs = Math.min(17, 540 / 32), ch = Math.min(14, 200 / rows);
      for (let w = 0; w < rows; w++) {
        W(z, `warp ${w}`, 16, 30 + w * ch + ch * 0.7, { s: Math.min(11, ch), mono: true });
        for (let l = 0; l < 32; l++) {
          const id = w * 32 + l, used = id < B;
          D.rect(g, 70 + l * cs, 30 + w * ch, cs - 1, ch - 1, { fill: !used ? z.col.bg : id === t ? z.col.red : (Math.floor(id / bx) % 2 ? z.col.cv : z.col.green), stroke: used ? null : z.col.line });
        }
      }
      if (nw > rows) W(z, `… ${nw - rows} more warps`, 70, 30 + rows * ch + 12, { s: 11, c: z.col.ink2 });
      const eff = B / (32 * nw);
      return `Block of ${bx} × ${by} = ${B} threads → warps = ⌈${B} ÷ 32⌉ = <b>${nw}</b>, empty lanes = ${32 * nw - B}, lane efficiency = ${fmt(100 * eff)} percent.<br>
        Thread t = ${t}${by > 1 ? ` (x ${t % bx}, y ${Math.floor(t / bx)}, so t = x + y × ${bx})` : ''} sits in <b>warp ⌊${t} ÷ 32⌋ = ${Math.floor(t / 32)}, lane ${t % 32}</b> (red). Colours change with each row of the block, so you see how 2-D blocks are cut row by row.`;
    }
  });

  def('littles', {
    title: "Little's law: how much work must be in flight", sub: 'Each tick the SM can start a few operations, and each one takes L ticks to finish. Step through the ticks.',
    W: 620, H: 260,
    params: [
      { k: 'lat', label: 'Latency L (ticks)', v: 8, min: 1, max: 24, step: 1 },
      { k: 'thr', label: 'Operations the SM can start per tick (in warps)', v: 1, min: 1, max: 4, step: 1 },
      { k: 'warps', label: 'Warps the SM has ready', v: 4, min: 1, max: 48, step: 1 }
    ],
    tips: [
      { t: 'L = 8 and only 4 warps: after 4 ticks every warp is waiting and the SM sits idle half the time.', set: { lat: 8, thr: 1, warps: 4 }, play: true },
      { t: 'Give it 8 warps (= L × throughput): there is always a ready warp, no idle ticks.', set: { lat: 8, thr: 1, warps: 8 }, play: true },
      { t: 'Two issues per tick needs twice as many warps in flight: 16.', set: { lat: 8, thr: 2, warps: 16 }, play: true }
    ],
    steps: () => 24,
    draw(z) {
      const { lat, thr, warps } = z.p, g = z.g;
      const ready = new Array(warps).fill(0), cw = 22, ROWS = Math.min(warps, 16);
      let idle = 0, issued = 0;
      const grid = [];
      for (let t = 0; t < z.step; t++) {
        let k = 0; const row = [];
        for (let w = 0; w < warps && k < thr; w++) if (ready[w] <= t) { ready[w] = t + lat; row.push(w); k++; issued++; }
        if (k < thr) idle += thr - k;
        grid.push(row);
      }
      W(z, 'tick →', 16, 18, { s: 10, c: z.col.ink2 });
      for (let w = 0; w < ROWS; w++) {
        W(z, `w${w}`, 16, 40 + w * 12, { s: 9, mono: true });
        for (let t = 0; t < 24; t++) {
          let st = 0;
          for (let q = 0; q < Math.min(t + 1, z.step); q++) if (grid[q] && grid[q].includes(w)) { if (q === t) st = 2; else if (t < q + lat) st = Math.max(st, 1); }
          D.rect(g, 50 + t * cw, 31 + w * 12, cw - 2, 10, { fill: t >= z.step ? z.col.surf : st === 2 ? z.col.green : st === 1 ? z.col.orange : z.col.bg });
        }
      }
      const need = lat * thr;
      return `Green = the warp issues an operation, orange = it waits L = ${lat} ticks for the result. Issued ${issued} of ${z.step * thr} possible slots, <b>${idle} idle slots</b>.<br>
        Little's law: work in flight = latency × throughput = ${lat} × ${thr} = <b>${need} warps</b> needed to keep the SM busy. You have ${warps}${warps >= need ? ', enough' : ', too few'}.${warps > 16 ? ' (Only the first 16 warps are drawn.)' : ''}`;
    }
  });

  const GPUS = { a100: ['A100 (CC 8.0)', 2048, 64, 32, 65536, 167936, 255], cc86: ['RTX 30xx (CC 8.6)', 1536, 48, 16, 65536, 102400, 255], t4: ['T4 (CC 7.5)', 1024, 32, 16, 65536, 65536, 255], fermi: ['Fermi (CC 2.0)', 1536, 48, 8, 32768, 49152, 63] };
  def('occupancy', {
    title: 'Occupancy calculator: four limits, the smallest wins', sub: 'Step through the thread, block, register and shared memory limits of one SM.',
    W: 620, H: 260,
    params: [
      { k: 'gpu', label: 'GPU', type: 'select', v: 'a100', opts: Object.entries(GPUS).map(([k, v]) => [k, v[0]]) },
      { k: 'b', label: 'Threads per block', v: 256, min: 32, max: 1024, step: 32 },
      { k: 'r', label: 'Registers per thread', v: 32, min: 8, max: 255, step: 1 },
      { k: 's', label: 'Shared memory per block (bytes)', v: 2048, min: 0, max: 100000, step: 256 }
    ],
    tips: [
      { t: 'A100, 256 threads, 40 registers: the register limit gives 6 blocks, 75 percent (workbook 7.5).', set: { gpu: 'a100', b: 256, r: 40, s: 0 }, play: true },
      { t: 'CC 8.6, 256 threads, 32 registers, 2 KB shared: 6 blocks, 100 percent (the occupancy calculator screenshot).', set: { gpu: 'cc86', b: 256, r: 32, s: 2048 }, play: true },
      { t: 'Same, 32 KB of shared memory per block: only 3 blocks fit, 50 percent.', set: { gpu: 'cc86', b: 256, r: 32, s: 32768 }, play: true },
      { t: 'Tiny 32 thread blocks on CC 8.6: the block limit (16) gives only 33 percent.', set: { gpu: 'cc86', b: 32, r: 32, s: 0 }, play: true }
    ],
    steps: () => 5,
    draw(z) {
      const [name, maxT, maxW, maxB, regs, smem, maxR] = GPUS[z.p.gpu], { b, r, s } = z.p, g = z.g;
      const wpb = cdiv(b, 32), rpw = Math.ceil(r * 32 / 256) * 256;
      const lw = Math.floor(maxW / wpb), lb = maxB, lr = r > maxR ? 0 : Math.floor(Math.floor(regs / rpw) / wpb);
      const ls = s ? Math.floor(smem / (s + (z.p.gpu === 'fermi' || z.p.gpu === 't4' ? 0 : 1024))) : Infinity;
      const lims = [['warps', lw, `⌊${maxW} ÷ ${wpb} warps per block⌋`], ['blocks', lb, `max ${maxB} blocks per SM`], ['registers', lr, `⌊⌊${regs} ÷ ${rpw}⌋ ÷ ${wpb}⌋ (${r} regs × 32, rounded up to 256 = ${rpw} per warp)`], ['shared memory', ls, s ? `⌊${smem} ÷ (${s} + ${z.p.gpu === 'fermi' || z.p.gpu === 't4' ? 0 : 1024} reserved)⌋` : 'no shared memory used']];
      const shown = lims.slice(0, Math.min(4, z.step)), best = Math.min(...lims.map(x => x[1]));
      const mx = Math.max(...lims.filter(x => isFinite(x[1])).map(x => x[1]), 1);
      shown.forEach(([lab, v, why], i) => {
        const y = 22 + i * 46;
        W(z, lab, 16, y + 14, { b: true, s: 12 });
        const len = isFinite(v) ? 300 * v / mx : 300;
        D.rect(g, 130, y, Math.max(2, len), 20, { fill: z.step >= 5 && v === best ? z.col.red : z.col.cv });
        W(z, isFinite(v) ? `${v} blocks` : 'no limit', 136 + Math.min(len, 300), y + 14, { s: 11 });
        W(z, why, 130, y + 34, { s: 10, c: z.col.ink2, mono: true });
      });
      const occ = best * wpb / maxW;
      if (z.step >= 5) W(z, `Blocks = ${best}, warps = ${best * wpb} of ${maxW}, occupancy ${fmt(100 * Math.min(1, occ))} percent`, 16, 222, { b: true, s: 13, c: z.col.red });
      return `${name}: ${maxT} threads, ${maxW} warps, ${maxB} blocks, ${regs} registers and ${smem} bytes of shared memory per SM. ` +
        (z.step >= 5 ? `The smallest limit (red) decides. Occupancy = active warps ÷ max warps = ${best * wpb} ÷ ${maxW}.` : 'Press Step to add each limit.');
    }
  });
})();

/* ---------- 3.x memory: where variables live, coalescing into 32 byte sectors, shared memory banks ---------- */
(() => {
  const { def, D } = CVZ, { cdiv, fmt, W } = CUDAZ;
  const gcd = (a, b) => b ? gcd(b, a % b) : a;
  const MEMS = {
    reg: ['int i = threadIdx.x;', 'register', 'one thread', 'the thread', 'about 1 tick', 'Registers sit inside the SM next to the cores. Each thread has its own.'],
    local: ['float big[100]; (indexed by a variable)', 'local memory (DRAM, cached in L1 and L2)', 'one thread', 'the thread', 'hundreds of ticks on a miss', 'Big per thread arrays and spilled registers go to local memory. Local means private, not near.'],
    shared: ['__shared__ float tile[256];', 'shared memory (on the SM)', 'all threads of one block', 'the block', 'about 20 to 30 ticks', 'Each block gets its own copy. Threads of other blocks cannot see it.'],
    global: ['cudaMalloc(&d_a, bytes);', 'global memory (device DRAM)', 'every thread of every kernel, and the host through cudaMemcpy', 'until cudaFree or program exit', 'about 400 to 800 ticks', 'The only memory every SM can read and write for the whole application (Quiz 1 question 8).'],
    constant: ['__constant__ float w[9];', 'constant memory (DRAM, with a constant cache per SM)', 'every thread, read only', 'the whole application', 'fast when the whole warp reads the same address', 'The host fills it with cudaMemcpyToSymbol. One fetch is broadcast to all 32 lanes.']
  };
  def('memhier', {
    title: 'Where does a variable live?', sub: 'Pick a declaration and step: where it is stored, who can see it, how long it lives, and how fast it is.',
    W: 620, H: 280,
    params: [{ k: 'm', label: 'Declaration', type: 'select', v: 'shared', opts: Object.entries(MEMS).map(([k, v]) => [k, v[0]]) }],
    tips: [
      { t: 'A plain local variable lives in a register: private, gone when the thread ends, the fastest.', set: { m: 'reg' }, play: true },
      { t: 'A __shared__ array: one copy per block, seen by all its threads, on the SM.', set: { m: 'shared' }, play: true },
      { t: 'Memory from cudaMalloc is global: every SM sees it and it survives across kernel launches.', set: { m: 'global' }, play: true },
      { t: 'A big private array can end up in local memory, which really lives in slow DRAM.', set: { m: 'local' }, play: true }
    ],
    steps: () => 4,
    draw(z) {
      const g = z.g, m = z.p.m, M = MEMS[m], s = z.step;
      const hi = (key) => s >= 1 && (key === m || (m === 'constant' && key === 'const') || (m === 'local' && key === 'localD'));
      for (let k = 0; k < 2; k++) {
        const x = 16 + k * 210;
        D.rect(g, x, 20, 196, 120, { stroke: z.col.line });
        W(z, `SM ${k}`, x + 8, 36, { b: true, s: 12 });
        for (let b = 0; b < 2; b++) {
          const bx = x + 8 + b * 94;
          const seen = s >= 2 && (m === 'global' || m === 'constant' || (m === 'shared' && k === 0 && b === 0) || ((m === 'reg' || m === 'local') && k === 0 && b === 0));
          D.rect(g, bx, 44, 86, 50, { stroke: seen ? z.col.green : z.col.line, w: seen ? 2.5 : 1 });
          W(z, `block ${k * 2 + b}`, bx + 6, 58, { s: 10, c: z.col.ink2 });
          for (let t = 0; t < 4; t++) {
            const one = (m === 'reg' || m === 'local') && k === 0 && b === 0 && t === 0;
            D.rect(g, bx + 6 + t * 19, 64, 15, 12, { fill: hi('reg') && one ? z.col.red : (s >= 2 && seen && !(m === 'reg' || m === 'local') ? z.col.green : (s >= 2 && one ? z.col.green : z.col.bg)) });
          }
          W(z, 'registers', bx + 6, 88, { s: 9, c: z.col.ink2 });
        }
        D.rect(g, x + 8, 102, 180, 30, { fill: hi('shared') && k === 0 ? z.col.red : z.col.surf, stroke: z.col.line });
        W(z, 'shared memory / L1', x + 16, 122, { s: 11, c: hi('shared') && k === 0 ? '#fff' : z.col.ink });
      }
      D.rect(g, 16, 150, 406, 26, { fill: z.col.surf, stroke: z.col.line });
      W(z, 'L2 cache (shared by all SMs)', 26, 168, { s: 11 });
      const dram = [['global', 'global'], ['localD', 'local'], ['const', 'constant']];
      dram.forEach(([key, lab], i) => {
        const x = 16 + i * 137;
        D.rect(g, x, 186, 132, 32, { fill: hi(key) ? z.col.red : z.col.bg, stroke: z.col.line });
        W(z, lab, x + 10, 207, { s: 11, c: hi(key) ? '#fff' : z.col.ink });
      });
      W(z, 'device DRAM (GBs)', 16, 234, { s: 10, c: z.col.ink2 });
      D.rect(g, 440, 186, 164, 32, { fill: z.col.bg, stroke: z.col.line });
      W(z, 'host RAM (over PCIe)', 450, 207, { s: 11 });
      const lines = [`Stored in: ${M[1]}`, `Seen by: ${M[2]}`, `Lives for: ${M[3]}`, `Speed: ${M[4]}`];
      ['1 where', '2 who', '3 how long', '4 how fast'].forEach((l, i) => W(z, l, 440, 40 + i * 30, { s: 12, b: i === s - 1, c: i < s ? z.col.cv : z.col.ink2 }));
      return `<code>${M[0]}</code><br>` + (s === 0 ? 'Press Step.' : lines.slice(0, s).join('<br>') + '<br>' + M[5] + (s >= 2 ? ' Green boxes show who can see it.' : ''));
    }
  });

  def('coalesce', {
    title: 'Coalescing: how many 32 byte sectors does one warp read touch?', sub: 'Thread t reads element offset + t × stride. Step to add one thread at a time and watch the sectors fill.',
    W: 620, H: 300,
    params: [
      { k: 's', label: 'Stride (elements)', v: 1, min: 1, max: 32, step: 1 },
      { k: 'e', label: 'Element size', type: 'select', v: '4', opts: [['4', 'float (4 bytes)'], ['8', 'double (8 bytes)']] },
      { k: 'o', label: 'Start offset (bytes)', v: 0, min: 0, max: 64, step: 4 }
    ],
    tips: [
      { t: 'Stride 1 floats: 32 × 4 = 128 bytes in exactly 4 sectors, 100 percent useful (workbook 7.2).', set: { s: 1, e: '4', o: 0 }, play: true },
      { t: 'Stride 2: every other float, 8 sectors, half of every sector is wasted.', set: { s: 2, e: '4', o: 0 }, play: true },
      { t: 'Stride 32 (walking down a column): 32 sectors for 128 useful bytes, 12.5 percent.', set: { s: 32, e: '4', o: 0 }, play: true },
      { t: 'Stride 1 but starting 16 bytes into a sector: 5 sectors, 80 percent (misalignment).', set: { s: 1, e: '4', o: 16 }, play: true }
    ],
    steps: () => 32,
    draw(z) {
      const g = z.g, s = z.p.s, e = +z.p.e, o = z.p.o, n = z.step;
      const addr = t => o + t * s * e;
      const last = addr(31) + e, nsec = cdiv(last, 32), per = nsec <= 16 ? 16 : 32, cw = 544 / per, ch = nsec <= 16 ? 26 : Math.min(14, 150 / cdiv(nsec, per));
      const hit = new Map();
      for (let t = 0; t < n; t++) { const a = addr(t); for (let b = a; b < a + e; b += 4) { const sct = Math.floor(b / 32); hit.set(sct, (hit.get(sct) || 0) + 4); } }
      W(z, 'memory, one box = one 32 byte sector (8 floats)', 16, 16, { s: 10, c: z.col.ink2 });
      for (let k = 0; k < nsec; k++) {
        const r = Math.floor(k / per), c = k % per, h = hit.get(k) || 0;
        D.rect(g, 16 + c * cw, 24 + r * ch, cw - 2, ch - 2, { fill: h ? (h === 32 ? z.col.green : z.col.orange) : z.col.bg, stroke: z.col.line, w: 0.5 });
      }
      const ty = 24 + cdiv(nsec, per) * ch + 22;
      W(z, 'warp lanes', 16, ty - 6, { s: 10, c: z.col.ink2 });
      for (let t = 0; t < 32; t++) {
        D.rect(g, 16 + t * 17, ty, 15, 14, { fill: t < n ? z.col.cv : z.col.bg, stroke: z.col.line, w: 0.5 });
        if (t === n - 1) {
          const sct = Math.floor(addr(t) / 32), r = Math.floor(sct / per), c = sct % per;
          D.arrow(g, 16 + t * 17 + 7, ty, 16 + c * cw + cw / 2 - 1, 24 + r * ch + ch - 2, z.col.red, 1.5, 6);
        }
      }
      const used = n * e, sec = hit.size, eff = sec ? used / (sec * 32) : 0;
      W(z, `${n} threads read ${used} useful bytes from ${sec} sectors (${sec * 32} bytes moved)`, 16, ty + 40, { s: 12, b: true });
      W(z, `efficiency = useful ÷ moved = ${fmt(100 * eff)} percent`, 16, ty + 60, { s: 12, c: eff >= 0.99 ? z.col.green : z.col.red });
      const bw = e === 4 && o === 0 ? ` Sector model on a T4: about 206 ÷ min(${s}, 8) = ${fmt(206 / Math.min(s, 8))} GB/s of useful bandwidth (workbook 11.1).` : '';
      return `Green = every byte of the sector is used, orange = part used, so the rest of the 32 bytes is wasted traffic. A warp's loads are combined (coalesced) into as few sectors as possible.${bw}`;
    }
  });

  def('banks', {
    title: 'Shared memory banks: who has to wait?', sub: 'Shared memory is split into 32 banks, each 4 bytes wide. Word w lives in bank w mod 32. Two different words in one bank must take turns.',
    W: 620, H: 300,
    params: [
      { k: 'mode', label: 'Access pattern', type: 'select', v: 'stride', opts: [['stride', 'thread t reads word s × t'], ['col', 'thread t reads tile[t][0] (a column)'], ['same', 'all threads read word 5']] },
      { k: 's', label: 'Stride s (words)', v: 1, min: 1, max: 64, step: 1 },
      { k: 'w', label: 'Row width of the tile (words)', v: 32, min: 16, max: 64, step: 1 }
    ],
    tips: [
      { t: 'Stride 1: thread t hits bank t, no conflict, one pass.', set: { mode: 'stride', s: 1 }, play: true },
      { t: 'Stride 2: threads 0 and 16 both land on bank 0, a 2-way conflict = gcd(2, 32).', set: { mode: 'stride', s: 2 }, play: true },
      { t: 'Reading a column of a 32 wide tile: every thread hits bank 0, a 32-way conflict (workbook 11.2).', set: { mode: 'col', w: 32 }, play: true },
      { t: 'Pad the row to 33 words: the column now spreads over all 32 banks, conflict free.', set: { mode: 'col', w: 33 }, play: true },
      { t: 'All threads read the same word: the value is broadcast, no conflict.', set: { mode: 'same' }, play: true }
    ],
    steps: () => 32,
    draw(z) {
      const g = z.g, { mode, s, w } = z.p, n = z.step;
      const word = t => mode === 'stride' ? s * t : mode === 'col' ? t * w : 5;
      const stack = Array.from({ length: 32 }, () => []);
      for (let t = 0; t < n; t++) { const wd = word(t), b = wd % 32; stack[b].push([t, wd]); }
      const cw = 18;
      W(z, 'bank', 16, 22, { s: 10, c: z.col.ink2 });
      for (let b = 0; b < 32; b++) {
        if (b % 4 === 0) W(z, String(b), 50 + b * cw, 22, { s: 9, mono: true, c: z.col.ink2 });
        D.rect(g, 50 + b * cw, 28, cw - 2, 4, { fill: z.col.cv });
        const distinct = [];
        stack[b].forEach(([t, wd], i) => {
          let k = distinct.indexOf(wd); if (k < 0) { distinct.push(wd); k = distinct.length - 1; }
          if (k < 14) D.rect(g, 50 + b * cw, 36 + k * 13, cw - 2, 11, { fill: k === 0 ? z.col.green : z.col.red });
        });
      }
      let worst = 0; stack.forEach(st => { worst = Math.max(worst, new Set(st.map(q => q[1])).size); });
      W(z, 'rows down = passes (each red box waits one more pass)', 50, 232, { s: 10, c: z.col.ink2 });
      W(z, `${n} threads placed, worst bank holds ${worst} different word${worst === 1 ? '' : 's'}`, 50, 256, { s: 12, b: true });
      W(z, worst <= 1 ? 'conflict free: 1 pass' : `${worst}-way conflict: ${worst} passes`, 50, 278, { s: 12, b: true, c: worst <= 1 ? z.col.green : z.col.red });
      const why = mode === 'stride' ? `For stride s the conflict is gcd(s, 32) = gcd(${s}, 32) = ${gcd(s, 32)}.` : mode === 'col' ? `Element [t][0] is word t × ${w}, bank (t × ${w}) mod 32. ${w % 32 === 0 ? 'Width a multiple of 32 puts every row start in the same bank.' : gcd(w, 32) === 1 ? 'An odd width spreads the column over every bank.' : `gcd(${w}, 32) = ${gcd(w, 32)}, so ${gcd(w, 32)} threads share each bank.`}` : 'Every thread reads one word, the hardware broadcasts it.';
      return `Thread t (step ${n}) reads word ${n ? word(n - 1) : '-'}, bank ${n ? word(n - 1) % 32 : '-'}. ${why}`;
    }
  });
})();

/* ---------- 4.x numbers and limits: IEEE-754 encoding and the roofline ---------- */
(() => {
  const { def, D } = CVZ, { fmt, W } = CUDAZ;
  const FORMATS = { fp32: ['float (FP32)', 8, 23], fp16: ['half (FP16)', 5, 10], bf16: ['bfloat16 (BF16)', 8, 7] };
  const rne = x => { const f = Math.floor(x), d = x - f; return d > 0.5 || (d === 0.5 && f % 2) ? f + 1 : f; };
  const encode = (v, E, M) => {
    const bias = 2 ** (E - 1) - 1, sign = v < 0 || Object.is(v, -0) ? 1 : 0, a = Math.abs(v);
    if (a === 0) return { sign, e: 0, be: 0, mi: 0, stored: 0, bias, zero: true };
    let e = Math.floor(Math.log2(a));
    if (2 ** e > a) e--; if (2 ** (e + 1) <= a) e++;
    let mi = rne((a / 2 ** e - 1) * 2 ** M);
    if (mi === 2 ** M) { mi = 0; e++; }
    const be = e + bias, over = be >= 2 ** E - 1, under = be <= 0;
    const stored = (sign ? -1 : 1) * (1 + mi / 2 ** M) * 2 ** e;
    return { sign, e, be, mi, stored, bias, over, under };
  };
  const bin = (a, fracBits) => {
    let ip = Math.floor(a), fp = a - ip, s = ip.toString(2) + '.', k = 0;
    while (k < fracBits && fp > 0) { fp *= 2; s += fp >= 1 ? '1' : '0'; if (fp >= 1) fp -= 1; k++; }
    if (k === 0) s += '0';
    return s + (fp > 0 ? '…' : '');
  };
  def('ieee', {
    title: 'How a decimal number is stored in IEEE-754', sub: 'Type a number and step: sign, binary, slide the point, biased exponent, mantissa bits, and what is really stored.',
    W: 620, H: 280,
    params: [
      { k: 'v', label: 'Number (type any decimal)', v: 6.75, type: 'text', num: true },
      { k: 'f', label: 'Format', type: 'select', v: 'fp32', opts: Object.entries(FORMATS).map(([k, x]) => [k, x[0]]) }
    ],
    tips: [
      { t: 'Workbook 5.1: 6.75 = 110.11 in binary = 1.1011 × 2², stored exponent 2 + 127 = 129.', set: { v: 6.75, f: 'fp32' }, play: true },
      { t: '−0.375 = −1.1 × 2⁻². Sign 1, exponent 125, the word is 0xBEC00000.', set: { v: -0.375, f: 'fp32' }, play: true },
      { t: '5.6 has an endless binary fraction, so a float stores 5.599999904632568 instead.', set: { v: 5.6, f: 'fp32' }, play: true },
      { t: 'The same 5.6 in FP16 keeps only 10 mantissa bits: 5.6015625.', set: { v: 5.6, f: 'fp16' }, play: true },
      { t: 'BF16 keeps FP32\'s 8 exponent bits but only 7 mantissa bits: 5.59375.', set: { v: 5.6, f: 'bf16' }, play: true }
    ],
    steps: () => 6,
    draw(z) {
      const g = z.g, [name, E, M] = FORMATS[z.p.f], v = +z.p.v || 0, r = encode(v, E, M), s = z.step;
      const lines = [
        ['1 sign', `${v < 0 ? 'negative' : 'positive'}, sign bit = ${r.sign}`],
        ['2 binary', `|${fmt(Math.abs(v))}| = ${bin(Math.abs(v), 16)}`],
        ['3 slide the point', r.zero ? 'zero has its own pattern (all bits 0)' : `1.${r.mi.toString(2).padStart(M, '0').replace(/0+$/, '') || '0'} × 2^${r.e}`],
        ['4 biased exponent', r.zero ? 'exponent bits all 0' : `${r.e} + ${r.bias} = ${r.be}${r.over ? ' (too big: overflow to infinity)' : r.under ? ' (too small: subnormal or zero)' : ''}`],
        ['5 mantissa', `keep ${M} bits after the point, round to nearest even`],
        ['6 stored value', r.over ? 'infinity' : `${r.stored}` + (r.stored === v ? ' (exact)' : `  error ${(r.stored - v).toExponential(2)}`)]];
      lines.slice(0, s).forEach(([a, b], i) => {
        W(z, a, 16, 26 + i * 24, { s: 12, b: true, c: i === s - 1 ? z.col.cv : z.col.ink2 });
        W(z, b, 150, 26 + i * 24, { s: 12, mono: true });
      });
      const bits = r.sign.toString() + (r.zero ? '0'.repeat(E) : Math.max(0, Math.min(2 ** E - 1, r.be)).toString(2).padStart(E, '0')) + (r.zero ? '0'.repeat(M) : r.mi.toString(2).padStart(M, '0'));
      const n = 1 + E + M, bw = Math.min(17, 588 / n);
      for (let i = 0; i < n; i++) {
        const part = i === 0 ? 0 : i <= E ? 1 : 2, show = (part === 0 && s >= 1) || (part === 1 && s >= 4) || (part === 2 && s >= 5);
        D.rect(g, 16 + i * bw, 186, bw - 1, 24, { fill: !show ? z.col.bg : part === 0 ? z.col.red : part === 1 ? z.col.orange : z.col.cv });
        if (show) W(z, bits[i], 16 + i * bw + (bw - 1) / 2, 203, { s: 11, a: 'center', mono: true, c: '#fff' });
      }
      W(z, `sign 1 bit`, 16, 226, { s: 10, c: z.col.red }); W(z, `exponent ${E} bits`, 16 + bw, 240, { s: 10, c: z.col.orange }); W(z, `mantissa ${M} bits`, 16 + (E + 1) * bw, 226, { s: 10, c: z.col.cv });
      let hex = '';
      if (n % 4 === 0) for (let i = 0; i < n; i += 4) hex += parseInt(bits.slice(i, i + 4), 2).toString(16).toUpperCase();
      if (s >= 6 && hex) W(z, `hex 0x${hex}`, 16, 268, { s: 12, mono: true, b: true });
      return `${name}: value = (−1)<sup>sign</sup> × 1.mantissa × 2<sup>exponent − ${r.bias}</sup>. ${s >= 6 ? (r.stored === v ? 'This number fits exactly.' : 'This number does not fit exactly, so the nearest representable value is stored.') : 'Press Step.'}`;
    }
  });

  const GPU = { fermi: ['Fermi (1000 GFLOP/s, 144 GB/s)', 1000, 144], t4: ['T4 FP32 (8100 GFLOP/s, 320 GB/s)', 8100, 320], a100: ['A100 FP32 (19,500 GFLOP/s, 1555 GB/s)', 19500, 1555], h100: ['H100 PCIe FP32 (51,000 GFLOP/s, 2000 GB/s)', 51000, 2000] };
  def('roofline', {
    title: 'The roofline: is a kernel limited by maths or by memory?', sub: 'Pick a GPU and a kernel\'s arithmetic intensity (FLOPs per byte moved). Step to draw the two roofs, the ridge and the kernel.',
    W: 620, H: 300,
    params: [
      { k: 'gpu', label: 'GPU', type: 'select', v: 'a100', opts: Object.entries(GPU).map(([k, x]) => [k, x[0]]) },
      { k: 'ai', label: 'Arithmetic intensity (FLOP per byte)', v: 0.25, min: 0.05, max: 128, step: 0.01 }
    ],
    tips: [
      { t: 'Plain matrix multiply (AI 0.25) on an A100: 0.25 × 1555 = 389 GFLOP/s, 50 times below the peak (workbook 5.4).', set: { gpu: 'a100', ai: 0.25 }, play: true },
      { t: 'SAXPY (AI 1/6) on Fermi: 24 GFLOP/s. Memory bound, more cores would not help.', set: { gpu: 'fermi', ai: 0.1667 }, play: true },
      { t: 'Tiling with T = 16 gives AI = 4 on Fermi: still left of the ridge at 6.94.', set: { gpu: 'fermi', ai: 4 }, play: true },
      { t: 'AI = 20 on the A100 passes the ridge at 12.5: now the maths units are the limit.', set: { gpu: 'a100', ai: 20 }, play: true }
    ],
    steps: () => 4,
    draw(z) {
      const g = z.g, [name, P, B] = GPU[z.p.gpu], ai = z.p.ai, s = z.step, ridge = P / B;
      const x0 = 70, y0 = 250, w = 360, h = 220, lx0 = Math.log10(1 / 32), lx1 = Math.log10(256);
      const ly1 = Math.log10(P * 2), ly0 = ly1 - 4;
      const X = a => x0 + (Math.log10(a) - lx0) / (lx1 - lx0) * w, Y = p => y0 - (Math.log10(p) - ly0) / (ly1 - ly0) * h;
      D.line(g, x0, y0, x0 + w, y0, z.col.ink2); D.line(g, x0, y0, x0, y0 - h, z.col.ink2);
      [1 / 16, 1, 16, 256].forEach(a => W(z, a < 1 ? '1/16' : String(a), X(a), y0 + 14, { s: 10, a: 'center', c: z.col.ink2 }));
      W(z, 'FLOP per byte (log)', x0 + w / 2, y0 + 28, { s: 10, a: 'center', c: z.col.ink2 });
      for (let k = 0; k <= 4; k++) { const p = 10 ** (ly0 + k); W(z, p >= 1000 ? fmt(p / 1000) + ' T' : fmt(p) + ' G', x0 - 6, Y(p) + 4, { s: 9, a: 'right', c: z.col.ink2 }); }
      if (s >= 1) { const aL = 10 ** lx0; D.line(g, X(aL), Y(aL * B), X(Math.min(ridge, 256)), Y(Math.min(ridge, 256) * B), z.col.orange, 2.5); }
      if (s >= 2) D.line(g, X(Math.max(ridge, 10 ** lx0)), Y(P), x0 + w, Y(P), z.col.green, 2.5);
      if (s >= 3) { D.line(g, X(ridge), Y(P), X(ridge), y0, z.col.ink2, 1, [4, 4]); D.circle(g, X(ridge), Y(P), 4, { fill: z.col.ink }); }
      const att = Math.min(P, ai * B);
      if (s >= 4) { D.line(g, X(ai), y0, X(ai), Y(att), z.col.red, 1, [3, 3]); D.circle(g, X(ai), Y(att), 6, { fill: z.col.red }); }
      const info = [['memory roof', `AI × ${B} GB/s`, z.col.orange], ['compute roof', `${fmt(P)} GFLOP/s`, z.col.green], ['ridge', `${fmt(P)} ÷ ${B} = ${fmt(ridge)}`, z.col.ink], ['kernel', `${fmt(att)} GFLOP/s`, z.col.red]];
      info.slice(0, s).forEach(([a, b, c], i) => { W(z, a, 450, 40 + i * 44, { s: 12, b: true, c }); W(z, b, 450, 58 + i * 44, { s: 11, mono: true }); });
      return `${name}. Attainable = min(peak, AI × bandwidth) = min(${fmt(P)}, ${fmt(ai)} × ${B}) = <b>${fmt(att)} GFLOP/s</b>, ${fmt(100 * att / P)} percent of peak. ` +
        (ai < ridge ? `AI ${fmt(ai)} is left of the ridge ${fmt(ridge)}: <b>memory bound</b>. Only more bandwidth or more reuse (higher AI) helps.` : `AI is right of the ridge: <b>compute bound</b>. Faster maths (more cores, tensor cores, lower precision) helps.`);
    }
  });
})();
