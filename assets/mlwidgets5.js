/* ===== MLOps animations (the MLOps subject).
   Uses the framework MLZ from assets/mlwidgets.js. Every animation starts empty and adds one step each time Step
   is pressed, with a plain English line for that step. ===== */

/* =====================================================================================================
   MLOps 1.1  setting up a computer: how the terminal finds python through PATH, and why each project gets a venv
   ===================================================================================================== */
(() => {
  const { trace, D, head, box } = MLZ;
  const PATHS = {
    unix: { sep: '/', base: [['/usr/local/bin', []], ['/usr/bin', ['python3', 'pip3', 'git']], ['/bin', ['ls', 'cat']]],
      venv: ['~/project/.venv/bin', ['python', 'python3', 'pip', 'activate']], pkgs: '~/project/.venv/lib/python3.14/site-packages', cmd: 'python', shell: 'macOS, Linux or ChromeOS terminal' },
    win: { sep: '\\', base: [['~\\AppData\\Local\\Programs\\Python\\Python314', ['python.exe']], ['C:\\Windows\\System32', ['cmd.exe', 'where.exe']], ['~\\AppData\\Local\\Microsoft\\WindowsApps', ['python.exe (Store alias)']]],
      venv: ['~\\project\\.venv\\Scripts', ['python.exe', 'pip.exe', 'Activate.ps1']], pkgs: '~\\project\\.venv\\Lib\\site-packages', cmd: 'python', shell: 'Windows PowerShell' }
  };

  trace('mlpath', {
    title: 'How the terminal finds python',
    sub: 'When you type a command, the terminal looks through the folders listed in the PATH variable, in order, and runs the first program with that name. Activating a virtual environment simply puts its folder at the front of PATH.',
    W: 600, H: 330,
    params: [
      { k: 'os', label: 'System', type: 'select', v: 'unix', opts: [['unix', 'macOS, Linux or ChromeOS'], ['win', 'Windows (PowerShell)']] },
      { k: 'venv', label: 'Virtual environment', type: 'select', v: 'off', opts: [['off', 'Not activated'], ['on', 'Activated (.venv)']] }
    ],
    tips: [
      { t: 'macOS or Linux without a virtual environment: many systems have only python3, so typing python finds nothing.', set: { os: 'unix', venv: 'off' }, play: true },
      { t: 'Activate the environment: its folder is checked first, so python and pip now mean the project’s own copies.', set: { os: 'unix', venv: 'on' }, play: true }
    ],
    frames(p) {
      const P = PATHS[p.os], dirs = (p.venv === 'on' ? [P.venv] : []).concat(P.base);
      const want = p.os === 'win' ? 'python.exe' : 'python';
      const fr = [{ dirs, k: -1, found: -1, say: `You type <b>${P.cmd}</b> in the ${P.shell}. PATH lists ${dirs.length} folders${p.venv === 'on' ? ', and the first one is the project’s .venv folder because activate put it there' : ''}.` }];
      let found = -1;
      for (let k = 0; k < dirs.length; k++) {
        const hit = dirs[k][1].some(n => n === want);
        fr.push({ dirs, k, found: hit ? k : -1, say: hit ? `Folder ${k + 1}: <b>${dirs[k][0]}</b> has ${want}. The search stops here.` : `Folder ${k + 1}: ${dirs[k][0]} has no ${want}${dirs[k][1].length ? ` (only ${dirs[k][1].join(', ')})` : ''}, so keep looking.` });
        if (hit) { found = k; break; }
      }
      let end;
      if (found < 0) end = 'No folder has <b>python</b>, so you get “command not found”. Type <b>python3</b> instead, or create and activate a virtual environment, which adds a python command.';
      else if (p.venv === 'on') end = `The project’s own python runs, and pip installs into <b>${P.pkgs}</b>. Other projects and the system are not touched.`;
      else end = 'The python installed for your whole user account runs. Packages you install now are shared by every project, which leads to version clashes. Use a virtual environment per project.';
      fr.push({ dirs, k: found < 0 ? dirs.length : found, found, done: true, say: end });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, 'PATH, searched from top to bottom', 14, 26);
      f.dirs.forEach((d, i) => {
        const y = 40 + i * 62, on = i === f.k, hit = i === f.found, seen = f.k >= 0 && i <= f.k;
        box(z, 14, y, 330, 46, '', { fill: hit ? 'rgba(22,163,74,0.18)' : (on ? c.bg : c.surf), stroke: hit ? c.green : (on ? c.cv : c.line), w: on || hit ? 2.5 : 1.5 });
        D.text(g, `${i + 1}. ${d[0]}`, 24, y + 19, { s: 12, mono: true, b: true, c: c.ink });
        D.text(g, d[1].length ? d[1].join('  ') : '(no programs we need)', 24, y + 37, { s: 11, mono: true, c: seen ? c.ink2 : c.line });
        if (seen) D.text(g, hit ? 'found' : 'no', 336, y + 28, { s: 12, b: true, a: 'right', c: hit ? c.green : c.red });
      });
      head(z, 'You typed', 370, 26);
      box(z, 370, 40, 216, 40, '> python', { mono: true, s: 14, b: true, fill: c.bg });
      if (f.done) {
        const ok = f.found >= 0;
        box(z, 370, 100, 216, 70, ok ? `runs folder ${f.found + 1}` : 'command not found', { s: 14, b: true, fill: ok ? 'rgba(22,163,74,0.18)' : 'rgba(220,38,38,0.15)', stroke: ok ? c.green : c.red });
      }
      D.text(g, 'green: the first match wins', 370, 300, { s: 10, c: c.ink2 });
      D.text(g, 'activate puts .venv at the top', 370, 316, { s: 10, c: c.ink2 });
    }
  });

  trace('mlvenvs', {
    title: 'One shared install against one environment per project',
    sub: 'Project A is new and uses pandas 3.0.2 with NumPy 2.4.6. Project B is an old model that was trained with NumPy 2.3.2. Watch what happens to each project when you install the second one’s packages.',
    W: 600, H: 330,
    params: [
      { k: 'mode', label: 'Where packages go', type: 'select', v: 'global', opts: [['global', 'One shared install for everything'], ['venv', 'A separate .venv in each project']] }
    ],
    tips: [
      { t: 'One shared install: installing project B’s requirements replaces NumPy 2.4.6 with 2.3.2, and project A is left with a version conflict.', set: { mode: 'global' }, play: true },
      { t: 'A .venv per project: each project keeps its own NumPy, so both keep working.', set: { mode: 'venv' }, play: true }
    ],
    frames(p) {
      const g = p.mode === 'global';
      const S = (a, b, ok, say, extra = {}) => ({ g, a, b, ok, say, ...extra });
      const fr = [S(null, null, [null, null], g ? 'There is one place for packages, shared by every project on the computer.' : 'Each project folder has its own .venv folder with its own packages.')];
      fr.push(S({ numpy: '2.4.6', pandas: '3.0.2' }, g ? null : {}, [true, null], 'Install project A: <b>pip install numpy==2.4.6 pandas==3.0.2</b>. Project A runs.'));
      if (g) {
        fr.push(S({ numpy: '2.3.2', pandas: '3.0.2' }, null, [true, true], 'Install project B: <b>pip install numpy==2.3.2</b>. pip removes NumPy 2.4.6 to make room, because one place can hold only one version, and only prints a warning about pandas.', { swap: true }));
        fr.push(S({ numpy: '2.3.2', pandas: '3.0.2' }, null, [false, true], 'Project B runs, but project A is now broken: its pandas 3.0.2 requires NumPy 2.3.3 or newer on Python 3.14, so <b>pip check</b> reports a conflict and A runs on a NumPy it was never tested with. Fixing A breaks B again. This is called <b>dependency hell</b>.'));
      } else {
        fr.push(S({ numpy: '2.4.6', pandas: '3.0.2' }, { numpy: '2.3.2' }, [true, true], 'Activate project B’s .venv and install <b>numpy==2.3.2</b>. It goes into B’s folder only.'));
        fr.push(S({ numpy: '2.4.6', pandas: '3.0.2' }, { numpy: '2.3.2' }, [true, true], 'Both projects run with the exact versions they need.'));
      }
      fr.push(S(fr[fr.length - 1].a, fr[fr.length - 1].b, fr[fr.length - 1].ok, g ? 'The fix is a virtual environment per project, plus a requirements.txt so anyone can rebuild the same set.' : 'Write each set down with <b>pip freeze &gt; requirements.txt</b>, so a teammate or a server can rebuild it with pip install -r requirements.txt.', { freeze: !g }));
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const proj = (x, name, ok) => {
        box(z, x, 20, 200, 60, '', { fill: ok === false ? 'rgba(220,38,38,0.15)' : (ok ? 'rgba(22,163,74,0.15)' : c.surf), stroke: ok === false ? c.red : (ok ? c.green : c.line) });
        D.text(g, name, x + 12, 44, { s: 13, b: true, c: c.ink });
        D.text(g, ok === null ? 'not installed yet' : (ok ? 'runs' : 'version conflict'), x + 12, 66, { s: 12, mono: true, c: ok === false ? c.red : (ok ? c.green : c.ink2) });
      };
      proj(40, 'Project A (new)', f.ok[0]);
      proj(360, 'Project B (old model)', f.ok[1]);
      const pk = (x, y, w, title, set) => {
        box(z, x, y, w, 120, '', { fill: c.bg, dash: set ? null : [4, 3] });
        D.text(g, title, x + 10, y + 20, { s: 11, b: true, c: c.ink2 });
        Object.entries(set || {}).forEach(([n, v], i) => D.text(g, `${n} ${v}`, x + 10, y + 46 + i * 22, { s: 13, mono: true, b: n === 'numpy', c: n === 'numpy' && f.swap ? c.red : c.ink }));
      };
      if (f.g) {
        pk(150, 130, 300, 'one shared site-packages', f.a);
        D.arrow(g, 140, 82, 220, 128, c.ink2, 1.5, 6); D.arrow(g, 460, 82, 380, 128, c.ink2, 1.5, 6);
      } else {
        pk(40, 130, 200, 'A/.venv', f.a); pk(360, 130, 200, 'B/.venv', f.b);
        D.arrow(g, 140, 82, 140, 128, c.ink2, 1.5, 6); D.arrow(g, 460, 82, 460, 128, c.ink2, 1.5, 6);
      }
      if (f.freeze) D.text(g, 'pip freeze > requirements.txt  (one file in each project)', 300, 300, { a: 'center', s: 12, mono: true, c: c.cv });
    }
  });
})();

