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

/* ---------- 5.x parallel patterns: reduction, tiled matmul, stencil halo, convolution, scan ---------- */
(() => {
  const { def, D } = CVZ, { cdiv, fmt, W } = CUDAZ;
  const nums = (s, n) => { const a = String(s).split(/[\s,]+/).filter(x => x !== '').map(Number).filter(x => isFinite(x)); return a.slice(0, n); };
  const pow2 = n => { let p = 1; while (p < n) p *= 2; return p; };

  def('reduce', {
    title: 'Tree reduction: adding a block of numbers in log₂ n steps', sub: 'Each level, half of the remaining threads add a partner\'s value. Watch which threads work and how the warps split.',
    W: 620, H: 280,
    params: [
      { k: 'vals', label: 'Numbers (up to 32, padded with 0 to a power of two)', type: 'text', v: '3, 1, 4, 1, 5, 9, 2, 6' },
      { k: 'mode', label: 'Pairing', type: 'select', v: 'seq', opts: [['seq', 'sequential: thread t < s adds t + s (s halves)'], ['int', 'interleaved: t % 2s == 0 adds t + s (s doubles)']] },
      { k: 'ws', label: 'Warp size to draw (real GPUs use 32)', type: 'select', v: '4', opts: [['4', '4 lanes (small, to see splits)'], ['8', '8 lanes'], ['32', '32 lanes']] }
    ],
    tips: [
      { t: 'Workbook 10.2: [3, 1, 4, 1, 5, 9, 2, 6] gives 31 after 3 levels (step 4, then 2, then 1).', set: { vals: '3, 1, 4, 1, 5, 9, 2, 6', mode: 'seq' }, play: true },
      { t: 'Interleaved pairing: the working threads are spread out, so every warp stays split (divergent) at every level.', set: { vals: '3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3', mode: 'int', ws: '4' }, play: true },
      { t: 'Sequential pairing on 16 numbers: working threads are packed at the front, so whole warps go idle early and only the last levels split.', set: { vals: '3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3', mode: 'seq', ws: '4' }, play: true }
    ],
    steps: z => Math.log2(pow2(Math.max(2, nums(z.p.vals, 32).length))),
    draw(z) {
      const g = z.g, src = nums(z.p.vals, 32), n = pow2(Math.max(2, src.length)), ws = +z.p.ws, L = Math.log2(n);
      let a = src.concat(new Array(n - src.length).fill(0));
      const cw = Math.min(36, 588 / n), rh = Math.min(40, 230 / (L + 1));
      const rows = [a.slice()], act = [];
      for (let l = 0; l < L; l++) {
        const s = z.p.mode === 'seq' ? n >> (l + 1) : 1 << l, b = a.slice(), on = [];
        for (let t = 0; t < n; t++) {
          const work = z.p.mode === 'seq' ? t < s : t % (2 * s) === 0;
          if (work) { b[t] = a[t] + a[t + s]; on.push([t, t + s]); }
        }
        a = b; rows.push(a.slice()); act.push(on);
      }
      const show = Math.min(z.step, L);
      for (let r = 0; r <= show; r++) {
        const y = 14 + r * rh, on = r > 0 ? act[r - 1] : [], target = new Set(on.map(p => p[0]));
        if (r > 0) on.forEach(([t, u]) => { D.line(g, 16 + u * cw + cw / 2, y - rh + 22, 16 + t * cw + cw / 2, y, z.col.orange, 1); D.line(g, 16 + t * cw + cw / 2, y - rh + 22, 16 + t * cw + cw / 2, y, z.col.orange, 1); });
        for (let t = 0; t < n; t++) {
          D.rect(g, 16 + t * cw, y, cw - 2, 20, { fill: target.has(t) ? z.col.green : z.col.bg, stroke: z.col.line, w: 0.5 });
          if (cw >= 16) W(z, String(rows[r][t]), 16 + t * cw + (cw - 2) / 2, y + 14, { s: cw >= 24 ? 11 : 8, a: 'center', mono: true, c: target.has(t) ? '#fff' : z.col.ink });
        }
      }
      for (let w = 0; w < n / ws; w++) D.line(g, 16 + w * ws * cw - 1, 8, 16 + w * ws * cw - 1, 14 + (show + 1) * rh - rh + 22, z.col.cv, 1, [2, 3]);
      let msg = `n = ${n}: ${L} levels, ${n - 1} additions in total (one adder alone would need ${n - 1} steps).`;
      if (show > 0) {
        const on = act[show - 1].map(p => p[0]), warps = new Set(on.map(t => Math.floor(t / ws))), split = [...warps].filter(w => on.filter(t => Math.floor(t / ws) === w).length < ws).length;
        msg += `<br>Level ${show}: <b>${on.length} threads add</b>, they sit in ${warps.size} warp${warps.size === 1 ? '' : 's'} of ${ws} lanes, <b>${split} split</b> (some lanes idle).` + (show === L ? ` Result: <b>${rows[L][0]}</b>.` : '');
      }
      return msg + ' Dotted lines mark warp borders. There is a __syncthreads() between levels.';
    }
  });

  def('tilemm', {
    title: 'Tiled matrix multiply: one block, phase by phase', sub: 'Click a tile of C to choose the block. Each phase loads one T × T tile of A and one of B into shared memory.',
    W: 620, H: 300,
    params: [
      { k: 'n', label: 'Matrix size n', v: 8, min: 2, max: 16, step: 1 },
      { k: 'T', label: 'Tile size T', v: 4, min: 1, max: 8, step: 1 }
    ],
    tips: [
      { t: 'n = 8, T = 4: 2 phases. Each thread loads 2 × 2 = 4 values instead of 2 × 8 = 16.', set: { n: 8, T: 4 }, play: true },
      { t: 'Workbook 7.1: n = 5 with 4 × 4 tiles. 2 phases, 4 blocks, 64 threads, 39 idle, 100 reads instead of 250.', set: { n: 5, T: 4 }, play: true },
      { t: 'Slide 21: n = 4, T = 2. 4 blocks, 2 phases, 64 loads in total (= 2n³ ÷ T).', set: { n: 4, T: 2 }, play: true }
    ],
    init(z) { z.state.bi = 0; z.state.bj = 0; },
    click(z, x, y, kind) {
      if (kind !== 'down') return;
      const { n, T } = z.p, c = Math.min(26, 128 / n), x0 = 40 + n * c, y0 = 40 + n * c, nb = cdiv(n, T);
      const j = Math.floor((x - x0) / (c * T)), i = Math.floor((y - y0) / (c * T));
      if (i >= 0 && j >= 0 && i < nb && j < nb) { z.state.bi = i; z.state.bj = j; z.step = 0; }
    },
    steps: z => cdiv(z.p.n, z.p.T),
    draw(z) {
      const g = z.g, { n, T } = z.p, c = Math.min(26, 128 / n), nb = cdiv(n, T), ph = nb;
      const bi = Math.min(z.state.bi || 0, nb - 1), bj = Math.min(z.state.bj || 0, nb - 1), p = z.step - 1;
      const xA = 20, yA = 40 + n * c, xB = 40 + n * c, yB = 20, xC = xB, yC = yA;
      const grid = (x, y, lab, hl) => {
        for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) D.rect(g, x + j * c, y + i * c, c - 1, c - 1, { fill: hl(i, j) || z.col.bg });
        W(z, lab, x, y - 5, { s: 11, b: true });
      };
      grid(xA, yA, 'A', (i, j) => p >= 0 && Math.floor(i / T) === bi && Math.floor(j / T) === p ? z.col.orange : (Math.floor(i / T) === bi ? z.col.surf : null));
      grid(xB, yB, 'B', (i, j) => p >= 0 && Math.floor(i / T) === p && Math.floor(j / T) === bj ? z.col.purple : (Math.floor(j / T) === bj ? z.col.surf : null));
      grid(xC, yC, 'C', (i, j) => Math.floor(i / T) === bi && Math.floor(j / T) === bj ? (z.step >= ph ? z.col.green : z.col.yellow) : null);
      D.rect(g, xC + bj * T * c - 1, yC + bi * T * c - 1, Math.min(T, n - bj * T) * c + 1, Math.min(T, n - bi * T) * c + 1, { stroke: z.col.red, w: 2 });
      const tx = 60 + 2 * n * c, threads = nb * nb * T * T;
      const lines = [`phases = ⌈${n} ÷ ${T}⌉ = ${ph}`, `blocks = ${nb} × ${nb} = ${nb * nb}`, `threads = ${threads}, idle ${threads - n * n}`,
        `loads per thread: ${2 * ph} (plain ${2 * n})`, `total reads: ${2 * n * n * ph} (plain ${2 * n ** 3})`];
      lines.forEach((l, i) => W(z, l, tx, 40 + i * 22, { s: 12, mono: true }));
      if (p >= 0) W(z, `phase ${p + 1}: A tile (${bi}, ${p}) and B tile (${p}, ${bj})`, tx, 170, { s: 12, b: true, c: z.col.cv });
      return `Block (${bi}, ${bj}) computes the red tile of C. In phase k its threads copy A tile (${bi}, k) (orange) and B tile (k, ${bj}) (purple) into shared memory, call __syncthreads(), add T = ${T} products each, and call __syncthreads() again before the next phase overwrites the tiles. Every value loaded is used T times, so global reads drop by a factor of T.`;
    }
  });

  def('stencil', {
    title: '1-D stencil with a halo in shared memory', sub: 'Each output adds the 2R + 1 inputs around it. A block loads its B inputs plus R extra on each side (the halo) once, then every thread reads from shared memory.',
    W: 620, H: 250,
    params: [
      { k: 'R', label: 'Radius R', v: 3, min: 1, max: 4, step: 1 },
      { k: 'B', label: 'Threads per block B', v: 8, min: 4, max: 16, step: 1 },
      { k: 't', label: 'Show the inputs of thread', v: 0, min: 0, max: 15, step: 1 }
    ],
    tips: [
      { t: 'R = 3, B = 8: the tile holds 8 + 6 = 14 values. Without sharing, 8 outputs would read 8 × 7 = 56 values.', set: { R: 3, B: 8, t: 0 }, play: true },
      { t: 'Thread 0 needs the 3 halo values on the left, loaded by the extra step.', set: { R: 3, B: 8, t: 0 }, play: true },
      { t: 'Workbook 6.4: R = 3, B = 256 gives 262 values, 1.023 reads per output instead of 7.', set: { R: 3, B: 16, t: 5 }, play: true }
    ],
    steps: () => 4,
    draw(z) {
      const g = z.g, { R, B } = z.p, t = Math.min(z.p.t, B - 1), s = z.step, cw = Math.min(30, 560 / (B + 2 * R));
      const x0 = 16;
      W(z, 'global input', x0, 24, { s: 11, c: z.col.ink2 });
      for (let i = -R; i < B + R; i++) {
        const halo = i < 0 || i >= B;
        D.rect(g, x0 + (i + R) * cw, 30, cw - 2, 22, { fill: halo ? z.col.surf : z.col.bg, stroke: z.col.line, w: 0.5 });
        W(z, String(i), x0 + (i + R) * cw + (cw - 2) / 2, 45, { s: 9, a: 'center', mono: true, c: z.col.ink2 });
      }
      W(z, 'shared tile (B + 2R values)', x0, 92, { s: 11, c: z.col.ink2 });
      for (let i = -R; i < B + R; i++) {
        const halo = i < 0 || i >= B, loaded = (!halo && s >= 1) || (halo && s >= 2);
        D.rect(g, x0 + (i + R) * cw, 98, cw - 2, 22, { fill: loaded ? (halo ? z.col.orange : z.col.cv) : z.col.bg, stroke: z.col.line, w: 0.5 });
        if (loaded && s >= 1) D.line(g, x0 + (i + R) * cw + cw / 2 - 1, 52, x0 + (i + R) * cw + cw / 2 - 1, 98, halo ? z.col.orange : z.col.cv, 1);
      }
      if (s >= 3) { D.line(g, x0, 132, x0 + (B + 2 * R) * cw, 132, z.col.red, 2, [6, 4]); W(z, '__syncthreads()', x0, 148, { s: 11, c: z.col.red, mono: true }); }
      if (s >= 4) {
        for (let k = -R; k <= R; k++) D.arrow(g, x0 + (t + k + R) * cw + cw / 2 - 1, 122, x0 + (t + R) * cw + cw / 2 - 1, 190, z.col.green, 1.2, 5);
        D.rect(g, x0 + (t + R) * cw, 192, cw - 2, 22, { fill: z.col.green });
        W(z, `out[${t}]`, x0 + (t + R) * cw + (cw - 2) / 2, 232, { s: 10, a: 'center', mono: true });
      }
      const step = ['Press Step.', 'Step 1: thread i copies in[i] into tile[i + R].', `Step 2: the first R = ${R} threads also copy the ${R} values on each side (the halo, orange).`, 'Step 3: wait until the whole tile is loaded.', `Step 4: thread ${t} adds tile[${t}] to tile[${t + 2 * R}], all from shared memory.`][s];
      return `${step}<br>Values loaded per block = B + 2R = ${B + 2 * R}. Reads per output: ${fmt((B + 2 * R) / B)} with the tile against 2R + 1 = ${2 * R + 1} without it.`;
    }
  });

  const IMGS = { ramp: Array.from({ length: 5 }, (_, i) => Array.from({ length: 5 }, (_, j) => 5 * i + j + 1)), edge: Array.from({ length: 5 }, () => [0, 0, 255, 255, 255]), sharp: Array.from({ length: 5 }, (_, i) => Array.from({ length: 5 }, (_, j) => 5 * i + 10 * j + 10)) };
  const FILT = { diag: [[1, 0], [0, -1]], box2: [[1, 1], [1, 1]], sobelx: [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], sobely: [[-1, -2, -1], [0, 0, 0], [1, 2, 1]], sharpen: [[0, -1, 0], [-1, 5, -1], [0, -1, 0]] };
  def('conv2d', {
    title: '2-D convolution by hand: slide, multiply, add', sub: 'One GPU thread computes one output. Step to move the filter one place and see its multiply-adds.',
    W: 620, H: 280,
    params: [
      { k: 'img', label: 'Picture (5 × 5)', type: 'select', v: 'ramp', opts: [['ramp', 'numbers 1 to 25 row by row'], ['edge', 'dark left, bright right (an edge)'], ['sharp', 'a smooth slope (workbook R channel)']] },
      { k: 'f', label: 'Filter', type: 'select', v: 'diag', opts: [['diag', 'with rows (1, 0) and (0, −1)'], ['box2', 'box with rows (1, 1) and (1, 1)'], ['sobelx', 'Sobel Gx'], ['sobely', 'Sobel Gy'], ['sharpen', 'sharpen']] },
      { k: 'pad', label: 'Zero padding (keeps the size)', type: 'check', v: false }
    ],
    tips: [
      { t: 'Workbook 8.2: every output of the filter with rows (1, 0) and (0, −1) on 1 to 25 is −6, because the picture is a smooth slope.', set: { img: 'ramp', f: 'diag', pad: false }, play: true },
      { t: 'Box filter on 1 to 25: the first output is 1 + 2 + 6 + 7 = 16.', set: { img: 'ramp', f: 'box2', pad: false }, play: true },
      { t: 'Sobel Gx on an edge: large values where dark meets bright, 0 on flat parts.', set: { img: 'edge', f: 'sobelx', pad: false }, play: true },
      { t: 'Workbook 8.2: sharpen with zero padding. The middle 40 stays 40, the corner 10 becomes 15 and the corner 70 becomes 225, because the padding counts as 0.', set: { img: 'sharp', f: 'sharpen', pad: true }, play: true }
    ],
    steps: z => { const k = FILT[z.p.f].length, o = z.p.pad ? 5 : 6 - k; return o * o; },
    draw(z) {
      const g = z.g, F = FILT[z.p.f], k = F.length, r = Math.floor((k - 1) / 2), pad = z.p.pad ? r : 0, I = IMGS[z.p.img];
      const o = z.p.pad ? 5 : 6 - k, c = 36, x0 = 16, y0 = 24;
      const px = (i, j) => (i < 0 || j < 0 || i >= 5 || j >= 5) ? 0 : I[i][j];
      const out = []; for (let i = 0; i < o; i++) for (let j = 0; j < o; j++) { let s = 0; for (let a = 0; a < k; a++) for (let b = 0; b < k; b++) s += F[a][b] * px(i - pad + a, j - pad + b); out.push(s); }
      const cur = z.step - 1, ci = Math.floor(cur / o), cj = cur % o;
      W(z, 'input', x0, 16, { s: 11, c: z.col.ink2 });
      for (let i = 0; i < 5; i++) for (let j = 0; j < 5; j++) {
        const inWin = cur >= 0 && i >= ci - pad && i < ci - pad + k && j >= cj - pad && j < cj - pad + k;
        D.rect(g, x0 + j * c, y0 + i * c, c - 2, c - 2, { fill: inWin ? z.col.orange : z.col.bg, stroke: z.col.line, w: 0.5 });
        W(z, String(I[i][j]), x0 + j * c + c / 2 - 1, y0 + i * c + c / 2 + 4, { s: 11, a: 'center', mono: true, c: inWin ? '#fff' : z.col.ink });
      }
      if (cur >= 0 && pad) D.rect(g, x0 + (cj - pad) * c - 1, y0 + (ci - pad) * c - 1, k * c, k * c, { stroke: z.col.red, w: 2 });
      const fx = 220;
      W(z, 'filter', fx, 16, { s: 11, c: z.col.ink2 });
      for (let a = 0; a < k; a++) for (let b = 0; b < k; b++) { D.rect(g, fx + b * 28, y0 + a * 28, 26, 26, { fill: z.col.surf }); W(z, String(F[a][b]), fx + b * 28 + 13, y0 + a * 28 + 17, { s: 11, a: 'center', mono: true }); }
      const ox = 330, oc = Math.min(48, 190 / o);
      W(z, `output ${o} × ${o}`, ox, 16, { s: 11, c: z.col.ink2 });
      for (let q = 0; q < o * o; q++) {
        const i = Math.floor(q / o), j = q % o, done = q <= cur;
        D.rect(g, ox + j * oc, y0 + i * oc, oc - 2, oc - 2, { fill: q === cur ? z.col.green : z.col.bg, stroke: z.col.line, w: 0.5 });
        if (done) W(z, String(out[q]), ox + j * oc + oc / 2 - 1, y0 + i * oc + oc / 2 + 4, { s: oc >= 40 ? 11 : 9, a: 'center', mono: true, c: q === cur ? '#fff' : z.col.ink });
      }
      let terms = '';
      if (cur >= 0) { const t = []; for (let a = 0; a < k; a++) for (let b = 0; b < k; b++) if (F[a][b]) t.push(`${F[a][b]} × ${px(ci - pad + a, cj - pad + b)}`); terms = `Output (${ci}, ${cj}) = ${t.join(' + ')} = <b>${out[cur]}</b>.`; }
      return `Output size = ${z.p.pad ? `5 + 2 × ${r} − ${k} + 1 = 5 (same)` : `5 − ${k} + 1 = ${o}`}. ${k * k} multiply-adds per output, ${k * k * o * o} for the whole picture. ${terms || 'Press Step.'}`;
    }
  });

  def('scan', {
    title: 'Parallel prefix sum (scan)', sub: 'Every output is the sum of all inputs before it. Step through a parallel scan level by level.',
    W: 620, H: 290,
    params: [
      { k: 'vals', label: 'Numbers (up to 16, padded with 0 to a power of two)', type: 'text', v: '3, 1, 7, 0, 4, 1, 6, 3' },
      { k: 'mode', label: 'Algorithm', type: 'select', v: 'hs', opts: [['hs', 'Hillis and Steele (inclusive, n log n adds)'], ['bl', 'Blelloch (exclusive, up sweep then down sweep, 2n adds)']] }
    ],
    tips: [
      { t: 'Hillis and Steele: at level d every element adds the one 2ᵈ to its left. 3 levels for 8 numbers.', set: { vals: '3, 1, 7, 0, 4, 1, 6, 3', mode: 'hs' }, play: true },
      { t: 'Blelloch: build partial sums up a tree, clear the last one, then sweep down swapping and adding. Result is exclusive: 0, 3, 4, 11, 11, 15, 16, 22.', set: { vals: '3, 1, 7, 0, 4, 1, 6, 3', mode: 'bl' }, play: true }
    ],
    steps: z => { const n = pow2(Math.max(2, nums(z.p.vals, 16).length)), L = Math.log2(n); return z.p.mode === 'hs' ? L : 2 * L + 1; },
    draw(z) {
      const g = z.g, src = nums(z.p.vals, 16), n = pow2(Math.max(2, src.length)), L = Math.log2(n);
      let a = src.concat(new Array(n - src.length).fill(0));
      const rows = [[a.slice(), [], 'input']];
      if (z.p.mode === 'hs') {
        for (let d = 0; d < L; d++) { const s = 1 << d, b = a.slice(), ed = []; for (let i = s; i < n; i++) { b[i] = a[i] + a[i - s]; ed.push([i - s, i]); } a = b; rows.push([a.slice(), ed, `add the value ${s} to the left`]); }
      } else {
        for (let d = 0; d < L; d++) { const s = 1 << d, ed = []; for (let k = 0; k < n; k += 2 * s) { a[k + 2 * s - 1] += a[k + s - 1]; ed.push([k + s - 1, k + 2 * s - 1]); } rows.push([a.slice(), ed, `up sweep, stride ${s}`]); }
        a[n - 1] = 0; rows.push([a.slice(), [], 'clear the last value']);
        for (let d = L - 1; d >= 0; d--) { const s = 1 << d, ed = []; for (let k = 0; k < n; k += 2 * s) { const t = a[k + s - 1]; a[k + s - 1] = a[k + 2 * s - 1]; a[k + 2 * s - 1] += t; ed.push([k + s - 1, k + 2 * s - 1]); } rows.push([a.slice(), ed, `down sweep, stride ${s}`]); }
      }
      const cw = Math.min(30, 400 / n), rh = Math.min(36, 260 / rows.length), show = Math.min(z.step, rows.length - 1);
      for (let r = 0; r <= show; r++) {
        const [v, ed, lab] = rows[r], y = 10 + r * rh, hit = new Set(ed.map(e => e[1]));
        ed.forEach(([u, t]) => D.line(g, 16 + u * cw + cw / 2, y - rh + 20, 16 + t * cw + cw / 2, y, z.col.orange, 1));
        for (let i = 0; i < n; i++) {
          D.rect(g, 16 + i * cw, y, cw - 2, 20, { fill: hit.has(i) ? z.col.green : z.col.bg, stroke: z.col.line, w: 0.5 });
          W(z, String(v[i]), 16 + i * cw + (cw - 2) / 2, y + 14, { s: cw >= 26 ? 11 : 9, a: 'center', mono: true, c: hit.has(i) ? '#fff' : z.col.ink });
        }
        W(z, lab, 30 + n * cw, y + 14, { s: 10.5, c: r === show ? z.col.cv : z.col.ink2, b: r === show });
      }
      const adds = z.p.mode === 'hs' ? rows.slice(1).reduce((s, r) => s + r[1].length, 0) : 2 * (n - 1);
      return `${n} numbers. ${z.p.mode === 'hs' ? `Hillis and Steele does ${adds} additions in ${L} levels (more work than the ${n - 1} of a serial loop, but only ${L} steps).` : `Blelloch does about 2(n − 1) = ${adds} additions in ${2 * L} levels: work efficient.`} Scans are used for stream compaction, radix sort and allocating output space in parallel.`;
    }
  });
})();

