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
    sub: 'Project A is new and needs NumPy 2.4. Project B is an old model that was trained with NumPy 1.26. Watch what happens to each project when you install the second one’s packages.',
    W: 600, H: 330,
    params: [
      { k: 'mode', label: 'Where packages go', type: 'select', v: 'global', opts: [['global', 'One shared install for everything'], ['venv', 'A separate .venv in each project']] }
    ],
    tips: [
      { t: 'One shared install: installing project B’s requirements replaces NumPy 2.4 with 1.26, and project A stops working.', set: { mode: 'global' }, play: true },
      { t: 'A .venv per project: each project keeps its own NumPy, so both keep working.', set: { mode: 'venv' }, play: true }
    ],
    frames(p) {
      const g = p.mode === 'global';
      const S = (a, b, ok, say, extra = {}) => ({ g, a, b, ok, say, ...extra });
      const fr = [S(null, null, [null, null], g ? 'There is one place for packages, shared by every project on the computer.' : 'Each project folder has its own .venv folder with its own packages.')];
      fr.push(S({ numpy: '2.4.6', pandas: '3.0.2' }, g ? null : {}, [true, null], 'Install project A: <b>pip install numpy==2.4.6 pandas==3.0.2</b>. Project A runs.'));
      if (g) {
        fr.push(S({ numpy: '1.26.4', pandas: '3.0.2' }, null, [true, true], 'Install project B: <b>pip install numpy==1.26.4</b>. pip removes NumPy 2.4.6 to make room, because one place can hold only one version.', { swap: true }));
        fr.push(S({ numpy: '1.26.4', pandas: '3.0.2' }, null, [false, true], 'Project B runs, but project A now fails: pandas 3.0 on Python 3.14 needs NumPy 2.3.3 or newer. Fixing A breaks B again. This is called <b>dependency hell</b>.'));
      } else {
        fr.push(S({ numpy: '2.4.6', pandas: '3.0.2' }, { numpy: '1.26.4' }, [true, true], 'Activate project B’s .venv and install <b>numpy==1.26.4</b>. It goes into B’s folder only.'));
        fr.push(S({ numpy: '2.4.6', pandas: '3.0.2' }, { numpy: '1.26.4' }, [true, true], 'Both projects run with the exact versions they need.'));
      }
      fr.push(S(fr[fr.length - 1].a, fr[fr.length - 1].b, fr[fr.length - 1].ok, g ? 'The fix is a virtual environment per project, plus a requirements.txt so anyone can rebuild the same set.' : 'Write each set down with <b>pip freeze &gt; requirements.txt</b>, so a teammate or a server can rebuild it with pip install -r requirements.txt.', { freeze: !g }));
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const proj = (x, name, ok) => {
        box(z, x, 20, 200, 60, '', { fill: ok === false ? 'rgba(220,38,38,0.15)' : (ok ? 'rgba(22,163,74,0.15)' : c.surf), stroke: ok === false ? c.red : (ok ? c.green : c.line) });
        D.text(g, name, x + 12, 44, { s: 13, b: true, c: c.ink });
        D.text(g, ok === null ? 'not installed yet' : (ok ? 'runs' : 'fails to import'), x + 12, 66, { s: 12, mono: true, c: ok === false ? c.red : (ok ? c.green : c.ink2) });
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