/* =====================================================================================================
   MLOps 1.2  the lifecycle at three automation levels, and why a fixed random seed makes runs repeatable
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, box, rng, klass } = MLZ;
  const STAGES = ['Define the problem', 'Get and version data', 'Train and track', 'Evaluate', 'Register the model', 'Deploy', 'Monitor', 'Retrain'];
  const AUTO = { // which stages run without a person, per maturity level (Google Cloud MLOps levels 0, 1, 2)
    '0': [false, false, false, false, false, false, false, false],
    '1': [false, true, true, true, true, false, true, true],
    '2': [false, true, true, true, true, true, true, true]
  };
  const NOTE = {
    '0': ['A person writes down the goal and the success metric.', 'Someone exports a CSV by hand.', 'A data scientist runs a notebook.', 'They check the score by eye.', 'The model file is emailed or copied to a shared drive.', 'An engineer rewrites the code for production.', 'Nobody watches the model after launch.', 'Retraining happens months later, when someone notices.'],
    '1': ['A person writes down the goal and the success metric.', 'A pipeline pulls fresh data and records its version.', 'The pipeline trains and logs parameters and metrics.', 'Automatic checks compare the new model with the current one.', 'Passing models go into a model registry.', 'Release is still started by a person.', 'Dashboards and alerts watch inputs and accuracy.', 'Drift or a schedule triggers the training pipeline again.'],
    '2': ['A person writes down the goal and the success metric.', 'Data arrives through tested, versioned pipelines.', 'Training runs as a tested pipeline, built and shipped by CI.', 'Quality gates block worse models.', 'The registry keeps every version for rollback.', 'CD rolls the model out, often to a small share of users first.', 'Monitoring compares live data with the training data.', 'Retraining, testing and release run end to end.']
  };

  trace('mllifecycle', {
    title: 'The MLOps lifecycle at three levels of automation',
    sub: 'A model goes round the same loop again and again. The difference between a hobby project and a reliable product is how much of the loop runs automatically. Green stages run without a person, grey stages need one.',
    W: 600, H: 330,
    params: [
      { k: 'level', label: 'Maturity level', type: 'select', v: '0', opts: [['0', 'Level 0: everything by hand'], ['1', 'Level 1: automated training pipeline'], ['2', 'Level 2: CI/CD for the whole pipeline']] }
    ],
    tips: [
      { t: 'Level 0: every stage needs a person, so the model is rarely retrained and quietly gets worse.', set: { level: '0' }, play: true },
      { t: 'Level 2: only defining the problem needs a person. New code and new data both flow to production through tested pipelines.', set: { level: '2' }, play: true }
    ],
    frames(p) {
      const a = AUTO[p.level], fr = [{ k: -1, a, say: `Level ${p.level}. The loop has ${STAGES.length} stages. Press Step to walk round it.` }];
      STAGES.forEach((s, k) => fr.push({ k, a, say: `<b>${s}</b>: ${NOTE[p.level][k]} ${a[k] ? '(automatic)' : '(by hand)'}` }));
      const n = a.filter(Boolean).length;
      fr.push({ k: 8, a, say: `${n} of ${STAGES.length} stages run automatically. ${p.level === '0' ? 'Most teams start here. The first goal is level 1: make training a repeatable pipeline.' : (p.level === '1' ? 'The model retrains itself, but changes to the pipeline code still go out by hand.' : 'This is where large ML products aim to be. Changes to code, data and model all go through tests.')}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, cx = 222, cy = 165, RX = 150, RY = 138;
      const at = k => { const t = -Math.PI / 2 + k * 2 * Math.PI / STAGES.length; return [cx + RX * Math.cos(t), cy + RY * Math.sin(t)]; };
      STAGES.forEach((s, k) => {
        const [x1, y1] = at(k), [x2, y2] = at(k + 1), dx = x2 - x1, dy = y2 - y1;
        D.arrow(g, x1 + dx * 0.32, y1 + dy * 0.32, x1 + dx * 0.68, y1 + dy * 0.68, c.ink2, 1.5, 6);
      });
      STAGES.forEach((s, k) => {
        const [x, y] = at(k), seen = k <= f.k, on = k === f.k;
        box(z, x - 60, y - 15, 120, 30, s, { s: 11, b: on, fill: seen ? (f.a[k] ? 'rgba(22,163,74,0.18)' : c.bg) : c.surf, stroke: on ? c.cv : (seen && f.a[k] ? c.green : c.line), w: on ? 2.5 : 1.2 });
      });
      head(z, 'Automatic so far', 450, 40);
      const n = f.a.slice(0, Math.max(0, Math.min(8, f.k + 1))).filter(Boolean).length;
      D.text(g, `${n} / ${Math.max(0, Math.min(8, f.k + 1))}`, 450, 72, { s: 22, mono: true, b: true, c: c.ink });
      D.text(g, 'green: runs without a person', 450, 290, { s: 10, c: c.green });
      D.text(g, 'grey: needs a person', 450, 306, { s: 10, c: c.ink2 });
    }
  });

  // 40 fixed points in two overlapping groups, used by every run
  const PTS = (() => { const R = rng(17), out = []; const gs = () => { let u = 0; while (u === 0) u = R(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * R()); };
    for (let i = 0; i < 40; i++) { const y = i % 2; out.push([y * 1.2 + gs() * 0.8, y * 0.9 + gs() * 0.8, y]); } return out; })();
  function runOnce(seed) {
    const R = rng(seed), idx = PTS.map((_, i) => i);
    for (let i = idx.length - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]]; }
    const tr = idx.slice(0, 30), te = idx.slice(30), cen = [0, 1].map(c => { const m = tr.filter(i => PTS[i][2] === c); return [m.reduce((a, i) => a + PTS[i][0], 0) / m.length, m.reduce((a, i) => a + PTS[i][1], 0) / m.length]; });
    const pred = i => ((PTS[i][0] - cen[0][0]) ** 2 + (PTS[i][1] - cen[0][1]) ** 2 <= (PTS[i][0] - cen[1][0]) ** 2 + (PTS[i][1] - cen[1][1]) ** 2 ? 0 : 1);
    return { te, acc: te.filter(i => pred(i) === PTS[i][2]).length / te.length };
  }

  trace('mlseeds', {
    title: 'Same code, same data, different score: the random seed',
    sub: 'Each run shuffles the same 40 points, trains a nearest centroid classifier on 30 and tests on the other 10 (circled). The shuffle uses a random number generator. Fix its seed and every run repeats exactly.',
    W: 600, H: 330,
    params: [
      { k: 'seed', label: 'Random seed', type: 'select', v: 'none', opts: [['none', 'Not set: a new seed every run'], ['fixed', 'Fixed: seed = 42 every run']] }
    ],
    tips: [
      { t: 'No seed: five runs of identical code give different test accuracies, so you cannot tell whether a change helped.', set: { seed: 'none' }, play: true },
      { t: 'Seed fixed at 42: every run picks the same test points and gets the same score, so results can be repeated and compared.', set: { seed: 'fixed' }, play: true }
    ],
    frames(p) {
      const fr = [{ runs: [], cur: null, say: 'The data never changes: 40 points in two groups. Only the random split changes between runs.' }], runs = [];
      for (let r = 0; r < 5; r++) {
        const seed = p.seed === 'fixed' ? 42 : 1000 + 37 * r, out = runOnce(seed);
        runs.push(out.acc);
        fr.push({ runs: runs.slice(), cur: out, say: `Run ${r + 1} (seed ${seed}${p.seed === 'fixed' ? '' : ', different each time'}): test accuracy <b>${f2(out.acc * 100, 0)} percent</b>.` });
      }
      const lo = Math.min(...runs), hi = Math.max(...runs);
      fr.push({ runs, cur: fr[fr.length - 1].cur, say: hi === lo ? `All five runs agree exactly at ${f2(lo * 100, 0)} percent. A fixed seed makes results repeatable, not better: this split happens to be harder than most. Record the seed with the code, and report the spread over several seeds as the honest uncertainty.` : `The scores range from ${f2(lo * 100, 0)} to ${f2(hi * 100, 0)} percent with nothing changed. A 10 point “improvement” could be pure luck.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, X = v => 30 + (v + 2.5) / 6 * 330, Y = v => 300 - (v + 2.5) / 5.5 * 270;
      g.strokeStyle = c.line; g.strokeRect(20, 20, 350, 290);
      PTS.forEach((q, i) => {
        D.circle(g, X(q[0]), Y(q[1]), 4, { fill: klass(z, q[2]) });
        if (f.cur && f.cur.te.includes(i)) D.circle(g, X(q[0]), Y(q[1]), 8, { stroke: c.ink, w: 1.5 });
      });
      head(z, 'Test accuracy per run', 400, 30);
      f.runs.forEach((a, r) => {
        D.text(g, `run ${r + 1}`, 400, 60 + r * 30, { s: 12, c: c.ink2 });
        g.fillStyle = c.cv; g.fillRect(450, 48 + r * 30, a * 100, 16);
        D.text(g, `${f2(a * 100, 0)}%`, 456 + a * 100, 61 + r * 30, { s: 12, mono: true, b: true, c: c.ink });
      });
      D.text(g, 'circled: the 10 test points of the latest run', 400, 306, { s: 10, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   MLOps 2.1  pipelines: one row flowing through fitted steps, and leakage when a step sees the test rows
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, box } = MLZ;
  const nf = v => f2(v, 2).replace('-', '−');
  const TRAIN = [[2, 'basic'], [10, 'plus'], [null, 'premium'], [30, 'basic'], [18, 'plus']];
  const ROWS = { a: [4, 'basic'], b: [null, 'plus'], c: [40, 'student'] };
  const W = { b: 0.3, t: -1.1, basic: 0.9, plus: -0.3, premium: -0.6 };

  trace('mlpipeflow', {
    title: 'A pipeline learns on training rows, then applies the same steps to every new row',
    sub: 'The pipeline has three steps before the model: fill a missing tenure with the median, scale it to a z score, and one hot encode the plan. fit learns the median, mean, spread and list of plans from the training rows only. predict reuses them.',
    W: 600, H: 330,
    params: [
      { k: 'row', label: 'New customer', type: 'select', v: 'a', opts: [['a', 'tenure 4 months, plan basic'], ['b', 'tenure missing, plan plus'], ['c', 'tenure 40 months, plan student (never seen)']] }
    ],
    tips: [
      { t: 'A missing tenure: the imputer fills in the training median, 14, so the model still gets a number.', set: { row: 'b' }, play: true },
      { t: 'An unseen plan: with handle_unknown set to ignore, every plan column becomes 0 instead of crashing the service.', set: { row: 'c' }, play: true }
    ],
    frames(p) {
      const known = TRAIN.map(r => r[0]).filter(v => v !== null).sort((a, b) => a - b);
      const med = (known[1] + known[2]) / 2;
      const filled = TRAIN.map(r => (r[0] === null ? med : r[0])), mean = filled.reduce((a, v) => a + v, 0) / filled.length;
      const sd = Math.sqrt(filled.reduce((a, v) => a + (v - mean) ** 2, 0) / filled.length), plans = ['basic', 'plus', 'premium'];
      const [t, plan] = ROWS[p.row], t1 = t === null ? med : t, z = (t1 - mean) / sd, oh = plans.map(q => (q === plan ? 1 : 0));
      const logit = W.b + W.t * z + W.basic * oh[0] + W.plus * oh[1] + W.premium * oh[2], prob = 1 / (1 + Math.exp(-logit));
      const S = (st, say, extra = {}) => ({ st, med, mean, sd, plans, t, plan, t1, z, oh, logit, prob, say, ...extra });
      return [
        S(0, 'Five training rows. One tenure is missing. Nothing has been learned yet.'),
        S(1, `fit, step 1: the imputer learns the <b>median</b> of the known tenures (2, 10, 18, 30) = <b>${f2(med, 0)}</b>.`),
        S(2, `fit, step 2: the scaler learns the mean <b>${f2(mean, 1)}</b> and the spread <b>${f2(sd, 2)}</b> of the filled tenures.`),
        S(3, 'fit, step 3: the encoder learns the plans it has seen: basic, plus, premium. Then the model is trained on the transformed rows (here its weights are fixed so the numbers are easy to follow).'),
        S(4, `predict: a new customer arrives with tenure ${t === null ? 'missing' : t} and plan ${plan}.`),
        S(5, t === null ? `Impute: the missing tenure becomes the training median, <b>${f2(med, 0)}</b>.` : `Impute: tenure ${t} is present, so it passes through unchanged.`),
        S(6, `Scale: z = (${f2(t1, 0)} − ${f2(mean, 1)}) / ${f2(sd, 2)} = <b>${nf(z)}</b>, using the training mean and spread, never statistics of the new row.`),
        S(7, plans.includes(plan) ? `One hot: plan ${plan} becomes [${oh.join(', ')}].` : `One hot: “${plan}” was never seen in training. With handle_unknown='ignore' it becomes [0, 0, 0] instead of an error.`),
        S(8, `Model: logit = ${nf(logit)}, so the churn probability is <b>${f2(prob, 2)}</b>. One saved pipeline object did all of this, so training and serving cannot drift apart.`)
      ];
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, 'Training rows (tenure, plan)', 14, 24);
      TRAIN.forEach((r, i) => D.text(g, `${r[0] === null ? 'NaN' : r[0]}  ${r[1]}`, 18, 46 + i * 18, { s: 12, mono: true, c: r[0] === null ? c.red : c.ink }));
      const steps = [['Impute', f.st >= 1 ? `median = ${f2(f.med, 0)}` : 'not fitted'], ['Scale', f.st >= 2 ? `mean ${f2(f.mean, 1)}, sd ${f2(f.sd, 2)}` : 'not fitted'], ['One hot', f.st >= 3 ? 'basic plus premium' : 'not fitted'], ['Model', f.st >= 3 ? 'trained' : 'not fitted']];
      steps.forEach(([n, s], i) => {
        const x = 14 + i * 146, on = f.st >= 5 && f.st - 5 === i;
        box(z, x, 150, 132, 56, '', { fill: on ? 'rgba(14,116,144,0.15)' : c.surf, stroke: on ? c.cv : c.line, w: on ? 2.5 : 1.5 });
        D.text(g, n, x + 10, 170, { s: 13, b: true, c: c.ink });
        D.text(g, s, x + 10, 192, { s: 10, mono: true, c: f.st >= i + 1 || (i === 3 && f.st >= 3) ? c.green : c.ink2 });
        if (i < 3) D.arrow(g, x + 134, 178, x + 144, 178, c.ink2, 1.5, 5);
      });
      if (f.st >= 4) {
        head(z, 'New row as it moves through', 14, 236);
        const vals = [`tenure ${f.t === null ? 'missing' : f.t}, ${f.plan}`, `tenure ${f2(f.t1, 0)}`, `z = ${nf(f.z)}`, `[${f.oh.join(', ')}]`, `p = ${f2(f.prob, 2)}`];
        vals.forEach((v, i) => { if (f.st >= 4 + i) box(z, 14 + i * 116, 250, 108, 34, v, { s: 11, mono: true, fill: i === 4 ? c.bg : c.surf }); });
      }
      D.text(g, 'fit learns from training rows only', 360, 40, { s: 11, c: c.ink2 });
      D.text(g, 'predict reuses what fit learned', 360, 58, { s: 11, c: c.ink2 });
    }
  });

  trace('mlleak', {
    title: 'Leakage: a step that sees the test rows makes noise look useful',
    sub: '100 rows of pure random numbers in 5000 columns, with random labels, so no model can honestly beat 50 percent. Choosing the 20 “best” columns is a step that learns from labels. Watch which rows it is allowed to see in 5 fold cross validation.',
    W: 600, H: 330,
    params: [
      { k: 'way', label: 'Where the column choice happens', type: 'select', v: 'wrong', opts: [['wrong', 'Before cross validation, on all rows'], ['right', 'Inside the pipeline, on each training fold']] }
    ],
    tips: [
      { t: 'Choosing columns on all rows first: the test rows helped pick the columns, so the score is a fantasy.', set: { way: 'wrong' }, play: true },
      { t: 'Inside the pipeline: each fold picks its own columns from its 80 training rows, and the honest score of about 50 percent appears.', set: { way: 'right' }, play: true }
    ],
    frames(p) {
      const wrong = p.way === 'wrong', fr = [{ k: -1, wrong, say: 'The 100 rows are split into 5 folds of 20. Each fold takes one turn as the test set.' }];
      if (wrong) fr.push({ k: -1, sel: true, wrong, say: 'First, SelectKBest looks at <b>all 100 rows</b> and their labels, and keeps the 20 columns that happen to match the labels best.' });
      for (let k = 0; k < 5; k++) fr.push({ k, wrong, sel: wrong, say: wrong ? `Fold ${k + 1}: train on 80 rows, test on 20. But the 20 test rows already helped choose the columns.` : `Fold ${k + 1}: the pipeline chooses 20 columns using only the 80 training rows (blue), then tests on the 20 unseen rows (orange).` });
      fr.push({ k: 5, wrong, sel: wrong, say: wrong ? 'Average accuracy <b>0.85</b> on pure noise (from the program below). The model learned nothing real, the selection step peeked at the answers.' : 'Average accuracy <b>0.48</b> (from the program below): the honest answer for random data. Put every step that learns from data inside the pipeline.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, '100 rows in 5 folds', 14, 24);
      for (let k = 0; k < 5; k++) {
        const y = 40 + k * 44, test = k === f.k, train = f.k >= 0 && f.k < 5 && !test;
        box(z, 14, y, 200, 34, `rows ${k * 20 + 1} to ${k * 20 + 20}`, { s: 12, fill: test ? 'rgba(234,88,12,0.2)' : (train ? 'rgba(37,99,235,0.15)' : c.surf), stroke: test ? c.orange : (train ? c.accent : c.line) });
      }
      box(z, 260, 60, 320, 70, '', { fill: c.bg });
      D.text(g, 'Column choice (SelectKBest, k = 20)', 272, 82, { s: 12, b: true, c: c.ink });
      D.text(g, f.sel ? 'learned from: all 100 rows, test rows included' : (f.k >= 0 && f.k < 5 ? 'learned from: the 80 training rows of this fold' : 'learned from: not yet'), 272, 108, { s: 11, c: f.sel ? c.red : c.ink2 });
      if (f.k === 5) box(z, 260, 160, 320, 60, `cross validation accuracy ${f.wrong ? '0.85' : '0.48'}`, { s: 15, b: true, mono: true, fill: f.wrong ? 'rgba(220,38,38,0.15)' : 'rgba(22,163,74,0.15)', stroke: f.wrong ? c.red : c.green });
      D.text(g, 'blue: training rows   orange: test rows', 260, 300, { s: 10, c: c.ink2 });
      D.text(g, 'honest accuracy on random labels: about 0.5', 260, 316, { s: 10, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   MLOps 2.2  serving: one HTTP request through a model API, and online against batch prediction
   ===================================================================================================== */