/* ---------- 6.x execution: warp divergence, warp schedulers, streams ---------- */
(() => {
  const { def, D } = CVZ, { cdiv, fmt, W } = CUDAZ;
  const CONDS = {
    even: ['if (tid % 2 == 0) A else B', t => t % 2 === 0 ? 0 : 1, 2],
    q9: ['if (tid % 4 == 1) A else B (Quiz 1 Q9)', t => t % 4 === 1 ? 0 : 1, 2],
    lt: ['if (tid < K) A else B', null, 2],
    warp: ['if ((tid / 32) % 2 == 0) A else B', t => Math.floor(t / 32) % 2 === 0 ? 0 : 1, 2],
    sw4: ['switch (tid % 4): 4 cases', t => t % 4, 4]
  };
  def('diverge', {
    title: 'Warp divergence: when lanes of one warp take different paths', sub: 'A warp issues one instruction for all its lanes. If lanes disagree at a branch, the warp runs each path in turn and masks the lanes that did not take it.',
    W: 620, H: 280,
    params: [
      { k: 'c', label: 'Branch', type: 'select', v: 'q9', opts: Object.entries(CONDS).map(([k, x]) => [k, x[0]]) },
      { k: 'B', label: 'Threads in the block', v: 32, min: 32, max: 128, step: 32 },
      { k: 'K', label: 'K (for tid < K)', v: 40, min: 0, max: 128, step: 1 },
      { k: 'ta', label: 'Ticks for path A (case 0)', v: 10, min: 1, max: 40, step: 1 },
      { k: 'tb', label: 'Ticks for every other path', v: 10, min: 1, max: 40, step: 1 }
    ],
    tips: [
      { t: 'Quiz 1 Q9: lanes 1, 5, 9, …, 29 take branch A. Their ids add up to 120. The warp runs both branches.', set: { c: 'q9', B: 32, ta: 10, tb: 10 }, play: true },
      { t: 'Workbook 7.3: tid % 2 with 10 ticks each: 20 ticks instead of 10, efficiency 50 percent.', set: { c: 'even', B: 32, ta: 10, tb: 10 }, play: true },
      { t: 'Branch on the warp number: whole warps go the same way, no warp diverges.', set: { c: 'warp', B: 128, ta: 10, tb: 10 }, play: true },
      { t: 'if (tid < 40) in a 64 thread block: only warp 1 splits.', set: { c: 'lt', B: 64, K: 40, ta: 10, tb: 10 }, play: true },
      { t: 'A 4-way switch: 40 ticks, 25 percent.', set: { c: 'sw4', B: 32, ta: 10, tb: 10 }, play: true }
    ],
    steps: z => CONDS[z.p.c][2] + 2,
    draw(z) {
      const g = z.g, { c, B, K, ta, tb } = z.p, [lab, f0, np] = CONDS[c], f = f0 || (t => t < K ? 0 : 1);
      const cols = [z.col.green, z.col.orange, z.col.purple, z.col.cv], nw = B / 32, s = z.step;
      const len = p => p === 0 ? ta : tb;
      let tot = 0, maxT = 0;
      const warpT = [];
      for (let w = 0; w < nw; w++) {
        const used = new Set(); let lane = 0;
        for (let l = 0; l < 32; l++) { const p = f(w * 32 + l); used.add(p); lane += len(p); }
        const T = [...used].reduce((a, p) => a + len(p), 0);
        warpT.push([T, lane, [...used].sort()]); tot += T; maxT = Math.max(maxT, T);
      }
      for (let w = 0; w < nw; w++) {
        const y = 20 + w * 62;
        W(z, `warp ${w}`, 16, y + 12, { s: 11, mono: true });
        for (let l = 0; l < 32; l++) {
          const tid = w * 32 + l, p = f(tid), on = s >= 2 && s - 2 === p, shown = s >= 1;
          D.rect(g, 70 + l * 16, y, 14, 16, { fill: !shown ? z.col.bg : (s >= 2 && !on && s - 2 < np ? z.col.surf : cols[p]) });
        }
        const [T, lane, used] = warpT[w];
        let x = 70;
        used.forEach(p => { const wd = 400 * len(p) / Math.max(maxT, 1); if (s >= 2 + p) D.rect(g, x, y + 22, wd - 2, 12, { fill: cols[p] }); x += wd; });
        if (s > np + 1) W(z, `${T} ticks, ${fmt(100 * lane / (32 * T))} percent`, 480, y + 33, { s: 10.5, b: true });
      }
      const Q9 = c === 'q9' ? ` Sum of thread ids taking A: ${Array.from({ length: B }, (_, t) => t).filter(t => f(t) === 0).reduce((a, b) => a + b, 0)}.` : '';
      return `<code>${lab}</code>. ` + (s === 0 ? 'Press Step to colour each lane by its path.' : s <= np + 1 ? `Colours show the path of each lane. ${s >= 2 ? `Now running path ${np === 2 ? 'AB'[s - 2] : 'case ' + (s - 2)}: lanes on other paths are masked (pale).` : ''}` :
        `A warp takes the sum of the lengths of every path any of its lanes needs. Efficiency = useful lane ticks ÷ (32 × warp ticks).`) + Q9;
    }
  });

  const PROGS = { cccl: 'CCCL', cl: 'CL', ccccccl: 'CCCCCCCL' };
  def('sched', {
    title: 'Warp schedulers: round robin against greedy then oldest', sub: 'Each tick the scheduler issues one instruction from a ready warp. C takes 1 tick, a load L makes the warp wait. Step through the ticks.',
    W: 620, H: 260,
    params: [
      { k: 'pol', label: 'Policy', type: 'select', v: 'rr', opts: [['rr', 'round robin (RR)'], ['gto', 'greedy then oldest (GTO)'], ['two', 'two level (groups of 2, RR inside)']] },
      { k: 'nw', label: 'Warps', v: 4, min: 1, max: 6, step: 1 },
      { k: 'L', label: 'Load wait L (ticks)', v: 12, min: 2, max: 20, step: 1 },
      { k: 'prog', label: 'Each warp runs (3 times)', type: 'select', v: 'cccl', opts: [['cccl', 'C C C L'], ['cl', 'C L'], ['ccccccl', 'C C C C C C C L']] }
    ],
    tips: [
      { t: 'Workbook 7.4, RR: all four warps reach their load together and wait together: 75 ticks, 16 idle.', set: { pol: 'rr', nw: 4, L: 12, prog: 'cccl' }, play: true },
      { t: 'GTO: warp 0 runs ahead to its load, then warp 1 and so on. Loads are spread out: 59 ticks, 0 idle, the best possible.', set: { pol: 'gto', nw: 4, L: 12, prog: 'cccl' }, play: true },
      { t: 'Two level: 63 ticks, 4 idle, in between.', set: { pol: 'two', nw: 4, L: 12, prog: 'cccl' }, play: true },
      { t: 'GTO with only 3 warps: 6 idle ticks remain (workbook P7.4.5).', set: { pol: 'gto', nw: 3, L: 12, prog: 'cccl' }, play: true }
    ],
    init(z) { z.state.sim = null; },
    sim(z) {
      const { pol, nw, L } = z.p, prog = PROGS[z.p.prog].repeat(3), pc = new Array(nw).fill(0), ready = new Array(nw).fill(0), tl = [];
      let t = 0, last = -1, idle = 0, lastLoad = 0, grp = 0;
      while (pc.some(p => p < prog.length) && t < 400) {
        const cand = []; for (let w = 0; w < nw; w++) if (pc[w] < prog.length && ready[w] <= t) cand.push(w);
        let pick = -1;
        const rr = set => { for (let k = 1; k <= nw; k++) { const w = (last + k + nw) % nw; if (set.includes(w)) return w; } return -1; };
        if (cand.length) {
          if (pol === 'rr') pick = rr(cand);
          else if (pol === 'gto') pick = cand.includes(last) ? last : Math.min(...cand);
          else { const ng = cdiv(nw, 2); for (let q = 0; q < ng; q++) { const gI = (grp + q) % ng, c2 = cand.filter(w => Math.floor(w / 2) === gI); if (c2.length) { grp = gI; pick = rr(c2); break; } } }
        }
        if (pick < 0) { idle++; tl.push([-1, '']); }
        else { const ins = prog[pc[pick]++]; ready[pick] = ins === 'L' ? t + L : t + 1; if (ins === 'L') lastLoad = t; last = pick; tl.push([pick, ins]); }
        t++;
      }
      return { tl, idle, finish: lastLoad + L, total: nw * prog.length };
    },
    steps: z => { const r = z.spec.sim(z); return r.tl.length; },
    draw(z) {
      const g = z.g, r = z.spec.sim(z), n = r.tl.length, cw = Math.min(14, 560 / n), s = z.step, { nw, L } = z.p;
      W(z, 'tick →', 16, 16, { s: 10, c: z.col.ink2 });
      for (let w = 0; w < nw; w++) W(z, `W${w}`, 16, 40 + w * 22, { s: 11, mono: true });
      W(z, 'idle', 16, 40 + nw * 22, { s: 11, mono: true, c: z.col.red });
      for (let t = 0; t < Math.min(s, n); t++) {
        const [w, ins] = r.tl[t], x = 50 + t * cw;
        if (w < 0) D.rect(g, x, 28 + nw * 22, cw - 1, 16, { fill: z.col.red });
        else D.rect(g, x, 28 + w * 22, cw - 1, 16, { fill: ins === 'L' ? z.col.orange : z.col.green });
      }
      for (let t = 0; t <= n; t += 10) W(z, String(t), 50 + t * cw, 60 + nw * 22, { s: 9, a: 'center', c: z.col.ink2 });
      const done = s >= n;
      return `Green = a 1 tick instruction, orange = a load (the warp then waits L = ${L} ticks), red = no warp is ready. ` +
        (done ? `Finish = last load + L = <b>${r.finish}</b> ticks, <b>${r.idle} idle</b>. Best possible = (${r.total} instructions − 1) + ${L} = ${r.total - 1 + L}.` : `Tick ${s} of ${n}.`);
    }
  });

  def('streams', {
    title: 'CUDA streams: overlapping copies and kernels', sub: 'Split the data into chunks. While chunk 2 is copied in, chunk 1 can compute and chunk 0 can be copied out.',
    W: 620, H: 250,
    params: [
      { k: 'n', label: 'Chunks (streams in turn)', v: 4, min: 1, max: 16, step: 1 },
      { k: 'a', label: 'Copy in per chunk (ms)', v: 1, min: 0.5, max: 10, step: 0.5 },
      { k: 'k', label: 'Kernel per chunk (ms)', v: 1, min: 0.5, max: 10, step: 0.5 },
      { k: 'b', label: 'Copy out per chunk (ms)', v: 1, min: 0.5, max: 10, step: 0.5 },
      { k: 'eng', label: 'Copy engines', type: 'select', v: '2', opts: [['2', 'two (one each way)'], ['1', 'one shared']] }
    ],
    tips: [
      { t: 'Workbook 6.3: three equal stages and 4 chunks: 12 t serial, 6 t overlapped, 2 times faster.', set: { n: 4, a: 1, k: 1, b: 1, eng: '2' }, play: true },
      { t: '16 chunks: 48 t against 18 t, 2.67 times. The limit is 3 times, the number of stages.', set: { n: 16, a: 1, k: 1, b: 1, eng: '2' }, play: true },
      { t: 'Stages 2, 5 and 2 ms with 10 chunks: 90 ms against 54 ms. The kernel is the bottleneck.', set: { n: 10, a: 2, k: 5, b: 2, eng: '2' }, play: true },
      { t: 'With one copy engine the copies in and out cannot overlap each other.', set: { n: 4, a: 1, k: 1, b: 1, eng: '1' }, play: true }
    ],
    steps: z => z.p.n,
    draw(z) {
      const g = z.g, { n, a, k, b } = z.p, one = z.p.eng === '1', s = z.step;
      let h2d = 0, comp = 0, d2h = 0;
      const jobs = [];
      for (let i = 0; i < n; i++) {
        const s1 = one ? Math.max(h2d, d2h) : h2d, e1 = s1 + a; h2d = e1; if (one) d2h = Math.max(d2h, e1);
        const s2 = Math.max(e1, comp), e2 = s2 + k; comp = e2;
        const s3 = Math.max(e2, one ? h2d : d2h), e3 = s3 + b; d2h = e3; if (one) h2d = Math.max(h2d, e3);
        jobs.push([[s1, e1], [s2, e2], [s3, e3]]);
      }
      const total = Math.max(...jobs.map(j => j[2][1])), serial = n * (a + k + b), sc = 440 / Math.max(total, serial);
      const lanes = ['copy in', 'kernel', 'copy out'], cols = [z.col.orange, z.col.green, z.col.purple];
      W(z, 'serial (one stream)', 16, 20, { s: 11, b: true });
      D.rect(g, 100, 28, serial * sc, 14, { fill: z.col.surf, stroke: z.col.line });
      W(z, `${fmt(serial)} ms`, 106 + serial * sc, 40, { s: 10 });
      W(z, 'overlapped', 16, 70, { s: 11, b: true });
      lanes.forEach((l, r) => W(z, l, 16, 96 + r * 28, { s: 10.5, c: z.col.ink2 }));
      jobs.slice(0, s).forEach((j, i) => j.forEach(([x0, x1], r) => {
        D.rect(g, 100 + x0 * sc, 84 + r * 28, Math.max(1, (x1 - x0) * sc - 1), 18, { fill: cols[r] });
        if ((x1 - x0) * sc > 12) W(z, String(i), 100 + (x0 + x1) / 2 * sc, 97 + r * 28, { s: 9, a: 'center', c: '#fff', mono: true });
      }));
      if (s >= n) { D.line(g, 100 + total * sc, 78, 100 + total * sc, 170, z.col.red, 1.5, [4, 3]); W(z, `${fmt(total)} ms`, 100 + total * sc + 4, 186, { s: 11, b: true, c: z.col.red }); }
      return `Serial = N × (in + kernel + out) = ${n} × ${fmt(a + k + b)} = ${fmt(serial)} ms.` + (s >= n ? ` Overlapped = <b>${fmt(total)} ms</b>, speedup <b>${fmt(serial / total)}</b>. With equal stages t this is (N + 2) t, so the speedup approaches the number of stages.` : ' Press Step to issue each chunk into its stream.');
    }
  });
})();

