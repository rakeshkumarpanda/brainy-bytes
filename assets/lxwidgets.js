/* ===== Unix and Linux playful step animations (assets/lxwidgets.js) =====
   Each animation is a PK.widget from assets/playkit.js (the playful DSA style: Pip the guide, tonal cells that change
   shape on a spring, confetti on success), played by the VIZ player from assets/viz.js. That player has Play, Step,
   Back, a scrubber, speed and Reset, and assets/voiceteach.js reads each step aloud with "Voice on".
   A lesson places one with <div class="viz" data-viz="pk" data-pk="name" data-cfg='{"input key": value}'>.

   Extra layers for this subject, on top of the playkit ones:
     {t: 'fs', label, tree: [name, [children]] , cls: {'/path': cls}, tag: {'/path': 'small text'}}   a file tree
     {t: 'term', label, lines: [['c', 'command'] | ['o', 'output'] | ['e', 'error']]}                   a terminal
     {t: 'flow', label, items: [[text, small, cls]], arrows: [cls]}                                       boxes in a row
     {t: 'perm', label, mode: 0o754, cls: {bit index 0..8: cls}, special}                                 rwx groups
   The bottom of the file wires the Copy buttons of the lxkit.run() terminal boxes. ===== */
(() => {
  const D = PK.draw, esc = VIZ.kit.esc;
  const def = (name, fn) => { PK.defs[name] = fn; };
  const cfgOf = el => { try { return JSON.parse(el.dataset.cfg || '{}'); } catch (e) { return {}; } };
  /* a widget whose input values can be set by the lesson through data-cfg */
  const W = (el, o) => { const c = cfgOf(el); (o.inputs || []).forEach(f => { if (c[f.k] !== undefined) f.val = c[f.k]; }); return PK.widget(el, o); };

  /* ---------- layers ---------- */
  D.fs = L => {
    const cls = L.cls || {}, tag = L.tag || {};
    const walk = (node, path) => {
      const [name, kids] = node, p = path === '' ? (name === '/' ? '/' : name) : (path === '/' ? '/' : path + '/') + name;
      const icon = kids ? '📁' : /\.(sh)$/.test(name) ? '⚙️' : '📄';
      return `<li><span class="${cls[p] || ''}">${icon} ${esc(name)}</span>${tag[p] ? `<small>${esc(tag[p])}</small>` : ''}${kids && kids.length ? `<ul>${kids.map(k => walk(k, p)).join('')}</ul>` : ''}</li>`;
    };
    return `${L.label ? `<div class="pk-lab">${L.label}</div>` : ''}<ul class="pk-fs">${walk(L.tree, '')}</ul>`;
  };
  D.term = L => `${L.label ? `<div class="pk-lab">${L.label}</div>` : ''}<div class="pk-term">${(L.lines || []).map(([k, s]) => `<div class="${k}">${k === 'h' ? `<span class="h">${esc(s)}</span>` : esc(s)}</div>`).join('') || '<span class="pk-empty">empty screen</span>'}</div>`;
  D.flow = L => {
    const items = L.items || [], ar = L.arrows || [];
    return `${L.label ? `<div class="pk-lab">${L.label}</div>` : ''}<div class="pk-flow">${items.map(([t, s, c], i) => `${i ? `<span class="pk-arr ${ar[i - 1] || ''}">${L.back ? '⇄' : '→'}</span>` : ''}<div class="pk-box ${c || ''}">${esc(t)}${s ? `<small>${esc(s)}</small>` : ''}</div>`).join('')}</div>`;
  };
  D.perm = L => {
    const m = L.mode, cls = L.cls || {}, names = ['owner (u)', 'group (g)', 'others (o)'], ch = 'rwx';
    const groups = [0, 1, 2].map(g => {
      const cells = [0, 1, 2].map(b => { const bit = 8 - (g * 3 + b), on = (m >> bit) & 1; return `<div class="pk-slot"><div class="pk-cell ${cls[g * 3 + b] || (on ? 'cur' : 'ghost')}">${on ? ch[b] : '-'}</div><span class="pk-idx">${[4, 2, 1][b]}</span></div>`; }).join('');
      return `<div class="pk-pg"><span>${names[g]}</span><div class="pk-row">${cells}</div><b class="pk-pv">${(m >> (6 - g * 3)) & 7}</b></div>`;
    }).join('');
    return `${L.label ? `<div class="pk-lab">${L.label}</div>` : ''}<div class="pk-perm">${groups}</div>`;
  };

  /* a text buffer with a cursor, for the vim animation */
  D.buf = L => {
    const lines = L.lines.length ? L.lines : [''];
    const rows = lines.map((s, r) => {
      const chars = [...(s.length ? s : ' ')].map((ch, c) => `<span class="${r === L.r && c === Math.min(L.c, Math.max(s.length - (L.mode === 'INSERT' ? 0 : 1), 0)) ? (L.mode === 'INSERT' ? 'ins' : 'cur') : ''}">${esc(ch)}</span>`).join('');
      const tail = L.mode === 'INSERT' && r === L.r && L.c >= s.length && s.length ? '<span class="ins"> </span>' : '';
      return `<div class="${r === L.r ? 'on' : ''}"><i>${r + 1}</i>${chars}${tail}</div>`;
    }).join('');
    return `${L.label ? `<div class="pk-lab">${L.label}</div>` : ''}<div class="pk-buf">${rows}<div class="pk-bufbar"><b>${L.mode === 'INSERT' ? '-- INSERT --' : L.mode === 'CMD' ? ':' + esc(L.cmd || '') : 'NORMAL'}</b><span>${L.r + 1},${L.c + 1}</span>${L.reg ? `<span>register: ${esc(L.reg)}</span>` : ''}</div></div>`;
  };

  /* ---------- 1.1 Meet Unix and Linux ---------- */
  const HISTORY = [
    [1969, 'Ken Thompson and Dennis Ritchie start Unix at Bell Labs, on a spare PDP-7 computer.'],
    [1973, 'Unix is rewritten in the new C language, so it can move to other computers.'],
    [1978, 'The University of California, Berkeley ships its first Berkeley Software Distribution (BSD) of Unix tools.'],
    [1983, 'Richard Stallman announces the GNU project, a free Unix-like system.'],
    [1988, 'The first POSIX standard (IEEE 1003.1) says what every Unix-like system must offer.'],
    [1991, 'Linus Torvalds, a student in Helsinki, posts about his hobby kernel and releases Linux 0.01.'],
    [1992, 'Linux moves to the GNU General Public License, so anyone may use, change and share it.'],
    [1993, 'Debian and Slackware, two of the oldest distributions, are born.'],
    [1994, 'Linux 1.0 is released.'],
    [2004, 'Ubuntu is released and makes Linux friendly on the desktop.'],
    [2008, 'The first Android phone ships, with the Linux kernel inside.'],
    [2017, 'From November 2017, every one of the 500 fastest supercomputers in the world runs Linux.']
  ];
  def('lx-timeline', el => W(el, {
    title: 'Fifty years of Unix and Linux',
    sub: 'Type a year. Pip walks through history and stops at your year to show what existed then.',
    inputs: [{ k: 'year', label: 'Stop at year', type: 'num', val: 1991, min: 1969, max: 2026, w: 100 }],
    check: v => v.year < 1969 || v.year > 2026 ? 'Pick a year from 1969 to 2026.' : '',
    random: () => ({ year: 1969 + Math.floor(Math.random() * 58) }),
    frames: v => {
      const years = HISTORY.map(h => h[0]), fr = [];
      const row = (k, extra = {}) => ({ t: 'row', label: 'Timeline', cells: years, idx: false, cls: Object.assign(Object.fromEntries(years.map((y, i) => [i, i < k ? (y <= v.year ? 'yes' : 'done') : ''])), extra), small: true });
      fr.push({ msg: `Let us travel from 1969 to <b>${v.year}</b>. Each box is a big moment.`, mood: 'idle', layers: [row(0)] });
      for (let i = 0; i < HISTORY.length; i++) {
        const [y, what] = HISTORY[i];
        if (y > v.year) { fr.push({ msg: `<b>${y}</b> is after ${v.year}, so in ${v.year} this had not happened yet. We stop here.`, mood: 'sad', fx: 'shake', layers: [row(i, { [i]: 'no' })] }); break; }
        fr.push({ msg: `<b>${y}</b>: ${what}`, mood: y === 1991 ? 'wow' : 'look', fx: y === 1991 ? 'burst' : undefined, layers: [row(i, { [i]: 'look' })], vars: { year: y } });
      }
      const seen = HISTORY.filter(h => h[0] <= v.year).length;
      fr.push({ msg: `By ${v.year}, ${seen} of these ${HISTORY.length} moments had happened. ${v.year >= 1991 ? 'Linux already existed.' : 'Linux did not exist yet, but Unix did.'}`, mood: 'happy', fx: 'burst', layers: [row(seen)] });
      return fr;
    }
  }));

  def('lx-layers', el => W(el, {
    title: 'What happens when you type a command',
    sub: 'Type a command. Watch it travel down through the layers of the system to the hardware and back.',
    inputs: [{ k: 'cmd', label: 'Command', type: 'text', val: 'ls', w: 140 }],
    random: () => ({ cmd: ['ls', 'cat notes.txt', 'date', 'mkdir pics', 'whoami'][Math.floor(Math.random() * 5)] }),
    frames: v => {
      const cmd = String(v.cmd).trim() || 'ls', prog = cmd.split(/\s+/)[0];
      const hw = /^(cat|ls|mkdir|rm|cp|touch|less|head|tail)$/.test(prog) ? 'disk' : prog === 'date' ? 'clock chip' : 'memory';
      const call = { ls: 'getdents64', cat: 'read', mkdir: 'mkdir', rm: 'unlinkat', cp: 'read and write', touch: 'utimensat', date: 'clock_gettime', whoami: 'geteuid' }[prog] || 'read and write';
      const L = ['You', 'Terminal', 'Shell (bash)', prog, 'C library', 'Kernel', hw];
      const sm = ['types', 'shows text', 'reads the line', 'the program', 'glibc', 'system call', 'hardware'];
      const f = (k, back, extra) => ({ t: 'flow', label: 'Layers, from you to the hardware', items: L.map((x, i) => [x, sm[i], i === k ? (back ? 'yes' : 'look') : i < k || back && i > k ? 'cur' : '']), arrows: L.map((_, i) => i < k ? 'yes' : '') , ...extra });
      return [
        { msg: `You type <code>${esc(cmd)}</code> and press Enter.`, mood: 'idle', layers: [f(0)] },
        { msg: 'The <b>terminal</b> is only a window. It sends the letters you typed to the shell.', mood: 'look', layers: [f(1)] },
        { msg: `The <b>shell</b> reads the line, splits it into words, and finds the program <code>${esc(prog)}</code> in a folder listed in PATH, usually /usr/bin.`, mood: 'think', layers: [f(2)] },
        { msg: `The shell asks the kernel to start <code>${esc(prog)}</code> as a new process. Now ${esc(prog)} runs.`, mood: 'work', layers: [f(3)] },
        { msg: `${esc(prog)} cannot touch the hardware itself. It calls a function in the <b>C library</b>, which turns it into a system call.`, mood: 'look', layers: [f(4)] },
        { msg: `The <b>kernel</b> receives the system call <code>${esc(call)}</code>. Only the kernel may talk to devices.`, mood: 'wow', layers: [f(5)] },
        { msg: `The kernel asks the <b>${hw}</b> for the data.`, mood: 'work', layers: [f(6)] },
        { msg: 'The answer travels back up: kernel, C library, the program, which prints the result into the terminal.', mood: 'happy', fx: 'burst', layers: [f(0, true, { back: true })] }
      ];
    }
  }));

  const DISTROS = [
    ['Ubuntu', 'deb', 'fixed, LTS every 2 years', ['beginner', 'server', 'desktop']],
    ['Debian', 'deb', 'fixed, very stable', ['server', 'stable']],
    ['Fedora', 'rpm', 'fixed, about every 6 months', ['desktop', 'latest']],
    ['RHEL', 'rpm', 'fixed, 10 years of support', ['server', 'company']],
    ['Arch', 'pacman', 'rolling', ['latest', 'learn']],
    ['Alpine', 'apk', 'fixed, tiny', ['container']],
    ['Linux Mint', 'deb', 'fixed, based on Ubuntu', ['beginner', 'desktop']]
  ];
  def('lx-distro', el => W(el, {
    title: 'Find a distribution for a job',
    sub: 'Pick what you need. Pip checks every distribution against it, one by one.',
    inputs: [{ k: 'need', label: 'I need', type: 'seg', val: 'beginner', opts: [['beginner', 'An easy first desktop'], ['server', 'A web server'], ['container', 'A tiny container'], ['latest', 'The newest software'], ['company', 'Paid company support']] }],
    frames: v => {
      const names = DISTROS.map(d => d[0]), fr = [], ok = [];
      const row = (cls, tag) => ({ t: 'row', label: 'Distributions', cells: names, idx: false, cls, tag });
      fr.push({ msg: 'Every distribution has the same Linux kernel inside. They differ in packages, release style and who supports them.', mood: 'idle', layers: [row({})] });
      DISTROS.forEach((d, i) => {
        const hit = d[3].includes(v.need);
        const cls = {}; ok.forEach(k => { cls[k] = 'yes'; }); cls[i] = hit ? 'yes' : 'no';
        if (hit) ok.push(i);
        fr.push({ msg: `<b>${d[0]}</b>: packages ${d[1]}, releases ${d[2]}. ${hit ? 'A good fit.' : 'Not the best fit for this job.'}`, mood: hit ? 'happy' : 'sad', fx: hit ? 'burst' : undefined, layers: [row(cls, { [i]: d[1] })] });
      });
      const cls = {}; ok.forEach(k => { cls[k] = 'win'; });
      fr.push({ msg: `Good choices: ${ok.map(k => names[k]).join(', ')}. Any of them can run the same commands you learn here.`, mood: 'wow', fx: 'rain', layers: [row(cls)] });
      return fr;
    }
  }));

  /* ---------- shared: a pretend computer from assets/lxshell.js, so animations show real behaviour ---------- */
  const world = lab => new LXSH.World(lab || {});
  const HOME_TREE = () => ['/', [['bin', []], ['etc', [['passwd'], ['hostname'], ['os-release']]], ['home', [['asha', []], ['learner', [['notes.txt'], ['fruits.txt'], ['logs', [['app.log'], ['old.log']]], ['scripts', [['hello.sh']]], ['projects', []]]]]], ['tmp', []], ['usr', [['bin', []]]], ['var', [['log', []]]]]];

  /* 1.2 the parts of a command line */
  def('lx-cmdparts', el => W(el, {
    title: 'Take a command apart',
    sub: 'Type any command. Pip splits it into words the way the shell does and names each part.',
    inputs: [{ k: 'line', label: 'Command line', type: 'text', val: 'ls -l -a /etc', w: 300 }],
    random: () => ({ line: ['ls -la ~/logs', 'grep -i error app.log', 'cp -r photos backup', 'head -n 3 notes.txt', 'echo "two words" one'][Math.floor(Math.random() * 5)] }),
    frames: v => {
      const w = world(); let toks;
      try { toks = w.lex(String(v.line)).filter(t => t.w).map(t => w.wordText(t.w)); } catch (e) { return [{ msg: 'That line has an unclosed quote. Close it and try again.', mood: 'think', fx: 'shake', layers: [] }]; }
      if (!toks.length) return [{ msg: 'Type a command first.', mood: 'think', layers: [] }];
      const kind = toks.map((t, i) => i === 0 ? 'command' : /^--?\w/.test(t) ? 'option' : 'argument');
      const fr = [{ msg: 'The shell reads the line and splits it at spaces into words. Quotes keep words together.', mood: 'look', layers: [{ t: 'row', label: 'Words', cells: toks, idx: true }] }];
      toks.forEach((t, i) => {
        const cls = {}; for (let j = 0; j < i; j++) cls[j] = kind[j] === 'command' ? 'piv' : kind[j] === 'option' ? 'mv' : 'cur'; cls[i] = 'look';
        const say = kind[i] === 'command' ? `<code>${esc(t)}</code> is the <b>command</b>, the program to run. The shell looks for it in the folders listed in PATH.` : kind[i] === 'option' ? `<code>${esc(t)}</code> is an <b>option</b> (also called a flag). It starts with a dash and changes how the command behaves.${/^-[a-zA-Z]{2,}$/.test(t) ? ` Short options can be joined: ${esc(t)} means ${t.slice(1).split('').map(c => '-' + c).join(' ')}.` : ''}` : `<code>${esc(t)}</code> is an <b>argument</b>: what the command works on, often a file or folder name.`;
        fr.push({ msg: say, mood: 'look', layers: [{ t: 'row', label: 'Words', cells: toks, idx: true, cls, tag: Object.fromEntries(kind.slice(0, i + 1).map((k, j) => [j, k])) }] });
      });
      const cls = Object.fromEntries(kind.map((k, j) => [j, k === 'command' ? 'piv' : k === 'option' ? 'mv' : 'cur']));
      const r = w.run(String(v.line));
      fr.push({ msg: `Done: 1 command, ${kind.filter(k => k === 'option').length} option(s), ${kind.filter(k => k === 'argument').length} argument(s). Here is what the practice shell prints for it.`, mood: 'happy', fx: 'burst', layers: [{ t: 'row', label: 'Words', cells: toks, idx: true, cls, tag: Object.fromEntries(kind.map((k, j) => [j, k])) }, { t: 'term', lines: [['c', String(v.line)]].concat(r.out.replace(/\n$/, '').split('\n').slice(0, 8).filter(x => x !== '').map(x => ['o', x])) }] });
      return fr;
    }
  }));

  /* 2.1 resolving a path one name at a time */
  def('lx-path', el => W(el, {
    title: 'Follow a path through the tree',
    sub: 'Give a starting folder and a path. Pip walks the tree one name at a time, the way the kernel does.',
    inputs: [{ k: 'cwd', label: 'You are in', type: 'text', val: '/home/learner', w: 170 }, { k: 'path', label: 'Path', type: 'text', val: '../learner/logs/app.log', w: 220 }],
    random: () => ({ path: ['/etc/passwd', 'logs/../notes.txt', '~/scripts/hello.sh', './logs/old.log', '../../tmp', 'logs/missing.txt'][Math.floor(Math.random() * 6)] }),
    frames: v => {
      const w = world(); const cwd = String(v.cwd).trim() || '/';
      if (!w.node(w.abs(cwd)) || w.node(w.abs(cwd)).type !== 'd') return [{ msg: `${esc(cwd)} is not a folder in this tree. Try /home/learner.`, mood: 'think', fx: 'shake', layers: [{ t: 'fs', tree: HOME_TREE() }] }];
      let path = String(v.path).trim();
      const fr = [], tree = HOME_TREE();
      let at = path.startsWith('/') ? '/' : path.startsWith('~') ? '/home/learner' : w.abs(cwd);
      const why = path.startsWith('/') ? 'The path starts with <b>/</b>, so it is <b>absolute</b>: start at the root.' : path.startsWith('~') ? '<b>~</b> means your home folder, /home/learner.' : `The path does not start with /, so it is <b>relative</b>: start where you are, ${esc(w.abs(cwd))}.`;
      fr.push({ msg: why, mood: 'look', layers: [{ t: 'fs', tree, cls: { [at]: 'look' } }], vars: { at } });
      const parts = path.replace(/^~/, '').split('/').filter(Boolean);
      for (const p of parts) {
        const next = p === '.' ? at : p === '..' ? (at === '/' ? '/' : at.replace(/\/[^/]+$/, '') || '/') : (at === '/' ? '' : at) + '/' + p;
        const n = w.node(next);
        const say = p === '.' ? '<b>.</b> means "this folder", so we stay.' : p === '..' ? `<b>..</b> means "the parent folder", so we go up to ${esc(next)}.` : n ? `Go into <b>${esc(p)}</b>: now at ${esc(next)}.` : `There is no <b>${esc(p)}</b> inside ${esc(at)}. The shell would say: No such file or directory.`;
        if (!n) { fr.push({ msg: say, mood: 'sad', fx: 'shake', layers: [{ t: 'fs', tree, cls: { [at]: 'no' } }], vars: { at } }); return fr; }
        at = next;
        fr.push({ msg: say, mood: 'look', layers: [{ t: 'fs', tree, cls: { [at]: 'look' } }], vars: { at } });
      }
      fr.push({ msg: `Arrived. The full absolute path is <b>${esc(at)}</b>.`, mood: 'happy', fx: 'burst', layers: [{ t: 'fs', tree, cls: { [at]: 'yes' } }], vars: { at } });
      return fr;
    }
  }));

  /* 2.2 glob patterns */
  def('lx-glob', el => W(el, {
    title: 'Which files does a pattern match',
    sub: 'Type a pattern with * ? or [ ]. Pip tests every file name and lights up the matches.',
    inputs: [{ k: 'pat', label: 'Pattern', type: 'text', val: '*.txt', w: 140 }, { k: 'names', label: 'File names', type: 'text', val: 'notes.txt, fruits.txt, marks.csv, photo1.jpg, photo2.jpg, photo10.jpg, .bashrc, README', w: 380 }],
    random: () => ({ pat: ['photo?.jpg', '*.jpg', '[nf]*', '*[0-9]*', '*', '.*', '[!a-m]*'][Math.floor(Math.random() * 7)] }),
    frames: v => {
      const names = PK.parseList(v.names, false), pat = String(v.pat).trim();
      let re = '';
      for (let i = 0; i < pat.length; i++) { const c = pat[i]; if (c === '*') re += '.*'; else if (c === '?') re += '.'; else if (c === '[') { const j = pat.indexOf(']', i + 1); if (j < 0) { re += '\\['; continue; } let set = pat.slice(i + 1, j); if (set[0] === '!' || set[0] === '^') set = '^' + set.slice(1); re += '[' + set + ']'; i = j; } else re += c.replace(/[.+^${}()|\\]/g, '\\$&'); }
      const R = new RegExp('^' + re + '$'), hits = {};
      const fr = [{ msg: `Pattern <code>${esc(pat)}</code>: <b>*</b> matches any text (even none), <b>?</b> exactly one character, <b>[abc]</b> one of those characters, <b>[!abc]</b> one character that is not.`, mood: 'think', layers: [{ t: 'row', label: 'Files in the folder', cells: names, idx: false }] }];
      names.forEach((n, i) => {
        const hidden = n.startsWith('.') && !pat.startsWith('.');
        const ok = !hidden && R.test(n);
        hits[i] = ok ? 'yes' : 'no';
        fr.push({ msg: `<code>${esc(n)}</code>: ${ok ? 'matches.' : hidden ? 'starts with a dot, and a pattern only matches hidden files when it also starts with a dot.' : 'does not match.'}`, mood: ok ? 'happy' : 'sad', layers: [{ t: 'row', label: 'Files in the folder', cells: names, idx: false, cls: Object.assign({}, hits, { [i]: ok ? 'yes' : 'no' }) }] });
      });
      const got = names.filter((_, i) => hits[i] === 'yes');
      fr.push({ msg: got.length ? `The shell replaces <code>${esc(pat)}</code> with: <code>${esc(got.sort().join(' '))}</code> before the command even starts.` : `Nothing matches, so bash leaves the pattern as it is: the command receives the text <code>${esc(pat)}</code>.`, mood: got.length ? 'wow' : 'think', fx: got.length ? 'rain' : undefined, layers: [{ t: 'row', label: 'Files in the folder', cells: names, idx: false, cls: Object.fromEntries(Object.entries(hits).map(([k, c]) => [k, c === 'yes' ? 'win' : 'done'])) }] });
      return fr;
    }
  }));

  /* 2.3 head, tail and wc on a real file of the practice shell */
  def('lx-headtail', el => W(el, {
    title: 'head, tail and wc, line by line',
    sub: 'Pick a command and a number. Pip walks through the file and picks the lines that command prints.',
    inputs: [{ k: 'cmd', label: 'Command', type: 'seg', val: 'head', opts: [['head', 'head -n N'], ['tail', 'tail -n N'], ['from', 'tail -n +N'], ['wc', 'wc -l']] },
             { k: 'n', label: 'N', type: 'num', val: 3, min: 0, max: 20, w: 70 },
             { k: 'file', label: 'File', type: 'seg', val: 'logs/app.log', opts: [['logs/app.log', 'logs/app.log'], ['fruits.txt', 'fruits.txt'], ['poem.txt', 'poem.txt']] }],
    random: () => ({ cmd: ['head', 'tail', 'from', 'wc'][Math.floor(Math.random() * 4)], n: 1 + Math.floor(Math.random() * 5) }),
    check: v => Number.isInteger(Number(v.n)) && v.n >= 0 && v.n <= 20 ? '' : 'N should be a whole number from 0 to 20.',
    frames: v => {
      const w = world(), path = String(v.file), n = Number(v.n);
      const nd = w.node(w.abs(path)), body = nd && nd.type === 'f' ? nd.data : '';
      const lines = body.replace(/\n$/, '').split('\n'), L = lines.length;
      const label = { head: `head -n ${n} ${path}`, tail: `tail -n ${n} ${path}`, from: `tail -n +${n} ${path}`, wc: `wc -l ${path}` }[v.cmd];
      const view = (pick, cur) => [{ t: 'term', label: `${path} has ${L} lines`, lines: lines.map((s, i) => [i === cur || pick.has(i) ? 'h' : 'o', `${String(i + 1).padStart(2)}  ${s}`]) }];
      const fr = [{ msg: `<code>${esc(label)}</code>. ${v.cmd === 'head' ? 'head prints the first N lines, then stops reading.' : v.cmd === 'tail' ? 'tail prints the last N lines.' : v.cmd === 'from' ? 'With a plus sign, tail starts at line N and prints everything after it. tail -n +2 is the classic way to skip a header line.' : 'wc -l counts newline characters, which is the number of lines.'}`, mood: 'think', layers: view(new Set(), -1) }];
      const pick = new Set();
      if (v.cmd === 'wc') {
        lines.forEach((_, i) => { pick.add(i); if (i < 3 || i === L - 1) fr.push({ msg: `Line ${i + 1} ends with a newline. Count so far: <b>${i + 1}</b>.`, mood: 'look', layers: view(pick, i) }); });
        fr.push({ msg: `Result: <code>${L} ${esc(path)}</code>`, mood: 'happy', fx: 'burst', layers: view(pick, -1) });
        return fr;
      }
      let idx = [];
      if (v.cmd === 'head') idx = lines.map((_, i) => i).slice(0, n);
      else if (v.cmd === 'tail') idx = n ? lines.map((_, i) => i).slice(-n) : [];
      else idx = lines.map((_, i) => i).slice(Math.max(n, 1) - 1);
      idx.forEach((i, k) => { pick.add(i); if (k < 4 || k === idx.length - 1) fr.push({ msg: `Line ${i + 1} is picked${k === idx.length - 1 ? ', and that is the last one.' : '.'}`, mood: 'look', layers: view(pick, i) }); });
      if (v.cmd === 'head' && n > L) fr.push({ msg: `You asked for ${n} lines but the file has only ${L}, so head prints them all without any error.`, mood: 'think', layers: view(pick, -1) });
      if (v.cmd === 'from' && n === 0) fr.push({ msg: 'tail -n +0 behaves like tail -n +1: the whole file.', mood: 'think', layers: view(pick, -1) });
      fr.push({ msg: idx.length ? `Output: ${idx.length} line${idx.length > 1 ? 's' : ''}, shown in their original order.` : 'Output: nothing at all.', mood: idx.length ? 'happy' : 'sad', fx: idx.length ? 'burst' : undefined, layers: [{ t: 'term', label: 'What the terminal shows', lines: [['c', label]].concat(idx.map(i => ['o', lines[i]])) }] });
      return fr;
    }
  }));

  /* 3.2 vim: modes and keys on a small buffer */
  def('lx-vim', el => W(el, {
    title: 'Drive vim one key at a time',
    sub: 'Type keys as you would in vim. Write &lt;Esc&gt; for the Escape key. Spaces between keys in Normal mode are ignored here, so you can write dd p. Pip shows the mode and the cursor after every key.',
    inputs: [{ k: 'keys', label: 'Keys', type: 'text', val: 'j dd p 0 i- <Esc> :wq', w: 360 }, { k: 'text', label: 'Start text (lines split by |)', type: 'text', val: 'Buy milk|Call grandma|Finish the Linux lesson', w: 360 }],
    random: () => ({ keys: ['x x x', 'A today<Esc>', 'oWater the plants<Esc>', 'yy p p', 'G dd u', 'w cwPhone<Esc>', 'jj$x', 'dd dd u u'][Math.floor(Math.random() * 8)] }),
    frames: v => {
      let lines = String(v.text).split('|'), r = 0, c = 0, mode = 'NORMAL', reg = '', cmd = '', saved = false;
      const undo = [], fr = [], toks = [];
      const src = String(v.keys);
      for (let i = 0; i < src.length; i++) { if (src.startsWith('<Esc>', i)) { toks.push('<Esc>'); i += 4; } else toks.push(src[i]); }
      const snap = () => undo.push({ lines: lines.slice(), r, c });
      const clampC = () => { const n = lines[r].length; c = Math.max(0, Math.min(c, mode === 'INSERT' ? n : Math.max(n - 1, 0))); };
      const show = (msg, mood, fx) => fr.push({ msg, mood: mood || 'look', fx, layers: [{ t: 'buf', label: 'notes.txt in vim', lines: lines.slice(), r, c, mode, reg, cmd }] });
      show('vim opens in <b>Normal</b> mode, where every key is a command, not text. Press <code>i</code> to start typing and <code>Esc</code> to come back.', 'think');
      let pend = '', typed = '', steps = 0, quit = false;
      const runCmd = () => {
        const c2 = cmd.trim(); mode = 'NORMAL'; cmd = '';
        if (c2 === 'w' || c2 === 'wq' || c2 === 'x') { saved = true; if (c2 !== 'w') quit = true; undo.length = 0; fr.push({ msg: `<code>:${esc(c2)}</code> writes the file${c2 === 'w' ? '' : ' and quits'}. vim reports "notes.txt" ${lines.length}L written.`, mood: 'wow', fx: 'burst', layers: [{ t: 'buf', label: 'notes.txt in vim', lines: lines.slice(), r, c, mode: 'CMD', cmd: c2 }] }); }
        else if (c2 === 'q!') { quit = true; show('<code>:q!</code> quits and throws away every unsaved change. The file on disk stays as it was at the last write.', 'think'); }
        else if (c2 === 'q') { if (undo.length) show('<code>:q</code> refuses with E37: No write since last change (add ! to override).', 'sad', 'shake'); else { quit = true; show('<code>:q</code> quits, there were no unsaved changes.', 'happy'); } }
        else show(`Command <code>:${esc(c2)}</code> is not shown in this animation. Try :w, :wq, :q or :q!.`, 'think');
      };
      const flushTyped = () => { if (typed) { show(`Typed <code>${esc(typed)}</code> as text.`, 'look'); typed = ''; } };
      for (const k of toks) {
        if (++steps > 80) { show('That is a lot of keys. I stopped after 80.', 'think'); break; }
        if (mode === 'INSERT') {
          if (k === '<Esc>') { flushTyped(); mode = 'NORMAL'; c = Math.max(c - 1, 0); clampC(); show('<code>Esc</code> leaves Insert mode. The cursor steps back one place, as in real vim.', 'happy'); continue; }
          lines[r] = lines[r].slice(0, c) + k + lines[r].slice(c); c++; typed += k; continue;
        }
        if (mode === 'CMD') {
          if (k === '<Esc>') { mode = 'NORMAL'; cmd = ''; show('Esc cancels the command line.', 'think'); continue; }
          if (k === ' ') { runCmd(); continue; }
          cmd += k; continue;
        }
        if (k === ' ') continue;
        const key = pend + k; pend = '';
        if (key === 'd' || key === 'y' || key === 'g' || key === 'c') { pend = key; continue; }
        if (key === ':') { mode = 'CMD'; cmd = ''; continue; }
        if (key === 'h') { c--; clampC(); show('<code>h</code> moves left.'); }
        else if (key === 'l') { c++; clampC(); show('<code>l</code> moves right.'); }
        else if (key === 'j') { if (r < lines.length - 1) r++; clampC(); show('<code>j</code> moves down one line.'); }
        else if (key === 'k') { if (r > 0) r--; clampC(); show('<code>k</code> moves up one line.'); }
        else if (key === '0') { c = 0; show('<code>0</code> jumps to the start of the line.'); }
        else if (key === '$') { c = Math.max(lines[r].length - 1, 0); show('<code>$</code> jumps to the end of the line.'); }
        else if (key === 'w') { const m = /\S*\s+/.exec(lines[r].slice(c)); if (m && c + m[0].length < lines[r].length) c += m[0].length; show('<code>w</code> jumps to the start of the next word.'); }
        else if (key === 'b') { const left = lines[r].slice(0, c).replace(/\s+$/, ''); c = Math.max(left.lastIndexOf(' ') + 1, 0); show('<code>b</code> jumps back to the start of a word.'); }
        else if (key === 'gg') { r = 0; c = 0; show('<code>gg</code> goes to the first line.'); }
        else if (key === 'G') { r = lines.length - 1; c = 0; show('<code>G</code> goes to the last line.'); }
        else if (key === 'x') { if (lines[r].length) { snap(); reg = lines[r][c]; lines[r] = lines[r].slice(0, c) + lines[r].slice(c + 1); clampC(); show(`<code>x</code> deletes the character under the cursor (${esc(reg)}).`, 'look'); } }
        else if (key === 'dd') { snap(); reg = lines[r] + '⏎'; lines.splice(r, 1); if (!lines.length) lines = ['']; if (r >= lines.length) r = lines.length - 1; c = 0; show('<code>dd</code> deletes the whole line and keeps it in the register, ready to paste.', 'look', 'shake'); }
        else if (key === 'yy') { reg = lines[r] + '⏎'; show('<code>yy</code> yanks (copies) the line into the register. The text does not change.', 'look'); }
        else if (key === 'p' || key === 'P') { if (!reg) { show('The register is empty, nothing to paste.', 'sad'); continue; } snap(); if (reg.endsWith('⏎')) { const at = key === 'p' ? r + 1 : r; lines.splice(at, 0, reg.slice(0, -1)); r = at; c = 0; } else { const at = key === 'p' ? c + 1 : c; lines[r] = lines[r].slice(0, at) + reg + lines[r].slice(at); c = at; } show(`<code>${key}</code> pastes ${key === 'p' ? 'after' : 'before'} the cursor.`, 'happy'); }
        else if (key === 'u') { const u = undo.pop(); if (u) { ({ lines, r, c } = u); show('<code>u</code> undoes the last change.', 'happy'); } else show('Nothing left to undo.', 'think'); }
        else if (key === 'cw') { snap(); const m = /^\S*/.exec(lines[r].slice(c)); lines[r] = lines[r].slice(0, c) + lines[r].slice(c + m[0].length); mode = 'INSERT'; show('<code>cw</code> deletes to the end of the word and switches to Insert mode.', 'look'); }
        else if ('iaAoO'.includes(key)) {
          snap();
          if (key === 'a') c = Math.min(c + 1, lines[r].length);
          if (key === 'A') c = lines[r].length;
          if (key === 'o') { lines.splice(r + 1, 0, ''); r++; c = 0; }
          if (key === 'O') { lines.splice(r, 0, ''); c = 0; }
          mode = 'INSERT';
          show({ i: '<code>i</code> inserts before the cursor.', a: '<code>a</code> appends after the cursor.', A: '<code>A</code> appends at the end of the line.', o: '<code>o</code> opens a new line below.', O: '<code>O</code> opens a new line above.' }[key] + ' Insert mode: now keys are text.', 'happy');
        }
        else if (key === '<Esc>') show('Already in Normal mode. Pressing Esc again is harmless, which is why people press it when unsure.', 'think');
        else show(`<code>${esc(key)}</code> is not one of the keys this animation knows. Try h j k l w b 0 $ gg G x dd yy p P u i a A o O cw and :wq.`, 'sad');
      }
      flushTyped();
      if (mode === 'CMD') runCmd();
      if (!quit && mode === 'INSERT') show('Still in Insert mode. Press Esc before any Normal command or before :wq.', 'think');
      else if (!quit && !saved) show('Done. To save and quit, type <code>:wq</code> and press Enter.', 'happy');
      return fr;
    }
  }));

  /* 3.1 chmod: octal or symbolic to permission bits */
  def('lx-chmod', el => W(el, {
    title: 'chmod, bit by bit',
    sub: 'Start from a mode, apply a chmod change in numbers (750) or letters (g+w, o-r, u=rwx). Watch every bit.',
    inputs: [{ k: 'start', label: 'Start mode', type: 'text', val: '644', w: 90 }, { k: 'change', label: 'chmod', type: 'text', val: 'u+x,g+w', w: 150 }],
    random: () => ({ change: ['755', '600', 'a+x', 'go-r', 'u=rwx,go=rx', 'o=', '+x', '711'][Math.floor(Math.random() * 8)] }),
    check: v => /^[0-7]{3}$/.test(String(v.start)) ? '' : 'The start mode needs three octal digits, for example 644.',
    frames: v => {
      let m = parseInt(v.start, 8); const ch = String(v.change).trim(), fr = [];
      const show = (cls, msg, mood, fx) => fr.push({ msg, mood, fx, layers: [{ t: 'perm', label: `Mode ${m.toString(8).padStart(3, '0')}  ${['---','--x','-w-','-wx','r--','r-x','rw-','rwx'][m >> 6 & 7]}${['---','--x','-w-','-wx','r--','r-x','rw-','rwx'][m >> 3 & 7]}${['---','--x','-w-','-wx','r--','r-x','rw-','rwx'][m & 7]}`, mode: m, cls }] });
      show({}, `Each group has three switches: <b>r</b> read (4), <b>w</b> write (2), <b>x</b> execute (1). Add them up per group to get one digit. Start: ${v.start}.`, 'idle');
      if (/^[0-7]{3}$/.test(ch)) {
        const t = parseInt(ch, 8);
        [0, 1, 2].forEach(g => {
          const d = (t >> (6 - 3 * g)) & 7, cls = {};
          [0, 1, 2].forEach(b => { cls[g * 3 + b] = 'look'; });
          m = (m & ~(7 << (6 - 3 * g))) | (d << (6 - 3 * g));
          const parts = [[4, 'r'], [2, 'w'], [1, 'x']].filter(([n]) => d & n).map(([n, c]) => `${c} (${n})`);
          show(cls, `Digit ${g + 1} is <b>${d}</b> = ${parts.length ? parts.join(' + ') : 'nothing'}, so the ${['owner', 'group', 'others'][g]} get ${parts.length ? parts.map(p => p[0]).join('') : 'no rights'}.`, 'look');
        });
      } else {
        for (const cl of ch.split(',')) {
          const mm = /^([ugoa]*)([-+=])([rwx]*)$/.exec(cl);
          if (!mm) { fr.push({ msg: `I do not understand <code>${esc(cl)}</code>. Use who (u, g, o, a), then + - or =, then letters r w x. Example: g+w.`, mood: 'sad', fx: 'shake' }); return fr; }
          const who = mm[1] || 'a', cls = {};
          ['u', 'g', 'o'].forEach((w2, g) => {
            if (!who.includes(w2) && !who.includes('a')) return;
            let bits = 0; [...mm[3]].forEach(c => { bits |= { r: 4, w: 2, x: 1 }[c]; });
            const sh = 6 - 3 * g, before = (m >> sh) & 7;
            const after = mm[2] === '+' ? before | bits : mm[2] === '-' ? before & ~bits : bits;
            m = (m & ~(7 << sh)) | (after << sh);
            [0, 1, 2].forEach(b => { const bit = 4 >> b; if ((before & bit) !== (after & bit)) cls[g * 3 + b] = after & bit ? 'yes' : 'no'; });
          });
          show(cls, `<code>${esc(cl)}</code>: ${mm[2] === '+' ? 'switch on' : mm[2] === '-' ? 'switch off' : 'set exactly'} ${mm[3] || 'nothing'} for ${who.replace('a', 'everyone').replace('u', 'owner ').replace('g', 'group ').replace('o', 'others ')}. Green bits turned on, red bits turned off.`, 'look');
        }
      }
      show({}, `Result: <b>${m.toString(8).padStart(3, '0')}</b>. In ls -l you would see -${['---','--x','-w-','-wx','r--','r-x','rw-','rwx'][m >> 6 & 7]}${['---','--x','-w-','-wx','r--','r-x','rw-','rwx'][m >> 3 & 7]}${['---','--x','-w-','-wx','r--','r-x','rw-','rwx'][m & 7]} for a file.`, 'happy', 'burst');
      return fr;
    }
  }));

  /* 3.1 may this user do this? */
  def('lx-access', el => W(el, {
    title: 'May this person open the file',
    sub: 'Pick a user, a file mode and an action. Pip follows the same order of checks as the kernel.',
    inputs: [{ k: 'who', label: 'User', type: 'seg', val: 'asha', opts: [['learner', 'learner (owner)'], ['asha', 'asha (in group team)'], ['ravi', 'ravi (other)'], ['root', 'root']] },
      { k: 'mode', label: 'Mode of report.txt', type: 'text', val: '640', w: 90 }, { k: 'act', label: 'Wants to', type: 'seg', val: 'r', opts: [['r', 'read'], ['w', 'write'], ['x', 'execute']] }],
    check: v => /^[0-7]{3}$/.test(String(v.mode)) ? '' : 'Mode needs three octal digits.',
    frames: v => {
      const m = parseInt(v.mode, 8), bit = { r: 4, w: 2, x: 1 }[v.act], word = { r: 'read', w: 'write', x: 'execute' }[v.act];
      const L = c => [{ t: 'perm', label: 'report.txt, owner learner, group team', mode: m, cls: c }];
      const fr = [{ msg: `${v.who} wants to <b>${word}</b> report.txt (owner learner, group team, mode ${v.mode}).`, mood: 'think', layers: L({}) }];
      if (v.who === 'root') {
        const ok = v.act !== 'x' || (m & 0o111);
        fr.push({ msg: ok ? 'root skips the read and write checks. Allowed.' : 'Even root may only execute a file when at least one x bit is set. Denied.', mood: ok ? 'happy' : 'sad', fx: ok ? 'burst' : 'shake', layers: L({}) });
        return fr;
      }
      const g = v.who === 'learner' ? 0 : v.who === 'asha' ? 1 : 2, name = ['owner', 'group', 'others'][g];
      if (g >= 1) fr.push({ msg: `${v.who} is not the owner, so the owner bits do not count for them at all.`, mood: 'look', layers: L({ 0: 'done', 1: 'done', 2: 'done' }) });
      if (g === 2) fr.push({ msg: `${v.who} is not in the group team either, so only the <b>others</b> bits count.`, mood: 'look', layers: L({ 0: 'done', 1: 'done', 2: 'done', 3: 'done', 4: 'done', 5: 'done' }) });
      const idx = g * 3 + [4, 2, 1].indexOf(bit), on = (m >> (8 - idx)) & 1;
      fr.push({ msg: `The kernel uses only the <b>${name}</b> group of bits. The ${word} bit there is ${on ? 'on' : 'off'}. ${on ? 'Allowed.' : 'Denied: Permission denied.'}`, mood: on ? 'happy' : 'sad', fx: on ? 'burst' : 'shake', layers: L({ [idx]: on ? 'yes' : 'no' }) });
      return fr;
    }
  }));

  /* 2.x onward: run a pipeline stage by stage in the practice shell and show the data between stages */
  def('lx-pipe', el => W(el, {
    title: 'Watch data flow through a pipeline',
    sub: 'Type a pipeline. Pip runs it in the practice shell one stage at a time and shows what passes through each pipe.',
    inputs: [{ k: 'line', label: 'Pipeline', type: 'text', val: 'cat fruits.txt | sort | uniq -c | sort -rn | head -3', w: 420 }],
    random: () => ({ line: ['grep ERROR logs/app.log | cut -d" " -f4- | sort', 'cut -d, -f2 marks.csv | tail -n +2 | sort | uniq -c', 'ls -l | grep "^d" | wc -l', 'cat poem.txt | tr a-z A-Z | head -2', "awk -F, 'NR>1 {print $3, $1}' marks.csv | sort -rn | head -2"][Math.floor(Math.random() * 5)] }),
    frames: v => {
      const line = String(v.line).trim(), w = world();
      let tree; try { tree = w.parse(w.lex(line)); } catch (e) { return [{ msg: 'The shell could not read that line: ' + esc(e.message), mood: 'sad', fx: 'shake', layers: [] }]; }
      const pipe = tree.items.length === 1 && tree.items[0].p.t === 'pipe' ? tree.items[0].p : null;
      if (!pipe) return [{ msg: 'Type one pipeline, with commands joined by |.', mood: 'think', layers: [] }];
      const stages = line.split(/\|(?![^"']*["'][^"']*$)/).map(s => s.trim());
      if (stages.length !== pipe.cmds.length) stages.length = 0;
      const names = pipe.cmds.map((c, i) => stages[i] || ('stage ' + (i + 1)));
      const fr = [{ msg: `This pipeline has ${pipe.cmds.length} stage(s). All of them start at the same time, and each one reads the output of the one before it.`, mood: 'look', layers: [{ t: 'flow', items: names.map(n => [n, '']) }] }];
      let data = '';
      for (let i = 0; i < pipe.cmds.length; i++) {
        let buf = ''; const save = w.outHook; w.outHook = s => { buf += s; };
        try { w.withRedir(pipe.cmds[i], data, null); } catch (e) { buf += 'error: ' + e.message + '\n'; } finally { w.outHook = save; }
        data = buf;
        const shown = data.replace(/\n$/, '').split('\n');
        fr.push({ msg: `<code>${esc(names[i])}</code> ${i ? 'reads the lines from the pipe and' : ''} writes ${shown.filter(x => x !== '').length} line(s)${i < pipe.cmds.length - 1 ? ' into the next pipe' : ' to your screen'}.`, mood: i === pipe.cmds.length - 1 ? 'happy' : 'work', fx: i === pipe.cmds.length - 1 ? 'burst' : undefined,
          layers: [{ t: 'flow', items: names.map((n, k) => [n, '', k < i ? 'done' : k === i ? (i === pipe.cmds.length - 1 ? 'yes' : 'look') : '']), arrows: names.map((_, k) => k < i ? 'yes' : '') }, { t: 'term', label: i < pipe.cmds.length - 1 ? 'In the pipe now' : 'On your screen', lines: shown.slice(0, 10).map(x => ['o', x]).concat(shown.length > 10 ? [['o', `... ${shown.length - 10} more line(s)`]] : []) }] });
      }
      return fr;
    }
  }));

  /* ---------- wiring for lxkit.run() boxes ---------- */
  function wire(root) {
    root.querySelectorAll('.lx-run .lx-copy').forEach(b => {
      if (b.dataset.on) return;
      b.dataset.on = '1';
      b.addEventListener('click', () => {
        const cmds = [...b.closest('.lx-run').querySelectorAll('.lx-cmd')].map(x => x.textContent).join('\n');
        (navigator.clipboard ? navigator.clipboard.writeText(cmds) : Promise.reject()).then(() => { b.textContent = 'Copied'; setTimeout(() => { b.textContent = 'Copy'; }, 1200); }, () => { b.textContent = 'Select and copy'; });
      });
    });
  }
  function start() { VIZ.mountAll(document); wire(document); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