(() => {
  const { trace, D, f2, head, box } = MLZ;
  const REQ = {
    good: { body: '{"features": [5.9, 3.0, 5.1, 1.8]}', ok: true, out: '{"class": "virginica", "probability": 0.703}' },
    text: { body: '{"features": [5.9, "wide"]}', ok: false, out: '{"error": "send {\\"features\\": [four numbers]}"}' },
    get: { body: '(GET, no body)', ok: false, method: 'GET', out: '405 Method Not Allowed' }
  };

  trace('mlrequest', {
    title: 'One request through a model API',
    sub: 'A client (a website, an app or another service) sends JSON over HTTP. The web framework routes it to a function, the input is checked, the pipeline that was loaded once at start up predicts, and JSON goes back with a status code.',
    W: 600, H: 330,
    params: [
      { k: 'req', label: 'Request', type: 'select', v: 'good', opts: [['good', 'POST /predict with four numbers'], ['text', 'POST /predict with a word instead of a number'], ['get', 'GET /predict']] }
    ],
    tips: [
      { t: 'A word instead of a number: validation stops it with status 422 before the model is called.', set: { req: 'text' }, play: true },
      { t: 'GET instead of POST: the route only accepts POST, so the framework answers 405 without running your code.', set: { req: 'get' }, play: true }
    ],
    frames(p) {
      const R = REQ[p.req], S = (k, say, extra = {}) => ({ k, R, say, ...extra });
      const fr = [S(0, 'At start up the server loads the saved pipeline into memory once, not on every request.'),
        S(1, `The client sends <b>${R.method || 'POST'} /predict</b> with body ${R.body}.`)];
      if (R.method === 'GET') { fr.push(S(2, 'The router finds /predict but it only allows POST, so it answers <b>405 Method Not Allowed</b>.', { stop: 2, code: 405 })); return fr; }
      fr.push(S(2, 'The router matches POST /predict and calls the predict function.'));
      if (!R.ok) { fr.push(S(3, 'Validation: "wide" is not a number and there are only 2 values. The function returns <b>422</b> with an error message. The model never sees bad data.', { stop: 3, code: 422 })); return fr; }
      fr.push(S(3, 'Validation passes: four numbers.'));
      fr.push(S(4, 'The pipeline scales the four numbers and the model computes class probabilities in well under a millisecond.'));
      fr.push(S(5, `The function returns <b>200</b> with ${R.out}.`, { code: 200 }));
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, names = ['Load model at start up', 'Client sends JSON', 'Router', 'Validate input', 'Pipeline predicts', 'JSON response'];
      names.forEach((n, i) => {
        const x = 14 + (i % 3) * 196, y = i < 3 ? 40 : 150, seen = i <= f.k, on = i === f.k, bad = f.stop === i;
        box(z, x, y, 176, 60, n, { s: 12, b: on, fill: bad ? 'rgba(220,38,38,0.15)' : (seen ? 'rgba(22,163,74,0.12)' : c.surf), stroke: bad ? c.red : (on ? c.cv : c.line), w: on ? 2.5 : 1.5 });
        if (i < 5 && i !== 2) D.arrow(g, x + 178, y + 30, x + 194, y + 30, c.ink2, 1.5, 5);
      });
      D.arrow(g, 14 + 2 * 196 + 88, 102, 14 + 88, 148, c.ink2, 1.5, 6);
      if (f.k >= 1) { head(z, 'Request', 14, 246); D.text(g, `${f.R.method || 'POST'} /predict  ${f.R.body}`, 14, 268, { s: 11, mono: true, c: c.ink }); }
      if (f.code) { head(z, 'Response', 14, 294); D.text(g, `${f.code}  ${f.code === 200 ? f.R.out : (f.code === 405 ? 'Method Not Allowed' : f.R.out)}`, 14, 316, { s: 11, mono: true, b: true, c: f.code === 200 ? c.green : c.red }); }
    }
  });

  trace('mlservemodes', {
    title: 'Online against batch prediction',
    sub: 'Online serving answers each request the moment it arrives. Batch serving collects the work and scores everything in one run, for example at 2 am, and stores the answers for later. Eight customer events arrive during the day.',
    W: 600, H: 330,
    params: [
      { k: 'mode', label: 'Serving mode', type: 'select', v: 'online', opts: [['online', 'Online: a web API answers each request'], ['batch', 'Batch: score everything at night']] }
    ],
    tips: [
      { t: 'Online: each answer is ready in milliseconds and uses the newest data, but a server must be running all the time.', set: { mode: 'online' }, play: true },
      { t: 'Batch: the answers wait until the nightly run, but one big run is cheaper and simpler to operate.', set: { mode: 'batch' }, play: true }
    ],
    frames(p) {
      const times = [8.5, 9.25, 11, 12.5, 14, 15.75, 18, 21.5], fr = [{ n: 0, mode: p.mode, say: 'A day from 6 am to 6 am the next morning. Each dot is a customer event that needs a prediction.' }];
      times.forEach((t, i) => fr.push({ n: i + 1, mode: p.mode, times, say: p.mode === 'online' ? `Event at ${Math.floor(t)}:${t % 1 ? String(Math.round((t % 1) * 60)).padStart(2, '0') : '00'}: the API answers about 20 milliseconds later.` : `Event at ${Math.floor(t)}:${t % 1 ? String(Math.round((t % 1) * 60)).padStart(2, '0') : '00'}: it is stored and waits for the nightly run.` }));
      fr.push({ n: 8, mode: p.mode, times, night: p.mode === 'batch', say: p.mode === 'online' ? 'Every answer came almost at once. Use online serving when the answer is needed during the visit: fraud checks, search ranking, recommendations on the page.' : 'At 2:00 one job scores all 8 events together and writes the answers to a table. The 8:30 event waited about 17.5 hours. Use batch when tomorrow is soon enough: churn lists, weekly forecasts, email campaigns.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, X = h => 30 + (h - 6) / 24 * 540;
      D.line(g, X(6), 150, X(30), 150, c.ink2, 2);
      [6, 9, 12, 15, 18, 21, 24, 27, 30].forEach(h => { D.line(g, X(h), 145, X(h), 155, c.ink2, 1); D.text(g, `${h % 24}:00`, X(h), 172, { a: 'center', s: 10, c: c.ink2 }); });
      if (f.mode === 'batch') { D.line(g, X(26), 60, X(26), 240, c.purple, 2, [5, 4]); D.text(g, 'nightly run 2:00', X(26), 52, { a: 'center', s: 11, b: true, c: c.purple }); }
      (f.times || []).slice(0, f.n).forEach((t, i) => {
        D.circle(g, X(t), 150, 6, { fill: c.cv });
        if (f.mode === 'online') { D.line(g, X(t), 150, X(t), 100, c.green, 2); D.text(g, 'answer', X(t), 94 - (i % 2) * 14, { a: 'center', s: 9, c: c.green }); }
        else if (f.night) { g.save(); g.strokeStyle = c.orange; g.lineWidth = 1.2; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(X(t), 158); g.quadraticCurveTo((X(t) + X(26)) / 2, 230 + i * 6, X(26), 160); g.stroke(); g.restore(); }
      });
      D.text(g, f.mode === 'online' ? 'green: answer within milliseconds' : 'orange: waiting time until the nightly run', 30, 300, { s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   MLOps 2.3  Docker and CI/CD: the layer cache, and a CI/CD pipeline that stops at the first failure
   ===================================================================================================== */
(() => {
  const { trace, D, head, box } = MLZ;
  /* step times in seconds come from real builds of the chapter's project (python:3.14-slim, 2026) */
  const ORDERS = {
    good: [['FROM python:3.14-slim', [], 0], ['WORKDIR /app', [], 0], ['COPY requirements.txt .', ['reqs'], 0], ['RUN pip install -r requirements.txt', [], 18], ['COPY train.py app.py ./', ['code'], 0], ['RUN python train.py', [], 1.6], ['RUN useradd appuser', [], 0.1]],
    bad: [['FROM python:3.14-slim', [], 0], ['WORKDIR /app', [], 0], ['COPY . .', ['reqs', 'code'], 0.4], ['RUN pip install -r requirements.txt', [], 18.6], ['RUN python train.py', [], 1.2]]
  };
  const CH = { code: 'app.py', reqs: 'requirements.txt', none: 'nothing' };
  const sec = v => (v < 0.05 ? '0 s' : `${v.toFixed(1)} s`);

  trace('mllayers', {
    title: 'The Docker layer cache',
    sub: 'Each Dockerfile instruction makes one layer. On a rebuild Docker reuses a layer from its cache unless the instruction or the files it copies changed. Once one layer runs again, every layer above it runs again too. The times come from real builds of this chapter&rsquo;s project.',
    W: 600, H: 340,
    params: [
      { k: 'order', label: 'Dockerfile order', type: 'select', v: 'good', opts: [['good', 'Good: requirements first, code later'], ['bad', 'Bad: COPY . . before pip install']] },
      { k: 'change', label: 'You changed', type: 'select', v: 'code', opts: [['code', 'app.py (your code)'], ['reqs', 'requirements.txt'], ['none', 'Nothing']] }
    ],
    tips: [
      { t: 'Bad order and a one line code change: COPY . . sees a changed file, so pip install runs again for about 18 seconds.', set: { order: 'bad', change: 'code' }, play: true },
      { t: 'Changing requirements.txt rebuilds pip install in both orders. That is expected, because the packages really changed.', set: { order: 'good', change: 'reqs' }, play: true }
    ],
    frames(p) {
      const S = ORDERS[p.order], fr = [{ S, n: 0, runs: [], say: `A rebuild after you changed <b>${CH[p.change]}</b>. Docker checks the layers from the bottom up.` }];
      let dirty = false, total = 0;
      const runs = [];
      S.forEach(([ins, deps, t], i) => {
        const why = deps.includes(p.change) ? 'its files changed' : (dirty ? 'a layer below it ran again' : '');
        if (why) dirty = true;
        runs.push(!!why); if (why) total += t;
        fr.push({ S, n: i + 1, runs: runs.slice(), say: why ? `<b>${ins}</b> runs again because ${why} (${sec(t)}).` : `<b>${ins}</b> is unchanged: CACHED.` });
      });
      const end = p.change === 'none' ? 'Nothing changed, so every layer came from the cache and the build finished almost at once.'
        : `Steps that ran again took about <b>${sec(total)}</b>. ${p.order === 'bad' && p.change === 'code' ? 'One line of code cost a full reinstall. Copy requirements.txt and install first, then copy the code.' : (p.order === 'good' && p.change === 'code' ? 'The slow pip install layer was reused, so a code change rebuilds in seconds.' : 'New packages need a new install whatever the order.')}`;
      fr.push({ S, n: S.length, runs: runs.slice(), total, done: true, say: end });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, n = f.S.length, H = 36, y0 = 30 + (7 - n) * H;
      head(z, 'Image layers (the first instruction is at the bottom)', 14, 20);
      f.S.forEach(([ins, , t], i) => {
        const y = y0 + (n - 1 - i) * (H + 4), seen = i < f.n, run = f.runs[i];
        box(z, 14, y, 390, H, ins, { mono: true, s: 12, fill: !seen ? c.surf : (run ? 'rgba(234,88,12,0.18)' : 'rgba(22,163,74,0.15)'), stroke: !seen ? c.line : (run ? c.orange : c.green), w: i === f.n - 1 ? 2.5 : 1.5 });
        if (seen) D.text(g, run ? `runs again  ${sec(t)}` : 'CACHED', 416, y + H / 2 + 4, { s: 12, b: true, c: run ? c.orange : c.green });
      });
      if (f.done) D.text(g, `time for the steps that ran: ${sec(f.total || 0)}`, 14, 326, { s: 13, b: true, c: c.ink });
    }
  });

  const STAGES = ['git push', 'Install packages', 'Train the model', 'Run pytest (7 tests)', 'Build the image', 'Smoke test container', 'Push image (main only)', 'Deploy'];
  trace('mlcipipe', {
    title: 'A CI/CD pipeline for a model',
    sub: 'Every push starts the pipeline on a clean machine. Continuous integration (CI) installs, trains and tests. Continuous delivery (CD) builds the image, checks that the container really answers, pushes it to a registry and deploys it. The first failing stage stops everything after it.',
    W: 600, H: 330,
    params: [
      { k: 'run', label: 'What happens in this push', type: 'select', v: 'pass', opts: [['pass', 'Everything is fine'], ['gate', 'The new model is less accurate'], ['smoke', 'The container does not start']] }
    ],
    tips: [
      { t: 'A worse model: the accuracy gate test fails, so no image is built and the old model keeps serving.', set: { run: 'gate' }, play: true },
      { t: 'All tests pass but the container crashes at start up (for example a missing file). Only the smoke test catches this.', set: { run: 'smoke' }, play: true }
    ],
    frames(p) {
      const fail = { pass: -1, gate: 3, smoke: 5 }[p.run];
      const say = [
        'You push a commit. GitHub Actions starts a fresh Ubuntu machine and checks out the code.',
        'pip install -r requirements-dev.txt installs the pinned versions, the same ones as on your computer.',
        p.run === 'gate' ? 'python train.py trains the new model. Its test accuracy is 0.84 this time.' : 'python train.py trains the model and saves it with its metadata (test accuracy 0.9111).',
        p.run === 'gate' ? 'pytest: test_accuracy_gate fails because 0.84 is below the 0.90 gate. The run turns red and the pull request cannot be merged.' : 'pytest: all 7 tests pass (API, bad input, accuracy gate, invariance, direction, latency).',
        'docker build makes the image. The pip layer comes from the cache when requirements.txt did not change.',
        p.run === 'smoke' ? 'The smoke test starts the container and calls /health 20 times. It never answers, because the model file is missing from the image. The run turns red.' : 'The smoke test starts the container and calls /health and /predict with curl. Both answer.',
        'On main only, the image is pushed to the registry, tagged with the commit id, so every version can be found again.',
        'The deploy step tells the server to run the new image. If it misbehaves, rolling back means running the previous tag.'];
      const fr = [];
      for (let i = 0; i < STAGES.length; i++) {
        fr.push({ k: i, fail, say: say[i] });
        if (i === fail) break;
      }
      fr.push({ k: fail >= 0 ? fail : STAGES.length - 1, fail, done: true, say: fail >= 0 ? `Stopped at <b>${STAGES[fail]}</b>. Nothing after it ran, so the broken version never reached users. Fix it and push again.` : 'Green from push to deploy. The same steps run the same way on every push, which is the point of CI/CD.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      STAGES.forEach((n, i) => {
        const x = 14 + (i % 4) * 147, y = i < 4 ? 40 : 186, bad = i === f.fail && f.k >= i, ok = i <= f.k && !bad, skip = f.done && f.fail >= 0 && i > f.fail;
        box(z, x, y, 130, 60, n, { s: 12, b: i === f.k, fill: bad ? 'rgba(220,38,38,0.15)' : (ok ? 'rgba(22,163,74,0.14)' : c.surf), stroke: bad ? c.red : (ok ? c.green : c.line), w: i === f.k ? 2.5 : 1.5, dash: skip ? [4, 4] : undefined });
        if (ok || bad) D.text(g, bad ? 'failed' : 'passed', x + 65, y + 78, { a: 'center', s: 11, b: true, c: bad ? c.red : c.green });
        else if (skip) D.text(g, 'skipped', x + 65, y + 78, { a: 'center', s: 11, c: c.ink2 });
        if (i % 4 !== 3) D.arrow(g, x + 131, y + 30, x + 145, y + 30, c.ink2, 1.5, 5);
      });
      D.arrow(g, 14 + 3 * 147 + 65, 128, 14 + 65, 184, c.ink2, 1.5, 6);
      head(z, 'CI: install, train, test', 14, 30, { s: 11 }); head(z, 'CD: build, check, ship', 170, 182, { s: 11 });
      if (f.done) D.text(g, f.fail >= 0 ? 'Pipeline red: the change is blocked.' : 'Pipeline green: the new version is live.', 14, 316, { s: 13, b: true, c: f.fail >= 0 ? c.red : c.green });
    }
  });
})();

/* =====================================================================================================
   MLOps 3.1  experiment tracking and the model registry: the winner's curse, and aliases that move
   ===================================================================================================== */
(() => {
  const { trace, D, head, box, rng } = MLZ;
  const gauss = R => { const u = Math.max(R(), 1e-12), v = R(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };

  trace('mlruns', {
    title: 'Many tracked runs and the winner&rsquo;s curse',
    sub: 'Every dot is one tracked run. Its true quality is hidden. What you see is its score on one validation set, which adds a little luck. Picking the highest dot also picks the luckiest run, so its score on a fresh test set is usually lower.',
    W: 600, H: 330,
    params: [{ k: 'n', label: 'Runs compared on one validation set', type: 'select', v: '20', opts: [['5', '5 runs'], ['20', '20 runs'], ['100', '100 runs']] }],
    tips: [
      { t: '100 runs: the best validation score climbs, but the same model on fresh data does not. The gap grows with the number of runs.', set: { n: '100' }, play: true },
      { t: '5 runs: little room for luck, so the winner&rsquo;s validation and test scores are close.', set: { n: '5' }, play: true }
    ],
    frames(p) {
      const n = +p.n, R = rng(9), runs = Array.from({ length: n }, () => { const q = 0.80 + 0.05 * R(); return { q, v: q + 0.02 * gauss(R), t: q }; });
      const batch = Math.max(1, Math.ceil(n / 6)), fr = [{ runs, k: 0, say: `${n} runs with different settings, all scored on the same validation set.` }];
      for (let k = batch; k < n + batch; k += batch) { const m = Math.min(k, n); fr.push({ runs, k: m, say: `${m} of ${n} runs logged. The tracker stores the settings and the validation score of each.` }); if (m === n) break; }
      let b = 0; runs.forEach((r, i) => { if (r.v > runs[b].v) b = i; });
      fr.push({ runs, k: n, best: b, say: `The best validation score is <b>${runs[b].v.toFixed(3)}</b> (run ${b + 1}). That run becomes the champion.` });
      fr.push({ runs, k: n, best: b, test: true, say: `On a large fresh test set the same model scores <b>${runs[b].t.toFixed(3)}</b>, a drop of ${(runs[b].v - runs[b].t).toFixed(3)}. Report the champion on untouched test data, once.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, n = f.runs.length, X = i => 50 + (i + 0.5) / n * 530, Y = a => 290 - (a - 0.74) / 0.18 * 260;
      D.line(g, 50, 290, 580, 290, c.ink2, 1); D.line(g, 50, 290, 50, 30, c.ink2, 1);
      [0.75, 0.80, 0.85, 0.90].forEach(a => { D.text(g, a.toFixed(2), 44, Y(a) + 4, { a: 'right', s: 10, c: c.ink2 }); D.line(g, 50, Y(a), 580, Y(a), c.line, 0.5); });
      D.text(g, 'run number', 315, 312, { a: 'center', s: 11, c: c.ink2 }); head(z, 'validation score', 56, 24, { s: 11 });
      f.runs.slice(0, f.k).forEach((r, i) => D.circle(g, X(i), Y(r.v), n > 50 ? 3 : 5, { fill: i === f.best ? c.green : c.cv }));
      if (f.best !== undefined) {
        const r = f.runs[f.best]; g.save(); g.strokeStyle = c.green; g.lineWidth = 2; g.beginPath(); g.arc(X(f.best), Y(r.v), 10, 0, 7); g.stroke(); g.restore();
        if (f.test) { D.line(g, X(f.best), Y(r.v), X(f.best), Y(r.t), c.orange, 1.5, [3, 3]); g.save(); g.strokeStyle = c.orange; g.lineWidth = 2.5; g.beginPath(); g.arc(X(f.best), Y(r.t), 6, 0, 7); g.stroke(); g.restore();
          D.text(g, 'green: champion on validation, orange ring: the same model on fresh test data', 56, 44, { s: 11, c: c.ink2 }); }
      }
    }
  });

  const VERS = [{ d: 'tree depth 2', auc: 0.9555 }, { d: 'stump depth 1', auc: 0.8844 }, { d: 'logistic C=1', auc: 0.9942 }];
  trace('mlregistry', {
    title: 'A model registry: fixed versions, moving aliases',
    sub: 'Each registered version is frozen and keeps its number. Aliases such as champion and challenger are labels that point at a version. The service always loads the champion, so promoting or rolling back means moving one label. The scores are holdout AUCs from the chapter&rsquo;s program.',
    W: 600, H: 330,
    params: [{ k: 'margin', label: 'Promotion gate: beat the champion by', type: 'select', v: '0.002', opts: [['0.002', '0.002 AUC'], ['0.05', '0.05 AUC (strict)']] }],
    tips: [
      { t: 'Strict gate: v3 is better by 0.039, which is less than 0.05, so v1 stays champion. Gates trade safety against progress.', set: { margin: '0.05' }, play: true },
      { t: 'Normal gate: v3 is promoted, then rolled back after an incident without any retraining.', set: { margin: '0.002' }, play: true }
    ],
    frames(p) {
      const m = +p.margin, fr = [];
      const st = (n, champ, chall, say, extra = {}) => fr.push({ n, champ, chall, say, ...extra });
      st(1, 1, 0, 'Register v1 (tree depth 2, AUC 0.9555). There is no champion yet, so v1 becomes champion and the service loads it.');
      st(2, 1, 2, 'Register v2 (stump, AUC 0.8844) as challenger. It is compared with the champion on the same holdout data.');
      st(2, 1, 0, `v2 is worse than v1 (0.8844 against 0.9555), so it is not promoted. It stays in the registry for the record.`, { rej: 2 });
      st(3, 1, 3, 'Register v3 (logistic regression, AUC 0.9942) as challenger.');
      const ok = 0.9942 >= 0.9555 + m;
      if (!ok) { st(3, 1, 0, `v3 is better by 0.0387, but the gate asks for ${m}. Not promoted, v1 stays champion. A strict gate also blocks real improvements.`, { rej: 3, done: true }); return fr; }
      st(3, 3, 0, 'v3 beats v1 by 0.0387, more than the 0.002 gate. The champion alias moves to v3 and the service loads v3 on its next reload.');
      st(3, 1, 0, 'An incident: v3 misbehaves on live traffic. Rollback is one action: move champion back to v1. Nothing is retrained or rebuilt.', { incident: 3, done: true });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, 'Registered versions of breast-cancer-classifier', 14, 24);
      VERS.slice(0, f.n).forEach((v, i) => {
        const x = 24 + i * 192, y = 120, isC = f.champ === i + 1, isCh = f.chall === i + 1, bad = f.rej === i + 1 || f.incident === i + 1;
        box(z, x, y, 168, 92, '', { fill: isC ? 'rgba(22,163,74,0.14)' : (bad ? 'rgba(220,38,38,0.10)' : c.surf), stroke: isC ? c.green : (isCh ? c.purple : (bad ? c.red : c.line)), w: isC || isCh ? 2.5 : 1.5 });
        D.text(g, `v${i + 1}`, x + 84, y + 28, { a: 'center', s: 18, b: true, c: c.ink });
        D.text(g, v.d, x + 84, y + 52, { a: 'center', s: 12, c: c.ink2 });
        D.text(g, `AUC ${v.auc.toFixed(4)}`, x + 84, y + 74, { a: 'center', s: 12, b: true, c: c.ink });
        if (isC) { box(z, x + 24, y - 52, 120, 30, 'champion', { s: 13, b: true, fill: c.green, stroke: c.green, c: '#fff' }); D.arrow(g, x + 84, y - 22, x + 84, y - 2, c.green, 2, 6); }
        if (isCh) { box(z, x + 24, y - 52, 120, 30, 'challenger', { s: 13, b: true, fill: c.purple, stroke: c.purple, c: '#fff' }); D.arrow(g, x + 84, y - 22, x + 84, y - 2, c.purple, 2, 6); }
        if (f.incident === i + 1) D.text(g, 'incident', x + 84, y + 112, { a: 'center', s: 12, b: true, c: c.red });
        if (f.rej === i + 1) D.text(g, 'not promoted', x + 84, y + 112, { a: 'center', s: 12, b: true, c: c.red });
      });
      D.text(g, `The service loads: models:/breast-cancer-classifier@champion = v${f.champ}`, 14, 300, { s: 13, b: true, mono: true, c: c.ink });
    }
  });
})();