/* ---------- 7.x synchronisation: lost updates, lock algorithms step by step ---------- */
(() => {
  const { def, D } = CVZ, { fmt, W } = CUDAZ;
  const rng = seed => () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  def('counter', {
    title: 'counter = counter + 1 is three steps: load, add, store', sub: 'Several threads add 1 to one counter. Step through one micro step at a time and watch updates get lost.',
    W: 620, H: 280,
    params: [
      { k: 'n', label: 'Threads', v: 2, min: 2, max: 8, step: 1 },
      { k: 'mode', label: 'How they run', type: 'select', v: 'bad', opts: [['bad', 'the bad order from the lecture'], ['lock', 'lock step, like one warp (all load, all add, all store)'], ['rand', 'a random order (pick a seed)'], ['serial', 'one after another'], ['atomic', 'atomicAdd (load, add, store as one step)']] },
      { k: 'seed', label: 'Seed for the random order', v: 7, min: 1, max: 50, step: 1 }
    ],
    tips: [
      { t: 'Lecture 10 table: both threads load 0, both store 1. The counter ends at 1 instead of 2.', set: { n: 2, mode: 'bad' }, play: true },
      { t: 'Workbook 10.1: 10 threads of one warp in lock step all load 0, so the result is 1 and 9 updates are lost (8 threads shown here).', set: { n: 8, mode: 'lock' }, play: true },
      { t: 'Try different seeds: with 3 threads the result can be 1, 2 or 3, only about 0.4 percent of orders give 3.', set: { n: 3, mode: 'rand', seed: 11 }, play: true },
      { t: 'atomicAdd makes the three steps indivisible: always correct.', set: { n: 8, mode: 'atomic' }, play: true }
    ],
    order(z) {
      const { n, mode } = z.p, ops = [];
      if (mode === 'atomic') { for (let t = 0; t < n; t++) ops.push([t, 'A']); return ops; }
      if (mode === 'serial') { for (let t = 0; t < n; t++) ['L', '+', 'S'].forEach(o => ops.push([t, o])); return ops; }
      if (mode === 'lock') { ['L', '+', 'S'].forEach(o => { for (let t = 0; t < n; t++) ops.push([t, o]); }); return ops; }
      if (mode === 'bad') { ops.push([0, 'L'], [1, 'L'], [0, '+'], [1, '+'], [0, 'S'], [1, 'S']); for (let t = 2; t < n; t++) ['L', '+', 'S'].forEach(o => ops.push([t, o])); return ops; }
      const r = rng(z.p.seed * 97 + n), left = new Array(n).fill(0);
      for (let k = 0; k < 3 * n; k++) { const can = []; for (let t = 0; t < n; t++) if (left[t] < 3) can.push(t); const t = can[Math.floor(r() * can.length)]; ops.push([t, 'L+S'[left[t]]]); left[t]++; }
      return ops;
    },
    steps: z => z.spec.order(z).length,
    draw(z) {
      const g = z.g, n = z.p.n, ops = z.spec.order(z), s = z.step, reg = new Array(n).fill(null);
      let mem = 0;
      const hist = [];
      for (let k = 0; k < s; k++) {
        const [t, o] = ops[k];
        if (o === 'L') reg[t] = mem; else if (o === '+') reg[t] += 1; else if (o === 'S') mem = reg[t]; else { mem += 1; reg[t] = mem; }
        hist.push([t, o, mem]);
      }
      const cw = Math.min(30, 440 / ops.length);
      W(z, 'step →', 70, 16, { s: 10, c: z.col.ink2 });
      for (let t = 0; t < n; t++) {
        W(z, `T${t}`, 16, 38 + t * 22, { s: 11, mono: true });
        W(z, reg[t] === null ? 'r = -' : `r = ${reg[t]}`, 520, 38 + t * 22, { s: 11, mono: true, c: z.col.ink2 });
      }
      hist.forEach(([t, o], k) => {
        const col = o === 'L' ? z.col.cv : o === '+' ? z.col.orange : o === 'S' ? z.col.purple : z.col.green;
        D.rect(g, 70 + k * cw, 26 + t * 22, cw - 2, 18, { fill: col });
        if (cw >= 14) W(z, o === 'A' ? 'a' : o, 70 + k * cw + (cw - 2) / 2, 39 + t * 22, { s: 10, a: 'center', c: '#fff', mono: true, b: true });
      });
      const y = 40 + n * 22;
      W(z, 'memory', 16, y + 12, { s: 11, b: true });
      hist.forEach(([, , m], k) => { if (cw >= 14) W(z, String(m), 70 + k * cw + (cw - 2) / 2, y + 12, { s: 10, a: 'center', mono: true }); });
      W(z, `counter = ${mem}`, 16, y + 44, { s: 15, b: true, c: s >= ops.length ? (mem === n ? z.col.green : z.col.red) : z.col.ink });
      return `L = load into a register, + = add 1 in the register, S = store back, a = atomicAdd. ` + (s >= ops.length ? (mem === n ? `<span class="ok">Correct: ${n}.</span>` : `<span class="bad">Expected ${n}, got ${mem}: ${n - mem} update${n - mem === 1 ? '' : 's'} lost.</span> A thread stored a value computed from an old load.`) : `Step ${s} of ${ops.length}.`);
    }
  });

  const ALGOS = {
    v1: { name: 'Dekker attempt 1: take turns', vars: { turn: 0 }, code: i => [['wait while turn == ' + (1 - i), (st, me) => st.turn === 1 - me], ['critical section', null], ['turn = ' + (1 - i), (st, me) => { st.turn = 1 - me; }]] },
    v2: { name: 'Dekker attempt 2: check, then set', vars: { f0: 0, f1: 0 }, code: i => [[`wait while flag${1 - i}`, (st, me) => !!st['f' + (1 - me)]], [`flag${i} = true`, (st, me) => { st['f' + me] = 1; }], ['critical section', null], [`flag${i} = false`, (st, me) => { st['f' + me] = 0; }]] },
    v3: { name: 'Dekker attempt 3: set, then check', vars: { f0: 0, f1: 0 }, code: i => [[`flag${i} = true`, (st, me) => { st['f' + me] = 1; }], [`wait while flag${1 - i}`, (st, me) => !!st['f' + (1 - me)]], ['critical section', null], [`flag${i} = false`, (st, me) => { st['f' + me] = 0; }]] },
    pet: { name: 'Peterson', vars: { f0: 0, f1: 0, turn: 0 }, code: i => [[`flag${i} = true`, (st, me) => { st['f' + me] = 1; }], [`turn = ${1 - i}`, (st, me) => { st.turn = 1 - me; }], [`wait while flag${1 - i} and turn == ${1 - i}`, (st, me) => !!st['f' + (1 - me)] && st.turn === 1 - me], ['critical section', null], [`flag${i} = false`, (st, me) => { st['f' + me] = 0; }]] }
  };
  def('locks', {
    title: 'Two threads, one critical section: step through lock attempts', sub: 'Pick an algorithm and a schedule (which thread takes the next step). Watch for both threads inside at once, or both waiting for ever.',
    W: 620, H: 300,
    params: [
      { k: 'alg', label: 'Algorithm', type: 'select', v: 'v2', opts: Object.entries(ALGOS).map(([k, a]) => [k, a.name]) },
      { k: 'sch', label: 'Schedule (0 and 1 = which thread steps next)', type: 'text', v: '0101010101010101' },
      { k: 'want', label: 'Thread 1 wants the critical section', type: 'check', v: true },
      { k: 'rounds', label: 'Times each thread enters', v: 1, min: 1, max: 3, step: 1 }
    ],
    tips: [
      { t: 'Attempt 2 with 0101…: both check the other flag before either sets its own, so both enter. Mutual exclusion is broken (not a deadlock as slide 8 says).', set: { alg: 'v2', sch: '0101010101010101', want: true, rounds: 1 }, play: true },
      { t: 'Attempt 3 with 0101…: both raise their flags, then each waits for the other for ever. Deadlock.', set: { alg: 'v3', sch: '0101010101010101', want: true, rounds: 1 }, play: true },
      { t: 'Attempt 1 when thread 1 does not want in: thread 0 enters once, hands the turn over, then waits for ever. No progress.', set: { alg: 'v1', sch: '0000000000', want: false, rounds: 2 }, play: true },
      { t: 'Peterson with the same tricky schedule: one thread waits, the other enters, then they swap. All three rules hold.', set: { alg: 'pet', sch: '010101010101010101010101', want: true, rounds: 2 }, play: true }
    ],
    steps: z => String(z.p.sch).replace(/[^01]/g, '').length,
    draw(z) {
      const g = z.g, A = ALGOS[z.p.alg], sch = String(z.p.sch).replace(/[^01]/g, ''), st = Object.assign({}, A.vars), code = [A.code(0), A.code(1)];
      const pc = [0, 0], done = [0, 0], spins = [0, 0], need = [z.p.rounds, z.p.want ? z.p.rounds : 0];
      let both = false, last = '';
      for (let k = 0; k < Math.min(z.step, sch.length); k++) {
        const me = +sch[k];
        if (done[me] >= need[me]) { last = `T${me} has nothing to do`; continue; }
        const [txt, fn] = code[me][pc[me]];
        if (txt.startsWith('wait')) { if (fn(st, me)) { spins[me]++; last = `T${me} spins: ${txt}`; continue; } spins[me] = 0; pc[me]++; last = `T${me} passes the gate`; }
        else if (fn) { fn(st, me); pc[me]++; last = `T${me}: ${txt}`; }
        else { pc[me]++; last = `T${me} works in the critical section`; }
        if (pc[me] >= code[me].length) { pc[me] = 0; done[me]++; }
        const csIdx = code[0].findIndex(c => c[1] === null);
        if (pc[0] === csIdx && pc[1] === csIdx && done[0] < need[0] && done[1] < need[1]) both = true;
      }
      const csIdx = code[0].findIndex(c => c[1] === null);
      [0, 1].forEach(me => {
        const x = 16 + me * 300;
        W(z, `Thread ${me}${me === 1 && !z.p.want ? ' (not interested)' : ''}`, x, 20, { s: 12, b: true });
        code[me].forEach(([txt], i) => {
          const at = pc[me] === i && done[me] < need[me], cs = i === csIdx;
          D.rect(g, x, 30 + i * 30, 280, 24, { fill: at ? (cs ? z.col.red : z.col.cv) : (cs ? z.col.surf : z.col.bg), stroke: z.col.line, w: 0.5 });
          W(z, txt, x + 8, 47 + i * 30, { s: 11, mono: true, c: at ? '#fff' : z.col.ink });
        });
        W(z, done[me] >= need[me] ? 'finished' : `entered ${done[me]} of ${need[me]}`, x, 30 + code[me].length * 30 + 16, { s: 11, c: z.col.ink2 });
      });
      W(z, 'shared: ' + Object.entries(st).map(([k, v]) => `${k.replace(/^f/, 'flag')} = ${v}`).join('   '), 16, 230, { s: 12, mono: true, b: true });
      const waiting = [0, 1].every(me => done[me] < need[me] && code[me][pc[me]][0].startsWith('wait') && code[me][pc[me]][1](st, me));
      const stuck0 = done[0] < need[0] && code[0][pc[0]][0].startsWith('wait') && code[0][pc[0]][1](st, 0) && done[1] >= need[1];
      W(z, both ? 'BOTH threads are in the critical section' : waiting ? 'DEADLOCK: each waits for the other for ever' : stuck0 ? 'NO PROGRESS: thread 0 waits for a thread that never comes' : (done[0] >= need[0] && done[1] >= need[1] ? 'Both finished safely' : last), 16, 262, { s: 13, b: true, c: both || waiting || stuck0 ? z.col.red : z.col.green });
      return `${A.name}. The filled line is the next step of that thread. It turns red when that step is the critical section. Edit the schedule to try other orders. Rules: mutual exclusion (never both inside), progress (no deadlock, nobody blocked by a thread that is not trying), bounded waiting.`;
    }
  });
})();

