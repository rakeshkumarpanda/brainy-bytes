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
