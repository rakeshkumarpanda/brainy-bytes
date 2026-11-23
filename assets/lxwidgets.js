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