/* ---------- 7.2 barriers and atomics: barrier against lock timelines, privatised atomics, priority counter ---------- */
(() => {
  const { def, D } = CVZ, { fmt, W } = CUDAZ;
  const rng = seed => () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };

  def('syncbar', {
    title: 'Barrier or lock: who waits, and for how long', sub: 'Each thread first does some work of its own length. Then it either meets the others at a barrier, or takes a lock for its critical section.',
    W: 620, H: 300,
    params: [
      { k: 'n', label: 'Threads', v: 4, min: 2, max: 8, step: 1 },
      { k: 'mode', label: 'What happens after the work', type: 'select', v: 'barrier', opts: [['barrier', '__syncthreads(): everyone waits for the slowest'], ['cas', 'atomicCAS spin lock: a random waiter wins'], ['ticket', 'ticket lock: first come, first served']] },
      { k: 'cs', label: 'Length of the critical section', v: 2, min: 1, max: 3, step: 1 },
      { k: 'seed', label: 'Seed for the work lengths', v: 3, min: 1, max: 30, step: 1 }
    ],
    tips: [
      { t: 'Barrier: the fast threads wait (grey) for the slowest one. Then all go on together.', set: { n: 4, mode: 'barrier', seed: 3 }, play: true },
      { t: 'Spin lock: only one thread at a time is in the critical section (orange). The others spin.', set: { n: 4, mode: 'cas', cs: 2, seed: 3 }, play: true },
      { t: 'Spin lock with 8 threads: the order of entry is luck, so a thread that arrived early can be passed many times.', set: { n: 8, mode: 'cas', cs: 2, seed: 9 }, play: true },
      { t: 'Ticket lock with the same threads: they enter in the order they arrived. This is the Bakery idea built from atomicAdd.', set: { n: 8, mode: 'ticket', cs: 2, seed: 9 }, play: true }
    ],
    sim(z) {
      const n = z.p.n, r = rng(z.p.seed * 31 + n), a = [];
      for (let t = 0; t < n; t++) a.push(1 + Math.floor(r() * 5));
      const rows = a.map(() => []), entry = [];
      if (z.p.mode === 'barrier') {
        const M = Math.max(...a);
        a.forEach((x, t) => { for (let k = 0; k < M; k++) rows[t].push(k < x ? 'W' : '.'); rows[t].push('B', 'B'); });
        return { a, rows, entry, T: M + 2, M };
      }
      const ph = a.map(() => 'work'), rem = a.slice(), arr = a.map(() => 0);
      let owner = -1, tick = 0;
      while (ph.some(p => p !== 'done') && tick < 60) {
        if (owner < 0) {
          const w = []; ph.forEach((p, t) => { if (p === 'want') w.push(t); });
          if (w.length) {
            owner = z.p.mode === 'ticket' ? w.sort((x, y) => arr[x] - arr[y] || x - y)[0] : w[Math.floor(r() * w.length)];
            ph[owner] = 'cs'; rem[owner] = z.p.cs; entry.push(owner);
          }
        }
        ph.forEach((p, t) => {
          if (p === 'work') { rows[t].push('W'); if (--rem[t] === 0) { ph[t] = 'want'; arr[t] = tick + 1; } }
          else if (p === 'want') rows[t].push('.');
          else if (p === 'cs') { rows[t].push('C'); if (--rem[t] === 0) { ph[t] = 'done'; owner = -1; } }
          else rows[t].push(' ');
        });
        tick++;
      }
      return { a, rows, entry, T: tick, arr };
    },
    steps: z => z.spec.sim(z).T,
    draw(z) {
      const g = z.g, R = z.spec.sim(z), s = z.step, n = z.p.n, cw = Math.min(32, 500 / R.T);
      const col = { W: z.col.cv, '.': z.col.line, C: z.col.orange, B: z.col.purple };
      for (let k = 0; k <= R.T; k += 5) W(z, String(k), 60 + k * cw, 18, { s: 9, a: 'center', c: z.col.ink2 });
      R.rows.forEach((row, t) => {
        W(z, `T${t}`, 16, 40 + t * 24, { s: 11, mono: true });
        row.slice(0, s).forEach((c, k) => { if (c !== ' ') D.rect(g, 60 + k * cw, 27 + t * 24, cw - 1, 18, { fill: col[c], stroke: c === '.' ? z.col.line : null, w: 0.5 }); });
      });
      if (z.p.mode === 'barrier' && s >= R.M) D.line(g, 60 + R.M * cw, 22, 60 + R.M * cw, 30 + n * 24, z.col.red, 2, [4, 3]);
      const ly = 46 + n * 24;
      [['work', 'W'], ['waiting or spinning', '.'], [z.p.mode === 'barrier' ? 'after the barrier' : 'critical section', z.p.mode === 'barrier' ? 'B' : 'C']].forEach(([l, c], i) => {
        D.rect(g, 16 + i * 180, ly, 14, 14, { fill: col[c], stroke: z.col.line, w: 0.5 });
        W(z, l, 36 + i * 180, ly + 11, { s: 11 });
      });
      const wait = R.rows.reduce((acc, row) => acc + row.slice(0, s).filter(c => c === '.').length, 0);
      W(z, `time ${Math.min(s, R.T)} of ${R.T}   waiting ticks so far ${wait}`, 16, ly + 40, { s: 12, b: true });
      if (z.p.mode === 'barrier') return `Work lengths ${R.a.join(', ')}. Everyone waits until the slowest thread (length ${R.M}) reaches the barrier, then all continue together. A barrier makes the whole block wait, and only works inside one block.`;
      const order = R.entry.map(t => 'T' + t).join(', ');
      return `Work lengths ${R.a.join(', ')}. Order of entry: ${order}. ` + (z.p.mode === 'cas' ? 'With atomicCAS nobody keeps a queue: every spinner retries, and the hardware picks a winner. There is no fairness.' : 'Each thread takes a ticket with atomicAdd and waits until the "now serving" counter shows it. Earliest arrival enters first, ties by id.');
    }
  });

  def('privat', {
    title: 'Counting with atomics: one global counter or one per block', sub: 'Every thread adds 1. Atomics on the same address run one after another, so the number of global atomics decides the waiting.',
    W: 620, H: 290,
    params: [
      { k: 'b', label: 'Blocks', v: 10, min: 1, max: 10, step: 1 },
      { k: 'tpb', label: 'Threads per block', type: 'select', v: '256', opts: [['32', '32'], ['64', '64'], ['128', '128'], ['256', '256']] },
      { k: 'mode', label: 'Method', type: 'select', v: 'global', opts: [['global', 'atomicAdd on the global counter from every thread'], ['shared', 'atomicAdd in shared memory, then one global atomicAdd per block']] }
    ],
    tips: [
      { t: 'Workbook 10.1: 10 blocks of 256 threads, one global atomic per thread: 2560 global atomics on one address.', set: { b: 10, tpb: '256', mode: 'global' }, play: true },
      { t: 'Same work with a shared counter per block: 2560 fast shared atomics, but only 10 global ones.', set: { b: 10, tpb: '256', mode: 'shared' }, play: true }
    ],
    steps: z => z.p.b,
    draw(z) {
      const g = z.g, B = z.p.b, T = +z.p.tpb, s = z.step, sh = z.p.mode === 'shared';
      const bw = Math.min(54, 560 / B);
      for (let b = 0; b < B; b++) {
        const x = 16 + b * bw, done = b < s;
        D.rect(g, x, 30, bw - 6, 58, { fill: done ? z.col.surf : z.col.bg, stroke: done ? z.col.cv : z.col.line, w: done ? 2 : 1 });
        W(z, `block ${b}`, x + (bw - 6) / 2, 46, { s: 10, a: 'center' });
        if (sh) W(z, done ? String(T) : '0', x + (bw - 6) / 2, 74, { s: 12, a: 'center', mono: true, b: true, c: done ? z.col.cv : z.col.ink2 });
        if (done) D.arrow(g, x + (bw - 6) / 2, 92, 310, 140, sh ? z.col.green : z.col.red, sh ? 2 : 1, 5);
      }
      if (sh) W(z, 'shared counters', 16, 22, { s: 10, c: z.col.ink2 });
      D.rect(g, 240, 144, 140, 36, { fill: z.col.surf, stroke: z.col.ink, w: 1.5 });
      W(z, `global = ${s * T}`, 310, 167, { s: 13, a: 'center', mono: true, b: true });
      const ga = sh ? s : s * T, maxg = B * T;
      W(z, 'global atomics', 16, 214, { s: 11, b: true });
      D.rect(g, 130, 202, 440, 16, { fill: z.col.bg, stroke: z.col.line, w: 0.5 });
      D.rect(g, 130, 202, Math.max(1, 440 * ga / maxg), 16, { fill: sh ? z.col.green : z.col.red });
      W(z, String(ga), 130 + Math.max(1, 440 * ga / maxg) + 6, 215, { s: 11, mono: true, b: true });
      W(z, 'shared atomics', 16, 246, { s: 11, b: true });
      W(z, String(sh ? s * T : 0), 130, 246, { s: 11, mono: true });
      return `${B} blocks × ${T} threads = ${B * T} additions. ` + (sh ? `Each block counts in its own shared memory, then thread 0 adds the block total with one global atomicAdd: <b>${B}</b> global atomics in all. This is called privatisation.` : `Every thread does atomicAdd on the same global address: <b>${B * T}</b> global atomics, and they run one after another.`) + ` Done ${s} of ${B} blocks.`;
    }
  });

  def('prio', {
    title: 'A priority lock from one "now serving" counter', sub: 'Threads wait until the counter equals their priority. Watch what goes wrong when every thread adds 1 on the way out.',
    W: 620, H: 290,
    params: [
      { k: 'pr', label: 'Priorities of the threads (0 goes first)', type: 'text', v: '0, 1, 2, 2, 2, 3, 4' },
      { k: 'fix', label: 'Advance one level only when the whole level is done', type: 'check', v: false }
    ],
    tips: [
      { t: 'The lecture code: three threads have priority 2. Each adds 1, so the counter jumps from 2 to 5. Priorities 3 and 4 wait for ever.', set: { pr: '0, 1, 2, 2, 2, 3, 4', fix: false }, play: true },
      { t: 'The fix: count the threads that finish a level and move the counter on once per level.', set: { pr: '0, 1, 2, 2, 2, 3, 4', fix: true }, play: true },
      { t: 'No thread has priority 0 here, so nobody ever moves the counter. Everyone waits.', set: { pr: '1, 1, 2', fix: false }, play: true }
    ],
    parse(z) { return String(z.p.pr).split(/[^0-9]+/).filter(x => x !== '').slice(0, 10).map(Number).map(v => Math.min(v, 9)); },
    sim(z) {
      const P = z.spec.parse(z), done = P.map(() => false), rounds = [];
      let cur = 0;
      for (let guard = 0; guard < 20; guard++) {
        const grp = []; P.forEach((p, t) => { if (!done[t] && p === cur) grp.push(t); });
        if (!grp.length) break;
        grp.forEach(t => { done[t] = true; });
        const before = cur;
        if (z.p.fix) { cur += 1; while (cur <= 9 && !P.some((p, t) => !done[t] && p === cur) && P.some((p, t) => !done[t] && p > cur)) cur++; }
        else cur += grp.length;
        rounds.push({ grp, before, after: cur, done: done.slice() });
      }
      return { P, rounds };
    },
    steps: z => Math.max(1, z.spec.sim(z).rounds.length),
    draw(z) {
      const g = z.g, { P, rounds } = z.spec.sim(z), s = Math.min(z.step, rounds.length);
      const cur = s ? rounds[s - 1].after : 0, done = s ? rounds[s - 1].done : P.map(() => false), grp = s ? rounds[s - 1].grp : [];
      const L = 11, cw = 52;
      for (let v = 0; v < L; v++) {
        const x = 16 + v * cw;
        D.rect(g, x, 30, cw - 4, 22, { fill: v === cur ? z.col.orange : z.col.bg, stroke: z.col.line, w: 0.5 });
        W(z, String(v), x + (cw - 4) / 2, 46, { s: 11, a: 'center', mono: true, b: v === cur, c: v === cur ? '#fff' : z.col.ink });
      }
      W(z, 'now serving', 16, 20, { s: 10, c: z.col.ink2 });
      const per = {};
      P.forEach((p, t) => {
        const k = per[p] = (per[p] || 0) + 1, x = 16 + p * cw, y = 60 + (k - 1) * 30;
        if (k > 5) return;
        const inNow = grp.includes(t), fin = done[t];
        D.rect(g, x, y, cw - 4, 24, { fill: inNow ? z.col.cv : fin ? z.col.surf : z.col.bg, stroke: !fin && s >= rounds.length && z.step >= 1 ? z.col.red : z.col.line, w: !fin && s >= rounds.length ? 1.5 : 0.5 });
        W(z, `T${t}`, x + (cw - 4) / 2, y + 16, { s: 11, a: 'center', mono: true, c: inNow ? '#fff' : z.col.ink });
      });
      Object.entries(per).forEach(([p, c]) => { if (c > 5) W(z, `+${c - 5} more`, 16 + p * cw + (cw - 4) / 2, 222, { s: 10, a: 'center', c: z.col.ink2 }); });
      const stuck = P.filter((p, t) => !done[t]).length, end = s >= rounds.length && z.step >= 1;
      const msg = !rounds.length ? 'Nobody has priority 0, so the counter never moves: everyone waits for ever.' : grp.length > 1 ? `${grp.length} threads with priority ${P[grp[0]]} are inside together: this is not mutual exclusion.` : grp.length ? `T${grp[0]} works, then the counter moves to ${cur}.` : 'Press Step.';
      W(z, msg, 16, 248, { s: 12, b: true, c: grp.length > 1 || !rounds.length ? z.col.red : z.col.ink });
      if (end && rounds.length) W(z, stuck ? `${stuck} thread${stuck === 1 ? '' : 's'} wait for ever: the counter skipped past their level.` : 'Every thread finished.', 16, 274, { s: 12, b: true, c: stuck ? z.col.red : z.col.green });
      return `Lock: spin while atomicCAS(&now, my, my) != my. Unlock: atomicAdd(&now, 1). ` + (z.p.fix ? 'Fixed version: the last thread of a level moves the counter once, and empty levels are skipped.' : 'Lecture version: every thread adds 1 on the way out.') + ' Another problem the picture cannot show: if the priority 0 blocks are not resident on the GPU, nobody ever moves the counter.';
    }
  });
})();

