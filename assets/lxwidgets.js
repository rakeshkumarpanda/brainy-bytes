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
    return `${L.label ? `<div class="pk-lab">${L.label}</div>` : ''}<div class="pk-flow">${items.map(([t, s, c], i) => `${i && !L.plain ? `<span class="pk-arr ${ar[i - 1] || ''}">${L.back ? '⇄' : '→'}</span>` : ''}<div class="pk-box ${c || ''}">${esc(t)}${s ? `<small>${esc(s)}</small>` : ''}</div>`).join('')}</div>`;
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

  /* the three standard streams of a command: {t: 'fds', label, cmd, rows: [[fd, name, dest, cls]]} */
  D.fds = L => `${L.label ? `<div class="pk-lab">${L.label}</div>` : ''}<div class="pk-fds"><div class="pk-fdcmd">${esc(L.cmd)}</div><div>${L.rows.map(([n, name, dest, c]) => `<div class="pk-fd ${c || ''}"><b>${n}</b><span>${name}</span><i>${n === 0 ? '←' : '→'}</i><em>${esc(dest)}</em></div>`).join('')}</div></div>`;

  /* lines with the matched parts marked: {t: 'match', label, rows: [[text, [[from, to]...], cls]]} */
  D.match = L => `${L.label ? `<div class="pk-lab">${L.label}</div>` : ''}<div class="pk-match">${L.rows.map(([t, rg, c]) => {
    let h = '', at = 0; (rg || []).forEach(([a, b]) => { h += esc(t.slice(at, a)) + `<mark>${esc(t.slice(a, b)) || '&#8203;'}</mark>`; at = b; });
    return `<div class="${c || ''}">${h + esc(t.slice(at))}</div>`; }).join('')}</div>`;

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

  /* power 2.1 regular expressions: read a pattern piece by piece, then test it on every line */
  const reParts = (p, ere) => {
    const out = []; let i = 0;
    const sp = c => ere ? p[i] === c : p[i] === '\\' && p[i + 1] === c;
    const quant = () => {
      if (p[i] === '*') { i++; return 'repeated 0 or more times'; }
      if (sp('+')) { i += ere ? 1 : 2; return 'repeated 1 or more times'; }
      if (sp('?')) { i += ere ? 1 : 2; return 'optional (0 or 1 time)'; }
      if (sp('{')) { const j = p.indexOf(ere ? '}' : '\\}', i); if (j > 0) { const body = p.slice(i + (ere ? 1 : 2), j); i = j + (ere ? 1 : 2); const [a, b] = body.split(','); return b === undefined ? `exactly ${a} times` : b === '' ? `at least ${a} times` : `between ${a} and ${b} times`; } }
      return '';
    };
    while (i < p.length) {
      const st = i; let what = '';
      if (p[i] === '^' && i === 0) { i++; what = 'the start of the line'; }
      else if (p[i] === '$' && i === p.length - 1) { i++; what = 'the end of the line'; }
      else if (p[i] === '.') { i++; what = 'any one character'; }
      else if (p[i] === '[') { let j = i + 1; if (p[j] === '^') j++; if (p[j] === ']') j++; while (j < p.length && p[j] !== ']') { if (p.startsWith('[:', j)) j = p.indexOf(':]', j) + 2; else j++; } const body = p.slice(i + 1, j); i = j + 1; what = body.startsWith('^') ? `one character that is NOT in ${esc(body.slice(1))}` : `one character from ${esc(body)}`; }
      else if (sp('(')) { i += ere ? 1 : 2; out.push([p.slice(st, i), 'start a group']); continue; }
      else if (sp(')')) { i += ere ? 1 : 2; const q = quant(); out.push([p.slice(st, i), 'end the group' + (q ? ', the whole group ' + q : '')]); continue; }
      else if (sp('|')) { i += ere ? 1 : 2; out.push([p.slice(st, i), 'OR: the part before or the part after']); continue; }
      else if (p[i] === '\\') { const c = p[i + 1]; i += 2; what = { w: 'one word character (letter, digit or _)', s: 'one space or tab', b: 'a word boundary', '<': 'the start of a word', '>': 'the end of a word', d: 'a digit (only in grep -P)' }[c] || `the character ${esc(c)} itself`; }
      else { let j = i; while (j < p.length && /[A-Za-z0-9 ,:_=@%#'"-]/.test(p[j]) && !(j > i && /[*+?{]/.test(p[j + 1] || '') )) j++; if (j === i) j = i + 1; const lit = p.slice(i, j); i = j; what = lit.length > 1 ? `the text "${esc(lit)}"` : `the character "${esc(lit)}"`; }
      const q = quant();
      out.push([p.slice(st, i), what + (q ? ', ' + q : '')]);
    }
    return out;
  };
  def('lx-regex', el => W(el, {
    title: 'Read and test a regular expression',
    sub: 'Type a pattern and pick basic (grep) or extended (grep -E) syntax. Pip explains each piece, then tries it on every line and marks what matched.',
    inputs: [{ k: 'pat', label: 'Pattern', type: 'text', val: 'ERROR|WARN', w: 220 }, { k: 'mode', label: 'Syntax', type: 'seg', val: 'E', opts: [['B', 'grep (basic)'], ['E', 'grep -E (extended)']] },
             { k: 'file', label: 'Lines from', type: 'seg', val: 'logs/app.log', opts: [['logs/app.log', 'logs/app.log'], ['marks.csv', 'marks.csv'], ['poem.txt', 'poem.txt'], ['fruits.txt', 'fruits.txt']] }],
    random: () => (['^2026.*ERROR', '[0-9]{2}s$', 'user [a-z]+', '^(Asha|Ravi),', ',[89][0-9]$', 'an+a', '^[A-Z][a-z]+ [a-z]+$', 'o[a-z]*e'].map(x => ({ pat: x, mode: 'E' })).concat([{ pat: 'a\\{2\\}', mode: 'B' }, { pat: 'ERROR\\|WARN', mode: 'B' }]))[Math.floor(Math.random() * 10)],
    frames: v => {
      const pat = String(v.pat), ere = v.mode === 'E', w = world(), nd = w.node(w.abs(v.file));
      const lines = (nd && nd.data || '').replace(/\n$/, '').split('\n');
      let re; try { re = LXSH.toRe(pat, ere, 'g'); } catch (e) { return [{ msg: 'That pattern is not valid: ' + esc(e.message), mood: 'sad', fx: 'shake', layers: [] }]; }
      const parts = reParts(pat, ere);
      const fr = [{ msg: `Pattern <code>${esc(pat)}</code> in ${ere ? 'extended' : 'basic'} syntax. ${ere ? 'In extended syntax + ? | ( ) { } are special by themselves.' : 'In basic syntax + ? | ( ) { } are plain characters, and become special only with a backslash in front.'}`, mood: 'think', layers: [{ t: 'flow', label: 'The pieces', items: parts.map(([t]) => [t, '', '']) }] }];
      parts.forEach(([t, m], k) => fr.push({ msg: `<code>${esc(t)}</code> means ${m}.`, mood: 'look', layers: [{ t: 'flow', label: 'The pieces', items: parts.map(([x], j) => [x, '', j === k ? 'look' : j < k ? 'done' : '']) }] }));
      const rows = [], hits = [];
      lines.forEach((l, i) => {
        re.lastIndex = 0; const rg = []; let m;
        while ((m = re.exec(l))) { rg.push([m.index, m.index + m[0].length]); if (!m[0].length) re.lastIndex++; }
        rows.push([l, rg, rg.length ? 'yes' : 'no']); if (rg.length) hits.push(i);
      });
      const shown = []; rows.forEach((r, i) => { shown.push(r); if (i < 3 || i === rows.length - 1) fr.push({ msg: r[1].length ? `Line ${i + 1} matches. The marked part is what the pattern found.` : `Line ${i + 1} has no match, so grep skips it.`, mood: r[1].length ? 'happy' : 'look', layers: [{ t: 'match', label: v.file, rows: shown.concat(rows.slice(i + 1).map(x => [x[0], [], ''])) }] }); });
      fr.push({ msg: hits.length ? `${hits.length} of ${lines.length} lines match. grep ${ere ? '-E ' : ''}would print exactly those lines, and grep -o only the marked parts.` : 'No line matches, so grep prints nothing and exits with status 1.', mood: hits.length ? 'wow' : 'sad', fx: hits.length ? 'burst' : undefined, layers: [{ t: 'match', label: v.file, rows }, { t: 'term', label: 'What the terminal shows', lines: [['c', `grep ${ere ? '-E ' : ''}'${pat}' ${v.file}`]].concat(hits.map(i => ['o', lines[i]])) }] });
      return fr;
    }
  }));

  /* power 2.2 sed: the cycle of read line, run the script, print the pattern space */
  def('lx-sed', el => W(el, {
    title: 'Watch the sed cycle',
    sub: 'Type a sed script with s, d and p commands, optional addresses (2, $, /regex/, 2,4) and -n. Pip runs the cycle for every line: read it into the pattern space, apply each command, print.',
    inputs: [{ k: 'script', label: 'Script', type: 'text', val: '/INFO/d; s/ERROR/ALERT/', w: 300 }, { k: 'n', label: 'Option', type: 'seg', val: '', opts: [['', 'none'], ['-n', '-n (no auto print)']] },
             { k: 'file', label: 'File', type: 'seg', val: 'logs/app.log', opts: [['logs/app.log', 'logs/app.log'], ['notes.txt', 'notes.txt'], ['poem.txt', 'poem.txt'], ['marks.csv', 'marks.csv']] }],
    random: () => ([['1d', '', 'marks.csv'], ['s/a/A/g', '', 'notes.txt'], ['2,3p', '-n', 'poem.txt'], ['/ERROR/p', '-n', 'logs/app.log'], ['$d', '', 'poem.txt'], ['s/,/ | /g', '', 'marks.csv'], ['/maths/!d', '', 'marks.csv']].map(([script, n, file]) => ({ script, n, file })))[Math.floor(Math.random() * 7)],
    frames: v => {
      const w = world(), nd = w.node(w.abs(v.file)), L = (nd && nd.data || '').replace(/\n$/, '').split('\n'), quiet = v.n === '-n';
      const cmds = [];
      for (const raw of String(v.script).split(';').map(x => x.trim()).filter(Boolean)) {
        const m = /^(\d+|\$|\/(?:[^/\\]|\\.)*\/)?(?:,(\d+|\$|\/(?:[^/\\]|\\.)*\/))?\s*(!?)\s*([sdp])(.*)$/.exec(raw);
        if (!m) return [{ msg: `I only know s, d and p here, with optional addresses. <code>${esc(raw)}</code> is not one of them.`, mood: 'sad', fx: 'shake', layers: [] }];
        const ad = x => x === undefined ? null : x === '$' ? { last: 1 } : /^\d+$/.test(x) ? { n: +x } : { re: LXSH.toRe(x.slice(1, -1), false, '') };
        const c = { raw, a1: ad(m[1]), a2: ad(m[2]), neg: !!m[3], op: m[4], on: false };
        if (c.op === 's') { const d = m[5][0], parts = m[5].slice(1).split(d); if (parts.length < 2) return [{ msg: 'An s command needs the form s/old/new/ with three slashes.', mood: 'sad', fx: 'shake', layers: [] }]; c.re = LXSH.toRe(parts[0], false, parts[2] && parts[2].includes('g') ? 'g' : ''); c.rep = parts[1].replace(/\\(\d)/g, '$$$1').replace(/&/g, '$$&'); c.p = (parts[2] || '').includes('p'); }
        cmds.push(c);
      }
      const out = [], fr = [];
      const lay = (ps, cur, k) => [{ t: 'flow', label: 'The script, one command after another', items: cmds.map((c, j) => [c.raw, '', j === k ? 'look' : '']) },
        { t: 'term', label: 'Input, the current line is marked', lines: L.map((x, i) => [i === cur ? 'h' : 'o', x]) },
        { t: 'flow', label: 'Pattern space', items: [[ps === null ? '(deleted)' : ps || ' ', '', ps === null ? 'no' : 'cur']] },
        { t: 'term', label: 'Output so far', lines: out.map(x => ['o', x]) }];
      fr.push({ msg: `sed reads one line at a time into the <b>pattern space</b>, runs the whole script on it, then ${quiet ? 'prints nothing unless a p command says so, because of -n' : 'prints the pattern space'} and goes on with the next line.`, mood: 'think', layers: lay('', -1, -1) });
      const showMax = L.length <= 5 ? 99 : 3;
      L.forEach((line, i) => {
        let ps = line;
        const verbose = i < showMax || i === L.length - 1;
        if (verbose) fr.push({ msg: `Line ${i + 1} goes into the pattern space.`, mood: 'look', layers: lay(ps, i, -1) });
        for (let k = 0; k < cmds.length && ps !== null; k++) {
          const c = cmds[k];
          const hit = a => a === null ? true : a.last ? i === L.length - 1 : a.n !== undefined ? i + 1 === a.n : a.re.test(ps);
          let on;
          if (c.a2) { if (c.on) { on = true; if (hit(c.a2)) c.on = false; } else if (hit(c.a1)) { on = true; c.on = !(c.a2.n !== undefined && c.a2.n <= i + 1); } else on = false; }
          else on = hit(c.a1);
          if (c.neg) on = !on;
          if (!on) { if (verbose) fr.push({ msg: `<code>${esc(c.raw)}</code>: the address does not select line ${i + 1}, so the command is skipped.`, mood: 'look', layers: lay(ps, i, k) }); continue; }
          if (c.op === 'd') { ps = null; if (verbose) fr.push({ msg: `<code>${esc(c.raw)}</code>: delete. The line is dropped and sed starts the next cycle at once.`, mood: 'look', fx: 'shake', layers: lay(ps, i, k) }); break; }
          if (c.op === 'p') { out.push(ps); if (verbose) fr.push({ msg: `<code>${esc(c.raw)}</code>: print the pattern space now.`, mood: 'happy', layers: lay(ps, i, k) }); continue; }
          const was = ps; c.re.lastIndex = 0; ps = ps.replace(c.re, c.rep);
          if (c.p && was !== ps) out.push(ps);
          if (verbose) fr.push({ msg: was === ps ? `<code>${esc(c.raw)}</code>: no match on this line, nothing changes.` : `<code>${esc(c.raw)}</code>: substitute${c.re.global ? ' every match' : ' the first match'}.`, mood: was === ps ? 'look' : 'happy', layers: lay(ps, i, k) });
        }
        if (ps !== null && !quiet) out.push(ps);
        if (verbose) fr.push({ msg: ps === null ? 'Nothing is printed for this line.' : quiet ? 'End of the script. With -n there is no automatic print.' : 'End of the script: the pattern space is printed.', mood: 'look', layers: lay(ps, i, -1) });
        else if (i === showMax) fr.push({ msg: `The same cycle runs for the remaining lines up to line ${L.length - 1}.`, mood: 'think', layers: lay(ps, i, -1) });
      });
      fr.push({ msg: `Done. sed ${quiet ? '-n ' : ''}'${esc(v.script)}' prints ${out.length} line${out.length === 1 ? '' : 's'}. The file itself is not changed unless you add -i.`, mood: 'wow', fx: 'burst', layers: [{ t: 'term', label: 'What the terminal shows', lines: [['c', `sed ${quiet ? '-n ' : ''}'${v.script}' ${v.file}`]].concat(out.map(x => ['o', x])) }] });
      return fr;
    }
  }));

  /* power 2.3 awk: split each line into fields, then run the program in the practice shell */
  def('lx-awk', el => W(el, {
    title: 'How awk sees a line',
    sub: 'Choose a file, a field separator and a program. Pip splits the first lines into fields $1, $2 and so on, then runs the whole program in the practice shell.',
    inputs: [{ k: 'prog', label: 'Program', type: 'text', val: 'NR > 1 { print $1, $3 }', w: 330 }, { k: 'fs', label: 'Field separator -F', type: 'seg', val: ',', opts: [[' ', 'spaces (default)'], [',', ','], [':', ':']] },
             { k: 'file', label: 'File', type: 'seg', val: 'marks.csv', opts: [['marks.csv', 'marks.csv'], ['logs/app.log', 'logs/app.log'], ['/etc/passwd', '/etc/passwd'], ['poem.txt', 'poem.txt']] }],
    random: () => ([['NR > 1 { sum += $3 } END { print sum / (NR - 1) }', ',', 'marks.csv'], ['$3 >= 85', ',', 'marks.csv'], ['{ print $3, $4 }', ' ', 'logs/app.log'], ['/ERROR/ { print $NF }', ' ', 'logs/app.log'], ['{ print $1, $7 }', ':', '/etc/passwd'], ['{ print NF, $1 }', ' ', 'poem.txt'], ['NR > 1 { n[$2]++ } END { for (s in n) print s, n[s] }', ',', 'marks.csv']].map(([prog, fs, file]) => ({ prog, fs, file })))[Math.floor(Math.random() * 7)],
    frames: v => {
      const w = world(), nd = w.node(w.abs(v.file)), L = (nd && nd.data || '').replace(/\n$/, '').split('\n'), fs = v.fs;
      const split = l => fs === ' ' ? l.trim().split(/[ \t]+/).filter(Boolean) : l.split(fs);
      const fr = [{ msg: `awk reads <code>${esc(v.file)}</code> one line (record) at a time. ${fs === ' ' ? 'By default fields are separated by runs of spaces and tabs.' : `With -F'${fs}' every ${fs === ',' ? 'comma' : 'colon'} separates two fields.`} $0 is the whole line, NR counts lines and NF counts fields.`, mood: 'think', layers: [{ t: 'term', label: v.file, lines: L.slice(0, 6).map(x => ['o', x]).concat(L.length > 6 ? [['o', '...']] : []) }] }];
      L.slice(0, Math.min(3, L.length)).forEach((l, i) => {
        const f = split(l);
        fr.push({ msg: `Line ${i + 1}: NR = ${i + 1}, NF = ${f.length}. ${f.length ? `$1 is "${esc(f[0])}"${f.length > 1 ? `, $NF (the last field) is "${esc(f[f.length - 1])}"` : ''}.` : 'The line is empty.'}`, mood: 'look', layers: [{ t: 'term', label: '$0', lines: [['h', l]] }, { t: 'row', label: 'Fields', cells: f.map(x => x.length > 14 ? x.slice(0, 13) + '…' : x), idx: false, tag: Object.fromEntries(f.map((_, k) => [k, '$' + (k + 1)])) }] });
      });
      const cmd = `awk${fs === ' ' ? '' : ` -F'${fs}'`} '${v.prog}' ${v.file}`;
      const r = w.run(cmd);
      const bad = /^awk: /m.test(r.out);
      fr.push({ msg: bad ? 'awk could not run that program. Read the message, fix the program and press Show me again.' : `The program <code>${esc(v.prog)}</code> runs on every line: a pattern chooses lines, the action in braces says what to do. BEGIN runs before the first line and END after the last.`, mood: bad ? 'sad' : 'wow', fx: bad ? 'shake' : 'burst', layers: [{ t: 'term', label: 'What the terminal shows', lines: [['c', cmd]].concat(r.out.replace(/\n$/, '').split('\n').filter((x, k, a) => x !== '' || k < a.length - 1).map(x => [bad ? 'e' : 'o', x])) }] });
      return fr;
    }
  }));

  /* power 3.1 find: walk the tree and test every entry */
  def('lx-find', el => W(el, {
    title: 'Watch find walk the tree',
    sub: 'Type the tests that follow find . (for example -type f -name "*.txt"). Pip visits every entry below your home folder, top down, and checks the tests.',
    inputs: [{ k: 'expr', label: 'find .', type: 'text', val: "-type f -name '*.txt'", w: 360 }],
    random: () => ({ expr: ["-type d", "-name '*.log'", "-type f -size -1k", "-empty", "-type f ! -name '*.txt'", "-path ./logs -prune -o -type f -print", "-type f \\( -name '*.jpg' -o -name '*.png' \\)", "-maxdepth 1 -type f"][Math.floor(Math.random() * 8)] }),
    frames: v => {
      const w = world(), expr = String(v.expr).trim();
      const all = w.run('find .').out.replace(/\n$/, '').split('\n');
      const r = w.run('find . ' + expr);
      if (/^find: /m.test(r.out)) return [{ msg: 'find did not accept that: ' + esc(r.out.trim()), mood: 'sad', fx: 'shake', layers: [] }];
      const hits = new Set(r.out.replace(/\n$/, '').split('\n').filter(Boolean));
      const build = (path, name) => { const n = w.node(w.abs(path), false); return n && n.type === 'd' ? [name, Object.keys(n.kids).sort().map(k => build(path + '/' + k, k))] : [name]; };
      const tree = build('.', '.');
      const cls = {}, tag = {};
      const L = () => [{ t: 'fs', label: 'Your home folder, as find sees it', tree, cls: Object.assign({}, cls), tag: Object.assign({}, tag) }];
      const fr = [{ msg: `find starts at <code>.</code>, the current folder, and visits every entry below it, folder by folder. For each one it checks <code>${esc(expr)}</code>. Tests joined without -o must all be true.`, mood: 'think', layers: L() }];
      const visited = all.filter(p => w.node(w.abs(p), false));
      visited.forEach((p, i) => {
        const yes = hits.has(p);
        cls[p] = yes ? 'yes' : 'no'; tag[p] = yes ? 'match' : '';
        const verbose = i < 8 || yes;
        if (verbose) fr.push({ msg: `<code>${esc(p)}</code>: ${yes ? 'all tests pass, so find prints it.' : 'the tests fail (or the entry was skipped), so nothing is printed.'}`, mood: yes ? 'happy' : 'look', layers: L() });
      });
      fr.push({ msg: hits.size ? `${hits.size} match${hits.size === 1 ? '' : 'es'}. find prints them in the order it visited them.` : 'Nothing matched, so find prints nothing.', mood: hits.size ? 'wow' : 'think', fx: hits.size ? 'burst' : undefined, layers: L().concat([{ t: 'term', label: 'What the terminal shows', lines: [['c', 'find . ' + expr]].concat(r.out.replace(/\n$/, '').split('\n').filter(Boolean).map(x => ['o', x])) }]) });
      return fr;
    }
  }));

  /* power 3.2 archives: tar packs files into blocks, then gzip or xz squeezes the result */
  def('lx-tar', el => W(el, {
    title: 'Pack, then squeeze',
    sub: 'Name files or folders from your home folder and pick a format. Pip packs each one into the archive block by block, then compresses it, and shows the sizes the practice shell measures.',
    inputs: [{ k: 'files', label: 'Files and folders', type: 'text', val: 'logs notes.txt', w: 300 },
             { k: 'fmt', label: 'Format', type: 'seg', val: 'gz', opts: [['tar', 'tar only'], ['gz', 'tar + gzip'], ['xz', 'tar + xz'], ['zip', 'zip']] }],
    random: () => ({ files: ['logs', 'notes.txt poem.txt', 'scripts logs', 'marks.csv fruits.txt notes.txt', 'photos'][Math.floor(Math.random() * 5)], fmt: ['tar', 'gz', 'xz', 'zip'][Math.floor(Math.random() * 4)] }),
    frames: v => {
      const w = world(), names = String(v.files).trim().split(/\s+/).filter(Boolean), fmt = v.fmt;
      if (!names.length) return [{ msg: 'Type at least one file or folder, for example logs notes.txt.', mood: 'think', layers: [] }];
      const miss = names.filter(n => !w.node(w.abs(n)));
      if (miss.length) return [{ msg: `${esc(miss.join(', '))} is not in your home folder. Try logs, scripts, photos, notes.txt, poem.txt, fruits.txt or marks.csv.`, mood: 'sad', fx: 'shake', layers: [] }];
      const items = []; names.forEach(n => w.collect(w.abs(n), n, items, () => false));
      const out = fmt === 'tar' ? 'backup.tar' : fmt === 'gz' ? 'backup.tar.gz' : fmt === 'xz' ? 'backup.tar.xz' : 'backup.zip';
      const cmd = fmt === 'zip' ? `zip -r ${out} ${names.join(' ')}` : `tar -c${fmt === 'gz' ? 'z' : fmt === 'xz' ? 'J' : ''}vf ${out} ${names.join(' ')}`;
      const size = it => it.data ? new TextEncoder().encode(it.data).length : 0;
      const raw = items.reduce((t, it) => t + size(it), 0);
      const boxes = (k, cls) => items.map((it, i) => [it.path, it.type === 'd' ? 'folder' : size(it) + ' bytes', i < k ? cls : i === k ? 'cur' : '']);
      const fr = [{ msg: `<code>${esc(cmd)}</code>. ${fmt === 'zip' ? 'zip packs and compresses each file on its own, in one step.' : 'tar first glues everything into one file. It does not compress anything by itself.'} Together the files hold ${raw} bytes of data.`, mood: 'think', layers: [{ t: 'flow', label: 'Going into the archive', items: boxes(-1, 'done') }] }];
      let blocks = 0;
      items.forEach((it, i) => {
        const b = 1 + Math.ceil(size(it) / 512); blocks += b;
        if (fmt === 'zip') fr.push({ msg: `<code>${esc(it.path)}</code>: zip writes a small header, then the ${it.type === 'd' ? 'folder entry' : 'data, squeezed if that makes it smaller'}.`, mood: 'look', layers: [{ t: 'flow', label: 'Going into the archive', items: boxes(i, 'done') }] });
        else fr.push({ msg: `<code>${esc(it.path)}</code>: one 512 byte header block with its name, owner, mode and time${it.type === 'd' ? '. A folder has no data.' : `, then ${b - 1} data block${b - 1 === 1 ? '' : 's'} of 512 bytes for its ${size(it)} bytes.`} Running total: ${blocks} block${blocks === 1 ? "" : "s"}.`, mood: 'look', layers: [{ t: 'flow', label: 'Going into the archive', items: boxes(i, 'done') }] });
      });
      const r = w.run(cmd), nd = w.node(w.abs(out)), fin = nd ? w.size(nd) : 0;
      if (fmt !== 'zip') {
        const tarBytes = (blocks + 2) * 512, rec = Math.ceil(tarBytes / 10240) * 10240;
        fr.push({ msg: `Two empty blocks mark the end: ${blocks + 2} blocks, ${tarBytes} bytes. GNU tar then pads the file to a whole record of 20 blocks (10240 bytes), so the tar is <b>${rec} bytes</b>, bigger than the data itself.`, mood: 'wow', layers: [{ t: 'flow', label: 'Sizes', items: [['data', raw + ' bytes', 'look'], ['tar', rec + ' bytes', 'cur']] }] });
        if (fmt !== 'tar') fr.push({ msg: `${fmt === 'gz' ? 'gzip' : 'xz'} now squeezes the whole tar stream. All that padding is zeros, which compress to almost nothing, so the final file is about <b>${fin} bytes</b>. Real numbers on a real machine differ a little.`, mood: 'happy', layers: [{ t: 'flow', label: 'Sizes', items: [['data', raw + ' bytes', 'look'], ['tar', rec + ' bytes', 'done'], [out, fin + ' bytes', 'yes']] }] });
      } else fr.push({ msg: `The finished zip is about <b>${fin} bytes</b>. Each file can be pulled out on its own, without reading the others.`, mood: 'happy', layers: [{ t: 'flow', label: 'Sizes', items: [['data', raw + ' bytes', 'look'], [out, fin + ' bytes', 'yes']] }] });
      const ls = w.run('ls -l ' + out).out;
      fr.push({ msg: 'Done. The original files are still there. Archiving copies them, it does not move them.', mood: 'happy', fx: 'burst', layers: [{ t: 'term', label: 'What the terminal shows', lines: [['c', cmd]].concat(r.out.replace(/\n$/, '').split('\n').filter(Boolean).map(x => ['o', x])).concat([['c', 'ls -l ' + out], ['o', ls.trim()]]) }] });
      return fr;
    }
  }));

  /* power 4.1 jobs and signals: run a list of commands and watch every job change state */
  def('lx-jobs', el => W(el, {
    title: 'Jobs, states and signals',
    sub: 'Type commands separated by commas. Pip runs them one by one in the practice shell and shows every job of this shell with its state. Ctrl+Z is written here as kill -STOP, which sends the same kind of stop signal.',
    inputs: [{ k: 'cmds', label: 'Commands', type: 'text', val: 'sleep 300 &, sleep 600 &, kill -STOP %1, jobs, bg %1, kill %2, fg %1', w: 460 }],
    random: () => ({ cmds: ['sleep 100 &, jobs, kill %1', 'yes > /dev/null &, ps, kill -9 %1', 'sleep 50 &, sleep 20, jobs, sleep 40, jobs', 'sleep 300 &, kill -STOP %1, jobs, kill -CONT %1, jobs', 'nice -n 10 sleep 200 &, ps -o pid,ni,cmd, kill %1', 'sleep 30 &, wait, echo $?'][Math.floor(Math.random() * 6)] }),
    frames: v => {
      const w = world(), cmds = String(v.cmds).split(',').map(x => x.trim()).filter(Boolean);
      if (!cmds.length) return [{ msg: 'Type at least one command, for example sleep 300 &.', mood: 'think', layers: [] }];
      const seen = new Map();
      const table = () => {
        w.jobs.forEach(j => seen.set(j.id + ':' + j.pid, j));
        const items = [...seen.values()].map(j => [`[${j.id}] ${j.cmd}`, `${j.state} · PID ${j.pid}`, j.state === 'Running' ? 'cur' : j.state === 'Stopped' ? 'look' : j.state === 'Done' ? 'yes' : 'no']);
        return items.length ? [{ t: 'flow', label: 'Jobs of this shell', items, plain: true }] : [{ t: 'flow', label: 'Jobs of this shell', items: [['no jobs yet', 'start one with &', '']] }];
      };
      const says = c => /&\s*$/.test(c) ? 'The trailing & starts it in the background. bash prints the job number in brackets and the process ID, then gives the prompt back at once.'
        : /^kill\s+-(STOP|19|TSTP)/i.test(c) ? 'SIGSTOP freezes the process. It keeps its memory but gets no CPU time. Ctrl+Z sends SIGTSTP, which does the same for the job in the foreground.'
        : /^kill\s+-(CONT|18)/i.test(c) ? 'SIGCONT lets a stopped process run again.'
        : /^kill\s+-(9|KILL)/i.test(c) ? 'SIGKILL cannot be caught or ignored. The kernel ends the process at once, with no chance to clean up.'
        : /^kill\b/.test(c) ? 'kill with no signal sends SIGTERM (15), a polite request to finish. A well written program saves its work and exits.'
        : /^bg\b/.test(c) ? 'bg continues a stopped job in the background, as if it had been started with &.'
        : /^fg\b/.test(c) ? 'fg brings a job to the foreground, so the shell waits for it to finish. The practice shell moves its clock forward instead of waiting.'
        : /^jobs\b/.test(c) ? 'jobs lists the jobs this shell started. + marks the current job, the one fg and bg use by default, and - the one before it.'
        : /^sleep\b/.test(c) ? 'A sleep in the foreground: the practice shell moves its clock forward by that many seconds.'
        : /^wait\b/.test(c) ? 'wait pauses until background jobs finish, and its exit status is the status of the job it waited for.'
        : 'The shell runs it as a normal command.';
      const fr = [{ msg: 'Every command you start becomes a process with its own ID. A process started from this shell with & becomes a <b>job</b> too, so the shell can stop, continue or kill it by job number.', mood: 'think', layers: table() }];
      const term = [];
      cmds.forEach((c, i) => {
        const r = w.run(c);
        term.push(['c', c]); r.out.replace(/\n$/, '').split('\n').filter(x => x !== '').forEach(x => term.push(['o', x]));
        fr.push({ msg: `<code>${esc(c)}</code>: ${says(c)}`, mood: /kill/.test(c) ? 'wow' : 'look', fx: /kill\s+(-9|-KILL|%|\d)/.test(c) ? 'shake' : undefined, layers: table().concat([{ t: 'term', label: 'Terminal', lines: term.slice(-10) }]) });
      });
      fr.push({ msg: 'That is the whole life of a job: started, maybe stopped and continued, and finally done or ended by a signal.', mood: 'happy', fx: 'burst', layers: table().concat([{ t: 'term', label: 'Terminal', lines: term.slice(-12) }]) });
      return fr;
    }
  }));

  /* power 4.2 how bash finds a command: alias, function, builtin, then each folder of PATH in order */
  def('lx-cmdpath', el => W(el, {
    title: 'How bash finds a command',
    sub: 'Type a command name and a PATH. Pip checks aliases and builtins first, then looks in each PATH folder from left to right and runs the first match. The practice computer has a script called tool in ~/bin.',
    inputs: [{ k: 'name', label: 'Command', type: 'text', val: 'tool', w: 120 }, { k: 'path', label: 'PATH', type: 'text', val: '/home/learner/bin:/usr/local/bin:/usr/bin:/bin', w: 360 }],
    random: () => [{ name: 'ls', path: '/usr/local/bin:/usr/bin:/bin' }, { name: 'tool', path: '/usr/local/bin:/usr/bin:/bin' }, { name: 'll', path: '/usr/bin:/bin' }, { name: 'cd', path: '/usr/bin' }, { name: 'grep', path: '/home/learner/bin' }, { name: 'tool', path: '/home/learner/bin:/usr/bin' }][Math.floor(Math.random() * 6)],
    frames: v => {
      const w = world(), name = String(v.name).trim(), path = String(v.path).trim();
      if (!/^[\w.-]+$/.test(name)) return [{ msg: 'Type one command name without spaces or slashes, for example ls or tool.', mood: 'think', layers: [] }];
      w.run('mkdir -p ~/bin'); w.run('printf "#!/bin/bash\\necho tool from ~/bin\\n" > ~/bin/tool && chmod +x ~/bin/tool');
      w.vars.PATH = path;
      const dirs = path.split(':');
      const steps = [['alias?', '', ''], ['builtin?', '', '']].concat(dirs.map(d => [d || '(empty = current folder)', '', '']));
      const L = (cls, note) => [{ t: 'flow', label: 'Where bash looks, in order', items: steps.map((x, i) => [x[0], note[i] || '', cls[i] || '']) }];
      const cls = [], note = [];
      const fr = [{ msg: `You typed <code>${esc(name)}</code>. Before it searches any folder, bash checks whether the word is an alias, a function or a builtin command.`, mood: 'think', layers: L(cls, note) }];
      if (w.aliases[name]) { cls[0] = 'yes'; note[0] = esc(w.aliases[name]); fr.push({ msg: `<code>${esc(name)}</code> is an alias for <code>${esc(w.aliases[name])}</code>. bash swaps it in and starts again with the first word of that text.`, mood: 'wow', fx: 'burst', layers: L(cls, note) }); return fr; }
      cls[0] = 'no'; note[0] = 'no';
      fr.push({ msg: 'Not an alias.', mood: 'look', layers: L(cls, note) });
      if (['cd', 'echo', 'pwd', 'export', 'alias', 'history', 'type', 'source', 'exit', 'read', 'test', 'jobs', 'fg', 'bg', 'kill', 'printf', 'set', 'unset', 'declare'].includes(name)) { cls[1] = 'yes'; note[1] = 'built in'; fr.push({ msg: `<code>${esc(name)}</code> is built into bash, so no folder is searched at all. cd must be a builtin: a separate program could not change the folder of the shell that started it.`, mood: 'wow', fx: 'burst', layers: L(cls, note) }); return fr; }
      cls[1] = 'no'; note[1] = 'no';
      fr.push({ msg: 'Not a builtin either, so bash walks through the folders of PATH, split at each colon.', mood: 'look', layers: L(cls, note) });
      let found = null;
      dirs.forEach((d, k) => {
        if (found) return;
        const i = k + 2, full = (d || '.') + '/' + name, n = w.node(w.abs(full));
        if (n && n.type === 'f' && (n.mode & 0o111)) { found = full; cls[i] = 'yes'; note[i] = 'found ' + name; fr.push({ msg: `<code>${esc(full)}</code> exists and is executable. bash stops here and runs it. Folders further right are never checked.`, mood: 'happy', layers: L(cls, note) }); }
        else { cls[i] = 'no'; note[i] = 'not here'; fr.push({ msg: `No executable <code>${esc(name)}</code> in <code>${esc(d || '.')}</code>.`, mood: 'look', layers: L(cls, note) }); }
      });
      const r = w.run(name);
      fr.push({ msg: found ? `Done. bash remembers the place in a small table (see <code>hash</code>), so the next time it does not search again.` : `No folder had it, so bash prints the famous error and sets the exit status to 127.`, mood: found ? 'happy' : 'sad', fx: found ? 'burst' : 'shake', layers: L(cls, note).concat([{ t: 'term', label: 'What the terminal shows', lines: [['c', name]].concat(r.out.replace(/\n$/, '').split('\n').filter(Boolean).map(x => [/not found/.test(x) ? 'e' : 'o', x])) }]) });
      return fr;
    }
  }));

  /* scripting 1.1 arguments: how a command line becomes $0, $1, $2 ... and what "$@" and "$*" give */
  def('lx-args', el => W(el, {
    title: 'From command line to $1, $2, $3',
    sub: 'Type how you would run a script, with any quotes you like. Pip splits it into words exactly as bash does and fills the special variables the script sees.',
    inputs: [{ k: 'line', label: 'Command line', type: 'text', val: './greet.sh Asha "New Delhi" 42', w: 380 }],
    random: () => ({ line: ['./greet.sh Asha "New Delhi" 42', "./backup.sh -v /home/asha 'My Files'", './sum.sh 10 20 30 40', './copy.sh "a b" c\\ d e', './empty.sh "" two'][Math.floor(Math.random() * 5)] }),
    frames: v => {
      const w = world(), line = String(v.line).trim();
      let words; try { words = w.lex(line).filter(t => t.w).map(t => t.w); } catch (e) { return [{ msg: 'bash could not read that line: ' + esc(e.message), mood: 'sad', fx: 'shake', layers: [] }]; }
      if (!words.length) return [{ msg: 'Type a command line, for example ./greet.sh Asha "New Delhi".', mood: 'think', layers: [] }];
      const vals = words.map(x => w.expandWord(x).join(' '));
      const box = (lab, val, cls) => [lab, val === '' ? '(empty)' : val, cls];
      const fr = [{ msg: `bash first splits <code>${esc(line)}</code> into words at spaces that are not inside quotes or escaped with a backslash. The quotes themselves are removed.`, mood: 'think', layers: [{ t: 'flow', label: 'Words', items: vals.map((x, i) => [x === '' ? '(empty)' : x, 'word ' + i, '']), plain: true }] }];
      const items = [];
      vals.forEach((x, i) => { items.push(box('$' + i, x, i === 0 ? 'look' : 'cur')); fr.push({ msg: i === 0 ? `Word 0 is the command itself. Inside the script it is <code>$0</code>: <b>${esc(x)}</b>.` : `Word ${i} becomes <code>$${i > 9 ? '{' + i + '}' : i}</code>: <b>${esc(x || '(an empty string)')}</b>${/\s/.test(x) ? '. The quotes kept the space inside one argument.' : '.'}`, mood: 'look', layers: [{ t: 'flow', label: 'What the script sees', items: items.slice(), plain: true }] }); });
      const args = vals.slice(1);
      fr.push({ msg: `<code>$#</code> is the number of arguments, not counting $0: <b>${args.length}</b>.`, mood: 'happy', layers: [{ t: 'flow', label: 'What the script sees', items: items.concat([['$#', String(args.length), 'yes']]), plain: true }] });
      fr.push({ msg: '<code>"$@"</code> (with the quotes) gives every argument back as its own word, exactly as typed. Use it to pass arguments on to another command.', mood: 'look', layers: [{ t: 'flow', label: '"$@" gives ' + args.length + ' word' + (args.length === 1 ? '' : 's'), items: args.map(x => [x === '' ? '(empty)' : x, '', 'yes']), plain: true }] });
      fr.push({ msg: '<code>"$*"</code> glues all arguments into one word with spaces between them.', mood: 'look', layers: [{ t: 'flow', label: '"$*" gives 1 word', items: [[args.join(' ') || '(empty)', '', 'look']], plain: true }] });
      const loose = args.join(' ').split(/\s+/).filter(Boolean);
      fr.push({ msg: `Without quotes, <code>$@</code> and <code>$*</code> are split again at every space, giving ${loose.length} word${loose.length === 1 ? '' : 's'}${loose.length !== args.length ? ', which breaks arguments that contain spaces or are empty' : ''}. That is why scripts almost always write "$@".`, mood: loose.length !== args.length ? 'wow' : 'happy', fx: loose.length !== args.length ? 'shake' : 'burst', layers: [{ t: 'flow', label: 'Unquoted $@ gives ' + loose.length + ' word' + (loose.length === 1 ? '' : 's'), items: loose.map(x => [x, '', loose.length !== args.length ? 'no' : 'yes']), plain: true }] });
      return fr;
    }
  }));

  /* scripting 1.2 the order of expansions on one command line */
  def('lx-expand', el => W(el, {
    title: 'The expansions, in order',
    sub: 'Type a command line. Pip applies the shell expansions one stage at a time, in the order the bash manual gives, and then runs the result in the practice shell.',
    inputs: [{ k: 'line', label: 'Command line', type: 'text', val: 'echo {a,b}.txt ~ $USER "$HOME" $(whoami) $((6*7)) *.csv', w: 440 }],
    random: () => ({ line: ['echo file{1..3}.log', 'echo "$USER has $(ls logs | wc -l) logs"', "echo '$HOME' \"$HOME\" $HOME", 'echo *.txt', 'name="a   b"; echo $name "$name"', 'echo ~/notes.txt $((2**10))', 'echo {x,y}{1,2}'][Math.floor(Math.random() * 7)] }),
    frames: v => {
      const w = world(), all = String(v.line).trim();
      const cut = all.lastIndexOf(';'), pre = cut >= 0 ? all.slice(0, cut) : '', line = cut >= 0 ? all.slice(cut + 1).trim() : all;
      if (pre) w.run(pre);
      let toks; try { toks = w.lex(line); } catch (e) { return [{ msg: 'bash could not read that line: ' + esc(e.message), mood: 'sad', fx: 'shake', layers: [] }]; }
      if (toks.some(t => t.op)) {
        const r = w.run(line);
        return [{ msg: 'This animation follows one simple command. Your line has pipes or redirections, so here is just its result.', mood: 'think', layers: [{ t: 'term', label: 'Result', lines: [['c', line]].concat(r.out.replace(/\n$/, '').split('\n').filter(Boolean).map(x => ['o', x])) }] }];
      }
      /* a word is a list of parts {t, q}. show() draws it with its quotes still on */
      let words = toks.filter(t => t.w).map(t => t.w.parts.map(p => ({ t: p.t, q: p.q })));
      if (!words.length) return [{ msg: 'Type a command line, for example echo {a,b}.txt $HOME.', mood: 'think', layers: [] }];
      const show = ws => ws.map(ps => ps.map(p => p.q === 1 ? `'${p.t}'` : p.q === 2 ? `"${p.t}"` : p.t).join(''));
      const L = (label, ws, cls) => [{ t: 'flow', label, items: show(ws).map((x, i) => [x || '(empty)', '', cls && cls[i] || '']), plain: true }];
      const fr = [{ msg: `bash has split <code>${esc(line)}</code> into words. Now it expands them, stage by stage. Quotes are still in place and decide what each stage may touch.`, mood: 'think', layers: L('Words as typed', words) }];
      const stage = (n, name, fn, why) => {
        const before = JSON.stringify(words);
        const cls = [], next = [];
        words.forEach(ps => { const r = fn(ps); r.forEach(x => { next.push(x); cls.push(r.length === 1 && JSON.stringify(x) === JSON.stringify(ps) ? '' : 'yes'); }); });
        words = next;
        const changed = JSON.stringify(words) !== before;
        fr.push({ msg: `<b>${n}. ${name}.</b> ${why} ${changed ? '' : '<i>Nothing to do on this line.</i>'}`, mood: changed ? 'wow' : 'look', layers: L(`After stage ${n}`, words, cls) });
      };
      const unq = ps => ps.every(p => !p.q);
      stage(1, 'Brace expansion', ps => unq(ps) && ps.length === 1 && /\{[^{}]*(,|\.\.)[^{}]*\}/.test(ps[0].t) ? w.braces(ps[0].t).map(t => [{ t, q: 0 }]) : [ps], '{a,b} and {1..5} make several words. It is pure text work and happens first, before any variable is read.');
      stage(2, 'Tilde expansion', ps => ps[0].q === 0 && (ps[0].t === '~' || ps[0].t.startsWith('~/')) ? [[{ t: '/home/learner' + ps[0].t.slice(1), q: 0 }].concat(ps.slice(1))] : [ps], 'A ~ at the start of an unquoted word becomes your home folder.');
      stage(3, 'Parameter, arithmetic and command substitution', ps => [ps.map(p => p.q === 1 || !/\$/.test(p.t) ? p : { t: w.expandStr(p.t), q: p.q, sub: !p.q })], '$NAME, $((maths)) and $(command) are replaced by their values, from left to right. Single quotes protect their text completely, double quotes still allow this stage.');
      stage(4, 'Word splitting', ps => { if (!ps.some(p => p.sub)) return [ps]; const parts = ps.map(p => p.t).join('').split(/\s+/).filter(Boolean); return parts.map(t => [{ t, q: 0 }]); }, 'Results of stage 3 that were <b>not</b> in double quotes are split at spaces, tabs and newlines into separate words. An empty unquoted result disappears.');
      stage(5, 'Pathname expansion (globbing)', ps => { if (!unq(ps)) return [ps]; const t = ps.map(p => p.t).join(''); if (!/[*?[]/.test(t)) return [ps]; const g = w.glob(t); return g.length ? g.map(x => [{ t: x, q: 0 }]) : [ps]; }, 'Unquoted words with * ? or [ ] are replaced by matching file names, sorted. If nothing matches, the word stays as it is.');
      stage(6, 'Quote removal', ps => [[{ t: ps.map(p => p.t).join(''), q: 0 }]], 'Finally the quote characters themselves are removed. What is left are the exact arguments the command receives.');
      const r = w.run(line);
      fr.push({ msg: `The command now runs with ${words.length - 1} argument${words.length === 2 ? '' : 's'}.`, mood: 'happy', fx: 'burst', layers: L('Final arguments', words, words.map(() => 'cur')).concat([{ t: 'term', label: 'What the terminal shows', lines: [['c', line]].concat(r.out.replace(/\n$/, '').split('\n').filter(x => x !== '').map(x => ['o', x])) }]) });
      return fr;
    }
  }));

  /* scripting 2.1 what test and [ ] really receive, and why [[ ]] is safer */
  def('lx-test', el => W(el, {
    title: 'What the test command really sees',
    sub: 'Set some variables, then type a test in [ ] or [[ ]]. Pip expands it exactly as bash would, counts the arguments that reach test, and shows which rule decides the answer.',
    inputs: [{ k: 'setup', label: 'Variables', type: 'text', val: 'x=""; n=7', w: 200 }, { k: 'test', label: 'Test', type: 'text', val: '[ $x = yes ]', w: 260 }],
    random: () => [{ setup: 'x=""; n=7', test: '[ $x = yes ]' }, { setup: 'x=""; n=7', test: '[[ $x = yes ]]' }, { setup: 'n=7', test: '[ $n -gt 5 ]' }, { setup: 'f="My Report.txt"', test: '[ -f $f ]' }, { setup: 'name=asha', test: '[[ $name == a* ]]' }, { setup: 'n=abc', test: '[ $n -eq 3 ]' }, { setup: 'x=hello', test: '[ -n "$x" ]' }][Math.floor(Math.random() * 7)],
    frames: v => {
      const w = world(), setup = String(v.setup || '').trim(), line = String(v.test || '').trim();
      if (setup) w.run(setup);
      const dbl = /^\[\[\s.*\s\]\]$/.test(line), sq = /^\[\s.*\s\]$/.test(line) || /^test\s/.test(line);
      if (!dbl && !sq) return [{ msg: 'Type a test that starts with [ and a space and ends with a space and ], or one in [[ ]], for example [ -f notes.txt ].', mood: 'think', layers: [] }];
      const fr = [{ msg: `${setup ? `First the variables are set: <code>${esc(setup)}</code>. ` : ''}Now bash reads <code>${esc(line)}</code>.`, mood: 'think', layers: [{ t: 'term', label: 'The line', lines: [['c', line]] }] }];
      const r = w.run(line), err = r.out.replace(/\n$/, '');
      const status = [{ t: 'flow', label: 'Exit status', items: [[String(r.code), r.code === 0 ? 'true' : r.code === 1 ? 'false' : 'error', r.code === 0 ? 'yes' : r.code === 1 ? 'look' : 'no']], plain: true }];
      if (dbl) {
        fr.push({ msg: '<code>[[ ]]</code> is part of the bash language, not a command. Inside it bash does <b>no word splitting and no globbing</b>, so an empty or spaced variable stays exactly one value.', mood: 'look', layers: [] });
        const inner = line.replace(/^\[\[\s*|\s*\]\]$/g, '');
        let toks = []; try { toks = w.lex(inner).filter(t => t.w).map(t => t.w); } catch (e) { toks = []; }
        const items = toks.map(t => { const raw = t.parts.map(p => p.t).join(''); const val = /^(==?|!=|=~|<|>|-[a-z]{1,2}|&&|\|\||!)$/.test(raw) && !t.parts.some(p => p.q) ? raw : t.parts.map(p => p.q === 1 ? p.t : w.expandStr(p.t)).join(''); return [val === '' ? '(empty)' : val, raw === val ? '' : raw, val === '' ? 'look' : 'cur']; });
        fr.push({ msg: 'These are the values [[ ]] compares. After <code>==</code> and <code>!=</code> an unquoted right side is a <b>pattern</b>, and after <code>=~</code> it is a regular expression.', mood: 'look', layers: [{ t: 'flow', label: 'Values inside [[ ]]', items, plain: true }] });
        fr.push({ msg: err ? `bash says: <code>${esc(err)}</code>` : `The test is <b>${r.code === 0 ? 'true' : 'false'}</b>, so the exit status is ${r.code}.`, mood: r.code === 0 ? 'happy' : r.code === 1 ? 'look' : 'sad', fx: r.code === 0 ? 'burst' : r.code > 1 ? 'shake' : undefined, layers: status });
        return fr;
      }
      let toks = []; try { toks = w.lex(line).filter(t => t.w).map(t => t.w); } catch (e) { return [{ msg: 'bash could not read that line: ' + esc(e.message), mood: 'sad', fx: 'shake', layers: [] }]; }
      const words = toks.flatMap(t => w.expandWord(t));
      const args = words.slice(1, words[0] === '[' && words[words.length - 1] === ']' ? -1 : undefined);
      const lost = toks.length - words.length;
      fr.push({ msg: `<code>[</code> is an ordinary command, another name for <code>test</code>. So its arguments go through normal expansion and word splitting first${lost > 0 ? `. ${lost} word${lost === 1 ? '' : 's'} vanished because an unquoted variable was empty` : lost < 0 ? '. An unquoted variable with spaces was split into extra words' : ''}.`, mood: lost ? 'wow' : 'look', fx: lost ? 'shake' : undefined, layers: [{ t: 'flow', label: `test receives ${args.length} argument${args.length === 1 ? '' : 's'}`, items: args.map(a => [a === '' ? '(empty)' : a, '', lost ? 'no' : 'cur']), plain: true }] });
      const n = args.length;
      const rule = n === 0 ? 'With <b>0 arguments</b> the answer is always false.'
        : n === 1 ? 'With <b>1 argument</b> test is true when that argument is not empty.'
        : n === 2 ? (args[0] === '!' ? 'With <b>2 arguments</b> starting with !, test negates the 1-argument rule.' : `With <b>2 arguments</b> the first must be a unary operator such as -f, -d, -z or -n. Here it is <code>${esc(args[0])}</code>.`)
        : n === 3 ? `With <b>3 arguments</b> the middle one must be a binary operator such as =, !=, -eq or -lt. Here it is <code>${esc(args[1])}</code>.`
        : 'With <b>4 or more arguments</b> test needs ! or the -a and -o connectors, otherwise there are too many arguments.';
      fr.push({ msg: rule + ' These rules by argument count come from the test entry in the bash manual.', mood: 'think', layers: [{ t: 'flow', label: `test receives ${n} argument${n === 1 ? '' : 's'}`, items: args.map(a => [a === '' ? '(empty)' : a, '', 'cur']), plain: true }] });
      fr.push({ msg: err ? `bash says: <code>${esc(err)}</code>${lost > 0 ? ' Quote the variable, as in "$x", or use [[ ]], and the empty value stays an argument.' : lost < 0 ? ' Quote the variable, as in "$f", or use [[ ]], and the value stays one argument.' : ''}` : `The test is <b>${r.code === 0 ? 'true' : 'false'}</b>, so the exit status is ${r.code}.`, mood: r.code === 0 ? 'happy' : r.code === 1 ? 'look' : 'sad', fx: r.code === 0 ? 'burst' : r.code > 1 ? 'shake' : undefined, layers: status });
      return fr;
    }
  }));

  /* scripting 2.1 case: patterns tried from top to bottom, the first match wins */
  def('lx-case', el => W(el, {
    title: 'case: the first matching pattern wins',
    sub: 'Type a value and some case arms, separated by semicolons. Pip tries every pattern from the top, as bash does, and runs the first arm that matches.',
    inputs: [{ k: 'value', label: 'Value', type: 'text', val: 'holiday.JPG', w: 160 }, { k: 'arms', label: 'Arms', type: 'text', val: '*.txt) text file ; *.jpg|*.[Jj][Pp][Gg]) photo ; *) something else', w: 420 }],
    random: () => [{ value: 'holiday.JPG', arms: '*.txt) text file ; *.jpg|*.[Jj][Pp][Gg]) photo ; *) something else' }, { value: 'YES', arms: '[yY]|[yY][eE][sS]) agreed ; [nN]*) refused ; *) please answer' }, { value: 'start', arms: 'start) starting ; stop) stopping ; restart) restarting ; *) usage: start or stop' }, { value: 'report-2026.csv', arms: '*.csv) table ; report-*) report ; *) other' }, { value: '42', arms: '*[!0-9]*) not a number ; ?|??) small number ; *) big number' }][Math.floor(Math.random() * 5)],
    frames: v => {
      const w = world(), val = String(v.value);
      const arms = String(v.arms).split(';').map(x => x.trim()).filter(Boolean).map(a => { const k = a.indexOf(')'); return k < 0 ? null : [a.slice(0, k).trim().replace(/^\(/, ''), a.slice(k + 1).trim()]; });
      if (!arms.length || arms.some(a => !a || !a[0])) return [{ msg: 'Write each arm as pattern) words, for example *.txt) text file, and separate arms with semicolons.', mood: 'think', layers: [] }];
      const q = s => "'" + s.replace(/'/g, "'\\''") + "'";
      const rows = arms.map(([p, act]) => [p + ')', act, '']);
      const fr = [{ msg: `bash compares <b>${esc(val)}</b> with each pattern in turn. Patterns use the same wildcards as file names: * ? and [ ], and | separates choices.`, mood: 'think', layers: [{ t: 'flow', label: 'case "$value" in', items: rows.map(r => r.slice()), plain: true }] }];
      let hit = -1;
      for (let i = 0; i < arms.length && hit < 0; i++) {
        const pats = arms[i][0].split('|');
        for (const p of pats) {
          const ok = w.run(`[[ ${q(val)} == ${p} ]]`).code === 0;
          const cur = rows.map((r, j) => [r[0], r[1], j < i ? 'no' : j === i ? (ok ? 'yes' : 'look') : '']);
          fr.push({ msg: `Does <b>${esc(val)}</b> match <code>${esc(p)}</code>? ${ok ? '<b>Yes.</b>' : 'No.'}${!ok && val !== val.toLowerCase() && w.run(`[[ ${q(val.toLowerCase())} == ${p} ]]`).code === 0 ? ' It would match in small letters, because patterns are case sensitive.' : ''}`, mood: ok ? 'wow' : 'look', layers: [{ t: 'flow', label: 'case "$value" in', items: cur, plain: true }] });
          if (ok) { hit = i; break; }
        }
      }
      const final = rows.map((r, j) => [r[0], r[1], j === hit ? 'yes' : j < hit || hit < 0 ? 'no' : 'ghost']);
      fr.push(hit < 0
        ? { msg: 'No pattern matched, so case runs nothing and its exit status is 0. A last arm <code>*)</code> catches everything else.', mood: 'sad', layers: [{ t: 'flow', label: 'case "$value" in', items: final, plain: true }] }
        : { msg: `The arm <code>${esc(arms[hit][0])})</code> runs and prints <b>${esc(arms[hit][1])}</b>. With <code>;;</code> at its end, case stops here and the later arms are never tried.`, mood: 'happy', fx: 'burst', layers: [{ t: 'flow', label: 'case "$value" in', items: final, plain: true }, { t: 'term', label: 'Output', lines: [['o', arms[hit][1]]] }] });
      return fr;
    }
  }));

  /* scripting 2.2 a loop, one pass at a time: for over words, C-style for, and while read over the lines of a file */
  def('lx-loop', el => W(el, {
    title: 'A loop, one pass at a time',
    sub: 'Type a loop header and a body. Pip works out the list first, then runs the body once per item and shows the loop variable and the output of every pass.',
    inputs: [{ k: 'head', label: 'Loop header', type: 'text', val: 'for f in *.txt', w: 260 }, { k: 'body', label: 'Body', type: 'text', val: 'echo "$f: $(wc -l < "$f") lines"', w: 300 }],
    random: () => [{ head: 'for f in *.txt', body: 'echo "$f: $(wc -l < "$f") lines"' }, { head: 'for n in {1..5}', body: 'echo "$n squared is $((n * n))"' }, { head: 'for ((i = 10; i > 0; i -= 3))', body: 'echo "countdown $i"' }, { head: 'while IFS=, read -r name subject score', body: 'echo "$name scored $score"', file: 'marks.csv' }, { head: 'for word in "New Delhi" Pune "Navi Mumbai"', body: 'echo "city: $word"' }, { head: 'while read -r fruit', body: 'echo "${fruit^^}"' }][Math.floor(Math.random() * 6)],
    frames: v => {
      const w = world(), head = String(v.head).trim().replace(/;?\s*do$/, ''), body = String(v.body).trim();
      const passes = [], cap = 12;
      let m, fr = [], kind = '';
      const out = r => r.out.replace(/\n$/, '').split('\n').filter(x => x !== '');
      const term = [];
      const pass = (label, vars) => {
        Object.assign(w.vars, vars);
        const r = w.run(body); const o = out(r);
        o.forEach(x => term.push(['o', x]));
        passes.push(label);
        return o;
      };
      if ((m = /^for\s+([A-Za-z_]\w*)\s+in\s+(.*)$/.exec(head))) {
        kind = 'list';
        let words; try { words = w.lex(m[2]).filter(t => t.w).flatMap(t => w.expandWord(t.w)); } catch (e) { return [{ msg: 'bash could not read that list: ' + esc(e.message), mood: 'sad', fx: 'shake', layers: [] }]; }
        fr.push({ msg: `First bash expands the list after <code>in</code>, once, before the loop starts. Here it gives <b>${words.length}</b> item${words.length === 1 ? '' : 's'}.${!words.length ? ' An empty list means the body never runs.' : ''}`, mood: 'think', layers: [{ t: 'flow', label: 'The list', items: words.map(x => [x, '', 'cur']), plain: true }] });
        words.slice(0, cap).forEach((x, i) => {
          const o = pass(x, { [m[1]]: x });
          fr.push({ msg: `Pass ${i + 1}: <code>${esc(m[1])}</code> is <b>${esc(x)}</b>. The body runs${o.length ? ` and prints <b>${esc(o.join(' / '))}</b>` : ' and prints nothing'}.`, mood: 'work', layers: [{ t: 'flow', label: 'The list', items: words.map((y, j) => [y, '', j < i ? 'no' : j === i ? 'yes' : 'cur']), plain: true }, { t: 'term', label: 'Output so far', lines: term.slice() }] });
        });
        if (words.length > cap) fr.push({ msg: `The animation stops after ${cap} passes. The real loop would go on for all ${words.length} items.`, mood: 'look', layers: [] });
      } else if ((m = /^for\s*\(\((.*);(.*);(.*)\)\)$/.exec(head))) {
        kind = 'c';
        const [init, cond, step] = [m[1].trim(), m[2].trim(), m[3].trim()];
        try { if (init) w.arith(init); } catch (e) { return [{ msg: 'The first part could not be worked out: ' + esc(e.message), mood: 'sad', fx: 'shake', layers: [] }]; }
        fr.push({ msg: `A C-style loop has three parts. <code>${esc(init || '(nothing)')}</code> runs once at the start. <code>${esc(cond || '(always true)')}</code> is checked before every pass. <code>${esc(step || '(nothing)')}</code> runs after every pass.`, mood: 'think', layers: [] });
        let i = 0;
        while (i < cap) {
          let ok; try { ok = cond ? w.arith(cond) !== 0 : true; } catch (e) { fr.push({ msg: 'The test could not be worked out: ' + esc(e.message), mood: 'sad', layers: [] }); break; }
          const shown = Object.keys(w.vars).filter(k => new RegExp('\\b' + k + '\\b').test(cond || init)).map(k => `${k}=${w.vars[k]}`).join(', ');
          if (!ok) { fr.push({ msg: `Check <code>${esc(cond)}</code> with ${esc(shown)}: <b>false</b>, so the loop ends.`, mood: 'look', layers: [{ t: 'term', label: 'Output', lines: term.slice() }] }); break; }
          const o = pass(shown, {});
          fr.push({ msg: `Check <code>${esc(cond || 'true')}</code> with ${esc(shown || 'no variables')}: true. Pass ${i + 1} prints <b>${esc(o.join(' / ') || 'nothing')}</b>. Then <code>${esc(step || 'nothing')}</code> runs.`, mood: 'work', layers: [{ t: 'term', label: 'Output so far', lines: term.slice() }] });
          try { if (step) w.arith(step); } catch (e) { break; }
          i++;
        }
        if (i >= cap) fr.push({ msg: `The animation stops after ${cap} passes.`, mood: 'look', layers: [] });
      } else if ((m = /^while\s+(?:(IFS=\S*)\s+)?read\s+(?:-r\s+)?(.+)$/.exec(head))) {
        kind = 'read';
        const file = v.file || (/IFS=,/.test(head) ? 'marks.csv' : 'fruits.txt'), n = w.node(w.abs(file));
        const names = m[2].trim().split(/\s+/), ifs = m[1] ? m[1].slice(4).replace(/^['"]|['"]$/g, '') : null;
        const lines = n ? n.data.replace(/\n$/, '').split('\n') : [];
        fr.push({ msg: `<code>while read</code> reads one line of input per pass, here from <code>done &lt; ${esc(file)}</code>. It splits the line at ${ifs === null ? 'spaces and tabs' : ifs === '' ? 'nothing (IFS is empty)' : `<code>${esc(ifs)}</code>`} into ${names.map(x => '<code>' + esc(x) + '</code>').join(', ')}, the last name taking the rest. When no line is left, read fails and the loop ends.`, mood: 'think', layers: [{ t: 'flow', label: file, items: lines.map(x => [x, '', 'cur']), plain: true }] });
        lines.slice(0, cap).forEach((line, i) => {
          if (ifs !== null) w.vars.IFS = ifs;
          w.run(`read -r ${names.join(' ')} <<< ${"'" + line.replace(/'/g, "'\\''") + "'"}`);
          if (ifs !== null) delete w.vars.IFS;
          const vals = names.map(x => [x + '=' + (w.vars[x] ?? ''), '', 'look']);
          const o = pass(line, {});
          fr.push({ msg: `Pass ${i + 1} reads <b>${esc(line)}</b>. The body prints <b>${esc(o.join(' / ') || 'nothing')}</b>.`, mood: 'work', layers: [{ t: 'flow', label: file, items: lines.map((y, j) => [y, '', j < i ? 'no' : j === i ? 'yes' : 'cur']), plain: true }, { t: 'flow', label: 'Variables', items: vals, plain: true }, { t: 'term', label: 'Output so far', lines: term.slice() }] });
        });
        if (lines.length > cap) fr.push({ msg: `The animation stops after ${cap} lines.`, mood: 'look', layers: [] });
        else fr.push({ msg: 'No line is left, so read returns status 1 and the while loop stops.', mood: 'look', layers: [] });
      } else return [{ msg: 'Try a header like for f in *.txt, for ((i = 0; i < 5; i++)) or while read -r line.', mood: 'think', layers: [] }];
      fr.push({ msg: `Done: the body ran <b>${passes.length}</b> time${passes.length === 1 ? '' : 's'}.${kind === 'list' ? ' The loop variable keeps its last value after done.' : ''}`, mood: 'happy', fx: 'burst', layers: [{ t: 'term', label: 'All output', lines: term.slice() }] });
      return fr;
    }
  }));

  /* scripting 3.1 the call stack and local: bash looks a variable up from the newest call outwards (dynamic scope) */
  def('lx-scope', el => W(el, {
    title: 'Who sees which variable',
    sub: 'main sets x, then calls f, and f calls g. Choose whether f declares x as local and pick the values. Pip builds the call stack and shows which x every line reads, then checks it in the practice shell.',
    inputs: [{ k: 'outer', label: 'main sets x to', type: 'text', val: 'red', w: 110 }, { k: 'inner', label: 'f sets x to', type: 'text', val: 'blue', w: 110 },
             { k: 'mode', label: 'In f', type: 'seg', val: 'local', opts: [['local', 'local x=...'], ['plain', 'x=... (no local)']] }],
    random: () => ({ outer: ['red', 'Pune', '10'][Math.floor(Math.random() * 3)], inner: ['blue', 'Delhi', '99'][Math.floor(Math.random() * 3)], mode: Math.random() < 0.5 ? 'local' : 'plain' }),
    frames: v => {
      const w = world(), O = String(v.outer).replace(/[^\w.-]/g, '') || 'red', I = String(v.inner).replace(/[^\w.-]/g, '') || 'blue', loc = v.mode === 'local';
      const src = `x=${O}\ng() { echo "g sees $x"; }\nf() { ${loc ? 'local ' : ''}x=${I}; echo "f sees $x"; g; }\nf\necho "main sees $x"`;
      const real = w.run(src.replace(/\n/g, '; ').replace(/\{; /g, '{ ')).out.replace(/\n$/, '').split('\n');
      const stack = (rows, cur) => ({ t: 'flow', label: 'Call stack, newest on the right', items: rows.map(([n, vars], i) => [n, vars, i === cur ? 'cur' : '']), plain: true });
      const term = [];
      const code = { t: 'term', label: 'The script', lines: src.split('\n').map(l => ['c', l]) };
      const fr = [{ msg: 'bash keeps a <b>call stack</b>: one frame for the script itself (main) and one more for each function call that is still running.', mood: 'think', layers: [code] }];
      fr.push({ msg: `main runs <code>x=${esc(O)}</code>. That is a <b>global</b> variable, stored in main’s frame.`, mood: 'look', layers: [stack([['main', `x=${O}`]], 0)] });
      const fVars = loc ? `local x=${I}` : '(no variables of its own)', mainX = loc ? O : I;
      fr.push({ msg: loc ? `f runs <code>local x=${esc(I)}</code>. A new x is created in f’s own frame. main’s x is hidden, not changed.` : `f runs <code>x=${esc(I)}</code> without local. bash looks for an existing x, finds it in main, and <b>changes main’s x</b>.`, mood: loc ? 'look' : 'wow', fx: loc ? undefined : 'shake', layers: [stack([['main', `x=${mainX}`], ['f', fVars]], 1)] });
      term.push(['o', real[0] || '']);
      fr.push({ msg: `f prints its x: <b>${esc(real[0] || '')}</b>.`, mood: 'look', layers: [stack([['main', `x=${mainX}`], ['f', fVars]], 1), { t: 'term', label: 'Output', lines: term.slice() }] });
      term.push(['o', real[1] || '']);
      fr.push({ msg: `f calls g. g has no x of its own, so bash searches the stack from the newest frame outwards and finds ${loc ? 'f’s local x' : 'main’s x'}. This is called <b>dynamic scope</b>: g sees the variables of whoever called it. g prints <b>${esc(real[1] || '')}</b>.`, mood: 'wow', layers: [stack([['main', `x=${mainX}`], ['f', fVars], ['g', '(nothing)']], 2), { t: 'term', label: 'Output', lines: term.slice() }] });
      fr.push({ msg: `g returns, then f returns. Their frames are removed${loc ? ', and the local x goes with them' : ''}.`, mood: 'look', layers: [stack([['main', `x=${mainX}`]], 0)] });
      term.push(['o', real[2] || '']);
      fr.push({ msg: loc ? `main still has its own value: <b>${esc(real[2] || '')}</b>. local protected it.` : `main now sees <b>${esc(real[2] || '')}</b>. The function changed a global variable by accident. Declare helper variables with local to avoid this.`, mood: loc ? 'happy' : 'sad', fx: loc ? 'burst' : 'shake', layers: [stack([['main', `x=${mainX}`]], 0), { t: 'term', label: 'Output, checked in the practice shell', lines: term.slice() }] });
      return fr;
    }
  }));

  /* scripting 3.2 an array as numbered boxes, changed one command at a time */
  def('lx-array', el => W(el, {
    title: 'An array, box by box',
    sub: 'Create an array, then type commands separated by semicolons. Pip runs each one in the practice shell and redraws the boxes with their indexes, so gaps, appends and slices are easy to see.',
    inputs: [{ k: 'def', label: 'Create', type: 'text', val: 'fruits=(apple "star fruit" mango)', w: 300 }, { k: 'ops', label: 'Then run', type: 'text', val: 'fruits+=(kiwi); unset "fruits[1]"; fruits[6]=fig; echo ${#fruits[@]}; echo ${!fruits[@]}', w: 420 }],
    random: () => [{ def: 'fruits=(apple "star fruit" mango)', ops: 'fruits+=(kiwi); unset "fruits[1]"; fruits[6]=fig; echo ${#fruits[@]}; echo ${!fruits[@]}' }, { def: 'n=(5 3 8 1)', ops: 'n[0]=50; echo ${n[-1]}; echo "${n[@]:1:2}"; n=("${n[@]}" 9)' }, { def: 'declare -A age=([asha]=31 [ravi]=28)', ops: 'age[meera]=35; echo ${age[ravi]}; unset "age[asha]"; echo ${#age[@]}' }, { def: 'files=(*.txt)', ops: 'echo ${#files[@]}; files+=(new.log); echo "${files[@]%.*}"' }][Math.floor(Math.random() * 4)],
    frames: v => {
      const w = world(), def = String(v.def).trim();
      const m = /^(?:declare\s+-([aA])\s+)?([A-Za-z_]\w*)=\(/.exec(def);
      if (!m) return [{ msg: 'Start with name=(values), for example fruits=(apple mango), or declare -A name=([key]=value).', mood: 'think', layers: [] }];
      const name = m[2], assoc = m[1] === 'A';
      const r0 = w.run(def);
      if (r0.code) return [{ msg: 'bash could not create the array: ' + esc(r0.out), mood: 'sad', fx: 'shake', layers: [] }];
      const cells = (hi) => {
        const keys = w.arrKeys(name).map(String);
        return { t: 'flow', label: `${name}: ${keys.length} element${keys.length === 1 ? '' : 's'}${assoc ? ' (associative)' : ''}`, items: keys.length ? keys.map(k => [w.arrGet(name, assoc ? k : k) || '(empty)', '[' + k + ']', hi && hi.includes(k) ? 'yes' : 'cur']) : [['(no elements)', '', 'ghost']], plain: true };
      };
      const fr = [{ msg: assoc ? `<code>declare -A</code> made an <b>associative array</b>: its indexes are text keys. bash does not keep the keys in the order you typed them.` : `bash made an <b>indexed array</b>. Every value sits in a box with a number, starting at <b>0</b>.${/\*/.test(def) ? ' The glob filled it with the matching file names.' : ''}`, mood: 'think', layers: [cells()] }];
      const term = [];
      const ops = String(v.ops).split(/;\s*/).map(x => x.trim()).filter(Boolean).slice(0, 10);
      ops.forEach(op => {
        const before = w.arrKeys(name).map(k => k + '=' + w.arrGet(name, String(k)));
        const r = w.run(op); const o = r.out.replace(/\n$/, '');
        const after = w.arrKeys(name).map(String);
        const changed = after.filter(k => !before.includes(k + '=' + w.arrGet(name, k)));
        if (o) o.split('\n').forEach(x => term.push(['o', x]));
        term.push(['c', op]);
        const say = /^unset/.test(op) ? (assoc ? 'unset removed that key and its value.' : 'unset removed that element. The other indexes do not move, so the array now has a gap.')
          : /\+=\(/.test(op) ? 'An append with += adds after the highest index.'
          : /=\("\$\{/.test(op) ? 'Copying with ("${name[@]}") packs the values into indexes 0, 1, 2 ... again, so gaps disappear.'
          : /\[\d+\]=/.test(op) && !assoc ? 'Setting an index far past the end is allowed. The indexes in between simply do not exist.'
          : /\$\{#/.test(op) ? '${#name[@]} counts the elements that exist, not the highest index plus one.'
          : /\$\{!/.test(op) ? '${!name[@]} lists the indexes (or keys) that exist.'
          : /:\d+(:\d+)?\}/.test(op) ? '${name[@]:start:count} takes a slice of the values.'
          : /\[-\d+\]/.test(op) ? 'A negative index counts from the end, -1 is the last element.'
          : /=/.test(op) ? 'The assignment stored a value in one box.' : 'This reads the array without changing it.';
        fr.push({ msg: `<code>${esc(op)}</code>${o ? ` prints <b>${esc(o)}</b>` : ''}. ${say}${r.code ? ' bash reported an error.' : ''}`, mood: changed.length ? 'wow' : 'look', layers: [cells(changed), { t: 'term', label: 'Output', lines: term.filter(x => x[0] === 'o').length ? term.filter(x => x[0] === 'o') : [['o', '(nothing printed yet)']] }] });
      });
      fr.push({ msg: 'Always loop over the values with "${name[@]}" in double quotes, so a value with a space stays one item.', mood: 'happy', fx: 'burst', layers: [cells()] });
      return fr;
    }
  }));

  /* scripting 4.1 set -e, set -u and pipefail: which failing line stops a script, and which does not */
  const EXITS = {
    cd: ['cd /tmp/nowhere', 'rm -f old.log', 'echo "cleaned up"'],
    grepc: ['grep -q pizza fruits.txt && echo "found pizza"', 'echo "next step"', 'count=$(grep -c pizza fruits.txt)', 'echo "count=$count"'],
    arith: ['n=0', '(( n++ ))', 'echo "n is now $n"'],
    pipe: ['grep pizza fruits.txt | sort', 'echo "sorted"', 'echo "user is $USERNAME"', 'echo "done"'],
    guard: ['if grep -q pizza fruits.txt; then echo yes; else echo no; fi', 'false || echo "recovered"', 'false', 'echo "never printed with set -e"']
  };
  def('lx-errexit', el => W(el, {
    title: 'Which failure stops the script',
    sub: 'Pick a small script and switch the safety options on or off. Pip runs it line by line, explains why each failing line does or does not stop the script under the bash rules, and then runs the whole file to check.',
    inputs: [{ k: 'script', label: 'Script', type: 'seg', val: 'grepc', opts: [['cd', 'cd that fails'], ['grepc', 'grep -c finds nothing'], ['arith', '(( n++ )) from 0'], ['pipe', 'pipe and unset variable'], ['guard', 'if, || and a bare false']] },
             { k: 'e', label: 'set -e', type: 'seg', val: 'on', opts: [['on', 'on'], ['off', 'off']] }, { k: 'u', label: 'set -u', type: 'seg', val: 'off', opts: [['on', 'on'], ['off', 'off']] }, { k: 'p', label: 'pipefail', type: 'seg', val: 'off', opts: [['on', 'on'], ['off', 'off']] }],
    random: () => ({ script: Object.keys(EXITS)[Math.floor(Math.random() * 5)], e: 'on', u: Math.random() < 0.5 ? 'on' : 'off', p: Math.random() < 0.5 ? 'on' : 'off' }),
    frames: v => {
      const lines = EXITS[v.script] || EXITS.grepc, E = v.e === 'on', U = v.u === 'on', P = v.p === 'on';
      const flags = [E && 'set -e', U && 'set -u', P && 'set -o pipefail'].filter(Boolean);
      const w = world(); if (U) w.run('set -u'); if (P) w.run('set -o pipefail');
      const rows = lines.map(l => [l, '', '']), term = [];
      const draw = (k, cls) => ({ t: 'flow', label: 'The script' + (flags.length ? ' with ' + flags.join(', ') : ' with no options'), items: rows.map((r, j) => [r[0], r[1], j === k ? cls : r[2]]), plain: true });
      const fr = [{ msg: flags.length ? `The script starts with <code>${esc(flags.join('; '))}</code>.` : 'No safety options are on, so bash runs every line whatever happens.', mood: 'think', layers: [draw(-1)] }];
      let stopped = -1;
      for (let k = 0; k < lines.length; k++) {
        const line = lines[k];
        /* run a && / || list part by part, to know whether the last part ran */
        const parts = line.split(/\s(&&|\|\|)\s/), steps = [];
        let code = 0, out = '', lastRan = true, unbound = false;
        if (parts.length > 1 && !/^if\s/.test(line)) {
          let i = 0, r = w.run(parts[0]); code = r.code; out += r.out; steps.push(parts[0]);
          for (i = 1; i < parts.length; i += 2) { const op = parts[i], next = parts[i + 1]; if ((op === '&&' && code === 0) || (op === '||' && code !== 0)) { r = w.run(next); code = r.code; out += r.out; lastRan = i + 1 === parts.length - 1; } else lastRan = false; }
          lastRan = lastRan && code !== 0 && (parts.length < 3 || true);
        } else { const r = w.run(line); code = r.code; out = r.out; }
        unbound = /unbound variable/.test(out);
        out.replace(/\n$/, '').split('\n').filter(x => x !== '').forEach(x => term.push([/unbound|No such|cannot/.test(x) ? 'e' : 'o', x]));
        const isIf = /^(if|while|until)\s/.test(line), isNeg = /^!\s/.test(line), isList = parts.length > 1 && !isIf;
        const isPipe = /[^|]\|[^|]/.test(line) && !isList;
        let why, stop = false;
        if (unbound) { stop = U; why = 'With set -u, using a variable that was never set is an error, and a script exits at once, even without set -e.'; }
        else if (code === 0) why = isList ? 'The list as a whole succeeded.' : 'Status 0, success.';
        else if (isIf) why = 'A failure inside the test of if, while or until is how the condition says no. set -e ignores it.';
        else if (isNeg) why = 'A command reversed with ! never triggers set -e.';
        else if (isList && !lastRan) why = 'A failure in the && or || list, but not in its last command, is treated as a decision. set -e ignores it.';
        else if (isPipe && !P) why = 'A pipeline’s status is that of its last command, here sort, which succeeded. Without pipefail the failing grep is invisible.';
        else if (isPipe && P) { stop = E; why = 'With pipefail the pipeline fails when any part fails, here grep.' + (E ? ' set -e stops the script.' : ' set -e is off, so the script goes on.'); }
        else if (/^\(\(/.test(line)) { stop = E; why = '(( n++ )) gives the old value, 0, and an arithmetic result of 0 means status 1.' + (E ? ' set -e stops the script, a famous surprise.' : ''); }
        else if (/=\$\(/.test(line)) { stop = E; why = 'An assignment gets the status of its command substitution. grep -c prints 0 and exits with 1 when nothing matches.' + (E ? ' set -e stops the script here.' : ''); }
        else { stop = E; why = `Status ${code}.` + (E ? ' set -e stops the script.' : ' Without set -e the script just carries on.'); }
        rows[k][1] = 'status ' + code; rows[k][2] = stop ? 'no' : code ? 'look' : 'yes';
        fr.push({ msg: `<code>${esc(line)}</code> ends with status ${code}. ${why}`, mood: stop ? 'sad' : code ? 'look' : 'happy', fx: stop ? 'shake' : undefined, layers: [draw(k, stop ? 'no' : code ? 'look' : 'yes'), { t: 'term', label: 'Output so far', lines: term.length ? term.slice() : [['o', '(nothing yet)']] }] });
        if (stop) { stopped = k; break; }
      }
      if (stopped >= 0) for (let j = stopped + 1; j < rows.length; j++) rows[j][2] = 'ghost';
      const chk = world(); chk.run(`printf '%s\\n' ${['#!/bin/bash'].concat(flags, lines).map(x => "'" + x.replace(/'/g, "'\\''") + "'").join(' ')} > s.sh`);
      const res = chk.run('bash s.sh; echo "exit status $?"').out.replace(/\n$/, '').split('\n').filter(x => x !== '');
      fr.push({ msg: stopped >= 0 ? `The script stopped at line ${stopped + 1}, so the lines after it never ran. Here is the whole file run by the practice shell.` : 'Every line ran. Here is the whole file run by the practice shell.', mood: stopped >= 0 ? 'wow' : 'happy', fx: 'burst', layers: [draw(-1), { t: 'term', label: 'bash s.sh', lines: res.map(x => [/unbound|No such|cannot/.test(x) ? 'e' : 'o', x]) }] });
      return fr;
    }
  }));

  /* scripting 4.2 a crontab line: five time fields, read one by one, and the next times it fires */
  def('lx-cron', el => W(el, {
    title: 'Read a crontab line',
    sub: 'Type the five time fields of a cron schedule (or a word like @daily). Pip explains every field and lists the next times cron would start the job, counting from Monday 23 November 2026, 09:30.',
    inputs: [{ k: 'expr', label: 'Schedule', type: 'text', val: '*/15 9-17 * * 1-5', w: 240 }],
    random: () => ({ expr: ['*/15 9-17 * * 1-5', '0 6 * * mon', '30 2 * * *', '0 0 1 * *', '0 9 * * 1', '0 8,20 * * *', '5 4 * * sun', '0 0 13 * fri', '@hourly', '0 */6 * * *'][Math.floor(Math.random() * 10)] }),
    frames: v => {
      let expr = String(v.expr).trim().toLowerCase();
      const special = { '@yearly': '0 0 1 1 *', '@annually': '0 0 1 1 *', '@monthly': '0 0 1 * *', '@weekly': '0 0 * * 0', '@daily': '0 0 * * *', '@midnight': '0 0 * * *', '@hourly': '0 * * * *' };
      const fr = [];
      if (expr === '@reboot') return [{ msg: '<code>@reboot</code> runs the job once, each time the cron daemon starts, which normally means once after every boot. It has no clock time.', mood: 'look', layers: [] }];
      if (special[expr]) { fr.push({ msg: `<code>${esc(expr)}</code> is a short name for <code>${special[expr]}</code>.`, mood: 'think', layers: [] }); expr = special[expr]; }
      const f = expr.split(/\s+/);
      if (f.length !== 5) return [{ msg: `A schedule has exactly 5 fields: minute, hour, day of month, month and day of week. You typed ${f.length}.`, mood: 'think', fx: 'shake', layers: [] }];
      const names = [null, null, null, 'jan feb mar apr may jun jul aug sep oct nov dec'.split(' '), 'sun mon tue wed thu fri sat'.split(' ')];
      const lim = [[0, 59], [0, 23], [1, 31], [1, 12], [0, 7]], label = ['minute', 'hour', 'day of month', 'month', 'day of week'];
      const sets = [];
      for (let k = 0; k < 5; k++) {
        const set = new Set(); let bad = false;
        f[k].split(',').forEach(part => {
          const m = /^(\*|([0-9a-z]+)(?:-([0-9a-z]+))?)(?:\/(\d+))?$/.exec(part);
          if (!m) { bad = true; return; }
          const num = x => { if (/^\d+$/.test(x)) return +x; const n = names[k] ? names[k].indexOf(x) : -1; return n >= 0 ? n + (k === 3 ? 1 : 0) : NaN; };
          let a = lim[k][0], b = lim[k][1];
          if (m[1] !== '*') { a = num(m[2]); b = m[3] !== undefined ? num(m[3]) : (m[4] ? lim[k][1] : a); }
          const st = m[4] ? +m[4] : 1;
          if (!(a >= lim[k][0] && b <= lim[k][1] && a <= b && st > 0)) { bad = true; return; }
          for (let x = a; x <= b; x += st) set.add(k === 4 && x === 7 ? 0 : x);
        });
        if (bad) return [{ msg: `The ${label[k]} field <code>${esc(f[k])}</code> is not valid. It must use numbers from ${lim[k][0]} to ${lim[k][1]}${names[k] ? ' or names such as ' + names[k].slice(0, 3).join(', ') : ''}, with * , - and /.`, mood: 'sad', fx: 'shake', layers: [] }];
        sets.push(set);
      }
      const say = (k) => {
        const x = f[k];
        if (x === '*') return 'every ' + label[k];
        if (/^\*\/\d+$/.test(x)) return `every ${x.slice(2)} ${label[k]}s, starting at ${lim[k][0]}`;
        const show = [...sets[k]].sort((p, q) => p - q).map(n => k === 4 ? 'Sun Mon Tue Wed Thu Fri Sat'.split(' ')[n] : k === 3 ? 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')[n - 1] : String(n));
        return (show.length > 8 ? show.slice(0, 8).join(', ') + ' ...' : show.join(', '));
      };
      const items = (hi) => f.map((x, k) => [x, label[k], k === hi ? 'cur' : k < hi ? 'yes' : '']);
      f.forEach((x, k) => fr.push({ msg: `Field ${k + 1}, the <b>${label[k]}</b>: <code>${esc(x)}</code> means <b>${esc(say(k))}</b>.`, mood: 'look', layers: [{ t: 'flow', label: 'minute hour day-of-month month day-of-week', items: items(k), plain: true }] }));
      const domR = f[2] !== '*', dowR = f[4] !== '*';
      if (domR && dowR) fr.push({ msg: 'Both the day of month and the day of week are set. cron then runs the job when <b>either</b> matches, not only when both do. This rule surprises many people.', mood: 'wow', fx: 'shake', layers: [] });
      const runs = []; let t = Date.UTC(2026, 10, 23, 9, 31);
      const end = t + 366 * 864e5 * 2;
      while (runs.length < 6 && t < end) {
        const d = new Date(t), mi = d.getUTCMinutes(), h = d.getUTCHours(), dom = d.getUTCDate(), mo = d.getUTCMonth() + 1, dow = d.getUTCDay();
        if (!sets[3].has(mo)) { t = Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1); continue; }
        const dayOk = domR && dowR ? sets[2].has(dom) || sets[4].has(dow) : sets[2].has(dom) && sets[4].has(dow);
        if (!dayOk) { t = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), dom + 1); continue; }
        if (!sets[1].has(h)) { t = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), dom, h + 1); continue; }
        if (sets[0].has(mi)) runs.push(t);
        t += 6e4;
      }
      const fmt = ms => { const d = new Date(ms), z = n => String(n).padStart(2, '0'); return `${'Sun Mon Tue Wed Thu Fri Sat'.split(' ')[d.getUTCDay()]} ${d.getUTCFullYear()}-${z(d.getUTCMonth() + 1)}-${z(d.getUTCDate())} ${z(d.getUTCHours())}:${z(d.getUTCMinutes())}`; };
      fr.push({ msg: runs.length ? `Starting from Monday 23 November 2026, 09:30, cron would start the job at these times.` : 'This schedule never matches a real date, for example 30 February, so the job would never run.', mood: runs.length ? 'happy' : 'sad', fx: runs.length ? 'burst' : 'shake', layers: [{ t: 'term', label: 'Next runs', lines: runs.map(x => ['o', fmt(x)]) }] });
      return fr;
    }
  }));

  /* admin 1.1 account files: a line of /etc/passwd, /etc/shadow, /etc/group or sudoers, read field by field */
  const ACCT = {
    passwd: { label: 'one line of /etc/passwd', eg: ['dev1:x:1002:1002:Dev One,,,:/home/dev1:/bin/bash', 'www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin', 'root:x:0:0:root:/root:/bin/bash', 'backup:x:34:34:backup:/var/backups:/usr/sbin/nologin'] },
    shadow: { label: 'one line of /etc/shadow', eg: ['dev1:$y$j9T$Hk3...$Qx9...:20780:0:99999:7:::', 'dev1:!:20780:0:99999:7:::', 'ops:$6$salt$hash:20700:1:90:14:30::', 'daemon:*:20415:0:99999:7:::'] },
    group: { label: 'one line of /etc/group', eg: ['sudo:x:27:learner,dev1', 'web:x:1003:', 'docker:x:998:asha,dev1'] },
    sudoers: { label: 'one rule in /etc/sudoers', eg: ['%sudo ALL=(ALL:ALL) ALL', 'dev1 ALL=(root) NOPASSWD: /usr/bin/systemctl restart nginx', 'backup web1=(postgres) /usr/bin/pg_dump', 'root ALL=(ALL:ALL) ALL'] }
  };
  def('lx-account', el => W(el, {
    title: 'Read an account line',
    sub: 'Pick a file, then type or pick a line. Pip reads it one field at a time, as login, su, sudo and ls do.',
    inputs: [{ k: 'file', label: 'File', type: 'seg', val: 'passwd', opts: [['passwd', '/etc/passwd'], ['shadow', '/etc/shadow'], ['group', '/etc/group'], ['sudoers', 'sudoers']] },
             { k: 'line', label: 'Line', type: 'text', val: 'dev1:x:1002:1002:Dev One,,,:/home/dev1:/bin/bash', w: 380 }],
    random: () => { const k = Object.keys(ACCT)[Math.floor(Math.random() * 4)], eg = ACCT[k].eg; return { file: k, line: eg[Math.floor(Math.random() * eg.length)] }; },
    frames: v => {
      const kind = ACCT[v.file] ? v.file : 'passwd', line = String(v.line).trim();
      const day = d => { const t = new Date(+d * 864e5); return t.toISOString().slice(0, 10); };
      let fields = [], names = [];
      if (kind === 'sudoers') {
        const m = /^(\S+)\s+([^=\s]+)\s*=\s*(?:\(([^)]*)\)\s*)?((?:(?:NOPASSWD|PASSWD|NOEXEC|SETENV):\s*)*)(.+)$/.exec(line);
        if (!m) return [{ msg: 'A sudoers rule reads: who, where = (as whom) commands, for example <code>dev1 ALL=(root) /usr/bin/systemctl</code>. visudo would refuse this line.', mood: 'sad', fx: 'shake', layers: [] }];
        names = ['who', 'on which hosts', 'as which user and group', 'tags', 'commands'];
        fields = [m[1], m[2], m[3] === undefined ? '(root, the default)' : m[3], m[4].trim() || '(none)', m[5]];
        const say = [
          m[1].startsWith('%') ? `every member of the group <b>${esc(m[1].slice(1))}</b> (a % in front means a group)` : `the user <b>${esc(m[1])}</b>`,
          m[2] === 'ALL' ? 'on any host. The same sudoers file can be shared by many machines' : `only on the host called <b>${esc(m[2])}</b>`,
          m[3] === undefined ? 'may run commands as root, because no run-as list was given' : `may run commands as <b>${esc(m[3])}</b>. Before the colon are users, after it groups`,
          /NOPASSWD/.test(m[4]) ? '<b>NOPASSWD</b>: sudo will not ask for the user’s own password. Use it only for narrow commands' : 'no tags, so sudo asks for the user’s own password (not the root password), then remembers it for a few minutes',
          m[5].trim() === 'ALL' ? 'any command at all. This is full root power' : `only <code>${esc(m[5])}</code>, with exactly these arguments if arguments are given. Always write full paths`];
        const fr = names.map((n, k) => ({ msg: `${n[0].toUpperCase() + n.slice(1)}: ${say[k]}.`, mood: k === 4 && m[5].trim() === 'ALL' ? 'wow' : 'look', layers: [{ t: 'flow', label: 'who host=(runas) tags commands', items: fields.map((f, j) => [f, names[j], j === k ? 'cur' : j < k ? 'yes' : '']), plain: true }] }));
        fr.push({ msg: 'Always edit sudoers with <code>sudo visudo</code> or a file in /etc/sudoers.d with <code>sudo visudo -f</code>. visudo checks the syntax before saving, so a typo cannot lock everyone out of sudo.', mood: 'happy', fx: 'burst', layers: [{ t: 'flow', label: 'The whole rule', items: fields.map((f, j) => [f, names[j], 'yes']), plain: true }] });
        return fr;
      }
      const f = line.split(':');
      const want = { passwd: 7, shadow: 9, group: 4 }[kind];
      if (f.length !== want) return [{ msg: `A line of /etc/${kind} has exactly ${want} fields separated by colons. This one has ${f.length}.`, mood: 'sad', fx: 'shake', layers: [] }];
      let say;
      if (kind === 'passwd') {
        names = ['user name', 'password', 'UID', 'GID', 'comment (GECOS)', 'home folder', 'login shell'];
        const uid = +f[2];
        say = [`The login name is <b>${esc(f[0])}</b>.`,
          f[1] === 'x' ? 'An <b>x</b> means the real password hash lives in /etc/shadow, which only root can read.' : 'The password field is not x. Modern systems keep hashes in /etc/shadow instead.',
          `The user ID is <b>${esc(f[2])}</b>. ${uid === 0 ? 'UID 0 is root, whatever the name. The kernel checks the number, not the name.' : uid < 1000 ? 'Below 1000 on Debian and Ubuntu means a system account for a service.' : 'From 1000 up means a normal person’s account (UID_MIN in /etc/login.defs).'}`,
          `The primary group ID is <b>${esc(f[3])}</b>. New files get this group. Its name is in /etc/group.`,
          `The comment is <b>${esc(f[4]) || '(empty)'}</b>, usually the full name. Commas separate room, phone and other old fields.`,
          `The home folder is <b>${esc(f[5])}</b>. ~ means this folder for this user.`,
          /nologin|false$/.test(f[6]) ? `The shell is <b>${esc(f[6])}</b>, so nobody can log in as this account. Services run as it without a shell.` : `The shell <b>${esc(f[6])}</b> starts when this user logs in.`];
      } else if (kind === 'shadow') {
        names = ['user name', 'password hash', 'last change', 'min days', 'max days', 'warn days', 'inactive days', 'expire date', 'reserved'];
        const h = f[1], alg = { '$y$': 'yescrypt', '$6$': 'SHA-512 crypt', '$5$': 'SHA-256 crypt', '$1$': 'MD5 crypt (weak, old)', '$2b$': 'bcrypt' };
        const a = Object.keys(alg).find(k => h.startsWith(k));
        say = [`The account <b>${esc(f[0])}</b>.`,
          h === '*' ? 'A <b>*</b> means no password can ever match, which is normal for system accounts.' : h.startsWith('!') ? 'A <b>!</b> in front means the password is <b>locked</b>. passwd -l or usermod -L adds it, and a fresh useradd account starts locked until it gets a password.' : h === '' ? 'An empty field means no password at all, which is dangerous.' : `A hash made with <b>${a ? alg[a] : 'an unknown method'}</b>. The format is $method$salt$hash, and the salt makes equal passwords look different.`,
          `Last changed on day <b>${esc(f[2])}</b> counted from 1 January 1970, which is ${/^\d+$/.test(f[2]) ? day(f[2]) : 'not a number'}.`,
          `At least <b>${esc(f[3]) || 0}</b> days must pass before the user may change it again.`,
          f[4] === '99999' || f[4] === '' ? 'Max <b>99999</b> days means the password never really expires.' : `The password must be changed every <b>${esc(f[4])}</b> days.`,
          `The user is warned <b>${esc(f[5]) || 0}</b> days before it expires.`,
          f[6] ? `After expiry the account still works for <b>${esc(f[6])}</b> days, then it is disabled.` : 'Empty, so no grace period is set.',
          f[7] ? `The whole account expires on day ${esc(f[7])}.` : 'Empty, so the account itself never expires.',
          'Reserved for future use, always empty.'];
      } else {
        names = ['group name', 'password', 'GID', 'members'];
        const mem = f[3] ? f[3].split(',') : [];
        say = [`The group is <b>${esc(f[0])}</b>.`, 'Group passwords are almost never used. x points to /etc/gshadow.', `The group ID is <b>${esc(f[2])}</b>.`,
          mem.length ? `Extra members: <b>${esc(mem.join(', '))}</b>. Users whose primary GID is ${esc(f[2])} in /etc/passwd also belong, but are not listed here.` : 'No extra members are listed. Users whose primary GID is this one still belong.'];
      }
      const fr = names.map((n, k) => ({ msg: `Field ${k + 1}, ${n}: ${say[k]}`, mood: k === 1 && kind === 'shadow' && f[1].startsWith('!') ? 'wow' : 'look', layers: [{ t: 'flow', label: ACCT[kind].label, items: f.map((x, j) => [x === '' ? '(empty)' : x.length > 18 ? x.slice(0, 16) + '…' : x, names[j], j === k ? 'cur' : j < k ? 'yes' : '']), plain: true }] }));
      const tip = { passwd: `<code>getent passwd ${esc(f[0])}</code> prints this line, and <code>id ${esc(f[0])}</code> shows the IDs with names.`, shadow: `<code>sudo chage -l ${esc(f[0])}</code> shows these dates in words, and <code>sudo passwd -S ${esc(f[0])}</code> gives a one-line status.`, group: `<code>getent group ${esc(f[0])}</code> prints this line, and <code>sudo usermod -aG ${esc(f[0])} NAME</code> adds a member.` }[kind];
      fr.push({ msg: 'Every field read. ' + tip, mood: 'happy', fx: 'burst', layers: [{ t: 'flow', label: ACCT[kind].label, items: f.map((x, j) => [x === '' ? '(empty)' : x.length > 18 ? x.slice(0, 16) + '…' : x, names[j], 'yes']), plain: true }] });
      return fr;
    }
  }));

  /* admin 1.2 apt: resolving dependencies, downloading, unpacking, setting up, and removing with autoremove */
  def('lx-apt', el => W(el, {
    title: 'What apt does for you',
    sub: 'Pick a package and an action. Pip runs apt in the practice shell, which uses real Ubuntu 24.04 package data, and shows each stage: dependencies, download, unpack, set up, and cleaning up.',
    inputs: [{ k: 'pkg', label: 'Package', type: 'seg', val: 'jq', opts: [['jq', 'jq'], ['cowsay', 'cowsay'], ['figlet', 'figlet'], ['tree', 'tree']] },
             { k: 'act', label: 'Action', type: 'seg', val: 'install', opts: [['install', 'install'], ['remove', 'remove, then autoremove']] }],
    random: () => ({ pkg: ['jq', 'cowsay', 'figlet', 'tree'][Math.floor(Math.random() * 4)], act: Math.random() < 0.6 ? 'install' : 'remove' }),
    frames: v => {
      const pkg = ['jq', 'cowsay', 'figlet', 'tree'].includes(v.pkg) ? v.pkg : 'jq', w = world();
      const deps = n => { const o = w.run('apt-cache depends ' + n).out; return [...o.matchAll(/Depends: (\S+)/g)].map(m => m[1]); };
      const chain = []; const walk = n => { if (chain.includes(n)) return; chain.push(n); deps(n).forEach(walk); }; walk(pkg);
      const lines = o => o.replace(/\n$/, '').split('\n').filter(x => x !== '').map(x => [/^E:/.test(x) ? 'e' : 'o', x]);
      const box = (st, label) => ({ t: 'flow', label: label || 'Packages', items: chain.map(n => [n, st[n] || '', st[n] === 'installed' || st[n] === 'set up' ? 'yes' : st[n] === 'removed' ? 'no' : st[n] ? 'cur' : '']), arrows: chain.slice(1).map(() => ''), plain: true });
      const fr = [];
      if (v.act !== 'remove') {
        const pre = w.run('dpkg -l ' + pkg + ' 2>/dev/null').code === 0;
        fr.push({ msg: `You type <code>sudo apt install ${pkg}</code>. apt first reads its package lists, which <code>sudo apt update</code> downloads from the repositories in /etc/apt/sources.list.d.`, mood: 'think', layers: [box({ [pkg]: 'requested' })] });
        if (pre) {
          const r = w.run('sudo apt install -y ' + pkg);
          fr.push({ msg: `${pkg} is part of the base system here, so apt has nothing to do.`, mood: 'happy', fx: 'burst', layers: [box({ [pkg]: 'installed' }), { t: 'term', label: '$ sudo apt install ' + pkg, lines: lines(r.out) }] });
          return fr;
        }
        const st = {}; chain.forEach((n, i) => { st[n] = i ? 'needed' : 'requested'; });
        fr.push({ msg: chain.length > 1 ? `apt reads the Depends field of each package. ${pkg} needs ${chain.slice(1).join(', then ')}. These are installed automatically and marked as automatic.` : `${pkg} has no dependencies that are missing here.`, mood: 'look', layers: [box(st, 'Dependency chain')] });
        const r = w.run('sudo apt install -y ' + pkg), L = lines(r.out);
        const head = L.filter(([, x]) => /^(The following|  |\d+ upgraded|Need to get|After this)/.test(x));
        fr.push({ msg: 'apt prints a plan: what is new, how much it downloads and how much disk space it uses. Without -y it asks before it goes on.', mood: 'look', layers: [box(st), { t: 'term', label: 'The plan', lines: head }] });
        chain.forEach(n => { st[n] = 'downloaded'; });
        fr.push({ msg: 'Every .deb file is downloaded into /var/cache/apt/archives. apt checks the signature of the package lists, so a changed file is refused.', mood: 'look', layers: [box(st), { t: 'term', label: 'Download', lines: L.filter(([, x]) => /^(Get|Fetched)/.test(x)) }] });
        chain.forEach(n => { st[n] = 'unpacked'; });
        fr.push({ msg: 'apt hands the files to dpkg, which unpacks each one into place and records every file it owns in /var/lib/dpkg.', mood: 'look', layers: [box(st), { t: 'term', label: 'Unpack', lines: L.filter(([, x]) => /^(Selecting|Preparing|Unpacking)/.test(x)) }] });
        const setup = L.filter(([, x]) => /^Setting up/.test(x));
        setup.forEach(([, x], i) => { const n = x.split(' ')[2].split(':')[0]; st[n] = 'set up'; fr.push({ msg: `dpkg sets up <b>${esc(n)}</b>${i < setup.length - 1 ? ', a dependency, before the package that needs it' : ', last, because everything it needs is ready'}. Setting up runs the package’s own scripts, for example to create a system user or start a service.`, mood: i === setup.length - 1 ? 'happy' : 'look', layers: [box(st), { t: 'term', label: 'Set up', lines: setup.slice(0, i + 1) }] }); });
        const t = pkg === 'jq' ? w.run('jq --version') : pkg === 'cowsay' ? w.run('/usr/games/cowsay done') : w.run('dpkg -L ' + pkg + ' | tail -1');
        const lst = w.run('apt list --installed ' + chain.join(' ')).out;
        fr.push({ msg: `Done. apt list shows which packages you asked for and which came automatically.${pkg === 'cowsay' ? ' cowsay lives in /usr/games, which sudo and this shell do not have in PATH, so the full path is used.' : ''}`, mood: 'happy', fx: 'burst', layers: [box(Object.fromEntries(chain.map(n => [n, 'installed']))), { t: 'term', label: 'Check', lines: lines(lst).concat(lines(t.out)) }] });
        return fr;
      }
      const pre = w.run('dpkg -l ' + pkg + ' 2>/dev/null').code === 0;
      if (pre) {
        const r = w.run('echo n | sudo apt remove ' + pkg);
        return [{ msg: `${pkg} belongs to the base system of the practice computer. apt would remove it, but here Pip stops at the question. Removing base tools is how systems break, so read the plan every time.`, mood: 'wow', fx: 'shake', layers: [box({ [pkg]: 'base system' }), { t: 'term', label: '$ sudo apt remove ' + pkg, lines: lines(r.out) }] }];
      }
      w.run('sudo apt install -y ' + pkg);
      const st = Object.fromEntries(chain.map((n, i) => [n, i ? 'automatic' : 'manual']));
      fr.push({ msg: `${pkg} is installed. apt remembers that you asked for ${pkg} by hand, while ${chain.length > 1 ? chain.slice(1).join(' and ') + ' came automatically' : 'nothing else came with it'}.`, mood: 'think', layers: [box(st, 'Installed packages')] });
      const r = w.run('echo y | sudo apt remove ' + pkg);
      st[pkg] = 'removed';
      fr.push({ msg: chain.length > 1 ? `<code>sudo apt remove ${pkg}</code> removes only ${pkg}. The automatic packages stay, and apt says they are no longer required.` : `<code>sudo apt remove ${pkg}</code> removes it. Its configuration files would stay unless you use apt purge.`, mood: 'look', layers: [box(st), { t: 'term', label: '$ sudo apt remove ' + pkg, lines: lines(r.out) }] });
      if (chain.length > 1) {
        const r2 = w.run('sudo apt autoremove -y');
        chain.forEach(n => { st[n] = 'removed'; });
        fr.push({ msg: '<code>sudo apt autoremove</code> removes automatic packages that nothing needs any more. Read its list before you agree, because it can include packages you used directly.', mood: 'happy', fx: 'burst', layers: [box(st), { t: 'term', label: '$ sudo apt autoremove', lines: lines(r2.out) }] });
      }
      return fr;
    }
  }));

  /* admin 2.1 the boot sequence, stage by stage, with a chosen place where it can break */
  def('lx-boot', el => W(el, {
    title: 'From power button to login',
    sub: 'Press Play to follow a Linux machine as it starts. Pick a fault to see where the boot stops, what the screen shows, and how an admin fixes it.',
    inputs: [{ k: 'fault', label: 'Fault', type: 'seg', val: 'none', opts: [['none', 'no fault'], ['grub', 'broken boot loader'], ['initramfs', 'root disk not found'], ['fstab', 'typo in /etc/fstab'], ['service', 'a service fails']] }],
    random: () => ({ fault: ['none', 'grub', 'initramfs', 'fstab', 'service'][Math.floor(Math.random() * 5)] }),
    frames: v => {
      const S = ['Firmware', 'Boot loader', 'Kernel', 'initramfs', 'systemd', 'Login'];
      const sm = ['UEFI or BIOS', 'GRUB', 'vmlinuz', 'early root', 'PID 1', 'getty, sshd'];
      const stop = { grub: 1, initramfs: 3, fstab: 4 }[v.fault];
      const flow = (k, bad) => ({ t: 'flow', label: 'Boot stages', items: S.map((x, i) => [x, sm[i], bad && i === k ? 'no' : i === k ? 'cur' : i < k ? 'yes' : stop !== undefined && i > stop && bad ? 'ghost' : '']), arrows: S.slice(1).map((_, i) => i < k ? 'yes' : '') });
      const say = [
        'Power on. The firmware (UEFI on modern PCs, BIOS on old ones) tests the hardware and looks for something to boot. UEFI reads a boot loader file from the EFI System Partition, usually mounted at /boot/efi.',
        'GRUB shows its menu, reads /boot/grub/grub.cfg, then loads the kernel file (/boot/vmlinuz-VERSION) and the initramfs into memory, and passes the kernel command line, such as root=UUID=... ro quiet.',
        'The kernel unpacks itself, detects CPUs, memory and devices, and mounts the initramfs, a small file system in memory, as a temporary root.',
        'The initramfs loads the drivers needed to reach the real root disk, for example for NVMe, RAID, LVM or disk encryption, where it asks for the passphrase. Then it mounts the real root and switches to it.',
        'The kernel starts /sbin/init, which is systemd, as process 1. systemd reads its units, mounts the file systems in /etc/fstab and starts services in parallel, in the order their dependencies need, until default.target is reached.',
        'Login prompts appear: getty on the text consoles, a display manager on a desktop, and sshd for remote logins. The machine is up.'];
      const screen = {
        grub: ['error: unknown filesystem.', 'Entering rescue mode...', 'grub rescue>'],
        initramfs: ['Gave up waiting for root file system device.', 'ALERT!  UUID=6c1f0d3a-... does not exist.  Dropping to a shell!', '(initramfs)'],
        fstab: ['[FAILED] Failed to mount data.mount - /data.', '[DEPEND] Dependency failed for local-fs.target - Local File Systems.', 'You are in emergency mode. After logging in, type "journalctl -xb" to view', 'system logs, "systemctl reboot" to reboot, "systemctl default" or "exit"', 'to boot into default mode.', 'Give root password for maintenance']
      };
      const fix = {
        grub: 'Fix: boot from a live USB, mount the installed system, and run grub-install and update-grub (grub2-mkconfig on Fedora) inside a chroot.',
        initramfs: 'Fix: check the disk is connected and healthy, compare the UUID with blkid, and rebuild the initramfs with update-initramfs -u (dracut -f on Fedora) if a driver is missing.',
        fstab: 'Fix: log in as root, mount / read-write with mount -o remount,rw /, correct /etc/fstab, test it with findmnt --verify or mount -a, and reboot. Adding nofail to lines for disks that may be missing prevents this.'
      };
      const fr = [];
      for (let k = 0; k < S.length; k++) {
        if (stop === k) {
          fr.push({ msg: `The boot stops at the ${S[k].toLowerCase()} stage. This is what the screen shows.`, mood: 'sad', fx: 'shake', layers: [flow(k, true), { t: 'term', label: 'Console', lines: screen[v.fault].map(x => [/^(error|ALERT|\[FAILED\]|Gave)/.test(x) ? 'e' : 'o', x]) }] });
          fr.push({ msg: fix[v.fault], mood: 'think', layers: [flow(k, true)] });
          return fr;
        }
        fr.push({ msg: say[k], mood: k === S.length - 1 ? 'happy' : 'look', fx: k === S.length - 1 && v.fault !== 'service' ? 'burst' : undefined, layers: [flow(k)] });
      }
      if (v.fault === 'service') {
        const w = world(), r = w.run('systemctl --failed'), r2 = w.run('sudo journalctl -u backup -p err');
        fr.push({ msg: 'A failing service does not stop the boot. The machine comes up, but systemctl reports a degraded state, so always check for failed units after a boot.', mood: 'wow', fx: 'shake', layers: [flow(S.length), { t: 'term', label: '$ systemctl --failed', lines: r.out.split('\n').slice(0, 2).map(x => ['o', x]) }] });
        fr.push({ msg: 'The journal of the unit tells why it failed. Here the backup target folder is missing.', mood: 'think', layers: [{ t: 'term', label: '$ sudo journalctl -u backup -p err', lines: r2.out.replace(/\n$/, '').split('\n').map(x => ['e', x]) }] });
      }
      return fr;
    }
  }));

  /* power 1.1 redirection: the file descriptor table, left to right */
  def('lx-redirect', el => W(el, {
    title: 'Where does each stream go',
    sub: 'Type a command with redirections. Pip reads them left to right, exactly like bash, updates the table of streams, and then runs the command in the practice shell.',
    inputs: [{ k: 'line', label: 'Command', type: 'text', val: 'ls notes.txt nothere > out.txt 2>&1', w: 420 }],
    random: () => ({ line: ['ls notes.txt nothere 2>&1 > out.txt', 'ls notes.txt nothere 2> errors.txt', 'ls nothere 2>/dev/null', 'wc -l < fruits.txt', 'ls notes.txt nothere &> all.txt', 'echo hello >> notes.txt', 'tr a-z A-Z <<< hello', 'echo oops >&2'][Math.floor(Math.random() * 8)] }),
    frames: v => {
      const line = String(v.line).trim(), w = world();
      let tree; try { tree = w.parse(w.lex(line)); } catch (e) { return [{ msg: 'The shell could not read that line: ' + esc(e.message), mood: 'sad', fx: 'shake', layers: [] }]; }
      const pp = tree.items.length === 1 ? tree.items[0].p : null, node = pp && pp.t === 'pipe' && pp.cmds.length === 1 && pp.cmds[0].t === 'cmd' ? pp.cmds[0] : pp && pp.t === 'cmd' ? pp : null;
      if (!node) return [{ msg: 'Type one simple command with redirections, without | or ;. Pipes have their own animation.', mood: 'think', layers: [] }];
      const name = node.words.map(x => w.wordText(x)).join(' ');
      const fd = { 0: 'the keyboard', 1: 'the terminal', 2: 'the terminal' };
      const rows = cls => [[0, 'stdin', fd[0], cls[0]], [1, 'stdout', fd[1], cls[1]], [2, 'stderr', fd[2], cls[2]]];
      const L = (cls) => [{ t: 'fds', label: 'The streams of ' + esc(name.split(' ')[0] || 'the command'), cmd: line, rows: rows(cls || {}) }];
      const fr = [{ msg: 'Every command starts with three open streams: 0 standard input from the keyboard, 1 standard output and 2 standard error, both to the terminal.', mood: 'think', layers: L() }];
      const files = new Set();
      for (const r of node.redir) {
        const f = r.w ? w.wordText(r.w) : '';
        let msg = '', c = {};
        if (r.op === '<') { fd[0] = f; c = { 0: 'look' }; msg = `<code>&lt; ${esc(f)}</code>: standard input now reads from the file ${esc(f)} instead of the keyboard.`; }
        else if (r.op === '<<<') { fd[0] = 'the text ' + f; c = { 0: 'look' }; msg = `<code>&lt;&lt;&lt;</code> is a here string: the word ${esc(f)} plus a newline becomes the input.`; }
        else if (r.op === '<<') { fd[0] = 'the here document'; c = { 0: 'look' }; msg = 'A here document: the following lines up to the end word become the input.'; }
        else if (r.op === '>' || r.op === '>|') { fd[1] = f; files.add(f); c = { 1: 'look' }; msg = `<code>&gt; ${esc(f)}</code>: standard output goes to ${esc(f)}. The file is created, or emptied if it exists, before the command even starts.`; }
        else if (r.op === '>>') { fd[1] = f + ' (append)'; files.add(f); c = { 1: 'look' }; msg = `<code>&gt;&gt; ${esc(f)}</code>: standard output is added to the end of ${esc(f)}. Nothing already there is lost.`; }
        else if (r.op === '2>' || r.op === '2>>') { fd[2] = f + (r.op === '2>>' ? ' (append)' : ''); if (f !== '/dev/null') files.add(f); c = { 2: 'look' }; msg = f === '/dev/null' ? '<code>2&gt; /dev/null</code>: error messages go to /dev/null, a special file that throws away everything written to it.' : `<code>2&gt; ${esc(f)}</code>: only stream 2, the error messages, goes to ${esc(f)}.`; }
        else if (r.op === '&>' || r.op === '&>>') { fd[1] = fd[2] = f; files.add(f); c = { 1: 'look', 2: 'look' }; msg = `<code>&amp;&gt; ${esc(f)}</code>: a bash shortcut that sends both stdout and stderr to ${esc(f)}.`; }
        else if (r.op === '2>&1') { fd[2] = fd[1]; c = { 2: 'look' }; msg = `<code>2&gt;&amp;1</code>: make stream 2 point to <b>wherever stream 1 points right now</b>, which is ${esc(fd[1])}. It copies the current target, it does not follow later changes.`; }
        else if (r.op === '>&2') { fd[1] = fd[2]; c = { 1: 'look' }; msg = `<code>&gt;&amp;2</code>: stream 1 now points where stream 2 points, ${esc(fd[2])}. Scripts use this to print error messages.`; }
        fr.push({ msg, mood: 'look', layers: L(c) });
      }
      const r = w.run(line);
      const done = [{ t: 'term', label: 'On the terminal', lines: [['c', line]].concat(r.out ? r.out.replace(/\n$/, '').split('\n').map(x => ['o', x]) : []) }];
      files.forEach(f => { if (f === '/dev/null') return; const n = w.node(w.abs(f)); if (n) done.push({ t: 'term', label: 'Inside ' + esc(f), lines: n.data ? n.data.replace(/\n$/, '').split('\n').map(x => ['o', x]) : [] }); });
      fr.push({ msg: `Now the command runs. ${r.out ? 'Whatever still points at the terminal appears on screen.' : 'Nothing points at the terminal any more, so the screen stays empty.'}${files.size ? ' The files hold the rest.' : ''}`, mood: 'happy', fx: 'burst', layers: L().concat(done) });
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
        const box = b.closest('.lx-run'), cmds = box.classList.contains('lx-shape') ? box.querySelector('pre').textContent : [...box.querySelectorAll('.lx-cmd')].map(x => x.textContent).join('\n');
        (navigator.clipboard ? navigator.clipboard.writeText(cmds) : Promise.reject()).then(() => { b.textContent = 'Copied'; setTimeout(() => { b.textContent = 'Copy'; }, 1200); }, () => { b.textContent = 'Select and copy'; });
      });
    });
  }
  function start() { VIZ.mountAll(document); wire(document); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