/* ---------- 8.x number formats, quantisation, im2col, waves, tile intensity, swizzle, matmul ladder ---------- */
(() => {
  const { def, D } = CVZ, { fmt, W } = CUDAZ;
  const rnd = (x, E, M, maxv) => {
    if (!isFinite(x) || x === 0) return x;
    const bias = 2 ** (E - 1) - 1, a = Math.abs(x);
    let e = Math.floor(Math.log2(a));
    if (e < 1 - bias) e = 1 - bias;
    const q = 2 ** (e - M), v = a / q;
    let f = Math.floor(v);
    const d = v - f;
    if (d > 0.5 || (d === 0.5 && f % 2 === 1)) f += 1;
    const r = f * q;
    return Math.sign(x) * (r > maxv ? Infinity : r);
  };
  const ieeeMax = (E, M) => (2 - 2 ** -M) * 2 ** (2 ** E - 2 - (2 ** (E - 1) - 1));
  const FMTS = [
    ['FP32', 8, 23, x => Math.fround(x)],
    ['TF32', 8, 10, x => rnd(x, 8, 10, ieeeMax(8, 10))],
    ['BF16', 8, 7, x => rnd(x, 8, 7, ieeeMax(8, 7))],
    ['FP16', 5, 10, x => rnd(x, 5, 10, 65504)],
    ['FP8 E4M3', 4, 3, x => rnd(x, 4, 3, 448)],
    ['FP8 E5M2', 5, 2, x => rnd(x, 5, 2, 57344)]
  ];
  const show = v => !isFinite(v) ? 'overflow' : v === 0 ? '0' : Math.abs(v) >= 1e6 || Math.abs(v) < 1e-4 ? v.toExponential(4) : String(+v.toPrecision(8));

  def('formats', {
    title: 'One number, six formats: what survives?', sub: 'Type a number. Each row stores it in a different format with round to nearest and shows what comes back.',
    W: 620, H: 280,
    params: [{ k: 'x', label: 'Number to store', v: 300.7, type: 'text', num: true }],
    tips: [
      { t: '300.7: FP16 keeps 300.75, BF16 only 300. BF16 fails on detail.', set: { x: 300.7 }, play: true },
      { t: '70000: FP16 overflows (its largest number is 65,504). BF16 keeps the size: 70,144.', set: { x: 70000 }, play: true },
      { t: '0.00000001: FP16 underflows to 0. BF16 and TF32 keep it, since they have FP32\'s 8 exponent bits.', set: { x: 1e-8 }, play: true },
      { t: 'π: FP32 gives 7 correct digits, FP16 and BF16 give 3.140625, and FP8 gives only 3.25 or 3.', set: { x: 3.14159265 }, play: true }
    ],
    steps: () => FMTS.length,
    draw(z) {
      const g = z.g, x = Number(z.p.x), s = z.step;
      W(z, 'format', 16, 20, { s: 11, b: true, c: z.col.ink2 });
      W(z, 'bits: sign, exponent, mantissa', 110, 20, { s: 11, b: true, c: z.col.ink2 });
      W(z, 'stored value', 316, 20, { s: 11, b: true, c: z.col.ink2 });
      W(z, 'relative error', 486, 20, { s: 11, b: true, c: z.col.ink2 });
      FMTS.forEach(([name, E, M, f], i) => {
        const y = 44 + i * 36;
        W(z, name, 16, y + 13, { s: 12, b: true });
        const u = 4;
        D.rect(g, 110, y, u, 18, { fill: z.col.orange });
        D.rect(g, 110 + u, y, E * u, 18, { fill: z.col.purple });
        D.rect(g, 110 + u + E * u, y, M * u, 18, { fill: z.col.cv });
        W(z, `1 + ${E} + ${M}`, 110 + (1 + E + M) * u + 6, y + 13, { s: 10, c: z.col.ink2 });
        if (i < s) {
          const v = f(x), bad = !isFinite(v) || (v === 0 && x !== 0);
          W(z, show(v), 316, y + 13, { s: 12, mono: true, b: true, c: bad ? z.col.red : z.col.ink });
          const err = x === 0 ? 0 : Math.abs(v - x) / Math.abs(x);
          W(z, !isFinite(v) ? 'too big' : v === 0 && x !== 0 ? 'too small, lost' : err === 0 ? 'exact' : err < 1e-4 ? err.toExponential(1) : (100 * err).toPrecision(2) + ' %', 486, y + 13, { s: 11, mono: true, c: bad ? z.col.red : z.col.ink2 });
        }
      });
      return `Exponent bits (purple) set the range: how big and how small a number can be. Mantissa bits (green) set the detail: about ${''}0.3 decimal digits each. ` + (s >= FMTS.length ? 'FP16 fails on size, BF16 fails on detail. That is why BF16 is preferred for training.' : `Showing ${s} of ${FMTS.length} formats.`);
    }
  });

  def('quant', {
    title: 'INT8 quantisation: scale, round, store, bring back', sub: 'Pick weights and a range. Each weight becomes a small integer q, and s × q is what the GPU sees later.',
    W: 620, H: 290,
    params: [
      { k: 'w', label: 'Weights', type: 'text', v: '0.3, -0.8, 1.0, -0.05, 0.62' },
      { k: 'bits', label: 'Bits', type: 'select', v: '8', opts: [['8', 'INT8 (q from -127 to 127)'], ['4', 'INT4 (q from -7 to 7)']] },
      { k: 'R', label: 'Range R (values from -R to R)', v: 1, min: 0.5, max: 4, step: 0.5 }
    ],
    tips: [
      { t: 'Workbook: range -1 to 1, the weight 0.3 becomes q = 38 and comes back as 0.2992.', set: { w: '0.3, -0.8, 1.0, -0.05, 0.62', bits: '8', R: 1 }, play: true },
      { t: 'Range -2 to 2: -0.8 becomes q = -51 and comes back as -0.8031. A wider range means coarser steps.', set: { w: '-0.8, 0.3, 1.5', bits: '8', R: 2 }, play: true },
      { t: 'INT4 has only 15 levels: errors grow a lot.', set: { w: '0.3, -0.8, 1.0, -0.05, 0.62', bits: '4', R: 1 }, play: true },
      { t: 'A range that is too small clips the large weights to ±R.', set: { w: '0.3, -0.8, 1.0, -0.05, 2.5', bits: '8', R: 1 }, play: true }
    ],
    steps: () => 4,
    draw(z) {
      const g = z.g, s = z.step, R = z.p.R, qm = z.p.bits === '4' ? 7 : 127, sc = R / qm;
      const ws = String(z.p.w).split(/[^0-9.eE+-]+/).filter(t => t !== '' && !isNaN(+t)).slice(0, 6).map(Number);
      const rows = ws.map(x => { const r = x / sc, q0 = Math.round(r), q = Math.max(-qm, Math.min(qm, q0)); return { x, r, q, clip: q !== q0, back: q * sc }; });
      W(z, `s = R ÷ ${qm} = ${fmt(R)} ÷ ${qm} = ${sc.toPrecision(4)}`, 16, 20, { s: 13, b: true, mono: true });
      const x0 = 40, x1 = 580, Rv = Math.max(R, ...ws.map(Math.abs)), X = v => x0 + (v + Rv) / (2 * Rv) * (x1 - x0);
      D.line(g, x0, 66, x1, 66, z.col.ink2, 1);
      const every = qm > 7 ? 16 : 1;
      for (let q = -qm; q <= qm; q += 1) if (q % every === 0 || q === qm || q === -qm) D.line(g, X(q * sc), 60, X(q * sc), 72, z.col.ink2, 1);
      W(z, fmt(-Rv), x0, 88, { s: 10, a: 'center', c: z.col.ink2 }); W(z, '0', X(0), 88, { s: 10, a: 'center', c: z.col.ink2 }); W(z, fmt(Rv), x1, 88, { s: 10, a: 'center', c: z.col.ink2 });
      rows.forEach(r => {
        D.circle(g, X(r.x), 54, 4, { fill: z.col.cv });
        if (s >= 4) { D.rect(g, X(r.back) - 4, 74, 8, 8, { fill: r.clip ? z.col.red : z.col.orange }); }
      });
      const lab = ['weight x', 'x ÷ s', 'q (round, clip)', 'back: s × q', 'error'], cw = 82;
      lab.forEach((l, i) => W(z, l, 16, 124 + i * 26, { s: 11, b: true }));
      rows.forEach((r, j) => {
        const cx = 140 + j * cw + cw / 2, cell = (i, txt, c) => W(z, txt, cx, 124 + i * 26, { s: 11, a: 'center', mono: true, c: c || z.col.ink });
        cell(0, String(r.x));
        if (s >= 2) cell(1, r.r.toFixed(2));
        if (s >= 3) cell(2, String(r.q), r.clip ? z.col.red : z.col.ink);
        if (s >= 4) { cell(3, r.back.toFixed(4)); cell(4, Math.abs(r.back - r.x).toFixed(4), r.clip ? z.col.red : z.col.ink2); }
      });
      const msgs = ['Step 1: the scale s is the size of one integer step.', 'Step 2: divide each weight by s.', 'Step 3: round to the nearest integer and clip to the allowed range. This q is stored in 1 byte (or half a byte for INT4).', 'Step 4: multiply back by s. Green dots are the true weights, orange squares what comes back. Red means clipped.'];
      return msgs[Math.max(0, s - 1)] + ` Storage falls from 4 bytes to ${z.p.bits === '4' ? 'half a byte' : '1 byte'} per weight.`;
    }
  });

  const IMGS = { ramp: Array.from({ length: 16 }, (_, i) => i), edge: [0, 0, 9, 9, 0, 0, 9, 9, 0, 0, 9, 9, 0, 0, 9, 9], dot: [0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] };
  const FILT = { sobelx: [1, 0, -1, 2, 0, -2, 1, 0, -1], box: [1, 1, 1, 1, 1, 1, 1, 1, 1], center: [0, 0, 0, 0, 1, 0, 0, 0, 0] };
  def('im2col', {
    title: 'im2col: a convolution becomes one matrix multiply', sub: 'Every 3 × 3 window of the 4 × 4 picture is flattened into a row. Then each output is one row times the flattened filter.',
    W: 620, H: 290,
    params: [
      { k: 'img', label: 'Picture', type: 'select', v: 'ramp', opts: [['ramp', 'values 0 to 15 (the worked example)'], ['edge', 'a vertical edge'], ['dot', 'one bright dot']] },
      { k: 'f', label: 'Filter', type: 'select', v: 'sobelx', opts: [['sobelx', 'Sobel x (1 0 -1, 2 0 -2, 1 0 -1)'], ['box', 'box (all 1)'], ['center', 'identity (centre 1)']] }
    ],
    tips: [
      { t: 'The worked example: every output is -8, because a ramp has the same slope everywhere.', set: { img: 'ramp', f: 'sobelx' }, play: true },
      { t: 'A vertical edge gives strong responses where the window covers the jump.', set: { img: 'edge', f: 'sobelx' }, play: true },
      { t: 'The box filter adds up each window. Notice how each pixel appears in several rows: im2col copies data.', set: { img: 'ramp', f: 'box' }, play: true }
    ],
    steps: () => 9,
    draw(z) {
      const g = z.g, s = z.step, X = IMGS[z.p.img], F = FILT[z.p.f];
      const wins = [[0, 0], [0, 1], [1, 0], [1, 1]].map(([r, c]) => { const v = []; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) v.push(X[(r + i) * 4 + c + j]); return { r, c, v, out: v.reduce((a, x, k) => a + x * F[k], 0) }; });
      const cur = s >= 1 && s <= 4 ? s - 1 : s >= 6 ? s - 6 : -1;
      W(z, 'picture 4 × 4', 16, 20, { s: 11, b: true });
      for (let i = 0; i < 16; i++) {
        const r = Math.floor(i / 4), c = i % 4, w = cur >= 0 ? wins[cur] : null, inside = w && r >= w.r && r < w.r + 3 && c >= w.c && c < w.c + 3;
        D.rect(g, 16 + c * 26, 30 + r * 26, 25, 25, { fill: inside ? z.col.surf : z.col.bg, stroke: inside ? z.col.cv : z.col.line, w: inside ? 2 : 0.5 });
        W(z, String(X[i]), 16 + c * 26 + 12.5, 30 + r * 26 + 17, { s: 11, a: 'center', mono: true });
      }
      W(z, 'im2col matrix 4 × 9', 140, 20, { s: 11, b: true });
      wins.forEach((w, k) => {
        if (s < k + 1) return;
        w.v.forEach((v, j) => {
          D.rect(g, 140 + j * 24, 30 + k * 26, 23, 25, { fill: k === cur ? z.col.surf : z.col.bg, stroke: k === cur ? z.col.cv : z.col.line, w: k === cur ? 1.5 : 0.5 });
          W(z, String(v), 140 + j * 24 + 11.5, 30 + k * 26 + 17, { s: 11, a: 'center', mono: true });
        });
      });
      if (s >= 5) {
        W(z, 'filter', 378, 20, { s: 11, b: true });
        F.forEach((v, j) => { D.rect(g, 380, 30 + j * 24, 30, 23, { fill: z.col.bg, stroke: z.col.orange, w: 1 }); W(z, String(v), 395, 30 + j * 24 + 16, { s: 11, a: 'center', mono: true }); });
        W(z, '=', 428, 70, { s: 16, b: true });
      }
      W(z, 'output', 450, 20, { s: 11, b: true });
      wins.forEach((w, k) => {
        if (s < k + 6) return;
        D.rect(g, 450, 30 + k * 26, 40, 25, { fill: k === cur ? z.col.cv : z.col.surf, stroke: z.col.line, w: 0.5 });
        W(z, String(w.out), 470, 30 + k * 26 + 17, { s: 11, a: 'center', mono: true, b: true, c: k === cur ? '#fff' : z.col.ink });
        D.rect(g, 520 + w.c * 42, 30 + w.r * 30, 40, 28, { fill: z.col.surf, stroke: z.col.line, w: 0.5 });
        W(z, String(w.out), 540 + w.c * 42, 30 + w.r * 30 + 19, { s: 11, a: 'center', mono: true, b: true });
      });
      if (s >= 6) W(z, '2 × 2 picture', 520, 20, { s: 11, b: true });
      let msg = 'Press Step to cut out the first window.';
      if (s >= 1 && s <= 4) msg = `Window ${s} (top left at row ${wins[s - 1].r}, column ${wins[s - 1].c}) is read row by row into row ${s} of the matrix.`;
      if (s === 5) msg = 'The 3 × 3 filter is flattened into a column of 9 numbers.';
      if (s >= 6) { const w = wins[s - 6]; msg = `row ${s - 5} · filter = ${w.v.map((v, j) => `${v}×${F[j]}`).join(' + ')} = ${w.out}`; }
      W(z, msg.length > 95 ? msg.slice(0, 95) + '…' : msg, 16, 270, { s: 11, mono: s >= 6 });
      return `(4 × 9) times (9 × 1) gives 4 outputs. With 64 filters the column becomes a 9 × 64 matrix: a real GEMM that tensor cores can run. The cost: each pixel is copied into up to 9 rows, so libraries build the matrix on the fly (implicit GEMM).`;
    }
  });

  def('waves', {
    title: 'Wave quantisation: blocks run in waves', sub: 'Each SM holds a few blocks at a time. One wave fills every SM. A last wave that is almost empty still costs a full wave of time.',
    W: 620, H: 280,
    params: [
      { k: 'n', label: 'Blocks in the grid', type: 'text', num: true, v: 217 },
      { k: 'sm', label: 'GPU', type: 'select', v: '108', opts: [['108', 'A100 (108 SMs)'], ['114', 'H100 PCIe (114 SMs)'], ['132', 'H100 SXM (132 SMs)'], ['40', 'T4 (40 SMs)']] },
      { k: 'b', label: 'Blocks per SM at once', v: 1, min: 1, max: 4, step: 1 }
    ],
    tips: [
      { t: '216 blocks on an A100, one per SM: exactly 2 full waves.', set: { n: 216, sm: '108', b: 1 }, play: true },
      { t: '217 blocks: a third wave with one block while 107 SMs wait. 0.5 percent more work, 50 percent more time.', set: { n: 217, sm: '108', b: 1 }, play: true },
      { t: 'Workbook: 115 blocks on 114 SMs need 2 waves, only 50.4 percent busy.', set: { n: 115, sm: '114', b: 1 }, play: true },
      { t: 'The naive matmul: 16,384 blocks, 2 per SM on 114 SMs: 72 waves, so the partial last wave hardly matters.', set: { n: 16384, sm: '114', b: 2 }, play: true }
    ],
    steps: z => Math.max(1, Math.min(200, Math.ceil(Math.max(1, Math.floor(Number(z.p.n) || 1)) / (+z.p.sm * z.p.b)))),
    draw(z) {
      const g = z.g, n = Math.max(1, Math.floor(Number(z.p.n) || 1)), Wv = +z.p.sm * z.p.b, waves = Math.ceil(n / Wv), s = z.step;
      const shown = Math.min(waves, 200), bw = Math.min(60, 540 / shown), H = 150, base = 190;
      W(z, `one wave = ${z.p.sm} SMs × ${z.p.b} = ${Wv} blocks`, 16, 20, { s: 12, b: true });
      D.line(g, 50, base, 50 + shown * bw, base, z.col.ink2, 1);
      D.line(g, 50, base - H, 590, base - H, z.col.line, 1, [3, 3]);
      W(z, '100%', 16, base - H + 4, { s: 10, c: z.col.ink2 });
      for (let k = 0; k < Math.min(s, shown); k++) {
        const used = Math.min(Wv, n - k * Wv), h = H * used / Wv;
        D.rect(g, 50 + k * bw, base - H, Math.max(1, bw - 2), H, { fill: z.col.bg, stroke: z.col.line, w: 0.5 });
        D.rect(g, 50 + k * bw, base - h, Math.max(1, bw - 2), h, { fill: used < Wv ? z.col.orange : z.col.cv });
        if (bw >= 26) W(z, `${used}`, 50 + k * bw + (bw - 2) / 2, base - h - 4, { s: 10, a: 'center', mono: true });
      }
      W(z, 'waves (time) →', 50, base + 18, { s: 10, c: z.col.ink2 });
      const eff = n / (Wv * waves);
      if (s >= waves) W(z, `${waves} wave${waves === 1 ? '' : 's'}, SMs busy on average ${(100 * eff).toFixed(1)}%`, 16, base + 50, { s: 14, b: true, c: eff < 0.8 ? z.col.red : z.col.green });
      return `waves = ⌈blocks ÷ (SMs × blocks per SM)⌉ = ⌈${n} ÷ ${Wv}⌉ = ${waves}. Efficiency = blocks ÷ (wave size × waves) = ${n} ÷ ${Wv * waves} = ${(100 * eff).toFixed(1)}%.` + (waves > 200 ? ' Only the first 200 waves are drawn.' : '');
    }
  });

  const LADDER = [['warp tiling, no tensor cores', 32], ['TMA + tensor cores', 317], ['larger tile', 423], ['TMA and tensor core pipeline', 498], ['2 consumer warp groups', 610], ['persistent kernel', 660], ['faster barriers', 704], ['clusters + multicast', 734], ['micro optimisations', 747], ['async stores', 758], ['Hilbert schedule', 764]];
  def('tileai', {
    title: 'Bigger tiles, more work per byte', sub: 'A block computes a BM × BN tile of C. Each step along K it loads a strip of A and a strip of B. Pick the tile and see where it lands on the H100 roofline.',
    W: 620, H: 290,
    params: [
      { k: 'bm', label: 'BM (rows of the tile)', type: 'select', v: '128', opts: [['16', '16'], ['32', '32'], ['64', '64'], ['128', '128'], ['256', '256']] },
      { k: 'bn', label: 'BN (columns of the tile)', type: 'select', v: '128', opts: [['16', '16'], ['32', '32'], ['64', '64'], ['128', '128'], ['256', '256']] },
      { k: 'dt', label: 'Number format', type: 'select', v: 'fp32', opts: [['fp32', 'FP32 (4 bytes, CUDA cores, roof 51 TFLOP/s)'], ['bf16', 'BF16 (2 bytes, tensor cores, roof 756 TFLOP/s)']] }
    ],
    tips: [
      { t: 'FP32 32 × 32: AI 8, so at 2 TB/s it can reach only 16 TFLOP/s.', set: { bm: '32', bn: '32', dt: 'fp32' }, play: true },
      { t: 'FP32 128 × 128: AI 32, enough to reach the 51 TFLOP/s FP32 roof.', set: { bm: '128', bn: '128', dt: 'fp32' }, play: true },
      { t: 'A long thin tile 16 × 256 has the same area as 64 × 64 but less reuse. Square is best.', set: { bm: '16', bn: '256', dt: 'fp32' }, play: true },
      { t: 'BF16 needs AI 378 to reach 756 TFLOP/s. Even 256 × 256 (AI 128) is far below: tiles must also be reused from L2 and SMEM.', set: { bm: '256', bn: '256', dt: 'bf16' }, play: true }
    ],
    steps: () => 3,
    draw(z) {
      const g = z.g, s = z.step, BM = +z.p.bm, BN = +z.p.bn, b = z.p.dt === 'fp32' ? 4 : 2, roof = z.p.dt === 'fp32' ? 51 : 756, bwTB = 2.0;
      const ai = 2 * BM * BN / (b * (BM + BN)), reach = Math.min(roof, ai * bwTB);
      const k = 0.6, BK = 16;
      W(z, 'A strip', 16, 20, { s: 10, c: z.col.ink2 });
      D.rect(g, 16, 30, BK * k * 2, BM * k, { fill: z.col.orange, stroke: z.col.line });
      W(z, 'B strip', 60, 20, { s: 10, c: z.col.ink2 });
      D.rect(g, 60, 30, BN * k, BK * k * 2, { fill: z.col.purple, stroke: z.col.line });
      D.rect(g, 60, 30 + BK * k * 2 + 4, BN * k, BM * k, { fill: z.col.surf, stroke: z.col.cv, w: 1.5 });
      W(z, `C ${BM} × ${BN}`, 60 + BN * k / 2, 34 + BK * k * 2 + BM * k / 2 + 4, { s: 10, a: 'center', b: true });
      const lines = [`per K step: load (${BM} + ${BN}) × BK numbers, do 2 × ${BM} × ${BN} × BK FLOPs`, `AI = (2 ÷ ${b}) × ${BM}·${BN} ÷ (${BM} + ${BN}) = ${fmt(ai)} FLOP/byte`, `at ${bwTB} TB/s: ${fmt(ai)} × 2 = ${fmt(ai * bwTB)} TFLOP/s, roof ${roof}, so about ${fmt(reach)} TFLOP/s`];
      lines.slice(0, s).forEach((t, i) => W(z, t, 16, 226 + i * 20, { s: 11, mono: true, b: i === s - 1 }));
      const px = 400, py = 30, pw = 200, ph = 150, lx = v => px + (Math.log10(v) + 1) / 5 * pw, ly = v => py + ph - (Math.log10(v) + 1) / 4 * ph;
      D.rect(g, px, py, pw, ph, { fill: z.col.bg, stroke: z.col.line, w: 0.5 });
      const ridge = roof / bwTB;
      D.line(g, lx(0.1), ly(0.2), lx(ridge), ly(roof), z.col.ink2, 1.5);
      D.line(g, lx(ridge), ly(roof), lx(9999), ly(roof), z.col.ink2, 1.5);
      W(z, 'AI (log) →', px + pw - 50, py + ph + 14, { s: 9, c: z.col.ink2 });
      W(z, `roof ${roof}`, px + 4, ly(roof) - 4, { s: 9, c: z.col.ink2 });
      if (s >= 3) { D.circle(g, lx(ai), ly(reach), 5, { fill: reach < roof ? z.col.red : z.col.green }); D.line(g, lx(ridge), py, lx(ridge), py + ph, z.col.line, 1, [3, 3]); W(z, `ridge ${fmt(ridge)}`, Math.min(lx(ridge) + 3, px + pw - 60), py + ph - 6, { s: 9, c: z.col.ink2 }); }
      return 'BK cancels, so only the tile shape matters. For a fixed area, BM + BN is smallest when BM = BN, so square tiles give the most reuse and bigger tiles do better, until registers and shared memory run out.';
    }
  });

  def('swizzle', {
    title: 'Swizzling: XOR spreads a column over all banks', sub: 'A 128 byte row of a shared memory tile is 8 chunks of 16 bytes, and each chunk sits on 4 banks. Read one column (the same chunk of 8 rows) and count the clashes.',
    W: 620, H: 270,
    params: [
      { k: 'col', label: 'Column (logical chunk) to read', v: 0, min: 0, max: 7, step: 1 },
      { k: 'swz', label: 'Swizzle: slot = chunk XOR row', type: 'check', v: false }
    ],
    tips: [
      { t: 'No swizzle: all 8 rows of chunk 0 land in slot 0, the same 4 banks. An 8 way conflict.', set: { col: 0, swz: false }, play: true },
      { t: 'With the XOR swizzle the same column lands in 8 different slots. No conflict, and each row is still one contiguous 128 byte line.', set: { col: 0, swz: true }, play: true },
      { t: 'Worked example: row 5, chunk 2 goes to slot 2 XOR 5 = 7.', set: { col: 2, swz: true }, play: true }
    ],
    steps: () => 8,
    draw(z) {
      const g = z.g, s = z.step, c0 = z.p.col, sw = z.p.swz, cw = 30, ch = 22;
      const slot = (r, c) => sw ? (c ^ r) : c, hits = new Array(8).fill(0);
      W(z, 'physical slots (each 16 bytes = 4 banks)', 60, 18, { s: 11, b: true });
      for (let c = 0; c < 8; c++) W(z, `${4 * c}-${4 * c + 3}`, 60 + c * cw + cw / 2, 34, { s: 9, a: 'center', c: z.col.ink2 });
      for (let r = 0; r < 8; r++) {
        W(z, `row ${r}`, 16, 54 + r * ch, { s: 10, mono: true });
        for (let c = 0; c < 8; c++) {
          const lc = sw ? (c ^ r) : c, read = r < s && lc === c0;
          if (read) hits[c]++;
          D.rect(g, 60 + c * cw, 40 + r * ch, cw - 2, ch - 2, { fill: read ? z.col.cv : lc === c0 ? z.col.surf : z.col.bg, stroke: z.col.line, w: 0.5 });
          W(z, `${r},${lc}`, 60 + c * cw + (cw - 2) / 2, 40 + r * ch + 14, { s: 9, a: 'center', mono: true, c: read ? '#fff' : z.col.ink });
        }
      }
      W(z, 'reads per slot', 60, 236, { s: 10, c: z.col.ink2 });
      hits.forEach((h, c) => W(z, String(h), 60 + c * cw + cw / 2, 254, { s: 12, a: 'center', mono: true, b: true, c: h > 1 ? z.col.red : z.col.ink }));
      const worst = Math.max(...hits);
      W(z, `row r, chunk ${c0}`, 340, 60, { s: 12, b: true });
      W(z, sw ? `slot = ${c0} XOR r` : `slot = ${c0} for every row`, 340, 84, { s: 12, mono: true });
      if (s >= 1) { const r = s - 1; W(z, `row ${r}: ${sw ? `${c0} XOR ${r} = ${(c0 ^ r).toString(2).padStart(3, '0')}₂ = ${slot(r, c0)}` : `slot ${c0}`}`, 340, 112, { s: 12, mono: true }); }
      W(z, `worst slot: ${worst} read${worst === 1 ? '' : 's'}${worst > 1 ? ', a ' + worst + ' way conflict' : ', no conflict'}`, 340, 150, { s: 13, b: true, c: worst > 1 ? z.col.red : z.col.green });
      return 'Labels show (row, logical chunk) stored in each physical slot. XOR with the row number is its own inverse, so applying it again gives back the original layout. TMA on Hopper can swizzle tiles as it copies them (the 128 byte mode XORs address bits 7 to 9 into bits 4 to 6).';
    }
  });

  def('mmladder', {
    title: 'Climbing to the H100 speed of light', sub: 'Each step of the matmul blog fixes one bottleneck. Step through and watch BF16 TFLOP/s rise toward the 989 peak.',
    W: 620, H: 300,
    params: [],
    tips: [{ t: 'Watch the one big jump: switching to tensor cores with TMA loads gives 10 times. Every later step is about keeping the tensor cores busy.', set: {}, play: true }],
    steps: () => LADDER.length,
    draw(z) {
      const g = z.g, s = z.step, x0 = 190, wmax = 380, sc = wmax / 989;
      D.line(g, x0 + 989 * sc, 20, x0 + 989 * sc, 270, z.col.red, 1.5, [4, 3]);
      W(z, 'peak 989', x0 + 989 * sc - 50, 14, { s: 10, c: z.col.red, b: true });
      LADDER.forEach(([name, v], i) => {
        const y = 26 + i * 22;
        W(z, name, 16, y + 13, { s: 10.5, c: i < s ? z.col.ink : z.col.ink2 });
        if (i < s) {
          D.rect(g, x0, y, Math.max(2, v * sc), 16, { fill: i === s - 1 ? z.col.cv : z.col.surf, stroke: z.col.line, w: 0.5 });
          W(z, String(v), x0 + Math.max(2, v * sc) + 5, y + 13, { s: 10.5, mono: true, b: i === s - 1 });
        }
      });
      const cur = s ? LADDER[s - 1][1] : 0;
      return s ? `${LADDER[s - 1][0]}: ${cur} TFLOP/s, ${(100 * cur / 989).toFixed(0)}% of peak.` + (s === LADDER.length ? ' The final kernel matches or slightly beats cuBLAS for the tested sizes. Numbers as reported in the blog post.' : '') : 'Press Step. Before this ladder, the naive kernel ran at 3.17 TFLOP/s in FP32, and 0.24 with uncoalesced loads.';
    }
  });
})();

/* ---------- 8.2 WMMA: one warp walks along K ---------- */
(() => {
  const { def, D } = CVZ, { W } = CUDAZ;
  def('wmma', {
    title: 'WMMA: one warp owns one 16 × 16 tile of C', sub: 'Pick the tile. Each step the warp loads a 16 × 16 tile of A and of B into fragments and calls mma_sync once: c += a × b.',
    W: 620, H: 300,
    params: [
      { k: 'n', label: 'Matrix size M = N = K', type: 'select', v: '64', opts: [['64', '64 (4 × 4 tiles)'], ['128', '128 (8 × 8 tiles)']] },
      { k: 'tr', label: 'Tile row (warpM)', v: 1, min: 0, max: 7, step: 1 },
      { k: 'tc', label: 'Tile column (warpN)', v: 2, min: 0, max: 7, step: 1 }
    ],
    tips: [
      { t: '64 × 64: the warp walks 4 steps along K, so 4 mma_sync calls for its tile.', set: { n: '64', tr: 1, tc: 2 }, play: true },
      { t: '128 × 128: 8 steps. The whole matrix needs 8 × 8 × 8 = 512 calls of 8192 FLOPs each.', set: { n: '128', tr: 5, tc: 3 }, play: true }
    ],
    steps: z => +z.p.n / 16,
    draw(z) {
      const g = z.g, n = +z.p.n, T = n / 16, tr = Math.min(z.p.tr, T - 1), tc = Math.min(z.p.tc, T - 1), s = z.step, cs = Math.min(24, 136 / T);
      const bx = 190, by = 30, ax = bx - 12 - T * cs, ay = by + T * cs + 16, cx = bx, cy = ay;
      W(z, 'B (K × N)', bx, by - 8, { s: 10, b: true });
      W(z, 'A (M × K)', ax, ay - 6, { s: 10, b: true });
      W(z, 'C (M × N)', cx + T * cs + 6, cy + 12, { s: 10, b: true });
      for (let i = 0; i < T; i++) for (let j = 0; j < T; j++) {
        const bOn = j === tc && i === s - 1, aOn = i === tr && j === s - 1, cOn = i === tr && j === tc;
        D.rect(g, bx + j * cs, by + i * cs, cs - 1, cs - 1, { fill: bOn ? z.col.purple : j === tc && i < s ? z.col.surf : z.col.bg, stroke: z.col.line, w: 0.5 });
        D.rect(g, ax + j * cs, ay + i * cs, cs - 1, cs - 1, { fill: aOn ? z.col.orange : i === tr && j < s ? z.col.surf : z.col.bg, stroke: z.col.line, w: 0.5 });
        D.rect(g, cx + i * 0 + j * cs, cy + i * cs, cs - 1, cs - 1, { fill: cOn ? (s ? z.col.cv : z.col.surf) : z.col.bg, stroke: cOn ? z.col.cv : z.col.line, w: cOn ? 2 : 0.5 });
      }
      const tx = 380;
      W(z, `warp tile (${tr}, ${tc})`, tx, 40, { s: 13, b: true });
      W(z, `k steps done: ${s} of ${T}`, tx, 66, { s: 12, mono: true });
      W(z, `mma_sync calls: ${s}`, tx, 88, { s: 12, mono: true });
      W(z, `FLOPs: ${s} × 8192 = ${s * 8192}`, tx, 110, { s: 11, mono: true });
      W(z, `whole matrix: ${T}² tiles × ${T} steps`, tx, 150, { s: 11, mono: true });
      W(z, `= ${T ** 3} calls = 2 × ${n}³ FLOPs`, tx, 172, { s: 11, mono: true, b: true });
      return s ? `Step ${s}: load_matrix_sync reads A tile (${tr}, ${s - 1}) and B tile (${s - 1}, ${tc}), then mma_sync adds their product into the FP32 accumulator fragment. The 32 threads share the fragments, and nobody may assume which thread holds which numbers.` : 'Press Step. The accumulator fragment starts at 0 (fill_fragment).';
    }
  });
})();

/* ---------- 9.1 debugging and profiling: out of bounds writes, reading a profiler report ---------- */
(() => {
  const { def, D } = CVZ, { W } = CUDAZ;
  def('oob', {
    title: 'Out of bounds writes: what memcheck sees', sub: 'Thread i writes data[i + offset] into an array of n ints. Step through the threads and watch which writes leave the array.',
    W: 620, H: 280,
    params: [
      { k: 't', label: 'Threads', v: 32, min: 4, max: 48, step: 4 },
      { k: 'off', label: 'Offset (thread i writes index i + offset)', v: 10, min: 0, max: 16, step: 1 },
      { k: 'n', label: 'Array size n (ints)', v: 10, min: 4, max: 64, step: 2 }
    ],
    tips: [
      { t: 'Lecture 12: 32 threads, offset 10, an array of 10. Every write is out of bounds, from index 10 to 41 (not only threads 0 to 21 as slide 6 says).', set: { t: 32, off: 10, n: 10 }, play: true },
      { t: 'The fixed kernel: offset 0 and n at least the thread count. No bad writes.', set: { t: 32, off: 0, n: 32 }, play: true },
      { t: 'Off by one, as in the cuda-gdb example: offset 1 with 32 threads and 32 ints. Only the last thread writes out of bounds.', set: { t: 32, off: 1, n: 32 }, play: true }
    ],
    steps: z => z.p.t,
    draw(z) {
      const g = z.g, T = z.p.t, off = z.p.off, n = z.p.n, s = z.step, last = Math.max(n, off + T), cols = 24, cw = 23;
      let bad = 0;
      for (let i = 0; i < s; i++) if (i + off >= n) bad++;
      for (let idx = 0; idx < Math.min(last, 72); idx++) {
        const r = Math.floor(idx / cols), c = idx % cols, x = 16 + c * cw, y = 30 + r * 46;
        const writer = idx - off, written = writer >= 0 && writer < s, inside = idx < n;
        D.rect(g, x, y, cw - 2, 22, { fill: written ? (inside ? z.col.green : z.col.red) : inside ? z.col.surf : z.col.bg, stroke: inside ? z.col.cv : z.col.line, w: inside ? 1.5 : 0.5 });
        W(z, String(idx), x + (cw - 2) / 2, y + 15, { s: 9, a: 'center', mono: true, c: written ? '#fff' : z.col.ink2 });
        if (written) W(z, `t${writer}`, x + (cw - 2) / 2, y + 34, { s: 8.5, a: 'center', mono: true, c: z.col.ink2 });
      }
      W(z, `array: indices 0 to ${n - 1}`, 16, 20, { s: 11, b: true, c: z.col.cv });
      W(z, `${s} of ${T} threads have written. Bad writes so far: ${bad}`, 16, 200, { s: 13, b: true, c: bad ? z.col.red : z.col.green });
      const totalBad = Array.from({ length: T }, (_, i) => i + off >= n).filter(Boolean).length;
      W(z, `In total ${totalBad} of ${T} threads write outside the array (indices ${Math.max(n, off)} to ${off + T - 1}).`.replace(/indices (\d+) to (\d+)\)/, (m, a, b) => +a > +b ? 'none)' : m), 16, 226, { s: 12 });
      return 'Green: a write inside the array. Red: a write outside it. Without compute-sanitizer such a program often runs silently, because small overruns land in memory the program happens to own. compute-sanitizer reports every bad write with the thread, the block and the source line.';
    }
  });

  def('diagnose', {
    title: 'Reading a profiler report: what limits this kernel?', sub: 'Enter three numbers from the Nsight Compute summary. Step through the reasoning the lecture uses.',
    W: 620, H: 290,
    params: [
      { k: 'c', label: 'Compute (SM) throughput %', v: 37, min: 0, max: 100, step: 1 },
      { k: 'm', label: 'Memory throughput %', v: 44, min: 0, max: 100, step: 1 },
      { k: 'a', label: 'SM active cycles % (active ÷ elapsed)', v: 76, min: 0, max: 100, step: 1 }
    ],
    tips: [
      { t: 'The slide 22 report: compute 37%, memory 44%, SMs active 76%. Neither unit is busy: latency bound.', set: { c: 37, m: 44, a: 76 }, play: true },
      { t: 'A streaming kernel like saxpy: memory near its peak. Memory bound.', set: { c: 20, m: 88, a: 97 }, play: true },
      { t: 'A well tiled matmul: compute near its peak. Compute bound.', set: { c: 85, m: 40, a: 98 }, play: true }
    ],
    steps: () => 3,
    draw(z) {
      const g = z.g, s = z.step, c = z.p.c, m = z.p.m, a = z.p.a, px = 60, py = 30, pw = 200, ph = 200;
      D.rect(g, px, py, pw, ph, { fill: z.col.bg, stroke: z.col.line, w: 0.5 });
      const X = v => px + v / 100 * pw, Y = v => py + ph - v / 100 * ph;
      D.rect(g, X(60), py, pw * 0.4, ph * 0.4, { fill: z.col.surf });
      D.line(g, X(60), py, X(60), py + ph, z.col.ink2, 1, [4, 3]);
      D.line(g, px, Y(60), px + pw, Y(60), z.col.ink2, 1, [4, 3]);
      W(z, 'compute % →', px + pw - 70, py + ph + 16, { s: 10, c: z.col.ink2 });
      W(z, 'memory %', 16, py + 8, { s: 10, c: z.col.ink2 });
      W(z, 'latency bound', X(4), Y(8), { s: 10, c: z.col.ink2 });
      W(z, 'memory bound', X(4), Y(94), { s: 10, c: z.col.ink2 });
      W(z, 'compute bound', X(64), Y(8), { s: 10, c: z.col.ink2 });
      W(z, 'both busy', X(64), Y(94), { s: 10, c: z.col.ink2 });
      if (s >= 2) D.circle(g, X(c), Y(m), 6, { fill: z.col.orange });
      const tx = 290;
      const lines = [];
      if (s >= 1) lines.push([`1. SMs active ${a}% of the time.`, a < 85 ? 'The grid is too small or uneven: some SMs sit idle.' : 'Every SM had work almost all the time.']);
      if (s >= 2) lines.push([`2. Compute ${c}%, memory ${m}%.`, c >= 60 && m >= 60 ? 'Both are high: well balanced.' : c >= 60 ? 'Compute is the busy unit.' : m >= 60 ? 'Memory is the busy unit.' : 'Both are under 60% of peak.']);
      if (s >= 3) {
        const v = c >= 60 && c >= m ? ['Compute bound.', 'Use tensor cores, fewer instructions, cheaper maths.'] : m >= 60 ? ['Memory bound.', 'Coalesce, reuse data in shared memory, use narrower types.'] : ['Latency bound: warps mostly wait.', 'More work per launch, more loads in flight (ILP), more warps, fewer syncs. Check the stall reasons.'];
        lines.push([`3. ${v[0]}`, v[1]]);
      }
      let y = 40;
      lines.forEach(([h, t]) => { W(z, h, tx, y, { s: 12, b: true }); y += 18; const words = t.split(' '); let line = ''; words.forEach(w => { if ((line + ' ' + w).length > 44) { W(z, line, tx, y, { s: 11, c: z.col.ink2 }); y += 16; line = w; } else line = line ? line + ' ' + w : w; }); if (line) { W(z, line, tx, y, { s: 11, c: z.col.ink2 }); y += 16; } y += 10; });
      return 'Rule of thumb from the lecture: a unit under about 60% of its peak is not the limit. If neither compute nor memory is high, the warps spend their time waiting, so look at Warp State Statistics: long scoreboard means waiting on global memory, barrier means __syncthreads, MIO throttle means shared memory pressure.';
    }
  });
})();

/* ---------- 9.2 Triton: one program handles a whole block of indices ---------- */
(() => {
  const { def, D } = CVZ, { W } = CUDAZ;
  def('triton', {
    title: 'Triton: each program instance handles a block of elements', sub: 'In CUDA one thread handles one element. In Triton one program handles BLOCK elements at once, and a mask switches off the ones past the end.',
    W: 620, H: 260,
    params: [
      { k: 'n', label: 'Array length n', v: 22, min: 1, max: 48, step: 1 },
      { k: 'B', label: 'BLOCK', type: 'select', v: '8', opts: [['4', '4'], ['8', '8'], ['16', '16']] }
    ],
    tips: [
      { t: 'n = 22 with BLOCK 8: three programs. The last one has only 6 real elements, so 2 lanes are masked off.', set: { n: 22, B: '8' }, play: true },
      { t: 'n = 32 with BLOCK 16: two programs and nothing masked.', set: { n: 32, B: '16' }, play: true }
    ],
    steps: z => Math.ceil(z.p.n / +z.p.B),
    draw(z) {
      const g = z.g, n = z.p.n, B = +z.p.B, P = Math.ceil(n / B), s = z.step, cw = Math.min(26, 580 / (P * B));
      const cols = [z.col.cv, z.col.orange, z.col.purple, z.col.green];
      W(z, `grid = cdiv(${n}, ${B}) = ${P} program${P === 1 ? '' : 's'}`, 16, 20, { s: 12, b: true, mono: true });
      for (let p = 0; p < P; p++) for (let j = 0; j < B; j++) {
        const off = p * B + j, x = 16 + off * cw, live = off < n, on = p < s;
        D.rect(g, x, 40, cw - 2, 30, { fill: on ? (live ? cols[p % 4] : z.col.red) : z.col.bg, stroke: z.col.line, w: 0.5 });
        if (cw >= 16) W(z, String(off), x + (cw - 2) / 2, 60, { s: 9, a: 'center', mono: true, c: on ? '#fff' : z.col.ink2 });
        if (j === 0) W(z, `pid ${p}`, x, 88, { s: 10, c: on ? z.col.ink : z.col.ink2 });
      }
      D.line(g, 16 + n * cw - 1, 34, 16 + n * cw - 1, 76, z.col.red, 2, [4, 3]);
      W(z, `n = ${n}`, Math.min(16 + n * cw + 4, 560), 30, { s: 10, c: z.col.red, b: true });
      if (s >= 1) {
        const p = s - 1, lo = p * B, hi = lo + B - 1, live = Math.min(n, lo + B) - lo;
        W(z, `pid = ${p}`, 16, 130, { s: 12, mono: true });
        W(z, `offs = ${p} × ${B} + arange(0, ${B}) = ${lo} … ${hi}`, 16, 154, { s: 12, mono: true });
        W(z, `mask = offs < ${n}: ${live} true, ${B - live} false`, 16, 178, { s: 12, mono: true, c: B - live ? z.col.red : z.col.ink });
        W(z, `tl.load and tl.store touch only the ${live} lanes where the mask is true`, 16, 202, { s: 12 });
      }
      return 'Triton decides how the BLOCK lanes map to threads, vector loads and shared memory. You think in blocks, and the compiler handles coalescing and many tiling details. The mask plays the role of if (i < n) in CUDA.';
    }
  });
})();

/* ---------- 10.1 Quiz 1 Q7: trace one thread of a matrix vector kernel ---------- */
(() => {
  const { def, D } = CVZ, { W } = CUDAZ;
  def('matvec', {
    title: 'Trace one thread of matVecMul', sub: 'Thread i owns row i of A. Step through its loop: read A[i·N + j] and x[j], multiply, add to sum.',
    W: 620, H: 270,
    params: [
      { k: 'A', label: 'A (4 rows, separated by /)', type: 'text', v: '1 2 1 0 / 0 1 3 1 / 2 0 1 2 / 1 1 0 1' },
      { k: 'x', label: 'x', type: 'text', v: '1 2 3 4' },
      { k: 'i', label: 'Thread i', v: 2, min: 0, max: 3, step: 1 }
    ],
    tips: [
      { t: 'Quiz 1 Q7: thread 2 takes row 2 = [2, 0, 1, 2]: 2·1 + 0·2 + 1·3 + 2·4 = 13.', set: { A: '1 2 1 0 / 0 1 3 1 / 2 0 1 2 / 1 1 0 1', x: '1 2 3 4', i: 2 }, play: true },
      { t: 'Thread 1 with the same data: 0·1 + 1·2 + 3·3 + 1·4 = 15.', set: { i: 1 }, play: true }
    ],
    steps: () => 4,
    draw(z) {
      const g = z.g, s = z.step, i = z.p.i;
      const nums = t => String(t).split(/[^0-9.-]+/).filter(v => v !== '' && !isNaN(+v)).map(Number);
      const rows = String(z.p.A).split('/').map(nums).slice(0, 4);
      while (rows.length < 4) rows.push([0, 0, 0, 0]);
      rows.forEach(r => { while (r.length < 4) r.push(0); r.length = 4; });
      const x = nums(z.p.x).slice(0, 4); while (x.length < 4) x.push(0);
      W(z, 'A (row major)', 16, 20, { s: 11, b: true });
      for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) {
        const on = r === i && c === s - 1, row = r === i;
        D.rect(g, 16 + c * 34, 30 + r * 30, 32, 28, { fill: on ? z.col.orange : row ? z.col.surf : z.col.bg, stroke: row ? z.col.cv : z.col.line, w: row ? 1.5 : 0.5 });
        W(z, String(rows[r][c]), 32 + c * 34, 49 + r * 30, { s: 12, a: 'center', mono: true, c: on ? '#fff' : z.col.ink });
      }
      W(z, 'x', 170, 20, { s: 11, b: true });
      x.forEach((v, j) => { const on = j === s - 1; D.rect(g, 170, 30 + j * 30, 32, 28, { fill: on ? z.col.purple : z.col.bg, stroke: z.col.line, w: 0.5 }); W(z, String(v), 186, 49 + j * 30, { s: 12, a: 'center', mono: true, c: on ? '#fff' : z.col.ink }); });
      W(z, 'j', 230, 20, { s: 11, b: true }); W(z, 'index i·N + j', 260, 20, { s: 11, b: true }); W(z, 'product', 380, 20, { s: 11, b: true }); W(z, 'sum', 470, 20, { s: 11, b: true });
      let sum = 0;
      for (let j = 0; j < s; j++) {
        const p = rows[i][j] * x[j]; sum += p;
        W(z, String(j), 230, 49 + j * 30, { s: 12, mono: true });
        W(z, String(i * 4 + j), 260, 49 + j * 30, { s: 12, mono: true });
        W(z, `${rows[i][j]} × ${x[j]} = ${p}`, 380, 49 + j * 30, { s: 12, mono: true });
        W(z, String(sum), 470, 49 + j * 30, { s: 12, mono: true, b: j === s - 1 });
      }
      W(z, `i = blockIdx.x · blockDim.x + threadIdx.x = 0 · 4 + ${i} = ${i}`, 16, 178, { s: 12, mono: true });
      if (s >= 4) W(z, `y[${i}] = ${sum}`, 16, 214, { s: 16, b: true, c: z.col.green });
      return 'Row i starts at flat index i × N. Each loop step reads one element of A and one of x, so a thread does 8 loads and 1 store here.';
    }
  });
})();
